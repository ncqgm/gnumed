#!/usr/bin/python
#############################################################################
#
# gmGP_Measurements
# ----------------------------------
#
# This panel will allow the input of measurements eg Blood pressure, weight
# height, INR, etc, or display things '  measurable' grabbed from other sections
# e.g Hb, wcc etc
#
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    09.08.2002 rterry initial implementation, untested
#
# @TODO: just about everything. Gui for demonstration purposes only
#	
#      
############################################################################

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmEditArea                              #panel class holding editing
import gmPlugin_Patient
import gmLog
import gmI18N
from gmListCtrlMapper import gmListCtrlMapper

import gmPatientHolder

ID_MEASUREMENTVALUESLIST = wxNewId()
gmSECTION_MEASUREMENTS = 10
ID_MEASURMENTTYPESLIST = wxNewId()

#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
measurementtypesdata = {
1 : ("Blood Pressure",""),
2 : ("Height",""),
3 : ("Weight",""),
4 : ("INR",""),
5 : ("Etc, Etc....",""),
}

values_BP_data = {
1 : ("01/10/2001","140/80"),
2 : ("19/01/2002","180/105"),
3 : ("21/05/2002","156/84"),
4 : ("08/08/2002","170/110"),
}

values_INR_data = {
1 : ("01/10/2001","1.1"),
2 : ("19/01/2002","2.7"),
3 : ("21/05/2002","3.5"),
4 : ("08/08/2002","2.8"),
}
values_Weight_data = {
1 : ("01/10/2001","79.8"),
2 : ("19/01/2002","88.5"),
3 : ("21/05/2002","87.4"),
4 : ("08/08/2002","87.3"),
}
values_Height_data = {
1 : ("01/10/2001","142"),
2 : ("19/01/2002","148"),
3 : ("21/05/2002","149"),
4 : ("08/08/2002","152"),
}
measurement_prompts = {
1:("Type"),
2:("Value"),
3:("Date"),
4:("Comment"),
5:("Progress Notes"), 
6:(""),
	}

class MeasurementPanel (wxPanel, gmPatientHolder.PatientHolder):
	def __init__(self,parent, id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)
		gmPatientHolder.PatientHolder.__init__(self)
		#--------------------
		#add the main heading
		#--------------------
		self.pasthistorypanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1," MEASUREMENTS ")
		#----------------------------------
		#dummy panel above the editing area
		#----------------------------------
		self.dummypanel1 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel1.SetBackgroundColour(wxColor(222,222,222))
		##--------------------------------------------------
		#now create the editarea specific for measurements
		#--------------------------------------------------
		#self.editarea = gmEditArea.EditArea(self,-1,measurement_prompts,gmSECTION_MEASUREMENTS)
		self.editarea = gmEditArea.gmMeasurementEditArea(self, -1)
		#self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		#self.dummypanel2.SetBackgroundColour(wxColor(222,222,222))
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.measurementtypes_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Type")
		self.measurements_values_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Values")
		self.sizer_measurements_types_heading = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_measurements_types_heading.Add(self.measurementtypes_heading,1, wxEXPAND)
		self.sizer_measurements_types_heading.Add(self.measurements_values_heading,1, wxEXPAND)

		#--------------------------------------------------------------------------------------                                                                               
		#add the list of significant problems
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.measurement_types_list = wxListCtrl(self, ID_MEASURMENTTYPESLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.measurement_types_list.SetFont(wxFont(10,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		self.measurements_values_list = wxListCtrl(self, ID_MEASUREMENTVALUESLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.measurements_values_list.SetFont(wxFont(10,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		self.sizer_measurementtypes_values = wxBoxSizer(wxHORIZONTAL)
		self.sizer_measurementtypes_values.Add(self.measurement_types_list,4,wxEXPAND)
		self.sizer_measurementtypes_values.Add(self.measurements_values_list,6, wxEXPAND)
		#---------------------------------------------	  
		# add some dummy data to the measurements list
		#---------------------------------------------
		self.measurement_types_list.InsertColumn(0, _("Type"))
		self.measurement_types_list.InsertColumn(1, "")
		#-------------------------------------------------------------
		#loop through the measurementtypesdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.measurement_types_list.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		m = gmListCtrlMapper(self.measurement_types_list)
		m.SetData(measurementtypesdata)
		self.typesMapper = m
		#items = measurementtypesdata.items()
		#for x in range(len(items)):
		#	key, data = items[x]
		#	self.measurement_types_list.InsertStringItem(x, data[0])
		#	self.measurement_types_list.SetStringItem(x, 1, data[1])
		#	self.measurement_types_list.SetItemData(x, key)
		self.measurement_types_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.measurement_types_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#-----------------------------------------	  
		# add some dummy data to the values list
		#-----------------------------------------
		self.measurements_values_list.InsertColumn(0, "Date")
		self.measurements_values_list.InsertColumn(1, "Value")
		#-------------------------------------------------------------
		#loop through the measurementtypesdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.measurement_types_list.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		m = gmListCtrlMapper(self.measurements_values_list)
		m.SetData(values_BP_data)
		self.valueMapper = m	
		#items = values_BP_data.items()
		#for x in range(len(items)):
		#	key, data = items[x]
		#	self.measurements_values_list.InsertStringItem(x, data[0])
		#	self.measurements_values_list.SetStringItem(x, 1, data[1])
		#	self.measurements_values_list.SetItemData(x, key)
		self.measurements_values_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.measurements_values_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.pasthistorypanelheading,0,wxEXPAND)
		self.mainsizer.Add(self.dummypanel1,0,wxEXPAND)
		self.mainsizer.Add(self.editarea,1,wxEXPAND)
		self.mainsizer.Add(self.sizer_measurements_types_heading,0,wxEXPAND)
		self.mainsizer.Add(self.sizer_measurementtypes_values,2,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(True)
		self.Show(True)
	
		
#--------------------------------------------------------------------
class gmGP_Measurements (gmPlugin_Patient.wxPatientPlugin):
	"""
	Plugin to encapsulate the prescriptions window
	"""

	__icons = {
"""icon_Set_Square""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"S\x05Cu\xae\xc4`\xf5|\x85d\x05\xa7\x9c\xc4\
\xe4l0O\x0f\xc8S6\xb70w60\x00\xf3\xfda|s\x0b0?\x02\xc4w\xb3p\x83\xc9+\x00\
\xf9~\xf9y\xa9P\x8e\x82\x82^D\x84\x9e\x02\x14 \x0b\xe6c\x11\xd4\xcb\'\xac2\
\x1f\r@\\\x19\x81\n\xa1\x82\xa8\x00\xb7\xa0?\x10\xe4\xeb\xe9\xe5\xfbC\x015\
\xdcI}\x95z\x00\xc7\xd5_\x1b'
}

	def name (self):
		return 'Measurements'

	def MenuInfo (self):
		return ('view', '&Measurements')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_Set_Square""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_Set_Square""")]

	def GetWidget (self, parent):
		return  MeasurementPanel (parent, -1)


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(MeasurementPanel, -1)
	app.MainLoop()
