#!/usr/bin/env python
#----------------------------------------------------------------------
"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on proper mime type handling at the OS level.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmShowMedDocs.py,v $
__version__ = "$Revision: 1.38 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, os, re

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == '__main__':
    _log.SetAllLogLevels(gmLog.lData)
    from Gnumed.pycommon import gmI18N
else:
    from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmCfg, gmWhoAmI, gmPG, gmMimeLib, gmExceptions
from Gnumed.business import gmPatient, gmMedDoc
from Gnumed.wxpython import gmGuiHelpers

from wxPython.wx import *

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()
#----------------------------------------------------------------------
#        self.tree = MyTreeCtrl(self, tID, wxDefaultPosition, wxDefaultSize,
#                               wxTR_HAS_BUTTONS | wxTR_EDIT_LABELS# | wxTR_MULTIPLE
#                               , self.log)

        # NOTE:  For some reason tree items have to have a data object in
        #        order to be sorted.  Since our compare just uses the labels
        #        we don't need any real data, so we'll just use None.

#        EVT_TREE_ITEM_EXPANDED  (self, tID, self.OnItemExpanded)
#        EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
#        EVT_TREE_SEL_CHANGED    (self, tID, self.OnSelChanged)
#        EVT_TREE_BEGIN_LABEL_EDIT(self, tID, self.OnBeginEdit)
#        EVT_TREE_END_LABEL_EDIT (self, tID, self.OnEndEdit)
#        EVT_TREE_ITEM_ACTIVATED (self, tID, self.OnActivate)

#        EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)

