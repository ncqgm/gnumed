"""GnuMed preliminary clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

Make sure to call set_func_ask_user() and set_encounter_ttl()
early on in your code (before cClinicalRecord.__init__() is
called for the first time).
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.106 2004-05-30 19:54:57 ncq Exp $
__version__ = "$Revision: 1.106 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# standard libs
import sys, string, time, copy

from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmWhoAmI
if __name__ == "__main__":
	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmPathLab, gmAllergy, gmVaccination, gmEMRStructItems

# 3rd party
import mx.DateTime as mxDT

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
		self._backend = gmPG.ConnectionPool()

		self._ro_conn_clin = self._backend.GetConnection('historica')
		if self._ro_conn_clin is None:
			raise gmExceptions.ConstructorError, "cannot connect EMR of patient [%s] to service 'historica'" % aPKey

		self.id_patient = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		self.__db_cache = {}

		# make sure we have a xxxDEFAULTxxx health issue
		if not self.__load_default_health_issue():
			raise gmExceptions.ConstructorError, "cannot activate default health issue for patient [%s]" % aPKey
		self.health_issue = self.default_health_issue

		# what episode did we work on last time we saw this patient ?
		# also load corresponding health issue
		if not self.__load_last_active_episode():
			raise gmExceptions.ConstructorError, "cannot activate an episode for patient [%s]" % aPKey

		# load current or create new encounter
		# FIXME: this should be configurable (for explanation see the method source)
		if not self.__initiate_active_encounter():
			raise gmExceptions.ConstructorError, "cannot activate an encounter for patient [%s]" % aPKey

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
		sig = "%s:%s" % (gmSignals.health_issue_change_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self._health_issues_modified)
		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self.db_callback_vaccs_modified)
		sig = "%s:%s" % (gmSignals.allg_mod_db(), self.id_patient)
		self._backend.Unlisten(service = 'historica', signal = sig, callback = self._db_callback_allg_modified)

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
		exists = result[0][0]
		if not exists:
			_log.Log(gmLog.lErr, "patient [%s] not in demographic database" % self.id_patient)
			return None
		# patient linked in our local clinical database ?
		cmd = "select exists(select pk from xlnk_identity where xfk_identity = %s)"
		result = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if result is None:
			_log.Log(gmLog.lErr, 'unable to check for patient [%s] existence in clinical database' % self.id_patient)
			return None
		exists = result[0][0]
		if not exists:
			_log.Log(gmLog.lInfo, "patient [%s] not in clinical database" % self.id_patient)
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
		return True
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		# backend
		sig = "%s:%s" % (gmSignals.vacc_mod_db(), self.id_patient)
		if not self._backend.Listen('historica', sig, self.db_callback_vaccs_modified):
			return None
		sig = "%s:%s" % (gmSignals.allg_mod_db(), self.id_patient)
		if not self._backend.Listen(service = 'historica', signal = sig, callback = self._db_callback_allg_modified):
			return None
		sig = "%s:%s" % (gmSignals.health_issue_change_db(), self.id_patient)
		if not self._backend.Listen(service = 'historica', signal = sig, callback = self._health_issues_modified):
			return None
		return 1
	#--------------------------------------------------------
	def db_callback_vaccs_modified(self, **kwds):
		try:
			del self.__db_cache['vaccinations']
		except KeyError:
			pass
		try:
			del self.__db_cache['missing vaccinations']
		except KeyError:
			pass
		# frontend notify
		gmDispatcher.send(signal = gmSignals.vaccinations_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
	def _db_callback_allg_modified(self):
		curs = self._ro_conn_clin.cursor()
		# did number of allergies change for our patient ?
		cmd = "select count(*) from v_pat_allergies where id_patient=%s"
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
		return gmPG.run_commit('historica', [(cmd, [self.__encounter['id'], self.__episode['id'], note])])
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
		issues = self.get_health_issues()
		issue_map = {}
		for issue in issues:
			issue_map[issue['id']] = issue['description']
		episodes = self.get_episodes()
		episode_map = {}
		for episode in episodes:
			episode_map[episode['id_episode']] = episode['episode']
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
			'id_item',
			'id_encounter',
			'id_episode',
			'id_health_issue',
			'src_table'
		]
		select_from = "select %s from v_patient_items" % ', '.join(fields)
		# handle constraint conditions
		where_snippets = []
		params = {}
		where_snippets.append('id_patient=%(pat_id)s')
		params['pat_id'] = self.id_patient
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
				where_snippets.append('id_encounter in %(enc)s')
			else:
				where_snippets.append('id_encounter=%(enc)s')
		# episodes
		if not episodes is None and len(episodes) > 0:
			params['epi'] = episodes
			if len(episodes) > 1:
				where_snippets.append('id_episode in %(epi)s')
			else:
				where_snippets.append('id_episode=%(epi)s')
		# health issues
		if not issues is None and len(issues) > 0:
			params['issue'] = issues
			if len(issues) > 1:
				where_snippets.append('id_health_issue in %(issue)s')
			else:
				where_snippets.append('id_health_issue=%(issue)s')

		where_clause = ' and '.join(where_snippets)
		order_by = 'order by src_table, age'
		cmd = "%s where %s %s" % (select_from, where_clause, order_by)

#		print "QUERY: " + cmd
		rows, view_col_idx = gmPG.run_ro_query('historica', cmd, 1, params)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load item links for patient [%s]' % self.id_patient)
			return None

		# -- sort the data --
		# FIXME: by issue/encounter/episode, eg formatting
		# aggregate by src_table for item retrieval
		items_by_table = {}
		for item in rows:
			src_table = item[view_col_idx['src_table']]
			id_item = item[view_col_idx['id_item']]
			if not items_by_table.has_key(src_table):
				items_by_table[src_table] = {}
			items_by_table[src_table][id_item] = item

		# get mapping for issue/episode IDs
		issues = self.get_health_issues()
		issue_map = {}
		for issue in issues:
			issue_map[issue['id']] = issue['description']
		episodes = self.get_episodes()
		episode_map = {}
		for episode in episodes:
			episode_map[episode['id_episode']] = episode['episode']
		emr_data = {}
		# get item data from all source tables
		curs = self._ro_conn_clin.cursor()
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
	# allergy API
	#--------------------------------------------------------
 	def get_allergies(self, remove_sensitivities = None):
		"""Retrieves patient allergy items"""
 		try:
 			self.__db_cache['allergies']
 		except KeyError:
			# FIXME: date range, episode, encounter, issue, test filter
 			self.__db_cache['allergies'] = []
			cmd = "select id from v_pat_allergies where id_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load allergies for patient [%s]' % self.id_patient)
				del self.__db_cache['allergies']
				return None
			# Instantiate allergy items and keep cache
			for row in rows:
				try:
					self.__db_cache['allergies'].append(gmAllergy.cAllergy(aPK_obj=row[0]))
				except gmExceptions.ConstructorError:
					_log.LogException('allergy error on [%s] for patient [%s]' % (row[0], self.id_patient) , sys.exc_info(), verbose=0)
					_log.Log(gmLog.lInfo, 'better to report an error than rely on incomplete allergy information')
					del self.__db_cache['allergies']
					return None
		# constrain by type (sensitivity/allergy)
 		if remove_sensitivities:
			tmp = []
 			for allergy in self.__db_cache['allergies']:
				if allergy['type'] != 'sensitivity':
					tmp.append(allergy)
			return tmp
		return self.__db_cache['allergies']
	#--------------------------------------------------------
	def add_allergy(self, substance=None, allg_type=None, encounter_id=None, episode_id=None):
		if encounter_id is None:
			encounter_id = self.__encounter['id']
		if episode_id is None:
			episode_id = self.__episode['id']
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
	def set_allergenic_state(self, status=None):
		pass
	#--------------------------------------------------------
	# episodes API
	#--------------------------------------------------------
	def get_active_episode(self):
		return self.__episode
	#--------------------------------------------------------
	def get_episodes(self, id_list=None):
		"""Fetches from backend patient episodes.
		"""
		try:
			self.__db_cache['episodes']
		except KeyError:
			self.__db_cache['episodes'] = []
			cmd = "select id_episode from v_pat_episodes where id_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load episodes for patient [%s]' % self.id_patient)
				del self.__db_cache['episodes']
				return None
			for row in rows:
				try:
					self.__db_cache['episodes'].append(gmEMRStructItems.cEpisode(aPK_obj=row[0]))
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)

		if id_list is None:
			return self.__db_cache['episodes']
		filtered_episodes = []
		for episode in self.__db_cache['episodes']:
			if episode['id'] in id_list:
				filtered_episodes.append(episode)
		return filtered_episodes
	#------------------------------------------------------------------
	def add_episode(self, episode_name = 'xxxDEFAULTxxx', id_health_issue = None):
		"""Add episode 'episode_name' for a patient's health issue.

		- id_health_issue - given health issue PK
		- episode_name - episode name

		- adds default episode if no name given
		- silently returns if episode already exists
		"""
		try:
			self.__db_cache['episodes']
		except KeyError:
			self.get_episodes()
		if id_health_issue is None:
			id_health_issue = self.health_issue['ID']
		# already there ?
		for episode in self.__db_cache['episodes']:
			if episode['episode'] == episode_name:
				if episode['id_health_issue'] == id_health_issue:
					return episode
				else:
					_log.Log(gmLog.lErr, 'episode [%s] already exists for patient [%s]' % (episode_name, self.id_patient))
					_log.Log(gmLog.lErr, 'cannot change health issue link from [%s] to [%s]' % (episode['id_health_issue'], id_health_issue))
					return None
		# no, try to create it
		success, episode = gmEMRStructItems.create_episode(id_patient=self.id_patient, id_health_issue=id_health_issue, episode_name=episode_name)
		if not success:
			_log.Log(gmLog.lErr, 'cannot create episode [%s] for patient [%s] and health issue [%s]' % (episode_name, self.id_patient, id_health_issue))
			return None
		return episode
	#--------------------------------------------------------
	def __load_last_active_episode(self):
		# check if there's an active episode
		cmd = "select id_episode from last_act_episode where id_patient=%s limit 1"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if rows is None:
			_log.Log(gmLog.lErr, 'cannot load last active episode for patient [%s]' % self.id_patient)
			return None
		episode = None
		if len(rows) != 0:
			try:
				episode = gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])
			except gmExceptions.ConstructorError, msg:
				_log.Log(str(msg), sys.exc_info(), verbose=0)

		# no last_active_episode recorded, so try to find the
		# episode with the most recently modified clinical item
		if episode is None:
			cmd = """
				select id
				from clin_episode
				where id=(
					select distinct on(id_episode) id_episode
					from v_patient_items
					where
						id_patient=%s
							and
						modified_when=(select max(vpi.modified_when) from v_patient_items vpi where vpi.id_patient=%s))"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error getting most recent episode from v_patient_items for patient [%s]' % self.id_patient)
			else:
				if len(rows) != 0:
					try:
						episode = gmEMRStructItems.cEpisode(aPK_obj=rows[0][0])
						episode.set_active()
					except gmExceptions.ConstructorError, msg:
						_log.Log(str(msg), sys.exc_info(), verbose=0)
						episode = None

		# no clinical items recorded, so try to find
		# the youngest episode for this patient
		if episode is None:
			cmd = """
				select cle.id
				from clin_episode cle, clin_health_issue chi
				where
					chi.id_patient = %s
						and
					chi.id = cle.id_health_issue
						and
					cle.modified_when = (
						select max(cle1.modified_when) from clin_episode cle1 where cle1.id=cle.id
					)"""
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error getting most recently touched episode on patient [%s]' % self.id_patient)
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
			episode = gmEMRStructItem.create_episode(health_issue_id=self.health_issue['id'])
			if episode is None:
				_log.Log(gmLog.lErr, 'cannot even activate default episode for patient [%s], aborting' %  self.id_patient)
				return False
			episode.set_active()

		self.__episode = episode
		# load corresponding health issue
		self.health_issue = self.get_health_issues(id_list=[self.__episode['id_health_issue']])
		if self.health_issue is None:
			_log.Log(gmLog.lErr, 'cannot activate health issue linked from episode [%s], using default' % str(self.__episode))
			self.health_issue = self.default_health_issue

		return True
	#--------------------------------------------------------
	def set_active_episode(self, ep_name='xxxDEFAULTxxx'):
		if self.get_episodes() is None:
			_log.Log(gmLog.lErr, 'cannot activate episode [%s], cannot get episode list' % ep_name)
			return False
		for episode in self.__db_cache['episodes']:
			if episode['episode'] == ep_name:
				episode.set_active()
				return True
		_log.Log(gmLog.lErr, 'cannot activate episode [%s], not found in list' % ep_name)
		return False
	#--------------------------------------------------------
	# health issues API
	#--------------------------------------------------------
	def get_health_issues(self, id_list = None):
		try:
			self.__db_cache['health issues']
		except KeyError:
			self.__db_cache['health issues'] = []
			cmd = "select id from clin_health_issue where id_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load health issues for patient [%s]' % self.id_patient)
				del self.__db_cache['health issues']
				return None
			for row in rows:
				try:
					self.__db_cache['health issues'].append(gmEMRStructItems.cHealthIssue(aPK_obj=row[0]))
				except gmExceptions.ConstructorError, msg:
					_log.LogException(str(msg), sys.exc_info(), verbose=0)
		if id_list is None:
			return self.__db_cache['health issues']
		filtered_issues = []
		for issue in self.__db_cache['health issues']:
			if issue['id'] in id_list:
				filtered_issues.append(issue)
		return filtered_issues
	#--------------------------------------------------------
	def __load_default_health_issue(self):
		success, self.default_health_issue = gmEMRStructItems.create_health_issue(patient_id=self.id_patient)
		if not success:
			_log.Log(gmLog.lErr, 'cannot load default health issue for patient [%s]' % self.id_patient)
			return None
		return True
	#------------------------------------------------------------------
	def add_health_issue(self, health_issue_name = 'xxxDEFAULTxxx'):
		"""Adds patient health issue.

		- silently returns if it already exists
		"""
		try:
			self.__db_cache['health issues']
		except KeyError:
			self.get_health_issues()
		# already there ?
		for issue in self.__db_cache['health issues']:
			if issue['description'] == health_issue_name:
				return issue
		# no, try to create it
		success, issue = gmEMRStructItems.create_health_issue(patient_id=self.id_patient, description=health_issue_name)
		if not success:
			_log.Log(gmLog.lErr, 'cannot create health issue [%s] for patient [%s]' % (health_issue_name, self.id_patient))
			return None
		return issue
	#--------------------------------------------------------
	# vaccinations API
	#--------------------------------------------------------
	def get_vaccinated_indications(self):
		"""Retrieves patient vaccinated indications list.
		"""
		# most likely, vaccinations will be fetched close
		# by so it makes sense to count on the cache being
		# filled (or fill it for nearby use)
		vaccinations = self.get_vaccinations()
		if vaccinations is None:
			_log.Log(gmLog.lErr, 'cannot load vaccinated indications for patient [%s]' % self.id_patient)
			return (None, [[_('ERROR: cannot retrieve vaccinated indications'), _('ERROR: cannot retrieve vaccinated indications')]])
		if len(vaccinations) == 0:
			return (1, [[_('no vaccinations recorded'), _('no vaccinations recorded')]])
		v_indications = []
		for vacc in vaccinations:
			v_indications.append([vacc['indication'], vacc['l10n_indication']])
		return (1, v_indications)
	#--------------------------------------------------------
	def get_vaccinated_regimes(self):
		"""Retrieves regimes for which patient has received any vaccinations.
		"""
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
	def get_vaccinations(self, ID = None, indication_list = None):
		"""Retrieves list of vaccinations the patient has received.

		optional:
		* ID - PK of the vaccinated indication
		* indication_list - indications we want to retrieve vaccination
			items for, must be primary language, not l10n_indication
		"""
		try:
			self.__db_cache['vaccinations']
		except KeyError:
			self.__db_cache['vaccinations'] = []
			# get list of IDs
			# FIXME: date range, episode, encounter, issue, test filter
			cmd = "select id from vaccination where fk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'cannot load vaccinations for patient [%s]' % self.id_patient)
				del self.__db_cache['vaccinations']
				return None
			# Instantiate vaccination items and keep cache
			for row in rows:
				try:
					self.__db_cache['vaccinations'].append(gmVaccination.cVaccination(aPK_obj=row[0]))
				except gmExceptions.ConstructorError:
					_log.LogException('vaccination error on [%s] for patient [%s]' % (row[0], self.id_patient) , sys.exc_info(), verbose=0)
		# apply filters
		# 1) do we have an ID ?
		if ID is not None:
			for shot in self.__db_cache['vaccinations']:
				if shot['pk_vaccination'] == ID:
					return shot
			_log.Log(gmLog.lErr, 'no vaccination [%s] found for patient [%s]' % (ID, self.id_patient))
			return None
		# 2) only certain indications ?
		filtered_shots = []
		if indication_list is not None:
			if len(indication_list) != 0:
				for shot in self.__db_cache['vaccinations']:
					if shot['indication'] in indication_list:
						filtered_shots.append(shot)	
				return (filtered_shots)
		return (self.__db_cache['vaccinations'])
	#--------------------------------------------------------
	def get_missing_vaccinations(self, indication_list = None):
		try:
			self.__db_cache['missing vaccinations']
		except KeyError:
			self.__db_cache['missing vaccinations'] = {}
			# 1) non-booster
			self.__db_cache['missing vaccinations']['due'] = []
			# get list of (indication, seq_no) tuples
			cmd = "select indication, seq_no from v_pat_missing_vaccs where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error loading (indication, seq_no) for due/overdue vaccinations for patient [%s]' % self.id_patient)
				return None
			pk_args = {'pat_id': self.id_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					pk_args['seq_no'] = row[1]
					try:
						self.__db_cache['missing vaccinations']['due'].append(gmVaccination.cMissingVaccination(aPK_obj=pk_args))
					except gmExceptions.ConstructorError:
						_log.LogException('vaccination error on [%s] for patient [%s]' % (row[0], self.id_patient) , sys.exc_info(), verbose=0)
			# 2) boosters
			self.__db_cache['missing vaccinations']['boosters'] = []
			# get list of indications
			cmd = "select indication, seq_no from v_pat_missing_boosters where pk_patient=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
			if rows is None:
				_log.Log(gmLog.lErr, 'error loading indications for missing boosters for patient [%s]' % self.id_patient)
				return None
			pk_args = {'pat_id': self.id_patient}
			if rows is not None:
				for row in rows:
					pk_args['indication'] = row[0]
					try:
						self.__db_cache['missing vaccinations']['boosters'].append(gmVaccination.cMissingBooster(aPK_obj=pk_args))
					except gmExceptions.ConstructorError:
						_log.LogException('booster error on [%s] for patient [%s]' % (row[0], self.id_patient) , sys.exc_info(), verbose=0)
		# if any filters ...
		if indication_list is None:
			return self.__db_cache['missing vaccinations']
		if len(indication_list) == 0:
			return self.__db_cache['missing vaccinations']
		# ... apply them
		filtered_shots = {
			'due': [],
			'boosters': []
		}
		for due_shot in self.__db_cache['missing vaccinations']['due']:
			if due_shot['indication'] in indication_list: #and due_shot not in filtered_shots['due']:
				filtered_shots['due'].append(due_shot)
		for due_shot in self.__db_cache['missing vaccinations']['boosters']:
			if due_shot['indication'] in indication_list: #and due_shot not in filtered_shots['boosters']:
				filtered_shots['boosters'].append(due_shot)
		return filtered_shots
	#--------------------------------------------------------
	# Carlos: putting this into gmClinicalRecord only makes sense
	# if it operates on the vaccinations tied to a patient, hence
	# I will let this operate on self.__db_cache['missing vaccinations'],
	# if you want a generic method make it module-level, or better
	# yet put it into gmVaccination.py
	def get_indications_from_vaccinations(self, vaccinations=None):
		"""Retrieves vaccination bundle indications list.

		* vaccinations = list of any type of vaccination
			- indicated
			- due vacc
			- overdue vaccs
			- due boosters
			- arbitrary
		"""
		if vaccinations is None:
			_log.Log(gmLog.lErr, 'list of vaccinations must be supplied')
			return (None, [['ERROR: list of vaccinations not supplied', _('ERROR: list of vaccinations not supplied')]])
		if len(vaccinations) == 0:
			return (1, [['empty list of vaccinations', _('empty list of vaccinations')]])
		inds = []
		for vacc in vaccinations:
			try:
				inds.append([vacc['indication'], vacc['l10n_indication']])
			except KeyError:
				try:
					inds.append([vacc['indication'], vacc['indication']])
				except KeyError:
					inds.append(['vacc -> ind error: %s' % str(vacc), _('vacc -> ind error: %s') % str(vacc)])
		return (1, inds)
	#--------------------------------------------------------
	def add_vaccination(self, vaccine):
		"""Creates a new vaccination entry in backend."""
		return gmVaccination.create_vaccination(
			patient_id = self.id_patient,
			episode_id = self.__episode['id'],
			encounter_id = self.__encounter['id'],
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
		result = gmEMRStructItems.create_encounter(
			fk_patient = self.id_patient,
			fk_provider = _whoami.get_staff_ID()
		)
		if result is False:
			return False
		self.__encounter = result
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
		enc_rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, sttl)
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
		enc_rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient, sttl, httl)
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
			from v_basic_person	where i_id=%s"""
		pat = gmPG.run_ro_query('personalia', cmd, None, self.id_patient)
		if (pat is None) or (len(pat) == 0):
			_log.Log(gmLog.lErr, 'cannot access patient [%s]' % self.id_patient)
			return False
		pat_str = '%s %s %s (%s), %s, #%s' % (
			pat[0][0][:5],
			pat[0][1][:12],
			pat[0][2][:12],
			pat[0][3],
			pat[0][4].Format('%Y-%m-%d'),
			self.id_patient
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
	#------------------------------------------------------------------
	# lab data API
	#------------------------------------------------------------------
	def get_lab_results(self):
		try:
			return self.__db_cache['lab results']
		except KeyError:
			pass
		self.__db_cache['lab results'] = []
		# get list of IDs
		# FIXME: date range, episode, encounter, issue, test filter
		# FIXME: hardcoded limit on # of test results
		cmd = "select pk_result from v_results4lab_req where pk_patient=%s limit 500"
		rows = gmPG.run_ro_query('historica', cmd, None, self.id_patient)
		if rows is None:
			return False
		for row in rows:
			try:
				self.__db_cache['lab results'].append(gmPathLab.cLabResult(aPK_obj=row[0]))
			except gmExceptions.ConstructorError:
				_log.Log('lab result error', sys.exc_info())

		return self.__db_cache['lab results']
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
			encounter_id = self.__encounter['id']
		if episode_id is None:
			episode_id = self.__episode['id']
		status, data = gmPathLab.create_lab_request(
			lab=lab,
			req_id=req_id,
			pat_id=self.id_patient,
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
	# trial: allergy panel
	#------------------------------------------------------------------
	def create_allergy(self, allergy):
		"""tries to add allergy to database."""
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		if rw_conn is None:
			_log.Log(gmLog.lErr, 'cannot connect to service [historica]')
			return None
		rw_curs = rw_conn.cursor()
		# FIXME: id_type hardcoded, not reading checkbox states (allergy or sensitivity)
		cmd = """
