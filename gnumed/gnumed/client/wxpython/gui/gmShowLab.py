"""Notebook plugin showing patient specific lab data.
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmShowLab.py,v $
__version__ = "$Revision: 1.24 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys

# 3rd party
import wx
import wx.grid

from Gnumed.pycommon import gmI18N, gmGuiBroker, gmExceptions
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmGuiHelpers, gmPlugin, gmLabWidgets

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#== classes for standalone use ==================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

	from Gnumed.business import gmXdtObjects, gmXdtMappings, gmDemographicRecord

	wxID_btn_quit = wx.NewId()

	class cStandalonePanel(wx.Panel):

		def __init__(self, parent, id):
			# get patient from file
			if self.__get_pat_data() is None:
				raise gmExceptions.ConstructorError, "Cannot load patient data."

			# set up database connectivity
			auth_data = gmLoginInfo.LoginInfo(
				user = _cfg.get('database', 'user'),
				password = _cfg.get('database', 'password'),
				host = _cfg.get('database', 'host'),
				port = _cfg.get('database', 'port'),
				database = _cfg.get('database', 'database')
			)
			backend = gmPG.ConnectionPool(login = auth_data)

			# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
			cooked_search_terms = {
				#'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
				'lastname': self.__xdt_pat['last name'],
				'firstname': self.__xdt_pat['first name'],
				'gender': self.__xdt_pat['gender']
			}
			# find matching patient IDs
			searcher = gmPerson.cPatientSearcher_SQL()
			patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
			print "must use dto, not search_dict"
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
				gm_pat = gmPerson.gmCurrentPatient(aPKey = patient_ids[0])
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
			wx.Panel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("Stored lab data"))

			# make patient panel
			gender = gmDemographicRecord.map_gender_gm2long[gmXdtMappings.map_gender_xdt2gm[self.__xdt_pat['gender']]]
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wx.NORMAL, wx.NORMAL, 0, ""))

			# make lab record grid 
			self.grid = gmLabWidgets.cLabDataGrid(self, -1)
			self.grid.update()

			# buttons
			btn_quit = wx.Button(
				parent = self,
				id = wxID_btn_quit,
				label = _('Quit')
			)
			wx.EVT_BUTTON (btn_quit, wxID_btn_quit, self.__on_quit)
			szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
			szr_buttons.Add(btn_quit, 0, wxALIGN_CENTER_VERTICAL, 1)

			# layout
			szr_main = wx.BoxSizer(wx.VERTICAL)
			#szr_grid = wxGridSizer(0,wxEXPAND,0)
			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
			szr_main.Add(self.grid, 1,wxEXPAND, 1)
			#szr_main.Add(szr_grid, 1, wxEXPAND, 9)
			#szr_grid.Add(self.grid, 1, wxEXPAND, 9)
			szr_main.Add(szr_buttons, 0, wxEXPAND, 1)

			self.SetAutoLayout(1)
			self.SetSizer(szr_main)
			#szr_main.Fit(self)
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

	class cPluginGridPanel(wx.Panel):
		def __init__(self, parent, id):
			# set up widgets
			wx.Panel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make grid
			self.grid = gmLabWidgets.cLabDataGrid(self, -1)

			# just one vertical sizer
			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(self.grid, 1,wxEXPAND, 1)
			self.SetAutoLayout(1)
			self.SetSizer(sizer)
			sizer.Fit(self)
			self.Layout()
	#------------------------------------------------------------
	class gmShowLab(gmPlugin.cNotebookPluginOld):
		tab_name = _("path lab")

		def name (self):
			return gmShowLab.tab_name

		def GetWidget (self, parent):
			self._widget = cPluginGridPanel(parent, -1)
			return self._widget

		def MenuInfo (self):
			return ('tools', _('Show &archived lab data'))

		def populate_with_data(self):
			# no use reloading if invisible
			if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
				return 1
			if self._widget.grid.update() is None:
				_log.Log(gmLog.lErr, "cannot update grid with lab data")
				return None
			# FIXME: ?!?
			self._widget.Layout()
			self._widget.Refresh()
			return 1

		def can_receive_focus(self):
			# need patient
			if not self._verify_patient_avail():
				return None
			return True
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
# $Log: gmShowLab.py,v $
# Revision 1.24  2008-03-06 18:32:31  ncq
# - standard lib logging only
#
# Revision 1.23  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.22  2007/03/08 11:54:44  ncq
# - cleanup
#
# Revision 1.21  2007/01/21 12:22:02  ncq
# - comment on search_dict -> dto
#
# Revision 1.20  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.19  2006/07/24 14:19:36  ncq
# - cleanup
#
# Revision 1.18  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.17  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.16  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.15  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.14  2004/07/15 16:04:05  ncq
# - fixed missing relative import
#
# Revision 1.13  2004/07/15 15:53:52  ncq
# - go back to notebook plugin
# - big cleanup/refactoring, see wxpython/gmLabWidgets.py
#
# Revision 1.12  2004/07/15 07:57:21  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.11  2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.10  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.9  2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.8  2004/05/21 07:28:55  shilbert
# - multiline cells now actually work
# - grid now fully expands as per request by ncq
#
# Revision 1.7  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.6  2004/04/20 00:15:36  ncq
# - slight deuglification
#
# Revision 1.5  2004/04/16 22:28:07  shilbert
# - code cleanups , make use of 'def __compile_stats():'
# - framework for user defined lab profiles
#
# Revision 1.4  2004/04/16 00:27:13  ncq
# - PyCompat
#
# Revision 1.3  2004/04/15 20:14:14  shilbert
# - supports multiline text, uses custom renderer
# - changes in font, data alignment
#
# Revision 1.2  2004/04/15 09:52:22  shilbert
# - display unified_name instead of lab_name as requested by ncq
#
# Revision 1.1  2004/04/15 09:45:31  ncq
# - first functional version, still ugly
#
