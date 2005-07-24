# -*- coding: iso-8859-1 -*-
"""GnuMed GUI client

The application framework and main window of the
all signing all dancing GNUMed reference client.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.

copyright: authors
"""
#==============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmGuiMain.py,v $
# $Id: gmGuiMain.py,v 1.211 2005-07-24 11:35:59 ncq Exp $
__version__ = "$Revision: 1.211 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import sys, time, os, cPickle, zlib

try:
	from wxPython import wx
except ImportError:
	print "GNUmed startup: Cannot import wxPython library."
	print "GNUmed startup: Make sure wxPython is installed."
	print 'CRITICAL ERROR: Error importing wxPython. Halted.'
	raise

from Gnumed.pycommon import gmLog, gmCfg, gmWhoAmI, gmPG, gmDispatcher, gmSignals, gmCLI, gmGuiBroker, gmI18N
from Gnumed.wxpython import gmGuiHelpers, gmHorstSpace, gmRichardSpace, gmEMRBrowser, gmDemographicsWidgets, gmEMRStructWidgets, gmEditArea
from Gnumed.business import gmPerson
from Gnumed.exporters import gmPatientExporter
from Gnumed.pycommon.gmPyCompat import *

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()
email_logger = None
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_log.Log(gmLog.lInfo, 'GUI framework: %s' % wx.wxVERSION_STRING)

#try:
#	vm = wx.VideoMode()
#	_log.Log(gmLog.lInfo, 'display: %s:%s@%s' % (vm.v, vm.h, vm.bpp))
#except AttributeError:
#	pass

# set up database connection encoding
encoding = _cfg.get('backend', 'client encoding')
if encoding is None:
	print 'WARNING: option <client encoding> not set in config file'
	_log.Log(gmLog.lWarn, 'you need to set the parameter <client encoding> in the config file')
	_log.Log(gmLog.lWarn, 'on Linux you can determine a likely candidate for the encoding by running "locale charmap"')
gmPG.set_default_client_encoding(encoding)

# set up database connection timezone
timezone = _cfg.get('backend', 'client timezone')
if timezone is not None:
	gmPG.set_default_client_timezone(timezone)

ID_ABOUT = wx.wxNewId ()
ID_CONTRIBUTORS = wx.wxNewId()
ID_EXIT = wx.wxNewId ()
ID_HELP = wx.wxNewId ()
ID_NOTEBOOK = wx.wxNewId ()
ID_LEFTBOX = wx.wxNewId ()
ID_EXPORT_EMR = wx.wxNewId()
ID_EXPORT_EMR_JOURNAL = wx.wxNewId()
ID_EXPORT_MEDISTAR = wx.wxNewId()
ID_CREATE_PATIENT = wx.wxNewId()
ID_SEARCH_EMR = wx.wxNewId()
ID_ADD_HEALTH_ISSUE_TO_EMR = wx.wxNewId()
#==============================================================================

icon_serpent = \
"""x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec"""

