#!/usr/bin/python
#=====================================================
# TODO:
#  - if no xDT file found
#    * browse GnuMed patient database
#    * allow patient data input
#  - cancel-quit button
#  - load external file(s) (fax, digicam etc.)
#  - wxDateEntry() mit ordentlichem Validator
#  - Funktion Seiten umsortieren fertigstellen
#  - phrasewheel on Kurzkommentar
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmScanIdxMedDocs.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

try:
    import wxversion
    import wx
except ImportError:
    from wxPython import wx


#import Image
import os, time, shutil, os.path

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
    _log.SetAllLogLevels(gmLog.lData)

from Gnumed.pycommon import gmCfg, gmMatchProvider, gmExceptions, gmI18N
from Gnumed.business import gmXmlDocDesc, gmXdtObjects
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel
from Gnumed.wxGladeWidgets import wxgScanIdxPanel

_cfg = gmCfg.gmDefCfgFile

[   wxID_indexPnl,
    wxID_TBOX_desc_long,
    wxID_indexPnlBEFNRBOX,
    wxID_TBOX_doc_date,
    wxID_TBOX_dob,
    wxID_BTN_del_page,
    wxID_BTN_select_files,
    wxID_BTN_save_data,
    wxID_BTN_show_page,
    wxID_BTN_load_pages,
    wxID_TB_BTN_del_page,
    wxID_TB_BTN_select_files,
    wxID_TB_BTN_save_data,
    wxID_TB_BTN_show_page,
    wxID_TB_BTN_load_pages,
    wxID_TB_BTN_aquire_docs,
    wxID_TB_BTN_show_dirs_in_repository,
    wxID_SelBOX_doc_type,
    wxID_TBOX_first_name,
    wxID_TBOX_last_name,
    wxID_LBOX_doc_pages,
    wxID_TBOX_desc_short,
    wxID_PNL_main
] = map(lambda _init_ctrls: wx.NewId(), range(23))
#====================================
class cDocWheel(gmPhraseWheel.cPhraseWheel):
    def __init__(self, parent):
        # FIXME: we need to set this to non-learning mode
        self.mp = gmMatchProvider.cMatchProvider_FixedList([])
        self.mp.setWordSeparators(separators = '[ \t=+&:@]+')
        
        gmPhraseWheel.cPhraseWheel.__init__(
            self,
            parent = parent,
            id = -1,
            aMatchProvider = self.mp,
            size = wx.DefaultSize,
            pos = wx.DefaultPosition
            #self.wheel_callback
        )
        self.SetToolTipString(_('the document identifier is usually written or stamped onto the physical pages of the document'))
    #--------------------------------
    def update_choices(self, aRepository):
        doc_dirs = self.get_choices(aRepository)
        self.mp.setItems(doc_dirs)
        self.Clear()
    #--------------------------------
    def get_choices(self, aRepository = None):
        """Return a list of dirs that can be indexed.

        - directory names in self.repository correspond to
          identification strings on paper documents
        - when starting to type an ident the phrase
          wheel must show matching directories
        """
        # get document directories
        doc_dirs = os.listdir(aRepository)

        # generate list of choices
        phrase_wheel_choices = []
        for i in range(len(doc_dirs)):
            full_dir = os.path.join(aRepository, doc_dirs[i])

            # don't add stray files
            if not os.path.isdir(full_dir):
                _log.Log(gmLog.lData, "ignoring stray file [%s]" % doc_dirs[i])
                continue

            if not self.__could_be_locked(full_dir):
                _log.Log(gmLog.lInfo, "Document directory [%s] not checkpointed for indexing. Skipping." % full_dir)
                continue

            # same weight for all of them
            phrase_wheel_choices.append({'data': i, 'label': doc_dirs[i], 'weight': 1})

        #<DEBUG>
        _log.Log(gmLog.lData, "document dirs: %s" % str(phrase_wheel_choices))
        #</DEBUG>

        if len(phrase_wheel_choices) == 0:
            _log.Log(gmLog.lWarn, "No document directories in repository. Nothing to do.")
            dlg = wx.MessageDialog(
                self,
                _("There are no documents in the repository.\n(%s)\n\nSeems like there's nothing to do today." % aRepository),
                _('Information'),
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            
        return phrase_wheel_choices
    #----------------------------------------
    def __could_be_locked(self, aDir):
        """check whether we _could_ acquire the lock for indexing

        i.e., whether we should worry about this directory at all
        """
        # FIXME: embedded -> database !
        indexing_file = os.path.join(aDir, _cfg.get("index", "lock file"))
        can_index_file = os.path.join(aDir, _cfg.get("index", "checkpoint file"))
        cookie = _cfg.get("index", "cookie")

        # 1) anyone indexing already ?
        if os.path.exists(indexing_file):
            _log.Log(gmLog.lInfo, 'Indexing lock [%s] exists.' % indexing_file)
            # did _we_ lock this dir earlier and then died unexpectedly ?
            fhandle = open(indexing_file, 'r')
            tmp = fhandle.readline()
            fhandle.close()
            tmp = string.replace(tmp,'\015','')
            tmp = string.replace(tmp,'\012','')
            # yep, it's our cookie
            if (tmp == cookie) and (os.path.exists(can_index_file)):
                _log.Log(gmLog.lInfo, 'Seems like *we* locked this directory.')
                _log.Log(gmLog.lInfo, 'At least it is locked with our cookie ([%s]).' % cookie)
                _log.Log(gmLog.lInfo, 'Unlocking directory.')
                os.remove(indexing_file)
            # nope, someone else
            else:
                return None

        # 2) check for ready-for-indexing checkpoint
        if not os.path.exists(can_index_file):
            _log.Log(gmLog.lInfo, 'Checkpoint [%s] does not exist.' % can_index_file)
            return None

        return 1
#====================================
class myScanIdxPanel(wxgScanIdxPanel):
    def __init__(self, parent):
        # provide repository
        self.__get_repository()

        # provide valid choices for document types
        self.__get_valid_doc_types()
    
        #wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize)

        ## set up GUI
        #self._init_ctrls()
        #self.__set_properties()
        #self.__do_layout()

        ## we are indexing data of one particular patient
        ## this is a design decision
        #if __name__ == '__main__':
        #    if not self.__load_patient_from_file():
        #        raise gmExceptions.ConstructorError, 'cannot load patient from file'
        #    self.fill_pat_fields()
        #    self.doc_id_wheel.update_choices(self.repository)
        #else:
        #    self.doc_id_wheel = None
    #--------------------------------------
    """def _init_ctrls(self):

        # -- main panel -----------------------
        self.PNL_main = wx.Panel(
            id = wxID_PNL_main,
            name = 'main panel',
            parent = self,
            style = wx.TAB_TRAVERSAL
        )
        #-- left column -----------------------
        self.lbl_left_header = wx.StaticText(
            id = -1,
            name = 'lbl_left_header',
            parent = self.PNL_main,
            label = _("1) select")
        )
        self.lbl_left_header.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
        #--- document ID phrase wheel ---------
        if __name__ == '__main__':
            self.lbl_doc_id_wheel = wx.StaticText(
                id =  -1,
                name = 'lbl_doc_id_wheel',
                parent = self.PNL_main,
                label = _("document identifier")
            )
            #--------------------------------------
        
            self.doc_id_wheel = cDocWheel(self.PNL_main)
            self.doc_id_wheel.on_resize (None)
            # -- load pages button ----------------
            self.BTN_load_pages = wx.Button(
                id = wxID_BTN_load_pages,
                name = 'BTN_load_pages',
                parent = self.PNL_main,
                label = _("load pages")
            )
            self.BTN_load_pages.SetToolTipString(_('load the pages of this document'))
            wx.EVT_BUTTON(self.BTN_load_pages, wxID_BTN_load_pages, self.on_load_pages)
            #--------------------------------------
            self.staticText4 = wx.StaticText(
                id = -1,
                name = 'staticText4',
                parent = self.PNL_main,
                label = _("or")
            )
            self.staticText4.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
            # -- select files button --------------
            self.BTN_select_files = wx.Button(
                id = wxID_BTN_select_files,
                name = 'BTN_select_files',
                parent = self.PNL_main,
                label = _("load fax document")
            )
            self.BTN_select_files.SetToolTipString(_('currently non-functional: load a fax document'))
            wx.EVT_BUTTON(self.BTN_select_files, wx.ID_BTN_select_files, self.on_select_files)
        #--------------------------------------
        self.lbl_doc_pages = wx.StaticText(
            id = -1,
            name = 'lbl_doc_pages',
            parent = self.PNL_main,
            label = _("document pages")
        )
        # -- list box with pages --------------
        self.LBOX_doc_pages = wx.ListBox(
                id = wxID_LBOX_doc_pages,
            name = 'LBOX_doc_pages',
                parent = self.PNL_main,
            style = wx.LB_SORT,
            choices=[]
        )
        # -- show page button -----------------
        self.BTN_show_page = wx.Button(
            id = wxID_BTN_show_page,
            name = 'BTN_show_page',
            parent = self.PNL_main,
            label = _("show page")
        )
        # -- delete page button ---------------
        self.BTN_del_page = wx.Button(
            id = wxID_BTN_del_page,
            name = 'BTN_del_page',
            parent = self.PNL_main,
            label = _("delete page")
        )

        #-- middle column ---------------------
        self.lbl_middle_header = wx.StaticText(
            id = -1,
            name = 'lbl_middle_header',
            parent = self.PNL_main,
            label = _("2) describe")
        )
        self.lbl_middle_header.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
        #--------------------------------------
        if __name__ == '__main__':
            self.lbl_first_name = wx.StaticText(
                id = -1,
                name = 'lbl_first_name',
                parent = self.PNL_main,
                label = _("first name")
            )
            # -- first name text box --------------
            self.TBOX_first_name = wx.TextCtrl(
                id = wxID_TBOX_first_name,
                name = 'TBOX_first_name',
                parent = self.PNL_main,
                value = _("loading ..."),
                style=wx.TE_READONLY
            )
            self.TBOX_first_name.Enable(False)
            self.TBOX_first_name.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.TBOX_first_name.SetToolTipString(_('not editable, loaded from file'))
            #--------------------------------------
            self.lbl_last_name = wx.StaticText(
                id = -1,
                name = 'lbl_last_name',
                parent = self.PNL_main,
                label = _("last name")
            )
            # -- last name text box ---------------
            self.TBOX_last_name = wx.TextCtrl(
                id = wxID_TBOX_last_name,
                name = 'TBOX_last_name',
                parent = self.PNL_main,
                value = _("loading ..."),
                style=wx.TE_READONLY
            )
            self.TBOX_last_name.Enable(False)
            self.TBOX_last_name.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.TBOX_last_name.SetToolTipString(_('not editable, loaded from file'))
            #--------------------------------------
            self.lbl_dob = wx.StaticText(
                id = -1,
                name = 'lbl_dob',
                parent = self.PNL_main,
                label = _("date of birth")
            )
            # -- dob text box ---------------------
            self.TBOX_dob = wx.TextCtrl(
                id = wxID_TBOX_dob,
                name = 'TBOX_dob',
                parent = self.PNL_main,
                value = _("loading ..."), 
                style=wx.TE_READONLY
            )
            self.TBOX_dob.Enable(False)
            self.TBOX_dob.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.TBOX_dob.SetToolTipString(_('not editable, loaded from file'))
        #--------------------------------------
        self.lbl_doc_date = wx.StaticText(
            id =  -1,
            name = 'lbl_doc_date',
            parent = self.PNL_main,
            label = _("date (YYYY-MM-DD)")
        )
        # -- document creation text box -------
        self.TBOX_doc_date = wx.TextCtrl(
            id = wxID_TBOX_doc_date,
            name = 'TBOX_doc_date',
            parent = self.PNL_main,
            # FIXME: default date should be changeable
            value = time.strftime('%Y-%m-%d',time.localtime())
        )
        #--------------------------------------
        self.lbl_desc_short = wx.StaticText(
            id = -1,
            name = 'lbl_desc_short',
            parent = self.PNL_main,
            label = _("short comment")
        )
        # -- short document comment text box --
        self.TBOX_desc_short = wx.TextCtrl(
            id = wxID_TBOX_desc_short,
            name = 'TBOX_desc_short',
            parent = self.PNL_main,
            value = _("please fill in")
        )
        #--------------------------------------
        self.lbl_doc_type = wx.StaticText(
            id = -1,
            name = 'lbl_doc_type',
            parent = self.PNL_main,
            label = _("document type")
        )
        # -- document type selection box ------
        self.SelBOX_doc_type = wx.ComboBox(
            id = wxID_SelBOX_doc_type,
            name = 'SelBOX_doc_type',
            parent = self.PNL_main,
            value = _('choose document type'),
            choices = self.valid_doc_types,
            style=wx.CB_DROPDOWN
        )
        self.SelBOX_doc_type.SetLabel('')
        
        #-- right column ----------------------
        self.lbl_right_header = wx.StaticText(
            id = -1,
            name = 'lbl_right_header',
            parent = self.PNL_main,
            label = _("3) save")
        )
        self.lbl_right_header.SetFont(wx.Font(25, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
        # -- save data button -----------------
        self.BTN_save_data = wx.Button(
            id = wxID_BTN_save_data,
            name = 'BTN_save_data',
            parent = self.PNL_main,
            label = _("save data")
        )

        #-- bottom area -----------------------
        self.lbl_desc_long = wx.StaticText(
            id = -1,
            name = 'lbl_desc_long',
            parent = self.PNL_main,
            label = _("additional comment")
        )
        # -- long document comment text box ---
        self.TBOX_desc_long = wx.TextCtrl(
            id = wxID_TBOX_desc_long,
            name = 'TBOX_desc_long',
            parent = self.PNL_main,
            value = "",
            style=wx.TE_MULTILINE
        )
    """
    #--------------------------------
    """def __set_properties(self):
        self.SetTitle(_("GnuMed/Archiv: Associating documents with patients."))

        self.PNL_main.SetBackgroundColour(wx.Colour(225, 225, 225))
        
        self.LBOX_doc_pages.SetToolTipString(_('these pages make up the current document'))
        self.BTN_show_page.SetToolTipString(_('display selected part of the document'))
        self.BTN_del_page.SetToolTipString(_('delete selected part of the document'))
        
        self.TBOX_doc_date.SetToolTipString(_('date of creation of the document content\nformat: YYYY-MM-DD'))
        self.TBOX_desc_short.SetToolTipString(_('a short comment on the document content'))
        self.SelBOX_doc_type.SetToolTipString(_('Document types are determined by the database.\nAsk your database administrator to add more types if needed.'))
        self.BTN_save_data.SetToolTipString(_('save entered metadata with document'))
        self.TBOX_desc_long.SetToolTipString(_('a summary or longer comment for this document'))
        
        wx.EVT_BUTTON(self.BTN_show_page, wxID_BTN_show_page, self.on_show_page)
        wx.EVT_BUTTON(self.BTN_del_page, wxID_BTN_del_page, self.on_del_page)
        wx.EVT_BUTTON(self.BTN_save_data, wxID_BTN_save_data, self.on_save_data)
        wx.EVT_BUTTON(self.BTN_save_data, wxID_BTN_save_data, self.on_save_data)
        

        self.LBOX_doc_pages.SetSelection(0)
        self.SelBOX_doc_type.SetSelection(0)
    """
    #--------------------------------
    """def __do_layout(self):

        szr_main_outer = wx.BoxSizer(wx.HORIZONTAL)

        # left vertical column (1/3) in upper half of the screen
        szr_left = wx.BoxSizer(wx.VERTICAL)
        szr_left.Add(self.lbl_left_header, 0, 0, 0)
        if __name__ == '__main__':
            szr_left.Add(self.lbl_doc_id_wheel, 0, wx.LEFT|wx.TOP, 5)
            szr_left.Add(self.doc_id_wheel, 0, wx.EXPAND|wx.ALL, 5)
            szr_left.Add(self.BTN_load_pages, 1, wx.EXPAND|wx.ALL, 5)
            szr_left.Add(self.staticText4, 0, wx.LEFT, 5)
            szr_left.Add(self.BTN_select_files, 1, wx.EXPAND|wx.ALL, 5)
        szr_left.Add(self.lbl_doc_pages, 0, wx.LEFT, 5)
        szr_left.Add(self.LBOX_doc_pages, 1, wx.EXPAND|wx.ALL, 5)
        szr_left_btns = wx.BoxSizer(wx.HORIZONTAL)
        szr_left_btns.Add(self.BTN_show_page, 1, wx.RIGHT|wx.TOP, 5)
        szr_left_btns.Add(self.BTN_del_page, 1, wx.TOP, 5)
        szr_left.Add(szr_left_btns, 1, wx.EXPAND|wx.ALIGN_BOTTOM, 0)

        # middle vertical column (2/3) in upper half of the screen
        szr_middle = wx.BoxSizer(wx.VERTICAL)
        szr_middle.Add(self.lbl_middle_header, 0, 0, 0)
        if __name__ == '__main__':
            szr_middle.Add(self.lbl_first_name, 0, wx.LEFT|wx.TOP, 5)
            szr_middle.Add(self.TBOX_first_name, 0, wx.EXPAND|wx.ALL, 5)
            szr_middle.Add(self.lbl_last_name, 0, wx.LEFT, 5)
            szr_middle.Add(self.TBOX_last_name, 0, wx.EXPAND|wx.ALL, 5)
            szr_middle.Add(self.lbl_dob, 0, wx.LEFT, 5)
            szr_middle.Add(self.TBOX_dob, 0, wx.EXPAND|wx.ALL, 5)
        szr_middle.Add(self.lbl_doc_date, 0, wx.LEFT, 5)
        szr_middle.Add(self.TBOX_doc_date, 0, wx.EXPAND|wx.ALL, 5)
        szr_middle.Add(self.lbl_desc_short, 0, wx.LEFT, 5)
        szr_middle.Add(self.TBOX_desc_short, 0, wx.EXPAND|wx.ALL, 5)
        szr_middle.Add(self.lbl_doc_type, 0, wx.LEFT, 5)
        szr_middle.Add(self.SelBOX_doc_type, 0, wx.EXPAND|wx.ALL, 5)
        
        # rightmost vertical column (3/3) in upper half of the screen
        szr_right = wx.BoxSizer(wx.VERTICAL)
        szr_right.Add(self.lbl_right_header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 20)
        szr_right.Add(self.BTN_save_data, 1, wx.EXPAND, 0)

        # group columns
        szr_top_grid = wx.GridSizer(1, 3, 0, 0)
        szr_top_grid.Add(szr_left, 1, wx.EXPAND|wx.LEFT, 40)
        szr_top_grid.Add(szr_middle, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, 40)
        szr_top_grid.Add(szr_right, 1, wx.ALIGN_RIGHT|wx.EXPAND|wx.LEFT|wx.RIGHT, 20)

        # single textbox area in lower half of the screen
        szr_bottom = wx.BoxSizer(wx.VERTICAL)
        szr_bottom.Add(self.lbl_desc_long, 0, wx.BOTTOM, 5)
        szr_bottom.Add(self.TBOX_desc_long, 1, wx.EXPAND, 0)

        # group top and bottom parts
        szr_main_inner = wx.BoxSizer(wx.VERTICAL)
        szr_main_inner.Add(szr_top_grid, 2, wx.EXPAND, 0)
        szr_main_inner.Add(szr_bottom, 1, wx.EXPAND|wx.ALL, 20)

        self.PNL_main.SetAutoLayout(1)
        self.PNL_main.SetSizer(szr_main_inner)
        szr_main_inner.Fit(self.PNL_main)
        szr_main_outer.Add(self.PNL_main, 1, wx.EXPAND, 0)
        self.SetAutoLayout(1)
        self.SetSizer(szr_main_outer)
        szr_main_outer.Fit(self)
        self.Layout()
    """
    #--------------------------------
    def __get_valid_doc_types(self):
        # running standalone ? -> configfile
        if __name__ == '__main__':
            self.valid_doc_types = _cfg.get("metadata", "doctypes")
        # we run embedded -> query database
        else:   
            doc_types = []
            cmd = "SELECT name FROM blobs.doc_type"
            rows = gmPG.run_ro_query('blobs', cmd)
            # FIXME: error handling
            for row in rows:
                doc_types.append(row[0])
            self.valid_doc_types = doc_types
    #--------------------------------
    def __get_repository(self):
        # running standalone ? -> configfile
        if __name__ == '__main__':
            # repository base
            self.repository = os.path.abspath(os.path.expanduser(_cfg.get("index", "repository")))
            if not os.path.exists(self.repository):
                msg = _('Repository directory [%s] does not exist.' % self.repository)
                gm_show_error(
                msg,
                _('starting document indexer')
                )
                raise ConstructorError, msg
        # we run embedded -> query database
        else :
            # fixme : needs to be read from db
            self.repository = '/home/basti/gnumed/repository'
    #----------------------------------------
    def set_wheel_link(self, aWheel):
        self.doc_id_wheel = aWheel
    #----------------------------------------
    # event handlers
    #----------------------------------------
    def on_load_pages(self, event):
        curr_doc_id = self.doc_id_wheel.GetLineText(0)

        # has the user supplied anything ?
        if curr_doc_id == '':
            _log.Log(gmLog.lErr, 'No document ID typed in yet !')
            gm_show_error (
                _('You must type in a document ID !\n\nUsually you will find the document ID written on\nthe physical sheet of paper. There should only be one\nper document even if there are multiple pages.'),
                _('loading document')
            )
            return None

        full_dir = os.path.join(self.repository, curr_doc_id)

        # lock this directory now
        if not self.__lock_for_indexing(full_dir):
            _log.Log(gmLog.lErr, "Cannot lock directory [%s] for indexing." % full_dir)
            gm_show_error (
                _('Cannot lock document directory for indexing.\n(%s)' % full_dir),
                _('loading document')
            )
            return None

        # actually try loading pages
        if not self.__load_doc(full_dir):
            _log.Log(gmLog.lErr, "Cannot load document object file list.")
            gm_show_error (
                _('Cannot load document object file list.'),
                _('loading document')
            )
            return None

        self.__fill_doc_fields()
    #----------------------------------------
    def on_save_data(self, event):
        """Save collected metadata into XML file."""

        if not self.__valid_input():
            return None
        else:
            full_dir = os.path.join(self.repository, self.doc_id_wheel.GetLineText(0))
            self.__dump_metadata_to_xml(full_dir)
            if not self.__keep_patient_file(full_dir):
                return None
            self.__unlock_for_import(full_dir)
            self.__clear_doc_fields()
            self.doc_id_wheel.update_choices(self.repository)
    #----------------------------------------
    def on_show_page(self, event):
        # did user select a page ?
        page_idx = self.LBOX_doc_pages.GetSelection()

        if page_idx == -1:
            dlg = wx.MessageDialog(
                self,
                _('You must select a page before you can view it.'),
                _('displaying page'),
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return None

        # now, which file was that again ?
        page_data = self.LBOX_doc_pages.GetClientData(page_idx)
        page_fname = page_data['file name']

        import gmMimeLib
        (result, msg) = gmMimeLib.call_viewer_on_file(page_fname)
        if not result:
            gm_show_error (
                _('Cannot display page %s.\n%s') % (page_idx+1, msg),
                _('displaying page')
            )
            return None
        return 1
    #----------------------------------------
    def on_show_doc_dirs(self, event):
        choices = []
        doc_dirs = self.doc_id_wheel.get_choices( aRepository = self.repository)
        for i in doc_dirs:
            choices.append(i['label'])
            dlg = wx.SingleChoiceDialog(
                self,
                _('You must select a directory before you can index its documents.'),
                _('showing indexable document directories'),
                choices,
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return None
    
    
    #----------------------------------------
    def on_del_page(self, event):
        page_idx = self.LBOX_doc_pages.GetSelection()

        if page_idx == -1:
            dlg = wx.MessageDialog(
                self,
                _('You must select a page before you can delete it.'),
                _('deleting page'),
                wx.OK | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
            return None

        page_data = self.LBOX_doc_pages.GetClientData(page_idx)

        # remove page from document
        page_oid = page_data['oid']
        if not self.__xml_doc_desc.remove_object(page_oid):
            _log.Log(gmLog.lErr, 'Cannot delete page from document.' % page_fname)
            gm_show_error (
                _('Cannot delete page %s. It does not seem to belong to the document.') % page_idx+1,
                _('deleting page')
            )
            return None

        # remove physical file
        page_fname = page_data['file name']
        if not os.path.exists(page_fname):
            _log.Log(gmLog.lErr, 'Cannot delete page. File [%s] does not exist !' % page_fname)
        else:
            os.remove(page_fname)

        # reload LBOX_doc_pages
        self.__reload_doc_pages()

        return 1
    #----------------------------------------
    def on_select_files (self, event):
        # patient file chooser
        dlg = wx.FileDialog(
            self,
            _('choose a file'),
            '',
            '',
            wildcard = "all (*.*)|*.*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg",
            style = wx.FILE_MUST_EXIST
        )
        dlg.ShowModal()
        dlg.Destroy()
        aDir = os.path.dirname(dlg.GetPath())
        self.doc_id_wheel.SetValue(aDir)
        # aDir is just a dummy here
        self.on_load_pages(aDir)
        return None
    #----------------------------------------
    def wheel_callback (self, data):
        pass
        #print "Selected :%s" % data
    #----------------------------------------
    # patient related helpers
    #----------------------------------------
    def __load_patient_from_file(self):
        """Get data of patient for which to index documents.

        - later on we might want to provide access
          to other methods of getting the patient
        """
        pat_file = os.path.abspath(os.path.expanduser(_cfg.get("index", "patient file")))
        # FIXME: actually handle pat_format, too  :-)
        pat_format = _cfg.get("index", "patient file format")
        _log.Log(gmLog.lWarn, 'patient file format is [%s]' % pat_format)
        _log.Log(gmLog.lWarn, 'note that we only handle xDT files so far')

        # get patient data from xDT file
        try:
            self.__xdt_patient = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
        except:
            _log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
            gm_show_error(
                aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
                aTitle = _('loading patient from xDT file')
            )
            return None

        return 1
    #----------------------------------------
    def fill_pat_fields(self):
        if __name__ == '__main__':
            # reading from xdt-file
            self.TBOX_first_name.SetValue(self.__xdt_patient['first name'])
            self.TBOX_last_name.SetValue(self.__xdt_patient['last name'])
            self.TBOX_dob.SetValue("%s.%s.%s" % (self.__xdt_patient['dob day'], self.__xdt_patient['dob month'], self.__xdt_patient['dob year']))
    #----------------------------------------
    def __keep_patient_file(self, aDir):
        # keep patient file for import
        tmp = os.path.abspath(os.path.expanduser(_cfg.get("index", "patient file")))
        fname = os.path.split(tmp)[1]
        new_name = os.path.join(aDir, fname)
        try:
            shutil.copyfile(tmp, new_name)
        except:
            _log.LogException("Cannot copy patient data file.", sys.exc_info(), fatal=1)
            gm_show_error (
                _('Cannot copy patient file\n[%s]\ninto data directory\n[%s].') % (tmp, aDir),
                _('Error')
            )
            return None
        return 1
    #----------------------------------------
    # document related helpers
    #----------------------------------------
    def __load_doc(self, aDir):
        # try to init XML document description
        try:
            self.__xml_doc_desc = gmXmlDocDesc.xmlDocDesc(aBaseDir = aDir)
        except:
            _log.LogException('cannot access XML document description in metadata file [%s]' % fname, sys.exc_info())
            return None
        return 1
    #----------------------------------------
    def __fill_doc_fields(self):
        self.__clear_doc_fields()
        self.__reload_doc_pages()
    #----------------------------------------
    def __clear_doc_fields(self):
        # clear fields
        # FIXME: make this configurable: either now() or last_date()
        self.TBOX_doc_date.SetValue(time.strftime('%Y-%m-%d', time.localtime()))
        self.TBOX_desc_short.SetValue(_('please fill in'))
        self.TBOX_desc_long.SetValue(_('please fill in'))
        self.SelBOX_doc_type.SetValue(_('choose document type'))
        self.LBOX_doc_pages.Clear()
    #----------------------------------------
    def __reload_doc_pages(self):
        self.LBOX_doc_pages.Clear()
        objLst = self.__xml_doc_desc['objects']
        # FIXME: sort !
        for oid, obj in objLst.items():
            page_num = obj['index']
            path, name = os.path.split(obj['file name'])
            obj['oid'] = oid
            self.LBOX_doc_pages.Append(_('page %s (%s in %s)') % (page_num, name, path), obj)
    #----------------------------------------
    # 
    #----------------------------------------
    def __dump_metadata_to_xml(self, aDir):

        content = []

        tag = _cfg.get("metadata", "document_tag")
        content.append('<%s>\n' % tag)

        tag = _cfg.get("metadata", "name_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.__xdt_patient['last name'], tag))

        tag = _cfg.get("metadata", "firstname_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.__xdt_patient['first name'], tag))

        tag = _cfg.get("metadata", "birth_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.__xdt_patient['dob'], tag))

        tag = _cfg.get("metadata", "date_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.TBOX_doc_date.GetLineText(0), tag))

        tag = _cfg.get("metadata", "type_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.SelBOX_doc_type.GetStringSelection(), tag))

        tag = _cfg.get("metadata", "comment_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.TBOX_desc_short.GetLineText(0), tag))

        tag = _cfg.get("metadata", "aux_comment_tag")
        content.append('<%s>%s</%s>\n' % (tag, self.TBOX_desc_long.GetValue(), tag))

        tag = _cfg.get("metadata", "ref_tag")
        doc_ref = self.doc_id_wheel.GetLineText(0)
        content.append('<%s>%s</%s>\n' % (tag, doc_ref, tag))

        # FIXME: take reordering into account
        tag = _cfg.get("metadata", "obj_tag")
        objLst = self.__xml_doc_desc['objects']
        for object in objLst.values():
            dirname, fname = os.path.split(object['file name'])
            content.append('<%s>%s</%s>\n' % (tag, fname, tag))

        content.append('</%s>\n' % _cfg.get("metadata", "document_tag"))

        # overwrite old XML metadata file and write new one
        xml_fname = os.path.join(aDir, _cfg.get("metadata", "description"))
        os.remove(xml_fname)
        xml_file = open(xml_fname, "w")
        map(xml_file.write, content)
        xml_file.close()
    #----------------------------------------
    def __valid_input(self):
        # check whether values for date of record, record type, short comment and extended comment
        # have been filled in

        lboxlen = self.LBOX_doc_pages.GetCount()
        date = self.TBOX_doc_date.GetLineText(0)
        datechecklist = string.split(date, '-')
        shortDescription = self.TBOX_desc_short.GetLineText(0)
        docType = self.SelBOX_doc_type.GetSelection()

        # count pages to index
        if lboxlen == 0:
            msg = _('number of pages: none ?\n\n forgot to load pages ? ')
        # do some checking on the date
        elif date == _('please fill in'):
            msg = _('document date: missing')
        elif len(date) != 10:
            msg = _('document date: must be 10 characters long')
        elif len(datechecklist) != 3:
            msg = _('document date: invalid format\n\nvalid format: YYYY-MM-DD')
        elif len(datechecklist[0]) != 4:
            msg = _('document date: year must be 4 digits')
        elif int(datechecklist[0]) < 1900:
            msg = _('document date: document from before 1900 ?!?\n\nI want a copy !')
        elif datechecklist[0] > time.strftime("%Y", time.localtime()):
            msg = _('document date: no future !')
        elif len(datechecklist[1]) != 2:
            msg = _('document date: month must be 2 digits')
        elif len(datechecklist[2]) != 2:
            msg = _('document date: day must be 2 digits')
        elif int(datechecklist[1]) not in range(1, 13):
            msg = _('document date: month must be 1 to 12')
        elif int(datechecklist[2]) not in range(1, 32):
            msg = _('document date: day must be 1 to 31')
        elif shortDescription == _('please fill in') or shortDescription == '':
            msg = _('You must type in a short document comment.')
        elif docType == -1 or docType == _('please choose'):
            msg = _('You must select a document type.')
        else:
            return 1

        _log.Log(gmLog.lErr, 'Collected metadata is not fully valid.')
        _log.Log(gmLog.lData, msg)

        dlg = wx.MessageDialog(
            self,
            _('The data you entered about the current document\nis not complete. Please enter the missing information.\n\n%s' % msg),
            _('data input error'),
            wx.OK | wx.ICON_ERROR
        )
        dlg.ShowModal()
        dlg.Destroy()

        return 0
    #----------------------------------------
    # locking related helpers
    #----------------------------------------
    def __unlock_for_import(self, aDir):
        """three-stage locking"""

        indexing_file = os.path.join(aDir, _cfg.get("index", "lock file"))
        can_index_file = os.path.join(aDir, _cfg.get("index", "checkpoint file"))
        can_import_file = os.path.join(aDir, _cfg.get("import", "checkpoint file"))

        # 1) set ready-for-import checkpoint
        try:
            tag_file = open(can_import_file, "w")
            tag_file.close()
        except IOError:
            exc = sys.exc_info()
            _log.LogException('Cannot write import checkpoint file [%s]. Leaving locked for indexing.' % can_import_file, exc, fatal=0)
            return None

        # 2) remove ready-for-indexing checkpoint
        os.remove(can_index_file)

        # 3) remove indexing lock
        os.remove(indexing_file)

        return 1
    #----------------------------------------
    def __lock_for_indexing(self, aDir):
        """three-stage locking

        - there still is the possibility for a race between
          1) and 2) by two clients attempting to start indexing
          at the same time
        """
        can_index_file = os.path.join(aDir, _cfg.get("index", "checkpoint file"))
        indexing_file = os.path.join(aDir, _cfg.get("index", "lock file"))
        cookie = _cfg.get("index", "cookie")

        # 1) anyone indexing already ?
        if os.path.exists(indexing_file):
            _log.Log(gmLog.lInfo, 'Someone seems to be indexing this directory already. Indexing lock [%s] exists.' % indexing_file)
            return None

        # 2) lock for indexing by us and store cookie
        try:
            tag_file = open(indexing_file, 'w')
            tag_file.write(cookie)
            tag_file.close()
        except IOError:
            # this shouldn't happen
            exc = sys.exc_info()
            _log.LogException('Exception: Cannot acquire indexing lock [%s].' % indexing_file, exc, fatal = 0)
            return None

        # 3) check for ready-for-indexing checkpoint
        # this should not happen, really, since we check in _init_phrasewheel() already
        if not os.path.exists(can_index_file):
            # unlock again
            _log.Log(gmLog.lInfo, 'Not ready for indexing yet. Releasing indexing lock [%s] again.' % indexing_file)
            os.remove(indexing_file)
            return None
        return 1
#======================================================
# main
#------------------------------------------------------
# == classes for standalone use ======================
if __name__ == '__main__':
    if _cfg is None:
        msg = _('Cannot index documents without a configuration file.')
        gm_show_error(
            msg,
            _('starting document indexer')
        )
        raise ConstructorError, msg
    
    try:
        wx.InitAllImageHandlers()
        application = wx.PyWidgetTester(size=(800,600))
        application.SetWidget(indexPnl)
        application.MainLoop()
    except StandardError:
        exc = sys.exc_info()
        _log.LogException('Unhandled exception.', exc, fatal=1)
        # FIXME: remove pending indexing locks
        raise

    # FIXME: remove pending indexing locks
# == classes for plugin use ===========================
else:
    from Gnumed.wxpython import gmPlugin, images_Archive_plugin, images_Archive_plugin1
    from Gnumed.pycommon import gmGuiBroker, gmPG
    
    class gmScanIdxMedDocs(gmPlugin.cNotebookPluginOld):
        tab_name = _("Index Documents")
        
        def name (self):
            return gmScanIdxMedDocs.tab_name
        
        def MenuInfo (self):
            return ('tools', _('&Index Documents'))
            
        def GetWidget (self, parent):
            self.panel = indexPnl(parent)
            return self.panel
        
        def ReceiveFocus(self):
            self.panel.fill_pat_fields()
            self.doc_id_wheel.update_choices(self.panel.repository)
            self._set_status_txt(_('steps: 1: select document | 2: describe it | 3: save it'))
            # FIXME: register interest in patient_changed signal, too
            #self.panel.tree.SelectItem(self.panel.tree.root)
            return 1
        # ---------------------------------------------
        def can_receive_focus(self):
            # need patient
            if not self._verify_patient_avail():
                return None
            return 1
        # ---------------------------------------------
        def populate_toolbar (self, tb, widget):
            tool1 = tb.AddTool(
                wxID_TB_BTN_select_files,
                images_Archive_plugin1.getfoldersearchBitmap(),
                shortHelpString=_("select files"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_select_files, widget.on_select_files)
                        
            tool1 = tb.AddControl(wx.StaticBitmap(
                tb,
                -1,
                images_Archive_plugin.getvertical_separator_thinBitmap(),
                wx.DefaultPosition,
                wx.DefaultSize
            ))
                        
            self.doc_id_wheel = cDocWheel(tb)
            self.panel.set_wheel_link(self.doc_id_wheel)
            tool1 = tb.AddControl(
                self.doc_id_wheel
                )
            self.doc_id_wheel.on_resize (None)
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_load_pages,
                images_Archive_plugin.getcontentsBitmap(),
                shortHelpString=_("load pages"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_load_pages, widget.on_load_pages)
                        
            """tool1 = tb.AddControl(wxStaticBitmap(
                tb,
                -1,
                images_Archive_plugin.getvertical_separator_thinBitmap(),
                wx.DefaultPosition,
                wx.DefaultSize
            ))
            """
            tb.AddSeparator()
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_show_page,
                images_Archive_plugin.getreportsBitmap(),
                shortHelpString=_("show page"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_show_page, widget.on_show_page)
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_del_page,
                images_Archive_plugin.getcontentsBitmap(),
                shortHelpString=_("delete page"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_del_page, widget.on_del_page)
                    
            tool1 = tb.AddTool(
                wxID_TB_BTN_save_data,
                images_Archive_plugin.getsaveBitmap(),
                shortHelpString=_("save document"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_save_data, widget.on_save_data)
            
            tb.AddControl(wx.StaticBitmap(
                tb,
                -1,
                images_Archive_plugin.getvertical_separator_thinBitmap(),
                wx.DefaultPosition,
                wx.DefaultSize
            ))
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_aquire_docs,
                images_Archive_plugin1.getfoldersearchBitmap(),
                shortHelpString=_("aquire documents"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_aquire_docs, self.SetScanWidget)
            
            tool1 = tb.AddTool(
                wxID_TB_BTN_show_dirs_in_repository,
                images_Archive_plugin1.getfoldersearchBitmap(),
                shortHelpString=_("show directories in repository"),
                isToggle=False
            )
            wx.EVT_TOOL (tb, wxID_TB_BTN_show_dirs_in_repository, widget.on_show_doc_dirs)#(doc_dirs = self.panel.repository))
        # ---------------------------------------------
        def SetScanWidget (self,parent):
            self.Raise(plugin_name = 'gmScanMedDocs')
#======================================================
# this line is a replacement for gmPhraseWheel just in case it doesn't work 
#self.doc_id_wheel = wxTextCtrl(id = wxID_indexPnlBEFNRBOX, name = 'textCtrl1', parent = self.PNL_main, pos = wxPoint(48, 112), size = wxSize(176, 22), style = 0, value = _('document#'))
#======================================================
# $Log: gmScanIdxMedDocs.py,v $
# Revision 1.1  2005-11-25 21:21:53  shilbert
# - initial non-working version of combined scan and index plugin
#
# Revision 1.19  2005/09/27 20:22:43  ncq
# - a few wx2.6 fixes
#
# Revision 1.18  2005/01/31 09:48:51  ncq
# - cleanup
#
# Revision 1.17  2004/03/19 20:49:21  shilbert
# - fixed import
#
# Revision 1.16  2004/03/08 22:06:54  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.15  2004/02/25 09:46:19  ncq
# - import from pycommon now, not python-common
#
# Revision 1.14  2004/01/17 10:32:45  shilbert
# - changed setScanWidget() to match recent Raise() syntax changes in gmPlugin
#
# Revision 1.13  2004/01/17 00:46:27  shilbert
# - two new features implemented
#   on_show_doc_dirs()
#   setScanWidget()
#
# Revision 1.12  2003/11/29 23:57:51  shilbert
# - GUI cleanup
#
# Revision 1.11  2003/11/19 22:25:00  ncq
# - fixed list match provider now has setItems() so use it
# - remove unneeded return from update_choices()
#
# Revision 1.10  2003/11/19 19:50:28  shilbert
# - fix update choices for doc wheel
#
# Revision 1.9  2003/11/19 13:40:51  ncq
# - fixed doc wheel creation in dotoolbar
#
# Revision 1.8  2003/11/19 13:34:29  ncq
# - moved doc wheel to its own class
#
# Revision 1.7  2003/11/19 00:33:53  shilbert
# - added phrase_wheel to toolbar
#
# Revision 1.6  2003/11/18 14:12:23  ncq
# - cleanup
#
# Revision 1.5  2003/11/09 16:01:16  ncq
# - cleanup
#
# Revision 1.4  2003/11/09 15:42:27  shilbert
# - plugin makes use of GNUmed's toolbar and statusbar
#
# Revision 1.3  2003/11/08 18:15:05  ncq
# - name changed
# - cleanup
#
# Revision 1.2  2003/11/08 18:11:13  ncq
# - cleanup
#
# Revision 1.1  2003/11/08 12:07:43  shilbert
# - name change index_med_docs -> gmIndexMedDocs
# - fixed issues with updated phrasewheel
# - made it work as plugin again
#
# Revision 1.1  2003/08/28 17:35:52  shilbert
# - changes to make it work as GNUmed plugin
#
# Revision 1.6  2003/04/25 12:56:19  ncq
# - clarified message
#
# Revision 1.5  2003/04/22 10:14:31  ncq
# - disabled some fields from being tabbed in
#
# Revision 1.4  2003/04/20 16:10:12  ncq
# - warn on missing repository or config file
#
# Revision 1.3  2003/04/20 15:29:49  ncq
# - adapted to getting away from old doc*.py modules
#
# Revision 1.2  2003/04/19 22:51:57  ncq
# - switch from docPatient to xdtPatient go get away from docPatient's import gmPG
#
# Revision 1.1  2003/04/06 09:43:14  ncq
# - moved here from test-area/blobs_hilbert/
#
# Revision 1.27  2003/03/01 14:40:10  ncq
# - added extensive TODO
# - added explicit license statement !!
#
# Revision 1.26  2003/01/14 22:11:27  ncq
# - reloads phrase wheel after save
#
# Revision 1.25  2002/12/29 00:54:02  ncq
# - started support for loading of external files
# - fixed gmI18N import position
#
# Revision 1.24  2002/12/22 11:51:24  ncq
# - patient format -> patient file format
#
# Revision 1.23  2002/12/13 10:39:30  ncq
# - fixed shutils -> shutil
#
# Revision 1.22  2002/12/09 23:06:11  ncq
# - test for loaded pages before saving document
#
# Revision 1.21  2002/12/02 03:28:16  ncq
# - converted to sizers
# - first provisions for plugin()ification
#
# Revision 1.20  2002/11/30 19:45:46  ncq
# - when keeping the patient file: do name.split()[0] and use full old path when copying
#
# Revision 1.19  2002/11/23 16:45:21  ncq
# - make work with pyPgSQL
# - fully working now but needs a bit of polish
#
# Revision 1.18  2002/10/01 09:47:36  ncq
# - sync, should sort of work
#
# Revision 1.17  2002/09/30 08:18:07  ncq
# - config file cleanup
#
# Revision 1.16  2002/09/28 15:59:33  ncq
# - keep patient file for import
#
# Revision 1.15  2002/09/22 18:37:58  ncq
# - minor cleanups
#
# Revision 1.14  2002/09/17 01:44:06  ncq
# - correctly import docDocument
#
# Revision 1.13  2002/09/17 01:14:16  ncq
# - delete_page seems to work now
#
