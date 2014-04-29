# -*- coding: utf-8 -*-
"""GNUmed clinical patient record.

Make sure to call set_func_ask_user() and set_encounter_ttl() early on in
your code (before cClinicalRecord.__init__() is called for the first time).
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

# standard libs
import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmLog2, gmDateTime, gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmAllergy
from Gnumed.business import gmPathLab
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinNarrative
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmMedication
from Gnumed.business import gmVaccination
from Gnumed.business import gmFamilyHistory
from Gnumed.business.gmDemographicRecord import get_occupations


_log = logging.getLogger('gm.emr')

_here = None
#============================================================
# helper functions
#------------------------------------------------------------
_func_ask_user = None

def set_func_ask_user(a_func = None):
	if not callable(a_func):
		_log.error('[%] not callable, not setting _func_ask_user', a_func)
		return False

	_log.debug('setting _func_ask_user to [%s]', a_func)

	global _func_ask_user
	_func_ask_user = a_func

#============================================================
class cClinicalRecord(object):

	def __init__(self, aPKey=None, allow_user_interaction=True):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self.pk_patient = aPKey			# == identity.pk == primary key

		# FIXME: delegate to worker thread
		# log access to patient record (HIPAA, for example)
		cmd = u'SELECT gm.log_access2emr(%(todo)s)'
		args = {'todo': u'patient [%s]' % aPKey}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		from Gnumed.business import gmPraxis
		global _here
		if _here is None:
			_here = gmPraxis.gmCurrentPraxisBranch()

		# load current or create new encounter
		if _func_ask_user is None:
			_log.error('[_func_ask_user] is None')
			print "*** GNUmed [%s]: _func_ask_user is not set ***" % self.__class__.__name__

		# FIXME: delegate to worker thread ?
		self.remove_empty_encounters()

		self.__encounter = None
		if not self.__initiate_active_encounter(allow_user_interaction = allow_user_interaction):
			raise gmExceptions.ConstructorError, "cannot activate an encounter for patient [%s]" % aPKey

		# FIXME: delegate to worker thread
		gmAllergy.ensure_has_allergy_state(encounter = self.current_encounter['pk_encounter'])

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.debug('Instantiated clinical record for patient [%s].' % self.pk_patient)
	#--------------------------------------------------------
	def __del__(self):
		pass
	#--------------------------------------------------------
	def cleanup(self):
		_log.debug('cleaning up after clinical record for patient [%s]' % self.pk_patient)
		return True
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		gmDispatcher.connect(signal = u'clin.encounter_mod_db', receiver = self.db_callback_encounter_mod_db)

		return True
	#--------------------------------------------------------
	def db_callback_encounter_mod_db(self, **kwds):

		# get the current encounter as an extra instance
		# from the database to check for changes
		curr_enc_in_db = gmEMRStructItems.cEncounter(aPK_obj = self.current_encounter['pk_encounter'])

		# the encounter just retrieved and the active encounter
		# have got the same transaction ID so there's no change
		# in the database, there could be a local change in
		# the active encounter but that doesn't matter
		# THIS DOES NOT WORK
#		if curr_enc_in_db['xmin_encounter'] == self.current_encounter['xmin_encounter']:
#			return True

		# there must have been a change to the active encounter
		# committed to the database from elsewhere,
		# we must fail propagating the change, however, if
		# there are local changes
		if self.current_encounter.is_modified():
			_log.debug('unsaved changes in active encounter, cannot switch to another one')
			raise ValueError('unsaved changes in active encounter, cannot switch to another one')

		if self.current_encounter.same_payload(another_object = curr_enc_in_db):
			_log.debug('clin.encounter_mod_db received but no change to active encounter payload')
			return True

		# there was a change in the database from elsewhere,
		# locally, however, we don't have any changes, therefore
		# we can propagate the remote change locally without
		# losing anything
		_log.debug('active encounter modified remotely, reloading and announcing the modification')
		self.current_encounter.refetch_payload()
		gmDispatcher.send(u'current_encounter_modified')

		return True
	#--------------------------------------------------------
	# API: family history
	#--------------------------------------------------------
	def get_family_history(self, episodes=None, issues=None, encounters=None):
		fhx = gmFamilyHistory.get_family_history (
			order_by = u'l10n_relation, condition',
			patient = self.pk_patient
		)

		if episodes is not None:
			fhx = filter(lambda f: f['pk_episode'] in episodes, fhx)

		if issues is not None:
			fhx = filter(lambda f: f['pk_health_issue'] in issues, fhx)

		if encounters is not None:
			fhx = filter(lambda f: f['pk_encounter'] in encounters, fhx)

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
	# API: performed procedures
	#--------------------------------------------------------
	def get_performed_procedures(self, episodes=None, issues=None):

		procs = gmEMRStructItems.get_performed_procedures(patient = self.pk_patient)

		if episodes is not None:
			procs = filter(lambda p: p['pk_episode'] in episodes, procs)

		if issues is not None:
			procs = filter(lambda p: p['pk_health_issue'] in issues, procs)

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
	# API: hospitalizations
	#--------------------------------------------------------
	def get_hospital_stays(self, episodes=None, issues=None, ongoing_only=False):
		stays = gmEMRStructItems.get_patient_hospital_stays(patient = self.pk_patient, ongoing_only = ongoing_only)
		if episodes is not None:
			stays = filter(lambda s: s['pk_episode'] in episodes, stays)
		if issues is not None:
			stays = filter(lambda s: s['pk_health_issue'] in issues, stays)
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
		where_parts = [u'pk_patient = %(pat)s']
		if cover_period is not None:
			where_parts.append(u'discharge > (now() - %(range)s)')

		cmd = u"""
			SELECT hospital, count(1) AS frequency
			FROM clin.v_hospital_stays
			WHERE
				%s
			GROUP BY hospital
			ORDER BY frequency DESC
		""" % u' AND '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows
	#--------------------------------------------------------
	# API: narrative
	#--------------------------------------------------------
	def add_notes(self, notes=None, episode=None, encounter=None):

		enc = gmTools.coalesce (
			encounter,
			self.current_encounter['pk_encounter']
		)

		for note in notes:
			success, data = gmClinNarrative.create_clin_narrative (
				narrative = note[1],
				soap_cat = note[0],
				episode_id = episode,
				encounter_id = enc
			)

		return True
	#--------------------------------------------------------
	def add_clin_narrative(self, note='', soap_cat='s', episode=None):
		if note.strip() == '':
			_log.info('will not create empty clinical note')
			return None
		if isinstance(episode, gmEMRStructItems.cEpisode):
			episode = episode['pk_episode']
		status, data = gmClinNarrative.create_clin_narrative (
			narrative = note,
			soap_cat = soap_cat,
			episode_id = episode,
			encounter_id = self.current_encounter['pk_encounter']
		)
		if not status:
			_log.error(str(data))
			return None
		return data
	#--------------------------------------------------------
	def get_clin_narrative(self, since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None):
		"""Get SOAP notes pertinent to this encounter.

			since
				- initial date for narrative items
			until
				- final date for narrative items
			encounters
				- list of encounters whose narrative are to be retrieved
			episodes
				- list of episodes whose narrative are to be retrieved
			issues
				- list of health issues whose narrative are to be retrieved
			soap_cats
				- list of SOAP categories of the narrative to be retrieved
		"""
		where_parts = [u'pk_patient = %(pat)s']
		args = {u'pat': self.pk_patient}

		if issues is not None:
			where_parts.append(u'pk_health_issue IN %(issues)s')
			args['issues'] = tuple(issues)

		if episodes is not None:
			where_parts.append(u'pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		if encounters is not None:
			where_parts.append(u'pk_encounter IN %(encs)s')
			args['encs'] = tuple(encounters)

		if soap_cats is not None:
			where_parts.append(u'c_vn.soap_cat IN %(cats)s')
			soap_cats = list(soap_cats)
			args['cats'] = [ cat.lower() for cat in soap_cats if cat is not None ]
			if None in soap_cats:
				args['cats'].append(None)
			args['cats'] = tuple(args['cats'])

		cmd = u"""
			SELECT
				c_vn.*,
				c_scr.rank AS soap_rank
			FROM
				clin.v_narrative c_vn
					LEFT JOIN clin.soap_cat_ranks c_scr on c_vn.soap_cat = c_scr.soap_cat
			WHERE %s
			ORDER BY date, soap_rank
		""" % u' AND '.join(where_parts)

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		filtered_narrative = [ gmClinNarrative.cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': row}) for row in rows ]

		if since is not None:
			filtered_narrative = filter(lambda narr: narr['date'] >= since, filtered_narrative)

		if until is not None:
			filtered_narrative = filter(lambda narr: narr['date'] < until, filtered_narrative)

		if providers is not None:
			filtered_narrative = filter(lambda narr: narr['modified_by'] in providers, filtered_narrative)

		return filtered_narrative
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
			time_range = time_range
		)
	#--------------------------------------------------------
	def search_narrative_simple(self, search_term=''):

		search_term = search_term.strip()
		if search_term == '':
			return []

		cmd = u"""
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
from clin.v_narrative4search vn4s
WHERE
	pk_patient = %(pat)s and
	vn4s.narrative ~ %(term)s
