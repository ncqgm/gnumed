"""GnuMed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).
	
	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/cfmoro/soap_input/Attic/gmEMRStructWidgets.py,v $
# $Id: gmEMRStructWidgets.py,v 1.4 2005-01-24 16:57:38 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmLog, gmI18N
from Gnumed.business import gmEMRStructItems, gmPatient, gmSOAPimporter
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers
from Gnumed.pycommon.gmPyCompat import *

import SOAPMultiSash

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
class cEpisodeEditor(wx.wxPanel):
	"""
	This widget allows the creation and addition of episodes.

	On top, a table displays the existing episodes (date, description, open).
	Under the table: there is an adequate editor for each of the fields of
	the edited episodes.
	Under the editor: control buttons 

	   At startup, the table is populated with existing episodes. Clear and add buttons
	   are displayed. By pressing the add button, sanity checks are performed, the
	   new episode is created and the list is refreshed from backend.
	   Editing an episode: by right clicking over an episode row in the table, a
	   pop up menu with the 'Edit episode' option is shown, that make the values
	   to be displayed editor fields for the user to modify them. Bottom buttons show
	   'Restore' and 'Update'  actions. On update, the editing fields are cleaned and
	   the contents of the table, refresed from backend.
	"""
	def __init__(self, parent, id, pk_health_issue):

		# parent class initialization
		wx.wxPanel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize,
			style = wx.wxNO_BORDER
		)

		# edited episodes' issue's PK
		self.__pk_health_issue = pk_health_issue
		pat = gmPatient.gmCurrentPatient()
		# patient EMR
		self.__emr = pat.get_clinical_record()
		# patient episodes
		self.__episodes = None
		# selected episode
		self.__selected_episode = None
		
		# ui contruction and event handling set up
		self.__do_layout()
		self.__register_interests()
		
		self.__refresh_episode_list()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.
		"""
		# instantiate and initialize widgets
		# - episodes list
		self.__LST_episodes = wx.wxListCtrl(
			self,
			-1,
			style = wx.wxLC_REPORT | wx.wxSUNKEN_BORDER | wx.wxLC_SINGLE_SEL
		)
		self.__LST_episodes.InsertColumn(0, _('Start date'))
		self.__LST_episodes.InsertColumn(1, _('Description'), wx.wxLIST_FORMAT_RIGHT)
#		self.__LST_episodes.InsertColumn(2, _('Category'))
		self.__LST_episodes.InsertColumn(2, _('Is open'))
#		self.__LST_episodes.InsertColumn(3, _('Is open'))
		self.__LST_episodes.SetColumnWidth(0, 100)
		self.__LST_episodes.SetColumnWidth(1, 230)
		self.__LST_episodes.SetColumnWidth(2, 70)
#		self.__LST_episodes.SetColumnWidth(3, 70)
		szr_list = wx.wxStaticBoxSizer (
			wx.wxStaticBox(self, -1, _('Episode list')),
			wx.wxHORIZONTAL
		)
		szr_list.Add(self.__LST_episodes, 1, wx.wxEXPAND | wx.wxTOP, border=4)

		# - episode editor
		self.__STT_description = wx.wxStaticText(self, -1, _('Description'))
		# FIXME: configure, attach matcher (Karsten)
		self.__PRW_description = gmPhraseWheel.cPhraseWheel(self, -1)
		self.__STT_soap_cat = wx.wxStaticText(self, -1, _('Category'))
		soap_choices = [_('--Select category--')]
		soap_choices.extend(gmSOAPimporter.soap_bundle_SOAP_CATS)
		self.__CHC_soap_cat = wx.wxChoice(self, -1, choices=soap_choices)
		szr_input = wx.wxFlexGridSizer(cols = 2, rows = 2, vgap = 4, hgap = 4)
		szr_input.AddGrowableCol(1)
		szr_input.Add(self.__STT_description, 0, wx.wxSHAPED | wx.wxALIGN_CENTER)
		# FIXME: avoid phrasewheel to grow vertically
		szr_input.Add(self.__PRW_description, 1, wx.wxEXPAND)
		szr_input.Add(self.__STT_soap_cat, 0, wx.wxSHAPED | wx.wxALIGN_CENTER)
		szr_input.Add(self.__CHC_soap_cat, 0, wx.wxSHAPED)

		# - buttons
		self.__BTN_add = wx.wxButton(self, -1, _('Add episode'))
		self.__BTN_clear = wx.wxButton(self, -1, _('Clear'))
		szr_actions = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_actions.Add(self.__BTN_add, 0, wx.wxSHAPED)
		szr_actions.Add(self.__BTN_clear, 0, wx.wxSHAPED | wx.wxALIGN_RIGHT)

		# arrange widgets
#		# FIXME: can we not simply merge szr_editor and szr_main ?
#		szr_editor = wx.wxStaticBoxSizer (
#			wx.wxStaticBox(self, -1, _('Episode editor')),
#			wx.wxVERTICAL
#		)
#		szr_editor.Add(szr_input, 1, wx.wxEXPAND | wx.wxALIGN_LEFT | wx.wxTOP, border=4)
#		szr_editor.Add(szr_actions, 1, wx.wxALIGN_CENTER | wx.wxTOP, border = 10)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(szr_list, 2, wx.wxEXPAND)
		szr_main.Add(szr_input, 1, wx.wxEXPAND | wx.wxALIGN_LEFT | wx.wxTOP, border=4)
		szr_main.Add(szr_actions, 1, wx.wxALIGN_CENTER | wx.wxTOP, border = 10)
