from wxPython.wx import *
from gmListCtrlMapper import *
try:
	import gmLog
except:
	sys.path.append('../pycommon')
	import gmLog
	
Inboxdata = {
1 : ("Pathology", "5 unread results (Douglas Pathology)"),
2 : ("Radiology", "1 Xray of femur (Newcastle radiology)"),
3 : ("", "Head CT (Hunter Diagnostic Imaging)"),
4 : ("Internal Mail ", "from practice nurse - non urgent"),
}
ID_INBOX = wxNewId()
class Inbox(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	list_inbox = wxListCtrl(self, ID_INBOX,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
	list_inbox.InsertColumn(0, "From")
	list_inbox.InsertColumn(1, "Message", wxLIST_FORMAT_LEFT)
	self.list_inbox = list_inbox
	self.lc_mapper = gmListCtrlMapper(self.list_inbox)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	self.SetData( Inboxdata)

	list_inbox.SetColumnWidth(0, wxLIST_AUTOSIZE)
        list_inbox.SetColumnWidth(1, wxLIST_AUTOSIZE)
	sizer = wxBoxSizer(wxVERTICAL)
	sizer.Add(list_inbox,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        #self.Show(true) 

	print self.GetData() 

    def SetData( self, map):
	self.lc_mapper.SetData( map)

    def GetData(self):
	return self.lc_mapper.GetData()
	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(Inbox, -1)
	app.MainLoop()
