"""GNUmed PostgreSQL connection handling.

TODO: iterator/generator batch fetching:
	- http://groups-beta.google.com/group/comp.lang.python/msg/7ff516d7d9387dad
	- search Google for "Geneator/Iterator Nesting Problem - Any Ideas? 2.4"

winner:
def resultset_functional_batchgenerator(cursor, size=100):
	for results in iter(lambda: cursor.fetchmany(size), []):
		for rec in results:
			yield rec
"""
# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmPG2.py,v $
__version__ = "$Revision: 1.28 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import time, locale, sys, re, os, codecs, types, datetime


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmLoginInfo, gmExceptions, gmDateTime

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


# 3rd party
try:
	import psycopg2 as dbapi
except ImportError:
	_log.LogException("Python database adapter psycopg2 not found.", sys.exc_info(), verbose=1)
	print "CRITICAL ERROR: Cannot find module psycopg2 for connecting to the database server."
	raise

_log.Log(gmLog.lData, 'psycopg2 version: %s' % dbapi.__version__)
_log.Log(gmLog.lInfo, 'PostgreSQL via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
if not (float(dbapi.apilevel) >= 2.0):
	raise ImportError('gmPG2: supported DB-API level too low')
if not (dbapi.threadsafety > 0):
	raise ImportError('gmPG2: lacking minimum thread safety in psycopg2')
if not (dbapi.paramstyle == 'pyformat'):
	raise ImportError('gmPG2: lacking pyformat (%%(<name>)s style) placeholder support in psycopg2')
try:
	dbapi.__version__.index('dt')
except ValueError:
	raise ImportError('gmPG2: lacking datetime support in psycopg2')
try:
	dbapi.__version__.index('ext')
except ValueError:
	raise ImportError('gmPG2: lacking extensions support in psycopg2')
try:
	dbapi.__version__.index('pq3')
except ValueError:
	raise ImportError('gmPG2: lacking v3 backend protocol support in psycopg2')

import psycopg2.extras
import psycopg2.extensions

# =======================================================================
#_default_client_encoding = 'UNICODE'
_default_client_encoding = 'UTF8'
_log.Log(gmLog.lInfo, 'assuming default client encoding of [%s]' % _default_client_encoding)

# default time zone for connections
if gmDateTime.current_iso_timezone_string is None:
	gmDateTime.init()
_default_client_timezone = gmDateTime.current_iso_timezone_string
_log.Log(gmLog.lInfo, 'assuming default client time zone of [%s]' % _default_client_timezone)

# MUST NOT be uniocde or else getquoted will not work
_timestamp_template = "cast('%s' as timestamp with time zone)"
FixedOffsetTimezone = dbapi.tz.FixedOffsetTimezone

_default_dsn = None
_default_login = None

postgresql_version_string = None
postgresql_version = None			# accuracy: major.minor

# =======================================================================
# global data
# =======================================================================

known_schema_hashes = {
	'devel': 'not released, testing only',
	'v2': 'b09d50d7ed3f91ddf4c4ddb8ea507720',
	'v3': 'e73718eaf230d8f1d2d01afa8462e176',
	'v4': 'v4 not released'
}

map_schema_hash2version = {
	'b09d50d7ed3f91ddf4c4ddb8ea507720': 'v2',
	'e73718eaf230d8f1d2d01afa8462e176': 'v3'
}

# get columns and data types for a given table
query_table_col_defs = u"""select
	cols.column_name,
	cols.udt_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

query_table_attributes = u"""select
	cols.column_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

# =======================================================================
# module globals API
# =======================================================================
def set_default_client_encoding(encoding = None):
	# check whether psycopg2 can handle this encoding
	if encoding not in psycopg2.extensions.encodings:
		raise ValueError('psycopg2 does not know how to handle (wire) client encoding [%s]' % encoding)
	# check whether Python can handle this encoding
	py_enc = psycopg2.extensions.encodings[encoding]
	try:
		codecs.lookup(py_enc)
	except LookupError:
		_log.Log(gmLog.lWarn, '<codecs> module can NOT handle encoding [psycopg2::<%s> -> Python::<%s>]' % (encoding, py_enc))
		raise
	# FIXME: check encoding against the database
	# FIXME: - but we may not yet have access
	# FIXME: - psycopg2 will pull its encodings from the database eventually
	# it seems save to set it
	global _default_client_encoding
	_log.Log(gmLog.lInfo, 'setting default client encoding from [%s] to [%s]' % (_default_client_encoding, str(encoding)))
	_default_client_encoding = encoding
	return True
#---------------------------------------------------
def set_default_client_timezone(timezone = None):
	# FIXME: verify against database before setting
	global _default_client_timezone
	_log.Log(gmLog.lInfo, 'setting default client time zone from [%s] to [%s]' % (_default_client_timezone, timezone))
	_default_client_timezone = timezone
	return True
# =======================================================================
# login API
# =======================================================================
def __prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#---------------------------------------------------
def __request_login_params_tui():
	"""Text mode request of database login parameters"""
	import getpass
	login = gmLoginInfo.LoginInfo('', '', '')

	print "\nPlease enter the required login parameters:"
	try:
		host = __prompted_input("host ['' = non-TCP/IP]: ", '')
		database = __prompted_input("database [gnumed_v3]: ", 'gnumed_v3')
		user = __prompted_input("user name: ", '')
		password = getpass.getpass("password (not shown): ")
		port = __prompted_input("port [5432]: ", 5432)
	except KeyboardInterrupt:
		_log.Log(gmLog.lWarn, "user cancelled text mode login dialog")
		print "user cancelled text mode login dialog"
		raise gmExceptions.ConnectionError(_("Cannot connect to database without login information!"))

	login.SetInfo(user, password, dbname=database, host=host, port=port)
	return login
#---------------------------------------------------
def __request_login_params_gui_wx():
	"""GUI (wx) input request for database login parameters.

	Returns gmLoginInfo.LoginInfo object
	"""
	import wx
	# OK, wxPython was already loaded. But has the main Application instance
	# been initialized yet ? if not, the exception will kick us out
	if wx.GetApp() is None:
		raise gmExceptions.NoGuiError(_("The wxPython GUI framework hasn't been initialized yet!"))

	# Let's launch the login dialog
	# if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmLoginDialog
	dlg = gmLoginDialog.LoginDialog(None, -1)
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo()
	dlg.Destroy()
	del gmLoginDialog

	#if user cancelled or something else went wrong, raise an exception
	if login is None:
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

	return login
#---------------------------------------------------
def request_login_params():
	"""Request login parameters for database connection.
	"""
	# are we inside X ?
	# (if we aren't wxGTK will crash hard at
	# C-level with "can't open Display")
	if os.environ.has_key('DISPLAY'):
		# try GUI
		try:
			return __request_login_params_gui_wx()
		except:
			pass
	# well, either we are on the console or
	# wxPython does not work, use text mode
	return __request_login_params_tui()

# =======================================================================
# DSN API
# -----------------------------------------------------------------------
def make_psycopg2_dsn(database=None, host=None, port=5432, user=None, password=None):
	dsn_parts = []

	if (database is not None) and (database.strip() != ''):
		dsn_parts.append('dbname=%s' % database)

	if (host is not None) and (host.strip() != ''):
		dsn_parts.append('host=%s' % host)

	if (port is not None) and (str(port).strip() != ''):
		dsn_parts.append('port=%s' % port)

	if (user is not None) and (user.strip() != ''):
		dsn_parts.append('user=%s' % user)

	if (password is not None) and (password.strip() != ''):
		dsn_parts.append('password=%s' % password)

	return ' '.join(dsn_parts)
# ------------------------------------------------------
def get_default_login():
	# make sure we do have a login
	get_default_dsn()
	return _default_login
# ------------------------------------------------------
def get_default_dsn():
	global _default_dsn
	if _default_dsn is not None:
		return _default_dsn

	login = request_login_params()
	set_default_login(login=login)

	return _default_dsn
# ------------------------------------------------------
def set_default_login(login=None):
	if login is None:
		return False

	global _default_login
	_default_login = login
	_log.Log(gmLog.lInfo, 'setting default login from [%s] to [%s]' % (_default_login, login))

	global _default_dsn
	dsn = make_psycopg2_dsn(login.database, login.host, login.port, login.user, login.password)
	_default_dsn = dsn
	_log.Log(gmLog.lInfo, 'setting default DSN from [%s] to [%s]' % (_default_dsn, dsn))

	return True
# =======================================================================
# netadata API
# =======================================================================
def database_schema_compatible(link_obj=None, version=None):
	expected_hash = known_schema_hashes[version]
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': u'select md5(gm_concat_table_structure()) as md5'}])
	if rows[0]['md5'] != expected_hash:
		_log.Log(gmLog.lErr, 'database schema version mismatch')
		_log.Log(gmLog.lErr, 'expected: %s (%s)' % (version, expected_hash))
		_log.Log(gmLog.lErr, 'detected: %s (%s)' % (get_schema_version(link_obj=link_obj), rows[0]['md5']))
		return False
	_log.Log(gmLog.lInfo, 'detected schema version [%s], hash [%s]' % (map_schema_hash2version[rows[0]['md5']], rows[0]['md5']))
	return True
#------------------------------------------------------------------------
def get_schema_version(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select md5(gm_concat_table_structure()) as md5'}])
	try:
		return map_schema_hash2version[rows[0]['md5']]
	except KeyError:
		return u'unknown database schema version, MD5 hash is [%s]' % rows[0]['md5']
#------------------------------------------------------------------------
def get_current_user():
	rows, idx = run_ro_queries(queries = [{'cmd': u'select CURRENT_USER'}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_child_tables(schema='public', table=None):
	"""Return child tables of <table>."""
	cmd = u"""
select
	pgn.nspname as namespace,
	pgc.relname as table
from
	pg_namespace pgn,
	pg_class pgc
where
	pgc.relnamespace = pgn.oid
		and
	pgc.oid in (
		select inhrelid from pg_inherits where inhparent = (
			select oid from pg_class where
				relnamespace = (select oid from pg_namespace where nspname = %(schema)s) and
				relname = %(table)s
		)
	)"""
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'schema': schema, 'table': table}}])
	return rows
