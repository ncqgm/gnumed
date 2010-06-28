# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/testing/test-psycopg2-datetime-systematic.py,v $
__version__ = "$Revision: 1.4 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'
# =======================================================================

print "testing psycopg2 date/time parsing"

import psycopg2
print "psycopg2:", psycopg2.__version__

dsn = u'dbname=template1 user=xxx password=xxx'
dsn = u'you need to adjust this'
#dsn = u'dbname=gnumed_v14 user=any-doc password=any-doc'
print "DSN:", dsn

conn = psycopg2.connect(dsn=dsn)

curs = conn.cursor()
cmd = u"""
select
	name,
	abbrev,
	utc_offset,
	case when
		is_dst then 'DST'
		else 'non-DST'
	end
from pg_timezone_names"""
curs.execute(cmd)
rows = curs.fetchall()
curs.close()
conn.rollback()

for row in rows:

	curs = conn.cursor()

	tz = row[0]
	cmd = u"set timezone to '%s'" % tz
	try:
		curs.execute(cmd)
	except StandardError, e:
		print "cannot SET time zone to", row
		curs.close()
		conn.rollback()
		continue

	cmd = u"""select '1920-01-19 23:00:00+01'::timestamp with time zone"""
	try:
		curs.execute(cmd)
		curs.fetchone()
		print "%s (%s / %s / %s) works" % (tz, row[1], row[2], row[3])
	except StandardError, e:
		print "%s (%s / %s / %s) failed in SELECT" % (tz, row[1], row[2], row[3])
		print " ", e

	curs.close()
	conn.rollback()

conn.close()

# =======================================================================
# $Log: test-psycopg2-datetime-systematic.py,v $
# Revision 1.4  2010-02-02 13:53:51  ncq
# - bump db version
#
# Revision 1.3  2009/08/24 20:11:27  ncq
# - bump db version
# - fix tag creation
# - provider inbox:
# 	enable filter-to-active-patient,
# 	listen to new signal,
# 	use cInboxMessage class
# - properly constrain LOINC phrasewheel SQL
# - include v12 scripts in release
# - install arriba jar to /usr/local/bin/
# - check for table existence in audit schema generator
# - include dem.message inbox with additional generic signals
#
# Revision 1.2  2009/04/14 17:55:59  ncq
# - impoved output
#
# Revision 1.1  2009/02/10 18:45:32  ncq
# - psycopg2 cannot parse a bunch of settable time zones
#
# Revision 1.1  2009/02/10 13:57:03  ncq
# - test for psycopg2 on Ubuntu-Intrepid
#