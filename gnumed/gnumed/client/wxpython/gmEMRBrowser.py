"""GNUmed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.65 2007-01-15 13:08:55 ncq Exp $
__version__ = "$Revision: 1.65 $"
__author__ = "cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# std lib
import sys, types, os.path, StringIO

# 3rd party
import wx

# GNUmed libs
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmRegetMixin, gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets, gmEditArea
from Gnumed.wxGladeWidgets import wxgScrolledEMRTreePnl, wxgSplittedEMRTreeBrowserPnl

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# module level constants
dialog_OK = -2

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
		gmGuiHelpers.gm_statustext(_('Cannot export EMR. No active patient.'), gmLog.lErr)
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
class cEMRTree(wx.TreeCtrl, gmGuiHelpers.cTreeExpansionHistoryMixin):
	"""This wx.TreeCtrl derivative displays a tree view of the medical record."""

	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_HAS_BUTTONS | wx.NO_BORDER
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		gmGuiHelpers.cTreeExpansionHistoryMixin.__init__(self)

		try:
			self.__narr_display = kwds['narr_display']
			del kwds['narr_display']
		except KeyError:
			self.__narr_display = None
		self.__pat = gmPerson.gmCurrentPatient()
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)

		self.__make_popup_menus()
		self.__register_events()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		if not self.__pat.is_connected():
			gmGuiHelpers.gm_statustext (
				_('Cannot load clinical narrative. No active patient.'),
				gmLog.lWarn
			)
			return False

		if not self.__populate_tree():
			return False

		return True
	#--------------------------------------------------------
	def set_narrative_display(self, narrative_display=None):
		self.__narr_display = narrative_display
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		"""Configures enabled event signals."""
		wx.EVT_TREE_SEL_CHANGED (self, self.GetId(), self._on_tree_item_selected)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self._on_tree_item_right_clicked)
	#--------------------------------------------------------
	def __populate_tree(self):
		"""Updates EMR browser data."""
		# FIXME: auto select the previously self.__curr_node if not None
		# FIXME: error handling

		wx.BeginBusyCursor()

		self.snapshot_expansion()
		self.DeleteAllItems()

		# init new tree
		ident = self.__pat.get_identity()
		root_item = self.AddRoot(_('%s EMR') % ident['description'])
		self.SetPyData(root_item, None)
		self.SetItemHasChildren(root_item, True)

		# have the tree filled by the exporter
		self.__exporter.get_historical_tree(self)
		self.SelectItem(root_item)

		# and uncollapse
		self.Expand(root_item)

		# display patient summary info
		label = _('Summary')
		underline = '=' * len(label)
		if self.__narr_display is not None:
			self.__narr_display.Clear()
			self.__narr_display.WriteText('%s\n%s\n\n' % (label, underline))
			self.__narr_display.WriteText(self.__exporter.get_summary_info(0))

		self.restore_expansion()

		wx.EndBusyCursor()
		return True
	#--------------------------------------------------------
	def __make_popup_menus(self):
		# make popup menus for later use

		# - episodes
		self.__epi_context_popup = wx.Menu()

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Edit episode details')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__edit_episode)

#		menu_id = wx.NewId()
#		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('rename episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__rename_episode)

		# delete episode
		# attach all encounters to another episode

		# - encounters
		self.__enc_context_popup = wx.Menu()
		menu_id = wx.NewId()
		# - move data
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('move encounter data to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
		# - edit encounter details
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('edit consultation details')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__edit_consultation_details)
		# attach encounter to another patient
		# delete encounter
		# attach all progress notes to another encounter

		# - health issues
		self.__issue_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__issue_context_popup.AppendItem(wx.MenuItem(self.__issue_context_popup, menu_id, _('edit health issue')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__edit_issue)
		
		# - root node
		self.__root_context_popup = wx.Menu()
		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('create health issue')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__create_issue)
		# print " attach issue to another patient"
		# print " move all episodes to another issue"
	#--------------------------------------------------------
	# episodes
	def __handle_episode_context(self, pos=wx.DefaultPosition):
		self.__epi_context_popup.SetTitle(_('Episode %s') % self.__curr_node_data['description'])
		self.PopupMenu(self.__epi_context_popup, pos)
	#--------------------------------------------------------
	def __edit_episode(self, event):
		node_data = self.GetPyData(self.__curr_node)
		dlg = gmEMRStructWidgets.cEpisodeEditAreaDlg(parent=self, episode=node_data)
		result = dlg.ShowModal()
		if result == wx.ID_OK:
			self.__populate_tree()
	#--------------------------------------------------------
#	def __rename_episode(self, event):
#		dlg = wx.TextEntryDialog (
#			parent = self,
#			message = _('Old: "%s"\nPlease type the new description:\n') % self.__curr_node_data['description'],
#			caption = _('Renaming episode ...'),
#			defaultValue = ''
#		)
#		result = dlg.ShowModal()
#		if result == wx.ID_CANCEL:
#			return
#		new_name = dlg.GetValue().strip()
#		if new_name == '':
#			return
#		if new_name == self.__curr_node_data['description']:
#			return
#		if self.__curr_node_data.rename(new_name):
#			# avoid collapsing view
#			self.SetItemText(self.__curr_node, new_name)
#			return
#		gmGuiHelpers.gm_show_error (
#			_('Cannot rename episode from\n\n [%s]\n\nto\n\n [%s].') % (self.__curr_node_data['description'], new_name),
#			_('Error renaming episode ...'),
#			gmLog.lErr
#		)
#		return
	#--------------------------------------------------------
	def __delete_episode(self, event):
		print "deleting episode"
		print self.__curr_node_data
	#--------------------------------------------------------
	def __relink_episode_encounters(self, event):
		print "relinking encounters of episode"
		print self.__curr_node_data
	#--------------------------------------------------------
	# encounters
	def __handle_encounter_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__enc_context_popup, pos)
	#--------------------------------------------------------
	def __edit_consultation_details(self, event):
		node_data = self.GetPyData(self.__curr_node)
		dlg = gmEMRStructWidgets.cEncounterEditAreaDlg(parent=self, encounter=node_data)
		dlg.ShowModal()
		self.__populate_tree()
	#--------------------------------------------------------
	def __relink_encounter_data2episode(self, event):

		node_parent = self.GetItemParent(self.__curr_node)
		owning_episode = self.GetPyData(node_parent)

		episode_selector = gmEMRStructWidgets.cEpisodeSelectorDlg (
			None,
			-1,
			caption = _('Reordering EMR ...'),
			msg = _(
				'The EMR entries in this encounter were attached to episode:\n "%s"\n'
				"Please select the episode you want to move them to:"
			) % owning_episode['description'],
			action_txt = _('move entries'),
			pk_health_issue = owning_episode['pk_health_issue']
		)
		retval = episode_selector.ShowModal()
		target = episode_selector.get_selected_episode()
		episode_selector.Destroy()
		
		if retval == dialog_OK:
			target_episode_node = self.__find_node(self.GetRootItem(), target)
			if target_episode_node and target_episode_node.IsOk():
				print "DEBUG trying to move node ", node, " to ", target_episode_node
				self.__move_node(node, target_episode_node)
				self.EnsureVisible(target_episode_node)
			else:
				print "No target episode node found"
			self.__curr_node_data.transfer_clinical_data (
				source_episode = owning_episode,
				target_episode = target_episode_node
			)
		
		# FIXME: GNUmed internal signal
		#self._on_episodes_modified()
	#--------------------------------------------------------
	def __find_node(self, root, data_object):
		nodes = []
		id , cookie = self.GetFirstChild(root)

		#print "DEBUG id , cookie", id, cookie
		#print "DEBUG id dict is ", id.__dict__.keys()
		while id.IsOk():
			nodes.append(id)
			id, cookie = self.GetNextChild( root, cookie)

		l = [x for x in nodes if self.GetPyData(x) == data_object]
		if l == []:
			print "DEBUG looking further in ", nodes
			if nodes == []:
				return None
			else:
				for x in nodes:
					val = self.__find_node(x, data_object)
					if val:
						return val
		else:
			return l[0]
	#--------------------------------------------------------
	def __move_node(self, node, target_node):
		new_node = self.AppendItem(target_node, self.GetItemText(node))
		self.SetPyData(new_node, self.GetPyData(node))
		id, cookie = self.GetFirstChild(node)
		while id.IsOk():
			self.__move_node(id, new_node)
			id, cookie = self.GetNextChild(node)
		self.Delete(node)
	#--------------------------------------------------------
	# health issues
	def __handle_issue_context(self, pos=wx.DefaultPosition):
#		self.__issue_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__issue_context_popup, pos)
	#--------------------------------------------------------
	def __edit_issue(self, event):
		ea = gmEMRStructWidgets.cHealthIssueEditAreaDlg(parent=self, id=-1, issue=self.__curr_node_data)
		ea.ShowModal()
		self.SetItemText(self.__curr_node, self.__curr_node_data['description'])
		self.Refresh()
		#self.Update()
		return
	#--------------------------------------------------------
	# root
	def __handle_root_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__root_context_popup, pos)		
	#--------------------------------------------------------
	def __create_issue(self, event):

		return True

		# FIXME: refactor this code, present in three places
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmGuiHelpers.gm_statustext(_('Cannot add health issue. No active patient.'), gmLog.lErr)
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
			self.__exporter._add_health_issue_branch (self, ea._health_issue)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		"""Displays information for a selected tree node."""
		# retrieve the selected EMR element
		sel_item = event.GetItem()
		node_data = self.GetPyData(sel_item)
		self.__curr_node = sel_item

		# update displayed text
		if isinstance(node_data, (gmEMRStructItems.cHealthIssue, types.DictType)):
			txt = self.__exporter.get_issue_info(issue=node_data)
		elif isinstance(node_data, gmEMRStructItems.cEpisode):
			txt = self.__exporter.get_episode_summary(episode=node_data)
		elif isinstance(node_data, gmEMRStructItems.cEncounter):
			epi = self.GetPyData(self.GetItemParent(sel_item))
			txt = self.__exporter.get_encounter_info(episode=epi, encounter=node_data)
		else:
			txt = _('Summary') + '\n=======\n\n' + self.__exporter.get_summary_info(0)

		if self.__narr_display is not None:
			self.__narr_display.Clear()
			self.__narr_display.WriteText(txt)

		return True
	#--------------------------------------------------------
	def _on_tree_item_right_clicked(self, event):
		"""Right button clicked: display the popup for the tree"""
		# FIXME: should get the list item at the current position
		# FIXME: should then update the context

		node = event.GetItem()
		self.SelectItem(node)
		self.__curr_node_data = self.GetPyData(node)
		self.__curr_node = node

		pos = wx.DefaultPosition
		if isinstance(self.__curr_node_data, gmEMRStructItems.cHealthIssue):
			self.__handle_issue_context(pos=pos)
		elif isinstance(self.__curr_node_data, gmEMRStructItems.cEpisode):
			self.__handle_episode_context(pos=pos)
		elif isinstance(self.__curr_node_data, gmEMRStructItems.cEncounter):
			self.__handle_encounter_context(pos=pos)
		elif node == self.GetRootItem():
			self.__handle_root_context()
		else:
			print "error: unknown node type, no popup menu"
		event.Skip()
#================================================================
class cScrolledEMRTreePnl(wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A scrollable panel holding an EMR tree.

	Lacks a widget to display details for selected items. The
	tree data will be refetched - if necessary - when the widget
	is repainted. Refetching can also be initiated (given it is
	necessary) by calling repopulate_ui().
	"""
	def __init__(self, *args, **kwds):
		wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__register_interests()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._schedule_data_reget)
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Fills UI with data."""
		if not self._emr_tree.refresh():
			_log.Log(gmLog.lErr, "cannot update EMR tree")
			return False
		return True
#============================================================
class cSplittedEMRTreeBrowserPnl(wxgSplittedEMRTreeBrowserPnl.wxgSplittedEMRTreeBrowserPnl):
	"""A splitter window holding an EMR tree.

	The left hand side displays a scrollable EMR tree while
	on the right details for selected items are displayed.
	"""
	def __init__(self, *args, **kwds):
		wxgSplittedEMRTreeBrowserPnl.wxgSplittedEMRTreeBrowserPnl.__init__(self, *args, **kwds)
		self._pnl_emr_tree._emr_tree.set_narrative_display(narrative_display = self._TCTRL_item_details)
	#--------------------------------------------------------
	def repopulate_ui(self):
		"""Fills UI with data."""
		if not self._pnl_emr_tree._populate_with_data():
			_log.Log(gmLog.lErr, "cannot update EMR tree")
			return False
		self._splitter_browser.SetSashPosition(self._splitter_browser.GetSizeTuple()[0]/3, True)
		return True
#================================================================
#class cEMRJournalPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
class cEMRJournalPanel(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
#		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

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
		gmDispatcher.connect(signal = gmSignals.post_patient_selection(), receiver = self._on_post_patient_selection)
		return 1
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		# FIXME: check for visibility
		self.__journal.SetValue(u'')
		return True
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
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
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
#	def _populate_with_data(self):
#		"""Fills UI with data.
#		"""
#		if self.refresh_journal():
#			return True
#		return False
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
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient = patient)

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

	_log.Log (gmLog.lInfo, "closing emr browser...")

