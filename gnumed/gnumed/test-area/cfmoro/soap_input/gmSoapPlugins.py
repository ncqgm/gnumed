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
__version__ = "$Revision: 1.29 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std
import types

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

		self.__pat = gmPerson.gmCurrentPatient()
		self.__selected_episode = None

		# ui contruction and event handling set up
		self.__do_layout()
		self.__register_interests()
		self._populate_with_data()

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
		
		self.__BTN_add_unassociated = wx.wxButton(PNL_soap_editors, -1, _('&Unassociated new progress note'))
		self.__BTN_add_unassociated.SetToolTipString(_('create a progress note that is not at first associated with any episode'))

		# FIXME comment out that button for now until we fully
		# understand how we want it to work.
		#self.__BTN_new = wx.wxButton(PNL_soap_editors, -1, _('&New'))
		#self.__BTN_new.Disable()
		#self.__BTN_new.SetToolTipString(_('create empty progress note for new problem'))

		# - arrange widgets
		szr_btns_left = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns_left.Add(self.__BTN_save, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_clear, 0, wx.wxSHAPED)		
		szr_btns_left.Add(self.__BTN_remove, 0, wx.wxSHAPED)
		szr_btns_left.Add(self.__BTN_add_unassociated, 0, wx.wxSHAPED)
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
		emr = self.__pat.get_clinical_record()
		problems = emr.get_problems()
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
	#def __get_problem_by_struct_element_REMOVE(self, emr_struct_element):
	#	"""
	#	Retrieve the problem in the list that corresponds with a
	#	issue, episode (both typically selected via dialog) or
	#	problem name (typically in an unassociated note).
	#	"""
	#	result_problem = None
	#
	#	emr = self.__pat.get_clinical_record()
	#
	#	if isinstance(emr_struct_element, gmEMRStructItems.cHealthIssue):
	#		for problem in emr.get_problems():
	#			if problem['pk_health_issue'] == emr_struct_element['id']:
	#				result_problem = problem
	#	elif isinstance(emr_struct_element, gmEMRStructItems.cEpisode):
	#		for problem in emr.get_problems():
	#			if problem['pk_episode'] == emr_struct_element['pk_episode']:
	#				result_problem = problem
	#	elif isinstance(emr_struct_element, types.StringType):
	#		for problem in emr.get_problems():
	#			if problem['problem'] == emr_struct_element:
	#				result_problem = problem					
	#	return result_problem

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
		displayed_episodes = []
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, gmSOAPWidgets.cResizingSoapPanel):
				if content.GetEpisode() == gmSOAPWidgets.NOTE_SAVED:
					displayed_episodes.append(gmSOAPWidgets.NOTE_SAVED)
				elif content.GetEpisode() is not None:
					displayed_episodes.append(content.GetEpisode()['description'])
				elif content.GetEpisode() is None:
					displayed_episodes.append(content.GetHeadingTxt())
		return displayed_episodes
		
	#--------------------------------------------------------
	def __get_leaf_for_episode(self, episode):
		"""
		Retrieves the displayed leaf for the given episode (or the first
		is they are multiple, eg. after saving various soap notes).
		@param episode The episode to retrieve the displayed note for.
		@type episode gmEMRStructItems.cEpisode
		"""
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:
			content = a_leaf.get_content()
			if isinstance(content, gmSOAPWidgets.cResizingSoapPanel) \
			and content.GetEpisode() == episode:
				return a_leaf
		return None
	#--------------------------------------------------------
	def __focus_episode(self, episode_name):
		"""
		Focus in multisash widget the progress note for the given
		episode name.
		
		@param episode_name: The name of the episode to focus
		@type episode_name: string
		"""
		all_leafs = self.__soap_multisash.get_displayed_leafs()
		for a_leaf in all_leafs:			
			content = a_leaf.get_content()
			target_name = ''
			
			if content is not None \
				and isinstance(content, gmSOAPWidgets.cResizingSoapPanel) \
				and content.GetEpisode() != gmSOAPWidgets.NOTE_SAVED \
				and content.GetEpisode() is not None:
					target_name = content.GetEpisode()['description']
			elif content.GetEpisode() is None:
				target_name = content.GetHeadingTxt()

			if target_name == episode_name:
				a_leaf.Select()
				return
	#--------------------------------------------------------
