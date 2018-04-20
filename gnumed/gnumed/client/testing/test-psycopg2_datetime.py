# =======================================================================
__version__ = "$Revision: 1.1 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'
# =======================================================================

import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
print locale.getlocale()

print "testing psycopg2 date/time parsing"

import datetime as pydt

# just to make sure it exists as we use it in GNUmed
import mx.DateTime as mxDT

import psycopg2
print "psycopg2:", psycopg2.__version__

# =======================================================================
class cAdapterPyDateTime(object):

	def __init__(self, dt):
		if dt.tzinfo is None:
			raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % _timestamp_template % dt.isoformat())
		self.__dt = dt

	def getquoted(self):
		#return (_timestamp_template % self.__dt.isoformat()).replace(',', '.')
		return _timestamp_template % self.__dt.isoformat()
# -----------------------------------------------------------------------
class cAdapterMxDateTime(object):

	def __init__(self, dt):
		if dt.tz == '???':
			_log.info('[%s]: no time zone string available in (%s), assuming local time zone', self.__class__.__name__, dt)
		self.__dt = dt

	def getquoted(self):
		return mxDT.ISO.str(self.__dt).replace(',', '.')
# -----------------------------------------------------------------------
# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
import psycopg2.extensions

psycopg2.extensions.register_adapter(pydt.datetime, cAdapterPyDateTime)

try:
	import mx.DateTime as mxDT
	#psycopg2.extensions.register_adapter(mxDT.DateTimeType, cAdapterMxDateTime)
	psycopg2.extensions.register_type(psycopg2._psycopg.MXDATETIME)
except ImportError:
	_log.warning('cannot import mx.DateTime')
#=======================================================================

dsn = 'dbname=gnumed_v9 host=publicdb.gnumed.de port=5432 user=any-doc password=any-doc sslmode=prefer'
print dsn

import psycopg2.extras
conn = psycopg2.connect(dsn=dsn, connection_factory=psycopg2.extras.DictConnection)
#conn = psycopg2.connect(dsn=dsn)

now = mxDT.now()
print now
print '%s' % now
print mxDT.ISO.str(now)

#mxDT.ISO.str(now).replace(',', '.')

cmd = """select * from dem.v_staff where db_user = CURRENT_USER"""
curs = conn.cursor()
curs.execute(cmd)
data = curs.fetchall()
print data
curs.close()
conn.close()

print "success"

# =======================================================================
