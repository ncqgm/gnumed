"""GNUmed narrative handling widgets."""
#================================================================
__version__ = "$Revision: 1.46 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging, os, os.path, time, re as regex, shutil


import wx
import wx.lib.expando as wx_expando
import wx.lib.agw.supertooltip as agw_stt
import wx.lib.statbmp as wx_genstatbmp


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSurgery
from Gnumed.business import gmForms
from Gnumed.business import gmDocuments
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmKeywordExpansion

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmTextExpansionWidgets

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
		# cancelled
		if encounters is None:
			return True
		# none selected
		if len(encounters) == 0:
			return True

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
			providers = [ gmStaff.gmCurrentProvider()['short_alias'] ]
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
		) % gmStaff.gmCurrentProvider()['short_alias'],
		columns = [_('when'), _('type'), _('entry')],
		single_selection = True,
		can_return_empty = False,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
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

	items = [ [gmPerson.cIdentity(aPK_obj =
	r['pk_patient'])['description_gender'], r['narrative'],
	r['src_table']] for r in results ]

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
def export_narrative_for_medistar_import(parent=None, soap_cats=u'soapu', encounter=None):

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
		soap_cats = u'soapu',
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
def select_narrative_from_episodes_new(parent=None, soap_cats=None):
	"""soap_cats needs to be a list"""

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	selected_soap = {}
	selected_narrative_pks = []

	#-----------------------------------------------
	def pick_soap_from_episode(episode):

		narr_for_epi = emr.get_clin_narrative(episodes = [episode['pk_episode']], soap_cats = soap_cats)

		if len(narr_for_epi) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for selected episode.'))
			return True

		dlg = cNarrativeListSelectorDlg (
			parent = parent,
			id = -1,
			narrative = narr_for_epi,
			msg = _(
				'\n This is the narrative (type %s) for the chosen episodes.\n'
				'\n'
				' Now, mark the entries you want to include in your report.\n'
			) % u'/'.join([ gmClinNarrative.soap_cat2l10n[cat] for cat in gmTools.coalesce(soap_cats, list(u'soapu')) ])
		)
#		selection_idxs = []
#		for idx in range(len(narr_for_epi)):
#			if narr_for_epi[idx]['pk_narrative'] in selected_narrative_pks:
#				selection_idxs.append(idx)
#		if len(selection_idxs) != 0:
#			dlg.set_selections(selections = selection_idxs)
		btn_pressed = dlg.ShowModal()
		selected_narr = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			return True

		selected_narrative_pks = [ i['pk_narrative'] for i in selected_narr ]
		for narr in selected_narr:
			selected_soap[narr['pk_narrative']] = narr

		print "before returning from picking soap"

		return True
	#-----------------------------------------------
	selected_episode_pks = []

	all_epis = [ epi for epi in emr.get_episodes() if epi.has_narrative ]

	if len(all_epis) == 0:
		gmDispatcher.send(signal = 'statustext', msg = _('No episodes recorded for the health issues selected.'))
		return []

	dlg = gmEMRStructWidgets.cEpisodeListSelectorDlg (
		parent = parent,
		id = -1,
		episodes = all_epis,
		msg = _('\n Select the the episode you want to report on.\n')
	)
