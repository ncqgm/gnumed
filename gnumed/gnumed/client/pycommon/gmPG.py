

# This remains for documentation only.
raise ImportError('This module is deprecated. Use gmPG2.py.')



"""Broker for PostgreSQL distributed backend connections.

@copyright: author

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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmPG.py,v $
__version__ = "$Revision: 1.90 $"
__author__  = "H.Herb <hherb@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

print "gmPG phased out, please replace with gmPG2"

import sys
sys.exit

_query_logging_verbosity = 1

# check whether this adapter module suits our needs
assert(float(dbapi.apilevel) >= 2.0)
assert(dbapi.threadsafety > 0)
assert(dbapi.paramstyle == 'pyformat')

_listener_api = None

# default encoding for connections
_default_client_encoding = {'wire': None, 'string': None}

# default time zone for connections
# OR: mxDT.now().gmtoffset()
if time.daylight:
	tz = time.altzone
else:
	tz = time.timezone
# do some magic to convert Python's timezone to a valid ISO timezone
# is this safe or will it return things like 13.5 hours ?
_default_client_timezone = "%+.1f" % (-tz / 3600.0)

_serialize_failure = "serialize access due to concurrent update"

#======================================================================
# a bunch of useful queries
#----------------------------------------------------------------------
QTablePrimaryKeyIndex = """
SELECT
	indkey
FROM
	pg_index
WHERE
	indrelid =
	(SELECT oid FROM pg_class WHERE relname = '%s');
"""

query_pkey_name = """
SELECT
	pga.attname
FROM
	(pg_attribute pga inner join pg_index pgi on (pga.attrelid=pgi.indrelid))
WHERE
	pga.attnum=pgi.indkey[0]
		and
	pgi.indisprimary is true
		and
	pga.attrelid=(SELECT oid FROM pg_class WHERE relname = %s)"""

query_fkey_names = """
select tgargs from pg_trigger where
	tgname like 'RI%%'
		and
	tgrelid = (
		select oid from pg_class where relname=%s
	)
"""

# get columns and data types for a given table
query_table_col_defs = """select
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

query_table_attributes = """select
	cols.column_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

query_child_tables = """
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


# a handy return to dbapi simplicity
last_ro_cursor_desc = None

