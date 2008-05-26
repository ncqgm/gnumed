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
# $Id: gmGuiMain.py,v 1.404 2008-05-26 13:31:34 ncq Exp $
__version__ = "$Revision: 1.404 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import sys, time, os, cPickle, zlib, locale, os.path, datetime as pyDT, webbrowser, shutil, logging


# 3rd party libs
# wxpython version cannot be enforced inside py2exe and friends
if not hasattr(sys, 'frozen'):
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
version = int(u'%s%s' % (wx.MAJOR_VERSION, wx.MINOR_VERSION))
if (version < 26) or ('unicode' not in wx.PlatformInfo):
	print "GNUmed startup: Unsupported wxPython version (%s: %s)." % (wx.VERSION_STRING, wx.PlatformInfo)
	print "GNUmed startup: wxPython 2.6+ with unicode support is required."
	print 'CRITICAL ERROR: Proper wxPython version not found. Halted.'
	raise ValueError('wxPython 2.6+ with unicode support not found')


# GNUmed libs
from Gnumed.pycommon import gmCfg, gmPG2, gmDispatcher, gmGuiBroker, gmI18N, gmExceptions, gmShellAPI, gmTools, gmDateTime, gmHooks, gmBackendListener, gmCfg2, gmLog2
from Gnumed.wxpython import gmGuiHelpers, gmHorstSpace, gmEMRBrowser, gmDemographicsWidgets, gmEMRStructWidgets
from Gnumed.wxpython import gmStaffWidgets, gmMedDocWidgets, gmPatSearchWidgets, gmAllergyWidgets, gmListWidgets
from Gnumed.wxpython import gmFormWidgets, gmSnellen, gmProviderInboxWidgets, gmCfgWidgets, gmExceptionHandlingWidgets, gmTimer
from Gnumed.business import gmPerson, gmClinicalRecord, gmSurgery, gmEMRStructItems
from Gnumed.exporters import gmPatientExporter

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

_cfg = gmCfg2.gmCfgData()
_provider = None
_scripting_listener = None
expected_db_ver = u'devel'
current_client_ver = u'CVS HEAD'
current_client_branch = '0.2.8'

_log = logging.getLogger('gm.main')
_log.info(__version__)
_log.info('wxPython GUI framework: %s %s' % (wx.VERSION_STRING, wx.PlatformInfo))
_log.info('GNUmed client version [%s] on branch [%s]', current_client_ver, current_client_branch)
_log.info('expected database version [%s]', expected_db_ver)

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

	ifap_cmd = dbcfg.get2 (
		option = 'external.ifap-win.shell_command',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = 'wine "C:\Ifapwin\WIAMDB.EXE"'
	)
	found, binary = gmShellAPI.detect_external_binary(ifap_cmd)
	if not found:
		gmDispatcher.send('statustext', msg = _('Cannot call IFAP via [%s].') % ifap_cmd)
		return False
	ifap_cmd = binary

	if import_drugs:
		transfer_file = os.path.expanduser(dbcfg.get2 (
			option = 'external.ifap-win.transfer_file',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = '~/.wine/drive_c/Ifapwin/ifap2gnumed.csv'
		))
		# file must exist for Ifap to write into it
		try:
			f = open(transfer_file, 'w+b').close()
		except IOError:
			_log.exception('Cannot create IFAP <-> GNUmed transfer file [%s]', transfer_file)
			gmDispatcher.send('statustext', msg = _('Cannot create IFAP <-> GNUmed transfer file [%s].') % transfer_file)
			return False

	wx.BeginBusyCursor()
	gmShellAPI.run_command_in_shell(command = ifap_cmd, blocking = import_drugs)
	wx.EndBusyCursor()

	if import_drugs:
		# COMMENT: this file must exist PRIOR to invoking IFAP
		# COMMENT: or else IFAP will not write data into it ...
		try:
			csv_file = open(transfer_file, 'rb')						# FIXME: encoding
		except:
			_log.exception('cannot access [%s]', fname)
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
# FIXME: this belongs elsewhere
def check_for_updates():

	dbcfg = gmCfg.cCfgSQL()

	url = dbcfg.get2 (
		option = u'horstspace.update.url',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = u'http://www.gnumed.de/downloads/gnumed-versions.txt'
	)

	consider_latest_branch = bool(dbcfg.get2 (
		option = u'horstspace.update.consider_latest_branch',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = True
	))

	found, msg = gmTools.check_for_update (
		url = url,
		current_branch = current_client_branch,
		current_version = current_client_ver,
		consider_latest_branch = consider_latest_branch
	)

	if found is False:
		gmDispatcher.send(signal = 'statustext', msg = _('Your client is up to date.'))
		return

	gmGuiHelpers.gm_show_info (
		msg,
		_('Checking for client updates')
	)

