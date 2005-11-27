"""GnuMed clinical narrative business object.

"""
#============================================================
__version__ = "$Revision: 1.20 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (for details see http://gnu.org)'

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cDiag(gmClinItem.cClinItem):
	"""Represents one real diagnosis.
	"""
	_cmd_fetch_payload = """select *, xmin_clin_diag, xmin_clin_narrative from clin.v_pat_diag where pk_diag=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.clin_diag where pk=%(pk_diag)s and xmin=%(xmin_clin_diag)s for update""",
		"""select 1 from clin.clin_narrative where pk=%(pk_diag)s and xmin=%(xmin_clin_narrative)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.clin_diag set
				laterality=%()s,
				laterality=%(laterality)s,
				is_chronic=%(is_chronic)s::boolean,
				is_active=%(is_active)s::boolean,
				is_definite=%(is_definite)s::boolean,
				clinically_relevant=%(clinically_relevant)s::boolean
			where pk=%(pk_diag)s""",
		"""update clin.clin_narrative set
				narrative=%(diagnosis)s
			where pk=%(pk_diag)s""",
		"""select xmin_clin_diag, xmin_clin_narrative from clin.v_pat_diag where pk_diag=%s(pk_diag)s"""
		]

	_updatable_fields = [
		'diagnosis',
		'laterality',
		'is_chronic',
		'is_active',
		'is_definite',
		'clinically_relevant'
	]
	#--------------------------------------------------------
	def get_codes(self):
		"""
			Retrieves codes linked to this diagnosis
		"""
		cmd = "select code, coding_system from clin.v_codes4diag where diagnosis=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['diagnosis']])
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting codes for diagnosis [%s] (%s)' % (self._payload[self._idx['diagnosis']], self.pk_obj))
			return []
		return rows
	#--------------------------------------------------------
	def add_code(self, code=None, coding_system=None):
		"""
			Associates a code (from coding system) with this diagnosis.
		"""
		# insert new code
		queries = []
		cmd = "select add_coded_term (%s, %s, %s)"
		queries.append((cmd, [self._payload[self._idx['diagnosis']], code, coding_system]))
		result, msg = gmPG.run_commit('historica', queries, True)
		if result is None:
			return (False, msg)
		return (True, msg)
#============================================================
class cNarrative(gmClinItem.cClinItem):
	"""
		Represents one clinical free text entry
	"""
	_cmd_fetch_payload = """
		select *, xmin_clin_narrative from clin.v_pat_narrative where pk_narrative=%s"""
