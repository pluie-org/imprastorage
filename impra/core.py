#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.4                                                             #
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
from time                 import time
from impra.imap           import ImapHelper, ImapConfig
from impra.util           import __CALLER__, RuTime, formatBytes, randomFrom, bstr, quote_escape, stack, run, file_exists, get_file_content, DEBUG, DEBUG_ALL, DEBUG_LEVEL, DEBUG_NOTICE, DEBUG_WARN, mkdir_p, is_binary, clear, Clz
from impra.crypt          import Kirmah, ConfigKey, Noiser, Randomiz, hash_sha256, hash_md5_file, BadKeyException


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class FSplitter ~~

class FSplitter :
    """"""
    
    def __init__(self, ck, wkdir='./'):
        """"""
        self.ck         = ck
        self.wkdir      = wkdir
        self.DIR_CACHE  = join(self.wkdir,'.cache')+sep
        self.DIR_INBOX  = join(self.wkdir,'inbox')+sep
        self.DIR_OUTBOX = join(self.wkdir,'outbox')+sep
        self.DIR_DEPLOY = join(self.wkdir,'deploy')+sep
    
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
        rt = RuTime(eval(__CALLER__()))
        f = open(fromPath, 'rb+')
        m = mmap(f.fileno(), 0)
        p = 0
        psize = ceil(getsize(fromPath)/hlst['head'][1])
        print(formatBytes(getsize(fromPath))+' on '+str(len(hlst['data']))+' parts (~'+formatBytes(psize)+')')
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
            #~ print(self.DIR_OUTBOX+phlst[1]+'.ipr')
            #~ print(str(phlst[2])+' - '+str(size)+' - '+str(phlst[3])+' = '+str(phlst[2]+size+phlst[3]))
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
            print('\n-- `%s` already exist, deploying file as :\n-- `%s`\n' % (filePath+ext,filePath+'-'+str(uid)+ext))
            filePath += '-'+str(uid)
        filePath += ext
            
        fp = open(filePath, 'wb+')
        depDir = self.DIR_INBOX
        if fake : depDir = self.DIR_OUTBOX
        while p < hlst['head'][1] :
            self._mergePart(fp,p,hlst['data'][p],depDir)
            p += 1
        fp.close()
        rt.stop()
        return dirPath+fileName+ext

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
            #print(self.ini.toString())
    
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
    
    MD5            = 7
    """"""
    HASH           = 0
    """"""
    LABEL          = 1
    """"""
    PARTS          = 2
    """"""
    EXT            = 3    
    """"""
    OWNER          = 4
    """"""
    CATG           = 5
    """"""
    UID            = 6
    """"""
    BFLAG          = 7
    """"""
    
    FILE_BINARY    = 'b'
    FILE_CRYPT     = 'c'
    
    
    def __init__(self, key, mark, encdata='', dicCategory={}, id=0):
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
        self.km   = Kirmah(key, mark)
        self.dic  = {}
        self.id   = id
        if encdata =='' : self.dic = {}
        else : self.dic = self.decrypt(encdata)
        for k in dicCategory :
            if not self.SEP_KEY_INTERN+k in self.dic:
                self.dic[self.SEP_KEY_INTERN+k] = dicCategory[k]

    def add(self,key, label, count, ext='', usr='', cat='', md5='', bFlag='b'):
        """Add an entry to the index
        """
        if self.get(md5) == None : 
            self.dic[md5] = (key,label,count,ext,usr,cat, self.id, bFlag)
            self.id +=1
        else : 
            print(label+' already exist')

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

    def encrypt(self):
        """"""
        #~ print('encrypting index :')
        jdata = jdumps(self.dic)
        #~ print(jdata)
        return self.km.encrypt(jdata,'.index',22)

    def decrypt(self,data):
        """"""
        #~ print('decrypting index : ')
        try :
            jdata = self.km.decrypt(data,'.index',22)        
            data  = jloads(jdata)
        except ValueError as e:
            raise BadKeyException(e)
        return data

    def print(self,header='', matchIds=None):
        """Print index content as formated bloc"""
        #clear()
        if header is not '':print(header)
        from impra.cli import printLineSep, LINE_SEP_LEN, LINE_SEP_CHAR
        #printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print(' ID'+' '*1, Clz.BG4+Clz.fgB7, False, False)
        print('HASH'  +' '*15, end='')
        print('LABEL' +' '*38, end='')
        print('PART'  +' '*2 , end='')
        print('TYPE'  +' '*2 , end='')
        print('OWNER' +' '*12, end='')
        Clz.print('CATEGORY'+' '*17, Clz.BG4+Clz.fgB7)        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        data = ''
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        for k in r :
            v = self.dic.get(k)
            k = k.lstrip('\n\r')
            if not k[0]==self.SEP_KEY_INTERN and len(k)>1:
                if matchIds==None or v[self.UID] in matchIds:
                    Clz.print(str(v[self.UID]).rjust(1+ceil(len(str(v[self.UID]))/10),' ') +' '*2, Clz.fgB1, False)
                    Clz.print(str(k)[0:12]+'...  ' +' '*2, Clz.fgn2, False)
                    Clz.print(str(v[self.LABEL]).ljust(42,' ') +' '*2, Clz.fgB7, False)
                    Clz.print(str(v[self.PARTS]).rjust(2 ,'0') +' '*2, Clz.fgB5, False)
                    Clz.print(str(v[self.EXT]).ljust(5,' ') +' '*2, Clz.fgB4, False)
                    Clz.print(self.getUser(str(v[self.OWNER])).ljust(15,' ') +' '*2, Clz.fgB7, False)
                    Clz.print(str(v[self.CATG]) +' '*2, Clz.fgB4)

        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class ImpraStorage:
    """"""
    
    def __init__(self, conf, remIndex=False, wkdir=None):
        """"""
        from impra.util import DEBUG_INFO
        rt = RuTime(eval(__CALLER__()),DEBUG_INFO)
        if wkdir == None : wkdir = abspath(join(dirname( __file__ ), '..', 'wk'))
        self.wkdir   = wkdir
        self.conf    = conf
        self.pathInd = dirname(self.conf.ini.path)+sep+'.index'
        self.rootBox = self.conf.get('box','imap')
        iconf        = ImapConfig(self.conf.get('host','imap'), self.conf.get('port','imap'), self.conf.get('user', 'imap'), self.conf.get('pass', 'imap'))
        self.ih      = ImapHelper(iconf,self.rootBox)
        self.mb      = MailBuilder(self.conf.get('salt','keys'))
        self.fsplit  = FSplitter(ConfigKey(),self.wkdir)
        self.delids  = []
        if remIndex  : self.removeIndex()
        self.index   = self.getIndex()
        rt.stop()

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
        usrName = self.conf.get('name','infos')
        return {'catg':self.conf.get('types','catg'), 'users':{ ('%s' % self.mb.getHashName('all')) : 'all', ('%s' % self.mb.getHashName(usrName)) : usrName}}

    def getIndex(self):
        """"""
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_WARN, DEBUG_INFO       
        rt = RuTime(eval(__CALLER__()),DEBUG_INFO)
        index   = None
        encData = ''
        uid     = self.conf.get('uid'  ,'index')
        date    = self.conf.get('date ','index')
        nid     = self.conf.get('nid'  ,'index')
        tstamp  = self.conf.get('time' ,'index')
        if nid is None : nid = 0
        refresh = False
        if tstamp is not None and (datetime.now() - datetime.strptime(tstamp[:-7], '%Y-%m-%d %H:%M:%S')) < timedelta(minutes = 1) :
            # getFromFile
            if uid != None and file_exists(self.pathInd): # int(self.idx) == int(uid) 
                self.idx = uid
                encData = get_file_content(self.pathInd)
            else: refresh = True
        else: refresh = True
        if refresh :
            self._getIdIndex()
            if self.idx :
                encData = self._getCryptIndex()
                with open(self.pathInd, mode='w', encoding='utf-8') as o:
                    o.write(encData)
                self.conf.set('time',str(datetime.now()),'index')

        index = ImpraIndex(self.conf.get('key','keys'),self.conf.get('mark','keys'), encData, self.getIndexDefaultCatg(), int(nid))
        rt.stop()
        return index
        
    def removeIndex(self):
        """"""
        self._getIdIndex()
        if self.idx :
            self.ih.delete(self.idx, True)
        self.ih.deleteBin()
        self.conf.rem('*','index')        
        self.idx = None
        remove(self.pathInd)

    def saveIndex(self):
        """"""
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_NOTICE, DEBUG_WARN, DEBUG_INFO
        rt = RuTime(eval(__CALLER__()),DEBUG_INFO)
        if self.idx != None :
            self.ih.delete(self.idx, True)
        for i in self.delids : self.ih.delete(i, True)
        encData  = self.index.encrypt() 
        msgIndex = self.mb.buildIndex(encData)        
        if DEBUG and DEBUG_LEVEL <= DEBUG_NOTICE : print(msgIndex.as_string())
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
        cdata = self.index.km.subenc(get_file_content(path))
        with open(self.fsplit.DIR_CACHE+'.~KirmahEnc', mode='w') as o:
            o.write(cdata)
        return self.fsplit.DIR_CACHE+'.~KirmahEnc'
        
    def decryptTextFile(self,path):
        """"""
        data  = self.index.km.subdec(get_file_content(path))
        with open(path, mode='w') as o:
            o.write(data)            
    
    def addFile(self, path, label, usr='all', catg=''):
        """"""
        done = False
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_NOTICE, DEBUG_WARN, DEBUG_INFO
        rt = RuTime(eval(__CALLER__('"%s","%s","%s"' % (path[:13]+'...',label,usr))),DEBUG_INFO)

        _, ext = splitext(path)
        
        try:
            md5 = hash_md5_file(path)
            print('--\nmd5sum `%s` %s' % (path,md5))                
            if not self.index.get(md5) :
                
                if catg=='' : catg = self.index.getAutoCatg(ext)
                
                bFlag = ImpraIndex.FILE_BINARY
                if not is_binary(path): 
                    bFlag = ImpraIndex.FILE_CRYPT
                    path  = self.encryptTextFile(path)
                    
                hlst = self.fsplit.addFile(path,md5)
                if DEBUG and DEBUG_LEVEL <= DEBUG_NOTICE : 
                    print(hlst['head'])
                    for v in hlst['data']:
                        print(v)
                
                ownerHash = self.mb.getHashName(usr)
                self.index.addUser(usr,ownerHash)

                cancel  = False
                sendIds = []
                test    = True
                for row in hlst['data'] :
                    msg  = self.mb.build(self.conf.get('name','infos'),usr,hlst['head'][2],self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                    mid  = self.ih.send(msg.as_string(), self.rootBox)
                    if mid is not None :
                        print('part %s sent as msg %s' % (row[0],mid[1]))
                        sendIds.append((mid[1],row))
                        remove(self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                    else:
                        print('\n-- error occured when sending part : %s\n-- retrying' % row[0])
                        mid  = self.ih.send(msg.as_string(), self.rootBox)
                        if mid is not None :
                            print('part %s sent as msg %s' % (row[0],mid[1]))
                            sendIds.append((mid[1],row))
                            remove(self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                        else: 
                            print('\n-- can\'t send part %s\n-- cancelling ' % row[0])
                            cancel = True
                            break
                
                if cancel :
                    for mid, row in sendIds :
                        self.ih.delete(mid, True)
                        if file_exists(self.fsplit.DIR_OUTBOX+row[1]+'.ipr') : remove(self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                    self.clean()
                        
                else :
                    self.index.add(hlst['head'][3],label,hlst['head'][1],ext,ownerHash,catg,md5,bFlag)
                    done = self.saveIndex()
                    self.conf.set('nid', str(self.index.id),'index')
            else :
                print('--\nfile already exist on server as `%s` [id:%i]\n' % (self.index.dic[md5][ImpraIndex.LABEL],self.index.dic[md5][ImpraIndex.UID]))
        except Exception as e :
            print(e)
        rt.stop()
        return done

    def getFile(self,key):
        """"""
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_NOTICE, DEBUG_WARN, DEBUG_INFO
        done  = False
        row   = self.index.get(key)        
        if row==None : 
            print('--\n%s not on the server' % key)
        else :
            rt  = RuTime(eval(__CALLER__('"[%i] %s"' % (row[ImpraIndex.UID],row[ImpraIndex.LABEL]))),DEBUG_INFO)
            ck    = ConfigKey(row[ImpraIndex.HASH])
            hlst  = ck.getHashList(key,row[ImpraIndex.PARTS],True)
            ids   = self._getIdsBySubject(hlst['head'][2])
            if len(ids) >= row[ImpraIndex.PARTS]:
                status, resp = self.ih.srv.fetch(ids[0],'(BODY[HEADER.FIELDS (TO)])')
                to = bstr(resp[0][1][4:-4])
                if to == self.mb.getHashName('all')+'@'+self.mb.DOMAIN_NAME or to == self.mb.getHashName(self.conf.ini.get('name',self.conf.profile+'.infos'))+'@'+self.mb.DOMAIN_NAME :
                    for mid in ids :
                        self.ih.downloadAttachment(mid,self.fsplit.DIR_INBOX)
                    if DEBUG and DEBUG_LEVEL <= DEBUG_NOTICE : 
                        print(hlst['head'])
                        for v in hlst['data']:
                            print(v)
                    path = self.fsplit.deployFile(hlst, row[ImpraIndex.LABEL],  row[ImpraIndex.EXT], row[ImpraIndex.UID], row[ImpraIndex.CATG])
                    if row[ImpraIndex.BFLAG] == ImpraIndex.FILE_CRYPT:
                        self.decryptTextFile(path)
                    done = True
                else :
                    print('--\n`%s` is private' % row[ImpraIndex.LABEL])
            else :
                print('--\n`%s` invalid count parts %i/%i' %(row[ImpraIndex.LABEL],len(ids),row[ImpraIndex.PARTS]))

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
