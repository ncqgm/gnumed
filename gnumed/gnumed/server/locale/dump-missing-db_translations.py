#!/usr/bin/env python

"""GNUmed database i18n dumper.

This script dumps all the strings in the database
for which no translation is given.

Usage: just run it
"""
#============================================================
__version__ = "$Revision: 1.9 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string, codecs, logging


_log = logging.getLogger('gm.i18n_db')


sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2

#============================================================
def esc_str(astring):
	tmp = string.replace(astring, "'", "''")
	return tmp
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	print 'dumping untranslated database strings'
	# get strings
	cmd = u'select lang, orig from i18n.v_missing_translations order by lang'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	if rows is None:
		_log.error('cannot retrieve untranslated strings')
		sys.exit('cannot retrieve untranslated strings')
	if len(rows) == 0:
		_log.error('no untranslated strings available')
		print "nothing to translate"
		sys.exit(0)
	# write strings to file
	dump = codecs.open('gnumed-db_translation.sql', 'wb', 'utf8')
	dump.write('set default_transaction_read_only to off\n\n')
	dump.write('\unset ON_ERROR_STOP\n\n')
	for row in rows:
		dump.write("select i18n.upd_tx('%s', '%s', '');\n" % (row[0], esc_str(row[1])))
	dump.write('\n\set ON_ERROR_STOP 1\n')
	dump.close()
	# cleanup
	print "done"
#============================================================
