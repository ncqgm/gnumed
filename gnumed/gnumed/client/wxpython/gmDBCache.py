#!/usr/bin/python
#############################################################################
#
# gmCachedDBObject : abstraction and performance improvement for simple
#                     database query result objects
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG
# @change log:
#	15.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

import copy

class CachedDBObject:

	#static private variables:
	__buffer = None
	__id = None
	__db = None
	__querystr = None
	__lazy = 1	#default: set lazy on
	__expiry = -1	#default: buffer never expires
	__lastquery = None	#timestamp of last executed query
	__notify = {}
	__attributes = []

	def __init__(self, id=None, db=None, querystr=None, lazy=None, expiry=None):

		if db is not None:
			if CachedDBObject.__db is not db:
				CachedDBObject.__db = db
				self.reset

		if id is not None:
			self.setId(id)

		if querystr is not None:
			self.setQueryStr(querystr)

		if expiry is not None:
			CachedDBObject.__expiry = expiry

		if not lazy and self.__buffer is not None:
			self.__query()


	def reset(self):
		"force a re-query of buffer on next data access attempt"
		CachedDBObject.__buffer = None
		CachedDBObject.__lastquery = None

	def setQueryStr(self, querystr):
		if CachedDBObject.__querystr != querystr :
			CachedDBObject.__querystr = querystr
			self.reset

	def getQueryStr(self):
		return copy.copy(CachedDBObject.__querystr)

	def setId(self, id):
		if CachedDBObject.__id != id:
			CachedDBObject.__id = id
			self.reset()

	def getId(self):
		"get the ID of the current object"
		return copy.copy(CachedDBObject.__id)


	def get(self, id=None, copy=1):
		"""returns the buffer. If id is not None and not in cache,
		the backend will be queried."""
		if id is not None:
			if CachedDBObject.__id != id:
				CachedDBObject.__id = id
				self.reset()
		if CachedDBObject.__buffer is None:
			self.__query()
		if copy:
			try:
				return copy.copy(CachedDBObject.__buffer)
			except:
				return CachedDBObject.__buffer
		else:
			return CachedDBObject.__buffer



	def notify_me(self, who, callback=None):
		"""Register function 'callback' for caller 'who'
		This function will be called whenever the buffer changes
		If callback is None, the callback for caller 'who'
		will be removed (if exists)
		'callback' is a function that accepts two parameters:
		The first parameter is the identity of the registered
		caller ('who'), the second parameter is the buffer id.
		'callback' must not return anything"""
		if callback is None:
			try:
				del(CachedDBObject.__notify[who])
			except:
				pass
		else:
			CachedDBObject.__notify[who] = callback


	def notify(self):
		"forces execution of all registered callback functions"
		for caller in CachedDBObject.__notify.keys():
			CachedDBObject.__notify[caller](caller, CachedDBObject.__id)

	def attributes(self):
		"returns row attributes ('field names')"
		return CachedDBObject.__attributes


	def __query(self):
		assert (CachedDBObject.__id is not None)
		assert (CachedDBObject.__db is not None)
		assert (CachedDBObject.__querystr is not None)
		cursor = CachedDBObject.__db.cursor()
		print "Executing %s\n" % CachedDBObject.__querystr
		cursor.execute(CachedDBObject.__querystr)
		CachedDBObject.__buffer = cursor.fetchall()
		CachedDBObject.__attributes = gmPG.fieldNames(cursor)
		#let everybody know that our buffer has changed
		self.notify()


##############################################################

if __name__ == "__main__":

	def callback(who, id):
		print ">>> Here I am, the callback function! <<<"
		print ">>> My id is %s <<<" % str(id)
		print ">>> I was requested by %s <<<\n" % str(who)

	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('default')
	databases = CachedDBObject(db=db, id=-1, querystr="select * from pg_database")
	databases.notify_me("main", callback)
	dblist = databases.get()
	print "List of available databases:"
	print "-----------------------------------------------------"
	for d in dblist:
		for a in d:
			print str(a) + "\t",
		print "\n"


