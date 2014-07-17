#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  kirmah/cli.py
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  software  : Kirmah    <http://kirmah.sourceforge.net/>
#  version   : 2.18
#  date      : 2014
#  licence   : GPLv3.0   <http://www.gnu.org/licenses/>
#  author    : a-Sansara <[a-sansara]at[clochardprod]dot[net]>
#  copyright : pluie.org <http://www.pluie.org/>
#
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  This file is part of Kirmah.
#
#  Kirmah is free software (free as in speech) : you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  Kirmah is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Kirmah.  If not, see <http://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module cli ~~

from    optparse        import OptionGroup
from    psr.sys         import Sys, Io, Const, init
from    psr.log         import Log
from    psr.cli         import AbstractCli
from    kirmah.cliapp   import CliApp
import  kirmah.conf     as conf


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Cli ~~

class Cli(AbstractCli):

    def __init__(self, path, remote=False, rwargs=None, thread=None, loglvl=Const.LOG_DEFAULT):
        """"""
        AbstractCli.__init__(self, conf, self)


        Cli.HOME   = conf.DEFVAL_USER_PATH
        Cli.DIRKEY = Cli.HOME+'.'+conf.PRG_NAME.lower()+Sys.sep
        if not Sys.isUnix() :
            CHQ     = '"'
            self.HOME   = 'C:'+Sys.sep+conf.PRG_NAME.lower()+Sys.sep
            self.DIRKEY = self.HOME+'keys'+Sys.sep
        Sys.mkdir_p(Cli.DIRKEY)

        gpData = OptionGroup(self.parser, '')
        gpData.add_option('-a', '--fullcompress'  , action='store_true' )
        gpData.add_option('-z', '--compress'      , action='store_true' )
        gpData.add_option('-Z', '--nocompress'    , action='store_true' )
        gpData.add_option('-r', '--random'        , action='store_true' )
        gpData.add_option('-R', '--norandom'      , action='store_true' )
        gpData.add_option('-m', '--mix'           , action='store_true' )
        gpData.add_option('-M', '--nomix'         , action='store_true' )
        gpData.add_option('-j', '--multiprocess'  , action='store')
        gpData.add_option('-k', '--keyfile'       , action='store')
        gpData.add_option('-l', '--length'        , action='store', default=1024)
        gpData.add_option('-p', '--parts'         , action='store', default=22)
        gpData.add_option('-o', '--outputfile'    , action='store')
        self.parser.add_option_group(gpData)

        # rewrite argv sended by remote
        if rwargs is not None :
            import sys
            sys.argv = rwargs

        (o, a) = self.parser.parse_args()

        Sys.g.QUIET      = o.quiet
        Sys.g.THREAD_CLI = thread
        Sys.g.GUI        = thread is not None

        init(conf.PRG_NAME, o.debug, remote, not o.no_color, loglvl)


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

            elif a[0] in ['key','enc','dec','split','merge'] :

                app = CliApp(self.HOME, path, self, a, o)

                if a[0]=='key'  :
                    app.onCommandKey()
                else :
                    if not len(a)>1   :
                        self.parser.error_cmd((('an ',('inputFile',Sys.Clz.fgb3),' is required !'),), True)
                    elif not Io.file_exists(a[1]):
                        self.parser.error_cmd((('the file ',(a[1], Sys.Clz.fgb3), ' doesn\'t exists !'),), True)

                    elif a[0]=='enc'  : app.onCommandEnc()
                    elif a[0]=='dec'  : app.onCommandDec()
                    elif a[0]=='split': app.onCommandSplit()
                    elif a[0]=='merge': app.onCommandMerge()

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

        Sys.echo('  USAGE :\n'                , Sys.CLZ_HELP_CMD)
        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('help '                      , Sys.CLZ_HELP_CMD)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('key   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('[ -l '                      , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('length'                     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                          , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+Cli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('enc   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.echo(' -z|Z|a -r|R -m|M -j '      , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('numProcess'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                          , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('dec   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.echo(' -j '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('numProcess'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                          , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('split '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.echo(' -p '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('numParts'                   , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('tarOutputFile'              , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                          , Sys.CLZ_HELP_ARG)

        Sys.echo('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('merge '                     , Sys.CLZ_HELP_CMD, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.echo(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                          , Sys.CLZ_HELP_ARG)


    @staticmethod
    def print_options():
        """"""
        Sys.dprint('\n')
        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)

        Sys.echo('  MAIN OPTIONS :\n'                                       , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-v'.ljust(13,' ')+', --version'                     , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'display programm version'                          , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-d'.ljust(13,' ')+', --debug'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable debug mode'                                 , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-f'.ljust(13,' ')+', --force'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'force rewriting existing files without alert'      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-q'.ljust(13,' ')+', --quiet'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'don\'t print status messages to stdout'            , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-h'.ljust(13,' ')+', --help'                        , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'display help'                                      , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  KEY OPTIONS :\n'                                        , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-l '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LENGTH'.ljust(10,' ')                                     , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --length'.ljust(18,' ')                                 , Sys.CLZ_HELP_ARG, False)
        Sys.echo('LENGTH'.ljust(10,' ')                                     , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified key length (128 to 4096 - default:1024)' , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified key output filename'                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  ENCRYPT OPTIONS :\n'                                    , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-a'.ljust(13,' ')+', --fullcompress'                , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable full compression mode'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-z'.ljust(13,' ')+', --compress'                    , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable compression mode'                           , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-Z'.ljust(13,' ')+', --nocompress'                  , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'disable compression mode'                          , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-r'.ljust(13,' ')+', --random'                      , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable random mode'                                , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-R'.ljust(13,' ')+', --norandom'                    , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'disable random mode'                               , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-m'.ljust(13,' ')+', --mix'                         , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'enable mix mode'                                   , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-M'.ljust(13,' ')+', --nomix'                       , Sys.CLZ_HELP_ARG)
        Sys.echo(' '*50+'disable mix mode'                                  , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-j '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --multiprocess'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'number of process for encryption (2 to 8)'         , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'key filename used to encrypt'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified encrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  DECRYPT OPTIONS :\n'                                    , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-j '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --multiprocess'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'number of process for decryption (2 to 8)'         , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'key filename used to decrypt'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified decrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  SPLIT OPTIONS :\n'                                      , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-p '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --part'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'count part to split'                               , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'key filename used to split'                        , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('TARFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('TARFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified tar output filename'                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.echo('  MERGE OPTIONS :\n'                                      , Sys.CLZ_HELP_CMD)
        Sys.echo(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'key filename used to merge'                        , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'specified decrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

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

        Sys.echo(' '*4+'command key :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# generate a new crypted key of 2048 length', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('key -l ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('2048 ', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# generate a new crypted key (default length is 1024) in a specified location', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('key -o ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM)


        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command encrypt :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# encrypt specified file with default crypted key and default options', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'mySecretTextFile.txt', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# encrypt specified file with specified crypted key (full compression, no random but mix mode)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+'# on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('mySecretTextFile.txt', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -aRm -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo(Cli.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('test.kmh', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# encrypt specified file with default crypted key (no compression but random & mix mode and multiprocessing)', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('myBigTextFile.txt', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -Zrm -j ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('4', Sys.CLZ_HELP_PARAM)


        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command decrypt :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# decrypt specified file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'mySecretFile.kmh', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# decrypt specified file with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+Cli.conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('myEncryptedSecretFile.kmh', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo(Cli.HOME+'.kirmah'+Sys.sep+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('myDecryptedSecretFile.txt', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# decrypt specified file with default crypted key and multiprocessing', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('myEncryptedSecretFile.kmh', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -j ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('4'    , Sys.CLZ_HELP_PARAM)


        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command split :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# split specified file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('split ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'myBigBinaryFile.avi', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# split specified file on 55 parts with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('split ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('myBigBinaryFile.avi', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -p ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('55'   , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo(Cli.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('myBigBinaryFile.encrypted', Sys.CLZ_HELP_PARAM)


        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.echo('\n'+' '*4+'command merge :', Sys.CLZ_HELP_CMD)

        Sys.echo(' '*8+'# merge specified splitted file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('merge ', Sys.CLZ_HELP_CMD, False)
        Sys.echo(Cli.HOME+'6136bd1b53d84ecbad5380594eea7256176c19e0266c723ea2e982f8ca49922b.kcf', Sys.CLZ_HELP_PARAM)

        Sys.echo(' '*8+'# merge specified tark splitted file with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.echo('merge ', Sys.CLZ_HELP_CMD, False)
        Sys.echo('myBigBinaryFile.encrypted.tark', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo(Cli.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.echo('myBigBinaryFile.decrypted.avi', Sys.CLZ_HELP_PARAM)

        Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.dprint()
