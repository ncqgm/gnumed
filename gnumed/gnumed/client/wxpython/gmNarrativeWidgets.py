"""GNUmed narrative handling widgets."""
#================================================================
__version__ = "$Revision: 1.46 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, os, os.path, time, re as regex


import wx
import wx.lib.expando as wxexpando


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmDispatcher, gmTools, gmDateTime
from Gnumed.pycommon import gmShellAPI, gmPG2, gmCfg
from Gnumed.business import gmPerson, gmEMRStructItems, gmClinNarrative, gmSurgery
from Gnumed.wxpython import gmListWidgets, gmEMRStructWidgets, gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmPatSearchWidgets
from Gnumed.wxpython import gmCfgWidgets, gmDocumentWidgets
from Gnumed.exporters import gmPatientExporter


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#============================================================
# narrative related widgets/functions
#------------------------------------------------------------
def move_progress_notes_to_another_encounter(parent=None, encounters=None, episodes=None, patient=None, move_all=False):

	# sanity checks
	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot move progress notes. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	emr = patient.get_emr()

	if encounters is None:
		encs = emr.get_encounters(episodes = episodes)
		encounters = gmEMRStructWidgets.select_encounters (
			parent = parent,
			patient = patient,
			single_selection = False,
			encounters = encs
		)

	notes = emr.get_clin_narrative (
		encounters = encounters,
		episodes = episodes
	)

	# which narrative
	if move_all:
		selected_narr = notes
	else:
		selected_narr = gmListWidgets.get_choices_from_list (
			parent = parent,
			caption = _('Moving progress notes between encounters ...'),
			single_selection = False,
			can_return_empty = True,
			data = notes,
			msg = _('\n Select the progress notes to move from the list !\n\n'),
			columns = [_('when'), _('who'), _('type'), _('entry')],
			choices = [
				[	narr['date'].strftime('%x %H:%M'),
					narr['provider'],
					gmClinNarrative.soap_cat2l10n[narr['soap_cat']],
					narr['narrative'].replace('\n', '/').replace('\r', '/')
				] for narr in notes
			]
		)

	if not selected_narr:
		return True

	# which encounter to move to
	enc2move2 = gmEMRStructWidgets.select_encounters (
		parent = parent,
		patient = patient,
		single_selection = True
	)

	if not enc2move2:
		return True

	for narr in selected_narr:
		narr['pk_encounter'] = enc2move2['pk_encounter']
		narr.save()

	return True
#------------------------------------------------------------
def manage_progress_notes(parent=None, encounters=None, episodes=None, patient=None):

	# sanity checks
	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit progress notes. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	emr = patient.get_emr()
	#--------------------------
	def delete(item):
		if item is None:
			return False
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent,
			-1,
			caption = _('Deleting progress note'),
			question = _(
				'Are you positively sure you want to delete this\n'
				'progress note from the medical record ?\n'
				'\n'
				'Note that even if you chose to delete the entry it will\n'
				'still be (invisibly) kept in the audit trail to protect\n'
				'you from litigation because physical deletion is known\n'
				'to be unlawful in some jurisdictions.\n'
			),
			button_defs = (
				{'label': _('Delete'), 'tooltip': _('Yes, delete the progress note.'), 'default': False},
				{'label': _('Cancel'), 'tooltip': _('No, do NOT delete the progress note.'), 'default': True}
			)
		)
		decision = dlg.ShowModal()

		if decision != wx.ID_YES:
			return False

		gmClinNarrative.delete_clin_narrative(narrative = item['pk_narrative'])
		return True
	#--------------------------
	def edit(item):
		if item is None:
			return False

		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			parent,
			-1,
			title = _('Editing progress note'),
			msg = _('This is the original progress note:'),
			data = item.format(left_margin = u' ', fancy = True),
			text = item['narrative']
		)
		decision = dlg.ShowModal()

		if decision != wx.ID_SAVE:
			return False

		val = dlg.value
		dlg.Destroy()
		if val.strip() == u'':
			return False

		item['narrative'] = val
		item.save_payload()

		return True
	#--------------------------
	def refresh(lctrl):
		notes = emr.get_clin_narrative (
			encounters = encounters,
			episodes = episodes,
			providers = [ gmPerson.gmCurrentProvider()['short_alias'] ]
		)
		lctrl.set_string_items(items = [
			[	narr['date'].strftime('%x %H:%M'),
				gmClinNarrative.soap_cat2l10n[narr['soap_cat']],
				narr['narrative'].replace('\n', '/').replace('\r', '/')
			] for narr in notes
		])
		lctrl.set_data(data = notes)
	#--------------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Managing progress notes'),
		msg = _(
			'\n'
			' This list shows the progress notes by %s.\n'
			'\n'
		) % gmPerson.gmCurrentProvider()['short_alias'],
		columns = [_('when'), _('type'), _('entry')],
		single_selection = True,
		can_return_empty = False,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		ignore_OK_button = True
	)
#------------------------------------------------------------
def search_narrative_across_emrs(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	searcher = wx.TextEntryDialog (
		parent = parent,
		message = _('Enter (regex) term to search for across all EMRs:'),
		caption = _('Text search across all EMRs'),
		style = wx.OK | wx.CANCEL | wx.CENTRE
	)
	result = searcher.ShowModal()

	if result != wx.ID_OK:
		return

	wx.BeginBusyCursor()
	term = searcher.GetValue()
	searcher.Destroy()
	results = gmClinNarrative.search_text_across_emrs(search_term = term)
	wx.EndBusyCursor()

	if len(results) == 0:
		gmGuiHelpers.gm_show_info (
			_(
			'Nothing found for search term:\n'
			' "%s"'
			) % term,
			_('Search results')
		)
		return

	items = [ [gmPerson.cIdentity(aPK_obj = r['pk_patient'])['description_gender'], r['narrative'], r['src_table']] for r in results ]

	selected_patient = gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Search results for %s') % term,
		choices = items,
		columns = [_('Patient'), _('Match'), _('Match location')],
		data = [ r['pk_patient'] for r in results ],
		single_selection = True,
		can_return_empty = False
	)

	if selected_patient is None:
		return

	wx.CallAfter(gmPatSearchWidgets.set_active_patient, patient = gmPerson.cIdentity(aPK_obj = selected_patient))
