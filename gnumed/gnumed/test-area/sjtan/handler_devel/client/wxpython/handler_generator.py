	 	

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
		'wxTextCtrl': [("EVT_TEXT", "text_entered", "GetValue", "SetValue")],
		'wxComboBox': [("EVT_TEXT", "text_entered", "GetValue", "SetValue")] ,
		'wxRadioButton': [("EVT_RADIOBUTTON", "radiobutton_clicked", "GetValue", "SetValue")],
		'wxCheckBox': [("EVT_CHECKBOX", "checkbox_clicked", "GetValue", "SetValue")],
		'wxButton' : [("EVT_BUTTON", "button_clicked" , None , None )],
		'wxListBox': [("EVT_LISTBOX", "list_box_single_clicked", "GetStringSelection", "SetStringSelection"), ("EVT_LISTBOX_DCLICK", "list_box_double_clicked", "GetStringSelection", "SetStringSelection" )]
		}
		self.components = [ 'wxTextCtrl', 'wxComboBox', 'wxButton', 'wxRadioButton', 'wxCheckBox', 'wxListBox' ]
	

	
	def get_prog(self, component):
		if self.control_definition_str == None:
			self.control_definition_str = '\s+(self|parent)\s*.\s*(?P<component>\w+)\s*=\s*%s'
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
		if self.panel.__dict__.has_key('%s'):
			self.set_id_common( '%s',self.panel.%s)
			""" % (component,  component, component)
		
		
	def gen_command(self,  macro, function_suffix, accessor, setter,    component):
		self.evts.append("""if self.panel.__dict__.has_key('%s'):
			%s(self.panel.%s,\\\n\t\t\tself.id_map['%s'],\\\n\t\t\tself.%s_%s)""" % ( component, macro, component, component,  component , function_suffix) )
		self.funcs.append((component, function_suffix, accessor, setter ) )

	def process_comp_type_pair(self,  comp, type):

		#if self.parent_map.has_key(type):
		#	type = self.parent_map[type]

		params = self.gen_func_params_map[type]
		self.ids.append(self.gen_id_set(comp))
		for cmd_func in params:
			self.gen_command( macro = cmd_func[0], function_suffix = cmd_func[1] , accessor = cmd_func[2], setter = cmd_func[3], component =  comp) 	
	

	def process_map( self, map):
		self.process_list(self, map['components'])
		

	def clear_ui_state(self):
		self.funcs = []
		self.evts = []
		self.ids = []
		self.comps = []

	def process_list(self,  list):
		self.clear_ui_state()
		for (comp, type) in list:
			self.process_comp_type_pair( comp, type)
			
			
		#don't need
		for comp, type in list:
			self.comps.append(comp)
	
	def filename_without_suffix(self, filename):
		return  string.split(os.path.basename(filename),'.' )[0]


	def get_ui_fields(self, lines):
		list = []
		for l in lines:
			tuple = self.get_name_type_for_line(l)
			if tuple <> None:
				list.append(tuple)
		print "#", list
		return list	
		

	def set_file_containing_fields_to_process( self, filename):
		lines = fileinput.input(filename)
		list = self.get_ui_fields(lines)

		self.clear_ui_state()
		if list == []:
			return 0 
		self.process_list(list)
		return 1

		
	def get_paths( self, dir_path, filter_list=['.py'] , exclude_list=['__']):
		import dircache, os
		dir_list = dircache.listdir(os.path.abspath(dir_path))
		dir_list=dir_list[:]  # copy into a real list  as per python library reference 
		dircache.annotate('/', dir_list)
		list = filter( lambda x: x[-1] <> '/', dir_list)
		list = filter( lambda x: x[-3:] in filter_list, list)
		list = filter(lambda x: not filter( lambda z: x.startswith(z), exclude_list ) , list)
			
		print "#",  list	
		paths = []
		for x in list:
			path = os.path.join( dir_path, x)
			if os.path.isfile(path):
				paths.append(path)
		return paths		
		
	

	def process_directory( self, dir_path, filter_list=['.py'] , exclude_list=['__']):
		paths = self.get_paths( dir_path, filter_list, exclude_list)
				
		
		for path in paths:
			self.set_file_containing_fields_to_process( path)
			if self.funcs <> []:
				self.print_funcs( self.filename_without_suffix(path))

		self.print_imports()
		self.print_base_class()
		for path in paths:
			self.set_file_containing_fields_to_process( path)
			if self.funcs <> []:
				self.print_classes( self.filename_without_suffix(path))

		for path in paths:
			self.set_file_containing_fields_to_process( path)
			if self.funcs <> []:
				self.print_gui_broker_set_statement(self.filename_without_suffix(path))

			
				
	def process_ui_definition( self, filename, has_import_statements = 1):
		self.set_file_containing_fields_to_process(  filename)
		self.print_single_class( self.filename_without_suffix(filename) , has_import_statements)
		
	def create_handler_file(self, x, path):
		l = string.split(x, '.')
		prefix = l[0]
		print "#creating a handler as %s_handler from %s"%(prefix, path)
		self.process_ui_definition( path, has_import_statements = 0)

	def print_gui_broker_set_statement(self, name):

		print "GuiBroker()['%s_handler']= %s_mapping_handler()" % (name, name)
		print "print 'GuiBroker has handler', GuiBroker()['%s_handler']" % name
		
	def print_single_class(self, name, has_import_statements = 1):
		self.print_funcs(name)		
		if has_import_statements:
			self.print_setup()
		self.print_classes(name)
		
	def print_setup(self):
		self.print_imports()
		self.print_base_class()
		
	def print_imports(self):
		print """
