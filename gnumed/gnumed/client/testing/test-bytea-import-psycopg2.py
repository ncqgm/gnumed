import locale
# this is what makes the difference:
# likely because it somehow changes which encoding
# Python thinks comes back from file.read()
locale.setlocale(locale.LC_ALL, '')

import sys, os.path

import psycopg2 as dbapi

__license__ = "GPL"
dsn = "dbname=gnumed_v2 user=any-doc password=any-doc"
#dsn = "host=salaam.homeunix.com port=5433 dbname=gnumed_v2 user=any-doc password=any-doc"
fname = sys.argv[1]
encodings = 'win1250 win1252 latin1 iso-8859-15 sql_ascii latin9'.split()

log = open('test-bytea-import-psycopg2.log', 'wb')

log.write('running on:\n')
log.write(sys.version + '\n')
log.write(sys.platform + '\n')
conn = dbapi.connect(dsn=dsn + '\n')
#log.write(str(conn.version) + '\n')
conn.close()
del conn

log.write('importing: [%s]' % fname + '\n')

for encoding in encodings:

	print "encoding:", encoding

	log.write("----------------------------------------------" + '\n')
	log.write("testing encoding: [%s]" % encoding + '\n')

	log.write("Python string encoding [%s]" % sys.getdefaultencoding() + '\n')

	# reading file
	log.write("os.path.getsize(%s): [%s]" % (fname, os.path.getsize(fname)) + '\n')
	f = file(fname, "rb")
	img_data = f.read()
	f.close()
	log.write("type(img_data): [%s]" % type(img_data) + '\n')
	log.write("len(img_data) : [%s]" % len(img_data) + '\n')
	img_obj = dbapi.Binary(img_data)
	del(img_data)
	log.write("len(img_obj) : [%s]" % len(str(img_obj)) + '\n')
	log.write("type(img_obj): [%s]" % type(img_obj) + '\n')

	conn = dbapi.connect(dsn=dsn)
	# setting connection level client encoding
	try:
		conn.set_client_encoding(encoding)
	except:
		log.write("cannot set encoding [%s] on connection" % encoding + '\n')

	curs = conn.cursor()

	try:
		# import data
		cmd = "create table test (data bytea)"
		curs.execute(cmd)
		cmd = "insert into test (data) values (%s)"
		curs.execute(cmd, (img_obj, ))
		cmd = "select octet_length(data) from test"
		curs.execute(cmd)
		log.write("INSERTed octet_length(test.data): [%s]" % curs.fetchall()[0][0] + '\n')
		cmd = "update test set data=%s"
		curs.execute(cmd, (img_obj, ))
		cmd = "select octet_length(data) from test"
		curs.execute(cmd)
		log.write("UPDATEd octet_length(test.data): [%s]" % curs.fetchall()[0][0] + '\n')
		cmd = "select data from test"
		curs.execute(cmd)
		rows = curs.fetchone()
		log.write("len(SELECT)  : [%s]" % len(str(rows[0])) + '\n')
	except:
		log.write('cannot test encoding [%s]' % encoding + '\n')
		t, v, tb = sys.exc_info()
		log.write(str(t) + '\n')
		log.write(str(v) + '\n')

	# finish
	conn.rollback()
	curs.close()
	conn.close()

log.close()

#=======================================================================
# $Log: test-bytea-import-psycopg2.py,v $
# Revision 1.2  2007-05-22 13:34:48  ncq
# - port 5433 on salaam
#
# Revision 1.1  2006/09/01 15:25:43  ncq
# - first version for psycopg2
#
# Revision 1.2  2006/08/29 22:18:28  ncq
# - improve
#
# Revision 1.1  2006/07/01 08:43:58  ncq
# - first version
#
#