insert into allergy (
	id_type, id_encounter, id_episode,  substance, narrative, definite
) values (
	%s, %s, %s, %s, %s, %s
)
"""
		gmPG.run_query (rw_curs, cmd, 1, self.__encounter['id'], self.__episode['id'], allergy["substance"], allergy["reaction"], allergy["definite"])
		rw_curs.close()
		rw_conn.commit()
		rw_conn.close()

		return 1
	#------------------------------------------------------------------
	def get_past_history(self):
		if not self.__dict__.has_key('past_history'):
			from gmPastHistory import gmPastHistory
#			from gmEditAreaFacade import gmPHxEditAreaDecorator
			phx  = gmPastHistory(self._backend, self)
			self.past_history = gmPHxEditAreaDecorator(phx)
		return self.past_history
        #-------------------------------------------------------------------
        def store_referral (self, cursor, text, form_id):
		"""
		Stores a referral in the clinical narrative
		"""
		cmd = """
		insert into referral (
		id_encounter, id_episode,  narrative, fk_form
		) values (
		%s, %s, %s, %s
		)
		"""
		return gmPG.run_commit (cursor, [(cmd, [self.__encounter['id'], self.__episode['id'], text, form_id])])

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
# main
#------------------------------------------------------------
if __name__ == "__main__":
	_ = lambda x:x
	gmPG.set_default_client_encoding('latin1')
	try:
		emr = cClinicalRecord(aPKey = 12)
		lab = emr.get_lab_results()
		lab_file = open('lab-data.txt', 'wb')
		for lab_result in lab:
			lab_file.write(str(lab_result))
			lab_file.write('\n')
		lab_file.close()
	#	emr = record.get_text_dump()
	#	print emr
	#	vaccs = record.get_missing_vaccinations()
	#	print vaccs['overdue']
	#	print vaccs['boosters']
	#	dump = record.get_text_dump()
	#	if dump is not None:
	#		keys = dump.keys()
	#		keys.sort()
	#		for aged_line in keys:
	#			for line in dump[aged_line]:
	#				print line
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
		_log.LogException('unhandled exception', sys.exc_info(), verbose=1)
	gmPG.ConnectionPool().StopListeners()
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.106  2004-05-30 19:54:57  ncq
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