#------------------------------------------------------------
def search_narrative_in_emr(parent=None, patient=None):

	# sanity checks
	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot search EMR. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	searcher = wx.TextEntryDialog (
		parent = parent,
		message = _('Enter search term:'),
		caption = _('Text search of entire EMR of active patient'),
		style = wx.OK | wx.CANCEL | wx.CENTRE
	)
	result = searcher.ShowModal()

	if result != wx.ID_OK:
		searcher.Destroy()
		return False

	wx.BeginBusyCursor()
	val = searcher.GetValue()
	searcher.Destroy()
	emr = patient.get_emr()
	rows = emr.search_narrative_simple(val)
	wx.EndBusyCursor()

	if len(rows) == 0:
		gmGuiHelpers.gm_show_info (
			_(
			'Nothing found for search term:\n'
			' "%s"'
			) % val,
			_('Search results')
		)
		return True

	txt = u''
	for row in rows:
		txt += u'%s: %s\n' % (
			row['soap_cat'],
			row['narrative']
		)

		txt += u' %s: %s - %s %s\n' % (
			_('Encounter'),
			row['encounter_started'].strftime('%x %H:%M'),
			row['encounter_ended'].strftime('%H:%M'),
			row['encounter_type']
		)
		txt += u' %s: %s\n' % (
			_('Episode'),
			row['episode']
		)
		txt += u' %s: %s\n\n' % (
			_('Health issue'),
			row['health_issue']
		)

	msg = _(
		'Search term was: "%s"\n'
		'\n'
		'Search results:\n\n'
		'%s\n'
	) % (val, txt)

	dlg = wx.MessageDialog (
		parent = parent,
		message = msg,
		caption = _('Search results for %s') % val,
		style = wx.OK | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()

	return True
#------------------------------------------------------------
def export_narrative_for_medistar_import(parent=None, soap_cats=u'soap', encounter=None):

	# sanity checks
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR for Medistar. No active patient.'))
		return False

	if encounter is None:
		encounter = pat.get_emr().active_encounter

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

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
		pat.get_formatted_dob(format = '%Y-%m-%d')
	)
	dlg = wx.FileDialog (
		parent = parent,
		message = _("Save EMR extract for MEDISTAR import as..."),
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

	wx.BeginBusyCursor()
	_log.debug('exporting encounter for medistar import to [%s]', fname)
	exporter = gmPatientExporter.cMedistarSOAPExporter()
	successful, fname = exporter.export_to_file (
		filename = fname,
		encounter = encounter,
		soap_cats = u'soap',
		export_to_import_file = True
	)
	if not successful:
		gmGuiHelpers.gm_show_error (
			_('Error exporting progress notes for MEDISTAR import.'),
			_('MEDISTAR progress notes export')
		)
		wx.EndBusyCursor()
		return False

	gmDispatcher.send(signal = 'statustext', msg = _('Successfully exported progress notes into file [%s] for Medistar import.') % fname, beep=False)

	wx.EndBusyCursor()
	return True
#------------------------------------------------------------
def select_narrative_from_episodes(parent=None, soap_cats=None):
	"""soap_cats needs to be a list"""

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	selected_soap = {}
	selected_issue_pks = []
	selected_episode_pks = []
	selected_narrative_pks = []

	while 1:
		# 1) select health issues to select episodes from
		all_issues = emr.get_health_issues()
		all_issues.insert(0, gmEMRStructItems.get_dummy_health_issue())
		dlg = gmEMRStructWidgets.cIssueListSelectorDlg (
			parent = parent,
			id = -1,
			issues = all_issues,
			msg = _('\n In the list below mark the health issues you want to report on.\n')
		)
		selection_idxs = []
		for idx in range(len(all_issues)):
			if all_issues[idx]['pk_health_issue'] in selected_issue_pks:
				selection_idxs.append(idx)
		if len(selection_idxs) != 0:
			dlg.set_selections(selections = selection_idxs)
		btn_pressed = dlg.ShowModal()
		selected_issues = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			return selected_soap.values()

		selected_issue_pks = [ i['pk_health_issue'] for i in selected_issues ]

		while 1:
			# 2) select episodes to select items from
			all_epis = emr.get_episodes(issues = selected_issue_pks)

			if len(all_epis) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No episodes recorded for the health issues selected.'))
				break

			dlg = gmEMRStructWidgets.cEpisodeListSelectorDlg (
				parent = parent,
				id = -1,
				episodes = all_epis,
				msg = _(
					'\n These are the episodes known for the health issues just selected.\n\n'
					' Now, mark the the episodes you want to report on.\n'
				)
			)
			selection_idxs = []
			for idx in range(len(all_epis)):
				if all_epis[idx]['pk_episode'] in selected_episode_pks:
					selection_idxs.append(idx)
			if len(selection_idxs) != 0:
				dlg.set_selections(selections = selection_idxs)
			btn_pressed = dlg.ShowModal()
			selected_epis = dlg.get_selected_item_data()
			dlg.Destroy()

			if btn_pressed == wx.ID_CANCEL:
				break

			selected_episode_pks = [ i['pk_episode'] for i in selected_epis ]

			# 3) select narrative corresponding to the above constraints
			all_narr = emr.get_clin_narrative(episodes = selected_episode_pks, soap_cats = soap_cats)

			if len(all_narr) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for selected episodes.'))
				continue

			dlg = cNarrativeListSelectorDlg (
				parent = parent,
				id = -1,
				narrative = all_narr,
				msg = _(
					'\n This is the narrative (type %s) for the chosen episodes.\n\n'
					' Now, mark the entries you want to include in your report.\n'
				) % u'/'.join([ gmClinNarrative.soap_cat2l10n[cat] for cat in gmTools.coalesce(soap_cats, list(u'soap')) ])
			)
			selection_idxs = []
			for idx in range(len(all_narr)):
				if all_narr[idx]['pk_narrative'] in selected_narrative_pks:
					selection_idxs.append(idx)
			if len(selection_idxs) != 0:
				dlg.set_selections(selections = selection_idxs)
			btn_pressed = dlg.ShowModal()
			selected_narr = dlg.get_selected_item_data()
			dlg.Destroy()

			if btn_pressed == wx.ID_CANCEL:
				continue

			selected_narrative_pks = [ i['pk_narrative'] for i in selected_narr ]
			for narr in selected_narr:
				selected_soap[narr['pk_narrative']] = narr
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
			items = [ [narr['date'].strftime('%x %H:%M'), narr['provider'], gmClinNarrative.soap_cat2l10n[narr['soap_cat']], narr['narrative'].replace('\n', '/').replace('\r', '/')] for narr in narrative ]
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

		self.LBL_source_episode.SetLabel(u'%s%s' % (self.source_episode['description'], gmTools.coalesce(self.source_episode['health_issue'], u'', u' (%s)')))
		self.LBL_encounter.SetLabel('%s: %s %s - %s' % (
			self.encounter['started'].strftime('%x').decode(gmI18N.get_encoding()),
			self.encounter['l10n_type'],
			self.encounter['started'].strftime('%H:%M'),
			self.encounter['last_affirmed'].strftime('%H:%M')
		))
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		narr = emr.get_clin_narrative(episodes=[self.source_episode['pk_episode']], encounters=[self.encounter['pk_encounter']])
		if len(narr) == 0:
			narr = [{'narrative': _('There is no narrative for this episode in this encounter.')}]
		self.LBL_narrative.SetLabel(u'\n'.join([n['narrative'] for n in narr]))

	#------------------------------------------------------------
	def _on_move_button_pressed(self, event):

		target_episode = self._PRW_episode_selector.GetData(can_create = False)

		if target_episode is None:
			gmDispatcher.send(signal='statustext', msg=_('Must select episode to move narrative to first.'))
			# FIXME: set to pink
			self._PRW_episode_selector.SetFocus()
			return False

		target_episode = gmEMRStructItems.cEpisode(aPK_obj=target_episode)

		self.encounter.transfer_clinical_data (
			source_episode = self.source_episode,
			target_episode = target_episode
		)

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
#============================================================
from Gnumed.wxGladeWidgets import wxgSoapPluginPnl

class cSoapPluginPnl(wxgSoapPluginPnl.wxgSoapPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A panel for in-context editing of progress notes.

	Expects to be used as a notebook page.

	Left hand side:
	- problem list (health issues and active episodes)
	- hints area

	Right hand side:
	- previous notes
	- notebook with progress note editors
	- encounter details fields
	- visual soap area

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
	# public API
	#--------------------------------------------------------
	def save_encounter(self):

		if not self.__encounter_valid_for_save():
			return False

		emr = self.__pat.get_emr()
		enc = emr.active_encounter

		enc['pk_type'] = self._PRW_encounter_type.GetData()
		enc['started'] = self._PRW_encounter_start.GetData().get_pydt()
		enc['last_affirmed'] = self._PRW_encounter_end.GetData().get_pydt()
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

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_active_problems.set_columns([_('Last'), _('Problem'), _('Health issue')])
		self._LCTRL_active_problems.set_string_items()

		self._splitter_main.SetSashGravity(0.5)
		self._splitter_left.SetSashGravity(0.5)
		self._splitter_right.SetSashGravity(1.0)
		self._splitter_soap.SetSashGravity(0.75)

		splitter_size = self._splitter_main.GetSizeTuple()[0]
		self._splitter_main.SetSashPosition(splitter_size * 3 / 10, True)

		splitter_size = self._splitter_left.GetSizeTuple()[1]
		self._splitter_left.SetSashPosition(splitter_size * 6 / 20, True)

		splitter_size = self._splitter_right.GetSizeTuple()[1]
		self._splitter_right.SetSashPosition(splitter_size * 15 / 20, True)

		splitter_size = self._splitter_soap.GetSizeTuple()[0]
		self._splitter_soap.SetSashPosition(splitter_size * 3 / 4, True)

		self._NB_soap_editors.DeleteAllPages()
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self._LCTRL_active_problems.set_string_items()

		self._TCTRL_recent_notes.SetValue(u'')

		self._PRW_encounter_type.SetText(suppress_smarts = True)
		self._PRW_encounter_start.SetText(suppress_smarts = True)
		self._PRW_encounter_end.SetText(suppress_smarts = True)
		self._TCTRL_rfe.SetValue(u'')
		self._TCTRL_aoe.SetValue(u'')

		self._NB_soap_editors.DeleteAllPages()
		self._NB_soap_editors.add_editor()

		self._PNL_visual_soap.clear()

		self._lbl_hints.SetLabel(u'')
	#--------------------------------------------------------
	def __refresh_visual_soaps(self):
		self._PNL_visual_soap.refresh()
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""Update health problems list.
		"""

		self._LCTRL_active_problems.set_string_items()

		emr = self.__pat.get_emr()
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
				issue = emr.problem2issue(problem)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
				if last_encounter is None:
					last = issue['modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')

				list_items.append([last, problem['problem'], gmTools.u_left_arrow])

			elif problem['type'] == 'episode':
				epi = emr.problem2episode(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')

				list_items.append ([
					last,
					problem['problem'],
					gmTools.coalesce(initial = epi['health_issue'], instead = gmTools.u_diameter)
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
			self._SZR_problem_list_staticbox.SetLabel(_('%s (active+potential) problems') % len(list_items))
		else:
			self._SZR_problem_list_staticbox.SetLabel(_('%s active problems') % len(list_items))

		return True
	#--------------------------------------------------------
	def __refresh_recent_notes(self, problem=None):
		"""This refreshes the recent-notes part."""

		if problem is None:
			soap = u''
			caption = u'<?>'

		elif problem['type'] == u'issue':
			emr = self.__pat.get_emr()
			soap = u''
			caption = problem['problem'][:35]

			prev_enc = emr.get_last_but_one_encounter(issue_id = problem['pk_health_issue'])
			if prev_enc is not None:
				soap += prev_enc.format (
					with_soap = True,
					with_docs = False,
					with_tests = False,
					patient = self.__pat,
					issues = [ problem['pk_health_issue'] ],
					fancy_header = False
				)

			tmp = emr.active_encounter.format_soap (
				soap_cats = 'soap',
				emr = emr,
				issues = [ problem['pk_health_issue'] ],
			)
			if len(tmp) > 0:
				soap += _('Current encounter:') + u'\n'
				soap += u'\n'.join(tmp) + u'\n'

		elif problem['type'] == u'episode':
			emr = self.__pat.get_emr()
			soap = u''
			caption = problem['problem'][:35]

			prev_enc = emr.get_last_but_one_encounter(episode_id = problem['pk_episode'])
			if prev_enc is None:
				if problem['pk_health_issue'] is not None:
					prev_enc = emr.get_last_but_one_encounter(episode_id = problem['pk_health_issue'])
					if prev_enc is not None:
						soap += prev_enc.format (
							with_soap = True,
							with_docs = False,
							with_tests = False,
							patient = self.__pat,
							issues = [ problem['pk_health_issue'] ],
							fancy_header = False
						)
			else:
				soap += prev_enc.format (
					episodes = [ problem['pk_episode'] ],
					with_soap = True,
					with_docs = False,
					with_tests = False,
					patient = self.__pat,
					fancy_header = False
				)

			tmp = emr.active_encounter.format_soap (
				soap_cats = 'soap',
				emr = emr,
				issues = [ problem['pk_health_issue'] ],
			)
			if len(tmp) > 0:
				soap += _('Current encounter:') + u'\n'
				soap += u'\n'.join(tmp) + u'\n'

		else:
			soap = u''
			caption = u'<?>'

		self._TCTRL_recent_notes.SetValue(soap)
		self._TCTRL_recent_notes.ShowPosition(self._TCTRL_recent_notes.GetLastPosition())
		self._SZR_recent_notes_staticbox.SetLabel(_('Most recent notes on %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			caption,
			gmTools.u_right_double_angle_quote
		))

		self._TCTRL_recent_notes.Refresh()

		return True
	#--------------------------------------------------------
	def __refresh_encounter(self):
		"""Update encounter fields.
		"""
		emr = self.__pat.get_emr()
		enc = emr.active_encounter
		self._PRW_encounter_type.SetText(value = enc['l10n_type'], data = enc['pk_type'])

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = enc['started'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_encounter_start.SetText(fts.format_accurately(), data=fts)

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = enc['last_affirmed'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_encounter_end.SetText(fts.format_accurately(), data=fts)

		self._TCTRL_rfe.SetValue(gmTools.coalesce(enc['reason_for_encounter'], u''))
		self._TCTRL_aoe.SetValue(gmTools.coalesce(enc['assessment_of_encounter'], u''))

		self._PRW_encounter_type.Refresh()
		self._PRW_encounter_start.Refresh()
		self._PRW_encounter_end.Refresh()
		self._TCTRL_rfe.Refresh()
		self._TCTRL_aoe.Refresh()
	#--------------------------------------------------------
	def __encounter_modified(self):
		"""Assumes that the field data is valid."""

		emr = self.__pat.get_emr()
		enc = emr.active_encounter

		data = {
			'pk_type': self._PRW_encounter_type.GetData(),
			'reason_for_encounter': gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u''),
			'assessment_of_encounter': gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
			'pk_location': enc['pk_location']
		}

		if self._PRW_encounter_start.GetData() is None:
			data['started'] = None
		else:
			data['started'] = self._PRW_encounter_start.GetData().get_pydt()

		if self._PRW_encounter_end.GetData() is None:
			data['last_affirmed'] = None
		else:
			data['last_affirmed'] = self._PRW_encounter_end.GetData().get_pydt()

		return enc.same_payload(another_object = data)
	#--------------------------------------------------------
	def __encounter_valid_for_save(self):

		found_error = False

		if self._PRW_encounter_type.GetData() is None:
			found_error = True
			msg = _('Cannot save encounter: missing type.')

		if self._PRW_encounter_start.GetData() is None:
			found_error = True
			msg = _('Cannot save encounter: missing start time.')

		if self._PRW_encounter_end.GetData() is None:
			found_error = True
			msg = _('Cannot save encounter: missing end time.')

		if found_error:
			gmDispatcher.send(signal = 'statustext', msg = msg, beep = True)
			return False

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals."""
		# client internal signals
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'health_issue_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_doc_mod_db)
		gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)
		gmDispatcher.connect(signal = u'current_encounter_switched', receiver = self._on_current_encounter_switched)

		# synchronous signals
		self.__pat.register_pre_selection_callback(callback = self._pre_selection_callback)
		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)
	#--------------------------------------------------------
	def _pre_selection_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns True.
		"""
		# don't worry about the encounter here - it will be offered
		# for editing higher up if anything was saved to the EMR
		if not self.__pat.connected:
			return True
		return self._NB_soap_editors.warn_on_unsaved_soap()
	#--------------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to be shut down.

		Shutdown will not proceed before this returns.
		"""
		if not self.__pat.connected:
			return True

