
"""Operations are Load, Create, Update, Find.
use case:
	load an existing identity.

	let x = identity

	load x attributes.

	for y in fk(x):
		load y
		store y by pk(y) in x under fk
		
	
	for y in fkTo(x):
		load y
		store y by pk(y) in x under fkTo


"""
import testschema5 as testschema
import pgdb
class Loader:

	def __init__(self):
		self.values = {}
		self.collections = {}
		self.refs = {}
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
		if not self.collections.has_key(name):
			self.collections[name] = {}
		if not self.collections[name].has_key(id):
			self.collections[name][id] = {}
	
	def assertRef( self,name, id):
		if not self.refs.has_key(name):
			self.refs[name] = {}
		
		if not self.refs[name].has_key(id):
			self.refs[name][id] = {}
			
	
	def loadSimpleAttributes (self, name, id):
		attrs = self.schema.get_attributes(name)
		pk = self.pks[name]
		stmt = "select %s from %s where %s=%d" % ( ', '.join(attrs), name, pk, id)
		self.assertValues(name)	
		l = self.execute(stmt)
		if len (l) > 0:
			self.values[name][id] = self.execute(stmt)[0]
		
		

	def loadById( self, name, m, id ):
		id = int(id)
		self.loadSimpleAttributes( name, id )
		
		for k, (tag, map) in m.items():
			if tag == '-*':
				self.loadCollection( name, id, k, map)
			elif tag == '-1':
				self.loadRefAttribute(name, id, k,map)
			elif tag == '<-':
				self.loadSubClass(name, id, k, map)
			
	def getFkDetail(self, referer, referred):
		return filter( lambda( (t1,a1,t2,a2)): t1 == referer and t2 == referred, self.fk_details)
			
	def getSelectChildPk( self, referer, referred):
		l = self.getFkDetail(referer, referred)
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
		t1, a1, t2, a2 = l[0]

		pkReferer = self.pks[referer]
		pkReferred = self.pks[referred]
		return """select b.%s from %s a , %s b  where a.%s = %%d and a.%s = b.%s""" %  ( pkReferred, referer, referred, pkReferer, a1, a2)
		

	def getForeignIds( self, referredId, referer, referred ):
		stmt  = self.getSelectChildPk( referer, referred)
		
		ids = [ v[0] for v in self.execute( stmt % referredId)]
		return ids 

	def loadCollection(self, name , id, childName, childMap):
		ids = self.getForeignIds( id,  childName, name)
		
		for id2 in ids: 
			self.loadById( childName, childMap, id2) 

		self.assertCollections(name, id)
		self.collections[name][id][childName] = ids 
		
	
		
	def loadRefAttribute(self, name, id, childName, childMap):
		stmt = self.getSelectRefPk( name, childName)
		pk = self.execute(stmt % id)[0][0] or None
		self.loadById(childName, childMap, pk)
		self.assertRef(name, id)
		self.refs[name][id][childName] = pk
		
		
	def execute(self, stmt):
		c = pgdb.connect("localhost:gnumed")
		cu = c.cursor() 
		cu.execute(stmt)
		l = cu.fetchall()
		self.lastDescription = cu.description
		cu.close()
		return l

	def loadSubClass (self, name, id, childName, childMap):
		pass		

	def showRoot( self, name, id):
		id = int(id)
		m = self.schema.getModelFor(name)
		self.showById( name, m, id, tabs = 0)

	def showById(self, name, m, id, tabs):
		print tabs * '\t', id ,':', name

		
		l = [ (k, tags, map) for k, (tags,map) in m.items()]
	#	print "l", l
		def sortByTag( v1, v2):
			return cmp (v1[1], v2[1])
		l.sort(sortByTag)

		if self.values[name].has_key(id):
			print '\t' * (tabs),'  ', self.values[name][id]

		for k, tag, map in l:
			if tag == '-*':
	#			print "checking (name, id, k)", name, id, k
				if self.collections[name].has_key(id):
					
					l = self.collections[name][id].get(k, [])	
					for id2 in  l:
						self.showById( k, map, id2, tabs+1) 
						
			elif tag == '-1':
				if self.refs[name][id].has_key(k):	
					self.showById(  k, map, self.refs[name][id][k], tabs+1)
			elif tag == '<-':
				pass	
		

		
	

if __name__ == '__main__':

	config = testschema.config.split('\n')
	co = testschema.Config(config)
	s = testschema.SchemaParser(co)
	l = Loader()
	l.setSchema(s)

	while 1:
		[root,id] = [x.strip() for x in raw_input("Enter name of model root, id of instance (e.g. xlnk_identity,4  or identity,4 ):").split(',')]

		l.loadRoot(root, id)

		l.showRoot(root, id)

		print '-' * 50
		if raw_input('Debug values, collections (y/n) ? ')[0] == 'y':
			print 'values\t'*5
			for k,v in l.values.items():
				print '\t',k
				for k2, v2 in v.items():
					print '\t'*2, k2, v2
				
			print	
			print 'collections\t' * 5	
			for k,v in l.collections.items():
				print '\t', k
				for k2, v2 in v.items():
					print '\t'* 2, k2
					for k3, v3 in v2.items():
						print '\t' * 3, k3, v3
							
			print
			print
