from wxPython.wx import *

class SimpleEntryException ( Exception):
	pass

class SimpleRecordPanel(wxPanel):
	"""use this to create a prototype Form entry:
	pass in a list of   maps with name, value, size as keys.
	 "name" is the name of the field.
	 "size" is the key to a size value, 
	and "value" is the value to initially display.
	The default GUI element is a wxTextCntrl for each field.
	Call doSimpleRecordDialog for a modal record entry. 
	If Ok is pressed , an updated list with the new values is returned
	otherwise the old list is returned.
	"""


	def __init__(self, parent = None, frame = None, list = [], isHorizontal = 0):

		wxPanel.__init__(self, parent, 0)
#DEBUG		
		print "SimpleRecordPanel list =", list

		self.BUT_OK_ID = wxNewId()
		self.BUT_CANCEL_ID = wxNewId()

		self.frame = frame
		self.list = list
		self.uiMap = {}
		self.isHorizontal = isHorizontal

		if isHorizontal:
			sizer = wxFlexGridSizer( cols = len(list), hgap=6, vgap=6)	
		else:	
			sizer = wxFlexGridSizer( cols = 3, hgap=6, vgap=6)
		
#hacked this in
###

		
		labelMap = {}		## for horizontal layout
			
		for x in self.list:
			label = wxStaticText(self, -1, x['name'])
			sz = None 
			val = None
			try:
				sz = x['size']
			except:
				pass
			try:
				val = x['value']
			except:	
				pass
			if sz == None or sz < 100: 
				sz = 100
			if val == None :	
				val = ''
			if x.has_key('multiline') :
				extraStyle = wxTE_MULTILINE
				extent = parent.GetFullTextExtent('M')

				ysize = x['multiline'] * ( extent[1] + extent[2]  )	
			else:
				extraStyle = 0
				ysize = -1
		
			print "CREATING entry for SimpleRecordPanel size = ", (sz, ysize), "style = ", extraStyle

			entry = wxTextCtrl( self, -1, val, size = (sz ,ysize), style = extraStyle)

			self.uiMap[x['name']] = entry
			labelMap[x['name']] = label
			if not self.isHorizontal  :
				sizer.AddMany ( [label, (entry, 1, wxGROW) , (0,0)] )		

		if self.isHorizontal  :
			for x in self.list:
				sizer.AddMany( [labelMap[x['name']] ] )
			for x in self.list:
				sizer.AddMany ( [self.uiMap[x['name']]] )	
				
		

		buttonOK = wxButton(self, wxID_OK,     " OK ", size =  wxDefaultSize)
	        buttonCancel = wxButton(self, wxID_CANCEL, " Cancel ",size =  wxDefaultSize)
		sizer.AddMany( [ buttonOK, buttonCancel, (0,0) ])
		self.SetSizer(sizer)
		self.SetAutoLayout(true)
		sizer.Fit( parent)

	def getNewMap(self):
		newMap = {}
		for x in self.list:
			entry = self.uiMap[x['name']]
			val = entry.GetValue()
			newMap[x['name']] = val 

		return newMap			

	
	def getOldMap(self):
		oldMap = {}
		for x in self.list:
			oldMap[x['name']]= x['value']
		return oldMap 
			

def doSimpleDialog(frame, list, factory = None):
#cut and paste from sample.wxDialog
    win = wxDialog(frame, -1, "This is a wxDialog", wxDefaultPosition,size=(-1,350),  style=wxRESIZE_BORDER | wxSTAY_ON_TOP)
    if factory == None:
	print "no factory found"
    	panel = SimpleRecordPanel( win, frame, list)
    else:
	print " ** creating a factory"
	panel = factory.getUI( win, -1, [ frame, list ] )

    val = win.ShowModal()

    if val == wxID_OK:
	return panel.getNewMap()
    else:
	raise SimpleEntryException	
	

class TestApp(wxApp):
	def __init__(self):
                wxApp.__init__(self, 0)

        def OnInit(self):
                frame = wxFrame(None, -1, "Test Simple Record Entry", size=(500,400) )
                self.SetTopWindow(frame)
                self.frame= frame
                frame.Show(true)
		list = [ {"name": "name",   "size": 200, "value" : "John"},
			{ "name": "address" , "size": 300, "value":"17 Peel"},
			{ "name" : "phone" ,  "size" : 200, "value": "9911081" } ] 
		print doSimpleDialog( frame, list ) 
                return true

if __name__ == "__main__":
	app=TestApp()
	app.MainLoop()          
	
