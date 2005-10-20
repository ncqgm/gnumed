"""GnuMed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).
	
	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRStructWidgets.py,v $
# $Id: gmEMRStructWidgets.py,v 1.18 2005-10-20 07:42:27 ncq Exp $
__version__ = "$Revision: 1.18 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

# 3rd party
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

# GNUmed
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
class cHealthIssueEditArea(gmEditArea.cEditArea2):
	"""Edit Area for Health Issues.

	They correspond to "Past History" items.
	"""
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER, data_sink=None):
		gmEditArea.cEditArea2.__init__(self, parent, id, pos, size, style)
		# this edit area will ignore data_sink for now as
		# it seems reasonable to save back new health issues
		# immediately
	#----------------------------------------------------
	# public API
	#----------------------------------------------------
	def reset_ui(self):
		self.fld_condition.SetValue('')
		self.fld_age_onset.SetValue('')
		self.fld_year_onset.SetValue('')
		self.fld_progress_note.SetValue('')
		self.fld_condition.SetFocus()
	#----------------------------------------------------
	def save_data(self):
		# no pre-existing issue to deal with
		if self.data is None:
			return self.__save_new_entry()
		else:
			print self.__class__.__name__, "updating entry not implemented yet"
	#----------------------------------------------------
	def get_summary(self):
		tmp = _('pHx: %s (noticed at age %s in %s)') % (
			self.fld_condition.GetValue(),
			self.fld_age_onset.GetValue(),
			self.fld_year_onset.GetValue()
		)
		return tmp
	#----------------------------------------------------
	# intra-class API
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _('Condition'))
		self._add_prompt(line = 2, label = _('Noticed'))
		self._add_prompt(line = 3, label = _('Progress Note'))
	#----------------------------------------------------
	def _define_fields(self, parent):
		# condition
		cmd = """
			select distinct on (description) id, description
			from clin_health_issue where description %(fragment_condition)s"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', [cmd])
		mp.setThresholds(aWord=2, aSubstring=5)
		self.fld_condition = gmPhraseWheel.cPhraseWheel (
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.SIMPLE_BORDER
		)
		gmEditArea._decorate_editarea_field(self.fld_condition)
		self._add_field (
			line = 1,
			pos = 1,
			widget = self.fld_condition,
			weight = 3
		)
		self.fld_condition.SetFocus()
		# Onset
		label = wx.StaticText (
			parent = parent,
			id = -1,
			label = '%s: ' % _('Age'),
			style = wx.ALIGN_CENTRE
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
		label = wx.StaticText (
			parent = parent,
			id = -1,
			label = '%s: ' % _('Year'),
			style = wx.ALIGN_CENTRE
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
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', [cmd])
		mp.setThresholds(2, 4, 6)
		self.fld_progress_note = gmPhraseWheel.cPhraseWheel (
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.SIMPLE_BORDER | wx.TE_MULTILINE
		)
		gmEditArea._decorate_editarea_field(self.fld_progress_note)
		self._add_field (
			line = 3,
			pos = 1,
			widget = self.fld_progress_note,
			weight = 1
		)
		return 1
	#----------------------------------------------------
	# internal helpers
	#----------------------------------------------------
	def __save_new_entry(self):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_clinical_record()
		# create issue
		condition = self.fld_condition.GetValue()
		new_issue = emr.add_health_issue(issue_name = condition)

		#FIXME: use this for non-collapsing update of EMRBrowser
		self._health_issue = new_issue

		if new_issue is False:
			self._short_error = _('Health issue [%s] already exists. Cannot add duplicate.') % condition
			# FIXME: ask whether should update existing issue
			return False
		if new_issue is None:
			self._short_error = _('Error adding health issue [%s]') % condition
			return False
		# age onset
		age_onset = self.fld_age_onset.GetValue()
		# FIXME: plausibility checks until proper gmDateTimeInput used
		if age_onset != '':
			new_issue['age_noted'] = age_onset
			# FIXME: error handling
			new_issue.save_payload()
			
		# FIXME: handle fld_year_onset

		# progress note
		narr = self.fld_progress_note.GetValue().strip()
		if narr != '':
			epi = emr.add_episode(episode_name = _('past medical history'), pk_health_issue = new_issue['id'])
			epi['episode_open'] = False
			epi.save_payload()
			# FIXME: error handling
			if epi is not None:
				# FIXME: error handling
				emr.add_clin_narrative(note = narr, episode=epi)
		return True
#============================================================
class cEpisodeSelectorDlg(wx.Dialog):
	"""
	Pop up a episode picker dialog. Returns dialog_OK if an episode was
	selected, dialog_CANCELLED else.
	With get_selected_episode() the selected episode can be requested.
	"""
	def __init__(
					self,
					parent,
					id,
					caption = _('Episode selector'),					
					msg = '',
					action_txt = _('UNDEFINED action'),					
					pk_health_issue = None,
				 	pos = wx.DefaultPosition,
				 	size = wx.DefaultSize,
				 	style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
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
		wx.Dialog.__init__(self, parent, id, caption, pos, size, style)
		self.__episode_picker = cEpisodePicker(self, -1, msg, action_txt, pk_health_issue)
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
class cEpisodePicker(wx.Panel):
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
	def __init__(self, parent, id, msg, action_txt, pk_health_issue):
		"""
		Instantiate a new episode selector widget.
		
		@param action_txt Bottom action button display text
		@type action_txt string	
		 
		@param pk_health_issue Id of the health issue to select the episode for
		@type pk_health_issue integer		
		"""
		# parent class initialization
		wx.Panel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.NO_BORDER
		)

		# edited episodes' issue's PK
		self.__pk_health_issue = pk_health_issue
		self.__pat = gmPerson.gmCurrentPatient()
		# patient episodes
		self.__episodes = None
		# selected episode
		self.__selected_episode = None
		
		# ui contruction and event handling set up
		self.__do_layout(msg, action_txt)
		self.__register_interests()
		
		self.__refresh_episode_list()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self, msg, action_txt):
		"""
		Arrange widgets.

		@param action_txt Bottom action button display text
		@type action_txt string			
		"""
		# instantiate and initialize widgets
	
		# status info
		self.__STT_status = wx.StaticText(self, -1, msg)
		
		# - episode editor
		self.__STT_description = wx.StaticText(self, -1, _('Description'))
		
		# FIXME: configure, attach matcher (Karsten)
		self.__PRW_description = gmPhraseWheel.cPhraseWheel(self, -1)

		# - buttons
		action_msg = _('Create a new episode and %s') % action_txt
		self.__BTN_add = wx.Button(self, -1, action_msg)
		self.__BTN_cancel = wx.Button(self, -1, _('Cancel'))

		# layout input
		szr_actions = wx.BoxSizer(wx.HORIZONTAL)
		szr_actions.Add(self.__BTN_add, 0, wx.SHAPED)
		szr_actions.Add(self.__BTN_cancel, 0, wx.SHAPED | wx.ALIGN_RIGHT)
		
		szr_input = wx.FlexGridSizer(cols = 2, rows = 2, vgap = 4, hgap = 4)
		szr_input.AddGrowableCol(1)		
		szr_input.Add(self.__STT_description, 0, wx.SHAPED)
		szr_input.Add(self.__PRW_description, 1, wx.EXPAND)
#		szr_input.AddSpacer(0,0)
		szr_input.Add(szr_actions, 0, wx.ALIGN_CENTER | wx.TOP, border = 4)
		# - episodes list and new note for selected episode button
		self.__LST_episodes = wx.ListCtrl(
			self,
			-1,
			style = wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
		)
		self.__LST_episodes.InsertColumn(0, _('Last renamed'))
		self.__LST_episodes.InsertColumn(1, _('Description'), wx.LIST_FORMAT_RIGHT)
		self.__LST_episodes.InsertColumn(2, _('Is open'))
		# FIXME: dynamic calculation
		self.__LST_episodes.SetColumnWidth(0, 100)
		self.__LST_episodes.SetColumnWidth(1, 230)
		self.__LST_episodes.SetColumnWidth(2, 70)
		action_msg = _('Select and episode and %s') % action_txt
		self.__BTN_action = wx.Button(self, -1, action_msg)
		szr_list = wx.StaticBoxSizer (
			wx.StaticBox(self, -1, _('Episode list')),
			wx.VERTICAL
		)
		szr_list.Add(self.__LST_episodes, 1, wx.EXPAND | wx.TOP, border=4)
		szr_list.Add(self.__BTN_action, 0, wx.SHAPED | wx.ALIGN_CENTER, border=4)
		szr_list.SetItemMinSize(self.__LST_episodes, 1, 100)
		
		# layout sizers
		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__STT_status, 0, flag=wx.SHAPED | wx.ALIGN_LEFT | wx.TOP, border=4)
		szr_main.Add(szr_input, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.TOP, border=4)
		szr_main.Add(szr_list, 2, wx.EXPAND)		

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
		

	        issues = emr.get_health_issues()
	        issue_map = {}
		for issue in issues:
			issue_map[issue['id']] = issue['description']

		
		episodes = emr.get_episodes()
		self.__episodes = {}

		for idx in range(len(episodes)):
			epi = episodes[idx]
			# FIXME: this is NOT the proper date to show !
			self.__LST_episodes.InsertStringItem(idx,  str(epi['episode_modified_when']))
			self.__LST_episodes.SetStringItem(idx, 1, issue_map.get(epi['pk_health_issue'],'')+ ':' + epi['description'])
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
class cEpisodeEditorDlg(wx.Dialog):
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
				 	pos = wx.DefaultPosition,
				 	size = wx.DefaultSize,
				 	style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
				 ):
		"""
		Instantiate a new episode editor dialog.
		
		@param title Selector dialog descritive title
		@type title string
			 
		@param pk_health_issue Id of the health issue to select the episode for
		@type pk_health_issue integer
		"""
		# build ui
		wx.Dialog.__init__(self, parent, id, title, pos, size, style)
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
class cEpisodeEditor(wx.Panel):
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
		wx.Panel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.NO_BORDER
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
		self.__STT_description = wx.StaticText(self, -1, _('Description'))
		# FIXME: configure, attach matcher (Karsten)
		self.__PRW_description = gmPhraseWheel.cPhraseWheel(self, -1)
		szr_input = wx.FlexGridSizer(cols = 2, rows = 2, vgap = 4, hgap = 4)
		szr_input.AddGrowableCol(1)
		szr_input.Add(self.__STT_description, 0, wx.SHAPED | wx.ALIGN_CENTER)
		# FIXME: avoid phrasewheel to grow vertically
		szr_input.Add(self.__PRW_description, 1, wx.EXPAND)

		# - buttons		
		self.__BTN_add = wx.Button(self, -1, _('Add episode'))
		self.__BTN_clear = wx.Button(self, -1, _('Clear'))		
		szr_actions = wx.BoxSizer(wx.HORIZONTAL)
		szr_actions.Add(self.__BTN_add, 0, wx.SHAPED)
		szr_actions.Add(self.__BTN_clear, 0, wx.SHAPED | wx.ALIGN_RIGHT)

		# instantiate and initialize widgets
		# - episodes list
		self.__LST_episodes = wx.ListCtrl(
			self,
			-1,
			style = wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
		)
		self.__LST_episodes.InsertColumn(0, _('Start date'))
		self.__LST_episodes.InsertColumn(1, _('Description'), wx.LIST_FORMAT_RIGHT)
