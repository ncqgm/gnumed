from handler_gmSelectPerson import *

from wxPython.wx import *

from gmGuiBroker import *
class gmSelectPerson_handler_impl( gmSelectPerson_handler):
	def __init__(self, panel = None , model = None):
		gmSelectPerson_handler.__init__(self,panel, model)
		#self.set_impl( self)

	def buttonSelect_button_clicked( self, event):
		pass

		print "buttonSelect_button_clicked received ", event
			

	def buttonEdit_button_clicked( self, event):
		pass

		print "buttonEdit_button_clicked received ", event
			

	def buttonNew_button_clicked( self, event):
		gb = GuiBroker()
		map = gb['widgets']
		map['PatientsPanel'].plugin.OnTool(None)

		print  "buttonNew_button_clicked received ", event
			

	def buttonAdd_button_clicked( self, event):
		pass

		print "buttonAdd_button_clicked received ", event
			

	def buttonMerge_button_clicked( self, event):
		pass

		print "buttonMerge_button_clicked received ", event
			
