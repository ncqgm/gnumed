try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#--------------------------------------------------------------------
# A class for displaying social history
# This code is shit and needs fixing, here for gui development only
# TODO: Pass social history text to this panel not display fixed text
#--------------------------------------------------------------------
class SocialHistory(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	txt_social_history = wxTextCtrl(self, 30,
                        "Born in QLD, son of an itinerant drover. Mother worked as a bush nurse. "
                        "Two brothers, Fred and Peter. Left school aged 15yrs, apprentice fitter "
                        "then worked in industry for 10ys. At 22yrs age married Joan, two children"
                        "Peter b1980 and Rachaelb1981. Retired in 1990 due to receiving a fortune.",
                        #"previously unknown great aunt. Interests include surfing, fishing, carpentry",                       ,
                       wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
        txt_social_history.SetInsertionPoint(0)
	txt_social_history.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, 'xselfont'))
	#self.textCtrl1.SetFont(wxFont(14, wxSWISS, wxNORMAL, wxBOLD, False, 'verdana'))
        sizer.Add(txt_social_history,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(True)                 #tell frame to use the sizer
        #self.Show(True)
	self.text = txt_social_history

	print self.GetValue()

    def SetValue( self, text):
	    self.text.SetValue(text)

    def GetValue(self):
	    return self.text.GetValue()
if __name__ == "__main__":
    app = wxPyWidgetTester(size = (500, 100))
    app.SetWidget(SocialHistory, -1)
    app.MainLoop()
 