#		self.__LST_episodes.InsertColumn(2, _('Category'))
		self.__LST_episodes.InsertColumn(2, _('Is open'))
#		self.__LST_episodes.InsertColumn(3, _('Is open'))
		self.__LST_episodes.SetColumnWidth(0, 100)
		self.__LST_episodes.SetColumnWidth(1, 230)
		self.__LST_episodes.SetColumnWidth(2, 70)
#		self.__LST_episodes.SetColumnWidth(3, 70)
		self.__BTN_close = wx.Button(self, -1, _('Close'))
		szr_list = wx.StaticBoxSizer (
			wx.StaticBox(self, -1, _('Episode list')),
			wx.VERTICAL
		)
		szr_list.Add(self.__LST_episodes, 1, wx.EXPAND | wx.TOP, border=4)
		szr_list.Add(self.__BTN_close, 0, wx.SHAPED | wx.ALIGN_CENTER)
		
		# arrange widgets
#		# FIXME: can we not simply merge szr_editor and szr_main ?
#		szr_editor = wx.StaticBoxSizer (
#			wx.StaticBox(self, -1, _('Episode editor')),
#			wx.VERTICAL
#		)
#		szr_editor.Add(szr_input, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.TOP, border=4)
#		szr_editor.Add(szr_actions, 1, wx.ALIGN_CENTER | wx.TOP, border = 10)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(szr_input, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.TOP, border=4)
		szr_main.Add(szr_actions, 1, wx.ALIGN_CENTER | wx.TOP, border = 10)
		szr_main.Add(szr_list, 2, wx.EXPAND)
		
