#!/usr/bin/python
#############################################################################
#
# gmGP_Allergies:
# ----------------------------------
#
# This panel will hold all the allergy details, and allow entry
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
#           30.07.2002 rterry images inserted, code cleaned up
# @TODO:
#	- write cmEditArea.py
#	- decide on type of list and text control to use
#       - someone smart to fix the code (simplify for same result)
#      
############################################################################

from wxPython.wx import *
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmEditArea             #panel class holding editing prompts
import gmPlugin

ID_ALLERGYLIST = wxNewId()
ID_ALLERGIES = wxNewId ()
ID_ALL_MENU = wxNewId ()
gmSECTION_ALLERGY = 7
#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
allergydata = {
1 : ("penicillin","Allergy", "definate","amoxycillin trihydrate","anaphylaxis"),
2 : ("macrolides","Sensitivity","definate", "erythromycin ethyl succinate", "nausea and vomiting"),
3 : ( "celecoxib","Allergy","definate","celecoxib", "allergic drug rash"),
}

allergyprompts = {
1:("Date"),
2:("Search Drug"),
3:("Generic"),
4:("Class"),
5:("Reaction"),
6:("Type")
 }

class AllergyPanel(wxPanel):
	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		#--------------------
		#add the main heading
		#--------------------
		self.allergypanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  ALLERGIES  ")
		#--------------------------------------------
		#dummy panel will later hold the editing area
		#--------------------------------------------
		self.dummypanel = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.dummypanel.SetBackgroundColour(wxColor(222,222,222))
		#----------------------------------------------
		#now create the editarea specific for allergies
		#----------------------------------------------
		self.editarea = gmEditArea.EditArea(self,-1,allergyprompts,gmSECTION_ALLERGY)
		#-----------------------------------------------
		#add the divider headings below the editing area
		#-----------------------------------------------
		self.drug_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Allergy and Sensitivity - Summary")
		self.sizer_divider_drug_generic = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_divider_drug_generic.Add(self.drug_subheading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------                                                                               
		#add the list to contain the drugs person is allergic to
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.list_allergy = wxListCtrl(self, ID_ALLERGYLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_allergy.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		#----------------------------------------	  
		# add some dummy data to the allergy list
		#----------------------------------------
		self.list_allergy.InsertColumn(0, "Type")
		self.list_allergy.InsertColumn(1, "Status")
		self.list_allergy.InsertColumn(2, "Class")
		self.list_allergy.InsertColumn(3, "Generic")
		self.list_allergy.InsertColumn(4, "Reaction")
		#-------------------------------------------------------------
		#loop through the scriptdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_allergy.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = allergydata.items()
		for x in range(len(items)):
			key, data = items[x]
			self.list_allergy.InsertStringItem(x, data[0])
			self.list_allergy.SetStringItem(x, 1, data[1])
			self.list_allergy.SetStringItem(x, 2, data[2])
			self.list_allergy.SetStringItem(x, 3, data[3])
			self.list_allergy.SetStringItem(x, 4, data[4])
			self.list_allergy.SetItemData(x, key)

		self.list_allergy.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_allergy.SetColumnWidth(1, wxLIST_AUTOSIZE)
		self.list_allergy.SetColumnWidth(2, wxLIST_AUTOSIZE)
		self.list_allergy.SetColumnWidth(3, wxLIST_AUTOSIZE)
		self.list_allergy.SetColumnWidth(4, wxLIST_AUTOSIZE)
		#--------------------------------------------------------------------------------------
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		#--------------------------------------------------------------------------------------
		self.classtext_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Class notes for celecoxib")
		self.classtxt = wxTextCtrl(self,-1,
			"A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
			size=(200, 100), style=wxTE_MULTILINE)
		self.classtxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,'xselfont'))
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.allergypanelheading,0,wxEXPAND)
		self.mainsizer.Add(self.dummypanel,1,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
		self.mainsizer.Add(self.list_allergy,5,wxEXPAND)
		self.mainsizer.Add(self.classtext_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.classtxt,4,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(true)
		self.Show(true)
#----------------------------------------------------------------------	  
class gmGP_Allergies (gmPlugin.wxPatientPlugin):
	"""Plugin to encapsulate the allergies window"""

	__icons = {
0: 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}
   
	def name (self):
		return 'Allergies Window'

	def MenuInfo (self):
		return ('view', '&Allergies')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[0]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[0]

	def GetWidget (self, parent):
		return AllergyPanel (parent, -1)

#----------------------------------------------------------------------	  
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(AllergyPanel, -1)
	app.MainLoop()
