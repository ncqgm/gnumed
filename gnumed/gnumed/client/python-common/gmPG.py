#!/usr/bin/python
#############################################################################
#
# gmConnectionPool - Broker for Postgres distributed backend connections
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: pg, gmLoginInfo
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
#
# @TODO: testing
############################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.

"""gmConnectionPool - Broker for Postgres distributed backend connections
"""

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmPG.py,v $
__version__ = "$Revision: 1.21 $"
__author__  = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"

#python standard modules
import string, copy, os, sys, select, threading, time
#gnumed specific modules
import gmI18N, gmLog, gmLoginInfo, gmExceptions, gmBackendListener
_log = gmLog.gmDefLog

#3rd party dependencies
# first, do we have the preferred postgres-python library available ?
try:
	import pyPgSQL.PgSQL # try preferred backend library
	dbapi = pyPgSQL.PgSQL
	_isPGDB = 0
	print 'USING PYPGSQL!!!'
except ImportError:
	try:
	# well, well, no such luck - fall back to stock pgdb library
		import psycopg # try Zope library
		dbapi = psycopg
		_isPGDB = 0
		print 'USING PSYCOPG'
	except ImportError:
		try:
			import pgdb # try standard Postgres binding
			dbapi = pgdb
			_isPGDB = 1
			print 'USING PGDB'
		except ImportError:
			print "Apparently there is no database adapter available! Program halted"
			sys.exit(-1)

# FIXME: DBMS should eventually be configurable
__backend = 'Postgres'

_log.Log(gmLog.lInfo, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))

