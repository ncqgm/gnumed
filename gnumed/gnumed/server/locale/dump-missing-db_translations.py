#!/usr/bin/env python3

"""GNUmed database i18n dumper.

This script dumps all the strings in the database
for which no translation is given.

Usage: just run it
"""
#============================================================
__version__ = "$Revision: 1.9 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string, io, logging


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
	cmd = u'select lang, orig, english from i18n.v_missing_translations order by lang'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if rows is None:
		_log.error('cannot retrieve untranslated strings')
		sys.exit('cannot retrieve untranslated strings')
	if len(rows) == 0:
		_log.error('no untranslated strings available')
		print "nothing to translate"
		sys.exit(0)
	# write strings to file
	dump = open('gnumed-db_translation.sql', mode = 'wt', encoding = 'utf8')
	dump.write(u'set default_transaction_read_only to off\n\n')
	dump.write(u'\\unset ON_ERROR_STOP\n\n')
	for row in rows:
		dump.write(u"""select i18n.upd_tx('%s', '%s', ''); -- "en": %s\n""" % (row['lang'], esc_str(row['orig']), esc_str(row['english'])))
	dump.write(u'\n\set ON_ERROR_STOP 1\n')
	dump.close()
	# cleanup
	print "done"

#============================================================
