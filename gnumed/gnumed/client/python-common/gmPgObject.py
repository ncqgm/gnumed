#############################################################################
#
# gmPgObject - database row abstraction for gnumed
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: DB-API 2.0 compliant PostgreSQL adapter
#                CAVE: fetch() has to return a list !!!
#                when using pyPgSQL, set pyPgSQL.PgSQL.fetchReturnsList=1
#
# @TODO: Almost everything
# - compound primary keys (primary keys spanning more than one column)
# - write queries / write access
# - automatic child object creation for foreign keys
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmPgObject.py,v $      
__version__ = "$Revision: 1.13 $"                                               
__author__ = "Horst Herb <hherb@gnumed.net>"

import string

#==============================================================
QTablePrimaryKey = """
SELECT
	indkey
FROM
	pg_index
WHERE
	indrelid =
	(SELECT oid FROM pg_class WHERE relname = '%s');
"""

QTableForeignKeys = """
SELECT
	pg_trigger.*, pg_proc.proname, pg_class.relname, pg_type.typname
FROM
	pg_proc
		INNER JOIN pg_trigger ON pg_proc.oid = pg_trigger.tgfoid 
		INNER JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid 
		INNER JOIN pg_type ON pg_trigger.tgtype = pg_type.oid 
WHERE
	pg_class.relname = '%s';
"""

_cached_tables = []		
_table_metadata = {}
_column_indices = {}
_primarykeys = {}
_foreignkeys = {}
#==============================================================
def listForeignKeys(con, table):
	"""returns a dictionary of referenced foreign keys:
	key = column name of this table
	value = (referenced table name, referenced column name) tuple
	con = open database connection (DBAPI 2.0)"""
	global QTableForeignKeys
	references = {}
	cursor = con.cursor()
	try:
		cursor.execute(QTableForeignKeys % table)
	except ValueError:
		return {}
	d = cursor.description
	tgargs = 0
	#get the index of the column we are interested in, since we are fetching a list
	#and don't know anything about the order of columns in this table
	for row in d:
		if row[0] != 'tgargs':
			tgargs += 1
		else:
			break
	fkresult = cursor.fetchall()
	if len(fkresult) <=0:
		return {}
	for fk in fkresult:
		#ugly hack to cope with the NULL characters in the array
		fkarray = repr(fk[tgargs])
		fkname, referencing_table, referenced_table, dummy, referencing_column, referenced_column, dummy2  = string.split(fkarray, '\\x00')
		references[referencing_column] = (referenced_table, referenced_column)
	return references

def listPrimaryKey(con, table):
	"""return the column index of the primary key of the stated table
	con = open database connection (DBAPI 2.0)"""
	global QTablePrimaryKey
	cursor = con.cursor()
	cursor.execute(QTablePrimaryKey % table)
	pk = cursor.fetchone()
	return int(pk[0])-1

def cache_table_info(con, table, cursor=None):
	"""cache all relevant metatdata of the stated table
	if cursor is stated, use it otherwise a dummy query is executed
	con = open database connection (DBAPI 2.0)"""
	global _table_metadata
	global _column_indices
	global _primarykey
	global _foreignkeys
	global _cached_tables
	
	if table in _cached_tables:
		return
		
	if cursor is None:
		cursor = con.cursor()
		cursor.execute("select * from %s limit 1" % table)
		
	_table_metadata[table] = cursor.description
	_foreignkeys[table] = listForeignKeys(con, table)
	_primarykeys[table] = listPrimaryKey(con, table)
	index = {}
	for i in range(len (cursor.description)):
		index[cursor.description[i][0]] = i
	_column_indices[table] = index
	_cached_tables.append(table)
	
