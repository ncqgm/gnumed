"""GNUmed clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

Make sure to call set_func_ask_user() and set_encounter_ttl()
early on in your code (before cClinicalRecord.__init__() is
called for the first time).
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.266 2008-06-16 15:01:01 ncq Exp $
__version__ = "$Revision: 1.266 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

#===================================================
# TODO
# Basically we'll probably have to:
#
# a) serialize access to re-getting data from the cache so
#   that later-but-concurrent cache accesses spin until
#   the first one completes the refetch from the database
#
# b) serialize access to the cache per-se such that cache
#    flushes vs. cache regets happen atomically (where
#    flushes would abort/restart current regets)
#===================================================

# standard libs
import sys, string, time, copy, locale


# 3rd party
import mx.DateTime as mxDT, psycopg2, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmLog2, gmDateTime, gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()
from Gnumed.pycommon import gmExceptions, gmPG2, gmDispatcher, gmI18N, gmCfg, gmTools
from Gnumed.business import gmAllergy, gmEMRStructItems, gmClinNarrative, gmPathLab


_log = logging.getLogger('gm.emr')
_log.debug(__version__)

_me = None
_here = None

_func_ask_user = None
#============================================================
class cClinicalRecord(object):

	_clin_root_item_children_union_query = None

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		from Gnumed.business import gmSurgery, gmPerson
		global _me
		if _me is None:
			_me = gmPerson.gmCurrentProvider()
		global _here
		if _here is None:
			_here = gmSurgery.gmCurrentPractice()

		# ...........................................
		# this is a hack to speed up get_encounters()
		clin_root_item_children = gmPG2.get_child_tables('clin', 'clin_root_item')
		if cClinicalRecord._clin_root_item_children_union_query is None:
			union_phrase = u"""
select fk_encounter from
	%s.%s cn
		inner join
	(select pk from clin.episode ep where ep.fk_health_issue in %%s) as epi
		on (cn.fk_episode =  epi.pk)
"""
			cClinicalRecord._clin_root_item_children_union_query = u'union\n'.join (
				[ union_phrase % (child[0], child[1]) for child in clin_root_item_children ]
			)
		# ...........................................

		self.pk_patient = aPKey			# == identity.pk == primary key

		self.__db_cache = {
			'vaccinations': {}
		}

		# load current or create new encounter
		self.remove_empty_encounters()
		self.__encounter = None
		if not self.__initiate_active_encounter():
			raise gmExceptions.ConstructorError, "cannot activate an encounter for patient [%s]" % aPKey

		self.ensure_has_allergic_state()

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
		return True
	#--------------------------------------------------------
	def db_callback_vaccs_modified(self, **kwds):
		try:
			self.__db_cache['vaccinations'] = {}
		except KeyError:
			pass
		return True
	#--------------------------------------------------------
	def _health_issues_modified(self):
		try:
			del self.__db_cache['health issues']
		except KeyError:
			pass
		try:
			del self.__db_cache['problems']
		except KeyError:
			pass
		return 1
	#--------------------------------------------------------
	def _db_callback_episodes_modified(self):
#		try:
#			del self.__db_cache['episodes']
#		except KeyError:
#			pass
		try:
			del self.__db_cache['problems']
		except KeyError:
			pass
		return 1
	#--------------------------------------------------------
	def _clin_item_modified(self):
		_log.debug('DB: clin_root_item modification')
	#--------------------------------------------------------
	# Narrative API
	#--------------------------------------------------------
	def add_clin_narrative(self, note='', soap_cat='s', episode=None):
		if note.strip() == '':
			_log.info('will not create empty clinical note')
			return None
		status, data = gmClinNarrative.create_clin_narrative (
			narrative = note,
			soap_cat = soap_cat,
			episode_id = episode['pk_episode'],
			encounter_id = self.__encounter['pk_encounter']
		)
		if not status:
			_log.error(str(data))
			return None
		return data
	#--------------------------------------------------------
	def get_clin_narrative(self, since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None):
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
		cmd = u"""
			select cvpn.*, (select rank from clin.soap_cat_ranks where soap_cat = cvpn.soap_cat) as soap_rank
			from clin.v_pat_narrative cvpn
			where pk_patient = %s
			order by date, soap_rank
		"""
		rows, idx = gmPG2.run_ro_queries(queries=[{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx=True)

		filtered_narrative = [ gmClinNarrative.cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': row}) for row in rows ]

		if since is not None:
			filtered_narrative = filter(lambda narr: narr['date'] >= since, filtered_narrative)

		if until is not None:
			filtered_narrative = filter(lambda narr: narr['date'] < until, filtered_narrative)

		if issues is not None:
			filtered_narrative = filter(lambda narr: narr['pk_health_issue'] in issues, filtered_narrative)

		if episodes is not None:
			filtered_narrative = filter(lambda narr: narr['pk_episode'] in episodes, filtered_narrative)

		if encounters is not None:
			filtered_narrative = filter(lambda narr: narr['pk_encounter'] in encounters, filtered_narrative)

		if soap_cats is not None:
			soap_cats = map(lambda c: c.lower(), soap_cats)
			filtered_narrative = filter(lambda narr: narr['soap_cat'] in soap_cats, filtered_narrative)

		return filtered_narrative
	#--------------------------------------------------------
	def search_narrative_simple(self, search_term=''):
		search_term = search_term.strip()
		if search_term == '':
			return False
		cmd = """
select * from clin.v_narrative4search vn4s
where
	pk_patient = %s and
	vn4s.narrative ~ %s"""		# case sensitive
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, search_term]}])
		return rows
	#--------------------------------------------------------
	def get_text_dump_old(self):
		# don't know how to invalidate this by means of
		# a notify without catching notifies from *all*
		# child tables, the best solution would be if
		# inserts in child tables would also fire triggers
		# of ancestor tables, but oh well,
		# until then the text dump will not be cached ...
		try:
			return self.__db_cache['text dump old']
		except KeyError:
			pass
		# not cached so go get it
		fields = [
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
		cmd = "select %s from clin.v_pat_items where pk_patient=%%s order by src_table, clin_when" % string.join(fields, ', ')
		ro_conn = self._conn_pool.GetConnection('historica')
		curs = ro_conn.cursor()
		if not gmPG2.run_query(curs, None, cmd, self.pk_patient):
			_log.error('cannot load item links for patient [%s]' % self.pk_patient)
			curs.close()
			return None
		rows = curs.fetchall()
		view_col_idx = gmPG2.get_col_indices(curs)

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
			issue_map[issue['pk']] = issue['description']
		episodes = self.get_episodes()
		episode_map = {}
		for episode in episodes:
			episode_map[episode['pk_episode']] = episode['description']
		emr_data = {}
		# get item data from all source tables
		for src_table in items_by_table.keys():
			item_ids = items_by_table[src_table].keys()
			# we don't know anything about the columns of
			# the source tables but, hey, this is a dump
			if len(item_ids) == 0:
				_log.info('no items in table [%s] ?!?' % src_table)
				continue
			elif len(item_ids) == 1:
				cmd = "select * from %s where pk_item=%%s order by modified_when" % src_table
				if not gmPG2.run_query(curs, None, cmd, item_ids[0]):
					_log.error('cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "select * from %s where pk_item in %%s order by modified_when" % src_table
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
					'pk_item', 'id', 'fk_encounter', 'fk_episode'
				]
				col_data = []
				for col_name in table_col_idx.keys():
					if col_name in cols2ignore:
						continue
					emr_data[age].append("=> %s:" % col_name)
					emr_data[age].append(row[table_col_idx[col_name]])
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
		self._conn_pool.ReleaseConnection('historica')
		return emr_data
	#--------------------------------------------------------
	def get_text_dump(self, since=None, until=None, encounters=None, episodes=None, issues=None):
		# don't know how to invalidate this by means of
		# a notify without catching notifies from *all*
		# child tables, the best solution would be if
		# inserts in child tables would also fire triggers
		# of ancestor tables, but oh well,
		# until then the text dump will not be cached ...
		try:
			return self.__db_cache['text dump']
		except KeyError:
			pass
		# not cached so go get it
		# -- get the data --
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
		select_from = "select %s from clin.v_pat_items" % ', '.join(fields)
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
		cmd = "%s where %s %s" % (select_from, where_clause, order_by)

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
			issue_map[issue['pk']] = issue['description']
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
				cmd = "select * from %s where pk_item=%%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, item_ids[0]):
					_log.error('cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "select * from %s where pk_item in %%s order by modified_when" % src_table
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
		self._conn_pool.ReleaseConnection('historica')
		return emr_data
	#--------------------------------------------------------
	def get_patient_ID(self):
		return self.pk_patient
	#--------------------------------------------------------
	def get_statistics(self):
		union_query = u'\n	union all\n'.join ([
			u'select count(*) from clin.v_problem_list where pk_patient = %(pat)s',
			u'select count(*) from clin.encounter where fk_patient = %(pat)s',
			u'select count(*) from clin.v_pat_items where pk_patient = %(pat)s',
			u'select count(*) from blobs.doc_med where fk_identity = %(pat)s',
			u'select count(*) from clin.v_test_results where pk_patient = %(pat)s'
		])

		rows, idx = gmPG2.run_ro_queries (
			queries = [{'cmd': union_query, 'args': {'pat': self.pk_patient}}],
			get_col_idx = False
		)

		stats = dict (
			problems = rows[0][0],
			visits = rows[1][0],
			items = rows[2][0],
			documents = rows[3][0],
			results = rows[4][0]
		)

		return stats
	#--------------------------------------------------------
	def format_statistics(self):
		return _("""Medical problems: %(problems)s
