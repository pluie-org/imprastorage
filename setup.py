#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  setup.py
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

from impra             import conf
from distutils.core     import setup
import glob
import os

# I18N
I18NFILES = []

for filepath in glob.glob('resources/locale/*/LC_MESSAGES/*.mo'):
    lang = filepath[len('resources/locale/'):]
    targetpath = os.path.dirname(os.path.join('share/locale',lang))
    I18NFILES.append((targetpath, [filepath]))

setup(name      = conf.PRG_NAME,
      version   = conf.PRG_VERS,
      packages  = [conf.PRG_PACKAGE, 'psr'],
      scripts   = ['scripts/'+conf.PRG_SCRIPT, 'scripts/'+conf.PRG_CLI_NAME],
      data_files= [('/usr/share/pixmaps/'+conf.PRG_PACKAGE    , glob.glob('resources/pixmaps/'+conf.PRG_PACKAGE+'/*.png')),
                   ('/usr/share/applications'                 , ['resources/'+conf.PRG_PACKAGE+'.desktop']),
                   ('/usr/share/'+conf.PRG_PACKAGE            , glob.glob('resources/'+conf.PRG_PACKAGE+'/LICENSE')),
                   ('/usr/share/'+conf.PRG_PACKAGE+'/glade'   , glob.glob('resources/'+conf.PRG_PACKAGE+'/glade/*.glade'))]
                   + I18NFILES
      )