#==============================================================================
class gmTopLevelFrame(wx.Frame):
	"""GNUmed client's main windows frame.

	This is where it all happens. Avoid popping up any other windows.
	Most user interaction should happen to and from widgets within this frame
	"""
	#----------------------------------------------
	def __init__(self, parent, id, title, size=wx.DefaultSize):
		"""You'll have to browse the source to understand what the constructor does
		"""
		wx.Frame.__init__ (
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
		_log.info('workplace is >>>%s<<<', gmSurgery.gmCurrentPractice().active_workplace)
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
		if _cfg.get(option = 'slave'):
			self.__title_template = _('Enslaved GNUmed [%s%s.%s@%s] %s')
		else:
			self.__title_template = 'GNUmed [%s%s.%s@%s] %s'

		self.updateTitle()

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
	def __setup_accelerators(self):
		self.acctbl.append((wx.ACCEL_ALT | wx.ACCEL_CTRL, ord('X'), wx.ID_EXIT))
		self.acctbl.append((wx.ACCEL_CTRL, ord('H'), wx.ID_HELP))
		self.SetAcceleratorTable(wx.AcceleratorTable(self.acctbl))
	#----------------------------------------------
	def __set_GUI_size(self):
		"""Try to get previous window size from backend."""

		cfg = gmCfg.cCfgSQL()

		# width
		width = int(cfg.get2 (
			option = 'main.window.width',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = 800
		))

		# height
		height = int(cfg.get2 (
			option = 'main.window.height',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = 600
		))

		_log.debug('setting GUI size to [%s:%s]' % (width, height))
 		self.SetClientSize(wx.Size(width, height))
	#----------------------------------------------
	def __setup_main_menu(self):
		"""Create the main menu entries.

		Individual entries are farmed out to the modules.
		"""
		global wx
		self.mainmenu = wx.MenuBar()
		self.__gb['main.mainmenu'] = self.mainmenu

		# -- menu "GNUmed" -----------------
		menu_gnumed = wx.Menu()

		menu_config = wx.Menu()
		menu_gnumed.AppendMenu(wx.NewId(), _('Options ...'), menu_config)

		# -- submenu gnumed-config-db
		menu_cfg_db = wx.Menu()
		menu_config.AppendMenu(wx.NewId(), _('Database ...'), menu_cfg_db)

		ID = wx.NewId()
		menu_cfg_db.Append(ID, _('Language'), _('Configure the database language'))
		wx.EVT_MENU(self, ID, self.__on_set_db_lang)

		ID = wx.NewId()
		menu_cfg_db.Append(ID, _('Welcome message'), _('Configure the database welcome message (all users).'))
		wx.EVT_MENU(self, ID, self.__on_set_db_welcome)

		ID = wx.NewId()
		menu_cfg_db.Append(ID, _('Export chunk size'), _('Configure the chunk size used when exporting BLOBs from the database.'))
		wx.EVT_MENU(self, ID, self.__on_set_export_chunk_size)

		# -- submenu gnumed / config / ui
		menu_cfg_ui = wx.Menu()
		menu_config.AppendMenu(wx.NewId(), _('User interface ...'), menu_cfg_ui)

		ID = wx.NewId()
		menu_cfg_ui.Append(ID, _('Initial plugin'), _('Configure which plugin to show right after client startup.'))
		wx.EVT_MENU(self, ID, self.__on_set_startup_plugin)

		ID = wx.NewId()
		menu_cfg_ui.Append(ID, _('Workplaces'), _('Choose the plugins to load per workplace.'))
		wx.EVT_MENU(self, ID, self.__on_configure_workplace)

		# -- submenu gnumed / config / ui / docs
		menu_cfg_doc = wx.Menu()
		menu_cfg_ui.AppendMenu(wx.NewId(), _('Document handling ...'), menu_cfg_doc)

		ID = wx.NewId()
		menu_cfg_doc.Append(ID, _('Review dialog'), _('Configure review dialog after document display.'))
		wx.EVT_MENU(self, ID, self.__on_configure_doc_review_dialog)

		ID = wx.NewId()
		menu_cfg_doc.Append(ID, _('UUID display'), _('Configure unique ID dialog on document import.'))
		wx.EVT_MENU(self, ID, self.__on_configure_doc_uuid_dialog)

		ID = wx.NewId()
		menu_cfg_doc.Append(ID, _('Empty documents'), _('Whether to allow saving documents without parts.'))
		wx.EVT_MENU(self, ID, self.__on_configure_partless_docs)

		# -- submenu gnumed / config / ui / updates
		menu_cfg_update = wx.Menu()
		menu_cfg_ui.AppendMenu(wx.NewId(), _('Update handling ...'), menu_cfg_update)

		ID = wx.NewId()
		menu_cfg_update.Append(ID, _('Auto-check'), _('Whether to auto-check for updates at startup.'))
		wx.EVT_MENU(self, ID, self.__on_configure_update_check)

		ID = wx.NewId()
		menu_cfg_update.Append(ID, _('Check scope'), _('When checking for updates, consider latest branch, too ?'))
		wx.EVT_MENU(self, ID, self.__on_configure_update_check_scope)

		ID = wx.NewId()
		menu_cfg_update.Append(ID, _('URL'), _('The URL to retrieve version information from.'))
		wx.EVT_MENU(self, ID, self.__on_configure_update_url)

		# -- submenu gnumed / config / ui / patient search
		menu_cfg_pat_search = wx.Menu()
		menu_cfg_ui.AppendMenu(wx.NewId(), _('Patient search ...'), menu_cfg_pat_search)

		ID = wx.NewId()
		menu_cfg_pat_search.Append(ID, _('Birthday reminder'), _('Configure birthday reminder proximity interval.'))
		wx.EVT_MENU(self, ID, self.__on_set_dob_reminder_proximity)

		ID = wx.NewId()
		menu_cfg_pat_search.Append(ID, _('Immediate source activation'), _('Configure immediate activation of single external patient.'))
		wx.EVT_MENU(self, ID, self.__on_set_quick_pat_search)

		ID = wx.NewId()
		menu_cfg_pat_search.Append(ID, _('Initial plugin'), _('Configure which plugin to show right after patient activation.'))
		wx.EVT_MENU(self, ID, self.__on_set_initial_pat_plugin)

		# -- submenu gnumed / config / external tools
		menu_cfg_ext_tools = wx.Menu()
		menu_config.AppendMenu(wx.NewId(), _('External tools ...'), menu_cfg_ext_tools)

		ID = wx.NewId()
		menu_cfg_ext_tools.Append(ID, _('IFAP command'), _('Set the command to start IFAP.'))
		wx.EVT_MENU(self, ID, self.__on_set_ifap_cmd)

		ID = wx.NewId()
		menu_cfg_ext_tools.Append(ID, _('OOo startup time'), _('Set the time to wait for OpenOffice to settle after startup.'))
		wx.EVT_MENU(self, ID, self.__on_set_ooo_settle_time)

		# -- submenu gnumed / config / emr
		menu_cfg_emr = wx.Menu()
		menu_config.AppendMenu(wx.NewId(), _('EMR ...'), menu_cfg_emr)

		# -- submenu gnumed / config / emr / encounter
		menu_cfg_encounter = wx.Menu()
		menu_cfg_emr.AppendMenu(wx.NewId(), _('Encounter ...'), menu_cfg_encounter)

		ID = wx.NewId()
		menu_cfg_encounter.Append(ID, _('Edit on patient change'), _('Edit encounter details on changing of patients.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_enc_pat_change)

		ID = wx.NewId()
		menu_cfg_encounter.Append(ID, _('Minimum duration'), _('Minimum duration of an encounter.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_enc_min_ttl)

		ID = wx.NewId()
		menu_cfg_encounter.Append(ID, _('Maximum duration'), _('Maximum duration of an encounter.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_enc_max_ttl)

		ID = wx.NewId()
		menu_cfg_encounter.Append(ID, _('Minimum empty age'), _('Minimum age of an empty encounter before considering for deletion.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_enc_empty_ttl)

		ID = wx.NewId()
		menu_cfg_encounter.Append(ID, _('Default type'), _('Default type for new encounters.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_enc_default_type)

		# -- submenu gnumed / config / emr / episode
		menu_cfg_episode = wx.Menu()
		menu_cfg_emr.AppendMenu(wx.NewId(), _('Episode ...'), menu_cfg_episode)

		ID = wx.NewId()
		menu_cfg_episode.Append(ID, _('Dormancy'), _('Maximum length of dormancy after which an episode will be considered closed.'))
		wx.EVT_MENU(self, ID, self.__on_cfg_epi_ttl)

		# --
		menu_gnumed.AppendSeparator()

		ID = wx.NewId()
		menu_gnumed.Append(ID, _('Check for updates'), _('Check for new releases of the GNUmed client.'))
		wx.EVT_MENU(self, ID, self.__on_check_for_updates)

		menu_gnumed.Append(wx.ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUmed client.'))
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
		self.menu_office.Append(ID_EDIT_DOC_TYPES, _('Manage document types'), _('Edit the document types available in the system.'))
		wx.EVT_MENU(self, ID_EDIT_DOC_TYPES, self.__on_edit_doc_types)

		self.__gb['main.officemenu'] = self.menu_office
		self.mainmenu.Append(self.menu_office, _('&Office'))

		# -- menu "Patient" ---------------------------
		menu_patient = wx.Menu()

		ID_CREATE_PATIENT = wx.NewId()
		menu_patient.Append(ID_CREATE_PATIENT, _('Register new'), _("Register a new patient with this practice"))
		wx.EVT_MENU(self, ID_CREATE_PATIENT, self.__on_create_patient)

		ID_LOAD_EXT_PAT = wx.NewId()
		menu_patient.Append(ID_LOAD_EXT_PAT, _('Load external'), _('Load and possibly create patient from an external source.'))
		wx.EVT_MENU(self, ID_LOAD_EXT_PAT, self.__on_load_external_patient)

		ID_DEL_PAT = wx.NewId()
		menu_patient.Append(ID_DEL_PAT, _('Deactivate record'), _('Deactivate (exclude from search) patient record in database.'))
		wx.EVT_MENU(self, ID_DEL_PAT, self.__on_delete_patient)

		menu_patient.AppendSeparator()

		ID_ENLIST_PATIENT_AS_STAFF = wx.NewId()
		menu_patient.Append(ID_ENLIST_PATIENT_AS_STAFF, _('Enlist as staff'), _('Enlist current patient as staff member'))
		wx.EVT_MENU(self, ID_ENLIST_PATIENT_AS_STAFF, self.__on_enlist_patient_as_staff)

		# FIXME: temporary until external program framework is active
		ID = wx.NewId()
		menu_patient.Append(ID, _('Export to GDT'), _('Export demographics of current patient into GDT file.'))
		wx.EVT_MENU(self, ID, self.__on_export_as_gdt)

		menu_patient.AppendSeparator()

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

		# - submenu "Medical History"
		menu_history = wx.Menu()
		menu_emr.AppendMenu(wx.NewId(), _('Medical &history ...'), menu_history)
		# - add health issue
		ID_ADD_HEALTH_ISSUE_TO_EMR = wx.NewId()
		menu_history.Append (
			ID_ADD_HEALTH_ISSUE_TO_EMR,
			_('&Past history (foundational issue / PMH)'),
			_('Add a past/previous medical history item (foundational health issue) to the EMR of the active patient')
		)
		wx.EVT_MENU(self, ID_ADD_HEALTH_ISSUE_TO_EMR, self.__on_add_health_issue)
		# - document current medication
		ID_ADD_DRUGS_TO_EMR = wx.NewId()
		menu_history.Append (
			ID_ADD_DRUGS_TO_EMR,
			_('Current &medication'),
			_('Select current medication from drug database and save into progress notes.')
		)
		wx.EVT_MENU(self, ID_ADD_DRUGS_TO_EMR, self.__on_add_medication)
		# - add allergy
		ID = wx.NewId()
		menu_history.Append (
			ID,
			_('&Allergies'),
			_('Manage documentation of allergies for the current patient.')
		)
		wx.EVT_MENU(self, ID, self.__on_manage_allergies)
		# - edit occupation
		ID = wx.NewId()
		menu_history.Append(ID, _('&Occupation'), _('Edit occupation details for the current patient.'))
		wx.EVT_MENU(self, ID, self.__on_edit_occupation)

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
		elif gmShellAPI.detect_external_binary(binary = 'aeskulap')[0]:
			viewer = u'Aeskulap'
		elif gmShellAPI.detect_external_binary(binary = 'amide')[0]:
			viewer = u'AMIDE'
		elif gmShellAPI.detect_external_binary(binary = 'xmedcon')[0]:
			viewer = u'(x)medcon'
		self.menu_tools.Append(ID_DICOM_VIEWER, _('DICOM viewer'), _('Start DICOM viewer (%s) for CD-ROM (X-Ray, CT, MR, etc). On Windows just insert CD.') % viewer)
		wx.EVT_MENU(self, ID_DICOM_VIEWER, self.__on_dicom_viewer)
		if viewer == _('no viewer installed'):
			_log.info('neither of OsiriX / Aeskulap / AMIDE / xmedcon found, disabling "DICOM viewer" menu item')
			self.menu_tools.Enable(id=ID_DICOM_VIEWER, enable=False)

#		ID_DERMTOOL = wx.NewId()
#		self.menu_tools.Append(ID_DERMTOOL, _("Dermatology"), _("A tool to aid dermatology diagnosis"))
#		wx.EVT_MENU (self, ID_DERMTOOL, self.__dermtool)

		ID = wx.NewId()
		self.menu_tools.Append(ID, _('Snellen chart'), _('Display fullscreen snellen chart.'))
		wx.EVT_MENU(self, ID, self.__on_snellen)

		self.menu_tools.AppendSeparator()

		# menu "Knowledge" ---------------------
		menu_knowledge = wx.Menu()
		self.__gb['main.knowledgemenu'] = menu_knowledge
		self.mainmenu.Append(menu_knowledge, _("&Knowledge"))

		# - IFAP drug DB
		ID_IFAP = wx.NewId()
		menu_knowledge.Append(ID_IFAP, _('ifap index (Win)'), _('Start "ifap index PRAXIS (Windows)" drug browser'))
		wx.EVT_MENU(self, ID_IFAP, self.__on_ifap)

#		menu_knowledge.AppendSeparator()

		# - "recommended" medical links in the Wiki
		ID_MEDICAL_LINKS = wx.NewId()
		menu_knowledge.Append(ID_MEDICAL_LINKS, _('Medical links (www)'), _('Show a page of links to useful medical content.'))
		wx.EVT_MENU(self, ID_MEDICAL_LINKS, self.__on_medical_links)

		# -- menu "Help" --------------
		help_menu = wx.Menu()

		ID = wx.NewId()
		help_menu.Append(ID, _('GNUmed wiki'), _('Go to the GNUmed wiki on the web.'))
		wx.EVT_MENU(self, ID, self.__on_display_wiki)

		ID = wx.NewId()
		help_menu.Append(ID, _('User manual (www)'), _('Go to the User Manual on the web.'))
		wx.EVT_MENU(self, ID, self.__on_display_user_manual_online)

		menu_debugging = wx.Menu()
		help_menu.AppendMenu(wx.NewId(), _('Debugging ...'), menu_debugging)

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

		if _cfg.get(option = 'debug'):
			ID_TOGGLE_PAT_LOCK = wx.NewId()
			menu_debugging.Append(ID_TOGGLE_PAT_LOCK, _('Lock/unlock patient'), _('Lock/unlock patient - USE ONLY IF YOU KNOW WHAT YOU ARE DOING !'))
			wx.EVT_MENU(self, ID_TOGGLE_PAT_LOCK, self.__on_toggle_patient_lock)

			ID_TEST_EXCEPTION = wx.NewId()
			menu_debugging.Append(ID_TEST_EXCEPTION, _('Test error handling'), _('Throw an exception to test error handling.'))
			wx.EVT_MENU(self, ID_TEST_EXCEPTION, self.__on_test_exception)

			ID = wx.NewId()
			menu_debugging.Append(ID, _('Invoke inspector'), _('Invoke the widget hierarchy inspector (needs wxPython 2.8).'))
			wx.EVT_MENU(self, ID, self.__on_invoke_inspector)
			try:
				import wx.lib.inspection
			except ImportError:
				menu_debugging.Enable(id = ID, enable = False)

		help_menu.AppendSeparator()

		help_menu.Append(wx.ID_ABOUT, _('About GNUmed'), "")
		wx.EVT_MENU (self, wx.ID_ABOUT, self.OnAbout)

		ID_CONTRIBUTORS = wx.NewId()
		help_menu.Append(ID_CONTRIBUTORS, _('GNUmed contributors'), _('show GNUmed contributors'))
		wx.EVT_MENU(self, ID_CONTRIBUTORS, self.__on_show_contributors)

		help_menu.AppendSeparator()

		# among other things the Manual is added from a plugin
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
		gmDispatcher.connect(self._on_pre_patient_selection, 'pre_patient_selection')
		gmDispatcher.connect(self._on_post_patient_selection, 'post_patient_selection')
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_pat_name_changed)
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_pat_name_changed)

		gmDispatcher.connect(self._on_set_statustext, u'statustext')
		gmDispatcher.connect(self._on_request_user_attention, u'request_user_attention')

		gmDispatcher.connect(self._on_db_maintenance_warning, u'db_maintenance_warning')
	#-----------------------------------------------
	def _on_set_statustext(self, msg=None, loglevel=None, beep=True):

		if msg is None:
			msg = _('programmer forgot to specify status message')

		if loglevel is not None:
			_log.log(loglevel, msg.replace('\015', ' ').replace('\012', ' '))

		wx.CallAfter(self.SetStatusText, msg)

		if beep:
			wx.Bell()
	#-----------------------------------------------
	def _on_db_maintenance_warning(self):
		wx.CallAfter(self.__on_db_maintenance_warning)
	#-----------------------------------------------
	def __on_db_maintenance_warning(self):

		self.SetStatusText(_('The database will be shut down for maintenance in a few minutes.'))
		wx.Bell()
		if not wx.GetApp().IsActive():
			self.RequestUserAttention(flags = wx.USER_ATTENTION_ERROR)

		gmHooks.run_hook_script(hook = u'db_maintenance_warning')

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			None,
			-1,
			caption = _('Database shutdown warning'),
			question = _(
				'The database will be shut down for maintenance\n'
				'in a few minutes.\n'
				'\n'
				'In order to not suffer any loss of data you\n'
				'will need to save your current work and log\n'
				'out of this GNUmed client.\n'
			),
			button_defs = [
				{
					u'label': _('Close now'),
					u'tooltip': _('Close this GNUmed client immediately.'),
					u'default': False
				},
				{
					u'label': _('Finish work'),
					u'tooltip': _('Finish and save current work first, then manually close this GNUmed client.'),
					u'default': True
				}
			]
		)
		decision = dlg.ShowModal()
		if decision == wx.ID_YES:
			top_win = wx.GetApp().GetTopWindow()
			wx.CallAfter(top_win.Close)
	#-----------------------------------------------
	def _on_request_user_attention(self, msg=None, urgent=False):
		wx.CallAfter(self.__on_request_user_attention, msg, urgent)
	#-----------------------------------------------
	def __on_request_user_attention(self, msg=None, urgent=False):
		# already in the foreground ?
		if not wx.GetApp().IsActive():
			if urgent:
				self.RequestUserAttention(flags = wx.USER_ATTENTION_ERROR)
			else:
				self.RequestUserAttention(flags = wx.USER_ATTENTION_INFO)

		if msg is not None:
			self.SetStatusText(msg)

		if urgent:
			wx.Bell()

		gmHooks.run_hook_script(hook = u'request_user_attention')
	#-----------------------------------------------
	def _on_pat_name_changed(self):
		wx.CallAfter(self.__on_pat_name_changed)
	#-----------------------------------------------
	def __on_pat_name_changed(self):
		self.updateTitle()
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

		# let's try this async
		self.__sanity_check_encounter()

		self.__on_pre_patient_selection(**kwargs)
	#----------------------------------------------
	def __on_pre_patient_selection(self, **kwargs):

		# FIXME: we need a way to make sure the patient has not yet changed
#		pat = gmPerson.gmCurrentPatient()
#		if not pat.is_connected():
#			return True

		return True
	#----------------------------------------------
	def __sanity_check_encounter(self):

		dbcfg = gmCfg.cCfgSQL()
		check_enc = bool(dbcfg.get2 (
			option = 'encounter.show_editor_before_patient_change',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = True					# True: if needed, not always unconditionally
		))

		if not check_enc:
			return True

		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		enc = emr.get_active_encounter()

		# did we add anything to the EMR ?
		has_narr = enc.has_narrative()
		has_docs = enc.has_documents()

		if (not has_narr) and (not has_docs):
			return True

		empty_aoe = (gmTools.coalesce(enc['assessment_of_encounter'], '').strip() == u'')
		zero_duration = (enc['last_affirmed'] == enc['started'])

		# all is well anyway
		if (not empty_aoe) and (not zero_duration):
			return True

		if zero_duration:
			enc['last_affirmed'] = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)

		# no narrative, presumably only import of docs and done
		if not has_narr:
			if empty_aoe:
				enc['assessment_of_encounter'] = _('only documents added')
			enc['pk_type'] = gmEMRStructItems.get_encounter_type(description = 'chart review')[0]
			# "last_affirmed" should be latest modified_at of relevant docs but that's a lot more involved
			enc.save_payload()
			return True

		# does have narrative
		if empty_aoe:
			# - work out suitable default
			epis = emr.get_episodes_by_encounter()
			if len(epis) > 0:
				enc_summary = ''
				for epi in epis:
					enc_summary += '%s; ' % epi['description']
				enc['assessment_of_encounter'] = enc_summary

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
	def __on_check_for_updates(self, evt):
		check_for_updates()
	#----------------------------------------------
	# submenu GNUmed / database
	#----------------------------------------------
	def __on_set_export_chunk_size(self, evt):

		def is_valid(value):
			try:
				i = int(value)
			except:
				return False, value
			if i < 0:
				return False, value
			if i > (1024 * 1024 * 1024 * 10): 		# 10 GB
				return False, value
			return True, i

		gmCfgWidgets.configure_string_option (
			message = _(
				'Some network installations cannot cope with loading\n'
				'documents of arbitrary size in one piece from the\n'
				'database (mainly observed on older Windows versions)\n.'
				'\n'
				'Under such circumstances documents need to be retrieved\n'
				'in chunks and reassembled on the client.\n'
				'\n'
				'Here you can set the size (in Bytes) above which\n'
				'GNUmed will retrieve documents in chunks. Setting this\n'
				'value to 0 will disable the chunking protocol.'
			),
			option = 'horstspace.blob_export_chunk_size',
			bias = 'workplace',
			default_value = 1024 * 1024,
			validator = is_valid
		)
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
	def __on_set_db_welcome(self, event):
		dlg = gmGuiHelpers.cGreetingEditorDlg(self, -1)
		dlg.ShowModal()
	#----------------------------------------------
	# submenu GNUmed - config - external tools
	#----------------------------------------------
	def __on_set_ooo_settle_time(self, event):

		def is_valid(value):
			try:
				return True, float(value)
			except:
				return False, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'When GNUmed cannot find an OpenOffice server it\n'
				'will try to start one. OpenOffice, however, needs\n'
				'some time to fully start up.\n'
				'\n'
				'Here you can set the time for GNUmed to wait for OOo.\n'
			),
			option = 'external.ooo.startup_settle_time',
			bias = 'workplace',
			default_value = 2.0,
			validator = is_valid
		)
	#----------------------------------------------
	def __on_set_ifap_cmd(self, event):

		def is_valid(value):
			found, binary = gmShellAPI.detect_external_binary(value)
			if not found:
				gmDispatcher.send (
					signal = 'statustext',
					msg = _('The command [%s] is not found. This may or may not be a problem.') % value,
					beep = True
				)
				return False, value
			return True, binary

		gmCfgWidgets.configure_string_option (
			message = _(
				'Enter the shell command with which to start the\n'
				'the IFAP drug database.\n'
				'\n'
				'GNUmed will try to verify the path which may,\n'
				'however, fail if you are using an emulator such\n'
				'as Wine. Nevertheless, starting IFAP will work\n'
				'as long as the shell command is correct despite\n'
				'the failing test.'
			),
			option = 'external.ifap-win.shell_command',
			bias = 'workplace',
			default_value = 'C:\Ifapwin\WIAMDB.EXE',
			validator = is_valid
		)
	#----------------------------------------------
	# submenu GNUmed / config / ui
	#----------------------------------------------
	def __on_set_startup_plugin(self, evt):

		dbcfg = gmCfg.cCfgSQL()
		# get list of possible plugins
		plugin_list = gmTools.coalesce(dbcfg.get2 (
			option = u'horstspace.notebook.plugin_load_order',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user'
		), [])

		# get current setting
		initial_plugin = gmTools.coalesce(dbcfg.get2 (
			option = u'horstspace.plugin_to_raise_after_startup',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user'
		), u'gmEMRBrowserPlugin')
		try:
			selections = [plugin_list.index(initial_plugin)]
		except ValueError:
			selections = None

		# now let user decide
		plugin = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'Here you can choose which plugin you want\n'
				'GNUmed to display after initial startup.\n'
				'\n'
				'Note that the plugin must not require any\n'
				'patient to be activated.\n'
				'\n'
				'Select the desired plugin below:'
			),
			caption = _('Configuration'),
			choices = plugin_list,
			selections = selections,
			columns = [_('GNUmed Plugin')],
			single_selection = True
		)

		if plugin is None:
			return

		dbcfg.set (
			option = u'patient_search.plugin_to_raise_after_startup',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			value = plugin
		)
	#----------------------------------------------
	# submenu GNUmed / config / ui / patient search
	#----------------------------------------------
	def __on_set_quick_pat_search(self, evt):
		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'If there is only one external patient\n'
				'source available do you want GNUmed\n'
				'to immediately go ahead and search for\n'
				'matching patient records ?\n\n'
				'If not GNUmed will let you confirm the source.'
			),
			option = 'patient_search.external_sources.immediately_search_if_single_source',
			button_tooltips = [
				_('Yes, search for matches immediately.'),
				_('No, let me confirm the external patient first.')
			]
		)
	#----------------------------------------------
	def __on_set_dob_reminder_proximity(self, evt):

		def is_valid(value):
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'When a patient is activated GNUmed checks the\n'
				"proximity of the patient's birthday.\n"
				'\n'
				'If the birthday falls within the range of\n'
				' "today %s <the interval you set here>"\n'
				'GNUmed will remind you of the recent or\n'
				'imminent anniversary.'
			) % u'\u2213',
			option = u'patient_search.dob_warn_interval',
			bias = 'user',
			default_value = '1 week',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_set_initial_pat_plugin(self, evt):

		dbcfg = gmCfg.cCfgSQL()
		# get list of possible plugins
		plugin_list = gmTools.coalesce(dbcfg.get2 (
			option = u'horstspace.notebook.plugin_load_order',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user'
		), [])

		# get current setting
		initial_plugin = gmTools.coalesce(dbcfg.get2 (
			option = u'patient_search.plugin_to_raise_after_search',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user'
		), u'gmEMRBrowserPlugin')
		try:
			selections = [plugin_list.index(initial_plugin)]
		except ValueError:
			selections = None

		# now let user decide
		plugin = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'When a patient is activated GNUmed can\n'
				'be told to switch to a specific plugin.\n'
				'\n'
				'Select the desired plugin below:'
			),
			caption = _('Configuration'),
			choices = plugin_list,
			selections = selections,
			columns = [_('GNUmed Plugin')],
			single_selection = True
		)

		if plugin is None:
			return

		dbcfg.set (
			option = u'patient_search.plugin_to_raise_after_search',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			value = plugin
		)
	#----------------------------------------------
	# submenu GNUmed / config / encounter
	#----------------------------------------------
	def __on_cfg_enc_default_type(self, evt):
		enc_types = gmEMRStructItems.get_encounter_types()

		gmCfgWidgets.configure_string_from_list_option (
			parent = self,
			message = _('Select the default type for new encounters.\n'),
			option = 'encounter.default_type',
			bias = 'user',
			default_value = u'in surgery',
			choices = [ e[0] for e in enc_types ],
			columns = [_('Encounter type')],
			data = [ e[1] for e in enc_types ]
		)
	#----------------------------------------------
	def __on_cfg_enc_pat_change(self, event):
		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'Do you want GNUmed to show the consultation\n'
				'details editor when changing the active patient ?'
			),
			option = 'encounter.show_editor_before_patient_change',
			button_tooltips = [
				_('Yes, show the consultation editor if it seems appropriate.'),
				_('No, never show the consultation editor even if it would seem useful.')
			]
		)
	#----------------------------------------------
	def __on_cfg_enc_empty_ttl(self, evt):

		def is_valid(value):
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'When a patient is activated GNUmed checks the\n'
				'chart for encounters lacking any entries.\n'
				'\n'
				'Any such encounters older than what you set\n'
				'here will be removed from the medical record.\n'
				'\n'
				'To effectively disable removal of such encounters\n'
				'set this option to an improbable value.\n'
			),
			option = 'encounter.ttl_if_empty',
			bias = 'user',
			default_value = '1 week',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_cfg_enc_min_ttl(self, evt):

		def is_valid(value):
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'When a patient is activated GNUmed checks the\n'
				'age of the most recent consultation.\n'
				'\n'
				'If that consultation is younger than this age\n'
				'the existing consultation will be continued.\n'
				'\n'
				'(If it is really old a new consultation is\n'
				' started, or else GNUmed will ask you.)\n'
			),
			option = 'encounter.minimum_ttl',
			bias = 'user',
			default_value = '1 hour 30 minutes',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_cfg_enc_max_ttl(self, evt):

		def is_valid(value):
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'When a patient is activated GNUmed checks the\n'
				'age of the most recent consultation.\n'
				'\n'
				'If that consultation is older than this age\n'
				'GNUmed will always start a new consultation.\n'
				'\n'
				'(If it is very recent the existing consultation\n'
				' is continued, or else GNUmed will ask you.)\n'
			),
			option = 'encounter.maximum_ttl',
			bias = 'user',
			default_value = '6 hours',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_cfg_epi_ttl(self, evt):

		def is_valid(value):
			try:
				value = int(value)
			except:
				return False, value
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'At any time there can only be one open (ongoing) episode\n'
				'for each foundational health issue.\n'
				'\n'
				'When you try to open (add data to) an episode on a health\n'
				'issue GNUmed will check for an existing open episode on\n'
				'that issue. If there is any it will check the age of that\n'
				'episode. The episode is closed if it has been dormant (no\n'
				'data added, that is) for the period of time (in days) you\n'
				'set here.\n'
				'\n'
				"If the existing episode hasn't been dormant long enough\n"
				'GNUmed will consult you what to do.\n'
				'\n'
				'Enter maximum episode dormancy in DAYS:'
			),
			option = 'episode.ttl',
			bias = 'user',
			default_value = 60,
			validator = is_valid
		)
	#----------------------------------------------
	def __on_configure_workplace(self, evt):
		gmProviderInboxWidgets.configure_workplace_plugins(parent = self)
	#----------------------------------------------
	def __on_configure_update_check(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'Do you want GNUmed to check for updates at startup ?\n'
				'\n'
				'You will still need your system administrator to\n'
				'actually install any updates for you.\n'
			),
			option = u'horstspace.update.autocheck_at_startup',
			button_tooltips = [
				_('Yes, check for updates at startup.'),
				_('No, do not check for updates at startup.')
			]
		)
	#----------------------------------------------
	def __on_configure_update_check_scope(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'When checking for updates do you want GNUmed to\n'
				'look for bug fix updates only or do you want to\n'
				'know about features updates, too ?\n'
				'\n'
				'Minor updates (x.y.z.a -> x.y.z.b) contain bug fixes\n'
				'only. They can usually be installed without much\n'
				'preparation. They never require a database upgrade.\n'
				'\n'
				'Major updates (x.y.a -> x..y.b or y.a -> x.b) come\n'
				'with new features. They need more preparation and\n'
				'often require a database upgrade.\n'
				'\n'
				'You will still need your system administrator to\n'
				'actually install any updates for you.\n'
			),
			option = u'horstspace.update.consider_latest_branch',
			button_tooltips = [
				_('Yes, check for feature updates, too.'),
				_('No, check for bug-fix updates only.')
			]
		)
	#----------------------------------------------
	def __on_configure_update_url(self, evt):

		import urllib2 as url

		def is_valid(value):
			try:
				url.urlopen(value)
			except:
				return False, value

			return True, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed can check for new releases being available. To do\n'
				'so it needs to load version information from an URL.\n'
				'\n'
				'The default URL is:\n'
				'\n'
				' http://www.gnumed.de/downloads/gnumed-versions.txt\n'
				'\n'
				'but you can configure any other URL locally. Note\n'
				'that you must enter the location as a valid URL.\n'
				'Depending on the URL the client will need online\n'
				'access when checking for updates.'
			),
			option = u'horstspace.update.url',
			bias = u'workplace',
			default_value = u'http://www.gnumed.de/downloads/gnumed-versions.txt',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_configure_partless_docs(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'Do you want to allow saving of new documents without\n'
				'any parts or do you want GNUmed to enforce that they\n'
				'contain at least one part before they can be saved ?\n'
				'\n'
				'Part-less documents can be useful if you want to build\n'
				'up an index of, say, archived documents but do not\n'
				'want to scan in all the pages contained therein.'
			),
			option = u'horstspace.scan_index.allow_partless_documents',
			button_tooltips = [
				_('Yes, allow saving documents without any parts.'),
				_('No, require documents to have at least one part.')
			]
		)
	#----------------------------------------------
	def __on_configure_doc_uuid_dialog(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'After importing a new document do you\n'
				'want GNUmed to display the unique ID\n'
				'it auto-generated for that document ?\n'
				'\n'
				'This can be useful if you want to label the\n'
				'originals with that ID for later identification.'
			),
			option = u'horstspace.scan_index.show_doc_id',
			button_tooltips = [
				_('Yes, display the ID generated for the new document after importing.'),
				_('No, do not display the ID generated for the new document after importing.')
			]
		)
	#----------------------------------------------
	def __on_configure_doc_review_dialog(self, evt):

		def is_valid(value):
			try:
				value = int(value)
			except:
				return False, value
			if value not in [0, 1, 2]:
				return False, value
			return True, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed can show the document review dialog after\n'
				'calling the appropriate viewer for that document.\n'
				'\n'
				'Select the conditions under which you want\n'
				'GNUmed to do so:\n'
				'\n'
				' 0: never display the review dialog\n'
				' 1: always display the dialog\n'
				' 2: only if there is no previous review by me\n'
				'\n'
				'Note that if a viewer is configured to not block\n'
				'GNUmed during document display the review dialog\n'
				'will actually appear in parallel to the viewer.'
			),
			option = u'horstspace.document_viewer.review_after_display',
			bias = u'user',
			default_value = 2,
			validator = is_valid
		)
	#----------------------------------------------
	def __on_dicom_viewer(self, evt):

		if os.access('/Applications/OsiriX.app/Contents/MacOS/OsiriX', os.X_OK):
			gmShellAPI.run_command_in_shell('/Applications/OsiriX.app/Contents/MacOS/OsiriX', blocking=False)
			return

		for viewer in ['aeskulap', 'amide', 'xmedcon']:
			found, cmd = gmShellAPI.detect_external_binary(binary = viewer)
			if found:
				gmShellAPI.run_command_in_shell(cmd, blocking=False)
				return

		gmDispatcher.send(signal = 'statustext', msg = _('No DICOM viewer found.'), beep = True)
	#----------------------------------------------
	def __on_snellen(self, evt):
		cfg = gmSnellen.cSnellenCfgDlg()
		if cfg.ShowModal() != 0:
			return

		frame = gmSnellen.cSnellenChart (
			width = cfg.vals[0],
			height = cfg.vals[1],
			alpha = cfg.vals[2],
			mirr = cfg.vals[3],
			parent = None
		)
		frame.CentreOnScreen(wx.BOTH)
