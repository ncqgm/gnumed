
import sys
import re
import string

STATE_OBJECT = 1
STATE_PARSING = 2
STATE_CONTENT = 3

class ddlgen:

	
	

	def	__init__(self, filename):
		self.noPrintObjects=1
		if filename == None:
			self.usage()

		print "opening " , filename
		self.file = open(filename, "r")
		self.state = STATE_OBJECT
		self.stack = []
		self.last_spaces = 0
		self.mainMap = {}
		self.objects = {} 
		self.generation_ordering = []
		
		self.initRegex()
		self.parse()

		self.type_mappings = {"boolean": "boolean", "string": "text", "Long": "integer", "int": "integer", "Date": "timestamp", "float" : "real" }

		self.generate()

	def initRegex(self):
		indent_pat = "(?P<spaces>\s*)(?P<rest>.*)"
		obj_pat = "[\w]*"
		typed_pat = "(?P<attribute>\w+)\s*:\s*(?P<type>[a-zA-Z]+)"
		quoted_pat='\"[\w]*\"'
		restrict_pat = "(?P<attribute>\w+)\s*:\s*(?P<list>("+quoted_pat+"\s*,\s*)*\s*"+quoted_pat+")"

		mapped_pat = "\*\s*(?P<child>"+obj_pat+")\s*\[(?P<mapping>[\w.]*)\s*(?P<ordering>\w*)\]"

		forward_pat = "(forward)\s*(?P<object>"+obj_pat+"$)"
		
		self.re_indent = re.compile(indent_pat)
		self.re_object = re.compile( "^(?P<object>"+obj_pat+")$" )
		self.re_typed = re. compile( typed_pat )
		self.re_restrict = re.compile( restrict_pat)
		self.re_mapped = re. compile ( mapped_pat )

		self.re_forward = re. compile( forward_pat )

		

	def usage(self):
		print """

usage:
	python ddlgen filename

	where filename has syntax

	Class 
		
		string_type_instance
		
		string_type_instance: "choice1", "choice2", "choice3"
		
		simple_type_instance : simple_type
		
		Referenced_Class
		
		*Mapped_Class[Mapped_Class.selection.path  asc]

	
	
	
	Id will always be integer

	references will be generated from Class->Referenced_Class, and from Mapped_Class->Class
	simulating many-to-one, and one-to-many relationships. Intermediate classes must be
	used for many-to-many relationships.


	Output is data-definition in SQL.
	
	Example Script:

	
	RoleType
		Name : "programmer", "student", "analyst", "domain expert"
		
	Role	
		RoleType
		date:Date
		
		
	Names
		lastName
		firstName
	
	Address
		street1
		street2
		urb
		postcode

	Stakeholder
		*Role[Role.RoleType.name desc]
		Names
		DOB: Date
		Address
		
		
"""
		sys.exit(0)


	def parse(self):
		for x in self.file.readlines():
			self.parseNext(x)
			self.printObjects()


	def printObjects(self):
		if self.noPrintObjects:
			return
		print"##  ***** Printing Objects "
		for x in self.objects.keys():
			print x," : ", self.objects[x]
			print "-"* 62


	def parseNext(self, line):
		self.line = line.rstrip()
		if self.line == "":
			return
		self.m = self.re_indent.match(self.line)
		self.spaces = len(self.m.group("spaces"))	
		if (self.state == STATE_OBJECT):
			self.parseObject()

	def getEqual(self, list, object):
		for x in list:
			print x , " compared to " , object
			if x == object:
				return x
		return None

	def parseObject(self):
		object = self.m.group("rest")

		print "content = " , object , "spaces" , self.spaces


		if ( self.spaces == 0):
			match = self.re_forward.match(object)
			if match != None:
				print "forward declaration " + match.group("object")
			#	self.objects[match.group("object")] = {}
			#	self.generation_ordering.append(match.group("object"))
				return

			match =  self.re_object.match(object)
			if match == None:
				print "ERROR expected object : found "+object 
				Sys.exit(0)
			else:
				print "found object = " + object 
				self.objects[object] = { "fk": [] , "attributes" :  {"id": "Long"}  , "restrictions":{} , "child_ordering": {} , "primary_key": "id" }
				self.last_object = object
				object = match.group("object")
				self.generation_ordering.append(object)
		
			return

		if (self.spaces == 1):
			match = self.re_object.match(object)
			if match != None:
				if  self.objects.has_key(object) :
					print "  *found foreign key " + object
					self.objects[self.last_object]["fk"].append(object)
				else:
					print " found string type " + object
					self.objects[self.last_object]["attributes"][ object] = "string" 
				return
			
			match = self.re_typed.match(object)
			if match != None:
				print " found " + match.group("type") + " type  = " + match.group("attribute")
				self.objects[self.last_object]["attributes"][ match.group("attribute")]= match.group("type") 
				return
			match = self.re_restrict.match(object)
			if match != None:
				print " found " + match.group("attribute") + " of restriction " + match.group("list")
				self.objects[self.last_object]["attributes"][ match.group("attribute")] = "string"
				self.objects[self.last_object]["restrictions"][match.group("attribute")]=match.group("list")
			match = self.re_mapped.match(object)
			if match != None:
				print " found mapped type " + object
				print " putting foreign key in mapped child = " + match.group("child")
				self.objects[match.group("child")]["fk"].append(self.last_object)
				self.objects[self.last_object]["child_ordering"][match.group("child")]= { "path": match.group("mapping") , "order":match.group("ordering") }




	def check_dependencies(self):
		wt = 1
		for x in self.objects.keys():
			self.objects[x]["weight"] = wt
			wt = wt + 1
		for i in xrange(0, 4):#len(self.objects) / 4):		
			for x in self.objects.keys():
				for f in self.objects[x]["fk"]:
					self.objects[x]["weight"] += self.objects[f]["weight"]
		
		map = {}

		for x in self.objects.keys():
			map[self.objects[x]["weight"]] = x 

		list= []
		list.extend( map.keys() )
		list.sort()

		self.generation_ordering = []
		for y in list:
			print map[y], " has weight ", y
			self.generation_ordering.append(map[y])
			
			



	def generate(self):

		scripts = {}
		list = []
		list.extend(self.generation_ordering)
		for oname in list:
			lines = []	
			self.generate_table_definition( lines, oname);
			print "****  Generated table ", oname
			scripts[oname]=lines

		print "scripts ="
		for x in self.objects.keys():
			print x, scripts[x]

		self.check_dependencies()

			
		print "generation will proceed in " , self.generation_ordering
		f = open("ddl.sql", "w")
		for oname in self.generation_ordering:
			lines = scripts[oname]
			for x in lines:
				f.write(x)
				f.write('\n')
				print x;

		f.close()

			
	
	def generate_table_definition(self, lines,  tablename):
		attributes = self.objects[tablename]["attributes"]
		primary_key = self.objects[tablename]["primary_key"]
		foreign_keys = self.objects[tablename]["fk"]
		sequence = "%s_%s_seq" % ( tablename, primary_key)
		lines.append("drop sequence %s;" % sequence)
		lines.append("CREATE SEQUENCE %s;" % sequence );

		lines.append("drop TABLE %s cascade;" % tablename);
		lines.append("CREATE TABLE %s  (" % tablename);
		first = 1
		lastname = attributes.keys()[-1]
		for name in attributes.keys():
			line = []
			
				
			line.append(  name );
			line.append(" ");
			line.append( self.type_mappings[attributes[name]] );
			if name == primary_key:
				line.append(" ");
				line.append(" primary key default nextval('%s_%s_seq') not null" % (tablename, primary_key) );
		
			if name != lastname:
				line.append(", ")
		
			lines.append( string.join(line) )
			
			
		for f in foreign_keys:
			lines.append(",")

			line = []
			line.append(f.lower())
			line.append(" integer references ")
			line.append(f)
			line.append(" on delete cascade")
			lines.append( "".join(line) )

		
		
		lines.append(");")
		lines.append("");


			

		


				

	



if __name__ == "__main__":
	if (len(sys.argv) == 1):
		ddlgen(None)
	gen  = ddlgen( sys.argv[1])






