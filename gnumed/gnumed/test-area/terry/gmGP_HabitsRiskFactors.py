from wxPython.wx import *

class HabitsRiskFactors(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	sizer = wxBoxSizer(wxVERTICAL)
	
	#captions for the two columns
	#habit_caption = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Habits")
	#risk_caption =gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,"Risk Factors")
	
	#text controls for each column      
	txt_habits = wxTextCtrl(self, 30,
                        "Smoker - 30/day.\n"
			"Alcohol - 30gm/day (Previously very heavy.\n",
                              wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
	txt_habits.SetInsertionPoint(0)
	
	txt_riskfactors = wxTextCtrl(self,30,
			     "Hypercholesterolaemia \n"
			     "Current Smoker \n"
			     "NIDDM \n"
                             "No exercise data recorded\n",
			      wxDefaultPosition,wxDefaultSize, style = wxTE_MULTILINE)
	txt_riskfactors.SetInsertionPoint(0)
	#heading sizer- add headings
	#heading_sizer = wxBoxSizer(wxHORIZONTAL)
	#heading_sizer.Add(habit_caption,1,wxEXPAND)
	#heading_sizer.Add(risk_caption,1,wxEXPAND)
	#self.SetSizer(heading_sizer)  #set the sizer 
	#heading_sizer.Fit(self)             #set
	##text sizer - add text
        text_sizer = wxBoxSizer(wxHORIZONTAL)
	text_sizer.Add(txt_habits,1,wxEXPAND)
	text_sizer.Add(txt_riskfactors,1,wxEXPAND)
	self.SetSizer(text_sizer)  #set the sizer 
	text_sizer.Fit(self)             #set
	self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
	
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(HabitsRiskFactors, -1)
	app.MainLoop()
 