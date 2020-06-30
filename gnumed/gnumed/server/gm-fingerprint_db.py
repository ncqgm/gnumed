#!/usr/bin/env python3

#==============================================================
# This script can be used to fingerprint a GNUmed database.
#
# usage: ./gm-fingerprint_db.py <database name> <gm-dbo password>
#
# author: Karsten Hilbert
# license: GPL v2 or later
#
#==============================================================

import sys
import psycopg2
#import io

from Gnumed.pycommon import gmPG2

database = sys.argv[1]
passwd = sys.argv[2]
dsn = u'dbname=%s user=gm-dbo password=%s' % (database, passwd)
queries = [
	("SELECT pg_size_pretty(pg_database_size('%s'))" % database, "Size (DB)"),
	("SELECT md5(gm.concat_table_structure())", "Schema hash"),
	("SELECT setting FROM pg_settings WHERE name = 'server_version'", "Version (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'server_encoding'", "Encoding (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'lc_collate'", "LC_COLLATE (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'lc_ctype'", "LC_CTYPE (PG)"),
	("SELECT count(1) FROM dem.identity", "Patients"),
	("SELECT count(1) FROM clin.encounter", "Contacts"),
	("SELECT count(1) FROM clin.episode", "Episodes"),
	("SELECT count(1) FROM clin.health_issue", "Issues"),
	("SELECT count(1) FROM clin.test_result", "Results"),
	("SELECT count(1) FROM clin.vaccination", "Vaccinations"),
	("SELECT count(1) FROM blobs.doc_med", "Documents"),
	("SELECT count(1) FROM blobs.doc_obj", "Objects"),
	("SELECT count(1) FROM dem.org", "Organizations"),
	("SELECT count(1) FROM dem.org_unit", "Organizational units"),
	("SELECT max(modified_when) FROM audit.audit_fields", "Last .modified_when"),
	("SELECT max(audit_when) FROM audit.audit_trail", "Last .audit_when")
]

fname = u'gm_db-%s-fingerprint.log' % database
#==============================================================
#outfile = io.open(fname, mode = 'wt', encoding = 'utf8')

#outfile.write(u"Fingerprinting GNUmed database ...\n")
#outfile.write(u"\n")
#outfile.write(u"%20s: %s\n" % (u"Name (DB)", database))

conn = psycopg2.connect(dsn=dsn)
#curs = conn.cursor()
#
#for cmd, label in queries:
#	curs.execute(cmd)
#	rows = curs.fetchall()
#	outfile.write(u"%20s: %s\n" % (label, rows[0][0]))
#
if len(sys.argv) > 3:
	if sys.argv[3] == '--with-dump':
		with_dump = True
	else:
		with_dump = False
#		curs.execute('SELECT gm.concat_table_structure()')
#		rows = curs.fetchall()
#		outfile.write(u"\n%s\n" % rows[0][0])

gmPG2.fingerprint_db(conn = conn, with_dump = with_dump, fname = fname)

#curs.close()
conn.rollback()

#outfile.close()
#==============================================================