[   wxID_PNL_main,
    wxID_TB_BTN_show_page
] = map(lambda _init_ctrls: wxNewId(), range(2))
#================================================================
class cDocTree(wxTreeCtrl):
    """This wxTreeCtrl derivative displays a tree view of stored medical documents.
    """
    def __init__(self, parent, id):
        """Set up our specialised tree.
        """
        # get connection
        self.__backend = gmPG.ConnectionPool()
        self.__defconn = self.__backend.GetConnection('blobs')
        if self.__defconn is None:
            _log.Log(gmLog.lErr, "Cannot retrieve documents without database connection !")
            raise gmExceptions.ConstructorError, "cDocTree.__init__(): need db conn"

        # connect to config database
        self.__dbcfg = gmCfg.cCfgSQL(
            aConn = self.__backend.GetConnection('default'),
            aDBAPI = gmPG.dbapi
        )

        wxTreeCtrl.__init__(self, parent, id, style=wxTR_NO_BUTTONS)

        self.root = None
        self.doc_list = None
        self.curr_pat = gmPatient.gmCurrentPatient()
        _log.Log(gmLog.lData, self.curr_pat)
        # connect handlers
        EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
        EVT_TREE_ITEM_RIGHT_CLICK(self, self.GetId(), self.__on_right_click)
    #------------------------------------------------------------------------
    def update(self):
        if self.curr_pat['ID'] is None:
            _log.Log(gmLog.lErr, 'need patient for update')
            gmGuiHelpers.gm_show_error(
                aMessage = _('Cannot load documents.\nYou first need to select a patient.'),
                aTitle = _('loading document list')
            )
            return None

        if self.doc_list is not None:
            del self.doc_list

        if self.__populate_tree() is None:
            return None

        return 1
    #------------------------------------------------------------------------
    def __populate_tree(self):
        # FIXME: check if patient changed at all

        # clean old tree
        if not self.root is None:
            self.DeleteAllItems()

        # init new tree
        self.root = self.AddRoot(_("available documents (most recent on top)"), -1, -1)
        self.SetPyData(self.root, None)
        self.SetItemHasChildren(self.root, FALSE)

        # read documents from database
        doc_ids = self.curr_pat['document id list']
        if doc_ids is None:
            name = self.curr_pat['demographic record'].getActiveName()
            gmGuiHelpers.gm_show_error(
                aMessage = _('Cannot find any documents for patient\n[%s %s].') % (name['first'], name['last']),
                aTitle = _('loading document list')
            )
            return None

        # fill new tree from document list
        self.SetItemHasChildren(self.root, TRUE)

        # add our documents as first level nodes
        self.doc_list = {}
        for doc_id in doc_ids:
            try:
                doc = gmMedDoc.gmMedDoc(aPKey = doc_id)
            except:
                continue

            self.doc_list[doc_id] = doc
            mdata = doc.get_metadata()
            date = '%10s' % mdata['date'] + " " * 10
            typ = '%s' % mdata['type'] + " " * 25
            cmt = '"%s"' % mdata['comment'] + " " * 25
            ref = mdata['reference'] + " " * 15
            page_num = str(len(mdata['objects']))
            tmp = _('%s %s: %s (%s pages, %s)')
            # FIXME: handle date correctly
            label =  tmp % (date[:10], typ[:25], cmt[:25], page_num, ref[:15])
            doc_node = self.AppendItem(self.root, label)
            self.SetItemBold(doc_node, bold=TRUE)
            # id: doc_med.id for access
            # date: for sorting
            data = {
                'type': 'document',
                'id': doc_id,
                'date': mdata['date']
            }
            self.SetPyData(doc_node, data)
            self.SetItemHasChildren(doc_node, TRUE)

            # now add objects as child nodes
            i = 1
            for obj_id in mdata['objects'].keys():
                obj = mdata['objects'][obj_id]
                p = str(obj['index']) +  " "
                c = str(obj['comment'])
                s = str(obj['size'])
                if c == "None":
                    c = _("no comment available")
                tmp = _('page %s: \"%s\" (%s bytes)')
                label = tmp % (p[:2], c, s)
                obj_node = self.AppendItem(doc_node, label)
                # id = doc_med.id for retrival
                # seq_idx for sorting
                data = {
                    'type': 'object',
                    'id': obj_id,
                    'seq_idx'   : obj['index']
                }
                self.SetPyData(obj_node, data)
                i += 1
            # and expand
            #self.Expand(doc_node)

        # and uncollapse
        self.Expand(self.root)

        return 1
    #------------------------------------------------------------------------
    def OnCompareItems (self, item1, item2):
        """Used in sorting items.

        -1 - 1 < 2
         0 - 1 = 2
         1 - 1 > 2
        """
        data1 = self.GetPyData(item1)
        data2 = self.GetPyData(item2)

        # doc node
        if data1['type'] == 'document':
            # compare dates
            if data1['date'] > data2['date']:
                return -1
            elif data1['date'] == data2['date']:
                return 0
            return 1
        # object node
        else:
            # compare sequence IDs (= "page number")
            if data1['seq_idx'] < data2['seq_idx']:
                return -1
            elif data1['seq_idx'] == data2['seq_idx']:
                return 0
            return 1
    #------------------------------------------------------------------------
    def OnActivate (self, event):
        item = event.GetItem()
        node_data = self.GetPyData(item)

        # exclude pseudo root node
        if node_data is None:
            return None

        # do nothing with documents yet
        if node_data['type'] == 'document':
            return None

        # but do everything with objects
        obj_id = node_data['id']
        _log.Log(gmLog.lData, "User selected object [%s]" % obj_id)

        if __name__ == "__main__":
            tmp = "unknown_machine"
        else:
            tmp = _whoami.get_workplace()

        exp_base = self.__dbcfg.get(
            machine = tmp,
            option = "doc export dir"
        )
        if exp_base is None:
            exp_base = ''
        else:
            exp_base = os.path.abspath(os.path.expanduser(exp_base))
        if not os.path.exists(exp_base):
            _log.Log(gmLog.lErr, "The directory [%s] does not exist ! Falling back to default temporary directory." % exp_base) # which is tempfile.tempdir == None == use system defaults
        else:
            _log.Log(gmLog.lData, "working into directory [%s]" % exp_base)

        # instantiate object
        try:
            obj = gmMedDoc.gmMedObj(aPKey = obj_id)
        except:
            _log.LogException('Cannot instantiate object [%s]' % obj_id, sys.exc_info())
            gmGuiHelpers.gm_show_error(
                aMessage = _('Document part does not seem to exist in database !!'),
                aTitle = _('showing document')
            )
            return None

        if __name__ == "__main__":
            chunksize = None
        else:
            gb = gmGuiBroker.GuiBroker()
            chunksize = self.__dbcfg.get(
                machine = _whoami.get_workplace(),
                option = "doc export chunk size"
            )
        if chunksize is None:
            # 1 MB
            chunksize = 1 * 1024 * 1024

        # make sure metadata is there
        tmp = obj.get_metadata

        # retrieve object
        if not obj.export_to_file(aTempDir = exp_base, aChunkSize = chunksize):
            _log.Log(gmLog.lErr, "Cannot export object [%s] data from database !" % node_data['id'])
            gmGuiHelpers.gm_show_error(
                aMessage = _('Cannot export document part from database to file.'),
                aTitle = _('showing document')
            )
            return None

        fname = obj['filename']
        (result, msg) = gmMimeLib.call_viewer_on_file(fname)
        if not result:
            gmGuiHelpers.gm_show_error(
                aMessage = _('Cannot display object.\n%s.') % msg,
                aTitle = _('displaying page')
            )
            return None
        return 1
    #--------------------------------------------------------
    def __on_right_click(self, evt):
        item = evt.GetItem()
        node_data = self.GetPyData(item)

        # exclude pseudo root node
        if node_data is None:
            return None

        # objects
        if node_data['type'] == 'object':
            self.__handle_obj_context(node_data)

        # documents
        if node_data['type'] == 'document':
            self.__handle_doc_context(node_data)

        evt.Skip()
    #--------------------------------------------------------
    def __handle_doc_context(self, data):
        doc_id = data['id']
        try:
            doc = gmMedDoc.gmMedDoc(aPKey = doc_id)
        except:
            _log.LogException('Cannot init document [%s]' % doc_id, sys.exc_info())
            # FIXME: message box
            return None

        descriptions = doc['descriptions']

        # build menu
        wxIDs_desc = []
        desc_menu = wxMenu()
        for desc in descriptions:
            d_id = wxNewId()
            wxIDs_desc.append(d_id)
            # contract string
            tmp = re.split('\r\n+|\r+|\n+|\s+|\t+', desc)
            tmp = string.join(tmp, ' ')
            # but only use first 30 characters
            tmp = "%s ..." % tmp[:30]
            desc_menu.AppendItem(wxMenuItem(desc_menu, d_id, tmp))
            # connect handler
            EVT_MENU(desc_menu, d_id, self.__show_description)
        wxID_load_submenu = wxNewId()
        menu = wxMenu(title = _('document menu'))
        menu.AppendMenu(wxID_load_submenu, _('descriptions ...'), desc_menu)
        self.PopupMenu(menu, wxPyDefaultPosition)
        menu.Destroy()
    #--------------------------------------------------------
    def __show_description(self, evt):
        print "showing description"
    #--------------------------------------------------------
    def __handle_obj_context(self, data):
        print "handling object context menu"
    #--------------------------------------------------------

