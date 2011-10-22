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
	("select pg_size_pretty(pg_database_size('%s'))" % database, "Size"),
	("select md5(gm.concat_table_structure())", "Hash"),
	("select count(1) from dem.identity", "Patients"),
	("select count(1) from clin.encounter", "Contacts"),
	("select count(1) from clin.episode", "Episodes"),
	("select count(1) from clin.health_issue", "Issues"),
	("select count(1) from clin.test_result", "Results"),
	("select count(1) from clin.vaccination", "Vaccinations"),
	("select count(1) from blobs.doc_med", "Documents"),
	("select count(1) from blobs.doc_obj", "Objects")
]

fname = u'gm_db-%s-fingerprint.log' % database
#==============================================================
outfile = open(fname, 'wb')

outfile.write("Fingerprinting GNUmed database ...\n")
outfile.write("\n")
outfile.write("%15s: %s\n" % ("Name", database))

conn = psycopg2.connect(dsn=dsn)
curs = conn.cursor()

for cmd, label in queries:
	curs.execute(cmd)
	rows = curs.fetchall()
	outfile.write("%15s: %s\n" % (label, rows[0][0]))

if len(sys.argv) > 3:
	if sys.argv[3] == '--with-dump':
		curs.execute('select gm.concat_table_structure()')
		rows = curs.fetchall()
		outfile.write("\n%s\n" % rows[0][0])

curs.close()
conn.rollback()
#==============================================================
