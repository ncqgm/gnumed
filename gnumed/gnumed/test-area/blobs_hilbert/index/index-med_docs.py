#!/usr/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/index/Attic/index-med_docs.py,v $
__version__ = "$Revision: 1.21 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
			  Karsten Hilbert <Karsten.Hilbert@gmx.net>"

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

#import Image
import os, time, shutil, os.path

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
#<DEBUG>
gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
#</DEBUG>

from docPatient import *
from gmPhraseWheel import *
import docDocument
import gmCfg, gmI18N
import docXML

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

[	wxID_INDEXFRAME,
	wxID_TBOX_desc_long,
	wxID_INDEXFRAMEBEFNRBOX,
	wxID_TBOX_doc_date,
	wxID_TBOX_dob,
	wxID_BTN_del_page,
	wxID_BTN_load_fax,
	wxID_BTN_save_data,
	wxID_BTN_show_page,
	wxID_BTN_load_pages,
	wxID_SelBOX_doc_type,
	wxID_TBOX_first_name,
	wxID_TBOX_last_name,
	wxID_LBOX_doc_pages,
	wxID_TBOX_desc_short,
	wxID_PNL_main
] = map(lambda _init_ctrls: wxNewId(), range(16))

#====================================
class indexFrame(wxPanel):

	def __init__(self, parent):

		wxPanel.__init__(self, parent, -1, wxDefaultPosition, wxDefaultSize)

		# get valid document types from ini-file
		self.valid_doc_types = _cfg.get("metadata", "doctypes")
		# repository base
		self.repository = os.path.abspath(os.path.expanduser(_cfg.get("index", "repository")))

		# set up GUI
		self._init_ctrls(parent)

		# items for phraseWheel
		if not self._init_phrase_wheel():
			return -1

		self.__set_properties()
		self.__do_layout()

		# we are indexing data from one particular patient
		# this is a design decision
		if not self.__load_patient():
			return -1
		self.__fill_pat_fields()
	#--------------------------------------
	def _init_ctrls(self, prnt):

		# -- main panel -----------------------
		self.PNL_main = wxPanel(
			id = wxID_PNL_main,
			name = 'main panel',
			parent = self,
			style = wxTAB_TRAVERSAL
		)

		#-- left column -----------------------
		self.staticText1 = wxStaticText(
			id = -1,
			name = 'staticText1',
			parent = self.PNL_main,
			label = _("1) select")
		)
		#--------------------------------------
		self.staticText7 = wxStaticText(
			id =  -1,
			name = 'staticText7',
			parent = self.PNL_main,
			label = _("document identifier")
		)
		# -- load pages button ----------------
		self.BTN_load_pages = wxButton(
			id = wxID_BTN_load_pages,
			name = 'BTN_load_pages',
			parent = self.PNL_main,
			label = _("load pages")
		)
		#--------------------------------------
		self.staticText4 = wxStaticText(
			id = -1,
			name = 'staticText4',
			parent = self.PNL_main,
			label = _("or")
		)
		# -- load fax button ------------------
		self.BTN_load_fax = wxButton(
			id = wxID_BTN_load_fax,
			name = 'BTN_load_fax',
			parent = self.PNL_main,
			label = _("load fax document")
		)
		#--------------------------------------
		self.staticText8 = wxStaticText(
			id = -1,
			name = 'staticText8',
			parent = self.PNL_main,
			label = _("document pages")
		)
		# -- list box with pages --------------
		self.LBOX_doc_pages = wxListBox(
			id = wxID_LBOX_doc_pages,
			name = 'LBOX_doc_pages',
			parent = self.PNL_main,
			style = wxLB_SORT,
			choices=[]
		)
		# -- show page button -----------------
		self.BTN_show_page = wxButton(
			id = wxID_BTN_show_page,
			name = 'BTN_show_page',
			parent = self.PNL_main,
			label = _("show page")
		)
		# -- delete page button ---------------
		self.BTN_del_page = wxButton(
			id = wxID_BTN_del_page,
			name = 'BTN_del_page',
			parent = self.PNL_main,
			label = _("delete page")
		)

		#-- middle column ---------------------
		self.staticText2 = wxStaticText(
			id = -1,
			name = 'staticText2',
			parent = self.PNL_main,
			label = _("2) describe")
		)
		#--------------------------------------
		self.staticText9 = wxStaticText(
			id = -1,
			name = 'staticText9',
			parent = self.PNL_main,
			label = _("first name")
		)
		# -- first name text box --------------
		self.TBOX_first_name = wxTextCtrl(
			id = wxID_TBOX_first_name,
			name = 'TBOX_first_name',
			parent = self.PNL_main,
			value = _("loading ..."),
			style=wxTE_READONLY
		)
		#--------------------------------------
		self.staticText10 = wxStaticText(
			id = -1,
			name = 'staticText10',
			parent = self.PNL_main,
			label = _("last name")
		)
		# -- last name text box ---------------
		self.TBOX_last_name = wxTextCtrl(
			id = wxID_TBOX_last_name,
			name = 'TBOX_last_name',
			parent = self.PNL_main,
			value = _("loading ..."),
			style=wxTE_READONLY
		)
		#--------------------------------------
		self.staticText6 = wxStaticText(
			id = -1,
			name = 'staticText6',
			parent = self.PNL_main,
			label = _("date of birth")
		)
		# -- dob text box ---------------------
		self.TBOX_dob = wxTextCtrl(
			id = wxID_TBOX_dob,
			name = 'TBOX_dob',
			parent = self.PNL_main,
			value = _("loading ..."), 
			style=wxTE_READONLY
		)
		#--------------------------------------
		self.staticText5 = wxStaticText(
			id =  -1,
			name = 'staticText5',
			parent = self.PNL_main,
			label = _("date (YYYY-MM-DD)")
		)
		# -- document creation text box -------
		self.TBOX_doc_date = wxTextCtrl(
			id = wxID_TBOX_doc_date,
			name = 'TBOX_doc_date',
			parent = self.PNL_main,
			# FIXME: default date should be changeable
			value = time.strftime('%Y-%m-%d',time.localtime())
		)
		#--------------------------------------
		self.staticText11 = wxStaticText(
			id = -1,
			name = 'staticText11',
			parent = self.PNL_main,
			label = _("short comment")
		)
		# -- short document comment text box --
		self.TBOX_desc_short = wxTextCtrl(
			id = wxID_TBOX_desc_short,
			name = 'TBOX_desc_short',
			parent = self.PNL_main,
			value = _("please fill in")
		)
		#--------------------------------------
		self.staticText12 = wxStaticText(
			id = -1,
			name = 'staticText12',
			parent = self.PNL_main,
			label = _("document type")
		)
		# -- document type selection box ------
		self.SelBOX_doc_type = wxComboBox(
			id = wxID_SelBOX_doc_type,
			name = 'SelBOX_doc_type',
			parent = self.PNL_main,
			value = _('choose document type'),
			choices = self.valid_doc_types,
			style=wxCB_DROPDOWN
		)
		self.SelBOX_doc_type.SetLabel('')

		#-- right column ----------------------
		self.staticText3 = wxStaticText(
			id = -1,
			name = 'staticText3',
			parent = self.PNL_main,
			label = _("3) save")
		)
		# -- save data button -----------------
		self.BTN_save_data = wxButton(
			id = wxID_BTN_save_data,
			name = 'BTN_save_data',
			parent = self.PNL_main,
			label = _("save data")
		)

		#-- bottom area -----------------------
		self.staticText13 = wxStaticText(
			id = -1,
			name = 'staticText13',
			parent = self.PNL_main,
			label = _("additional comment")
		)
		# -- long document comment text box ---
		self.TBOX_desc_long = wxTextCtrl(
			id = wxID_TBOX_desc_long,
			name = 'TBOX_desc_long',
			parent = self.PNL_main,
			value = "",
			style=wxTE_MULTILINE
		)
	#--------------------------------
	def _init_phrase_wheel(self):
		"""Set up phrase wheel.

		- directory names in self.repository correspond to identification
		  strings on paper documents
		- when starting to type an ident the phrase wheel must
		  show matching directories
		"""

		# get document directories
		doc_dirs = os.listdir(self.repository)

		# generate list of choices
		phrase_wheel_choices = []
		for i in range(len(doc_dirs)):
			full_dir = os.path.join(self.repository, doc_dirs[i])

			# don't add stray files
			if not os.path.isdir(full_dir):
				_log.Log(gmLog.lData, "ignoring stray file [%s]" % doc_dirs[i])
				continue

			if not self.__could_be_locked(full_dir):
				_log.Log(gmLog.lInfo, "Document directory [%s] not yet checkpointed for indexing. Skipping." % full_dir)
				continue

			# same weight for all of them
			phrase_wheel_choices.append({'ID': i, 'label': doc_dirs[i], 'weight': 1})

		#<DEBUG>
		_log.Log(gmLog.lData, "document dirs: %s" % str(phrase_wheel_choices))
		#</DEBUG>

		if len(phrase_wheel_choices) == 0:
			_log.Log(gmLog.lWarn, "No document directories in repository. Nothing to do !.")
			dlg = wxMessageDialog(
				self,
				_("There are no documents in the repository.\n(%s)\n\nSeems like there's nothing to do today." % self.repository),
				_('Information'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# FIXME: we need to set this to non-learning mode
		mp = cMatchProvider_FixedList(phrase_wheel_choices)
		self.doc_id_wheel = cPhraseWheel(
			self.PNL_main,
			self.wheel_callback,
			aMatchProvider = mp,
			aDelay = 400
		)
		self.doc_id_wheel.on_resize (None)

		return 1
	#--------------------------------
	def __set_properties(self):
		self.SetTitle(_("GnuMed/Archiv: Associating documents with patients."))

		self.PNL_main.SetBackgroundColour(wxColour(225, 225, 225))
		self.TBOX_first_name.SetBackgroundColour(wxColour(255, 255, 255))
		self.TBOX_last_name.SetBackgroundColour(wxColour(255, 255, 255))
		self.TBOX_dob.SetBackgroundColour(wxColour(255, 255, 255))

		self.staticText1.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.staticText4.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.BTN_load_pages.SetToolTipString(_('load the pages of this document'))
		self.BTN_load_fax.SetToolTipString(_('currently non-functional: load a fax document'))
		self.LBOX_doc_pages.SetToolTipString(_('these pages make up the current document'))
		self.BTN_show_page.SetToolTipString(_('display selected part of the document'))
		self.BTN_del_page.SetToolTipString(_('delete selected part of the document'))
		self.TBOX_first_name.SetToolTipString(_('not editable, loaded from file'))
		self.TBOX_last_name.SetToolTipString(_('not editable, loaded from file'))
		self.TBOX_dob.SetToolTipString(_('not editable, loaded from file'))
		self.TBOX_doc_date.SetToolTipString(_('date of creation of the document content\nformat: YYYY-MM-DD'))
		self.TBOX_desc_short.SetToolTipString(_('a short comment on the document content'))
		self.SelBOX_doc_type.SetToolTipString(_('Document types are determined by the database.\nAsk your database administrator to add more types if needed.'))
		self.BTN_save_data.SetToolTipString(_('save entered metadata with document'))
		self.TBOX_desc_long.SetToolTipString(_('a summary or longer comment for this document'))
		self.doc_id_wheel.SetToolTipString(_('the document identifier is usually written or stamped onto the physical pages of the document'))

		EVT_BUTTON(self.BTN_load_pages, wxID_BTN_load_pages, self.on_load_pages)
		EVT_BUTTON(self.BTN_show_page, wxID_BTN_show_page, self.on_show_page)
		EVT_BUTTON(self.BTN_del_page, wxID_BTN_del_page, self.on_del_page)
		EVT_BUTTON(self.BTN_save_data, wxID_BTN_save_data, self.on_save_data)
		EVT_BUTTON(self.BTN_save_data, wxID_BTN_save_data, self.on_save_data)

		self.LBOX_doc_pages.SetSelection(0)
		self.SelBOX_doc_type.SetSelection(0)
	#--------------------------------
	def __do_layout(self):

		szr_main_outer = wxBoxSizer(wxHORIZONTAL)

		# left vertical column (1/3) in upper half of the screen
		szr_left = wxBoxSizer(wxVERTICAL)
		szr_left.Add(self.staticText1, 0, 0, 0)
		szr_left.Add(self.staticText7, 0, wxLEFT|wxTOP, 5)
		szr_left.Add(self.doc_id_wheel, 0, wxEXPAND|wxALL, 5)
		szr_left.Add(self.BTN_load_pages, 1, wxEXPAND|wxALL, 5)
		szr_left.Add(self.staticText4, 0, wxLEFT, 5)
		szr_left.Add(self.BTN_load_fax, 1, wxEXPAND|wxALL, 5)
		szr_left.Add(self.staticText8, 0, wxLEFT, 5)
		szr_left.Add(self.LBOX_doc_pages, 1, wxEXPAND|wxALL, 5)
		szr_left_btns = wxBoxSizer(wxHORIZONTAL)
		szr_left_btns.Add(self.BTN_show_page, 1, wxRIGHT|wxTOP, 5)
		szr_left_btns.Add(self.BTN_del_page, 1, wxTOP, 5)
		szr_left.Add(szr_left_btns, 1, wxEXPAND|wxALIGN_BOTTOM, 0)

		# middle vertical column (2/3) in upper half of the screen
		szr_middle = wxBoxSizer(wxVERTICAL)
		szr_middle.Add(self.staticText2, 0, 0, 0)
		szr_middle.Add(self.staticText9, 0, wxLEFT|wxTOP, 5)
		szr_middle.Add(self.TBOX_first_name, 0, wxEXPAND|wxALL, 5)
		szr_middle.Add(self.staticText10, 0, wxLEFT, 5)
		szr_middle.Add(self.TBOX_last_name, 0, wxEXPAND|wxALL, 5)
		szr_middle.Add(self.staticText6, 0, wxLEFT, 5)
		szr_middle.Add(self.TBOX_dob, 0, wxEXPAND|wxALL, 5)
		szr_middle.Add(self.staticText5, 0, wxLEFT, 5)
		szr_middle.Add(self.TBOX_doc_date, 0, wxEXPAND|wxALL, 5)
		szr_middle.Add(self.staticText11, 0, wxLEFT, 5)
		szr_middle.Add(self.TBOX_desc_short, 0, wxEXPAND|wxALL, 5)
		szr_middle.Add(self.staticText12, 0, wxLEFT, 5)
		szr_middle.Add(self.SelBOX_doc_type, 0, wxEXPAND|wxALL, 5)
		
		# rightmost vertical column (3/3) in upper half of the screen
		szr_right = wxBoxSizer(wxVERTICAL)
		szr_right.Add(self.staticText3, 0, wxALIGN_CENTER_HORIZONTAL|wxBOTTOM, 20)
		szr_right.Add(self.BTN_save_data, 1, wxEXPAND, 0)

		# group columns
		szr_top_grid = wxGridSizer(1, 3, 0, 0)
		szr_top_grid.Add(szr_left, 1, wxEXPAND|wxLEFT, 40)
		szr_top_grid.Add(szr_middle, 1, wxEXPAND|wxALIGN_CENTER_HORIZONTAL|wxLEFT, 40)
		szr_top_grid.Add(szr_right, 1, wxALIGN_RIGHT|wxEXPAND|wxLEFT|wxRIGHT, 20)

		# single textbox area in lower half of the screen
		szr_bottom = wxBoxSizer(wxVERTICAL)
		szr_bottom.Add(self.staticText13, 0, wxBOTTOM, 5)
		szr_bottom.Add(self.TBOX_desc_long, 1, wxEXPAND, 0)

		# group top and bottom parts
		szr_main_inner = wxBoxSizer(wxVERTICAL)
		szr_main_inner.Add(szr_top_grid, 2, wxEXPAND, 0)
		szr_main_inner.Add(szr_bottom, 1, wxEXPAND|wxALL, 20)

		self.PNL_main.SetAutoLayout(1)
		self.PNL_main.SetSizer(szr_main_inner)
		szr_main_inner.Fit(self.PNL_main)
		szr_main_outer.Add(self.PNL_main, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(szr_main_outer)
		szr_main_outer.Fit(self)
		self.Layout()
	#----------------------------------------
	# event handlers
	#----------------------------------------
	def on_load_pages(self, event):
		_log.Log(gmLog.lData, "Trying to load document.")

		curr_doc_id = self.doc_id_wheel.GetLineText(0)

		# has the user supplied anything ?
		if curr_doc_id == '':
			_log.Log(gmLog.lErr, 'No document ID typed in yet !')
			dlg = wxMessageDialog(
				self,
				_('You must type in a document ID !\n\nUsually you will find the document ID written on\nthe physical sheet of paper. There should be only one\nper document even if there are multiple pages.'),
				_('missing document ID'),
				wxOK | wxICON_EXCLAMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		full_dir = os.path.join(self.repository, curr_doc_id)

		# lock this directory now
		if not self.__lock_for_indexing(full_dir):
			_log.Log(gmLog.lErr, "Cannot lock directory [%s] for indexing." % full_dir)
			dlg = wxMessageDialog(
				self,
				_('Cannot lock document directory for indexing.\n(%s)\n\nPlease consult the error log for details.' % full_dir),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# actually try loading pages
		if not self.__load_doc(full_dir):
			_log.Log(gmLog.lErr, "Cannot load document object file list.")
			dlg = wxMessageDialog(
				self,
				_('Cannot load document object file list from xDT file.\n\nPlease consult the error log for details.'),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
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
			self.doc_id_wheel.Clear()
			# FIXME: this needs to be reloaded !
			#self.initgmPhraseWheel()
	#----------------------------------------
	def on_show_page(self, event):
		# did user select a page ?
		page_idx = self.LBOX_doc_pages.GetSelection()

		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can view it.'),
				_('displaying page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# now, which file was that again ?
		page_data = self.LBOX_doc_pages.GetClientData(page_idx)
		page_fname = page_data['file name']

		(result, msg) = docDocument.call_viewer_on_file(page_fname)
		if not result:
			dlg = wxMessageDialog(
				self,
				_('Cannot display page %s.\n%s') % (page_idx+1, msg),
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
	#----------------------------------------
	def on_del_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()

		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can delete it.'),
				_('deleting page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		page_data = self.LBOX_doc_pages.GetClientData(page_idx)

		# remove page from document
		page_oid = page_data['oid']
		if not self.myDoc.removeObject(page_oid):
			_log.Log(gmLog.lErr, 'Cannot delete page from document.' % page_fname)
			dlg = wxMessageDialog(
				self,
				_('Cannot delete page %s. It does not seem to belong to the document.') % page_idx+1,
				_('deleting page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# remove physical file
		page_fname = page_data['file name']
		if not os.path.exists(page_fname):
			_log.Log(gmLog.lErr, 'Cannot delete page. File [%s] does not exist !' % page_fname)
		else:
			os.remove(page_fname)

		_log.Log(gmLog.lInfo, "Deleted file [%s] from document." % page_fname)

		# reload LBOX_doc_pages
		self.__reload_doc_pages()

		return 1
	#----------------------------------------
	def wheel_callback (self, data):
		pass
		#print "Selected :%s" % data
	#----------------------------------------
	# internal methods
	#----------------------------------------
	def __load_patient(self):
		# later on we might want to provide access
		# to other methods of getting the patient

		# get patient data from BDT/XDT file
		pat_file = os.path.abspath(os.path.expanduser(_cfg.get("index", "patient file")))
		pat_format = _cfg.get("index", "patient format")
		self.myPatient = cPatient()
		if not self.myPatient.loadFromFile(pat_format, pat_file):
			_log.Log(gmLog.lPanic, "Cannot read patient from %s file [%s]" % (pat_format, pat_file))
			dlg = wxMessageDialog(
				self,
				_('Cannot load patient from %s file\n[%s]\nPlease consult the error log for details.') % (pat_format, pat_file),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return 1
	#----------------------------------------
	def __fill_pat_fields(self):
		self.TBOX_first_name.SetValue(self.myPatient.firstnames)
		self.TBOX_last_name.SetValue(self.myPatient.lastnames)
		self.TBOX_dob.SetValue(self.myPatient.dob)
	#----------------------------------------
	def __clear_doc_fields(self):
		# clear fields
		self.TBOX_doc_date.SetValue(time.strftime('%Y-%m-%d', time.localtime()))
		self.TBOX_desc_short.SetValue(_('please fill in'))
		self.TBOX_desc_long.SetValue(_('please fill in'))
		self.SelBOX_doc_type.SetValue(_('choose document type'))
		self.LBOX_doc_pages.Clear()
	#----------------------------------------
	def __load_doc(self, aDir):
		# well, so load the document from that directory
		_log.Log(gmLog.lData, 'working in [%s]' % aDir)

		# check for metadata file
		fname = os.path.join(aDir, _cfg.get("metadata", "description"))
		if not os.path.exists (fname):
			_log.Log(gmLog.lErr, 'Cannot access metadata file [%s].' % fname)
			dlg = wxMessageDialog(self, 
				_('Cannot access metadata file\n[%s].\nPlease see error log for details.') % fname,
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# actually get pages
		self.myDoc = docDocument.cDocument()
		if not self.myDoc.loadImgListFromXML(fname, aDir, _cfg, "metadata"):
			_log.Log(gmLog.lErr, 'Cannot load image list from metadata file [%s].' % fname)
			dlg = wxMessageDialog(self, 
				_('Cannot load image list from metadata file\n[%s].\n\nPlease see error log for details.') % fname,
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return 1
	#----------------------------------------
	def __fill_doc_fields(self):
		self.__clear_doc_fields()
		self.__reload_doc_pages()
	#----------------------------------------
	def __reload_doc_pages(self):
		self.LBOX_doc_pages.Clear()
		objLst = self.myDoc.getMetaData()['objects']
		# FIXME: sort !
		for oid, obj in objLst.items():
			page_num = obj['index']
			path, name = os.path.split(obj['file name'])
			obj['oid'] = oid
			self.LBOX_doc_pages.Append(_('page %s (%s in %s)') % (page_num, name, path), obj)
	#----------------------------------------
	def __dump_metadata_to_xml(self, aDir):

		content = []

		tag = _cfg.get("metadata", "document_tag")
		content.append('<%s>\n' % tag)

		tag = _cfg.get("metadata", "name_tag")
		content.append('<%s>%s</%s>\n' % (tag, self.myPatient.lastnames, tag))

		tag = _cfg.get("metadata", "firstname_tag")
		content.append('<%s>%s</%s>\n' % (tag, self.myPatient.firstnames, tag))

		tag = _cfg.get("metadata", "birth_tag")
		content.append('<%s>%s</%s>\n' % (tag, self.myPatient.dob, tag))

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
		objLst = self.myDoc.getMetaData()['objects']
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
	def __keep_patient_file(self, aDir):
		# keep patient file for import
		tmp = os.path.abspath(os.path.expanduser(_cfg.get("index", "patient file")))
		fname = os.path.split(tmp)[1]
		new_name = os.path.join(aDir, fname)
		try:
			shutils.copyfile(tmp, new_name)
		except:
			exc = sys.exc_info()
			_log.LogException("Cannot copy patient data file.", exc, fatal=1)
			dlg = wxMessageDialog(self, 
				_('Cannot copy patient file\n[%s]\nto data directory\n[%s]\n\nPlease see error log for details.') % (tmp, aDir),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
	#----------------------------------------
	def __valid_input(self):
		# check whether values for date of record, record type, short comment and extended comment
		# have been filled in
		date = self.TBOX_doc_date.GetLineText(0)
		datechecklist = string.split(date, '-')
		shortDescription = self.TBOX_desc_short.GetLineText(0)
		docType = self.SelBOX_doc_type.GetSelection()
		# do some checking on the date
		if date == _('please fill in'):
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
		elif docType == -1 or docType == 'please choose':
			msg = _('You must select a document type.')
		else:
			return 1

		_log.Log(gmLog.lErr, 'Collected metadata is not fully valid.')
		_log.Log(gmLog.lData, msg)

		dlg = wxMessageDialog(
			self,
			_('The data you entered about the current document\nis not complete. Please enter the missing information.\n\n%s' % msg),
			_('data input error'),
			wxOK | wxICON_ERROR
		)
		dlg.ShowModal()
		dlg.Destroy()

		return 0
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
	def __could_be_locked(self, aDir):
		"""check whether we _could_ acquire the lock for indexing

		i.e., whether we should worry about this directory at all
		"""
		indexing_file = os.path.join(aDir, _cfg.get("index", "lock file"))
		can_index_file = os.path.join(aDir, _cfg.get("index", "checkpoint file"))
		cookie = _cfg.get("index", "cookie")

		# 1) anyone indexing already ?
		if os.path.exists(indexing_file):
			_log.Log(gmLog.lInfo, 'Someone seems to be indexing this directory already. Indexing lock [%s] exists.' % indexing_file)
			# did _we_ lock this dir earlier and then died unexpectedly ?
			fhandle = open(indexing_file, 'r')
			tmp = fhandle.readline()
			fhandle.close()
			tmp = string.replace(tmp,'\015','')
			tmp = string.replace(tmp,'\012','')
			# yep, it's our cookie
			if (tmp == cookie) and (os.path.exists(can_index_file)):
				_log.Log(gmLog.lInfo, 'Seems like _we_ locked this directory earlier and subsequently died without completing our task.')
				_log.Log(gmLog.lInfo, 'At least the cookie we found is the one we use, too (%s).' % cookie)
				_log.Log(gmLog.lInfo, 'Unlocking this directory.')
				os.remove(indexing_file)
			# nope, someone else
			else:
				return None

		# 2) check for ready-for-indexing checkpoint
		if not os.path.exists(can_index_file):
			_log.Log(gmLog.lInfo, 'Not ready for indexing yet. Checkpoint [%s] does not exist.' % can_index_file)
			return None

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
		# this should not happen, really, since we check on _init_phrasewheel() already
		if not os.path.exists(can_index_file):
			# unlock again
			_log.Log(gmLog.lInfo, 'Not ready for indexing yet. Releasing indexing lock [%s] again.' % indexing_file)
			os.remove(indexing_file)
			return None

		return 1
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	try:
		wxInitAllImageHandlers()
		application = wxPyWidgetTester(size=(800,600))
		application.SetWidget(indexFrame)
		application.MainLoop()
	except:
		exc = sys.exc_info()
		_log.LogException('Unhandled exception.', exc, fatal=1)
		# FIXME: remove pending indexing locks
		raise

	# FIXME: remove pending indexing locks
else:
	import gmPlugin,gmGuiBroker

	class gmIndexMedDocs(gmPlugin.wxNotebookPlugin):
		def name (self):
			return "Index"

		def GetWidget (self, parent):
			return indexFrame (parent)

		def MenuInfo (self):
			return ('tools', '&Index Documents')

#======================================================
# this line is a replacement for gmPhraseWhell just in case it doesn't work 
#self.doc_id_wheel = wxTextCtrl(id = wxID_INDEXFRAMEBEFNRBOX, name = 'textCtrl1', parent = self.PNL_main, pos = wxPoint(48, 112), size = wxSize(176, 22), style = 0, value = _('document#'))
#======================================================
# $Log: index-med_docs.py,v $
# Revision 1.21  2002-12-02 03:28:16  ncq
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