# check whether this adapter module suits our needs
assert(float(dbapi.apilevel) >= 2.0)
assert(dbapi.threadsafety > 0)
assert(dbapi.paramstyle == 'pyformat')
#======================================================================
class ConnectionPool:
	"maintains a static dictionary of available database connections"

	#a dictionary with lists of databases; dictionary key is the name of the service
	__databases = {}
	
	#a dictionary mapping the physical databases to the services; key is service name
	__service_mapping = {}
	
	#number of connections in use for each service (for reference counting purposes)
	__connections_in_use = {}
	
	#variable used to check whether a first connection has been initialized yet or not
	__connected = None
	
	#a dictionary mapping all backend listening threads to database id
	__threads = {}
	
	#gmLoginInfo.LoginInfo instance
	__login = None
	#-----------------------------
	def __init__(self, login=None):
		"""parameter login is of type gmLoginInfo.LoginInfo"""
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__connected is None:
			ConnectionPool.__connected = self.__connect(login)
	#-----------------------------
	def GetConnection(self, service, readonly=1):
		"""if a distributed service exists, return it - otherwise return the default server"""

		if not readonly:
			user = "_%s" % logininfo.GetUser()
			#<DEBUG>
			_log.Log(gmLog.lData, "requesting RW connection to [%s] for %s" % (service, user))
			#</DEBUG>
			logininfo = self.GetLoginInfoFor(service)
			logininfo.SetUser(user)
			return self.__pgconnect(logininfo)

		#<DEBUG>
		_log.Log(gmLog.lData, "requesting RO connection to [%s]" % service)
		#</DEBUG>

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
	def Listen(self, service, signal, callback):
		"""Listen to 'signal' from backend in an asynchronous thread.
		If 'signal' is received from database 'service', activate
		the 'callback' function"""
		
		### check what physical database the service belongs to
		try:
			id = ConnectionPool.__service_mapping[service]
		except KeyError:
			id = 0
		### since we need only one listening thread per database
		if id not in ConnectionPool.__threads.keys():
			ConnectionPool.__threads[id] = self._StartListeningThread(service);
		self._ListenTo(service, signal, callback)
	#-----------------------------
	def _ListenTo(self, service, signal, callback):
		"Tell the backend to notify us asynchronously on 'signal'"
		try:
			id = ConnectionPool.__service_mapping[service]
		except KeyError:
			id = 0
		backendlistener = ConnectionPool.__threads[id]
		backendlistener.RegisterCallback(callback, signal)
	#-----------------------------
	def _StartListeningThread(self, service):
		try:
			backend = self.__service_mapping[service]
		except KeyError:
			backend=0
		l = self.GetLoginInfoFor(service)
		if backend not in self.__threads.keys():
			backend = gmBackendListener.BackendListener(service, l.GetDatabase(), l.GetUser(), l.GetPassword(), l.GetHost(), l.GetPort())
			return backend
	#-----------------------------
	def StopListeningThread(self, service):
		try:
			backend = self.__service_mapping[service]	
		except KeyError:
			backend = 0
		try:
			self.__threads[backend].Stop()
		except:
			pass
	#-----------------------------
	def GetAvailableServices(self):
		"""list all distributed services available on this system
		(according to configuration database)"""
		return ConnectionPool.__databases.keys()
	#-----------------------------
	def Connected(self):
		return ConnectionPool.__connected	
	#-----------------------------	
	def LogError(self, msg):
		"This function must be overridden by GUI applications"
		print msg
	#-----------------------------		
	def SetFetchReturnsList(self, on=1):
		"""when performance is crucial, let the db adapter
		return a list of lists instead a list of database objects.
		CAREFUL: this affects the whole connection!!!"""
		if dbapi is pyPgSQL.PgSQL:
			dbapi.fetchReturnsList = on
	#-----------------------------		
	def GetLoginInfoFor(self, service, login = None):
		"""return login information for a particular service"""

		if login is None:
			dblogin = ConnectionPool.__login
		else:
			dblogin = copy.deepcopy(login)

		# if requested service is not mapped, return default login information
		if not ConnectionPool.__service_mapping.has_key(service):
			return dblogin

		srvc_id = ConnectionPool.__service_mapping[service]
		if srvc_id == 0:
			return dblogin

		# get connection to database "config" and create cursor (HB)
		cdb = ConnectionPool.__databases['config']
		cursor = cdb.cursor()

		# actually fetch login parameters for the database
		querystr = "select name, host, port, opt, tty from db where id = %d" % srvc_id
		cursor.execute(querystr)
		database = cursor.fetchone()
		idx = cursorIndex(cursor)

		###get the name of the distributed datbase service
		try:
			dblogin.SetDatabase(string.strip(database[idx['name']]))
		except: pass
		###hostname of the distributed service
		try:
			dblogin.SetHost(string.strip(database[idx['host']]))
		except: pass
		###port of the distributed service
		try:
			dblogin.SetPort(database[idx['port']])
		except: pass
		###backend options of the distributed service
		try:
			dblogin.SetOptions(string.strip(database[idx['opt']]))
		except: pass
		###TTY option of the distributed service
		try:
			dblogin.SetTTY(string.strip(database[idx['tty']]))
		except:pass
		return dblogin			
	#-----------------------------
	# private methods
	#-----------------------------
	def __connect(self, login):
		"initialize connection to all neccessary servers"

		if login==None and ConnectionPool.__connected is None:
			try:
				login = inputLoginParams()
				print login.GetDBAPI_DSN()
			except:
				exc = sys.exc_info()
				_log.LogException("Exception: Cannot connect to databases without login information !", exc, fatal=1)
				raise gmExceptions.ConnectionError("Can't connect to database without login information!")

		_log.Log(gmLog.lData,login.GetInfoStr())
		ConnectionPool.__login = login

		#first, connect to the configuration server
		try:
			cdb = self.__pgconnect(login)
		except:
			exc = sys.exc_info()
			_log.LogException("Exception: Cannot connect to configuration database !", exc, fatal=1)
			raise gmExceptions.ConnectionError("Could not connect to configuration database  backend!")

		ConnectionPool.__connected = 1

		#this is the default gnumed server now!
		ConnectionPool.__databases['config'] = cdb
		ConnectionPool.__databases['default'] = cdb
		
		#preload all services with database id 0 (default)
		cursor = cdb.cursor()
		cursor.execute("select name from distributed_db")
		services = cursor.fetchall()
		for service in services:
			ConnectionPool.__service_mapping[service[0]] = 0

		#try to establish connections to all servers we need
		#according to configuration database
		cursor = cdb.cursor()
		try:
			cursor.execute("select * from config where profile='%s'" % login.GetProfile())
		except dbapi.OperationalError:
			# this is the first query, give nicer error
			raise gmExceptions.ConnectionError("Not GNUMed database")
		databases = cursor.fetchall()
		dbidx = cursorIndex(cursor)

		#for all configuration entries that match given user and profile
		for db in databases:

			###get the symbolic name of the distributed service
			cursor.execute("select name from distributed_db where id = %d" %  db[dbidx['ddb']])
			service = string.strip(cursor.fetchone()[0])
			#map the id of the real database to the service
			print "mapping %s to %s" % (service, str(db[dbidx['db']]))
			ConnectionPool.__service_mapping[service] = db[dbidx['db']]

			###initialize our reference counter
			ConnectionPool.__connections_in_use[service] = 0
			dblogin = self.GetLoginInfoFor(service,login)
			#update 'Database Broker' dictionary
			ConnectionPool.__databases[service] = self.__pgconnect(dblogin)
		try:
			cursor.close()
		except:
			pass
		return ConnectionPool.__connected
	
	#-----------------------------	
	def __pgconnect(self, login):
		"connect to a postgres backend as specified by login object; return a connection object"

		dsn = ""
		hostport = ""

		if _isPGDB:
			dsn, hostport = login.GetPGDB_DSN()
		else:
			dsn = login.GetDBAPI_DSN()
			hostport = "0"

		try:
			if _isPGDB:
				#print "trying PGDB"
				db = dbapi.connect(dsn, host=hostport)
			else:
				#print "trying Non-PGDB"
				db = dbapi.connect(dsn)
			return db
		except:
			exc = sys.exc_info()
			_log.LogException("Exception: Connection to database failed. DSN was [%s]" % dsn, exc)
			raise gmExceptions.ConnectionError, _("Connection to database failed. \nDSN was [%s], host:port was [%s]") % (dsn, hostport)
	
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
		for backend in self.__threads.keys():
			self.__threads[backend].Stop()
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

