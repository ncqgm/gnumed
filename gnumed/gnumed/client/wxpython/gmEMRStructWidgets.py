"""GNUmed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).
	
	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRStructWidgets.py,v $
# $Id: gmEMRStructWidgets.py,v 1.75 2008-05-07 15:21:10 ncq Exp $
__version__ = "$Revision: 1.75 $"
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL"

# stdlib
import sys, re, datetime as pydt, logging


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmMatchProvider, gmDispatcher, gmTools, gmDateTime, gmCfg
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter, gmSurgery
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmListWidgets
from Gnumed.wxGladeWidgets import wxgIssueSelectionDlg, wxgMoveNarrativeDlg
from Gnumed.wxGladeWidgets import wxgHealthIssueEditAreaPnl, wxgHealthIssueEditAreaDlg
from Gnumed.wxGladeWidgets import wxgEncounterEditAreaPnl, wxgEncounterEditAreaDlg
from Gnumed.wxGladeWidgets import wxgEpisodeEditAreaPnl, wxgEpisodeEditAreaDlg


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#================================================================
# encounter related widgets/functions
#----------------------------------------------------------------
def ask_for_encounter_continuation(msg=None, caption=None):
	dlg = gmGuiHelpers.c2ButtonQuestionDlg (
		parent = None,
		id = -1,
		caption = caption,
		question = msg,
		button_defs = [
			{'label': _('Continue'), 'tooltip': _('Continue the existing recent encounter.'), 'default': False},
			{'label': _('Start new'), 'tooltip': _('Start a new encounter. The existing one will be closed.'), 'default': True}
		],
		show_checkbox = False
	)
	result = dlg.ShowModal()
	if result == wx.ID_YES:
		return True
	return False
#----------------------------------------------------------------
class cEncounterTypePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of encounter type.

	- user input interpreted as encounter type in English or local language
	- data returned is pk of corresponding encounter type or None
	"""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select pk, l10n_description from (
	select distinct on (pk) * from (
		(select
			pk,
			_(description) as l10n_description,
			1 as rank
		from
			clin.encounter_type
		where
			_(description) %(fragment_condition)s

		) union all (

		select
			pk,
			_(description) as l10n_description,
			2 as rank
		from
			clin.encounter_type
		where
			description %(fragment_condition)s
		)
	) as q_distinct_pk
) as q_ordered order by rank, l10n_description
"""			]
		)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.selection_only = True
		self.picklist_delay = 50
#----------------------------------------------------------------
class cEncounterEditAreaPnl(wxgEncounterEditAreaPnl.wxgEncounterEditAreaPnl):

	def __init__(self, *args, **kwargs):
		try:
			self.__encounter = kwargs['encounter']
			del kwargs['encounter']
		except KeyError:
			self.__encounter = None

		wxgEncounterEditAreaPnl.wxgEncounterEditAreaPnl.__init__(self, *args, **kwargs)

		self.__init_ui()
		if self.__encounter is not None:
			self.refresh()
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_problems.InsertColumn(0, _('Episode'))
#		self._LCTRL_problems.InsertColumn(1, _('Foundational Issue'))
#		self._LCTRL_problems.InsertColumn(2, _('Assessment'))
		self._LCTRL_problems.InsertColumn(3, _('Narrative'))
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, encounter = None):

		if encounter is not None:
			self.__encounter = encounter

		# getting the patient via the encounter allows us to act
		# on any encounter regardless of the currently active patient
		pat = gmPerson.cPatient(aPK_obj = self.__encounter['pk_patient'])
		emr = pat.get_emr()
		episodes = emr.get_episodes_by_encounter(pk_encounter = self.__encounter['pk_encounter'])
		pos = len(episodes) + 1

		self._LCTRL_problems.DeleteAllItems()
		for episode in episodes:
			row_num = self._LCTRL_problems.InsertStringItem(pos, label = episode['description'])
#			self._LCTRL_problems.SetStringItem(index = row_num, col = 1, label = gmTools.coalesce(episode['health_issue'], ''))
		if len(episodes) > 0:
			self._LCTRL_problems.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
#			self._LCTRL_problems.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)		# wx.LIST_AUTOSIZE_USEHEADER

		self._PRW_encounter_type.SetText(self.__encounter['l10n_type'], data=self.__encounter['pk_type'])

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['started'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_start.SetText(fts.format_accurately(), data=fts)

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['last_affirmed'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_end.SetText(fts.format_accurately(), data=fts)

		self._TCTRL_rfe.SetValue(gmTools.coalesce(self.__encounter['reason_for_encounter'], ''))
		self._TCTRL_aoe.SetValue(gmTools.coalesce(self.__encounter['assessment_of_encounter'], ''))

		if self.__encounter['last_affirmed'] == self.__encounter['started']:
			self._PRW_end.SetFocus()
		else:
			self._TCTRL_aoe.SetFocus()

		self._TCTRL_patient.SetLabel(pat.get_description())

		return True
	#--------------------------------------------------------
	def __is_valid_for_save(self):

		if self._PRW_encounter_type.GetData is None:
			self._PRW_encounter_type.SetBackgroundColour('pink')
			self._PRW_encounter_type.Refresh()
			self._PRW_encounter_type.SetFocus()
			return False
		self._PRW_encounter_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_encounter_type.Refresh()

		if not self._PRW_start.is_valid_timestamp():
			self._PRW_start.SetFocus()
			return False

		if not self._PRW_end.is_valid_timestamp():
			self._PRW_end.SetFocus()
			return False

		return True
	#--------------------------------------------------------
	def save(self):
		if not self.__is_valid_for_save():
			return False

		self.__encounter['pk_type'] = self._PRW_encounter_type.GetData()
		self.__encounter['started'] = self._PRW_start.GetData().get_pydt()
		self.__encounter['last_affirmed'] = self._PRW_end.GetData().get_pydt()
		rfe = self._TCTRL_rfe.GetValue().strip()
		if len(rfe) != 0:
			self.__encounter['reason_for_encounter'] = rfe
		aoe = self._TCTRL_aoe.GetValue().strip()
		if len(aoe) != 0:
			self.__encounter['assessment_of_encounter'] = aoe

		self.__encounter.save_payload()			# FIXME: error checking

		return True
#----------------------------------------------------------------
class cEncounterEditAreaDlg(wxgEncounterEditAreaDlg.wxgEncounterEditAreaDlg):

	def __init__(self, *args, **kwargs):
		encounter = kwargs['encounter']
		del kwargs['encounter']

		wxgEncounterEditAreaDlg.wxgEncounterEditAreaDlg.__init__(self, *args, **kwargs)

		self._PNL_edit_area.refresh(encounter=encounter)

		self.Fit()
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
#================================================================
# episode related widgets/functions
#----------------------------------------------------------------
def move_episode_to_issue(episode=None, target_issue=None, save_to_backend=False):
	"""Prepare changing health issue for an episode.

	Checks for two-open-episodes conflict. When this
	function succeeds, the pk_health_issue has been set
	on the episode instance and the episode should - for
	all practical purposes - be ready for save_payload().
	"""
	# episode is closed: should always work
	if not episode['episode_open']:
		episode['pk_health_issue'] = target_issue['pk']
		if save_to_backend:
			episode.save_payload()
		return True

	# un-associate: should always work, too
	if target_issue is None:
		episode['pk_health_issue'] = None
		if save_to_backend:
			episode.save_payload()
		return True

	# try closing possibly expired episode on target issue if any
	db_cfg = gmCfg.cCfgSQL()
	epi_ttl = int(db_cfg.get2 (
		option = u'episode.ttl',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'user',
		default = 60				# 2 months
	))
	if target_issue.close_expired_episode(ttl=epi_ttl) is True:
		gmDispatcher.send(signal='statustext', msg=_('Closed episodes older than %s days on health issue [%s]') % (epi_ttl, target_issue['description']))
	existing_epi = target_issue.get_open_episode()

	# no more open episode on target issue: should work now
	if existing_epi is None:
		episode['pk_health_issue'] = target_issue['pk']
		if save_to_backend:
			episode.save_payload()
		return True

	# don't conflict on SELF ;-)
	if existing_epi['pk_episode'] == episode['pk_episode']:
		episode['pk_health_issue'] = target_issue['pk']
		if save_to_backend:
			episode.save_payload()
		return True

	# we got two open episodes at once, ask user
	move_range = episode.get_access_range()
	exist_range = existing_epi.get_access_range()
	question = _(
		'You want to associate the running episode:\n\n'
		' "%(new_epi_name)s" (%(new_epi_start)s - %(new_epi_end)s)\n\n'
		'with the foundational health issue:\n\n'
		' "%(issue_name)s"\n\n'
		'There already is another episode running\n'
		'for this foundational isssue:\n\n'
		' "%(old_epi_name)s" (%(old_epi_start)s - %(old_epi_end)s)\n\n'
		'However, there can only be one running\n'
		'episode per foundational health issue.\n\n'
		'Which episode do you want to close ?'
	) % {
		'new_epi_name': episode['description'],
		'new_epi_start': move_range[0].strftime('%m/%y'),
		'new_epi_end': move_range[1].strftime('%m/%y'),
		'issue_name': target_issue['description'],
		'old_epi_name': existing_epi['description'],
		'old_epi_start': exist_range[0].strftime('%m/%y'),
		'old_epi_end': exist_range[1].strftime('%m/%y')
	}
	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent = None,
		id = -1,
		caption = _('Resolving two-running-episodes conflict'),
		question = question,
		button_defs = [
			{'label': _('old episode'), 'default': True, 'tooltip': _('close existing episode "%s"') % existing_epi['description']},
			{'label': _('new episode'), 'default': False, 'tooltip': _('close moving (new) episode "%s"') % episode['description']}
		]
	)
	decision = dlg.ShowModal()

	if decision == wx.ID_CANCEL:
		# button 3: move cancelled by user
		return False

	elif decision == wx.ID_YES:
		# button 1: close old episode
		existing_epi['episode_open'] = False
		existing_epi.save_payload()

	elif decision == wx.ID_NO:
		# button 2: close new episode
		episode['episode_open'] = False

	else:
		raise ValueError('invalid result from c3ButtonQuestionDlg: [%s]' % decision)

	episode['pk_health_issue'] = target_issue['pk']
	if save_to_backend:
		episode.save_payload()
	return True
#----------------------------------------------------------------
class cEpisodeListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	# FIXME: support pre-selection

	def __init__(self, *args, **kwargs):

		episodes = kwargs['episodes']
		del kwargs['episodes']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the episodes you are interested in ...'))
		self._LCTRL_items.set_columns([_('Episode'), _('Status'), _('Health Issue')])
		self._LCTRL_items.set_string_items (
			items = [ [epi['description'], gmTools.bool2str(epi['episode_open'], _('ongoing'), u''), gmTools.coalesce(epi['health_issue'], u'')] for epi in episodes ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = episodes)
#----------------------------------------------------------------
class cEpisodeDescriptionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select an episode *description*.

	The user can select an episode description from the previously
	used descriptions across all episodes across all patients.

	Selection is done with a phrasewheel so the user can
	type the episode name and matches will be shown. Typing
	"*" will show the entire list of episodes.

	If the user types a description not existing yet a
	new episode description will be returned.
	"""
	def __init__(self, *args, **kwargs):

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
				select distinct on (description) description, description, 1
				from clin.episode
				where description %(fragment_condition)s
				order by description
				limit 30"""
			]
		)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
#----------------------------------------------------------------
class cEpisodeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select an episode.

	The user can select an episode from the existing episodes of a
	patient. Selection is done with a phrasewheel so the user
	can type the episode name and matches will be shown. Typing
	"*" will show the entire list of episodes. Closed episodes
	will be marked as such. If the user types an episode name not
	in the list of existing episodes a new episode can be created
	from it if the programmer activated that feature.

	If keyword <patient_id> is set to None or left out the control
	will listen to patient change signals and therefore act on
	gmPerson.gmCurrentPatient() changes.
	"""
	def __init__(self, *args, **kwargs):

		ctxt = {'ctxt_pat': {'where_part': u'pk_patient=%(pat)s', 'placeholder': u'pat'}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select * from (
	(select
		pk_episode,
		case when health_issue is Null
			then description
			else description || ' - ' || health_issue
		end as description,
		1 as weight
	 from
	  	clin.v_pat_episodes
	 where
		episode_open is true and
		description %(fragment_condition)s and
		%(ctxt_pat)s
	) union all (
	 select
		pk_episode,
		case when health_issue is Null
			then description || _(' (closed)')
			else description || _(' (closed)') || ' - ' || health_issue
		end as description,
		1 as weight
	 from
		clin.v_pat_episodes
	 where
		description %(fragment_condition)s and
		episode_open is false and
		%(ctxt_pat)s
	)) as union_result
order by weight, description
limit 30"""
],
			context = ctxt
		)

		try:
			kwargs['patient_id']
		except KeyError:
			kwargs['patient_id'] = None

		if kwargs['patient_id'] is None:
			self.use_current_patient = True
			self.__register_patient_change_signals()
			pat = gmPerson.gmCurrentPatient()
			if pat.is_connected():
				mp.set_context('pat', pat.ID)
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_patient(self, patient_id=None):
		if self.use_current_patient:
			return False
		self.__patient_id = int(patient_id)
		self.set_context('pat', self.__patient_id)
		return True
	#--------------------------------------------------------
	def GetData(self, can_create=False, is_open=False):
		if self.data is None:
			if can_create:
				epi_name = self.GetValue().strip()

				if self.use_current_patient:
					pat = gmPerson.gmCurrentPatient()
				else:
					pat = gmPerson.cPatient(aPK_obj=self.__patient_id)
				emr = pat.get_emr()

				epi = emr.add_episode(episode_name=epi_name, is_open=is_open)
				if epi is None:
					self.data = None
				else:
					self.data = epi['pk_episode']

		return gmPhraseWheel.cPhraseWheel.GetData(self)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __register_patient_change_signals(self):
		gmDispatcher.connect(self._pre_patient_selection, u'pre_patient_selection')
		gmDispatcher.connect(self._post_patient_selection, u'post_patient_selection')
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.ID)
		return True
#----------------------------------------------------------------
class cEpisodeEditAreaPnl(wxgEpisodeEditAreaPnl.wxgEpisodeEditAreaPnl):

	def __init__(self, *args, **kwargs):
		try:
			self.__episode = kwargs['episode']
			del kwargs['episode']
		except KeyError:
			self.__episode = None

		wxgEpisodeEditAreaPnl.wxgEpisodeEditAreaPnl.__init__(self, *args, **kwargs)

		self.refresh()
	#------------------------------------------------------------
	def refresh(self, episode=None):
		if episode is not None:
			self.__episode = episode

		if self.__episode is None:
			return

		ident = gmPerson.cIdentity(aPK_obj = self.__episode['pk_patient'])
		self._TCTRL_patient.SetValue(ident.get_description())

		if self.__episode['pk_health_issue'] is not None:
			self._PRW_issue.SetText(self.__episode['health_issue'], data=self.__episode['pk_health_issue'])

		self._PRW_description.SetText(self.__episode['description'], data=self.__episode['description'])

		self._CHBOX_closed.SetValue(not self.__episode['episode_open'])
	#------------------------------------------------------------
	def save(self):
		self.__episode['episode_open'] = not self._CHBOX_closed.IsChecked()

		issue_name = self._PRW_issue.GetValue().strip()
		if len(issue_name) == 0:
			self.__episode['pk_health_issue'] = None
		else:
			self.__episode['pk_health_issue'] = self._PRW_issue.GetData(can_create=True)
			issue = gmEMRStructItems.cHealthIssue(aPK_obj=self.__episode['pk_health_issue'])
			if not move_episode_to_issue(episode = self.__episode, target_issue = issue, save_to_backend = False):
				gmDispatcher.send(signal='statustext', msg=
						_('Cannot attach episode [%s] to health issue [%s] because it already has a running episode.') % (
						self.__episode['description'],
						issue['description']
					)
				)
				return False

		desc = self._PRW_description.GetValue().strip()
		if len(desc) != 0:
			self.__episode['description'] = desc

		self.__episode.save_payload()
		return True
#----------------------------------------------------------------
class cEpisodeEditAreaDlg(wxgEpisodeEditAreaDlg.wxgEpisodeEditAreaDlg):

	def __init__(self, *args, **kwargs):
		try:
			episode = kwargs['episode']
			del kwargs['episode']
		except KeyError:
			episode = None

		wxgEpisodeEditAreaDlg.wxgEpisodeEditAreaDlg.__init__(self, *args, **kwargs)

		self._PNL_edit_area.refresh(episode=episode)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PNL_edit_area.refresh()
#================================================================
# foundational issue related widgets/functions
#----------------------------------------------------------------
class cIssueListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	# FIXME: support pre-selection

	def __init__(self, *args, **kwargs):

		issues = kwargs['issues']
		del kwargs['issues']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the health issues you are interested in ...'))
		self._LCTRL_items.set_columns([u'', _('Health Issue'), u'', u'', u''])

		for issue in issues:
			if issue['is_confidential']:
				row_num = self._LCTRL_items.InsertStringItem(sys.maxint, label = _('confidential'))
				self._LCTRL_items.SetItemTextColour(row_num, col=wx.NamedColour('RED'))
			else:
				row_num = self._LCTRL_items.InsertStringItem(sys.maxint, label = u'')

			self._LCTRL_items.SetStringItem(index = row_num, col = 1, label = issue['description'])
			if issue['clinically_relevant']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 2, label = _('relevant'))
			if issue['is_active']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 3, label = _('active'))
			if issue['is_cause_of_death']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 4, label = _('fatal'))

		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = issues)
#----------------------------------------------------------------
class cIssueSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let the user select a health issue.

	The user can select a health issue from the existing issues
	of a patient. Selection is done with a phrasewheel so the user
	can type the issue name and matches will be shown. Typing
	"*" will show the entire list of issues. Inactive issues
	will be marked as such. If the user types an issue name not
	in the list of existing issues a new issue can be created
	from it if the programmer activated that feature.

	If keyword <patient_id> is set to None or left out the control
	will listen to patient change signals and therefore act on
	gmPerson.gmCurrentPatient() changes.
	"""
	def __init__(self, *args, **kwargs):

		ctxt = {'ctxt_pat': {'where_part': u'fk_patient=%(pat)s', 'placeholder': u'pat'}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			# FIXME: consider clin.health_issue.clinically_relevant
			queries = [u"""
(select pk, description, 1
	from clin.health_issue where
		is_active is true and
		description %(fragment_condition)s and
		%(ctxt_pat)s
	order by description)

union

(select pk, description || _(' (inactive)'), 2
	from clin.health_issue where
		is_active is false and
		description %(fragment_condition)s and
		%(ctxt_pat)s
	order by description)"""
			],
			context = ctxt
		)

		try: kwargs['patient_id']
		except KeyError: kwargs['patient_id'] = None

		if kwargs['patient_id'] is None:
			self.use_current_patient = True
			self.__register_patient_change_signals()
			pat = gmPerson.gmCurrentPatient()
			if pat.is_connected():
				mp.set_context('pat', pat.ID)
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_patient(self, patient_id=None):
		if self.use_current_patient:
			return False
		self.__patient_id = int(patient_id)
		self.set_context('pat', self.__patient_id)
		return True
	#--------------------------------------------------------
	def GetData(self, can_create=False, is_open=False):
		if self.data is None:
			if can_create:
				issue_name = self.GetValue().strip()

				if self.use_current_patient:
					pat = gmPerson.gmCurrentPatient()
				else:
					pat = gmPerson.cPatient(aPK_obj=self.__patient_id)
				emr = pat.get_emr()

				issue = emr.add_health_issue(issue_name = issue_name)
				if issue is None:
					self.data = None
				else:
					self.data = issue['pk']

		return gmPhraseWheel.cPhraseWheel.GetData(self)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __register_patient_change_signals(self):
		gmDispatcher.connect(self._pre_patient_selection, u'pre_patient_selection')
		gmDispatcher.connect(self._post_patient_selection, u'post_patient_selection')
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.ID)
		return True
