#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/log.py
#  # # # # # # # # # # # # # # # # # # # # # # #
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
# ~~ module log ~~

try :
    from inspect        import signature
except :
    # < python 3.3
    signature = None
    pass

from psr.sys     import Sys, Const


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ Class Log ~~

class Log:

    def __init__(self, level=Const.LOG_DEFAULT, debug=True, wtime=True):
        self.debug = debug
        self.level = level
        self.wtime = wtime

    def __call__(self, func, *args):
        def wrapped_func(*args, **kwargs):
            debug, wtime      = self.debug and Sys.g.DEBUG and self.level >= Sys.g.LOG_LEVEL, self.wtime and Sys.g.LOG_TIME
            self.debug_start_time  = None if not wtime else Sys.datetime.now()
            if debug :
                # >= python 3.3
                if signature is not None :
                    l = [p.name for p in signature(func).parameters.values()]
                # < python 3.3
                # !! BAD FIX !!
                else :
                    l = ['self' if args[0].__class__ is not None  else '']

                n = args+tuple(kwargs.items())
                if len(n)>0 and l[0] == 'self':
                    n = n[1:]
                    s = args[0].__class__.__name__ +'.'+func.__name__
                else:
                    s = func.__name__
                Log._write(s, self.debug_start_time, True, n)
            f  = func(*args, **kwargs)
            if debug :
                Log._write(s, self.debug_start_time, False)
            return f
        return wrapped_func


    @staticmethod
    def _formatArgs(args):
        """"""
        args = list(args)
        for i,a in enumerate(args) :
            if not (isinstance(a, str) or isinstance(a, bytes)):
                a = str(a)
            if len(a) > Sys.g.LOG_LIM_ARG_LENGTH :
                args[i] = a[:Sys.g.LOG_LIM_ARG_LENGTH]+'...' if isinstance(a, str) else bytes('...','utf-8')
        args = str(args)[1:-1]
        if args[-1:] == ',' : args = args[:-1]
        return args


    @staticmethod
    def _write(sign, t=None, enter=True, args=''):
        """"""
        if Sys.g.DEBUG :
            #~ DONT USE Sys.g.RLOCK
            isChildProc = not Sys.g_is_main_proc()
            bind_data   = []
            if t is not None :
                bind_data += Sys.pdate(t.timetuple() if enter else Sys.datetime.now().timetuple(), isChildProc)

            a, b, c, d, e = ('=> ' if enter else '<= '), '['+str(Sys.getpid()).rjust(5,' ')+']', ' '+sign+'(', Log._formatArgs(args), ') '
            if not isChildProc :
                Sys.echo(a , Sys.CLZ_IO  , False)
                Sys.echo(b , Sys.CLZ_PID if  not isChildProc else Sys.CLZ_CPID, False)
                Sys.echo(c , Sys.CLZ_FUNC, False)
                try:
                    Sys.echo(d , Sys.CLZ_ARGS, False)
                except :
                    Sys.echo('?nr_arg?' , Sys.CLZ_ARGS, False)
                    pass
                Sys.echo(e , Sys.CLZ_FUNC, False)

            bind_data += [(a, Const.CLZ_IO),(b, Const.CLZ_CPID if isChildProc else Const.CLZ_PID),(c , Const.CLZ_CFUNC if isChildProc else Const.CLZ_FUNC),(d , Const.CLZ_ARGS),(e , Const.CLZ_CFUNC if isChildProc else Const.CLZ_FUNC)]

            if not enter and t is not None :
                bind_data += Sys.pdelta(t, '', isChildProc)
            else :
                bind_data += Sys.dprint(dbcall=isChildProc)

            if isChildProc :
                Sys.sendMainProcMsg(1, bind_data)
            else :
                Sys.wlog(bind_data)
