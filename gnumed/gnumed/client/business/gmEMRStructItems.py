"""GnuMed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.77 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys, string

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem, gmClinNarrative
from Gnumed.pycommon.gmPyCompat import *

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
class cHealthIssue(gmClinItem.cClinItem):
	"""Represents one health issue.
	"""
	_cmd_fetch_payload = """select *, xmin from clin.health_issue where pk=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.health_issue where pk=%(pk)s and xmin=%(xmin)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.health_issue set
				description=%(description)s,
				age_noted=%(age_noted)s
			where pk=%(pk)s""",
		"""select xmin from clin.health_issue where pk=%(pk)s"""
	]
	_updatable_fields = [
		'description',
		'age_noted'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, patient_id=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select pk from clin.health_issue where id_patient=%s and description=%s"
			rows = gmPG.run_ro_query('historica', cmd, None, patient_id, name)
			if rows is None:
				raise gmExceptions.ConstructorError, 'error getting health issue for [%s:%s]' % (patient_id, name)
			if len(rows) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no health issue for [%s:%s]' % (patient_id, name)
			pk = rows[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['id_patient']]
	#--------------------------------------------------------
	def rename(self, description=None):
		"""Method for issue renaming.

		@param description
			- the new descriptive name for the issue
		@type description
			- a string instance
		"""
		# sanity check
		if not type(description) in [str, unicode] or description.strip() == '':
			_log.Log(gmLog.lErr, '<description> must be a non empty string instance')
			return False
		# update the issue description
		old_description = self._payload[self._idx['description']]
		self._payload[self._idx['description']] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.Log(gmLog.lErr, 'cannot rename health issue [%s] with [%s]' % (self, description))
			self._payload[self._idx['description']] = old_description
			return False
		return True
	#--------------------------------------------------------
	def close_expired_episodes(self, ttl=180):
		"""ttl in days"""
		cmd = """
update clin.episode set is_open = false where pk in (
	select pk_episode from clin.v_pat_items where
			pk_health_issue = %(issue)s and
			age > (%(ttl)s || ' days')::interval
	except
		select pk from clin.episode where
			is_open and
			fk_health_issue = %(issue)s and
			age(modified_when) < (%(ttl)s || ' days')::interval
)"""
		args = {'issue': self.pk_obj, 'ttl': ttl}
		success, msg = gmPG.run_commit2 ('historica', [(cmd, [args])])
		if success:
			return True
		return False
#============================================================
class cEpisode(gmClinItem.cClinItem):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = """select *, xmin_episode from clin.v_pat_episodes where pk_episode=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.episode where pk=%(pk_episode)s and xmin=%(xmin_episode)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.episode set
				fk_health_issue=%(pk_health_issue)s,
				is_open=%(episode_open)s::boolean,
				description=%(description)s
			where pk=%(pk_episode)s""",
		"""select xmin_episode from clin.v_pat_episodes where pk_episode=%(pk_episode)s"""
	]
	_updatable_fields = [
		'pk_health_issue',
		'episode_open',
		'description'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, id_patient=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select pk_episode from clin.v_pat_episodes where pk_patient=%s and description=%s limit 1"
			rows = gmPG.run_ro_query('historica', cmd, None, id_patient, name)
			if rows is None:
				raise gmExceptions.ConstructorError, 'error getting episode for [%s:%s]' % (id_patient, name)
			if len(rows) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no episode for [%s:%s]' % (id_patient, name)
			pk = rows[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
#	def save_payload(self, conn=None):
#		if self._payload[self._idx['episode_open']]:
#			self._cmds_store_payload[0] = """
#				update clin.episode set
#					is_open = false
#				where
#					is_open = true and pk=%(pk_episode)s"""
#		else:
#			self._cmds_store_payload[0] = """select %(pk_episode)s"""
#		gmClinItem.cClinItem.save_payload(self, conn=conn)
	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['pk_patient']]
	#--------------------------------------------------------
	def get_description(self):
		return self._payload[self._idx['description']]
	#--------------------------------------------------------
	def rename(self, description=None):
		"""Method for episode editing, that is, episode renaming.

		@param description
			- the new descriptive name for the encounter
		@type description
			- a string instance
		"""
		# sanity check
		if not type(description) in [str, unicode]  or description.strip() == '':
			_log.Log(gmLog.lErr, '<description> must be a non empty string instance')
			return False
		# update the episode description
		old_description = self._payload[self._idx['description']]
		self._payload[self._idx['description']] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.Log(gmLog.lErr, 'cannot rename episode [%s] with [%s]' % (self, description))
			self._payload[self._idx['description']] = old_description
			return False
		return True