def getBackendName():
	return __backend

#---------------------------------------------------

def prompted_input(prompt, default=None):
	try:
		res = raw_input(prompt)
	except:
		return default
	if res == '':
		return default
	return res

#---------------------------------------------------

def inputTMLoginParams():
	"""text mode input request of database login parameters"""
	login = gmLoginInfo.LoginInfo('', '')
	try:
		print "\nPlease enter the required login parameters:"
		database = prompted_input("database [gnumed] : ", 'gnumed')
		user = prompted_input("user name : ", '')
		password = prompted_input("password : ",'')
		host = prompted_input("host [localhost] : ", 'localhost')
		port = prompted_input("port [5432] : ", 5432)
		login.SetInfo(user, password, dbname=database, host=host, port=port)
	except:
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))
	return login

#---------------------------------------------------

def inputWXLoginParams():
	"""GUI (wx) mode input request of database login parameters.
	Returns gmLoginInfo.LoginInfo object"""

	import sys, wxPython.wx
	#the next statement will raise an exception if wxPython is not loaded yet
	sys.modules['wxPython']
	#OK, wxPython was already loaded. But has the main Application instance been initialized already?
	#if not, the exception will kick us out
	if wxPython.wx.wxGetApp() is None:
		raise gmExceptions.NoGuiError(_("The wx GUI framework hasn't been initialized yet!"))

	#Let's launch the login dialog
	#if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmLoginDialog
	dlg = gmLoginDialog.LoginDialog(None, -1, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo ()
	#if user cancelled or something else went wrong, raise an exception
	if login is None:
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))
	#memory cleanup, shouldn't really be neccessary
	dlg.Destroy()

	del gmLoginDialog
	return login

#---------------------------------------------------

def inputLoginParams():
	"input request for database backend login parameters. Try GUI dialog if available"
	try:
		login = inputWXLoginParams()
	except:
		login = inputTMLoginParams()
	return login

#==================================================================
# Main
#==================================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	_log.Log(gmLog.lData, 'DBMS "%s" via DB-API module "%s": API level %s, thread safety %s, parameter style "%s"' % (__backend, dbapi, dbapi.apilevel, dbapi.threadsafety, dbapi.paramstyle))
	_ = lambda x:x

	dbpool = ConnectionPool()
	### Let's see what services are distributed in this system:
	print "\n\nServices available on this system:"
	print '-----------------------------------------'
	for service in dbpool.GetAvailableServices():
		print service
		dummy=dbpool.GetConnection(service)
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

	def TestCallback():
		print "[Backend notification received!]"
		
	print "\n-------------------------------------"
	print "Testing asynchronous notification for approx. 20 seconds"
	print "start psql in another window connect to gnumed"
	print "and type 'notify test'; if everything works,"
	print "a message [Backend notification received!] should appear\n"
	dbpool.Listen('config', 'test', TestCallback)
	time.sleep(20)	
	dbpool.StopListeningThread('config')	
	print "Requesting write access connection:"
	con = dbpool.GetConnection('config', readonly=0)

#==================================================================
# $Log: gmPG.py,v $
# Revision 1.21  2002-09-30 08:26:57  ncq
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
