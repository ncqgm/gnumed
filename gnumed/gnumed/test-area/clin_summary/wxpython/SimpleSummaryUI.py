from wxPython.wx import *

from gmSQLListControl import *
from SimpleDefaultSummaryCommandConfig  import *
from SimpleRecordDisplayPanel import *
from SimplePopupQueryResultWindow import *
from threading import *
#---------------------------------------------------------------------------

class  PopupTimer(wxTimer):
	def __init__(self, parent, query, point = wxPoint(0,0) ):
		wxTimer.__init__(self)
		self.point = point
		self.parent = parent
		self.key = 'a'+query
		print "popup query = ", query
		self.win = SimplePopupQueryResultWindow(parent, query)

	def Notify(self):
		#wxMutexGuiEnter()
		
		pos = self.parent.GetParent().ClientToScreen ( (0,0) )	
		(w,h) = self.parent.GetParent().GetSizeTuple()
		if self.point.y  > h/2:
			y = 0
		else:
			y= h/2	

		print "POPUP POSITION ", pos, (w,h), (0,y)
		
                self.win.Position((0,0),  (self.point.x /2 , self.point.y + 30))
                self.win.Show(true)
		#self.win.Centre(wxBOTH)
		#wxMutexGuiRelease()

	def Stop(self):
		wxTimer.Stop(self)
		#wxMutexGuiEnter()
		
		self.win.Show(false)
		self.win.Destroy()
		#wxMutexGuiRelease()
		 

