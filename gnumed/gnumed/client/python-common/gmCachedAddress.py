#############################################################################
#
# gmCachedAddress - data broker for a person's address
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

class AddressCache(gmDBCache.DBcache):
	pass

class CachedAddress(gmDBCache.CachedDBObject):
	__dbcache = AddressCache()

	def __init__(self, db=None):
		#reference our class hierarchy level "singleton" cache
		self.cache = CachedAddress.__dbcache
		#make sure we allocte the default database connection
		#in case no connection has been passed as parameter
		if db is None and self.cache.db is None:
			conn = gmPG.ConnectionPool()
			self.cache.db = conn.GetConnection('geographica')

		gmDBCache.CachedDBObject.__init__(self, self.cache, id=-1, db=db,
		                          querystr="select * from v_basic_address where id = %d")

	def get(self, id=None, by_reference=0, refresh_only=0):
		#allow only searches when the id is available
		assert(self.cache.id is not None or id is not None)
		return gmDBCache.CachedDBObject.get(self, id, by_reference, refresh_only)

	def create_address_link( self, addressMap, db):
		"""create an address_link. This has a processing dependency: The person database sequencer must have been used."""
		queries = []
        	queries.append( """insert into v_basic_address(number, street, street2, city, state,  country, postcode )
                   values ( '%(number)s', '%(street)s', '%(street2)s', trim(upper('%(city)s')),trim(upper('%(state)s')), '%(country)s','%(postcode)s' )"""%addressMap)

                queries.append("""insert into identities_addresses (id_identity, id_address, address_source ) select i.last_value,
                   a.last_value, CURRENT_USER from identity_id_seq i, address_id_seq a  """)

                                #also save the type in identities_addresses
                queries.append ("""update identities_addresses set id_type=(select id from address_type ia where trim(lower(ia.name)) = trim(lower('%(address_at)s'))) where identities_addresses.id = currval('identities_addresses_id_seq')""" % addressMap)

                #queries.append("""select currval('identity_id_seq'), currval('identities_addresses_id_seq')""")

		cursor = db.cursor()

		for x in queries:
			print x
			cursor.execute(x)


	def update_address_link(self, addressMap, db):
			queries = []
                        queries.append("""update v_basic_address set number= '%(number)s',street= '%(street)s',
                         street2='%(street2)s',  city=upper('%(city)s'),state=upper('%(state)s'), country='%(country)s',
                        postcode='%(postcode)s' where  id=%(id)d"""%addressMap)

			cursor = db.cursor()

	                for x in queries:
        	                print x
                	        cursor.execute(x)

                        self.reset()
                        self.notify()



			





	def dictresult(self, id=None):
		if id is not None:
			self.get(id, refresh_only=1)
		#try:
			return gmDBCache.CachedDBObject.dictresult(self)[0]
		#except Exception, errorStr:
		#		print "error in dictresult", errorStr
		#		return None



if __name__ == "__main__":
	p = CachedAddress()
	(data,) = p.get(id=1)
	for a in data:
		print a
	print p.dictresult()

