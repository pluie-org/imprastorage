#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/sys.py
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
# ~~ module sys ~~

from psr.io             import Io
from psr.const          import Const
from threading          import RLock, current_thread
from multiprocessing    import Event
from queue              import Queue

def init(name, debug, remote=False, color=True, loglvl=Const.LOG_NEVER):
    Sys.g_init(name, debug, remote, color, loglvl)
    Sys.g_set_main_proc(remote)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Sys ~~

class Sys:
    """"""

    from platform   import system  as getSysName
    from os         import system  as sysCall, remove as removeFile, makedirs, sep, getpid, listdir
    from getpass    import getuser as getUserLogin
    from time       import strftime, mktime, time, localtime, sleep
    from datetime   import datetime, timedelta
    from sys        import exit, stdout, executable
    from os.path    import abspath, dirname, join, realpath, basename, getsize, isdir, splitext
    from math       import log, floor, ceil
    from _thread    import exit as thread_exit

    import builtins as g

    g.DEBUG                    = False
    g.LOG_LEVEL                = Const.LOG_DEFAULT
    g.LOG_TIME                 = False
    g.LOG_LIM_ARG_LENGTH       = Const.LOG_LIM_ARG_LENGTH
    g.QUIET                    = False
    g.COLOR_MODE               = True
    g.RLOCK                    = None
    g.MPRLOCK                  = None
    g.WPIPE                    = None
    g.THREAD_CLI               = None
    g.UI_AUTO_SCROLL           = True
    g.CPID                     = None
    g.SIGNAL_STOP              = 0
    g.SIGNAL_START             = 1
    g.SIGNAL_RUN               = 2
    g.SIGNAL_CLEAR             = 3
    g.GUI                      = False
    g.GUI_PRINT_STDOUT         = True
    g.MPEVENT                  = Event()
    g.LOG_QUEUE                = None


    @staticmethod
    def g_init(prjName, debug=True, remote=False, color=True, loglvl=Const.LOG_DEFAULT):
        """"""
        Sys.g.PRJ_NAME             = prjName
        Sys.g.DEBUG                = debug
        Sys.g.COLOR_MODE           = color
        Sys.g.LOG_LEVEL            = loglvl
        Sys.g.LOG_TIME             = True
        Sys.g.MAIN_PROC            = None
        Sys.g.RLOCK                = RLock()
        Sys.g.LOG_QUEUE            = Queue() if Sys.g.GUI else None


    @staticmethod
    def sendMainProcMsg(type, data):
        """"""
        if not Sys.g_is_main_proc() and Sys.g.WPIPE  is not None and Sys.g.CPID is not None and type in range(4) :
            Sys.g.WPIPE.send((Sys.g.CPID, type, data))


    @staticmethod
    def g_set_main_proc(ppid=None):
        """"""
        Sys.g.MAIN_PROC = Sys.getpid() if ppid is None or ppid is False else ppid


    @staticmethod
    def g_is_main_proc():
        """"""
        try :
            return Sys.g.MAIN_PROC == Sys.getpid()
        except :
            return False


    @staticmethod
    def g_has_ui_trace():
        """"""
        try:
            return Sys.g.GUI and Sys.g.DEBUG
        except Exception as e:
            return False


    @staticmethod
    def cli_emit_progress(value=0):
        """"""
        if Sys.g.THREAD_CLI is not None : Sys.g.THREAD_CLI.progress(value)


    @staticmethod
    def is_cli_cancel(event=None):
        """"""
        c = Sys.g.THREAD_CLI is not None and Sys.g.THREAD_CLI.cancelled
        return c or (event is not None and event.is_set())


    @staticmethod
    def isUnix():
        """"""
        return not Sys.getSysName() == 'Windows'


    @staticmethod
    def clear():
        return Sys.sysCall('cls' if not Sys.isUnix() else 'clear')


    @staticmethod
    def mkdir_p(path):
        """"""
        try:
            Sys.makedirs(path)
        except OSError as e:
            if e.errno == Io.EEXIST:
                pass
            else: raise


    @staticmethod
    def readableBytes(b, p=2):
        """Give a human representation of bytes size `b`
        :Returns: `str`
        """
        if b is None or b=='': return '0'
        else :b = int(b)
        units = [Const.UNIT_SHORT_B, Const.UNIT_SHORT_KIB, Const.UNIT_SHORT_MIB, Const.UNIT_SHORT_GIB, Const.UNIT_SHORT_TIB];
        b = max(b,0);
        if b == 0 : lb= 0
        else : lb    = Sys.log(b)
        p = Sys.floor(lb/Sys.log(1024))
        p = min(p, len(units)- 1)
        #Uncomment one of the following alternatives
        b /= pow(1024,p)
        #b /= (1 << (10 * p))
        return str(round(b, 1))+' '+units[p]


    @staticmethod
    def getFileExt(fromPath):
        """"""
        return Sys.splitext(fromPath)


    @staticmethod
    def getFileSize(path):
        """"""
        return Sys.readableBytes(Sys.getsize(path))


    @staticmethod
    def getPrintableBytes(bdata):
        """"""
        data = ''
        if isinstance(bdata,bytes) :
            try:
                data = str(bdata, 'utf-8')
            except Exception as e:
                hexv = []
                for i in bdata[1:] :
                    hexv.append(hex(i)[2:].rjust(2,'0'))
                data = ' '.join(hexv)
                pass
        else :
            data = bdata
        return data


    @staticmethod
    def getHexaBytes(bdata):
        """"""
        data = ''
        if isinstance(bdata,bytes) :
            hexv = []
            for i in bdata[1:] :
                hexv.append(hex(i)[2:].rjust(2,'0'))
                data = ' '.join(hexv)
        else :
            data = bdata
        return data


    @staticmethod
    # never log this func -> maximum recursion
    def wlog(data=[('','default')]):
        """"""
        if not Sys.is_cli_cancel():
            if Sys.g.LOG_QUEUE is not None :
                try :
                    Sys.g.LOG_QUEUE.put((current_thread().name,data))
                    Sys.cli_emit_progress()
                except Exception as e:
                    Sys.pwarn((('wlog exception ',(str(e),Sys.CLZ_ERROR_PARAM), ' !'),), True)

        else :
            Sys.g.THREAD_CLI.stop()


    @staticmethod
    def pwlog(data, guiClear=False):
        """ data=[('text', keycolor, newline)]"""
        if guiClear : Sys.wlog(Sys.g.SIGNAL_CLEAR)
        wd = []
        for item in data :
            nl = False if len(item)< 3 else (item[2]==1 or item[2]==True)
            c  = Const.CLZ_0 if (len(item)< 2 or item[1] not in Sys.clzdic) else item[1]
            Sys.echo(item[0], Sys.clzdic[c], nl)
            wd += [(item[0], c)]
            if nl and Sys.g.GUI :
                Sys.wlog(wd)
                wd = []
        if len(wd) > 0 and Sys.g.GUI :
            Sys.wlog(wd)


    @staticmethod
    def echo(data, colors, endLF=True, endClz=True):
        """"""
        if isinstance(data,bytes) :
            data = Sys.getPrintableBytes(data)

        ev = '' if not endLF else Sys.Clz._LF
        tokens = [c.lstrip(Sys.Clz._MARKER[0]).rstrip(Sys.Clz._SEP) for c in colors.split(Sys.Clz._MARKER) if c is not '']
        if Sys.isUnix() :
            if data is None: data = ''
            if endClz : data += Sys.Clz._uOFF
            if Sys.g.COLOR_MODE :
                Sys.dprint(eval('Sys.Clz._u'+'+Sys.Clz._u'.join(tokens))+data,end=ev, dbcall=False)
            else :
                Sys.dprint(data,end=ev, dbcall=False)
        else :
            if Sys.g.COLOR_MODE : Sys.Clz.setColor(eval('Sys.Clz._w'+'|Sys.Clz._w'.join(tokens)))
            Sys.dprint(data,end=ev, dbcall=False)
            Sys.stdout.flush()
            if endClz and Sys.g.COLOR_MODE : Sys.Clz.setColor(Sys.Clz._wOFF)


    @staticmethod
    def dprint(d='',end=Const.LF, dbcall=False):
        """"""
        dbcall = Sys.g.QUIET
        if not dbcall :
            if not Sys.g.GUI or Sys.g.GUI_PRINT_STDOUT :
                if Sys.g.RLOCK is not None :
                    with Sys.g.RLOCK :
                        if not Sys.g.QUIET :
                            print(d,end=end)
                else :
                    if not Sys.g.QUIET :
                        print(d,end=end)

        bdata = [(d,Const.CLZ_DEFAULT)]
        return bdata


    @staticmethod
    def eprint(d='', label=Const.WARN, dbcall=False):
        """"""
        c = Sys.CLZ_ERROR if label is Const.ERROR else Sys.CLZ_WARN
        Sys.echo(' '+label+' : ', c, False, False)
        Sys.echo(str(d)+' ', c, True, True)

        bdata = [(label+' : ' , label),(str(d)+' ', label)]
        return bdata


    @staticmethod
    def pdate(t, dbcall = False):
        """"""
        t, s = Sys.strftime('%H:%M',t), Sys.strftime(':%S ',t)
        if not dbcall :
            Sys.echo(t , Sys.CLZ_TIME, False)
            Sys.echo(s , Sys.CLZ_SEC , False)

        bdata = [(t , Const.CLZ_TIME),(s , Const.CLZ_SEC)]
        return bdata


    @staticmethod
    def pkval(label, value, pad=40, dbcall= False):
        """"""
        l, v = label.rjust(pad,' '), ' '+str(value)
        if not dbcall :
            Sys.echo(l, Sys.CLZ_SEC  , False)
            Sys.echo(v, Sys.CLZ_TIME , True)

        bdata = [(l, Const.CLZ_SEC),(v, Const.CLZ_TIME)]
        return bdata


    @staticmethod
    def getDelta(t):
        v = ''.join(['{:.5f}'.format(Sys.time()-(Sys.mktime(t.timetuple())+1e-6*t.microsecond)),' s'])
        return v

    @staticmethod
    def pdelta(t, label='', dbcall= False):
        """"""
        if len(label)>0 and not dbcall : Sys.echo(label+' ', Sys.CLZ_IO, False)
        v = Sys.getDelta(t)
        if not dbcall :
            Sys.echo(v, Sys.CLZ_DELTA)

        bdata = []
        if len(label)>0 :
            bdata.append((label+' ', Const.CLZ_IO))
        bdata.append((v, Const.CLZ_DELTA))
        return bdata


    @staticmethod
    def pcontent(content, color=None, bcolor=Const.CLZ_DEFAULT, dbcall= False):
        """"""
        if not dbcall : Sys.echo(content, Sys.CLZ_SEC if color is None else color)

        bdata = [(content, bcolor)]
        return bdata


    @staticmethod
    def pwarn(data, isError=False, length=Const.LINE_SEP_LEN, dbcall=False):
        """ data struct :
          ( # line0
            'simple line', # LF
            # line1
            #    p0                   p1                      p2
             ('complex line with ',('paramValue',fgcolor), ' suit complex line'), # LF
            # line2
             'other simple line '
          )
        """
        w      = ' '+(Const.WARN if not isError else Const.ERROR)+' : '
        clz    = Sys.CLZ_WARN if not isError else Sys.CLZ_ERROR
        clzp   = Sys.CLZ_WARN_PARAM if not isError else Sys.CLZ_ERROR_PARAM
        uiclz  = Const.CLZ_WARN if not isError else Const.CLZ_ERROR
        uiclzp = Const.CLZ_WARN_PARAM if not isError else Const.CLZ_ERROR_PARAM

        if not dbcall : Sys.echo(w, clzp, False, False)
        bdata  = []
        if not Sys.g.QUIET :
            bdata.append((w, uiclzp))
        for i, line in enumerate(data) :
            if i > 0 :
                if not dbcall : Sys.echo(' '*len(w), clz, False, False)
                if not Sys.g.QUIET :
                    bdata.append((' '*len(w), uiclz))
            if isinstance(line,str) :
                s = line.ljust(length-len(w),' ')
                if not dbcall : Sys.echo(s, clz, True, True)

                if not Sys.g.QUIET :
                    bdata.append((s, uiclz))
                    Sys.wlog(bdata)
                    bdata = []
            else :
                sl = 0
                for p in line :
                    if isinstance(p,str) :
                        Sys.echo(p, clz, False, False)
                        bdata.append((p, uiclz))
                        sl += len(p)
                    else :
                        Sys.echo(p[0], clzp+p[1], False, False)
                        bdata.append((p[0], uiclzp))
                        sl += len(p[0])
                s = ' '.ljust(length-sl-len(w),' ')
                if not dbcall : Sys.echo(s, clz, True, True)
                if not Sys.g.QUIET :
                    bdata.append((s, uiclz))
                    Sys.wlog(bdata)
                    bdata = []

        if not dbcall  : Sys.dprint()
        if Sys.g.DEBUG : Sys.wlog([('',Const.CLZ_DEFAULT)])


    @staticmethod
    def _psymbol(ch, done=True):
        """"""
        Sys.echo(' ', Sys.CLZ_DEFAULT, False, False)
        Sys.echo(' '+ch+' ',  Sys.CLZ_HEAD_APP if done else Sys.CLZ_SYMBOL, False, True)
        Sys.echo(' ', Sys.CLZ_DEFAULT, False, True)
        bdata = [(' ', Const.CLZ_DEFAULT),(' '+ch+' ', Const.CLZ_HEAD_APP if done else Sys.CLZ_SYMBOL),(' ', Const.CLZ_DEFAULT)]
        return bdata


    @staticmethod
    def pask(ask, yesValue='yes', noValue='no'):
        """"""
        Sys._psymbol('?')
        Sys.echo('', Sys.Clz.fgb3, False, False)
        ask    = ask + ' ('+yesValue+'/'+noValue+') ? '
        answer = input(ask)
        while answer.lower()!=yesValue.lower() and answer.lower()!=noValue.lower() :
            s = 'Please enter either '+yesValue+' or '+noValue+' : '
            answer = input(' '.ljust(5,' ')+s.ljust(len(ask),' '))
        Sys.dprint()
        return answer.lower()==yesValue.lower()


    @staticmethod
    def pstep(title, stime, done, noelf=False, exitOnFailed=True, length=100):
        """"""
        if stime is not None :
            v = ' ('+''.join(['{:.5f}'.format(Sys.time()-(Sys.mktime(stime.timetuple())+1e-6*stime.microsecond)),' s'])+')'
        else : v = ''
        bdata = Sys._psymbol('*')
        Sys.echo(title, Sys.CLZ_TITLE, False, False)
        Sys.echo(v+' '.ljust(length-len(title)-20-len(v), ' '),Sys.CLZ_DELTA, False, True)
        if done :
            Sys.echo(' ==  '+Const.OK+'  == ', Sys.CLZ_OK)
        else :
            Sys.echo(' ==  '+Const.KO+'  == ', Sys.CLZ_KO)

        bdata = bdata + [(title, Const.CLZ_TITLE),(v+' '.ljust(length-len(title)-20-len(v)), Const.CLZ_DELTA),(' ==  '+(Const.OK if done else Const.KO)+'  == ', (Const.CLZ_OK if done else Const.CLZ_KO))]

        Sys.wlog(bdata)
        if not noelf :
            Sys.wlog(Sys.dprint())

        if exitOnFailed and not done:
           Sys.exit(1)


    @staticmethod
    def ptask(title='Processing, please wait'):
        if not Sys.g.QUIET :
            s = ' '+title+'...'
            Sys.echo(s, Sys.CLZ_TASK )
            Sys.wlog([(s, Const.CLZ_TASK)])
            Sys.wlog(Sys.dprint())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Coloriz ~~

