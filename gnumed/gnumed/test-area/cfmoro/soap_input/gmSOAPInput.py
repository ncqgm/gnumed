"""
    GnuMed multisash based SOAP input panel
    
    Health issues are selected in a list.
    The user can split new soap windows, which are disposed
    in stack.
    Usability is provided by:
        -Logically enabling/disabling action buttons
        -Controlling user actions and rising informative
         message boxes when needed.

    Post-0.1? :
        -Add context information widgets
"""
#================================================================
__version__ = "$Revision: 1.15 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.business import gmEMRStructItems, gmPatient, gmClinNarrative
from Gnumed.wxpython import gmRegetMixin
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

import SOAP2, SOAPMultiSash

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================

# FIXME attribute encapsulation and private methods
# FIXME i18n

# Auto-completion test words
# FIXME currently copied form SOAP2.py
AOElist = [{'label':'otitis media', 'data':1, 'weight':1},
    {'label':'otitis externa', 'data':2, 'weight':1},
    {'label':'cellulitis', 'data':3, 'weight':1},
    {'label':'gingivitis', 'data':4, 'weight':1},
    {'label':'ganglion', 'data':5, 'weight':1}]

Subjlist = [{'label':'earache', 'data':1, 'weight':1},
    {'label':'earache', 'data':1, 'weight':1},
    {'label':'ear discahrge', 'data':2, 'weight':1},
    {'label':'eardrum bulging', 'data':3, 'weight':1},
    {'label':'sore arm', 'data':4, 'weight':1},
    {'label':'sore tooth', 'data':5, 'weight':1}]

Planlist = [{'label':'pencillin V', 'data':1, 'weight':1},
    {'label':'penicillin X', 'data':2, 'weight':1},
    {'label':'penicillinamine', 'data':3, 'weight':1},
    {'label':'penthrane', 'data':4, 'weight':1},
    {'label':'penthidine', 'data':5, 'weight':1}]
        
