"""GnuMed preliminary clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.60 2004-01-18 21:41:49 ncq Exp $
__version__ = "$Revision: 1.60 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, string, time

if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG, gmSignals, gmDispatcher, gmWhoAmI
_whoami = gmWhoAmI.cWhoAmI()

import mx.DateTime as mxDT
#============================================================
class gmClinicalRecord:

	# handlers for __getitem__()
	_get_handler = {}

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self._backend = gmPG.ConnectionPool()

		self._ro_conn_clin = self._backend.GetConnection('historica')
		if self._ro_conn_clin is None:
			raise gmExceptions.ConstructorError, "cannot connect EMR of patient [%s] to service 'historica'" % aPKey

		self.id_patient = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		self.__db_cache = {}

		# make sure we have a xxxDEFAULTxxx health issue
		self.id_default_health_issue = None
		if not self.__load_default_health_issue():
			raise gmExceptions.ConstructorError, "cannot activate default health issue for patient [%s]" % aPKey
		self.id_health_issue = self.id_default_health_issue

		# what episode did we work on last time we saw this patient ?
		self.id_episode = None
		if not self.__load_last_active_episode():
			raise gmExceptions.ConstructorError, "cannot activate an episode for patient [%s]" % aPKey

		# load or create current encounter
		# FIXME: this should be configurable (for explanation see the method source)
		self.encounter_soft_ttl = '2 hours'
		self.encounter_hard_ttl = '5 hours'
		self.id_encounter = None

		# register backend notification interests
		# (keep this last so we won't hang on threads when
		#  failing this constructor for other reasons ...)
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "cannot register signal interests"

		_log.Log(gmLog.lData, 'Instantiated clinical record for patient [%s].' % self.id_patient)
	#--------------------------------------------------------
	def __del__(self):
		pass
	#--------------------------------------------------------
	def cleanup(self):
		_log.Log(gmLog.lData, 'cleaning up after clinical record for patient [%s]' % self.id_patient)
		sig = "%s:%s" % (gmSignals.item_change_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self._clin_item_modified)
		sig = "%s:%s" % (gmSignals.health_issue_change_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self._health_issues_modified)
		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self._vaccinations_modified)

		self._backend.Unlisten(service = 'historica', signal = gmSignals.allergy_add_del_db(), callback = self._allergy_added_deleted)

		self._backend.ReleaseConnection('historica')
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		# patient in demographic database ?
		cmd = "select exists(select id from identity where id = %s)"
		result = gmPG.run_ro_query('personalia', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in demographic database' % self.id_patient)
			return None
		if len(result) == 0:
			_log.Log(gmLog.lErr, "no patient [%s] in demographic database" % self.id_patient)
			return None
		# patient linked in our local clinical database ?
		cmd = "select exists(select pk from xlnk_identity where xfk_identity = %s)"
		result = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in clinical database' % self.id_patient)
			return None
		if len(result) == 0:
			_log.Log(gmLog.lInfo, "no patient [%s] in clinical database" % self.id_patient)
			cmd1 = "insert into xlnk_identity (xfk_identity, pupic) values (%s, %s)"
			cmd2 = "select currval('xlnk_identity_pk_seq')"
			status = gmPG.run_commit('historica', [
				(cmd1, [self.id_patient, self.id_patient]),
				(cmd2, [])
			])
			if status is None:
				_log.Log(gmLog.lErr, 'cannot insert patient [%s] into clinical database' % self.id_patient)
				return None
			if status != 1:
				_log.Log(gmLog.lData, 'inserted patient [%s] into clinical database with local id [%s]' % (self.id_patient, status[0][0]))
		return (1==1)
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		# backend
		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.id_patient)
		if not self._backend.Listen('historica', sig, self.db_cb_vaccinations_modified):
			return None
		if not self._backend.Listen(service = 'historica', signal = gmSignals.allergy_add_del_db(), callback = self._allergy_added_deleted):
			return None
		if not self._backend.Listen(service = 'historica', signal = gmSignals.health_issue_change_db(), callback = self._health_issues_modified):
			return None
		sig = "%s:%s" % (gmSignals.item_change_db(), self.id_patient)
		if not self._backend.Listen(service = 'historica', signal = sig, callback = self._clin_item_modified):
			return None
		return 1
	#--------------------------------------------------------
	def db_cb_vaccinations_modified(self, **kwds):
		try:
			del self.__db_cache['vaccinations']
		except KeyError:
			pass
		try:
			del self.__db_cache['idx vaccinations']
		except KeyError:
			pass
		try:
			del self.__db_cache['due vaccinations']
		except KeyError:
			pass

		gmDispatcher.send(signal = gmSignals.vaccinations_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _allergy_added_deleted(self):
		curs = self._ro_conn_clin.cursor()
		# did number of allergies change for our patient ?
		cmd = "select count(*) from v_i18n_patient_allergies where id_patient=%s"
		if not gmPG.run_query(curs, cmd, self.id_patient):
			curs.close()
			_log.Log(gmLog.lData, 'cannot check for added/deleted allergies, assuming addition/deletion did occurr')
			# error: invalidate cache
			del self.__db_cache['allergies']
			# and tell others
			gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
			return 1
		result = curs.fetchone()
		curs.close()
		# not cached yet
		try:
			nr_cached_allergies = len(self.__db_cache['allergies'])
		except KeyError:
			gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
			return 1
		# no change for our patient ...
		if result == nr_cached_allergies:
			return 1
		# else invalidate cache
		del self.__db_cache['allergies']
		gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _health_issues_modified(self):
		_log.Log(gmLog.lData, 'DB: clin_health_issue modification')
		try:
			del self.__db_cache['health issues']
		except KeyError:
			pass
		gmDispatcher.send(signal = gmSignals.health_issue_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _clin_item_modified(self):
		_log.Log(gmLog.lData, 'DB: clin_root_item modification')
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def add_clinical_note(self, note = None):
		if note is None:
			_log.Log(gmLog.lInfo, 'will not create empty clinical note')
			return 1
		cmd = "insert into clin_note(id_encounter, id_episode, narrative) values (%s, %s, %s)"
		return gmPG.run_commit('historica', [(cmd, [self.id_encounter, self.id_episode, note])])
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.
		"""
		try:
			return gmClinicalRecord._get_handler[aVar](self)
		except KeyError:
			_log.LogException('Missing get handler for [%s]' % aVar, sys.exc_info())
			return None
	#--------------------------------------------------------
	# FIXME: date range
	def get_text_dump(self):
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
		fields = [
			'age',
			"to_char(modified_when, 'YYYY-MM-DD @ HH24:MI') as modified_when",
			'modified_by',
			'clin_when',
			"case is_modified when false then '%s' else '%s' end as modified_string" % (_('original entry'), _('modified entry')),
			'id_item',
			'id_encounter',
			'id_episode',
			'id_health_issue',
			'src_table'
		]
		cmd = "select %s from v_patient_items where id_patient=%%s order by src_table, age" % string.join(fields, ', ')
		curs = self._ro_conn_clin.cursor()
		if not gmPG.run_query(curs, cmd, self.id_patient):
			_log.Log(gmLog.lErr, 'cannot load item links for patient [%s]' % self.id_patient)
			curs.close()
			return None
		rows = curs.fetchall()
		view_col_idx = gmPG.get_col_indices(curs)

		# aggregate by src_table for item retrieval
		items_by_table = {}
		for item in rows:
			src_table = item[view_col_idx['src_table']]
			id_item = item[view_col_idx['id_item']]
			if not items_by_table.has_key(src_table):
				items_by_table[src_table] = {}
			items_by_table[src_table][id_item] = item

		# get mapping for issue/episode IDs
		issue_map = self.get_health_issue_names()
		if issue_map is None:
			issue_map = {}
		episode_map = self.get_episodes()
		if episode_map is None:
			episode_map = {}
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
				if not gmPG.run_query(curs, cmd, item_ids[0]):
					_log.Log(gmLog.lErr, 'cannot load items from table [%s]' % src_table)
					# skip this table
					continue
			elif len(item_ids) > 1:
				cmd = "select * from %s where pk_item in %%s order by modified_when" % src_table
				if not gmPG.run_query(curs, cmd, (tuple(item_ids),)):
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
					episode_name = episode_map[view_row[view_col_idx['id_episode']]]
				except:
					episode_name = view_row[view_col_idx['id_episode']]
				try:
					issue_name = issue_map[view_row[view_col_idx['id_health_issue']]]
				except:
					issue_name = view_row[view_col_idx['id_health_issue']]

				if not emr_data.has_key(age):
					emr_data[age] = []

				emr_data[age].append(
					_('%s: encounter (%s)') % (
						view_row[view_col_idx['clin_when']],
						view_row[view_col_idx['id_encounter']]
					)
				)
				emr_data[age].append(_('health issue: %s') % issue_name)
				emr_data[age].append(_('episode     : %s') % episode_name)
				# format table specific data columns
				# - ignore those, they are metadata, some
				#   are in v_patient_items data already
				cols2ignore = [
					'pk_audit', 'row_version', 'modified_when', 'modified_by',
					'pk_item', 'id', 'id_encounter', 'id_episode'
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
		return emr_data
	#--------------------------------------------------------
	def get_patient_ID(self):
		return self.id_patient
	#--------------------------------------------------------
	# allergy methods
	#--------------------------------------------------------
	def get_allergies(self, remove_sensitivities = None):
		"""Return rows from v_i18n_patient_allergies."""
		try:
			self.__db_cache['allergies']
		except:
			self.__db_cache['allergies'] = []
			cmd = "select * from v_i18n_patient_allergies where id_patient=%s"
			rows, col_idx = gmPG.run_ro_query('historica', cmd, 1, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load allergies for patient [%s]' % self.id_patient)
				del self.__db_cache['allergies']
				return None
			self.__db_cache['allergies'] = rows
			self.__db_cache['idx allergies'] = col_idx

		data = []
		if remove_sensitivities:
			col_idx = self.__db_cache['idx allergies']
			for allergy in self.__db_cache['allergies']:
				if allergy[col_idx['id_type']] == 1:
					data.append(allergy)
		else:
			data = self.__db_cache['allergies']
		return data
	#--------------------------------------------------------
	def get_allergy_names(self, remove_sensitivities = None):
		data = []
		try:
			self.__db_cache['allergies']
		except KeyError:
			if self.get_allergies(remove_sensitivities) is None:
				# remember: empty list will return false
				# even though this is what we get with no allergies
				_log.Log(gmLog.lErr, "Cannot load allergies")
				return []
		idx = self.__db_cache['idx allergies']
		for allergy in self.__db_cache['allergies']:
			tmp = {}
			tmp['id'] = allergy[idx['id']]
			# do we know the allergene ?
			if allergy[idx['allergene']] not in [None, '']:
				tmp['name'] = allergy[idx['allergene']]
			# no but the substance
			else:
				tmp['name'] = allergy[idx['substance']]
			data.append(tmp)
		return data
	#--------------------------------------------------------
	def _get_allergies_list(self):
		"""Return list of IDs in v_i18n_patient_allergies for this patient."""
		try:
			return self.__db_cache['allergy IDs']
		except KeyError:
			pass
		self.__db_cache['allergy IDs'] = []
		curs = self._ro_conn_clin.cursor()
		cmd = "select id from v_i18n_patient_allergies where id_patient=%s"
		if not gmPG.run_query(curs, cmd, self.id_patient):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load list of allergies for patient [%s]' % self.id_patient)
			del self.__db_cache['allergy IDs']
			return None
		rows = curs.fetchall()
		curs.close()
		for row in rows:
			self.__db_cache['allergy IDs'].extend(row)
		return self.__db_cache['allergy IDs']
	#--------------------------------------------------------
	# episodes API
	#--------------------------------------------------------
	def get_episodes(self):
		try:
			return self.__db_cache['episodes']
		except KeyError:
			pass
		self.__db_cache['episodes'] = {}
		cmd = "select id_episode, episode from v_patient_episodes where id_patient=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load episodes for patient [%s]' % self.id_patient)
			del self.__db_cache['episodes']
			return None
		idx_id = 0
		idx_name = 1
		for row in rows:
			self.__db_cache['episodes'][row[idx_id]] = row[idx_name]
		return self.__db_cache['episodes']
	#------------------------------------------------------------------
	def set_active_episode(self, episode_name = None, episode_id = None):
		# 1) verify that episode exists
		# - either map id to name
		if episode_id is None:
			# if name not given assume default episode
			if episode_name is None:
				episode_name = 'xxxDEFAULTxxx'
			cmd = "select id_episode from v_patient_episodes where id_patient=%s and episode=%s limit 1"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, episode_name)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot check for episode [%s] existence' % episode_name)
				return None
			elif len(rows) == 0:
				_log.Log(gmLog.lErr, 'patient [%s] has no episode [%s]' % (self.id_patient, episode_name))
				return None
			else:
				episode_id = rows[0][0]
		# - or check if id exists
		else:
			cmd = "select exists(select episode from v_patient_episodes where id_patient=%s and id_episode=%s)"
			result = gmPG.run_ro_query('historica', cmd, None, self.id_patient, episode_id)
			if result is None:
				_log.Log(gmLog.lErr, 'cannot check for episode [%s] existence' % episode_id)
				return None
			if not result[0][0]:
				_log.Log(gmLog.lErr, 'patient [%s] has no episode [%s]' % (self.id_patient, episode_id))
				return None

		self.id_episode = episode_id

		# 2) load corresponding health issue
		cmd = "select id_health_issue from v_patient_episodes where id_episode=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_episode)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot find health issue linked from episode [%s] (%s), using default' % (episode_name, self.id_episode))
			id_health_issue = self.id_default_health_issue
		elif len(rows) == 0:
			_log.Log(gmLog.lErr, 'cannot find health issue linked from episode [%s] (%s), using default' % (episode_name, self.id_episode))
			id_health_issue = self.id_default_health_issue
		else:
			id_health_issue = rows[0][0]

		self.id_health_issue = id_health_issue

		# 3) try to record episode as most recently used one
		cmd1 = "delete from last_act_episode where id_patient=%s"
		cmd2 = "insert into last_act_episode(id_episode, id_patient) values (%s, %s)"
		result = gmPG.run_commit('historica', [
			(cmd1, [self.id_patient]),
			(cmd2, [self.id_episode, self.id_patient])
		])
		if result != 1:
			_log.Log(gmLog.lWarn, 'cannot record episode [%s] as most recently used for patient [%s]' % (self.id_episode, self.id_patient))

		return 1
	#------------------------------------------------------------------
	def add_episode(self, episode_name = 'xxxDEFAULTxxx', id_health_issue = None):
		"""Add episode 'episode_name'.

		- returns ID of episode
		- adds default episode if no name given
		"""
		# anything to do ?
		cmd = "select id_episode from v_patient_episodes where id_patient=%s and episode=%s limit 1"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, episode_name)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot check if episode [%s] exists for patient [%s]' % (episode_name, self.id_patient))
			return None
		# episode already exists
		if len(rows) != 0:
			return rows[0][0]

		# episode does not exist yet so create it
		# no health issue given -> use active health issue
		if id_health_issue is None:
			id_health_issue = self.id_health_issue
		cmd1 = "insert into clin_episode (id_health_issue, description) values (%s, %s)"
		cmd2 = "select currval('clin_episode_id_seq')"
		rows = gmPG.run_commit('historica', [
			(cmd1, [id_health_issue, episode_name]),
			(cmd2, [])
		])
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot insert episode [%s] for patient [%s]' % (episode_name, self.id_patient))
			return None
		if len(rows) == 0:
			_log.Log(gmLog.lErr, 'cannot obtain id of last episode insertion')
			return None
		return rows[0][0]
	#--------------------------------------------------------
	def __load_last_active_episode(self):
		# check if there's an active episode
		cmd = "select id_episode from last_act_episode where id_patient=%s limit 1"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		# error
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load last active episode for patient [%s]' % self.id_patient)
			return None
		# no last_active_episode recorded so far
		episode_name = 'xxxDEFAULTxxx'
		if len(rows) == 0:
			# find episode with the most recently modified clinical item
			# FIXME: optimize query
			cmd = """
				select description
				from clin_episode
				where id=(
					select distinct on(id_episode) id_episode
					from v_patient_items
					where
						id_patient=%s
							and
						modified_when=(select max(modified_when) where id_patient=%s)
				)"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, self.id_patient)
			# error
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot check for most recently used episode on patient [%s]' % self.id_patient)
				return None
			# no episode-connected clinical items recorded so far
			if len(rows) == 0:
				_log.Log(gmLog.lErr, 'no episodes in v_patient_items for patient [%s]' % self.id_patient)
			else:
				episode_name = rows[0][0]
			# try to activate episode
			if self.set_active_episode(episode_name):
				return 1
			_log.Log(gmLog.lErr, 'cannot activate episode [%s] for patient [%s]' % (episode_name, self.id_patient))
			return None
		# found last_active_episode
		self.id_episode = rows[0][0]

		# load corresponding health issue
		cmd = "select id_health_issue from v_patient_episodes where id_episode=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_episode)
		if rows is None:
			self.id_health_issue = self.id_default_health_issue
			_log.Log(gmLog.lErr, 'cannot find health issue linked from episode [%s], using default' % self.id_episode)
		elif len(rows) == 0:
			self.id_health_issue = self.id_default_health_issue
			_log.Log(gmLog.lErr, 'cannot find health issue linked from episode [%s], using default' % self.id_episode)
		else:
			self.id_health_issue = rows[0][0]

		return 1
	#--------------------------------------------------------
	# health issues API
	#--------------------------------------------------------
	def get_health_issues(self):
		try:
			return self.__db_cache['health issues']
		except KeyError:
			pass
		self.__db_cache['health issues'] = {}
		curs = self._ro_conn_clin.cursor()
		cmd = "select id, description from clin_health_issue where id_patient=%s"
		if not gmPG.run_query(curs, cmd, self.id_patient):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load health issues for patient [%s]' % self.id_patient)
			del self.__db_cache['health issues']
			return None
		rows = curs.fetchall()
		col_idx = gmPG.get_col_indices(curs)
		curs.close()
		idx_id = col_idx['id']
		idx_name = col_idx['description']
		for row in rows:
			self.__db_cache['health issues'][row[idx_id]] = row[idx_name]
		return self.__db_cache['health issues']
	#--------------------------------------------------------
	def get_health_issue_names(self):
		try:
			return self.__db_cache['health issue names']
		except KeyError:
			pass
		self.__db_cache['health issue names'] = {}
		curs = self._ro_conn_clin.cursor()
		cmd = "select id, description from clin_health_issue where id_patient=%s"
		if not gmPG.run_query(curs, cmd, self.id_patient):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load health issue names for patient [%s]' % self.id_patient)
			del self.__db_cache['health issue names']
			return None
		rows = curs.fetchall()
		col_idx = gmPG.get_col_indices(curs)
		curs.close()
		idx_id = col_idx['id']
		idx_name = col_idx['description']
		for row in rows:
			self.__db_cache['health issue names'][row[idx_id]] = row[idx_name]
		return self.__db_cache['health issue names']
	#------------------------------------------------------------------
	def __load_default_health_issue(self):
		self.id_default_health_issue = self.add_health_issue()
		if self.id_default_health_issue is None:
			_log.Log(gmLog.lErr, 'cannot load default health issue for patient [%s]' % self.id_patient)
			return None
		return 1
	#------------------------------------------------------------------
	def add_health_issue(self, health_issue_name = 'xxxDEFAULTxxx'):
		curs = self._ro_conn_clin.cursor()
		cmd = "select id from clin_health_issue where id_patient=%s and description=%s"
		if not gmPG.run_query(curs, cmd, self.id_patient, health_issue_name):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot check if health issue [%s] exists for patient [%s]' % (health_issue_name, self.id_patient))
			return None
		row = curs.fetchone()
		curs.close()
		# issue exists already
		if row is not None:
			return row[0]
		# issue does not exist yet so create it
		_log.Log(gmLog.lData, "health issue [%s] does not exist for patient [%s]" % (health_issue_name, self.id_patient))
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		rw_curs = rw_conn.cursor()
		cmd = "insert into clin_health_issue (id_patient, description) values (%s, %s)"
		if not gmPG.run_query(rw_curs, cmd, self.id_patient, health_issue_name):
			rw_curs.close()
			rw_conn.close()
			_log.Log(gmLog.lErr, 'cannot insert health issue [%s] for patient [%s]' % (health_issue_name, self.id_patient))
			return None
		# get ID of insertion
		cmd = "select currval('clin_health_issue_id_seq')"
		if not gmPG.run_query(rw_curs, cmd):
			rw_curs.close()
			rw_conn.close()
			_log.Log(gmLog.lErr, 'cannot obtain id of last health issue insertion')
			return None
		id_issue = rw_curs.fetchone()[0]
		# and commit our work
		rw_conn.commit()
		rw_curs.close()
		rw_conn.close()
		_log.Log(gmLog.lData, 'inserted [%s] issue with ID [%s] for patient [%s]' % (health_issue_name, id_issue, self.id_patient))
		
		return id_issue
	#--------------------------------------------------------
	# vaccinations API
	#--------------------------------------------------------
	def get_vaccinated_indications(self):
		cmd = """
			select distinct on (indication)
				indication,
				_(indication)
			from v_patient_vacc4ind
			where pk_patient=%s"""
		rows = gmPG.run_ro_query('historica', cmd, 0, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load vaccinated indications for patient [%s]' % self.id_patient)
			return None
		if len(rows) == 0:
			return [[_('no vaccinations recorded'), '']]
		return rows
	#--------------------------------------------------------
	def get_vaccinated_regimes(self):
		cmd = """
			select distinct on (regime)
				regime,
				_(indication)
			from v_patient_vaccinations
			where pk_patient = %s"""
		rows = gmPG.run_ro_query('historica', cmd, 0, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load vaccinations for patient [%s]' % self.id_patient)
			return None
		if len(rows) == 0:
			return [[_('no vaccinations recorded'), '']]
		return rows
	#--------------------------------------------------------
	def get_vaccinations(self, regime_list = None, ID = None, indication_list = None):
		try:
			self.__db_cache['vaccinations']
			self.__db_cache['idx vaccinations']
		except KeyError:
			self.__db_cache['vaccinations'] = []
#			cmd = """
#				select
#					pk_vaccination,
#					date,
#					vaccine,
#					vaccine_short,
#					batch_no,
#					regime,
#					indication,
#					is_booster,
#					seq_no,
#					site,
#					pk_provider,
#					narrative
#				from  v_patient_vaccinations
#				where pk_patient = %s"""
			cmd = """
				select
					pk_vaccination,
					pk_indication,
					date,
					indication,
					vaccine,
					vaccine_short,
					batch_no,
					site,
					narrative,
					pk_provider,
					pk_vaccine
				from  v_patient_vacc4ind
				where pk_patient = %s"""
			rows, self.__db_cache['idx vaccinations'] = gmPG.run_ro_query('historica', cmd, 1, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load vaccinations for patient [%s]' % self.id_patient)
				del self.__db_cache['vaccinations']
				return (None, None)
			self.__db_cache['vaccinations'] = rows
		# apply filters
		# 1) do we have an ID ?
		if ID is not None:
			for shot in self.__db_cache['vaccinations']:
				if shot[self.__db_cache['idx vaccinations']['pk_vaccination']] == ID:
					return shot, self.__db_cache['idx vaccinations']
			_log.Log(gmLog.lErr, 'no vaccination [%s] found for patient [%s]' % (ID, self.id_patient))
			return (None, None)
		filtered_shots = self.__db_cache['vaccinations']
		# 2) only certain regimes ?
#		if regime_list is not None and len(regime_list) != 0:
#			for shot in filtered_shots:
#				if shot[self.__db_cache['idx vaccinations']['regime']] not in regime_list:
#					filtered_shots.remove(shot)
		# 3) only certain indications ?
		if indication_list is not None and len(indication_list) != 0:
			for shot in filtered_shots:
				if shot[self.__db_cache['idx vaccinations']['indication']] not in indication_list:
					filtered_shots.remove(shot)
		# return what we got so far
		return (filtered_shots, self.__db_cache['idx vaccinations'])
	#--------------------------------------------------------
	def get_due_vaccinations(self):
		# FIXME: be smarter about boosters !
		try:
			return self.__db_cache['due vaccinations']
		except KeyError:
			pass
		self.__db_cache['due vaccinations'] = {}
		# due
		cmd = """
select
	pk_vacc_def,
	regime,
	seq_no,
	is_booster,
	latest_due,
	time_left,
	min_interval,
	comment
from v_pat_due_vaccs
where pk_patient = %s
order by time_left
"""
		rows = gmPG.run_ro_query('historica', cmd, 0, self.id_patient)
		if rows is None:
			return None
		self.__db_cache['due vaccinations']['due'] = []
		if len(rows) != 0:
			self.__db_cache['due vaccinations']['due'].extend(rows)

		# overdue
		cmd = """
select
	pk_vacc_def,
	regime,
	seq_no,
	is_booster,
	amount_overdue,
	min_interval,
	comment
from v_pat_overdue_vaccs
where pk_patient = %s
order by amount_overdue
"""
		rows = gmPG.run_ro_query('historica', cmd, 0, self.id_patient)
		if rows is None:
			return None

		self.__db_cache['due vaccinations']['overdue'] = []
		if len(rows) != 0:
			self.__db_cache['due vaccinations']['overdue'].extend(rows)

		return self.__db_cache['due vaccinations']
	#--------------------------------------------------------
	def add_vaccination(self, aVacc = None):
		if aVacc is None:
			_log.Log(gmLog.lErr, 'must have vaccination to save it')
			return (None, _('programming error'))

		# insert command
		cols = []
		val_snippets = []
		vals1 = {}

		cols.append('id_encounter')
		val_snippets.append('%(encounter)s')
		vals1['encounter'] = self.id_encounter

		cols.append('id_episode')
		val_snippets.append('%(episode)s')
		vals1['episode'] = self.id_episode

		cols.append('fk_patient')
		val_snippets.append('%(pat)s')
		vals1['pat'] = self.id_patient

		cols.append('fk_provider')
		val_snippets.append('%(doc)s')
		vals1['doc'] = _whoami.get_staff_ID()

		try:
			vals1['date'] = aVacc['date given']
			cols.append('clin_when')
			val_snippets.append('%(date)s')
		except KeyError:
			_log.LogException('missing date_given', sys.exc_info(), verbose=0)
			return (None, _('"date given" missing'))

		try:
			vals1['narrative'] = aVacc['progress note']
			cols.append('narrative')
			val_snippets.append('%(narrative)s')
		except KeyError:
			pass

		try:
			vals1['site'] = aVacc['site given']
			cols.append('site')
			val_snippets.append('%(site)s')
		except KeyError:
			pass

		try:
			vals1['batch'] = aVacc['batch no']
			cols.append('batch_no')
			val_snippets.append('%(batch)s')
		except KeyError:
			_log.LogException('missing batch #', sys.exc_info(), verbose=0)
			return (None, _('"batch #" missing'))

		try:
			vals1['vaccine'] = aVacc['vaccine']
			if aVacc['vaccine'] == '':
				raise KeyError
			cols.append('fk_vaccine')
			val_snippets.append('(select id from vaccine where trade_name=%(vaccine)s)')
		except KeyError:
			_log.LogException('missing vaccine name', sys.exc_info(), verbose=0)
			return (None, _('"vaccine name" missing'))

		cols_clause = string.join(cols, ',')
		vals_clause = string.join(val_snippets, ',')
		cmd1 = "insert into vaccination (%s) values (%s)" % (cols_clause, vals_clause)

		# return new ID cmd
		cmd2 = "select currval('vaccination_id_seq')"

		result, msg = gmPG.run_commit('historica', [
			(cmd1, [vals1]),
			(cmd2, [])
		], 1)
		if result is None:
			return (None, msg)
		return (1, result[0][0])
	#--------------------------------------------------------
	def update_vaccination(self, aVacc = None):
		if aVacc is None:
			_log.Log(gmLog.lErr, 'must have vaccination to update it')
			return (None, _('programming error'))

		set_snippets = []
		vals = {}
		# ID
		try:
			vals['id_vacc'] = aVacc['ID']
		except KeyError:
			_log.LogException('need to know ID to be able to update vaccination', sys.exc_info(), verbose=0)
			return (None, _('programming error'))
		# when given
		try:
			vals['date'] = aVacc['date given']
			set_snippets.append('clin_when=%(date)s')
		except KeyError:
			pass
		# narrative
		try:
			vals['narrative'] = aVacc['progress note']
			set_snippets.append('narrative=%(narrative)s')
		except KeyError:
			pass
		# vaccine
		try:
			if aVacc['vaccine'] == '':
				raise KeyError
			vals['vaccine'] = aVacc['vaccine']
			set_snippets.append('fk_vaccine=(select id from vaccine where trade_name=%(vaccine)s)')
		except KeyError:
			pass
		# site
		try:
			if aVacc['site given'] == '':
				raise KeyError
			vals['site'] = aVacc['site given']
			set_snippets.append('site=%(site)s')
		except KeyError:
			pass
		# batch no
		try:
			if aVacc['batch no'] == '':
				raise KeyError
			vals['batchno'] = aVacc['batch no']
			set_snippets.append('batch_no=%(batchno)s')
		except KeyError:
			pass

		set_clause = ', '.join(set_snippets)
		where_clause = 'where id=%(id_vacc)s'
		cmd = 'update vaccination set %s %s' % (set_clause, where_clause)
		result, msg = gmPG.run_commit('historica', [
			(cmd, [vals])
		], 1)
		if result is None:
			return (None, msg)
		return (1, '')
	#--------------------------------------------------------
	# set up handler map
	_get_handler['health issues'] = get_health_issues
	_get_handler['health issue names'] = get_health_issue_names
	#------------------------------------------------------------------
	# encounter API
	#------------------------------------------------------------------
	def attach_to_encounter(self, anID = None, forced = None, comment = 'affirmed'):
		"""Try to attach to an encounter.
		"""
		self.id_encounter = None

		# if forced to ...
		if forced:
			# ... create a new encounter and attach to that
			if anID is None:
				self.id_encounter = self.__add_encounter()
				if self.id_encounter is None:
					return -1, ''
				else:
					return 1, ''
			# ... attach to a particular encounter
			else:
				self.id_encounter = anID
				if not self.__affirm_current_encounter(comment):
					return -1, ''
				else:
					return 1, ''

		# else auto-search for encounter and attach if necessary
		if anID is None:
			# 1) very recent encounter recorded ? (that we always consider current)
			cmd = """
				select pk_encounter
				from v_i18n_curr_encounters
				where
					pk_patient=%s
						and
					now() - last_affirmed < %s::interval
				"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, self.encounter_soft_ttl)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot access current encounter table')
				return -1, ''
			# yes, so update and return that
			if len(rows) != 0:
				self.id_encounter = rows[0][0]
				if not self.__affirm_current_encounter(comment):
					return -1, ''
				else:
					return 1, ''

			# 2) encounter recorded that's fairly recent ?
			cmd = """
				select
					pk_encounter,
					started,
					last_affirmed,
					status,
					description,
					type
				from v_i18n_curr_encounters
				where
					pk_patient=%s
						and
					now() - last_affirmed < %s::interval
				limit 1"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, self.encounter_hard_ttl)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot access current encounter table')
				return -1, ''
			# ask user what to do about it
			if len(rows) != 0:
				data = {
					'ID': rows[0][0],
					'started': rows[0][1],
					'affirmed': rows[0][2],
					'status': rows[0][3],
					'comment': rows[0][4],
					'type': rows[0][5]
				}
				return 0, data

			# 3) no encounter active or encounter timed out, create new one
			self.id_encounter = self.__add_encounter()
			if self.id_encounter is None:
				return -1, ''
			else:
				return 1, ''
		else:
			_log.Log(gmLog.lErr, 'invalid argument combination: forced=false & anID given (= %d)' % anID)
			return -1, ''
	#------------------------------------------------------------------
	def __add_encounter(self, aComment = 'created', encounter_name = None):
		"""Insert a new encounter.
		"""
		# delete old entries if any
		cmd1 = "delete from curr_encounter where id_encounter in (select id from clin_encounter where fk_patient=%s)"
		# insert new encounter
		# FIXME: we don't deal with location yet
		if encounter_name is None:
			encounter_name = 'auto-created %s' % mxDT.today().Format('%A %Y-%m-%d %H:%M')
		cmd2 = "insert into clin_encounter(fk_patient, fk_location, fk_provider, description) values(%s, -1, %s, %s)"
		# and record as currently active encounter
		cmd3 = "insert into curr_encounter (id_encounter, \"comment\") values (currval('clin_encounter_id_seq'), %s)"

		return gmPG.run_commit('historica', [
			(cmd1, [self.id_patient]),
			(cmd2, [self.id_patient, _whoami.get_staff_ID(), encounter_name]),
			(cmd3, [aComment])
		])
	#------------------------------------------------------------------
	def __affirm_current_encounter(self, aComment = 'affirmed'):
		"""Update internal comment and time stamp on curr_encounter row.
		"""
		cmd = "update curr_encounter set comment=%s where id_encounter=%s"
		if not gmPG.run_commit('historica', [(cmd, [aComment, self.id_encounter])]):
			_log.Log(gmLog.lErr, 'cannot reaffirm encounter')
			return None
		return 1
	#------------------------------------------------------------------
	# trial: allergy panel
	#------------------------------------------------------------------
	def create_allergy(self, map):
		"""tries to add allergy to database."""
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		if rw_conn is None:
			_log.Log(gmLog.lErr, 'cannot connect to service [historica]')
			return None
		rw_curs = rw_conn.cursor()
		# FIXME: id_type hardcoded, not reading checkbox states (allergy or sensitivity)
		cmd = """
insert into allergy (
	id_type, id_encounter, id_episode,  substance, reaction, definite
) values (
	%s, %s, %s, %s, %s, %s
)
"""
		gmPG.run_query (rw_curs, cmd, 1, self.id_encounter, self.id_episode, map["substance"], map["reaction"], map["definite"])
		rw_curs.close()
		rw_conn.commit()
		rw_conn.close()

		return 1
	#------------------------------------------------------------------
	def get_past_history(self):
		if not self.__dict__.has_key('past_history'):
			from gmPastHistory import gmPastHistory
			from gmEditAreaFacade import gmPHxEditAreaDecorator
			phx  = gmPastHistory(self._backend, self)
			self.past_history = gmPHxEditAreaDecorator(phx)
		return self.past_history
#============================================================
class gmClinicalPart:
	def __init__(self, backend, patient):
		self._backend = backend
		self.patient = patient
		
	def id_patient(self):
		return self.patient.id_patient

	def id_encounter(self):
		return self.patient.id_encounter

	def id_episode(self):
		return self.patient.id_episode


        def escape_str_quote(self, s):
               if type(s) == type(""):
			s = s.replace("'", "\\\'" )
               return s


	def _print(self, *kargs):
		return

	def validate_not_null( self, values, fields):
		for f in fields:
			if values.has_key(f):
				assert  type(values[f]) == type('')
				assert  values[f].strip() <> ''

	def to_keyed_map(self, list_with_id , fields):
		all_map = {}
		for row in list_with_id:
			map = {}
			for i in xrange(0, len(fields)):
				try:
					map[fields[i]] = row[i+1]
				except:
					pass
			all_map[row[0]]= map	

		return all_map
#============================================================
# convenience functions
#------------------------------------------------------------
def get_vacc_regimes():
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

#------------------------------------------------------------
# main
#------------------------------------------------------------
if __name__ == "__main__":
	_ = lambda x:x
	gmPG.set_default_client_encoding('latin1')
	record = gmClinicalRecord(aPKey = 11)
#	dump = record.get_text_dump()
#	if dump is not None:
#		keys = dump.keys()
#		keys.sort()
#		for aged_line in keys:
#			for line in dump[aged_line]:
#				print line
#	dump = record.get_due_vaccinations()
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
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.60  2004-01-18 21:41:49  ncq
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
