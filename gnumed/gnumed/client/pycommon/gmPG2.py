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
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import time
import sys
import os
import io
import codecs
import types
import logging
import datetime as pydt
import re as regex


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLoginInfo
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon.gmTools import prompted_input, u_replacement_character

_log = logging.getLogger('gm.db')


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
import psycopg2.errorcodes as sql_error_codes

# =======================================================================
_default_client_encoding = 'UTF8'
_log.info('assuming default client encoding of [%s]' % _default_client_encoding)

# things timezone
_default_client_timezone = None			# default time zone for connections
_sql_set_timezone = None
_timestamp_template = "cast('%s' as timestamp with time zone)"		# MUST NOT be uniocde or else getquoted will not work
FixedOffsetTimezone = dbapi.tz.FixedOffsetTimezone

_default_dsn = None
_default_login = None

default_database = 'gnumed_v21'

postgresql_version_string = None
postgresql_version = None			# accuracy: major.minor

__ro_conn_pool = None

auto_request_login_params = True
# =======================================================================
# global data
# =======================================================================

known_schema_hashes = {
	0: 'not released, testing only',
	2: 'b09d50d7ed3f91ddf4c4ddb8ea507720',
	3: 'e73718eaf230d8f1d2d01afa8462e176',
	4: '4428ccf2e54c289136819e701bb095ea',
	5: '7e7b093af57aea48c288e76632a382e5',	# ... old (v1) style hashes
	6: '90e2026ac2efd236da9c8608b8685b2d',	# new (v2) style hashes ...
	7: '6c9f6d3981483f8e9433df99d1947b27',
	8: '89b13a7af83337c3aad153b717e52360',
	9: '641a9b2be3c378ffc2bb2f0b1c9f051d',
	10: '7ef42a8fb2bd929a2cdd0c63864b4e8a',
	11: '03042ae24f3f92877d986fb0a6184d76',
	12: '06183a6616db62257e22814007a8ed07',
	13: 'fab7c1ae408a6530c47f9b5111a0841e',
	14: 'e170d543f067d1ea60bfe9076b1560cf',
	15: '70012ff960b77ecdff4981c94b5b55b6',
	16: '0bcf44ca22c479b52976e5eda1de8161',
	17: '161428ee97a00e3bf56168c3a15b7b50',
	18: 'a0f9efcabdecfb4ddb6d8c0b69c02092',
	#19: '419e5225259c53dd36ad80d82066ff02'	# 19.0 only
	#19: '9765373098b03fb208332498f34cd4b5' # until 19.11
	19: '57f009a159f55f77525cc0291e0c8b60', # starting with 19.12
	20: 'baed1901ed4c2f272b56c8cb2c6d88e8',
	21: 'e6a51a89dd22b75b61ead8f7083f251f'
}

map_schema_hash2version = {
	'b09d50d7ed3f91ddf4c4ddb8ea507720': 2,
	'e73718eaf230d8f1d2d01afa8462e176': 3,
	'4428ccf2e54c289136819e701bb095ea': 4,
	'7e7b093af57aea48c288e76632a382e5': 5,
	'90e2026ac2efd236da9c8608b8685b2d': 6,
	'6c9f6d3981483f8e9433df99d1947b27': 7,
	'89b13a7af83337c3aad153b717e52360': 8,
	'641a9b2be3c378ffc2bb2f0b1c9f051d': 9,
	'7ef42a8fb2bd929a2cdd0c63864b4e8a': 10,
	'03042ae24f3f92877d986fb0a6184d76': 11,
	'06183a6616db62257e22814007a8ed07': 12,
	'fab7c1ae408a6530c47f9b5111a0841e': 13,
	'e170d543f067d1ea60bfe9076b1560cf': 14,
	'70012ff960b77ecdff4981c94b5b55b6': 15,
	'0bcf44ca22c479b52976e5eda1de8161': 16,
	'161428ee97a00e3bf56168c3a15b7b50': 17,
	'a0f9efcabdecfb4ddb6d8c0b69c02092': 18,
	#'419e5225259c53dd36ad80d82066ff02': 19	# 19.0 only
	#'9765373098b03fb208332498f34cd4b5': 19 # until 19.11
	'57f009a159f55f77525cc0291e0c8b60': 19, # starting with 19.12
	'baed1901ed4c2f272b56c8cb2c6d88e8': 20,
	'e6a51a89dd22b75b61ead8f7083f251f': 21
}

