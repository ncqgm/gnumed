"""GNUmed narrative handling widgets."""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmNarrativeWidgets.py,v $
# $Id: gmNarrativeWidgets.py,v 1.19 2009-01-03 17:29:01 ncq Exp $
__version__ = "$Revision: 1.19 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, os, os.path, time, re as regex


import wx
import wx.lib.expando as wxexpando


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmDispatcher, gmTools, gmDateTime, gmPG2
from Gnumed.business import gmPerson, gmEMRStructItems, gmClinNarrative
from Gnumed.exporters import gmPatientExporter
from Gnumed.wxpython import gmListWidgets, gmEMRStructWidgets, gmRegetMixin, gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgMoveNarrativeDlg, wxgSoapNoteExpandoEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#============================================================
# narrative related widgets/functions
#------------------------------------------------------------
def edit_progress_notes(parent=None, encounters=None, episodes=None, patient=None):

	#-------------------------------------
	def save_note(new=None, old=None):
		if new is None:
			return False

		if new.strip() == u'':
			return False

		selected_narr['narrative'] = new
		selected_narr.save_payload()

		return True
	#-------------------------------------
	# sanity checks
	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit progress notes. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	emr = patient.get_emr()
	notes = emr.get_clin_narrative (
		encounters = encounters,
		episodes = episodes,
		providers = [ gmPerson.gmCurrentProvider()['short_alias'] ]
	)

	dlg = cNarrativeListSelectorDlg (
		parent = parent,
		id = -1,
		narrative = notes,
		msg = _(
			'\n'
			' This list shows the progress notes by %s.\n'
			'\n\n'
			' Select the one you want to edit:\n'
		) % gmPerson.gmCurrentProvider()['short_alias'],
		style = wx.LC_SINGLE_SEL
	)

	btn_pressed = dlg.ShowModal()
	selected_narr = dlg.get_selected_item_data(only_one = True)
	dlg.Destroy()

	if btn_pressed == wx.ID_CANCEL:
		return

	dlg = gmGuiHelpers.cMultilineTextEntryDlg (
		parent,
		-1,
		title = _('Editing progress note'),
		msg = _(
			'This is the original progress note:\n'
			'\n'
			' %s'
		) % selected_narr.format(left_margin = u' ', fancy = True),
		text = selected_narr['narrative'],
		cb_save = save_note
	)
	dlg.ShowModal()

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

	if result == wx.ID_OK:

		wx.BeginBusyCursor()
		val = searcher.GetValue()
		emr = patient.get_emr()
		rows = emr.search_narrative_simple(val)
		wx.EndBusyCursor()

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
			caption = _('search results'),
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
		encounter = pat.get_emr().get_active_encounter()

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
		pat['dob'].strftime('%Y-%m-%d')
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
		enc = emr.get_active_encounter()

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

		splitter_size = self._splitter_main.GetSizeTuple()[0]
		self._splitter_main.SetSashPosition(splitter_size * 3 / 10, True)

		splitter_size = self._splitter_left.GetSizeTuple()[1]
		self._splitter_left.SetSashPosition(splitter_size * 6 / 20, True)

		splitter_size = self._splitter_right.GetSizeTuple()[1]
		self._splitter_right.SetSashPosition(splitter_size * 15 / 20, True)
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self._LCTRL_active_problems.set_string_items()
		self._lbl_hints.SetLabel(u'')
		self._TCTRL_recent_notes.SetValue(u'')
		self._NB_soap_editors.DeleteAllPages()
		self._NB_soap_editors.add_editor()
		self._PRW_encounter_type.SetText(suppress_smarts = True)
		self._PRW_encounter_start.SetText(suppress_smarts = True)
		self._PRW_encounter_end.SetText(suppress_smarts = True)
		self._TCTRL_rfe.SetValue(u'')
		self._TCTRL_aoe.SetValue(u'')
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""Update health problems list.
		"""
		self._LCTRL_active_problems.set_string_items()
		emr = self.__pat.get_emr()
		problems = emr.get_problems()
		list_items = []
		active_problems = []
		for problem in problems:
			if not problem['problem_active']:
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

		return True
	#--------------------------------------------------------
	def __refresh_recent_notes(self):

		emr = self.__pat.get_emr()
		problem = self._NB_soap_editors.get_current_problem()

		if problem is None:
			soap = u''

		elif problem['type'] == u'issue':
			soap = u''

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

			tmp = emr.get_active_encounter().format_soap (
				soap_cats = 'soap',
				emr = emr,
				issues = [ problem['pk_health_issue'] ],
			)
			if len(tmp) > 0:
				soap += _('Current encounter:') + u'\n'
				soap += u'\n'.join(tmp) + u'\n'

		elif problem['type'] == u'episode':
			soap = u''

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

			tmp = emr.get_active_encounter().format_soap (
				soap_cats = 'soap',
				emr = emr,
				issues = [ problem['pk_health_issue'] ],
			)
			if len(tmp) > 0:
				soap += _('Current encounter:') + u'\n'
				soap += u'\n'.join(tmp) + u'\n'

		else:
			soap = u''

		self._TCTRL_recent_notes.SetValue(soap)
		self._TCTRL_recent_notes.ShowPosition(self._TCTRL_recent_notes.GetLastPosition())
	#--------------------------------------------------------
	def __refresh_encounter(self):
		"""Update encounter fields.
		"""
		emr = self.__pat.get_emr()
		enc = emr.get_active_encounter()
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

		self._TCTRL_rfe.SetValue(gmTools.coalesce(enc['reason_for_encounter'], ''))

		self._TCTRL_aoe.SetValue(gmTools.coalesce(enc['assessment_of_encounter'], ''))
	#--------------------------------------------------------
	def __encounter_modified(self):
		"""Assumes that the field data is valid."""

		emr = self.__pat.get_emr()
		enc = emr.get_active_encounter()

		if self._PRW_encounter_type.GetData() != enc['pk_type']:
			print "pk type difference"
			print "field:", self._PRW_encounter_type.GetData()
			print "class:", enc['pk_type']
			return True

		if self._PRW_encounter_start.GetData() is None:
			print "start time None"
			return True

		if self._PRW_encounter_start.GetData().get_pydt() != enc['started']:
			print "start time difference"
			return True

		if self._PRW_encounter_end.GetData() is None:
			print "end time None"
			return True

		if self._PRW_encounter_end.GetData().get_pydt() != enc['last_affirmed']:
			print "end time difference"
			return True

		if self._TCTRL_rfe.GetValue().strip() != enc['reason_for_encounter']:
			print "rfe difference"
			return True

		if self._TCTRL_aoe.GetValue().strip() != enc['assessment_of_encounter']:
			print "aoe difference"
			return True

		return False
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
		gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)

		# synchronous signals
		self.__pat.register_pre_selection_callback(callback = self._pre_selection_callback)
		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)
	#--------------------------------------------------------
	def _pre_selection_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns.
		"""
		# don't worry about the encounter here - it will be offered
		# for editing higher up if anything was saved to the EMR
		if not self._NB_soap_editors.save_all_editors():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
	#--------------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to be shut down.

		Shutdown will not proceed before this returns.
		"""
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

		if not self._NB_soap_editors.save_all_editors():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
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
	def _on_episode_issue_mod_db(self):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_current_encounter_modified(self):
		wx.CallAfter(self.__refresh_encounter)
	#--------------------------------------------------------
	def _on_problem_activated(self, event):
		"""Open progress note editor for this problem.
		"""
		problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		if problem is None:
			return True

		if self._NB_soap_editors.add_editor(problem = problem):
			self.__refresh_recent_notes()
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
		self.__refresh_recent_notes()
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
		if not self._NB_soap_editors.save_all_editors():
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
		self.__refresh_recent_notes()
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
		emr.start_new_encounter()
		gmDispatcher.send(signal = u'statustext', msg = _('Started new encounter for active patient.'))

		event.Skip()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		self.__refresh_encounter()
		# don't ! only do on NB page change, add_editor etc
		#self.__refresh_recent_notes()
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
#		self.__register_interests()
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
			label = _('new episode')
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

		if allow_same_problem:
			new_page = cSoapNoteExpandoEditAreaPnl(parent = self, id = -1, problem = problem_to_add)
			result = self.AddPage (
				page = new_page,
				text = label,
				select = True
			)
			return result

		# new unassociated problem
		if problem_to_add is None:
			# check for dupes
			for page_idx in range(self.GetPageCount()):
				page = self.GetPage(page_idx)
				# found
				if page.problem is None:
					self.SetSelection(page_idx)
					gmDispatcher.send(signal = u'statustext', msg = u'Raising existing editor.', beep = True)
					return True
				continue
			# not found
			new_page = cSoapNoteExpandoEditAreaPnl(parent = self, id = -1, problem = problem_to_add)
			result = self.AddPage (
				page = new_page,
				text = label,
				select = True
			)
			return result

		# real problem
		# - raise existing editor ?
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

		# - add new editor
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
	def save_all_editors(self):

		all_closed = True

		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx+1)
			if page.save(emr = emr, rfe = rfe, aoe = aoe):
				self.DeletePage(page_idx)
			else:
				all_closed = False

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()

		return (all_closed == True)
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
				message = _('Enter a descriptive name for the new episode:'),
				caption = _('Adding a new episode'),
				defaultValue = epi_name,
				style = wx.OK | wx.CANCEL | wx.CENTRE
			)
			decision = dlg.ShowModal()
			if decision != wx.ID_OK:
				return False

			epi_name = dlg.GetValue().strip()
			if epi_name == u'':
				gmGuiHelpers.gm_show_error(_('Cannot save a new episode without a name.'), _('saving progress note'))
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
	#--------------------------------------------------------
	def __on_char(self, evt):
		char = unichr(evt.GetUnicodeKey())

		if self.__keyword_separators.match(char) is None:
			evt.Skip()
			return

		if self.LastPosition == 1:
			evt.Skip()
			return

		caret_pos, line_no = self.PositionToXY(self.InsertionPoint)
		line = self.GetLineText(line_no)
		word = self.__keyword_separators.split(line[:caret_pos])[-1]

		if (word != u'$$steffi') and (word not in [ r[0] for r in gmPG2.get_text_expansion_keywords() ]):
			evt.Skip()
			return

		start = self.InsertionPoint - len(word)
		wx.CallAfter(self.replace_keyword_with_expansion, word, start)
		evt.Skip()
		return
	#------------------------------------------------
	def replace_keyword_with_expansion(self, keyword=None, position=None):

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
# main
#------------------------------------------------------------
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_select_narrative_from_episodes():
		pat = gmPerson.ask_for_patient()
		gmPerson.set_active_patient(patient = pat)
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
		gmPerson.set_active_patient(patient=patient)

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
# $Log: gmNarrativeWidgets.py,v $
# Revision 1.19  2009-01-03 17:29:01  ncq
# - listen on new current_encounter_modified
# - detecting encounter field changes at exit/patient doesn't properly work
# - refresh recent notes where needed
#
# Revision 1.18  2009/01/02 11:41:16  ncq
# - improved event handling
#
# Revision 1.17  2008/12/27 15:50:41  ncq
# - almost finish implementing soap saving
#
# Revision 1.16  2008/12/26 22:35:44  ncq
# - edit_progress_notes
# - implement most of new soap plugin functionality
#
# Revision 1.15  2008/11/24 11:10:29  ncq
# - cleanup
#
# Revision 1.14  2008/11/23 12:47:02  ncq
# - preset splitter ratios and gravity
# - cleanup
# - reorder recent notes with most recent on bottom as per list
#
# Revision 1.13  2008/11/20 20:35:50  ncq
# - new soap plugin widgets
#
# Revision 1.12  2008/10/26 01:21:52  ncq
# - factor out searching EMR for narrative
#
# Revision 1.11  2008/10/22 12:21:57  ncq
# - use %x in strftime where appropriate
#
# Revision 1.10  2008/10/12 16:26:20  ncq
# - consultation -> encounter
#
# Revision 1.9  2008/09/02 19:01:12  ncq
# - adjust to clin health_issue fk_patient drop and related changes
#
# Revision 1.8  2008/07/28 15:46:05  ncq
# - export_narrative_for_medistar_import
#
# Revision 1.7  2008/03/05 22:30:14  ncq
# - new style logging
#
# Revision 1.6  2007/12/03 20:45:28  ncq
# - improved docs
#
# Revision 1.5  2007/09/10 12:36:02  ncq
# - improved wording in narrative selector at SOAP level
#
# Revision 1.4  2007/09/09 19:21:04  ncq
# - get top level wx.App window if parent is None
# - support filtering by soap_cats
#
# Revision 1.3  2007/09/07 22:45:58  ncq
# - much improved select_narrative_from_episodes()
#
# Revision 1.2  2007/09/07 10:59:17  ncq
# - greatly improve select_narrative_by_episodes
#   - remember selections
#   - properly levelled looping
# - fix test suite
#
# Revision 1.1  2007/08/29 22:06:15  ncq
# - factored out narrative widgets
#
#
