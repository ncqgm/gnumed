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
#
# @TODO: Almost everything
############################################################################

import string, gettext, copy, pg, gmLoginInfo

_ = gettext.gettext

LIFE_CONNECTION_DELETE_ATTEMPT = _("attempt to teminate a database connection possibly still in use")

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
			self.LogError(_("FATAL ERROR: can't connect to configuration database"))
			return None

		#first, connect to the configuration server
		cdb = self.__pgconnect(login)
		if cdb is None:
			return None
		else:
			ConnectionPool.__connected = 1

		#this is the default gnumed server now!
		ConnectionPool.__databases['config'] = cdb

		#try to establish connections to all servers we need
		#according to configuration database
		databases = cdb.query("select * from config where profile='%s'"
		                      % login.GetProfile()).dictresult()

		#for all configuration entries that match given user and profile
		for db in databases:
			###get the symbolic name of the distributed service
			service = string.strip(cdb.query(
			                       "select name from distributed_db where id = %d"
			                       % db['ddb']).getresult()[0][0])
			###initialize our reference counter
			ConnectionPool.__connections_in_use[service]=0
			###try to get login information for a particular service
			database = cdb.query("select name, host, port, opt, tty from db where id = %d"
			                     % db['db']).dictresult()[0]
			###create a copy of the default login information, keeping user name and password
			dblogin = copy.deepcopy(login)
			###get the name of the distributed datbase service
			try:
				dblogin.SetDatabase(string.strip(database['name']))
			except: pass
			###hostname of the distributed service
			try:
				dblogin.SetHost(string.strip(database['host']))
			except: pass
			###port of the distributed service
			try:
				dblogin.SetPort(database['port'])
			except: pass
			###backend options of the distributed service
			try:
				dblogin.SetOptions(string.strip(database['opt']))
			except: pass
			###TTY option of the distributed service
			try:
				dblogin.SetTTY(string.strip(database['tty']))
			except:pass
			#update 'Database Broker' dictionary
			ConnectionPool.__databases[service] = self.__pgconnect(dblogin)

			return ConnectionPool.__connected



	### private method
	def __pgconnect(self, login):
		"connect to a postgres backend as specified by login object; return a connection object"
		try:
			#print "Trying to connect:\nuser = [%s]\nPassword=[%s]\nHost=[%s]\nPort=[%d]\nOpt=[%s]\ntty=[%s]" \
			#      % (login.GetUser(), login.GetPassword(), login.GetHost(), int(login.GetPort()), login.GetOptions(), login.GetTTY())
			db = pg.connect(dbname=login.GetDatabase(),
					host = login.GetHost(),
					port = int(login.GetPort()),
					opt = login.GetOptions(),
					tty = login.GetTTY(),
					user = login.GetUser(),
					passwd = login.GetPassword())
			return db
		except TypeError:
			msg = _("Query failed when trying to connect to backend [%s]:\n \
				Bad argument type, or too many arguments.") % login.GetDatabase()
			self.LogError(msg)
			return None
		except SyntaxError:
			msg =_("Query failed when trying to connect to backend [%s]:\n \
			        Wrong syntax.") % login.GetDatabase()
			self.LogError(msg)
			return None
		except pg.error:
			msg = _("Query failed when trying to connect to backend [%s]:\n \
			        Some error occurred during pg connection definition") % login.GetDatabase()
			self.LogError(msg)
			return None


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
					#let the end user know thatshit is happening
					raise LIFE_CONNECTION_DELETE_ATTEMPT
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

	### 2.) with this basic login information, log into the service pool
	dbpool = ConnectionPool(login)

	### 3.) Let's see what services are distributed in this system:
	print "\n\nServices available on this system:"
	print '-----------------------------------------'
	for service in dbpool.GetAvailableServices():
		print service
		dummy=dbpool.GetConnection(service)
		print "Available tables within service: ", service
		for table in dummy.query("select tablename, tableowner from pg_tables where tablename not like 'pg_%'").dictresult():
			print "%s (owned by user %s)" % (table['tablename'], table['tableowner'])
		print "\n.......................................\n"

	### 4.) We have probably not distributed the services in full:
	db = dbpool.GetConnection('config')
	print "\n\nPossible services on any gnumed system:"
	print '-----------------------------------------'
	for service in  db.query("select name from distributed_db").getresult():
		print service[0]