#======================================================================
class ConnectionPool:
	"maintains a static dictionary of available database connections"

	# cached read-only connection objects
	__ro_conns = {}
	# maps service names to physical databases
	__service2db_map = {}
	# connections in use per service (for reference counting)
	__conn_use_count = {}
	# variable used to check whether a first connection has been initialized yet or not
	__is_connected = None
	# maps backend listening threads to database ids
	__listeners = {}
	# gmLoginInfo.LoginInfo instance
	__login = None
	#-----------------------------
	def __init__(self, login=None, encoding=None):
		"""parameter login is of type gmLoginInfo.LoginInfo"""
		# if login data is given: re-establish connections
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__is_connected is None:
			# CAREFUL: this affects the whole connection
			dbapi.fetchReturnsList = True
			ConnectionPool.__is_connected = self.__setup_default_ro_conns(login=login, encoding=encoding)
	#-----------------------------
	def __del__(self):
		pass
		# NOTE: do not kill listeners here which would mean to
		# kill them when we throw away *any* ConnectionPool
		# instance - not what we want
	#-----------------------------
	# connection API
	#-----------------------------
	def GetConnection(self, service="default", readonly=1, encoding=None, extra_verbose=None):
		"""Get a connection."""

		logininfo = self.GetLoginInfoFor(service)

		# either get a cached read-only connection
		if readonly:
			if ConnectionPool.__ro_conns.has_key(service):
				try:
					ConnectionPool.__conn_use_count[service] += 1
				except KeyError:
					ConnectionPool.__conn_use_count[service] = 1
				conn = ConnectionPool.__ro_conns[service]
			else:
				try:
					ConnectionPool.__conn_use_count['default'] += 1
				except KeyError:
					ConnectionPool.__conn_use_count['default'] = 1
				conn = ConnectionPool.__ro_conns['default']
		# or a brand-new read-write connection
		else:
			_log.Log(gmLog.lData, "requesting RW connection to service [%s]" % service)
			conn = self.__pgconnect(logininfo, readonly = 0, encoding = encoding)
			if conn is None:
				return None

		if extra_verbose:
			conn.conn.toggleShowQuery

		return conn
	#-----------------------------
	def ReleaseConnection(self, service):
		"""decrease reference counter of active connection"""
		if ConnectionPool.__ro_conns.has_key(service):
			try:
				ConnectionPool.__conn_use_count[service] -= 1
			except:
				ConnectionPool.__conn_use_count[service] = 0
		else:
			try:
				ConnectionPool.__conn_use_count['default'] -= 1
			except:
				ConnectionPool.__conn_use_count['default'] = 0
	#-----------------------------
	def Connected(self):
		return ConnectionPool.__is_connected
	#-----------------------------
	def get_connection_for_user(self, user=None, password=None, service="default", encoding=None, extra_verbose=None):
		"""Get a connection for a given user.

		This will return a connection just as GetConnection() would
		except that the user to be used for authentication can be
		specified. All the other parameters are going to be the
		same, IOW it will connect to the same server, port and database
		as any other connection obtained through this broker.

		You will have to specify the password, of course, if it
		is needed for PostgreSQL authentication.

		This will always return a read-write connection.
		"""
		if user is None:
			_log.Log(gmLog.lErr, 'user must be given')
			raise ValueError, 'gmPG.py::%s.get_connection_for_user(): user name must be given' % self.__class__.__name__

		logininfo = self.GetLoginInfoFor(service)
		logininfo.SetUser(user=user)
		logininfo.SetPassword(passwd=password)

		_log.Log(gmLog.lData, "requesting RW connection to service [%s]" % service)
		conn = self.__pgconnect(logininfo, readonly = 0, encoding = encoding)
		if conn is None:
			return None

		if extra_verbose:
			conn.conn.toggleShowQuery

		return conn
	#-----------------------------
	# notification API
	#-----------------------------
	def Listen(self, service, signal, callback):
		"""Listen to 'signal' from backend in an asynchronous thread.

		If 'signal' is received from database 'service', activate
		the 'callback' function"""
		# FIXME: error handling

		# lazy import of gmBackendListener
		if _listener_api is None:
			if not _import_listener_engine():
				_log.Log(gmLog.lErr, 'cannot load backend listener code')
				return None

		# get physical database for service
		try:
			backend = ConnectionPool.__service2db_map[service]
		except KeyError:
			backend = 0
		_log.Log(gmLog.lData, "connecting notification [%s] from service [%s] (id %s) with callback %s" % (signal, service, backend, callback))
		# start thread if not listening yet,
		# but only one per physical database
		if backend not in ConnectionPool.__listeners.keys():
			auth = self.GetLoginInfoFor(service)
			listener = _listener_api.BackendListener(
				service,
				auth.GetDatabase(),
				auth.GetUser(),
				auth.GetPassword(),
				auth.GetHost(),
				int(auth.GetPort())
			)
			ConnectionPool.__listeners[backend] = listener
		# actually start listening
		listener = ConnectionPool.__listeners[backend]
		listener.register_callback(signal, callback)
		return 1
	#-----------------------------
	def Unlisten(self, service, signal, callback):
		# get physical database for service
		try:
			backend = ConnectionPool.__service2db_map[service]
		except KeyError:
			backend = 0
		_log.Log(gmLog.lData, "disconnecting notification [%s] from service [%s] (id %s) from callback %s" % (signal, service, backend, callback))
		if backend not in ConnectionPool.__listeners.keys():
			return 1
		listener = ConnectionPool.__listeners[backend]
		listener.unregister_callback(signal, callback)
	#-----------------------------
	def StopListener(self, service):
		try:
			backend = self.__service2db_map[service]
		except KeyError:
			_log.Log(gmLog.lWarn, 'cannot stop listener on backend')
			return None
		try:
			ConnectionPool.__listeners[backend].stop_thread()
			del ConnectionPool.__listeners[backend]
		except:
			_log.LogException('cannot stop listener on backend [%s]' % backend, sys.exc_info(), verbose = 0)
			return None
		return 1
	#-----------------------------
	def StopListeners(self):
		for backend in ConnectionPool.__listeners.keys():
			try:
				ConnectionPool.__listeners[backend].stop_thread()
				del ConnectionPool.__listeners[backend]
			except:
				_log.LogException('cannot stop listener on backend [%s]' % backend, sys.exc_info(), verbose = 0)
		return 1
	#-----------------------------
	# misc API
	#-----------------------------
	def GetAvailableServices(self):
		"""list all distributed services available on this system
		(according to configuration database)"""
		return ConnectionPool.__ro_conns.keys()
	#-----------------------------		
	def GetLoginInfoFor(self, service, login = None):
		"""return login information for a particular service"""
		if login is None:
			dblogin = ConnectionPool.__login
		else:
			dblogin = copy.deepcopy(login)
		# if service not mapped, return default login information
		try:
			srvc_id = ConnectionPool.__service2db_map[service]
		except KeyError:
			return dblogin
		# a service in the default database
		if srvc_id == 0:
			return dblogin
		# actually fetch parameters for db where service
		# is located from config DB
		cfg_db = ConnectionPool.__ro_conns['default']
		cursor = cfg_db.cursor()
		cmd = "select name, host, port from cfg.db where pk=%s"
		if not run_query(cursor, None, cmd, srvc_id):
			_log.Log(gmLog.lPanic, 'cannot get login info for service [%s] with id [%s] from config database' % (service, srvc_id))
			_log.Log(gmLog.lPanic, 'make sure your service-to-database mappings are properly configured')
			_log.Log(gmLog.lWarn, 'trying to make do with default login parameters')
			return dblogin
		auth_data = cursor.fetchone()
		idx = get_col_indices(cursor)
		cursor.close()
		# substitute values into default login data
		try: # db name
			dblogin.SetDatabase(string.strip(auth_data[idx['name']]))
		except: pass
		try: # host name
			dblogin.SetHost(string.strip(auth_data[idx['host']]))
		except: pass
		try: # port
			dblogin.SetPort(auth_data[idx['port']])
		except: pass
		# and return what we thus got - which may very well be identical to the default login ...
		return dblogin			
	#-----------------------------
	# private methods
	#-----------------------------
	def __setup_default_ro_conns(self, login=None, encoding=None):
		"""Initialize connections to all servers."""
		if login is None and ConnectionPool.__is_connected is None:
			try:
				login = request_login_params()
			except:
				_log.LogException("Exception: Cannot connect to databases without login information !", sys.exc_info(), verbose=1)
				raise gmExceptions.ConnectionError("Can't connect to database without login information!")

		_log.Log(gmLog.lData, login.GetInfoStr())
		ConnectionPool.__login = login

		# connect to the configuration server
		cfg_db = self.__pgconnect(login, readonly=1, encoding=encoding)
		if cfg_db is None:
			raise gmExceptions.ConnectionError, _('Cannot connect to configuration database with:\n\n[%s]') % login.GetInfoStr()

		# this is the default gnumed server now
		ConnectionPool.__ro_conns['default'] = cfg_db
		cursor = cfg_db.cursor()
		# document DB version
		cursor.execute("select version()")
		_log.Log(gmLog.lInfo, 'service [default/config] running on [%s]' % cursor.fetchone()[0])
		# preload all services with database pk 0 (default)
		cmd = "select name from cfg.distributed_db"
		if not run_query(cursor, None, cmd):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load service names from configuration database")
		services = cursor.fetchall()
		for service in services:
			ConnectionPool.__service2db_map[service[0]] = 0

		# establish connections to all servers we need
		# according to configuration database
		cmd = "select * from cfg.config where profile=%s"
		if not run_query(cursor, None, cmd, login.GetProfile()):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load user profile [%s] from database" % login.GetProfile())
		databases = cursor.fetchall()
		dbidx = get_col_indices(cursor)

		# for all configuration entries that match given user and profile
		for db in databases:
			# - get symbolic name of distributed service
			cursor.execute("select name from cfg.distributed_db where pk=%d" %  db[dbidx['ddb']])
			service = string.strip(cursor.fetchone()[0])
			# - map service name to id of real database
			_log.Log(gmLog.lData, "mapping service [%s] to DB ID [%s]" % (service, db[dbidx['db']]))
			ConnectionPool.__service2db_map[service] = db[dbidx['db']]
			# - init ref counter
			ConnectionPool.__conn_use_count[service] = 0
			dblogin = self.GetLoginInfoFor(service, login)
			# - update 'Database Broker' dictionary
			conn = self.__pgconnect(dblogin, readonly=1, encoding=encoding)
			if conn is None:
				raise gmExceptions.ConnectionError, _('Cannot connect to database with:\n\n[%s]') % login.GetInfoStr()
			ConnectionPool.__ro_conns[service] = conn
			# - document DB version
			cursor.execute("select version()")
			_log.Log(gmLog.lInfo, 'service [%s] running on [%s]' % (service, cursor.fetchone()[0]))
		cursor.close()
		ConnectionPool.__is_connected = 1
		return ConnectionPool.__is_connected
	#-----------------------------
	def __pgconnect(self, login, readonly=1, encoding=None):
		"""Connect to a postgres backend as specified by login object.

		- returns a connection object
		- encoding works like this:
			- encoding specified in the call to __pgconnect() overrides
			- encoding set by a call to gmPG.set_default_encoding() overrides
			- encoding taken from Python string encoding
		- wire_encoding and string_encoding must essentially just be different
		  names for one and the same (IOW entirely compatible) encodings, such
		  as "win1250" and "cp1250"
		"""
		dsn = ""
		hostport = ""
		dsn = login.GetDBAPI_DSN()
		hostport = "0"

		if encoding is None:
			encoding = _default_client_encoding

		# encoding a Unicode string with this encoding must
		# yield a byte string encoded such that it can be decoded
		# safely by wire_encoding
		string_encoding = encoding['string']
		if string_encoding is None:
			string_encoding = _default_client_encoding['string']
		if string_encoding is None:
#			string_encoding = sys.getdefaultencoding()
			string_encoding = locale.getlocale()[1]
			_log.Log(gmLog.lWarn, 'client encoding not specified, this may lead to data corruption in some cases')
			_log.Log(gmLog.lWarn, 'therefore the string encoding currently set in the active locale is used: [%s]' % string_encoding)
			_log.Log(gmLog.lWarn, 'for this to have any chance to work the application MUST have called locale.setlocale() before')
		_log.Log(gmLog.lInfo, 'using string encoding [%s] to encode Unicode strings for transmission to the database' % string_encoding)

		# Python does not necessarily have to know this encoding by name
		# but it must know an equivalent encoding which guarantees roundtrip
		# equality (set that via string_encoding)
		wire_encoding = encoding['wire']
		if wire_encoding is None:
			wire_encoding = _default_client_encoding['wire']
		if wire_encoding is None:
			wire_encoding = string_encoding
		if wire_encoding is None:
			raise ValueError, '<wire_encoding> cannot be None'

		try:
			# FIXME: eventually use UTF or UTF8 for READONLY connections _only_
			conn = dbapi.connect(dsn=dsn, client_encoding=(string_encoding, 'strict'), unicode_results=1)
		except StandardError:
			_log.LogException("database connection failed: DSN = [%s], host:port = [%s]" % (dsn, hostport), sys.exc_info(), verbose = 1)
			return None

		# set the default characteristics of our sessions
		curs = conn.cursor()

		# - client encoding
		cmd = "set client_encoding to '%s'" % wire_encoding
		try:
			curs.execute(cmd)
		except:
			curs.close()
			conn.close()
			_log.Log(gmLog.lErr, 'query [%s]' % cmd)
			_log.LogException (
				'cannot set string-on-the-wire client_encoding on connection to [%s], this would likely lead to data corruption' % wire_encoding,
				sys.exc_info(),
				verbose = _query_logging_verbosity
			)
			raise
		_log.Log(gmLog.lData, 'string-on-the-wire client_encoding set to [%s]' % wire_encoding)

		# - client time zone
