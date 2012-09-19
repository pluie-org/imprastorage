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

from base64     import urlsafe_b64encode
from inspect    import stack
from errno      import EEXIST
from hashlib    import sha256
from math       import log, floor, ceil
from os         import urandom, popen, sep, makedirs, system
from os.path    import dirname, realpath, abspath, join
from random     import choice
from re         import split as regsplit
from subprocess import PIPE, Popen
from sys        import stderr, executable as pyexec
import platform
#~ from sys.stdout import isatty
from time       import time

DEBUG_ALL    = 0
DEBUG_WARN   = 1
DEBUG_NOTICE = 2
DEBUG_INFO   = 3

DEBUG       = True
DEBUG_LEVEL = DEBUG_INFO

COLOR_MODE  = True

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
    r = open(fileName, 'rt')
    data = r.read()
    r.close()
    return data
    
def get_file_binary(fileName):
    """Get file content of `fileName`
    :Returns: `str`
    """
    r = open(fileName, 'rb')
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

def is_binary(filename):
    """Check if given filename is binary."""
    done = False
    fp = open(filename, 'rb')
    try:
        CHUNKSIZE = 1024
        while 1:
            chunk = fp.read(CHUNKSIZE)
            if b'\0' in chunk:  done = True # found null byte
            if done or len(chunk) < CHUNKSIZE: break
    finally:
        fp.close()
    return done

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
        if e.errno == EEXIST:
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
    val = "self.__class__.__name__+'.%s' % stack()[1][3]+'("+quote_escape(args)+") "
    if DEBUG and DEBUG_LEVEL<=DEBUG_WARN : val += "l:'+str(stack()[1][2])"
    else: val += "'"
    return val

if platform.system() == 'Windows' :
    clear  = lambda: system('cls')
else : clear = lambda: system('clear')


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
        global C
        if self.debug :print(C.BRED+' ==> '+C.BYELLOW+self._paramize(self.label)+C.OFF)
        self.sc = time()
    
    def stop(self):
        """Stop duration and print basics stats duration on console"""
        self.ec = time()
        if self.debug: self._stats()

    def _paramize(self,data):
        global C
        s = data.replace('(','('+C.GREEN)
        s = s.replace(')',C.BYELLOW+')'+C.OFF)
        return s
    
    def _stats(self):
        global C
        print(C.BRED+' <== '+C.BYELLOW+self._paramize(self.label)+(' %s%.5f s%s' % (C.WHITE,self.ec-self.sc,C.OFF)))


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

class Coloriz:

    # Reset
    OFF     ='\033[1;m'

    # Regular Colors
    BLACK         ='\033[0;30m'
    RED           ='\033[0;31m'
    GREEN         ='\033[0;32m'
    YELLOW        ='\033[0;33m'
    BLUE          ='\033[0;34m'
    PURPLE        ='\033[0;35m'
    CYAN          ='\033[0;36m'
    WHITE         ='\033[0;37m'

    # Bold
    BBLACK        ='\033[1;30m'
    BRED          ='\033[1;31m'
    BGREEN        ='\033[1;32m'
    BYELLOW       ='\033[1;33m'
    BBLUE         ='\033[1;34m'
    BPURPLE       ='\033[1;35m'
    BCYAN         ='\033[1;36m'
    BWHITE        ='\033[1;37m'

    # Underline
    UBLACK       ='\033[4;30m'
    URED         ='\033[4;31m'
    UGREEN       ='\033[4;32m'
    UYELLOW      ='\033[4;33m'
    UBLUE        ='\033[4;34m'
    UPURPLE      ='\033[4;35m'
    UCYAN        ='\033[4;36m'
    UWHITE       ='\033[4;37m'

    # Background
    ON_BLACK     ='\033[40m'  
    ON_RED       ='\033[41m'  
    ON_GREEN     ='\033[42m'  
    ON_YELLOW    ='\033[43m'  
    ON_BLUE      ='\033[44m'  
    ON_PURPLE    ='\033[45m'  
    ON_CYAN      ='\033[46m'  
    ON_WHITE     ='\033[47m'  

    # High Intensity
    IBLACK       ='\033[0;90m'
    IRED         ='\033[0;91m'
    IGREEN       ='\033[0;92m'
    IYELLOW      ='\033[0;93m'
    IBLUE        ='\033[0;94m'
    IPURPLE      ='\033[0;95m'
    ICYAN        ='\033[0;96m'
    IWHITE       ='\033[0;97m'

    # Bold High Intensity
    BIBLACK      ='\033[1;90m'
    BIRED        ='\033[1;91m'
    BIGREEN      ='\033[1;92m'
    BIYELLOW     ='\033[1;93m'
    BIBLUE       ='\033[1;94m'
    BIPURPLE     ='\033[1;95m'
    BICYAN       ='\033[1;96m'
    BIWHITE      ='\033[1;97m'

    # High Intensity backgrounds
    ON_IBLACK    ='\033[0;100m'
    ON_IRED      ='\033[0;101m'
    ON_IGREEN    ='\033[0;102m'
    ON_IYELLOW   ='\033[0;103m'
    ON_IBLUE     ='\033[0;104m'
    ON_IPURPLE   ='\033[10;95m'
    ON_ICYAN     ='\033[0;106m'
    ON_IWHITE    ='\033[0;107m'
    
    def __init__(self):
        """"""
        global COLOR_MODE
        if not COLOR_MODE :
            self.OFF = self.BLACK = self.RED = self.GREEN = self.YELLOW = self.BLUE = self.PURPLE = self.CYAN = self.WHITE = self.BBLACK = self.BRED = self.BGREEN = self.BYELLOW = self.BBLUE = self.BPURPLE = self.BCYAN = self.BWHITE = self.UBLACK = self.URED = self.UGREEN = self.UYELLOW = self.UBLUE = self.UPURPLE = self.UCYAN = self.UWHITE = self.ON_BLACK = self.ON_RED = self.ON_GREEN = self.ON_YELLOW = self.ON_BLUE = self.ON_PURPLE = self.ON_CYAN = self.ON_WHITE = self.IBLACK = self.IRED = self.IGREEN = self.IYELLOW = self.IBLUE = self.IPURPLE = self.ICYAN = self.IWHITE = self.BIBLACK = self.BIRED = self.BIGREEN = self.BIYELLOW = self.BIBLUE = self.BIPURPLE = self.BICYAN = self.BIWHITE = self.ON_IBLACK = self.ON_IRED = self.ON_IGREEN = self.ON_IYELLOW = self.ON_IBLUE = self.ON_IPURPLE = self.ON_ICYAN = self.ON_IWHITE = ''

C = Coloriz()
