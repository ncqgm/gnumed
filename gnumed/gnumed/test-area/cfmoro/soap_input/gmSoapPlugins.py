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
__version__ = "$Revision: 1.21 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmSignals, gmWhoAmI
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmSOAPWidgets, gmEMRStructWidgets
from Gnumed.pycommon.gmPyCompat import *

import multisash

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
		print "creating", self.__class__.__name__
		wx.wxPanel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize,
			style = wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		pat = gmPerson.gmCurrentPatient()
		self.__emr = pat.get_clinical_record()
		self.__selected_episode = None

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
		self.__soap_multisash = multisash.cMultiSash(PNL_soap_editors, -1)				
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

		# FIXME comment out that button for now until we fully
		# understand how we want it to work.
		#self.__BTN_new = wx.wxButton(PNL_soap_editors, -1, _('&New'))
		#self.__BTN_new.Disable()
		#self.__BTN_new.SetToolTipString(_('create empty progress note for new problem'))

		# - arrange widgets
		szr_btns_left = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns_left.Add(self.__BTN_save, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_clear, 0, wx.wxSHAPED)
		#szr_btns_left.Add(self.__BTN_new, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_remove, 0, wx.wxSHAPED)
		szr_left = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_left.Add(self.__soap_multisash, 1, wx.wxEXPAND)
		szr_left.Add(szr_btns_left)
		PNL_soap_editors.SetSizerAndFit(szr_left)

		# right hand side
		# - problem list
		self.__LST_problems = wx.wxListBox (
			self.__splitter,
			-1,
			style= wx.wxNO_BORDER
		)

		# arrange widgets
		self.__splitter.SetMinimumPaneSize(20)
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
		for problem in problems:
			item = '%s (%s)' % (problem['problem'], problem['type'])
			self.__LST_problems.Append(item, problem)
		splitter_width = self.__splitter.GetSizeTuple()[0]
		self.__splitter.SetSashPosition((splitter_width / 2), True)
		return True
		
	#--------------------------------------------------------
	def __update_button_state(self):
		"""
		Check and configure adecuate buttons enabling state
		"""						
		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
		# if soap stack is empty, disable save, clear and remove buttons		
		if isinstance(selected_soap, multisash.cEmptyChild) or selected_soap.IsSaved():
			self.__BTN_save.Enable(False)
			self.__BTN_clear.Enable(False)
			self.__BTN_remove.Enable(False)
		else:
			self.__BTN_save.Enable(True)
			self.__BTN_clear.Enable(True)
			self.__BTN_remove.Enable(True)

		# disabled save button when soap was dumped to backend
		if isinstance(selected_soap, gmSOAPWidgets.cResizingSoapPanel) and selected_soap.IsSaved():
			self.__BTN_remove.Enable(True)
					
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
	def __make_soap_editor(self):
		"""
		Instantiates a new soap editor. The widget itself (cMultiSashedSoapPanel)
		is the temporary parent, as the final one will be the multisash bottom
		leaf (by reparenting).
		"""
		soap_editor = gmSOAPWidgets.cResizingSoapPanel(self, self.__selected_episode)
		return soap_editor
	#--------------------------------------------------------
	def __get_displayed_episodes(self):
		"""
		Retrieves the list of episodes that are currently displayed in the
		multisash widget.
		"""
		in_edition_episodes = []
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, gmSOAPWidgets.cResizingSoapPanel):
				in_edition_episodes.append(content.GetProblem()['pk_episode'])
		return in_edition_episodes

	#--------------------------------------------------------
	def __focus_episode(self, episode_id):
		"""
		Retrieves the list of episodes that are currently displayed in the
		multisash widget.
		"""
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, gmSOAPWidgets.cResizingSoapPanel) and \
			content.GetProblem()['pk_episode'] == episode_id:
				a_leaf.Select()
				return
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
		#wx.EVT_BUTTON(self.__BTN_new, self.__BTN_new.GetId(), self.__on_new)
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
		print self.__class__.__name__, "-> __on_problem_selected()"
		problem_idx = self.__LST_problems.GetSelection()
		problem = self.__LST_problems.GetClientData(problem_idx)
		print "problem", problem

		# FIXME: constant in gmEMRStructIssues 
		if problem['type'] == 'issue':
			print "... is issue"
			# health issue selected, show episode selector dialog
			pk_issue = problem['pk_health_issue']
			episode_selector = gmEMRStructWidgets.cEpisodeSelectorDlg (
				None,
				-1,
				_('Create or select episode'),
				_('Add episode and start progress note'),
				pk_health_issue = pk_issue
			)
			retval = episode_selector.ShowModal()
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
			print "... is episode"
			self.__selected_episode = problem
		else:
			msg = _('Cannot open progress note editor for problem:\n%s') % problem
			gmGuiHelpers.gm_show_error(msg, _('progress note editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid problem type [%s]' % type(problem))
			return False

		episode_id = self.__selected_episode['pk_episode']
		if episode_id not in self.__get_displayed_episodes():
			# create new leaf always on bottom
			successful, errno = self.__soap_multisash.add_content(content = self.__make_soap_editor())
			# FIXME: actually, one would have to check errno but there is only one error number so far
			if not successful:
				msg = _('Cannot open progress note editor for\n\n'
						'[%s]\n\n'
						'The GnuMed window is too small. Please enlarge\n'
						'the lowermost editor and try again.') % problem['problem']
				gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		else:
			self.__focus_episode(episode_id)
			# FIXME: find and focus
#			msg = _(
#				'There already is a progress note editor open for\n'
#				'[%s]\n\n'
#				'We are lacking code to focus that editor yet.'
#			) % problem['problem']
#			gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		self.__update_button_state()
	#--------------------------------------------------------	
	def __on_patient_selected(self):
		self._schedule_data_reget()
		
	#--------------------------------------------------------
	def __on_save(self, event):
		"""
		Obtain SOAP data from selected editor and dump to backend
		"""

		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
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
		for input_key in selected_soap.GetSOAP().GetValue().keys():
			bundle.append (
			{
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY:input_key,
				gmSOAPimporter.soap_bundle_TYPES_KEY:['Hx'],
				gmSOAPimporter.soap_bundle_TEXT_KEY:selected_soap.GetSOAP().GetValue()[input_key],
				gmSOAPimporter.soap_bundle_CLIN_CTX_KEY:clin_ctx,
				gmSOAPimporter.soap_bundle_STRUCT_DATA_KEY:{}
			}
			)

		# let's dump soap contents		   
		print 'Saving: %s' % bundle
		importer = gmSOAPimporter.cSOAPImporter()
		importer.import_soap(bundle)		
				
		# update buttons
		selected_soap.SetSaved(True)
		self.__update_button_state()
		
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		Clear currently selected SOAP input widget
		"""
			
		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
		selected_soap.Clear()

	#--------------------------------------------------------
	def __on_new(self, evt):
		"""
		Create and display a new SOAP input widget on the stack
		"""
		pass

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

		print "remove SOAP input widget"
		selected_leaf = self.__soap_multisash.get_focussed_leaf()
		selected_leaf.DestroyLeaf()

		#print "problems with soap: %s" % (self.__managed_episodes)
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
	def activate_selected_problem(self):
		"""
		Activate the currently selected problem, simulating double clicking
		over the problem in the list and therefore, firing the actions
		to create a new soap for the problem.
		"""
		self.__on_problem_selected(None)
		
	#--------------------------------------------------------
	def get_selected_episode(self):
		"""
		Retrieves selected episode in list
		"""
		return self.__selected_episode

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__selected_episode = None
		#self.__managed_episodes = []
		self.__LST_problems.Clear()
		self.__soap_multisash.Clear()
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
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# display standalone browser
		application = wx.wxPyWidgetTester(size=(600,400))
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
# Revision 1.21  2005-02-22 18:22:31  ncq
# - cleanup
#
# Revision 1.20  2005/02/21 23:44:59  cfmoro
# Commented out New button. Focus editor when trying to add and existing one. Clean ups
#
# Revision 1.19  2005/02/21 11:52:37  cfmoro
# Ported action of buttons to recent changes. Begin made them functional
#
# Revision 1.18  2005/02/21 10:20:46  cfmoro
# Class renaming
#
# Revision 1.17  2005/02/17 16:46:20  cfmoro
# Adding and removing soap editors. Simplified multisash interface.
#
# Revision 1.16  2005/02/16 11:19:12  ncq
# - better error handling
# - tabified
# - get_bottom_leaf() verified
#
# Revision 1.15  2005/02/14 00:58:37  cfmoro
# Restarted the adaptation of multisash widget to make it completely usable for GnuMed while keeping it generic and not SOAP dependent. Advance step by step. Step 1: Disabled leaf creators, create new widgets on bottom and keep consistency while deleting leafs
#
# Revision 1.14  2005/02/09 20:19:58  cfmoro
# Making soap editor made factory function outside SOAPMultiSash
#
# Revision 1.13  2005/02/08 11:36:11  ncq
# - lessen reliance on implicit callbacks
# - make things more explicit, eg Pythonic
#
# Revision 1.12  2005/02/02 21:43:13  cfmoro
# Adapted to recent gmEMRStructWidgets changes. Multiple editors can be created
#
# Revision 1.11  2005/01/31 13:06:02  ncq
# - use gmPerson.ask_for_patient()
#
# Revision 1.10  2005/01/31 09:50:59  ncq
# - gmPatient -> gmPerson
#
# Revision 1.9  2005/01/29 18:04:58  ncq
# - cleanup/added "$ Log" CVS keyword
#
#