#		if self.__encounter_modified():
#			do_save_enc = gmGuiHelpers.gm_show_question (
#				aMessage = _(
#					'You have modified the details\n'
#					'of the current encounter.\n'
#					'\n'
#					'Do you want to save those changes ?'
#				),
#				aTitle = _('Starting new encounter')
#			)
#			if do_save_enc:
#				if not self.save_encounter():
#					gmDispatcher.send(signal = u'statustext', msg = _('Error saving current encounter.'), beep = True)

		emr = self.__pat.get_emr()
		if not self._NB_soap_editors.save_all_editors(emr = emr, rfe = self._TCTRL_rfe.GetValue().strip(), aoe = self._TCTRL_aoe.GetValue().strip()):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
		return True
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		self.__reset_ui_content()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_doc_mod_db(self):
		wx.CallAfter(self.__refresh_visual_soaps)
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_current_encounter_modified(self):
		wx.CallAfter(self.__refresh_encounter)
	#--------------------------------------------------------
	def _on_current_encounter_switched(self):
		wx.CallAfter(self.__on_current_encounter_switched)
	#--------------------------------------------------------
	def __on_current_encounter_switched(self):
		self.__refresh_encounter()
		self.__refresh_visual_soaps()
	#--------------------------------------------------------
	def _on_problem_focused(self, event):
		"""Show related note at the bottom."""
		pass
	#--------------------------------------------------------
	def _on_problem_selected(self, event):
		"""Show related note at the bottom."""
		emr = self.__pat.get_emr()
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

		dbcfg = gmCfg.cCfgSQL()
		allow_duplicate_editors = bool(dbcfg.get2 (
			option = u'horstspace.soap_editor.allow_same_episode_multiple_times',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user',
			default = False
		))
		if self._NB_soap_editors.add_editor(problem = problem, allow_same_problem = allow_duplicate_editors):
			return True

		gmGuiHelpers.gm_show_error (
			aMessage = _(
				'Cannot open progress note editor for\n\n'
				'[%s].\n\n'
			) % problem['problem'],
			aTitle = _('opening progress note editor')
		)
		event.Skip()
		return False
	#--------------------------------------------------------
	def _on_discard_editor_button_pressed(self, event):
		self._NB_soap_editors.close_current_editor()
		event.Skip()
	#--------------------------------------------------------
	def _on_new_editor_button_pressed(self, event):
		self._NB_soap_editors.add_editor()
		event.Skip()
	#--------------------------------------------------------
	def _on_clear_editor_button_pressed(self, event):
		self._NB_soap_editors.clear_current_editor()
		event.Skip()
	#--------------------------------------------------------
	def _on_save_all_button_pressed(self, event):
		self.save_encounter()
		emr = self.__pat.get_emr()
		if not self._NB_soap_editors.save_all_editors(emr = emr, rfe = self._TCTRL_rfe.GetValue().strip(), aoe = self._TCTRL_aoe.GetValue().strip()):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
		event.Skip()
	#--------------------------------------------------------
	def _on_save_encounter_button_pressed(self, event):
		self.save_encounter()
		event.Skip()
	#--------------------------------------------------------
	def _on_save_note_button_pressed(self, event):
		emr = self.__pat.get_emr()
		self._NB_soap_editors.save_current_editor (
			emr = emr,
			rfe = self._TCTRL_rfe.GetValue().strip(),
			aoe = self._TCTRL_aoe.GetValue().strip()
		)
		event.Skip()
	#--------------------------------------------------------
	def _on_new_encounter_button_pressed(self, event):

		if self.__encounter_modified():
			do_save_enc = gmGuiHelpers.gm_show_question (
				aMessage = _(
					'You have modified the details\n'
					'of the current encounter.\n'
					'\n'
					'Do you want to save those changes ?'
				),
				aTitle = _('Starting new encounter')
			)
			if do_save_enc:
				if not self.save_encounter():
					gmDispatcher.send(signal = u'statustext', msg = _('Error saving current encounter.'), beep = True)
					return False

		emr = self.__pat.get_emr()
		gmDispatcher.send(signal = u'statustext', msg = _('Started new encounter for active patient.'), beep = True)

		event.Skip()

		wx.CallAfter(gmEMRStructWidgets.start_new_encounter, emr = emr)
	#--------------------------------------------------------
	def _on_show_closed_episodes_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	def _on_irrelevant_issues_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		self.__refresh_encounter()
		self.__refresh_visual_soaps()
		return True
