
from wxPython.wx import *
import images
import images_gnuMedGP_Toolbar
import images_gnuMedGP_TabbedLists           #bitmaps for tabs on notebook
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
import gmGP_ClinicalSummary
import gmGP_TabbedLists
import gmGP_ScratchPadRecalls
#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

ID_OVERVIEW = wxNewId()
ID_PATIENTDETAILS = wxNewId()
ID_CLINICALNOTES  = wxNewId()
ID_FAMILYHISTORY  = wxNewId()
ID_PASTHISTORY  = wxNewId()
ID_IMMUNISATIONS = wxNewId()
ID_ALLERGY = wxNewId()
ID_REQUESTS  = wxNewId()
ID_REFERRALS  = wxNewId()
ID_RECALLS  = wxNewId()
ID_PROGRESSNOTES  = wxNewId()
ID_BMI = wxNewId()
ID_CALCULATOR = wxNewId()
ID_EXIT = wxNewId()
ID_CALENDAR = wxNewId()
ID_PREGCALC = wxNewId()
ID_CONTENTS = wxNewId()
ID_SEARCHFORHELPON = wxNewId()
ID_TECHNICALSUPPORT = wxNewId()
ID_ABOUT = wxNewId() 	


#--------------------------------------------------------------------
# A class for displaying a patients entire medical record
# form of a social history, family history, active problems, habits
# risk factos and an inbox
# This code is shit and needs fixing, here for gui development only
# TODO:almost everything
#--------------------------------------------------------------------	

class PatientMain(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,0)
	
	#----------------------------------------------------------------------------- 
        #create the sizer to occupy the area between the sizer containing the toolbars
	#and the status bar. This central container will contain the main panels and will
	#have a border round it's entirity. 
	#-----------------------------------------------------------------------------
	self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
	#-------------------------------------------------------------------------------
	#create instance of the gui panels which will first load for the patients screen
	#-------------------------------------------------------------------------------
	self.summarypanel = gmGP_ClinicalSummary.ClinicalSummary(self,-1)
	self.tabbedlists = gmGP_TabbedLists.TabbedLists(self,-1)
	self.scratchpadrecalls =  gmGP_ScratchPadRecalls.ScratchPadRecalls(self,-1)
	#------------------------------------------------------------------------------
	#this sizer will contains the summary paneland the shadow underneath this panel
	#------------------------------------------------------------------------------
        self.szr_left_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)               #will hold summary + shadow under
        szr_left_shadow_under = wxBoxSizer (wxHORIZONTAL)                                #sizer to hold space and shadow
	szr_left_shadow_under.Add(20,20,0,wxEXPAND)                                      #1:add the space
	self.left_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)     #2:create window to be the shadow
	self.left_shadow_under.SetBackgroundColour(wxColor(131,129,131))                 #3:and make it gray
        szr_left_shadow_under.Add(self.left_shadow_under,12,wxEXPAND)                    #4:add the gray shadow after space
	self.sizer_swap_panel = wxBoxSizer(wxHORIZONTAL)
	self.sizer_swap_panel.Add(self.summarypanel,1,wxEXPAND)
	self.szr_left_main_panel_and_shadow_under.Add(self.sizer_swap_panel, 97,wxEXPAND)    #5:add summary panel
	self.szr_left_main_panel_and_shadow_under.Add(szr_left_shadow_under,2,wxEXPAND)  #6:add the shadow under the top panel 
	#-----------------------------------------------------------------------
        #now make the shadow to the right of the summary panel, out of a
	#vertical sizer, with a spacer at the top and a button filling the rest
	#-----------------------------------------------------------------------
	self.left_shadow_vertical = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	self.left_shadow_vertical.SetBackgroundColour(wxColor(131,129,131)) 
	self.szr_left_shadow_vertical = wxBoxSizer(wxVERTICAL)
	self.szr_left_shadow_vertical.Add(40,20,0,wxEXPAND) #1:add the space
	self.szr_left_shadow_vertical.Add(self.left_shadow_vertical,1,wxEXPAND)
	#-------------------------------------------------------------------------
	#now make a vertical box sizer to hold the right main panel(which contains
	#the tabbed lists, the scratch pad and the review/recalls due 
	#-------------------------------------------------------------------------
	self.szr_right_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)             #sizer will hold lists + scratchrecalls
	self.szr_right_shadow_under = wxBoxSizer (wxHORIZONTAL)                         #will hold shadow under the lists
	self.right_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)   #create window to be shadow    
	self.right_shadow_under.SetBackgroundColour(wxColor(131,129,131))               #make this gray
	self.szr_right_main_panel_and_shadow_under.Add(self.tabbedlists,40,wxEXPAND)
	self.szr_right_main_panel_and_shadow_under.Add(self.scratchpadrecalls,55,wxEXPAND)
	self.szr_right_shadow_under.Add(20,20,0,wxEXPAND)                               #1:add the space at start of shadow
	self.szr_right_shadow_under.Add(self.right_shadow_under,12,wxEXPAND)
	self.szr_right_main_panel_and_shadow_under.Add(self.szr_right_shadow_under,1,wxEXPAND)
	#-----------------------------------------------------------------------
        #now make the shadow to the right of the tabbed lists panel, out of a
	#vertical sizer, with a spacer at the top and a button filling the rest
	#-----------------------------------------------------------------------
	self.right_shadow_vertical = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	self.right_shadow_vertical.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	self.szr_right_shadow_vertical = wxBoxSizer(wxVERTICAL)
	self.szr_right_shadow_vertical.Add(40,60,0,wxEXPAND) #1:add the space
	self.szr_right_shadow_vertical.Add(self.right_shadow_vertical,1,wxEXPAND)

	#-------------------------------------------
	#add the shadow under the main summary panel
	#-------------------------------------------
	self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
	self.szr_main_panels.Add(self.szr_left_main_panel_and_shadow_under,53,wxEXPAND)
	self.szr_main_panels.Add(self.szr_left_shadow_vertical,1,wxEXPAND)
	self.szr_main_panels.Add(10,20,0,wxEXPAND)
	self.szr_main_panels.Add(self.szr_right_main_panel_and_shadow_under,40,wxEXPAND)
	self.szr_main_panels.Add(self.szr_right_shadow_vertical,1,wxEXPAND)
	self.szr_central_container.Add(self.szr_main_panels,1,wxEXPAND|wxALL,5)
	#--------------------------------------------------------------------
        #now create the  the main sizer to contain all the others on the form
	#--------------------------------------------------------------------
	self.szr_main_container = wxBoxSizer(wxVERTICAL)
	#--------------------------------------------------------------------------
       	#Now add the top panel to the main background sizer of the whole frame, and
	#underneath that add a panel for demo purposes
	#--------------------------------------------------------------------------
	#self.szr_main_container.Add(self.szr_top_panel,1,wxEXPAND)
	self.szr_main_container.Add(self.szr_central_container,10, wxEXPAND)
        self.SetSizer(self.szr_main_container)        #set the sizer 
	self.szr_main_container.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)                          #show the frame   
        
  
	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 300))
	app.SetWidget(PatientMain, -1)
	app.MainLoop()
 
