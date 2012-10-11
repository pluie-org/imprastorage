#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.8                                                             #
#   date      : 2012                                                            #
#   licence   : GPLv3.0   <http://www.gnu.org/licenses/>                        #
#   author    : a-Sansara <http://www.a-sansara.net/>                           #
#   copyright : pluie.org <http://www.pluie.org/>                               #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   This file is part of ImpraStorage.
#
#   ImpraStorage is free software (free as in speech) : you can redistribute it 
#   and/or modify it under the terms of the GNU General Public License as 
#   published by the Free Software Foundation, either version 3 of the License, 
#   or (at your option) any later version.
#
#   ImpraStorage is distributed in the hope that it will be useful, but WITHOUT 
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
#   more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ImpraStorage.  If not, see <http://www.gnu.org/licenses/>.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ package core ~~

from base64               import urlsafe_b64encode, b64decode
from binascii             import b2a_base64, a2b_base64
from datetime             import datetime, timedelta
from email.encoders       import encode_base64
from email.header         import Header
from email.mime.base      import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.utils          import formatdate
from json                 import dump as jdump, load as jload, dumps as jdumps, loads as jloads
from math                 import ceil, floor
from mmap                 import mmap
from os                   import remove, urandom, sep
from os.path              import abspath, dirname, join, realpath, basename, getsize, splitext
from re                   import split as regsplit, match as regmatch, compile as regcompile, search as regsearch
from time                 import time, sleep
from impra.imap           import ImapHelper, ImapConfig, BadLoginException
from impra.util           import __CALLER__, RuTime, formatBytes, randomFrom, bstr, quote_escape, stack, run, file_exists, get_file_content, DEBUG, mkdir_p, is_binary, clear, Clz, mprint
from impra.crypt          import Kirmah, ConfigKey, Noiser, Randomiz, hash_sha256, hash_md5_file, BadKeyException, hash_sha256_file
from sys                  import exit as sysexit

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class FSplitter ~~

class FSplitter :
    """"""
    
    def __init__(self, ck, wkdir='./'):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        self.ck         = ck
        self.wkdir      = wkdir
        self.DIR_CACHE  = join(self.wkdir,'.cache')+sep
        self.DIR_INBOX  = join(self.wkdir,'inbox')+sep
        self.DIR_OUTBOX = join(self.wkdir,'outbox')+sep
        self.DIR_DEPLOY = join(self.wkdir,'deploy')+sep
        rt.stop()
    
    def addFile(self, fromPath, label, fixCount = False):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        fsize = getsize(fromPath)
        count = ceil(fsize/self.ck.psize)
        minp, maxp = 52, 62
        if   fsize < 4800000   : minp, maxp =  8, 16
        elif fsize < 22200000  : minp, maxp = 16, 22
        elif fsize < 48000000  : minp, maxp = 22, 32
        elif fsize < 222000000 : minp, maxp = 32, 42
        if not fixCount :
            if count < minp : count = randomFrom(maxp,minp)
        else: count = fixCount
        if not count > 62 :
            hlst   = self._split(fromPath, self.ck.getHashList(label,count, True))            
        else : 
            raise Exception(fromPath+' size exceeds limits (max : '+formatBytes(self.ck.psize*62)+' ['+str(self.ck.psize*64)+' bytes])')
        rt.stop()
        return hlst

    def _split(self, fromPath, hlst):
        """"""
        rt = RuTime(eval(__CALLER__()),DEBUG.INFO)
        f = open(fromPath, 'rb+')
        m = mmap(f.fileno(), 0)
        p = 0
        psize = ceil(getsize(fromPath)/hlst['head'][1])
        Clz.print(' '+formatBytes(getsize(fromPath)), Clz.fgB2, False)
        Clz.print(' on '                        , Clz.fgn7, False)
        Clz.print(str(len(hlst['data']))        , Clz.fgB1, False)
        Clz.print(' parts (~'                   , Clz.fgn7, False)
        Clz.print(formatBytes(psize)            , Clz.fgB2, False)
        Clz.print(')'                           , Clz.fgn7)
        while m.tell() < m.size():
            self._splitPart(m,p,psize,hlst['data'][p])
            p += 1
        m.close()
        hlst['data'] = sorted(hlst['data'], key=lambda lst: lst[4])
        hlst['head'].append(psize)
        rt.stop()
        return hlst

    def _splitPart(self,mmap,part,size,phlst):
        """"""
        rt = RuTime(eval(__CALLER__('mmap,%s,%s,phlist' % (part,size))))
        with open(self.DIR_OUTBOX+phlst[1]+'.ipr', mode='wb') as o:
            #~ mprint(self.DIR_OUTBOX+phlst[1]+'.ipr')
            #~ mprint(str(phlst[2])+' - '+str(size)+' - '+str(phlst[3])+' = '+str(phlst[2]+size+phlst[3]))
            o.write(self.ck.noiser.getNoise(phlst[2])+mmap.read(size)+self.ck.noiser.getNoise(phlst[3]))
            
        rt.stop()
        
    def deployFile(self, hlst, fileName, ext='', uid='', dirs=None, fake=False):
        """"""
        rt = RuTime(eval(__CALLER__()))
        p = 0
        hlst['data'] = sorted(hlst['data'], key=lambda lst: lst[0])
        
        if dirs is not None and dirs!='none' :
            dirPath = join(self.DIR_DEPLOY,dirs)+sep
            mkdir_p(dirPath)
        else: dirPath = self.DIR_DEPLOY
        
        filePath = dirPath+fileName
        if file_exists(filePath+ext):
            Clz.print('\n name already exist, deploying file as :' , Clz.fgB1)
            Clz.print(' '+basename(filePath)                       , Clz.fgB2, False)
            Clz.print('-'+str(uid)                                 , Clz.fgB1, False)
            Clz.print(ext                                          , Clz.fgB2)
            filePath += '-'+str(uid)
        else :
            Clz.print('\n deploying file as :' , Clz.fgn7)
            Clz.print(' '+basename(filePath)+ext                   , Clz.fgB2, False)
        filePath += ext
        filePath = abspath(filePath)
        fp = open(filePath, 'wb+')
        depDir = self.DIR_INBOX
        if fake : depDir = self.DIR_OUTBOX
        while p < hlst['head'][1] :
            self._mergePart(fp,p,hlst['data'][p],depDir)
            p += 1
        fp.close()
        rt.stop()
        return filePath

    def _mergePart(self,fp,part,phlst,depDir):
        """"""
        rt = RuTime(eval(__CALLER__('fp,%s,phlist,depDir' % part)))
        with open(depDir+phlst[1]+'.ipr', mode='rb') as o:
            fp.write(o.read()[phlst[2]:-phlst[3]])
            o.close()
        remove(depDir+phlst[1]+'.ipr')
        rt.stop()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraConf ~~

