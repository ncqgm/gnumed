#############################################################################
#
# gmMedGPTabbedLists :convenience widget that displays a notebook widget
#                     notebook pages contain lists of information needed in
#                     in everyday general practice consultation
#                     eg patients scripts, referral letters, inbox
#                     recalls, measurements etc
# Description of Gui: the background panel contains:
#                     - wxWindow as a shadow behind the wxNotebook
#                     - a wxNotebook wigit to hold the lists
#                     - lists as needed
#                     
# ---------------------------------------------------------------------------
#
# @author: Dr. Richard TEry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies:
# @change log:
#	25.05.2002 rterry first draft, untested
#
# @TODO: Almost everything
#        Why arn't the lists showing on the tabs 
#        Allow user configuration of which pages to display
#        Make icons on tabs user configurable
#        ?can cursor tool tip change when hovered over bitmap on a tab?
#        remove non-used imports from below this text
############################################################################
from wxPython.wx import *
from wxPython.gizmos import *
from wxPython.stc import *
import keyword
import time
import images                                #bitmaps for column headers of lists
import images_gnuMedGP_TabbedLists           #bitmaps for tabs on notebook
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

#--------------------------------------------------
#Dummy data to simulate previously prescribed items
#--------------------------------------------------
scriptdata = {
1 : ("Adalat Oris", "1 mane","21/01/2002", "Hypertension","30 Rpt5","29/02/2000"),
2 : ("Nitrolingual Spray", "1 spray when needed","24/08/2001", "Angina","1 Rpt2","01/06/2001"),
3 : ("Losec", "1 mane", "21/01/2002","Reflux Oesophagitis","30 Rpt5","16/11/2001"),
4 : ("Zoloft", "1 mane", "24/04/2002","Depression","30 Rpt0","24/04/2002"),
}