#------------------------------------------------------------
class cIssueSelectionDlg(wxgIssueSelectionDlg.wxgIssueSelectionDlg):

	def __init__(self, *args, **kwargs):
		try:
			msg = kwargs['message']
		except KeyError:
			msg = None
		del kwargs['message']
		wxgIssueSelectionDlg.wxgIssueSelectionDlg.__init__(self, *args, **kwargs)
		if msg is not None:
			self._lbl_message.SetLabel(label=msg)
	#--------------------------------------------------------
	def _on_OK_button_pressed(self, event):
		event.Skip()
		pk_issue = self._PhWheel_issue.GetData(can_create=True)
		if pk_issue is None:
			gmGuiHelpers.gm_show_error (
				_('Cannot create new health issue:\n [%(issue)s]') % {'issue': self._PhWheel_issue.GetValue().strip()},
				_('Selecting health issue')
			)
			return False
		return True
#------------------------------------------------------------
class cHealthIssueEditAreaPnl(wxgHealthIssueEditAreaPnl.wxgHealthIssueEditAreaPnl):
	"""Panel encapsulating health issue edit area functionality."""

	def __init__(self, *args, **kwargs):
		wxgHealthIssueEditAreaPnl.wxgHealthIssueEditAreaPnl.__init__(self, *args, **kwargs)

		try:
			self.__issue = kwargs['issue']
		except KeyError:
			self.__issue = None

		# FIXME: include more sources: coding systems/other database columns
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"select distinct on (description) description, description from clin.health_issue where description %(fragment_condition)s limit 50"]
		)
		mp.setThresholds(1, 3, 5)
		self._PRW_condition.matcher = mp

		self._PRW_age_noted.add_callback_on_lose_focus(self._on_leave_age_noted)
		self._PRW_year_noted.add_callback_on_lose_focus(self._on_leave_year_noted)

		self._PRW_age_noted.add_callback_on_modified(self._on_modified_age_noted)
		self._PRW_year_noted.add_callback_on_modified(self._on_modified_year_noted)

		self.refresh()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _on_leave_age_noted(self, *args, **kwargs):

		if not self._PRW_age_noted.IsModified():
			return True

		str_age = self._PRW_age_noted.GetValue().strip()

		if str_age == u'':
			wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
			return True

		age = gmTools.str2interval(str_interval = str_age)
		pat = gmPerson.gmCurrentPatient()
		max_age = pydt.datetime.now(tz=pat['dob'].tzinfo) - pat['dob']

		if age is None:
			gmDispatcher.send(signal='statustext', msg=_('Cannot parse [%s] into valid interval.') % str_age)
		if age >= max_age:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _(
					'Foundational health issue cannot have been noted at age %s. Patient is only %s old.'
				) % (age, pat.get_medical_age())
			)

		if (age is None) or (age >= max_age):
			self._PRW_age_noted.SetBackgroundColour('pink')
			self._PRW_age_noted.Refresh()
			wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
			return True

		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_age_noted.Refresh()
		self._PRW_age_noted.SetData(data=age)

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = pat['dob'] + age,
			accuracy = gmDateTime.acc_months
		)
		wx.CallAfter(self._PRW_year_noted.SetText, str(fts), fts)
		# if we do this we will *always* navigate there, regardless of TAB vs ALT-TAB
		#wx.CallAfter(self._ChBOX_active.SetFocus)
		# if we do the following instead it will take us to the save/update button ...
		#wx.CallAfter(self.Navigate)

		return True
	#--------------------------------------------------------
	def _on_leave_year_noted(self, *args, **kwargs):

		if not self._PRW_year_noted.IsModified():
			return True

		year_noted = self._PRW_year_noted.GetData()

		if year_noted is None:
			if self._PRW_year_noted.GetValue().strip() == u'':
				wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
				return True
			self._PRW_year_noted.SetBackgroundColour('pink')
			self._PRW_year_noted.Refresh()
			wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
			return True

		year_noted = year_noted.get_pydt()

		if year_noted >= pydt.datetime.now(tz=year_noted.tzinfo):
			gmDispatcher.send(signal='statustext', msg=_('Condition diagnosed in the future.'))
			self._PRW_year_noted.SetBackgroundColour('pink')
			self._PRW_year_noted.Refresh()
			wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
			return True

		self._PRW_year_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_year_noted.Refresh()

		pat = gmPerson.gmCurrentPatient()
		age = year_noted - pat['dob']
		str_age = gmPerson.format_age_medically(age)
		wx.CallAfter(self._PRW_age_noted.SetText, str_age, age)

		return True
	#--------------------------------------------------------
	def _on_modified_age_noted(self, *args, **kwargs):
		wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
		return True
	#--------------------------------------------------------
	def _on_modified_year_noted(self, *args, **kwargs):
		wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
		return True
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def clear(self):
		self.__issue = None
		return self.refresh()
	#--------------------------------------------------------
	def refresh(self, issue=None):

		if issue is not None:
			self.__issue = issue

		self._PRW_condition.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_condition.Refresh()
		self._PRW_condition.SetFocus()
		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_age_noted.Refresh()

		if self.__issue is None:
			self._PRW_condition.SetText()
			self._ChBOX_left.SetValue(0)
			self._ChBOX_right.SetValue(0)
			self._TCTRL_notes.SetValue('')
			self._PRW_age_noted.SetText()
			self._PRW_year_noted.SetText()
			self._ChBOX_active.SetValue(0)
			self._ChBOX_relevant.SetValue(1)
			self._ChBOX_is_operation.SetValue(0)
			self._ChBOX_confidential.SetValue(0)
			self._ChBOX_caused_death.SetValue(0)
			return True

		if not isinstance(self.__issue, gmEMRStructItems.cHealthIssue):
			raise ValueError('[%s].refresh(): expected gmEMRStructItems.cHealthIssue instance, got [%s] instead' % (self.__class__.__name__, self.__issue))

		self._PRW_condition.SetText(self.__issue['description'])
		lat = gmTools.coalesce(self.__issue['laterality'], '')
		if lat.find('s') == -1:
			self._ChBOX_left.SetValue(0)
		else:
			self._ChBOX_left.SetValue(1)
		if lat.find('d') == -1:
			self._ChBOX_right.SetValue(0)
		else:
			self._ChBOX_right.SetValue(1)
		self._TCTRL_notes.SetValue('')
		if self.__issue['age_noted'] is None:
			self._PRW_age_noted.SetText()
		else:
			self._PRW_age_noted.SetText (
				value = '%sd' % self.__issue['age_noted'].days,
				data = self.__issue['age_noted']
			)
		self._ChBOX_active.SetValue(self.__issue['is_active'])
		self._ChBOX_relevant.SetValue(self.__issue['clinically_relevant'])
		self._ChBOX_is_operation.SetValue(0)		# FIXME
		self._ChBOX_confidential.SetValue(self.__issue['is_confidential'])
		self._ChBOX_caused_death.SetValue(self.__issue['is_cause_of_death'])

		# this dance should assure self._PRW_year_noted gets set -- but it doesn't ...
