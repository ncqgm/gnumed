from gmSelectPerson import *   
	#  DlgSelectPerson

import gmGuiBroker

from SelectPersonDialogFactory import *
from SimpleUIFactory import *
from SimpleDefaultCommandMap import *

class  SelectPersonTestFactory (SelectPersonDialogFactory, SimpleUIFactory ):

	def __init__( self, commandMapper = SimpleDefaultCommandMap()):
		self.commandMapper = commandMapper	
	def createDialog( self, parent, id):
		
		self.commandMapper.setParent(parent)
		
		self.cmds = self.commandMapper.getMap()	
		dialog = DlgSelectPerson(parent, id)
	
		for x in self.cmds.keys():
			dialog.addCommand( x, self.cmds[x])			
		

		print "dialog commands set to ", dialog.getCommands() 
		dialog.MakeModal(true)
		return dialog

	def getUI( self, parent, id, data = None):
		return self.createDialog( parent, id)


class TestApp(wxApp):
        def __init__(self, factory):
		self.factory = factory
                wxApp.__init__(self, 0)

        def OnInit(self):
                frame = wxFrame(None, -1, "Select Person" , size=(500,400) )
		
                self.SetTopWindow(frame)
                self.frame= frame
                frame.Show(true)
                frame.SetFocus()
		dialog = self.factory.createDialog( frame, -1)
		dialog.Show()		
                return true



if __name__ == "__main__":
	app = TestApp( SelectPersonTestFactory())
        app.MainLoop()
	