#		szr_main.Add(szr_editor, 1, wx.EXPAND | wx.TOP, border=4)

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
	
	ID_EPISODE_SELECTOR = wx.NewId()
	ID_EPISODE_EDITOR = wx.NewId()
	ID_EXIT = wx.NewId()
	
	#================================================================	
	class testapp (wx.App):
			"""
			Test application for testing EMR struct widgets
			"""			
			#--------------------------------------------------------
			def OnInit (self):
				"""
				Create test application UI
				"""
				frame = wx.Frame(
							None,
							-4,
							'Testing EMR struct widgets',
							size=wx.Size(600, 400),
							style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
						)
				filemenu= wx.Menu()
				filemenu.Append(ID_EPISODE_SELECTOR, "&Test episode selector","Testing episode selector")
				filemenu.Append(ID_EPISODE_EDITOR, "&Test episode editor","Testing episode editor")				
				filemenu.AppendSeparator()
				filemenu.Append(ID_EXIT,"E&xit"," Terminate test application")
				# Creating the menubar.
	
				menuBar = wx.MenuBar()
				menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
	
				frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
	
				txt = wx.StaticText( frame, -1, _("Select desired test option from the 'File' menu"),
				wx.DefaultPosition, wx.DefaultSize, 0 )

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
					'Info about current status of things',
					_('start progress note'),
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
# Revision 1.18  2005-10-20 07:42:27  ncq
# - somewhat improved edit area for issue
#
# Revision 1.17  2005/10/08 12:33:09  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.16  2005/10/04 19:24:53  sjtan
# browser now remembers expansion state and select state between change of patients, between health issue rename, episode rename or encounter relinking. This helps when reviewing the record more than once in a day.
#
# Revision 1.15  2005/09/27 20:44:58  ncq
# - wx.wx* -> wx.*
#
# Revision 1.14  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.13  2005/09/24 09:17:28  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.12  2005/08/06 16:50:51  ncq
# - zero-size spacer seems pointless and besides it
#   don't work like that in wx2.5
#
# Revision 1.11  2005/06/29 15:06:38  ncq
# - defaults for edit area popup/editarea2 __init__
#
# Revision 1.10  2005/06/28 17:14:56  cfmoro
# Auto size flag causes the text not being displayed
#
# Revision 1.9  2005/06/20 13:03:38  cfmoro
# Relink encounter to another episode
#
# Revision 1.8  2005/06/10 23:22:43  ncq
# - SQL2 match provider now requires query *list*
#
# Revision 1.7  2005/05/06 15:30:15  ncq
# - attempt to properly set focus
#
# Revision 1.6  2005/04/25 08:30:59  ncq
# - make past medical history proxy episodes closed by default
#
# Revision 1.5  2005/04/24 14:45:18  ncq
# - cleanup, use generic edit area popup dialog
# - "finalize" (as for 0.1) health issue edit area
#
# Revision 1.4  2005/04/20 22:09:54  ncq
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
