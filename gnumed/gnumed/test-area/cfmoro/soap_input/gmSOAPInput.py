"""
	GnuMed SOAP input panel
"""
#================================================================
__version__ = "$Revision: 1.11 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.business import gmEMRStructItems, gmPatient
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
		
		
class cSOAPControl(wx.wxPanel):
	
	def __init__(self, parent):
	
		# panel (super) initialization
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		
		# soap's health issue heading
		self.soap_label = wx.wxStaticText(self, -1, "Select issue and press 'New'")
		self.health_issue = None
		print "AAAAAAA"
		
		# soap rich and smart text editor
		# FIXME currently copied form SOAP2.py
		self.soap_text_editor = SOAP2.ResizingWindow (self, -1, size = wx.wxSize (300, 150))
		self.S = SOAP2.ResizingSTC (self.soap_text_editor, -1)
		self.S.AttachMatcher (cMatchProvider_FixedList (Subjlist))
		self.O = SOAP2.ResizingSTC (self.soap_text_editor, -1)
		self.A = SOAP2.ResizingSTC (self.soap_text_editor, -1)
		self.A.AttachMatcher (cMatchProvider_FixedList (AOElist))
		self.P = SOAP2.ResizingSTC (self.soap_text_editor, -1)
		self.P.AttachMatcher (cMatchProvider_FixedList (Planlist))
		self.S.prev = None
		self.S.next = self.O
		self.O.prev = self.S
		self.O.next = self.A
		self.A.prev = self.O
		self.A.next = self.P
		self.P.prev = self.A
		self.P.next = None
		self.soap_text_editor.AddWidget (self.S, "Subjective")
		self.soap_text_editor.Newline ()
		self.soap_text_editor.AddWidget (self.O, "Objective")
		self.soap_text_editor.Newline ()
		self.soap_text_editor.AddWidget (self.A, "Assessment")
		self.soap_text_editor.Newline ()
		self.soap_text_editor.AddWidget (self.P, "Plan")
		self.soap_text_editor.SetValues ({"Subjective":"sore ear", "Plan":"Amoxycillin"})
		self.soap_text_editor.ReSize ()
		
		# sizers
		self.soap_control_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.soap_control_sizer.Add(self.soap_label)           
		self.soap_control_sizer.Add(self.soap_text_editor)
		
		# do layout
		self.SetSizerAndFit(self.soap_control_sizer)
		
		# 
		
	def SetHealthIssue(self, selected_issue):
		"""
		Sets health issue SOAP editor
		"""
		self.health_issue = selected_issue
		if self.health_issue is None or len(self.health_issue) == 0:
			self.soap_label.SetLabel("Select issue and press 'New'")
		else:
			txt = '%s# %s'%(self.health_issue[0]+1, self.health_issue[1]['description'])
			self.soap_label.SetLabel(txt)
			size = self.soap_label.GetBestSize()
			self.soap_control_sizer.SetItemMinSize(self.soap_label, size.width, size.height)
			self.Layout()
		self.ShowContents()
			

		
	def GetHealthIssue(self):
		"""
		Sets health issue SOAP editor
		"""
		return self.health_issue
		
	def GetSOAP(self):
		"""
		Retrieves SOAP text editor
		"""
		return self.soap_text_editor
	
	def ClearSOAP(self):
		"""
		Clear values in SOAP text editor
		"""
		self.soap_text_editor.SetValues ({"Subjective":" ", "Objective":" ", "Assessment":" ", "Plan":" "})

	def HideContents(self):
		self.soap_label.Hide()
		self.soap_text_editor.Hide()
		
	def ShowContents(self):
		self.soap_label.Show(True)
		self.soap_text_editor.Show(True)

