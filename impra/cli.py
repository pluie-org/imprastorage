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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ package cli ~~
    
from optparse import OptionParser, OptionGroup
desc="""version : 0.41                                    copyright : pluie.org 
author  : a-Sansara                                 license : GNU GPLv3

ImpraStorage provided a private imap access to store large files.
Each file stored on the server is split in severals random parts.
Each part also contains random noise data (lenght depends on a crypt key)
to ensure privacy and exclude easy merge without the corresponding key.

An index of files stored is encrypt (rsa 1024) and regularly updated.
Once decrypt, it permit to perform search on the server and
download each part.

transfert process is transparent. Just vizualize locally the index of
stored files and simply select files to download or upload.
ImpraStorage automatically launch the parts to download, then merge parts
in the appropriate way to rebuild the original file. Inversely, a file
to upload is splitt -in several parts with addition of noise data), and
ImpraStorage randomly upload each parts then update the index.

"""


class _SimplerOptionParser(OptionParser):
    """A simplified OptionParser"""
    
    def format_description(self, formatter):
        return self.description

    def format_epilog(self, formatter):
        return self.epilog

parser      = _SimplerOptionParser(prog='imprastorage', usage='\n\n %prog COMMAND [OPTION]...',epilog="""

conf command Examples:

  Initialize program and set config on default profile with keys generation :
    imprastorage conf -K -H imap.gmail.com -P 993 -U login -X password

  Set config on a new profile with same keys from previous active profile:
    imprastorage conf -A profile1 -H myimapserver.net -P 993 -U login \\
    -X password -B boxname

  Load config from a profile (wich become active) :
    imprastorage conf -DA profile2

  List config from profile :
    imprastorage conf -LA profile1


data command Examples:
    
  List index on a specified box (different from box on active profile)
    imprastorage data -lb boxname

  Add file
    imprastorage data -a /path/tofile 'my video'

  Add file with category (category is also a directory structure recreate
  when downloading files)
    imprastorage data -a /path/tofile '2009 - en la playa' -c videos/perso/2009

  Get file 
    imprastorage data -g '2009 - en la playa'

  Get file by id
    imprastorage data -G 22

  Remove from server a file by id
    imprastorage data -R 22
   
  Search files matching pattern :
    imprastorage data -s 'holydays'

  Search files upload by a particular user on a category :
    imprastorage data -s * -c films -u myfriend

""",description=desc)

gpData      = OptionGroup(parser, '\ndata related Options (command data)\n-----------------------------------')
gpConf      = OptionGroup(parser, '\nconf related Options (command conf)\n-----------------------------------')

# metavar='<ARG1> <ARG2>', nargs=2
parser.add_option('-v', '--version'       , help='show program\'s version number and exit'                     , dest='version'        , action='store_true' , default=False)
parser.add_option('-q', '--quiet'         , help='don\'t print status messages to stdout'                      , dest='verbose'        , action='store_false', default=True)
parser.add_option('-f', '--force'         , help='dont confirm and force action'                               , dest='force'          , action='store_true' , default=False)
parser.add_option('-d', '--debug'         , help='set debug mode'                                              , dest='debug'          , action='store_true' , default=False)

gpData.add_option('-l', '--list'          , help='list index on imap server'                                   , dest='list_index'     , action='store_true' , default=False)
gpData.add_option('-b', '--boxname'       , help='switch boxname on imap server'                               , dest='switch_boxname' , action='store',       metavar='BOXN')
gpData.add_option('-a', '--add'           , help='add file FILE with specified LABEL on server'                , dest='add'            , action='store',       metavar='FILE LABEL', nargs=2)
gpData.add_option('-g', '--get'           , help='get file with specified LABEL from server'                   , dest='get'            , action='store',       metavar='LABEL')
gpData.add_option('-G', '--get-by-id'     , help='get file with specified ID from server'                      , dest='get_by_id'      , action='store',       metavar='ID')
gpData.add_option('-s', '--search'        , help='search file with specified PATTERN'                          , dest='search'         , action='store',       metavar='PATTERN')
gpData.add_option('-c', '--category'      , help='set specified CATEGORY (crit. for opt. -l,-a or -s)'         , dest='category'       , action='store',       metavar='CATG'   , default='none')
gpData.add_option('-u', '--user'          , help='set specified USER (crit. for opt. -l,-a or -s)'             , dest='owner'          , action='store',       metavar='OWNER'  , default='all')
gpData.add_option('-o', '--output-dir'    , help='set specified OUTPUT DIR (for opt. -l,-a,-d or -g)'          , dest='output'         , action='store',       metavar='DIR')
gpData.add_option('-r', '--remove'        , help='remove FILE with specified LABEL from server'                , dest='remove'         , action='store',       metavar='LABEL')
gpData.add_option('-R', '--remove-by-id'  , help='remove FILE with specified ID from server'                   , dest='remove_by_id'   , action='store',       metavar='ID')
parser.add_option_group(gpData)                                                                             

gpConf.add_option('-L', '--list-conf'     , help='list configuration'                                          , dest='list_conf'      , action='store')
gpConf.add_option('-A', '--active-profile', help='set active profile'                                          , dest='profile'        , action='store',       metavar='PROFILE', default='default')
gpConf.add_option('-H', '--set-host'      , help='set imap host server'                                        , dest='host'           , action='store',       metavar='HOST')
gpConf.add_option('-U', '--set-user'      , help='set imap user login'                                         , dest='user'           , action='store',       metavar='USER')
gpConf.add_option('-X', '--set-pass'      , help='set imap user password'                                      , dest='password'       , action='store',       metavar='PASS')
gpConf.add_option('-P', '--set-port'      , help='set imap port (default:[%default])'                          , dest='port'           , action='store',       metavar='PORT'   , default=993)
gpConf.add_option('-B', '--set-boxname'   , help='set boxName on imap server (default:[%default])'             , dest='boxname'        , action='store',       metavar='BOXN'   , default='__IMPRA')
gpConf.add_option('-K', '--gen-keys'      , help='generate new pub/private keys'                               , dest='generate_keys'  , action='store_true',  default=False)
gpConf.add_option('-D', '--load-conf'     , help='load configuration'                                          , dest='load_conf'      , action='store_true',  default=False)
parser.add_option_group(gpConf)

def show_index():
    print('show_index')

(opts, args) = parser.parse_args()
#~ if not 'toto' in opts.__dict__ :
    #~ print("mandatory option is missing\n")
    #~ parser.print_help()
    #~ exit(-1)*/
#~ print('--------')
#~ print(opts)
#~ print('--------')
#~ print(args)
    
