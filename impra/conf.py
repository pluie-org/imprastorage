#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/conf.py
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
# ~~ module conf ~~

from getpass          import getuser as getUserLogin
from os               import sep
from os.path          import dirname, realpath, isdir, join

PRG_NAME            = 'Imprastorage'
PRG_PACKAGE         = 'impra'
PRG_SCRIPT          = PRG_NAME.lower()
PRG_CLI_NAME        = PRG_SCRIPT+'-cli'
PRG_VERS            = '1.01'
PRG_AUTHOR          = 'a-Sansara'
PRG_COPY            = 'pluie.org'
PRG_YEAR            = '2013'
PRG_WEBSITE         = 'http://imprastorage.sourceforge.net'
PRG_LICENSE         = 'GNU GPL v3'
PRG_RESOURCES_PATH  = '/usr/share/'+PRG_PACKAGE+sep
if not isdir(PRG_RESOURCES_PATH):
    PRG_RESOURCES_PATH = dirname(dirname(realpath(__file__)))+sep+'resources'+sep+PRG_PACKAGE+sep
#~ print(PRG_RESOURCES_PATH)
PRG_GLADE_PATH      = PRG_RESOURCES_PATH+'glade'+sep+PRG_PACKAGE+'.glade'
PRG_LICENSE_PATH    = PRG_RESOURCES_PATH+'/LICENSE'
PRG_LOGO_PATH       = join(PRG_RESOURCES_PATH,'..'+sep,'pixmaps'+sep,PRG_PACKAGE+sep,PRG_PACKAGE+'.png')
PRG_LOGO_ICON_PATH  = join(PRG_RESOURCES_PATH,'..'+sep,'pixmaps'+sep,PRG_PACKAGE+sep,PRG_PACKAGE+'_ico.png')
PRG_ABOUT_LOGO_SIZE = 160
PRG_ABOUT_COPYRIGHT = '(c) '+PRG_AUTHOR+' - '+PRG_COPY+' '+PRG_YEAR
PRG_ABOUT_COMMENTS  = ''.join(['ImpraStorage provided a  private imap access to store large files','\n', 'license ',PRG_LICENSE])
PRG_DESC            = """
  ImpraStorage provided a  private imap access to store large files. Each file stored on the server is split 
  in severals  random parts.  Each part also  contains random  noise data (lenght depends on a crypt key) to 
  ensure privacy and exclude easy merge without the corresponding key.

  An index of files  stored is encrypt (with the symmetric-key algorithm Kirmah) and regularly updated. Once
  decrypt, it permit to perform search on the server and download each part.

  Transfert process is transparent. Just vizualize locally the index of stored files and simply select files 
  to download or upload.  ImpraStorage automatically  launch the  parts to download, then merge parts in the 
  appropriate way to rebuild the original file.  Inversely, a file to upload is split (in several parts with 
  addition of noise data), and ImpraStorage randomly upload each parts then update the index.

"""

DEFVAL_USER_PATH    = ''.join([sep,'home',sep,getUserLogin(),sep])
DEFVAL_UKEY_PATH    = ''.join([DEFVAL_USER_PATH, '.', PRG_PACKAGE,sep])
DEFVAL_UKEY_NAME    = '.default.key'
DEFVAL_UKEY_LENGHT  = 1024

DEBUG               = True
UI_TRACE            = True
PCOLOR              = True

def redefinePaths(path):

    PRG_GLADE_PATH      = path+PRG_PACKAGE+sep+'glade'+sep+PRG_PACKAGE+'.glade'
    PRG_LICENSE_PATH    = path+PRG_PACKAGE+sep+'LICENSE'
    PRG_LOGO_PATH       = path+'pixmaps'+sep+PRG_PACKAGE+sep+PRG_PACKAGE+'.png'
    PRG_LOGO_ICON_PATH  = path+'pixmaps'+sep+PRG_PACKAGE+sep+PRG_PACKAGE+'_ico.png'