#		self.SetTopWindow(frame)
#		frame.Destroy = frame.DestroyWhenApp
		frame.Show(True)
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
	# Help / Debugging
	#----------------------------------------------
	def __on_save_screenshot(self, evt):

#		src_rect = self.GetRect()
#		sdc = wx.ScreenDC()						# whole screen area
#		mdc = wx.MemoryDC()
#		img = wx.EmptyBitmap(src_rect.width, src_rect.height)	# must be large enough for snapshot
#		mdc.SelectObject(img)
#		mdc.Blit (								# copy ...
#			0, 0,								# ... to here in the target ...
#			src_rect.width, src_rect.height,	# ... that much in ...
#			sdc,								# ... the source (the screen) ...
#			0, 0								# ... starting at
#		)

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
	def __on_invoke_inspector(self, evt):
		import wx.lib.inspection
		wx.lib.inspection.InspectionTool().Show()
	#----------------------------------------------
	def __on_display_bugtracker(self, evt):
		webbrowser.open (
			url = 'http://savannah.gnu.org/bugs/?group=gnumed',
			new = False,
			autoraise = True
		)
	#----------------------------------------------
	def __on_display_wiki(self, evt):
		webbrowser.open (
			url = 'http://wiki.gnumed.de',
			new = False,
			autoraise = True
		)
	#----------------------------------------------
	def __on_display_user_manual_online(self, evt):
		webbrowser.open (
			url = 'http://wiki.gnumed.de/bin/view/Gnumed/GnumedManual#UserGuideInManual',
			new = False,
			autoraise = True
		)
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
		name = os.path.basename(gmLog2._logfile_name)
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

		_log.warning('syncing log file for backup to [%s]', new_name)
		gmLog2.flush()
		shutil.copy2(gmLog2._logfile_name, new_name)
		gmDispatcher.send('statustext', msg = _('Log file backed up as [%s].') % new_name)
	#----------------------------------------------
	# GNUmed /
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
	def __on_edit_occupation(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add allergy. No active patient.'))
			return False
		gmDemographicsWidgets.edit_occupation()
		evt.Skip()
	#----------------------------------------------
	def __on_show_emr_summary(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot show EMR summary. No active patient.'))
			return False

		emr = pat.get_emr()
		dlg = wx.MessageDialog (
			parent = self,
			message = emr.format_statistics(),
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

		_log.debug('exporting EMR journal to [%s]' % fname)
		# instantiate exporter
		exporter = gmPatientExporter.cEMRJournalExporter()

		wx.BeginBusyCursor()
		try:
			fname = exporter.export_to_file(filename = fname)
		except:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Error exporting patient EMR as chronological journal.'),
				_('EMR journal export')
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

		_log.debug('exporting EMR journal to [%s]' % fname)
		# instantiate exporter
		exporter = gmPatientExporter.cMedistarSOAPExporter()
		wx.BeginBusyCursor()
		successful, fname = exporter.export_to_file(filename=fname)
		wx.EndBusyCursor()
		if not successful:
			gmGuiHelpers.gm_show_error (
				_('Error exporting progress notes of current encounter for MEDISTAR import.'),
				_('MEDISTAR progress notes export')
			)
			return False

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported todays progress notes into file [%s] for Medistar import.') % fname, beep=False)

		return True
	#----------------------------------------------
	def __on_load_external_patient(self, event):
		dbcfg = gmCfg.cCfgSQL()
		search_immediately = bool(dbcfg.get2 (
			option = 'patient_search.external_sources.immediately_search_if_single_source',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = 0
		))
		gmPatSearchWidgets.get_person_from_external_sources(parent=self, search_immediately=search_immediately, activate_immediately=True)
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
		# shut down backend notifications listener
		listener = gmBackendListener.gmBackendListener()
		listener.stop_thread()

		# shutdown application scripting listener
		if _scripting_listener is not None:
			try:
				_scripting_listener.shutdown()
			except:
				_log.exception('cannot stop scripting listener thread')

		gmDispatcher.disconnect(self._on_set_statustext, 'statustext')

		# signal imminent demise to plugins
		gmDispatcher.send(u'application_closing')

		# remember GUI size
		curr_width, curr_height = self.GetClientSizeTuple()
		_log.info('GUI size at shutdown: [%s:%s]' % (curr_width, curr_height))
		dbcfg = gmCfg.cCfgSQL()
		dbcfg.set (
			option = 'main.window.width',
			value = curr_width,
			workplace = gmSurgery.gmCurrentPractice().active_workplace
		)
		dbcfg.set (
			option = 'main.window.height',
			value = curr_height,
			workplace = gmSurgery.gmCurrentPractice().active_workplace
		)

		self.timer.Stop()

		sys.stdin = sys.__stdin__
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
	#----------------------------------------------
#	def OnIdle(self, event):
#		"""Here we can process any background tasks
#		"""
#		pass
	#----------------------------------------------
	def OnIconize(self, event):
		# FIXME: we should maximize the amount of title bar information here
		#_log.info('OnIconify')
		event.Skip()
	#----------------------------------------------
	def OnMaximize(self, event):
		# FIXME: we should change the amount of title bar information here
		#_log.info('OnMaximize')
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
			gmSurgery.gmCurrentPractice().active_workplace,
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

		self.__starting_up = True

		gmExceptionHandlingWidgets.install_wx_exception_handler()

		# set this so things like "wx.StandardPaths.GetDataDir()" work as expected
		self.SetAppName(u'gnumed')
#		self.SetVendor(u'The GNUmed Development Community.')
		paths = gmTools.gmPaths(app_name = 'gnumed', wx = wx)
		paths.init_paths(wx = wx, app_name = 'gnumed')

		if not self.__setup_cfg():
			return False

		self.__guibroker = gmGuiBroker.GuiBroker()
		self.__setup_platform()

		if not self.__establish_backend_connection():
			return False

		self.__check_for_updates()

		# FIXME: load last position from backend
		frame = gmTopLevelFrame(None, -1, _('GNUmed client'), (640,440))
		frame.CentreOnScreen(wx.BOTH)
		frame.Show(True)
		self.SetTopWindow(frame)

		if _cfg.get(option = 'slave'):
			if not self.__setup_scripting_listener():
				return False

		if _cfg.get(option = 'debug'):
			self.RedirectStdio()
			print "***** Redirecting STDOUT/STDERR to this log window *****"

		self.user_activity_detected = True
		self.elapsed_inactivity_slices = 0
		# FIXME: make configurable
		self.max_user_inactivity_slices = 15	# 15 * 2000ms == 30 seconds
		self.user_activity_timer = gmTimer.cTimer (
			callback = self._on_user_activity_timer_expired,
			delay = 2000			# hence a minimum of 2 and max of 3.999... seconds after which inactivity is detected
		)
		self.user_activity_timer.Start(oneShot=True)

		self.__register_events()

		wx.CallAfter(self._do_after_init)

		return True
	#----------------------------------------------
	def OnExit(self):
		"""Called:

		- after destroying all application windows and controls
		- before wx.Windows internal cleanup
		"""
		gmExceptionHandlingWidgets.uninstall_wx_exception_handler()
	#----------------------------------------------
	def _on_query_end_session(self, *args, **kwargs):
		print "unhandled event detected: QUERY_END_SESSION"
		_log.warning('unhandled event detected: QUERY_END_SESSION')
		_log.info('we should be saving ourselves from here')
	#----------------------------------------------
	def _on_end_session(self, *args, **kwargs):
		print "unhandled event detected: END_SESSION"
		_log.warning('unhandled event detected: END_SESSION')
	#----------------------------------------------
	def _on_app_activated(self, evt):
		if evt.GetActive():
			if self.__starting_up:
				gmHooks.run_hook_script(hook = u'app_activated_startup')
			else:
				gmHooks.run_hook_script(hook = u'app_activated')
		else:
			gmHooks.run_hook_script(hook = u'app_deactivated')

		evt.Skip()
	#----------------------------------------------
	def _on_user_activity(self, evt):
		self.user_activity_detected = True
		evt.Skip()
	#----------------------------------------------
	def _on_user_activity_timer_expired(self, cookie=None):

#		print "inactivity timer expired"
#		print "elapsed slices:", self.elapsed_inactivity_slices + 1
#		print "activity:", self.user_activity_detected

		if self.user_activity_detected:
			self.elapsed_inactivity_slices = 0
			self.user_activity_detected = False
			self.elapsed_inactivity_slices += 1
		else:
			if self.elapsed_inactivity_slices >= self.max_user_inactivity_slices:
#				print "User was inactive for 30 seconds."
				pass

		self.user_activity_timer.Start(oneShot = True)
	#----------------------------------------------
	# internal helpers
	#----------------------------------------------
	def _signal_debugging_monitor(*args, **kwargs):
		try:
			kwargs['originated_in_database']
			print '==> got notification from database "%s":' % kwargs['signal']
		except KeyError:
			print '==> received signal from client: "%s"' % kwargs['signal']

		del kwargs['signal']
		for key in kwargs.keys():
			print '    [%s]: %s' % (key, kwargs[key])
	#----------------------------------------------
	def _do_after_init(self):
		self.__starting_up = False
		gmClinicalRecord.set_func_ask_user(a_func = gmEMRStructWidgets.ask_for_encounter_continuation)
		self.__guibroker['horstspace.top_panel'].patient_selector.SetFocus()
		gmHooks.run_hook_script(hook = u'startup-after-GUI-init')
	#----------------------------------------------
	def __register_events(self):
		wx.EVT_QUERY_END_SESSION(self, self._on_query_end_session)
		wx.EVT_END_SESSION(self, self._on_end_session)
		self.Bind(wx.EVT_ACTIVATE_APP, self._on_app_activated)
		#You can bind your app to wx.EVT_ACTIVATE_APP which will fire when your app
		#get/looses focus, or you can wx.EVT_ACTIVATE with any of your toplevel
		#windows and call evt.GetActive() in the handler to see whether it is
		#gaining or loosing focus.

		self.Bind(wx.EVT_MOUSE_EVENTS, self._on_user_activity)
		self.Bind(wx.EVT_KEY_DOWN, self._on_user_activity)

		if _cfg.get(option = 'debug'):
			gmDispatcher.connect(receiver = self._signal_debugging_monitor)
	#----------------------------------------------
	def __check_for_updates(self):

		dbcfg = gmCfg.cCfgSQL()

		do_check = bool(dbcfg.get2 (
			option = u'horstspace.update.autocheck_at_startup',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = True
		))

		if not do_check:
			return

		check_for_updates()
	#----------------------------------------------
	def __establish_backend_connection(self):
		"""Handle all the database related tasks necessary for startup."""

		# log on
		from Gnumed.wxpython import gmAuthWidgets
		override = _cfg.get(option = '--override-schema-check', source_order = [('cli', 'return')])
		connected = gmAuthWidgets.connect_to_database (
			expected_version = expected_db_ver,
			require_version = not override,
			client_version = current_client_ver
		)
		if not connected:
			_log.warning("Login attempt unsuccessful. Can't run GNUmed without database connection")
			return False

		# check account <-> staff member association
		try:
			global _provider
			_provider = gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())
		except gmExceptions.ConstructorError, ValueError:
			account = gmPG2.get_current_user()
			_log.exception('DB account [%s] cannot be used as a GNUmed staff login', account)
			msg = _(
				'The database account [%s] cannot be used as a\n'
				'staff member login for GNUmed. There was an\n'
				'error retrieving staff details for it.\n\n'
				'Please ask your administrator for help.\n'
			) % account
			gmGuiHelpers.gm_show_error(msg, _('Checking access permissions'))
			return False

		# improve exception handler setup
		tmp = '%s%s %s (%s = %s)' % (
			gmTools.coalesce(_provider['title'], ''),
			_provider['firstnames'],
			_provider['lastnames'],
			_provider['short_alias'],
			_provider['db_user']
		)
		gmExceptionHandlingWidgets.set_staff_name(staff_name = tmp)

		# display database banner
		surgery = gmSurgery.gmCurrentPractice()
		msg = surgery.db_logon_banner
		if msg != u'':
			gmGuiHelpers.gm_show_info(msg, _('Verifying database'))

		# check database language settings
		self.__set_db_lang()

		return True
	#----------------------------------------------
	def __setup_cfg(self):

		paths = gmTools.gmPaths()

		candidates = []
		explicit_file = _cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
		if explicit_file is not None:
			candidates.append(explicit_file)
		# provide a few fallbacks in the event the --conf-file isn't writable
		candidates.append(os.path.join(paths.user_config_dir, 'gnumed.conf'))
		candidates.append(os.path.join(paths.local_base_dir, 'gnumed.conf'))
		candidates.append(os.path.join(paths.working_dir, 'gnumed.conf'))

		for candidate in candidates:
			try:
				open(candidate, 'a+').close()
				_cfg.set_option(option = u'user_preferences_file', value = candidate)
				break
			except IOError:
				continue

		if _cfg.get(option = u'user_preferences_file') is None:
			msg = _(
				'Cannot find configuration file in any of:\n'
				'\n'
				' %s\n'
				'You may need to use the comand line option\n'
				'\n'
				'	--conf-file=<FILE>'
			) % '\n '.join(candidates)
			gmGuiHelpers.gm_show_error(msg, _('Checking configuration files'))
			return False

		return True
	#----------------------------------------------
	def __setup_scripting_listener(self):

		from socket import error as SocketError
		from Gnumed.pycommon import gmScriptingListener
		from Gnumed.wxpython import gmMacro

		slave_personality = gmTools.coalesce (
			_cfg.get (
				group = u'workplace',
				option = u'slave personality',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('user', 'return'),
					('system', 'return')
				]
		 	),
			u'gnumed-client'
		)

		# FIXME: handle port via /var/run/
		port = gmTools.coalesce (
			int(_cfg.get (
				group = u'workplace',
				option = u'xml-rpc port',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('user', 'return'),
					('system', 'return')
				]
			)),
			9999
		)

		macro_executor = gmMacro.cMacroPrimitives(personality = slave_personality)
		global _scripting_listener
		try:
			_scripting_listener = gmScriptingListener.cScriptingListener(port = port, macro_executor = macro_executor)
		except SocketError, e:
			_log.exception('cannot start GNUmed XML-RPC server')
			gmGuiHelpers.gm_show_error (
				aMessage = (
					'Cannot start the GNUmed server:\n'
					'\n'
					' [%s]'
				) % e,
				aTitle = _('GNUmed startup')
			)
			return False

		_log.info('slave mode personality is [%s]' % slave_personality)
		return True
	#----------------------------------------------
	def __setup_platform(self):

		import wx.lib.colourdb
		wx.lib.colourdb.updateColourDB()

		if wx.Platform == '__WXMSW__':
			_log.info('running on MS Windows')
		elif wx.Platform == '__WXGTK__':
			_log.info('running on GTK (probably Linux)')
		elif wx.Platform == '__WXMAC__':
			_log.info('running on Mac OS')
		else:
			_log.info('running on an unknown platform (%s)' % wx.Platform)
	#----------------------------------------------
	def __set_db_lang(self):
		if gmI18N.system_locale is None or gmI18N.system_locale == '':
			_log.warning("system locale is undefined (probably meaning 'C')")
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
			_log.debug("database locale currently not set")
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
			_log.debug("current database locale: [%s]" % db_lang)
			# check if we can match up system and db language somehow
			if db_lang == gmI18N.system_locale_level['full']:
				_log.debug('Database locale (%s) up to date.' % db_lang)
				return True
			if db_lang == gmI18N.system_locale_level['country']:
				_log.debug('Database locale (%s) matches system locale (%s) at country level.' % (db_lang, gmI18N.system_locale))
				return True
			if db_lang == gmI18N.system_locale_level['language']:
				_log.debug('Database locale (%s) matches system locale (%s) at language level.' % (db_lang, gmI18N.system_locale))
				return True
			# no match
			_log.warning('database locale [%s] does not match system locale [%s]' % (db_lang, gmI18N.system_locale))

		# returns either None or a locale string
		ignored_sys_lang = _cfg.get (
			group = u'backend',
			option = u'ignored mismatching system locale',
			source_order = [('user', 'return'), ('local', 'return')]
		)
		# are we to ignore *this* mismatch ?
		if gmI18N.system_locale == ignored_sys_lang:
			_log.info('configured to ignore system-to-database locale mismatch')
			return True
		# no, so ask user
		if not gmGuiHelpers.gm_show_question (
			aMessage = msg,
			aTitle = _('checking database language settings'),
		):
			_log.info('User did not want to set database locale. Ignoring mismatch next time.')
