"""this script analyses sql scripts, and creates xmlrpc create, update, delete, select functions served 
from one server at _port on the localhost. It also does a partial relational graph , with a view for 
automated generation of navigatable user interfaces .
	USAGE:
		python analyse_sql3.py  filename  > server.py    
	
		where filename is  the sql file to analyse e.g. gmclinical.sql
		server.py will contain the server code . Note some output is directed to stderr as part
		of feedback for debugging.
		
		
"""

import string
import sys

import re


stack = []
_port = 9000
_dns = "::gnumed"

from getopt import *
optlist,remaining_args = getopt( sys.argv[1:], "hp:c:")
for (opt, value) in optlist:
	sys.stderr.write( "option %s=%s\n" % (opt, value))
	if opt == '-h':
		print """
	USAGE:
		python analyse_sql3.py  -p port -c connect_string  filename  > server.py    

		where 
			port : the port number for the xmlrpc server (default is 9000)
			
			connect_string: the string used for database connection (default '::gnumed')
			
			filename :  the sql file or path to file: e.g ../sql/gmclinical.sql

		output is to stdout so in the above example
		server.py will contain the server code . 
		Note some output is directed to stderr as part
		of feedback for debugging.

		EXAMPLE:
			python2.2 analyse_sql3.py  -p9001 -c'localhost::gnumed' ../sql/gmdrugs.sql
		
		"""
		sys.exit(0)
	if opt == '-p':
		_port = int(value)
		sys.stderr.write("*** server port set to %d\n" % _port)
	
	if opt == '-c':
		_dns = value
	


"do some processing on the line. Accumulate results in state variables."
def process_complex( line):
	#print "looking at "
	#print line
	prog = re.compile(".*create\s+table\s+(?P<tablename>\w+)\s*\(.*(\w+\s+references\s+\w+)+.*", re.M | re.I | re.S)
	x =  prog.match(line)
	if (x <> None):
		sys.stderr.write(x.string )
                sys.stderr.write('\n')
	return x	

def process_simple( line):
	prog = re.compile(".*create\s+table\s+(?P<tablename>\w+)\s*\(.*(?!\w+\s+references\s+\w+).*", re.M | re.I | re.S)
        x =  prog.match(line)
        if (x <> None):
                sys.stderr.write(x.string)
                sys.stderr.write('\n')
        return x


def get_table_complexity_lists(re_objects):
	print "#simple tables"
	simple = []
	complex = []
	for x in re_objects:
		if ( x.lastindex == 1):
			print '#', x.group('tablename') 
			simple.append(x)
		else:
			complex.append(x)
		
	print "\n\n#complex tables"
	for x in complex:
			print '#', x.group('tablename') 
		

	return simple, complex			
			
""" This takes a list of MatchObjects created by re , which represent simple table creation sql expression
    It parses out the primary key and the likely user data fields.
    returns a  map of tablename and list of a primary key and a list of data fields.
"""    
def guess_simple_struct(simple):
	prog = re.compile("\s*(?P<fieldname>\w+)\s*(varchar|text|intege|float)+.*", re.I)
	prog2 = re.compile("\s*(?P<fieldname>\w+)\s*(serial|(.*\s*primary key))+.*", re.I)
	data_map = {}
	for x in simple:
		print "\n\n#looking at table ", x.group('tablename')
		lines = x.string.split("\n")
		
	##-------  Initialize data sinks
		edit_fields= []
		primary_key = None
		
		for y in lines:
			z = prog.match(y)
			if (z <> None):
				print "#User Data Line is (?) ", z.string
				edit_fields.append(z.group('fieldname'))
			else:
				z = prog2.match(y)
				if (z <> None):
					print "#a primary key (?) is ", z.string
					primary_key = z.group('fieldname')
					
	
		if len ( edit_fields) > 0 :
			data_map[x.group('tablename')] = [ primary_key, edit_fields]
		
	return data_map

def suggest_simple_ui( struct_map):
	for k,v in struct_map.items():
		#print "\n\n#have a server class which relates to table ", k, " and each tuple object can be identified by sql field ", v[0]
		#print "#the server tuple objects have editable fields :"
		for x in v[1]:
			sys.stderr.write( "\t#%s\n"% (x) )  

def insert_lists ( list, table, other):	
	new_list = []
	for x in list:
		if x[-1] == table:
			x.append(other)
		new_list.append(x)
	return new_list	
			

def get_links(  re_obj,   other):
	sys.stderr.write( " ".join ( ("\n","from table ", other , "\n") ) ) 
	prog = re.compile(".*references\s+(?P<table>\w+)\s*.*", re.I)
	lines = re_obj.string.split("\n")

	list = []
	for x in lines:
		z = prog.match(x)
		if z <> None:
			sys.stderr.write("".join( ("from '", z.string, "'\n") ) )
			table = z.group('table')
			sys.stderr.write( "referenced table = " +  table )
			sys.stderr.write("\n")
			list.append( [  other, table])
	return list			

