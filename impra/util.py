#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.6                                                             #
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
from os.path    import dirname, realpath, abspath, join, getsize
from random     import choice
from re         import split as regsplit, search as regsearch, finditer as regfinditer
from subprocess import PIPE, Popen
from sys        import stderr, executable as pyexec, stdout
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
    if DEBUG and DEBUG_LEVEL<=DEBUG_WARN : val += "l:'+str(stack()[1][2]) "
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
        global Clz
        if self.debug :
            Clz.print(' ==> ', Clz.fgb1, False)
            self._paramize(self.label)
            Clz.print('', Clz.OFF)
        self.sc = time()
    
    def stop(self):
        """Stop duration and print basics stats duration on console"""
        self.ec = time()
        if self.debug: self._stats()

    def _paramize(self,data):
        global Clz
        sp = [m.start() for m in regfinditer('\(', data)]
        ep = [m.start() for m in regfinditer('\)', data)]
        if len(sp) > 0 :
            Clz.print(data[:sp[0]+1], Clz.fgb3, False)
            Clz.print(data[sp[0]+1:ep[0]], Clz.fgn7, False)
            Clz.print(data[ep[0]:], Clz.fgb3, False)
        else:
            Clz.print(data, Clz.fgb3, False, True)
    
    def _stats(self):
        global Clz
        Clz.print(' <== ', Clz.fgb1, False)
        self._paramize(self.label)
        Clz.print('%.5f' % (self.ec-self.sc), Clz.fgN4)


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

    def getSections(self):
        """"""
        l = {}
        for s in self.dic:
            section = s.split('.')
            if len(section)> 1 and not section[0] in l :
                l[section[0]] = 1
        return [k for i,k in enumerate(l)]

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
    
    def print(self,section='*', withoutSectionName=False):
        """"""
        a = ''
        for s in self.dic:
            if section=='*' or section+'.'==s[:len(section)+1]:
                if s!='main':
                    #~ if section=='*': content += '\n['+s+']\n'
                    #~ else : content += '\n['+s[len(section)+1:]+']\n'
                    print()
                    if not withoutSectionName : 
                        Clz.print('['+s+']', Clz.fgB3)
                    else: Clz.print('['+s.split('.')[1]+']', Clz.fgB3)
                for k in sorted(self.dic[s]):
                    k = k.rstrip(' ')
                    if s!='main' :
                        a = ''
                        if len(self.dic[s][k]) > 50: a = '...'
                        Clz.print(k.ljust(10,' ')+' = '       , Clz.fgn7, False)
                        if Clz.isUnix or k is not 'key' :
                            Clz.print(self.dic[s][k][:50]+a, Clz.fgN2)
                        else: Clz.print('key is masked', Clz.fgb1)
    
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Coloriz ~~

class Coloriz:

    _MARKER        = '!§'
    """"""
    _SEP           = ';'
    """"""
    _PATTERN_COLOR = '^'+_MARKER[0]+'[nfNFbB][0-7]'+_SEP+'$'
    """"""
    _wFH   = 0x0008
    """"""
    _wBH   = 0x0080
    """"""
    _uOFF  = '\033[1;m'
    """"""
    _wOFF  = None
    """"""
    _LF    = '\n'
    """"""
    OFF    = _MARKER+_MARKER[0]+'OFF'+_SEP+_MARKER
    """"""
    isUnix = platform.system() != 'Windows'
    """"""
    
    def __init__(self):
        """Colors for both plateform are : 0: black - 1: red - 2:green - 3: yellow - 4: blue - 5: purple - 6: cyan - 7: white 
        available class members :
        foreground normal (same as bold for w32): 
           self.fgn0 -> self.fgn7
        foreground bold :
           self.fgb0 -> self.fgb7
        foreground high intensity (same as bold high intensity for w35):
           self.fgN0 -> self.fgN7
        foreground bold high intensity :
           self.fgB0 -> self.fgB7
        background
           self.bg0 -> self.bg7
        background high intensity
           self.BG0 -> self.BG7
        default colors :
            self.OFF
        
            usage : 
            pc = PColor()
            pc.print('%smon label%s:%sma value%s' % (pc.BG4+pc.fgN7, pc.OFF+pc.fgn1, pc.fgb4, pc.OFF))
        """
        global COLOR_MODE
        self.active = COLOR_MODE
        if not self.isUnix:
            j = 0
            for i in (0,4,2,6,1,5,3,7):
                exec('self._wf%i = 0x000%i' % (i,j) + '\nself._wb%i = 0x00%i0' % (i,j) + '\nself._wF%i = 0x000%i | self._wFH' % (i,j) + '\nself._wB%i = 0x00%i0 | self._wBH' % (i,j))
                # normal eq bold
                exec('self._wn%i = self._wf%i' % (i,i))
                # normal high intensity eq bold high intensity
                exec('self._wN%i = self._wB%i' % (i,i))
                j += 1
                
        if not self.isUnix :
            import impra.w32color as w32cons
            self._wOFF    = w32cons.get_text_attr()
            self._wOFFbg  = self._wOFF & 0x0070
            self._wOFFfg  = self._wOFF & 0x0007
            self.setColor = w32cons.set_text_attr

        for i in range(0,8):            
            # foreground normal
            exec('self.fgn%i = self._MARKER + self._MARKER[0] + "n%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._un%i = "\\033[0;3%im"' % (i,i))
            # foreground bold
            exec('self.fgb%i = self._MARKER + self._MARKER[0] + "f%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._uf%i = "\\033[1;3%im"' % (i,i))
            # foreground high intensity
            exec('self.fgN%i = self._MARKER + self._MARKER[0] + "N%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._uN%i = "\\033[0;9%im"' % (i,i))
            # foreground bold high intensity
            exec('self.fgB%i = self._MARKER + self._MARKER[0] + "F%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._uF%i = "\\033[1;9%im"' % (i,i))
            # background 
            exec('self.bg%i = self._MARKER + self._MARKER[0] + "b%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._ub%i = "\\033[4%im"' % (i,i))
            # background high intensity
            exec('self.BG%i = self._MARKER + self._MARKER[0] + "B%i" + self._SEP + self._MARKER' % (i,i))
            if True or isUnix : exec('self._uB%i = "\\033[0;10%im"' % (i,i))

    def print(self,data,colors,endLF=True,endClz=True):
        """"""
        if not endLF : ev = ''
        else: ev = self._LF
        if self.active : 
            tokens = [c.lstrip(self._MARKER[0]).rstrip(self._SEP) for c in colors.split(self._MARKER) if c is not '']
            if self.isUnix :
                if endClz : data += self._uOFF
                print(eval('self._u'+'+self._u'.join(tokens))+data,end=ev)
            else :
                self.setColor(eval('self._w'+'|self._w'.join(tokens)))
                print(data,end=ev)
                stdout.flush()
                if endClz : self.setColor(self._wOFF)
        else: 
            print(data,end=ev)

Clz = Coloriz()
