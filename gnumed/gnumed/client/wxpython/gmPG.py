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
#
# @TODO: Almost everything
############################################################################

import pg
import gmLoginInfo


class ConnectionPool:
	"maintains a static dictionary of available database connections"

	#a dictionary with lists of databases; dictionary key is the name of the database
	__databases = {}
	__connected = None


	def __init__(self, login=None, profile='default'):
		if login is not None:
			self.__disconnect()
		if ConnectionPool.__connected is None:
			ConnectionPool.__connected = self.__connect(login)


	def __connect(self, login):
		"initialize connection to all neccessary servers"

		if login=None:
			self.LogError(_("FATAL ERROR: can't connect to configuration database"))
			return 0

		#first, connect to the configuration server
		cdb = self.__pgconnect(login)
		if cbd is None:
			return
		else:
			ConnectionPool.__connected = 1

		#this is the default gnumed server now!
		ConnectionPool.__databases['gnumed'] = cdb

		#try to establish connections to all servers we need
		#according to configuration database
		databases = cdb.query("select * from config where username='%s' and profile='%s'"
		                      % (login.GetUser(), login.GetProfile()).dictresult()

		#for all configuration entries that mach given user and profile
		for db in databases:
			#get the symbolic name of the distributed service
			service = string.strip(cdb.query(
			                       "select name from distributed_db where id = %d"
			                       % db['ddb']).result()[0][0])
			#try to get login information for a particular service
			database = cdb.query("select name, port, host, opt, tty from db where id = %d"
			                     % db['db']).dictresult()[0]

			dblogin = login
			if database.has_key('user') and database['user'] != '':
				dblogin.SetUser(database[user])
			else:
				dblogin.SetUser(login.GetUser())
			if database.has_key('crypt_pwd') and database['crypt_pwd'] != '':
				dblogin.SetUser(self.__decrypt(database['crypt_pwd'], database['crypt_algo'], login.GetPassord())
			else:
				dblogin.SetUser(login.GetPassword())

			#TODO: ...

			ConnectionPool.__databases[service] = self.__pgconnect(dblogin)




	def __pgconnect(self, login):
		"connect to a postgres backend; return a connection object"

		try:
			db = pg.connect(dbname=login.GetDatabase(),
					host = login.GetHost(),
					port = login.GetPort(),
					opt = login.GetOptions(),
					tty = login.GetTTY(),
					user = login.GetUser()
					passwd = login.GetPassword())
			return db
		except TypeError:
			msg = _("Query failed when trying to connect to backend:\n \
				Bad argument type, or too many arguments.")
			self.LogError(msg)
			return None
		except SyntaxError:
			msg =_("Query failed when trying to connect to backend:\n \
			        Wrong syntax.")
			self.LogError(msg)
			return None
		except pg.error:
			msg = _("Query failed when trying to connect to backend:\n \
			        Some error occurred during pg connection definition")
			self.LogError(msg)
			return None


	def __decrypt(self, crypt_pwd, crypt_algo, pwd):
		"""decrypt the encrypted password crypt_pwd using the stated algorithm
		and the given password pwd"""
		#TODO!!!
		result = crypt_pwd
		return result


	def disconnect(self):
		if gmdbConnectionPool.__connected is None:
			return
		#disconnect from all databases
		for key in ConnectionPool.__databases.keys():
			ConnectionPool.__databases[key].disconnect()
		#clear the dictionary
		ConnectionPool.__databases.clear()
		gmdbConnectionPool.__connected = 0


	def getConnection(self, service):
		return gmdbConnectionPool.__databases[service]

	def LogError(msg):
		"This function must be overridden by GUI applications"
		print msg




