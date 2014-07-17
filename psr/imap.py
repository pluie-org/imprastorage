#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/imap.py
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
# ~~ module imap ~~

from imaplib            import Commands, IMAP4_SSL, Time2Internaldate
from binascii           import b2a_base64, a2b_base64
from codecs             import register, StreamReader, StreamWriter
from email              import message_from_bytes
from email.header       import decode_header
from email.message      import Message
from re                 import search as research, split as resplit
from multiprocessing    import Process
from psr.sys            import Io, Sys, Const
from psr.log            import Log


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ ImapUtf7 decoding/encoding ~~

def _seq_encode(seq,l):
    """"""
    if len(seq) > 0 :
        l.append('&%s-' % str(b2a_base64(bytes(''.join(seq),'utf-16be')),'utf-8').rstrip('\n=').replace('/', ','))
    elif l:
        l.append('-')


def _seq_decode(seq,l):
    """"""
    d = ''.join(seq[1:])
    pad = 4-(len(d)%4)
    l.append(str(a2b_base64(bytes(d.replace(',', '/')+pad*'=','utf-16be')),'utf-16be'))


def encode(s):
    """"""
    l, e, = [], []
    for c in s :
        if ord(c) in range(0x20,0x7e):
            if e : _seq_encode(e,l)
            e = []
            l.append(c)
            if c == '&' : l.append('-')
        else :
            e.append(c)
    if e : _seq_encode(e,l)
    return ''.join(l)


def decode(s):
    """"""
    l, d = [], []
    for c in s:
        if c == '&' and not d : d.append('&')
        elif c == '-' and d:
            if len(d) == 1: l.append('&')
            else : _seq_decode(d,l)
            d = []
        elif d: d.append(c)
        else: l.append(c)
    if d: _seq_decode(d,l)
    return ''.join(l)


def _encoder(s):
    """"""
    e = bytes(encode(s),'utf-8')
    return e, len(e)


def _decoder(s):
    """"""
    d = decode(str(s,'utf-8'))
    return d, len(d)


def _codec_imap4utf7(name):
    """"""
    if name == 'imap4-utf-7':
        return (_encoder, _decoder, Imap4Utf7StreamReader, Imap4Utf7StreamWriter)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ StreamReader & StreamWriter ~~

class Imap4Utf7StreamReader(StreamReader):
    def decode(self, s, errors='strict'): return _decoder(s)

class Imap4Utf7StreamWriter(StreamWriter):
    def decode(self, s, errors='strict'): return _encoder(s)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ registering codec ~~

register(_codec_imap4utf7)




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ Imap utilities ~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImapConfig ~~

class ImapConfig:
    """"""

    def __init__(self, host, user, pwd, port='993'):
        """"""
        self.host = host
        self.user = user
        self.pwd  = pwd
        self.port = str(port)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImapClient ~~

class ImapClient(IMAP4_SSL):
    """"""

    Commands['XLIST'] =  ('AUTH', 'SELECTED')

    @Log(Const.LOG_DEBUG)
    def xlist(self, directory='""', pattern='*'):
        """(X)List mailbox names in directory matching pattern. Using Google's XLIST extension

        (status, [data]) = <instance>.xlist(directory='""', pattern='*')

        'data' is list of XLIST responses.

        thks to barduck : http://stackoverflow.com/users/602242/barduck
        """
        try :
            name         = 'XLIST'
            status, data = self._simple_command(name, directory, pattern)
            return self._untagged_response(status, data, name)
        except :
            return 'NO', ''


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImapHelper ~~

