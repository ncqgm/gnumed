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
		        "The information in the lists and text boxes below is completely dummy stuff.\n\n"
		          "When Karsten and Ian finish the wxWordWheel.py then I'll be\n\n"
		          "able to finish designing the editing area!!!! \n\n"
                                      "which by rights, should occupy the space this text box does \n\n"
     		 	  "View this screen about 1/2 the size of your monitor width. Bye for now...\n\n",  
                                       size = (200,100), style=wxTE_MULTILINE)
          
          self.dummypanel2 = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,0)
          #-----------------------------------------------
          #add the divider headings below the editing area
          #-----------------------------------------------
          self.drug_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Drug and Reaction")
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
          #self.allergy_list  = wxListCtrl(self,ID_ALLERGYLIST, wxDefaultPosition, wxDefaultSize, style = 0)
	  #--------------------------------------------------------------------------
	  # OR: Add a simple listcontrol under that for recall items and insert dummy data
	  #--------------------------------------------------------------------------
	  allergysamplelist =['Allergy        -Definate-  Celecoxib   Generic specific Uricaria',
		       "Sensitivity    -Definate-   Macrolides   Class reaction    vomiting"]

	  self.allergy_list = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, allergysamplelist,
                            wxLB_SINGLE)
          #list_allergy.SetForegroundColour(wxColor(255,0,0))
	  self.allergy_list.SetFont(wxFont(14,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
          #--------------------------------------------------------------------------------------
          #add a richtext control or a wxTextCtrl multiline to display the class text information
          #e.g. would contain say information re the penicillins
          #--------------------------------------------------------------------------------------
          self.classtext_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Class notes for celecoxib")
          self.classtxt = wxTextCtrl(self,-1,
                   "A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
 
                                        
                                          size=(200, 100), style=wxTE_MULTILINE)
	  self.classtxt.SetFont(wxFont(14,wxSWISS,wxNORMAL,wxNORMAL,false,'xselfont'))
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
          self.mainsizer.Add(self.allergy_list,4,wxEXPAND)
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
         frame = MyFrame(NULL, -1, "gnuMEdGP_PreAlphaGUI__AllergyPanel_V0.0.1", 
		                           wxDefaultPosition, size = wxSize(600,500),
		                           style= wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
         frame.Show (true)
         self.SetTopWindow(frame)
         return true
    
if __name__ == "__main__":
    app = App(0)
    app.MainLoop()