#		cmd = "set session time zone interval '%s'" % _default_client_timezone
		cmd = "set time zone '%s'" % _default_client_timezone
		if not run_query(curs, None, cmd):
			_log.Log(gmLog.lErr, 'cannot set client time zone to [%s]' % _default_client_timezone)
			_log.Log(gmLog.lWarn, 'not setting this will lead to incorrect dates/times')
		else:
			_log.Log (gmLog.lData, 'time zone set to [%s]' % _default_client_timezone)

		# - datestyle
		# FIXME: add DMY/YMD handling
		cmd = "set datestyle to 'ISO'"
		if not run_query(curs, None, cmd):
			_log.Log(gmLog.lErr, 'cannot set client date style to ISO')
			_log.Log(gmLog.lWarn, 'you better use other means to make your server delivers valid ISO timestamps with time zone')

		# - transaction isolation level
		if readonly:
			isolation_level = 'READ COMMITTED'
		else:
			isolation_level = 'SERIALIZABLE'
		cmd = 'set session characteristics as transaction isolation level %s' % isolation_level
		if not run_query(curs, None, cmd):
			curs.close()
			conn.close()
			_log.Log(gmLog.lErr, 'cannot set connection characteristics to [%s]' % isolation_level)
			return None

		# - access mode
		if readonly:
			access_mode = 'READ ONLY'
		else:
			access_mode = 'READ WRITE'
		_log.Log(gmLog.lData, "setting session to [%s] for %s@%s:%s" % (access_mode, login.GetUser(), login.GetHost(), login.GetDatabase()))
		cmd = 'set session characteristics as transaction %s' % access_mode
		if not run_query(curs, 0, cmd):
			_log.Log(gmLog.lErr, 'cannot set connection characteristics to [%s]' % access_mode)
			curs.close()
			conn.close()
			return None

		conn.commit()
		curs.close()
		return conn
	#-----------------------------
	def __disconnect(self, force_it=0):
		"""safe disconnect (respecting possibly active connections) unless the force flag is set"""
		# are we connected at all?
		if ConnectionPool.__is_connected is None:
			# just in case
			ConnectionPool.__ro_conns.clear()
			return
		# stop all background threads
		for backend in ConnectionPool.__listeners.keys():
			ConnectionPool.__listeners[backend].stop_thread()
			del ConnectionPool.__listeners[backend]
		# disconnect from all databases
		for key in ConnectionPool.__ro_conns.keys():
			# check whether this connection might still be in use ...
			if ConnectionPool.__conn_use_count[key] > 0 :
				# unless we are really mean
				if force_it == 0:
					# let the end user know that shit is happening
					raise gmExceptions.ConnectionError, "Attempting to close a database connection that is still in use"
			else:
				# close the connection
				ConnectionPool.__ro_conns[key].close()

		# clear the dictionary (would close all connections anyway)
		ConnectionPool.__ro_conns.clear()
		ConnectionPool.__is_connected = None

#---------------------------------------------------
# database helper functions
#---------------------------------------------------
def fieldNames(cursor):
	"returns the attribute names of the fetched rows in natural sequence as a list"
	names=[]
	for d in cursor.description:
		names.append(d[0])
	return names
#---------------------------------------------------
def run_query(aCursor=None, verbosity=None, aQuery=None, *args):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to run query')
		return None
	if aQuery is None:
		_log.Log(gmLog.lErr, 'need query to run it')
		return None
	if verbosity is None:
		verbosity = _query_logging_verbosity

#	t1 = time.time()
	try:
		aCursor.execute(aQuery, *args)
	except:
		_log.LogException("query >>>%s<<< with args >>>%s<<< failed" % (aQuery, args), sys.exc_info(), verbose = verbosity)
		return None
#	t2 = time.time()
#	print t2-t1, aQuery
	return 1
