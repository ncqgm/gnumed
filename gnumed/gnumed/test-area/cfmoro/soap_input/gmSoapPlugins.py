"""GnuMed SOAP input widget.
	
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
__version__ = "$Revision: 1.9 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmSignals, gmWhoAmI
from Gnumed.business import gmEMRStructItems, gmPatient, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmSOAPWidgets
from Gnumed.pycommon.gmPyCompat import *

import SOAPMultiSash, gmEMRStructWidgets

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
		wx.wxPanel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize,
			style = wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		pat = gmPatient.gmCurrentPatient()
		self.__emr = pat.get_clinical_record()
		self.__managed_episodes = []			# avoid duplicate SOAP notes
		self.__selected_episode = None

		# multisash's selected leaf
		self.__focussed_soap_editor = None
		# multisash's selected soap widget
		self.__selected_soap = None

		# ui contruction and event handling set up
		self.__do_layout()
		self.__register_interests()
		self._populate_with_data()
#		self._schedule_data_reget()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.

		left: soap editors
		right: problem list (mix of issues and episodes)
		"""
		# SOAP input panel main splitter window
		self.__splitter = wx.wxSplitterWindow(self, -1)

		# left hand side
		# - soap inputs panel
		PNL_soap_editors = wx.wxPanel(self.__splitter, -1)
		print "CREATING SOAPMultiSash" 
		self.__soap_multisash = SOAPMultiSash.cSOAPMultiSash(self, PNL_soap_editors, -1)
		print "SETTING SOAPMultiSash controller" 
		#self.__soap_multisash.SetController(self)		# what does this do ?
		# - buttons
		self.__BTN_save = wx.wxButton(PNL_soap_editors, -1, _('&Save'))
		self.__BTN_save.Disable()
		self.__BTN_save.SetToolTipString(_('save focussed progress note into medical record'))

		self.__BTN_clear = wx.wxButton(PNL_soap_editors, -1, _('&Clear'))
		self.__BTN_clear.Disable()
		self.__BTN_clear.SetToolTipString(_('clear focussed progress note'))

		self.__BTN_remove = wx.wxButton(PNL_soap_editors, -1, _('&Remove'))
		self.__BTN_remove.Disable()
		self.__BTN_remove.SetToolTipString(_('close focussed progress note'))

		self.__BTN_new = wx.wxButton(PNL_soap_editors, -1, _('&New'))
		self.__BTN_new.Disable()
		self.__BTN_new.SetToolTipString(_('create empty progress note for new problem'))

		# - arrange widgets
		szr_btns_left = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns_left.Add(self.__BTN_save, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_clear, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_new, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_remove, 0, wx.wxSHAPED)
		szr_left = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_left.Add(self.__soap_multisash, 1, wx.wxEXPAND)
		szr_left.Add(szr_btns_left)
		PNL_soap_editors.SetSizerAndFit(szr_left)

		# right hand side
		# - problem list
#		PNL_problems = wx.wxPanel(self.__splitter, -1)
		self.__LST_problems = wx.wxListBox (
			self.__splitter,
#			PNL_problems,
			-1,
			style= wx.wxNO_BORDER
		)
#		# - arrange widgets
#		szr_right = wx.wxBoxSizer(wx.wxVERTICAL)
#		szr_right.Add(self.__LST_problems, 1, wx.wxEXPAND)
#		PNL_problems.SetSizerAndFit(szr_right)

		# arrange widgets
		self.__splitter.SetMinimumPaneSize(20)
