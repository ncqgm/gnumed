#############################################################################
#
# gmCachedDBObject : abstraction and performance improvement for simple
#                     database query result objects
#
#
# CachedDBObject is a base class which should not
# be used directly.
# In order to derive a functional class from CachedDBObject, do as follows:
#
# class Derived(CachedDBObject):
#
#       #first, create the "shared buffer" variable
#	dbcache = DBcache()
#       #this static variable MUST have the name "dbcache"
#       #it must create an instance of DBcache or a subclass thereof
#
#       #then, create the appropriate constructor
#	def __init__(...)
#		#now create a reference to the static variable
#		self.cache = Derived.dbcache
#		#and pass it to the constructor
#		cachedDBObject.__init__( cache=self.cache...)
#               #__init__ MUST call the base class constructor
#
# When creating more than one instance from "Derived",
# the callback system should be used to ensure that any
# instance using the shared buffer gets notified of buffer changes:
#
# myInstance = Derived(...)
# myInstance.notify_me('identifier of myInstance', callback_function)
#
# where 'identifier of myInstance' is an arbitrary string and
# 'callback function' is a function of the prototype:
#
# function('identifier of callback triggering class', 'id')
#
# where 'id' typically would be the foreign key causing the
# current data set in the buffer
#
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL v2 or later (details at http://www.gnu.org)
# @dependencies: gmPG
# @change log:
#	15.03.2002 hherb first draft, untested
#	27.03.2002 hherb started working on thread safety
#
# @TODO: Almost everything
############################################################################

# standard Python modules
import copy, threading
# GNUmed modules
import gmLog, gmPG

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DBcache:
	"prototype for a database object cache 'static' (singleton) information"
	def __init__(self):
		self.buffer = None	#the buffer holding the query result(s)
		self.id = None	#the unique database object id, if applicable
		self.db = None	#the backend connection handle
		self.querystr = None	#the backend query string (SQL)
		self.lazy = 1	#default: set lazy on
		self.expiry = -1	#default: buffer never expires
		self.lastquery = None	#timestamp of last executed query
		self.notify = {}	#callback function dictionary;
		                        #key is registrar id, value is callback function
		self.attributes = []	#list of attribute ('fields') labels
		self.querylock = threading.Lock()	#for multithreaded applications:
		                                        #to prevent dirty buffer reads
		self.notifylock = threading.Lock()	#for multithreaded applications:
		                                        #to prevent dirty widget updates
		self.notifyqueue = 0	#for multithreaded applications:
		                        #to prevent unnecessary widget updates


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CachedDBObject:

	#static private variables (singleton style):
	__dbcache = DBcache()

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def __init__(self, cache=None, id=None, db=None, querystr=None, lazy=None, expiry=None):

		#derived classes MUST replace CachedDBObject with their own classname!
		if cache is None:
			self.cache = CachedDBObject.__dbcache
		else:
			self.cache = cache
		#exec("self.cache = %s.dbcache" % self.__class__.__name__)

		self.who = None	#ID for callback function

		if db is not None:
			if self.cache.db is not db:
				self.cache.db = db
				self.reset

		if id is not None:
			self.setId(id)

		if querystr is not None:
			self.setQueryStr(querystr)

		if expiry is not None:
			self.cache.expiry = expiry

		if not lazy and self.cache.buffer is not None:
			self.__query()
		#<DEBUG>
		#_myLog.Log(gmLog.lData, "Instantiated. ID='" + str(self.cache.id) +
		#		"' DB='" + str(self.cache.db) +
		#		"' query='" + str(self.cache.querystr) +
		#		"' lazy='" + str(self.cache.lazy) +
		#		"' expiry='" + str(self.cache.expiry) + "'")
		#</DEBUG>

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def reset(self):
		"force a re-query of buffer on next data access attempt"
		print "Resetting cache"
		self.cache.querylock.acquire(1)
		self.cache.buffer = None
		self.cache.lastquery = None
		self.cache.querylock.release()

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def setQueryStr(self, querystr):
		if self.cache.querystr != querystr :
			self.cache.querystr = querystr
			self.reset
			#<DEBUG>
			#_myLog.Log(gmLog.lData, "changing query to SQL>>>" + str(querystr) + "<<<SQL")
			#</DEBUG>

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def getQueryStr(self):
		return copy.copy(self.cache.querystr)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def setId(self, id, lazy=0):
		print"Person setId to ", id
		if lazy:
			if self.cache.id != id:
				self.cache.id = id
				self.reset()
		else:
			self.get(id=id, refresh_only=1)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def getId(self):
		"get the ID of the current object"
		return self.cache.id

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def get(self, id=None, by_reference=0, refresh_only=0):
		"""returns the buffer. If id is not None and not in cache,
		the backend will be queried.
		If by_reference is not zero, a copy of the buffer instead of a reference
		to it will be returned.
		When using multiple threads to access the data,
		always use copies of the buffer!
		"""
		#<DEBUG>
		#print "get called by [%s]" % self.who
		#</DEBUG>
		if id is not None:
			if self.cache.id != id:
				self.cache.id = id
				self.reset()
		if self.cache.buffer is None:
			self.__query()
		#make sure we are not accessing the buffer while a query modifies it
		self.cache.querylock.acquire(1)
		try: #make sure the lock is released, no matter what
			if not by_reference:
				buf = copy.deepcopy(self.cache.buffer)
			else:
				buf = self.cache.buffer
		finally: #make sure the lock is released, no matter what
			self.cache.querylock.release()
		if not refresh_only:
			return buf

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def notify_me(self, who, callback=None):
		"""Register function 'callback' for caller 'who'

		If callback is None, the callback for caller 'who'
		will be removed (if exists)
		'callback' is a function that accepts two parameters:
		The first parameter is the identity of the registered
		caller ('who'), the second parameter is the buffer id.
		'callback' must not return anything"""
		if callback is None:
			try:
				del(self.cache.notify[who])
			except:
				pass
		else:
			self.who = who	#remember who I am
			self.cache.notify[who] = callback


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def queue_notification(self, queue=1):
		"simple helper mechanism to ensure only the most recent thread updates widgets on data change"
		self.cache.notifylock.acquire(1)
		if queue==1:
			notifyqueue = self.cache.notifyqueue + 1
		else:
			#reset the queue
			notifyqueue = 0
		self.cache.notifyqueue = notifyqueue
		self.cache.notifylock.release()
		return notifyqueue


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def notify(self):
		"""forces execution of all registered callback functions
		This function will be called whenever the buffer changes
		"""
		#prevent multiple threads from messing up
		#this is a nasty lock which might block
		nq= self.queue_notification()
		#make sure we release the lock even if something goes wrong
		for caller in self.cache.notify.keys():
			#as the next statement is "python thread atomic", it should not be affected
			#by thread concurrency - we should not need a thread lock here (?)
			if self.cache.notifyqueue>nq:
				#another thread has made a newer buffer modification,
				#let it do the job instead
				return
			#do not notify me if I triggered the query myself
			if caller != self.who:
				#first parameter to callback function is the
				#identity of the class triggering the callbacks,
				#second parameter is the buffer id
				self.cache.notify[caller](self.who, self.cache.id)
			#<DEBUG>
			#else:
			#	print "Callback function skipped for [%s]" % self.who
			#</DEBUG>
		nq = self.queue_notification(0) #finished notifying, we can reset the queue


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def attributes(self):
		"returns row attributes ('field names')"
		return self.cache.attributes


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def pprint(self):
		"format buffer content in printable form"
		buf = self.get(by_reference=0)
		#labels = self.attributes()
		pstr=''
		for row in buf:
			for attr in row:
				pstr =  "%s %s | " % (pstr, str(attr))
			pstr = pstr + "\n"
		return pstr


	def dictresult(self):
		if self.cache.buffer is None:
			print self, "self.cache.buffer == None"
			return None
		dictres = []
		index=0
		for f in self.cache.buffer:
			dict = {}
			i=0
			for a in self.cache.attributes:
				dict[a]=f[i]
				i+=1
			dictres.append(dict)
		return dictres


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	def __query(self):
		#<DEBUG>
		#print "%s doing a query" % self.who
		#</DEBUG>

		assert (self.cache.db is not None)
		if self.cache.querystr is None:
			return None
		#assert (self.cache.querystr is not None)

		#make sure different threads are not trying
		#to cause the buffer update concurrently
		self.cache.querylock.acquire(1)
		#make sure we release the lock even if something goes wrong
		try:

			cursor = self.cache.db.cursor()
			#<DEBUG>
			#print "Executing %s\n" % self.cache.querystr
			#</DEBUG>
			if self.cache.id is not None:
				querystr = self.cache.querystr % self.cache.id
			else:
				querystr = self.cache.querystr
			print "Executing query " , querystr
			cursor.execute(querystr)
			print "filling buffer"
			self.cache.buffer = copy.deepcopy(cursor.fetchall())
			self.cache.attributes = gmPG.fieldNames(cursor)
		finally:
			self.cache.querylock.release()
		#now let everybody know that our buffer has changed
		self.notify()


        def getSqlSettings(self):
                return ["set datestyle to european", "set transaction isolation level serializable"]




##############################################################
# convenience only, really
_myLog = gmLog.gmDefLog

if __name__ == "__main__":


	class tables(CachedDBObject):
		dbcache = DBcache()
		def __init__(self, db):
			cache=tables.dbcache
			CachedDBObject.__init__(self, cache, db=db, querystr="select * from pg_tables where tablename not like 'pg_%'")

	class dbs(CachedDBObject):
		dbcache = DBcache()
		def __init__(self, db):
			cache=dbs.dbcache
			CachedDBObject.__init__(self, cache, db=db, querystr="select datname from pg_database")


	#<DEBUG>
	#aHandle = gmLog.LogTargetConsole(gmLog.lData)
	#_myLog.AddTarget(aHandle)
	#</DEBUG>

	def callback(who, id):
		print ">>> Here I am, the callback function! <<<"
		print ">>> My id is %s <<<" % str(id)
		print ">>> I was requested by %s <<<\n" % str(who)

	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('default')

	#instance of the base class
	databases = CachedDBObject(db=db, querystr="select * from pg_database")
	#register callback function for base class instance
	databases.notify_me("main", callback)

	#instances of derived classes
	tablelist = tables(db)
	#dbl and dbl2 share the same buffer, tablelist has it's own as
	#it is derived from a different subclass

	dbl = dbs(db)
	dbl.notify_me("dbl", callback)

	dbl2 = dbs(db)
	dbl2.notify_me("dbl2", callback)

	#databases will now access the backend. No callback should be fired,
	#as there is nobody to share the buffer with.

	dblist = databases.get()
	print "List of available databases:"
	print "-----------------------------------------------------"
	for d in dblist:
		for a in d:
			print str(a) + "\t",
		print "\n"
	dblist2 = databases.get()
	if dblist is dblist2:
		print "Something went wrong!\nReference instead of copy returned for shared buffer"
		import sys
		sys.exit(1)

	print "List of tables in current database:"
	print "-----------------------------------------------------"
	print tablelist.pprint()

	#now dbl should access the data, and dbl2 should get notified
	#via callback that the buffer has changed

	print "List of databases (names only):"
	print "-----------------------------------------------------"
	print dbl.pprint()

	#just to demonstrate that dbl and dbl2 have not modified
	#the base class buffer
	print "List of databases (all attributes again):"
	print "-----------------------------------------------------"
	print databases.pprint()
	print "-----------------------------------------------------"
	print dbl2.pprint()

	print "This should be true (1):", dbl.cache is dbl2.cache
	print "This should be false(0):", dbl.cache is tablelist.cache




