#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/cli.py
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

from    optparse        import OptionParser, OptionGroup
from    psr.sys         import Sys, Io, Const, init
from    psr.log         import Log

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class TinyParser ~~

class TinyParser(OptionParser):


    def format_description(self, formatter):
        """"""
        return self.description


    def format_epilog(self, formatter):
        """"""
        return self.epilog


    def error(self, errMsg, errData=None):
        """"""
        self.print_usage('')
        self.error_cmd((errMsg,))



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class AbstractConf ~~

class YourConf():

    PRG_NAME     = 'your-program'
    PRG_VERS     = '1.0'
    PRG_AUTHOR   = 'you'
    PRG_LICENSE  = 'GNU GPL v3'
    PRG_COPY     = 'company'
    PRG_CLI_NAME = 'your-cli-program'
    PRG_DESC     = 'your desc'

# you must provide a global conf object

prgconf = YourConf()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class AbstractCli ~~

class AbstractCli():

    conf = YourConf()

    def __init__(self, prgconf=None, *args, **kwargs):
        """"""
        if not Sys.isUnix : Const.LINE_SEP_CHAR = '-'
        AbstractCli.conf        = prgconf
        self.CHQ                = "'"
        self.parser             = TinyParser()
        self.parser.print_help  = self.print_help
        self.parser.print_usage = self.print_usage
        self.parser.error_cmd   = self.error_cmd

        self.parser.add_option('-v', '--version'  , action='store_true', default=False)
        self.parser.add_option('-d', '--debug'    , action='store_true', default=False)
        self.parser.add_option('-f', '--force'    , action='store_true', default=False)
        self.parser.add_option('-q', '--quiet'    , action='store_true', default=False)

        self.parser.add_option('--no-color'       , action='store_true' , default=False)
        

    def error_cmd(self, data, pusage=False):
        """"""
        if pusage : self.print_usage('')
        Sys.dprint()
        Sys.pwarn(data, True)
        AbstractCli.exit(1)

    @staticmethod
    def exit(code):
        """"""
        if Sys.isUnix() : Sys.exit(code)


    @staticmethod
    def print_header():
        """"""
        a = AbstractCli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        b = AbstractCli.printHeaderTitle(AbstractCli.conf.PRG_CLI_NAME)
        c = AbstractCli.printHeaderPart('version'  ,AbstractCli.conf.PRG_VERS)
        d = AbstractCli.printHeaderPart('author'   ,AbstractCli.conf.PRG_AUTHOR)
        e = AbstractCli.printHeaderPart('license'  ,AbstractCli.conf.PRG_LICENSE)
        f = AbstractCli.printHeaderPart('copyright',AbstractCli.conf.PRG_COPY)
        Sys.echo(' ', Sys.Clz.OFF)
        AbstractCli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.wlog(a)
        Sys.wlog(b + c + d + e + f )
        Sys.wlog(a)
        #~ Sys.wlog(Sys.dprint())


    @staticmethod
    def printLineSep(sep,lenSep):
        """"""
        s = sep*lenSep
        Sys.echo(s, Sys.CLZ_HEAD_LINE)
        return [(s, Const.CLZ_HEAD_SEP)]


    @staticmethod
    def printHeaderTitle(title):
        """"""
        s = ' == '+title+' == '
        Sys.echo(s, Sys.CLZ_HEAD_APP, False, True)
        return [(s, Const.CLZ_HEAD_APP)]


    @staticmethod
    def printHeaderPart(label,value):
        """"""
        a, b, c = ' [',':' ,'] '
        Sys.echo(a    , Sys.CLZ_HEAD_SEP, False)
        Sys.echo(label, Sys.CLZ_HEAD_KEY, False)
        Sys.echo(b    , Sys.CLZ_HEAD_SEP, False)
        Sys.echo(value, Sys.CLZ_HEAD_VAL, False)
        Sys.echo(c    , Sys.CLZ_HEAD_SEP, False)
        return [(a,Const.CLZ_HEAD_SEP),(label,Const.CLZ_HEAD_KEY),(b,Const.CLZ_HEAD_SEP),(value,Const.CLZ_HEAD_VAL),(c,Const.CLZ_HEAD_SEP)]


    @staticmethod
    def print_version(data):
        """"""
        AbstractCli.print_header()


    @staticmethod
    def print_options():
        """"""
        Sys.dprint('\n')
        AbstractCli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)

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
        Sys.echo(' '*4+'-a '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('VALUE'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --bind_opt_a'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('VALUE'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'description option a'                              , Sys.CLZ_HELP_ARG_INFO)
        Sys.echo(' '*4+'-b '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.echo('VALUE'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(', --bind_opt_b'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.echo('VALUE'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.echo(' '*50+'description option b'                              , Sys.CLZ_HELP_ARG_INFO)



    def print_usage(self, data, withoutHeader=False):
        """"""
        if not withoutHeader : AbstractCli.print_header()

        Sys.echo('  USAGE :\n'                            , Sys.CLZ_HELP_CMD)
        Sys.echo('    '+AbstractCli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('help '                                  , Sys.CLZ_HELP_CMD)

        Sys.echo('    '+AbstractCli.conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.echo('cmd   '                                 , Sys.CLZ_HELP_CMD, False)
        Sys.echo('[ -a '                                  , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('param_a'                                , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(' -b '                                   , Sys.CLZ_HELP_ARG, False)
        Sys.echo('{'                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('param_b'                                , Sys.CLZ_HELP_PARAM, False)
        Sys.echo('}'                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.echo(']'                                      , Sys.CLZ_HELP_ARG)


    @staticmethod
    def print_help():
        """"""