#============================================================
class cSOAPControl(wx.wxPanel):
    """
    Basic SOAP input widget. It provides Ian's SOAP editor and a staticText
    that displays the which issue is current SOAP related to.
    """
    
    #--------------------------------------------------------
    def __init__(self, parent):
        """
        Construct a new SOAP input widget
        
        @param parent: the parent widget        
        """
        
        # panel initialization
        wx.wxPanel.__init__ (self,
            parent,
            -1,
            wx.wxPyDefaultPosition,
            wx.wxPyDefaultSize,
            wx.wxNO_BORDER
        )
        
        # soap's health issue staticText heading
        self._soap_label = wx.wxStaticText(self, -1, "Select issue and press 'New'")
        # related health issue
        self._health_issue = None
        print "...creating new soap input widget"
        # flag indicating saved state
        self.is_saved = False
        
        # soap rich and smart text editor
        # FIXME currently copied form SOAP2.py
        self._soap_text_editor = SOAP2.ResizingWindow (self, -1, size = wx.wxSize (300, 150))
        self._S = SOAP2.ResizingSTC (self._soap_text_editor, -1)
        self._S.AttachMatcher (cMatchProvider_FixedList (Subjlist))
        self._O = SOAP2.ResizingSTC (self._soap_text_editor, -1)
        self._A = SOAP2.ResizingSTC (self._soap_text_editor, -1)
        self._A.AttachMatcher (cMatchProvider_FixedList (AOElist))
        self._P = SOAP2.ResizingSTC (self._soap_text_editor, -1)
        self._P.AttachMatcher (cMatchProvider_FixedList (Planlist))
        self._S.prev = None
        self._S.next = self._O
        self._O.prev = self._S
        self._O.next = self._A
        self._A.prev = self._O
        self._A.next = self._P
        self._P.prev = self._A
        self._P.next = None
        self._soap_text_editor.AddWidget (self._S, "Subjective")
        self._soap_text_editor.Newline ()
        self._soap_text_editor.AddWidget (self._O, "Objective")
        self._soap_text_editor.Newline ()
        self._soap_text_editor.AddWidget (self._A, "Assessment")
        self._soap_text_editor.Newline ()
        self._soap_text_editor.AddWidget (self._P, "Plan")
        self._soap_text_editor.SetValues ({"Subjective":"sore ear", "Plan":"Amoxycillin"})
        self._soap_text_editor.ReSize ()
        
        # sizers for widgets
        self._soap_control_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
        self._soap_control_sizer.Add(self._soap_label)           
        self._soap_control_sizer.Add(self._soap_text_editor)
        
        # do layout
        self.SetSizerAndFit(self._soap_control_sizer)        
        
    #--------------------------------------------------------
    def SetHealthIssue(self, selected_issue):
        """
        Set the related health issue for this SOAP input widget.
        Update heading label with health issue data.
        
        @type selected_issue: gmEMRStructItems.cHealthIssue
        @param selected_issue: SOAP input widget's related health issue
        """
        self._health_issue = selected_issue
        if self._health_issue is None or len(self._health_issue) == 0:
            self._soap_label.SetLabel("Select issue and press 'New'")
        else:
            txt = '%s# %s'%(self._health_issue[0]+1,self._health_issue[1]['description'])
            # update staticText content and recalculate sizer internal values
            self._SetHeading(txt)
        self.ShowContents()
            
    #--------------------------------------------------------
    def GetHealthIssue(self):
        """
        Retrieve the related health issue for this SOAP input widget.
        """
        return self._health_issue
    
    #--------------------------------------------------------
    def GetSOAP(self):
        """
        Retrieves widget's SOAP text editor
        """
        return self._soap_text_editor
    
    #--------------------------------------------------------
    def ClearSOAP(self):
        """
        Clear any entries in widget's SOAP text editor
        """
        self._soap_text_editor.SetValues ({"Subjective":" ", "Objective":" ",
            "Assessment":" ", "Plan":" "})

    #--------------------------------------------------------
    def HideContents(self):
        """
        Hide widget's components (health issue heading and SOAP text editor)
        """
        self._soap_label.Hide()
        self._soap_text_editor.Hide()
    
    #--------------------------------------------------------    
    def ShowContents(self):
        """
        Show widget's components (health issue heading and SOAP text editor)
        """
        self._soap_label.Show(True)
        self._soap_text_editor.Show(True)

    #--------------------------------------------------------
    def IsContentShown(self):
        """
        Check if contents are being shown
        """
        return self._soap_label.IsShown()
        
    #--------------------------------------------------------    
    def SetSaved(self, is_saved):
        """
        Set SOAP input widget saved (dumped to backend) state
        
        @param is_saved: Flag indicating wether the SOAP has been dumped to
                         persistent backend
        @type is_saved: boolean
        """
        self.is_saved = is_saved
        if is_saved:
            self._SetHeading(self._soap_label.GetLabel() + '. SAVED')

    #--------------------------------------------------------    
    def IsSaved(self):
        """
        Check  SOAP input widget saved (dumped to backend) state
        
        """
        return self.is_saved
            
    #--------------------------------------------------------    
    def _SetHeading(self, txt):
        """
        Configure SOAP widget's heading title
        
        @param txt: New widget's heading title to set
        @type txt: string
        """
        self._soap_label.SetLabel(txt)
        size = self._soap_label.GetBestSize()
        self._soap_control_sizer.SetItemMinSize(self._soap_label, size.width, size.height)
        self.Layout()
        
    #--------------------------------------------------------    
    def ResetAndHide(self):
        """
        Reset all data and hide contents
        
        """        
        self.SetHealthIssue(None)            
        self.SetSaved(False)
        self.ClearSOAP()        
        self.HideContents()
                    
