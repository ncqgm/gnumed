from wxPython.wx import *
import gmGuiBroker, gmLog
	

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
        # IH: as requested, this is now a multi-toolbar
        # FIXME: how to we set the right width? 300 does it for now!
        self.tb1 = wxPanel (self, -1, size = wxSize (300, 25)) # force thin line
        self.subbars = {}
	self.sizer.Add(1,3,0,wxEXPAND)		  
        self.sizer.Add(tb2,1,wxEXPAND)
        self.sizer.Add(self.tb1,1,wxEXPAND)
	self.SetSizer(self.sizer)  #set the sizer 
	self.sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
        

    def AddBar (self, key):
        """
        Creates and returns a new empyty toolbar, referenced by key
        Key must correspond to the notebook page number is defined by the notebook (see gmPlugin.py)
        """
        self.subbars[key] = wxToolBar (self.tb1, -1, size=self.tb1.GetClientSize (), style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        self.subbars[key].SetToolBitmapSize((16,16))
        if len (self.subbars) == 1:
            self.subbars[key].Show ()
            self.__current = key
        else:
            self.subbars[key].Hide ()
        return self.subbars[key]
            
    def ShowBar (self, key):
        """
        Displays the named toolbar
        """
        self.subbars[self.__current].Hide ()
        if self.subbars.has_key (key):
            self.subbars[key].Show ()
            self.__current = key
        else:
            gmLog.gmDefLog.Log (gmLog.lErr, "tried to show non-existent toolbar %s" % key)

    def DeleteBar (self, key):
        """
        Removes a toolbar
        """
        if self.subbars.has_key (key):
            self.subbars[key].Destroy ()
            del self.subbars[key]
            if self.__current == key and len (self.subbars):
                self.__current = self.subbars.keys () [0]
                self.subbars[self.__current].Show ()
        else:
            gmLog.gmDefLog.Log (gmLog.lErr, "tried to delete non-existent %s" % key)

	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(Toolbar, -1)
	app.MainLoop()
           