map_client_branch2required_db_version = {
	u'GIT tree': 0,
	u'0.3': 9,
	u'0.4': 10,
	u'0.5': 11,
	u'0.6': 12,
	u'0.7': 13,
	u'0.8': 14,
	u'0.9': 15,
	u'1.0': 16,		# intentional duplicate with 1.1
	u'1.1': 16,
	u'1.2': 17,
	u'1.3': 18,
	u'1.4': 19,
	u'1.5': 20,
	u'1.6': 21
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

# only works for single-column FKs but that's fine
# needs gm-dbo, any-doc won't work
SQL_foreign_key_name = u"""SELECT
	fk_tbl.*,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = fk_tbl.connamespace) AS constraint_schema,
	fk_tbl.conname AS constraint_name,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = (SELECT relnamespace FROM pg_class where oid = fk_tbl.conrelid)) AS source_schema,
	(SELECT relname FROM pg_catalog.pg_class where oid = fk_tbl.conrelid) AS source_table,
	(SELECT attname FROM pg_catalog.pg_attribute WHERE attnum = fk_tbl.conkey[1] AND attrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass) AS source_column,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = (SELECT relnamespace FROM pg_class where oid = fk_tbl.confrelid)) AS target_schema,
	(SELECT relname FROM pg_catalog.pg_class where oid = fk_tbl.confrelid) AS target_table,
	(SELECT attname FROM pg_catalog.pg_attribute WHERE attnum = fk_tbl.confkey[1] AND attrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass) AS target_column
FROM
	pg_catalog.pg_constraint fk_tbl
WHERE
	fk_tbl.contype = 'f'
		AND
	fk_tbl.conrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass
		AND
	fk_tbl.conkey[1] = (
		SELECT
			col_tbl1.attnum
		FROM
			pg_catalog.pg_attribute col_tbl1
		WHERE
			col_tbl1.attname = %(src_col)s
				AND
			col_tbl1.attrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass
	)
		AND
	fk_tbl.confrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass
		AND
	fk_tbl.confkey[1] = (
		SELECT
			col_tbl2.attnum
		FROM
			pg_catalog.pg_attribute col_tbl2
		WHERE
			col_tbl2.attname = %(target_col)s
				AND
			col_tbl2.attrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass
	)
"""

SQL_get_index_name = u"""
SELECT
	(SELECT nspname FROM pg_namespace WHERE pg_namespace.oid = pg_class.relnamespace)
		AS index_schema,
	pg_class.relname
		AS index_name
FROM
	pg_class
WHERE
	pg_class.oid IN (
		SELECT
			indexrelid
		FROM
			pg_index
		WHERE
			pg_index.indrelid = %(idx_tbl)s::regclass
				AND
			pg_index.indnatts = 1		-- only one column in index
				AND
			pg_index.indkey[0] IN (
				SELECT
					pg_attribute.attnum
				FROM
					pg_attribute
				WHERE
					pg_attribute.attrelid = %(idx_tbl)s::regclass
						AND
					pg_attribute.attname = %(idx_col)s
				)
	)
"""

# =======================================================================
# module globals API
# =======================================================================
def set_default_client_encoding(encoding = None):
	# check whether psycopg2 can handle this encoding
	if encoding not in psycopg2.extensions.encodings:
		raise ValueError('psycopg2 does not know how to handle client (wire) encoding [%s]' % encoding)
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

	# FIXME: use __validate
	global _default_client_timezone
	_log.info('setting default client time zone from [%s] to [%s]' % (_default_client_timezone, timezone))
	_default_client_timezone = timezone

	global _sql_set_timezone
	_sql_set_timezone = u'set timezone to %s'

	return True

#---------------------------------------------------
def __validate_timezone(conn=None, timezone=None):

	_log.debug(u'validating time zone [%s]', timezone)

	cmd = u'set timezone to %(tz)s'
	args = {u'tz': timezone}

	conn.commit()
	curs = conn.cursor()
	is_valid = False
	try:
		curs.execute(cmd, args)
		_log.info(u'time zone [%s] is settable', timezone)
		# can we actually use it, though ?
		cmd = u"""select '1920-01-19 23:00:00+01'::timestamp with time zone"""
		try:
			curs.execute(cmd)
			curs.fetchone()
			_log.info(u'time zone [%s] is usable', timezone)
			is_valid = True
		except:
			_log.error('error using time zone [%s]', timezone)
	except dbapi.DataError:
		_log.warning(u'time zone [%s] is not settable', timezone)
	except:
		_log.error(u'failed to set time zone to [%s]', timezone)
		_log.exception(u'')

	curs.close()
	conn.rollback()

	return is_valid

#---------------------------------------------------
def __expand_timezone(conn=None, timezone=None):
	"""some timezone defs are abbreviations so try to expand
	them because "set time zone" doesn't take abbreviations"""

	cmd = u"""
select distinct on (abbrev) name
from pg_timezone_names
where
	abbrev = %(tz)s and
	name ~ '^[^/]+/[^/]+$' and
	name !~ '^Etc/'
"""
	args = {u'tz': timezone}

	conn.commit()
	curs = conn.cursor()

	result = timezone
	try:
		curs.execute(cmd, args)
		rows = curs.fetchall()
		if len(rows) > 0:
			result = rows[0]['name']
			_log.debug(u'[%s] maps to [%s]', timezone, result)
	except:
		_log.exception(u'cannot expand timezone abbreviation [%s]', timezone)

	curs.close()
	conn.rollback()

	return result

#---------------------------------------------------
def __detect_client_timezone(conn=None):
	"""This is run on the very first connection."""

	# FIXME: check whether server.timezone is the same
	# FIXME: value as what we eventually detect

	# we need gmDateTime to be initialized
	if gmDateTime.current_local_iso_numeric_timezone_string is None:
		gmDateTime.init()

	_log.debug('trying to detect timezone from system')

	tz_candidates = []
	try:
		tz = os.environ['TZ'].decode(gmI18N.get_encoding(), 'replace')
		tz_candidates.append(tz)
		expanded = __expand_timezone(conn = conn, timezone = tz)
		if expanded != tz:
			tz_candidates.append(expanded)
	except KeyError:
		pass

	tz_candidates.append(gmDateTime.current_local_timezone_name)
	expanded = __expand_timezone(conn = conn, timezone = gmDateTime.current_local_timezone_name)
	if expanded != gmDateTime.current_local_timezone_name:
		tz_candidates.append(expanded)

	_log.debug('candidates: %s', str(tz_candidates))

	# find best among candidates
	global _default_client_timezone
	global _sql_set_timezone
	found = False
	for tz in tz_candidates:
		if __validate_timezone(conn = conn, timezone = tz):
			_default_client_timezone = tz
			_sql_set_timezone = u'set timezone to %s'
			found = True
			break

	if not found:
		_default_client_timezone = gmDateTime.current_local_iso_numeric_timezone_string
		_sql_set_timezone = u"set time zone interval %s hour to minute"

	_log.info('client system time zone detected as equivalent to [%s]', _default_client_timezone)

# =======================================================================
# login API
# =======================================================================
def __request_login_params_tui():
	"""Text mode request of database login parameters"""
	import getpass
	login = gmLoginInfo.LoginInfo()

	print "\nPlease enter the required login parameters:"
	try:
		login.host = prompted_input(prompt = "host ('' = non-TCP/IP)", default = '')
		login.database = prompted_input(prompt = "database", default = default_database)
		login.user = prompted_input(prompt = "user name", default = '')
		tmp = 'password for "%s" (not shown): ' % login.user
		login.password = getpass.getpass(tmp)
		login.port = prompted_input(prompt = "port", default = 5432)
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
		raise AssertionError(_("The wxPython GUI framework hasn't been initialized yet!"))

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
	"""Request login parameters for database connection."""
	# do we auto-request parameters at all ?
	if not auto_request_login_params:
		raise Exception('Cannot request login parameters.')

	# are we inside X ?
	# (if we aren't wxGTK will crash hard at
	# C-level with "can't open Display")
	if u'DISPLAY' in os.environ:
		# try wxPython GUI
		try: return __request_login_params_gui_wx()
		except: pass

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

	if login.host is not None:
		if login.host.strip() == u'':
			login.host = None

	global _default_login
	_default_login = login
	_log.info('setting default login from [%s] to [%s]' % (_default_login, login))

	dsn = make_psycopg2_dsn(login.database, login.host, login.port, login.user, login.password)

	global _default_dsn
	if _default_dsn is None:
		old_dsn = u'None'
	else:
		old_dsn = regex.sub(r'password=[^\s]+', u'password=%s' % u_replacement_character, _default_dsn)
	_log.info ('setting default DSN from [%s] to [%s]',
		old_dsn,
		regex.sub(r'password=[^\s]+', u'password=%s' % u_replacement_character, dsn)
	)
	_default_dsn = dsn

	return True

#------------------------------------------------------------------------
def log_auth_environment():
	try:
		pgpass_file = os.path.expanduser(os.path.join('~', '.pgpass'))
		if os.path.exists(pgpass_file):
			_log.debug('standard .pgpass (%s) exists', pgpass_file)
		else:
			_log.debug('standard .pgpass (%s) not found', pgpass_file)
		pgpass_var = os.getenv('PGPASSFILE')
		if pgpass_var is None:
			_log.debug('$PGPASSFILE not set')
		else:
			if os.path.exists(pgpass_var):
				_log.debug('$PGPASSFILE=%s exists', pgpass_var)
			else:
				_log.debug('$PGPASSFILE=%s not found')
	except Exception:
		_log.exception('cannot detect .pgpass and or $PGPASSFILE')

# =======================================================================
# netadata API
# =======================================================================
def database_schema_compatible(link_obj=None, version=None, verbose=True):
	expected_hash = known_schema_hashes[version]
	if version == 0:
		args = {'ver': 9999}
	else:
		args = {'ver': version}
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
			for line in get_schema_structure(link_obj = link_obj).split():
				_log.debug(line)
			_log.debug('schema revision history dump follows:')
			for line in get_schema_revision_history(link_obj = link_obj):
				_log.debug(u' - '.join(line))
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
def get_schema_hash(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': u'select md5(gm.concat_table_structure()) as md5'}])
	return rows[0]['md5']
#------------------------------------------------------------------------
def get_schema_revision_history(link_obj=None):

	if table_exists(link_obj = link_obj, schema = 'gm', table = 'schema_revision'):
		cmd = u"""
			SELECT
				imported::text,
				version,
				filename
			FROM gm.schema_revision
			ORDER BY imported"""
	elif table_exists(link_obj = link_obj, schema = 'public', table = 'gm_schema_revision'):
		cmd = u"""
			SELECT
				imported::text,
				version,
				filename
			FROM public.gm_schema_revision
			ORDER BY imported"""
	else:
		return []

	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}])
	return rows
#------------------------------------------------------------------------
def get_current_user():
	rows, idx = run_ro_queries(queries = [{'cmd': u'select CURRENT_USER'}])
	return rows[0][0]
#------------------------------------------------------------------------
def get_foreign_keys2column(schema='public', table=None, column=None, link_obj=None):
	"""Get the foreign keys pointing to schema.table.column.

	Does not properly work with multi-column FKs.
	GNUmed doesn't use any, however.
	"""
	cmd = u"""
select
	%(schema)s as referenced_schema,
	%(tbl)s as referenced_table,
	%(col)s as referenced_column,
	pgc.confkey as referenced_column_list,
	pgc.conrelid::regclass as referencing_table,
	pgc.conkey as referencing_column_list,
	(select attname from pg_attribute where attnum = pgc.conkey[1] and attrelid = pgc.conrelid) as referencing_column
from
	pg_constraint pgc
where
	pgc.contype = 'f'
		and
	pgc.confrelid = (
		select oid from pg_class where relname = %(tbl)s and relnamespace = (
			select oid from pg_namespace where nspname = %(schema)s
		 )
	)	and
	(
		select attnum
		from pg_attribute
		where
			attrelid = (select oid from pg_class where relname = %(tbl)s and relnamespace = (
				select oid from pg_namespace where nspname = %(schema)s
			))
				and
			attname = %(col)s
	) = any(pgc.confkey)
"""

	args = {
		'schema': schema,
		'tbl': table,
		'col': column
	}

	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [
			{'cmd': cmd, 'args': args}
		]
	)

	return rows

