#!/usr/bin/python
from wxPython.wx import *
import images
import images_gnuMedGP_Toolbar
import images_gnuMedGP_TabbedLists           #bitmaps for tabs on notebook
import gmGuiElement_HeadingCaptionPanel        #panel class to display top headings
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing alert messages
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin

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
#--------------------------------------------------
#Dummy data to simulate previously prescribed items
#--------------------------------------------------
scriptdata = {
1 : ("Adalat Oris", "30mg","1 mane","21/01/2002", "Hypertension","30 Rpt5","29/02/2000"),
2 : ("Nitrolingual Spray","", "1 spray when needed","24/08/2001", "Angina","1 Rpt2","01/06/2001"),
3 : ("Losec", "20mg","1 mane", "21/01/2002","Reflux Oesophagitis","30 Rpt5","16/11/2001"),
4 : ("Zoloft", "50mg","1 mane", "24/04/2002","Depression","30 Rpt0","24/04/2002"),
}
scratchpaddata = {
1 : ("01/12/2001", "check BP next visit"),
2 : ("01/12/2001", "daughter requests dementia screen"),
}
recalldata = {
1 : ("Annual Checkup", "due in 1 month"),
2 : ("PAP smear", "overdue 6 months"),
}
#---------------------------------------------------------------------------   
#This class consists of a panel + sizer + static text control
#used to display heading over anothe wigit eg. Active problem list
#expects title, rgb colours of foreground and background
#TODO: HOW TO PUT IN DEFAULT COLOURS
#---------------------------------------------------------------------------
class Patient_Demographic_details(wxPanel):
      def __init__(self, parent, id):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSUNKEN_BORDER )	
	b1 = wxButton(self,-1,"This panel will have all the demographic details on it")
	self.sizer = wxBoxSizer(wxVERTICAL)
	self.sizer.Add(b1)
	self.SetSizer(self.sizer)
	self.sizer(Fit)
	self.AutoLayout(true)
	self.Show(true)
	       
class Patient_Picture_Panel(wxPanel):
    def __init__(self, parent, id):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSUNKEN_BORDER )	
	
	self.sizer = wxBoxSizer(wxVERTICAL)
	#AT A BITMAP FOR PATIENT PICTURE
	wxImage_AddHandler(wxPNGHandler())
	bitmap = "any_body2.png"
	png = wxImage(bitmap, wxBITMAP_TYPE_PNG).ConvertToBitmap()
	bmp = wxStaticBitmap(self, -1, png, wxPoint(0, 0), wxSize(png.GetWidth(), png.GetHeight()))
	self.sizer.Add(bmp, 0, wxGROW|wxALIGN_CENTER_VERTICAL) # |wxALL, 10)
        self.SetSizer(self.sizer)  #set the sizer 
	self.sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
class Wigit_Caption_Panel1(wxPanel):
    def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )	
	sizer = wxBoxSizer(wxVERTICAL)	
	self.SetCaptionBackgroundColor()                                               #set background colour  
        self.caption = wxStaticText(self,-1, title,style = wxALIGN_CENTRE) #add static text control for the capion
	self.SetCaptionForegroundColor()                                               #set caption text colour 
	caption.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
        sizer.Add(caption,1,wxEXPAND)                                      #add caption to the sizer
	self.SetSizer(sizer)                                               #set the sizer 
	sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                                           #tell frame to use the sizer
        self.Show(true)                                                    #show the panel   
	
    def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
	self.SetBackgroundColour(wxColour(bg_red,bg_blue,bg_green))
			  
    def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
	self.caption.SetForegroundColour(wxColour(fg_red,fg_blue,fg_green))
	return
     
#class gnuMedGP_Caption_Panel(wxPanel):
    #def __init__(self, parent, id, title):
    	#wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )	
	#sizer = wxBoxSizer(wxVERTICAL)	
	#self.SetBackgroundColour(wxColour(197,194,255))   
	##SetCaptionBackgroundColor()                                               #set background colour  
        #caption = wxStaticText(self,-1, title,style = wxALIGN_CENTRE) #add static text control for the capion
        #caption.SetForegroundColour(wxWHITE)	
         ##SetCaptionForegroundColor()                                               #set caption text colour 
	#caption.SetFont(wxFont(14,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
        #sizer.Add(caption,1,wxEXPAND)                                      #add caption to the sizer
	#self.SetSizer(sizer)                                               #set the sizer 
	#sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
        #self.SetAutoLayout(true)                                           #tell frame to use the sizer
        #self.Show(true)                                                    #show the panel   
	
    #def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
	#self.SetBackgroundColour(wxColour(bg_red,bg_blue,bg_green))
			  
    #def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
	#self.caption.SetForegroundColour(wxColour(fg_red,fg_blue,fg_green))
	#return

