"""GNUmed vaccination related business objects.
"""
#============================================================
__version__ = "$Revision: 1.38 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import sys, copy, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
#	from Gnumed.pycommon import 		#, gmDateTime, gmLog2
#	gmDateTime.init()
#	gmI18N.activate_locale()
from Gnumed.pycommon import gmBusinessDBObject, gmPG2, gmI18N, gmTools
from Gnumed.business import gmMedication


_log = logging.getLogger('gm.vaccination')
_log.info(__version__)

#============================================================
def get_indications(order_by=None):
	cmd = u'SELECT * from clin.vacc_indication'

	if order_by is not None:
		cmd = u'%s ORDER BY %s' % (cmd, order_by)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)

	return rows
#============================================================
_sql_fetch_vaccine = u"""SELECT *, xmin_vaccine FROM clin.v_vaccines WHERE %s"""

class cVaccine(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one vaccine."""

	_cmd_fetch_payload = _sql_fetch_vaccine % u"pk_vaccine = %s"

	_cmds_store_payload = [
		u"""UPDATE clin.vaccine SET
				--id_route = %(pk_route)s,
				--is_live = %(is_live)s,
				min_age = %(min_age)s,
				max_age = %(max_age)s,
				comment = gm.nullify_empty_string(%(comment)s),
				fk_brand = %(pk_brand)s
			WHERE
				pk = %(pk_vaccine)s
					AND
				xmin = %(xmin_vaccine)s
			RETURNING
				xmin as xmin_vaccine
		"""
	]

	_updatable_fields = [
		#u'pk_route',
		#u'is_live',
		u'min_age',
		u'max_age',
		u'comment',
		u'pk_brand'
	]
	#--------------------------------------------------------
	def set_indications(self, indications=None, pk_indications=None):
		queries = [{
			'cmd': u'DELETE FROM clin.lnk_vaccine2inds WHERE fk_vaccine = %(pk_vacc)s',
			'args': {'pk_vacc': self._payload[self._idx['pk_vaccine']]}
		}]

		if pk_indications is None:
			if set(self._payload[self._idx['indications']]) == set(indications):
				return

			for ind in indications:
				queries.append ({
					'cmd': u"""
						INSERT INTO clin.lnk_vaccine2inds (
							fk_vaccine,
							fk_indication
						) VALUES (
							%(pk_vacc)s,
							(SELECT id FROM clin.vacc_indication WHERE description = %(ind)s)
						)""",
					'args': {'pk_vacc': self._payload[self._idx['pk_vaccine']], 'ind': ind}
				})
		else:
			if set(self._payload[self._idx['pk_indications']]) == set(pk_indications):
				return

			for pk_ind in pk_indications:
				queries.append ({
					'cmd': u"""
						INSERT INTO clin.lnk_vaccine2inds (
							fk_vaccine,
							fk_indication
						) VALUES (
							%(pk_vacc)s,
							%(pk_ind)s
						)""",
					'args': {'pk_vacc': self._payload[self._idx['pk_vaccine']], 'pk_ind': pk_ind}
				})

		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_brand(self):
		return gmMedication.cBrandedDrug(aPK_obj = self._payload[self._idx['pk_brand']])

	brand = property(_get_brand, lambda x:x)
	#--------------------------------------------------------
	def _get_is_in_use(self):
		cmd = u'SELECT EXISTS(SELECT 1 FROM clin.vaccination WHERE fk_vaccine = %(pk)s)'
		args = {'pk': self._payload[self._idx['pk_vaccine']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use = property(_get_is_in_use, lambda x:x)
#------------------------------------------------------------
def create_vaccine(pk_brand=None, brand_name=None, indications=None):

	if pk_brand is None:
		prep = _('vaccine')
		_log.debug('creating branded drug [%s %s]', brand_name, prep)
		drug = gmMedication.create_branded_drug (
			brand_name = brand_name,
			preparation = prep,
			return_existing = True
		)
		drug['atc'] = u'J07'
		drug.save()
		pk_brand = drug['pk_brand']

	cmd = u'INSERT INTO clin.vaccine (fk_brand) values (%(pk_brand)s) RETURNING pk'
	queries = [{'cmd': cmd, 'args': {'pk_brand': pk_brand}}]

	for indication in indications:
		cmd = u"""
			INSERT INTO clin.lnk_vaccine2inds (
				fk_vaccine,
				fk_indication
			) VALUES (
				currval(pg_get_serial_sequence('clin.vaccine', 'pk')),
				(SELECT id
				 FROM clin.vacc_indication
				 WHERE
					lower(description) = lower(%(ind)s)
				 LIMIT 1
				)
			)
			RETURNING fk_vaccine
		"""
		queries.append({'cmd': cmd, 'args': {'ind': indication}})

	rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = False, return_data = True)

	return cVaccine(aPK_obj = rows[0]['fk_vaccine'])
#------------------------------------------------------------
def delete_vaccine(vaccine=None):

	cmd = u'DELETE FROM clin.vaccine WHERE pk = %(pk)s'
	args = {'pk': vaccine}

	try:
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	except gmPG2.dbapi.IntegrityError:
		_log.exception('cannot delete vaccine [%s]', vaccine)
		return False

	return True
#------------------------------------------------------------
def get_vaccines(order_by=None):

	if order_by is None:
		cmd = _sql_fetch_vaccine % u'TRUE'
	else:
		cmd = _sql_fetch_vaccine % (u'TRUE\nORDER BY %s' % order_by)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)

	return [ cVaccine(row = {'data': r, 'idx': idx, 'pk_field': 'pk_vaccine'}) for r in rows ]
#------------------------------------------------------------
def map_indications2generic_vaccine(indications=None):

	args = {'inds': indications}
	cmd = _sql_fetch_vaccine % (u'is_fake_vaccine is True AND indications @> %(inds)s AND %(inds)s @> indications')

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	if len(rows) == 0:
		_log.warning('no fake, generic vaccine found for [%s]', indications)
		return None

	return cVaccine(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_vaccine'})
#------------------------------------------------------------
def regenerate_generic_vaccines():

	cmd = u'select gm.create_generic_monovalent_vaccines()'
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd}], return_data = True)

	cmd = u'select gm.create_generic_combi_vaccines()'
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd}], return_data = True)

	return rows[0][0]
#============================================================
# vaccination related classes
#============================================================
sql_fetch_vaccination = u"""SELECT * FROM clin.v_pat_vaccinations WHERE %s"""

class cVaccination(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = sql_fetch_vaccination % u"pk_vaccination = %s"

	_cmds_store_payload = [
		u"""UPDATE clin.vaccination SET
				soap_cat = %(soap_cat)s,
				clin_when = %(date_given)s,
				site = gm.nullify_empty_string(%(site)s),
				batch_no = gm.nullify_empty_string(%(batch_no)s),
				reaction = gm.nullify_empty_string(%(reaction)s),
				narrative = gm.nullify_empty_string(%(comment)s),
				fk_vaccine = %(pk_vaccine)s,
				fk_provider = %(pk_provider)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s
			WHERE
				pk = %(pk_vaccination)s
					AND
				xmin = %(xmin_vaccination)s
			RETURNING
				xmin as xmin_vaccination
		"""
	]

	_updatable_fields = [
		u'soap_cat',
		u'date_given',
		u'site',
		u'batch_no',
		u'reaction',
		u'comment',
		u'pk_vaccine',
		u'pk_provider',
		u'pk_encounter',
		u'pk_episode'
	]
	#--------------------------------------------------------
	def format(self, with_indications=False, with_comment=False, with_reaction=False, date_format='%Y-%m-%d'):

		lines = []

		lines.append (u' %s: %s [%s]%s' % (
			self._payload[self._idx['date_given']].strftime(date_format).decode(gmI18N.get_encoding()),
			self._payload[self._idx['vaccine']],
			self._payload[self._idx['batch_no']],
			gmTools.coalesce(self._payload[self._idx['site']], u'', u' (%s)')
		))

		if with_comment:
			if self._payload[self._idx['comment']] is not None:
				lines.append(u'   %s' % self._payload[self._idx['comment']])

		if with_reaction:
			if self._payload[self._idx['reaction']] is not None:
				lines.append(u'   %s' % self._payload[self._idx['reaction']])

		if with_indications:
			lines.append(u'   %s' % u' / '.join(self._payload[self._idx['indications']]))

		return lines
#------------------------------------------------------------
def create_vaccination(encounter=None, episode=None, vaccine=None, batch_no=None):

	cmd = u"""
		INSERT INTO clin.vaccination (
			fk_encounter,
			fk_episode,
			fk_vaccine,
			batch_no
		) VALUES (
			%(enc)s,
			%(epi)s,
			%(vacc)s,
			%(batch)s
		) RETURNING pk;
	"""
	args = {
		u'enc': encounter,
		u'epi': episode,
		u'vacc': vaccine,
		u'batch': batch_no
	}

	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False, return_data = True)

	return cVaccination(aPK_obj = rows[0][0])

#------------------------------------------------------------

def delete_vaccination(vaccination=None):
	cmd = u"""DELETE FROM clin.vaccination WHERE pk = %(pk)s"""
	args = {'pk': vaccination}

	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

#------------------------------------------------------------

def format_latest_vaccinations(output_format=u'latex', emr=None):

	_log.debug(u'formatting latest vaccinations into [%s]', output_format)

	vaccs = emr.get_latest_vaccinations()

	if output_format == u'latex':
		return __format_latest_vaccinations_latex(vaccinations = vaccs)

	msg = _('unknown vaccinations output format [%s]') % output_format
	_log.error(msg)
	return msg

#------------------------------------------------------------

def __format_latest_vaccinations_latex(vaccinations=None):

	if len(vaccinations) == 0:
		return u'\\noindent %s' % _('No vaccinations to format.')

	tex =  u'\\noindent %s {\\tiny (%s)\\par}\n' % (_('Latest vaccinations'), _('per target condition'))
	tex += u'\n'
	tex += u'\\noindent \\begin{tabular}{|l|l|l|l|l|l|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s & {\\footnotesize %s} & {\\footnotesize %s} & {\\footnotesize %s\\footnotemark} & {\\footnotesize %s\\footnotemark} \\\\ \n' % (
		_('Target'),
		_('Last given'),
		_('Vaccine'),
		_('Lot \#'),
		_('S/P'),
		gmTools.u_sum
	)
	tex += u'\\hline\n'
	tex += u'\n'
	tex += u'\\hline\n'
	tex += u'%s'
	tex += u'\n'
	tex += u'\\end{tabular}\n'
	tex += u'\n'
	tex += u'\\addtocounter{footnote}{-1} \n'
	tex += u'\\footnotetext{%s} \n' % _('S/P -- "S"ubjective: this vaccination was remembered by the patient. "P"lan: this vaccination was administered in the practice or copied from trustworthy records.')
	tex += u'\\addtocounter{footnote}{1} \n'
	tex += u'\\footnotetext{%s -- %s} \n' % (gmTools.u_sum, _('Total number of vaccinations recorded for the corresponding target condition.'))
	tex += u'\n'

	row_template = u'%s & %s & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize %s} \\\\ \n'
	lines = u''
	targets = sorted(vaccinations.keys())
	for target in targets:
		target_count, vacc = vaccinations[target]
		lines += row_template % (
			target,
			vacc['date_given'].strftime('%Y %b %d').decode(gmI18N.get_encoding()),
			vacc['vaccine'],
			gmTools.tex_escape_string(vacc['batch_no'].strip()),
			vacc['soap_cat'].upper(),
			target_count
		)
		if vacc['site'] is not None:
			lines += u' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par} \\\\ \n' % (_('Injection site'), vacc['site'].strip())
		if vacc['reaction'] is not None:
			lines += u' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par} \\\\ \n' % (_('Reaction'), vacc['reaction'].strip())
		if vacc['comment'] is not None:
			lines += u' & \\multicolumn{5}{l|}{\\scriptsize %s: %s\\par} \\\\ \n' % (_('Comment'), vacc['comment'].strip())
		lines += u'\\hline \n'

	return tex % lines

#============================================================
#============================================================
#============================================================
# old code
#============================================================
class cMissingVaccination(gmBusinessDBObject.cBusinessDBObject):
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
class cMissingBooster(gmBusinessDBObject.cBusinessDBObject):
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
class cScheduledVaccination(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one vaccination scheduled following a course.
	"""
	_cmd_fetch_payload = u"select * from clin.v_vaccs_scheduled4pat where pk_vacc_def=%s"
	_cmds_lock_rows_for_update = []
	_cmds_store_payload = ["""select 1"""]
	_updatable_fields = []
#============================================================
class cVaccinationCourse(gmBusinessDBObject.cBusinessDBObject):
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
#============================================================
# convenience functions
#------------------------------------------------------------
def create_vaccination_old(patient_id=None, episode_id=None, encounter_id=None, staff_id = None, vaccine=None):
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
		_log.error('error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (False, _('internal error, check log'))
	if len(rows) > 1:
		_log.error('episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
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
		_log.exception('cannot instantiate vaccination' % (result[0][0]), sys.exc_info, verbose=0)
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
		_log.error('list of vaccinations must be supplied')
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
	# FIXME: add method schedule_vaccination_course() to gmPerson.cPatient
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
	# FIXME: add method schedule_vaccination_course() to gmPerson.cPatient
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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG
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
	def test_get_vaccines():

		for vaccine in get_vaccines():
			print vaccine

	#--------------------------------------------------------
	#test_vaccination_course()
	#test_put_patient_on_schedule()
	#test_scheduled_vacc()
	#test_vacc()
	#test_due_vacc()
	#test_due_booster()

	test_get_vaccines()
#============================================================

