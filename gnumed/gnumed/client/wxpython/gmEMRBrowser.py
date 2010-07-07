"""GNUmed patient EMR tree browser.
"""
#================================================================
__version__ = "$Revision: 1.111 $"
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
from Gnumed.wxpython import gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets
from Gnumed.wxpython import gmAllergyWidgets, gmNarrativeWidgets, gmPatSearchWidgets
from Gnumed.wxpython import gmDemographicsWidgets


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

		self._old_cursor_pos = None

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

		# handle tooltips
#		wx.EVT_MOTION(self, self._on_mouse_motion)
		wx.EVT_TREE_ITEM_GETTOOLTIP(self, -1, self._on_tree_item_gettooltip)

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
		self.__curr_node = root_item

		self.SelectItem(root_item)
		self.Expand(root_item)
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
			if node_data['pk_health_issue'] is None:
				txt = _('Pool of unassociated episodes:\n\n  "%s"') % node_data['description']
			else:
				txt = node_data.format(left_margin=1, patient = self.__pat)

		elif isinstance(node_data, gmEMRStructItems.cEpisode):
			txt = node_data.format(left_margin = 1, patient = self.__pat)

		elif isinstance(node_data, gmEMRStructItems.cEncounter):
			epi = self.GetPyData(self.GetItemParent(self.__curr_node))
			txt = node_data.format(episodes = [epi['pk_episode']], with_soap = True, left_margin = 1, patient = self.__pat)

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

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Promote')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__promote_episode_to_issue)

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Move encounters')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__move_encounters)

		# - encounters
		self.__enc_context_popup = wx.Menu(title = _('Encounter Menu'))
		# - move data
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Move data to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
		# - edit encounter details
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__edit_encounter_details)

		item = self.__enc_context_popup.Append(-1, _('Edit progress notes'))
		self.Bind(wx.EVT_MENU, self.__edit_progress_notes, item)

		item = self.__enc_context_popup.Append(-1, _('Move progress notes'))
		self.Bind(wx.EVT_MENU, self.__move_progress_notes, item)

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

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Create health issue')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__create_issue)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage allergies')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__document_allergy)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage procedures')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_procedures)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage hospitalizations')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_hospital_stays)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage occupation')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_occupation)

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
	# episode level
	#--------------------------------------------------------
	def __move_encounters(self, event):
		episode = self.GetPyData(self.__curr_node)

		gmNarrativeWidgets.move_progress_notes_to_another_encounter (
			parent = self,
			episodes = [episode['pk_episode']],
			move_all = True
		)
	#--------------------------------------------------------
	def __edit_episode(self, event):
		gmEMRStructWidgets.edit_episode(parent = self, episode = self.__curr_node_data)
	#--------------------------------------------------------
	def __promote_episode_to_issue(self, evt):
		pat = gmPerson.gmCurrentPatient()
		gmEMRStructWidgets.promote_episode_to_issue(parent=self, episode = self.__curr_node_data, emr = pat.get_emr())
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
	# encounter level
	#--------------------------------------------------------
	def __move_progress_notes(self, evt):
		encounter = self.GetPyData(self.__curr_node)
		node_parent = self.GetItemParent(self.__curr_node)
		episode = self.GetPyData(node_parent)

		gmNarrativeWidgets.move_progress_notes_to_another_encounter (
			parent = self,
			encounters = [encounter['pk_encounter']],
			episodes = [episode['pk_episode']]
		)
	#--------------------------------------------------------
	def __edit_progress_notes(self, event):
		encounter = self.GetPyData(self.__curr_node)
		node_parent = self.GetItemParent(self.__curr_node)
		episode = self.GetPyData(node_parent)

		gmNarrativeWidgets.manage_progress_notes (
			parent = self,
			encounters = [encounter['pk_encounter']],
			episodes = [episode['pk_episode']]
		)
	#--------------------------------------------------------
	def __edit_encounter_details(self, event):
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
	# issue level
	#--------------------------------------------------------
	def __edit_issue(self, event):
		gmEMRStructWidgets.edit_health_issue(parent = self, issue = self.__curr_node_data)
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
	# EMR level
	#--------------------------------------------------------
	def __create_issue(self, event):
		gmEMRStructWidgets.edit_health_issue(parent = self, issue = None)
	#--------------------------------------------------------
	def __document_allergy(self, event):
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		# FIXME: use signal and use node level update
		if dlg.ShowModal() == wx.ID_OK:
			self.__populate_tree()
		dlg.Destroy()
		return
	#--------------------------------------------------------
	def __manage_procedures(self, event):
		gmEMRStructWidgets.manage_performed_procedures(parent = self)
	#--------------------------------------------------------
	def __manage_hospital_stays(self, event):
		gmEMRStructWidgets.manage_hospital_stays(parent = self)
	#--------------------------------------------------------
	def __manage_occupation(self, event):
		gmDemographicsWidgets.edit_occupation()
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
#	#--------------------------------------------------------
#	def _on_mouse_motion(self, event):
#
#		cursor_pos = (event.GetX(), event.GetY())
#
#		self.SetToolTipString(u'')
#
#		if cursor_pos != self._old_cursor_pos:
#			self._old_cursor_pos = cursor_pos
#			(item, flags) = self.HitTest(cursor_pos)
#			#if flags != wx.TREE_HITTEST_NOWHERE:
#			if flags == wx.TREE_HITTEST_ONITEMLABEL:
#				data = self.GetPyData(item)
#
#				if not isinstance(data, gmEMRStructItems.cEncounter):
#					return
#
#				self.SetToolTip(u'%s  %s  %s - %s\n\nRFE: %s\nAOE: %s' % (
#					data['started'].strftime('%x'),
#					data['l10n_type'],
#					data['started'].strftime('%H:%m'),
#					data['last_affirmed'].strftime('%H:%m'),
#					gmTools.coalesce(data['reason_for_encounter'], u''),
#					gmTools.coalesce(data['assessment_of_encounter'], u'')
#				))
	#--------------------------------------------------------
	def _on_tree_item_gettooltip(self, event):

		item = event.GetItem()

		if not item.IsOk():
			event.SetToolTip(u' ')
			return

		data = self.GetPyData(item)

		if isinstance(data, gmEMRStructItems.cEncounter):
			event.SetToolTip(u'%s  %s  %s - %s\n\nRFE: %s\nAOE: %s' % (
				data['started'].strftime('%x'),
				data['l10n_type'],
				data['started'].strftime('%H:%M'),
				data['last_affirmed'].strftime('%H:%M'),
				gmTools.coalesce(data['reason_for_encounter'], u''),
				gmTools.coalesce(data['assessment_of_encounter'], u'')
			))

		elif isinstance(data, gmEMRStructItems.cEpisode):
			tt = u''
			tt += gmTools.bool2subst (
				(data['diagnostic_certainty_classification'] is not None),
				data.diagnostic_certainty_description + u'\n\n',
				u''
			)
			tt += gmTools.bool2subst (
				data['episode_open'],
				_('ongoing episode'),
				_('closed episode'),
				'error: episode state is None'
			)
			if tt == u'':
				tt = u' '
			event.SetToolTip(tt)

		elif isinstance(data, gmEMRStructItems.cHealthIssue):
			tt = u''
			tt += gmTools.bool2subst(data['is_confidential'], _('*** CONFIDENTIAL ***\n\n'), u'')
			tt += gmTools.bool2subst (
				(data['diagnostic_certainty_classification'] is not None),
				data.diagnostic_certainty_description + u'\n',
				u''
			)
			tt += gmTools.bool2subst (
				(data['laterality'] not in [None, u'na']),
				data.laterality_description + u'\n',
				u''
			)
			# noted_at_age is too costly
			tt += gmTools.bool2subst(data['is_active'], _('active') + u'\n', u'')
			tt += gmTools.bool2subst(data['clinically_relevant'], _('clinically relevant') + u'\n', u'')
			tt += gmTools.bool2subst(data['is_cause_of_death'], _('contributed to death') + u'\n', u'')
			tt += gmTools.coalesce(data['grouping'], u'', _('Grouping: %s'))
			if tt == u'':
				tt = u' '
			event.SetToolTip(tt)

		else:
			event.SetToolTip(u' ')
			#self.SetToolTipString(u'')

		# doing this prevents the tooltip from showing at all
		#event.Skip()

