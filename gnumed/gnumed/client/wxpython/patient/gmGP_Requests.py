#!/usr/bin/python
#############################################################################
#
# gmPrescription:
# ----------------------------------
#
# This panel will hold all the prescrition, and allow entry
# of those details via the editing area (gmEditArea.py - currently a
# vapour module
#
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#
# @TODO:
#	- write cmEditArea.py
#	- decide on type of list and text control to use
#       - someone smart to fix the code (simplify for same result)
#      
############################################################################

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import gmGuiElement_HeadingCaptionPanel		#panel class to display top headings
import gmGuiElement_DividerCaptionPanel		#panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel		#panel to hold flashing alert messages
import gmEditArea             			#panel class holding editing prompts and text boxes
import gmPlugin_Patient
from gmPatientHolder import PatientHolder

ID_REQUESTSLIST = wxNewId()
gmSECTION_REQUESTS = 9
#------------------------------------
#Dummy data to simulate script items
#------------------------------------
requestdata = {
1 : ("Pathology - Douglas Hanly Moir - FBC;UEC;LFT's; Notes:'General tiredness",""),
2 : ("Radiology - Newcastle Diagnostic Imaging - CT Abdomen; Notes:'LIF mass'", "")
}

requestprompts = {
1:("Request Type"),
2:("Company"),
3:("Street"),
4:("Suburb"),
5:("Request(s)"),
6:("Notes on Form"),
7:("Medications"),
8:("Copy to"),
9:("Progress Notes"),
10:("")
	}


class RequestsPanel (wxPanel, PatientHolder):
     def __init__(self,parent, id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		PatientHolder.__init__(self)
		#--------------------
		#add the main heading
		#--------------------
		self.requestspanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"     REQUESTS     ")
		#--------------------------------------------
		
		#--------------------------------------------
		self.sizer_top  = wxBoxSizer(wxHORIZONTAL)
		#FIXME remove the date text below
		self.txt_requestDate = wxTextCtrl(self, -1, "12/06/2002",wxDefaultPosition,wxDefaultSize)
		self.spacer = wxWindow(self,-1, wxDefaultPosition,wxDefaultSize,0) 
		self.spacer.SetBackgroundColour(wxColor(222,222,222))
		self.sizer_top.Add(self.spacer,6,wxEXPAND)
		self.sizer_top.Add(self.txt_requestDate,1,wxEXPAND|wxALL,2)
		self.sizer_top.Add(10,0,0)
		#---------------------------------------------
		#now create the editarea specific for requests
		#---------------------------------------------
		self.editarea = gmEditArea.gmRequestEditArea(self,-1)
		#-----------------------------------------------------------------
		#add the divider headings for requests generated this consultation
		#-----------------------------------------------------------------
		self.requestsgenerated_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Requests generated this consultation"))
		self.sizer_requestsgenerated = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_requestsgenerated.Add(self.requestsgenerated_subheading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------                                                                               
		#add the list to contain the requests the doctor has ordered for person this consult
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.list_requests = wxListCtrl(self, ID_REQUESTSLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_requests.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		#----------------------------------------	  
		# add some dummy data to the allergy list
		self.list_requests.InsertColumn(0, _("Request summary"))
		self.list_requests.InsertColumn(1, "")
		#-------------------------------------------------------------
		#loop through the requestdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_requests.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = requestdata.items()
		for x in range(len(items)):
			key, data = items[x]
			self.list_requests.InsertStringItem(x, data[0])
			self.list_requests.SetStringItem(x, 1, data[1])
			self.list_requests.SetItemData(x, key)
		self.list_requests.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_requests.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		
		self.mainsizer.Add(self.requestspanelheading,0,wxEXPAND)
		self.mainsizer.Add(0,5,0)
		self.mainsizer.Add(self.sizer_top,0,wxEXPAND)
		self.mainsizer.Add(self.editarea,9,wxEXPAND)
		self.mainsizer.Add(self.requestsgenerated_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.list_requests,7,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.SetAutoLayout(True)
		self.Show(True)
	
		
class gmGP_Requests (gmPlugin_Patient.wxPatientPlugin):
	"""
	Plugin to encapsulate the requests window
	"""
	__icons = {
"""icon_blood_sample""": "x\xda}\x90=\x0b\xc3 \x10\x86\xf7\xfc\n\xc1\xc4\x14\x02r.\xd51\x18p\xacC\x96\
[K\xe9Vj\xff\xff\xd4\x9e\x1f\xa5g!\xea\xf2<\xbe/'\x9e\x1e/3\xec\xb39\x0b:F\
\x98y\xb8\xee\xf3*nBZg7\x80\xcc\x9a88\x80\xe02c\xbb\xb7\x85\xc7\xc2\x005\xbf\
\x94|h\xfd\x89\xd8\x01\xed\xcc\xaa\xf07/>|I\xcf{\x86\xd8\xcau\x98l\xc3k8\x11\
{\xe77\xefj\x99\xafNj\xfd/\xb5\xce\x96KL\xd92\x89)\xc6^\x92\xc3\xae\x8ei\x89\
\xd8M'\xb7vOB)\xe5\xd8\xbd\xf3\xd75\xc9\\\x95\x13sU*\xe6\x9aT\xea\xe0C\x8e\
\xa5~\x03\xa2\x9e`\x0c"
}

	def name (self):
		return 'Requests'

	def MenuInfo (self):
		return ('view', '&Requests') #FIXME fix the ampersand to a logical place in relationship to other buttons

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_blood_sample""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_blood_sample""")]

	def GetWidget (self, parent):
		return  RequestsPanel (parent, -1)


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(RequestsPanel, -1)
	app.MainLoop()
