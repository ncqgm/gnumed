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
__version__ = "$Revision: 1.64 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import time, locale, sys, re as regex, os, codecs, types, datetime, logging


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLoginInfo, gmExceptions, gmDateTime, gmBorg


_log = logging.getLogger('gnumed.database')
_log.info(__version__)


# 3rd party
try:
	import psycopg2 as dbapi
except ImportError:
	_log.exception("Python database adapter psycopg2 not found.")
	print "CRITICAL ERROR: Cannot find module psycopg2 for connecting to the database server."
	raise

_log.info('psycopg2 version: %s' % dbapi.__version__)
_log.info('PostgreSQL via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
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
import psycopg2.pool

# =======================================================================
#_default_client_encoding = 'UNICODE'
_default_client_encoding = 'UTF8'
_log.info('assuming default client encoding of [%s]' % _default_client_encoding)

# default time zone for connections
if gmDateTime.current_iso_timezone_string is None:
	gmDateTime.init()
_default_client_timezone = gmDateTime.current_iso_timezone_string
_log.info('assuming default client time zone of [%s]' % _default_client_timezone)

# MUST NOT be uniocde or else getquoted will not work
_timestamp_template = "cast('%s' as timestamp with time zone)"
FixedOffsetTimezone = dbapi.tz.FixedOffsetTimezone

_default_dsn = None
_default_login = None

postgresql_version_string = None
postgresql_version = None			# accuracy: major.minor

__ro_conn_pool = None

# =======================================================================
# global data
# =======================================================================

known_schema_hashes = {
	'devel': 'not released, testing only',
	'v2': 'b09d50d7ed3f91ddf4c4ddb8ea507720',
	'v3': 'e73718eaf230d8f1d2d01afa8462e176',
	'v4': '4428ccf2e54c289136819e701bb095ea',
	'v5': '7e7b093af57aea48c288e76632a382e5',	# old (v1) style hash
	'v6': '90e2026ac2efd236da9c8608b8685b2d',	# new (v2) style hash
	'v7': '6c9f6d3981483f8e9433df99d1947b27',
	'v8': '89b13a7af83337c3aad153b717e52360'
}

map_schema_hash2version = {
	'b09d50d7ed3f91ddf4c4ddb8ea507720': 'v2',
	'e73718eaf230d8f1d2d01afa8462e176': 'v3',
	'4428ccf2e54c289136819e701bb095ea': 'v4',
	'7e7b093af57aea48c288e76632a382e5': 'v5',
	'90e2026ac2efd236da9c8608b8685b2d': 'v6',
	'6c9f6d3981483f8e9433df99d1947b27': 'v7',
	'89b13a7af83337c3aad153b717e52360': 'v8'
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
		_log.warning('<codecs> module can NOT handle encoding [psycopg2::<%s> -> Python::<%s>]' % (encoding, py_enc))
		raise
	# FIXME: check encoding against the database
	# FIXME: - but we may not yet have access
	# FIXME: - psycopg2 will pull its encodings from the database eventually
	# it seems save to set it
	global _default_client_encoding
	_log.info('setting default client encoding from [%s] to [%s]' % (_default_client_encoding, str(encoding)))
	_default_client_encoding = encoding
	return True
#---------------------------------------------------
def set_default_client_timezone(timezone = None):
	# FIXME: verify against database before setting
	global _default_client_timezone
	_log.info('setting default client time zone from [%s] to [%s]' % (_default_client_timezone, timezone))
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
	login = gmLoginInfo.LoginInfo()

	print "\nPlease enter the required login parameters:"
	try:
		login.host = __prompted_input("host ['' = non-TCP/IP]: ", '')
		login.database = __prompted_input("database [gnumed_v8]: ", 'gnumed_v8')
		login.user = __prompted_input("user name: ", '')
		login.password = getpass.getpass("password (not shown): ")
		login.port = __prompted_input("port [5432]: ", 5432)
	except KeyboardInterrupt:
		_log.warning("user cancelled text mode login dialog")
		print "user cancelled text mode login dialog"
		raise gmExceptions.ConnectionError(_("Cannot connect to database without login information!"))

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
	import gmAuthWidgets
	dlg = gmAuthWidgets.cLoginDialog(None, -1)
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo()
	dlg.Destroy()

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

	dsn_parts.append('sslmode=prefer')

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
	_log.info('setting default login from [%s] to [%s]' % (_default_login, login))

	global _default_dsn
	dsn = make_psycopg2_dsn(login.database, login.host, login.port, login.user, login.password)
	_default_dsn = dsn
	_log.info('setting default DSN from [%s] to [%s]' % (_default_dsn, dsn))

	return True
# =======================================================================
# netadata API
# =======================================================================
def sanity_check_database_settings():
	_log.info('checking database settings')
	settings = {
		u'allow_system_table_mods': [u'off', u'system breakage'],
		u'fsync': [u'on', u'data loss/corruption'],
		u'full_page_writes': [u'on', u'data loss/corruption'],
		u'password_encryption': [u'on', u'breach of confidentiality'],
		u'regex_flavor': [u'advanced', u'query breakage'],
		u'synchronous_commit': [u'on', u'data loss/corruption'],
		u'sql_inheritance': [u'on', u'query breakage, data loss/corruption']
	}

	cmd = u"select name, setting from pg_settings where name in %(settings)s"
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'settings': tuple(settings.keys())}}])

	all_good = True
	msg = []
	for row in rows:
		if row[1] != settings[row[0]][0]:
			all_good = False
			msg.append(' option [%s] = [%s] risks "%s"' % (row[0], row[1], settings[row[0]][1]))
			_log.warning('PG option [%s] set to [%s], expected [%s], risk: <%s>' % (row[0], row[1], settings[row[0]][0], settings[row[0]][1]))

	if not all_good:
		return u'\n'.join(msg)

	return True
