from wxPython.wx import *
from wxPython.gizmos import *
from wxPython.stc import *
import keyword
ID_ABOUT = 101
ID_EXIT  = 102
ID_FINDPATIENT = 103
class ClinicalSummary(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id)
	self.SetAutoLayout(true)
	self.SetBackgroundColour(wxColour(192,192,192))                              #background is gray
	#------------------------------------------------------------------------
	#Contruct the background shadow which gives 3D effect to the summary page
	#------------------------------------------------------------------------
	self.backshadow =wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 
                           0)                                                        #shadow behind summary panel 
	self.backshadow.SetBackgroundColour(wxColour(131,129,131))                   #is a darker gray then main panel
      	lc = wxLayoutConstraints()                                                   #add layout constraints for sizing   
	lc.top.SameAs(self,wxTop,15)
	lc.left.SameAs(self,wxLeft,15)
        lc.width.PercentOf(self, wxRight, 95)
        lc.height.PercentOf(self,wxHeight,95)
	self.backshadow.SetConstraints(lc)
	#----------------------------------------------------------
	#construct summary panel which will hold all other controls
	#----------------------------------------------------------
	self.summarypanel = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize,
                            wxSIMPLE_BORDER)
        self.summarypanel.SetBackgroundColour(wxWHITE)
	lc = wxLayoutConstraints()
	lc.top.SameAs(self, wxTop,7)
	lc.left.SameAs(self,wxLeft,7)
        lc.right.PercentOf(self, wxRight, 96)
        lc.height.PercentOf(self, wxHeight,95)
        self.summarypanel.SetConstraints(lc)
        #-------------------------------------------------
	#Add a label which will contain the social history
	#-------------------------------------------------
	socialhistory = wxStaticText(self.summarypanel, -1,"Hello, this is my social history")
        lc = wxLayoutConstraints()
        lc.top.SameAs  (self.summarypanel, wxTop, 5)
        lc.left.SameAs (self.summarypanel, wxLeft, 100)
        lc.height.PercentOf (self.summarypanel,wxHeight,15)
	lc.right.PercentOf (self.summarypanel, wxRight,100)
	socialhistory.SetConstraints(lc);
	#---------------------------------------
	#set the label color for social history
	#--------------------------------------
	socialhistory.SetBackgroundColour (wxBLUE) #why doesn't this work.
	socialhistory.SetForegroundColour (wxRED)
	
	#------------------------------------------------
        #add another label for the family history summary
	#------------------------------------------------
	familyhistory = wxStaticText(self.summarypanel, -1,"This is the family history summary")
        lc = wxLayoutConstraints()
        lc.top.Below(socialhistory)
        lc.left.SameAs (self.summarypanel, wxLeft, 100)
        lc.height.PercentOf (self.summarypanel,wxHeight,12)
	lc.right.PercentOf (self.summarypanel, wxRight,100)
	familyhistory.SetConstraints(lc);

	#--------------------------------------------------------------------------
	#draw the dividing panel between family history and the active problem list
	#--------------------------------------------------------------------------
	paneltop = wxPanel(self.summarypanel,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(familyhistory)
	lc.height.PercentOf(self.summarypanel,wxHeight,4)
	lc.left.SameAs(self.summarypanel, wxLeft, 0)
	lc.width.PercentOf(self.summarypanel, wxWidth,100)
	paneltop.SetConstraints(lc);
	paneltop.SetBackgroundColour(wxColour(197,194,255))
	#------------------------------------------------------------
	#put a caption in the middle of this (probably an easier way?
	#------------------------------------------------------------
	paneltop_caption = wxStaticText(paneltop,-1, 'Active Problems')
	
	lc = wxLayoutConstraints()
        lc.top.SameAs(paneltop,wxTop,1)
        lc.left.SameAs (paneltop, wxLeft, 100)
	lc.width.SameAs(paneltop,wxWidth)
        lc.height.PercentOf (paneltop,wxHeight,100)
	lc.centreX.SameAs(paneltop,wxCentreX)
	paneltop_caption.SetConstraints(lc);
	paneltop_caption.SetForegroundColour(wxWHITE)
	
	paneltop_caption.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'verdana'))

	
	activeproblemsamplelist =['1980 Hypertension','1982 Acute myocardial infartion', '1992 NIDDM']
	activeproblem_listbox = wxListBox(self.summarypanel,-1,wxDefaultPosition, wxDefaultSize, activeproblemsamplelist,
                            wxLB_SINGLE)
	
	activeproblem_listbox.SetBackgroundColour(wxColor(255,255,197))
	lc = wxLayoutConstraints()
	lc.top.Below(paneltop)
	lc.height.PercentOf(self.summarypanel,wxHeight,20)
	lc.left.SameAs(self.summarypanel, wxLeft, 0)
	lc.width.PercentOf(self.summarypanel, wxWidth,100)
	activeproblem_listbox.SetConstraints(lc);

	#--------------------------------------------------------------------------
	#draw the dividing panel between the active problem list and habits info
	#--------------------------------------------------------------------------
	panel_habitsheading = wxPanel(self.summarypanel,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(activeproblem_listbox)
	lc.height.PercentOf(self.summarypanel,wxHeight,4)
	lc.left.SameAs(self.summarypanel, wxLeft, 0)
	lc.width.PercentOf(self.summarypanel, wxWidth,100)
	panel_habitsheading.SetConstraints(lc);
	panel_habitsheading.SetBackgroundColour(wxColour(197,194,255))
	#----------------------------------------------------
	#put a caption "Habit"in the middle of left hand side
	#----------------------------------------------------
	panel_habitheading_caption = wxStaticText(panel_habitsheading,-1, 'Habits')
	lc = wxLayoutConstraints()
        lc.top.SameAs(panel_habitsheading,wxTop,1)
        lc.left.SameAs (panel_habitsheading, wxLeft, 100)
	lc.width.PercentOf(panel_habitsheading,wxWidth,50)
        lc.height.PercentOf (panel_habitsheading,wxHeight,100)
	lc.centreX.SameAs(panel_habitsheading,wxCentreX)
	panel_habitheading_caption.SetConstraints(lc);
	panel_habitheading_caption.SetForegroundColour(wxWHITE)
	panel_habitheading_caption.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,'verdana'))
	#------------------------------------------------------------
	#put a caption "Risk Factors"in the middle of right hand side
	#------------------------------------------------------------
	panel_riskfactors_heading_caption = wxStaticText(panel_habitsheading,-1, 'Risk Factors')
	lc = wxLayoutConstraints()
        lc.top.SameAs(panel_habitsheading,wxTop,1)
        lc.left.SameAs (panel_habitheading_caption, wxLeft, 100)
	lc.width.PercentOf(panel_habitsheading,wxWidth,50)
        lc.height.PercentOf (panel_habitsheading,wxHeight,100)
	#lc.centreX.SameAs(panel_habitsheading,wxCentreX)
	panel_riskfactors_heading_caption.SetConstraints(lc);
	panel_riskfactors_heading_caption.SetForegroundColour(wxWHITE)
	panel_riskfactors_heading_caption.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,'verdana'))

	#-------------------------------------------------
	#Add a label which will contain the habits stuff
	#-------------------------------------------------
	habithistory_lbl = wxStaticText(self.summarypanel, -1,'Smoker 20/day')
        lc = wxLayoutConstraints()
        lc.top.Below  (panel_habitsheading)
        lc.left.SameAs (self.summarypanel, wxLeft, 0)
        lc.height.PercentOf (self.summarypanel,wxHeight,12)
	lc.right.PercentOf (self.summarypanel, wxRight,100)
	habithistory_lbl.SetConstraints(lc);
	#--------------------------------------------------------------------------
	#draw the dividing panel between the habits info and patient inbox
	#--------------------------------------------------------------------------
	panel_inboxheading = wxPanel(self.summarypanel,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(habithistory_lbl)
	lc.height.PercentOf(self.summarypanel,wxHeight,4)
	lc.left.SameAs(self.summarypanel, wxLeft, 0)
	lc.width.PercentOf(self.summarypanel, wxWidth,100)
	panel_inboxheading.SetConstraints(lc);
	panel_inboxheading.SetBackgroundColour(wxColour(197,194,255))
	#------------------------------------------------------------
	#put a caption in the middle of this (probably an easier way?
	#------------------------------------------------------------
	panel_inboxheading_caption = wxStaticText(panel_inboxheading,-1, 'Inbox')
	lc = wxLayoutConstraints()
        lc.top.SameAs(panel_inboxheading,wxTop,1)
        lc.left.SameAs (panel_inboxheading, wxLeft, 100)
	lc.width.SameAs(panel_inboxheading,wxWidth)
        lc.height.PercentOf (panel_inboxheading,wxHeight,100)
	lc.centreX.SameAs(panel_inboxheading,wxCentreX)
	panel_inboxheading_caption.SetConstraints(lc);
	panel_inboxheading_caption.SetForegroundColour(wxWHITE)
	panel_inboxheading_caption.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,'verdana'))
	#---------------------------------------------------------------------------
	#add a listbox to contain the outstanding tasks list eg pathology unread etc
	#---------------------------------------------------------------------------
	
	inbox_samplelist =['Pathology:    5 unread results (Douglas Pathology)','Radiology:    1 Xray of femur (Newcastle radiology)', 
		    '                :    Head CT (Hunter Diagnostic Imaging)','Letter      :     Dr Imall heart', 'Message:     from practice nurse - non urgent']
	inbox_listbox = wxListBox(self.summarypanel,-1,wxDefaultPosition, wxDefaultSize, inbox_samplelist,
                            wxLB_SINGLE)
	
	lc = wxLayoutConstraints()
	lc.top.Below(panel_inboxheading)
	lc.height.PercentOf(self.summarypanel, wxHeight, 20)
	lc.left.SameAs(self.summarypanel, wxLeft, 0)
	lc.width.PercentOf(self.summarypanel, wxWidth,100)
        inbox_listbox.SetConstraints(lc);



if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ClinicalSummary, -1)
	app.MainLoop()
 
