"""GNUmed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.50 2005-12-27 02:52:40 sjtan Exp $
__version__ = "$Revision: 1.50 $"
__author__ = "cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# std lib
import sys, types, os.path, StringIO

# 3rd party
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

# GNUmed libs
from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets, gmEditArea
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# module level constants
dialog_CANCELLED = -1
dialog_OK = -2
MAX_EXPANSION_HISTORY = 2

#============================================================
def export_emr_to_ascii(parent=None):
	"""
	Dump the patient's EMR from GUI client
	@param parent - The parent widget
	@type parent - A wx.Window instance
	"""
	# sanity checks
	pat = gmPerson.gmCurrentPatient()
	if not pat.is_connected():
		gmGuiHelpers.gm_beep_statustext(_('Cannot export EMR. No active patient.'), gmLog.lErr)
		return False
	if parent is None:
		_log.Log(gmLog.lErr, 'cannot dump emr in gui mode without parent widget')
		return False
	# get file name
	aWildcard = "%s (*.txt)|*.txt|%s (*.*)|*.*" % (_("text files"), _("all files"))
	aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed')))
	ident = pat.get_identity()
	fname = '%s-%s_%s.txt' % (_('emr-export'), ident['lastnames'], ident['firstnames'])
	dlg = wx.FileDialog (
		parent = parent,
		message = _("Save patient's EMR as..."),
		defaultDir = aDefDir,
		defaultFile = fname,
		wildcard = aWildcard,
		style = wx.SAVE
	)
	choice = dlg.ShowModal()
	fname = dlg.GetPath()
	dlg.Destroy()
	if choice == wx.ID_OK:
		_log.Log(gmLog.lData, 'exporting EMR to [%s]' % fname)
		output_file = open(fname, 'wb')
		# instantiate exporter
		exporter = gmPatientExporter.cEmrExport(patient = pat)
		exporter.set_output_file(output_file)
		exporter.dump_constraints()
		exporter.dump_demographic_record(True)
		exporter.dump_clinical_record()
		exporter.dump_med_docs()
		output_file.close()
		gmGuiHelpers.gm_show_info('EMR successfully exported to file: %s' % fname, _('emr_dump'), gmLog.lInfo)
#============================================================
class cEMRBrowserPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id=-1):
		"""
		Contructs a new instance of EMR browser panel

		parent - Wx parent widget
		id - Wx widget id
		"""
		# Call parents constructors
		wx.Panel.__init__ (
			self,
			parent,
			id,
			wx.DefaultPosition,
			wx.DefaultSize,
			wx.NO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)
		
		self.__custom_right_widget = None
		self.__selected_node = None

		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()

		self.expansion_history = ExpansionHistory(self, self.__emr_tree)
	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Arranges EMR browser layout
		"""
		
		# splitter window
		self.__tree_narr_splitter = wx.SplitterWindow(self, -1)
		# emr tree
		self.__emr_tree = wx.TreeCtrl (
			self.__tree_narr_splitter,
			-1,
			style=wx.TR_HAS_BUTTONS | wx.NO_BORDER
		)
		
		# narrative details text control
		self.__narr_TextCtrl = wx.TextCtrl (
			self.__tree_narr_splitter,
			-1,
			style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP
		)
		# set up splitter
		# FIXME: read/save value from/into backend
		self.__tree_narr_splitter.SetMinimumPaneSize(20)
		self.__tree_narr_splitter.SplitVertically(self.__emr_tree, self.__narr_TextCtrl)

		self.__szr_main = wx.BoxSizer(wx.VERTICAL)
		self.__szr_main.Add(self.__tree_narr_splitter, 1, wx.EXPAND, 0)

		self.SetAutoLayout(1)
		self.SetSizer(self.__szr_main)
		self.__szr_main.Fit(self)
		self.__szr_main.SetSizeHints(self)

		# make popup menus for later use

		# - episodes
		self.__epi_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('rename episode')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__rename_episode)