#================================================================
# $Log: gmEMRBrowser.py,v $
# Revision 1.65  2007-01-15 13:08:55  ncq
# - remove explicit __relink_episode2issue as episode details editor now does it
#
# Revision 1.64  2007/01/13 22:26:55  ncq
# - remove cruft
# - mix expansion history into emr tree browser
#
# Revision 1.63  2007/01/06 23:41:40  ncq
# - missing :
#
# Revision 1.62  2007/01/04 23:41:36  ncq
# - use new episode edit area
#
# Revision 1.61  2006/12/25 22:50:50  ncq
# - add editing of consultation details from EMR tree right-click popup menu
#
# Revision 1.60  2006/12/13 23:32:41  ncq
# - emr journal on a diet
#
# Revision 1.59  2006/11/24 14:20:44  ncq
# - used shiny new health issue edit area in issue context menu
# - refresh tree after editing health issue
#
# Revision 1.58  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.57  2006/11/05 16:02:00  ncq
# - cleanup
#
# Revision 1.56  2006/10/09 12:22:27  ncq
# - some cleanup
# - adjust to changed signature of encounter.transfer_clinical_data()
#
# Revision 1.55  2006/06/26 13:03:22  ncq
# - improve menu strings
# - implement moving episodes among issues
#
# Revision 1.54  2006/05/28 20:53:28  ncq
# - cleanup, fix some variables and typos
#
# Revision 1.53  2006/05/28 16:23:10  ncq
# - cleanup
# - dedicated cEMRTree akin to cDocTree
# - wxGladify tree widgets
#
# Revision 1.52  2006/05/15 13:35:59  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.51  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.50  2005/12/27 02:52:40  sjtan
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