#============================================================
class cSoapNoteInputNotebook(wx.Notebook):
	"""A notebook holding panels with progress note editors.

	There can be one or several progress note editor panel
	for each episode being worked on. The editor class in
	each panel is configurable.

	There will always be one open editor.
	"""
	def __init__(self, *args, **kwargs):

		kwargs['style'] = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER

		wx.Notebook.__init__(self, *args, **kwargs)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def add_editor(self, problem=None, allow_same_problem=False):
		"""Add a progress note editor page.

		The way <allow_same_problem> is currently used in callers
		it only applies to unassociated episodes.
		"""
		problem_to_add = problem

		# determine label
		if problem_to_add is None:
			label = _('new problem')
		else:
			# normalize problem type
			if isinstance(problem_to_add, gmEMRStructItems.cEpisode):
				problem_to_add = gmEMRStructItems.episode2problem(episode = problem_to_add)

			elif isinstance(problem_to_add, gmEMRStructItems.cHealthIssue):
				problem_to_add = gmEMRStructItems.health_issue2problem(episode = problem_to_add)

			if not isinstance(problem_to_add, gmEMRStructItems.cProblem):
				raise TypeError('cannot open progress note editor for [%s]' % problem_to_add)

			label = problem_to_add['problem']
			# FIXME: configure maximum length
			if len(label) > 23:
				label = label[:21] + gmTools.u_ellipsis

		# new unassociated problem or dupes allowed
		if (problem_to_add is None) or allow_same_problem:
			new_page = cSoapNoteExpandoEditAreaPnl(parent = self, id = -1, problem = problem_to_add)
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

			# editor is for unassociated new problem
			if page.problem is None:
				continue

			# editor is for episode
			if page.problem['type'] == 'episode':
				if page.problem['pk_episode'] == problem_to_add['pk_episode']:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = u'statustext', msg = u'Raising existing editor.', beep = True)
					return True
				continue

			# editor is for health issue
			if page.problem['type'] == 'issue':
				if page.problem['pk_health_issue'] == problem_to_add['pk_health_issue']:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = u'statustext', msg = u'Raising existing editor.', beep = True)
					return True
				continue

		# - or add new editor
		new_page = cSoapNoteExpandoEditAreaPnl(parent = self, id = -1, problem = problem_to_add)
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
	def save_current_editor(self, emr=None, rfe=None, aoe=None):

		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)

		if not page.save(emr = emr, rfe = rfe, aoe = aoe):
			return

		self.DeletePage(page_idx)

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()
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
	def save_all_editors(self, emr=None, rfe=None, aoe=None):

		all_closed = True
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			if page.save(emr = emr, rfe = rfe, aoe = aoe):
				self.DeletePage(page_idx)
			else:
				all_closed = False

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()

		return (all_closed is True)
	#--------------------------------------------------------
	def clear_current_editor(self):
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		page.clear()
	#--------------------------------------------------------
	def get_current_problem(self):
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		return page.problem
#============================================================
from Gnumed.wxGladeWidgets import wxgSoapNoteExpandoEditAreaPnl

