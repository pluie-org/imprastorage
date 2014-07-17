#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/mproc.py
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
# ~~ module mproc ~~

from multiprocessing                import Process, current_process, Pipe
from multiprocessing.connection     import wait
from threading                      import current_thread
from psr.sys                        import Sys, Const, init
from psr.log                        import Log

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Worker ~~

class Worker:

    @Log(Const.LOG_BUILD)
    def __init__(self, appname, debug, gui, color, loglvl, ppid, event, id, wp, delay, task, *args, **kwargs):
        def mptask(id, *args, **kwargs):
            Sys.sendMainProcMsg(Manager.MSG_INIT, None)
            otask = task(id=id, event=event, *args, **kwargs)
            Sys.sendMainProcMsg(Manager.MSG_END, None)
            return otask

        init(appname, debug, ppid, color, loglvl)
        Sys.g.WPIPE   = wp
        Sys.g.CPID    = id
        Sys.g.GUI     = gui
        # initialize child process event with parent process event
        Sys.g.MPEVENT = event
        if delay : Sys.sleep(delay)
        mptask(id, *args, **kwargs)
        # don't directly close pipe 'cause of eventual logging
        # pipe will auto close on terminating child process


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Manager ~~

class Manager:

    MSG_INIT     = 0
    MSG_PRINT    = 1
    MSG_DATA     = 2
    MSG_END      = 3
    TYPE_MSG     = list(range(4))
    K_ID         = 0
    K_TYPE       = 1
    K_DATA       = 2
    K_PROC       = 0
    K_PIPE       = 1

    checktime    = None

    @Log(Const.LOG_UI)
    def __init__(self, task, nproc=2, delay=None, event=None, *args, **kwargs):
        """"""
        self.readers = []
        self.plist   = []
        self.onstart_bind = None
        self.onrun_bind   = None
        self.onend_bind   = None
        for id in range(nproc):
            r, w = Pipe(duplex=False)
            self.readers.append(r)
            # (process, wpipe)
            p = Process(target=Worker, args=tuple([Sys.g.PRJ_NAME, Sys.g.DEBUG, Sys.g.GUI, Sys.g.COLOR_MODE, Sys.g.LOG_LEVEL, Sys.getpid(), event, id, w, delay, task])+tuple(args), kwargs=kwargs)
            self.plist.append((p, w))

    @Log(Const.LOG_APP)
    def run(self, checktime=None, onstart_bind=None, onrun_bind=None, onend_bind=None):
        self.checktime    = checktime
        self.onstart_bind = onstart_bind
        self.onrun_bind   = onrun_bind
        self.onend_bind   = onend_bind
        for p, w in self.plist:
            p.start()
            w.close()
        self.wait()


    @Log(Const.LOG_DEBUG)
    def wait(self):
        """"""
        while self.readers:
            self.wait_childs()
            if self.checktime is not None : Sys.sleep(self.checktime)


    def getcpid(self, id):
        """"""
        return self.plist[id][self.K_PROC].pid


    @Log(Const.LOG_ALL)
    def wait_childs(self):
        """"""
        for r in wait(self.readers):
            try:
                msg = r.recv()
            except EOFError:
                self.readers.remove(r)
            else:
                if len(msg)==3 and msg[self.K_TYPE] in self.TYPE_MSG :

                    cpid = self.getcpid(msg[self.K_ID])

                    if msg[self.K_TYPE] == self.MSG_INIT :
                        if hasattr(self.onstart_bind, '__call__'):
                            self.onstart_bind(msg[self.K_ID], cpid, msg[self.K_DATA])

                    elif msg[self.K_TYPE] == self.MSG_PRINT :
                        if Sys.g.DEBUG :
                            if not Sys.g.GUI :
                                for item in msg[self.K_DATA] :
                                    Sys.echo(item[0], Sys.clzdic[item[1]], False, True)
                                Sys.dprint('')
                            #~ else :
                            Sys.wlog(msg[self.K_DATA])

                    elif msg[self.K_TYPE] == self.MSG_DATA :
                        if hasattr(self.onrun_bind, '__call__'):
                            self.onrun_bind(msg[self.K_ID], cpid, msg[self.K_DATA])

                    elif msg[self.K_TYPE] == self.MSG_END :
                        if hasattr(self.onend_bind, '__call__'):
                            self.onend_bind(msg[self.K_ID], cpid, msg[self.K_DATA])
