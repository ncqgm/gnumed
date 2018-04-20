# -*- coding: utf-8 -*-
#
# please run this script against a database which is configured to be readonly by:
#
#	alter databaes <NAME> set default_transaction_read_only to on
#
# if cmd line argument is "show_problem" -> exhibit the problem

db = 'gnumed_v20'		# a database configured "alter database %s set default_transaction_read_only to on"
user = 'gm-dbo'			# a user with CREATE DATABASE powers

#--------------------------------------------------------------------------------
import sys
import psycopg2


cmd_def_tx_ro = "SELECT upper(source), name, upper(setting) FROM pg_settings WHERE name = 'default_transaction_read_only'"
cmd_create_db = "create database %s_copy template %s" % (db, db)
cmd_drop_db = "drop database %s_copy" % db

show_problem = False
if len(sys.argv) > 1:
	if sys.argv[1] == 'show_problem':
		show_problem = True

conn = psycopg2.connect(dbname = db, user = user)
print 'conn:', conn
print 'readonly:', conn.readonly
print 'autocommit:', conn.autocommit
print 'setting autocommit to False'
conn.autocommit = False
print 'autocommit now:', conn.autocommit
if show_problem:
	print 'vvvvv this creates the problem vvvvv'
	print ' setting readonly to False'
	conn.readonly = False
	print ' readonly now:', conn.readonly
	print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
print 'setting autocommit to True'
conn.autocommit = True
print 'autocommit now:', conn.autocommit
print 'setting readonly to False'
conn.readonly = False
print 'readonly now:', conn.readonly
curs = conn.cursor()
curs.execute(cmd_def_tx_ro)
print 'querying DEFAULT_TRANSACTION_READ_ONLY state (should show "ON")'
print curs.fetchall()
curs.close()
conn.commit()
print 'the following SQL will fail:', cmd_create_db
print '(note that the transaction being talked about is implicit to PostgreSQL, due to autocommit mode)'
curs = conn.cursor()
try:
	curs.execute(cmd_create_db)
	curs.execute(cmd_drop_db)
except psycopg2.InternalError as ex:
	print 'SQL failed:'
	print ex

print 'shutting down'

curs.close()
conn.rollback()
conn.close()
