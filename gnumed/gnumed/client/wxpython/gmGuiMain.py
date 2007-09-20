# -*- coding: utf8 -*-
"""GNUmed GUI client.

This contains the GUI application framework and main window
of the all signing all dancing GNUmed Python Reference
client. It relies on the <gnumed.py> launcher having set up
the non-GUI-related runtime environment.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.

copyright: authors
"""
#==============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmGuiMain.py,v $
# $Id: gmGuiMain.py,v 1.355 2007-09-20 19:35:14 ncq Exp $
__version__ = "$Revision: 1.355 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import sys, time, os, cPickle, zlib, locale, os.path, datetime as pyDT, webbrowser, shutil


# 3rd party libs
if not hasattr(sys, 'frozen'):		# do not check inside py2exe and friends
	import wxversion
	wxversion.ensureMinimal('2.6-unicode', optionsRequired=True)

try:
	import wx
except ImportError:
	print "GNUmed startup: Cannot import wxPython library."
	print "GNUmed startup: Make sure wxPython is installed."
	print 'CRITICAL ERROR: Error importing wxPython. Halted.'
	raise

# do this check just in case, so we can make sure
# py2exe and friends include the proper version, too
#version = '%s.%s' % (wx.MAJOR_VERSION, wx.MINOR_VERSION)
#if (version =< '2.6') or ('unicode' not in wx.PlatformInfo):
if (wx.MAJOR_VERSION < 2) or (wx.MINOR_VERSION < 6) or ('unicode' not in wx.PlatformInfo):
	print "GNUmed startup: Unsupported wxPython version (%s: %s)." % (wx.VERSION_STRING, wx.PlatformInfo)
	print "GNUmed startup: wxPython 2.6+ with unicode support is required."
	print 'CRITICAL ERROR: Proper wxPython version not found. Halted.'
	raise ValueError('wxPython 2.6+ with unicode support not found')


# GNUmed libs
from Gnumed.pycommon import gmLog, gmCfg, gmPG2, gmDispatcher, gmSignals, gmCLI, gmGuiBroker, gmI18N, gmExceptions, gmShellAPI, gmTools, gmDateTime, gmHooks
from Gnumed.wxpython import gmGuiHelpers, gmHorstSpace, gmEMRBrowser, gmDemographicsWidgets, gmEMRStructWidgets, gmStaffWidgets, gmMedDocWidgets, gmPatSearchWidgets, gmAllergyWidgets, gmListWidgets, gmFormWidgets
from Gnumed.business import gmPerson, gmClinicalRecord
from Gnumed.exporters import gmPatientExporter

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

_cfg = gmCfg.gmDefCfgFile
_provider = None
email_logger = None
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_log.Log(gmLog.lInfo, 'wxPython GUI framework: %s %s' % (wx.VERSION_STRING, wx.PlatformInfo))


# set up database connection timezone
timezone = _cfg.get('backend', 'client timezone')
if timezone is not None:
	gmPG2.set_default_client_timezone(timezone)

expected_db_ver = u'devel'

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
# FIXME: this belongs elsewhere
def jump_to_ifap(import_drugs=False):

	dbcfg = gmCfg.cCfgSQL()

	if import_drugs:
		transfer_file = os.path.expanduser(dbcfg.get2 (
			option = 'external.ifap-win.transfer_file',
			workplace = _provider.workplace,
			bias = 'workplace',
			default = '~/.wine/drive_c/Ifapwin/ifap2gnumed.csv'
		))
		# file must exist for Ifap to write into it
		f = open(transfer_file, 'w+b')
		f.close()

	# FIXME: make this more generic so several commands are tried
	# FIXME: (windows, linux, mac) until one succeeds or all fail
	ifap_cmd = dbcfg.get2 (
		option = 'external.ifap-win.shell_command',
		workplace = _provider.workplace,
		bias = 'workplace',
		default = 'wine "C:\Ifapwin\WIAMDB.EXE"'
	)

	wx.BeginBusyCursor()
	gmShellAPI.run_command_in_shell(command = ifap_cmd, blocking = import_drugs)
	wx.EndBusyCursor()

	if import_drugs:
		# COMMENT: this file must exist PRIOR to invoking IFAP
		# COMMENT: or else IFAP will not write data into it ...
		try:
			csv_file = open(transfer_file, 'rb')						# FIXME: encoding
		except:
			_log.LogException('cannot access [%s]' % fname)
			csv_file = None

		if csv_file is not None:
			import csv
			csv_lines = csv.DictReader (
				csv_file,
				fieldnames = u'PZN Handelsname Form Abpackungsmenge Einheit Preis1 Hersteller Preis2 rezeptpflichtig Festbetrag Packungszahl Packungsgröße'.split(),
				delimiter = ';'
			)
			pat = gmPerson.gmCurrentPatient()
			emr = pat.get_emr()
			# dummy episode for now
			epi = emr.add_episode(episode_name = _('Current medication'))
			for line in csv_lines:
				narr = u'%sx %s %s %s (\u2258 %s %s) von %s (%s)' % (
					line['Packungszahl'].strip(),
					line['Handelsname'].strip(),
					line['Form'].strip(),
					line[u'Packungsgröße'].strip(),
					line['Abpackungsmenge'].strip(),
					line['Einheit'].strip(),
					line['Hersteller'].strip(),
					line['PZN'].strip()
				)
				emr.add_clin_narrative(note = narr, soap_cat = 's', episode = epi)
			csv_file.close()

	return True

