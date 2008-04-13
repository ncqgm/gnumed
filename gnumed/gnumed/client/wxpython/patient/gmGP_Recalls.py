#!/usr/bin/python
###############################################################
#
# gmGP_Recalls.py
# ----------------------------------
#
# This panel will hold all the recall details, and allow entry
# of those details via the editing area (gmEditArea.py)
# 
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    0108.2002 rterry initial implementation, untested
#
# @TODO:
#      
###############################################################
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import gmGuiElement_HeadingCaptionPanel		#panel class to display top headings
import gmGuiElement_DividerCaptionPanel		#panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel		#panel to hold flashing alert messages
import gmEditArea             				#panel class holding editing prompts and text boxes
import gmPlugin_Patient
from gmPatientHolder import PatientHolder
ID_RECALL_LIST = wxNewId()
gmSECTION_RECALLS = 12
#------------------------------------------------------------------
#Dummy data to simulate recall items
#this is best displayed as a concatenated string of edit area lines
#------------------------------------------------------------------
recalldata = {
1 : ("Rectal examination and prostate blood test on 10/11/2002 to see Dr R Terry (Letter)","NOT SAVED"),
2 : ("Screening Colonoscopy on 01/07/2004 to see Dr R Terry (Letter)", "RECALL LOGGED")
}

recallprompts = {
1:("To see Dr"),
2:("For"),
3:("Date Due"),
4:("Add Text"),
5:("Include Forms"),
6:("Contact By"),
7:("Progress Notes"),
8:("")		 
}


class RecallsPanel(wxPanel , PatientHolder):
	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)	  
		PatientHolder.__init__(self)
		#--------------------
		#add the main heading
		#--------------------
		self.recallspanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  RECALLS & REVIEWS  ")
		#-------------------------------------------- 
		#dummy panel will later hold the editing area
		#--------------------------------------------
		self.dummypanel = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel.SetBackgroundColour(wxColor(222,222,222))
		#----------------------------------------------
		#now create the editarea specific for allergies
		#----------------------------------------------
		self.editarea = gmEditArea.gmRecallEditArea(self,-1)
		self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel2.SetBackgroundColour(wxColor(222,222,222))
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.recall_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Recalls entered this consultation"))
		self.sizer_divider_recalls = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_divider_recalls.Add(self.recall_subheading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------                                                                               
		#add the list to contain the recalls entered this session
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.list_recalls = wxListCtrl(self, ID_RECALL_LIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		#self.list_recalls.SetForegroundColour(wxColor(131,129,131))	
		self.list_recalls.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		#----------------------------------------	  
		# add some dummy data to the allergy list
		self.list_recalls.InsertColumn(0, _("Recall Details"))
		self.list_recalls.InsertColumn(1, _("Status"))
		#-------------------------------------------------------------
		#loop through the scriptdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_recalls.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = recalldata.items()
		for x in range(len(items)):
			key, data = items[x]
			self.list_recalls.InsertStringItem(x, data[0])
			self.list_recalls.SetStringItem(x, 1, data[1])
			self.list_recalls.SetItemData(x, key)
		self.list_recalls.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_recalls.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.recallspanelheading,0,wxEXPAND)
		#self.mainsizer.Add(self.dummypanel,1,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		#self.mainsizer.Add(self.dummypanel2,1,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_recalls,0,wxEXPAND)
		self.mainsizer.Add(self.list_recalls,4,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(True)
		self.Show(True)
#----------------------------------------------------------------------
class gmGP_Recalls(gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the immunisation window."""

	__icons = {
"""icon_talking_head""": 'x\xda\x8d\x8e=\x0b\xc3 \x10\x86\xf7\xfc\x8a\x03\x85\x14\x02\xa2Kc\xb7\xa0\
\x901\x0eY\\C\xe8\xd4P\xfb\xff\xa7z\xa7\xd1\xa6\xcd\xd0\xd3\xe5yx\xef\xe3\
\xb2\xbdT3\xb7\xea\n\xf1\xdf@\xb5\xcd2\xb7\x02V0\xdb\xb2>\x88X$\xd6\xeb\xdeJ\
I\xdc![\x89\x8f\xd8!\x8f\xba\xf0\xb0\xf3\xa8\x899\xb2\x96Z\xe6~\x88<\x85\xe7\
\x9d\xc0\xa7\xf0hs8 \x1bm\xacI\x0c"\x17\xa4J\xf7\xd5:\x95\xe2/\xe9}\xf8\x91\
\x1e\xe5\xd7\xcc\xe8\xbc8lw\xe8\xcaMI:G\xb9\xee\xd0\xee\x06Ou.\xc3\xe7v\x97\
\x83\xd11^\xb6\x97n^\x93\xfbH\xc6\x80\xefI\x9c\x86%\x80\xd5\x99\xe9H:3fQ\x8a\
7\x97\xb8jB'
}

	def name (self):
		return 'Recalls and Reviews Window'

	def MenuInfo (self):
		return ('view', '&Recalls + Reviews')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_talking_head""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_talking_head""")]

	def GetWidget (self, parent):
		return RecallsPanel (parent, -1)
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(RecallsPanel, -1)
	app.MainLoop()
