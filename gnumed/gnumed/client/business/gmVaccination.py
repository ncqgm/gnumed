"""GnuMed vaccination related business objects.

"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmVaccination.py,v $
# $Id: gmVaccination.py,v 1.13 2004-10-18 11:35:42 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import types

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmPG
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cVaccination(gmClinItem.cClinItem):
	"""Represents one vaccination event.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_vacc4ind
		where pk_vaccination=%s
		order by date desc"""

	_cmds_store_payload = [
		"""select 1 from vaccination where id=%(pk_vaccination)s for update""",
		"""update vaccination set
				clin_when=%(date)s,
				narrative=%(narrative)s,
				fk_provider=%(pk_provider)s,
				fk_vaccine=(select id from vaccine where trade_name=%(vaccine)s),
				site=%(site)s,
				batch_no=%(batch_no)s
			where id=%(pk_vaccination)s"""
		]

	_updatable_fields = [
		'date',
		'narrative',
		'pk_provider',
		'vaccine',
		'site',
		'batch_no'
	]
	#--------------------------------------------------------
	def set_booster_status(self, is_booster=None):
		if is_booster is None:
			return False
		self._idx['is_booster'] = len(self._payload)
		self._payload.append(is_booster)
		if is_booster:
			self.set_seq_no(seq_no = -1)
		return True
	#--------------------------------------------------------
	def set_seq_no(self, seq_no=None):
		int(seq_no)
		self._idx['seq_no'] = len(self._payload)
		self._payload.append(seq_no)
		if seq_no > 0:
			self.set_booster_status(is_booster=False)
		return True
	#--------------------------------------------------------
#	def get_next_shot_due(self):
		"""
		Retrieves next shot due date
		"""
		# FIXME: this will break due to not being initialized
#		return self.__next_shot_due
	#--------------------------------------------------------
#	def set_next_shot_due(self, next_shot_due):
#		"""
#		Sets next shot due date
#		
#		* next_shot_due : Schedulled date for next vaccination shot
#		"""
#		self.__next_shot_due = next_shot_due
#============================================================
class cMissingVaccination(gmClinItem.cClinItem):
	"""Represents one missing vaccination.

	- can be due or overdue
	"""
	_cmd_fetch_payload = """
			(select *, False as overdue
			from v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				age((select dob from identity where id=%(pat_id)s)) between age_due_min and coalesce(age_due_max, '115 years'::interval)
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s
			order by time_left)

				UNION

			(select *, True as overdue
			from v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				now() - ((select dob from identity where id=%(pat_id)s)) >  coalesce(age_due_max, '115 years'::interval)
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s		
			order by amount_overdue)"""

	_cmds_store_payload = []

	_updatable_fields = []
	#--------------------------------------------------------
	def is_overdue(self):
		return self['overdue']
	#--------------------------------------------------------
	def create_vaccination(self):
		# FIXME: create vaccination from myself,
		# either pass in episode/encounter/vaccine id or use default for
		# episode/encounter or use curr_pat.* if pk_patient=curr_pat,
		# should we auto-destroy after create_vaccination() ?
		return (False, 'not implemented')
#============================================================
class cMissingBooster(gmClinItem.cClinItem):
	"""Represents one due booster.
	"""
	_cmd_fetch_payload = """
		select *, now() - amount_overdue as latest_due
		from v_pat_missing_boosters vpmb
		where
			pk_patient=%(pat_id)s
				and
			indication=%(indication)s
		order by amount_overdue"""
	_cmds_store_payload = []

	_updatable_fields = []
#============================================================
class cScheduledVaccination(gmClinItem.cClinItem):
	"""Represents one vaccination scheduled following a regime.
	"""
	_cmd_fetch_payload = """
			select *
			from v_vaccs_scheduled4pat
			where pk_vacc_def=%s"""

	_cmds_store_payload = []

	_updatable_fields = []

