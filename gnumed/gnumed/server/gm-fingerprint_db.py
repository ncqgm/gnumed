#!/usr/bin/env python

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

database = sys.argv[1]
passwd = sys.argv[2]
dsn = u'dbname=%s user=gm-dbo password=%s' % (database, passwd)
queries = [
	("SELECT md5(gm.concat_table_structure())", "Schema hash"),
	("SELECT pg_size_pretty(pg_database_size('%s'))" % database, "Size"),
	("SELECT count(1) FROM dem.identity", "Patients"),
	("SELECT count(1) FROM clin.encounter", "Contacts"),
	("SELECT count(1) FROM clin.episode", "Episodes"),
	("SELECT count(1) FROM clin.health_issue", "Issues"),
	("SELECT count(1) FROM clin.test_result", "Results"),
	("SELECT count(1) FROM clin.vaccination", "Vaccinations"),
	("SELECT count(1) FROM blobs.doc_med", "Documents"),
	("SELECT count(1) FROM blobs.doc_obj", "Objects"),
	("SELECT setting FROM pg_settings WHERE name = 'server_version'", "Version (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'server_encoding'", "Encoding (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'lc_collate'", "LC_COLLATE (PG)"),
	("SELECT setting FROM pg_settings WHERE name = 'lc_ctype'", "LC_CTYPE (PG)")
]

fname = u'gm_db-%s-fingerprint.log' % database
#==============================================================
outfile = open(fname, 'wb')

outfile.write("Fingerprinting GNUmed database ...\n")
outfile.write("\n")
outfile.write("%20s: %s\n" % ("Name", database))

conn = psycopg2.connect(dsn=dsn)
curs = conn.cursor()

for cmd, label in queries:
	curs.execute(cmd)
	rows = curs.fetchall()
	outfile.write("%20s: %s\n" % (label, rows[0][0]))

if len(sys.argv) > 3:
	if sys.argv[3] == '--with-dump':
		curs.execute('SELECT gm.concat_table_structure()')
		rows = curs.fetchall()
		outfile.write("\n%s\n" % rows[0][0])

curs.close()
conn.rollback()
#==============================================================