#		menu_id = wx.NewId()
#		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('close episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__close_episode)
#		menu_id = wx.NewId()
#		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('delete episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__delete_episode)
#		menu_id = wx.NewId()
#		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('attach episode to another health issue')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode)
#		menu_id = wx.NewId()
#		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('attach all encounters to another episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode_encounters)

		# - encounters
		self.__enc_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('attach encounter to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
#		menu_id = wx.NewId()
#		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('attach encounter to another patient')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter2patient)
#		menu_id = wx.NewId()
#		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('delete encounter')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__delete_encounter)
#		menu_id = wx.NewId()
#		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('attach all progress notes to another encounter')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_notes2encounter)

		# - health issues
		self.__issue_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__issue_context_popup.AppendItem(wx.MenuItem(self.__issue_context_popup, menu_id, _('rename health issue')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__rename_issue)
		
		# - root node
		self.__root_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('create health issue')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__create_issue)
#		print " add new episode to issue"
#		print " attach issue to another patient"
#		print " move all episodes to another issue"
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configures enabled event signals
		"""
		# wx.Python events
		wx.EVT_TREE_SEL_CHANGED(self.__emr_tree, self.__emr_tree.GetId(), self._on_tree_item_selected)
		wx.EVT_TREE_ITEM_RIGHT_CLICK(self.__emr_tree, self.__emr_tree.GetId(), self.__on_tree_item_right_clicked)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self._on_episodes_modified)
		gmDispatcher.connect(signal=gmSignals.clin_item_updated(), receiver = self._on_clin_item_updated)
	#--------------------------------------------------------
	def __on_dump_emr(self, event):
		"""Dump EMR to file."""		   
		self.__exporter.dump_emr_gui(parent = self)
	#--------------------------------------------------------
	def _on_patient_selected(self):
		"""Patient changed."""
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_episodes_modified(self):
		"""Episode changed."""
		#less drastic ui update more usable
		self._schedule_data_reget()
		print "DEBUG ======================SIGNALLED EPISODE_MODIFIED==============="
		#self.__exporter.refresh_historical_tree( self.__emr_tree)

	def _on_clin_item_updated(self):
		#self.__exporter.refresh_historical_tree( self.__emr_tree)
		self._schedule_data_reget()

		
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		"""
		Displays information for a selected tree node
		"""
		# retrieve the selected EMR element
		sel_item = event.GetItem()
		sel_item_obj = self.__emr_tree.GetPyData(sel_item)
		self.__selected_node = sel_item

		self.__display_narrative_on_right_pane()

		# update displayed text
		if isinstance(sel_item_obj, (gmEMRStructItems.cHealthIssue, types.DictType)):
			txt = self.__exporter.get_issue_info(issue=sel_item_obj)

		elif isinstance(sel_item_obj, gmEMRStructItems.cEpisode):
			txt = self.__exporter.get_episode_summary(episode=sel_item_obj)
		elif isinstance(sel_item_obj, gmEMRStructItems.cEncounter):
			epi = self.__emr_tree.GetPyData(self.__emr_tree.GetItemParent(sel_item))
			txt = self.__exporter.get_encounter_info(episode=epi, encounter=sel_item_obj)
		else:
			txt = _('Summary') + '\n=======\n\n' + self.__exporter.get_summary_info(0)

		self.__narr_TextCtrl.Clear()
		self.__narr_TextCtrl.WriteText(txt)
	#--------------------------------------------------------
	def __on_tree_item_right_clicked(self, event):
		"""
		Right button clicked: display the popup for the tree
		"""
		# FIXME: should get the list item at the current position
		# FIXME: should then update the context

		node = event.GetItem()
		node_data = self.__emr_tree.GetPyData(node)

		self.__emr_tree.SelectItem(node)

		# FIXME: get position from tree item
#		pos = (event.GetX(), event.GetY())
		pos = wx.DefaultPosition
		if isinstance(node_data, gmEMRStructItems.cHealthIssue):
			self.__handle_issue_context(issue=node_data, pos=pos)
		elif isinstance(node_data, gmEMRStructItems.cEpisode):
			self.__handle_episode_context(episode=node_data, pos=pos)
		elif isinstance(node_data, gmEMRStructItems.cEncounter):
			self.__handle_encounter_context(encounter=node_data, pos=pos)
		elif node == self.__emr_tree.GetRootItem():
			self.__handle_root_context()
		else:
			print "error: unknown node type, no popup menu"
		event.Skip()
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
		

		self.expansion_history.remember_expansion()
		
		# clear previous contents
		self.__emr_tree.DeleteAllItems()
		
		# FIXME: auto select the previously self.__selected_node if not None

		# EMR tree root item
		ident = self.__pat.get_identity()
		root_item = self.__emr_tree.AddRoot(_('%s EMR') % ident['description'])


		# Obtain all the tree from exporter
		self.__exporter.get_historical_tree(self.__emr_tree)



		# Expand root node and display patient summary info
		self.__emr_tree.Expand(root_item)
		label = _('Summary')
		underline = '=' * len(label)
		self.__narr_TextCtrl.WriteText('%s\n%s\n\n' % (label, underline))
		self.__narr_TextCtrl.WriteText(self.__exporter.get_summary_info(0))

		# Set sash position
		self.__tree_narr_splitter.SetSashPosition(self.__tree_narr_splitter.GetSizeTuple()[0]/3, True)

		self.expansion_history.restore_expansion()
		
		

		# FIXME: error handling
		return True

			

	#--------------------------------------------------------
	def get_selection(self):
		"""
		"""
		return self.__selected_node
	#--------------------------------------------------------
	def get_item_parent(self, tree_item):
		"""
		"""		
		return self.__emr_tree.GetItemParent(tree_item)
	#--------------------------------------------------------
	def SetCustomRightWidget(self, widget):
		"""
		@param widget: 
		@type widget: 
		"""
		widget.Reparent(self.__tree_narr_splitter)
		self.__custom_right_widget = widget
		self.__tree_narr_splitter.ReplaceWindow(self.__narr_TextCtrl, self.__custom_right_widget)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""
		Clear all information displayed in browser (tree and details area)
		"""
		#self.__emr_tree.DeleteAllItems()    # need this not to be done until expansion of tree recorded
		self.__narr_TextCtrl.Clear()
	#--------------------------------------------------------
	def __display_narrative_on_right_pane(self):
		"""
		"""
		# FIXME: confirmation dialog to avoid loosing edits

		# FIXME: really needed ?
		if id(self.__tree_narr_splitter.GetWindow2()) == id(self.__narr_TextCtrl):
			return True
		self.__tree_narr_splitter.ReplaceWindow(self.__custom_right_widget, self.__narr_TextCtrl)
#		self.__custom_right_widget.Destroy()
		self.__custom_right_widget = None
	#--------------------------------------------------------
	# episodes
	def __handle_episode_context(self, episode=None, pos=wx.DefaultPosition):
		self.__selected_episode = episode
		self.__epi_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__epi_context_popup, pos)
	#--------------------------------------------------------
	def __rename_episode(self, event):
		dlg = wx.TextEntryDialog (
			parent = self,
			message = _('Old: "%s"\nPlease type the new description:\n') % self.__selected_episode['description'],
			caption = _('Renaming episode ...'),
			defaultValue = ''
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return
		new_name = dlg.GetValue().strip()
		if new_name == '':
			return
		if new_name == self.__selected_episode['description']:
			return
		if self.__selected_episode.rename(new_name):
			#avoid collapsing view
			self.__emr_tree.SetItemText( self.__selected_node, new_name)
			return
		gmGuiHelpers.gm_show_error(
			_('Cannot rename episode from\n\n [%s]\n\nto\n\n [%s].') % (self.__selected_episode['description'], new_name),
			_('Error renaming episode ...'),
			gmLog.lErr
		)
		return
	#--------------------------------------------------------
	def __close_episode(self, event):
		print "closing episode"
		print self.__selected_episode
	#--------------------------------------------------------
	def __delete_episode(self, event):
		print "deleting episode"
		print self.__selected_episode
	#--------------------------------------------------------
	def __relink_episode(self, event):
		print "relinking episode"
		print self.__selected_episode
	#--------------------------------------------------------
	def __relink_episode_encounters(self, event):
		print "relinking encounters of episode"
		print self.__selected_episode
	#--------------------------------------------------------
	# encounters
	def __handle_encounter_context(self, encounter = None, pos=wx.DefaultPosition):
		self.__selected_encounter = encounter
		self.PopupMenu(self.__enc_context_popup, pos)
	#--------------------------------------------------------
	def __relink_encounter_data2episode(self, event):
		# find episode we are interested in
		node = self.__emr_tree.GetSelection()
		node_parent = self.__emr_tree.GetItemParent(node)
		curr_episode = self.__emr_tree.GetPyData(node_parent)
		episode_selector = gmEMRStructWidgets.cEpisodeSelectorDlg (
			None,
			-1,
			caption = _('Reordering EMR ...'),
			msg = _(
				'The EMR entries in this encounter were attached to episode:\n "%s"\n'
				"Please select the episode you want to move them to:"
			) % curr_episode['description'],
			action_txt = _('move entries'),
			pk_health_issue = curr_episode['pk_health_issue']
		)
		retval = episode_selector.ShowModal() # Shows it
		episode_selector.Destroy() # finally destroy it when finished.
		
		if retval == dialog_OK:
			target = episode_selector.get_selected_episode()

			target_episode_node = self.find_node( self.__emr_tree, self.__emr_tree.GetRootItem(),  target)
			if target_episode_node and target_episode_node.IsOk():
				print "DEBUG trying to move node ", node, " to ", target_episode_node
				self.move_node(self.__emr_tree, node, target_episode_node) 
				self.__emr_tree.EnsureVisible(target_episode_node)
			else:
				print "No target episode node found"

			self.__selected_encounter.transfer_clinical_data(from_episode = curr_episode, 
									 to_episode = target 
									 )
			
			
		elif retval == dialog_CANCELLED:
			pass
		else:
			raise Exception('Invalid dialog return code [%s]' % retval)
		
		# FIXME: GNUmed internal signal
		
#		self._on_episodes_modified()

		
	
	#FIXME refactor move to exporter ?
	def find_node(self,tree, root,  data_object):
		nodes = []
		id , cookie = tree.GetFirstChild( root)

		#print "DEBUG id , cookie", id, cookie
		#print "DEBUG id dict is ", id.__dict__.keys()	
		while id.IsOk() :
			nodes.append(id)
			id, cookie = tree.GetNextChild( root, cookie)
			

		l = [x for x in nodes if tree.GetPyData( x) == data_object] 
		if l == []:
			print "DEBUG looking further in ", nodes
			if nodes == []:
				return None
			else:
				for x in nodes:
					val = self.find_node(tree, x, data_object)
					if val:
						return val
				
		else:
			return l[0]

	def move_node( self, tree, node, target_node):
		new_node = tree.AppendItem( target_node, tree.GetItemText(node))
		tree.SetPyData( new_node,  tree.GetPyData(node) )
		id, cookie = tree.GetFirstChild( node)
		while id.IsOk():
			self.move_node(tree, id, new_node)
			id, cookie = tree.GetNextChild( node)
		
		tree.Delete(node)
		

		
		
	#--------------------------------------------------------
	# health issues
	def __handle_issue_context(self, issue=None, pos=wx.DefaultPosition):
		self.__selected_issue = issue
#		self.__issue_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__issue_context_popup, pos)
	#--------------------------------------------------------
	def __rename_issue(self, event):
		dlg = wx.TextEntryDialog (
			parent = self,
			message = _('Old: "%s"\nPlease type the new description:\n') % self.__selected_issue['description'],
			caption = _('Renaming health issue ...'),
			defaultValue = ''
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return
		new_name = dlg.GetValue().strip()
		if new_name == '':
			return
		if new_name == self.__selected_issue['description']:
			return
		if self.__selected_issue.rename(new_name):
			#DEBUG why doesn't a refresh occur ?
			self.__emr_tree.SetItemText(self.__selected_node,  new_name)
			return
		gmGuiHelpers.gm_show_error (
			_('Cannot rename health issue from\n\n [%s]\n\nto\n\n [%s].') % (self.__selected_issue['description'], new_name),
			_('Error renaming health issue ...'),
			gmLog.lErr
		)
		return
	#--------------------------------------------------------
	# health issues
	def __handle_root_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__root_context_popup, pos)		
	#--------------------------------------------------------
	def __create_issue(self, event):
		# FIXME: refactor this code, present in three places
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(_('Cannot add health issue. No active patient.'), gmLog.lErr)
			return False
		ea = gmEMRStructWidgets.cHealthIssueEditArea (
			self,
			-1,
			wx.DefaultPosition,
			wx.DefaultSize,
			wx.NO_BORDER | wx.TAB_TRAVERSAL
		)
			
		popup = gmEditArea.cEditAreaPopup (
			parent = None,
			id = -1,
			title = _('Add health issue (pHx item)'),
			size = (200,200),
			pos = wx.DefaultPosition,
			style = wx.CENTRE | wx.STAY_ON_TOP | wx.CAPTION | wx.SUNKEN_BORDER,
			name ='',
			edit_area = ea
		)
		result = popup.ShowModal()
		if ea._health_issue :
			self.__exporter._add_health_issue_branch( self.__emr_tree, ea._health_issue)


#================================================================
class cEMRJournalPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__do_layout()

		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		self.__journal = wx.TextCtrl (
			self,
			-1,
			_('No EMR data loaded.'),
			style = wx.TE_MULTILINE | wx.TE_READONLY
		)
		self.__journal.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
		# arrange widgets
		szr_outer = wx.BoxSizer(wx.VERTICAL)
		szr_outer.Add(self.__journal, 1, wx.EXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self._on_patient_selected)
		return 1
	#--------------------------------------------------------
	def _on_patient_selected(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Fills UI with data.
		"""
#		self.__reset_ui_content()
		if self.refresh_journal():
			return True
		return False
	#--------------------------------------------------------
	def refresh_journal(self):

		# get data from backend
		txt = StringIO.StringIO()
		exporter = gmPatientExporter.cEMRJournalExporter()
		# FIXME: if journal is large this will error out, use generator/yield etc
		successful = exporter.export(txt)
		if not successful:
			_log.Log(gmLog.lErr, 'cannot get EMR journal')
			self.__journal.SetValue (_(
				'An error occurred while retrieving the EMR\n'
				'in journal form for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return False
		self.__journal.SetValue(txt.getvalue())
		txt.close()
		return True


#================================================================

class ExpansionHistory:
	def __init__(self, emr_browser, tree):
		self._browser =emr_browser
		self._tree = tree

		
		self._expansion_history = {} # for remembering expansion states of previously visited histories
		self.__last_pat_desc = None
		self.__selected_node = None
		
	def remember_expansion(self):
		ix = self.__last_pat_desc
		if ix is None:
			return
		#print "\nDEBUG Remembering with index",ix , " type of ix is ", type(ix)
		#print
		l = []
		
		#if cache full resize 
		if not self._expansion_history.has_key(ix) and  len( self._expansion_history) > MAX_EXPANSION_HISTORY:
				i = MAX_EXPANSION_HISTORY / 4
				for k in self._expansion_history.keys():
					del (self._expansion_history[k])
					i -= 1
					if i < 1:
						break
				
		self._expansion_history[ix] = l
		self._record_expansion(self._tree, self._tree.GetRootItem(), l)
		

	def _record_expansion(self,tree,  root, l):
		if not root or not root.IsOk():
			return
		id, cookie = tree.GetFirstChild( root)
		#print "id", id, " is Ok", id.IsOk()
		while id.IsOk():
			expanded = tree.IsExpanded(id)
			#print "id expanded = ", expanded
			l2 = [tree.IsSelected(id)]
			
			if expanded:
				self._record_expansion(tree, id, l2)
			#print "expansion at ", id , " is ",  l2
			l.append(l2)
			id, cookie = tree.GetNextChild(root,  cookie)
		
	def restore_expansion(self):
		ix = gmPerson.gmCurrentPatient().get_identity()['description']
		self.__last_pat_desc  = ix 

		print "DEBUG restoring with ",ix 
		if self._expansion_history.has_key(ix):
			l = self._expansion_history[ix]
		        self.__selected_node = None
			self._restore_expand( self._tree, self._tree.GetRootItem(), l)

		if self.__selected_node:		
			self._tree.SelectItem( self.__selected_node)	

	
	
	def _restore_expand(self, tree, root, l):
		id, cookie = tree.GetFirstChild(root)
		for x in l:
			if not id.IsOk():
				break
			selected = x[0]
			if selected:
				self.__selected_node = id	
			x = x[1:]
			if x <>  []:
				tree.Expand( id)
				self._restore_expand( tree, id, x)
			id, cookie = tree.GetNextChild(root, cookie)
	
			

	

		
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
		gmPG.set_default_client_encoding('latin1')
		pool = gmPG.ConnectionPool()
		
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(person = patient)

		# display standalone browser
		application = wx.PyWidgetTester(size=(800,600))
		emr_browser = cEMRBrowserPanel(application.frame, -1)
		emr_browser.refresh_tree()

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

	_log.Log (gmLog.lInfo, "closing emr browser...")

#================================================================
# $Log: gmEMRBrowser.py,v $
# Revision 1.50  2005-12-27 02:52:40  sjtan
#
# allow choice of closing old episode, or relinking to old episode, whenever opening a new episode in the present of an already open episode of an issue.
# Small logic error fixed where the id of the health_issue was passed in as the id of an episode.
#
# Revision 1.49  2005/10/18 13:34:00  sjtan
# after running; small diffs
#
# Revision 1.48  2005/10/09 06:42:02  sjtan
# timely cache update means a complete tree reconstruct can be done quite fast ( currently sized records anyway),
# so don't use refresh_historical_tree() - need to debug this anyway.
#
# Revision 1.47  2005/10/08 12:33:10  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.46  2005/10/04 19:24:53  sjtan
# browser now remembers expansion state and select state between change of patients, between health issue rename, episode rename or encounter relinking. This helps when reviewing the record more than once in a day.
#
# Revision 1.45  2005/10/04 13:09:49  sjtan
# correct syntax errors; get soap entry working again.
#
# Revision 1.44  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.43  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.42  2005/09/27 20:44:58  ncq
# - wx.wx* -> wx.*
#
# Revision 1.41  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.40  2005/09/24 09:17:28  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.39  2005/09/11 17:30:02  ncq
# - cleanup
#
# Revision 1.38  2005/09/08 16:57:48  ncq
# - smaller font in journal display
#
# Revision 1.37  2005/07/21 21:00:46  ncq
# - cleanup, better strings
#
# Revision 1.36  2005/07/02 18:20:52  ncq
# - quite some cleanup
#
# Revision 1.35  2005/06/29 18:35:17  cfmoro
# create encounter from EMR tree. Added FIXME for refactor duplicated code
#
# Revision 1.34  2005/06/29 12:53:50  cfmoro
# Added create issue menu item to root node
#
# Revision 1.33  2005/06/23 14:59:43  ncq
# - cleanup __relink_encounter_data2episode()
#
# Revision 1.32  2005/06/20 13:03:38  cfmoro
# Relink encounter to another episode
#
# Revision 1.31  2005/06/15 22:27:20  ncq
# - allow issue renaming
#
# Revision 1.30  2005/06/14 20:26:04  cfmoro
# refresh tree on unit test startup
#
# Revision 1.29  2005/06/14 20:14:16  cfmoro
# unit testing fix
#
# Revision 1.28  2005/06/14 18:57:50  ncq
# - support renaming an episode
#
# Revision 1.27  2005/04/24 14:44:05  ncq
# - callbacks must be _* not __* or else namespace invisibility will ensue
#
# Revision 1.26  2005/04/12 16:19:49  ncq
# - add cEMRJournalPanel for plugin
#
# Revision 1.25  2005/04/05 16:21:54  ncq
# - a fix by Syan
# - cleanup
#
# Revision 1.24  2005/04/03 20:10:51  ncq
# - add export_emr_to_ascii()
#
# Revision 1.23  2005/04/03 09:15:39  ncq
# - roll back EMR export button
#   - my suggestion to place it there wasn't logically sound
#     and it screwed up changing the right hand window, too
#
# Revision 1.22	 2005/04/02 21:37:27  cfmoro
# Unlinked episodes displayes in EMR tree and dump
#
# Revision 1.21	 2005/04/02 20:45:14  cfmoro
# Implementated	 exporting emr from gui client
#
# Revision 1.20	 2005/03/30 22:10:07  ncq
# - just cleanup
#
# Revision 1.19	 2005/03/30 18:59:03  cfmoro
# Added file selector dialog to emr dump callback function
#
# Revision 1.18	 2005/03/30 18:14:56  cfmoro
# Added emr export button
#
# Revision 1.17  2005/03/29 07:27:14  ncq
# - add missing argument
#
# Revision 1.16  2005/03/11 22:52:54  ncq
# - simplify popup menu use
#
# Revision 1.15  2005/03/10 19:51:29  cfmoro
# Obtained problem from cClinicalRecord on progress notes edition
#
# Revision 1.14  2005/03/09 20:00:13  cfmoro
# Added fixme comment in problem retrieval
#
# Revision 1.13  2005/03/09 19:43:21  cfmoro
# EMR browser edit problem-episodes notes responsible for providing the narrative definitions to cSoapResizingPanel
#
# Revision 1.12  2005/03/09 18:31:57  cfmoro
# As proof of concept: episode editor and notes editor are displayed in the right panel. Just an initial draft, needs feeback a lot of coding yet ;)
#
# Revision 1.11  2005/03/09 16:58:09  cfmoro
# Thanks to Syan code, added contextual menu to emr tree. Linked episode edition action with the responsible dialog
#
# Revision 1.10  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.9  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.8  2005/01/31 13:02:18  ncq
# - use ask_for_patient() in gmPerson.py
#
# Revision 1.7  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.6  2004/10/31 00:37:13  cfmoro
# Fixed some method names. Refresh function made public for easy reload, eg. standalone. Refresh browser at startup in standalone mode
#
# Revision 1.5  2004/09/06 18:57:27  ncq
# - Carlos pluginized the lot ! :-)
# - plus some fixes/tabified it
#
# Revision 1.4	2004/09/01 22:01:45	 ncq
# - actually use Carlos' issue/episode summary code
#
# Revision 1.3	2004/08/11 09:46:24	 ncq
# - now that EMR exporter supports SOAP notes - display them
#
# Revision 1.2	2004/07/26 00:09:27	 ncq
# - Carlos brings us data display for the encounters - can REALLY browse EMR now !
#
# Revision 1.1	2004/07/21 12:30:25	 ncq
# - initial checkin
#
