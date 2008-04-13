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
# @author: Dr. Richard Terry
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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_TabbedLists.py,v $
# $Id: gmGP_TabbedLists.py,v 1.21 2008-04-13 14:39:49 ncq Exp $
__version__ = "$Revision: 1.21 $"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx
	#from wxPython.gizmos import *
	#from wxPython.stc import *

import keyword
import time
import images #bitmaps for column headers of lists
import gmPlugin, gmShadow
#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin
import zlib, cPickle


scriptdata = {
1 : ("Adalat Oris", "30mg","1 mane","21/01/2002", "Hypertension","30 Rpt5","29/02/2000"),
2 : ("Nitrolingual Spray","", "1 spray when needed","24/08/2001", "Angina","1 Rpt2","01/06/2001"),
3 : ("Losec", "20mg","1 mane", "21/01/2002","Reflux Oesophagitis","30 Rpt5","16/11/2001"),
4 : ("Zoloft", "50mg","1 mane", "24/04/2002","Depression","30 Rpt0","24/04/2002"),
}

#=====================================================================
class Notebook(wxNotebook):
    """ sets tooltips for notebook tab images """

    tip_shown=0
    def __init__(self, parent, id):
        wxNotebook.__init__(self,parent,id)

	# tool tips activated in...
        self.tip_area1=wxRect(2,2,30,30)
        self.tip_area2=wxRect(32,2,31,30)
        self.tip_area3=wxRect(63,2,31,30)
        self.tip_area4=wxRect(94,2,31,30)
        self.tip_area5=wxRect(125,2,31,30)
        self.tip_area6=wxRect(156,2,31,30)

	EVT_MOTION(self, self.OnMouseMotion)
        EVT_LEFT_DOWN(self, self.OnLeftDown)

    def OnMouseMotion(self, evt):
	pt_local = self.GetPosition()
	#print 'x_local', pt_local.x, 'y_local', pt_local.y		#test
	pt_global = self.ClientToScreen(pt_local)
	#print 'x_global', pt_global.x, 'y_global', pt_global.y		#test

	x, y = evt.GetPosition()					# clean-up --- pt_local = x,y (?)
        if(self.tip_area1.Inside(wxPoint(x,y))):
            if(self.tip_shown!=1):
                tipwin1=wxTipWindow(self, _('Prescriptions'))
                tipwin1.SetBoundingRect(wxRect(1+pt_global.x,1+pt_global.y,30,30))
                pt=wxPoint((1+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin1.Move(pt) # position tool tip
                self.tip_shown=1 # avoid tool tip flashing

        elif(self.tip_area2.Inside(wxPoint(x,y))):
            if(self.tip_shown!=2):
                tipwin2=wxTipWindow(self, _('Requests'))
                tipwin2.SetBoundingRect(wxRect(32+pt_global.x,1+pt_global.y,31,30))
                pt=wxPoint((32+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin2.Move(pt)
		self.tip_shown=2

        elif(self.tip_area3.Inside(wxPoint(x,y))):
            if(self.tip_shown!=3):
                tipwin3=wxTipWindow(self, _('Measurements'))
                tipwin3.SetBoundingRect(wxRect(63+pt_global.x,1+pt_global.y,31,30))
                pt=wxPoint((63+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin3.Move(pt)
                self.tip_shown=3

        elif(self.tip_area4.Inside(wxPoint(x,y))):
            if(self.tip_shown!=4):
                tipwin4=wxTipWindow(self, _('Referrals'))
                tipwin4.SetBoundingRect(wxRect(94+pt_global.x,1+pt_global.y,31,30))
                pt=wxPoint((94+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin4.Move(pt)
                self.tip_shown=4

        elif(self.tip_area5.Inside(wxPoint(x,y))):
            if(self.tip_shown!=5):
                tipwin5=wxTipWindow(self, _('Recalls and Reviews'))
                tipwin5.SetBoundingRect(wxRect(125+pt_global.x,1+pt_global.y,31,30))
                pt=wxPoint((125+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin5.Move(pt)
                self.tip_shown=5

        elif(self.tip_area6.Inside(wxPoint(x,y))):
            if(self.tip_shown!=6):
                tipwin6=wxTipWindow(self, _('Inbox'))
                tipwin6.SetBoundingRect(wxRect(156+pt_global.x,1+pt_global.y,31,30))
                pt=wxPoint((156+pt_global.x+4+5), (1+pt_global.y+32+4))
                tipwin6.Move(pt)
                self.tip_shown=6
        else:
            self.tip_shown=0

    def OnLeftDown(self,evt):		# have fix clicking problem - make tab select a single click
	pass
	#self.tipwin1.destroy()  	# ???

class TabbedLists(wxPanel): #, wxColumnSorterMixin):
    """ a panel to hold the tabbed list """
    __icons_script = {"""icon_Rx_symbol""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"c\x05Cu\xae\xc4`u=\x85d\x05e\x03 p\xb3\x00\
\xf3#@|\x0b\x03\x10\x04\xf3\x15\x80|\xbf\xfc\xbcT(\x07\x15\xe0\x15\xd4\x83\
\x00t\xc1\x08 \x80\x8a"\t\xc2I\xb2\x04\xc1 "\x82R\x8b\x80\x08UP\x01b,\xdc\
\x9b\x10+\x14\xc0\xa6\xa2\xf9\x1d\xa8\x0eI;\x02DD\xe0\x0c%=\x00D|Hk'}

    __icons_requests = {"""icon_blood_sample""": "x\xdau\x8f\xbd\n\xc3 \x10\x80\xf7<\xc5A\x94\x14\x04Qh\x89c0\xe0\x98\x1b\xb2\
\xb8\x96\xd2\xad\xf4\xfa\xfeS\x8d?\xe0\x05r\xdb\xf7\xdd\xff\xed\xf3\xb3\xc3>\
\xd9;\xd8\x07X\x03v\x1a\x9e\xfb$\xe1\x05cp&Ef<\xd8;\xbfz\x97y<xv\xf3Z\xf3K\
\xa9\x0f\x8d!\xf1F\xdfw\x06\xdd\x86\x85\xd2\x1cK\xb31sa\xd5\x9ak^\xb4|\x1dFm\
Y\xad\x07\x16'\xa5\xf5YE\x9d\x1cS\x84xR\x84JE\xa6R\r\x12\x1bO\xb8(b\x1b\x93\
\xc1\x91\x1dABJ\xc1\xee\xeaLU\xbd\xa9\xaa7M\tq\xf9\xe3\xb5\xd2\x7fZ\x8fVi"}

    __icons_measurements = {"""icon_Set_Square""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"S\x05Cu\xae\xc4`\xf5|\x85d\x05\xa7\x9c\xc4\
\xe4l0O\x0f\xc8S6\xb70w60\x00\xf3#@|7\x0b7\x18_\x01\xc8\xf7\xcb\xcfK\x05s\
\xfca\x8a\xcd-\xa0\x92\n\nz\x11\x11z\nP\x80,\x98\x8fEP/\x9f\xb0\xca|4\x00qe\
\x04*\x84\n\xa2\x02\xdc\x82\xfe@\x90\xaf\xa7\x97\xef\x0f\x05\xd4p\'\xf5U\xea\
\x01\x00\xd2 _\x1b'}

    __icons_referrals = {"""icon_writing_pen""": "x\xda\x8d\x901\x0b\xc3 \x10F\xf7\xfc\n\xa1\x83\x85\xc0\x87Y\xa2\xb3B\xc6:d\
\xb95\x84N\r\xb5\xff\x7f\xaa9-\xd4K\xa1\x11\x11\xde\xbb\xe7\xa0\xd7\xed5t\
\xb3\x1eF\x95w>t\xb7\xcc\x1ajU~[\xd6\x07S\x9f\xe9\xe2\x9d\x0f\xde1\xc7\x9d'7\
\x05c\x98U\xe6[z\xde\x19\xd2>\xb4\xce\x98:\xa4\xc26XW\xe3v\x9d\x93\x00\x0e\
\x92\x90\x12\xa4D\x04HHB\xa4\xc3u\xc4\x1e$d\t\x85,a+k\xd8\xca\x1aJ\xc9\xa1\
\x90\x80\xfa!\xbf\xde\x8e\xcf\xfa\xf3Kx\x03\x0b\xf8P\xa7"

, """icon_outgoing_letter""": "x\xda]\xcd;\x0e\x830\x10\x04\xd0\x9eSXJ\xe1T+\\$r\x9dH.\xe3\x82f[\x84R\x05e\
r\xff*\xbb\xb6\xf1\x87\x11B\xccc\x0c\xd7\xfd\xe7\xa6\xc5\xba\xbb\x91\xebf\
\x9c\x9d\xd6\xc5\xc2l\xe6\xb1\xaf\xdb'5\x92v\xf1\xb3&u#\xfd\x85\xef;\x15\xd6\
\x97\xc1\x87g\xf0\xa9G\xed\xf3\\\xbb\xc9!.\x0f\x1d\x12\x1d\xda\x90\xa8jE\xa2\
\xa6m\t!\x9c\x96`\xddaX\x82\x13f-(\x96Q\x94\x0b\x02\xb1`\x04*\xb2*\xabq\x87\
\x8c\x1c\x1e1-G\xcc6\x1eG\x8c\xf2Q\xb9\xf5?\xeas \x0fQ\xa4?:Rj{"}

    __icons_recalls = {"""icon_talking_head""": 'x\xda\x8d\x8f1\x0b\xc3 \x10\x85\xf7\xfc\x8a\x83\x0e\x16\x041K\xe3\xac\xe0\
\xd8\x0cYn\r\xa1SC\xed\xff\x9fzw\x1a\x8b\xa6C\x1f"\xbc\xef\xde\xdd\xe9u\x7f\
\x8f\xc3\xa2\xc6\x1b\xd0\xa1K\r\xeb\xa2\x006\xf0\xfb\xba=\xc5%r\x17\xef|\xf0\
N\xbcf?\xb9)X+~foI1\xd7\r\xf9{z=\xc4 \x17\xa3\x8b\xa1\x14\xe1\x90\xc9ja\xc1=\
\x84\xbf b:Ad\xd8\xcd$\x86\xd0mg\x04-\xe4\x18\xcem;\x16\xfd\x86\t\xfa\xf6\
\xfc"\xad\xeb\xa2\xda\xad\xcfI\x8a\xd5$Oc\x81\x04\xbf\x8b\x8e\x8fS\x90\xa1\
\xf9\x00[x_\x8e'}

    __icons_inbox = {"""icon_inbox""": "x\xda\x85\xd01\x0e\xc20\x0c\x05\xd0\xbd\xa7\x88\xc4\x10&+\x19\x80\xcc e\xac\
\x87.^\xab\x8a\x89\ns\xff\t\xc7Nh2\xf1UU\xfdOv#\xe5\xbc\x7f\xe2\xb4\xf8xu\
\xf2\\\\\xf4\xd3\xbaxv\x9b\xbb\xef\xeb\xf6\xd2\xe6\xa4\xcd\xfc~jA)\xa7\x10\
\xf2#'\xedTzN\xbf\x0e\xa5\xdfR\x90\xd4\xe5\x12\x00 \xfb\xfa\x83,\xc84\"S\x99\
4m\xc8\xa4hZQ\xe7\xa0\xcd\x1a\xca\x9c)\x11\x8aVd\xac\xeb\xc8\x07\x92\xaa\xce\
uHl\xa1\x11\xa9dD\xb3q\x9d\x11\xe5\xa7\xf2\xea\x0f\xea\xd3\x90\x86\xf4\xb7tD\
\x10\xbe\xb8\xbej\xdf"}

    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id)
	self.SetAutoLayout(True)
	sizer = wxBoxSizer(wxHORIZONTAL)
	self.SetBackgroundColour(wxColour(222,222,222))
       	#-----------------------------------------------------
	#create imagelist for use by the lists in the notebook
	#e.g the icons to sort the columns up and down
	#-----------------------------------------------------
	self.ListsImageList= wxImageList(16,16)
	self.small_arrow_up = self.ListsImageList.Add(images.getSmallUpArrowBitmap())
        self.small_arrow_down = self.ListsImageList.Add(images.getSmallDnArrowBitmap())
	#------------------------------------------------------------------------
	#----------------------------------------------------------------------
	#Add a notebook control to hold the lists of things eg scripts, recalls
	#----------------------------------------------------------------------
	#self.notebook1 = Notebook(self, -1, wxDefaultPosition, wxDefaultSize, style = 0)
        self.notebook1 = Notebook(self, -1)
	#-------------------------------------------------------------------------
	#Associate an imagelist with the notebook and add images to the image list
	#-------------------------------------------------------------------------
	tabimage_Script = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = -1
        self.notebook1.il = wxImageList(16, 16)
	tabimage_Script = self.notebook1.il.Add(self.getBitmap(self.__icons_script[_("""icon_Rx_symbol""")]))
	tabimage_Requests = self.notebook1.il.Add( self.getBitmap(self.__icons_requests[_("""icon_blood_sample""")]))
	tabimage_Measurements = self.notebook1.il.Add( self.getBitmap(self.__icons_measurements[_("""icon_Set_Square""")]))
	tabimage_Referrals = self.notebook1.il.Add( self.getBitmap(self.__icons_referrals[_("""icon_writing_pen""")]))
	tabimage_Recalls = self.notebook1.il.Add(self.getBitmap(self.__icons_recalls[_("""icon_talking_head""")]))
	tabimage_Inbox = self.notebook1.il.Add(self.getBitmap(self.__icons_inbox[_("""icon_inbox""")]))
	self.notebook1.SetImageList(self.notebook1.il)
	szr_notebook = wxNotebookSizer(self.notebook1)
	#----------------------------------------------------------------------------------
	#now create the lists that will sit on the notebook pages, and add them to the page
	#----------------------------------------------------------------------------------
	szr_script_page= wxBoxSizer(wxVERTICAL)
	ListScript_ID = wxNewId()                                                         #can use wxLC_VRULES to put faint cols in list
       	self.List_Script = wxListCtrl(self.notebook1, ListScript_ID,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
        szr_script_page.Add(self.List_Script,100,wxEXPAND)
        self.List_Script.SetForegroundColour(wxColor(131,129,131))
	self.List_Requests = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Measurements = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Referrals = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Recalls = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Inbox = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)

	self.notebook1.AddPage(self.List_Script, '', True, tabimage_Script)
	#self.notebook1.AddPage(True, tabimage_Inbox, szr_script_page, '')
	self.notebook1.AddPage(self.List_Requests, '', True, tabimage_Requests)
	self.notebook1.AddPage(self.List_Measurements, '', True, tabimage_Measurements)
	self.notebook1.AddPage(self.List_Referrals, '', True, tabimage_Referrals)
	self.notebook1.AddPage(self.List_Recalls, '', True, tabimage_Recalls)
	self.notebook1.AddPage(self.List_Inbox, '', True, tabimage_Inbox)
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
	info.m_text = _("Drug")
	self.List_Script.InsertColumnInfo(0, info)


	info.m_format = wxLIST_FORMAT_LEFT
	info.m_text = _("Dose")
	self.List_Script.InsertColumnInfo(1, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = _("Instructions")
	self.List_Script.InsertColumnInfo(2, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = _("Last Date")
	self.List_Script.InsertColumnInfo(3, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = _("Prescribed For")
	self.List_Script.InsertColumnInfo(4, info)


	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = _("Quantity")
	self.List_Script.InsertColumnInfo(5, info)


	info.m_format = 0
	info.m_text = _("First Date")
	self.List_Script.InsertColumnInfo(6, info)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = scriptdata.items()
	for x in range(len(items)):
            key, data = items[x]
	    #<DEBUG>
            gmLog.gmDefLog.Log (gmLog.lData, items[x])
            #</DEBUG>
	    #print x, data[0],data[1],data[2]
	    self.List_Script.InsertStringItem(x, data[0])
            self.List_Script.SetStringItem(x, 1, data[1])
            self.List_Script.SetStringItem(x, 2, data[2])
	    self.List_Script.SetStringItem(x, 3, data[3])
	    self.List_Script.SetStringItem(x, 4, data[4])
	    self.List_Script.SetStringItem(x, 5, data[5])
	    self.List_Script.SetStringItem(x, 6, data[6])
	    self.List_Script.SetItemData(x, key)
	#--------------------------------------------------------
	#note the number pased to the wxColumnSorterMixin must be
	#the 1 based count of columns
	#--------------------------------------------------------
        self.itemDataMap = scriptdata
        #wxColumnSorterMixin.__init__(self, 5)              #I excluded first date as it didn't sort

	self.List_Script.SetColumnWidth(0, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(1, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(2, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(3, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(4, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(5, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(6, 150)
	sizer.AddSizer(szr_notebook,40,wxEXPAND)
	self.SetSizer(sizer)  #set the sizer
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(True)                 #tell frame to use the sizer
        self.Show(True)

    def getBitmap (self,__icon):
        # returns the images on the tabs
	return wxBitmapFromXPMData(cPickle.loads(zlib.decompress( __icon )))

#=====================================================================
class gmGP_TabbedLists (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the tabbed lists
    """
    def name (self):
        return 'TabbedListsPlugin'

    def register (self):
        self.mwm = self.gb['clinical.manager']
        self.mwm.RegisterRightSide ('tabbed_lists', TabbedLists
                                   (self.mwm.righthalfpanel, -1), position=1)

    def unregister (self):
        self.mwm.Unregister ('tabbed_lists')

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 300))
	app.SetWidget(TabbedLists, -1)
	app.MainLoop()
 
#=====================================================================
# $Log: gmGP_TabbedLists.py,v $
# Revision 1.21  2008-04-13 14:39:49  ncq
# - no more old style logging
#
# Revision 1.20  2005/09/26 18:01:53  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.19  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.18  2003/11/17 10:56:42  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.17  2003/05/03 02:20:24  michaelb
# bug fix: make wxPython 2.4.0.7's wxRect:Inside happy
#
# Revision 1.16  2003/04/23 09:20:32  ncq
# - reordered arguments and removed keywords from Tabbed Lists to work
#   around difference betwee 2.0.4.1 to 2.0.4.7
#
# Revision 1.15  2003/04/05 00:39:23  ncq
# - "patient" is now "clinical", changed all the references
#
# Revision 1.14  2003/02/25 05:30:46  michaelb
# improvements on the tooltips 'attached' to the tab images
#
# Revision 1.13  2003/02/20 02:13:49  michaelb
# adding tooltips for the images on the tabs of the wxNotebook
#
# Revision 1.12  2003/02/07 21:01:21  sjtan
#
# refactored to re-use handler_generator.generator. Handler for gmSelectPerson as test.
#
# Revision 1.11  2003/02/02 06:36:26  michaelb
# split '__icons' into multiple dictionaries
# added 'icon_outgoing_letter' to '__icons_referrals' so it similar to 'gmGP_Referrals.py'
#
# Revision 1.10  2003/01/30 06:02:14  michaelb
# tiny bit of clean-up
#
# Revision 1.9  2003/01/28 06:47:43  michaelb
# removed dependence on "images_gnuMedGP_TabbedLists.py", changed drugs tab icon to 'Rx'
#
# Revision 1.8  2003/01/25 23:02:53  ncq
# - cvs keywords/metadata
#
