	 	

import fileinput
import re

import string
import sys


class generator:
	def __init__(self):
		self.funcs = []
		self.evts = []
		self.prog_map = None
		self.gen_func_params_map = {
		'EditAreaTextBox': [("EVT_TEXT", "text_entered")],
		'wxTextCtrl': [("EVT_TEXT", "text_entered")],
		'wxComboBox': [("EVT_TEXT", "text_entered")] ,
		'wxRadioButton': [("EVT_RADIOBUTTON", "radiobutton_clicked")],
		'wxCheckBox': [("EVT_CHECKBOX", "checkbox_clicked")],
		'wxButton' : [("EVT_BUTTON", "button_clicked" )],
		'wxListBox': [("EVT_LISTBOX", "list_box_single_clicked"), ("EVT_LISTBOX_DCLICK", "list_box_double_clicked")]
		}
		self.components = [ 'EditAreaTextBox','wxTextCtrl', 'wxComboBox', 'wxButton', 'wxRadioButton', 'wxCheckBox', 'wxListBox' ]
		
	def get_prog_map(self):
		"""returns a regular expression object map for the different components """

		if self.prog_map <> None:
			return self.prog_map
		
		prog_map = {}
		editarea_str = '\s+self\s*.\s*(?P<component>\w+)\s*=\s*%s'
		for c in self.components:
			prog_map[c] = re.compile( editarea_str % c , re.I)

		self.prog_map = prog_map	

		return self.prog_map	

	def get_name_type_for_line( self, line):
		prog_map = self.get_prog_map()
		for c in prog_map.keys():
			re_match_obj =  prog_map[c].match(line)
			if re_match_obj == None:
				continue
			return ( re_match_obj.group('component'), c )
		return None
		
			

	def gen_id_set(self, component):
		return """
		id = wxNewId()
		self.panel.%s.SetId(id)
		self.id_map['%s'] = id
		""" % ( component, component)
		
		
	def gen_command(self,  macro, func, comp):
		self.evts.append("%s(self.panel.%s,\\\n\t\t\tself.id_map['%s'],\\\n\t\t\tself.%s_%s)" % ( macro, comp, comp,  comp , func) )
		self.funcs.append("%s_%s"%(comp, func) )

	def process_comp_type_pair(self,  comp, type):
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
		
	def print_single_class(self, name):
		self.print_imports()
		self.print_class(name)
		
	def print_imports(self):
		print """
from wxPython.wx import * """		
	
	def print_class(self , name ):
		
		print """

class %s_handler:

	def create_handler(self, panel):
		return %s_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}
""" % (name, name)
		
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


		


