"""GNUmed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.93.2.2 2008-10-12 17:02:59 ncq Exp $
__version__ = "$Revision: 1.93.2.2 $"
__author__ = "cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# std lib
import sys, types, os.path, StringIO, codecs, logging

# 3rd party
import wx

# GNUmed libs
from Gnumed.pycommon import gmI18N, gmDispatcher, gmExceptions, gmTools
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter
from Gnumed.wxpython import gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets, gmAllergyWidgets, gmNarrativeWidgets
from Gnumed.wxGladeWidgets import wxgScrolledEMRTreePnl, wxgSplittedEMRTreeBrowserPnl

_log = logging.getLogger('gm.ui')
_log.info(__version__)

#============================================================
def export_emr_to_ascii(parent=None):
	"""
	Dump the patient's EMR from GUI client
	@param parent - The parent widget
	@type parent - A wx.Window instance
	"""
	# sanity checks
	if parent is None:
		raise TypeError('expected wx.Window instance as parent, got <None>')

	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		gmDispatcher.send(signal='statustext', msg=_('Cannot export EMR. No active patient.'))
		return False

	# get file name
	wc = "%s (*.txt)|*.txt|%s (*)|*" % (_("text files"), _("all files"))
	defdir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'EMR', pat['dirname'])))
	gmTools.mkdir(defdir)
	fname = '%s-%s_%s.txt' % (_('emr-export'), pat['lastnames'], pat['firstnames'])
	dlg = wx.FileDialog (
		parent = parent,
		message = _("Save patient's EMR as..."),
		defaultDir = defdir,
		defaultFile = fname,
		wildcard = wc,
		style = wx.SAVE
	)
	choice = dlg.ShowModal()
	fname = dlg.GetPath()
	dlg.Destroy()
	if choice != wx.ID_OK:
		return None

	_log.debug('exporting EMR to [%s]', fname)

#	output_file = open(fname, 'wb')
	output_file = codecs.open(fname, 'wb', encoding='utf8', errors='replace')
	exporter = gmPatientExporter.cEmrExport(patient = pat)
	exporter.set_output_file(output_file)
	exporter.dump_constraints()
	exporter.dump_demographic_record(True)
	exporter.dump_clinical_record()
	exporter.dump_med_docs()
	output_file.close()

	gmDispatcher.send('statustext', msg = _('EMR successfully exported to file: %s') % fname, beep = False)
	return fname
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
		self.__curr_node = None
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)

		self.__make_popup_menus()
		self.__register_events()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		if not self.__pat.connected:
			gmDispatcher.send(signal='statustext', msg=_('Cannot load clinical narrative. No active patient.'),)
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

		gmDispatcher.connect(signal = 'narrative_mod_db', receiver = self._on_narrative_mod_db)
		gmDispatcher.connect(signal = 'episode_mod_db', receiver = self._on_episode_mod_db)
		gmDispatcher.connect(signal = 'health_issue_mod_db', receiver = self._on_issue_mod_db)
	#--------------------------------------------------------
	def __populate_tree(self):
		"""Updates EMR browser data."""
		# FIXME: auto select the previously self.__curr_node if not None
		# FIXME: error handling

		wx.BeginBusyCursor()

		self.snapshot_expansion()

		# init new tree
		self.DeleteAllItems()
		root_item = self.AddRoot(_('EMR of %s') % self.__pat['description'])
		self.SetPyData(root_item, None)
		self.SetItemHasChildren(root_item, True)

		# have the tree filled by the exporter
		self.__exporter.get_historical_tree(self)

		self.SelectItem(root_item)
		self.Expand(root_item)
		self.__curr_node = root_item
		self.__update_text_for_selected_node()

		self.restore_expansion()

		wx.EndBusyCursor()
		return True
	#--------------------------------------------------------
	def __update_text_for_selected_node(self):
		"""Displays information for the selected tree node."""

		if self.__narr_display is None:
			return

		if self.__curr_node is None:
			return

		node_data = self.GetPyData(self.__curr_node)

		# update displayed text
		if isinstance(node_data, (gmEMRStructItems.cHealthIssue, types.DictType)):
			# FIXME: turn into real dummy issue
			if node_data['pk'] is None:
				txt = _('Pool of unassociated episodes:\n\n  "%s"') % node_data['description']
			else:
				txt = node_data.format(left_margin=1, patient = self.__pat)

		elif isinstance(node_data, gmEMRStructItems.cEpisode):
			txt = node_data.format(left_margin = 1, patient = self.__pat)

		elif isinstance(node_data, gmEMRStructItems.cEncounter):
			epi = self.GetPyData(self.GetItemParent(self.__curr_node))
			txt = node_data.format(episode = epi, with_soap = True, left_margin = 1, patient = self.__pat)

		else:
			emr = self.__pat.get_emr()
			txt = emr.format_summary()

		self.__narr_display.Clear()
		self.__narr_display.WriteText(txt)
	#--------------------------------------------------------
	def __make_popup_menus(self):

		# - episodes
		self.__epi_context_popup = wx.Menu(title = _('Episode Menu'))

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__edit_episode)

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Delete')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__delete_episode)
		# attach all encounters to another episode

		# - encounters
		self.__enc_context_popup = wx.Menu(title = _('Encounter Menu'))
		# - move data
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Move data to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
		# - edit encounter details
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__edit_consultation_details)

		item = self.__enc_context_popup.Append(-1, _('Export for Medistar'))
		self.Bind(wx.EVT_MENU, self.__export_encounter_for_medistar, item)

		# - health issues
		self.__issue_context_popup = wx.Menu(title = _('Health Issue Menu'))

		menu_id = wx.NewId()
		self.__issue_context_popup.AppendItem(wx.MenuItem(self.__issue_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__edit_issue)

		menu_id = wx.NewId()
		self.__issue_context_popup.AppendItem(wx.MenuItem(self.__issue_context_popup, menu_id, _('Delete')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__delete_issue)

		self.__issue_context_popup.AppendSeparator()

		menu_id = wx.NewId()
		self.__issue_context_popup.AppendItem(wx.MenuItem(self.__issue_context_popup, menu_id, _('Open to encounter level')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__expand_issue_to_encounter_level)
		# print " attach issue to another patient"
		# print " move all episodes to another issue"

		# - root node
		self.__root_context_popup = wx.Menu(title = _('EMR Menu'))
		# add health issue
		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('create health issue')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__create_issue)
		# add allergy
		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('manage allergies')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__document_allergy)

		self.__root_context_popup.AppendSeparator()

		# expand tree
		expand_menu = wx.Menu()
		self.__root_context_popup.AppendMenu(wx.NewId(), _('Open EMR to ...'), expand_menu)

		menu_id = wx.NewId()
		expand_menu.AppendItem(wx.MenuItem(expand_menu, menu_id, _('... issue level')))
		wx.EVT_MENU(expand_menu, menu_id, self.__expand_to_issue_level)

		menu_id = wx.NewId()
		expand_menu.AppendItem(wx.MenuItem(expand_menu, menu_id, _('... episode level')))
		wx.EVT_MENU(expand_menu, menu_id, self.__expand_to_episode_level)

		menu_id = wx.NewId()
		expand_menu.AppendItem(wx.MenuItem(expand_menu, menu_id, _('... encounter level')))
		wx.EVT_MENU(expand_menu, menu_id, self.__expand_to_encounter_level)
	#--------------------------------------------------------
	def __handle_root_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__root_context_popup, pos)
	#--------------------------------------------------------
	def __handle_issue_context(self, pos=wx.DefaultPosition):
#		self.__issue_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__issue_context_popup, pos)
	#--------------------------------------------------------
	def __handle_episode_context(self, pos=wx.DefaultPosition):
		self.__epi_context_popup.SetTitle(_('Episode %s') % self.__curr_node_data['description'])
		self.PopupMenu(self.__epi_context_popup, pos)
	#--------------------------------------------------------
	def __handle_encounter_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__enc_context_popup, pos)
	#--------------------------------------------------------
	#--------------------------------------------------------
	def __edit_episode(self, event):
		dlg = gmEMRStructWidgets.cEpisodeEditAreaDlg(parent=self, episode=self.__curr_node_data)
		dlg.ShowModal()
	#--------------------------------------------------------
	def __delete_episode(self, event):
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent = self,
			id = -1,
			caption = _('Deleting episode'),
			button_defs = [
				{'label': _('Yes, delete'), 'tooltip': _('Delete the episode if possible (it must be completely empty).')},
				{'label': _('No, cancel'), 'tooltip': _('Cancel and do NOT delete the episode.')}
			],
			question = _(
				'Are you sure you want to delete this episode ?\n'
				'\n'
				' "%s"\n'
			) % self.__curr_node_data['description']
		)
		result = dlg.ShowModal()
		if result != wx.ID_YES:
			return

		try:
			gmEMRStructItems.delete_episode(episode = self.__curr_node_data)
		except gmExceptions.DatabaseObjectInUseError:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete episode. There is still clinical data recorded for it.'))
			return
	#--------------------------------------------------------
	def __edit_consultation_details(self, event):
		node_data = self.GetPyData(self.__curr_node)
		dlg = gmEMRStructWidgets.cEncounterEditAreaDlg(parent=self, encounter=node_data)
		dlg.ShowModal()
		dlg.Destroy()
		self.__populate_tree()
	#--------------------------------------------------------
	def __relink_encounter_data2episode(self, event):

		node_parent = self.GetItemParent(self.__curr_node)
		owning_episode = self.GetPyData(node_parent)

		episode_selector = gmNarrativeWidgets.cMoveNarrativeDlg (
			self,
			-1,
			episode = owning_episode,
			encounter = self.__curr_node_data
		)

		result = episode_selector.ShowModal()
		episode_selector.Destroy()

		if result == wx.ID_YES:
			self.__populate_tree()
	#--------------------------------------------------------
	def __edit_issue(self, event):
		dlg = gmEMRStructWidgets.cHealthIssueEditAreaDlg(parent=self, id=-1, issue=self.__curr_node_data)
		dlg.ShowModal()
		dlg.Destroy()
	#--------------------------------------------------------
	def __delete_issue(self, event):
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent = self,
			id = -1,
			caption = _('Deleting health issue'),
			button_defs = [
				{'label': _('Yes, delete'), 'tooltip': _('Delete the health issue if possible (it must be completely empty).')},
				{'label': _('No, cancel'), 'tooltip': _('Cancel and do NOT delete the health issue.')}
			],
			question = _(
				'Are you sure you want to delete this health issue ?\n'
				'\n'
				' "%s"\n'
			) % self.__curr_node_data['description']
		)
		result = dlg.ShowModal()
		if result != wx.ID_YES:
			dlg.Destroy()
			return

		dlg.Destroy()

		try:
			gmEMRStructItems.delete_health_issue(health_issue = self.__curr_node_data)
		except gmExceptions.DatabaseObjectInUseError:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete health issue. There is still clinical data recorded for it.'))
	#--------------------------------------------------------
	def __expand_issue_to_encounter_level(self, evt):

		if not self.__curr_node.IsOk():
			return

		self.Expand(self.__curr_node)

		epi, epi_cookie = self.GetFirstChild(self.__curr_node)
		while epi.IsOk():
			self.Expand(epi)
			epi, epi_cookie = self.GetNextChild(self.__curr_node, epi_cookie)
	#--------------------------------------------------------
	def __create_issue(self, event):
		ea = gmEMRStructWidgets.cHealthIssueEditAreaDlg(parent=self, id=-1)
		ea.ShowModal()
	#--------------------------------------------------------
	def __document_allergy(self, event):
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		# FIXME: use signal and use node level update
		if dlg.ShowModal() == wx.ID_OK:
			self.__populate_tree()
		dlg.Destroy()
		return
	#--------------------------------------------------------
	def __expand_to_issue_level(self, evt):

		root_item = self.GetRootItem()

		if not root_item.IsOk():
			return

		self.Expand(root_item)

		# collapse episodes and issues
		issue, issue_cookie = self.GetFirstChild(root_item)
		while issue.IsOk():
			self.Collapse(issue)
			epi, epi_cookie = self.GetFirstChild(issue)
			while epi.IsOk():
				self.Collapse(epi)
				epi, epi_cookie = self.GetNextChild(issue, epi_cookie)
			issue, issue_cookie = self.GetNextChild(root_item, issue_cookie)
	#--------------------------------------------------------
	def __expand_to_episode_level(self, evt):

		root_item = self.GetRootItem()

		if not root_item.IsOk():
			return

		self.Expand(root_item)

		# collapse episodes, expand issues
		issue, issue_cookie = self.GetFirstChild(root_item)
		while issue.IsOk():
			self.Expand(issue)
			epi, epi_cookie = self.GetFirstChild(issue)
			while epi.IsOk():
				self.Collapse(epi)
				epi, epi_cookie = self.GetNextChild(issue, epi_cookie)
			issue, issue_cookie = self.GetNextChild(root_item, issue_cookie)
	#--------------------------------------------------------
	def __expand_to_encounter_level(self, evt):

		root_item = self.GetRootItem()

		if not root_item.IsOk():
			return

		self.Expand(root_item)

		# collapse episodes, expand issues
		issue, issue_cookie = self.GetFirstChild(root_item)
		while issue.IsOk():
			self.Expand(issue)
			epi, epi_cookie = self.GetFirstChild(issue)
			while epi.IsOk():
				self.Expand(epi)
				epi, epi_cookie = self.GetNextChild(issue, epi_cookie)
			issue, issue_cookie = self.GetNextChild(root_item, issue_cookie)
	#--------------------------------------------------------
	def __export_encounter_for_medistar(self, evt):
		gmNarrativeWidgets.export_narrative_for_medistar_import (
			parent = self,
			soap_cats = u'soap',
			encounter = self.__curr_node_data
		)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_narrative_mod_db(self, *args, **kwargs):
		wx.CallAfter(self.__update_text_for_selected_node)
	#--------------------------------------------------------
	def _on_episode_mod_db(self, *args, **kwargs):
		wx.CallAfter(self.__populate_tree)
	#--------------------------------------------------------
	def _on_issue_mod_db(self, *args, **kwargs):
		wx.CallAfter(self.__populate_tree)
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		sel_item = event.GetItem()
		self.__curr_node = sel_item
		self.__update_text_for_selected_node()
		return True
	#--------------------------------------------------------
	def _on_tree_item_right_clicked(self, event):
		"""Right button clicked: display the popup for the tree"""

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
		elif type(self.__curr_node_data) == type({}):
			# ignore pseudo node "free-standing episodes"
			pass
		else:
			print "error: unknown node type, no popup menu"
		event.Skip()
	#--------------------------------------------------------
	def OnCompareItems (self, node1=None, node2=None):
		"""Used in sorting items.

		-1: 1 < 2
		 0: 1 = 2
		 1: 1 > 2
		"""
		# FIXME: implement sort modes, chron, reverse cron, by regex, etc

		item1 = self.GetPyData(node1)
		item2 = self.GetPyData(node2)

		# encounters: reverse chron
		if isinstance(item1, gmEMRStructItems.cEncounter):
			if item1['started'] == item2['started']:
				return 0
			if item1['started'] > item2['started']:
				return -1
			return 1

		# episodes: chron
		if isinstance(item1, gmEMRStructItems.cEpisode):
			start1 = item1.get_access_range()[0]
			start2 = item2.get_access_range()[0]
			if start1 == start2:
				return 0
			if start1 < start2:
				return -1
			return 1

		# issues: alpha
		if isinstance(item1, gmEMRStructItems.cHealthIssue):
			if item1['description'].lower() == item2['description'].lower():
				return 0
			if item1['description'].lower() > item2['description'].lower():
				return 1
			return -1

		# dummy health issue always on top
		if isinstance(item1, type({})):
			return -1

		return 0
#================================================================
class cScrolledEMRTreePnl(wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl):
	"""A scrollable panel holding an EMR tree.

	Lacks a widget to display details for selected items. The
	tree data will be refetched - if necessary - whenever
	repopulate_ui() is called, e.g., when then patient is changed.
	"""
	def __init__(self, *args, **kwds):
		wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl.__init__(self, *args, **kwds)
#		self.__register_interests()
	#--------------------------------------------------------
#	def __register_interests(self):
#		gmDispatcher.connect(signal= u'post_patient_selection', receiver=self.repopulate_ui)
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._emr_tree.refresh()
		return True
#============================================================
class cSplittedEMRTreeBrowserPnl(wxgSplittedEMRTreeBrowserPnl.wxgSplittedEMRTreeBrowserPnl):
	"""A splitter window holding an EMR tree.

	The left hand side displays a scrollable EMR tree while
	on the right details for selected items are displayed.

	Expects to be put into a Notebook.
	"""
	def __init__(self, *args, **kwds):
		wxgSplittedEMRTreeBrowserPnl.wxgSplittedEMRTreeBrowserPnl.__init__(self, *args, **kwds)
		self._pnl_emr_tree._emr_tree.set_narrative_display(narrative_display = self._TCTRL_item_details)
		self.__register_events()
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		return True
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		if self.GetParent().GetCurrentPage() == self:
			self.repopulate_ui()
		return True
	#--------------------------------------------------------
	def repopulate_ui(self):
		"""Fills UI with data."""
		self._pnl_emr_tree.repopulate_ui()
		self._splitter_browser.SetSashPosition(self._splitter_browser.GetSizeTuple()[0]/3, True)
		return True
#================================================================
class cEMRJournalPanel(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

		self.__do_layout()
		self.__register_events()
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
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Expects to be in a Notebook."""
		if self.GetParent().GetCurrentPage() == self:
			self.repopulate_ui()
		return True
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		txt = StringIO.StringIO()
		exporter = gmPatientExporter.cEMRJournalExporter()
		# FIXME: if journal is large this will error out, use generator/yield etc
		# FIXME: turn into proper list
		try:
			exporter.export(txt)
			self.__journal.SetValue(txt.getvalue())
		except ValueError:
			_log.exception('cannot get EMR journal')
			self.__journal.SetValue (_(
				'An error occurred while retrieving the EMR\n'
				'in journal form for the active patient.\n\n'
				'Please check the log file for details.'
			))
		txt.close()
		self.__journal.ShowPosition(self.__journal.GetLastPosition())
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	_log.info("starting emr browser...")

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
		_log.exception("unhandled exception caught !")
		# but re-raise them
		raise

	_log.info("closing emr browser...")

