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

from wxPython.wx import *
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmEditArea                              #panel class holding editing
import gmPlugin

ID_SCRIPTICON = wxNewId ()
ID_SCRIPTLIST = wxNewId()
ID_SCRIPTMENU = wxNewId ()
gmSECTION_SCRIPT = 8
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


class PrescriptionPanel (wxPanel):
     def __init__(self,parent, id):
          #wxPanel.__init__(self,parent, id)
	  wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
          #--------------------
          #add the main heading
          #--------------------
          self.scriptpanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  SCRIPTS  ")
          #--------------------------------------------
          #sizer to hold either just date, or the
	  #authority details, aia, authority number
          #--------------------------------------------
	  self.sizer_authority  = wxGridSizer(2,0,1,1)
	  self.sizer1 = wxBoxSizer(wxHORIZONTAL)
	  self.txt_scriptDate = wxTextCtrl(self,-1,"12/06/2002",wxDefaultPosition,wxDefaultSize)
	  self.spacer = wxWindow(self,-1, wxDefaultPosition,wxDefaultSize,0) 
	  self.spacer.SetBackgroundColour(wxColor(222,222,222))
	  #self.lbl_authorityindication = gmEditArea.EditAreaPromptLabel(self,-1,"Indication")
          #self.lbl_authoritynumber = gmEditArea.EditAreaPromptLabel(self,-1,"Auth No.")
	  #self.txt_authorityindication =  wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize)
	  #self.txt_authorityindication.Hide()
	  self.sizer_authority.Add(self.spacer,1,wxEXPAND)
	  self.sizer1.Add(1,0,20)
	  self.sizer1.Add(self.txt_scriptDate,3,wxEXPAND|wxALL,3)
	  self.sizer1.Add(1,0,1)
	  self.sizer_authority.Add(self.sizer1,0,wxEXPAND)
	  #-------------------------------------------------
	  #now create the editarea specific for prescribing
	  #-------------------------------------------------
          self.editarea = gmEditArea.EditArea(self,-1,scriptprompts,gmSECTION_SCRIPT)
          #---------------------------------------------------------------------
          #add the divider headings below the editing area for drug interactions
	  #and add text control to show mini-drug interactions
          #---------------------------------------------------------------------
	  self.interactiontext_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Drug Interactions")
	  self.sizer_divider_interaction_text = wxBoxSizer(wxHORIZONTAL) 
          self.sizer_divider_interaction_text.Add(self.interactiontext_subheading,1, wxEXPAND)
	  self.interactiontxt = wxTextCtrl(self,-1,
                   "Mini-Drug interaction text goes here (click this for full description)", style=wxTE_MULTILINE)
	  self.interactiontxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,'xselfont'))
	  #------------------------------------------------------------------------------------
          #add the divider headings below the drug interactions as heading for items prescribed
          #------------------------------------------------------------------------------------
          self.itemsprescribedheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Items prescribed this consultation")
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
       	  self.list_script = wxListCtrl(self, ID_SCRIPTLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
          self.list_script.SetFont(wxFont(10,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
	  EVT_RIGHT_UP(self.list_script, self.OnRightMouseUp)
          #----------------------------------------	  
          # add some dummy data to the allergy list
	  self.list_script.InsertColumn(0, "Drug")
	  self.list_script.InsertColumn(1, "Strength")
	  self.list_script.InsertColumn(2, "Directions")
	  self.list_script.InsertColumn(3, "For")
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
          self.mainsizer.Add(self.sizer_authority,2,wxEXPAND)
          self.mainsizer.Add(self.editarea,10,wxEXPAND)
          self.mainsizer.Add(self.sizer_divider_interaction_text,0,wxEXPAND)
       	  self.mainsizer.Add(self.interactiontxt,4,wxEXPAND)
          self.mainsizer.Add(self.itemsprescribedheading,0,wxEXPAND)
	  self.mainsizer.Add(self.list_script,4,wxEXPAND)
          self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
          self.SetSizer(self.mainsizer)
          self.SetAutoLayout(true)
          self.Show(true)
	  
     def OnRightMouseUp(self, event):
	   "A right mouse click triggers a popup menu for the list script"
	   #-------------------
	   #create a popup menu
	   #-------------------
	   self.menu = wxMenu()
	   self.menu.Append(0,"Authority Indications")
	   self.menu.Append(1,"Interactions")
	   self.menu.Append(2, "Pregnancy Information")
	   self.menu.Append(3,"Resticted use Information")
	   self.menu.AppendSeparator()
	   self.menu.Append(4, "Edit Item")
	   self.menu.Append(5,"Delete Item")
	   self.menu.Append(6, "Delete all Items")
	   self.menu.Append(7,"Make Item Reg 24")
	   self.menu.AppendSeparator()
	   self.menu.Append(8, "Brief Product Information")
	   self.menu.Append(9,"Full Product Information")
	   self.menu.AppendSeparator()
	   self.menu.Append(10, "Print Single Item")
	   self.menu.Append(11,"Print All Items")
	   self.menu.AppendSeparator()
	   self.menu.Append(12,"Reprint Item")
	   self.menu.Append(13,"Reprint All Items")
	   self.menu.AppendSeparator()
	   self.menu.Append(14,"Save Item no print")
	   self.menu.Append(15,"Save All Items no printt")
	   self.menu.AppendSeparator()
	   self.menu.Append(16,"Change Font")
	   self.menu.Append(17,"Save list layout")
	   self.menu.AppendSeparator()
	   self.menu.Append(18,"Help")
	   self.menu.AppendSeparator()
	   self.menu.Append(19,"Exit")
	   ##connect the events to event handler functions
	   #EVT_MENU(self, 0, self.OnEncrypt)
	   #EVT_MENU(self, 1, self.OnDecrypt)
	   #EVT_MENU(self, 2, self.OnSetPassphrase)
	   #------------
	   #show the menu 
	   #-------------
	   popup = self.list_script.PopupMenu(self.menu,event.GetPosition()) 
	   # whatever the user selected in the menu will have
	   # been handled already virtue of the MENU events
	   # created above
   
	   #free resources
	   self.menu.Destroy()
   
	   #anybody else needs to intercept right click events?
	   event.Skip()#
	
          
class gmGP_Prescriptions (gmPlugin.wxPatientPlugin):
	"""
	Plugin to encapsulate the prescriptions window
	"""

	__icons = {
"""Rx symbol""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"c\x05Cu\xae\xc4`u=\x85d\x05e\x03 p\xb3\x00\
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
			return self.__icons["""Rx symbol"""]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons["""Rx symbol"""]
	   
	def GetWidget (self, parent):
		return  PrescriptionPanel (parent, -1)


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ImmunisationPanel, -1)
	app.MainLoop()