#============================================================	       	       
class cSOAPInputPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):
	
	def __init__(self, parent, id):
		"""
		Contructs a new instance of SOAP input panel

		parent - Wx parent widget
		id - Wx widget id
		"""
		
		# panel  super classes initialization
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
		self.patient = gmPatient.gmCurrentPatient()
		self.emr = self.patient.get_clinical_record()
		self.selected_issue = []
		self.issues_with_soap = []
		
		# ui contruction and event interests
		self.do_layout()
		self.register_interests()
		self._populate_with_data()

	#--------------------------------------------------------
	def do_layout(self):
		"""
		Arranges SOAP input layout
		"""		
		
		# SOAP input panel main splitter window
		self.soap_emr_splitter = wx.wxSplitterWindow(self, -1)

		# SOAP panel
		self.soap_panel = wx.wxPanel(self.soap_emr_splitter,-1)
		# SOAP multisash
		self.soap_multisash = SOAPMultiSash.cSOAPMultiSash(self.soap_panel, -1)
		self.soap_multisash.SetDefaultChildClassAndControllerObject(cSOAPControl,self)
		#self.soap_multisash.GetSelectedLeaf().GetSOAPPanel().Hide()
		#self.soap_multisash.GetSelectedLeaf().UnSelect()
		# SOAP action buttons
		self.save_button = wx.wxButton(self.soap_panel, -1, "&Save")
		self.save_button.Disable()
		self.clear_button = wx.wxButton(self.soap_panel, -1, "&Clear")
		self.clear_button.Disable()
		self.new_button = wx.wxButton(self.soap_panel, -1, "&New")
		self.new_button.Disable()
		self.remove_button = wx.wxButton(self.soap_panel, -1, "&Remove")
		self.remove_button.Disable()


		# EMR tree
		self.emr_panel = wx.wxPanel(self.soap_emr_splitter,-1)
		self.health_issues_list = wx.wxListBox(
			self.emr_panel,
			-1,
			style= wx.wxNO_BORDER
		)
			
		# action buttons sizer
		self.soap_actions_sizer = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.soap_actions_sizer.Add(self.save_button, 0,wx.wxSHAPED)
		self.soap_actions_sizer.Add(self.clear_button, 0,wx.wxSHAPED)
		self.soap_actions_sizer.Add(self.new_button, 0,wx.wxSHAPED)
		self.soap_actions_sizer.Add(self.remove_button, 0,wx.wxSHAPED)
		# SOAP area main sizer
		self.soap_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.soap_panel_sizer.Add(self.soap_multisash, 1, wx.wxEXPAND)		
		self.soap_panel_sizer.Add(self.soap_actions_sizer)
		self.soap_panel.SetSizerAndFit(self.soap_panel_sizer)		
		
		
		# EMR area main sizer
		self.emr_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)	
		self.emr_panel_sizer.Add(self.health_issues_list, 1, wx.wxEXPAND)
		self.emr_panel.SetSizerAndFit(self.emr_panel_sizer)		
		
		
		# SOAP - EMR splitter basic configuration
		self.soap_emr_splitter.SetMinimumPaneSize(20)
		self.soap_emr_splitter.SplitVertically(self.soap_panel, self.emr_panel)
		
		# SOAP input main sizer
		self.main_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.main_sizer.Add(self.soap_emr_splitter, 1, wx.wxEXPAND, 0)
		self.SetSizerAndFit(self.main_sizer)


	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def create_soap_editor(self, evt):
		print "Creating new SOAP..."
		
	def register_interests(self):
		"""
		Configures enabled event signals
		"""
		# wx.wxPython events
		wx.EVT_LISTBOX(self.health_issues_list,self.health_issues_list.GetId(), self.on_health_issue_selected)
		wx.EVT_BUTTON(self.save_button, self.save_button.GetId(), self.on_save)
		wx.EVT_BUTTON(self.clear_button, self.clear_button.GetId(), self.on_clear)
		wx.EVT_BUTTON(self.new_button, self.new_button.GetId(), self.on_new)
		wx.EVT_BUTTON(self.remove_button, self.remove_button.GetId(), self.on_remove)
					
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self.on_patient_selected)
		
	#--------------------------------------------------------
	def on_save(self, event):
		"""
		Obtains SOAP input from selected editor and dumps it to backend
		"""
		if self.soap_multisash.GetSelectedLeaf() is None or len(self.issues_with_soap) == 0:
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
		else:
			selected_soap = self.soap_multisash.GetSelectedLeaf().GetSOAPPanel().GetSOAP()
			print selected_soap.GetValues()
			print "Saving SOAP: %s"%(selected_soap.GetValues())
			
	#--------------------------------------------------------
	def on_clear(self, event):
		"""
		Clears selected SOAP editor
		"""
		if self.soap_multisash.GetSelectedLeaf() is None or len(self.issues_with_soap) == 0:
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
		else:
			print "Clear SOAP"
			selected_soap_panel = self.soap_multisash.GetSelectedLeaf().GetSOAPPanel()
			selected_soap_panel.ClearSOAP()
		

	#--------------------------------------------------------
	def on_new(self, event):
		"""
		Creates and displays a new SOAP input editor
		"""

		if self.soap_multisash.GetSelectedLeaf() is None:
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
		elif self.selected_issue is None or len(self.selected_issue) == 0:
			wx.wxMessageBox("There is not any problem selected.\nA problem must be selected to create a new SOAP note.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
		else:
			print "New SOAP"
			# FIXME only when unique and empty SOAP
			selected_leaf = self.soap_multisash.GetSelectedLeaf()
			selected_issue = selected_leaf.GetSOAPPanel().GetHealthIssue()
			if selected_issue is None or len(selected_issue) == 0:
			#selected_soap_panel = self.soap_multisash.GetSelectedLeaf().GetSOAPPanel()
				selected_leaf.GetSOAPPanel().SetHealthIssue(self.selected_issue)
				selected_leaf.GetSOAPPanel().Show()
				selected_leaf.detail.Select()
				selected_leaf.creatorHor.Show(True)
				selected_leaf.closer.Show(True)
				self.issues_with_soap.append(self.selected_issue[1])
				
			else:
				if self.selected_issue[1] in self.issues_with_soap:
					print "Issue has already soap"
					wx.wxMessageBox("The SOAP note can't be created.\nCurrently selected health issue has yet an associated SOAP note in this encounter.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
				else:
					# FIXME calculate height
					selected_leaf.AddLeaf(SOAPMultiSash.MV_VER, 130)

			print "Issues with soap: %s"%(self.issues_with_soap)
			self.check_buttons()	
		
	#--------------------------------------------------------
	def on_remove(self, event):
		"""
		Creates and displays a new SOAP input editor
		"""
		if self.soap_multisash.GetSelectedLeaf() is None or len(self.issues_with_soap) == 0:
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.", caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION, parent = self)
		else:
			print "Remove SOAP"
			selected_leaf = self.soap_multisash.GetSelectedLeaf()
			selected_leaf.DestroyLeaf()

			print "Issues with soap: %s"%(self.issues_with_soap)
			self.check_buttons()	
	#--------------------------------------------------------	
	def on_patient_selected(self):
		"""
		Current patient changed
		"""
		self._schedule_data_reget()
	#--------------------------------------------------------
	def on_health_issue_selected(self, event):
		"""
		Displays information for a selected tree node
		"""		
		self.selected_issue = [self.health_issues_list.GetSelection(), self.health_issues_list.GetClientData(self.health_issues_list.GetSelection())]
		print 'Selected: %s'%(self.selected_issue)
		if not self.new_button.IsEnabled():
			self.new_button.Enable(True)

	#--------------------------------------------------------	
	def check_buttons(self):
		"""
		Check and configure adecuate buttons enable state
		"""
		enable = True
		if not self.soap_multisash.GetSelectedLeaf() is  None and len(self.issues_with_soap) > 0:
			enable = True
		else:
			enable = False
		self.save_button.Enable(enable)
		self.clear_button.Enable(enable)
		self.remove_button.Enable(enable)

		if self.soap_multisash.GetSelectedLeaf() is  None:
			self.new_button.Enable(False)
		else:
			self.new_button.Enable(True)
		
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		print "Populate with data!!"
		self.reset_ui_content()
		if self.refresh_tree():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		

	def get_issues_with_soap(self):
		"""
		Retrieves EMR tree's health issues for wich a soap note is created
		"""
		return self.issues_with_soap
		
	def get_selected_issue(self):
		"""
		Retrieves EMR tree's selected health issue
		"""
		return self.selected_issue
		
	def refresh_tree(self):
		"""
		Updates EMR browser data
		"""
		# EMR tree root item
		#demographic_record = self.patient.get_demographic_record()
		#names = demographic_record.get_names()
		#root_item = self.health_issues_list.AddRoot(_('%s %s EMR') % (names['first'], names['last']))
		if self.health_issues_list.GetCount() > 0:
			return False
		cont = 0
		for a_health_issue in self.emr.get_health_issues():			
			cont = cont+1
			a_key = '#%s %s'%(cont,a_health_issue['description'])
			self.health_issues_list.Append(a_key,a_health_issue)
			
		# Set sash position
		self.soap_emr_splitter.SetSashPosition(self.soap_emr_splitter.GetSizeTuple()[0]/2, True)

		return True


	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information displayed in browser (tree and details area)
		"""
		self.selected_issue = None
		self.issues_with_soap = []
		self.health_issues_list.Clear()
		self.soap_multisash.Clear()
		self.soap_multisash.SetDefaultChildClassAndControllerObject(cSOAPControl,self)
		

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
