"""GNUmed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.41 2005-09-26 18:01:50 ncq Exp $
__version__ = "$Revision: 1.41 $"
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
#============================================================
def export_emr_to_ascii(parent=None):
	"""
	Dump the patient's EMR from GUI client
	@param parent - The parent widget
	@type parent - A wxWindow instance
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
	dlg = wx.wxFileDialog (
		parent = parent,
		message = _("Save patient's EMR as..."),
		defaultDir = aDefDir,
		defaultFile = fname,
		wildcard = aWildcard,
		style = wx.wxSAVE
	)
	choice = dlg.ShowModal()
	fname = dlg.GetPath()
	dlg.Destroy()
	if choice == wx.wxID_OK:
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
class cEMRBrowserPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id=-1):
		"""
		Contructs a new instance of EMR browser panel

		parent - Wx parent widget
		id - Wx widget id
		"""
		# Call parents constructors
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxDefaultPosition,
			wx.wxDefaultSize,
			wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)
		
		self.__custom_right_widget = None
		self.__selected_node = None

		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()
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
			style = wx.wxTE_MULTILINE | wx.wxTE_READONLY | wx.wxTE_DONTWRAP
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

		# make popup menus for later use

		# - episodes
		self.__epi_context_popup = wx.wxMenu()
		menu_id = wx.wxNewId()
		self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('rename episode')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__rename_episode)