#		self._PRW_age_noted.SetFocus()
#		self._PRW_condition.SetFocus()

		return True
	#--------------------------------------------------------
	def __is_valid_for_save(self):

		if self._PRW_condition.GetValue().strip() == '':
			self._PRW_condition.SetBackgroundColour('pink')
			self._PRW_condition.Refresh()
			self._PRW_condition.SetFocus()
			return False
		self._PRW_condition.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_condition.Refresh()

		# FIXME: check age/year diagnosed
		age_noted = self._PRW_age_noted.GetValue().strip()
		if age_noted != '':
			if gmTools.str2interval(str_interval=age_noted) is None:
				self._PRW_age_noted.SetBackgroundColour('pink')
				self._PRW_age_noted.Refresh()
				self._PRW_age_noted.SetFocus()
				return False
		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_age_noted.Refresh()

		return True
	#--------------------------------------------------------
	def save(self, can_create=True):
		if not self.__is_valid_for_save():
			return False

		desc = self._PRW_condition.GetValue().strip()

		if self.__issue is None:
			if not can_create:
				gmDispatcher.send(signal='statustext', msg=_('Creating new health issue not allowed.'))
				return False
			pat = gmPerson.gmCurrentPatient()
			emr = pat.get_emr()
			self.__issue = emr.add_health_issue(issue_name = desc)
		else:
			self.__issue['description'] = desc

		side = ''
		if self._ChBOX_left.GetValue():
			side += 's'
		if self._ChBOX_right.GetValue():
			side += 'd'
		if side != '':
			self.__issue['laterality'] = side

		self.__issue['is_active'] = bool(self._ChBOX_active.GetValue())
		self.__issue['clinically_relevant'] = bool(self._ChBOX_relevant.GetValue())
		self.__issue['is_confidential'] = bool(self._ChBOX_confidential.GetValue())
		self.__issue['is_cause_of_death'] = bool(self._ChBOX_caused_death.GetValue())
		age_noted = self._PRW_age_noted.GetData()
		if age_noted is not None:
			self.__issue['age_noted'] = age_noted

		self.__issue.save_payload()			# FIXME: error checking

		narr = self._TCTRL_notes.GetValue().strip()
		if narr != '':
			pat = gmPerson.gmCurrentPatient()
			emr = pat.get_emr()
			epi = emr.add_episode(episode_name = _('past medical history'), pk_health_issue = self.__issue['pk'], is_open=None)
			if epi is not None:
				epi['episode_open'] = False
				epi.save_payload()			# FIXME: error handling
				emr.add_clin_narrative(note = narr, soap_cat='s', episode=epi)

		# FIXME: handle is_operation

		return True