class ImapHelper:
    """"""

    K_HEAD, K_DATA = 0, 1
    """"""
    OK           = 'OK'
    """"""
    KO           = 'NO'
    """"""
    ENCODING     = 'utf-8'
    """"""
    REG_SATUS    = r'^"?(.*)"? \(([^\(]*)\)'
    """"""
    NO_SELECT    = '\\Noselect'
    """"""
    CHILDREN     = '\\HasChildren'
    """"""
    NO_CHILDREN  = '\\HasNoChildren'
    """"""
    INBOX        = '\\Inbox'
    """"""
    DRAFTS       = '\\Drafts'
    """"""
    TRASH        = '\\Trash'
    """"""
    SENT         = '\\Sent'
    """"""
    DELETED      = '\\Deleted'
    """"""
    FLAGS        = '+FLAGS'
    """"""

    @Log(Const.LOG_BUILD)
    def __init__(self, conf, box='INBOX', noBoxCreat=False):
        """"""
        if conf.host != None and research('yahoo.com', conf.host) is not None :
            self.DRAFTS = self.DRAFTS[:-1]
        self.conf       = conf
        self.rootBox    = box
        self.BOXS       = {}
        self.cnx        = None
        self.cnxusr     = None
        self.noBoxCreat = noBoxCreat
        self.switchAccount(self.conf, self.rootBox, True)

    @Log()
    def reconnect(self):
        """"""
        Sys.pwlog([(' Reconnecting... ', Const.CLZ_7, True)])
        self.switchAccount(self.conf, self.rootBox, True)


    @Log()
    def switchAccount(self, conf, box='INBOX', force=False):
        """"""
        if force or self.cnx is None or self.cnxusr is not conf.user :
            try :
                Sys.pwlog([(' Attempt to login... '                , Const.CLZ_7),
                           ('('                                    , Const.CLZ_0),
                           (conf.user                              , Const.CLZ_2),
                           ('@'                                    , Const.CLZ_0),
                           (conf.host                              , Const.CLZ_3),
                           (':'                                    , Const.CLZ_0),
                           (conf.port                              , Const.CLZ_4),
                           (')'                                    , Const.CLZ_0, True)])

                self.cnx = ImapClient(conf.host,conf.port)
            except Exception as e :
                raise BadHostException()

            try :
                status, resp = self.cnx.login(conf.user,conf.pwd)

            except Exception as e :
                status = self.KO
                pass
            finally :
                if status == self.KO :
                    self.cnxusr = None
                    raise BadLoginException(' Cannot login with '+conf.user+':'+conf.pwd)
                else :
                    Sys.pwlog([(' Connected ', Const.CLZ_2, True),
                               (Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0, True)])
                    self.cnxusr = conf.user
                    try :
                        status, resp = self.cnx.select(self.rootBox)
                        if status == self.KO and not self.noBoxCreat:
                            self.createBox(self.rootBox)
                            status, resp = self.cnx.select(self.rootBox)
                        self.initBoxNames()
                    except Exception as e :
                        print(e)
        

    @Log()
    def createBox(self, box):
        """"""
        status, resp = self.cnx.create(encode(box))
        return status==self.OK


    @Log()
    def deleteBox(self, box):
        """"""
        status, resp = self.cnx.delete(encode(box))
        return status==self.OK


    @Log(Const.LOG_DEBUG)
    def initBoxNames(self):
        """"""
        status, resp = self.cnx.xlist()
        if status == self.OK :
            bdef, bname, c = None, None, None
            for c in resp :
                bdef, bname = c[1:-1].split(b') "/" "')
                if bdef == Io.bytes(self.NO_SELECT+' '+self.CHILDREN) :
                    self.BOXS['/'] = Io.str(bname)
                elif bdef == Io.bytes(self.NO_CHILDREN+' '+self.INBOX) :
                    self.BOXS[self.INBOX] = self.INBOX[1:].upper()
                elif bdef == Io.bytes(self.NO_CHILDREN+' '+self.DRAFTS) :
                    self.BOXS[self.DRAFTS] = Io.str(bname)
                elif bdef == Io.bytes(self.NO_CHILDREN+' '+self.TRASH) :
                    self.BOXS[self.TRASH] = Io.str(bname)
                elif bdef == Io.bytes(self.NO_CHILDREN+' '+self.SENT) :
                    self.BOXS[self.SENT] = Io.str(bname)
        else :
            self.BOXS = { '/' : '/', self.INBOX : self.INBOX[1:].upper(), self.DRAFTS : self.DRAFTS[1:], self.TRASH : self.TRASH[1:], self.SENT : self.SENT[1:] }


    @Log(Const.LOG_DEBUG)
    def listBox(self, box='INBOX', pattern='*'):
        """"""
        status, resp = self.cnx.list(box,pattern)
        l = []
        for r in resp :
            if  r is not None :
                name = Io.str(r).split(' "/" ')
                l.append((name[0][1:-1].split(' '),name[1][1:-1]))
        return l


    @Log(Const.LOG_DEBUG)
    def status(self, box='INBOX'):
        """"""
        status, resp = self.cnx.status(box, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        if status == self.OK :
            data = research(self.REG_SATUS, Io.str(resp[self.K_HEAD]))
            l    = resplit(' ',data.group(2))
            dic  = {'BOX' : box}
            for i in range(len(l)):
                if i%2 == 0 : dic[l[i]] = int(l[i+1])
        else : dic = {}
        return dic


    @Log()
    def countSeen(self, box='INBOX'):
        """"""
        s = self.status(box)
        return s['MESSAGES']-s['UNSEEN']


    @Log()
    def countUnseen(self, box='INBOX'):
        """"""
        return self.status(box)['UNSEEN']


    @Log()
    def countMsg(self, box='INBOX'):
        """"""
        return self.status(box)['MESSAGES']


    @Log(Const.LOG_DEBUG)
    def _ids(self, box='INBOX', search='ALL', charset=None, byUid=False):
        """"""
        status, resp = self.cnx.select(box)
        if status == self.KO :
            self.createBox(box)
            self.cnx.select(box)
        status, resp = self.cnx.search(charset, '(%s)' % search)
        return resplit(' ',Io.str(resp[self.K_HEAD]))


    @Log()
    def idsUnseen(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'UNSEEN', charset)


    @Log()
    def idsMsg(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'ALL', charset)


    @Log()
    def idsSeen(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'NOT UNSEEN', charset)


    @Log(Const.LOG_DEBUG)
    def search(self, query, byUid=False):
        """"""
        if byUid :
            status, resp = self.cnx.uid('search', None, query)
        else :
            status, resp = self.cnx.search(None, query)
        ids = [m for m in resp[0].split()]
        return ids


    @Log()
    def searchBySubject(self, subject, byUid=False):
        """"""
        return self.search('(SUBJECT "%s")' % subject, byUid)


    @Log()
    def getUid(self, mid):
        """"""
        value = ''
        status, resp = self.cnx.fetch(mid, '(UID)')
        if status==self.OK :
            # '$mid (UID $uid)'
            value = resp[0][len(str(mid))+6:-1]
        return value


    @Log(Const.LOG_DEBUG)
    def fetch(self, mid, query, byUid=False):
        """"""
        if not byUid :
            status, resp = self.cnx.fetch(mid, query)
        else:
            status, resp = self.cnx.uid('fetch', mid, query)
        return status, resp


    @Log()
    def headerField(self, mid, field, byUid=False):
        """"""
        value = ''
        field = field.upper()
        query = '(UID BODY[HEADER' + ('])' if field=='*' or field=='ALL' else '.FIELDS (%s)])' % field)
        status, resp = self.fetch(mid, query, byUid)
        if status==self.OK and resp[0]!=None:
            value = Io.str(resp[0][1][len(field)+2:-4])
        return value


    @Log()
    def getSubject(self, mid, byUid=False):
        """"""
        status, resp = self.fetch(mid, '(UID BODY[HEADER.FIELDS (SUBJECT)])', byUid)
        subject = decode_header(str(resp[self.K_HEAD][1][9:-4], 'utf-8'))[0]        
        s = subject[0]
        if subject[1] :
            s = str(s,subject[1])
        return s


    @staticmethod
    def _getIdsList(ids):
        idslist = None
        if isinstance(ids,list):
            if len(ids) > 0 and ids[0]!='' and ids[0]!=None:
                li = len(ids)-1
                if int(ids[0])+li == int(ids[li]):
                    idslist = Io.str(ids[0]+b':'+ids[li]) if isinstance(ids[0],bytes) else str(ids[0])+':'+str(ids[li])
                else :
                    idslist = Io.str(b','.join(ids)) if isinstance(ids[0],bytes) else ','.join(ids)
        elif isinstance(ids, int) and ids > 0:
            idslist = Io.str(ids)
        return idslist


    @Log()
    def delete(self, ids, byUid=False, expunge=True):
        """"""
        status, delids = None, ImapHelper._getIdsList(ids)
        #~ print(delids)
        if delids is not None :
            if byUid:
                status, resp = self.cnx.uid( 'store', delids, self.FLAGS, self.DELETED )
            else :
                status, resp = self.cnx.store(delids, self.FLAGS, self.DELETED)
            if expunge :
                self.cnx.expunge()
        return status == self.OK


    @Log()
    def clearTrash(self):
        """"""
        self.cnx.select(self.BOXS[self.TRASH])
        ids = self.search('ALL',True)
        if len(ids) > 0 and ids[0]!='' and ids[0]!=None:
            delids = ImapHelper._getIdsList(ids)            
            status, resp = self.cnx.uid('store', delids, self.FLAGS, self.DELETED )
            
            Sys.pwlog([(' Deleting msg ', Const.CLZ_0),
                       (delids                    , Const.CLZ_1),
                       (' '+status              , Const.CLZ_7, True)])
            self.cnx.expunge()
        self.cnx.select(self.rootBox)


    @Log()
    def getEmail(self, mid, byUid=False):
        """"""
        status, resp = self.fetch(mid,'(UID RFC822)', byUid)
        if status == self.OK and resp[0]!=None:
            msg = message_from_bytes(resp[0][1])
        else :
            msg = None
        return msg


    @Log(Const.LOG_APP)
    def getAttachment(self, msg, toDir='./', byUid=False):
        """"""
        # self.download(msg, toDir, byUid, False)
        # p = Process(target=self.download, args=(msg, toDir, byUid))
        # p.start()
        # p.join()
        if not isinstance(msg, Message) :
            msg = self.getEmail(msg, byUid)
        for part in msg.walk():
            filename = part.get_filename()
            if part.get_content_maintype() == 'multipart' or not filename : continue
            with Io.wfile(Sys.join(toDir, filename)) as fo :
                fo.write(part.get_payload(decode=True))
        

    @Log(Const.LOG_APP)
    def download(self, msg, toDir, byUid=False, reconError=True):
        """"""
        try:            
            if not isinstance(msg, Message) :
                msg = self.getEmail(msg, byUid)
            for part in msg.walk():
                filename = part.get_filename()
                if part.get_content_maintype() == 'multipart' or not filename : continue
                with Io.wfile(Sys.join(toDir, filename)) as fo :
                    fo.write(part.get_payload(decode=True))
        except Exception as e :
            print(e)
            self.reconnect()
            self.download(msg, toDir, byUid, False)


    @Log()
    def send(self, msg, box='INBOX'):
        """"""
        mid  = None
        date = Time2Internaldate(Sys.time())
        status, resp  = self.cnx.append(box, '\Draft', date, bytes(msg,'utf-8'))
        if status==self.OK:
            mid = str(resp[0],'utf-8')[11:-11].split(' ')
        return mid



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class BadLoginException ~~

class BadLoginException(BaseException):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class BadLoginException ~~

class BadHostException(BaseException):
    pass
