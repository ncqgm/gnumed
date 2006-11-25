"""the objective with this tool , is to have a semi-automated document model
constructor, that reads a database's metadata, and also uses a configuration file
to construct a meaningful representation of a document . The document would
also be accompanied by information not specific to the document, but often
included in the document by convention ( e.g. address, vaccine regime).
	The parsing occurs in 3 stages:
		stage 1, the document root is explored from parent->child direction,
		as the document root usually has a one-to-many relationship with
		the document parts.

		stage 2, once stage 1 has gotten most of the document parts,
		some parts are known to have a many-to-many relationship,
		so a many-to-one then one-to-many relationship needs to be retrieved,
		and this is done by trying to extract based on a configuration file
		definition.

		stage 3 , some parts cannot be reached by the above heuristics,
		so an attempt is made to retrieve those parts by specifying a 
		search start node, and then searching both one-to-many and many-to-one
		depth first exhaustively, whilst not including nodes already
		seen in stage 1 and stage 2. The start nodes are specified in the
		configuration file.

	The next stage of the experiment , is to try to write a gui generator
	based on a configuration file that specifies different ui gestures for
	parts of a document schema. 

	Other constructs , include a serializer, deserializer/ merger, 

	an exporter /tranformer , or transformer /importer, 

	non-gui document update action paths , 

	cross document update action paths ( e.g. recalls )


"""


import pyPgSQL.PgSQL as dbapi 
import re
import sys
import traceback as tb
import base64
import binascii
import ConfigParser

""" uncomment the credentials below for local testing.
"""
#credentials = "hherb.com:gnumed:any-doc:any-doc"
#credentials = "127.0.0.1::gnumedtest:gm-dbo:pass"
#credentials = "salaam.homeunix.com::gnumed:any-doc:any-doc"
credentials = "127.0.0.1::gnumed_v3:gm-dbo:gm-dbo"