#------------------------------------------------------------
class cHealthIssueEditAreaDlg(wxgHealthIssueEditAreaDlg.wxgHealthIssueEditAreaDlg):

	def __init__(self, *args, **kwargs):
		try:
			issue = kwargs['issue']
			del kwargs['issue']
		except KeyError:
			issue = None

		wxgHealthIssueEditAreaDlg.wxgHealthIssueEditAreaDlg.__init__(self, *args, **kwargs)

		if issue is None:
			self._BTN_save.SetLabel(_('Save'))
			self._BTN_clear.SetLabel(_('Clear'))
		else:
			self._BTN_save.SetLabel(_('Update'))
			self._BTN_clear.SetLabel(_('Restore'))

		self._PNL_edit_area.refresh(issue = issue)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PNL_edit_area.refresh()
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	
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
				frame = wx.Frame (
							None,
							-4,
							'Testing EMR struct widgets',
							size=wx.Size(600, 400),
							style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
						)
				filemenu= wx.Menu()
				filemenu.AppendSeparator()
				filemenu.Append(ID_EXIT,"E&xit"," Terminate test application")

				# Creating the menubar.	
				menuBar = wx.MenuBar()
				menuBar.Append(filemenu,"&File")
	
				frame.SetMenuBar(menuBar)
	
				txt = wx.StaticText( frame, -1, _("Select desired test option from the 'File' menu"),
				wx.DefaultPosition, wx.DefaultSize, 0 )

				# event handlers
				wx.EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)

				# patient EMR
				self.__pat = gmPerson.gmCurrentPatient()

				frame.Show(1)
				return 1					
			#--------------------------------------------------------
			def OnCloseWindow (self, e):
				"""
				Close test aplication
				"""
				self.ExitMainLoop ()
	#----------------------------------------------------------------
	def test_encounter_edit_area_panel():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		enc = emr.get_active_encounter()
		#enc = gmEMRStructItems.cEncounter(1)
		pnl = cEncounterEditAreaPnl(app.frame, -1, encounter=enc)
		app.frame.Show(True)
		app.MainLoop()
		return
	#----------------------------------------------------------------
	def test_encounter_edit_area_dialog():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		enc = emr.get_active_encounter()
		#enc = gmEMRStructItems.cEncounter(1)

		dlg = cEncounterEditAreaDlg(parent=app.frame, id=-1, size = (400,400), encounter=enc)
		dlg.ShowModal()