#============================================================
class cEncounter(gmClinItem.cClinItem):
	"""Represents one encounter.
	"""
	_cmd_fetch_payload = """
		select *, xmin_encounter from clin.v_pat_encounters where pk_encounter=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.encounter where pk=%(pk_encounter)s and xmin=%(xmin_encounter)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.encounter set
				started=%(started)s,
				last_affirmed=%(last_affirmed)s,
				fk_location=%(pk_location)s,
				fk_type=%(pk_type)s,
				reason_for_encounter=%(reason_for_encounter)s,
				assessment_of_encounter=%(assessment_of_encounter)s
			where pk=%(pk_encounter)s""",
		"""select xmin_encounter from clin.v_pat_encounters where pk_encounter=%(pk_encounter)s"""
	]
	_updatable_fields = [
		'started',
		'last_affirmed',
		'pk_location',
		'pk_type',
		'reason_for_encounter',
		'assessment_of_encounter'
	]
	#--------------------------------------------------------
	def set_active(self, staff_id=None):
		"""Set the enconter as the active one.

		"Setting active" means making sure the encounter
		row has the youngest "last_affirmed" timestamp of
		all encounter rows for this patient.

		staff_id - Provider's primary key
		"""
		self._payload[self._idx['last_affirmed']] = mxDT.now()
		if not self.save_payload():
			_log.Log(gmLog.lErr, 'cannot reaffirm encounter [%s]' % self.pk_obj)
			_log.Log(gmLog.lErr, str(msg))
			return False
		return True
	#--------------------------------------------------------
	def transfer_clinical_data(self, from_episode, to_episode):
		"""
		Moves every element currently linked to the current encounter
		and the from_episode onto to_episode.

		@param from_episode The episode the elements are currently linked to.
		@type to_episode A cEpisode intance.
		@param to_episode The episode the elements will be relinked to.
		@type to_episode A cEpisode intance.
		"""
		# sanity check
		if from_episode['pk_episode'] == to_episode['pk_episode']:
			return (True, True)
		queries = []
		# FIXME: this will work but it will not invalidate the cache,
		# FIXME: hence the next save_payload will fail (because xmin is now different)
		cmd = """
			UPDATE clin.clin_root_item SET fk_episode = %s 
 			WHERE fk_encounter = %s AND fk_episode = %s
			"""
		queries.append((cmd, [to_episode['pk_episode'], self.pk_obj, from_episode['pk_episode']]))
		# run queries
		success, data = gmPG.run_commit2(link_obj = 'historica', queries = queries)
		if not success:
			_log.Log(gmLog.lErr, 'cannot relink elements of encounter [%s] from episode [%s] to episode [%s]: %s' % (
				self.pk_obj,
				from_episode['pk_episode'],
				to_episode['pk_episode'],
				str(data)
			))
			err, msg = data
			return (False, msg)
		return (True, True)
