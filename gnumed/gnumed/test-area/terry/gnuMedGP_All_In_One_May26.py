from wxPython.wx import *
from wxPython.gizmos import *
from wxPython.stc import *
import keyword
import time
import images
import images_gnuMedGP_TabbedLists
ID_ABOUT = 101
ID_EXIT  = 102
ID_FINDPATIENT = 103
class MyPanel(wxPanel):
    def __init__(self, parent):
	wxPanel.__init__(self, parent, -1)
	self.SetAutoLayout(true)
	#----------------------------------------
	#background of the entire windows is gray
	#----------------------------------------
	self.SetBackgroundColour(wxColour(192,192,192))
	#----------------------------------------------
	#now add the shadow underneath the main display
	#----------------------------------------------
	self.panel_shadow_under =wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 
                           0)
	self.panel_shadow_under.SetBackgroundColour(wxColour(131,129,131))
      	lc = wxLayoutConstraints()
	lc.top.SameAs(self,wxTop,15)
	lc.left.SameAs(self,wxLeft,15)
        lc.width.PercentOf(self, wxRight, 55.5)
        lc.height.PercentOf(self,wxHeight,95)
	self.panel_shadow_under.SetConstraints(lc)
	#-------------------------------
	#construct left hand white panel
	#-------------------------------
	self.panelB = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize,
                            wxSIMPLE_BORDER)
        self.panelB.SetBackgroundColour(wxWHITE)
	lc = wxLayoutConstraints()
	lc.top.SameAs(self, wxTop,7)
	lc.left.SameAs(self,wxLeft,7)
        lc.right.PercentOf(self, wxRight, 56)
        lc.height.PercentOf(self, wxHeight,95)
        self.panelB.SetConstraints(lc)
		
	#-------------------------------------------------
	#Add a label which will contain the social history
	#-------------------------------------------------
	socialhistory = wxStaticText(self.panelB, -1,"Hello, this is my social history")
        lc = wxLayoutConstraints()
        lc.top.SameAs  (self.panelB, wxTop, 5)
        lc.left.SameAs (self.panelB, wxLeft, 100)
        lc.height.PercentOf (self.panelB,wxHeight,15)
	lc.right.PercentOf (self.panelB, wxRight,100)
	socialhistory.SetConstraints(lc);
	#---------------------------------------
	#set the label color for social history
	#--------------------------------------
	socialhistory.SetBackgroundColour (wxBLUE) #why doesn't this work.
	socialhistory.SetForegroundColour (wxRED)
	
	#------------------------------------------------
        #add another label for the family history summary
	#------------------------------------------------
	familyhistory = wxStaticText(self.panelB, -1,"This is the family history summary")
        lc = wxLayoutConstraints()
        lc.top.Below(socialhistory)
        lc.left.SameAs (self.panelB, wxLeft, 100)
        lc.height.PercentOf (self.panelB,wxHeight,12)
	lc.right.PercentOf (self.panelB, wxRight,100)
	familyhistory.SetConstraints(lc);

	#--------------------------------------------------------------------------
	#draw the dividing panel between family history and the active problem list
	#--------------------------------------------------------------------------
	paneltop = wxPanel(self.panelB,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(familyhistory)
	lc.height.PercentOf(self.panelB,wxHeight,4)
	lc.left.SameAs(self.panelB, wxLeft, 0)
	lc.width.PercentOf(self.panelB, wxWidth,100)
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
	activeproblem_listbox = wxListBox(self.panelB,-1,wxDefaultPosition, wxDefaultSize, activeproblemsamplelist,
                            wxLB_SINGLE)
	
	activeproblem_listbox.SetBackgroundColour(wxColor(255,255,197))
	lc = wxLayoutConstraints()
	lc.top.Below(paneltop)
	lc.height.PercentOf(self.panelB,wxHeight,20)
	lc.left.SameAs(self.panelB, wxLeft, 0)
	lc.width.PercentOf(self.panelB, wxWidth,100)
	activeproblem_listbox.SetConstraints(lc);

	#--------------------------------------------------------------------------
	#draw the dividing panel between the active problem list and habits info
	#--------------------------------------------------------------------------
	panel_habitsheading = wxPanel(self.panelB,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(activeproblem_listbox)
	lc.height.PercentOf(self.panelB,wxHeight,4)
	lc.left.SameAs(self.panelB, wxLeft, 0)
	lc.width.PercentOf(self.panelB, wxWidth,100)
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
	habithistory_lbl = wxStaticText(self.panelB, -1,'Smoker 20/day')
        lc = wxLayoutConstraints()
        lc.top.Below  (panel_habitsheading)
        lc.left.SameAs (self.panelB, wxLeft, 0)
        lc.height.PercentOf (self.panelB,wxHeight,12)
	lc.right.PercentOf (self.panelB, wxRight,100)
	habithistory_lbl.SetConstraints(lc);
	#--------------------------------------------------------------------------
	#draw the dividing panel between the habits info and patient inbox
	#--------------------------------------------------------------------------
	panel_inboxheading = wxPanel(self.panelB,-1,wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
	lc = wxLayoutConstraints()
	lc.top.Below(habithistory_lbl)
	lc.height.PercentOf(self.panelB,wxHeight,4)
	lc.left.SameAs(self.panelB, wxLeft, 0)
	lc.width.PercentOf(self.panelB, wxWidth,100)
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
	inbox_listbox = wxListBox(self.panelB,-1,wxDefaultPosition, wxDefaultSize, inbox_samplelist,
                            wxLB_SINGLE)
	
	lc = wxLayoutConstraints()
	lc.top.Below(panel_inboxheading)
	lc.height.PercentOf(self.panelB, wxHeight, 20)
	lc.left.SameAs(self.panelB, wxLeft, 0)
	lc.width.PercentOf(self.panelB, wxWidth,100)
        inbox_listbox.SetConstraints(lc);

	#-----------------------------------------------------------------------
	#now add the shadow underneath the right hand side of the screen
	#---------------------------------------------------------------
	self.panel_shadow_under_right =wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 
                           0)
	self.panel_shadow_under_right.SetBackgroundColour(wxColour(131,129,131))
      	lc = wxLayoutConstraints()
	lc.top.SameAs(self.panel_shadow_under,wxTop,0)
	lc.left.RightOf(self.panel_shadow_under,20)
        lc.width.PercentOf(self, wxRight, 40)
        lc.height.PercentOf(self,wxHeight,95)
	self.panel_shadow_under_right.SetConstraints(lc)
	self.notebook1 = wxNotebook(self, -1, wxDefaultPosition, wxDefaultSize, style = 0)
	#-------------------------------------------------------------------------
	#Associate an imagelist with the notebook and add images to the image list
	#-------------------------------------------------------------------------
	tabimage_1 = tabimage_2 = tabimage_2 = tabimage_2 = tabimage_2 = tabimage_2 = -1
        self.notebook1.il = wxImageList(8, 8)
        tabimage_1 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ScriptBitmap())
        tabimage_2 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RequestsBitmap())
	tabimage_3 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_MeasurementsBitmap())
	tabimage_4 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_ReferralsBitmap())
	tabimage_5 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_RecallsBitmap())
	tabimage_6 = self.notebook1.il.Add(images_gnuMedGP_TabbedLists.getTab_Letters_ReceivedBitmap())
	self.notebook1.SetImageList(self.notebook1.il)
	lc = wxLayoutConstraints()
	lc.top.SameAs(self, wxTop,7)
	lc.left.SameAs(self.panel_shadow_under, wxRight,12)
        lc.width.SameAs(self.panel_shadow_under_right, wxWidth)
        lc.height.PercentOf (self.panelB, wxHeight,45)
	self.notebook1.SetConstraints(lc)


	self.listCtrl1 = wxListCtrl(self.notebook1, -1, wxDefaultPosition, wxDefaultSize,0)
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_1, pPage = self.listCtrl1, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_2, pPage = self.listCtrl1, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_3, pPage = self.listCtrl1, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_4, pPage = self.listCtrl1, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_5, pPage = self.listCtrl1, strText = '')
	self.notebook1.AddPage(bSelect = true, imageId = tabimage_6, pPage = self.listCtrl1, strText = '')

	lc = wxLayoutConstraints()
	lc.top.SameAs(self.notebook1, wxTop,0)
	lc.left.SameAs(self.notebook1, wxLeft,0)
        lc.width.SameAs(self.notebook1, wxWidth)
        lc.height.PercentOf (self.notebook1, wxHeight,100)
	self.listCtrl1.SetConstraints(lc)

	#------------------------------------------------------------------------
	#construct bottom right hand  white panel to hold scratch pad + reminders
	#------------------------------------------------------------------------
	self.panel_scratch_reminders = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize,
                            wxSIMPLE_BORDER)
        self.panel_scratch_reminders.SetBackgroundColour(wxWHITE)
	lc = wxLayoutConstraints()
	lc.top.Below(self.notebook1, 10)
	lc.left.SameAs(self.notebook1, wxLeft,0)
        lc.width.SameAs(self.notebook1, wxWidth)
        lc.height.PercentOf (self.panelB, wxHeight,53)
	self.panel_scratch_reminders.SetConstraints(lc);	

	##----------------------------------------
	##Add an editable list box for scratch pad
	#-----------------------------------------
	self.elb = wxEditableListBox(self.panel_scratch_reminders, -1, "Scratch Pad",wxDefaultPosition, wxDefaultSize)
                                     

        self.elb.SetStrings(["Check if has done microalbumin",
                             "Ask about flowers",
                              "Check BP next visit",
                              ])
	lc = wxLayoutConstraints()
        lc.top.SameAs  (self.panel_scratch_reminders,wxTop,2)
        lc.left.SameAs (self.panel_scratch_reminders, wxLeft, 2)
        lc.height.PercentOf (self.panel_scratch_reminders,wxHeight,50)
	lc.right.PercentOf (self.panel_scratch_reminders, wxRight,99)
	self.elb.SetConstraints(lc);