#		pnl = cEncounterEditAreaDlg(app.frame, -1, encounter=enc)
#		app.frame.Show(True)
#		app.MainLoop()
	#----------------------------------------------------------------
	def test_epsiode_edit_area_pnl():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		pnl = cEpisodeEditAreaPnl(app.frame, -1, episode=epi)
		app.frame.Show(True)
		app.MainLoop()
	#----------------------------------------------------------------
	def test_episode_edit_area_dialog():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		dlg = cEpisodeEditAreaDlg(parent=app.frame, id=-1, size = (400,400), episode=epi)
		dlg.ShowModal()
	#----------------------------------------------------------------
	def test_episode_selection_prw():
		app = wx.PyWidgetTester(size = (400, 40))
		app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(180,20), pos=(10,20))
#		app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(350,20), pos=(10,20), patient_id=pat.ID)
		app.MainLoop()
	#----------------------------------------------------------------
	def test_health_issue_edit_area_dlg():
		app = wx.PyWidgetTester(size = (200, 300))
		dlg = cHealthIssueEditAreaDlg(parent=None, id=-1, size = (400,400))
		dlg.ShowModal()
	#----------------------------------------------------------------
	def test_health_issue_edit_area_pnl():
		app = wx.PyWidgetTester(size = (200, 300))
		app.SetWidget(cHealthIssueEditAreaPnl, id=-1, size = (400,400))
		app.MainLoop()
	#================================================================

	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):

		gmI18N.activate_locale()
		gmI18N.install_domain()
		gmDateTime.init()

		# obtain patient
		pat = gmPerson.ask_for_patient()
		if pat is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=pat)