from wxPython.wx import *
from  gmGuiBroker import GuiBroker
"""		

	def get_parts_name(self, name):
			parts = string.split( name, '_')
			if len(parts) > 1:
				name = '_'.join( parts[1:])
				prefix = parts[0]
				return name, prefix
			
			return name, ""
	
	def print_base_class(self  ):
		
		print """

class base_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return  self.__init__(panel, model, self.impl)

	def __init__(self, panel, model = None, impl = None):
		self.panel = panel
		self.set_impl(impl)	
		if panel <> None:
			self.set_id()
			self.set_evt()
			self.set_name_map()

		self.set_model(model)
			
	def set_id(self):
		# pure virtual
		pass
	
	def set_evt(self):
		# pure virtual
		pass

	def set_name_map(self):
		# implement in subclasses,ie. pure virtual(c++) or abstact method( java)
		pass
		
	def set_model(self,  model):
		if model == None:
			self.model ={}
			return
		
		self.model = model
		
		
		if  len(model) > 0 and self.panel <> None:
			self.update_ui(model)
			
	def update_ui(self, model = None):
		if model == None:
			model = self.model
		if not  self.__dict__.has_key('name_map'):
			return
		if self.name_map == None:
			return
		
		for k in model.keys():
			v = model[k]
			map = self.name_map.get( k, None)
			if map == None:
				continue
			print "comp map = ", map
			setter = map.get('setter_name', None)
			if setter == None:
				continue
			component = map.get('comp_name')
			if component ==  None:
				continue
			
			#setter(component, v)
			try:
				exec( 'self.panel.%s.%s("%s")' % ( component, setter, v) )
			except:
				try:
					exec( 'self.panel.%s.%s(%s)' % ( component, setter, v) )
				except:
					print 'failed to set',component,setter,  v
			
			
		
	def set_impl(self, impl):
		self.impl = impl
		if impl <> None:
			impl.set_owner(self)

	def get_valid_component( self , key):
		if self.panel.__dict__.has_key(key):
			return self.panel.__dict__[key]
		return None


	def set_id_common(self, name ,  control ):
		id = control.GetId()
		if id <= 0:
			id = wxNewId()
			control.SetId(id)
		self.id_map[name] = id

		
	""" 
	
	def print_funcs(self, name):

	
		print """
class %s_funcs:
		""" % name
		
		for i in self.funcs:
			print """
	def %s_%s( self, event):
		pass
	""" %( i[0], i[1] )
	
	def print_classes(self, name):
		
		print"""
class %s_handler(base_handler, %s_funcs):
	
	
	def __init__(self, panel = None, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		""" % (name, name)
		
	
		print """
	def set_name_map(self):
		map = {}
		"""
		for i in self.funcs:
			name_comp, prefix = self.get_parts_name( i[0] )
			print""" 
		comp_map = { 'component': self.get_valid_component('%s') ,\n\t\t\t'comp_name' : '%s','setter_name' :  '%s' } 
		map['%s'] = comp_map
		""" % (  i[0], i[0],  i[3] , name_comp) 

		print """
		self.name_map = map
	

	def set_id(self):
		self.id_map = {}
""" 
		
		for i in self.ids:
			print i
		
		
		print """
	def set_evt(self):
		pass
		"""
		for i in self.evts:
			print"""
		%s""" % i
			

		print """
class %s_mapping_handler(%s_handler):
	def __init__(self, panel = None, model = None, impl = None):
		%s_handler.__init__(self, panel, model, impl)
		
	""" % (name, name, name)

		for i in self.funcs:
			print """
		
	def %s_%s( self, event): 

		if self.impl <> None:
			self.impl.%s_%s(  event) 
			""" % (i[0], i[1] ,i[0],i[1])
						
			print """
		print "%s_%s received ", event
			""" % (i[0], i[1])
			#    comp, func_suffix
			
			if i[2] == None:	# no accessor
				continue
			
			name, prefix = self.get_parts_name(i[0])
				
			print """	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['%s']= obj.%s()
			except:
				# for dumbdbm persistent maps
				self.model['%s'] = str(obj.%s())
				
			print self.model, "%s = ",  self.model['%s']
		"""  	% (name, i[2], name, i[2], name, name)
			#comp, accessor, comp , comp, comp



def usage():
	print """
	
	generates empty handler scripts for wxPython ui scripts.

	python handler_generator -h | -d directory | -f file

			where 
				-h  this hekp

				-d  directory to find source files of ui definitions
				-f  file of ui definition
			
			examples:
			python handler_generator -d patient > handler_patient.py
				regenerates handler_patient.py

			python handler_generator -d gui > handler_gui.py

			python handler_gen_editarea.py > EditAreaHandler.py

			python handler_generator -f gmSelectPerson.py > handler_gmSelectPerson.py


"""

if __name__=="__main__":
	import getopt
	gen = generator()
	if len(sys.argv[1:]) == 0 :
		usage()
		sys.exit(0)
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

	usage()		