class ClinNotesPanel(wxPanel):
		

		
	global menuCommands
	menuCommands = [ 'new', 'edit', 'delete' ]


		
	def __init__(self, parent, 
			personDetails = [ { 'name': 'nobody', 'address': 'nowhere' }] 
							, timing=200 ):

		wxPanel.__init__(self, parent, -1)
		#self.setPersonUIFactory( personUIFactory)
		self.frame = parent
		self.personDetails = personDetails
		self.createDetailsMap()
		#self.SetScrollbars( 50, 50, 20, 20)
		font = self.GetFont()
		font.SetPointSize(12)
		self.SetFont(font)
		#self.parts = [ 'soc_hx', 'phx','habits', 'meds','functional', 'allergies', 'immune', 'ix_phx',  'family_hx',  'problems' ]
		self.parts   = [ 'phx', 'habits', 'meds', 'allergies', 'ix_phx', 'family_hx', 'immune', 'soc_hx', 'problems',   'functional' ]

		heights = { 'phx': 100, 'meds' : 100, 'allergies': 40 , 'immune' : 50, 'soc_hx' : 30, 'habits' : 30,
				'family_hx' : 30 , 'functional' : 30 , 'ix_phx' : 100, 'problems' : 100 }
		widths = { 'phx': 2, 'habits': 1, 'meds': 2, 'allergies' :1, 'ix_phx' : 2, 'family_hx' : 1, 'problems' : 2, 'functional': 1, 'soc_hx' :1 , 'immune' : 2}
                self.ids = {} 
                ui = {}
		self.ui = ui
		self.menuMap = {}
		self.menuItemIdMap = {}
		self.timing = timing

		

                for x in self.parts:
			id =   wxNewId()
			self.ids[x]  = id
                        ui[x] = SQLListControl(self, self.ids[x], size=  ( 140, heights[x]) )
			#wxListCtrl( self, self.ids[x], wxDefaultPosition, (120, heights[x]), style = wxLC_LIST|wxLC_VRULES |wxLC_HRULES    ) 
			font = wxFont( 11, wxROMAN, wxNORMAL, wxLIGHT) 
			ui[x].SetFont(font)		

			self.menuItemIdMap[x] = self.createMenuItemIdMap()
			
			
			menu = self.createMenu(x,  self.menuItemIdMap[x]['to_id'] )
			self.menuMap[x] = menu
			EVT_RIGHT_DOWN( ui[x], self.doPopupMenu) 
			EVT_ENTER_WINDOW ( ui[x], self.doPopupWindow)
			EVT_LEAVE_WINDOW ( ui[x], self.doKillPopupWindow)

		self.cols = 2 
                #sizer = wxFlexGridSizer( cols = self.cols, hgap=1, vgap=1 )
		topSizer = wxBoxSizer (wxVERTICAL)
			
		detailSizers = self.getSizersWithPersonDetails( personDetails)
		#sizer = wxBoxSizer( wxHORIZONTAL)
		#for szr in detailSizers :
		#	sizer.Add( szr, 0, wxLEFT )
		innerSizer = wxBoxSizer(wxVERTICAL)
		for x in detailSizers:
			innerSizer.Add(x, 0, wxGROW)
		
		topSizer.Add( innerSizer, 0, wxALL)	
		flip = 0	
		for x in self.parts:
			if flip == 0:
				sizer = wxBoxSizer(wxHORIZONTAL )
				topSizer.Add(sizer, 1, wxGROW)
			box = wxStaticBox( self, -1, x)
			font = box.GetFont()
			font.SetPointSize(9)
			box.SetFont(font)
			bsizer = wxStaticBoxSizer( box, wxHORIZONTAL )
			bsizer.Add( ui[x],  1,   wxGROW )		
			sizer.Add( bsizer, widths[x], wxGROW | wxCENTRE ) 
			flip = (flip + widths[x]) % 3 
			

		
		self.SetSizer(topSizer)
		sizer.Fit(self)
        	self.SetAutoLayout(true)

		EVT_SIZE( self,  self.OnActivate)

		#for x in self.parts:
		#	ui[x].InsertStringItem(1, 1,x)

		self.timers = {}
		self.uiLock = Semaphore() 
	def createDetailsMap(self, list = None):
		if list == None:
			list = self.personDetails
		map = {}
		for x in list:
			map [x['name']] = x['value']
		self.detailsMap = map

	# added for persistent screens
	
	def setPersonDetails(self, detailsList):
		for x in detailsList:
			name = x['name']
			try:
				ui = self.detailsUI[name]
				ui.SetLabel(str(x['value']))
			except Exception , errorStr:
				print "in ClinPanel.SetPersonDetails ", errorStr
 
		self.personDetails = detailsList
		self.createDetailsMap()
		self.refreshAll()
		self.Fit()

	def getSizersWithPersonDetails(self, personDetails):
		szlist = []
		flip = 0
		hsizer = wxBoxSizer( wxHORIZONTAL )
		szlist.append(hsizer)
		dummy = wxStaticText(self, -1, '   ')
		self.detailsUI = {}
		for x in personDetails:
			label = wxStaticText( self, -1, x['name'], size = (30,-1) )
			val = wxStaticText(self, -1, str(x['value']) , size = (30, -1))
			self.detailsUI[x['name']]= val
			font = label.GetFont()
			font.SetPointSize(10)
			val.SetFont(font)
			label.SetFont(font)
			hsizer.Add( label,0, 0)
			hsizer.Add( dummy, 0, 0)
			hsizer.Add(val,1,  wxEXPAND)
			hsizer.Add( dummy, 0, 0)
			flip = (flip + 1) % 3 
			if flip == 0 :
				hsizer = wxBoxSizer(wxHORIZONTAL)
				szlist.append(hsizer)
		return szlist 

	def doPopupWindow( self, event):
		event.Skip()
		listctrl = event.GetEventObject()
		query = listctrl.GetQueryStr()
		key = 'a'+str(query)
		if self.uiLock.acquire(0) :
			if not self.timers.has_key(key) or  self.timers[key] == None:
				self.timers[key] = PopupTimer(listctrl, query, listctrl.ClientToScreen(event.GetPosition()) )
				self.timers[key].Start(self.timing, true)
			self.uiLock.release()

	def doKillPopupWindow( self, event):
		key ='a'+ str( event.GetEventObject().GetQueryStr())

		if self.uiLock.acquire(0) :
			if self.timers.has_key(key) and self.timers[key] != None:			
				self.timers[key].Stop()
				self.timers[key] = None
			self.uiLock.release()

	def doPopupMenu(self, event):
		ctrl =  event.GetEventObject()
		print "popup " , ctrl
		id = event.GetId()
		
		ctrl.PopupMenu(self.menuMap[self.getCtrlName(ctrl)], event.GetPosition() )


	def doPartsMenuCommand( self, event):
		part = self.getPartForMenu(event.GetEventObject())
		id =  event.GetId()
		cmdKey =  self.menuItemIdMap[part]['to_key'][id] 

		print "menu command",event.GetString(), event.GetEventObject(), id, " part = ", part 
		print "command = ", cmdKey

		cmd = self.cmdMap[part][cmdKey]

		print "found command = ", cmd
		event.SetEventObject( self.ui[part] )
		cmd.execute(event,  self.detailsMap['id'])
				 
		
	def getPartForMenu( self, menu):
		for x in self.menuMap:
			if self.menuMap[x] == menu :
				return x
		return ""
	def getCtrlName(self, ctrl):
		for x in self.ui.keys():	
			if self.ui[x] == ctrl:
				return x
		return x
			
	def createMenuItemIdMap(self) :
		map  =  {}
		map['to_id'] = {}
		map['to_key'] = {}
		for k in menuCommands:
			id = wxNewId()
			map['to_id'][k] = id
			map['to_key'][id] = k	
		return map	

	def createMenu (self,  name, map):
		menu = wxMenu()
		for k  in menuCommands:
			menu.Append( map[k], "%s %s"% (k, name))
			EVT_MENU( self.ui[name], map[k], self.doPartsMenuCommand)
			 
		return menu


	def setCommandMap( self, map):
		self.cmdMap = map
	

	def OnActivate(self, event):
		event.Skip()
		self.refreshAll()
		return 0 

	def refreshAll(self):
		for x in self.parts:	
			try:
				subMap = self.cmdMap[x]
				cmd = subMap['refresh']
				ui = self.ui[x]
				cmd.execute(ui, self.detailsMap['id'] )		
			except Exception, errorStr:
				print "exception in refreshAll on part ", x, errorStr	

	def setPersonUIFactory(self, factory):
		self.personUIFactory = factory

	def getPersonUIFactory(self):
		return self.personUIFactory

		
#---------------------------------------------------------------------------
class TestApp(wxApp):

        def OnInit(self):
                frame = wxFrame( None, -1, "Test Summary Sheet", size = (510, 600) )
		personDetails = [ { 'name': 'person name', 'value' : 'harry smith' } ]
                win =  ClinNotesPanel( frame, personDetails)
		DefaultSummaryCommandConfig().configure(win)
                frame.Show()
                return true

if __name__ == "__main__":
        app = TestApp( )
        app.MainLoop()

