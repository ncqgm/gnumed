usage=""" python editarea_gen_listener.py  > EditAreaHandler.py   and generates handler
	hooks for the different uis in gmEditArea.

	  Any handling code will be lost so must backup old handler scripts to later 
	  cut and paste. Could use a wxGlade like mechanism for merging user code with
	  generated code.

	  Name changes on gmEditArea will be reflected onto EditAreaHandler ,
	  and the function names will change if the editarea component names are changed.
	  """
	 	

import fileinput
import re

import string
import sys

target = 'gmEditArea.py'
global funcs
funcs = [] 

class generator:
	def __init__(self):
		self.funcs = []
		self.evts = []
		self.gen_func_params_map = {
		'EditAreaTextBox': ("EVT_TEXT", "text_entered"),
		'wxTextCtrl': ("EVT_TEXT", "text_entered"),
		'wxComboBox': ("EVT_TEXT", "text_entered") ,
		'wxRadioButton': ("EVT_RADIOBUTTON", "radiobutton_clicked"),
		'wxCheckBox': ("EVT_CHECKBOX", "checkbox_clicked"),
		'wxButton' : ("EVT_BUTTON", "button_clicked" )
		}
	def gen_id_set(self, component):
		return """
		id = wxNewId()
		self.panel.%s.SetId(id)
		self.id_map['%s'] = id
		""" % ( component, component)
		
		
	def gen_command(self,  macro, func, comp):
		self.funcs.append("%s_%s"%(func, comp) )
		self.evts.append("%s(self.panel.%s,\\\n\t\t\tself.id_map['%s'],\\\n\t\t\tself.%s_%s)" % ( macro, comp, comp, func, comp ) )
		self.ids.append(self.gen_id_set(comp))
		

	def process_map_item(self,  comp, type):
		params = self.gen_func_params_map[type]
		self.gen_command( params[0], params[1], comp) 	

	def process_map(self,  map):
		self.funcs = []
		self.evts = []
		self.ids = []
		self.comps = []
		for comp, type in map['components']:
			self.process_map_item( comp, type)
			
		#don't need
		for comp, type in map['components']:
			self.comps.append(comp)
		
	def print_imports(self):
		print """
from wxPython.wx import * """		
	
	def print_class(self , name ):
		
		print """

class %s_handler:
	def __init__(self, panel):
		self.panel = panel
		self.__set_id()
		self.__set_evt()

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
		pass""" % i
			print """
		print "%s received ", event
			""" % i
		
		
			

	
	
			
			
	
		
	
			
		
		

def process_section(gen,  map):
#	print "#the section map = ", map
	gen.process_map(map)
	gen.print_class( map['name'])

	

lines = fileinput.input(target)

print """# scanning for section headers,
#	then for components in file """, target, """
#	and generating a script template for attaching
#	a listener to the components.  """
section_str = '.*section\s*==\s*(?P<section>\w+)'
prog1 = re.compile(section_str, re.I )

components = [ 'EditAreaTextBox','wxTextCtrl', 'wxComboBox', 'wxButton', 'wxRadioButton', 'wxCheckBox' ]

editarea_str = '\s+self\s*.\s*(?P<component>\w+)\s*=\s*%s'

prog_def = re.compile( '(?P<name>gmSECTION\w+)\s*=\s*(?P<number>[0-9]+)')
section_num_map = {}

prog_map = {}
for c in components:
	prog_map[c] = re.compile( editarea_str % c , re.I)
	
section_map = {}

gen = generator()
gen.print_imports()

for l in lines:
	re_match_obj = prog_def.match(l)
	if re_match_obj <> None:
		section_num_map[int(re_match_obj.group('number'))] = re_match_obj.group('name')
		continue
	# match a section start : the state 'creating map' is when section_map.has_key['name'] 
	re_match_obj =  prog1.match(l)
	if re_match_obj <> None:
		sys.stderr.write('\nSection is %s\n' % re_match_obj.group('section') )
		if section_map <> {} :
			process_section(gen, section_map)

		section_map = {}
		section_map['name'] = re_match_obj.group('section') 
		section_map['components'] = []
		
	# match for components	
	#sys.stderr.write( "#checking  %s against %s\n"% (l,  prog_map.keys()))
	for c in prog_map.keys():
		#if  c == 'wxCheckBox' and section_map.has_key('name') and section_map['name'] =="gmSECTION_SCRIPT":
		#	sys.stderr.write('checking %s against %s\n' % (l, c))
		re_match_obj =  prog_map[c].match(l)
		if re_match_obj <> None and section_map.has_key('name'):
			sys.stderr.write( '#*** %s is a %s\n'%( re_match_obj.group('component'), c ))	
			section_map['components'].append( (  re_match_obj.group('component'), c ) )
			break
	

if section_map.has_key('name'):
	process_section(gen, section_map)

print "section_num_map = ", section_num_map	


	