#---------------------------------------------------
def run_commit2(link_obj=None, queries=None, end_tx=False, max_tries=1, extra_verbose=False, get_col_idx = False):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	<link_obj>
		can be either:
		- a cursor
		- a connection
		- a service name

	<queries>
		is a list of (query, [args]) tuples to be
		executed as a single transaction, the last
		query may usefully return rows (such as a
		"select currval('some_sequence')" statement)

	<end_tx>
		- controls whether the transaction is finalized (eg.
		  committed/rolled back) or not, this allows the
		  call to run_commit2() to be part of a framing
		  transaction
		- if <link_obj> is a service name the transaction is
		  always finalized regardless of what <end_tx> says
		- if link_obj is a connection then <end_tx> will
		  default to False unless it is explicitly set to
		  True which is taken to mean "yes, you do have full
		  control over the transaction" in which case the
		  transaction is properly finalized

	<max_tries>
		- controls the number of times a transaction is retried
		  after a concurrency error
		- note that *all* <queries> are rerun if a concurrency
		  error occurrs
		- max_tries is honored if and only if link_obj is a service
		  name such that we have full control over the transaction

	<get_col_idx>
		- if true, the returned data will include a dictionary
		  mapping field names to column positions
		- if false, the returned data returns an empty dict

	method result:
		- returns a tuple (status, data)
		- <status>:
			* True - if all queries succeeded (also if there were 0 queries)
			* False - if *any* error occurred
		- <data> if <status> is True:
			* (None, {}) if last query did not return rows
			* ("fetchall() result", <index>) if last query returned any rows
			* for <index> see <get_col_idx>
		- <data> if <status> is False:
			* a tuple (error, message) where <error> can be:
			* 1: unspecified error
			* 2: concurrency error
			* 3: constraint violation (non-primary key)
			* 4: access violation
	"""
	# sanity checks
	if queries is None:
		return (False, (1, 'forgot to pass in queries'))
	if len(queries) == 0:
		return (True, 'no queries to execute')

	# check link_obj
	# is it a cursor ?
	if hasattr(link_obj, 'fetchone') and hasattr(link_obj, 'description'):
		return __commit2cursor(cursor=link_obj, queries=queries, extra_verbose=extra_verbose, get_col_idx=get_col_idx)
	# is it a connection ?
	if (hasattr(link_obj, 'commit') and hasattr(link_obj, 'cursor')):
		return __commit2conn(conn=link_obj, queries=queries, end_tx=end_tx, extra_verbose=extra_verbose, get_col_idx=get_col_idx)
	# take it to be a service name then
	return __commit2service(service=link_obj, queries=queries, max_tries=max_tries, extra_verbose=extra_verbose, get_col_idx=get_col_idx)
#---------------------------------------------------
def __commit2service(service=None, queries=None, max_tries=1, extra_verbose=False, get_col_idx=False):
	# sanity checks
	try: int(max_tries)
	except ValueEror: max_tries = 1
	if max_tries > 4:
		max_tries = 4
	if max_tries < 1:
		max_tries = 1
	# get cursor
	pool = ConnectionPool()
	conn = pool.GetConnection(str(service), readonly = 0)
	if conn is None:
		msg = 'cannot connect to service [%s]'
		_log.Log(gmLog.lErr, msg % service)
		return (False, (1, _(msg) % service))
	if extra_verbose:
		conn.conn.toggleShowQuery
	curs = conn.cursor()
	for attempt in range(0, max_tries):
		if extra_verbose:
			_log.Log(gmLog.lData, 'attempt %s' % attempt)
		# run queries
		for query, args in queries:
			if extra_verbose:
				t1 = time.time()
			try:
				curs.execute(query, *args)
			# FIXME: be more specific in exception catching
			except:
				if extra_verbose:
					duration = time.time() - t1
					_log.Log(gmLog.lData, 'query took %3.3f seconds' % duration)
				conn.rollback()
				exc_info = sys.exc_info()
				typ, val, tb = exc_info
				if str(val).find(_serialize_failure) > 0:
					_log.Log(gmLog.lData, 'concurrency conflict detected, cannot serialize access due to concurrent update')
					if attempt < max_tries:
						# jump to next full attempt
						time.sleep(0.1)
						continue
					curs.close()
					conn.close()
					return (False, (2, 'l'))
				# FIXME: handle more types of errors
				_log.Log(gmLog.lErr, 'query: %s'  % query[:2048])
				try:
					_log.Log(gmLog.lErr, 'argument: %s'  % str(args)[:2048])
				except MemoryError:
					pass
				_log.LogException("query failed on link [%s]" % service, exc_info)
				if extra_verbose:
					__log_PG_settings(curs)
				curs.close()
				conn.close()
				tmp = str(val).replace('ERROR:', '')
				tmp = tmp.replace('ExecAppend:', '')
				tmp = tmp.strip()
				return (False, (1, _('SQL: %s') % tmp))
			# apparently succeeded
			if extra_verbose:
				duration = time.time() - t1
				_log.Log(gmLog.lData, 'query: %s'  % query[:2048])
				try:
					_log.Log(gmLog.lData, 'args : %s'  % str(args)[:2048])
				except MemoryError:
					pass
				_log.Log(gmLog.lData, 'query succeeded on link [%s]' % service)
				_log.Log(gmLog.lData, '%s rows affected/returned in %3.3f seconds' % (curs.rowcount, duration))
		# done with queries
		break # out of retry loop
	# done with attempt(s)
	# did we get result rows in the last query ?
	data = None
	idx = {}
	# now, the DB-API is ambigous about whether cursor.description
	# and cursor.rowcount apply to the most recent query in a cursor
	# (does this statement make any sense in the first place ?) or
	# to the entire lifetime of said cursor, pyPgSQL thinks the
	# latter, hence we need to catch exceptions when there's no
	# data from the *last* query
	try:
		data = curs.fetchall()
	except:
		if extra_verbose:
			_log.Log(gmLog.lData, 'fetchall(): last query did not return rows')
		# should be None if no rows were returned ...
		if curs.description is not None:
			_log.Log(gmLog.lData, 'there seem to be rows but fetchall() failed -- DB API violation ?')
			_log.Log(gmLog.lData, 'rowcount: %s, description: %s' % (curs.rowcount, curs.description))
	conn.commit()
	if get_col_idx:
		idx = get_col_indices(curs)
	curs.close()
	conn.close()
	return (True, (data, idx))
#---------------------------------------------------
def __commit2conn(conn=None, queries=None, end_tx=False, extra_verbose=False, get_col_idx=False):
	if extra_verbose:
		conn.conn.toggleShowQuery

	# get cursor
	curs = conn.cursor()

	# run queries
	for query, args in queries:
		if extra_verbose:
			t1 = time.time()
		try:
			curs.execute(query, *args)
		except:
			if extra_verbose:
				duration = time.time() - t1
				_log.Log(gmLog.lData, 'query took %3.3f seconds' % duration)
			conn.rollback()
			exc_info = sys.exc_info()
			typ, val, tb = exc_info
			if str(val).find(_serialize_failure) > 0:
				_log.Log(gmLog.lData, 'concurrency conflict detected, cannot serialize access due to concurrent update')
				curs.close()
				if extra_verbose:
					conn.conn.toggleShowQuery
				return (False, (2, 'l'))
			# FIXME: handle more types of errors
			_log.Log(gmLog.lErr, 'query: %s'  % query[:2048])
			try:
				_log.Log(gmLog.lErr, 'args : %s'  % str(args)[:2048])
			except MemoryError:
				pass
			_log.LogException("query failed on link [%s]" % conn, exc_info)
			if extra_verbose:
				__log_PG_settings(curs)
			curs.close()
			tmp = str(val).replace('ERROR:', '')
			tmp = tmp.replace('ExecAppend:', '')
			tmp = tmp.strip()
			if extra_verbose:
				conn.conn.toggleShowQuery
			return (False, (1, _('SQL: %s') % tmp))
		# apparently succeeded
		if extra_verbose:
			duration = time.time() - t1
			_log.Log(gmLog.lData, 'query: %s'  % query[:2048])
			try:
				_log.Log(gmLog.lData, 'args : %s'  % str(args)[:2048])
			except MemoryError:
				pass
			_log.Log(gmLog.lData, 'query succeeded on link [%s]' % conn)
			_log.Log(gmLog.lData, '%s rows affected/returned in %3.3f seconds' % (curs.rowcount, duration))
	# done with queries
	if extra_verbose:
		conn.conn.toggleShowQuery
	# did we get result rows in the last query ?
	data = None
	idx = {}
	# now, the DB-API is ambigous about whether cursor.description
	# and cursor.rowcount apply to the most recent query in a cursor
	# (does this statement make any sense in the first place ?) or
	# to the entire lifetime of said cursor, pyPgSQL thinks the
	# latter, hence we need to catch exceptions when there's no
	# data from the *last* query
	try:
		data = curs.fetchall()
	except:
		if extra_verbose:
			_log.Log(gmLog.lData, 'fetchall(): last query did not return rows')
		# should be None if no rows were returned ...
		if curs.description is not None:
			_log.Log(gmLog.lData, 'there seem to be rows but fetchall() failed -- DB API violation ?')
			_log.Log(gmLog.lData, 'rowcount: %s, description: %s' % (curs.rowcount, curs.description))
	if end_tx:
		conn.commit()
	if get_col_idx:
		idx = get_col_indices(curs)
	curs.close()
	return (True, (data, idx))
#---------------------------------------------------
def __commit2cursor(cursor=None, queries=None, extra_verbose=False, get_col_idx=False):
	# run queries
	for query, args in queries:
		if extra_verbose:
			t1 = time.time()
		try:
			curs.execute(query, *args)
		except:
			if extra_verbose:
				duration = time.time() - t1
				_log.Log(gmLog.lData, 'query took %3.3f seconds' % duration)
			exc_info = sys.exc_info()
			typ, val, tb = exc_info
			if str(val).find(_serialize_failure) > 0:
				_log.Log(gmLog.lData, 'concurrency conflict detected, cannot serialize access due to concurrent update')
				return (False, (2, 'l'))
			# FIXME: handle more types of errors
			_log.Log(gmLog.lErr, 'query: %s'  % query[:2048])
			try:
				_log.Log(gmLog.lErr, 'args : %s'  % str(args)[:2048])
			except MemoryError:
				pass
			_log.LogException("query failed on link [%s]" % cursor, exc_info)
			if extra_verbose:
				__log_PG_settings(curs)
			tmp = str(val).replace('ERROR:', '')
			tmp = tmp.replace('ExecAppend:', '')
			tmp = tmp.strip()
			return (False, (1, _('SQL: %s') % tmp))
		# apparently succeeded
		if extra_verbose:
			duration = time.time() - t1
			_log.Log(gmLog.lData, 'query: %s'  % query[:2048])
			try:
				_log.Log(gmLog.lData, 'args : %s'  % str(args)[:2048])
			except MemoryError:
				pass
			_log.Log(gmLog.lData, 'query succeeded on link [%s]' % cursor)
			_log.Log(gmLog.lData, '%s rows affected/returned in %3.3f seconds' % (curs.rowcount, duration))

	# did we get result rows in the last query ?
	data = None
	idx = {}
	# now, the DB-API is ambigous about whether cursor.description
	# and cursor.rowcount apply to the most recent query in a cursor
	# (does this statement make any sense in the first place ?) or
	# to the entire lifetime of said cursor, pyPgSQL thinks the
	# latter, hence we need to catch exceptions when there's no
	# data from the *last* query
	try:
		data = curs.fetchall()
	except:
		if extra_verbose:
			_log.Log(gmLog.lData, 'fetchall(): last query did not return rows')
		# should be None if no rows were returned ...
		if curs.description is not None:
			_log.Log(gmLog.lData, 'there seem to be rows but fetchall() failed -- DB API violation ?')
			_log.Log(gmLog.lData, 'rowcount: %s, description: %s' % (curs.rowcount, curs.description))
	if get_col_idx:
		idx = get_col_indices(curs)
	return (True, (data, idx))
#---------------------------------------------------
def run_commit(link_obj = None, queries = None, return_err_msg = None):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	- link_obj can be
	  - a cursor: rollback/commit must be done by the caller
	  - a connection: rollback/commit is handled
	  - a service name: rollback/commit is handled

	- queries is a list of (query, [args]) tuples
	  - executed as a single transaction

	- returns:
	  - a tuple (<value>, error) if return_err_msg is True
	  - a scalar <value> if return_err_msg is False

	- <value> will be
	  - None: if any query failed
	  - 1: if all queries succeeded (also 0 queries)
      - data: if the last query returned rows
	"""
	print "DEPRECATION WARNING: gmPG.run_commit() is deprecated, use run_commit2() instead"

	# sanity checks
	if link_obj is None:
		raise TypeError, 'gmPG.run_commit(): link_obj must be of type service name, connection or cursor'
	if queries is None:
		raise TypeError, 'gmPG.run_commit(): forgot to pass in queries'
	if len(queries) == 0:
		_log.Log(gmLog.lWarn, 'no queries to execute ?!?')
		if return_err_msg:
			return (1, 'no queries to execute ?!?')
		return 1

	close_cursor = noop
	close_conn = noop
	commit = noop
	rollback = noop
	# is it a cursor ?
	if hasattr(link_obj, 'fetchone') and hasattr(link_obj, 'description'):
		curs = link_obj
	# is it a connection ?
	elif (hasattr(link_obj, 'commit') and hasattr(link_obj, 'cursor')):
		curs = link_obj.cursor()
		close_cursor = curs.close
		conn = link_obj
		commit = link_obj.commit
		rollback = link_obj.rollback
	# take it to be a service name then
	else:
		pool = ConnectionPool()
		conn = pool.GetConnection(link_obj, readonly = 0)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot connect to service [%s]' % link_obj)
			if return_err_msg:
				return (None, _('cannot connect to service [%s]') % link_obj)
			return None
		curs = conn.cursor()
		close_cursor = curs.close
		close_conn = conn.close
		commit = conn.commit
		rollback = conn.rollback
	# run queries
	for query, args in queries:
#		t1 = time.time()
		try:
			curs.execute (query, *args)
		except:
			rollback()
			exc_info = sys.exc_info()
			_log.LogException ("RW query >>>%s<<< with args >>>%s<<< failed on link [%s]" % (query[:1024], str(args)[:1024], link_obj), exc_info, verbose = _query_logging_verbosity)
			__log_PG_settings(curs)
			close_cursor()
			close_conn()
			if return_err_msg:
				typ, val, tb = exc_info
				tmp = string.replace(str(val), 'ERROR:', '')
				tmp = string.replace(tmp, 'ExecAppend:', '')
				tmp = string.strip(tmp)
				return (None, 'SQL: %s' % tmp)
			return None
#		t2 = time.time()
#		print t2-t1, query
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, '%s rows affected by >>>%s<<<' % (curs.rowcount, query))
	# did we get result rows in the last query ?
	data = None
	# now, the DB-API is ambigous about whether cursor.description
	# and cursor.rowcount apply to the most recent query in a cursor
	# (does that statement make any sense ?!?) or to the entire lifetime
	# of said cursor, pyPgSQL thinks the latter, hence we need to catch
	# exceptions when there's no data from the *last* query
	try:
		data = curs.fetchall()
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, 'last query returned %s rows' % curs.rowcount)
	except:
		if _query_logging_verbosity == 1:
			_log.Log(gmLog.lData, 'fetchall(): last query did not return rows')
		# something seems odd
		if curs.description is not None:
			if curs.rowcount > 0:
				_log.Log(gmLog.lData, 'there seem to be rows but fetchall() failed -- DB API violation ?')
				_log.Log(gmLog.lData, 'rowcount: %s, description: %s' % (curs.rowcount, curs.description))

	# clean up
	commit()
	close_cursor()
	close_conn()

	if data is None: status = 1
	else: status = data
	if return_err_msg: return (status, '')
	return status
