# -*- coding: utf-8 -*-

"""GNUmed GUI client.

This contains the GUI application framework and main window
of the all signing all dancing GNUmed Python Reference
client. It relies on the <gnumed.py> launcher having set up
the non-GUI-related runtime environment.

copyright: authors
"""
#==============================================================================
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import sys
import time
import os
import os.path
import datetime as pyDT
import shutil
import logging
import urllib.request
import subprocess
import glob

_log = logging.getLogger('gm.main')


# 3rd party libs: wxPython
try:
	import wx
	_log.info('wxPython version loaded: %s %s' % (wx.VERSION_STRING, wx.PlatformInfo))
except ImportError:
	_log.exception('cannot import wxPython')
	print('GNUmed startup: Cannot import wxPython library.')
	print('GNUmed startup: Make sure wxPython is installed.')
	print('CRITICAL ERROR: Error importing wxPython. Halted.')
	raise

# do this check just in case, so we can make sure
# py2exe and friends include the proper version, too
version = int('%s%s' % (wx.MAJOR_VERSION, wx.MINOR_VERSION))
if (version < 40) or ('unicode' not in wx.PlatformInfo):
	print('GNUmed startup: Unsupported wxPython version (%s: %s).' % (wx.VERSION_STRING, wx.PlatformInfo))
	print('GNUmed startup: wxPython 4.0+ with unicode support is required.')
	print('CRITICAL ERROR: Proper wxPython version not found. Halted.')
	raise ValueError('wxPython 4.0+ with unicode support not found')


# GNUmed libs
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmGuiBroker
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmBackendListener
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmConnectionPool
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmWorkerThread

from Gnumed.business import gmPerson
from Gnumed.business import gmClinicalRecord
from Gnumed.business import gmPraxis
from Gnumed.business import gmEncounter
from Gnumed.business import gmArriba
from Gnumed.business import gmStaff
from Gnumed.business import gmAutoFileImport

from Gnumed.exporters import gmPatientExporter

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmHorstSpace
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmPersonCreationWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmExceptionHandlingWidgets
from Gnumed.wxpython import gmNarrativeWorkflows
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmSubstanceIntakeWidgets
from Gnumed.wxpython import gmStaffWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmTimer
from Gnumed.wxpython import gmMeasurementWidgets
from Gnumed.wxpython import gmMedicationWorkflows
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmSnellen
from Gnumed.wxpython import gmVaccWidgets
from Gnumed.wxpython import gmI18nWidgets
from Gnumed.wxpython import gmCodingWidgets
from Gnumed.wxpython import gmOrganizationWidgets
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmFamilyHistoryWidgets
from Gnumed.wxpython import gmDataPackWidgets
from Gnumed.wxpython import gmContactWidgets
from Gnumed.wxpython import gmAddressWidgets
from Gnumed.wxpython import gmBillingWidgets
from Gnumed.wxpython import gmKeywordExpansionWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets
from Gnumed.wxpython import gmPraxisWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmAutoHintWidgets
from Gnumed.wxpython import gmPregWidgets
from Gnumed.wxpython import gmExternalCareWidgets
from Gnumed.wxpython import gmHabitWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets
from Gnumed.wxpython import gmATCWidgets
from Gnumed.wxpython import gmLOINCWidgets
from Gnumed.wxpython import gmVisualProgressNoteWidgets
from Gnumed.wxpython import gmHospitalStayWidgets
from Gnumed.wxpython import gmProcedureWidgets
from Gnumed.wxpython import gmExportAreaWidgets


_cfg = gmCfgINI.gmCfgData()
_provider = None
_scripting_listener = None
_original_wxEndBusyCursor = None
if __name__ == '__main__':
	_ = lambda x:x

#==============================================================================
class cLog_wx2gm(wx.Log):
	# redirect wx.LogXXX() calls to python logging log
	def DoLogTextAtLevel(self, level, msg):
		_log.log(level, msg)

