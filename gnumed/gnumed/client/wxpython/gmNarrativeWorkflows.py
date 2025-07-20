"""GNUmed narrative workflows."""
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
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmHealthIssue
from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmNarrativeWidgets
from Gnumed.wxpython.gmPatSearchWidgets import set_active_patient

from Gnumed.exporters import gmPatientExporter


_log = logging.getLogger('gm.ui')

#============================================================
# narrative related widgets/functions
#------------------------------------------------------------
def edit_narrative(parent=None, narrative=None, single_entry=False):
	assert isinstance(narrative, gmClinNarrative.cNarrative), '<narrative> must be of type <cNarrative>'

	title = _('Editing progress note')
	if narrative['modified_by_raw'] == gmStaff.gmCurrentProvider()['db_user']:
		msg = _('Your original progress note:')
	else:
		msg = _('Original progress note by %s [%s]\n(will be notified of changes):') % (
			narrative['modified_by'],
			narrative['modified_by_raw']
		)
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	dlg = gmGuiHelpers.cMultilineTextEntryDlg (
		parent,
		-1,
		title = title,
		msg = msg,
		data = narrative.format(left_margin = ' ', fancy = True),
		text = narrative['narrative'].strip()
	)
	decision = dlg.ShowModal()
	val = dlg.value.strip()
	dlg.DestroyLater()
	if decision != wx.ID_SAVE:
		return False

	if val == '':
		return False

	if val == narrative['narrative'].strip():
		return False

	if narrative['modified_by_raw'] == gmStaff.gmCurrentProvider()['db_user']:
		narrative['narrative'] = val
		narrative.save_payload()
		return True

	q = _(
		'Original progress note written by someone else:\n'
		'\n'
		' %s (%s)\n'
		'\n'
		'Upon saving changes that person will be notified.\n'
		'\n'
		'Consider saving as a new progress note instead.'
	) % (
		narrative['modified_by_raw'],
		narrative['modified_by']
	)
	buttons = [
		{'label': _('Save changes'), 'default': True},
		{'label': _('Save new note')},
		{'label': _('Discard')}
	]
	dlg = gmGuiHelpers.c3ButtonQuestionDlg(parent = parent, caption = title, question = q, button_defs = buttons)
	decision = dlg.ShowModal()
	dlg.DestroyLater()
	if decision not in [wx.ID_YES, wx.ID_NO]:
		return False

	if decision == wx.ID_NO:
		# create new progress note within the same context as the original one
		gmClinNarrative.create_narrative_item (
			narrative = val,
			soap_cat = narrative['soap_cat'],
			episode_id = narrative['pk_episode'],
			encounter_id = narrative['pk_encounter']
		)
		return True

	# notify original provider
	msg = gmProviderInbox.create_inbox_message (
		staff = narrative.staff_id,
		message_type = _('Change notification'),
		message_category = 'administrative',
		subject = _('A progress note of yours has been edited.'),
		patient = narrative['pk_patient']
	)
	msg['data'] = _(
		'Original (by [%s]):\n'
		'%s\n'
		'\n'
		'Edited (by [%s]):\n'
		'%s'
	) % (
		narrative['modified_by'],
		narrative['narrative'].strip(),
		gmStaff.gmCurrentProvider()['short_alias'],
		val
	)
	msg.save()
	# notify /me about the staff member notification
	#gmProviderInbox.create_inbox_message (
	#	staff = curr_prov['pk_staff'],
	#	message_type = _('Privacy notice'),
	#	message_category = 'administrative',
	#	subject = _('%s: Staff member %s has been notified of your chart access.') % (prov, pat)
	#)
	# save narrative change
	narrative['narrative'] = val
	narrative.save()
	return True

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

	emr = patient.emr

	if encounters is None:
		all_encs_in_epi = emr.get_encounters(episodes = episodes, skip_empty = True)
		# nothing to do ?
		if len(all_encs_in_epi) == 0:
			return True
		encounters = gmEncounterWidgets.select_encounters (
			parent = parent,
			patient = patient,
			single_selection = False,
			encounters = all_encs_in_epi
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
					narr['modified_by'],
					gmSoapDefs.soap_cat2l10n[narr['soap_cat']],
					narr['narrative'].replace('\n', '/').replace('\r', '/')
				] for narr in notes
			]
		)

	if not selected_narr:
		return True

	# which encounter to move to
	enc2move2 = gmEncounterWidgets.select_encounters (
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

	emr = patient.emr
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
			data = item.format(left_margin = ' ', fancy = True),
			text = item['narrative']
		)
		decision = dlg.ShowModal()

		if decision != wx.ID_SAVE:
			return False

		val = dlg.value
		dlg.DestroyLater()
		if val.strip() == '':
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
				gmSoapDefs.soap_cat2l10n[narr['soap_cat']],
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

	search_term_dlg = wx.TextEntryDialog (
		parent,
		_('Enter (regex) term to search for across all EMRs:'),
		caption = _('Text search across all EMRs'),
		style = wx.OK | wx.CANCEL | wx.CENTRE
	)
	result = search_term_dlg.ShowModal()

	if result != wx.ID_OK:
		return

	wx.BeginBusyCursor()
	search_term = search_term_dlg.GetValue()
	search_term_dlg.DestroyLater()
	results = gmClinNarrative.search_text_across_emrs(search_term = search_term)
	wx.EndBusyCursor()

	if len(results) == 0:
		gmGuiHelpers.gm_show_info (
			_(
			'Nothing found for search term:\n'
			' "%s"'
			) % search_term,
			_('Search results')
		)
		return

	items = [ [
		gmPerson.cPerson(aPK_obj = r['pk_patient']).description_gender,
		r['narrative'],
		r['src_table']
	] for r in results ]

	selected_patient = gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Search results for [%s]') % search_term,
		choices = items,
		columns = [_('Patient'), _('Match'), _('Match location')],
		data = [ r['pk_patient'] for r in results ],
		single_selection = True,
		can_return_empty = False
	)

	if selected_patient is None:
		return

	wx.CallAfter(set_active_patient, patient = gmPerson.cPerson(aPK_obj = selected_patient))

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

	search_term_dlg = wx.TextEntryDialog (
		parent,
		_('Enter search term:'),
		caption = _('Text search of entire EMR of active patient'),
		style = wx.OK | wx.CANCEL | wx.CENTRE
	)
	result = search_term_dlg.ShowModal()

	if result != wx.ID_OK:
		search_term_dlg.DestroyLater()
		return False

	wx.BeginBusyCursor()
	val = search_term_dlg.GetValue()
	search_term_dlg.DestroyLater()
	emr = patient.emr
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

	txt = ''
	for row in rows:
		txt += '%s: %s\n' % (
			row['soap_cat'],
			row['narrative']
		)

		txt += ' %s: %s - %s %s\n' % (
			_('Encounter'),
			row['encounter_started'].strftime('%x %H:%M'),
			row['encounter_ended'].strftime('%H:%M'),
			row['encounter_type']
		)
		txt += ' %s: %s\n' % (
			_('Episode'),
			row['episode']
		)
		txt += ' %s: %s\n\n' % (
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
		caption = _('Search results for [%s]') % val,
		style = wx.OK | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.DestroyLater()

	return True

#------------------------------------------------------------
def export_narrative_for_medistar_import(parent=None, soap_cats='soapu', encounter=None):

	# sanity checks
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot export EMR for Medistar. No active patient.'))
		return False

	if encounter is None:
		encounter = pat.emr.active_encounter

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# get file name
	aWildcard = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
		# FIXME: make configurable
	aDefDir = gmTools.gmPaths().user_work_dir
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
		style = wx.FD_SAVE
	)
	choice = dlg.ShowModal()
	fname = dlg.GetPath()
	dlg.DestroyLater()
	if choice != wx.ID_OK:
		return False

	wx.BeginBusyCursor()
	_log.debug('exporting encounter for medistar import to [%s]', fname)
	exporter = gmPatientExporter.cMedistarSOAPExporter(patient = pat)
	successful, fname = exporter.save_to_file (
		filename = fname,
		encounter = encounter,
		soap_cats = 'soapu',
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
def select_narrative(parent=None, soap_cats=None, msg=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if soap_cats is None:
		soap_cats = 'soapu'
	soap_cats = list(soap_cats)
	i18n_soap_cats = [ gmSoapDefs.soap_cat2l10n[cat].upper() for cat in soap_cats ]

	if msg is None:
		msg = _('Pick the [%s] narrative you want to use.') % '/'.join(i18n_soap_cats)

	#-----------------------------------------------
	def get_tooltip(soap):
		return soap.format(fancy = True, width = 60)
	#-----------------------------------------------
	def refresh(lctrl):
		lctrl.secondary_sort_column = 0
		soap = emr.get_clin_narrative(soap_cats = soap_cats)
		lctrl.set_string_items ([ [
			s['date'].strftime('%Y %m %d'),
			s['modified_by'],
			gmSoapDefs.soap_cat2l10n[s['soap_cat']],
			s['narrative'],
			s['episode'],
			s['health_issue']
		] for s in soap ])
		lctrl.set_data(soap)
	#-----------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Picking [%s] narrative') % ('/'.join(i18n_soap_cats)),
		columns = [_('When'), _('Who'), _('Type'), _('Entry'), _('Episode'), _('Issue')],
		single_selection = False,
		can_return_empty = False,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
	)

#------------------------------------------------------------
def select_narrative_by_issue(parent=None, soap_cats=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	# not useful if you think about it:
#	issues = [ i for i in emr.health_issues ]
#	if len(issues) == 0:
#		gmDispatcher.send(signal = 'statustext', msg = _('No progress notes found.'))
#		return []

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if soap_cats is None:
		soap_cats = 'soapu'
	soap_cats = list(soap_cats)
	i18n_soap_cats = [ gmSoapDefs.soap_cat2l10n[cat].upper() for cat in soap_cats ]

	selected_soap = {}
	#selected_narrative_pks = []

	#-----------------------------------------------
	def get_soap_tooltip(soap):
		return soap.format(fancy = True, width = 60)
	#-----------------------------------------------
	def pick_soap_from_issue(issue):

		if issue is None:
			return False

		narr_for_issue = emr.get_clin_narrative(issues = [issue['pk_health_issue']], soap_cats = soap_cats)

		if len(narr_for_issue) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for this health issue.'))
			return True

		selected_narr = gmListWidgets.get_choices_from_list (
			parent = parent,
			msg = _('Pick the [%s] narrative you want to include in the report.') % '/'.join(i18n_soap_cats),
			caption = _('Picking [%s] from %s%s%s') % (
				'/'.join(i18n_soap_cats),
				gmTools.u_left_double_angle_quote,
				issue['description'],
				gmTools.u_right_double_angle_quote
			),
			columns = [_('When'), _('Who'), _('Type'), _('Entry')],
			choices = [ [
				narr['date'].strftime('%Y %b %d  %H:%M'),
				narr['modified_by'],
				gmSoapDefs.soap_cat2l10n[narr['soap_cat']],
				narr['narrative'].replace('\n', '//').replace('\r', '//')
			] for narr in narr_for_issue ],
			data = narr_for_issue,
			#selections=None,
			#edit_callback=None,
			single_selection = False,
			can_return_empty = False,
			list_tooltip_callback = get_soap_tooltip
		)

		if selected_narr is None:
			return True

		for narr in selected_narr:
			selected_soap[narr['pk_narrative']] = narr

		return True
	#-----------------------------------------------
	def edit_issue(issue):
		return gmEMRStructWidgets.edit_health_issue(parent = parent, issue = issue)
	#-----------------------------------------------
	def refresh_issues(lctrl):
		#issues = [ i for i in emr.health_issues ]
		issues = emr.health_issues
		lctrl.set_string_items ([ [
				gmTools.bool2subst(i['is_confidential'], _('!! CONFIDENTIAL !!'), ''),
				i['description'],
				gmTools.bool2subst(i['is_active'], _('active'), _('inactive'))
			] for i in issues
		])
		lctrl.set_data(issues)
	#-----------------------------------------------
	def get_issue_tooltip(issue):
		return issue.format (
			patient = pat,
			with_encounters = False,
			with_medications = False,
			with_hospital_stays = False,
			with_procedures = False,
			with_family_history = False,
			with_documents = False,
			with_tests = False,
			with_vaccinations = False
		)
	#-----------------------------------------------
	#selected_episode_pks = []

	issues_picked_from = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\n Select the issue you want to report on.'),
		caption = _('Picking [%s] from health issues') % '/'.join(i18n_soap_cats),
		columns = [_('Privacy'), _('Issue'), _('Status')],
		edit_callback = edit_issue,
		refresh_callback = refresh_issues,
		single_selection = True,
		can_return_empty = True,
		ignore_OK_button = False,
		left_extra_button = (
			_('&Pick notes'),
			_('Pick [%s] entries from selected health issue') % '/'.join(i18n_soap_cats),
			pick_soap_from_issue
		),
		list_tooltip_callback = get_issue_tooltip
	)

	if issues_picked_from is None:
		return []

	return selected_soap.values()

#	selection_idxs = []
#	for idx in range(len(all_epis)):
#		if all_epis[idx]['pk_episode'] in selected_episode_pks:
#			selection_idxs.append(idx)
#	if len(selection_idxs) != 0:
#		dlg.set_selections(selections = selection_idxs)

#------------------------------------------------------------
def select_narrative_by_episode(parent=None, soap_cats=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	all_epis = [ epi for epi in emr.get_episodes(order_by = 'description') if epi.has_narrative ]
	if len(all_epis) == 0:
		gmDispatcher.send(signal = 'statustext', msg = _('No episodes with progress notes found.'))
		return []

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if soap_cats is None:
		soap_cats = 'soapu'
	soap_cats = list(soap_cats)
	i18n_soap_cats = [ gmSoapDefs.soap_cat2l10n[cat].upper() for cat in soap_cats ]

	selected_soap = {}
	#selected_narrative_pks = []

	#-----------------------------------------------
	def get_soap_tooltip(soap):
		return soap.format(fancy = True, width = 60)
	#-----------------------------------------------
	def pick_soap_from_episode(episode):

		if episode is None:
			return False

		narr_for_epi = emr.get_clin_narrative(episodes = [episode['pk_episode']], soap_cats = soap_cats)

		if len(narr_for_epi) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for selected episode.'))
			return True

		selected_narr = gmListWidgets.get_choices_from_list (
			parent = parent,
			msg = _('Pick the [%s] narrative you want to include in the report.') % '/'.join(i18n_soap_cats),
			caption = _('Picking [%s] from %s%s%s') % (
				'/'.join(i18n_soap_cats),
				gmTools.u_left_double_angle_quote,
				episode['description'],
				gmTools.u_right_double_angle_quote
			),
			columns = [_('When'), _('Who'), _('Type'), _('Entry')],
			choices = [ [
				narr['date'].strftime('%Y %b %d  %H:%M'),
				narr['modified_by'],
				gmSoapDefs.soap_cat2l10n[narr['soap_cat']],
				narr['narrative'].replace('\n', '//').replace('\r', '//')
			] for narr in narr_for_epi ],
			data = narr_for_epi,
			#selections=None,
			#edit_callback=None,
			single_selection = False,
			can_return_empty = False,
			list_tooltip_callback = get_soap_tooltip
		)

		if selected_narr is None:
			return True

		for narr in selected_narr:
			selected_soap[narr['pk_narrative']] = narr

		return True

#		selection_idxs = []
#		for idx in range(len(narr_for_epi)):
#			if narr_for_epi[idx]['pk_narrative'] in selected_narrative_pks:
#				selection_idxs.append(idx)
#		if len(selection_idxs) != 0:
#			dlg.set_selections(selections = selection_idxs)

#		selected_narrative_pks = [ i['pk_narrative'] for i in selected_narr ]
#		for narr in selected_narr:
#			selected_soap[narr['pk_narrative']] = narr
#
#		print "before returning from picking soap"
#
#		return True
#	#-----------------------------------------------
	def edit_episode(episode):
		return gmEMRStructWidgets.edit_episode(parent = parent, episode = episode)
	#-----------------------------------------------
	def refresh_episodes(lctrl):
		all_epis = [ epi for epi in emr.get_episodes(order_by = 'description') if epi.has_narrative ]
		lctrl.set_string_items ([ [
				'%s%s' % (e['description'], gmTools.coalesce(e['health_issue'], '', ' (%s)')),
				gmTools.bool2subst(e['episode_open'], _('open'), _('closed'))
			] for e in all_epis
		])
		lctrl.set_data(all_epis)
	#-----------------------------------------------
	def get_episode_tooltip(episode):
		return episode.format (
			patient = pat,
			with_encounters = False,
			with_documents = False,
			with_hospital_stays = False,
			with_procedures = False,
			with_family_history = False,
			with_tests = False,
			with_vaccinations = False
		)
	#-----------------------------------------------
	#selected_episode_pks = []

	epis_picked_from = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\n Select the episode you want to report on.'),
		caption = _('Picking [%s] from episodes') % '/'.join(i18n_soap_cats),
		columns = [_('Episode'), _('Status')],
		edit_callback = edit_episode,
		refresh_callback = refresh_episodes,
		single_selection = True,
		can_return_empty = True,
		ignore_OK_button = False,
		left_extra_button = (
			_('&Pick notes'),
			_('Pick [%s] entries from selected episode') % '/'.join(i18n_soap_cats),
			pick_soap_from_episode
		),
		list_tooltip_callback = get_episode_tooltip
	)

	if epis_picked_from is None:
		return []

	return selected_soap.values()

#	selection_idxs = []
#	for idx in range(len(all_epis)):
#		if all_epis[idx]['pk_episode'] in selected_episode_pks:
#			selection_idxs.append(idx)
#	if len(selection_idxs) != 0:
#		dlg.set_selections(selections = selection_idxs)

#------------------------------------------------------------
def select_narrative_from_episodes(parent=None, soap_cats=None):
	"""soap_cats needs to be a list"""

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	selected_soap = {}
	selected_issue_pks = []
	selected_episode_pks = []
	selected_narrative_pks = []

	while 1:
		# 1) select health issues to select episodes from
		all_issues = emr.get_health_issues()
		all_issues.insert(0, gmHealthIssue.get_dummy_health_issue())
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
		dlg.DestroyLater()

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
			dlg.DestroyLater()

			if btn_pressed == wx.ID_CANCEL:
				break

			selected_episode_pks = [ i['pk_episode'] for i in selected_epis ]

			# 3) select narrative corresponding to the above constraints
			all_narr = emr.get_clin_narrative(episodes = selected_episode_pks, soap_cats = soap_cats)

			if len(all_narr) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for selected episodes.'))
				continue

			dlg = gmNarrativeWidgets.cNarrativeListSelectorDlg (
				parent = parent,
				id = -1,
				narrative = all_narr,
				msg = _(
					'\n This is the narrative (type %s) for the chosen episodes.\n\n'
					' Now, mark the entries you want to include in your report.\n'
				) % '/'.join([ gmSoapDefs.soap_cat2l10n[cat] for cat in gmTools.coalesce(soap_cats, list('soapu')) ])
			)
			selection_idxs = []
			for idx in range(len(all_narr)):
				if all_narr[idx]['pk_narrative'] in selected_narrative_pks:
					selection_idxs.append(idx)
			if len(selection_idxs) != 0:
				dlg.set_selections(selections = selection_idxs)
			btn_pressed = dlg.ShowModal()
			selected_narr = dlg.get_selected_item_data()
			dlg.DestroyLater()

			if btn_pressed == wx.ID_CANCEL:
				continue

			selected_narrative_pks = [ i['pk_narrative'] for i in selected_narr ]
			for narr in selected_narr:
				selected_soap[narr['pk_narrative']] = narr

#------------------------------------------------------------
def generate_failsafe_narrative(pk_patient:int=None, max_width:int=80, eol:str=None) -> str|list:
	if not pk_patient:
		pk_patient = gmPerson.gmCurrentPatient().ID
	lines, footer = gmFormWidgets.generate_failsafe_form_wrapper (
		pk_patient = pk_patient,
		title = _('Progress Notes -- %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d'),
		max_width = max_width
	)
	lines.append('')
	lines.append('#' + '-' * (max_width - 2) + '#')
	lines.extend(gmClinNarrative.format_narrative_for_failsafe_output (
		pk_patient = pk_patient,
		max_width = max_width
	))
	lines.append('')
	lines.extend(footer)
	if eol:
		return eol.join(lines)

	return lines

#------------------------------------------------------------
def save_failsafe_narrative(pk_patient:int=None, max_width:int=80, filename:str=None) -> str:
	if not filename:
		filename = gmTools.get_unique_filename()
	with open(filename, 'w', encoding = 'utf8') as narr_file:
		narr_file.write(generate_failsafe_narrative(pk_patient = pk_patient, max_width = max_width, eol = '\n'))
	return filename

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPersonSearch

	#----------------------------------------
	def test_select_narrative_from_episodes():
		pat = gmPersonSearch.ask_for_patient()
		set_active_patient(patient = pat)
		#app = wx.PyWidgetTester(size = (200, 200))
		sels = select_narrative_from_episodes()
		print("selected:")
		for sel in sels:
			print(sel)
	#----------------------------------------
	def test_select_narrative():
		pat = gmPersonSearch.ask_for_patient()
		set_active_patient(patient = pat)
		#app = wx.PyWidgetTester(size = (200, 200))
		sels = select_narrative(parent=None, soap_cats = None)
		print("selected:")
		for sel in sels:
			print(sel)
	#----------------------------------------
	#test_select_narrative_from_episodes()
	test_select_narrative()
