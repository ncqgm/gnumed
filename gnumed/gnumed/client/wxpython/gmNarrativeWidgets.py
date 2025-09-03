"""GNUmed narrative handling widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging
import time


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgDB

from Gnumed.business import gmPerson
from Gnumed.business import gmHealthIssue
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmPraxis
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmEpisode
from Gnumed.business import gmProblem

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmProgressNotesEAWidgets
from Gnumed.wxpython.gmPatSearchWidgets import set_active_patient


_log = logging.getLogger('gm.ui')

#============================================================
# narrative related widgets
#------------------------------------------------------------
class cNarrativeListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	def __init__(self, *args, **kwargs):

		narrative = kwargs['narrative']
		del kwargs['narrative']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the narrative you are interested in ...'))
		# FIXME: add epi/issue
		self._LCTRL_items.set_columns([_('when'), _('who'), _('type'), _('entry')]) #, _('Episode'), u'', _('Health Issue')])
		# FIXME: date used should be date of encounter, not date_modified
		self._LCTRL_items.set_string_items (
			items = [ [narr['date'].strftime('%x %H:%M'), narr['modified_by'], gmSoapDefs.soap_cat2l10n[narr['soap_cat']], narr['narrative'].replace('\n', '/').replace('\r', '/')] for narr in narrative ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = narrative)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMoveNarrativeDlg

class cMoveNarrativeDlg(wxgMoveNarrativeDlg.wxgMoveNarrativeDlg):

	def __init__(self, *args, **kwargs):

		self.encounter = kwargs['encounter']
		self.source_episode = kwargs['episode']
		del kwargs['encounter']
		del kwargs['episode']

		wxgMoveNarrativeDlg.wxgMoveNarrativeDlg.__init__(self, *args, **kwargs)

		self.LBL_source_episode.SetLabel('%s%s' % (self.source_episode['description'], gmTools.coalesce(self.source_episode['health_issue'], '', ' (%s)')))
		self.LBL_encounter.SetLabel('%s: %s %s - %s' % (
			self.encounter['started'].strftime('%Y %b %d'),
			self.encounter['l10n_type'],
			self.encounter['started'].strftime('%H:%M'),
			self.encounter['last_affirmed'].strftime('%H:%M')
		))
		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		narr = emr.get_clin_narrative(episodes=[self.source_episode['pk_episode']], encounters=[self.encounter['pk_encounter']])
		if len(narr) == 0:
			narr = [{'narrative': _('There is no narrative for this episode in this encounter.')}]
		self.LBL_narrative.SetLabel('\n'.join([n['narrative'] for n in narr]))

	#------------------------------------------------------------
	def _on_move_button_pressed(self, event):

		target_episode = self._PRW_episode_selector.GetData(can_create = False)

		if target_episode is None:
			gmDispatcher.send(signal='statustext', msg=_('Must select episode to move narrative to first.'))
			# FIXME: set to pink
			self._PRW_episode_selector.SetFocus()
			return False

		target_episode = gmEpisode.cEpisode(aPK_obj=target_episode)

		self.encounter.transfer_clinical_data (
			source_episode = self.source_episode,
			target_episode = target_episode
		)

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

#============================================================
#============================================================
from Gnumed.wxGladeWidgets import wxgSoapPluginPnl

class cSoapPluginPnl(wxgSoapPluginPnl.wxgSoapPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A panel for in-context editing of progress notes.

	Expects to be used as a notebook page.

	Left hand side:
	- problem list (health issues and active episodes)
	- previous notes

	Right hand side:
	- panel handling
		- encounter details fields
		- notebook with progress note editors
		- visual progress notes

	Listens to patient change signals, thus acts on the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgSoapPluginPnl.wxgSoapPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__init_ui()
		self.__reset_ui_content()
		self.__register_interests()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_active_problems.set_columns([_('Last'), _('Problem'), _('In health issue')])
		self._LCTRL_active_problems.set_string_items()
		self._LCTRL_active_problems.extend_popup_menu_callback = self._extend_popup_menu

		self._splitter_main.SetSashGravity(0.5)
		self._splitter_left.SetSashGravity(0.5)

		splitter_size = self._splitter_main.GetSize()[0]
		self._splitter_main.SetSashPosition(splitter_size * 3 // 10, True)

		splitter_size = self._splitter_left.GetSize()[1]
		self._splitter_left.SetSashPosition(splitter_size * 6 // 20, True)

	#--------------------------------------------------------
	def _extend_popup_menu(self, menu=None):
		problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		if problem is None:
			return
		self.__focussed_problem = problem

		menu_item = menu.Append(-1, _('Edit'))
		if self.__focussed_problem['type'] == 'issue':
			self.Bind(wx.EVT_MENU, self._on_edit_issue, menu_item)
		if self.__focussed_problem['type'] == 'episode':
			self.Bind(wx.EVT_MENU, self._on_edit_episode, menu_item)

	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""Clear all information from input panel."""

		self._LCTRL_active_problems.set_string_items()

		self._TCTRL_recent_notes.SetValue('')
		self._SZR_recent_notes.StaticBox.SetLabel(_('Most recent notes on selected problem'))

		self._PNL_editors.patient = None
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""Update health problems list."""

		self._LCTRL_active_problems.set_string_items()

		emr = self.__pat.emr
		problems = emr.get_problems (
			include_closed_episodes = self._CHBOX_show_closed_episodes.IsChecked(),
			include_irrelevant_issues = self._CHBOX_irrelevant_issues.IsChecked()
		)

		list_items = []
		active_problems = []
		for problem in problems:
			if not problem['problem_active']:
				if not problem['is_potential_problem']:
					continue

			active_problems.append(problem)

			if problem['type'] == 'issue':
				issue = gmHealthIssue.cHealthIssue.from_problem(problem)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
				if last_encounter is None:
					last = issue['modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')

				list_items.append([last, problem['problem'], gmTools.u_left_arrow_with_tail])

			elif problem['type'] == 'episode':
				epi = gmEpisode.cEpisode.from_problem(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')

				list_items.append ([
					last,
					problem['problem'],
					gmTools.coalesce(value2test = epi['health_issue'], return_instead = '?')		#gmTools.u_diameter
				])

		self._LCTRL_active_problems.set_string_items(items = list_items)
		self._LCTRL_active_problems.set_column_widths()
		self._LCTRL_active_problems.set_data(data = active_problems)

		showing_potential_problems = (
			self._CHBOX_show_closed_episodes.IsChecked()
				or
			self._CHBOX_irrelevant_issues.IsChecked()
		)
		if showing_potential_problems:
			self._SZR_problem_list.StaticBox.SetLabel(_('%s (active+potential) problems') % len(list_items))
		else:
			self._SZR_problem_list.StaticBox.SetLabel(_('%s active problems') % len(list_items))

		return True
	#--------------------------------------------------------
	def __get_info_for_issue_problem(self, problem=None, fancy=False):
		soap = ''
		emr = self.__pat.emr
		prev_enc = emr.get_last_but_one_encounter(issue_id = problem['pk_health_issue'])
		if prev_enc is not None:
			soap += prev_enc.format (
				issues = [ problem['pk_health_issue'] ],
				with_soap = True,
				with_docs = fancy,
				with_tests = fancy,
				patient = self.__pat,
				fancy_header = False,
				with_rfe_aoe = True
			)

		tmp = emr.active_encounter.format_soap (
			soap_cats = 'soapu',
			emr = emr,
			issues = [ problem['pk_health_issue'] ],
		)
		if len(tmp) > 0:
			soap += _('Current encounter:') + '\n'
			soap += '\n'.join(tmp) + '\n'

		if problem['summary'] is not None:
			soap += '\n-- %s ----------\n%s' % (
				_('Cumulative summary'),
				gmTools.wrap (
					text = problem['summary'],
					width = 45,
					initial_indent = ' ',
					subsequent_indent = ' '
				).strip('\n')
			)

		return soap
	#--------------------------------------------------------
	def __get_info_for_episode_problem(self, problem=None, fancy=False):
		soap = ''
		emr = self.__pat.emr
		prev_enc = emr.get_last_but_one_encounter(episode_id = problem['pk_episode'])
		if prev_enc is not None:
			soap += prev_enc.format (
				episodes = [ problem['pk_episode'] ],
				with_soap = True,
				with_docs = fancy,
				with_tests = fancy,
				patient = self.__pat,
				fancy_header = False,
				with_rfe_aoe = True
			)
		else:
			if problem['pk_health_issue'] is not None:
				prev_enc = emr.get_last_but_one_encounter(episode_id = problem['pk_health_issue'])
				if prev_enc is not None:
					soap += prev_enc.format (
						with_soap = True,
						with_docs = fancy,
						with_tests = fancy,
						patient = self.__pat,
						issues = [ problem['pk_health_issue'] ],
						fancy_header = False,
						with_rfe_aoe = True
					)

		if problem['pk_health_issue'] is None:
			tmp = emr.active_encounter.format_soap(soap_cats = 'soapu', emr = emr)
		else:
			tmp = emr.active_encounter.format_soap(soap_cats = 'soapu', emr = emr, issues = [problem['pk_health_issue']])
		if len(tmp) > 0:
			soap += _('Current encounter:') + '\n'
			soap += '\n'.join(tmp) + '\n'

		if problem['summary'] is not None:
			soap += '\n-- %s ----------\n%s' % (
				_('Cumulative summary'),
				gmTools.wrap (
					text = problem['summary'],
					width = 45,
					initial_indent = ' ',
					subsequent_indent = ' '
				).strip('\n')
			)

		return soap
	#--------------------------------------------------------
	def __refresh_recent_notes(self, problem=None):
		"""This refreshes the recent-notes part."""

		if problem is None:
			caption = '<?>'
			txt = ''
		elif problem['type'] == 'issue':
			caption = problem['problem'][:35]
			txt = self.__get_info_for_issue_problem(problem = problem, fancy = not self._RBTN_notes_only.GetValue())
		elif problem['type'] == 'episode':
			caption = problem['problem'][:35]
			txt = self.__get_info_for_episode_problem(problem = problem, fancy = not self._RBTN_notes_only.GetValue())

		self._TCTRL_recent_notes.SetValue(txt)
		self._TCTRL_recent_notes.ShowPosition(self._TCTRL_recent_notes.GetLastPosition())
		self._SZR_recent_notes.StaticBox.SetLabel(_('Most recent info on %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			caption,
			gmTools.u_right_double_angle_quote
		))

		self._TCTRL_recent_notes.Refresh()

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals."""
		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'clin.episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = 'clin.health_issue_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = 'clin.episode_code_mod_db', receiver = self._on_episode_issue_mod_db)
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self.__reset_ui_content()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
		self._PNL_editors.patient = self.__pat
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	# problem list specific events
	#--------------------------------------------------------
	def _on_problem_focused(self, event):
		"""Show related note at the bottom."""
		pass
	#--------------------------------------------------------
	def _on_edit_issue(self, evt):
		gmEMRStructWidgets.edit_health_issue(parent = self, issue = self.__focussed_problem.as_health_issue)

	#--------------------------------------------------------
	def _on_edit_episode(self, evt):
		gmEMRStructWidgets.edit_episode(parent = self, episode = self.__focussed_problem.as_episode)

	#--------------------------------------------------------
	def _on_problem_selected(self, event):
		"""Show related note at the bottom."""
		self.__refresh_recent_notes (
			problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		)
	#--------------------------------------------------------
	def _on_problem_activated(self, event):
		"""Open progress note editor for this problem.
		"""
		problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		if problem is None:
			return True

		allow_duplicate_editors = gmCfgDB.get4user (
			option = 'horstspace.soap_editor.allow_same_episode_multiple_times',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		if self._PNL_editors.add_editor(problem = problem, allow_same_problem = allow_duplicate_editors):
			return True

		gmGuiHelpers.gm_show_error (
			_(
				'Cannot open progress note editor for\n\n'
				'[%s].\n\n'
			) % problem['problem'],
			_('opening progress note editor')
		)
		return False
	#--------------------------------------------------------
	def _on_show_closed_episodes_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	def _on_irrelevant_issues_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	# recent-notes specific events
	#--------------------------------------------------------
	def _on_notes_only_selected(self, event):
		self.__refresh_recent_notes (
			problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		)
	#--------------------------------------------------------
	def _on_full_encounter_selected(self, event):
		self.__refresh_recent_notes (
			problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	# only needed for debugging:
	#def _schedule_data_reget(self):
	#	gmRegetMixin.cRegetOnPaintMixin._schedule_data_reget(self)
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		return True

#============================================================
from Gnumed.wxGladeWidgets import wxgFancySoapEditorPnl

class cFancySoapEditorPnl(wxgFancySoapEditorPnl.wxgFancySoapEditorPnl):
	"""A panel holding everything needed to edit in context:

		- encounter metadata
		- progress notes
			- textual
			- visual
		- episode summary

	Does NOT act on the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgFancySoapEditorPnl.wxgFancySoapEditorPnl.__init__(self, *args, **kwargs)

		self.__init_ui()
		self.patient = None
		self.__register_interests()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def add_editor(self, problem=None, allow_same_problem=False):
		return self._NB_soap_editors.add_editor(problem = problem, allow_same_problem = allow_same_problem)
	#--------------------------------------------------------
	def _get_patient(self):
		return self.__pat

	def _set_patient(self, patient):
		try:
			self.__pat
		except AttributeError:
			self.__pat = None
		if not self.__pat:
			if patient:
				patient.register_before_switching_from_patient_callback(callback = self._before_switching_from_patient_callback)
		self.__pat = patient
		self.__refresh_encounter()
		self.__refresh_soap_notebook()

	patient = property(_get_patient, _set_patient)
	#--------------------------------------------------------
	def save_encounter(self):

		if self.__pat is None:
			return True

		if not self.__encounter_valid_for_save():
			return False

		enc = self.__pat.emr.active_encounter

		rfe = self._TCTRL_rfe.GetValue().strip()
		if len(rfe) == 0:
			enc['reason_for_encounter'] = None
		else:
			enc['reason_for_encounter'] = rfe
		aoe = self._TCTRL_aoe.GetValue().strip()
		if len(aoe) == 0:
			enc['assessment_of_encounter'] = None
		else:
			enc['assessment_of_encounter'] = aoe

		enc.save_payload()

		enc.generic_codes_rfe = [ c['data'] for c in self._PRW_rfe_codes.GetData() ]
		enc.generic_codes_aoe = [ c['data'] for c in self._PRW_aoe_codes.GetData() ]

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._NB_soap_editors.MoveAfterInTabOrder(self._PRW_aoe_codes)
	#--------------------------------------------------------
	def __reset_soap_notebook(self):
		self._NB_soap_editors.DeleteAllPages()
		self._NB_soap_editors.add_editor()
	#--------------------------------------------------------
	def __refresh_soap_notebook(self):
		self.__reset_soap_notebook()

		if self.__pat is None:
			return

#		auto_open_recent_problems = gmCfgDB.get4user (
#			option = 'horstspace.soap_editor.auto_open_latest_episodes',
#			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
#			default = True
#		)

		emr = self.__pat.emr
		recent_epis = emr.active_encounter.get_episodes()
		prev_enc = emr.get_last_but_one_encounter()
		if prev_enc is not None:
			recent_epis.extend(prev_enc.get_episodes())

		for epi in recent_epis:
			if not epi['episode_open']:
				continue
			self._NB_soap_editors.add_editor(problem = epi)

	#--------------------------------------------------------
	def __reset_encounter_fields(self):
		self._TCTRL_rfe.SetValue('')
		self._PRW_rfe_codes.SetText(suppress_smarts = True)
		self._TCTRL_aoe.SetValue('')
		self._PRW_aoe_codes.SetText(suppress_smarts = True)

	#--------------------------------------------------------
	def __refresh_encounter(self):
		"""Update encounter fields."""

		self.__reset_encounter_fields()

		if self.__pat is None:
			return

		enc = self.__pat.emr.active_encounter

		self._TCTRL_rfe.SetValue(gmTools.coalesce(enc['reason_for_encounter'], ''))
		val, data = self._PRW_rfe_codes.generic_linked_codes2item_dict(enc.generic_codes_rfe)
		self._PRW_rfe_codes.SetText(val, data)

		self._TCTRL_aoe.SetValue(gmTools.coalesce(enc['assessment_of_encounter'], ''))
		val, data = self._PRW_aoe_codes.generic_linked_codes2item_dict(enc.generic_codes_aoe)
		self._PRW_aoe_codes.SetText(val, data)

		self._TCTRL_rfe.Refresh()
		self._PRW_rfe_codes.Refresh()
		self._TCTRL_aoe.Refresh()
		self._PRW_aoe_codes.Refresh()

	#--------------------------------------------------------
	def __refresh_current_editor(self):
		self._NB_soap_editors.refresh_current_editor()

#	#--------------------------------------------------------
#	def __encounter_modified(self):
#		"""Assumes that the field data is valid."""
#
#		emr = self.__pat.emr
#		enc = emr.active_encounter
#
#		data = {
#			'pk_type': enc['pk_type'],
#			'reason_for_encounter': gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u''),
#			'assessment_of_encounter': gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
#			'pk_location': enc['pk_org_unit'],
#			'pk_patient': enc['pk_patient'],
#			'pk_generic_codes_rfe': self._PRW_rfe_codes.GetData(),
#			'pk_generic_codes_aoe': self._PRW_aoe_codes.GetData(),
#			'started': enc['started'],
#			'last_affirmed': enc['last_affirmed']
#		}
#
#		return not enc.same_payload(another_object = data)
	#--------------------------------------------------------
	def __encounter_valid_for_save(self):
		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals."""
		# synchronous signals
		gmDispatcher.send(signal = 'register_pre_exit_callback', callback = self._pre_exit_callback)

		# client internal signals
		gmDispatcher.connect(signal = 'blobs.doc_med_mod_db', receiver = self._on_doc_mod_db)			# visual progress notes
		gmDispatcher.connect(signal = 'current_encounter_modified', receiver = self._on_current_encounter_modified)
		gmDispatcher.connect(signal = 'current_encounter_switched', receiver = self._on_current_encounter_switched)
		gmDispatcher.connect(signal = 'clin.rfe_code_mod_db', receiver = self._on_encounter_code_modified)
		gmDispatcher.connect(signal = 'clin.aoe_code_mod_db', receiver = self._on_encounter_code_modified)
	#--------------------------------------------------------
	def _before_switching_from_patient_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns True.
		"""
		# don't worry about the encounter here - it will be offered
		# for editing higher up if anything was saved to the EMR
		if self.__pat is None:
			return True
		return self._NB_soap_editors.warn_on_unsaved_soap()
	#--------------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to (be) shut down.

		Shutdown will not proceed before this returns.
		"""
		if self.__pat is None:
			return True

#		if self.__encounter_modified():
#			do_save_enc = gmGuiHelpers.gm_show_question (
#				question = _(
#					'You have modified the details\n'
#					'of the current encounter.\n'
#					'\n'
#					'Do you want to save those changes ?'
#				),
#				title = _('Starting new encounter')
#			)
#			if do_save_enc:
#				if not self.save_encounter():
#					gmDispatcher.send(signal = u'statustext', msg = _('Error saving current encounter.'), beep = True)

		saved = self._NB_soap_editors.save_all_editors (
			emr = self.__pat.emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), ''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), '')
			]
		)
		if not saved:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
		return True
	#--------------------------------------------------------
	def _on_doc_mod_db(self):
		self.__refresh_current_editor()
	#--------------------------------------------------------
	def _on_encounter_code_modified(self):
		self.__pat.emr.active_encounter.refetch_payload()
		self.__refresh_encounter()
	#--------------------------------------------------------
	def _on_current_encounter_modified(self):
		self.__refresh_encounter()
	#--------------------------------------------------------
	def _on_current_encounter_switched(self):
		self.__refresh_encounter()
	#--------------------------------------------------------
	# SOAP editor specific buttons
	#--------------------------------------------------------
	def _on_discard_editor_button_pressed(self, event):
		self._NB_soap_editors.close_current_editor()
		event.Skip()
	#--------------------------------------------------------
	def _on_new_editor_button_pressed(self, event):
		self._NB_soap_editors.add_editor(allow_same_problem = True)
		event.Skip()
	#--------------------------------------------------------
	def _on_clear_editor_button_pressed(self, event):
		self._NB_soap_editors.clear_current_editor()
		event.Skip()
	#--------------------------------------------------------
	def _on_save_note_button_pressed(self, event):
		self._NB_soap_editors.save_current_editor (
			emr = self.__pat.emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), ''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), '')
			]
		)
		event.Skip()
	#--------------------------------------------------------
	def _on_save_note_under_button_pressed(self, event):
		encounter = gmEncounterWidgets.select_encounters (
			parent = self,
			patient = self.__pat,
			single_selection = True
		)
		# cancelled or None selected:
		if encounter is None:
			return

		self._NB_soap_editors.save_current_editor (
			emr = self.__pat.emr,
			encounter = encounter['pk_encounter'],
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), ''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), '')
			]
		)
		event.Skip()
	#--------------------------------------------------------
	def _on_image_button_pressed(self, event):
		self._NB_soap_editors.add_visual_progress_note_to_current_problem()
		event.Skip()
	#--------------------------------------------------------
	# encounter specific buttons
	#--------------------------------------------------------
	def _on_save_encounter_button_pressed(self, event):
		self.save_encounter()
		event.Skip()
	#--------------------------------------------------------
	# other buttons
	#--------------------------------------------------------
	def _on_save_all_button_pressed(self, event):
		self.save_encounter()
		time.sleep(0.3)
		event.Skip()
		wx.SafeYield()

		wx.CallAfter(self._save_all_button_pressed_bottom_half)
		wx.SafeYield()
	#--------------------------------------------------------
	def _save_all_button_pressed_bottom_half(self):
		emr = self.__pat.emr
		saved = self._NB_soap_editors.save_all_editors (
			emr = emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), ''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), '')
			]
		)
		if not saved:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)