__wxlog = cLog_wx2gm()
_log.info('redirecting wx.Log to [%s]', __wxlog)
wx.Log.SetActiveTarget(__wxlog)
#wx.LogDebug('test message')

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
		wx.Frame.__init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE)

		self.__setup_font()

		self.__gb = gmGuiBroker.GuiBroker()
		self.__pre_exit_callbacks = []
		self.bar_width = -1
		self.menu_id2plugin = {}

		_log.info('workplace is >>>%s<<<', gmPraxis.gmCurrentPraxisBranch().active_workplace)

		self.setup_statusbar()
		self.SetStatusText(_('You are logged in as %s%s.%s (%s). DB account <%s>.') % (
			gmTools.coalesce(_provider['title'], ''),
			_provider['firstnames'][:1],
			_provider['lastnames'],
			_provider['short_alias'],
			_provider['db_user']
		))
		self.__setup_main_menu()

		self.__set_window_title_template()
		self.__update_window_title()

		#icon_bundle = wx.IconBundle()
		#icon_bundle.AddIcon(wx.Icon("my_icon_16_16.ico", wx.BITMAP_TYPE_ICO))
		#icon_bundle.AddIcon(wx.Icon("my_icon_32_32.ico", wx.BITMAP_TYPE_ICO))
		#self.SetIcons(icon_bundle)
		self.SetIcon(gmTools.get_icon(wx = wx))

		self.__register_events()

		self.LayoutMgr = gmHorstSpace.cHorstSpaceLayoutMgr(self, -1)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.LayoutMgr, 10, wx.EXPAND | wx.ALL, 1)

		self.SetAutoLayout(True)
		self.SetSizerAndFit(self.vbox)

		# don't allow the window to get too small
		# setsizehints only allows minimum size, therefore window can't become small enough
		# effectively we need the font size to be configurable according to screen size
		#self.vbox.SetSizeHints(self)
		self.__set_GUI_size()

	#----------------------------------------------
	def __setup_font(self):

		font = self.GetFont()
		_log.debug('system default font is [%s] (%s)', font.GetNativeFontInfoUserDesc(), font.GetNativeFontInfoDesc())

		desired_font_face = _cfg.get (
			group = 'workplace',
			option = 'client font',
			source_order = [
				('explicit', 'return'),
				('workbase', 'return'),
				('local', 'return'),
				('user', 'return'),
				('system', 'return')
			]
		)

		fonts2try = []
		if desired_font_face is not None:
			_log.info('client is configured to use font [%s]', desired_font_face)
			fonts2try.append(desired_font_face)

		if wx.Platform == '__WXMSW__':
			sane_font_face = 'Noto Sans'
			_log.info('MS Windows: appending fallback font candidate [%s]', sane_font_face)
			fonts2try.append(sane_font_face)
			sane_font_face = 'DejaVu Sans'
			_log.info('MS Windows: appending fallback font candidate [%s]', sane_font_face)
			fonts2try.append(sane_font_face)

		if len(fonts2try) == 0:
			return

		for font_face in fonts2try:
			success = font.SetFaceName(font_face)
			if success:
				self.SetFont(font)
				_log.debug('switched font to [%s] (%s)', font.GetNativeFontInfoUserDesc(), font.GetNativeFontInfoDesc())
				return
			font = self.GetFont()
			_log.error('cannot switch font from [%s] (%s) to [%s]', font.GetNativeFontInfoUserDesc(), font.GetNativeFontInfoDesc(), font_face)

		return

	#----------------------------------------------
	def __set_GUI_size(self):
		"""Try to get previous window size from backend."""
		width = gmCfgDB.get4workplace (
			option = 'main.window.width',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = 800
		)
		height = gmCfgDB.get4workplace (
			option = 'main.window.height',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = 600
		)
		_log.debug('previous GUI size [%sx%s]', width, height)
		pos_x = gmCfgDB.get4workplace (
			option = 'main.window.position.x',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = 0
		)
		pos_y = gmCfgDB.get4workplace (
			option = 'main.window.position.y',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = 0
		)
		_log.debug('previous GUI position [%s:%s]', pos_x, pos_y)

		curr_disp_width = wx.DisplaySize()[0]
		curr_disp_height = wx.DisplaySize()[1]
		# max size = display
		if width > curr_disp_width:
			_log.debug('adjusting GUI width from %s to display width %s', width, curr_disp_width)
			width = curr_disp_width
		if height > curr_disp_height:
			_log.debug('adjusting GUI height from %s to display height %s', height, curr_disp_height)
			height = curr_disp_height
		# min size = 100x100
		if width < 100:
			_log.debug('adjusting GUI width to minimum of 100 pixel')
			width = 100
		if height < 100:
			_log.debug('adjusting GUI height to minimum of 100 pixel')
			height = 100
		_log.info('setting GUI geom to [%sx%s] @ [%s:%s]', width, height, pos_x, pos_y)

		#self.SetClientSize(wx.Size(width, height))
		self.SetSize(wx.Size(width, height))
		self.SetPosition(wx.Point(pos_x, pos_y))

	#----------------------------------------------
	def __setup_main_menu(self):
		"""Create the main menu entries.

		Individual entries are farmed out to the modules.

		menu item template:

		item = menu_*.Append(-1)
		self.Bind(wx.EVT_MENU, self.__on_*, item)
		"""
		global wx
		self.mainmenu = wx.MenuBar()
		self.__gb['main.mainmenu'] = self.mainmenu

		# -- menu "GNUmed" -----------------
		menu_gnumed = wx.Menu()
		self.menu_plugins = wx.Menu()
		menu_gnumed.Append(wx.NewId(), _('&Go to plugin ...'), self.menu_plugins)
		item = menu_gnumed.Append(-1, _('Check for updates'), _('Check for new releases of the GNUmed client.'))
		self.Bind(wx.EVT_MENU, self.__on_check_for_updates, item)
		item = menu_gnumed.Append(-1, _('Announce downtime'), _('Announce database maintenance downtime to all connected clients.'))
		self.Bind(wx.EVT_MENU, self.__on_announce_maintenance, item)
		menu_gnumed.AppendSeparator()

		# GNUmed / Preferences
		menu_config = wx.Menu()

		item = menu_config.Append(-1, _('All options'), _('List all options as configured in the database.'))
		self.Bind(wx.EVT_MENU, self.__on_list_configuration, item)

		# GNUmed / Preferences / Database
		menu_cfg_db = wx.Menu()
		item = menu_cfg_db.Append(-1, _('Language'), _('Configure the database language'))
		self.Bind(wx.EVT_MENU, self.__on_configure_db_lang, item)
		item = menu_cfg_db.Append(-1, _('Welcome message'), _('Configure the database welcome message (all users).'))
		self.Bind(wx.EVT_MENU, self.__on_configure_db_welcome, item)
		menu_config.Append(wx.NewId(), _('Database ...'), menu_cfg_db)

		# GNUmed / Preferences / Client
		menu_cfg_client = wx.Menu()
		item = menu_cfg_client.Append(-1, _('Export chunk size'), _('Configure the chunk size used when exporting BLOBs from the database.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_export_chunk_size, item)
		item = menu_cfg_client.Append(-1, _('Email address'), _('The email address of the user for sending bug reports, etc.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_user_email, item)
		menu_config.Append(wx.NewId(), _('Client parameters ...'), menu_cfg_client)

		# GNUmed / Preferences / UI
		menu_cfg_ui = wx.Menu()
		item = menu_cfg_ui.Append(-1, _('Medication measurements'), _('Select the measurements panel to show in the medications plugin.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_meds_lab_pnl, item)
		item = menu_cfg_ui.Append(-1, _('General measurements'), _('Select the measurements panel to show in the top pane.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_top_lab_pnl, item)

		# gnumed / config / ui / docs
		menu_cfg_doc = wx.Menu()
		item = menu_cfg_doc.Append(-1, _('Review dialog'), _('Configure review dialog after document display.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_doc_review_dialog, item)
		item = menu_cfg_doc.Append(-1, _('UUID display'), _('Configure unique ID dialog on document import.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_doc_uuid_dialog, item)
		item = menu_cfg_doc.Append(-1, _('Empty documents'), _('Whether to allow saving documents without parts.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_partless_docs, item)
		item = menu_cfg_doc.Append(-1, _('Generate UUID'), _('Whether to generate UUIDs for new documents.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_generate_doc_uuid, item)
		menu_cfg_ui.Append(wx.NewId(), _('Document handling ...'), menu_cfg_doc)

		# gnumed / config / ui / updates
		menu_cfg_update = wx.Menu()
		item = menu_cfg_update.Append(-1, _('Auto-check'), _('Whether to auto-check for updates at startup.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_update_check, item)
		item = menu_cfg_update.Append(-1, _('Check scope'), _('When checking for updates, consider latest branch, too ?'))
		self.Bind(wx.EVT_MENU, self.__on_configure_update_check_scope, item)
		item = menu_cfg_update.Append(-1, _('URL'), _('The URL to retrieve version information from.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_update_url, item)
		menu_cfg_ui.Append(wx.NewId(), _('Update handling ...'), menu_cfg_update)

		# gnumed / config / ui / patient
		menu_cfg_pat_search = wx.Menu()
		item = menu_cfg_pat_search.Append(-1, _('Birthday reminder'), _('Configure birthday reminder proximity interval.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_dob_reminder_proximity, item)
		item = menu_cfg_pat_search.Append(-1, _('Immediate source activation'), _('Configure immediate activation of single external person.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_quick_pat_search, item)
		item = menu_cfg_pat_search.Append(-1, _('Initial plugin'), _('Configure which plugin to show right after person activation.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_initial_pat_plugin, item)
		item = menu_cfg_pat_search.Append(-1, _('Default region'), _('Configure the default region for person creation.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_default_region, item)
		item = menu_cfg_pat_search.Append(-1, _('Default country'), _('Configure the default country for person creation.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_default_country, item)
		menu_cfg_ui.Append(wx.NewId(), _('Person ...'), menu_cfg_pat_search)

		# gnumed / config / ui / soap handling
		menu_cfg_soap_editing = wx.Menu()
		item = menu_cfg_soap_editing.Append(-1, _('Multiple new episodes'), _('Configure opening multiple new episodes on a patient at once.'))
		self.Bind(wx.EVT_MENU, self.__on_allow_multiple_new_episodes, item)
		item = menu_cfg_soap_editing.Append(-1, _('Auto-open editors'), _('Configure auto-opening editors for recent problems.'))
		self.Bind(wx.EVT_MENU, self.__on_allow_auto_open_episodes, item)
		item = menu_cfg_soap_editing.Append(-1, _('SOAP fields'), _('Configure SOAP editor - individual SOAP fields vs text editor like'))
		self.Bind(wx.EVT_MENU, self.__on_use_fields_in_soap_editor, item)
		menu_cfg_ui.Append(wx.NewId(), _('Progress notes handling ...'), menu_cfg_soap_editing)

		# gnumed / config / External tools
		menu_cfg_ext_tools = wx.Menu()
#		item = menu_cfg_ext_tools.Append(-1, _('IFAP command'), _('Set the command to start IFAP.'))
#		self.Bind(wx.EVT_MENU, self.__on_configure_ifap_cmd, item)
		item = menu_cfg_ext_tools.Append(-1, _('MI/stroke risk calc cmd'), _('Set the command to start the CV risk calculator.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_acs_risk_calculator_cmd, item)
		item = menu_cfg_ext_tools.Append(-1, _('OOo startup time'), _('Set the time to wait for OpenOffice to settle after startup.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_ooo_settle_time, item)
		item = menu_cfg_ext_tools.Append(-1, _('Measurements URL'), _('URL for measurements encyclopedia.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_measurements_url, item)
		item = menu_cfg_ext_tools.Append(-1, _('Drug data source'), _('Select the drug data source.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_drug_data_source, item)
#		item = menu_cfg_ext_tools.Append(-1, _('FreeDiams path'), _('Set the path for the FreeDiams binary.'))
#		self.Bind(wx.EVT_MENU, self.__on_configure_freediams_cmd, item)
		item = menu_cfg_ext_tools.Append(-1, _('ADR URL (Meds)'), _('URL for reporting Adverse Drug Reactions.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_drug_ADR_url, item)
		item = menu_cfg_ext_tools.Append(-1, _('ADR URL (Vx)'), _('URL for reporting Adverse Drug Reactions to *vaccines*.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_vaccine_ADR_url, item)
		item = menu_cfg_ext_tools.Append(-1, _('Vacc plans URL'), _('URL for vaccination plans.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_vaccination_plans_url, item)
		item = menu_cfg_ext_tools.Append(-1, _('Visual SOAP editor'), _('Set the command for calling the visual progress note editor.'))
		self.Bind(wx.EVT_MENU, self.__on_configure_visual_soap_cmd, item)
		menu_config.Append(wx.NewId(), _('External tools ...'), menu_cfg_ext_tools)

		# gnumed / config / billing
		menu_cfg_bill = wx.Menu()
		item = menu_cfg_bill.Append(-1, _('Invoice ID template'), _('Set the template for generating invoice IDs.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_invoice_id_template, item)
		item = menu_cfg_bill.Append(-1, _('Invoice template (no VAT)'), _('Select the template for printing an invoice without VAT.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_invoice_template_no_vat, item)
		item = menu_cfg_bill.Append(-1, _('Invoice template (with VAT)'), _('Select the template for printing an invoice with VAT.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_invoice_template_with_vat, item)
		item = menu_cfg_bill.Append(-1, _('Catalogs URL'), _('URL for billing catalogs (schedules of fees).'))
		self.Bind(wx.EVT_MENU, self.__on_configure_billing_catalogs_url, item)

		#  gnumed / config / emr
		menu_cfg_emr = wx.Menu()
		item = menu_cfg_emr.Append(-1, _('Medication list template'), _('Select the template for printing a medication list.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_medication_list_template, item)
		item = menu_cfg_emr.Append(-1, _('Prescription mode'), _('Select the default mode for creating a prescription.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_prescription_mode, item)
		item = menu_cfg_emr.Append(-1, _('Prescription template'), _('Select the template for printing a prescription.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_prescription_template, item)
		item = menu_cfg_emr.Append(-1, _('Default Gnuplot template'), _('Select the default template for plotting test results.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_default_gnuplot_template, item)
		item = menu_cfg_emr.Append(-1, _('Fallback provider'), _('Select the doctor to fall back to for patients without a primary provider.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_fallback_primary_provider, item)

		# gnumed / config / emr / encounter
		menu_cfg_encounter = wx.Menu()
		item = menu_cfg_encounter.Append(-1, _('Edit before patient change'), _('Edit encounter details before change of patient.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_enc_pat_change, item)
		item = menu_cfg_encounter.Append(-1, _('Minimum duration'), _('Minimum duration of an encounter.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_enc_min_ttl, item)
		item = menu_cfg_encounter.Append(-1, _('Maximum duration'), _('Maximum duration of an encounter.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_enc_max_ttl, item)
		item = menu_cfg_encounter.Append(-1, _('Minimum empty age'), _('Minimum age of an empty encounter before considering for deletion.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_enc_empty_ttl, item)
		item = menu_cfg_encounter.Append(-1, _('Default type'), _('Default type for new encounters.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_enc_default_type, item)
		menu_cfg_emr.Append(wx.NewId(), _('Encounter ...'), menu_cfg_encounter)

		# gnumed / config / emr / episode
		menu_cfg_episode = wx.Menu()
		item = menu_cfg_episode.Append(-1, _('Dormancy'), _('Maximum length of dormancy after which an episode will be considered closed.'))
		self.Bind(wx.EVT_MENU, self.__on_cfg_epi_ttl, item)
		menu_cfg_emr.Append(wx.NewId(), _('Episode ...'), menu_cfg_episode)

		menu_config.Append(wx.NewId(), _('User interface ...'), menu_cfg_ui)
		menu_config.Append(wx.NewId(), _('EMR ...'), menu_cfg_emr)
		menu_config.Append(wx.NewId(), _('Billing ...'), menu_cfg_bill)
		menu_gnumed.Append(wx.NewId(), _('Preferences ...'), menu_config)

		#  gnumed / master data
		menu_master_data = wx.Menu()
		item = menu_master_data.Append(-1, _('Manage lists'), _('Manage various lists of master data.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_master_data, item)
		item = menu_master_data.Append(-1, _('Manage praxis'), _('Manage your praxis branches.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_praxis, item)
		item = menu_master_data.Append(-1, _('Install data packs'), _('Install reference data from data packs.'))
		self.Bind(wx.EVT_MENU, self.__on_install_data_packs, item)
		item = menu_master_data.Append(-1, _('Update ATC'), _('Install ATC reference data.'))
		self.Bind(wx.EVT_MENU, self.__on_update_atc, item)
		item = menu_master_data.Append(-1, _('Update LOINC'), _('Download and install LOINC reference data.'))
		self.Bind(wx.EVT_MENU, self.__on_update_loinc, item)
		item = menu_master_data.Append(-1, _('Create fake vaccines'), _('Re-create fake generic vaccines.'))
		self.Bind(wx.EVT_MENU, self.__on_generate_vaccines, item)
		menu_gnumed.Append(wx.NewId(), _('&Master data ...'), menu_master_data)

		#  gnumed / users
		menu_users = wx.Menu()
		item = menu_users.Append(-1, _('&Add user'), _('Add a new GNUmed user'))
		self.Bind(wx.EVT_MENU, self.__on_add_new_staff, item)
		item = menu_users.Append(-1, _('&Edit users'), _('Edit the list of GNUmed users'))
		self.Bind(wx.EVT_MENU, self.__on_edit_staff_list, item)
		item = menu_users.Append(-1, _('&Change DB owner PWD'), _('Change the password of the GNUmed database owner'))
		self.Bind(wx.EVT_MENU, self.__on_edit_gmdbowner_password, item)
		menu_gnumed.Append(wx.NewId(), _('&Users ...'), menu_users)

		menu_gnumed.AppendSeparator()

		item = menu_gnumed.Append(wx.ID_EXIT, _('E&xit\tAlt-X'), _('Close this GNUmed client.'))
		self.Bind(wx.EVT_MENU, self.__on_exit_gnumed, item)

		self.mainmenu.Append(menu_gnumed, '&GNUmed')

		# -- menu "Person" ---------------------------
		menu_person = wx.Menu()

		item = menu_person.Append(-1, _('Search'), _('Search for a person.'))
		self.Bind(wx.EVT_MENU, self.__on_search_person, item)
		acc_tab = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, item.GetId())])
		self.SetAcceleratorTable(acc_tab)
		item = menu_person.Append(-1, _('&Register person'), _("Register a new person with GNUmed"))
		self.Bind(wx.EVT_MENU, self.__on_create_new_patient, item)

		menu_person_import = wx.Menu()
		item = menu_person_import.Append(-1, _('From &External sources'), _('Load and possibly create person from available external sources.'))
		self.Bind(wx.EVT_MENU, self.__on_load_external_patient, item)
		item = menu_person_import.Append(-1, _('&vCard file \u2192 patient'), _('Import demographics from .vcf vCard file as patient'))
		self.Bind(wx.EVT_MENU, self.__on_import_vcard_from_file, item)
		item = menu_person_import.Append(-1, _('Clipboard (&XML) \u2192 patient'), _('Import demographics from clipboard (LinuxMedNews XML) as patient'))
		self.Bind(wx.EVT_MENU, self.__on_import_xml_linuxmednews, item)
		item = menu_person_import.Append(-1, _('Clipboard (&vCard) \u2192 patient'), _('Import demographics from clipboard (vCard) as patient'))
		self.Bind(wx.EVT_MENU, self.__on_import_vcard_from_clipboard, item)
		menu_person.Append(wx.NewId(), _('&Import\u2026'), menu_person_import)

		menu_person_export = wx.Menu()
		menu_person_export_clipboard = wx.Menu()
		item = menu_person_export_clipboard.Append(-1, '&GDT', _('Export demographics of currently active person as GDT into clipboard.'))
		self.Bind(wx.EVT_MENU, self.__on_export_gdt2clipboard, item)
		item = menu_person_export_clipboard.Append(-1, '&XML (LinuxMedNews)', _('Export demographics of currently active person as XML (LinuxMedNews) into clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_export_linuxmednews_xml2clipboard, item)
		item = menu_person_export_clipboard.Append(-1, '&vCard', _('Export demographics of currently active person as vCard into clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_export_vcard2clipboard, item)
		menu_person_export.Append(wx.NewId(), _('\u2192 &Clipboard as\u2026'), menu_person_export_clipboard)

		menu_person_export_file = wx.Menu()
		item = menu_person_export_file.Append(-1, '&GDT', _('Export demographics of currently active person into GDT file.'))
		self.Bind(wx.EVT_MENU, self.__on_export_as_gdt, item)
		item = menu_person_export_file.Append(-1, '&vCard', _('Export demographics of currently active person into vCard file.'))
		self.Bind(wx.EVT_MENU, self.__on_export_as_vcard, item)
		menu_person_export.Append(wx.NewId(), _('\u2192 &File as\u2026'), menu_person_export_file)

		menu_person.Append(wx.NewId(), _('E&xport\u2026'), menu_person_export)

		item = menu_person.Append(-1, _('&Merge persons'), _('Merge two persons into one.'))
		self.Bind(wx.EVT_MENU, self.__on_merge_patients, item)
		item = menu_person.Append(-1, _('Deactivate record'), _('Deactivate (exclude from search) person record in database.'))
		self.Bind(wx.EVT_MENU, self.__on_delete_patient, item)
		menu_person.AppendSeparator()
		item = menu_person.Append(-1, _('Add &tag'), _('Add a text/image tag to this person.'))
		self.Bind(wx.EVT_MENU, self.__on_add_tag2person, item)
		item = menu_person.Append(-1, _('Enlist as user'), _('Enlist current person as GNUmed user'))
		self.Bind(wx.EVT_MENU, self.__on_enlist_patient_as_staff, item)
		menu_person.AppendSeparator()

		self.mainmenu.Append(menu_person, _('&Person'))
		self.__gb['main.patientmenu'] = menu_person

		# -- menu "EMR" ---------------------------
		menu_emr = wx.Menu()

		# -- EMR / Manage
		menu_emr_manage = wx.Menu()
		item = menu_emr_manage.Append(-1, _('&Past history (health issue / PMH)'), _('Add a past/previous medical history item (health issue) to the EMR of the active patient'))
		self.Bind(wx.EVT_MENU, self.__on_add_health_issue, item)
		item = menu_emr_manage.Append(-1, _('&Episode'), _('Add an episode of illness to the EMR of the active patient'))
		self.Bind(wx.EVT_MENU, self.__on_add_episode, item)
		item = menu_emr_manage.Append(-1, _('&Medication'), _('Add medication / substance use entry.'))
		self.Bind(wx.EVT_MENU, self.__on_add_medication, item)
		item = menu_emr_manage.Append(-1, _('&Allergies'), _('Manage documentation of allergies for the current patient.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_allergies, item)
		item = menu_emr_manage.Append(-1, _('&Occupation'), _('Edit occupation details for the current patient.'))
		self.Bind(wx.EVT_MENU, self.__on_edit_occupation, item)
		item = menu_emr_manage.Append(-1, _('&Hospitalizations'), _('Manage hospitalizations.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_hospital_stays, item)
		item = menu_emr_manage.Append(-1, _('&External care'), _('Manage external care.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_external_care, item)
		item = menu_emr_manage.Append(-1, _('&Procedures'), _('Manage procedures performed on the patient.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_performed_procedures, item)
		item = menu_emr_manage.Append(-1, _('&Measurements'), _('Manage measurement results for the current patient.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_measurements, item)
		item = menu_emr_manage.Append(-1, _('&Vaccinations: by date'), _('Vaccinations ordered by date.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_vaccination, item)
		item = menu_emr_manage.Append(-1, _('&Vaccinations: by indication'), _('Vaccinations ordered by indication, showing all shots.'))
		self.Bind(wx.EVT_MENU, self.__on_show_all_vaccinations_by_indication, item)
		item = menu_emr_manage.Append(-1, _('&Vaccinations: latest per indication'), _('Vaccinations ordered by indication, showing latest shot for each.'))
		self.Bind(wx.EVT_MENU, self.__on_show_latest_vaccinations, item)
		item = menu_emr_manage.Append(-1, _('&Family history (FHx)'), _('Manage family history.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_fhx, item)
		item = menu_emr_manage.Append(-1, _('&Encounters'), _('List all encounters including empty ones.'))
		self.Bind(wx.EVT_MENU, self.__on_list_encounters, item)
		item = menu_emr_manage.Append(-1, _('&Pregnancy'), _('Calculate EDC.'))
		self.Bind(wx.EVT_MENU, self.__on_calc_edc, item)
		item = menu_emr_manage.Append(-1, _('Suppressed hints'), _('Manage dynamic hints suppressed in this patient.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_suppressed_hints, item)
		item = menu_emr_manage.Append(-1, _('Substance abuse'), _('Manage substance abuse documentation of this patient.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_substance_abuse, item)
		menu_emr.Append(wx.NewId(), _('&Manage ...'), menu_emr_manage)

		# - EMR /
		item = menu_emr.Append(-1, _('Search this EMR'), _('Search for data in the EMR of the active patient'))
		self.Bind(wx.EVT_MENU, self.__on_search_emr, item)
		item = menu_emr.Append(-1, _('Search all EMRs'), _('Search for data across the EMRs of all patients'))
		self.Bind(wx.EVT_MENU, self.__on_search_across_emrs, item)
		item = menu_emr.Append(-1, _('Start new encounter'), _('Start a new encounter for the active patient right now.'))
		self.Bind(wx.EVT_MENU, self.__on_start_new_encounter, item)

#		# - EMR / Show as /
#		menu_emr_show = wx.Menu()

		item = menu_emr.Append(-1, _('Statistics'), _('Show a high-level statistic summary of the EMR.'))
		self.Bind(wx.EVT_MENU, self.__on_show_emr_summary, item)

#		menu_emr.Append(wx.NewId(), _('Show as ...'), menu_emr_show)
#		self.__gb['main.emr_showmenu'] = menu_emr_show

		menu_emr.AppendSeparator()

		# -- EMR / Export as
		menu_emr_export = wx.Menu()
		item = menu_emr_export.Append(-1, _('Journal (encounters)'), _("Copy EMR of the active patient as a chronological journal into export area"))
		self.Bind(wx.EVT_MENU, self.__on_export_emr_as_journal, item)
		item = menu_emr_export.Append(-1, _('Journal (mod time)'), _("Copy EMR of active patient as journal (by last modification time) into export area"))
		self.Bind(wx.EVT_MENU, self.__on_export_emr_by_last_mod, item)
		item = menu_emr_export.Append(-1, _('Text document'), _("Copy EMR of active patient as text document into export area"))
		self.Bind(wx.EVT_MENU, self.__export_emr_as_textfile, item)
		item = menu_emr_export.Append(-1, _('Timeline file'), _("Copy EMR of active patient as timeline file (XML) into export area"))
		self.Bind(wx.EVT_MENU, self.__export_emr_as_timeline_xml, item)
		item = menu_emr_export.Append(-1, _('Care structure'), _("Copy EMR of active patient as care structure text file into export area"))
		self.Bind(wx.EVT_MENU, self.__export_emr_as_care_structure, item)
		# structure file
		item = menu_emr_export.Append(-1, _('MEDISTAR import format (as file)'), _("GNUmed -> MEDISTAR. Save progress notes of active patient's active encounter into a text file."))
		self.Bind(wx.EVT_MENU, self.__on_export_for_medistar, item)
		menu_emr.Append(wx.NewId(), _('Put into export area as ...'), menu_emr_export)

		menu_emr.AppendSeparator()

		self.mainmenu.Append(menu_emr, _("&EMR"))
		self.__gb['main.emrmenu'] = menu_emr

		# -- menu "Paperwork" ---------------------
		menu_paperwork = wx.Menu()
		item = menu_paperwork.Append(-1, _('Document from &template'), _('Create document/form for current patient from template.'))
		self.Bind(wx.EVT_MENU, self.__on_new_letter, item)
		item = menu_paperwork.Append(-1, _('&Generic document'), _('Write free-form document for current patient.'))
		self.Bind(wx.EVT_MENU, self.__on_new_generic_letter, item)
		item = menu_paperwork.Append(-1, _('&Failsafe document'), _('Generate failsafe document.'))
		self.Bind(wx.EVT_MENU, self.__on_generate_failsafe_document, item)
		item = menu_paperwork.Append(-1, _('Screenshot -> export area'), _('Put screenshot into patient export area.'))
		self.Bind(wx.EVT_MENU, self.__on_save_screenshot_into_export_area, item)
		menu_paperwork.AppendSeparator()
		item = menu_paperwork.Append(-1, _('List placeholders'), _('Show list of all placeholders.'))
		self.Bind(wx.EVT_MENU, self.__on_show_placeholders, item)
		item = menu_paperwork.Append(-1, _('Test placeholder'), _('Manually test placeholders'))
		self.Bind(wx.EVT_MENU, self.__on_test_placeholders, item)
		item = menu_paperwork.Append(-1, _('List passphrases'), _('Show list of paperwork passphrases'))
		self.Bind(wx.EVT_MENU, self.__on_show_paperwork_passphrases, item)
#		item = menu_paperwork.Append(-1, _('Select receiver'), _('Select a letter receiver for testing.'))
#		self.Bind(wx.EVT_MENU, self.__on_test_receiver_selection, item)
		self.mainmenu.Append(menu_paperwork, _('&Correspondence'))
		self.__gb['main.paperworkmenu'] = menu_paperwork

		# -- menu "Tools" -------------------------
		self.menu_tools = wx.Menu()
		viewer = _('no viewer installed')
		if gmShellAPI.detect_external_binary(binary = 'ginkgocadx')[0]:
			viewer = 'Ginkgo CADx'
		elif os.access('/Applications/OsiriX.app/Contents/MacOS/OsiriX', os.X_OK):
			viewer = 'OsiriX'
		elif gmShellAPI.detect_external_binary(binary = 'aeskulap')[0]:
			viewer = 'Aeskulap'
		elif gmShellAPI.detect_external_binary(binary = 'amide')[0]:
			viewer = 'AMIDE'
		elif gmShellAPI.detect_external_binary(binary = 'dicomscope')[0]:
			viewer = 'DicomScope'
		elif gmShellAPI.detect_external_binary(binary = 'xmedcon')[0]:
			viewer = '(x)medcon'
		item = self.menu_tools.Append(-1, _('DICOM viewer'), _('Start DICOM viewer (%s) for CD-ROM (X-Ray, CT, MR, etc). On Windows just insert CD.') % viewer)
		self.Bind(wx.EVT_MENU, self.__on_dicom_viewer, item)
		if viewer == _('no viewer installed'):
			_log.info('neither of Ginkgo CADx / OsiriX / Aeskulap / AMIDE / DicomScope / xmedcon found, disabling "DICOM viewer" menu item')
			self.menu_tools.Enable(id = item.Id, enable=False)
		item = self.menu_tools.Append(-1, _('Snellen chart'), _('Display fullscreen snellen chart.'))
		self.Bind(wx.EVT_MENU, self.__on_snellen, item)
		item = self.menu_tools.Append(-1, _('MI/stroke risk'), _('Acute coronary syndrome/stroke risk assessment.'))
		self.Bind(wx.EVT_MENU, self.__on_acs_risk_assessment, item)
		item = self.menu_tools.Append(-1, 'arriba', _('arriba: cardiovascular risk assessment (%s).') % 'www.arriba-hausarzt.de')
		self.Bind(wx.EVT_MENU, self.__on_arriba, item)
		if not gmShellAPI.detect_external_binary(binary = 'arriba')[0]:
			_log.info('<arriba> not found, disabling "arriba" menu item')
			self.menu_tools.Enable(id = item.Id, enable = False)

		menu_lab = wx.Menu()
		item = menu_lab.Append(-1, _('Show HL7'), _('Show formatted data from HL7 file'))
		self.Bind(wx.EVT_MENU, self.__on_show_hl7, item)
		item = menu_lab.Append(-1, _('Unwrap XML'), _('Unwrap HL7 data from XML file (Excelleris, ...)'))
		self.Bind(wx.EVT_MENU, self.__on_unwrap_hl7_from_xml, item)
		item = menu_lab.Append(-1, _('Stage HL7'), _('Stage HL7 data from file'))
		self.Bind(wx.EVT_MENU, self.__on_stage_hl7, item)
		item = menu_lab.Append(-1, _('Browse pending'), _('Browse pending (staged) incoming data'))
		self.Bind(wx.EVT_MENU, self.__on_incoming, item)
		self.menu_tools.Append(wx.NewId(), _('Lab results ...'), menu_lab)

		menu_tech_tools = wx.Menu()
		item = menu_tech_tools.Append(-1, _('&Screenshot'), _('Save a screenshot of this GNUmed client.'))
		self.Bind(wx.EVT_MENU, self.__on_save_screenshot, item)
		item = menu_tech_tools.Append(-1, _('Status line: &Clear'), _('Clear the status line.'))
		self.Bind(wx.EVT_MENU, self.__on_clear_status_line, item)
		item = menu_tech_tools.Append(-1, _('Status line: History'), _('Show status line history.'))
		self.Bind(wx.EVT_MENU, self.__on_show_status_line_history, item)
		item = menu_tech_tools.Append(-1, _('Tooltips on'), _('Globally enable tooltips.'))
		self.Bind(wx.EVT_MENU, self.__on_enable_tooltips, item)
		item = menu_tech_tools.Append(-1, _('Tooltips off'), _('Globally (attempt to) disable tooltips.'))
		self.Bind(wx.EVT_MENU, self.__on_disable_tooltips, item)
		item = menu_tech_tools.Append(-1, _('Unlock mouse'), _('Unlock mouse pointer in case it got stuck in hourglass mode.'))
		self.Bind(wx.EVT_MENU, self.__on_unblock_cursor, item)
		item = menu_tech_tools.Append(-1, _('pgAdmin III'), _('pgAdmin III: Browse GNUmed database(s) in PostgreSQL server.'))
		self.Bind(wx.EVT_MENU, self.__on_pgadmin3, item)
		if _cfg.get(option = 'debug'):
			item = menu_tech_tools.Append(-1, _('Lock/unlock patient search'), _('Lock/unlock patient search - USE ONLY IF YOU KNOW WHAT YOU ARE DOING !'))
			self.Bind(wx.EVT_MENU, self.__on_toggle_patient_lock, item)
		menu_tests = wx.Menu()
		item = menu_tests.Append(-1, _('Admin connection'), _('Test connecting to the database as admin.'))
		self.Bind(wx.EVT_MENU, self.__on_gm_dbo_connection_test, item)
		if _cfg.get(option = 'debug'):
			item = menu_tests.Append(-1, _('Error handling'), _('Throw an exception to test error handling.'))
			self.Bind(wx.EVT_MENU, self.__on_test_exception, item)
			item = menu_tests.Append(-1, _('Access violation exception'), _('Simulate an access violation exception.'))
			self.Bind(wx.EVT_MENU, self.__on_test_access_violation, item)
			item = menu_tests.Append(-1, _('Access checking'), _('Simulate a failing access check.'))
			self.Bind(wx.EVT_MENU, self.__on_test_access_checking, item)
			try:
				item = menu_tests.Append(-1, _('Fault handler'), _('Simulate a catastrophic fault (SIGSEGV).'))
				self.Bind(wx.EVT_MENU, self.__on_test_segfault, item)
			except ImportError:
				pass
			try:
				import wx.lib.inspection
				item = menu_tech_tools.Append(-1, _('Invoke inspector'), _('Invoke the widget hierarchy inspector.'))
				self.Bind(wx.EVT_MENU, self.__on_invoke_inspector, item)
			except ImportError:
				pass
		menu_tech_tools.Append(wx.NewId(), _('Tests ...'), menu_tests)
		self.menu_tools.Append(wx.NewId(), _('&Technical ...'), menu_tech_tools)
		self.menu_tools.AppendSeparator()

		self.mainmenu.Append(self.menu_tools, _("&Tools"))
		self.__gb['main.toolsmenu'] = self.menu_tools

		# -- menu "Knowledge" ---------------------
		menu_knowledge = wx.Menu()

		# -- Knowledge / Drugs
		menu_drug_dbs = wx.Menu()
		item = menu_drug_dbs.Append(-1, _('&Database'), _('Jump to the drug database configured as the default.'))
		self.Bind(wx.EVT_MENU, self.__on_jump_to_drug_db, item)
#		# - IFAP drug DB
#		item = menu_drug_dbs.Append(-1, u'ifap', _('Start "ifap index PRAXIS" %s drug browser (Windows/Wine, Germany)') % gmTools.u_registered_trademark)
#		self.Bind(wx.EVT_MENU, self.__on_ifap, item)
		item = menu_drug_dbs.Append(-1, 'kompendium.ch', _('Show "kompendium.ch" drug database (online, Switzerland)'))
		self.Bind(wx.EVT_MENU, self.__on_kompendium_ch, item)
		menu_knowledge.Append(wx.NewId(), _('&Drug Resources'), menu_drug_dbs)

#		menu_knowledge.AppendSeparator()

		item = menu_knowledge.Append(-1, _('Medical links (www)'), _('Show a page of links to useful medical content.'))
		self.Bind(wx.EVT_MENU, self.__on_medical_links, item)

		self.mainmenu.Append(menu_knowledge, _('&Knowledge'))
		self.__gb['main.knowledgemenu'] = menu_knowledge

		# -- menu "Office" --------------------
		self.menu_office = wx.Menu()

		item = self.menu_office.Append(-1, _('&Audit trail'), _('Display database audit trail.'))
		self.Bind(wx.EVT_MENU, self.__on_display_audit_trail, item)

		self.menu_office.AppendSeparator()

		item = self.menu_office.Append(-1, _('&Bills'), _('List all bills across all patients.'))
		self.Bind(wx.EVT_MENU, self.__on_show_all_bills, item)

		item = self.menu_office.Append(-1, _('&Organizations'), _('Manage organizations.'))
		self.Bind(wx.EVT_MENU, self.__on_manage_orgs, item)

		self.mainmenu.Append(self.menu_office, _('&Office'))
		self.__gb['main.officemenu'] = self.menu_office

		# -- menu "Help" --------------
		help_menu = wx.Menu()
		help_menu.Append(-1, _('Documentation'), _('GNUmed documentation (online)'))
		self.Bind(wx.EVT_MENU, self.__on_display_wiki, item)
		help_menu.Append(-1, _('User manual (www)'), _('Go to the User Manual on the web.'))
		self.Bind(wx.EVT_MENU, self.__on_display_user_manual_online, item)
#		item = help_menu.Append(-1, _('Menu reference (www)'), _('View the reference for menu items on the web.'))
#		self.Bind(wx.EVT_MENU, self.__on_menu_reference, item)

		menu_log = wx.Menu()
		item = menu_log.Append(-1, _('show'), _('Show log file in text viewer.'))
		self.Bind(wx.EVT_MENU, self.__on_show_log_file, item)
		item = menu_log.Append(-1, _('save'), _('Backup content of the log to another file.'))
		self.Bind(wx.EVT_MENU, self.__on_backup_log_file, item)
		item = menu_log.Append(-1, _('email'), _('Send log file to the authors for help.'))
		self.Bind(wx.EVT_MENU, self.__on_email_log_file, item)

		menu_browse = wx.Menu()
		item = menu_browse.Append(-1, _('work dir'), _('Browse user working directory [%s].') % gmTools.gmPaths().user_work_dir)
		self.Bind(wx.EVT_MENU, self.__on_browse_work_dir, item)
		item = menu_browse.Append(-1, _('tmp dir'), _('Browse temporary directory [%s].') % gmTools.gmPaths().tmp_dir)
		self.Bind(wx.EVT_MENU, self.__on_browse_tmp_dir, item)
		item = menu_browse.Append(-1, _('internal work dir'), _('Browse internal working directory [%s].') % gmTools.gmPaths().user_appdata_dir)
		self.Bind(wx.EVT_MENU, self.__on_browse_internal_work_dir, item)

		menu_debugging = wx.Menu()
		item = menu_debugging.Append(-1, _('Bug tracker'), _('Go to the GNUmed bug tracker on the web.'))
		self.Bind(wx.EVT_MENU, self.__on_display_bugtracker, item)
#		item = menu_debugging.Append(-1, _('Reload hook script'), _('Reload hook script from hard drive.'))
#		self.Bind(wx.EVT_MENU, self.__on_reload_hook_script, item)
		menu_debugging.Append(wx.NewId(), _('Log ...'), menu_log)
		menu_debugging.Append(wx.NewId(), _('Browse ...'), menu_browse)
		help_menu.Append(wx.NewId(), _('Debugging ...'), menu_debugging)
		help_menu.AppendSeparator()

		item = help_menu.Append(wx.ID_ABOUT, _('About GNUmed'), '')
		self.Bind(wx.EVT_MENU, self.OnAbout, item)
		item = help_menu.Append(-1, _('About database'), _('Show information about the current database.'))
		self.Bind(wx.EVT_MENU, self.__on_about_database, item)
		item = help_menu.Append(-1, _('About contributors'), _('Show GNUmed contributors'))
		self.Bind(wx.EVT_MENU, self.__on_show_contributors, item)
#		item = help_menu.Append(-1, _('Git log'), _('Show full git commit log'))
#		self.Bind(wx.EVT_MENU, self.__on_show_git_log, item)
		help_menu.AppendSeparator()
		self.mainmenu.Append(help_menu, _("&Help/Info"))
		# among other things the Manual is added from a plugin
		self.__gb['main.helpmenu'] = help_menu

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

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_QUERY_END_SESSION, self._on_query_end_session)
		self.Bind(wx.EVT_END_SESSION, self._on_end_session)

		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'statustext', receiver = self._on_set_statustext)
		gmDispatcher.connect(signal = 'request_user_attention', receiver = self._on_request_user_attention)
		gmDispatcher.connect(signal = 'register_pre_exit_callback', receiver = self._register_pre_exit_callback)
		gmDispatcher.connect(signal = 'plugin_loaded', receiver = self._on_plugin_loaded)

		gmDispatcher.connect(signal = 'db_maintenance_warning', receiver = self._on_db_maintenance_warning)
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

		# FIXME: xxxxxxx signal

		gmPerson.gmCurrentPatient().register_before_switching_from_patient_callback(callback = self._before_switching_from_patient_callback)

	#----------------------------------------------
	def _on_database_signal(self, **kwds):

		if kwds['table'] == 'dem.praxis_branch':
			if kwds['operation'] != 'UPDATE':
				return True
			branch = gmPraxis.gmCurrentPraxisBranch()
			if branch['pk_praxis_branch'] != kwds['pk_of_row']:
				return True
			self.__update_window_title()
			return True

		if kwds['table'] == 'dem.names':
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				if pat.ID != kwds['pk_identity']:
					return True
			self.__update_window_title()
			return True

		if kwds['table'] == 'dem.identity':
			if kwds['operation'] != 'UPDATE':
				return True
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				if pat.ID != kwds['pk_identity']:
					return True
			self.__update_window_title()
			return True

		return True

	#-----------------------------------------------
	def _on_plugin_loaded(self, plugin_name=None, class_name=None, menu_name=None, menu_item_name=None, menu_help_string=None):

		_log.debug('registering plugin with menu system')
		_log.debug(' generic name: %s', plugin_name)
		_log.debug(' class name: %s', class_name)
		_log.debug(' specific menu: %s', menu_name)
		_log.debug(' menu item: %s', menu_item_name)

		# add to generic "go to plugin" menu
		item = self.menu_plugins.Append(-1, plugin_name, _('Raise plugin [%s].') % plugin_name)
		self.Bind(wx.EVT_MENU, self.__on_raise_a_plugin, item)
		self.menu_id2plugin[item.Id] = class_name

		# add to specific menu if so requested
		if menu_name is not None:
			menu = self.__gb['main.%smenu' % menu_name]
			item = menu.Append(-1, menu_item_name, menu_help_string)
			self.Bind(wx.EVT_MENU, self.__on_raise_a_plugin, item)
			self.menu_id2plugin[item.Id] = class_name

		return True
	#----------------------------------------------
	def __on_raise_a_plugin(self, evt):
		gmDispatcher.send (
			signal = 'display_widget',
			name = self.menu_id2plugin[evt.Id]
		)
	#----------------------------------------------
	def _on_query_end_session(self, *args, **kwargs):
		wx.Bell()
		wx.Bell()
		wx.Bell()
		_log.warning('unhandled event detected: QUERY_END_SESSION')
		_log.info('we should be saving ourselves from here')
		gmLog2.flush()
		print('unhandled event detected: QUERY_END_SESSION')
	#----------------------------------------------
	def _on_end_session(self, *args, **kwargs):
		wx.Bell()
		wx.Bell()
		wx.Bell()
		_log.warning('unhandled event detected: END_SESSION')
		gmLog2.flush()
		print('unhandled event detected: END_SESSION')

	#-----------------------------------------------
	def _register_pre_exit_callback(self, callback=None):
		if not callable(callback):
			raise TypeError('callback [%s] not callable' % callback)

		self.__pre_exit_callbacks.append(callback)

	#-----------------------------------------------
	def _on_set_statustext_pubsub(self, context=None):
		try:
			beep = context.data['beep']
		except KeyError:
			beep = False
		wx.CallAfter(self.SetStatusText, '%s' % context.data['msg'], beep = beep)

	#-----------------------------------------------
	def _on_set_statustext(self, msg=None, loglevel=None, beep=True):
		if msg is None:
			msg = _('programmer forgot to specify status message')
		if loglevel is not None:
			_log.log(loglevel, msg.replace('\015', ' ').replace('\012', ' '))
		wx.CallAfter(self.SetStatusText, msg, beep = beep)

	#-----------------------------------------------
	def _on_db_maintenance_warning(self):

		self.SetStatusText(_('The database will be shut down for maintenance in a few minutes.'))
		wx.Bell()
		if not wx.GetApp().IsActive():
			self.RequestUserAttention(flags = wx.USER_ATTENTION_ERROR)

		gmHooks.run_hook_script(hook = 'db_maintenance_warning')

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
					'label': _('Close now'),
					'tooltip': _('Close this GNUmed client immediately.'),
					'default': False
				},
				{
					'label': _('Finish work'),
					'tooltip': _('Finish and save current work first, then manually close this GNUmed client.'),
					'default': True
				}
			]
		)
		decision = dlg.ShowModal()
		if decision == wx.ID_YES:
			top_win = wx.GetApp().GetTopWindow()
			wx.CallAfter(top_win.Close)

	#-----------------------------------------------
	def _on_request_user_attention(self, msg=None, urgent=False):
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

		gmHooks.run_hook_script(hook = 'request_user_attention')
	#-----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		self.__update_window_title()
		gmDispatcher.send(signal = 'statustext', msg = '')
		try:
			gmHooks.run_hook_script(hook = 'post_patient_activation')
		except Exception:
			_log.exception('error running hook [post_patient_activation]')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot run script after patient activation.'))

	#----------------------------------------------
	def _before_switching_from_patient_callback(self):
		msg = _(
			'Before activation of another patient review the\n'
			'encounter details of the patient you just worked on:\n'
		)
		gmEncounterWidgets.sanity_check_encounter_of_active_patient(parent = self, msg = msg)
		return True
	#----------------------------------------------
	# menu "paperwork"
	#----------------------------------------------
	def __on_show_docs(self, evt):
		gmDispatcher.send(signal='show_document_viewer')

	#----------------------------------------------
	def __on_new_letter(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot write letter. No active patient.'), beep = True)
			return True
		gmFormWidgets.print_doc_from_template(parent = self)#, keep_a_copy = True)

	#----------------------------------------------
	def __on_new_generic_letter(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot write letter. No active patient.'), beep = True)
			return True

		gmFormWidgets.print_generic_document(parent = self)

	#----------------------------------------------
	def __on_generate_failsafe_document(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot generate document. No active patient.'), beep = True)
			return True

		known_templates = [
			[_('Vaccination history'), gmVaccWidgets.save_failsafe_vaccination_history ],
			[_('Medication list'), gmMedicationWorkflows.save_failsafe_medication_list],
			[_('Prescription'), gmMedicationWorkflows.save_failsafe_prescription],
			[_('Documents list'), gmDocumentWidgets.save_failsafe_documents_list],
			[_('Measurements'), gmMeasurementWidgets.save_failsafe_test_results_list],
			[_('Progress notes'), gmNarrativeWorkflows.save_failsafe_narrative]
			#,[_(''), ]
		]
		doc_type = gmListWidgets.get_choices_from_list (
			#parent=None,
			msg = _('A text-only document will be generated and displayed for editing and printing.'),
			caption = _('Generate failsafe document'),
			columns = [_('Document type')],
			choices = [ [t[0]] for t in known_templates ],
			data = known_templates,
			#selections=None,
			#edit_callback=None,
			#new_callback=None,
			#delete_callback=None,
			#refresh_callback=None,
			single_selection = True,
			close_on_activate = True
			#can_return_empty = True,
			#ignore_OK_button=False,
			#left_extra_button=None,
			#middle_extra_button=None,
			#right_extra_button=None,
			#list_tooltip_callback=None
		)
		if not doc_type:
			return

		doc = doc_type[1](max_width = 80)
		gmMimeLib.call_editor_on_file(filename = doc, block = True)

	#----------------------------------------------
	def __on_show_placeholders(self, evt):
		from Gnumed.wxpython.gmMacro import show_placeholders
		show_placeholders()

	#----------------------------------------------
	def __on_show_paperwork_passphrases(self, evt):
		gmExportAreaWidgets.manage_paperwork_passphrases(parent = self)

	#----------------------------------------------
	def __on_save_screenshot_into_export_area(self, evt):
		evt.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot put screenshot into export area. No active patient.'), beep = True)
			return False

		screenshot_file = self.__save_screenshot_to_file()
		if not os.path.exists(screenshot_file):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot put screenshot into export area. No screenshot found.'), beep = True)
			return False

		pat.export_area.add_file(filename = screenshot_file, hint = _('GMd screenshot'))
		return True

	#----------------------------------------------
	def __on_test_receiver_selection(self, evt):
		dlg = gmFormWidgets.cReceiverSelectionDlg(None, -1)
		dlg.patient = gmPerson.gmCurrentPatient()
		choice = dlg.ShowModal()
		name = dlg.name
		adr = dlg.address
		dlg.DestroyLater()
		if choice == wx.ID_CANCEL:
			print('receiver selection cancelled')
			return

		print(name)
		print(adr.format())

	#----------------------------------------------
	# help menu
	#----------------------------------------------
	def OnAbout(self, event):

		return

		# segfaults on wxPhoenix
		from Gnumed.wxpython import gmAbout
		frame_about = gmAbout.AboutFrame (
			self,
			-1,
			_("About GNUmed"),
			size=wx.Size(350, 300),
			style = wx.MAXIMIZE_BOX,
			version = _cfg.get(option = 'client_version'),
			debug = _cfg.get(option = 'debug')
		)
		frame_about.Centre(wx.BOTH)
		gmTopLevelFrame.otherWin = frame_about
		frame_about.Show(True)
		frame_about.DestroyLater()

	#----------------------------------------------
	def __on_about_database(self, evt):
		praxis = gmPraxis.gmCurrentPraxisBranch()
		msg = praxis.db_logon_banner
		creds = gmConnectionPool.gmConnectionPool().credentials
		auth = _(
			'\n\n'
			' praxis:       %s\n'
			' branch:       %s\n'
			' workplace:    %s\n'
			' account:      %s\n'
			' locale:       %s\n'
			' access:       %s\n'
			' database:     %s\n'
			' server:       %s\n'
			' PostgreSQL:   %s\n'
		) % (
			praxis['praxis'],
			praxis['branch'],
			praxis.active_workplace,
			creds.user,
			gmPG2.get_current_user_language(),
			_provider['role'],
			creds.database,
			gmTools.coalesce(creds.host, '<localhost>'),
			gmPG2.postgresql_version_string
		)
		msg += auth
		gmGuiHelpers.gm_show_info(msg, _('About database and server'))

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
		contribs.DestroyLater()

	#----------------------------------------------
	def __on_show_git_log(self, event):
		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/documentation/code-smell/commits.log')

	#----------------------------------------------
	# GNUmed menu
	#----------------------------------------------
	def __on_exit_gnumed(self, event):
		"""Invoked from Menu GNUmed / Exit (which calls this ID_EXIT handler)."""
		_log.debug('gmTopLevelFrame._on_exit_gnumed() start')
		self.Close(True)	# -> calls wx.EVT_CLOSE handler
		_log.debug('gmTopLevelFrame._on_exit_gnumed() end')

	#----------------------------------------------
	def __on_check_for_updates(self, evt):
		gmCfgWidgets.check_for_updates()

	#----------------------------------------------
	def __on_announce_maintenance(self, evt):
		send = gmGuiHelpers.gm_show_question (
			_('This will send a notification about database downtime\n'
			  'to all GNUmed clients connected to your database.\n'
			  '\n'
			  'Do you want to send the notification ?\n'
			),
			_('Announcing database maintenance downtime')
		)
		if not send:
			return
		gmPG2.send_maintenance_notification()
	#----------------------------------------------
	#----------------------------------------------
	def __on_list_configuration(self, evt):
		gmCfgWidgets.list_configuration(parent = self)
	#----------------------------------------------
	# submenu GNUmed / options / client
	#----------------------------------------------
	def __on_configure_export_chunk_size(self, evt):

		def is_valid(value):
			try:
				i = int(value)
			except Exception:
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
	# submenu GNUmed / database
	#----------------------------------------------
	def __on_configure_db_lang(self, event):

		langs = gmPG2.get_translation_languages()

		for lang in [
			gmI18N.system_locale_level['language'],
			gmI18N.system_locale_level['country'],
			gmI18N.system_locale_level['full']
		]:
			if lang not in langs:
				langs.append(lang)

		selected_lang = gmPG2.get_current_user_language()
		try:
			selections = [langs.index(selected_lang)]
		except ValueError:
			selections = None

		language = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'Please select your database language from the list below.\n'
				'\n'
				'Your current setting is [%s].\n'
				'\n'
				'This setting will not affect the language the user interface\n'
				'is displayed in but rather that of the metadata returned\n'
				'from the database such as encounter types, document types,\n'
				'and EMR formatting.\n'
				'\n'
				'To switch back to the default English language unselect all\n'
				'pre-selected languages from the list below.'
			) % gmTools.coalesce(selected_lang, _('not configured')),
			caption = _('Configuring database language'),
			choices = langs,
			selections = selections,
			columns = [_('Language')],
			data = langs,
			single_selection = True,
			can_return_empty = True
		)

		if language is None:
			return

		if language == []:
			language = None

		try:
			_provider.get_staff().database_language = language
			return
		except ValueError:
			pass

		force_language = gmGuiHelpers.gm_show_question (
			_('The database currently holds no translations for\n'
			  'language [%s]. However, you can add translations\n'
			  'for things like document or encounter types yourself.\n'
			  '\n'
			  'Do you want to force the language setting to [%s] ?'
			) % (language, language),
			_('Configuring database language')
		)
		if not force_language:
			return

		gmPG2.force_user_language(language = language)
	#----------------------------------------------
	def __on_configure_db_welcome(self, event):
		dlg = gmPraxisWidgets.cGreetingEditorDlg(self, -1)
		dlg.ShowModal()
	#----------------------------------------------
	# submenu GNUmed - config - external tools
	#----------------------------------------------
	def __on_configure_ooo_settle_time(self, event):

		def is_valid(value):
			try:
				value = float(value)
				return True, value
			except Exception:
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
	def __on_configure_drug_data_source(self, evt):
		gmSubstanceMgmtWidgets.configure_drug_data_source(parent = self)

	#----------------------------------------------
	def __on_configure_drug_ADR_url(self, evt):
		gmMedicationWorkflows.configure_drug_ADR_url()

	#----------------------------------------------
	def __on_configure_vaccine_ADR_url(self, evt):
		gmVaccWidgets.configure_vaccine_ADR_url()

	#----------------------------------------------
	def __on_configure_vaccination_plans_url(self, evt):
		gmVaccWidgets.configure_vaccination_plans_url()

	#----------------------------------------------
	def __on_configure_measurements_url(self, evt):

		from Gnumed.business import gmPathLab
		german_default = gmPathLab.URL_test_result_information

		def is_valid(value):
			value = value.strip()
			if value == '':
				return True, german_default
			try:
				urllib.request.urlopen(value)
				return True, value
			except Exception:
				return True, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed will use this URL to access an encyclopedia of\n'
				'measurement/lab methods from within the measurements grid.\n'
				'\n'
				'You can leave this empty but to set it to a specific\n'
				'address the URL must be accessible now.'
			),
			option = 'external.urls.measurements_encyclopedia',
			bias = 'user',
			default_value = german_default,
			validator = is_valid
		)

	#----------------------------------------------
	def __on_configure_acs_risk_calculator_cmd(self, event):

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
				'the ACS risk assessment calculator.\n'
				'\n'
				'GNUmed will try to verify the path which may,\n'
				'however, fail if you are using an emulator such\n'
				'as Wine. Nevertheless, starting the calculator\n'
				'will work as long as the shell command is correct\n'
				'despite the failing test.'
			),
			option = 'external.tools.acs_risk_calculator_cmd',
			bias = 'user',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_configure_visual_soap_cmd(self, event):
		gmVisualProgressNoteWidgets.configure_visual_progress_note_editor()
	#----------------------------------------------
	def __on_configure_freediams_cmd(self, event):

		def is_valid(value):
			found, binary = gmShellAPI.detect_external_binary(value)
			if not found:
				gmDispatcher.send (
					signal = 'statustext',
					msg = _('The command [%s] is not found.') % value,
					beep = True
				)
				return False, value
			return True, binary
		#------------------------------------------
		gmCfgWidgets.configure_string_option (
			message = _(
				'Enter the shell command with which to start\n'
				'the FreeDiams drug database frontend.\n'
				'\n'
				'GNUmed will try to verify that path.'
			),
			option = 'external.tools.freediams_cmd',
			bias = 'workplace',
			default_value = None,
			validator = is_valid
		)
	#----------------------------------------------
	def __on_configure_ifap_cmd(self, event):

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
	def __on_configure_startup_plugin(self, evt):
		# get list of possible plugins
		plugin_list = gmTools.coalesce(gmCfgDB.get4user (
			option = 'horstspace.notebook.plugin_load_order',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		), [])

		# get current setting
		initial_plugin = gmTools.coalesce(gmCfgDB.get4user (
			option = 'horstspace.plugin_to_raise_after_startup',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		), 'gmEMRBrowserPlugin')
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

		gmCfgDB.set (
			option = 'horstspace.plugin_to_raise_after_startup',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			value = plugin
		)

	#----------------------------------------------
	# submenu GNUmed / config / ui / patient search
	#----------------------------------------------
	def __on_configure_quick_pat_search(self, evt):
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
	def __on_cfg_default_region(self, evt):
		gmAddressWidgets.configure_default_region()
	#----------------------------------------------
	def __on_cfg_default_country(self, evt):
		gmAddressWidgets.configure_default_country()
	#----------------------------------------------
	def __on_configure_dob_reminder_proximity(self, evt):

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
			) % '\u2213',
			option = 'patient_search.dob_warn_interval',
			bias = 'user',
			default_value = '1 week',
			validator = is_valid
		)
	#----------------------------------------------
	def __on_allow_multiple_new_episodes(self, evt):

		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'When adding progress notes do you want to\n'
				'allow opening several unassociated, new\n'
				'episodes for a patient at once ?\n'
				'\n'
				'This can be particularly helpful when entering\n'
				'progress notes on entirely new patients presenting\n'
				'with a multitude of problems on their first visit.'
			),
			option = 'horstspace.soap_editor.allow_same_episode_multiple_times',
			button_tooltips = [
				_('Yes, allow for multiple new episodes concurrently.'),
				_('No, only allow editing one new episode at a time.')
			]
		)
	#----------------------------------------------
	def __on_allow_auto_open_episodes(self, evt):

		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'When activating a patient, do you want GNUmed to\n'
				'auto-open editors for all active problems that were\n'
				'touched upon during the current and the most recent\n'
				'encounter ?'
			),
			option = 'horstspace.soap_editor.auto_open_latest_episodes',
			button_tooltips = [
				_('Yes, auto-open editors for all problems of the most recent encounter.'),
				_('No, only auto-open one editor for a new, unassociated problem.')
			]
		)

	#----------------------------------------------
	def __on_use_fields_in_soap_editor(self, evt):
		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'When editing progress notes, do you want GNUmed to\n'
				'show individual fields for each of the SOAP categories\n'
				'or do you want to use a text-editor like field for\n'
				'all SOAP categories which can then be set per line\n'
				'of input ?'
			),
			option = 'horstspace.soap_editor.use_one_field_per_soap_category',
			button_tooltips = [
				_('Yes, show a dedicated field per SOAP category.'),
				_('No, use one field for all SOAP categories.')
			]
		)

	#----------------------------------------------
	def __on_configure_initial_pat_plugin(self, evt):
		# get list of possible plugins
		plugin_list = gmTools.coalesce(gmCfgDB.get4user (
			option = 'horstspace.notebook.plugin_load_order',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		), [])

		# get current setting
		initial_plugin = gmTools.coalesce(gmCfgDB.get4user (
			option = 'patient_search.plugin_to_raise_after_search',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		), 'gmPatientOverviewPlugin')
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

		gmCfgDB.set (
			option = 'patient_search.plugin_to_raise_after_search',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			value = plugin
		)

	#----------------------------------------------
	# submenu GNUmed / config / billing
	#----------------------------------------------
	def __on_cfg_invoice_template_no_vat(self, evt):
		gmBillingWidgets.configure_invoice_template(parent = self, with_vat = False)
	#----------------------------------------------
	def __on_cfg_invoice_template_with_vat(self, evt):
		gmBillingWidgets.configure_invoice_template(parent = self, with_vat = True)
	#----------------------------------------------
	def __on_configure_billing_catalogs_url(self, evt):
		german_default = 'https://www.e-bis.de/goae/defaultFrame.htm'

		def is_valid(value):
			value = value.strip()
			if value == '':
				return True, german_default
			try:
				urllib.request.urlopen(value)
				return True, value
			except Exception:
				return True, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed will use this URL to let you browse\n'
				'billing catalogs (schedules of fees).\n'
				'\n'
				'You can leave this empty but to set it to a specific\n'
				'address the URL must be accessible now.'
			),
			option = 'external.urls.schedules_of_fees',
			bias = 'user',
			default_value = german_default,
			validator = is_valid
		)

	#----------------------------------------------
	def __on_cfg_invoice_id_template(self, evt):
		from Gnumed.business.gmBilling import DEFAULT_INVOICE_ID_TEMPLATE
		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed will use this template to generate invoice IDs.\n'
				'\n'
				'If unset GNUmed will use the builtin format\n'
				' >>>%s<<<\n'
				'\n'
				'The template is processed according to Python\n'
				'String Formatting rules with dictionary data.\n'
				'\n'
				'The following placeholders can be used:\n'
				' %%(pk_pat)s - primary key of the patient\n'
				' %%(date)s - current date\n'
				' %%(time)s - current time\n'
				' %%(firstname)s - first names of patient\n'
				' %%(lastname)s - last names of patient\n'
				' %%(dob)s - date of birth of patient\n'
				' #counter# - replaced by a counter\n'
				'  - counting up from 1 to 999999 until the invoice ID is unique\n'
				'  - optional if %%(time)s is included\n'
				'\n'
				'Length modifiers are respected so that\n'
				'%%(lastname)4.4s will work as expected.\n'
			) % DEFAULT_INVOICE_ID_TEMPLATE,
			option = u'billing.invoice_id_template'
		)

	#----------------------------------------------
	# submenu GNUmed / config / encounter
	#----------------------------------------------
	def __on_cfg_medication_list_template(self, evt):
		gmMedicationWorkflows.configure_medication_list_template(parent = self)

	#----------------------------------------------
	def __on_cfg_prescription_template(self, evt):
		gmMedicationWorkflows.configure_prescription_template(parent = self)

	#----------------------------------------------
	def __on_cfg_prescription_mode(self, evt):
		gmCfgWidgets.configure_string_from_list_option (
			parent = self,
			message = _('Select the default prescription mode.\n'),
			option = 'horst_space.default_prescription_mode',
			bias = 'user',
			default_value = 'form',
			choices = [ _('Formular'), _('Datenbank') ],
			columns = [_('Prescription mode')],
			data = [ 'form', 'database' ]
		)

	#----------------------------------------------
	def __on_cfg_default_gnuplot_template(self, evt):
		gmMeasurementWidgets.configure_default_gnuplot_template(parent = self)

	#----------------------------------------------
	def __on_cfg_fallback_primary_provider(self, evt):
		gmPraxisWidgets.configure_fallback_primary_provider(parent = self)

	#----------------------------------------------
	def __on_cfg_meds_lab_pnl(self, evt):
		gmMedicationWorkflows.configure_default_medications_lab_panel(parent = self)

	#----------------------------------------------
	def __on_cfg_top_lab_pnl(self, evt):
		gmMeasurementWidgets.configure_default_top_lab_panel(parent = self)

	#----------------------------------------------
	def __on_cfg_enc_default_type(self, evt):
		enc_types = gmEncounter.get_encounter_types()
		msg = _(
			'Select the default type for new encounters.\n'
			'\n'
			'Leaving this unset will make GNUmed apply the most commonly used type.\n'
		)
		gmCfgWidgets.configure_string_from_list_option (
			parent = self,
			message = msg,
			option = 'encounter.default_type',
			bias = 'user',
#			default_value = u'in surgery',
			choices = [ e[0] for e in enc_types ],
			columns = [_('Encounter type')],
			data = [ e[1] for e in enc_types ]
		)
	#----------------------------------------------
	def __on_cfg_enc_pat_change(self, event):
		gmCfgWidgets.configure_boolean_option (
			parent = self,
			question = _(
				'Do you want GNUmed to show the encounter\n'
				'details editor when changing the active patient ?'
			),
			option = 'encounter.show_editor_before_patient_change',
			button_tooltips = [
				_('Yes, show the encounter editor if it seems appropriate.'),
				_('No, never show the encounter editor even if it would seem useful.')
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
				'age of the most recent encounter.\n'
				'\n'
				'If that encounter is younger than this age\n'
				'the existing encounter will be continued.\n'
				'\n'
				'(If it is really old a new encounter is\n'
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
				'age of the most recent encounter.\n'
				'\n'
				'If that encounter is older than this age\n'
				'GNUmed will always start a new encounter.\n'
				'\n'
				'(If it is very recent the existing encounter\n'
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
			except Exception:
				return False, value
			return gmPG2.is_pg_interval(candidate=value), value

		gmCfgWidgets.configure_string_option (
			message = _(
				'At any time there can only be one open (ongoing)\n'
				'episode for each health issue.\n'
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
	def __on_configure_user_email(self, evt):
		email = gmPraxis.gmCurrentPraxisBranch().user_email

		dlg = wx.TextEntryDialog (
			self,
			_(
				'If you want the GNUmed developers to be able to\n'
				'contact you directly - rather than via the public\n'
				'mailing list only - you can enter your preferred\n'
				'email address here.\n'
				'\n'
				'This address will then be included with bug reports\n'
				'or contributions to the GNUmed community you may\n'
				'choose to send from within the GNUmed client.\n'
				'\n'
				'Leave this blank if you wish to stay anonymous.\n'
			),
			caption = _('Please enter your email address.'),
			value = gmTools.coalesce(email, ''),
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		decision = dlg.ShowModal()
		if decision == wx.ID_CANCEL:
			dlg.DestroyLater()
			return

		email = dlg.GetValue().strip()
		gmPraxis.gmCurrentPraxisBranch().user_email = email
		gmExceptionHandlingWidgets.set_sender_email(email)
		dlg.DestroyLater()
	#----------------------------------------------
	def __on_configure_update_check(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'Do you want GNUmed to check for updates at startup ?\n'
				'\n'
				'You will still need your system administrator to\n'
				'actually install any updates for you.\n'
			),
			option = 'horstspace.update.autocheck_at_startup',
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
			option = 'horstspace.update.consider_latest_branch',
			button_tooltips = [
				_('Yes, check for feature updates, too.'),
				_('No, check for bug-fix updates only.')
			]
		)
	#----------------------------------------------
	def __on_configure_update_url(self, evt):

		def is_valid(value):
			try:
				urllib.request.urlopen(value)
			except Exception:
				return False, value

			return True, value

		gmCfgWidgets.configure_string_option (
			message = _(
				'GNUmed can check for new releases being available. To do\n'
				'so it needs to load version information from an URL.\n'
				'\n'
				'The default URL is:\n'
				'\n'
				' https://www.gnumed.de/downloads/gnumed-versions.txt\n'
				'\n'
				'but you can configure any other URL locally. Note\n'
				'that you must enter the location as a valid URL.\n'
				'Depending on the URL the client will need online\n'
				'access when checking for updates.'
			),
			option = 'horstspace.update.url',
			bias = 'workplace',
			default_value = 'https://www.gnumed.de/downloads/gnumed-versions.txt',
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
			option = 'horstspace.scan_index.allow_partless_documents',
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
			option = 'horstspace.scan_index.show_doc_id',
			button_tooltips = [
				_('Yes, display the ID generated for the new document after importing.'),
				_('No, do not display the ID generated for the new document after importing.')
			]
		)
	#----------------------------------------------
	def __on_configure_generate_doc_uuid(self, evt):
		gmCfgWidgets.configure_boolean_option (
			question = _(
				'After importing a new document do you\n'
				'want GNUmed to generate a unique ID\n'
				'(UUID) for that document ?\n'
				'\n'
				'This can be useful if you want to label the\n'
				'originals with that ID for later identification.'
			),
			option = 'horstspace.scan_index.generate_doc_uuid',
			button_tooltips = [
				_('Yes, generate a UUID for the new document after importing.'),
				_('No, do not generate a UUID for the new document after importing.')
			]
		)
	#----------------------------------------------
	def __on_configure_doc_review_dialog(self, evt):

		def is_valid(value):
			try:
				value = int(value)
			except Exception:
				return False, value
			if value not in [0, 1, 2, 3, 4]:
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
				' 3: only if there is no previous review at all\n'
				' 4: only if there is no review by the responsible reviewer\n'
				'\n'
				'Note that if a viewer is configured to not block\n'
				'GNUmed during document display the review dialog\n'
				'will actually appear in parallel to the viewer.'
			),
			option = 'horstspace.document_viewer.review_after_display',
			bias = 'user',
			default_value = 3,
			validator = is_valid
		)
	#----------------------------------------------
	def __on_manage_master_data(self, evt):

		# this is how it is sorted
		master_data_lists = [
			'adr',
			'provinces',
			'codes',
			'billables',
			'ref_data_sources',
			'meds_substances',
			'meds_doses',
			'meds_components',
			'meds_drugs',
			'meds_vaccines',
			'orgs',
			'labs',
			'meta_test_types',
			'test_types',
			'test_panels',
			'form_templates',
			'doc_types',
			'enc_types',
			'communication_channel_types',
			'text_expansions',
			'patient_tags',
			'gender_defs',
			'hints',
			'db_translations',
			'workplaces'
		]

		master_data_list_names = {
			'adr': _('Addresses (likely slow)'),
			'hints': _('Dynamic automatic hints'),
			'codes': _('Codes and their respective terms'),
			'communication_channel_types': _('Communication channel types'),
			'orgs': _('Organizations with their units, addresses, and comm channels'),
			'labs': _('Measurements: diagnostic organizations (path labs, ...)'),
			'test_types': _('Measurements: test types'),
			'test_panels': _('Measurements: test panels/profiles/batteries'),
			'form_templates': _('Document templates (forms, letters, plots, ...)'),
			'doc_types': _('Document types'),
			'enc_types': _('Encounter types'),
			'text_expansions': _('Keyword based text expansion macros'),
			'meta_test_types': _('Measurements: aggregate test types'),
			'patient_tags': _('Patient tags'),
			'provinces': _('Provinces (counties, territories, states, regions, ...)'),
			'db_translations': _('String translations in the database'),
			'meds_vaccines': _('Medications: vaccines'),
			'meds_substances': _('Medications: base substances'),
			'meds_doses':      _('Medications: substance dosage'),
			'meds_components': _('Medications: drug components'),
			'meds_drugs':      _('Medications: drug products and generic drugs'),
			'workplaces': _('Workplace profiles (which plugins to load)'),
			'billables': _('Billable items'),
			'ref_data_sources': _('Reference data sources'),
			'gender_defs': _('Gender definitions')
		}

		map_list2handler = {
			'form_templates': gmFormWidgets.manage_form_templates,
			'doc_types': gmDocumentWidgets.manage_document_types,
			'text_expansions': gmKeywordExpansionWidgets.configure_keyword_text_expansion,
			'db_translations': gmI18nWidgets.manage_translations,
			'codes': gmCodingWidgets.browse_coded_terms,
			'enc_types': gmEncounterWidgets.manage_encounter_types,
			'provinces': gmAddressWidgets.manage_regions,
			'workplaces': gmPraxisWidgets.configure_workplace_plugins,
			'labs': gmMeasurementWidgets.manage_measurement_orgs,
			'test_types': gmMeasurementWidgets.manage_measurement_types,
			'meta_test_types': gmMeasurementWidgets.manage_meta_test_types,
			'orgs': gmOrganizationWidgets.manage_orgs,
			'adr': gmAddressWidgets.manage_addresses,
			'meds_substances': gmSubstanceMgmtWidgets.manage_substances,
			'meds_doses': gmSubstanceMgmtWidgets.manage_substance_doses,
			'meds_components': gmSubstanceMgmtWidgets.manage_drug_components,
			'meds_drugs': gmSubstanceMgmtWidgets.manage_drug_products,
			'meds_vaccines': gmVaccWidgets.manage_vaccines,
			'patient_tags': gmDemographicsWidgets.manage_tag_images,
			'communication_channel_types': gmContactWidgets.manage_comm_channel_types,
			'billables': gmBillingWidgets.manage_billables,
			'ref_data_sources': gmCodingWidgets.browse_data_sources,
			'hints': gmAutoHintWidgets.manage_dynamic_hints,
			'test_panels': gmMeasurementWidgets.manage_test_panels,
			'gender_defs': gmDemographicsWidgets.manage_gender_definitions
		}

		#---------------------------------
		def edit(item):
			try: map_list2handler[item](parent = self)
			except KeyError: pass
			return False

		#---------------------------------

		gmListWidgets.get_choices_from_list (
			parent = self,
			caption = _('Master data management'),
			choices = [ master_data_list_names[lst] for lst in master_data_lists],
			data = master_data_lists,
			columns = [_('Select the list you want to manage:')],
			edit_callback = edit,
			single_selection = True,
			ignore_OK_button = True
		)
	#----------------------------------------------
	def __on_manage_praxis(self, evt):
		gmPraxisWidgets.manage_praxis_branches(parent = self)

	#----------------------------------------------
	def __on_dicom_viewer(self, evt):

		found, cmd = gmShellAPI.detect_external_binary(binary = 'ginkgocadx')
		if found:
			gmShellAPI.run_command_in_shell(cmd, blocking=False)
			return

		if os.access('/Applications/OsiriX.app/Contents/MacOS/OsiriX', os.X_OK):
			gmShellAPI.run_command_in_shell('/Applications/OsiriX.app/Contents/MacOS/OsiriX', blocking = False)
			return

		for viewer in ['aeskulap', 'amide', 'dicomscope', 'xmedcon']:
			found, cmd = gmShellAPI.detect_external_binary(binary = viewer)
			if found:
				gmShellAPI.run_command_in_shell(cmd, blocking = False)
				return

		gmDispatcher.send(signal = 'statustext', msg = _('No DICOM viewer found.'), beep = True)
	#----------------------------------------------
	def __on_arriba(self, evt):

		curr_pat = gmPerson.gmCurrentPatient()

		arriba = gmArriba.cArriba()
		pat = gmTools.bool2subst(curr_pat.connected, curr_pat, None)
		if not arriba.run(patient = pat, debug = _cfg.get(option = 'debug')):
			return

		# FIXME: try to find patient
		if curr_pat is None:
			return

		if arriba.pdf_result is None:
			return

		doc = gmDocumentWidgets.save_file_as_new_document (
			parent = self,
			filename = arriba.pdf_result,
			document_type = _('risk assessment'),
			pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit'],
			date_generated = gmDateTime.pydt_now_here()
		)

		try: os.remove(arriba.pdf_result)
		except Exception: _log.exception('cannot remove [%s]', arriba.pdf_result)

		if doc is None:
			return

		doc['comment'] = 'arriba: %s' % _('cardiovascular risk assessment')
		doc.save()

		try:
			open(arriba.xml_result).close()
			part = doc.add_part(file = arriba.xml_result)
		except Exception:
			_log.exception('error accessing [%s]', arriba.xml_result)
			gmDispatcher.send(signal = 'statustext', msg = _('[arriba] XML result not found in [%s]') % arriba.xml_result, beep = False)

		if part is None:
			return

		part['obj_comment'] = 'XML-Daten'
		part['filename'] = 'arriba-result.xml'
		part.save()
	#----------------------------------------------
	def __on_acs_risk_assessment(self, evt):
		cmd = gmCfgDB.get4user (
			option = 'external.tools.acs_risk_calculator_cmd',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)

		if cmd is None:
			gmDispatcher.send(signal = 'statustext', msg = _('ACS risk assessment calculator not configured.'), beep = True)
			return

		cwd = gmTools.gmPaths().user_tmp_dir
		try:
			subprocess.check_call (
				args = (cmd,),
				close_fds = True,
				cwd = cwd
			)
		except (OSError, ValueError, subprocess.CalledProcessError):
			_log.exception('there was a problem executing [%s]', cmd)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot run [%s] !') % cmd, beep = True)
			return

		pdfs = glob.glob(os.path.join(cwd, 'arriba-%s-*.pdf' % gmDateTime.pydt_now_here().strftime('%Y-%m-%d')))
		for pdf in pdfs:
			try:
				open(pdf).close()
			except Exception:
				_log.exception('error accessing [%s]', pdf)
				gmDispatcher.send(signal = 'statustext', msg = _('There was a problem accessing the [arriba] result in [%s] !') % pdf, beep = True)
				continue

			doc = gmDocumentWidgets.save_file_as_new_document (
				parent = self,
				filename = pdf,
				document_type = 'risk assessment',
				pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit'],
				date_generated = gmDateTime.pydt_now_here()
			)

			try:
				os.remove(pdf)
			except Exception:
				_log.exception('cannot remove [%s]', pdf)

			if doc is None:
				continue
			doc['comment'] = 'arriba: %s' % _('cardiovascular risk assessment')
			doc.save()

		return

	#----------------------------------------------
	def __on_show_hl7(self, evt):
#		from Gnumed.business import gmClinicalCalculator
#		calc = gmClinicalCalculator.cClinicalCalculator(patient = gmPerson.gmCurrentPatient())
#		result = calc.eGFR_CKD_EPI
#		print(u'%s' % result.format(with_formula = True, with_warnings = True, with_variables = True, with_sub_results = True, with_hints = True))
#		return
		gmMeasurementWidgets.show_hl7_file(parent = self)
	#----------------------------------------------
	def __on_unwrap_hl7_from_xml(self, evt):
		gmMeasurementWidgets.unwrap_HL7_from_XML(parent = self)
	#----------------------------------------------
	def __on_stage_hl7(self, evt):
		gmMeasurementWidgets.stage_hl7_file(parent = self)
	#----------------------------------------------
	def __on_incoming(self, evt):
		gmMeasurementWidgets.browse_incoming(parent = self)
	#----------------------------------------------
	def __on_snellen(self, evt):
		dlg = gmSnellen.cSnellenCfgDlg()
		if dlg.ShowModal() != wx.ID_OK:
			return

		frame = gmSnellen.cSnellenChart (
			width = dlg.vals[0],
			height = dlg.vals[1],
			alpha = dlg.vals[2],
			mirr = dlg.vals[3],
			parent = None
		)
		frame.CentreOnScreen(wx.BOTH)
#		self.SetTopWindow(frame)
#		frame.Destroy = frame.DestroyWhenApp
		frame.Show(True)
	#----------------------------------------------
	#----------------------------------------------
	def __on_medical_links(self, evt):
		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/bin/view/Gnumed/MedicalContentLinks#AnchorLocaleI%s' % gmI18N.system_locale_level['language'])

	#----------------------------------------------
	def __on_jump_to_drug_db(self, evt):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			curr_pat = None
		gmSubstanceMgmtWidgets.jump_to_drug_database(patient = curr_pat)

	#----------------------------------------------
	def __on_kompendium_ch(self, evt):
		gmNetworkTools.open_url_in_browser(url = 'https://www.kompendium.ch')

	#----------------------------------------------
	# Office
	#----------------------------------------------
	def __on_display_audit_trail(self, evt):
		gmPraxisWidgets.show_audit_trail(parent = self)

	#----------------------------------------------
	def __on_show_all_bills(self, evt):
		gmBillingWidgets.manage_bills(parent = self)

	#----------------------------------------------
	def __on_manage_orgs(self, evt):
		gmOrganizationWidgets.manage_orgs(parent = self)

	#----------------------------------------------
	# Help / Debugging
	#----------------------------------------------
	def __on_save_screenshot(self, evt):
		title = gmGuiHelpers.undecorate_window_title(self.Title.rstrip())
		png_fname = os.path.join (
			gmTools.gmPaths().home_dir,
			'gnumed',
			'gm-%s-%s.png' % (title, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
		)
		self.__save_screenshot_to_file(filename = png_fname)

	#----------------------------------------------
	def __on_test_exception(self, evt):
		raise ValueError('raised ValueError to test exception handling')

	#----------------------------------------------
	def __on_test_segfault(self, evt):
		import faulthandler
		_log.debug('testing faulthandler via SIGSEGV')
		faulthandler._sigsegv()

	#----------------------------------------------
	def __on_test_placeholders(self, evt):
		from Gnumed.wxpython.gmMacro import test_placeholders_interactively
		test_placeholders_interactively()

	#----------------------------------------------
	def __on_test_access_violation(self, evt):
		raise gmExceptions.AccessDenied (
			_('[-9999]: <access violation test error>'),
			source = 'GNUmed code',
			code = -9999,
			details = _('This is a deliberate AccessDenied exception thrown to test the handling of access violations by means of a decorator.')
		)
	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('admin', activity = _('testing access check for non-existent <admin> role'))
	def __on_test_access_checking(self, evt):
		raise gmExceptions.AccessDenied (
			_('[-9999]: <access violation test error>'),
			source = 'GNUmed code',
			code = -9999,
			details = _('This is a deliberate AccessDenied exception. You should not see this message because the role is checked in a decorator.')
		)
	#----------------------------------------------
	def __on_invoke_inspector(self, evt):
		import wx.lib.inspection
		wx.lib.inspection.InspectionTool().Show()
	#----------------------------------------------
	def __on_display_bugtracker(self, evt):
		gmNetworkTools.open_url_in_browser(url = 'https://bugs.launchpad.net/gnumed/')
	#----------------------------------------------
	def __on_display_wiki(self, evt):
		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/documentation/')
	#----------------------------------------------
	def __on_display_user_manual_online(self, evt):
		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/documentation/GNUmedManual.html')

#	#----------------------------------------------
#	def __on_menu_reference(self, evt):
#		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/bin/view/Gnumed/MenuReference')

	#----------------------------------------------
	def __on_pgadmin3(self, evt):
		found, cmd = gmShellAPI.detect_external_binary(binary = 'pgadmin3')
		if found:
			gmShellAPI.run_command_in_shell(cmd, blocking = False)
			return
		gmDispatcher.send(signal = 'statustext', msg = _('pgAdmin III not found.'), beep = True)

	#----------------------------------------------
	def __on_gm_dbo_connection_test(self, evt):
		conn = gmAuthWidgets.get_dbowner_connection (
			procedure = _('Test for connecting as database admin (owner).'),
			dbo_account = 'gm-dbo'
		)
		if conn is not None:
			gmGuiHelpers.gm_show_info(_('Successfully connected as database owner.'))

	#----------------------------------------------
	def __on_reload_hook_script(self, evt):
		if not gmHooks.import_hook_module(reimport = True):
			gmDispatcher.send(signal = 'statustext', msg = _('Error reloading hook script.'))
	#----------------------------------------------
	def __on_unblock_cursor(self, evt):
		wx.EndBusyCursor()
	#----------------------------------------------
	def __on_clear_status_line(self, evt):
		gmDispatcher.send(signal = 'statustext', msg = '')
		self.StatusBar.set_normal_color()

	#----------------------------------------------
	def __on_show_status_line_history(self, evt):
		self.StatusBar.show_history()

	#----------------------------------------------
	def __on_enable_tooltips(self, evt):
		wx.ToolTip.Enable(True)

	#----------------------------------------------
	def __on_disable_tooltips(self, evt):
		wx.ToolTip.Enable(False)

	#----------------------------------------------
	def __on_toggle_patient_lock(self, evt):
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.locked:
			curr_pat.force_unlock()
		else:
			curr_pat.locked = True
	#----------------------------------------------
	def __on_show_log_file(self, evt):
		gmLog2.flush()
		gmMimeLib.call_viewer_on_file(gmLog2._logfile_name, block = False)
	#----------------------------------------------
	def __on_backup_log_file(self, evt):
		name = os.path.basename(gmLog2._logfile_name)
		name, ext = os.path.splitext(name)
		new_name = '%s_%s%s' % (name, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ext)
		new_path = gmTools.gmPaths().user_work_dir

		dlg = wx.FileDialog (
			parent = self,
			message = _("Save current log as..."),
			defaultDir = new_path,
			defaultFile = new_name,
			wildcard = "%s (*.log)|*.log" % _("log files"),
			style = wx.FD_SAVE
		)
		choice = dlg.ShowModal()
		new_name = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		_log.warning('syncing log file for backup to [%s]', new_name)
		gmLog2.flush()
		shutil.copy2(gmLog2._logfile_name, new_name)
		gmDispatcher.send('statustext', msg = _('Log file backed up as [%s].') % new_name)
	#----------------------------------------------
	def __on_email_log_file(self, evt):
		gmExceptionHandlingWidgets.mail_log(parent = self)

	#----------------------------------------------
	def __on_browse_tmp_dir(self, evt):
		gmMimeLib.call_viewer_on_file(gmTools.gmPaths().tmp_dir, block = False)

	#----------------------------------------------
	def __on_browse_work_dir(self, evt):
		gmMimeLib.call_viewer_on_file(gmTools.gmPaths().user_work_dir, block = False)

	#----------------------------------------------
	def __on_browse_internal_work_dir(self, evt):
		gmMimeLib.call_viewer_on_file(gmTools.gmPaths().user_appdata_dir, block = False)

	#----------------------------------------------
	# GNUmed /
	#----------------------------------------------
	def OnClose(self, event):
		"""This is the wx.EVT_CLOSE handler.

		- framework still functional
		"""
		_log.debug('gmTopLevelFrame.OnClose() start')
		self._clean_exit()
		self.DestroyLater()
		_log.debug('gmTopLevelFrame.OnClose() end')
		return True

	#----------------------------------------------
	def __on_start_new_encounter(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot start new encounter. No active patient.'))
			return False
		emr = pat.emr
		gmEncounterWidgets.start_new_encounter(emr = emr)
	#----------------------------------------------
	def __on_list_encounters(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot list encounters. No active patient.'))
			return False
		gmEncounterWidgets.select_encounters()
	#----------------------------------------------
	def __on_add_health_issue(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add health issue. No active patient.'))
			return False
		gmEMRStructWidgets.edit_health_issue(parent = self, issue = None)
	#----------------------------------------------
	def __on_add_episode(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add episode. No active patient.'))
			return False
		gmEMRStructWidgets.edit_episode(parent = self, episode = None)
	#----------------------------------------------
	def __on_add_medication(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add medication. No active patient.'))
			return False

		gmSubstanceIntakeWidgets.edit_intake_with_regimen(parent = self)

		evt.Skip()
	#----------------------------------------------
	def __on_manage_allergies(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add allergy. No active patient.'))
			return False
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_manage_performed_procedures(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage performed procedures. No active patient.'))
			return False
		gmProcedureWidgets.manage_performed_procedures(parent = self)
		evt.Skip()
	#----------------------------------------------
	def __on_manage_hospital_stays(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage hospitalizations. No active patient.'))
			return False
		gmHospitalStayWidgets.manage_hospital_stays(parent = self)
		evt.Skip()
	#----------------------------------------------
	def __on_manage_external_care(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage external care. No active patient.'))
			return False
		gmExternalCareWidgets.manage_external_care(parent = self)
		evt.Skip()
	#----------------------------------------------
	def __on_edit_occupation(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit occupation. No active patient.'))
			return False
		gmDemographicsWidgets.edit_occupation()
		evt.Skip()

	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage vaccinations'))
	def __on_manage_vaccination(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add vaccinations. No active patient.'))
			return False

		gmVaccWidgets.manage_vaccinations(parent = self, latest_only = False)
		evt.Skip()

	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage vaccinations'))
	def __on_show_latest_vaccinations(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage vaccinations. No active patient.'))
			return False

		gmVaccWidgets.manage_vaccinations(parent = self, latest_only = True)
		evt.Skip()

	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage vaccinations'))
	def __on_show_all_vaccinations_by_indication(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage vaccinations. No active patient.'))
			return False

		gmVaccWidgets.manage_vaccinations(parent = self, latest_only = False, expand_indications = True)
		evt.Skip()

	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage family history'))
	def __on_manage_fhx(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage family history. No active patient.'))
			return False

		gmFamilyHistoryWidgets.manage_family_history(parent = self)
		evt.Skip()
	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage vaccinations'))
	def __on_manage_measurements(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage measurements. No active patient.'))
			return False
		gmMeasurementWidgets.manage_measurements(parent = self, single_selection = True, emr = pat.emr)
	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('calculate EDC'))
	def __on_calc_edc(self, evt):
		pat = gmPerson.gmCurrentPatient()
		gmPregWidgets.calculate_edc(parent = self, patient = pat)

	#----------------------------------------------
	@gmAccessPermissionWidgets.verify_minimum_required_role('full clinical access', activity = _('manage suppressed hints'))
	def __on_manage_suppressed_hints(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage suppressed hints. No active patient.'))
			return False
		gmAutoHintWidgets.manage_suppressed_hints(parent = self, pk_identity = pat.ID)

	#----------------------------------------------
	def __on_manage_substance_abuse(self, evt):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot manage smoking status. No active patient.'))
			return False
		gmHabitWidgets.manage_substance_abuse(parent = self, patient = pat)

	#----------------------------------------------
	def __on_show_emr_summary(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot show EMR summary. No active patient.'))
			return False

		emr = pat.emr
		dlg = wx.MessageDialog (
			parent = self,
			message = emr.format_statistics(),
			caption = _('EMR Summary'),
			style = wx.OK | wx.STAY_ON_TOP
		)
		dlg.ShowModal()
		dlg.DestroyLater()
		return True
	#----------------------------------------------
	def __on_search_emr(self, event):
		return gmNarrativeWorkflows.search_narrative_in_emr(parent=self)
	#----------------------------------------------
	def __on_search_across_emrs(self, event):
		gmNarrativeWorkflows.search_narrative_across_emrs(parent=self)

	#----------------------------------------------
	def __export_emr_as_textfile(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR. No active patient.'))
			return False
		from Gnumed.exporters import gmPatientExporter
		exporter = gmPatientExporter.cEmrExport(patient = pat)
		fname = gmTools.get_unique_filename(prefix = 'gm-exp-', suffix = '.txt')
		output_file = open(fname, mode = 'wt', encoding = 'utf8', errors = 'replace')
		exporter.set_output_file(output_file)
		exporter.dump_constraints()
		exporter.dump_demographic_record(True)
		exporter.dump_clinical_record()
		exporter.dump_med_docs()
		output_file.close()
		pat.export_area.add_file(filename = fname, hint = _('EMR as text document'))

	#----------------------------------------------
	def __export_emr_as_timeline_xml(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR. No active patient.'))
			return False
		wx.BeginBusyCursor()
		from Gnumed.exporters import gmTimelineExporter
		try:
			fname = gmTimelineExporter.create_timeline_file (
				patient = pat,
				include_documents = True,
				include_vaccinations = True,
				include_encounters = True
			)
		finally:
			wx.EndBusyCursor()
		pat.export_area.add_file(filename = fname, hint = _('EMR as timeline file (XML)'))

	#----------------------------------------------
	def __export_emr_as_care_structure(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR. No active patient.'))
			return False

		wx.BeginBusyCursor()
		try:
			fname = pat.emr.export_care_structure()
			pat.export_area.add_file(filename = fname, hint = _('EMR as care structure file'))
		except Exception:
			_log.exception('error adding EMR structure file to export area')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR.'))
		finally:
			wx.EndBusyCursor()

	#----------------------------------------------
#	def __on_save_emr_by_last_mod(self, event):
#		# sanity checks
#		pat = gmPerson.gmCurrentPatient()
#		if not pat.connected:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR journal by last modification time. No active patient.'))
#			return False
#
#		# get file name
#		aWildcard = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
#		aDefDir = gmTools.gmPaths().user_work_dir
#		fname = '%s-%s_%s.txt' % (_('journal_by_last_mod_time'), pat['lastnames'], pat['firstnames'])
#		dlg = wx.FileDialog (
#			parent = self,
#			message = _("Save patient's EMR journal as..."),
#			defaultDir = aDefDir,
#			defaultFile = fname,
#			wildcard = aWildcard,
#			style = wx.FD_SAVE
#		)
#		choice = dlg.ShowModal()
#		fname = dlg.GetPath()
#		dlg.DestroyLater()
#		if choice != wx.ID_OK:
#			return True
#
#		_log.debug('exporting EMR journal (by last mod) to [%s]' % fname)
#
#		exporter = gmPatientExporter.cEMRJournalExporter()
#
#		wx.BeginBusyCursor()
#		try:
#			fname = exporter.save_to_file_by_mod_time(filename = fname, patient = pat)
#		except Exception:
#			wx.EndBusyCursor()
#			_log.exception('error exporting EMR')
#			gmGuiHelpers.gm_show_error (
#				_('Error exporting patient EMR as journal by last modification time.'),
#				_('EMR journal export')
#			)
#			return
#		wx.EndBusyCursor()
#
#		gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported EMR as journal by last modification time into file [%s].') % fname, beep=False)
#
#		return True

#	#----------------------------------------------
#	def __on_save_emr_as_journal(self, event):
#		# sanity checks
#		pat = gmPerson.gmCurrentPatient()
#		if not pat.connected:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR journal. No active patient.'))
#			return False
#		# get file name
#		aWildcard = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
#		aDefDir = gmTools.gmPaths().user_work_dir
#		fname = '%s-%s_%s.txt' % (_('emr-journal'), pat['lastnames'], pat['firstnames'])
#		dlg = wx.FileDialog (
#			parent = self,
#			message = _("Save patient's EMR journal as..."),
#			defaultDir = aDefDir,
#			defaultFile = fname,
#			wildcard = aWildcard,
#			style = wx.FD_SAVE
#		)
#		choice = dlg.ShowModal()
#		fname = dlg.GetPath()
#		dlg.DestroyLater()
#		if choice != wx.ID_OK:
#			return True
#
#		_log.debug('exporting EMR journal to [%s]' % fname)
#		# instantiate exporter
#		exporter = gmPatientExporter.cEMRJournalExporter()
#
#		wx.BeginBusyCursor()
#		try:
#			fname = exporter.save_to_file_by_encounter(filename = fname, patient = pat)
#		except Exception:
#			wx.EndBusyCursor()
#			_log.exception('error exporting EMR')
#			gmGuiHelpers.gm_show_error (
#				_('Error exporting patient EMR as chronological journal.'),
#				_('EMR journal export')
#			)
#			return
#		wx.EndBusyCursor()
#
#		gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported EMR as chronological journal into file [%s].') % fname, beep=False)
#
#		return True

	#----------------------------------------------
	def __on_export_emr_by_last_mod(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR journal by last modification time. No active patient.'))
			return False

		exporter = gmPatientExporter.cEMRJournalExporter()
		wx.BeginBusyCursor()
		try:
			fname = exporter.save_to_file_by_mod_time(patient = pat)
		except Exception:
			wx.EndBusyCursor()
			_log.exception('error exporting EMR')
			gmGuiHelpers.gm_show_error (
				_('Error exporting patient EMR as journal by last modification time.'),
				_('EMR journal export')
			)
			return
		wx.EndBusyCursor()

		pat.export_area.add_file(filename = fname, hint = _('EMR journal by last modification time'))

		return True

	#----------------------------------------------
	def __on_export_emr_as_journal(self, event):
		# sanity checks
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR journal. No active patient.'))
			return False

		exporter = gmPatientExporter.cEMRJournalExporter()
		wx.BeginBusyCursor()
		try:
			fname = exporter.save_to_file_by_encounter(patient = pat)
		except Exception:
			wx.EndBusyCursor()
			_log.exception('error exporting EMR')
			gmGuiHelpers.gm_show_error (
				_('Error exporting patient EMR as chronological journal.'),
				_('EMR journal export')
			)
			return
		wx.EndBusyCursor()

		pat.export_area.add_file(filename = fname, hint = _('EMR journal by encounter'))

		return True

	#----------------------------------------------
	def __on_export_for_medistar(self, event):
		gmNarrativeWorkflows.export_narrative_for_medistar_import (
			parent = self,
			soap_cats = 'soapu',
			encounter = None			# IOW, the current one
		)

	#----------------------------------------------
	def __on_add_tag2person(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add tag to person. No active patient.'))
			return

		tag = gmDemographicsWidgets.manage_tag_images(parent = self)
		if tag is None:
			return

		tag = curr_pat.add_tag(tag['pk_tag_image'])
		msg = _('Edit the comment on tag [%s]') % tag['l10n_description']
		comment = wx.GetTextFromUser (
			message = msg,
			caption = _('Editing tag comment'),
			default_value = gmTools.coalesce(tag['comment'], ''),
			parent = self
		)

		if comment == '':
			return

		if comment.strip() == tag['comment']:
			return

		if comment == ' ':
			tag['comment'] = None
		else:
			tag['comment'] = comment.strip()

		tag.save()

	#----------------------------------------------
	def __on_load_external_patient(self, event):
		search_immediately = gmCfgDB.get4user (
			option = 'patient_search.external_sources.immediately_search_if_single_source',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		gmPatSearchWidgets.get_person_from_external_sources(parent = self, search_immediately = search_immediately, activate_immediately = True)

	#----------------------------------------------
	def __on_export_gdt2clipboard(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export patient as GDT. No active patient.'))
			return False
		enc = 'cp850'			# FIXME: configurable
		gdt_name = curr_pat.export_as_gdt(encoding = enc)
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics as GDT to clipboard.'))
		gmGuiHelpers.file2clipboard(filename = gdt_name, announce_result = True)

	#----------------------------------------------
	def __on_export_vcard2clipboard(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export patient as VCARD. No active patient.'))
			return False
		vcf_name = curr_pat.export_as_vcard()
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics as VCARD to clipboard.'))
		gmGuiHelpers.file2clipboard(filename = vcf_name, announce_result = True)

	#----------------------------------------------
	def __on_export_linuxmednews_xml2clipboard(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export patient as XML (LinuxMedNews). No active patient.'))
			return False
		fname = curr_pat.export_as_xml_linuxmednews()
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics to XML file [%s].') % fname)
		gmGuiHelpers.file2clipboard(filename = fname, announce_result = True)

	#----------------------------------------------
	def __on_export_as_gdt(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export patient as GDT. No active patient.'))
			return False
		enc = 'cp850'			# FIXME: configurable
		fname = os.path.join(gmTools.gmPaths().user_work_dir, 'current-patient.gdt')
		curr_pat.export_as_gdt(filename = fname, encoding = enc)
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics to GDT file [%s].') % fname)

	#----------------------------------------------
	def __on_export_as_vcard(self, event):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export patient as VCARD. No active patient.'))
			return False
		fname = os.path.join(gmTools.gmPaths().user_work_dir, 'current-patient.vcf')
		curr_pat.export_as_vcard(filename = fname)
		gmDispatcher.send(signal = 'statustext', msg = _('Exported demographics to VCARD file [%s].') % fname)

	#----------------------------------------------
	def __on_import_xml_linuxmednews(self, evt):
		gmPatSearchWidgets.load_person_from_xml_linuxmednews_via_clipboard()

	#----------------------------------------------
	def __on_import_vcard_from_clipboard(self, evt):
		gmPatSearchWidgets.load_person_from_vcard_via_clipboard()

	#----------------------------------------------
	def __on_import_vcard_from_file(self, evt):
		gmPatSearchWidgets.load_person_from_vcard_file()

	#----------------------------------------------
	def __on_search_person(self, evt):
		gmDispatcher.send(signal = 'focus_patient_search')
	#----------------------------------------------
	def __on_create_new_patient(self, evt):
		gmPersonCreationWidgets.create_new_person(parent = self, activate = True)
	#----------------------------------------------
	def __on_enlist_patient_as_staff(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot add staff member. No active patient.'))
			return False
		dlg = gmStaffWidgets.cAddPatientAsStaffDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_delete_patient(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete patient. No patient active.'))
			return False
		gmDemographicsWidgets.disable_identity(identity = pat)
		return True
	#----------------------------------------------
	def __on_merge_patients(self, event):
		gmPatSearchWidgets.merge_patients(parent=self)
	#----------------------------------------------
	def __on_add_new_staff(self, event):
		"""Create new person and add it as staff."""
		if not gmPersonCreationWidgets.create_new_person(parent = self, activate = True):
			return
		dlg = gmStaffWidgets.cAddPatientAsStaffDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_edit_staff_list(self, event):
		dlg = gmStaffWidgets.cEditStaffListDlg(parent=self, id=-1)
		dlg.ShowModal()
	#----------------------------------------------
	def __on_edit_gmdbowner_password(self, evt):
		gmAuthWidgets.change_gmdbowner_password()
	#----------------------------------------------
	def __on_update_loinc(self, evt):
		gmLOINCWidgets.update_loinc_reference_data()

	#----------------------------------------------
	def __on_update_atc(self, evt):
		gmATCWidgets.update_atc_reference_data()

	#----------------------------------------------
	def __on_install_data_packs(self, evt):
		gmDataPackWidgets.manage_data_packs(parent = self)

	#----------------------------------------------
	def __on_generate_vaccines(self, evt):
		gmVaccWidgets.regenerate_generic_vaccines()

	#----------------------------------------------
	def _clean_exit(self):
		"""Cleanup helper.

		- should ALWAYS be called when this program is
		  to be terminated
		- ANY code that should be executed before a
		  regular shutdown should go in here
		- framework still functional
		"""
		_log.debug('gmTopLevelFrame._clean_exit() start')

		# shut down backend notifications listener
		if 'no_db_listener' not in _cfg.get(option = 'special'):
			listener = gmBackendListener.gmBackendListener()
			try:
				listener.shutdown()
			except Exception:
				_log.exception('cannot stop backend notifications listener thread')

		# shutdown application scripting listener
		if _scripting_listener is not None:
			try:
				_scripting_listener.shutdown()
			except Exception:
				_log.exception('cannot stop scripting listener thread')

		# shutdown timers
		self.StatusBar.clock_update_timer.Stop()
		gmTimer.shutdown()
		gmPhraseWheel.shutdown()

		# run synchronous pre-exit callback
		for call_back in self.__pre_exit_callbacks:
			try:
				call_back()
			except Exception:
				print('*** pre-exit callback failed ***')
				print('%s' % call_back)
				_log.exception('callback [%s] failed', call_back)

		# signal imminent demise to plugins
		gmDispatcher.send('application_closing')

		# do not show status line messages anymore
		gmDispatcher.disconnect(self._on_set_statustext, 'statustext')

		# remember GUI size and position
		#curr_width, curr_height = self.GetClientSize()
		curr_width, curr_height = self.GetSize()
		_log.info('GUI size at shutdown: [%s:%s]' % (curr_width, curr_height))
		curr_pos_x, curr_pos_y = self.GetScreenPosition()
		_log.info('GUI position at shutdown: [%s:%s]' % (curr_pos_x, curr_pos_y))
		if 0 not in [curr_width, curr_height]:
			try:
				gmCfgDB.set (
					option = 'main.window.width',
					value = curr_width,
					workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
				)
				gmCfgDB.set (
					option = 'main.window.height',
					value = curr_height,
					workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
				)
				gmCfgDB.set (
					option = 'main.window.position.x',
					value = curr_pos_x,
					workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
				)
				gmCfgDB.set (
					option = 'main.window.position.y',
					value = curr_pos_y,
					workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
				)
			except Exception:
				_log.exception('cannot save current client window size and/or position')

		if _cfg.get(option = 'debug'):
			print('---=== GNUmed shutdown ===---')
			try:
				print(_('You have to manually close this window to finalize shutting down GNUmed.'))
				print(_('This is so that you can inspect the console output at your leisure.'))
			except UnicodeEncodeError:
				print('You have to manually close this window to finalize shutting down GNUmed.')
				print('This is so that you can inspect the console output at your leisure.')
			print('---=== GNUmed shutdown ===---')

		# shutdown GUI exception handling
		gmExceptionHandlingWidgets.uninstall_wx_exception_handler()

		# are we clean ?
		import threading
		_log.debug("%s active threads", threading.activeCount())
		for t in threading.enumerate():
			_log.debug('thread %s', t)
			if t.name == 'MainThread':
				continue
			print('GNUmed: waiting for thread [%s] to finish' % t.name)

		_log.debug('gmTopLevelFrame._clean_exit() end')

	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def __set_window_title_template(self):
		if _cfg.get(option = 'slave'):
			self.__title_template = '%s%s: %%(pat)s [%%(prov)s@%%(wp)s in %%(site)s of %%(prax)s] (%s:%s)' % (
				gmTools._GM_TITLE_PREFIX,
				gmTools.u_chain,
				_cfg.get(option = 'slave personality'),
				_cfg.get(option = 'xml-rpc port')
			)
		else:
			self.__title_template = '%s: %%(pat)s [%%(prov)s@%%(wp)s in %%(site)s of %%(prax)s]' % gmTools._GM_TITLE_PREFIX

	#----------------------------------------------
	def __update_window_title(self):
		"""Update title of main window based on template.

		This gives nice tooltips on iconified GNUmed instances.

		User research indicates that in the title bar people want
		the date of birth, not the age, so please stick to this
		convention.
		"""
		args = {}

		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			args['pat'] = '%s %s %s (%s) #%d' % (
				gmTools.coalesce(pat['title'], '', '%.4s'),
				pat['firstnames'],
				pat['lastnames'],
				pat.get_formatted_dob(format = '%Y %b %d'),
				pat['pk_identity']
			)
		else:
			args['pat'] = _('no patient')

		args['prov'] = '%s%s.%s' % (
			gmTools.coalesce(_provider['title'], '', '%s '),
			_provider['firstnames'][:1],
			_provider['lastnames']
		)

		praxis = gmPraxis.gmCurrentPraxisBranch()
		args['wp'] = praxis.active_workplace
		args['site'] = praxis['branch']
		args['prax'] = praxis['praxis']

		self.SetTitle(self.__title_template % args)

	#----------------------------------------------
	def __save_screenshot_to_file(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-screenshot-%s-' % pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
				suffix = '.png'
			)
		return gmGuiHelpers.save_screenshot_to_file(filename = filename, widget = self, settle_time = 500)

	#----------------------------------------------
	def setup_statusbar(self):
		self.StatusBar = cStatusBar(self)
		self.SetStatusText = self.StatusBar.SetStatusText
		self.PushStatusText = self.StatusBar.PushStatusText

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
	def OnPanelSize(self, event):
		wx.LayoutAlgorithm().LayoutWindow(self.LayoutMgr, self.nb)

#==============================================================================
class cStatusBar(wx.StatusBar):

	def __init__(self, *args, **kwargs):
		try:
			kwargs['style'] = kwargs['style'] | wx.STB_SIZEGRIP | wx.STB_SHOW_TIPS
		except KeyError:
			kwargs['style']  = wx.STB_SIZEGRIP | wx.STB_SHOW_TIPS
		super().__init__(*args, **kwargs)

		self.FieldsCount = 2
		self.SetStatusWidths([-1, 225])

		self.__msg_fifo = []
		self.__normal_background_colour = self.GetBackgroundColour()
		self.__blink_background_color = 'yellow'
		self.__times_to_blink = 0
		self.__blink_counter = 0

		self.clock_update_timer = wx.PyTimer(self._cb_update_clock)
		self.clock_update_timer.Start(milliseconds = 1000)

		self.Bind(wx.EVT_LEFT_DCLICK, self._on_show_history)

	#----------------------------------------------
	def SetStatusText(self, text, i=0, beep=False):
		prev = self.previous_text
		msg = self.__update_history(text, i)
		super().SetStatusText(msg, i)
		if beep:
			wx.Bell()
		self.__initiate_blinking(text, i, prev)

	#----------------------------------------------
	def PushStatusText(self, text, field=0):
		prev = self.previous_text
		msg = self.__update_history(text, field)
		super().PushStatusText(msg, field)
		self.__initiate_blinking(text, field, prev)

	#----------------------------------------------
	def set_normal_color(self):
		return self.SetBackgroundColour(self.__normal_background_colour)

	#----------------------------------------------
	def show_history(self):
		lines = []
		for entry in self.__msg_fifo:
			lines.append('%s (%s)' % (entry['text'], ','.join(entry['timestamps'])))
		gmGuiHelpers.gm_show_info (
			title = _('Statusbar history'),
			info = _(
				'%s - now\n'
				'\n'
				'%s'
			) % (
				gmDateTime.pydt_now_here().strftime('%H:%M'),
				'\n'.join(lines)
			)
		)

	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def _cb_update_clock(self):
		"""Advances date and local time in the second slot.

		Also drives blinking activity.
		"""
		t = time.localtime(time.time())
		st = time.strftime('%Y %b %d  %H:%M:%S', t)
		self.SetStatusText(st, 1)
		if self.__times_to_blink > 0:
			self.__perhaps_blink()

	#----------------------------------------------
	def __perhaps_blink(self):
		if self.__blink_counter > self.__times_to_blink:
			self.set_normal_color()
			self.__times_to_blink = 0
			self.__blink_counter = 0
			return

		if self.SetBackgroundColour(self.__blink_background_color):
			self.__blink_counter += 1
			return

		self.set_normal_color()

	#----------------------------------------------
	def __initiate_blinking(self, text, field, previous_text):
		if field != 0:
			return
		text = text.strip()
		if text == '':
			return
		if text == previous_text:
			return
		self.__blink_counter = 0
		self.__times_to_blink = 2

	#----------------------------------------------
	def _get_previous_text(self):
		if len(self.__msg_fifo) == 0:
			return None
		return self.__msg_fifo[0]['text']

	previous_text = property(_get_previous_text)

	#----------------------------------------------
	def __update_history(self, text, field):
		if field > 0:
			return text

		text = text.strip()
		if text == '':
			return text

		now = gmDateTime.pydt_now_here().strftime('%H:%M')
		if len(self.__msg_fifo) == 0:
			self.__msg_fifo.append({'text': text, 'timestamps': [now]})
			return '%s %s' % (now, text)

		last = self.__msg_fifo[0]
		if text == last['text']:
			last['timestamps'].insert(0, now)
			return '%s %s (#%s)' % (now, text, len(last['timestamps']))

		self.__msg_fifo.insert(0, {'text': text, 'timestamps': [now]})
		if len(self.__msg_fifo) > 20:
			self.__msg_fifo = self.__msg_fifo[:20]
		return '%s %s' % (now, text)

	#----------------------------------------------
	def _on_show_history(self, evt):
		self.show_history()

	#----------------------------------------------
	def __print_msg_fifo(self, context=None):
		print('----------------------------------')
		print('Statusbar history @ [%s]:' % gmDateTime.pydt_now_here().strftime('%H:%M'))
		print('\n'.join(self.__msg_fifo))
		print('----------------------------------')

	#----------------------------------------------
	def _on_print_history(self, evt):
		evt.Skip()
		self.__print_msg_fifo()

#==============================================================================
class gmApp(wx.App):

	def OnInit(self):
		if _cfg.get(option = 'debug'):
			self.SetAssertMode(wx.APP_ASSERT_EXCEPTION | wx.APP_ASSERT_LOG)
		else:
			self.SetAssertMode(wx.APP_ASSERT_SUPPRESS)
			if callable(getattr(self, 'GTKSuppressDiagnostics', None)):
				# available from wxPython 4.2.0 only, removes all useless GTK errors on stdout
				_log.info('self.GTKSuppressDiagnostics(): suppressing GTK stdout diagnostics stream')
				self.GTKSuppressDiagnostics()

		self.__starting_up = True
		wx.ToolTip.SetAutoPop(3000)		# show tooltips for x msecs
		gmExceptionHandlingWidgets.install_wx_exception_handler()
		gmExceptionHandlingWidgets.set_client_version(_cfg.get(option = 'client_version'))
		self.__setup_wx_app_identifiers()
		gmTools.gmPaths(app_name = 'gnumed', wx = wx)
		self.__log_display_properties()
		if not self.__setup_prefs_file():
			return False

		gmExceptionHandlingWidgets.set_sender_email(gmPraxis.gmCurrentPraxisBranch().user_email)
		self.__guibroker = gmGuiBroker.GuiBroker()
		self.__setup_platform()
		if not self.__establish_backend_connection():
			return False

		if not self.__verify_db_account():
			return False

		if not self.__verify_praxis_branch():
			return False

		self.__check_db_lang()
		self.__update_workplace_list()
		self.__check_for_updates()
		if not self.__setup_scripting_listener():
			return False

		frame = gmTopLevelFrame(None, id = -1, title = _('GNUmed client'), size = (640, 440))
		frame.CentreOnScreen(wx.BOTH)
		self.SetTopWindow(frame)
		frame.Show(True)
		self.__setup_debugging_output()
		self.__setup_user_activity_timer()
		self.__setup_autoimport_timer()
		self.__register_events()
		wx.CallAfter(self._do_after_init)
		return True

	#----------------------------------------------
	def OnExit(self):
		"""Called internally by wxPython after EVT_CLOSE has been handled on last frame.

		- after destroying all application windows and controls
		- before wx.Windows internal cleanup
		"""
		_log.debug('gmApp.OnExit() start')

		self.__shutdown_user_activity_timer()
		self.__shutdown_autoimport_timer()

		if _cfg.get(option = 'debug'):
			self.RestoreStdio()
			sys.stdin = sys.__stdin__
			sys.stdout = sys.__stdout__
			sys.stderr = sys.__stderr__

		top_wins = wx.GetTopLevelWindows()
		if len(top_wins) > 0:
			_log.debug('%s top level windows still around in <app>.OnExit()', len(top_wins))
			_log.debug(top_wins)
			for win in top_wins:
				_log.debug('destroying: %s', win)
				win.DestroyLater()

		_log.debug('gmApp.OnExit() end')
		return 0

	#----------------------------------------------
	def MainLoop(self):
		_log.debug('starting main event loop')
		result = super().MainLoop()
		_log.debug('after running main event loop')
		return result

	#----------------------------------------------
	def _on_query_end_session(self, *args, **kwargs):
		wx.Bell()
		wx.Bell()
		wx.Bell()
		_log.warning('unhandled event detected: QUERY_END_SESSION')
		_log.info('we should be saving ourselves from here')
		gmLog2.flush()
		print('unhandled event detected: QUERY_END_SESSION')
	#----------------------------------------------
	def _on_end_session(self, *args, **kwargs):
		wx.Bell()
		wx.Bell()
		wx.Bell()
		_log.warning('unhandled event detected: END_SESSION')
		gmLog2.flush()
		print('unhandled event detected: END_SESSION')
	#----------------------------------------------
	def _on_app_activated(self, evt):
		if evt.GetActive():
			if self.__starting_up:
				gmHooks.run_hook_script(hook = 'app_activated_startup')
			else:
				gmHooks.run_hook_script(hook = 'app_activated')
		else:
			gmHooks.run_hook_script(hook = 'app_deactivated')

		evt.Skip()
	#----------------------------------------------
	def _on_user_activity(self, evt):
		self.user_activity_detected = True
		evt.Skip()

	#----------------------------------------------
	def _on_user_activity_timer_expired(self, cookie=None):
		if self.user_activity_detected:
			self.elapsed_inactivity_slices = 0
			self.user_activity_detected = False
			self.elapsed_inactivity_slices += 1
		else:
			if self.elapsed_inactivity_slices >= self.max_user_inactivity_slices:
#				print("User was inactive for 30 seconds.")
				pass

		self.user_activity_timer.Start(oneShot = True)

	#----------------------------------------------
	def _on_autoimport_timer_expired(self, cookie=None):
		gmWorkerThread.execute_in_worker_thread (
			payload_function = gmAutoFileImport._worker__auto_import_files,
			completion_callback = self._forwarder__restart_autoimport_timer,
			worker_name = 'auto-file-importer'
		)

	#----------------------------------------------
	# internal helpers
	#----------------------------------------------
	def _do_after_init(self):
		self.__starting_up = False
		#gmClinicalRecord.set_func_ask_user(a_func = gmEncounterWidgets.ask_for_encounter_continuation)
		self.__guibroker['horstspace.top_panel']._TCTRL_patient_selector.SetFocus()
		self.user_activity_timer.Start(oneShot = True)
		self.autoimport_timer.Start(oneShot = True)
		gmHooks.run_hook_script(hook = 'startup-after-GUI-init')
		#log_colors_known2wx()

	#----------------------------------------------
	def __setup_autoimport_timer(self):
		self.autoimport_timer = gmTimer.cTimer (
			callback = self._on_autoimport_timer_expired,
			# FIXME: make configurable
			delay = 3 * 60 * 1000		# every 3 minutes
		)

	#----------------------------------------------
	def _forwarder__restart_autoimport_timer(self, import_result):
		"""Called from worker thread as completion callback."""
		wx.CallAfter(self.autoimport_timer.Start, oneShot = True)

	#----------------------------------------------
	def __shutdown_autoimport_timer(self):
		try:
			self.autoimport_timer.Stop()
			del self.autoimport_timer
		except Exception:
			pass

	#----------------------------------------------
	def __setup_user_activity_timer(self):
		self.user_activity_detected = True
		self.elapsed_inactivity_slices = 0
		# FIXME: make configurable
		self.max_user_inactivity_slices = 15	# 15 * 2000ms == 30 seconds
		self.user_activity_timer = gmTimer.cTimer (
			callback = self._on_user_activity_timer_expired,
			delay = 2000			# hence a minimum of 2 and max of 3.999... seconds after which inactivity is detected
		)

	#----------------------------------------------
	def __shutdown_user_activity_timer(self):
		try:
			self.user_activity_timer.Stop()
			del self.user_activity_timer
		except Exception:
			pass

	#----------------------------------------------
	def __register_events(self):
		self.Bind(wx.EVT_QUERY_END_SESSION, self._on_query_end_session)
		self.Bind(wx.EVT_END_SESSION, self._on_end_session)

		# You can bind your app to wx.EVT_ACTIVATE_APP which will fire when your
		# app gets/looses focus, or you can wx.EVT_ACTIVATE with any of your
		# toplevel windows and call evt.GetActive() in the handler to see whether
		# it is gaining or losing focus.
		self.Bind(wx.EVT_ACTIVATE_APP, self._on_app_activated)

		self.Bind(wx.EVT_MOUSE_EVENTS, self._on_user_activity)
		self.Bind(wx.EVT_KEY_DOWN, self._on_user_activity)

	#----------------------------------------------
	def __setup_debugging_output(self):
		if not _cfg.get(option = 'debug'):
			return

		self.RedirectStdio()
		self.SetOutputWindowAttributes(title = _('GNUmed STDOUT/STDERR window'))
		# print this so people know what this window is for
		# and don't get surprised when it pops up later
		print('---=== GNUmed startup ===---')
		print(_('redirecting STDOUT/STDERR to this log window'))
		print('---=== GNUmed startup ===---')

	#----------------------------------------------
	def __setup_wx_app_identifiers(self):
		# set this so things like "wx.StandardPaths.GetDataDir()" work as expected
		self.SetAppName('gnumed')
		self.SetVendorName('gnumed_community')
		try:
			self.SetAppDisplayName('GNUmed %s' % _cfg.get(option = 'client_version'))
		except AttributeError:
			_log.info('SetAppDisplayName() not supported')
		try:
			self.SetVendorDisplayName('The GNUmed Development Community.')
		except AttributeError:
			_log.info('SetVendorDisplayName() not supported')

	#----------------------------------------------
	def __log_display_properties(self):
		dw, dh = wx.DisplaySize()
		_log.info('display size: %s:%s' % (wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X), wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)))
		_log.debug('display size: %s:%s %s mm', dw, dh, wx.DisplaySizeMM())
		for disp_idx in range(wx.Display.GetCount()):
			disp = wx.Display(disp_idx)
			disp_mode = disp.CurrentMode
			_log.debug('display [%s] "%s": primary=%s, client_area=%s, geom=%s, vid_mode=[%sbpp across %sx%spx @%sHz]',
				disp_idx, disp.Name, disp.IsPrimary(), disp.ClientArea, disp.Geometry,
				disp_mode.bpp, disp_mode.Width, disp_mode.Height, disp_mode.refresh
			)

	#----------------------------------------------
	def __check_for_updates(self):
		if _cfg.get(option = 'skip-update-check'):
			return

		do_check = gmCfgDB.get4workplace (
			option = 'horstspace.update.autocheck_at_startup',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = True
		)
		if not do_check:
			return

		gmCfgWidgets.check_for_updates(do_async = True)

	#----------------------------------------------
	def __establish_backend_connection(self):
		"""Handle all the database related tasks necessary for startup."""
		override = _cfg.get(option = '--override-schema-check', source_order = [('cli', 'return')])
		from Gnumed.wxpython import gmAuthWidgets
		connected = gmAuthWidgets.connect_to_database (
			expected_version = gmPG2.map_client_branch2required_db_version[_cfg.get(option = 'client_branch')],
			require_version = not override
		)
		if connected:
			gmCfgDB.log_all_options()
			return True

		_log.warning("Login attempt unsuccessful. Can't run GNUmed without database connection")
		return False

	#----------------------------------------------
	def __verify_db_account(self):
		# check account <-> staff member association
		global _provider
		try:
			_provider = gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())
		except ValueError:
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

		return True

	#----------------------------------------------
	def __verify_praxis_branch(self):

		if not gmPraxisWidgets.set_active_praxis_branch(no_parent = True):
			_log.debug('failed to activate branch')
			return False

		creds = gmConnectionPool.gmConnectionPool().credentials
		msg = '\n'
		msg += _('Database <%s> on <%s>') % (
			creds.database,
			gmTools.coalesce(creds.host, 'localhost')
		)
		msg += '\n\n'
		praxis = gmPraxis.gmCurrentPraxisBranch()
		msg += _('Branch "%s" of praxis "%s"\n') % (
			praxis['branch'],
			praxis['praxis']
		)
		msg += '\n\n'
		banner = praxis.db_logon_banner
		if banner.strip() == '':
			return True

		msg += banner
		msg += '\n\n'
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			None,		#self.GetTopWindow(),				# freezes
			-1,
			caption = _('Verifying database'),
			question = gmTools.wrap(msg, 60, initial_indent = '    ', subsequent_indent = '    '),
			button_defs = [
				{'label': _('Connect'), 'tooltip': _('Yes, connect to this database.'), 'default': True},
				{'label': _('Disconnect'), 'tooltip': _('No, do not connect to this database.'), 'default': False}
			]
		)
		log_on = dlg.ShowModal()
		dlg.DestroyLater()
		if log_on == wx.ID_YES:
			_log.debug('returning for logon')
			return True

		_log.info('user decided to not connect to this database')
		return False

	#----------------------------------------------
	def __update_workplace_list(self):
		wps = gmPraxis.gmCurrentPraxisBranch().workplaces
		if len(wps) == 0:
			return

		prefs_file = _cfg.get(option = 'user_preferences_file')
		gmCfgINI.set_option_in_INI_file (
			filename = prefs_file,
			group = 'profile %s' % _cfg.get(option = 'backend_profile'),
			option = 'last known workplaces',
			value = wps
		)
		_cfg.reload_file_source(filename = prefs_file)

	#----------------------------------------------
	def __setup_prefs_file(self):
		"""Setup access to a config file for storing preferences."""

		paths = gmTools.gmPaths()
		candidates = []
		explicit_file = _cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
		if explicit_file is not None:
			candidates.append(explicit_file)
		# provide a few fallbacks in the event the --conf-file isn't writable
		candidates.append(os.path.join(paths.user_config_dir, 'gnumed.conf'))
		candidates.append(os.path.join(paths.local_base_dir, 'gnumed.conf'))
		candidates.append(os.path.join(paths.working_dir, 'gnumed.conf'))

		prefs_file = None
		for candidate in candidates:
			try:
				open(candidate, 'a+').close()
				prefs_file = candidate
				break
			except IOError:
				continue

		if prefs_file is None:
			msg = _(
				'Cannot find configuration file in any of:\n'
				'\n'
				' %s\n'
				'You may need to use the command line option\n'
				'\n'
				'	--conf-file=<FILE>'
			) % '\n '.join(candidates)
			gmGuiHelpers.gm_show_error(msg, _('Checking configuration files'))
			return False

		_cfg.set_option(option = 'user_preferences_file', value = prefs_file)
		_log.info('user preferences file: %s', prefs_file)

		return True

	#----------------------------------------------
	def __setup_scripting_listener(self):
		if not _cfg.get(option = 'slave'):
			return True

		from socket import error as SocketError
		from Gnumed.pycommon import gmScriptingListener
		from Gnumed.wxpython import gmMacro

		slave_personality = gmTools.coalesce (
			_cfg.get (
				group = 'workplace',
				option = 'slave personality',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('user', 'return'),
					('system', 'return')
				]
		 	),
			'gnumed-client'
		)
		_cfg.set_option(option = 'slave personality', value = slave_personality)

		# FIXME: handle port via /var/run/
		port = int (
			gmTools.coalesce (
				_cfg.get (
					group = 'workplace',
					option = 'xml-rpc port',
					source_order = [
						('explicit', 'return'),
						('workbase', 'return'),
						('user', 'return'),
						('system', 'return')
					]
				),
				9999
			)
		)
		_cfg.set_option(option = 'xml-rpc port', value = port)

		macro_executor = gmMacro.cMacroPrimitives(personality = slave_personality)
		global _scripting_listener
		try:
			_scripting_listener = gmScriptingListener.cScriptingListener(port = port, macro_executor = macro_executor)
		except SocketError as e:
			_log.exception('cannot start GNUmed XML-RPC server')
			gmGuiHelpers.gm_show_error (
				error = (
					'Cannot start the GNUmed server:\n'
					'\n'
					' [%s]'
				) % e,
				title = _('GNUmed startup')
			)
			return False

		return True

	#----------------------------------------------
	def __setup_platform(self):

		import wx.lib.colourdb
		wx.lib.colourdb.updateColourDB()

		traits = self.GetTraits()
		try:
			_log.info('desktop environment: [%s]', traits.GetDesktopEnvironment())
		except Exception:
			pass

		if wx.Platform == '__WXMSW__':
			_log.info('running on MS Windows')
		elif wx.Platform == '__WXGTK__':
			_log.info('running on GTK (probably Linux)')
		elif wx.Platform == '__WXMAC__':
			_log.info('running on Mac OS')
			wx.SystemOptions.SetOptionInt('mac.textcontrol-use-spell-checker', 1)
		else:
			_log.info('running on an unknown platform (%s)' % wx.Platform)

	#----------------------------------------------
	def __check_db_lang(self):
		if gmI18N.system_locale is None or gmI18N.system_locale == '':
			_log.warning("system locale is undefined (probably meaning 'C')")
			return True

		curr_db_lang = gmPG2.get_current_user_language()
		_log.debug('current user language in DB: %s', curr_db_lang)
		if curr_db_lang is None:
			_log.info('no language selected in DB, trying to set')
			for lang in [gmI18N.system_locale_level['full'], gmI18N.system_locale_level['country'], gmI18N.system_locale_level['language']]:
				if len(lang) == 0:
					continue
				if gmPG2.set_user_language(language = lang):
					_log.debug("Successfully set database language to [%s]." % lang)
					return True

				_log.error('Cannot set database language to [%s].' % lang)
			return True

		if curr_db_lang == gmI18N.system_locale_level['full']:
			_log.debug('Database locale (%s) up to date.' % curr_db_lang)
			return True

		if curr_db_lang == gmI18N.system_locale_level['country']:
			_log.debug('Database locale (%s) matches system locale (%s) at country level.' % (curr_db_lang, gmI18N.system_locale))
			return True

		if curr_db_lang == gmI18N.system_locale_level['language']:
			_log.debug('Database locale (%s) matches system locale (%s) at language level.' % (curr_db_lang, gmI18N.system_locale))
			return True

		_log.warning('database locale [%s] does not match system locale [%s]' % (curr_db_lang, gmI18N.system_locale))
		sys_lang2ignore = _cfg.get (
			group = 'backend',
			option = 'ignored mismatching system locale',
			source_order = [('explicit', 'return'), ('local', 'return'), ('user', 'return'), ('system', 'return')]
		)
		if gmI18N.system_locale == sys_lang2ignore:
			_log.info('configured to ignore system-to-database locale mismatch')
			return True

		# no match, not ignoring
		msg = _(
			"The currently selected database language ('%s') does\n"
			"not match the current system language ('%s').\n"
			"\n"
			"Do you want to set the database language to '%s' ?\n"
		) % (curr_db_lang, gmI18N.system_locale, gmI18N.system_locale)
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			None,
			-1,
			caption = _('Checking database language settings'),
			question = msg,
			button_defs = [
				{'label': _('Set'), 'tooltip': _('Set your database language to [%s].') % gmI18N.system_locale, 'default': True},
				{'label': _("Don't set"), 'tooltip': _('Do not set your database language now.'), 'default': False}
			],
			show_checkbox = True,
			checkbox_msg = _('Remember to ignore language mismatch'),
			checkbox_tooltip = _(
				'Checking this will make GNUmed remember your decision\n'
				'until the system language is changed.\n'
				'\n'
				'You can also reactivate this inquiry by removing the\n'
				'corresponding "ignore" option from the configuration file\n'
				'\n'
				' [%s]'
			) % _cfg.get(option = 'user_preferences_file')
		)
		decision = dlg.ShowModal()
		remember2ignore_this_mismatch = dlg._CHBOX_dont_ask_again.GetValue()
		dlg.DestroyLater()
		if decision == wx.ID_NO:
			if not remember2ignore_this_mismatch:
				return True
			_log.info('User did not want to set database locale. Ignoring mismatch next time.')
			gmCfgINI.set_option_in_INI_file (
				filename = _cfg.get(option = 'user_preferences_file'),
				group = 'backend',
				option = 'ignored mismatching system locale',
				value = gmI18N.system_locale
			)
			return True

		for lang in [gmI18N.system_locale_level['full'], gmI18N.system_locale_level['country'], gmI18N.system_locale_level['language']]:
			if len(lang) == 0:
				continue
			if gmPG2.set_user_language(language = lang):
				_log.debug("Successfully set database language to [%s]." % lang)
				return True

			_log.error('Cannot set database language to [%s].' % lang)
		# no match found but user wanted to set language anyways, so force it
		_log.info('forcing database language to [%s]', gmI18N.system_locale_level['country'])
		gmPG2.force_user_language(language = gmI18N.system_locale_level['country'])
		return True

#==============================================================================
def _signal_debugging_monitor(*args, **kwargs):
	try:
		kwargs['originated_in_database']
		print('==> got notification from database "%s":' % kwargs['signal'])
	except KeyError:
		print('==> received signal from client: "%s"' % kwargs['signal'])

	del kwargs['signal']
	for key in kwargs:
		# careful because of possibly limited console output encoding
		try: print('    [%s]: %s' % (key, kwargs[key]))
		except Exception: print('cannot print signal information')

#==============================================================================
def _safe_wxEndBusyCursor():
	try: _original_wxEndBusyCursor()
	except wx.wxAssertionError: pass

#------------------------------------------------------------------------------
def setup_safe_wxEndBusyCursor():
	# monkey patch wxPython, needed on Windows, OSX, ...
	#if os.name != 'nt':
	#	return
	global _original_wxEndBusyCursor
	_original_wxEndBusyCursor = wx.EndBusyCursor
	wx.EndBusyCursor = _safe_wxEndBusyCursor
	_log.debug('monkey patched wx.EndBusyCursor:')
	_log.debug('[%s] -> [%s]', _original_wxEndBusyCursor, _safe_wxEndBusyCursor)

#==============================================================================
def setup_callbacks():
	gmPerson.set_yielder(wx.Yield)
	gmClinicalRecord.set_delayed_executor(wx.CallAfter)

#==============================================================================
def log_colors_known2wx():
	col_db = wx.ColourDatabase()
	col_names = []
	for r in range(256):
		for g in range(256):
			for b in range(256):
				wx.Yield()
				col = wx.Colour(r,g,b)
				col_name = col_db.FindName(col)
				if col_name:
					col_names.append(col_name)
	_log.debug('enumerated known colors')
	log_lines = []
	for col_name in sorted(col_names):
		wx.Yield()
		col = col_db.Find(col_name)
		log_lines.append(f'{col_name:<25} {col.red:<6} {col.green:<6} {col.blue:<6} {col.IsOk()}')
	gmLog2.log_multiline (
		level = logging.DEBUG,
		message = 'RGB colors known by name on this system:',
		text = '\n'.join(log_lines)
	)
	wx.Bell()

#==============================================================================
def main():
	# make sure signals end up in the main thread,
	# no matter the thread they came from
	gmDispatcher.set_main_thread_caller(wx.CallAfter)
	if _cfg.get(option = 'debug'):
		gmDispatcher.connect(receiver = _signal_debugging_monitor)
		_log.debug('gmDispatcher signal monitor activated')
	if 'debug_sizers' not in _cfg.get(option = 'special'):
		try:
			wx.SizerFlags.DisableConsistencyChecks()
			_log.debug('fatal sizer consistency checks disabled')
		except AttributeError:
			pass
	setup_safe_wxEndBusyCursor()
	setup_callbacks()

	# create an instance of our GNUmed main application
	# - do not redirect stdio (yet)
	# - allow signals to be delivered
	app = gmApp(redirect = False, clearSigInt = False)
	_log.debug('--== GUI startup finished ==----------------------------')
	app.MainLoop()

#==============================================================================
# Main
#==============================================================================
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()

	_log.info('Starting up as main module.')
	main()

#==============================================================================
