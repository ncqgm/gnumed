"""GNUmed vaccination related business objects.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmVaccination.py,v $
# $Id: gmVaccination.py,v 1.32 2006-10-25 07:17:40 ncq Exp $
__version__ = "$Revision: 1.32 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import types, copy

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmBusinessDBObject

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cVaccination(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one vaccination event.
	"""
	_cmd_fetch_payload = """
		select *, NULL as is_booster, -1 as seq_no, xmin_vaccination from clin.v_pat_vaccinations4indication
		where pk_vaccination=%s
		order by date desc"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.vaccination where id=%(pk_vaccination)s and xmin=%(xmin_vaccination)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.vaccination set
				clin_when=%(date)s,
				narrative=%(narrative)s,
				fk_provider=%(pk_provider)s,
				fk_vaccine=(select pk from clin.vaccine where trade_name=%(vaccine)s),
				site=%(site)s,
				batch_no=%(batch_no)s
			where id=%(pk_vaccination)s""",
		"""select xmin_vaccination from clin.v_pat_vaccinations4indication where pk_vaccination=%(pk_vaccination)s"""
		]
	_updatable_fields = [
		'date',
		'narrative',
		'pk_provider',
		'vaccine',
		'site',
		'batch_no',
		# the following two are updatable via __setitem__
		# API but not persisted via _cmds_store_payload
		'is_booster',
		'seq_no'
	]
	#--------------------------------------------------------
	def _init_from_row_data(self, row=None):
		"""Make sure we have is_booster/seq_no when loading from row data."""
		gmClinItem.cClinItem._init_from_row_data(self, row=row)
		try:
			idx = self._idx['is_booster']
		except KeyError:
			idx = len(self._payload)
			self._payload.append(False)
			# make local copy so we can safely modify it, but from
			# self._idx which is row['idx'] with possible modifications
			self._idx = copy.copy(self._idx)
			self._idx['is_booster'] = idx
		try:
			idx = self._idx['seq_no']
		except KeyError:
			idx = len(self._payload)
			self._payload.append(False)
			self._idx = copy.copy(self._idx)
			self._idx['seq_no'] = -1
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		gmClinItem.cClinItem.__setitem__(self, attribute, value)
		if attribute in ['is_booster', 'seq_no']:
			self._is_modified = False
#	#--------------------------------------------------------
#	def get_next_shot_due(self):
#		"""
#		Retrieves next shot due date
#		"""
#		# FIXME: this will break due to not being initialized
#		return self.__next_shot_due
#	#--------------------------------------------------------
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
			from clin.v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				(select dob from dem.identity where pk=%(pat_id)s) between (now() - age_due_min) and (now() - coalesce(age_due_max, '115 years'::interval))
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s
			order by time_left)

				UNION

			(select *, True as overdue
			from clin.v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				now() - ((select dob from dem.identity where pk=%(pat_id)s)) > coalesce(age_due_max, '115 years'::interval)
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s		
			order by amount_overdue)"""
	_cmds_lock_rows_for_update = []
	_cmds_store_payload = ["""select 1"""]
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
		from clin.v_pat_missing_boosters vpmb
		where
			pk_patient=%(pat_id)s
				and
			indication=%(indication)s
		order by amount_overdue"""
	_cmds_lock_rows_for_update = []
	_cmds_store_payload = ["""select 1"""]
	_updatable_fields = []
#============================================================
class cScheduledVaccination(gmClinItem.cClinItem):
	"""Represents one vaccination scheduled following a course.
	"""
	_cmd_fetch_payload = """select * from clin.v_vaccs_scheduled4pat where pk_vacc_def=%s"""
	_cmds_lock_rows_for_update = []
	_cmds_store_payload = ["""select 1"""]
	_updatable_fields = []
#============================================================
class cVaccinationCourse(gmClinItem.cClinItem):
	"""Represents one vaccination course.
	"""
	_cmd_fetch_payload = """
		select *, xmin_vaccination_course from clin.v_vaccination_courses
		where pk_course=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.vaccination_course where id=%(pk_course)s and xmin=%(xmin_vaccination_course)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.vaccination_course set
				name=%(course)s,
				fk_recommended_by=%(pk_recommended_by)s,
				fk_indication=(select id from clin.vacc_indication where description=%(indication)s),
				comment=%(comment)s
			where id=%(pk_course)s""",
		"""select xmin_vaccination_course from clin.v_vaccination_courses where pk_course=%(pk_course)s"""
	]
	_updatable_fields = [
		'course',
		'pk_recommended_by',
		'indication',
		'comment'
	]
#============================================================
class VaccByRecommender:
	_recommended_courses = None 
