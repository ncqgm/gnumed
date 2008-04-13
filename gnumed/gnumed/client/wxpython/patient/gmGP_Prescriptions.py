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

import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmEditArea                              #panel class holding editing
import gmPlugin_Patient
from gmPatientHolder import PatientHolder



ID_SCRIPTICON = wxNewId ()
ID_SCRIPTLIST = wxNewId()
ID_SCRIPTMENU = wxNewId ()
ID_POPUP1 = wxNewId()

gmSECTION_SCRIPT = 8
# script popup
ID_AuthInd = wxNewId()
ID_Interactions = wxNewId()
ID_PregInfo = wxNewId()
ID_Restrictions = wxNewId()
ID_EditItem = wxNewId()
ID_DelItem = wxNewId()
ID_DelAll = wxNewId()
ID_MakeItemReg24 = wxNewId()
ID_DrugInfoBrief = wxNewId()
ID_DrugInfoFull = wxNewId()
ID_PrintItem = wxNewId()
ID_PrintAll = wxNewId()
ID_ReprintItem = wxNewId()
ID_ReprintAll = wxNewId()
ID_JustSaveItem = wxNewId()
ID_JustSaveAll = wxNewId()
ID_ChangeFont = wxNewId()
ID_SaveListLayout = wxNewId()
ID_Help = wxNewId()
ID_Exit = wxNewId()
#------------------------------------
#Dummy data to simulate script items
#------------------------------------
scriptdata = {
1 : ("Fluvax","0.5ml", "to be injected by the doctor","flu immunisation"),
2 : ("Tenormin","50mg","1 daily", "hypertension"),
3 : ( "Ceclor CD","375mg","1 twice daily","sinusitis"),
}

scriptprompts = {
1:("Prescribe For"),
2:("Class"),
3:("Generic"),
4:("Brand"),
5:("Strength"),
6:("Directions"),
7:("For"),
8:("Progress Notes"),
9:(""),
 }


