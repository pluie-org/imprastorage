#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/cliapp.py
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
# ~~ module cliapp ~~

import  impra.conf      as conf
from    impra.core      import ImpraStorage, ImpraConf
from    impra.ini       import KiniFile
from    kirmah.crypt    import Kirmah, BadKeyException, KeyGen, represents_int, KeyGen, represents_int
from    psr.sys         import Sys, Const, Io
from    psr.log         import Log
from    psr.imap        import BadHostException, BadLoginException


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class CliApp ~~

class CliApp:

    @Log(Const.LOG_BUILD)
    def __init__(self, home, path, parser, Cli, a, o):
        """"""
        self.parser  = parser
        self.Cli     = Cli
        self.a       = a
        self.o       = o
        self.home    = home
        self.stime   = Sys.datetime.now()
        self.account = 'default'
        self.rootBox = '__impra__2'
        self.uid     = '0'
        self.date    = ''
        if not Io.file_exists('impra2.ini'+Kirmah.EXT):
            print('ini file not exist')
            if len(self.a)>0 and self.a[0]=='conf' and self.o.save :
                kg = KeyGen()
                Io.set_data('impra2.ini.key', kg.key)
                self.ini = KiniFile('impra2.ini')
                self.ini.set('key' , kg.key               , self.account+'.keys')
                self.ini.set('mark', kg.mark              , self.account+'.keys')
                self.ini.set('salt', '-¤-ImpraStorage-¤-' , self.account+'.keys')                
            else :
                self.needConfig()
                
        else :
            if not (len(self.a)>0 and self.a[0]=='conf') :
                self.ini     = KiniFile('impra2.ini')                
                self.impst   = ImpraStorage(ImpraConf(self.ini),wkdir=path)
                self.uid     = self.impst.idxu.conf.get('uid' ,'index')
                self.date    = self.impst.idxu.conf.get('date','index')
                self.account = self.impst.idxu.conf.get('user','imap')
                self.rootBox = self.impst.rootBox
                if self.impst.idxu.index != None:
                    noData = self.impst.idxu.index.isEmpty()
                    if self.uid  == None or noData : self.uid  = 'EMPTY'
                    if self.date == None or noData : self.date = ''
            else :
                self.ini = KiniFile('impra2.ini')


    @Log(Const.LOG_ALL)
    def pheader(self):
        self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        self.Cli.printHeaderTitle(self.Cli.conf.PRG_CLI_NAME)
        self.Cli.printHeaderPart('account', self.account)
        self.Cli.printHeaderPart('index'  , self.uid)
        self.Cli.printHeaderPart('box'    , self.rootBox)
        Sys.echo(self.date, Sys.Clz.fgB7, True, True)
        self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)


    @Log()
    def getMatchKey(self):
        key = None
        if not len(self.a)>1 :
            self.parser.error_cmd((a[0]+' command need an id',), True)
        else:
            if not represents_int(self.a[1]):
                self.parser.error_cmd((('not a valid id : ',(self.a[1], Sys.CLZ_ERROR_PARAM)),), False)
            else : 
                vid = self.a[1]
                key = self.impst.idxu.index.getById(vid)
                if key is None :
                    self.parser.error_cmd(((' not a valid id : ',(self.a[1], Sys.CLZ_ERROR_PARAM)),), False)
        return key


    @Log(Const.LOG_DEBUG)
    def onCommandAdd(self):
        """"""
        if not len(self.a)>1 :
            self.parser.error_cmd((self.a[0]+' command need one argument',), True)
        else:
            vfile = self.a[1]
            if not Io.file_exists(vfile) :
                if Sys.isdir(vfile):
                    for f in Sys.listdir(vfile):
                        if not Sys.isdir(f):
                            label, ext  = Sys.getFileExt(Sys.basename(f))
                            if self.o.category is None : self.o.category = ''
                            done = self.impst.addFile(vfile+Sys.sep+f, label , self.o.category)
                            if done :
                                self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                                Sys.dprint(' ', end='')
                                Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
                                Sys.dprint()
                else :
                    self.parser.error_cmd((self.a[0]+' is not a file or a directory',), True)
            else:
                if not len(self.a)>2 :
                    label = Sys.basename(vfile)
                else: label = self.a[2]
                if self.o.category is None : self.o.category = ''
                Sys.clear()
                self.pheader()
                done = self.impst.addFile(vfile,label,self.o.category)
                if done :
                    self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                    Sys.dprint(' ', end='')
                    Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
                    Sys.dprint()
                else :
                    self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                    Sys.dprint(' ', end='')
                    Sys.echo(' == KO == ', Sys.Clz.bg1+Sys.Clz.fgb7)
                    Sys.dprint()


    @Log(Const.LOG_DEBUG)
    def needConfig(self):
        Sys.clear()
        self.pheader()
        Sys.echo(' '*4+'ImpraStorage has no configuration file !!', Sys.Clz.fgB1)
        Sys.dprint()
        Sys.echo(' '*8+'# to create the config file you must use this command with appropriate values :',Sys.Clz.fgn7)
        Sys.echo(' '*8+'# type command help for details',Sys.Clz.fgn7)
        Sys.echo(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.echo('conf ', Sys.Clz.fgB3, False)
        Sys.echo('-S ', Sys.Clz.fgB3, False)
        Sys.echo('profileName ', Sys.Clz.fgB1, False)
        Sys.echo('-N ', Sys.Clz.fgB3, False)
        Sys.echo('yourName ', Sys.Clz.fgB1, False)        
        Sys.echo('-K -H ', Sys.Clz.fgB3, False)
        Sys.echo('accountHost ', Sys.Clz.fgB1, False)
        Sys.echo('-P ', Sys.Clz.fgB3, False)
        Sys.echo('993 ', Sys.Clz.fgB1, False)
        Sys.echo('-U ', Sys.Clz.fgB3, False)
        Sys.echo('accountName ', Sys.Clz.fgB1, False)
        Sys.echo('-X ', Sys.Clz.fgB3, False)
        Sys.echo('accountPassword ', Sys.Clz.fgB1)
        Sys.dprint()
        Sys.exit(1)


    @Log(Const.LOG_DEBUG)
    def onCommandConf(self):
        """"""
        if self.o.load is not None or self.o.view is not None or self.o.save is not None :
            
            if self.o.view is not None :
                self.o.active_profile = self.o.view
            if self.o.load is not None :
                self.o.active_profile = self.o.load
            if self.o.save is not None :
                self.o.active_profile = self.o.save
            
            if self.o.active_profile==None: 
                if self.ini.has('profile') : self.o.active_profile = self.ini.get('profile')
                else : self.o.active_profile = 'default'
            
            if self.o.load : 
                self.pheader()
                self.load_profile()

            elif self.o.view :
                self.pheader()
                if self.o.view == 'all' :
                    sections = self.ini.getSections()
                    if len(sections) > 0:
                        ap  = self.ini.get('profile')
                        sep = ''
                        for p in sections:
                            if p == ap : 
                                colr = Sys.Clz.fgB1
                                p = '*'+p
                            else : colr = Sys.Clz.fgB3                                        
                            Sys.echo(sep+p, colr, False)
                            if sep=='':sep=','
                        Sys.dprint()
                    else : Sys.echo(' no profiles', Sys.Clz.fgB1)
                else: 
                    print(self.ini.get('profile'))
                    self.ini.print(self.o.view)

            elif self.o.save :
                self.pheader()
                if not self.o.set_host and not self.o.set_user and not self.o.set_pass and not self.o.set_port and not self.o.set_boxname and not self.o.set_name and not self.o.gen_key and not self.o.set_multi and not self.o.remove_multi:
                    self.parser.error(' no options specified')
                else :
                    if self.o.set_port and not represents_int(self.o.set_port):
                        self.parser.error(' port must be a number')
                        self.exit(1)
                    else :
                        if self.o.set_boxname: self.ini.set('box'  , self.o.set_boxname, self.o.active_profile+'.imap')
                        if self.o.set_host   : self.ini.set('host' , self.o.set_host   , self.o.active_profile+'.imap')
                        if self.o.set_user   : self.ini.set('user' , self.o.set_user   , self.o.active_profile+'.imap')
                        if self.o.set_pass   : self.ini.set('pass' , self.o.set_pass   , self.o.active_profile+'.imap')
                        if self.o.set_port   : self.ini.set('port' , self.o.set_port   , self.o.active_profile+'.imap')                    
                        if self.o.set_name   : self.ini.set('name' , self.o.set_name   , self.o.active_profile+'.infos')
                        
                        if self.ini.has('multi',self.o.active_profile+'.imap'):
                            m = self.ini.get('multi',self.o.active_profile+'.imap')
                        else : m = None
                        if m is None : m = []
                        else : m = m.split(',')
                        m = [x for x in m if x]
                        if self.o.set_multi  :
                            if self.check_imap(self.o.set_multi):
                                if not self.o.set_multi in m :m.append(self.o.set_multi)
                            else:
                                Sys.dprint()
                                Sys.echo('imap profile '+self.o.set_multi+' not found', Sys.Clz.fgB1)
                                Sys.dprint()
                        elif self.o.remove_multi and self.o.remove_multi in m : m.remove(self.o.remove_multi)              
                        self.ini.set('multi', ','.join(m), self.o.active_profile+'.imap')
                        
                        if self.o.gen_key:
                            kg = KeyGen()
                            self.ini.set('key' , kg.key               , self.o.active_profile+'.keys')
                            self.ini.set('mark', kg.mark              , self.o.active_profile+'.keys')
                            self.ini.set('salt', '-¤-ImpraStorage-¤-' , self.o.active_profile+'.keys')
                        if self.check_profile(self.o.active_profile):
                            self.ini.set('profile', self.o.active_profile)
                        if not self.o.set_boxname and not self.ini.has('box', self.o.active_profile+'.imap') :
                            self.ini.set('box'  , self.rootBox, self.o.active_profile+'.imap')
                        self.ini.save()
                        self.ini.print(self.o.active_profile)
                        
        elif self.o.check :
            self.pheader()
            self.check_profile(self.o.check, True)

        else :
            self.parser.print_usage('')


    @Log(Const.LOG_DEBUG)
    def check_imap(self, profile):
        """"""
        return self.ini.has('host',profile+'.imap') and self.ini.has('user',profile+'.imap') and self.ini.has('pass',profile+'.imap') and self.ini.has('port',profile+'.imap')


    @Log(Const.LOG_DEBUG)
    def check_profile(self, profile, activeCheck=False):
        """"""
        c = self.ini.hasSection(profile+'.keys') and self.check_imap(profile) and self.ini.has('name',profile+'.infos')
        if activeCheck :
            if c :
                Sys.echo(' '+profile+' is ok', Sys.Clz.fgB2)
                Sys.echo(' testing...'       , Sys.Clz.fgB3)
                kini  = self.ini
                conf  = ImpraConf(kini, profile)
                impst = None
                try:                        
                    impst = ImpraStorage(self.ini.path, False)
                    Sys.echo(' done', Sys.Clz.fgB2)
                except BadHostException as e :
                    Sys.echo(' fail ! bad host or port !', Sys.Clz.fgB1)
                    pass
                    
                except BadLoginException as e:
                    Sys.echo(str(e)   , Sys.Clz.fgN1)
                    Sys.echo(' fail ! bad login or password !'  , Sys.Clz.fgB1)
                    pass
                except Exception as e:
                    Sys.echo(' fail ! check your configuration !'  , Sys.Clz.fgB1)
                    pass                    
                    
            else :
                Sys.echo(' profile `'              , Sys.Clz.fgB1, False)
                Sys.echo(profile                   , Sys.Clz.fgB3, False)
                Sys.echo('` is incomplete\n need :', Sys.Clz.fgB1)
                if not self.ini.hasSection(profile+'.keys'):
                    Sys.echo(' '*4+'key'.ljust(18,' ')+' (conf -S "'+profile+'" -K)', Sys.Clz.fgB3)
                if not self.ini.has('host',profile+'.imap'):
                    Sys.echo(' '*4+'imap host'.ljust(18,' ')+' (conf -S "'+profile+'" -H hostName)', Sys.Clz.fgB3)
                if not self.ini.has('user',profile+'.imap'):
                    Sys.echo(' '*4+'imap user'.ljust(18,' ')+' (conf -S "'+profile+'" -U accountName)', Sys.Clz.fgB3)
                if not self.ini.has('pass',profile+'.imap'):
                    Sys.echo(' '*4+'imap password'.ljust(18,' ')+' (conf -S "'+profile+'" -X password)', Sys.Clz.fgB3)
                if not self.ini.has('port',profile+'.imap'):
                    Sys.echo(' '*4+'imap port'.ljust(18,' ')+' (conf -S "'+profile+'" -P port)', Sys.Clz.fgB3)
            if not self.ini.has('name',profile+'.infos'):
                if c :
                    Sys.echo(' think to add your userName :',Sys.Clz.bgB3)
                Sys.echo(' '*4+'userName'.ljust(18,' ')+' (conf -S "'+profile+'" -N yourName)', Sys.Clz.fgB3)    
        return c 


    @Log(Const.LOG_DEBUG)
    def load_profile(self):
        """"""        
        if self.check_profile(self.o.active_profile):
            Sys.dprint(' ',end=' ')
            Sys.echo(' == profile `'      , Sys.Clz.bg2+Sys.Clz.fgb7, False)
            Sys.echo(self.o.active_profile, Sys.Clz.bg2+Sys.Clz.fgB3, False)
            Sys.echo('` loaded == '       , Sys.Clz.bg2+Sys.Clz.fgb7)
            Sys.dprint()
            self.ini.set('profile', self.o.active_profile)
            self.ini.save()
        else :
            self.check_profile(self.o.active_profile, True)


    @Log(Const.LOG_DEBUG)
    def onCommandImport(self):
        """"""
        print('cmd import')
        self.impst.sendFile(self.impst.getBackupAddMap(), True)


    @Log(Const.LOG_DEBUG)
    def onCommandEdit(self):
        """"""
        key = self.getMatchKey()
        if key is not None :
            if self.o.label is not None or self.o.category is not None :                
                if self.impst.editFile(key, self.o.label, self.o.category) :
                    Sys.clear()
                    self.pheader()
                    self.impst.idxu.index.print('ID', [int(self.a[1])])
                    Sys.dprint('\n ', end='')
                    Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
                    Sys.dprint()
                else :
                    self.parser.error_cmd((('id ', (self.a[1], Sys.CLZ_ERROR_PARAM), ' has not been modified '),), False)
            else :
                self.parser.error_cmd(((' command edit need a label or a category '),), True)
                

    @Log(Const.LOG_DEBUG)
    def onCommandExport(self):
        """"""
        Sys.clear()
        self.pheader()
        from time import strftime
        name = strftime('%Y%m%d%H%M%S')+'_'+self.impst.idxu.conf.profile
        Sys.echo(' saving ', Sys.Clz.fgn7, False)
        Sys.echo(name+'.index'+Kirmah.EXT, Sys.Clz.fgB2)
        Io.copy(self.impst.idxu.pathIdx, name+'.index'+Kirmah.EXT)
        Sys.echo(' saving ', Sys.Clz.fgn7, False)
        Sys.echo(name+'.ini'+Kirmah.EXT, Sys.Clz.fgB2)
        self.impst.idxu.conf.ini.save(name+'.ini', True)
        Sys.echo(' saving ', Sys.Clz.fgn7, False)
        Sys.echo(name+'.key', Sys.Clz.fgB2)
        Io.set_data(name+'.key', self.impst.idxu.conf.get('key','keys'))
        Sys.dprint('\n ', end='')
        Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
        Sys.dprint()


    @Log(Const.LOG_DEBUG)
    def onCommandGet(self):
        """"""
        if not len(self.a)>1 :
            self.parser.error_cmd((self.a[0]+' command need an id',), True)
        else:
            vid = self.a[1]
            ids = []
            for sid in vid.split(',') :
                seq = sid.split('-')
                if len(seq)==2 : ids.extend(range(int(seq[0]),int(seq[1])+1))
                else: ids.append(sid)
            for sid in ids :
                Sys.clear()
                self.pheader()
                if self.impst.getFile(sid) :
                    self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                    Sys.dprint(' ', end='')
                    Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
                    Sys.dprint()
                else:
                    self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                    Sys.dprint(' ', end='')
                    Sys.echo(' == `'                  , Sys.Clz.bg1+Sys.Clz.fgB7, False)
                    Sys.echo(str(sid)                 , Sys.Clz.bg1+Sys.Clz.fgB3, False)
                    Sys.echo('` KO == ', Sys.Clz.bg1+Sys.Clz.fgB7)
                    Sys.dprint()


    @Log(Const.LOG_DEBUG)
    def onCommandList(self):
        """"""
        matchIdsCatg = None                            
        matchIdsUser = None
        matchIdsAcc  = None
        matchIds     = None
        
        if self.o.account is not None :
            matchIdsAcc = []
            # print(self.impst.idxu.index.acclist)
            # print(self.impst.idxu.index.acclist.keys())
            if self.impst.idxu.conf.ini.has('user', self.o.account+'.imap') :
                usr = self.impst.idxu.conf.ini.get('user', self.o.account+'.imap')
                if usr in self.impst.idxu.index.acclist.keys() :
                    print(usr)
                for k in self.impst.idxu.index.acclist.keys():
                    if self.impst.idxu.index.acclist[k] == usr :
                        print('matched')
                        matchIdsAcc = self.impst.idxu.index.getByAccount(k)
                        print(matchIdsAcc)
                        break
            else :
                matchIdsAcc = []
        
        if self.o.category is not None :
            matchIdsCatg = self.impst.idxu.index.getByCategory(self.o.category)
        if self.o.user is not None :
            matchIdsUser = self.impst.idxu.index.getByUser(self.o.user)
        
        if self.o.category is not None :                                
            if self.o.user is not None :
                matchIds = self.impst.idxu.index.getIntersection(matchIdsCatg,matchIdsUser)
            else : matchIds = matchIdsCatg

        elif self.o.user is not None :
            matchIds = matchIdsUser                    

        if matchIdsAcc is not None:
            matchIds = matchIdsAcc if matchIds is None else self.impst.idxu.index.getIntersection(matchIdsAcc,matchIds)

        order = self.o.order
        if self.o.order_inv is not None:
            order = '-'+self.o.order_inv
        Sys.clear()
        self.pheader()
        self.impst.idxu.index.print(order,matchIds)


    @Log(Const.LOG_DEBUG)
    def onCommandRemove(self):
        """"""
        key = self.getMatchKey()
        if key is not None :
            Sys.clear()
            self.pheader()
            if self.impst.removeFile(self.a[1]) :
                self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                Sys.dprint(' ', end='')
                Sys.echo(' == OK == ', Sys.Clz.bg2+Sys.Clz.fgb7)
            else :
                self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                Sys.dprint(' ', end='')
                Sys.echo(' == can\'t remove file == ', Sys.Clz.bg3+Sys.Clz.fgB4)
            Sys.dprint()


    @Log(Const.LOG_DEBUG)
    def onCommandInfo(self):
        """"""
        key = self.getMatchKey()
        if key is not None :
            Sys.clear()
            self.pheader()
            self.impst.getInfo(int(self.a[1]))
            #~ self.cleanAccount('gmail6')


    def cleanAccount(self, account):
        """"""
        ids = self.impst.idxu.index.getByAccount(account)
        self.impst.idxu.switchFileAccount(account)
        self.pheader()
        print('cleaning account :'+account)
        self.impst.idxu.index.print('ID',ids)
        
        status, resp = self.impst.idxu.ih.cnx.uid('search', None, '(ALL)')
        allids = resp[0].split(b' ')
        
        goodids = []
        for uid in ids :
            key     = self.impst.idxu.index.getById(uid)
            row     = self.impst.idxu.index.get(key)
            if row is not None :
                km      = Kirmah(row[self.impst.idxu.index.KEY])
                hlst    = km.ck.getHashList(key, row[self.impst.idxu.index.PARTS], True)
                goodids += self.impst.idxu.ih.searchBySubject(hlst['head'][2], True)
        
        badids = [ i for i in set(allids).difference(set(goodids))]
        if len(badids)>0:
            self.impst.idxu.ih.delete(badids, True, True)
            self.impst.idxu.ih.clearTrash()


    @Log(Const.LOG_DEBUG)
    def onCommandSearch(self):
        """"""        
        if not len(self.a)>1 :
            self.parser.error_cmd((' search command need one argument',), True)
        else:
            vsearch = self.a[1]
            
            matchIds = self.impst.idxu.index.getByPattern(vsearch)
            Sys.clear()
            self.pheader()
            if matchIds is not None:
                Sys.echo(' searching --'   , Sys.Clz.fgB3, False)
                Sys.echo(' `'+vsearch+'`'  , Sys.Clz.fgB7, False)
                Sys.echo(' -- found '      , Sys.Clz.fgB3, False)
                Sys.echo(str(len(matchIds)), Sys.Clz.fgB1, False)
                Sys.echo(' results --'     , Sys.Clz.fgB3)
                self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                
                matchIdsCatg = None
                matchIdsUser = None
                matchIdsCrit = None
                if self.o.category is not None :
                    Sys.dprint(self.o.category)
                    matchIdsCatg = self.impst.idxu.index.getByCategory(self.o.category)
                if self.o.user is not None :
                    matchIdsUser = impst.idxu.index.getByUser(o.user)
                
                if self.o.category is not None :
                    if self.o.user is not None :
                        matchIdsCrit = self.impst.idxu.index.getIntersection(matchIdsCatg,matchIdsUser)
                    else : matchIdsCrit = matchIdsCatg
                
                elif self.o.user is not None :
                    matchIdsCrit = matchIdsUser
                
                if matchIdsCrit is not None :
                    matchIds = self.impst.idxu.index.getIntersection(matchIds,matchIdsCrit)
                
                order = self.o.order
                if self.o.order_inv is not None:
                    order = '-'+self.o.order_inv
                
                self.impst.idxu.index.print(self.o.order,matchIds)
            else:
                self.Cli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
                Sys.dprint(' ', end='')
                Sys.echo(' == no match found for pattern `', Sys.Clz.bg3+Sys.Clz.fgB4, False)
                Sys.echo(vsearch                           , Sys.Clz.bg3+Sys.Clz.fgB1, False)
                Sys.echo('` == '                           , Sys.Clz.bg3+Sys.Clz.fgB4)
                Sys.dprint()
