import pgdb
import re



class SchemaParser:


	
	def __init__(self, config):
		self.config = config
		self.build()
		
	

	def get_inherits(self):

		c = pgdb.connect("localhost:gnumed")
		cu = c.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_inherits c3
		where c3.inhrelid = c1.relfilenode and c3.inhparent = c2.relfilenode""")
		return cu.fetchall()

	def get_fk_list(self):
		"""get a foreign key list from pg_constraint"""
		c = pgdb.connect("localhost:gnumed")
		cu = c.cursor()
		cu.execute("""
		select c1.relname, c2.relname from pg_class c1, pg_class c2, pg_constraint c3 where c1.relfilenode = c3.conrelid and c2.relfilenode = c3.confrelid and c3.contype='f'""")
		r = cu.fetchall()
		return r


	def build(self):
		"""builds the from tables listed in self.config.roots, by 
		searching the foreign key constraints in pg_constraint, breadth first.
		e.g. find all tables that have foreign keys to identity, or identity has 
		foreign keys to . if not already in next level list of nodes,
		then add to the next level list of nodes. Then step through the list 
		and apply recursively the above steps.
		This is done in  self.build_levels(list)
		Each node's next level of nodes are stored in a map:
				self.next_level_map[node]=[next level nodes]
		
		The next step is to proceed from the root ( e.g. identity) node again,
		using self.next_level_map , and recursively build a heirarchical
		map using get_model(node) and then calling get_model recursively
		on the node's next level nodes, visiting any node not already visited.

		"""
		self.create_regex()
		#self.create_alias_sets()
		self.fks = self.get_fk_list()
		self.model = {}
		self.next_level_maps = {}
		for x in self.config.roots:
			self.visited = []
			self.target = x
			#self.next_level_maps[x] = {}
			self.next_level_map = {} #self.next_level_maps[x]
			self.build_levels([x])
			self.model[x] = self.get_model(x)
		
	
		for k, v in self.model.items():
			print "root object = ", k
			print "structure is :"
			print
			print k
			self.print_map( v, 1)
			

			print
			print

	def print_map(self, m , indent):
		for k, v in m.items():
			print '  ' * indent, k
			self.print_map( v, indent+1)
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
		for x in l:
			if x in self.visited:
				continue
			if m.has_key(x):
				m[x].update(self.get_model(x))
			else:
				m[x] = self.get_model(x)
		
		#print "\t\tmap is ", m
		return  m	


	def build_levels( self, node_list):
		if node_list is []:
			return
		next_level = []
		for x in node_list:
			if self.is_suppressed('', x) and x <> self.target:
				continue
			if x in self.next_level_map.keys():
				continue

			if self.is_type_table(x):
				continue


			next_level_for_x = self.find_next_level_nodes(x)
			self.next_level_map[x] = next_level_for_x
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
		inherits = self.get_inherits()
		for t, parent in inherits:
			if node == parent and not self.next_level_map.has_key(t):
				l.append(t)

		
		for t1, t2 in self.fks:
			if node == t2 and not self.is_suppressed(node, t1):#and not self.next_level_map.has_key(t1):
				l.append(t1)
				
			elif node == t1 and not self.is_suppressed(node, t2) and not self.next_level_map.has_key(t2):
				l.append(t2)

		
				
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
		return 0

	def is_type_table(self, t):
		for r in self.regex_type_tables:
			if r.match(t):
				return 1
		return 0
	
		
				
class Config:
	def __init__(self, lines):
		self.external_fk = {}
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
					
			
			
			
	def __str__(self):
		l = [ "Configuration is : ",
		"\troots are " + str(self.roots),
				
		#"\thide tables are "+ str(self.hidden),
		
		"\texternal foreign keys are (key = referrer)"+ str(self.external_fk),
		
		"\tlink tables are"+ str(self.link_tables),
		
		"\ttype tables are" + str(self.type_tables)
		]
		return '\n'.join(l)

if __name__ == '__main__':
	config = """
roots:	identity, org, xlnk_identity, form_instances, vacc_def
#hide:	xlnk_identity
external_fk:	xlnk_identity.xfk_identity references identity
link_tables:	lnk.*
type_tables:	^.*enum.*,^.*type., ^.*category, occupation, marital_status, staff_role
suppress:	xlnk_identity.last_act_episode, xlnk_identity.vaccination, xlnk_identity.clin_episode.last_act_episode, xlnk_identity.clin_root_item.clin_episode, identity..org, vacc_def..xlnk_identity

"""
	l = config.split("\n")
	configObject = Config(l)
	#print configObject
	s = SchemaParser(configObject)
	