class MyFrame(wxFrame):
    def __init__(self, parent, ID, title):
        wxFrame.__init__(self, parent, ID, title,
                         wxDefaultPosition, wxSize(800, 600))
        self.CreateStatusBar()
       	#menu = wxMenu()
        #menu.Append(ID_ABOUT, "&About",
                    #"More information about this program")
        #menu.AppendSeparator()
        #menu.Append(ID_EXIT, "E&xit", "Terminate the program")
	#menuBar = wxMenuBar()
        #menuBar.Append(menu, "&File");
	#self.SetMenuBar(menuBar)
	putpanel=MyPanel(self)
        #===================================================
        # create a toolbar underneath the menu. This will be
	# a horizontal tool bar with no border and be flat
	# here the bitmaps (pictures) for the tool bar are
	# added from the file images.py which should here
	# be located in the same directory as the
	# gmPythonTutorial.py file
	# note here that when multiple attributes are given
	# they are separated by the pipe character | ie
	# wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT
        #===================================================
        tb = self.CreateToolBar(wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
	menu = wxMenu()
        menu.Append(ID_ABOUT, "&About",
                    "More information about this program")
        menu.AppendSeparator()
        menu.Append(ID_EXIT, "E&xit", "Terminate the program")
	menuBar = wxMenuBar()
        menuBar.Append(menu, "&File");
	self.SetMenuBar(menuBar)
	ID_FINDPATIENT = wxNewId()
	tb.AddControl(wxStaticText(tb, ID_FINDPATIENT, label ='       Find Patient', name = 'lblFindPatient',size = (150,-1), style = 0))
	tb.AddControl(wxTextCtrl(tb, ID_FINDPATIENT, name ="txtFindPatient",size =(200,-1),style = 0, value = ''))
        
	tb.AddSimpleTool(10, images.getNewBitmap(), "New", "Start a new file")
        EVT_TOOL(self, 10, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 10, self.OnToolRClick)

        tb.AddSimpleTool(20, images.getOpenBitmap(), "Open", "Open a file")
        EVT_TOOL(self, 20, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 20, self.OnToolRClick)

        tb.AddSeparator()
        tb.AddSimpleTool(30, images.getCopyBitmap(), "Copy", "Copy a file")
        EVT_TOOL(self, 30, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 30, self.OnToolRClick)

        tb.AddSimpleTool(40, images.getPasteBitmap(), "Paste", "Paste a file")
        EVT_TOOL(self, 40, self.OnToolClick)
        EVT_TOOL_RCLICKED(self, 40, self.OnToolRClick)

        tb.AddSeparator()

        tool = tb.AddTool(50, images.getTog1Bitmap(),
                          shortHelpString="Toggle this", isToggle=true)
        EVT_TOOL(self, 50, self.OnToolClick)

        tb.AddTool(60, images.getTog1Bitmap(), images.getTog2Bitmap(),
                   shortHelpString="Toggle with 2 bitmaps", isToggle=true)
        EVT_TOOL(self, 60, self.OnToolClick)

        EVT_TOOL_ENTER(self, -1, self.OnToolEnter)
        EVT_TOOL_RCLICKED(self, -1, self.OnToolRClick)  # Match all
        #EVT_TIMER(self, -1, self.OnClearSB)
	#==========================================================
        # we will now add a control to the toolbar, here a combobox
	#==========================================================
        tb.AddSeparator()
        cbID = wxNewId()
        tb.AddControl(wxComboBox(tb, cbID, "surgery consultation", choices=["surgery consultation", "home visit", "phone consultation", "patient absent"],
                                 size=(150,-1), style=wxCB_DROPDOWN))
        EVT_COMBOBOX(self, cbID, self.OnCombo)

		#self.textCtrl4 = wxTextCtrl(id = wxID_WXFRAME1TEXTCTRL4, name = 'textCtrl4', parent = self, \
         #       pos = wxPoint(344, 130), size = wxSize(224, ctxtheight), style = 0, value = '')

	#===================================
        # finally, create the whole tool bar
	#===================================
        tb.Realize()

	#=========================================================================
	# now define the events which will be generated if the tool bar is clicked
	#=========================================================================
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

   
class MyApp(wxApp):
    def OnInit(self):
        frame = MyFrame(NULL, -1, "gnuMedGP")
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app = MyApp(0)
app.MainLoop()