class TabbedLIsts(wxPanel, wxColumnSorterMixin):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id)
	self.SetAutoLayout(true)
	self.SetBackgroundColour(wxColour(192,192,192))                              #panel background is grey
	#-----------------------------------------------------
	#create imagelist for use by the lists in the notebook
	#e.g the icons to sort the columns up and down
	#-----------------------------------------------------
	self.ListsImageList= wxImageList(16,16)
	self.small_arrow_up = self.ListsImageList.Add(images.getSmallUpArrowBitmap())
        self.small_arrow_down = self.ListsImageList.Add(images.getSmallDnArrowBitmap())
	#------------------------------------------------------------------------
	#Contruct the background shadow which gives 3D effect to the summary page
	#------------------------------------------------------------------------
	self.backshadow =wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 
                           0)                                                        #shadow behind summary panel 
	self.backshadow.SetBackgroundColour(wxColour(131,129,131))                   #is a darker gray then main panel
	#----------------------------------------------------------------------
	#Add a notebook control to hold the lists of things eg scripts, recalls
	#----------------------------------------------------------------------
	self.notebook1 = wxNotebook(self, -1, wxDefaultPosition, wxDefaultSize, style = 0)
	#-------------------------------------------------------------------------
	#Associate an imagelist with the notebook and add images to the image list
	#-------------------------------------------------------------------------
	tabimage_Script = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = -1
        self.notebook1.il = wxImageList(8, 8)
        tabimage_Script = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ScriptBitmap())
        tabimage_Requests = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RequestsBitmap())
	tabimage_Measurements = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_MeasurementsBitmap())
	tabimage_Referrals = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ReferralsBitmap())
	tabimage_Recalls = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RecallsBitmap())
	tabimage_Inbox = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_Letters_ReceivedBitmap())
	self.notebook1.SetImageList(self.notebook1.il)
	#-----------------------------------------------------------------------------
	# Set the layout constraints for the notebook relative to the back panel first
	#-----------------------------------------------------------------------------
	lc = wxLayoutConstraints()
	lc.top.SameAs(self, wxTop,7)
	lc.left.SameAs(self, wxLeft,7)
        lc.width.PercentOf(self, wxWidth,95)
        lc.height.PercentOf (self, wxHeight,95)
	self.notebook1.SetConstraints(lc);
	#----------------------------------------------------------------------------------
	#now create the lists that will sit on the notebook pages, and add them to the page
	#----------------------------------------------------------------------------------
	ListScript_ID = wxNewId()
       	self.List_Script = wxListCtrl(self.notebook1, ListScript_ID,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
	self.List_Requests = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Measurements = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Referrals = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Recalls = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Inbox = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Script, pPage = self.List_Script, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Requests, pPage = self.List_Requests, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Measurements, pPage = self.List_Measurements, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Referrals, pPage = self.List_Referrals, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Recalls, pPage = self.List_Recalls, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Inbox, pPage = self.List_Inbox, strText = '')
        self.notebook1.SetSelection(0)                               #start on scriptpage
	#--------------------------------------
	#Now lets do things to the script list:
	#--------------------------------------
	self.List_Script.SetImageList(self.ListsImageList, wxIMAGE_LIST_SMALL)
	#------------------------------------------------------------------------
	# since we want images on the column header we have to do it the hard way
	#------------------------------------------------------------------------
	info = wxListItem()
	info.m_mask = wxLIST_MASK_TEXT | wxLIST_MASK_IMAGE | wxLIST_MASK_FORMAT
	info.m_image = -1
	info.m_format = 0
	info.m_text = "Drug"
	self.List_Script.InsertColumnInfo(0, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Instructions"
	self.List_Script.InsertColumnInfo(1, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Last Date"
	self.List_Script.InsertColumnInfo(2, info)
	
	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Prescribed For"
	self.List_Script.InsertColumnInfo(3, info)
	
	
	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Quantity"
	self.List_Script.InsertColumnInfo(4, info)
	
	
	info.m_format = 0
	info.m_text = "First Date"
	self.List_Script.InsertColumnInfo(5, info)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = scriptdata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1],data[2]
	    self.List_Script.InsertStringItem(x, data[0])
            self.List_Script.SetStringItem(x, 1, data[1])
            self.List_Script.SetStringItem(x, 2, data[2])
	    self.List_Script.SetStringItem(x, 3, data[3])
	    self.List_Script.SetStringItem(x, 4, data[4])
	    self.List_Script.SetStringItem(x, 5, data[5])
	    self.List_Script.SetItemData(x, key)
	#--------------------------------------------------------
	#note the number pased to the wxColumnSorterMixin must be
	#the 1 based count of columns
	#--------------------------------------------------------
        self.itemDataMap = scriptdata        
        wxColumnSorterMixin.__init__(self, 5)              #I excluded first date as it didn't sort
	
	self.List_Script.SetColumnWidth(0, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(1, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(2, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(3, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(4, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(5, 150)
	#-------------------------------------------------
	#Just for display purposes, add some dummy entries
	#-------------------------------------------------
	lc = wxLayoutConstraints()
	lc.top.SameAs(self.notebook1, wxTop,0)
	lc.left.SameAs(self.notebook1, wxLeft,0)
        lc.width.SameAs(self.notebook1, wxWidth)
        lc.height.PercentOf (self.notebook1, wxHeight,100)
	self.List_Script.SetConstraints(lc);
	#--------------------------------------------------------------------------
	#Now set the layout constraints for the backshadow relative to the notebook
	#as this shadow sits lower than the tabs
	#I've left his code here and not at the top because I want the shadow to
	#start below the tab level and stay in proportion but it didn't work
	#TODO:this this later
	#--------------------------------------------------------------------------
     	lc = wxLayoutConstraints()                                                     
	lc.top.SameAs(self, wxTop,15)
	lc.left.SameAs(self,wxLeft,15)
        lc.width.PercentOf(self, wxRight, 95)
        lc.height.PercentOf(self,wxHeight,95) 
	self.backshadow.SetConstraints(lc);
	
	EVT_LIST_COL_CLICK(self, ListScript_ID, self.OnColClick)

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.List_Script

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.small_arrow_down, self.small_arrow_up)
    
    def OnColClick(self, event):
	print  "OnColClick: %d\n" % event.GetColumn()
        #self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (475, 320))
	app.SetWidget(TabbedLIsts, -1)
	app.MainLoop()
