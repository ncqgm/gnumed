from wxPython.wx import *
import gmGuiBroker, gmLog, gmConf
	

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
	#create the top toolbar. patient adds top line with patient name etc.
        #-------------------------------------------------------------------------
        self.toplinesizer = wxBoxSizer (wxHORIZONTAL)
	#-------------------------------------------------------------------------
	#create the second tool bar underneath which will hold most of the buttons
	#-------------------------------------------------------------------------
	self.bottomlinesizer = wxBoxSizer (wxHORIZONTAL)
        self.bottomline = wxPanel (self, -1)
        self.subbars = {}
	self.bottomlinesizer.Add (self.bottomline, 1, wxGROW)
	# IMHO: space is at too much of a premium for such padding
	#self.sizer.Add(1,3,0,wxEXPAND)		  
        self.sizer.Add(self.toplinesizer,1,wxEXPAND)
        self.sizer.Add(self.bottomlinesizer,1,wxEXPAND)
	## mini-toolbar for tools on right-hand of bottom line
	self.rightbottomtoolbar = wxToolBar (self, -1, size=wxSize (65, -1), style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        self.rightbottomtoolbar.SetToolBitmapSize((16,16))
	self.rightbottomtoolbar_no_tools = 0
	self.AddWidgetRightBottom (self.rightbottomtoolbar)
	self.SetSizer(self.sizer)  #set the sizer 
	self.sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
        

    def AddWidgetRightBottom (self, widget):
	"""
	Insert a widget on the right-hand side of the bottom toolbar
	"""
	self.bottomlinesizer.Add(widget,0,wxRIGHT,0)

    def AddWidgetTopLine (self, widget):
	"""
	Inserts a widget onto the top line
	"""
	self.toplinesizer.Add (widget, 0, wxEXPAND)

    def AddToolRightBottom (self, image, help, method):
	"""
	Adds a tool to the permanent toolbar on th bottom line, right-side
	"""
	id = wxNewId ()
	self.rightbottomtoolbar.AddTool (id, image, shortHelpString = help)
	self.rightbottomtoolbar.Realize ()
	EVT_TOOL (self, id, method)
	self.rightbottomtoolbar_no_tools += 1
	return id

    def DeleteToolRightBottom (self, tool):
	"""
	Removes a tool from the right-bottom toolbar
	"""
	self.rightbottomtoolbar.DeleteTool (tool)

    def AddBar (self, key):
        """
        Creates and returns a new empty toolbar, referenced by key
        Key should correspond to the notebook page number as defined by the notebook (see gmPlugin.py),
	so that gmGuiMain can display the toolbar with the notebook
        """
        self.subbars[key] = wxToolBar (self.bottomline, -1, size=self.bottomline.GetClientSize (), style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        self.subbars[key].SetToolBitmapSize((16,16))
        if len (self.subbars) == 1:
            self.subbars[key].Show (1)
            self.__current = key
        else:
            self.subbars[key].Hide ()
        return self.subbars[key]

    def ReFit (self):
	"""
	Refits the toolbar after its been changed
	"""
	tw = 0
	th = 0
	# get maximum size for the toolbar
	for i in self.subbars.values ():
		ntw, nth = i.GetSizeTuple ()
		if ntw > tw:
			tw = ntw
		if nth > th:
			th = nth
	#import pdb
	#pdb.set_trace ()
	s = wxSize (tw, th)
	self.bottomline.SetSize (s)
	for i in self.subbars.values ():
		i.SetSize (s)
	# right toolbar does not size properly
	self.rightbottomtoolbar.SetSize (wxSize (self.rightbottomtoolbar_no_tools*20, 20))
	self.sizer.Layout ()
	self.sizer.Fit (self)
            
    def ShowBar (self, key):
        """
        Displays the named toolbar
        """
        self.subbars[self.__current].Hide ()
        if self.subbars.has_key (key):
            self.subbars[key].Show (1)
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
                self.subbars[self.__current].Show (1)
        else:
            gmLog.gmDefLog.Log (gmLog.lErr, "tried to delete non-existent %s" % key)

	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(Toolbar, -1)
	app.MainLoop()
           