class cSoapNoteExpandoEditAreaPnl(wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl):

	def __init__(self, *args, **kwargs):

		try:
			self.problem = kwargs['problem']
			del kwargs['problem']
		except KeyError:
			self.problem = None

		wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl.__init__(self, *args, **kwargs)

		self.fields = [
			self._TCTRL_Soap,
			self._TCTRL_sOap,
			self._TCTRL_soAp,
			self._TCTRL_soaP
		]

		self.__register_interests()
	#--------------------------------------------------------
	def clear(self):
		for field in self.fields:
			field.SetValue(u'')
	#--------------------------------------------------------
	def save(self, emr=None, rfe=None, aoe=None):

		if self.empty:
			return True

		# new unassociated episode
		if (self.problem is None) or (self.problem['type'] == 'issue'):

			epi_name = gmTools.coalesce (
				aoe,
				gmTools.coalesce (
					rfe,
					u''
				)
			).strip().replace('\r', '//').replace('\n', '//')

			dlg = wx.TextEntryDialog (
				parent = self,
				message = _('Enter a short working name for this new problem:'),
				caption = _('Creating a problem (episode) to save the notelet under ...'),
				defaultValue = epi_name,
				style = wx.OK | wx.CANCEL | wx.CENTRE
			)
			decision = dlg.ShowModal()
			if decision != wx.ID_OK:
				return False

			epi_name = dlg.GetValue().strip()
			if epi_name == u'':
				gmGuiHelpers.gm_show_error(_('Cannot save a new problem without a name.'), _('saving progress note'))
				return False

			# create episode
			new_episode = emr.add_episode(episode_name = epi_name[:45], pk_health_issue = None, is_open = True)

			if self.problem is not None:
				issue = emr.problem2issue(self.problem)
				if not gmEMRStructWidgets.move_episode_to_issue(episode = new_episode, target_issue = issue, save_to_backend = True):
					gmGuiHelpers.gm_show_warning (
						_(
							'The new episode:\n'
							'\n'
							' "%s"\n'
							'\n'
							'will remain unassociated despite the editor\n'
							'having been invoked from the health issue:\n'
							'\n'
							' "%s"'
						) % (
							new_episode['description'],
							issue['description']
						),
						_('saving progress note')
					)

			epi_id = new_episode['pk_episode']
		else:
			epi_id = self.problem['pk_episode']

		emr.add_notes(notes = self.soap, episode = epi_id)

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		for field in self.fields:
			wxexpando.EVT_ETC_LAYOUT_NEEDED(field, field.GetId(), self._on_expando_needs_layout)
	#--------------------------------------------------------
	def _on_expando_needs_layout(self, evt):
		# need to tell ourselves to re-Layout to refresh scroll bars

		# provoke adding scrollbar if needed
		self.Fit()

		if self.HasScrollbar(wx.VERTICAL):
			# scroll panel to show cursor
			expando = self.FindWindowById(evt.GetId())
			y_expando = expando.GetPositionTuple()[1]
			h_expando = expando.GetSizeTuple()[1]
			line_cursor = expando.PositionToXY(expando.GetInsertionPoint())[1] + 1
			y_cursor = int(round((float(line_cursor) / expando.NumberOfLines) * h_expando))
			y_desired_visible = y_expando + y_cursor

			y_view = self.ViewStart[1]
			h_view = self.GetClientSizeTuple()[1]

