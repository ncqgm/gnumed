#!/usr/bin/python
#############################################################################
#
# gmAllergies:
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
ID_ALLERGYLIST = wxNewId()
#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
allergydata = {
1 : ("penicillin","Allergy", "definate","amoxycillin trihydrate","anaphylaxis"),
2 : ("macrolides","Sensitivity","definate", "erythromycin ethyl succinate", "nausea and vomiting"),
3 : ( "celecoxib","Allergy","definate","celecoxib", "allergic drug rash"),
}
class MyFrame(wxFrame):
     def __init__(self,parent,ID,title,position,size,style):
          wxFrame.__init__(self,parent,ID,title,
                           wxDefaultPosition,wxSize(600,550))
          #def __init__(self,parent, id,title,position,size,style):
		#wxFrame.__init__(self,parent, id,title,wxDefaultPosition,wxDefaultSize,style)
          ##--------------------
          #add the main heading
          #--------------------
          self.allergypanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"  ALLERGIES  ")
          #--------------------------------------------
          #dummy panel will later hold the editing area
          #--------------------------------------------
          self.dummypanel = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
          self.messagetxt = wxTextCtrl(self,-1,
                        "Hi Guys, this is a prototype Allergy Panel. Comments please to rterry@gnumed.net..\n\n"
		        "The information in the lists and text boxes below is completely dummy stuff.\n"
		          "When Karsten and Ian finish the wxWordWheel.py then I'll be\n"
		          "able to finish designing the editing area!!!! \n"
                                      "which by rights, should occupy the space this text box does \n\N"
     		 	  "View this screen about 1/2 the size of your monitor width. Bye for now...\n\n",  
                                       size = (200,100), style=wxTE_MULTILINE)
          
          self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
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
          #self.list_allergy.SetForegroundColour(wxColor(131,129,131))	
	  self.list_allergy.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
          #----------------------------------------	  
          # add some dummy data to the allergy list
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
	      print items[x]
	      #print x, data[0],data[1],data[2]
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
          #----------------------------------------
          #add an alert caption panel to the bottom
          #----------------------------------------
          self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
          #---------------------------------------------                                                                               
          #add all elements to the main background sizer
          #---------------------------------------------
          self.mainsizer = wxBoxSizer(wxVERTICAL)
          self.mainsizer.Add(self.allergypanelheading,0,wxEXPAND)
          self.mainsizer.Add(self.dummypanel,1,wxEXPAND)
          self.mainsizer.Add(self.messagetxt,4,wxEXPAND)
          self.mainsizer.Add(self.dummypanel2,1,wxEXPAND)
          self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
          self.mainsizer.Add(self.list_allergy,4,wxEXPAND)
          self.mainsizer.Add(self.classtext_subheading,0,wxEXPAND)
          self.mainsizer.Add(self.classtxt,4,wxEXPAND)
          self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
          self.SetSizer(self.mainsizer)
          self.mainsizer.Fit
          self.SetAutoLayout(true)
          self.Show(true)
          
          
          
          
class App(wxApp):
     def OnInit(self):
         #frame = MyFrame(NULL,-1,"Allergies")
         frame = MyFrame(NULL, -1, "gnuMEdGP_PreAlphaGUI__AllergyPanel_V0.0.2", 
		                           wxDefaultPosition, size = wxSize(600,500),
		                           style= wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
         frame.Show (true)
         self.SetTopWindow(frame)
         return true
    
if __name__ == "__main__":
    app = App(0)
    app.MainLoop()