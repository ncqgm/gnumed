#!/usr/bin/python

"""This is just a convenient higher-level wrapper for gmPG
for lazy programmers wanting to access GNUmed BLOBs.

@copyright: GPL
"""

# TODO: go from service "default" to services "personalia" and "blobs"
#-----------------------------------------------------------
import gmPG, gmLog, gmLoginInfo

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.4 $"

__log__ = gmLog.gmDefLog
#-----------------------------------------------------------
class cDatabase:
	def __init__(self, aCfg = None):
		__log__.Log(gmLog.lData, "instantiating befund database connection object")
		if aCfg == None:
			__log__.Log(gmLog.lErr, "Parameter aCfg must point to a ConfigParser object.")
			return None
		self.__cfg = aCfg
	#------------------------------------------
	def connect(self, readonly_flag=1):
		#get the login parameters
		login = gmLoginInfo.LoginInfo('', '')
		user = self.__cfg.get("database", "user")
		passwd = self.__cfg.get("database", "password")
		database = self.__cfg.get("database", "database")
		host = self.__cfg.get("database", "host")
		port = self.__cfg.get("database", "port")
		login.SetInfo(user, passwd, dbname=database, host=host, port=port)

		#now try to connect to the backend
		self.__backend = gmPG.ConnectionPool(login)

		if self.__backend.Connected() is not None:
			__log__.Log(gmLog.lInfo, "backend connection successfully established")
		else:
			__log__.Log(gmLog.lErr, "cannot establish backend connection")
			return None

		# FIXME: should be "personalia" and "blobs"
		self.__conn = self.__backend.GetConnection('default', readonly_flag)

		return (1==1)
	#------------------------------------------
	def disconnect(self):
		self.__backend.ReleaseConnection('default')
		#self.__backend.ReleaseConnection('personalia')
		#self.__backend.ReleaseConnection('blobs')
		__log__.Log(gmLog.lInfo, "releasing befund database connection")
	#------------------------------------------
	def importDocument(self, aPatient, aDocument):
		pat_id = None
		pat_ids = []

		__log__.Log(gmLog.lInfo, "inserting document")

		# make sure we are synced before starting a transaction
		self.__conn.commit()

		# make sure patient is there
		if not aPatient.importIntoGNUmed(self.__conn):
			__log__.Log(gmLog.lErr, "Cannot insert or retrieve patient !")
			return (1==0)

		# import actual document data
		if not aDocument.importIntoGNUmed(self.__conn, aPatient):
			__log__.Log(gmLog.lErr, "Cannot insert document data !")
			return (1==0)

		return (1==1)
	#------------------------------------------
	def runArbitraryQuery(self, aQuery = None):
		"""Run any query against our database.

		Be careful about potential result size !
		"""
		# sanity check
		if aQuery == None:
			__log__.Log(gmLog.lErr, "Must have a query to run it !")
			return None
		else:
			__log__.Log(gmLog.lData, "About to run query >>>%s<<<" % aQuery)

		# start our transaction (done implicitely by defining a cursor)
		cursor = self.__conn.cursor()

		# then run our query
		try:
			cursor.execute(aQuery)
		except:
			return None

		result = cursor.fetchall()
		__log__.Log(gmLog.lData, "Query yielded: >>>%s<<<" % result)
		cursor.close()
		return result
	#------------------------------------------
	# FIXME: this is conceptually rather ugly
	def getConn(self):
		return self.__conn
