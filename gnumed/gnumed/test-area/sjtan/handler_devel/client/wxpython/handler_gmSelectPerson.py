# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# [('buttonSelect', 'wxButton'), ('buttonEdit', 'wxButton'), ('buttonNew', 'wxButton'), ('buttonAdd', 'wxButton'), ('buttonMerge', 'wxButton')]

class gmSelectPerson_funcs:
		

	def buttonSelect_button_clicked( self, event):
		pass
	

	def buttonEdit_button_clicked( self, event):
		pass
	

	def buttonNew_button_clicked( self, event):
		pass
	

	def buttonAdd_button_clicked( self, event):
		pass
	

	def buttonMerge_button_clicked( self, event):
		pass
	

from wxPython.wx import *
from  gmGuiBroker import GuiBroker



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

		
	

class gmSelectPerson_handler(base_handler, gmSelectPerson_funcs):
	
	
	def __init__(self, panel = None, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('buttonSelect') ,
			'comp_name' : 'buttonSelect','setter_name' :  'None' } 
		map['buttonSelect'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonEdit') ,
			'comp_name' : 'buttonEdit','setter_name' :  'None' } 
		map['buttonEdit'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonNew') ,
			'comp_name' : 'buttonNew','setter_name' :  'None' } 
		map['buttonNew'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonAdd') ,
			'comp_name' : 'buttonAdd','setter_name' :  'None' } 
		map['buttonAdd'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonMerge') ,
			'comp_name' : 'buttonMerge','setter_name' :  'None' } 
		map['buttonMerge'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('buttonSelect'):
			self.set_id_common( 'buttonSelect',self.panel.buttonSelect)
			

		if self.panel.__dict__.has_key('buttonEdit'):
			self.set_id_common( 'buttonEdit',self.panel.buttonEdit)
			

		if self.panel.__dict__.has_key('buttonNew'):
			self.set_id_common( 'buttonNew',self.panel.buttonNew)
			

		if self.panel.__dict__.has_key('buttonAdd'):
			self.set_id_common( 'buttonAdd',self.panel.buttonAdd)
			

		if self.panel.__dict__.has_key('buttonMerge'):
			self.set_id_common( 'buttonMerge',self.panel.buttonMerge)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('buttonSelect'):
			EVT_BUTTON(self.panel.buttonSelect,\
			self.id_map['buttonSelect'],\
			self.buttonSelect_button_clicked)

		if self.panel.__dict__.has_key('buttonEdit'):
			EVT_BUTTON(self.panel.buttonEdit,\
			self.id_map['buttonEdit'],\
			self.buttonEdit_button_clicked)

		if self.panel.__dict__.has_key('buttonNew'):
			EVT_BUTTON(self.panel.buttonNew,\
			self.id_map['buttonNew'],\
			self.buttonNew_button_clicked)

		if self.panel.__dict__.has_key('buttonAdd'):
			EVT_BUTTON(self.panel.buttonAdd,\
			self.id_map['buttonAdd'],\
			self.buttonAdd_button_clicked)

		if self.panel.__dict__.has_key('buttonMerge'):
			EVT_BUTTON(self.panel.buttonMerge,\
			self.id_map['buttonMerge'],\
			self.buttonMerge_button_clicked)

class gmSelectPerson_mapping_handler(gmSelectPerson_handler):
	def __init__(self, panel = None, model = None, impl = None):
		gmSelectPerson_handler.__init__(self, panel, model, impl)
		
	

		
	def buttonSelect_button_clicked( self, event): 

		if self.impl <> None:
			self.impl.buttonSelect_button_clicked(  event) 
			

		print "buttonSelect_button_clicked received ", event
			

		
	def buttonEdit_button_clicked( self, event): 

		if self.impl <> None:
			self.impl.buttonEdit_button_clicked(  event) 
			

		print "buttonEdit_button_clicked received ", event
			

		
	def buttonNew_button_clicked( self, event): 

		if self.impl <> None:
			self.impl.buttonNew_button_clicked(  event) 
			

		print "buttonNew_button_clicked received ", event
			

		
	def buttonAdd_button_clicked( self, event): 

		if self.impl <> None:
			self.impl.buttonAdd_button_clicked(  event) 
			

		print "buttonAdd_button_clicked received ", event
			

		
	def buttonMerge_button_clicked( self, event): 

		if self.impl <> None:
			self.impl.buttonMerge_button_clicked(  event) 
			

		print "buttonMerge_button_clicked received ", event
			