#--------------------------------------------------------------------
# A class for displaying social history
# This code is shit and needs fixing, here for gui development only
# TODO: Pass social history text to this panel not display fixed text
#--------------------------------------------------------------------
class Social_History(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	txt_social_history = wxTextCtrl(self, 30,
                        "Born in QLD, son of an itinerant drover. Mother worked as a bush nurse. "
                        "Two brothers, Fred and Peter. Left school aged 15yrs, apprentice fitter "
                        "then worked in industry for 10ys. At 22yrs age married Joan, two children"
                        "Peter b1980 and Rachaelb1981. Retired in 1990 due to receiving a fortune.",
                        #"previously unknown great aunt. Interests include surfing, fishing, carpentry",                       ,
                       wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
        txt_social_history.SetInsertionPoint(0)
	txt_social_history.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
	#self.textCtrl1.SetFont(wxFont(14, wxSWISS, wxNORMAL, wxBOLD, false, 'verdana'))
        sizer.Add(txt_social_history,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
#--------------------------------------------------------------------
# A class for displaying patients active problems
# This code is shit and needs fixing, here for gui development only
# TODO: almost everything
#--------------------------------------------------------------------
class ActiveProblem_List(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	activeproblemsamplelist =['1980 Hypertension','1982 Acute myocardial infartion', '1992 NIDDM']
	sizer = wxBoxSizer(wxVERTICAL)
       
	activeproblems_listbox = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, activeproblemsamplelist,
                            wxLB_SINGLE)
        sizer.Add(activeproblems_listbox,100,wxEXPAND)
	activeproblems_listbox.SetBackgroundColour(wxColor(255,255,197))
	activeproblems_listbox.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
	self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
#--------------------------------------------------------------------
# A class for displaying social history
# This code is shit and needs fixing, here for gui development only
# TODO: Pass social history text to this panel not display fixed text
#--------------------------------------------------------------------
class Family_History(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	txt_family_history = wxTextCtrl(self, 30,
                        "FAMILY HISTORY: Stroke(father-died72yrs);NIDDM(general - maternal).\n",
                         wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
        txt_family_history.SetInsertionPoint(0)
	txt_family_history.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxNORMAL, false,'xselfont'))
	txt_family_history.SetForegroundColour(wxColour(1, 1, 255))
        sizer.Add(txt_family_history,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 



#--------------------------------------------------------------------
# A class for displaying a summary of patients clinical data in the
# form of a social history, family history, active problems, habits
# risk factos and an inbox
# This code is shit and needs fixing, here for gui development only
# TODO:almost everything
#--------------------------------------------------------------------	

class Clinical_Summary(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxSIMPLE_BORDER)
	sizer = wxBoxSizer(wxVERTICAL)
	social_history = Social_History(self,-1)
	
        family_history = Family_History(self,-1)
	activeproblem_list = ActiveProblem_List(self,-1)
	habits_riskfactors = Habits_RiskFactors(self,-1)
	inbox = Inbox(self,-1)
	heading1 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Active Problems" )                         
        heading2 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"     Habits            Risk Factors")
	heading3 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Inbox")
	sizer= wxBoxSizer(wxVERTICAL)
	sizer.Add(social_history,5,wxEXPAND)
	sizer.Add(family_history,5,wxEXPAND)
	sizer.Add(heading1,0,wxEXPAND)   
	sizer.Add(activeproblem_list,8,wxEXPAND)
	sizer.Add(heading2,0,wxEXPAND)  
	sizer.Add(habits_riskfactors,5,wxEXPAND)
	sizer.Add(heading3,0,wxEXPAND)  
	sizer.Add(inbox,5,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
class ScratchPad_RecallReviews1(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
	#add a label which is the heading for the text data entry 'Scratchpad' 	
	scratchpad_lbl = wxStaticText(self,-1, "Scratch Pad",style = wxALIGN_CENTRE) #add static text control for the capion
	scratchpad_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	scratchpad_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
	#Add a text control under that
	scratchpad_txt = wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize,0)
	#Add a label for the recalls/reviews list
	recalls_lbl = wxStaticText(self,-1, "Recalls/Reviews",style = wxALIGN_CENTRE) #add static text control for the capion
	recalls_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	recalls_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))

        #------------------------------------------------------------------------------
	#Add a simple listcontrol under that for scratchpad items and insert dummy data
	#------------------------------------------------------------------------------
	list_scratchpad = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
	list_scratchpad.InsertColumn(0, "Logged")
	list_scratchpad.InsertColumn(1, "", wxLIST_FORMAT_LEFT)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = scratchpaddata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1]
	    list_scratchpad.InsertStringItem(x, data[0])
            list_scratchpad.SetStringItem(x, 1, data[1])
            list_scratchpad.SetItemData(x, key)
	list_scratchpad.SetColumnWidth(0, wxLIST_AUTOSIZE)
        list_scratchpad.SetColumnWidth(1, 200)
	#--------------------------------------------------------------------------
	#Add a simple listcontrol under that for recall items and insert dummy data
	#--------------------------------------------------------------------------
	list_recalls = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
	list_recalls.InsertColumn(0, "Recall or Review")
	list_recalls.InsertColumn(1, "Status", wxLIST_FORMAT_LEFT)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = recalldata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1]
	    list_recalls.InsertStringItem(x, data[0])
            list_recalls.SetStringItem(x, 1, data[1])
            list_recalls.SetItemData(x, key)
	list_recalls.SetColumnWidth(0, wxLIST_AUTOSIZE)
        list_recalls.SetColumnWidth(1, 200)

        sizer= wxBoxSizer(wxVERTICAL)
	sizer.Add(scratchpad_lbl,0,wxEXPAND)
	sizer.Add(scratchpad_txt,0,wxEXPAND)
	#sizer.Add(10,10,0,wxEXPAND)
        sizer.Add(list_scratchpad,30,wxEXPAND) 
	sizer.Add(recalls_lbl,0, wxEXPAND)
	#sizer.Add(5,5,0,wxEXPAND)
	sizer.Add(list_recalls,70,wxEXPAND)
	self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