#============================================================                      
class cSOAPInputPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):
    """
    Basic multi-sash based SOAP input panel.
    Currently, displays a dynamic stack of SOAP input widgets on the left
    and the helth issues list on the right.
    """
    
    #--------------------------------------------------------
    def __init__(self, parent, id):
        """
        Contructs a new instance of SOAP input panel

        @param parent: Wx parent widget
        @param id: Wx widget id
        """
        
        # panel super classes initialization
        wx.wxPanel.__init__ (
            self,
            parent,
            id,
            wx.wxPyDefaultPosition,
            wx.wxPyDefaultSize,
            wx.wxNO_BORDER
        )        
        gmRegetMixin.cRegetOnPaintMixin.__init__(self)
        
        # business objects setup
        # active patient
        self._patient = gmPatient.gmCurrentPatient()
        # active patient's emr
        self._emr = self._patient.get_clinical_record()
        # store the currently selected SOAP input widget on health issues list
        # in the form of a two element list [issue index in list : health issue vo]
        self._selected_issue = []
        # store the health issues wich has an associated SOAP note created.
        # Useful to avoid duplicate SOAP notes for the same health issue
        self._issues_with_soap = []
        # multisash's selected leaf        
        self._selected_leaf = None
        # multisash's selected soap widget
        self._selected_soap = None        
        
        # ui contruction and event handling set up        
        self._do_layout()
        self._register_interests()
        self._populate_with_data()

    #--------------------------------------------------------
    def _do_layout(self):
        """
        Arrange SOAP input panel widgets
        """        
        
        # SOAP input panel main splitter window
        self._soap_emr_splitter = wx.wxSplitterWindow(self, -1)

        # SOAP input widget's (left) panel
        self._soap_panel = wx.wxPanel(self._soap_emr_splitter,-1)
        # SOAP multisash
        self._soap_multisash = SOAPMultiSash.cSOAPMultiSash(self._soap_panel, -1)
        # SOAP action buttons, disabled at startup
        self._save_button = wx.wxButton(self._soap_panel, -1, "&Save")
        self._save_button.Disable()
        self._clear_button = wx.wxButton(self._soap_panel, -1, "&Clear")
        self._clear_button.Disable()
        self._new_button = wx.wxButton(self._soap_panel, -1, "&New")
        self._new_button.Disable()
        self._remove_button = wx.wxButton(self._soap_panel, -1, "&Remove")
        self._remove_button.Disable()

        # health issues list (right) panel
        self._issues_panel = wx.wxPanel(self._soap_emr_splitter,-1)
        self._health_issues_list = wx.wxListBox(
            self._issues_panel,
            -1,
            style= wx.wxNO_BORDER
        )            
        
        # action buttons sizer
        self._soap_actions_sizer = wx.wxBoxSizer(wx.wxHORIZONTAL)
        self._soap_actions_sizer.Add(self._save_button, 0,wx.wxSHAPED)
        self._soap_actions_sizer.Add(self._clear_button, 0,wx.wxSHAPED)
        self._soap_actions_sizer.Add(self._new_button, 0,wx.wxSHAPED)
        self._soap_actions_sizer.Add(self._remove_button, 0,wx.wxSHAPED)
        # SOAP area main sizer
        self._soap_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
        self._soap_panel_sizer.Add(self._soap_multisash, 1, wx.wxEXPAND)        
        self._soap_panel_sizer.Add(self._soap_actions_sizer)
        self._soap_panel.SetSizerAndFit(self._soap_panel_sizer)        
        
        # health issues list area main sizer
        self._issues_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)    
        self._issues_panel_sizer.Add(self._health_issues_list, 1, wx.wxEXPAND)
        self._issues_panel.SetSizerAndFit(self._issues_panel_sizer)        
                
        # SOAP - issues list splitter basic configuration
        self._soap_emr_splitter.SetMinimumPaneSize(20)
        self._soap_emr_splitter.SplitVertically(self._soap_panel, self._issues_panel)
        
        # SOAP input panel main sizer
        self._main_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
        self._main_sizer.Add(self._soap_emr_splitter, 1, wx.wxEXPAND, 0)
        self.SetSizerAndFit(self._main_sizer)

    #--------------------------------------------------------
    # event handling
    #--------------------------------------------------------
    def _register_interests(self):
        """
        Configure enabled event signals
        """
        # wx.wxPython events
        wx.EVT_LISTBOX(self._health_issues_list, self._health_issues_list.GetId(),
            self._on_health_issue_selected)
        wx.EVT_BUTTON(self._save_button, self._save_button.GetId(), self._on_save)
        wx.EVT_BUTTON(self._clear_button, self._clear_button.GetId(),
            self._on_clear)
        wx.EVT_BUTTON(self._new_button, self._new_button.GetId(), self._on_new)
        wx.EVT_BUTTON(self._remove_button, self._remove_button.GetId(),
            self._on_remove)
                    
        # client internal signals
        gmDispatcher.connect(signal=gmSignals.patient_selected(),
            receiver=self._on_patient_selected)
        
    #--------------------------------------------------------
    def _on_save(self, event):
        """
        Obtain SOAP data from selected editor and dump to backend
        """
        # security check
        if not self._allow_perform_action(self._save_button.GetId()):
            return
    
        #FIXME support arbitrary narrative categories, not only soap        
        active_encounter = self._emr.get_active_encounter()
        active_episode = self._emr.get_active_episode()
        print "\nSOAP input: %s"%(self._selected_soap.GetSOAP().GetValues())        
        print "\nActive encounter: %s"%(active_encounter)
        print "\nActive episode: %s"%(active_episode)
        
        #print "\nCreating SOAP narratives: " 
        #stat, narr = gmClinNarrative.create_clin_narrative(narrative = selected_soap.GetSOAP().GetValues()['Subjective'],
        #    soap_cat = 's', episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        #print "\n   .Subjective: %s, %s"%(stat,narr)
        #stat, narr = gmClinNarrative.create_clin_narrative(narrative = selected_soap.GetSOAP().GetValues()['Objective'],
        #    soap_cat = 'o', episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        #print "\n   .Objective: %s, %s"%(stat,narr)
        #stat, narr = gmClinNarrative.create_clin_narrative(narrative = selected_soap.GetSOAP().GetValues()['Assessment'],
        #    soap_cat = 'a', episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        #print "\n   .Assesment: %s, %s"%(stat,narr)
        #stat, narr = gmClinNarrative.create_clin_narrative(narrative = selected_soap.GetSOAP().GetValues()['Plan'],
        #    soap_cat = 'p', episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        #print "\n   .Plan: %s, %s"%(stat,narr)
        
        self._selected_soap.SetSaved(True)
        self.check_buttons()
        print "Done!"
                    
    #--------------------------------------------------------
    def _on_clear(self, event):
        """
        Clear currently selected SOAP input widget
        """
        
        # security check
        if not self._allow_perform_action(self._clear_button.GetId()):
            return

        print "Clear SOAP"
        self._selected_soap.ClearSOAP()

    #--------------------------------------------------------
    def _on_new(self, event):
        """
        Create and display a new SOAP input widget on the stack
        """

        # security check
        if not self._allow_perform_action(self._new_button.GetId()):
            return
            
        print "New SOAP"        
        # first SOAP input widget is displayed by showing an empty hidden one
        if not self._selected_soap is None and not self._selected_soap.IsContentShown():
            self._issues_with_soap.append(self._selected_issue[1])
            self._selected_soap.SetHealthIssue(self._selected_issue)
            self._selected_leaf.GetSOAPPanel().Show()
            self._selected_leaf.detail.Select()
            self._selected_leaf.creatorHor.Show(True)
            self._selected_leaf.closer.Show(True)
            
        else:
            # create SOAP input widget for currently selected issue
            # FIXME: programmatically calculate height
            self._selected_leaf.AddLeaf(SOAPMultiSash.MV_VER, 130)

        print "Issues with soap: %s"%(self._issues_with_soap)
        
        
    #--------------------------------------------------------
    def _on_remove(self, event):
        """
        Removes currently selected SOAP input widget
        """

        # security check
        if not self._allow_perform_action(self._remove_button.GetId()):
            return
            
        print "Remove SOAP"        
        self._selected_leaf.DestroyLeaf()

        print "Issues with soap: %s"%(self._issues_with_soap)
        # there's no leaf selected after deletion, so disable all buttons
        self._save_button.Disable()
        self._clear_button.Disable()
        self._remove_button.Disable()
        # enable new button is soap stack is empty
        #selected_leaf = self._soap_multisash.GetSelectedLeaf()
        #if self._selected_soap.GetHealthIssue() is None:
        #    self._new_button.Enable(True)
        
    #--------------------------------------------------------    
    def _on_patient_selected(self):
        """
        Current patient changed
        """
        self._schedule_data_reget()
        
    #--------------------------------------------------------
    def _on_health_issue_selected(self, event):
        """
        When the user changes health issue selection, update selected issue
        reference and update buttons according its input status.
        """        
        self._selected_issue = [self._health_issues_list.GetSelection(),
            self._health_issues_list.GetClientData(self._health_issues_list.GetSelection())]
        #print 'Selected: %s'%(self._selected_issue)
        
        #if not self._new_button.IsEnabled():
        #    self._new_button.Enable(True)

        self.check_buttons()    

    #--------------------------------------------------------    
    def check_buttons(self):
        """
        Check and configure adecuate buttons enabling state
        """
        
        print "cSOAPInput.check_buttons" 
        
        if self._selected_leaf is None:
            print "Selected leaf NONE"
        if self._selected_soap is None:
            print "Selected soap NONE"
        if len(self._selected_issue)==0 is None:
            print "Selected issues 0"                                    
        if self._selected_leaf is None or self._selected_soap is None or len(self._selected_issue)==0:
            print "Won't check buttons for None leaf/soap/selected_issue"
            return
        
        # if soap stack is empty, disable save, clear and remove buttons
        print "Health issues: %s"%(self._selected_soap.GetHealthIssue())
        if self._selected_soap.GetHealthIssue() is None or self._selected_soap.IsSaved():
            self._save_button.Enable(False)
            self._clear_button.Enable(False)
            self._remove_button.Enable(False)
        else:
            self._save_button.Enable(True)
            self._clear_button.Enable(True)
            self._remove_button.Enable(True)
        
        # allow new when soap stack is empty
        # avoid enabling new button to create more than one soap per issue.        
        if self._selected_issue[1] in self._issues_with_soap:
            self._new_button.Enable(False)
        else:
            self._new_button.Enable(True)
            
        # disabled save button when soap was dumped to backend
        #print "Saved: %s"%(self._selected_soap.IsSaved())
        if self._selected_soap.IsSaved():
            self._remove_button.Enable(True)

    #--------------------------------------------------------    
    def _allow_perform_action(self, action_id):
        """
        Check if a concrte action can be performed for selected SOAP input widget
        
        @param action_id: ui widget wich fired the action
        """
        if (self._selected_leaf is None or \
            len(self._issues_with_soap) == 0) and \
            action_id != self._new_button.GetId():
            wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.",
                caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
                parent = self)
            return False

        if (self._selected_issue is None or len(self._selected_issue) == 0) \
            and action_id == self._new_button.GetId():
            wx.wxMessageBox("There is not any problem selected.\nA problem must be selected to create a new SOAP note.",
                caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
                parent = self)
            return False
        
        return True
        
    #--------------------------------------------------------
    # reget mixin API
    #--------------------------------------------------------
    def _populate_with_data(self):
        """
        Fills UI with data.
        """
        # FIXME: called on resize
        self.reset_ui_content()
        if self._refresh_issues_list():
            return True
        return False
        
    #--------------------------------------------------------
    # public API
    #--------------------------------------------------------        
    def get_issues_with_soap(self):
        """
        Retrieve health issues for wich a SOAP note is created
        """
        return self._issues_with_soap
        
    #--------------------------------------------------------        
    def get_selected_issue(self):
        """
        Retrieves selected health issue in list
        """
        return self._selected_issue
    
    #--------------------------------------------------------        
    def set_selected_leaf(self, selected_leaf, selected_soap):
        """
        Set multisash's currently selected leaf and soap widget
        
        @param selected_leaf: multisash's currently selected leaf
        @type selected_leaf: SOAPMultiSash.wxMultiViewLeaf
        
        @param selected_soap: multisash's currently selected soap
        @type selected_soap: gmSOAPInput.cSOAPControl
        """
        print "cSOAPInput.set_selected_leaf"
        self._selected_leaf = selected_leaf        
        self._selected_soap = selected_soap        
        print "\nSelected leaf: %s"%(self._selected_leaf)        
        print "Selected SOAP: %s"%(self._selected_soap)
        self.check_buttons()
                    
    #--------------------------------------------------------
    def _refresh_issues_list(self):
        """
        Updates health issues list
        """
        # FIXME remove
        if self._health_issues_list.GetCount() > 0:
            return False
        cont = 0
        for a_health_issue in self._emr.get_health_issues():            
            cont = cont+1
            a_key = '#%s %s'%(cont,a_health_issue['description'])
            self._health_issues_list.Append(a_key,a_health_issue)
            
        # Set sash position
        self._soap_emr_splitter.SetSashPosition(self._soap_emr_splitter.GetSizeTuple()[0]/2, True)

        return True

    #--------------------------------------------------------
    # internal API
    #--------------------------------------------------------
    def reset_ui_content(self):
        """
        Clear all information from input panel
        """
        self._selected_issue = []
        self._issues_with_soap = []
        self._health_issues_list.Clear()
        self._soap_multisash.Clear()
        self._soap_multisash.SetController(self)
        

