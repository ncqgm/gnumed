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

import gmDBCache

class PersonCache(gmDBCache.DBcache):
	pass

class CachedPerson(gmDBCache.CachedDBObject):
	__dbcache = PersonCache()

	def __init__(self, db):
		self.cache = CachedPerson.__dbcache
		gmDBCache.CachedDBObject.__init__(self, self.cache, id=-1, db=db,
		                          querystr="select * from v_basic_person where id = %d")

	def get(self, id=None, by_reference=0):
		#allow only searches when the id is available
		assert(self.cache.id is not None or id is not None)
		return gmDBCache.CachedDBObject.get(self, id, by_reference)


if __name__ == "__main__":
	import gmPG
	conn = gmPG.ConnectionPool()
	db = conn.GetConnection('demographica')

	p = CachedPerson(db)
	(data,) = p.get(id=1)
	for a in data:
		print a

