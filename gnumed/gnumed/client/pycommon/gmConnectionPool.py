# -*- coding: utf-8 -*-

"""GNUmed connection pooler.

Currently, only readonly connections are pooled.

This pool is (supposedly) thread safe.
"""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"


_DISABLE_CONNECTION_POOL = False		# set to True to disable the connection pool for debugging (= always return new connection)
_VERBOSE_PG_LOG = False				# set to True to force-enable verbose connections

# standard library imports
import os
import sys
import inspect
import logging
import threading
import types
import re as regex
import datetime as pydt


# 3rd party library imports
import psycopg2 as dbapi

if not (float(dbapi.apilevel) >= 2.0):
	raise ImportError('gmPG2: supported DB-API level too low')

if not (dbapi.threadsafety == 2):
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


import psycopg2.extensions
import psycopg2.extras
import psycopg2.errorcodes as PG_error_codes


# GNUmed module imports
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime


# CONSTANTS
_SQL_expand_tz_name = """
SELECT DISTINCT ON (abbrev) name
FROM pg_timezone_names
WHERE
	abbrev = %(tz)s
		AND
	name ~ '^[^/]+/[^/]+$'
		AND
	name !~ '^Etc/'
"""


# globals
_log = logging.getLogger('gm.db_pool')
_log.info('psycopg2 module version: %s' % dbapi.__version__)
_log.info('PostgreSQL via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
_log.info('libpq version (compiled in): %s', psycopg2.__libpq_version__)
_log.info('libpq version (loaded now) : %s', psycopg2.extensions.libpq_version())
#if '2.8' in dbapi.__version__:
#	_log.info('psycopg2 v2.8 detected, disabling connection pooling for the time being')
#	_DISABLE_CONNECTION_POOL = True


postgresql_version = None

_timestamp_template = "cast('%s' as timestamp with time zone)"		# MUST NOT be uniocde or else getquoted will not work (true in py3 ?)

_map_psyco_tx_status2str = [
	'TRANSACTION_STATUS_IDLE',
	'TRANSACTION_STATUS_ACTIVE',
	'TRANSACTION_STATUS_INTRANS',
	'TRANSACTION_STATUS_INERROR',
	'TRANSACTION_STATUS_UNKNOWN'
]

_map_psyco_conn_status2str = [
	'0 - ?',
	'STATUS_READY',
	'STATUS_BEGIN_ALIAS_IN_TRANSACTION',
	'STATUS_PREPARED'
]

_map_psyco_iso_level2str = {
	None: 'ISOLATION_LEVEL_DEFAULT (configured on server)',
	0: 'ISOLATION_LEVEL_AUTOCOMMIT',
	1: 'ISOLATION_LEVEL_READ_UNCOMMITTED',
	2: 'ISOLATION_LEVEL_REPEATABLE_READ',
	3: 'ISOLATION_LEVEL_SERIALIZABLE',
	4: 'ISOLATION_LEVEL_READ_UNCOMMITTED'
}

_connection_loss_markers = [
	'terminating connection due to administrator command'
]

#============================================================
class cPGCredentials:
	"""Holds PostgreSQL credentials"""

	def __init__(self) -> None:
		self.__host:str = None			# None: left out -> defaults to $PGHOST or implicit <localhost>
		self.__port:int = None			# None: left out -> defaults to $PGPORT or libpq compiled-in default (typically 5432)
		self.__database:str = None		# must be set before connecting
		self.__user:str = None			# must be set before connecting
		self.__password:str = None		# None: left out
										# -> try password-less connect (TRUST/IDENT/PEER)
										# -> try connect with password from <passfile> parameter or $PGPASSFILE or ~/.pgpass

	#--------------------------------------------------
	# properties
	#--------------------------------------------------
	def __format_credentials(self) -> str:
		"""Database credentials formatted as string."""
		cred_parts = [
			'dbname=%s' % self.__database,
			'host=%s' % self.__host,
			'port=%s' % self.__port,
			'user=%s' % self.__user
		]
		return ' '.join(cred_parts)

	formatted_credentials = property(__format_credentials)

	#--------------------------------------------------
	def generate_credentials_kwargs(self, connection_name:str=None) -> dict:
		"""Return dictionary with credentials suitable for psycopg2.connection() keyword arguments."""
		assert (self.__database is not None), 'self.__database must be defined'
		assert (self.__user is not None), 'self.__user must be defined'

		kwargs = {
			'dbname': self.__database,
			'user': self.__user,
			'application_name': gmTools.coalesce(connection_name, 'GNUmed'),
			'fallback_application_name': 'GNUmed',
			'sslmode': 'prefer',
			# try to enforce a useful encoding early on so that we
			# have a good chance of decoding authentication errors
			# containing foreign language characters
			'client_encoding': 'UTF8'
		}
		if self.__host is not None:
			kwargs['host'] = self.__host
		if self.__port is not None:
			kwargs['port'] = self.__port
		if self.__password is not None:
			kwargs['password'] = self.__password
		return kwargs

	credentials_kwargs = property(generate_credentials_kwargs)

	#--------------------------------------------------
	def _get_database(self) -> str:
		return self.__database

	def _set_database(self, database:str=None):
		assert database, '<database> must not be None'
		assert database.strip(), '<database> must not be empty'
		assert ('salaam.homeunix' not in database), 'The public database is not hosted by <salaam.homeunix.com> anymore.\n\nPlease point your configuration files to <publicdb.gnumed.de>.'
		self.__database = database.strip()
		_log.info('[%s]', self.__database)

	database = property(_get_database, _set_database)

	#--------------------------------------------------
	def _get_host(self) -> str:
		return self.__host

	def _set_host(self, host:str=None):
		if host is not None:
			host = host.strip()
			if host == '':
				host = None
		self.__host = host
		_log.info('[%s]', self.__host)

	host = property(_get_host, _set_host)

	#--------------------------------------------------
	def _get_port(self) -> int:
		return self.__port

	def _set_port(self, port=None):
		_log.info('[%s]', port)
		if port is None:
			self.__port = None
			return

		self.__port = int(port)

	port = property(_get_port, _set_port)

	#--------------------------------------------------
	def _get_user(self) -> str:
		return self.__user

	def _set_user(self, user:str=None):
		assert (user is not None), '<user> must not be None'
		assert (user.strip() != ''), '<user> must not be empty'
		self.__user = user.strip()
		_log.info('[%s]', self.__user)

	user = property(_get_user, _set_user)

	#--------------------------------------------------
	def _get_password(self) -> str:
		return self.__password

	def _set_password(self, password:str=None):
		if password is not None:
			gmLog2.add_word2hide(password)
		self.__password = password
		_log.info('password was set')

	password = property(_get_password, _set_password)

#============================================================
class gmConnectionPool(gmBorg.cBorg):
	"""The Singleton connection pool class.

	Any normal connection from GNUmed to PostgreSQL should go
	through this pool. It needs credentials to be provided
	via .credentials = <cPGCredentials>.
	"""
	def __init__(self) -> None:
		try:
			self.__initialized
			return

		except AttributeError:
			self.__initialized:bool = True

		_log.info('[%s]: first instantiation', self.__class__.__name__)
		self.__ro_conn_pool:dict[str, dbapi._psycopg.connection] = {}	# keyed by "credentials::thread ID"
		self.__SQL_set_client_timezone:str = None
		self.__client_timezone = None
		self.__creds:cPGCredentials = None
		self.__log_auth_environment()

	#--------------------------------------------------
	# connection API
	#--------------------------------------------------
	def get_connection(self, readonly:bool=True, verbose:bool=False, pooled:bool=True, connection_name:str=None, autocommit:bool=False, credentials:cPGCredentials=None) -> dbapi._psycopg.connection:
		"""Provide a database connection.

		Readonly connections can be pooled. If there is no
		suitable connection in the pool a new one will be
		created and stored. The pool is per-thread and
		per-credentials.

		Args:
			readonly: make connection read only
			verbose: make connection log more things
			pooled: return a pooled connection, if possible
			connection_name: a human readable name for the connection, avoid spaces
			autocommit: whether to autocommit
			credentials: use for getting a connection with other credentials different from what the pool was set to before

		Returns:
			a working connection to a PostgreSQL database
		"""
#		if _DISABLE_CONNECTION_POOL:
#			pooled = False

		if credentials is not None:
			pooled = False
		conn = None
		if readonly and pooled:
			try:
				conn = self.__ro_conn_pool[self.pool_key]
			except KeyError:
				_log.info('pooled RO conn with key [%s] requested, but not in pool, setting up', self.pool_key)
			if conn is not None:
				#if verbose:
				#	_log.debug('using pooled conn [%s]', self.pool_key)
				return conn

		if conn is None:
			conn = self.get_raw_connection (
				verbose = verbose,
				readonly = readonly,
				connection_name = connection_name,
				autocommit = autocommit,
				credentials = credentials
			)
		if readonly and pooled:
			# monkey patch close() for pooled RO connections
			conn.original_close = conn.close
			conn.close = _raise_exception_on_pooled_ro_conn_close
		# set connection properties
		# - client encoding
		encoding = 'UTF8'
		_log.debug('desired client (wire) encoding: [%s]', encoding)
		conn.set_client_encoding(encoding)
		# - transaction isolation level
		if not readonly:
			conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		# - client time zone
		_log.debug('client timezone [%s]', self.__client_timezone)
		curs = conn.cursor()
		curs.execute(self.__SQL_set_client_timezone, {'tz': self.__client_timezone})
		curs.close()
		conn.commit()
		if readonly and pooled:
			_log.debug('putting RO conn with key [%s] into pool', self.pool_key)
			self.__ro_conn_pool[self.pool_key] = conn
		if verbose:
			log_conn_state(conn)
		return conn

	#--------------------------------------------------
	def get_rw_conn(self, verbose:bool=False, connection_name:str=None, autocommit:bool=False) -> dbapi._psycopg.connection:
		return self.get_connection(verbose = verbose, readonly = False, connection_name = connection_name, autocommit = autocommit)

	#--------------------------------------------------
	def get_ro_conn(self, verbose:bool=False, connection_name:str=None, autocommit:bool=False) -> dbapi._psycopg.connection:
		return self.get_connection(verbose = verbose, readonly = False, connection_name = connection_name, autocommit = autocommit)

	#--------------------------------------------------
	def get_raw_connection(self, verbose:bool=False, readonly:bool=True, connection_name:str=None, autocommit:bool=False, credentials:cPGCredentials=None) -> dbapi._psycopg.connection:
		"""Get a raw, unadorned connection.

		This will not set any parameters such as encoding,
		timezone, or datestyle, hence it can be used for
		"service" connections for verifying encodings etc
		"""
#		# FIXME: support verbose
		if credentials is None:
			creds2use = self.__creds
		else:
			creds2use = credentials
		creds_kwargs = creds2use.generate_credentials_kwargs(connection_name = connection_name)
		try:
			# DictConnection now _is_ a real dictionary
			conn = dbapi.connect(connection_factory = psycopg2.extras.DictConnection, **creds_kwargs)
		except dbapi.OperationalError as e:
			_log.error('failed to establish connection [%s]', creds2use.formatted_credentials)
			t, v, tb = sys.exc_info()
			try:
				msg = e.args[0]
			except (AttributeError, IndexError, TypeError):
				raise

			if not self.__is_auth_fail_msg(msg):
				raise

			raise cAuthenticationError(creds2use.formatted_credentials, msg).with_traceback(tb)

		_log.debug('established connection "%s", backend PID: %s', gmTools.coalesce(connection_name, 'anonymous'), conn.get_backend_pid())
		# safe-guard
		conn._original_rollback = conn.rollback
		conn.rollback = types.MethodType(_safe_transaction_rollback, conn)

		# - inspect server
		self.__log_on_first_contact(conn)
		# - verify PG understands client time zone
		self.__detect_client_timezone(conn)
		# - set access mode
		if readonly:
			_log.debug('readonly: forcing autocommit=True to avoid <IDLE IN TRANSACTION>')
			autocommit = True
		else:
			_log.debug('autocommit is desired to be: %s', autocommit)
		conn.commit()
		conn.autocommit = autocommit
		conn.readonly = readonly
		# - assume verbose=True to mean we want debugging in the database, too
		if verbose or _VERBOSE_PG_LOG:
			_log.debug('enabling <plpgsql.extra_warnings/_errors>')
			curs = conn.cursor()
			try:
				curs.execute("SET plpgsql.extra_warnings TO 'all'")
			except Exception:
				_log.exception('cannot enable <plpgsql.extra_warnings>')
			finally:
				curs.close()
				conn.commit()
			curs = conn.cursor()
			try:
				curs.execute("SET plpgsql.extra_errors TO 'all'")
			except Exception:
				_log.exception('cannot enable <plpgsql.extra_errors>')
			finally:
				curs.close()
				conn.commit()
			_log.debug('enabling auto_explain')
			curs = conn.cursor()
			try:
				curs.execute("SELECT gm.load_auto_explain(3000)")
			except Exception:
				_log.exception('cannot enable auto_explain')
			finally:
				curs.close()
				conn.commit()
		return conn

	#--------------------------------------------------
	def get_dbowner_connection(self, readonly:bool=True, verbose:bool=False, connection_name:str=None, autocommit:bool=False, dbo_password:str=None, dbo_account:str='gm-dbo') -> dbapi._psycopg.connection:
		"""Return a connection for the database owner.

		Will not touch the pool.
		"""
		dbo_creds = cPGCredentials()
		dbo_creds.user = dbo_account
		dbo_creds.password = dbo_password
		dbo_creds.database = self.__creds.database
		dbo_creds.host = self.__creds.host
		dbo_creds.port = self.__creds.port
		return self.get_connection (
			pooled = False,
			readonly = readonly,
			verbose = verbose,
			connection_name = connection_name,
			autocommit = autocommit,
			credentials = dbo_creds
		)

	#--------------------------------------------------
	def discard_pooled_connection_of_thread(self):
		"""Discard from pool the connection of the current thread."""
		try:
			conn = self.__ro_conn_pool[self.pool_key]
		except KeyError:
			_log.debug('no connection pooled for thread [%s]', self.pool_key)
			return

		del self.__ro_conn_pool[self.pool_key]
		if conn.closed:
			return

		conn.close = conn.original_close
		conn.close()

	#--------------------------------------------------
	def shutdown(self):
		"""Close and discard all pooled connections."""
		for conn_key in self.__ro_conn_pool:
			conn = self.__ro_conn_pool[conn_key]
			if conn.closed:
				continue
			_log.debug('closing open database connection, pool key: %s', conn_key)
			log_conn_state(conn)
			conn.close = conn.original_close
			conn.close()
		del self.__ro_conn_pool

	#--------------------------------------------------
	# utility functions
	#--------------------------------------------------
	def __log_on_first_contact(self, conn:dbapi._psycopg.connection):
		global postgresql_version
		if postgresql_version is not None:
			return

		_log.debug('_\\\\// heed Prime Directive _\\\\//')
		# FIXME: verify PG version
		curs = conn.cursor()
		curs.execute ("""
			SELECT
				substring(setting, E'^\\\\d{1,2}\\\\.\\\\d{1,2}')::numeric AS version
			FROM
				pg_settings
			WHERE
				name = 'server_version'"""
		)
		postgresql_version = curs.fetchone()['version']
		_log.info('PostgreSQL version (numeric): %s' % postgresql_version)
		try:
			curs.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
			_log.info('database size: %s', curs.fetchone()[0])
		except Exception:
			_log.exception('cannot get database size')
		finally:
			curs.close()
			conn.commit()
		curs = conn.cursor()
		log_pg_settings(curs = curs)
		curs.close()
		conn.commit()
		_log.debug('done')

	#--------------------------------------------------
	def __log_auth_environment(self):
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
				_log.debug('$PGPASSFILE=%s -> file exists', pgpass_var)
			else:
				_log.debug('$PGPASSFILE=%s -> file not found')

	#--------------------------------------------------
	def __detect_client_timezone(self, conn:dbapi._psycopg.connection):
		"""This is run on the very first connection."""

		if self.__client_timezone is not None:
			return

		_log.debug('trying to detect timezone from system')
		# we need gmDateTime to be initialized
		if gmDateTime.current_local_iso_numeric_timezone_string is None:
			gmDateTime.init()
		tz_candidates = [gmDateTime.current_local_timezone_name]
		try:
			tz_candidates.append(os.environ['TZ'])
		except KeyError:
			pass
		expanded_tzs = []
		for tz in tz_candidates:
			expanded = self.__expand_timezone(conn, timezone = tz)
			if expanded != tz:
				expanded_tzs.append(expanded)
		tz_candidates.extend(expanded_tzs)
		_log.debug('candidates: %s', tz_candidates)
		# find best among candidates
		found = False
		for tz in tz_candidates:
			if self.__validate_timezone(conn = conn, timezone = tz):
				self.__client_timezone = tz
				self.__SQL_set_client_timezone = 'SET timezone TO %(tz)s'
				found = True
				break
		if not found:
			self.__client_timezone = gmDateTime.current_local_iso_numeric_timezone_string
			self.__SQL_set_client_timezone = 'set time zone interval %(tz)s hour to minute'
		_log.info('client system timezone detected as equivalent to [%s]', self.__client_timezone)
		# FIXME: check whether server.timezone is the same
		# FIXME: value as what we eventually detect

	#--------------------------------------------------
	def __expand_timezone(self, conn:dbapi._psycopg.connection, timezone:str):
		"""Some timezone defs are abbreviations so try to expand
		them because "set time zone" doesn't take abbreviations"""

		cmd = _SQL_expand_tz_name
		args = {'tz': timezone}
		conn.commit()
		curs = conn.cursor()
		result = timezone
		try:
			curs.execute(cmd, args)
			rows = curs.fetchall()
		except Exception:
			_log.exception('cannot expand timezone abbreviation [%s]', timezone)
		finally:
			curs.close()
			conn.rollback()
		if rows:
			result = rows[0]['name']
			_log.debug('[%s] maps to [%s]', timezone, result)
		return result

	#---------------------------------------------------
	def __validate_timezone(self, conn:dbapi._psycopg.connection, timezone:str) -> bool:
		_log.debug('validating timezone [%s]', timezone)
		cmd = 'SET timezone TO %(tz)s'
		args = {'tz': timezone}
		curs = conn.cursor()
		try:
			curs.execute(cmd, args)
		except dbapi.DataError:
			_log.warning('timezone [%s] is not settable', timezone)
			return False

		except Exception:
			_log.exception('failed to set timezone to [%s]', timezone)
			return False

		finally:
			conn.rollback()
		_log.info('time zone [%s] is settable', timezone)
		# can we actually use it, though ?
		SQL = "SELECT '1931-03-26 11:11:11+0'::timestamp with time zone"
		try:
			curs.execute(SQL)
			curs.fetchone()
		except Exception:
			_log.exception('error using timezone [%s]', timezone)
			return False

		finally:
			curs.close()
			conn.rollback()
		_log.info('timezone [%s] is usable', timezone)
		return True

	#--------------------------------------------------
	# properties
	#--------------------------------------------------
	def _get_credentials(self) -> cPGCredentials:
		return self.__creds

	def _set_credentials(self, creds:cPGCredentials=None):
		if self.__creds is None:
			self.__creds = creds
			return

		_log.debug('invalidating pooled connections on credentials change')
		pool_key_start_from_curr_creds = self.__creds.formatted_credentials + '::thread='
		for pool_key in self.__ro_conn_pool:
			if not pool_key.startswith(pool_key_start_from_curr_creds):
				continue
			conn = self.__ro_conn_pool[pool_key]
			del self.__ro_conn_pool[pool_key]
			if conn.closed:
				del conn
				continue
			_log.debug('closing open database connection, pool key: %s', pool_key)
			log_conn_state(conn)
			conn.original_close()
			del conn
		self.__creds = creds

	credentials = property(_get_credentials, _set_credentials)

	#--------------------------------------------------
	def _get_pool_key(self) -> str:
		return '%s::thread=%s' % (
			self.__creds.formatted_credentials,
			threading.current_thread().ident
		)

	pool_key = property(_get_pool_key)

	#--------------------------------------------------
	def __is_auth_fail_msg(self, msg:str) -> bool:
		if 'fe_sendauth' in msg:
			return True

		if regex.search('user ".*" does not exist', msg) is not None:
			return True

		if 'uthenti' in msg:
			return True

		if ((
				(regex.search('user ".*"', msg) is not None)
					or
				(regex.search('(R|r)ol{1,2}e', msg) is not None)
			)
			and ('exist' in msg)
			and (regex.search('n(o|ich)t', msg) is not None)
		):
			return True

		# to the best of our knowledge
		return False

#============================================================
# internal helpers
#------------------------------------------------------------
def exception_is_connection_loss(exc: Exception) -> bool:
	"""Checks whether exception represents connection loss."""
	if not isinstance(exc, dbapi.Error):
		# not a PG/psycopg2 exception
		return False

	try:
		if isinstance(exc, dbapi.errors.AdminShutdown):
			_log.debug('indicates connection loss due to admin shutdown')
			return True

	except AttributeError:	# psycopg2 2.7/2.8 transition (no AdminShutdown exception)
		pass
	try:
		msg = '%s' % exc.args[0]
	except (AttributeError, IndexError, TypeError):
		_log.debug('cannot extract message from exception')
		return False

	_log.debug('interpreting: %s', msg)
	for snippet in _connection_loss_markers:
		if snippet in msg:
			_log.debug('indicates connection loss')
			return True

	is_conn_loss = (
		# OperationalError
		('erver' in msg)
			and
		(
			('terminat' in msg)
				or
			('abnorm' in msg)
				or
			('end' in msg)
				or
			('no route' in msg)
		)
	) or (
		# InterfaceError
		('onnect' in msg)
			and
		(
			('close' in msg)
				or
			('end' in msg)
		)
	)
	if is_conn_loss:
		_log.debug('indicates connection loss')
	return is_conn_loss

#------------------------------------------------------------
def log_pg_exception_details(exc: Exception) -> bool:
	"""Logs details from a database exception."""
	if not isinstance(exc, dbapi.Error):
		return False

	try:
		for arg in exc.args:
			_log.debug('exc.arg: %s', arg)
	except AttributeError:
		_log.debug('exception has no <.args>')
	_log.debug('pgerror: [%s]', exc.pgerror)
	if exc.pgcode is None:
		_log.debug('pgcode : %s', exc.pgcode)
	else:
		_log.debug('pgcode : %s (%s)', exc.pgcode, PG_error_codes.lookup(exc.pgcode))
	log_cursor_state(exc.cursor)
	try:
		diags = exc.diag
	except AttributeError:
		_log.debug('<.diag> not available')
		diags = None
	if diags is None:
		return True

	for attr in dir(diags):
		if attr.startswith('__'):
			continue
		val = getattr(diags, attr)
		if val is None:
			continue
		_log.debug('%s: %s', attr, val)
	return True

#--------------------------------------------------
def log_pg_settings(curs) -> bool:
	"""Log PostgreSQL server settings."""
	# config settings
	try:
		curs.execute('SELECT * FROM pg_settings')
	except dbapi.Error:
		_log.exception('cannot retrieve PG settings ("SELECT ... FROM pg_settings" failed)')
		return False

	settings = curs.fetchall()
	if settings:
		for setting in settings:
			if setting['unit'] is None:
				unit = ''
			else:
				unit = ' %s' % setting['unit']
			if setting['sourcefile'] is None:
				sfile = ''
			else:
				sfile = '// %s @ %s' % (setting['sourcefile'], setting['sourceline'])
			pending_restart = u''
			try:
				if setting['pending_restart']:
					pending_restart = u'// needs restart'
			except KeyError:
				pass	# 'pending_restart' does not exist in PG 9.4 yet
			_log.debug('%s: %s%s (set from: [%s] // session RESET will set to: [%s]%s%s)',
				setting['name'],
				setting['setting'],
				unit,
				setting['source'],
				setting['reset_val'],
				pending_restart,
				sfile
			)
	# extensions
	try:
		curs.execute('select pg_available_extensions()')
	except Exception:
		_log.exception('cannot log available PG extensions')
		return False

	extensions = curs.fetchall()
	if extensions:
		for ext in extensions:
			_log.debug('PG extension: %s', ext['pg_available_extensions'])
	else:
		_log.error('no PG extensions available')
	# log pg_config -- can only be read by superusers :-/
	# database collation
	try:
		curs.execute('SELECT *, pg_database_collation_actual_version(oid), pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database()')
	except dbapi.Error:
		_log.exception('cannot log actual collation version (probably PG < 15)')
		curs.execute('SELECT * FROM pg_database WHERE datname = current_database()')
	config = curs.fetchall()
	gmLog2.log_multiline(10, message = 'PG database config', text = gmTools.format_dict_like(dict(config[0]), tabular = True))
	return True

#--------------------------------------------------
def log_cursor_state(cursor) -> None:
	"""Log details about a DB-API cursor."""
	if cursor is None:
		_log.debug('cursor: None')
		return

	conn = cursor.connection
	tx_status = conn.get_transaction_status()
	if tx_status in [ psycopg2.extensions.TRANSACTION_STATUS_INERROR, psycopg2.extensions.TRANSACTION_STATUS_UNKNOWN ]:
		isolation_level = '<tx aborted or unknown, cannot retrieve>'
	else:
		isolation_level = conn.isolation_level
	try:
		conn_deferrable = conn.deferrable
	except AttributeError:
		conn_deferrable = '<unavailable>'
	if cursor.query is None:
		query = '<no query>'
	else:
		query = cursor.query.decode(errors = 'replace')
	if conn.closed != 0:
		backend_pid = '<conn closed, cannot retrieve>'
	else:
		backend_pid = conn.get_backend_pid()
	txt = """Cursor
 identity: %s; name: %s
 closed: %s; scrollable: %s; with hold: %s; arraysize: %s; itersize: %s;
 last rowcount: %s; rownumber: %s; lastrowid (OID): %s;
 last description: %s
 statusmessage: %s
Connection
 identity: %s; backend pid: %s; protocol version: %s;
 closed: %s; autocommit: %s; isolation level: %s; encoding: %s; async: %s; deferrable: %s; readonly: %s;
 TX status: %s; CX status: %s; executing async op: %s;
Query
 %s""" % (
		# cursor level:
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
		# connection level:
		id(conn),
		backend_pid,
		conn.protocol_version,
		conn.closed,
		conn.autocommit,
		isolation_level,
		conn.encoding,
		conn.async_,
		conn_deferrable,
		conn.readonly,
		_map_psyco_tx_status2str[tx_status],
		_map_psyco_conn_status2str[conn.status],
		conn.isexecuting(),
		# query level:
		query
	)
	gmLog2.log_multiline(logging.DEBUG, message = 'Link state:', line_prefix = '', text = txt)

#--------------------------------------------------
def log_conn_state(conn:dbapi._psycopg.connection) -> None:
	"""Log details about a DB-API connection."""
	tx_status = conn.get_transaction_status()
	if tx_status in [ psycopg2.extensions.TRANSACTION_STATUS_INERROR, psycopg2.extensions.TRANSACTION_STATUS_UNKNOWN ]:
		isolation_level = '%s (tx aborted or unknown, cannot retrieve)' % conn.isolation_level
	else:
		isolation_level = '%s (%s)' % (conn.isolation_level, _map_psyco_iso_level2str[conn.isolation_level])
	conn_status = '%s (%s)' % (conn.status, _map_psyco_conn_status2str[conn.status])
	if conn.closed != 0:
		conn_status = 'undefined (%s)' % conn_status
		backend_pid = '<conn closed, cannot retrieve>'
	else:
		backend_pid = conn.get_backend_pid()
	try:
		conn_deferrable = conn.deferrable
	except AttributeError:
		conn_deferrable = '<unavailable>'
	d = {
		'identity': id(conn),
		'backend PID': backend_pid,
		'protocol version': conn.protocol_version,
		'encoding': conn.encoding,
		'closed': conn.closed,
		'readonly': conn.readonly,
		'autocommit': conn.autocommit,
		'isolation level (psyco)': isolation_level,
		'async': conn.async_,
		'deferrable': conn_deferrable,
		'transaction status': '%s (%s)' % (tx_status, _map_psyco_tx_status2str[tx_status]),
		'connection status': conn_status,
		'executing async op': conn.isexecuting(),
		'type': type(conn)
	}
	_log.debug(conn)
	for key in d:
		_log.debug('%s: %s', key, d[key])

#------------------------------------------------------------
def _safe_transaction_rollback(self) -> bool:
	"""Make connection.rollback() somewhat fault tolerant.

	Will *not* fail if the connection is already closed.

	Args:
		conn: a psycopg2 connection object
	"""
	if self.closed:
		_log.debug('fishy: connection already closed, cannot roll back')
		return True

	return self._original_rollback()

#------------------------------------------------------------
def _raise_exception_on_pooled_ro_conn_close():
	call_stack = inspect.stack()
	call_stack.reverse()
	for idx in range(1, len(call_stack)):
		caller = call_stack[idx]
		_log.debug('%s[%s] @ [%s] in [%s]', ' '* idx, caller[3], caller[2], caller[1])
	del call_stack
	raise TypeError('close() called on read-only connection')

#========================================================================
class cAuthenticationError(dbapi.OperationalError):

	def __init__(self, creds=None, prev_val=None):
		self.creds = creds
		self.prev_val = prev_val

	def __str__(self):
		return 'PostgreSQL: %sDSN: %s' % (self.prev_val, self.creds)

#============================================================
# Python -> PostgreSQL
#------------------------------------------------------------
# test when Squeeze (and thus psycopg2 2.2 becomes Stable
class cAdapterPyDateTime(object):

	def __init__(self, dt):
		if dt.tzinfo is None:
			raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % _timestamp_template % dt.isoformat())
		self.__dt = dt

	def getquoted(self):
		return _timestamp_template % self.__dt.isoformat()

