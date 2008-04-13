#!/usr/bin/python
#############################################################################
#
# gmGP_PastHistory.py
# ----------------------------------
#
# This panel will hold all the pasthistory details
#
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#           31.07.2002 rterry added to cvs
#
# @TODO:almost everything!
#	contains dummy data only
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
import gmEditArea             				#panel class holding editing prompts and text boxes
import gmPlugin_Patient

import gmDispatcher

from gmPatientHolder import PatientHolder
import gmPatientHolder

from gmListCtrlMapper import gmListCtrlMapper

import gmMultiColumnList

ID_SIGNIFICANTPASTHISTORYLIST = wxNewId()
ID_ACTIVEPROBLEMLIST = wxNewId()
gmSECTION_PASTHISTORY = 5
#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
activehistorydata = {
1 : ("1982","Hypertension"),
2 : ("1990","Ischaemic Heart Disease"),
3 : ("1995","NIDDM"),
4 : ("1998","Lymphoma"),
5:("1998","Chemotherapy"),
}
significanthistorydata = {
1 : ("1982","Hypertension"),
2 : ("1990","Acute myocardial infarction"),
3 : ("1994","CABG"),
4 : ("1995","Cholecystectomy"),			  
}

pasthistoryprompts = {
1:("Condition"),
2:("Notes"),
3:(""),
4:("Age Onset"),
5:("Year Onset"),
6:(""),
7:("Progress Notes"), 
8:(""),
	}


		
