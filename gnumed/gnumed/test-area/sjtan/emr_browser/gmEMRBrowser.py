"""GNUmed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/sjtan/emr_browser/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.6 2008-11-21 13:07:19 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmHealthIssue, gmPerson, gmPersonSearch
from Gnumed.wxpython import gmRegetMixin
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cEMRBrowserPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id):
		"""
		Constructs a new instance of EMR browser panel

		parent - Wx parent widget
		id - Wx widget id
		"""
		# Call parents constructors
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)

		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()
		
		self.__init_popup()

	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Arranges EMR browser layout
		"""
		# splitter window
		self.__tree_narr_splitter = wx.wxSplitterWindow(self, -1)
		# emr tree
		self.__emr_tree = wx.wxTreeCtrl (
			self.__tree_narr_splitter,
			-1,
			style=wx.wxTR_HAS_BUTTONS | wx.wxNO_BORDER
		)
		# narrative details text control
		self.__narr_TextCtrl = wx.wxTextCtrl (
			self.__tree_narr_splitter,
			-1,
			style=wx.wxTE_MULTILINE | wx.wxTE_READONLY | wx.wxTE_DONTWRAP
		)
		# set up splitter
		# FIXME: read/save value from/into backend
		self.__tree_narr_splitter.SetMinimumPaneSize(20)
		self.__tree_narr_splitter.SplitVertically(self.__emr_tree, self.__narr_TextCtrl)

		self.__szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__szr_main.Add(self.__tree_narr_splitter, 1, wx.wxEXPAND, 0)

		self.SetAutoLayout(1)
		self.SetSizer(self.__szr_main)
		self.__szr_main.Fit(self)
		self.__szr_main.SetSizeHints(self)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configures enabled event signals
		"""
		# wx.wxPython events
		wx.EVT_TREE_SEL_CHANGED(self.__emr_tree, self.__emr_tree.GetId(), self._on_tree_item_selected)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
	#--------------------------------------------------------
	def _on_patient_selected(self):
		"""Patient changed."""
		self.__exporter.set_patient(self.__pat)
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		"""
		Displays information for a selected tree node
		"""
		sel_item = event.GetItem()
		sel_item_obj = self.__emr_tree.GetPyData(sel_item)
	
		if(isinstance(sel_item_obj, gmEncounter.cEncounter)):
			header = _('Encounter\n=========\n\n')
			epi = self.__emr_tree.GetPyData(self.__emr_tree.GetItemParent(sel_item))
			txt = self.__exporter.dump_encounter_info(episode=epi, encounter=sel_item_obj)

		elif (isinstance(sel_item_obj, gmEpisode.cEpisode)):
			header = _('Episode\n=======\n\n')
			txt = self.__exporter.dump_episode_info(episode=sel_item_obj)

		elif (isinstance(sel_item_obj, gmHealthIssue.cHealthIssue)):
			header = _('Health Issue\n============\n\n')
			txt = self.__exporter.dump_issue_info(issue=sel_item_obj)

		else:
			header = _('Summary\n=======\n\n')
			txt = self.__exporter.dump_summary_info()

		self.__narr_TextCtrl.Clear()
		self.__narr_TextCtrl.WriteText(header)
		self.__narr_TextCtrl.WriteText(txt)
		
			
		self.popup.SetPopupContext(sel_item)
		 
		
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		self.__reset_ui_content()
		if self.refresh_tree():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
	def refresh_tree(self):
		"""
		Updates EMR browser data
		"""
		# EMR tree root item
		identity = self.__pat.get_identity()
		name = identity.get_active_name()
		if name is None:
			root_item = self.__emr_tree.AddRoot(_('EMR tree'))
		else:
			root_item = self.__emr_tree.AddRoot(_('%s %s EMR') % (name['firstnames'], name['lastnames']))

		# Obtain all the tree from exporter
		self.__exporter.get_historical_tree(self.__emr_tree)

		# Expand root node and display patient summary info
		self.__emr_tree.Expand(root_item)
		self.__narr_TextCtrl.WriteText(_('Summary\n=======\n\n'))
		self.__narr_TextCtrl.WriteText(self.__exporter.dump_summary_info(0))

		# Set sash position
		self.__tree_narr_splitter.SetSashPosition(self.__tree_narr_splitter.GetSizeTuple()[0]/3, True)

		# FIXME: error handling
		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""
		Clear all information displayed in browser (tree and details area)
		"""
		self.__emr_tree.DeleteAllItems()
		self.__narr_TextCtrl.Clear()
	#--------------------------------------------------------
#	def set_patient(self, patient):
#		"""
#		Configures EMR browser patient and instantiates exporter.
#		Appropriate for standalaone use.
#		patient - The patient to display EMR for
#		"""
#		self.__patient = patient
#		self.__exporter.set_patient(patient)

	def get_emr_tree(self):
		return self.__emr_tree	

	def get_EMR_item(self, selected_tree_item):
		return self.__emr_tree.GetPyData(selected_tree_item)
		
	def get_parent_EMR_item(self, selected_tree_item):
		return 	self.__emr_tree.GetPyData(self.__emr_tree.GetItemParent(selected_tree_item))
		
	def repopulate(self):
		self._populate_with_data()	

