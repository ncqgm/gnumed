"""Broker for Postgres distributed backend connections.

@copyright: author
@license: GPL (details at http://www.gnu.org)
"""
# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmPG.py,v $
__version__ = "$Revision: 1.60 $"
__author__  = "H.Herb <hherb@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>, K.Hilbert <Karsten.Hilbert@gmx.net>"

#python standard modules
import string, copy, os, sys, time

#gnumed specific modules
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmI18N, gmLoginInfo, gmExceptions, gmCLI

#3rd party dependencies

# FIXME: this needs a better way of specifying which library to
# load, add SQL-relay, too
# first, do we have the preferred postgres-python library available ?
try:
	import pyPgSQL.PgSQL # try preferred backend library
	dbapi = pyPgSQL.PgSQL
	_isPGDB = 0
except ImportError:
	try:
	# well, well, no such luck - fall back to stock pgdb library
		import psycopg # try Zope library
		dbapi = psycopg
		_isPGDB = 0
	except ImportError:
		try:
			import pgdb # try standard Postgres binding
			dbapi = pgdb
			_isPGDB = 1
		except ImportError:
			print "Cannot find any Python module for connecting to the database server. Program halted."
			_log.LogException("No Python database adapter found.", sys.exc_info(), fatal=1)
			raise

# FIXME: DBMS should eventually be configurable
__backend = 'Postgres'

_log.Log(gmLog.lInfo, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))

# check whether this adapter module suits our needs
assert(float(dbapi.apilevel) >= 2.0)
assert(dbapi.threadsafety > 0)
assert(dbapi.paramstyle == 'pyformat')


#=====================================================================

# convience function to escape strings for incorporation into SQL queries

def esc (s):
	return string.replace (s, "'", "''")

