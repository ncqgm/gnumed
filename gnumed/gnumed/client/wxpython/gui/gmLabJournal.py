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
from Gnumed.business import gmPatient, gmClinicalRecord, gmPathLab
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel
from Gnumed.pycommon.gmPyCompat import *

# 3rd party
from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

[   wxID_PNL_main,
	wxID_NB_LabJournal,
	wxID_LBOX_pending_results,
	wxID_PHRWH_labs,
	wxID_TXTCTRL_ids,
	wxID_BTN_save_request_ID
] = map(lambda _init_ctrls: wxNewId(), range(6))

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
			#id_callback = self.wheel_callback
		)
		self.SetToolTipString(_('choose which lab will process the probe with the specified ID'))
	
	#def wheel_callback(self, data):
	#	print data
#====================================
class gmLabIDListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wxDefaultPosition, size=wxDefaultSize, style=0):
        wxListCtrl.__init__(self, parent, ID, pos, size, style)
        wxListCtrlAutoWidthMixin.__init__(self)

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
		self.PNL_errors_tab = wxPanel( self, -1)
		szr_errors = self.__init_SZR_import_errors()

		self.PNL_errors_tab.SetAutoLayout( True )
		self.PNL_errors_tab.SetSizer( szr_errors )
		szr_errors.Fit( self.PNL_errors_tab )
		szr_errors.SetSizeHints( self.PNL_errors_tab )

		self.AddPage( self.PNL_errors_tab, _("lab errors"))
		
		self.curr_pat = gmPatient.gmCurrentPatient()
	#------------------------------------------------------------------------
	def __init_SZR_due (self, call_fit = True, set_sizer = True ):

		vbszr_main = wxBoxSizer( wxVERTICAL )
		lab_wheel = cLabWheel(self.PNL_due_tab)
		lab_wheel.on_resize (None)
		lab_wheel.addCallback(self.on_lab_selected)
		
		vbszr_main.AddWindow(lab_wheel, 0, wxALIGN_CENTER | wxALL, 5)

		self.item2 = wxTextCtrl(
			self.PNL_due_tab,
			wxID_TXTCTRL_ids,
			"",
			wxDefaultPosition,
			wxSize(80,-1),
			0
			)

		vbszr_main.AddWindow( self.item2, 0, wxALIGN_CENTER|wxALL, 5 )

		# -- "save request id" button -----------
		self.BTN_save_request_ID = wxButton(
			name = 'BTN_save_request_ID',
			parent = self.PNL_due_tab,
			id = wxID_BTN_save_request_ID,
			label = _("save request ID")
		)
		self.BTN_save_request_ID.SetToolTipString(_('associate chosen lab and ID with current patient'))
		EVT_BUTTON(self.BTN_save_request_ID, wxID_BTN_save_request_ID, self.on_save_request_ID)

		vbszr_main.AddWindow( self.BTN_save_request_ID, 0, wxALIGN_CENTER|wxALL, 5 )

		# maybe have a look at MultiColumnList
		# our actual list
		tID = wxNewId()
		self.lbox_pending = gmLabIDListCtrl(
			self.PNL_due_tab,
			tID,
			size=(400,100),
			style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES
		)#|wxLC_HRULES)

		self.lbox_pending.InsertColumn(0, _("date"))
		self.lbox_pending.InsertColumn(1, _("lab"))
		self.lbox_pending.InsertColumn(2, _("id"))
		self.lbox_pending.InsertColumn(3, _("patient"))
		self.lbox_pending.InsertColumn(4, _("status"))
		
		vbszr_main.AddWindow( self.lbox_pending, 0, wxALIGN_CENTER|wxALL, 5 )
		return vbszr_main

	def __init_SZR_import_errors (self, call_fit = True, set_sizer = True ):
	
		xvszr_main = wxBoxSizer( wxVERTICAL )
		
		tID = wxNewId()
		self.lbox_errors = gmLabIDListCtrl(
			self.PNL_errors_tab,
			tID,
			size=(400,100),
			style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES
		)#|wxLC_HRULES)
		
		xvszr_main.AddWindow(self.lbox_errors, 0, wxALIGN_CENTER | wxALL, 5)

		self.lbox_errors.InsertColumn(0, _("when"))
		self.lbox_errors.InsertColumn(1, _("problem"))
		self.lbox_errors.InsertColumn(2, _("solution"))
		 
		return xvszr_main
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
		
		self.item2.Clear()
		self.lbox_pending.Clear()
		#------ due PNL ------------------------------------
		pending_requests = self.__get_pending_requests()
		for request in pending_requests:
			# for pending requests
			if request[3]:
				self.idx = self.lbox_pending.InsertItem(info=wxListItem())
				idx=self.idx
				# -- display request date ------------------- 
				self.lbox_pending.SetStringItem(index = idx, col=0, label=request[0].date)
				# -- display request lab ---------------------
				lab = self.__get_labname(request[1])[0][0]
				self.lbox_pending.SetStringItem(index = idx, col=1, label=lab)
				# -- display associated patient name ---
				self.lbox_pending.SetStringItem(index = idx, col=2, label=request[2])
				patient = self.get_patient_for_lab_request(request[2],lab)
				# FIXME: make use of rest data in patient via mouse over context
				self.lbox_pending.SetStringItem(index = idx, col=3, label=patient[2]+' '+patient[3])
				self.lbox_pending.SetStringItem(index = idx, col=4, label=_('pending'))
		
		
		#----- import errors PNL -----------------------
		lab_errors = self.__show_import_errors()
		for lab_error in lab_errors:
			self.idx = self.lbox_errors.InsertItem(info=wxListItem())
			idx=self.idx
			# -- display  when error was reported ------------------- 
			self.lbox_errors.SetStringItem(index = idx, col=0, label=lab_error[1].date)
			# -- what's the problem ---------------------
			self.lbox_errors.SetStringItem(index = idx, col=1, label=lab_error[4])
			# -- how can we fix it ---
			self.lbox_errors.SetStringItem(index = idx, col=2, label=lab_error[5])
			
	#-------------------------------------------------------------------------
	def get_patient_for_lab_request(self,req_id,lab):
		lab_req = gmPathLab.cLabRequest(req_id=req_id, lab=lab)
		patient = lab_req.get_patient()
		return patient
	#-------------------------------------------------------------------------		
	def __get_pending_requests(self):
		query = """select clin_when, fk_test_org, request_id, is_pending from lab_request where is_pending is true"""
		pending_requests = gmPG.run_ro_query('historica', query)
		return pending_requests
	#------------------------------------------------------------------------
	def __show_import_errors(self):
		query = """select * from housekeeping_todo where category='lab'"""
		import_errors = gmPG.run_ro_query('historica', query)
		return import_errors
	#------------------------------------------------------------------------
	def __get_labname(self, data):
		query= """select internal_name from test_org where pk=%s"""
		labs = gmPG.run_ro_query('historica', query, None, data)
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
	#--------------------------------------------------------------------------	
	def guess_next_id(self, lab_name):
		last = self.__get_last_used_ID(lab_name)[0][0]
		next = chr(ord(last[-1:])+1)
		return next
	#-----------------------------------
	# event handlers
	#-----------------------------------
	def on_save_request_ID(self, event):
	
		emr = self.curr_pat.get_clinical_record()
		#test = gmPathLab.create_lab_request(lab=self.lab_name[0][0], req_id = self.item2.GetValue(), pat_id = self.curr_pat['ID'], encounter_id = emr.id_encounter, episode_id= emr.id_episode)
		test = gmPathLab.create_lab_request(req_id='ML#SC937-0176-CEC#11', lab='Enterprise Main Lab', encounter_id = emr.id_encounter, episode_id= emr.id_episode)
		# react on succes or failure of save_request
		#print self.lab_name[0][0] , self.item2.GetValue(), #pat_id, encounter_id, episode_id
		
		print test
		self.__populate_notebook()
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		#pass
		evt.Skip()
	#-------------------------------------------------------
	def on_lab_selected(self,data):
		print "phrase wheel just changed lab to", data
		# get last used id for lab
		self.lab_name = self.__get_labname(data)
		print self.lab_name
		#guess next id
		nID = self.guess_next_id(self.lab_name[0][0])
		# set field to that
		self.item2.SetValue(nID)
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
# Revision 1.5  2004-05-04 07:19:34  shilbert
# - kind of works, still a bug in create_request()
#
# Revision 1.4  2004/05/01 10:29:46  shilbert
# - custom event handlig code removed, pending lab ids input almost completed
#
# Revision 1.3  2004/04/29 21:05:19  shilbert
# - some more work on auto update of id field
#
# Revision 1.2  2004/04/28 16:12:02  ncq
# - cleanups, as usual
#
# Revision 1.1  2004/04/28 07:20:00  shilbert
# - initial release after name change, lacks features
#