#============================================================		
class cProblem(gmClinItem.cClinItem):
	"""Represents one problem.

	problems are the aggregation of
		issues w/o episodes,
		issues w/ episodes and
		episodes w/o issues
	"""
	_cmd_fetch_payload = ''					# will get programmatically defined in __init__
	_cmds_lock_rows_for_update = []
	_cmds_store_payload = ["""select 1"""]
	_updatable_fields = []

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None):
		"""Initialize.

		aPK_obj must contain the keys
			pk_patient
			pk_episode
			pk_health_issue
		"""
		if aPK_obj is None:
			raise gmExceptions.ConstructorError, 'cannot instatiate cProblem for PK: [%s]' % (aPK_obj)
		# As problems are rows from a view of different emr struct items,
		# the PK can't be a single field and, as some of the values of the
		# composed PK may be None, they must be queried using 'is null',
		# so we must programmatically construct the sql query
		where_parts = []
		pk = {}
		for col_name in aPK_obj.keys():
			val = aPK_obj[col_name]
			if val is None:
				where_parts.append('%s is null' % col_name)
			else:
				where_parts.append('%s=%%(%s)s' % (col_name, col_name))
				pk[col_name] = val
		cProblem._cmd_fetch_payload = """select * from clin.v_problem_list where """ + ' and '.join(where_parts)
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_as_episode(self):
		"""
		Retrieve the cEpisode instance equivalent to this problem.
		The problem's type attribute must be 'episode'
		"""
		if self._payload[self._idx['type']] != 'episode':
			_log.Log(gmLog.lErr, 'cannot convert problem [%s] of type [%s] to episode' % (self._payload[self._idx['problem']], self._payload[self._idx['type']]))
			return None
		try:
			episode = cEpisode(aPK_obj=self._payload[self._idx['pk_episode']])
		except gmExceptions.ConstructorError:
			_log.LogException('cannot get episode', sys.exc_info())
			return None		
		return episode
#============================================================
# convenience functions
#------------------------------------------------------------
def create_health_issue(patient_id=None, description=None):
	"""Creates a new health issue for a given patient.

	patient_id - given patient PK
	description - health issue name
	"""
	# already there ?
	try:
		h_issue = cHealthIssue(patient_id=patient_id, name=description)
		return (True, h_issue)
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
	# insert new health issue
	queries = []
	cmd = "insert into clin.health_issue (id_patient, description) values (%s, %s)"
	queries.append((cmd, [patient_id, description]))
	# get PK of inserted row
	cmd = "select currval('clin.health_issue_pk_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		h_issue = cHealthIssue(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate health issue [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, h_issue)
#-----------------------------------------------------------
def create_episode(pk_health_issue=None, episode_name=None, patient_id=None, is_open=False):
	"""Creates a new episode for a given patient's health issue.

	pk_health_issue - given health issue PK
	episode_name - name of episode
	"""
	# already there ?
	try:
		episode = cEpisode(id_patient=patient_id, name=episode_name)
		if episode['is_open'] != is_open:
			episode['is_open'] = is_open
			episode.save_payload()
		return (True, episode)
	except gmExceptions.ConstructorError:
		pass
	# generate queries
	queries = []
	# insert episode
	if patient_id is None:
		cmd = """insert into clin.episode (fk_health_issue, description, is_open) values (%s, %s, %s::boolean)"""
		queries.append((cmd, [pk_health_issue, episode_name, is_open]))
	else:
		cmd = """insert into clin.episode (fk_health_issue, fk_patient, description, is_open) values (%s, %s, %s, %s::boolean)"""
		queries.append((cmd, [pk_health_issue, patient_id, episode_name, is_open]))
	# retrieve PK
	cmd = "select currval('clin.episode_pk_seq')"
	queries.append((cmd, []))
	# run queries
	success, data = gmPG.run_commit2(link_obj = 'historica', queries = queries)
	if not success:
		_log.Log(gmLog.lErr, 'cannot create episode: %s' % str(data))
		err, msg = data
		return (False, msg)
	# now there ?
	rows, idx = data
	pk = rows[0][0]
	try:
		episode = cEpisode(aPK_obj = pk)
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate episode [%s]' % pk, sys.exc_info(), verbose=0)
		return (False, _('internal error, check log'))
	return (True, episode)