#		menu_id = wx.wxNewId()
#		self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('close episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__close_episode)
#		menu_id = wx.wxNewId()
#		self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('delete episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__delete_episode)
#		menu_id = wx.wxNewId()
#		self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('attach episode to another health issue')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode)
#		menu_id = wx.wxNewId()
#		self.__epi_context_popup.AppendItem(wx.wxMenuItem(self.__epi_context_popup, menu_id, _('attach all encounters to another episode')))
#		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__relink_episode_encounters)

		# - encounters
		self.__enc_context_popup = wx.wxMenu()
		menu_id = wx.wxNewId()
		self.__enc_context_popup.AppendItem(wx.wxMenuItem(self.__enc_context_popup, menu_id, _('attach encounter to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
#		menu_id = wx.wxNewId()
#		self.__enc_context_popup.AppendItem(wx.wxMenuItem(self.__enc_context_popup, menu_id, _('attach encounter to another patient')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter2patient)
#		menu_id = wx.wxNewId()
#		self.__enc_context_popup.AppendItem(wx.wxMenuItem(self.__enc_context_popup, menu_id, _('delete encounter')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__delete_encounter)
#		menu_id = wx.wxNewId()
#		self.__enc_context_popup.AppendItem(wx.wxMenuItem(self.__enc_context_popup, menu_id, _('attach all progress notes to another encounter')))
#		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_notes2encounter)

		# - health issues
		self.__issue_context_popup = wx.wxMenu()
		menu_id = wx.wxNewId()
		self.__issue_context_popup.AppendItem(wx.wxMenuItem(self.__issue_context_popup, menu_id, _('rename health issue')))
		wx.EVT_MENU(self.__issue_context_popup, menu_id, self.__rename_issue)
		
		# - root node
		self.__root_context_popup = wx.wxMenu()
		menu_id = wx.wxNewId()
		self.__root_context_popup.AppendItem(wx.wxMenuItem(self.__root_context_popup, menu_id, _('create health issue')))
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
		# wx.wxPython events
		wx.EVT_TREE_SEL_CHANGED(self.__emr_tree, self.__emr_tree.GetId(), self._on_tree_item_selected)
		wx.EVT_TREE_ITEM_RIGHT_CLICK(self.__emr_tree, self.__emr_tree.GetId(), self.__on_tree_item_right_clicked)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self._on_episodes_modified)
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
			txt = _('Summary') + '=======\n\n' + self.__exporter.get_summary_info(0)

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
		pos = wx.wxDefaultPosition
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
		self.__emr_tree.DeleteAllItems()
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
	def __handle_episode_context(self, episode=None, pos=wx.wxDefaultPosition):
		self.__selected_episode = episode
		self.__epi_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__epi_context_popup, pos)
	#--------------------------------------------------------
	def __rename_episode(self, event):
		dlg = wx.wxTextEntryDialog (
			parent = self,
			message = _('Old: "%s"\nPlease type the new description:\n') % self.__selected_episode['description'],
			caption = _('Renaming episode ...'),
			defaultValue = ''
		)
		result = dlg.ShowModal()
		if result == wx.wxID_CANCEL:
			return
		new_name = dlg.GetValue().strip()
		if new_name == '':
			return
		if new_name == self.__selected_episode['description']:
			return
		if self.__selected_episode.rename(new_name):
			return
		gmGuiHelpers.gm_show_err (
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
	def __handle_encounter_context(self, encounter = None, pos=wx.wxDefaultPosition):
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

		if retval == dialog_OK:
			target = episode_selector.get_selected_episode()
			self.__selected_encounter.transfer_clinical_data(from_episode = curr_episode, to_episode = target)
		elif retval == dialog_CANCELLED:
			pass
		else:
			raise Exception('Invalid dialog return code [%s]' % retval)
		episode_selector.Destroy() # finally destroy it when finished.
		# FIXME: GNUmed internal signal
#		self._on_episodes_modified()
	#--------------------------------------------------------
	# health issues
	def __handle_issue_context(self, issue=None, pos=wx.wxDefaultPosition):
		self.__selected_issue = issue
#		self.__issue_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__issue_context_popup, pos)
	#--------------------------------------------------------
	def __rename_issue(self, event):
		dlg = wx.wxTextEntryDialog (
			parent = self,
			message = _('Old: "%s"\nPlease type the new description:\n') % self.__selected_issue['description'],
			caption = _('Renaming health issue ...'),
			defaultValue = ''
		)
		result = dlg.ShowModal()
		if result == wx.wxID_CANCEL:
			return
		new_name = dlg.GetValue().strip()
		if new_name == '':
			return
		if new_name == self.__selected_issue['description']:
			return
		if self.__selected_issue.rename(new_name):
			return
		gmGuiHelpers.gm_show_err (
			_('Cannot rename health issue from\n\n [%s]\n\nto\n\n [%s].') % (self.__selected_issue['description'], new_name),
			_('Error renaming health issue ...'),
			gmLog.lErr
		)
		return
	#--------------------------------------------------------
	# health issues
	def __handle_root_context(self, pos=wx.wxDefaultPosition):
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
			wx.wxDefaultPosition,
			wx.wxDefaultSize,
			wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL
		)
			
		popup = gmEditArea.cEditAreaPopup (
			parent = None,
			id = -1,
			title = _('Add health issue (pHx item)'),
			size = (200,200),
			pos = wx.wxDefaultPosition,
			style = wx.wxCENTRE | wx.wxSTAY_ON_TOP | wx.wxCAPTION | wx.wxSUNKEN_BORDER,
			name ='',
			edit_area = ea
		)
		result = popup.ShowModal()
#================================================================
class cEMRJournalPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):
	def __init__(self, *args, **kwargs):
		wx.wxPanel.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__do_layout()

		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		self.__journal = wx.wxTextCtrl (
			self,
			-1,
			_('No EMR data loaded.'),
			style = wx.wxTE_MULTILINE | wx.wxTE_READONLY
		)
		self.__journal.SetFont(wx.wxFont(10, wx.wxMODERN, wx.wxNORMAL, wx.wxNORMAL))
		# arrange widgets
		szr_outer = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_outer.Add(self.__journal, 1, wx.wxEXPAND, 0)
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
		application = wx.wxPyWidgetTester(size=(800,600))
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
# Revision 1.41  2005-09-26 18:01:50  ncq
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