#------------POPUP methods -------------------------------
	def __init_popup(self):
		"""
		initializes the popup for the tree
		"""
		self.popup=gmPopupMenuEMRBrowser(self)
		wx.EVT_RIGHT_DOWN(self.__emr_tree, self.__show_popup)
	 

		
	def __show_popup(self, event):
		 self.PopupMenu(self.popup, (event.GetX(), event.GetY() ))

#== Module convenience functions (for standalone use) =======================

import Queue

class gmPopupMenuEMRBrowser(wx.wxMenu):
	"""
	popup menu for updating the EMR tree.
	"""
	def __init__(self , browser):
		wx.wxMenu.__init__(self)
		self.ID_NEW_ENCOUNTER=1	
		self.ID_NEW_HEALTH_ISSUE=2
		self.ID_NEW_EPISODE=3
		self.__browser = browser
		self.__mediator = NarrativeTreeItemMediator1(browser)
		wx.EVT_MENU(self.__browser, self.ID_NEW_HEALTH_ISSUE , self.__mediator.new_health_issue)
		wx.EVT_MENU(self.__browser, self.ID_NEW_EPISODE , self.__mediator.new_episode)
		
	def Clear(self):
		for item in self.GetMenuItems():
			self.Remove(item.GetId())
				
	def SetPopupContext( self, sel_item):
	
		self.Clear()
		
		sel_item_obj = self.__browser.get_EMR_item(sel_item)
		
		if(isinstance(sel_item_obj, gmEncounter.cEncounter)):
			header = _('Encounter\n=========\n\n')
			
			self.__append_new_encounter_menuitem(episode=self.__browser.get_parent_EMR_item(sel_item) )
			
			
		elif (isinstance(sel_item_obj, gmEpisode.cEpisode)):
			header = _('Episode\n=======\n\n')
			
			self.__append_new_encounter_menuitem(episode=self.__browser.get_EMR_item(sel_item) )
			
			self.__append_new_episode_menuitem(health_issue=self.__browser.get_parent_EMR_item(sel_item))
			
			
		elif (isinstance(sel_item_obj, gmHealthIssue.cHealthIssue)):
			header = _('Health Issue\n============\n\n')
			
			self.__append_new_episode_menuitem(health_issue=self.__browser.get_EMR_item(sel_item))
			
			self.Append(self.ID_NEW_HEALTH_ISSUE, "New Health Issue")
			

		else:
			header = _('Summary\n=======\n\n')
			self.Append(self.ID_NEW_HEALTH_ISSUE, "New Health Issue")
			

	def __append_new_encounter_menuitem(self, episode):
		self.Append(self.ID_NEW_ENCOUNTER, "New Encounter (of episode '%s')" % episode['description'] )
		
	def __append_new_episode_menuitem(self, health_issue):
		self.Append(self.ID_NEW_EPISODE, "New Episode(of health issue '%s')" % health_issue['description'] )

	
		