#	try:
		# lauch emr dialogs test application
#		app = testapp(0)
#		app.MainLoop()
#	except StandardError:
#		_log.exception("unhandled exception caught !")
		# but re-raise them
#		raise

		#test_encounter_edit_area_panel()
		#test_encounter_edit_area_dialog()
		#test_epsiode_edit_area_pnl()
		#test_episode_edit_area_dialog()
		test_health_issue_edit_area_dlg()
		#test_episode_selection_prw()

#================================================================
# $Log: gmEMRStructWidgets.py,v $
# Revision 1.75  2008-05-07 15:21:10  ncq
# - move health issue EA behaviour close to Richard's specs
#
# Revision 1.74  2008/03/05 22:37:45  ncq
# - new style logging
# - new health issue adding
#
# Revision 1.73  2008/01/30 14:03:41  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.72  2008/01/22 12:21:27  ncq
# - better encounter editor
#
# Revision 1.71  2007/10/07 12:32:41  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.70  2007/08/29 22:08:57  ncq
# - narrative widgets factored out
#
# Revision 1.69  2007/08/29 14:38:39  ncq
# - improve encounter details dialog
#
# Revision 1.68  2007/08/15 09:19:32  ncq
# - cleanup
#
# Revision 1.67  2007/08/13 22:00:48  ncq
# - proper year format specs
#
# Revision 1.66  2007/08/13 11:07:41  ncq
# - make episode descriptions phrasewheel actually *match*
#   on input, IOW, add a where clause to the select ;-)
#
# Revision 1.65  2007/08/12 00:09:07  ncq
# - no more gmSignals.py
#
# Revision 1.64  2007/07/13 12:20:48  ncq
# - select_narrative_from_episodes(), related widgets, and test suite
#
# Revision 1.63  2007/06/10 10:02:53  ncq
# - episode pk is pk_episode
#
# Revision 1.62  2007/05/18 13:28:57  ncq
# - implement cMoveNarrativeDlg
#
# Revision 1.61  2007/05/14 13:11:24  ncq
# - use statustext() signal
#
# Revision 1.60  2007/04/27 13:28:25  ncq
# - use c2ButtonQuestionDlg
#
# Revision 1.59  2007/04/25 22:00:47  ncq
# - use better question dialog for very recent encounter
#
# Revision 1.58  2007/04/13 15:58:00  ncq
# - don't conflict open episode on itself
#
# Revision 1.57  2007/04/02 18:39:52  ncq
# - gmFuzzyTimestamp -> gmDateTime
#
# Revision 1.56  2007/03/31 21:50:15  ncq
# - cPatient now cIdentity child
#
# Revision 1.55  2007/03/18 14:05:31  ncq
# - re-add lost 1.55
#
# Revision 1.55  2007/03/12 12:27:13  ncq
# - convert some statustext calls to use signal handler
#
# Revision 1.54  2007/03/08 11:39:13  ncq
# - cEpisodeSelectionPhraseWheel
# 	- limit 30
# 	- order by weight, description
# 	- show both open and closed
# 	- include health issue string
# 	- test suite
#
# Revision 1.53  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.52  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.51  2007/02/16 12:53:19  ncq
# - now that we have cPhraseWheel.suppress_text_update_smarts we
#   can avoid infinite looping due to circular on_modified callbacks
#
# Revision 1.50  2007/02/09 14:59:39  ncq
# - cleanup
#
# Revision 1.49  2007/02/06 13:43:40  ncq
# - no more aDelay in __init__()
#
# Revision 1.48  2007/02/05 12:15:23  ncq
# - no more aMatchProvider/selection_only in cPhraseWheel.__init__()
#
# Revision 1.47  2007/02/04 15:53:58  ncq
# - use SetText()
#
# Revision 1.46  2007/01/15 20:22:09  ncq
# - fix several bugs in move_episode_to_issue()
#
# Revision 1.45  2007/01/15 13:02:26  ncq
# - completely revamped move_episode_to_issue() and use it
#
# Revision 1.44  2007/01/09 12:59:01  ncq
# - datetime.timedelta needs int, not decimal, so make epi_ttl an int
# - missing _ in front of CHBOX_closed
# - save() needs to return True/False so dialog can close or not
#
# Revision 1.43  2007/01/04 23:29:02  ncq
# - cEpisodeDescriptionPhraseWheel
# - cEpisodeEditAreaPnl
# - cEpisodeEditAreaDlg
# - test suite enhancement
#
# Revision 1.42  2007/01/02 16:18:10  ncq
# - health issue phrasewheel: clin.health_issue has fk_patient, not pk_patient
#
# Revision 1.41  2006/12/25 22:52:14  ncq
# - encounter details editor
#   - set patient name
#   - valid_for_save(), save()
#   - properly set started/ended
#
# Revision 1.40  2006/12/23 01:07:28  ncq
# - fix encounter type phrasewheel query
# - add encounter details edit area panel/dialog
#   - still needs save() and friends fixed
# - general cleanup/moving about of stuff
# - fix move_episode_to_issue() logic
# - start cleanup of test suite
#
# Revision 1.39  2006/11/28 20:44:36  ncq
# - some rearrangement
#
# Revision 1.38  2006/11/27 23:15:01  ncq
# - remove prints
#
# Revision 1.37  2006/11/27 23:05:49  ncq
# - add commented out on_modified callbacks
#
# Revision 1.36  2006/11/27 12:40:20  ncq
# - adapt to field name fixes from wxGlade
#
# Revision 1.35  2006/11/24 16:40:35  ncq
# - age_noted can be NULL so handle set when refresh()ing health issue edit area
#
# Revision 1.34  2006/11/24 14:22:35  ncq
# - cannot pass issue keyword to wx.Dialog child in cHealthIssueEditAreaDlg.__init__
# - relabel buttons to save or update re clear/restore when adding/editing health issue
# - EndModal needs argument
#
# Revision 1.33  2006/11/24 09:55:05  ncq
# - cHealthIssueEditArea(Pnl/Dlg) closely following Richard's specs
# - test code
#
# Revision 1.32  2006/11/15 00:40:07  ncq
# - properly set up context for phrasewheels
#
# Revision 1.31  2006/10/31 17:21:16  ncq
# - unicode()ify queries
#
# Revision 1.30  2006/10/24 13:22:40  ncq
# - gmPG -> gmPG2
# - no need for service name in cMatchProvider_SQL2()
#
# Revision 1.29  2006/09/03 11:30:28  ncq
# - add move_episode_to_issue()
#
# Revision 1.28  2006/06/26 21:37:43  ncq
# - cleanup
#
# Revision 1.27  2006/06/26 13:07:00  ncq
# - fix issue selection phrasewheel SQL UNION
# - improved variable naming
# - track patient id in set_patient on issue/episode selection phrasewheel
#   so GetData can create new issues/episodes if told to do so
# - add cIssueSelectionDlg
#
# Revision 1.26  2006/06/23 21:32:11  ncq
# - add cIssueSelectionPhrasewheel
#
# Revision 1.25  2006/05/31 09:46:20  ncq
# - cleanup
#
# Revision 1.24  2006/05/28 15:40:51  ncq
# - fix typo in variable
#
# Revision 1.23  2006/05/25 22:19:25  ncq
# - add preconfigured episode selection/creation phrasewheel
# - cleanup, fix unit test
#
# Revision 1.22  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.21  2005/12/26 05:26:37  sjtan
#
# match schema
#
# Revision 1.20  2005/12/26 04:23:05  sjtan
#
# match schema changes.
#
# Revision 1.19  2005/12/06 14:24:15  ncq
# - clin.clin_health_issue/episode -> clin.health_issue/episode
#
# Revision 1.18  2005/10/20 07:42:27  ncq
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