#==============================================================================
class gmTopLevelFrame(wx.Frame):
	"""GNUmed client's main windows frame.

	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""

	#----------------------------------------------
	def __init__(self, parent, id, title, size=wx.DefaultSize, layout=None):
		"""You'll have to browse the source to understand what the constructor does
		"""
		wx.Frame.__init__(
			self,
			parent,
			id,
			title,
			size,
			style = wx.DEFAULT_FRAME_STYLE
		)

		#initialize the gui broker
		self.__gb = gmGuiBroker.GuiBroker()
		self.__gb['main.frame'] = self
		self.bar_width = -1
		_log.Log(gmLog.lData, 'workplace is >>>%s<<<' % _provider.workplace)
		self.__setup_main_menu()
		self.SetupStatusBar()
		self.SetStatusText(_('You are logged in as %s%s.%s (%s). DB account <%s>.') % (
			gmTools.coalesce(_provider['title'], ''),
			_provider['firstnames'][:1],
			_provider['lastnames'],
			_provider['short_alias'],
			_provider['db_user']
		))

		# set window title via template
		if self.__gb['main.slave_mode']:
			self.__title_template = _('Enslaved GNUmed [%s%s.%s@%s] %s')
		else:
			self.__title_template = 'GNUmed [%s%s.%s@%s] %s'

		self.LayoutMgr = gmHorstSpace.cHorstSpaceLayoutMgr(self, -1)

		# set window icon
		icon_bmp_data = wx.BitmapFromXPMData(cPickle.loads(zlib.decompress(icon_serpent)))
		icon = wx.EmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)

		self.acctbl = []
		self.__gb['main.accelerators'] = self.acctbl
		self.__register_events()
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.LayoutMgr, 10, wx.EXPAND | wx.ALL, 1)

		self.SetAutoLayout(True)
		self.SetSizerAndFit(self.vbox)

		# don't allow the window to get too small
		# setsizehints only allows minimum size, therefore window can't become small enough
		# effectively we need the font size to be configurable according to screen size
		#self.vbox.SetSizeHints(self)
		self.__set_GUI_size()

		self.Centre(wx.BOTH)
		self.Show(True)
	#----------------------------------------------
	def __set_GUI_size(self):
		"""Try to get previous window size from backend."""

		cfg = gmCfg.cCfgSQL()

		# width
		width = int(cfg.get2 (
			option = 'main.window.width',
			workplace = _provider.workplace,
			bias = 'workplace',
			default = 800
		))

		# height
		height = int(cfg.get2 (
			option = 'main.window.height',
			workplace = _provider.workplace,
			bias = 'workplace',
			default = 600
		))

		_log.Log(gmLog.lData, 'setting GUI size to [%s:%s]' % (width, height))
 		self.SetClientSize(wx.Size(width, height))
	#----------------------------------------------
	def __setup_accelerators(self):
		self.acctbl.append ((wx.ACCEL_ALT | wx.ACCEL_CTRL, ord('X'), wx.ID_EXIT))
		self.acctbl.append ((wx.ACCEL_CTRL, ord('H'), wx.ID_HELP))
		self.SetAcceleratorTable(wx.AcceleratorTable(self.acctbl))
	#----------------------------------------------
	def __setup_main_menu(self):
		"""Create the main menu entries.

		Individual entries are farmed out to the modules.
		"""
		# create main menu
		self.mainmenu = wx.MenuBar()
		self.__gb['main.mainmenu'] = self.mainmenu

		# menu "GNUmed"
		menu_gnumed = wx.Menu()

		menu_debugging = wx.Menu()
		menu_gnumed.AppendMenu(wx.NewId(), _('Debugging ...'), menu_debugging)

		ID_SCREENSHOT = wx.NewId()
		menu_debugging.Append(ID_SCREENSHOT, _('Screenshot'), _('Save a screenshot of this GNUmed client.'))
		wx.EVT_MENU(self, ID_SCREENSHOT, self.__on_save_screenshot)

		ID = wx.NewId()
		menu_debugging.Append(ID, _('Backup log file'), _('Backup the content of the log to another file.'))
		wx.EVT_MENU(self, ID, self.__on_backup_log_file)

		ID = wx.NewId()
		menu_debugging.Append(ID, _('Bug tracker'), _('Go to the GNUmed bug tracker on the web.'))
		wx.EVT_MENU(self, ID, self.__on_display_bugtracker)

		ID_UNBLOCK = wx.NewId()
		menu_debugging.Append(ID_UNBLOCK, _('Unlock mouse'), _('Unlock mouse pointer in case it got stuck in hourglass mode.'))
		wx.EVT_MENU(self, ID_UNBLOCK, self.__on_unblock_cursor)

		if gmCLI.has_arg('--debug'):

			ID_TOGGLE_PAT_LOCK = wx.NewId()
			menu_debugging.Append(ID_TOGGLE_PAT_LOCK, _('Lock/unlock patient'), _('Lock/unlock patient - USE ONLY IF YOU KNOW WHAT YOU ARE DOING !'))
			wx.EVT_MENU(self, ID_TOGGLE_PAT_LOCK, self.__on_toggle_patient_lock)

			ID_TEST_EXCEPTION = wx.NewId()
			menu_debugging.Append(ID_TEST_EXCEPTION, _('Test error handling'), _('Throw an exception to test error handling.'))
			wx.EVT_MENU(self, ID_TEST_EXCEPTION, self.__on_test_exception)

		menu_config = wx.Menu()
		menu_gnumed.AppendMenu(wx.NewId(), _('Options ...'), menu_config)

		ID = wx.NewId()
		menu_config.Append(ID, _('Database language'), _('Configure the database language.'))
		wx.EVT_MENU(self, ID, self.__on_set_db_lang)

#		ID = wx.NewId()
#		menu_config.Append(ID, _('Workplace plugins'), _('Choose the plugins to load in the current workplace.'))
#		wx.EVT_MENU(self, ID, self.__on_configure_workplace)

		menu_gnumed.AppendSeparator()

		menu_gnumed.Append(wx.ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUmed client'))
		wx.EVT_MENU(self, wx.ID_EXIT, self.__on_exit_gnumed)

		self.mainmenu.Append(menu_gnumed, '&GNUmed')

		# -- menu "Office" --------------------
		self.menu_office = wx.Menu()

		# FIXME: regroup into sub-menus

		ID_ADD_NEW_STAFF = wx.NewId()
		self.menu_office.Append(ID_ADD_NEW_STAFF, _('Add staff member'), _('Add a new staff member'))
		wx.EVT_MENU(self, ID_ADD_NEW_STAFF, self.__on_add_new_staff)

		ID_DEL_STAFF = wx.NewId()
		self.menu_office.Append(ID_DEL_STAFF, _('Edit staff list'), _('Edit the list of staff'))
		wx.EVT_MENU(self, ID_DEL_STAFF, self.__on_edit_staff_list)

		# - draw a line
		self.menu_office.AppendSeparator()

		ID_EDIT_DOC_TYPES = wx.NewId()
		self.menu_office.Append(ID_EDIT_DOC_TYPES, _('Edit document types'), _('Edit the list of document types available in the system.'))
		wx.EVT_MENU(self, ID_EDIT_DOC_TYPES, self.__on_edit_doc_types)

		self.__gb['main.officemenu'] = self.menu_office
		self.mainmenu.Append(self.menu_office, _('&Office'))

		# -- menu "Patient" ---------------------------
		menu_patient = wx.Menu()

		ID_LOAD_EXT_PAT = wx.NewId()
		menu_patient.Append(ID_LOAD_EXT_PAT, _('Load external patient'), _('Load patient from an external source.'))
		wx.EVT_MENU(self, ID_LOAD_EXT_PAT, self.__on_load_external_patient)

		# FIXME: temporary until external program framework is active
		ID = wx.NewId()
		menu_patient.Append(ID, _('GDT export'), _('Export demographics of current patient into GDT file.'))
		wx.EVT_MENU(self, ID, self.__on_export_as_gdt)

		ID_CREATE_PATIENT = wx.NewId()
		menu_patient.Append(ID_CREATE_PATIENT, _('Register new patient'), _("Register a new patient with this practice"))
		wx.EVT_MENU(self, ID_CREATE_PATIENT, self.__on_create_patient)

		ID_DEL_PAT = wx.NewId()
		menu_patient.Append(ID_DEL_PAT, _('Inactivate patient'), _('Deactivate patient in database.'))
		wx.EVT_MENU(self, ID_DEL_PAT, self.__on_delete_patient)

		ID_ENLIST_PATIENT_AS_STAFF = wx.NewId()
		menu_patient.Append(ID_ENLIST_PATIENT_AS_STAFF, _('Enlist as staff'), _('Enlist current patient as staff member'))
		wx.EVT_MENU(self, ID_ENLIST_PATIENT_AS_STAFF, self.__on_enlist_patient_as_staff)

		self.mainmenu.Append(menu_patient, '&Patient')
		self.__gb['main.patientmenu'] = menu_patient

		# -- menu "EMR" ---------------------------
		menu_emr = wx.Menu()
		self.mainmenu.Append(menu_emr, _("&EMR"))
		self.__gb['main.emrmenu'] = menu_emr
		# - submenu "export as"
		menu_emr_export = wx.Menu()
		menu_emr.AppendMenu(wx.NewId(), _('Export as ...'), menu_emr_export)
		#   1) ASCII
		ID_EXPORT_EMR_ASCII = wx.NewId()
		menu_emr_export.Append (
			ID_EXPORT_EMR_ASCII,
			_('Text document'),
			_("Export the EMR of the active patient into a text file")
		)
		wx.EVT_MENU(self, ID_EXPORT_EMR_ASCII, self.OnExportEMR)
		#   2) journal format
		ID_EXPORT_EMR_JOURNAL = wx.NewId()
		menu_emr_export.Append (
			ID_EXPORT_EMR_JOURNAL,
			_('Journal'),
			_("Export the EMR of the active patient as a chronological journal into a text file")
		)
		wx.EVT_MENU(self, ID_EXPORT_EMR_JOURNAL, self.__on_export_emr_as_journal)
		#   3) Medistar import format
		ID_EXPORT_MEDISTAR = wx.NewId()
		menu_emr_export.Append (
			ID_EXPORT_MEDISTAR,
			_('MEDISTAR import format'),
			_("GNUmed -> MEDISTAR. Export progress notes of active patient's active encounter into a text file.")
		)
		wx.EVT_MENU(self, ID_EXPORT_MEDISTAR, self.__on_export_for_medistar)
		# - summary
		ID_EMR_SUMMARY = wx.NewId()
		menu_emr.Append (
			ID_EMR_SUMMARY,
			_('Show Summary'),
			_('Show a summary of the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_EMR_SUMMARY, self.__on_show_emr_summary)
		# - submenu "show as"
		menu_emr_show = wx.Menu()
		menu_emr.AppendMenu(wx.NewId(), _('Show as ...'), menu_emr_show)
		self.__gb['main.emr_showmenu'] = menu_emr_show
		# - draw a line
		menu_emr.AppendSeparator()
		# - search
		ID_SEARCH_EMR = wx.NewId()
		menu_emr.Append (
			ID_SEARCH_EMR,
			_('Search'),
			_('Search for data in the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_SEARCH_EMR, self.__on_search_emr)
		# - start new encounter
		ID = wx.NewId()
		menu_emr.Append (
			ID,
			_('Start new encounter'),
			_('Start a new encounter for the active patient right now.')
		)
		wx.EVT_MENU(self, ID, self.__on_start_new_encounter)
		# - add health issue
		ID_ADD_HEALTH_ISSUE_TO_EMR = wx.NewId()
		menu_emr.Append (
			ID_ADD_HEALTH_ISSUE_TO_EMR,
			_('Add &Past History (Foundational Issue)'),
			_('Add a Past Medical History Item (Foundational Health Issue) to the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_ADD_HEALTH_ISSUE_TO_EMR, self.__on_add_health_issue)
		# - document current medication
		ID_ADD_DRUGS_TO_EMR = wx.NewId()
		menu_emr.Append (
			ID_ADD_DRUGS_TO_EMR,
			_('Document current medication'),
			_('Select current medication from drug database and save into progress notes.')
		)
		wx.EVT_MENU(self, ID_ADD_DRUGS_TO_EMR, self.__on_add_medication)
		# - add allergy
		ID = wx.NewId()
		menu_emr.Append (
			ID,
			_('manage &allergies'),
			_('Manage documentation of allergies for the current patient.')
		)
		wx.EVT_MENU(self, ID, self.__on_manage_allergies)
		# - draw a line
		menu_emr.AppendSeparator()

		# -- menu "paperwork" ---------------------
		menu_paperwork = wx.Menu()

		# submenu "Documents"
#		menu_docs = wx.Menu()
#		item = menu_docs.Append(-1, _('&Show docs'), _('Switch to document collection'))
#		self.Bind(wx.EVT_MENU, self__on_show_docs, item)
#		item = menu_docs.Append(-1, _('&Add document'), _('Add a new document'))

		item = menu_paperwork.Append(-1, _('&Write letter'), _('Write a letter for the current patient.'))
		self.Bind(wx.EVT_MENU, self.__on_new_letter, item)

		menu_paperwork.AppendSeparator()

		item = menu_paperwork.Append(-1, _('Manage templates'), _('Manage templates for forms and letters.'))
		self.Bind(wx.EVT_MENU, self.__on_edit_templates, item)

		self.mainmenu.Append(menu_paperwork, _('&Correspondence'))

		# menu "View" ---------------------------
#		self.menu_view = wx.Menu()
#		self.__gb['main.viewmenu'] = self.menu_view
#		self.mainmenu.Append(self.menu_view, _("&View"));

		# menu "Tools"
		self.menu_tools = wx.Menu()
		self.__gb['main.toolsmenu'] = self.menu_tools
		self.mainmenu.Append(self.menu_tools, _("&Tools"))

		ID_DICOM_VIEWER = wx.NewId()
		viewer = _('no viewer installed')
		if os.access('/Applications/OsiriX.app/Contents/MacOS/OsiriX', os.X_OK):
			viewer = u'OsiriX'
		elif os.access('/usr/bin/amide', os.X_OK):
			viewer = u'AMIDE'
		elif os.access('/usr/bin/xmedcon', os.X_OK):
			viewer = u'(x)medcon'
		self.menu_tools.Append(ID_DICOM_VIEWER, _('DICOM viewer'), _('Start DICOM viewer (%s) for CD-ROM (X-Ray, CT, MR, etc). On Windows just insert CD.') % viewer)
		wx.EVT_MENU(self, ID_DICOM_VIEWER, self.__on_dicom_viewer)
		if viewer == _('no viewer installed'):
			_log.Log(gmLog.lInfo, 'neither OsiriX nor AMIDE nor xmedcon found, disabling "DICOM viewer" menu item')
			self.menu_tools.Enable(id=ID_DICOM_VIEWER, enable=False)

#		ID_DERMTOOL = wx.NewId()
#		self.menu_tools.Append(ID_DERMTOOL, _("Dermatology"), _("A tool to aid dermatology diagnosis"))
#		wx.EVT_MENU (self, ID_DERMTOOL, self.__dermtool)

		self.menu_tools.AppendSeparator()

		# menu "Knowledge" ---------------------
		menu_knowledge = wx.Menu()
		self.__gb['main.knowledgemenu'] = menu_knowledge
		self.mainmenu.Append(menu_knowledge, _("&Knowledge"))

		# - IFAP drug DB
		ID_IFAP = wx.NewId()			# FIXME: add only if installed
		menu_knowledge.Append(ID_IFAP, _('ifap index (Win)'), _('Start "ifap index PRAXIS (Windows)" drug browser'))
		wx.EVT_MENU(self, ID_IFAP, self.__on_ifap)

#		menu_knowledge.AppendSeparator()

		# - "recommended" medical links in the Wiki
		ID_MEDICAL_LINKS = wx.NewId()
		menu_knowledge.Append(ID_MEDICAL_LINKS, _('medical links (WWW)'), _('Show a page of links to useful medical content.'))
		wx.EVT_MENU(self, ID_MEDICAL_LINKS, self.__on_medical_links)

		# menu "Help" -------------------------
		help_menu = wx.Menu()

		# - about
		help_menu.Append(wx.ID_ABOUT, _('About GNUmed'), "")
		wx.EVT_MENU (self, wx.ID_ABOUT, self.OnAbout)

		# - contributors
		ID_CONTRIBUTORS = wx.NewId()
		help_menu.Append(ID_CONTRIBUTORS, _('GNUmed contributors'), _('show GNUmed contributors'))
		wx.EVT_MENU(self, ID_CONTRIBUTORS, self.__on_show_contributors)

		# - among other things the Manual is added from a plugin
		help_menu.AppendSeparator()
		self.__gb['main.helpmenu'] = help_menu
		self.mainmenu.Append(help_menu, _("&Help"))

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
		gmDispatcher.connect(self._on_pre_patient_selection, gmSignals.pre_patient_selection())
		gmDispatcher.connect(self._on_post_patient_selection, gmSignals.post_patient_selection())

		gmDispatcher.connect(self._on_set_statustext, 'statustext')
	#-----------------------------------------------
	def _on_set_statustext(self, msg=None, loglevel=None, beep=True):

		if msg is None:
			msg = _('programmer forgot to specify status message')

		if loglevel is not None:
			_log.Log(loglevel, msg.replace('\015', ' ').replace('\012', ' '))

		if beep:
			wx.Bell()

		wx.CallAfter(self.SetStatusText, msg)

		return True
	#-----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		wx.CallAfter(self.__on_post_patient_selection, **kwargs)
	#----------------------------------------------
	def __on_post_patient_selection(self, **kwargs):
		self.updateTitle()
		try:
			gmHooks.run_hook_script(hook = u'post_patient_activation')
		except:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot run script after patient activation.'))
			raise
	#----------------------------------------------
	def _on_pre_patient_selection(self, **kwargs):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			return True
		self.__on_pre_patient_selection(**kwargs)
	#----------------------------------------------
	def __on_pre_patient_selection(self, **kwargs):

		# FIXME: we need a way to make sure the patient has not yet changed
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			return True

		# did we add anything to the EMR ?
		emr = pat.get_emr()
		enc = emr.get_active_encounter()
		if enc.has_clinical_data():

			empty_aoe = (gmTools.coalesce(enc['assessment_of_encounter'], '').strip() == '')
			zero_duration = (enc['last_affirmed'] == enc['started'])

			if empty_aoe or zero_duration:
				if empty_aoe:
					# - work out suitable default
					epis = emr.get_episodes_by_encounter()
					if len(epis) > 0:
						enc_summary = ''
						for epi in epis:
							enc_summary += '%s; ' % epi['description']
						enc['assessment_of_encounter'] = enc_summary
				if zero_duration:
					enc['last_affirmed'] = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)

				dlg = gmEMRStructWidgets.cEncounterEditAreaDlg(parent=self, encounter=enc)
				dlg.ShowModal()

		return True
	#----------------------------------------------
	# menu "paperwork"
	#----------------------------------------------
	def __on_show_docs(self, evt):
		gmDispatcher.send(signal='show_document_viewer')
	#----------------------------------------------
	def __on_new_letter(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot write letter. No active patient.'), beep = True)
			return True
		gmFormWidgets.create_new_letter(parent = self)
	#----------------------------------------------
	def __on_edit_templates(self, evt):
		gmFormWidgets.let_user_select_form_template(parent = self)
	#----------------------------------------------
	# help menu
	#----------------------------------------------
	def OnAbout(self, event):
		from Gnumed.wxpython import gmAbout
		gmAbout = gmAbout.AboutFrame(self, -1, _("About GNUmed"), size=wx.Size(350, 300), style = wx.MAXIMIZE_BOX)
		gmAbout.Centre(wx.BOTH)
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
			size = wx.Size(400,600),
			style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		)
		contribs.ShowModal()
		del contribs
		del gmAbout
	#----------------------------------------------
	# GNUmed menu
	#----------------------------------------------
	def __on_exit_gnumed(self, event):
		"""Invoked from Menu->Exit (calls ID_EXIT handler)."""
		# calls wx.EVT_CLOSE handler
		self.Close()
	#----------------------------------------------
	def __on_set_db_lang(self, event):

		rows, idx = gmPG2.run_ro_queries (
			queries = [{'cmd': u'select distinct lang from i18n.translations'}]
		)
		langs = [ row[0] for row in rows ]

		language = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'Please select the database language from the list below.\n\n'
				'This setting will not affect the language the user\n'
				'interface is displayed in.'
			),
			caption = _('configuring database language'),
			choices = langs,
			columns = [_('Language')],
			data = langs,
			single_selection = True
		)

		if language is None:
			return

		rows, idx = gmPG2.run_rw_queries (
			queries = [{'cmd': u'select i18n.set_curr_lang(%(lang)s)', 'args': {'lang': language}}]
		)
	#----------------------------------------------
#	def __on_configure_workplace(self, evt):
#		pass
	#----------------------------------------------
	def __on_unblock_cursor(self, evt):
		wx.EndBusyCursor()
	#----------------------------------------------
	def __on_toggle_patient_lock(self, evt):
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.locked:
			curr_pat.force_unlock()
		else:
			curr_pat.locked = True
	#----------------------------------------------
	def __on_backup_log_file(self, evt):
		for target in _log.get_targets():
			if isinstance(target, gmLog.cLogTargetFile):
				name = os.path.basename(target.ID)
				name, ext = os.path.splitext(name)
				new_name = '%s_%s%s' % (name, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ext)
				new_path = os.path.expanduser(os.path.join('~', 'gnumed', 'logs'))
				dlg = wx.FileDialog (
					parent = self,
					message = _("Save current log as..."),
					defaultDir = new_path,
					defaultFile = new_name,
					wildcard = "%s (*.log)|*.log" % _("log files"),
					style = wx.SAVE
				)
				choice = dlg.ShowModal()
				new_name = dlg.GetPath()
				dlg.Destroy()
				if choice != wx.ID_OK:
					return True
				_log.Log(gmLog.lWarn, 'syncing log file for backup to [%s]' % new_name)
				_log.flush()
				shutil.copy2(target.ID, new_name)
				gmDispatcher.send('statustext', msg = _('Log file backed up as [%s].') % new_name)
	#----------------------------------------------
	def __on_display_bugtracker(self, evt):
		webbrowser.open (
			url = 'http://savannah.gnu.org/bugs/?group=gnumed',
			new = False,
			autoraise = True
		)
	#----------------------------------------------
	def __on_dicom_viewer(self, evt):
		# raw check for OsiriX binary
		if os.access('/Applications/OsiriX.app/Contents/MacOS/OsiriX', os.X_OK):
			gmShellAPI.run_command_in_shell('/Applications/OsiriX.app/Contents/MacOS/OsiriX', blocking=False)
			return

		if os.access('/usr/bin/amide', os.X_OK):
			# FIXME: search for DICOMDIR and add that to AMIDE call
			gmShellAPI.run_command_in_shell('/usr/bin/amide', blocking=False)
			return

		# FIXME: 1) search for autorun.inf and run application with wine ([autorun] OPEN=...)
		# FIXME: 2) search for filetype DICOM and show list and call xmedcon on each
		# FIXME: scan CD for *.dcm files, put them into list and
		# FIXME: let user call viewer for each
		# FIXME: parse DICOMDIR file
		gmShellAPI.run_command_in_shell('xmedcon', blocking=False)
	#----------------------------------------------
	#----------------------------------------------
	def __on_medical_links(self, evt):
		webbrowser.open (
			url = 'http://wiki.gnumed.de/bin/view/Gnumed/MedicalContentLinks#AnchorLocaleI%s' % gmI18N.system_locale_level['language'],
			new = False,
			autoraise = True
		)
	#----------------------------------------------
	def __on_ifap(self, evt):
		jump_to_ifap()
	#----------------------------------------------
	#----------------------------------------------
	def __on_save_screenshot(self, evt):
		w, h = self.GetSize()
		wdc = wx.WindowDC(self)
		mdc = wx.MemoryDC()
		img = wx.EmptyBitmap(w, h)
		mdc.SelectObject(img)
		mdc.Blit(0, 0, w, h, wdc, 0, 0)
		# FIXME: improve filename with patient/workplace/provider, allow user to select/change
		fname = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'gnumed-screenshot-%s.png')) % pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		img.SaveFile(fname, wx.BITMAP_TYPE_PNG)
		gmDispatcher.send(signal = 'statustext', msg = _('Saved screenshot to file [%s].') % fname)
		evt.Skip()
	#----------------------------------------------
	def __on_test_exception(self, evt):
		#import nonexistant_module
		raise ValueError('raised ValueError to test exception handling')
	#----------------------------------------------
	def OnClose(self, event):
		"""This is the wx.EVT_CLOSE handler.

		- framework still functional
		"""
		# FIXME: ask user whether to *really* close and save all data
		# call cleanup helper
		self._clean_exit()
		self.Destroy()
	#----------------------------------------------
	def OnExportEMR(self, event):
		"""
		Export selected patient EMR to a file
		"""
		gmEMRBrowser.export_emr_to_ascii(parent=self)
	#----------------------------------------------
	def __dermtool (self, event):
		import Gnumed.wxpython.gmDermTool as DT
		frame = DT.DermToolDialog(None, -1)
		frame.Show(True)
	#----------------------------------------------
	def __on_start_new_encounter(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot start new encounter. No active patient.'))
			return False
		emr = pat.get_emr()
		emr.start_new_encounter()
		gmDispatcher.send(signal = 'statustext', msg = _('Started a new encounter for the active patient.'))
	#----------------------------------------------
	def __on_add_health_issue(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add health issue. No active patient.'))
			return False
		ea = gmEMRStructWidgets.cHealthIssueEditAreaDlg(parent=self, id=-1)
		ea.ShowModal()
	#----------------------------------------------
	def __on_add_medication(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add medication. No active patient.'))
			return False

		jump_to_ifap(import_drugs = True)

		evt.Skip()
	#----------------------------------------------
	def __on_manage_allergies(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add allergy. No active patient.'))
			return False

		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_show_emr_summary(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot show EMR summary. No active patient.'))
			return False

		emr = pat.get_emr()
		msg = _("""Medical problems: %(problems)s
