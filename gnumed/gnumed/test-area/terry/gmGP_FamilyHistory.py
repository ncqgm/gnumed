from wxPython.wx import *

#--------------------------------------------------------------------
# A class for displaying social history
# This code is shit and needs fixing, here for gui development only
# TODO: Pass social history text to this panel not display fixed text
#--------------------------------------------------------------------
class FamilyHistory(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	txt_family_history = wxTextCtrl(self, 30,
                        "FAMILY HISTORY: Stroke(father-died72yrs);NIDDM(general - maternal).\n",
                         wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
        txt_family_history.SetInsertionPoint(0)
	txt_family_history.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxNORMAL, false,'xselfont'))
	txt_family_history.SetForegroundColour(wxColour(1, 1, 255))
        sizer.Add(txt_family_history,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        #self.Show(true) 

	
if __name__ == "__main__":
    app = wxPyWidgetTester(size = (400, 100))
    app.SetWidget(FamilyHistory, -1)
    app.MainLoop()
 
