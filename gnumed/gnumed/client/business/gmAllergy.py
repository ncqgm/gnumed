"""GnuMed allergy related business object.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmAllergy.py,v $
# $Id: gmAllergy.py,v 1.27 2007-08-20 14:17:59 ncq Exp $
__version__ = "$Revision: 1.27 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL"

import types, sys

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog, gmPG2, gmI18N, gmBusinessDBObject

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


allergic_states = [None, -1, 0, 1]
#============================================================
class cAllergy(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one allergy item.

	Actually, those things are really things to *avoid*.
	Allergy is just one of several reasons for that.
	See Adrian's post on gm-dev.
	"""
	_cmd_fetch_payload = u"select * from clin.v_pat_allergies where pk_allergy=%s"
	_cmds_store_payload = [
		u"""update clin.allergy set
				clin_when=%(date)s,
				substance=%(substance)s,
				substance_code=%(substance_code)s,
				generics=%(generics)s,
				allergene=%(allergene)s,
				atc_code=%(atc_code)s,
				fk_type=%(pk_type)s,
				generic_specific=%(generic_specific)s::boolean,
				definite=%(definite)s::boolean,
				narrative=%(reaction)s
			where
				pk=%(pk_allergy)s and
				xmin=%(xmin_allergy)s""",
		u"""select xmin_allergy from clin.v_pat_allergies where pk_allergy=%(pk_allergy)s"""
	]
	_updatable_fields = [
		'date',
		'substance',
		'substance_code',	
		'generics',
		'allergene',
		'atc_code',
		'pk_type',
		'generic_specific',
		'definite',
		'reaction'
	]
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'pk_type':
			if value in ['allergy', 'sensitivity']:
				cmd = u'select pk from clin._enum_allergy_type where value=%s'
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [value]}])
				value = rows[0][0]

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
#============================================================
# convenience functions
#------------------------------------------------------------
def create_allergy(substance=None, allg_type=None, episode_id=None, encounter_id=None):
	"""Creates a new allergy clinical item.

	substance - allergic substance
	allg_type - allergy or sensitivity, pk or string
	encounter_id - encounter's primary key
	episode_id - episode's primary key
	"""
	# sanity checks:
	# 1) any of the args being None should fail the SQL code
	# 2) do episode/encounter belong to the same patient ?
	cmd = u"""
		select pk_patient from clin.v_pat_episodes where pk_episode=%s
			union
		select fk_patient from clin.encounter where pk=%s"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [episode_id, encounter_id]}])

	if len(rows) == 0:
		raise ValueError('error checking episode [%s] <-> encounter [%s] consistency' % (episode_id, encounter_id))

	if len(rows) > 1:
		raise ValueError('episode [%s] and encounter [%s] belong to different patients !?!' % (episode_id, encounter_id))

	pat_id = rows[0][0]

	cmd = u'select pk_allergy from clin.v_pat_allergies where pk_patient=%(pat)s and substance=%(substance)s'
	args = {'pat': pat_id, 'substance': substance}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	if len(rows) > 0:
		# don't implicitely change existing data
		return cAllergy(aPK_obj = rows[0][0])

	# insert new allergy
	queries = []

	if type(allg_type) == types.IntType:
		cmd = u"""
			insert into clin.allergy (fk_type, fk_encounter, fk_episode, substance)
			values (%s, %s, %s, %s)"""
	else:
		cmd = u"""
			insert into clin.allergy (fk_type, fk_encounter, fk_episode,  substance)
			values ((select pk from clin._enum_allergy_type where value = %s), %s, %s, %s)"""
	queries.append({'cmd': cmd, 'args': [allg_type, encounter_id, episode_id, substance]})

	cmd = u"select currval('clin.allergy_id_seq')"
	queries.append({'cmd': cmd})

	rows, idx = gmPG2.run_rw_queries(queries=queries, return_data=True)
	allergy = cAllergy(aPK_obj = rows[0][0])

	return allergy
#============================================================
def allergic_state2str(state=None):
	if state is None:
		return _('unknown allergic state')
	if state == -1:
		return _('undisclosed allergic state')
	if state == 0:
		return _('no known allergies')
	if state == 1:
		return _('does have allergies')

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

	allg = cAllergy(aPK_obj=1)
	print allg
	fields = allg.get_fields()
	for field in fields:
		print field, ':', allg[field]
	print "updatable:", allg.get_updatable_fields()
	enc_id = allg['pk_encounter']
	epi_id = allg['pk_episode']
	status, allg = create_allergy (
		substance = 'test substance',
		allg_type=1,
		episode_id = epi_id,
		encounter_id = enc_id
	)
	print allg
	allg['reaction'] = 'hehehe'
	status, data = allg.save_payload()
	print 'status:', status
	print 'data:', data
	print allg
#============================================================
# $Log: gmAllergy.py,v $
# Revision 1.27  2007-08-20 14:17:59  ncq
# - note on what an "allergy" really is to capture Adrian Midgleys input
#
# Revision 1.26  2007/03/26 16:48:34  ncq
# - various id -> pk/fk type fixes
#
# Revision 1.25  2007/03/21 08:09:07  ncq
# - add allergic_states
# - add allergic_state2str()
#
# Revision 1.24  2007/03/18 12:54:39  ncq
# - allow string and integer for setting pk_type on allergy
#
# Revision 1.24  2007/03/12 12:23:23  ncq
# - error handling now more exception centric
#
# Revision 1.23  2006/10/28 15:02:24  ncq
# - remove superfluous xmin_allergy
#
# Revision 1.22  2006/10/08 14:27:52  ncq
# - convert to cBusinessDBObject
# - convert to gmPG2
#
# Revision 1.21  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.20  2005/11/27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.19  2005/04/30 13:30:02  sjtan
#
# id_patient is  now pk_patient.
#
# Revision 1.18  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.17  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.16  2004/12/15 21:52:05  ncq
# - improve unit test
#
# Revision 1.15  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.14  2004/10/11 19:42:32  ncq
# - add license
# - adapt field names
# - some cleanup
#
# Revision 1.13  2004/06/28 12:18:41  ncq
# - more id_* -> fk_*
#
# Revision 1.12  2004/06/26 07:33:54  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.11  2004/06/14 08:22:10  ncq
# - cast to boolean in save payload
#
# Revision 1.10  2004/06/09 14:32:24  ncq
# - remove extraneous ()'s
#
# Revision 1.9  2004/06/08 00:41:38  ncq
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
