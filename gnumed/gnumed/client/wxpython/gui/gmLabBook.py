"""
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmLabBook.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re, string, random

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmPG, gmCfg, gmExceptions, gmWhoAmI
from Gnumed.business import gmPatient, gmClinicalRecord
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.pycommon.gmPyCompat import *

# 3rd party
from wxPython.wx import *
#from wxPython.grid import * 

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

[   wxID_PNL_main,
	wxID_NB_LabBook
] = map(lambda _init_ctrls: wxNewId(), range(2))
#================================================================


class cLabBookNB(wxNotebook):
	"""This wxNotebook derivative displays 'records still due' and lab-import related errors.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised notebook.
		"""
		# get connection
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')
		if self.__defconn is None:
			_log.Log(gmLog.lErr, "Cannot retrieve lab data without database connection !")
			raise gmExceptions.ConstructorError, "cLabBookNB.__init__(): need db conn"

		# connect to config database
		self.__dbcfg = gmCfg.cCfgSQL(
			aConn = self.__backend.GetConnection('default'),
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
			
		self.curr_pat = gmPatient.gmCurrentPatient()

	
	def OnLeftDClick(self, evt):
		pass
	#------------------------------------------------------------------------
	def update(self):
		if self.curr_pat['ID'] is None:
			_log.Log(gmLog.lErr, 'need patient for update, no patient related notebook tabs will be visible')
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot load lab book.\nYou first need to select a patient.'),
				aTitle = _('loading lab book')
			)
			return None
			
		if self.__populate_notebook() is None:
			return None

		return 1
	#------------------------------------------------------------------------
	def __populate_notebook(self):
		
		PNL_due_tab = wxPanel( self, -1 )
		PNL_error_tab = wxPanel( self, -1)
		self.AddPage( PNL_due_tab, _("outstanding results"))
		self.AddPage( PNL_error_tab, _("error log"))
		
		# FIXME: check if patient changed at all
		emr = self.curr_pat.get_clinical_record()
		# FIXME: there might be too many results to handle in memory
		lab = emr.get_lab_results()

		if lab is None or len(lab)==0:
			name = self.curr_pat['demographic record'].get_names()
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot find any lab data for patient\n[%s %s].') % (name['first'], name['last']),
				aTitle = _('loading lab record list')
				)
			return None
			
		else:
			return 1
	
	#------------------------------------------------------------------------		
	def __compile_stats(self, lab_results=None):
		# parse record for dates and tests
		dates = []
		test_names = []
		for result in lab_results:
			if result['val_when'].date not in dates:
				dates.append(result['val_when'].date)
			if result['unified_name'] not in test_names:
				test_names.append(result['unified_name'])
		dates.sort()
		print dates
		print test_names
		
		return dates, test_names
	#------------------------------------------------------------------------
	def __GetDataCell(self, item=None, xorder=None, yorder=None):
		#fixme: get real for x
		x = xorder.index(item['val_when'].date)
		y= yorder.index(item['unified_name'])
		return (y,x)
	#------------------------------------------------------------------------
	#def sort_by_value(self, d=None):
	#    """ Returns the keys of dictionary d sorted by their values """
	#    items=d.items()
	#    backitems=[ [v[1],v[0]] for v in items]
	#    backitems.sort()
	#    return [ backitems[i][1] for i in range(0,len(backitems))]
	
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		pass
		#evt.Skip()
	#--------------------------------------------------------
	#def __show_description(self, evt):
	#    print "showing description"
	#--------------------------------------------------------
	#def __handle_obj_context(self, data):
	#    print "handling object context menu"
	#--------------------------------------------------------
	
#== classes for standalone use ==================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmLoginInfo
	from Gnumed.business import gmXdtObjects, gmXdtMappings, gmDemographicRecord

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
				#'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
				'lastnames': self.__xdt_pat['last name'],
				'firstnames': self.__xdt_pat['first name'],
				'gender': self.__xdt_pat['gender']
			}
			print cooked_search_terms
			# find matching patient IDs
			searcher = gmPatient.cPatientSearcher_SQL()
			patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
			if patient_ids is None or len(patient_ids)== 0:
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
			self.SetTitle(_("lab book"))

			# make patient panel
			gender = gmDemographicRecord.map_gender_gm2long[gmXdtMappings.map_gender_xdt2gm[self.__xdt_pat['gender']]]
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make lab book notebook 
			self.nb = cLabBookNB(self, -1)
			self.nb.update()

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
			szr_nb = wxNotebookSizer( self.nb )
			
			szr_main.Add(szr_nb, 1, wxEXPAND, 9)
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

	class cPluginPanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make lab notebook
			self.nb = cLabBookNB(self, -1)
			
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

	class gmLabBook(gmPlugin.wxNotebookPlugin):
		tab_name = _("lab book")

		def name (self):
			return gmLabBook.tab_name

		def GetWidget (self, parent):
			self.panel = cPluginPanel(parent, -1)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('Show &lab book'))

		def ReceiveFocus(self):
			if self.panel.nb.update() is None:
				_log.Log(gmLog.lErr, "cannot update grid with lab data")
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
	_log.Log (gmLog.lInfo, "starting lab viewer")

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
	_log.Log (gmLog.lInfo, "closing lab viewer")
else:
	# we are being imported
	pass
#================================================================
# $Log: gmLabBook.py,v $
# Revision 1.1  2004-04-25 08:30:09  shilbert
# - initial check-in; needs work
#
