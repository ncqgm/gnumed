from wxPython.wx import *

#--------------------------------------------------------------------
# A class for displaying patients active problems
# This code is shit and needs fixing, here for gui development only
# TODO: almost everything
#--------------------------------------------------------------------
class ActiveProblems(wxPanel):
	def __init__(self, parent,id):
		wxPanel.__init__(
			self,
			parent,
			id,
			wxDefaultPosition,
			wxDefaultSize,
			0
		)
		activeproblemsamplelist = ['1980 Hypertension','1982 Acute myocardial infartion', '1992 NIDDM', "another list"]
		sizer = wxBoxSizer(wxVERTICAL)
		activeproblems_listbox = wxListBox(
			self,
			-1,
			wxDefaultPosition,
			wxDefaultSize,
			activeproblemsamplelist,
			wxLB_SINGLE
		)
		sizer.Add(activeproblems_listbox,100,wxEXPAND)
		activeproblems_listbox.SetBackgroundColour(wxColor(255,255,197))
		activeproblems_listbox.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.SetSizer(sizer)  #set the sizer 
		sizer.Fit(self)             #set to minimum size as calculated by sizer
		self.SetAutoLayout(true)                 #tell frame to use the sizer
        #self.Show(true) 
		self.list = activeproblems_listbox
		self.data = None

		print self.getLabels()
		

	def getListBox(self):
		return self.list

	def setData(self, labels, data = None):
		self.list.Clear()
		for x in labels:
			self.list.Append(x)
		self.data  = data	
		
		
	def getLabels(self):
		c = self.list.GetCount()
		list = []
		for i in xrange(0, c):
			list.append(self.list.GetString(i) )
		return list	
			
		
	def getData(self):
		return self.data

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 100))
	app.SetWidget(ActiveProblems, -1)
	app.MainLoop()
