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
# ~~ package util ~~

from hashlib    import sha256
from math       import log, floor, ceil
from random     import choice
from os         import urandom, popen, sep
from os.path    import dirname, realpath, abspath
from time       import time
from re         import split as regsplit
from base64     import urlsafe_b64encode
from inspect    import stack
from subprocess import PIPE, Popen
from sys        import stderr


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ methods ~~

def represents_int(s):
    """"""
    try: 
        int(s)
        return True
    except ValueError:
        return False

def quote_escape(data):
    """Escape simple quote
    :Returns: `str`
    """
    return data.replace('\'', r'\'')
    
def get_file_content(fileName):
    """Get file content of `fileName`
    :Returns: `str`
    """
    r = open(fileName, "rt")
    data = r.read()
    r.close()
    return data

def hash_sha256(data):
    """Get a sha256 hash of str `data`
    :Returns: `str`
    """
    return str(sha256(bytes(data,'utf-8')).hexdigest())

def randomFrom(val, sval=0):
    """Get a random number from range `sval=0` to `val`
    :Returns: `int`
    """
    lst = list(range(sval,val))
    return choice(lst)

def get_file_path(val):
    """"""
    return abspath(dirname(val))+sep

def file_exists(path):
    """"""
    try:
        with open(path) as f: 
            exist = True
    except IOError as e:
            exist = False
    return exist
   
