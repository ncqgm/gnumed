#!/usr/bin/env python
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
__version__ = "$Revision: 1.1 $"                                               
__author__ = "Horst Herb <hherb@gnumed.net>"
# $Log: gmPgObject.py,v $
# Revision 1.1  2002-10-23 14:34:43  hherb
# database row abstraction layer
#

import string


QTablePrimaryKey = """ SELECT indkey FROM pg_index WHERE indrelid =
(SELECT oid FROM pg_class WHERE relname = '%s') """


QTableForeignKeys = """SELECT pg_trigger.*, pg_proc.proname, pg_class.relname, pg_type.typname
FROM pg_proc INNER JOIN pg_trigger ON pg_proc.oid = pg_trigger.tgfoid 
INNER JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid 
INNER JOIN pg_type ON pg_trigger.tgtype = pg_type.oid 
WHERE pg_class.relname = '%s'"""

		
_table_metadata = {}
_column_indices = {}
_primarykeys = {}
_foreignkeys = {}


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
	fkresult = cursor.fetchall()
	if len(fkresult) <=0:
		return {}
	for fk in fkresult:
		fkarray = repr(fk['tgargs'])
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
		
	

class pgobject:
	
	def __init__(self, db, tablename, primarykey=None):
		#index of columns by column names
		self._index = None
		#DBAPI cursor.description
		self._metadata = None
		#list of referenced foreign keys
		self._foreignkeys = None
		#fetched row data
		self._row = None
		#open database connection
		self._db = db
		#name of the table this object is representing
		self._tablename = tablename
		#'dirty' flags: list of columns (colum names) that have been modified
		self._modified = []
		#value of the primary key
		self._primarykey = None
		#column(s) holding the primary key
		self._pkcolumn = None
		#the primary key of the last row that has been fetched
		self._fetched = None
		if primarykey is not None:
			self._fetch(primarykey)
	
		
	def __getitem__(self, key):
		"return the column as determined by either column name or column index"
		assert(self._primarykey is not None)
		if self._fetched is None or self._fetched != self._primarykey:
			self._fetch(self._primarykey)
		if self._row is None:
			return None
		#are we indexing the column by ordinal number or by column name?
		if type(key) == int:
			return self._row[key]
		else:
			return self._row[self._index[key]]
		
		
	def __setitem__(self, key, value):
		"set the value of the column as determined by either column name or index"
		#is table metadata already cached?
		if self._index is None:
			self._update_description()
		# are we dealing with a fetched row or with a new record?
		if self._row is None:
			#create an empty record if neccessary
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

		
		
	def __del__(self):
		self._save()
		
			
	def _save(self):
		#only save if there is data
		if self._row is None:
			print "No data to save ..."
			return
		#only save if something has been modified:
		if len(self._modified) > 0:
			if self._fetched > 0:
				print "Data has been modified, need to update backend"
			else:
				print "insert data into backend"
			
			
	
	def _fetch(self, primarykey):
		"fetch a row from the table as determined by the primary key"
		#self._save()
		self._primarykey = primarykey
		if self._pkcolumn is None:
			self._update_metadata()
		cursor = self._db.cursor()
		query = "select * from %s where %s = %s" % (self._tablename, self._pkcolumn, self._primarykey)
		#print query
		cursor.execute(query )
		self._row = cursor.fetchone()
		#did the query return a row?
		if (self._row is None) or (len(self._row) <=0):
			self._fetched = 0
		else:
			self._fetched = self._primarykey
		#data that has been just fetched cannot be modified yet
		self._modified = []
		

	def _update_metadata(self, cursor=None):
		"cache the tables meta data"
		global _column_indices
		global _pkcolumn
		global _foreignkeys
		global _table_descriptions
		cache_table_info(self._db, self._tablename, cursor)
		self._metadata = _table_metadata[self._tablename]
		self._index = _column_indices[self._tablename]
		self._pkcolumn = self._metadata[_primarykeys[self._tablename]][0]
		self._foreignkeys = _foreignkeys[self._tablename]
	
				
	def fetch(self, primarykey):
		"""fetch the row as determined by the primary key attribute
		lazy data access: data will not really be fetched before it is accessed"""
		#if we have data in cache, save it first; 'save()' will check for modifications first
		if self._fetched:
			self._save()
		self._primarykey = primarykey
		
		
				
if __name__ == "__main__":
# in order to test this you have to create a table 'testpgo'
# within the database gnumed first.
# create table testpgo(id serial primary key, text text, ts timestamp default now());

	from pyPgSQL import PgSQL as DB
	DB.fetchReturnsList=1
	db = DB.connect(database='gnumed')
	dbo = pgobject(db, 'testpgo', 1)
	print dbo['text'], str(dbo['ts'])
	dbo.fetch(2)
	print dbo['text'], str(dbo['ts'])
	print "Now changing a value, should force a backend update"
	dbo['text'] = "it really works!"
	print dbo['text']
	dbo.fetch(1)
	print dbo['text'], str(dbo['ts'])
	dbo.fetch(2)
	print dbo['text'], str(dbo['ts'])
	