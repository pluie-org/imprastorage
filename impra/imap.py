#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : ImpraStorage <http://imprastorage.sourceforge.net/>             #
#   version   : 0.4                                                             #
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
# ~~ package imap ~~

from email            import message_from_bytes
from email.header     import decode_header
from email.message    import Message
from imaplib          import IMAP4_SSL, Time2Internaldate
from os.path          import join
from re               import search, split
from time             import time
from impra.util       import __CALLER__, RuTime, bstr, stack
from binascii         import b2a_base64, a2b_base64
from codecs           import register, StreamReader, StreamWriter


def _seq_encode(seq,l):
    """"""
    if len(seq) > 0 :
        l.append('&%s-' % str(b2a_base64(bytes(''.join(seq),'utf-16be')),'utf-8').rstrip('\n=').replace('/', ','))
    elif l: 
        l.append('-')

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

def encoder(s):
    """"""
    e = bytes(encode(s),'utf-8')
    return e, len(e)

def _seq_decode(seq,l):
    """"""
    d = ''.join(seq[1:])
    pad = 4-(len(d)%4)
    l.append(str(a2b_base64(bytes(d.replace(',', '/')+pad*'=','utf-16be')),'utf-16be'))

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

def decoder(s):
    """"""
    d = decode(str(s,'utf-8'))
    return d, len(d)

def _codec_imap4utf7(name):
    """"""
    if name == 'imap4-utf-7':
        return (encoder, decoder, Imap4Utf7StreamReader, Imap4Utf7StreamWriter)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Imap4Utf7StreamWriter ~~

class Imap4Utf7StreamReader(StreamReader):
    """"""
    
    def decode(self, s, errors='strict'):
        """"""
        return decoder(s)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Imap4Utf7StreamWriter ~~

class Imap4Utf7StreamWriter(StreamWriter):
    """"""
    
    def decode(self, s, errors='strict'):
        """"""
        return encoder(s)


register(_codec_imap4utf7)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImapConfig ~~

