import sys, os.path
import pyPgSQL.PgSQL as dbapi

from Gnumed.pycommon import gmI18N, gmLog
# this is, what makes the difference:
# likely because it somehow changes which encoding
# Python thinks comes back from file.read()
gmI18N.activate_locale()

__license__ = "GPL"
dsn = "::gnumed_v2:any-doc:any-doc"
fname = sys.argv[1]
encodings = 'win1250 win1252 latin1 iso-8859-15 sql_ascii latin9'.split()
_log = gmLog.gmDefLog

_log.Log(gmLog.lInfo, 'running on:')
_log.Log(gmLog.lInfo, sys.version)
_log.Log(gmLog.lInfo, sys.platform)
conn = dbapi.connect(dsn=dsn)
_log.Log(gmLog.lInfo, conn.version)
conn.close()
del conn

_log.Log(gmLog.lInfo, 'importing: [%s]' % fname)

for encoding in encodings:

	print "encoding:", encoding

	_log.Log(gmLog.lInfo, "----------------------------------------------")
	_log.Log(gmLog.lInfo, "testing encoding: [%s]" % encoding)

	_log.Log(gmLog.lInfo, "Python string encoding [%s]" % sys.getdefaultencoding())

	# reading file
	_log.Log(gmLog.lInfo, "os.path.getsize(%s): [%s]" % (fname, os.path.getsize(fname)))
	f = file(fname, "rb")
	img_data = f.read()
	f.close()
	_log.Log(gmLog.lInfo, "type(img_data): [%s]" % type(img_data))
	_log.Log(gmLog.lInfo, "len(img_data) : [%s]" % len(img_data))
	img_obj = dbapi.PgBytea(img_data)
	del(img_data)
	_log.Log(gmLog.lInfo, "len(img_obj) : [%s]" % len(str(img_obj)))
	_log.Log(gmLog.lInfo, "type(img_obj): [%s]" % type(img_obj))

	# setting connection level client encoding
	try:
		conn = dbapi.connect(dsn=dsn, client_encoding = (encoding, 'strict'), unicode_results=0)
		curs = conn.cursor()
		cmd = "set client_encoding to '%s'" % encoding
		curs.execute(cmd)
		curs.close()
	except:
		_log.Log(gmLog.lInfo, "cannot set encoding [%s] in dbapi.connect()" % encoding)
		conn = dbapi.connect(dsn=dsn)

	curs = conn.cursor()

	try:
		# import data
		cmd = "create table test (data bytea)"
		curs.execute(cmd)
		cmd = "insert into test (data) values (%s)"
		curs.execute(cmd, img_obj)
		cmd = "select octet_length(data) from test"
		curs.execute(cmd)
		_log.Log(gmLog.lInfo, "INSERTed octet_length(test.data): [%s]" % curs.fetchall()[0][0])
		cmd = "update test set data=%s"
		curs.execute(cmd, img_obj)
		cmd = "select octet_length(data) from test"
		curs.execute(cmd)
		_log.Log(gmLog.lInfo, "UPDATEd octet_length(test.data): [%s]" % curs.fetchall()[0][0])
	except:
		_log.LogException('cannot test encoding [%s]' % encoding)

	# finish
	conn.rollback()
	curs.close()
	conn.close()

#=======================================================================
# $Log: test-bytea-import.py,v $
# Revision 1.2  2006-08-29 22:18:28  ncq
# - improve
#
# Revision 1.1  2006/07/01 08:43:58  ncq
# - first version
#
#
