"""GnuMed preliminary clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

Make sure to call set_func_ask_user() and set_encounter_ttl()
early on in your code (before cClinicalRecord.__init__() is
called for the first time).
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.170 2005-04-03 09:26:48 ncq Exp $
__version__ = "$Revision: 1.170 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# standard libs
import sys, string, time, copy

# 3rd party
import mx.DateTime as mxDT

from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmWhoAmI, gmI18N
from Gnumed.business import gmPathLab, gmAllergy, gmVaccination, gmEMRStructItems, gmClinNarrative
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
_whoami = gmWhoAmI.cWhoAmI()

# in AU the soft timeout better be 4 hours as of 2004
_encounter_soft_ttl = mxDT.TimeDelta(hours=4)
_encounter_hard_ttl = mxDT.TimeDelta(hours=6)

_func_ask_user = None
#============================================================
class cClinicalRecord:

	# handlers for __getitem__()
	_get_handler = {}

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self._conn_pool = gmPG.ConnectionPool()

		self.pk_patient = aPKey			# == identity.pk == primary key
		if not self.__patient_exists():
			raise gmExceptions.ConstructorError, "No patient with PK [%s] in database." % aPKey

		if not self.__provider_exists():
			raise gmExceptions.ConstructorError, "cannot make sure provider [%s] is in service 'historica'" % _whoami.get_staff_ID()

		self.__db_cache = {
			'vaccinations': {}
		}

		# load current or create new encounter
		# FIXME: this should be configurable (for explanation see the method source)
		t1 = time.time()
		if not self.__initiate_active_encounter():
			raise gmExceptions.ConstructorError, "cannot activate an encounter for patient [%s]" % aPKey
		duration = time.time() - t1
		_log.Log(gmLog.lData, '__initiate_active_encounter() took %s seconds' % duration)

		# FIXME: really do this ?
		# what episode did we work on last time we saw this patient ?
		# also load corresponding health issue
		t1 = time.time()
		if not self.__load_last_active_episode():
			raise gmExceptions.ConstructorError, "cannot activate an episode for patient [%s]" % aPKey
		duration = time.time() - t1
		_log.Log(gmLog.lData, '__load_last_active_episode() took %s seconds' % duration)

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
		t1 = time.time()
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "cannot register signal interests"
		duration = time.time() - t1
		_log.Log(gmLog.lData, '_register_interests() took %s seconds' % duration)

		_log.Log(gmLog.lData, 'Instantiated clinical record for patient [%s].' % self.pk_patient)
	#--------------------------------------------------------
	def __del__(self):
		pass
	#--------------------------------------------------------
	def cleanup(self):
		self.__episode.set_active()
		_log.Log(gmLog.lData, 'cleaning up after clinical record for patient [%s]' % self.pk_patient)

		sig = "%s:%s" % (gmSignals.health_issue_change_db(), self.pk_patient)
		self._conn_pool.Unlisten(service = 'historica', signal = sig, callback = self._health_issues_modified)

		sig = "%s:%s" % (gmSignals.episode_change_db(), self.pk_patient)
		self._conn_pool.Unlisten(service = 'historica', signal = sig, callback = self._db_callback_episodes_modified)

		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.pk_patient)
		self._conn_pool.Unlisten(service = 'historica', signal = sig, callback = self.db_callback_vaccs_modified)

		sig = "%s:%s" % (gmSignals.allg_mod_db(), self.pk_patient)
		self._conn_pool.Unlisten(service = 'historica', signal = sig, callback = self._db_callback_allg_modified)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __patient_exists(self):
		"""Does this patient exist ?

		- true/false
		"""
		# patient in demographic database ?
		cmd = "select exists(select pk from identity where pk = %s)"
		result = gmPG.run_ro_query('personalia', cmd, None, self.pk_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in demographic database' % self.pk_patient)
			return False
		exists = result[0][0]
		if not exists:
			_log.Log(gmLog.lErr, "patient [%s] not in demographic database" % self.pk_patient)
			return False
		# patient linked in our local clinical database ?
		cmd = "select exists(select pk from xlnk_identity where xfk_identity = %s)"
		result = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in clinical database' % self.pk_patient)
			return False
		exists = result[0][0]
		if not exists:
			_log.Log(gmLog.lInfo, "patient [%s] not in clinical database" % self.pk_patient)
			cmd1 = "insert into xlnk_identity (xfk_identity, pupic) values (%s, %s)"
			cmd2 = "select currval('xlnk_identity_pk_seq')"
			status = gmPG.run_commit('historica', [
				(cmd1, [self.pk_patient, self.pk_patient]),
				(cmd2, [])
			])
			if status is None:
				_log.Log(gmLog.lErr, 'cannot insert patient [%s] into clinical database' % self.pk_patient)
				return False
			if status != 1:
				_log.Log(gmLog.lData, 'inserted patient [%s] into clinical database with local id [%s]' % (self.pk_patient, status[0][0]))
		return True
	#--------------------------------------------------------
	def __provider_exists(self):
		"""Make sure provider is linked in clinical database.
		"""
		pk_provider = _whoami.get_staff_ID()
		# provider linked in our local clinical database ?
		cmd = "select exists(select pk from xlnk_identity where xfk_identity = %s)"
		exists = gmPG.run_ro_query('historica', cmd, None, pk_provider)
		if exists is None:
			_log.Log(gmLog.lErr, 'unable to check for provider [%s] existence in clinical database' % pk_provider)
			return False
		if not exists[0][0]:
			_log.Log(gmLog.lInfo, "provider [%s] not in clinical database" % pk_provider)
			cmd1 = "insert into xlnk_identity (xfk_identity, pupic) values (%s, %s)"
			cmd2 = "select currval('xlnk_identity_pk_seq')"
			status = gmPG.run_commit('historica', [
				(cmd1, [pk_provider, pk_provider]),
				(cmd2, [])
			])
			if status is None:
				_log.Log(gmLog.lErr, 'cannot insert provider [%s] into clinical database' % pk_provider)
				return False
			if status != 1:
				_log.Log(gmLog.lData, 'inserted provider [%s] into clinical database with local id [%s]' % (pk_provider, status[0][0]))
		return True
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		# backend notifications
		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.pk_patient)
		if not self._conn_pool.Listen('historica', sig, self.db_callback_vaccs_modified):
			return None

		sig = "%s:%s" % (gmSignals.allg_mod_db(), self.pk_patient)
		if not self._conn_pool.Listen(service = 'historica', signal = sig, callback = self._db_callback_allg_modified):
			return None

		sig = "%s:%s" % (gmSignals.health_issue_change_db(), self.pk_patient)
		if not self._conn_pool.Listen(service = 'historica', signal = sig, callback = self._health_issues_modified):
			return None

		sig = "%s:%s" % (gmSignals.episode_change_db(), self.pk_patient)
		if not self._conn_pool.Listen(service = 'historica', signal = sig, callback = self._db_callback_episodes_modified):
			return None

		return 1
	#--------------------------------------------------------
	def db_callback_vaccs_modified(self, **kwds):
		try:
			self.__db_cache['vaccinations'] = {}
		except KeyError:
			pass
		gmDispatcher.send(signal = gmSignals.vaccinations_updated(), sender = self.__class__.__name__)
		return True
	#--------------------------------------------------------
	def _db_callback_allg_modified(self):
		try:
			del self.__db_cache['allergies']
		except KeyError:
			pass
		gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _health_issues_modified(self):
		try:
			del self.__db_cache['health issues']
		except KeyError:
			pass
		gmDispatcher.send(signal = gmSignals.health_issue_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _db_callback_episodes_modified(self):
		try:
			del self.__db_cache['episodes']			
		except KeyError:
			pass
		try:
			del self.__db_cache['problems']			
		except KeyError:
			pass
		gmDispatcher.send(signal = gmSignals.episodes_modified(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _clin_item_modified(self):
		_log.Log(gmLog.lData, 'DB: clin_root_item modification')
	#--------------------------------------------------------
	# Narrative API
	#--------------------------------------------------------
	def add_clin_narrative(self, note = '', soap_cat='s'):
		if note.strip() == '':
			_log.Log(gmLog.lInfo, 'will not create empty clinical note')
			return None
		status, data = gmClinNarrative.create_clin_narrative (
			narrative=note,
			soap_cat=soap_cat,
			episode_id=self.__episode['pk_episode'],
			encounter_id=self.__encounter['pk_encounter']
		)
		if not status:
			_log.Log(gmLog.lErr, str(data))
			return None
		return data
	#--------------------------------------------------------
	def get_clin_narrative(self, since=None, until=None, encounters=None,
		episodes=None, issues=None, soap_cats=None, exclude_rfe_aoe=False):
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
				- list of SOAP categories of the narrative to be retrived
			exclude_rfe_aoe
				-  when True, filter out RFE and AOE narrative
		"""
		try:
			self.__db_cache['narrative']
		except KeyError:
			self.__db_cache['narrative'] = []
			cmd = "select * from v_pat_narrative where pk_patient=%s order by date"
			rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load narrative for patient [%s]' % self.pk_patient)
				del self.__db_cache['narrative']
				return None
			# Instantiate narrative items and keep cache
			for row in rows:
				narr_row = {
					'pk_field': 'pk_narrative',
					'idx': idx,
					'data': row
				}
				try:
					narr = gmClinNarrative.cNarrative(row=narr_row)
					self.__db_cache['narrative'].append(narr)
				except gmExceptions.ConstructorError:
					_log.LogException('narrative error on [%s] for patient [%s]' % (row[0], self.pk_patient) , sys.exc_info(), verbose=0)

		# ok, let's constrain our list
		filtered_narrative = []
		filtered_narrative.extend(self.__db_cache['narrative'])
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
			soap_cats = map(lambda c:string.lower(c), soap_cats)
			filtered_narrative = filter(lambda narr: narr['soap_cat'] in soap_cats, filtered_narrative)
		if exclude_rfe_aoe:
			filtered_narrative = filter(lambda narr: True not in [narr['is_rfe'], narr['is_aoe']], filtered_narrative)

		return filtered_narrative
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.
		"""
		try:
			return cClinicalRecord._get_handler[aVar](self)
		except KeyError:
			_log.LogException('Missing get handler for [%s]' % aVar, sys.exc_info())
			return None
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
		cmd = "select %s from v_pat_items where pk_patient=%%s order by src_table, age" % string.join(fields, ', ')
		ro_conn = self._conn_pool.GetConnection('historica')
		curs = ro_conn.cursor()
		if not gmPG.run_query(curs, None, cmd, self.pk_patient):
			_log.Log(gmLog.lErr, 'cannot load item links for patient [%s]' % self.pk_patient)
			curs.close()
			return None
		rows = curs.fetchall()
		view_col_idx = gmPG.get_col_indices(curs)

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
			issue_map[issue['id']] = issue['description']
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
				_log.Log(gmLog.lInfo, 'no items in table [%s] ?!?' % src_table)
				continue
			elif len(item_ids) == 1:
				cmd = "select * from %s where pk_item=%%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, item_ids[0]):
					_log.Log(gmLog.lErr, 'cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "select * from %s where pk_item in %%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, (tuple(item_ids),)):
					_log.Log(gmLog.lErr, 'cannot load items from table [%s]' % src_table)
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
				#   are in v_pat_items data already
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
		select_from = "select %s from v_pat_items" % ', '.join(fields)
		# handle constraint conditions
		where_snippets = []
		params = {}
		where_snippets.append('id_patient=%(pat_id)s')
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
			_log.Log(gmLog.lErr, 'cannot load item links for patient [%s]' % self.pk_patient)
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
			issue_map[issue['id']] = issue['description']
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
				_log.Log(gmLog.lInfo, 'no items in table [%s] ?!?' % src_table)
				continue
			elif len(item_ids) == 1:
				cmd = "select * from %s where pk_item=%%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, item_ids[0]):
					_log.Log(gmLog.lErr, 'cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "select * from %s where pk_item in %%s order by modified_when" % src_table
				if not gmPG.run_query(curs, None, cmd, (tuple(item_ids),)):
					_log.Log(gmLog.lErr, 'cannot load items from table [%s]' % src_table)
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
				#   are in v_pat_items data already
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
	# allergy API
	#--------------------------------------------------------
 	def get_allergies(self, remove_sensitivities=None, since=None, until=None, encounters=None, episodes=None, issues=None, ID_list=None):
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
		try:
			self.__db_cache['allergies']
		except KeyError:
			# FIXME: check allergy_state first, then cross-check with select exists(... from allergy)
			self.__db_cache['allergies'] = []
			cmd = "select pk_allergy from v_pat_allergies where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load allergies for patient [%s]' % self.pk_patient)
				del self.__db_cache['allergies']
				# better fail here contrary to what we do elsewhere
				return None
			# Instantiate allergy items and keep cache
			for row in rows:
				try:
					self.__db_cache['allergies'].append(gmAllergy.cAllergy(aPK_obj=row[0]))
				except gmExceptions.ConstructorError:
					_log.LogException('allergy error on [%s] for patient [%s]' % (row[0], self.pk_patient) , sys.exc_info(), verbose=0)
					_log.Log(gmLog.lInfo, 'better to report an error than rely on incomplete allergy information')
					del self.__db_cache['allergies']
					return None

		# ok, let's constrain our list
		filtered_allergies = []
		filtered_allergies.extend(self.__db_cache['allergies'])
		if ID_list is not None:
			filtered_allergies = filter(lambda allg: allg['pk_allergy'] in ID_list, filtered_allergies)
			if len(filtered_allergies) == 0:
				_log.Log(gmLog.lErr, 'no allergies of list [%s] found for patient [%s]' % (str(ID_list), self.pk_patient))
				# better fail here contrary to what we do elsewhere
				return None
			else:
				return filtered_allergies
		if remove_sensitivities is not None:
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
			episode_id = self.__episode['pk_episode']
		status, data = gmAllergy.create_allergy(
			substance=substance,
			allg_type=allg_type,
			encounter_id=encounter_id,
			episode_id=episode_id
		)
		if not status:
			_log.Log(gmLog.lErr, str(data))
			return None
		return data
	#--------------------------------------------------------
	def set_allergic_state(self, status=None):
		pass
	#--------------------------------------------------------
	# episodes API
	#--------------------------------------------------------
	def get_active_episode(self):
		return self.__episode
	#--------------------------------------------------------
	def get_episodes(self, id_list=None, issues = None):
		"""Fetches from backend patient episodes.

		id_list - Episodes' PKs
		issues - Health issues' PKs to filter episodes by
		"""
		try:
			self.__db_cache['episodes']
		except KeyError:
			self.__db_cache['episodes'] = []

			cmd = "select pk_episode from v_pat_episodes where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error loading episodes for patient [%s]' % self.pk_patient)
				del self.__db_cache['episodes']
				return None
			for row in rows:
				try:
					self.__db_cache['episodes'].append(gmEMRStructItems.cEpisode(aPK_obj=row[0]))
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)

		if id_list is None and issues is None:
			return self.__db_cache['episodes']
		# ok, let's filter episode list
		filtered_episodes = []
		filtered_episodes.extend(self.__db_cache['episodes'])
		if issues is not None:
			filtered_episodes = filter(lambda epi: epi['pk_health_issue'] in issues, filtered_episodes)
		if id_list is not None:
			if id_list == []:
				_log.Log(gmLog.lErr, 'id_list to filter by is empty, most likely a programming error')
			filtered_episodes = filter(lambda epi: epi['pk_episode'] in id_list, filtered_episodes)
		return filtered_episodes
	#------------------------------------------------------------------
	def add_episode(self, episode_name=None, pk_health_issue=None):
		"""Add episode 'episode_name' for a patient's health issue.

		- silently returns if episode already exists
		"""		
		if pk_health_issue is None:
			# create unattached episode for the current patient
			success, episode = gmEMRStructItems.create_episode (
				episode_name = episode_name,
				patient_id = self.pk_patient
			)
		else:
			# create episode for given health issue			
			success, episode = gmEMRStructItems.create_episode (
				pk_health_issue = pk_health_issue,
				episode_name = episode_name
			)			
		if not success:
			_log.Log(gmLog.lErr, 'cannot create episode [%s] for patient [%s] and health issue [%s]' % (episode_name, self.pk_patient, pk_health_issue))
			return None
		return episode
	#--------------------------------------------------------
	def __load_last_active_episode(self):
		# check if there's an active episode
		episode = None
		cmd = "select fk_episode from last_act_episode where id_patient=%s limit 1"
		rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting last_act_episode for patient [%s]' % self.pk_patient)
		else:
			if len(rows) != 0:
				try:
					episode = gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)

		# no last_active_episode recorded, so try to find the
		# episode with the most recently modified clinical item
		if episode is None:
			cmd = """