#============================================================
class cSoapNoteInputNotebook(wx.Notebook):
	"""A notebook holding panels with progress note editors.

	There can be one or several progress note editor panels
	for each episode being worked on. The editor class in
	each panel is configurable.

	There will always be one open editor.
	"""
	def __init__(self, *args, **kwargs):

		kwargs['style'] = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER

		wx.Notebook.__init__(self, *args, **kwargs)

		_log.debug('created wx.Notebook: %s with ID %s', self.__class__.__name__, self.Id)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def add_editor(self, problem=None, allow_same_problem=False):
		"""Add a progress note editor page.

		The way <allow_same_problem> is currently used in callers
		it only applies to unassociated episodes.
		"""
		# determine label
		if problem is None:
			label = _('new problem')
			problem_to_add = None
		else:
			# normalize problem type
			problem_to_add = gmProblem.cProblem.from_issue_or_episode(problem)
			if not isinstance(problem_to_add, gmProblem.cProblem):
				raise TypeError('cannot open progress note editor for [%s]' % problem)

			# FIXME: configure maximum length
			label = gmTools.shorten_text(text = problem_to_add['problem'],	max_length = 23)
		# new unassociated problem or dupes allowed
		if allow_same_problem:
			new_page = gmProgressNotesEAWidgets.cProgressNotesEAPnl(self, -1, problem = problem_to_add)
			result = self.AddPage (
				page = new_page,
				text = label,
				select = True
			)
			return result

		# real problem, no dupes allowed
		# - raise existing editor
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			if problem_to_add is None:
				if page.problem is None:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = 'statustext', msg = 'Raising existing editor.', beep = True)
					return True
				continue

			# editor is for unassociated new problem
			if page.problem is None:
				continue

			# editor is for episode
			if page.problem['type'] == 'episode':
				if page.problem['pk_episode'] == problem_to_add['pk_episode']:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = 'statustext', msg = 'Raising existing editor.', beep = True)
					return True
				continue

			# editor is for health issue
			if page.problem['type'] == 'issue':
				if page.problem['pk_health_issue'] == problem_to_add['pk_health_issue']:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = 'statustext', msg = 'Raising existing editor.', beep = True)
					return True
				continue

		# - or add new editor
		new_page = gmProgressNotesEAWidgets.cProgressNotesEAPnl(parent = self, problem = problem_to_add)
		result = self.AddPage (
			page = new_page,
			text = label,
			select = True
		)

		return result
	#--------------------------------------------------------
	def close_current_editor(self):

		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)

		if not page.empty:
			really_discard = gmGuiHelpers.gm_show_question (
				_('Are you sure you really want to\n'
				  'discard this progress note ?\n'
				),
				_('Discarding progress note')
			)
			if really_discard is False:
				return

		self.DeletePage(page_idx)

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()
	#--------------------------------------------------------
	def save_current_editor(self, emr=None, episode_name_candidates=None, encounter=None):
		page_idx = self.GetSelection()
		_log.debug('saving editor on current page (#%s)', page_idx)
		page = self.GetPage(page_idx)
		if not page.save(emr = emr, episode_name_candidates = episode_name_candidates, encounter = encounter):
			_log.debug('not saved, not deleting')
			return False

		_log.debug('deleting')
		self.DeletePage(page_idx)

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()
		return True
	#--------------------------------------------------------
	def warn_on_unsaved_soap(self):
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			if page.empty:
				continue

			gmGuiHelpers.gm_show_warning (
				_('There are unsaved progress notes !\n'),
				_('Unsaved progress notes')
			)
			return False

		return True
	#--------------------------------------------------------
	def save_all_editors(self, emr=None, episode_name_candidates=None):

		_log.debug('saving editors: %s', self.GetPageCount())

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()
			return True

		# first of all save the current editor such
		# as not to confuse the user by switching away
		# from the page she invoked [save all] from
		idx_of_current_page = self.GetSelection()
		_log.debug('saving editor on current page (#%s)', idx_of_current_page)
		all_closed = self.GetPage(idx_of_current_page).save(emr = emr, episode_name_candidates = episode_name_candidates)
		if all_closed:
			_log.debug('deleting')
			self.DeletePage(idx_of_current_page)
			idx_of_current_page = None
		else:
			_log.debug('not saved, not deleting')

		# now save remaining editors from right to left
		for page_idx in range((self.GetPageCount() - 1), -1, -1):
			# skip current ?
			if page_idx == idx_of_current_page:
				# we tried and failed, no need to retry
				continue
			_log.debug('saving editor on page %s of %s', page_idx, self.GetPageCount())
			try:
				self.ChangeSelection(page_idx)
				_log.debug('editor raised')
			except Exception:
				_log.exception('cannot raise editor')
			page = self.GetPage(page_idx)
			if page.save(emr = emr, episode_name_candidates = episode_name_candidates):
				_log.debug('saved, deleting')
				self.DeletePage(page_idx)
			else:
				_log.debug('not saved, not deleting')
				all_closed = False

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()

		return (all_closed is True)
	#--------------------------------------------------------
	def clear_current_editor(self):
		self.GetCurrentPage().clear()
	#--------------------------------------------------------
	def get_current_problem(self):
		return self.GetCurrentPage().problem
	#--------------------------------------------------------
	def refresh_current_editor(self):
		self.GetCurrentPage().refresh()
	#--------------------------------------------------------
	def add_visual_progress_note_to_current_problem(self):
		self.GetCurrentPage().add_visual_progress_note()

