#!/usr/bin/env python
#-*- coding: utf-8 -*-
#  impra/app.py
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
# ~~ module app ~~

from psr.sys                   import Sys, Io, Const, init
from psr.log                   import Log
from psr.mproc                 import Manager
from kirmah.ui                 import IdleObject
from impra                     import conf
from impra.core                import ImpraStorage, ImpraConf
from psr.imap                  import BadHostException, BadLoginException
from gi.repository.GObject     import threads_init, GObject, idle_add, SIGNAL_RUN_LAST, TYPE_NONE, TYPE_STRING, TYPE_INT, TYPE_FLOAT, TYPE_BOOLEAN
from gi.repository.Gtk         import STOCK_MEDIA_PAUSE, STOCK_NEW, STOCK_SAVE, STOCK_REFRESH, STOCK_REMOVE, STOCK_PROPERTIES, STOCK_EDIT, STOCK_DIALOG_INFO, STOCK_CLOSE
from threading                 import Thread, current_thread, enumerate as thread_enum

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class CliThread ~~

class ImpraThread(Thread, IdleObject):
    """"""
    __gsignals__ =  {          # signal type           signal return      signal args
        'completed'        : ( SIGNAL_RUN_LAST       , TYPE_NONE        , ()),
        'interrupted'      : ( SIGNAL_RUN_LAST       , TYPE_NONE        , ()),
        'progress'         : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_FLOAT,)),
        'fileget'          : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN, TYPE_STRING )),
        'fileremoved'      : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN, TYPE_STRING )),
        'fileadded'        : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN, TYPE_STRING)),
        'fileinfos'        : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN,)),
        'fileedited'       : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN,)),
        'indexrefreshed'   : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN,)),
        'needconfig'       : ( SIGNAL_RUN_LAST       , TYPE_NONE        , ()),       
        'filesearch'       : ( SIGNAL_RUN_LAST       , TYPE_NONE        , ()),
        'fileaddretry'     : ( SIGNAL_RUN_LAST       , TYPE_NONE        , (TYPE_BOOLEAN, TYPE_STRING)),
        'hasaddretry'      : ( SIGNAL_RUN_LAST       , TYPE_NONE        , ())
    }

    TASK_WAIT      = 0
    TASK_ADD       = 1
    TASK_GET       = 2
    TASK_REFRESH   = 3
    TASK_REMOVE    = 4
    TASK_INFOS     = 5
    TASK_EDIT      = 6
    TASK_ADD_RETRY = 7
    TASK_EXIT      = 8
    
    K_SIGNAL_NAME  = 0
    K_SIGNAL_BIND  = 1
    K_SIGNAL_DATA  = 2

    TASK_LABEL     = ['wait','add','get','refresh','remove','infos','edit','add-retry','exit']
    TASK_STOCK     = [STOCK_MEDIA_PAUSE, STOCK_NEW, STOCK_SAVE, STOCK_REFRESH, STOCK_REMOVE, STOCK_PROPERTIES, STOCK_EDIT, STOCK_DIALOG_INFO, STOCK_CLOSE]
    
    @Log(Const.LOG_DEBUG)
    def __init__(self, evtStop, taskQueue, condition, conf, name='ImpraThread', instce=None):
        Thread.__init__(self)
        IdleObject.__init__(self)
        self.setName(name)
        self.cancelled = False
        self.evtStop   = evtStop
        self.taskQueue = taskQueue
        self.condition = condition
        self.conf      = conf
        self.impst     = instce
        print(' INIT THREAD '+name)
        print(self.impst)
    
    @Log(Const.LOG_DEBUG)
    def connect_signals(self, signals, usrData=None):
        """"""
        for signal in signals:
            self.connect(signal[self.K_SIGNAL_NAME], signal[self.K_SIGNAL_BIND], signal[self.K_SIGNAL_DATA] if len(signal)>self.K_SIGNAL_DATA else usrData)


    @Log(Const.LOG_DEBUG)
    def run(self):
        """"""
        self.cancelled = False
        self.evtStop.clear()
        Sys.g.THREAD_CLI       = self
        Sys.g.GUI              = True
        Sys.g.GUI_PRINT_STDOUT = True
        done                   = False
        self.can_retry         = True
        init(conf.PRG_NAME, Sys.g.DEBUG, loglvl=Const.LOG_APP)        
        try :
            if self.impst is None :
                
                label = ' [[ INIT IMPRASTORAGE ]] '
                label = ' '+'~'*((Const.LINE_SEP_LEN-len(label))//2-1)+label+'~'*((Const.LINE_SEP_LEN-len(label))//2-1)+' '
                Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0     , True),
                           (label.ljust(Const.LINE_SEP_LEN, ' ')   , Const.CLZ_INIT  , True),
                           (Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0     , True)])
                
                self.impst = ImpraStorage(self.conf)

            done = True
        except Exception as e :
            self.emit('needconfig')
            raise e
        self.emit('indexrefreshed', done)
        if done :        
            while not self.evtStop.is_set() or not self.cancelled:
                with self.condition :
                    self.condition.wait_for(lambda : not self.taskQueue.empty(), 2)
                    
                    if self.can_retry and self.impst.hasBackupAddMap():
                        self.emit('hasaddretry')
                        self.can_retry = False
                    
                    if not self.taskQueue.empty():
                        task, params, idtask = self.taskQueue.get_nowait()
                        label = ' [[ TASK '+str(idtask)+' : '+self.TASK_LABEL[task].upper()+' ]] '
                        label = ' '+'>'*((Const.LINE_SEP_LEN-len(label))//2-1)+label+'<'*((Const.LINE_SEP_LEN-len(label))//2-1)+' '
                        Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0     , True),
                                   (label.ljust(Const.LINE_SEP_LEN, ' ')   , Const.CLZ_ACTION, True),
                                   (Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0     , True)])
                        
                        try:
                            if task is self.TASK_WAIT :
                                print('wait')
                                Sys.sleep(params)
                            elif task is self.TASK_GET:
                                #~ mg        = Manager(self.taskGet, 1, None, Sys.g.MPEVENT, uid=params)
                                #~ mg.run()
                                #~ self.emit('fileget', True, '')
                                #~ Thread(target=self.taskGet, name='impra-1', kwargs={'uid':params}).start()
                                print(params)
                                self.taskGet(params)
                            elif task is self.TASK_ADD:
                                self.taskAdd(params)
                            elif task is self.TASK_ADD_RETRY:
                                self.taskAddRetry(params)
                            elif task is self.TASK_REFRESH:
                                self.taskRefresh(params)
                            elif task is self.TASK_INFOS:
                                self.taskInfos(params)
                            elif task is self.TASK_REMOVE:
                                self.taskRemove(params)
                            elif task is self.TASK_EDIT:
                                self.taskEdit(params)
                            self.taskQueue.task_done()

                        except self.impst.SocketError() as e :
                            Sys.pwarn((('ImpraThread.run : ',(str(e),Sys.CLZ_WARN_PARAM), ' !'),))
                            self.impst.reconnect()

                        except Exception as e:
                            print(type(e))
                            Sys.pwarn((('ImpraThread.run : ',(str(e),Sys.CLZ_WARN_PARAM), ' !'),))                            
                    else :
                        """"""
                Sys.sleep(0.5)
        self.emit('completed')


    def taskGet(self, uid):
        """"""
        done, p = self.impst.getFile(uid)
        self.emit('fileget', done, p)

    
    def taskAdd(self, params):
        """"""
        fromPath, label, catg = params
        done, p = self.impst.addFile(fromPath, label, catg)
        self.emit('fileadded', done, p)
        self.emit('indexrefreshed', done)


    def taskAddRetry(self, params=None):
        done, p = self.impst.sendFile(self.impst.getBackupAddMap(), True)
        self.emit('fileadded', done, p)
        self.emit('indexrefreshed', done)
        self.can_retry = True


    def taskRefresh(self, noparam=None):
        """"""
        self.emit('progress',10)
        self.impst.idxu.get(True)
        self.emit('indexrefreshed', True)


    def taskInfos(self, uid):
        """"""
        self.impst.getInfo(uid)
        self.emit('fileinfos', True)


    def taskRemove(self, uid):
        """"""
        done, p = self.impst.removeFile(uid)
        self.emit('fileremoved', done, p)
        self.emit('indexrefreshed', done)


    def taskEdit(self, params):
        """"""
        key, label, catg = params 
        done = self.impst.editFile(key, label, catg)
        self.emit('fileedited', done)
        self.emit('indexrefreshed', done)


    @Log(Const.LOG_NEVER)
    def progress(self, value):
        """"""
        #~ print('progress '+str(value))        
        self.emit('progress', value)


    @Log(Const.LOG_NEVER)
    def cancel(self):
        """
        Threads in python are not cancellable, so we implement our own
        cancellation logic
        """
        self.cancelled = True
        self.evtStop.set()


    @Log(Const.LOG_NEVER)
    def stop(self):
        """"""
        if self.isAlive():
            self.cancel()
            if current_thread().getName()==self.getName():
                try:
                    self.emit('interrupted')
                    Sys.thread_exit()
                except RuntimeError as e :
                    print(str(self.getName()) + ' COULD NOT BE TERMINATED')
                    raise e