#-----------------------------------------------------------
def create_encounter(fk_patient=None, fk_location=-1, enc_type=None):
	"""Creates a new encounter for a patient.

	fk_patient - patient PK
	fk_location - encounter location
	enc_type - type of encounter

	FIXME: we don't deal with location yet
	"""
	# FIXME: look for MRU/MCU encounter type config here
	if enc_type is None:
		enc_type = 'in surgery'
	# insert new encounter
	queries = []
	try:
		enc_type = int(enc_type)
		cmd = """
			insert into clin.encounter (
				fk_patient, fk_location, fk_type
			) values (
				%s, -1, %s
			)"""
	except ValueError:
		enc_type = str(enc_type)
		cmd = """
			insert into clin.encounter (
				fk_patient, fk_location, fk_type
			) values (
				%s, -1,	coalesce((select pk from clin.encounter_type where description=%s), 0)
			)"""
	queries.append((cmd, [fk_patient, enc_type]))
	cmd = "select currval('clin.encounter_pk_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		encounter = cEncounter(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate encounter [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, encounter)
#-----------------------------------------------------------
def get_encounter_types():
	cmd = "SELECT _(description) from clin.encounter_type"
	result = gmPG.run_ro_query('historica', cmd, None)
	if (result is None) or (len(result) == 0):
		_log.Log(gmLog.lWarn, 'cannot load consultation types from backend')
		return [_('in surgery'), _('chart review')]
	consultation_types = []
	for cons_type in result:
		consultation_types.append(cons_type[0])
	return consultation_types
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')
	#--------------------------------------------------------
	# define tests
	#--------------------------------------------------------
	def test_problem():
		print "\nProblem test"
		print "------------"
		prob = cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': 1})
		print prob
		fields = prob.get_fields()
		for field in fields:
			print field, ':', prob[field]
		print '\nupdatable:', prob.get_updatable_fields()
		epi = prob.get_as_episode()
		print '\nas episode:'
		for field in epi.get_fields():
			print '   .%s : %s' % (field, epi[field])
	#--------------------------------------------------------
	def test_health_issue():
		print "\nhealth issue test"
		print "-----------------"
		h_issue = cHealthIssue(aPK_obj=1)
		print h_issue
		fields = h_issue.get_fields()
		for field in fields:
			print field, ':', h_issue[field]
		print "updatable:", h_issue.get_updatable_fields()
	#--------------------------------------------------------	
	def test_episode():
		print "\nepisode test"
		print "------------"
		episode = cEpisode(aPK_obj=1)
		print episode
		fields = episode.get_fields()
		for field in fields:
			print field, ':', episode[field]
		print "updatable:", episode.get_updatable_fields()
		raw_input('ENTER to continue')

		old_description = episode.get_description()
		old_enc = cEncounter(aPK_obj = 1)

		desc = '1-%s' % episode['description']
		print "==> renaming to", desc
		successful = episode.rename (
			description = desc
		)
		if not successful:
			print "error"
		else:
			print "success"
			for field in fields:
				print field, ':', episode[field]
		raw_input('ENTER to continue')

	#--------------------------------------------------------
	def test_encounter():
		print "\nencounter test"
		print "--------------"
		encounter = cEncounter(aPK_obj=1)
		print encounter
		fields = encounter.get_fields()
		for field in fields:
			print field, ':', encounter[field]
		print "updatable:", encounter.get_updatable_fields()

	#--------------------------------------------------------
	# run them
	test_episode()
	#test_problem()