########### may become obsolete
    def __show_error(self, aMessage = None, aTitle = ''):
        # sanity checks
        tmp = aMessage
        if aMessage is None:
            tmp = _('programmer forgot to specify error message')

        tmp = tmp + _("\n\nPlease consult the error log for further information !")

        dlg = wxMessageDialog(
            NULL,
            tmp,
            aTitle,
            wxOK | wxICON_ERROR
        )
        dlg.ShowModal()
        dlg.Destroy()
        return 1
#== classes for standalone use ==================================
if __name__ == '__main__':

    from Gnumed.pycommon import gmLoginInfo
    from Gnumed.business import gmXdtObjects, gmXdtMappings

    wxID_btn_quit = wxNewId()

    class cStandalonePanel(wxPanel):

        def __init__(self, parent, id):
            # get patient from file
            if self.__get_pat_data() is None:
                raise gmExceptions.ConstructorError, "Cannot load patient data."

            # set up database connectivity
            auth_data = gmLoginInfo.LoginInfo(
                user = _cfg.get('database', 'user'),
                passwd = _cfg.get('database', 'password'),
                host = _cfg.get('database', 'host'),
                port = _cfg.get('database', 'port'),
                database = _cfg.get('database', 'database')
            )
            backend = gmPG.ConnectionPool(login = auth_data)

            # mangle date of birth into ISO8601 (yyyymmdd) for Postgres
            cooked_search_terms = {
                #'globbing': None,
                #'case sensitive': None,
                'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
                'lastnames': self.__xdt_pat['last name'],
                #'gender': self.__xdt_pat['gender'],
                'firstnames': self.__xdt_pat['first name']
            }

            # find matching patient IDs
            searcher = gmPatient.cPatientSearcher_SQL()
            patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
            if patient_ids is None:
                gmGuiHelpers.gm_show_error(
                    aMessage = _('This patient does not exist in the document database.\n"%s %s"') % (self.__xdt_pat['first name'], self.__xdt_pat['last name']),
                    aTitle = _('searching patient')
                )
                _log.Log(gmLog.lPanic, self.__xdt_pat['all'])
                raise gmExceptions.ConstructorError, "Patient from XDT file does not exist in database."

            # ambigous ?
            if len(patient_ids) != 1:
                gmGuiHelpers.gm_show_error(
                    aMessage = _('Data in xDT file matches more than one patient in database !'),
                    aTitle = _('searching patient')
                )
                _log.Log(gmLog.lPanic, self.__xdt_pat['all'])
                raise gmExceptions.ConstructorError, "Problem getting patient ID from database. Aborting."

            try:
                gm_pat = gmPatient.gmCurrentPatient(aPKey = patient_ids[0])
            except:
                # this is an emergency
                gmGuiHelpers.gm_show_error(
                    aMessage = _('Cannot load patient from database !\nAborting.'),
                    aTitle = _('searching patient')
                )
                _log.Log(gmLog.lPanic, 'Cannot access patient [%s] in database.' % patient_ids[0])
                _log.Log(gmLog.lPanic, self.__xdt_pat['all'])
                raise

            # make main panel
            wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
            self.SetTitle(_("stored medical documents"))

            # make patient panel
            gender = gmPatient.gm2long_gender_map[gmXdtMappings.xdt_gmgender_map[self.__xdt_pat['gender']]]
            self.pat_panel = wxStaticText(
                id = -1,
                parent = self,
                label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
                style = wxALIGN_CENTER
            )
            self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

            # make document tree
            self.tree = cDocTree(self, -1)
            self.tree.update()
            self.tree.SelectItem(self.tree.root)

            # buttons
            btn_quit = wxButton(
                parent = self,
                id = wxID_btn_quit,
                label = _('Quit')
            )
            EVT_BUTTON (btn_quit, wxID_btn_quit, self.__on_quit)
            szr_buttons = wxBoxSizer(wxHORIZONTAL)
            szr_buttons.Add(btn_quit, 0, wxALIGN_CENTER_VERTICAL, 1)

            szr_main = wxBoxSizer(wxVERTICAL)
            szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
            szr_main.Add(self.tree, 1, wxEXPAND, 9)
            szr_main.Add(szr_buttons, 0, wxEXPAND, 1)

            self.SetAutoLayout(1)
            self.SetSizer(szr_main)
            szr_main.Fit(self)
            self.Layout()
        #--------------------------------------------------------
        def __get_pat_data(self):
            """Get data of patient for which to retrieve documents.

            """
            # FIXME: error checking
            pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
            # FIXME: actually handle pat_format, too
            pat_format = _cfg.get("viewer", "patient file format")

            # get patient data from BDT file
            try:
                self.__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
            except:
                _log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
                gmGuiHelpers.gm_show_error(
                    aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
                    aTitle = _('loading patient from xDT file')
                )
                return None

            return 1
        #--------------------------------------------------------
        def __on_quit(self, evt):
            app = wxGetApp()
            app.ExitMainLoop()