#------------------------------------------------------------------------
def get_index_name(indexed_table=None, indexed_column=None, link_obj=None):

	args = {
		'idx_tbl': indexed_table,
		'idx_col': indexed_column
	}
	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{'cmd': SQL_get_index_name, 'args': args}],
		get_col_idx = False
	)

	return rows

#------------------------------------------------------------------------
def get_foreign_key_names(src_schema=None, src_table=None, src_column=None, target_schema=None, target_table=None, target_column=None, link_obj=None):

	args = {
		'src_schema': src_schema,
		'src_tbl': src_table,
		'src_col': src_column,
		'target_schema': target_schema,
		'target_tbl': target_table,
		'target_col': target_column
	}

	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{'cmd': SQL_foreign_key_name, 'args': args}],
		get_col_idx = False
	)

	return rows

#------------------------------------------------------------------------
def get_child_tables(schema='public', table=None, link_obj=None):
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
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': {'schema': schema, 'table': table}}])
	return rows
#------------------------------------------------------------------------
def schema_exists(link_obj=None, schema=u'gm'):
	cmd = u"""SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = %(schema)s)"""
	args = {'schema': schema}
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]
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
def function_exists(link_obj=None, schema=None, function=None):

	cmd = u"""
		SELECT EXISTS (
			SELECT 1 FROM pg_proc
			WHERE proname = %(func)s AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = %(schema)s)
		)
	"""
	args = {
		'func': function,
		'schema': schema
	}
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])
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
		if col_name in col_indices:
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

#------------------------------------------------------------------------
# i18n functions
#------------------------------------------------------------------------
def export_translations_from_database(filename=None):
	tx_file = io.open(filename, mode = 'wt', encoding = 'utf8')
	tx_file.write(u'-- GNUmed database string translations exported %s\n' % gmDateTime.pydt_now_here().strftime('%Y-%m-%d %H:%M'))
	tx_file.write(u'-- - contains translations for each of [%s]\n' % u', '.join(get_translation_languages()))
	tx_file.write(u'-- - user database language is set to [%s]\n\n' % get_current_user_language())
	tx_file.write(u'-- Please email this file to <gnumed-devel@gnu.org>.\n')
	tx_file.write(u'-- ----------------------------------------------------------------------------------------------\n\n')
	tx_file.write(u'set default_transaction_read_only to off;\n\n')
	tx_file.write(u"set client_encoding to 'utf-8';\n\n")
	tx_file.write(u'\\unset ON_ERROR_STOP\n\n')

	cmd = u'SELECT lang, orig, trans FROM i18n.translations ORDER BY lang, orig'
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	for row in rows:
		line = u"select i18n.upd_tx(E'%s', E'%s', E'%s');\n" % (
			row['lang'].replace("'", "\\'"),
			row['orig'].replace("'", "\\'"),
			row['trans'].replace("'", "\\'")
		)
		tx_file.write(line)
	tx_file.write(u'\n')

	tx_file.write(u'\set ON_ERROR_STOP 1\n')
	tx_file.close()

	return True

#------------------------------------------------------------------------
def delete_translation_from_database(link_obj=None, language=None, original=None):
	cmd = u'DELETE FROM i18n.translations WHERE lang = %(lang)s AND orig = %(orig)s'
	args = {'lang': language, 'orig': original}
	run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = False, end_tx = True)
	return True

#------------------------------------------------------------------------
def update_translation_in_database(language=None, original=None, translation=None):
	cmd = u'SELECT i18n.upd_tx(%(lang)s, %(orig)s, %(trans)s)'
	args = {'lang': language, 'orig': original, 'trans': translation}
	run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = False)
	return args

#------------------------------------------------------------------------
def get_translation_languages():
	rows, idx = run_ro_queries (
		queries = [{'cmd': u'select distinct lang from i18n.translations'}]
	)
	return [ r[0] for r in rows ]

#------------------------------------------------------------------------
def get_database_translations(language=None, order_by=None):

	args = {'lang': language}
	_log.debug('language [%s]', language)

	if order_by is None:
		order_by = u'ORDER BY %s' % order_by
	else:
		order_by = u'ORDER BY lang, orig'

	if language is None:
		cmd = u"""
		SELECT DISTINCT ON (orig, lang)
			lang, orig, trans
		FROM ((

			-- strings stored as translation keys whether translated or not
			SELECT
				NULL as lang,
				ik.orig,
				NULL AS trans
			FROM
				i18n.keys ik

		) UNION ALL (

			-- already translated strings
			SELECT
				it.lang,
				it.orig,
				it.trans
			FROM
				i18n.translations it

		)) as translatable_strings
		%s""" % order_by
	else:
		cmd = u"""
		SELECT DISTINCT ON (orig, lang)
			lang, orig, trans
		FROM ((

			-- strings stored as translation keys whether translated or not
			SELECT
				%%(lang)s as lang,
				ik.orig,
				i18n._(ik.orig, %%(lang)s) AS trans
			FROM
				i18n.keys ik

		) UNION ALL (

			-- already translated strings
			SELECT
				%%(lang)s as lang,
				it.orig,
				i18n._(it.orig, %%(lang)s) AS trans
			FROM
				i18n.translations it

		)) AS translatable_strings
		%s""" % order_by

	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if rows is None:
		_log.error('no translatable strings found')
	else:
		_log.debug('%s translatable strings found', len(rows))

	return rows

#------------------------------------------------------------------------
def get_current_user_language():
	cmd = u'select i18n.get_curr_lang()'
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}])
	return rows[0][0]

#------------------------------------------------------------------------
def set_user_language(user=None, language=None):
	"""Set the user language in the database.

	user = None: current db user
	language = None: unset
	"""
	_log.info('setting database language for user [%s] to [%s]', user, language)

	args = {
		'usr': user,
		'lang': language
	}

	if language is None:
		if user is None:
			queries = [{'cmd': u'select i18n.unset_curr_lang()'}]
		else:
			queries = [{'cmd': u'select i18n.unset_curr_lang(%(usr)s)', 'args': args}]
		queries.append({'cmd': u'select True'})
	else:
		if user is None:
			queries = [{'cmd': u'select i18n.set_curr_lang(%(lang)s)', 'args': args}]
		else:
			queries = [{'cmd': u'select i18n.set_curr_lang(%(lang)s, %(usr)s)', 'args': args}]

	rows, idx = run_rw_queries(queries = queries, return_data = True)

	if not rows[0][0]:
		_log.error('cannot set database language to [%s] for user [%s]', language, user)

	return rows[0][0]
#------------------------------------------------------------------------
def force_user_language(language=None):
	"""Set the user language in the database.

	- regardless of whether there is any translation available.
	- only for the current user
	"""
	_log.info('forcing database language for current db user to [%s]', language)

	run_rw_queries(queries = [{
		'cmd': u'select i18n.force_curr_lang(%(lang)s)',
		'args': {'lang': language}
	}])

# =======================================================================
# query runners and helpers
# =======================================================================
def send_maintenance_notification():
	cmd = u'notify "db_maintenance_warning"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)
#------------------------------------------------------------------------
def send_maintenance_shutdown():
	cmd = u'notify "db_maintenance_disconnect"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)
#------------------------------------------------------------------------
def is_pg_interval(candidate=None):
	cmd = u'SELECT %(candidate)s::interval'
	try:
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
		return True
	except:
		cmd = u'SELECT %(candidate)s::text::interval'
		try:
			rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
			return True
		except:
			return False