#	def __check_problem(self, problem_name):
#		"""
#		Check whether the supplied problem (usually, from an unassociated
#		progress note, is an existing episode or we must create a new
#		episode (unattached to any problem).
#
#		@param problem_name: The progress note's problem name to check
#		@type problem: StringType
#		"""
#		emr = self.__pat.get_clinical_record()
#		target_episode = self.__get_problem_by_struct_element(problem_name)
#		if not target_episode is None and isinstance(target_episode, gmEMRStructItems.cEpisode):
#			# the text is not an existing episode, let's create it
#			target_episode = emr.add_episode (episode_name = problem_name)
#		if not target_episode is None:
#			return (True, target_episode)
#		else:
#			return (False, target_episode)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		wx.EVT_LISTBOX_DCLICK(self.__LST_problems, self.__LST_problems.GetId(), self.__on_problem_activated)
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self.__on_save)
		wx.EVT_BUTTON(self.__BTN_clear, self.__BTN_clear.GetId(), self.__on_clear)		
		wx.EVT_BUTTON(self.__BTN_remove, self.__BTN_remove.GetId(), self.__on_remove)
		wx.EVT_BUTTON(self.__BTN_add_unassociated, self.__BTN_add_unassociated.GetId(), self.__on_add_unassociated)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self.__on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self.__on_episodes_modified)
	#--------------------------------------------------------
	def __on_problem_activated(self, event):
		"""
		When the user changes health issue selection, update selected issue
		reference and update buttons according its input status.

		when the user selects a problem in the problem list:
			- check whether selection is issue or episode
			- if issue: create episode
			- if editor for episode exists: focus it
			- if no editor for episode exists: create one and focus it
			- update button status
			- if currently selected editor is an unassociated one and its episode name is empty,
			  set its episode name in phrasewheel
		"""
		print self.__class__.__name__, "-> __on_problem_activated()"
		problem_idx = self.__LST_problems.GetSelection()
		problem = self.__LST_problems.GetClientData(problem_idx)		

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
				print "would be refreshing problem list now"