class Coloriz:

    _MARKER        = '!§'
    """"""
    _SEP           = ';'
    """"""
    _PATTERN_COLOR = '^'+_MARKER[0]+'[nfNFbB][0-7]'+_SEP+'$'
    """"""
    _wFH   = 0x0008
    """"""
    _wBH   = 0x0080
    """"""
    _uOFF  = '\033[1;m'
    """"""
    _wOFF  = None
    """"""
    _LF    = Const.LF
    """"""
    OFF    = _MARKER+_MARKER[0]+'OFF'+_SEP+_MARKER
    """"""
    def __init__(self):
        """Colors for both plateform are : 0: black - 1: red - 2:green - 3: yellow - 4: blue - 5: purple - 6: cyan - 7: white
        available class members :
        foreground normal (same as bold for w32):
           self.fgn0 -> self.fgn7
        foreground bold :
           self.fgb0 -> self.fgb7
        foreground high intensity (same as bold high intensity for w35):
           self.fgN0 -> self.fgN7
        foreground bold high intensity :
           self.fgB0 -> self.fgB7
        background
           self.bg0 -> self.bg7
        background high intensity
           self.BG0 -> self.BG7
        default colors :
            self.OFF
        """
        if not Sys.isUnix():
            j = 0
            for i in (0,4,2,6,1,5,3,7):
                exec('self._wf%i = 0x000%i' % (i,j) + Const.LF+'self._wb%i = 0x00%i0' % (i,j) + Const.LF+'self._wF%i = 0x000%i | self._wFH' % (i,j) + Const.LF+'self._wB%i = 0x00%i0 | self._wBH' % (i,j))
                # normal eq bold
                exec('self._wn%i = self._wf%i' % (i,i))
                # normal high intensity eq bold high intensity
                exec('self._wN%i = self._wF%i' % (i,i))
                j += 1
            import psr.w32color as w32cons
            self._wOFF    = w32cons.get_text_attr()
            self._wOFFbg  = self._wOFF & 0x0070
            self._wOFFfg  = self._wOFF & 0x0007
            self.setColor = w32cons.set_text_attr

        for i in range(0,8):
            # foreground normal
            exec('self.fgn%i = self._MARKER + self._MARKER[0] + "n%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._un%i = "\\033[0;3%im"' % (i,i))
            # foreground bold
            exec('self.fgb%i = self._MARKER + self._MARKER[0] + "f%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._uf%i = "\\033[1;3%im"' % (i,i))
            # foreground high intensity
            exec('self.fgN%i = self._MARKER + self._MARKER[0] + "N%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._uN%i = "\\033[0;9%im"' % (i,i))
            # foreground bold high intensity
            exec('self.fgB%i = self._MARKER + self._MARKER[0] + "F%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._uF%i = "\\033[1;9%im"' % (i,i))
            # background
            exec('self.bg%i = self._MARKER + self._MARKER[0] + "b%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._ub%i = "\\033[4%im"' % (i,i))
            # background high intensity
            exec('self.BG%i = self._MARKER + self._MARKER[0] + "B%i" + self._SEP + self._MARKER' % (i,i))
            if Sys.isUnix() : exec('self._uB%i = "\\033[0;10%im"' % (i,i))