class PrescriptionPanel (wxPanel, PatientHolder):
	def __init__(self,parent, id):
		#wxPanel.__init__(self,parent, id)
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)
		PatientHolder.__init__(self)
		#--------------------
		#add the main heading
		#--------------------
		self.scriptpanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  SCRIPTS  ")
		#--------------------------------------------
		#sizer to hold either just date, or the
		#authority details, aia, authority number
		#--------------------------------------------
		self.sizer_authority  = wxGridSizer(1,0,0,0)
		self.sizer1 = wxBoxSizer(wxHORIZONTAL)
		self.txt_scriptDate = wxTextCtrl(self,-1,"12/06/2002",wxDefaultPosition,wxDefaultSize)
		self.spacer = wxWindow(self,-1, wxDefaultPosition,wxDefaultSize,0) 
		self.spacer.SetBackgroundColour(wxColor(222,222,222))
		#self.lbl_authorityindication = gmEditArea.EditAreaPromptLabel(self,-1,"Indication")
		#self.lbl_authoritynumber = gmEditArea.EditAreaPromptLabel(self,-1,"Auth No.")
		#self.txt_authorityindication =  wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize)
		#self.txt_authorityindication.Hide()
		#self.sizer_authority.Add(self.spacer,1,wxEXPAND)
		self.sizer1.Add(1,0,20)
		self.sizer1.Add(self.txt_scriptDate,3,wxEXPAND|wxALL,3)
		#self.sizer1.Add(1,0,1)
		self.sizer_authority.Add(self.sizer1,0,wxEXPAND)
		#-------------------------------------------------
		#now create the editarea specific for prescribing
		#-------------------------------------------------
		#self.editarea = gmEditArea.EditArea(self,-1,scriptprompts,gmSECTION_SCRIPT)
		self.editarea = gmEditArea.gmPrescriptionEditArea(self,-1)
		#---------------------------------------------------------------------
		#add the divider headings below the editing area for drug interactions
		#and add text control to show mini-drug interactions
		#---------------------------------------------------------------------
		self.interactiontext_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Drug Interactions"))
		self.sizer_divider_interaction_text = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_divider_interaction_text.Add(self.interactiontext_subheading,1, wxEXPAND)
		self.interactiontxt = wxTextCtrl(self,-1,
			"Mini-Drug interaction text goes here (click this for full description)\n \n"
			"Also, try clicking on the list below with the right mouse button to see a pop up menu",		    
			style=wxTE_MULTILINE)
		self.interactiontxt.SetFont(wxFont(10,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		#------------------------------------------------------------------------------------
		#add the divider headings below the drug interactions as heading for items prescribed
		#------------------------------------------------------------------------------------
		self.itemsprescribedheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Items prescribed this consultation"))
		self.sizer_itemsprescribed = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_itemsprescribed.Add(self.itemsprescribedheading,1, wxEXPAND)
		#--------------------------------------------------------------------------------------                                                                               
		#add the list to contain the drugs person is allergic to
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#
		#--------------------------------------------------------------------------------------
		self.list_script = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_script.SetFont(wxFont(10,wxSWISS, wxNORMAL, wxNORMAL, False, ''))
		EVT_RIGHT_UP(self.list_script, self.OnRightClickUp)
		#----------------------------------------
		# add some dummy data to the allergy list
		self.list_script.InsertColumn(0, _("Drug"))
		self.list_script.InsertColumn(1, _("Strength"))
		self.list_script.InsertColumn(2, _("Directions"))
		self.list_script.InsertColumn(3, _("For"))
		#-------------------------------------------------------------
		#loop through the scriptdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_script.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = scriptdata.items()
		for x in range(len(items)):
			key, data = items[x]
			self.list_script.InsertStringItem(x, data[0])
			self.list_script.SetStringItem(x, 1, data[1])
			self.list_script.SetStringItem(x, 2, data[2])
			self.list_script.SetStringItem(x, 3, data[3])
			self.list_script.SetItemData(x, key)

		self.list_script.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_script.SetColumnWidth(1, wxLIST_AUTOSIZE)
		self.list_script.SetColumnWidth(2, wxLIST_AUTOSIZE)
		self.list_script.SetColumnWidth(3, wxLIST_AUTOSIZE)
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.scriptpanelheading,0,wxEXPAND)
		self.mainsizer.Add(self.sizer_authority,1,wxEXPAND)
		self.mainsizer.Add(self.editarea,15,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_interaction_text,0,wxEXPAND)
		self.mainsizer.Add(self.interactiontxt,4,wxEXPAND)
		self.mainsizer.Add(self.itemsprescribedheading,0,wxEXPAND)
		self.mainsizer.Add(self.list_script,4,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.SetAutoLayout(True)
		self.Show(True)

	def OnRightClickUp(self, event):
		"""A right mouse click triggers a popup menu for the list script"""

		# create a temporary local popup menu
		aMenu = wxMenu()
		# Auth Ind: Australia: some drugs will only be subsidised given certain indications and explicit approval by authorities
		# like German "Positivliste"
		aMenu.Append(ID_AuthInd, _("Authority Indications"))
		aMenu.Append(ID_Interactions, _("Interactions"))
		aMenu.Append(ID_PregInfo, _("Pregnancy Information"))
		aMenu.Append(ID_Restrictions, _("Restricted Use Information"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_EditItem, _("Edit Item"))
		aMenu.Append(ID_DelItem, _("Delete Item"))
		aMenu.Append(ID_DelAll, _("Delete all Items"))
		# Reg 24: Australia: dispense all repeats at once
		aMenu.Append(ID_MakeItemReg24, _("Make Item Reg 24"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_DrugInfoBrief, _("Brief Product Information"))
		aMenu.Append(ID_DrugInfoFull, _("Full Product Information"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_PrintItem, _("Print Single Item"))
		aMenu.Append(ID_PrintAll, _("Print All Items"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_ReprintItem, _("Reprint Item"))
		aMenu.Append(ID_ReprintAll, _("Reprint All Items"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_JustSaveItem, _("Save Item no print"))
		aMenu.Append(ID_JustSaveAll, _("Save All Items no print"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_ChangeFont, _("Change Font"))
		aMenu.Append(ID_SaveListLayout, _("Save list layout"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_Help, _("Help"))
		aMenu.AppendSeparator()
		aMenu.Append(ID_Exit, _("Exit"))

		##connect the events to event handler functions
		EVT_MENU(self, ID_POPUP1, self.OnExitMenu)
		EVT_MENU(self, ID_PregInfo, gmLog.gmDefLog.Log(gmLog.lErr, "This should display Pregnancy Information !"))
		#EVT_MENU(self, ID_, gmLog.gmDefLog.Log(gmLog.lErr, "This should ... !")

		# show the menu
		self.PopupMenu(aMenu, event.GetPosition())
		#self.list_script.PopupMenu(aMenu,event.GetPosition())
		# whatever the user selected in the menu will have
		# been handled already virtue of the MENU events
		# created above

		# free resources
		aMenu.Destroy()

		# anybody else needs to intercept right click events?
		event.Skip()

	def OnExitMenu(self, event):
		print "OnExitMenu"
#--------------------------------------------------------------------
class gmGP_Prescriptions (gmPlugin_Patient.wxPatientPlugin):
	"""
	Plugin to encapsulate the prescriptions window
	"""

	__icons = {
"""icon_Rx_symbol""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"c\x05Cu\xae\xc4`u=\x85d\x05e\x03 p\xb3\x00\
\xf3#@|\x0b\x03\x10\x04\xf3\x15\x80|\xbf\xfc\xbcT(\x07\x15\xe0\x15\xd4\x83\
\x00t\xc1\x08 \x80\x8a"\t\xc2I\xb2\x04\xc1 "\x82R\x8b\x80\x08UP\x01b,\xdc\
\x9b\x10+\x14\xc0\xa6\xa2\xf9\x1d\xa8\x0eI;\x02DD\xe0\x0c%=\x00D|Hk'
}

	def name (self):
		return 'Prescription writer'

	def MenuInfo (self):
		return ('view', '&Script')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_Rx_symbol""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_Rx_symbol""")]

	def GetWidget (self, parent):
		panel =   PrescriptionPanel (parent, -1)
		return panel
#--------------------------------------------------------------------
if __name__ == '__main__':
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(PrescriptionPanel, -1)
	app.MainLoop()