#================================================================
# $Log: gmEMRBrowser.py,v $
# Revision 1.93.2.2  2008-10-12 17:02:59  ncq
# - wording of EMR browser root node as per Jim
#
# Revision 1.93.2.1  2008/08/31 22:17:01  ncq
# - don't crash on getting narrative change signal before tree has been populated
#
# Revision 1.93  2008/08/15 15:56:38  ncq
# - properly handle context click on pseudo-issue
#
# Revision 1.92  2008/07/28 15:44:39  ncq
# - context menu based Medistar export for any encounter
#
# Revision 1.91  2008/07/14 13:46:11  ncq
# - better naming of dummy health issue
#
# Revision 1.90  2008/07/12 15:31:23  ncq
# - improved formatting of issue info
#
# Revision 1.89  2008/07/07 13:44:33  ncq
# - current patient .connected
# - properly sort tree, encounters: most recent on top as per user request
#
# Revision 1.88  2008/06/28 18:25:58  ncq
# - add expand to ... level popup menu items in EMR tree
#
# Revision 1.87  2008/05/19 16:23:33  ncq
# - let EMR format its summary itself
#
# Revision 1.86  2008/04/11 12:27:45  ncq
# - listen to issue/episode/narrative change signals thereby
#   reducing direct repopulate calls
# - factor out __update_text_for_selected_node() and
#   call format() on nodes that have it
# - rearrange code layout
#
# Revision 1.85  2008/03/05 22:30:14  ncq
# - new style logging
#
# Revision 1.84  2008/01/30 14:07:24  ncq
# - do not use old cfg file support anymore
#
# Revision 1.83  2008/01/22 12:20:53  ncq
# - dummy health issue always on top
# - auto-scroll to bottom of journal
#
# Revision 1.82  2007/12/11 12:49:25  ncq
# - explicit signal handling
#
# Revision 1.81  2007/09/07 10:56:57  ncq
# - cleanup
#
# Revision 1.80  2007/08/29 22:09:10  ncq
# - narrative widgets factored out
#
# Revision 1.79  2007/08/15 14:57:52  ncq
# - pretty up tree popup menus
# - add deletion of health issues
#
# Revision 1.78  2007/08/12 00:09:07  ncq
# - no more gmSignals.py
#
# Revision 1.77  2007/06/18 20:31:10  ncq
# - case insensitively sort health issues
#
# Revision 1.76  2007/06/10 09:56:54  ncq
# - actually sort tree items, add sorting for health issues
#
# Revision 1.75  2007/05/21 14:48:20  ncq
# - cleanup
# - use pat['dirname'], use export/EMR/
# - unicode output files
#
# Revision 1.74  2007/05/21 13:05:25  ncq
# - catch-all wildcard on UNIX must be *, not *.*
#
# Revision 1.73  2007/05/18 13:29:25  ncq
# - some cleanup
# - properly support moving narrative between episodes
#
# Revision 1.72  2007/05/14 13:11:24  ncq
# - use statustext() signal
#
# Revision 1.71  2007/05/14 10:33:33  ncq
# - allow deleting episode
#
# Revision 1.70  2007/03/18 14:04:00  ncq
# - add allergy handling to menu and root node of tree
#
# Revision 1.69  2007/03/02 15:31:45  ncq
# - properly repopulation EMR tree and problem list :-)
#
# Revision 1.68  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.67  2007/02/16 12:51:46  ncq
# - fix add issue popup on root node as requested by user :-)
#
# Revision 1.66  2007/01/16 18:00:59  ncq
# - cleanup
# - explicitely sort episodes and encounters by when they were started
#
# Revision 1.65  2007/01/15 13:08:55  ncq
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
