#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.6                                                             #
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
APP_VERSION   = '0.6'
APP_AUTHOR    = 'a-Sansara'
APP_COPY      = 'pluie.org'
APP_LICENSE   = 'GNU GPLv3'
APP_DESC      = """
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

def printLineSep(sep,lenSep):
    """"""
    Clz.print(sep*lenSep, Clz.fgN0)
def printHeaderTitle(title):
    """"""
    Clz.print(' == '+title+' == ', Clz.BG4+Clz.fgB7, False, True)

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
        parser = _OptionParser()
        parser.print_help  = self.print_help
        parser.print_usage = self.print_usage
        self.wkpath        = path+core.sep+'wk'+core.sep
        gpData      = OptionGroup(parser, '')
        gpConf      = OptionGroup(parser, '')

        # metavar='<ARG1> <ARG2>', nargs=2
        parser.add_option('-q', '--quiet'         , help='don\'t print status messages to stdout'                      , action='store_false', default=True)
        parser.add_option('-d', '--debug'         , help='set debug mode'                                              , action='store_true' , default=False)
        
        gpData.add_option('-c', '--category'      , help='set specified CATEGORY (crit. for opt. -l,-a or -s)'         , action='store',       metavar='CATG         ')
        gpData.add_option('-u', '--user'          , help='set specified USER (crit. for opt. -l,-a or -s)'             , action='store',       metavar='OWNER        ')
        gpData.add_option('-o', '--order'         , help='set colon ORDER (crit. for opt. -l and -s)'                  , action='store',       metavar='ORDER        '  , default='ID')
        gpData.add_option('-O', '--order-inv'     , help='set colon ORDER_INVERSE (crit. for opt. -l and -s)'          , action='store',       metavar='ORDER_INVERSE')
        #gpData.add_option('-o', '--output-dir'    , help='set specified OUTPUT DIR (for opt. -l,-a,-d or -g)'          , action='store',       metavar='DIR        ')
        parser.add_option_group(gpData)                                                                             

        gpConf.add_option('-V', '--view'          , help='view configuration'                                          , action='store'                     )
        gpConf.add_option('-L', '--load'          , help='load configuration'                                          , action='store'                     )
        gpConf.add_option('-S', '--save'          , help='save configuration'                                          , action='store'                     )
        gpConf.add_option('-C', '--check'         , help='check configuration'                                         , action='store'                     )
        gpConf.add_option('-H', '--set-host'      , help='set imap host server'                                        , action='store',       metavar='HOST         ')
        gpConf.add_option('-U', '--set-user'      , help='set imap user login'                                         , action='store',       metavar='USER         ')
        gpConf.add_option('-X', '--set-pass'      , help='set imap user password'                                      , action='store',       metavar='PASS         ')
        gpConf.add_option('-P', '--set-port'      , help='set imap port'                                               , action='store',       metavar='PORT         ')
        gpConf.add_option('-N', '--set-name'      , help='set user name'                                               , action='store',       metavar='NAME         ')
        gpConf.add_option('-B', '--set-boxname'   , help='set boxName on imap server (default:[%default])'             , action='store',       metavar='BOXNAME      ')
        gpConf.add_option('-K', '--gen-key'       , help='generate new key'                                            , action='store_true',  default=False)

        parser.add_option_group(gpConf)

        (o, a) = parser.parse_args()
        
        print()
        if not a:

            try :
                if not o.help : 
                    self.parserError(' no commando specified')
                else :
                    core.clear()
                    parser.print_help()
            except :
                self.parserError(' no commando specified')

        else:
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ conf CMD ~~
            if a[0] == 'conf' :
                core.clear()
                if o.load is not None or o.view is not None or o.save is not None :
                    
                    if o.view is not None :
                        o.active_profile = o.view
                    if o.load is not None :
                        o.active_profile = o.load
                    if o.save is not None :
                        o.active_profile = o.save
                    
                    if o.active_profile==None: 
                        if self.ini.has('profile') : o.active_profile = self.ini.get('profile')
                        else : o.active_profile = 'default'
                    
                    if o.load : 
                        self.print_header()
                        self.load_profile(o)

                    elif o.view :
                        self.print_header()
                        if o.view == 'all' :
                            sections = self.ini.getSections()
                            if len(sections) > 0:
                                Clz.print(' '+','.join(sections), Clz.fgB3)
                            else : Clz.print(' no profiles', Clz.fgB1)
                        else: self.ini.print(o.view)

                    elif o.save :
                        self.print_header()
                        if not o.set_host and not o.set_user and not o.set_pass and not o.set_port and not o.set_boxname and not o.set_name and not o.gen_key:
                            parser.error(' no options specified')
                        else :
                            if o.set_port and not util.represents_int(o.set_port):
                                parser.error(' port must be a number')
                                self.exit(1)
                            else :
                                if o.set_boxname: self.ini.set('box' , o.set_boxname,o.active_profile+'.imap')
                                if o.set_host: self.ini.set('host', o.set_host,o.active_profile+'.imap')
                                if o.set_user: self.ini.set('user', o.set_user,o.active_profile+'.imap')
                                if o.set_pass: self.ini.set('pass', o.set_pass,o.active_profile+'.imap')
                                if o.set_port: self.ini.set('port', o.set_port,o.active_profile+'.imap')                    
                                if o.set_name: self.ini.set('name', o.set_name,o.active_profile+'.infos')
                                if o.gen_key:
                                    kg = crypt.KeyGen(256)
                                    self.ini.set('key' ,kg.key,o.active_profile+'.keys')
                                    self.ini.set('mark',kg.mark,o.active_profile+'.keys')
                                    self.ini.set('salt','-¤-ImpraStorage-¤-',o.active_profile+'.keys')
                                if self.check_profile(o.active_profile):
                                    self.ini.set('profile', o.active_profile)
                                self.ini.write()                                
                                self.ini.print(o.active_profile)
                elif o.check :
                    self.print_header()
                    self.check_profile(o.check, True)

                else :
                    self.print_usage('')
            
            elif a[0] == 'help':
                core.clear()
                parser.print_help()

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ data CMD ~~
            elif a[0] == 'list' or a[0] == 'add' or a[0] == 'get' or a[0] == 'remove' or a[0] == 'search' :

                o.active_profile = self.ini.get('profile')
                    
                    
                if self.check_profile(o.active_profile):
                    core.clear()
                    self.print_header()
                    conf  = core.ImpraConf(self.ini,o.active_profile)
                    impst = None
                    try:                        
                        impst = core.ImpraStorage(conf, False, self.wkpath)
                    except crypt.BadKeyException as e :
                        print()
                        Clz.print(' it seems that your current profile `'                    , Clz.fgB1, False)
                        Clz.print(o.active_profile                                           , Clz.fgB3, False)
                        Clz.print('` has a wrong key to decrypt index on server.'            , Clz.fgB1)
                        Clz.print(' you can remove index but all presents files on the box `', Clz.fgB1, False)
                        Clz.print(conf.get('box','imap')                                     , Clz.fgB3, False)
                        Clz.print('` will be unrecoverable\n'                                , Clz.fgB1, True, False)

                        remIndex = input(' remove index ? (yes/no) ')
                        if remIndex.lower()=='yes':
                            Clz.print(' ',Clz.OFF)
                            impst = core.ImpraStorage(conf, True, self.wkpath)
                            
                        else : 
                            print()
                            print(' bye')
                            print()
                            self.exit(1)


                    if a[0]=='list':

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
                            
                            matchIdsCatg = None                            
                            matchIdsUser = None
                            matchIds     = None
                            if o.category is not None :
                                print(o.category)
                                matchIdsCatg = impst.index.getByCategory(o.category)
                            if o.user is not None :
                                matchIdsUser = impst.index.getByUser(o.user)
                            
                            if o.category is not None :                                
                                if o.user is not None :
                                    matchIds = impst.index.getIntersection(matchIdsCatg,matchIdsUser)
                                else : matchIds = matchIdsCatg
                            
                            elif o.user is not None :
                                matchIds = matchIdsUser                            
                            
                            order = o.order
                            if o.order_inv is not None:
                                order = '-'+o.order_inv
                            impst.index.print(order,matchIds)


                    elif a[0] == 'add':
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need at least one argument',parser)
                        else:
                            vfile = a[1]
                            if util.file_exists(vfile) :
                                if not len(a)>2 :
                                    label, ext  = core.splitext(core.basename(vfile))
                                else: label = a[2]
                                if o.category is None : o.category = ''
                                done = impst.addFile(vfile,label,o.category)
                                if done :
                                    print('\n ',end='')
                                    Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                    print()
                                
                            else : self.error_cmd('`'+a[1]+' is not a file',parser)


                    elif a[0] == 'get':
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need one argument',parser)
                        else:
                            vid = a[1]
                            ids = []
                            for sid in vid.split(',') :
                                seq = sid.split('-')
                                if len(seq)==2 : ids.extend(range(int(seq[0]),int(seq[1])+1))
                                else: ids.append(sid)
                            for sid in ids :                                
                                key = impst.index.getById(str(sid))
                                if key !=None : 
                                    done = impst.getFile(key)
                                    if done :
                                        print('\n ',end='')
                                        Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                        print()
                                else: 
                                    print('\n ',end='')
                                    Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                    Clz.print(str(sid)                 , Clz.bg1+Clz.fgB3, False)
                                    Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                    print()


                    elif a[0] == 'search':

                        uid     = conf.get('uid' ,'index')
                        date    = conf.get('date','index')
                        account = conf.get('user','imap')
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need one argument',parser)
                        else : 

                            vsearch = a[1]
                            
                            matchIds = impst.index.getByPattern(vsearch)
                            core.clear()
                            if matchIds is not None:
                                printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
                                printHeaderTitle(APP_TITLE)
                                printHeaderPart('account',account)
                                printHeaderPart('index',uid)
                                printHeaderPart('box',impst.rootBox)
                                Clz.print(date, Clz.fgB7, True, True)
                                printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
                                Clz.print(' searching --'   , Clz.fgB3, False)
                                Clz.print(' `'+vsearch+'`' , Clz.fgB7, False)
                                Clz.print(' -- found '      , Clz.fgB3, False)
                                Clz.print(str(len(matchIds)), Clz.fgB1, False)
                                Clz.print(' results --'     , Clz.fgB3)
                                printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
                                
                                matchIdsCatg = None                            
                                matchIdsUser = None
                                matchIdsCrit = None
                                if o.category is not None :
                                    print(o.category)
                                    matchIdsCatg = impst.index.getByCategory(o.category)
                                if o.user is not None :
                                    matchIdsUser = impst.index.getByUser(o.user)
                                
                                if o.category is not None :                                
                                    if o.user is not None :
                                        matchIdsCrit = impst.index.getIntersection(matchIdsCatg,matchIdsUser)
                                    else : matchIdsCrit = matchIdsCatg
                                
                                elif o.user is not None :
                                    matchIdsCrit = matchIdsUser      
                                
                                if matchIdsCrit is not None :
                                    matchIds = impst.index.getIntersection(matchIds,matchIdsCrit)
                                
                                order = o.order
                                if o.order_inv is not None:
                                    order = '-'+o.order_inv
                                impst.index.print(o.order,matchIds)
                            else:
                                print('\n ',end='')
                                Clz.print(' == no match found for pattern `', Clz.bg3+Clz.fgB4, False)
                                Clz.print(vsearch                           , Clz.bg3+Clz.fgB1, False)
                                Clz.print('` == '                           , Clz.bg3+Clz.fgB4)
                                print()

                    elif a[0] == 'remove':
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need one argument',parser)                        
                        else :

                            if not util.represents_int(a[1]):
                                print('\n ',end='')
                                Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                print()
                                self.exit(1)
                            else : 
                                vid = a[1]
                                key = impst.index.getById(vid)
                                if key !=None : 
                                    done = impst.removeFile(key)
                                    if done :
                                        print('\n ',end='')
                                        Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                        print()
                                else: 
                                    print('\n ',end='')
                                    Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                    Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                    Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                    print()

            else : 
                self.error_cmd('unknow command `'+a[0]+'`',parser)
        print()
    
    
    def error_cmd(self,msg, parser):
        core.clear()
        self.print_usage('')
        Clz.print('error : '+msg,Clz.fgB7)
        self.exit(1)

    def parserError(self, msg):
        core.clear()
        self.print_usage('')
        Clz.print('error : '+msg,Clz.fgB7)
        self.exit(1)

    def exit(self, code):
        if Clz.isUnix : sys.exit(code)

    def check_profile(self,profile, activeCheck=False):
        """"""
        c = self.ini.hasSection(profile+'.keys') and self.ini.has('host',profile+'.imap') and self.ini.has('user',profile+'.imap') and self.ini.has('pass',profile+'.imap') and self.ini.has('port',profile+'.imap')
        if activeCheck :
            if c :
                Clz.print(' '+profile+' is ok', Clz.fgB2)
                Clz.print(' testing...', Clz.fgB3)
                conf  = core.ImpraConf(self.ini,profile)
                impst = None
                try:                        
                    impst = core.ImpraStorage(conf, False, self.wkpath)
                    Clz.print(' done...', Clz.fgB2)
                except crypt.BadKeyException as e :
                    pass
            else :
                Clz.print(' '+profile+' incomplete', Clz.fgB1)
                Clz.print(' need :', Clz.fgB1)
                if not self.ini.hasSection(profile+'.keys'):
                    Clz.print('    key (conf -S "'+profile+'" -K)', Clz.fgB1)
                if not self.ini.has('host',profile+'.imap'):
                    Clz.print('    imap host (conf -S "'+profile+'" -H hostName)', Clz.fgB1)
                if not self.ini.has('user',profile+'.imap'):
                    Clz.print('    imap user (conf -S "'+profile+'" -U userName)', Clz.fgB1)
                if not self.ini.has('pass',profile+'.imap'):
                    Clz.print('    imap password (conf -S "'+profile+'" -X password)', Clz.fgB1)
                if not self.ini.has('port',profile+'.imap'):
                    Clz.print('    imap port (conf -S "'+profile+'" -P port)', Clz.fgB1)
            if not self.ini.has('name',profile+'.infos'):
                if c :
                    Clz.print(' think to add your userName :',Clz.bgB3)
                Clz.print('    userName (conf -S "'+profile+'" -N yourName)', Clz.fgB3)    
        return c 

    def print_header(self):
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        printHeaderTitle(APP_TITLE)
        printHeaderPart('version',APP_VERSION)
        printHeaderPart('author',APP_AUTHOR)
        printHeaderPart('license',APP_LICENSE)
        printHeaderPart('copyright','2012 '+APP_COPY)        
        Clz.print(' ', Clz.OFF)
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        print()

    def print_version(self, data):
        self.print_header()

    def print_usage(self, data, withoutHeader=False):
        if not withoutHeader : self.print_header()
  
        Clz.print('  USAGE :\n', Clz.fgB3)
        Clz.print('    imprastorage ', Clz.fgb7, False)
        if Clz.isUnix:
            Clz.print('--help ', Clz.fgB3)
        else:
            Clz.print('help ', Clz.fgB3)
                
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('filePath', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('name', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('category', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(']', Clz.fgB3)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('get ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('id|ids', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('list ', Clz.fgB3, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('category', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -u ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -o', Clz.fgB3, False)
        Clz.print('|', Clz.fgB1, False)
        Clz.print('-O ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('colon', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(']', Clz.fgB3)
        
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('remove ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('id', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)
        
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('pattern', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('category', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -u ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -o', Clz.fgB3, False)
        Clz.print('|', Clz.fgB1, False)
        Clz.print('-O ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('colon', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(']', Clz.fgB3)
        
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('conf', Clz.fgB3, False)        
        Clz.print(' -L', Clz.fgB3, False)
        Clz.print('|', Clz.fgB1, False)
        Clz.print('-V ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('profile', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('conf', Clz.fgB3, False)        
        Clz.print(' -S ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('profile', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print(' -K', Clz.fgB3, False)
        Clz.print(', -H ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('host', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(', -U ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(', -X ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('password', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(', -P ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('port', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(', -B ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('box', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(', -N ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('name', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' ]', Clz.fgB3)
    
    def print_options(self):
        print('\n')
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('  MAIN OPTIONS :\n'                              , Clz.fgB3)        
        Clz.print(' '*4+'-h, --help'                                , Clz.fgB3)
        Clz.print(' '*50+'display help message'                     , Clz.fgB7)
        Clz.print(' '*4+'-q, --quiet'                               , Clz.fgB3)
        Clz.print(' '*50+'don\'t print status messages to stdout'   , Clz.fgB7)
        Clz.print(' '*4+'-d, --debug'                               , Clz.fgB3)
        Clz.print(' '*50+'set debug mode'                           , Clz.fgB7)
        print('\n')
        
        Clz.print('  COMMANDS OPTIONS :\n'                          , Clz.fgB3)
        Clz.print(' '*4+'-c '                                       , Clz.fgB3, False)
        Clz.print('CATEGORY'.ljust(10,' ')                          , Clz.fgB1, False)
        Clz.print(', --category     '.ljust(18,' ')                 , Clz.fgB3, False)
        Clz.print('CATEGORY'.ljust(10,' ')                          , Clz.fgB1)
        Clz.print(' '*50+'set a category'                           , Clz.fgB7)
        
        Clz.print(' '*4+'-u '                                       , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --user'.ljust(18,' ')                          , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set a user'                               , Clz.fgB7)
        
        Clz.print(' '*4+'-o '                                       , Clz.fgB3, False)
        Clz.print('COLON'.ljust(10,' ')                             , Clz.fgB1, False)
        Clz.print(', --order'.ljust(18,' ')                         , Clz.fgB3, False)
        Clz.print('COLON'.ljust(10,' ')                             , Clz.fgB1)
        Clz.print(' '*50+'order by specified colon'                 , Clz.fgB7)
        
        Clz.print(' '*4+'-O '                                       , Clz.fgB3, False)
        Clz.print('COLON'.ljust(10,' ')                             , Clz.fgB1, False)
        Clz.print(', --order-rev'.ljust(18,' ')                     , Clz.fgB3, False)
        Clz.print('COLON'.ljust(10,' ')                             , Clz.fgB1)
        Clz.print(' '*50+'reverse order by specified colon'         , Clz.fgB7)
        
        print('\n')
        Clz.print('  CONF OPTIONS :\n', Clz.fgB3)        
        Clz.print(' '*4+'-L '                                       , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --load'.ljust(18,' ')                          , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'load the specified profile'               , Clz.fgB7)
        
        Clz.print(' '*4+'-V '                                       , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --view'.ljust(18,' ')                          , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'view the specified profile (or * for all available)'  , Clz.fgB7)
        
        Clz.print(' '*4+'-S '                                       , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --order'.ljust(18,' ')                         , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'save the specified profile'               , Clz.fgB7)

        print('\n')
        Clz.print('  CONF -S OPTIONS :\n', Clz.fgB3)   
        Clz.print(' '*4+'-N '                                       , Clz.fgB3, False)
        Clz.print('NAME'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --set-name'.ljust(18,' ')                      , Clz.fgB3, False)
        Clz.print('NAME'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set imprastorage username'                , Clz.fgB7)
        
        Clz.print(' '*4+'-K '                                       , Clz.fgB3, False)
        Clz.print(''.ljust(10,' ')                                  , Clz.fgB1, False)
        Clz.print(', --gen-key'.ljust(18,' ')                       , Clz.fgB3, False)
        Clz.print(''.ljust(10,' ')                                  , Clz.fgB1)
        Clz.print(' '*50+'generate a new key'                       , Clz.fgB7)
        
        Clz.print(' '*4+'-H '                                       , Clz.fgB3, False)
        Clz.print('HOST'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --set-host'.ljust(18,' ')                      , Clz.fgB3, False)
        Clz.print('HOST'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set imap host'                            , Clz.fgB7)
        
        Clz.print(' '*4+'-U '                                       , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --set-user'.ljust(18,' ')                      , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set imap user'                            , Clz.fgB7)
        
        Clz.print(' '*4+'-X '                                       , Clz.fgB3, False)
        Clz.print('PASSWORD'.ljust(10,' ')                          , Clz.fgB1, False)
        Clz.print(', --set-password'.ljust(18,' ')                  , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set imap password'                        , Clz.fgB7)
        
        Clz.print(' '*4+'-P '                                       , Clz.fgB3, False)
        Clz.print('PORT'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --set-port'.ljust(18,' ')                      , Clz.fgB3, False)
        Clz.print('PORT'.ljust(10,' ')                              , Clz.fgB1)
        Clz.print(' '*50+'set imap port'                            , Clz.fgB7)
        
        Clz.print(' '*4+'-B '                                       , Clz.fgB3, False)
        Clz.print('BOXNAME'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --set-box'.ljust(18,' ')                       , Clz.fgB3, False)
        Clz.print('BOXNAME'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'set imap boxname (default:__impra__)'     , Clz.fgB7)
        
        print('\n')    


    def print_help(self):
        """"""
        self.print_header()
        Clz.print(APP_DESC, Clz.fgN1)
        self.print_usage('',True)
        self.print_options()
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        print()
        Clz.print('  EXEMPLES :\n', Clz.fgB3)
        
        
        Clz.print(' '*4+'command add :', Clz.fgB3)
        
        Clz.print(' '*8+'# add (upload) a file',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print('/home/Share/2009-mountains.avi', Clz.fgB1)
        
        Clz.print(' '*8+'# add a file with a label (label will be the filename on downloading)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print('/home/Share/2009-mountains.avi \'summer 2009 - in mountains\'', Clz.fgB1)
        
        Clz.print(' '*8+'# add a file on a category (category will be the dir structure on downloading)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print('/home/Share/2009-mountains.avi', Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('videos/perso/2009', Clz.fgB1)
        
        Clz.print(' '*8+'# add a file with a label on a category',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print('/home/Share/2009-mountains.avi \'summer 2009 - in mountains\'', Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('videos/perso/2009', Clz.fgB1)

        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command get :', Clz.fgB3)
        
        Clz.print(' '*8+'# get file with id 15',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('get ', Clz.fgB3, False)
        Clz.print('15', Clz.fgB1)
        
        Clz.print(' '*8+'# get files with id 15,16,17,18,19',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('get ', Clz.fgB3, False)
        Clz.print('15-19', Clz.fgB1)
        
        Clz.print(' '*8+'# get files with id 22,29,30',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('get ', Clz.fgB3, False)
        Clz.print('22,29,30', Clz.fgB1)
        
        Clz.print(' '*8+'# get files with id 22,29,30,31,32,33,34,35,48',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('get ', Clz.fgB3, False)
        Clz.print('22,29-35,48', Clz.fgB1)

        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command list :', Clz.fgB3)

        Clz.print(' '*8+'# list all files',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('list', Clz.fgB3)
                
        Clz.print(' '*8+'# list all files (sorted by LABEL)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('list', Clz.fgB3, False)
        Clz.print(' -o ' , Clz.fgB3, False)
        Clz.print('LABEL', Clz.fgB1)
        
        Clz.print(' '*8+'# list all files on category `videos/perso` ',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('list', Clz.fgB3, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1)

        Clz.print(' '*8+'# list all files sent by `bob`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('list', Clz.fgB3, False)
        Clz.print(' -u ' , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1)

        Clz.print(' '*8+'# list all files sent by `bob` on category `videos/perso` (reverse sorted by SIZE)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('list', Clz.fgB3, False)
        Clz.print(' -O ' , Clz.fgB3, False)
        Clz.print('SIZE', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1, False)
        Clz.print(' -u ' , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1)        

        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command remove :', Clz.fgB3)
        
        Clz.print(' '*8+'# remove file with id 15 (removing command only take a single id)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('remove ', Clz.fgB3, False)
        Clz.print('15', Clz.fgB1)
        
        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command search :', Clz.fgB3)
        
        Clz.print(' '*8+'# search all files wich contains `mountains`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('mountains', Clz.fgB1)
        
        Clz.print(' '*8+'# search all files wich contains `old mountain` on category `videos/perso`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'old mountain\'', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1)
        
        Clz.print(' '*8+'# search all files wich contains `old mountain` sent by user `bob`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'old mountain\'', Clz.fgB1, False)
        Clz.print(' -u ' , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1)
        
        Clz.print(' '*8+'# search all files wich contains `old mountain` (reverse sorted by SIZE)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'old mountain\'', Clz.fgB1, False)
        Clz.print(' -O ' , Clz.fgB3, False)
        Clz.print('SIZE', Clz.fgB1)

        Clz.print(' '*8+'# search all files wich contains `old mountain` sent by user `bob` and on category `videos/perso` (reverse',Clz.fgn7)
        Clz.print(' '*8+'# sorted by LABEL)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'old mountain\'', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1, False)        
        Clz.print(' -u '  , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1, False)
        Clz.print(' -O '  , Clz.fgB3, False)
        Clz.print('LABEL' , Clz.fgB1)
        
        Clz.print(' '*8+'# search all files starting by `old mountain`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'^old mountain\'', Clz.fgB1)

        Clz.print(' '*8+'# search all files ending by `old mountain`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print('\'old mountain$\'', Clz.fgB1)
        
        
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command conf :', Clz.fgB3)

        Clz.print(' '*8+'# this command is tipycally a profile creation (or rewrite if profile exists)',Clz.fgn7)
        Clz.print(' '*8+'# set a userName, generate a new Key and set imap account with  host,port,user,password for profile bobgmail',Clz.fgn7)
        Clz.print(' '*8+'# then set it as current profile',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1, False)
        Clz.print('-N ', Clz.fgB3, False)
        Clz.print('bob ', Clz.fgB1, False)        
        Clz.print('-K -H ', Clz.fgB3, False)
        Clz.print('imap.gmail.com ', Clz.fgB1, False)
        Clz.print('-P ', Clz.fgB3, False)
        Clz.print('993 ', Clz.fgB1, False)
        Clz.print('-U ', Clz.fgB3, False)
        Clz.print('bob22 ', Clz.fgB1, False)
        Clz.print('-X ', Clz.fgB3, False)
        Clz.print('mypassword ', Clz.fgB1)
        
        Clz.print(' '*8+'# load config profile bobimap and set it as current profile',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-L ', Clz.fgB3, False)
        Clz.print('bobimap ', Clz.fgB1)

        Clz.print(' '*8+'# view config current profile',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-V', Clz.fgB3)

        Clz.print(' '*8+'# view config profile bobgmail (current profile doesn\'t change)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-V ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1)
        
        Clz.print(' '*8+'# generate a new Key for current profile (carreful with this command if your account has no empty index - ',Clz.fgn7)
        Clz.print(' '*8+'# all files will be unrecoverable without the appropriate key)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S -K', Clz.fgB3)
        
        Clz.print(' '*8+'# generate a new Key for profile bobgmail and set it as current profile (carreful with this command ',Clz.fgn7)
        Clz.print(' '*8+'# if your account has no empty index - all files will be unrecoverable without the appropriate key)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1, False)
        Clz.print('-K', Clz.fgB3)

        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        print()


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
