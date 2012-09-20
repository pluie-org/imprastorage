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
import sys, os, platform
import impra.crypt as crypt
import impra.util  as util
import impra.core  as core
from   impra.util  import Clz


LINE_SEP_LEN  = 120
LINE_SEP_CHAR = '―'
if not Clz.isUnix : LINE_SEP_CHAR = '-'
APP_TITLE     = 'ImpraStorage'
APP_VERSION   = '0.5'
APP_AUTHOR    = 'a-Sansara'
APP_COPY      = 'pluie.org'
APP_LICENSE   = 'GNU GPLv3'
APP_DESC      = """
ImpraStorage provided a private imap access to store large files.
Each file stored on the server is split in severals random parts.
Each part also contains random noise data (lenght depends on a crypt key)
to ensure privacy and exclude easy merge without the corresponding key.

An index of files stored is encrypt (with the symmetric-key algorithm
Kirmah) and regularly updated. Once decrypt, it permit to perform search
on the server and download each part.

transfert process is transparent. Just vizualize locally the index of
stored files and simply select files to download or upload.
ImpraStorage automatically launch the parts to download, then merge parts
in the appropriate way to rebuild the original file. Inversely, a file
to upload is split (in several parts with addition of noise data), and
ImpraStorage randomly upload each parts then update the index.

"""

def printLineSep(sep,lenSep):
    """"""
    Clz.print(sep*lenSep, Clz.fgB0)
def printHeaderTitle(title):
    """"""
    Clz.print(' -- %s -- ' % title, Clz.BG4+Clz.fgB7, False, True)

def printHeaderPart(label,value):
    """"""
    Clz.print(' [' , Clz.fgB0, False)
    Clz.print(label, Clz.fgB3, False)
    Clz.print(':'  , Clz.fgB0, False)
    Clz.print(value, Clz.fgB4, False)
    Clz.print('] ' , Clz.fgB0, False)



class _OptionParser(OptionParser):
    """A simplified OptionParser"""
    
    def format_description(self, formatter):
        return self.description

    def format_epilog(self, formatter):
        return self.epilog


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Cli ~~

