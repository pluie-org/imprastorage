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
from os         import urandom, popen, sep, makedirs
from os.path    import dirname, realpath, abspath, join
from time       import time
from re         import split as regsplit
from base64     import urlsafe_b64encode
from inspect    import stack
from subprocess import PIPE, Popen
from sys        import stderr, executable as pyexec

DEBUG_ALL    = 0
DEBUG_WARN   = 1
DEBUG_NOTICE = 2
DEBUG_INFO   = 3

DEBUG       = True
DEBUG_LEVEL = DEBUG_INFO
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
    
def linefeed_escape(data):
    """Escape simple quote
    :Returns: `str`
    """
    return data.replace('\n', '\\n')
    
def get_file_content(fileName):
    """Get file content of `fileName`
    :Returns: `str`
    """
    r = open(fileName, "rt")
    data = r.read()
    r.close()
    return data
    
def get_file_binary(fileName):
    """Get file content of `fileName`
    :Returns: `str`
    """
    r = open(fileName, "rb")
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

def mkdir_p(path):
    """"""
    try:
        makedirs(path)
    except OSError as e: # Python >2.5
        if e.errno == errno.EEXIST:
            pass
        else: raise

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
    global DEBUG_LEVEL, DEBUG, DEBUG_WARN
    #~ print(inspect.stack()[1][3])
    #~ print(print(args))
    #~ print('-----')
    #~ print(inspect.stack())
    #~ print('---------------')
    val = "self.__class__.__name__+'.%s' % stack()[1][3]+'("+quote_escape(args)+") "
    if DEBUG and DEBUG_LEVEL<=DEBUG_WARN : val += "l:'+str(stack()[1][2])"
    else: val += "'"
    return val


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class RuTime ~~

class RuTime:
    """Give basics time stats"""

    def __init__(self,label,lvl=DEBUG_NOTICE):
        """Initialize duration with appropriate label"""
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_INFO
        self.debug      = DEBUG and DEBUG_LEVEL <= lvl
        self.debugStart = self.debug and lvl < DEBUG_INFO
        self.lvl        = lvl
        self.label      = label
        self._start()
    
    def _start(self):

        if self.debug :print(' ==> '+self.label)
        self.sc = time()
    
    def stop(self):
        """Stop duration and print basics stats duration on console"""
        self.ec = time()
        if self.debug: self._stats()
    
    def _stats(self):
        print(' <== '+self.label+(' [%.9f s]' % (self.ec - self.sc)))


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
# ~~ class StrIterator ~~

class StrIterator:

    MAX_ITER = 1000
    
    def __init__(self,data):
        self.l  = len(data)
        self.p  = ceil(self.l/self.MAX_ITER)
        self.d  = []
        for x in range(self.p):
            self.d.append(data[x*self.MAX_ITER:x*self.MAX_ITER+self.MAX_ITER])

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i > len(self.d)-1 :
            raise StopIteration 
        self.i += 1
        return self.d[self.i-1]