#============================================================
# convenience functions
#------------------------------------------------------------
def create_vaccination(patient_id=None, episode_id=None, encounter_id=None, staff_id = None, vaccine=None):
	# sanity check
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the patient ?
	cmd = """
select pk_patient
from clin.v_pat_episodes
where pk_episode=%s 
	union 
select pk_patient
from clin.v_pat_encounters
where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (False, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (False, _('consistency error, check log'))
	# insert new vaccination
	queries = []
	if type(vaccine) == types.IntType:
		cmd = """insert into clin.vaccination (fk_encounter, fk_episode, fk_patient, fk_provider, fk_vaccine)
				 values (%s, %s, %s, %s, %s)"""
	else:
		cmd = """insert into clin.vaccination (fk_encounter, fk_episode, fk_patient, fk_provider, fk_vaccine)
				 values (%s, %s, %s, %s, (select pk from clin.vaccine where trade_name=%s))"""
		vaccine = str(vaccine)
	queries.append((cmd, [encounter_id, episode_id, patient_id, staff_id, vaccine]))
	# get PK of inserted row
	cmd = "select currval('clin.vaccination_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if (result is None) or (len(result) == 0):
		return (False, msg)
	try:
		vacc = cVaccination(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate vaccination' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))

	return (True, vacc)
#--------------------------------------------------------
def get_vacc_courses():
	# FIXME: use cVaccinationCourse
	cmd = 'select name from clin.vaccination_course'
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
def get_vacc_regimes_by_recommender_ordered(pk_patient=None, clear_cache=False):
	# check DbC, if it fails exception is due
	int(pk_patient)

	cmd = """
select fk_regime
from clin.lnk_pat2vacc_reg l
where l.fk_patient = %s""" % pk_patient

	rows = gmPG.run_ro_query('historica', cmd)
	active = []
	if rows and len(rows):
		active = [ r[0] for r in rows]

	# FIXME: this is patient dependant so how would a cache
	# FIXME: work that's not taking into account pk_patient ?
#	recommended_regimes = VaccByRecommender._recommended_regimes
#	if not clear_cache and recommended_regimes:
#		return recommended_regimes, active

	r = ( {}, [] )

	# FIXME: use views ?	
	cmd = """
select 
	r.pk_regime , 
	r.pk_recommended_by , 
	r.indication, 
	r.regime , 
	extract (epoch from d.min_age_due) /60/60/24,
	extract (epoch from d.max_age_due)  /60/60/24, 		
	extract (epoch from d.min_interval ) /60/60/24, 
	d.seq_no
from 
	clin.v_vaccination_courses r, clin.vacc_def d 
where 
	d.fk_regime = r.pk_regime 
