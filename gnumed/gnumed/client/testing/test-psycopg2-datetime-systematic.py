# =======================================================================
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'
# =======================================================================

print "testing psycopg2 date/time parsing"

import psycopg2
print "psycopg2:", psycopg2.__version__

dsn = 'dbname=template1 user=xxx password=xxx'
dsn = 'you need to adjust this'
#dsn = u'dbname=gnumed_v21 user=any-doc password=any-doc'
print "DSN:", dsn

conn = psycopg2.connect(dsn=dsn)

curs = conn.cursor()
cmd = """
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
	cmd = "set timezone to '%s'" % tz
	try:
		curs.execute(cmd)
	except Exception, e:
		print "cannot SET time zone to", row
		curs.close()
		conn.rollback()
		continue

	cmd = """select '1920-01-19 23:00:00+01'::timestamp with time zone"""
	try:
		curs.execute(cmd)
		curs.fetchone()
		print "%s (%s / %s / %s) works" % (tz, row[1], row[2], row[3])
	except Exception, e:
		print "%s (%s / %s / %s) failed in SELECT" % (tz, row[1], row[2], row[3])
		print " ", e

	curs.close()
	conn.rollback()

conn.close()

# =======================================================================