class Cli:
    
    def __init__(self,path):

        self.ini    = util.IniFile(path+'impra.ini')
        parser = _OptionParser(prog='imprastorage', usage='\n\n\
------------------------------------------------------------------------------\n\
-- %s                                                             --\n\
------------------------------------------------------------------------------\n\
-- version : %s                                     copyright : %s --\n\
-- author  : %s                                  license : %s --\n\
------------------------------------------------------------------------------\n\
\n\
%s conf [-D|-L| -K,-H {host},-U {user},-X {password},-P {port},\n\
                  -B {boxname}] [-A profileName]\n\
%s data [-l |-a {file, label} |-g {id} |-s {pattern} | -r {id}]\n\
                  [-c {catg}, -u {owner}]'
            % (APP_TITLE,APP_VERSION,APP_COPY,APP_AUTHOR,APP_LICENSE,APP_TITLE.lower(),APP_TITLE.lower()) , epilog="""

conf command Examples:

  Initialize program and set config on default profile with keys generation :
    imprastorage conf -K -H imap.gmail.com -P 993 -U login -X password

  Set config on a new profile with same keys from previous active profile:
    imprastorage conf -H myimapserver.net -P 993 -U login -X password -B boxname -A profile1

  Load config from a profile (wich become active) :
    imprastorage conf -DA profile2

  List config from profile :
    imprastorage conf -LA profile1


data command Examples:
    
  List index
    imprastorage data -l

  Add file
    imprastorage data -a /path/tofile 'my video'

  Add file with category (category is also a directory structure recreate
  when downloading files)
    imprastorage data -a /path/tofile '2009 - en la playa' -c videos/perso/2009

  Get file by id
    imprastorage data -g 22

  Remove from server a file by id
    imprastorage data -g 22
   
  Search files matching pattern :
    imprastorage data -s 'holydays'

  Search files upload by a particular user on a category :
    imprastorage data -s * -c films -u myfriend

""",description=APP_DESC)

        gpData      = OptionGroup(parser, '\n------------------------------------\ndata related Options (command data)')
        gpConf      = OptionGroup(parser, '\n------------------------------------\nconf related Options (command conf)')

        # metavar='<ARG1> <ARG2>', nargs=2
        parser.add_option('-v', '--version'       , help='show program\'s version number and exit'                     , action='store_true' , default=False)
        parser.add_option('-q', '--quiet'         , help='don\'t print status messages to stdout'                      , action='store_false', default=True)
        parser.add_option('-d', '--debug'         , help='set debug mode'                                              , action='store_true' , default=False)

        gpData.add_option('-l', '--list'          , help='list index on imap server'                                   , action='store_true' )
        gpData.add_option('-a', '--add'           , help='add file FILE with specified LABEL on server'                , action='store',       metavar='FILE LABEL ', nargs=2)
        gpData.add_option('-g', '--get'           , help='get file with specified ID from server'                      , action='store',       metavar='ID         ')
        gpData.add_option('-s', '--search'        , help='search file with specified PATTERN'                          , action='store',       metavar='PATTERN    ')
        gpData.add_option('-r', '--remove'        , help='remove FILE with specified ID from server'                   , action='store',       metavar='ID         ')
        gpData.add_option('-c', '--category'      , help='set specified CATEGORY (crit. for opt. -l,-a or -s)'         , action='store',       metavar='CATG       '  , default='')
        gpData.add_option('-u', '--user'          , help='set specified USER (crit. for opt. -l,-a or -s)'             , action='store',       metavar='OWNER      '  , default='all')
        #gpData.add_option('-o', '--output-dir'    , help='set specified OUTPUT DIR (for opt. -l,-a,-d or -g)'          , action='store',       metavar='DIR        ')
        parser.add_option_group(gpData)                                                                             

        gpConf.add_option('-L', '--list-conf'     , help='list configuration'                                          , action='store_true',  default=False)
        gpConf.add_option('-D', '--load-conf'     , help='load configuration'                                          , action='store_true',  default=False)
        gpConf.add_option('-H', '--set-host'      , help='set imap host server'                                        , action='store',       metavar='HOST       ')
        gpConf.add_option('-U', '--set-user'      , help='set imap user login'                                         , action='store',       metavar='USER       ')
        gpConf.add_option('-X', '--set-pass'      , help='set imap user password'                                      , action='store',       metavar='PASS       ')
        gpConf.add_option('-P', '--set-port'      , help='set imap port'                                               , action='store',       metavar='PORT       ')
        gpConf.add_option('-N', '--set-name'      , help='set user name'                                               , action='store',       metavar='NAME       ')
        gpConf.add_option('-B', '--set-boxn'      , help='set boxName on imap server (default:[%default])'             , action='store',       metavar='BOXNAME    ')
        gpConf.add_option('-K', '--gen-keys'      , help='generate new key'                                            , action='store_true',  default=False)
        gpConf.add_option('-A', '--active-profile', help='set active profile'                                          , action='store',       metavar='PROFILE    ')

        parser.add_option_group(gpConf)

        (o, a) = parser.parse_args()
        
        

        if not a:
            parser.print_help()
            print()
            parser.error(' no commando specified')
            sys.exit(1)

        else:
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ conf CMD ~~
            if a[0] == 'conf' :
                
                if o.active_profile==None: 
                    if self.ini.has('profile') : o.active_profile = self.ini.get('profile')
                    else : o.active_profile = 'default'
                
                print(self.ini)
                
                if o.load_conf   : self.load_profile(o)

                elif o.list_conf : print(self.ini.toString(o.active_profile))

                else :
                    if not o.set_host and not o.set_user and not o.set_pass and not o.set_port and not o.set_boxn and not o.set_name and not o.gen_keys:
                        parser.error(' no options specified')
                    else :
                        if o.set_port and not util.represents_int(o.set_port):
                            parser.error(' port must be a number')
                            sys.exit(1)
                        if o.set_boxn: self.ini.set('box' , o.set_boxn,o.active_profile+'.imap')
                        if o.set_host: self.ini.set('host', o.set_host,o.active_profile+'.imap')
                        if o.set_user: self.ini.set('user', o.set_user,o.active_profile+'.imap')
                        if o.set_pass: self.ini.set('pass', o.set_pass,o.active_profile+'.imap')
                        if o.set_port: self.ini.set('port', o.set_port,o.active_profile+'.imap')                    
                        if o.set_name: self.ini.set('name', o.set_name,o.active_profile+'.infos')
                        if o.gen_keys:
                            kg = crypt.KeyGen(256)
                            self.ini.set('key' ,kg.key,o.active_profile+'.keys')
                            self.ini.set('mark',kg.mark,o.active_profile+'.keys')
                            self.ini.set('salt','-¤-ImpraStorage-¤-',o.active_profile+'.keys')
                        if self.check_profile(o.active_profile):
                            self.ini.set('profile', o.active_profile)
                        self.ini.write()
                        print(self.ini.toString(o.active_profile))

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ data CMD ~~
            elif a[0] == 'data' :

                o.active_profile = self.ini.get('profile')
                    
                if not o.list and not o.add and not o.get and not o.search and not o.remove :
                    parser.error(' no options specified')
                else :
                    
                    if self.check_profile(o.active_profile):
                        conf  = core.ImpraConf(self.ini,o.active_profile)
                        impst = None
                        try:
                            impst = core.ImpraStorage(conf)
                        except crypt.BadKeyException as e :
                            print('Error : ')
                            print(e)
                            print("""
it seems that your current profile %s has a wrong key to decrypt index on server.
you can remove index but all presents files on the box %s will be unrecoverable
""" % (o.active_profile, conf.get('box','imap')))
                            remIndex = input('remove index ? (yes/no)')
                            if remIndex.lower()=='yes':
                                impst = core.ImpraStorage(conf, True)
                            else : 
                                print('bye')
                                sys.exit(1)                        
                    
                        if o.list :
                            uid     = conf.get('uid' ,'index')
                            date    = conf.get('date','index')
                            account = conf.get('user','imap')
                            if impst.index != None:
                                noData = impst.index.isEmpty()
                                if uid  == None or noData : uid  = 'EMPTY'
                                if date == None or noData : date = ''
                                core.clear()
                                printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
                                printHeaderTitle(APP_TITLE)
                                printHeaderPart('account',account)
                                printHeaderPart('index',uid)
                                printHeaderPart('box',impst.rootBox)
                                Clz.print(date, Clz.fgB7, True, True)
                                printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
                                impst.index.print()

                            status, resp = impst.ih.srv.search(None, '(SUBJECT "%s")' % '584d15abeb71fbd92fa5861970088b32ebb1d2d6650cec6115a28b64877d70f2')
                            ids = [m for m in resp[0].split()]
                            for mid in ids :
                                status, resp = impst.ih.srv.fetch(mid,'(UID RFC822.SIZE)')                                
                                print(mid,status,resp)
                            
                        elif o.add :
                            done = impst.addFile(o.add[0],o.add[1],o.user,o.category)
                            if done :
                                print('OK')

                        elif o.get :
                            ids = []
                            for sid in o.get.split(',') :
                                seq = sid.split('-')
                                if len(seq)==2 : ids.extend(range(int(seq[0]),int(seq[1])+1))
                                else: ids.append(sid)
                            for sid in ids :                                
                                key = impst.index.getById(str(sid))
                                if key !=None : 
                                    done = impst.getFile(key)
                                    if done :
                                        print('OK')
                                else: print('-- `%s` is not a valid id --' % sid)

                        elif o.search :
                            matchIds = impst.index.getByPattern(o.search)
                            if matchIds is not None: 
                                headstr = '-'*120+'\n -- SEARCH: `'+o.search+'` -- found '+str(len(matchIds))+' results --\n'+'-'*120
                                impst.index.print(headstr,matchIds)
                            else:
                                print(' -- no match found for pattern `%s` --' % o.search)
                        elif o.remove :
                            print(o.remove)

                    #~ filePath = '/media/Data/dev/big_toph3.jpg' 
                    #~ lab = 'Meuf\'bonne aussi4' 
                    #~ print('\n -- ADD FILE -- ')
                    #~ impst.addFile(filePath,lab,conf.get('name','infos'),'images')                    
                    
                #~ else : 
                    #~ self.load_profile(o)
                    #~ print('data cmd')    
                    #~ print(o)

            else : parser.print_help()



    def check_profile(self,profile):
        """"""
        return self.ini.hasSection(profile+'.keys') and self.ini.has('host',profile+'.imap') and self.ini.has('user',profile+'.imap') and self.ini.has('pass',profile+'.imap') and self.ini.has('port',profile+'.imap')



    def load_profile(self,o):
        """"""
        if self.check_profile(o.active_profile):
            print('profile '+o.active_profile+' loaded')
            self.ini.set('profile', o.active_profile)
            self.ini.write()
        else :
            if not self.ini.hasSection(o.active_profile+'.imap'):
                print('profile '+o.active_profile+' don\'t exist !')
            else :
                print('profile '+o.active_profile+' can\'t be load - incomplete\n (did you remember to generate keys ?)')