#== classes for plugin use ======================================
else:
    class cPluginTreePanel(wxPanel):
        def __init__(self, parent, id):
            # set up widgets
            wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

            # make document tree
            self.tree = cDocTree(self, -1)

            # just one vertical sizer
            sizer = wxBoxSizer(wxVERTICAL)
            sizer.Add(self.tree, 1, wxEXPAND, 0)
            self.SetAutoLayout(1)
            self.SetSizer(sizer)
            sizer.Fit(self)
            self.Layout()
        #--------------------------------------------------------
        def __del__(self):
            # FIXME: return service handle
            #self.DB.disconnect()
            pass

    #------------------------------------------------------------
    from Gnumed.wxpython import gmPlugin, images_Archive_plugin, images_Archive_plugin1

    class gmShowMedDocs(gmPlugin.wxNotebookPlugin):
        tab_name = _("Documents")

        def name (self):
            return gmShowMedDocs.tab_name

        def GetWidget (self, parent):
            self.panel = cPluginTreePanel(parent, -1)
            return self.panel

        def MenuInfo (self):
            return ('tools', _('Show &archived documents'))

        def ReceiveFocus(self):
            if self.panel.tree.update() is None:
                _log.Log(gmLog.lErr, "cannot update document tree")
                return None
            # FIXME: register interest in patient_changed signal, too
            self.panel.tree.SelectItem(self.panel.tree.root)
            return 1

        def can_receive_focus(self):
            # need patient
            if not self._verify_patient_avail():
                return None
            return 1

        def DoToolbar (self, tb, widget):
            #tool1 = tb.AddTool(
            #   wxID_PNL_BTN_load_pages,
            #   images_Archive_plugin.getcontentsBitmap(),
            #   shortHelpString=_("load pages"),
            #   isToggle=false
            #)
            #EVT_TOOL (tb, wxID_PNL_BTN_load_pages, widget.on_load_pages)

            #tool1 = tb.AddTool(
            #   wxID_PNL_BTN_save_data,
            #   images_Archive_plugin.getsaveBitmap(),
            #   shortHelpString=_("save document"),
            #   isToggle=false
            #)
            #EVT_TOOL (tb, wxID_PNL_BTN_save_data, widget.on_save_data)
            
            #tool1 = tb.AddTool(
            #   wxID_PNL_BTN_del_page,
            #   images_Archive_plugin.getcontentsBitmap(),
            #   shortHelpString=_("delete page"),
            #   isToggle=false
            #)
            #EVT_TOOL (tb, wxID_PNL_BTN_del_page, widget.on_del_page)
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_show_page,
                images_Archive_plugin.getreportsBitmap(),
                shortHelpString=_("show document"),
                isToggle=false
            )
            EVT_TOOL (tb, wxID_TB_BTN_show_page, cDocTree.OnActivate)
    
            #tool1 = tb.AddTool(
            #   wxID_PNL_BTN_select_files,
            #   images_Archive_plugin1.getfoldersearchBitmap(),
            #   shortHelpString=_("select files"),
            #   isToggle=false
            #)
            #EVT_TOOL (tb, wxID_PNL_BTN_select_files, widget.on_select_files)
        
            tb.AddControl(wxStaticBitmap(
                tb,
                -1,
                images_Archive_plugin.getvertical_separator_thinBitmap(),
                wxDefaultPosition,
                wxDefaultSize
            ))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
    _log.Log (gmLog.lInfo, "starting display handler")

    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    # catch all remaining exceptions
    try:
        application = wxPyWidgetTester(size=(640,480))
        application.SetWidget(cStandalonePanel,-1)
        application.MainLoop()
    except:
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise

    _log.Log (gmLog.lInfo, "closing display handler")