#		select * , coalesce( (select lastnames ||', '|| firstnames from clin.clin.v_staff where clin.clin.v_staff.pk_staff = clin.v_pat_narrative.pk_provider), 'Anon') as provider,  xmin_clin_narrative from v_pat_narrative where pk_narrative=%s
	_cmds_lock_rows_for_update = [
		"""select 1 from clin.clin_narrative where pk=%(pk_narrative)s and xmin=%(xmin_clin_narrative)s for update"""
	]
	_cmds_store_payload = [
		"""update clin.clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(date)s,
				soap_cat=lower(%(soap_cat)s)
			where pk=%(pk_narrative)s""",
		"""select xmin_clin_narrative from clin.v_pat_narrative where pk_narrative=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'date',
		'soap_cat',
		'pk_episode'
	]
	#--------------------------------------------------------
	def get_codes(self):
		"""
			Retrieves codes linked to *this* narrative
		"""
		# Note: caching won't work without having a mechanism
		# to evict the cache when the backend changes
		cmd = "select code, xfk_coding_system from coded_narrative where term=%s"
		rows = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['narrative']])
		if rows is None:
			_log.Log(gmLog.lErr, 'error getting codes for narrative [%s]' % self.pk_obj)
			return []
		return rows
	#--------------------------------------------------------
	def add_code(self, code=None, coding_system=None):
		"""
			Associates a code (from coding system) with this narrative.
		"""
		# insert new code
		queries = []
		cmd = "select add_coded_term (%s, %s, %s)"
		queries.append((cmd, [self._payload[self._idx['narrative']], code, coding_system]))
		result, msg = gmPG.run_commit('historica', queries, True)
		if result is None:
			return (False, msg)
		return (True, msg)
#============================================================
# convenience functions
#============================================================
def create_clin_narrative(narrative = None, soap_cat = None, episode_id=None, encounter_id=None):
	"""
		Creates a new clinical narrative entry
		
		narrative - free text clinical narrative
		soap_cat - soap category
		episode_id - episodes's primary key
		encounter_id - encounter's primary key
	"""
	# sanity check
	# 1) any of the args being None should fail the SQL code
	#    but silently do not insert empty narrative
	if narrative.strip() == '':
		return (True, None)
	# 2) do episode/encounter belong to the patient ?
	cmd = """select pk_patient from clin.v_pat_episodes where pk_episode=%s 
				 union 
			 select pk_patient from clin.v_pat_encounters where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (False, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (False, _('consistency error, check log'))
	# insert new narrative
	queries = []
	cmd = """insert into clin.clin_narrative (fk_encounter, fk_episode, narrative, soap_cat)
				 values (%s, %s, %s, lower(%s))"""
	queries.append((cmd, [encounter_id, episode_id, narrative, soap_cat]))
	# get PK of inserted row
	cmd = "select currval('clin.clin_narrative_pk_seq')"
	queries.append((cmd, []))

	successful, data = gmPG.run_commit2('historica', queries)
	if not successful:
		err, msg = data
		return (False, msg)
	try:
		narrative = cNarrative(aPK_obj = data[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate narrative' % (data[0][0]), sys.exc_info, verbose=0)
		return (False, _('internal error, check log'))

	return (True, narrative)
#------------------------------------------------------------
def delete_clin_narrative(narrative=None):
	"""Deletes a clin.clin_narrative row by it's PK."""
	cmd = """delete from clin.clin_narrative where pk=%s"""
	successful, data = gmPG.run_commit2('historica', (cmd, [narrative]))
	if not successful:
		err, msg = data
		_log.Log(gmLog.lErr, 'cannot delete narrative (%s: %s)' % (err, msg))
		return False
	return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	print "\ndiagnose test"
	print  "-------------"
	diagnose = cDiag(aPK_obj=2)
	fields = diagnose.get_fields()
	for field in fields:
		print field, ':', diagnose[field]
	print "updatable:", diagnose.get_updatable_fields()
	print "codes:", diagnose.get_codes()
	#print "adding code..."
	#diagnose.add_code('Test code', 'Test coding system')
	#print "codes:", diagnose.get_codes()

	print "\nnarrative test"
	print	"--------------"
	narrative = cNarrative(aPK_obj=7)
	fields = narrative.get_fields()
	for field in fields:
		print field, ':', narrative[field]
	print "updatable:", narrative.get_updatable_fields()
	print "codes:", narrative.get_codes()
	#print "adding code..."
	#narrative.add_code('Test code', 'Test coding system')
	#print "codes:", diagnose.get_codes()
	
	#print "creating narrative..."
	#status, new_narrative = create_clin_narrative(narrative = 'Test narrative', soap_cat = 'a', episode_id=1, encounter_id=2)
	#print new_narrative
	
#============================================================
# $Log: gmClinNarrative.py,v $
# Revision 1.20  2005-11-27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.19  2005/10/10 18:27:34  ncq
# - v_pat_narrative already HAS .provider
#
# Revision 1.18  2005/10/08 12:33:09  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.17  2005/09/19 16:32:02  ncq
# - remove is_rfe/is_aoe/cRFE/cAOE
#
# Revision 1.16  2005/06/09 21:29:16  ncq
# - added missing s in %()s
#
# Revision 1.15  2005/05/17 08:00:09  ncq
# - in create_narrative() ignore empty narrative
#
# Revision 1.14  2005/04/11 17:53:47  ncq
# - id_patient -> pk_patient fix
#
# Revision 1.13  2005/04/08 13:27:54  ncq
# - adapt get_codes()
#
# Revision 1.12  2005/01/31 09:21:48  ncq
# - use commit2()
# - add delete_clin_narrative()
#
# Revision 1.11  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.10  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.9  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.8  2004/09/25 13:26:35  ncq
# - is_significant -> clinically_relevant
#
# Revision 1.7  2004/08/11 09:42:50  ncq
# - point clin_narrative VO to v_pat_narrative
# - robustify by applying lower() to soap_cat on insert/update
#
# Revision 1.6  2004/07/25 23:23:39  ncq
# - Carlos made cAOE.get_diagnosis() return a cDiag instead of a list
#
# Revision 1.5	2004/07/14 09:10:21	 ncq
# - Carlos' relentless work brings us get_codes(),
#	get_possible_codes() and adjustions for the fact
#	that we can now code any soap row
#
# Revision 1.4	2004/07/07 15:05:51	 ncq
# - syntax fixes by Carlos
# - get_codes(), get_possible_codes()
# - talk to the right views
#
# Revision 1.3	2004/07/06 00:09:19	 ncq
# - Carlos added create_clin_narrative(), cDiag, cNarrative, and unit tests - nice work !
#
# Revision 1.2	2004/07/05 10:24:46	 ncq
# - use v_pat_rfe/aoe, by Carlos
#
# Revision 1.1	2004/07/04 13:24:31	 ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