order by 
	r.pk_recommended_by, d.min_age_due""" 
	#print cmd
	#import pdb
	#pdb.set_trace()
	#
	rows = gmPG.run_ro_query('historica', cmd)
	if rows is None:
		VaccByRecommender._recommended_regimes = r
		return r, active

	row_fields = ['pk_regime', 'pk_recommender', 'indication' , 'regime', 'min_age_due', 'max_age_due', 'min_interval', 'seq_no' ]

	for row in rows:
		m = {}
		for k, i in zip(row_fields, range(len(row))):
			m[k] = row[i]
		pk_recommender = m['pk_recommender']

		if not pk_recommender in r[0].keys(): 
			r[0][pk_recommender] = []
			r[1].append(pk_recommender)
		r[0][pk_recommender].append(m)

	for k, v in r[0].items():
		print k
		for x in v:
			print '\t', x

	VaccByRecommender._recommended_regimes = r
	return r, active
#--------------------------------------------------------
def get_missing_vaccinations_ordered_min_due(pk_patient):
	# DbC
	int(pk_patient)

	cmd = """ 
	select 
		indication, regime, 
		pk_regime, 
		pk_recommended_by, 
		seq_no , 
		extract(epoch from age_due_min) /60/60/24 as age_due_min, 
		extract(epoch from age_due_max) /60/60/24 as age_due_max,
		extract(epoch from min_interval)/60/60/24 as min_interval
	from
		clin.v_pat_missing_vaccs 
	where pk_patient = %s
	order by age_due_min, pk_recommended_by, indication
	""" % pk_patient

	rows = gmPG.run_ro_query('historica', cmd)

	return rows
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
def put_patient_on_schedule(patient_id=None, course=None):
	"""
		Schedules a vaccination course for a patient

		* patient_id = Patient's PK
		* course = course object or Vaccination course's PK
	"""
	# FIXME: add method schedule_vaccination_course() to gmPerson.cPerson
	if isinstance(course, cVaccinationCourse):
		course_id = course['pk_course']
	else:
		course_id = course

	# insert new patient - vaccination course relation
	queries = []
	cmd = """insert into clin.lnk_pat2vacc_reg (fk_patient, fk_course)
			 values (%s, %s)"""
	queries.append((cmd, [patient_id, course_id]))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	return (True, msg)
#--------------------------------------------------------
def remove_patient_from_schedule(patient_id=None, course=None):
	"""unSchedules a vaccination course for a patient

		* patient_id = Patient's PK
		* course = course object or Vaccination course's PK
	"""
	# FIXME: add method schedule_vaccination_course() to gmPerson.cPerson
	if isinstance(course, cVaccinationCourse):
		course_id = course['pk_course']
	else:
		course_id = course

	# delete  patient - vaccination course relation
	queries = []
	cmd = """delete from clin.lnk_pat2vacc_reg where fk_patient = %s and fk_course = %s"""
			 
	queries.append((cmd, [patient_id, course_id]))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	return (True, msg)	
#--------------------------------------------------------
def get_matching_vaccines_for_indications( all_ind):

	quoted_inds = [ "'"+x + "%'" for x in all_ind]

#	cmd_inds_per_vaccine = """
#		select count(v.trade_name) , v.trade_name 
#		from 
#			clin.vaccine v, clin.lnk_vaccine2inds l, clin.vacc_indication i
#		where 
#			v.pk = l.fk_vaccine and l.fk_indication = i.id 
#		group 
#			by trade_name
#		"""

	cmd_inds_per_vaccine = """
select
	count(trade_name),
	trade_name
from clin.v_inds4vaccine
group by trade_name"""

	cmd_presence_in_vaccine = """
			select count(v.trade_name) , v.trade_name 
	
		from 
			clin.vaccine v, clin.lnk_vaccine2inds l, clin.vacc_indication i
		where 
			v.pk = l.fk_vaccine and l.fk_indication = i.id 	
		and  
			i.description like any ( array [ %s ] ) 		
		group 
			
			by trade_name

		"""		% ', '.join( quoted_inds )

	inds_per_vaccine = gmPG.run_ro_query( 'historica', cmd_inds_per_vaccine)
	
	presence_in_vaccine = gmPG.run_ro_query( 'historica', cmd_presence_in_vaccine)

	map_vacc_count_inds = dict ( [ (x[1], x[0]) for x in inds_per_vaccine ] )

	matched_vaccines = []
	for (presence, vaccine) in presence_in_vaccine:
		if presence == len ( all_ind) : 
			# matched the number of indications selected with a vaccine
			# is this also ALL the vaccine's indications ?
			if map_vacc_count_inds[vaccine] == presence:
				matched_vaccines.append(vaccine)
	return matched_vaccines
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
	def test_vaccination_course():
		vaccination_course = cVaccinationCourse(aPK_obj=7)
		print "\nVaccination course:"		
		print vaccination_course
		fields = vaccination_course.get_fields()
		for field in fields:
			print field, ':', vaccination_course[field]
		print "updatable:", vaccination_course.get_updatable_fields()
	#--------------------------------------------------------
	def test_put_patient_on_schedule():
		result, msg = put_patient_on_schedule(patient_id=12, course_id=1)
		print '\nPutting patient id 12 on schedule id 1... %s (%s)' % (result, msg)
	#--------------------------------------------------------

	gmPG.set_default_client_encoding('latin1')
	test_vaccination_course()
	#test_put_patient_on_schedule()
	test_scheduled_vacc()
	test_vacc()
	test_due_vacc()
#	test_due_booster()
#============================================================
# $Log: gmVaccination.py,v $
# Revision 1.32  2006-10-25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.31  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.30  2006/05/06 18:53:56  ncq
# - select age(...) <> ...; -> select ... <> now() - ...; as per Syan
#
# Revision 1.29  2006/05/04 17:55:08  ncq
# - lots of DDL naming adjustments
#   - many things spelled out at Richard's request
#   - regime -> course
#
# Revision 1.28  2006/01/10 23:22:53  sjtan
#
# id has become pk
#
# Revision 1.27  2006/01/09 10:43:07  ncq
# - more dem schema qualifications
#
# Revision 1.26  2006/01/07 11:23:24  ncq
# - must use """ for multi-line string
#
# Revision 1.25  2006/01/06 08:32:12  ncq
# - some cleanup, added view to backend, may need some fixing
#
# Revision 1.24  2006/01/05 22:39:57  sjtan
#
# vaccination use case; some sql stuff may need to be added ( e.g. permissions ); sorry in a hurry
#
# Revision 1.23  2005/12/29 21:54:35  ncq
# - adjust to schema changes
#
# Revision 1.22  2005/11/27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.21  2005/03/20 12:28:50  cfmoro
# On create_vaccination, id_patient -> pk_patient
#
# Revision 1.20  2005/02/12 13:56:49  ncq
# - identity.id -> identity.pk
#
# Revision 1.19  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.18  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.17  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.16  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.15  2004/10/27 12:11:59  ncq
# - add is_booster/seq_no as pseudo columns to _cmd_fetch_payload so
#   __init_from_pk() automagically creates all the right things
# - enhance _init_from_row_data() to construct those fields if need be
# - make __setitem__ aware of is_booster/seq_no being pseudo columns
#   that do not affect _is_modified
#
# Revision 1.14  2004/10/20 21:42:28  ncq
# - fix faulty appending on repeated use of set_booster_status/set_seq_no()
#
# Revision 1.13  2004/10/18 11:35:42  ncq
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
