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
#
# @TODO: Almost everything
############################################################################

#python standard modules
import string, gettext, copy
#3rd party dependencies
import pgdb
#gnumed specific modules
import gmLoginInfo, gmLog, gmExceptions

#take care of translating strings
_ = gettext.gettext

#create an alias for our DB API adapter module to make code independend of the adapter used
dbapi = pgdb
__backend = 'Postgres'
#check whether this adapter module suits our needs
assert(float(dbapi.apilevel) >= 2.0)
assert(dbapi.threadsafety > 0)
assert(dbapi.paramstyle == 'pyformat') 



class ConnectionPool:
	"maintains a static dictionary of available database connections"

	#a dictionary with lists of databases; dictionary key is the name of the database
	__databases = {}
	__connections_in_use = {}
	__connected = None


	def __init__(self, login=None):
		"parameter login is of type gmLoginInfo.LoginInfo"
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__connected is None:
			ConnectionPool.__connected = self.__connect(login)


	def __connect(self, login):
		"initialize connection to all neccessary servers"

		if login==None and ConnectionPool.__connected is None:
		    raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

		#first, connect to the configuration server
		try:
		    cdb = self.__pgconnect(login)
		except:
		    raise gmExceptions.ConnectionError(_("Could not connect to configuration database  backend!"))
		    
		ConnectionPool.__connected = 1

		#this is the default gnumed server now!
		ConnectionPool.__databases['config'] = cdb
		ConnectionPool.__databases['default'] = cdb

		#try to establish connections to all servers we need
		#according to configuration database
		cursor = cdb.cursor()
		cursor.execute("select * from config where profile='%s'" %
		            login.GetProfile())
		databases = cursor.fetchall()
		dbidx = cursorIndex(cursor)

		#for all configuration entries that match given user and profile
		for db in databases:

			###get the symbolic name of the distributed service
			cursor.execute("select name from distributed_db where id = %d" %  db[dbidx['ddb']])
			service = string.strip(cursor.fetchone()[0])
			print "processing service " , service

			###initialize our reference counter
			ConnectionPool.__connections_in_use[service]=0

			###try to get login information for a particular service
			querystr = "select name, host, port, opt, tty from db where id = %d" % db[dbidx['db']]
			cursor.execute(querystr)
			database = cursor.fetchone()
			idx = cursorIndex(cursor)

			###create a copy of the default login information, keeping user name and password
			dblogin = copy.deepcopy(login)
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
			#update 'Database Broker' dictionary
			ConnectionPool.__databases[service] = self.__pgconnect(dblogin)
		try:
		    cursor.close()
		except:
		    pass

		return ConnectionPool.__connected



	### private method
	def __pgconnect(self, login):
		"connect to a postgres backend as specified by login object; return a connection object"
		
		dsn, hostport = login.GetPGDB_DSN()
		try:
		    db = pgdb.connect(dsn, host=hostport)
		    return db
		except: 
		    self.LogError(_("Connection to database failed. \nDSN was [%s], host:port was [%s]") % (dsn, hostport))
		    raise gmExceptions.ConnectionError, _("Connection to database failed. \nDSN was [%s], host:port was [%s]") % (dsn, hostport)




	def __decrypt(self, crypt_pwd, crypt_algo, pwd):
		"""decrypt the encrypted password crypt_pwd using the stated algorithm
		and the given password pwd"""
		#TODO!!!
		pass


	def __disconnect(self, force_it=0):
		"safe disconnect (respecting possibly active connections) unless the force flag is set"
		###are we conected at all?
		if ConnectionPool.__connected is None:
			###just in case
			ConnectionPool.__databases.clear()
			return
		###disconnect from all databases
		for key in ConnectionPool.__databases.keys():
			### check whether this connection might still be in use ...
			if ConnectionPool.__connections_in_use[service] > 0 :
				###unless we are really mean :-(((
				if force_it == 0:
					#let the end user know that shit is happening
					raise gmExceptions.ConnectionError, \
					    _("Attempting to close a database connectiuon that is still in use")
			else:
				###close the connection
				ConnectionPool.__databases[key].close()

		#clear the dictionary (would close all connections anyway)
		ConnectionPool.__databases.clear()
		ConnectionPool.__connected = None



	def GetConnection(self, service):
		"if a distributed service exists, return it - otherwise return the default server"
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



	def GetAvailableServices(self):
		"""list all distributed services available on this system
		(according to configuration database)"""
		return ConnectionPool.__databases.keys()

	def Connected(self):
		return ConnectionPool.__connected

	def LogError(self, msg):
		"This function must be overridden by GUI applications"
		print msg


### database helper functions

def cursorIndex(cursor):
    "returns a dictionary of row atribute names and their row indices"
    i=0
    dict={}
    for d in cursor.description:
	dict[d[0]] = i
	i+=1
    return dict
    
    
def descriptionIndex(cursordescription):
    "returns a dictionary of row atribute names and their row indices"
    i=0
    dict={}
    for d in cursordescription:
	dict[d[0]] = i
	i+=1
    return dict    



def dictResult(cursor, fetched=None):
    if fetched is None:
	fetched = cursor.fetchall()
    attr = fieldNames(cursor)
    dictres = []
    for f in fetched:
	dict = {}
	i=0
	for a in attr:
    	    dict[a]=f[i]
	dictres.append(dict)
	i+=1
    return dictres
	
	
	
    
def fieldNames(cursor):
    "returns the attribute names of the fetched rows in natural sequence as a list"
    names=[]    
    for d in cursor.description:
	names.append(d[0])
    return names
	
    
def listDatabases(service='default'):
    assert(__backend == 'Postgres')
    return quickROQuery("select * from pg_database")
    
def listUserTables(service='default'):
    assert(__backend == 'Postgres')
    return quickROQuery("select * from pg_tables where tablename not like 'pg_%'", service)
    
    
def listSystemTables(service='default'):
    assert(__backend == 'Postgres')
    return quickROQuery("select * from pg_tables where tablename like 'pg_%'", service)
    
    
def listTables(service='default'):
    return quickROQuery("select * from pg_tables", service)
    

def quickROQuery(query, service='default'):
    "a quick read-only query that fetches all possible results at once"
    dbp = ConnectionPool()
    con = dbp.GetConnection(service)
    cur=con.cursor()
    cur.execute(query)
    return cur.fetchall(), cur.description 
    
    
def getBackendName():
    return __backend
    



### test function for this module: simple start as "main" module
if __name__ == "__main__":
	try:
		db = raw_input("which database hosts the gnumed configuration? [gnumed]: ")
	except:
		db='gnumed'

	try:
		usr = raw_input("enter user name for database [admin]: ")
	except:
		usr='admin'

	try:
		pwd = raw_input("enter your database user password []: ")
	except:
		pwd=''

	### 1.) create a login information object
	login = gmLoginInfo.LoginInfo(user=usr, passwd=pwd, database=db)
	dsn, hp = login.GetPGDB_DSN()
	print dsn, hp

	### 2.) with this basic login information, log into the service pool
	dbpool = ConnectionPool(login)

	### 3.) Let's see what services are distributed in this system:
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

	### 4.) We have probably not distributed the services in full:
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