#	selection_idxs = []
#	for idx in range(len(all_epis)):
#		if all_epis[idx]['pk_episode'] in selected_episode_pks:
#			selection_idxs.append(idx)
#	if len(selection_idxs) != 0:
#		dlg.set_selections(selections = selection_idxs)
	dlg.left_extra_button = (
		_('Pick SOAP'),
		_('Pick SOAP entries from topmost selected episode'),
		pick_soap_from_episode
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wx.ID_CANCEL:
		return None

	return selected_soap.values()
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
				) % u'/'.join([ gmClinNarrative.soap_cat2l10n[cat] for cat in gmTools.coalesce(soap_cats, list(u'soapu')) ])
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
	- previous notes

	Right hand side:
	- encounter details fields
	- notebook with progress note editors
	- visual progress notes
	- hints

	Listens to patient change signals, thus acts on the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgSoapPluginPnl.wxgSoapPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__patient_just_changed = False
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
		self._LCTRL_active_problems.set_columns([_('Last'), _('Problem'), _('In health issue')])
		self._LCTRL_active_problems.set_string_items()

		self._splitter_main.SetSashGravity(0.5)
		self._splitter_left.SetSashGravity(0.5)

		splitter_size = self._splitter_main.GetSizeTuple()[0]
		self._splitter_main.SetSashPosition(splitter_size * 3 / 10, True)

		splitter_size = self._splitter_left.GetSizeTuple()[1]
		self._splitter_left.SetSashPosition(splitter_size * 6 / 20, True)

		self._NB_soap_editors.DeleteAllPages()
		self._NB_soap_editors.MoveAfterInTabOrder(self._PRW_aoe_codes)
	#--------------------------------------------------------
	def _on_encounter_start_lost_focus(self):
		start = self._PRW_encounter_start.GetData()
		if start is None:
			return
		start = start.get_pydt()

		end = self._PRW_encounter_end.GetData()
		if end is None:
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = start,
				accuracy = gmDateTime.acc_minutes
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return
		end = end.get_pydt()

		if start > end:
			end = end.replace (
				year = start.year,
				month = start.month,
				day = start.day
			)
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = end,
				accuracy = gmDateTime.acc_minutes
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return

		emr = self.__pat.get_emr()
		if start != emr.active_encounter['started']:
			end = end.replace (
				year = start.year,
				month = start.month,
				day = start.day
			)
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = end,
				accuracy = gmDateTime.acc_minutes
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return

		return
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""Clear all information from input panel."""

		self._LCTRL_active_problems.set_string_items()

		self._TCTRL_recent_notes.SetValue(u'')
		self._SZR_recent_notes_staticbox.SetLabel(_('Most recent notes on selected problem'))

		self._TCTRL_rfe.SetValue(u'')
		self._PRW_rfe_codes.SetText(suppress_smarts = True)
		self._TCTRL_aoe.SetValue(u'')
		self._PRW_aoe_codes.SetText(suppress_smarts = True)

		self._NB_soap_editors.DeleteAllPages()
		self._NB_soap_editors.add_editor()
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""Update health problems list."""

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

				list_items.append([last, problem['problem'], gmTools.u_left_arrow_with_tail])

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
					gmTools.coalesce(initial = epi['health_issue'], instead = u'?')		#gmTools.u_diameter
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
	def __get_soap_for_issue_problem(self, problem=None):
		soap = u''
		emr = self.__pat.get_emr()
		prev_enc = emr.get_last_but_one_encounter(issue_id = problem['pk_health_issue'])
		if prev_enc is not None:
			soap += prev_enc.format (
				issues = [ problem['pk_health_issue'] ],
				with_soap = True,
				with_docs = False,
				with_tests = False,
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
			soap += _('Current encounter:') + u'\n'
			soap += u'\n'.join(tmp) + u'\n'

		if problem['summary'] is not None:
			soap += u'\n-- %s ----------\n%s' % (
				_('Cumulative summary'),
				gmTools.wrap (
					text = problem['summary'],
					width = 45,
					initial_indent = u' ',
					subsequent_indent = u' '
				).strip('\n')
			)

		return soap
	#--------------------------------------------------------
	def __get_soap_for_episode_problem(self, problem=None):
		soap = u''
		emr = self.__pat.get_emr()
		prev_enc = emr.get_last_but_one_encounter(episode_id = problem['pk_episode'])
		if prev_enc is not None:
			soap += prev_enc.format (
				episodes = [ problem['pk_episode'] ],
				with_soap = True,
				with_docs = False,
				with_tests = False,
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
						with_docs = False,
						with_tests = False,
						patient = self.__pat,
						issues = [ problem['pk_health_issue'] ],
						fancy_header = False,
						with_rfe_aoe = True
					)

		tmp = emr.active_encounter.format_soap (
			soap_cats = 'soapu',
			emr = emr,
			issues = [ problem['pk_health_issue'] ],
		)
		if len(tmp) > 0:
			soap += _('Current encounter:') + u'\n'
			soap += u'\n'.join(tmp) + u'\n'

		if problem['summary'] is not None:
			soap += u'\n-- %s ----------\n%s' % (
				_('Cumulative summary'),
				gmTools.wrap (
					text = problem['summary'],
					width = 45,
					initial_indent = u' ',
					subsequent_indent = u' '
				).strip('\n')
			)

		return soap
	#--------------------------------------------------------
	def __refresh_current_editor(self):
		self._NB_soap_editors.refresh_current_editor()
	#--------------------------------------------------------
	def __setup_initial_patient_editors(self):
		if not self.__patient_just_changed:
			return

		dbcfg = gmCfg.cCfgSQL()
		auto_open_recent_problems = bool(dbcfg.get2 (
			option = u'horstspace.soap_editor.auto_open_latest_episodes',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user',
			default = True
		))

		self.__patient_just_changed = False
		emr = self.__pat.get_emr()
		recent_epis = emr.active_encounter.get_episodes()
		prev_enc = emr.get_last_but_one_encounter()
		if prev_enc is not None:
			recent_epis.extend(prev_enc.get_episodes())

		for epi in recent_epis:
			if not epi['episode_open']:
				continue
			self._NB_soap_editors.add_editor(problem = epi, allow_same_problem = False)
	#--------------------------------------------------------
	def __refresh_recent_notes(self, problem=None):
		"""This refreshes the recent-notes part."""

		soap = u''
		caption = u'<?>'

		if problem['type'] == u'issue':
			caption = problem['problem'][:35]
			soap = self.__get_soap_for_issue_problem(problem = problem)

		elif problem['type'] == u'episode':
			caption = problem['problem'][:35]
			soap = self.__get_soap_for_episode_problem(problem = problem)

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
		"""Update encounter fields."""

		emr = self.__pat.get_emr()
		enc = emr.active_encounter

		self._TCTRL_rfe.SetValue(gmTools.coalesce(enc['reason_for_encounter'], u''))
		val, data = self._PRW_rfe_codes.generic_linked_codes2item_dict(enc.generic_codes_rfe)
		self._PRW_rfe_codes.SetText(val, data)

		self._TCTRL_aoe.SetValue(gmTools.coalesce(enc['assessment_of_encounter'], u''))
		val, data = self._PRW_aoe_codes.generic_linked_codes2item_dict(enc.generic_codes_aoe)
		self._PRW_aoe_codes.SetText(val, data)

		self._TCTRL_rfe.Refresh()
		self._PRW_rfe_codes.Refresh()
		self._TCTRL_aoe.Refresh()
		self._PRW_aoe_codes.Refresh()
	#--------------------------------------------------------
	def __encounter_modified(self):
		"""Assumes that the field data is valid."""

		emr = self.__pat.get_emr()
		enc = emr.active_encounter

		data = {
			'pk_type': enc['pk_type'],
			'reason_for_encounter': gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u''),
			'assessment_of_encounter': gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
			'pk_location': enc['pk_location'],
			'pk_patient': enc['pk_patient'],
			'pk_generic_codes_rfe': self._PRW_rfe_codes.GetData(),
			'pk_generic_codes_aoe': self._PRW_aoe_codes.GetData(),
			'started': enc['started'],
			'last_affirmed': enc['last_affirmed']
		}

		return not enc.same_payload(another_object = data)
	#--------------------------------------------------------
	def __encounter_valid_for_save(self):
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
		gmDispatcher.connect(signal = u'episode_code_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_doc_mod_db)			# visual progress notes
		gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)
		gmDispatcher.connect(signal = u'current_encounter_switched', receiver = self._on_current_encounter_switched)
		gmDispatcher.connect(signal = u'rfe_code_mod_db', receiver = self._on_encounter_code_modified)
		gmDispatcher.connect(signal = u'aoe_code_mod_db', receiver = self._on_encounter_code_modified)

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
		saved = self._NB_soap_editors.save_all_editors (
			emr = emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u'')
			]
		)
		if not saved:
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
		self.__patient_just_changed = True
	#--------------------------------------------------------
	def _on_doc_mod_db(self):
		wx.CallAfter(self.__refresh_current_editor)
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_encounter_code_modified(self):
		emr = self.__pat.get_emr()
		emr.active_encounter.refetch_payload()
		wx.CallAfter(self.__refresh_encounter)
	#--------------------------------------------------------
	def _on_current_encounter_modified(self):
		wx.CallAfter(self.__refresh_encounter)
	#--------------------------------------------------------
	def _on_current_encounter_switched(self):
		wx.CallAfter(self.__on_current_encounter_switched)
	#--------------------------------------------------------
	def __on_current_encounter_switched(self):
		self.__refresh_encounter()
	#--------------------------------------------------------
	# problem list specific events
	#--------------------------------------------------------
	def _on_problem_focused(self, event):
		"""Show related note at the bottom."""
		pass
	#--------------------------------------------------------
	def _on_problem_rclick(self, event):
		problem = self._LCTRL_active_problems.get_selected_item_data(only_one = True)
		if problem['type'] == u'issue':
			gmEMRStructWidgets.edit_health_issue(parent = self, issue = problem.get_as_health_issue())
			return

		if problem['type'] == u'episode':
			gmEMRStructWidgets.edit_episode(parent = self, episode = problem.get_as_episode())
			return

		event.Skip()
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
	def _on_show_closed_episodes_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	def _on_irrelevant_issues_checked(self, event):
		self.__refresh_problem_list()
	#--------------------------------------------------------
	# SOAP editor specific buttons
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
	def _on_save_note_button_pressed(self, event):
		emr = self.__pat.get_emr()
		self._NB_soap_editors.save_current_editor (
			emr = emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u'')
			]
		)
		event.Skip()
	#--------------------------------------------------------
	def _on_save_note_under_button_pressed(self, event):
		encounter = gmEMRStructWidgets.select_encounters (
			parent = self,
			patient = self.__pat,
			single_selection = True
		)
		# cancelled or None selected:
		if encounter is None:
			return

		emr = self.__pat.get_emr()
		self._NB_soap_editors.save_current_editor (
			emr = emr,
			encounter = encounter['pk_encounter'],
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u'')
			]
		)
		event.Skip()
	#--------------------------------------------------------
	def _on_image_button_pressed(self, event):
		emr = self.__pat.get_emr()
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
		emr = self.__pat.get_emr()
		saved = self._NB_soap_editors.save_all_editors (
			emr = emr,
			episode_name_candidates = [
				gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u''),
				gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u'')
			]
		)
		if not saved:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save all editors. Some were kept open.'), beep = True)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		self.__refresh_encounter()
		self.__setup_initial_patient_editors()
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
	def save_current_editor(self, emr=None, episode_name_candidates=None, encounter=None):

		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)

		if not page.save(emr = emr, episode_name_candidates = episode_name_candidates, encounter = encounter):
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
	def save_all_editors(self, emr=None, episode_name_candidates=None):

		_log.debug('saving editors: %s', self.GetPageCount())

		all_closed = True
		for page_idx in range((self.GetPageCount() - 1), -1, -1):
			_log.debug('#%s of %s', page_idx, self.GetPageCount())
			try:
				self.ChangeSelection(page_idx)
				_log.debug('editor raised')
			except:
				_log.exception('cannot raise editor')
			page = self.GetPage(page_idx)
			if page.save(emr = emr, episode_name_candidates = episode_name_candidates):
				_log.debug('saved, deleting now')
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
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		page.clear()
	#--------------------------------------------------------
	def get_current_problem(self):
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		return page.problem
	#--------------------------------------------------------
	def refresh_current_editor(self):
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		page.refresh()
	#--------------------------------------------------------
	def add_visual_progress_note_to_current_problem(self):
		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)
		page.add_visual_progress_note()