#==============================================================================
class gmTopLevelFrame(wx.wxFrame):
	"""GNUmed client's main windows frame.

	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""

	#----------------------------------------------
	def __init__(self, parent, id, title, size=wx.wxPyDefaultSize, layout=None):
		"""You'll have to browse the source to understand what the constructor does
		"""
		wx.wxFrame.__init__(
			self,
			parent,
			id,
			title,
			size,
			style = wx.wxDEFAULT_FRAME_STYLE
		)

		#initialize the gui broker
		self.__gb = gmGuiBroker.GuiBroker()
		self.__gb['EmergencyExit'] = self._clean_exit
		self.__gb['main.frame'] = self
		self.bar_width = -1
		_log.Log(gmLog.lData, 'workplace is >>>%s<<<' % _whoami.get_workplace())
		self.__setup_main_menu()
		self.SetupStatusBar()
		self.SetStatusText(_('You are logged in as %s (%s). DB account <%s>.') % (_whoami.get_staff_name(), _whoami.get_staff_sign(), _whoami.get_db_account()))
		self.__gb['main.statustext'] = self.SetStatusText

		# set window title via template
		if self.__gb['main.slave_mode']:
			self.__title_template = _('Slave GNUmed [%s@%s] %s: %s')
		else:
			self.__title_template = 'GNUmed [%s@%s] %s: %s'
		self.updateTitle(anActivity = _("idle"))
		self.__setup_platform()
		#  let others have access, too
		self.__gb['main.SetWindowTitle'] = self.updateTitle
		if layout is None:
			# get plugin layout style
			self.layout_style, set1 = gmCfg.getDBParam(
				workplace = _whoami.get_workplace(),
				option = 'main.window.layout_style'
				)
			if set1 is None:
				self.layout_style = 'status_quo'
				gmCfg.setDBParam (
					workplace = _whoami.get_workplace(),
					option = 'main.window.layout_style',
					value = self.layout_style
					)
			#----------------------
			# create layout manager
			#----------------------
			if self.layout_style == 'status_quo':
				_log.Log(gmLog.lInfo, 'loading Horst space layout manager')
				self.LayoutMgr = gmHorstSpace.cHorstSpaceLayoutMgr(self, -1)
			elif self.layout_style == 'terry':
				_log.Log(gmLog.lInfo, "loading Richard Terry's layout manager")
				self.LayoutMgr = gmRichardSpace.cLayoutMgr(self, -1)
		else:
			# layout class is explicitly provided, use that
			_log.Log (gmLog.lInfo, "loading %s as toplevel" % layout)
			l = layout.split (".")
			self.LayoutMgr = getattr (__import__ (".".join (l[:-1])), l[-1]) (self, -1)
		# set window icon
		icon_bmp_data = wx.wxBitmapFromXPMData(cPickle.loads(zlib.decompress(icon_serpent)))
		icon = wx.wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)
		self.acctbl = []
		self.__gb['main.accelerators'] = self.acctbl
		self.__register_events()
		self.vbox = wx.wxBoxSizer(wx.wxVERTICAL)
		self.vbox.Add(self.LayoutMgr, 10, wx.wxEXPAND | wx.wxALL, 1)

		self.SetAutoLayout(True)
		self.SetSizer(self.vbox)
		self.vbox.Fit(self)

		# don't allow the window to get too small
		# setsizehints only allows minimum size, therefore window can't become small enough
		# effectively we need the font size to be configurable according to screen size
		#self.vbox.SetSizeHints(self)
		self.__set_GUI_size()

		self.Centre(wx.wxBOTH)
		self.Show(True)
	#----------------------------------------------
	def __set_GUI_size(self):
		"""Try to get previous window size from backend."""

 		def_width, def_height = (640,480)
		# width
 		prev_width, set1 = gmCfg.getDBParam( 
			workplace = _whoami.get_workplace(),
 			option = 'main.window.width'
		)
		if set1 is None:
			desired_width = def_width
			gmCfg.setDBParam (
				workplace = _whoami.get_workplace(),
				option = 'main.window.width',
				value = desired_width
			)
		else:
			desired_width = int(prev_width)

		# height
 		prev_height, set1 = gmCfg.getDBParam( 
 			workplace = _whoami.get_workplace(),
 			option = 'main.window.height'
 		)
		if set1 is None:
 			desired_height = def_height
			gmCfg.setDBParam(
				workplace = _whoami.get_workplace(),
				option = 'main.window.height',
				value = desired_height
			)
		else:
			desired_height = int(prev_height)

		_log.Log(gmLog.lData, 'setting GUI size to [%s:%s]' % (desired_width, desired_height))
 		self.SetClientSize(wx.wxSize(desired_width, desired_height))
	#----------------------------------------------
	def __setup_platform(self):
		#do the platform dependent stuff
		if wx.wxPlatform == '__WXMSW__':
			#windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on MS Windows')
		elif wx.wxPlatform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			_log.Log(gmLog.lInfo,'running on GTK (probably Linux)')
		elif wx.wxPlatform == '__WXMAC__':
			#Mac OS specific stuff here
			_log.Log(gmLog.lInfo,'running on Mac OS')
		else:
			_log.Log(gmLog.lInfo,'running on an unknown platform (%s)' % wx.wxPlatform)
	#----------------------------------------------
	def __setup_accelerators(self):
		self.acctbl.append ((wx.wxACCEL_ALT | wx.wxACCEL_CTRL, ord('X'), ID_EXIT))
		self.acctbl.append ((wx.wxACCEL_CTRL, ord('H'), ID_HELP))
		self.SetAcceleratorTable(wx.wxAcceleratorTable (self.acctbl))
	#----------------------------------------------
	def __setup_main_menu(self):
		"""Create the main menu entries.

		Individual entries are farmed out to the modules.
		"""
		# create main menu
		self.mainmenu = wx.wxMenuBar()
		self.__gb['main.mainmenu'] = self.mainmenu

		# menu "GNUmed"
		menu_gnumed = wx.wxMenu()
#		menu_gnumed.AppendSeparator()
		menu_gnumed.Append(ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUmed client'))
		wx.EVT_MENU(self, ID_EXIT, self.OnFileExit)
		self.mainmenu.Append(menu_gnumed, '&GNUmed')
#		self.__gb['main.filemenu'] = menu_gnumed

		# menu "Patient"
		menu_patient = wx.wxMenu()
		menu_patient.Append(ID_CREATE_PATIENT, _('Register new patient'), _("Register a new patient with this practice"))
		wx.EVT_MENU(self, ID_CREATE_PATIENT, self.__on_create_patient)
		self.mainmenu.Append(menu_patient, '&Patient')
		self.__gb['main.patientmenu'] = menu_patient

		# menu "EMR" ---------------------------
		menu_emr = wx.wxMenu()
		self.mainmenu.Append(menu_emr, _("&EMR"))
		self.__gb['main.emrmenu'] = menu_emr
		# - submenu "export as"
		menu_emr_export = wx.wxMenu()
		menu_emr.AppendMenu(wx.wxNewId(), _('Export as ...'), menu_emr_export)
		#   1) ASCII
		menu_emr_export.Append (
			ID_EXPORT_EMR,
			_('Text document'),
			_("Export the EMR of the active patient into a text file")
		)
		wx.EVT_MENU(self, ID_EXPORT_EMR, self.OnExportEMR)
		#   2) journal format
		menu_emr_export.Append (
			ID_EXPORT_EMR_JOURNAL,
			_('Journal'),
			_("Export the EMR of the active patient as a chronological journal into a text file")
		)
		wx.EVT_MENU(self, ID_EXPORT_EMR_JOURNAL, self.__on_export_emr_as_journal)
		#   3) Medistar import format
		menu_emr_export.Append (
			ID_EXPORT_MEDISTAR,
			_('MEDISTAR import format'),
			_("GNUmed -> MEDISTAR. Export progress notes of active patient's active encounter into a text file.")
		)
		wx.EVT_MENU(self, ID_EXPORT_MEDISTAR, self.__on_export_for_medistar)
		# - submenu "show as"
		menu_emr_show = wx.wxMenu()
		menu_emr.AppendMenu(wx.wxNewId(), _('Show as ...'), menu_emr_show)
		self.__gb['main.emr_showmenu'] = menu_emr_show
		# - draw a line
		menu_emr.AppendSeparator()
		# - search
		menu_emr.Append (
			ID_SEARCH_EMR,
			_('Search'),
			_('Search for data in the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_SEARCH_EMR, self.__on_search_emr)
		# - add health issue
		menu_emr.Append (
			ID_ADD_HEALTH_ISSUE_TO_EMR,
			_('Add health issue (pHx item)'),
			_('Add a health issue (pHx item) to the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_ADD_HEALTH_ISSUE_TO_EMR, self.__on_add_health_issue)
		# - draw a line
		menu_emr.AppendSeparator()

		# menu "View" ---------------------------
#		self.menu_view = wx.wxMenu()
#		self.__gb['main.viewmenu'] = self.menu_view
#		self.mainmenu.Append(self.menu_view, _("&View"));

		# menu "Tools"
		self.menu_tools = wx.wxMenu()
		self.__gb['main.toolsmenu'] = self.menu_tools
		self.mainmenu.Append(self.menu_tools, _("&Tools"))

		# menu "Reference"
		self.menu_reference = wx.wxMenu()
		self.__gb['main.referencemenu'] = self.menu_reference
		self.mainmenu.Append(self.menu_reference, _("&Reference"))

		# menu "Help"
		help_menu = wx.wxMenu()
		# - about
		help_menu.Append(ID_ABOUT, _('About GNUmed'), "")
		wx.EVT_MENU (self, ID_ABOUT, self.OnAbout)
		# - contributors
		help_menu.Append(ID_CONTRIBUTORS, _('GNUmed contributors'), _('show GNUmed contributors'))
		wx.EVT_MENU (self, ID_CONTRIBUTORS, self.__on_show_contributors)
		# - among other things the Manual is added from a plugin
		help_menu.AppendSeparator()
		self.__gb['main.helpmenu'] = help_menu
		self.mainmenu.Append(help_menu, "&Help")

		# and activate menu structure
		self.SetMenuBar(self.mainmenu)
	#----------------------------------------------
	def __load_plugins(self):
		pass
	#----------------------------------------------
	# event handling
	#----------------------------------------------
	def __register_events(self):
		"""register events we want to react to"""
		# wxPython events
#		wx.EVT_IDLE(self, self.OnIdle)
		wx.EVT_CLOSE(self, self.OnClose)
		wx.EVT_ICONIZE(self, self.OnIconize)
		wx.EVT_MAXIMIZE(self, self.OnMaximize)

		# intra-client signals
		gmDispatcher.connect(self.on_patient_selected, gmSignals.patient_selected())
	#-----------------------------------------------
	def on_patient_selected(self, **kwargs):
		wx.wxCallAfter(self.__on_patient_selected, **kwargs)
	#----------------------------------------------
	def __on_patient_selected(self, **kwargs):
		pat = gmPerson.gmCurrentPatient()
		try:
			pat.get_clinical_record()
			pat.get_identity()
		except:
			_log.LogException("Unable to process signal. Is gmCurrentPatient up to date yet?", sys.exc_info(), verbose=4)
			return None
		self.updateTitle()
	#----------------------------------------------
	def OnAbout(self, event):
		from Gnumed.wxpython import gmAbout
		gmAbout = gmAbout.AboutFrame(self, -1, _("About GNUmed"), size=wx.wxSize(300, 250), style = wx.wxMAXIMIZE_BOX)
		gmAbout.Centre(wx.wxBOTH)
		gmTopLevelFrame.otherWin = gmAbout
		gmAbout.Show(True)
		del gmAbout
	#----------------------------------------------
	def __on_show_contributors(self, event):
		from Gnumed.wxpython import gmAbout
		contribs = gmAbout.cContributorsDlg (
			parent = self,
			id = -1,
			title = _('GNUmed contributors'),
			size = wx.wxSize(400,600),
			style = wx.wxDEFAULT_DIALOG_STYLE | wx.wxRESIZE_BORDER
		)
		contribs.ShowModal()
		del contribs
		del gmAbout
	#----------------------------------------------
	def OnFileExit(self, event):
		"""Invoked from Menu->Exit (calls ID_EXIT handler)."""
		# calls EVT_CLOSE handler
		self.Close()
	#----------------------------------------------
	def OnClose(self, event):
		"""EVT_CLOSE handler.

		- framework still functional
		"""
		# call cleanup helper
		self._clean_exit()
	#----------------------------------------------
	def OnExportEMR(self, event):
		"""
		Export selected patient EMR to a file
		"""
		gmEMRBrowser.export_emr_to_ascii(parent=self)
	#----------------------------------------------
	def __on_add_health_issue(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(_('Cannot add health issue. No active patient.'), gmLog.lErr)
			return False
		ea = gmEMRStructWidgets.cHealthIssueEditArea (
			self,
			-1,
			wx.wxDefaultPosition,
			wx.wxDefaultSize,
			wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL
		)
			
		popup = gmEditArea.cEditAreaPopup (
			parent = None,
			id = -1,
			title = _('Add health issue (pHx item)'),
			style = wx.wxCENTRE | wx.wxSTAY_ON_TOP | wx.wxCAPTION | wx.wxSUNKEN_BORDER,
			name ='',
			edit_area = ea
		)
		result = popup.ShowModal()
#		if result == wx.wxID_OK:
#			summary = self.__popup.get_summary()
#			wx.wxCallAfter(self.Embed, summary)

	#----------------------------------------------
	def __on_search_emr(self, event):
		print "lacking code to search EMR"
	#----------------------------------------------
	def __on_export_emr_as_journal(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(_('Cannot export EMR journal. No active patient.'), gmLog.lErr)
			return False
		# get file name
		aWildcard = "%s (*.txt)|*.txt|%s (*.*)|*.*" % (_("text files"), _("all files"))
		# FIXME: make configurable
		aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed', 'export')))
		ident = pat.get_identity()
		# FIXME: make configurable
		fname = '%s-%s_%s.txt' % (_('emr-journal'), ident['lastnames'], ident['firstnames'])
		dlg = wx.wxFileDialog (
			parent = self,
			message = _("Save patient's EMR journal as..."),
			defaultDir = aDefDir,
			defaultFile = fname,
			wildcard = aWildcard,
			style = wx.wxSAVE
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.wxID_OK:
			return True

		_log.Log(gmLog.lData, 'exporting EMR journal to [%s]' % fname)
		# instantiate exporter
		wx.wxBeginBusyCursor()
		exporter = gmPatientExporter.cEMRJournalExporter()
		successful, fname = exporter.export_to_file(filename = fname)
		wx.wxEndBusyCursor()
		if not successful:
			gmGuiHelpers.gm_show_error (
				_('Error exporting patient EMR as chronological journal.'),
				_('EMR journal export'),
				gmLog.lErr
			)
			return False

#		gmGuiHelpers.gm_show_info (
#				_('Successfully exported EMR as chronological journal into file\n\n[%s]') % fname,
#				_('EMR journal export'),
#				gmLog.lInfo
#			)
		return True
	#----------------------------------------------
	def __on_export_for_medistar(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(_('Cannot export EMR for Medistar. No active patient.'), gmLog.lErr)
			return False
		# get file name
		aWildcard = "%s (*.txt)|*.txt|%s (*.*)|*.*" % (_("text files"), _("all files"))
		# FIXME: make configurable
		aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed','export')))
		ident = pat.get_identity()		
		# FIXME: make configurable
		fname = '%s-%s-%s-%s-%s.txt' % (
			'Medistar-MD',
			time.strftime('%Y-%m-%d',time.localtime()),
			ident['lastnames'].replace(' ', '-'),
			ident['firstnames'].replace(' ', '_'),
			ident['dob'].Format('%Y-%m-%d')
		)
		dlg = wx.wxFileDialog (
			parent = self,
			message = _("Save patient's EMR for MEDISTAR as..."),
			defaultDir = aDefDir,
			defaultFile = fname,
			wildcard = aWildcard,
			style = wx.wxSAVE
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.wxID_OK:
			return False

		_log.Log(gmLog.lData, 'exporting EMR journal to [%s]' % fname)
		# instantiate exporter		
		wx.wxBeginBusyCursor()
		exporter = gmPatientExporter.cMedistarSOAPExporter()
		successful, fname = exporter.export_to_file(filename=fname)
		wx.wxEndBusyCursor()
		if not successful:
			gmGuiHelpers.gm_show_error (
				_('Error exporting progress notes of current encounter for MEDISTAR import.'),
				_('MEDISTAR progress notes export'),
				gmLog.lErr
			)
			return False

#		else:
#			gmGuiHelpers.gm_show_info (
#				'Heutige Karteieinträge erfolgreich für Medistar exportiert. Datei:\n\n[%s]' % fname,
#				'Medistar-Export',
#				gmLog.lInfo
#			)
		return True
	#----------------------------------------------
	def __on_create_patient(self, event):
		"""
		Launch create patient wizard
		"""
		wiz = gmDemographicsWidgets.cNewPatientWizard(parent=self)
		wiz.RunWizard(activate=True)
	#----------------------------------------------
	def _clean_exit(self):
		"""Cleanup helper.

		- should ALWAYS be called when this program is
		  to be terminated
		- ANY code that should be executed before a
		  regular shutdown should go in here
		- framework still functional
		"""
		# signal imminent demise to plugins
		gmDispatcher.send(gmSignals.application_closing())
		# remember GUI size
		curr_width, curr_height = self.GetClientSizeTuple()
		_log.Log(gmLog.lInfo, 'GUI size at shutdown: [%s:%s]' % (curr_width, curr_height))
		gmCfg.setDBParam(
			workplace = _whoami.get_workplace(),
			option = 'main.window.width',
			value = curr_width
		)
		gmCfg.setDBParam(
			workplace = _whoami.get_workplace(),
			option = 'main.window.height',
			value = curr_height
		)
		# user changed the sidebar size -- remember that
		if self.bar_width > -1 and self.bar_width != 210:
			gmCfg.setDBParam(
				workplace = _whoami.get_workplace(),
				option = 'main.window.sidebar_width',
				value = self.bar_width
			)
		# handle our own stuff
		gmPG.ConnectionPool().StopListeners()
		try:
			gmGuiBroker.GuiBroker()['scripting listener'].tell_thread_to_stop()
		except KeyError:
			pass
		except:
			_log.LogException('cannot stop scripting listener thread', sys.exc_info(), verbose=0)
		self.timer.Stop()
		self.mainmenu = None
		self.Destroy()
	#----------------------------------------------
#	def OnIdle(self, event):
#		"""Here we can process any background tasks
#		"""
#		pass
	#----------------------------------------------
	def OnIconize(self, event):
		# FIXME: we should maximize the amount of title bar information here
		#_log.Log(gmLog.lInfo, 'OnIconify')
		event.Skip()
	#----------------------------------------------
	def OnMaximize(self, event):
		# FIXME: we should change the amount of title bar information here
		#_log.Log(gmLog.lInfo,'OnMaximize')
		event.Skip()
	#----------------------------------------------
	#----------------------------------------------
	def updateTitle(self, anActivity = None):
		"""Update title of main window based on template.

		This gives nice tooltips on iconified GnuMed instances.
		User research indicates that in the title bar people want
		the date of birth, not the age, so please stick to this
		convention.
		"""
		if anActivity is not None:
			self.title_activity = str(anActivity)

		pat = gmPerson.gmCurrentPatient()
		if pat.is_connected():
			ident = pat.get_identity()
			title = ident['title']
			if title is None:
				title = ''
			else:
				title = title[:4] + '.'
			pat_str = "%s%s %s (%s) #%d" % (title, ident['firstnames'], ident['lastnames'], ident['dob'].Format (_('%d/%m/%y')), ident['pk_identity'])
		else:
			pat_str = _('no patient')

		title = self.__title_template % (_whoami.get_staff_name(), _whoami.get_workplace(), self.title_activity, pat_str)
		self.SetTitle(title)
	#----------------------------------------------
	#----------------------------------------------
	def SetupStatusBar(self):
		sb = self.CreateStatusBar(2, wx.wxST_SIZEGRIP)
		sb.SetStatusWidths([-1, 150])
		#add time and date display to the right corner of the status bar
		self.timer = wx.wxPyTimer(self._cb_update_clock)
		self._cb_update_clock()
		#update every second
		self.timer.Start(milliseconds=1000)
	#----------------------------------------------
	def _cb_update_clock(self):
		"""Displays date and local time in the second slot of the status bar"""
		t = time.localtime(time.time())
		st = time.strftime(gmI18N.gmTimeformat, t)
		self.SetStatusText(st,1)
	#----------------------------------------------
