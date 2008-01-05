"""GNUmed data mining middleware."""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmDataMining.py,v $
# $Id: gmDataMining.py,v 1.3 2008-01-05 23:24:29 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2


#============================================================
def report_exists(name=None):
	rows, idx = gmPG2.run_ro_queries(queries = [{
		'cmd': u'select exists(select 1 from cfg.report_query where label=%(name)s)',
		'args': {'name': name}
	}])
	return rows[0][0]
#--------------------------------------------------------
def save_report_definition(name=None, query=None, overwrite=False):
	if not overwrite:
		if report_exists(name=name):
			return False

	queries = [
		{'cmd': u'delete from cfg.report_query where label=%(name)s', 'args': {'name': name}},
		{'cmd': u'insert into cfg.report_query (label, cmd) values (%(name)s, %(query)s)',
		 'args': {'name': name, 'query': query}}
	]
	rows, idx = gmPG2.run_rw_queries(queries=queries)
	return True
#--------------------------------------------------------
def delete_report_definition(name=None):
	queries = [{
		'cmd': u'delete from cfg.report_query where label=%(name)s',
		'args': {'name': name}
	}]
	rows, idx = gmPG2.run_rw_queries(queries=queries)
	return True
#============================================================
if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		test_report = u'test suite report'
		test_query = u'select 1 as test_suite_report_result'

		print "delete (should work):", delete_report_definition(name = test_report)
		print "check (should return False):", report_exists(name = test_report)
		print "save (should work):", save_report_definition(name = test_report, query = test_query)
		print "save (should fail):", save_report_definition(name = test_report, query = test_query, overwrite = False)
		print "save (should work):", save_report_definition(name = test_report, query = test_query, overwrite = True)
		print "delete (should work):", delete_report_definition(name = test_report)
		print "check (should return False):", report_exists(name = test_report)
#============================================================
# $Log: gmDataMining.py,v $
# Revision 1.3  2008-01-05 23:24:29  ncq
# - fixup test framework
#
# Revision 1.2  2007/04/08 21:16:16  ncq
# - fix and add test suite
# - delete_report_definition()
#
# Revision 1.1  2007/04/08 19:20:04  ncq
# - added