else:
    # we are being imported
    pass
#================================================================
# $Log: gmShowMedDocs.py,v $
# Revision 1.38  2004-03-19 21:26:15  shilbert
# - more module import fixes
#
# Revision 1.37  2004/03/19 08:29:21  ncq
# - fix spurious whitespace
#
# Revision 1.36  2004/03/19 08:08:41  ncq
# - fix import of gmLoginInfo
# - remove dead code
#
# Revision 1.35  2004/03/07 22:19:26  ncq
# - proper import
# - re-fix gmTmpPatient -> gmPatient (fallout from "Syan's commit")
#
# Revision 1.34  2004/03/06 21:52:02  shilbert
# - adapted code to new API since __set/getitem is gone
#
# Revision 1.33  2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.32  2004/01/06 23:19:52  ncq
# - use whoami
#
# Revision 1.31  2003/11/17 10:56:40  sjtan
#
# synced and commiting.
#
# Revision 1.30  2003/11/16 11:53:32  shilbert
# - fixed stanalone mode
# - makes use of toolbar
#
# Revision 1.29  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.28  2003/08/27 12:31:41  ncq
# - some cleanup
#
# Revision 1.27  2003/08/24 12:50:20  shilbert
# - converted from __show_error() to gmGUIHelpers.gm_show_error()
#
# Revision 1.26  2003/06/29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.25  2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.24  2003/06/19 15:31:37  ncq
# - cleanup, page change vetoing
#
# Revision 1.23  2003/04/28 12:11:30  ncq
# - refactor name() to not directly return _(<name>)
#
# Revision 1.22  2003/04/20 15:39:36  ncq
# - call_viewer was moved to gmMimeLib
#
# Revision 1.21  2003/04/19 15:01:33  ncq
# - we need import re both standalone and plugin
#
# Revision 1.20  2003/04/18 22:34:44  ncq
# - document context menu, mainly for descriptions, currently
#
# Revision 1.19  2003/04/18 17:45:05  ncq
# - add quit button
#
# Revision 1.18  2003/04/18 16:40:04  ncq
# - works again as standalone
#
# Revision 1.17  2003/04/04 20:49:22  ncq
# - make plugin work with gmCurrentPatient
#
# Revision 1.16  2003/04/01 12:31:53  ncq
# - we can't use constant reference self.patient if we don't register interest
#   in gmSignals.patient_changed, hence, acquire patient when needed
#
# Revision 1.15  2003/03/25 19:57:09  ncq
# - add helper __show_error()
#
# Revision 1.14  2003/03/23 02:38:46  ncq
# - updated Hilmar's fix
#
# Revision 1.13  2003/03/02 17:03:19  ncq
# - make sure metadata is retrieved
#
# Revision 1.12  2003/03/02 11:13:01  hinnef
# preliminary fix for crash on ReceiveFocus()
#
# Revision 1.11  2003/02/25 23:30:31  ncq
# - need sys.exc_info() in LogException
#
# Revision 1.10  2003/02/24 23:14:53  ncq
# - adapt to get_patient_ids actually returning a flat list of IDs now
#
# Revision 1.9  2003/02/21 13:54:17  ncq
# - added even more likely and unlikely user warnings
#
# Revision 1.8  2003/02/20 01:25:18  ncq
# - read login data from config file again
#
# Revision 1.7  2003/02/19 15:19:43  ncq
# - remove extra print()
#
# Revision 1.6  2003/02/18 02:45:21  ncq
# - almost fixed standalone mode again
#
# Revision 1.5  2003/02/17 16:10:50  ncq
# - plugin mode seems to be fully working, actually calls viewers on files
#
# Revision 1.4  2003/02/15 14:21:49  ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.3  2003/02/11 18:26:16  ncq
# - fix exp_base buglet in OnActivate
#
# Revision 1.2  2003/02/09 23:41:09  ncq
# - reget doc list on receiving focus thus being able to react to selection of a different patient
#
# Revision 1.1  2003/02/09 20:07:31  ncq
# - works as a plugin, patient hardcoded, though
#
# Revision 1.8  2003/01/26 17:00:18  ncq
# - support chunked object retrieval
#
# Revision 1.7  2003/01/25 00:21:42  ncq
# - show nr of bytes on object in metadata :-)
#