#		self.__splitter.SplitVertically(PNL_soap_editors, PNL_problems)
		self.__splitter.SplitVertically(PNL_soap_editors, self.__LST_problems)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__splitter, 1, wx.wxEXPAND, 0)
		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""
		Updates health problems list
		"""
		self.__LST_problems.Clear()
		problems = self.__emr.get_problems()
		print 'PROBLEMS: %s' % problems
		for problem in problems:
			self.__LST_problems.Append(problem['problem'], problem)
		splitter_width = self.__splitter.GetSizeTuple()[0]
		self.__splitter.SetSashPosition((splitter_width / 2), True)
		return True
	#--------------------------------------------------------
	def __update_button_state(self):
		"""
		Check and configure adecuate buttons enabling state
		"""
		print "cMultiSashedSoapPanel.__update_button_state"

		if None in (self.__focussed_soap_editor, self.__selected_soap, self.__selected_episode):
			print "Selected leaf:", self.__focussed_soap_editor
			print "Selected soap:", self.__selected_soap
			print "Selected episode:", self.__selected_episode
			print "Won't check buttons for None leaf/soap/selected_episode"
			return False
						
		# if soap stack is empty, disable save, clear and remove buttons		
		if isinstance(self.__selected_soap, SOAPMultiSash.EmptyWidget) or self.__selected_soap.IsSaved():
			self.__BTN_save.Enable(False)
			self.__BTN_clear.Enable(False)
			self.__BTN_remove.Enable(False)
		else:
			self.__BTN_save.Enable(True)
			self.__BTN_clear.Enable(True)
			self.__BTN_remove.Enable(True)

		# allow new when soap stack is empty
		# avoid enabling new button to create more than one soap per issue.
		if self.__selected_episode['pk_episode'] in self.__managed_episodes:
			self.__BTN_new.Enable(False)
		else:
			self.__BTN_new.Enable(True)

		# disabled save button when soap was dumped to backend
		if not isinstance(self.__selected_soap, SOAPMultiSash.EmptyWidget) and self.__selected_soap.IsSaved():
			self.__BTN_remove.Enable(True)
	#--------------------------------------------------------	
	def __allow_perform_action(self, action_id):
		"""
		Check if a concrte action can be performed for selected SOAP input widget

		@param action_id: ui widget wich fired the action
		"""
		if action_id == self.__BTN_new.GetId():
			if self.__selected_episode is None:
				wx.wxMessageBox("There is not any problem selected.\nA problem must be selected to create a new SOAP note.",
					caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
					parent = self)
				return False

		if action_id != self.__BTN_new.GetId():
			if (self.__focussed_soap_editor is None) or (len(self.__managed_episodes) == 0):
				# FIXME: gui helpers
				wx.wxMessageBox("There is not any SOAP note selected.\nA SOAP note must be selected as target of desired action.",
					caption = "SOAP warning", style = wx.wxOK | wx.wxICON_EXCLAMATION,
					parent = self)
				return False
		return True
		
	#--------------------------------------------------------
	def __get_problem(self, emr_struct_element):
		"""
		Retrieve the problem in the list that corresponds with a
		issue or episode selected via dialog.
		"""
		result_problem = None
		
		if isinstance(emr_struct_element, gmEMRStructItems.cHealthIssue):
			for problem in self.__emr.get_problems():
				if problem['pk_health_issue'] == emr_struct_element['id']:
					result_problem = problem
		else:
			for problem in self.__emr.get_problems():
				if problem['pk_episode'] == emr_struct_element['pk_episode']:
					result_problem = problem			
				
		return result_problem
		
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		wx.EVT_LISTBOX_DCLICK(self.__LST_problems, self.__LST_problems.GetId(), self.__on_problem_selected)
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

		when the user selects a problem in the problem list:
			- check whether selection is issue or episode
			- if issue: create episode
			- if editor for episode exists: focus it
			- if no editor for episode exists: create one and focus it
			- update button status
		"""
		problem_idx = self.__LST_problems.GetSelection()
		problem = self.__LST_problems.GetClientData(problem_idx)

		# FIXME: constant in gmEMRStructIssues 
		if problem['type'] == 'issue':
			# health issue selected, show episode selector dialog
			pk_issue = problem['pk_health_issue']
			episode_selector = gmEMRStructWidgets.cEpisodeSelectorDlg(None, -1,
			'Episode selector', _('Add episode and start progress note'),
			pk_health_issue = pk_issue)
			retval = episode_selector.ShowModal() # Shows it
				
			if retval == gmEMRStructWidgets.dialog_OK:
				# FIXME refresh only if episode selector action button was performed
				self.__refresh_problem_list()
				self.__selected_episode = self.__get_problem(episode_selector.get_selected_episode())
				print 'Creating progress note for episode: %s' % self.__selected_episode
			elif retval == gmEMRStructWidgets.dialog_CANCELLED:
				print 'User canceled'
				return False
			else:
				raise Exception('Invalid dialog return code [%s]' % retval)
			episode_selector.Destroy() # finally destroy it when finished.	
		elif problem['type'] == 'episode':
			self.__selected_episode = problem
		else:
			msg = _('Cannot open progress note editor for problem:\n%s') % problem
			gmGuiHelpers.gm_show_error(msg, _('progress note editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid problem type [%s]' % type(problem))
			return False

		episode_id = self.__selected_episode['pk_episode']
		if episode_id not in self.__managed_episodes:
			# create
			self.__focussed_soap_editor.AddLeaf(SOAPMultiSash.MV_VER, 130)
			self.__managed_episodes.append(episode_id)
		else:
			# FIXME: find and focus
			pass

		#if not self.__BTN_new.IsEnabled():
		#	self.__BTN_new.Enable(True)

		self.__update_button_state()
				
	#--------------------------------------------------------	
	def __on_patient_selected(self):
		self._schedule_data_reget()
		
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
		self.__update_button_state()
		print "Done!"
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		Clear currently selected SOAP input widget
		"""
		# security check
		if not self.__allow_perform_action(self.__BTN_clear.GetId()):
			return

		self.__selected_soap.Clear()

	#--------------------------------------------------------
	def __on_new(self, evt):
		"""
		Create and display a new SOAP input widget on the stack
		"""
		pass
		# security check
		#if not self.__allow_perform_action(self.__BTN_new.GetId()):
		#	return

		#print "New SOAP"
		
		#if isinstance(self.__selected_soap, SOAPMultiSash.EmptyWidget):
		#	self.__managed_episodes.append(self.__selected_episode[1]['pk_episode'])
		#	self.__focussed_soap_editor.MakeSoapEditor()
		# first SOAP input widget is displayed by showing an empty hidden one
		#if not self.__selected_soap is None and not self.__selected_soap.IsContentShown():
#		#	self.__managed_episodes.append(self.__selected_episode[1])
#		#	self.__selected_soap.SetHealthIssue(self.__selected_episode)
		#	self.__focussed_soap_editor.GetSOAPPanel().Show()
		#	self.__focussed_soap_editor.detail.Select()
		#	self.__focussed_soap_editor.creatorHor.Show(True)
		#	self.__focussed_soap_editor.closer.Show(True)
			
		#else:
			# create SOAP input widget for currently selected issue
			# FIXME: programmatically calculate height
		#	self.__focussed_soap_editor.AddLeaf(SOAPMultiSash.MV_VER, 130)

		#print "problems with soap: %s"%(self.__managed_episodes)
		
		
	#--------------------------------------------------------
	def __on_remove(self, event):
		"""
		Removes currently selected SOAP input widget
		"""

		# security check
		if not self.__allow_perform_action(self.__BTN_remove.GetId()):
			return
			
		print "Remove SOAP"		
		self.__focussed_soap_editor.DestroyLeaf()

		print "problems with soap: %s"%(self.__managed_episodes)
		# there's no leaf selected after deletion, so disable all buttons
		self.__BTN_save.Disable()
		self.__BTN_clear.Disable()
		self.__BTN_remove.Disable()
		# enable new button is soap stack is empty
		#selected_leaf = self.__soap_multisash.GetSelectedLeaf()
		#if self.__selected_soap.GetHealthIssue() is None:
		#	self.__BTN_new.Enable(True)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		#self.reset_ui_content()
		if self.__refresh_problem_list():
			return True
		return False
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_managed_episodes(self):
		"""
		Retrieve health problems for wich a SOAP note is created
		"""
		return self.__managed_episodes
	#--------------------------------------------------------
	def get_selected_episode(self):
		"""
		Retrieves selected episode in list
		"""
		return self.__selected_episode
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
		self.__focussed_soap_editor = selected_leaf
		self.__selected_soap = selected_soap
		print "\nSelected leaf: %s"%(self.__focussed_soap_editor)
		print "Selected SOAP: %s"%(self.__selected_soap)
		self.__update_button_state()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__selected_episode = None
		self.__managed_episodes = []
		self.__LST_problems.Clear()
		self.__soap_multisash.Clear()

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

	import sys
	from Gnumed.pycommon import gmCfg, gmPG

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
#============================================================
# $Log: gmSoapPlugins.py,v $
# Revision 1.9  2005-01-29 18:04:58  ncq
# - cleanup/added "$ Log" CVS keyword
#
#