#---------------------------------------------------
def run_ro_query(link_obj = None, aQuery = None, get_col_idx = False, *args):
	"""Runs a read-only query.

	- link_obj can be a service name, connection or cursor object

	- return status:
		- return data			if get_col_idx is False
		- return (data, idx)	if get_col_idx is True

	- if query fails: data is None
	- if query is not a row-returning SQL statement: data is None

	- data is a list of tuples [(w,x,y,z), (a,b,c,d), ...] where each tuple is a table row
	- idx is a map of column name to their position in the row tuples
		e.g. { 'name': 3, 'id':0, 'job_description': 2, 'location':1 }

		usage:  e.g. data[0][idx['name']] would return z from [(w,x,y,z ),(a,b,c,d)]
	"""
	# sanity checks
	if link_obj is None:
		raise TypeError, 'gmPG.run_ro_query(): link_obj must be of type service name, connection or cursor'
	if aQuery is None:
		raise TypeError, 'gmPG.run_ro_query(): forgot to pass in aQuery'

	close_cursor = noop
	close_conn = noop
	# is it a cursor ?
	if hasattr(link_obj, 'fetchone') and hasattr(link_obj, 'description'):
		curs = link_obj
	# is it a connection ?
	elif (hasattr(link_obj, 'commit') and hasattr(link_obj, 'cursor')):
		curs = link_obj.cursor()
		close_cursor = curs.close
	# take it to be a service name then
	else:
		pool = ConnectionPool()
		conn = pool.GetConnection(link_obj, readonly = 1)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot get connection to service [%s]' % link_obj)
			if not get_col_idx:
				return None
			else:
				return None, None
		curs = conn.cursor()
		close_cursor = curs.close
		close_conn = pool.ReleaseConnection
#	t1 = time.time()
	# run the query
	try:
		curs.execute(aQuery, *args)
		global last_ro_cursor_desc
		last_ro_cursor_desc = curs.description
	except:
		_log.LogException("query >>>%s<<< with args >>>%s<<< failed on link [%s]" % (aQuery[:250], str(args)[:250], link_obj), sys.exc_info(), verbose = _query_logging_verbosity)		# this can fail on *large* args
		__log_PG_settings(curs)
		close_cursor()
		close_conn(link_obj)
		if not get_col_idx:
			return None
		else:
			return None, None
#	t2 = time.time()
#	print t2-t1, aQuery
	# and return the data, possibly including the column index
	if curs.description is None:
		data = None
		_log.Log(gmLog.lErr, 'query did not return rows')
	else:
		try:
			data = curs.fetchall()
		except:
			_log.LogException('cursor.fetchall() failed on link [%s]' % link_obj, sys.exc_info(), verbose = _query_logging_verbosity)
			close_cursor()
			close_conn(link_obj)
			if not get_col_idx:
				return None
			else:
				return None, None

	# can "close" before closing cursor since it just decrements the ref counter
	close_conn(link_obj)
	if get_col_idx:
		col_idx = get_col_indices(curs)
		close_cursor()
		return data, col_idx
	else:
		close_cursor()
		return data