#==============================================================
class pgobject:
	
	def __init__(self, db, table, pkey = None):
		"""db = gmPG.ConnectionPool object
		table = service and table as string in the format 'service.table'
		pkey: if stated, the object will be initialized from the backend 
		            using this primary key value"""
		
		#index of columns by column names
		self._index = None
		#DBAPI cursor.description
		self._metadata = None
		#list of referenced foreign keys
		self._foreignkeys = None
		#cache for referenced objects
		self._referenced = {}
		#fetched row data
		self._row = None
		#name of the service and table this object is representing
		st = string.split(table, '.')
		if len(st) == 1:
			self._service = 'default'
			self._tablename = st[0]
		else:
			self._service = st[0]
			self._tablename = st[1]
		#database connection broker
		self._dbbroker = db
		#reuseable open read-only database connection
		self._db = db.GetConnection(self._service)
		#'dirty' flags: list of columns (colum names) that have been modified
		self._modified = []
		#value of the primary key
		self._pkey = None
		#column(s) holding the primary key
		self._pkcolumn = None
		#the primary key of the last row that has been fetched
		self._fetched = None
		if pkey is not None:
			self.fetch(pkey)
	#---------------------------------------------
	def new_primary_key(self):
		"""returns a new primary key safely created via the appropriate backend sequence"""
		cursor.execute("select nextval('%s_%s_seq')" % (self._tablename, self._pkcolumn))
		pk, = cursor.fetchone()
		return pk
	#---------------------------------------------
	def __getitem__(self, aCol = None):
		"""Any class[x] is turned into class.__getitem__(self, x).

		returns a column by name or index
		"""
		# sanity checks
		if self._primarykey is None:
			return None
		if aCol is None:
			return None
			# FIXME: or rather return all columns ?

		# lazy access: did we fetch the data yet ?
		if self._fetched is None:
			# actually retrieve the row now
			self._fetch()

		if self._row is None:
			return None

		#are we indexing the column by ordinal number or by column name?
		if type(aCol) == int:
			return self._row[aCol]
		else:
			# does the given column name reference another table
			# (i.e. is it a foreign key) ?
			if self._foreignkeys.has_key(aCol):
				# yep, but not retrieved yet
				if not self._referenced.has_key(aCol):
					# so get it
					ref = pgobject(
						db = self._dbbroker,
						table = "%s.%s" % (self._service, self._foreignkeys[aCol][0]),
						pkey = self._row[self._index[aCol]]
					)
					# and keep a reference
					self._referenced[aCol] = ref
				#print "-> reference:", self._foreignkeys[aCol][0], self._foreignkeys[aCol][1]
				return self._referenced[aCol]
			else:
				return self._row[self._index[aCol]]
	#---------------------------------------------
	def __setitem__(self, key, value):
		"set the value of the column as determined by either column name or index"
		newflag = 0
		#is table metadata already cached?
		if self._index is None:
			self._update_metadata()
		# are we dealing with a fetched row or with a new record?
		if self._row is None:
			#create an empty record if neccessary
			newflag=1
			self._row = []
			for idx in range(len(self._metadata)):
				self._row.append(None)
		#are we indexing the column by ordinal number or by column name?
		if type(key) == int:
			idx = key
		else:
			idx = self._index[key]
		#has the column value really changed?
		if value != self._row[idx]:
			#changed once is enoug to remember
			if key not in self._modified:
				self._modified.append(key)
		self._row[idx] = value
		if newflag:
			#if a new record is accessed, we must refresh it from the backend
			#in order to fill the columns with the default values
			self._save()


		
		
	def __del__(self):
		self._save()
		
			
	def _save(self):
		#only save if there is data
		is_new=0
		if self._row is None:
			#nothing to save
			return
		#only save if something has been modified:
		if len(self._modified) > 0:
			if self._fetched > 0:
				#existing data has been modified
				colvals = "%s = %s" % (self._modified[0], self._quote(self._row[self._index[self._modified[0]]]))
				for column in self._modified[1:]:
					colvals = "%s , %s = %s" % (colvals, column, self._quote(self._row[self._index[column]]))
				query = "update %s set %s where %s = %s" % (self._tablename, colvals, self._pkcolumn, self._primarykey)
			else:
				#a new row has to be inserted
				is_new=1
				columns = ""
				count = 0
				#create a "safe" primary key (assumption: primary key is of type "serial")
				self._primarykey = self.new_primary_key()
				self._row[self._index[self._pkcolumn]] = self._primarykey
				if self._pkcolumn not in self._modified:
					self._modified.append(self._pkcolumn)
				for column in self._modified:
					value = self._row[self._index[column]]
					if value is not None:
						count += 1
						#print "quoting"
						value = self._quote(value)
						if count == 1:
							columns = column
							values = value
						else:
							columns = "%s, %s" % (columns, column)
							values = "%s, %s" % (values, value)
				query = "insert into %s(%s) values(%s)" % (self._tablename, columns, values)
			db = self._dbbroker.GetConnection(self._service, 0)
			cursor = db.cursor()
			cursor.execute(query)
			db.commit()
			self._modified = []
			if is_new:
				#reload row from backend, since columns may have changed 
				#through default constraints
				print "refreshing table ..."
				self._fetch()
	#---------------------------------------------
	def _quote(self, arg):
		"postgres specific quoting: strings in '', single ' escaped by another '"
		if type(arg) is str:
			q = "'%s'" % arg.replace("'", "''")
		else:
			q = str(arg)
		return q
	#---------------------------------------------
	def _fetch(self, primarykey = None):
		"""Actually fetch the row from the table determined by the primary key.

		if primarykey is not stated, the current object is
		refreshed from the backend
		"""
		#self._save()
		if primarykey is not None:
			self._primarykey = primarykey
		if self._pkcolumn is None:
			self._update_metadata()
		cursor = self._db.cursor()
		query = "select * from %s where %s = %s" % (self._tablename, self._pkcolumn, self._primarykey)
		cursor.execute(query)
		self._row = cursor.fetchone()
		#did the query return a row?
		if (self._row is None) or (len(self._row) <=0):
			self._fetched = 0
		else:
			self._fetched = self._primarykey
		#data that has been just fetched cannot be modified yet
		self._modified = []
		cursor.close()
	#---------------------------------------------
	def _update_metadata(self, cursor=None):
		"cache the table's meta data"
		global _column_indices
		global _pkcolumn
		global _foreignkeys
		global _table_descriptions
		cache_table_info(self._db, self._tablename, cursor)
		self._metadata = _table_metadata[self._tablename]
		self._index = _column_indices[self._tablename]
		self._pkcolumn = self._metadata[_primarykeys[self._tablename]][0]
		self._foreignkeys = _foreignkeys[self._tablename]
	#---------------------------------------------
	def fetch(self, primarykey):
		"""Fetch the row determined by the primary key attribute.

		lazy data access: data will not really be fetched before it is accessed"""
		#if we have data in cache, save it first; 'save()' will check for modifications first
		if self._fetched:
			self._save()
		self._fetched = None
		self._primarykey = primarykey
	#---------------------------------------------
	def save(self):
		"""force the current data to be written to the backend manually"""
		self._save()
	#---------------------------------------------
	def undo(self):
		"""reset the state ofthe row to the state it has on the backend"""
		if self._fetched:
			self._fetch()
		else:
			print "Undo for new objects not impemented yet"
		
