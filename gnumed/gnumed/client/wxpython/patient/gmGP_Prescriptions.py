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
from wxPython.wx import wxBitmapFromXPMData, wxImageFromBitmap
import cPickle, zlib   

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
	  
          #self.dummypanel = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
	  #self.dummypanel.SetBackgroundColour(wxColor(200,200,200))
          #-------------------------------------------------
	  #now create the editarea specific for prescribing
	  #-------------------------------------------------
          self.editarea = gmEditArea.EditArea(self,-1,scriptprompts,gmSECTION_SCRIPT)
          #self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
	  #self.dummypanel2.SetBackgroundColour(wxColor(222,222,222))
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
          self.list_script.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
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
      
          
class gmGP_Prescriptions (gmPlugin.wxPatientPlugin):
    """
    Plugin to encapsulate the prescriptions window
    """
    def name (self):
         return 'Prescription writer'

    def MenuInfo (self):
         return ('view', '&Script')

    def GetIcon (self):
         return getpatient_prescriptionsBitmap()

    def GetWidget (self, parent):
         return  PrescriptionPanel (parent, -1)


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ImmunisationPanel, -1)
	app.MainLoop()
               

#----------------------------------------------------------------------
def getpatient_prescriptionsData():
    return cPickle.loads(zlib.decompress(
'x\xda\x8d\x8d\xbd\n\xc30\x0c\x84\xf7<\x85\xa0\x83\x0b\x06!w\xe8\xcf\x16\x08\
d\xac\x87,\xb7\x96\xd2\xad\xd4}\xff\xa9\x96B\x12\x87\xb8\xb4\'c\xf8\xcew\xd6\
\xfe\xf9\x0e\xcd\xe0\xc2\x91\xf29Qp\xcdmp-\xddi\xd7I\'"\xc6^\xb9W\x1d\x8cy\
\xe6\xde8\x1a_t\x8c\xa1|\x16\x1dc\xca|M\xaf\x87A\x9a\xca2=r!\xa2\xc5\x04\xb0\
5\xabI\xfe/\x99RN26&\x10\xa3-[%\xebu\x8c?\xac\xeb\xb5\xe4\xb7\xed\xd0\xbb0=\
\xe0\xe1\xf5\xfc\xaa/\x9a\xcd\xb6\x90\x99\xfc\x01\xe6Ad\xdb' ))

def getpatient_prescriptionsBitmap():
    return wxBitmapFromXPMData(getpatient_prescriptionsData())

def getpatient_prescriptionsImage():
    return wxImageFromBitmap(getpatient_prescriptionsBitmap())

