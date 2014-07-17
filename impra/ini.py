#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/ini.py
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  software  : ImpraStorage    <http://kirmah.sourceforge.net/>
#  version   : 1.01
#  date      : 2014
#  licence   : GPLv3.0   <http://www.gnu.org/licenses/>
#  author    : a-Sansara <[a-sansara]at[clochardprod]dot[net]>
#  copyright : pluie.org <http://www.pluie.org/>
#
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  This file is part of ImpraStorage.
#
#  ImpraStorage is free software (free as in speech) : you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  ImpraStorage is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ImpraStorage.  If not, see <http://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module ini ~~

from re                 import split as regsplit
from psr.sys            import Sys, Io, Const
from psr.ini            import IniFile
from psr.log            import Log
from kirmah.crypt       import KeyGen

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class IniFile ~~

class KiniFile(IniFile):
    """Read and write inifile"""

    @Log(Const.LOG_BUILD)
    def __init__(self, path, keyPath=None):
        """"""
        self.path    = path
        self.dic     = {}
        self.keyPath = path+'.key' if keyPath is None else keyPath
        if not Io.file_exists(self.keyPath) :
            kg = KeyGen()
            Io.set_data(self.keyPath, kg.key)            
            if not Io.file_exists(path) :                
                self.set('profile'  , 'default', 'main')
                self.set('key'  ,kg.key,'default.keys')
                self.set('mark' ,kg.mark,'default.keys')
                self.set('salt' ,'-*-ImpraStorage-*-','default.keys')
                self.save()
        self.read()


    @Log()
    def save(self,path=None,notAssign=False):
        """"""
        path = path if path is not None else self.path
        Io.set_data(path, '# last updated : '+str(Sys.datetime.now())+Const.LF+self.toString())
        call = ' '.join(['python3', 'kirmah-cli.py', 'enc', '-qf', path, '-z', '-r', '-m', '-o', path+'.kmh', '-k', self.keyPath ])
        Sys.sysCall(call)
        Io.removeFile(path)
        if not notAssign : self.path = path


    @Log()
    def read(self):
        """"""
        try:
            call = ' '.join([Sys.executable, 'kirmah-cli.py', 'dec', '-qf', self.path+'.kmh', '-z', '-r', '-m', '-o', self.path, '-k', self.keyPath ])
            Sys.sysCall(call)            
            with Io.rfile(self.path, False) as fi:
                csection = 'main'
                self.dic[csection] = {}
                for l in fi:
                    l = l.rstrip().lstrip()
                    if len(l) > 0 and not l[0]=='#' :
                        d = regsplit(' *= *', l , 1)
                        if len(d)> 1:
                            self.dic[csection][d[0]] = d[1] if d[1] is not None else ''
                        elif len(l)>0 and l[0]=='[':
                            csection = l.strip('[]')
                            self.dic[csection] = {}
            Io.removeFile(self.path)
        except IOError :
            pass


    @Log()
    def delete(self):
        Io.removeFile(self.path+'.kmh')
        self.dic  = {}
