"""GNUmed Surgery related middleware."""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmSurgery.py,v $
# $Id: gmSurgery.py,v 1.1 2007-04-07 23:00:01 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2


#============================================================
class cSurgery(object):

	#--------------------------------------------------------
	# reports API
	#--------------------------------------------------------
	def report_exists(self, name=None):
		rows, idx = gmPG2.run_ro_query(queries = [{
			'cmd': 'select exists(select 1 from cfg.report_query where label=%(name)s)',
			'args': {'name': name}
		}])
		return rows[0][0]
	#--------------------------------------------------------
	def save_report_definition(self, name=None, query=None, overwrite=False):
		if not overwrite:
			if self.report_exists(name=name):
				return False

		queries = [
			{'cmd': u'delete from cfg.report_query where label=%(name)s', 'args': {'name': name}},
			{'cmd': u'insert into cfg.report_query (label, cmd) values (%(name)s, %(query)s)',
			 'args': {'name': name, 'query': query}}
		]
		rows, idx = gmPG2.run_rw_queries(queries=queries)
		return True
	#--------------------------------------------------------

#============================================================
if __name__ == '__main__':
	pass

#============================================================
# $Log: gmSurgery.py,v $
# Revision 1.1  2007-04-07 23:00:01  ncq
# - Medical Practice (Surgery) related stuff
#
#