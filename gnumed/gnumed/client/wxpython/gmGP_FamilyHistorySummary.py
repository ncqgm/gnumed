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
class FamilyHistorySummary(wx.Panel):
    def __init__(self, parent,id):
	wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0 )
	sizer = wx.BoxSizer(wx.VERTICAL)
	txt_family_history = wx.TextCtrl(self, 30,
                        "FAMILY HISTORY: Stroke(father-died72yrs);NIDDM(general - maternal).\n",
                         wx.DefaultPosition,wx.DefaultSize, style=wxTE_MULTILINE|wx.NO_3D|wx.SIMPLE_BORDER)
        txt_family_history.SetInsertionPoint(0)
	txt_family_history.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.NORMAL, False,'xselfont'))
	txt_family_history.SetForegroundColour(wx.Colour(1, 1, 255))
        sizer.Add(txt_family_history,100,wx.EXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(True)                 #tell frame to use the sizer
        #self.Show(True) 
	self.text = txt_family_history

	print self.GetValue()
	

    def GetValue(self):
	    return self.text.GetValue()

    def SetValue(self, val):
	    self.text.SetValue(val)

   
	
if __name__ == "__main__":
    app = wxPyWidgetTester(size = (400, 100))
    app.SetWidget(FamilyHistorySummary, -1)
    app.MainLoop()
 