class ImapConfig:
    """"""
    
    def __init__(self, host, port, user, pwd):
        """"""
        self.host = host
        self.port = port
        self.user = user
        self.pwd  = pwd


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
    REG_SATUS    = r'^"(\w*)" \(([^\(]*)\)'
    """"""
    NO_SELECT    = '\\Noselect'
    """"""
    CHILDREN     = '\\HasChildren'
    """"""
    NO_CHILDREN  = '\\HasNoChildren'
    """"""
    BOX_BIN      = '[Gmail]/Corbeille'
    """"""

    def __init__(self, conf, box='INBOX'):
        """"""
        rt = RuTime(eval(__CALLER__('conf,"'+box+'"')))
        self.srv = IMAP4_SSL(conf.host,conf.port)
        self.srv.login(conf.user,conf.pwd)
        self.rootBox = box
        status, resp = self.srv.select(self.rootBox)
        if status == self.KO :
            self.createBox(self.rootBox)
            self.srv.select(self.rootBox)
        rt.stop()

    def status(self,box='INBOX'):
        """"""
        status, resp = ih.srv.status(box, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        if status == 'OK' :
            data = search(self.REG_SATUS,bstr(resp[self.K_HEAD]))
            l = split(' ',data.group(2))
            dic = {'BOX' : data.group(1)}
            for i in range(len(l)): 
                if i%2 == 0 : dic[l[i]] = int(l[i+1])
        else : dic = {}
        return dic

    def countSeen(self, box='INBOX'):
        """"""
        s = self.status(box)
        return s['MESSAGES']-s['UNSEEN']

    def countUnseen(self, box='INBOX'):
        """"""
        return self.status(box)['UNSEEN']

    def countMsg(self, box='INBOX'):
        """"""
        return self.status(box)['MESSAGES']

    def _ids(self, box='INBOX', search='ALL', charset=None, byUid=False):
        """"""
        status, resp = self.srv.select(box)
        if status == self.KO :
            self.createBox(box)
            self.srv.select(box)
        status, resp = self.srv.search(charset, '(%s)' % search)
        return split(' ',bstr(resp[self.K_HEAD]))

    def idsUnseen(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'UNSEEN', charset)

    def idsMsg(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'ALL', charset)

    def idsSeen(self, box='INBOX', charset=None):
        """"""
        return self._ids(box,'NOT UNSEEN', charset)

    def listBox(self, box='INBOX', pattern='*'):
        """"""
        status, resp = self.srv.list(box,pattern)
        l = []
        for r in resp :
            name = bstr(r).split(' "/" ')
            l.append((name[0][1:-1].split(' '),decode(name[1][1:-1])))
        return l

    def createBox(self, box):
        """"""
        rt = RuTime(eval(__CALLER__(box)))
        status, resp = self.srv.create(encode(box))
        rt.stop()
        return status==self.OK

    def deleteBox(self, box):        
        """"""
        rt = RuTime(eval(__CALLER__(box)))
        status, resp = self.srv.delete(encode(box))
        rt.stop()
        return status==self.OK

    def subject(self, mid, byUid=False):
        """"""
        status, resp = self.fetch(mid, '(UID BODY[HEADER.FIELDS (SUBJECT)])', byUid)
        subject = decode_header(str(resp[self.K_HEAD][1][9:-4], 'utf-8'))[0]
        s = subject[0]
        if subject[1] :
            s = str(s,subject[1])
        return s

    def search(self, query, byUid=False):
        if byUid : 
            status, resp = self.srv.uid('search', None, query)
        else :
            status, resp = self.srv.search(None, query)
        ids = [m for m in resp[0].split()]        
        return ids
    
    def searchBySubject(self, subject, byUid=False):
        return self.search('(SUBJECT "%s")' % subject, byUid)

    def getUid(self, mid):
        """"""
        value = ''
        status, resp = self.srv.fetch(mid, '(UID)')
        if status==self.OK :
            value = resp[0][len(str(mid))+3:-1]        
        return value
    
    def fetch(self, mid, query, byUid=False):
        """"""
        if not byUid :
            status, resp = self.srv.fetch(mid, query)
        else:
            status, resp = self.srv.uid('fetch', mid, query)
        return status, resp

    def headerField(self, field, mid, byUid=False):
        """"""
        value = ''
        status, resp = self.fetch(mid, '(UID BODY[HEADER.FIELDS (%s)])' % field.upper(), byUid)
        if status==self.OK and resp[0]!=None:
            value = str(resp[0][1][len(field)+2:-4],'utf-8')
        return value

    def email(self, mid, byUid=False):
        """"""
        status, resp = self.fetch(mid,'(UID RFC822)', byUid)
        if status == self.OK and resp[0]!=None:
            msg = message_from_bytes(resp[0][1])
        else : 
            msg = None
        return msg

    def deleteBin(self):
        """"""
        from impra.util import DEBUG_NOTICE, DEBUG, DEBUG_LEVEL
        rt = RuTime(eval(__CALLER__()))
        self.srv.select(self.BOX_BIN)
        ids = self.search('ALL',True)        
        if len(ids) > 0 and ids[0]!='' and ids[0]!=None:
            #print(str(ids[0],'utf-8').split())
            for mid in ids:                
                #~ uid = bytes(mid)
                #~ print(type(mid))
                #~ print(mid)
                #status, resp = self.srv.store(mid, '+FLAGS', '\\Deleted')
                status, resp = self.srv.uid('store', mid, '+FLAGS', '\\Deleted' )
                
                if DEBUG and DEBUG_LEVEL <= DEBUG_NOTICE:
                    print('deleting msg '+str(mid))
                    print(status)
                    print(resp)
            self.srv.expunge()
        self.srv.select(self.rootBox)  
        rt.stop()
        
    def delete(self, mid, byUid=False):
        """"""
        rt = RuTime(eval(__CALLER__('%i' % int(mid))))
        status = None
        if int(mid) > 0 :
            if byUid:
                status, resp = self.srv.uid( 'store', mid, '+FLAGS', '\\Deleted' )
            else :
                status, resp = self.srv.store(mid, '+FLAGS', '\\Deleted')
            self.srv.expunge()
        rt.stop()
        return status == self.OK

    def downloadAttachment(self, msg, toDir='./'):
        """"""
        from impra.util import DEBUG, DEBUG_LEVEL, DEBUG_NOTICE, DEBUG_INFO
        rt = RuTime(eval(__CALLER__('%i' % int(msg))),DEBUG_INFO)
        if not isinstance(msg, Message) :
            msg = self.email(msg)
        for part in msg.walk():
            filename = part.get_filename()
            if filename != None and DEBUG and DEBUG_LEVEL <= DEBUG_NOTICE : print(filename)
            if part.get_content_maintype() == 'multipart' or not filename : continue
            fp = open(join(toDir, filename), 'wb')
            #print(part.get_payload(decode=True)[::-1])
            fp.write(part.get_payload(decode=True))
            fp.close()
        rt.stop()

    def send(self, msg, box='INBOX'):
        """"""
        from impra.util import DEBUG_INFO
        rt   = RuTime(eval(__CALLER__()),DEBUG_INFO)
        mid  = None
        date = Time2Internaldate(time())
        status, resp  = self.srv.append(box, '\Draft', date, bytes(msg,'utf-8'))
        if status==self.OK:
            mid = str(resp[0],'utf-8')[11:-11].split(' ')
        rt.stop()
        return mid

if __name__ == '__main__':
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    iconf  = ImapConfig("imap.gmail.com", 993, 'gpslot.001', '__gpslot#22')
    ih     = ImapHelper(iconf,'__SMILF')
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print('\n--------------------------------------------------------------------')
    print('-- STATUS DEFAULT BOX --')
    print(str(ih.status()))
    print('-- STATUS BOX __SMILF --')
    print(str(ih.status('__SMILF')))
    print('-- UNSEEN COUNT --')
    print(str(ih.countUnseen('__SMILF')))
    print('-- SEEN COUNT --')
    print(str(ih.countSeen('__SMILF')))
    print('-- MESSAGE COUNT --')
    print(str(ih.countMsg('__SMILF')))
    print('-- UNSEEN IDS --')
    print(ih.idsUnseen('__SMILF'))
    print('-- MESSAGES IDS --')
    print(ih.idsMsg('__SMILF'))
    print('-- SEEN IDS --')
    lunseen = ih.idsSeen('__SMILF')
    print(lunseen)
    print('-- LIST BOX --')
    lb = ih.listBox('')
    print(lb[5][1])
    print('-- SUBJECT ID 1 --')
    print(ih.subject(lunseen[0]))
    print('-- BODY ID 1 --')
    #print(ih.body(lunseen[0]))
    print('-- EMAIL ID 1 --')
    # 'partial', ('1', 'RFC822', 1, 1024)),
    #status, resp = ih.srv.fetch(lunseen[0],'(UID RFC822)')
    #status, resp = ih.srv.fetch('4','(UID body[header.fields (from to subject date)])')
    #status, resp = ih.srv.fetch(lunseen[1],'(UID RFC822.SIZE)')
    #status, resp = ih.srv.fetch(lunseen[1],'(UID RFC822.HEADER)')
    #status, resp = ih.srv.fetch(lunseen[1],'(UID BODYSTRUCTURE)')
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #msg = ih.email(lunseen[0])
    #print(type(msg))
    #print(msg)
    #print('-- ATTACHMENT ID 1 --')
    #ih.downloadAttachment(lunseen[0])


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ['MIME-Version', 'Received', 'Date', 'Message-ID', 'Subject', 'From', 'To', 'Content-Type']
    print('-- CREATE BOX __SMILF/böx --')
    print(ih.createBox("__SMILF/böx"))
    print('-- DELETE BOX böx --')
    print(ih.deleteBox("böx"))
    #~ OK
    #~ [b'Success']
    #~ True
    #~ NO
    #~ [b'[ALREADYEXISTS] Duplicate folder name b\xc3\xb6x (Failure)']
    #~ True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