#			print "expando:", y_expando, "->", h_expando, ", lines:", expando.NumberOfLines
#			print "cursor :", y_cursor, "at line", line_cursor, ", insertion point:", expando.GetInsertionPoint()
#			print "wanted :", y_desired_visible
#			print "view-y :", y_view
#			print "scroll2:", h_view

			# expando starts before view
			if y_desired_visible < y_view:
#				print "need to scroll up"
				self.Scroll(0, y_desired_visible)

			if y_desired_visible > h_view:
#				print "need to scroll down"
				self.Scroll(0, y_desired_visible)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_soap(self):
		note = []

		tmp = self._TCTRL_Soap.GetValue().strip()
		if tmp != u'':
			note.append(['s', tmp])

		tmp = self._TCTRL_sOap.GetValue().strip()
		if tmp != u'':
			note.append(['o', tmp])

		tmp = self._TCTRL_soAp.GetValue().strip()
		if tmp != u'':
			note.append(['a', tmp])

		tmp = self._TCTRL_soaP.GetValue().strip()
		if tmp != u'':
			note.append(['p', tmp])

		return note

	soap = property(_get_soap, lambda x:x)
	#--------------------------------------------------------
	def _get_empty(self):
		for field in self.fields:
			if field.GetValue().strip() != u'':
				return False
		return True

	empty = property(_get_empty, lambda x:x)
