"""
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmLabJournal.py,v $
__version__ = ""
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re# string #random

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmPG, gmCfg, gmExceptions, gmWhoAmI, gmMatchProvider
from Gnumed.business import gmPatient, gmClinicalRecord
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel
from Gnumed.pycommon.gmPyCompat import *

# 3rd party
from wxPython.wx import *
#from wxPython.grid import * 

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

[   wxID_PNL_main,
	wxID_NB_LabJournal,
	wxID_LBOX_pending_results,
	wxID_PHRWH_labs,
	wxID_TXTCTRL_ids,
	wxID_BTN_submit_Lab_ID
] = map(lambda _init_ctrls: wxNewId(), range(6))

wxEVT_ITEM_SELECTED = wxNewEventType()
#============================================================
def EVT_ITEM_SELECTED(win, func):
    win.Connect(-1, -1, wxEVT_ITEM_SELECTED, func)
#============================================================
class ItemSelectedEvent(wxPyCommandEvent):
    def __init__(self):
        wxPyEvent.__init__(self)
        self.SetEventType(wxEVT_ITEM_SELECTED)
#================================================================

class cLabWheel(gmPhraseWheel.cPhraseWheel):
	def __init__(self, parent):
		query = """
			select
				pk,
				internal_name
			from
				test_org
			"""
		self.mp = gmMatchProvider.cMatchProvider_SQL2('historica', query)
		self.mp.setThresholds(aWord=2, aSubstring=4)

		gmPhraseWheel.cPhraseWheel.__init__(
			self,
			parent = parent,
			id = -1,
			aMatchProvider = self.mp,
			size = wxDefaultSize,
			pos = wxDefaultPosition
			#self.wheel_callback
		)
		self.SetToolTipString(_('choose which lab will process the probe with the specified ID'))
#====================================
class cLabJournalNB(wxNotebook):
	"""This wxNotebook derivative displays 'records still due' and lab-import related errors.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised notebook.
		"""
		# connect to config database
		pool = gmPG.ConnectionPool()
		self.__dbcfg = gmCfg.cCfgSQL(
			aConn = pool.GetConnection('default'),
			aDBAPI = gmPG.dbapi
		)

		wxNotebook.__init__(
			self,
			parent,
			id,
			wxDefaultPosition,
			wxDefaultSize,
			0
		)
		# tab with pending requests
		self.PNL_due_tab = wxPanel( self, -1 )
		szr_due = self.__init_SZR_due()

		self.PNL_due_tab.SetAutoLayout( True )
		self.PNL_due_tab.SetSizer( szr_due )
		szr_due.Fit( self.PNL_due_tab )
		szr_due.SetSizeHints( self.PNL_due_tab )

		self.AddPage( self.PNL_due_tab, _("pending lab results"))

		# tab with errors
		self.PNL_error_tab = wxPanel( self, -1)
		self.AddPage( self.PNL_error_tab, _("lab errors"))

		self.curr_pat = gmPatient.gmCurrentPatient()
	#------------------------------------------------------------------------
	def __init_SZR_due (self, call_fit = True, set_sizer = True ):

		vbszr_main = wxBoxSizer( wxVERTICAL )
		lab_wheel = cLabWheel(self.PNL_due_tab)
		lab_wheel.on_resize (None)
		#lab_wheel = wxTextCtrl( 
			#self.PNL_due_tab,
			#wxID_PHRWH_labs,
			#"", 
			#wxDefaultPosition,
			#wxSize(80,-1),
			#0
			#)
		EVT_ITEM_SELECTED(self.PNL_due_tab,self.__on_lab_selected)
		
		vbszr_main.AddWindow(lab_wheel, 0, wxALIGN_CENTER | wxALL, 5)

		item2 = wxTextCtrl(
			self.PNL_due_tab,
			wxID_TXTCTRL_ids,
			"",
			wxDefaultPosition,
			wxSize(80,-1),
			0
			)

		vbszr_main.AddWindow( item2, 0, wxALIGN_CENTER|wxALL, 5 )

		# -- "submit lab id" button -----------
		self.BTN_submit_Lab_ID = wxButton(
			name = 'BTN_submit_Lab_ID',
			parent = self.PNL_due_tab,
			id = wxID_BTN_submit_Lab_ID,
			label = _("save request ID")
		)
		self.BTN_submit_Lab_ID.SetToolTipString(_('associate chosen lab and ID with current patient'))
		EVT_BUTTON(self.BTN_submit_Lab_ID, wxID_BTN_submit_Lab_ID, self.on_submit_ID)

		vbszr_main.AddWindow( self.BTN_submit_Lab_ID, 0, wxALIGN_CENTER|wxALL, 5 )

		# maybe have a look at MultiColumnList
		lbox_pending = wxListBox( 
			self.PNL_due_tab,
			wxID_LBOX_pending_results,
			wxDefaultPosition,
			wxSize(80,100), 
			["ListItem"] ,
			wxLB_SINGLE 
			)

		vbszr_main.AddWindow( lbox_pending, 0, wxALIGN_CENTER|wxALL, 5 )
		return vbszr_main

	#------------------------------------------------------------------------
	def OnLeftDClick(self, evt):
		pass
		
	
	#------------------------------------------------------------------------
	def update(self):
		if self.curr_pat['ID'] is None:
			_log.Log(gmLog.lErr, 'need patient for update, no patient related notebook tabs will be visible')
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot load lab journal.\nYou first need to select a patient.'),
				aTitle = _('loading lab journal')
			)
			return None

		if self.__populate_notebook() is None:
			return None
		return 1
	#------------------------------------------------------------------------
	def __populate_notebook(self):
		# Unfug
		# populate phrase_wheel on receive_focus
		# get_last_id() on wheel.lose_focus
		self.last_id = {}
		labs = self.__get_all_labs()
		for lab in labs:
			if not self.__get_last_used_ID(lab[1]) == []:
				self.last_id[lab[1]] = self.__get_last_used_ID(lab[1])[0][0]
				print self.last_id
		# FIXME: check if patient changed at all
		# emr = self.curr_pat.get_clinical_record()
		# FIXME: there might be too many results to handle in memory
		#lab = emr.get_lab_results()
		
		#if lab is None or len(lab)==0:
		#	name = self.curr_pat['demographic record'].get_names()
		#	gmGuiHelpers.gm_show_error(
		#		aMessage = _('Cannot find any lab data for patient\n[%s %s].') % (name['first'], name['last']),
		#		aTitle = _('loading lab record list')
		#		)
		#	return None
			
		#else:
	#		return 1
			
	#------------------------------------------------------------------------
	def __get_all_labs(self):
		query = """select pk, internal_name from test_org"""
		labs = gmPG.run_ro_query('historica', query)
		return labs
	#------------------------------------------------------------------------
	def __get_last_used_ID(self, lab_name):
		query = """
			select request_id 
			from lab_request lr0 
			where lr0.clin_when = (
				select max(lr1.clin_when)
				from lab_request lr1 
				where lr1.fk_test_org = ( 
					select pk 
					from test_org 
					where internal_name=%s 
				)
			)"""
		last_id = gmPG.run_ro_query('historica', query, None, lab_name)
		return last_id
	#-----------------------------------
	# event handlers
	#-----------------------------------
	def on_submit_ID(self, event):
		#get value for chosen laboratory
		
		#get id to associate with lab/probe
		#item2.
		pass
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		#pass
		evt.Skip()
	#-------------------------------------------------------
	def __on_lab_selected(self,evt):
		#item2.SetValue(self.last_id[self.item1.GetValue()])
		print ' it works'
#== classes for standalone use ==================================
if __name__ == '__main__':

	print "let's work on the plugin version only for now"

#	from Gnumed.pycommon import gmLoginInfo
#	from Gnumed.business import gmXdtObjects, gmXdtMappings, gmDemographicRecord

#	wxID_btn_quit = wxNewId()

#	class cStandalonePanel(wxPanel):

#		def __init__(self, parent, id):
#			# get patient from file
#			if self.__get_pat_data() is None:
#				raise gmExceptions.ConstructorError, "Cannot load patient data."

			# set up database connectivity
#			auth_data = gmLoginInfo.LoginInfo(
#				user = _cfg.get('database', 'user'),
#				passwd = _cfg.get('database', 'password'),
#				host = _cfg.get('database', 'host'),
#				port = _cfg.get('database', 'port'),
#				database = _cfg.get('database', 'database')
#			)
#			backend = gmPG.ConnectionPool(login = auth_data)

			# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
#			cooked_search_terms = {
				#'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
#				'lastnames': self.__xdt_pat['last name'],
#				'firstnames': self.__xdt_pat['first name'],
#				'gender': self.__xdt_pat['gender']
#			}
#			print cooked_search_terms
			# find matching patient IDs
#			searcher = gmPatient.cPatientSearcher_SQL()
#			patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
#			if patient_ids is None or len(patient_ids)== 0:
#				gmGuiHelpers.gm_show_error(
#					aMessage = _('This patient does not exist in the document database.\n"%s %s"') % (self.__xdt_pat['first name'], self.__xdt_pat['last name']),
#					aTitle = _('searching patient')
#				)
#				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
#				raise gmExceptions.ConstructorError, "Patient from XDT file does not exist in database."

			# ambigous ?
#			if len(patient_ids) != 1:
#				gmGuiHelpers.gm_show_error(
#					aMessage = _('Data in xDT file matches more than one patient in database !'),
#					aTitle = _('searching patient')
#				)
#				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
#				raise gmExceptions.ConstructorError, "Problem getting patient ID from database. Aborting."

#			try:
#				gm_pat = gmPatient.gmCurrentPatient(aPKey = patient_ids[0])
#			except:
				# this is an emergency
#				gmGuiHelpers.gm_show_error(
#					aMessage = _('Cannot load patient from database !\nAborting.'),
#					aTitle = _('searching patient')
#				)
#				_log.Log(gmLog.lPanic, 'Cannot access patient [%s] in database.' % patient_ids[0])
#				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
#				raise

			# make main panel
#			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
#			self.SetTitle(_("lab journal"))

			# make patient panel
#			gender = gmDemographicRecord.map_gender_gm2long[gmXdtMappings.map_gender_xdt2gm[self.__xdt_pat['gender']]]
#			self.pat_panel = wxStaticText(
#				id = -1,
#				parent = self,
#				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
#				style = wxALIGN_CENTER
#			)
#			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make lab journal notebook 
#			self.nb = cLabJournalNB(self, -1)
#			self.nb.update()

			# buttons
#			btn_quit = wxButton(
#				parent = self,
#				id = wxID_btn_quit,
#				label = _('Quit')
#			)
#			EVT_BUTTON (btn_quit, wxID_btn_quit, self.__on_quit)
			
#			szr_buttons = wxBoxSizer(wxHORIZONTAL)
#			szr_buttons.Add(btn_quit, 0, wxALIGN_CENTER_VERTICAL, 1)

#			szr_main = wxBoxSizer(wxVERTICAL)
#			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
#			szr_nb = wxNotebookSizer( self.nb )
			
#			szr_main.Add(szr_nb, 1, wxEXPAND, 9)
#			szr_main.Add(szr_buttons, 0, wxEXPAND, 1)

#			self.SetAutoLayout(1)
#			self.SetSizer(szr_main)
#			szr_main.Fit(self)
#			self.Layout()
		#--------------------------------------------------------
#		def __get_pat_data(self):
		#	"""Get data of patient for which to retrieve documents.

		#	"""
			# FIXME: error checking
