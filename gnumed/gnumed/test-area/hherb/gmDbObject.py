#############################################################################
#
# gmDbObject : base class for generic database objects
#              this base class should provide a higher level database API      
#              to the client programmers, since it takes care of
#              some error handling and handles the differences
#              between read-only and read/write connections
#
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG
# @TODO: Almost everything
############################################################################

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/hherb/gmDbObject.py,v $
__version__ = "$Revision: 1.1 $"
__author__  = "H. Herb <hherb@gnumed.net>"

import sys
import gmLog
_log = gmLog.gmDefLog
#============================================================
class DBObject:
	"""High level DB-API based base class for all gnumed database objects"""

	def __init__(self, dbbroker, service='default', select_query=None):
		"""dbbroker: database broker as in gmPG.py
		service: name of the gnumed database service the data is based on
		select_query: query that selects the rows associated with class instance"""
		self._db = dbbroker
		self.__service = service
		self._qSelect = select_query
		self._qInsert = None
		self._qUpdate = None
		self._qDelete = None
	#----------------------------
	def SetSelectQuery(self, query):
		"""Definition of the query string used to select the row(s)
		associated with this database object. Parameters (for example for
		a 'where' clause are allowed in
		 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qSelect = query
	#----------------------------
	def SetInsertQuery(self, query):
		"""Definition of the query that would insert a row into this
		database object. All parameters must
		be set in 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qInsert = query
	#----------------------------
	def SetUpdateQuery(self, query):
		"""Definition of the query neccessary to update the associated row.
		The string must have a '%(primarykey)s' parameter which is representing the 
		primary key attribute of the row to update. All other parameters must
		be set in 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qUpdate = query
	#----------------------------
	def SetDeleteQuery(self, query):
		"""Definition of the query neccessary to delete the associated row.
		The string must have a '%(primarykey)s' parameter which is representing the 
		primary key attribute of the row to delete"""
		self._qDelete = query
	#----------------------------
	def __log_error(self, msg, aMap = None):
		"""Please replace with gnumed logging functins s.a.p."""
		_log.Log(gmLog.lErr, msg)
		if aMap != None:
			_log.Log(gmLog.lData, "--------------------------------")
			for key in aMap.keys():
				_log.Log(gmLog.lData, "%s = %s" % (str(key), str(aMap[key])))
			_log.Log(gmLog.lData, "--------------------------------")
	#----------------------------
	def Select(self, map=None, maxfetch=0, listonly=0):
		"""Executes the select query and returns a list of
		PgResultSets (see pyPgSQL documentation)
		dictionary 'map' can be used for query parameters, for
		example for a 'WHERE' clause.
		'maxfetch' limits the number of rows returned
		'listonly' can speed things up if a large number
		of rows is expected as result by returning a simple list
		of lists instead of a list of PgResultSets"""
		if self._qSelect is None:
			self.__log_error("Error: select query not set yet!")
			return None
		result = []
		try:
			self._db.SetFetchReturnsList(listonly)
			try:
				con = self._db.GetConnection(self.__service)
			except:
				exc = sys.exc_info()
				_log.LogException("Failed to connect to backend.", exc, verbose=0)
				return None
			cursor = con.cursor()
			try:
				if map is not None:
					cursor.execute(self._qSelect, map)
				else:
					cursor.execute(self._qSelect)
			except:
				exc = sys.exc_info()
				_log.LogException("Query failed: >>>%s<<<" % map, exc, verbose=0)
				return None
			if maxfetch>0:
				result =  cursor.fetchmany(maxfetch)
			else:
				result = cursor.fetchall()
				#<DEBUG>
				_log.Log(gmLog.lData, "result: %s" % result)
				#print result
				#</DEBUG>
		finally:
			self._db.SetFetchReturnsList(0)
		if result is None:
			result = []
		return result
	#----------------------------
	def Insert(self, map):
		"""insert a row with attributes as listed in the dictionary 'map'.
		Returns the OID if succesful, otherwise returns 'None'"""
		oid = None
		if self._qInsert is None:
			self.__log_error("Error: insert query not set yet!")
			return None
		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			exc = sys.exc_info()
			_log.LogException("Failed to connect to backend.", exc, verbose=0)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qInsert, map)
		except:
			exc = sys.exc_info()
			_log.LogException("Query failed: >>>%s<<<" % map, exc, verbose=0)
			return None
		oid = cursor.oidValue
		con.commit()
		return oid
	#----------------------------
	def Update(self, map = None):
		"""update a row with attributes as listed in the dictionary "map".
		'map' dictionary  MUST contain the key 'primarykey' with the
		value set to the primay key of the row to be updated
		Returns 'None' if failed, the primary key if success """
		if self._qUpdate is None:
			self.__log_error("update query not set yet!")
			return None
		if not map.has_key('primarykey'):
			self.__log_error("no primary key in value map [%s]" % map)
			return None

		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			exc = sys.exc_info()
			_log.LogException("Failed to connect to backend.", exc, verbose=0)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qUpdate,map)
		except:
			exc = sys.exc_info()
			_log.LogException("Query failed: >>>%s<<<" % map, exc, verbose=0)
			return None
		con.commit()
		return primarykey
	#----------------------------
	def Delete(self, map):
		"""deletes a row as determined by the delete query string.
		'map' dictionary  MUST contain the key 'primarykey' with the
		value set to the primay key of the row to be deleted
		Returns 'None' if failed, the primary key if success """
		if self._qDelete is None:
			self.__log_error("delete query not set yet!")
			return None
		if not map.has_key('primarykey'):
			self.__log_error("no primary key in value map [%s]" % map)
			return None
		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			exc = sys.exc_info()
			_log.LogException("Failed to connect to backend.", exc, verbose=0)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qDelete, map)
		except:
			exc = sys.exc_info()
			_log.LogException("Failed to connect to backend.", exc, verbose=0)
			return None
		con.commit()
		return primarykey
#============================================================
# main
#============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmPG
	db = gmPG.ConnectionPool()
	dbo = DBObject(db, select_query = "select * from pg_tables where tablename not like 'pg_%'")
	rows = dbo.Select()
	for row in rows:
		print ""
		for key in row.keys():
			print "%s=%s," % (key, str(row[key])),

#============================================================
# $Log: gmDbObject.py,v $
# Revision 1.1  2005-01-19 15:05:54  ncq
# - moved here from main trunk
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.9  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.8  2003/08/24 13:42:13  hinnef
# changed verbose to 0 in exception logging to decrease log file size
#
# Revision 1.7  2003/06/26 21:33:29  ncq
# - fatal->verbose
#
# Revision 1.6  2003/01/16 14:45:03  ncq
# - debianized
#
# Revision 1.5  2002/09/26 13:18:24  ncq
# - log version
#
# Revision 1.4  2002/09/16 23:26:30  ncq
# - move setallloglevels to a saner place
#
# Revision 1.3  2002/09/16 10:44:08  ncq
# - add logging as requested
#
