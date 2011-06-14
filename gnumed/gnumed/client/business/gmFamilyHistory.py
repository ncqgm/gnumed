"""GNUmed family history handling middleware"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, logging


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
#from Gnumed.pycommon import gmHooks
#from Gnumed.pycommon import gmDispatcher

_log = logging.getLogger('gm.fhx')

#============================================================
# short description
#------------------------------------------------------------
_SQL_get_family_history = u"SELECT * from clin.v_family_history WHERE %s"

class cFamilyHistory(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a Family History item."""

	_cmd_fetch_payload = _SQL_get_family_history % u"pk_family_history = %s"
	_cmds_store_payload = [
		u"""
			UPDATE clin.family_history SET
				narrative = gm.nullify_empty_string(%(condition)s),
				age_noted = gm.nullify_empty_string(%(age_noted)s,
				age_of_death = %(age_of_death)s,
				contributed_to_death = %(contributed_to_death)s,
				clin_when = %(when_known_to_patient)s,
				name_relative = gm.nullify_empty_string(%(name_relative)s),
				dob_relative = %(dob_relative)s,
				fk_episodeo = %(pk_encounter)s,
				pk_episode)s,
				pk_fhx_relation_type)s
			WHERE
				pk = %(pk_family_history)s
					AND
				xmin = %(xmin_family_history)s
			RETURNING
				pk as pk_family_history,
				xmin as xmin_family_history
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		u'condition',
		u'age_noted',
		u'age_of_death',
		u'contributed_to_death',
		u'when_known_to_patient',
		u'name_relative',
		u'dob_relative',
		u'pk_encounter',
		u'pk_episode',
		u'pk_fhx_relation_type'
	]
#------------------------------------------------------------
def get_family_history(order_by=None, patient=None):

	args = {}
	where_parts = []

	if patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')
		args['pat'] = patient

	if order_by is None:
		if len(where_parts) == 0:
			order_by = u'true'
		else:
			order_by = u''
	else:
		if len(where_parts) == 0:
			order_by = u'true ORDER BY %s' % order_by
		else:
			order_by = u'ORDER BY %s' % order_by

	cmd = _SQL_get_family_history % u' AND '.join(where_parts) + u' ' + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cFamilyHistory(row = {'data': r, 'idx': idx, 'pk_field': 'pk_family_history'}) for r in rows ]
#------------------------------------------------------------
def create_family_history(encounter=None, episode=None, condition=None, relation=None):

	args = {
		u'enc': encounter,
		u'epi': episdoe,
		u'cond': condition,
		u'rel': relation
	}
	cmd = u"""
		INSERT INTO clin.family_history (
			soap_cat,
			fk_encounter,
			fk_episode,
			narrative,
			fk_relation_type
		) VALUES (
			's'::text,
			%(enc)s,
			%(epi)s,
			gm.nullify_empty_string(%(cond)s),
			%(rel)s
		)
		RETURNING pk
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cFamilyHistory(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_family_history(pk_family_history=None):
	args = {'pk': pk_family_history}
	cmd = u"DELETE FROM clin.family_history WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#------------------------------------------------------------




#============================================================
#def _on_code_link_modified():
#	"""Always relates to the active patient."""
#	gmHooks.run_hook_script(hook = u'after_code_link_modified')

#gmDispatcher.connect(_on_code_link_modified, u'episode_code_mod_db')
#gmDispatcher.connect(_on_code_link_modified, u'rfe_code_mod_db')
#gmDispatcher.connect(_on_code_link_modified, u'aoe_code_mod_db')
#gmDispatcher.connect(_on_code_link_modified, u'health_issue_code_mod_db')
#gmDispatcher.connect(_on_code_link_modified, u'narrative_code_mod_db')
#gmDispatcher.connect(_on_code_link_modified, u'procedure_code_mod_db')

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#----------------------------------------------------
	def test_get_fhx():
		print "family history:"
		for fhx in get_family_history():
			print fhx
	#----------------------------------------------------
	test_get_fhx()

#============================================================