Total visits: %(visits)s
Total EMR entries: %(items)s
Documents: %(documents)s
Test results: %(results)s

"""			) % self.get_statistics()
	#--------------------------------------------------------
	def format_summary(self):

		stats = self.get_statistics()
		first = self.get_first_encounter()
		last = self.get_last_encounter()

		txt = _('EMR Statistics\n\n')
		txt += _(' %s known problems\n') % stats['problems']
		txt += _(' %s visits from %s to %s\n') % (
			stats['visits'],
			first['started'].strftime('%x'),
			last['started'].strftime('%x')
		)
		txt += _(' %s documents\n') % stats['documents']
		txt += _(' %s test results\n\n') % stats['results']

		if self.allergic_state:
			txt += _('Allergies and Intolerances\n\n')
			for allg in self.get_allergies():
				txt += u' %s: %s\n' % (
					allg['descriptor'],
					gmTools.coalesce(allg['reaction'], _('unknown reaction'))
				)

		return txt
	#--------------------------------------------------------
	# allergy API
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
		cmd = u"select * from clin.v_pat_allergies where pk_patient=%s order by descriptor"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx=True)
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
	def add_allergy(self, substance=None, allg_type=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.__encounter['pk_encounter']

		if episode_id is None:
			issue = self.add_health_issue(issue_name = _('allergies/intolerances'))
			epi = self.add_episode(episode_name = substance, pk_health_issue = issue['pk'])
			episode_id = epi['pk_episode']

		new_allergy = gmAllergy.create_allergy (
			substance = substance,
			allg_type = allg_type,
			encounter_id = encounter_id,
			episode_id = episode_id
		)

		return new_allergy
	#--------------------------------------------------------
	def delete_allergy(self, pk_allergy=None):
		cmd = u'delete from clin.allergy where pk=%(pk_allg)s'
		args = {'pk_allg': pk_allergy}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def ensure_has_allergic_state(self):
		cmd = u'insert into clin.allergy_state (fk_patient, has_allergy) values (%(pat)s, %(state)s)'
		args = {'pat': self.pk_patient, 'state': None}
		try:
			gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		except psycopg2.IntegrityError:
			pass		# ignore, row seems to exist already
		return True
	#--------------------------------------------------------
	def _set_allergic_state(self, state):
		if state not in gmAllergy.allergic_states:
			raise ValueError('[%s].__set_allergic_state(): <state> must be one of %s' % (self.__class__.__name__, gmAllergy.allergic_states))
		cmd = u'update clin.allergy_state set has_allergy = %(state)s where fk_patient = %(pat)s'
		args = {'pat': self.pk_patient, 'state': state}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	def _get_allergic_state(self):
		cmd = u'select has_allergy from clin.allergy_state where fk_patient = %(pat)s'
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows[0][0]

	allergic_state = property(_get_allergic_state, _set_allergic_state)
	#--------------------------------------------------------
	# episodes API
	#--------------------------------------------------------
	def get_episodes(self, id_list=None, issues=None, open_status=None):
		"""Fetches from backend patient episodes.

		id_list - Episodes' PKs list
		issues - Health issues' PKs list to filter episodes by
		open_status - return all episodes, only open or closed one(s)
		"""
		cmd = u"select * from clin.v_pat_episodes where pk_patient=%s"
		rows, idx = gmPG2.run_ro_queries(queries=[{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx=True)
		tmp = []
		for r in rows:
			tmp.append(gmEMRStructItems.cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'}))

		# now filter
		if (id_list is None) and (issues is None) and (open_status is None):
			return tmp

		# ok, let's filter episode list
		filtered_episodes = []
		filtered_episodes.extend(tmp)
		if open_status is not None:
			filtered_episodes = filter(lambda epi: epi['episode_open'] == open_status, filtered_episodes)

		if issues is not None:
			filtered_episodes = filter(lambda epi: epi['pk_health_issue'] in issues, filtered_episodes)

		if id_list is not None:
			filtered_episodes = filter(lambda epi: epi['pk_episode'] in id_list, filtered_episodes)

		return filtered_episodes
	#------------------------------------------------------------------
	def get_episodes_by_encounter(self, pk_encounter=None):
		cmd = u"""select distinct pk_episode
					from clin.v_pat_items
					where pk_encounter=%(enc)s and pk_patient=%(pat)s"""
		args = {
			'enc': gmTools.coalesce(pk_encounter, self.__encounter['pk_encounter']),
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
	def add_episode(self, episode_name=None, pk_health_issue=None, is_open=False):
		"""Add episode 'episode_name' for a patient's health issue.

		- silently returns if episode already exists
		"""		
		episode = gmEMRStructItems.create_episode (
			pk_health_issue = pk_health_issue,
			episode_name = episode_name,
			patient_id = self.pk_patient,
			is_open = is_open,
			encounter = self.__encounter['pk_encounter']
		)
		return episode
	#--------------------------------------------------------
	def get_most_recent_episode(issue=None):
		# try to find the episode with the most recently modified clinical item
		cmd = u"""