class PastHistoryPanel(wxPanel, PatientHolder):
	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		PatientHolder.__init__(self)

		#--------------------
		#add the main heading
		#--------------------
		self.pasthistorypanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1, " PAST HISTORY  ")
		#----------------------------------
		#dummy panel above the editing area
		#----------------------------------
		self.dummypanel1 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel1.SetBackgroundColour(wxColor(222,222,222))
		#--------------------------------------------------
		#now create the editarea specific for past history
		#-------------------------------------------------
		#self.editarea = gmEditArea.EditArea(self,-1,pasthistoryprompts,gmSECTION_PASTHISTORY)
		self.editarea = gmEditArea.gmPastHistoryEditArea(self,-1)
		self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel2.SetBackgroundColour(wxColor(222,222,222))
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.significant_history_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Significant Past Problems"))
		self.sizer_significant_history_heading = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_significant_history_heading.Add(self.significant_history_heading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------                                                                               
		#add the list of significant problems
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		#self.significant_problem_list = wxListCtrl(self, ID_SIGNIFICANTPASTHISTORYLIST,  wxDefaultPosition, wxDefaultSize, wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.significant_problem_list = gmMultiColumnList.MultiColumnList(self, -1)
		self.significant_problem_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		#self.active_problem_list = wxListCtrl(self, ID_ACTIVEPROBLEMLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.active_problem_list = gmMultiColumnList.MultiColumnList(self, -1)
		self.active_problem_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		#---------------------------------------------------------	  
		# add some dummy data to the significant past problem list
		#---------------------------------------------------------
		#self.significant_problem_list.InsertColumn(0, _("year onset"))
		#self.significant_problem_list.InsertColumn(1, _("Condition"))
		#self.significant_problem_list.InsertColumn(2, _("Notes"))
		#-------------------------------------------------------------------------
		#loop through the significanthistorydata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.significant_problem_list.InsertStringItem(x, data[0])!!
		#--------------------------------------------------------------------------
		#self.significant_mapper = gmListCtrlMapper(self.significant_problem_list)
		#self.significant_mapper.SetData( significanthistorydata)
		self.significant_problem_list.SetData( significanthistorydata)
		#items = significanthistorydata.items()
		#for x in range(len(items)):
		#	key, data = items[x]
		#	gmLog.gmDefLog.Log (gmLog.lData, items[x])
		#	self.significant_problem_list.InsertStringItem(x, data[0])
		#	self.significant_problem_list.SetStringItem(x, 1, data[1])
		#	self.significant_problem_list.SetItemData(x, key)
		#	self.significant_problem_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		#self.significant_problem_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#------------------------------------------------	  
		#add some dummy data to the active problems list
		#------------------------------------------------
		#self.active_problem_list.InsertColumn(0, _("Year Onset"))
		#self.active_problem_list.InsertColumn(1, _("Condition"))
		#self.active_problem_list.InsertColumn(2, _("Notes"))
		#-------------------------------------------------------------
		#loop through the activehistorydata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.significant_problem_list.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		#self.active_mapper = gmListCtrlMapper(self.active_problem_list)
		#self.active_mapper.SetData( activehistorydata)
		self.active_problem_list.SetData( activehistorydata)

		#items = activehistorydata.items()
		#for x in range(len(items)):
		#	key, data = items[x]
		#	gmLog.gmDefLog.Log (gmLog.lData, items[x])
		#	self.active_problem_list.InsertStringItem(x, data[0])
		#	self.active_problem_list.SetStringItem(x, 1, data[1])
		#	self.active_problem_list.SetItemData(x, key)
		#self.active_problem_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		#self.active_problem_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#--------------------------------------------------------------------------------------
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		#--------------------------------------------------------------------------------------
		self.active_problems_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Active Problems"))
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.pasthistorypanelheading,0,wxEXPAND)
		#self.mainsizer.Add(self.dummypanel1,0,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		#self.mainsizer.Add(self.dummypanel2,0,wxEXPAND)
		self.mainsizer.Add(self.significant_history_heading,0,wxEXPAND)
		self.mainsizer.Add(self.significant_problem_list,4,wxEXPAND)
		self.mainsizer.Add(self.active_problems_heading,0,wxEXPAND)
		self.mainsizer.Add(self.active_problem_list,4,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(True)
		self.Show(True)

		gmDispatcher.connect(self._updateUI,  u'clin_history_updated')
	
		self.significant_problem_list.addItemListener( self._significantPastItemSelected)	

		self.active_problem_list.addItemListener(self._activePastItemSelected)

	def _significantPastItemSelected(self, event):
		clinical = self.get_past_history()
		self._historyItemSelected( event ,clinical.get_significant_past_history() )

	def _activePastItemSelected( self, event):
		clinical = self.get_past_history()
		self._historyItemSelected( event ,clinical.get_active_history() )

	def _historyItemSelected( self, event, list):	
		(selId, str) = event['item']
		for (id, map) in list:
			if id == selId:
				clinical = self.get_past_history()
				self.editarea.setInputFieldValues(map, id)


	def _updateUI(self):
		clinical = self.get_past_history()
		significant_past = clinical.get_significant_past_history()
		active_hx = clinical.get_active_history()
		self.active_problem_list.SetData(  self._get_list_map( active_hx) , fitClientSize = 1)
		#self.significant_mapper.SetData( self._get_list_map( significant_past) )
		self.significant_problem_list.SetData( self._get_list_map( significant_past), fitClientSize = 1 )

	
	def _get_list_map(self, clin_history_list):
		newMap = {}
		for (id, map) in clin_history_list:
			newMap[id] =   self.get_past_history().short_format(map)   
		return newMap	
	
	
		
		
		
#----------------------------------------------------------------------
class gmGP_PastHistory(gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the immunisation window."""

	__icons = {
"""icon_hx_ship""": 'x\xdaU\x8e1\x0b\x830\x10\x85\xf7\xfe\x8a\x80\x82\x85@\xa8K\xb5\xdb\x11\xc1\
\xb17\xb8\xbcU\xa4S\xa5\xe9\xff\x9fz\x97\xc44^$\xe4{w\xef\x9d\xd7\xfd\xdb_\
\x96\xae\xbf\x1b\xf9\x1e\xa6\xef.\xeb\xd2\xc1l\xc6\xef\xeb\xf6\x8ed\x85\x9a\
\x9b\xd40F&\xe5a\x1c\xa6\xcc\xcd\xd1\x9f\x13\x9b\xd4W%r\x10~\x86\xcf+\x02ks\
\x1e\xe7)\x0f\xbb\xc4e\xb8U\xf6\xa3\x9f|\x0es\xce\x18H\x85T)1\x00\xcc\x8c \
\x07\x95\x18\xc0\x80e\xab\x8d"\x12\xac\xd8\x1b\x96\xc7_\xb42\x198\xe7Vv&9\
\xda\xab\xec\x00\x11\xceb\x8c\xc4\xc9\x1e\x87H\x02P-\x92\x1dm\xfaU\xb0@\x11I\
E\xbd\x08\x95\x1d\xf9:\xeci\x83\x84\xe6my\xb2\xae\xb2\xe8\xa4e\xbb\xadO\x14\
\xdd\x0f&\xf7\x8a\xe4'
}

	def name (self):
		return 'Pasthistory Window'

	def MenuInfo (self):
		return ('view', '&Past History')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_hx_ship""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_hx_ship""")]

	def GetWidget (self, parent):
		return PastHistoryPanel (parent, -1)
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(PastHistoryPanel, -1)
	app.MainLoop()
