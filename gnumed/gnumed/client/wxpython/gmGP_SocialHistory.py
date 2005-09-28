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
class SocialHistory(wx.Panel):
    def __init__(self, parent,id):
	wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0 )
	sizer = wx.BoxSizer(wx.VERTICAL)
	txt_social_history = wx.TextCtrl(self, 30,
                        "Born in QLD, son of an itinerant drover. Mother worked as a bush nurse. "
                        "Two brothers, Fred and Peter. Left school aged 15yrs, apprentice fitter "
                        "then worked in industry for 10ys. At 22yrs age married Joan, two children"
                        "Peter b1980 and Rachaelb1981. Retired in 1990 due to receiving a fortune.",
                        #"previously unknown great aunt. Interests include surfing, fishing, carpentry",                       ,
                       wx.DefaultPosition,wx.DefaultSize, style=wxTE_MULTILINE|wx.NO_3D|wx.SIMPLE_BORDER)
        txt_social_history.SetInsertionPoint(0)
	txt_social_history.SetFont(wx.Font(12,wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'xselfont'))
	#self.textCtrl1.SetFont(wx.Font(14, wx.SWISS, wxNORMAL, wx.BOLD, False, 'verdana'))
        sizer.Add(txt_social_history,100,wx.EXPAND)
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
 
