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

from base64               import urlsafe_b64encode
from binascii             import b2a_base64, a2b_base64
from email.encoders       import encode_base64
from email.header         import Header
from email.mime.base      import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.utils          import formatdate
from math                 import ceil, floor
from mmap                 import mmap
from os                   import remove, urandom, sep
from os.path              import abspath, dirname, join, realpath, basename, getsize, splitext
from re                   import split as regsplit
from impra.imap           import ImapHelper, ImapConfig
from impra.util           import __CALLER__, Rsa, RuTime, Noiser, Randomiz, RuTime, hash_sha256, formatBytes, randomFrom, bstr, quote_escape, stack, run, file_exists, get_file_content, get_file_binary

DEBUG = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ConfigKey ~~

class ConfigKey:
    """"""
    
    def __init__(self, key=None, psize=19710000):
        """"""
        if key : self.key = bytes(key,'utf-8')
        else : self.key = self._build()
        self.psize  = psize
        self.salt   = str(self.key[::-4])
        self.noiser = Noiser(self.key)
        self.rdmz   = Randomiz(1)

    def getHashList(self,name,count,noSorted=False):
        """"""
        rt = RuTime(eval(__CALLER__('"%s",%s,%i' % (name,count,noSorted))))
        self.rdmz.new(count)
        dic, lst, hroot = {}, [], hash_sha256(self.salt+name)
        for i in range(count) :  
            self.noiser.build(i)
            d     = str(i).rjust(2,'0')
            # part n°, hash, lns, lne, pos
            hpart = hash_sha256(self.salt+name+'.part'+d)[:-3]+str(ord(hroot[i])).rjust(3,'0')
            lst.append((d, hpart, self.noiser.lns, self.noiser.lne, self.rdmz.get()))
        dic['head'] = [name,count,hroot,self.getKey()]
        if not noSorted :
            lst = sorted(lst, key=lambda lst: lst[4])
        dic['data'] = lst
        rt.stop()
        return dic
    
    def _build(self,l=48):
        """"""
        return urlsafe_b64encode(urandom(l))
    
    def getKey(self):
        """"""
        return str(self.key,'utf-8')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class FSplitter ~~

class FSplitter :
    """"""
    
    def __init__(self, ck, wkdir='./'):
        """"""
        self.ck         = ck
        self.wkdir      = wkdir
        self.DIR_CACHE  = self.wkdir+sep+'cache'+sep
        self.DIR_INBOX  = self.wkdir+sep+'inbox'+sep
        self.DIR_OUTBOX = self.wkdir+sep+'outbox'+sep
        self.DIR_DEPLOY = self.wkdir+sep+'deploy'+sep
    
    def addFile(self, fromPath, label, fixCount = False):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        fsize = getsize(fromPath)
        count = ceil(fsize/self.ck.psize)
        minp, maxp = 52, 62
        if   fsize < 4800000   : minp, maxp =  8, 12
        elif fsize < 22200000  : minp, maxp = 12, 22
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
            o.write(self.ck.noiser.getNoise(phlst[2])+mmap.read(size)+self.ck.noiser.getNoise(phlst[3]))
        rt.stop()
        
    def deployFile(self, hlst, ext='', fake=False):
        """"""
        rt = RuTime(eval(__CALLER__()))
        p = 0
        hlst['data'] = sorted(hlst['data'], key=lambda lst: lst[0])
        fp = open(self.DIR_DEPLOY+hlst['head'][0]+ext, 'wb+')
        depDir = self.DIR_INBOX
        if fake : depDir = self.DIR_OUTBOX
        while p < hlst['head'][1] :
            self._mergePart(fp,p,hlst['data'][p],depDir)
            p += 1
        fp.close()
        rt.stop()

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
            rsa = Rsa()
            self.set('host','host','imap')
            self.set('port','993','imap')
            self.set('user','login','imap')
            self.set('pass','password','imap')
            self.set('box' ,'__IMPRA','imap')
            self.set('pubKey',rsa.pubKey,'keys')
            self.set('prvKey',rsa.prvKey,'keys')
            self.set('salt'  ,'-¤-ImpraStorage-¤-','keys')
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraIndex ~~

