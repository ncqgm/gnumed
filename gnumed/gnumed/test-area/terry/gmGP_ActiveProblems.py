from wxPython.wx import *

#--------------------------------------------------------------------
# A class for displaying patients active problems
# This code is shit and needs fixing, here for gui development only
# TODO: almost everything
#--------------------------------------------------------------------
class ActiveProblems(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	activeproblemsamplelist =['1980 Hypertension','1982 Acute myocardial infartion', '1992 NIDDM']
	sizer = wxBoxSizer(wxVERTICAL)
       
	activeproblems_listbox = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, activeproblemsamplelist,
                            wxLB_SINGLE)
        sizer.Add(activeproblems_listbox,100,wxEXPAND)
	activeproblems_listbox.SetBackgroundColour(wxColor(255,255,197))
	activeproblems_listbox.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
	self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 

	
if __name__ == "__main__":
    app = wxPyWidgetTester(size = (400, 100))
    app.SetWidget(ActiveProblems, -1)
    app.MainLoop()
 