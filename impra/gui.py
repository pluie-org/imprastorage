#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  impra/gui.py
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
# ~~ module gui ~~

from gi.repository    import Gtk, GObject, GLib, Gdk, Pango
from kirmah.crypt     import KeyGen, Kirmah, KirmahHeader, ConfigKey, BadKeyException, b2a_base64, a2b_base64, hash_sha256_file
from impra.ui         import Gui, CliThread
from impra            import conf
from psr.sys          import Sys, Io, Const, init
from psr.log          import Log
from psr.ini          import IniFile
from psr.imap         import ImapConfig, ImapHelper, BadLoginException, BadHostException
import  impra.conf    as conf
from    impra.core    import ImpraStorage, ImpraConf
from    impra.index   import ImpraIndex
from    impra.ini     import KiniFile
from    threading     import Condition, RLock, Event
from    queue         import Queue
from    impra.app     import ImpraThread


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class AppGui ~~

class AppGui(Gui):

    start           = False
    poslog          = 0

    TASK_RUN        = False
    BAD_CONF        = False
    PENDING_ID      = 0

    @Log(Const.LOG_BUILD)
    def __init__(self, wname='window1'):
        """"""            
        super().__init__(wname)


    @Log(Const.LOG_UI)
    def on_start(self):
        """"""
        Sys.g.GUI_PRINT_STDOUT = False
        Sys.g.GUI              = True
        init(conf.PRG_NAME, False, Sys.getpid(), True, Const.LOG_ALL)
        self.conf        = ImpraConf(KiniFile('impra2.ini'))
        self.populate_profiles()
        self.populate_config()
        self.taskLabel     = ImpraThread.TASK_LABEL
        self.taskStock     = ImpraThread.TASK_STOCK
        self.progressbar   = self.get('progressbar1')
        self.textview      = self.get('textview1')
        try :
            self.textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1.0))
            self.textview.modify_font(Pango.font_description_from_string ('DejaVu Sans Mono Book 11' if Sys.isUnix() else 'Lucida Conosle 11'))
        except :
            pass
        self.textbuffer    = self.textview.get_buffer()
        self.tags          = self.buildTxtTags(self.textbuffer)
        self.initWidgetByThread('impra-1', self.textview, self.textbuffer, self.progressbar, self.tags)
        self.initWidgetByThread('MainThread', self.textview, self.textbuffer, self.progressbar, self.tags)
        self.tree          = self.get('treeview1')
        self.tree.connect('row-activated', self.on_row_select)
        self.tree.get_selection().connect('changed', self.on_tree_selection_changed)
        self.launch_thread(self.on_ended)
        
        self.searchCatg    = self.get('comboboxtext1')
        self.searchUser    = self.get('comboboxtext4')
        self.searchAccount = self.get('comboboxtext5')
        self.filterIds     = None
        self.index         = None
        self.taskList      = {}
        self.threads_work  = [False, False]


    def on_ended(self, thread=None, ref=None):
        """""" 
        print('ended')

    
    def on_delete_event(self, data=None, data2=None):
        """"""
        print('on_delete_event')
        self.thimpra.stop()
        if self.thimpra2 is not None :
            self.thimpra2.stop()



    # ~~ INDEX ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def on_tree_selection_changed(self, selection):
        """"""
        model, treeiter = selection.get_selected()
        hasSel = treeiter != None
        if hasSel :
            """"""
        self.unselect_actions(hasSel, True)
    

    @Log(Const.LOG_UI)
    def unselect_actions(self, sensible=False, exceptAdd=False):
        """"""
        self.get('button5').set_sensitive(sensible)
        self.get('button6').set_sensitive(sensible)
        if not exceptAdd : self.get('button12').set_sensitive(sensible)
        self.get('button7').set_sensitive(sensible)

    
    @Log(Const.LOG_UI)
    def build_treeview_column(self):
        """"""
        if self.tree.get_column(0)==None :            
            self.get('label5').set_label(' '+self.conf.get('user', 'imap',defaultValue=''))
            self.get('label7').set_label(' '+self.conf.get('uid', 'index',defaultValue=''))
            self.get('label9').set_label(' '+self.conf.get('box', 'imap',defaultValue=''))
            self.get('label10').set_label(' '+self.conf.get('date', 'index',defaultValue=''))
            #~ self.update_progress(10, 10)
            #~ self.progressbar.set_fraction(10/100.0)
            css      = [('#900000', 'white'), (None, '#82C59A'), (None, '#D4D4D4'), (None, '#D290C5'), (None, '#D87475'), (None, '#C58473'), (None, '#A7A2A2'), (None, '#EAD049'), (None, '#81AFDD')]
            for i, s in enumerate(ImpraIndex.COLS[:-1]):
                r  = Gtk.CellRendererText()
                
                #~ r.set_property('family', 'mono')
                r.set_property('size-set', True)
                r.set_property('size-points', 11)
                if css[i][0] is not None :
                    r.set_property('cell-background', css[i][0])
                if css[i][1] is not None :    
                    r.set_property('foreground', css[i][1])
                if i==0:
                    r.set_property('weight', 800)
                if i==1 or i==0 or i==3:
                    r.set_property('family', 'DejaVu Sans Mono')
                    #~ r.set_property('size-points', 10)
                if i==2:
                    r.set_property('width', 350)
                if i==6:
                    r.set_property('width', 90)
                if i==7:
                    r.set_property('width', 120)
                    """"""
                cl = Gtk.TreeViewColumn(s, r, text=i)
                cl.set_attributes(r, text=i, cell_background=ImpraIndex.ACCOUNT+1+(1 if i==0 else 0)) 
                cl.set_sort_column_id(i)
                cl.set_resizable(True)
                cl.connect('clicked', self.on_column_click)
                self.tree.append_column(cl)


    @Log(Const.LOG_UI)
    def populate_index(self):
        """"""
        self.BLOCK_REPOPULATE = False
        if self.index is None or self.index != self.thimpra.impst.idxu.index :
            self.index = self.thimpra.impst.idxu.index
        data     = sorted([(self.index.dic.get(k),k) for i, k in enumerate(self.index.dic) if not k.startswith(self.index.SEP_KEY_INTERN)], reverse=False, key=lambda lst:lst[0][self.index.UID])
        store    = self.get('treestore1')
        store.clear()
        drow     = None
        i        = 0
        tsize    = 0
        psize    = 0
        accounts = self.thimpra.impst.idxu.getAccountList()
        allCatg, allUsers, allAccounts, tmp = [], [], [ accounts[a] for a in accounts], ''
        for row, key in data :
            
            tsize += row[self.index.SIZE]
            if self.filterIds==None or row[self.index.UID] in self.filterIds:
            
                drow = list(row[:-1])
                psize += row[self.index.SIZE]

                if drow[self.index.CATG] not in allCatg :
                    allCatg.append(drow[self.index.CATG])
                tmp = self.index.getUser(drow[self.index.USER])                
                if tmp not in allUsers :
                    allUsers.append(tmp)
                drow[self.index.PARTS]     = ('%s' % drow[self.index.PARTS]).rjust(2,' ')
                drow[self.index.UID]       = ('%s' % drow[self.index.UID]).rjust(4,' ')
                drow[self.index.HASH]      = '%s' % drow[self.index.HASH][0:6]+'…'
                drow[self.index.SIZE]      = Sys.readableBytes(row[self.index.SIZE]).rjust(11,' ')+'  '
                drow[self.index.USER]      = self.index.getUser(drow[self.index.USER])
                drow[self.index.ACCOUNT]   = self.index.acclist[drow[self.index.ACCOUNT]]
                drow.append('#222222' if i%2!=0 else '#1C1C1C')
                drow.append('#640000' if i%2!=0 else '#900000')
                store.append(None, drow)
                i += 1
                self.progressbar.set_fraction(10+i*90/len(data)/100.0)
            
        # repopulate only if not search
        if self.filterIds==None :
            #~ Sys.pwlog([(' Populating search filters...', Const.CLZ_0, True)])
            self.populate_search_filters(allCatg, allUsers, allAccounts)
        
        self.get('checkbutton1').set_sensitive(True)
        
        self.get('label12').set_label(' '+(Sys.readableBytes(psize)+' / ' if psize != tsize else '')+Sys.readableBytes(tsize))
        
        self.get('button9').set_sensitive(True)
        self.get('button12').set_sensitive(True)
        return False


    # ~~ force redrawing odd/even tree rows ~~~~~~~
    
    @Log(Const.LOG_UI)
    def on_column_click(self, treeviewcolumn, user_param1=None):
        """"""
        for i, row in enumerate(self.tree.get_model()):
            row[self.index.ACCOUNT+1] = '#222222' if i%2!=0 else '#1C1C1C'
            row[self.index.ACCOUNT+2] = '#640000' if i%2!=0 else '#900000'


    @Log(Const.LOG_UI)
    def populate_search_filters(self, catgs=(), users=(), accounts=()):
        """"""        
        lst = ((Gtk.ListStore(str), sorted(catgs)   , '-- All categories --', self.searchCatg),
               (Gtk.ListStore(str), sorted(users)   , '-- All users --'     , self.searchUser),
               (Gtk.ListStore(str), sorted(accounts), '-- All accounts --'  , self.searchAccount))
        for data in lst :
            data[0].append([data[2]])
            for item in data[1]:
                data[0].append([item])
            data[3].set_model(data[0])
            data[3].set_active(0)

    
    # ~~ SEARCH ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def on_search(self, btn, data=None):
        """"""
        self.get('entry16').set_sensitive(btn.get_active())
        self.get('comboboxtext1').set_sensitive(btn.get_active())
        self.get('comboboxtext4').set_sensitive(btn.get_active())
        self.get('comboboxtext5').set_sensitive(btn.get_active())
        self.get('button8').set_sensitive(btn.get_active())
        if not btn.get_active() :
            self.filterIds = None
            if not self.BLOCK_REPOPULATE :
                self.populate_index()


    def get_search_filter(self, comboName):
        """"""
        value = ''
        citer = self.get(comboName).get_active_iter()     
        if citer != None:
            model =  self.get(comboName).get_model()
            if model[citer][0] != model[model.get_iter_first()][0] :
                value = model[citer][0]
        return value

    
    def on_launch_search(self, btn, data=None):
        """"""
        self.on_search(self.get('checkbutton1'))
        slabel = self.get('entry16').get_text()
        scatg  = self.get_search_filter('comboboxtext1')
        suser  = self.get_search_filter('comboboxtext4')
        sacc   = self.get_search_filter('comboboxtext5')
        
        matchIdsAcc  = None
        matchIdsCatg = None
        matchIdsUser = None
        matchIdsCrit = None
        matchIds     = self.index.getByPattern(slabel)
        
        if sacc != '' :
            matchIdsAcc = []
            for k in self.index.acclist.keys():
                if self.index.acclist[k] == sacc :    
                    print('key : '+str(k)+' - sacc : '+str(sacc))
                    matchIdsAcc = self.index.getByAccount(k)
                    break        
            matchIds     = self.index.getIntersection(matchIds,matchIdsAcc)
            
        if   scatg != '' : matchIdsCatg = self.index.getByCategory(scatg)
        if   suser != '' : matchIdsUser = self.index.getByUser(suser)        
        if   scatg != '' : matchIdsCrit = self.index.getIntersection(matchIdsCatg,matchIdsUser) if suser != '' else matchIdsCatg           
        elif suser != '' : matchIdsCrit = matchIdsUser
        else             : matchIdsCrit = matchIds

        if matchIdsCrit is not None :
            self.filterIds = self.index.getIntersection(matchIds,matchIdsCrit)        
        
        self.populate_index()

        
    
    # ~~ ADD ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    @Log(Const.LOG_UI)
    def on_add_file(self, btn, data=None):
        """"""
        self.get('dialog1').show()


    @Log(Const.LOG_UI)
    def on_add_file_set(self, fc, data=None):
        """"""
        fname, ext = Sys.getFileExt( fc.get_filename())
        catg = self.index.getAutoCatg(ext)
        if (self.get('entry2').get_text() == '' or self.get('checkbutton2').get_active()) and catg!='none' :
            self.get('entry2').set_text(catg)


    @Log(Const.LOG_UI)
    def add_file(self, btn, data=None):
        """"""
        fileName = self.get('filechooserbutton1').get_filename()
        label    = self.get('entry1').get_text()
        category = self.get('entry2').get_text()
        btn.set_sensitive(False)
        self.on_cancel_add(btn)
        self.launch_action(ImpraThread.TASK_ADD, (fileName, label, category))


    @Log(Const.LOG_UI)
    def on_cancel_add(self, btn, data=None):
        """"""
        self.get('dialog1').hide()
        self.get('filechooserbutton1').set_filename('')
        self.get('entry1').set_text('')
        self.get('entry2').set_text('')
        btn.set_sensitive(True)

    
    # ~~ EDIT ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # double-clic row
    @Log(Const.LOG_UI)
    def on_row_select(self, treeview, path, view_column, data=None):
        """"""
        store    = self.get('treestore1')
        treeiter = store.get_iter(path)
        self.editUid      = store.get_value(treeiter, self.index.UID)
        self.editKey      = self.index.getById(self.editUid)
        self.editLabel    = store.get_value(treeiter, self.index.LABEL)
        self.editCategory = store.get_value(treeiter, self.index.CATG)
        self.on_edit_file()


    @Log(Const.LOG_UI)
    def on_edit_file(self):
        """"""        
        self.get('label39').set_text(' Editing `'+self.editLabel+'` ('+str(self.editUid)+')')
        self.get('entry17').set_text(self.editLabel)
        self.get('entry18').set_text(self.editCategory)
        self.get('dialog2').show()

    
    @Log(Const.LOG_UI)
    def on_edit(self, btn, data=None):
        """"""
        label    = self.get('entry17').get_text()
        category = self.get('entry18').get_text()
        btn.set_sensitive(False)
        self.on_cancel_edit(btn)
        if label != self.editLabel or category != self.editCategory :
            self.launch_action(ImpraThread.TASK_EDIT, (self.editKey, label, category))


    @Log(Const.LOG_UI)
    def on_cancel_edit(self, btn, data=None):
        """"""
        self.get('dialog2').hide()
        self.get('entry17').set_text('')
        self.get('entry18').set_text('')
        btn.set_sensitive(True)


    def get_selected_uid(self):
        """"""
        model, treeiter = self.tree.get_selection().get_selected()
        return int(model[treeiter][0])
    
    # ~~ INFOS ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def on_file_infos(self, btn, data=None):
        """"""        
        self.launch_action(ImpraThread.TASK_INFOS, self.get_selected_uid())

    
    # ~~ GET ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def on_file_download(self, btn, data=None):
        """"""
        self.launch_action(ImpraThread.TASK_GET, self.get_selected_uid())


    # ~~ REMOVE ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def on_file_delete(self, btn, data=None):
        """"""
        self.launch_action(ImpraThread.TASK_REMOVE, self.get_selected_uid())


    # ~~ REFRESH ACTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def on_refresh(self, btn, data=None):
        """"""
        self.BLOCK_REPOPULATE = True
        self.get('treestore1').clear()
        if btn is not None :
            Sys.cli_emit_progress(0)
            self.get('checkbutton1').set_sensitive(False)
            self.get('checkbutton1').set_active(False)
            self.unselect_actions()
            self.get('button9').set_sensitive(False)
            self.launch_action(ImpraThread.TASK_REFRESH, [])
        else :
            self.populate_index()


    def on_remove_pending(self, btn, keyPending, execute=False, keepRetry=True):
        """"""
        print('on_remove_pending')
        if keyPending in self.taskList :
            action, params, keep = self.taskList[keyPending]
            print('keyPending : '+str(keyPending))
            print('execute : '+str(execute))
            print('keepRetry : '+str(keepRetry))
            print('action : '+str(action))
            print('params : '+str(params))
            print('keep : '+str(keep))
            if keep and keepRetry :
                pass
            else :
                self.taskList.pop(keyPending)
                self.get('box19').remove(btn)
                if len(self.taskList)==0:
                    self.get('paned1').set_position(5000)
                if execute :
                    self.launch_action(action, params)


    def populate_pending_task(self, action, params, execute=False):
        """"""
        print('populate_pending_task')
        self.get('paned1').set_position(1030)
        keyPending = 'pending-'+str(self.PENDING_ID)
        keep       = action==ImpraThread.TASK_ADD_RETRY
        self.taskList[keyPending] = (action, params, keep)
        w     = Gtk.Button(label='Pending task '+self.taskLabel[action], image=Gtk.Image(stock=self.taskStock[action]))
        w.set_tooltip_text('click to '+('execute' if keep else 'remove')+' task '+self.taskLabel[action]+('' if keep else ' ('+str(params)+')'))
        w.set_property('halign', Gtk.Align.START)
        w.connect('clicked', self.on_remove_pending, keyPending, execute, not keep)
        w.set_name(keyPending)        
        self.get('box19').pack_start(w, False, False, 1)
        w.show()
        #~ self.get('box19').show()


    def launch_action(self, action, params):
        """"""
        if not self.threads_work[0] :
            self.threads_work[0] = True            
            self.taskQueue.put_nowait((action, params, self.PENDING_ID))
            
        else:
            self.populate_pending_task(action, params)
            
        self.PENDING_ID += 1
            
            #~ self.do_pending_task()
            
            
            #~ self.threads_work[1] = True
            #~ print('task thread 2')
            #~ self.taskQueue.put_nowait((action, params))
            #~ if self.thimpra2 is None :
                #~ self.thimpra2  = ImpraThread(self.evtStop, self.taskQueue, self.condition, self.conf, 'impra-2')            
                #~ self.thimpra2.connect_signals(self.signalsDef, None)
                #~ self.thimpra2.start()

            #~ keyPending = 'pending-'+str(self.PENDING_ID)
            #~ ltask = ['wait','add','get','refresh','remove','infos','edit','exit']
            #~ self.taskList[keyPending] = (action, params)
            #~ w     = Gtk.Button(label='remove pending task '+ltask[action]+' ['+str(params)+']', image=Gtk.Image(stock=Gtk.STOCK_REMOVE))
            #~ w.connect('clicked', self.on_remove_pending, keyPending)
            #~ self.get('box19').pack_start(w, True, True, 5)
            #~ self.PENDING_ID += 1

        
    def do_pending_task(self):
        """"""
        print('do_pending_task')
        wlist = self.get('box19').get_children()
        if len(wlist)>0 :
            keyPending = wlist[0].get_name()
            self.on_remove_pending(wlist[0], keyPending, True)            

    




    # ~~ ACTIONS CALLBACK ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def on_has_add_retry(self, thread, usrData):
        """"""
        print('on_has_add_retry')
        self.populate_pending_task(ImpraThread.TASK_ADD_RETRY, None, True)        
        self.PENDING_ID += 1
    
    
    def on_common_ending_action(self, thread=None, done=None, key=None, usrData=None):
        """"""
        if thread.name == 'impra-1' :
            self.threads_work[0] = False
            self.do_pending_task()
        self.on_progress(thread)

    
    def on_need_config(self, thread=None, usrData=None):
        """"""
        self.BAD_CONF = True
        if thread.name == 'impra-1' :
            self.threads_work[0] = False
            self.do_pending_task()
        self.get('notebook1').set_current_page(1)
        self.get('label42').set_text('Something is wrong in your configuration')


    def on_index_refresh(self, thread=None, ref=None, updated=None, usrData=None):
        """"""
        self.on_common_ending_action(thread)
        if self.tree.get_column(0) == None :
            self.build_treeview_column()
        self.on_refresh(None)
        

    # ~~ IMPRA THREAD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @Log(Const.LOG_UI)
    def launch_thread(self, on_complete, userData=None):        
        self.evtStop    = Event()
        self.taskQueue  = Queue()
        self.condition  = Condition(RLock())
        self.thimpra2   = None    
        self.thimpra    = ImpraThread(self.evtStop, self.taskQueue, self.condition, self.conf, 'impra-1')
        self.signalsDef = (('completed'    , on_complete),
                          ('interrupted'   , self.on_interrupted),
                          ('progress'      , self.on_progress),
                          ('fileadded'     , self.on_common_ending_action),
                          ('fileget'       , self.on_common_ending_action),
                          ('fileinfos'     , self.on_common_ending_action),
                          ('fileremoved'   , self.on_common_ending_action),
                          ('fileedited'    , self.on_common_ending_action),
                          ('fileaddretry'  , self.on_common_ending_action),
                          ('indexrefreshed', self.on_index_refresh),                          
                          ('hasaddretry'   , self.on_has_add_retry),
                          ('needconfig'    , self.on_need_config))
        self.thimpra.connect_signals(self.signalsDef, userData)
        self.thimpra.start()


    # ~~ CONFIG PAGE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def populate_profiles(self):
        """"""
        l = Gtk.ListStore(str)
        l.append(['current profile'])
        sections = sorted(self.conf.ini.getSections())
        if len(sections) > 0:
            ap  = self.conf.ini.get('profile')
            sep = ''
            for p in sections:
                if p != ap and p != '':
                    l.append([p])
        self.get('comboboxtext3').set_model(l)
        self.get('comboboxtext3').set_active(0)


    def on_profile_change(self, combo, data=None):
        """"""
        citer = combo.get_active_iter()     
        if citer != None:
            model   = combo.get_model()
            profile = model[citer][0]
            if profile == 'current profile' :
                profile = None
            self.populate_config(profile)

    
    def on_gen_new_key(self, btn, data=None):
        """"""
        kg = KeyGen(int(self.get('spinbutton1').get_value()))
        self.get('entry14').set_text(kg.key)
        self.get('entry15').set_text(kg.mark)
        # 18


    def on_delete_profile(self, btn, data=None):
        """"""
        p = self.get('entry3').get_text()
        if p != self.conf.profile :
            self.conf.remProfile(p)
        else :
            """"""
            print('is current')
        model = self.get('comboboxtext3').get_model()
        citer = self.get('comboboxtext3').get_active_iter()
        del(model[citer])
        self.get('comboboxtext3').set_active(0)
        # 17


    def on_edit_new_profile(self, btn, data=None):
        """"""
        self.populate_config('new')
        self.get('spinbutton1').set_sensitive(True)
        self.get('spinbutton2').set_sensitive(True)
        self.get('button18').set_sensitive(True)


    def on_hide_pwd(self, btn, data=None):
        """"""
        self.get('entry12').set_visibility(not btn.get_active())
        self.get('entry13').set_visibility(not btn.get_active())


    @Log(Const.LOG_UI)
    def populate_config(self, p=None):
        """"""
        self.get('button18').set_sensitive(False)
        profile = self.conf.profile if p is None else p
        self.get('label41').set_label('')
        self.get('label42').set_label('')
        self.get('label2').set_label('')
        self.get('entry3').set_text(profile)
        
        self.get('entry4').set_text(self.conf.get('name', 'infos', profile,''))
        self.get('entry5').set_text(self.conf.get('host', 'imap', profile,''))
        self.get('entry6').set_text(self.conf.get('port', 'imap', profile,''))
        self.get('entry7').set_text(self.conf.get('user', 'imap', profile,''))
        self.get('entry13').set_text(self.conf.get('pass', 'imap', profile,''))

        m = self.getMultiAccount()

        l = Gtk.ListStore(str)
        l.append(['*new'])
        for a in m:l.append([a])
        self.get('comboboxtext2').set_model(l)
        self.get('comboboxtext2').set_active(0)

        self.get('entry8').set_text('')
        self.get('entry9').set_text('')
        self.get('entry10').set_text('')
        self.get('entry11').set_text('')
        self.get('entry12').set_text('')

        key = self.conf.get('key', 'keys', profile,'')
        hasKey = key != ''
        self.get('entry14').set_text(key)
        self.get('entry14').set_sensitive(False)
        self.get('entry15').set_text(self.conf.get('mark', 'keys', profile,''))
        self.get('entry15').set_sensitive(False)
        self.get('spinbutton1').set_value(len(key))
        self.get('spinbutton1').set_sensitive(p is not None or self.BAD_CONF)
        self.get('spinbutton2').set_value(128)
        self.get('spinbutton2').set_sensitive(p is not None or self.BAD_CONF)
        self.get('button18').set_sensitive(p is not None or self.BAD_CONF)
        self.get('button17').set_sensitive(p is not None or self.BAD_CONF)
        
    
    def getMultiAccount(self):
        """"""
        if self.conf.ini.has('multi' , self.conf.profile+'.imap'):
            m = self.conf.ini.get('multi', self.conf.profile+'.imap')
        else : m = None
        if m is None : m = []
        else : m = m.split(',')
        m = [x for x in m if x]
        return sorted(m)
        
        
    def on_add_multiaccount(self, btn, data=None):
        """"""
        profile = self.get('entry8').get_text()
        if profile != '' :
            m = self.getMultiAccount()
            if profile is not None and profile is not '' :
                canAdd = self.on_test_account(None)
                if canAdd :
                    if profile not in m :
                        m.append(profile)
                    
                    self.conf.ini.set('multi', ','.join(m), self.conf.profile+'.imap')        
                    self.conf.ini.set('host' , self.get('entry9').get_text()   , profile+'.imap')
                    self.conf.ini.set('user' , self.get('entry11').get_text()  , profile+'.imap')
                    self.conf.ini.set('pass' , self.get('entry12').get_text()  , profile+'.imap')
                    self.conf.ini.set('port' , self.get('entry10').get_text()  , profile+'.imap')            
                    self.conf.ini.save()
                    self.conf.ini.print(profile)
                    self.get('entry9').set_text('')
                    self.get('entry10').set_text('')
                    self.get('entry11').set_text('')
                    self.get('entry12').set_text('')
                    self.populate_config()
                
                else :
                    self.get('label2').set_label('can\'t add : '+self.get('label2').get_label())
        else :
            self.get('label2').show()
            self.get('label2').set_label('need an account name')


    def test_imap(self, names):
        """"""
        self.get(names[4]).set_label('testing...')        
        conf = ImapConfig(self.get(names[0]).get_text(), self.get(names[1]).get_text(), self.get(names[2]).get_text(), self.get(names[3]).get_text())
        done = False
        if not ((conf.host != '' and conf.host is not None) and (conf.user != '' and conf.user is not None) and (conf.port != '' and conf.port is not None) and (conf.pwd != '' and conf.pwd is not None)):
            msg = 'nodata'
        else :
            print('test_imap')
            try :
                msg  = ''     
                ih   = ImapHelper(conf, 'INBOX', True)
                done = True
            except Exception as e:
                msg = e.__name__                
                print(e)

        self.get(names[4]).set_label('test ok' if done else 'test failed ! ['+msg+']')
        self.get(names[4]).show()
        return done


    def on_test_main_imap(self, btn, data=None):
        """"""
        return self.test_imap(('entry5', 'entry7', 'entry13', 'entry6', 'label41'))


    def on_test_account(self, btn, data=None):
        """"""
        return self.test_imap(('entry9', 'entry11', 'entry12', 'entry10', 'label2'))        
        
    
    def on_multiaccount_change(self, combo, data=None):
        """"""
        citer = combo.get_active_iter()
        self.get('button15').set_sensitive(True)    
        if citer != None:
            model   = combo.get_model()
            account = model[citer][0]
            self.get('entry8').set_text('')
            self.get('label2').set_label('')
            if account == '*new' :
                self.get('button2').set_label('add account')
                self.get('button4').set_sensitive(False)
            if account is not None and account is not '' and account != '*new':
                self.get('button2').set_label('edit account')
                self.get('button4').set_sensitive(True)
                self.get('entry8').set_text(account)
                self.get('entry9').set_text(self.conf.get('host', 'imap', account,''))
                self.get('entry10').set_text(self.conf.get('port', 'imap', account,''))
                self.get('entry11').set_text(self.conf.get('user', 'imap', account,''))
                self.get('entry12').set_text(self.conf.get('pass', 'imap', account,''))
        
    
    def on_remove_multiaccount(self, btn, data=None):
        """"""
        m = self.getMultiAccount()
        profile = self.get('entry8').get_text()        
        citer = self.get('comboboxtext2').get_active_iter()
        if citer != None:
            model =self.get('comboboxtext2').get_model()
            account = model[citer][0]
        
        #~ if profile != account
        if account in m :
            m.remove(account)
            self.conf.remProfile(account)
            self.conf.ini.set('multi', ','.join(m), self.conf.profile+'.imap') 
        self.populate_config()
        
        
    def on_save_profile(self, btn, data=None):
        """"""
        profile = self.get('entry3').get_text()
        if profile != '' :
            usr = self.get('entry4').get_text()
            if usr != '' :
                canSave = self.on_test_main_imap(None)
                if canSave :
                    if not(self.get('entry14').get_text() != '' and self.get('entry15').get_text()!= '') :
                        self.on_gen_new_key(None)

                    self.get('spinbutton1').set_sensitive(False)
                    self.get('spinbutton2').set_sensitive(False)

                    self.conf.ini.set('name', usr                           , profile+'.infos')
                    
                    self.conf.ini.set('key' , self.get('entry14').get_text(), profile+'.keys')
                    self.conf.ini.set('mark', self.get('entry15').get_text(), profile+'.keys')
                    self.conf.ini.set('salt', '-¤-ImpraStorage-¤-'          , profile+'.keys')

                    self.conf.ini.set('host', self.get('entry5').get_text() , profile+'.imap')
                    self.conf.ini.set('user', self.get('entry7').get_text() , profile+'.imap')
                    self.conf.ini.set('pass', self.get('entry13').get_text(), profile+'.imap')
                    self.conf.ini.set('port', self.get('entry6').get_text() , profile+'.imap')
                    self.conf.ini.set('box' , '__impra2__'                  , profile+'.imap')

                    self.conf.ini.set('profile', profile, 'main')
                    self.conf.ini.print(profile)
                    self.conf.ini.print('main')

                    self.conf.ini.save()
                    if self.BAD_CONF :
                        self.BAD_CONF = False
                    self.on_delete_event()    
                    self.launch_thread(self.on_ended)
                else :
                    self.get('label42').set_label('can\'t save : '+self.get('label41').get_label())
            
            else :
                self.get('label42').set_label('user name is empty')
            
        else :
            self.get('label42').set_label('profile name is empty')
        #~ self.get('entry3').set_text(profile)