class ImpraIndex:
    """A representation of the index stored on the server"""
    
    SEP_ITEM       = ';'
    """Separator used for entry"""
    
    SEP_TOKEN      = '#'
    """Separator used for token"""
    
    SEP_CATEGORY   = '¤'
    """Separator used for category section"""
    
    QUOTE_REPL     = '§'
    """Char replacement of simple quote String"""
    
    SEP_KEY_INTERN = '@'
    """Separator used for internal key such categories"""
    
    
    def __init__(self, rsa, encdata='', dicCategory={}, id=0):
        """Initialize the index with rsa and encoded data

        :Parameters:
            `rsa` : impra.Rsa
                Rsa instance initialized with appropriate private and public
                keys to decrypt/encrypt data
            `encdata` : str
                initial content of the index encrypted with rsa
        """
        self.ck   = ConfigKey('b-gs_bv1qyb_UFUwPWhm8xM3KJU1k2UBNfjgRBQhvkY2KYI_BF0RBTiqoqDaJlaP')
        self.fspl = FSplitter(self.ck,join(rsa.dpath,'wk')+sep)
        self.rsa  = rsa
        self.dic  = {}
        self.id   = id
        if encdata =='' : data = encdata
        else : data = self.rsa.decrypt(encdata)
        data = data.replace(self.QUOTE_REPL, '\'')
        ld   = regsplit('\n?\r? ?'+self.SEP_CATEGORY+' ?\n\r??',data)
        l    = regsplit(self.SEP_ITEM,ld[0])
        for row in l:
            d = regsplit(self.SEP_TOKEN,row)
            del d[7:]
            #  key : count, hash, ext, usr, cat
            if len(d)>5 and d!='': 
                self.dic[d[1]] = d
        if len(ld)>1:
            l = regsplit(self.SEP_ITEM,ld[1].lstrip('\n\r'))
            for row in l:
                d = regsplit(' ?= ?',row,1)
                if len(d)> 1 and len(d[0]) > 3 :
                    self.dic[d[0].lstrip('\n\r')] = d[1]
        else: 
            for k in dicCategory : 
                self.dic[self.SEP_KEY_INTERN+k] = dicCategory[k]

    def add(self,key, label, count, ext='', usr='', cat=''):
        """Add an entry to the index with appropriate label, key used by entry
        to decode data, and parts count
        """
        if self.search(label) == None : 
            self.dic[label] = (key,label,count,ext,usr,cat, self.id)
            self.id +=1
        else : 
            print(label+' already exist')

    def rem(self,label):
        """Remove the selected label from the index"""
        self.dic.pop(label, None)

    def search(self,label):
        """Search the corresponding label in the index"""
        return self.dic.get(label)
        
    def searchById(self,sid):
        """Search the corresponding label in the index"""
        rt = RuTime(eval(__CALLER__()))
        l  = None
        r = [v for i, v in enumerate(self.dic) if self.dic[v][6] == str(sid)]
        if len(r)>0: l = r[0]
        rt.stop()
        return l

    def toString(self, withoutCatg=False, idFirst=False):
        """Make a string representation of the index as it was store on the server"""
        data   = cdata = ''
        for k in sorted(self.dic):           
            v = self.dic.get(k)
            k = k.lstrip('\n\r')
            if k[0]==self.SEP_KEY_INTERN and len(k)>1:
                cdata += k+'='+v+self.SEP_ITEM
            else :        
                if not idFirst :
                    for i in v: 
                        data += str(i)+self.SEP_TOKEN
                else :
                    data += str(v[6]).rjust(1+ceil(len(str(v[6]))/10),' ')+' '
                    for i in v[:-1]: 
                        data += str(i)+self.SEP_TOKEN
            data = data.rstrip(self.SEP_TOKEN)+self.SEP_ITEM
        if not withoutCatg :
            data += self.SEP_CATEGORY+'\n'+cdata
        return data;

    def encrypt(self):
        """"""
        return self.rsa.encrypt(self.toString().replace('\'', self.QUOTE_REPL))

    def impracrypt(self):
        """"""
        data = self.toString().replace('\'', self.QUOTE_REPL)
        
        with open(self.rsa.dpath+'.tmpdecd2', mode='w', encoding='utf-8') as o:
            o.write(data)
            
        hlst = self.fspl.addFile(self.rsa.dpath+'.tmpdecd2','.index',12)
        print(hlst['head'])
        hlst['data'] = sorted(hlst['data'], reverse=True, key=lambda lst: lst[4])        
        data = b''
        encA = []
        for row in hlst['data']:
            data += get_file_binary(self.fspl.DIR_OUTBOX+row[1]+'.ipr')
            encA.append(get_file_binary(self.fspl.DIR_OUTBOX+row[1]+'.ipr'))
            print(row)
        encData = b2a_base64(data)
        with open(self.rsa.dpath+'.tmpencd2', mode='wb') as o:
            o.write(encData)
        print('-- enc DATA --')
        #print(encData)
        decData = a2b_base64(encData)
        print(type(decData))
        print(len(decData))
        #print(str(decData))
        encB = hlst['head'][1]*[None]
        stpos = 0
        tsize = 0
        print('total size : '+str(len(decData)))
        for row in hlst['data']:
            thesize = row[2]+hlst['head'][4]+row[3]
            print(str(row[4])+' - '+row[1]+' ('+str(thesize)+')')
            print('spos = '+str(stpos))                
            print(stpos)
            epos = stpos+row[2]+hlst['head'][4]+row[3]                
            print('epos = '+str(epos)+'('+str(row[2])+','+str(hlst['head'][4])+','+str(row[3])+') ['+str(thesize)+']')
            print(epos)
            dd = decData[stpos:epos]
            stpos = epos+1
            print('----------')
            print(dd)
            print('-----------------------------------')
            tsize += thesize
            with open(self.fspl.DIR_OUTBOX+row[1]+'.ipr2', mode='wb') as o:
                o.write(dd)
        print('total size : '+str(tsize))
        print('-- decoding DATA2 --')
        for row in hlst['data']:
            print(row)
        hlst['data'] = sorted(hlst['data'], reverse=False, key=lambda lst: lst[4])        
        self.fspl.deployFile(hlst, '.dec', True)
        
    def print(self,withoutCatg=False, header=''):
        """Print index content as formated bloc"""
        data = self.toString(withoutCatg,True).split(';')
        print(header)
        for row in data: 
            if row.rstrip('\n') != '': print(row)
            


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class ImpraStorage:
    """"""
    
    def __init__(self, rsa, conf, remIndex=False, wkdir=None):
        """"""
        if wkdir == None : wkdir = abspath(join(dirname( __file__ ), '..', 'wk'))
        self.wkdir   = wkdir
        self.conf    = conf
        self.pathInd = dirname(self.conf.ini.path)+sep+'.index'
        self.rootBox = self.conf.get('box','imap')
        iconf        = ImapConfig(self.conf.get('host','imap'), self.conf.get('port','imap'), self.conf.get('user', 'imap'), self.conf.get('pass', 'imap'))
        self.ih      = ImapHelper(iconf,self.rootBox)
        self.mb      = MailBuilder(self.conf.get('salt','keys'))
        self.rsa     = rsa
        self.fsplit  = FSplitter(ConfigKey(),self.wkdir)
        self.delids  = []
        if remIndex  : self.removeIndex()
        self.index   = self.getIndex()

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

    def getIndex(self):
        """"""
        rt = RuTime(eval(__CALLER__()))
        index   = None
        encData = ''
        uid     = self.conf.get('uid' ,'index')
        date    = self.conf.get('date','index')
        nid     = self.conf.get('nid' ,'index')
        if nid==None : nid = 0
        if uid !=None : print(uid+' - '+date+' - ['+(str(nid))+']')
        self._getIdIndex()
        if self.idx :
            # getFromFile
            if int(self.idx) == int(uid) and file_exists(self.pathInd):
                encData = get_file_content(self.pathInd)
                print('cache')
            else:
                encData = self._getCryptIndex()
                with open(self.pathInd, mode='w', encoding='utf-8') as o:
                    o.write(encData)
        index = ImpraIndex(self.rsa, encData, {'catg':self.conf.get('types','catg')}, int(nid))            
        rt.stop()
        return index
        
    def removeIndex(self):
        """"""
        self._getIdIndex()
        if self.idx :
            self.ih.delete(self.idx, True)
        self.ih.deleteBin()

    def saveIndex(self):
        """"""
        global DEBUG
        rt = RuTime(eval(__CALLER__()))
        if self.idx != None :
            self.ih.delete(self.idx, True)
        for i in self.delids : self.ih.delete(i, True)
        encData  = self.index.encrypt() 
        msgIndex = self.mb.buildIndex(encData)        
        if DEBUG: print(msgIndex.as_string())
        ids = self.ih.send(msgIndex.as_string(), self.rootBox)
        date = self.ih.headerField('date', ids[1], True)
        self.conf.set('uid',ids[1],'index')
        self.conf.set('date',date,'index')
        with open(self.pathInd, mode='w', encoding='utf-8') as o:
            o.write(encData)        
        self.ih.deleteBin()
        #self.index = self.getIndex()
        rt.stop()

    def addFile(self, path, label, usr='all', catg=''):
        """"""
        global DEBUG
        rt = RuTime(eval(__CALLER__('"%s","%s","%s"' % (path[:13]+'...',label,usr))))
        
        #~ hlst = self.fsplit.addFile(path,label)
        #~ self.fsplit.deployFile(hlst,True)
        _, ext = splitext(path)
        try:
            if self.index.search(label)==None :
                hlst = self.fsplit.addFile(path,label)
                if DEBUG : 
                    print(hlst['head'])
                    for v in hlst['data']:
                        print(v)
                nameFrom = self.conf.ini.get('name',self.conf.profile+'.infos')
                for row in hlst['data'] :
                    msg  = self.mb.build(nameFrom,usr,hlst['head'][2],self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                    self.ih.send(msg.as_string(), self.rootBox)
                    remove(self.fsplit.DIR_OUTBOX+row[1]+'.ipr')
                self.index.add(hlst['head'][3],hlst['head'][0],hlst['head'][1],ext,self.mb.getHashName(usr),catg)
                self.saveIndex()
                self.conf.set('nid', str(self.index.id),'index')
            else :
                raise Exception(label + ' already exist on server')
        except Exception as e :
            print(e)
        rt.stop()

    def getFile(self,label):
        """"""
        global DEBUG
        rt  = RuTime(eval(__CALLER__('"%s"' % label)))
        if label==None : 
            print(str(label)+' unexist')
        else :
            key = self.index.search(label)
            if label!=None and key!=None:
                ck    = ConfigKey(key[0])
                count = int(key[2])
                hlst  = ck.getHashList(label,count,True)
                ids   = self._getIdsBySubject(hlst['head'][2])
                if len(ids) >= count:
                    status, resp = self.ih.srv.fetch(ids[0],'(BODY[HEADER.FIELDS (TO)])')
                    to = bstr(resp[0][1][4:-4])
                    if to == self.mb.getHashName('all')+'@'+self.mb.DOMAIN_NAME or to == self.mb.getHashName(self.conf.ini.get('name',self.conf.profile+'.infos'))+'@'+self.mb.DOMAIN_NAME :
                        for mid in ids :
                            self.ih.downloadAttachment(mid,self.fsplit.DIR_INBOX)
                        if DEBUG :
                            print(hlst['head'])
                            for v in hlst['data']:
                                print(v)
                        self.fsplit.deployFile(hlst, key[3])
                    else :
                        #raise Exception(label+' is private')
                        print(label+' is private')
                else :
                    #raise Exception(label+' : invalid count parts '+str(len(ids))+'/'+str(count))
                    print(label+' : invalid count parts '+str(len(ids))+'/'+str(count))
            else:
                #raise Exception(str(label)+' not on the server')
                print(str(label)+' not on the server')
        rt.stop()

    def clean(self):
        """"""
        rt = RuTime(eval(__CALLER__()))
        self.index = self.getIndex()
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
