class DBObject:
	"""Base class for all gnumed database objects"""
	
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
		
		
	def SetSelectQuery(self, query):
		"""Definition of the query string used to select the row(s)
		associated with this database object. Parameters (for example for
		a 'where' clause are allowed in
		 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qSelect = query
	
			
	def SetInsertQuery(self, query):
		"""Definition of the query that would insert a row into this
		database object. All parameters must
		be set in 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qInsert = query
	
			
	def SetUpdateQuery(self, query):
		"""Definition of the query neccessary to update the associated row.
		The string must have a '%(primarykey)s' parameter which is representing the 
		primary key attribute of the row to update. All other parameters must
		be set in 'dictionary parameter style', that is as '%(dictionary key)s'
		All parameters have to be passed as strings, but no quoting!!!"""
		self._qUpdate = query
	
			
	def SetDeleteQuery(self, query):
		"""Definition of the query neccessary to delete the associated row.
		The string must have a '%(primarykey)s' parameter which is representing the 
		primary key attribute of the row to delete"""
		self._qDelete = query
		
		
	def LogError(self, msg, map):
		"""Please replace with gnumed logging functins s.a.p."""
		print msg
		for key in map.keys():
			print "%s = %s", str(key), str(map[key])
	
			
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
			self.LogError("Error: select query not set yet!")
			return None
		result = []
		try:
			self._db.SetFetchReturnsList(listonly)
			try:
				con = self._db.GetConnection(self.__service)
			except:
				self.LogError(_("Failed to connect to backend in DBObject.Select()"), map)
				return None
			cursor = con.cursor()
			try:
				if map is not None:
					cursor.execute(self._qSelect, map)
				else:
					cursor.execute(self._qSelect)
			except:
				self.LogError(_("Failed to execute query in DBObject.Select()"), map)
				return None
			if maxfetch>0:
				result =  cursor.fetchmany(maxfetch)
			else:
				result = cursor.fetchall()
				print result
		finally:
			self._db.SetFetchReturnsList(0)
		if result is None:
			result = []
		return result
		
		
	def Insert(self, map):
		"""insert a row with attributes as listed in the dictionary 'map'.
		Returns the OID is succesful, otherwise returns 'None'"""
		oid = None
		if self._qInsert is None:
			self.LogError("Error: insert query not set yet!")
			return None
		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			self.LogError(_("Failed to connect to backend in DBObject.Select()"), map)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qInsert, map)
		except:
			self.LogError(_("Failed to execute query in DBObject.Insert()"), map)
			return None
		oid = cursor.oidValue
		con.commit()
		return oid
		
	
	def Update(self, map):
		"""update a row with attributes as listed in the dictionary "map".
		'map' dictionary  MUST contain the key 'primarykey' with the
		value set to the primay key of the row to be updated
		Returns 'None' if failed, the primary key if success """
		if self._qUpdate is None:
			self.LogError("Error: update query not set yet!")
			return None
		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			self.LogError(_("Failed to connect to backend in DBObject.Select()"), map)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qUpdate,map)
		except:
			self.LogError(_("Failed to execute query in DBObject.Insert()"), map)
			return None
		con.commit()
		return primarykey
	
	
	def Delete(self, map):
		"""deletes a row as determined by the delete query string.
		'map' dictionary  MUST contain the key 'primarykey' with the
		value set to the primay key of the row to be deleted
		Returns 'None' if failed, the primary key if success """
		if self._qDelete is None:
			self.LogError("Error: delete query not set yet!")
			return None
		try:
			con = self._db.GetConnection(self.__service, readonly=0)
		except:
			self.LogError(_("Failed to connect to backend in DBObject.Select()"), map)
			return None
		cursor = con.cursor()
		try:
			cursor.execute(self._qDelete, map)
		except:
			self.LogError(_("Failed to execute query in DBObject.Delete()"), map)
			return None
		con.commit()
		return primarykey
		

if __name__ == "__main__":
	import gmPG
	db=gmPG.ConnectionPool()
	dbo = DBObject(db, select_query = "select * from pg_tables where tablename not like 'pg_%'")
	rows = dbo.Select()
	for row in rows:
		print ""
		for key in row.keys():
			print "%s=%s," % (key, str(row[key])) ,
		