Total visits: %(visits)s
Total EMR entries: %(items)s
Stored documents: %(documents)s

""") % emr.get_summary()
		dlg = wx.MessageDialog (
			parent = None,
			message = msg,
			caption = _('EMR Summary'),
			style = wx.OK | wx.STAY_ON_TOP
		)
		dlg.ShowModal()
		dlg.Destroy()
		return True
	#----------------------------------------------
	def __on_search_emr(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot search EMR. No active patient.'))
			return False

		searcher = wx.TextEntryDialog (
			parent = self,
			message = _('Enter search term:'),
			caption = _('Text search of entire EMR'),
			style = wx.OK | wx.CANCEL | wx.CENTRE,
			pos = wx.DefaultPosition
		)
		result = searcher.ShowModal()
		if result == wx.ID_OK:
			val = searcher.GetValue()
			wx.BeginBusyCursor()
			emr = pat.get_emr()
			rows = emr.search_narrative_simple(val)
			wx.EndBusyCursor()
			txt = ''
			for row in rows:
				txt += '%s - %s\n%s\n\n' % (row[1], row[4], row[2])
			msg = _(
"""Search term was: "%s"

Search results:
%s
""") % (val, txt)
			dlg = wx.MessageDialog (
				parent = None,
				message = msg,
				caption = _('search results'),
				style = wx.OK | wx.STAY_ON_TOP
			)
			dlg.ShowModal()
			dlg.Destroy()
			return True
	#----------------------------------------------
	def __on_export_emr_as_journal(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR journal. No active patient.'))
			return False
		# get file name
		aWildcard = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
		# FIXME: make configurable
		aDefDir = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'EMR', pat['dirname']))
		gmTools.mkdir(aDefDir)
		# FIXME: make configurable
		fname = '%s-%s_%s.txt' % (_('emr-journal'), pat['lastnames'], pat['firstnames'])
		dlg = wx.FileDialog (
			parent = self,
			message = _("Save patient's EMR journal as..."),
			defaultDir = aDefDir,
			defaultFile = fname,
			wildcard = aWildcard,
			style = wx.SAVE
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.ID_OK:
			return True

		_log.Log(gmLog.lData, 'exporting EMR journal to [%s]' % fname)
		# instantiate exporter
		exporter = gmPatientExporter.cEMRJournalExporter()

		wx.BeginBusyCursor()
		try:
			fname = exporter.export_to_file(filename = fname)
		except:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Error exporting patient EMR as chronological journal.'),
				_('EMR journal export'),
				gmLog.lErr
			)
			raise
		wx.EndBusyCursor()

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported EMR as chronological journal into file [%s].') % fname, beep=False)

		return True
	#----------------------------------------------
	def __on_export_for_medistar(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR for Medistar. No active patient.'))
			return False
		# get file name
		aWildcard = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
		# FIXME: make configurable
		aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed','export')))
		# FIXME: make configurable
		fname = '%s-%s-%s-%s-%s.txt' % (
			'Medistar-MD',
			time.strftime('%Y-%m-%d',time.localtime()),
			pat['lastnames'].replace(' ', '-'),
			pat['firstnames'].replace(' ', '_'),
			pat['dob'].strftime('%Y-%m-%d')
		)
		dlg = wx.FileDialog (
			parent = self,
			message = _("Save patient's EMR for MEDISTAR as..."),
			defaultDir = aDefDir,
			defaultFile = fname,
			wildcard = aWildcard,
			style = wx.SAVE
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.ID_OK:
			return False

		_log.Log(gmLog.lData, 'exporting EMR journal to [%s]' % fname)
		# instantiate exporter
		exporter = gmPatientExporter.cMedistarSOAPExporter()
		wx.BeginBusyCursor()
		successful, fname = exporter.export_to_file(filename=fname)
		wx.EndBusyCursor()
		if not successful:
			gmGuiHelpers.gm_show_error (
				_('Error exporting progress notes of current encounter for MEDISTAR import.'),
				_('MEDISTAR progress notes export'),
				gmLog.lErr
			)
			return False

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported todays progress notes into file [%s] for Medistar import.') % fname, beep=False)

		return True
	#----------------------------------------------
	def __on_load_external_patient(self, event):
		gmPatSearchWidgets.load_patient_from_external_sources(parent=self)
	#----------------------------------------------
	def __on_export_as_gdt(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		# FIXME: configurable
		enc = 'cp850'
		fname = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'xDT', 'current-patient.gdt'))
		curr_pat.export_as_gdt(filename = fname, encoding = enc)
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics to GDT file [%s].') % fname)
	#----------------------------------------------
	def __on_create_patient(self, event):
		"""Launch create patient wizard.
		"""
		wiz = gmDemographicsWidgets.cNewPatientWizard(parent=self)
		wiz.RunWizard(activate=True)
	#----------------------------------------------
	def __on_enlist_patient_as_staff(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add staff member. No active patient.'))
			return False
		dlg = gmStaffWidgets.cAddPatientAsStaffDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_delete_patient(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete patient. No patient active.'))
			return False
		gmDemographicsWidgets.disable_identity(identity=pat)
		return True
	#----------------------------------------------
	def __on_add_new_staff(self, event):
		"""Create new person and add it as staff."""
		wiz = gmDemographicsWidgets.cNewPatientWizard(parent=self)
		if not wiz.RunWizard(activate=True):
			return False
		dlg = gmStaffWidgets.cAddPatientAsStaffDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_edit_staff_list(self, event):
		dlg = gmStaffWidgets.cEditStaffListDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_edit_doc_types(self, event):
		dlg = gmMedDocWidgets.cEditDocumentTypesDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def _clean_exit(self):
		"""Cleanup helper.

		- should ALWAYS be called when this program is
		  to be terminated
		- ANY code that should be executed before a
		  regular shutdown should go in here
		- framework still functional
		"""
		gmDispatcher.disconnect(self._on_set_statustext, 'statustext')
		# signal imminent demise to plugins
		gmDispatcher.send(gmSignals.application_closing())
		# remember GUI size
		curr_width, curr_height = self.GetClientSizeTuple()
		_log.Log(gmLog.lInfo, 'GUI size at shutdown: [%s:%s]' % (curr_width, curr_height))
		dbcfg = gmCfg.cCfgSQL()
		dbcfg.set (
			option = 'main.window.width',
			value = curr_width,
			workplace = _provider.workplace
		)
		dbcfg.set (
			option = 'main.window.height',
			value = curr_height,
			workplace = _provider.workplace
		)
		# handle our own stuff
		try:
			gmGuiBroker.GuiBroker()['scripting listener'].tell_thread_to_stop()
		except KeyError:
			pass
		except:
			_log.LogException('cannot stop scripting listener thread', verbose=0)
		self.timer.Stop()
#		self.mainmenu = None
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
	# internal API
	#----------------------------------------------
	def updateTitle(self):
		"""Update title of main window based on template.

		This gives nice tooltips on iconified GNUmed instances.
		User research indicates that in the title bar people want
		the date of birth, not the age, so please stick to this
		convention.
		"""
		pat = gmPerson.gmCurrentPatient()
		if pat.is_connected():
			title = pat['title']
			if title is None:
				title = ''
			else:
				title = title[:4] + '.'
			pat_str = "%s%s %s (%s) #%d" % (title, pat['firstnames'], pat['lastnames'], pat['dob'].strftime('%x').decode(gmI18N.get_encoding()), pat['pk_identity'])
		else:
			pat_str = _('no patient')

		title = self.__title_template % (
			gmTools.coalesce(_provider['title'], ''),
			_provider['firstnames'][:1],
			_provider['lastnames'],
			_provider.workplace,
			pat_str
		)
		self.SetTitle(title)
	#----------------------------------------------
	#----------------------------------------------
	def SetupStatusBar(self):
		sb = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		sb.SetStatusWidths([-1, 150])
		#add time and date display to the right corner of the status bar
		self.timer = wx.PyTimer(self._cb_update_clock)
		self._cb_update_clock()
		#update every second
		self.timer.Start(milliseconds=1000)
	#----------------------------------------------
	def _cb_update_clock(self):
		"""Displays date and local time in the second slot of the status bar"""
		t = time.localtime(time.time())
		st = time.strftime('%c', t).decode(gmI18N.get_encoding())
		self.SetStatusText(st,1)
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
		wx.LayoutAlgorithm().LayoutWindow (self.LayoutMgr, self.nb)
	#------------------------------------------------
#	def OnSashDrag (self, event):
#		if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
#			return
#		self.leftbox.SetDefaultSize(wx.Size(event.GetDragRect().width, 1000))
#		self.bar_width = event.GetDragRect().width
#		wx.LayoutAlgorithm().LayoutWindow(self.LayoutMgr, self.nb)
#		self.nb.Refresh()

#==============================================================================
class gmApp(wx.App):

	def OnInit(self):
		gmGuiHelpers.install_wx_exception_handler()

		# set this so things like "wx.StandardPaths.GetDataDir()" work as expected
		self.SetAppName(u'gnumed')
		#self.SetVendor(u'The GNUmed Development Community.')
		paths = gmTools.gmPaths(app_name = 'gnumed', wx = wx)
		paths.init_paths(wx = wx, app_name = 'gnumed')

		if gmCLI.has_arg('--conf-file'):
			candidates = [gmCLI.arg['--conf-file']]
		else:
			candidates = [
				os.path.join(paths.user_config_dir, 'gnumed.conf'),
				os.path.join(paths.local_base_dir, 'gnumed.conf')
			]
		for candidate in candidates:
			try:
				open(candidate).close()
				self.user_prefs_cfg_file = gmCfg.cCfgFile(aFile = candidate, flags = gmCfg.cfg_IGNORE_CMD_LINE)
				break
			except IOError:
				continue

		# create a GUI element dictionary that
		# will be static and alive as long as app runs
		self.__guibroker = gmGuiBroker.GuiBroker()

		self.__setup_platform()

		# check for slave mode
#		tmp = self.user_prefs_cfg_file.get('workplace', 'slave mode')
#		if tmp == "1":
#			self.__guibroker['main.slave_mode'] = True
#			_log.Log(gmLog.lInfo, 'slave mode is ON')
#		else:
#			self.__guibroker['main.slave_mode'] = False
#			_log.Log(gmLog.lInfo, 'slave mode is OFF')

		# connect to backend (implicitely runs login dialog)
		from Gnumed.wxpython import gmLogin
		if not gmLogin.connect_to_database(expected_version = expected_db_ver, require_version = not gmCLI.has_arg('--override-schema-check')):
			_log.Log(gmLog.lWarn, "Login attempt unsuccessful. Can't run GNUmed without database connection")
			return False

		if gmCLI.has_arg('--debug'):
			self.RedirectStdio()

		if self.__guibroker['main.slave_mode']:
			self.__guibroker['main.slave_personality'] = self.user_prefs_cfg_file.get('workplace', 'slave personality')
			if not self.__guibroker['main.slave_personality']:
				msg = _(
					'Slave mode requested but personality not set.\n\n'
					'(The personality must be set so that clients can\n'
					'find the appropriate GNUmed instance to attach to.)\n\n'
					'Set slave personality in config file !'
				)
				gmGuiHelpers.gm_show_error(msg, _('Starting slave mode'), gmLog.lErr)
				return False
			_log.Log(gmLog.lInfo, 'assuming slave mode personality [%s]' % self.__guibroker['main.slave_personality'])

		# check account <-> staff member association
		try:
			global _provider
			_provider = gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())
		except gmExceptions.ConstructorError, ValueError:
			account = gmPG2.get_current_user()
			_log.LogException('DB account [%s] cannot be used as a GNUmed staff login' % account, sys.exc_info(), verbose=0)
			msg = _(
				'The database account [%s] cannot be used as a\n'
				'staff member login for GNUmed. There was an\n'
				'error retrieving staff details for it.\n\n'
				'Please ask your administrator for help.\n'
			) % account
			gmGuiHelpers.gm_show_error(msg, _('Checking access permissions'))
			return False

		wx.EVT_QUERY_END_SESSION(self, self._on_query_end_session)
		wx.EVT_END_SESSION(self, self._on_end_session)

		# set up language in database
		self.__set_db_lang()

		# display database banner
		rows, idx = gmPG2.run_ro_queries(link_obj = None, queries = [{'cmd': u'select _(message) as message from cfg.db_logon_banner'}])
		if len(rows) > 0:
			msg = rows[0]['message'].strip()
			if msg != u'':
				gmGuiHelpers.gm_show_info(msg, _('Verifying database'))

		# create the main window
		cli_layout = gmCLI.arg.get('--layout', None)
		# FIXME: load last position from backend
		frame = gmTopLevelFrame(None, -1, _('GNUmed client'), (640,440), cli_layout)
		self.SetTopWindow(frame)

		frame.CentreOnScreen(wx.BOTH)
		frame.Show(True)

		# last but not least: start macro listener if so desired
		if self.__guibroker['main.slave_mode']:
			import socket
			from Gnumed.pycommon import gmScriptingListener
			from Gnumed.wxpython import gmMacro
			macro_executor = gmMacro.cMacroPrimitives(self.__guibroker['main.slave_personality'])
			port = self.user_prefs_cfg_file.get('workplace', 'xml-rpc port')
			if not port:
				port = 9999
			try:
				self.__guibroker['scripting listener'] = gmScriptingListener.cScriptingListener(port, macro_executor)
			except socket.error, e:
				_log.LogException('cannot start GNUmed XML-RPC server')
				gmGuiHelpers.gm_show_error (
					aMessage = (
						'Cannot start the GNUmed server:\n'
						'\n'
						' [%s]'
					) % e,
					aTitle = _('GNUmed startup')
				)
				return False

			_log.Log(gmLog.lInfo, 'listening for commands on port [%s]' % port)

		wx.CallAfter(self._do_after_init)

		return True
	#----------------------------------------------
	def _do_after_init(self):
		# - setup GUI callback in clinical record
		gmClinicalRecord.set_func_ask_user(a_func = gmEMRStructWidgets.ask_for_encounter_continuation)

		# - raise startup-default plugin (done in cTopLevelFrame)

		gmPatSearchWidgets.load_patient_from_external_sources(self.GetTopWindow())

		self.__guibroker['horstspace.top_panel'].patient_selector.SetFocus()

		gmHooks.run_hook_script(hook = u'startup-after-GUI-init')
	#----------------------------------------------
	def OnExit(self):
		"""Called:

		- after destroying all application windows and controls
		- before wx.Windows internal cleanup
		"""
		gmGuiHelpers.uninstall_wx_exception_handler()
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
		#do the platform dependent stuff
		if wx.Platform == '__WXMSW__':
			#windoze specific stuff here
			_log.Log(gmLog.lInfo,'running on MS Windows')
		elif wx.Platform == '__WXGTK__':
			#GTK (Linux etc.) specific stuff here
			_log.Log(gmLog.lInfo,'running on GTK (probably Linux)')
		elif wx.Platform == '__WXMAC__':
			#Mac OS specific stuff here
			_log.Log(gmLog.lInfo,'running on Mac OS')
		else:
			_log.Log(gmLog.lInfo,'running on an unknown platform (%s)' % wx.Platform)
	#----------------------------------------------
	def __set_db_lang(self):
		if gmI18N.system_locale is None or gmI18N.system_locale == '':
			_log.Log(gmLog.lWarn, "system locale is undefined (probably meaning 'C')")
			return True

		db_lang = None
		# get current database locale
		rows, idx = gmPG2.run_ro_queries(link_obj=None, queries = [{'cmd': u"select lang from i18n.curr_lang where user=CURRENT_USER"}])
		if len(rows) == 0:
			msg = _(
				"There is no language selected in the database for user [%s].\n"
				"Your system language is currently set to [%s].\n\n"
				"Do you want to set the database language to '%s' ?\n\n"
				"Answering <NO> will remember that decision until\n"
				"the system language is changed. You can also reactivate\n"
				"this inquiry by removing the appropriate ignore option\n"
				"from the configuration file."
			)  % (_provider['db_user'], gmI18N.system_locale, gmI18N.system_locale)
			_log.Log(gmLog.lData, "database locale currently not set")
		else:
			db_lang = rows[0]['lang']
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
				return True
			if db_lang == gmI18N.system_locale_level['country']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at country level.' % (db_lang, gmI18N.system_locale))
				return True
			if db_lang == gmI18N.system_locale_level['language']:
				_log.Log(gmLog.lData, 'Database locale (%s) matches system locale (%s) at language level.' % (db_lang, gmI18N.system_locale))
				return True
			# no match
			_log.Log(gmLog.lWarn, 'database locale [%s] does not match system locale [%s]' % (db_lang, gmI18N.system_locale))

		# returns either None or a locale string
		ignored_sys_lang = self.user_prefs_cfg_file.get('backend', 'ignored mismatching system locale')
		# are we to ignore *this* mismatch ?
		if gmI18N.system_locale == ignored_sys_lang:
			_log.Log(gmLog.lInfo, 'configured to ignore system-to-database locale mismatch')
			return True
		# no, so ask user
		if not gmGuiHelpers.gm_show_question (
			aMessage = msg,
			aTitle = _('checking database language settings'),
		):
			_log.Log(gmLog.lInfo, 'User did not want to set database locale. Ignoring mismatch next time.')
			comment = [
				"If the system locale matches this value a mismatch",
				"with the database locale will be ignored.",
				"Remove this option if you want to stop ignoring mismatches.",
			]
			self.user_prefs_cfg_file.set('backend', 'ignored mismatching system locale', gmI18N.system_locale, comment)
			self.user_prefs_cfg_file.store()
			return True

		# try setting database language (only possible if translation exists)
		for lang in [gmI18N.system_locale_level['full'], gmI18N.system_locale_level['country'], gmI18N.system_locale_level['language']]:
			if len(lang) > 0:
				# users are getting confused, so don't show these "errors",
				# they really are just notices about us being nice
				rows, idx = gmPG2.run_rw_queries (
					link_obj = None,
					queries = [{'cmd': u'select i18n.set_curr_lang(%s)', 'args': [lang]}],
					return_data = True
				)
				if rows[0][0]:
					_log.Log(gmLog.lData, "Successfully set database language to [%s]." % lang)
				else:
					_log.Log(gmLog.lErr, 'Cannot set database language to [%s].' % lang)
					continue
				return True

		# user wanted to set the DB language but that failed
		# so try falling back to Englisch
		set_default = gmGuiHelpers.gm_show_question (
			_(
				'Failed to set database language to [%s].\n\n'
				'No translation available.\n\n'
				'Do you want to set the database language to English ?'
			) % gmI18N.system_locale,
			_('setting database language')
		)
		if set_default:
			gmPG2.run_rw_queries(link_obj=None, queries=[{'cmd': u'select i18n.force_curr_lang(%s)', 'args': [u'en_GB']}])

		return False
#==============================================================================
def main():
	wx.Image_AddHandler(wx.PNGHandler())
	wx.Image_AddHandler(wx.JPEGHandler())
	wx.Image_AddHandler(wx.GIFHandler())
	# create an instance of our GNUmed main application
	# - do not redirect stdio (yet)
	# - allow signals to be delivered
	app = gmApp(redirect = False, clearSigInt = False)
	_log.Log(gmLog.lInfo, 'display: %s:%s' % (wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X), wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)))
	# and enter the main event loop
	app.MainLoop()
#==============================================================================
# Main
#==============================================================================
if __name__ == '__main__':

	from GNUmed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	_log.AddTarget(aLogTarget)
	_log.Log(gmLog.lInfo, 'Starting up as main module.')
	main()

#==============================================================================
# $Log: gmGuiMain.py,v $
# Revision 1.355  2007-09-20 19:35:14  ncq
# - somewhat cleanup exit code
#
# Revision 1.354  2007/09/17 21:46:51  ncq
# - comment out unimplemented menu item
#
# Revision 1.353  2007/09/10 12:35:32  ncq
# - cleanup
#
# Revision 1.352  2007/09/04 23:29:03  ncq
# - slave mode now set via --slave inside login dialog
#
# Revision 1.351  2007/09/03 11:03:59  ncq
# - enhanced error handling testing
#
# Revision 1.350  2007/08/31 23:04:40  ncq
# - feedback on failing to write letter w/o active patient
#
# Revision 1.349  2007/08/29 14:40:41  ncq
# - remove "activity" part from window title - we never started using it
# - add menu item for managing paperwork templates
# - no more singular get_choice_from_list()
# - feedback on starting new encounter
#
# Revision 1.348  2007/08/12 00:09:07  ncq
# - no more gmSignals.py
#
# Revision 1.347  2007/08/07 21:42:40  ncq
# - cPaths -> gmPaths
#
# Revision 1.346  2007/07/22 10:47:48  ncq
# - fix typo
#
# Revision 1.345  2007/07/22 10:04:49  ncq
# - only allow new letter from menu if patient active
#
# Revision 1.344  2007/07/22 09:25:59  ncq
# - support AMIDE DICOM viewer if installed
# - menu "correspondence" with item "write letter"
# - adjust to new get_choice_from_list()
#
# Revision 1.343  2007/07/17 21:43:50  ncq
# - use refcounted patient lock
#
# Revision 1.342  2007/07/17 15:52:57  ncq
# - display proper error message when starting the XML RPC server fails
#
# Revision 1.341  2007/07/17 13:52:12  ncq
# - fix SQL query for db welcome message
#
# Revision 1.340  2007/07/17 13:42:13  ncq
# - make displaying welcome message optional
#
# Revision 1.339  2007/07/11 21:09:05  ncq
# - add lock/unlock patient
#
# Revision 1.338  2007/07/09 12:44:06  ncq
# - make office menu accessible to plugins
#
# Revision 1.337  2007/06/28 12:37:22  ncq
# - show proper title in caption line of main window
# - improved menus
# - allow signals to be delivered
#
# Revision 1.336  2007/06/11 20:30:46  ncq
# - set expected database version to "devel"
#
# Revision 1.335  2007/06/10 10:18:37  ncq
# - fix setting database language
#
# Revision 1.334  2007/05/21 14:48:58  ncq
# - use export/EMR/pat['dirname']
#
# Revision 1.333  2007/05/21 13:05:25  ncq
# - catch-all wildcard on UNIX must be *, not *.*
#
# Revision 1.332  2007/05/18 10:14:50  ncq
# - revert testing
#
# Revision 1.331  2007/05/18 10:14:22  ncq
# - support OsiriX dicom viewer if available
# - only enable dicom viewer menu item if a (known) viewer is available
#   (does not affect viewing from document system)
#
# Revision 1.330  2007/05/11 14:18:04  ncq
# - put debugging stuff into submenue
#
# Revision 1.329  2007/05/08 16:06:03  ncq
# - cleanup menu layout
# - link to bug tracker on Savannah
# - add exception handler test
# - install/uninstall wxPython based exception display handler at appropriate times
#
# Revision 1.328  2007/05/08 11:15:41  ncq
# - redirect stdio when debugging is enabled
#
# Revision 1.327  2007/05/07 12:35:20  ncq
# - improve use of gmTools.cPaths()
#
# Revision 1.326  2007/05/07 08:04:13  ncq
# - rename menu admin to office
#
# Revision 1.325  2007/04/27 13:29:08  ncq
# - bump expected db version
#
# Revision 1.324  2007/04/25 22:01:25  ncq
# - add database language configurator
#
# Revision 1.323  2007/04/19 13:12:51  ncq
# - use gmTools.cPaths to use proper user prefs file
#
# Revision 1.322  2007/04/11 20:43:51  ncq
# - cleanup
#
# Revision 1.321  2007/04/11 14:51:55  ncq
# - use SetAppName() on App instance
#
# Revision 1.320  2007/04/02 18:40:58  ncq
# - add menu item to start new encounter
#
# Revision 1.319  2007/04/01 15:28:14  ncq
# - safely get_encoding()
#
# Revision 1.318  2007/03/26 16:09:50  ncq
# - lots of statustext signal fixes
#
# Revision 1.317  2007/03/26 14:44:20  ncq
# - eventually support flushing/backing up the log file
# - add hook startup-after-GUI-init
#
# Revision 1.316  2007/03/23 16:42:46  ncq
# - upon initial startup set focus to patient selector as requested by user ;-)
#
# Revision 1.315  2007/03/18 14:08:39  ncq
# - add allergy handling
# - disconnect statustext handler on shutdown
# - run_hook_script() now in gmHooks.py
#
# Revision 1.314  2007/03/10 15:15:18  ncq
# - anchor medical content links based on locale
#
# Revision 1.313  2007/03/09 16:58:13  ncq
# - do not include encoding in GDT file name anymore, we now put it into the file itself
#
# Revision 1.312  2007/03/08 16:20:28  ncq
# - typo fix
#
# Revision 1.311  2007/03/08 11:40:38  ncq
# - setting client encoding now done directly from login function
# - user preferences file now gnumed.conf again
#
# Revision 1.310  2007/03/02 15:40:42  ncq
# - make ourselves a listener for gmSignals.statustext()
# - decode() strftime() output to u''
#
# Revision 1.309  2007/02/22 17:35:22  ncq
# - add export as GDT
#
# Revision 1.308  2007/02/19 16:14:06  ncq
# - use gmGuiHelpers.run_hook_script()
#
# Revision 1.307  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.306  2007/02/09 15:01:14  ncq
# - show consultation editor just before patient change if
#   either assessment of encounter is empty or the duration is zero
# - if the duration is zero, then set last_affirmed to now()
#
# Revision 1.305  2007/02/04 17:30:08  ncq
# - need to expand ~/ appropriately
#
# Revision 1.304  2007/01/30 17:53:29  ncq
# - improved doc string
# - cleanup
# - use user preferences file for saving locale mismatch ignoring
#
# Revision 1.303  2007/01/24 11:04:53  ncq
# - use global expected_db_ver and set it to "v5"
#
# Revision 1.302  2007/01/20 22:04:50  ncq
# - run user script after patient activation
#
# Revision 1.301  2007/01/17 13:39:10  ncq
# - show encounter summary editor before patient change
#   only if actually entered any data
#
# Revision 1.300  2007/01/15 13:06:49  ncq
# - if we can "import webbrowser" we really shouldn't "gmShellAPI.run_command_in_shell('firefox')"
#
# Revision 1.299  2007/01/13 22:21:58  ncq
# - try capturing the title bar, too, in snapshot()
#
# Revision 1.298  2007/01/09 18:02:46  ncq
# - add jump_to_ifap() ready for being factored out
#
# Revision 1.297  2007/01/09 13:00:09  ncq
# - wx.CallAfter(self._do_after_init) in OnInit() so we can properly order things
#   to do after init: we already check external patient sources
#
# Revision 1.296  2007/01/04 22:52:01  ncq
# - accelerator key for "health issue" in EMR menu
#
# Revision 1.295  2006/12/27 16:44:02  ncq
# - delay looking up of external patients on startup so we don't
#   fail the entire application if there's an error in that code
#
# Revision 1.294  2006/12/25 22:54:28  ncq
# - add comment on prospective DICOM viewer behaviour
# - link to firefox with URL of medical content links wiki page from knowledge menu
#
# Revision 1.293  2006/12/23 15:25:40  ncq
# - use gmShellAPI
#
# Revision 1.292  2006/12/21 17:54:23  ncq
# - cleanup
#
# Revision 1.291  2006/12/21 17:19:49  ncq
# - need to do *something* in setup_platform, and be it "pass"
#
# Revision 1.290  2006/12/21 16:53:59  ncq
# - init image handlers once for good
#
# Revision 1.289  2006/12/21 11:04:29  ncq
# - ensureMinimal() is the proper way to go about ensuring a minimum wxPython version
# - only set gmPG2 module global encoding if explicitely set by config file
# - use more predefined wx.ID_*s and do away with module global wx.NewId() constants
# - fix standalone startup to init gmI18N
#
# Revision 1.288  2006/12/18 12:59:24  ncq
# - properly ensure minimum wxPython version, including unicode,
#   should now allow for 2.7, 2.8, gtk2, mac, msw
#
# Revision 1.287  2006/12/17 22:20:33  ncq
# - accept wxPython > 2.6
#
# Revision 1.286  2006/12/15 15:26:21  ncq
# - cleanup
#
# Revision 1.285  2006/12/15 15:25:01  ncq
# - delete checking of database version to gmLogin.py where it belongs
#
# Revision 1.284  2006/12/13 15:01:35  ncq
# - on_add_medication does not work yet
#
# Revision 1.283  2006/12/13 15:00:38  ncq
# - import datetime
# - we already have _provider so no need for on-the-spot gmPerson.gmCurrentProvider()
# - improve menu item labels
# - make transfer file and shell command configurable for ifap call
# - snapshot name includes timestamp
#
# Revision 1.282  2006/12/06 16:08:44  ncq
# - improved __on_ifap() to display return values in message box
#
# Revision 1.281  2006/12/05 14:00:16  ncq
# - define expected db schema version
# - improve schema hash checking
# - add IFAP drug db link under "Knowledge" menu
#
# Revision 1.280  2006/12/01 13:58:12  ncq
# - add screenshot function
#
# Revision 1.279  2006/11/24 14:22:57  ncq
# - use shiny new health issue edit area
#
# Revision 1.278  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.277  2006/11/20 17:26:46  ncq
# - missing self.
#
# Revision 1.276  2006/11/20 16:04:08  ncq
# - translate Help menu title
# - move unlock mouse to tools menu
# - comment out dermatology module from tools menu as there is no maintainer
#
# Revision 1.275  2006/11/19 11:15:13  ncq
# - cannot wx.CallAfter() __on_pre_patient_selection() since
#   patient would have changed underhand
#
# Revision 1.274  2006/11/07 00:31:23  ncq
# - remove some cruft
#
# Revision 1.273  2006/11/06 12:53:09  ncq
# - lower severity of verbose part of "incompatible database warning" message
#
# Revision 1.272  2006/11/05 16:04:29  ncq
# - add menu item GNUmed/Unlock mouse
#
# Revision 1.271  2006/10/31 12:39:54  ncq
# - remove traces of gmPG
#
# Revision 1.270  2006/10/28 13:03:58  ncq
# - check patient before calling wxCallAfter() in _pre_patient_selection
# - strftime() doesn't take u''
#
# Revision 1.269  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.268  2006/10/25 07:26:42  ncq
# - make do without gmPG
#
# Revision 1.267  2006/10/24 13:24:12  ncq
# - now use gmLogin.connect_to_database()
#
# Revision 1.266  2006/10/09 12:25:21  ncq
# - almost entirely convert over to gmPG2
# - rip out layout manager selection code
# - better use of db level cfg
# - default size now 800x600
#
# Revision 1.265  2006/08/11 13:10:08  ncq
# - even if we cannot find wxversion still test for 2.6.x/unicode after
#   the fact and make very unhappy noises before drifting off into coma
#
# Revision 1.264  2006/08/06 20:04:02  ncq
# - improve wxPython version checking and related messages
#
# Revision 1.263  2006/08/01 22:04:32  ncq
# - call disable_identity()
#
# Revision 1.262  2006/07/30 18:47:19  ncq
# - add load ext pat to patient menu
# - prepare patient "deletion" from menu
#
# Revision 1.261  2006/07/24 11:30:02  ncq
# - must set parent when loading external patients
#
# Revision 1.260  2006/07/21 21:34:58  ncq
# - check for minimum required version/type of wxPython
#
# Revision 1.259  2006/07/18 21:17:21  ncq
# - use gmPatSearchWidgets.load_patient_from_external_sources()
#
# Revision 1.258  2006/07/17 21:07:59  ncq
# - create new patient from BDT file if not found
#
# Revision 1.257  2006/07/17 18:50:11  ncq
# - upon startup activate patient read from xDT file if patient exists
#
# Revision 1.256  2006/07/17 10:53:50  ncq
# - don't die on missing bdt file on startup
#
# Revision 1.255  2006/07/13 21:01:26  ncq
# - display external patient on startup if XDT file available
#
# Revision 1.254  2006/07/07 12:09:00  ncq
# - cleanup
# - add document type editing to administrative menu
#
# Revision 1.253  2006/07/01 15:12:02  ncq
# - set_curr_lang() failure has been downgraded to warning
#
# Revision 1.252  2006/07/01 11:32:13  ncq
# - setting up database connection encoding now requires two encoding names
#
# Revision 1.251  2006/06/28 10:18:02  ncq
# - only set gmPG default client encoding if actually set in the config file
#
# Revision 1.250  2006/06/13 20:35:46  ncq
# - use localized date/time format taken from datetime library
#
# Revision 1.249  2006/06/10 05:12:42  ncq
# - edit staff list
#
# Revision 1.248  2006/06/07 21:04:19  ncq
# - fix re-setting DB lang to en_GB on failure to set preferred lang
#
# Revision 1.247  2006/06/06 20:48:31  ncq
# - actually implement delisting staff member
#
# Revision 1.246  2006/06/06 10:22:23  ncq
# - menu_office -> menu_administration
# - menu_reference -> menu_knowledge
# - cleanup
#
# Revision 1.245  2006/05/20 18:36:45  ncq
# - reset DB language to EN on failing to set it to the user's locale
#
# Revision 1.244  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.243  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.242  2006/05/14 18:09:05  ncq
# - db_account -> db_user
#
# Revision 1.241  2006/05/12 12:20:38  ncq
# - use gmCurrentProvider
# - whoami -> whereami
#
# Revision 1.240  2006/05/10 13:08:37  ncq
# - properly log physical screen size
#
# Revision 1.239  2006/05/06 18:50:43  ncq
# - improve summary display after user complaint
#
# Revision 1.238  2006/05/04 17:52:04  ncq
# - mark EMR summary for translation
#
# Revision 1.237  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.236  2006/04/23 16:49:41  ncq
# - add "Show EMR summary" as per list discussion
#
# Revision 1.235  2006/03/14 21:37:18  ncq
# - add menu "Office"
# - add menu item "add staff member" under "Office" serially calling new patient wizard and add staff dialog
# - fix encounter summary
#
# Revision 1.234  2006/03/09 21:12:44  ncq
# - allow current patient to be enlisted as staff from the main menu
#
# Revision 1.233  2006/02/27 22:38:36  ncq
# - spell out rfe/aoe as per Richard's request
#
# Revision 1.232  2006/01/24 21:09:45  ncq
# - use whoami.get_short_alias
#
# Revision 1.231  2006/01/15 14:29:44  ncq
# - cleanup
#
# Revision 1.230  2006/01/09 20:27:04  ncq
# - set_curr_lang() is in schema i18n, too
#
# Revision 1.229  2006/01/09 20:19:06  ncq
# - adjust to i18n schema
#
# Revision 1.228  2006/01/03 12:12:03  ncq
# - make epydoc happy re _()
#
# Revision 1.227  2005/12/27 18:54:50  ncq
# - -> GNUmed
# - enlarge About
# - verify database on startup
# - display database banner if it exists
#
# Revision 1.226  2005/12/14 17:01:51  ncq
# - use improved db cfg option getting
#
# Revision 1.225  2005/11/29 18:59:41  ncq
# - cleanup
#
# Revision 1.224  2005/11/27 20:20:46  ncq
# - slave mode cfg return is string, not integer
#
# Revision 1.223  2005/11/18 15:23:23  ncq
# - enable simple EMR search
#
# Revision 1.222  2005/11/06 11:10:42  ihaywood
# dermtool proof-of-concept
# Access from Tools|Dermatology menu item
# A small range of derm pictures using free-as-in-speech sources are included.
#
# CVm: ----------------------------------------------------------------------
#
# Revision 1.221  2005/10/12 22:32:22  ncq
# - encounter['description'] -> encounter['aoe']
#
# Revision 1.220  2005/10/08 12:37:25  sjtan
# enc['description'] can return None
#
# Revision 1.219  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.218  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.217  2005/09/27 20:44:58  ncq
# - wx.wx* -> wx.*
#
# Revision 1.216  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.215  2005/09/24 09:17:28  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.214  2005/09/11 17:34:10  ncq
# - support consultation summary generation just before
#   switching to the next patient
#
# Revision 1.213  2005/09/04 07:30:24  ncq
# - comment out search-patient menu item for now
#
# Revision 1.212  2005/07/24 18:57:48  ncq
# - add "search" to "patient" menu - all it does is focus the search box ...
#
# Revision 1.211  2005/07/24 11:35:59  ncq
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
# Fix to allow running gmAbout.py under wxpython26 wx.Size > wx.Size
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
# - move to wx.* use
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
#   wx.Panel child class
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
# - also process wx.EVT_NOTEBOOK_PAGE_CHANGING
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