#------------------------------------------------------------------------
def table_exists(link_obj=None, schema=None, table=None):
	"""Returns false, true."""
	cmd = u"""
select exists (
	select 1 from information_schema.tables
	where
		table_schema = %s and
		table_name = %s and
		table_type = 'BASE TABLE'
)"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': (schema, table)}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_col_indices(cursor = None):
	if cursor.description is None:
		_log.Log(gmLog.lErr, 'no result description available: unused cursor or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in cursor.description:
		col_indices[col_desc[0]] = col_index
		col_index += 1
	return col_indices
#------------------------------------------------------------------------
def get_col_defs(link_obj=None, schema='public', table=None):
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_col_defs, 'args': (schema, table)}])
	col_names = []
	col_type = {}
	for row in rows:
		col_names.append(row[0])
		# map array types
		if row[1].startswith('_'):
			col_type[row[0]] = row[1][1:] + '[]'
		else:
			col_type[row[0]] = row[1]
	col_defs = []
	col_defs.append(col_names)
	col_defs.append(col_type)
	return col_defs
#------------------------------------------------------------------------
def get_col_names(link_obj=None, schema='public', table=None):
	"""Return column attributes of table"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_attributes, 'args': (schema, table)}])
	cols = []
	for row in rows:
		cols.append(row[0])
	return cols