class ImpraConf:
    """"""
    
    SEP_SECTION = '.'
    """"""
    
    def __init__(self, iniFile, profile='default'):
        """"""
        self.profile = profile
        self.ini = iniFile
        save = False
        if self.ini.isEmpty():
            save = True
            kg = crypt.KeyGen(256)
            self.set('host' ,'host','imap')
            self.set('port' ,'993','imap')
            self.set('user' ,'login','imap')
            self.set('pass' ,'password','imap')
            self.set('box'  ,'__IMPRA','imap')
            self.set('key'  ,kg.key,'keys')
            self.set('mark' ,kg.mark,'keys')
            self.set('salt' ,'-¤-ImpraStorage-¤-','keys')
        if not self.ini.hasSection(self.profile+self.SEP_SECTION+'catg'):
            save = True
            try:
                self.set('users', self.get('name','infos'),'catg')
            except Exception : pass
            self.set('types', 'music,films,doc,images,archives,games','catg')
        if save : 
            self.ini.write()
    
    def get(self, key, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        v = None
        if self.ini.has(key,profile+self.SEP_SECTION+section):
            v = self.ini.get(key, profile+self.SEP_SECTION+section)
        return v
    
    def set(self, key, value, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        v = self.ini.set(key, value, profile+self.SEP_SECTION+section)
        self.ini.write()
        return v

    def rem(self, key, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        v = self.ini.rem(key, profile+self.SEP_SECTION+section)
        self.ini.write()
        return v


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraIndex ~~

class ImpraIndex:
    """A representation of the index stored on the server"""
    
    SEP_ITEM       = '―'
    """Separator used for entry"""
    
    SEP_TOKEN      = '#'
    """Separator used for token"""
    
    SEP_CATEGORY   = '¤'
    """Separator used for category section"""
    
    QUOTE_REPL     = '§'
    """Char replacement of simple quote String"""
    
    SEP_KEY_INTERN = '@'
    """Separator used for internal key such categories"""
    
    HASH           = 0
    """"""
    LABEL          = 1
    """"""
    PARTS          = 2
    """"""
    EXT            = 3    
    """"""
    USER           = 4
    """"""
    CATG           = 5
    """"""
    UID            = 6
    """"""
    BFLAG          = 7
    """"""
    SIZE           = 8
    """"""
    ACCOUNT        = 9
    """"""    
    FILE_BINARY    = 'b'
    """"""
    FILE_CRYPT     = 'c'
    """"""
    COLS           = ('HASH','LABEL','PART','TYPE','USER','CATEGORY','ID','BLFAG','SIZE')
    """"""
    
    def __init__(self, key, mark, encdata='', dicCategory={}):
        """Initialize the index with rsa and encoded data

        :Parameters:
            `key`     : str
                appropriate key to decrypt/encrypt data
            `mark`    : str
                appropriate mark to check correct key
            `encdata` : str
                initial content of the index encrypted with Kirmah Algorythm 
                and representing a dic index as json string
        """
        rt    = RuTime(eval(__CALLER__()))
        self.km   = Kirmah(key, mark)
        self.dic  = {}        
        if encdata =='' :
            self.dic = {}
            self.id = 1
        else :
            self.dic = self.decrypt(encdata)
            l = [self.dic[k][self.UID] for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
            if len(l) > 0 :
                self.id = max(l)+1
            else: self.id = 1
        for k in dicCategory :
            if k == "users" :
                for k1 in dicCategory[k]:
                    if self.SEP_KEY_INTERN+k in self.dic:
                        if k1 not in self.dic[self.SEP_KEY_INTERN+k]:
                            self.dic[self.SEP_KEY_INTERN+k][k1] = dicCategory[k][k1]
            else :
                if not self.SEP_KEY_INTERN+k in self.dic:
                    self.dic[self.SEP_KEY_INTERN+k] = dicCategory[k]
        rt.stop()

    def add(self,key, label, count, ext='', usr='', cat='', md5='', bFlag='b', size='', account=''):
        """Add an entry to the index
        """
        rt    = RuTime(eval(__CALLER__()))
        if self.get(md5) == None : 
            self.dic[md5] = (key,label,count,ext,usr,cat,self.id,bFlag,size,account)
            self.id +=1
        else : 
            mprint(label+' already exist')
        rt.stop()

    def addUser(self, nameFrom, hashName):
        """"""
        if not self.hasUser(hashName):
            self.dic[self.SEP_KEY_INTERN+'users'][hashName] = nameFrom
    
    def hasUser(self, hashName):
        """"""
        if not self.SEP_KEY_INTERN+'users' in self.dic:
            self.dic[self.SEP_KEY_INTERN+'users'] = {}
        return hashName in self.dic[self.SEP_KEY_INTERN+'users']
            
    def getUser(self, hashName):
        """"""
        usrName = 'Anonymous'
        if self.hasUser(hashName):
            usrName = self.dic[self.SEP_KEY_INTERN+'users'][hashName]
        return usrName

    def rem(self,label):
        """Remove the selected label from the index"""
        self.dic.pop(label, None)
    
    def getAutoCatg(self,ext):
        """"""
        catg = 'none'
        if regsearch('\.(jpg|jpeg|gif|png)',ext):
            catg = 'images'
        elif regsearch('\.(txt|doc|odt|csv|pdf)',ext):
            catg = 'doc'
        elif regsearch('\.(mp4|avi|mpg|mpeg|flv|ogv)',ext):
            catg = 'films'
        elif regsearch('\.(mp3|ogg|flac)',ext):
            catg = 'music'
        elif regsearch('\.(zip|7z|tar|gz|rar|bz|xz|jar)',ext):
            catg = 'archives'
        return catg
        
    def isEmpty(self):
        """"""
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        return len(r) == 0
        
    def getLabel(self, key):
        """Get label corresponding to key in the index
        :Returns: `str`|None label
        """
        value = ''
        row   = self.get(key)
        if row is not None :
            value = row[self.LABEL]

    def get(self, key):
        """Get the corresponding key in the index
        :Returns: `tuple` row
        """
        row = None
        if key in self.dic : row = self.dic.get(key)
        return row

    def edit(self, key, label=None, category=None):
        """Get the corresponding key in the index
        :Returns: `tuple` row
        """
        rt    = RuTime(eval(__CALLER__()))
        done = False
        row  = self.dic[key]
        r    = list(row)
        if label != None :
            r[self.LABEL] = label
        if category != None :
            r[self.CATG] = category
        self.dic[key] = tuple(r)
        done = row != self.dic[key]
        rt.stop()
        return done
        
    def getById(self,sid):
        """Get the corresponding id in the index
        :Returns: `str`|None key
        """
        rt = RuTime(eval(__CALLER__(sid)))
        l  = None
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and self.dic[k][self.UID] == int(sid)]
        if len(r)==1: l = r[0]
        rt.stop()
        return l

    def fixAccount(self,account):
        """"""
        rt    = RuTime(eval(__CALLER__('%s' % account)))
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        for k in r:
            t = list(self.dic[k])
            if len(t)-1 < self.ACCOUNT:
                t.append(account)
            else:
                t[self.ACCOUNT] = account
            self.dic[k] = tuple(t)
        rt.stop()

    def getLightestAccount(self,l):
        """"""
        rt    = RuTime(eval(__CALLER__('%s' % str(l))))
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        t = {}
        for k in r:
            if not self.dic[k][self.ACCOUNT] in t: t[self.dic[k][self.ACCOUNT]] = self.dic[k][self.SIZE]
            else: t[self.dic[k][self.ACCOUNT]] += int(self.dic[k][self.SIZE])
        profile = None
        r = []
        for a in l:
            if not a in t :
                profile = a
                break
            else : r.append((t[a],a))
        if profile is None :
            d = sorted(r, reverse=False, key=lambda lst:lst[0])
            profile = d[0][1]
        rt.stop()
        return profile

    def fixDuplicateIds(self):
        """Get corresponding keys of duplicate ids in the index
        :Returns: `str`|None key
        """
        rt = RuTime(eval(__CALLER__()))
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        l = [(k,self.dic[k][self.UID]) for k in r]
        l2 = [k[1] for k in l]
        if len(l2)> 0 :
            mxid = max(l2)
            import collections
            l3 = [x for x, y in collections.Counter(l2).items() if y > 1]
            d  = [k[0] for k in l if any( k[1] == v for v in l3)]
            for k in d:
                mxid += 1
                #mprint(self.dic[k])
                t = list(self.dic[k])
                t[self.UID] = mxid
                #mprint(t)
                self.dic[k] = tuple(t)
            self.id = mxid+1
        else:
            self.id = 1
            d = ()
        rt.stop()
        return len(d)>0

    def getByLabel(self,label):
        """Get the corresponding label in the index
        :Returns: `str`|None key
        """
        rt = RuTime(eval(__CALLER__(sid)))
        l  = None
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and self.dic[k][self.LABEL] == int(label)]
        if len(r)==1: l = r[0]
        rt.stop()
        return l
    
    def getByPattern(self,pattern):
        """Get ids corresponding to label matching the pattern in the index
        :Returns: `[uid]`|None matchIds
        """
        rt = RuTime(eval(__CALLER__(pattern)))
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(pattern,self.dic[k][self.LABEL]) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        rt.stop()
        return l
    
    def getByCategory(self,category):
        """Get ids corresponding to category
        :Returns: `[uid]`|None matchIds
        """
        rt = RuTime(eval(__CALLER__(category)))
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(category,self.dic[k][self.CATG]) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        rt.stop()
        return l
        
    def getByUser(self,user):
        """Get ids corresponding to category
        :Returns: `[uid]`|None matchIds
        """
        rt = RuTime(eval(__CALLER__(user)))
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(user,self.getUser(self.dic[k][self.USER])) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        rt.stop()
        return l
        
    def getIntersection(self,list1, list2):
        """Get ids intercept list1 and list2
        :Returns: `[uid]`|None matchIds
        """
        rt = RuTime(eval(__CALLER__()))
        l = [ i for i in set(list1).intersection(set(list2))]
        rt.stop()
        return l

    def encrypt(self):
        """"""
        #~ mprint('encrypting index :')
        jdata = jdumps(self.dic)
        #~ mprint(jdata)
        return self.km.encrypt(jdata,'.index',22)

    def decrypt(self,data):
        """"""
        #~ mprint('decrypting index : ')
        try :
            jdata = self.km.decrypt(data,'.index',22)
            data  = jloads(jdata)
        except ValueError as e:
            raise BadKeyException(e)
        return data

    def print(self,order='ID', matchIds=None):
        """Print index content as formated bloc"""
        #clear()
        from impra.cli import printLineSep, LINE_SEP_LEN, LINE_SEP_CHAR
        inv    = order.startswith('-')
        if inv : order = order[1:]
        orderIndex = self.COLS.index(order)
        if orderIndex is None : orderIndex = self.COLS.index('ID')
        
        d = sorted([(self.dic.get(k),k) for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)], reverse=inv, key=lambda lst:lst[0][orderIndex])

        sizeid = 1+ceil(len(d))
        if sizeid < 3 : sizeid = 3
        sizeid = 3
        addsize = abs(3 - sizeid); 

        Clz.print(' ID'+' '*(1+addsize), Clz.BG4+Clz.fgB7, False, False)
        mprint('HASH'  +' '*6 , end='')
        mprint('LABEL' +' '*(35), end='')
        mprint('SIZE'  +' '*5 , end='')
        mprint('PART'  +' '*2 , end='')
        mprint('TYPE'  +' '*2 , end='')
        mprint('USER'  +' '*7 , end='')
        #mprint('CATEGORY'+' '*(17-addsize))
        mprint('CATEGORY'+' '*(17-addsize), end='')
        Clz.print('ACCOUNT'+' '*(2), Clz.BG4+Clz.fgB7)
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)        
        dbg = DEBUG.active
        DEBUG.active = True        
        a = ''
        tsize = 0
        psize = 0
        acc   = {}
        for v,k in d :
            if matchIds==None or v[self.UID] in matchIds:
                a = ''
                Clz.print(str(v[self.UID]).rjust(sizeid,' '), Clz.bg1+Clz.fgB7, False)
                Clz.print(' '+str(k)[0:6]+'... '                                 , Clz.fgN2, False)
                if len(v[self.LABEL])>36 : a = '...'
                Clz.print(str(v[self.LABEL][:36]+a).ljust(40,' ')                , Clz.fgN7, False)
                a = ''
                Clz.print(formatBytes(int(v[self.SIZE]))[:8].rjust(8,' ')+' '*2  , Clz.fgN5, False)
                Clz.print(str(v[self.PARTS]).rjust(2 ,'0') +' '*2                , Clz.fgN1, False)
                Clz.print(str(v[self.EXT][:5]).ljust(7,' ')                      , Clz.fgn3, False)
                Clz.print(self.getUser(str(v[self.USER])).ljust(11  ,' ')        , Clz.fgn7, False)
                #~ Clz.print(str(v[self.CATG]).ljust(30 ,' ')                       , Clz.fgN3)
                if len(v[self.CATG])>22 : a = '...'
                Clz.print(str(v[self.CATG]+a).ljust(25 ,' ')                     , Clz.fgN3, False)
                if len(v)-1==self.ACCOUNT:
                    Clz.print(str(v[self.ACCOUNT]).ljust(14 ,' ')                , Clz.fgN3)
                    if v[self.ACCOUNT] in acc :
                        acc[v[self.ACCOUNT]] += int(v[self.SIZE])
                    else : acc[v[self.ACCOUNT]] = int(v[self.SIZE])
                else: mprint()

                psize += int(v[self.SIZE])
            tsize += int(v[self.SIZE])
        if len(d)==0:
            Clz.print(' empty', Clz.fgB1)
        DEBUG.active = dbg
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        c = Clz.fgB2
        if psize != tsize : c = Clz.fgB7
        Clz.print(' size : ', Clz.fgB3, False)
        Clz.print(formatBytes(int(psize))[:9].rjust(9,' '), c, False)
        if psize != tsize :
            Clz.print(' / ', Clz.fgB3, False)
            Clz.print(formatBytes(int(tsize)), Clz.fgB2, False)
        mprint()
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)

        #~ Clz.print(' '*4+'[', Clz.fgB7, False)
        #~ sep = ''
        #~ for k in acc:
            #~ if k!= '':
                #~ Clz.print(sep+k,Clz.fgB3,False)
                #~ Clz.print(':',Clz.fgB7,False)
                #~ Clz.print(formatBytes(acc[k]),Clz.fgB2,False)
                #~ if sep=='':sep = ','
        #~ Clz.print(']', Clz.fgB7, False)
        #~ mprint()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class ImpraStorage:
    """"""
    
    def __init__(self, conf, remIndex=False, wkdir=None):
        """"""
        rt = RuTime(eval(__CALLER__()),DEBUG.INFO)
        if wkdir == None : wkdir = abspath(join(dirname( __file__ ), '..', 'wk'))
        self.wkdir   = wkdir
        self.conf    = conf
        self.pathInd = dirname(self.conf.ini.path)+sep+'.index'
        self.rootBox = self.conf.get('box','imap')        
        self.mb      = MailBuilder(self.conf.get('salt','keys'))
        self.fsplit  = FSplitter(ConfigKey(),self.wkdir)
        self.delids  = []
        self.ih      = None
        self._setIndexImap()
        if remIndex  : self.removeIndex()
        self.getIndex()
        rt.stop()

    def _setIndexImap(self):
        iconf        = ImapConfig(self.conf.get('host','imap'), self.conf.get('port','imap'), self.conf.get('user', 'imap'), self.conf.get('pass', 'imap'))
        try :
            if self.rootBox == None :
                self.rootBox = '__impra__'
                self.conf.set('box',self.rootBox,'imap')
            if self.ih is None or self.ih.conf.user != iconf.user :
                try :
                    self.ih  = ImapHelper(iconf,self.rootBox)
                except BadLoginException as e1:
                    Clz.print('Error :', Clz.fgB1, True, False)
                    mprint(e1)
                    Clz.print('', Clz.OFF)
                    sysexit(1)

        except Exception as e:
            Clz.print('Error :', Clz.fgB1, True, False)
            mprint(e)
            Clz.print('check your connection or your imap config', Clz.fgB1)
            sysexit(1)

    def _getIdIndex(self):
        """"""
        mid = None
        ids = self.ih.searchBySubject(self.mb.getHashName('index'),True)
        if len(ids) > 0 and int(ids[0]) >= 0 :
            mid = ids[len(ids)-1]
            for i in ids:
                if i != mid : self.delids.append(i)
        self.idx = mid
        return mid

    def _getIdsBySubject(self,subject):
        """"""
        status, resp = self.ih.srv.search(None, '(SUBJECT "%s")' % subject)
        ids = [m for m in resp[0].split()]
        return ids

    def _getCryptIndex(self):
        """"""
        encData = ''
        if not self.idx : self._getIdIndex()
        if self.idx :
            msgIndex = self.ih.email(self.idx, True)
            if msgIndex != None :                
                for part in msgIndex.walk():
                    ms  = part.get_payload(decode=True)
                encData = str(ms,'utf-8')
        return encData

    def getIndexDefaultCatg(self):
        """"""
        usrName  = self.conf.get('name','infos')
        defUsers = self.conf.get('users','catg').split(',')
        dic      = {'catg':self.conf.get('types','catg'), 'users':{ ('%s' % self.mb.getHashName('all')) : 'all', ('%s' % self.mb.getHashName(usrName)) : usrName}}
        for u in defUsers :
           dic['users'][('%s' % self.mb.getHashName(u.strip()))] = u.strip()
        return dic

    def getIndex(self, forceRefresh=False):
        """"""
        rt = RuTime(eval(__CALLER__()),DEBUG.INFO)
        index   = None
        encData = ''
        uid     = self.conf.get('uid'  ,'index')
        date    = self.conf.get('date ','index')
        tstamp  = self.conf.get('time' ,'index')
        refresh = forceRefresh
        if not refresh and tstamp is not None and (datetime.now() - datetime.strptime(tstamp[:-7], '%Y-%m-%d %H:%M:%S')) < timedelta(minutes = 1) :
            # getFromFile
            if uid != None and file_exists(self.pathInd): # int(self.idx) == int(uid) 
                self.idx = uid
                encData = get_file_content(self.pathInd)
                Clz.print(' get index from cache', Clz.fgn7)
            else: refresh = True
        else: refresh = True
        self.irefresh = refresh
        if refresh :
            Clz.print(' refreshing index', Clz.fgn7)
            self._getIdIndex()
            if self.idx :
                encData = self._getCryptIndex()
                with open(self.pathInd, mode='w', encoding='utf-8') as o:
                    o.write(encData)
                self.conf.set('time',str(datetime.now()),'index')
        self.importIndex(encData)
        rt.stop()

    def importIndex(self, encData):
        self.index = ImpraIndex(self.conf.get('key','keys'),self.conf.get('mark','keys'), encData, self.getIndexDefaultCatg())
        defUsers = self.conf.get('users','catg')
        if not ImpraIndex.SEP_KEY_INTERN+'users' in self.index.dic:
            self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'] = {}
        for k in self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users']:
            if self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'][k] not in [ i.strip() for i in defUsers.split(',')]:
                self.conf.set('users',defUsers+', '+self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'][k],'catg')
        
    def removeIndex(self):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        self._getIdIndex()
        if self.idx :
            self.ih.delete(self.idx, True)
        self.ih.deleteBin()
        self.conf.rem('*','index')        
        self.idx = None
        remove(self.pathInd)
        rt.stop()

    def saveIndex(self):
        """"""
        rt = RuTime(eval(__CALLER__()),DEBUG.INFO)
        try:
            if self.idx != None :
                self.ih.delete(self.idx, True)
        except Exception as e :
            mprint('error : ')
            mprint(e)            
        #~ if len(self.delids) > 0 :
            #~ for i in self.delids : self.ih.delete(i, True, False)
            #~ Clz.print('\n expunge, waiting server...\n', Clz.fgB1)
            #~ self.srv.expunge()
            #~ sleep(2)
        self.index.fixDuplicateIds()
        #~ self.index.fixAccount('gmail5')
        encData  = self.index.encrypt() 
        msgIndex = self.mb.buildIndex(encData)        
        if DEBUG.level <= DEBUG.NOTICE : mprint(msgIndex.as_string())
        ids = self.ih.send(msgIndex.as_string(), self.rootBox)
        date = self.ih.headerField('date', ids[1], True)
        self.conf.set('uid',ids[1],'index')
        self.conf.set('date',date,'index')
        with open(self.pathInd, mode='w', encoding='utf-8') as o:
            o.write(encData)
        self.conf.set('time',str(datetime.now()),'index')
        self.clean()
        rt.stop()
        return True
    
    def encryptTextFile(self,path):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        cdata = self.index.km.subenc(get_file_content(path))
        with open(self.fsplit.DIR_CACHE+'.~KirmahEnc', mode='w') as o:
            o.write(cdata)
        rt.stop()
        return self.fsplit.DIR_CACHE+'.~KirmahEnc'
        
    def decryptTextFile(self,path):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        data  = self.index.km.subdec(get_file_content(path))
        with open(path, mode='w') as o:
            o.write(data)
        rt.stop()
    
    def checkSendIds(self,sendIds,subject):
        """"""
        lloc = [bytes(str(data[0]),'utf-8') for mid, data in enumerate(sendIds)]
        lsrv = self.ih.searchBySubject(subject,True)
        return  [ int(i) for i in set(lloc).difference(set(lsrv))]
    
    def switchFileAccount(self,profile=None):
        """"""
        rt    = RuTime(eval(__CALLER__('%s' % str(profile))))
        pl = self.conf.get('multi','imap')
        if pl is not None :
            pl = pl.split(',')
            if len(pl) > 0:
                if not self.conf.profile in pl:
                    pl.append(self.conf.profile)
                iconf   = self.ih.conf
                account = self.conf.get('user','imap',profile)
                if True or iconf.user != account :
                    # reinit
                    iconf.user = None
                    try :
                        if profile is None : profile = self.index.getLightestAccount(pl)
                        if profile in pl :
                            iconf.user = self.conf.get('user','imap',profile)
                            iconf.pwd  = self.conf.get('pass','imap',profile)
                            iconf.host = self.conf.get('host','imap',profile)
                            iconf.port = self.conf.get('port','imap',profile)
                        self.ih = ImapHelper(iconf,self.rootBox)
                    except Exception as e:
                        mprint('Error : ')
                        mprint(e)
                        mprint('check your connection or your imap config for profile '+profile)
        rt.stop()
        if profile is None: profile = self.conf.profile
        return profile
    
    def addFile(self, path, label, catg=''):
        """"""
        done = False
        rt = RuTime(eval(__CALLER__()),DEBUG.INFO)
     
        account = self.switchFileAccount()       

        _, ext = splitext(path)
        #~ try:
        size = getsize(path)
        if size > 0 :
            md5     = hash_sha256_file(path)
            mprint()
            Clz.print(' account : '       , Clz.fgn7, False)
            Clz.print(self.ih.conf.user   , Clz.fgB7)
            Clz.print(' file    : '       , Clz.fgn7, False)
            Clz.print(path                , Clz.fgN1)
            Clz.print(' hash    : '       , Clz.fgn7, False)                
            Clz.print(md5                 , Clz.fgN2)
            mprint()
            if not self.index.get(md5) :
                
                if catg=='' : catg = self.index.getAutoCatg(ext)
                
                bFlag = ImpraIndex.FILE_BINARY
                if not is_binary(path): 
                    bFlag = ImpraIndex.FILE_CRYPT
                    path  = self.encryptTextFile(path)
                    
                hlst = self.fsplit.addFile(path,md5)
                if DEBUG.active and DEBUG.level <= DEBUG.NOTICE : 
                    mprint(hlst['head'])
                    for v in hlst['data']:
                        mprint(v)
                
                usr = self.conf.get('name','infos')
                ownerHash = self.mb.getHashName(usr)
                self.index.addUser(usr,ownerHash)
                
                cancel  = False
                sendIds = []
                test    = True
                for row in hlst['data'] :
                    msg  = self.mb.build(usr,'all',hlst['head'][2],self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                    mid  = None
                    try :
                        mid  = self.ih.send(msg.as_string(), self.rootBox)
                    except Exception as e:
                        Clz.print('Error :', Clz.fgB1, True, False)
                        mprint(e)
                        Clz.print('retry', Clz.fgB1)
                        self.switchFileAccount(account)
                        mid  = self.ih.send(msg.as_string(), self.rootBox)
                    
                    if mid is not None :
                        #sleep(0.5)
                        # dont remove
                        status, resp = self.ih.fetch(mid[1],'(UID BODYSTRUCTURE)', True)
                        if status == self.ih.OK:
                            sendIds.append((mid[1],row))
                            mprint(' ',end='')
                            Clz.print('part '        , Clz.fgn7, False)
                            Clz.print(str(row[0])    , Clz.fgB2, False)
                            Clz.print(' sent as msg ', Clz.fgn7, False)
                            Clz.print(str(mid[1])    , Clz.fgB1)
                        else:
                            mprint('\n-- error occured when sending part : %s\n-- retrying' % row[0])

                if not cancel :

                    diff = self.checkSendIds(sendIds,hlst['head'][2])
                    #~ mprint('diff')
                    #~ for mid in diff :
                        #~ if mid > 0:
                            #~ mprint(mid)
                            #self.ih.delete(str(mid), True, False)
                    if len(diff) > 0 :                        
                        for mid in diff :
                            status, resp = self.ih.fetch(str(mid),'(UID BODYSTRUCTURE)', True)
                            if not status == self.ih.OK:
                                Clz.print(' error when sending, missing parts :', Clz.fgB1)
                                # bugfix mid would be without +1
                                k = [ k for k in sendIds if len(k)>0 and int(k[0]) == int(mid+1)]
                                if len(k) > 0 :
                                    mprint(k)
                                    row = k[0][1]
                                    msg  = self.mb.build(usr,'all',hlst['head'][2],self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                                    if DEBUG.active :
                                        Clz.print(' resending part '      , Clz.fgn7, False)
                                        Clz.print(str(row[0])             , Clz.fgN2)
                                    mid  = self.ih.send(msg.as_string(), self.rootBox)
                    else :
                        mprint()
                        #Clz.print(' index intall files checked\n', Clz.fgB2)
                    self._setIndexImap()
                    self.getIndex(True)
                    self.index.add(hlst['head'][3],label,hlst['head'][1],ext,ownerHash,catg,md5,bFlag,size,account)                        
                    done = self.saveIndex()    
                
                # clean 
                for mid, row in sendIds :
                    if cancel : self.ih.delete(mid, True)
                    if file_exists(self.fsplit.DIR_OUTBOX+row[1]+'.ipr') : remove(self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                self.clean()

            else :
                mprint(' ',end='')
                Clz.print(' == file already exist on server as '    , Clz.fgN7+Clz.bg1, False)
                Clz.print(self.index.dic[md5][ImpraIndex.LABEL]     , Clz.bg1+Clz.fgB3, False)
                Clz.print(' [id:'                                   , Clz.fgN7+Clz.bg1, False)
                Clz.print(str(self.index.dic[md5][ImpraIndex.UID])  , Clz.bg1+Clz.fgB3, False)
                Clz.print('] == '                                   , Clz.fgN7+Clz.bg1)
                mprint()
        else :
            mprint(' ',end='')
            Clz.print(' == files is empty or don\t exists == ' , Clz.bg1+Clz.fgN7)
            mprint()
                
        #~ except Exception as e :
            #~ mprint('Erroreuh')
            #~ mprint(e)
        self._setIndexImap()
        rt.stop()
        return done


    def editFile(self,key,label,category):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        done = False
        row  = self.index.get(key)
        if row==None : 
                mprint()
                Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                Clz.print(str(key)                 , Clz.bg1+Clz.fgB3, False)
                Clz.print('` not on the server == ', Clz.bg1+Clz.fgB7)
                mprint()
        else :
            done = self.index.edit(key,label,category)
        rt.stop()
        return done

    def removeFile(self,key):
        """"""
        done = False
        row  = self.index.get(key)
        if row==None : 
                mprint()
                Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                Clz.print(str(key)                 , Clz.bg1+Clz.fgB3, False)
                Clz.print('` not on the server == ', Clz.bg1+Clz.fgB7)
                mprint()
        else :
            rt  = RuTime(eval(__CALLER__('"[%i] %s"' % (row[ImpraIndex.UID],row[ImpraIndex.LABEL]))),DEBUG.INFO)
            self.switchFileAccount(row[ImpraIndex.ACCOUNT])
            account = self.ih.conf.user
            if DEBUG.active : 
                Clz.print(' account : '       , Clz.fgn7, False)
                Clz.print(account             , Clz.fgB7)
            ck    = ConfigKey(row[ImpraIndex.HASH])
            hlst  = ck.getHashList(key,row[ImpraIndex.PARTS],True)
            Clz.print(' get file list from server', Clz.fgn7)
            ids   = self.ih.searchBySubject(hlst['head'][2], True)
            for mid in ids :
                self.ih.delete(mid, True, False)
            Clz.print('\n expunge, waiting pls...\n', Clz.fgB1)
            self.ih.srv.expunge()
            sleep(0.5)
            self._setIndexImap()
            self.getIndex(True)
            self.index.rem(key)
            done = self.saveIndex()
            rt.stop()
        return done
        
    def getFile(self,key):
        """"""
        done  = False
        row   = self.index.get(key)
        if row==None : 
            mprint()
            Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
            Clz.print(str(key)                 , Clz.bg1+Clz.fgB3, False)
            Clz.print('` not on the server == ', Clz.bg1+Clz.fgB7)
            mprint()
            
        else :
            rt  = RuTime(eval(__CALLER__('"[%i] %s"' % (row[ImpraIndex.UID],row[ImpraIndex.LABEL]))),DEBUG.INFO)
            self.switchFileAccount(row[ImpraIndex.ACCOUNT])
            account = self.ih.conf.user
            Clz.print(' account : '       , Clz.fgn7, False)
            Clz.print(account             , Clz.fgB7)
            ck    = ConfigKey(row[ImpraIndex.HASH])
            hlst  = ck.getHashList(key,row[ImpraIndex.PARTS],True)
            ids   = self.ih.searchBySubject(hlst['head'][2],True)

            if len(ids) >= row[ImpraIndex.PARTS]:

                for mid in ids :
                    self.ih.downloadAttachment(mid,self.fsplit.DIR_INBOX, True)
                if DEBUG.active and DEBUG.level <= DEBUG.NOTICE : 
                    mprint(hlst['head'])
                    for v in hlst['data']:
                        mprint(v)
                path = self.fsplit.deployFile(hlst, row[ImpraIndex.LABEL],  row[ImpraIndex.EXT], row[ImpraIndex.UID], row[ImpraIndex.CATG])
                if row[ImpraIndex.BFLAG] == ImpraIndex.FILE_CRYPT:
                    self.decryptTextFile(path)
                mprint()
                Clz.print(' deploying in ', Clz.fgn7)
                Clz.print(' '+dirname(path), Clz.fgB2)
                mprint()
                done = True

            else :
                mprint()
                Clz.print(' == `'                         , Clz.BG3+Clz.fgB1, False)
                Clz.print(row[ImpraIndex.LABEL]           , Clz.BG3+Clz.fgB4, False)
                Clz.print('` invalid count parts '        , Clz.BG3+Clz.fgB1, False)
                Clz.print(str(len(ids))                   , Clz.BG3+Clz.fgB4, False)                
                Clz.print('/'                             , Clz.BG3+Clz.fgB1, False)
                Clz.print(str(row[ImpraIndex.PARTS])      , Clz.BG3+Clz.fgB4, False)
                Clz.print(' == '                          , Clz.BG3+Clz.fgB1)                
                mprint()
            self._setIndexImap()
            rt.stop()
        return done

    def clean(self):
        """"""
        rt = RuTime(eval(__CALLER__()))
        self.ih.deleteBin()
        if file_exists(self.fsplit.DIR_CACHE+'.~KirmahEnc'):remove(self.fsplit.DIR_CACHE+'.~KirmahEnc')
        rt.stop()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class MailBuilder ~~

class MailBuilder:
    """A simple mail builder to create mails for ImpraIndex and parts attchments"""

    DOMAIN_NAME = 'impra.storage'
    """Domain name used for from and to mail fields"""

    def __init__(self, salt=''):
        """"""
        self.salt = salt
    
    def getHashName(self, name):
        """Return a simplified hash of specified name
        :Returns: `str`
        """
        return hash_sha256(self.salt+name)[0:12]

    def build(self, nameFrom, nameTo, subject, filePath):
        """Build mail with attachment part
        :Returns: 'email.message.Message'
        """
        rt  = RuTime(eval(__CALLER__('%s' % basename(filePath))))
        msg = MIMEMultipart()
        msg['From']    = self.getHashName(nameFrom)+'@'+self.DOMAIN_NAME
        msg['To']      = self.getHashName(nameTo)+'@'+self.DOMAIN_NAME
        msg['Date']    = formatdate(localtime=True)
        msg['Subject'] = Header(subject,'utf-8')        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(filePath, 'rb').read())
        encode_base64(part)
        part.add_header('Content-Disposition','attachment; filename="%s"' % basename(filePath))
        msg.attach(part)
        rt.stop()
        return msg
        
    def buildIndex(self, data):
        """Build mail for ImpraIndex
        :Returns: 'email.message.Message'
        """
        rt  = RuTime(eval(__CALLER__()))
        msg = MIMEMultipart()
        msg['From']    = self.getHashName('system')+'@'+self.DOMAIN_NAME
        msg['To']      = self.getHashName('all')+'@'+self.DOMAIN_NAME
        msg['Date']    = formatdate(localtime=True)
        msg['Subject'] = Header(self.getHashName('index'),'utf-8')
        msg.attach(MIMEText(data,_charset='utf-8'))
        rt.stop() 
        return msg
