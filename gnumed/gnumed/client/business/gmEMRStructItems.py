"""GnuMed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.8 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cHealthIssue(gmClinItem.cClinItem):
	"""Represents one health issue.
	"""
	_cmd_fetch_payload = """select * from clin_health_issue where id=%s"""

	_cmds_store_payload = [
		"""select 1 from clin_health_issue where id=%(id)s for update""",
		"""update clin_health_issue set
				description=%(description)s
			where id=%(id)s"""
		]

	_updatable_fields = [
		'description'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, patient_id=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select id from clin_health_issue where id_patient=%s and description=%s"
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
#============================================================
class cEpisode(gmClinItem.cClinItem):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_episodes
		where id_episode=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_episode where id=%(id)s for update""",
		"""update clin_episode set
				description=%(episode)s,
				id_health_issue=%(id_health_issue)s
			where id=%(id)s"""
		]
	_updatable_fields = [
		'episode',
		'id_health_issue'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, id_patient=None, name='xxxDEFAULTxxx'):
		pk = aPK_obj
		if pk is None:
			cmd = "select id_episode from v_pat_episodes where id_patient=%s and episode=%s limit 1"
			rows = gmPG.run_ro_query('historica', cmd, None, id_patient, name)
			if rows is None:
				raise gmExceptions.ConstructorError, 'error getting episode for [%s:%s]' % (id_patient, name)
			if len(rows) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no episode for [%s:%s]' % (id_patient, name)
			pk = rows[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['id_patient']]
	#--------------------------------------------------------
	def set_active(self):
		cmd1 = """
			delete from last_act_episode
			where id_patient=(select id_patient from clin_health_issue where id=%s)"""
		cmd2 = """
			insert into last_act_episode(id_episode, id_patient)
			values (%s,	(select id_patient from clin_health_issue where id=%s))"""
		success, msg = gmPG.run_commit('historica', [
			(cmd1, [self._payload[self._idx['id_health_issue']]]),
			(cmd2, [self.pk_obj, self._payload[self._idx['id_health_issue']]])
		], True)
		if not success:
			_log.Log(gmLog.lErr, 'cannot record episode [%s] as most recently used one for health issue [%s]' % (self.pk_obj, self._payload[self._idx['id_health_issue']]))
			_log.Log(gmLog.lErr, str(msg))
			return False
		return True
#============================================================
class cEncounter(gmClinItem.cClinItem):
	"""Represents one encounter.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_encounters
		where pk_encounter=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_encounter where id=%(pk_encounter)s for update""",
		"""update clin_encounter set
				description=%(description)s,
				started=%(started)s,
				last_affirmed=%(last_affirmed)s,
				pk_location=%(pk_location)s,
				pk_provider=%(pk_provider)s,
				pk_type=%(pk_type)s
			where id=%(pk_encounter)s"""
		]

	_updatable_fields = [
		'description',
		'started',
		'last_affirmed',
		'pk_location',
		'pk_provider',
		'pk_type'
	]
	#--------------------------------------------------------
	def set_active(self, staff_id=None):
		cmd = """update clin_encounter set
					fk_provider=%s,
					last_affirmed=now()
				where id=%s"""
		success, msg = gmPG.run_commit('historica', [(cmd, [staff_id, self.pk_obj])], True)
		if not success:
			_log.Log(gmLog.lErr, 'cannot reaffirm encounter [%s]' % self.pk_obj)
			_log.Log(gmLog.lErr, str(msg))
			return False
		return True
#============================================================
# convenience functions
#------------------------------------------------------------	
def create_health_issue(patient_id=None, description='xxxDEFAULTxxx'):
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
	cmd = "insert into clin_health_issue (id_patient, description) values (%s, %s)"
	queries.append((cmd, [patient_id, description]))
	# get PK of inserted row
	cmd = "select currval('clin_health_issue_id_seq')"
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
def create_episode(id_patient = None, id_health_issue = None, episode_name='xxxDEFAULTxxx'):
	"""Creates a new episode for a given patient's health issue.

    id_patient - patient PK
	id_health_issue - given health issue PK
	episode_name - health issue name
	"""
	# already there ?
	try:
		episode = cEpisode(id_patient=id_patient, episode_name=episode_name)
		return (True, episode)
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
	# insert new episode
	queries = []
	cmd = "insert into clin_episode (id_health_issue, description) values (%s, %s)"
	queries.append((cmd, [id_health_issue, episode_name]))
	# get PK of inserted row
	cmd = "select currval('clin_episode_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, msg)
	try:
		episode = cEpisode(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate episode [%s]' % (result[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))
	return (True, episode)
#-----------------------------------------------------------
def create_encounter(fk_patient=None, fk_location=-1, fk_provider=None, description=None, enc_type=None):
	"""Creates a new encounter for a patient.

	fk_patient - patient PK
	fk_location - encounter location
	fk_provider - who was the patient seen by
	description - name or description for the encounter
	enc_type - type of encounter

	FIXME: we don't deal with location yet
	"""
	# sanity check:
	if description is None:
		description = 'auto-created %s' % mxDT.today().Format('%A %Y-%m-%d %H:%M')
	# FIXME: look for MRU/MCU encounter type here
	if enc_type is None:
		enc_type = 'chart review'
	# insert new encounter
	queries = []
	try:
		enc_type = int(enc_type)
		cmd = """
			insert into clin_encounter (
				fk_patient, fk_location, fk_provider, description, fk_type
			) values (
				%s, -1, %s, %s,	%s
			)"""
	except ValueError:
		enc_type = str(enc_type)
		cmd = """
			insert into clin_encounter (
				fk_patient, fk_location, fk_provider, description, fk_type
			) values (
				%s, -1, %s, %s,	coalesce((select id from encounter_type where description=%s), 0)
			)"""
	queries.append((cmd, [fk_patient, fk_provider, description, enc_type]))
	cmd = "select currval('clin_encounter_id_seq')"
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
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	print "health issue test"
	print "-----------------"
	h_issue = cHealthIssue(aPK_obj=1)
	print h_issue
	fields = h_issue.get_fields()
	for field in fields:
		print field, ':', h_issue[field]
	print "updatable:", h_issue.get_updatable_fields()
	

	print "episode test"
	print "------------"
	episode = cEpisode(aPK_obj=1)
	print episode
	fields = episode.get_fields()
	for field in fields:
		print field, ':', episode[field]
	print "updatable:", episode.get_updatable_fields()

	print "encounter test"
	print "--------------"
	encounter = cEncounter(aPK_obj=1)
	print encounter
	fields = encounter.get_fields()
	for field in fields:
		print field, ':', encounter[field]
	print "updatable:", encounter.get_updatable_fields()
#============================================================
# $Log: gmEMRStructItems.py,v $
# Revision 1.8  2004-05-22 12:42:54  ncq
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
