
db = 'gnumed_v20'		# a database configured "alter database %s set default_transaction_read_only to on"
user = 'gm-dbo'			# a user with CREATE DATABASE powers



cmd_def_tx_ro = "SELECT upper(source), name, upper(setting) FROM pg_settings WHERE name = 'default_transaction_read_only'"
cmd_create_db = "create database %s_copy template %s" % (db, db)


import sys
import psycopg2


conn = psycopg2.connect(dbname = db, user = user)
print 'readonly:', conn.readonly
print 'autocommit:', conn.autocommit
conn.readonly = False
print 'readonly now:', conn.readonly
#curs = conn.cursor()
#curs.execute(cmd_def_tx_ro)
#print 'should show DEFAULT_TRANSACTION_READ_ONLY set to ON'
#print curs.fetchall()
#curs.close()
#conn.commit()
conn.autocommit = True
print 'readonly:', conn.readonly
print 'autocommit:', conn.autocommit
print 'the following CREATE DATABASE should fail'
curs = conn.cursor()
curs.execute(cmd_create_db)
curs.close()
conn.rollback()
conn.close()

sys.exit()





curs = conn.cursor()
#cmd_def_tx_ro = u'show default_transaction_read_only;'
cmd_def_tx_ro = "SELECT upper(source), name, upper(setting) FROM pg_settings WHERE name = 'default_transaction_read_only'"
cmd_tx_ro = 'show transaction_read_only;'
cmd_DEL = 'DELETE FROM dem.identity where pk is NULL'

print conn
print 'initial RO state:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()

#print ''
print 'setting <conn.readonly = False> ...'
conn.readonly = False
print 'RO state in same TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()
print 'RO state in next TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()

print ''
print 'setting <conn.autocommit = True> (conn.readonly still False) ...'
print '-> means exiting psyco TX handling, needed for some DDL such as CREATE DATABASE ...'
conn.autocommit = True
print 'RO state in same TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()
print 'RO state in next TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()

print ''
print 'setting <conn.autocommit = False> (conn.readonly still False) ...'
print '-> means exiting psyco TX handling, needed for some DDL such as CREATE DATABASE ...'
conn.autocommit = False
print 'RO state in same TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()
print 'RO state in same TX:'
print '  psyco (conn.readonly):', conn.readonly
print '  psyco (conn.autocommit):', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_def_tx_ro
curs.execute(cmd_tx_ro)
print '  PG:', curs.fetchall(), '- %s' % cmd_tx_ro
print '  running DELETE:', cmd_DEL
try:
	curs.execute(cmd_DEL)
	print '  success'
except Exception as e:
	print '  failed:', e
conn.commit()



sys.exit()






print 'RO state in same TX:'
print '  psyco - conn.readonly:', conn.readonly
print '  psyco - conn.autocommit:', conn.autocommit
curs.execute(cmd_def_tx_ro)
print '  PG - default_transaction_read_only:', curs.fetchall()
curs.execute(cmd_tx_ro)
print '  PG - transaction_read_only:', curs.fetchall()
conn.commit()
print 'RO state in next TX:'
print '  psyco - conn.readonly:', conn.readonly
curs.execute(cmd_def_tx_ro)
print '  PG - default_transaction_read_only:', curs.fetchall()
curs.execute(cmd_tx_ro)
print '  PG - transaction_read_only:', curs.fetchall()
conn.commit()

print ''

print 'PG/psyco split brain because of:'
cmd = "SELECT upper(source), name, upper(setting) FROM pg_settings WHERE name = 'default_transaction_read_only'"
print '  SQL:', cmd
curs.execute(cmd)
print '  PG:', curs.fetchall()



conn.commit()
curs.execute('DELETE FROM dem.identity where pk is NULL')


curs.close()
conn.commit()
conn.close()
