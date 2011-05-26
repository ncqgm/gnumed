"""GNUmed coding systems handling middleware"""
#============================================================
__license__ = "GPL"
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, logging


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject

_log = logging.getLogger('gm.coding')
_log.info(__version__)

#============================================================
# generic linked code handling
#------------------------------------------------------------
_SQL_get_generic_linked_codes = u"SELECT * FROM clin.v_linked_codes WHERE %s"

class cGenericLinkedCode(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a generic linked code.

	READ ONLY
	"""
	_cmd_fetch_payload = _SQL_get_generic_linked_codes % u"pk_lnk_code2item = %s"
	_cmds_store_payload = []
	_updatable_fields = []
#------------------------------------------------------------
def get_generic_linked_codes(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_generic_linked_codes % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]
#============================================================
# this class represents a generic (non-qualified) code
#------------------------------------------------------------
_SQL_get_generic_code = u"SELECT * FROM ref.v_generic_codes WHERE %s"

class cGenericCode(gmBusinessDBObject.cBusinessDBObject):
	"""READ ONLY"""
	_cmd_fetch_payload = _SQL_get_generic_code % u"pk_generic_code = %s"
	_cmds_store_payload = []
	_updatable_fields = []
#------------------------------------------------------------
def get_generic_codes(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_generic_code % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cGenericCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_generic_code'}) for r in rows ]

#============================================================
# module level functions
#------------------------------------------------------------
def get_coded_terms(coding_systems=None, languages=None, order_by=None):

	where_snippets = []
	args = {}

	if coding_systems is not None:
		where_snippets.append(u"((coding_system IN %(sys)s) OR (coding_system_long IN %(sys)s)")
		args['sys'] = tuple(coding_systems)

	if languages is not None:
		where_snippets.append(u'lang IN %(lang)s')
		args['lang'] = tuple(languages)

	cmd = u'select * from ref.v_coded_terms'

	if len(where_snippets) > 0:
		cmd += u' WHERE %s' % u' AND '.join(where_snippets)

	if order_by is not None:
		cmd += u' ORDER BY %s' % order_by

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	return rows
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
		print "generic codes:"
		for code in get_generic_codes():
			print code
	#----------------------------------------------------
	def test_get_coded_terms():
		print "known codes:"
		for term in get_coded_terms():
			print term
	#----------------------------------------------------
	def test_get_generic_linked_codes():
		print "generically linked generic codes:"
		for code in get_generic_linked_codes():
			print code
	#----------------------------------------------------
	#test_get_coded_terms()
	#test_get_generic_codes()
	test_get_generic_linked_codes()

#============================================================
