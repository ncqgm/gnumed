
"""Operations are Load, Create, Update, Find.
use case:
	load an existing identity using the information in testschema.

	
	


"""
import testschema5 as testschema
import pgdb
import traceback,sys

#credentials = "localhost:gnumed:any-doc:any-doc"
credentials = "hherb.com:gnumed:any-doc:any-doc"

class Loader:

	def __init__(self):
		self.values = {}
		self.collections = {}
		self.refs = {}
		self.subclass = {}
		self.conn = pgdb.connect(credentials)
		self.descriptions= {}
		pass	

	def setSchema(self, s):
		self.schema = s
		self.m = {}
		self.fk_details = self.schema.get_fk_details()
		self.pks = dict ( self.schema.get_pk_attr() )
		

	def loadRoot(self, x, id):
		m = self.schema.getModelFor(x)
		self.loadById(x, m, id)

	def assertValues(self, name):
		if not self.values.has_key(name):
			self.values[name] = {}
		
	def assertCollections(self, name,  id):
		self._assertExists(self.collections, name, id)
	
	def assertRef( self,name, id):
		self._assertExists(self.refs, name, id)

	def assertSubClass(self, name, id):
		self._assertExists(self.subclass, name, id)

	
	def _assertExists(self, map, name, id):
		if not map.has_key(name):
			map[name] = {}
		
		if not map[name].has_key(id):
			map[name][id] = {}
		
	
	def loadSimpleAttributes (self, name, id):
		"""
		@type name: string
		@param name: the name of the table to load attributes from.
		@type id : int
		@param id: the primary key value which selects the row of the table from which to load attributes

		uses schema.get_attributes(tablename) to get filtered attributes (
		excluding infrastructure fields e.g. fields for auditing ;  postgres fields, 
		negatively numbered in pg_attribute; foreign key fields.
		"""
		attrs = self.schema.get_attributes(name)
		pk = self.pks[name]
		stmt = "select %s from %s where %s=%d" % ( ', '.join(attrs), name, pk, id)
		self.assertValues(name)	
		l = self.execute(stmt,name)
		if len (l) > 0:
			self.values[name][id] = l[0]
		
		

	def loadById( self, name, m, id ):
		id = int(id)
		self.loadSimpleAttributes( name, id )
			
		for k, (tag, map) in m.items():
			if tag == '-*':
				self.loadCollection( name, id, k, map)
			elif tag == '-1':
				# this try is for the case where -1 is a reversed_link
				# i.e. a many-to-one relationship (A->B) represented by a link from
				#  B to A.
				try:
					self.loadRefAttribute(name, id, k,map)
				except:	
					self.loadCollection(name, id, k, map)	

		for k, (tag, map) in m.items():
			if tag == '<-':
				self.loadSubClass(name, id, k, map)
				if self.hasSubClassInstance( name, id, k):
					self.mergeSubClassClassInstances(name, id, k)
			
	def getFkDetail(self, referer, referred):
		return filter( lambda( (t1,a1,t2,a2)): t1 == referer and t2 == referred, self.fk_details)
			
	def getSelectChildPk( self, referer, referred):
		l = self.getFkDetail(referer, referred)
		print "for getSelectedChildPk l is", l
		if len(l) >= 1:
			"""
			a1 - attribute referer
			a2 - attribute referred
			"""
			t1,a1,t2,a2 = l[0]
			stmt = """select a.%s from %s a,  %s b  where a.%s = b.%s and b.%s = %%d""" % (self.pks[referer], referer, referred, a1, a2,  self.pks[referred]  ) 
		#	print "a1, a2, stmt ", a1, a2, stmt
			return stmt



	def getSelectRefPk(self, referer, referred):
		l = self.getFkDetail(referer, referred)
		#print "referer, referred , l ",referer, referred, l
		#print "self.fk_details", self.fk_details
		t1, a1, t2, a2 = l[0]

		pkReferer = self.pks[referer]
		pkReferred = self.pks[referred]
		return """select b.%s from %s a , %s b  where a.%s = %%d and a.%s = b.%s""" %  ( pkReferred, referer, referred, pkReferer, a1, a2)
		

	def getForeignIds( self, referredId, referer, referred ):
		stmt  = self.getSelectChildPk( referer, referred)
		if stmt is None:
			stmt = self.getSelectChildPk(referred, referer)
		#<DEBUG>
		print "in getForeignIds(), stmt = ", stmt, "referredId = ", referredId
		#</DEBUG>
		if referredId is None or stmt is None:
			return []
		cmd = stmt % referredId
		try:
			l = self.execute(cmd)
			ids = [ v[0] for v in l]
			return ids 
		except:
			for i in range(3):
				print sys.exc_info()[i]
			traceback.print_tb(sys.exc_info()[2])	

			return []

	def loadCollection(self, name , id, childName, childMap):
		ids = self.getForeignIds( id,  childName, name)
		
		for id2 in ids: 
			self.loadById( childName, childMap, id2) 

		self.assertCollections(name, id)
		self.collections[name][id][childName] = ids 
		
	
		
	def loadRefAttribute(self, name, id, childName, childMap):
		stmt = self.getSelectRefPk( name, childName)
		l = self.execute(stmt % id)
		if (len(l) == 0):
			return
		pk = l[0][0] 
		self.loadById(childName, childMap, pk)
		self.assertRef(name, id)
		self.refs[name][id][childName] = pk
	
	
		
	def execute(self, stmt, label = 'last'):
		cu = self.conn.cursor() 
		self.conn.commit()
		cu.execute(stmt)
		l = cu.fetchall()
		if not self.descriptions.has_key(label):
			self.descriptions[label] = cu.description
		cu.close()
		return l

	def loadSubClass (self, name, id, childName, childMap):
		stmt = "select %s from %s where %s = %%d" % ( self.pks[childName], childName, self.pks[name] )

		l = self.execute(stmt % id)
		if len(l) > 0:
			id2 = l[0][0]
			self.assertSubClass(name, id)
			self.subclass[name][id][childName] =id2
			print "found subclass id", childName, id2
			self.loadById(childName, childMap, id2)

	def hasSubClassInstance( self, name ,id, subName):
		return self.subclass.has_key(name) and self.subclass[name].has_key(id) and self.subclass[name][id].has_key(subName)

	def mergeSubClassClassInstances(self, name, id, subName):
		
		id2 = self.subclass[name][id][subName]
		self.assertValues(name)	
		m1 = self.values[name][id]
		self.assertCollections(name, id)
		c1 = self.collections[name][id]
		self.assertRef(name, id)
		r1 = self.refs[name][id]

		d2 = dict( [(v[0],1) for v in self.descriptions.get(subName, []) ] )
		for i in xrange(len(m1)):
			if not d2.has_key(self.descriptions[name][i][0]):
				self.values[subName][id2].append(m1[i])
			
		self.assertCollections(subName,id2)
		self.collections[subName][id2].update(c1)
		self.assertRef(subName,id2)
		self.refs[subName][id2].update(r1)
		
		del self.values[name][id]
		del self.collections[name][id]
		del self.refs[name][id]

	def showRoot( self, name, id):
		id = int(id)
		#m = self.schema.getModelFor(name)
		self.showById( name,  id, tabs = 0)

	def showById(self, name,  id, tabs):
		print tabs * '\t', id ,':', name

		
	#	l = [ (k, tags, map) for k, (tags,map) in m.items()]
	#	print "l", l
	#	def sortByTag( v1, v2):
	#		return cmp (v1[1], v2[1])
	#	l.sort(sortByTag)

		if self.values[name].has_key(id):
			print '\t' * (tabs),'  ', self.values[name][id]

	#	for k, tag, map in l:
			#if tag == '-*':
	#			print "checking (name, id, k)", name, id, k
		
		m = self.collections.get(name, {}).get(id, {})
		for k,v in m.items():
			for id2 in v:
				self.showById( k, id2, tabs+1) 
				
		m1 = self.refs.get(name, {}).get(id, {})
		for k, id2 in m1.items():
			self.showById( k, id2, tabs+1)

		#if self.refs.get(name,{}).get(id, {}).has_key(k):	
		# self.showById(  k, self.refs[name][id][k], tabs+1)

		m2 = self.subclass.get(name, {}).get( id, {})
		for k, id2 in m2.items():
			self.showById( k, id2, tabs+1)
		
		#if self.subclass.get(name,{}).get(id,{}).has_key(k):
		#			self.showById( k, map, self.subclass[name][id][k], tabs+1)
		

	def printState(self):
		print 'descriptions\t'*5
		for k,v in self.descriptions.items():
			print k, ':',  [x[0] for x in v]
			print
		print

		print 'values\t'*5
		for k,v in self.values.items():
			print '\t',k
			for k2, v2 in v.items():
				print '\t'*2, k2, v2
			
		print	
		print 'collections\t' * 5	
		for k,v in self.collections.items():
			print '\t', k
			for k2, v2 in v.items():
				print '\t'* 2, k2
				for k3, v3 in v2.items():
					print '\t' * 3, k3, v3
						
		print
		print

	

if __name__ == '__main__':

	config = testschema.config.split('\n')
	co = testschema.Config(config)
	s = testschema.SchemaParser(co)
	l = Loader()
	l.setSchema(s)

	while 1:
		try:
			[root,id] = [x.strip() for x in raw_input("Enter name of model root, id of instance (e.g. xlnk_identity,4  or identity,4 ):").split(',')]

			l.loadRoot(root, id)

			l.showRoot(root, id)
		except:
			for i in range(2):
				print sys.exc_info()[i]
			traceback.print_tb(sys.exc_info()[2])

		print '-' * 50
		if raw_input('Debug values, collections (y/n) ? ')[0] == 'y':
			l.printState()
