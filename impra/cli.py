#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/cli.py
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
# ~~ module cli ~~

from    optparse        import OptionGroup
from    psr.sys         import Sys, Io, Const, init
from    psr.log         import Log
from    psr.cli         import AbstractCli
import  impra.conf      as conf
from    impra.cliapp    import CliApp


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Cli ~~

class Cli(AbstractCli):

    def __init__(self, path, remote=False, rwargs=None, thread=None, loglvl=Const.LOG_ALL):
        """"""
        AbstractCli.__init__(self, conf, self)

        Cli.HOME   = conf.DEFVAL_USER_PATH
        Cli.DIRKEY = Cli.HOME+'.'+conf.PRG_NAME.lower()+Sys.sep
        if not Sys.isUnix() :
            Cli.CHQ    = '"'
            Cli.HOME   = 'C:'+Sys.sep+conf.PRG_NAME.lower()+Sys.sep
            Cli.DIRKEY = self.HOME+'keys'+Sys.sep
        Sys.mkdir_p(Cli.DIRKEY)

        gpData = OptionGroup(self.parser, '')
        gpData = OptionGroup(self.parser, '')
        gpConf = OptionGroup(self.parser, '')
        
        gpData.add_option('-c', '--category'      , action='store',       metavar='CATG            ')
        gpData.add_option('-u', '--user'          , action='store',       metavar='OWNER           ')
        gpData.add_option('-l', '--label'         , action='store',       metavar='LABEL           ')
        gpData.add_option('-o', '--order'         , action='store',       metavar='ORDER           '  , default='ID')
        gpData.add_option('-O', '--order-inv'     , action='store',       metavar='ORDER_INVERSE   ')
        gpData.add_option('-a', '--account'       , action='store',       metavar='ACCOUNT         ')
        self.parser.add_option_group(gpData)        

        gpConf.add_option('-V', '--view'          , action='store'                                  )
        gpConf.add_option('-L', '--load'          , action='store'                                  )
        gpConf.add_option('-S', '--save'          , action='store'                                  )
        gpConf.add_option('-C', '--check'         , action='store'                                  )
        gpConf.add_option('-H', '--set-host'      , action='store',       metavar='HOST            ')
        gpConf.add_option('-U', '--set-user'      , action='store',       metavar='USER            ')
        gpConf.add_option('-X', '--set-pass'      , action='store',       metavar='PASS            ')
        gpConf.add_option('-P', '--set-port'      , action='store',       metavar='PORT            ')
        gpConf.add_option('-N', '--set-name'      , action='store',       metavar='NAME            ')
        gpConf.add_option('-M', '--set-multi'     , action='store',       metavar='PROFILE         ')
        gpConf.add_option('-R', '--remove-multi'  , action='store',       metavar='PROFILE         ')
        gpConf.add_option('-B', '--set-boxname'   , action='store',       metavar='BOXNAME         ')
        gpConf.add_option('-K', '--gen-key'       , action='store_true',  default=False)
        self.parser.add_option_group(gpConf)

        # rewrite argv sended by remote
        if rwargs is not None :
            import sys
            sys.argv = rwargs

        (o, a) = self.parser.parse_args()

        Sys.g.QUIET      = o.quiet
        Sys.g.THREAD_CLI = thread
        Sys.g.GUI        = thread is not None

        init(conf.PRG_NAME, o.debug, remote, not o.no_color, loglvl)
        Const.LINE_SEP_LEN = 120

        if not a:
            try :
                if not o.help or not o.version:
                    self.parser.error_cmd(('no command specified',), True)
                else :
                    Sys.clear()
                    Cli.print_help()
            except :
                if not o.version :
                    self.parser.error_cmd(('no command specified',), True)
                else :
                    Cli.print_header()

        else:
            if a[0] == 'help':
                Sys.clear()
                Cli.print_help()

            elif a[0] in ['add','conf','import','info', 'edit','export','get','list','remove','search'] :
                app = CliApp(self.HOME, path, self.parser, Cli, a, o)

                if a[0]=='add':
                    app.onCommandAdd()
                elif a[0]=='conf':
                    app.onCommandConf()
                elif a[0]=='info':
                    app.onCommandInfo()
                elif a[0]=='import':
                    app.onCommandImport()
                elif a[0]=='edit':
                    app.onCommandEdit()
                elif a[0]=='export':
                    app.onCommandExport()
                elif a[0]=='get':
                    app.onCommandGet()
                elif a[0]=='list':
                    app.onCommandList()
                elif a[0]=='remove':
                    app.onCommandRemove()
                elif a[0]=='search':
                    app.onCommandSearch()
                    
                Sys.dprint('PUT END SIGNAL')
                if Sys.g.LOG_QUEUE is not None :
                    Sys.g.LOG_QUEUE.put(Sys.g.SIGNAL_STOP)

            else :
                self.parser.error_cmd((('unknow command ',(a[0],Sys.Clz.fgb3)),), True)

        if not o.quiet : Sys.dprint()


    @staticmethod
    def print_usage(data, withoutHeader=False):
        """"""
        if not withoutHeader : Cli.print_header()

        Sys.echo('  USAGE :\n'                    , Sys.CLZ_HELP_CMD)
        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('help '                          , Sys.CLZ_HELP_CMD)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('add'.ljust(10,' ')              , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('filePath'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' ['                              , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('name'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('category'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                              , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('edit'.ljust(10,' ')             , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('id'                             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' [ -l '                          , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('label'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('category'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                              , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('get'.ljust(10,' ')              , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('id|ids'                         , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('list'.ljust(10,' ')             , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('[ -c '                          , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('category'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('user'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('|'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('-O '                            , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('colon'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -a '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('account'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                              , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('remove'.ljust(10,' ')           , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('id'                             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('info'.ljust(10,' ')             , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('id'                             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('search'.ljust(10,' ')           , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('pattern'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' [ -c '                          , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('category'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('user'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('|'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('-O '                            , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('colon'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                              , Sys.CLZ_HELP_ARG)
        
        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('export'.ljust(10,' ')           , Sys.CLZ_HELP_CMD)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('import'.ljust(10,' ')           , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('filePath'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('conf'.ljust(10,' ')             , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('-L'                             , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('|'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('-V'                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('|'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('-C '                            , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('profile'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG  , False)
        Sys.echo('conf'.ljust(10,' ')             , Sys.CLZ_HELP_CMD  , False)
        Sys.echo('-S '                            , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('profile'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' [ -K -H '                       , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('host'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -U '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('user'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -X '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('password'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -P '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('port'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -B '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('box'                            , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -N '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('name'                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' \\'                            , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*45                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -M '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('profile'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -R '                           , Sys.CLZ_HELP_ARG  , False)
        Sys.echo('{'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('profile'                        , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' ]'                             , Sys.CLZ_HELP_ARG)        


    @staticmethod
    def print_options():
        """"""
        Sys.dprint('\n')
        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)

        Sys.echo('  MAIN OPTIONS :\n'                                       , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-h'.ljust(13,' ')+', --help'                        , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'display help'                                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-q'.ljust(13,' ')+', --quiet'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'don\'t print status messages to stdout'            , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-v'.ljust(13,' ')+', --version'                     , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'display programm version'                          , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-d'.ljust(13,' ')+', --debug'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable debug mode'                                 , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-f'.ljust(13,' ')+', --force'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'force rewriting existing files without alert'      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+' '.ljust(13,' ')+', --no-color'                     , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'disable color mode'                                , Sys.CLZ_HELP_ARG_INFO)


        Sys.dprint('\n')
        Sys.echo('  COMMANDS OPTIONS:\n'                                    , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-c '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('CATEGORY'.ljust(10,' ')                                   , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --category'.ljust(18,' ')                               , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LENGTH'.ljust(10,' ')                                     , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set a category'                                    , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('USER'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --user'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('USER'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set a user'                                        , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-l '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LABEL'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --label'.ljust(18,' ')                                  , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LABEL'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set a label (edit mode only)'                      , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COLON'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --order'.ljust(18,' ')                                  , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COLON'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'order by specified colon'                          , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-O '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COLON'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --order-rev'.ljust(18,' ')                              , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COLON'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'reverse order by specified colon'                  , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-a '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('ACCOUNT'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --account'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('ACCOUNT'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set an profile account'                            , Sys.CLZ_HELP_ARG_INFO) 
        
        Sys.dprint('\n')
        Sys.echo('  CONF OPTIONS:\n'                                        , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-L '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --load'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'load the specified profile'                        , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-V '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --view'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'view the specified profile (or \'all\' for view availables)', Sys.CLZ_HELP_ARG_INFO)        
        
        Sys.echo(' '*4+'-C '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --check'.ljust(18,' ')                                  , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'check the specified profile'                       , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-S '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --save'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'save the specified profile'                        , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  CONF -S OPTIONS:\n'                                     , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-N '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('NAME'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-name'.ljust(18,' ')                               , Sys.CLZ_HELP_ARG, False)
        Sys.echo('NAME'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imprastorage username'                         , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-K '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo(''.ljust(10,' ')                                           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --gen-key'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo(''.ljust(10,' ')                                           , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'generate a new key'                                , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-H '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('HOST'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-host'.ljust(18,' ')                               , Sys.CLZ_HELP_ARG, False)
        Sys.echo('HOST'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imap host'                                     , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-U '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('USER'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-user'.ljust(18,' ')                               , Sys.CLZ_HELP_ARG, False)
        Sys.echo('USER'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imap user'                                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-X '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PASSWORD'.ljust(10,' ')                                   , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-password'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PASSWORD'.ljust(10,' ')                                   , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imap password'                                 , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-P '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PORT'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-port'.ljust(18,' ')                               , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PORT'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imap port'                                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-B '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('BOXNAME'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-box'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('BOXNAME'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'set imap boxname (default:__impra2__)'             , Sys.CLZ_HELP_ARG_INFO)
        
        Sys.echo(' '*4+'-P '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --set-multi'.ljust(18,' ')                              , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'add imap multi account'                            , Sys.CLZ_HELP_ARG_INFO)

        Sys.echo(' '*4+'-R '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --remove-multi'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.echo('PROFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'remove imap multi account'                         , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')


    @staticmethod
    def print_help():
        """"""
        Cli.print_header()
        Sys.echo(Cli.conf.PRG_DESC, Sys.CLZ_HELP_DESC)
        Cli.print_usage('',True)
        Cli.print_options()
        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.dprint()
        Sys.echo('  EXEMPLES :\n', Sys.CLZ_HELP_CMD)
        CHQ  = "'"

        Sys.echo(' '*4+'command add :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# add (upload) a file', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('add ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'Share'+Sys.sep+'2009-mountains.avi', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# add a file with a label (label will be the filename on downloading)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('add ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'Share'+Sys.sep+'2009-mountains.avi', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c ', Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso/2009', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# add a file with a label on a category', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('add ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'Share'+Sys.sep+'2009-mountains.avi '+CHQ+'summer 2009 - in mountains'+CHQ, Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c ', Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso/2009', Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command edit :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# edit label on file with id 15', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('edit '                    , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -l '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('newname'                  , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# edit category on file with id 15', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('edit '                    , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('new/category'             , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# edit label and category on file with id 15', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('edit '                    , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('new/category'             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -l '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo(CHQ+'my newName'+CHQ       , Sys.CLZ_HELP_PARAM)


        
        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command get :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# get file with id 15', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('get '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# get files with id 15,16,17,18,19', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('get '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15-19'                    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# get files with id 22,29,30', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('get '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('22,29,30'                 , Sys.CLZ_HELP_PARAM)
        
        Sys.echo(' '*8+'# get files with id 22,29,30,31,32,33,34,35,48', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('get '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('22,29-35,48'              , Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command list :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# list all files'   , Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list '                    , Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# list all files (sorted by LABEL)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -o '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LABEL'                    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# list all files on category `videos/perso` ', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso'             , Sys.CLZ_HELP_PARAM)
        
        Sys.echo(' '*8+'# list all files sent by `Imran`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -u '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM)
        
        Sys.echo(' '*8+'# list all files sent by `Imran` on category `videos/perso` (reverse sorted by SIZE)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -O '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('SIZE'                     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso'             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# list all files sent by `Imran` on category `videos/perso` (reverse sorted by SIZE) and account imran22', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('list'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -O '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('SIZE'                     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso'             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -a '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imran22'                  , Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command remove :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# remove file with id 15 (removing command only take a single id)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('remove '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command info :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# get info about file with id 15', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('info '                    , Sys.CLZ_HELP_CMD, False)
        Sys.echo('15'                       , Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command search :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# search all files wich contains `mountains`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo('mountains'                , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files wich contains `old mountain` on category `videos/perso`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'old mountain'+CHQ     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso'             , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files wich contains `old mountain` sent by user `Imran`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'old mountain'+CHQ     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files wich contains `old mountain` (reverse sorted by SIZE)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'old mountain'+CHQ     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -O '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('SIZE'                     , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files wich contains `old mountain` sent by user `Imran` and on category `videos/perso` (reverse', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# sorted by LABEL)' , Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'old mountain'+CHQ     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -c '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('videos/perso'             , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -u '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -O '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LABEL'                    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files starting by `old mountain`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'^old mountain'+CHQ    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files starting by `old mountain`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'^old mountain'+CHQ    , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# search all files ending by `old mountain`', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('search '                  , Sys.CLZ_HELP_CMD, False)
        Sys.echo(CHQ+'old mountain$'+CHQ    , Sys.CLZ_HELP_PARAM)
        


        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command export :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# export the current index (as an encrypt file)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('export '                  , Sys.CLZ_HELP_CMD)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command import :', Sys.CLZ_HELP_CMD)
        
        Sys.echo(' '*8+'# import an index (build by export command)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# carreful with this command, current index will be unrecoverable', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('import '                   , Sys.CLZ_HELP_CMD, False)
        Sys.echo('20121010222244_gmail.index', Sys.CLZ_HELP_PARAM)



        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command conf :', Sys.CLZ_HELP_CMD)
        
        Sys.echo(' '*8+'# this command is tipycally a profile creation (or rewrite if profile exists)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# set a userName, generate a new Key and set imap account with  host,port,user,password for profile imrangmail', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# then set it as current profile', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -S '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imrangmail'               , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -N '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('Imran'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -K -H '                  , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imap.gmail.com'           , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -P '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('993'                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -U '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imran22'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -X '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imranpassword'            , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# check config profile imranimap (current profile doesn\'t change)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -C '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imranimap'                , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# load config profile imranimap and set it as current profile', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -L '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imranimap'                , Sys.CLZ_HELP_PARAM)
        
        Sys.echo(' '*8+'# list all config profile', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -V '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('all'                      , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# view config profile imrangmail (current profile doesn\'t change)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf '                    , Sys.CLZ_HELP_CMD, False)
        Sys.echo('-V '                      , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imrangmail'               , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# generate a new Key for profile imrangmail and set it as current profile (carreful with this command ', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# if your account has no empty index - all files will be unrecoverable without the appropriate key)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -S '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imrangmail'               , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -K '                     , Sys.CLZ_HELP_ARG)
        
        Sys.echo(' '*8+'# add multi account to profile imrangmail (accounts must be on same host)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -S '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imrangmail'               , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -M '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imranimap'                , Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# remove multi account to profile imrangmail', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('conf'                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo(' -S '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imrangmail'               , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -R '                     , Sys.CLZ_HELP_ARG, False)
        Sys.echo('imranimap'                , Sys.CLZ_HELP_PARAM)

        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.dprint()
