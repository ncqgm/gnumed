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
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmFamilyHistory
from Gnumed.business import gmVaccination
from Gnumed.wxpython import gmRegetMixin


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
		self._LCTRL_identity.set_columns(columns = [u''])
		self._LCTRL_identity.item_tooltip_callback = self._calc_identity_item_tooltip

		self._LCTRL_problems.set_columns(columns = [u''])
		self._LCTRL_problems.item_tooltip_callback = self._calc_problem_list_item_tooltip

		self._LCTRL_contacts.set_columns(columns = [u''])
		self._LCTRL_contacts.item_tooltip_callback = self._calc_contacts_list_item_tooltip

		self._LCTRL_meds.set_columns(columns = [u''])
		self._LCTRL_meds.item_tooltip_callback = self._calc_meds_list_item_tooltip

		self._LCTRL_history.set_columns(columns = [u''])
		self._LCTRL_history.item_tooltip_callback = self._calc_history_list_item_tooltip
	#--------------------------------------------------------
	def __reset_ui_content(self):
		self._LCTRL_identity.set_string_items()
		self._LCTRL_problems.set_string_items()
		self._LCTRL_contacts.set_string_items()
		self._LCTRL_meds.set_string_items()
		self._LCTRL_history.set_string_items()
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
		# maybe make this update identity field only
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'comm_channel_mod_db', receiver = self._on_post_patient_selection)
		# no signal for external IDs yet
		# no signal for address yet

		gmDispatcher.connect(signal = u'episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = u'health_issue_mod_db', receiver = self._on_episode_issue_mod_db)

		gmDispatcher.connect(signal = u'substance_intake_mod_db', receiver = self._on_post_patient_selection)

		gmDispatcher.connect(signal = u'hospital_stay_mod_db', receiver = self._on_post_patient_selection)
		#gmDispatcher.connect(signal = u'family_history_mod_db', receiver = self._on_post_patient_selection)


#		gmDispatcher.connect(signal = u'episode_code_mod_db', receiver = self._on_episode_issue_mod_db)
#		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_doc_mod_db)			# visual progress notes
#		gmDispatcher.connect(signal = u'current_encounter_modified', receiver = self._on_current_encounter_modified)
#		gmDispatcher.connect(signal = u'current_encounter_switched', receiver = self._on_current_encounter_switched)
#		gmDispatcher.connect(signal = u'rfe_code_mod_db', receiver = self._on_encounter_code_modified)
#		gmDispatcher.connect(signal = u'aoe_code_mod_db', receiver = self._on_encounter_code_modified)

		# synchronous signals
#		self.__pat.register_pre_selection_callback(callback = self._pre_selection_callback)
#		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)

	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
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

		self.__refresh_problems(patient = pat)
		self.__refresh_meds(patient = pat)
		self.__refresh_history(patient = pat)

		return True
	#-----------------------------------------------------
	# internal helpers
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
			list_items.append(u'%s %s' % (
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
	def __refresh_meds(self, patient=None):
		emr = patient.get_emr()
		list_items = []
		meds = emr.get_current_substance_intake(include_inactive = False, include_unapproved = True, order_by = u'substance')
		for med in meds:
			list_items.append(_('%s %s %s%s') % (
				med['substance'],
				med['amount'],
				med['unit'],
				gmTools.coalesce (
					med['schedule'],
					u'',
					u': %s'
				)
			))
		self._LCTRL_meds.set_string_items(items = list_items)
		self._LCTRL_meds.set_data(data = meds)
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
		return data.format(one_line = False, allergy = allg)
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
			list_items.append(_('%(typ)s: %(street)s %(no)s%(sub)s, %(zip)s %(urb)s, %(cstate)s, %(ccountry)s') % {
				'typ': adr['l10n_address_type'],
				'street': adr['street'],
				'no': adr['number'],
				'sub': gmTools.coalesce(adr['subunit'], u'', u'/%s'),
				'zip': adr['postcode'],
				'urb': adr['urb'],
				'cstate': adr['code_state'],
				'ccountry': adr['code_country']
			})
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
		items.extend([ u'%(name)s: %(value)s' % i for i in ids ])
		data.extend(ids)

		self._LCTRL_identity.set_string_items(items = items)
		self._LCTRL_identity.set_data(data = data)
	#-----------------------------------------------------
	def _calc_identity_item_tooltip(self, data):
		if isinstance(data, gmPerson.cPersonName):
			return data['comment']
		return u'issued by: %s%s' % (
			data['issuer'],
			gmTools.coalesce(data['comment'], u'', u'\n\n%s')
		)
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