#============================================================
# $Log: gmEMRStructItems.py,v $
# Revision 1.77  2006-03-09 21:11:49  ncq
# - spell out rfe/aoe
#
# Revision 1.76  2006/02/27 22:38:36  ncq
# - spell out rfe/aoe as per Richard's request
#
# Revision 1.75  2005/12/26 05:26:38  sjtan
#
# match schema
#
# Revision 1.74  2005/12/25 13:24:30  sjtan
#
# schema changes in names .
#
# Revision 1.73  2005/12/06 17:57:13  ncq
# - more id->pk fixes
#
# Revision 1.72  2005/12/06 14:24:14  ncq
# - clin.clin_health_issue/episode -> clin.health_issue/episode
#
# Revision 1.71  2005/11/27 12:56:19  ncq
# - add get_encounter_types()
#
# Revision 1.70  2005/11/27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.69  2005/10/15 18:15:37  ncq
# - cleanup
# - clin_encounter has fk_*, not pk_*
# - remove clin_encounter.pk_provider support
# - fix cEncounter.set_active()
# - comment on that transfer_clinical_data will work but will not
#   notify others about its changes
#
# Revision 1.68  2005/10/12 22:31:13  ncq
# - encounter['rfe'] not mandatory anymore, hence don't need default
# - encounters don't have a provider
#
# Revision 1.67  2005/10/11 21:49:36  ncq
# - make create_encounter oblivious of emr object again
#
# Revision 1.66  2005/10/08 12:33:09  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.65  2005/10/04 19:21:31  sjtan
# unicode and str are different but printable types.
#
# Revision 1.64  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.63  2005/09/22 15:45:11  ncq
# - clin_encounter.fk_provider removed
#
# Revision 1.62  2005/09/19 16:32:42  ncq
# - add rfe/aoe support to clin_encounter
# - remove get_aoes()/get_rfes()
#
# Revision 1.61  2005/09/12 15:05:58  ncq
# - improve close_expired_episodes()
#
# Revision 1.60  2005/09/11 17:23:53  ncq
# - close_expired_episodes()
# - support is_open when adding episode
#
# Revision 1.59  2005/08/22 13:02:46  ncq
# - prepare for 0.2
#
# Revision 1.58  2005/07/02 18:16:58  ncq
# - default encounter type "in surgery" for 0.1, to become
#   "in surgery"-on-write later on
#
# Revision 1.57  2005/06/23 14:58:51  ncq
# - clean up transfer_clinical_data()
#
# Revision 1.56  2005/06/20 18:48:51  ncq
# - a little cleanup in transfer_data
#
# Revision 1.55  2005/06/20 13:03:38  cfmoro
# Relink encounter to another episode
#
# Revision 1.54  2005/06/15 22:25:29  ncq
# - issue.rename()
#
# Revision 1.53  2005/06/14 18:53:37  ncq
# - really do rename in rename(), needs to set _is_modified to work
#
# Revision 1.52  2005/06/12 21:40:42  ncq
# - cleanup
#
# Revision 1.51  2005/05/14 15:05:40  ncq
# - show HH:MM in auto-created encounters
#
# Revision 1.50  2005/04/25 08:28:28  ncq
# - episode now has .description
#
# Revision 1.49  2005/04/24 14:42:22  ncq
# - add age_noted as changable
#
# Revision 1.48  2005/04/03 20:05:38  ncq
# - cEpisode.set_active() doesn't make sense no more
#
# Revision 1.47  2005/03/29 07:22:38  ncq
# - improve text for auto generated encounters
#
# Revision 1.46  2005/03/23 18:31:19  ncq
# - v_patient_items -> v_pat_items
#
# Revision 1.45  2005/03/20 16:47:26  ncq
# - cleanup
#
# Revision 1.44  2005/03/17 21:59:35  cfmoro
# Fixed log comment
#
# Revision 1.43  2005/03/17 21:46:23  cfmoro
# Simplified cEpisode.rename function
#
# Revision 1.42  2005/03/17 21:14:45  cfmoro
# Improved exception handling in get_as_episode.
#
# Revision 1.41  2005/03/17 13:35:52  ncq
# - cleanup and streamlining
#
# Revision 1.40  2005/03/16 19:10:06  cfmoro
# Added cProblem.get_as_episode method
#
# Revision 1.39  2005/03/14 14:28:54  ncq
# - id_patient -> pk_patient
# - properly handle simplified episode naming in create_episode()
#
# Revision 1.38  2005/03/08 16:42:47  ncq
# - there are episodes w/ and w/o fk_patient IS NULL so handle that
#   properly in set_active()
#
# Revision 1.37  2005/02/28 18:15:36  ncq
# - proper fix for not being able to fetch unnamed episodes
#   is to require a name in the first place ...
#
# Revision 1.36  2005/02/20 10:30:49  sjtan
#
# unnamed episodes cannot be refetched.
#
# Revision 1.35  2005/01/31 12:58:24  ncq
# - episode.rename() finally works
#
# Revision 1.34  2005/01/31 09:35:28  ncq
# - add episode.get_description() to return clin_narrative row
# - improve episode.rename() - works for adding new narrative now
# - improve create_episode() - revise later
# - improve unit testing
#
# Revision 1.33  2005/01/29 17:53:57  ncq
# - debug/enhance create_episode
#
# Revision 1.32  2005/01/25 17:24:57  ncq
# - streamlined cEpisode.rename()
#
# Revision 1.31  2005/01/25 01:36:19  cfmoro
# Added cEpisode.rename method
#
# Revision 1.30  2005/01/15 20:24:35  ncq
# - streamlined cProblem
#
# Revision 1.29  2005/01/15 19:55:55  cfmoro
# Added problem support to emr
#
# Revision 1.28  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.27  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.26  2004/12/15 10:42:09  ncq
# - cClinEpisode not handles the fields properly
#
# Revision 1.25  2004/12/15 10:28:11  ncq
# - fix create_episode() aka add_episode()
#
# Revision 1.24  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.23  2004/09/19 15:02:29  ncq
# - episode: id -> pk, support fk_patient
# - no default name in create_health_issue
#
# Revision 1.22  2004/07/05 10:24:46  ncq
# - use v_pat_rfe/aoe, by Carlos
#
# Revision 1.21  2004/07/04 15:09:40  ncq
# - when refactoring need to fix imports, too
#
# Revision 1.20  2004/07/04 13:24:31  ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
# Revision 1.19  2004/06/30 20:34:37  ncq
# - cEncounter.get_RFEs()
#
# Revision 1.18  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.17  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.16  2004/06/08 00:44:41  ncq
# - v_pat_episodes now has description, not episode for name of episode
#
# Revision 1.15  2004/06/02 22:12:48  ncq
# - cleanup
#
# Revision 1.14  2004/06/02 13:45:19  sjtan
#
# episode->description for update statement as well.
#
# Revision 1.13  2004/06/02 13:18:48  sjtan
#
# revert, as backend view definition was changed yesterday to be more consistent.
#
# Revision 1.12  2004/06/02 12:48:56  sjtan
#
# map episode to description in cursor.description, so can find as episode['description']
# and also save.
#
# Revision 1.11  2004/06/01 23:53:56  ncq
# - v_pat_episodes.episode -> *.description
#
# Revision 1.10  2004/06/01 08:20:14  ncq
# - limit in get_lab_results
#
# Revision 1.9  2004/05/30 20:10:31  ncq
# - cleanup
#
# Revision 1.8  2004/05/22 12:42:54  ncq
# - add create_episode()
# - cleanup add_episode()
#
# Revision 1.7  2004/05/18 22:36:52  ncq
# - need mx.DateTime
# - fix fields updatable in episode
# - fix delete action in episode.set_active()
#
# Revision 1.6  2004/05/18 20:35:42  ncq
# - cleanup
#
# Revision 1.5  2004/05/17 19:02:26  ncq
# - encounter.set_active()
# - improve create_encounter()
#
# Revision 1.4  2004/05/16 15:47:51  ncq
# - add episode.set_active()
#
# Revision 1.3  2004/05/16 14:31:27  ncq
# - cleanup
# - allow health issue to be instantiated by name/patient
# - create_health_issue()/create_encounter
# - based on Carlos' work
#
# Revision 1.2  2004/05/12 14:28:53  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.1  2004/04/17 12:18:50  ncq
# - health issue, episode, encounter classes
#