#---------------------------------------------------
#---------------------------------------------------
def get_col_indices(aCursor = None):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to get column indices')
		return None
	if aCursor.description is None:
		_log.Log(gmLog.lErr, 'no result description available: cursor unused or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in aCursor.description:
		col_indices[col_desc[0]] = col_index
		col_index += 1
	return col_indices
#---------------------------------------------------
#---------------------------------------------------
#---------------------------------------------------
def get_pkey_name(aCursor = None, aTable = None):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to determine primary key')
		return None
	if aTable is None:
		_log.Log(gmLog.lErr, 'need table name for which to determine primary key')

	if not run_query(aCursor, None, query_pkey_name, aTable):
		_log.Log(gmLog.lErr, 'cannot determine primary key')
		return -1
	result = aCursor.fetchone()
	if result is None:
		return None
	return result[0]
#---------------------------------------------------
def get_fkey_defs(source, table):
	"""Returns a dictionary of referenced foreign keys.

	key = column name of this table
	value = (referenced table name, referenced column name) tuple
	"""
	manage_connection = 0
	close_cursor = 1
	# is it a cursor ?
	if hasattr(source, 'fetchone') and hasattr(source, 'description'):
		close_cursor = 0
		curs = source
	# is it a connection ?
	elif (hasattr(source, 'commit') and hasattr(source, 'cursor')):
		curs = source.cursor()
	# take it to be a service name then
	else:
		manage_connection = 1
		pool = ConnectionPool()
		conn = pool.GetConnection(source)
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot get fkey names on table [%s] from source [%s]' % (table, source))
			return None
		curs = conn.cursor()

	if not run_query(curs, None, query_fkey_names, table):
		if close_cursor:
			curs.close()
		if manage_connection:
			pool.ReleaseConnection(source)
		_log.Log(gmLog.lErr, 'cannot get foreign keys on table [%s] from source [%s]' % (table, source))
		return None

	fks = curs.fetchall()
	if close_cursor:
		curs.close()
	if manage_connection:
		pool.ReleaseConnection(source)

	references = {}
	for fk in fks:
		fkname, src_table, target_table, tmp, src_col, target_col, tmp = string.split(fk[0], '\x00')
		references[src_col] = (target_table, target_col)

	return references
#---------------------------------------------------
def add_housekeeping_todo(
	reporter='$RCSfile: gmPG.py,v $ $Revision: 1.90 $',
	receiver='DEFAULT',
	problem='lazy programmer',
	solution='lazy programmer',
	context='lazy programmer',
	category='lazy programmer'
):
	queries = []
	cmd = "insert into housekeeping_todo (reported_by, reported_to, problem, solution, context, category) values (%s, %s, %s, %s, %s, %s)"
	queries.append((cmd, [reporter, receiver, problem, solution, context, category]))
	cmd = "select currval('housekeeping_todo_pk_seq')"
	queries.append((cmd, []))
	result, err = run_commit('historica', queries, 1)
	if result is None:
		_log.Log(gmLog.lErr, err)
		return (None, err)
	return (1, result[0][0])
#==================================================================
def __run_notifications_debugger():
	#-------------------------------
	def myCallback(**kwds):
		sys.stdout.flush()
		print "\n=== myCallback: got called ==="
		print kwds
	#-------------------------------

	dbpool = ConnectionPool()
	roconn = dbpool.GetConnection('default', extra_verbose=1)
	rocurs = roconn.cursor()

	# main shell loop
	print "PostgreSQL backend listener debug shell"
	while 1:
		print "---------------------------------------"
		typed = raw_input("=> ")
		args = typed.split(' ')
		# mothing typed ?
		if len(args) == 0:
			continue
		# help
		if args[0] in ('help', '?'):
			print "known commands"
			print "--------------"
			print "'listen' - start listening to a signal"
			print "'ignore' - stop listening to a signal"
			print "'send'   - send a signal"
			print "'quit', 'exit', 'done' - well, chicken out"
			continue
		# exit
		if args[0] in ('quit', 'exit', 'done'):
			break
		# signal stuff
		if args[0] in ("listen", "ignore", "send"):
			typed = raw_input("signal name: ")
			sig_names = typed.split(' ')
			# mothing typed ?
			if len(sig_names) == 0:
				continue
			if args[0] == "listen":
				dbpool.Listen('default', sig_names[0], myCallback)
			if args[0] == "ignore":
				dbpool.Unlisten('default', sig_names[0], myCallback)
			if args[0] == "send":
				cmd = 'NOTIFY "%s"' % sig_names[0]
				print "... running >>>%s<<<" % (cmd)
				if not run_query(rocurs, None, cmd):
					print "... error sending [%s]" % cmd
				roconn.commit()
			continue
		print 'unknown command [%s]' % typed

	# clean up
	print "please wait a second or two for threads to sync and die"
	dbpool.StopListener('default')
	rocurs.close()
	roconn.close()
	dbpool.ReleaseConnection('default')
#==================================================================
# Main - unit testing
#------------------------------------------------------------------
if __name__ == "__main__":
	_log.Log(gmLog.lData, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % ('PostgreSQL', dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))

	print "Do you want to test the backend notification code ?"
	yes_no = raw_input('y/n: ')
	if yes_no == 'y':
		__run_notifications_debugger()
		sys.exit()

	dbpool = ConnectionPool()
	### Let's see what services are distributed in this system:
	print "\n\nServices available on this system:"
	print '-----------------------------------------'
	for service in dbpool.GetAvailableServices():
		print service
		dummy = dbpool.GetConnection(service)
		print "\n.......................................\n"

	### We have probably not distributed the services in full:
	db = dbpool.GetConnection('config')
	print "\n\nPossible services on any gnumed system:"
	print '-----------------------------------------'
	cursor = db.cursor()
	cursor.execute("select name from cfg.distributed_db")
	for service in  cursor.fetchall():
		print service[0]

	print "\nTesting convenience funtions:\n============================\n"

	print "\nResult as dictionary\n==================\n"
	cur = db.cursor()
	cursor.execute("select * from cfg.db")
	d = dictResult(cursor)
	print d
	print "\nResult attributes\n==================\n"
	n = fieldNames(cursor)
	#-------------------------------
	def TestCallback():
		print "[Backend notification received!]"
	#-------------------------------
	print "\n-------------------------------------"
	print "Testing asynchronous notification for approx. 20 seconds"
	print "start psql in another window connect to gnumed"
	print "and type 'notify test'; if everything works,"
	print "a message [Backend notification received!] should appear\n"
	dbpool.Listen('default', 'test', TestCallback)
	time.sleep(20)
	dbpool.StopListener('default')
	print "Requesting write access connection:"
	con = dbpool.GetConnection('default', readonly=0)

#==================================================================
