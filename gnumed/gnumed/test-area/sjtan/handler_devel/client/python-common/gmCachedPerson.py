#############################################################################
#
# gmCachedPerson - data broker for single person information
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	10.03.2002 hherb first draft, largely untested
#
# @TODO: Almost everything
############################################################################

import gmDBCache, gmPG

class PersonCache(gmDBCache.DBcache):
	pass

class CachedPerson(gmDBCache.CachedDBObject):
	__dbcache = PersonCache()

	def __init__(self, db=None):
		#reference our class hierarchy level "singleton" cache
		self.cache = CachedPerson.__dbcache
		#make sure we allocte the default database connection
		#in case no connection has been passed as parameter
		if db is None and self.cache.db is None:
			conn = gmPG.ConnectionPool()
			self.cache.db = conn.GetConnection('demographica')

		gmDBCache.CachedDBObject.__init__(self, self.cache, id=-1, db=db,
		                          querystr="select * from v_basic_person where id = %d")

	def get(self, id=None, by_reference=0, refresh_only=0):
		#allow only searches when the id is available
		assert(self.cache.id is not None or id is not None)
		return gmDBCache.CachedDBObject.get(self, id, by_reference, refresh_only)

	def addresses_link(self, id):
		cursor = self.cache.db.cursor()
		# changed from selecting id_address to id inorder to get type
		cursor.execute("select id from identities_addresses where id_identity = %d" % id)
		addresses_link = cursor.fetchall()
		print "from identities_addresses: address_link  id s= ", addresses_link
		return addresses_link

	def dictresult(self, id=None):
		if id is not None:
			self.get(id, refresh_only=1)
		try:
			return gmDBCache.CachedDBObject.dictresult(self)[0]
		except:
			return None

	def create_person(self, map, db):
				"""create a person through sql , but no transaction statements"""
		                queries = []

                                queries.append( """insert into v_basic_person ( title,lastnames, firstnames,  gender, dob, cob )        
	                               values ('%(title)s', '%(lastnames)s', '%(firstnames)s',  '%(gender)s', '%(dob)s', '%(cob)s')"""%map) 
				cursor = db.cursor()

				for x in queries:
					print x
					cursor.execute(x)

	def update_person(self, personMap, db):
			queries = []
			queries.append("""update v_basic_person set title='%(title)s',  lastnames='%(lastnames)s', firstnames='%(firstnames)s',
				gender= '%(gender)s',  dob='%(dob)s', cob ='%(cob)s' where id=%(id)d""" %personMap )

                        cursor = db.cursor()

                        for x in queries:
				print x
				cursor.execute(x)

			self.reset()
			self.notify()




if __name__ == "__main__":
	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('demographica')

	p = CachedPerson(db)
	(data,) = p.get(id=1)
	for a in data:
		print a
	print p.dictresult()

