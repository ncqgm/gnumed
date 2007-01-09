"""GNUmed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).
	
	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRStructWidgets.py,v $
# $Id: gmEMRStructWidgets.py,v 1.44 2007-01-09 12:59:01 ncq Exp $
__version__ = "$Revision: 1.44 $"
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL"

# stdlib
import sys, re, datetime as pydt

# 3rd party
import wx

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmMatchProvider, gmDispatcher, gmSignals, gmTools, gmFuzzyTimestamp, gmCfg
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
if __name__ == '__main__':
	gmI18N.install_domain()
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmEditArea
from Gnumed.wxGladeWidgets import wxgIssueSelectionDlg
from Gnumed.wxGladeWidgets import wxgHealthIssueEditAreaPnl, wxgHealthIssueEditAreaDlg
from Gnumed.wxGladeWidgets import wxgEncounterEditAreaPnl, wxgEncounterEditAreaDlg
from Gnumed.wxGladeWidgets import wxgEpisodeEditAreaPnl, wxgEpisodeEditAreaDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
	
# module level constants
dialog_CANCELLED = -1
dialog_OK = -2

#================================================================
# encounter related widgets/functions
#----------------------------------------------------------------
class cEncounterTypePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of encounter type.

	- user input interpreted as encounter type in English or local language
	- data returned is pk of corresponding encounter type or None
	"""
	def __init__(self, *args, **kwargs):

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
		kwargs['aMatchProvider'] = mp
		kwargs['aDelay'] = 50
		kwargs['selection_only'] = True

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)
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
		self._LCTRL_problems.InsertColumn(1, _('Foundational Issue'))
		self._LCTRL_problems.InsertColumn(2, _('Assessment'))
		self._LCTRL_problems.InsertColumn(3, _('Narrative'))
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, encounter = None):

		if encounter is not None:
			self.__encounter = encounter

		# getting the patient via the encounter allows us to act
		# on any encounter regardless of the currently active encounter
		ident = gmPerson.cIdentity(aPK_obj = self.__encounter['pk_patient'])
		pat = gmPerson.cPatient(identity = ident)
		emr = pat.get_emr()
		episodes = emr.get_episodes_by_encounter(pk_encounter = self.__encounter['pk_encounter'])
		pos = len(episodes) + 1

		print "epis:", episodes
		print "FIXME: episodes empty"

		self._LCTRL_problems.DeleteAllItems()
		for episode in episodes:
			row_num = self._LCTRL_problems.InsertStringItem(pos, label = episode['description'])
			self._LCTRL_problems.SetStringItem(index = row_num, col = 1, label = gmTools.coalesce(episode['health_issue'], ''))
		if len(episodes) > 0:
			self._LCTRL_problems.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_problems.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)		# wx.LIST_AUTOSIZE_USEHEADER

		self._PRW_encounter_type.SetValue(self.__encounter['l10n_type'], data=self.__encounter['pk_type'])

		fts = gmFuzzyTimestamp.cFuzzyTimestamp (
			timestamp = self.__encounter['started'],
			accuracy = gmFuzzyTimestamp.acc_minutes
		)
		self._PRW_start.SetValue(fts.format_accurately(), data=fts)

		fts = gmFuzzyTimestamp.cFuzzyTimestamp (
			timestamp = self.__encounter['last_affirmed'],
			accuracy = gmFuzzyTimestamp.acc_minutes
		)
		self._PRW_end.SetValue(fts.format_accurately(), data=fts)

		self._TCTRL_rfe.SetValue(gmTools.coalesce(self.__encounter['reason_for_encounter'], ''))
		self._TCTRL_aoe.SetValue(gmTools.coalesce(self.__encounter['assessment_of_encounter'], ''))

		if self.__encounter['last_affirmed'] == self.__encounter['started']:
			self._PRW_end.SetFocus()
		else:
			self._TCTRL_aoe.SetFocus()

		self._LBL_patient.SetLabel(ident.get_description())

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

		self.Refresh()		# needed ?
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
def move_episode_to_issue(episode=None, target_issue=None):

	# we need a target issue
	if target_issue is None:
		if episode['pk_health_issue'] is None:
			msg = _(
				'\nThe episode\n'
				'  [%(epi)s]\n'
				'currently does not belong to a health issue.\n\n'
				'Please select the health issue you want to move it to:\n'
			) % {'epi': episode['description']}
		else:
			msg = _(
				'\nThe episode\n'
				'  [%(epi)s]\n'
				'currently belongs to the health issue\n'
				'  [%(issue)s]\n\n'
				'Please select the health issue you want to move it to:\n'
			) % {'epi': episode['description'], 'issue': episode['health_issue']}

		dlg = cIssueSelectionDlg(self, -1, message=msg)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.Destroy()
			return True

		pk_issue = dlg._PhWheel_issue.GetData()
		dlg.Destroy()
		if episode['pk_health_issue'] == pk_issue:
			return True

		target_issue = gmEMRStructItems.cHealthIssue(aPK_obj=pk_issue)

	# resolve two-open-episodes conflict
	if episode['episode_open']:
		# FIXME: should we do this on the source issue, too ?
		target_issue.close_expired_episode(ttl=90)
		epi_exist = target_issue.get_open_episode()
		if epi_exist is not None:
			move_range = episode.get_access_range()
			exist_range = epi_exist.get_access_range()
			decision = gmGuiHelpers.gm_show_question (
"""There cannot be two open episodes for a
health issue at the same time.

The episode you want to move

 (1) "%(epi_move)s" (%(epi_move_first)s - %(epi_move_last)s)

is currently open. The health issue

 "%(issue)s"

you want to move it to also has an open episode:

 (2) "%(epi_exist)s" (%(epi_exist_first)s - %(epi_exist_last)s)

[%(y)s] - close the episode on the move (1)
[%(n)s] - close the existing episode (2)
[%(c)s] - abort moving the episode
"""				% {
					'epi_move': episode['description'],
					'epi_move_first': move_range['earliest'],
					'epi_move_last': move_range['latest'],
					'issue': target_issue['description'],
					'epi_exist': epi_exist['description'],
					'epi_exist_first': exist_range['earliest'],
					'epi_exist_last': exist_range['latest'],
					'y': _('yes'),
					'n': _('no'),
					'c': _('cancel')
				},
				_('Moving episode'),
				cancel_button = True
			)
			if decision is None:
				return True
			if decision is True:
				episode['episode_open'] = False
			elif decision is False:
				epi_exist['episode_open'] = False
				epi_exist.save_payload()

	episode['pk_health_issue'] = target_issue['pk']
	success, data = episode.save_payload()
	if not success:
		gmGuiHelpers.gm_show_error (
			_('Cannot move episode\n [%(epi)s]\n into health issue\n [%(issue)s].') % {
				'epi': episode['description'],
				'issue': target_issue['description']
			},
			_('Moving episode')
		)
		return True

	# FIXME: signal issue/episode change
	return True
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
				order by description
				limit 30"""
			]
		)
		kwargs['aMatchProvider'] = mp
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
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
u"""select pk_episode, description, 1 from clin.v_pat_episodes where
		episode_open is true and
		description %(fragment_condition)s and
		%(ctxt_pat)s""",
u"""select pk_episode, description || _(' (closed)'), 1 from clin.v_pat_episodes where
		description %(fragment_condition)s and
		%(ctxt_pat)s"""
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
				mp.set_context('pat', pat.getID())
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		kwargs['aMatchProvider'] = mp
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
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
					ident = gmPerson.cIdentity(aPK_obj=self.__patient_id)
					pat = gmPerson.cPatient(identity=ident)
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
		gmDispatcher.connect(self._pre_patient_selection, gmSignals.pre_patient_selection())
		gmDispatcher.connect(self._post_patient_selection, gmSignals.post_patient_selection())
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.getID())
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
			self._PRW_issue.SetValue(self.__episode['health_issue'], data=self.__episode['pk_health_issue'])

		self._PRW_description.SetValue(self.__episode['description'], data=self.__episode['description'])

		self._CHBOX_closed.SetValue(not self.__episode['episode_open'])
	#------------------------------------------------------------
	def save(self):
		self.__episode['episode_open'] = not self._CHBOX_closed.IsChecked()

		issue_name = self._PRW_issue.GetValue().strip()
		if len(issue_name) == 0:
			self.__episode['pk_health_issue'] = None
		else:
			self.__episode['pk_health_issue'] = self._PRW_issue.GetData(can_create=True)
			if self.__episode['episode_open']:
				issue = gmEMRStructItems.cHealthIssue(aPK_obj=self.__episode['pk_health_issue'])
				db_cfg = gmCfg.cCfgSQL()
				epi_ttl = int(db_cfg.get2 (
					option = u'episode.ttl',
					workplace = gmPerson.gmCurrentProvider().get_workplace(),
					bias = 'user',
					default = 60				# 2 months
				))
				if issue.close_expired_episode(ttl=epi_ttl) is False:
					prev_epi = issue.get_open_episode()
					first, last = prev_epi.get_access_range()
					title = _('open episode conflict')
					msg = _(
						'You want to move the open episode\n'
						' [%s]\n'
						'to the Foundational Issue\n'
						' [%s]\n\n'
						'That issue already has an open episode:\n'
						' [%s]\n'
						' last accessed: %s\n\n'
						'There cannot be two open episodes at once, however!\n\n'
						'Do you want to close the episode\n'
						' [%s] ?'
						) % (
						self.__episode['description'],
						issue_name,
						prev_epi['description'],
						last.strftime('%Y-%m-%d'),
						prev_epi['description']
					)
					if not gmGuiHelpers.gm_show_question(msg, title):
						return False
					issue.close_episode()

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
				mp.set_context('pat', pat.getID())
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		kwargs['aMatchProvider'] = mp
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
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
					ident = gmPerson.cIdentity(aPK_obj=self.__patient_id)
					pat = gmPerson.cPatient(identity=ident)
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
		gmDispatcher.connect(self._pre_patient_selection, gmSignals.pre_patient_selection())
		gmDispatcher.connect(self._post_patient_selection, gmSignals.post_patient_selection())
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.getID())
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

	# FIXME: add on_lose_focus handling for year_diagnosed

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
		self._PRW_condition.setMatchProvider(mp = mp)

		self._PRW_age_noted.add_callback_on_lose_focus(self._on_leave_age_noted)
		self._PRW_year_noted.add_callback_on_lose_focus(self._on_leave_year_noted)

#		self._PRW_age_noted.add_callback_on_modified(self._on_modified_age_noted)
#		self._PRW_year_noted.add_callback_on_modified(self._on_modified_year_noted)

		self.refresh()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _on_leave_age_noted(self, *args, **kwargs):

		str_age = self._PRW_age_noted.GetValue().strip()

		if str_age == '':
			wx.CallAfter(self._PRW_year_noted.SetValue, '')
			return True

		age = gmTools.str2interval(str_interval = str_age)
		pat = gmPerson.gmCurrentPatient()
		ident = pat.get_identity()
		max_age =  pydt.datetime.now(tz=ident['dob'].tzinfo) - ident['dob']

		if age is None:
			gmGuiHelpers.gm_statustext(_('Cannot parse [%s] into valid interval.') % str_age)
		if age >= max_age:
			gmGuiHelpers.gm_statustext(_('Patient is only %s old. Cannot accept age [%s].') % (ident.get_medical_age(), age))

		if (age is None) or (age >= max_age):
			self._PRW_age_noted.SetBackgroundColour('pink')
			self._PRW_age_noted.Refresh()
			wx.CallAfter(self._PRW_year_noted.SetValue, '')
			return True

		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_age_noted.Refresh()
		self._PRW_age_noted.SetData(data=age)

		fts = gmFuzzyTimestamp.cFuzzyTimestamp (
			timestamp = ident['dob'] + age,
			accuracy = gmFuzzyTimestamp.acc_months
		)
		wx.CallAfter(self._PRW_year_noted.SetValue, str(fts), fts)
		# if we do this we will *always* navigate there, regardless of TAB vs ALT-TAB
		#wx.CallAfter(self._ChBOX_active.SetFocus)
		# if we do the following instead it will take us to the save/update button ...
		#wx.CallAfter(self.Navigate)

		return True
	#--------------------------------------------------------
	def _on_leave_year_noted(self, *args, **kwargs):

		year_noted = self._PRW_year_noted.GetData()

		if year_noted is None:
			if self._PRW_year_noted.GetValue().strip() == '':
				wx.CallAfter(self._PRW_age_noted.SetValue, '')
				return True

		year_noted = year_noted.get_pydt()

		if year_noted >= pydt.datetime.now(tz=year_noted.tzinfo):
			gmGuiHelpers.gm_statustext(_('Condition diagnosed in the future.'))
			self._PRW_year_noted.SetBackgroundColour('pink')
			self._PRW_year_noted.Refresh()
			wx.CallAfter(self._PRW_age_noted.SetValue, '')
			return True

		self._PRW_year_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_year_noted.Refresh()

		pat = gmPerson.gmCurrentPatient()
		ident = pat.get_identity()
		age = year_noted - ident['dob']
		str_age = gmPerson.format_age_medically(age)
		wx.CallAfter(self._PRW_age_noted.SetValue, str_age, age)

		return True
	#--------------------------------------------------------
	def _on_modified_age_noted(self, *args, **kwargs):
		self._PRW_year_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		#self._PRW_year_noted.Refresh()
		wx.CallAfter(self._PRW_year_noted.SetValue, '', None)
		return True
	#--------------------------------------------------------
	def _on_modified_year_noted(self, *args, **kwargs):
		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		#self._PRW_age_noted.Refresh()
		wx.CallAfter(self._PRW_age_noted.SetValue, '', None)
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
			self._PRW_condition.SetValue('')
			self._ChBOX_left.SetValue(0)
			self._ChBOX_right.SetValue(0)
			self._TCTRL_notes.SetValue('')
			self._PRW_age_noted.SetValue('')
			self._PRW_year_noted.SetValue('')
			self._ChBOX_active.SetValue(0)
			self._ChBOX_relevant.SetValue(1)
			self._ChBOX_is_operation.SetValue(0)
			self._ChBOX_confidential.SetValue(0)
			self._ChBOX_caused_death.SetValue(0)
			return True

		if not isinstance(self.__issue, gmEMRStructItems.cHealthIssue):
			raise ValueError('[%s].refresh(): expected gmEMRStructItems.cHealthIssue instance, got [%s] instead' % (self.__class__.__name__, self.__issue))

		self._PRW_condition.SetValue(self.__issue['description'])
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
			self._PRW_age_noted.SetValue('')
		else:
			self._PRW_age_noted.SetValue (
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
				gmGuiHelpers.gm_statustext(_('Creating new health issue not allowed.'))
				return False
			pat = gmPerson.gmCurrentPatient()
			success, self.__issue = gmEMRStructItems.create_health_issue (
				patient_id = pat.get_id(),
				description = desc
			)
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

		self.Refresh()		# needed ?
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
#============================================================
# unchecked older widgtets
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

		
		emr = self.__pat.get_emr()
		

	        issues = emr.get_health_issues()
	        issue_map = {}
		for issue in issues:
			issue_map[issue['pk']] = issue['description']

		
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
		self.__selected_episode = self.__pat.get_emr().add_episode (
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
		episodes = self.__pat.get_emr().get_episodes()
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
			#self.__pat.get_emr().add_episode(episode_name= , pk_health_issue=self.__pk_health_issue)
			print 'Creating episode: %s' % self.__PRW_description.GetValue()
			# FIXME 
			self.__selected_episode = self.__pat.get_emr().add_episode (
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
#	_log.Log (gmLog.lInfo, "starting EMR struct editor...")

#	ID_EPISODE_SELECTOR = wx.NewId()
#	ID_EPISODE_EDITOR = wx.NewId()
#	ID_EXIT = wx.NewId()
	
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
				pk_issue = self.__pat.get_emr().get_health_issues()[0]['pk']
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
				pk_issue = self.__pat.get_emr().get_health_issues()[0]['pk']
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
		return
	#----------------------------------------------------------------
	def test_epsiode_edit_area_pnl():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		pnl = cEpisodeEditAreaPnl(app.frame, -1, episode=epi)
		app.frame.Show(True)
		app.MainLoop()
		return
	#----------------------------------------------------------------
	def test_episode_edit_area_dialog():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		dlg = cEpisodeEditAreaDlg(parent=app.frame, id=-1, size = (400,400), episode=epi)
		dlg.ShowModal()
		return
	#================================================================
#	import sys

#	_cfg = gmCfg.gmDefCfgFile	 
#	if _cfg is None:
#		_log.Log(gmLog.lErr, "Cannot run without config file.")
#		sys.exit("Cannot run without config file.")

#	try:
#		# make sure we have a db connection
#		gmPG2.set_default_client_encoding('UNICODE')

#		# obtain patient
#		patient = gmPerson.ask_for_patient()
#		if patient is None:
#			print "No patient. Exiting gracefully..."
#			sys.exit(0)
#		gmPerson.set_active_patient(patient=patient)

		# lauch emr dialogs test application
#		app = testapp(0)
#		app.MainLoop()
				
		# clean up
#		if patient is not None:
#			try:
#				patient.cleanup()
#			except:
#				print "error cleaning up patient"
#	except StandardError:
#		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
#		# but re-raise them
#		raise

#	_log.Log (gmLog.lInfo, "closing notes input...")

	# obtain patient
	pat = gmPerson.ask_for_patient()
	if pat is None:
		print "No patient. Exiting gracefully..."
		sys.exit(0)
	gmPerson.set_active_patient(patient=pat)

	#test_encounter_edit_area_panel()
	#test_encounter_edit_area_dialog()
	#test_epsiode_edit_area_pnl()
	test_episode_edit_area_dialog()

#	app = wx.PyWidgetTester(size = (200, 300))
#	dlg = cHealthIssueEditAreaDlg(parent=None, id=-1, size = (400,400))
#	dlg.ShowModal()

#	app.SetWidget(cHealthIssueEditAreaPnl, id=-1, size = (400,400))
#	app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(180,20), pos=(10,20))
#	app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(180,20), pos=(10,20), patient_id=pat.getID())
#	app.MainLoop()

#================================================================
# $Log: gmEMRStructWidgets.py,v $
# Revision 1.44  2007-01-09 12:59:01  ncq
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
