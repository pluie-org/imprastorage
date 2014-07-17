#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/index.py
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
# ~~ module index ~~

from binascii               import a2b_base64
from collections            import Counter
from json                   import dumps as jdumps, loads as jloads
from re                     import split as regsplit, match as regmatch, compile as regcompile, search as regsearch
from psr.sys                import Sys, Io, Const
from psr.log                import Log
from psr.imap               import BadLoginException
from impra.mail             import MailBuilder
from kirmah.crypt           import Kirmah, BadKeyException

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class ImpraIndex ~~

class ImpraIndex:
    """A representation of the index stored on the server"""

    SEP_KEY_INTERN = '§'
    """Separator used for internal key such categories"""
    UID            = 0
    """"""
    HASH           = 1
    """"""
    LABEL          = 2
    """"""
    SIZE           = 3
    """"""
    PARTS          = 4
    """"""
    EXT            = 5
    """"""
    USER           = 6
    """"""
    CATG           = 7
    """"""
    ACCOUNT        = 8
    """"""
    KEY            = 9
    """"""
    FILE_BINARY    = 'b'
    """"""
    FILE_CRYPT     = 'c'
    """"""
    COLS           = ('ID','HASH','LABEL','SIZE','PART','TYPE','USER','CATEGORY','ACCOUNT','KEY')
    """"""
    KEY_EXT        = '.key'
    

    @Log(Const.LOG_BUILD)
    def __init__(self, key, path, dicCategory={}, accountList={}, emit=False):
        """Initialize the index with rsa and encoded data

        :Parameters:
            `key`     : str
                appropriate key to decrypt/encrypt data
            `mark`    : str
                appropriate mark to check correct key
            `encdata` : str
                initial content of the index encrypted with Kirmah Algorythm
                and representing a dic index as json string
        """
        self.pathPlain = path[:-len(Kirmah.EXT)]
        self.keyPath   = self.pathPlain+self.KEY_EXT
        self.path      = path
        Io.set_data(self.keyPath, key)
        self.dic       = {}
        self.acclist   = accountList
        encdata        = Io.get_data(path, True) if Io.file_exists(path) else b''

        if encdata == b'' :
            self.dic = {}
            self.id  = 1
        else :
            self.dic = self.decrypt(path)
            l        = [self.dic[k][self.UID] for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
            if len(l) > 0 :
                self.id = max(l)+1
            else: self.id = 1
        for k in dicCategory :
            if k == 'users' :
                for k1 in dicCategory[k]:
                    if self.SEP_KEY_INTERN+k in self.dic:
                        if k1 not in self.dic[self.SEP_KEY_INTERN+k]:
                            self.dic[self.SEP_KEY_INTERN+k][k1] = dicCategory[k][k1]
            else :
                if not self.SEP_KEY_INTERN+k in self.dic:
                    self.dic[self.SEP_KEY_INTERN+k] = dicCategory[k]


    @Log()
    def add(self, key, label, count, ext='', usr='', cat='', fhash='', size=0, account=''):
        """Add an entry to the index
        """
        if self.get(fhash) == None :
            self.dic[fhash] = (self.id, fhash, label, size, count, ext, usr, cat, account, key)
            self.id +=1
            return self.id-1 
        else :
           Sys.dprint(label+' already exist')


    @Log()
    def addUser(self, nameFrom, hashName):
        """"""
        if not self.hasUser(hashName):
            self.dic[self.SEP_KEY_INTERN+'users'][hashName] = nameFrom


    @Log(Const.LOG_ALL)
    def hasUser(self, hashName):
        """"""
        if not self.SEP_KEY_INTERN+'users' in self.dic:
            self.dic[self.SEP_KEY_INTERN+'users'] = {}
        return hashName in self.dic[self.SEP_KEY_INTERN+'users']


    @Log(Const.LOG_ALL)
    def getUser(self, hashName):
        """"""
        usrName = 'Anonymous'
        if self.hasUser(hashName):
            usrName = self.dic[self.SEP_KEY_INTERN+'users'][hashName]
        return usrName

    
    def getAllCatgs(self):
        """"""
        return self.dic[self.SEP_KEY_INTERN+'catg'].split(',') if self.SEP_KEY_INTERN+'catg' in self.dic else []


    @Log()
    def rem(self,label):
        """Remove the selected label from the index"""
        self.dic.pop(label, None)


    @Log()
    def getAutoCatg(self,ext):
        """"""
        catg = 'none'
        if regsearch('\.(jpg|jpeg|gif|png)',ext):
            catg = 'images'
        elif regsearch('\.(txt|doc|odt|csv|pdf)',ext):
            catg = 'doc'
        elif regsearch('\.(sh|py|c|cpp|h|php|bash)',ext):
            catg = 'code'
        elif regsearch('\.(mp4|avi|mpg|mpeg|flv|ogv)',ext):
            catg = 'films'
        elif regsearch('\.(mp3|ogg|flac)',ext):
            catg = 'music'
        elif regsearch('\.(zip|7z|tar|gz|rar|bz|xz|jar|bz2)',ext):
            catg = 'archives'
        return catg


    @Log()
    def isEmpty(self):
        """"""
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        return len(r) == 0


    @Log()
    def getLabel(self, key):
        """Get label corresponding to key in the index
        :Returns: `str`|None label
        """
        value = ''
        row   = self.get(key)
        if row is not None :
            value = row[self.LABEL]


    @Log()
    def get(self, key):
        """Get the corresponding key in the index
        :Returns: `tuple` row
        """
        row = None
        if key in self.dic : row = self.dic.get(key)
        return row


    @Log()
    def edit(self, key, label=None, category=None):
        """Get the corresponding key in the index
        :Returns: `tuple` row
        """
        done = False
        row  = self.dic[key]
        r    = list(row)
        if label != None :
            try :
                name, ext = Sys.getFileExt(label)
                r[self.LABEL] = name
                if ext is not '' :
                    r[self.EXT] = ext
            except Exception as e :
                r[self.LABEL] = label
        if category != None :
            r[self.CATG] = category
        self.dic[key] = tuple(r)
        done = row != self.dic[key]
        return done


    @Log()
    def getById(self, sid):
        """Get the corresponding id in the index
        :Returns: `str`|None key
        """
        l  = None
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and self.dic[k][self.UID] == int(sid)]
        if len(r)==1 : l = r[0]
        return l


    @Log()
    def fixAccount(self,account):
        """"""
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        for k in r:
            t = list(self.dic[k])
            if len(t)-1 < self.ACCOUNT:
                t.append(account)
            else:
                t[self.ACCOUNT] = account
            self.dic[k] = tuple(t)


    @Log()
    def getLightestAccount(self,l):
        """"""
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        t = {}
        for k in r:
            if not self.dic[k][self.ACCOUNT] in t: t[self.dic[k][self.ACCOUNT]] = self.dic[k][self.SIZE]
            else: t[self.dic[k][self.ACCOUNT]] += int(self.dic[k][self.SIZE])
        profile = None
        r = []
        for a in l:
            if not a in t :
                profile = a
                break
            else : 
                r.append((t[a],a))
        if profile is None :
            d = sorted(r, reverse=False, key=lambda lst:lst[0])
            profile = d[0][1]
        return profile


    @Log()
    def fixDuplicateIds(self):
        """Get corresponding keys of duplicate ids in the index
        :Returns: `str`|None key
        """
        r  = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)]
        l  = [(k,self.dic[k][self.UID]) for k in r]
        l2 = [k[1] for k in l]
        if len(l2)> 0 :
            mxid = max(l2)
            l3   = [x for x, y in Counter(l2).items() if y > 1]
            d    = [k[0] for k in l if any( k[1] == v for v in l3)]
            for k in d:
                mxid += 1
                #mprint(self.dic[k])
                t = list(self.dic[k])
                t[self.UID] = mxid
                #mprint(t)
                self.dic[k] = tuple(t)
            self.id = mxid+1
        else:
            self.id = 1
            d = ()
        return len(d)>0


    @Log()
    def getByLabel(self,label):
        """Get the corresponding label in the index
        :Returns: `str`|None key
        """
        l  = None
        r = [k for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and self.dic[k][self.LABEL] == label]
        if len(r)==1: l = r[0]
        return l


    @Log()
    def getByPattern(self,pattern):
        """Get ids corresponding to label matching the pattern in the index
        :Returns: `[uid]`|None matchIds
        """
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(pattern,self.dic[k][self.LABEL]) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        return l


    @Log()
    def getByCategory(self,category):
        """Get ids corresponding to category
        :Returns: `[uid]`|None matchIds
        """
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(category,self.dic[k][self.CATG]) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        return l


    @Log()
    def getByAccount(self,account):
        """Get ids corresponding to account
        :Returns: `[uid]`|None matchIds
        """
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and account==self.dic[k][self.ACCOUNT] ]
        l = [self.dic[k][self.UID] for k in r]
        return l


    @Log()
    def getByUser(self,user):
        """Get ids corresponding to category
        :Returns: `[uid]`|None matchIds
        """
        l = None
        r = [ k for i,k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN) and regsearch(user,self.getUser(self.dic[k][self.USER])) is not None ]
        l = [self.dic[k][self.UID] for k in r]
        return l


    @Log()
    def getIntersection(self,list1, list2):
        """Get ids intercept list1 and list2
        :Returns: `[uid]`|None matchIds
        """
        l = [ i for i in set(list1).intersection(set(list2))]
        return l


    @Log()
    def encrypt(self, fromPath=None):
        """"""
        if fromPath is None :
            fromPath = self.pathPlain
        Sys.pwlog([(' Encrypt Index... ' , Const.CLZ_0, True)])
        Io.set_data(fromPath, jdumps(self.dic))        
        call = ' '.join([Sys.executable, 'kirmah-cli.py', 'enc', '-qfj2' if Sys.isUnix() else '-qf', fromPath, '-z', '-r', '-m', '-o', fromPath+Kirmah.EXT, '-k', self.keyPath ])
        #~ print(call)
        Sys.sysCall(call)
        Io.removeFile(fromPath)
        Sys.pwlog([(' done', Const.CLZ_2, True)])   
        return Io.get_data(fromPath+Kirmah.EXT, True)


    @Log(Const.LOG_APP)
    def decrypt(self, fromPath=None):
        """"""        
        done = False
        try :
            if fromPath is None :
                fromPath = self.path
            toPath = fromPath[:-len(Kirmah.EXT)] if fromPath.endswith(Kirmah.EXT) else fromPath+'.dump'
            if Io.file_exists(fromPath) :
                Sys.pwlog([(' Decrypt Index... '                        , Const.CLZ_0, True)])
                call = ' '.join([Sys.executable, 'kirmah-cli.py', 'dec', '-qfj2' if Sys.isUnix() else '-qf', fromPath, '-z', '-r', '-m', '-o', toPath, '-k', self.keyPath ])
                print(call)
                Sys.sysCall(call)
                data   = jloads(Io.get_data(toPath))
                Io.removeFile(toPath)
            else :
                data = {}
            done = True
        except ValueError as e:
            raise BadKeyException(e)
        Sys.pwlog([(' done'if done else ' ko'    , Const.CLZ_2 if done else Const.CLZ_1, True)])
        return data


    @Log(Const.LOG_ALL)
    def print(self,order='ID', matchIds=None):
        """Print index content as formated bloc"""
        #~ Sys.clear()
        #~ Cli.print_header()
        #~ AbstractCli.printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)

        inv    = order.startswith('-')
        if inv : order = order[1:]
        orderIndex = self.COLS.index(order)
        if orderIndex is None : orderIndex = self.COLS.index('ID')
        d = sorted([(self.dic.get(k),k) for i, k in enumerate(self.dic) if not k.startswith(self.SEP_KEY_INTERN)], reverse=inv, key=lambda lst:lst[0][orderIndex])

        sizeid = 1+Sys.ceil(len(str(len(d))))
        if sizeid < 3 : sizeid = 3
        addsize = abs(3 - sizeid);
        
        sort = '^' if inv else '_' #'ↆ'

        space = (4+addsize, 8, 38, 10, 3, 5, 11, 24-addsize, 13)
        for i, s in enumerate(self.COLS[:-1]):
            symb, c = sort if order == s else ' ', Sys.Clz.BG4+Sys.Clz.fgB7 if order != s else Sys.Clz.BG7+Sys.Clz.fgB4
            Sys.echo ((' '+s+symb).ljust(space[i],' ') , c, False, False)
        Sys.echo('', c)
        Sys.echo(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN, Sys.CLZ_HEAD_LINE)

        a = ''
        tsize = 0
        psize = 0
        acc   = {}
        wrap  = '… ' if Sys.isUnix() else '/ '
        for v,k in d :
            if matchIds==None or v[self.UID] in matchIds:
                if v[self.SIZE] == '' : v[self.SIZE] = 0
                a = ''
                Sys.echo(str(v[self.UID]).rjust(sizeid+1,' ')                               , Sys.Clz.bg1+Sys.Clz.fgB7, False)
                Sys.echo(' '+str(k).ljust(9,' ')[0:6]+wrap                                  , Sys.Clz.fgN2, False)
                if len(v[self.LABEL])>36 : a = wrap
                try:
                    Sys.echo(str(v[self.LABEL][:36]+a).ljust(38,' ')                        , Sys.Clz.fgN7, False)
                except:
                    pass
                    j = 0
                    for c in v[self.LABEL][:36] :                        
                        try:
                            Sys.echo(str(c)                                                 , Sys.Clz.fgN7, False, False)
                        except:
                            Sys.echo('?'                                                    , Sys.Clz.fgN7, False, False)
                        j += 1
                    Sys.echo(''.ljust(38-j,' ')                      , Sys.Clz.fgN7, False, False)

                a = ''
                Sys.echo(Sys.readableBytes(v[self.SIZE])[:9].rjust(9,' ')+' '*2             , Sys.Clz.fgN5, False)
                Sys.echo(str(v[self.PARTS]).rjust(2 ,'0') +' '*2                            , Sys.Clz.fgN1, False)
                Sys.echo(str(v[self.EXT][:6]).ljust(7,' ')                                  , Sys.Clz.fgn3, False)
                Sys.echo(self.getUser(str(v[self.USER])).ljust(11  ,' ')                    , Sys.Clz.fgn7, False)
                #~ Sys.echo(str(v[self.CATG]).ljust(30 ,' ')                       , Clz.fgN3)
                if len(v[self.CATG])>22 : a = wrap
                Sys.echo(str(v[self.CATG][:22]+a).ljust(24 ,' ')                            , Sys.Clz.fgN3, False)
                a = ''
                if len(v)-2==self.ACCOUNT:
                    if v[self.ACCOUNT] in self.acclist :
                        if len(self.acclist[v[self.ACCOUNT]])>11 : a = '…'
                        Sys.echo(str(self.acclist[v[self.ACCOUNT]][:11]+a).ljust(12 ,' ')    , Sys.Clz.fgN4)
                    else :
                        Sys.echo(str(v[self.ACCOUNT][:11]+'!').ljust(12 ,' ')                , Sys.Clz.fgN4)
                    if v[self.ACCOUNT] in acc :
                        acc[v[self.ACCOUNT]] += int(v[self.SIZE])
                    else : acc[v[self.ACCOUNT]] = int(v[self.SIZE])
                else: Sys.dprint()
            
                psize += int(v[self.SIZE])
            tsize += int(v[self.SIZE])
        if len(d)==0:
            Sys.echo(' empty', Sys.Clz.fgB1)

        Sys.echo(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN, Sys.CLZ_HEAD_LINE)
        c = Sys.Clz.fgB2
        if psize != tsize : c = Sys.Clz.fgB7
        Sys.echo(' size : ', Sys.Clz.fgB3, False)
        Sys.echo(Sys.readableBytes(psize)[:9].rjust(9,' '), c, False)
        if psize != tsize :
            Sys.echo(' / ', Sys.Clz.fgB3, False)
            Sys.echo(Sys.readableBytes(tsize), Sys.Clz.fgB2, False)
        Sys.dprint()
        Sys.echo(Const.LINE_SEP_CHAR*Const.LINE_SEP_LEN, Sys.CLZ_HEAD_LINE)

        #~ Sys.echo(' '*4+'[', Sys.Clz.fgB7, False)
        #~ sep = ''
        #~ for k in acc:
            #~ if k!= '':
                #~ Sys.echo(sep+k,Sys.Clz.fgB3,False)
                #~ Sys.echo(':',Sys.Clz.fgB7,False)
                #~ Sys.echo(Sys.readableBytes(acc[k]),Sys.Clz.fgB2,False)
                #~ if sep=='':sep = ','
        #~ Sys.echo(']', Sys.Clz.fgB7, False)
        #~ mprint()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class IndexUpdater ~~

