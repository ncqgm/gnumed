"""
	GnuMed SOAP input panel
"""
#================================================================
__version__ = "$Revision: 1.3 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPatient
from Gnumed.wxpython import gmRegetMixin
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

import SOAP2

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================

# FIXME attribute encapsulation and private methods

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
	
	def __init__(self, parent, health_issue):
	
		# panel (super) initialization
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		
		# soap's health issue heading
		self.soap_label = wx.wxStaticText(self, -1, health_issue['description'])
		
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
		self.exporter = gmPatientExporter.cEmrExport(patient = self.patient)
		self.selected_issue = None		
		
		# ui contruction and event interests
		self.do_layout()
		self.register_interests()
		self.reset_ui_content()

	#--------------------------------------------------------
	def do_layout(self):
		"""
		Arranges SOAP input layout
		"""
		
		import SOAPMultiSash	
		
		# SOAP input panel main splitter window
		self.soap_emr_splitter = wx.wxSplitterWindow(self, -1)

		# SOAP panel
		self.soap_panel = wx.wxPanel(self.soap_emr_splitter,-1)
		# SOAP multisash
		self.soap_multisash = SOAPMultiSash.cSOAPMultiSash(self.soap_panel, -1)
		# SOAP action buttons
		self.save_button = wx.wxButton(self.soap_panel, -1, "&Save")
		self.clear_button = wx.wxButton(self.soap_panel, -1, "&Clear")
		self.new_button = wx.wxButton(self.soap_panel, -1, "&New")
		self.remove_button = wx.wxButton(self.soap_panel, -1, "&Remove")

		# EMR tree
		self.emr_panel = wx.wxPanel(self.soap_emr_splitter,-1)
		self.emr_tree = wx.wxTreeCtrl (
			self.emr_panel,
			-1,
			style=wx.wxTR_HAS_BUTTONS | wx.wxNO_BORDER
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
		self.emr_panel_sizer.Add(self.emr_tree, 1, wx.wxEXPAND)
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
		wx.EVT_TREE_SEL_CHANGED(self.emr_tree,self.emr_tree.GetId(), self.on_tree_item_selected)
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
		#result = self.soap_multisash.GetSaveData()
		selected_soap_panel = self.soap_multisash.GetSelectedSOAPPanel()
		print "Saving SOAP: %s"%(selected_soap_panel.GetSOAP().GetValues())
			
	#--------------------------------------------------------
	def on_clear(self, event):
		"""
		Clears selected SOAP editor
		"""
		print "Clear SOAP"
		selected_soap_panel = self.soap_multisash.GetSelectedSOAPPanel()
		selected_soap_panel.ClearSOAP()
		
	#--------------------------------------------------------
	def on_new(self, event):
		"""
		Creates and displays a new SOAP input editor
		"""
		print "New SOAP"		
		
	#--------------------------------------------------------
	def on_remove(self, event):
		"""
		Creates and displays a new SOAP input editor
		"""
		print "Remove SOAP"		
		
	#--------------------------------------------------------	
	def on_patient_selected(self):
		"""
		Current patient changed
		"""
		self.exporter.set_patient(self.patient)
		self._schedule_data_reget()
	#--------------------------------------------------------
	def on_tree_item_selected(self, event):
		"""
		Displays information for a selected tree node
		"""
		sel_item = event.GetItem()
		sel_item_obj = self.emr_tree.GetPyData(sel_item)

		if (isinstance(sel_item_obj, gmEMRStructItems.cHealthIssue)):
			self.selected_issue = sel_item_obj				
			if not (isinstance(self.soap_multisash.GetDefaultChildClass(), cSOAPControl)):
				self.soap_multisash.SetDefaultChildClassAndControllerObject(cSOAPControl,self)
				self.Refresh()
			
				

	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		self.reset_ui_content()
		if self.refresh_tree():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
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
		demographic_record = self.patient.get_demographic_record()
		names = demographic_record.get_names()
		root_item = self.emr_tree.AddRoot(_('%s %s EMR') % (names['first'], names['last']))

		# Obtain all the tree from exporter
		self.exporter.get_historical_tree(self.emr_tree)

		# Expand root node and display patient summary info
		self.emr_tree.Expand(root_item)

		# Set sash position
		self.soap_emr_splitter.SetSashPosition(self.soap_emr_splitter.GetSizeTuple()[0]/2, True)

		# FIXME: error handling
		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information displayed in browser (tree and details area)
		"""
		self.emr_tree.DeleteAllItems()
		

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

	# Ask patient to dump and set in exporter object
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
		soap_input.refresh_tree()
		
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