Sys.Clz                  = Coloriz()
Sys.CLZ_TIME             = Sys.Clz.fgN2+Sys.Clz.bg0
Sys.CLZ_SEC              = Sys.Clz.fgb7+Sys.Clz.bg0
Sys.CLZ_PID              = Sys.Clz.fgb1+Sys.Clz.bg0
Sys.CLZ_PPID             = Sys.Clz.fgb1+Sys.Clz.bg0
Sys.CLZ_CPID             = Sys.Clz.fgb7+Sys.Clz.bg0
Sys.CLZ_IO               = Sys.Clz.fgB1+Sys.Clz.bg0
Sys.CLZ_FUNC             = Sys.Clz.fgb3+Sys.Clz.bg0
Sys.CLZ_CFUNC            = Sys.Clz.fgb3+Sys.Clz.bg0
Sys.CLZ_ARGS             = Sys.Clz.fgn7+Sys.Clz.bg0
Sys.CLZ_DELTA            = Sys.Clz.fgN4+Sys.Clz.bg0
Sys.CLZ_TASK             = Sys.Clz.fgB2+Sys.Clz.bg0
Sys.CLZ_ERROR            = Sys.Clz.fgb7+Sys.Clz.bg1
Sys.CLZ_ERROR_PARAM      = Sys.Clz.fgb3+Sys.Clz.bg1
Sys.CLZ_WARN             = Sys.Clz.fgb7+Sys.Clz.bg5
Sys.CLZ_WARN_PARAM       = Sys.Clz.fgb3+Sys.Clz.bg5
Sys.CLZ_DEFAULT          = Sys.Clz.fgb7+Sys.Clz.bg0
Sys.CLZ_TITLE            = Sys.Clz.fgB7+Sys.Clz.bg0
Sys.CLZ_SYMBOL           = Sys.Clz.BG4+Sys.Clz.fgB7
Sys.CLZ_OK               = Sys.Clz.bg2+Sys.Clz.fgb7
Sys.CLZ_KO               = Sys.Clz.bg1+Sys.Clz.fgb7
Sys.CLZ_ACTION           = Sys.Clz.BG4+Sys.Clz.fgB7
Sys.CLZ_INIT             = Sys.Clz.BG4+Sys.Clz.fgB7
Sys.CLZ_HELP_PRG         = Sys.Clz.fgb7
Sys.CLZ_HELP_CMD         = Sys.Clz.fgB3
Sys.CLZ_HELP_PARAM       = Sys.Clz.fgB1
Sys.CLZ_HELP_ARG         = Sys.Clz.fgB3
Sys.CLZ_HELP_COMMENT     = Sys.Clz.fgn7
Sys.CLZ_HELP_ARG_INFO    = Sys.Clz.fgb7
Sys.CLZ_HELP_DESC        = Sys.Clz.fgN1
Sys.CLZ_HEAD_APP         = Sys.Clz.BG4+Sys.Clz.fgB7
Sys.CLZ_HEAD_KEY         = Sys.Clz.fgB3
Sys.CLZ_HEAD_VAL         = Sys.Clz.fgB4
Sys.CLZ_HEAD_SEP         = Sys.Clz.fgB0
Sys.CLZ_HEAD_LINE        = Sys.Clz.fgN0

