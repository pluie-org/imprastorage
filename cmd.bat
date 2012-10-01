:: # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
::                                                                               #
::   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
::   version   : 0.7                                                             #
::   date      : 2012                                                            #
::   licence   : GPLv3.0   <http://www.gnu.org/licenses/>                        #
::   author    : a-Sansara <http://www.a-sansara.net/>                           #
::   copyright : pluie.org <http://www.pluie.org/>                               #
::                                                                               #
:: # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
::
::   This file is part of ImpraStorage.
::
::   ImpraStorage is free software (free as in speech) : you can redistribute it 
::   and/or modify it under the terms of the GNU General Public License as 
::   published by the Free Software Foundation, either version 3 of the License, 
::   or (at your option) any later version.
::
::   ImpraStorage is distributed in the hope that it will be useful, but WITHOUT 
::   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
::   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
::   more details.
::
::   You should have received a copy of the GNU General Public License
::   along with ImpraStorage.  If not, see <http://www.gnu.org/licenses/>.
@echo off
TITLE ImpraStorage (GNU GPLv3)
set cmd=''
set /P cmd=imprastorage %=%
set acmd=%cmd:"='%
imprastorage.exe %cmd%
cmd.bat
