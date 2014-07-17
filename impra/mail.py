#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/mail.py
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
# ~~ module mail ~~
from binascii               import b2a_base64
from email.encoders         import encode_base64
from email.header           import Header
from email.mime.base        import MIMEBase
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
from email.utils            import formatdate
from psr.log                import Log
from psr.sys                import Io, Sys, Const
from kirmah.crypt           import hash_sha256

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class MailBuilder ~~

class MailBuilder:
    """A simple mail builder to create mails for ImpraIndex and parts attAchments"""

    DOMAIN_NAME = 'impra.storage'
    """Domain name used for from and to mail fields"""

    @Log(Const.LOG_BUILD)
    def __init__(self, salt=''):
        """"""
        self.salt = salt


    @Log(Const.LOG_DEBUG)    
    def getHashName(self, name):
        """Return a simplified hash of specified name
        :Returns: `str`
        """
        return hash_sha256(self.salt+name)[0:12]


    @Log()
    def build(self, nameFrom, nameTo, subject, filePath):
        """Build mail with attachment part
        :Returns: 'email.message.Message'
        """
        msg = MIMEMultipart()
        msg['From']    = self.getHashName(nameFrom)+'@'+self.DOMAIN_NAME
        msg['To']      = self.getHashName(nameTo)+'@'+self.DOMAIN_NAME
        msg['Date']    = formatdate(localtime=True)
        msg['Subject'] = Header(subject,'utf-8')        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(filePath, 'rb').read())
        encode_base64(part)
        part.add_header('Content-Disposition','attachment; filename="%s"' % Sys.basename(filePath))
        msg.attach(part)
        return msg


    @Log()
    def buildIndex(self, fromPath):
        """Build mail for ImpraIndex
        :Returns: 'email.message.Message'
        """
        msg = MIMEText(Io.str(b2a_base64(Io.get_data(fromPath, True))), 'plain', 'utf-8')
        msg['From']    = self.getHashName('system')+'@'+self.DOMAIN_NAME
        msg['To']      = self.getHashName('all')+'@'+self.DOMAIN_NAME
        msg['Date']    = formatdate(localtime=True)
        msg['Subject'] = Header(self.getHashName('index'),'utf-8')      
        return msg
