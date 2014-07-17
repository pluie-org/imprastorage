#!/usr/bin/env python
#-*- coding: utf-8 -*-
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

import sys
from cx_Freeze import setup, Executable

productName = "ImpraStorage"

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","subprocess","importlib","platform"], 
                     "excludes": ["tkinter"],
                     "include_files": [('launcher.bat','launcher.bat'),('cmd.bat','cmd.bat'),('wk','wk')]
                        }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
#    base = "Win32GUI"






if 'bdist_msi' in sys.argv:
    sys.argv += ['--initial-target-dir', 'C:\\' + productName]
#    sys.argv += ['--install-script', 'install.py']

    exe = Executable(
            script="imprastorage.py",
            base=None,
            targetName="imprastorage.exe"
        )
    setup(
            name="ImpraStorage.exe",
            version="1.01",
            author="a-Sansara",
            description="ImpraStorage provided a private imap access to store large files. License GNU GPLv3 Copyright 2014 pluie.org",
            executables=[exe],
            options = {"build_exe": build_exe_options},
            scripts=[
                
                ]
        ) 
else :

	setup(  name = "ImpraStorage",
	        version = "1.01",
	        description = "ImpraStorage provided a  private imap access to store large files",
	        options = {"build_exe": build_exe_options},
	        executables = [Executable("imprastorage.py", base=base)])