# the default rule is to not include enum_.. tables as a dependency labelling table.

rules = [  lambda rel: re.match( 'enum.*', rel[-1]) ]

def get_rules():
	return rules

def set_rules(r):
	rules = r
		
def is_non_candidate_relation( relation ):
	for r in rules:
		if r(relation):
			return 1
	return 0	

def get_no_dependencies(dependencies):
	""" dependencies is a list of relation list pairs where (a,b) means a depends on b."""
	candidates = []
	dependants = []

	
	for x in dependencies:
		if  is_non_candidate_relation(x):
			continue
		if not x[-1] in candidates:
			candidates.append(x[-1])
		if not x[0] in dependants:	
			dependants.append(x[0])

	no_dependencies = []	
	no_dependencies.extend( candidates)
	for x in dependants:
		if x in no_dependencies:
			no_dependencies.remove( x )
	
	return no_dependencies

def count_dependants( no_dependencies, relations):
	count = {}
	for x in no_dependencies:
		count[x] = []

	for r in relations:
		if r[-1] in no_dependencies:
			count[r[-1]].append( r[0] )
	return count

def get_reference_map( complex):
	list = []
	#for x in complex:
	#	list.append ( [x.group('tablename')] )
	for x in complex:
		table = x.group('tablename')
		list += get_links( x, table )
		
	print "#dependencies = \n#",list	
	
	no_dependencies = get_no_dependencies(list)

	print "\n\n#These tables have no complex dependencies:\n#", no_dependencies

	counts = count_dependants(no_dependencies, list)

	for k,v in counts.items():
		print "# ", k, " has ", len(v) , "dependants, which are", v

		
def gen_xmlrpc_server_handler_base( ):
	print "from  SimpleXMLRPCServer import *"
	print "from pyPgSQL.PgSQL import *"


	print "class ExportFunc:"
	print"""
		def __init__(self, database_name_str):
			self.conn = None
			self.dns = database_name_str

		def _get_conn(self):
			if self.conn == None:
				self.conn = connect( self.dns)
			return self.conn
	    	
			   
		def _close_conn(self):
			if self.conn <> None:
				self.conn.close()
				self.conn = None
		
		def _execute_cmd( self, cmd):
		    conn = self._get_conn()
		    cursor = conn.cursor()
		    cursor.execute(cmd)
		    return cursor	

	
		def _do_query( self, query, offset = 0, length = 100 ):
			cmd = '%s LIMIT %s OFFSET %d' % ( query, length, offset)
			cursor = self._execute_cmd( cmd)
			return cursor.fetchall()

		def get_description(self,  tablename):
			cmd = "select * from "+tablename+" where false"
			conn = self._get_conn()
			cursor = conn.cursor()
			cursor.execute(cmd)
			d  =  cursor.description
			l = []
			for x in d:
				l.append( [x[0], x[1]])
			return l
			
		
		def _do_update( self, cmd):
		    print "before _do_update ", cmd	
	    	    cursor = self._execute_cmd(cmd)   	
		    cursor.execute("commit")
		    self._close_conn()

	   """ 
		
		

		


def print_insert_statement(  tablename, primary_key, data_fields):
	print  string.join( ("\tdef create_" + tablename," (self, ", ",".join(data_fields), "):"))
	l = []
	for x in data_fields:
		if type(x) == type("s"):
			l.append( "'%s'")
		else:
			l.append( "%s")
	s = ", ".join(l)
	
	print '\t\tcmd =  """insert into ', tablename , '( ', ',' .join( data_fields) ,") values (%s) " % (s) , '""" % (' , ','.join(data_fields), ')'
	print '\t\tself._do_update(cmd)'
	print '\t\treturn ""'
	print '\n\n'

def print_select_all( tablename):
	print """
	def select_all_"""+tablename+ """( self, start = 0, limit = 200 ):
		cmd = "select * from """,tablename,""""
		result = self._do_query(  cmd, start, limit)
		return result
	"""

def print_select_statement_begins_with( tablename ):
	print  string.join( ("\tdef select_start_" + tablename," (self, field_name, field_value, start = 0, limit = 100 ) :") )
	print '\t\tcmd = """ '
	print '\t\tselect * from ', tablename, " where strpos( $s, '$s') == 1 '$", " ( field_name, field_value)", '"""';

	print '\t\tresult = self._do_query( cmd, start, limit)'

	print '\t\treturn result'

def print_select_by_pk( tablename, pk):
	print 
	print "\tdef select_by_pk_%s( self, pk_val):"%(tablename)
	print "\t\tcmd = ", "'select * from %s where %s"%(tablename, pk) , "= %s'%(pk_val)"
	print """
		result = self._do_query(cmd, 0, 'ALL')
		return result
	"""
		 

