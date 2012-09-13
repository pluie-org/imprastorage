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
from impra.util import IniFile, Rsa, RuTime, get_file_path
from impra.cli  import Cli



if __name__ == '__main__':
    
    Cli(get_file_path(__file__ ))
    #~ rt    = RuTime(__name__+'()')
    #~ conf  = ImpraConf(IniFile('./impra.ini'))
    #~ rsa   = Rsa(conf.ini.get('prvKey',conf.profile+'.keys'),conf.ini.get('pubKey',conf.profile+'.keys'))
    #~ impst = ImpraStorage(rsa, conf)
#~ 
    #~ print('\n -- INDEX DATA -- ')
    #~ impst.index.print()
    #~ print('-- LIST BOX --')
    #~ lb = impst.ih.listBox('/')
    #~ print(lb)
#~ 
    #~ #print('-- DELETE BIN --')
    #~ #impst.ih.deleteBin()
#~ 
    #~ filePath = '/media/Data/dev/big_toph3.jpg'
#~ 
    #~ lab = 'Meuf\'bonne aussi4'
#~ 
    #~ print('\n -- ADD FILE -- ')
    #~ impst.addFile(filePath,lab,conf.ini.get('name',conf.profile+'.infos'),'images')
#~ 
    #~ print('\n -- GET FILE -- ')
    #~ impst.getFile(lab)
#~ 
    #~ print('\n -- INDEX DATA -- ')
    #~ impst.index.print()
    #~ 
    #~ print('\n -- CLEAN -- ')
    #~ impst.clean()
#~ 
    #~ rt.stop()

#python  -O -m compileall impra/*.py
