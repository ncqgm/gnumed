#!/usr/bin/python
#############################################################################
#
# gmimmunisations
# ----------------------------------
#
# This panel will hold all the immunisation details
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
#	
#      
############################################################################

from wxPython.wx import *
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmEditArea_1h             #panel class holding editing prompts and text boxes
import gmPlugin
import images_gnuMedGP_Toolbar
ID_IMMUNISATIONLIST = wxNewId()
ID_IMMUNISATIONS = wxNewId()
ID_ALL_MENU  = wxNewId()

gmSECTION_IMMUNISATIONS = 6
#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
scheduledata = {
1 : ("Influenza","null"),
2 : ("Tetanus","null"),
3 : ("Typhoid","null"),
}
vaccinedata = {
1 : ("Fluvax","15/03/2001"),
2 : ("Vaxigrip","22/04/2002"),
}

immunisationprompts = {
1:("Target Disease"),
2:("Vaccine"),
3:("Date Given"),
4:("Serial No."),
5:("Site injected"),
6:("Progress Notes"),
7:("")    
 }

class ImmunisationPanel(wxPanel):
       def __init__(self, parent,id):
	  wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)                     
     
          #--------------------
          #add the main heading
          #--------------------
          self.immunisationpanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  IMMUNISATIONS  ")
          #--------------------------------------------
          #dummy panel will later hold the editing area
          #--------------------------------------------
          self.dummypanel1 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
	  self.dummypanel1.SetBackgroundColour(wxColor(222,222,222))
          #--------------------------------------------------
	  #now create the editarea specific for immunisations
	  #--------------------------------------------------
          self.editarea = gmEditArea_1h.EditArea(self,-1,immunisationprompts,gmSECTION_IMMUNISATIONS)
          #self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
	  #self.dummypanel2.SetBackgroundColour(wxColor(222,222,222))
          #-----------------------------------------------
          #add the divider headings below the editing area
          #-----------------------------------------------
          self.disease_schedule_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Disease or Schedule")
	  self.vaccine_given_heading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Vaccine Given")
          self.sizer_divider_schedule_vaccinegiven = wxBoxSizer(wxHORIZONTAL) 
          self.sizer_divider_schedule_vaccinegiven.Add(self.disease_schedule_heading,1, wxEXPAND)
	  self.sizer_divider_schedule_vaccinegiven.Add( self.vaccine_given_heading,1, wxEXPAND)
	  
          #--------------------------------------------------------------------------------------                                                                               
          #add the list to contain the drugs person is allergic to
          #
          # c++ Default Constructor:
          # wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
          # const wxSize& size = wxDefaultSize, long style = wxLC_ICON, 
          # const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
	  #
          #--------------------------------------------------------------------------------------
       	  self.disease_schedule_list = wxListCtrl(self, ID_IMMUNISATIONLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
          self.disease_schedule_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
	  self.schedule_vaccine_given_list = wxListCtrl(self, ID_IMMUNISATIONLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
          self.schedule_vaccine_given_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))

	  self.sizer_schedule_vaccine = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_schedule_vaccine.Add(self.disease_schedule_list,4,wxEXPAND)
	  self.sizer_schedule_vaccine.Add(self.schedule_vaccine_given_list,6, wxEXPAND)
	  
          #-----------------------------------------	  
          # add some dummy data to the Schedule list
	  #-----------------------------------------
	  self.disease_schedule_list.InsertColumn(0, "Schedule")
	  self.disease_schedule_list.InsertColumn(1, "null")
	  #-------------------------------------------------------------
          #loop through the scheduledata array and add to the list control
	  #note the different syntax for the first coloum of each row
	  #i.e. here > self.disease_schedule_list.InsertStringItem(x, data[0])!!
	  #-------------------------------------------------------------
	  items = scheduledata.items()
	  for x in range(len(items)):
	      key, data = items[x]
	      print items[x]
	      #print x, data[0],data[1],data[2]
	      self.disease_schedule_list.InsertStringItem(x, data[0])
	      #self.disease_schedule_list.SetStringItem(x, 1, data[1])
	      #self.disease_schedule_list.SetStringItem(x, 2, data[2])
	      #self.disease_schedule_list.SetStringItem(x, 3, data[3])
	      #self.disease_schedule_list.SetStringItem(x, 4, data[4])
	      self.disease_schedule_list.SetItemData(x, key)
	  self.disease_schedule_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
          #self.disease_schedule_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(2, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(3, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(4, wxLIST_AUTOSIZE)
	  
	   #-----------------------------------------	  
          # add some dummy data to the vaccines list
	  #-----------------------------------------
	  self.schedule_vaccine_given_list.InsertColumn(0, "Vaccine")
	  self.schedule_vaccine_given_list.InsertColumn(1, "null")
	  #-------------------------------------------------------------
          #loop through the scheduledata array and add to the list control
	  #note the different syntax for the first coloum of each row
	  #i.e. here > self.disease_schedule_list.InsertStringItem(x, data[0])!!
	  #-------------------------------------------------------------
	  items = vaccinedata.items()
	  for x in range(len(items)):
	      key, data = items[x]
	      print items[x]
	      #print x, data[0],data[1],data[2]
	      self.schedule_vaccine_given_list.InsertStringItem(x, data[0])
	     
	      self.schedule_vaccine_given_list.SetStringItem(x, 1, data[1])
	      #self.disease_schedule_list.SetStringItem(x, 2, data[2])
	      #self.disease_schedule_list.SetStringItem(x, 3, data[3])
	      #self.disease_schedule_list.SetStringItem(x, 4, data[4])
	      self.schedule_vaccine_given_list.SetItemData(x, key)
	  self.schedule_vaccine_given_list.SetColumnWidth(0, wxLIST_AUTOSIZE)
          self.schedule_vaccine_given_list.SetColumnWidth(1, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(2, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(3, wxLIST_AUTOSIZE)
	  #self.disease_schedule_list.SetColumnWidth(4, wxLIST_AUTOSIZE)
	  #--------------------------------------------------------------------------------------
          #add a richtext control or a wxTextCtrl multiline to display the class text information
          #e.g. would contain say information re the penicillins
          #--------------------------------------------------------------------------------------
          self.missing_immunisations_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Missing Immunisations")
          self.missingimmunisationtxt = wxTextCtrl(self,-1, "Schedule: Pneumococcal - no vaccination recorded",
                   
                                        
                                          size=(200, 100), style=wxTE_MULTILINE)
	  self.missingimmunisationtxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,'xselfont'))
          #----------------------------------------
          #add an alert caption panel to the bottom
          #----------------------------------------
          self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
          #---------------------------------------------                                                                               
          #add all elements to the main background sizer
          #---------------------------------------------
          self.mainsizer = wxBoxSizer(wxVERTICAL)
          self.mainsizer.Add(self.immunisationpanelheading,0,wxEXPAND)
          self.mainsizer.Add(self.dummypanel1,1,wxEXPAND)
          self.mainsizer.Add(self.editarea,6,wxEXPAND)
          #self.mainsizer.Add(self.dummypanel2,1,wxEXPAND)
          self.mainsizer.Add(self.sizer_divider_schedule_vaccinegiven,0,wxEXPAND)
          self.mainsizer.Add( self.sizer_schedule_vaccine,4,wxEXPAND)
          self.mainsizer.Add(self.missing_immunisations_subheading,0,wxEXPAND)
          self.mainsizer.Add(self.missingimmunisationtxt,4,wxEXPAND)
          self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
          self.SetSizer(self.mainsizer)
          self.mainsizer.Fit
          self.SetAutoLayout(true)
      
class gmGP_Immunisation (gmPlugin.wxSmallPagePlugin):
    """
    Plugin to encapsulate the allergies window
    """
    
    def name (self):
           return 'Immunisations Window'

    def MenuInfo (self):
           return ('view', '&Immunisation')

    def GetIcon (self):
           return images_gnuMedGP_Toolbar.getToolbar_ImmunisationBitmap()

    def GetWidget (self, parent):
           return ImmunisationPanel (parent, -1)
          
          

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ImmunisationPanel, -1)
	app.MainLoop()
           