#============================================================
class cSoapLineTextCtrl(wxexpando.ExpandoTextCtrl):

	def __init__(self, *args, **kwargs):

		wxexpando.ExpandoTextCtrl.__init__(self, *args, **kwargs)

		self.__keyword_separators = regex.compile("[!?'\".,:;)}\]\r\n\s\t]+")

		self.__register_interests()
	#------------------------------------------------
	# event handling
	#------------------------------------------------
	def __register_interests(self):
		#wx.EVT_KEY_DOWN (self, self.__on_key_down)
		#wx.EVT_KEY_UP (self, self.__OnKeyUp)
		wx.EVT_CHAR(self, self.__on_char)
		wx.EVT_SET_FOCUS(self, self.__on_focus)
	#--------------------------------------------------------
	def __on_focus(self, evt):
		evt.Skip()
		wx.CallAfter(self._after_on_focus)
	#--------------------------------------------------------
	def _after_on_focus(self):
		evt = wx.PyCommandEvent(wxexpando.wxEVT_ETC_LAYOUT_NEEDED, self.GetId())
		evt.SetEventObject(self)
		evt.height = None
		evt.numLines = None
		self.GetEventHandler().ProcessEvent(evt)
	#--------------------------------------------------------
	def __on_char(self, evt):
		char = unichr(evt.GetUnicodeKey())

		if self.LastPosition == 1:
			evt.Skip()
			return

		explicit_expansion = False
		if evt.GetModifiers() == (wx.MOD_CMD | wx.MOD_ALT): # portable CTRL-ALT-...
			if evt.GetKeyCode() != 13:
				evt.Skip()
				return
			explicit_expansion = True

		if not explicit_expansion:
			if self.__keyword_separators.match(char) is None:
				evt.Skip()
				return

		caret_pos, line_no = self.PositionToXY(self.InsertionPoint)
		line = self.GetLineText(line_no)
		word = self.__keyword_separators.split(line[:caret_pos])[-1]

		if (
			(not explicit_expansion)
				and
			(word != u'$$steffi')			# Easter Egg ;-)
				and
			(word not in [ r[0] for r in gmPG2.get_text_expansion_keywords() ])
		):
			evt.Skip()
			return

		start = self.InsertionPoint - len(word)
		wx.CallAfter(self.replace_keyword_with_expansion, word, start, explicit_expansion)

		evt.Skip()
		return
	#------------------------------------------------
	def replace_keyword_with_expansion(self, keyword=None, position=None, show_list=False):

		if show_list:
			candidates = gmPG2.get_keyword_expansion_candidates(keyword = keyword)
			if len(candidates) == 0:
				return
			if len(candidates) == 1:
				keyword = candidates[0]
			else:
				keyword = gmListWidgets.get_choices_from_list (
					parent = self,
					msg = _(
						'Several macros match the keyword [%s].\n'
						'\n'
						'Please select the expansion you want to happen.'
					) % keyword,
					caption = _('Selecting text macro'),
					choices = candidates,
					columns = [_('Keyword')],
					single_selection = True,
					can_return_empty = False
				)
				if keyword is None:
					return

		expansion = gmPG2.expand_keyword(keyword = keyword)

		if expansion is None:
			return

		if expansion == u'':
			return

		self.Replace (
			position,
			position + len(keyword),
			expansion
		)

		self.SetInsertionPoint(position + len(expansion) + 1)
		self.ShowPosition(position + len(expansion) + 1)

		return
#============================================================
# visual progress notes
#============================================================
visual_progress_note_document_type = u'visual progress note'

#============================================================
def configure_visual_progress_note_editor():

	def is_valid(value):
		found, binary = gmShellAPI.detect_external_binary(value)
		if not found:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('The command [%s] is not found.') % value,
				beep = True
			)
			return True, value
		return True, binary
	#------------------------------------------
	gmCfgWidgets.configure_string_option (
		message = _(
			'Enter the shell command with which to start\n'
			'the image editor for visual progress notes.\n'
			'\n'
			'Any "%(img)s" included with the arguments\n'
			'will be replaced by the file name of the\n'
			'note template.'
		),
		option = u'external.tools.visual_soap_editor_cmd',
		bias = 'user',
		default_value = None,
		validator = is_valid
	)
#============================================================
def edit_visual_progress_note(filename=None, episode=None):
	"""This assumes <filename> contains an image which can be handled by the configured image editor."""

	dbcfg = gmCfg.cCfgSQL()
	cmd = dbcfg.get2 (
		option = u'external.tools.visual_soap_editor_cmd',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'user'
	)

	if cmd is None:
		gmDispatcher.send(signal = u'statustext', msg = _('Editor for visual progress note not configured.'), beep = False)
		cmd = configure_visual_progress_note_editor()
		if cmd is None:
			gmDispatcher.send(signal = u'statustext', msg = _('Editor for visual progress note not configured.'), beep = True)
			return None

	if u'%(img)s' in cmd:
		cmd % {u'img': filename}
	else:
		cmd = u'%s %s' % (cmd, filename)

	# FIXME: create copy and hand that to the editor
	success = gmShellAPI.run_command_in_shell(cmd, blocking = True)
	if not success:
		gmGuiHelpers.gm_show_error (
			_(
				'There was a problem with running the editor\n'
				'for visual progress notes.\n'
				'\n'
				' [%s]\n'
				'\n'
			) % cmd,
			_('Editing visual progress note')
		)
		return None

	try:
		open(filename, 'r').close()
	except StandardError:
		_log.exception('problem accessing visual progress note file [%s]', filename)
		gmGuiHelpers.gm_show_error (
			_(
				'There was a problem reading the visual\n'
				'progress note from the file:\n'
				'\n'
				' [%s]\n'
				'\n'
			) % filename,
			_('Saving visual progress note')
		)
		return None

	# FIXME: compare copy to original

	doc = gmDocumentWidgets.save_file_as_new_document (
		filename = filename,
		document_type = visual_progress_note_document_type,
		episode = episode,
		unlock_patient = True
	)

	return doc
#============================================================
class cVisualSoapTemplatePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of visual SOAP template."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