#------------------------------------------------------------------------
def database_schema_compatible(link_obj=None, version=None, verbose=True):
	expected_hash = known_schema_hashes[version]
	if version == 'devel':
		args = {'ver': '9999'}
	else:
		args = {'ver': version.strip('v')}
	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{
			'cmd': u'select md5(gm.concat_table_structure(%(ver)s::integer)) as md5',
			'args': args
		}]
	)
	if rows[0]['md5'] != expected_hash:
		_log.error('database schema version mismatch')
		_log.error('expected: %s (%s)' % (version, expected_hash))
		_log.error('detected: %s (%s)' % (get_schema_version(link_obj=link_obj), rows[0]['md5']))
		if verbose:
			_log.debug('schema dump follows:')
			for line in get_schema_structure(link_obj=link_obj).split():
				_log.debug(line)
		return False
	_log.info('detected schema version [%s], hash [%s]' % (map_schema_hash2version[rows[0]['md5']], rows[0]['md5']))
	return True
#------------------------------------------------------------------------
def get_schema_version(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select md5(gm.concat_table_structure()) as md5'}])
	try:
		return map_schema_hash2version[rows[0]['md5']]
	except KeyError:
		return u'unknown database schema version, MD5 hash is [%s]' % rows[0]['md5']
#------------------------------------------------------------------------
def get_schema_structure(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select gm.concat_table_structure()'}])
	return rows[0][0]
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
		_log.error('no result description available: unused cursor or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in cursor.description:
		col_name = col_desc[0]
		# a query like "select 1,2;" will return two columns of the same name !
		# hence adjust to that, note, however, that dict-style access won't work
		# on results of such queries ...
		if col_indices.has_key(col_name):
			col_name = '%s_%s' % (col_name, col_index)
		col_indices[col_name] = col_index
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
# query runners and helpers
# =======================================================================
def is_pg_interval(candidate=None):
	cmd = u'select %(candidate)s::interval'
	try:
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
		return True
	except:
		cmd = u'select %(candidate)s::text::interval'
		try:
			rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
			return True
		except:
			return False
#------------------------------------------------------------------------
def bytea2file(data_query=None, filename=None, chunk_size=0, data_size=None, data_size_query=None):
	outfile = file(filename, 'wb')
	result = bytea2file_object(data_query=data_query, file_obj=outfile, chunk_size=chunk_size, data_size=data_size, data_size_query=data_size_query)
	outfile.close()
	return result
#------------------------------------------------------------------------
def bytea2file_object(data_query=None, file_obj=None, chunk_size=0, data_size=None, data_size_query=None):
	"""Store data from a bytea field into a file.

	<data_query>
	- dict {'cmd': ..., 'args': ...}
	- 'cmd' must be unicode containing "... substring(data from %(start)s for %(size)s) ..."
	- 'args' must be a dict
	- must return one row with one field of type bytea
	<file>
	- must be a file like Python object
	<data_size>
	- integer of the total size of the expected data or None
	<data_size_query>
	- dict {'cmd': ..., 'args': ...}
	- cmd must be unicode
	- must return one row with one field with the octet_length() of the data field
	- used only when <data_size> is None
	"""
	if data_size == 0:
		return True

	# If the client sets an encoding other than the default we
	# will receive encoding-parsed data which isn't the binary
	# content we want. Hence we need to get our own connection.
	# It must be a read-write one so that we don't affect the
	# encoding for other users of the shared read-only
	# connections.
	# Actually, encodings shouldn't be applied to binary data
	# (eg. bytea types) in the first place but that is only
	# reported to be fixed > v7.4.
	# further tests reveal that at least on PG 8.0 this bug still
	# manifests itself
	conn = get_raw_connection()

	if data_size is None:
		rows, idx = run_ro_queries(link_obj = conn, queries = [data_size_query])
		data_size = rows[0][0]
		if data_size in [None, 0]:
			conn.close()
			return True

	_log.debug('expecting bytea data of size: [%s] bytes' % data_size)
	_log.debug('using chunk size of: [%s] bytes' % chunk_size)

	# chunk size of 0 means "retrieve whole field at once"
	if chunk_size == 0:
		chunk_size = data_size
		_log.debug('chunk size [0] bytes: retrieving all data at once')

	# Windoze sucks: it can't transfer objects of arbitrary size,
	# anyways, we need to split the transfer,
	# however, only possible if postgres >= 7.2
	needed_chunks, remainder = divmod(data_size, chunk_size)
	_log.debug('chunks to retrieve: [%s]' % needed_chunks)
	_log.debug('remainder to retrieve: [%s] bytes' % remainder)

	# retrieve chunks, skipped if data size < chunk size,
	# does this not carry the danger of cutting up multi-byte escape sequences ?
	# no, since bytea is binary,
	# yes, since in bytea there are *some* escaped values, still
	# no, since those are only escaped during *transfer*, not on-disk, hence
	# only complete escape sequences are put on the wire
	for chunk_id in range(needed_chunks):
		chunk_start = (chunk_id * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = chunk_size
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except:
			_log.error('cannot retrieve chunk [%s/%s], size [%s], try decreasing chunk size' % (chunk_id+1, needed_chunks, chunk_size))
			conn.close()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(str(rows[0][0]))

	# retrieve remainder
	if remainder > 0:
		chunk_start = (needed_chunks * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = remainder
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except:
			_log.error('cannot retrieve remaining [%s] bytes' % remainder)
			conn.close()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(str(rows[0][0]))

	conn.close()
	return True
#------------------------------------------------------------------------
def file2bytea(query=None, filename=None, args=None, conn=None):
	"""Store data from a file into a bytea field.

	The query must:
	- be in unicode
	- contain a format spec identifying the row (eg a primary key) matching <args>
	- contain a format spec %(data)s::bytea
	"""
	# read data from file
	infile = file(filename, "rb")
	data_as_byte_string = infile.read()
	infile.close()
	if args is None:
		args = {}
	args['data'] = buffer(data_as_byte_string)
	del(data_as_byte_string)

	# insert the data
	if conn is None:
		conn = get_raw_connection()
	run_rw_queries(link_obj=conn, queries = [{'cmd': query, 'args': args}], end_tx=True)
	conn.close()

	return
#------------------------------------------------------------------------
def sanitize_pg_regex(expression=None, escape_all=False):
	"""Escape input for use in a PostgreSQL regular expression.

	If a fragment comes from user input and is to be used
	as a regular expression we need to make sure it doesn't
	contain invalid regex patterns such as unbalanced ('s.

	<escape_all>
		True: try to escape *all* metacharacters
		False: only escape those which render the regex invalid
	"""
	return expression.replace (
			'(', '\('
		).replace (
			')', '\)'
		).replace (
			'[', '\['
		)
		#']', '\]',			# not needed
#------------------------------------------------------------------------
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
		curs = link_obj
		curs_close = __noop
		conn_close = __noop
		tx_rollback = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		conn_close = __noop
		tx_rollback = link_obj.rollback
	elif link_obj is None:
		conn = get_connection(readonly=True, verbose=verbose)
		curs = conn.cursor()
		curs_close = curs.close
		conn_close = conn.close
		tx_rollback = conn.rollback
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	if verbose:
		_log.debug('cursor: %s' % curs)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "run_ro_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				_log.debug('ran query: [%s]' % curs.query)
				_log.debug('PG status message: %s' % curs.statusmessage)
				_log.debug('cursor description: %s' % curs.description)
		except:
			curs_close()
			tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			conn_close()
			_log.error('query failed: [%s]' % curs.query)
			_log.error('PG status message: %s' % curs.statusmessage)
			_log.flush()
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if get_col_idx:
			col_idx = get_col_indices(curs)
		if verbose:
			_log.debug('last query returned [%s (%s)] rows' % (curs.rowcount, len(data)))
			_log.debug('cursor description: %s' % curs.description)

	curs_close()
	tx_rollback()		# rollback just so that we don't stay IDLE IN TRANSACTION forever
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
		  call to run_rw_queries() to be part of a framing
		  transaction
		- if link_obj is a connection then <end_tx> will
		  default to False unless it is explicitely set to
		  True which is taken to mean "yes, you do have full
		  control over the transaction" in which case the
		  transaction is properly finalized
		- if link_obj is a cursor we CANNOT finalize the
		  transaction because we would need the connection for that
		- if link_obj is None <end_tx> will, of course, always be True

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
			args = None
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
# connection handling API
# -----------------------------------------------------------------------
class cConnectionPool(psycopg2.pool.PersistentConnectionPool):
	"""
	GNUmed database connection pool.

	Extends psycopg2's PersistentConnectionPool with
	a custom _connect() function. Supports one connection
	per thread - which also ties it to one particular DSN.
	"""
	#--------------------------------------------------
	def _connect(self, key=None):

		conn = get_raw_connection(dsn = self._kwargs['dsn'], verbose = self._kwargs['verbose'])

		if key is not None:
			self._used[key] = conn
			self._rused[id(conn)] = key
		else:
			self._pool.append(conn)

		return conn
# -----------------------------------------------------------------------
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
		if regex.search('user ".*" does not exist', str(v)) is not None:
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
		_log.info('PostgreSQL version (numeric): %s' % postgresql_version)
		if verbose:
			__log_PG_settings(curs=curs)
		curs.close()
		conn.commit()
		
	conn.is_decorated = False

	return conn
# =======================================================================
def get_connection(dsn=None, readonly=True, encoding=None, verbose=False, pooled=True):
	"""Get a new connection.

	This assumes the locale system has been initialzied
	unless an encoding is specified.
	"""
	# FIXME: support pooled on RW, too
	# FIXME: for now, support the default DSN only
	if pooled and readonly and (dsn is None):
		global __ro_conn_pool
		if __ro_conn_pool is None:
			__ro_conn_pool = cConnectionPool (
				minconn = 1,
				maxconn = 2,
				dsn = dsn,
				verbose = verbose
			)
		conn = __ro_conn_pool.getconn()
		conn.close = __noop					# do not close pooled ro connections
	else:
		conn = get_raw_connection(dsn=dsn, verbose=verbose)

	if conn.is_decorated:
		return conn

	if encoding is None:
		encoding = _default_client_encoding
	if encoding is None:
		encoding = gmI18N.get_encoding()
		_log.warning('client encoding not specified')
		_log.warning('the string encoding currently set in the active locale is used: [%s]' % encoding)
		_log.warning('for this to work the application MUST have called locale.setlocale() before')

	# set connection properties
	# 1) client encoding
	_log.debug('client string encoding [%s]' % encoding)
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
		_log.debug('isolation level [read committed]')
	else:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		_log.debug('isolation level [serializable]')

	curs = conn.cursor()

	# 3) client time zone
	_log.debug('time zone [%s]' % _default_client_timezone)
	cmd = "set time zone interval '%s' hour to minute" % _default_client_timezone
	curs.execute(cmd)

	# 4) datestyle
	# regarding DMY/YMD handling: since we force *input* to
	# ISO, too, the DMY/YMD setting is not needed
	_log.debug('datestyle [ISO]')
	cmd = "set datestyle to 'ISO'"
	curs.execute(cmd)

	# 5) access mode
	if readonly:
		access_mode = 'READ ONLY'
	else:
		access_mode = 'READ WRITE'
	_log.debug('access mode [%s]' % access_mode)
	cmd = 'set session characteristics as transaction %s' % access_mode
	curs.execute(cmd)

	# 6) SQL inheritance mode
	_log.debug('sql_inheritance [on]')
	cmd = 'set sql_inheritance to on'
	curs.execute(cmd)

	# version string
	global postgresql_version_string
	if postgresql_version_string is None:
		curs.execute('select version()')
		postgresql_version_string = curs.fetchone()['version']
		_log.info('PostgreSQL version (string): "%s"' % postgresql_version_string)

	curs.close()
	conn.commit()

	conn.is_decorated = True

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
		_log.exception("cannot log PG settings (>>>show all<<< failed)")
		return False
	settings = curs.fetchall()
	if settings is None:
		_log.error('cannot log PG settings (>>>show all<<< did not return rows)')
		return False
	for setting in settings:
		_log.debug("PG option [%s]: %s" % (setting[0], setting[1]))
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
		#return (_timestamp_template % self.__dt.isoformat()).replace(',', '.')
		return _timestamp_template % self.__dt.isoformat()
# -----------------------------------------------------------------------
class cAdapterMxDateTime(object):

	def __init__(self, dt):
		if dt.tz == '???':
			_log.info('[%s]: no time zone string available in (%s), assuming local time zone' % (self.__class__.__name__, dt))
		self.__dt = dt

	def getquoted(self):
#		return (_timestamp_template % mxDT.ISO.str(self.__dt)).replace(',', '.')
		return mxDT.ISO.str(self.__dt).replace(',', '.')
# =======================================================================
#  main
# -----------------------------------------------------------------------

# make sure psycopg2 knows how to handle unicode ...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

try:
	# properly adapt *tuples* into (a, b, c, ...) in "... IN ..." queries
	psycopg2.extensions.register_adapter(tuple, psycopg2.extras.SQL_IN)
except AttributeError:
	# only needed in psycopg2 < 0.2.6
	pass

# do NOT adapt *lists* to "... IN (*) ..." syntax because we want
# them adapted to "... ARRAY()..." so we can support PG arrays
#psycopg2.extensions.register_adapter(list, psycopg2.extras.SQL_IN)

# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
psycopg2.extensions.register_adapter(datetime.datetime, cAdapterPyDateTime)
try:
	import mx.DateTime as mxDT
	psycopg2.extensions.register_adapter(mxDT.DateTimeType, cAdapterMxDateTime)
except ImportError:
	_log.warning('cannot import mx.DateTime')

if __name__ == "__main__":

	logging.basicConfig(level=logging.DEBUG)

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

		dsn = 'dbname=gnumed_v8'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v8 user=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v8 user=any-doc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v8 user=any-doc password=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v8 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=True)

		dsn = 'dbname=gnumed_v8 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=False)

		dsn = 'dbname=gnumed_v8 user=any-doc password=any-doc'
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

		dsn = 'dbname=gnumed_v8 user=any-doc password=any-doc'
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
	def test_connection_pool():
		dsn = get_default_dsn()
		pool = cConnectionPool(minconn=1, maxconn=2, dsn=None, verbose=False)
		print pool
		print pool.getconn()
		print pool.getconn()
		print pool.getconn()
		print type(pool.getconn())
	#--------------------------------------------------------------------
	def test_list_args():
		dsn = get_default_dsn()
		conn = get_connection(dsn, readonly=True)
		curs = conn.cursor()
		curs.execute('select * from clin.clin_narrative where narrative = %s', ['a'])
	#--------------------------------------------------------------------
	def test_sanitize_pg_regex():
		tests = [
			['(', '\\(']
			, ['[', '\\[']
			, [')', '\\)']
		]
		for test in tests:
			result = sanitize_pg_regex(test[0])
			if result != test[1]:
				print 'ERROR: sanitize_pg_regex(%s) returned "%s", expected "%s"' % (test[0], result, test[1])
	#--------------------------------------------------------------------
	def test_is_pg_interval():
		status = True
		tests = [
			[None, True],		# None == NULL == succeeds !
			[1, True],
			['1', True],
			['abc', False]
		]

		if not is_pg_interval():
			print 'ERROR: is_pg_interval() returned "False", expected "True"'
			status = False

		for test in tests:
			result = is_pg_interval(test[0])
			if result != test[1]:
				print 'ERROR: is_pg_interval(%s) returned "%s", expected "%s"' % (test[0], result, test[1])
				status = False

		return status
	#--------------------------------------------------------------------
	# run tests
#	test_get_connection()
#	test_exceptions()
#	test_ro_queries()
#	test_request_dsn()
#	test_set_encoding()
#	test_connection_pool()
#	test_list_args()
#	test_sanitize_pg_regex()
	test_is_pg_interval()

# =======================================================================
# $Log: gmPG2.py,v $
# Revision 1.64  2007-12-11 15:38:11  ncq
# - use std logging
#
# Revision 1.63  2007/12/06 13:07:19  ncq
# - add v8 schema hash
#
# Revision 1.62  2007/12/04 16:14:24  ncq
# - use gmAuthWidgets
#
# Revision 1.61  2007/12/04 15:11:20  ncq
# - sanity_check_database_settings()
# - force sql_inheritance to on after connect
#
# Revision 1.60  2007/11/09 14:39:10  ncq
# - log schema dump if verbose on failed version detection
#
# Revision 1.59  2007/10/25 16:41:30  ncq
# - is_pg_interval() + test
#
# Revision 1.58  2007/10/22 12:37:59  ncq
# - default db change
#
# Revision 1.57  2007/09/24 18:29:42  ncq
# - select 1,2; will return two columns with the same name !
#   hence, mapping names to column indices in a dict will not work :-(
#   fix breakage but don't really support it, either
#
# Revision 1.56  2007/09/18 22:53:26  ncq
# - enhance file2bytea to accept conn argument
#
# Revision 1.55  2007/09/17 21:46:28  ncq
# - make hash for v7 known
#
# Revision 1.54  2007/08/31 14:28:29  ncq
# - improved docs
#
# Revision 1.53  2007/08/08 21:25:39  ncq
# - improve bytea2file()
#
# Revision 1.52  2007/07/22 09:03:33  ncq
# - bytea2file(_object)()
# - file2bytea()
#
# Revision 1.51  2007/07/03 15:53:50  ncq
# - import re as regex
# - sanitize_pg_regex() and test
#
# Revision 1.50  2007/06/28 12:35:38  ncq
# - optionalize SQL IN tuple adaptation as it's now builtin to 0.2.6 psycopg2
#
# Revision 1.49  2007/06/15 10:24:24  ncq
# - add a test to the test suite
#
# Revision 1.48  2007/06/12 16:02:12  ncq
# - fix case when there are no args for execute()
#
# Revision 1.47  2007/06/11 20:24:18  ncq
# - bump database version
#
# Revision 1.46  2007/05/07 16:45:12  ncq
# - add v6 schema hash
#
# Revision 1.45  2007/05/07 16:28:34  ncq
# - use database maintenance functions in schema "gm"
#
# Revision 1.44  2007/04/27 13:19:58  ncq
# - get_schema_structure()
#
# Revision 1.43  2007/04/02 18:36:17  ncq
# - fix comment
#
# Revision 1.42  2007/04/02 14:31:17  ncq
# - v5 -> v6
#
# Revision 1.41  2007/04/01 15:27:09  ncq
# - safely get_encoding()
#
# Revision 1.40  2007/03/26 16:08:06  ncq
# - added v5 hash
#
# Revision 1.39  2007/03/08 11:37:24  ncq
# - simplified gmLogin
# - log PG settings on first connection if verbose
#
# Revision 1.38  2007/03/01 14:05:53  ncq
# - rollback in run_ro_queries() even if no error occurred such that
#   we don't stay IDLE IN TRANSACTION
#
# Revision 1.37  2007/03/01 14:03:53  ncq
# - in run_ro_queries() we now need to rollback failed transactions due to
#   the connections being pooled - or else abort state could carry over into
#   the next use of that connection - since transactions aren't really
#   in need of ending
#
# Revision 1.36  2007/02/19 15:00:53  ncq
# - restrict pooling to the default DSN, too
#
# Revision 1.35  2007/02/18 16:56:21  ncq
# - add connection pool for read-only connections ...
#
# Revision 1.34  2007/02/06 12:11:25  ncq
# - gnumed_v5
#
# Revision 1.33  2007/01/24 11:03:55  ncq
# - add sslmode=prefer to DSN
#
# Revision 1.32  2007/01/23 14:03:14  ncq
# - add known v4 schema hash - backport from 0.2.4
#
# Revision 1.31  2007/01/17 13:26:02  ncq
# - note on MDY/DMY handling
# - slightly easier python datetime adaptation
#
# Revision 1.30  2007/01/16 12:45:21  ncq
# - properly import/adapt mx.DateTime
#
# Revision 1.29  2007/01/16 10:28:49  ncq
# - do not FAIL on mxDT timezone string being ??? as
#   it should then be assumed to be local time
# - use mx.DateTime.ISO.str() to include timestamp in output
#
# Revision 1.28  2007/01/04 22:51:10  ncq
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