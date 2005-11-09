import pgdb
import re
import sys


credentials = "hherb.com:gnumed:any-doc:any-doc"

""" uncomment the credentials below for local testing.
this is meant to sit on a server object, either local machine or LAN. 
and will take a long time across the internet. 
The values in self.model, self.values, self.collections, self.refs
need to be packed up and serialized by a server for sending to a client.
"""
#credentials = "localhost:gnumed:any-doc:any-doc"

class SchemaParser:
	
	def __init__(self, config):
		self.config = config

		self.global_implied_attrs = ['modified_by', 'modified_when', 'pk_audit', 'row_version']
		self.create_regex()
		#self.create_alias_sets()
		self.model = {}
		self.next_level_maps = {}
		self.type_tables = {} 
		self.parents = {}
		self.global_visited = {}
		self.forms = {}
		self.conn = pgdb.connect(credentials)
		self.fks = self.get_fk_list()
		self.inherits = self.get_inherits()
		self.childParentsMap = self.makeParentLists()
		print "child parent list = ",self.childParentsMap
		self.attr_types = {}

		self.build()
	
	def makeParentLists(self):
		m = {}
		for c, p in self.inherits:
			m[c] = m.get(c, [])
			m[c].append(p)
	
		return m

	def isDirectChild(self, child, parent):
		
		for c, p in self.inherits:
			if  c== child and p == parent:
				return 1
		return 0


	def get_inherits(self):

		cu = self.conn.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_inherits c3
		where c3.inhrelid = c1.relfilenode and c3.inhparent = c2.relfilenode""")
		return cu.fetchall()

	def get_fk_list(self):
		"""get a foreign key list from pg_constraint"""
		cu = self.conn.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_constraint c3 where c1.relfilenode = c3.conrelid and c2.relfilenode = c3.confrelid and c3.contype='f'""")
		r = cu.fetchall()
		return r


	def get_fk_details(self):
		"""gets table, keying attribute, foreign table, foreign key attr"""

		cu = self.conn.cursor()
		cu.execute( """
		select c1.relname,a1.attname, c2.relname, a2.attname from pg_class c1, pg_class c2, pg_constraint c3 , pg_attribute a1, pg_attribute a2 where c1.relfilenode = c3.conrelid and c2.relfilenode = c3.confrelid and c3.contype='f' and c3.conrelid = a1.attrelid and c3.conkey[1] = a1.attnum and c3.confkey[1] = a2.attnum and c3.confrelid = a2.attrelid
			""")
		r = cu.fetchall()
		return r
		

	def get_attributes(self, table, foreign_keys = 0):
		if foreign_keys:
			fk_cmp = ''
		else:
			fk_cmp = 'not'

		cu = self.conn.cursor()
		tables_checked_for_fk = [table] + self.get_ancestors(table)
		clause = """select attname from pg_attribute , pg_class, pg_constraint   where relfilenode = attrelid and relname = '%s' and pg_constraint.conrelid = relfilenode and pg_constraint.contype ='f' and conkey[1] = attnum"""
		l_fk = []
		for x in tables_checked_for_fk:
			l_fk.extend([ x[0] for x in self.execute(clause % x)] )
			
		
	#	cu.execute("""
	#	select attname from pg_attribute a, pg_class c where c.relfilenode = a.attrelid
	#	and c.relname = '%s' and a.attnum > 0
	#	and  a.attnum %s in ( select  pc.conkey[1] from pg_constraint pc where pc.contype='f' and pc.conrelid = c.relfilenode) 
	#	and a.attname not in %s 
	#	""" % (table, fk_cmp, str(tuple( ['modified_by', 'modified_when', 'pk_audit', 'row_version']) )))
	#	r = cu.fetchall()

		l = self.global_implied_attrs + l_fk
		excludes = ', '.join ( [ ''.join(["'",x,"'"]) for x in l ] ) 
		r = self.execute("""
		select attname from pg_attribute a, pg_class c where c.relfilenode = a.attrelid and
		c.relname = '%s' and attnum > 0 and a.attname %s in ( %s ) """ % ( table, fk_cmp, excludes) ) 
		l = [ x[0] for x in r]
		return l

	def get_attribute_type(self, table, attr):
		if not self.attr_types.has_key(table):
			r = self.execute("""
		select attname, typname from pg_type t, pg_attribute a, pg_class c where c.relfilenode = a.attrelid and c.relname = '%s'  and a.atttypid = t.oid
			""" % ( table) )
			self.attr_types[table]  = dict([ (x[0],x[1]) for x in r] )

		return self.attr_types[table].get(attr,'text') 
		
	def get_ancestors( self,  child):
		parents = self.childParentsMap.get(child, [])
		#print "PARENTS=", parents
		ancestors = []
		for x in parents:
			ancestors = parents + self.get_ancestors(x)
		return ancestors

	def execute(self,stmt):
		cu = self.conn.cursor()
		cu.execute(stmt)
		r = cu.fetchall()
		cu.close()
		return r
		
	
	def get_pk_attr( self):
		stmt = """
		select  c.relname, a.attname from pg_attribute a, pg_class c, pg_constraint pc where  a.attrelid = c.relfilenode and pc.contype= 'p' and pc.conrelid = a.attrelid and pc.conkey[1] = a.attnum

		""" 
		cu = self.conn.cursor()
		cu.execute(stmt)
		return cu.fetchall()


	def build(self):
		"""builds the document schema from tables listed in self.config.roots, by 
		searching the foreign key constraints in pg_constraint, breadth first.
		e.g. find all tables that have foreign keys to identity, or identity has 
		foreign keys to . if not already in next level list of nodes,
		then add to the next level list of nodes. Then step through the list 
		and apply recursively the above steps. Only add nodes if they aren't on
		a path being suppressed.
		
		This is done in  self.build_levels(list)
		
		Each node's next level of nodes are stored in a map:
				self.next_level_map[node]=[next level nodes]
		
		The next step is to proceed from the root ( e.g. identity) node again,
		using self.next_level_map , and recursively build a heirarchical
		map using get_model(node) and then calling get_model recursively
		on the node's next level nodes, visiting any node not already visited.

		"""
		for x in self.config.roots:
			self.visited = []
			self.target = x
			#self.next_level_maps[x] = {}
			self.next_level_map = {} #self.next_level_maps[x]
			self.next_up = None
			self.parents[x] = [] 
			self.build_levels([(x,'root')])
			self.model[x] =  self.get_model(x)

			for y in self.visited: self.global_visited[y] = 1
		
	
		for k,  map in self.model.items():
			print "root object = ", k
			print "structure is :"
			print
			print "root", k
			self.print_map(  map, 1)
			
			

			print
			print

		#print self.type_tables
		#print "These tables are not type tables"
		#print  filter( lambda(x): x not in self.type_tables.keys() , self.global_visited.keys() ) 

	#	print 
	#	print "These tables have non-reference/non-structural attributes"
	#	print self.getDomainAttributedTables()

	#	print 
		print "The flattened attributes were:-"

		self.get_forms(1)



	def getDomainAttributedTables(self):
		return filter( lambda(x): x not in self.type_tables.keys() and len(self.get_attributes(x)) > 1 , self.global_visited.keys() )

	def getModelFor(self, k):
		return self.model.get(k, {})

	def getModel(self):
		return self.model


	def print_map(self,  m , indent ):
		items = [(k, tag, map) for  k, (tag, map) in m.items()] 
		def mycmp(x, y):
			return cmp(x[1], y[1])
			
		items.sort( mycmp)
		
		for k, tag,map in items:
			print '  ' * indent,tag, k
			if self.config.show_attrs:
				if self.config.show_attr_direction == 'h':
					print '  ' * indent, '  ', self.get_attributes(k)
				else:
					l = self.get_attributes(k)
					for x in l:
						print '  ' * indent, '\t\t-', x
				print
			
			self.print_map( map, indent+1)
			if indent == 1:
				print

	def get_model(self, node):
		m = {}
		self.visited.append(node)	
		
		if not self.next_level_map.has_key(node):
			return { }	
		l = self.next_level_map[node]
		print "get model for ", node
		print "\t\t is ", l
		for x,tag in l:
			if tag =='-1(2)':
				m[x] = (tag, {})
				continue

			if x in self.visited and not (x in [ node for r,p,node in self.config.double_linked] and self.target in [ r for r,p, node in self.config.double_linked]):
				continue
			
			if m.has_key(x):
				m2 = self.get_model(x)
				m[x]= (tag, m[x][1].update(m2))
			else:
				m[x] = (tag, self.get_model(x))
		
		#print "\t\tmap is ", m
		return  m	


	def build_levels( self, node_list):
		if node_list is []:
			return
		next_level = []
		for x,tag in node_list:
			#print "checking x", x
			if self.is_suppressed('', x) and x <> self.target:
			#	print "suppressing ", x
				continue
			if x in self.next_level_map.keys():
			#	print x, "already in ", self.next_level_map.keys()
				continue

			if self.is_type_table(x):
				self.type_tables[x] = 1
				continue
			#print "searching x", x

			next_level_for_x = self.find_next_level_nodes(x)
			self.next_level_map[x] = next_level_for_x

			for y in next_level_for_x:
				if not self.parents.has_key(y):
					self.parents[y] = [x]
				else:	self.parents[y].append(x)	

			next_level += next_level_for_x
		if next_level == []:
			return
		
		self.build_levels( next_level)
		
		
	def is_suppressed( self,parent, node):
		
		l = self.config.suppress
	#	print "CHECKING is_suppressed", parent ,node
		for (root,aparent, anode) in l:
	#		print "\tagainst ",root, aparent, anode
			if self.target == root and anode == node and (aparent =='' or parent == aparent):
	#			print "\t is suppressed**"
				return 1
		return 0	

	def find_next_level_nodes(self, node):
		l = []
		for t, parent in self.inherits:
			if node == parent and not self.next_level_map.has_key(t):
				l.append((t, "<-") )

		
		repeat_fk = []
		for t1, t2 in self.fks:
			if node == t2 and not self.is_suppressed(node, t1):#and not self.next_level_map.has_key(t1):
				if not self.is_reversed_link(t2,t1):

					l.append( (t1, "-*") )
				else:
					l.append( (t1, '-1') )
				
			elif node == t1 and not self.is_suppressed(node, t2):
				if not self.next_level_map.has_key(t2):
					print "adding link ", self.target, node, t2
					l.append( (t2, "-1") )
				else:
					print "** repeated fk =", t2
					repeat_fk.append(t2)
	
		#if repeat_fk <> []:
		#	print "parent, node,REPEAT FK = ", self.target, node, repeat_fk
		#	print "check against"
		#	for x in self.config.double_linked:
		#		print '\t\t\t', x
		for x in repeat_fk:
			for ( root, referer, referred) in self.config.double_linked:
				if [self.target, node, x] == [ root, referer, referred] and referred  not in self.parents.get(node,[]) :
					print "ALLOWING REPEAT FK", self.target, node, x, " parents of ", node, " are ", self.parents.get(node, [])
					
					l.append((x, '-1(2)') )

		
				
		#print "found next level for ", node , " = ", l		
		return l

	def create_regex(self):
		
		self.regex_link_tables, self.regex_type_tables = [], []
		
		self._create_regex_list( self.regex_link_tables, self.config.link_tables)
		self._create_regex_list( self.regex_type_tables, self.config.type_tables)
		
	def _create_regex_list(self, regex_list , tables):	
		
		for s in tables:
			r = re.compile(s, re.I)
			regex_list.append(r)
			
	def is_link_table(self, k):
		for r in self.regex_link_tables:
			if r.match(k):
				return 1
			else:
				print k, " does not match ", r.pattern
		return 0

	def is_reversed_link(self, parent, node):
		for p, n in self.config.reversed_link:
			if parent == p and n == node:
				return True
		
		return False
		
	def is_type_table(self, t):
		for r in self.regex_type_tables:
			if r.match(t):
				return 1
		return 0


		

	def get_flat_attributes(self, attributes, node,  nodeMap):
		for x in self.get_attributes(node):
				attributes.append( node+'.'+x)

		for k, (tag, map) in nodeMap.items():
			if tag == '-1':
				self.get_flat_attributes( attributes,k ,  map)
			elif tag == '-1(2)':
				attributes.append(k+'.'+self.get_attributes(k)[0])
		
				
			
	def get_forms( self, printForms = 0):
		"""
		the structure of self.form is 
		a map[root] = ( attributes, listOfFormsInRoot)

		Each item  in listOfFormsInRoot , the structure is :-
			( nodeName, 			
			
		"""
		for k in self.config.roots:
			map = self.model[k]
			a = [] 
			self.get_flat_attributes(a, k, map)
			allForms = []
			self.get_collection_forms( allForms, map)
			self.forms[k] = [(k, a +[ allForms]) ]

			if printForms:
				print
				print "-" * 30
				print "Form  ", k  ," is:-"
				self.print_form_list( self.forms[k], 0)
		
		return self.forms

	def print_form_list(self, list, tab):	
		"""list is a list of a pair tuple (x, l) 
		where 	x is nodeName, 
			l is a list of  node.attribute or a list of pair tuple(x,l) as above.
			if l has no node.attribute items, it is a subclass list.
		"""	
		for (k, a) in list:
			print "\t" * tab , "For collection item ", k

			if filter(lambda(x): type(x) <> type([]), a) == []:
				#if a == []:
					print "collection subtypes are:"
			else:	
				print "\t" * tab , "attributes are :"

			for k2 in self.sort_pk_first(a):
				if type(k2) == type([]):
					self.print_form_list(k2, tab+1)
				else:
					print "\t" * (tab + 1), k2
			#self.print_form_list(subList, tab+1)


	def sort_pk_first( self, l):
		def sort_path(k1, k2):
			[t1,a1] = k1.split('.')
			[t2,a2] = k2.split('.')
			aIsId = a1[:2] in ['id', 'pk']
			bIsId = a2[:2] in ['id', 'pk']
			if aIsId and not bIsId:
				return -1
			if not aIsId and bIsId:
				return 1
			
			return cmp(t1,t2) 
	
		#l.sort(sort_path)
		return l

	
		
	def mergeParentAttributes( self, attributes, parent_attrs):
		print "*** Merging parent attributes ", parent_attrs
		for node, x in [z.split('.') for z in parent_attrs]:	
			skip = 0
			for n, a in [y.split('.') for y in attributes]:
				if a == x and self.isDirectChild( n, node):
					skip = 1
			if not skip:
				attributes.append( node+'.'+x)

	
	def get_collection_forms(self, allForms, map, parent_attrs = []):

		for k2, (tag, map2) in map.items():
			if tag == '-*' or tag == '<-':
				a2 = []
				self.get_flat_attributes( a2, k2, map2)

				if tag == '<-':
					self.mergeParentAttributes(a2, parent_attrs)
						#a2.extend( parent_attrs )

				if '<-' in [ tag for k,(tag,m) in map2.items() ]:
					inc_parent_attrs = a2
					a2 = []
				else:
					inc_parent_attrs = []

				forms = []
				self.get_collection_forms(forms , map2, inc_parent_attrs)
				if forms <> []:
					a2.append(forms)
				#print "appending ", k2, (a2, forms)
				allForms.append( (k2, a2 ))
							
				
					
			
	


