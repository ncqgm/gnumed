#!/usr/bin/python
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

	def dictresult(self):
		try:
			return gmDBCache.CachedDBObject.dictresult(self)[0]
		except:
			return None


if __name__ == "__main__":
	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('demographica')

	p = CachedPerson(db)
	(data,) = p.get(id=1)
	for a in data:
		print a
	print p.dictresult()

