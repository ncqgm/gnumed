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
__version__ = "$Revision: 1.3 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import time, locale, sys, re, os

# GNUmed
import gmLog, gmLoginInfo, gmExceptions
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# 3rd party
try:
	import psycopg2 as dbapi
	_log.Log(gmLog.lData, 'psycopg2 version: %s' % dbapi._psycopg.__version__)
	_log.Log(gmLog.lInfo, 'PostgreSQL via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
	assert(float(dbapi.apilevel) >= 2.0)
	assert(dbapi.threadsafety > 0)
	assert(dbapi.paramstyle == 'pyformat')
except ImportError:
	_log.LogException("Python database adapter psycopg2 not found.", sys.exc_info(), verbose=1)
	print "CRITICAL ERROR: Cannot find module psycopg2 for connecting to the database server."
	raise

import psycopg2.extras
import psycopg2.extensions

# =======================================================================

_default_client_encoding = 'utf8'
_log.Log(gmLog.lInfo, 'assuming default client encoding of [%s]' % _default_client_encoding)

# default time zone for connections
# OR: mxDT.now().gmtoffset()
if time.daylight:
	tz = time.altzone
else:
	tz = time.timezone
# do some magic to convert Python's timezone to a valid ISO timezone
# is this safe or will it return things like 13.5 hours ?
_default_client_timezone = "%+.1f" % (-tz / 3600.0)
_log.Log(gmLog.lInfo, 'assuming default client time zone of [%s]' % _default_client_timezone)
try:
	import mx.DateTime as mxDT
	_log.Log(gmLog.lInfo, 'mx.DateTime.now().gmtoffset() is: [%s]' % mxDT.now().gmtoffset())
	del mxDT
except: pass

_default_dsn = None

_v2_schema_hash = 'not released, testing only'
#_v2_schema_hash = 'b09d50d7ed3f91ddf4c4ddb8ea507720'
# =======================================================================
def set_default_client_encoding(encoding = None):
	# FIXME: maybe check encoding against codecs.lookup() ?
	# FIXME: or somehow check it against the database - but we may not yet have access
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

	dsn_parts.append('port=%s' % port)

	if (user is not None) and (user.strip() != ''):
		dsn_parts.append('user=%s' % user)

	if (password is not None) and (password.strip() != ''):
		dsn_parts.append('password=%s' % password)

	return ' '.join(dsn_parts)
# ------------------------------------------------------
def get_default_dsn():
	global _default_dsn
	if _default_dsn is not None:
		return _default_dsn

	login = request_login_params()
	dsn = make_psycopg2_dsn(login.database, login.host, login.port, login.user, login.password)
	set_default_dsn(dsn)

	return _default_dsn
# ------------------------------------------------------
def set_default_dsn(dsn = None):
	global _default_dsn
	_log.Log(gmLog.lInfo, 'setting default DSN from [%s] to [%s]' % (_default_dsn, dsn))
	_default_dsn = dsn
	return True
# =======================================================================
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
# =======================================================================
def run_ro_queries(link_obj=None, queries=None, verbose=False, return_data=True, get_col_idx=False):
	"""Run read-only queries.

	queries must be a list of dicts [{'cmd': <string>, 'args': <dict> or <tuple>}, {...}, ...]
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		curs = link_obj
		curs_close = __noop
		conn_close = __noop
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		conn_close = __noop
	elif link_obj is None:
		conn = get_connection()
		conn_close = conn.close
		curs = conn.cursor()
		curs_close = curs.close
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	for query in queries:
		try:
			args = query['args']
		except KeyError:
			args = (None,)
		try:
			curs.execute(query['cmd'], args)
		except:
			curs_close()
			conn_close()
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	conn_close()
	return (data, col_idx)
# =======================================================================
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
		conn_commit = link_obj.commit
		conn_rollback = link_obj.rollback
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
#		encoding = sys.getdefaultencoding()
		encoding = locale.getlocale()[1]
		_log.Log(gmLog.lWarn, 'client encoding not specified')
		_log.Log(gmLog.lWarn, 'the string encoding currently set in the active locale is used: [%s]' % encoding)
		_log.Log(gmLog.lWarn, 'for this to work the application MUST have called locale.setlocale() before')

	# set connection properties

	# 1) client encoding
	_log.Log(gmLog.lData, 'setting client string encoding to [%s]' % encoding)
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
		_log.Log(gmLog.lData, 'setting isolation level to [read committed]')
	else:
		conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
		_log.Log(gmLog.lData, 'setting isolation level to [serializable]')

	curs = conn.cursor()

	# 3) client time zone
	_log.Log(gmLog.lData, 'setting time zone to [%s]' % _default_client_timezone)
	cmd = "set time zone '%s'" % _default_client_timezone
	curs.execute(cmd)

	# 4) datestyle
	# FIXME: add DMY/YMD handling
	_log.Log(gmLog.lData, 'setting datestyle to [ISO]')
	cmd = "set datestyle to 'ISO'"
	curs.execute(cmd)

	# 5) access mode
	if readonly:
		access_mode = 'READ ONLY'
	else:
		access_mode = 'READ WRITE'
	_log.Log(gmLog.lData, 'setting access mode to [%s]' % access_mode)
	cmd = 'set session characteristics as transaction %s' % access_mode
	curs.execute(cmd)

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
		curs.execute('show all')
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
#  main
# -----------------------------------------------------------------------
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

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

		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': 'select version()'}], return_data=True, get_col_idx=True)
		print data
		print idx
		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': 'select 1'}], return_data=True, get_col_idx=True)
		print data
		print idx

		curs = conn.cursor()

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': 'select version()'}], return_data=True, get_col_idx=True)
		print data
		print idx

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': 'select 1'}], return_data=True, get_col_idx=True)
		print data
		print idx

		curs.close()
	#--------------------------------------------------------------------
	def test_request_dsn():
		conn = get_connection()
		print conn
		conn.close()
	#--------------------------------------------------------------------
	# run tests
	test_get_connection()
	test_exceptions()
	test_ro_queries()
	test_request_dsn()
	print "tests ran successfully"

# =======================================================================
# $Log: gmPG2.py,v $
# Revision 1.3  2006-09-30 11:57:48  ncq
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