select pk
from clin_episode
where pk=(
	select distinct on(pk_episode) pk_episode
	from v_pat_items
	where
		pk_patient=%s
			and
		modified_when=(
			select max(vpi.modified_when)
			from v_pat_items vpi
			where vpi.pk_patient=%s
		)
	-- guard against several episodes created at the same moment of time
	limit 1
	)"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error getting most recent episode from v_pat_items for patient [%s]' % self.pk_patient)
			else:
				if len(rows) != 0:
					try:
						episode = gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])
						episode.set_active()
					except gmExceptions.ConstructorError, msg:
						_log.LogException(str(msg), sys.exc_info(), verbose=0)
						episode = None

		# no clinical items recorded, so try to find
		# the youngest episode for this patient
		if episode is None:
			cmd = """
select vpe0.pk_episode
from
	v_pat_episodes vpe0
where
	vpe0.pk_patient = %s
		and
	vpe0.episode_modified_when = (
		select max(vpe1.episode_modified_when)
		from v_pat_episodes vpe1
		where vpe1.pk_episode=vpe0.pk_episode
	)"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error getting most recently touched episode on patient [%s]' % self.pk_patient)
			else:
				if len(rows) != 0:
					try:
						episode = gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])
						episode.set_active()
					except gmExceptions.ConstructorError, msg:
						_log.Log(str(msg), sys.exc_info(), verbose=0)
						episode = None

		# none found whatsoever
		if episode is None:
			# so try to create default episode ...
			# FIXME: really create default episode ???
			success, result = gmEMRStructItems.create_episode (
				episode_name = 'xxxDEFAULTxxx',
				patient_id = self.pk_patient
			)
			if not success:
				_log.Log(gmLog.lErr, 'cannot even activate default episode for patient [%s], aborting' %  self.pk_patient)
				_log.Log(gmLog.lErr, result)
				return False
			episode = result
			episode.set_active()

		self.__episode = episode
		# load corresponding health issue
		self.__health_issue = None
		if self.__episode['pk_health_issue'] is not None:
			self.__health_issue = self.get_health_issues(id_list=[self.__episode['pk_health_issue']])
			if self.__health_issue is None:
				_log.Log(gmLog.lErr, 'cannot activate health issue linked from episode [%s]' % str(self.__episode))

		return True
	#--------------------------------------------------------
	def set_active_episode(self, ep_name='xxxDEFAULTxxx'):
		if self.get_episodes() is None:
			_log.Log(gmLog.lErr, 'cannot activate episode [%s], cannot get episode list' % ep_name)
			return False
		for episode in self.__db_cache['episodes']:
			if episode['description'] == ep_name:
				episode.set_active()
				return True
		_log.Log(gmLog.lErr, 'cannot activate episode [%s], not found in list' % ep_name)
		return False
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
		try:
			self.__db_cache['problems']
		except KeyError:
			self.__db_cache['problems'] = []
			cmd= """select pk_health_issue, pk_episode from v_problem_list
					where pk_patient=%s"""
			rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load problems for patient [%s]' % self.pk_patient)
				del self.__db_cache['problems']
				return None
			# Instantiate problem items
			pk_args = {}
			for row in rows:
				pk_args['pk_health_issue'] = row[idx['pk_health_issue']]
				pk_args['pk_episode'] = row[idx['pk_episode']]				
				try:
					problem = gmEMRStructItems.cProblem(aPK_obj=pk_args)
					self.__db_cache['problems'].append(problem)
				except gmExceptions.ConstructorError:
					_log.LogException('problem error on [%s] for patient [%s]' % (row, self.pk_patient), sys.exc_info(), verbose=0)
					
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
	def problem2episode(self, problem):
		"""
		Retrieve the cEpisode instance equivalent to the given problem.
		The problem's type attribute must be 'episode'
		
		@param problem: The problem to retrieve its related episode for
		@type problem: A gmEMRStructItems.cProblem instance
		"""
		if problem['type'] != 'episode':
			_log.Log(gmLog.lErr, 'cannot convert non episode problem to episode: problem [%s] type [%s]' % (problem['problem'], problem['type']))
			return None
		return self.get_episodes(id_list=[problem['pk_episode']])[0]
	#--------------------------------------------------------
	# health issues API
	#--------------------------------------------------------
	def get_health_issues(self, id_list = None):
		try:
			self.__db_cache['health issues']
		except KeyError:
			self.__db_cache['health issues'] = []
			cmd = "select id from clin_health_issue where id_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load health issues for patient [%s]' % self.pk_patient)
				del self.__db_cache['health issues']
				return None
			for row in rows:
				try:
					self.__db_cache['health issues'].append(gmEMRStructItems.cHealthIssue(aPK_obj=row[0]))
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)
		if id_list is None:
			return self.__db_cache['health issues']
		if id_list == []:
			_log.Log(gmLog.lErr, 'id_list to filter by is empty, most likely a programming error')
		filtered_issues = []
		for issue in self.__db_cache['health issues']:
			if issue['id'] in id_list:
				filtered_issues.append(issue)
		return filtered_issues
	#------------------------------------------------------------------
	def add_health_issue(self, health_issue_name=None):
		"""Adds patient health issue.

		- silently returns if it already exists
		"""
		issues = self.get_health_issues()
		l = [i for i in issues if  i['description'] == health_issue_name]
		if len(l) > 0:
			return l[0]
		
	
		success, issue = gmEMRStructItems.create_health_issue(patient_id=self.pk_patient, description=health_issue_name)
		if not success:
			_log.Log(gmLog.lErr, 'cannot create health issue [%s] for patient [%s]' % (health_issue_name, self.pk_patient))
			return None
		return issue
	#--------------------------------------------------------
	def problem2issue(self, problem):
		"""
		Retrieve the cIssue instance equivalent to the given problem.
		The problem's type attribute must be 'issue'.
		
		@param problem: The problem to retrieve the corresponding issue for
		@type problem: A gmEMRStructItems.cProblem instance
		"""
		if problem['type'] != 'issue':
			_log.Log(gmLog.lErr, 'cannot convert non issue problem to issue: problem [%s] type [%s]' % (problem['problem'], problem['type']))
			return None
		return self.get_health_issues(id_list=[problem['pk_health_issue']])[0]
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
		try:
			self.__db_cache['vaccinations']['scheduled regimes']
		except KeyError:
			# retrieve vaccination regimes definitions
			self.__db_cache['vaccinations']['scheduled regimes'] = []
			cmd = """select distinct on(pk_regime) pk_regime
					 from v_vaccs_scheduled4pat
					 where pk_patient=%s"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot retrieve scheduled vaccination regimes')
				del self.__db_cache['vaccinations']['scheduled regimes']
				return None
			# Instantiate vaccination items and keep cache
			for row in rows:
				try:
					self.__db_cache['vaccinations']['scheduled regimes'].append(gmVaccination.cVaccinationRegime(aPK_obj=row[0]))
				except gmExceptions.ConstructorError:
					_log.LogException('vaccination regime error on [%s] for patient [%s]' % (row[0], self.pk_patient) , sys.exc_info(), verbose=0)

		# ok, let's constrain our list
		filtered_regimes = []
		filtered_regimes.extend(self.__db_cache['vaccinations']['scheduled regimes'])
		if ID is not None:
			filtered_regimes = filter(lambda regime: regime['pk_regime'] == ID, filtered_regimes)
			if len(filtered_regimes) == 0:
				_log.Log(gmLog.lErr, 'no vaccination regime [%s] found for patient [%s]' % (ID, self.pk_patient))
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
			_log.Log(gmLog.lErr, 'cannot load vaccinated indications for patient [%s]' % self.pk_patient)
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
			cmd= """select * from v_pat_vacc4ind
					where pk_patient=%s
 					order by indication, date"""
			rows, idx  = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load given vaccinations for patient [%s]' % self.pk_patient)
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
				try:
					vacc = gmVaccination.cVaccination(row=vacc_row)
					self.__db_cache['vaccinations']['vaccinated'].append(vacc)
				except gmExceptions.ConstructorError:
					_log.LogException('vaccination error on [%s] for patient [%s]' % (row, self.pk_patient), sys.exc_info(), verbose=0)
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
				_log.Log(gmLog.lErr, 'no vaccination [%s] found for patient [%s]' % (ID, self.pk_patient))
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
			cmd = """select * from v_vaccs_scheduled4pat where pk_patient=%s"""
			rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load scheduled vaccinations for patient [%s]' % self.pk_patient)
				del self.__db_cache['vaccinations']['scheduled']
				return None
			# Instantiate vaccination items
			for row in rows:
				vacc_row = {
					'pk_field': 'pk_vacc_def',
					'idx': idx,
					'data': row
				}
				try:
					self.__db_cache['vaccinations']['scheduled'].append(gmVaccination.cScheduledVaccination(row = vacc_row))
				except gmExceptions.ConstructorError:
					_log.LogException('vaccination error on [%s] for patient [%s]' % (row[0], self.pk_patient), sys.exc_info(), verbose=0)

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
			cmd = "select indication, seq_no from v_pat_missing_vaccs where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error loading (indication, seq_no) for due/overdue vaccinations for patient [%s]' % self.pk_patient)
				return None
			pk_args = {'pat_id': self.pk_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					pk_args['seq_no'] = row[1]
					try:
						self.__db_cache['vaccinations']['missing']['due'].append(gmVaccination.cMissingVaccination(aPK_obj=pk_args))
					except gmExceptions.ConstructorError:
						_log.LogException('vaccination error on [%s] for patient [%s]' % (row[0], self.pk_patient) , sys.exc_info(), verbose=0)
			# 2) boosters
			self.__db_cache['vaccinations']['missing']['boosters'] = []
			# get list of indications
			cmd = "select indication, seq_no from v_pat_missing_boosters where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error loading indications for missing boosters for patient [%s]' % self.pk_patient)
				return None
			pk_args = {'pat_id': self.pk_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					try:
						self.__db_cache['vaccinations']['missing']['boosters'].append(gmVaccination.cMissingBooster(aPK_obj=pk_args))
					except gmExceptions.ConstructorError:
						_log.LogException('booster error on [%s] for patient [%s]' % (row[0], self.pk_patient) , sys.exc_info(), verbose=0)
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
	def add_vaccination(self, vaccine=None):
		"""Creates a new vaccination entry in backend."""
		return gmVaccination.create_vaccination (
			patient_id = self.pk_patient,
			episode_id = self.__episode['pk_episode'],
			encounter_id = self.__encounter['pk_encounter'],
			staff_id = _whoami.get_staff_ID(),
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
		# 3) no encounter yet or too old, create new one
		successful, enc = gmEMRStructItems.create_encounter (
			fk_patient = self.pk_patient,
			fk_provider = _whoami.get_staff_ID()
		)
		if not successful:
			return False
		self.__encounter = enc
		return True
	#------------------------------------------------------------------
	def __activate_very_recent_encounter(self):
		"""Try to attach to a "very recent" encounter if there is one.

		returns:
			False: no "very recent" encounter, create new one
	    	True: success
		"""
		days, seconds = _encounter_soft_ttl.absvalues()
		sttl = '%s days %s seconds' % (days, seconds)
		cmd = """
			select pk_encounter
			from v_most_recent_encounters
			where
				pk_patient=%s
					and
				age(last_affirmed) < %s::interval
			"""
		enc_rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient, sttl)
		# error
		if enc_rows is None:
			_log.Log(gmLog.lErr, 'error accessing encounter tables')
			return False
		# none found
		if len(enc_rows) == 0:
			return False
		# attach to existing
		try:
			self.__encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		except gmExceptions.ConstructorError, msg:
			_log.LogException(str(msg), sys.exc_info(), verbose=0)
			return False
		self.__encounter.set_active(staff_id = _whoami.get_staff_ID())
		return True
	#------------------------------------------------------------------
	def __activate_fairly_recent_encounter(self):
		"""Try to attach to a "fairly recent" encounter if there is one.

		returns:
			False: no "fairly recent" encounter, create new one
	    	True: success
		"""
		# if we find one will we even be able to ask the user ?
		if _func_ask_user is None:
			return False
		days, seconds = _encounter_soft_ttl.absvalues()
		sttl = '%s days %s seconds' % (days, seconds)
		days, seconds = _encounter_hard_ttl.absvalues()
		httl = '%s days %s seconds' % (days, seconds)
		cmd = """
			select	pk_encounter
			from v_most_recent_encounters
			where
				pk_patient=%s
					and
				age(last_affirmed) between %s::interval and %s::interval
			"""
		enc_rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient, sttl, httl)
		# error
		if enc_rows is None:
			_log.Log(gmLog.lErr, 'error accessing encounter tables')
			return False
		# none found
		if len(enc_rows) == 0:
			return False
		try:
			encounter = gmEMRStructItems.cEncounter(aPK_obj=enc_rows[0][0])
		except gmExceptions.ConstructorError:
			return False
		# ask user whether to attach or not
		cmd = """
			select title, firstnames, lastnames, gender, dob
			from v_basic_person	where pk_identity=%s"""
		pat = gmPG.run_ro_query('personalia', cmd, None, self.pk_patient)
		if (pat is None) or (len(pat) == 0):
			_log.Log(gmLog.lErr, 'cannot access patient [%s]' % self.pk_patient)
			return False
		pat_str = '%s %s %s (%s), %s, #%s' % (
			pat[0][0][:5],
			pat[0][1][:12],
			pat[0][2][:12],
			pat[0][3],
			pat[0][4].Format('%Y-%m-%d'),
			self.pk_patient
		)
		msg = _(
			'A fairly recent encounter exists for patient:\n'
			' %s\n'
			'started    : %s\n'
			'affirmed   : %s\n'
			'type       : %s\n'
			'description: %s\n\n'
			'Do you want to reactivate this encounter ?\n'
			'Hitting "No" will start a new one.'
		) % (pat_str, encounter['started'], encounter['last_affirmed'], encounter['l10n_type'], encounter['description'])
		title = _('recording patient encounter')
		attach = False
		try:
			attach = _func_ask_user(msg, title)
		except:
			_log.LogException('cannot ask user for guidance', sys.exc_info(), verbose=0)
			return False
		if not attach:
			return False
		# attach to existing
		self.__encounter = encounter
		self.__encounter.set_active(staff_id = _whoami.get_staff_ID())
		return True
	#------------------------------------------------------------------
	def get_active_encounter(self):
		return self.__encounter
	#------------------------------------------------------------------
	def attach_to_encounter(self, anID = None):
#		"""Attach to an encounter but do not activate it.
#		"""
		# FIXME: this is the correct implementation but I
		# think the concept of attach_to_encounter is flawed,
		# eg we don't need it
#		if anID is None:
#			return False
#		encounter = gmEMRStructItems.cEncounter(aPK_obj= anID)
#		if encounter is None:
#			_log.Log(gmLog.lWarn, 'cannot instantiante encounter [%s]' % anID)
#			return False
#		if not encounter.set_attached_to(staff_id = _whoami.get_staff_ID()):
#		    _log.Log(gmLog.lWarn, 'cannot attach to encounter [%s]' % anID)
#		    return False
#		self.encounter = encounter
#		return True
		pass
	#--------------------------------------------------------
	def get_encounters(self, since=None, until=None, id_list=None, episodes=None, issues=None):
		"""
		Retrieves patient's encounters

		id_list - PKs of encounters to fetch
		since - initial date for encounter items, DateTime instance
		until - final date for encounter items, DateTime instance
		episodes - PKs of the episodes the encounters belong to (many-to-many relation)
		issues - PKs of the health issues the encounters belong to (many-to-many relation)
		"""
		try:
			self.__db_cache['encounters']
		except KeyError:
			# fetch all encounters for patient
			self.__db_cache['encounters'] = []
			cmd = "select id from clin_encounter where fk_patient=%s order by started"
			rows = gmPG.run_ro_query('historica', cmd, None, self.pk_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load encounters for patient [%s]' % self.pk_patient)
				del self.__db_cache['encounters']
				return None
			for row in rows:
				try:
					self.__db_cache['encounters'].append(gmEMRStructItems.cEncounter(aPK_obj=row[0]))
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)					
		# we've got the encounters, start filtering
		filtered_encounters = []
		filtered_encounters.extend(self.__db_cache['encounters'])
		if id_list is not None:
			filtered_encounters = filter(lambda enc: enc['pk_encounter'] in id_list, filtered_encounters)
		if since is not None:
			filtered_encounters = filter(lambda enc: enc['started'] >= since, filtered_encounters)
		if until is not None:
			filtered_encounters = filter(lambda enc: enc['last_affirmed'] <= until, filtered_encounters)
		if issues is not None and len(issues) > 0:
			if len(issues) == 1:		# work around pyPgSQL IN() bug with one-element-tuples
				issues.append(issues[0])
			cmd = """
select distinct pk_encounter
from v_pat_items
where pk_health_issue in %s and pk_patient = %s"""
			rows = gmPG.run_ro_query('historica', cmd, None, (tuple(issues), self.pk_patient))
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load encounters for issues [%s] (patient [%s])' % (str(issues), self.pk_patient))
			else:
				enc_ids = map(lambda x:x[0], rows)
				filtered_encounters = filter(lambda enc: enc['pk_encounter'] in enc_ids, filtered_encounters)
		if episodes is not None and len(episodes) > 0:
			if len(episodes) == 1:
				episodes.append(episodes[0])
			cmd = """
select distinct pk_encounter
from v_pat_items
where pk_episode in %s and pk_patient = %s"""
			rows = gmPG.run_ro_query('historica', cmd, None, (tuple(episodes), self.pk_patient))
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load encounters for episodes [%s] (patient [%s])' % (str(episodes), self.pk_patient))
			else:
				epi_ids = map(lambda x:x[0], rows)
				filtered_encounters = filter(lambda enc: enc['pk_encounter'] in epi_ids, filtered_encounters)

		return filtered_encounters
	#--------------------------------------------------------		
	def get_first_encounter(self, issue_id=None, episode_id=None):
		"""
			Retrieves first encounter for a particular issue and/or episode

			issue_id - First encounter associated health issue
			episode - First encounter associated episode
		"""
		h_iss = issue_id
		epis = episode_id
		if issue_id is not None:
			h_iss = [issue_id]
		if episode_id is not None:
			epis = [episode_id]
		encounters = self.get_encounters(issues=h_iss, episodes=epis)
		if encounters is None or len(encounters) == 0:
			_log.Log(gmLog.lErr, 'cannot retrieve first encounter for episodes [%s], issues [%s] (patient PK [%s])' % (str(epis), str(h_iss), self.pk_patient))
			return None
		# FIXME: this does not scale particularly well
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[0]
	#--------------------------------------------------------		
	def get_last_encounter(self, issue_id=None, episode_id=None):
		"""
			Retrieves last encounter for a concrete issue and/or episode
			
			issue_id - Last encounter associated health issue
			episode_id - Last encounter associated episode
		"""
		h_iss = issue_id
		epis = episode_id
		if issue_id is not None:
			h_iss = [issue_id]
		if episode_id is not None:
			epis = [episode_id]
		encounters = self.get_encounters(issues=h_iss, episodes=epis)
		if encounters is None or len(encounters) == 0:
			_log.Log(gmLog.lErr, 'cannot retrieve last encounter for episodes [%s], issues [%s]. Patient PK [%s]' % (str(epis), str(h_iss), self.pk_patient))
			return None
		# FIXME: this does not scale particularly well
		encounters.sort(lambda x,y: cmp(x['started'], y['started']))
		return encounters[-1]
	#------------------------------------------------------------------
	# lab data API
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

		cmd = """select * from v_results4lab_req where pk_patient=%%s %s""" % lim
		rows, idx = gmPG.run_ro_query('historica', cmd, True, self.pk_patient)
		if rows is None:
			return False
		for row in rows:
			lab_row = {
				'pk_field': 'pk_result',
				'idx': idx,
				'data': row
			}			
			try:
				lab_result = gmPathLab.cLabResult(row=lab_row)
				self.__db_cache['lab results'].append(lab_result)
			except gmExceptions.ConstructorError:
				_log.Log('lab result error', sys.exc_info())

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
		try:
			req = gmPathLab.cLabRequest(aPK_obj=pk, req_id=req_id, lab=lab)
		except gmExceptions.ConstructorError:
			_log.LogException('cannot get lab request', sys.exc_info())
			return None
		return req
	#------------------------------------------------------------------
	def add_lab_request(self, lab=None, req_id=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.__encounter['pk_encounter']
		if episode_id is None:
			episode_id = self.__episode['pk_episode']
		status, data = gmPathLab.create_lab_request(
			lab=lab,
			req_id=req_id,
			pat_id=self.pk_patient,
			encounter_id=encounter_id,
			episode_id=episode_id
		)
		if not status:
			_log.Log(gmLog.lErr, str(data))
			return None
		return data
	#------------------------------------------------------------------
	# unchecked stuff
	#------------------------------------------------------------------
        def store_referral (self, cursor, text, form_id):
		"""
		Stores a referral in the clinical narrative
		"""
		cmd = """
		insert into referral (
		fk_encounter, fk_episode, narrative, fk_form
		) values (
		%s, %s, %s, %s
		)
		"""
		return gmPG.run_commit (cursor, [(cmd, [self.__encounter['pk_encounter'], self.__episode['pk_episode'], text, form_id])])

#============================================================
# convenience functions
#------------------------------------------------------------
def set_encounter_ttl(soft = None, hard = None):
	if soft is not None:
		global _encounter_soft_ttl
		_encounter_soft_ttl = soft
	if hard is not None:
		global _encounter_hard_ttl
		_encounter_hard_ttl = hard
#------------------------------------------------------------
def set_func_ask_user(a_func = None):
	if a_func is not None:
		global _func_ask_user
		_func_ask_user = a_func
#------------------------------------------------------------
def get_item_types():
	cmd = "select pk, type, code from clin_item_type"
	data = gmPG.run_ro_query('historica', cmd)

#------------------------------------------------------------
# main
#------------------------------------------------------------
if __name__ == "__main__":
	import traceback
	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
	gmPG.set_default_client_encoding('latin1')
	try:
		emr = cClinicalRecord(aPKey = 12)

		# problems
		problems = emr.get_problems()
		print 'Problems:'
		for a_problem in problems:
			print '    -[problem:"%s"] [type:"%s"]' % (a_problem['problem'], a_problem['type'])
			if a_problem['type'] == 'episode':
				print '      .as episode: %s' % emr.problem2episode(a_problem)
		
		# Vacc regimes
		vacc_regimes = emr.get_scheduled_vaccination_regimes(indications = ['tetanus'])
		print '\nVaccination regimes: '
		for a_regime in vacc_regimes:
			pass
			#print a_regime
		vacc_regime = emr.get_scheduled_vaccination_regimes(ID=10)			
		#print vacc_regime
		
		# vaccination regimes and vaccinations for regimes
		scheduled_vaccs = emr.get_scheduled_vaccinations(indications = ['tetanus'])
		print 'Vaccinations for the regime:'
		for a_scheduled_vacc in scheduled_vaccs:
			pass
			#print '   %s' %(a_scheduled_vacc)

		# vaccination next shot and booster
		vaccinations = emr.get_vaccinations()
		for a_vacc in vaccinations:
			print '\nVaccination %s , date: %s, booster: %s, seq no: %s' %(a_vacc['batch_no'], a_vacc['date'].Format('%Y-%m-%d'), a_vacc['is_booster'], a_vacc['seq_no'])

		# first and last encounters
		first_encounter = emr.get_first_encounter(issue_id = 1)
		print '\nFirst encounter: ' + str(first_encounter)
		last_encounter = emr.get_last_encounter(episode_id = 1)
		print '\nLast encounter: ' + str(last_encounter)
		print ''
		
		# lab results
		lab = emr.get_lab_results()
		lab_file = open('lab-data.txt', 'wb')
		for lab_result in lab:
			lab_file.write(str(lab_result))
			lab_file.write('\n')
		lab_file.close()
		
		# soap notes
		narrative = emr.get_clin_narrative(
			since = mxDT.DateTime(2000, 2, 18),
			until = mxDT.DateTime(2010, 9, 18),
			issues = [1],
			episodes = [1],
			encounters = [1,2],
			soap_cats = ['s', 'p']
		)
		print '# of clinical notes:', str(len(narrative))
		for a_narr in narrative:
			print '%s - %s - %s - %s - %s - %s\n' % (
				a_narr['date'].Format('%Y-%m-%d'),
				str(a_narr['pk_health_issue']),
				str(a_narr['pk_episode']),
				str(a_narr['pk_encounter']),
				a_narr['soap_cat'],
				a_narr['narrative']
			)
			 
	#	dump = record.get_missing_vaccinations()
	#	f = open('vaccs.lst', 'wb')
	#	if dump is not None:
	#		print "=== due ==="
	#		f.write("=== due ===\n")
	#		for row in dump['due']:
	#			print row
	#			f.write(repr(row))
	#			f.write('\n')
	#		print "=== overdue ==="
	#		f.write("=== overdue ===\n")
	#		for row in dump['overdue']:
	#			print row
	#			f.write(repr(row))
	#			f.write('\n')
	#	f.close()
	except:
		traceback.print_exc(file=sys.stdout)
		_log.LogException('unhandled exception', sys.exc_info(), verbose=1)
	gmPG.ConnectionPool().StopListeners()
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.170  2005-04-03 09:26:48  ncq
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