#==============================================================				
if __name__ == "__main__":

	import sys, gmPG, gmLoginInfo
	
	login = gmLoginInfo.LoginInfo(user="hherb", passwd='')
	db = gmPG.ConnectionPool(login)
	db.SetFetchReturnsList(1)

	#request a writeable connection and create test tables
	con = db.GetConnection('default', readonly = 0)
	cursor = con.cursor()

	try:
		cursor.execute("drop sequence test_pgo_id_seq;")
		con.commit()
		cursor.execute("drop table test_pgo;");
		con.commit()
	except:
		pass

	try:
		cursor.execute("drop sequence test_pgofk_id_seq")
		con.commit()
		cursor.execute("drop table test_pgofk");
		con.commit()
	except:
		print "table test_pgofk or sequence test_pgofk_id_seq did not exist"
		
	try:
		cursor.execute("create table test_pgofk (id serial primary key, text text, ts timestamp default now())")
		cursor.execute("create table test_pgo (id serial primary key, id_fk integer references test_pgofk, text text, ts timestamp default now())")
		con.commit()
	except:
		print "Could not create test tables on backend. Test failed"
		sys.exit(-1)
	
	try:
		cursor.execute("insert into test_pgofk(text) values('this is the text in the referenced table')")
		cursor.execute("insert into test_pgo(id_fk, text) values(1, 'this is the text in the referencing table 1')")
		cursor.execute("insert into test_pgo(id_fk, text) values(1, 'this is the text in the referencing table 2')")
		con.commit()
	except:
		print "Cannot fill test tables with default values! - Test failed."
		sys.exit(-1)
		
	dbo = pgobject(db, 'test_pgo', 1)
	print dbo['text'], str(dbo['ts'])
	print "Now changing a value, should force a backend update"
	dbo['text'] = "it really works!!!"
	print dbo['text']
	dbo.fetch(2)
	print dbo['text'], str(dbo['ts'])
	dbo.fetch(1)
	print dbo['text'], str(dbo['ts'])
	dbo = pgobject(db, 'test_pgo')
	dbo['text'] = "this wasn't there before"
	dbo = pgobject(db, 'test_pgo', 1)
	print dbo['id_fk']['text'] 
	dbo['id_fk']['text'] = "this is a new foreign key for table 1!"
	print "\nText before change:", dbo['text']
	dbo['text'] = "I just changed it!"
	print "Text after change (not committed):", dbo['text']
	dbo.undo()
	print "Text after undo:", dbo['text']
	
#==============================================================
# $Log: gmPgObject.py,v $
# Revision 1.13  2003-02-07 14:26:28  ncq
# - code commenting, basically
#
# Revision 1.12  2003/02/03 16:25:56  ncq
# - coding style
#
# Revision 1.11  2003/01/16 14:45:04  ncq
# - debianized
#
# Revision 1.10  2002/10/26 04:43:06  hherb
# Undo implemented for fetched rows modified before committtment
# Manually enforced "save" implemented
#
# Revision 1.9  2002/10/26 04:32:32  hherb
# minor code cleanup, comments added
#
# Revision 1.8  2002/10/26 04:14:24  hherb
# when a newly created object (row) is first modified, it is saved to the backend and refreshed from the backend in order to load default values
#
# Revision 1.7  2002/10/26 02:47:08  hherb
# object changes now saved to backend. Foreign key references now transparently dereferenced (write access untested)
#
# Revision 1.6  2002/10/25 13:04:15  hherb
# API change: pgobject constructor takes now gmPG.ConnectionPool as argument insted of an open connection
# Write functionality now enabled, quoting works for strings, some datatypes still will crash
#
# Revision 1.5  2002/10/24 21:41:40  hherb
# quoting of strings in write queries
#
# Revision 1.4  2002/10/23 22:08:49  hherb
# saving changes to backend partially implemented (query string generation); still needs quoting fixed
#
# Revision 1.3  2002/10/23 15:05:47  hherb
# "Lazy fetch" now working when primary key passed as parameter to class constructor
#
# Revision 1.2  2002/10/23 15:01:24  hherb
# meta data caching now working
#
# Revision 1.1  2002/10/23 14:34:43  hherb
# database row abstraction layer
#