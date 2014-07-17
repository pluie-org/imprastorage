#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/const.py
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
# ~~ module const ~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Const ~~

class Const:

    LOG_NEVER             = -1
    LOG_ALL               = 0
    LOG_BUILD             = 1
    LOG_PRIVATE           = 2
    LOG_DEBUG             = 3
    LOG_WARN              = 4
    LOG_UI                = 5
    LOG_DEFAULT           = 6
    LOG_APP               = 7

    CLZ_TIME              = 'time'
    CLZ_SEC               = 'sec'
    CLZ_CPID              = 'cpid'
    CLZ_PID               = 'pid'
    CLZ_IO                = 'io'
    CLZ_FUNC              = 'func'
    CLZ_CFUNC             = 'cfunc'
    CLZ_ARGS              = 'args'
    CLZ_DELTA             = 'delta'
    CLZ_ERROR             = 'error'
    CLZ_ERROR_PARAM       = 'errorp'
    CLZ_WARN              = 'warn'
    CLZ_WARN_PARAM        = 'warnp'
    CLZ_DEFAULT           = 'default'
    CLZ_TITLE             = 'title'
    CLZ_OK                = 'ok'
    CLZ_KO                = 'ko'
    CLZ_TASK              = 'task'
    CLZ_SYMBOL            = 'symbol'
    CLZ_ACTION            = 'action'
    CLZ_INIT              = 'init'
    
    CLZ_0                 = 'color0'
    CLZ_1                 = 'color1'
    CLZ_2                 = 'color2'
    CLZ_3                 = 'color3'
    CLZ_4                 = 'color4'
    CLZ_5                 = 'color5'
    CLZ_6                 = 'color6'
    CLZ_7                 = 'color7'

    CLZ_HEAD_APP          = 'headapp'
    CLZ_HEAD_SEP          = 'headsep'
    CLZ_HEAD_KEY          = 'headkey'
    CLZ_HEAD_VAL          = 'headval'

    ERROR                 = 'ERROR'
    WARN                  = 'WARNING'
    OK                    = 'OK'
    KO                    = 'KO'

    LOG_LIM_ARG_LENGTH    = 20

    LF                    = """
"""
    LF_STR                = '\n'

    UNIT_SHORT_B          = 'B'
    UNIT_SHORT_KIB        = 'KiB'
    UNIT_SHORT_MIB        = 'MiB'
    UNIT_SHORT_GIB        = 'GiB'
    UNIT_SHORT_TIB        = 'TiB'

    LINE_SEP_LEN          = 100
    LINE_SEP_CHAR         = '-'

const = Const()
