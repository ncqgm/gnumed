# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>EditAreaTextBox|wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)

from wxPython.wx import * 


class gmSelectPerson_handler:

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


		id = self.panel.buttonSelect.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonSelect.SetId(id)
		self.id_map['buttonSelect'] = id
		

		id = self.panel.buttonEdit.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonEdit.SetId(id)
		self.id_map['buttonEdit'] = id
		

		id = self.panel.buttonNew.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonNew.SetId(id)
		self.id_map['buttonNew'] = id
		

		id = self.panel.buttonAdd.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonAdd.SetId(id)
		self.id_map['buttonAdd'] = id
		

		id = self.panel.buttonMerge.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonMerge.SetId(id)
		self.id_map['buttonMerge'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.buttonSelect,\
			self.id_map['buttonSelect'],\
			self.buttonSelect_button_clicked)

		EVT_BUTTON(self.panel.buttonEdit,\
			self.id_map['buttonEdit'],\
			self.buttonEdit_button_clicked)

		EVT_BUTTON(self.panel.buttonNew,\
			self.id_map['buttonNew'],\
			self.buttonNew_button_clicked)

		EVT_BUTTON(self.panel.buttonAdd,\
			self.id_map['buttonAdd'],\
			self.buttonAdd_button_clicked)

		EVT_BUTTON(self.panel.buttonMerge,\
			self.id_map['buttonMerge'],\
			self.buttonMerge_button_clicked)

	def buttonSelect_button_clicked( self, event):
		pass
		if self.impl <> None:
			self.impl.buttonSelect_button_clicked(self, event) 
			

		print "buttonSelect_button_clicked received ", event
			

	def buttonEdit_button_clicked( self, event):
		pass
		if self.impl <> None:
			self.impl.buttonEdit_button_clicked(self, event) 
			

		print "buttonEdit_button_clicked received ", event
			

	def buttonNew_button_clicked( self, event):
		pass
		if self.impl <> None:
			self.impl.buttonNew_button_clicked(self, event) 
			

		print "buttonNew_button_clicked received ", event
			

	def buttonAdd_button_clicked( self, event):
		pass
		if self.impl <> None:
			self.impl.buttonAdd_button_clicked(self, event) 
			

		print "buttonAdd_button_clicked received ", event
			

	def buttonMerge_button_clicked( self, event):
		pass
		if self.impl <> None:
			self.impl.buttonMerge_button_clicked(self, event) 
			

		print "buttonMerge_button_clicked received ", event
			