listener_api = None
#======================================================================
class ConnectionPool:
	"maintains a static dictionary of available database connections"

	#a dictionary with lists of databases; dictionary key is the name of the service
	__databases = {}
	#a dictionary mapping the physical databases to the services; key is service name
	__service2db_map = {}
	#number of connections in use for each service (for reference counting purposes)
	__connections_in_use = {}
	#variable used to check whether a first connection has been initialized yet or not
	__connected = None
	#a dictionary mapping all backend listening threads to database id
	__listeners = {}
	#gmLoginInfo.LoginInfo instance
	__login = None
	#-----------------------------
	def __init__(self, login=None):
		"""parameter login is of type gmLoginInfo.LoginInfo"""
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__connected is None:
			self.SetFetchReturnsList()
			ConnectionPool.__connected = self.__setup_default_ro_conns(login)
	#-----------------------------
	def __del__(self):
		for backend in ConnectionPool.__listeners.keys():
			ConnectionPool.__listeners[backend].tell_thread_to_stop()
			del ConnectionPool.__listeners[backend]
	#-----------------------------
	# connection API
	#-----------------------------
	def GetConnection(self, service = "default", readonly = 1, checked = 1):
		"""check connection is live"""

		conn =  self.GetConnectionUnchecked(service, readonly)
		if checked:
			try:
				cursor = conn.cursor()
				cursor.execute("select 1;")
				cursor.close()
			except StandardError:
				_log.LogException("connection is dead", sys.exc_info(), 4)
				_log.Data("trying a direct connection via __pgconnect()")
				# actually this sort of defies the whole thing since
				# GetLoginInfoFor() depends on GetConnection() ...
				logininfo = self.GetLoginInfoFor(service)
				conn = self.__pgconnect(logininfo, readonly)
				try:
					cursor = conn.cursor()
					cursor.execute("select 1;")
					cursor.close()
				except:
					_log.LogException("connection is dead", sys.exc_info(), 4)
					return  None

		return conn
	#-----------------------------
	def GetConnectionUnchecked(self, service = "default", readonly = 1):
		"""if a distributed service exists, return it - otherwise return the default server"""

		logininfo = self.GetLoginInfoFor(service)

		# get new read-write connection
		if not readonly:
			_log.Log(gmLog.lData, "requesting RW connection to service [%s]" % service)
			return self.__pgconnect(logininfo, readonly = 0)

		# return a cached read-only connection
		_log.Log(gmLog.lData, "requesting RO connection to service [%s]" % service)
		if ConnectionPool.__databases.has_key(service):
			try:
				ConnectionPool.__connections_in_use[service] += 1
			except:
				ConnectionPool.__connections_in_use[service] = 1
			return ConnectionPool.__databases[service]
		else:
			try:
				ConnectionPool.__connections_in_use['default'] += 1
			except:
				ConnectionPool.__connections_in_use['default'] = 1

			return ConnectionPool.__databases['default']
		
	#-----------------------------
	def ReleaseConnection(self, service):
		"decrease reference counter of active connection"
		if ConnectionPool.__databases.has_key(service):
			try:
				ConnectionPool.__connections_in_use[service] -= 1
			except:
				ConnectionPool.__connections_in_use[service] = 0
		else:
			try:
				ConnectionPool.__connections_in_use['default'] -= 1
			except:
				ConnectionPool.__connections_in_use['default'] = 0
	#-----------------------------
	def Connected(self):
		return ConnectionPool.__connected	
	#-----------------------------
	# notification API
	#-----------------------------
	def Listen(self, service, signal, callback):
		"""Listen to 'signal' from backend in an asynchronous thread.

		If 'signal' is received from database 'service', activate
		the 'callback' function"""
		# FIXME: error handling

		# lazy import of gmBackendListener
		if listener_api is None:
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
			listener = listener_api.BackendListener(
				service,
				auth.GetDatabase(),
				auth.GetUser(readonly=1),
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
			backend = 0
		try:
			self.__listeners[backend].tell_thread_to_stop()
			del self.__listeners[backend]
		except:
			pass
	#-----------------------------
	# misc API
	#-----------------------------
	def GetAvailableServices(self):
		"""list all distributed services available on this system
		(according to configuration database)"""
		return ConnectionPool.__databases.keys()
	#-----------------------------	
	def LogError(self, msg):
		"This function must be overridden by GUI applications"
	#-----------------------------		
	def SetFetchReturnsList(self, on=1):
		"""when performance is crucial, let the db adapter
		return a list of lists instead a list of database objects.
		CAREFUL: this affects the whole connection!!!"""
		if dbapi is pyPgSQL.PgSQL:
			dbapi.fetchReturnsList = on
		else:
			_log.Log(gmLog.lWarn, 'not supported with DB-API [%s], please supply a patch' % dbapi)
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
		cfg_db = ConnectionPool.__databases['config']
		cursor = cfg_db.cursor()
		cmd = "select name, host, port, opt, tty from db where id = %d" % srvc_id
		if not run_query(cursor, cmd):
			_log.Log(gmLog.lPanic, 'cannot get login info for service [%s] with id [%s] from config database' % (service, srvc_id))
			_log.Log(gmLog.lPanic, 'make sure your service-to-database mappings are properly configured')
			_log.Log(gmLog.lWarn, 'trying to make do with default login parameters')
			return dblogin
		auth_data = cursor.fetchone()
		idx = cursorIndex(cursor)
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
		try: # backend options (not that I have any idea what we'd need them for, but hey :-)
			dblogin.SetOptions(string.strip(auth_data[idx['opt']]))
		except: pass
		try: # tty option (what's that, actually ?)
			dblogin.SetTTY(string.strip(auth_data[idx['tty']]))
		except:pass
		# and return what we thus got - which may very well be identical to the default login ...
		return dblogin			
	#-----------------------------
	# private methods
	#-----------------------------
	def __setup_default_ro_conns(self, login):
		"""Initialize connections to all servers."""

		if login is None and ConnectionPool.__connected is None:
			try:
				login = request_login_params()
			except:
				_log.LogException("Exception: Cannot connect to databases without login information !", sys.exc_info(), fatal=1)
				raise gmExceptions.ConnectionError("Can't connect to database without login information!")

		_log.Log(gmLog.lData, login.GetInfoStr())
		ConnectionPool.__login = login

		# connect to the configuration server
		cfg_db = self.__pgconnect(login, readonly=1)
		if cfg_db is None:
			raise gmExceptions.ConnectionError, _('Cannot connect to configuration database with:\n\n[%s]') % login.GetInfoStr()

		ConnectionPool.__connected = 1

		# this is the default gnumed server now
		ConnectionPool.__databases['config'] = cfg_db
		ConnectionPool.__databases['default'] = cfg_db
		
		# preload all services with database id 0 (default)
		cursor = cfg_db.cursor()
		cmd = "select name from distributed_db;"
		if not run_query(cursor, cmd):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load service names from configuration database")
		services = cursor.fetchall()
		for service in services:
			ConnectionPool.__service2db_map[service[0]] = 0

		# establish connections to all servers we need
		# according to configuration database
		cmd = "select * from config where profile='%s'" % login.GetProfile()
		if not run_query(cursor, cmd):
			cursor.close()
			raise gmExceptions.ConnectionError("cannot load user profile [%s] from database" % login.GetProfile())
		databases = cursor.fetchall()
		dbidx = cursorIndex(cursor)

		#for all configuration entries that match given user and profile
		for db in databases:
			###get the symbolic name of the distributed service
			cursor.execute("select name from distributed_db where id = %d" %  db[dbidx['ddb']])
			service = string.strip(cursor.fetchone()[0])
			# map service name to id of real database
			_log.Log(gmLog.lData, "mapping service [%s] to DB ID [%s]" % (service, db[dbidx['db']]))
			ConnectionPool.__service2db_map[service] = db[dbidx['db']]

			# init ref counter
			ConnectionPool.__connections_in_use[service] = 0
			dblogin = self.GetLoginInfoFor(service, login)
			# update 'Database Broker' dictionary
			conn = self.__pgconnect(dblogin, readonly=1)
			if conn is None:
				raise gmExceptions.ConnectionError, _('Cannot connect to database with:\n\n[%s]') % login.GetInfoStr()
			ConnectionPool.__databases[service] = conn
		cursor.close()
		return ConnectionPool.__connected
	#-----------------------------
	def __pgconnect(self, login, readonly=2):
		"""connect to a postgres backend as specified by login object; return a connection object"""
		dsn = ""
		hostport = ""

		if _isPGDB:
			dsn, hostport = login.GetPGDB_DSN(readonly)
		else:
			dsn = login.GetDBAPI_DSN(readonly)
			hostport = "0"

		try:
			if _isPGDB:
				conn = dbapi.connect(dsn, host=hostport)
			else:
				conn = dbapi.connect(dsn)
		except StandardError:
			_log.LogException("database connection failed: DSN = [%s], host:port = [%s]" % (dsn, hostport), sys.exc_info(), fatal = 1)
			return None

		# set the default characteristics of our sessions
		cmd = 'set session characteristics as transaction isolation level SERIALIZABLE;'
		curs = conn.cursor()
		if not run_query(curs, cmd):
			cur.close()
			conn.close()
			_log.Log(gmLog.lErr, 'cannot set connection characteristics to "serializable"')
			return None

		#  this needs >= 7.4
		if readonly:
			access_mode = 'READ ONLY'
		else:
			access_mode = 'READ WRITE'
		_log.Log(gmLog.lData, "setting session to [%s] for %s@%s:%s" % (access_mode, login.GetUser(readonly), login.GetHost(), login.GetDatabase()))
		cmd = 'set session characteristics as transaction %s;' % access_mode
		# activate when 7.4 is common
#		if not run_query(curs, cmd):
#			_log.Log(gmLog.lErr, 'cannot set connection characteristics to [%s]' % access_mode)
			# FIXME: once 7.4 is minimum, close connection and return None here

		conn.commit()
		curs.close()
		return conn
	#-----------------------------
	def __decrypt(self, crypt_pwd, crypt_algo, pwd):
		"""decrypt the encrypted password crypt_pwd using the stated algorithm
		and the given password pwd"""
		#TODO!!!
		pass
	
	#-----------------------------
	def __disconnect(self, force_it=0):
		"safe disconnect (respecting possibly active connections) unless the force flag is set"
		###are we connected at all?
		if ConnectionPool.__connected is None:
			###just in case
			ConnectionPool.__databases.clear()
			return
		#stop all background threads
		for backend in self.__listeners.keys():
			self.__listeners[backend].tell_thread_to_stop()
			del self.__listeners[backend]
		###disconnect from all databases
		for key in ConnectionPool.__databases.keys():
			### check whether this connection might still be in use ...
			if ConnectionPool.__connections_in_use[key] > 0 :
				###unless we are really mean :-(((
				if force_it == 0:
					#let the end user know that shit is happening
					raise gmExceptions.ConnectionError, "Attempting to close a database connection that is still in use"
			else:
				###close the connection
				ConnectionPool.__databases[key].close()

		#clear the dictionary (would close all connections anyway)
		ConnectionPool.__databases.clear()
		ConnectionPool.__connected = None
#---------------------------------------------------
# database helper functions
#---------------------------------------------------

def cursorIndex(cursor):
	"""returns a dictionary of row atribute names and their row indices"""
	i=0
	dict={}
    
	if cursor.description is None:
		return None
        
	for d in cursor.description:
		dict[d[0]] = i
		i+=1
	return dict

#---------------------------------------------------

def descriptionIndex(cursordescription):
	"""returns a dictionary of row atribute names and their row indices"""
	i=0
	dict={}
	for d in cursordescription:
		dict[d[0]] = i
		i+=1
	return dict

#---------------------------------------------------

def dictResult(cursor, fetched=None):
	"returns the all rows fetchable by the cursor as dictionary (attribute:value)"
	if fetched is None:
		fetched = cursor.fetchall()
	attr = fieldNames(cursor)
	dictres = []
	for f in fetched:
		dict = {}
		i=0
		for a in attr:
			dict[a]=f[i]
			i+=1
		dictres.append(dict)
	return dictres

#---------------------------------------------------

def fieldNames(cursor):
	"returns the attribute names of the fetched rows in natural sequence as a list"
	names=[]
	for d in cursor.description:
		names.append(d[0])
	return names

#---------------------------------------------------

def listDatabases(service='default'):
	"list all accessible databases on the database backend of the specified service"
	assert(__backend == 'Postgres')
	return quickROQuery("select * from pg_database")

#---------------------------------------------------

def listUserTables(service='default'):
	"list the tables except all system tables of the specified service"
	assert(__backend == 'Postgres')
	return quickROQuery("select * from pg_tables where tablename not like 'pg_%'", service)

#---------------------------------------------------

def listSystemTables(service='default'):
	"list the system tables of the specified service"
	assert(__backend == 'Postgres')
	return quickROQuery("select * from pg_tables where tablename like 'pg_%'", service)

#---------------------------------------------------

def listTables(service='default'):
	"list all tables available in the specified service"
	return quickROQuery("select * from pg_tables", service)

#---------------------------------------------------

def quickROQuery(query, service='default'):
	"""a quick read-only query that fetches all possible results at once
	returns the tuple containing the fetched rows and the cursor 'description' object"""

	dbp = ConnectionPool()
	con = dbp.GetConnection(service)
	cur=con.cursor()
	cur.execute(query)
	return cur.fetchall(), cur.description
#---------------------------------------------------
#---------------------------------------------------
def _import_listener_engine():
	try:
		import gmBackendListener
	except ImportError:
		_log.LogException('cannot import gmBackendListener')
		return None
	global listener_api
	listener_api = gmBackendListener
	return 1
#---------------------------------------------------
def run_query(aCursor = None, aQuery = None, *args):
	# sanity checks
	if aCursor is None:
		_log.Log(gmLog.lErr, 'need cursor to run query')
		return None
	if aQuery is None:
		_log.Log(gmLog.lErr, 'need query to run it')
		return None

	try:
		aCursor.execute(aQuery, *args)
	except:
		if gmCLI.has_arg("--debug"):
			log_much = 1
		else:
			log_much = 0
		_log.LogException("query >>>%s<<< (args: %s) failed" % (aQuery, args), sys.exc_info(), verbose = log_much)
		return None
	return 1
#---------------------------------------------------
def getBackendName():
	return __backend
#===================================================
def prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#---------------------------------------------------
def request_login_params_tui():
	"""text mode request of database login parameters
	"""
	import getpass
	login = gmLoginInfo.LoginInfo('', '')

	print "\nPlease enter the required login parameters:"
	try:
		database = prompted_input("database [gnumed]: ", 'gnumed')
		user = prompted_input("user name: ", '')
		password = getpass.getpass("password (not shown): ")
		host = prompted_input("host [localhost]: ", 'localhost')
		port = prompted_input("port [5432]: ", 5432)
	except KeyboardInterrupt:
		_log.Log(gmLog.lWarn, "user cancelled text mode login dialog")
		print "user cancelled text mode login dialog"
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

	login.SetInfo(user, password, dbname=database, host=host, port=port)
	return login
#---------------------------------------------------
def request_login_params_gui_wx():
	"""GUI (wx) input request for database login parameters.

	Returns gmLoginInfo.LoginInfo object
	"""
	import wxPython.wx
	# the next statement will raise an exception if wxPython is not loaded yet
	sys.modules['wxPython']
	# OK, wxPython was already loaded. But has the main Application instance
	# been initialized yet ? if not, the exception will kick us out
	if wxPython.wx.wxGetApp() is None:
		raise gmExceptions.NoGuiError(_("The wx GUI framework hasn't been initialized yet!"))

	# Let's launch the login dialog
	# if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmLoginDialog
	dlg = gmLoginDialog.LoginDialog(None, -1, png_bitmap = 'bitmaps/gnumedlogo.png')
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
			login = request_login_params_gui_wx()
			return login
		except:
			pass
	# well, either we are on the console or
	# wxPython does not work, use text mode
	login = request_login_params_tui()
	return login
#==================================================================
# Main
#==================================================================
def run_notifications_debugger():
	#-------------------------------
	def myCallback(**kwds):
		sys.stdout.flush()
		print "\n=== myCallback: got called ==="
		print kwds
	#-------------------------------

	dbpool = ConnectionPool()
	roconn = dbpool.GetConnection('default')
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
				cmd = 'NOTIFY "%s";' % sig_names[0]
				print "... running >>>%s<<<" % cmd
				if not run_query(rocurs, cmd):
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
#------------------------------------------------------------------
if __name__ == "__main__":
	_log.Log(gmLog.lData, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
	_ = lambda x:x

	print "Do you want to test the backend notification code ?"
	yes_no = raw_input('y/n: ')
	if yes_no == 'y':
		run_notifications_debugger()
		sys.exit()

	dbpool = ConnectionPool()
	### Let's see what services are distributed in this system:
	print "\n\nServices available on this system:"
	print '-----------------------------------------'
	for service in dbpool.GetAvailableServices():
		print service
		dummy = dbpool.GetConnection(service)
		print "Available tables within service: ", service
		tables, cd = listUserTables(service)
		idx = descriptionIndex(cd)
		for table in tables:
			print "%s (owned by user %s)" % (table[idx['tablename']], table[idx['tableowner']])
		print "\n.......................................\n"

	### We have probably not distributed the services in full:
	db = dbpool.GetConnection('config')
	print "\n\nPossible services on any gnumed system:"
	print '-----------------------------------------'
	cursor = db.cursor()
	cursor.execute("select name from distributed_db")
	for service in  cursor.fetchall():
		print service[0]

	print "\nTesting convenience funtions:\n============================\n"
	print "Databases:\n============\n"
	res, descr = listDatabases()
	for r in res: print r
	print "\nTables:\n========\n"
	res, descr = listTables()
	for r in res: print r
	print "\nResult as dictionary\n==================\n"
	cur = db.cursor()
	cursor.execute("select * from db")
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
	dbpool.Listen('config', 'test', TestCallback)
	time.sleep(20)
	dbpool.StopListener('config')
	print "Requesting write access connection:"
	con = dbpool.GetConnection('config', readonly=0)

#==================================================================
# $Log: gmPG.py,v $
# Revision 1.60  2003-06-26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.59  2003/06/25 22:24:55  ncq
# - improve logging in run_query() depending on --debug (yuck !)
#
# Revision 1.58  2003/06/23 21:21:55  ncq
# - missing "return None" in run_query added
#
# Revision 1.57  2003/06/23 14:25:40  ncq
# - let DB-API do the quoting
#
# Revision 1.56  2003/06/21 10:53:03  ncq
# - correctly handle failing connections to cfg db
#
# Revision 1.55  2003/06/14 22:41:51  ncq
# - remove dead code
#
# Revision 1.54  2003/06/10 08:48:12  ncq
# - on-demand import of gmBackendListener so we can use gmPG generically
#   without having to have pyPgSQL available (as long as we don't use
#   notifications)
#
# Revision 1.53  2003/06/03 13:59:20  ncq
# - rewrite the lifeness check to look much cleaner
#
# Revision 1.52  2003/06/03 13:46:52  ncq
# - some more fixes to Syans connection liveness check in GetConnection()
#
# Revision 1.51  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.50  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.49  2003/06/01 12:21:25  ncq
# - re-enable listening to async backend notifies
# - what do you mean "reactivate when needed" ?! this is used *already*
#
# Revision 1.48  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.47  2003/05/17 17:29:28  ncq
# - teach it new-style ro/rw connection handling, mainly __pgconnect()
#
# Revision 1.46  2003/05/17 09:49:10  ncq
# - set default transaction isolation level to serializable
# - prepare for 7.4 read-only/read-write support on connections
#
# Revision 1.45  2003/05/05 15:23:39  ncq
# - close cursor as early as possible in GetLoginInfoFor()
#
# Revision 1.44  2003/05/05 14:08:19  hinnef
# bug fixes in cursorIndex and getLoginInfo
#
# Revision 1.43  2003/05/03 14:15:31  ncq
# - sync and stop threads in __del__
#
# Revision 1.42  2003/05/01 15:01:10  ncq
# - port must be int in backend.listener()
# - remove printk()s
#
# Revision 1.41  2003/04/28 13:23:53  ncq
# - make backend listener shell work by committing after notifying
#
# Revision 1.40  2003/04/27 11:52:26  ncq
# - added notifications debugger shell in test environment
#
# Revision 1.39  2003/04/27 11:37:46  ncq
# - heaps of cleanup, __service_mapping -> __service2db_map, cdb -> cfg_db
# - merge _ListenTo and _StartListeningThread into Listen()
# - add Unlisten()
#
# Revision 1.38  2003/04/25 13:02:10  ncq
# - cleanup and adaptation to cleaned up backend listener code
#
# Revision 1.37  2003/04/08 08:58:00  ncq
# - added comment
#
# Revision 1.36  2003/04/07 00:40:45  ncq
# - now finally also support running on the console (not within a terminal window inside X)
#
# Revision 1.35  2003/03/27 21:11:26  ncq
# - audit for connection object leaks
#
# Revision 1.34  2003/02/24 23:17:32  ncq
# - moved some comments out of the way
# - convenience function run_query()
#
# Revision 1.33  2003/02/19 23:41:23  ncq
# - removed excessive printk's
#
# Revision 1.32  2003/02/07 14:23:48  ncq
# - == None -> is None
#
# Revision 1.31  2003/01/16 14:45:04  ncq
# - debianized
#
# Revision 1.30  2003/01/06 14:35:02  ncq
# - fail gracefully on not being able to connect RW
#
# Revision 1.29  2003/01/05 09:58:19  ncq
# - explicitely use service=default on empty Get/ReleaseConnection()
#
# Revision 1.28  2002/10/29 23:12:25  ncq
# - a bit of cleanup
#
# Revision 1.27  2002/10/26 16:17:13  ncq
# - more explicit error reporting
#
# Revision 1.26  2002/10/26 02:45:52  hherb
# error in name mangling for writeable connections fixed (persisting "_" prepended to user name when connection reused)
#
# Revision 1.25  2002/10/25 13:02:35  hherb
# FetchReturnsList now default on connection creation
#
# Revision 1.24  2002/10/20 16:10:46  ncq
# - a few bits here and there
# - cleaner logging
# - raise ImportError on failing to import a database adapter instead of dying immediately
#
# Revision 1.23  2002/09/30 16:20:30  ncq
# - wrap printk()s in <DEBUG>
#
# Revision 1.22  2002/09/30 15:48:16  ncq
# - fix dumb bug regarding assignment of local variable logininfo
#
# Revision 1.21  2002/09/30 08:26:57  ncq
# - a bit saner logging
#
# Revision 1.20  2002/09/29 14:39:44  ncq
# - cleanup, clarification
#
# Revision 1.19  2002/09/26 13:14:59  ncq
# - log version
#
# Revision 1.18  2002/09/19 18:07:48  hinnef
# fixed two bugs that prevented distributed services from working (HB)
#
# Revision 1.17  2002/09/15 13:20:17  hherb
# option to return results as list instead of result set objects added
#
# Revision 1.16  2002/09/10 07:44:29  ncq
# - added changelog keyword
#
# @change log:
#	25.10.2001 hherb first draft, untested
#	29.10.2001 hherb crude functionality achieved (works ! (sortof))
#	30.10.2001 hherb reference counting to prevent disconnection of active connections
#	==========================================================================
#	significant version change!
#	==========================================================================
#	08.02.2002 hherb made DB API 2.0 compatible.
#	01.09.2002 hherb pyPgSQL preferred adapter
#	01.09.2002 hherb writeable connections, start work on asynchronous part
