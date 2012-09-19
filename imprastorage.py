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
from impra.util import IniFile, RuTime, get_file_path
from impra.cli  import Cli


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
        Cli(get_file_path(__file__ ))
    #~ except Exception as e :
        #~ print(e)

#python  -O -m compileall impra/*.py