class NarrativeTreeItemMediator1:
	"""
	handler for popup menu actions.
	Handles the unchanged new item problem , where no tree events are fired, by listening
	on the edit control events.
	"""
	def __init__(self, browser):
		self.q, self.q_edit  = Queue.Queue(), Queue.Queue()
		self.__browser = browser
		wx.EVT_TREE_END_LABEL_EDIT(self.get_emr_tree(), self.get_emr_tree().GetId(), self.__end_label_edit)
		
		self.HEALTH_ISSUE_START_LABEL="NEW HEALTH ISSUE"
		self.EPISODE_START_LABEL="NEW EPISODE"
		
	def get_browser(self):
		return self.__browser
	
		
	def get_emr_tree(self):
		return self.__browser.get_emr_tree()	
		
	def new_health_issue(self, menu_event):
		"""
		entry from MenuItem New Health Issue
		"""
		self.start_edit_root_node( self.HEALTH_ISSUE_START_LABEL)
	
	def new_episode(self, menu_event):
		"""
		entry from MenuItem New Episode Issue
		"""
		self.start_edit_child_node( self.EPISODE_START_LABEL)	
		
	def start_edit_child_node(self, start_edit_text):
		root_node = self.get_emr_tree().GetSelection()
		if start_edit_text == self.EPISODE_START_LABEL and \
		isinstance(self.get_browser().get_EMR_item(root_node), gmEpisode.cEpisode):
			root_node = self.get_emr_tree().GetItemParent(root_node)

		self.q_edit.put( (root_node, start_edit_text) )
		wx.wxCallAfter( self.start_edit_node)# , root_node, start_edit_text)
		
	def start_edit_root_node(self, start_edit_text ):
		"""
		this handles the problem of no event fired if label unchanged.
		By detecting for the return key on the edit control, the start text 
		can be compared, and if no change, the node is deleted
		in the __key_down handler
		"""
		root_node = self.get_emr_tree().GetRootItem()

		self.q_edit.put( (root_node, start_edit_text) )
		wx.wxCallAfter(self.start_edit_node)#, root_node, start_edit_text)
	
	def __get_edit_node_parameters(self):
		node = None		
		while True:
			try:
				print "removed edit request"
				old_node = node
				(node, start_edit_text) = self.q_edit.get_nowait()	

				if not old_node is None:
					print "request on old root_node discarded : ", old_node, start_edit_text

			except Queue.Empty:
				break
		return node, start_edit_text	
			
	def start_edit_node(self ):# , node, start_edit_text):
		node, start_edit_text = self.__get_edit_node_parameters()
		if not node is None:	
			root_node = node
			node= self.get_emr_tree().AppendItem(root_node, start_edit_text)
			self.get_emr_tree().EnsureVisible(node)
			self.get_emr_tree().EditLabel(node)
			self.edit_control = self.get_emr_tree().GetEditControl()
			print self.edit_control
			self.start_edit_text = start_edit_text
			self.edit_node = node	
			# this is needed to catch the enter key being pressed, and no change is made to the label
			wx.EVT_KEY_DOWN( self.edit_control,  self.__key_down)
			# this is needed to catch when the mouse is clicked off the label editor, and editing ceases, and there
			# is no change to the label
			wx.EVT_KILL_FOCUS(self.edit_control, self.__kill_focus)
		else:
			print "No node was found"
		
	def __end_label_edit(self, tree_event):
		"""
		check to see if editing cancelled , and if not, then do update for each kind of label
		"""
		print "end label edit Handled" 
		print "tree_event is ", tree_event
		print "after ", tree_event.__dict__
		print "label is ", tree_event.GetLabel()
		 
			
		if tree_event.IsEditCancelled() or len(tree_event.GetLabel().strip()) == 0:
			tree_event.Skip()
			#self.__item_to_delete = tree_event.GetItem()
			self.q.put(tree_event.GetItem())
			wx.wxCallAfter(self.__delete_item)
		else:
			if self.start_edit_text == self.HEALTH_ISSUE_START_LABEL:
				wx.wxCallAfter(self.__add_new_health_issue_to_record)
			
			elif self.start_edit_text == self.EPISODE_START_LABEL:
				wx.wxCallAfter(self.__add_new_episode_to_record)	
			
	def __key_down(self, event):
		"""
		this event on the EditControl needs to be handled because
		1) pressing enter whilst no change in label , does not fire any END_LABEL event, so tentative 
		tree items cannot be deleted.
		
		 .
		"""
		print "Item is ", event.GetKeyCode()
		event.Skip()
		
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.__check_for_unchanged_item()
			
	
				
	def __kill_focus(self, event):
		print "kill focuse"
		
		self.__check_for_unchanged_item()
		event.Skip()
	
	def __check_for_unchanged_item(self):	
			text = self.edit_control.GetValue().strip() 
			print "Text was ", text
			print "Text unchanged ", text == self.start_edit_text
			
			#if the text is unchanged, then delete the new node.
			if self.edit_node and text == self.start_edit_text:
				self.q.put( self.edit_node )
				self.edit_node =None
				wx.wxCallAfter(self.__delete_item)
		
	def __delete_item(self):
			while not self.q.empty():
				try:
					item = self.q.get_nowait()
					self.get_emr_tree().Delete(item)
				except Queue.Empty:
					break
					
	def __add_new_health_issue_to_record(self):
		print "add new health issue to record"
		pat = gmPerson.gmCurrentPatient()
		rec = pat.get_clinical_record()
		issue = rec.add_health_issue( self.get_emr_tree().GetItemText(self.edit_node).strip() )
		if not issue is None and isinstance(issue, gmHealthIssue.cHealthIssue):
			self.get_emr_tree().SetPyData( self.edit_node, issue)
			
		 
		
	def __add_new_episode_to_record(self):
		print "add new episode to record"
		pat = gmPerson.gmCurrentPatient()
		rec = pat.get_clinical_record()
		print "health_issue pk = ", self.get_browser().get_parent_EMR_item(self.edit_node).pk_obj
		print "text = ", self.get_emr_tree().GetItemText(self.edit_node).strip()
		
		episode = rec.add_episode( self.get_emr_tree().GetItemText(self.edit_node).strip(), self.get_browser().get_parent_EMR_item(self.edit_node).pk_obj )
		 
		if not episode is None and isinstance(episode, gmEpisode.cEpisode):
			self.get_emr_tree().SetPyData( self.edit_node, episode)	
		
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmCfg

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting emr browser...")

	_cfg = gmCfg.gmDefCfgFile	 
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# make sure we have a db connection
		pool = gmPG.ConnectionPool()

		# obtain patient
		patient = gmPersonSearch.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# display standalone browser
		application = wx.wxPyWidgetTester(size=(800,600))
		emr_browser = cEMRBrowserPanel(application.frame, -1)
#		emr_browser.set_patient(patient)		
		emr_browser.refresh_tree()

		application.frame.Show(True)
		application.MainLoop()

		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except Exception:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	try:
		pool.StopListeners()
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
		raise

	_log.Log (gmLog.lInfo, "closing emr browser...")

#================================================================