#----------------------------------------------------------------
#This one uses a simple list box which I think is more attractive
#----------------------------------------------------------------
class ScratchPad_RecallReviews(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
	#add a label which is the heading for the text data entry 'Scratchpad' 	
	scratchpad_lbl = wxStaticText(self,-1, "Scratch Pad",style = wxALIGN_CENTRE) #add static text control for the capion
	scratchpad_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	scratchpad_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
	#Add a text control under that
	scratchpad_txt = wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize,0)
	#Add a label for the recalls/reviews list
	recalls_lbl = wxStaticText(self,-1, "Recalls/Reviews",style = wxALIGN_CENTRE) #add static text control for the capion
	recalls_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	recalls_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
	scratchpadsamplelist =['01/12/2001     Check BP next visit','12/01/2002     ?compliance problem with meds', '12/01/2002     cat died, may still be depressed']
	list_scratchpad = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, scratchpadsamplelist,
                            wxLB_SINGLE)
        list_scratchpad.SetForegroundColour(wxColor(255,0,0))
	list_scratchpad.SetFont(wxFont(11,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
	recallsamplelist =['NIDDM           Overdue 6 Months','PROSTATE  Due in 1 month', 'Iron Studies   Due Now']

	list_recalls = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, recallsamplelist,
                            wxLB_SINGLE)
        list_recalls.SetForegroundColour(wxColor(255,0,0))
	list_recalls.SetFont(wxFont(11,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))

        sizer= wxBoxSizer(wxVERTICAL)
	sizer.Add(scratchpad_lbl,0,wxEXPAND)
	sizer.Add(scratchpad_txt,0,wxEXPAND)
	#sizer.Add(10,10,0,wxEXPAND)
        sizer.Add(list_scratchpad,30,wxEXPAND) 
	sizer.Add(recalls_lbl,0, wxEXPAND)
	#sizer.Add(5,5,0,wxEXPAND)
	sizer.Add(list_recalls,70,wxEXPAND)
	self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 


class Habits_RiskFactors(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	#captions for the two columns
	habit_caption = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Habits")
	risk_caption =gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Risk Factors")
	#text controls for each column      
	txt_habits = wxTextCtrl(self, 30,
                        "Smoker - 30/day.\n",
			#"Alcohol - 30gm/day (Previously very heavy.\n",
                              wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
	#txt_family_history = wxTextCtrl(self, 30,
                        #"FAMILY HISTORY: Stroke(father-died72yrs);NIDDM(general - maternal).\n",
                         #wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
	
	
        txt_habits.SetInsertionPoint(0)
	
	txt_riskfactors = wxTextCtrl(self,30,
			     "Hypercholesterolaemia \n",
			     #"Current Smoker \n",
			     #"NIDDM \n",
                             #"No exercise data recorded\n",
			      wxDefaultPosition,wxDefaultSize, style = wxTE_MULTILINE)
	txt_riskfactors.SetInsertionPoint(0)
	#heading sizer- add headings
	heading_sizer = wxBoxSizer(wxHORIZONTAL)
	heading_sizer.Add(habit_caption,50,wxEXPAND)
	heading_sizer.Add(risk_caption,50,wxEXPAND)
	self.SetSizer(heading_sizer)  #set the sizer 
	heading_sizer.Fit(self)             #set
	##text sizer - add text
        text_sizer = wxBoxSizer(wxHORIZONTAL)
	text_sizer.Add(txt_habits,50,wxEXPAND)
	text_sizer.Add(txt_riskfactors,50,wxEXPAND)
	self.SetSizer(text_sizer)  #set the sizer 
	text_sizer.Fit(self)             #set
	##stick heading and text onto a verticalbox sizer
        #back_sizer = wxBoxSizer(wxVERTICAL)
	#back_sizer.Add(heading_sizer,1,wxEXPAND)
        #back_sizer.Add(text_sizer,99,wxEXPAND)
	#self.SetSizer(back_sizer)  #set the sizer 
	#back_sizer.Fit(self)             #set
	#sizer.Add(heading_sizer,1,wxEXPAND)
	#sizer.Add(back_sizer,1,wxEXPAND)
        #self.SetSizer(sizer)  #set the sizer 
	#sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
class Inbox(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	inbox_samplelist =['Pathology:    5 unread results (Douglas Pathology)','Radiology:    1 Xray of femur (Newcastle radiology)', 
		    '                :    Head CT (Hunter Diagnostic Imaging)','Letter      :     Dr Imall heart', 'Message:     from practice nurse - non urgent']
	inbox_listbox = wxListBox(self,-1,wxDefaultPosition, wxDefaultSize, inbox_samplelist,
                            wxLB_SINGLE)
	inbox_listbox.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxNORMAL, false,'xselfont'))
	sizer = wxBoxSizer(wxVERTICAL)
	sizer.Add(inbox_listbox,100,wxEXPAND)
        self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
		
class ToolBar_Panel(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER )
	#----------------------------------------------------------------
	#horizontal sizer holds first the patient picture panel, then the
	#two vertically stacked toolbars
	#----------------------------------------------------------------
        self.sizer_back = wxBoxSizer(wxHORIZONTAL) 
	self.sizer_left = wxBoxSizer(wxVERTICAL)
        self.SetBackgroundColour(wxColour(222,222,222)) #(197,194,197)) #222,218,222
	#-------------------------------------------------------------------------
	#create the top toolbar with the findpatient, age and allergies text boxes
        #-------------------------------------------------------------------------
        tb2 = wxToolBar(self,-1,wxDefaultPosition,wxDefaultSize,wxTB_HORIZONTAL|wxRAISED_BORDER|wxTB_FLAT)
        self.ToolBar2 = tb2
        tb2.SetToolBitmapSize((21,21))
	ID_FINDPATIENTLBL = wxNewId()
	ID_FINDPATIENTTXT = wxNewId()
	
        tb2.AddSeparator()
	tb2.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_FindPatientBitmap(),
                          shortHelpString="Find a patient")
	tb2.AddControl(wxTextCtrl(tb2, ID_FINDPATIENTTXT, name ="txtFindPatient",size =(300,-1),style = 0, value = ''))
	tb2.AddSeparator()	
	tb2.AddControl(wxStaticText(tb2, ID_FINDPATIENTLBL, label ='Age', name = 'lblAge',size = (30,-1), style = 0))
	tb2.AddSeparator()
        tb2.AddControl(wxTextCtrl(tb2, ID_FINDPATIENTTXT, name ="txtFindPatient",size =(30,-1),style = 0, value = ''))
	tb2.AddSeparator()	
	tb2.AddControl(wxStaticText(tb2, ID_FINDPATIENTLBL, label ='Allergies', name = 'lblAge',size = (50,-1), style = 0))
	tb2.AddControl(wxTextCtrl(tb2, ID_FINDPATIENTTXT, name ="txtFindPatient",size =(250,-1),style = 0, value = ''))
	tb2.Realize
	#-------------------------------------------------------------------------
	#create the second tool bar underneath which will hold most of the buttons
	#-------------------------------------------------------------------------
	tb1 = wxToolBar(self,-1,wxDefaultPosition,wxDefaultSize,wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
        self.ToolBar1 = tb1
        tb1.SetToolBitmapSize((16,16))
	EVT_TOOL(self, 30, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 30, self.OnToolRClick)
	EVT_TOOL(self, 40, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 40, self.OnToolRClick)
	EVT_TOOL(self, 50, self.OnToolClick)
	
	EVT_TOOL(self, ID_PATIENTDETAILS, self.OnPatientDetailsClicked)

        #EVT_TOOL_ENTER(self, -1, self.OnToolEnter)
        #EVT_TOOL_RCLICKED(self, -1, self.OnToolRClick)  # Match all
	tb1.AddSeparator()
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_HomeBitmap(),
                          shortHelpString="Overview of patients records")
	#add a custom separator to the toolbar
	tb1.AddControl(wxStaticBitmap(tb1, -1, images_gnuMedGP_Toolbar.getCustom_SeparatorBitmap(), wxDefaultPosition, wxDefaultSize))
	tool1 = tb1.AddTool(ID_PATIENTDETAILS, images_gnuMedGP_Toolbar.getToolbar_ManBitmap(),
                          shortHelpString="Demographic details for patient")
		#EVT_TOOL(self, ID_MOVE_MODE_BUTTON, self.SetMode)
	tb1.AddControl(wxStaticBitmap(tb1, -1, images_gnuMedGP_Toolbar.getCustom_SeparatorBitmap(), wxDefaultPosition, wxDefaultSize))
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_FamilyHistoryBitmap(),
                          shortHelpString="Family History")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_PastHistoryBitmap(),
                          shortHelpString="Past History")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_ImmunizationsBitmap(),
                          shortHelpString="Immunisations")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_AllergiesBitmap(),
                          shortHelpString="Allergies")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_ScriptBitmap(),
		     shortHelpString="Prescriptions")
        tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_RequestsBitmap(),
                          shortHelpString="Requests e.g pathology")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_MeasurementsBitmap(),
                          shortHelpString="Measurements")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_ReferralsBitmap(),
                          shortHelpString="Referrals or letters")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_RecallsBitmap(),
                          shortHelpString="Recalls")
	tb1.AddControl(wxStaticBitmap(tb1, -1, images_gnuMedGP_Toolbar.getCustom_SeparatorBitmap(), wxDefaultPosition, wxDefaultSize))

	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_BMICalcBitmap(),
                          shortHelpString="Body Mass Index Calculator")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_CalculatorBitmap(),
                          shortHelpString="Dosage Calculator")
	
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_CalendarBitmap(),
                          shortHelpString="Calendar")
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_PregcalcBitmap(),
                          shortHelpString="Pregnancy Calculator")
	#tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_ContactsBitmap(),
         
                 #shortHelpString="Toggle this")
	tb1.AddControl(wxStaticBitmap(tb1, -1, images_gnuMedGP_Toolbar.getCustom_SeparatorBitmap(), wxDefaultPosition, wxDefaultSize))
	  
	tb1.AddSeparator()
	tb1.AddSeparator()
	tb1.AddSeparator()
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_ProgressNotesBitmap(),
                          shortHelpString="Progress NOtes")
	tb1.AddSeparator()
	tb1.AddSeparator()
	tb1.AddSeparator()
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_PrinterBitmap(),
                          shortHelpString="Printer")
	tb1.AddSeparator()
	tb1.AddSeparator()
	tb1.AddSeparator()
	tool1 = tb1.AddTool(50, images_gnuMedGP_Toolbar.getToolbar_SaveBitmap(),
                          shortHelpString="Save changes")
	tb1.AddSeparator()
	tb1.AddSeparator()
	tb1.AddSeparator()
        cbID = wxNewId()
        tb1.AddControl(wxComboBox(tb1, cbID, "surgery consultation", choices=["surgery consultation", "home visit", "phone consultation", "patient absent"],
                                 size=(150,-1), style=wxCB_DROPDOWN))
        EVT_COMBOBOX(self, cbID, self.OnCombo)

    	tb1.Realize()
	
	self.sizer_left.Add(1,3,0,wxEXPAND)		  
        self.sizer_left.Add(tb2,0,wxEXPAND)
        self.sizer_left.Add(tb1,100,wxEXPAND)
	self.szr_patient_picture = wxBoxSizer(wxVERTICAL)
	self.patient_picture = Patient_Picture_Panel(self,-1)
	self.szr_patient_picture.Add(self.patient_picture,1,0)
	self.sizer_back.Add(10,0,0)
	self.sizer_back.Add(self.szr_patient_picture,1,wxEXPAND)
	self.sizer_back.Add(self.sizer_left,14,wxEXPAND)
	self.SetSizer(self.sizer_back)  #set the sizer 
	self.sizer_back.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 
	
    def OnPatientDetailsClicked(self, event):	
	TestFrame.szr_left_main_panel_and_shadow_under.Remove(self.summary_panel)
	
	self.summary_panel = None
	self.patientdemographicdetails = Patient_Demographic_details(self,-1)
	TestFrame.szr_left_main_panel_and_shadow_under(self.patientdemographicdetails,1,wxEXPAND)
	TestFrame.szr_left_main_panel_and_shadow_under.Layout()
	
	
    def OnToolClick(self, event):
        self.log.WriteText("tool %s clicked\n" % event.GetId())

    def OnToolRClick(self, event):
        self.log.WriteText("tool %s right-clicked\n" % event.GetId())

    def OnCombo(self, event):
        self.log.WriteText("combobox item selected: %s\n" % event.GetString())

    def OnToolEnter(self, event):
        self.log.WriteText('OnToolEnter: %s, %s\n' % (event.GetId(), event.GetInt()))
        if self.timer is None:
            self.timer = wxTimer(self)
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer.Start(2000)
        event.Skip()	