#============================================================
# main
#------------------------------------------------------------
# make sure psycopg2 knows how to handle unicode ...
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2._psycopg.UNICODEARRAY)

# tell psycopg2 how to adapt datetime types with timestamps when locales are in use
# check in 0.9:
psycopg2.extensions.register_adapter(pydt.datetime, cAdapterPyDateTime)

# turn dict()s into JSON - only works > 9.2
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

# do NOT adapt *lists* to "... IN (*) ..." syntax because we want
# them adapted to "... ARRAY[]..." so we can support PG arrays

#============================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------------------
	def test_exceptions():
		print("testing exceptions")

		try:
			raise cAuthenticationError('no credentials', 'no previous exception')
		except cAuthenticationError:
			t, v, tb = sys.exc_info()
			print(t)
			print(v)
			print(tb)

	#--------------------------------------------------------------------
	def test_verbose_get_connection():
		creds = cPGCredentials()
		creds.database = 'gnumed_v22'
		creds.user = 'any-doc'
		pool = gmConnectionPool()
		pool.credentials = creds
		conn = pool.get_connection(verbose = True)
		#conn = pool.get_connection(verbose = False)
		curs = conn.cursor()
		curs.execute('select pg_sleep(4);')

	#--------------------------------------------------------------------
	def test_get_connection():
		print("testing get_connection() from new pool")

		pool = gmConnectionPool()
		creds = cPGCredentials()
		pool.credentials = creds

		print('')
		try:
			_log.debug('3')
			conn = pool.get_connection()
			print("1) ERROR: get_connection() did not fail")
		except AssertionError:
			_log.error('failed, as expected')
			print("1) SUCCESS: get_connection(%s) failed as expected" % pool)
			t, v = sys.exc_info()[:2]
			print (' ', t)
			print (' ', v)

		print('')
		creds.database = 'gnumed_v22'
		try:
			conn = pool.get_connection()
			print("2) ERROR: get_connection() did not fail")
		except AssertionError:
			_log.error('failed, as expected')
			print("2) SUCCESS: get_connection() failed as expected")
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		creds.database = 'gnumed_v22'
		creds.user = 'abc'
		try:
			conn = pool.get_connection()
			print("3) ERROR: get_connection() did not fail")
		except cAuthenticationError:
			_log.error('failed, as expected')
			print("3) SUCCESS: get_connection() failed as expected")
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		creds.database = 'gnumed_v22'
		creds.user = 'any-doc'
		creds.password = 'abcd'
		try:
			conn = pool.get_connection()
			print("4) ERROR: get_connection() did not fail")
		except cAuthenticationError:
			_log.error('failed, as expected')
			print("4) SUCCESS: get_connection() failed as expected")
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		creds.password = 'any-doc'
		conn = pool.get_connection(readonly=True)
		print('5) SUCCESS: get_connection(ro)')

		print('')
		conn = pool.get_connection(readonly=False, verbose=True)
		print('6) SUCCESS: get_connection(rw)')

		print('')
		try:
			conn = pool.get_connection()
			print("7) SUCCESS:")
			print('pid:', conn.get_backend_pid())
		except cAuthenticationError:
			print("7) SUCCESS: get_connection() failed")
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		try:
			conn = pool.get_connection()
			curs = conn.cursor()
			input('hit enter to run query')
			curs.execute('selec 1')
		except Exception as exc:
			_log.error('failed, as expected')
			print('ERROR')
			_log.exception('exception occurred')
			log_pg_exception_details(exc)
			if exception_is_connection_loss(exc):
				_log.error('lost connection')

		try:
			conn = pool.get_connection()
			curs = conn.cursor()
			input('hit enter to run query')
			curs.execute('select 1 from table_does_not_exist')
		except Exception as exc:
			_log.error('failed, as expected')
			print('ERROR')
			_log.exception('exception occurred')
			log_pg_exception_details(exc)
			if exception_is_connection_loss(exc):
				_log.error('lost connection')

	#--------------------------------------------------------------------
	def test_change_creds():
		print("testing credentials change")
		pool = gmConnectionPool()
		creds = cPGCredentials()
		creds.database = 'gnumed_v22'
		creds.user = 'any-doc'
		pool.credentials = creds
		conn = pool.get_connection()
		_log.debug('changing credentials')
		creds.user = 'gm-dbo'
		pool.credentials = creds
		conn = pool.get_connection()
		print(conn)

	#--------------------------------------------------------------------
	def test_credentials():
		print("testing credentials with spaces")
		pool = gmConnectionPool()
		creds = cPGCredentials()
		creds.database = 'gnumed_v22'
		creds.user = 'any-doc'
		creds.password = 'any-doc'
		pool.credentials = creds
		conn = pool.get_connection()
		print(conn)
		creds.password = 'a - b'
		pool.credentials = creds
		conn = pool.get_connection()

	#--------------------------------------------------------------------
	#test_credentials()
	#test_exceptions()
	#test_get_connection()
	test_verbose_get_connection()
	#test_change_creds()