#		ctxt = {'ctxt_pat': {'where_part': u'pk_patient = %(pat)s and', 'placeholder': u'pat'}}

"""
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
"""
select
	pk_hospital_stay,
	descr
from (
	select distinct on (pk_hospital_stay)
		pk_hospital_stay,
		descr
	from
		(select
			pk_hospital_stay,
			(
				to_char(admission, 'YYYY-Mon-DD')
				|| coalesce((' (' || hospital || '):'), ': ')
				|| episode
				|| coalesce((' (' || health_issue || ')'), '')
			) as descr
		 from
		 	clin.v_pat_hospital_stays
		 where
			%(ctxt_pat)s

			hospital %(fragment_condition)s
				or
			episode %(fragment_condition)s
				or
			health_issue %(fragment_condition)s
		) as the_stays
) as distinct_stays
order by descr
limit 25
"""
"""			],
			context = ctxt
		)
		mp.setThresholds(3, 4, 6)
		mp.set_context('pat', gmPerson.gmCurrentPatient().ID)

		self.matcher = mp
		self.selection_only = True
"""

#============================================================
from Gnumed.wxGladeWidgets import wxgVisualSoapPnl

class cVisualSoapPnl(wxgVisualSoapPnl.wxgVisualSoapPnl):

	def __init__(self, *args, **kwargs):

		wxgVisualSoapPnl.wxgVisualSoapPnl.__init__(self, *args, **kwargs)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def clear(self):
		# FIXME: clear image field, too
		self._PRW_episode.SetText(value = u'', data = None)
		#self._PRW_comment.SetText(value = u'', data = None)
		self._PRW_comment.SetValue(u'')
		self._PRW_template.SetText(value = u'', data = None)
		self._LCTRL_visual_soaps.set_columns([_('Sketches')])
	#--------------------------------------------------------
	def refresh(self, patient=None, encounter=None):

		self.clear()

		if patient is None:
			patient = gmPerson.gmCurrentPatient()

		if not patient.connected:
			return

		emr = patient.get_emr()
		if encounter is None:
			encounter = emr.active_encounter

		folder = patient.get_document_folder()
		soap_docs = folder.get_documents (
			doc_type = visual_progress_note_document_type,
			encounter = encounter['pk_encounter']
		)

		self._LCTRL_visual_soaps.set_string_items ([
			u'%s%s%s' % (
				gmTools.coalesce(sd['comment'], u'', u'%s\n'),
				gmTools.coalesce(sd['ext_ref'], u'', u'%s\n'),
				sd['episode']
			) for sd in soap_docs
		])
		self._LCTRL_visual_soaps.set_data(soap_docs)

		#self.Layout()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_visual_soap_selected(self, event):

		doc = self._LCTRL_visual_soaps.get_selected_item_data(only_one = True)
		if doc is None:
			return

		parts = doc.get_parts()
		if len(parts) == 0:
			gmDispatcher.send(signal = u'statustext', msg = _('No images in visual progress note.'))
			return

		fname = parts[0].export_to_file()
		if fname is None:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot export visual progress note to file.'))
			return

		img_data = None
		rescaled_width = 300
		try:
			img_data = wx.Image(fname, wx.BITMAP_TYPE_ANY)
			current_width = img_data.GetWidth()
			current_height = img_data.GetHeight()
			rescaled_height = (rescaled_width * current_height) / current_width
			img_data.Rescale(rescaled_width, rescaled_height, quality = wx.IMAGE_QUALITY_HIGH)		# w, h
			bmp_data = wx.BitmapFromImage(img_data)
		except:
			_log.exception('cannot load visual progress note from [%s]', fname)
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot load visual progress note from [%s].') % fname)
			del img_data
			return

		del img_data
		self._IMG_soap.SetBitmap(bmp_data)

		self._PRW_episode.SetText(value = doc['episode'], data = doc['pk_episode'])
		if doc['comment'] is not None:
			self._PRW_comment.SetValue(doc['comment'].strip())

		return
	#--------------------------------------------------------
	def _on_from_file_button_pressed(self, event):

		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a visual progress note template file'),
			defaultDir = os.path.expanduser('~'),
			defaultFile = '',
			#wildcard = "%s (*)|*|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.Destroy()
			return

		full_filename = dlg.GetPath()
		dlg.Hide()
		dlg.Destroy()

		#shutil.copy2(gmLog2._logfile_name, new_name)

		episode = self._PRW_episode.GetData(can_create = True, is_open = False, as_instance = True)
		if episode is None:
			if self._PRW_episode.GetValue().strip() == u'':
				# dummy episode to hold images
				self._PRW_episode.SetText(value = _('visual progress notes'))
				episode = self._PRW_episode.GetData(can_create = True, is_open = False, as_instance = True)

		doc = edit_visual_progress_note(filename = full_filename, episode = episode)
		doc.set_reviewed(technically_abnormal=False, clinically_relevant=True)
		doc['comment'] = self._PRW_comment.GetValue().strip()
		doc.save()
	#--------------------------------------------------------
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_select_narrative_from_episodes():
		pat = gmPerson.ask_for_patient()
		gmPatSearchWidgets.set_active_patient(patient = pat)
		app = wx.PyWidgetTester(size = (200, 200))
		sels = select_narrative_from_episodes()
		print "selected:"
		for sel in sels:
			print sel
	#----------------------------------------
	def test_cSoapNoteExpandoEditAreaPnl():
		pat = gmPerson.ask_for_patient()
		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cSoapNoteExpandoEditAreaPnl(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
	#----------------------------------------
	def test_cSoapPluginPnl():
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			return
		gmPatSearchWidgets.set_active_patient(patient=patient)

		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cSoapPluginPnl(application.frame, -1)
		application.frame.Show(True)
		soap_input._schedule_data_reget()
		application.MainLoop()
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		#test_select_narrative_from_episodes()
		test_cSoapNoteExpandoEditAreaPnl()
		#test_cSoapPluginPnl()

#============================================================

