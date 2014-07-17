#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/core.py
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
# ~~ module core ~~

from random         import choice
from psr.sys        import Sys, Const, Io
from psr.log        import Log
from psr.imap       import ImapConfig, ImapHelper
from impra.index    import ImpraIndex, IndexUpdater, jdumps, jloads
from impra.ini      import KiniFile
from kirmah.crypt   import KeyGen, Kirmah, hash_sha256_file


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraConf ~~

class ImpraConf:
    """"""

    SEP_SECTION = '.'
    """"""

    def __init__(self, iniFile, defaultKeyLenght = 1024):
        """"""
        self.ini     = iniFile
        self.profile = self.ini.get('profile')  
        save = False
        if self.ini.isEmpty():
            save = True
            kg   = KeyGen(defaultKeyLenght)
            self.set('host' ,'host','imap')
            self.set('port' ,'993','imap')
            self.set('user' ,'login','imap')
            self.set('pass' ,'password','imap')
            self.set('box'  ,'__impra__','imap')
            self.set('key'  , kg.key,'keys')
            self.set('mark' , kg.mark,'keys')
            self.set('salt' ,'-¤-ImpraStorage-¤-','keys')
        if not self.ini.hasSection(self.profile+self.SEP_SECTION+'catg'):
            save = True
            try:
                self.set('users', self.get('name','infos'),'catg')
            except Exception : pass
            self.set('types', 'music,films,doc,images,archives,games','catg')
        
        if save :
            self.ini.save()


    def get(self, key, section='main', profile=None, defaultValue=None):
        """"""
        if profile == None : profile = self.profile
        v = defaultValue
        if self.ini.has(key,profile+self.SEP_SECTION+section):
            v = self.ini.get(key, profile+self.SEP_SECTION+section)
        return v


    def set(self, key, value, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        v = self.ini.set(key, value, profile+self.SEP_SECTION+section)
        self.ini.save()
        return v


    def sets(self, data, section='main', profile=None, save=True):
        """"""
        if profile == None : profile = self.profile
        v = []
        for vals in data:
            v.append(self.ini.set(vals[0], vals[1], profile+self.SEP_SECTION+(section if len(vals)==2 else vals[2])))
        if save : self.ini.save()
        return v

    
    def renameProfile(self, profile, toName, defaultProfile=False):
        """"""
        o, dic = [], self.ini.getSection(profile)
        for s in dic :
            o = []
            for key in dic[s] : 
                o.append([key, dic[s][key], s])
            self.sets(o, profile=toName, save=not defaultProfile)
        if defaultProfile :
            self.ini.set('profile', toName)
            self.ini.save()


    def rem(self, key, section='main', profile=None):
        """"""
        if profile == None : profile = self.profile
        v = self.ini.rem(key, profile+self.SEP_SECTION+section)
        self.ini.save()
        return v
    

    def remProfile(self, profile):
        """"""
        if profile is not None :
            print(self.ini.getSections())
            print('-'*10)
            s = self.ini.getSection(profile)
            d = s.copy()
            print(d)
            for section in d :
                print('    pop '+profile+self.SEP_SECTION+section)
                self.ini.dic.pop(profile+self.SEP_SECTION+section)
                for key in d[section] :
                    print('        '+key)
                    print('            ['+profile+self.SEP_SECTION+section+']')
                    self.ini.rem(key, profile+self.SEP_SECTION+section)
            self.ini.save()
        #~ return v


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraStorage ~~

class ImpraStorage:
    """"""    

    @Log(Const.LOG_BUILD)
    def __init__(self, conf, remIndex=False, wkdir='./', emit=None):
        """"""
        iconf           = ImapConfig(conf.get('host','imap'), conf.get('user', 'imap'), conf.get('pass', 'imap'), conf.get('port','imap'))
        self.rootBox    = conf.get('box', 'imap')
        self.emit       = emit        
        self.wkdir      = wkdir 
        self.idxu       = IndexUpdater(ImapHelper(iconf, self.rootBox), conf, self.wkdir, emit=emit)
        self.outbox     = self.wkdir + 'outbox/'
        self.inbox      = self.wkdir + 'inbox/'
        self.deploy     = self.wkdir + 'deploy/'    
        self.addmapPath = self.outbox+'.addmap'
        self.wkdir      = wkdir
        #~ impconf.renameProfile('default', 'gmail1', True)
        #~ impconf.ini.print()
        
    
    
    def SocketError(self):
        """"""
        return self.idxu.ih.cnx.abort
    
    def reconnect(self):
        """"""
        self.idxu.ih.reconnect()


    def backupAddMap(self, data):
        """"""
        Io.set_data(self.addmapPath, jdumps(data))
        call = ' '.join([Sys.executable, 'kirmah-cli.py', 'enc', '-qf', self.addmapPath, '-z', '-r', '-m', '-o', self.addmapPath+Kirmah.EXT, '-k', self.idxu.index.keyPath ])
        print(call)
        Sys.sysCall(call)
        Io.removeFile(self.addmapPath)


    def getBackupAddMap(self):
        """"""
        data = None
        if Io.file_exists(self.addmapPath+Kirmah.EXT) :
            call = ' '.join([Sys.executable, 'kirmah-cli.py', 'dec', '-qf', self.addmapPath+Kirmah.EXT, '-z', '-r', '-m', '-o', self.addmapPath, '-k', self.idxu.index.keyPath ])            
            print(call)
            Sys.sysCall(call)
            data = jloads(Io.get_data(self.addmapPath))
            Io.removeFile(self.addmapPath)
        return data


    def hasBackupAddMap(self):
        """"""
        return Io.file_exists(self.addmapPath+Kirmah.EXT)


    @Log(Const.LOG_DEBUG)
    def sendFile(self, data, retry=False):
        """"""
        done = None
        key  = None
        if data is not None :
            key , label, ext, count, catg, hlst, usr, ownerHash, sha256, size = data            
            self.idxu.index.addUser(usr, ownerHash)            
            account = self.idxu.switchFileAccount()            
            sendIds = []
            cancel  = False
            d       = None
            
            Sys.cli_emit_progress(0)
            Sys.sleep(0.2)
            if not retry:
                Sys.pwlog([(' Sending... '              , Const.CLZ_7),
                           (' ('                        , Const.CLZ_0),
                           (' ~'+Sys.readableBytes(Sys.getsize(self.outbox+hlst['data'][0][1]+Kirmah.EXT)), Const.CLZ_3),
                           (' per msg ) '               , Const.CLZ_0, True)])
            else :
                Sys.pwlog([(' Retry sending last file... '              , Const.CLZ_0),
                           (label+ext                                   , Const.CLZ_7),
                           (' ('+catg+')'                               , Const.CLZ_3 , True)])
            
            ignore = False
            
            for i, row in enumerate(hlst['data']):
                """"""
                if retry :
                    if not Io.file_exists(self.outbox+row[1]+Kirmah.EXT):                        
                        continue
                    elif not ignore:                        
                        Sys.pwlog([(' Ignoring file 1 to '+str(i), Const.CLZ_1, True)])
                        ignore = True

                d   = Sys.datetime.now()
                msg = self.idxu.mb.build(usr, 'all',  hlst['head'][2], self.outbox+row[1]+Kirmah.EXT)
                try :
                    mid = self.idxu.ih.send(msg.as_string(), self.rootBox)
                except Exception as e :
                    Sys.pwarn((('addFile : ',(str(e),Sys.CLZ_WARN_PARAM), ' !'),))
                    Sys.echo('waiting 5 s and retry')
                    Sys.sleep(5)
                    # force reconnect
                    self.impst.idxu.switchFileAccount(account, True)
                    # retry
                    mid = self.idxu.ih.send(msg.as_string(), self.rootBox)
                finally :    
                    if not mid is None :                    
                        status, resp = self.idxu.ih.fetch(mid[1],'(UID BODYSTRUCTURE)', True)
                        if status == self.idxu.ih.OK:
                            sendIds.append((mid[1],row))
                            Sys.pwlog([(' part '                          , Const.CLZ_0),
                                       (str(row[0]).rjust(2, '0')         , Const.CLZ_2),                        
                                       (' sent as msg '                   , Const.CLZ_0),
                                       (str(mid[1]).rjust(5, '0')         , Const.CLZ_1),
                                       (' ('                              , Const.CLZ_7),
                                       (str(int(row[4])+1).rjust(2, '0')  , Const.CLZ_2),
                                       ('/'                               , Const.CLZ_7),                
                                       (str(count)                        , Const.CLZ_3),
                                       (') in '                           , Const.CLZ_7),
                                       (Sys.getDelta(d)                   , Const.CLZ_4,True)])
                            
                            Sys.cli_emit_progress(int((i+1)*100/len(hlst['data'])))
                            
                            Sys.removeFile(self.outbox+row[1]+Kirmah.EXT)
                        else:
                            Sys.pwarn((('error occured when sending part ',(row[0], Sys.Clz.fgb3), ' !'),))

            diff = self.checkSendIds(sendIds,hlst['head'][2])
            if len(sendIds)==count or retry :
                self.idxu.get(True)
                self.idxu.index.add(key, label, hlst['head'][1], ext, ownerHash, catg, sha256, size, account)
                done = self.idxu.update()
                Io.removeFile(self.addmapPath+Kirmah.EXT)

            # resending missing parts
            else :
                Sys.pwarn((('TODO => must resending ',('missing',Sys.CLZ_WARN_PARAM), ' parts'),))
                print(diff)

            # clean 
            for mid, row in sendIds :                
                if Io.file_exists(self.outbox+row[1]+Kirmah.EXT) : Sys.removeFile(self.outbox+row[1]+Kirmah.EXT)
            if cancel : 
                delids = [ mid for mid, row in senids]
                print(delids)
                self.idxu.ih.delete(delids, True)
        return done, key


    @Log(Const.LOG_APP)
    def addFile(self, fromPath, label='', catg='', sendAddMap=False):
        """"""
        #~ Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0, True)])
        data    = self.buildFile(fromPath, label, catg) if not sendAddMap else self.getBackupAddMap()
        return self.sendFile(data)


    def getCountParts(self, fromPath):
        """"""
        fsize = Sys.getsize(fromPath)
        count = Sys.ceil(fsize/19710000)
        minp, maxp = 52, 62
        if   fsize < 4800000   : minp, maxp =  8, 16
        elif fsize < 22200000  : minp, maxp = 16, 22
        elif fsize < 48000000  : minp, maxp = 22, 32
        elif fsize < 222000000 : minp, maxp = 32, 42
        if count < minp :
            count = choice(list(range(minp,maxp)))
        if not count > 62 :
            return count 
        else : 
            raise Exception(fromPath+' size exceeds limits (max : '+formatBytes(self.ck.psize*62)+' ['+str(self.ck.psize*64)+' bytes])')


    @Log()
    def buildFile(self, fromPath, label='', catg='') :
        count   = self.getCountParts(fromPath)
        Sys.pwlog([(' Get Hash... '         , Const.CLZ_7, True)])
        sha256  = hash_sha256_file(fromPath)
        Sys.pwlog([(' hash : '              , Const.CLZ_0),
                   (sha256                  , Const.CLZ_2, True),
                   (' Build File...'        , Const.CLZ_0, True)])

        kg      = KeyGen(128)
        size    = Sys.getsize(fromPath)
        row     = self.idxu.index.get(sha256)
        if row is None :
            if label == '':
                label, ext = Sys.getFileExt(Sys.basename(fromPath))
            else :
                label, ext = Sys.getFileExt(label)
            if catg=='' :
                catg = self.idxu.index.getAutoCatg(ext)
            size          = Sys.getsize(fromPath)
            
            Sys.pwlog([(' Splitting '           , Const.CLZ_1),
                       (label                   , Const.CLZ_7),
                       (ext                     , Const.CLZ_7),
                       (' ('                    , Const.CLZ_0),
                       (Sys.readableBytes(size) , Const.CLZ_3),
                       (')'                     , Const.CLZ_0, True)])
            Sys.cli_emit_progress(0)
            Sys.sleep(0.2)
            km            = Kirmah(kg.key)
            km.DIR_OUTBOX = self.outbox
            # hlst genetate with sha256
            hlst          = km.ck.getHashList(sha256, int(count), True)
            usr           = self.idxu.conf.get('name','infos')
            ownerHash     = self.idxu.mb.getHashName(usr)            
            km.split(fromPath, hlst)
            Sys.pwlog([(' done '  , Const.CLZ_2, True)])
            row = [kg.key , label, ext, count, catg, hlst, usr, ownerHash, sha256, size]
            self.backupAddMap(row)

        else :
            
            Sys.pwlog([(' File Already exist ! '  , Const.CLZ_1, True),
                       (' id : '.rjust(10,' ')    , Const.CLZ_0),
                       (str(row[ImpraIndex.UID])  , Const.CLZ_1, True),
                       (' label : '.rjust(10,' ') , Const.CLZ_0),
                       (row[ImpraIndex.LABEL]     , Const.CLZ_3, True)])
            
            row = None
        return row 


    @Log()
    def checkSendIds(self, sendIds, subject):
        """"""
        lloc = [Io.bytes(str(data[0])) for mid, data in enumerate(sendIds)]
        lsrv = self.idxu.ih.searchBySubject(subject,True)
        return  [ int(i) for i in set(lloc).difference(set(lsrv))]


    @Log(Const.LOG_APP)
    def editFile(self, key, label, category):
        """"""
        #~ Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0, True)])
        done = False
        uid  = self.idxu._getId(True)
        uidx = self.idxu.conf.get('uid'  ,'index')
        if int(uid) != int(uidx) : self.idxu.get(True)
        row  = self.idxu.index.get(key)
        if row is not None:
            if row[ImpraIndex.LABEL]!=label or row[ImpraIndex.CATG]!=category:

                Sys.pwlog([(' Editing file '                                          , Const.CLZ_0),
                           (row[ImpraIndex.LABEL]                                     , Const.CLZ_7),
                           (' ['                                                      , Const.CLZ_0),
                           (row[ImpraIndex.CATG]                                      , Const.CLZ_4),
                           ('] to : '                                                 , Const.CLZ_0),
                           (label if label is not None else row[ImpraIndex.LABEL]     , Const.CLZ_3),
                           (' ['                                                      , Const.CLZ_0),
                           (category if category is not None else row[ImpraIndex.CATG], Const.CLZ_2),
                           (']'                                                       , Const.CLZ_0, True)])
                
                done = self.idxu.index.edit(key, label, category)
                
        Sys.pwlog([(' done' if done else 'ko', Const.CLZ_2 if done else Const.CLZ_1, True)])
        if done : 
            Sys.pwlog([(' Updating index...', Const.CLZ_0, True)])
            self.idxu.update()
        return done


    @Log(Const.LOG_APP)
    def getFile(self, uid):
        """"""
        #~ Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0, True)])
        done    = False
        key     = self.idxu.index.getById(uid)
        row     = self.idxu.index.get(key)
        filePath= None
        try :
            if row is not None :
                account = self.idxu.switchFileAccount(row[self.idxu.index.ACCOUNT])
                km      = Kirmah(row[self.idxu.index.KEY])
                hlst    = km.ck.getHashList(key, row[self.idxu.index.PARTS], True)
                ids     = self.idxu.ih.searchBySubject(hlst['head'][2], True)
                Sys.cli_emit_progress(0)
                Sys.sleep(0.2)
                Sys.pwlog([(' Downloading : '                                    , Const.CLZ_7),
                           (row[self.idxu.index.LABEL]+row[self.idxu.index.EXT]  , Const.CLZ_2),
                           (' ('                                                 , Const.CLZ_0),
                           (Sys.readableBytes(row[self.idxu.index.SIZE])         , Const.CLZ_3),
                           (')'                                                  , Const.CLZ_0),
                           (' please wait...'                                    , Const.CLZ_7, True)])
                
                if len(ids) >= row[self.idxu.index.PARTS]:
                    self.getFileParts(row, ids)
                    
                    Sys.pwlog([(' Merging parts...', Const.CLZ_7, True)])
                    Sys.cli_emit_progress(0)
                    Sys.sleep(0.2)
                    filePath = km.merge(hlst, self.deploy+row[self.idxu.index.CATG]+Sys.sep+row[self.idxu.index.LABEL], ext=row[self.idxu.index.EXT], uid=row[self.idxu.index.UID], dirs=self.inbox)
                    
                    
                    Sys.pwlog([(' Deployed as '                          , Const.CLZ_7),
                               (filePath                                 , Const.CLZ_2),
                               (' ('                                     , Const.CLZ_0),
                               (Sys.readableBytes(Sys.getsize(filePath)) , Const.CLZ_3),
                               (') '                                     , Const.CLZ_0, True),
                               (' Checking integrity...'                 , Const.CLZ_7, True)])
                    Sys.sleep(0.2)
                    sha256  = hash_sha256_file(filePath)
                    done    = sha256==row[ImpraIndex.HASH]
                    done = True    

                else:
                    print('incomplete')
                    
        except Exception as e :
            print(e)
        Sys.pwlog([(' done' if done else 'ko', Const.CLZ_2 if done else Const.CLZ_1, True)])
        return done, filePath


    def getFileParts(self, row, ids):
        """"""
        done = False
        if len(ids) >= row[self.idxu.index.PARTS]:
            for i, uid in enumerate(ids):
                d   = Sys.datetime.now()                    
                self.idxu.ih.getAttachment(uid, self.inbox, True)
                
                Sys.pwlog([(' part '                , Const.CLZ_0),
                           (str(i+1).rjust(2, ' ')  , Const.CLZ_2),
                           (' / '                   , Const.CLZ_0),
                           (str(len(ids))           , Const.CLZ_3),
                           (' downloaded in '       , Const.CLZ_0),
                           (Sys.getDelta(d)         , Const.CLZ_4, True)])

                Sys.cli_emit_progress(int((i+1)*100/len(ids)))
                Sys.sleep(0.5)
                
            Sys.mkdir_p(self.deploy+row[self.idxu.index.CATG])
            Sys.cli_emit_progress(100)
            

    @Log(Const.LOG_APP)
    def getInfo(self, uid):
        """"""
        done    = False
        key     = self.idxu.index.getById(uid)
        row     = self.idxu.index.get(key)
        if row is not None :
            account = self.idxu.switchFileAccount(row[self.idxu.index.ACCOUNT])
            km      = Kirmah(row[self.idxu.index.KEY])
            hlst    = km.ck.getHashList(key, row[self.idxu.index.PARTS], True)
            
            Sys.pwlog([('id '.rjust(14,' ')+': '                                    , Const.CLZ_0),
                       (str(row[ImpraIndex.UID])                                    , Const.CLZ_1, True),
                       ('hash '.rjust(14,' ')+': '                                  , Const.CLZ_0),
                       (row[ImpraIndex.HASH]                                        , Const.CLZ_2, True),
                       ('name '.rjust(14,' ')+': '                                  , Const.CLZ_0),
                       (row[ImpraIndex.LABEL]+row[ImpraIndex.EXT]                   , Const.CLZ_7, True),
                       ('size '.rjust(14,' ')+': '                                  , Const.CLZ_0),
                       (Sys.readableBytes(row[ImpraIndex.SIZE])                     , Const.CLZ_6, True),
                       ('category '.rjust(14,' ')+': '                              , Const.CLZ_0),
                       (row[ImpraIndex.CATG]                                        , Const.CLZ_5, True),
                       ('user '.rjust(14,' ')+': '                                  , Const.CLZ_0),
                       (self.idxu.index.getUser(row[ImpraIndex.USER])               , Const.CLZ_3),
                       (' ('+row[ImpraIndex.USER]+')'                               , Const.CLZ_5, True),
                       ('account '.rjust(14,' ')+': '                               , Const.CLZ_0),
                       (self.idxu.conf.get('user' , 'imap', row[ImpraIndex.ACCOUNT]), Const.CLZ_4, True),
                       (Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN                      , Const.CLZ_0, True),
                       ('subject '.rjust(14,' ')+': '                               , Const.CLZ_0),
                       (hlst['head'][2]                                             , Const.CLZ_1, True)])

            ids     = self.idxu.ih.searchBySubject(hlst['head'][2], True)
            
            for i, uid in enumerate(ids):
                if i < len(hlst['data']) :
                    
                    Sys.pwlog([('attach file '.rjust(14,' ')+': '       , Const.CLZ_0),
                               (hlst['data'][i][1]+Kirmah.EXT           , Const.CLZ_2),
                               (' ('                                    , Const.CLZ_0),
                               (str(int(uid))                           , Const.CLZ_1),
                               (') ('                                   , Const.CLZ_0),
                               (str(hlst['data'][i][4])                 , Const.CLZ_3),
                               (')'                                     , Const.CLZ_0, True)])
                else:
                    Sys.pwlog([(' Wrong id (to del)'.ljust(14,' ')+': ' , Const.CLZ_2),
                               (str(uid)                                , Const.CLZ_2, True)])
        return done


    @Log(Const.LOG_APP)
    def removeFile(self, uid):
        """"""
        #~ Sys.pwlog([(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN , Const.CLZ_0, True)])
        done    = False
        key     = self.idxu.index.getById(uid)
        row     = self.idxu.index.get(key)
        if row is not None:
            account = self.idxu.switchFileAccount(row[self.idxu.index.ACCOUNT])
            Sys.pwlog([(' Removing... plz wait. '     , Const.CLZ_7)])
            km      = Kirmah(row[self.idxu.index.KEY])
            hlst    = km.ck.getHashList(key, row[self.idxu.index.PARTS], True)
            ids     = self.idxu.ih.searchBySubject(hlst['head'][2], True)
            self.idxu.ih.delete(ids, True, True)
            self.idxu.ih.clearTrash()
            self.idxu.switchFileAccount(self.idxu.conf.profile)
            self.idxu.get(True)
            self.idxu.index.rem(key)
            done = self.idxu.update()
        return done, key
