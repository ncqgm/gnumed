"""GnuMed allergy related business object.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmAllergy.py,v $
# $Id: gmAllergy.py,v 1.9 2004-06-08 00:41:38 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cAllergy(gmClinItem.cClinItem):
	"""Represents one allergy event.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_allergies
		where id=%s"""

	_cmds_store_payload = [
		"""select 1 from allergy where id=%(id)s for update""",
		"""update allergy set
				substance=%(substance)s,
				substance_code=%(substance_code)s,
				generics=%(generics)s,
				allergene=%(allergene)s,
				atc_code=%(atc_code)s,
				id_type=%(id_type)s,
				generic_specific=%(generic_specific)s,
				definite=%(definite)s,
				narrative=%(reaction)s
			where id=%(id)s"""
		]

	_updatable_fields = [
		'substance',
		'substance_code',	
		'generics',
		'allergene',
		'atc_code',
		'id_type',
		'generic_specific',
		'definite',
		'reaction'
	]
#============================================================
# convenience functions
#------------------------------------------------------------
def create_allergy(substance=None, allg_type=None, episode_id=None, encounter_id=None):
	"""Creates a new allergy clinical item.

	substance - allergic substance
	allg_type - allergy or sensitivity
	encounter_id - encounter's primary key
	episode_id - episode's primary key
	"""
	# sanity checks:
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the same patient ?
	cmd = """
		select id_patient from v_pat_episodes where id_episode=%s
			union
		select pk_patient from v_pat_encounters where pk_encounter=%s"""
	rows = gmPG.run_ro_query('historica', cmd, None, episode_id, encounter_id)
	if (rows is None) or (len(rows) == 0):
		_log.Log(gmLog.lErr, 'error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))
		return (None, _('internal error, check log'))
	if len(rows) > 1:
		_log.Log(gmLog.lErr, 'episode [%s] and encounter [%s] belong to more than one patient !?!' % (episode_id, encounter_id))
		return (None, _('consistency error, check log'))
	pat_id = rows[0][0]
	# insert new allergy
	queries = []
	if type(allg_type) == types.IntType:
		cmd = """
			insert into allergy (id_type, id_encounter, id_episode, substance)
			values (%s, %s, %s, %s)"""
	else:
		cmd = """
			insert into allergy (id_type, id_encounter, id_episode,  substance)
			values ((select id from _enum_allergy_type where value=%s), %s, %s, %s)"""
		allg_type = str(allg_type)
	queries.append((cmd, [allg_type, encounter_id, episode_id, substance]))
	# set patient has_allergy status
	cmd = """delete from allergy_state where fk_patient=%s"""
	queries.append((cmd, [pat_id]))
	cmd = """insert into allergy_state (fk_patient, has_allergy) values (%s, 1)"""
	queries.append((cmd, [pat_id]))
	# get PK of inserted row
	cmd = "select currval('allergy_id_seq')"
	queries.append((cmd, []))
	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (None, msg)
	try:
		allergy = cAllergy(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate allergy [%s]' % (result[0][0]), sys.exc_info(), verbose=0)
		return (None, _('internal error, check log'))
	return (True, allergy)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	from Gnumed.pycommon import gmPG, gmI18N

	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	gmPG.set_default_client_encoding('latin1')
	allg = cAllergy(aPK_obj=1)
	print allg
	fields = allg.get_fields()
	for field in fields:
		print field, ':', allg[field]
	print "updatable:", allg.get_updatable_fields()
	enc_id = allg['id_encounter']
	epi_id = allg['id_episode']
	status, allg = create_allergy (
		substance = 'test substance',
		allg_type=1,
		episode_id = epi_id,
		encounter_id = enc_id
	)
	print allg
	allg['reaction'] = 'hehehe'
	allg.save_payload()
	print allg
#============================================================
# $Log: gmAllergy.py,v $
# Revision 1.9  2004-06-08 00:41:38  ncq
# - fix imports, cleanup, improved self-test
#
# Revision 1.8  2004/06/02 21:47:27  ncq
# - improved sanity check in create_allergy() contributed by Carlos
#
# Revision 1.7  2004/05/30 18:33:28  ncq
# - cleanup, create_allergy, done mostly by Carlos
#
# Revision 1.6  2004/05/12 14:28:52  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.5  2004/04/20 13:32:33  ncq
# - improved __str__ output
#
# Revision 1.4  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.3  2004/04/16 16:17:33  ncq
# - test save_payload
#
# Revision 1.2  2004/04/16 00:00:59  ncq
# - Carlos fixes
# - save_payload should now work
#
# Revision 1.1  2004/04/12 22:58:55  ncq
# - Carlos sent me this
#