#============================================================
from Gnumed.wxGladeWidgets import wxgSoapNoteExpandoEditAreaPnl

class cSoapNoteExpandoEditAreaPnl(wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl):
	"""An Edit Area like panel for entering progress notes.

	Subjective:					Codes:
		expando text ctrl
	Objective:					Codes:
		expando text ctrl
	Assessment:					Codes:
		expando text ctrl
	Plan:						Codes:
		expando text ctrl
	visual progress notes
		panel with images
	Episode synopsis:			Codes:
		text ctrl

	- knows the problem this edit area is about
	- can deal with issue or episode type problems
	"""

	def __init__(self, *args, **kwargs):

		try:
			self.problem = kwargs['problem']
			del kwargs['problem']
		except KeyError:
			self.problem = None

		wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl.__init__(self, *args, **kwargs)

		self.soap_fields = [
			self._TCTRL_Soap,
			self._TCTRL_sOap,
			self._TCTRL_soAp,
			self._TCTRL_soaP
		]

		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	def __init_ui(self):
		self.refresh_summary()
		if self.problem is not None:
			if self.problem['summary'] is None:
				self._TCTRL_episode_summary.SetValue(u'')
		self.refresh_visual_soap()
	#--------------------------------------------------------
	def refresh(self):
		self.refresh_summary()
		self.refresh_visual_soap()
	#--------------------------------------------------------
	def refresh_summary(self):
		self._TCTRL_episode_summary.SetValue(u'')
		self._PRW_episode_codes.SetText(u'', self._PRW_episode_codes.list2data_dict([]))
		self._LBL_summary.SetLabel(_('Episode synopsis'))

		# new problem ?
		if self.problem is None:
			return

		# issue-level problem ?
		if self.problem['type'] == u'issue':
			return

		# episode-level problem
		caption = _(u'Synopsis (%s)') % (
			gmDateTime.pydt_strftime (
				self.problem['modified_when'],
				format = '%B %Y',
				accuracy = gmDateTime.acc_days
			)
		)
		self._LBL_summary.SetLabel(caption)

		if self.problem['summary'] is not None:
			self._TCTRL_episode_summary.SetValue(self.problem['summary'].strip())

		val, data = self._PRW_episode_codes.generic_linked_codes2item_dict(self.problem.generic_codes)
		self._PRW_episode_codes.SetText(val, data)
	#--------------------------------------------------------
	def refresh_visual_soap(self):
		if self.problem is None:
			self._PNL_visual_soap.refresh(document_folder = None)
			return

		if self.problem['type'] == u'issue':
			self._PNL_visual_soap.refresh(document_folder = None)
			return

		if self.problem['type'] == u'episode':
			pat = gmPerson.gmCurrentPatient()
			doc_folder = pat.get_document_folder()
			emr = pat.get_emr()
			self._PNL_visual_soap.refresh (
				document_folder = doc_folder,
				episodes = [self.problem['pk_episode']],
				encounter = emr.active_encounter['pk_encounter']
			)
			return
	#--------------------------------------------------------
	def clear(self):
		for field in self.soap_fields:
			field.SetValue(u'')
		self._TCTRL_episode_summary.SetValue(u'')
		self._LBL_summary.SetLabel(_('Episode synopsis'))
		self._PRW_episode_codes.SetText(u'', self._PRW_episode_codes.list2data_dict([]))
		self._PNL_visual_soap.clear()
	#--------------------------------------------------------
	def add_visual_progress_note(self):
		fname, discard_unmodified = select_visual_progress_note_template(parent = self)
		if fname is None:
			return False

		if self.problem is None:
			issue = None
			episode = None
		elif self.problem['type'] == 'issue':
			issue = self.problem['pk_health_issue']
			episode = None
		else:
			issue = self.problem['pk_health_issue']
			episode = gmEMRStructItems.problem2episode(self.problem)

		wx.CallAfter (
			edit_visual_progress_note,
			filename = fname,
			episode = episode,
			discard_unmodified = discard_unmodified,
			health_issue = issue
		)
	#--------------------------------------------------------
	def save(self, emr=None, episode_name_candidates=None, encounter=None):

		if self.empty:
			return True

		# new episode (standalone=unassociated or new-in-issue)
		if (self.problem is None) or (self.problem['type'] == 'issue'):
			episode = self.__create_new_episode(emr = emr, episode_name_candidates = episode_name_candidates)
			# user cancelled
			if episode is None:
				return False
		# existing episode
		else:
			episode = emr.problem2episode(self.problem)

		if encounter is None:
			encounter = emr.current_encounter['pk_encounter']

		soap_notes = []
		for note in self.soap:
			saved, data = gmClinNarrative.create_clin_narrative (
				soap_cat = note[0],
				narrative = note[1],
				episode_id = episode['pk_episode'],
				encounter_id = encounter
			)
			if saved:
				soap_notes.append(data)

		# codes per narrative !