#	def on_user_error (self, signal, message):
#		"response to user_error event"
#		self.SetStatusText (message, 0)
#		wx.wxBell()
	#------------------------------------------------
	def Lock(self):
		"""Lock GNUmed client against unauthorized access"""
		# FIXME
#		for i in range(1, self.nb.GetPageCount()):
#			self.nb.GetPage(i).Enable(False)
		return
	#----------------------------------------------
	def Unlock(self):
		"""Unlock the main notebook widgets
		As long as we are not logged into the database backend,
		all pages but the 'login' page of the main notebook widget
		are locked; i.e. not accessible by the user
		"""
		#unlock notebook pages
#		for i in range(1, self.nb.GetPageCount()):
#			self.nb.GetPage(i).Enable(True)
		# go straight to patient selection
#		self.nb.AdvanceSelection()
		return
	#-----------------------------------------------
	def OnPanelSize (self, event):
		wx.wxLayoutAlgorithm().LayoutWindow (self.LayoutMgr, self.nb)
	#------------------------------------------------
	def OnSashDrag (self, event):
		if event.GetDragStatus() == wx.wxSASH_STATUS_OUT_OF_RANGE:
			return
		self.leftbox.SetDefaultSize(wxSize(event.GetDragRect().width, 1000))
		self.bar_width = event.GetDragRect().width
		wx.wxLayoutAlgorithm().LayoutWindow(self.LayoutMgr, self.nb)
		self.nb.Refresh()

