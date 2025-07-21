"""GNUmed patient overview widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmHealthIssue
from Gnumed.business import gmFamilyHistory
from Gnumed.business import gmVaccination
from Gnumed.business import gmDocuments
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmExternalCare
from Gnumed.business import gmAutoHints
from Gnumed.business import gmMedication
from Gnumed.business import gmPerformedProcedure
from Gnumed.business import gmHospitalStay
from Gnumed.business import gmEncounter
from Gnumed.business import gmEpisode

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmContactWidgets
from Gnumed.wxpython import gmSubstanceIntakeWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmVaccWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmPregWidgets
from Gnumed.wxpython import gmHospitalStayWidgets
from Gnumed.wxpython import gmProcedureWidgets
from Gnumed.wxpython import gmFamilyHistoryWidgets


_log = logging.getLogger('gm.patient')
#============================================================
from Gnumed.wxGladeWidgets import wxgPatientOverviewPnl

class cPatientOverviewPnl(wxgPatientOverviewPnl.wxgPatientOverviewPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, *args, **kwargs):
		wxgPatientOverviewPnl.wxgPatientOverviewPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):

		#self._LCTRL_history.debug = u'LCTRL_history_sizing'

		# left
		self._LCTRL_identity.set_columns(columns = [''])
		self._LCTRL_identity.item_tooltip_callback = self._calc_identity_item_tooltip
		self._LCTRL_identity.activate_callback = self._on_identity_item_activated

		self._LCTRL_contacts.set_columns(columns = [''])
		self._LCTRL_contacts.item_tooltip_callback = self._calc_contacts_list_item_tooltip
		self._LCTRL_contacts.activate_callback = self._on_contacts_item_activated

		self._LCTRL_encounters.set_columns(columns = [''])
		self._LCTRL_encounters.item_tooltip_callback = self._calc_encounters_list_item_tooltip
		self._LCTRL_encounters.activate_callback = self._on_encounter_activated

		# middle
		self._LCTRL_meds.set_columns(columns = [''])
		self._LCTRL_meds.item_tooltip_callback = self._calc_meds_list_item_tooltip
		self._LCTRL_meds.activate_callback = self._on_meds_item_activated

		if gmGuiHelpers.is_probably_dark_theme():
			self._LCTRL_problems.SetBackgroundColour(wx.Colour(0, 0, 120)) # blue
		else:
			self._LCTRL_problems.SetBackgroundColour(wx.Colour(255, 238, 180)) # orig light yellow
		self._LCTRL_problems.set_columns(columns = [''])
		self._LCTRL_problems.item_tooltip_callback = self._calc_problem_list_item_tooltip
		self._LCTRL_problems.activate_callback = self._on_problem_activated

		self._LCTRL_history.set_columns(columns = [''])
		self._LCTRL_history.item_tooltip_callback = self._calc_history_list_item_tooltip
		self._LCTRL_history.activate_callback = self._on_history_item_activated

		# right hand side
		self._LCTRL_inbox.set_columns(columns = [''])
		self._LCTRL_inbox.item_tooltip_callback = self._calc_inbox_item_tooltip
		self._LCTRL_inbox.activate_callback = self._on_inbox_item_activated

		self._LCTRL_results.set_columns(columns = [''])
		self._LCTRL_results.item_tooltip_callback = self._calc_results_list_item_tooltip
		self._LCTRL_results.activate_callback = self._on_result_activated

		self._LCTRL_documents.set_columns(columns = [''])
		self._LCTRL_documents.item_tooltip_callback = self._calc_documents_list_item_tooltip
		self._LCTRL_documents.activate_callback = self._on_document_activated

	#--------------------------------------------------------
	def __reset_ui_content(self):
		self._LCTRL_identity.set_string_items()
		self._LCTRL_contacts.set_string_items()
		self._LCTRL_encounters.set_string_items()

		self._LCTRL_problems.set_string_items()
		self._LCTRL_meds.set_string_items()
		self._LCTRL_history.set_string_items()

		self._LCTRL_inbox.set_string_items()
		self._LCTRL_results.set_string_items()
		self._LCTRL_documents.set_string_items()

	#-----------------------------------------------------
	# event handling
	#-----------------------------------------------------
	def __register_interests(self):
		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)

		# generic database change signal
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

		# database change signals
		# no signal for external IDs yet
		# no signal for address yet
		##gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)
		##gmDispatcher.connect(signal = u'current_encounter_switched', receiver = self._on_current_encounter_switched)

		# doesn't have pk_identity:
		gmDispatcher.connect(signal = 'clin.reviewed_test_results_mod_db', receiver = self._on_post_patient_selection)

		# synchronous signals
#		self.__pat.register_before_switching_from_patient_callback(callback = self._before_switching_from_patient_callback)
#		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		# only empty out here, do NOT access the patient
		# or else we will access the old patient while it
		# may not be valid anymore ...
		self.__reset_ui_content()

	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):

		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return True

		if kwds['pk_identity'] != pat.ID:
			return True

		if kwds['table'] == 'dem.identity':
			if kwds['operation'] != 'UPDATE':
				return True

		if kwds['table'] in [
			'blobs.doc_med',
			'clin.episode',
			'clin.health_issue',
			'clin.suppressed_hint',
			'clin.substance_intake',
			'clin.hospital_stay',
			'clin.procedure',
			'clin.vaccination',
			'clin.family_history',
			'clin.test_result',
			'clin.export_item',
			'clin.external_care',
			'dem.identity',
			'dem.names',
			'dem.lnk_identity2comm',
			'dem.lnk_job2person',
			'dem.message_inbox',
			'ref.auto_hint'
		]:
			self._schedule_data_reget()
			return True

		return True

	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			self.__reset_ui_content()
			return True

		self.__refresh_identity(patient = pat)
		self.__refresh_contacts(patient = pat)
		self.__refresh_encounters(patient = pat)

		self.__refresh_problems(patient = pat)
		self.__refresh_meds(patient = pat)
		self.__refresh_history(patient = pat)

		self.__refresh_inbox(patient = pat)
		self.__refresh_results(patient = pat)
		self.__refresh_documents(patient = pat)

		return True

	#-----------------------------------------------------
	# internal helpers
	#-----------------------------------------------------
	def __refresh_results(self, patient=None):

		emr = patient.emr
		most_recent = emr.get_most_recent_results_for_patient()
		if len(most_recent) == 0:
			self._LCTRL_results.set_string_items(items = [])
			self._LCTRL_results.set_data(data = [])
			return
		most_recent = most_recent[0]

		list_items = []
		list_data = []
		now = gmDateTime.pydt_now_here()

		list_items.append(_('Most recent lab work: %s ago (%s)') % (
			gmDateTime.format_interval_medically(now - most_recent['clin_when']),
			most_recent['clin_when'].strftime('%Y %b %d')
		))
		list_data.append(most_recent)

		unsigned = emr.get_unsigned_results(order_by = "(trim(coalesce(abnormality_indicator), '') <> '') DESC NULLS LAST, unified_abbrev")
		no_of_reds = 0
		for result in unsigned:
			if result['abnormality_indicator'] is not None:
				if result['abnormality_indicator'].strip() != '':
					no_of_reds += 1
			list_items.append(_('%s %s%s%s (%s ago, %s)') % (
				result['unified_abbrev'],
				result['unified_val'],
				gmTools.coalesce(result['val_unit'], '', ' %s'),
				gmTools.coalesce(result['abnormality_indicator'], '', ' %s'),
				gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - result['clin_when']),
				gmTools.u_writing_hand
			))
			list_data.append(result)

		self._LCTRL_results.set_string_items(items = list_items)
		self._LCTRL_results.set_data(data = list_data)

		if no_of_reds > 0:
			for idx in range(1, no_of_reds + 1):
				self._LCTRL_results.SetItemTextColour(idx, wx.Colour('RED'))

	#-----------------------------------------------------
	def _calc_results_list_item_tooltip(self, data):
		return data.format()

	#-----------------------------------------------------
	def _on_result_activated(self, event):
#		data = self._LCTRL_inbox.get_selected_item_data(only_one = True)
#
#		if data is not None:
#			# <ctrl> down ?
#			if wx.GetKeyState(wx.WXK_CONTROL):
#				if isinstance(data, gmProviderInbox.cInboxMessage):
#					xxxxxxxxx
		gmDispatcher.send(signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return

	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_inbox(self, patient=None):
		list_items = []
		list_data = []
		highlight_list = []
		failed_list = []
		line_idx = -1

		overdue_messages = patient.overdue_messages
		if len(overdue_messages) > 0:
			highlight_list.extend(range(len(overdue_messages)))
		for msg in overdue_messages:
			line_idx += 1
			list_items.append(_('overdue %s: %s') % (
				gmDateTime.format_interval_medically(msg['interval_due']),
				gmTools.coalesce(msg['comment'], '?')
			))
			list_data.append(msg)

		for msg in patient.get_messages(order_by = 'due_date NULLS LAST, importance DESC, received_when DESC'):
			# already displayed above ?
			if msg['is_overdue']:
				continue
			# not relevant anymore ?
			if msg['is_expired']:
				continue
			line_idx += 1
			if msg['due_date'] is None:
				label = '%s%s' % (
					msg['l10n_type'],
					gmTools.coalesce(msg['comment'], '', ': %s')
				)
			else:
				label = _('due in %s%s') % (
					gmDateTime.format_interval_medically(msg['interval_due']),
					gmTools.coalesce(msg['comment'], '', ': %s')
				)
			list_items.append(label)
			list_data.append(msg)

		pk_enc = patient.emr.active_encounter['pk_encounter']
		for hint in patient._get_dynamic_hints(pk_encounter = pk_enc):
			line_idx += 1
			list_items.append(hint['title'])
			list_data.append(hint)
			if hint.failed:
				failed_list.append(line_idx)
				continue
			if hint['highlight_as_priority']:
				highlight_list.append(line_idx)

		hints = patient.suppressed_hints
		if len(hints) > 0:
			list_items.append((_("suppr'd (%s):") % len(hints)) + ' ' + ','.join([h['title'][:7] + gmTools.u_ellipsis for h in hints]))
			list_data.append(_('Suppressed hints:\n') + '\n'.join(['%s: %s' % (hints.index(h) + 1, h['title']) for h in hints]))

		self._LCTRL_inbox.set_string_items(items = list_items)
		self._LCTRL_inbox.set_data(data = list_data)

		for idx in highlight_list:
			self._LCTRL_inbox.SetItemTextColour(idx, wx.Colour('RED'))

		for idx in failed_list:
			self._LCTRL_inbox.SetItemTextColour(idx, wx.Colour('ORANGE'))

	#-----------------------------------------------------
	def _calc_inbox_item_tooltip(self, data):
		if isinstance(data, gmProviderInbox.cInboxMessage):
			return data.format()

		if isinstance(data, gmAutoHints.cDynamicHint):
			return '%s\n\n%s%s\n\n%s          %s' % (
				data['title'],
				gmTools.wrap(data['hint'], width = 50),
				gmTools.wrap(gmTools.coalesce(data['recommendation'], '', '\n\n%s'), width =  50),
				gmTools.wrap(gmTools.coalesce(data['url'], '', '%s\n\n'), width = 50),
				data['source']
			)

		if isinstance(data, type('')):
			return data

		return None

	#-----------------------------------------------------
	def _on_inbox_item_activated(self, event):

		data = self._LCTRL_inbox.get_selected_item_data(only_one = True)

		# if it is a dynamic hint open the URL for that
		if isinstance(data, gmAutoHints.cDynamicHint):
			if data['url'] is not None:
				gmNetworkTools.open_url_in_browser(data['url'])
			return

		# holding down <CTRL> when double-clicking an inbox
		# item indicates the desire to delete it
		# <ctrl> down ?
		if wx.GetKeyState(wx.WXK_CONTROL):
			# better safe than sorry: can only delete real inbox items
			if data is None:
				return
			if not isinstance(data, gmProviderInbox.cInboxMessage):
				return
			delete_it = gmGuiHelpers.gm_show_question (
				question = _('Do you really want to\ndelete this inbox message ?'),
				title = _('Deleting inbox message')
			)
			if not delete_it:
				return
			gmProviderInbox.delete_inbox_message(inbox_message = data['pk_inbox_message'])
			return

		if data is None:
			gmDispatcher.send(signal = 'display_widget', name = 'gmProviderInboxPlugin')
			return

		if not isinstance(data, gmProviderInbox.cInboxMessage):
			gmDispatcher.send(signal = 'display_widget', name = 'gmProviderInboxPlugin')
			return

		gmDispatcher.send(signal = 'display_widget', name = 'gmProviderInboxPlugin', filter_by_active_patient = True)
		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_documents(self, patient=None):

		list_items = []
		list_data = []

		# export area items
		item_count = len(patient.export_area.items)
		if item_count == 1:
			list_items.append(_('Export area: 1 item'))
			list_data.append('')
		if item_count > 1:
			list_items.append(_('Export area: %s items') % item_count)
			list_data.append('')

		doc_folder = patient.get_document_folder()

		# unsigned docs first
		docs = doc_folder.get_unsigned_documents()
		no_of_unsigned = len(docs)
		for doc in docs:
			list_items.append('%s %s (%s)' % (
				doc['clin_when'].strftime('%m/%Y'),
				doc['l10n_type'],
				gmTools.u_writing_hand
			))
			list_data.append(doc)

		# other, signed docs second
		docs = doc_folder.get_documents(order_by = 'clin_when DESC', exclude_unsigned = True)
		for doc in docs[:5]:
			list_items.append('%s %s' % (
				doc['clin_when'].strftime('%m/%Y'),
				doc['l10n_type']
			))
			list_data.append(doc)
		if len(docs) > 5:
			list_items.append(_('%s %s more not shown %s') % (
				gmTools.u_ellipsis,
				len(docs) - 5,
				gmTools.u_ellipsis
			))
			list_data.append('')

		self._LCTRL_documents.set_string_items(items = list_items)
		self._LCTRL_documents.set_data(data = list_data)

		if no_of_unsigned > 0:
			start_idx = 0
			if item_count > 0:
				start_idx = 1
			end_idx = no_of_unsigned + start_idx
			for idx in range(start_idx, end_idx):
				self._LCTRL_documents.SetItemTextColour(idx, wx.Colour('RED'))
	#-----------------------------------------------------
	def _calc_documents_list_item_tooltip(self, data):
		if isinstance(data, gmDocuments.cDocument):
			return data.format()

		return None
	#-----------------------------------------------------
	def _on_document_activated(self, event):
		data = self._LCTRL_documents.get_selected_item_data(only_one = True)

		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if isinstance(data, gmDocuments.cDocument):
					if len(data.parts) > 0:
						gmDocumentWidgets.display_document_part(parent = self, part = data.parts[0])
					else:
						gmDocumentWidgets.review_document(parent = self, document = data)
					return

		gmDispatcher.send(signal = 'display_widget', name = 'gmShowMedDocs')
		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_encounters(self, patient=None):

		emr = patient.emr

		list_items = []
		list_data = []

		is_waiting = False
		wlist = patient.get_waiting_list_entry()
		if len(wlist) > 0:
			is_waiting = True
			list_items.append(_('Currently %s entries in waiting list') % len(wlist))
			tt = []
			for w in wlist:
				tt.append('%s %s%s%s' % (
					gmTools.u_triangular_bullet,
					gmDateTime.format_interval_medically(w['waiting_time']),
					gmTools.coalesce(w['waiting_zone'], '', ' in "%s"'),
					gmTools.coalesce(w['comment'], '', ': %s')
				))
			if len(tt) > 0:
				tt = '\n'.join(tt)
			else:
				tt = None
			list_data.append({'wlist': tt})

		first = emr.get_first_encounter()
		if first is not None:
			list_items.append (
				_('first (in GMd): %s, %s') % (
					first['started'].strftime('%Y %b %d'),
					first['l10n_type']
				)
			)
			list_data.append(first)

		last = emr.get_last_but_one_encounter()
		if last is not None:
			list_items.append (
				_('last: %s, %s') % (
					last['started'].strftime('%Y %b %d'),
					last['l10n_type']
				)
			)
			list_data.append(last)

		encs = emr.get_encounter_stats_by_type()
		for enc in encs:
			item = ' %s x %s' % (enc['frequency'], enc['l10n_type'])
			list_items.append(item)
			list_data.append(item)

		stays = emr.get_hospital_stay_stats_by_hospital()
		for stay in stays:
			item = ' %s x %s' % (
				stay['frequency'],
				stay['hospital']
			)
			list_items.append(item)
			list_data.append({'stay': item})

		self._LCTRL_encounters.set_string_items(items = list_items)
		self._LCTRL_encounters.set_data(data = list_data)
		if is_waiting:
			self._LCTRL_encounters.SetItemTextColour(0, wx.Colour('RED'))

	#-----------------------------------------------------
	def _calc_encounters_list_item_tooltip(self, data):
		if isinstance(data, gmEncounter.cEncounter):
			return data.format (
				with_vaccinations = False,
				with_tests = False,
				with_docs = False,
				with_co_encountlet_hints = True,
				with_rfe_aoe = True
			)

		if type(data) is dict:
			key, val = list(data.items())[0]
			if key == 'wlist':
				return val

			if key == 'stay':
				return None

		return data
	#-----------------------------------------------------
	def _on_encounter_activated(self, event):
		data = self._LCTRL_encounters.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if isinstance(data, gmEncounter.cEncounter):
					gmEncounterWidgets.edit_encounter(parent = self, encounter = data)
					return

		if type(data) is dict:
			key, val = list(data.items())[0]
			if key == 'wlist':
				gmDispatcher.send(signal = 'display_widget', name = 'gmWaitingListPlugin')
				return
			if key == 'stay':
				wx.CallAfter(gmHospitalStayWidgets.manage_hospital_stays, parent = self)
				return

		wx.CallAfter(gmEncounterWidgets.manage_encounters, parent = self, ignore_OK_button = False)

	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_history(self, patient=None):
		emr = patient.emr

		sort_key_list = []
		date_format4sorting = '%Y %m %d %H %M %S'
		now = gmDateTime.pydt_now_here()
		data = {}

		# undated entries
		# pregnancy
		edc = emr.EDC
		if edc is not None:
			sort_key = '99999 edc'
			if emr.EDC_is_fishy:
				label = _('EDC (!?!): %s') % edc.strftime('%Y %b %d')
				tt = _(
					'The Expected Date of Confinement is rather questionable.\n'
					'\n'
					'Please check patient age, patient gender, time until/since EDC.'
				)
			else:
				label = _('EDC: %s') % edc.strftime('%Y %b %d')
				tt = ''
			sort_key_list.append(sort_key)
			data[sort_key] = [label, tt]

		# family history
		fhxs = emr.get_family_history()
		for fhx in fhxs:
			sort_key = '99998 %s::%s' % (fhx['l10n_relation'], fhx['pk_family_history'])
			sort_key_list.append(sort_key)
			#fhx['when_known_to_patient'].strftime('%Y %m %d %H %M %S')
			label = '%s%s: %s' % (fhx['l10n_relation'], gmTools.coalesce(fhx['age_noted'], '', ' (@ %s)'), fhx['condition'])
			data[sort_key] = [label, fhx]
		del fhxs

		# dated entries
		issues = [
			i for i in emr.get_health_issues()
			if ((i['clinically_relevant'] is False) or (i['is_active'] is False))
		]
		for issue in issues:
			last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
			linked_encounter = issue.encounter
			when_candidates = [issue['modified_when'], linked_encounter['last_affirmed']]
			if last_encounter is not None:
				when_candidates.append(last_encounter['last_affirmed'])
			if (patient['dob'] is not None) and (issue['age_noted'] is not None):
				when_candidates.append(patient['dob'] + issue['age_noted'])
			if issue['is_active']:
				# sort active issues by time of most recent clinical access, which
				# means the most recent of:
				# issue.modified_when
				# last_encounter.last_affirmed
				# linked_encounter.last_affirmed
				# dob + age
				relevant_date = max(when_candidates)
			else:
				# sort IN-active issues by best guess of real clinical start
				# means either:
				# - dob + age
				# or the earliest of:
				# - issue.modified_when
				# - last_encounter.last_affirmed
				# - linked_encounter.last_affirmed
				if (patient['dob'] is not None) and (issue['age_noted'] is not None):
					relevant_date = patient['dob'] + issue['age_noted']
				else:
					relevant_date = min(when_candidates)
			sort_key = '%s::%s' % (relevant_date.strftime(date_format4sorting), issue['pk_health_issue'])
			relevant_date_str = relevant_date.strftime('%Y %b')
			if issue['age_noted'] is None:
				age = _(' (entered %s ago)') % gmDateTime.format_interval_medically(now - issue.encounter['started'])
			else:
				age = ' (@ %s)' % gmDateTime.format_interval_medically(issue['age_noted'])
			sort_key_list.append(sort_key)
			data[sort_key] = ['%s %s%s' % (relevant_date_str, issue['description'], age), issue]
		del issues

		stays = emr.get_hospital_stays()
		for stay in stays:
			sort_key = '%s::%s' % (stay['admission'].strftime(date_format4sorting), stay['pk_hospital_stay'])
			label = '%s %s: %s (%s)' % (
				stay['admission'].strftime('%Y %b'),
				stay['hospital'],
				stay['episode'],
				_('%s ago') % gmDateTime.format_interval_medically(now - stay['admission'])
			)
			sort_key_list.append(sort_key)
			data[sort_key] = [label, stay]
		del stays

		procs = emr.get_performed_procedures()
		for proc in procs:
			sort_key = '%s::%s' % (proc['clin_when'].strftime(date_format4sorting), proc['pk_procedure'])
			label = '%s%s %s (%s @ %s)' % (
				proc['clin_when'].strftime('%Y %b'),
				gmTools.bool2subst(proc['is_ongoing'], gmTools.u_ellipsis, '', ''),
				proc['performed_procedure'],
				_('%s ago') % gmDateTime.format_interval_medically(now - proc['clin_when']),
				gmDateTime.format_interval_medically(proc['clin_when'] - patient['dob'])
			)
			sort_key_list.append(sort_key)
			data[sort_key] = [label, proc]
		del procs

		vaccs = emr.latest_vaccinations
		for ind, tmp in vaccs.items():
			no_of_shots, vacc = tmp
			sort_key = '%s::%s::%s' % (vacc['date_given'].strftime(date_format4sorting), vacc['pk_vaccination'], ind)
			label = _('%s Vacc: %s (latest of %s: %s ago)') % (
				vacc['date_given'].strftime('%Y %b'),
				ind,
				no_of_shots,
				gmDateTime.format_interval_medically(now - vacc['date_given'])
			)
			sort_key_list.append(sort_key)
			data[sort_key] = [label, vacc]
		del vaccs

		for abuse in [ a for a in emr.abused_substances if a['use_type'] == gmMedication.USE_TYPE_PREVIOUSLY_ADDICTED ]:
			sort_key = '%s::%s' % (abuse['last_checked_when'].strftime(date_format4sorting), abuse['substance'])
			label = _('Hx of addiction: %s') % abuse['substance']
			sort_key_list.append(sort_key)
			data[sort_key] = [label, abuse]

		sort_key_list.sort()
		sort_key_list.reverse()
		list_items = []
		list_data = []
		for key in sort_key_list:
			label, item = data[key]
			list_items.append(label)
			list_data.append(item)

		self._LCTRL_history.set_string_items(items = list_items)
		self._LCTRL_history.set_data(data = list_data)

	#-----------------------------------------------------
	def _calc_history_list_item_tooltip(self, data):

		if isinstance(data, gmHealthIssue.cHealthIssue):
			return data.format (
				patient = gmPerson.gmCurrentPatient(),
				with_medications = False,
				with_hospital_stays = False,
				with_procedures = False,
				with_family_history = False,
				with_documents = False,
				with_tests = False,
				with_vaccinations = False
			).strip('\n')

		if isinstance(data, gmMedication.cSubstanceIntakeEntry):
			return data.format(single_line = False)

		if isinstance(data, gmFamilyHistory.cFamilyHistory):
			return data.format(include_episode = True, include_comment = True)

		if isinstance(data, gmHospitalStay.cHospitalStay):
			return data.format()

		if isinstance(data, gmPerformedProcedure.cPerformedProcedure):
			return data.format(include_episode = True, include_codes = False, include_address = True, include_comm = True)

		if isinstance(data, gmVaccination.cVaccination):
			return '\n'.join(data.format (
				with_indications = True,
				with_comment = True,
				with_reaction = True,
				date_format = '%Y %b %d'
			))

		# EDC
		if isinstance(data, str):
			if data == '':
				return None
			return data

		return None

	#-----------------------------------------------------
	def _on_history_item_activated(self, event):
		data = self._LCTRL_history.get_selected_item_data(only_one = True)
		if data is None:
			return

		if isinstance(data, str):
			gmPregWidgets.calculate_edc(parent = self, patient = gmPerson.gmCurrentPatient())
			return

		# <ctrl> down ?
		if wx.GetKeyState(wx.WXK_CONTROL):
			if isinstance(data, gmHealthIssue.cHealthIssue):
				gmEMRStructWidgets.edit_health_issue(parent = self, issue = data)
				return
			if isinstance(data, gmFamilyHistory.cFamilyHistory):
				gmFamilyHistoryWidgets.edit_family_history(parent = self, family_history = data)
				return
			if isinstance(data, gmHospitalStay.cHospitalStay):
				gmHospitalStayWidgets.edit_hospital_stay(parent = self, hospital_stay = data)
				return
			if isinstance(data, gmPerformedProcedure.cPerformedProcedure):
				gmProcedureWidgets.edit_procedure(parent = self, procedure = data)
				return
			if isinstance(data, gmVaccination.cVaccination):
				gmVaccWidgets.edit_vaccination(parent = self, vaccination = data, single_entry = True)
				return
			return

		if isinstance(data, gmHealthIssue.cHealthIssue):
			gmDispatcher.send(signal = 'display_widget', name = 'gmEMRBrowserPlugin')
			return
		if isinstance(data, gmFamilyHistory.cFamilyHistory):
			gmFamilyHistoryWidgets.manage_family_history(parent = self)
			return
		if isinstance(data, gmHospitalStay.cHospitalStay):
			gmHospitalStayWidgets.manage_hospital_stays(parent = self)
			return
		if isinstance(data, gmPerformedProcedure.cPerformedProcedure):
			gmProcedureWidgets.manage_performed_procedures(parent = self)
			return
		if isinstance(data, gmVaccination.cVaccination):
			gmVaccWidgets.manage_vaccinations(parent = self)
			return

		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_meds(self, patient=None):

		emr = patient.emr

		list_items = []
		data_items = []
		first_red = False

		# harmful substance use ?
		abuses = emr.abused_substances
		if len([ a for a in abuses if a['use_type'] in gmMedication.USE_TYPES_ACTIVE_MISUSE ]) > 0:
			list_items.append(_('active substance abuse'))
			data_items.append('\n'.join([ a.format(left_margin=0, date_format='%Y %b %d', single_line=True) for a in abuses ]))

		# list by product or substance:
		intakes = emr.get_current_medications(include_inactive = False, order_by = 'substance')
		multi_products_already_seen = []
		for intake in intakes:
			drug = intake.containing_drug
			if drug and len(drug['components']) > 1:
				if intake['product'] in multi_products_already_seen:
					continue
				multi_products_already_seen.append(intake['product'])
				list_items.append(_('%s %s%s') % (
					intake['product'],
					drug['l10n_preparation'],
					gmTools.coalesce(intake['schedule'], '', ': %s')
				))
				data_items.append(intake)
				continue
			list_items.append(_('%s %s%s%s') % (
				intake['substance'],
				gmTools.coalesce(intake['amount'], ''),
				intake.formatted_units,
				gmTools.coalesce(intake['schedule'], '', ': %s')
			))
			data_items.append(intake)

		self._LCTRL_meds.set_string_items(items = list_items)
		self._LCTRL_meds.set_data(data = data_items)

		if first_red:
			self._LCTRL_meds.SetItemTextColour(0, wx.Colour('RED'))

	#-----------------------------------------------------
	def _calc_meds_list_item_tooltip(self, data):
		if isinstance(data, str):
			return data

		emr = gmPerson.gmCurrentPatient().emr
		atcs = []
		if data['atc_substance'] is not None:
			atcs.append(data['atc_substance'])
		allg = emr.is_allergic_to(atcs = atcs, inns = [data['substance']])
		if allg is False:
			allg = None
		return data.format(allergy = allg, eol = '\n')

	#-----------------------------------------------------
	def _on_meds_item_activated(self, event):
		data = self._LCTRL_meds.get_selected_item_data(only_one = True)

		if data is None:
			return

#		if isinstance(data, str):
#			gmHabitWidgets.manage_substance_abuse(parent = self, patient = gmPerson.gmCurrentPatient())
#			return

		# <ctrl> down ? -> edit
		if wx.GetKeyState(wx.WXK_CONTROL):
			wx.CallAfter(gmSubstanceIntakeWidgets.edit_intake_with_regimen, parent = self, intake_with_regimen = data)
			return

		gmDispatcher.send(signal = 'display_widget', name = 'gmCurrentSubstancesPlugin')

	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_contacts(self, patient=None):
		emr = patient.emr

		list_items = []
		list_data = []
		is_in_hospital = False

		stays = emr.get_hospital_stays(ongoing_only = True)
		if len(stays) > 0:
			list_items.append(_('** Currently hospitalized: %s **') % stays[0]['hospital'])
			list_data.append(stays[0])
			is_in_hospital = True

		adrs = patient.get_addresses()
		for adr in adrs:
			list_items.append(adr.format(single_line = True, verbose = False, show_type = True))
			list_data.append(adr)

		comms = patient.get_comm_channels()
		for comm in comms:
			list_items.append('%s: %s%s' % (
				comm['l10n_comm_type'],
				comm['url'],
				gmTools.coalesce(comm['comment'], '', ' (%s)')
			))
			list_data.append(comm)

		ident = patient.emergency_contact_in_database
		if ident is not None:
			list_items.append(_('emergency: %s') % ident.description_gender)
			list_data.append(ident)

		if patient['emergency_contact'] is not None:
			list_items.append(_('emergency: %s') % patient['emergency_contact'].split('\n')[0])
			list_data.append(patient['emergency_contact'])

		provider = patient.primary_provider
		if provider is not None:
			list_items.append(_('in-praxis: %s') % patient.primary_provider_identity.get_description_gender(with_nickname = False))
			list_data.append(provider)

		for item in emr.external_care_items:
			list_items.append(_('care: %s%s@%s') % (
				gmTools.coalesce(item['provider'], '', '%s, '),
				item['unit'],
				item['organization']
			))
			list_data.append(item)

		self._LCTRL_contacts.set_string_items(items = list_items)
		self._LCTRL_contacts.set_data(data = list_data)
		if is_in_hospital:
			self._LCTRL_contacts.SetItemTextColour(0, wx.Colour('RED'))

	#-----------------------------------------------------
	def _calc_contacts_list_item_tooltip(self, data):

		if isinstance(data, gmHospitalStay.cHospitalStay):
			return data.format()

		if isinstance(data, gmExternalCare.cExternalCareItem):
			return '\n'.join(data.format (
				with_health_issue = True,
				with_address = True,
				with_comms = True
			))

		if isinstance(data, gmDemographicRecord.cPatientAddress):
			return '\n'.join(data.format())

		if isinstance(data, gmDemographicRecord.cCommChannel):
			parts = []
			if data['is_confidential']:
				parts.append(_('*** CONFIDENTIAL ***'))
			if data['comment'] is not None:
				parts.append(data['comment'])
			return '\n'.join(parts)

		if isinstance(data, gmPerson.cPerson):
			return '%s\n\n%s' % (
				data.description_gender,
				'\n'.join([
					'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), '', '')
					)
					for c in data.get_comm_channels()
				])
			)

		if isinstance(data, str):
			return data

		if isinstance(data, gmStaff.cStaff):
			ident = data.identity
			return '%s: %s\n\n%s%s' % (
				data['short_alias'],
				ident.description_gender,
				'\n'.join([
					'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), '', '')
					)
					for c in ident.get_comm_channels()
				]),
				gmTools.coalesce(data['comment'], '', '\n\n%s')
			)

		return None

	#-----------------------------------------------------
	def _on_contacts_item_activated(self, event):
		data = self._LCTRL_contacts.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if isinstance(data, gmHospitalStay.cHospitalStay):
					gmHospitalStayWidgets.edit_hospital_stay(parent = self, hospital_stay = data)
					return
				if isinstance(data, gmDemographicRecord.cPatientAddress):
					pass
				if isinstance(data, gmDemographicRecord.cCommChannel):
					gmContactWidgets.edit_comm_channel(parent = self, comm_channel = data, channel_owner = gmPerson.gmCurrentPatient())
					return
				if isinstance(data, gmPerson.cPerson):
					pass
				if isinstance(data, gmStaff.cStaff):
					pass

		gmDispatcher.send(signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')

	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_problems(self, patient=None):
		emr = patient.emr

		problems = [
			p for p in emr.get_problems(include_closed_episodes = False, include_irrelevant_issues = False)
			if p['problem_active']
		]

		epi_issues = [ p['pk_health_issue'] for p in problems if p['type'] == 'episode' ]
		list_items = []
		list_data = []
		for problem in problems:
			if problem['type'] == 'issue':
				issue = gmHealthIssue.cHealthIssue.from_problem(problem)
				if issue['pk_health_issue'] in epi_issues:
					continue	# skip duplicates (issue/episode)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
				if last_encounter is None:
					last = issue['modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				list_items.append('%s: %s' % (problem['problem'], last))
			elif problem['type'] == 'episode':
				epi = gmEpisode.cEpisode.from_problem(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				list_items.append('%s: %s (%s)' % (
					problem['problem'],
					last,
					gmTools.coalesce(epi['health_issue'], gmTools.u_diameter)
				))
			list_data.append(problem)

		care = emr.get_external_care_items(exclude_inactive = True)
		for item in care:
			# skip those already-shown(-or-not)
			if item['pk_health_issue'] is not None:
				continue
			list_items.append(_('extrnl: %s (%s@%s)') % (
				item['issue'],
				item['unit'],
				item['organization']
			))
			list_data.append(item)

		self._LCTRL_problems.set_string_items(items = list_items)
		self._LCTRL_problems.set_data(data = list_data)

	#-----------------------------------------------------
	def _calc_problem_list_item_tooltip(self, data) -> str:

		if isinstance(data, gmExternalCare.cExternalCareItem):
			tt = '\n'.join(data.format (
				with_health_issue = True,
				with_address = True,
				with_comms = True
			))
			return tt

		if data['type'] == 'issue':
			issue = gmHealthIssue.cHealthIssue.from_problem(data)
			tt = issue.format (
				patient = gmPerson.gmCurrentPatient(),
				with_medications = False,
				with_hospital_stays = False,
				with_procedures = False,
				with_family_history = False,
				with_documents = False,
				with_tests = False,
				with_vaccinations = False
			).strip('\n')
			return tt

		if data['type'] == 'episode':
			epi = gmEpisode.cEpisode.from_problem(data)
			tt = epi.format (
				patient = gmPerson.gmCurrentPatient(),
				with_encounters = False,
				with_hospital_stays = False,
				with_procedures = False,
				with_family_history = False,
				with_documents = False,
				with_tests = False,
				with_vaccinations = False,
				with_health_issue = True
			).strip('\n')
			return tt

		return None

	#-----------------------------------------------------
	def _on_problem_activated(self, event):
		data = self._LCTRL_problems.get_selected_item_data(only_one = True)
		if data:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if data['type'] == 'issue':
					gmEMRStructWidgets.edit_health_issue(parent = self, issue = gmHealthIssue.cHealthIssue.from_problem(data))
					return

				if data['type'] == 'episode':
					gmEMRStructWidgets.edit_episode(parent = self, episode = gmEpisode.cEpisode.from_problem(data))
					return

		gmDispatcher.send(signal = 'display_widget', name = 'gmEMRBrowserPlugin')

	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_identity(self, patient=None):
		# names (.comment -> tooltip)
		names = patient.get_names(exclude_active = True)
		items = [
			_('aka: %(last)s, %(first)s%(nick)s') % {
				'last': n['lastnames'],
				'first': n['firstnames'],
				'nick': gmTools.coalesce(n['preferred'], '', " '%s'")
			} for n in names
		]
		data = names

		# IDs (.issuer & .comment -> tooltip)
		ids = patient.external_ids
		for i in ids:
			items.append('%s: %s' % (i['name'], i['value']))
			data.append({'id': i})

		# occupation
		jobs = patient.get_occupations()
		for j in jobs:
			items.append(_('job: %s (%s)') % (
				j['l10n_occupation'],
				j['modified_when'].strftime('%m/%Y')
			))
			data.append({'job': j})

		self._LCTRL_identity.set_string_items(items = items)
		self._LCTRL_identity.set_data(data = data)

	#-----------------------------------------------------
	def _calc_identity_item_tooltip(self, data):
		if isinstance(data, gmPerson.cPersonName):
			return data['comment']
		if isinstance(data, dict):
			key = list(data)[0]
			val = data[key]
			if key == 'id':
				return _('issued by: %s%s') % (
					val['issuer'],
					gmTools.coalesce(val['comment'], '', '\n\n%s')
				)
			if key == 'job':
				tt = _('Last modified: %s') % val['modified_when'].strftime('%m/%Y')
				if val['activities'] is None:
					return tt
				return tt + ('\n\n' + _('Activities:\n\n%s') % val['activities'])

		return None

	#-----------------------------------------------------
	def _on_identity_item_activated(self, event):
		data = self._LCTRL_identity.get_selected_item_data(only_one = True)
		if data is None:
			gmDispatcher.send(signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')

		# <ctrl> down ?
		if not wx.GetKeyState(wx.WXK_CONTROL):
			gmDispatcher.send(signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')

		# <ctrl> down !
		if isinstance(data, gmPerson.cPersonName):
			ea = gmDemographicsWidgets.cPersonNameEAPnl(self, -1, name = data)
			dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
			dlg.SetTitle(_('Cloning name'))
			dlg.ShowModal()
			return

		if isinstance(data, dict):
			key = list(data)[0]
			val = data[key]
			if key == 'id':
				ea = gmDemographicsWidgets.cExternalIDEditAreaPnl(self, -1, external_id = val)
				ea.id_holder = gmPerson.gmCurrentPatient()
				dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
				dlg.SetTitle(_('Editing external ID'))
				dlg.ShowModal()
				return
			if key == 'job':
				gmDemographicsWidgets.edit_occupation()
				return

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	#--------------------------------------------------------
	#test_org_unit_prw()