order by
	encounter_started
"""		# case sensitive
		rows, idx = gmPG2.run_ro_queries(queries = [
			{'cmd': cmd, 'args': {'pat': self.pk_patient, 'term': search_term}}
		])
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
			if not items_by_table.has_key(src_table):
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
		for src_table in items_by_table.keys():
			item_ids = items_by_table[src_table].keys()
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
				except:
					episode_name = view_row[view_col_idx['pk_episode']]
				try:
					issue_name = issue_map[view_row[view_col_idx['pk_health_issue']]]
				except:
					issue_name = view_row[view_col_idx['pk_health_issue']]

				if not emr_data.has_key(age):
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
				for col_name in table_col_idx.keys():
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
		union_query = u'\n	union all\n'.join ([
			u"""
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
			u'SELECT count(1) FROM clin.encounter WHERE fk_patient = %(pat)s',
			u'SELECT count(1) FROM clin.v_pat_items WHERE pk_patient = %(pat)s',
			u'SELECT count(1) FROM blobs.v_doc_med WHERE pk_patient = %(pat)s',
			u'SELECT count(1) FROM clin.v_test_results WHERE pk_patient = %(pat)s',
			u'SELECT count(1) FROM clin.v_hospital_stays WHERE pk_patient = %(pat)s',
			u'SELECT count(1) FROM clin.v_procedures WHERE pk_patient = %(pat)s',
			# active and approved substances == medication
			u"""
				SELECT count(1)
				FROM clin.v_substance_intakes
				WHERE
					pk_patient = %(pat)s
						AND
					is_currently_active IN (null, true)
						AND
					intake_is_approved_of IN (null, true)""",
			u'SELECT count(1) FROM clin.v_pat_vaccinations WHERE pk_patient = %(pat)s'
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

		cmd = u"SELECT dob from dem.v_basic_person where pk_identity = %(pk)s"
		args = {'pk': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		dob = rows[0]['dob']

		stats = self.get_statistics()
		first = self.get_first_encounter()
		last = self.get_last_encounter()
		probs = self.get_problems()

		txt = u''
		if len(probs) > 0:
			txt += _(' %s known problems, clinically relevant thereof:\n') % stats['problems']
		else:
			txt += _(' %s known problems\n') % stats['problems']
		for prob in probs:
			if not prob['clinically_relevant']:
				continue
			txt += u'   \u00BB%s\u00AB (%s)\n' % (
				prob['problem'],
				gmTools.bool2subst(prob['problem_active'], _('active'), _('inactive'))
			)
		txt += u'\n'
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
			txt += u'\n'
		else:
			txt += _(', most recently:\n%s\n') % self.get_latest_hospital_stay().format(left_margin = 3)
		# FIXME: perhaps only count "ongoing ones"
		txt += _(' %s performed procedures') % stats['procedures']
		if stats['procedures'] == 0:
			txt += u'\n'
		else:
			txt += _(', most recently:\n%s\n') % self.get_latest_performed_procedure().format(left_margin = 3)

		txt += u'\n'
		txt += _('Allergies and Intolerances\n')

		allg_state = self.allergy_state
		txt += (u' ' + allg_state.state_string)
		if allg_state['last_confirmed'] is not None:
			txt += _(' (last confirmed %s)') % gmDateTime.pydt_strftime(allg_state['last_confirmed'], '%Y %b %d')
		txt += u'\n'
		txt += gmTools.coalesce(allg_state['comment'], u'', u' %s\n')
		for allg in self.get_allergies():
			txt += u' %s: %s\n' % (
				allg['descriptor'],
				gmTools.coalesce(allg['reaction'], _('unknown reaction'))
			)

		meds = self.get_current_substance_intakes(order_by = u'intake_is_approved_of DESC, substance')
		if len(meds) > 0:
			txt += u'\n'
			txt += _('Medications and Substances')
			txt += u'\n'
		for m in meds:
			txt += u'%s\n' % m.format_as_one_line(left_margin = 1)

		fhx = self.get_family_history()
		if len(fhx) > 0:
			txt += u'\n'
			txt += _('Family History')
			txt += u'\n'
		for f in fhx:
			txt += u'%s\n' % f.format(left_margin = 1)

		jobs = get_occupations(pk_identity = self.pk_patient)
		if len(jobs) > 0:
			txt += u'\n'
			txt += _('Occupations')
			txt += u'\n'
		for job in jobs:
			txt += u' %s%s\n' % (
				job['l10n_occupation'],
				gmTools.coalesce(job['activities'], u'', u': %s')
			)

		vaccs = self.get_latest_vaccinations()
		if len(vaccs) > 0:
			txt += u'\n'
			txt += _('Vaccinations')
			txt += u'\n'
		inds = sorted(vaccs.keys())
		for ind in inds:
			ind_count, vacc = vaccs[ind]
			if dob is None:
				age_given = u''
			else:
				age_given = u' @ %s' % gmDateTime.format_apparent_age_medically(gmDateTime.calculate_apparent_age (
					start = dob,
					end = vacc['date_given']
				))
			since = _('%s ago') % gmDateTime.format_interval_medically(vacc['interval_since_given'])
			txt += u' %s (%s%s): %s%s (%s %s%s%s)\n' % (
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

		return txt
	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, patient=None):
		txt = u''
		for enc in self.get_encounters(skip_empty = True):
			txt += gmTools.u_box_horiz_4dashes * 70 + u'\n'
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
		cmd = u"SELECT * FROM clin.v_pat_allergies WHERE pk_patient=%s order by descriptor"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx = True)
		allergies = []
		for r in rows:
			allergies.append(gmAllergy.cAllergy(row = {'data': r, 'idx': idx, 'pk_field': 'pk_allergy'}))

		# ok, let's constrain our list
		filtered_allergies = []
		filtered_allergies.extend(allergies)

		if ID_list is not None:
			filtered_allergies = filter(lambda allg: allg['pk_allergy'] in ID_list, filtered_allergies)
			if len(filtered_allergies) == 0:
				_log.error('no allergies of list [%s] found for patient [%s]' % (str(ID_list), self.pk_patient))
				# better fail here contrary to what we do elsewhere
				return None
			else:
				return filtered_allergies

		if remove_sensitivities:
			filtered_allergies = filter(lambda allg: allg['type'] == 'allergy', filtered_allergies)
		if since is not None:
			filtered_allergies = filter(lambda allg: allg['date'] >= since, filtered_allergies)
		if until is not None:
			filtered_allergies = filter(lambda allg: allg['date'] < until, filtered_allergies)
		if issues is not None:
			filtered_allergies = filter(lambda allg: allg['pk_health_issue'] in issues, filtered_allergies)
		if episodes is not None:
			filtered_allergies = filter(lambda allg: allg['pk_episode'] in episodes, filtered_allergies)
		if encounters is not None:
			filtered_allergies = filter(lambda allg: allg['pk_encounter'] in encounters, filtered_allergies)

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
		cmd = u'delete FROM clin.allergy WHERE pk=%(pk_allg)s'
		args = {'pk_allg': pk_allergy}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def is_allergic_to(self, atcs=None, inns=None, brand=None):
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
			'brand': brand,
			'pat': self.pk_patient
		}
		allergenes = []
		where_parts = []

		if len(atcs) == 0:
			atcs = None
		if atcs is not None:
			where_parts.append(u'atc_code in %(atcs)s')
		if len(inns) == 0:
			inns = None
		if inns is not None:
			where_parts.append(u'generics in %(inns)s')
			allergenes.extend(inns)
		if brand is not None:
			where_parts.append(u'substance = %(brand)s')
			allergenes.append(brand)

		if len(allergenes) != 0:
			where_parts.append(u'allergene in %(allgs)s')
			args['allgs'] = tuple(allergenes)

		cmd = u"""
SELECT * FROM clin.v_pat_allergies
WHERE
	pk_patient = %%(pat)s
	AND ( %s )""" % u' OR '.join(where_parts)

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
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by

		args = {
			'pat': self.pk_patient,
			'open': open_status
		}
		where_parts = [u'pk_patient = %(pat)s']

		if open_status is not None:
			where_parts.append(u'episode_open IS %(open)s')

		if unlinked_only:
			where_parts.append(u'pk_health_issue is NULL')

		if issues is not None:
			where_parts.append(u'pk_health_issue IN %(issues)s')
			args['issues'] = tuple(issues)

		if id_list is not None:
			where_parts.append(u'pk_episode IN %(epis)s')
			args['epis'] = tuple(id_list)

		cmd = u"SELECT * FROM clin.v_pat_episodes WHERE %s %s" % (
			u' AND '.join(where_parts),
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
		cmd = u"""SELECT distinct pk_episode
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
	def add_episode(self, episode_name=None, pk_health_issue=None, is_open=False, allow_dupes=False):
		"""Add episode 'episode_name' for a patient's health issue.

		- silently returns if episode already exists
		"""
		episode = gmEMRStructItems.create_episode (
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

		issue_where = gmTools.coalesce(issue, u'', u'and pk_health_issue = %(issue)s')

		cmd = u"""
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
		cmd = u"""
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

		cmd = u"""SELECT pk_health_issue, pk_episode FROM clin.v_problem_list WHERE pk_patient = %(pat)s ORDER BY problem"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		# Instantiate problem items
		problems = []
		for row in rows:
			pk_args = {
				u'pk_patient': self.pk_patient,
				u'pk_health_issue': row['pk_health_issue'],
				u'pk_episode': row['pk_episode']
			}
			problems.append(gmEMRStructItems.cProblem(aPK_obj = pk_args, try_potential_problems = False))

		# include non-problems ?
		other_rows = []
		if include_closed_episodes:
			cmd = u"""SELECT pk_health_issue, pk_episode FROM clin.v_potential_problem_list WHERE pk_patient = %(pat)s and type = 'episode'"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			other_rows.extend(rows)

		if include_irrelevant_issues:
			cmd = u"""SELECT pk_health_issue, pk_episode FROM clin.v_potential_problem_list WHERE pk_patient = %(pat)s and type = 'health issue'"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
			other_rows.extend(rows)

		if len(other_rows) > 0:
			for row in other_rows:
				pk_args = {
					u'pk_patient': self.pk_patient,
					u'pk_health_issue': row['pk_health_issue'],
					u'pk_episode': row['pk_episode']
				}
				problems.append(gmEMRStructItems.cProblem(aPK_obj = pk_args, try_potential_problems = True))

		# filter ?
		if (episodes is None) and (issues is None):
			return problems

		# filter
		if issues is not None:
			problems = filter(lambda epi: epi['pk_health_issue'] in issues, problems)
		if episodes is not None:
			problems = filter(lambda epi: epi['pk_episode'] in episodes, problems)

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
	# API: health issues
	#--------------------------------------------------------
	def get_health_issues(self, id_list = None):

		cmd = u"SELECT *, xmin_health_issue FROM clin.v_health_issues WHERE pk_patient = %(pat)s ORDER BY description"
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
	def get_current_substance_intakes(self, include_inactive=True, include_unapproved=False, order_by=None, episodes=None, issues=None):

		where_parts = [u'pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if not include_inactive:
			where_parts.append(u'is_currently_active IN (true, null)')

		if not include_unapproved:
			where_parts.append(u'intake_is_approved_of IN (true, null)')

		if order_by is None:
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by

		cmd = u"SELECT * FROM clin.v_substance_intakes WHERE %s %s" % (
			u'\nAND '.join(where_parts),
			order_by
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		meds = [ gmMedication.cSubstanceIntakeEntry(row = {'idx': idx, 'data': r, 'pk_field': 'pk_substance_intake'})  for r in rows ]

		if episodes is not None:
			meds = filter(lambda s: s['pk_episode'] in episodes, meds)

		if issues is not None:
			meds = filter(lambda s: s['pk_health_issue'] in issues, meds)

		return meds
	#--------------------------------------------------------
	def add_substance_intake(self, pk_substance=None, pk_component=None, episode=None, preparation=None):
		return gmMedication.create_substance_intake (
			pk_substance = pk_substance,
			pk_component = pk_component,
			encounter = self.current_encounter['pk_encounter'],
			episode = episode,
			preparation = preparation
		)
	#--------------------------------------------------------
	def substance_intake_exists(self, pk_component=None, pk_substance=None):
		return gmMedication.substance_intake_exists (
			pk_component = pk_component,
			pk_substance = pk_substance,
			pk_identity = self.pk_patient
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
	def get_latest_vaccinations(self, episodes=None, issues=None):
		"""Returns latest given vaccination for each vaccinated indication.

		as a dict {'l10n_indication': cVaccination instance}

		Note that this will produce duplicate vaccination instances on combi-indication vaccines !
		"""
		# find the PKs
		args = {'pat': self.pk_patient}
		where_parts = [u'pk_patient = %(pat)s']

		if (episodes is not None) and (len(episodes) > 0):
			where_parts.append(u'pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		if (issues is not None) and (len(issues) > 0):
			where_parts.append(u'pk_episode IN (select pk from clin.episode where fk_health_issue IN %(issues)s)')
			args['issues'] = tuple(issues)

		cmd = u'SELECT pk_vaccination, l10n_indication, indication_count FROM clin.v_pat_last_vacc4indication WHERE %s' % u'\nAND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		# none found
		if len(rows) == 0:
			return {}

		vpks = [ ind['pk_vaccination'] for ind in rows ]
		vinds = [ ind['l10n_indication'] for ind in rows ]
		ind_counts = [ ind['indication_count'] for ind in rows ]

		# turn them into vaccinations
		cmd = gmVaccination.sql_fetch_vaccination % u'pk_vaccination IN %(pks)s'
		args = {'pks': tuple(vpks)}
		rows, row_idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		vaccs = {}
		for idx in range(len(vpks)):
			pk = vpks[idx]
			ind_count = ind_counts[idx]
			for r in rows:
				if r['pk_vaccination'] == pk:
					vaccs[vinds[idx]] = (ind_count, gmVaccination.cVaccination(row = {'idx': row_idx, 'data': r, 'pk_field': 'pk_vaccination'}))

		return vaccs
	#--------------------------------------------------------
	def get_vaccinations(self, order_by=None, episodes=None, issues=None, encounters=None):

		args = {'pat': self.pk_patient}
		where_parts = [u'pk_patient = %(pat)s']

		if order_by is None:
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by

		if (episodes is not None) and (len(episodes) > 0):
			where_parts.append(u'pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		if (issues is not None) and (len(issues) > 0):
			where_parts.append(u'pk_episode IN (SELECT pk FROM clin.episode WHERE fk_health_issue IN %(issues)s)')
			args['issues'] = tuple(issues)

		if (encounters is not None) and (len(encounters) > 0):
			where_parts.append(u'pk_encounter IN %(encs)s')
			args['encs'] = tuple(encounters)

		cmd = u'%s %s' % (
			gmVaccination.sql_fetch_vaccination % u'\nAND '.join(where_parts),
			order_by
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		vaccs = [ gmVaccination.cVaccination(row = {'idx': idx, 'data': r, 'pk_field': 'pk_vaccination'})  for r in rows ]

		return vaccs

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
			filtered_regimes = filter(lambda regime: regime['pk_course'] == ID, filtered_regimes)
			if len(filtered_regimes) == 0:
				_log.error('no vaccination course [%s] found for patient [%s]' % (ID, self.pk_patient))
				return []
			else:
				return filtered_regimes[0]
		if indications is not None:
			filtered_regimes = filter(lambda regime: regime['indication'] in indications, filtered_regimes)

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
			for ind in vaccs_by_ind.keys():
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

		# first ever setting ?
		if self.__encounter is None:
			_log.debug('first setting of active encounter in this clinical record instance')
		else:
			_log.debug('switching of active encounter')
			# fail if the currently active encounter has unsaved changes
			if self.__encounter.is_modified():
				_log.debug('unsaved changes in active encounter, cannot switch to another one')
				raise ValueError('unsaved changes in active encounter, cannot switch to another one')

		# be more conservative, it seems to have brought about
		# races involving encounter mod signals which made GNUmed crash
#		# set the currently active encounter and announce that change
#		if encounter['started'].strftime('%Y-%m-%d %H:%M') == encounter['last_affirmed'].strftime('%Y-%m-%d %H:%M'):
#			now = gmDateTime.pydt_now_here()
#			if now > encounter['started']:
#				encounter['last_affirmed'] = now		# this will trigger an "clin.encounter_mod_db"
#				encounter.save()
		prev_enc = None
		if self.__encounter is not None:
			prev_enc = self.__encounter
		encounter.lock(exclusive = False)		# lock new
		self.__encounter = encounter
		if prev_enc is not None:				# unlock old
			prev_enc.unlock(exclusive = False)
		gmDispatcher.send(u'current_encounter_switched')

		return True

	current_encounter = property(_get_current_encounter, _set_current_encounter)
	active_encounter = property(_get_current_encounter, _set_current_encounter)
	#------------------------------------------------------------------
	def __initiate_active_encounter(self, allow_user_interaction=True):

		# 1) "very recent" encounter recorded ?
		if self.__activate_very_recent_encounter():
			return True

		# 2) "fairly recent" encounter recorded ?
		if self.__activate_fairly_recent_encounter(allow_user_interaction = allow_user_interaction):
			return True

		# 3) start a completely new encounter
		self.start_new_encounter()
		return True
	#------------------------------------------------------------------
	def __activate_very_recent_encounter(self):
		"""Try to attach to a "very recent" encounter if there is one.

		returns:
			False: no "very recent" encounter, create new one
	    	True: success
		"""
		cfg_db = gmCfg.cCfgSQL()
		min_ttl = cfg_db.get2 (
			option = u'encounter.minimum_ttl',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'1 hour 30 minutes'
		)
		cmd = u"""
			SELECT pk_encounter
			FROM clin.v_most_recent_encounters
			WHERE
				pk_patient = %s
					and
				last_affirmed > (now() - %s::interval)
			ORDER BY
				last_affirmed DESC"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, min_ttl]}])
		# none found
		if len(enc_rows) == 0:
			_log.debug('no <very recent> encounter (younger than [%s]) found' % min_ttl)
			return False
		# attach to existing
		self.current_encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		_log.debug('"very recent" encounter [%s] found and re-activated' % enc_rows[0][0])
		return True
	#------------------------------------------------------------------
	def __activate_fairly_recent_encounter(self, allow_user_interaction=True):
		"""Try to attach to a "fairly recent" encounter if there is one.

		returns:
			False: no "fairly recent" encounter, create new one
	    	True: success
		"""
		if _func_ask_user is None:
			_log.debug('cannot ask user for guidance, not looking for fairly recent encounter')
			return False

		if not allow_user_interaction:
			_log.exception('user interaction not desired, not looking for fairly recent encounter')
			return False

		cfg_db = gmCfg.cCfgSQL()
		min_ttl = cfg_db.get2 (
			option = u'encounter.minimum_ttl',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'1 hour 30 minutes'
		)
		max_ttl = cfg_db.get2 (
			option = u'encounter.maximum_ttl',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'6 hours'
		)
		cmd = u"""
			SELECT pk_encounter
			FROM clin.v_most_recent_encounters
			WHERE
				pk_patient=%s
					AND
				last_affirmed BETWEEN (now() - %s::interval) AND (now() - %s::interval)
			ORDER BY
				last_affirmed DESC"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, max_ttl, min_ttl]}])
		# none found
		if len(enc_rows) == 0:
			_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
			return False

		_log.debug('"fairly recent" encounter [%s] found', enc_rows[0][0])

		encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		# ask user whether to attach or not
		cmd = u"""
			SELECT title, firstnames, lastnames, gender, dob
			FROM dem.v_basic_person WHERE pk_identity=%s"""
		pats, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		pat = pats[0]
		pat_str = u'%s %s %s (%s), %s  [#%s]' % (
			gmTools.coalesce(pat[0], u'')[:5],
			pat[1][:15],
			pat[2][:15],
			pat[3],
			gmDateTime.pydt_strftime(pat[4], '%Y %b %d'),
			self.pk_patient
		)
		msg = _(
			'%s\n'
			'\n'
			"This patient's chart was worked on only recently:\n"
			'\n'
			' %s  %s - %s  (%s)\n'
			'\n'
			' Reason for Encounter:\n'
			'  %s\n'
			' Assessment of Encounter:\n'
			'  %s\n'
			'\n'
			'Do you want to continue that consultation\n'
			'or do you want to start a new one ?\n'
		) % (
			pat_str,
			gmDateTime.pydt_strftime(encounter['started'], '%Y %b %d'),
			gmDateTime.pydt_strftime(encounter['started'], '%H:%M'), gmDateTime.pydt_strftime(encounter['last_affirmed'], '%H:%M'),
			encounter['l10n_type'],
			gmTools.coalesce(encounter['reason_for_encounter'], _('none given')),
			gmTools.coalesce(encounter['assessment_of_encounter'], _('none given')),
		)
		attach = False
		try:
			attach = _func_ask_user(msg = msg, caption = _('Starting patient encounter'), encounter = encounter)
		except:
			_log.exception('cannot ask user for guidance, not attaching to existing encounter')
			return False
		if not attach:
			return False

		# attach to existing
		self.current_encounter = encounter
		_log.debug('"fairly recent" encounter re-activated')
		return True
	#------------------------------------------------------------------
	def start_new_encounter(self):
		cfg_db = gmCfg.cCfgSQL()
		enc_type = cfg_db.get2 (
			option = u'encounter.default_type',
			workplace = _here.active_workplace,
			bias = u'user'
		)
		if enc_type is None:
			enc_type = gmEMRStructItems.get_most_commonly_used_encounter_type()
		if enc_type is None:
			enc_type = u'in surgery'
		enc = gmEMRStructItems.create_encounter(fk_patient = self.pk_patient, enc_type = enc_type)
		enc['pk_org_unit'] = _here['pk_org_unit']
		enc.save()
		self.current_encounter = enc
		_log.debug('new encounter [%s] initiated' % self.current_encounter['pk_encounter'])
	#------------------------------------------------------------------
	def get_encounters(self, since=None, until=None, id_list=None, episodes=None, issues=None, skip_empty=False):
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
		where_parts = [u'c_vpe.pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if skip_empty:
			where_parts.append(u"""NOT (
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
			where_parts.append(u'c_vpe.started >= %(start)s')
			args['start'] = since

		if until is not None:
			where_parts.append(u'c_vpe.last_affirmed <= %(end)s')
			args['end'] = since

		cmd = u"""
			SELECT *
			FROM clin.v_pat_encounters c_vpe
			WHERE
				%s
			ORDER BY started
		""" % u' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		encounters = [ gmEMRStructItems.cEncounter(row = {'data': r, 'idx': idx, 'pk_field': 'pk_encounter'}) for r in rows ]

		# we've got the encounters, start filtering
		filtered_encounters = []
		filtered_encounters.extend(encounters)

		if id_list is not None:
			filtered_encounters = filter(lambda enc: enc['pk_encounter'] in id_list, filtered_encounters)

		if (issues is not None) and (len(issues) > 0):
			issues = tuple(issues)
			# however, this seems like the proper approach:
			# - find episodes corresponding to the health issues in question
			cmd = u"SELECT distinct pk FROM clin.episode WHERE fk_health_issue in %(issues)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'issues': issues}}])
			epi_ids = map(lambda x:x[0], rows)
			if episodes is None:
				episodes = []
			episodes.extend(epi_ids)

		if (episodes is not None) and (len(episodes) > 0):
			episodes = tuple(episodes)
			# if the episodes to filter by belong to the patient in question so will
			# the encounters found with them - hence we don't need a WHERE on the patient ...
			cmd = u"SELECT distinct fk_encounter FROM clin.clin_root_item WHERE fk_episode in %(epis)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'epis': episodes}}])
			enc_ids = map(lambda x:x[0], rows)
			filtered_encounters = filter(lambda enc: enc['pk_encounter'] in enc_ids, filtered_encounters)

		return filtered_encounters
	#--------------------------------------------------------
	def get_first_encounter(self, issue_id=None, episode_id=None):
		"""Retrieves first encounter for a particular issue and/or episode.

		issue_id - First encounter associated health issue
		episode - First encounter associated episode
		"""
		# FIXME: use direct query
		if issue_id is None:
			issues = None
		else:
			issues = [issue_id]

		if episode_id is None:
			episodes = None
		else:
			episodes = [episode_id]

		encounters = self.get_encounters(issues=issues, episodes=episodes)
		if len(encounters) == 0:
			return None

		# FIXME: this does not scale particularly well, I assume
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[0]
	#--------------------------------------------------------
	def get_earliest_care_date(self):
		args = {'pat': self.pk_patient}
		cmd = u"""
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
	def get_last_encounter(self, issue_id=None, episode_id=None):
		"""Retrieves last encounter for a concrete issue and/or episode

		issue_id - Last encounter associated health issue
		episode_id - Last encounter associated episode
		"""
		# FIXME: use direct query

		if issue_id is None:
			issues = None
		else:
			issues = [issue_id]

		if episode_id is None:
			episodes = None
		else:
			episodes = [episode_id]

		encounters = self.get_encounters(issues=issues, episodes=episodes)
		if len(encounters) == 0:
			return None

		# FIXME: this does not scale particularly well, I assume
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[-1]

	last_encounter = property(get_last_encounter, lambda x:x)
	#------------------------------------------------------------------
	def get_encounter_stats_by_type(self, cover_period=None):
		args = {'pat': self.pk_patient, 'range': cover_period}
		where_parts = [u'pk_patient = %(pat)s']
		if cover_period is not None:
			where_parts.append(u'last_affirmed > now() - %(range)s')

		cmd = u"""
			SELECT l10n_type, count(1) AS frequency
			FROM clin.v_pat_encounters
			WHERE
				%s
			GROUP BY l10n_type
			ORDER BY frequency DESC
		""" % u' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows
	#------------------------------------------------------------------
	def get_last_but_one_encounter(self, issue_id=None, episode_id=None):

		args = {'pat': self.pk_patient}

		if (issue_id is None) and (episode_id is None):
			cmd = u"""
				SELECT * FROM clin.v_pat_encounters
				WHERE pk_patient = %(pat)s
				ORDER BY started DESC
				LIMIT 2
			"""
		else:
			where_parts = []

			if issue_id is not None:
				where_parts.append(u'pk_health_issue = %(issue)s')
				args['issue'] = issue_id

			if episode_id is not None:
				where_parts.append(u'pk_episode = %(epi)s')
				args['epi'] = episode_id

			cmd = u"""
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
			""" % u' AND '.join(where_parts)

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
	#------------------------------------------------------------------
	def remove_empty_encounters(self):
		cfg_db = gmCfg.cCfgSQL()
		ttl = cfg_db.get2 (
			option = u'encounter.ttl_if_empty',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'1 week'
		)

#		# FIXME: this should be done async
		cmd = u"SELECT clin.remove_old_empty_encounters(%(pat)s::INTEGER, %(ttl)s::INTERVAL)"
		args = {'pat': self.pk_patient, 'ttl': ttl}
		try:
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		except:
			_log.exception('error deleting empty encounters')

		return True
	#------------------------------------------------------------------
	# API: measurements / test results
	#------------------------------------------------------------------
	def get_most_recent_results(self, test_type=None, loinc=None, no_of_results=1):
		return gmPathLab.get_most_recent_results (
			test_type = test_type,
			loinc = loinc,
			no_of_results = no_of_results,
			patient = self.pk_patient
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
	def get_unsigned_results(self, order_by=None):
		if order_by is None:
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by
		cmd = u"""
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
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by

		if unique_meta_types:
			cmd = u"""
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
			cmd = u"""
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
		where_parts = [u'pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if tests is not None:
			where_parts.append(u'pk_test_type IN %(tests)s')
			args['tests'] = tuple(tests)

		cmd = u"""
			SELECT DISTINCT ON (clin_when_day) date_trunc('day', clin_when) as clin_when_day
			FROM clin.v_test_results
			WHERE %s
			ORDER BY clin_when_day %s
		""" % (
			u' AND '.join(where_parts),
			gmTools.bool2subst(reverse_chronological, u'DESC', u'ASC', u'DESC')
		)
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

		where_parts = [u'pk_patient = %(pat)s']
		args = {'pat': self.pk_patient}

		if tests is not None:
			where_parts.append(u'pk_test_type IN %(tests)s')
			args['tests'] = tuple(tests)

		if encounter is not None:
			where_parts.append(u'pk_encounter = %(enc)s')
			args['enc'] = encounter

		if episodes is not None:
			where_parts.append(u'pk_episode IN %(epis)s')
			args['epis'] = tuple(episodes)

		cmd = u"""
			SELECT * FROM clin.v_test_results
			WHERE %s
			ORDER BY clin_when %s, pk_episode, unified_name
		""" % (
			u' AND '.join(where_parts),
			gmTools.bool2subst(reverse_chronological, u'DESC', u'ASC', u'DESC')
		)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		tests = [ gmPathLab.cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ]

		return tests
	#------------------------------------------------------------------
	def add_test_result(self, episode=None, type=None, intended_reviewer=None, val_num=None, val_alpha=None, unit=None):

		try:
			epi = int(episode)
		except:
			epi = episode['pk_episode']

		try:
			type = int(type)
		except:
			type = type['pk_test_type']

		if intended_reviewer is None:
			intended_reviewer = gmStaff.gmCurrentProvider()['pk_staff']

		tr = gmPathLab.create_test_result (
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
	#-----------------------------------------
	def test_allergy_state():
		emr = cClinicalRecord(aPKey=1)
		state = emr.allergy_state
		print "allergy state is:", state

		print "setting state to 0"
		emr.allergy_state = 0

		print "setting state to None"
		emr.allergy_state = None

		print "setting state to 'abc'"
		emr.allergy_state = 'abc'
	#-----------------------------------------
	def test_get_test_names():
		emr = cClinicalRecord(aPKey = 6, allow_user_interaction = False)
		rows = emr.get_test_types_for_results(unique_meta_types = True)
		print "test result names:", len(rows)
#		for row in rows:
#			print row
	#-----------------------------------------
	def test_get_dates_for_results():
		emr = cClinicalRecord(aPKey=12)
		rows = emr.get_dates_for_results()
		print "test result dates:"
		for row in rows:
			print row
	#-----------------------------------------
	def test_get_measurements():
		emr = cClinicalRecord(aPKey=12)
		rows, idx = emr.get_measurements_by_date()
		print "test results:"
		for row in rows:
			print row
	#-----------------------------------------
	def test_get_test_results_by_date():
		emr = cClinicalRecord(aPKey=12)
		tests = emr.get_test_results_by_date()
		print "test results:"
		for test in tests:
			print test
	#-----------------------------------------
	def test_get_statistics():
		emr = cClinicalRecord(aPKey=12)
		for key, item in emr.get_statistics().iteritems():
			print key, ":", item
	#-----------------------------------------
	def test_get_problems():
		emr = cClinicalRecord(aPKey=12)

		probs = emr.get_problems()
		print "normal probs (%s):" % len(probs)
		for p in probs:
			print u'%s (%s)' % (p['problem'], p['type'])

		probs = emr.get_problems(include_closed_episodes=True)
		print "probs + closed episodes (%s):" % len(probs)
		for p in probs:
			print u'%s (%s)' % (p['problem'], p['type'])

		probs = emr.get_problems(include_irrelevant_issues=True)
		print "probs + issues (%s):" % len(probs)
		for p in probs:
			print u'%s (%s)' % (p['problem'], p['type'])

		probs = emr.get_problems(include_closed_episodes=True, include_irrelevant_issues=True)
		print "probs + issues + epis (%s):" % len(probs)
		for p in probs:
			print u'%s (%s)' % (p['problem'], p['type'])
	#-----------------------------------------
	def test_add_test_result():
		emr = cClinicalRecord(aPKey=12)
		tr = emr.add_test_result (
			episode = 1,
			intended_reviewer = 1,
			type = 1,
			val_num = 75,
			val_alpha = u'somewhat obese',
			unit = u'kg'
		)
		print tr
	#-----------------------------------------
	def test_get_most_recent_episode():
		emr = cClinicalRecord(aPKey=12)
		print emr.get_most_recent_episode(issue = 2)
	#-----------------------------------------
	def test_get_almost_recent_encounter():
		emr = cClinicalRecord(aPKey=12)
		print emr.get_last_encounter(issue_id=2)
		print emr.get_last_but_one_encounter(issue_id=2)
	#-----------------------------------------
	def test_get_meds():
		emr = cClinicalRecord(aPKey=12)
		for med in emr.get_current_substance_intakes():
			print med
	#-----------------------------------------
	def test_is_allergic_to():
		emr = cClinicalRecord(aPKey = 12)
		print emr.is_allergic_to(atcs = tuple(sys.argv[2:]), inns = tuple(sys.argv[2:]), brand = sys.argv[2])
	#-----------------------------------------
	def test_get_as_journal():
		emr = cClinicalRecord(aPKey = 12)
		for journal_line in emr.get_as_journal():
			#print journal_line.keys()
			print u'%(date)s  %(modified_by)s  %(soap_cat)s  %(narrative)s' % journal_line
			print ""
	#-----------------------------------------
	def test_get_most_recent():
		emr = cClinicalRecord(aPKey=12)
		print emr.get_most_recent_results()
	#-----------------------------------------
	def test_episodes():
		emr = cClinicalRecord(aPKey=12)
		print "episodes:", emr.episodes
		print "unlinked:", emr.unlinked_episodes

	#-----------------------------------------
	def test_format_as_journal():
		emr = cClinicalRecord(aPKey=12)
		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = 12)
		print emr.format_as_journal(left_margin = 1, patient = pat)
	#-----------------------------------------

	#test_allergy_state()
	#test_is_allergic_to()

	test_get_test_names()
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

#	emr = cClinicalRecord(aPKey = 12)

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
#	vaccinations = emr.get_vaccinations()
#	for a_vacc in vaccinations:
#		print '\nVaccination %s , date: %s, booster: %s, seq no: %s' %(a_vacc['batch_no'], a_vacc['date'].strftime('%Y-%m-%d'), a_vacc['is_booster'], a_vacc['seq_no'])

#	# first and last encounters
#	first_encounter = emr.get_first_encounter(issue_id = 1)
#	print '\nFirst encounter: ' + str(first_encounter)
#	last_encounter = emr.get_last_encounter(episode_id = 1)
#	print '\nLast encounter: ' + str(last_encounter)
#	print ''

	#dump = record.get_missing_vaccinations()
	#f = open('vaccs.lst', 'wb')
	#if dump is not None:
	#	print "=== due ==="
	#	f.write("=== due ===\n")
	#	for row in dump['due']:
	#		print row
	#		f.write(repr(row))
	#		f.write('\n')
	#	print "=== overdue ==="
	#	f.write("=== overdue ===\n")
	#	for row in dump['overdue']:
	#		print row
	#		f.write(repr(row))
	#		f.write('\n')
	#f.close()

