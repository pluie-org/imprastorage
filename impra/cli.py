#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.8                                                             #
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
from   impra.util  import Clz, mprint
from   time        import strftime

LINE_SEP_LEN  = 120
LINE_SEP_CHAR = '―'
if not Clz.isUnix : LINE_SEP_CHAR = '-'
APP_TITLE     = 'ImpraStorage'
APP_VERSION   = '0.8'
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
        parser.add_option('-q', '--quiet'         , help='don\'t print status messages to stdout'                      , action='store_true', default=False)
        parser.add_option('-d', '--debug'         , help='set debug mode'                                              , action='store_true' , default=False)
        parser.add_option('--no-color'            , help='disable color mode'                                          , action='store_true' , default=False)
        
        gpData.add_option('-c', '--category'      , help='set specified CATEGORY (crit. for opt. -l,-a or -s)'         , action='store',       metavar='CATG            ')
        gpData.add_option('-u', '--user'          , help='set specified USER (crit. for opt. -l,-a or -s)'             , action='store',       metavar='OWNER           ')
        gpData.add_option('-l', '--label'         , help='set specified LABEL (edit mode only)'                        , action='store',       metavar='LABEL           ')
        gpData.add_option('-o', '--order'         , help='set colon ORDER (crit. for opt. -l and -s)'                  , action='store',       metavar='ORDER           '  , default='ID')
        gpData.add_option('-O', '--order-inv'     , help='set colon ORDER_INVERSE (crit. for opt. -l and -s)'          , action='store',       metavar='ORDER_INVERSE   ')
        #gpData.add_option('-o', '--output-dir'    , help='set specified OUTPUT DIR (for opt. -l,-a,-d or -g)'          , action='store',       metavar='DIR        ')
        parser.add_option_group(gpData)                                                                             

        gpConf.add_option('-V', '--view'          , help='view configuration'                                          , action='store'                                  )
        gpConf.add_option('-L', '--load'          , help='load configuration'                                          , action='store'                                  )
        gpConf.add_option('-S', '--save'          , help='save configuration'                                          , action='store'                                  )
        gpConf.add_option('-C', '--check'         , help='check configuration'                                         , action='store'                                  )
        gpConf.add_option('-H', '--set-host'      , help='set imap host server'                                        , action='store',       metavar='HOST            ')
        gpConf.add_option('-U', '--set-user'      , help='set imap user login'                                         , action='store',       metavar='USER            ')
        gpConf.add_option('-X', '--set-pass'      , help='set imap user password'                                      , action='store',       metavar='PASS            ')
        gpConf.add_option('-P', '--set-port'      , help='set imap port'                                               , action='store',       metavar='PORT            ')
        gpConf.add_option('-N', '--set-name'      , help='set user name'                                               , action='store',       metavar='NAME            ')
        gpConf.add_option('-M', '--set-multi'     , help='set multi account'                                           , action='store',       metavar='ACCOUNT PASSWORD', nargs=2)
        gpConf.add_option('-R', '--remove-multi'  , help='remove multi account'                                        , action='store',       metavar='ACCOUNT         ')
        gpConf.add_option('-B', '--set-boxname'   , help='set boxName on imap server (default:[%default])'             , action='store',       metavar='BOXNAME         ')
        gpConf.add_option('-K', '--gen-key'       , help='generate new key'                                            , action='store_true',  default=False)

        parser.add_option_group(gpConf)

        (o, a) = parser.parse_args()
        
        if o.no_color :
            util.Clz.active = False
        
        if o.quiet :
            util.DEBUG.active = False
        else:
            util.DEBUG.active = True
            if o.debug :            
                util.DEBUG.level  = util.DEBUG.ALL
            else : 
                util.DEBUG.level  = util.DEBUG.INFO
        
        mprint()
        if not a:

            try :
                if not o.help : 
                    self.parserError(' no commando specified')
                else :
                    if util.DEBUG.active : core.clear()
                    parser.print_help()
            except :
                self.parserError(' no commando specified')

        else:

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ conf CMD ~~
            if a[0] == 'conf' :
                if util.DEBUG.active : core.clear()
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
                                ap  = self.ini.get('profile')
                                sep = ''
                                for p in sections:
                                    if p == ap : 
                                        colr = Clz.fgB1
                                        p = '*'+p
                                    else : colr = Clz.fgB3                                        
                                    Clz.print(sep+p, colr, False)
                                    if sep=='':sep=','
                                mprint()
                            else : Clz.print(' no profiles', Clz.fgB1)
                        else: self.ini.print(o.view)

                    elif o.save :
                        self.print_header()
                        if not o.set_host and not o.set_user and not o.set_pass and not o.set_port and not o.set_boxname and not o.set_name and not o.gen_key and not o.set_multi and not o.remove_multi:
                            parser.error(' no options specified')
                        else :
                            if o.set_port and not util.represents_int(o.set_port):
                                parser.error(' port must be a number')
                                self.exit(1)
                            else :
                                if o.set_boxname: self.ini.set('box'  , o.set_boxname,o.active_profile+'.imap')
                                if o.set_host   : self.ini.set('host' , o.set_host,o.active_profile+'.imap')
                                if o.set_user   : self.ini.set('user' , o.set_user,o.active_profile+'.imap')
                                if o.set_pass   : self.ini.set('pass' , o.set_pass,o.active_profile+'.imap')
                                if o.set_port   : self.ini.set('port' , o.set_port,o.active_profile+'.imap')                    
                                if o.set_name   : self.ini.set('name' , o.set_name,o.active_profile+'.infos')
                                
                                m = self.ini.get('multi',o.active_profile+'.imap')
                                if m is None : m = {}
                                else: m = eval(m)
                                if o.set_multi  : m[o.set_multi[0]] = o.set_multi[1]                                    
                                elif o.remove_multi and m is not None and o.remove_multi in m : m.pop(o.remove_multi,None)                                
                                self.ini.set('multi', core.jdumps(m),o.active_profile+'.imap')
                                
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
                if util.DEBUG.active : core.clear()
                parser.print_help()

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ~~ data CMD ~~
            elif not self.ini.isEmpty() and (a[0] == 'list' or a[0] == 'add' or a[0] == 'get' or a[0] == 'remove' or a[0] == 'search' or a[0] == 'edit' or a[0] == 'export' or a[0] == 'import'):

                o.active_profile = self.ini.get('profile')
                    
                    
                if self.check_profile(o.active_profile):
                    if util.DEBUG.active : core.clear()
                    if util.DEBUG.active: self.print_header()
                    conf  = core.ImpraConf(self.ini,o.active_profile)
                    impst = None
                    try:                        
                        impst = core.ImpraStorage(conf, False, self.wkpath)
                    except crypt.BadKeyException as e :
                        mprint()
                        Clz.print(' it seems that your current profile `'                    , Clz.fgB1, False)
                        Clz.print(o.active_profile                                           , Clz.fgB3, False)
                        Clz.print('` (account:`'                                             , Clz.fgB1, False)
                        Clz.print(conf.get('user','imap')                                    , Clz.fgB3, False)
                        Clz.print('`) has a wrong key to decrypt index on server.'           , Clz.fgB1)
                        Clz.print(' you can remove index but all presents files`'            , Clz.fgB1, False)
                        Clz.print('` will be unrecoverable\n'                                , Clz.fgB1, True, False)
                        
                        resp = input(' backup index ? (yes/no) ')
                        if resp.lower()=='yes':
                            encData = util.get_file_content(core.dirname(conf.ini.path)+core.sep+'.index')
                            ipath   = core.dirname(conf.ini.path)+core.sep+strftime('%Y%m%d%H%M%S')+'-'+o.active_profile+'.index'
                            with open(ipath, mode='w', encoding='utf-8') as o:
                                o.write(encData)
                            Clz.print('\nindex backup in `',Clz.fgn7, False)
                            Clz.print(ipath,Clz.fgB3, False)
                            Clz.print('`',Clz.fgn7)                            
                            Clz.print('\n',Clz.fgB1, True, False)
                        resp = input(' remove index ? (yes/no) ')
                        if resp.lower()=='yes':
                            impst = core.ImpraStorage(conf, True, self.wkpath)
                            mprint()
                            mprint(' bye')
                            Clz.print(' ',Clz.OFF)
                            mprint()
                            self.exit(1)
                            
                        else : 
                            mprint()
                            mprint(' bye')
                            Clz.print(' ',Clz.OFF)
                            mprint()
                            self.exit(1)


                    if a[0]=='export':
                        if not impst.irefresh: impst.getIndex(True)
                        encData  = impst.index.encrypt()
                        ipath   = core.dirname(conf.ini.path)+core.sep+strftime('%Y%m%d%H%M%S')+'_'+o.active_profile+'.index'
                        with open(ipath, mode='w', encoding='utf-8') as o:
                            o.write(encData)
                        mprint()
                        Clz.print(' index saved as ', Clz.fgn7)
                        Clz.print(' '+ipath, Clz.fgB2)
                        mprint()

                    if a[0]=='import':
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need one argument',parser)
                        else :
                            vfile = a[1]
                            if util.file_exists(vfile) :
                                encData = util.get_file_content(vfile)
                                try :
                                    impst.importIndex(encData)
                                    impst.saveIndex()
                                    mprint('\n ',end='')
                                    Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                    mprint()
                                except crypt.BadKeyException as e:
                                    mprint()
                                    Clz.print(' Error : BadKeyException', Clz.fgB1)
                                    Clz.print(' Your profile key don\'t match the index', Clz.fgB1)
                                    mprint()
                            else :
                                mprint()
                                Clz.print(' file not found', Clz.fgB1)
                                mprint()
                
                    elif a[0]=='list':

                        uid     = conf.get('uid' ,'index')
                        date    = conf.get('date','index')
                        account = conf.get('user','imap')
                        if impst.index != None:
                            noData = impst.index.isEmpty()
                            if uid  == None or noData : uid  = 'EMPTY'
                            if date == None or noData : date = ''
                            if util.DEBUG.active : core.clear()
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
                                mprint(o.category)
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
                            if not util.file_exists(vfile) :
                                if os.path.isdir(vfile):
                                    for f in os.listdir(vfile):
                                        if not os.path.isdir(f):
                                            label, ext  = core.splitext(core.basename(f))
                                            if o.category is None : o.category = ''
                                            done = impst.addFile(vfile+core.sep+f,label,o.category)
                                            if done :
                                                mprint('\n ',end='')
                                                Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                                mprint()
                                else : self.error_cmd('`'+a[1]+' is not a file or dir',parser)
                            else:
                                if not len(a)>2 :
                                    label, ext  = core.splitext(core.basename(vfile))
                                else: label = a[2]
                                if o.category is None : o.category = ''
                                done = impst.addFile(vfile,label,o.category)
                                if done :
                                    mprint('\n ',end='')
                                    Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                    mprint()
                            

                    elif a[0] == 'edit':
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need an id',parser)
                        else:
                            if not util.represents_int(a[1]):
                                mprint('\n ',end='')
                                Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                mprint()
                                self.exit(1)
                            else : 
                                vid = a[1]
                                key = impst.index.getById(vid)
                                if key !=None : 
                                    done = impst.editFile(key,o.label,o.category)
                                    if done :
                                        impst.saveIndex()
                                        mprint('\n ',end='')
                                        Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                        mprint()
                                    else :
                                        mprint('\n ',end='')
                                        Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                        Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                        Clz.print('` has not been modified == ', Clz.bg1+Clz.fgB7)
                                        mprint()                                        
                                else: 
                                    mprint('\n ',end='')
                                    Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                    Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                    Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                    mprint()

                    elif a[0] == 'get':
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need an id',parser)
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
                                        mprint('\n ',end='')
                                        Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                        mprint()
                                else: 
                                    mprint('\n ',end='')
                                    Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                    Clz.print(str(sid)                 , Clz.bg1+Clz.fgB3, False)
                                    Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                    mprint()


                    elif a[0] == 'search':

                        uid     = conf.get('uid' ,'index')
                        date    = conf.get('date','index')
                        account = conf.get('user','imap')
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need one argument',parser)
                        else : 

                            vsearch = a[1]
                            
                            matchIds = impst.index.getByPattern(vsearch)
                            if util.DEBUG.active : core.clear()
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
                                    mprint(o.category)
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
                                mprint('\n ',end='')
                                Clz.print(' == no match found for pattern `', Clz.bg3+Clz.fgB4, False)
                                Clz.print(vsearch                           , Clz.bg3+Clz.fgB1, False)
                                Clz.print('` == '                           , Clz.bg3+Clz.fgB4)
                                mprint()

                    elif a[0] == 'remove':
                        
                        if not len(a)>1 : self.error_cmd('`'+a[0]+' need an id',parser)                        
                        else :

                            if not util.represents_int(a[1]):
                                mprint('\n ',end='')
                                Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                mprint()
                                self.exit(1)
                            else : 
                                vid = a[1]
                                key = impst.index.getById(vid)
                                if key !=None : 
                                    done = impst.removeFile(key)
                                    if done :
                                        mprint('\n ',end='')
                                        Clz.print(' == OK == ', Clz.bg2+Clz.fgb7)
                                        mprint()
                                else: 
                                    mprint('\n ',end='')
                                    Clz.print(' == `'                  , Clz.bg1+Clz.fgB7, False)
                                    Clz.print(a[1]                     , Clz.bg1+Clz.fgB3, False)
                                    Clz.print('` is not a valid id == ', Clz.bg1+Clz.fgB7)
                                    mprint()
                else :
                    self.check_profile(o.active_profile, True)

            else :
                if self.ini.isEmpty() :
                    Clz.print(' '*4+'ImpraStorage has no configuration file !!', Clz.fgB1)
                    mprint()
                    Clz.print(' '*8+'# to create the config file you must use this command with appropriate values :',Clz.fgn7)
                    Clz.print(' '*8+'# type command help for details',Clz.fgn7)
                    Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
                    Clz.print('conf ', Clz.fgB3, False)
                    Clz.print('-S ', Clz.fgB3, False)
                    Clz.print('profileName ', Clz.fgB1, False)
                    Clz.print('-N ', Clz.fgB3, False)
                    Clz.print('yourName ', Clz.fgB1, False)        
                    Clz.print('-K -H ', Clz.fgB3, False)
                    Clz.print('your.host.net ', Clz.fgB1, False)
                    Clz.print('-P ', Clz.fgB3, False)
                    Clz.print('993 ', Clz.fgB1, False)
                    Clz.print('-U ', Clz.fgB3, False)
                    Clz.print('accountName ', Clz.fgB1, False)
                    Clz.print('-X ', Clz.fgB3, False)
                    Clz.print('accountPassword ', Clz.fgB1)
                else :
                    self.error_cmd('unknow command `'+a[0]+'`',parser)
        mprint()
    
    
    def error_cmd(self,msg, parser):
        if util.DEBUG.active : core.clear()
        self.print_usage('')
        Clz.print('error : '+msg,Clz.fgB7)
        self.exit(1)

    def parserError(self, msg):
        if util.DEBUG.active : core.clear()
        self.print_usage('')
        Clz.print('error : '+msg,Clz.fgB7)
        self.exit(1)

    def exit(self, code):
        if Clz.isUnix : sys.exit(code)

    def check_profile(self,profile, activeCheck=False):
        """"""
        c = self.ini.hasSection(profile+'.keys') and self.ini.has('host',profile+'.imap') and self.ini.has('user',profile+'.imap') and self.ini.has('pass',profile+'.imap') and self.ini.has('port',profile+'.imap') and self.ini.has('name',profile+'.infos')
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
                Clz.print(' profile `'              , Clz.fgB1, False)
                Clz.print(profile                   , Clz.fgB3, False)
                Clz.print('` is incomplete\n need :', Clz.fgB1)
                if not self.ini.hasSection(profile+'.keys'):
                    Clz.print(' '*4+'key'.ljust(18,' ')+' (conf -S "'+profile+'" -K)', Clz.fgB3)
                if not self.ini.has('host',profile+'.imap'):
                    Clz.print(' '*4+'imap host'.ljust(18,' ')+' (conf -S "'+profile+'" -H hostName)', Clz.fgB3)
                if not self.ini.has('user',profile+'.imap'):
                    Clz.print(' '*4+'imap user'.ljust(18,' ')+' (conf -S "'+profile+'" -U accountName)', Clz.fgB3)
                if not self.ini.has('pass',profile+'.imap'):
                    Clz.print(' '*4+'imap password'.ljust(18,' ')+' (conf -S "'+profile+'" -X password)', Clz.fgB3)
                if not self.ini.has('port',profile+'.imap'):
                    Clz.print(' '*4+'imap port'.ljust(18,' ')+' (conf -S "'+profile+'" -P port)', Clz.fgB3)
            if not self.ini.has('name',profile+'.infos'):
                if c :
                    Clz.print(' think to add your userName :',Clz.bgB3)
                Clz.print(' '*4+'userName'.ljust(18,' ')+' (conf -S "'+profile+'" -N yourName)', Clz.fgB3)    
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
        mprint()

    def print_version(self, data):
        self.print_header()

    def print_usage(self, data, withoutHeader=False):
        if not withoutHeader : self.print_header()
  
        Clz.print('  USAGE :\n', Clz.fgB3)
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('help ', Clz.fgB3)
                
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('add '.ljust(8,' '), Clz.fgB3, False)
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
        Clz.print('edit '.ljust(8,' '), Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('id', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print(' -l ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('label', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('category', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(']', Clz.fgB3)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('get '.ljust(8,' '), Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('id|ids', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('list '.ljust(8,' '), Clz.fgB3, False)
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
        Clz.print('remove '.ljust(8,' '), Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('id', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)
        
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('search '.ljust(8,' '), Clz.fgB3, False)
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
        Clz.print('export '.ljust(8,' '), Clz.fgB3)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('import '.ljust(8,' '), Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('filePath', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1)
        
        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('conf '.ljust(8,' '), Clz.fgB3, False)        
        Clz.print('-L', Clz.fgB3, False)
        Clz.print('|', Clz.fgB1, False)
        Clz.print('-V', Clz.fgB3, False)
        Clz.print('|', Clz.fgB1, False)
        Clz.print('-C ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('profile', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1)

        Clz.print('    imprastorage ', Clz.fgb7, False)
        Clz.print('conf '.ljust(8,' '), Clz.fgB3, False)        
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('profile', Clz.fgB1, False)
        Clz.print('} ', Clz.fgB1, False)
        Clz.print('[', Clz.fgB3, False)
        Clz.print(' -K', Clz.fgB3, False)
        Clz.print(' -H ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('host', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -U ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -X ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('password', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -P ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('port', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -B ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('box', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -N ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('name', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' \\', Clz.fgB3)
        
        Clz.print(' '*40, Clz.fgb7, False)
        Clz.print('-M ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('} {', Clz.fgB1, False)
        Clz.print('pass', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' -R ', Clz.fgB3, False)
        Clz.print('{', Clz.fgB1, False)
        Clz.print('user', Clz.fgB1, False)
        Clz.print('}', Clz.fgB1, False)
        Clz.print(' ]', Clz.fgB3)
    
    def print_options(self):
        mprint('\n')
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('  MAIN OPTIONS :\n'                              , Clz.fgB3)        
        Clz.print(' '*4+'-h, --help'                                , Clz.fgB3)
        Clz.print(' '*50+'display help message'                     , Clz.fgB7)
        Clz.print(' '*4+'-q, --quiet'                               , Clz.fgB3)
        Clz.print(' '*50+'don\'t print status messages to stdout'   , Clz.fgB7)
        Clz.print(' '*4+'-d, --debug'                               , Clz.fgB3)
        Clz.print(' '*50+'set debug mode'                           , Clz.fgB7)
        Clz.print(' '*4+'    --no-color'                            , Clz.fgB3)
        Clz.print(' '*50+'disable color mode'                       , Clz.fgB7)
        mprint('\n')
        
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

        Clz.print(' '*4+'-l '                                       , Clz.fgB3, False)
        Clz.print('LABEL'.ljust(10,' ')                             , Clz.fgB1, False)
        Clz.print(', --label'.ljust(18,' ')                         , Clz.fgB3, False)
        Clz.print('LABEL'.ljust(10,' ')                             , Clz.fgB1)
        Clz.print(' '*50+'set a label (edit mode only)'             , Clz.fgB7)
        
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
        
        mprint('\n')
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
        Clz.print(' '*50+'view the specified profile (or \'all\' for view availables)'  , Clz.fgB7)

        Clz.print(' '*4+'-C '                                       , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --check'.ljust(18,' ')                         , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'check the specified profile'              , Clz.fgB7)
        
        Clz.print(' '*4+'-S '                                       , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1, False)
        Clz.print(', --save'.ljust(18,' ')                          , Clz.fgB3, False)
        Clz.print('PROFILE'.ljust(10,' ')                           , Clz.fgB1)
        Clz.print(' '*50+'save the specified profile'               , Clz.fgB7)

        mprint('\n')
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
        
        Clz.print(' '*4+'-M '                                       , Clz.fgB3, False)
        Clz.print('USER PASS'.ljust(10,' ')                         , Clz.fgB1, False)
        Clz.print(', --set-multi'.ljust(18,' ')                     , Clz.fgB3, False)
        Clz.print('USER PASS'.ljust(10,' ')                         , Clz.fgB1)        
        Clz.print(' '*50+'add imap multi account'                   , Clz.fgB7)

        Clz.print(' '*4+'-R '                                       , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1, False)
        Clz.print(', --remove-multi'.ljust(18,' ')                  , Clz.fgB3, False)
        Clz.print('USER'.ljust(10,' ')                              , Clz.fgB1)        
        Clz.print(' '*50+'remove imap multi account'                , Clz.fgB7)
        
        mprint('\n')    


    def print_help(self):
        """"""
        self.print_header()
        Clz.print(APP_DESC, Clz.fgN1)
        self.print_usage('',True)
        self.print_options()
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        mprint()
        Clz.print('  EXEMPLES :\n', Clz.fgB3)
        CHQ  = "'"
        sep = core.sep
        HOME = sep+'home'+sep
        if not Clz.isUnix :
            CHQ  = '"'
            HOME = 'C:'+sep
        
        Clz.print(' '*4+'command add :', Clz.fgB3)
        
        Clz.print(' '*8+'# add (upload) a file',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print(HOME+'Share'+sep+'2009-mountains.avi', Clz.fgB1)
        
        Clz.print(' '*8+'# add a file with a label (label will be the filename on downloading)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print(HOME+'Share'+sep+'2009-mountains.avi '+CHQ+'summer 2009 - in mountains'+CHQ, Clz.fgB1)
        
        Clz.print(' '*8+'# add a file on a category (category will be the dir structure on downloading)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print(HOME+'Share'+sep+'2009-mountains.avi', Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('videos/perso/2009', Clz.fgB1)
        
        Clz.print(' '*8+'# add a file with a label on a category',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('add ', Clz.fgB3, False)
        Clz.print(HOME+'Share'+sep+'2009-mountains.avi '+CHQ+'summer 2009 - in mountains'+CHQ, Clz.fgB1, False)
        Clz.print(' -c ', Clz.fgB3, False)
        Clz.print('videos/perso/2009', Clz.fgB1)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command edit :', Clz.fgB3)
        
        Clz.print(' '*8+'# edit label on file with id 15',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('edit ', Clz.fgB3, False)
        Clz.print('15', Clz.fgB1, False)
        Clz.print(' -l ' , Clz.fgB3, False)
        Clz.print('newName', Clz.fgB1)

        Clz.print(' '*8+'# edit category on file with id 15',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('edit ', Clz.fgB3, False)
        Clz.print('15', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('new/category', Clz.fgB1)

        Clz.print(' '*8+'# edit label and category on file with id 15',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('edit ', Clz.fgB3, False)
        Clz.print('15', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('new/category', Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print(CHQ+'my newName'+CHQ, Clz.fgB1)
        
        
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
        Clz.print(CHQ+'old mountain'+CHQ, Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1)
        
        Clz.print(' '*8+'# search all files wich contains `old mountain` sent by user `bob`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print(CHQ+'old mountain'+CHQ, Clz.fgB1, False)
        Clz.print(' -u ' , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1)
        
        Clz.print(' '*8+'# search all files wich contains `old mountain` (reverse sorted by SIZE)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print(CHQ+'old mountain'+CHQ, Clz.fgB1, False)
        Clz.print(' -O ' , Clz.fgB3, False)
        Clz.print('SIZE', Clz.fgB1)

        Clz.print(' '*8+'# search all files wich contains `old mountain` sent by user `bob` and on category `videos/perso` (reverse',Clz.fgn7)
        Clz.print(' '*8+'# sorted by LABEL)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print(CHQ+'old mountain'+CHQ, Clz.fgB1, False)
        Clz.print(' -c ' , Clz.fgB3, False)
        Clz.print('videos/perso', Clz.fgB1, False)        
        Clz.print(' -u '  , Clz.fgB3, False)
        Clz.print('bob', Clz.fgB1, False)
        Clz.print(' -O '  , Clz.fgB3, False)
        Clz.print('LABEL' , Clz.fgB1)
        
        Clz.print(' '*8+'# search all files starting by `old mountain`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print(CHQ+'^old mountain'+CHQ, Clz.fgB1)

        Clz.print(' '*8+'# search all files ending by `old mountain`',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('search ', Clz.fgB3, False)
        Clz.print(CHQ+'old mountain$'+CHQ, Clz.fgB1)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command export :', Clz.fgB3)        

        Clz.print(' '*8+'# export the current index (as an encrypt file)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('export ', Clz.fgB3)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Clz.print('\n'+' '*4+'command import :', Clz.fgB3)        

        Clz.print(' '*8+'# import an index (build by export command)',Clz.fgn7)
        Clz.print(' '*8+'# carreful with this command, current index will be unrecoverable',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('import ', Clz.fgB3, False)
        Clz.print(' 20121010222244_gmail.index', Clz.fgB1)
        
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

        Clz.print(' '*8+'# check config profile bobimap (current profile doesn\'t change)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-C ', Clz.fgB3, False)
        Clz.print('bobimap ', Clz.fgB1)
        
        Clz.print(' '*8+'# load config profile bobimap and set it as current profile',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-L ', Clz.fgB3, False)
        Clz.print('bobimap ', Clz.fgB1)

        Clz.print(' '*8+'# list all config profile',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-V ', Clz.fgB3, False)
        Clz.print('all ', Clz.fgB1)

        Clz.print(' '*8+'# view config profile bobgmail (current profile doesn\'t change)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-V ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1)
        
        Clz.print(' '*8+'# generate a new Key for profile bobgmail and set it as current profile (carreful with this command ',Clz.fgn7)
        Clz.print(' '*8+'# if your account has no empty index - all files will be unrecoverable without the appropriate key)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1, False)
        Clz.print('-K ', Clz.fgB3)
        
        Clz.print(' '*8+'# add multi account to profile bobgmail (accounts must be on same host)',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1, False)
        Clz.print('-M ', Clz.fgB3, False)
        Clz.print('bob23 passbob23', Clz.fgB1)
        
        Clz.print(' '*8+'# remove multi account to profile bobgmail',Clz.fgn7)
        Clz.print(' '*8+'imprastorage ', Clz.fgB7, False)
        Clz.print('conf ', Clz.fgB3, False)
        Clz.print('-S ', Clz.fgB3, False)
        Clz.print('bobgmail ', Clz.fgB1, False)
        Clz.print('-R ', Clz.fgB3, False)
        Clz.print('bob23', Clz.fgB1)

        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        mprint()


    def load_profile(self,o):
        """"""        
        if self.check_profile(o.active_profile):
            mprint('',end=' ')
            Clz.print(' == profile `', Clz.bg2+Clz.fgb7, False)
            Clz.print(o.active_profile, Clz.bg2+Clz.fgB3, False)
            Clz.print('` loaded == ', Clz.bg2+Clz.fgb7)
            mprint()
            self.ini.set('profile', o.active_profile)
            self.ini.write()
        else :
            self.check_profile(o.active_profile, True)
