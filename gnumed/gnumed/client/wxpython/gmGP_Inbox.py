try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from gmListCtrlMapper import *
try:
	from Gnumed.pycommon import gmLog
except:
	sys.path.append('../pycommon')
	import gmLog

Inboxdata = {
1 : ("Pathology", "5 unread results (Douglas Pathology)"),
2 : ("Radiology", "1 Xray of femur (Newcastle radiology)"),
3 : ("", "Head CT (Hunter Diagnostic Imaging)"),
4 : ("Internal Mail ", "from practice nurse - non urgent"),
}
ID_INBOX = wx.NewId()

class Inbox(wx.Panel):
    def __init__(self, parent,id):
	wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, 0 )
	list_inbox = wx.ListCtrl(self, ID_INBOX,  wx.DefaultPosition, wx.DefaultSize,wx.LC_REPORT|wx.LC_NO_HEADER|wx.SUNKEN_BORDER)
	list_inbox.InsertColumn(0, "From")
	list_inbox.InsertColumn(1, "Message", wx.LIST_FORMAT_LEFT)
	self.list_inbox = list_inbox
	self.lc_mapper = gmListCtrlMapper(self.list_inbox)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	self.SetData( Inboxdata)

	list_inbox.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        list_inbox.SetColumnWidth(1, wx.LIST_AUTOSIZE)
	sizer = wx.BoxSizer(wx.VERTICAL)
	sizer.Add(list_inbox,100,wx.EXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(True)                 #tell frame to use the sizer
        #self.Show(True) 

	print self.GetData() 

    def SetData( self, map):
	self.lc_mapper.SetData( map)

    def GetData(self):
	return self.lc_mapper.GetData()
	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(Inbox, -1)
	app.MainLoop()

#===========================================================
# $Log: gmGP_Inbox.py,v $
# Revision 1.10  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.9  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.8  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.7  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.6  2004/06/20 16:01:05  ncq
# - please epydoc more carefully
#