#			comment = [
#				"If the system locale matches this value a mismatch",
#				"with the database locale will be ignored.",
#				"Remove this option if you want to stop ignoring mismatches.",
#			]
			gmCfg2.set_option_in_INI_file (
				filename = _cfg.get(option = 'user_preferences_file'),
				group = 'backend',
				option = 'ignored mismatching system locale',
				value = gmI18N.system_locale
			)
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
					_log.debug("Successfully set database language to [%s]." % lang)
				else:
					_log.error('Cannot set database language to [%s].' % lang)
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

	# create an instance of our GNUmed main application
	# - do not redirect stdio (yet)
	# - allow signals to be delivered
	app = gmApp(redirect = False, clearSigInt = False)
	_log.info('display: %s:%s' % (wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X), wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)))
	app.MainLoop()
#==============================================================================
# Main
#==============================================================================
if __name__ == '__main__':

	from GNUmed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	# console is Good(tm)
	_log.info('Starting up as main module.')
	main()

#==============================================================================
# $Log: gmGuiMain.py,v $
# Revision 1.404  2008-05-26 13:31:34  ncq
# - "properly" set current branch
#
# Revision 1.403  2008/05/26 12:09:37  ncq
# - some cleanup
# - check_for_updates and call that from menu item
#   and startup process
# - menu items for configuring update check
#
# Revision 1.402  2008/05/21 15:53:06  ncq
# - add initial support for update notifier
#
# Revision 1.401  2008/05/20 16:44:44  ncq
# - clean up OnInit
# - start listening to user inactivity
#
# Revision 1.400  2008/05/19 16:24:07  ncq
# - let EMR format its summary itself
#
# Revision 1.399  2008/05/13 14:12:55  ncq
# - exc handling adjustments
#
# Revision 1.398  2008/04/29 18:30:42  ncq
# - promote workplace logging to info
#
# Revision 1.397  2008/04/28 13:32:39  ncq
# - take approprate action on db maintenance warning
#
# Revision 1.396  2008/04/26 21:36:42  ncq
# - fix faulty variable
# - when debugging explicitely print into log window
#   immediately after creation so focus isn't taken
#   away at a later and inconvenient time
#
# Revision 1.395  2008/04/16 20:39:39  ncq
# - working versions of the wxGlade code and use it, too
# - show client version in login dialog
#
# Revision 1.394  2008/04/11 12:28:30  ncq
# - abort if there's no user preferences config file whatsoever
#
# Revision 1.393  2008/03/29 16:09:53  ncq
# - improved comments
# - wx version checking for faulty
# - enhance color db
# - make sure at least one user preferences file candidate is writable
#
# Revision 1.392  2008/03/09 20:16:14  ncq
# - load_patient_* -> get_person_*
#
# Revision 1.391  2008/03/06 18:34:08  ncq
# - better error handling around IFAP access
#
# Revision 1.390  2008/03/05 22:38:26  ncq
# - set encounter type to chart review on docs-only encounters
#
# Revision 1.389  2008/02/29 23:46:59  ncq
# - new debugging option: widget inspector (needs 2.8)
#
# Revision 1.388  2008/02/25 17:37:16  ncq
# - use new-style logging
#
# Revision 1.387  2008/01/30 14:07:49  ncq
# - improved wording of partless document option
#
# Revision 1.386  2008/01/27 21:15:20  ncq
# - configure partless docs
# - label changes
# - use gmCfg2 for setting options
#
# Revision 1.385  2008/01/22 12:23:39  ncq
# - reorder menus as per list discussion
# - wiki link/online user manual link in help menu
#
# Revision 1.384  2008/01/16 19:40:22  ncq
# - menu item renaming "Upper lower" per Jim
# - more config options
# - add Aeskulap to DICOM viewers and better detection of those
#
# Revision 1.383  2008/01/13 01:19:11  ncq
# - don't crash on inaccessible IFAP transfer file
# - doc management configuration
# - restore Stdio on exit
# - set staff name for exception handling
#
# Revision 1.382  2008/01/07 19:53:00  ncq
# - misspelled variable fix
#
# Revision 1.381  2008/01/05 22:30:30  ncq
# - some wording cleanup for menu items
#
# Revision 1.380  2007/12/26 22:45:46  ncq
# - tuples separate by , not :
#
# Revision 1.379  2007/12/23 22:03:59  ncq
# - no more gmCLI
#
# Revision 1.378  2007/12/23 20:28:44  ncq
# - use gmCfg2, less gmCLI use
# - cleanup
# - less guibroker use
#
# Revision 1.377  2007/12/12 16:24:32  ncq
# - cleanup
#
# Revision 1.376  2007/12/11 12:49:26  ncq
# - explicit signal handling
#
# Revision 1.375  2007/12/06 10:47:14  ncq
# - submenu EMR -> History Taking
#
# Revision 1.374  2007/12/04 18:38:04  ncq
# - edit occupation via menu
#
# Revision 1.373  2007/12/04 16:16:27  ncq
# - use gmAuthWidgets
#
# Revision 1.372  2007/12/04 15:20:31  ncq
# - assume default slave personality "gnumed-client" if not set
#
# Revision 1.371  2007/12/03 21:06:00  ncq
# - streamline OnInit()
#
# Revision 1.370  2007/11/28 22:36:40  ncq
# - listen on identity/name changes for current patient
#
# Revision 1.369  2007/11/23 23:33:50  ncq
# - can now configure workplace plugins
#
# Revision 1.368  2007/11/03 17:57:19  ncq
# - call hook on request_user_attention and app window actication/deactivation
# - call hook on client init startup
# - hence no more hardcoded checking external sources on startup
#   as users can do it from the hook if needed, hook example
#   updated thusly
# - hence to check-sources-on-startup configuration needed
#   anymore
#
# Revision 1.367  2007/11/02 13:59:04  ncq
# - teach client about its own version
# - log client/db version
# - a bunch of config options
# - listen to request_user_attention
# - listen to APP activation/deactivation
#
# Revision 1.366  2007/10/25 20:11:29  ncq
# - configure initial plugin after patient search
#
# Revision 1.365  2007/10/25 16:41:04  ncq
# - a whole bunch of config options
#
# Revision 1.364  2007/10/25 12:20:36  ncq
# - improve db origination detection for signals in signal monitor
#
# Revision 1.363  2007/10/23 21:41:42  ncq
# - on --debug monitor signals
#
# Revision 1.362  2007/10/23 21:25:32  ncq
# - shutdown backend notification listener on exit
#
# Revision 1.361  2007/10/21 20:19:26  ncq
# - add more config options
#
# Revision 1.360  2007/10/19 21:20:17  ncq
# - init *all* image handler
#
# Revision 1.359  2007/10/19 12:51:39  ncq
# - configure/do quick external patient search
# - add Snellen chart
#
# Revision 1.358  2007/10/11 12:10:52  ncq
# - add initial updateTitle() call
# - reorganize menus a bit
# - add gnumed / config / emr / encounter / edit-before-patient-change
# - improve logic in encounter editor showing before patient change
#
# Revision 1.357  2007/10/08 12:49:48  ncq
# - active_workplace now property of gmPractice
# - rearrange options manage
# - allow editing ifap startup command
#
# Revision 1.356  2007/09/20 21:30:39  ncq
# - cleanup
# - allow setting db logon banner
#
# Revision 1.355  2007/09/20 19:35:14  ncq
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