class TestFrame(wxFrame):
    def __init__(self,parent, id,title,position,size):
        wxFrame.__init__(self,parent, id,title,position, size)
        EVT_CLOSE(self, self.OnCloseWindow)
	self.CreateMenu()
	self.CreateStatusBar()
	self.CreateSizers()

    def CreateSizers(self):
	#----------------------------------------------------------------------------
	#create a horizontal sizer which will contain all windows at the top of the
	#screen (ie menu's and picture panel - which are on sub sizers)
        #add a wxPanel to this sizer which sits on the left and occupies 90% of width
        #followed by panel for the patients picture which occupies 10%. Add labels for
	#demo patients
	#-----------------------------------------------------------------------------
        self.szr_top_panel = wxBoxSizer(wxHORIZONTAL) 
        toolbars = ToolBar_Panel(self,-1)
	self.szr_top_panel.Add(toolbars,1,wxEXPAND)
	#----------------------------------------------------------------------------- 
        #create the sizer to occupy the area between the sizer containing the toolbars
	#and the status bar. This central container will contain the main panels and will
	#have a border round it's entirity. 
	#-----------------------------------------------------------------------------
	self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
	#-----------------------------------------------------------------------
	#this sizer will contains the summary panel and all other panels and the
	#shadow underneath this panel
	#----------------------------------------------------------------------
        self.summary_panel = Clinical_Summary(self,-1)
        self.szr_left_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)
        self.szr_left_main_panel_and_shadow_under.Add(self.summary_panel, 97,wxEXPAND) #replace with summary panel
	#-------------------------------------------------------------------------
	#now construct the sizer to contain the shadow underneath
	#this horizontal sizer contains a space and the right aligned gray shadow
	#-------------------------------------------------------------------------
	self.left_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	self.left_shadow_under.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	szr_left_shadow_under = wxBoxSizer (wxHORIZONTAL)          #Hsizer will have two things on it
        szr_left_shadow_under.Add(20,20,0,wxEXPAND) #1:add the space
	szr_left_shadow_under.Add(self.left_shadow_under,12,wxEXPAND)
	self.szr_left_main_panel_and_shadow_under.Add(szr_left_shadow_under,2,wxEXPAND)
	#-----------------------------------------------------------------------
        #now make the shadow to the right of the summary panel, out of a
	#vertical sizer, with a spacer at the top and a button filling the rest
	#-----------------------------------------------------------------------
	self.left_shadow_vertical = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	self.left_shadow_vertical.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
	self.szr_left_shadow_vertical = wxBoxSizer(wxVERTICAL)
	self.szr_left_shadow_vertical.Add(40,20,0,wxEXPAND) #1:add the space
	self.szr_left_shadow_vertical.Add(self.left_shadow_vertical,1,wxEXPAND)
	#-------------------------------------------------------------------------
	#now make a vertical box sizer to hold the right main panel(which contains
	#the tabbed lists, the scratch pad and the review/recalls due and put
	#the horizontal sizer to contain the backshadow under this
	#-------------------------------------------------------------------------
	self.right_shadow_under = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
	self.right_shadow_under.SetBackgroundColour(wxColor(131,129,131))          #gray shadow under the panel
	self.szr_right_main_panel_and_shadow_under = wxBoxSizer(wxVERTICAL)
	#==============================================================
	#NOTEBOOK STUFF NOTEBOOK STUFF NOTEBOOK STUFF NOTEBOOKSTUFF
	#===========================================================
	#-----------------------------------------------------
	#create imagelist for use by the lists in the notebook
	#e.g the icons to sort the columns up and down
	#-----------------------------------------------------
	self.ListsImageList= wxImageList(16,16)
	self.small_arrow_up = self.ListsImageList.Add(images.getSmallUpArrowBitmap())
        self.small_arrow_down = self.ListsImageList.Add(images.getSmallDnArrowBitmap())
	#------------------------------------------------------------------------
	#----------------------------------------------------------------------
	#Add a notebook control to hold the lists of things eg scripts, recalls
	#----------------------------------------------------------------------
	self.notebook1 = wxNotebook(self, -1, wxDefaultPosition, wxDefaultSize, style = 0)
	#-------------------------------------------------------------------------
	#Associate an imagelist with the notebook and add images to the image list
	#-------------------------------------------------------------------------
	tabimage_Script = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = tabimage_Requests = -1
        self.notebook1.il = wxImageList(16, 16)
        tabimage_Script = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ScriptBitmap())
        tabimage_Requests = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RequestsBitmap())
	tabimage_Measurements = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_MeasurementsBitmap())
	tabimage_Referrals = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ReferralsBitmap())
	tabimage_Recalls = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RecallsBitmap())
	tabimage_Inbox = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_Letters_ReceivedBitmap())
	self.notebook1.SetImageList(self.notebook1.il)
	szr_notebook = wxNotebookSizer(self.notebook1)
	#----------------------------------------------------------------------------------
	#now create the lists that will sit on the notebook pages, and add them to the page
	#----------------------------------------------------------------------------------
	#medstatus_lbl = wxStaticText(self,-1, "Active Medications",style = wxALIGN_CENTRE) #add static text control for the capion
	#medstatus_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	#medstatus_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
        szr_script_page= wxBoxSizer(wxVERTICAL)
	#szr_script_page.Add(medstatus_lbl,0,wxEXPAND)
	ListScript_ID = wxNewId()                                                         #can use wxLC_VRULES to put faint cols in list
       	self.List_Script = wxListCtrl(self.notebook1, ListScript_ID,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxSUNKEN_BORDER)
        szr_script_page.Add(self.List_Script,100,wxEXPAND)
        self.List_Script.SetForegroundColour(wxColor(131,129,131))	
	self.List_Requests = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Measurements = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Referrals = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Recalls = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.List_Inbox = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,wxSUNKEN_BORDER)
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Inbox, pPage = self.List_Script, strText = '')
	#self.notebook1.AddPage(bSelect = true, imageId = tabimage_Inbox, pPage = szr_script_page, strText = '')

	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Requests, pPage = self.List_Requests, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Measurements, pPage = self.List_Measurements, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Referrals, pPage = self.List_Referrals, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Recalls, pPage = self.List_Recalls, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_Inbox, pPage = self.List_Inbox, strText = '')
        self.notebook1.SetSelection(0)                               #start on scriptpage