def print_update_statement(tablename, primary_key, data_fields):
	print
	print "\tdef update_%s(self, pk_val, map_fields):" % (tablename)
	print """
		list = []
		for k,v in map_fields:
			if (v.type == 'n'):
				list.append( "set %s = %s" % ( k, v) )
			else:
				list.append( "set %s = '%s'" % ( k, v) )


		s = ",".join(list)	
		cmd = "update """, tablename,""" %s where """,  primary_key,""" = pk_val" % s """
	print """
		self._do_update( cmd)
		return ""
	 	"""

def print_delete_by_pk( tablename, primary_key):
	print
	print "\tdef delete_%s(self, pk_val):" % ( tablename)
	print "\t\tcmd = 'delete from %s where %s = pk_val' " % ( tablename, primary_key)
	print "\t\tself._do_update(cmd)"
	print '\t\treturn ""'

def print_describe_fields(tablename):
	print """
	def describe_fields_"""+tablename+"""(self):
		d =  self.get_description( '"""+tablename+"""')
		print "returning ", d
		return d
	"""
		
def print_notify_change( tablename, primary_key ):
	
	print"""	
	def notify_change_""" + tablename + """ ( self, frontend, changes) :
		for k in changes.keys():
			if ( self.changes.has_key[k]):
				# check for possible conflict
				if (self.changes[k].frontend <> frontend):
					#a front end is making a change before a previous change
					# by a different front end has been propogated to all front ends.
					print "*** possible lost update"
					print "earlier update by ", self.changes[k].frontend, " overwritten by ", frontend, " on object ", changes[k]
			self.changes[k].change = changes[k]
			self.changes[k].timestamp = self.server_timestamp
			self.changes[k].frontend = frontend
		
	

		

	def _get_changes_later_than(self, timestamp):
		changes = {}
		for k,v in self.changes:
			pass
		

	def poll_changed( self, frontend,  frontend_timestamp) :	
		"Timestamping and update by client polling: every change in 
	an object at the server is associated with a single server timestamp 
	which increases	incrementally. 
			Every time a client polls and retrieves an update, it
	gets back all changes which have timestamps later than it's last 
	retrieved timestamp. The client then is given back these changes and
	the latest server timestamp. The server updates its local record of
	the client's timestamp to the latest timestamp. 
						The server also finds the
	minimum timestamp in the clients' timestamp record. If there are 
	any changes that are earlier than the minimum timestamp, then they
	are removed from the server cache of changes, as these changes 
	should have been propogated to all clients. "	
 		
		later_changes = self._get_changes_later_than(frontend_timestamp)

		frontend_timestamp = self.server_timestamp + 1

		self._update_frontend_timestamps( frontend, frontend_timestamp)

		earliest = self._get_earliest_frontend_timestamp()

		self._remove_changes_earlier_than( earliest)

		return [ frontend_timestamp, later_changes]	

	"""	

	
def print_start_server( tablename, host = 'localhost', dns ='::gnumed', port = 9000):
	print "server = SimpleXMLRPCServer( ('%s' , %d))"%(host, port)
	print "impl = %s_server( '%s')" % ( tablename, dns)
	print "server.register_instance(impl)"
	print "server.serve_forever()"


def gen_xmlrpc_server_class( name ):
	print "\nclass "+name+"_server( ExportFunc):"
	print "\tdef __init__(self, dns):"
	print "\t\tExportFunc.__init__(self, dns)"

def gen_xmlrpc_server_func( tablename, primary_key, data_fields):
	print_insert_statement( tablename, primary_key, data_fields)
	print_select_statement_begins_with( tablename )
	print_select_by_pk( tablename, primary_key)
	print_select_all(tablename)
	print_update_statement(tablename, primary_key, data_fields)
	print_delete_by_pk( tablename, primary_key)
	print_describe_fields(tablename)

def gen_xmlrpc_server_main( name, host , dns ,  port ):
	print_start_server( name, host, dns, port )
	

def gen_simple_servers( struct_map):
	name = "simple_tables"
	gen_xmlrpc_server_handler_base()
	gen_xmlrpc_server_class(name)
	for k,v in struct_map.items():
		gen_xmlrpc_server_func( k, v[0], v[1] )
	gen_xmlrpc_server_main(name,host = 'localhost',  dns = _dns,  port = _port)	


lines=[]
import fileinput

for line in fileinput.input(remaining_args):
	lines.append(line)

print """#Create one large string from string lines from fileinput."""
all_lines = "".join(lines)
statements = string.split(all_lines, ";")

#for x indd statements:
#	print "STATEMENT\n",x.strip()

re_obj_table_statements = []
for x in statements:
	x = x.strip()
	y = process_complex(x)
	if (y == None):
		y = process_simple(x)

	if (y <> None):
		re_obj_table_statements.append(y)

simple,complex = get_table_complexity_lists(re_obj_table_statements)		

#  process simple database into xmlrpc server.

struct_map = guess_simple_struct( simple)		
suggest_simple_ui( struct_map)
complex_structmap = guess_simple_struct(complex)
for k,v in complex_structmap.items() :
	struct_map [k] = v
gen_simple_servers(struct_map)
print"#\n\n"

# process the complex databases

get_reference_map( complex)
