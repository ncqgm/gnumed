"""
A plugin for searching the patient database
"""

from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar

ID_FINDPTICON = wxNewId ()
ID_FINDPTTXT = wxNewId ()
ID_PTAGE = wxNewId ()
ID_ALLERGYTXT = wxNewId ()

class gmPatientSearch (gmPlugin.wxBasePlugin):

    def name (self):
        return 'PatientSearch'

    def register (self):
        # first, set up the toolbar
        tb1 = self.gb['main.top_toolbar']
        tb1.AddSeparator()
	tb1.AddTool(ID_FINDPTICON, images_gnuMedGP_Toolbar.getToolbar_FindPatientBitmap(), shortHelpString="Find a patient")
        EVT_TOOL (tb1, ID_FINDPTICON, self.OnSearch)
        self.pt_name_ctrl = wxTextCtrl(tb1, ID_FINDPTTXT, name ="txtFindPatient",size =(300,-1),style = 0, value = '')
        EVT_TEXT_ENTER (self.pt_name_ctrl, ID_FINDPTTXT, self.OnSearch)
	tb1.AddControl(self.pt_name_ctrl)
	tb1.AddSeparator()	
	tb1.AddControl(wxStaticText(tb1, -1, label ='Age', name = 'lblAge',size = (30,-1), style = 0))
	tb1.AddSeparator()
        self.pt_age_ctrl = wxTextCtrl(tb1, ID_PTAGE, name ="txtPtAge",size =(30,-1),style = 0, value = '')
        tb1.AddControl(self.pt_age_ctrl)
	tb1.AddSeparator()	
	tb1.AddControl(wxStaticText(tb1, -1, label ='Allergies', name = 'lblAge',size = (50,-1), style = 0))
	self.pt_allergies_ctrl = wxTextCtrl(tb1, ID_ALLERGYTXT, name ="txtFindPatient",size =(250,-1),style = 0, value = '')
        self.gb['main.top_toolbar.allergies'] = self.pt_allergies_ctrl # in case other widget wants to talk to this control
        tb1.AddControl (self.pt_allergies_ctrl)

        # now set up the searching list
        self.mwm = self.gb ['main.manager']
        self.srch_list = wxListCtrl (self.mwm, -1)
        self.mwm.RegisterLeftSide ('find_patient_list', self.srch_list)

    def OnSearch (self, event):
        """
        Search for patient and display
        """
        name = self.pt_name_ctrl.GetValue ()
        self.mwm.Display ('find_patient_list')

