# -*- coding: utf-8 -*-
"""GNUmed clinical patient record."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

# standard libs
import sys
import logging
import threading
import datetime as pydt

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmDateTime

if __name__ == '__main__':
	from Gnumed.pycommon import gmLog2
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmTools

from Gnumed.business import gmGenericEMRItem
from Gnumed.business import gmAllergy
from Gnumed.business import gmPathLab
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmMedication
from Gnumed.business import gmVaccination
from Gnumed.business import gmFamilyHistory
from Gnumed.business import gmExternalCare
from Gnumed.business import gmOrganization
from Gnumed.business import gmAutoHints
from Gnumed.business.gmDemographicRecord import get_occupations


_log = logging.getLogger('gm.emr')

_here = None
#============================================================
# helper functions
#------------------------------------------------------------
#_func_ask_user = None
#
#def set_func_ask_user(a_func = None):
#	if not callable(a_func):
#		_log.error('[%] not callable, not setting _func_ask_user', a_func)
#		return False
#
#	_log.debug('setting _func_ask_user to [%s]', a_func)
#
#	global _func_ask_user
#	_func_ask_user = a_func

#============================================================
from Gnumed.business.gmDocuments import cDocument
from Gnumed.business.gmProviderInbox import cInboxMessage

_map_table2class = {
	'clin.encounter': gmEMRStructItems.cEncounter,
	'clin.episode': gmEMRStructItems.cEpisode,
	'clin.health_issue': gmEMRStructItems.cHealthIssue,
	'clin.external_care': gmExternalCare.cExternalCareItem,
	'clin.vaccination': gmVaccination.cVaccination,
	'clin.clin_narrative': gmClinNarrative.cNarrative,
	'clin.test_result': gmPathLab.cTestResult,
	'clin.substance_intake': gmMedication.cSubstanceIntakeEntry,
	'clin.hospital_stay': gmEMRStructItems.cHospitalStay,
	'clin.procedure': gmEMRStructItems.cPerformedProcedure,
	'clin.allergy': gmAllergy.cAllergy,
	'clin.allergy_state': gmAllergy.cAllergyState,
	'clin.family_history': gmFamilyHistory.cFamilyHistory,
	'clin.suppressed_hint': gmAutoHints.cSuppressedHint,
	'blobs.doc_med': cDocument,
	'dem.message_inbox': cInboxMessage,
	'ref.auto_hint': gmAutoHints.cDynamicHint
}

def instantiate_clin_root_item(table, pk):
	try:
		item_class = _map_table2class[table]
	except KeyError:
		_log.error('unmapped clin_root_item entry [%s], cannot instantiate', table)
		return None

	return item_class(aPK_obj = pk)

#------------------------------------------------------------
def format_clin_root_item(table, pk, patient=None):

	instance = instantiate_clin_root_item(table, pk)
	if instance is None:
		return _('cannot instantiate clinical root item <%s(%s)>' % (table, pk))

#	if patient is not None:
#		if patient.ID != instance['pk_patient']:
#			raise ValueError(u'patient passed in: [%s], but instance is: [%s:%s:%s]' % (patient.ID, table, pk, instance['pk_patient']))

	if hasattr(instance, 'format_maximum_information'):
		return '\n'.join(instance.format_maximum_information(patient = patient))

	if hasattr(instance, 'format'):
		try:
			formatted = instance.format(patient = patient)
		except TypeError:
			formatted = instance.format()
		if type(formatted) == type([]):
			return '\n'.join(formatted)
		return formatted

	d = instance.fields_as_dict (
		date_format = '%Y %b %d  %H:%M',
		none_string = gmTools.u_diameter,
		escape_style = None,
		bool_strings = [_('True'), _('False')]
	)
	return gmTools.format_dict_like(d, tabular = True, value_delimiters = None)

#============================================================
def __noop_delayed_execute(*args, **kwargs):
	pass


_delayed_execute = __noop_delayed_execute


def set_delayed_executor(executor):
	if not callable(executor):
		raise TypeError('executor <%s> is not callable' % executor)
	global _delayed_execute
	_delayed_execute = executor
	_log.debug('setting delayed executor to <%s>', executor)

#------------------------------------------------------------
class cClinicalRecord(object):

	def __init__(self, aPKey=None):#, allow_user_interaction=True, encounter=None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self.pk_patient = aPKey			# == identity.pk == primary key
		self.gender = None
		self.dob = None

		from Gnumed.business import gmPraxis
		global _here
		if _here is None:
			_here = gmPraxis.gmCurrentPraxisBranch()

		self.__encounter = None
		self.__setup_active_encounter()

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
		if not self._register_interests():
			raise gmExceptions.ConstructorError("cannot register signal interests")

		gmAllergy.ensure_has_allergy_state(encounter = self.current_encounter['pk_encounter'])
		#_delayed_execute(gmAllergy.ensure_has_allergy_state, encounter = self.current_encounter['pk_encounter'])

		self.__calculator = None

		_log.debug('Instantiated clinical record for patient [%s].' % self.pk_patient)

#	#--------------------------------------------------------
#	def __old_style_init(self, allow_user_interaction=True):
#
#		_log.error('%s.__old_style_init() used', self.__class__.__name__)
#		print u'*** GNUmed [%s]: __old_style_init() used ***' % self.__class__.__name__
#
#		# FIXME: delegate to worker thread
#		# log access to patient record (HIPAA, for example)
#		cmd = u'SELECT gm.log_access2emr(%(todo)s)'
#		args = {'todo': u'patient [%s]' % self.pk_patient}
#		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#
#		# load current or create new encounter
#		if _func_ask_user is None:
#			_log.error('[_func_ask_user] is None')
#			print "*** GNUmed [%s]: _func_ask_user is not set ***" % self.__class__.__name__
#
##		# FIXME: delegate to worker thread ?
#		self.remove_empty_encounters()
#
#		self.__encounter = None
#		if not self.__initiate_active_encounter(allow_user_interaction = allow_user_interaction):
#			raise gmExceptions.ConstructorError("cannot activate an encounter for patient [%s]" % self.pk_patient)
#
##		# FIXME: delegate to worker thread
#		gmAllergy.ensure_has_allergy_state(encounter = self.current_encounter['pk_encounter'])

	#--------------------------------------------------------
	def cleanup(self):
		_log.debug('cleaning up after clinical record for patient [%s]' % self.pk_patient)
		if self.__encounter is not None:
			self.__encounter.unlock(exclusive = False)
		return True

	#--------------------------------------------------------
	def log_access(self, action=None):
		if action is None:
			action = 'EMR access for pk_identity [%s]' % self.pk_patient
		args = {'action': action}
		cmd = 'SELECT gm.log_access2emr(%(action)s)'
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	#--------------------------------------------------------
	def _get_calculator(self):
		if self.__calculator is None:
			from Gnumed.business.gmClinicalCalculator import cClinicalCalculator
			self.__calculator = cClinicalCalculator()
			from Gnumed.business.gmPerson import gmCurrentPatient
			curr_pat = gmCurrentPatient()
			if curr_pat.ID == self.pk_patient:
				self.__calculator.patient = curr_pat
			else:
				from Gnumed.business.gmPerson import cPatient
				self.__calculator.patient = cPatient(self.pk_patient)
		return self.__calculator

	calculator = property(_get_calculator, lambda x:x)

	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self.db_modification_callback)
		return True

	#--------------------------------------------------------
	def db_modification_callback(self, **kwds):

		if kwds['table'] != 'clin.encounter':
			return True

		if self.current_encounter is None:
			_log.debug('locally no encounter current, ignoring encounter modification signal')
			return True

		if int(kwds['pk_of_row']) != self.current_encounter['pk_encounter']:
			_log.debug('DB reported modification of encounter: #%s', kwds['pk_of_row'])
			_log.debug('our locally active encounter is: #%s', self.current_encounter['pk_encounter'])
			_log.debug('modified encounter != our encounter, ignoring')
			return True

		_log.debug('remote modification of our encounter signalled (local: #%s, remote: #%s)', self.current_encounter['pk_encounter'], kwds['pk_of_row'])

		# did someone delete the current encounter from under our feet ?
		if kwds['operation'] == 'DELETE':
			_log.error('local encounter has been DELETEd remotely, trying to get now-active encounter from database')
			if self.current_encounter.is_modified():
				_log.error('local encounter instance has .is_modified()=True, losing local changes')
				_log.error('this hints at an error in .is_modified handling')
			# dirty fix: get now-active encounter
			self.current_encounter.unlock(exclusive = False)
			self.__encounter = None
			self.__setup_active_encounter()
			gmDispatcher.send('current_encounter_switched')
			return True

		# get the current encounter as an extra instance
		# from the database to check for changes
		curr_enc_in_db = gmEMRStructItems.cEncounter(aPK_obj = self.current_encounter['pk_encounter'])

		# the encounter just retrieved and the active encounter
		# have got the same transaction ID so there's no change
		# in the database, there could be a local change in
		# the active encounter but that doesn't matter because
		# no one else can have written to the DB so far (XMIN match)
		if curr_enc_in_db['xmin_encounter'] == self.current_encounter['xmin_encounter']:
			_log.debug('in-client and in-DB instance of encounter #%s have matching XMINs (%s), DB has NOT been written to since we last loaded the encounter', self.current_encounter['pk_encounter'], self.current_encounter['xmin_encounter'])
			if self.current_encounter.is_modified():
				_log.error('encounter modification signal from DB with same XMIN as in local in-client instance of encounter BUT local instance ALSO has .is_modified()=True')
				_log.error('this hints at an error in .is_modified handling')
				gmTools.compare_dict_likes(self.current_encounter.fields_as_dict(), curr_enc_in_db.fields_as_dict(), 'modified enc in client', 'signalled enc loaded from DB')
			return True

		# there must have been a change to the active encounter
		# committed to the database from elsewhere,
		# we must fail to propagate the change, however, if
		# there are local changes pending
		if self.current_encounter.is_modified():
			gmTools.compare_dict_likes(self.current_encounter.fields_as_dict(), curr_enc_in_db.fields_as_dict(), 'modified enc in client', 'signalled enc loaded from DB')
			raise ValueError('unsaved changes in locally active encounter [%s], cannot switch to DB state of encounter [%s]' % (
				self.current_encounter['pk_encounter'],
				curr_enc_in_db['pk_encounter']
			))

		# don't do this, because same_payload() does not compare _all_
		# fields so we can get into a reality disconnect if we
		# don't announce the modification
#		if self.current_encounter.same_payload(another_object = curr_enc_in_db):
#			_log.debug('clin.encounter_mod_db received but no change to active encounter payload')
#			return True

		# there was a change in the database from elsewhere;
		# locally, however, we don't have any pending changes;
		# therefore we can propagate the remote change locally
		# without losing anything;
		# this really should be the standard case
		gmTools.compare_dict_likes(self.current_encounter.fields_as_dict(), curr_enc_in_db.fields_as_dict(), 'modified enc in client', 'enc loaded from DB')
		_log.debug('active encounter modified remotely, no locally pending changes, reloading from DB and locally announcing the remote modification')
		self.current_encounter.refetch_payload()
		gmDispatcher.send('current_encounter_modified')
		return True

	#--------------------------------------------------------
	# API: family history
	#--------------------------------------------------------
	def get_family_history(self, episodes=None, issues=None, encounters=None):
		fhx = gmFamilyHistory.get_family_history (
			order_by = 'l10n_relation, condition',
			patient = self.pk_patient
		)

		if episodes is not None:
			fhx = [ f for f in fhx if f['pk_episode'] in episodes ]

		if issues is not None:
			fhx = [ f for f in fhx if f['pk_health_issue'] in issues ]

		if encounters is not None:
			fhx = [ f for f in fhx if f['pk_encounter'] in encounters ]

		return fhx

	#--------------------------------------------------------
	def add_family_history(self, episode=None, condition=None, relation=None):
		return gmFamilyHistory.create_family_history (
			encounter = self.current_encounter['pk_encounter'],
			episode = episode,
			condition = condition,
			relation = relation
		)

	#--------------------------------------------------------
	# API: pregnancy
	#--------------------------------------------------------
	def _get_gender(self):
		if self.__gender is not None:
			return self.__gender
		cmd = 'SELECT gender, dob FROM dem.v_all_persons WHERE pk_identity = %(pat)s'
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		self.__gender = rows[0]['gender']
		self.__dob = rows[0]['dob']

	def _set_gender(self, gender):
		self.__gender = gender

	gender = property(_get_gender, _set_gender)

	#--------------------------------------------------------
	def _get_dob(self):
		if self.__dob is not None:
			return self.__dob
		cmd = 'SELECT gender, dob FROM dem.v_all_persons WHERE pk_identity = %(pat)s'
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		self.__gender = rows[0]['gender']
		self.__dob = rows[0]['dob']

	def _set_dob(self, dob):
		self.__dob = dob

	dob = property(_get_dob, _set_dob)

	#--------------------------------------------------------
	def _get_EDC(self):
		cmd = 'SELECT edc FROM clin.patient WHERE fk_identity = %(pat)s'
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) == 0:
			return None
		return rows[0]['edc']

	def _set_EDC(self, edc):
		cmd = """
			INSERT INTO clin.patient (fk_identity, edc) SELECT
				%(pat)s,
				%(edc)s
			WHERE NOT EXISTS (
				SELECT 1 FROM clin.patient WHERE fk_identity = %(pat)s
			)
			RETURNING pk"""
		args = {'pat': self.pk_patient, 'edc': edc}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False, return_data = True)
		if len(rows) == 0:
			cmd = 'UPDATE clin.patient SET edc = %(edc)s WHERE fk_identity = %(pat)s'
			gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	EDC = property(_get_EDC, _set_EDC)

	#--------------------------------------------------------
	def _EDC_is_fishy(self):
		edc = self.EDC
		if edc is None:
			return False
		if self.gender != 'f':
			return True
		now = gmDateTime.pydt_now_here()
		# mother too young
		if (self.dob + pydt.timedelta(weeks = 5 * 52)) > now:
			return True
		# mother too old
		if (self.dob + pydt.timedelta(weeks = 55 * 52)) < now:
			return True
		# Beulah Hunter, 375 days (http://www.reference.com/motif/health/longest-human-pregnancy-on-record)
		# EDC too far in the future
		if (edc - pydt.timedelta(days = 380)) > now:
			return True
		# even if the pregnancy would have *started* when it
		# was documented to *end* it would be over by now by
		# all accounts
		# EDC too far in the past
		if edc < (now - pydt.timedelta(days = 380)):
			return True

	EDC_is_fishy = property(_EDC_is_fishy, lambda x:x)

	#--------------------------------------------------------
	def __normalize_smoking_details(self, details):
		try:
			details['quit_when']
		except KeyError:
			details['quit_when'] = None

		try:
			details['last_confirmed']
			if details['last_confirmed'] is None:
				details['last_confirmed'] = gmDateTime.pydt_now_here()
		except KeyError:
			details['last_confirmed'] = gmDateTime.pydt_now_here()

		try:
			details['comment']
			if details['comment'].strip() == '':
				details['comment'] = None
		except KeyError:
			details['comment'] = None

		return details

	#--------------------------------------------------------
	def _get_smoking_status(self):
		use = self.harmful_substance_use
		if use is None:
			return None
		return use['tobacco']

	def _set_smoking_status(self, status):
		# valid ?
		status_flag, details = status
		self.__harmful_substance_use = None
		args = {
			'pat': self.pk_patient,
			'status': status_flag
		}
		if status_flag is None:
			cmd = 'UPDATE clin.patient SET smoking_status = %(status)s, smoking_details = NULL WHERE fk_identity = %(pat)s'
		elif status_flag == 0:
			details['quit_when'] = None
			args['details'] = gmTools.dict2json(self.__normalize_smoking_details(details))
			cmd = 'UPDATE clin.patient SET smoking_status = %(status)s, smoking_details = %(details)s WHERE fk_identity = %(pat)s'
		else:
			args['details'] = gmTools.dict2json(self.__normalize_smoking_details(details))
			cmd = 'UPDATE clin.patient SET smoking_status = %(status)s, smoking_details = %(details)s WHERE fk_identity = %(pat)s'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	smoking_status = property(_get_smoking_status, _set_smoking_status)

	#--------------------------------------------------------
	def _get_alcohol_status(self):
		use = self.harmful_substance_use
		if use is None:
			return None
		return use['alcohol']

	def _set_alcohol_status(self, status):
		# valid ?
		harmful, details = status
		self.__harmful_substance_use = None
		args = {'pat': self.pk_patient}
		if harmful is None:
			cmd = 'UPDATE clin.patient SET c2_currently_harmful_use = NULL, c2_details = NULL WHERE fk_identity = %(pat)s'
		elif harmful is False:
			cmd = 'UPDATE clin.patient SET c2_currently_harmful_use = FALSE, c2_details = gm.nullify_empty_string(%(details)s) WHERE fk_identity = %(pat)s'
		else:
			cmd = 'UPDATE clin.patient SET c2_currently_harmful_use = TRUE, c2_details = gm.nullify_empty_string(%(details)s) WHERE fk_identity = %(pat)s'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	alcohol_status = property(_get_alcohol_status, _set_alcohol_status)

	#--------------------------------------------------------
	def _get_drugs_status(self):
		use = self.harmful_substance_use
		if use is None:
			return None
		return use['drugs']

	def _set_drugs_status(self, status):
		# valid ?
		harmful, details = status
		self.__harmful_substance_use = None
		args = {'pat': self.pk_patient}
		if harmful is None:
			cmd = 'UPDATE clin.patient SET drugs_currently_harmful_use = NULL, drugs_details = NULL WHERE fk_identity = %(pat)s'
		elif harmful is False:
			cmd = 'UPDATE clin.patient SET drugs_currently_harmful_use = FALSE, drugs_details = gm.nullify_empty_string(%(details)s) WHERE fk_identity = %(pat)s'
		else:
			cmd = 'UPDATE clin.patient SET drugs_currently_harmful_use = TRUE, drugs_details = gm.nullify_empty_string(%(details)s) WHERE fk_identity = %(pat)s'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	drugs_status = property(_get_drugs_status, _set_drugs_status)

	#--------------------------------------------------------
	def _get_harmful_substance_use(self):
		# caching does not take into account status changes from elsewhere
		try:
			self.__harmful_substance_use
		except AttributeError:
			self.__harmful_substance_use = None

		if self.__harmful_substance_use is not None:
			return self.__harmful_substance_use

		args = {'pat': self.pk_patient}
		cmd = """
			SELECT
				-- tobacco use
				smoking_status,
				smoking_details,
				(smoking_details->>'last_confirmed')::timestamp with time zone
					AS ts_last,
				(smoking_details->>'quit_when')::timestamp with time zone
					AS ts_quit,
				-- c2 use
				c2_currently_harmful_use,
				c2_details,
				-- other drugs use
				drugs_currently_harmful_use,
				drugs_details
			FROM clin.patient
			WHERE fk_identity = %(pat)s
		"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) == 0:
			return None
		# disentangle smoking
		status = rows[0]['smoking_status']
		details = rows[0]['smoking_details']
		if status is not None:
			details['last_confirmed'] = rows[0]['ts_last']
			details['quit_when'] = rows[0]['ts_quit']
		# set fields
		self.__harmful_substance_use = {
			'tobacco':  (status, details),
			'alcohol': (rows[0]['c2_currently_harmful_use'], rows[0]['c2_details']),
			'drugs': (rows[0]['drugs_currently_harmful_use'], rows[0]['drugs_details'])
		}

		return self.__harmful_substance_use


	def _get_harmful_substance_use2(self):
		cmd = 'SELECT * FROM clin.v_substance_intakes WHERE harmful_use_type  = %s'

	harmful_substance_use = property(_get_harmful_substance_use, lambda x:x)

	#--------------------------------------------------------
	def format_harmful_substance_use(self, include_tobacco=True, include_alcohol=True, include_drugs=True, include_nonuse=True, include_unknown=True):
		use = self.harmful_substance_use
		if use is None:
			return []

		lines = []

		if include_tobacco:
			status, details = use['tobacco']
			add_details = False
			if status is None:
				if include_unknown:
					lines.append(_('unknown smoking status'))
			elif status == 0:
				if include_nonuse:
					lines.append('%s (%s)' % (_('non-smoker'), gmDateTime.pydt_strftime(details['last_confirmed'], '%Y %b %d')))
					add_details = True
			elif status == 1:		# now or previous
				if details['quit_when'] is None:
					lines.append('%s (%s)' % (_('current smoker'), gmDateTime.pydt_strftime(details['last_confirmed'], '%Y %b %d')))
					add_details = True
				elif details['quit_when'] < gmDateTime.pydt_now_here():
					if include_nonuse:
						lines.append('%s (%s)' % (_('ex-smoker'), gmDateTime.pydt_strftime(details['last_confirmed'], '%Y %b %d')))
						add_details = True
				else:
					lines.append('%s (%s)' % (_('current smoker'), gmDateTime.pydt_strftime(details['last_confirmed'], '%Y %b %d')))
					add_details = True
			elif status == 2:		# addicted
				lines.append('%s (%s)' % (_('tobacco addiction'), gmDateTime.pydt_strftime(details['last_confirmed'], '%Y %b %d')))
				add_details = True
			if add_details:
				if details['quit_when'] is not None:
					lines.append(' %s: %s' % (_('Quit date'), gmDateTime.pydt_strftime(details['quit_when'], '%Y %b %d')))
				if details['comment'] is not None:
					lines.append(' %s' % details['comment'])

		if include_alcohol:
			status, details = use['alcohol']
			if status is False:
				if include_nonuse:
					if len(lines) > 0:
						lines.append('')
					lines.append(_('no or non-harmful alcohol use'))
					lines.append(' %s' % details)
			elif status is True:
				if len(lines) > 0:
					lines.append('')
				lines.append(_('harmful alcohol use'))
				lines.append(' %s' % details)
			else:
				if include_unknown:
					if len(lines) > 0:
						lines.append('')
					lines.append(_('unknown alcohol use'))
					lines.append(' %s' % details)

		if include_drugs:
			status, details = use['drugs']
			if status is False:
				if include_nonuse:
					if len(lines) > 0:
						lines.append('')
					lines.append(_('no or non-harmful drug use'))
					lines.append(' %s' % details)
			elif status is True:
				if len(lines) > 0:
					lines.append('')
				lines.append(_('harmful drug use'))
				lines.append(' %s' % details)
			else:
				if include_unknown:
					if len(lines) > 0:
						lines.append('')
					lines.append(_('unknown drug use'))
					lines.append(' %s' % details)

		return lines

	#--------------------------------------------------------
	def _get_currently_abuses_substances(self):
		# returns True / False / None (= unknown)

		use = self.harmful_substance_use
		# we know that at least one group is used:
		if use['alcohol'][0] is True:
			return True
		if use['drugs'][0] is True:
			return True
		if use['tobacco'][0] > 0:
		# is True:
			if use['tobacco'][1]['quit_when'] is None:
				return True
		# at this point no group is currently used for sure
		# we don't know about some of the groups so we can NOT say: no abuse at all:
		if use['alcohol'][0] is None:
			return None
		if use['drugs'][0] is None:
			return None
		if use['tobacco'][0] is None:
			return None
		# at this point all groups must be FALSE, except for
		# tobacco which can also be TRUE _but_, if so, a quit
		# date has been set, which is considered non-abuse
		return False

	currently_abuses_substances = property(_get_currently_abuses_substances, lambda x:x)

	#--------------------------------------------------------
	# API: performed procedures
	#--------------------------------------------------------
	def get_performed_procedures(self, episodes=None, issues=None):

		procs = gmEMRStructItems.get_performed_procedures(patient = self.pk_patient)

		if episodes is not None:
			procs = [ p for p in procs if p['pk_episode'] in episodes ]

		if issues is not None:
			procs = [ p for p in procs if p['pk_health_issue'] in issues ]

		return procs

	performed_procedures = property(get_performed_procedures, lambda x:x)
	#--------------------------------------------------------
	def get_latest_performed_procedure(self):
		return gmEMRStructItems.get_latest_performed_procedure(patient = self.pk_patient)
	#--------------------------------------------------------
	def add_performed_procedure(self, episode=None, location=None, hospital_stay=None, procedure=None):
		return gmEMRStructItems.create_performed_procedure (
			encounter = self.current_encounter['pk_encounter'],
			episode = episode,
			location = location,
			hospital_stay = hospital_stay,
			procedure = procedure
		)
	#--------------------------------------------------------
	def get_procedure_locations_as_org_units(self):
		where = 'pk_org_unit IN (SELECT DISTINCT pk_org_unit FROM clin.v_procedures_not_at_hospital WHERE pk_patient = %(pat)s)'
		args = {'pat': self.pk_patient}
		cmd = gmOrganization._SQL_get_org_unit % where
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmOrganization.cOrgUnit(row = {'pk_field': 'pk_org_unit', 'data': r, 'idx': idx}) for r in rows ]

	#--------------------------------------------------------
	# API: hospitalizations
	#--------------------------------------------------------
	def get_hospital_stays(self, episodes=None, issues=None, ongoing_only=False):
		stays = gmEMRStructItems.get_patient_hospital_stays(patient = self.pk_patient, ongoing_only = ongoing_only)
		if episodes is not None:
			stays = [ s for s in stays if s['pk_episode'] in episodes ]
		if issues is not None:
			stays = [ s for s in stays if s['pk_health_issue'] in issues ]
		return stays

	hospital_stays = property(get_hospital_stays, lambda x:x)
	#--------------------------------------------------------
	def get_latest_hospital_stay(self):
		return gmEMRStructItems.get_latest_patient_hospital_stay(patient = self.pk_patient)
	#--------------------------------------------------------
	def add_hospital_stay(self, episode=None, fk_org_unit=None):
		return gmEMRStructItems.create_hospital_stay (
			encounter = self.current_encounter['pk_encounter'],
			episode = episode,
			fk_org_unit = fk_org_unit
		)
	#--------------------------------------------------------
	def get_hospital_stay_stats_by_hospital(self, cover_period=None):
		args = {'pat': self.pk_patient, 'range': cover_period}
		where_parts = ['pk_patient = %(pat)s']
		if cover_period is not None:
			where_parts.append('discharge > (now() - %(range)s)')

		cmd = """
			SELECT hospital, count(1) AS frequency
			FROM clin.v_hospital_stays
			WHERE
				%s
			GROUP BY hospital
			ORDER BY frequency DESC
		""" % ' AND '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows
	#--------------------------------------------------------
	def get_attended_hospitals_as_org_units(self):
		where = 'pk_org_unit IN (SELECT DISTINCT pk_org_unit FROM clin.v_hospital_stays WHERE pk_patient = %(pat)s)'
		args = {'pat': self.pk_patient}
		cmd = gmOrganization._SQL_get_org_unit % where
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmOrganization.cOrgUnit(row = {'pk_field': 'pk_org_unit', 'data': r, 'idx': idx}) for r in rows ]

	#--------------------------------------------------------
	# API: narrative
	#--------------------------------------------------------
	def add_notes(self, notes=None, episode=None, encounter=None):
		enc = gmTools.coalesce (
			encounter,
			self.current_encounter['pk_encounter']
		)
		for note in notes:
			gmClinNarrative.create_narrative_item (
				narrative = note[1],
				soap_cat = note[0],
				episode_id = episode,
				encounter_id = enc
			)
		return True

	#--------------------------------------------------------
	def add_clin_narrative(self, note='', soap_cat='s', episode=None, link_obj=None):
		if note.strip() == '':
			_log.info('will not create empty clinical note')
			return None
		if isinstance(episode, gmEMRStructItems.cEpisode):
			episode = episode['pk_episode']
		instance = gmClinNarrative.create_narrative_item (
			link_obj = link_obj,
			narrative = note,
			soap_cat = soap_cat,
			episode_id = episode,
			encounter_id = self.current_encounter['pk_encounter']
		)
		return instance

	#--------------------------------------------------------
	def get_clin_narrative(self, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None):
		"""Get SOAP notes pertinent to this encounter.

			encounters
				- list of encounters the narrative of which are to be retrieved
			episodes
				- list of episodes the narrative of which are to be retrieved
			issues
				- list of health issues the narrative of which are to be retrieved
			soap_cats
				- list of SOAP categories of the narrative to be retrieved
		"""
		where_parts = ['pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if issues is not None:
			where_parts.append('pk_health_issue IN %(issues)s')
			if len(issues) == 0:
				args['issues'] = tuple()
			else:
				if isinstance(issues[0], gmEMRStructItems.cHealthIssue):
					args['issues'] = tuple([ i['pk_health_issue'] for i in issues ])
				elif isinstance(issues[0], int):
					args['issues'] = tuple(issues)
				else:
					raise ValueError('<issues> must be list of type int (=pk) or cHealthIssue, but 1st issue is: %s' % issues[0])

		if episodes is not None:
			where_parts.append('pk_episode IN %(epis)s')
			if len(episodes) == 0:
				args['epis'] = tuple()
			else:
				if isinstance(episodes[0], gmEMRStructItems.cEpisode):
					args['epis'] = tuple([ e['pk_episode'] for e in episodes ])
				elif isinstance(episodes[0], int):
					args['epis'] = tuple(episodes)
				else:
					raise ValueError('<episodes> must be list of type int (=pk) or cEpisode, but 1st episode is: %s' % episodes[0])

		if encounters is not None:
			where_parts.append('pk_encounter IN %(encs)s')
			if len(encounters) == 0:
				args['encs'] = tuple()
			else:
				if isinstance(encounters[0], gmEMRStructItems.cEncounter):
					args['encs'] = tuple([ e['pk_encounter'] for e in encounters ])
				elif isinstance(encounters[0], int):
					args['encs'] = tuple(encounters)
				else:
					raise ValueError('<encounters> must be list of type int (=pk) or cEncounter, but 1st encounter is: %s' % encounters[0])

		if soap_cats is not None:
			where_parts.append('c_vn.soap_cat IN %(cats)s')
			args['cats'] = tuple(gmSoapDefs.soap_cats2list(soap_cats))

		if providers is not None:
			where_parts.append('c_vn.modified_by IN %(docs)s')
			args['docs'] = tuple(providers)

		cmd = """
			SELECT
				c_vn.*,
				c_scr.rank AS soap_rank
			FROM
				clin.v_narrative c_vn
					LEFT JOIN clin.soap_cat_ranks c_scr on c_vn.soap_cat = c_scr.soap_cat
			WHERE %s
			ORDER BY date, soap_rank
		""" % ' AND '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmClinNarrative.cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': row}) for row in rows ]

	#--------------------------------------------------------
	def search_narrative_simple(self, search_term=''):

		search_term = search_term.strip()
		if search_term == '':
			return []

		cmd = """
			SELECT
				*,
				coalesce((SELECT description FROM clin.episode WHERE pk = vn4s.pk_episode), vn4s.src_table)
					as episode,
				coalesce((SELECT description FROM clin.health_issue WHERE pk = vn4s.pk_health_issue), vn4s.src_table)
					as health_issue,
				(SELECT started FROM clin.encounter WHERE pk = vn4s.pk_encounter)
					as encounter_started,
				(SELECT last_affirmed FROM clin.encounter WHERE pk = vn4s.pk_encounter)
					as encounter_ended,
				(SELECT _(description) FROM clin.encounter_type WHERE pk = (SELECT fk_type FROM clin.encounter WHERE pk = vn4s.pk_encounter))
					as encounter_type
-- CHANGE BACK IN V23:
			--FROM clin.v_narrative4search vn4s
			FROM v_narrative4search vn4s
			WHERE
				pk_patient = %(pat)s and
				vn4s.narrative ~ %(term)s
			order by
				encounter_started
		""" # case sensitive
		#rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pat': self.pk_patient, 'term': search_term}}])
		queries = [
			{'cmd': gmClinNarrative._VIEW_clin_v_narrative4search},
			{'cmd': cmd, 'args': {'pat': self.pk_patient, 'term': search_term}}
		]
		rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = True, return_data = True)
		return rows

	#--------------------------------------------------------
	def get_text_dump(self, since=None, until=None, encounters=None, episodes=None, issues=None):
		fields = [
			'age',
			"to_char(modified_when, 'YYYY-MM-DD @ HH24:MI') as modified_when",
			'modified_by',
			'clin_when',
			"case is_modified when false then '%s' else '%s' end as modified_string" % (_('original entry'), _('modified entry')),
			'pk_item',
			'pk_encounter',
			'pk_episode',
			'pk_health_issue',
			'src_table'
		]
		select_from = "SELECT %s FROM clin.v_pat_items" % ', '.join(fields)
		# handle constraint conditions
		where_snippets = []
		params = {}
		where_snippets.append('pk_patient=%(pat_id)s')
		params['pat_id'] = self.pk_patient
		if not since is None:
			where_snippets.append('clin_when >= %(since)s')
			params['since'] = since
		if not until is None:
			where_snippets.append('clin_when <= %(until)s')
			params['until'] = until
		# FIXME: these are interrelated, eg if we constrain encounter
		# we automatically constrain issue/episode, so handle that,
		# encounters
		if not encounters is None and len(encounters) > 0:
			params['enc'] = encounters
			if len(encounters) > 1:
				where_snippets.append('fk_encounter in %(enc)s')
			else:
				where_snippets.append('fk_encounter=%(enc)s')
		# episodes
		if not episodes is None and len(episodes) > 0:
			params['epi'] = episodes
			if len(episodes) > 1:
				where_snippets.append('fk_episode in %(epi)s')
			else:
				where_snippets.append('fk_episode=%(epi)s')
		# health issues
		if not issues is None and len(issues) > 0:
			params['issue'] = issues
			if len(issues) > 1:
				where_snippets.append('fk_health_issue in %(issue)s')
			else:
				where_snippets.append('fk_health_issue=%(issue)s')

		where_clause = ' and '.join(where_snippets)
		order_by = 'order by src_table, age'
		cmd = "%s WHERE %s %s" % (select_from, where_clause, order_by)

		rows, view_col_idx = gmPG.run_ro_query('historica', cmd, 1, params)
		if rows is None:
			_log.error('cannot load item links for patient [%s]' % self.pk_patient)
			return None

		# -- sort the data --
		# FIXME: by issue/encounter/episode, eg formatting
		# aggregate by src_table for item retrieval
		items_by_table = {}
		for item in rows:
			src_table = item[view_col_idx['src_table']]
			pk_item = item[view_col_idx['pk_item']]
			if src_table not in items_by_table:
				items_by_table[src_table] = {}
			items_by_table[src_table][pk_item] = item

		# get mapping for issue/episode IDs
		issues = self.get_health_issues()
		issue_map = {}
		for issue in issues:
			issue_map[issue['pk_health_issue']] = issue['description']
		episodes = self.get_episodes()
		episode_map = {}
		for episode in episodes:
			episode_map[episode['pk_episode']] = episode['description']
		emr_data = {}
		# get item data from all source tables
		ro_conn = self._conn_pool.GetConnection('historica')
		curs = ro_conn.cursor()
		for src_table in items_by_table:
			item_ids = list(items_by_table[src_table])
			# we don't know anything about the columns of
			# the source tables but, hey, this is a dump
			if len(item_ids) == 0:
				_log.info('no items in table [%s] ?!?' % src_table)
				continue
			elif len(item_ids) == 1:
				cmd = "SELECT * FROM %s WHERE pk_item=%%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, item_ids[0]):
					_log.error('cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "SELECT * FROM %s WHERE pk_item in %%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, (tuple(item_ids),)):
					_log.error('cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			rows = curs.fetchall()
			table_col_idx = gmPG.get_col_indices(curs)
			# format per-table items
			for row in rows:
				# FIXME: make this get_pkey_name()
				pk_item = row[table_col_idx['pk_item']]
				view_row = items_by_table[src_table][pk_item]
				age = view_row[view_col_idx['age']]
				# format metadata
				try:
					episode_name = episode_map[view_row[view_col_idx['pk_episode']]]
				except Exception:
					episode_name = view_row[view_col_idx['pk_episode']]
				try:
					issue_name = issue_map[view_row[view_col_idx['pk_health_issue']]]
				except Exception:
					issue_name = view_row[view_col_idx['pk_health_issue']]

				if age not in emr_data:
					emr_data[age] = []

				emr_data[age].append(
					_('%s: encounter (%s)') % (
						view_row[view_col_idx['clin_when']],
						view_row[view_col_idx['pk_encounter']]
					)
				)
				emr_data[age].append(_('health issue: %s') % issue_name)
				emr_data[age].append(_('episode     : %s') % episode_name)
				# format table specific data columns
				# - ignore those, they are metadata, some
				#   are in clin.v_pat_items data already
				cols2ignore = [
					'pk_audit', 'row_version', 'modified_when', 'modified_by',
					'pk_item', 'id', 'fk_encounter', 'fk_episode', 'pk'
				]
				col_data = []
				for col_name in table_col_idx:
					if col_name in cols2ignore:
						continue
					emr_data[age].append("=> %s: %s" % (col_name, row[table_col_idx[col_name]]))
				emr_data[age].append("----------------------------------------------------")
				emr_data[age].append("-- %s from table %s" % (
					view_row[view_col_idx['modified_string']],
					src_table
				))
				emr_data[age].append("-- written %s by %s" % (
					view_row[view_col_idx['modified_when']],
					view_row[view_col_idx['modified_by']]
				))
				emr_data[age].append("----------------------------------------------------")
		curs.close()
		return emr_data
	#--------------------------------------------------------
	def get_patient_ID(self):
		return self.pk_patient
	#--------------------------------------------------------
	def get_statistics(self):
		union_query = '\n	union all\n'.join ([
			"""
				SELECT ((
					-- all relevant health issues + active episodes WITH health issue
					SELECT COUNT(1)
					FROM clin.v_problem_list
					WHERE
						pk_patient = %(pat)s
							AND
						pk_health_issue is not null
				) + (
					-- active episodes WITHOUT health issue
					SELECT COUNT(1)
					FROM clin.v_problem_list
					WHERE
						pk_patient = %(pat)s
							AND
						pk_health_issue is null
				))""",
			'SELECT count(1) FROM clin.encounter WHERE fk_patient = %(pat)s',
			'SELECT count(1) FROM clin.v_pat_items WHERE pk_patient = %(pat)s',
			'SELECT count(1) FROM blobs.v_doc_med WHERE pk_patient = %(pat)s',
			'SELECT count(1) FROM clin.v_test_results WHERE pk_patient = %(pat)s',
			'SELECT count(1) FROM clin.v_hospital_stays WHERE pk_patient = %(pat)s',
			'SELECT count(1) FROM clin.v_procedures WHERE pk_patient = %(pat)s',
			# active and approved substances == medication
			"""
				SELECT count(1)
				FROM clin.v_substance_intakes
				WHERE
					pk_patient = %(pat)s
						AND
					is_currently_active IN (null, true)
						AND
					intake_is_approved_of IN (null, true)""",
			'SELECT count(1) FROM clin.v_vaccinations WHERE pk_patient = %(pat)s'
		])

		rows, idx = gmPG2.run_ro_queries (
			queries = [{'cmd': union_query, 'args': {'pat': self.pk_patient}}],
			get_col_idx = False
		)

		stats = dict (
			problems = rows[0][0],
			encounters = rows[1][0],
			items = rows[2][0],
			documents = rows[3][0],
			results = rows[4][0],
			stays = rows[5][0],
			procedures = rows[6][0],
			active_drugs = rows[7][0],
			vaccinations = rows[8][0]
		)

		return stats
	#--------------------------------------------------------
	def format_statistics(self):
		return _(
			'Medical problems: %(problems)s\n'
			'Total encounters: %(encounters)s\n'
			'Total EMR entries: %(items)s\n'
			'Active medications: %(active_drugs)s\n'
			'Documents: %(documents)s\n'
			'Test results: %(results)s\n'
			'Hospitalizations: %(stays)s\n'
			'Procedures: %(procedures)s\n'
			'Vaccinations: %(vaccinations)s'
		) % self.get_statistics()
	#--------------------------------------------------------
	def format_summary(self):

		cmd = "SELECT dob FROM dem.v_all_persons WHERE pk_identity = %(pk)s"
		args = {'pk': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		dob = rows[0]['dob']

		stats = self.get_statistics()
		first = self.get_first_encounter()
		last = self.get_last_encounter()
		probs = self.get_problems()

		txt = ''
		if len(probs) > 0:
			txt += _(' %s known problems, clinically relevant thereof:\n') % stats['problems']
		else:
			txt += _(' %s known problems\n') % stats['problems']
		for prob in probs:
			if not prob['clinically_relevant']:
				continue
			txt += '   \u00BB%s\u00AB (%s)\n' % (
				prob['problem'],
				gmTools.bool2subst(prob['problem_active'], _('active'), _('inactive'))
			)
		txt += '\n'
		txt += _(' %s encounters from %s to %s\n') % (
			stats['encounters'],
			gmDateTime.pydt_strftime(first['started'], '%Y %b %d'),
			gmDateTime.pydt_strftime(last['started'], '%Y %b %d')
		)
		txt += _(' %s active medications\n') % stats['active_drugs']
		txt += _(' %s documents\n') % stats['documents']
		txt += _(' %s test results\n') % stats['results']
		txt += _(' %s hospitalizations') % stats['stays']
		if stats['stays'] == 0:
			txt += '\n'
		else:
			txt += _(', most recently:\n%s\n') % self.get_latest_hospital_stay().format(left_margin = 3)
		# FIXME: perhaps only count "ongoing ones"
		txt += _(' %s performed procedures') % stats['procedures']
		if stats['procedures'] == 0:
			txt += '\n'
		else:
			txt += _(', most recently:\n%s\n') % self.get_latest_performed_procedure().format(left_margin = 3)

		txt += '\n'
		txt += _('Allergies and Intolerances\n')

		allg_state = self.allergy_state
		txt += (' ' + allg_state.state_string)
		if allg_state['last_confirmed'] is not None:
			txt += _(' (last confirmed %s)') % gmDateTime.pydt_strftime(allg_state['last_confirmed'], '%Y %b %d')
		txt += '\n'
		txt += gmTools.coalesce(allg_state['comment'], '', ' %s\n')
		for allg in self.get_allergies():
			txt += ' %s: %s\n' % (
				allg['descriptor'],
				gmTools.coalesce(allg['reaction'], _('unknown reaction'))
			)

		meds = self.get_current_medications(order_by = 'intake_is_approved_of DESC, substance')
		if len(meds) > 0:
			txt += '\n'
			txt += _('Medications and Substances')
			txt += '\n'
		for m in meds:
			txt += '%s\n' % m.format_as_single_line(left_margin = 1)

		fhx = self.get_family_history()
		if len(fhx) > 0:
			txt += '\n'
			txt += _('Family History')
			txt += '\n'
		for f in fhx:
			txt += '%s\n' % f.format(left_margin = 1)

		jobs = get_occupations(pk_identity = self.pk_patient)
		if len(jobs) > 0:
			txt += '\n'
			txt += _('Occupations')
			txt += '\n'
		for job in jobs:
			txt += ' %s%s\n' % (
				job['l10n_occupation'],
				gmTools.coalesce(job['activities'], '', ': %s')
			)

		vaccs = self.get_latest_vaccinations()
		if len(vaccs) > 0:
			txt += '\n'
			txt += _('Vaccinations')
			txt += '\n'
		inds = sorted(vaccs)
		for ind in inds:
			ind_count, vacc = vaccs[ind]
			if dob is None:
				age_given = ''
			else:
				age_given = ' @ %s' % gmDateTime.format_apparent_age_medically(gmDateTime.calculate_apparent_age (
					start = dob,
					end = vacc['date_given']
				))
			since = _('%s ago') % gmDateTime.format_interval_medically(vacc['interval_since_given'])
			txt += ' %s (%s%s): %s%s (%s %s%s%s)\n' % (
				ind,
				gmTools.u_sum,
				ind_count,
				#gmDateTime.pydt_strftime(vacc['date_given'], '%b %Y'),
				since,
				age_given,
				vacc['vaccine'],
				gmTools.u_left_double_angle_quote,
				vacc['batch_no'],
				gmTools.u_right_double_angle_quote
			)

		care = self.get_external_care_items(order_by = 'issue, organization, unit, provider', exclude_inactive = True)
		if len(care) > 0:
			txt += '\n'
			txt += _('External care')
			txt += '\n'
		for item in care:
			txt += ' %s: %s\n' % (
				item['issue'],
				gmTools.coalesce (
					item['provider'],
					'%s@%s' % (item['unit'], item['organization']),
					'%%s (%s@%s)' % (item['unit'], item['organization'])
				)
			)

		return txt

	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, patient=None):
		txt = ''
		for enc in self.get_encounters(skip_empty = True):
			txt += gmTools.u_box_horiz_4dashes * 70 + '\n'
			txt += enc.format (
				episodes = None,			# means: each touched upon
				left_margin = left_margin,
				patient = patient,
				fancy_header = False,
				with_soap = True,
				with_docs = True,
				with_tests = True,
				with_vaccinations = True,
				with_co_encountlet_hints = False,		# irrelevant
				with_rfe_aoe = True,
				with_family_history = True,
				by_episode = True
			)

		return txt

	#--------------------------------------------------------
	def get_as_journal(self, since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None, order_by=None, time_range=None):
		return gmClinNarrative.get_as_journal (
			patient = self.pk_patient,
			since = since,
			until = until,
			encounters = encounters,
			episodes = episodes,
			issues = issues,
			soap_cats = soap_cats,
			providers = providers,
			order_by = order_by,
			time_range = time_range,
			active_encounter = self.active_encounter
		)

	#------------------------------------------------------------------
	def get_generic_emr_items(self, pk_encounters=None, pk_episodes=None, pk_health_issues=None, use_active_encounter=False, order_by=None):
		if use_active_encounter:
			active_encounter = self.active_encounter
		else:
			active_encounter = None
		return gmGenericEMRItem.get_generic_emr_items (
			patient = self.pk_patient,
			encounters = pk_encounters,
			episodes = pk_episodes,
			issues = pk_health_issues,
			active_encounter = active_encounter,
			order_by = order_by
		)

	#--------------------------------------------------------
	# API: allergy
	#--------------------------------------------------------
	def get_allergies(self, remove_sensitivities=False, since=None, until=None, encounters=None, episodes=None, issues=None, ID_list=None):
		"""Retrieves patient allergy items.

			remove_sensitivities
				- retrieve real allergies only, without sensitivities
			since
				- initial date for allergy items
			until
				- final date for allergy items
			encounters
				- list of encounters whose allergies are to be retrieved
			episodes
				- list of episodes whose allergies are to be retrieved
			issues
				- list of health issues whose allergies are to be retrieved
        """
		cmd = "SELECT * FROM clin.v_pat_allergies WHERE pk_patient=%s order by descriptor"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx = True)
		filtered_allergies = []
		for r in rows:
			filtered_allergies.append(gmAllergy.cAllergy(row = {'data': r, 'idx': idx, 'pk_field': 'pk_allergy'}))

		# ok, let's constrain our list
		if ID_list is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['pk_allergy'] in ID_list ]
			if len(filtered_allergies) == 0:
				_log.error('no allergies of list [%s] found for patient [%s]' % (str(ID_list), self.pk_patient))
				# better fail here contrary to what we do elsewhere
				return None
			else:
				return filtered_allergies

		if remove_sensitivities:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['type'] == 'allergy' ]
		if since is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['date'] >= since ]
		if until is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['date'] < until ]
		if issues is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['pk_health_issue'] in issues ]
		if episodes is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['pk_episode'] in episodes ]
		if encounters is not None:
			filtered_allergies = [ allg for allg in filtered_allergies if allg['pk_encounter'] in encounters ]

		return filtered_allergies
	#--------------------------------------------------------
	def add_allergy(self, allergene=None, allg_type=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.current_encounter['pk_encounter']

		if episode_id is None:
			issue = self.add_health_issue(issue_name = _('Allergies/Intolerances'))
			epi = self.add_episode(episode_name = _('Allergy detail: %s') % allergene, pk_health_issue = issue['pk_health_issue'])
			episode_id = epi['pk_episode']

		new_allergy = gmAllergy.create_allergy (
			allergene = allergene,
			allg_type = allg_type,
			encounter_id = encounter_id,
			episode_id = episode_id
		)

		return new_allergy
	#--------------------------------------------------------
	def delete_allergy(self, pk_allergy=None):
		cmd = 'delete FROM clin.allergy WHERE pk=%(pk_allg)s'
		args = {'pk_allg': pk_allergy}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	#--------------------------------------------------------
	def is_allergic_to(self, atcs=None, inns=None, product_name=None):
		"""Cave: only use with one potential allergic agent
		otherwise you won't know which of the agents the allergy is to."""

		# we don't know the state
		if self.allergy_state is None:
			return None

		# we know there's no allergies
		if self.allergy_state == 0:
			return False

		args = {
			'atcs': atcs,
			'inns': inns,
			'prod_name': product_name,
			'pat': self.pk_patient
		}
		allergenes = []
		where_parts = []

		if len(atcs) == 0:
			atcs = None
		if atcs is not None:
			where_parts.append('atc_code in %(atcs)s')
		if len(inns) == 0:
			inns = None
		if inns is not None:
			where_parts.append('generics in %(inns)s')
			allergenes.extend(inns)
		if product_name is not None:
			where_parts.append('substance = %(prod_name)s')
			allergenes.append(product_name)

		if len(allergenes) != 0:
			where_parts.append('allergene in %(allgs)s')
			args['allgs'] = tuple(allergenes)

		cmd = """
SELECT * FROM clin.v_pat_allergies
WHERE
	pk_patient = %%(pat)s
	AND ( %s )""" % ' OR '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return False

		return gmAllergy.cAllergy(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_allergy'})
	#--------------------------------------------------------
	def _set_allergy_state(self, state):

		if state not in gmAllergy.allergy_states:
			raise ValueError('[%s].__set_allergy_state(): <state> must be one of %s' % (self.__class__.__name__, gmAllergy.allergy_states))

		allg_state = gmAllergy.ensure_has_allergy_state(encounter = self.current_encounter['pk_encounter'])
		allg_state['has_allergy'] = state
		allg_state.save_payload()
		return True

	def _get_allergy_state(self):
		return gmAllergy.ensure_has_allergy_state(encounter = self.current_encounter['pk_encounter'])

	allergy_state = property(_get_allergy_state, _set_allergy_state)
	#--------------------------------------------------------
	# API: external care
	#--------------------------------------------------------
	def get_external_care_items(self, order_by=None, exclude_inactive=False):
		return gmExternalCare.get_external_care_items (
			pk_identity = self.pk_patient,
			order_by = order_by,
			exclude_inactive = exclude_inactive
		)

	external_care_items = property(get_external_care_items, lambda x:x)

	#--------------------------------------------------------
	# API: episodes
	#--------------------------------------------------------
	def get_episodes(self, id_list=None, issues=None, open_status=None, order_by=None, unlinked_only=False):
		"""Fetches from backend patient episodes.

		id_list - Episodes' PKs list
		issues - Health issues' PKs list to filter episodes by
		open_status - return all (None) episodes, only open (True) or closed (False) one(s)
		"""
		if (unlinked_only is True) and (issues is not None):
			raise ValueError('<unlinked_only> cannot be TRUE if <issues> is not None')

		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by

		args = {
			'pat': self.pk_patient,
			'open': open_status
		}
		where_parts = ['pk_patient = %(pat)s']

		if open_status is not None:
			where_parts.append('episode_open IS %(open)s')

		if unlinked_only:
			where_parts.append('pk_health_issue is NULL')

		if issues is not None:
			where_parts.append('pk_health_issue IN %(issues)s')
			args['issues'] = tuple(issues)

		if id_list is not None:
			where_parts.append('pk_episode IN %(epis)s')
			args['epis'] = tuple(id_list)

		cmd = "SELECT * FROM clin.v_pat_episodes WHERE %s %s" % (
			' AND '.join(where_parts),
			order_by
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		return [ gmEMRStructItems.cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'}) for r in rows ]

	episodes = property(get_episodes, lambda x:x)
	#------------------------------------------------------------------
	def get_unlinked_episodes(self, open_status=None, order_by=None):
		return self.get_episodes(open_status = open_status, order_by = order_by, unlinked_only = True)

	unlinked_episodes = property(get_unlinked_episodes, lambda x:x)
	#------------------------------------------------------------------
	def get_episodes_by_encounter(self, pk_encounter=None):
		cmd = """SELECT distinct pk_episode
					from clin.v_pat_items
					WHERE pk_encounter=%(enc)s and pk_patient=%(pat)s"""
		args = {
			'enc': gmTools.coalesce(pk_encounter, self.current_encounter['pk_encounter']),
			'pat': self.pk_patient
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if len(rows) == 0:
			return []
		epis = []
		for row in rows:
			epis.append(row[0])
		return self.get_episodes(id_list=epis)
	#------------------------------------------------------------------
	def add_episode(self, episode_name=None, pk_health_issue=None, is_open=False, allow_dupes=False, link_obj=None):
		"""Add episode 'episode_name' for a patient's health issue.

		- silently returns if episode already exists
		"""
		episode = gmEMRStructItems.create_episode (
			link_obj = link_obj,
			pk_health_issue = pk_health_issue,
			episode_name = episode_name,
			is_open = is_open,
			encounter = self.current_encounter['pk_encounter'],
			allow_dupes = allow_dupes
		)
		return episode
	#--------------------------------------------------------
	def get_most_recent_episode(self, issue=None):
		# try to find the episode with the most recently modified clinical item
		issue_where = gmTools.coalesce (
			value2test = issue,
			return_instead = '',
			value2return = 'and pk_health_issue = %(issue)s'
		)
		cmd = """
SELECT pk
from clin.episode
WHERE pk = (
	SELECT distinct on(pk_episode) pk_episode
	from clin.v_pat_items
	WHERE
		pk_patient = %%(pat)s
			and
		modified_when = (
			SELECT max(vpi.modified_when)
			from clin.v_pat_items vpi
			WHERE vpi.pk_patient = %%(pat)s
		)
		%s
	-- guard against several episodes created at the same moment of time
	limit 1
	)""" % issue_where
		rows, idx = gmPG2.run_ro_queries(queries = [
			{'cmd': cmd, 'args': {'pat': self.pk_patient, 'issue': issue}}
		])
		if len(rows) != 0:
			return gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])

		# no clinical items recorded, so try to find
		# the youngest episode for this patient
		cmd = """
SELECT vpe0.pk_episode
from
	clin.v_pat_episodes vpe0
WHERE
	vpe0.pk_patient = %%(pat)s
		and
	vpe0.episode_modified_when = (
		SELECT max(vpe1.episode_modified_when)
		from clin.v_pat_episodes vpe1
		WHERE vpe1.pk_episode = vpe0.pk_episode
	)
	%s""" % issue_where
		rows, idx = gmPG2.run_ro_queries(queries = [
			{'cmd': cmd, 'args': {'pat': self.pk_patient, 'issue': issue}}
		])
		if len(rows) != 0:
			return gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])

		return None
	#--------------------------------------------------------
	def episode2problem(self, episode=None):
		return gmEMRStructItems.episode2problem(episode=episode)
	#--------------------------------------------------------
	# API: problems
	#--------------------------------------------------------
	def get_problems(self, episodes=None, issues=None, include_closed_episodes=False, include_irrelevant_issues=False):
		"""Retrieve a patient's problems.

		"Problems" are the UNION of:

			- issues which are .clinically_relevant
			- episodes which are .is_open

		Therefore, both an issue and the open episode
		thereof can each be listed as a problem.

		include_closed_episodes/include_irrelevant_issues will
		include	those -- which departs from the definition of
		the problem list being "active" items only ...

		episodes - episodes' PKs to filter problems by
		issues - health issues' PKs to filter problems by
		"""
		# FIXME: this could use a good measure of streamlining, probably

		args = {'pat': self.pk_patient}

		cmd = """SELECT pk_health_issue, pk_episode FROM clin.v_problem_list WHERE pk_patient = %(pat)s ORDER BY problem"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		# Instantiate problem items
		problems = []
		for row in rows:
			pk_args = {
				'pk_patient': self.pk_patient,
				'pk_health_issue': row['pk_health_issue'],
				'pk_episode': row['pk_episode']
			}
			problems.append(gmEMRStructItems.cProblem(aPK_obj = pk_args, try_potential_problems = False))

		# include non-problems ?
		other_rows = []
		if include_closed_episodes:
			cmd = """SELECT pk_health_issue, pk_episode FROM clin.v_potential_problem_list WHERE pk_patient = %(pat)s and type = 'episode'"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			other_rows.extend(rows)

		if include_irrelevant_issues:
			cmd = """SELECT pk_health_issue, pk_episode FROM clin.v_potential_problem_list WHERE pk_patient = %(pat)s and type = 'health issue'"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			other_rows.extend(rows)

		if len(other_rows) > 0:
			for row in other_rows:
				pk_args = {
					'pk_patient': self.pk_patient,
					'pk_health_issue': row['pk_health_issue'],
					'pk_episode': row['pk_episode']
				}
				problems.append(gmEMRStructItems.cProblem(aPK_obj = pk_args, try_potential_problems = True))

		# filter
		if issues is not None:
			problems = [ p for p in problems if p['pk_health_issue'] in issues ]
		if episodes is not None:
			problems = [ p for p in problems if p['pk_episode'] in episodes ]

		return problems

	#--------------------------------------------------------
	def problem2episode(self, problem=None):
		return gmEMRStructItems.problem2episode(problem = problem)

	#--------------------------------------------------------
	def problem2issue(self, problem=None):
		return gmEMRStructItems.problem2issue(problem = problem)

	#--------------------------------------------------------
	def reclass_problem(self, problem):
		return gmEMRStructItems.reclass_problem(problem = problem)

	#--------------------------------------------------------
	def get_candidate_diagnoses(self):
		cmd = "SELECT * FROM clin.v_candidate_diagnoses WHERE pk_patient = %(pat)s"
		rows, idx = gmPG2.run_ro_queries (
			queries = [{'cmd': cmd, 'args': {'pat': self.pk_patient}}],
			get_col_idx = False
		)
		return rows

	candidate_diagnoses = property(get_candidate_diagnoses)

	#--------------------------------------------------------
	# API: health issues
	#--------------------------------------------------------
	def get_health_issues(self, id_list = None):

		cmd = "SELECT *, xmin_health_issue FROM clin.v_health_issues WHERE pk_patient = %(pat)s ORDER BY description"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pat': self.pk_patient}}], get_col_idx = True)
		issues = [ gmEMRStructItems.cHealthIssue(row = {'idx': idx, 'data': r, 'pk_field': 'pk_health_issue'}) for r in rows ]

		if id_list is None:
			return issues

		if len(id_list) == 0:
			raise ValueError('id_list to filter by is empty, most likely a programming error')

		filtered_issues = []
		for issue in issues:
			if issue['pk_health_issue'] in id_list:
				filtered_issues.append(issue)

		return filtered_issues

	health_issues = property(get_health_issues, lambda x:x)

	#------------------------------------------------------------------
	def add_health_issue(self, issue_name=None):
		"""Adds patient health issue."""
		return gmEMRStructItems.create_health_issue (
			description = issue_name,
			encounter = self.current_encounter['pk_encounter'],
			patient = self.pk_patient
		)
	#--------------------------------------------------------
	def health_issue2problem(self, issue=None):
		return gmEMRStructItems.health_issue2problem(issue = issue)
	#--------------------------------------------------------
	# API: substance intake
	#--------------------------------------------------------
	def get_current_medications(self, include_inactive=True, include_unapproved=False, order_by=None, episodes=None, issues=None):
		return self._get_current_substance_intakes (
			include_inactive = include_inactive,
			include_unapproved = include_unapproved,
			order_by = order_by,
			episodes = episodes,
			issues = issues,
			exclude_medications = False,
			exclude_potential_abuses = True
		)

	#--------------------------------------------------------
	def _get_abused_substances(self, order_by=None):
		return self._get_current_substance_intakes (
			include_inactive = True,
			include_unapproved = True,
			order_by = order_by,
			episodes = None,
			issues = None,
			exclude_medications = True,
			exclude_potential_abuses = False
		)

	abused_substances = property(_get_abused_substances, lambda x:x)

	#--------------------------------------------------------
	def _get_current_substance_intakes(self, include_inactive=True, include_unapproved=False, order_by=None, episodes=None, issues=None, exclude_potential_abuses=False, exclude_medications=False):

		where_parts = ['pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if not include_inactive:
			where_parts.append('is_currently_active IN (TRUE, NULL)')

		if not include_unapproved:
			where_parts.append('intake_is_approved_of IN (TRUE, NULL)')

		if exclude_potential_abuses:
			where_parts.append('harmful_use_type IS NULL')

		if exclude_medications:
			where_parts.append('harmful_use_type IS NOT NULL')

		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by

		cmd = "SELECT * FROM clin.v_substance_intakes WHERE %s %s" % (
			'\nAND '.join(where_parts),
			order_by
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		intakes = [ gmMedication.cSubstanceIntakeEntry(row = {'idx': idx, 'data': r, 'pk_field': 'pk_substance_intake'})  for r in rows ]

		if episodes is not None:
			intakes = [ i for i in intakes if i['pk_episode'] in episodes  ]

		if issues is not None:
			intakes = [ i for i in intakes if i ['pk_health_issue'] in issues ]

		return intakes

	#--------------------------------------------------------
	def add_substance_intake(self, pk_component=None, pk_episode=None, pk_drug_product=None, pk_health_issue=None):
		pk_enc = self.current_encounter['pk_encounter']
		if pk_episode is None:
			pk_episode = gmMedication.create_default_medication_history_episode (
				pk_health_issue = pk_health_issue,
				encounter = pk_enc
			)
		return gmMedication.create_substance_intake (
			pk_component = pk_component,
			pk_encounter = pk_enc,
			pk_episode = pk_episode,
			pk_drug_product = pk_drug_product
		)

	#--------------------------------------------------------
	def substance_intake_exists(self, pk_component=None, pk_substance=None, pk_drug_product=None):
		return gmMedication.substance_intake_exists (
			pk_component = pk_component,
			pk_substance = pk_substance,
			pk_identity = self.pk_patient,
			pk_drug_product = pk_drug_product
		)

	#--------------------------------------------------------
	# API: vaccinations
	#--------------------------------------------------------
	def add_vaccination(self, episode=None, vaccine=None, batch_no=None):
		return gmVaccination.create_vaccination (
			encounter = self.current_encounter['pk_encounter'],
			episode = episode,
			vaccine = vaccine,
			batch_no = batch_no
		)

	#--------------------------------------------------------
	def get_latest_vaccinations(self, episodes=None, issues=None, atc_indications=None):
		"""Returns latest given vaccination for each vaccinated indication.

		as a dict {'l10n_indication': cVaccination instance}

		Note that this will produce duplicate vaccination instances on combi-indication vaccines !
		"""
		args = {'pat': self.pk_patient}
		where_parts = ['c_v_shots.pk_patient = %(pat)s']

		if (episodes is not None) and (len(episodes) > 0):
			where_parts.append('c_v_shots.pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		if (issues is not None) and (len(issues) > 0):
			where_parts.append('c_v_shots.pk_episode IN (select pk from clin.episode where fk_health_issue IN %(issues)s)')
			args['issues'] = tuple(issues)

		if (atc_indications is not None) and (len(atc_indications) > 0):
			where_parts.append('c_v_plv4i.atc_indication IN %(atc_inds)s')
			args['atc_inds'] = tuple(atc_indications)

		# find the shots
		cmd = """
			SELECT
				c_v_shots.*,
				c_v_plv4i.l10n_indication,
				c_v_plv4i.no_of_shots
			FROM
				clin.v_vaccinations c_v_shots
					JOIN clin.v_pat_last_vacc4indication c_v_plv4i ON (c_v_shots.pk_vaccination = c_v_plv4i.pk_vaccination)
			WHERE %s
		""" % '\nAND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		# none found
		if len(rows) == 0:
			return {}

		# turn them into vaccinations
		# (idx is constant)
		vaccs = {}
		for shot_row in rows:
			vaccs[shot_row['l10n_indication']] = (
				shot_row['no_of_shots'],
				gmVaccination.cVaccination(row = {'idx': idx, 'data': shot_row, 'pk_field': 'pk_vaccination'})
			)

		return vaccs

	#--------------------------------------------------------
	def get_vaccinations(self, order_by=None, episodes=None, issues=None, encounters=None):
		return gmVaccination.get_vaccinations (
			pk_identity = self.pk_patient,
			pk_episodes = episodes,
			pk_health_issues = issues,
			pk_encounters = encounters,
			order_by = order_by,
			return_pks = False
		)

	vaccinations = property(get_vaccinations, lambda x:x)

	#--------------------------------------------------------
	# old/obsolete:
	#--------------------------------------------------------
	def get_scheduled_vaccination_regimes(self, ID=None, indications=None):
		"""Retrieves vaccination regimes the patient is on.

			optional:
			* ID - PK of the vaccination regime	
			* indications - indications we want to retrieve vaccination
				regimes for, must be primary language, not l10n_indication
		"""
		# FIXME: use course, not regime
		# retrieve vaccination regimes definitions
		cmd = """SELECT distinct on(pk_course) pk_course
				 FROM clin.v_vaccs_scheduled4pat
				 WHERE pk_patient=%s"""
		rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
		if rows is None:
			_log.error('cannot retrieve scheduled vaccination courses')
			return None
		# Instantiate vaccination items and keep cache
		for row in rows:
			self.__db_cache['vaccinations']['scheduled regimes'].append(gmVaccination.cVaccinationCourse(aPK_obj=row[0]))

		# ok, let's constrain our list
		filtered_regimes = []
		filtered_regimes.extend(self.__db_cache['vaccinations']['scheduled regimes'])
		if ID is not None:
			filtered_regimes = [ r for r in filtered_regimes if r['pk_course'] == ID ]
			if len(filtered_regimes) == 0:
				_log.error('no vaccination course [%s] found for patient [%s]' % (ID, self.pk_patient))
				return []
			else:
				return filtered_regimes[0]
		if indications is not None:
			filtered_regimes = [ r for r in filtered_regimes if r['indication'] in indications ]

		return filtered_regimes
	#--------------------------------------------------------
#	def get_vaccinated_indications(self):
#		"""Retrieves patient vaccinated indications list.
#
#		Note that this does NOT rely on the patient being on
#		some schedule or other but rather works with what the
#		patient has ACTUALLY been vaccinated against. This is
#		deliberate !
#		"""
#		# most likely, vaccinations will be fetched close
#		# by so it makes sense to count on the cache being
#		# filled (or fill it for nearby use)
#		vaccinations = self.get_vaccinations()
#		if vaccinations is None:
#			_log.error('cannot load vaccinated indications for patient [%s]' % self.pk_patient)
#			return (False, [[_('ERROR: cannot retrieve vaccinated indications'), _('ERROR: cannot retrieve vaccinated indications')]])
#		if len(vaccinations) == 0:
#			return (True, [[_('no vaccinations recorded'), _('no vaccinations recorded')]])
#		v_indications = []
#		for vacc in vaccinations:
#			tmp = [vacc['indication'], vacc['l10n_indication']]
#			# remove duplicates
#			if tmp in v_indications:
#				continue
#			v_indications.append(tmp)
#		return (True, v_indications)
	#--------------------------------------------------------
	def get_vaccinations_old(self, ID=None, indications=None, since=None, until=None, encounters=None, episodes=None, issues=None):
		"""Retrieves list of vaccinations the patient has received.

		optional:
		* ID - PK of a vaccination
		* indications - indications we want to retrieve vaccination
			items for, must be primary language, not l10n_indication
        * since - initial date for allergy items
        * until - final date for allergy items
        * encounters - list of encounters whose allergies are to be retrieved
        * episodes - list of episodes whose allergies are to be retrieved
        * issues - list of health issues whose allergies are to be retrieved
		"""
		try:
			self.__db_cache['vaccinations']['vaccinated']
		except KeyError:
			self.__db_cache['vaccinations']['vaccinated'] = []
			# Important fetch ordering by indication, date to know if a vaccination is booster
			cmd= """SELECT * FROM clin.v_pat_vaccinations4indication
					WHERE pk_patient=%s
 					order by indication, date"""
			rows, idx  = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.error('cannot load given vaccinations for patient [%s]' % self.pk_patient)
				del self.__db_cache['vaccinations']['vaccinated']
				return None
			# Instantiate vaccination items
			vaccs_by_ind = {}
			for row in rows:
				vacc_row = {
					'pk_field': 'pk_vaccination',
					'idx': idx,
					'data': row
				}
				vacc = gmVaccination.cVaccination(row=vacc_row)
				self.__db_cache['vaccinations']['vaccinated'].append(vacc)
				# keep them, ordered by indication
				try:
					vaccs_by_ind[vacc['indication']].append(vacc)
				except KeyError:
					vaccs_by_ind[vacc['indication']] = [vacc]

			# calculate sequence number and is_booster
			for ind in vaccs_by_ind:
				vacc_regimes = self.get_scheduled_vaccination_regimes(indications = [ind])
				for vacc in vaccs_by_ind[ind]:
					# due to the "order by indication, date" the vaccinations are in the
					# right temporal order inside the indication-keyed dicts
					seq_no = vaccs_by_ind[ind].index(vacc) + 1
					vacc['seq_no'] = seq_no
					# if no active schedule for indication we cannot
					# check for booster status (eg. seq_no > max_shot)
					if (vacc_regimes is None) or (len(vacc_regimes) == 0):
						continue
					if seq_no > vacc_regimes[0]['shots']:
						vacc['is_booster'] = True
			del vaccs_by_ind

		# ok, let's constrain our list
		filtered_shots = []
		filtered_shots.extend(self.__db_cache['vaccinations']['vaccinated'])
		if ID is not None:
			filtered_shots = filter(lambda shot: shot['pk_vaccination'] == ID, filtered_shots)
			if len(filtered_shots) == 0:
				_log.error('no vaccination [%s] found for patient [%s]' % (ID, self.pk_patient))
				return None
			else:
				return filtered_shots[0]
		if since is not None:
			filtered_shots = filter(lambda shot: shot['date'] >= since, filtered_shots)
		if until is not None:
			filtered_shots = filter(lambda shot: shot['date'] < until, filtered_shots)
		if issues is not None:
			filtered_shots = filter(lambda shot: shot['pk_health_issue'] in issues, filtered_shots)
		if episodes is not None:
			filtered_shots = filter(lambda shot: shot['pk_episode'] in episodes, filtered_shots)
		if encounters is not None:
			filtered_shots = filter(lambda shot: shot['pk_encounter'] in encounters, filtered_shots)
		if indications is not None:
			filtered_shots = filter(lambda shot: shot['indication'] in indications, filtered_shots)
		return filtered_shots
	#--------------------------------------------------------
	def get_scheduled_vaccinations(self, indications=None):
		"""Retrieves vaccinations scheduled for a regime a patient is on.

		The regime is referenced by its indication (not l10n)

		* indications - List of indications (not l10n) of regimes we want scheduled
		                vaccinations to be fetched for
		"""
		try:
			self.__db_cache['vaccinations']['scheduled']
		except KeyError:
			self.__db_cache['vaccinations']['scheduled'] = []
			cmd = """SELECT * FROM clin.v_vaccs_scheduled4pat WHERE pk_patient=%s"""
			rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.error('cannot load scheduled vaccinations for patient [%s]' % self.pk_patient)
				del self.__db_cache['vaccinations']['scheduled']
				return None
			# Instantiate vaccination items
			for row in rows:
				vacc_row = {
					'pk_field': 'pk_vacc_def',
					'idx': idx,
					'data': row
				}
				self.__db_cache['vaccinations']['scheduled'].append(gmVaccination.cScheduledVaccination(row = vacc_row))

		# ok, let's constrain our list
		if indications is None:
			return self.__db_cache['vaccinations']['scheduled']
		filtered_shots = []
		filtered_shots.extend(self.__db_cache['vaccinations']['scheduled'])
		filtered_shots = filter(lambda shot: shot['indication'] in indications, filtered_shots)
		return filtered_shots
	#--------------------------------------------------------
	def get_missing_vaccinations(self, indications=None):
		try:
			self.__db_cache['vaccinations']['missing']
		except KeyError:
			self.__db_cache['vaccinations']['missing'] = {}
			# 1) non-booster
			self.__db_cache['vaccinations']['missing']['due'] = []
			# get list of (indication, seq_no) tuples
			cmd = "SELECT indication, seq_no FROM clin.v_pat_missing_vaccs WHERE pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.error('error loading (indication, seq_no) for due/overdue vaccinations for patient [%s]' % self.pk_patient)
				return None
			pk_args = {'pat_id': self.pk_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					pk_args['seq_no'] = row[1]
					self.__db_cache['vaccinations']['missing']['due'].append(gmVaccination.cMissingVaccination(aPK_obj=pk_args))

			# 2) boosters
			self.__db_cache['vaccinations']['missing']['boosters'] = []
			# get list of indications
			cmd = "SELECT indication, seq_no FROM clin.v_pat_missing_boosters WHERE pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.error('error loading indications for missing boosters for patient [%s]' % self.pk_patient)
				return None
			pk_args = {'pat_id': self.pk_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					self.__db_cache['vaccinations']['missing']['boosters'].append(gmVaccination.cMissingBooster(aPK_obj=pk_args))

		# if any filters ...
		if indications is None:
			return self.__db_cache['vaccinations']['missing']
		if len(indications) == 0:
			return self.__db_cache['vaccinations']['missing']
		# ... apply them
		filtered_shots = {
			'due': [],
			'boosters': []
		}
		for due_shot in self.__db_cache['vaccinations']['missing']['due']:
			if due_shot['indication'] in indications: #and due_shot not in filtered_shots['due']:
				filtered_shots['due'].append(due_shot)
		for due_shot in self.__db_cache['vaccinations']['missing']['boosters']:
			if due_shot['indication'] in indications: #and due_shot not in filtered_shots['boosters']:
				filtered_shots['boosters'].append(due_shot)
		return filtered_shots

	#------------------------------------------------------------------
	# API: encounters
	#------------------------------------------------------------------
	def _get_current_encounter(self):
		return self.__encounter

	def _set_current_encounter(self, encounter):
		# first ever setting ? -> fast path
		if self.__encounter is None:
			_log.debug('first setting of active encounter in this clinical record instance')
			encounter.lock(exclusive = False)		# lock new
			self.__encounter = encounter
			gmDispatcher.send('current_encounter_switched')
			return True

		# real switch -> slow path
		_log.debug('switching of active encounter')
		# fail if the currently active encounter has unsaved changes
		if self.__encounter.is_modified():
			gmTools.compare_dict_likes(self.__encounter, encounter, 'modified enc in client', 'enc to switch to')
			_log.error('current in client: %s', self.__encounter)
			raise ValueError('unsaved changes in active encounter [%s], cannot switch to another one [%s]' % (
				self.__encounter['pk_encounter'],
				encounter['pk_encounter']
			))

		prev_enc = self.__encounter
		encounter.lock(exclusive = False)		# lock new
		self.__encounter = encounter
		prev_enc.unlock(exclusive = False)		# unlock old
		gmDispatcher.send('current_encounter_switched')

		return True

	current_encounter = property(_get_current_encounter, _set_current_encounter)
	active_encounter = property(_get_current_encounter, _set_current_encounter)

	#--------------------------------------------------------
	def __setup_active_encounter(self):
		_log.debug('setting up active encounter for identity [%s]', self.pk_patient)

		# log access to patient record (HIPAA, for example)
		_delayed_execute(self.log_access, action = 'setting up active encounter for identity [%s]' % self.pk_patient)

		# cleanup (not async, because we don't want recent encounters
		# to become the active one just because they are recent)
		self.remove_empty_encounters()

		# activate very recent encounter if available
		if self.__activate_very_recent_encounter():
			return

		fairly_recent_enc = self.__get_fairly_recent_encounter()

		# create new encounter for the time being
		self.start_new_encounter()

		if fairly_recent_enc is None:
			return

		# but check whether user wants to continue a "fairly recent" one
		gmDispatcher.send (
			signal = 'ask_for_encounter_continuation',
			new_encounter = self.__encounter,
			fairly_recent_encounter = fairly_recent_enc
		)

	#------------------------------------------------------------------
	def __activate_very_recent_encounter(self):
		"""Try to attach to a "very recent" encounter if there is one.

		returns:
			False: no "very recent" encounter
	    	True: success
		"""
		cfg_db = gmCfg.cCfgSQL()
		min_ttl = cfg_db.get2 (
			option = 'encounter.minimum_ttl',
			workplace = _here.active_workplace,
			bias = 'user',
			default = '1 hour 30 minutes'
		)
		cmd = gmEMRStructItems.SQL_get_encounters % """pk_encounter = (
			SELECT pk_encounter
			FROM clin.v_most_recent_encounters
			WHERE
				pk_patient = %s
					and
				last_affirmed > (now() - %s::interval)
			ORDER BY
				last_affirmed DESC
			LIMIT 1
		)"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, min_ttl]}], get_col_idx = True)

		# none found
		if len(enc_rows) == 0:
			_log.debug('no <very recent> encounter (younger than [%s]) found' % min_ttl)
			return False

		_log.debug('"very recent" encounter [%s] found and re-activated' % enc_rows[0]['pk_encounter'])

		# attach to existing
		self.current_encounter = gmEMRStructItems.cEncounter(row = {'data': enc_rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})
		return True

	#------------------------------------------------------------------
	def __get_fairly_recent_encounter(self):
		cfg_db = gmCfg.cCfgSQL()
		min_ttl = cfg_db.get2 (
			option = 'encounter.minimum_ttl',
			workplace = _here.active_workplace,
			bias = 'user',
			default = '1 hour 30 minutes'
		)
		max_ttl = cfg_db.get2 (
			option = 'encounter.maximum_ttl',
			workplace = _here.active_workplace,
			bias = 'user',
			default = '6 hours'
		)

		# do we happen to have a "fairly recent" candidate ?
		cmd = gmEMRStructItems.SQL_get_encounters % """pk_encounter = (
			SELECT pk_encounter
			FROM clin.v_most_recent_encounters
			WHERE
				pk_patient=%s
					AND
				last_affirmed BETWEEN (now() - %s::interval) AND (now() - %s::interval)
			ORDER BY
				last_affirmed DESC
			LIMIT 1
		)"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, max_ttl, min_ttl]}], get_col_idx = True)

		# none found
		if len(enc_rows) == 0:
			_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
			return None

		_log.debug('"fairly recent" encounter [%s] found', enc_rows[0]['pk_encounter'])
		return gmEMRStructItems.cEncounter(row = {'data': enc_rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})

#	#------------------------------------------------------------------
#	def __check_for_fairly_recent_encounter(self):
#
#		cfg_db = gmCfg.cCfgSQL()
#		min_ttl = cfg_db.get2 (
#			option = u'encounter.minimum_ttl',
#			workplace = _here.active_workplace,
#			bias = u'user',
#			default = u'1 hour 30 minutes'
#		)
#		max_ttl = cfg_db.get2 (
#			option = u'encounter.maximum_ttl',
#			workplace = _here.active_workplace,
#			bias = u'user',
#			default = u'6 hours'
#		)
#
#		# do we happen to have a "fairly recent" candidate ?
#		cmd = gmEMRStructItems.SQL_get_encounters % u"""pk_encounter = (
#			SELECT pk_encounter
#			FROM clin.v_most_recent_encounters
#			WHERE
#				pk_patient=%s
#					AND
#				last_affirmed BETWEEN (now() - %s::interval) AND (now() - %s::interval)
#			ORDER BY
#				last_affirmed DESC
#			LIMIT 1
#		)"""
#		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, max_ttl, min_ttl]}], get_col_idx = True)
#
#		# none found
#		if len(enc_rows) == 0:
#			_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
#			return
#
#		_log.debug('"fairly recent" encounter [%s] found', enc_rows[0]['pk_encounter'])
#		fairly_recent_enc = gmEMRStructItems.cEncounter(row = {'data': enc_rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})
#		gmDispatcher.send(u'ask_for_encounter_continuation', current = self.__encounter, fairly_recent_encounter = fairly_recent_enc)

#	#------------------------------------------------------------------
#	def __activate_fairly_recent_encounter(self, allow_user_interaction=True):
#		"""Try to attach to a "fairly recent" encounter if there is one.
#
#		returns:
#			False: no "fairly recent" encounter, create new one
#	    	True: success
#		"""
#		if _func_ask_user is None:
#			_log.debug('cannot ask user for guidance, not looking for fairly recent encounter')
#			return False
#
#		if not allow_user_interaction:
#			_log.exception('user interaction not desired, not looking for fairly recent encounter')
#			return False
#
#		cfg_db = gmCfg.cCfgSQL()
#		min_ttl = cfg_db.get2 (
#			option = u'encounter.minimum_ttl',
#			workplace = _here.active_workplace,
#			bias = u'user',
#			default = u'1 hour 30 minutes'
#		)
#		max_ttl = cfg_db.get2 (
#			option = u'encounter.maximum_ttl',
#			workplace = _here.active_workplace,
#			bias = u'user',
#			default = u'6 hours'
#		)
#		cmd = u"""
#			SELECT pk_encounter
#			FROM clin.v_most_recent_encounters
#			WHERE
#				pk_patient=%s
#					AND
#				last_affirmed BETWEEN (now() - %s::interval) AND (now() - %s::interval)
#			ORDER BY
#				last_affirmed DESC"""
#		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, max_ttl, min_ttl]}])
#		# none found
#		if len(enc_rows) == 0:
#			_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
#			return False
#
#		_log.debug('"fairly recent" encounter [%s] found', enc_rows[0][0])
#
#		encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
#		# ask user whether to attach or not
#		cmd = u"""
#			SELECT title, firstnames, lastnames, gender, dob
#			FROM dem.v_all_persons WHERE pk_identity=%s"""
#		pats, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
#		pat = pats[0]
#		pat_str = u'%s %s %s (%s), %s  [#%s]' % (
#			gmTools.coalesce(pat[0], u'')[:5],
#			pat[1][:15],
#			pat[2][:15],
#			pat[3],
#			gmDateTime.pydt_strftime(pat[4], '%Y %b %d'),
#			self.pk_patient
#		)
#		msg = _(
#			'%s\n'
#			'\n'
#			"This patient's chart was worked on only recently:\n"
#			'\n'
#			' %s  %s - %s  (%s)\n'
#			'\n'
#			' Reason for Encounter:\n'
#			'  %s\n'
#			' Assessment of Encounter:\n'
#			'  %s\n'
#			'\n'
#			'Do you want to continue that consultation\n'
#			'or do you want to start a new one ?\n'
#		) % (
#			pat_str,
#			gmDateTime.pydt_strftime(encounter['started'], '%Y %b %d'),
#			gmDateTime.pydt_strftime(encounter['started'], '%H:%M'), gmDateTime.pydt_strftime(encounter['last_affirmed'], '%H:%M'),
#			encounter['l10n_type'],
#			gmTools.coalesce(encounter['reason_for_encounter'], _('none given')),
#			gmTools.coalesce(encounter['assessment_of_encounter'], _('none given')),
#		)
#		attach = False
#		try:
#			attach = _func_ask_user(msg = msg, caption = _('Starting patient encounter'), encounter = encounter)
#		except Exception:
#			_log.exception('cannot ask user for guidance, not attaching to existing encounter')
#			return False
#		if not attach:
#			return False
#
#		# attach to existing
#		self.current_encounter = encounter
#		_log.debug('"fairly recent" encounter re-activated')
#		return True

	#------------------------------------------------------------------
	def start_new_encounter(self):
		cfg_db = gmCfg.cCfgSQL()
		enc_type = cfg_db.get2 (
			option = 'encounter.default_type',
			workplace = _here.active_workplace,
			bias = 'user'
		)
		if enc_type is None:
			enc_type = gmEMRStructItems.get_most_commonly_used_encounter_type()
		if enc_type is None:
			enc_type = 'in surgery'
		enc = gmEMRStructItems.create_encounter(fk_patient = self.pk_patient, enc_type = enc_type)
		enc['pk_org_unit'] = _here['pk_org_unit']
		enc.save()
		self.current_encounter = enc
		_log.debug('new encounter [%s] activated', enc['pk_encounter'])

	#------------------------------------------------------------------
	def get_encounters(self, since=None, until=None, id_list=None, episodes=None, issues=None, skip_empty=False, order_by=None, max_encounters=None):
		"""Retrieves patient's encounters.

		id_list - PKs of encounters to fetch
		since - initial date for encounter items, DateTime instance
		until - final date for encounter items, DateTime instance
		episodes - PKs of the episodes the encounters belong to (many-to-many relation)
		issues - PKs of the health issues the encounters belong to (many-to-many relation)
		skip_empty - do NOT return those which do not have any of documents/clinical items/RFE/AOE

		NOTE: if you specify *both* issues and episodes
		you will get the *aggregate* of all encounters even
		if the episodes all belong to the health issues listed.
		IOW, the issues broaden the episode list rather than
		the episode list narrowing the episodes-from-issues
		list.
		Rationale: If it was the other way round it would be
		redundant to specify the list of issues at all.
		"""
		# if issues are given, translate them to their episodes
		if (issues is not None) and (len(issues) > 0):
			# - find episodes corresponding to the health issues in question
			cmd = "SELECT distinct pk_episode FROM clin.v_pat_episodes WHERE pk_health_issue in %(issue_pks)s AND pk_patient = %(pat)s"
			args = {'issue_pks': tuple(issues), 'pat': self.pk_patient}
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
			epis4issues_pks = [ r['pk_episode']  for r in rows ]
			if episodes is None:
				episodes = []
			episodes.extend(epis4issues_pks)

		if (episodes is not None) and (len(episodes) > 0):
			# since the episodes to filter by belong to the patient in question so will
			# the encounters found with them - hence we don't need a WHERE on the patient ...
			# but, better safe than sorry ...
			args = {'epi_pks': tuple(episodes), 'pat': self.pk_patient}
			cmd = "SELECT distinct fk_encounter FROM clin.clin_root_item WHERE fk_episode IN %(epi_pks)s AND fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pat)s)"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
			encs4epis_pks = [ r['fk_encounter'] for r in rows ]
			if id_list is None:
				id_list = []
			id_list.extend(encs4epis_pks)

		where_parts = ['c_vpe.pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if skip_empty:
			where_parts.append("""NOT (
				gm.is_null_or_blank_string(c_vpe.reason_for_encounter)
					AND
				gm.is_null_or_blank_string(c_vpe.assessment_of_encounter)
					AND
				NOT EXISTS (
					SELECT 1 FROM clin.v_pat_items c_vpi WHERE c_vpi.pk_patient = %(pat)s AND c_vpi.pk_encounter = c_vpe.pk_encounter
						UNION ALL
					SELECT 1 FROM blobs.v_doc_med b_vdm WHERE b_vdm.pk_patient = %(pat)s AND b_vdm.pk_encounter = c_vpe.pk_encounter
				))""")

		if since is not None:
			where_parts.append('c_vpe.started >= %(start)s')
			args['start'] = since

		if until is not None:
			where_parts.append('c_vpe.last_affirmed <= %(end)s')
			args['end'] = since

		if (id_list is not None) and (len(id_list) > 0):
			where_parts.append('c_vpe.pk_encounter IN %(enc_pks)s')
			args['enc_pks'] = tuple(id_list)

		if order_by is None:
			order_by = 'c_vpe.started'

		if max_encounters is None:
			limit = ''
		else:
			limit = 'LIMIT %s' % max_encounters

		cmd = """
			SELECT * FROM clin.v_pat_encounters c_vpe
			WHERE
				%s
			ORDER BY %s %s
		""" % (
			' AND '.join(where_parts),
			order_by,
			limit
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		encounters = [ gmEMRStructItems.cEncounter(row = {'data': r, 'idx': idx, 'pk_field': 'pk_encounter'}) for r in rows ]

		# we've got the encounters, start filtering
		filtered_encounters = []
		filtered_encounters.extend(encounters)

		if (episodes is not None) and (len(episodes) > 0):
			# since the episodes to filter by belong to the patient in question so will
			# the encounters found with them - hence we don't need a WHERE on the patient ...
			# but, better safe than sorry ...
			args = {'epi_pks': tuple(episodes), 'pat': self.pk_patient}
			cmd = "SELECT distinct fk_encounter FROM clin.clin_root_item WHERE fk_episode IN %(epi_pks)s AND fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pat)s)"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
			encs4epis_pks = [ r['fk_encounter'] for r in rows ]
			filtered_encounters = [ enc for enc in filtered_encounters if enc['pk_encounter'] in encs4epis_pks ]

		return filtered_encounters

	#--------------------------------------------------------
	def get_first_encounter(self, issue_id=None, episode_id=None):
		"""Retrieves first encounter for a particular issue and/or episode.

		issue_id - First encounter associated health issue
		episode - First encounter associated episode
		"""
		if issue_id is None:
			issues = None
		else:
			issues = [issue_id]

		if episode_id is None:
			episodes = None
		else:
			episodes = [episode_id]

		encounters = self.get_encounters(issues = issues, episodes = episodes, order_by = 'started', max_encounters = 1)
		if len(encounters) == 0:
			return None

		return encounters[0]

	first_encounter = property(get_first_encounter, lambda x:x)

	#--------------------------------------------------------
	def get_earliest_care_date(self):
		args = {'pat': self.pk_patient}
		cmd = """
SELECT MIN(earliest) FROM (
	(
		SELECT MIN(episode_modified_when) AS earliest FROM clin.v_pat_episodes WHERE pk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(modified_when) AS earliest FROM clin.v_health_issues WHERE pk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(modified_when) AS earliest FROM clin.encounter WHERE fk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(started) AS earliest FROM clin.v_pat_encounters WHERE pk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(modified_when) AS earliest FROM clin.v_pat_items WHERE pk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(modified_when) AS earliest FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat)s

	) UNION ALL (

		SELECT MIN(last_confirmed) AS earliest FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat)s

	)
) AS candidates"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows[0][0]

	earliest_care_date = property(get_earliest_care_date, lambda x:x)

	#--------------------------------------------------------
	def get_most_recent_care_date(self):
		encounters = self.get_encounters(order_by = 'started DESC', max_encounters = 1)
		if len(encounters) == 0:
			return None
		return encounters[0]['last_affirmed']

	most_recent_care_date = property(get_most_recent_care_date)

	#--------------------------------------------------------
	def get_last_encounter(self, issue_id=None, episode_id=None):
		"""Retrieves last encounter for a concrete issue and/or episode

		issue_id - Last encounter associated health issue
		episode_id - Last encounter associated episode
		"""
		if issue_id is None:
			issues = None
		else:
			issues = [issue_id]

		if episode_id is None:
			episodes = None
		else:
			episodes = [episode_id]

		encounters = self.get_encounters(issues = issues, episodes = episodes, order_by = 'started DESC', max_encounters = 1)
		if len(encounters) == 0:
			return None

		return encounters[0]

	last_encounter = property(get_last_encounter, lambda x:x)

	#------------------------------------------------------------------
	def get_encounter_stats_by_type(self, cover_period=None):
		args = {'pat': self.pk_patient, 'range': cover_period}
		where_parts = ['pk_patient = %(pat)s']
		if cover_period is not None:
			where_parts.append('last_affirmed > now() - %(range)s')

		cmd = """
			SELECT l10n_type, count(1) AS frequency
			FROM clin.v_pat_encounters
			WHERE
				%s
			GROUP BY l10n_type
			ORDER BY frequency DESC
		""" % ' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows

	#------------------------------------------------------------------
	def get_last_but_one_encounter(self, issue_id=None, episode_id=None):

		args = {'pat': self.pk_patient}

		if (issue_id is None) and (episode_id is None):
			cmd = """
				SELECT * FROM clin.v_pat_encounters
				WHERE pk_patient = %(pat)s
				ORDER BY started DESC
				LIMIT 2
			"""
		else:
			where_parts = []

			if issue_id is not None:
				where_parts.append('pk_health_issue = %(issue)s')
				args['issue'] = issue_id

			if episode_id is not None:
				where_parts.append('pk_episode = %(epi)s')
				args['epi'] = episode_id

			cmd = """
				SELECT *
				FROM clin.v_pat_encounters
				WHERE
					pk_patient = %%(pat)s
						AND
					pk_encounter IN (
						SELECT distinct pk_encounter
						FROM clin.v_narrative
						WHERE
							%s
					)
				ORDER BY started DESC
				LIMIT 2
			""" % ' AND '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return None

		# just one encounter within the above limits
		if len(rows) == 1:
			# is it the current encounter ?
			if rows[0]['pk_encounter'] == self.current_encounter['pk_encounter']:
				# yes
				return None
			# no
			return gmEMRStructItems.cEncounter(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})

		# more than one encounter
		if rows[0]['pk_encounter'] == self.current_encounter['pk_encounter']:
			return gmEMRStructItems.cEncounter(row = {'data': rows[1], 'idx': idx, 'pk_field': 'pk_encounter'})

		return gmEMRStructItems.cEncounter(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})

	last_but_one_encounter = property(get_last_but_one_encounter, lambda x:x)

	#------------------------------------------------------------------
	def remove_empty_encounters(self):
		_log.debug('removing empty encounters for pk_identity [%s]', self.pk_patient)
		cfg_db = gmCfg.cCfgSQL()
		ttl = cfg_db.get2 (
			option = 'encounter.ttl_if_empty',
			workplace = _here.active_workplace,
			bias = 'user',
			default = '1 week'
		)
#		# FIXME: this should be done async
		cmd = "SELECT clin.remove_old_empty_encounters(%(pat)s::INTEGER, %(ttl)s::INTERVAL)"
		args = {'pat': self.pk_patient, 'ttl': ttl}
		try:
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
		except Exception:
			_log.exception('error deleting empty encounters')
			return False

		if not rows[0][0]:
			_log.debug('no encounters deleted (less than 2 exist)')

		return True

	#------------------------------------------------------------------
	# API: measurements / test results
	#------------------------------------------------------------------
	def get_most_recent_results_for_patient(self, no_of_results=1):
		return gmPathLab.get_most_recent_results_for_patient (
			no_of_results = no_of_results,
			patient = self.pk_patient
		)

	#------------------------------------------------------------------
	def get_most_recent_results_in_loinc_group(self, loincs=None, max_no_of_results=1, consider_indirect_matches=False):
		return gmPathLab.get_most_recent_results_in_loinc_group (
			loincs = loincs,
			max_no_of_results = max_no_of_results,
			patient = self.pk_patient,
			consider_indirect_matches = consider_indirect_matches
		)

	#------------------------------------------------------------------
	def get_most_recent_results_for_test_type(self, test_type=None, max_no_of_results=1):
		return gmPathLab.get_most_recent_results_for_test_type (
			test_type = test_type,
			max_no_of_results = max_no_of_results,
			patient = self.pk_patient
		)

	#------------------------------------------------------------------
	def get_most_recent_result_for_test_types(self, pk_test_types=None):
		return gmPathLab.get_most_recent_result_for_test_types (
			pk_test_types = pk_test_types,
			pk_patient = self.pk_patient
		)

	#------------------------------------------------------------------
	def get_result_at_timestamp(self, timestamp=None, test_type=None, loinc=None, tolerance_interval='12 hours'):
		return gmPathLab.get_result_at_timestamp (
			timestamp = timestamp,
			test_type = test_type,
			loinc = loinc,
			tolerance_interval = tolerance_interval,
			patient = self.pk_patient
		)

	#------------------------------------------------------------------
	def get_results_for_day(self, timestamp=None, order_by=None):
		return gmPathLab.get_results_for_day (
			timestamp = timestamp,
			patient = self.pk_patient,
			order_by = order_by
		)

	#------------------------------------------------------------------
	def get_results_for_issue(self, pk_health_issue=None, order_by=None):
		return gmPathLab.get_results_for_issue (
			pk_health_issue = pk_health_issue,
			order_by = order_by
		)

	#------------------------------------------------------------------
	def get_results_for_episode(self, pk_episode=None):
		return gmPathLab.get_results_for_episode(pk_episode = pk_episode)

	#------------------------------------------------------------------
	def get_unsigned_results(self, order_by=None):
		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by
		cmd = """
			SELECT * FROM clin.v_test_results
			WHERE
				pk_patient = %%(pat)s
					AND
				reviewed IS FALSE
			%s""" % order_by
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmPathLab.cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ]

	#------------------------------------------------------------------
	# FIXME: use psyopg2 dbapi extension of named cursors - they are *server* side !
	def get_test_types_for_results(self, order_by=None, unique_meta_types=False):
		"""Retrieve data about test types for which this patient has results."""
		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by

		if unique_meta_types:
			cmd = """
				SELECT * FROM clin.v_test_types c_vtt
				WHERE c_vtt.pk_test_type IN (
						SELECT DISTINCT ON (c_vtr1.pk_meta_test_type) c_vtr1.pk_test_type
						FROM clin.v_test_results c_vtr1
						WHERE
							c_vtr1.pk_patient = %%(pat)s
								AND
							c_vtr1.pk_meta_test_type IS NOT NULL
					UNION ALL
						SELECT DISTINCT ON (c_vtr2.pk_test_type) c_vtr2.pk_test_type
						FROM clin.v_test_results c_vtr2
						WHERE
							c_vtr2.pk_patient = %%(pat)s
								AND
							c_vtr2.pk_meta_test_type IS NULL
				)
				%s""" % order_by
		else:
			cmd = """
				SELECT * FROM clin.v_test_types c_vtt
				WHERE c_vtt.pk_test_type IN (
					SELECT DISTINCT ON (c_vtr.pk_test_type) c_vtr.pk_test_type
					FROM clin.v_test_results c_vtr
					WHERE c_vtr.pk_patient = %%(pat)s
				)
				%s""" % order_by

		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmPathLab.cMeasurementType(row = {'pk_field': 'pk_test_type', 'idx': idx, 'data': r}) for r in rows ]

	#------------------------------------------------------------------
	def get_dates_for_results(self, tests=None, reverse_chronological=True):
		"""Get the dates for which we have results."""
		where_parts = ['pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if tests is not None:
			where_parts.append('pk_test_type IN %(tests)s')
			args['tests'] = tuple(tests)

		cmd = """
			SELECT DISTINCT ON (clin_when_day)
				clin_when_day,
				is_reviewed
			FROM (
				SELECT
					date_trunc('day', clin_when)
						AS clin_when_day,
					bool_and(reviewed)
						AS is_reviewed
				FROM (
					SELECT
						clin_when,
						reviewed,
						pk_patient,
						pk_test_result
					FROM clin.v_test_results
					WHERE %s
				)
					AS patient_tests
				GROUP BY clin_when_day
			)
				AS grouped_days
			ORDER BY clin_when_day %s
		""" % (
			' AND '.join(where_parts),
			gmTools.bool2subst(reverse_chronological, 'DESC', 'ASC', 'DESC')
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows

	#------------------------------------------------------------------
	def get_issues_or_episodes_for_results(self, tests=None):
		"""Get the issues/episodes for which we have results."""
		where_parts = ['pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if tests is not None:
			where_parts.append('pk_test_type IN %(tests)s')
			args['tests'] = tuple(tests)
		where = ' AND '.join(where_parts)
		cmd = """
		SELECT * FROM ((
			-- issues, each including all it"s episodes
			SELECT
				health_issue AS problem,
				pk_health_issue,
				NULL::integer AS pk_episode,
				1 AS rank
			FROM clin.v_test_results
			WHERE pk_health_issue IS NOT NULL AND %s
			GROUP BY pk_health_issue, problem
		) UNION ALL (
			-- episodes w/o issue
			SELECT
				episode AS problem,
				NULL::integer AS pk_health_issue,
				pk_episode,
				2 AS rank
			FROM clin.v_test_results
			WHERE pk_health_issue IS NULL AND %s
			GROUP BY pk_episode, problem
		)) AS grouped_union
		ORDER BY rank, problem
		""" % (where, where)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows

	#------------------------------------------------------------------
	def get_test_results(self, encounters=None, episodes=None, tests=None, order_by=None):
		return gmPathLab.get_test_results (
			pk_patient = self.pk_patient,
			encounters = encounters,
			episodes = episodes,
			order_by = order_by
		)
	#------------------------------------------------------------------
	def get_test_results_by_date(self, encounter=None, episodes=None, tests=None, reverse_chronological=True):

		where_parts = ['pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if tests is not None:
			where_parts.append('pk_test_type IN %(tests)s')
			args['tests'] = tuple(tests)

		if encounter is not None:
			where_parts.append('pk_encounter = %(enc)s')
			args['enc'] = encounter

		if episodes is not None:
			where_parts.append('pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		cmd = """
			SELECT * FROM clin.v_test_results
			WHERE %s
			ORDER BY clin_when %s, pk_episode, unified_name
		""" % (
			' AND '.join(where_parts),
			gmTools.bool2subst(reverse_chronological, 'DESC', 'ASC', 'DESC')
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		tests = [ gmPathLab.cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ]

		return tests
	#------------------------------------------------------------------
	def add_test_result(self, episode=None, type=None, intended_reviewer=None, val_num=None, val_alpha=None, unit=None, link_obj=None):

		try:
			epi = int(episode)
		except Exception:
			epi = episode['pk_episode']

		try:
			type = int(type)
		except Exception:
			type = type['pk_test_type']

		tr = gmPathLab.create_test_result (
			link_obj = link_obj,
			encounter = self.current_encounter['pk_encounter'],
			episode = epi,
			type = type,
			intended_reviewer = intended_reviewer,
			val_num = val_num,
			val_alpha = val_alpha,
			unit = unit
		)

		return tr

	#------------------------------------------------------------------
	def get_labs_as_org_units(self):
		where = 'pk_org_unit IN (%s)' % """
			SELECT DISTINCT fk_org_unit FROM clin.test_org WHERE pk IN (
				SELECT DISTINCT pk_test_org FROM clin.v_test_results where pk_patient = %(pat)s
			)"""
		args = {'pat': self.pk_patient}
		cmd = gmOrganization._SQL_get_org_unit % where
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmOrganization.cOrgUnit(row = {'pk_field': 'pk_org_unit', 'data': r, 'idx': idx}) for r in rows ]

	#------------------------------------------------------------------
	def _get_best_gfr_or_crea(self):
		measured_gfrs = self.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		measured_gfr = measured_gfrs[0] if len(measured_gfrs) > 0 else None
		creas = self.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		crea = creas[0] if len(creas) > 0 else None

		if (measured_gfr is None) and (crea is None):
			return None

		if (measured_gfr is not None) and (crea is None):
			return measured_gfr

		# from here, Crea cannot be None anymore
		if measured_gfr is None:
			eGFR = self.calculator.eGFR
			if eGFR.numeric_value is None:
				return crea
			return eGFR

		# from here, measured_gfr cannot be None anymore, either
		two_weeks = pydt.timedelta(weeks = 2)
		gfr_too_old = (crea['clin_when'] - measured_gfr['clin_when']) > two_weeks
		if not gfr_too_old:
			return measured_gfr

		# from here, measured_gfr is considered too
		# old, so attempt a more timely estimate
		eGFR = self.calculator.eGFR
		if eGFR.numeric_value is None:
			# return crea since we cannot get a
			# better estimate for some reason
			return crea

		return eGFR

	best_gfr_or_crea = property(_get_best_gfr_or_crea, lambda x:x)

	#------------------------------------------------------------------
	def _get_bmi(self):
		return self.calculator.bmi

	bmi = property(_get_bmi, lambda x:x)

	#------------------------------------------------------------------
	def _get_dynamic_hints(self):
		return gmAutoHints.get_hints_for_patient(pk_identity = self.pk_patient, pk_encounter = self.current_encounter['pk_encounter'])

	dynamic_hints = property(_get_dynamic_hints, lambda x:x)

	#------------------------------------------------------------------
	#------------------------------------------------------------------
	#------------------------------------------------------------------
	def get_lab_request(self, pk=None, req_id=None, lab=None):
		# FIXME: verify that it is our patient ? ...
		req = gmPathLab.cLabRequest(aPK_obj=pk, req_id=req_id, lab=lab)
		return req
	#------------------------------------------------------------------
	def add_lab_request(self, lab=None, req_id=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.current_encounter['pk_encounter']
		status, data = gmPathLab.create_lab_request(
			lab=lab,
			req_id=req_id,
			pat_id=self.pk_patient,
			encounter_id=encounter_id,
			episode_id=episode_id
		)
		if not status:
			_log.error(str(data))
			return None
		return data

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2

	from Gnumed.business import gmPraxis
	branches = gmPraxis.get_praxis_branches()
	praxis = gmPraxis.gmCurrentPraxisBranch(branches[0])

	def _do_delayed(*args, **kwargs):
		print(args)
		print(kwargs)
		args[0](*args[1:], **kwargs)

	set_delayed_executor(_do_delayed)

	#-----------------------------------------
	def test_allergy_state():
		emr = cClinicalRecord(aPKey=1)
		state = emr.allergy_state
		print("allergy state is:", state)

		print("setting state to 0")
		emr.allergy_state = 0

		print("setting state to None")
		emr.allergy_state = None

		print("setting state to 'abc'")
		emr.allergy_state = 'abc'

	#-----------------------------------------
	def test_get_test_names():
		emr = cClinicalRecord(aPKey = 6)
		rows = emr.get_test_types_for_results(unique_meta_types = True)
		print("test result names:", len(rows))
#		for row in rows:
#			print row

	#-----------------------------------------
	def test_get_dates_for_results():
		emr = cClinicalRecord(aPKey=12)
		rows = emr.get_dates_for_results()
		print("test result dates:")
		for row in rows:
			print(row)

	#-----------------------------------------
	def test_get_measurements():
		emr = cClinicalRecord(aPKey=12)
		rows, idx = emr.get_measurements_by_date()
		print("test results:")
		for row in rows:
			print(row)

	#-----------------------------------------
	def test_get_test_results_by_date():
		emr = cClinicalRecord(aPKey=12)
		tests = emr.get_test_results_by_date()
		print("test results:")
		for test in tests:
			print(test)

	#-----------------------------------------
	def test_get_statistics():
		emr = cClinicalRecord(aPKey=12)
		for key, item in emr.get_statistics().items():
			print(key, ":", item)

	#-----------------------------------------
	def test_get_problems():
		emr = cClinicalRecord(aPKey=12)

		probs = emr.get_problems()
		print("normal probs (%s):" % len(probs))
		for p in probs:
			print('%s (%s)' % (p['problem'], p['type']))

		probs = emr.get_problems(include_closed_episodes=True)
		print("probs + closed episodes (%s):" % len(probs))
		for p in probs:
			print('%s (%s)' % (p['problem'], p['type']))

		probs = emr.get_problems(include_irrelevant_issues=True)
		print("probs + issues (%s):" % len(probs))
		for p in probs:
			print('%s (%s)' % (p['problem'], p['type']))

		probs = emr.get_problems(include_closed_episodes=True, include_irrelevant_issues=True)
		print("probs + issues + epis (%s):" % len(probs))
		for p in probs:
			print('%s (%s)' % (p['problem'], p['type']))

	#-----------------------------------------
	def test_add_test_result():
		emr = cClinicalRecord(aPKey=12)
		tr = emr.add_test_result (
			episode = 1,
			intended_reviewer = 1,
			type = 1,
			val_num = 75,
			val_alpha = 'somewhat obese',
			unit = 'kg'
		)
		print(tr)

	#-----------------------------------------
	def test_get_most_recent_episode():
		emr = cClinicalRecord(aPKey=12)
		print(emr.get_most_recent_episode(issue = 2))

	#-----------------------------------------
	def test_get_almost_recent_encounter():
		emr = cClinicalRecord(aPKey=12)
		print(emr.get_last_encounter(issue_id=2))
		print(emr.get_last_but_one_encounter(issue_id=2))

	#-----------------------------------------
	def test_get_encounters():
		emr = cClinicalRecord(aPKey = 5)
		print(emr.get_first_encounter(episode_id = 1638))
		print(emr.get_last_encounter(episode_id = 1638))

	#-----------------------------------------
	def test_get_issues():
		emr = cClinicalRecord(aPKey = 12)
		for issue in emr.health_issues:
			print(issue['description'])

	#-----------------------------------------
	def test_get_dx():
		emr = cClinicalRecord(aPKey = 12)
		for dx in emr.candidate_diagnoses:
			print(dx)

	#-----------------------------------------
	def test_get_meds():
		emr = cClinicalRecord(aPKey=12)
		for med in emr.get_current_medications():
			print(med)

	#-----------------------------------------
	def test_get_abuses():
		emr = cClinicalRecord(aPKey=12)
		for med in emr.abused_substances:
			print(med.format(single_line = True))

	#-----------------------------------------
	def test_is_allergic_to():
		emr = cClinicalRecord(aPKey = 12)
		print(emr.is_allergic_to(atcs = tuple(sys.argv[2:]), inns = tuple(sys.argv[2:]), product_name = sys.argv[2]))

	#-----------------------------------------
	def test_get_as_journal():
		emr = cClinicalRecord(aPKey = 12)
		for journal_line in emr.get_as_journal():
			#print(list(journal_line))
			print('%(date)s  %(modified_by)s  %(soap_cat)s  %(narrative)s' % journal_line)
			print("")

	#-----------------------------------------
	def test_get_most_recent():
		emr = cClinicalRecord(aPKey=12)
		print(emr.get_most_recent_results_for_test_type())

	#-----------------------------------------
	def test_episodes():
		emr = cClinicalRecord(aPKey=12)
		print("episodes:", emr.episodes)
		print("unlinked:", emr.unlinked_episodes)

	#-----------------------------------------
	def test_format_as_journal():
		emr = cClinicalRecord(aPKey=12)
		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = 12)
		print(emr.format_as_journal(left_margin = 1, patient = pat))

	#-----------------------------------------
	def test_smoking():
		emr = cClinicalRecord(aPKey=12)
		#print emr.is_or_was_smoker
		smoking, details = emr.smoking_status
		print('status:', smoking)
		print('details:')
		print(details)
		emr.smoking_status = (True, {'comment': '2', 'last_confirmed': gmDateTime.pydt_now_here()})
		print(emr.smoking_status)
		print(emr.alcohol_status)
		print(emr.drugs_status)

	#-----------------------------------------

	#test_allergy_state()
	#test_is_allergic_to()

	#test_get_test_names()
	#test_get_dates_for_results()
	#test_get_measurements()
	#test_get_test_results_by_date()
	#test_get_statistics()
	#test_get_problems()
	#test_add_test_result()
	#test_get_most_recent_episode()
	#test_get_almost_recent_encounter()
	#test_get_meds()
	#test_get_as_journal()
	#test_get_most_recent()
	#test_episodes()
	#test_format_as_journal()
	#test_smoking()
	#test_get_abuses()
	#test_get_encounters()
	#test_get_issues()
	#test_get_dx()

	emr = cClinicalRecord(aPKey = 12)

#	# Vacc regimes
#	vacc_regimes = emr.get_scheduled_vaccination_regimes(indications = ['tetanus'])
#	print '\nVaccination regimes: '
#	for a_regime in vacc_regimes:
#		pass
#		#print a_regime
#	vacc_regime = emr.get_scheduled_vaccination_regimes(ID=10)
#	#print vacc_regime

#	# vaccination regimes and vaccinations for regimes
#	scheduled_vaccs = emr.get_scheduled_vaccinations(indications = ['tetanus'])
#	print 'Vaccinations for the regime:'
#	for a_scheduled_vacc in scheduled_vaccs:
#		pass
#		#print '   %s' %(a_scheduled_vacc)

#	# vaccination next shot and booster
	v1 = emr.vaccinations
	print(v1)
	v2 = gmVaccination.get_vaccinations(pk_identity = 12, return_pks = True)
	print(v2)
	for v in v1:
		if v['pk_vaccination'] not in v2:
			print('ERROR')

#	for a_vacc in vaccinations:
#		print '\nVaccination %s , date: %s, booster: %s, seq no: %s' %(a_vacc['batch_no'], a_vacc['date'].strftime('%Y-%m-%d'), a_vacc['is_booster'], a_vacc['seq_no'])

#	# first and last encounters
#	first_encounter = emr.get_first_encounter(issue_id = 1)
#	print '\nFirst encounter: ' + str(first_encounter)
#	last_encounter = emr.get_last_encounter(episode_id = 1)
#	print '\nLast encounter: ' + str(last_encounter)
#	print ''

	#dump = record.get_missing_vaccinations()
	#f = io.open('vaccs.lst', 'wb')
	#if dump is not None:
	#	print "=== due ==="
	#	f.write(u"=== due ===\n")
	#	for row in dump['due']:
	#		print row
	#		f.write(repr(row))
	#		f.write(u'\n')
	#	print "=== overdue ==="
	#	f.write(u"=== overdue ===\n")
	#	for row in dump['overdue']:
	#		print row
	#		f.write(repr(row))
	#		f.write(u'\n')
	#f.close()

