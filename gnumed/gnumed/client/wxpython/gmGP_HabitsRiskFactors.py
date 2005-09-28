try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

class HabitsRiskFactors(wx.Panel):
    def __init__(self, parent,id):
	wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0 )
	sizer = wx.BoxSizer(wx.VERTICAL)
	
	#captions for the two columns
	#habit_caption = gmTerryGuiParts..cDividerCaption(self,-1,"Habits")
	#risk_caption = gmTerryGuiParts.cDividerCaption(self,-1,"Risk Factors")
	
	#text controls for each column      
	txt_habits = wx.TextCtrl(self, 30,
                        "Smoker - 30/day.\n"
			"Alcohol - 30gm/day (Previously very heavy.\n",
                              wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wx.NO_3D|wx.SIMPLE_BORDER)
	txt_habits.SetInsertionPoint(0)
	
	txt_riskfactors = wx.TextCtrl(self,30,
			     "Hypercholesterolaemia \n"
			     "Current Smoker \n"
			     "NIDDM \n"
                             "No exercise data recorded\n",
			      wxDefaultPosition,wx.DefaultSize, style = wx.TE_MULTILINE)
	txt_riskfactors.SetInsertionPoint(0)
	#heading sizer- add headings
	#heading_sizer = wxBoxSizer(wxHORIZONTAL)
	#heading_sizer.Add(habit_caption,1,wxEXPAND)
	#heading_sizer.Add(risk_caption,1,wxEXPAND)
	#self.SetSizer(heading_sizer)  #set the sizer 
	#heading_sizer.Fit(self)             #set
	##text sizer - add text
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
	text_sizer.Add(txt_habits,1,wx.EXPAND)
	text_sizer.Add(txt_riskfactors,1,wx.EXPAND)
	self.SetSizer(text_sizer)  #set the sizer 
	text_sizer.Fit(self)             #set
	self.SetAutoLayout(True)                 #tell frame to use the sizer
        #self.Show(True)
	
	self.lists = { 'habit': txt_habits, 'risk': txt_riskfactors }

	print self.GetData()

	self.SetData( { 'habit': ['smoker', 'drinks 20/day'] , 'risk': [ 'cholesterol', 'diabetes'] } )

    def getTextCtrl(self, which):
		return self.lists.get(which, "risk")

    def SetData(self, map):
		for which, data in map.items():
			if type(data) == type(""):
				self.lists.get(which, 'risk').SetValue(data)
			
			if type(data) in [ type([]), type ( () ) ]:
				self.lists.get(which, 'risk').SetValue("\n".join(data))
	
    def GetData(self):
		map = {}
		for k in self.lists.keys():
			map[k] = self.lists[k].GetValue().split('\n')
		return map

	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(HabitsRiskFactors, -1)
	app.MainLoop()
 