Sys.CLZ_0                = Sys.Clz.fgn7
Sys.CLZ_1                = Sys.Clz.fgB1
Sys.CLZ_2                = Sys.Clz.fgB2
Sys.CLZ_3                = Sys.Clz.fgB3
Sys.CLZ_4                = Sys.Clz.fgB4
Sys.CLZ_5                = Sys.Clz.fgB5
Sys.CLZ_6                = Sys.Clz.fgB6
Sys.CLZ_7                = Sys.Clz.fgB7

Sys.clzdic               = { Const.CLZ_0       : Sys.CLZ_0      , Const.CLZ_1     : Sys.CLZ_1     , Const.CLZ_2           : Sys.CLZ_2, 
                             Const.CLZ_3       : Sys.CLZ_3      , Const.CLZ_4     : Sys.CLZ_4     , Const.CLZ_5           : Sys.CLZ_5,
                             Const.CLZ_6       : Sys.CLZ_6      , Const.CLZ_7     : Sys.CLZ_7     ,
                             Const.CLZ_TASK    : Sys.CLZ_TASK   , Const.CLZ_SYMBOL: Sys.CLZ_SYMBOL, 
                             Const.CLZ_TIME    : Sys.CLZ_TIME   , Const.CLZ_SEC   : Sys.CLZ_SEC   , 
                             Const.CLZ_IO      : Sys.CLZ_IO     , Const.CLZ_CPID  : Sys.CLZ_CPID  , Const.CLZ_PID         : Sys.CLZ_PID, 
                             Const.CLZ_CFUNC   : Sys.CLZ_CFUNC  , Const.CLZ_FUNC  : Sys.CLZ_FUNC  , Const.CLZ_ARGS        : Sys.CLZ_ARGS, 
                             Const.CLZ_DELTA   : Sys.CLZ_DELTA  , 
                             Const.CLZ_ERROR   : Sys.CLZ_ERROR  , Const.CLZ_WARN  : Sys.CLZ_WARN  , Const.CLZ_ERROR_PARAM : Sys.CLZ_ERROR_PARAM, Const.CLZ_WARN_PARAM : Sys.CLZ_WARN_PARAM, 
                             Const.CLZ_DEFAULT : Sys.CLZ_DEFAULT,
                             Const.CLZ_ACTION  : Sys.CLZ_ACTION ,
                             Const.CLZ_INIT    : Sys.CLZ_INIT
                           }
