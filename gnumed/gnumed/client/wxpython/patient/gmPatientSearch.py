"""
A plugin for searching the patient database by name.
Required the gmPatientWindowPlgin to be loaded.
CANNOT BE UNLOADED
"""

from wxPython.wx import *
import gmPlugin
import images_gnuMedGP_Toolbar
import gmSQLListControl
from string import *
import gettext
_ = gettext.gettext
import gmLog

ID_FINDPTICON = wxNewId ()
ID_FINDPTTXT = wxNewId ()
ID_PTAGE = wxNewId ()
ID_ALLERGYTXT = wxNewId ()

class gmPatientSearch (gmPlugin.wxBasePlugin):

    def name (self):
        return 'Patient Search'

    def register (self):
        # first, set up the toolbar
        tb1 = self.gb['main.top_toolbar']
        tb1.AddSeparator()
	tb1.AddTool(ID_FINDPTICON, images_gnuMedGP_Toolbar.getToolbar_FindPatientBitmap(), shortHelpString="Find a patient")
        EVT_TOOL (tb1, ID_FINDPTICON, self.OnSearch)
        self.pt_name_ctrl = wxTextCtrl(tb1, ID_FINDPTTXT, name ="txtFindPatient",size =(300,-1),style = 0, value = '')
        EVT_TEXT_ENTER (tb1, ID_FINDPTTXT, self.OnSearch)
	tb1.AddControl(self.pt_name_ctrl)
	tb1.AddSeparator()	
	tb1.AddControl(wxStaticText(tb1, -1, label ='Age', name = 'lblAge',size = (30,-1), style = 0))
	tb1.AddSeparator()
        self.pt_age_ctrl = wxTextCtrl(tb1, ID_PTAGE, name ="txtPtAge",size =(30,-1),style = 0, value = '')
        tb1.AddControl(self.pt_age_ctrl)
	tb1.AddSeparator()	
	tb1.AddControl(wxStaticText(tb1, -1, label ='Allergies', name = 'lblAge',size = (50,-1), style = 0))
	self.pt_allergies_ctrl = wxTextCtrl(tb1, ID_ALLERGYTXT, name ="txtFindPatient",size =(250,-1),style = 0, value = '')
        tb1.AddControl (self.pt_allergies_ctrl)

        # now set up the searching list
        self.mwm = self.gb ['patient.manager']
        ID_LIST = wxNewId ()
        self.srch_list = gmSQLListControl.SQLListControl (self.mwm, ID_LIST, hideid=true)
        self.mwm.RegisterLeftSide ('Patient Search', self.srch_list)
        EVT_LIST_ITEM_SELECTED (self.srch_list, ID_LIST, self.OnSelected)

    def OnSearch (self, event):
        """
        Search for patient and display
        """
        name = split (lower(self.pt_name_ctrl.GetValue ()))
        self.mwm.Display ('Patient Search')
        self.gb['modules.gui']['Patient'].Raise ()
        if len (name) == 0: # list everyone! (temporary, for small database)
            query = """
select id, firstnames, lastnames, dob, gender from v_basic_person
order by lastnames"""
        elif len (name) == 1:  # surname only
            query = """
select id, firstnames, lastnames, dob, gender from v_basic_person
where lastnames ilike '%s%%' 
order by lastnames""" % name[0]
        else: # two words: sur- and firstname search 
            query = """
select id, firstnames, lastnames, dob, gender from v_basic_person
where firstnames ilike '%s%%' and lastnames ilike '%s%%'
order by lastnames""" % (name[0], name[1])
        self.srch_list.SetLabels ([_('First name'), _('Family name'), _('Date of birth'), _('Gender')]) 
        self.srch_list.SetQueryStr (query, 'demographica')
        self.srch_list.RunQuery ()

    def OnSelected (self, event):
        gmLog.gmDefLog.Log (gmLog.lInfo, "selected patient ID %s" % event.GetData ())

