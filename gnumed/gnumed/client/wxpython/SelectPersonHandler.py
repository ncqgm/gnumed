
from wxPython.wx import * 


class SelectPersonHandler_handler:

	def create_handler(self, panel):
		return SelectPersonHandler_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.buttonSelect.SetId(id)
		self.id_map['buttonSelect'] = id
		

		id = wxNewId()
		self.panel.buttonEdit.SetId(id)
		self.id_map['buttonEdit'] = id
		

		id = wxNewId()
		self.panel.buttonNew.SetId(id)
		self.id_map['buttonNew'] = id
		

		id = wxNewId()
		self.panel.buttonAdd.SetId(id)
		self.id_map['buttonAdd'] = id
		

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

		print "buttonSelect_button_clicked received ", event
			

	def buttonEdit_button_clicked( self, event):
		pass

		print "buttonEdit_button_clicked received ", event
			

	def buttonNew_button_clicked( self, event):
		pass

		print "buttonNew_button_clicked received ", event
			

	def buttonAdd_button_clicked( self, event):
		pass

		print "buttonAdd_button_clicked received ", event
			

	def buttonMerge_button_clicked( self, event):
		pass

		print "buttonMerge_button_clicked received ", event
			