class Config:
	def __init__(self, lines):
		self.external_fk = {}
		self.double_linked = []
		self.reversed_link = []
		for l in lines:
			#no indentation
			l = l.strip()
			
			#skip empty
			if l == '':
				continue
			#skip comments
			if l[0] == '#':
				continue
			print "parsing ", l	
			name, defn = l.split(':')
			name = name.strip()
			print "checking ", name

			if name == "roots":
				self.roots = [x.strip() for x in defn.split(',')]
			
			elif name == "hide":
				self.hidden = [x.strip() for x in defn.split(',')]

			elif name == "external_fk":
				
				i = 0
				parts = defn.split(' ')
				for x in parts:
					if i == 0:
						x= x.strip()
						if x== '':
							continue
						fktable, fk = [y.strip() for y in x.split(".")]
						i += 1
						
					elif i == 1:
						if not x.strip() == 'references':
							print "Syntax error in ", parts, " expected references "
							return
						i += 1
					elif i == 2:
						table = x.strip()

						self.external_fk[fktable] = { 'fk': fk , 'table': table }
						break
					
			elif name == 'link_tables':
				self.link_tables = [ x.strip() for x in defn.split(',') ]

			elif name == 'type_tables':
				self.type_tables = [ x.strip() for x in defn.split(',') ]

			elif name == 'suppress':
				"""use path suppression to control tree parsing"""
				self.suppress = []
				l = [ x.strip() for x in defn.split(',') ]
				for x in l:
					nodes = x.split('.')
					if len(nodes) == 2:
						root, parent, node = nodes[0], nodes[0], nodes[1]
					elif len(nodes) == 3:
						root, parent, node =  nodes
					else:
						print "error parsing suppression expression ", x
						continue
					print "adding suppression ", root, parent, node
					self.suppress.append( (root, parent, node) )
					
			elif name == 'show_attrs':
				self.show_attrs = int( defn.strip() )
			
			elif name == 'show_attr_direction':
				self.show_attr_direction= defn.strip()

			elif name == 'double_linked':
				l = [ x.strip() for x in defn.split(',') ]
				for y in l:
					self.double_linked.append( [ z.strip() for z in y.split('.') ] )
			elif name == "reversed_link":
				l = [ x.strip() for x in defn.split(',') ]
				for y in l:
					self.reversed_link.append( [ z.strip() for z in y.split('.') ] )
			
	def __str__(self):
		l = [ "Configuration is : ",
		"\troots are " + str(self.roots),
				
		#"\thide tables are "+ str(self.hidden),
		
		"\texternal foreign keys are (key = referrer)"+ str(self.external_fk),
		
		"\tlink tables are"+ str(self.link_tables),
		
		"\ttype tables are" + str(self.type_tables),

		"\tsuppressed paths are (root, direct parent, node) ", str(self.suppress)
		
		]
		return '\n'.join(l)

