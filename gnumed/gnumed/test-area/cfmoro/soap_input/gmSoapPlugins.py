"""
	GnuMed multisash notes input panel
	
	Health problems are selected in a list.
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
__version__ = "$Revision: 1.2 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals, gmWhoAmI
from Gnumed.business import gmEMRStructItems, gmPatient, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmResizingWidgets, gmSoapWidgets
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

import SOAPMultiSash

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


# FIXME attribute encapsulation and private methods
# FIXME i18n
#============================================================					  
class cMultiSashedSoapPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):
	"""
	Basic multi-sash based note input panel.
	Currently, displays a dynamic stack of note input widgets on the left
	and the health problems list on the right.
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
		self.__pat = gmPatient.gmCurrentPatient()
		# active patient's emr
		self.__emr = self.__pat.get_clinical_record()
		# store the currently selected SOAP input widget on health problems list
		# in the form of a two element list [issue index in list : health issue vo]
		self.__selected_issue = []
		# store the health problems wich has an associated SOAP note created.
		# Useful to avoid duplicate SOAP notes for the same health issue
		self.__problems_with_soap = []
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
		self.__splitter = wx.wxSplitterWindow(self, -1)

		# left hand side
		# - soap inputs panel
		PNL_soap = wx.wxPanel(self.__splitter, -1)
		self.__soap_multisash = SOAPMultiSash.cSOAPMultiSash(PNL_soap, -1)
		# - buttons
		# FIXME: tooltips
		self.__BTN_save = wx.wxButton(PNL_soap, -1, "&Save")
		self.__BTN_save.Disable()
		self.__BTN_clear = wx.wxButton(PNL_soap, -1, "&Clear")
		self.__BTN_clear.Disable()
		self.__BTN_new = wx.wxButton(PNL_soap, -1, "&New")
		self.__BTN_new.Disable()
		self.__BTN_remove = wx.wxButton(PNL_soap, -1, "&Remove")
		self.__BTN_remove.Disable()
		# - arrange widgets
		szr_btns_left = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns_left.Add(self.__BTN_save, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_clear, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_new, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_remove, 0, wx.wxSHAPED)
		szr_left = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_left.Add(self.__soap_multisash, 1, wx.wxEXPAND)
		szr_left.Add(szr_btns_left)
		PNL_soap.SetSizerAndFit(szr_left)

		# right hand side
		# - problem list
#		PNL_problems = wx.wxPanel(self.__splitter, -1)
		self.__problem_list = wx.wxListBox (
			self.__splitter,
#			PNL_problems,
			-1,
			style= wx.wxNO_BORDER
		)
#		# - arrange widgets
#		szr_right = wx.wxBoxSizer(wx.wxVERTICAL)
#		szr_right.Add(self.__problem_list, 1, wx.wxEXPAND)
#		PNL_problems.SetSizerAndFit(szr_right)

		# arrange widgets
		self.__splitter.SetMinimumPaneSize(20)
