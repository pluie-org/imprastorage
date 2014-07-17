#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/ini.py
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  software  : Kirmah    <http://kirmah.sourceforge.net/>
#  version   : 2.18
#  date      : 2014
#  licence   : GPLv3.0   <http://www.gnu.org/licenses/>
#  author    : a-Sansara <[a-sansara]at[clochardprod]dot[net]>
#  copyright : pluie.org <http://www.pluie.org/>
#
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  This file is part of Kirmah.
#
#  Kirmah is free software (free as in speech) : you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  Kirmah is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Kirmah.  If not, see <http://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module ini ~~

from re                 import split as regsplit
from psr.sys            import Sys, Io, Const
from psr.log            import Log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class IniFile ~~

class IniFile:
    """Read and write inifile"""

    @Log(Const.LOG_BUILD)
    def __init__(self, path):
        """"""
        self.path = path
        self.dic  = {'main':{}}
        self.read()
        if not 'main' in self.dic :
            self.dic['main'] = {}


    @Log(Const.LOG_DEBUG)
    def isEmpty(self):
        """"""
        return len(self.dic)==0


    @Log(Const.LOG_DEBUG)
    def has(self, key, section='main'):
        """"""
        d = self.hasSection(section) and (key in self.dic[section])
        return d


    @Log(Const.LOG_DEBUG)
    def hasSection(self, section):
        """"""
        d = (section in self.dic)
        return d


    @Log(Const.LOG_DEBUG)
    def get(self, key, section='main'):
        """"""
        return self.dic[section][key]
        #if section in self.dic :
        #    return self.dic[section][key]
        #else :
        #    return ''


    @Log(Const.LOG_DEBUG)
    def set(self, key, val, section='main'):
        """"""
        v = None
        if not section in self.dic:
            self.dic[section]  = {}
        if key in self.dic[section]:
            v = self.dic[section].pop(key)
        self.dic[section][key] = str(val)
        return v


    @Log()
    def rem(self, key, section):
        """"""
        v = None
        if section in self.dic :
            if key == '*' :
                v = self.dic.pop(section)
            elif key in self.dic[section]:
                v = self.dic[section].pop(key)
        return v


    @Log()
    def save(self,path=None):
        """"""
        Io.set_data(path if path is not None else self.path, '# last updated : '+str(Sys.datetime.now())+Const.LF+self.toString())


    @Log(Const.LOG_DEBUG)
    def getSection(self, section):
        """"""
        data = {}
        for s in self.dic :
            if s.startswith(section, 0) : data[s[len(section)+1:]] = self.dic[s].copy()
        return data


    @Log(Const.LOG_DEBUG)
    def getSections(self):
        """"""
        l = {}
        for s in self.dic:
            section = s.split('.')
            if len(section)> 1 and not section[0] in l :
                l[section[0]] = 1
        return [k for i,k in enumerate(l)]


    @Log(Const.LOG_DEBUG)
    def toString(self, section='*'):
        """"""
        content = ''
        main    = ''
        for s in self.dic:
            if section=='*' or section+'.'==s[:len(section)+1]:
                if s!='main':
                    content += Const.LF+'['+s+']'+Const.LF
                for k in sorted(self.dic[s]):
                    k = k.rstrip(' ')
                    v = self.dic[s][k] if self.dic[s][k] is not None else ''
                    if s!='main' :
                        content += k+' = '+str(v)+Const.LF
                    else : main += k+' = '+str(v)+Const.LF
        return main + content


    @Log(Const.LOG_DEBUG)
    def print(self, section='*', withoutSectionName=False):
        """"""
        if section=='main' or section=='*' :
            self.printSection('main', withoutSectionName)

        for s in self.dic:
            if section=='*' or section+'.'==s[:len(section)+1]:
                if s!='main':
                    self.printSection(s, withoutSectionName)


    @Log(Const.LOG_DEBUG)
    def printSection(self, sectionName, withoutSectionName=False):
        """"""
        if sectionName!='main':
            Sys.dprint()
            if not withoutSectionName :
                Sys.echo('['+sectionName+']', Sys.Clz.fgB3)
            else:
                Sys.echo('['+sectionName.split('.')[1]+']', Sys.Clz.fgB3)
        if sectionName in self.dic :
            for k in sorted(self.dic[sectionName]):
                k = k.rstrip(' ')
                a = ''
                Sys.echo(k.ljust(10,' ')+' = '       , Sys.Clz.fgn7, False)
                if self.dic[sectionName][k] is not None :
                    if len(self.dic[sectionName][k]) > 98: a = '…'
                    if Sys.isUnix() or k is not 'key' :
                        Sys.echo(self.dic[sectionName][k][:98]+a, Sys.Clz.fgN2)
                    else:
                        Sys.echo('key is masked', Sys.Clz.fgb1)

    @Log()
    def read(self):
        """"""
        try:
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
        except IOError :
            pass


    @Log()
    def delete(self):
        Io.removeFile(self.path)
        self.dic  = {}
