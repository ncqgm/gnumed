
from wxPython.wx import *

#---------------------------------------------------------------------------   
#Creates all the sizers necessary to hold the top two menu's, picture
#from for patients picture, the main two left and right panels, with shadows
#---------------------------------------------------------------------------

class TestFrame(wxFrame):
    def __init__(self,parent, id,title,position,size):
        wxFrame.__init__(self,parent, id,title,position, size)
        EVT_CLOSE(self, self.OnCloseWindow)
	
	#----------------------------------------------------------------------------
	#create a horizontal sizer which will contain all windows at the top of the
	#screen (ie menu's and picture panel - which are on sub sizers)
        #add a wxPanel to this sizer which sits on the left and occupies 90% of width
        #followed by panel for the patients picture which occupies 10%. Add labels for
	#demo patients
	#-----------------------------------------------------------------------------
        szr_top_panel = wxBoxSizer(wxHORIZONTAL)            
	pnl_for_tool_bars = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,wxSIMPLE_BORDER)
	lbl_for_tool_bars = wxStaticText(pnl_for_tool_bars, -1, 
	       "THIS WILL CONTAIN TWO TOOL BARS AND SITS AT TOP OF SCREEN", wxDefaultPosition, wxDefaultSize)
	szr_top_panel.Add(pnl_for_tool_bars, 9,wxEXPAND)
	pnl_for_patient_picture = wxPanel(self,-1,wxDefaultPosition,wxDefaultSize,wxSIMPLE_BORDER)
	lbl_pnl_for_patient_picture = wxStaticText(pnl_for_patient_picture, -1, 
						   "PATIENT PICTURE", wxDefaultPosition, wxDefaultSize)
	szr_top_panel.Add(pnl_for_patient_picture,1,wxEXPAND)
	#----------------------------------------------------------------------------- 
        #create the sizer to occupy the area between the sizer containing the toolbars
	#and the status bar. This central container will contain the main panels and will
	#have a border round it's entirity. 
	#-----------------------------------------------------------------------------
	szr_central_container = wxBoxSizer(wxHORIZONTAL)
	b1 = wxButton(self,-1,"summary panel will go here")
	b6 = wxButton(self,-1,"This contains tabbed lists etc")
		
	#------------------------------------------------------------------
	#this sizer contains the summary panel and all other panels and the
	#shadow underneath this panel
	#------------------------------------------------------------------
        szr_left_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)
        szr_left_main_panel_and_shadow_under.Add(b1, 97,wxEXPAND) #replace with summary panel
	#-------------------------------------------------------------------------
	#now construct the sizer to contain the shadow underneath
	#this horizontal sizer contains a space and the right aligned gray shadow
	#-------------------------------------------------------------------------
	left_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	left_shadow_under.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	szr_left_shadow_under = wxBoxSizer (wxHORIZONTAL)          #Hsizer will have two things on it
        szr_left_shadow_under.Add(20,20,0,wxEXPAND) #1:add the space
	szr_left_shadow_under.Add(left_shadow_under,12,wxEXPAND)
	szr_left_main_panel_and_shadow_under.Add(szr_left_shadow_under,2,wxEXPAND)
	#-----------------------------------------------------------------------
        #now make the shadow to the right of the summary panel, out of a
	#vertical sizer, with a spacer at the top and a button filling the rest
	#-----------------------------------------------------------------------
	left_shadow_vertical = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	left_shadow_vertical.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	szr_left_shadow_vertical = wxBoxSizer(wxVERTICAL)
	szr_left_shadow_vertical.Add(40,20,0,wxEXPAND) #1:add the space
	szr_left_shadow_vertical.Add(left_shadow_vertical,1,wxEXPAND)
	#-------------------------------------------------------------------------
	#now make a vertical box sizer to hold the right main panel(which contains
	#the tabbed lists, the scratch pad and the review/recalls due and put
	#the horizontal sizer to contain the backshadow under this
	#-------------------------------------------------------------------------
	right_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	right_shadow_under.SetBackgroundColour(wxColor(131,129,131))          #gray shadow under the panel
	szr_right_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)
	szr_right_main_panel_and_shadow_under.Add(b6,97,wxEXPAND)
	szr_right_shadow_under = wxBoxSizer (wxHORIZONTAL)         
        szr_right_shadow_under.Add(20,20,0,wxEXPAND)                          #1:add the space at start of shadow
	szr_right_shadow_under.Add(right_shadow_under,12,wxEXPAND)
	szr_right_main_panel_and_shadow_under.Add(szr_right_shadow_under,2,wxEXPAND)
	#-----------------------------------------------------------------------
        #now make the shadow to the right of the tabbed lists panel, out of a
	#vertical sizer, with a spacer at the top and a button filling the rest
	#-----------------------------------------------------------------------
	right_shadow_vertical = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	right_shadow_vertical.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	szr_right_shadow_vertical = wxBoxSizer(wxVERTICAL)
	szr_right_shadow_vertical.Add(40,20,0,wxEXPAND) #1:add the space
	szr_right_shadow_vertical.Add(right_shadow_vertical,1,wxEXPAND)

	#-------------------------------------------
	#add the shadow under the main summary panel
	#-------------------------------------------
	szr_main_panels = wxBoxSizer(wxHORIZONTAL)
	szr_main_panels.Add(szr_left_main_panel_and_shadow_under,55,wxEXPAND)
	szr_main_panels.Add(szr_left_shadow_vertical,1,wxEXPAND)
	szr_main_panels.Add(10,20,0,wxEXPAND)
	szr_main_panels.Add(szr_right_main_panel_and_shadow_under,38,wxEXPAND)
	szr_main_panels.Add(szr_right_shadow_vertical,1,wxEXPAND)
	szr_central_container.Add(szr_main_panels,1,wxEXPAND|wxALL,5)
	#--------------------------------------------------------------------
        #now create the  the main sizer to contain all the others on the form
	#--------------------------------------------------------------------
	szr_main_container = wxBoxSizer(wxVERTICAL)
	#--------------------------------------------------------------------------
       	#Now add the top panel to the main background sizer of the whole frame, and
	#underneath that add a panel for demo purposes
	#--------------------------------------------------------------------------
	szr_main_container.Add(szr_top_panel,1,wxEXPAND)
	szr_main_container.Add(szr_central_container,9, wxEXPAND)
        self.SetSizer(szr_main_container)        #set the sizer 
	szr_main_container.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)                          #show the frame   
        
	
  
    def OnCloseWindow(self, event):
        self.Destroy()
    
class App(wxApp):
    def OnInit(self):
        frame = TestFrame(NULL, -1, "gnuMEdGP_PreAlphaGUI__SizerVersion_V0.0.1",wxDefaultPosition,size=(800,600))
        self.SetTopWindow(frame)
        return true


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()