from wxPython.wx import *
from gmSQLSimpleSearch import SQLSimpleSearch, ID_COMBO_SEARCHEXPR
import gettext
_ = gettext.gettext

ID_BUTTON_SELECT = wxNewId()
ID_BUTTON_ADD = wxNewId()
ID_BUTTON_NEW = wxNewId()
ID_BUTTON_MERGE = wxNewId()
ID_BUTTON_EDIT = wxNewId()
ID_LISTCTRL = wxNewId()

class DlgSelectPerson(SQLSimpleSearch):
	"The central dialog interface to all person related queries"

	def __init__(self, parent, id,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL, service = 'demographica' ):

		SQLSimpleSearch.__init__(self, parent, id, pos, size, style, service)
		#add a bottom row sizer to hold a few buttons
		self.sizerButtons = wxBoxSizer( wxHORIZONTAL )
		#add a "select patient" button
		self.buttonSelect = wxButton( self, ID_BUTTON_SELECT, _("&Select"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonSelect, 0, wxALIGN_CENTRE|wxALL, 2 )
		#edit this patient
		self.buttonEdit = wxButton( self, ID_BUTTON_EDIT, _("&Edit"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonEdit, 0, wxALIGN_CENTRE|wxALL, 2 )
		#add a new patient
		self.buttonNew = wxButton( self, ID_BUTTON_NEW, _("&New"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonNew, 0, wxALIGN_CENTRE|wxALL, 2 )
		#add patient to this family / address button
		self.buttonAdd = wxButton( self, ID_BUTTON_ADD, _("&Add"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonAdd, 0, wxALIGN_CENTRE|wxALL, 2 )
		#merge two or more atient entries into one
		self.buttonMerge = wxButton( self, ID_BUTTON_MERGE, _("&Merge"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonMerge, 0, wxALIGN_CENTRE|wxALL, 2 )

		self.sizerTopVertical.AddSizer( self.sizerButtons, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 2 )

		self.init_datalinks()


#---------------------- added this stuff
	def init_datalinks(self):
		
		# human readable "xxxPerson" string mapping
		self.cmdId_map = { ID_BUTTON_SELECT:"selectPerson", ID_BUTTON_ADD: "addPerson", ID_BUTTON_NEW:"newPerson",
		ID_BUTTON_MERGE:"mergePerson", ID_BUTTON_EDIT:"editPerson" }

		for x in self.cmdId_map.keys():
			EVT_BUTTON(self,  x, self.doCommand)
		
		#EVT_CHAR( self.comboSearchExpr, self.onComboKey)
		EVT_TEXT( self, ID_COMBO_SEARCHEXPR, self.onComboText)
                EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self.OnSearchResultItemActivated)

		

		self.commandMap = {}
		self.sqlcmd = ""

	def onComboKey( self,  ke):
		print "got " , ke.KeyCode()
		ke.Skip()

	def onComboText(self, event):
		print "got " , event.GetString()
		self.prefix = event.GetString()
		try:
			command = self.commandMap["searchPerson"]
			print "onComboText found ", command
			command.execute( self.prefix, self)
		except Exception , errorStr:
			print "search command failed with " , Exception ,errorStr

	
	def GetSelectedRow(self):
		text = self.listctrlSearchResults.GetSelectedRow()
		print "selected row is ", text
		return text

	def GetSelectedList(self):
		values = self.GetSelectedRow()
		labels = self.GetLabels()
		selList = []
		for i in range (0, len(labels)):
			selList.append( { 'name': labels[i], 'value': values[i] } ) 
		return selList 


	def update(self):
		self.updateList()

	def updateList(self, sqlcmd = ""):
		if sqlcmd != "":
			self.sqlcmd = sqlcmd
		else:
			sqlcmd = self.sqlcmd
		self.listctrlSearchResults.SetQueryStr(sqlcmd)
		self.listctrlSearchResults.RunQuery()

	def getCommands(self):
		return self.commandMap

	def setCommands(self, commandMap):
		self.commandMap = commandMap
		print "command map set to ", commandMap

	def addCommand( self, key, command):
		self.commandMap[key] = command
		print "this command added to select person = ", key, command
		
	
	def doCommand( self,  event):
		id = event.GetId()
		event.SetEventObject(self)
		strCmd = ""
		try:
			strCmd = self.cmdId_map[id]
			command = self.commandMap[strCmd]
			print "trying to execute ", command
			command.execute( event, self)	
		except Exception ,errorStr:
			print strCmd, " command failed with " , Exception ,errorStr


	def OnSearchResultItemActivated(self, event) :
		data = self.GetSelectedList()
		command = self.commandMap["enterNotes"]
		print " before command.execute",  data, command
		command.execute( event, self)		

	
#------------------------------ end of changes 19/03/2002

	def TransformQuery(self, searchexpr):
		"'virtual' function of the base class, adjusted to the needs of this dialog"
		selectclause = "select * from v_selectperson"
		orderclause = "order by surname, firstnames"
		if self.checkboxCaseInsensitive.GetValue():
			whereclause = "where (surname ~* '%s')" % searchexpr
		else:
			whereclause = "where (surname like '%s')" % searchexpr

            	query = "%s %s %s ;" % (selectclause, whereclause, orderclause)
		#print query


	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(DlgSelectPerson, -1)
	app.MainLoop()

