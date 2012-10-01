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

from impra.core import ImpraConf, ImpraStorage
from impra.util import IniFile, RuTime, get_file_path, PColor
from impra.cli  import Cli
import sys, os

if __name__ == '__main__':
    #~ try :
        #~ print('\033[1;30mGray like Ghost\033[1;m')
        #~ print('\033[1;31mRed like Radish\033[1;m')
        #~ print('\033[1;32mGreen like Grass\033[1;m')
        #~ print('\033[1;33mYellow like Yolk\033[1;m')
        #~ print('\033[1;34mBlue like Blood\033[1;m')
        #~ print('\033[1;35mMagenta like Mimosa\033[1;m')
        #~ print('\033[1;36mCyan like Caribbean\033[1;m')
        #~ print('\033[1;37mWhite like Whipped Cream\033[1;m')
        #~ print('\033[1;38mCrimson like Chianti\033[1;m')
        #~ print('\033[1;41mHighlighted Red like Radish\033[1;m')
        #~ print('\033[1;42mHighlighted Green like Grass\033[1;m')
        #~ print('\033[1;43mHighlighted Brown like Bear\033[1;m')
        #~ print('\033[1;44mHighlighted Blue like Blood\033[1;m')
        #~ print('\033[1;45mHighlighted Magenta like Mimosa\033[1;m')
        #~ print('\033[1;46mHighlighted Cyan like Caribbean\033[1;m')
        #~ print('\033[1;47mHighlighted Gray like Ghost\033[1;m')
        #~ print('\033[1;48mHighlighted Crimson like Chianti\033[1;m')
        from re import finditer as regfinditer
        data = ' ==> MaClasse.maMethod "mon param","other Param" '
        qp = (int(a.start()) for a in list(regfinditer('\(', data)))
        print(data)
        print([m.start() for m in regfinditer('"', data)])
        sp = [m.start() for m in regfinditer('\(', data)]
        ep = [m.start() for m in regfinditer('\)', data)]

        Clz = PColor()
        if len(sp) > 0 :
            Clz.print(data[:sp[0]+1], Clz.fgb3, False)
            Clz.print(data[sp[0]+1:ep[0]], Clz.fgn2, False)
            Clz.print(data[ep[0]:], Clz.fgb3, False)
        else: Clz.print(data, Clz.fgb2, False)
        #~ clz.print(' -- ImpraStorage -- ',clz.BG4+clz.fgB3,False,True)
        #~ clz.print(' [',clz.fgB0,False)
        #~ clz.print('account',clz.fgB3,False)
        #~ clz.print(':',clz.fgB0,False)
        #~ clz.print('gplslot.001',clz.fgB4,False)
        #~ clz.print('] ',clz.fgB0)
        #~ print()
        #~ clz.print('color0',clz.fgb0)
        #~ clz.print('color1',clz.fgb1)
        #~ clz.print('color2',clz.fgb2)
        #~ clz.print('color3',clz.fgb3)
        #~ clz.print('color4',clz.fgb4)
        #~ clz.print('color5',clz.fgb5)
        #~ clz.print('color6',clz.fgb6)
        #~ clz.print('color7',clz.fgb7)
        #~ print()
        #~ clz.print('color0',clz.fgB0)
        #~ clz.print('color1',clz.fgB1)
        #~ clz.print('color2',clz.fgB2)
        #~ clz.print('color3',clz.fgB3)
        #~ clz.print('color4',clz.fgB4)
        #~ clz.print('color5',clz.fgB5)
        #~ clz.print('color6',clz.fgB6)
        #~ clz.print('color7',clz.fgB7)
        #~ print()
        #~ clz.print('color0',clz.bg0+clz.fgb0)
        #~ clz.print('color1',clz.bg1+clz.fgb0)
        #~ clz.print('color2',clz.bg2+clz.fgb0)
        #~ clz.print('color3',clz.bg3+clz.fgb0)
        #~ clz.print('color4',clz.bg4+clz.fgb0)
        #~ clz.print('color5',clz.bg5+clz.fgb0)
        #~ clz.print('color6',clz.bg6+clz.fgb0)
        #~ clz.print('color7',clz.bg7+clz.fgb0)
        #~ print()
        #~ clz.print('color0',clz.BG0+clz.fgB0)
        #~ clz.print('color1',clz.BG1+clz.fgB0)
        #~ clz.print('color2',clz.BG2+clz.fgB0)
        #~ clz.print('color3',clz.BG3+clz.fgB0)
        #~ clz.print('color4',clz.BG4+clz.fgB0)
        #~ clz.print('color5',clz.BG5+clz.fgB0)
        #~ clz.print('color6',clz.BG6+clz.fgB0)
        #~ clz.print('color7',clz.BG7+clz.fgB0)
        #~ print()
        #Cli(get_file_path(__file__ ))        
        #os.system('echo python imprastorage data -l')
        
    #~ except Exception as e :
        #~ print(e)

#python  -O -m compileall impra/*.py
