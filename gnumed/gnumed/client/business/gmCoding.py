"""GNUmed coding systems handling middleware"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys
import logging


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmDispatcher


_log = logging.getLogger('gm.coding')

#============================================================
def _on_code_link_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = 'after_code_link_modified')

gmDispatcher.connect(_on_code_link_modified, 'clin.episode_code_mod_db')
gmDispatcher.connect(_on_code_link_modified, 'clin.rfe_code_mod_db')
gmDispatcher.connect(_on_code_link_modified, 'clin.aoe_code_mod_db')
gmDispatcher.connect(_on_code_link_modified, 'clin.health_issue_code_mod_db')
gmDispatcher.connect(_on_code_link_modified, 'clin.narrative_code_mod_db')
gmDispatcher.connect(_on_code_link_modified, 'clin.procedure_code_mod_db')

#============================================================
# generic linked code handling
#------------------------------------------------------------
_SQL_get_generic_linked_codes = "SELECT * FROM clin.v_linked_codes WHERE %s"

class cGenericLinkedCode(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a generic linked code.

	READ ONLY
	"""
	_cmd_fetch_payload = _SQL_get_generic_linked_codes % "pk_lnk_code2item = %s"
	_cmds_store_payload:list = []
	_updatable_fields:list = []
#------------------------------------------------------------
def get_generic_linked_codes(order_by=None):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_generic_linked_codes % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return [ cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

#============================================================
# this class represents a generic (non-qualified) code
#------------------------------------------------------------
_SQL_get_generic_code = "SELECT * FROM ref.v_generic_codes WHERE %s"

class cGenericCode(gmBusinessDBObject.cBusinessDBObject):
	"""READ ONLY"""
	_cmd_fetch_payload = _SQL_get_generic_code % "pk_generic_code = %s"
	_cmds_store_payload:list = []
	_updatable_fields:list = []
#------------------------------------------------------------
def get_generic_codes(order_by=None):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_generic_code % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return [ cGenericCode(row = {'data': r, 'pk_field': 'pk_generic_code'}) for r in rows ]

#============================================================
# module level functions
#------------------------------------------------------------
def get_coded_terms(coding_systems=None, languages=None, order_by=None):

	where_snippets = []
	args = {}

	if coding_systems is not None:
		where_snippets.append("((coding_system = ANY(%(sys)s)) OR (coding_system_long = ANY(%(sys)s))")
		args['sys'] = coding_systems

	if languages is not None:
		where_snippets.append('lang = ANY(%(lang)s)')
		args['lang'] = languages

	cmd = 'select * from ref.v_coded_terms'

	if len(where_snippets) > 0:
		cmd += ' WHERE %s' % ' AND '.join(where_snippets)

	if order_by is not None:
		cmd += ' ORDER BY %s' % order_by

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	return rows

#============================================================
def get_data_sources(order_by='name_long, lang, version'):
	cmd = 'SELECT * FROM ref.data_source ORDER BY %s' % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return rows

#============================================================
def create_data_source(long_name=None, short_name=None, version=None, source=None, language=None):

		args = {
			'lname': long_name,
			'sname': short_name,
			'ver': version,
			'src': source,
			'lang': language
		}

		cmd = "SELECT pk FROM ref.data_source WHERE name_long = %(lname)s AND name_short = %(sname)s AND version = %(ver)s"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			return rows[0]['pk']

		cmd = """
			INSERT INTO ref.data_source (name_long, name_short, version, source, lang)
			VALUES (
				%(lname)s,
				%(sname)s,
				%(ver)s,
				%(src)s,
				%(lang)s
			)
			RETURNING pk
		"""
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

		return rows[0]['pk']

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#----------------------------------------------------
	def test_get_generic_codes():
		print("generic codes:")
		for code in get_generic_codes():
			print(code)
	#----------------------------------------------------
	def test_get_coded_terms():
		print("known codes:")
		for term in get_coded_terms():
			print(term)
	#----------------------------------------------------
	def test_get_generic_linked_codes():
		print("generically linked generic codes:")
		for code in get_generic_linked_codes():
			print(code)
	#----------------------------------------------------
	#test_get_coded_terms()
	#test_get_generic_codes()
	test_get_generic_linked_codes()

#============================================================