#============================================================
class cVaccinationRegime(gmClinItem.cClinItem):
	"""Represents one vaccination regime.
	"""
	_cmd_fetch_payload = """
		select * from v_vacc_regimes
		where pk_regime=%s"""

	_cmds_store_payload = [
		"""select 1 from vacc_regime where id=%(pk_regime)s for update""",
		"""update vacc_regime set
				name=%(regime)s,
				fk_recommended_by=%(pk_recommended_by)s,
				fk_indication=(select id from vacc_indication where description=%(indication)s),
				comment=%(comment)s
			where id=%(pk_regime)s"""
		]

	_updatable_fields = [
		'regime',
		'pk_recommended_by',
		'indication',
		'comment'
	]
#============================================================
# convenience functions
#------------------------------------------------------------
def create_vaccination(patient_id=None, episode_id=None, encounter_id=None, staff_id = None, vaccine=None):
	# sanity check
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the patient ?
	cmd = """select id_patient from v_pat_episodes where pk_episode=%s 
                 union 
             select pk_patient from v_pat_encounters where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (None, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (None, _('consistency error, check log'))
	# insert new vaccination
	queries = []
	if type(vaccine) == types.IntType:
		cmd = """insert into vaccination (fk_encounter, fk_episode, fk_patient, fk_provider, fk_vaccine)
				 values (%s, %s, %s, %s, %s)"""
	else:
		cmd = """insert into vaccination (fk_encounter, fk_episode, fk_patient, fk_provider, fk_vaccine)
				 values (%s, %s, %s, %s, (select id from vaccine where trade_name=%s))"""
		vaccine = str(vaccine)
	queries.append((cmd, [encounter_id, episode_id, patient_id, staff_id, vaccine]))
	# get PK of inserted row
	cmd = "select currval('vaccination_id_seq')"
	queries.append((cmd, []))

	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (None, msg)

	try:
		vacc = cVaccination(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate vaccination' % (result[0][0]), sys.exc_info, verbose=0)
		return (None, _('internal error, check log'))

	return (True, vacc)
#--------------------------------------------------------
def get_vacc_regimes():
	# FIXME: use cVaccinationRegime
	cmd = 'select name from vacc_regime'
	rows = gmPG.run_ro_query('historica', cmd)
	if rows is None:
		return None
	if len(rows) == 0:
		return []
	data = []
	for row in rows:
		data.extend(rows)
	return data
#--------------------------------------------------------
def get_indications_from_vaccinations(vaccinations=None):
	"""Retrieves vaccination bundle indications list.

		* vaccinations = list of any type of vaccination
			- indicated
			- due vacc
			- overdue vaccs
			- due boosters
			- arbitrary
	"""
	# FIXME: can we not achieve this by:
	# [lambda [vacc['indication'], ['l10n_indication']] for vacc in vaccination_list]
	# I think we could, but we would be lacking error handling
	if vaccinations is None:
		_log.Log(gmLog.lErr, 'list of vaccinations must be supplied')
		return (False, [['ERROR: list of vaccinations not supplied', _('ERROR: list of vaccinations not supplied')]])
	if len(vaccinations) == 0:
		return (True, [['empty list of vaccinations', _('empty list of vaccinations')]])
	inds = []
	for vacc in vaccinations:
		try:
			inds.append([vacc['indication'], vacc['l10n_indication']])
		except KeyError:
			try:
				inds.append([vacc['indication'], vacc['indication']])
			except KeyError:
				inds.append(['vacc -> ind error: %s' % str(vacc), _('vacc -> ind error: %s') % str(vacc)])
	return (True, inds)
#--------------------------------------------------------
def put_patient_on_schedule(patient_id=None, regime=None):
	"""
		Schedules a vaccination regime for a patient

		* patient_id = Patient's PK
		* regime_id = regime object or Vaccination regime's PK
	"""
	# FIXME: add method schedule_vaccination_regime() to gmPatient.cPerson
	if isinstance(regime, cVaccinationRegime):
		reg_id = regime['pk_regime']
	else:
		reg_id = regime

	# insert new patient - vaccination regime relation
	queries = []
	cmd = """insert into lnk_pat2vacc_reg (fk_patient, fk_regime)
			 values (%s, %s)"""
	queries.append((cmd, [patient_id, reg_id]))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	return (True, msg)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	#--------------------------------------------------------
	def test_vacc():
		vacc = cVaccination(aPK_obj=1)
		print vacc
		fields = vacc.get_fields()
		for field in fields:
			print field, ':', vacc[field]
		print "updatable:", vacc.get_updatable_fields()
	#--------------------------------------------------------
	def test_due_vacc():
		# Test for a due vaccination
		pk_args = {
			'pat_id': 12,
			'indication': 'meningococcus C',
			'seq_no': 1
		}
		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
		fields = missing_vacc.get_fields()
		print "\nDue vaccination:"
		print missing_vacc
		for field in fields:
			print field, ':', missing_vacc[field]
		# Test for an overdue vaccination
		pk_args = {
			'pat_id': 12,
			'indication': 'haemophilus influenzae b',
			'seq_no': 2
		}
		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
		fields = missing_vacc.get_fields()
		print "\nOverdue vaccination (?):"
		print missing_vacc
		for field in fields:
			print field, ':', missing_vacc[field]
	#--------------------------------------------------------
	def test_due_booster():
		pk_args = {
			'pat_id': 12,
			'indication': 'tetanus'
		}
		missing_booster = cMissingBooster(aPK_obj=pk_args)
		fields = missing_booster.get_fields()
		print "\nDue booster:"
		print missing_booster
		for field in fields:
			print field, ':', missing_booster[field]
	#--------------------------------------------------------
	def test_scheduled_vacc():
		scheduled_vacc = cScheduledVaccination(aPK_obj=20)
		print "\nScheduled vaccination:"
		print scheduled_vacc
		fields = scheduled_vacc.get_fields()
		for field in fields:
			print field, ':', scheduled_vacc[field]
		print "updatable:", scheduled_vacc.get_updatable_fields()
	#--------------------------------------------------------
	def test_vaccination_regime():
		vacc_regime = cVaccinationRegime(aPK_obj=7)
		print "\nVaccination regime:"		
		print vacc_regime
		fields = vacc_regime.get_fields()
		for field in fields:
			print field, ':', vacc_regime[field]
		print "updatable:", vacc_regime.get_updatable_fields()
	#--------------------------------------------------------
	def test_put_patient_on_schedule():
		result, msg = put_patient_on_schedule(patient_id=12, regime_id=1)
		print '\nPutting patient id 12 on schedule id 1... %s (%s)' % (result, msg)
	#--------------------------------------------------------

	gmPG.set_default_client_encoding('latin1')
	test_vaccination_regime()
	#test_put_patient_on_schedule()
	test_scheduled_vacc()
	test_vacc()
	test_due_vacc()
#	test_due_booster()
#============================================================
# $Log: gmVaccination.py,v $
# Revision 1.13  2004-10-18 11:35:42  ncq
# - cleanup
#
# Revision 1.12  2004/10/12 11:16:22  ncq
# - robustify cVaccination.set_seq_no/set_booster_status
# - Carlos added cVaccinationRegime/put_patient_on_schedule
# - some test code
#
# Revision 1.11  2004/09/28 12:28:12  ncq
# - cVaccination: add set_booster_status(), set_seq_no()
# - add cScheduledVaccination (by Carlos)
# - improve testing
#
# Revision 1.10  2004/08/20 13:19:52  ncq
# - add license
#
# Revision 1.9  2004/06/28 12:18:52  ncq
# - more id_* -> fk_*
#
# Revision 1.8  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.7  2004/06/13 08:03:07  ncq
# - cleanup, better separate vaccination code from general EMR code
#
# Revision 1.6  2004/06/08 00:48:05  ncq
# - cleanup
#
# Revision 1.5  2004/05/14 13:17:27  ncq
# - less useless verbosity
# - cleanup
#
# Revision 1.4  2004/05/12 14:30:30  ncq
# - cMissingVaccination()
# - cMissingBooster()
#
# Revision 1.3  2004/04/24 12:59:17  ncq
# - all shiny and new, vastly improved vaccinations
#   handling via clinical item objects
# - mainly thanks to Carlos Moro
#
# Revision 1.2  2004/04/11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 10:16:53  ncq
# - first version
#