def formatBytes(b, p=2):
    """Give a human representation of bytes size `b`
    :Returns: `str`
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']; 
    b = max(b,0);
    if b == 0 : lb= 0
    else : lb    = log(b) 
    p = floor(lb/log(1024))
    p = min(p, len(units)- 1) 
    #Uncomment one of the following alternatives
    b /= pow(1024,p)
    #b /= (1 << (10 * p)) 
    return str(round(b, p))+' '+units[p] 

def bstr(b,enc='utf-8'):
    """"""
    return str(b, encoding=enc)

def run(cmdline):
    """"""
    try:
        p = Popen(cmdline, shell=True,stdout=PIPE, stderr=PIPE)
        cmdout, cmderr =  p.communicate()
        rcode = p.wait()
        if rcode < 0:
            print((stderr,"Child was terminated by signal",rcode))
        else:
            return (rcode,cmdout,cmderr)
    except OSError as e :
        return (e,cmdout,cmderr)

def __CALLER__(args=''):
    """Give basic information of caller method
    usage ::

        eval(__CALLER())
        eval(__CALLER('"%s","%s"' % (arg1,arg2)))
        
    :Returns: `str`
    """    
    #~ print(inspect.stack()[1][3])
    #~ print(print(args))
    #~ print('-----')
    #~ print(inspect.stack())
    #~ print('---------------')
    val = "self.__class__.__name__+'.%s' % stack()[1][3]+'("+quote_escape(args)+") l:'+str(stack()[1][2])"
    return val


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Noiser ~~

class Noiser:
    """"""
    
    KEY_LEN = 64
    """"""

    def __init__(self, key, part=0):
        """"""
        if len(key)!=self.KEY_LEN : 
            raise Exception('Invalid Pass length')
        else :
            self.key  = key
            self.build(part)

    def build(self, part):
        """"""
        if not part < self.KEY_LEN-1 : raise Exception('part exceed limit')
        else :
            self.part, v = part, 0
            for i in self.key[::-2] : v += i
            v  = int(ceil(v/4.22))
            self.lns = int(ceil(v/2))-self.key[self.part]
            self.lne = int(v-self.lns-self.key[self.part+2])

    def getNoise(self, l):
        """"""
        return urandom(l)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Randomiz ~~

class Randomiz:
    """"""
    
    def __init__(self,count):
        """"""
        self.lst = list(range(0,count))
        self.count = len(self.lst)
    
    def new(self,count=None):
        """"""
        if count : self.count = count
        self.__init__(self.count)
    
    def get(self):
        """"""
        pos = choice(self.lst)
        del self.lst[self.lst.index(pos)]
        return pos


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class RuTime ~~

class RuTime:
    """Give basics time stats"""

    def __init__(self,label):
        """Initialize duration with appropriate label"""
        self.label = label        
        self._start()
    
    def _start(self):
        from impra.core import DEBUG
        if DEBUG :print(' ==> '+self.label)
        self.sc = time()
    
    def stop(self):
        """Stop duration and print basics stats duration on console"""
        from impra.core import DEBUG
        self.ec = time()
        if DEBUG:self._stats()
    
    def _stats(self):
        print(' <== '+self.label+(' [%.9f s]' % (self.ec - self.sc))+' <¤¤ ')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class IniFile ~~

class IniFile:
    """Read a write inifile"""
    
    def __init__(self,path):
        """"""
        self.path = path
        self.dic  = {}
        self.read()

    def isEmpty(self):
        """"""
        return len(self.dic)==0

    def has(self, key, section='main'):
        """"""
        d = self.hasSection(section) and (key in self.dic[section])
        return d
        
    def hasSection(self, section):
        """"""
        d = (section in self.dic)
        return d

    def get(self, key, section='main'):
        """"""
        return self.dic[section][key]

    def set(self, key, val, section='main'):
        """"""
        v = None
        if not section in self.dic:
            self.dic[section]  = {}
        if key in self.dic[section]:
            v = self.dic[section].pop(key)
        self.dic[section][key] = val
        return v
    
    def rem(self, key, section):
        """"""
        v = None        
        if section in self.dic :
            if key == '*' : 
                v = self.dic.pop(section)
            elif key in self.dic[section]: 
                v = self.dic[section].pop(key)
        return v
    
    def write(self,path=None):
        """"""
        if path == None : path = self.path
        content = self.toString()
        with open(path, mode='w', encoding='utf-8') as o:
            o.write(content)

    def toString(self,section='*'):
        """"""
        content = ''
        main    = ''
        for s in self.dic:
            if section=='*' or section+'.'==s[:len(section)+1]:
                if s!='main':
                    #~ if section=='*': content += '\n['+s+']\n'
                    #~ else : content += '\n['+s[len(section)+1:]+']\n'
                    content += '\n['+s+']\n'
                for k in sorted(self.dic[s]):
                    k = k.rstrip(' ')
                    if s!='main' :
                        content += k+' = '+self.dic[s][k]+'\n'
                    else : main += k+' = '+self.dic[s][k]+'\n'
        return main + content
    
    def read(self):
        """"""
        try:
            with open(self.path, encoding='utf-8') as o:
                csection = 'main'
                self.dic[csection] = {}  
                for l in o:
                    l = l.rstrip()
                    d = regsplit(' *= *',l,1)
                    if len(d)> 1:
                        self.dic[csection][d[0]] = d[1]
                    elif len(l)>0 and l[0]=='[':
                        csection = l.strip('[]')
                        self.dic[csection] = {}
        except IOError : pass




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class BadKeysException(BaseException):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Rsa ~~

class Rsa:
    """"""
    
    def __init__(self, prvKey=None, pubKey=None, dpath='./', forceKeyGen=False):
        """"""
        self.cpath  = dirname(realpath(__file__))+'/../desurveil/scripts/'
        self.prvKey = prvKey
        self.pubKey = pubKey
        self.dpath  = dpath
        if prvKey == None or pubKey==None : self.key(forceKeyGen)

    def key(self,force=False):
        """"""
        cmd = self.cpath+"desurveil key -a "+self.dpath+".impra_id_rsa -l "+self.dpath+".impra_id_rsa.pub"
        #print(cmd)
        
        try :
            with open(self.dpath+'.impra_id_rsa','rt') as f: pass
            if force:d = popen(cmd).read()
        except IOError as e:
            d = popen(cmd).read()
            #print(d)
        self.prvKey = get_file_content(self.dpath+'.impra_id_rsa')
        self.pubKey = get_file_content(self.dpath+'.impra_id_rsa.pub')
        #~ print('pubKey : \n'+self.pubKey)
        #~ print('prvKey : \n'+self.prvKey)
    
    def encrypt(self,data):
        """"""
        key = ''
        if self.pubKey != None : key = " -CI '"+self.pubKey+"'"
        #if self.pubKey != None : key = " -C '"+self.dpath+".impra_id_rsa.pub'"
        cmd = self.cpath+"desurveil encrypt -i '"+data+"'"+key
        #print(cmd)
        return popen(cmd).read()

    def decrypt(self,data):
        """"""
        key = ''
        if self.prvKey != None : key = " -CI '"+self.prvKey+"'"
        #if self.prvKey != None : key = " -C '"+self.dpath+".impra_id_rsa'"
        cmd = self.cpath+"desurveil decrypt -i '"+data+"'"+key
        
        rs = run(cmd)
        if rs[0]==1:
            raise BadKeysException('bad key to decrypt')
        else :
            encData = str(rs[1],'utf-8')
        return encData