#				self.__refresh_problem_list()
				self.__selected_episode = episode_selector.get_selected_episode()
				print 'Creating progress note for episode: %s' % self.__selected_episode
			elif retval == gmEMRStructWidgets.dialog_CANCELLED:
				print 'User canceled'
				return False
			else:
				raise Exception('Invalid dialog return code [%s]' % retval)
			episode_selector.Destroy() # finally destroy it when finished.
		elif problem['type'] == 'episode':
			print "... is episode"
			self.__selected_episode = self.__pat.get_clinical_record().get_episodes(id_list=[problem['pk_episode']])[0]
		else:
			msg = _('Cannot open progress note editor for problem:\n%s') % problem
			gmGuiHelpers.gm_show_error(msg, _('progress note editor'), gmLog.lErr)
			_log.Log(gmLog.lErr, 'invalid problem type [%s]' % type(problem))
			return False
				
		episode_name = self.__selected_episode['description']
		if episode_name not in self.__get_displayed_episodes():
			focused_widget = self.__soap_multisash.get_focussed_leaf().get_content()
			if isinstance(focused_widget, gmSOAPWidgets.cResizingSoapPanel) and (focused_widget.GetEpisode() is None or focused_widget.GetEpisode() == gmSOAPWidgets.NOTE_SAVED) and focused_widget.GetHeadingTxt().strip() == '':
				# configure episode name in unassociated progress note
				focused_widget = self.__soap_multisash.get_focussed_leaf().get_content()		
				focused_widget.SetHeadingTxt(self.__selected_episode['description'])
				return
			# let's create new note for the selected episode
			if gmSOAPWidgets.NOTE_SAVED in self.__get_displayed_episodes():
				# there are some displayed empty notes (after saving)
				# set the selected problem in first of them
				leaf = self.__get_leaf_for_episode(episode = gmSOAPWidgets.NOTE_SAVED)
				leaf.get_content().SetEpisode(self.__selected_episode)
			else:
				# create note in new leaf, always on bottom
				successful, errno = self.__soap_multisash.add_content(content = self.__make_soap_editor())
				# FIXME: actually, one would have to check errno but there is only one error number so far
				if not successful:
					msg = _('Cannot open progress note editor for\n\n'
							'[%s]\n\n'
							'The GnuMed window is too small. Please enlarge\n'
							'the lowermost editor and try again.') % problem['problem']
					gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		else:
			# let's find and focus the displayed note for the selected episode
			self.__focus_episode(episode_name)
		self.__update_button_state()

	#--------------------------------------------------------
	def __on_patient_selected(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def __on_episodes_modified(self):
		print "episodes modified ..."
		self._schedule_data_reget()
	#--------------------------------------------------------
	def __on_save(self, event):
		"""
		Obtain SOAP data from selected editor and dump to backend
		"""
		emr = self.__pat.get_clinical_record()
		focussed_leaf = self.__soap_multisash.get_focussed_leaf()
		soap_widget = focussed_leaf.get_content()
		soap_editor = soap_widget.get_editor()
		episode = soap_widget.GetEpisode()
		# do we need to create a new episode ?
		if episode is None:
			episode_name = soap_widget.GetHeadingTxt()
			if episode_name is None or episode_name.strip() == '':
				msg = _('Need a name for the new episode to save new progress note under.\n'
						'Please type a new episode name or select an existing one from the list.')
				gmGuiHelpers.gm_show_error(msg, _('saving progress note'), gmLog.lErr)
				return False
			emr = self.__pat.get_clinical_record()
			episode = emr.add_episode(episode_name = episode_name)
#			stat, problem = self.__check_problem(episode_name)
#			if not stat:
			if episode is None:
				msg = _('Cannot create episode [%s] to save progress note under.' % episode_name)
				gmGuiHelpers.gm_show_error(msg, _('saving progress note'), gmLog.lErr)
				return False
			print "SAVING UNASSOCIATED note for episode: %s " % episode
		# set up clinical context in soap bundle
		encounter = emr.get_active_encounter()
		staff_id = gmWhoAmI.cWhoAmI().get_staff_ID()
		clin_ctx = {
			gmSOAPimporter.soap_bundle_EPISODE_ID_KEY: episode['pk_episode'],
			gmSOAPimporter.soap_bundle_ENCOUNTER_ID_KEY: encounter['pk_encounter'],
			gmSOAPimporter.soap_bundle_STAFF_ID_KEY: staff_id
		}
		# fill bundle for import
		bundle = []
		editor_content = soap_editor.GetValue()
		print editor_content
#		for input_label in editor_content.keys():
		for input_label in editor_content.values():
			print "Data: %s" % input_label.data
			print "Value: %s" % input_label.value
#			narr = editor_content[input_label].value
#			if isinstance(narr, gmClinNarrative.cNarrative):
#				# double-check staff_id vs. narr['who owns it']
#				print "updating existing narrative"
#				narr['narrative'] = editor_content['text']
#				narr['soap_cat'] = editor_content['soap_cat']
#				successful, data = narr.save_payload()
#				if not successful:
					# FIXME: pop up error dialog etc.
#					print "cannot update narrative"
#					print data
#					continue
				# FIXME: update associated types list
 				# FIXME: handle embedded structural data list
#				continue
			bundle.append ({
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY: input_label.data['soap_cat'],
				gmSOAPimporter.soap_bundle_TYPES_KEY: [],		# these types need to come from the editor
				gmSOAPimporter.soap_bundle_TEXT_KEY: input_label.value,
				gmSOAPimporter.soap_bundle_CLIN_CTX_KEY: clin_ctx,
				gmSOAPimporter.soap_bundle_STRUCT_DATA_KEY: {}	# this data needs to come from the editor
			})

		# let's dump soap contents		   
		print 'Saving: %s' % bundle
		#importer = gmSOAPimporter.cSOAPImporter()
		#importer.import_soap(bundle)
				
		# update buttons
		soap_widget.SetSaved(True)
		self.__update_button_state()
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""
		Clear currently selected SOAP input widget
		"""
			
		selected_soap = self.__soap_multisash.get_focussed_leaf().get_content()
		selected_soap.Clear()

	#--------------------------------------------------------
	def __on_add_unassociated(self, evt):
		"""
		Create and display a new SOAP input widget on the stack for an unassociated
		progress note.
		"""
		successful, errno = self.__soap_multisash.add_content(content = gmSOAPWidgets.cResizingSoapPanel(self))
		# FIXME: actually, one would have to check errno but there is only one error number so far
		if not successful:
			msg = _('Cannot open progress note editor for\n\n'
					'[%s]\n\n'
					'The GnuMed window is too small. Please enlarge\n'
					'the lowermost editor and try again.') % problem['problem']
			gmGuiHelpers.gm_show_info(aMessage = msg, aTitle = _('opening progress note editor'))
		self.__update_button_state()
				
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
	#def activate_selected_problem(self):
	#	"""
	#	Activate the currently selected problem, simulating double clicking
	#	over the problem in the list and therefore, firing the actions
	#	to create a new soap for the problem.
	#	"""
	#	self.__on_problem_activated(None)
	#	
	#--------------------------------------------------------
	#def get_selected_episode(self):
	#	"""
	#	Retrieves selected episode in list
	#	"""
	#	return self.__selected_episode

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
		application = wx.wxPyWidgetTester(size=(800,500))
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
# Revision 1.29  2005-03-14 20:55:25  cfmoro
# Let saved unassociated note be reused on new problem activation. Minot clean ups
#
# Revision 1.28  2005/03/14 18:22:22  cfmoro
# Passing episodes instead of problems to soap editor. Clean ups
#
# Revision 1.27  2005/03/14 14:49:05  ncq
# - ongoing work/cleanup
# - self.__emr is dangerous, use self.__pat.get_clinical_record()
#
# Revision 1.26  2005/03/13 09:04:34  cfmoro
# Added intial support for unassociated progress notes
#
# Revision 1.25  2005/03/03 21:34:23  ncq
# - cleanup
# - start implementing saving existing narratives
#
# Revision 1.24  2005/02/24 20:03:02  cfmoro
# Fixed bug when focusing and any of the content is None
#
# Revision 1.23  2005/02/23 19:41:26  ncq
# - listen to episodes_modified() signal instead of manual refresh
# - cleanup, renaming, pretty close to being moved to main trunk
#
# Revision 1.22  2005/02/23 03:19:02  cfmoro
# Fixed bug while refreshing leafs, using recursivity. On save, clear the editor and reutilize on future notes. Clean ups
#
# Revision 1.21  2005/02/22 18:22:31  ncq
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