#--------------------------------------
	#Now lets do things to the script list:
	#--------------------------------------
	self.List_Script.SetImageList(self.ListsImageList, wxIMAGE_LIST_SMALL)
	#------------------------------------------------------------------------
	# since we want images on the column header we have to do it the hard way
	#------------------------------------------------------------------------
	info = wxListItem()
	info.m_mask = wxLIST_MASK_TEXT | wxLIST_MASK_IMAGE | wxLIST_MASK_FORMAT
	info.m_image = -1
	info.m_format = 0
	info.m_text = "Drug"
	self.List_Script.InsertColumnInfo(0, info)

	
	info.m_format = wxLIST_FORMAT_LEFT
	info.m_text = "Dose"
	self.List_Script.InsertColumnInfo(1, info)
	
	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Instructions"
	self.List_Script.InsertColumnInfo(2, info)

	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Last Date"
	self.List_Script.InsertColumnInfo(3, info)
	
	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Prescribed For"
	self.List_Script.InsertColumnInfo(4, info)
	
	
	info.m_format = wxLIST_FORMAT_RIGHT
	info.m_text = "Quantity"
	self.List_Script.InsertColumnInfo(5, info)
	
	
	info.m_format = 0
	info.m_text = "First Date"
	self.List_Script.InsertColumnInfo(6, info)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = scriptdata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1],data[2]
	    self.List_Script.InsertStringItem(x, data[0])
            self.List_Script.SetStringItem(x, 1, data[1])
            self.List_Script.SetStringItem(x, 2, data[2])
	    self.List_Script.SetStringItem(x, 3, data[3])
	    self.List_Script.SetStringItem(x, 4, data[4])
	    self.List_Script.SetStringItem(x, 5, data[5])
	    self.List_Script.SetStringItem(x, 6, data[6])
	    self.List_Script.SetItemData(x, key)
	#--------------------------------------------------------
	#note the number pased to the wxColumnSorterMixin must be
	#the 1 based count of columns
	#--------------------------------------------------------
        self.itemDataMap = scriptdata        
        #wxColumnSorterMixin.__init__(self, 5)              #I excluded first date as it didn't sort
	
	self.List_Script.SetColumnWidth(0, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(1, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(2, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(3, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(4, wxLIST_AUTOSIZE)
	self.List_Script.SetColumnWidth(5, wxLIST_AUTOSIZE)
        self.List_Script.SetColumnWidth(6, 150)
	#self.__sizer.AddSizer(self.__nbs, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )
	self.szr_right_main_panel_and_shadow_under.AddSizer(szr_notebook,40,wxEXPAND)
	scratchpad_recalls_reviews = ScratchPad_RecallReviews(self,-1)
	self.szr_right_main_panel_and_shadow_under.Add(scratchpad_recalls_reviews,55,wxEXPAND)
	self.szr_right_shadow_under = wxBoxSizer (wxHORIZONTAL)         
        self.szr_right_shadow_under.Add(20,20,0,wxEXPAND)                          #1:add the space at start of shadow
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
	self.szr_main_container.Add(self.szr_top_panel,1,wxEXPAND)
	self.szr_main_container.Add(self.szr_central_container,10, wxEXPAND)
        self.SetSizer(self.szr_main_container)        #set the sizer 
	self.szr_main_container.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)                          #show the frame   
        
    def Notify(self):
	"Displays date and local time in the second slot of the status bar"

	t = time.localtime(time.time())
	st = time.strftime(gmTimeformat, t)
	self.SetStatusText(st,1)

    def SetupStatusBar(self):
	self.CreateStatusBar(2, wxST_SIZEGRIP)
	#add time and date display to the right corner of the status bar
	self.timer = wxPyTimer(self.Notify)
	#update every second
	self.timer.Start(1000)
	self.Notify()

    def OnFileExit(self, event):
	    self.Close()



    def CleanExit(self):
	    """This function should ALWAYS be called when this
	    program is to be terminated.
	    ANY code that should be executed before a regular shutdown
	    should go in here
	    """
	    self.timer.Stop ()
	    self.mainmenu=None
	    self.window=None
	    self.Destroy()



    def OnClose(self,event):
	    self.CleanExit()




    def OnIdle(self, event):
	    """Here we can process any background tasks
	    """
	    pass



    def OnIconize(self, event):
	    wxLogMessage('OnIconify')



    def OnMaximize(self, event):
		wxLogMessage('OnMaximize')
		
    def OnCloseWindow(self, event):
        self.Destroy()
    def CreateMenu(self):
	
	menu_file = wxMenu()
        menu_file.Append(ID_EXIT, "E&xit", "Terminate the program")
	menuBar = wxMenuBar()
	#-------------------------
	#View menu
	#-------------------------
	menu_view = wxMenu()
	menu_view.Append(ID_OVERVIEW,"&Overview", "Overview of patients medical record")
	menu_view.AppendSeparator()
	menu_view.Append(ID_PATIENTDETAILS,"Patient Details")
	menu_view.Append(ID_CLINICALNOTES,"Clinical Notes")
	menu_view.Append(ID_FAMILYHISTORY,"Family History")
	menu_view.Append(ID_PASTHISTORY,"Past History")
	menu_view.Append(ID_IMMUNISATIONS,"Immunisations")
	menu_view.Append(ID_ALLERGY,"Allergies")
	menu_view.Append(ID_REQUESTS,"Requests")
	menu_view.Append(ID_REFERRALS,"Referrals")
	menu_view.Append(ID_RECALLS,"Recalls")
	menu_view.Append(ID_PROGRESSNOTES,"Progress Notes")
	menu_tools = wxMenu()
	menu_tools.Append(ID_BMI,"BMI Calculator", "Body mass index calculator")
	menu_tools.Append(ID_CALCULATOR,"Calculator", "Calculator")
	menu_tools.Append(ID_CALENDAR,"Calendar", "Calendar")
	menu_tools.Append(ID_PREGCALC,"Pregnancy Calculator", "Pregnancy Calculator")
        menu_help = wxMenu()
	menu_help.Append(ID_CONTENTS,"Contents", "Contents for gnuMedGP Help")
	menu_help.AppendSeparator()
	menu_help.Append(ID_SEARCHFORHELPON,"Search for help on", "Search for help on topic")
	menu_help.Append(ID_TECHNICALSUPPORT,"Technical Support", "Obstain technical support")
	menu_help.AppendSeparator()
	menu_help.Append(ID_ABOUT,"About gnuMedGP", "")
        menuBar.Append(menu_file, "&File");
	menuBar.Append(menu_view, "&View");
	menuBar.Append(menu_tools, "&Tools");
	menuBar.Append(menu_help, "&Help");
	self.SetMenuBar(menuBar)
	
class App(wxApp):
    def OnInit(self):
        frame = TestFrame(NULL, -1, "gnuMedGP_PreAlphaGUI__SizerVersion_V0.0.1J",wxDefaultPosition,size=(800,600))
        self.SetTopWindow(frame)
        return true


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()