#== Module convenience functions (for standalone use) =======================
def prompted_input(prompt, default=None):
    """
    Obtains entry from standard input
    
    promp - Promt text to display in standard output
    default - Default value (for user to press only intro)
    """
    usr_input = raw_input(prompt)
    if usr_input == '':
        return default
    return usr_input
    
#------------------------------------------------------------                 
def askForPatient():
    """
        Main module application patient selection function.
    """
    
    # Variable initializations
    pat_searcher = gmPatient.cPatientSearcher_SQL()

    # Ask patient
    patient_term = prompted_input("\nPatient search term (or 'bye' to exit) (eg. Kirk): ")
    
    if patient_term == 'bye':
        return None
    search_ids = pat_searcher.get_patient_ids(search_term = patient_term)
    if search_ids is None or len(search_ids) == 0:
        prompted_input("No patient matches the query term. Press any key to continue.")
        return None
    elif len(search_ids) > 1:
        prompted_input("Various patients match the query term. Press any key to continue.")
        return None
    patient_id = search_ids[0]
    patient = gmPatient.gmCurrentPatient(patient_id)
    
    return patient
    
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

    from Gnumed.pycommon import gmCfg

    _log.SetAllLogLevels(gmLog.lData)
    _log.Log (gmLog.lInfo, "starting SOAP input panel...")

    _cfg = gmCfg.gmDefCfgFile     
    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    try:
        # make sure we have a db connection
        gmPG.set_default_client_encoding('latin1')
        pool = gmPG.ConnectionPool()
        
        # obtain patient
        patient = askForPatient()
        if patient is None:
            print "No patient. Exiting gracefully..."
            sys.exit(0)

        # display standalone browser
        application = wx.wxPyWidgetTester(size=(800,600))
        soap_input = cSOAPInputPanel(application.frame, -1)
        #soap_input.refresh_tree()
        
        application.frame.Show(True)
        application.MainLoop()
        
        # clean up
        if patient is not None:
            try:
                patient.cleanup()
            except:
                print "error cleaning up patient"
    except StandardError:
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise
    try:
        pool.StopListeners()
    except:
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
        raise

    _log.Log (gmLog.lInfo, "closing SOAP input...")
