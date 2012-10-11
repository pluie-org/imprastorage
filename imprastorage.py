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

from impra.core import ImpraConf, ImpraStorage, realpath, dirname, abspath, sep
from impra.util import IniFile, RuTime, get_file_path, Clz, mprint
from impra.cli  import Cli
import sys, os

# TODO
#   - check encrypt marker on crypt file
#   - readjust cli commands
#   - write help in colors

if __name__ == '__main__':
    try:
        if not Clz.isUnix:
            if len(sys.argv)>1 and sys.argv[1] == '--run' :
                Cli.print_header(None)
                os.system(realpath('./cmd.bat'))
            elif len(sys.argv)==1 :
                os.system(realpath('./launcher.bat'))
            else: Cli(realpath('./')+sep)
        else :
            Cli(get_file_path(realpath('./')+sep))
    except KeyboardInterrupt as e :        
        Clz.print('\nKeyboardInterrupt\n', Clz.fgB1)

#python  -O -m compileall impra/*.py