# =======================================================================
# query runners
# =======================================================================
def run_ro_queries(link_obj=None, queries=None, verbose=False, return_data=True, get_col_idx=False):
	"""Run read-only queries.

	<queries> must be a list of dicts:
		[
			{'cmd': <string>, 'args': <dict> or <tuple>},
			{...},
			...
		]
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		_log.Log(gmLog.lData, 'link object: %s' % link_obj)
		curs = link_obj
		curs_close = __noop
		conn_close = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		conn_close = __noop
	elif link_obj is None:
		conn = get_connection(readonly=True, verbose=verbose)
		conn_close = conn.close
		curs = conn.cursor()
		curs_close = curs.close
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	if verbose:
		_log.Log(gmLog.lData, 'cursor: %s' % curs)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "run_ro_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = (None,)
#		if verbose:		# mogrify does not support unicode queries, yet
#			_log.Log(gmLog.lData, 'running: %s' % curs.mogrify(query['cmd'], args))
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				_log.Log(gmLog.lData, 'ran query: [%s]' % curs.query)
				_log.Log(gmLog.lData, 'PG status message: %s' % curs.statusmessage)
				_log.Log(gmLog.lData, 'cursor description: %s' % curs.description)
		except:
			_log.Log(gmLog.lErr, 'query failed: [%s]' % curs.query)
			_log.Log(gmLog.lErr, 'PG status message: %s' % curs.statusmessage)
			curs_close()
			conn_close()
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if get_col_idx:
			col_idx = get_col_indices(curs)
		if verbose:
			_log.Log(gmLog.lData, 'last query returned [%s (%s)] rows' % (curs.rowcount, len(data)))
			_log.Log(gmLog.lData, 'cursor description: %s' % curs.description)

	curs_close()
	conn_close()
	return (data, col_idx)
#------------------------------------------------------------------------
def run_rw_queries(link_obj=None, queries=None, end_tx=False, return_data=None, get_col_idx=False, verbose=False):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	<link_obj>
		can be either:
		- a cursor
		- a connection

	<queries>
		is a list of dicts [{'cmd': <string>, 'args': <dict> or <tuple>)
		to be executed as a single transaction, the last
		query may usefully return rows (such as a
		"select currval('some_sequence')" statement)

	<end_tx>
		- controls whether the transaction is finalized (eg.
		  committed/rolled back) or not, this allows the
		  call to run_commit2() to be part of a framing
		  transaction
		- if link_obj is a connection then <end_tx> will
		  default to False unless it is explicitely set to
		  True which is taken to mean "yes, you do have full
		  control over the transaction" in which case the
		  transaction is properly finalized
		- if link_obj is a cursor we CANNOT finalize the
		  transaction because we would need the connection for that

	<return_data>
		- if true, the returned data will include the rows
		  the last query selected
		- if false, it returns None instead

	<get_col_idx>
		- if true, the returned data will include a dictionary
		  mapping field names to column positions
		- if false, the returned data returns None instead

	method result:
		- returns a tuple (data, idx)
		- <data>:
			* (None, None) if last query did not return rows
			* ("fetchall() result", <index>) if last query returned any rows
			* for <index> see <get_col_idx>
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		conn_close = __noop
		conn_commit = __noop
		conn_rollback = __noop
		curs = link_obj
		curs_close = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		conn_close = __noop
		if end_tx:
			conn_commit = link_obj.commit
			conn_rollback = link_obj.rollback
		else:
			conn_commit = __noop
			conn_rollback = __noop
		curs = link_obj.cursor()
		curs_close = curs.close
	elif link_obj is None:
		conn = get_connection(readonly=False)
		conn_close = conn.close
		conn_commit = conn.commit
		conn_rollback = conn.rollback
		curs = conn.cursor()
		curs_close = curs.close
	else:
		raise ValueError('link_obj must be cursor, connection or None and not [%s]' % link_obj)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "run_ro_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = (None,)
		try:
			curs.execute(query['cmd'], args)
		except:
			curs_close()
			conn_rollback()
			conn_close()
			raise

	data = None
	col_idx = None
	if return_data:
		try:
			data = curs.fetchall()
		except:
			curs_close()
			conn_rollback()
			conn_close()
			raise
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	conn_commit()
	conn_close()

	return (data, col_idx)
# =======================================================================
def get_raw_connection(dsn=None, verbose=False):
	"""Get a raw, unadorned connection.

	- this will not set any parameters such as encoding, timezone, rw/ro, datestyle
	- the only requirement is a valid DSN
	- hence it can be used for "service" connections
	  for verifying encodings etc
	"""
	# FIXME: support verbose

	if dsn is None:
		dsn = get_default_dsn()

	try:
		conn = dbapi.connect(dsn=dsn, connection_factory=psycopg2.extras.DictConnection)
	except dbapi.OperationalError:
		t, v, tb = sys.exc_info()
		if str(v).find('fe_sendauth') != -1:
			raise cAuthenticationError, (dsn, v), tb
		if str(v).find('authentication failed for user') != -1:
			raise cAuthenticationError, (dsn, v), tb
		if re.search('user ".*" does not exist', str(v)) is not None:
			raise cAuthenticationError, (dsn, v), tb
		raise

	global postgresql_version
	if postgresql_version is None:
		curs = conn.cursor()
		curs.execute("""
			select
				(split_part(setting, '.', 1) || '.' || split_part(setting, '.', 2))::numeric as version
			from pg_settings
			where name='server_version'"""
		)
		postgresql_version = curs.fetchone()['version']
		curs.close()
		conn.commit()
		_log.Log(gmLog.lInfo, 'PostgreSQL version (numeric): %s' % postgresql_version)

	return conn
# =======================================================================
def get_connection(dsn=None, readonly=True, encoding=None, verbose=False, pooled=True):
	"""Get a new connection.

	This assumes the locale system has been initialzied
	unless an encoding is specified.
	"""
	# FIXME: support pooled, verbose

	conn = get_raw_connection(dsn=dsn, verbose=verbose)

	if encoding is None:
		encoding = _default_client_encoding
	if encoding is None:
		encoding = locale.getlocale()[1]
		_log.Log(gmLog.lWarn, 'client encoding not specified')
		_log.Log(gmLog.lWarn, 'the string encoding currently set in the active locale is used: [%s]' % encoding)
		_log.Log(gmLog.lWarn, 'for this to work the application MUST have called locale.setlocale() before')

	# set connection properties
	# 1) client encoding
	_log.Log(gmLog.lData, 'client string encoding [%s]' % encoding)
	try:
		conn.set_client_encoding(encoding)
	except dbapi.OperationalError:
		t, v, tb = sys.exc_info()
		if str(v).find("can't set encoding to") != -1:
			raise cEncodingError, (encoding, v), tb
		raise

	# 2) transaction isolation level
	if readonly:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
		_log.Log(gmLog.lData, 'isolation level [read committed]')
	else:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		_log.Log(gmLog.lData, 'isolation level [serializable]')

	curs = conn.cursor()

	# 3) client time zone
	_log.Log(gmLog.lData, 'time zone [%s]' % _default_client_timezone)
	cmd = "set time zone interval '%s' hour to minute" % _default_client_timezone
	curs.execute(cmd)

	# 4) datestyle
	# FIXME: add DMY/YMD handling
	_log.Log(gmLog.lData, 'datestyle [ISO]')
	cmd = "set datestyle to 'ISO'"
	curs.execute(cmd)

	# 5) access mode
	if readonly:
		access_mode = 'READ ONLY'
	else:
		access_mode = 'READ WRITE'
	_log.Log(gmLog.lData, 'access mode [%s]' % access_mode)
	cmd = 'set session characteristics as transaction %s' % access_mode
	curs.execute(cmd)

	# version string
	global postgresql_version_string
	if postgresql_version_string is None:
		curs.execute('select version()')
		postgresql_version_string = curs.fetchone()['version']
		_log.Log(gmLog.lInfo, 'PostgreSQL version (string): "%s"' % postgresql_version_string)

	curs.close()
	conn.commit()
	return conn
# =======================================================================
# internal helpers
# -----------------------------------------------------------------------
def __noop():
	pass
# -----------------------------------------------------------------------
def __log_PG_settings(curs=None):
	# don't use any of the run_*()s since that might
	# create a loop if we fail here
	try:
		curs.execute(u'show all')
	except:
		_log.LogException("cannot log PG settings (>>>show all<<< failed)", sys.exc_info(), verbose = 0)
		return False
	settings = curs.fetchall()
	if settings is None:
		_log.Log(gmLog.lErr, 'cannot log PG settings (>>>show all<<< did not return rows)')
		return False
	for setting in settings:
		_log.Log(gmLog.lData, "PG option [%s]: %s" % (setting[0], setting[1]))
	return True
# =======================================================================
class cAuthenticationError(dbapi.OperationalError):

	def __init__(self, dsn=None, prev_val=None):
		self.dsn = dsn
		self.prev_val = prev_val

	def __str__(self):
		return 'PostgreSQL: %sDSN: %s' % (self.prev_val, self.dsn)

# =======================================================================
class cEncodingError(dbapi.OperationalError):

	def __init__(self, encoding=None, prev_val=None):
		self.encoding = encoding
		self.prev_val = prev_val

	def __str__(self):
		return 'PostgreSQL: %s\nencoding: %s' % (self.prev_val, self.encoding)
# =======================================================================
class cAdapterPyDateTime(object):

	def __init__(self, dt):
		if dt.tzinfo is None:
			raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % _timestamp_template % dt.isoformat())
		self.__dt = dt

	def getquoted(self):
		return _timestamp_template % self.__dt.isoformat().replace(',', '.')
# -----------------------------------------------------------------------
class cAdapterMxDateTime(object):

	def __init__(self, dt):
		if dt.tz == '???':
			raise ValueError('mx.DateTime instance is lacking a time zone: [%s]' % _timestamp_template % dt)
		self.__dt = dt

	def getquoted(self):
		return (_timestamp_template % self.__dt).replace(',', '.')
# =======================================================================
#  main
# -----------------------------------------------------------------------

# make sure psycopg2 knows how to handle unicode ...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

# properly adapt *tuples* into (a, b, c, ...) in "... IN ..." queries
psycopg2.extensions.register_adapter(tuple, psycopg2.extras.SQL_IN)

# do NOT adapt *lists* to "... IN (*) ..." syntax because we want
# them adapted to "... ARRAY()..." so we can support PG arrays
#psycopg2.extensions.register_adapter(list, psycopg2.extras.SQL_IN)

# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
psycopg2.extensions.register_adapter(datetime.datetime, cAdapterPyDateTime)
try:
	psycopg2.extensions.register_adapter(mxDT.DateTimeType, cAdapterMxDateTime)
except:
	pass

if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

	gmDateTime.init()

	#--------------------------------------------------------------------
	def test_get_connection():
		print "testing get_connection()"

		dsn = 'foo'
		try:
			conn = get_connection(dsn=dsn)
		except dbapi.OperationalError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v3'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v3 user=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v3 user=any-doc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v3 user=any-doc password=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v3 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=True)

		dsn = 'dbname=gnumed_v3 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=False)

		dsn = 'dbname=gnumed_v3 user=any-doc password=any-doc'
		encoding = 'foo'
		try:
			conn = get_connection(dsn=dsn, encoding=encoding)
		except cEncodingError:
			print "SUCCESS: get_connection(%s, %s) failed as expected" % (dsn, encoding)
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v
	#--------------------------------------------------------------------
	def test_exceptions():
		print "testing exceptions"

		try:
			raise cAuthenticationError('no dsn', 'no previous exception')
		except cAuthenticationError:
			t, v, tb = sys.exc_info()
			print t
			print v
			print tb

		try:
			raise cEncodingError('no dsn', 'no previous exception')
		except cEncodingError:
			t, v, tb = sys.exc_info()
			print t
			print v
			print tb
	#--------------------------------------------------------------------
	def test_ro_queries():
		print "testing run_ro_queries()"

		dsn = 'dbname=gnumed_v3 user=any-doc password=any-doc'
		conn = get_connection(dsn, readonly=True)

		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'select version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx
		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'select 1'}], return_data=True, get_col_idx=True)
		print data
		print idx

		curs = conn.cursor()

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'select version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'select 1'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx

		try:
			data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'selec 1'}], return_data=True, get_col_idx=True, verbose=True)
			print data
			print idx
		except psycopg2.ProgrammingError:
			print 'SUCCESS: run_ro_queries("selec 1") failed as expected'
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		curs.close()
	#--------------------------------------------------------------------
	def test_request_dsn():
		conn = get_connection()
		print conn
		conn.close()
	#--------------------------------------------------------------------
	def test_set_encoding():
		print "testing set_default_client_encoding()"

		enc = 'foo'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = ''
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'latin1'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'utf8'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'unicode'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		enc = 'UNICODE'
		try:
			set_default_client_encoding(enc)
			print "SUCCESS: encoding [%s] worked" % enc
		except ValueError:
			print "SUCCESS: set_default_client_encoding(%s) failed as expected" % enc
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v
	#--------------------------------------------------------------------
	# run tests
	test_get_connection()
	test_exceptions()
	test_ro_queries()
	test_request_dsn()
	test_set_encoding()
	print "tests ran successfully"

# =======================================================================
# $Log: gmPG2.py,v $
# Revision 1.28  2007-01-04 22:51:10  ncq
# - change hash for unreleased v4
#
# Revision 1.27  2007/01/03 11:54:16  ncq
# - log successful schema hash, too
#
# Revision 1.26  2007/01/02 19:47:29  ncq
# - support (and use) <link_obj> in get_schema_version()
#
# Revision 1.25  2007/01/02 16:17:13  ncq
# - slightly improved logging
# - fix fatal typo in set_default_login()
# - add <link_obj> support to database_schema_compatible()
# - really apply end_tx to run_rw_queries !
#
# Revision 1.24  2006/12/29 16:25:35  ncq
# - add PostgreSQL version handling
#
# Revision 1.23  2006/12/27 16:41:15  ncq
# - make sure python datetime adapter does not put ',' into string
#
# Revision 1.22  2006/12/22 16:54:44  ncq
# - init gmDateTime if necessary
#
# Revision 1.21  2006/12/21 17:44:54  ncq
# - use gmDateTime.current_iso_timezone_*string* as that is ISO conformant
#
# Revision 1.20  2006/12/21 10:52:52  ncq
# - fix test suite
# - set default client encoding to "UTF8" which is more precise than "UNICODE"
# - use gmDateTime for timezone handling thereby fixing the time.daylight error
#
# Revision 1.19  2006/12/18 17:39:55  ncq
# - make v3 database have known hash
#
# Revision 1.18  2006/12/18 14:55:40  ncq
# - u''ify a query
#
# Revision 1.17  2006/12/15 15:23:50  ncq
# - improve database_schema_compatible()
#
# Revision 1.16  2006/12/12 13:14:32  ncq
# - u''ify queries
#
# Revision 1.15  2006/12/06 20:32:09  ncq
# - careful about port.strip()
#
# Revision 1.14  2006/12/06 16:06:30  ncq
# - cleanup
# - handle empty port def in make_psycopg2_dsn()
# - get_col_defs()
# - get_col_indices()
# - get_col_names()
# - table_exists()
#
# Revision 1.13  2006/12/05 13:58:45  ncq
# - add get_schema_version()
# - improve handling of known schema hashes
# - register UNICODEARRAY psycopg2 extension
#
# Revision 1.12  2006/11/24 09:51:16  ncq
# - whitespace fix
#
# Revision 1.11  2006/11/14 16:56:23  ncq
# - improved (and documented) rationale for registering SQL_IN adapter on tuples only
#
# Revision 1.10  2006/11/07 23:52:48  ncq
# - register our own adapters for mx.DateTime and datetime.datetime so
#   we can solve the "ss,ms" issue in locale-aware str(timestamp)
#
# Revision 1.9  2006/11/07 00:30:36  ncq
# - activate SQL_IN for lists only
#
# Revision 1.8  2006/11/05 17:03:26  ncq
# - register SQL_INI adapter for tuples and lists
#
# Revision 1.7  2006/10/24 13:20:07  ncq
# - fix get_current_user()
# - add default login handling
# - remove set_default_dsn() - now use set_default_login() which will create the DSN, too
# - slighly less verbose logging for log size sanity
#
# Revision 1.6  2006/10/23 13:22:38  ncq
# - add get_child_tables()
#
# Revision 1.5  2006/10/10 07:38:22  ncq
# - tighten checks on psycopg2 capabilities
#
# Revision 1.4  2006/10/08 09:23:40  ncq
# - default encoding UNICODE, not utf8
# - add database_schema_compatible()
# - smartify set_default_client_encoding()
# - support <verbose> in run_ro_queries()
# - non-fatally warn on non-unicode queries
# - register unicode type so psycopg2 knows how to deal with u''
# - improve test suite
#
# Revision 1.3  2006/09/30 11:57:48  ncq
# - document get_raw_connection()
#
# Revision 1.2  2006/09/30 11:52:40  ncq
# - factor out get_raw_connection()
# - reorder conecction customization in get_connection()
#
# Revision 1.1  2006/09/21 19:18:35  ncq
# - first psycopg2 version
#
#