select pk
from clin.episode
where pk=(
	select distinct on(pk_episode) pk_episode
	from clin.v_pat_items
	where
		pk_patient=%s
			and
		modified_when=(
			select max(vpi.modified_when)
			from clin.v_pat_items vpi
			where vpi.pk_patient=%(pat)s
		)
	-- guard against several episodes created at the same moment of time
	limit 1
	)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		if len(rows) != 0:
			return gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])

		# no clinical items recorded, so try to find
		# the youngest episode for this patient
		cmd = u"""
select vpe0.pk_episode
from
	clin.v_pat_episodes vpe0
where
	vpe0.pk_patient = %s
		and
	vpe0.episode_modified_when = (
		select max(vpe1.episode_modified_when)
		from clin.v_pat_episodes vpe1
		where vpe1.pk_episode=vpe0.pk_episode
	)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		if len(rows) != 0:
			return gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])

		return None
	#--------------------------------------------------------
	def episode2problem(self, episode=None):
		return self.get_problems(episodes = [episode['pk_episode']])
	#--------------------------------------------------------
	# problems API
	#--------------------------------------------------------
	def get_problems(self, episodes = None, issues = None):
		"""
		Retrieve patient's problems: problems are the sum of issues w/o episodes,
		issues w/ episodes and episodes w/o issues
		
		episodes - Episodes' PKs to filter problems by
		issues - Health issues' PKs to filter problems by
		"""
#		try:
#			self.__db_cache['problems']
#		except KeyError:

		cmd = u"""select pk_health_issue, pk_episode from clin.v_problem_list where pk_patient=%s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx=True)
		self.__db_cache['problems'] = []
		# Instantiate problem items
		pk_args = {}
		for row in rows:
			pk_args['pk_health_issue'] = row[idx['pk_health_issue']]
			pk_args['pk_episode'] = row[idx['pk_episode']]
			problem = gmEMRStructItems.cProblem(aPK_obj=pk_args)
			self.__db_cache['problems'].append(problem)

		# now filter					
		if episodes is None and issues is None:
			return self.__db_cache['problems']
		# ok, let's filter problem list
		filtered_problems = []
		filtered_problems.extend(self.__db_cache['problems'])
		if issues is not None:
			filtered_problems = filter(lambda epi: epi['pk_health_issue'] in issues, filtered_problems)
		if episodes is not None:
			filtered_problems = filter(lambda epi: epi['pk_episode'] in episodes, filtered_problems)
		return filtered_problems
	#--------------------------------------------------------
	def problem2episode(self, problem=None):
		"""
		Retrieve the cEpisode instance equivalent to the given problem.
		The problem's type attribute must be 'episode'
		
		@param problem: The problem to retrieve its related episode for
		@type problem: A gmEMRStructItems.cProblem instance
		"""
		if isinstance(problem, gmEMRStructItems.cProblem) and (problem['type'] == 'episode'):
			return self.get_episodes(id_list=[problem['pk_episode']])[0]

		if isinstance(problem, gmEMRStructItems.cEpisode):
			return problem

		raise TypeError('cannot convert [%s] to episode' % problem)
	#--------------------------------------------------------
	def problem2issue(self, problem=None):
		"""
		Retrieve the cIssue instance equivalent to the given problem.
		The problem's type attribute must be 'issue'.
		
		@param problem: The problem to retrieve the corresponding issue for
		@type problem: A gmEMRStructItems.cProblem instance
		"""
		if isinstance(problem, gmEMRStructItems.cProblem) and (problem['type'] == 'issue'):
			return self.get_health_issues(id_list=[problem['pk_health_issue']])[0]

		if isinstance(problem, gmEMRStructItems.cHealthIssue):
			return problem

		raise TypeError('cannot convert [%s] to health issue' % problem)
	#--------------------------------------------------------
	def reclass_problem(self, problem):
		"""Transform given problem into either episode or health issue instance.
		"""
		if not isinstance(problem, gmEMRStructItems.cProblem):
			_log.debug(str(problem))
			raise TypeError, 'cannot reclass [%s] instance to problem' % type(problem)
		if problem['type'] == 'episode':
			return self.get_episodes(id_list=[problem['pk_episode']])[0]
		if problem['type'] == 'issue':
			return self.get_health_issues(id_list=[problem['pk_health_issue']])[0]
		return None
	#--------------------------------------------------------
	# health issues API
	#--------------------------------------------------------
	def get_health_issues(self, id_list = None):
		cmd = u"select *, xmin from clin.health_issue where fk_patient=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx = True)
		issues = []
		for row in rows:
			r = {'idx': idx, 'data': row, 'pk_field': 'pk'}
			issues.append(gmEMRStructItems.cHealthIssue(row=r))

		if id_list is None:
			return issues

		if len(id_list) == 0:
			raise ValueError('id_list to filter by is empty, most likely a programming error')

		filtered_issues = []
		for issue in issues:
			if issue['pk'] in id_list:
				filtered_issues.append(issue)

		return filtered_issues
	#------------------------------------------------------------------
	def add_health_issue(self, issue_name=None):
		"""Adds patient health issue."""
		success, issue = gmEMRStructItems.create_health_issue (
			patient_id = self.pk_patient,
			description = issue_name,
			encounter = self.__encounter['pk_encounter']
		)
		if not success:
			_log.error('cannot create health issue [%s] for patient [%s]' % (issue_name, self.pk_patient))
			return None
		return issue
	#--------------------------------------------------------
	def health_issue2problem(self, issue=None):
		return self.get_problems(issues = [issue['pk']])
	#--------------------------------------------------------
	# vaccinations API
	#--------------------------------------------------------
	def get_scheduled_vaccination_regimes(self, ID=None, indications=None):
		"""Retrieves vaccination regimes the patient is on.

			optional:
			* ID - PK of the vaccination regime				
			* indications - indications we want to retrieve vaccination
				regimes for, must be primary language, not l10n_indication
		"""
		# FIXME: use course, not regime
		try:
			self.__db_cache['vaccinations']['scheduled regimes']
		except KeyError:
			# retrieve vaccination regimes definitions
			self.__db_cache['vaccinations']['scheduled regimes'] = []
			cmd = """select distinct on(pk_course) pk_course
					 from clin.v_vaccs_scheduled4pat
					 where pk_patient=%s"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.error('cannot retrieve scheduled vaccination courses')
				del self.__db_cache['vaccinations']['scheduled regimes']
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
	def get_vaccinated_indications(self):
		"""Retrieves patient vaccinated indications list.

		Note that this does NOT rely on the patient being on
		some schedule or other but rather works with what the
		patient has ACTUALLY been vaccinated against. This is
		deliberate !
		"""
		# most likely, vaccinations will be fetched close
		# by so it makes sense to count on the cache being
		# filled (or fill it for nearby use)
		vaccinations = self.get_vaccinations()
		if vaccinations is None:
			_log.error('cannot load vaccinated indications for patient [%s]' % self.pk_patient)
			return (False, [[_('ERROR: cannot retrieve vaccinated indications'), _('ERROR: cannot retrieve vaccinated indications')]])
		if len(vaccinations) == 0:
			return (True, [[_('no vaccinations recorded'), _('no vaccinations recorded')]])
		v_indications = []
		for vacc in vaccinations:
			tmp = [vacc['indication'], vacc['l10n_indication']]
			# remove duplicates
			if tmp in v_indications:
				continue
			v_indications.append(tmp)
		return (True, v_indications)
	#--------------------------------------------------------
	def get_vaccinations(self, ID=None, indications=None, since=None, until=None, encounters=None, episodes=None, issues=None):
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
			cmd= """select * from clin.v_pat_vaccinations4indication
					where pk_patient=%s
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
			cmd = """select * from clin.v_vaccs_scheduled4pat where pk_patient=%s"""
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
			cmd = "select indication, seq_no from clin.v_pat_missing_vaccs where pk_patient=%s"
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
			cmd = "select indication, seq_no from clin.v_pat_missing_boosters where pk_patient=%s"
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
	#--------------------------------------------------------
	def add_vaccination(self, vaccine=None, episode=None):
		"""Creates a new vaccination entry in backend."""
		return gmVaccination.create_vaccination (
			patient_id = self.pk_patient,
			episode_id = episode['pk_episode'],
			encounter_id = self.__encounter['pk_encounter'],
			staff_id = _me['pk_staff'],
			vaccine = vaccine
		)
	#------------------------------------------------------------------
	# encounter API
	#------------------------------------------------------------------
	def __initiate_active_encounter(self):
		# 1) "very recent" encounter recorded ?
		if self.__activate_very_recent_encounter():
			return True
		# 2) "fairly recent" encounter recorded ?
		if self.__activate_fairly_recent_encounter():
			return True
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
			select pk_encounter
			from clin.v_most_recent_encounters
			where
				pk_patient = %s
					and
				last_affirmed > (now() - %s::interval)"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, min_ttl]}])
		# none found
		if len(enc_rows) == 0:
			_log.debug('no <very recent> encounter (younger than [%s]) found' % min_ttl)
			return False
		# attach to existing
		self.__encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		self.__encounter.set_active(staff_id = _me['pk_staff'])
		_log.debug('"very recent" encounter [%s] found and re-activated' % enc_rows[0][0])
		return True
	#------------------------------------------------------------------
	def __activate_fairly_recent_encounter(self):
		"""Try to attach to a "fairly recent" encounter if there is one.

		returns:
			False: no "fairly recent" encounter, create new one
	    	True: success
		"""
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
			select pk_encounter
			from clin.v_most_recent_encounters
			where
				pk_patient=%s
					and
				last_affirmed between (now() - %s::interval) and (now() - %s::interval)"""
		enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient, max_ttl, min_ttl]}])
		# none found
		if len(enc_rows) == 0:
			_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
			return False
		encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		# ask user whether to attach or not
		cmd = u"""
			select title, firstnames, lastnames, gender, dob
			from dem.v_basic_person where pk_identity=%s"""
		pats, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}])
		pat = pats[0]
		pat_str = u'%s %s %s (%s), %s, #%s' % (
			gmTools.coalesce(pat[0], u'')[:5],
			pat[1][:15],
			pat[2][:15],
			pat[3],
			pat[4].strftime('%Y-%m-%d'),
			self.pk_patient
		)
		enc = gmI18N.get_encoding()
		msg = _(
			'Very recently (between "%s" and "%s" ago)\n'
			'a consultation has been recorded for the patient:\n'
			'\n'
			' %s\n'
			'\n'
			'with the following details:\n'
			'\n'
			' date: %s\n'
			' time: %s - %s\n'
			' type: %s\n'
			' request: %s\n'
			' outcome: %s\n'
			'\n'
			'Do you want to continue this consultation\n'
			'or do you want to start a new one ?\n'
		) % (
			max_ttl,
			min_ttl,
			pat_str,
			encounter['started'].strftime('%x').decode(enc),
			encounter['started'].strftime('%H:%M'), encounter['last_affirmed'].strftime('%H:%M'),
			encounter['l10n_type'],
			gmTools.coalesce(encounter['reason_for_encounter'], _('none given')),
			gmTools.coalesce(encounter['assessment_of_encounter'], _('none given')),
		)
		attach = False
		try:
			attach = _func_ask_user(msg = msg, caption = _('starting patient encounter'))
		except:
			_log.exception('cannot ask user for guidance')
			return False
		if not attach:
			return False
		# attach to existing
		self.__encounter = encounter
		self.__encounter.set_active(staff_id = _me['pk_staff'])
		_log.debug('"fairly recent" encounter [%s] found and re-activated' % enc_rows[0][0])
		return True
	#------------------------------------------------------------------
	def start_new_encounter(self):
		cfg_db = gmCfg.cCfgSQL()
		enc_type = cfg_db.get2 (
			option = u'encounter.default_type',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'in surgery'
		)
		# FIXME: look for MRU/MCU encounter type config here
		self.__encounter = gmEMRStructItems.create_encounter(fk_patient = self.pk_patient, enc_type = enc_type)
		self.__encounter.set_active(staff_id = _me['pk_staff'])
		_log.debug('new encounter [%s] initiated' % self.__encounter['pk_encounter'])
	#------------------------------------------------------------------
	def get_active_encounter(self):
		return self.__encounter
	#------------------------------------------------------------------
	def get_encounters(self, since=None, until=None, id_list=None, episodes=None, issues=None):
		"""Retrieves patient's encounters.

		id_list - PKs of encounters to fetch
		since - initial date for encounter items, DateTime instance
		until - final date for encounter items, DateTime instance
		episodes - PKs of the episodes the encounters belong to (many-to-many relation)
		issues - PKs of the health issues the encounters belong to (many-to-many relation)

		NOTE: if you specify *both* issues and episodes
		you will get the *aggregate* of all encounters even
		if the episodes all belong to the health issues listed.
		IOW, the issues broaden the episode list rather than
		the episode list narrowing the episodes-from-issues
		list.
		Rationale: If it was the other way round it would be
		redundant to specify the list of issues at all.
		"""
		# fetch all encounters for patient
		cmd = u"select * from clin.v_pat_encounters where pk_patient=%s order by started"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_patient]}], get_col_idx=True)
		encounters = []
		for r in rows:
			encounters.append(gmEMRStructItems.cEncounter(row={'data': r, 'idx': idx, 'pk_field': 'pk_encounter'}))

		# we've got the encounters, start filtering
		filtered_encounters = []
		filtered_encounters.extend(encounters)
		if id_list is not None:
			filtered_encounters = filter(lambda enc: enc['pk_encounter'] in id_list, filtered_encounters)
		if since is not None:
			filtered_encounters = filter(lambda enc: enc['started'] >= since, filtered_encounters)
		if until is not None:
			filtered_encounters = filter(lambda enc: enc['last_affirmed'] <= until, filtered_encounters)

		if (issues is not None) and (len(issues) > 0):

			issues = tuple(issues)

			# Syan attests that an explicit union of child tables is way faster
			# as there seem to be problems with parent table expansion and use
			# of child table indexes, so if get_encounter() runs very slow on
			# your machine use the lines below

#			rows = gmPG.run_ro_query('historica', cClinicalRecord._clin_root_item_children_union_query, None, (tuple(issues),))
#			if rows is None:
#				_log.error('cannot load encounters for issues [%s] (patient [%s])' % (str(issues), self.pk_patient))
#			else:
#				enc_ids = map(lambda x:x[0], rows)
#				filtered_encounters = filter(lambda enc: enc['pk_encounter'] in enc_ids, filtered_encounters)

			# this problem seems fixed for us as of PostgreSQL 8.2  :-)

			# however, this seems like the proper approach:
			# - find episodes corresponding to the health issues in question
			cmd = u"select distinct pk from clin.episode where fk_health_issue in %(issues)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'issues': issues}}])
			epi_ids = map(lambda x:x[0], rows)
			if episodes is None:
				episodes = []
			episodes.extend(epi_ids)

		if (episodes is not None) and (len(episodes) > 0):

			episodes = tuple(episodes)

			# if the episodes to filter by belong to the patient in question so will
			# the encounters found with them - hence we don't need a WHERE on the patient ...
			cmd = u"select distinct fk_encounter from clin.clin_root_item where fk_episode in %(epis)s"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'epis': episodes}}])
			enc_ids = map(lambda x:x[0], rows)
			filtered_encounters = filter(lambda enc: enc['pk_encounter'] in enc_ids, filtered_encounters)

		return filtered_encounters
	#--------------------------------------------------------
	def get_first_encounter(self, issue_id=None, episode_id=None):
		"""Retrieves first encounter for a particular issue and/or episode

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

		encounters = self.get_encounters(issues=issues, episodes=episodes)
		if len(encounters) == 0:
			return None

		# FIXME: this does not scale particularly well, I assume
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[0]
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

		encounters = self.get_encounters(issues=issues, episodes=episodes)
		if len(encounters) == 0:
			return None

		# FIXME: this does not scale particularly well, I assume
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[-1]
	#------------------------------------------------------------------
	def remove_empty_encounters(self):
		# remove empty encounters
		cfg_db = gmCfg.cCfgSQL()
		ttl = cfg_db.get2 (
			option = u'encounter.ttl_if_empty',
			workplace = _here.active_workplace,
			bias = u'user',
			default = u'1 week'
		)

		# FIXME: this should be done async
		cmd = u"""
delete from clin.encounter where
	clin.encounter.fk_patient = %(pat)s and
	age(clin.encounter.last_affirmed) > %(ttl)s::interval and
	not exists (select 1 from clin.clin_root_item where fk_encounter = clin.encounter.pk) and
	not exists (select 1 from blobs.doc_med where fk_encounter = clin.encounter.pk) and
	not exists (select 1 from clin.episode where fk_encounter = clin.encounter.pk) and
	not exists (select 1 from clin.health_issue where fk_encounter = clin.encounter.pk) and
	not exists (select 1 from clin.operation where fk_encounter = clin.encounter.pk)
"""
		try:
			rows, idx = gmPG2.run_rw_queries(queries = [{
				'cmd': cmd,
				'args': {'pat': self.pk_patient, 'ttl': ttl}
			}])
		except:
			_log.exception('error deleting empty encounters')

		return True
	#------------------------------------------------------------------
	# measurements API
	#------------------------------------------------------------------
	def get_test_types_for_results(self):
		"""Retrieve data about test types for which this patient has results."""
		cmd = u"""
select foo.unified_name, foo.unified_code from (
	select distinct on (unified_name, unified_code)
		unified_name,
		unified_code,
		clin_when,
		pk_episode
	from clin.v_test_results
	where pk_patient = %(pat)s
) as foo
order by foo.clin_when desc, foo.pk_episode, foo.unified_name"""
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows
	#------------------------------------------------------------------
	def get_test_types_details(self):
		"""Retrieve details on tests grouped under unified names for this patient's results."""
		cmd = u"""
select * from clin.v_unified_test_types where pk_test_type in (
	select distinct on (unified_name, unified_code) pk_test_type
	from clin.v_test_results
	where pk_patient = %(pat)s
)
order by unified_name"""
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return rows, idx
	#------------------------------------------------------------------
	def get_dates_for_results(self):
		"""Get the dates for which we have results."""
		cmd = u"""
select distinct on (cwhen) date_trunc('day', clin_when) as cwhen
from clin.v_test_results
where pk_patient = %(pat)s
order by cwhen desc"""
		args = {'pat': self.pk_patient}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows
	#------------------------------------------------------------------
	def get_test_results_by_date(self):
		cmd = u"""
select *, xmin_test_result from clin.v_test_results
where pk_patient = %(pat)s
order by clin_when desc, pk_episode, unified_name"""
		args = {'pat': self.pk_patient}
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
			from Gnumed.business import gmPerson
			intended_reviewer = _me['pk_staff']

		tr = gmPathLab.create_test_result (
			encounter = self.__encounter['pk_encounter'],
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
	def get_lab_results(self, limit=None, since=None, until=None, encounters=None, episodes=None, issues=None):
		"""Retrieves lab result clinical items.

		limit - maximum number of results to retrieve
		since - initial date
		until - final date
		encounters - list of encounters
		episodes - list of episodes
		issues - list of health issues
		"""
		try:
			return self.__db_cache['lab results']
		except KeyError:
			pass
		self.__db_cache['lab results'] = []
		if limit is None:
			lim = ''
		else:
			# only use limit if all other constraints are None
			if since is None and until is None and encounters is None and episodes is None and issues is None:
				lim = "limit %s" % limit
			else:
				lim = ''

		cmd = """select * from clin.v_results4lab_req where pk_patient=%%s %s""" % lim
		rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
		if rows is None:
			return False
		for row in rows:
			lab_row = {
				'pk_field': 'pk_result',
				'idx': idx,
				'data': row
			}			
			lab_result = gmPathLab.cLabResult(row=lab_row)
			self.__db_cache['lab results'].append(lab_result)

		# ok, let's constrain our list
		filtered_lab_results = []
		filtered_lab_results.extend(self.__db_cache['lab results'])
		if since is not None:
			filtered_lab_results = filter(lambda lres: lres['req_when'] >= since, filtered_lab_results)
		if until is not None:
			filtered_lab_results = filter(lambda lres: lres['req_when'] < until, filtered_lab_results)
 		if issues is not None:
			filtered_lab_results = filter(lambda lres: lres['pk_health_issue'] in issues, filtered_lab_results)
		if episodes is not None:
			filtered_lab_results = filter(lambda lres: lres['pk_episode'] in episodes, filtered_lab_results)
		if encounters is not None:
			filtered_lab_results = filter(lambda lres: lres['pk_encounter'] in encounters, filtered_lab_results)
		return filtered_lab_results
	#------------------------------------------------------------------
	def get_lab_request(self, pk=None, req_id=None, lab=None):
		# FIXME: verify that it is our patient ? ...
		req = gmPathLab.cLabRequest(aPK_obj=pk, req_id=req_id, lab=lab)
		return req
	#------------------------------------------------------------------
	def add_lab_request(self, lab=None, req_id=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.__encounter['pk_encounter']
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
# convenience functions
#------------------------------------------------------------
def set_func_ask_user(a_func = None):
	if a_func is not None:
		global _func_ask_user
		_func_ask_user = a_func
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	#-----------------------------------------
	def test_allergic_state():
		emr = cClinicalRecord(aPKey=1)
		state = emr.allergic_state
		print "allergic state is:", state
		print "setting state to -1"
		emr.allergic_state = 'abc'
	#-----------------------------------------
	def test_get_test_names():
		emr = cClinicalRecord(aPKey=12)
		rows = emr.get_test_types_for_results()
		print "test result names:"
		for row in rows:
			print row
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
	def test_get_test_types_details():
		emr = cClinicalRecord(aPKey=12)
		rows, idx = emr.get_test_types_details()
		print "test type details:"
		for row in rows:
			print row
	#-----------------------------------------
	def test_get_statistics():
		emr = cClinicalRecord(aPKey=12)
		for key, item in emr.get_statistics().iteritems():
			print key, ":", item
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
	if (len(sys.argv) > 0) and (sys.argv[1] == 'test'):
		#test_allergic_state()
		#test_get_test_names()
		#test_get_dates_for_results()
		#test_get_measurements()
		#test_get_test_results_by_date()
		#test_get_test_types_details()
		#test_get_statistics()
		test_add_test_result()

	sys.exit(1)

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
		
#	# lab results
#	lab = emr.get_lab_results()
#	lab_file = open('lab-data.txt', 'wb')
#	for lab_result in lab:
#		lab_file.write(str(lab_result))
#		lab_file.write('\n')
#	lab_file.close()
		
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
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.266  2008-06-16 15:01:01  ncq
# - test suite cleanup
# - add_test_result
#
# Revision 1.265  2008/05/19 16:22:55  ncq
# - format_statistics/summary()
#
# Revision 1.264  2008/05/19 15:43:17  ncq
# - get_summary -> _statistics
# - get all statistics in one database roundtrip
# - fix test suite
#
# Revision 1.263  2008/04/22 21:12:08  ncq
# - get_test_results_by_date and test
#
# Revision 1.262  2008/04/11 23:07:08  ncq
# - fix remove_empty_encounters()
#
# Revision 1.261  2008/03/29 16:04:31  ncq
# - retrieve test results ordered by day-truncated date
#
# Revision 1.260  2008/03/20 15:28:17  ncq
# - get_test_types_details() w/ test
#
# Revision 1.259  2008/03/17 14:53:57  ncq
# - improve deletion of empty encounters
# - get_test_types_for_results()
# - get_dates_for_results()
# - get_measurements_by_date()
# - improve tests
#
# Revision 1.258  2008/03/05 22:24:31  ncq
# - support fk_encounter in issue and episode creation
#
# Revision 1.257  2008/02/25 16:58:03  ncq
# - use new logging
#
# Revision 1.256  2008/01/30 13:34:49  ncq
# - switch to std lib logging
#
# Revision 1.255  2008/01/16 19:43:28  ncq
# - use backend configured default encounter type in create_encounter()
# - configurable empty encounter removal age
#
# Revision 1.254  2007/12/26 18:31:53  ncq
# - remove reference to old PG library
#
# Revision 1.253  2007/12/11 12:59:11  ncq
# - cleanup and explicit signal handling
#
# Revision 1.252  2007/10/25 12:26:05  ncq
# - cleanup
#
# Revision 1.251  2007/10/25 12:15:39  ncq
# - we don't send allergy_updated() signal anymore, the backend does it for us
#
# Revision 1.250  2007/10/08 13:22:42  ncq
# - avoid circular import
#
# Revision 1.249  2007/10/08 13:17:55  ncq
# - missing gmPerson import
#
# Revision 1.248  2007/10/07 12:22:51  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.247  2007/09/24 22:07:32  ncq
# - be careful about deleting empty encounters - make sure they are at least 1 week old
#
# Revision 1.246  2007/09/07 10:55:40  ncq
# - order by in get_clin_narrative()
#
# Revision 1.245  2007/06/28 12:30:05  ncq
# - uncache get_clin_narrative access
#
# Revision 1.244  2007/06/19 12:40:40  ncq
# - cleanup
#
# Revision 1.243  2007/04/25 21:59:15  ncq
# - improve message on very-recent-encounter
#
# Revision 1.242  2007/04/06 23:12:58  ncq
# - move remove_empty_encounters() from cleanup() to init()
#
# Revision 1.241  2007/04/02 18:32:51  ncq
# - start_new_encounter()
#
# Revision 1.240  2007/04/01 15:25:25  ncq
# - safely get encoding
#
# Revision 1.239  2007/03/31 21:18:13  ncq
# - fix get_episodes_by_encounter()
#
# Revision 1.238  2007/03/26 16:49:26  ncq
# - settle on health issue/episode naming for newly added allergies
#
# Revision 1.237  2007/03/23 15:01:14  ncq
# - cleanup get_allergies() API
#
# Revision 1.236  2007/03/21 08:12:14  ncq
# - allergic_state property
# - send allergy_modified() signal
# - make cClinicalRecord a new-style class
#
# Revision 1.235  2007/03/18 13:01:16  ncq
# - re-add lost 1.235
# - add ensure_has_allergic_state()
# - remove allergies cache
# - add delete_allergy()
#
# Revision 1.235  2007/03/12 12:23:54  ncq
# - create_allergy() now throws exceptions so deal with that
#
# Revision 1.234  2007/03/02 15:29:33  ncq
# - need to decode() strftime() output to u''
#
# Revision 1.233  2007/02/19 14:06:56  ncq
# - add_health_issue() should return True if health_issue already exists
#
# Revision 1.232  2007/02/17 14:08:52  ncq
# - gmPerson.gmCurrentProvider.workplace now a property
#
# Revision 1.231  2007/02/09 14:58:43  ncq
# - honor <pk_encounter> in get_episodes_by_encounter
#   instead of always assuming the current encounter
#
# Revision 1.230  2007/01/31 23:30:33  ncq
# - fix __activate_fairly_recent_encounter()
#
# Revision 1.229  2007/01/29 11:58:53  ncq
# - cleanup
# - let _ask_user_func fail so programmers knows early
#
# Revision 1.228  2007/01/09 18:01:12  ncq
# - error policy is now exceptions
#
# Revision 1.227  2007/01/09 12:55:29  ncq
# - create_episode() now always takes patient fk
#
# Revision 1.226  2006/12/25 22:48:09  ncq
# - comment on PG 8.2 fixing child table index scans for us
#
# Revision 1.225  2006/12/13 13:41:33  ncq
# - add remove_empty_encounters() and call from cleanup()
#
# Revision 1.224  2006/12/13 00:30:43  ncq
# - fix get_health_issues() id_list sanity check insanity
#
# Revision 1.223  2006/11/28 20:39:30  ncq
# - improve problem2*()
# - de-cache get_health_issues()
#
# Revision 1.222  2006/11/26 15:43:41  ncq
# - keys in get_summary() shouldn't be _()
#
# Revision 1.221  2006/11/24 14:15:20  ncq
# - u'' one query
#
# Revision 1.220  2006/11/20 18:22:39  ncq
# - invalidate problem cache when health issues are updated, too
# - do not use cache for now when getting problems/episodes
#
# Revision 1.219  2006/11/19 10:50:35  ncq
# - fix get_episodes_by_encounter()
#
# Revision 1.218  2006/11/14 16:55:05  ncq
# - make sure issues/episodes are tuple()s in get_encounters()
#
# Revision 1.217  2006/11/05 17:53:15  ncq
# - one more get_col_idx
#
# Revision 1.216  2006/11/05 17:01:50  ncq
# - fix some queries to produce proper rows
# - var name fixes in get_encounters()
#
# Revision 1.215  2006/11/05 16:28:24  ncq
# - fix a few double uses of variable row
#
# Revision 1.214  2006/11/05 16:20:49  ncq
# - remove 2 printk()s
#
# Revision 1.213  2006/11/05 15:59:16  ncq
# - make encounter ttl configurable
# - audit clinical data retrieval and never appear to succeed if something fails
#   - this will show up some more exceptions which were thought harmless before and therefor masked out
# - u'' some queries
# - clarify get_encounters()
# - remove cruft
# - more gmPG -> gmPG2
#
# Revision 1.212  2006/10/28 15:01:21  ncq
# - speed up allergy, encounter fetching
# - unicode() queries
#
# Revision 1.211  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.210  2006/10/25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.209  2006/10/24 13:14:07  ncq
# - must import gmPG2, too, now
#
# Revision 1.208  2006/10/23 13:06:19  ncq
# - don't import path lab/vaccs business objects, they are not converted yet
# - use gmPG2 (not finished yet)
# - comment out backend signal handling for now
# - drop services support
#
# Revision 1.207  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.206  2006/06/26 12:25:30  ncq
# - cleanup
#
# Revision 1.205  2006/06/07 22:01:57  ncq
# - cVaccinationRegime -> cVaccinationCourse
#
# Revision 1.204  2006/05/28 15:25:18  ncq
# - ever better docs in get_encounters() just short of a proper fix
#
# Revision 1.203  2006/05/25 22:10:43  ncq
# - improve comment in get_encounters()
#
# Revision 1.202  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.201  2006/05/12 13:54:26  ncq
# - lazy import gmPerson
#
# Revision 1.200  2006/05/12 12:02:25  ncq
# - use gmCurrentProvider()
#
# Revision 1.199  2006/05/06 18:53:56  ncq
# - select age(...) <> ...; -> select ... <> now() - ...; as per Syan
#
# Revision 1.198  2006/05/04 18:01:39  ncq
# - "properly" include Syan's hack to speed up get_encounters()
#   - not active but has comment on how and when to activate it
#   - programmatically finds clin_root_item child tables :-)
# - vaccination regime -> course adjustments
# - try yet another approach in get_encounters() which really
#   should speed things up, too, without resorting to brute-force
#   child table resolution just yet
#
# Revision 1.197  2006/04/23 16:49:03  ncq
# - properly access encounters by health issue
#
# Revision 1.196  2006/04/23 16:46:28  ncq
# - do not select age field from clin.v_pat_items since it doesn't exist anymore
# - add get_summary()
# - try faster get_encounters()
#
# Revision 1.195  2006/02/27 22:38:36  ncq
# - spell out rfe/aoe as per Richard's request
#
# Revision 1.194  2006/01/07 13:00:19  ncq
# - add some schema qualifiers
#
# Revision 1.193  2005/12/26 12:03:10  sjtan
#
# more schema matching. some delegation .
#
# Revision 1.192  2005/12/25 13:24:30  sjtan
#
# schema changes in names .
#
# Revision 1.191  2005/12/10 22:55:17  ncq
# - fully log newly created encounters
#
# Revision 1.190  2005/12/06 14:24:14  ncq
# - clin.clin_health_issue/episode -> clin.health_issue/episode
#
# Revision 1.189  2005/11/27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.188  2005/11/18 15:16:15  ncq
# - add simple (non-context aware) search function
#
# Revision 1.187  2005/10/19 09:16:29  ncq
# - cleanup, return to well-defined state re narrative
#   cache rebuild, to be fixed later
#
# Revision 1.186  2005/10/15 18:19:23  ncq
# - cleanup
# - improved logging when initiating active encounter
#
# Revision 1.185  2005/10/11 21:03:13  ncq
# - a bit of cleanup re Syan's changes
#
# Revision 1.184  2005/10/08 12:33:08  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.183  2005/10/04 19:31:45  sjtan
# allow for flagged invalidation of cache and cache reloading.
#
# Revision 1.182  2005/09/22 15:45:11  ncq
# - clin_encounter.fk_provider removed
#
# Revision 1.181  2005/09/12 15:05:44  ncq
# - enhance get_episodes() to allow selection by is_open
#
# Revision 1.180  2005/09/11 17:21:55  ncq
# - get_episodes_by_encounter()
# - support is_open when adding episodes
#
# Revision 1.179  2005/09/09 13:49:25  ncq
# - add instance casts from/to episode/issue/problem
#
# Revision 1.178  2005/09/05 16:26:36  ncq
# - add reclass_problem()
# - improve problem2(episode | issue)
#
# Revision 1.177  2005/08/14 15:34:32  ncq
# - TODO item
#
# Revision 1.176  2005/08/06 16:03:31  ncq
# - guard against concurrent cache flushing
#
# Revision 1.175  2005/05/08 21:40:27  ncq
# - robustify get_first/last_encounter() as there may really be None
#
# Revision 1.174  2005/04/27 12:24:23  sjtan
#
# id_patient should be pk_patient ? changed a while ago. effect: enables emr_dump window to display.
#
# Revision 1.173  2005/04/24 14:41:04  ncq
# - cleanup, fail in add_health_issue if issue exists
#
# Revision 1.172  2005/04/11 17:54:19  ncq
# - cleanup
#
# Revision 1.171  2005/04/03 20:04:56  ncq
# - remove __load_active_episode() sillyness and related stuff
#
# Revision 1.170  2005/04/03 09:26:48  ncq
# - cleanup
#
# Revision 1.169  2005/03/30 22:07:35  ncq
# - guard against several "latest episodes"
# - maybe do away with the *explicit* "latest episode" stuff ?
#
# Revision 1.168  2005/03/23 18:30:40  ncq
# - v_patient_items -> v_pat_items
# - add problem2issue()
#
# Revision 1.167  2005/03/20 16:47:26  ncq
# - cleanup
#
# Revision 1.166  2005/03/17 21:15:29  cfmoro
# Added problem2episode cast method
#
# Revision 1.165  2005/03/14 18:16:52  cfmoro
# Create episode according to only_standalone_epi_has_patient backend constraint
#
# Revision 1.164  2005/03/14 14:27:21  ncq
# - id_patient -> pk_patient
# - rewrite add_episode() work with simplified episode naming
#
# Revision 1.163  2005/03/10 19:49:34  cfmoro
# Added episodes and issues constraints to get_problem
#
# Revision 1.162  2005/03/01 20:48:46  ncq
# - rearrange __init__ such that encounter is set up before episode
# - fix handling in __load_last_active_episode()
#
# Revision 1.161  2005/02/23 19:38:40  ncq
# - listen to episode changes in DB, too
#
# Revision 1.160  2005/02/20 10:31:44  sjtan
#
# lazy initialize preconditions for create_episode.
#
# Revision 1.159  2005/02/13 15:44:52  ncq
# - v_basic_person.i_pk -> pk_identity
#
# Revision 1.158  2005/02/12 13:52:45  ncq
# - identity.id -> pk
# - v_basic_person.i_id -> i_pk
# - self.id_patient -> self.pk_patient
#
# Revision 1.157  2005/02/02 19:55:26  cfmoro
# Delete problems cache on episodes modified callback method
#
# Revision 1.156  2005/01/31 20:25:07  ncq
# - listen on episode changes, too
#
# Revision 1.155  2005/01/29 19:20:49  cfmoro
# Commented out episode cache update after episode creation, should we use gmSignals?
#
# Revision 1.154  2005/01/29 19:14:00  cfmoro
# Added newly created episode to episode cache
#
# Revision 1.153  2005/01/15 19:55:55  cfmoro
# Added problem support to emr
#
# Revision 1.152  2004/12/18 15:57:57  ncq
# - Syan found a logging bug, which is now fixed
# - eventually fix bug in use of create_encounter() that
#   prevented gmSoapImporter from working properly
#
# Revision 1.151  2004/12/15 10:28:11  ncq
# - fix create_episode() aka add_episode()
#
# Revision 1.150  2004/10/27 12:09:28  ncq
# - properly set booster/seq_no in the face of the patient
#   not being on any vaccination schedule
#
# Revision 1.149  2004/10/26 12:51:24  ncq
# - Carlos: bulk load lab results
#
# Revision 1.148  2004/10/20 21:50:29  ncq
# - return [] on no vacc regimes found
# - in get_vaccinations() handle case where patient is not on any schedule
#
# Revision 1.147  2004/10/20 12:28:25  ncq
# - revert back to Carlos' bulk loading code
# - keep some bits of what Syan added
# - he likes to force overwriting other peoples' commits
# - if that continues his CVS rights are at stake (to be discussed
#   on list when appropriate)
#
# Revision 1.144  2004/10/18 11:33:48  ncq
# - more bulk loading
#
# Revision 1.143  2004/10/12 18:39:12  ncq
# - first cut at using Carlos' bulk fetcher in get_vaccinations(),
#   seems to work fine so far ... please test and report lossage ...
#
# Revision 1.142  2004/10/12 11:14:51  ncq
# - improve get_scheduled_vaccination_regimes/get_vaccinations, mostly by Carlos
#
# Revision 1.141  2004/10/11 19:50:15  ncq
# - improve get_allergies()
#
# Revision 1.140  2004/09/28 12:19:15  ncq
# - any vaccination related data now cached under 'vaccinations' so
#   all of it is flushed when any change to vaccinations occurs
# - rewrite get_scheduled_vaccination_regimes() (Carlos)
# - in get_vaccinations() compute seq_no and is_booster status
#
# Revision 1.139  2004/09/19 15:07:01  ncq
# - we don't use a default health issue anymore
# - remove duplicate existence checks
# - cleanup, reformat/fix episode queries
#
# Revision 1.138  2004/09/13 19:07:00  ncq
# - get_scheduled_vaccination_regimes() returns list of lists
#   (indication, l10n_indication, nr_of_shots) - this allows to
#   easily build table of given/missing vaccinations
#
# Revision 1.137  2004/09/06 18:54:31  ncq
# - some cleanup
# - in get_first/last_encounter we do need to check issue/episode for None so
#   we won't be applying the "one-item -> two-duplicate-items for IN query" trick
#   to "None" which would yield the wrong results
#
# Revision 1.136  2004/08/31 19:19:43  ncq
# - Carlos added constraints to get_encounters()
# - he also added get_first/last_encounter()
#
# Revision 1.135  2004/08/23 09:07:58  ncq
# - removed unneeded get_vaccinated_regimes() - was faulty anyways
#
# Revision 1.134  2004/08/11 09:44:15  ncq
# - gracefully continue loading clin_narrative items if one fails
# - map soap_cats filter to lowercase in get_clin_narrative()
#
# Revision 1.133  2004/08/11 09:01:27  ncq
# - Carlos-contributed get_clin_narrative() with usual filtering
#   and soap_cat filtering based on v_pat_narrative
#
# Revision 1.132  2004/07/17 21:08:51  ncq
# - gmPG.run_query() now has a verbosity parameter, so use it
#
# Revision 1.131  2004/07/06 00:11:11  ncq
# - make add_clin_narrative use gmClinNarrative.create_clin_narrative()
#
# Revision 1.130  2004/07/05 22:30:01  ncq
# - improve get_text_dump()
#
# Revision 1.129  2004/07/05 22:23:38  ncq
# - log some timings to find time sinks
# - get_clinical_record now takes between 4 and 11 seconds
# - record active episode at clinical record *cleanup* instead of startup !
#
# Revision 1.128  2004/07/02 00:20:54  ncq
# - v_patient_items.id_item -> pk_item
#
# Revision 1.127  2004/06/30 20:33:40  ncq
# - add_clinical_note() -> add_clin_narrative()
#
# Revision 1.126  2004/06/30 15:31:22  shilbert
# - fk/pk issue fixed
#
# Revision 1.125  2004/06/28 16:05:42  ncq
# - fix spurious 'id' for episode -> pk_episode
#
# Revision 1.124  2004/06/28 12:18:41  ncq
# - more id_* -> fk_*
#
# Revision 1.123  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.122  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.121  2004/06/20 18:39:30  ncq
# - get_encounters() added by Carlos
#
# Revision 1.120  2004/06/17 21:30:53  ncq
# - time range constraints in get()ters, by Carlos
#
# Revision 1.119  2004/06/15 19:08:15  ncq
# - self._backend -> self._conn_pool
# - remove instance level self._ro_conn_clin
# - cleanup
#
# Revision 1.118  2004/06/14 06:36:51  ncq
# - fix = -> == in filter(lambda ...)
#
# Revision 1.117  2004/06/13 08:03:07  ncq
# - cleanup, better separate vaccination code from general EMR code
#
# Revision 1.116  2004/06/13 07:55:00  ncq
# - create_allergy moved to gmAllergy
# - get_indications moved to gmVaccinations
# - many get_*()ers constrained by issue/episode/encounter
# - code by Carlos
#
# Revision 1.115  2004/06/09 14:33:31  ncq
# - cleanup
# - rewrite _db_callback_allg_modified()
#
# Revision 1.114  2004/06/08 00:43:26  ncq
# - add staff_id to add_allergy, unearthed by unittest
#
# Revision 1.113  2004/06/02 22:18:14  ncq
# - fix my broken streamlining
#
# Revision 1.112  2004/06/02 22:11:47  ncq
# - streamline Syan's check for failing create_episode() in __load_last_active_episode()
#
# Revision 1.111  2004/06/02 13:10:18  sjtan
#
# error handling , in case unsuccessful get_episodes.
#
# Revision 1.110  2004/06/01 23:51:33  ncq
# - id_episode/pk_encounter
#
# Revision 1.109  2004/06/01 08:21:56  ncq
# - default limit to all on get_lab_results()
#
# Revision 1.108  2004/06/01 08:20:14  ncq
# - limit in get_lab_results
#
# Revision 1.107  2004/05/30 20:51:34  ncq
# - verify provider in __init__, too
#
# Revision 1.106  2004/05/30 19:54:57  ncq
# - comment out attach_to_encounter(), actually, all relevant
#   methods should have encounter_id, episode_id kwds that
#   default to self.__*['id']
# - add_allergy()
#
# Revision 1.105  2004/05/28 15:46:28  ncq
# - get_active_episode()
#
# Revision 1.104  2004/05/28 15:11:32  ncq
# - get_active_encounter()
#
# Revision 1.103  2004/05/27 13:40:21  ihaywood
# more work on referrals, still not there yet
#
# Revision 1.102  2004/05/24 21:13:33  ncq
# - return better from add_lab_request()
#
# Revision 1.101  2004/05/24 20:52:18  ncq
# - add_lab_request()
#
# Revision 1.100  2004/05/23 12:28:58  ncq
# - fix missing : and episode reference before assignment
#
# Revision 1.99  2004/05/22 12:42:53  ncq
# - add create_episode()
# - cleanup add_episode()
#
# Revision 1.98  2004/05/22 11:46:15  ncq
# - some cleanup re allergy signal handling
# - get_health_issue_names doesn't exist anymore, so use get_health_issues
#
# Revision 1.97  2004/05/18 22:35:09  ncq
# - readd set_active_episode()
#
# Revision 1.96  2004/05/18 20:33:40  ncq
# - fix call to create_encounter() in __initiate_active_encounter()
#
# Revision 1.95  2004/05/17 19:01:40  ncq
# - convert encounter API to use encounter class
#
# Revision 1.94  2004/05/16 15:47:27  ncq
# - switch to use of episode class
#
# Revision 1.93  2004/05/16 14:34:45  ncq
# - cleanup, small fix in patient xdb checking
# - switch health issue handling to clin item class
#
# Revision 1.92  2004/05/14 13:16:34  ncq
# - cleanup, remove dead code
#
# Revision 1.91  2004/05/12 14:33:42  ncq
# - get_due_vaccinations -> get_missing_vaccinations + rewrite
#   thereof for value object use
# - __activate_fairly_recent_encounter now fails right away if it
#   cannot talk to the user anyways
#
# Revision 1.90  2004/05/08 17:41:34  ncq
# - due vaccs views are better now, so simplify get_due_vaccinations()
#
# Revision 1.89  2004/05/02 19:27:30  ncq
# - simplify get_due_vaccinations
#
# Revision 1.88  2004/04/24 12:59:17  ncq
# - all shiny and new, vastly improved vaccinations
#   handling via clinical item objects
# - mainly thanks to Carlos Moro
#
# Revision 1.87  2004/04/20 12:56:58  ncq
# - remove outdated get_due_vaccs(), use get_due_vaccinations() now
#
# Revision 1.86  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.85  2004/04/17 11:54:16  ncq
# - v_patient_episodes -> v_pat_episodes
#
# Revision 1.84  2004/04/15 09:46:56  ncq
# - cleanup, get_lab_data -> get_lab_results
#
# Revision 1.83  2004/04/14 21:06:10  ncq
# - return cLabResult from get_lab_data()
#
# Revision 1.82  2004/03/27 22:18:43  ncq
# - 7.4 doesn't allow aggregates in subselects which refer to outer-query
#   columns only, therefor use explicit inner query from list
#
# Revision 1.81  2004/03/25 11:00:19  ncq
# test get_lab_data()
#
# Revision 1.80  2004/03/23 17:32:59  ncq
# - support "unified" test code/name on get_lab_data()
#
# Revision 1.79  2004/03/23 15:04:59  ncq
# - merge Carlos' constraints into get_text_dump
# - add gmPatient.export_data()
#
# Revision 1.78  2004/03/23 02:29:24  ncq
# - cleanup import/add pyCompat
# - get_lab_data()
# - unit test
#
# Revision 1.77  2004/03/20 19:41:59  ncq
# - gmClin* cClin*
#
# Revision 1.76  2004/03/19 11:55:38  ncq
# - in allergy.reaction -> allergy.narrative
#
# Revision 1.75  2004/03/04 19:35:01  ncq
# - AU has rules on encounter timeout, so use them
#
# Revision 1.74  2004/02/25 09:46:19  ncq
# - import from pycommon now, not python-common
#
# Revision 1.73  2004/02/18 15:25:20  ncq
# - rewrote encounter support
#   - __init__() now initiates encounter
#   - _encounter_soft/hard_ttl now global mx.DateTime.TimeDelta
#   - added set_encounter_ttl()
#   - added set_func_ask_user() for UI callback on "fairly recent"
#     encounter detection
#
# Revision 1.72  2004/02/17 04:04:34  ihaywood
# fixed patient creation refeential integrity error
#
# Revision 1.71  2004/02/14 00:37:10  ihaywood
# Bugfixes
# 	- weeks = days / 7
# 	- create_new_patient to maintain xlnk_identity in historica
#
# Revision 1.70  2004/02/12 23:39:33  ihaywood
# fixed parse errors on vaccine queries (I'm using postgres 7.3.3)
#
# Revision 1.69  2004/02/02 23:02:40  ncq
# - it's personalia, not demographica
#
# Revision 1.68  2004/02/02 16:19:03  ncq
# - rewrite get_due_vaccinations() taking advantage of indication-based tables
#
# Revision 1.67  2004/01/26 22:08:52  ncq
# - gracefully handle failure to retrive vacc_ind
#
# Revision 1.66  2004/01/26 21:48:48  ncq
# - v_patient_vacc4ind -> v_pat_vacc4ind
#
# Revision 1.65  2004/01/24 17:07:46  ncq
# - fix insertion into xlnk_identity
#
# Revision 1.64  2004/01/21 16:52:02  ncq
# - eventually do the right thing in get_vaccinations()
#
# Revision 1.63  2004/01/21 15:53:05  ncq
# - use deepcopy when copying dict as to leave original intact in get_vaccinations()
#
# Revision 1.62  2004/01/19 13:41:15  ncq
# - fix typos in SQL
#
# Revision 1.61  2004/01/19 13:30:46  ncq
# - substantially smarten up __load_last_active_episode() after cleaning it up
#
# Revision 1.60  2004/01/18 21:41:49  ncq
# - get_vaccinated_indications()
# - make get_vaccinations() work against v_patient_vacc4ind
# - don't store vacc_def/link on saving vaccination
# - update_vaccination()
#
# Revision 1.59  2004/01/15 15:05:13  ncq
# - verify patient id in xlnk_identity in _pkey_exists()
# - make set_active_episode() logic more consistent - don't create default episode ...
# - also, failing to record most_recently_used episode should prevent us
#   from still keeping things up
#
# Revision 1.58  2004/01/12 16:20:14  ncq
# - set_active_episode() does not read rows from run_commit()
# - need to check for argument aVacc keys *before* adding
#   corresponding snippets to where/cols clause else we would end
#   up with orphaned query parts
# - also, aVacc will always have all keys, it's just that they may
#   be empty (because editarea.GetValue() will always return something)
# - fix set_active_encounter: don't ask for column index
#
# Revision 1.57  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.56  2004/01/06 09:56:41  ncq
# - default encounter name __default__ is nonsense, of course,
#   use mxDateTime.today().Format() instead
# - consolidate API:
#   - load_most_recent_episode() -> load_last_active_episode()
#   - _get_* -> get_*
#   - sort methods
# - convert more gmPG.run_query()
# - handle health issue on episode change as they are tighthly coupled
#
# Revision 1.55  2003/12/29 16:13:51  uid66147
# - listen to vaccination changes in DB
# - allow filtering by ID in get_vaccinations()
# - order get_due_vacc() by time_left/amount_overdue
# - add add_vaccination()
# - deal with provider in encounter handling
#
# Revision 1.54  2003/12/02 01:58:28  ncq
# - make get_due_vaccinations return the right thing on empty lists
#
# Revision 1.53  2003/12/01 01:01:05  ncq
# - add get_vaccinated_regimes()
# - allow regime_list filter in get_vaccinations()
# - handle empty lists better in get_due_vaccinations()
#
# Revision 1.52  2003/11/30 01:05:30  ncq
# - improve get_vaccinations
# - added get_vacc_regimes
#
# Revision 1.51  2003/11/28 10:06:18  ncq
# - remove dead code
#
# Revision 1.50  2003/11/28 08:08:05  ncq
# - improve get_due_vaccinations()
#
# Revision 1.49  2003/11/19 23:27:44  sjtan
#
# make _print()  a dummy function , so that  code reaching gmLog through this function works;
#
# Revision 1.48  2003/11/18 14:16:41  ncq
# - cleanup
# - intentionally comment out some methods and remove some code that
#   isn't fit for the main trunk such that it breaks and gets fixed
#   eventually
#
# Revision 1.47  2003/11/17 11:34:22  sjtan
#
# no ref to yaml
#
# Revision 1.46  2003/11/17 11:32:46  sjtan
#
# print ... -> _log.Log(gmLog.lInfo ...)
#
# Revision 1.45  2003/11/17 10:56:33  sjtan
#
# synced and commiting.
#
#
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.44  2003/11/16 19:30:26  ncq
# - use clin_when in clin_root_item
# - pretty _print(EMR text dump)
#
# Revision 1.43  2003/11/11 20:28:59  ncq
# - get_allergy_names(), reimplemented
#
# Revision 1.42  2003/11/11 18:20:58  ncq
# - fix get_text_dump() to actually do what it suggests
#
# Revision 1.41  2003/11/09 22:51:29  ncq
# - don't close cursor prematurely in get_text_dump()
#
# Revision 1.40  2003/11/09 16:24:03  ncq
# - typo fix
#
# Revision 1.39  2003/11/09 03:29:11  ncq
# - API cleanup, __set/getitem__ deprecated
#
# Revision 1.38  2003/10/31 23:18:48  ncq
# - improve encounter business
#
# Revision 1.37  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.36  2003/10/19 12:12:36  ncq
# - remove obsolete code
# - filter out sensitivities on get_allergy_names
# - start get_vacc_status
#
# Revision 1.35  2003/09/30 19:11:58  ncq
# - remove dead code
#
# Revision 1.34  2003/07/19 20:17:23  ncq
# - code cleanup
# - add cleanup()
# - use signals better
# - fix get_text_dump()
#
# Revision 1.33  2003/07/09 16:20:18  ncq
# - remove dead code
# - def_conn_ro -> ro_conn_clin
# - check for patient existence in personalia, not historica
# - listen to health issue changes, too
# - add _get_health_issues
#
# Revision 1.32  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.31  2003/07/05 13:44:12  ncq
# - modify -> modified
#
# Revision 1.30  2003/07/03 15:20:55  ncq
# - lots od cleanup, some nice formatting for text dump of EMR
#
# Revision 1.29  2003/06/27 22:54:29  ncq
# - improved _get_text_dump()
# - added _get_episode/health_issue_names()
# - remove old workaround code
# - sort test output by age, oldest on top
#
# Revision 1.28  2003/06/27 16:03:50  ncq
# - no need for ; in DB-API queries
# - implement EMR text dump
#
# Revision 1.27  2003/06/26 21:24:49  ncq
# - cleanup re quoting + ";" and (cmd, arg) style
#
# Revision 1.26  2003/06/26 06:05:38  ncq
# - always add ; at end of sql queries but have space after %s
#
# Revision 1.25  2003/06/26 02:29:20  ihaywood
# Bugfix for searching for pre-existing health issue records
#
# Revision 1.24  2003/06/24 12:55:08  ncq
# - eventually make create_clinical_note() functional
#
# Revision 1.23  2003/06/23 22:28:22  ncq
# - finish encounter handling for now, somewhat tested
# - use gmPG.run_query changes where appropriate
# - insert_clin_note() finished but untested
# - cleanup
#
# Revision 1.22  2003/06/22 16:17:40  ncq
# - start dealing with encounter initialization
# - add create_clinical_note()
# - cleanup
#
# Revision 1.21  2003/06/19 15:22:57  ncq
# - fix spelling error in SQL in episode creation
#
# Revision 1.20  2003/06/03 14:05:05  ncq
# - start listening threads last in __init__ so we won't hang
#   if anything else fails in the constructor
#
# Revision 1.19  2003/06/03 13:17:32  ncq
# - finish default clinical episode/health issue handling, simple tests work
# - clinical encounter handling still insufficient
# - add some more comments to Syan's code
#
# Revision 1.18  2003/06/02 20:58:32  ncq
# - nearly finished with default episode/health issue stuff
#
# Revision 1.17  2003/06/01 16:25:51  ncq
# - preliminary code for episode handling
#
# Revision 1.16  2003/06/01 15:00:31  sjtan
#
# works with definite, maybe note definate.
#
# Revision 1.15  2003/06/01 14:45:31  sjtan
#
# definite and definate databases catered for, temporarily.
#
# Revision 1.14  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.13  2003/06/01 14:15:48  ncq
# - more comments
#
# Revision 1.12  2003/06/01 14:11:52  ncq
# - added some comments
#
# Revision 1.11  2003/06/01 14:07:42  ncq
# - "select into" is an update command, too
#
# Revision 1.10  2003/06/01 13:53:55  ncq
# - typo fixes, cleanup, spelling definate -> definite
# - fix my obsolote handling of patient allergies tables
# - remove obsolete clin_transaction stuff
#
# Revision 1.9  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.8  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.7  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.6  2003/05/17 17:23:43  ncq
# - a little more testing in main()
#
# Revision 1.5  2003/05/05 00:06:32  ncq
# - make allergies work again after EMR rework
#
# Revision 1.4  2003/05/03 14:11:22  ncq
# - make allergy change signalling work properly
#
# Revision 1.3  2003/05/03 00:41:14  ncq
# - fetchall() returns list, not dict, so handle accordingly in "allergy names"
#
# Revision 1.2  2003/05/01 14:59:24  ncq
# - listen on allergy add/delete in backend, invalidate cache and notify frontend
# - "allergies", "allergy names" getters
#
# Revision 1.1  2003/04/29 12:33:20  ncq
# - first draft
#