#		szr_main.Add(szr_editor, 1, wx.wxEXPAND | wx.wxTOP, border=4)

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	def __refresh_episode_list(self):
		"""Update the table of episodes.
		"""
		self.__selected_episode = None
		self.__LST_episodes.DeleteAllItems()

		# populate table and cache episode list
		episodes = self.__emr.get_episodes()
		self.__episodes = {}
		for idx in range(len(episodes)):
			epi = episodes[idx]
			# FIXME: this is NOT the proper date to show !
			self.__LST_episodes.InsertStringItem(idx,  str(epi['episode_modified_when']))
#			self.__LST_episodes.SetStringItem(idx, 0, str(epi['episode_modified_when']))
			self.__LST_episodes.SetStringItem(idx, 1, epi['description'])
#			self.__LST_episodes.SetStringItem(idx, 2, epi['soap_cat'])
			self.__LST_episodes.SetStringItem(idx, 2, str(epi['episode_open']))
#			self.__LST_episodes.SetStringItem(idx, 3, str(epi['episode_open']))
			self.__episodes[idx] = epi
			self.__LST_episodes.SetItemData(idx, idx)

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals.
		"""
		# wxPython events
		wx.EVT_LIST_ITEM_ACTIVATED(self, self.__LST_episodes.GetId(), self.__on_episode_activated)
		wx.EVT_BUTTON(self.__BTN_clear, self.__BTN_clear.GetId(), self.__on_clear)
		wx.EVT_BUTTON(self.__BTN_add, self.__BTN_add.GetId(), self.__on_add)
	#--------------------------------------------------------
	def __on_episode_activated(self, event):
		"""
		When the user activates an episode on the table (by double clicking or
		pressing enter)
		"""
		sel_idx = self.__LST_episodes.GetItemData(event.m_itemIndex)
		self.__selected_episode = self.__episodes[sel_idx]
		print 'Selected episode: ', self.__selected_episode
		self.__PRW_description.SetValue(self.__selected_episode['description'])
		self.__CHC_soap_cat.SetStringSelection(self.__selected_episode['soap_cat'])
		self.__BTN_add.SetLabel(_('Update'))
		self.__BTN_clear.SetLabel(_('Cancel'))
		event.Skip()
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		On new episode: clear input fields
		On episode edition: clear input fields and restores actions
		buttons for a new episode.
		"""
		self.__PRW_description.Clear()
		self.__CHC_soap_cat.SetSelection(0)
		if not self.__selected_episode is None:
			# on episode edition
			self.__BTN_add.SetLabel(_('Add episode'))
			self.__BTN_clear.SetLabel(_('Clear'))
			self.__selected_episode = None
		event.Skip()

	#--------------------------------------------------------
	def __on_add(self, event):
		"""
		On new episode: add episode to backend
		On episode edition: update episode in backend, clear input fields
		and restore buttons for a new episode
		"""
		description = self.__PRW_description.GetValue()
		soap_cat = self.__CHC_soap_cat.GetStringSelection()

		# sanity check
		if self.__selected_episode is None:
			action = 'create'
		else:
			action = 'update'
		if (description is None or
		 description.strip() == '' or
		 self.__CHC_soap_cat.GetSelection() == 0):
			msg = _('Cannot %s episode.\nAll required fields must be filled.') % action
			gmGuiHelpers.gm_show_error(msg, _('episode editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid description:soap cat [%s:%s]' % (description, soap_cat))
			return False

		if self.__selected_episode is None:
			# on new episode
			#self.__emr.add_episode(episode_name= , pk_health_issue=self.__pk_health_issue, soap_cat= self.__CHC_soap_cat.GetStringSelection())
			print 'Creating episode: %s , soap: %s' % (self.__PRW_description.GetValue(),self.__CHC_soap_cat.GetStringSelection())
		else:
			# on episode edition
			#self.__selected_episode['description'] = self.__PRW_description.GetValue()
			#self.__selected_episode.save_payload()
			print 'Renaming episode: %s' % self.__selected_episode

		# do clear stuff
		self.__on_clear(event)
		# refresh episode table
		self.__refresh_episode_list

#== Module convenience functions (for standalone use) =======================
def prompted_input(prompt, default=None):
	"""
	Obtains entry from standard input
	
	promp - Promt text to display in standard output
	default - Default value (for user to press only intro)
	"""
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input

#------------------------------------------------------------
def askForPatient():
	"""
		Main module application patient selection function.
	"""
	
	# Variable initializations
	pat_searcher = gmPatient.cPatientSearcher_SQL()

	# Ask patient
	patient_term = prompted_input("\nPatient search term (or 'bye' to exit) (eg. Kirk): ")

	if patient_term == 'bye':
		return None
	search_ids = pat_searcher.get_patient_ids(search_term = patient_term)
	if search_ids is None or len(search_ids) == 0:
		prompted_input("No patient matches the query term. Press any key to continue.")
		return None
	elif len(search_ids) > 1:
		prompted_input("Various patients match the query term. Press any key to continue.")
		return None
	patient_id = search_ids[0]
	patient = gmPatient.gmCurrentPatient(patient_id)

	return patient

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	import sys
	from Gnumed.pycommon import gmCfg, gmPG

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting EMR struct editor...")

	_cfg = gmCfg.gmDefCfgFile	 
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# make sure we have a db connection
		gmPG.set_default_client_encoding('latin1')
		pool = gmPG.ConnectionPool()

		# obtain patient
		patient = askForPatient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# display standalone editor
		application = wx.wxPyWidgetTester(size=(470,300))
		episode_editor = cEpisodeEditor(application.frame, -1, pk_health_issue=1)

		application.frame.Show(True)
		application.MainLoop()

		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	try:
		pool.StopListeners()
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
		raise

	_log.Log (gmLog.lInfo, "closing notes input...")
#================================================================
# $Log: gmEMRStructWidgets.py,v $
# Revision 1.4  2005-01-24 16:57:38  ncq
# - some cleanup here and there
#
#