class IndexUpdater:
    """"""
    @Log(Const.LOG_BUILD)
    def __init__(self, ih, conf, wkdir='./', emit=None):
        """"""
        self.idx     = None
        self.index   = None
        self.emit    = emit
        self.delids  = []
        self.ih      = ih
        self.conf    = conf
        self.pathIdx = wkdir+'.index.'+self.conf.profile+Kirmah.EXT
        self.mb      = MailBuilder(self.conf.get('salt','keys'))
        self.rootBox = self.conf.get('box','imap')
        self.get()


    @Log(Const.LOG_DEBUG)
    def _getId(self, notAssign=False):
        """"""
        idx = None
        ids = self.ih.searchBySubject(self.mb.getHashName('index'),True)
        if len(ids) > 0 and int(ids[0]) >= 0 :
            idx = ids[-1]
            if not notAssign: self.delids = ids[:-1]
        if not notAssign:
            self.idx = idx
        return idx 


    @Log()
    def get(self, forceRefresh=False):
        """"""
        self.switchFileAccount(self.conf.profile)
        index   = None
        uid     = self.conf.get('uid'  ,'index')
        date    = self.conf.get('date' ,'index')
        tstamp  = self.conf.get('time' ,'index')
        refresh = forceRefresh        
        delta   = None if tstamp is None else Sys.datetime.now() - Sys.datetime.strptime(tstamp[:-7], '%Y-%m-%d %H:%M:%S')
        if not refresh and tstamp is not None and delta < Sys.timedelta(minutes = 3) :
            # getFromFile            
            if uid != None and Io.file_exists(self.pathIdx): # int(self.idx) == int(uid) 
                self.idx = uid
                Sys.pwlog([(' Get index from cache '  , Const.CLZ_7),
                           ('('                       , Const.CLZ_0),
                           (str(int(self.idx))        , Const.CLZ_2),
                           (')'                       , Const.CLZ_0, True)])
            else: refresh = True
        else: refresh = True
        self.irefresh = refresh
        if refresh :
            Sys.pwlog([(' Checking index...', Const.CLZ_0, True)])
            self._getId()
            if self.idx :
                if int(self.idx) != int(uid) or not Io.file_exists(self.pathIdx):
                    Sys.pwlog([(' Refreshing index (local:', Const.CLZ_0),
                               (str(int(uid))              , Const.CLZ_2),
                               (' / remote:'               , Const.CLZ_0),
                               (str(int(self.idx))         , Const.CLZ_1),
                               (')'                        , Const.CLZ_0, True)])
                    
                    date = self.ih.headerField(self.idx, 'date', True)
                    self.conf.sets((['uid'  , str(int(self.idx))     , 'index'],
                                    ['date' , date                   , 'index'],
                                    ['time' , str(Sys.datetime.now()), 'index']))
                    self._saveLocalIndex()
                else :
                    Sys.pwlog([(' Get index from cache '  , Const.CLZ_7),
                               ('('                       , Const.CLZ_0),
                               (str(int(self.idx))        , Const.CLZ_2),
                               (')'                       , Const.CLZ_0, True)])
                self.conf.set('time',str(Sys.datetime.now()),'index')
        self.build()        


    @Log()
    def build(self):
        Sys.pwlog([(' Reading index, please wait...', Const.CLZ_7, True)])
        self.index = ImpraIndex(self.conf.get('key','keys'), self.pathIdx, self.getIndexDefaultCatg(), self.getAccountList())
        defUsers   = self.conf.get('users','catg')
        if not ImpraIndex.SEP_KEY_INTERN+'users' in self.index.dic:
            self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'] = {}
        for k in self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users']:
            if self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'][k] not in [ i.strip() for i in defUsers.split(',')]:
                self.conf.set('users',defUsers+', '+self.index.dic[ImpraIndex.SEP_KEY_INTERN+'users'][k],'catg')


    @Log(Const.LOG_DEBUG)
    def getAccountList(self):
        l  = {}
        pl = self.conf.get('multi','imap')
        if pl is not None and len(pl)>0 :
            pl = pl.split(',')
            if len(pl) > 0:
                if not self.conf.profile in pl:
                    pl.append(self.conf.profile)
        else : pl = [self.conf.profile]
        for p in pl : l[p] = self.conf.get('user','imap',p)
        return l
        

    @Log(Const.LOG_DEBUG)
    def getIndexDefaultCatg(self):
        """"""
        usrName  = self.conf.get('name','infos')
        defUsers = self.conf.get('users','catg').split(',')
        dic      = {'catg':self.conf.get('types','catg'), 'users':{ ('%s' % self.mb.getHashName('all')) : 'all', ('%s' % self.mb.getHashName(usrName)) : usrName}}
        for u in defUsers :
           dic['users'][('%s' % self.mb.getHashName(u.strip()))] = u.strip()
        return dic


    @Log(Const.LOG_DEBUG)
    def _saveLocalIndex(self):
        """"""
        if not self.idx : self._getId()
        if self.idx :
            msg     = self.ih.getEmail(self.idx, True)
            content = b''
            for part in msg.walk():
                content += part.get_payload(decode=True)
            Io.set_data(self.pathIdx, a2b_base64(content), True)
        

    @Log()
    def removeLocal(self):
        """"""
        self.conf.rem('*','index')
        self.conf.save()
        self.idx = None
        Io.removeFile(self.pathIdx)


    @Log()
    def remove(self):
        """"""
        self._getId()
        try:
            if self.idx!= None : self.delids.append(Io.bytes(self.idx))
            self.ih.delete(self.delids, True)
            self.idx = None
        except Exception as e :
            Sys.dprint('error : ')
            Sys.dprint(e)
            
        self.ih.clearTrash()
        self.removeLocal()
        

    @Log(Const.LOG_APP)
    def update(self):
        """"""
        self.switchFileAccount(self.conf.profile)
        try:
            if self.idx != None :
                if not isinstance(self.idx,bytes):
                    self.idx = Io.bytes(self.idx)                
                self.delids.append(self.idx)
        except Exception as e :
            Sys.dprint('error : ')
            Sys.dprint(e)   

        self.index.fixDuplicateIds()
        #~ self.index.fixAccount('gmail5')
        self.index.encrypt()
        msgIndex    = self.mb.buildIndex(self.pathIdx)
        _, self.idx = self.ih.send(msgIndex.as_string(), self.rootBox)
        date        = self.ih.headerField(self.idx, 'date', True)
        self.conf.sets((['uid'  , self.idx              , 'index'],
                       ['date' , date                   , 'index'],
                       ['time' , str(Sys.datetime.now()), 'index']))
        
        Sys.pwlog([(' Index updated ('  , Const.CLZ_0),
                   (str(int(self.idx))  , Const.CLZ_2),
                   (') '                , Const.CLZ_0),
                   (str(date)           , Const.CLZ_7, True)])
        
        try :
            self.ih.delete(self.delids, True)       
        except :
            Sys.dprint('error : ')
            Sys.dprint(e)
        self.ih.clearTrash()
        return True

    @Log()
    def switchFileAccount(self, profile=None, force=False):
        """"""
        pl = self.conf.get('multi','imap')
        if pl is not None and len(pl)>0 :
            pl = pl.split(',')
            if len(pl) > 0:
                if not self.conf.profile in pl:
                    pl.append(self.conf.profile)
                iconf   = self.ih.conf
                account = self.conf.get('user','imap',profile)
                if True or iconf.user != account :
                    # reinit
                    iconf.user = None
                    try :
                        if profile is None : profile = self.index.getLightestAccount(pl)                        
                        if profile in pl :
                            iconf.user = self.conf.get('user','imap',profile)
                            iconf.pwd  = self.conf.get('pass','imap',profile)
                            iconf.host = self.conf.get('host','imap',profile)
                            iconf.port = self.conf.get('port','imap',profile)
                        self.ih.switchAccount(iconf, self.rootBox, force)
                    except BadLoginException as e:
                        Sys.dprint('Error : ')
                        Sys.dprint(e)
                        Sys.dprint('check your connection or your imap config for profile '+profile)
        if profile is None: profile = self.conf.profile
        return profile
