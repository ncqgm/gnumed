#!/usr/bin/env python

"""GnuMed database i18n dumper.

This script dumps all the strings in the database
for which no translation is given.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/locale/dump-missing-db_translations.py,v $
# $Id: dump-missing-db_translations.py,v 1.5 2006-01-09 13:48:23 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

from Gnumed.pycommon import gmPG
# FIXME:
gmPG.set_default_client_encoding('latin1')

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
	cmd = 'select lang, orig from i18n.v_missing_translations order by lang'
	rows = gmPG.run_ro_query('default', cmd)
	if rows is None:
		_log.Log(gmLog.lErr, 'cannot retrieve untranslated strings')
		sys.exit('cannot retrieve untranslated strings')
	if len(rows) is None:
		_log.Log(gmLog.lErr, 'no untranslated strings available')
		print "nothing to translate"
		sys.exit(0)
	# write strings to file
	dump = open('gnumed-db_translation.sql', 'wb')
	dump.write('\unset ON_ERROR_STOP\n\n')
	for row in rows:
		dump.write("select i18n.upd_tx('%s', '%s', '');\n" % (row[0], esc_str(row[1])))
	dump.write('\n\set ON_ERROR_STOP 1\n')
	dump.close()
	# cleanup
	print "done"
#============================================================
# $Log: dump-missing-db_translations.py,v $
# Revision 1.5  2006-01-09 13:48:23  ncq
# - adjust to schema "i18n"
#
# Revision 1.4  2005/03/31 20:11:22  ncq
# - use i18n_upd_tx()
#
# Revision 1.3  2004/05/22 11:50:55  ncq
# - fix imports
#
# Revision 1.2  2004/01/12 17:15:18  ncq
# - removed extra "values" in SQL template
#
# Revision 1.1  2003/12/29 14:57:37  uid66147
# - dumps missing translations from GnuMed database
#