#------------------------------------------------------------------------
def lock_row(link_obj=None, table=None, pk=None, exclusive=False):
	"""Uses pg_advisory(_shared).

	- locks stack upon each other and need one unlock per lock
	- same connection:
		- all locks succeed
	- different connections:
		- shared + shared succeed
		- shared + exclusive fail
	"""
	_log.debug('locking row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	if exclusive:
		cmd = u"""SELECT pg_try_advisory_lock('%s'::regclass::oid::int, %s)""" % (table, pk)
	else:
		cmd = u"""SELECT pg_try_advisory_lock_shared('%s'::regclass::oid::int, %s)""" % (table, pk)
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		return True
	_log.warning('cannot lock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	return False

#------------------------------------------------------------------------
def unlock_row(link_obj=None, table=None, pk=None, exclusive=False):
	"""Uses pg_advisory_unlock(_shared).

	- each lock needs one unlock
	"""
	_log.debug('trying to unlock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	if exclusive:
		cmd = u"SELECT pg_advisory_unlock('%s'::regclass::oid::int, %s)" % (table, pk)
	else:
		cmd = u"SELECT pg_advisory_unlock_shared('%s'::regclass::oid::int, %s)" % (table, pk)
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		return True
	_log.warning('cannot unlock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	return False

#------------------------------------------------------------------------
def row_is_locked(table=None, pk=None):
	"""Looks at pk_locks

	- does not take into account locks other than 'advisory', however
	"""
	cmd = u"""SELECT EXISTS (
		SELECT 1 FROM pg_locks WHERE
			classid = '%s'::regclass::oid::int
				AND
			objid = %s
				AND
			locktype = 'advisory'
	)""" % (table, pk)
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		_log.debug('row is locked: [%s] [%s]', table, pk)
		return True
	_log.debug('row is NOT locked: [%s] [%s]', table, pk)
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
	conn = get_raw_connection(readonly=True)

	if data_size is None:
		rows, idx = run_ro_queries(link_obj = conn, queries = [data_size_query])
		data_size = rows[0][0]
		if data_size in [None, 0]:
			conn.rollback()
			return True

	max_chunk_size = 1024 * 1024 * 20			# 20 MB, works for typical CR DICOMs
	if chunk_size == 0:
		chunk_size = min(data_size, max_chunk_size)

	_log.debug('expecting %s bytes of BYTEA data in chunks of %s bytes', data_size, chunk_size)

	# Windoze sucks: it can't transfer objects of arbitrary size,
	# anyways, we need to split the transfer,
	# however, only possible if postgres >= 7.2
	needed_chunks, remainder = divmod(data_size, chunk_size)
	_log.debug('# of chunks: %s; remainder: %s bytes', needed_chunks, remainder)

#	# since we now require PG 9.1 we can disable this workaround:
#	# try setting "bytea_output"
#	# - fails if not necessary
#	# - succeeds if necessary
#	try:
#		run_ro_queries(link_obj = conn, queries = [{'cmd': u"set bytea_output to 'escape'"}])
#	except dbapi.ProgrammingError:
#		_log.debug('failed to set bytea_output to "escape", not necessary')

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
			conn.rollback()
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
			conn.rollback()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(str(rows[0][0]))

	conn.rollback()
	return True

#------------------------------------------------------------------------
def file2bytea(query=None, filename=None, args=None, conn=None, file_md5=None):
	"""Store data from a file into a bytea field.

	The query must:
	- be in unicode
	- contain a format spec identifying the row (eg a primary key)
	  matching <args> if it is an UPDATE
	- contain a format spec " <field> = %(data)s::bytea"

	The query CAN return the MD5 of the inserted data:
		RETURNING md5(<field>) AS md5
	in which case it will compare it to the md5
	of the file.
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
		conn = get_raw_connection(readonly = False)
		close_conn = True
	else:
		close_conn = False

	rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = (file_md5 is not None))

	success_status = True
	if file_md5 is None:
		conn.commit()
	else:
		db_md5 = rows[0]['md5']
		if file_md5 != db_md5:
			conn.rollback()
			success_status = False
			_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
		else:
			conn.commit()
			_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)

	if close_conn:
		conn.close()

	return success_status

#------------------------------------------------------------------------
def file2lo(filename=None, conn=None, check_md5=False):
	# 1 GB limit unless 64 bit Python build ...
	file_size = os.path.getsize(filename)
	if file_size > (1024 * 1024) * 1024:
		_log.debug(u'file size of [%s] > 1 GB, supposedly not supported by psycopg2 large objects (but seems to work anyway ?)', file_size)
#		return -1

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop
	_log.debug(u'[%s] -> large object', filename)

	# insert the data
	lo = conn.lobject(0, 'w', 0, filename)
	lo_oid = lo.oid
	lo.close()
	_log.debug('large object OID: %s', lo_oid)

	# verify
	if file_md5 is None:
		conn.commit()
		close_conn()
		return lo_oid
	cmd = u'SELECT md5(lo_get(%(loid)s::oid))'
	args = {'loid': lo_oid}
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database large object match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return lo_oid
	conn.rollback()
	close_conn()
	_log.error('MD5 sums of data file and database large object [%s] do not match: [file::%s] <> [DB::%s]', lo_oid, file_md5, db_md5)
	return -1

#------------------------------------------------------------------------
def file2bytea_lo(filename=None, conn=None, file_md5=None):
	# 1 GB limit unless 64 bit Python build ...
	file_size = os.path.getsize(filename)
	if file_size > (1024 * 1024) * 1024:
		_log.debug(u'file size of [%s] > 1 GB, supposedly not supported by psycopg2 large objects (but seems to work anyway ?)', file_size)
#		return -1

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop
	_log.debug(u'[%s] -> large object', filename)

	# insert the data
	lo = conn.lobject(0, 'w', 0, filename)
	lo_oid = lo.oid
	lo.close()
	_log.debug('large object OID: %s', lo_oid)

	# verify
	if file_md5 is None:
		conn.commit()
		close_conn()
		return lo_oid
	cmd = u'SELECT md5(lo_get(%(loid)s::oid))'
	args = {'loid': lo_oid}
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database large object match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return lo_oid
	conn.rollback()
	close_conn()
	_log.error('MD5 sums of data file and database large object [%s] do not match: [file::%s] <> [DB::%s]', lo_oid, file_md5, db_md5)
	return -1

#------------------------------------------------------------------------
def file2bytea_copy_from(table=None, columns=None, filename=None, conn=None, md5_query=None, file_md5=None):
	# md5_query: dict{'cmd': ..., 'args': ...}

	# UNTESTED

	chunk_size = 32 * (1024 * 1024)
	_log.debug('[%s] (%s bytes) --(%s bytes)-> %s(%s)', filename, os.path.getsize(filename), chunk_size, table, columns)
	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = True
	else:
		close_conn = False
	curs = conn.cursor()
	# write
	infile = file(filename, "rb")
	curs.copy_from(infile, table, size = chunk_size, columns = columns)
	infile.close()
	curs.close()
	if None in [file_md5, md5_query]:
		conn.commit()
		close_conn()
		return True
	# verify
	rows, idx = run_ro_queries(link_obj = conn, queries = [md5_query])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return True
	close_conn()
	_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
	return False

#------------------------------------------------------------------------
def file2bytea_overlay(query=None, args=None, filename=None, conn=None, md5_query=None, file_md5=None):
	"""Store data from a file into a bytea field.

	The query must:
	- 'cmd' must be in unicode
	- 'cmd' must contain a format spec identifying the row (eg
	  a primary key) matching <args> if it is an UPDATE
	- 'cmd' must contain "... SET ... <some_bytea_field> = OVERLAY(some_bytea_field PLACING %(data)s::bytea FROM %(start)s FOR %(size)s) ..."
	- 'args' must be a dict matching 'cmd'

	The query CAN return the MD5 of the inserted data:
		RETURNING md5(<field>) AS md5
	in which case it will compare it to the md5
	of the file.

	UPDATE
		the_table
	SET
		bytea_field = OVERLAY (
			coalesce(bytea_field, '':bytea),
			PLACING
				%(data)s::bytea
			FROM
				%(start)s
			FOR
				%(size)s
		)
	WHERE
		primary_key = pk_value

	SELECT md5(bytea_field) FROM the_table WHERE primary_key = pk_value
	"""
	chunk_size = 32 * (1024 * 1024)
	file_size = os.path.getsize(filename)
	if file_size <= chunk_size:
		chunk_size = file_size
	needed_chunks, remainder = divmod(file_size, chunk_size)
	_log.debug('file data: %s bytes, chunks: %s, chunk size: %s bytes, remainder: %s bytes', file_size, needed_chunks, chunk_size, remainder)

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop

	infile = file(filename, "rb")
	# write chunks
	for chunk_id in range(needed_chunks):
		chunk_start = (chunk_id * chunk_size) + 1
		args['start'] = chunk_start
		args['size'] = chunk_size
		data_as_byte_string = infile.read(chunk_size)
		args['data'] = buffer(data_as_byte_string)
		del(data_as_byte_string)
		try:
			rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = False)
		except StandardError:
			_log.exception('cannot write chunk [%s/%s] of size [%s], try decreasing chunk size', chunk_id+1, needed_chunks, chunk_size)
			conn.rollback()
			close_conn()
			infile.close()
			raise
	# write remainder
	if remainder > 0:
		chunk_start = (needed_chunks * chunk_size) + 1
		args['start'] = chunk_start
		args['size'] = remainder
		data_as_byte_string = infile.read(remainder)
		args['data'] = buffer(data_as_byte_string)
		del(data_as_byte_string)
		try:
			rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = False)
		except StandardError:
			_log.error('cannot retrieve remaining [%s] bytes' % remainder)
			conn.rollback()
			close_conn()
			infile.close()
			raise
	infile.close()
	if None in [file_md5, md5_query]:
		conn.commit()
		close_conn()
		return True
	# verify
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': md5_query, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return True
	close_conn()
	_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
	return False

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
		).replace (
			'+', '\+'
		).replace (
			'.', '\.'
		).replace (
			'*', '\*'
		)
		#']', '\]',			# not needed

#------------------------------------------------------------------------
def capture_cursor_state(cursor=None):
	conn = cursor.connection
	txt = u"""Link state:
Cursor
  identity: %s; name: %s
  closed: %s; scrollable: %s; with hold: %s; arraysize: %s; itersize: %s;
  last rowcount: %s; rownumber: %s; lastrowid (OID): %s;
  last description: %s
  statusmessage: %s
Connection
  identity: %s; backend pid: %s; protocol version: %s;
  closed: %s; autocommit: %s; isolation level: %s; encoding: %s; async: %s;
  TX status: %s; CX status: %s; executing async op: %s;
Query
  %s
""" % (
		id(cursor),
		cursor.name,
		cursor.closed,
		cursor.scrollable,
		cursor.withhold,
		cursor.arraysize,
		cursor.itersize,
		cursor.rowcount,
		cursor.rownumber,
		cursor.lastrowid,
		cursor.description,
		cursor.statusmessage,

		id(conn),
		conn.get_backend_pid(),
		conn.protocol_version,
		conn.closed,
		conn.autocommit,
		conn.isolation_level,
		conn.encoding,
		conn.async,
		conn.get_transaction_status(),
		conn.status,
		conn.isexecuting(),

		cursor.query,
	)
	return txt

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
		curs_close = lambda :1
		tx_rollback = lambda :1
		readonly_rollback_just_in_case = lambda :1
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		tx_rollback = link_obj.rollback
		if link_obj.autocommit is True:		# readonly connection ?
			readonly_rollback_just_in_case = link_obj.rollback
		else:
			# do not rollback readonly queries on passed-in readwrite
			# connections just in case because they may have already
			# seen fully legitimate write action which would get lost
			readonly_rollback_just_in_case = lambda :1
	elif link_obj is None:
		conn = get_connection(readonly=True, verbose=verbose)
		curs = conn.cursor()
		curs_close = curs.close
		tx_rollback = conn.rollback
		readonly_rollback_just_in_case = conn.rollback
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	if verbose:
		_log.debug('cursor: %s', curs)

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
				_log.debug(capture_cursor_state(curs))
		except dbapi.Error as pg_exc:
			_log.error('query failed in RO connection')
			_log.error(capture_cursor_state(curs))
			pg_exc = make_pg_exception_fields_unicode(pg_exc)
			_log.error('PG error code: %s', pg_exc.pgcode)
			if pg_exc.pgerror is not None:
				_log.error(u'PG error message: %s', pg_exc.u_pgerror)
			try:
				curs_close()
			except dbapi.InterfaceError:
				_log.exception('cannot close cursor')
			tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			if pg_exc.pgcode == sql_error_codes.INSUFFICIENT_PRIVILEGE:
				details = u'Query: [%s]' % curs.query.strip().strip(u'\n').strip().strip(u'\n')
				if curs.statusmessage != u'':
					details = u'Status: %s\n%s' % (
						curs.statusmessage.strip().strip(u'\n').strip().strip(u'\n'),
						details
					)
				if pg_exc.pgerror is None:
					msg = u'[%s]' % pg_exc.pgcode
				else:
					msg = u'[%s]: %s' % (pg_exc.pgcode, pg_exc.u_pgerror)
				raise gmExceptions.AccessDenied (
					msg,
					source = u'PostgreSQL',
					code = pg_exc.pgcode,
					details = details
				)
			raise
		except:
			_log.exception('query failed in RO connection')
			_log.error(capture_cursor_state(curs))
			try:
				curs_close()
			except dbapi.InterfaceError:
				_log.exception('cannot close cursor')
			tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if verbose:
			_log.debug('last query returned [%s (%s)] rows', curs.rowcount, len(data))
			_log.debug('cursor description: %s', str(curs.description))
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	readonly_rollback_just_in_case()
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
		"SELECT currval('some_sequence')" statement)

	<end_tx>
		- controls whether the transaction is finalized (eg.
		  committed/rolled back) or not, this allows the
		  call to run_rw_queries() to be part of a framing
		  transaction
		- if link_obj is a connection then <end_tx> will
		  default to False unless it is explicitly set to
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
		conn_close = lambda :1
		conn_commit = lambda :1
		tx_rollback = lambda :1
		curs = link_obj
		curs_close = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		conn_close = lambda :1
		if end_tx:
			conn_commit = link_obj.commit
			tx_rollback = link_obj.rollback
		else:
			conn_commit = lambda :1
			tx_rollback = lambda :1
		curs = link_obj.cursor()
		curs_close = curs.close
	elif link_obj is None:
		conn = get_connection(readonly=False)
		conn_close = conn.close
		conn_commit = conn.commit
		tx_rollback = conn.rollback
		curs = conn.cursor()
		curs_close = curs.close
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	for query in queries:
		if type(query['cmd']) is not types.UnicodeType:
			print "gmPG2.run_rw_queries(): non-unicode query"
			print query['cmd']
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				_log.debug(capture_cursor_state(curs))
		# DB related exceptions
		except dbapi.Error as pg_exc:
			_log.error('query failed in RW connection')
			_log.error(capture_cursor_state(curs))
			pg_exc = make_pg_exception_fields_unicode(pg_exc)
			_log.error(u'PG error code: %s', pg_exc.pgcode)
			if pg_exc.pgerror is not None:
				_log.error(u'PG error message: %s', pg_exc.u_pgerror)
			# privilege problem
			if pg_exc.pgcode == sql_error_codes.INSUFFICIENT_PRIVILEGE:
				details = u'Query: [%s]' % curs.query.strip().strip(u'\n').strip().strip(u'\n')
				if curs.statusmessage != u'':
					details = u'Status: %s\n%s' % (
						curs.statusmessage.strip().strip(u'\n').strip().strip(u'\n'),
						details
					)
				if pg_exc.pgerror is None:
					msg = u'[%s]' % pg_exc.pgcode
				else:
					msg = u'[%s]: %s' % (pg_exc.pgcode, pg_exc.u_pgerror)
				try:
					curs_close()
					tx_rollback()			# just for good measure
					conn_close()
				except dbapi.InterfaceError:
					_log.exception('cannot cleanup')
				raise gmExceptions.AccessDenied (
					msg,
					source = u'PostgreSQL',
					code = pg_exc.pgcode,
					details = details
				)
			# other problem
			gmLog2.log_stack_trace()
			try:
				curs_close()
				tx_rollback()			# just for good measure
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
			raise
		# other exception
		except:
			_log.exception('error running query in RW connection')
			_log.error(capture_cursor_state(curs))
			gmLog2.log_stack_trace()
			try:
				curs_close()
				tx_rollback()
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
			raise

	data = None
	col_idx = None
	if return_data:
		try:
			data = curs.fetchall()
		except:
			_log.exception('error fetching data from RW query')
			gmLog2.log_stack_trace()
			try:
				curs_close()
				tx_rollback()
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
				raise
			raise
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	conn_commit()
	conn_close()

	return (data, col_idx)

#------------------------------------------------------------------------
def run_insert(link_obj=None, schema=None, table=None, values=None, returning=None, end_tx=False, get_col_idx=False, verbose=False):
	"""Generates SQL for an INSERT query.

	values: dict of values keyed by field to insert them into
	"""
	if schema is None:
		schema = u'public'

	fields = values.keys()		# that way val_snippets and fields really should end up in the same order
	val_snippets = []
	for field in fields:
		val_snippets.append(u'%%(%s)s' % field)

	if returning is None:
		returning = u''
		return_data = False
	else:
		returning = u'\n\tRETURNING\n\t\t%s' % u', '.join(returning)
		return_data = True

	cmd = u"""\nINSERT INTO %s.%s (
		%s
	) VALUES (
		%s
	)%s""" % (
		schema,
		table,
		u',\n\t\t'.join(fields),
		u',\n\t\t'.join(val_snippets),
		returning
	)

	_log.debug(u'running SQL: >>>%s<<<', cmd)

	return run_rw_queries (
		link_obj = link_obj,
		queries = [{'cmd': cmd, 'args': values}],
		end_tx = end_tx,
		return_data = return_data,
		get_col_idx = get_col_idx,
		verbose = verbose
	)

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

		conn = get_raw_connection(dsn = self._kwargs['dsn'], verbose = self._kwargs['verbose'], readonly=True)

		conn.original_close = conn.close
		conn.close = _raise_exception_on_ro_conn_close

		if key is not None:
			self._used[key] = conn
			self._rused[id(conn)] = key
		else:
			self._pool.append(conn)

		return conn
	#--------------------------------------------------
	def shutdown(self):
		for conn_key in self._used.keys():
			_log.debug('closing pooled database connection, pool key: %s, backend PID: %s', conn_key, self._used[conn_key].get_backend_pid())
			self._used[conn_key].original_close()

# -----------------------------------------------------------------------
def get_raw_connection(dsn=None, verbose=False, readonly=True):
	"""Get a raw, unadorned connection.

	- this will not set any parameters such as encoding, timezone, datestyle
	- the only requirement is a valid DSN
	- hence it can be used for "service" connections
	  for verifying encodings etc
	"""
	# FIXME: support verbose
	if dsn is None:
		dsn = get_default_dsn()

	if u'host=salaam.homeunix' in dsn:
		raise ValueError('The public database is not hosted by <salaam.homeunix.com> anymore.\n\nPlease point your configuration files to <publicdb.gnumed.de>.')

	try:
		conn = dbapi.connect(dsn=dsn, connection_factory=psycopg2.extras.DictConnection)
		#conn = dbapi.connect(dsn=dsn, cursor_factory=psycopg2.extras.RealDictCursor)
	except dbapi.OperationalError, e:

		t, v, tb = sys.exc_info()
		try:
			msg = e.args[0]
		except (AttributeError, IndexError, TypeError):
			raise

		msg = unicode(msg, gmI18N.get_encoding(), 'replace')

		if msg.find('fe_sendauth') != -1:
			raise cAuthenticationError, (dsn, msg), tb

		if regex.search('user ".*" does not exist', msg) is not None:
			raise cAuthenticationError, (dsn, msg), tb

		if msg.find('uthenti') != -1:
			raise cAuthenticationError, (dsn, msg), tb

		raise

	_log.debug('new database connection, backend PID: %s, readonly: %s', conn.get_backend_pid(), readonly)

	# do first-time stuff
	global postgresql_version
	if postgresql_version is None:
		curs = conn.cursor()
		curs.execute("""
			SELECT
				substring(setting, E'^\\\\d{1,2}\\\\.\\\\d{1,2}')::numeric AS version
			FROM
				pg_settings
			WHERE
				name = 'server_version'
		""")
		postgresql_version = curs.fetchone()['version']
		_log.info('PostgreSQL version (numeric): %s' % postgresql_version)
		try:
			curs.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
			_log.info('database size: %s', curs.fetchone()[0])
		except:
			pass
		if verbose:
			_log_PG_settings(curs=curs)
		curs.close()
		conn.commit()

	if _default_client_timezone is None:
		__detect_client_timezone(conn = conn)

	curs = conn.cursor()

	# set access mode
	conn.set_session(readonly = readonly)
	conn.set_session(autocommit = readonly)
	if readonly:
		_log.debug('access mode [READ ONLY]')
		#conn.set_session(readonly = True)
		_log.debug('readonly: autocommit=True to avoid <IDLE IN TRANSACTION>')
#		conn.autocommit = True
#		cmd = 'set session characteristics as transaction READ ONLY'
#		curs.execute(cmd)
#		cmd = 'set default_transaction_read_only to on'
#		curs.execute(cmd)
	else:
		_log.debug('access mode [READ WRITE]')
#		conn.set_session(readonly = False)
		_log.debug('readwrite: autocommit=False')
#		cmd = 'set session characteristics as transaction READ WRITE'
#		curs.execute(cmd)
#		cmd = 'set default_transaction_read_only to off'
#		curs.execute(cmd)

	curs.close()
	conn.commit()

	conn.is_decorated = False

	return conn
# =======================================================================
def get_connection(dsn=None, readonly=True, encoding=None, verbose=False, pooled=True):
	"""Get a new connection.

	This assumes the locale system has been initialized
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
	else:
		conn = get_raw_connection(dsn=dsn, verbose=verbose, readonly=False)

	if conn.is_decorated:
		return conn

	if encoding is None:
		encoding = _default_client_encoding
	if encoding is None:
		encoding = gmI18N.get_encoding()
		_log.warning('client encoding not specified')
		_log.warning('the string encoding currently set in the active locale is used: [%s]' % encoding)
		_log.warning('for this to work properly the application MUST have called locale.setlocale() before')

	# set connection properties
	# - client encoding
	try:
		conn.set_client_encoding(encoding)
	except dbapi.OperationalError:
		t, v, tb = sys.exc_info()
		if str(v).find("can't set encoding to") != -1:
			raise cEncodingError, (encoding, v), tb
		raise

	# - transaction isolation level
	if readonly:
		# alter-database default, checked at connect, no need to set now
		iso_level = u'read committed'
	else:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		iso_level = u'serializable'

	_log.debug('client string encoding [%s], isolation level [%s], time zone [%s]', encoding, iso_level, _default_client_timezone)

	curs = conn.cursor()

	# - client time zone
	curs.execute(_sql_set_timezone, [_default_client_timezone])

	conn.commit()

#	# FIXME: remove this whole affair once either 9.0 is standard (Ubuntu 10 LTS is
#	# FIXME: PG 8.4, however!) or else when psycopg2 supports a workaround
#	#
#	# - bytea data format
#	# PG 9.0 switched to - by default - using "hex" rather than "escape",
#	# however, psycopg2's linked with a pre-9.0 libpq do assume "escape"
#	# as the transmission mode for bytea output,
#	# so try to set this setting back to "escape",
#	# if that's not possible the reason will be that PG < 9.0 does not support
#	# that setting - which also means we don't need it and can ignore the
#	# failure
#	cmd = "set bytea_output to 'escape'"
#	try:
#		curs.execute(cmd)
#	except dbapi.ProgrammingError:
#		_log.error('cannot set bytea_output format')

	curs.close()
	conn.commit()

	conn.is_decorated = True

	return conn
#-----------------------------------------------------------------------
def shutdown():
	if __ro_conn_pool is None:
		return
	__ro_conn_pool.shutdown()
# ======================================================================
# internal helpers
#-----------------------------------------------------------------------
def __noop():
	pass
#-----------------------------------------------------------------------
def _raise_exception_on_ro_conn_close():
	raise TypeError(u'close() called on read-only connection')
#-----------------------------------------------------------------------
def log_database_access(action=None):
	run_insert (
		schema = u'gm',
		table = u'access_log',
		values = {u'user_action': action},
		end_tx = True
	)
#-----------------------------------------------------------------------
def sanity_check_time_skew(tolerance=60):
	"""Check server time and local time to be within
	the given tolerance of each other.

	tolerance: seconds
	"""
	_log.debug('maximum skew tolerance (seconds): %s', tolerance)

	cmd = u"SELECT now() at time zone 'UTC'"
	conn = get_raw_connection(readonly=True)
	curs = conn.cursor()

	start = time.time()
	rows, idx = run_ro_queries(link_obj = curs, queries = [{'cmd': cmd}])
	end = time.time()
	client_now_as_utc = pydt.datetime.utcnow()

	curs.close()
	conn.commit()

	server_now_as_utc = rows[0][0]
	query_duration = end - start
	_log.info('server "now" (UTC): %s', server_now_as_utc)
	_log.info('client "now" (UTC): %s', client_now_as_utc)
	_log.debug('wire roundtrip (seconds): %s', query_duration)

	if query_duration > tolerance:
		_log.error('useless to check client/server time skew, wire roundtrip > tolerance')
		return False

	if server_now_as_utc > client_now_as_utc:
		real_skew = server_now_as_utc - client_now_as_utc
	else:
		real_skew = client_now_as_utc - server_now_as_utc

	_log.debug('client/server time skew: %s', real_skew)

	if real_skew > pydt.timedelta(seconds = tolerance):
		_log.error('client/server time skew > tolerance')
		return False

	return True
#-----------------------------------------------------------------------
def sanity_check_database_settings():
	"""Checks database settings.

	returns (status, message)
	status:
		0: no problem
		1: non-fatal problem
		2: fatal problem
	"""
	_log.debug('checking database settings')

	conn = get_connection()

	# - version string
	global postgresql_version_string
	if postgresql_version_string is None:
		curs = conn.cursor()
		curs.execute('SELECT version()')
		postgresql_version_string = curs.fetchone()['version']
		curs.close()
		_log.info('PostgreSQL version (string): "%s"' % postgresql_version_string)

	options2check = {
		# setting: [expected value, risk, fatal?]
		u'allow_system_table_mods': [u'off', u'system breakage', False],
		u'check_function_bodies': [u'on', u'suboptimal error detection', False],
		u'datestyle': [u'ISO', u'faulty timestamp parsing', True],
		u'default_transaction_isolation': [u'read committed', u'faulty database reads', True],
		u'default_transaction_read_only': [u'on', u'accidental database writes', False],
		u'fsync': [u'on', u'data loss/corruption', True],
		u'full_page_writes': [u'on', u'data loss/corruption', False],
		u'lc_messages': [u'C', u'suboptimal error detection', False],
		u'password_encryption': [u'on', u'breach of confidentiality', False],
		#u'regex_flavor': [u'advanced', u'query breakage', False],					# 9.0 doesn't support this anymore, default now advanced anyway
		u'synchronous_commit': [u'on', u'data loss/corruption', False],
		u'sql_inheritance': [u'on', u'query breakage, data loss/corruption', True],
		u'ignore_checksum_failure': [u'off', u'data loss/corruption', False],		# starting with PG 9.3
		u'track_commit_timestamp': [u'on', u'suboptimal auditing', False]			# starting with PG 9.3
	}

	from Gnumed.pycommon import gmCfg2
	_cfg = gmCfg2.gmCfgData()
	if _cfg.get(option = u'hipaa'):
		options2check[u'log_connections'] = [u'on', u'non-compliance with HIPAA', True]
		options2check[u'log_disconnections'] = [u'on', u'non-compliance with HIPAA', True]
	else:
		options2check[u'log_connections'] = [u'on', u'non-compliance with HIPAA', None]
		options2check[u'log_disconnections'] = [u'on', u'non-compliance with HIPAA', None]

	cmd = u"SELECT name, setting from pg_settings where name in %(settings)s"
	rows, idx = run_ro_queries (
		link_obj = conn,
		queries = [{'cmd': cmd, 'args': {'settings': tuple(options2check.keys())}}],
		get_col_idx = False
	)

	found_error = False
	found_problem = False
	msg = []
	for row in rows:
		option = row['name']
		value_found = row['setting']
		value_expected = options2check[option][0]
		risk = options2check[option][1]
		fatal_setting = options2check[option][2]
		if value_found != value_expected:
			if fatal_setting is True:
				found_error = True
			elif fatal_setting is False:
				found_problem = True
			elif fatal_setting is None:
				pass
			else:
				_log.error(options2check[option])
				raise ValueError(u'invalid database configuration sanity check')
			msg.append(_(' option [%s]: %s') % (option, value_found))
			msg.append(_('  risk: %s') % risk)
			_log.warning('PG option [%s] set to [%s], expected [%s], risk: <%s>' % (option, value_found, value_expected, risk))

	if found_error:
		return 2, u'\n'.join(msg)

	if found_problem:
		return 1, u'\n'.join(msg)

	return 0, u''
#------------------------------------------------------------------------
def _log_PG_settings(curs=None):
	# don't use any of the run_*()s since that might
	# create a loop if we fail here
	# FIXME: use pg_settings
	try:
		curs.execute(u'show all')
	except:
		_log.exception(u'cannot log PG settings (>>>show all<<< failed)')
		return False
	settings = curs.fetchall()
	if settings is None:
		_log.error(u'cannot log PG settings (>>>show all<<< did not return rows)')
		return False
	for setting in settings:
		_log.debug(u'PG option [%s]: %s', setting['name'], setting['setting'])

	try:
		curs.execute(u'select pg_available_extensions()')
	except:
		_log.exception(u'cannot log available PG extensions')
		return False
	extensions = curs.fetchall()
	if extensions is None:
		_log.error(u'no PG extensions available')
		return False
	for ext in extensions:
		_log.debug(u'PG extension: %s', ext['pg_available_extensions'])

	return True
#========================================================================
def make_pg_exception_fields_unicode(exc):

	if not isinstance(exc, dbapi.Error):
		return exc

	if exc.pgerror is None:
		try:
			msg = exc.args[0]
		except (AttributeError, IndexError, TypeError):
			return exc
		# assumption
		exc.u_pgerror = unicode(msg, gmI18N.get_encoding(), 'replace')
		return exc

	# assumption
	exc.u_pgerror = unicode(exc.pgerror, gmI18N.get_encoding(), 'replace').strip().strip(u'\n').strip().strip(u'\n')

	return exc
#------------------------------------------------------------------------
def extract_msg_from_pg_exception(exc=None):

	try:
		msg = exc.args[0]
	except (AttributeError, IndexError, TypeError):
		return u'cannot extract message from exception'

	# assumption
	return unicode(msg, gmI18N.get_encoding(), 'replace')
# =======================================================================
class cAuthenticationError(dbapi.OperationalError):

	def __init__(self, dsn=None, prev_val=None):
		self.dsn = dsn
		self.prev_val = prev_val

	def __str__(self):
		_log.warning('%s.__str__() called', self.__class__.__name__)
		tmp = u'PostgreSQL: %sDSN: %s' % (self.prev_val, self.dsn)
		_log.error(tmp)
		return tmp.encode(gmI18N.get_encoding(), 'replace')

	def __unicode__(self):
		return u'PostgreSQL: %sDSN: %s' % (self.prev_val, self.dsn)

# =======================================================================
# custom psycopg2 extensions
# =======================================================================
class cEncodingError(dbapi.OperationalError):

	def __init__(self, encoding=None, prev_val=None):
		self.encoding = encoding
		self.prev_val = prev_val

	def __str__(self):
		_log.warning('%s.__str__() called', self.__class__.__name__)
		return 'PostgreSQL: %s\nencoding: %s' % (self.prev_val.encode(gmI18N.get_encoding(), 'replace'), self.encoding.encode(gmI18N.get_encoding(), 'replace'))

	def __unicode__(self):
		return u'PostgreSQL: %s\nencoding: %s' % (self.prev_val, self.encoding)

# -----------------------------------------------------------------------
# Python -> PostgreSQL
# -----------------------------------------------------------------------
# test when Squeeze (and thus psycopg2 2.2 becomes Stable
class cAdapterPyDateTime(object):

	def __init__(self, dt):
		if dt.tzinfo is None:
			raise ValueError(u'datetime.datetime instance is lacking a time zone: [%s]' % _timestamp_template % dt.isoformat())
		self.__dt = dt

	def getquoted(self):
		return _timestamp_template % self.__dt.isoformat()

## remove for 0.9
## ----------------------------------------------------------------------
##class cAdapterMxDateTime(object):
##
##	def __init__(self, dt):
##		if dt.tz == '???':
##			_log.info('[%s]: no time zone string available in (%s), assuming local time zone', self.__class__.__name__, dt)
##		self.__dt = dt
##
##	def getquoted(self):
##		# under some locale settings the mx.DateTime ISO formatter
##		# will insert "," into the ISO string,
##		# while this is allowed per the ISO8601 spec PostgreSQL
##		# cannot currently handle that,
##		# so map those "," to "." to make things work:
##		return mxDT.ISO.str(self.__dt).replace(',', '.')
##
## ----------------------------------------------------------------------
## PostgreSQL -> Python
## ----------------------------------------------------------------------

#=======================================================================
#  main
#-----------------------------------------------------------------------

# make sure psycopg2 knows how to handle unicode ...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
# check in 0.9:
psycopg2.extensions.register_adapter(pydt.datetime, cAdapterPyDateTime)

# turn dict()s into JSON - only works > 9.2
#psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

# do NOT adapt *lists* to "... IN (*) ..." syntax because we want
# them adapted to "... ARRAY[]..." so we can support PG arrays

#=======================================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon.gmTools import file2md5

	logging.basicConfig(level=logging.DEBUG)

	#--------------------------------------------------------------------
	def test_file2bytea():
		run_rw_queries(queries = [
			{'cmd': u'drop table if exists test_bytea'},
			{'cmd': u'create table test_bytea (data bytea)'}
		])

		try:
			file2bytea(query = u'insert into test_bytea values (%(data)s::bytea) returning md5(data) as md5', filename = sys.argv[2], file_md5 = file2md5(sys.argv[2], True))
		except:
			_log.exception('error')

		run_rw_queries(queries = [
			{'cmd': u'drop table test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_file2bytea_lo():
		lo_oid = file2bytea_lo (
			filename = sys.argv[2]
			#, file_md5 = file2md5(sys.argv[2], True)
		)
		print lo_oid
#		if lo_oid != -1:
#			run_rw_queries(queries = [
#				{'cmd': u'select lo_unlink(%(loid)s::oid)', 'args': {'loid': lo_oid}}
#			])

	#--------------------------------------------------------------------
	def test_file2bytea_copy_from():

		run_rw_queries(queries = [
			{'cmd': u'drop table if exists test_bytea'},
			{'cmd': u'create table test_bytea (pk serial primary key, data bytea)'},
			{'cmd': u"insert into test_bytea (data) values (NULL::bytea)"}
		])

		md5_query = {
			'cmd': u'select md5(data) AS md5 FROM test_bytea WHERE pk = %(pk)s',
			'args': {'pk': 1}
		}

		file2bytea_copy_from (
			table = u'test_bytea',
			columns = [u'data'],
			filename = sys.argv[2],
			md5_query = md5_query,
			file_md5 = file2md5(sys.argv[2], True)
		)

		run_rw_queries(queries = [
			{'cmd': u'drop table if exists test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_file2bytea_overlay():

		run_rw_queries(queries = [
			{'cmd': u'drop table if exists test_bytea'},
			{'cmd': u'create table test_bytea (pk serial primary key, data bytea)'},
			{'cmd': u"insert into test_bytea (data) values (NULL::bytea)"}
		])

		cmd = u"""
		update test_bytea
		set data = overlay (
			coalesce(data, ''::bytea)
			placing %(data)s::bytea
			from %(start)s
			for %(size)s
		)
		where
			pk > %(pk)s
		"""
		md5_cmd = u'select md5(data) from test_bytea'
		args = {'pk': 0}
		file2bytea_overlay (
			query = cmd,
			args = args,
			filename = sys.argv[2],
			conn = None,
			md5_query = md5_cmd,
			file_md5 = file2md5(sys.argv[2], True)
		)

		run_rw_queries(queries = [
			{'cmd': u'drop table test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_get_connection():
		print "testing get_connection()"

		dsn = 'foo'
		try:
			conn = get_connection(dsn=dsn)
		except dbapi.OperationalError, e:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc password=abc'
		try:
			conn = get_connection(dsn=dsn)
		except cAuthenticationError:
			print "SUCCESS: get_connection(%s) failed as expected" % dsn
			t, v = sys.exc_info()[:2]
			print ' ', t
			print ' ', v

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=True)

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=False)

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
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

		dsn = 'dbname=gnumed_v9 user=any-doc password=any-doc'
		conn = get_connection(dsn, readonly=True)

		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'SELECT version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx
		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': u'SELECT 1'}], return_data=True, get_col_idx=True)
		print data
		print idx

		curs = conn.cursor()

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'SELECT version()'}], return_data=True, get_col_idx=True, verbose=True)
		print data
		print idx

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': u'SELECT 1'}], return_data=True, get_col_idx=True, verbose=True)
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
		curs.execute('SELECT * from clin.clin_narrative where narrative = %s', ['a'])
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
	def test_sanity_check_time_skew():
		sanity_check_time_skew()
	#--------------------------------------------------------------------
	def test_get_foreign_key_names():
		print get_foreign_key_names (
			src_schema = u'clin',
			src_table = u'vaccination',
			src_column = u'fk_episode',
			target_schema = u'clin',
			target_table = u'episode',
			target_column = u'pk'
		)
	#--------------------------------------------------------------------
	def test_get_foreign_key_details():
		for row in get_foreign_keys2column (
			schema = u'clin',
			table = u'episode',
			column = u'pk'
		):
			print '%s.%s references %s.%s.%s' % (
				row['referencing_table'],
				row['referencing_column'],
				row['referenced_schema'],
				row['referenced_table'],
				row['referenced_column']
			)
	#--------------------------------------------------------------------
	def test_set_user_language():
		# (user, language, result, exception type)
		tests = [
			# current user
			[None, 'de_DE', True],
			[None, 'lang_w/o_tx', False],
			[None, None, True],
			# valid user
			['any-doc', 'de_DE', True],
			['any-doc', 'lang_w/o_tx', False],
			['any-doc', None, True],
			# invalid user
			['invalid user', 'de_DE', None],
			['invalid user', 'lang_w/o_tx', False], # lang checking happens before user checking
			['invalid user', None, True]
		]
		for test in tests:
			try:
				result = set_user_language(user = test[0], language = test[1])
				if result != test[2]:
					print "test:", test
					print "result:", result, "expected:", test[2]
			except psycopg2.IntegrityError, e:
				if test[2] is None:
					continue
				print "test:", test
				print "expected exception"
				print "result:", e
	#--------------------------------------------------------------------
	def test_get_schema_revision_history():
		for line in get_schema_revision_history():
			print u' - '.join(line)
	#--------------------------------------------------------------------
	def test_run_query():
		gmDateTime.init()
		args = {'dt': gmDateTime.pydt_max_here()}
		cmd = u"SELECT %(dt)s"

		#cmd = u"SELECT 'infinity'::timestamp with time zone"

		cmd = u"""
SELECT to_timestamp (foofoo,'YYMMDD.HH24MI') FROM (
	SELECT REGEXP_REPLACE (
		't1.130729.0902.tif',			-- string
		E'(.1)\.([0-9\.]+)(\.tif)',		-- pattern
		E'\\\\2'						-- replacement
	) AS foofoo
) AS foo"""
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		print rows
		print rows[0]
		print rows[0][0]
	#--------------------------------------------------------------------
	def test_schema_exists():
		print schema_exists()
	#--------------------------------------------------------------------
	def test_row_locks():
		row_is_locked(table = 'dem.identity', pk = 12)

		print "1st connection:"
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)
		print " 1st shared lock succeeded:", lock_row(table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)

		print "   2nd shared lock should succeed:", lock_row(table = 'dem.identity', pk = 12, exclusive = False)
		print "   `-> unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)
		print "   exclusive lock should succeed:", lock_row(table = 'dem.identity', pk = 12, exclusive = True)
		print "   `-> unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = True)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)

		print "2nd connection:"
		conn = get_raw_connection(readonly=True)
		print " shared lock should succeed:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False)
		print " `-> unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)
		print " exclusive lock succeeded ?", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = True), "(should fail)"
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)

		print "1st connection:"
		print " unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)

		print "2nd connection:"
		print " exclusive lock should succeed", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = True)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)
		print "  shared lock should succeed:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False)
		print "  `-> unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)
		print " unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False)
		print " locked:", row_is_locked(table = 'dem.identity', pk = 12)

		conn.close()
	#--------------------------------------------------------------------
	def test_get_foreign_key_names():
		print get_foreign_key_names (
			src_schema = 'dem',
			src_table = 'names',
			src_column = 'id_identity',
			target_schema = 'dem',
			target_table = 'identity',
			target_column = 'pk'
		)
	#--------------------------------------------------------------------
	def test_get_index_name():
		print get_index_name(indexed_table = 'clin.vaccination', indexed_column = 'fk_episode')

	#--------------------------------------------------------------------
	def test_faulty_SQL():
		run_ro_queries(queries = [{'cmd': u'SELEC 1'}])

	#--------------------------------------------------------------------
	# run tests
	#test_get_connection()
	#test_exceptions()
	#test_ro_queries()
	#test_request_dsn()
	#test_set_encoding()
	#test_connection_pool()
	#test_list_args()
	#test_sanitize_pg_regex()
	#test_is_pg_interval()
	#test_sanity_check_time_skew()
	#test_get_foreign_key_details()
	#test_get_foreign_key_names()
	#test_get_index_name()
	#test_set_user_language()
	#test_get_schema_revision_history()
	#test_run_query()
	#test_schema_exists()
	#test_get_foreign_key_names()
	#test_row_locks()
	#test_file2bytea()
	#test_file2bytea_overlay()
	#test_file2bytea_copy_from()
	#test_file2bytea_lo()
	test_faulty_SQL()

# ======================================================================