#			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			# FIXME: actually handle pat_format, too
#			pat_format = _cfg.get("viewer", "patient file format")

			# get patient data from BDT file
#			try:
#				self.__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
#			except:
#				_log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
#				gmGuiHelpers.gm_show_error(
#					aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
#					aTitle = _('loading patient from xDT file')
#				)
#				return None

#			return 1
		#--------------------------------------------------------
#		def __on_quit(self, evt):
#			app = wxGetApp()
#			app.ExitMainLoop()

#== classes for plugin use ======================================
else:

	class cPluginPanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make lab notebook
			self.nb = cLabJournalNB(self, -1)
			
			# just one vertical sizer
			sizer = wxBoxSizer(wxVERTICAL)
			szr_nb = wxNotebookSizer( self.nb )
			
			sizer.Add(szr_nb, 1, wxEXPAND, 0)
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

	class gmLabJournal(gmPlugin.wxNotebookPlugin):
		tab_name = _("lab journal")

		def name (self):
			return gmLabJournal.tab_name

		def GetWidget (self, parent):
			self.panel = cPluginPanel(parent, -1)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('Show &lab journal'))

		def ReceiveFocus(self):
			if self.panel.nb.update() is None:
				_log.Log(gmLog.lErr, "cannot update lab journal with data")
				return None
			# FIXME: register interest in patient_changed signal, too
			#self.panel.tree.SelectItem(self.panel.tree.root)
			self.DoStatusText()
			return 1

		def can_receive_focus(self):
			# need patient
			if not self._verify_patient_avail():
				return None
			return 1

		def DoToolbar (self, tb, widget):
			
			tb.AddControl(wxStaticBitmap(
				tb,
				-1,
				images_Archive_plugin.getvertical_separator_thinBitmap(),
				wxDefaultPosition,
				wxDefaultSize
			))
			
		def DoStatusText (self):
			# FIXME: people want an optional beep and an optional red backgound here
			#set_statustext = gb['main.statustext']
				txt = _('how are you doing today ?') 
				if not self._set_status_txt(txt):
					return None
				return 1
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting lab journal")

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
	#gmPG.StopListeners()
	_log.Log (gmLog.lInfo, "closing lab journal")
else:
	# we are being imported
	pass
#================================================================
# $Log: gmLabJournal.py,v $
# Revision 1.3  2004-04-29 21:05:19  shilbert
# - some more work on auto update of id field
#
# Revision 1.2  2004/04/28 16:12:02  ncq
# - cleanups, as usual
#
# Revision 1.1  2004/04/28 07:20:00  shilbert
# - initial release after name change, lacks features
#
