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


_log = logging.getLogger('gm.coding')
_log.info(__version__)
#============================================================
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

	print "known codes:"
	for term in get_coded_terms():
		print term

#============================================================
