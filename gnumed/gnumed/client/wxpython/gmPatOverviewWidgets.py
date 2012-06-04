"""GNUmed patient overview widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmFamilyHistory
from Gnumed.business import gmVaccination
from Gnumed.business import gmDocuments
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmContactWidgets
from Gnumed.wxpython import gmMedicationWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmFamilyHistoryWidgets
from Gnumed.wxpython import gmVaccWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmGuiHelpers


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
		# left
		self._LCTRL_identity.set_columns(columns = [u''])
		self._LCTRL_identity.item_tooltip_callback = self._calc_identity_item_tooltip
		self._LCTRL_identity.activate_callback = self._on_identity_item_activated

		self._LCTRL_contacts.set_columns(columns = [u''])
		self._LCTRL_contacts.item_tooltip_callback = self._calc_contacts_list_item_tooltip
		self._LCTRL_contacts.activate_callback = self._on_contacts_item_activated

		self._LCTRL_encounters.set_columns(columns = [u''])
		self._LCTRL_encounters.item_tooltip_callback = self._calc_encounters_list_item_tooltip
		self._LCTRL_encounters.activate_callback = self._on_encounter_activated

		# middle
		self._LCTRL_problems.set_columns(columns = [u''])
		self._LCTRL_problems.item_tooltip_callback = self._calc_problem_list_item_tooltip
		self._LCTRL_problems.activate_callback = self._on_problem_activated

		self._LCTRL_meds.set_columns(columns = [u''])
		self._LCTRL_meds.item_tooltip_callback = self._calc_meds_list_item_tooltip
		self._LCTRL_meds.activate_callback = self._on_meds_item_activated

		self._LCTRL_history.set_columns(columns = [u''])
		self._LCTRL_history.item_tooltip_callback = self._calc_history_list_item_tooltip
		self._LCTRL_history.activate_callback = self._on_history_item_activated

		# right hand side
		self._LCTRL_inbox.set_columns(columns = [u''])
		self._LCTRL_inbox.item_tooltip_callback = self._calc_inbox_item_tooltip
		self._LCTRL_inbox.activate_callback = self._on_inbox_item_activated

		self._LCTRL_results.set_columns(columns = [u''])
		self._LCTRL_results.item_tooltip_callback = self._calc_results_list_item_tooltip
		self._LCTRL_results.activate_callback = self._on_result_activated

		self._LCTRL_documents.set_columns(columns = [u''])
		self._LCTRL_documents.item_tooltip_callback = self._calc_documents_list_item_tooltip
		self._LCTRL_documents.activate_callback = self._on_document_activated
	#--------------------------------------------------------
	def __reset_ui_content(self):
		self._LCTRL_identity.set_string_items()
		self._LCTRL_contacts.set_string_items()
		self._LCTRL_encounters.set_string_items()
		self._PRW_encounter_range.SetText(value = u'', data = None)

		self._LCTRL_problems.set_string_items()
		self._LCTRL_meds.set_string_items()
		self._LCTRL_history.set_string_items()

		self._LCTRL_inbox.set_string_items()
		self._LCTRL_results.set_string_items()
		self._LCTRL_documents.set_string_items()
	#-----------------------------------------------------
	# event handling
	#-----------------------------------------------------
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database listener
	# threads, dispatcher signals etc.
	def __register_interests(self):
		# client internal signals
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)

		# database change signals
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'comm_channel_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'job_mod_db', receiver = self._on_post_patient_selection)
		# no signal for external IDs yet
		# no signal for address yet
		#gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)
		#gmDispatcher.connect(signal = u'current_encounter_switched', receiver = self._on_current_encounter_switched)

		gmDispatcher.connect(signal = u'episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'health_issue_mod_db', receiver = self._on_episode_issue_mod_db)

		gmDispatcher.connect(signal = u'substance_intake_mod_db', receiver = self._on_post_patient_selection)

		gmDispatcher.connect(signal = u'hospital_stay_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'family_history_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'procedure_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'vacc_mod_db', receiver = self._on_post_patient_selection)

		gmDispatcher.connect(signal = u'message_inbox_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'test_result_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_post_patient_selection)

		# synchronous signals
#		self.__pat.register_pre_selection_callback(callback = self._pre_selection_callback)
#		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)

		self._PRW_encounter_range.add_callback_on_selection(callback = self._on_encounter_range_selected)
	#--------------------------------------------------------
	def _on_encounter_range_selected(self, data):
		wx.CallAfter(self.__refresh_encounters, patient = gmPerson.gmCurrentPatient())
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		# only empty out here, do NOT access the patient
		# or else we will access the old patient while it
		# may not be valid anymore ...
		wx.CallAfter(self.__reset_ui_content)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		wx.CallAfter(self._schedule_data_reget)
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
		list_items = []
		list_data = []

		emr = patient.get_emr()
		most_recent = emr.get_most_recent_result()
		if most_recent is None:
			self._LCTRL_results.set_string_items(items = [])
			self._LCTRL_results.set_data(data = [])
			return

		list_items.append(_('Latest: %s ago (%s %s %s %s%s)') % (
			gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - most_recent['clin_when']),
			most_recent['unified_abbrev'],
			most_recent['unified_val'],
			most_recent['val_unit'],
			gmTools.coalesce(most_recent['abnormality_indicator'], u'', u' %s'),
			gmTools.bool2subst(most_recent['reviewed'], u'', u' %s' % gmTools.u_writing_hand)
		))
		list_data.append(most_recent)
		most_recent_needs_red = False
		if most_recent['is_technically_abnormal'] is True:
			if most_recent['is_clinically_relevant']:
				most_recent_needs_red = True
		else:
			if most_recent['abnormality_indicator'] not in [None, u'']:
				most_recent_needs_red = True

		unsigned = emr.get_unsigned_results(order_by = u"(trim(coalesce(abnormality_indicator), '') <> '') DESC NULLS LAST, unified_abbrev")
		no_of_reds = 0
		for result in unsigned:
			if result['pk_test_result'] == most_recent['pk_test_result']:
				continue
			if result['abnormality_indicator'] is not None:
				if result['abnormality_indicator'].strip() != u'':
					no_of_reds += 1
			list_items.append(_('%s %s %s %s (%s ago, %s)') % (
				result['unified_abbrev'],
				result['unified_val'],
				result['val_unit'],
				gmTools.coalesce(result['abnormality_indicator'], u'', u' %s'),
				gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - result['clin_when']),
				gmTools.u_writing_hand
			))
			list_data.append(result)

		self._LCTRL_results.set_string_items(items = list_items)
		self._LCTRL_results.set_data(data = list_data)

		if most_recent_needs_red:
			self._LCTRL_results.SetItemTextColour(0, wx.NamedColour('RED'))
		if no_of_reds > 0:
			for idx in range(1, no_of_reds + 1):
				self._LCTRL_results.SetItemTextColour(idx, wx.NamedColour('RED'))
	#-----------------------------------------------------
	def _calc_results_list_item_tooltip(self, data):
		return u'\n'.join(data.format())
	#-----------------------------------------------------
	def _on_result_activated(self, event):
#		data = self._LCTRL_inbox.get_selected_item_data(only_one = True)
#
#		if data is not None:
#			# <ctrl> down ?
#			if wx.GetKeyState(wx.WXK_CONTROL):
#				if isinstance(data, gmProviderInbox.cInboxMessage):
#					xxxxxxxxx
		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_inbox(self, patient=None):
		list_items = []
		list_data = []

		due_messages = patient.due_messages
		no_of_dues = len(due_messages)
		for msg in due_messages:
			list_items.append(_('due %s: %s') % (
				gmDateTime.format_interval_medically(msg['interval_due']),
				gmTools.coalesce(msg['comment'], u'?')
			))
			list_data.append(msg)

		for msg in patient.messages:
			# already displayed above ?
			if msg['is_due']:
				continue
			# not relevant anymore ?
			if msg['is_expired']:
				continue
			list_items.append(u'%s%s' % (
				msg['l10n_type'],
				gmTools.coalesce(msg['comment'], u'', u': %s')
			))
			list_data.append(msg)

		for hint in patient.dynamic_hints:
			list_items.append(hint['title'])
			list_data.append(hint)

		self._LCTRL_inbox.set_string_items(items = list_items)
		self._LCTRL_inbox.set_data(data = list_data)

		if no_of_dues > 0:
			for idx in range(no_of_dues):
				self._LCTRL_inbox.SetItemTextColour(idx, wx.NamedColour('RED'))
	#-----------------------------------------------------
	def _calc_inbox_item_tooltip(self, data):
		if isinstance(data, gmProviderInbox.cInboxMessage):
			return data.format()

		if isinstance(data, gmProviderInbox.cDynamicHint):
			return u'%s\n\n%s\n\n%s          %s' % (
				data['title'],
				gmTools.wrap(data['hint'], width = 50),
				gmTools.wrap(gmTools.coalesce(data['url'], u'', u'%s\n\n'), width = 50),
				data['source']
			)

		return None
	#-----------------------------------------------------
	def _on_inbox_item_activated(self, event):

		data = self._LCTRL_inbox.get_selected_item_data(only_one = True)

		if isinstance(data, gmProviderInbox.cDynamicHint):
			if data['url'] is not None:
				gmNetworkTools.open_url_in_browser(data['url'])
			return

		# <ctrl> down ?
		if not wx.GetKeyState(wx.WXK_CONTROL):
			wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmProviderInboxPlugin')
			return

		if data is None:
			wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmProviderInboxPlugin')
			return

		if not isinstance(data, gmProviderInbox.cInboxMessage):
			wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmProviderInboxPlugin')
			return

		delete_it = gmGuiHelpers.gm_show_question (
			question = _('Do you really want to\ndelete this inbox message ?'),
			title = _('Deleting inbox message')
		)
		if not delete_it:
			return

		gmProviderInbox.delete_inbox_message(inbox_message = data['pk_inbox_message'])
		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_documents(self, patient=None):
		doc_folder = patient.get_document_folder()

		list_items = []
		list_data = []

		docs = doc_folder.get_unsigned_documents()
		no_of_unsigned = len(docs)
		for doc in docs:
			list_items.append(u'%s %s (%s)' % (
				gmDateTime.pydt_strftime(doc['clin_when'], format = '%m/%Y', accuracy = gmDateTime.acc_months),
				doc['l10n_type'],
				gmTools.u_writing_hand
			))
			list_data.append(doc)

		docs = doc_folder.get_documents(order_by = u'ORDER BY clin_when DESC', exclude_unsigned = True)
		for doc in docs[:5]:
			list_items.append(u'%s %s' % (
				gmDateTime.pydt_strftime(doc['clin_when'], format = '%m/%Y', accuracy = gmDateTime.acc_months),
				doc['l10n_type']
			))
			list_data.append(doc)
		if len(docs) > 5:
			list_items.append(_('%s %s more not shown %s') % (
				gmTools.u_ellipsis,
				len(docs) - 5,
				gmTools.u_ellipsis
			))
			list_data.append(u'')

		self._LCTRL_documents.set_string_items(items = list_items)
		self._LCTRL_documents.set_data(data = list_data)

		if no_of_unsigned > 0:
			for idx in range(no_of_unsigned):
				self._LCTRL_documents.SetItemTextColour(idx, wx.NamedColour('RED'))
	#-----------------------------------------------------
	def _calc_documents_list_item_tooltip(self, data):
		emr = gmPerson.gmCurrentPatient().get_emr()

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

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmShowMedDocs')
		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_encounters(self, patient=None):

		cover_period = self._PRW_encounter_range.GetData()
		if cover_period is None:
			if self._PRW_encounter_range.GetValue().strip() != u'':
				return

		emr = patient.get_emr()

		list_items = []
		list_data = []

		is_waiting = False
		wlist = patient.get_waiting_list_entry()
		if len(wlist) > 0:
			is_waiting = True
			w = wlist[0]
			list_items.append(_('Currently in waiting list [%s]') % w['waiting_zone'])
			list_data.append({'wlist': gmTools.coalesce(w['comment'], None)})

		first = emr.get_first_encounter()
		if first is not None:
			list_items.append (
				_('first: %s, %s') % (
					gmDateTime.pydt_strftime (
						first['started'],
						format = '%Y %b %d',
						accuracy = gmDateTime.acc_days
					),
					first['l10n_type']
				)
			)
			list_data.append(first)

		last = emr.get_last_but_one_encounter()
		if last is not None:
			list_items.append (
				_('last: %s, %s') % (
					gmDateTime.pydt_strftime (
						last['started'],
						format = '%Y %b %d',
						accuracy = gmDateTime.acc_days
					),
					last['l10n_type']
				)
			)
			list_data.append(last)

		encs = emr.get_encounter_stats_by_type(cover_period = cover_period)
		for enc in encs:
			item = u'%s x %s' % (enc['frequency'], enc['l10n_type'])
			list_items.append(item)
			list_data.append(item)

		stays = emr.get_hospital_stay_stats_by_hospital(cover_period = cover_period)
		for stay in stays:
			item = u'%s x %s' % (
				stay['frequency'],
				stay['hospital']
			)
			list_items.append(item)
			list_data.append({'stay': item})

		self._LCTRL_encounters.set_string_items(items = list_items)
		self._LCTRL_encounters.set_data(data = list_data)
		if is_waiting:
			self._LCTRL_encounters.SetItemTextColour(0, wx.NamedColour('RED'))
	#-----------------------------------------------------
	def _calc_encounters_list_item_tooltip(self, data):
		emr = gmPerson.gmCurrentPatient().get_emr()

		if isinstance(data, gmEMRStructItems.cEncounter):
			return data.format (
				with_vaccinations = False,
				with_tests = False,
				with_docs = False,
				with_co_encountlet_hints = True,
				with_rfe_aoe = True
			)

		if type(data) == type({}):
			key, val = data.items()[0]
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
				if isinstance(data, gmEMRStructItems.cEncounter):
					gmEMRStructWidgets.edit_encounter(parent = self, encounter = data)
					return

		if type(data) == type({}):
			key, val = data.items()[0]
			if key == 'wlist':
				wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmWaitingListPlugin')
				return
			if key == 'stay':
				wx.CallAfter(gmEMRStructWidgets.manage_hospital_stays, parent = self)
				return

		wx.CallAfter(gmEMRStructWidgets.manage_encounters, parent = self, ignore_OK_button = False)
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_history(self, patient=None):
		emr = patient.get_emr()

		list_items = []
		list_data = []

		issues = [
			i for i in emr.get_health_issues()
			if ((i['clinically_relevant'] is False) or (i['is_active'] is False))
		]
		for issue in issues:
			last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
			if last_encounter is None:
				last = issue['modified_when'].strftime('%m/%Y')
			else:
				last = last_encounter['last_affirmed'].strftime('%m/%Y')
			list_items.append(u'%s %s' % (last, issue['description']))
			list_data.append(issue)
		del issues

		fhxs = emr.get_family_history()
		for fhx in fhxs:
			list_items.append(u'%s: %s%s' % (
				fhx['l10n_relation'],
				fhx['condition'],
				gmTools.coalesce(fhx['age_noted'], u'', u' (@ %s)')
			))
			list_data.append(fhx)
		del fhxs

		stays = emr.get_hospital_stays()
		for stay in stays:
			if stay['discharge'] is not None:
				discharge = u''
			else:
				discharge = gmTools.u_ellipsis
			list_items.append(u'%s%s %s: %s' % (
				gmDateTime.pydt_strftime(stay['admission'], format = '%Y %b %d'),
				discharge,
				stay['hospital'],
				stay['episode']
			))
			list_data.append(stay)
		del stays

		procs = emr.get_performed_procedures()
		for proc in procs:
			list_items.append(u'%s%s %s' % (
				gmDateTime.pydt_strftime(proc['clin_when'], format = '%Y %b %d'),
				gmTools.bool2subst(proc['is_ongoing'], gmTools.u_ellipsis, u'', u''),
				proc['performed_procedure']
			))
			list_data.append(proc)
		del procs

		vaccs = emr.get_latest_vaccinations()
		for ind, tmp in vaccs.items():
			tmp, vacc = tmp
			list_items.append(_('%s Vacc: %s') % (
				gmDateTime.pydt_strftime(vacc['date_given'], format = '%Y %b %d'),
				ind
			))
			list_data.append(vacc)
		del vaccs

		self._LCTRL_history.set_string_items(items = list_items)
		self._LCTRL_history.set_data(data = list_data)
	#-----------------------------------------------------
	def _calc_history_list_item_tooltip(self, data):

		if isinstance(data, gmEMRStructItems.cHealthIssue):
			return data.format (
				patient = gmPerson.gmCurrentPatient(),
				with_medications = False,
				with_hospital_stays = False,
				with_procedures = False,
				with_family_history = False,
				with_documents = False,
				with_tests = False,
				with_vaccinations = False
			).strip(u'\n')

		if isinstance(data, gmFamilyHistory.cFamilyHistory):
			return data.format(include_episode = True, include_comment = True)

		if isinstance(data, gmEMRStructItems.cHospitalStay):
			return data.format()

		if isinstance(data, gmEMRStructItems.cPerformedProcedure):
			return data.format(include_episode = True)

		if isinstance(data, gmVaccination.cVaccination):
			return u'\n'.join(data.format (
				with_indications = True,
				with_comment = True,
				with_reaction = True,
				date_format = '%Y %b %d'
			))

		return None
	#-----------------------------------------------------
	def _on_history_item_activated(self, event):
		data = self._LCTRL_history.get_selected_item_data(only_one = True)
		if data is None:
			return

		# <ctrl> down ?
		if wx.GetKeyState(wx.WXK_CONTROL):
			if isinstance(data, gmEMRStructItems.cHealthIssue):
				gmEMRStructWidgets.edit_health_issue(parent = self, issue = data)
				return
			if isinstance(data, gmFamilyHistory.cFamilyHistory):
				FamilyHistoryWidgets.edit_family_history(parent = self, family_history = data)
				return
			if isinstance(data, gmEMRStructItems.cHospitalStay):
				gmEMRStructWidgets.edit_hospital_stay(parent = self, hospital_stay = data)
				return
			if isinstance(data, gmEMRStructItems.cPerformedProcedure):
				gmEMRStructWidgets.edit_procedure(parent = self, procedure = data)
				return
			if isinstance(data, gmVaccination.cVaccination):
				gmVaccWidgets.edit_vaccination(parent = self, vaccination = data, single_entry = True)
				return
			return

		if isinstance(data, gmEMRStructItems.cHealthIssue):
			wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmEMRBrowserPlugin')
			return
		if isinstance(data, gmFamilyHistory.cFamilyHistory):
			FamilyHistoryWidgets.manage_family_history(parent = self)
			return
		if isinstance(data, gmEMRStructItems.cHospitalStay):
			gmEMRStructWidgets.manage_hospital_stays(parent = self)
			return
		if isinstance(data, gmEMRStructItems.cPerformedProcedure):
			gmEMRStructWidgets.manage_performed_procedures(parent = self)
			return
		if isinstance(data, gmVaccination.cVaccination):
			gmVaccWidgets.manage_vaccinations(parent = self)
			return

		return
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_meds(self, patient=None):
		# list by brand or substance:
		emr = patient.get_emr()
		intakes = emr.get_current_substance_intake(include_inactive = False, include_unapproved = True, order_by = u'substance')

		list_items = []
		multi_brands_already_seen = []
		for intake in intakes:
			brand = intake.containing_drug
			if brand is None or len(brand['pk_components']) == 1:
				list_items.append(_('%s %s %s%s') % (
					intake['substance'],
					intake['amount'],
					intake['unit'],
					gmTools.coalesce (
						intake['schedule'],
						u'',
						u': %s'
					)
				))
			else:
				if intake['brand'] in multi_brands_already_seen:
					continue
				multi_brands_already_seen.append(intake['brand'])
				list_items.append(_('%s %s%s') % (
					intake['brand'],
					brand['preparation'],
					gmTools.coalesce (
						intake['schedule'],
						u'',
						u': %s'
					)
				))
		self._LCTRL_meds.set_string_items(items = list_items)
		self._LCTRL_meds.set_data(data = intakes)
	#-----------------------------------------------------
	def _calc_meds_list_item_tooltip(self, data):
		emr = gmPerson.gmCurrentPatient().get_emr()
		atcs = []
		if data['atc_substance'] is not None:
			atcs.append(data['atc_substance'])
#		if data['atc_brand'] is not None:
#			atcs.append(data['atc_brand'])
#		allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (data['substance'],), brand = data['brand'])
		allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (data['substance'],))
		if allg is False:
			allg = None
		return data.format(one_line = False, allergy = allg, show_all_brand_components = True)
	#-----------------------------------------------------
	def _on_meds_item_activated(self, event):
		data = self._LCTRL_meds.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				wx.CallAfter(gmMedicationWidgets.edit_intake_of_substance, parent = self, substance = data)
				return

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmCurrentSubstancesPlugin')
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_contacts(self, patient=None):
		emr = patient.get_emr()

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
			list_items.append(u'%s: %s' % (
				comm['l10n_comm_type'],
				comm['url']
			))
			list_data.append(comm)

		ident = patient.emergency_contact_in_database
		if ident is not None:
			list_items.append(_('emergency: %s') % ident['description_gender'])
			list_data.append(ident)

		if patient['emergency_contact'] is not None:
			list_items.append(_('emergency: %s') % patient['emergency_contact'].split(u'\n')[0])
			list_data.append(patient['emergency_contact'])

		provider = patient.primary_provider
		if provider is not None:
			list_items.append(_('in-praxis: %s') % provider.identity['description_gender'])
			list_data.append(provider)

		self._LCTRL_contacts.set_string_items(items = list_items)
		self._LCTRL_contacts.set_data(data = list_data)
		if is_in_hospital:
			self._LCTRL_contacts.SetItemTextColour(0, wx.NamedColour('RED'))
	#-----------------------------------------------------
	def _calc_contacts_list_item_tooltip(self, data):

		if isinstance(data, gmEMRStructItems.cHospitalStay):
			return data.format()

		if isinstance(data, gmDemographicRecord.cPatientAddress):
			return u'\n'.join(data.format())

		if isinstance(data, gmDemographicRecord.cCommChannel):
			return gmTools.bool2subst (
				data['is_confidential'],
				_('*** CONFIDENTIAL ***'),
				None
			)

		if isinstance(data, gmPerson.cIdentity):
			return u'%s\n\n%s' % (
				data['description_gender'],
				u'\n'.join([
					u'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), u'', u'')
					)
					for c in data.get_comm_channels()
				])
			)

		if isinstance(data, basestring):
			return data

		if isinstance(data, gmStaff.cStaff):
			ident = data.identity
			return u'%s: %s\n\n%s%s' % (
				data['short_alias'],
				ident['description_gender'],
				u'\n'.join([
					u'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), u'', u'')
					)
					for c in ident.get_comm_channels()
				]),
				gmTools.coalesce(data['comment'], u'', u'\n\n%s')
			)

		return None
	#-----------------------------------------------------
	def _on_contacts_item_activated(self, event):
		data = self._LCTRL_contacts.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if isinstance(data, gmEMRStructItems.cHospitalStay):
					gmEMRStructWidgets.edit_hospital_stay(parent = self, hospital_stay = data)
					return
				if isinstance(data, gmDemographicRecord.cPatientAddress):
					pass
				if isinstance(data, gmDemographicRecord.cCommChannel):
					gmContactWidgets.edit_comm_channel(parent = self, comm_channel = data, channel_owner = gmPerson.gmCurrentPatient())
					return
				if isinstance(data, gmPerson.cIdentity):
					pass
				if isinstance(data, gmStaff.cStaff):
					pass

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_problems(self, patient=None):
		emr = patient.get_emr()

		problems = [
			p for p in emr.get_problems(include_closed_episodes = False, include_irrelevant_issues = False)
			if p['problem_active']
		]

		list_items = []
		for problem in problems:
			if problem['type'] == 'issue':
				issue = emr.problem2issue(problem)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
				if last_encounter is None:
					last = issue['modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				list_items.append(u'%s: %s' % (problem['problem'], last))

			elif problem['type'] == 'episode':
				epi = emr.problem2episode(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				list_items.append(u'%s: %s' % (problem['problem'], last))

		self._LCTRL_problems.set_string_items(items = list_items)
		self._LCTRL_problems.set_data(data = problems)
	#-----------------------------------------------------
	def _calc_problem_list_item_tooltip(self, data):
		emr = gmPerson.gmCurrentPatient().get_emr()

		if data['type'] == 'issue':
			issue = emr.problem2issue(data)
			tt = issue.format (
				patient = gmPerson.gmCurrentPatient(),
				with_medications = False,
				with_hospital_stays = False,
				with_procedures = False,
				with_family_history = False,
				with_documents = False,
				with_tests = False,
				with_vaccinations = False
			).strip(u'\n')
			return tt

		if data['type'] == 'episode':
			epi = emr.problem2episode(data)
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
			).strip(u'\n')
			return tt

		return None
	#-----------------------------------------------------
	def _on_problem_activated(self, event):
		data = self._LCTRL_problems.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				emr = gmPerson.gmCurrentPatient().get_emr()
				if data['type'] == 'issue':
					gmEMRStructWidgets.edit_health_issue(parent = self, issue = emr.problem2issue(data))
					return
				if data['type'] == 'episode':
					gmEMRStructWidgets.edit_episode(parent = self, episode = emr.problem2episode(data))
					return

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmEMRBrowserPlugin')
	#-----------------------------------------------------
	#-----------------------------------------------------
	def __refresh_identity(self, patient=None):
		# names (.comment -> tooltip)
		names = patient.get_names(exclude_active = True)
		items = [
			_('aka: %(last)s, %(first)s%(nick)s') % {
				'last': n['lastnames'],
				'first': n['firstnames'],
				'nick': gmTools.coalesce(n['preferred'], u'', u" '%s'")
			} for n in names
		]
		data = names

		# IDs (.issuer & .comment -> tooltip)
		ids = patient.external_ids
		for i in ids:
			items.append(u'%(name)s: %(value)s' % i)
			data.append({'id': i})

		# occupation
		jobs = patient.get_occupations()
		for j in jobs:
			items.append(_('job: %s') % j['l10n_occupation'])
			data.append({'job': j})

		self._LCTRL_identity.set_string_items(items = items)
		self._LCTRL_identity.set_data(data = data)
	#-----------------------------------------------------
	def _calc_identity_item_tooltip(self, data):
		if isinstance(data, gmPerson.cPersonName):
			return data['comment']
		if isinstance(data, type({})):
			key = data.keys()[0]
			val = data[key]
			if key == 'id':
				return _('issued by: %s%s') % (
					val['issuer'],
					gmTools.coalesce(val['comment'], u'', u'\n\n%s')
				)
			if key == 'job':
				if val['activities'] is None:
					return None
				return _('Activities:\n\n%s') % val['activities']

		return None
	#-----------------------------------------------------
	def _on_identity_item_activated(self, event):
		data = self._LCTRL_identity.get_selected_item_data(only_one = True)
		if data is not None:
			# <ctrl> down ?
			if wx.GetKeyState(wx.WXK_CONTROL):
				if isinstance(data, gmPerson.cPersonName):
					ea = gmDemographicsWidgets.cPersonNameEAPnl(self, -1, name = data)
					dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
					dlg.SetTitle(_('Cloning name'))
					dlg.ShowModal()
					return
				if isinstance(data, type({})):
					key = data.keys()[0]
					val = data[key]
					if key == 'id':
						ea = gmDemographicsWidgets.cExternalIDEditAreaPnl(self, -1, external_id = val)
						ea.identity = gmPerson.gmCurrentPatient()
						dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
						dlg.SetTitle(_('Editing external ID'))
						dlg.ShowModal()
						return
					if key == 'job':
						gmDemographicsWidgets.edit_occupation()
						return

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	#--------------------------------------------------------
	#test_org_unit_prw()
