from wxPython.wx import *
from SimpleUIFactory import *


class SimpleRecordDisplayPanel( wxPanel):

	def __init__(self, parent, id = -1, 
				list = [ {'name': 'FirstName', 'value':'Harry' } , {'name' : 'address', 'value': '57 Fifth st' } ], 
				 fontSize = 8):
	
		wxPanel.__init__(self, parent, id )
		self.fontSize = fontSize

		sizer = wxFlexGridSizer( cols = 6, hgap = 5, vgap = 5)
		for x in list:
			comps = self.getFieldComponents( x)
			sizer.AddMany( [ comps[0], comps[1], (0,0)  ])
		self.SetSizer(sizer)
		self.SetAutoLayout(true)
		sizer.Fit(parent)	
	

	def getFieldComponents(self, x):
		label = wxStaticText( self, -1, x['name'])
		font = label.GetFont()
		font.SetPointSize(self.fontSize)
		label.SetFont(font)

		field = wxStaticText( self, -1, x['value'])
		field.SetFont(font)
		return [ label, field ]

class SimpleRecordDisplayFactory( SimpleUIFactory):
	
	def getUI( self, parent , id = -1,  params = []):
		list = params[0]
		print "list = ", list
		panel = SimpleRecordDisplayPanel( parent, id, list)
		return panel

class TestApp(wxApp):

        def OnInit(self):
                frame = wxFrame( None, -1, "Test Summary Sheet", size = (510, 600) )
                win =  SimpleRecordDisplayFactory(). getUI ( frame, params = [ 
                                 [ {'name': 'FirstName', 'value':'Harry' } , {'name' : 'address', 'value': '57 Fifth st' } ]
				] )
                frame.Show()
                return true

if __name__ == "__main__":
        app = TestApp( )
        app.MainLoop()


			
