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

import inspect
from base64               import urlsafe_b64encode
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
from impra.util           import __CALLER__, Rsa, RuTime, Noiser, Randomiz, RuTime, hash_sha256, formatBytes, randomFrom, bstr, quote_escape, stack


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
        rt = RuTime('getHashList')
        rt = RuTime(eval(__CALLER__('"%s",%s,%i' % (name,count,noSorted))))
        self.rdmz.new(count)
        dic, lst, hroot = {}, [], hash_sha256(self.salt+name)
        for i in range(count) :  
            self.noiser.build(i)
            d     = str(i).rjust(2,'0')
            # part n°, hash, lns, lne, pos
            hpart = hash_sha256(self.salt+name+'.part'+d)[:-3]+str(ord(hroot[i])).rjust(3,'0')
            lst.append((d, hpart, self.noiser.lns, self.noiser.lne, self.rdmz.get()))
        dic['head'] = (name,count,hroot,self.getKey())
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
    
    def addFile(self, fromPath, label):
        """"""
        rt    = RuTime(eval(__CALLER__()))
        fsize = getsize(fromPath)
        count = ceil(fsize/self.ck.psize)
        minp, maxp = 52, 62
        if   fsize < 4800000   : minp, maxp =  8, 12
        elif fsize < 22200000  : minp, maxp = 12, 22
        elif fsize < 48000000  : minp, maxp = 22, 32
        elif fsize < 222000000 : minp, maxp = 32, 42
        if count < minp : count = randomFrom(maxp,minp)
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
            self.set('host','imap.gmail.com','imap')
            self.set('port','993','imap')
            self.set('user','login','imap')
            self.set('pass','**********','imap')
            self.set('box' ,'__SMILF','imap')
            self.set('pubKey',rsa.pubKey,'keys')
            self.set('prvKey',rsa.prvKey,'keys')
            self.set('salt'  ,'-¤-ImpraStorage-¤-','keys')
        if not self.ini.hasSection(self.profile+self.SEP_SECTION+'catg'):
            save = True
            self.set('users', self.get('name','infos'),'catg')
            self.set('types', 'music,films,doc,images,archives,games','catg')        
        if save : 
            self.ini.write()
            print(self.ini.toString())
    
    def get(self, key, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        return self.ini.get(key, profile+self.SEP_SECTION+section)
    
    def set(self, key, value, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        return self.ini.set(key, value, profile+self.SEP_SECTION+section)


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
    
    QUOTE_REPL     = '-§'
    """Char replacement of simple quote String"""
    
    SEP_KEY_INTERN = '@'
    """Separator used for internal key such categories"""
    
    
    def __init__(self, rsa, encdata='', dicCategory={}):
        """Initialize the index with rsa and encoded data

        :Parameters:
            `rsa` : impra.Rsa
                Rsa instance initialized with appropriate private and public
                keys to decrypt/encrypt data
            `encdata` : str
                initial content of the index encrypted with rsa
        """
        self.rsa  = rsa
        self.dic  = {}
        if encdata =='' : data = encdata
        else : data = self.rsa.decrypt(encdata)
        data = data.replace(self.QUOTE_REPL, '\'')
        ld   = regsplit('\n? ?'+self.SEP_CATEGORY+' ?\n?',data)
        l    = regsplit(self.SEP_ITEM,ld[0])        
        for row in l:
            d = regsplit(self.SEP_TOKEN,row)
            #  key : count, hash, ext, usr, cat
            if len(d)>4 and d!='': self.dic[d[1]] = d
        if len(ld)>1:
            l = regsplit(self.SEP_ITEM,ld[1].lstrip('\n'))
            for row in l:
                d = regsplit(' ?= ?',row,1)
                if len(d)> 1 and len(d[0]) > 3 :
                    self.dic[d[0]] = d[1]
        else: 
            for k in dicCategory : 
                self.dic[self.SEP_KEY_INTERN+k] = dicCategory[k]

    def add(self,key, label, count, ext='', usr='', cat=''):
        """Add an entry to the index with appropriate label, key used by entry
        to decode data, and parts count
        """
        if self.search(label) == None : 
            self.dic[label] = (key,label,count,ext,usr,cat)
        else : 
            print(label+' already exist')

    def rem(self,label):
        """Remove the selected label from the index"""
        self.dic.pop(label, None)

    def search(self,label):
        """Search the corresponding label in the index"""
        return self.dic.get(label)

    def toString(self):
        """Make a string representation of the index as it was store on the server"""
        data   = cdata = ''
        for k in sorted(self.dic):           
            v = self.dic.get(k)
            if k[0]==self.SEP_KEY_INTERN and len(k)>1:
                cdata += k+'='+v+self.SEP_ITEM
            else :
                for i in v: data += str(i)+self.SEP_TOKEN
            data = data.rstrip(self.SEP_TOKEN)+self.SEP_ITEM
        return data+self.SEP_CATEGORY+'\n'+cdata;
    
    def encrypt(self):
        """"""        
        return self.rsa.encrypt(self.toString().replace('\'', self.QUOTE_REPL))

    def print(self):
        """Print index content as formated bloc"""
        data = self.toString().split(';')
        for row in data:
            if row.rstrip('\n') != '': print(row)
            

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class ImpraStorage:
    """"""
    
    def __init__(self, rsa, conf, wkdir=None):
        """"""
        if wkdir == None : wkdir = abspath(join(dirname( __file__ ), '..', 'wk'))
        self.wkdir   = wkdir
        self.conf    = conf
        self.rootBox = self.conf.get('box','imap')
        iconf        = ImapConfig(self.conf.get('host','imap'), self.conf.get('port','imap'), self.conf.get('user', 'imap'), self.conf.get('pass', 'imap'))
        self.ih      = ImapHelper(iconf,self.rootBox)
        self.mb      = MailBuilder(self.conf.get('salt','keys'))
        self.rsa     = rsa
        self.fsplit  = FSplitter(ConfigKey(),self.wkdir)
        self.delids  = []
        self.index   = self.getIndex()

    def _getIdIndex(self):
        """"""
        mid = None
        status, resp = self.ih.srv.search(None, '(SUBJECT "%s")' % self.mb.getHashName('index'))
        ids = [m for m in resp[0].split()]
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

    def getIndex(self):
        """"""
        self._getIdIndex()
        if self.idx :
            msgIndex = self.ih.email(self.idx)
            for i in self.delids : self.ih.delete(i)
            for part in msgIndex.walk():
                ms  = part.get_payload(decode=True)
            encData = str(ms,'utf-8')
        else :
            encData = ''
        self.ih.deleteBin()
        return ImpraIndex(self.rsa,encData, {'catg':self.conf.get('types','catg')})

    def saveIndex(self):
        """"""
        rt = RuTime(eval(__CALLER__()))
        if self.idx != None :
            self.ih.delete(self.idx)
        encData  = self.index.encrypt() 
        msgIndex = self.mb.buildIndex(encData)        
        print(msgIndex.as_string())
        self.ih.send(msgIndex.as_string(), self.rootBox)
        #self.index = self.getIndex()
        rt.stop()

    def addFile(self, path, label, usr='all', catg=''):
        """"""
        rt = RuTime(eval(__CALLER__('"%s","%s","%s"' % (path[:13]+'...',label,usr))))
        
        #~ hlst = self.fsplit.addFile(path,label)
        #~ self.fsplit.deployFile(hlst,True)
        _, ext = splitext(path)
        try:
            if self.index.search(label)==None :
                hlst = self.fsplit.addFile(path,label)
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
            else :
                raise Exception(label + ' already exist on server')
        except Exception as e :
            print(e)
        rt.stop()

    def getFile(self,label):
        """"""
        rt  = RuTime(eval(__CALLER__('"%s"' % label)))
        key = self.index.search(label)
        if key!=None :
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
                    print(hlst['head'])
                    for v in hlst['data']:
                        print(v)
                    self.fsplit.deployFile(hlst, key[3])
                else :
                    raise Exception(label+' is private')
            else :
                raise Exception(label+' : invalid count parts '+str(len(ids))+'/'+str(count))
        else:
            raise Exception(label+' not on the server')
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