#==============================================================================
class gmApp(wx.wxApp):

	def OnInit(self):
		# create a GUI element dictionary that
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()
		self.__setup_platform()

		# check for slave mode
		tmp = _cfg.get('workplace', 'slave mode')
		if tmp == 1:
			self.__guibroker['main.slave_mode'] = True
		else:
			self.__guibroker['main.slave_mode'] = False
		if self.__guibroker['main.slave_mode']:
			self.__guibroker['main.slave_personality'] = _cfg.get('workplace', 'slave personality')
			if not self.__guibroker['main.slave_personality']:
				msg = _(
					'Slave mode requested but personality not set.\n\n'
					'(The personality must be set so that clients can\n'
					'find the appropriate GnuMed instance to attach to.)\n\n'
					'Set slave personality in config file !'
				)
				gmGuiHelpers.gm_show_error(msg, _('Starting slave mode'), gmLog.lErr)
				return False
			_log.Log(gmLog.lInfo, 'assuming slave mode personality [%s]' % self.__guibroker['main.slave_personality'])
		# connect to backend (implicitely runs login dialog)
		from Gnumed.wxpython import gmLogin
		self.__backend = gmLogin.Login()
		if self.__backend is None:
			_log.Log(gmLog.lWarn, "Login attempt unsuccesful. Can't run GnuMed without database connection")
			return False

		try:
			tmp = _whoami.get_staff_ID()
		except ValueError:
			_log.LogException('DB account [%s] not mapped to GnuMed staff member' % _whoami.get_db_account(), sys.exc_info(), verbose=0)
			msg = _(
				'The database account [%s] is not associated with\n'
				'any staff member known to GnuMed. You therefor\n'
				'cannot use GnuMed with this account.\n\n'
				'Please ask your administrator for help.\n'
			) % _whoami.get_db_account()
			gmGuiHelpers.gm_show_error(msg, _('Checking access permissions'))
			return False

		wx.EVT_QUERY_END_SESSION(self, self._on_query_end_session)
		wx.EVT_END_SESSION(self, self._on_end_session)

		# set up language in database
		self.__set_db_lang()
		# create the main window
		cli_layout = gmCLI.arg.get('--layout', None)
		frame = gmTopLevelFrame(None, -1, _('GnuMed client'), (640,440), cli_layout)
		# and tell the app to use it
		self.SetTopWindow(frame)
		#frame.Unlock()
		# NOTE: the following only works under Windows according
		# to the docs and bombs under wxPython-2.4 on GTK/Linux
		#frame.Maximize(True)
		frame.CentreOnScreen(wx.wxBOTH)
		frame.Show(True)

		# last but not least: start macro listener if so desired
		if self.__guibroker['main.slave_mode']:
			from Gnumed.pycommon import gmScriptingListener
			from Gnumed.wxpython import gmMacro
			macro_executor = gmMacro.cMacroPrimitives(self.__guibroker['main.slave_personality'])
			port = _cfg.get('workplace', 'xml-rpc port')
			if not port:
				port = 9999
			self.__guibroker['scripting listener'] = gmScriptingListener.cScriptingListener(port, macro_executor)
			_log.Log(gmLog.lInfo, 'listening for commands on port [%s]' % port)

		return True
	#----------------------------------------------
	def OnExit(self):
		"""Called:

		- after destroying all application windows and controls
		- before wxWindows internal cleanup
		"""
		pass
	#----------------------------------------------
	def _on_query_end_session(self):
		print "unhandled event detected: QUERY_END_SESSION"
		_log.Log(gmLog.lWarn, 'unhandled event detected: QUERY_END_SESSION')
		_log.Log(gmLog.lInfo, 'we should be saving ourselves from here')
	#----------------------------------------------
	def _on_end_session(self):
		print "unhandled event detected: END_SESSION"
		_log.Log(gmLog.lWarn, 'unhandled event detected: END_SESSION')
	#----------------------------------------------
	# internal helpers
	#----------------------------------------------
	def __setup_platform(self):
		if wx.wxPlatform == '__WXMSW__':
			# windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on Microsoft Windows')
			# need to explicitely init image handlers on windows
			wx.wxInitAllImageHandlers()
	#----------------------------------------------
	def __set_db_lang(self):
		if gmI18N.system_locale is None or gmI18N.system_locale == '':
			_log.Log(gmLog.lWarn, "system locale is undefined (probably meaning 'C')")
			return 1

		db_lang = None
		# get current database locale
		cmd = "select lang from i18n_curr_lang where owner = CURRENT_USER limit 1;"
		result = gmPG.run_ro_query('default', cmd, 0)
		if result is None:
			# if the actual query fails assume the admin
			# knows her stuff and fail graciously
			_log.Log(gmLog.lWarn, 'cannot get database language')
			_log.Log(gmLog.lInfo, 'assuming language settings are not wanted/needed')
			return None
		if len(result) == 0:
			msg = _(
				"There is no language selected in the database for user [%s].\n"
				"Your system language is currently set to [%s].\n\n"
				"Do you want to set the database language to '%s' ?\n\n"
				"Answering <NO> will remember that decision until\n"
				"the system language is changed. You can also reactivate\n"
				"this inquiry by removing the appropriate ignore option\n"
				"from the configuration file."
			)  % (_whoami.get_db_account(), gmI18N.system_locale, gmI18N.system_locale)
			_log.Log(gmLog.lData, "database locale currently not set")
		else:
			db_lang = result[0][0]
			msg = _(
				"The currently selected database language ('%s') does\n"
				"not match the current system language ('%s').\n\n"
				"Do you want to set the database language to '%s' ?\n\n"
				"Answering <NO> will remember that decision until\n"
				"the system language is changed. You can also reactivate\n"
				"this inquiry by removing the appropriate ignore option\n"
				"from the configuration file."
			) % (db_lang, gmI18N.system_locale, gmI18N.system_locale)
			_log.Log(gmLog.lData, "current database locale: [%s]" % db_lang)
			# check if we can match up system and db language somehow
			if db_lang == gmI18N.system_locale_level['full']:
				_log.Log(gmLog.lData, 'Database locale (%s) up to date.' % db_lang)
				return 1
			if db_lang == gmI18N.system_locale_level['country']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at country level.' % (db_lang, gmI18N.system_locale))
				return 1
			if db_lang == gmI18N.system_locale_level['language']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at language level.' % (db_lang, gmI18N.system_locale))
				return 1
			# no match
			_log.Log(gmLog.lWarn, 'database locale [%s] does not match system locale [%s]' % (db_lang, gmI18N.system_locale))

		# returns either None or a locale string
		ignored_sys_lang = _cfg.get('backend', 'ignored mismatching system locale')
		# are we to ignore *this* mismatch ?
		if gmI18N.system_locale == ignored_sys_lang:
			_log.Log(gmLog.lInfo, 'configured to ignore system-to-database locale mismatch')
			return 1
		# no, so ask user
		dlg = wx.wxMessageDialog(
			parent = None,
			message = msg,
			caption = _('checking database language settings'),
			style = wx.wxYES_NO | wx.wxCENTRE | wx.wxICON_QUESTION
		)
		result = dlg.ShowModal()
		dlg.Destroy()

		if result == wx.wxID_NO:
			_log.Log(gmLog.lInfo, 'User did not want to set database locale. Ignoring mismatch next time.')
			comment = [
				"If the system locale matches this value a mismatch",
				"with the database locale will be ignored.",
				"Remove this option if you want to stop ignoring mismatches.",
			]
			_cfg.set('backend', 'ignored mismatching system locale', gmI18N.system_locale, comment)
			_cfg.store()
			return 1

		# try setting database language (only possible if translation exists)
		cmd = "select set_curr_lang(%s) "
		for lang in [gmI18N.system_locale_level['full'], gmI18N.system_locale_level['country'], gmI18N.system_locale_level['language']]:
			if len (lang) > 0:
				# FIXME: we would need to run that on all databases we connect to ...
				result = gmPG.run_commit('default', [
					(cmd, [lang])
					])
				if result is None:
					_log.Log(gmLog.lErr, 'Cannot set database language to [%s].' % lang)
					continue
				_log.Log(gmLog.lData, "Successfully set database language to [%s]." % lang)
				return 1
		return None