config = """
roots:	identity, names,  org, xlnk_identity
#roots:, form_instances, vacc_def
#hide:	xlnk_identity
external_fk:	xlnk_identity.xfk_identity references identity
link_tables:	^lnk.*
reversed_link:	xlnk_identity.allergy_state, clin_root_item.lnk_type2item, clin_narrative.clin_diag, clin_narrative.lnk_code2narr

type_tables:	^.*enum.*, ^.*category,  marital_status, staff_role, clin_item_type

suppress:	xlnk_identity.xlnk_identity.referral,  xlnk_identity.xlnk_identity.test_org,xlnk_identity.clin_encounter.clin_root_item,xlnk_identity.test_result, xlnk_identity.lab_request, xlnk_identity.last_act_episode, xlnk_identity.vaccination, xlnk_identity.clin_episode.last_act_episode, xlnk_identity.test_type.test_result,  identity..org,  xlnk_identity.test_org.test_type, xlnk_identity.form_instances.referral,  org.lnk_person_org_address.identity, org.lnk_person_org_address.occupation, identity.comm_channel.lnk_org2comm_channel, org.comm_channel.lnk_identity2comm_chan, identity.occupation.lnk_job2person

double_linked:	xlnk_identity.referral.xlnk_identity, identity.lnk_person2relative.identity, identity.lnk_job2person.occupation, xlnk_identity.lnk_result2lab_req.test_result, 	xlnk_identity.clin_root_item.clin_episode, xlnk_identity.test_result.xlnk_identity, xlnk_identity.lab_request.xlnk_identity

show_attrs:	0
#show_attr_direction:	v
show_attr_direction:	h

"""