class schemascan2:

	def __init__( self, creds , config_filenames):
		self.con = dbapi.connect(creds)
		self.cfg = ConfigParser.ConfigParser()
		self.cfg.read(config_filenames)
		self._get_config_parameters()
		self.all_seen = {} 

	def _get_config_parameters(self):
		self.no_follow_parents =[x.strip() for x in self.cfg.get("exclude parent_child", "parents").split(',')]
		self.follow_child_parents =[x.strip() for x in self.cfg.get("include child_parent", "childs").split(',')]
		self.other_roots =[x.strip() for x in self.cfg.get("include other_document_roots", "other_roots").split(',')]

		self.primary_root = self.cfg.get('primary root', 'root').strip()

		self.no_parent_child = [ (x[0].strip(),x[1].strip()) for x in [y.split('/') for y in [z for z in self.cfg.get("exclude parent_child_paths","paths").split(",")]] ]

		self.search_path = self.cfg.get('schema config', 'search_path')

		self.type_col = int( self.cfg.get('metadata config', 'dbapi_attrtype_col') )
		self.desc_col = int( self.cfg.get('metadata config', 'dbapi_attrname_col') )
		self.type_mapping = dict( [ (int(y[0].strip()), y[1].strip())  for y in [ x.split('/') for x in self.cfg.get('metadata config', 'attrtype_mapping').split(',')] ] )

	def get_attributes(self, table):
		cu = self.con.cursor()
		cu.execute('set search_path to ' + self.search_path)
		cu.execute("select * from %s limit 1" % table)
		cu.fetchone()

		l = {}
		for x in cu.description:
			l[x[self.desc_col]] = self.type_mapping[ x[self.type_col] ]
		return l


	def show_fk_details(self):
		for child, refering_col , parent, parent_pk in self.get_fk_details():
			print child, refering_col , "->", parent, parent_pk



	def get_fk_details(self ):
		"""gets table, keying attribute, 
		{pointing to}  foreign table, foreign key attr { foreign table primary key }
		   this only works for single attribute foreign keys , not multiple attribute 
		
		details:
			pg_class has relname, relfilenode
			pg_attribute  has attrelid ( references relfilenode), attname, attnum

			pg_constraint has   conrelid, conkey, confrelid,  confkey  
				( 
				where relid refers to pg_class.relfilenode, and key refers to 
				pg_attribute.attnum 
				)
				
				Note that the 'f' means this is the 'father' or the parent
				table, and the many children point to it.

				or - it is the foreign table, which is pointed to by
				the table *having* the foreign key. confkey is actually
				the primary key of the foreign table


		"""

		cu = self.con.cursor()
		cu.execute( """
		select 
		       c1.relname, a1.attname, 
		       c2.relname, a2.attname 
		from pg_class c1, pg_class c2, 
			pg_constraint con , 
		     pg_attribute a1, pg_attribute a2 
		where 
			c1.relfilenode = con.conrelid 
		and 	c2.relfilenode = con.confrelid 
		and 	con.contype='f' 
		and 	con.conrelid = a1.attrelid 
		and 	con.conkey[1] = a1.attnum    
		and 	con.confkey[1] = a2.attnum 
		and     con.confrelid = a2.attrelid
			""")
		r = cu.fetchall()
		return r
		
	def build_parent_child_list( self, root = None):
		"""returns a ordered list of : 
			node, { 'pk': pk of node, 
				'child_fks': a list of (child,fk) pointing to node
				}
		"""
		self.all_seen = {}
		root = root or self.primary_root
		pc_list = []
		process_q = [root]
		

		childparents = self.get_fk_details()
		
		parent_child = {}

		for child, fk, parent, pk in childparents:
			if not parent_child.has_key(parent):
				parent_child[parent] = { 'pk': pk, 'child_fks': [] }

			parent_child[parent]['child_fks'].append( (child, fk) )
		while process_q <> []:
			node = process_q.pop()
			if self.all_seen.has_key(node):
				continue
			self.all_seen[node] = 1

			if node in self.no_follow_parents:
				continue

			pk_children_fks = parent_child.get(node, None)
			if not pk_children_fks:
				continue

			# process path exclusions
			l = []
			for child, fk in pk_children_fks['child_fks']:
				if (node,child) in self.no_parent_child:
					continue
				l.append( (child, fk ))
			pk_children_fks['child_fks'] = l

			pc_list.append( ( node, pk_children_fks) )
			process_q.reverse()
			process_q.extend(  [child for (child, fk) in pk_children_fks['child_fks']] )
			process_q.reverse()

		return pc_list

	def get_child_filters(self):
		"""get back a follow list, from child to parent, for child tables named "lnk*" """
		
		def child_filter_lnk_prefix( child):
			return child[:3] == 'lnk'
	
		def child_filter_application_special( child):
			return child  in self.follow_child_parents

		
		filters =  [ 	child_filter_lnk_prefix, 
				child_filter_application_special
				
				]
		
		return filters


	def do_filter_follow_link_tables( self, parent_child_list, child_filters):

		childparents = self.get_fk_details()
		
		child_to_parents = {}
		for child, fk, parent, pk in childparents:
			if not child_to_parents.has_key(child):
				child_to_parents[child] = { }
			child_to_parents[child][parent] = { 'child_key': fk, 'parent_pk': pk }

		follow_list = []
		for node, pk_child_fks_map in parent_child_list:
			for child, fk in pk_child_fks_map['child_fks']:
				#print child[:3], '= lnk ?'
				is_included = False
				for filter in child_filters:
					is_included |= filter(child)

				if is_included:
					print "following ", child
					parents_dict = child_to_parents.get(child, {})
					#print "parents_dict", parents_dict
					child_follow_list = []
					node_referred = False
					for parent, keymap in parents_dict.items():
						if parent == node and not node_referred:
							node_referred= True
							continue

						child_follow_list.append( ( parent, keymap ) )
					follow_list.append( (node, child, child_follow_list) )
					
					self.all_seen[child] = 1
					for parent, kmap in child_follow_list:
						self.all_seen[parent] = 1
					
		return follow_list
		"""
			this is ( child, [ (parent, { 'child_key': , 'parent_pk': } ), ... ] )
		"""

	def follow_both_directions(self, node_q ):
		from_child = {}
		from_parent = {}
		for child, fk, parent, pk in self.get_fk_details():
			if not from_parent.has_key(parent) :
				from_parent[parent] = {}
			if not from_child.has_key(child):
				from_child[child] = {}
			from_parent[parent][child] = { 'pk' : pk, 'child_fk': fk }
			from_child[child][parent] = { 'pk': pk, 'child_fk': fk }
	
		orig_node_q = node_q
		follow_list = []
		while node_q <> []:
			outlist = []
			node = node_q.pop()
			if from_parent.has_key(node):
				for child, keys in from_parent[node].items():

					if child in orig_node_q or child in self.all_seen:
						continue
					self.all_seen[child] = 1
					outlist.append( {  'dir': '<-', 'to': child, 'pk': keys['pk'], 'child_fk': keys['child_fk'] } )
					node_q.append(child)

			if from_child.has_key(node):
				for parent, keys in from_child[node].items():
					if parent in orig_node_q or parent in self.all_seen:
						continue
					self.all_seen[parent] = 1
					outlist.append( { 'dir': '->', 'to': parent, 'pk': keys['pk'], 'child_fk': keys['child_fk'] } )
					node_q.append(parent)
					
			self.all_seen[node]=1
			follow_list.append((node, outlist))
		return follow_list

	def follow_other ( self):
		#print "FOLLOW OTHER ", self.other_roots
		l = []
		l.extend(self.other_roots)
		return self.follow_both_directions(l)

	def show_parent_child_list(self, parent_child_list = None):
		"""demonstrates the structure of parent_child_list """
		if not parent_child_list: 
			parent_child_list = self.build_parent_child_list()
		
		for node, pk_child_fks_map in parent_child_list:
			print node, '.', pk_child_fks_map['pk']
			for child, fk in pk_child_fks_map['child_fks']:
				print "\t", child, '.', fk
			print


	def get_compact_relax_ng(self):
		parent_child_list = self.build_parent_child_list( )

		follow_list = self.do_filter_follow_link_tables ( 
				parent_child_list, 
				s.get_child_filters() 
				)

			
		#print "DEBUG", parent_child_list

		lines = [ "grammar { ", "start = " + self.primary_root.capitalize() ]
		type_map = {}
		order = []
		for node , pk_child_fks_map in parent_child_list:
			pre =  node.capitalize() + " = element "+ node + " { "
			pk = "\telement " + pk_child_fks_map['pk'] + " { xsd:integer }"
			
			
			elems = []
			for child , fk in pk_child_fks_map['child_fks']:
				elem = "\t\t" +child.capitalize() + "*"
				elems.append( elem)
			
			
			x = type_map.get(node, [])
			if x == []:
				x.append(pre)
				order.append(node)

			#x.append(pk)
			x.extend(elems)
			type_map[node] = x
			
			for child, fk in pk_child_fks_map['child_fks']:
				child_pre = child.capitalize() + " = element " + child + " { "
				child_fk = "\t\telement " + fk + " " + "{ xsd:integer}"
				child_fk_name = "\t\telement "+fk+"_keyname "+ "{ ChildKey }"
				x = type_map.get(child,[])
				if x == []:
					x.append( child_pre)
					order.append(child)
		
				x.extend ( [ child_fk, child_fk_name ] )
				
				type_map[child] = x

		for orig_parent, child, referenced_keymap_list in follow_list:
			# orig_parent -> child -> referenced
			for referenced , keymap in referenced_keymap_list:

				referenced_line  = '\t\t' + referenced.capitalize() 
			
				type_map[child].append ( referenced_line)
				
				x = type_map.get(referenced, [] )
				if x == []:
					defn = referenced.capitalize() + " = element " + \
							referenced + " { "
					x.append(defn)
					order.append(referenced)

				type_map[referenced] = x


		for node, follow_list in self.follow_other():
			#print "checking ", node
			for map in follow_list:

				if map['dir'] == '<-':
					suffix = '*'
				else:
					suffix = ''
				node2 = map['to']
				#print "DEBUG node", node, "node2",node
				x = type_map.get(node2,[])
				if x == []:
					defn = node2.capitalize() + "= element " + node2 + " {"
					x.append(defn)
					order.append(node2)
				type_map[node2] = x

				x = type_map.get(node,[])
				if x == []:
					defn = node.capitalize() + "=element " + node + " { "
					x.append(defn)
					order.append(node)
				x.append ( '\t\t' + node2.capitalize() + suffix )
				type_map[node] = x	

		print "\nDEBUG\n"

		#for node in order:
		#	print
		#	print node
		#	print self.get_attributes(node)
		
		#print


		for node in order:
			attrmap = self.get_attributes(node)
			x = type_map[node]
			for attr,typename in attrmap.items():
				#print "DEBUG", node, attr, typename
				if attr[:3] <> 'fk_':
					x.append('\t\telement '+attr+' { '+typename +'} ' )

		for node in order:	
			lines.extend( type_map[node] + ["}\n"] )
		
		return "\n\t".join(lines) + "\n}"	
		

		
		



if __name__ == "__main__":
	accept = 'n'
	while accept[:1] is 'N' or accept [:1] is 'n':
		print "credentials are ", credentials
		accept = raw_input("accept ? ")
		if accept[:1] in ['N', 'n']:
			new_creds = raw_input (" enter new credentials :")
			if new_creds:
				credentials = new_creds

	
	s = schemascan2(credentials, 'schemascan2_gnumed.cfg')
	s.show_fk_details()

	parent_child_list = s.build_parent_child_list( )

	s.show_parent_child_list( parent_child_list )

	
	follow_list = s.do_filter_follow_link_tables ( parent_child_list, s.get_child_filters() )

	print "following lnk_* tables "

	for orig_parent, child, parent_keymap_list in follow_list:
		print orig_parent , "has" ,child
		for referenced, keymap in parent_keymap_list:
			print "\t", keymap['child_key'], " -> ", referenced, ".", keymap['parent_pk']

		print

	for node, follow_list in s.follow_other():
		print "FOLLOWING OTHER ROOTS"

		print node
		for map in follow_list:
			print '\t', map['dir'] , map['to'], "fk=",map['child_fk'], "pk=", map['pk'] 

	print s.get_compact_relax_ng()