#==============================================================================
def main():
	#create an instance of our GNUmed main application
	app = gmApp(0)
	#and enter the main event loop
	app.MainLoop()
#==============================================================================
# Main
#==============================================================================
if __name__ == '__main__':
	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	_log.AddTarget(aLogTarget)
	_log.Log(gmLog.lInfo, 'Starting up as main module.')
	gb = gmGuiBroker.GuiBroker()
	gb['gnumed_dir'] = os.curdir + "/.."
	main()

#==============================================================================
# $Log: gmGuiMain.py,v $
# Revision 1.211  2005-07-24 11:35:59  ncq
# - use robustified gmTimer.Start() interface
#
# Revision 1.210  2005/07/11 09:05:31  ncq
# - be more careful about failing to import wxPython
# - make contributors list accessible from main menu
#
# Revision 1.209  2005/07/02 18:21:36  ncq
# - GnuMed -> GNUmed
#
# Revision 1.208  2005/06/30 10:21:01  cfmoro
# String corrections
#
# Revision 1.207  2005/06/30 10:10:08  cfmoro
# String corrections
#
# Revision 1.206  2005/06/29 20:03:45  ncq
# - cleanup
#
# Revision 1.205  2005/06/29 18:28:33  cfmoro
# Minor fix
#
# Revision 1.204  2005/06/29 15:08:47  ncq
# - some cleanup
# - allow adding past history item from EMR menu
#
# Revision 1.203  2005/06/28 16:48:45  cfmoro
# File dialog for journal and medistar EMR export
#
# Revision 1.202  2005/06/23 15:00:11  ncq
# - cleanup
#
# Revision 1.201  2005/06/21 04:59:40  rterry
# Fix to allow running gmAbout.py under wxpython26 wxSize > wx.wxSize
#
# Revision 1.200  2005/06/19 16:38:03  ncq
# - set encoding of gmGuiMain.py to latin1
#
# Revision 1.199  2005/06/13 21:41:29  ncq
# - add missing function
#
# Revision 1.198  2005/06/12 22:16:22  ncq
# - allow for explicitely setting timezone via config file
# - cleanup, prepare for EMR search
#
# Revision 1.197  2005/06/07 20:52:49  ncq
# - improved EMR menu structure
#
# Revision 1.196  2005/05/24 19:50:26  ncq
# - make "patient" menu available globally
#
# Revision 1.195  2005/05/14 14:57:37  ncq
# - activate new patient after creation
#
# Revision 1.194  2005/05/12 15:11:08  ncq
# - add Medistar export menu item
#
# Revision 1.193  2005/04/28 21:29:58  ncq
# - improve status bar
#
# Revision 1.192  2005/04/26 20:02:20  ncq
# - proper call cNewPatientWizard
#
# Revision 1.191  2005/04/17 16:30:34  ncq
# - improve menu structure
#
# Revision 1.190  2005/04/14 08:54:48  ncq
# - comment out a display logging change that just might crash Richard
# - add missing wx. prefix
#
# Revision 1.189  2005/04/12 18:33:29  cfmoro
# typo fix
#
# Revision 1.188  2005/04/12 10:03:20  ncq
# - slightly rearrange main menu
# - add journal export function
# - move to wx.wx* use
#
# Revision 1.187  2005/04/10 17:12:09  cfmoro
# Added create patient menu option
#
# Revision 1.186  2005/04/03 20:12:12  ncq
# - better wording in status line
# - add menu "EMR" with "export" item and use gmEMRBrowser.export_emr_to_ascii()
#
# Revision 1.185  2005/04/02 20:45:12  cfmoro
# Implementated  exporting emr from gui client
#
# Revision 1.184  2005/03/29 07:27:54  ncq
# - just silly cleanup
#
# Revision 1.183  2005/03/14 14:37:19  ncq
# - attempt to log display settings
#
# Revision 1.182  2005/03/08 16:45:55  ncq
# - properly handle title
#
# Revision 1.181  2005/03/06 14:50:45  ncq
# - 'demographic record' -> get_identity()
#
# Revision 1.180  2005/02/13 15:28:07  ncq
# - v_basic_person.i_pk -> pk_identity
#
# Revision 1.179  2005/02/12 13:58:20  ncq
# - v_basic_person.i_id -> i_pk
#
# Revision 1.178  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.177  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.176  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.175  2004/10/01 13:17:35  ncq
# - eventually do what was intended on slave_mode != 1
#
# Revision 1.174  2004/10/01 11:49:59  ncq
# - improve message on unset database language
#
# Revision 1.173  2004/09/13 09:36:43  ncq
# - cleanup
# - --slave -> 'main.slave_mode'
#
# Revision 1.172  2004/09/06 22:21:08  ncq
# - properly use setDBParam()
# - store sidebar.width if not found
#
# Revision 1.171  2004/09/05 14:47:24  ncq
# - fix setDBParam() calls
#
# Revision 1.170  2004/08/20 13:34:48  ncq
# - getFirstMatchingDBSet() -> getDBParam()
#
# Revision 1.169  2004/08/11 08:15:06  ncq
# - log debugging info on why workplace appears to be list on Richard's machine
#
# Revision 1.168  2004/08/09 00:03:19  ncq
# - Horst space layout manager factored out into its own file
#
# Revision 1.167  2004/08/04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.166  2004/07/28 15:40:05  ncq
# - log wxWidgets version
#
# Revision 1.165  2004/07/24 17:21:49  ncq
# - some cleanup, also re from wxPython import wx
# - factored out Horst space layout manager into it's own
#   wxPanel child class
# - subsequently renamed
# 	'main.notebook.plugins' -> 'horstspace.notebook.pages'
# 	'modules.gui' -> 'horstspace.notebook.gui' (to be renamed horstspace.notebook.plugins later)
# - adapt to said changes
#
# Revision 1.164  2004/07/24 10:26:35  ncq
# - two missing event.Skip()s added
#
# Revision 1.163  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.162  2004/07/18 19:54:44  ncq
# - improved logging for page change/veto debugging
#
# Revision 1.161  2004/07/18 19:49:07  ncq
# - cleanup, commenting, better logging
# - preparation for inner-frame notebook layout manager arrival
# - use Python True, not wxWidgets true, as Python tells us to do
#
# Revision 1.160  2004/07/15 18:41:22  ncq
# - cautiously go back to previous notebook plugin handling
#   avoiding to remove too much of Ian's new work
# - store window size across sessions
# - try a trick for veto()ing failing notebook page changes on broken platforms
#
# Revision 1.159  2004/07/15 14:02:43  ncq
# - refactored out __set_GUI_size() from TopLevelFrame.__init__()
#   so cleanup will be easier
# - added comment on layout managers
#
# Revision 1.158  2004/07/15 07:57:20  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.157  2004/06/26 23:09:22  ncq
# - better comments
#
# Revision 1.156  2004/06/25 14:39:35  ncq
# - make right-click runtime load/drop of plugins work again
#
# Revision 1.155  2004/06/25 12:51:23  ncq
# - InstPlugin() -> instantiate_plugin()
#
# Revision 1.154  2004/06/25 12:37:20  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.153  2004/06/23 20:53:30  ncq
# - don't break the i18n epydoc fixup, if you don't understand it then ask
#
# Revision 1.152  2004/06/22 07:58:47  ihaywood
# minor bugfixes
# let gmCfg cope with config files that are not real files
#
# Revision 1.151  2004/06/21 16:06:54  ncq
# - fix epydoc i18n fix
#
# Revision 1.150  2004/06/21 14:48:26  sjtan
#
# restored some methods that gmContacts depends on, after they were booted
# out from gmDemographicRecord with no home to go , works again ;
# removed cCatFinder('occupation') instantiating in main module scope
# which was a source of complaint , as it still will lazy load anyway.
#
# Revision 1.149  2004/06/20 16:01:05  ncq
# - please epydoc more carefully
#
# Revision 1.148  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.147  2004/06/13 22:31:48  ncq
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
# Revision 1.146  2004/06/01 07:59:55  ncq
# - comments improved
#
# Revision 1.145  2004/05/15 15:51:03  sjtan
#
# hoping to link this to organization widget.
#
# Revision 1.144  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.143  2004/03/12 13:22:02  ncq
# - fix imports
#
# Revision 1.142  2004/03/04 19:46:54  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.141  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.140  2004/02/18 14:00:56  ncq
# - moved encounter handling to gmClinicalRecord.__init__()
#
# Revision 1.139  2004/02/12 23:55:34  ncq
# - different title bar on --slave
#
# Revision 1.138  2004/02/05 23:54:11  ncq
# - wxCallAfter()
# - start/stop scripting listener
#
# Revision 1.137  2004/01/29 16:12:18  ncq
# - add check for DB account to staff member mapping
#
# Revision 1.136  2004/01/18 21:52:20  ncq
# - stop backend listeners in clean_exit()
#
# Revision 1.135  2004/01/06 10:05:21  ncq
# - question dialog on continuing previous encounter was incorrect
#
# Revision 1.134  2004/01/04 09:33:32  ihaywood
# minor bugfixes, can now create new patients, but doesn't update properly
#
# Revision 1.133  2003/12/29 23:32:56  ncq
# - reverted tolerance to missing db account <-> staff member mapping
# - added comment as to why
#
# Revision 1.132  2003/12/29 20:44:16  uid67323
# -fixed the bug that made gnumed crash if no staff entry was available for the current user
#
# Revision 1.131  2003/12/29 16:56:00  uid66147
# - current user now handled by whoami
# - updateTitle() has only one parameter left: anActivity, the others can be derived
#
# Revision 1.130  2003/11/30 01:09:10  ncq
# - use gmGuiHelpers
#
# Revision 1.129  2003/11/29 01:33:23  ncq
# - a bit of streamlining
#
# Revision 1.128  2003/11/21 19:55:32  hinnef
# re-included patch from 1.116 that was lost before
#
# Revision 1.127  2003/11/19 14:45:32  ncq
# - re-decrease excess logging on plugin load failure which
#   got dropped in Syans recent commit
#
# Revision 1.126  2003/11/19 01:22:24  ncq
# - some cleanup, some local vars renamed
#
# Revision 1.125  2003/11/19 01:01:17  shilbert
# - fix for new demographic API got lost
#
# Revision 1.124  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.123  2003/11/11 18:22:18  ncq
# - fix longstanding bug in plugin loader error handler (duh !)
#
# Revision 1.122  2003/11/09 17:37:12  shilbert
# - ['demographics'] -> ['demographic record']
#
# Revision 1.121  2003/10/31 23:23:17  ncq
# - make "attach to encounter ?" dialog more informative
#
# Revision 1.120  2003/10/27 15:53:10  ncq
# - getDOB has changed
#
# Revision 1.119  2003/10/26 17:39:00  ncq
# - cleanup
#
# Revision 1.118  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# syncing with main tree.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.116  2003/10/22 21:34:42  hinnef
# -changed string array for main.window.size into two separate integer parameters
#
# Revision 1.115  2003/10/19 12:17:16  ncq
# - just cleanup
#
# Revision 1.114  2003/10/13 21:00:29  hinnef
# -added main.window.size config parameter (will be set on startup)
#
# Revision 1.113  2003/09/03 17:32:41  hinnef
# make use of gmWhoAmI
#
# Revision 1.112  2003/07/21 21:05:56  ncq
# - actually set database client encoding from config file, warn if missing
#
# Revision 1.111  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.110  2003/06/26 22:28:50  ncq
# - need to define self.nb before using it
# - reordered __init__ for clarity
#
# Revision 1.109  2003/06/26 21:38:28  ncq
# - fatal->verbose
# - ignore system-to-database locale mismatch if user so desires
#
# Revision 1.108  2003/06/25 22:50:30  ncq
# - large cleanup
# - lots of comments re method call order on application closing
# - send application_closing() from _clean_exit()
# - add OnExit() handler, catch/log session management events
# - add helper __show_question()
#
# Revision 1.107  2003/06/24 12:55:40  ncq
# - typo: it's qUestion, not qestion
#
# Revision 1.106  2003/06/23 22:29:59  ncq
# - in on_patient_selected() add code to attach to a
#   previous encounter or create one if necessary
# - show_error/quesion() helper
#
# Revision 1.105  2003/06/19 15:27:53  ncq
# - also process EVT_NOTEBOOK_PAGE_CHANGING
#   - veto() page change if can_receive_focus() is false
#
# Revision 1.104  2003/06/17 22:30:41  ncq
# - some cleanup
#
# Revision 1.103  2003/06/10 09:55:34  ncq
# - don't import handler_loader anymore
#
# Revision 1.102  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.101  2003/06/01 12:36:40  ncq
# - no way cluttering INFO level log files with arbitrary patient data
#
# Revision 1.100  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.99  2003/05/12 09:13:31  ncq
# - SQL ends with ";", cleanup
#
# Revision 1.98  2003/05/10 18:47:08  hinnef
# - set 'currentUser' in GuiBroker-dict
#
# Revision 1.97  2003/05/03 14:16:33  ncq
# - we don't use OnIdle(), so don't hook it
#
# Revision 1.96  2003/04/28 12:04:09  ncq
# - use plugin.internal_name()
#
# Revision 1.95  2003/04/25 13:03:07  ncq
# - just some silly whitespace fix
#
# Revision 1.94  2003/04/08 21:24:14  ncq
# - renamed gmGP_Toolbar -> gmTopPanel
#
# Revision 1.93  2003/04/04 20:43:47  ncq
# - take advantage of gmCurrentPatient()
#
# Revision 1.92  2003/04/03 13:50:21  ncq
# - catch more early results of connection failures ...
#
# Revision 1.91  2003/04/01 15:55:24  ncq
# - fix setting of db lang, better message if no lang set yet
#
# Revision 1.90  2003/04/01 12:26:04  ncq
# - add menu "Reference"
#
# Revision 1.89  2003/03/30 00:24:00  ncq
# - typos
# - (hopefully) less confusing printk()s at startup
#
# Revision 1.88  2003/03/29 14:12:35  ncq
# - set minimum size to 320x240
#
# Revision 1.87  2003/03/29 13:48:42  ncq
# - cleanup, clarify, improve sizer use
#
# Revision 1.86  2003/03/24 17:15:05  ncq
# - slightly speed up startup by using pre-calculated system_locale_level dict
#
# Revision 1.85  2003/03/23 11:46:14  ncq
# - remove extra debugging statements
#
# Revision 1.84  2003/02/17 16:20:38  ncq
# - streamline imports
# - comment out app_init signal dispatch since it breaks
#
# Revision 1.83  2003/02/14 00:05:36  sjtan
#
# generated files more usable.
#
# Revision 1.82  2003/02/13 08:21:18  ihaywood
# bugfix for MSW
#
# Revision 1.81  2003/02/12 23:45:49  sjtan
#
# removing dead code.
#
# Revision 1.80  2003/02/12 23:37:58  sjtan
#
# now using gmDispatcher and gmSignals for initialization and cleanup.
# Comment out the import handler_loader in gmGuiMain will restore back
# to prototype GUI stage.
#
# Revision 1.79  2003/02/11 12:21:19  sjtan
#
# one more dependency formed , at closing , to implement saving of persistence objects.
# this should be temporary, if a periodic save mechanism is implemented
#
# Revision 1.78  2003/02/09 20:02:55  ncq
# - rename main.notebook.numbers to main.notebook.plugins
#
# Revision 1.77  2003/02/09 12:44:43  ncq
# - fixed my typo
#
# Revision 1.76  2003/02/09 09:47:38  sjtan
#
# handler loading placed here.
#
# Revision 1.75  2003/02/09 09:05:30  michaelb
# renamed 'icon_gui_main' to 'icon_serpent', added icon to loading-plugins-progress-dialog box
#
# Revision 1.74  2003/02/07 22:57:59  ncq
# - fixed extra (% cmd)
#
# Revision 1.73  2003/02/07 14:30:33  ncq
# - setting the db language now works
#
# Revision 1.72  2003/02/07 08:57:39  ncq
# - fixed type
#
# Revision 1.71  2003/02/07 08:37:13  ncq
# - fixed some fallout from SJT's work
# - don't die if select lang from i18n_curr_lang returns None
#
# Revision 1.70  2003/02/07 05:13:59  sjtan
#
# took out the myLog temporary so not broken when I'm running to see if hooks work.
#
# Revision 1.69  2003/02/06 14:02:47  ncq
# - some more logging to catch the set_db_lang problem
#
# Revision 1.68  2003/02/06 12:44:06  ncq
# - curr_locale -> system_locale
#
# Revision 1.67  2003/02/05 12:15:01  ncq
# - not auto-sets the database level language if so desired and possible
#
# Revision 1.66  2003/02/02 09:11:19  ihaywood
# gmDemographics will connect, search and emit patient_selected
#
# Revision 1.65  2003/02/01 21:59:42  michaelb
# moved 'About GnuMed' into module; gmGuiMain version no longer displayed in about box
#
# Revision 1.64  2003/02/01 11:57:56  ncq
# - display gmGuiMain version in About box
#
# Revision 1.63  2003/02/01 07:10:50  michaelb
# fixed scrolling problem
#
# Revision 1.61  2003/01/29 04:26:37  michaelb
# removed import images_gnuMedGP_TabbedLists.py
#
# Revision 1.60  2003/01/14 19:36:04  ncq
# - frame.Maximize() works on Windows ONLY
#
# Revision 1.59  2003/01/14 09:10:19  ncq
# - maybe icons work better now ?
#
# Revision 1.58  2003/01/13 06:30:16  michaelb
# the serpent window-icon was added
#
# Revision 1.57  2003/01/12 17:31:10  ncq
# - catch failing plugins better
#
# Revision 1.56  2003/01/12 01:46:57  ncq
# - coding style cleanup
#
# Revision 1.55  2003/01/11 22:03:30  hinnef
# removed gmConf
#
# Revision 1.54  2003/01/05 10:03:30  ncq
# - code cleanup
# - use new plugin config storage infrastructure
#
# Revision 1.53  2003/01/04 07:43:55  ihaywood
# Popup menus on notebook tabs
#
# Revision 1.52  2002/12/26 15:50:39  ncq
# - title bar fine-tuning
#
# Revision 1.51  2002/11/30 11:09:55  ncq
# - refined title bar
# - comments
#
# Revision 1.50  2002/11/13 10:07:25  ncq
# - export updateTitle() via guibroker
# - internally set title according to template
#
# Revision 1.49  2002/11/12 21:24:51  hherb
# started to use dispatcher signals
#
# Revision 1.48  2002/11/09 18:14:38  hherb
# Errors / delay caused by loading plugin progess bar fixed
#
# Revision 1.47  2002/09/30 10:57:56  ncq
# - make GnuMed consistent spelling in user-visible strings
#
# Revision 1.46  2002/09/26 13:24:15  ncq
# - log version
#
# Revision 1.45  2002/09/12 23:21:38  ncq
# - fix progress bar
#
# Revision 1.44  2002/09/10 12:25:33  ncq
# - gimmicks rule :-)
# - display plugin_nr/nr_of_plugins on load in progress bar
#
# Revision 1.43  2002/09/10 10:26:03  ncq
# - properly i18n() strings
#
# Revision 1.42  2002/09/10 09:08:49  ncq
# - set a useful window title and add a comment regarding this item
#
# Revision 1.41  2002/09/09 10:07:48  ncq
# - long initial string so module names fit into progress bar display
#
# Revision 1.40  2002/09/09 00:52:55  ncq
# - show progress bar on plugin load :-)
#
# Revision 1.39  2002/09/08 23:17:37  ncq
# - removed obsolete reference to gmLogFrame.py
#
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