if __name__ == '__main__':
	l = config.split("\n")
	configObject = Config(l)


	if len(sys.argv) > 1:
		for x in sys.argv:
			if x == '-showattr':
				configObject.show_attrs = 1
	

	print configObject
	print "*"* 40
	s = SchemaParser(configObject)

	

#=========================================================================
# BUGFIX:
#
# if your pgdb shows this behaviour:
#
#Traceback (most recent call last):
#  File "testschema5.py", line 410, in ?
#    s = SchemaParser(configObject)
#  File "testschema5.py", line 15, in __init__
#    self.build()
#  File "testschema5.py", line 101, in build
#    self.fks = self.get_fk_list()
#  File "testschema5.py", line 32, in get_fk_list
#    cu.execute("""
#  File "/usr/lib/python2.2/site-packages/pgdb.py", line 189, in execute
#    self.executemany(operation, (params,))
#  File "/usr/lib/python2.2/site-packages/pgdb.py", line 221, in executemany
#    desc = typ[1:2]+self.__cache.getdescr(typ[2])
#  File "/usr/lib/python2.2/site-packages/pgdb.py", line 149, in getdescr
#    self.__source.execute(
#_pg.error: ERROR:  column "typprtlen" does not exist
#                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# you need to patch $PYTHONPATH/pgdb.py like this:
#
# - in pgdb.py find the method getdescr()
# - find the line with "typprtlen"
# - replace "typprtlen" with -1
#=========================================================================