#============================================================
#============================================================
from Gnumed.wxGladeWidgets import wxgSimpleSoapPluginPnl

class cSimpleSoapPluginPnl(wxgSimpleSoapPluginPnl.wxgSimpleSoapPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	def __init__(self, *args, **kwargs):

		wxgSimpleSoapPluginPnl.wxgSimpleSoapPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__curr_pat = gmPerson.gmCurrentPatient()
		self.__problem = None
		self.__init_ui()
		self.__register_interests()
	#-----------------------------------------------------
	# internal API
	#-----------------------------------------------------
	def __init_ui(self):
		self._LCTRL_problems.set_columns(columns = [_('Problem list')])
		self._LCTRL_problems.activate_callback = self._on_problem_activated
		self._LCTRL_problems.item_tooltip_callback = self._on_get_problem_tooltip

		self._splitter_main.SetSashGravity(0.5)
		splitter_width = self._splitter_main.GetSize()[0]
		self._splitter_main.SetSashPosition(splitter_width // 2, True)

		self._TCTRL_soap.Disable()
		self._BTN_save_soap.Disable()
		self._BTN_clear_soap.Disable()
	#-----------------------------------------------------
	def __reset_ui(self):
		self._LCTRL_problems.set_string_items()
		self._TCTRL_soap_problem.SetValue(_('<above, double-click problem to start entering SOAP note>'))
		self._TCTRL_soap.SetValue('')
		self._CHBOX_filter_by_problem.SetLabel(_('&Filter by problem'))
		self._TCTRL_journal.SetValue('')

		self._TCTRL_soap.Disable()
		self._BTN_save_soap.Disable()
		self._BTN_clear_soap.Disable()
	#-----------------------------------------------------
	def __save_soap(self):
		if not self.__curr_pat.connected:
			return None

		if self.__problem is None:
			return None

		saved = self.__curr_pat.emr.add_clin_narrative (
			note = self._TCTRL_soap.GetValue().strip(),
			soap_cat = 'u',
			episode = self.__problem
		)

		if saved is None:
			return False

		self._TCTRL_soap.SetValue('')
		self.__refresh_journal()
		return True
	#-----------------------------------------------------
	def __perhaps_save_soap(self):
		if self._TCTRL_soap.GetValue().strip() == '':
			return True
		if self.__problem is None:
			# FIXME: this could potentially lose input
			self._TCTRL_soap.SetValue('')
			return None
		save_it = gmGuiHelpers.gm_show_question (
			title = _('Saving SOAP note'),
			question = _('Do you want to save the SOAP note ?')
		)
		if save_it:
			return self.__save_soap()
		return False
	#-----------------------------------------------------
	def __refresh_problem_list(self):
		self._LCTRL_problems.set_string_items()
		emr = self.__curr_pat.emr
		epis = emr.get_episodes(open_status = True)
		if len(epis) > 0:
			self._LCTRL_problems.set_string_items(items = [ '%s%s' % (
				e['description'],
				gmTools.coalesce(e['health_issue'], '', ' (%s)')
			) for e in epis ])
			self._LCTRL_problems.set_data(epis)
	#-----------------------------------------------------
	def __refresh_journal(self):
		self._TCTRL_journal.SetValue('')
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)

		if epi is not None:
			self._CHBOX_filter_by_problem.SetLabel(_('&Filter by problem %s%s%s') % (
				gmTools.u_left_double_angle_quote,
				epi['description'],
				gmTools.u_right_double_angle_quote
			))
			self._CHBOX_filter_by_problem.Refresh()

		if not self._CHBOX_filter_by_problem.IsChecked():
			self._TCTRL_journal.SetValue(self.__curr_pat.emr.format_summary())
			return

		if epi is None:
			return

		self._TCTRL_journal.SetValue(epi.format_as_journal())
	#-----------------------------------------------------
	# event handling
	#-----------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals."""
		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'clin.episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = 'clin.health_issue_mod_db', receiver = self._on_episode_issue_mod_db)

		# synchronous signals
		self.__curr_pat.register_before_switching_from_patient_callback(callback = self._before_switching_from_patient_callback)
		gmDispatcher.send(signal = 'register_pre_exit_callback', callback = self._pre_exit_callback)
	#-----------------------------------------------------
	def _before_switching_from_patient_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns True.
		"""
		if not self.__curr_pat.connected:
			return True
		self.__perhaps_save_soap()
		self.__problem = None
		return True
	#-----------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to be shut down.

		Shutdown will not proceed before this returns.
		"""
		if not self.__curr_pat.connected:
			return
		if not self.__save_soap():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save SimpleNotes SOAP note.'), beep = True)
		return
	#-----------------------------------------------------
	def _on_pre_patient_unselection(self):
		self.__reset_ui()
	#-----------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#-----------------------------------------------------
	def _on_episode_issue_mod_db(self):
		self._schedule_data_reget()
	#-----------------------------------------------------
	def _on_problem_activated(self, event):
		self.__perhaps_save_soap()
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)
		self._TCTRL_soap_problem.SetValue(_('Progress note: %s%s') % (
			epi['description'],
			gmTools.coalesce(epi['health_issue'], '', ' (%s)')
		))
		self.__problem = epi
		self._TCTRL_soap.SetValue('')

		self._TCTRL_soap.Enable()
		self._BTN_save_soap.Enable()
		self._BTN_clear_soap.Enable()
	#-----------------------------------------------------
	def _on_get_problem_tooltip(self, episode):
		return episode.format (
			patient = self.__curr_pat,
			with_summary = False,
			with_codes = True,
			with_encounters = False,
			with_documents = False,
			with_hospital_stays = False,
			with_procedures = False,
			with_family_history = False,
			with_tests = False,
			with_vaccinations = False,
			with_health_issue = True
		)
	#-----------------------------------------------------
	def _on_list_item_selected(self, event):
		event.Skip()
		self.__refresh_journal()
	#-----------------------------------------------------
	def _on_filter_by_problem_checked(self, event):
		event.Skip()
		self.__refresh_journal()
	#-----------------------------------------------------
	def _on_add_problem_button_pressed(self, event):
		event.Skip()
		epi_name = wx.GetTextFromUser (
			_('Please enter a name for the new problem:'),
			caption = _('Adding a problem'),
			parent = self
		).strip()
		if epi_name == '':
			return
		self.__curr_pat.emr.add_episode (
			episode_name = epi_name,
			pk_health_issue = None,
			is_open = True
		)
	#-----------------------------------------------------
	def _on_edit_problem_button_pressed(self, event):
		event.Skip()
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)
		if epi is None:
			return
		gmEMRStructWidgets.edit_episode(parent = self, episode = epi)
	#-----------------------------------------------------
	def _on_delete_problem_button_pressed(self, event):
		event.Skip()
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)
		if epi is None:
			return
		if not gmEpisode.delete_episode(episode = epi):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete problem. There is still clinical data recorded for it.'))
	#-----------------------------------------------------
	def _on_save_soap_button_pressed(self, event):
		event.Skip()
		self.__save_soap()
	#-----------------------------------------------------
	def _on_clear_soap_button_pressed(self, event):
		event.Skip()
		self._TCTRL_soap.SetValue('')
	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		self.__refresh_journal()
		self._TCTRL_soap.SetValue('')
		return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#----------------------------------------
	def test_cSoapPluginPnl():
		patient = gmPersonSearch.ask_for_patient()
		if patient is None:
			print("No patient. Exiting gracefully...")
			return
		set_active_patient(patient=patient)

#		application = wx.PyWidgetTester(size=(800,500))
#		soap_input = cSoapPluginPnl(application.frame, -1)
#		application.frame.Show(True)
#		soap_input._schedule_data_reget()
#		application.MainLoop()
	#----------------------------------------
	#test_cSoapPluginPnl()
