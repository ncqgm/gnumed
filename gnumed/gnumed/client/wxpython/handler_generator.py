	 	

import fileinput
import re

import string
import sys, os


class generator:
	"""generates a empty event hooking class something like borland delphi events editing tab on property panel, for a panel that exposes controls as 
	self. pointed attributes at the top level. NB won't recurse into contained panels that contain controls, must process the script of the contained panels to generate their handlers. 
	
	USAGE: 
		1. manual method:
			a. parse the relevant script into lines with fileinput package.
			b. for each line, call get_name_type_for_line to get back a tuple of the control name vs. its type name (e.g. text_ctrl_1 vs. wxTextCtrl)
			c. add this tuple to a list. 
			d. When finished processing all lines, call process_list(list) and standout output will be the generated empty handler script
			
		2. single file :
			a. call process_ui_definition( filename), and the
			above steps will be done. Won't work for conditional
			creational scripts like gmEditArea. The handler name 
			will be derived from the filename.
		
		3. directory of files:
			a. call process_directory(directory)
			and the steps for single file.
			
			"""
			
	def __init__(self):
		self.funcs = []
		self.evts = []
		self.prog_map = None
		self.type_search_str = None
		self.control_definition_str = None
		self.gen_func_params_map = {
		#'EditAreaTextBox': [("EVT_TEXT", "text_entered")],
		'wxTextCtrl': [("EVT_TEXT", "text_entered")],
		'wxComboBox': [("EVT_TEXT", "text_entered")] ,
		'wxRadioButton': [("EVT_RADIOBUTTON", "radiobutton_clicked")],
		'wxCheckBox': [("EVT_CHECKBOX", "checkbox_clicked")],
		'wxButton' : [("EVT_BUTTON", "button_clicked" )],
		'wxListBox': [("EVT_LISTBOX", "list_box_single_clicked"), ("EVT_LISTBOX_DCLICK", "list_box_double_clicked")]
		}
		self.components = [ 'EditAreaTextBox','wxTextCtrl', 'wxComboBox', 'wxButton', 'wxRadioButton', 'wxCheckBox', 'wxListBox' ]
	

	
	def get_prog(self, component):
		if self.control_definition_str == None:
			self.control_definition_str = '\s+self\s*.\s*(?P<component>\w+)\s*=\s*%s'
		return re.compile(self.control_definition_str % component, re.I)
		
	def get_prog_map(self):
		"""returns a regular expression object map for the different components """

		if self.prog_map <> None:
			return self.prog_map
		
		prog_map = {}
		for c in self.components:
			prog_map[c] = self.get_prog(c)

		self.prog_map = prog_map	

		return self.prog_map	

	def check_for_new_type_definition(self, line):
		if self.type_search_str == None:
			self.type_search_str = 'class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>%s)' % '|'.join(self.components)
			print "# type_search_str = ", self.type_search_str
			self.prog_type = re.compile( self.type_search_str, re.I)
		re_match = self.prog_type.match(line)
		if re_match == None:
			return

		new_type = re_match.group('new_type')
		base_type = re_match.group('base_type')

		print "# found new type = %s which is base_type %s\n" % ( new_type , base_type)
		self.components.append( new_type )
		self.prog_map[new_type] = self.get_prog(new_type)
		self.gen_func_params_map[new_type] = self.gen_func_params_map[base_type]

		

			

	def get_name_type_for_line( self, line):
		self.check_for_new_type_definition( line)
		prog_map = self.get_prog_map()
		for c in prog_map.keys():
			re_match_obj =  prog_map[c].match(line)
			if re_match_obj == None:
				continue
			return ( re_match_obj.group('component'), c )
		return None
		
			

	def gen_id_set(self, component):
		return """
		id = self.panel.%s.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.%s.SetId(id)
		self.id_map['%s'] = id
		""" % ( component, component, component)
		
		
	def gen_command(self,  macro, func, comp):
		self.evts.append("%s(self.panel.%s,\\\n\t\t\tself.id_map['%s'],\\\n\t\t\tself.%s_%s)" % ( macro, comp, comp,  comp , func) )
		self.funcs.append("%s_%s"%(comp, func) )

	def process_comp_type_pair(self,  comp, type):

		#if self.parent_map.has_key(type):
		#	type = self.parent_map[type]

		params = self.gen_func_params_map[type]
		self.ids.append(self.gen_id_set(comp))
		for cmd_func in params:
			self.gen_command( cmd_func[0], cmd_func[1], comp) 	

	def process_map( self, map):
		self.process_list(self, map['components'])

	def process_list(self,  list):
		self.funcs = []
		self.evts = []
		self.ids = []
		self.comps = []
		for (comp, type) in list:
			self.process_comp_type_pair( comp, type)
			
		#don't need
		for comp, type in list:
			self.comps.append(comp)

	def process_ui_definition( self, filename, has_import_statements = 1):
		lines = fileinput.input(filename)
		list = []
		for l in lines:
			tuple = self.get_name_type_for_line(l)
			if tuple <> None:
				list.append(tuple)
		print "#", list
		if list == []:
			return
		self.process_list(list)
		self.print_single_class( string.split(os.path.basename(filename),'.' )[0] , has_import_statements)
		

	def process_directory( self, dir_path, filter_list=['.py'] , exclude_list=['__']):
		import dircache, os
		dir_list = dircache.listdir(os.path.abspath(dir_path))
		dir_list=dir_list[:]  # copy into a real list  as per python library reference 
		dircache.annotate('/', dir_list)
		list = filter( lambda x: x[-1] <> '/', dir_list)
		list = filter( lambda x: x[-3:] in filter_list, list)
		list = filter(lambda x: not filter( lambda z: x.startswith(z), exclude_list ) , list)
			
		print "#",  list	
		self.print_imports()
		for x in list:
			path = os.path.join( dir_path, x)
			if os.path.isfile(path):
				self.create_handler_file( x, path)
				
		
	def create_handler_file(self, x, path):
		l = string.split(x, '.')
		prefix = l[0]
		print "#creating a handler as %s_handler from %s"%(prefix, path)
		self.process_ui_definition( path, has_import_statements = 0)

		
	def print_single_class(self, name, has_import_statements = 1):
		if has_import_statements:
			self.print_imports()
		self.print_class(name)
		
	def print_imports(self):
		print """
from wxPython.wx import * """		
	
	def print_class(self , name ):
		
		print """

class %s_handler:

	def create_handler(self, panel):
		return self.__init__(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
	
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}
""" % name
		
		for i in self.ids:
			print i
		
		
		print """
	def __set_evt(self):
		pass
		"""
		for i in self.evts:
			print"""
		%s""" % i
			
		
		

		for i in self.funcs:
			print """
	def %s( self, event):
		pass
		if self.impl <> None:
			self.impl.%s(self, event) 
			""" % (i,i )
			print """
		print "%s received ", event
			""" % i



def usage():
	print """
	
	generates empty handler scripts for wxPython ui scripts.

	python handler_generator -h | -d directory | -f file

			where 
				-h  this hekp

				-d  directory to find source files of ui definitions
				-f  file of ui definition

"""

if __name__=="__main__":
	import getopt
	gen = generator()
	options, other_args  = getopt.getopt(sys.argv[1:], "hd:f:")
	for opt, value in options:
		if opt == '-h':
			print usage() 
			sys.exit(0)
		
		if opt == '-f':
			generator().process_ui_definition(value, has_import_statements = 1)
			sys.exit(0)

		if opt == '-d' and value <> None :	
			generator().process_directory(value)
			sys.exit(0)
