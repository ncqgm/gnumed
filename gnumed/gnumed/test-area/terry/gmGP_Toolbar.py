from wxPython.wx import *
import gmGuiBroker
	

class Toolbar(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER )
	#----------------------------------------------------------------
	#horizontal sizer holds first the patient picture panel, then the
	#two vertically stacked toolbars
	#----------------------------------------------------------------
        self.sizer = wxBoxSizer(wxVERTICAL) 
	self.SetBackgroundColour(wxColour(222,222,222))
        #(197,194,197)) #222,218,222
        gb = gmGuiBroker.GuiBroker ()
    
	#-------------------------------------------------------------------------
	#create the top toolbar with the findpatient, age and allergies text boxes
        #-------------------------------------------------------------------------
        tb2 = wxToolBar(self,-1,wxDefaultPosition,wxDefaultSize,wxTB_HORIZONTAL|wxRAISED_BORDER|wxTB_FLAT)
        tb2.SetToolBitmapSize((21,21))
        gb['main.top_toolbar'] = tb2
	#-------------------------------------------------------------------------
	#create the second tool bar underneath which will hold most of the buttons
	#-------------------------------------------------------------------------
	tb1 = wxToolBar(self,-1,wxDefaultPosition,wxDefaultSize,wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        tb1.SetToolBitmapSize((16,16))
        gb['main.bottom_toolbar'] = tb1
	
	self.sizer.Add(1,3,0,wxEXPAND)		  
        self.sizer.Add(tb2,1,wxEXPAND)
        self.sizer.Add(tb1,1,wxEXPAND)
	self.SetSizer(self.sizer)  #set the sizer 
	self.sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
        

	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(Toolbar, -1)
	app.MainLoop()
           
