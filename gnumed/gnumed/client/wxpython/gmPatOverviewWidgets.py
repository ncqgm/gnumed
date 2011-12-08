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

from Gnumed.business import gmPerson
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmEMRStructItems

#from Gnumed.wxpython import gmListWidgets
#from Gnumed.wxpython import gmEditArea
#from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmRegetMixin
#from Gnumed.wxpython import gmAddressWidgets
#from Gnumed.wxpython import gmGuiHelpers

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
	#--------------------------------------------------------
	def __reset_ui_content(self):
		self._LCTRL_identity.set_string_items()
		self._LCTRL_problems.set_string_items()
		self._LCTRL_contacts.set_string_items()
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
		self.__refresh_problems(patient = pat)
		self.__refresh_contacts(patient = pat)
		return True
	#-----------------------------------------------------
	# internal helpers
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
