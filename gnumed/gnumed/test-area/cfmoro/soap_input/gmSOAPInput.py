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
__version__ = "$Revision: 1.23 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals, gmWhoAmI
from Gnumed.business import gmEMRStructItems, gmPatient, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

sys.path.append ('../../ian') 
import SOAP2

import SOAPMultiSash

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
		self.__soap_label = wx.wxStaticText(self, -1, "Select issue and press 'New'")
		# related health issue
		self.__health_issue = None
		print "...creating new soap input widget"
		# flag indicating saved state
		self.is_saved = False
		
		# soap rich and smart text editor
		# FIXME currently copied form SOAP2.py
		self.__soap_text_editor = SOAP2.ResizingWindow (self, -1, size = wx.wxSize (300, 150))
		self.__S = SOAP2.ResizingSTC (self.__soap_text_editor, -1)
		self.__S.AttachMatcher (cMatchProvider_FixedList (Subjlist))
		self.__O = SOAP2.ResizingSTC (self.__soap_text_editor, -1)
		self.__A = SOAP2.ResizingSTC (self.__soap_text_editor, -1)
		self.__A.AttachMatcher (cMatchProvider_FixedList (AOElist))
		self.__P = SOAP2.ResizingSTC (self.__soap_text_editor, -1)
		self.__P.AttachMatcher (cMatchProvider_FixedList (Planlist))
		self.__S.prev = None
		self.__S.next = self.__O
		self.__O.prev = self.__S
		self.__O.next = self.__A
		self.__A.prev = self.__O
		self.__A.next = self.__P
		self.__P.prev = self.__A
		self.__P.next = None
		self.__soap_text_editor.AddWidget (self.__S, gmSOAPimporter.soap_bundle_SOAP_CATS[0])
		self.__soap_text_editor.Newline ()
		self.__soap_text_editor.AddWidget (self.__O, gmSOAPimporter.soap_bundle_SOAP_CATS[1])
		self.__soap_text_editor.Newline ()
		self.__soap_text_editor.AddWidget (self.__A, gmSOAPimporter.soap_bundle_SOAP_CATS[2])
		self.__soap_text_editor.Newline ()
		self.__soap_text_editor.AddWidget (self.__P, gmSOAPimporter.soap_bundle_SOAP_CATS[3])
		self.__soap_text_editor.SetValues ({gmSOAPimporter.soap_bundle_SOAP_CATS[0]:"sore ear", gmSOAPimporter.soap_bundle_SOAP_CATS[3]:"Amoxycillin"})
		self.__soap_text_editor.ReSize ()
		
		# sizers for widgets
		self.__soap_control_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__soap_control_sizer.Add(self.__soap_label)		   
		self.__soap_control_sizer.Add(self.__soap_text_editor)
		
		# do layout
		self.SetSizerAndFit(self.__soap_control_sizer)		
		
	#--------------------------------------------------------
	def SetHealthIssue(self, selected_issue):
		"""
		Set the related health issue for this SOAP input widget.
		Update heading label with health issue data.
		
		@type selected_issue: gmEMRStructItems.cHealthIssue
		@param selected_issue: SOAP input widget's related health issue
		"""
		self.__health_issue = selected_issue
		if self.__health_issue is None or len(self.__health_issue) == 0:
			self.__soap_label.SetLabel("Select issue and press 'New'")
		else:
			txt = '%s# %s'%(self.__health_issue[0]+1,self.__health_issue[1]['description'])
			# update staticText content and recalculate sizer internal values
			self.__SetHeading(txt)
		self.ShowContents()
			
	#--------------------------------------------------------
	def GetHealthIssue(self):
		"""
		Retrieve the related health issue for this SOAP input widget.
		"""
		return self.__health_issue
	
	#--------------------------------------------------------
	def GetSOAP(self):
		"""
		Retrieves widget's SOAP text editor
		"""
		return self.__soap_text_editor
	
	#--------------------------------------------------------
	def ClearSOAP(self):
		"""
		Clear any entries in widget's SOAP text editor
		"""
		self.__soap_text_editor.SetValues ({"Subjective":" ", "Objective":" ",
			"Assessment":" ", "Plan":" "})

	#--------------------------------------------------------
	def HideContents(self):
		"""
		Hide widget's components (health issue heading and SOAP text editor)
		"""
		self.__soap_label.Hide()
		self.__soap_text_editor.Hide()
	
	#--------------------------------------------------------	
	def ShowContents(self):
		"""
		Show widget's components (health issue heading and SOAP text editor)
		"""
		self.__soap_label.Show(True)
		self.__soap_text_editor.Show(True)

	#--------------------------------------------------------
	def IsContentShown(self):
		"""
		Check if contents are being shown
		"""
		return self.__soap_label.IsShown()
		
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
			self.__SetHeading(self.__soap_label.GetLabel() + '. SAVED')

	#--------------------------------------------------------	
	def IsSaved(self):
		"""
		Check  SOAP input widget saved (dumped to backend) state
		
		"""
		return self.is_saved
			
	#--------------------------------------------------------	
	def __SetHeading(self, txt):
		"""
		Configure SOAP widget's heading title
		
		@param txt: New widget's heading title to set
		@type txt: string
		"""
		self.__soap_label.SetLabel(txt)
		size = self.__soap_label.GetBestSize()
		self.__soap_control_sizer.SetItemMinSize(self.__soap_label, size.width, size.height)
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
		self.__patient = gmPatient.gmCurrentPatient()
		# active patient's emr
		self.__emr = self.__patient.get_clinical_record()
		# store the currently selected SOAP input widget on health issues list
		# in the form of a two element list [issue index in list : health issue vo]
		self.__selected_issue = []
		# store the health issues wich has an associated SOAP note created.
		# Useful to avoid duplicate SOAP notes for the same health issue
		self.__issues_with_soap = []
		# multisash's selected leaf		
		self.__selected_leaf = None
		# multisash's selected soap widget
		self.__selected_soap = None		
		
		# ui contruction and event handling set up		
		self.__do_layout()
		self.__register_interests()
		self._populate_with_data()

	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Arrange SOAP input panel widgets
		"""		
		
		# SOAP input panel main splitter window
		self.__soap_emr_splitter = wx.wxSplitterWindow(self, -1)

		# SOAP input widget's (left) panel
		self.__soap_panel = wx.wxPanel(self.__soap_emr_splitter,-1)
		# SOAP multisash
		self.__soap_multisash = SOAPMultiSash.cSOAPMultiSash(self.__soap_panel, -1)
		# SOAP action buttons, disabled at startup
		self.__save_button = wx.wxButton(self.__soap_panel, -1, "&Save")
		self.__save_button.Disable()
		self.__clear_button = wx.wxButton(self.__soap_panel, -1, "&Clear")
		self.__clear_button.Disable()
		self.__new_button = wx.wxButton(self.__soap_panel, -1, "&New")
		self.__new_button.Disable()
		self.__remove_button = wx.wxButton(self.__soap_panel, -1, "&Remove")
		self.__remove_button.Disable()

		# health issues list (right) panel
		self.__issues_panel = wx.wxPanel(self.__soap_emr_splitter,-1)
		self.__health_issues_list = wx.wxListBox(
			self.__issues_panel,
			-1,
			style= wx.wxNO_BORDER
		)			
		
		# action buttons sizer
		self.__soap_actions_sizer = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.__soap_actions_sizer.Add(self.__save_button, 0,wx.wxSHAPED)
		self.__soap_actions_sizer.Add(self.__clear_button, 0,wx.wxSHAPED)
		self.__soap_actions_sizer.Add(self.__new_button, 0,wx.wxSHAPED)
		self.__soap_actions_sizer.Add(self.__remove_button, 0,wx.wxSHAPED)
		# SOAP area main sizer
		self.__soap_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__soap_panel_sizer.Add(self.__soap_multisash, 1, wx.wxEXPAND)		
		self.__soap_panel_sizer.Add(self.__soap_actions_sizer)
		self.__soap_panel.SetSizerAndFit(self.__soap_panel_sizer)		
		
		# health issues list area main sizer
		self.__issues_panel_sizer = wx.wxBoxSizer(wx.wxVERTICAL)	
		self.__issues_panel_sizer.Add(self.__health_issues_list, 1, wx.wxEXPAND)
		self.__issues_panel.SetSizerAndFit(self.__issues_panel_sizer)		
				
		# SOAP - issues list splitter basic configuration
		self.__soap_emr_splitter.SetMinimumPaneSize(20)
		self.__soap_emr_splitter.SplitVertically(self.__soap_panel, self.__issues_panel)
		
		# SOAP input panel main sizer
		self.__main_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__main_sizer.Add(self.__soap_emr_splitter, 1, wx.wxEXPAND, 0)
		self.SetSizerAndFit(self.__main_sizer)

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configure enabled event signals
		"""
		# wx.wxPython events
		wx.EVT_LISTBOX(self.__health_issues_list, self.__health_issues_list.GetId(),
			self.__on_health_issue_selected)
		wx.EVT_BUTTON(self.__save_button, self.__save_button.GetId(), self.__on_save)
		wx.EVT_BUTTON(self.__clear_button, self.__clear_button.GetId(),
			self.__on_clear)
		wx.EVT_BUTTON(self.__new_button, self.__new_button.GetId(), self.__on_new)
		wx.EVT_BUTTON(self.__remove_button, self.__remove_button.GetId(),
			self.__on_remove)
					
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(),
			receiver=self.__on_patient_selected)
		
	#--------------------------------------------------------
	def __on_save(self, event):
		"""
		Obtain SOAP data from selected editor and dump to backend
		"""
		# security check
		if not self.__allow_perform_action(self.__save_button.GetId()):
			return
	
		#FIXME initial development implementation. Refactor and update
		vepisode_id = self.__emr.get_active_episode()['pk_episode']
		vencounter_id = self.__emr.get_active_episode()['pk_episode']
		vstaff_id = gmWhoAmI.cWhoAmI().get_staff_ID()
		# compose soap bundle
		clin_ctx = {
			gmSOAPimporter.soap_bundle_EPISODE_ID_KEY:vepisode_id,
			gmSOAPimporter.soap_bundle_ENCOUNTER_ID_KEY: vencounter_id,
			gmSOAPimporter.soap_bundle_STAFF_ID_KEY: vstaff_id
		}
		bundle = []
		# iterate over input keys
		for input_key in self.__selected_soap.GetSOAP().GetValues().keys():
			print "*** KEY: %s" % input_key
			bundle.append(
			{
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY:input_key,
				gmSOAPimporter.soap_bundle_TYPES_KEY:['Hx'],
				gmSOAPimporter.soap_bundle_TEXT_KEY:self.__selected_soap.GetSOAP().GetValues()[input_key],
				gmSOAPimporter.soap_bundle_CLIN_CTX_KEY:clin_ctx,
				gmSOAPimporter.soap_bundle_STRUCT_DATA_KEY:{}
			}
			)

		# let's dump soap contents		   
		importer = gmSOAPimporter.cSOAPImporter()
		print "*** BUNDLE: %s" % bundle
		importer.import_soap(bundle)
				
		# update buttons
		self.__selected_soap.SetSaved(True)
		self.check_buttons()
		print "Done!"
					
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		Clear currently selected SOAP input widget
		"""
		
		# security check
		if not self.__allow_perform_action(self.__clear_button.GetId()):
			return

		print "Clear SOAP"
		self.__selected_soap.ClearSOAP()

	#--------------------------------------------------------
	def __on_new(self, event):
		"""
		Create and display a new SOAP input widget on the stack
		"""

		# security check
		if not self.__allow_perform_action(self.__new_button.GetId()):
			return
			
		print "New SOAP"		
		# first SOAP input widget is displayed by showing an empty hidden one
		if not self.__selected_soap is None and not self.__selected_soap.IsContentShown():
			self.__issues_with_soap.append(self.__selected_issue[1])
			self.__selected_soap.SetHealthIssue(self.__selected_issue)
			self.__selected_leaf.GetSOAPPanel().Show()
			self.__selected_leaf.detail.Select()
			self.__selected_leaf.creatorHor.Show(True)
			self.__selected_leaf.closer.Show(True)
			
		else:
			# create SOAP input widget for currently selected issue
			# FIXME: programmatically calculate height
			self.__selected_leaf.AddLeaf(SOAPMultiSash.MV_VER, 130)

		print "Issues with soap: %s"%(self.__issues_with_soap)
		
		
	#--------------------------------------------------------
	def __on_remove(self, event):
		"""
		Removes currently selected SOAP input widget
		"""

		# security check
		if not self.__allow_perform_action(self.__remove_button.GetId()):
			return
			
		print "Remove SOAP"		
		self.__selected_leaf.DestroyLeaf()

		print "Issues with soap: %s"%(self.__issues_with_soap)
		# there's no leaf selected after deletion, so disable all buttons
		self.__save_button.Disable()
		self.__clear_button.Disable()
		self.__remove_button.Disable()
		# enable new button is soap stack is empty
		#selected_leaf = self.__soap_multisash.GetSelectedLeaf()
		#if self.__selected_soap.GetHealthIssue() is None:
		#	self.__new_button.Enable(True)
		
	#--------------------------------------------------------	
	def __on_patient_selected(self):
		"""
		Current patient changed
		"""
		self.__schedule_data_reget()
		
	#--------------------------------------------------------
	def __on_health_issue_selected(self, event):
		"""
		When the user changes health issue selection, update selected issue
		reference and update buttons according its input status.
		"""		
		self.__selected_issue = [self.__health_issues_list.GetSelection(),
			self.__health_issues_list.GetClientData(self.__health_issues_list.GetSelection())]
		#print 'Selected: %s'%(self.__selected_issue)
		
		#if not self.__new_button.IsEnabled():
		#	self.__new_button.Enable(True)

		self.check_buttons()	

	#--------------------------------------------------------	
	def check_buttons(self):
		"""
		Check and configure adecuate buttons enabling state
		"""
		print "cSOAPInput.check_buttons" 
		
		if self.__selected_leaf is None:
			print "Selected leaf NONE"
		if self.__selected_soap is None:
			print "Selected soap NONE"
		if len(self.__selected_issue)==0 is None:
			print "Selected issues 0"									
		if self.__selected_leaf is None or self.__selected_soap is None or len(self.__selected_issue)==0:
			print "Won't check buttons for None leaf/soap/selected_issue"
			return
		
		# if soap stack is empty, disable save, clear and remove buttons
		print "Health issues: %s"%(self.__selected_soap.GetHealthIssue())
		if self.__selected_soap.GetHealthIssue() is None or self.__selected_soap.IsSaved():
			self.__save_button.Enable(False)
			self.__clear_button.Enable(False)
			self.__remove_button.Enable(False)
		else:
			self.__save_button.Enable(True)
			self.__clear_button.Enable(True)
			self.__remove_button.Enable(True)
		
		# allow new when soap stack is empty
		# avoid enabling new button to create more than one soap per issue.		
		if self.__selected_issue[1] in self.__issues_with_soap:
			self.__new_button.Enable(False)
		else:
			self.__new_button.Enable(True)
			
		# disabled save button when soap was dumped to backend
		#print "Saved: %s"%(self.__selected_soap.IsSaved())
		if self.__selected_soap.IsSaved():
			self.__remove_button.Enable(True)

	#--------------------------------------------------------	
	def __allow_perform_action(self, action_id):
		"""
		Check if a concrte action can be performed for selected SOAP input widget
		
		@param action_id: ui widget wich fired the action
		"""
		if (self.__selected_leaf is None or \
			len(self.__issues_with_soap) == 0) and \
			action_id != self.__new_button.GetId():
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.",
				caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
				parent = self)
			return False

		if (self.__selected_issue is None or len(self.__selected_issue) == 0) \
			and action_id == self.__new_button.GetId():
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
		if self.__refresh_issues_list():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
	def get_issues_with_soap(self):
		"""
		Retrieve health issues for wich a SOAP note is created
		"""
		return self.__issues_with_soap
		
	#--------------------------------------------------------		
	def get_selected_issue(self):
		"""
		Retrieves selected health issue in list
		"""
		return self.__selected_issue
	
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
		self.__selected_leaf = selected_leaf		
		self.__selected_soap = selected_soap		
		print "\nSelected leaf: %s"%(self.__selected_leaf)		
		print "Selected SOAP: %s"%(self.__selected_soap)
		self.check_buttons()
					
	#--------------------------------------------------------
	def __refresh_issues_list(self):
		"""
		Updates health issues list
		"""
		# FIXME remove
		if self.__health_issues_list.GetCount() > 0:
			return False
		cont = 0
		for a_health_issue in self.__emr.get_health_issues():			
			cont = cont+1
			a_key = '#%s %s'%(cont,a_health_issue['description'])
			self.__health_issues_list.Append(a_key,a_health_issue)
			
		# Set sash position
		self.__soap_emr_splitter.SetSashPosition(self.__soap_emr_splitter.GetSizeTuple()[0]/2, True)

		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__selected_issue = []
		self.__issues_with_soap = []
		self.__health_issues_list.Clear()
		self.__soap_multisash.Clear()
		self.__soap_multisash.SetController(self)
		

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