#widgetXY.GetToolTip().Enable(False)
#
#seems to work, supposing the tooltip is actually set for the widget,
#otherwise a test would be needed
#if widgetXY.GetToolTip():
#    widgetXY.GetToolTip().Enable(False)
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

		# issues: alpha by grouping, no grouping at the bottom
		if isinstance(item1, gmEMRStructItems.cHealthIssue):

			# no grouping below grouping
			if item1['grouping'] is None:
				if item2['grouping'] is not None:
					return 1

			# grouping above no grouping
			if item1['grouping'] is not None:
				if item2['grouping'] is None:
					return -1

			# both no grouping: alpha on description
			if (item1['grouping'] is None) and (item2['grouping'] is None):
				if item1['description'].lower() < item2['description'].lower():
					return -1
				if item1['description'].lower() > item2['description'].lower():
					return 1
				return 0

			# both with grouping: alpha on grouping, then alpha on description
			if item1['grouping'] < item2['grouping']:
				return -1

			if item1['grouping'] > item2['grouping']:
				return 1

			if item1['description'].lower() < item2['description'].lower():
				return -1

			if item1['description'].lower() > item2['description'].lower():
				return 1

			return 0

		# dummy health issue always on top
		if isinstance(item1, type({})):
			return -1

		return 0
#================================================================
from Gnumed.wxGladeWidgets import wxgScrolledEMRTreePnl

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
from Gnumed.wxGladeWidgets import wxgSplittedEMRTreeBrowserPnl

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
		gmPatSearchWidgets.set_active_patient(patient = patient)

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