#		for note in soap_notes:
#			if note['soap_cat'] == u's':
#				codes = self._PRW_Soap_codes
#			elif note['soap_cat'] == u'o':
#			elif note['soap_cat'] == u'a':
#			elif note['soap_cat'] == u'p':

		# set summary but only if not already set above for a
		# newly created episode (either standalone or within
		# a health issue)
		if self.problem is not None:
			if self.problem['type'] == 'episode':
				episode['summary'] = self._TCTRL_episode_summary.GetValue().strip()
				episode.save()

		# codes for episode
		episode.generic_codes = [ d['data'] for d in self._PRW_episode_codes.GetData() ]

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __create_new_episode(self, emr=None, episode_name_candidates=None):

		episode_name_candidates.append(self._TCTRL_episode_summary.GetValue().strip())
		for candidate in episode_name_candidates:
			if candidate is None:
				continue
			epi_name = candidate.strip().replace('\r', '//').replace('\n', '//')
			break

		dlg = wx.TextEntryDialog (
			parent = self,
			message = _('Enter a short working name for this new problem:'),
			caption = _('Creating a problem (episode) to save the notelet under ...'),
			defaultValue = epi_name,
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		decision = dlg.ShowModal()
		if decision != wx.ID_OK:
			return None

		epi_name = dlg.GetValue().strip()
		if epi_name == u'':
			gmGuiHelpers.gm_show_error(_('Cannot save a new problem without a name.'), _('saving progress note'))
			return None

		# create episode
		new_episode = emr.add_episode(episode_name = epi_name[:45], pk_health_issue = None, is_open = True)
		new_episode['summary'] = self._TCTRL_episode_summary.GetValue().strip()
		new_episode.save()

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

		return new_episode
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		for field in self.soap_fields:
			wx_expando.EVT_ETC_LAYOUT_NEEDED(field, field.GetId(), self._on_expando_needs_layout)
		wx_expando.EVT_ETC_LAYOUT_NEEDED(self._TCTRL_episode_summary, self._TCTRL_episode_summary.GetId(), self._on_expando_needs_layout)
		gmDispatcher.connect(signal = u'doc_page_mod_db', receiver = self._refresh_visual_soap)
	#--------------------------------------------------------
	def _refresh_visual_soap(self):
		wx.CallAfter(self.refresh_visual_soap)
	#--------------------------------------------------------
	def _on_expando_needs_layout(self, evt):
		# need to tell ourselves to re-Layout to refresh scroll bars

		# provoke adding scrollbar if needed
		#self.Fit()				# works on Linux but not on Windows
		self.FitInside()		# needed on Windows rather than self.Fit()

		if self.HasScrollbar(wx.VERTICAL):
			# scroll panel to show cursor
			expando = self.FindWindowById(evt.GetId())
			y_expando = expando.GetPositionTuple()[1]
			h_expando = expando.GetSizeTuple()[1]
			line_cursor = expando.PositionToXY(expando.GetInsertionPoint())[1] + 1
			if expando.NumberOfLines == 0:
				no_of_lines = 1
			else:
				no_of_lines = expando.NumberOfLines
			y_cursor = int(round((float(line_cursor) / no_of_lines) * h_expando))
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
		soap_notes = []

		tmp = self._TCTRL_Soap.GetValue().strip()
		if tmp != u'':
			soap_notes.append(['s', tmp])

		tmp = self._TCTRL_sOap.GetValue().strip()
		if tmp != u'':
			soap_notes.append(['o', tmp])

		tmp = self._TCTRL_soAp.GetValue().strip()
		if tmp != u'':
			soap_notes.append(['a', tmp])

		tmp = self._TCTRL_soaP.GetValue().strip()
		if tmp != u'':
			soap_notes.append(['p', tmp])

		return soap_notes

	soap = property(_get_soap, lambda x:x)
	#--------------------------------------------------------
	def _get_empty(self):

		# soap fields
		for field in self.soap_fields:
			if field.GetValue().strip() != u'':
				return False

		# summary
		summary = self._TCTRL_episode_summary.GetValue().strip()
		if self.problem is None:
			if summary != u'':
				return False
		elif self.problem['type'] == u'issue':
			if summary != u'':
				return False
		else:
			if self.problem['summary'] is None:
				if summary != u'':
					return False
			else:
				if summary != self.problem['summary'].strip():
					return False

		# codes
		new_codes = self._PRW_episode_codes.GetData()
		if self.problem is None:
			if len(new_codes) > 0:
				return False
		elif self.problem['type'] == u'issue':
			if len(new_codes) > 0:
				return False
		else:
			old_code_pks = self.problem.generic_codes
			if len(old_code_pks) != len(new_codes):
				return False
			for code in new_codes:
				if code['data'] not in old_code_pks:
					return False

		return True

	empty = property(_get_empty, lambda x:x)
#============================================================
class cSoapLineTextCtrl(wx_expando.ExpandoTextCtrl):

	def __init__(self, *args, **kwargs):

		wx_expando.ExpandoTextCtrl.__init__(self, *args, **kwargs)

		self.__keyword_separators = regex.compile("[!?'\".,:;)}\]\r\n\s\t]+")

		self.__register_interests()
	#------------------------------------------------
	# fixup errors in platform expando.py
	#------------------------------------------------
	def _wrapLine(self, line, dc, width):

		if (wx.MAJOR_VERSION >= 2) and (wx.MINOR_VERSION > 8):
			return super(cSoapLineTextCtrl, self)._wrapLine(line, dc, width)

		# THIS FIX LIFTED FROM TRUNK IN SVN:
		# Estimate where the control will wrap the lines and
		# return the count of extra lines needed.
		pte = dc.GetPartialTextExtents(line)
		width -= wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
		idx = 0
		start = 0
		count = 0
		spc = -1
		while idx < len(pte):
		    if line[idx] == ' ':
		        spc = idx
		    if pte[idx] - start > width:
		        # we've reached the max width, add a new line
		        count += 1
		        # did we see a space? if so restart the count at that pos
		        if spc != -1:
		            idx = spc + 1
		            spc = -1
		        if idx < len(pte):
		            start = pte[idx]
		    else:
		        idx += 1
		return count
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
		#wx.CallAfter(self._adjustCtrl)
		evt = wx.PyCommandEvent(wx_expando.wxEVT_ETC_LAYOUT_NEEDED, self.GetId())
		evt.SetEventObject(self)
		#evt.height = None
		#evt.numLines = None
		#evt.height = self.GetSize().height
		#evt.numLines = self.GetNumberOfLines()
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
		keyword = self.__keyword_separators.split(line[:caret_pos])[-1]

		if (
			(not explicit_expansion)
				and
			(keyword != u'$$steffi')			# Easter Egg ;-)
				and
			(keyword not in [ r[0] for r in gmKeywordExpansion.get_textual_expansion_keywords() ])
		):
			evt.Skip()
			return

		start = self.InsertionPoint - len(keyword)
		wx.CallAfter(self.replace_keyword_with_expansion, keyword, start, explicit_expansion)

		evt.Skip()
		return
	#------------------------------------------------
	def replace_keyword_with_expansion(self, keyword=None, position=None, show_list=False):

		expansion = gmTextExpansionWidgets.expand_keyword(parent = self, keyword = keyword, show_list = show_list)

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
def configure_visual_progress_note_editor():

	def is_valid(value):

		if value is None:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('You need to actually set an editor.'),
				beep = True
			)
			return False, value

		if value.strip() == u'':
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('You need to actually set an editor.'),
				beep = True
			)
			return False, value

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
	cmd = gmCfgWidgets.configure_string_option (
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

	return cmd
#============================================================
def select_file_as_visual_progress_note_template(parent=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = wx.FileDialog (
		parent = parent,
		message = _('Choose file to use as template for new visual progress note'),
		defaultDir = os.path.expanduser('~'),
		defaultFile = '',
		#wildcard = "%s (*)|*|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
		style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST
	)
	result = dlg.ShowModal()

	if result == wx.ID_CANCEL:
		dlg.Destroy()
		return None

	full_filename = dlg.GetPath()
	dlg.Hide()
	dlg.Destroy()
	return full_filename
#------------------------------------------------------------
def select_visual_progress_note_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Visual progress note source'),
		question = _('From which source do you want to pick the image template ?'),
		button_defs = [
			{'label': _('Database'), 'tooltip': _('List of templates in the database.'), 'default': True},
			{'label': _('File'), 'tooltip': _('Files in the filesystem.'), 'default': False},
			{'label': _('Device'), 'tooltip': _('Image capture devices (scanners, cameras, etc)'), 'default': False}
		]
	)
	result = dlg.ShowModal()
	dlg.Destroy()

	# 1) select from template
	if result == wx.ID_YES:
		_log.debug('visual progress note template from: database template')
		from Gnumed.wxpython import gmFormWidgets
		template = gmFormWidgets.manage_form_templates (
			parent = parent,
			template_types = [gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE],
			active_only = True
		)
		if template is None:
			return (None, None)
		filename = template.export_to_file()
		if filename is None:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot export visual progress note template for [%s].') % template['name_long'])
			return (None, None)
		return (filename, True)

	# 2) select from disk file
	if result == wx.ID_NO:
		_log.debug('visual progress note template from: disk file')
		fname = select_file_as_visual_progress_note_template(parent = parent)
		if fname is None:
			return (None, None)
		# create a copy of the picked file -- don't modify the original
		ext = os.path.splitext(fname)[1]
		tmp_name = gmTools.get_unique_filename(suffix = ext)
		_log.debug('visual progress note from file: [%s] -> [%s]', fname, tmp_name)
		shutil.copy2(fname, tmp_name)
		return (tmp_name, False)

	# 3) acquire from capture device
	if result == wx.ID_CANCEL:
		_log.debug('visual progress note template from: image capture device')
		fnames = gmDocumentWidgets.acquire_images_from_capture_device(device = None, calling_window = parent)
		if fnames is None:
			return (None, None)
		if len(fnames) == 0:
			return (None, None)
		return (fnames[0], False)

	_log.debug('no visual progress note template source selected')
	return (None, None)
#------------------------------------------------------------
def edit_visual_progress_note(filename=None, episode=None, discard_unmodified=False, doc_part=None, health_issue=None):
	"""This assumes <filename> contains an image which can be handled by the configured image editor."""

	if doc_part is not None:
		filename = doc_part.export_to_file()
		if filename is None:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot export visual progress note to file.'))
			return None

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
		cmd = cmd % {u'img': filename}
	else:
		cmd = u'%s %s' % (cmd, filename)

	if discard_unmodified:
		original_stat = os.stat(filename)
		original_md5 = gmTools.file2md5(filename)

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

	if discard_unmodified:
		modified_stat = os.stat(filename)
		# same size ?
		if original_stat.st_size == modified_stat.st_size:
			modified_md5 = gmTools.file2md5(filename)
			# same hash ?
			if original_md5 == modified_md5:
				_log.debug('visual progress note (template) not modified')
				# ask user to decide
				msg = _(
					u'You either created a visual progress note from a template\n'
					u'in the database (rather than from a file on disk) or you\n'
					u'edited an existing visual progress note.\n'
					u'\n'
					u'The template/original was not modified at all, however.\n'
					u'\n'
					u'Do you still want to save the unmodified image as a\n'
					u'visual progress note into the EMR of the patient ?\n'
				)
				save_unmodified = gmGuiHelpers.gm_show_question (
					msg,
					_('Saving visual progress note')
				)
				if not save_unmodified:
					_log.debug('user discarded unmodified note')
					return

	if doc_part is not None:
		_log.debug('updating visual progress note')
		doc_part.update_data_from_file(fname = filename)
		doc_part.set_reviewed(technically_abnormal = False, clinically_relevant = True)
		return None

	if not isinstance(episode, gmEMRStructItems.cEpisode):
		if episode is None:
			episode = _('visual progress notes')
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		episode = emr.add_episode(episode_name = episode.strip(), pk_health_issue = health_issue, is_open = False)

	doc = gmDocumentWidgets.save_file_as_new_document (
		filename = filename,
		document_type = gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE,
		episode = episode,
		unlock_patient = False
	)
	doc.set_reviewed(technically_abnormal = False, clinically_relevant = True)

	return doc
#============================================================
class cVisualSoapTemplatePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of visual SOAP template."""

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		query = u"""
SELECT
	pk AS data,
	name_short AS list_label,
	name_sort AS field_label
FROM
	ref.paperwork_templates
WHERE
	fk_template_type = (SELECT pk FROM ref.form_types WHERE name = '%s') AND (
		name_long %%(fragment_condition)s
			OR
		name_short %%(fragment_condition)s
	)
ORDER BY list_label
LIMIT 15
"""	% gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
		mp.setThresholds(2, 3, 5)

		self.matcher = mp
		self.selection_only = True
	#--------------------------------------------------------
	def _data2instance(self):
		if self.GetData() is None:
			return None

		return gmForms.cFormTemplate(aPK_obj = self.GetData())
#============================================================
from Gnumed.wxGladeWidgets import wxgVisualSoapPresenterPnl

class cVisualSoapPresenterPnl(wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl):

	def __init__(self, *args, **kwargs):
		wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl.__init__(self, *args, **kwargs)
		self._SZR_soap = self.GetSizer()
		self.__bitmaps = []
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, document_folder=None, episodes=None, encounter=None):

		self.clear()
		if document_folder is not None:
			soap_docs = document_folder.get_visual_progress_notes(episodes = episodes, encounter = encounter)
			if len(soap_docs) > 0:
				for soap_doc in soap_docs:
					parts = soap_doc.parts
					if len(parts) == 0:
						continue
					part = parts[0]
					fname = part.export_to_file()
					if fname is None:
						continue

					# create bitmap
					img = gmGuiHelpers.file2scaled_image (
						filename = fname,
						height = 30
					)
					#bmp = wx.StaticBitmap(self, -1, img, style = wx.NO_BORDER)
					bmp = wx_genstatbmp.GenStaticBitmap(self, -1, img, style = wx.NO_BORDER)

					# create tooltip
					img = gmGuiHelpers.file2scaled_image (
						filename = fname,
						height = 150
					)
					tip = agw_stt.SuperToolTip (
						u'',
						bodyImage = img,
						header = _('Created: %s') % part['date_generated'].strftime('%Y %B %d').decode(gmI18N.get_encoding()),
						footer = gmTools.coalesce(part['doc_comment'], u'').strip()
					)
					tip.SetTopGradientColor('white')
					tip.SetMiddleGradientColor('white')
					tip.SetBottomGradientColor('white')
					tip.SetTarget(bmp)

					bmp.doc_part = part
					bmp.Bind(wx.EVT_LEFT_UP, self._on_bitmap_leftclicked)
					# FIXME: add context menu for Delete/Clone/Add/Configure
					self._SZR_soap.Add(bmp, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM | wx.EXPAND, 3)
					self.__bitmaps.append(bmp)

		self.GetParent().Layout()
	#--------------------------------------------------------
	def clear(self):
		while len(self._SZR_soap.GetChildren()) > 0:
			self._SZR_soap.Detach(0)
#		for child_idx in range(len(self._SZR_soap.GetChildren())):
#			self._SZR_soap.Detach(child_idx)
		for bmp in self.__bitmaps:
			bmp.Destroy()
		self.__bitmaps = []
	#--------------------------------------------------------
	def _on_bitmap_leftclicked(self, evt):
		wx.CallAfter (
			edit_visual_progress_note,
			doc_part = evt.GetEventObject().doc_part,
			discard_unmodified = True
		)
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
		splitter_width = self._splitter_main.GetSizeTuple()[0]
		self._splitter_main.SetSashPosition(splitter_width / 2, True)

		self._TCTRL_soap.Disable()
		self._BTN_save_soap.Disable()
		self._BTN_clear_soap.Disable()
	#-----------------------------------------------------
	def __reset_ui(self):
		self._LCTRL_problems.set_string_items()
		self._TCTRL_soap_problem.SetValue(_('<above, double-click problem to start entering SOAP note>'))
		self._TCTRL_soap.SetValue(u'')
		self._CHBOX_filter_by_problem.SetLabel(_('&Filter by problem'))
		self._TCTRL_journal.SetValue(u'')

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
			soap_cat = u'u',
			episode = self.__problem
		)

		if saved is None:
			return False

		self._TCTRL_soap.SetValue(u'')
		self.__refresh_journal()
		return True
	#-----------------------------------------------------
	def __perhaps_save_soap(self):
		if self._TCTRL_soap.GetValue().strip() == u'':
			return True
		if self.__problem is None:
			# FIXME: this could potentially lose input
			self._TCTRL_soap.SetValue(u'')
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
		emr = self.__curr_pat.get_emr()
		epis = emr.get_episodes(open_status = True)
		if len(epis) > 0:
			self._LCTRL_problems.set_string_items(items = [ u'%s%s' % (
				e['description'],
				gmTools.coalesce(e['health_issue'], u'', u' (%s)')
			) for e in epis ])
			self._LCTRL_problems.set_data(epis)
	#-----------------------------------------------------
	def __refresh_journal(self):
		self._TCTRL_journal.SetValue(u'')
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)

		if epi is not None:
			self._CHBOX_filter_by_problem.SetLabel(_('&Filter by problem %s%s%s') % (
				gmTools.u_left_double_angle_quote,
				epi['description'],
				gmTools.u_right_double_angle_quote
			))
			self._CHBOX_filter_by_problem.Refresh()

		if not self._CHBOX_filter_by_problem.IsChecked():
			self._TCTRL_journal.SetValue(self.__curr_pat.emr.format_summary(dob = self.__curr_pat['dob']))
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
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'health_issue_mod_db', receiver = self._on_episode_issue_mod_db)

		# synchronous signals
		self.__curr_pat.register_pre_selection_callback(callback = self._pre_selection_callback)
		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)
	#-----------------------------------------------------
	def _pre_selection_callback(self):
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
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__reset_ui)
	#-----------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
	#-----------------------------------------------------
	def _on_episode_issue_mod_db(self):
		wx.CallAfter(self._schedule_data_reget)
	#-----------------------------------------------------
	def _on_problem_activated(self, event):
		self.__perhaps_save_soap()
		epi = self._LCTRL_problems.get_selected_item_data(only_one = True)
		self._TCTRL_soap_problem.SetValue(_('Progress note: %s%s') % (
			epi['description'],
			gmTools.coalesce(epi['health_issue'], u'', u' (%s)')
		))
		self.__problem = epi
		self._TCTRL_soap.SetValue(u'')

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
		if epi_name == u'':
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
		if not gmEMRStructItems.delete_episode(episode = epi):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete problem. There is still clinical data recorded for it.'))
	#-----------------------------------------------------
	def _on_save_soap_button_pressed(self, event):
		event.Skip()
		self.__save_soap()
	#-----------------------------------------------------
	def _on_clear_soap_button_pressed(self, event):
		event.Skip()
		self._TCTRL_soap.SetValue(u'')
	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		self.__refresh_problem_list()
		self.__refresh_journal()
		self._TCTRL_soap.SetValue(u'')
		return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_select_narrative_from_episodes():
		pat = gmPersonSearch.ask_for_patient()
		gmPatSearchWidgets.set_active_patient(patient = pat)
		app = wx.PyWidgetTester(size = (200, 200))
		sels = select_narrative_from_episodes()
		print "selected:"
		for sel in sels:
			print sel
	#----------------------------------------
	def test_cSoapNoteExpandoEditAreaPnl():
		pat = gmPersonSearch.ask_for_patient()
		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cSoapNoteExpandoEditAreaPnl(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
	#----------------------------------------
	def test_cSoapPluginPnl():
		patient = gmPersonSearch.ask_for_patient()
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
	#test_select_narrative_from_episodes()
	test_cSoapNoteExpandoEditAreaPnl()
	#test_cSoapPluginPnl()

#============================================================