#		self.__splitter.SplitVertically(PNL_soap, PNL_problems)
		self.__splitter.SplitVertically(PNL_soap, self.__problem_list)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__splitter, 1, wx.wxEXPAND, 0)
		self.SetSizerAndFit(szr_main)

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		wx.EVT_LISTBOX(self.__problem_list, self.__problem_list.GetId(), self.__on_problem_selected)
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self.__on_save)
		wx.EVT_BUTTON(self.__BTN_clear, self.__BTN_clear.GetId(), self.__on_clear)
		wx.EVT_BUTTON(self.__BTN_new, self.__BTN_new.GetId(), self.__on_new)
		wx.EVT_BUTTON(self.__BTN_remove, self.__BTN_remove.GetId(), self.__on_remove)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self.__on_patient_selected)
	#--------------------------------------------------------
	def __on_problem_selected(self, event):
		"""
		When the user changes health issue selection, update selected issue
		reference and update buttons according its input status.
		"""
		issue_idx = self.__problem_list.GetSelection()
		self.__selected_issue = [
			issue_idx,
			self.__problem_list.GetClientData(issue_idx)
		]
		#print 'Selected: %s'%(self.__selected_issue)

		#if not self.__BTN_new.IsEnabled():
		#	self.__BTN_new.Enable(True)

		self.check_buttons()
	#--------------------------------------------------------
	def __on_save(self, event):
		"""
		Obtain SOAP data from selected editor and dump to backend
		"""
		# security check
		if not self.__allow_perform_action(self.__BTN_save.GetId()):
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
		for input_key in self.__selected_soap.GetSOAP().GetValue().keys():
			print "*** KEY: %s" % input_key
			bundle.append(
			{
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY:input_key,
				gmSOAPimporter.soap_bundle_TYPES_KEY:['Hx'],
				gmSOAPimporter.soap_bundle_TEXT_KEY:self.__selected_soap.GetSOAP().GetValue()[input_key],
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
		if not self.__allow_perform_action(self.__BTN_clear.GetId()):
			return

		print "Clear SOAP"
		self.__selected_soap.ClearSOAP()

	#--------------------------------------------------------
	def __on_new(self, event):
		"""
		Create and display a new SOAP input widget on the stack
		"""

		# security check
		if not self.__allow_perform_action(self.__BTN_new.GetId()):
			return
			
		print "New SOAP"		
		# first SOAP input widget is displayed by showing an empty hidden one
		if not self.__selected_soap is None and not self.__selected_soap.IsContentShown():
			self.__problems_with_soap.append(self.__selected_issue[1])
			self.__selected_soap.SetHealthIssue(self.__selected_issue)
			self.__selected_leaf.GetSOAPPanel().Show()
			self.__selected_leaf.detail.Select()
			self.__selected_leaf.creatorHor.Show(True)
			self.__selected_leaf.closer.Show(True)
			
		else:
			# create SOAP input widget for currently selected issue
			# FIXME: programmatically calculate height
			self.__selected_leaf.AddLeaf(SOAPMultiSash.MV_VER, 130)

		print "problems with soap: %s"%(self.__problems_with_soap)
		
		
	#--------------------------------------------------------
	def __on_remove(self, event):
		"""
		Removes currently selected SOAP input widget
		"""

		# security check
		if not self.__allow_perform_action(self.__BTN_remove.GetId()):
			return
			
		print "Remove SOAP"		
		self.__selected_leaf.DestroyLeaf()

		print "problems with soap: %s"%(self.__problems_with_soap)
		# there's no leaf selected after deletion, so disable all buttons
		self.__BTN_save.Disable()
		self.__BTN_clear.Disable()
		self.__BTN_remove.Disable()
		# enable new button is soap stack is empty
		#selected_leaf = self.__soap_multisash.GetSelectedLeaf()
		#if self.__selected_soap.GetHealthIssue() is None:
		#	self.__BTN_new.Enable(True)
		
	#--------------------------------------------------------	
	def __on_patient_selected(self):
		"""
		Current patient changed
		"""
		self.__schedule_data_reget()
	#--------------------------------------------------------	
	def check_buttons(self):
		"""
		Check and configure adecuate buttons enabling state
		"""
		print "cMultiSashedSoapPanel.check_buttons" 
		
		if self.__selected_leaf is None:
			print "Selected leaf NONE"
		if self.__selected_soap is None:
			print "Selected soap NONE"
		if len(self.__selected_issue)==0 is None:
			print "Selected problems 0"									
		if self.__selected_leaf is None or self.__selected_soap is None or len(self.__selected_issue)==0:
			print "Won't check buttons for None leaf/soap/selected_issue"
			return
		
		# if soap stack is empty, disable save, clear and remove buttons
		print "Health problems: %s"%(self.__selected_soap.GetHealthIssue())
		if self.__selected_soap.GetHealthIssue() is None or self.__selected_soap.IsSaved():
			self.__BTN_save.Enable(False)
			self.__BTN_clear.Enable(False)
			self.__BTN_remove.Enable(False)
		else:
			self.__BTN_save.Enable(True)
			self.__BTN_clear.Enable(True)
			self.__BTN_remove.Enable(True)
		
		# allow new when soap stack is empty
		# avoid enabling new button to create more than one soap per issue.		
		if self.__selected_issue[1] in self.__problems_with_soap:
			self.__BTN_new.Enable(False)
		else:
			self.__BTN_new.Enable(True)
			
		# disabled save button when soap was dumped to backend
		#print "Saved: %s"%(self.__selected_soap.IsSaved())
		if self.__selected_soap.IsSaved():
			self.__BTN_remove.Enable(True)

	#--------------------------------------------------------	
	def __allow_perform_action(self, action_id):
		"""
		Check if a concrte action can be performed for selected SOAP input widget
		
		@param action_id: ui widget wich fired the action
		"""
		if (self.__selected_leaf is None or \
			len(self.__problems_with_soap) == 0) and \
			action_id != self.__BTN_new.GetId():
			wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.",
				caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
				parent = self)
			return False

		if (self.__selected_issue is None or len(self.__selected_issue) == 0) \
			and action_id == self.__BTN_new.GetId():
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
		if self.__refresh_problems_list():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
	def get_problems_with_soap(self):
		"""
		Retrieve health problems for wich a SOAP note is created
		"""
		return self.__problems_with_soap
		
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
		@type selected_soap: gmSOAPInput.cSoapPanel
		"""
		print "cMultiSashedSoapPanel.set_selected_leaf"
		self.__selected_leaf = selected_leaf		
		self.__selected_soap = selected_soap		
		print "\nSelected leaf: %s"%(self.__selected_leaf)		
		print "Selected SOAP: %s"%(self.__selected_soap)
		self.check_buttons()
					
	#--------------------------------------------------------
	def __refresh_problems_list(self):
		"""
		Updates health problems list
		"""
		# FIXME remove
		if self.__problem_list.GetCount() > 0:
			return False
		cont = 0
		for a_health_issue in self.__emr.get_health_problems():			
			cont = cont+1
			a_key = '#%s %s'%(cont,a_health_issue['description'])
			self.__problem_list.Append(a_key,a_health_issue)
			
		# Set sash position
		self.__splitter.SetSashPosition(self.__splitter.GetSizeTuple()[0]/2, True)

		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__selected_issue = []
		self.__problems_with_soap = []
		self.__problem_list.Clear()
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
	_log.Log (gmLog.lInfo, "starting notes input panel...")

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
		soap_input = cMultiSashedSoapPanel(application.frame, -1)
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

	_log.Log (gmLog.lInfo, "closing notes input...")
