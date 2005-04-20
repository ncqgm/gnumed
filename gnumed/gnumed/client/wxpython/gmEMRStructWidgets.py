"""GnuMed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).
	
	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRStructWidgets.py,v $
# $Id: gmEMRStructWidgets.py,v 1.4 2005-04-20 22:09:54 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmLog, gmI18N, gmMatchProvider
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmEditArea
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
	
# module level constants
dialog_CANCELLED = -1
dialog_OK = -2

#============================================================
class cNewHealthIssuePopup(wx.wxDialog):
	def __init__ (self, parent, id, title, pos, size, style, name):
		wx.wxDialog.__init__(self, parent, id, title, pos, size, style, name)
		self.__wxID_BTN_SAVE = wx.wxNewId()
		self.__wxID_BTN_RESET = wx.wxNewId()
		self.__do_layout()
		self.__register_events()
	#------------------------------------------------------------------
	def __do_layout(self):
		self.__editarea = cHealthIssueEditArea(self, -1, wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL)

		self.__btn_SAVE = wx.wxButton(self, self.__wxID_BTN_SAVE, _("Save"))
		self.__btn_SAVE.SetToolTipString(_('save entry into medical record'))
		self.__btn_RESET = wx.wxButton(self, self.__wxID_BTN_RESET, _("Reset"))
		self.__btn_RESET.SetToolTipString(_('reset entry'))
		self.__btn_CANCEL = wx.wxButton(self, wx.wxID_CANCEL, _("Cancel"))
#		self.__btn_CANCEL.SetToolTipString(_('discard entry and cancel'))

		szr_buttons = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_buttons.Add(self.__btn_SAVE, 1, wx.wxEXPAND | wx.wxALL, 1)
		szr_buttons.Add(self.__btn_RESET, 1, wx.wxEXPAND | wx.wxALL, 1)
		szr_buttons.Add(self.__btn_CANCEL, 1, wx.wxEXPAND | wx.wxALL, 1)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__editarea, 1, wx.wxEXPAND)
		szr_main.Add(szr_buttons, 0, wx.wxEXPAND)

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
		wx.EVT_BUTTON(self.__btn_SAVE, self.__wxID_BTN_SAVE, self._on_SAVE_btn_pressed)
		wx.EVT_BUTTON(self.__btn_RESET, self.__wxID_BTN_RESET, self._on_RESET_btn_pressed)
		wx.EVT_BUTTON(self.__btn_CANCEL, wx.wxID_CANCEL, self._on_CANCEL_btn_pressed)

		wx.EVT_CLOSE(self, self._on_CANCEL_btn_pressed)

		# client internal signals
#		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._on_activating_patient)
#		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._on_application_closing)
#		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self.on_patient_selected)

		return 1
	#--------------------------------------------------------
	def _on_SAVE_btn_pressed(self, evt):
		print "saving"
		self.EndModal(wx.wxID_OK)
	#--------------------------------------------------------
	def _on_CANCEL_btn_pressed(self, evt):
		"""
		Configure appropiate *dialog* return value when the user clicks the
		window system's closer (usually X)
		"""
		print "cancelling"
		self.EndModal(wx.wxID_CANCEL)
	#--------------------------------------------------------
	def _on_RESET_btn_pressed(self, evt):
		print "resetting fields"
#============================================================
class cHealthIssueEditArea(gmEditArea.cEditArea2):
	"""Edit Area for Health Issues.

	They correspond to Past History items.
	"""
	def __init__(self, parent, id, pos, size, style):
		gmEditArea.cEditArea2.__init__(self, parent, id, pos, size, style)
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _('Condition'))
		self._add_prompt(line = 2, label = _('Onset'))
		self._add_prompt(line = 3, label = _('Progress Note'))
	#----------------------------------------------------
	def _define_fields(self, parent):
		# condition
		cmd = """
			select distinct on (description) id, description
			from clin_health_issue where description %(fragment_condition)s"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', cmd)
		mp.setThresholds(aWord=2, aSubstring=5)
		self.fld_condition = gmPhraseWheel.cPhraseWheel (
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.wxSIMPLE_BORDER
		)
		gmEditArea._decorate_editarea_field(self.fld_condition)
		self._add_field (
			line = 1,
			pos = 1,
			widget = self.fld_condition,
			weight = 3
		)
		# Onset
		label = wx.wxStaticText (
			parent = parent,
			id = -1,
			label = '%s: ' % _('Age'),
			style = wx.wxALIGN_CENTRE
		)
		self._add_field (
			line = 2,
			pos = 1,
			widget = label,
			weight = 0
		)
		# FIXME: gmDateTimeInput
		self.fld_age_onset = gmEditArea.cEditAreaField(parent)
		self._add_field (
			line = 2,
			pos = 2,
			widget = self.fld_age_onset,
			weight = 2
		)
		label = wx.wxStaticText (
			parent = parent,
			id = -1,
			label = '%s: ' % _('Year'),
			style = wx.wxALIGN_CENTRE
		)
		self._add_field (
			line = 2,
			pos = 3,
			widget = label,
			weight = 0
		)
		# FIXME: gmDateTimeInput
		self.fld_year_onset = gmEditArea.cEditAreaField(parent)
		self._add_field (
			line = 2,
			pos = 4,
			widget = self.fld_year_onset,
			weight = 2
		)
		# Progress note
		cmd = """
			select distinct on (narrative) pk, narrative
			from clin_narrative where narrative %(fragment_condition)s limit 30"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', cmd)
		mp.setThresholds(2, 4, 6)
		self.fld_progress_note = gmPhraseWheel.cPhraseWheel (
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.wxSIMPLE_BORDER
		)
		gmEditArea._decorate_editarea_field(self.fld_progress_note)
		self._add_field (
			line = 3,
			pos = 1,
			widget = self.fld_progress_note,
			weight = 1
		)
		return 1
#============================================================
class cEpisodeSelectorDlg(wx.wxDialog):
	"""
	Pop up a episode picker dialog. Returns dialog_OK if an episode was
	selected, dialog_CANCELLED else.
	With get_selected_episode() the selected episode can be requested.
	"""
	def __init__(
					self,
					parent,
					id,
					title = _('Episode selector'),
					action_txt = _('Select'),
					pk_health_issue = None,
				 	pos = wx.wxPyDefaultPosition,
				 	size = wx.wxPyDefaultSize,
				 	style = wx.wxDEFAULT_DIALOG_STYLE | wx.wxRESIZE_BORDER
				 ):
		"""
		Instantiate a new episode selector dialog.
		
		@param title Selector dialog descritive title
		@type title string
	
		@param action_txt Bottom action button display text
		@type action_txt string	
		 
		@param pk_health_issue Id of the health issue to select the episode for
		@type pk_health_issue integer
		"""
		# build ui
		wx.wxDialog.__init__(self, parent, id, title, pos, size, style)
		self.__episode_picker = cEpisodePicker(self, -1, action_txt, pk_health_issue)
		self.Fit()
		# event handling
		wx.EVT_CLOSE(self, self.__on_close)
	#--------------------------------------------------------
	def get_selected_episode(self):
		"""
		Retrieve the selected episode
		"""
		return self.__episode_picker.get_selected_episode()
	#--------------------------------------------------------
	def __on_close(self, evt):
		"""
		Configure appropiate *dialog* return value when the user clicks the
		window system's closer (usually X)
		"""
		self.EndModal(dialog_CANCELLED)
#============================================================
class cEpisodePicker(wx.wxPanel):
	"""
	This widget allows the selection and addition of episodes.
	
	On top: there is an adequate editor for each of the fields of
	the edited episodes, along action buttons.
	Below: a table displays the existing episodes (date, description, open).	
	On bottom: close button

	At startup, the table is populated with existing episodes. By pressing
	the add button, sanity checks are performed, the new episode is created,
	is set as selected episode and the dialog is closed.
	An episode in the list can be selected (and the dialog closes) by either:
	double clicking the episode; or selecting the episode and pressing the 
	bottom button.	
	
	With get_selected_episode() the selected episode can be requested.
	"""
	def __init__(self, parent, id, action_txt, pk_health_issue):
		"""
		Instantiate a new episode selector widget.
		
		@param action_txt Bottom action button display text
		@type action_txt string	
		 
		@param pk_health_issue Id of the health issue to select the episode for
		@type pk_health_issue integer		
		"""
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
		self.__pat = gmPerson.gmCurrentPatient()
		# patient episodes
		self.__episodes = None
		# selected episode
		self.__selected_episode = None
		
		# ui contruction and event handling set up
		self.__do_layout(action_txt)
		self.__register_interests()
		
		self.__refresh_episode_list()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self, action_txt):
		"""
		Arrange widgets.

		@param action_txt Bottom action button display text
		@type action_txt string			
		"""
		# instantiate and initialize widgets

		# - episode editor
		self.__STT_description = wx.wxStaticText(self, -1, _('Description'))
		# FIXME: configure, attach matcher (Karsten)
		self.__PRW_description = gmPhraseWheel.cPhraseWheel(self, -1)
		szr_input = wx.wxFlexGridSizer(cols = 2, rows = 2, vgap = 4, hgap = 4)
		szr_input.AddGrowableCol(1)
		szr_input.Add(self.__STT_description, 0, wx.wxSHAPED | wx.wxALIGN_CENTER)
		szr_input.Add(self.__PRW_description, 1, wx.wxEXPAND)

		# - buttons
		self.__BTN_add = wx.wxButton(self, -1, action_txt)
		self.__BTN_cancel = wx.wxButton(self, -1, _('Cancel'))
		szr_actions = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_actions.Add(self.__BTN_add, 0, wx.wxSHAPED)
		szr_actions.Add(self.__BTN_cancel, 0, wx.wxSHAPED | wx.wxALIGN_RIGHT)
		
		# - episodes list and new note for selected episode button
		self.__LST_episodes = wx.wxListCtrl(
			self,
			-1,
			style = wx.wxLC_REPORT | wx.wxSUNKEN_BORDER | wx.wxLC_SINGLE_SEL
		)
		self.__LST_episodes.InsertColumn(0, _('Last renamed'))
		self.__LST_episodes.InsertColumn(1, _('Description'), wx.wxLIST_FORMAT_RIGHT)
		self.__LST_episodes.InsertColumn(2, _('Is open'))
		self.__LST_episodes.SetColumnWidth(0, 100)
		self.__LST_episodes.SetColumnWidth(1, 230)
		self.__LST_episodes.SetColumnWidth(2, 70)		
		self.__BTN_action = wx.wxButton(self, -1, action_txt)				
		szr_list = wx.wxStaticBoxSizer (
			wx.wxStaticBox(self, -1, _('Episode list')),
			wx.wxVERTICAL
		)
		szr_list.Add(self.__LST_episodes, 1, wx.wxEXPAND | wx.wxTOP, border=4)
		szr_list.Add(self.__BTN_action, 0, wx.wxSHAPED | wx.wxALIGN_CENTER, border=4)
		
		# layout sizers
		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(szr_input, 1, wx.wxEXPAND | wx.wxALIGN_LEFT | wx.wxTOP, border=4)
		szr_main.Add(szr_actions, 1, wx.wxALIGN_CENTER | wx.wxTOP, border = 10)
		szr_main.Add(szr_list, 2, wx.wxEXPAND)		

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	def __refresh_episode_list(self):
		"""Update the table of episodes.
		"""
		self.__selected_episode = None
		self.__LST_episodes.DeleteAllItems()
		self.__BTN_action.Enable(False)

		# populate table and cache episode list
		emr = self.__pat.get_clinical_record()
		episodes = emr.get_episodes()
		self.__episodes = {}
		for idx in range(len(episodes)):
			epi = episodes[idx]
			# FIXME: this is NOT the proper date to show !
			self.__LST_episodes.InsertStringItem(idx,  str(epi['episode_modified_when']))
			self.__LST_episodes.SetStringItem(idx, 1, epi['description'])
			self.__LST_episodes.SetStringItem(idx, 2, str(epi['episode_open']))
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
		wx.EVT_LIST_ITEM_SELECTED(self, self.__LST_episodes.GetId(), self.__on_episode_selected)
		wx.EVT_BUTTON(self.__BTN_cancel, self.__BTN_cancel.GetId(), self.__on_cancel)
		wx.EVT_BUTTON(self.__BTN_add, self.__BTN_add.GetId(), self.__on_add)
		wx.EVT_BUTTON(self.__BTN_action, self.__BTN_action.GetId(), self.__on_action)
		
	#--------------------------------------------------------
	def __on_action(self, event):
		"""
		When the user press bottom action button for a selected episode.
		Close the dialog returning OK.
		"""
		self.GetParent().EndModal(dialog_OK)
		event.Skip()
				
	#--------------------------------------------------------
	def __on_episode_selected(self, event):
		"""
		When the user selects an episode on the table (by single clicking over one row).
		Update selected episode and if necessary, enable bottom action button.
		"""
		sel_idx = self.__LST_episodes.GetItemData(event.m_itemIndex)
		self.__selected_episode = self.__episodes[sel_idx]
		print 'Selected episode ID [%s]' % self.__selected_episode['pk_episode']
		if not self.__BTN_action.IsEnabled():
			self.__BTN_action.Enable(True)
		event.Skip()
				
	#--------------------------------------------------------
	def __on_episode_activated(self, event):
		"""
		When the user activates an episode on the table (by double clicking or
		pressing enter).
		Update selected episode and close the dialog returning OK.
		"""
		sel_idx = self.__LST_episodes.GetItemData(event.m_itemIndex)
		self.__selected_episode = self.__episodes[sel_idx]
		self.GetParent().EndModal(dialog_OK)
		event.Skip()
		
	#--------------------------------------------------------
	def __on_cancel(self, event):
		"""
		Cancel episode picking.
		Set selected episode to None and close the dialog returning CANCELLED
		"""
		self.__selected_episode = None
		self.GetParent().EndModal(dialog_CANCELLED)
		event.Skip()
		
	#--------------------------------------------------------
	def __on_add(self, event):
		"""
		Add a new episode to backend and return OK
		"""
		description = self.__PRW_description.GetValue()

		if (description is None or description.strip() == ''):
			msg = _('Cannot create episode.\nAll required fields must be filled.')
			gmGuiHelpers.gm_show_error(msg, _('episode picker'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid description [%s]' % description)
			return False

		print 'Creating episode: %s' % self.__PRW_description.GetValue()
		self.__selected_episode = self.__pat.get_clinical_record().add_episode (
			episode_name = self.__PRW_description.GetValue(),
			pk_health_issue = self.__pk_health_issue
		)
		print self.__selected_episode
		self.GetParent().EndModal(dialog_OK)
		event.Skip()
	#--------------------------------------------------------
	# Public API
	#--------------------------------------------------------	
	def get_selected_episode(self):
		"""
		Retrieve the selected episode.
		"""
		return self.__selected_episode

#============================================================
class cEpisodeEditorDlg(wx.wxDialog):
	"""
	Pop up an episode editor dialog.
	Return CANCELLED by pressing close button or window closer (X).
	"""
	def __init__(
					self,
					parent,
					id,
					title = _('Episode editor'),
					pk_health_issue=None,
				 	pos = wx.wxPyDefaultPosition,
				 	size = wx.wxPyDefaultSize,
				 	style = wx.wxDEFAULT_DIALOG_STYLE | wx.wxRESIZE_BORDER
				 ):
		"""
		Instantiate a new episode editor dialog.
		
		@param title Selector dialog descritive title
		@type title string
			 
		@param pk_health_issue Id of the health issue to select the episode for
		@type pk_health_issue integer
		"""
		# build ui
		wx.wxDialog.__init__(self, parent, id, title, pos, size, style)
		self.__episode_picker = cEpisodeEditor(self, -1, pk_health_issue)
		self.Fit()
		# event handling
		wx.EVT_CLOSE(self, self.__on_close)					
			
	#--------------------------------------------------------	
	def __on_close(self, evt):
		"""
		Return appropiate value when the user clicks the
		window system's closer (usually X)
		"""
		self.EndModal(dialog_CANCELLED)
		
#============================================================
class cEpisodeEditor(wx.wxPanel):
	"""
	This widget allows the creation and addition of episodes.
	
	On top: there is an adequate editor for each of the fields of
	the edited episodes.
	On below: a table displays the existing episodes (date, description, open).	
	On bottom: close button

	At startup, the table is populated with existing episodes. Clear and add buttons
	are displayed. By pressing the add button, after passing sanity checks, the
	new episode is created and the list is refreshed from backend.
	Editing an episode: by double clicking over an episode row in the table, 
	the episode is set in the editor fields for the user to modify them.
	Action buttons show 'Restore' and 'Update'  actions. On update, the editing
	fields are cleaned and the contents of the table, refresed from backend.
	"""
	def __init__(self, parent, id, pk_health_issue):
		"""
		Instantiate a new episode editor widget.
		
		@param pk_health_issue Id of the health issue to create/edit the episodes for
		@type pk_health_issue integer
		"""
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
		self.__pat = gmPerson.gmCurrentPatient()
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

		# - episode editor
		self.__STT_description = wx.wxStaticText(self, -1, _('Description'))
		# FIXME: configure, attach matcher (Karsten)
		self.__PRW_description = gmPhraseWheel.cPhraseWheel(self, -1)
		szr_input = wx.wxFlexGridSizer(cols = 2, rows = 2, vgap = 4, hgap = 4)
		szr_input.AddGrowableCol(1)
		szr_input.Add(self.__STT_description, 0, wx.wxSHAPED | wx.wxALIGN_CENTER)
		# FIXME: avoid phrasewheel to grow vertically
		szr_input.Add(self.__PRW_description, 1, wx.wxEXPAND)

		# - buttons		
		self.__BTN_add = wx.wxButton(self, -1, _('Add episode'))
		self.__BTN_clear = wx.wxButton(self, -1, _('Clear'))		
		szr_actions = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_actions.Add(self.__BTN_add, 0, wx.wxSHAPED)
		szr_actions.Add(self.__BTN_clear, 0, wx.wxSHAPED | wx.wxALIGN_RIGHT)

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
		self.__BTN_close = wx.wxButton(self, -1, _('Close'))
		szr_list = wx.wxStaticBoxSizer (
			wx.wxStaticBox(self, -1, _('Episode list')),
			wx.wxVERTICAL
		)
		szr_list.Add(self.__LST_episodes, 1, wx.wxEXPAND | wx.wxTOP, border=4)
		szr_list.Add(self.__BTN_close, 0, wx.wxSHAPED | wx.wxALIGN_CENTER)
		
		# arrange widgets
#		# FIXME: can we not simply merge szr_editor and szr_main ?
#		szr_editor = wx.wxStaticBoxSizer (
#			wx.wxStaticBox(self, -1, _('Episode editor')),
#			wx.wxVERTICAL
#		)
#		szr_editor.Add(szr_input, 1, wx.wxEXPAND | wx.wxALIGN_LEFT | wx.wxTOP, border=4)
#		szr_editor.Add(szr_actions, 1, wx.wxALIGN_CENTER | wx.wxTOP, border = 10)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(szr_input, 1, wx.wxEXPAND | wx.wxALIGN_LEFT | wx.wxTOP, border=4)
		szr_main.Add(szr_actions, 1, wx.wxALIGN_CENTER | wx.wxTOP, border = 10)
		szr_main.Add(szr_list, 2, wx.wxEXPAND)
		
#		szr_main.Add(szr_editor, 1, wx.wxEXPAND | wx.wxTOP, border=4)

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	def __refresh_episode_list(self):
		"""Update the table of episodes.
		"""
		self.__selected_episode = None
		self.__LST_episodes.DeleteAllItems()

		# populate table and cache episode list
		episodes = self.__pat.get_clinical_record().get_episodes()
		self.__episodes = {}
		for idx in range(len(episodes)):
			epi = episodes[idx]
			# FIXME: this is NOT the proper date to show !
			self.__LST_episodes.InsertStringItem(idx,  str(epi['episode_modified_when']))
#			self.__LST_episodes.SetStringItem(idx, 0, str(epi['episode_modified_when']))
			self.__LST_episodes.SetStringItem(idx, 1, epi['description'])
			self.__LST_episodes.SetStringItem(idx, 2, str(epi['episode_open']))
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
		wx.EVT_BUTTON(self.__BTN_close, self.__BTN_close.GetId(), self.__on_close)
		
	#--------------------------------------------------------
	def __on_close(self, event):
		"""
		Close episode editor, making the dialog returning CANCELLED
		Set selected episode to None and close the dialog returning CANCELLED
		"""
		self.__selected_episode = None
		self.GetParent().EndModal(dialog_CANCELLED)
		event.Skip()
				
	#--------------------------------------------------------
	def __on_episode_activated(self, event):
		"""
		When the user activates an episode on the table (by double clicking or
		pressing enter).
		The episode is selected. Editor fields are set with its values. Action
		buttons display update/cancel options.
		"""
		sel_idx = self.__LST_episodes.GetItemData(event.m_itemIndex)
		self.__selected_episode = self.__episodes[sel_idx]
		print 'Selected episode: ', self.__selected_episode
		self.__PRW_description.SetValue(self.__selected_episode['description'])
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
		if not self.__selected_episode is None:
			# on episode edition
			self.__BTN_add.SetLabel(_('Add episode'))
			self.__BTN_clear.SetLabel(_('Clear'))
			self.__selected_episode = None
		event.Skip()

	#--------------------------------------------------------
	def __on_add(self, event):
		"""
		On new episode: add episode to backend, clear input fields, refresh list
		On episode edition: update episode in backend, clear input fields,
		restore buttons for a new episode, refresh list
		"""
		description = self.__PRW_description.GetValue()

		# sanity check
		if self.__selected_episode is None:
			action = 'create'
		else:
			action = 'update'
		if (description is None or description.strip() == ''):
			msg = _('Cannot %s episode.\nAll required fields must be filled.') % action
			gmGuiHelpers.gm_show_error(msg, _('episode editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid description:soap cat [%s]' % description)
			return False

		if self.__selected_episode is None:
			# on new episode
			#self.__pat.get_clinical_record().add_episode(episode_name= , pk_health_issue=self.__pk_health_issue)
			print 'Creating episode: %s' % self.__PRW_description.GetValue()
			# FIXME 
			self.__selected_episode = self.__pat.get_clinical_record().add_episode (
				episode_name = self.__PRW_description.GetValue(),
				pk_health_issue = self.__pk_health_issue
			)			
		else:
			# on episode edition
			#self.__selected_episode['description'] = self.__PRW_description.GetValue()
			#self.__selected_episode.save_payload()
			print 'Renaming episode: %s' % self.__selected_episode

		# do clear stuff
		self.__on_clear(event)
		# refresh episode table
		self.__refresh_episode_list()
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting EMR struct editor...")
	
	ID_EPISODE_SELECTOR = wx.wxNewId()
	ID_EPISODE_EDITOR = wx.wxNewId()
	ID_EXIT = wx.wxNewId()
	
	#================================================================	
	class testapp (wx.wxApp):
			"""
			Test application for testing EMR struct widgets
			"""			
			#--------------------------------------------------------
			def OnInit (self):
				"""
				Create test application UI
				"""
				frame = wx.wxFrame(
							None,
							-4,
							'Testing EMR struct widgets',
							size=wx.wxSize(600, 400),
							style=wx.wxDEFAULT_FRAME_STYLE | wx.wxNO_FULL_REPAINT_ON_RESIZE
						)
				filemenu= wx.wxMenu()
				filemenu.Append(ID_EPISODE_SELECTOR, "&Test episode selector","Testing episode selector")
				filemenu.Append(ID_EPISODE_EDITOR, "&Test episode editor","Testing episode editor")				
				filemenu.AppendSeparator()
				filemenu.Append(ID_EXIT,"E&xit"," Terminate test application")
				# Creating the menubar.
	
				menuBar = wx.wxMenuBar()
				menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
	
				frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
	
				txt = wx.wxStaticText( frame, -1, _("Select desired test option from the 'File' menu"),
				wx.wxDefaultPosition, wx.wxDefaultSize, 0 )

				# event handlers
				wx.EVT_MENU(frame, ID_EPISODE_SELECTOR, self.OnEpisodeSelector)
				wx.EVT_MENU(frame, ID_EPISODE_EDITOR, self.OnEpisodeEditor)
				wx.EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)

				# patient EMR
				self.__pat = gmPerson.gmCurrentPatient()

				frame.Show(1)
				return 1					
				
			#--------------------------------------------------------			
			def OnEpisodeSelector(self,evt):
				"""
				Test episode selector dialog
				"""
				pk_issue = self.__pat.get_clinical_record().get_health_issues()[0]['id']
				episode_selector = cEpisodeSelectorDlg(
					None,
					-1,
					'Episode selector test',
					_('Add episode and start progress note'),
					pk_health_issue = pk_issue
				)
				retval = episode_selector.ShowModal() # Shows it
				
				if retval == dialog_OK:
					selected_episode = episode_selector.get_selected_episode()
					print 'Creating progress note for episode: %s' % selected_episode
				elif retval == dialog_CANCELLED:
					print 'User canceled'
				else:
					raise Exception('Invalid dialog return code [%s]' % retval)
				episode_selector.Destroy() # finally destroy it when finished.	
				
			#--------------------------------------------------------			
			def OnEpisodeEditor(self,evt):
				"""
				Test episode editor dialog
				"""
				pk_issue = self.__pat.get_clinical_record().get_health_issues()[0]['id']
				episode_selector = cEpisodeEditorDlg(None, -1,
				'Episode editor test', pk_health_issue = pk_issue)
				retval = episode_selector.ShowModal() # Shows it
				
				#if retval == dialog_OK:
					#selected_episode = episode_selector.get_selected_episode()
					#print 'Creating progress note for episode: %s' % selected_episode
				if retval == dialog_CANCELLED:
					print 'User closed episode editor'
				else:
					raise Exception('Invalid dialog return code [%s]' % retval)
				episode_selector.Destroy() # finally destroy it when finished.
				
			#--------------------------------------------------------
			def OnCloseWindow (self, e):
				"""
				Close test aplication
				"""
				self.ExitMainLoop ()
				
	#================================================================
	import sys
	from Gnumed.pycommon import gmCfg, gmPG

	_cfg = gmCfg.gmDefCfgFile	 
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# make sure we have a db connection
		gmPG.set_default_client_encoding('latin1')
		pool = gmPG.ConnectionPool()

		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# lauch emr dialogs test application
		app = testapp(0)
		app.MainLoop()
				
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
# Revision 1.4  2005-04-20 22:09:54  ncq
# - add edit area and popup dialog for health issue
#
# Revision 1.3  2005/03/14 14:36:31  ncq
# - use simplified episode naming
#
# Revision 1.2  2005/01/31 18:51:08  ncq
# - caching emr = patient.get_clinical_record() locally is unsafe
#   because patient can change but emr will stay the same (it's a
#   local "pointer", after all, and not a singleton)
# - adding episodes actually works now
#
# Revision 1.1  2005/01/31 13:09:21  ncq
# - this is OK to go in
#
# Revision 1.9  2005/01/31 13:06:02  ncq
# - use gmPerson.ask_for_patient()
#
# Revision 1.8  2005/01/31 09:50:59  ncq
# - gmPatient -> gmPerson
#
# Revision 1.7  2005/01/29 19:12:19  cfmoro
# Episode creation on episode editor widget
#
# Revision 1.6  2005/01/29 18:01:20  ncq
# - some cleanup
# - actually create new episodes
#
# Revision 1.5  2005/01/28 18:05:56  cfmoro
# Implemented episode picker and episode selector dialogs and widgets
#
# Revision 1.4  2005/01/24 16:57:38  ncq
# - some cleanup here and there
#
#
