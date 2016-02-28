"""GNUmed patient EMR tree browser."""
#================================================================
__author__ = "cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import os.path
import StringIO
import io
import logging


# 3rd party
import wx
import wx.lib.mixins.treemixin as treemixin


# GNUmed libs
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmLog2

from Gnumed.exporters import gmPatientExporter

from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmPerson
from Gnumed.business import gmSOAPimporter
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmClinicalRecord

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmSOAPWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmNarrativeWidgets
from Gnumed.wxpython import gmNarrativeWorkflows
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmVaccWidgets
from Gnumed.wxpython import gmFamilyHistoryWidgets
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmTimer


_log = logging.getLogger('gm.ui')

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
	defdir = os.path.abspath(os.path.expanduser(os.path.join('~', 'gnumed', pat['dirname'])))
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

	output_file = io.open(fname, mode = 'wt', encoding = 'utf8', errors = 'replace')
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
class cEMRTree(wx.TreeCtrl, treemixin.ExpansionState):
	"""This wx.TreeCtrl derivative displays a tree view of a medical record."""

	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_HAS_BUTTONS | wx.NO_BORDER | wx.TR_SINGLE
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		self.__soap_display = None
		self.__soap_display_mode = u'details'				# "details" or "journal" or "revisions"
		self.__img_display = None
		self.__cb__enable_display_mode_selection = lambda x:x
		self.__cb__select_edit_mode = lambda x:x
		self.__cb__add_soap_editor = lambda x:x
		self.__pat = None
		self.__curr_node = None
		self.__expanded_nodes = None

		self.__make_popup_menus()
		self.__register_events()

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def _get_soap_display(self):
		return self.__soap_display

	def _set_soap_display(self, soap_display=None):
		self.__soap_display = soap_display
		self.__soap_display_prop_font = soap_display.GetFont()
		self.__soap_display_mono_font = wx.FontFromNativeInfo(self.__soap_display_prop_font.NativeFontInfo)
		self.__soap_display_mono_font.SetFamily(wx.FONTFAMILY_TELETYPE)
		self.__soap_display_mono_font.SetPointSize(self.__soap_display_prop_font.GetPointSize() - 2)

	soap_display = property(_get_soap_display, _set_soap_display)

	#--------------------------------------------------------
	def _get_image_display(self):
		return self.__img_display

	def _set_image_display(self, image_display=None):
		self.__img_display = image_display

	image_display = property(_get_image_display, _set_image_display)

	#--------------------------------------------------------
	def set_enable_display_mode_selection_callback(self, callback):
		if not callable(callback):
			raise ValueError('callback [%s] not callable' % callback)
		self.__cb__enable_display_mode_selection = callback

	#--------------------------------------------------------
	def _set_edit_mode_selector(self, callback):
		if callback is None:
			callback = lambda x:x
		if not callable(callback):
			raise ValueError('edit mode selector [%s] not callable' % callback)
		self.__cb__select_edit_mode = callback

	edit_mode_selector = property(lambda x:x, _set_edit_mode_selector)

	#--------------------------------------------------------
	def _set_soap_editor_adder(self, callback):
		if callback is None:
			callback = lambda x:x
		if not callable(callback):
			raise ValueError('soap editor adder [%s] not callable' % callback)
		self.__cb__add_soap_editor = callback

	soap_editor_adder = property(lambda x:x, _set_soap_editor_adder)

	#--------------------------------------------------------
	# ExpansionState mixin API
	#--------------------------------------------------------
	def GetItemIdentity(self, item):
		if item is None:
			return u'invalid item'

		if not item.IsOk():
			return u'invalid item'

		try:
			node_data = self.GetPyData(item)
		except wx.PyAssertionError:
			_log.exception('unfathomable self.GetPyData() problem occurred, faking root node')
			_log.error('real node: %s', item)
			_log.error('node.IsOk(): %s', item.IsOk())		# already survived this further up
			_log.error('is root node: %s', item == self.GetRootItem())
			_log.error('node.m_pItem: %s', getattr(item, 'm_pItem', '<NO SUCH ATTRIBUTE>'))
			_log.error('node attributes: %s', dir(item))
			gmLog2.log_stack_trace()
			return u'invalid item'

		if isinstance(node_data, gmEMRStructItems.cHealthIssue):
			return u'issue::%s' % node_data['pk_health_issue']
		if isinstance(node_data, gmEMRStructItems.cEpisode):
			return u'episode::%s' % node_data['pk_episode']
		if isinstance(node_data, gmEMRStructItems.cEncounter):
			return u'encounter::%s' % node_data['pk_encounter']
		# unassociated episodes
		if isinstance(node_data, type({})):
			return u'dummy node::%s' % self.__pat.ID
		# root node == EMR level
		return u'root node::%s' % self.__pat.ID

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		"""Configures enabled event signals."""
		wx.EVT_TREE_SEL_CHANGED (self, self.GetId(), self._on_tree_item_selected)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self._on_tree_item_right_clicked)
		self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._on_tree_item_expanding)

		# handle tooltips
#		wx.EVT_MOTION(self, self._on_mouse_motion)
		wx.EVT_TREE_ITEM_GETTOOLTIP(self, -1, self._on_tree_item_gettooltip)

		# FIXME: xxxxx signal
		gmDispatcher.connect(signal = 'narrative_mod_db', receiver = self._on_narrative_mod_db)
		gmDispatcher.connect(signal = 'clin.episode_mod_db', receiver = self._on_episode_mod_db)
		gmDispatcher.connect(signal = 'clin.health_issue_mod_db', receiver = self._on_issue_mod_db)
		gmDispatcher.connect(signal = 'clin.family_history_mod_db', receiver = self._on_issue_mod_db)

	#--------------------------------------------------------
	def clear_tree(self):
		self.DeleteAllItems()
		self.__expanded_nodes = None

	#--------------------------------------------------------
	def __populate_tree(self):
		"""Updates EMR browser data."""
		# FIXME: auto select the previously self.__curr_node if not None
		# FIXME: error handling

		wx.BeginBusyCursor()

		if self.__pat is None:
			self.clear_tree()
			self.__expanded_nodes = None
			wx.EndBusyCursor()
			return True

		# init new tree
		root_item = self.__populate_root_node()
		self.__curr_node = root_item
		if self.__expanded_nodes is not None:
			self.ExpansionState = self.__expanded_nodes
		self.SelectItem(root_item)
		self.Expand(root_item)
		self.__update_text_for_selected_node()					# this is fairly slow, too

		wx.EndBusyCursor()
		return True
	#--------------------------------------------------------
	def __populate_root_node(self):

		self.DeleteAllItems()

		root_item = self.AddRoot(_('EMR of %(lastnames)s, %(firstnames)s') % self.__pat.get_active_name())
		self.SetItemPyData(root_item, None)
		self.SetItemHasChildren(root_item, True)

		self.__root_tooltip = self.__pat['description_gender'] + u'\n'
		if self.__pat['deceased'] is None:
			self.__root_tooltip += u' %s (%s)\n\n' % (
				self.__pat.get_formatted_dob(format = '%d %b %Y', encoding = gmI18N.get_encoding()),
				self.__pat['medical_age']
			)
		else:
			template = u' %s - %s (%s)\n\n'
			self.__root_tooltip += template % (
				self.__pat.get_formatted_dob(format = '%d.%b %Y', encoding = gmI18N.get_encoding()),
				gmDateTime.pydt_strftime(self.__pat['deceased'], '%Y %b %d'),
				self.__pat['medical_age']
			)
		self.__root_tooltip += gmTools.coalesce(self.__pat['comment'], u'', u'%s\n\n')
		doc = self.__pat.primary_provider
		if doc is not None:
			self.__root_tooltip += u'%s:\n' % _('Primary provider in this praxis')
			self.__root_tooltip += u' %s %s %s (%s)%s\n\n' % (
				gmTools.coalesce(doc['title'], gmPerson.map_gender2salutation(gender = doc['gender'])),
				doc['firstnames'],
				doc['lastnames'],
				doc['short_alias'],
				gmTools.bool2subst(doc['is_active'], u'', u' [%s]' % _('inactive'))
			)
		if not ((self.__pat['emergency_contact'] is None) and (self.__pat['pk_emergency_contact'] is None)):
			self.__root_tooltip += _('In case of emergency contact:') + u'\n'
			if self.__pat['emergency_contact'] is not None:
				self.__root_tooltip += gmTools.wrap (
					text = u'%s\n' % self.__pat['emergency_contact'],
					width = 60,
					initial_indent = u' ',
					subsequent_indent = u' '
				)
			if self.__pat['pk_emergency_contact'] is not None:
				contact = self.__pat.emergency_contact_in_database
				self.__root_tooltip += u' %s\n' % contact['description_gender']
		self.__root_tooltip = self.__root_tooltip.strip('\n')
		if self.__root_tooltip == u'':
			self.__root_tooltip = u' '

		return root_item

	#--------------------------------------------------------
	def __update_text_for_selected_node(self):
		"""Displays information for the selected tree node."""

		if self.__soap_display is None:
			return

		self.__soap_display.Clear()
		self.__img_display.clear()

		if self.__curr_node is None:
			return

		if not self.__curr_node.IsOk():
			return

		try:
			node_data = self.GetPyData(self.__curr_node)
		except wx.PyAssertionError:
			node_data = None		# fake a root node
			_log.exception('unfathomable self.GetPyData() problem occurred, faking root node')
			_log.error('real node: %s', self.__curr_node)
			_log.error('node.IsOk(): %s', self.__curr_node.IsOk())		# already survived this further up
			_log.error('is root node: %s', self.__curr_node == self.GetRootItem())
			_log.error('node.m_pItem: %s', getattr(self.__curr_node, 'm_pItem', '<NO SUCH ATTRIBUTE>'))
			_log.error('node attributes: %s', dir(self.__curr_node))
			gmLog2.log_stack_trace()

		doc_folder = self.__pat.get_document_folder()

		if isinstance(node_data, gmEMRStructItems.cHealthIssue):
			self.__cb__enable_display_mode_selection(True)
			txt = u'invalid SOAP display mode [%s]' % self.__soap_display_mode
			if self.__soap_display_mode == u'details':
				txt = node_data.format(left_margin = 1, patient = self.__pat)
				font = self.__soap_display_prop_font
			if self.__soap_display_mode == u'journal':
				txt = node_data.format_as_journal(left_margin = 1)
				font = self.__soap_display_prop_font
			if self.__soap_display_mode == u'revisions':
				txt = node_data.formatted_revision_history
				font = self.__soap_display_mono_font
			epis = node_data.episodes
			if len(epis) > 0:
				self.__img_display.refresh (
					document_folder = doc_folder,
					episodes = [ epi['pk_episode'] for epi in epis ]
				)
			self.__soap_display.SetFont(font)
			self.__soap_display.WriteText(txt)
			self.__soap_display.ShowPosition(0)
			return

		# unassociated episodes		# FIXME: turn into real dummy issue
		if isinstance(node_data, type({})):
			self.__cb__enable_display_mode_selection(True)
			if self.__soap_display_mode == u'details':
				txt = _('Pool of unassociated episodes "%s":\n') % node_data['description']
				epis = self.__pat.emr.get_episodes(unlinked_only = True, order_by = u'episode_open DESC, description')
				if len(epis) > 0:
					txt += u'\n'
				for epi in epis:
					txt += epi.format (
						left_margin = 1,
						patient = self.__pat,
						with_summary = True,
						with_codes = False,
						with_encounters = False,
						with_documents = False,
						with_hospital_stays = False,
						with_procedures = False,
						with_family_history = False,
						with_tests = False,
						with_vaccinations = False,
						with_health_issue = False
					)
					txt += u'\n'
			else:
				epis = self.__pat.emr.get_episodes(unlinked_only = True, order_by = u'episode_open DESC, description')
				txt = u''
				if len(epis) > 0:
					txt += _(' Listing of unassociated episodes\n')
				for epi in epis:
					txt += u' %s\n' % (gmTools.u_box_horiz_4dashes * 60)
					txt += epi.format (
						left_margin = 1,
						patient = self.__pat,
						with_summary = False,
						with_codes = False,
						with_encounters = False,
						with_documents = False,
						with_hospital_stays = False,
						with_procedures = False,
						with_family_history = False,
						with_tests = False,
						with_vaccinations = False,
						with_health_issue = False
					)
					txt += u'\n'
					txt += epi.format_as_journal(left_margin = 2)
			self.__soap_display.SetFont(self.__soap_display_prop_font)
			self.__soap_display.WriteText(txt)
			self.__soap_display.ShowPosition(0)
			return

		if isinstance(node_data, gmEMRStructItems.cEpisode):
			self.__cb__enable_display_mode_selection(True)
			txt = u'invalid SOAP display mode [%s]' % self.__soap_display_mode
			if self.__soap_display_mode == u'details':
				txt = node_data.format(left_margin = 1, patient = self.__pat)
				font = self.__soap_display_prop_font
			if self.__soap_display_mode == u'journal':
				txt = node_data.format_as_journal(left_margin = 1)
				font = self.__soap_display_prop_font
			if self.__soap_display_mode == u'revisions':
				txt = node_data.formatted_revision_history
				font = self.__soap_display_mono_font
			self.__img_display.refresh (
				document_folder = doc_folder,
				episodes = [ node_data['pk_episode'] ]
			)
			self.__soap_display.SetFont(font)
			self.__soap_display.WriteText(txt)
			self.__soap_display.ShowPosition(0)
			return

		if isinstance(node_data, gmEMRStructItems.cEncounter):
			self.__cb__enable_display_mode_selection(True)
			epi = self.GetPyData(self.GetItemParent(self.__curr_node))
			if self.__soap_display_mode == u'revisions':
				txt = node_data.formatted_revision_history
				font = self.__soap_display_mono_font
			else:
				txt = node_data.format (
					episodes = [epi['pk_episode']],
					with_soap = True,
					left_margin = 1,
					patient = self.__pat,
					with_co_encountlet_hints = True
				)
				font = self.__soap_display_prop_font
			self.__img_display.refresh (
				document_folder = doc_folder,
				episodes = [ epi['pk_episode'] ],
				encounter = node_data['pk_encounter']
			)
			self.__soap_display.SetFont(font)
			self.__soap_display.WriteText(txt)
			self.__soap_display.ShowPosition(0)
			return

		# root node == EMR level
		self.__cb__enable_display_mode_selection(True)
		if self.__soap_display_mode == u'details':
			emr = self.__pat.get_emr()
			txt = emr.format_summary()
		else:
			txt = self.__pat.emr.format_as_journal(left_margin = 1, patient = self.__pat)
		self.__soap_display.SetFont(self.__soap_display_prop_font)
		self.__soap_display.WriteText(txt)
		self.__soap_display.ShowPosition(0)

	#--------------------------------------------------------
	def __make_popup_menus(self):

		# - root node
		self.__root_context_popup = wx.Menu(title = _('EMR Actions:'))

		item = self.__root_context_popup.Append(-1, _('Print EMR'))
		self.Bind(wx.EVT_MENU, self.__print_emr, item)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Create health issue')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__create_issue)

		item = self.__root_context_popup.Append(-1, _('Create episode'))
		self.Bind(wx.EVT_MENU, self.__create_episode, item)

		item = self.__root_context_popup.Append(-1, _('Create progress note'))
		self.Bind(wx.EVT_MENU, self.__create_soap_editor, item)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage allergies')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__document_allergy)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage family history')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_family_history)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage hospitalizations')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_hospital_stays)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage occupation')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_occupation)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage procedures')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_procedures)

		menu_id = wx.NewId()
		self.__root_context_popup.AppendItem(wx.MenuItem(self.__root_context_popup, menu_id, _('Manage vaccinations')))
		wx.EVT_MENU(self.__root_context_popup, menu_id, self.__manage_vaccinations)

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

		# - health issues
		self.__issue_context_popup = wx.Menu(title = _('Health Issue Actions:'))

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

		item = self.__issue_context_popup.Append(-1, _('Create progress note'))
		self.Bind(wx.EVT_MENU, self.__create_soap_editor, item)

		# - episodes
		self.__epi_context_popup = wx.Menu(title = _('Episode Actions:'))

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__edit_episode)

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Delete')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__delete_episode)

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Promote')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__promote_episode_to_issue)

		item = self.__epi_context_popup.Append(-1, _('Create progress note'))
		self.Bind(wx.EVT_MENU, self.__create_soap_editor, item)

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Move encounters')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__move_encounters)

		# - encounters
		self.__enc_context_popup = wx.Menu(title = _('Encounter Actions:'))
		# - move data
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Move data to another episode')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__relink_encounter_data2episode)
		# - edit encounter details
		menu_id = wx.NewId()
		self.__enc_context_popup.AppendItem(wx.MenuItem(self.__enc_context_popup, menu_id, _('Edit details')))
		wx.EVT_MENU(self.__enc_context_popup, menu_id, self.__edit_encounter_details)

		# would require pre-configurable save-under which we don't have
		#item = self.__enc_context_popup.Append(-1, _('Create progress note'))
		#self.Bind(wx.EVT_MENU, self.__create_soap_editor, item)

		item = self.__enc_context_popup.Append(-1, _('Edit progress notes'))
		self.Bind(wx.EVT_MENU, self.__edit_progress_notes, item)

		item = self.__enc_context_popup.Append(-1, _('Move progress notes'))
		self.Bind(wx.EVT_MENU, self.__move_progress_notes, item)

		item = self.__enc_context_popup.Append(-1, _('Export for Medistar'))
		self.Bind(wx.EVT_MENU, self.__export_encounter_for_medistar, item)

	#--------------------------------------------------------
	def __handle_root_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__root_context_popup, pos)

	#--------------------------------------------------------
	def __handle_issue_context(self, pos=wx.DefaultPosition):
#		self.__issue_context_popup.SetTitle(_('Episode %s') % episode['description'])
		self.PopupMenu(self.__issue_context_popup, pos)

	#--------------------------------------------------------
	def __handle_episode_context(self, pos=wx.DefaultPosition):
#		self.__epi_context_popup.SetTitle(_('Episode %s') % self.__curr_node_data['description'])
		self.PopupMenu(self.__epi_context_popup, pos)

	#--------------------------------------------------------
	def __handle_encounter_context(self, pos=wx.DefaultPosition):
		self.PopupMenu(self.__enc_context_popup, pos)

	#--------------------------------------------------------
	# episode level
	#--------------------------------------------------------
	def __move_encounters(self, event):
		episode = self.GetPyData(self.__curr_node)

		gmNarrativeWorkflows.move_progress_notes_to_another_encounter (
			parent = self,
			episodes = [episode['pk_episode']],
			move_all = True
		)

	#--------------------------------------------------------
	def __edit_episode(self, event):
		gmEMRStructWidgets.edit_episode(parent = self, episode = self.__curr_node_data)

	#--------------------------------------------------------
	def __promote_episode_to_issue(self, evt):
		gmEMRStructWidgets.promote_episode_to_issue(parent=self, episode = self.__curr_node_data, emr = self.__pat.emr)

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

		if not gmEMRStructItems.delete_episode(episode = self.__curr_node_data):
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete episode. There is still clinical data recorded for it.'))

	#--------------------------------------------------------
	def __expand_episode_node(self, episode_node=None):
		self.DeleteChildren(episode_node)

		emr = self.__pat.emr
		epi = self.GetPyData(episode_node)
		encounters = emr.get_encounters(episodes = [epi['pk_episode']], skip_empty = True)
		if len(encounters) == 0:
			self.SetItemHasChildren(episode_node, False)
			return

		self.SetItemHasChildren(episode_node, True)

		for enc in encounters:
			label = u'%s: %s' % (
				enc['started'].strftime('%Y-%m-%d'),
				gmTools.unwrap (
					gmTools.coalesce (
						gmTools.coalesce (
							gmTools.coalesce (
								enc.get_latest_soap (				# soAp
									soap_cat = 'a',
									episode = epi['pk_episode']
								),
								enc['assessment_of_encounter']		# or AOE
							),
							enc['reason_for_encounter']				# or RFE
						),
						enc['l10n_type']							# or type
					),
					max_length = 40
				)
			)
			encounter_node = self.AppendItem(episode_node, label)
			self.SetItemPyData(encounter_node, enc)
			# we don't expand encounter nodes (what for ?)
			self.SetItemHasChildren(encounter_node, False)

		self.SortChildren(episode_node)

	#--------------------------------------------------------
	# encounter level
	#--------------------------------------------------------
	def __move_progress_notes(self, evt):
		encounter = self.GetPyData(self.__curr_node)
		node_parent = self.GetItemParent(self.__curr_node)
		episode = self.GetPyData(node_parent)

		gmNarrativeWorkflows.move_progress_notes_to_another_encounter (
			parent = self,
			encounters = [encounter['pk_encounter']],
			episodes = [episode['pk_episode']]
		)
	#--------------------------------------------------------
	def __edit_progress_notes(self, event):
		encounter = self.GetPyData(self.__curr_node)
		node_parent = self.GetItemParent(self.__curr_node)
		episode = self.GetPyData(node_parent)

		gmNarrativeWorkflows.manage_progress_notes (
			parent = self,
			encounters = [encounter['pk_encounter']],
			episodes = [episode['pk_episode']]
		)
	#--------------------------------------------------------
	def __edit_encounter_details(self, event):
		node_data = self.GetPyData(self.__curr_node)
		gmEncounterWidgets.edit_encounter(parent = self, encounter = node_data)
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

		if not gmEMRStructItems.delete_health_issue(health_issue = self.__curr_node_data):
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
	def __expand_issue_node(self, issue_node=None):
		self.DeleteChildren(issue_node)

		issue = self.GetPyData(issue_node)
		episodes = self.__pat.emr.get_episodes(issues = [issue['pk_health_issue']])
		if len(episodes) == 0:
			self.SetItemHasChildren(issue_node, False)
			return

		self.SetItemHasChildren(issue_node, True)

		for episode in episodes:
			episode_node =  self.AppendItem(issue_node, episode['description'])
			self.SetItemPyData(episode_node, episode)
			# fake it so we can expand it
			self.SetItemHasChildren(episode_node, True)

		self.SortChildren(issue_node)

	#--------------------------------------------------------
	def __expand_pseudo_issue_node(self, fake_issue_node=None):
		self.DeleteChildren(fake_issue_node)

		episodes = self.__pat.emr.unlinked_episodes
		if len(episodes) == 0:
			self.SetItemHasChildren(fake_issue_node, False)
			return

		self.SetItemHasChildren(fake_issue_node, True)

		for episode in episodes:
			episode_node =  self.AppendItem(fake_issue_node, episode['description'])
			self.SetItemPyData(episode_node, episode)
			if episode['episode_open']:
				self.SetItemBold(fake_issue_node, True)
			# fake it so we can expand it
			self.SetItemHasChildren(episode_node, True)

		self.SortChildren(fake_issue_node)

	#--------------------------------------------------------
	# EMR level
	#--------------------------------------------------------
	def __print_emr(self, event):
		gmFormWidgets.print_doc_from_template(parent = self)

	#--------------------------------------------------------
	def __create_issue(self, event):
		gmEMRStructWidgets.edit_health_issue(parent = self, issue = None)

	#--------------------------------------------------------
	def __create_episode(self, event):
		gmEMRStructWidgets.edit_episode(parent = self, episode = None)

	#--------------------------------------------------------
	def __create_soap_editor(self, event):
		self.__cb__select_edit_mode(True)
		self.__cb__add_soap_editor(problem = self.__curr_node_data, allow_same_problem = False)

	#--------------------------------------------------------
	def __document_allergy(self, event):
		dlg = gmAllergyWidgets.cAllergyManagerDlg(parent=self, id=-1)
		# FIXME: use signal and use node level update
		if dlg.ShowModal() == wx.ID_OK:
			self.__expanded_nodes = self.ExpansionState
			self.__populate_tree()
		dlg.Destroy()
		return

	#--------------------------------------------------------
	def __manage_procedures(self, event):
		gmEMRStructWidgets.manage_performed_procedures(parent = self)

	#--------------------------------------------------------
	def __manage_family_history(self, event):
		gmFamilyHistoryWidgets.manage_family_history(parent = self)

	#--------------------------------------------------------
	def __manage_hospital_stays(self, event):
		gmEMRStructWidgets.manage_hospital_stays(parent = self)

	#--------------------------------------------------------
	def __manage_occupation(self, event):
		gmDemographicsWidgets.edit_occupation()

	#--------------------------------------------------------
	def __manage_vaccinations(self, event):
		gmVaccWidgets.manage_vaccinations(parent = self)

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
		gmNarrativeWorkflows.export_narrative_for_medistar_import (
			parent = self,
			soap_cats = u'soapu',
			encounter = self.__curr_node_data
		)
	#--------------------------------------------------------
	def __expand_root_node(self):
		root_node = self.GetRootItem()
		self.DeleteChildren(root_node)

		issues = [{
			'description': _('Unattributed episodes'),
			'laterality': None,
			'diagnostic_certainty_classification': None,
			'has_open_episode': False,
			'pk_health_issue': None
		}]
		issues.extend(self.__pat.emr.health_issues)
		for issue in issues:
			issue_node =  self.AppendItem(root_node, u'%s%s%s' % (
				issue['description'],
				gmTools.coalesce(issue['laterality'], u'', u' [%s]', none_equivalents = [None, u'na']),
				gmTools.coalesce(issue['diagnostic_certainty_classification'], u'', u' [%s]')
			))
			self.SetItemBold(issue_node, issue['has_open_episode'])
			self.SetItemPyData(issue_node, issue)
			# fake it so we can expand it
			self.SetItemHasChildren(issue_node, True)

		self.SetItemHasChildren(root_node, (len(issues) != 0))
		self.SortChildren(root_node)

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_narrative_mod_db(self, *args, **kwargs):
		self.__update_text_for_selected_node()

	#--------------------------------------------------------
	def _on_episode_mod_db(self, *args, **kwargs):
		self.__expanded_nodes = self.ExpansionState
		self.__populate_tree()
	#--------------------------------------------------------
	def _on_issue_mod_db(self, *args, **kwargs):
		self.__expanded_nodes = self.ExpansionState
		self.__populate_tree()
	#--------------------------------------------------------
	def _on_tree_item_expanding(self, event):
		event.Skip()

		node = event.GetItem()
		if node == self.GetRootItem():
			self.__expand_root_node()
			return

		node_data = self.GetPyData(node)

		if isinstance(node_data, gmEMRStructItems.cHealthIssue):
			self.__expand_issue_node(issue_node = node)
			return

		if isinstance(node_data, gmEMRStructItems.cEpisode):
			self.__expand_episode_node(episode_node = node)
			return

		# pseudo node "free-standing episodes"
		if type(node_data) == type({}):
			self.__expand_pseudo_issue_node(fake_issue_node = node)
			return

		# encounter nodes do not need expanding
		#if isinstance(node_data, gmEMRStructItems.cEncounter):
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
#					gmDateTime.pydt_strftime(data['started'], '%Y %b %d'),
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
			tt = u'%s  %s  %s - %s\n' % (
				gmDateTime.pydt_strftime(data['started'], '%Y %b %d'),
				data['l10n_type'],
				data['started'].strftime('%H:%M'),
				data['last_affirmed'].strftime('%H:%M')
			)
			if data['reason_for_encounter'] is not None:
				tt += u'\n'
				tt += _('RFE: %s') % data['reason_for_encounter']
				if len(data['pk_generic_codes_rfe']) > 0:
					for code in data.generic_codes_rfe:
						tt += u'\n %s: %s%s%s\n  (%s %s)' % (
							code['code'],
							gmTools.u_left_double_angle_quote,
							code['term'],
							gmTools.u_right_double_angle_quote,
							code['name_short'],
							code['version']
						)
			if data['assessment_of_encounter'] is not None:
				tt += u'\n'
				tt += _('AOE: %s') % data['assessment_of_encounter']
				if len(data['pk_generic_codes_aoe']) > 0:
					for code in data.generic_codes_aoe:
						tt += u'\n %s: %s%s%s\n  (%s %s)' % (
							code['code'],
							gmTools.u_left_double_angle_quote,
							code['term'],
							gmTools.u_right_double_angle_quote,
							code['name_short'],
							code['version']
						)

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
			) + u'\n'
			tt += gmTools.coalesce(data['summary'], u'', u'\n%s')
			if len(data['pk_generic_codes']) > 0:
				tt += u'\n'
				for code in data.generic_codes:
					tt += u'%s: %s%s%s\n  (%s %s)\n' % (
						code['code'],
						gmTools.u_left_double_angle_quote,
						code['term'],
						gmTools.u_right_double_angle_quote,
						code['name_short'],
						code['version']
					)

			tt = tt.strip(u'\n')
			if tt == u'':
				tt = u' '

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
			tt += gmTools.coalesce(data['grouping'], u'\n', _('Grouping: %s') + u'\n')
			tt += gmTools.coalesce(data['summary'], u'', u'\n%s')
			if len(data['pk_generic_codes']) > 0:
				tt += u'\n'
				for code in data.generic_codes:
					tt += u'%s: %s%s%s\n  (%s %s)\n' % (
						code['code'],
						gmTools.u_left_double_angle_quote,
						code['term'],
						gmTools.u_right_double_angle_quote,
						code['name_short'],
						code['version']
					)

			tt = tt.strip(u'\n')
			if tt == u'':
				tt = u' '

		else:
			tt = self.__root_tooltip

		event.SetToolTip(tt)

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

		if not node1:
			_log.debug('invalid node 1')
			return 0
		if not node2:
			_log.debug('invalid node 2')
			return 0

		if not node1.IsOk():
			_log.debug('invalid node 1')
			return 0
		if not node2.IsOk():
			_log.debug('invalid node 2')
			return 0

		item1 = self.GetPyData(node1)
		item2 = self.GetPyData(node2)

		# dummy health issue always on top
		if isinstance(item1, type({})):
			return -1
		if isinstance(item2, type({})):
			return 1

		# encounters: reverse chronologically
		if isinstance(item1, gmEMRStructItems.cEncounter):
			if item1['started'] == item2['started']:
				return 0
			if item1['started'] > item2['started']:
				return -1
			return 1

		# episodes: chronologically
		if isinstance(item1, gmEMRStructItems.cEpisode):
			start1 = item1.best_guess_start_date
			start2 = item2.best_guess_start_date
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

		_log.error('unknown item type during sorting EMR tree:')
		_log.error('item1: %s', type(item1))
		_log.error('item2: %s', type(item2))

		return 0
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_patient(self):
		return self.__pat

	def _set_patient(self, patient):
		if self.__pat == patient:
			return
		self.__pat = patient
		if patient is None:
			self.clear_tree()
			return
		return self.__populate_tree()

	patient = property(_get_patient, _set_patient)
	#--------------------------------------------------------
	def _get_details_display_mode(self):
		return self.__soap_display_mode

	def _set_details_display_mode(self, mode):
		if mode not in [u'details', u'journal', u'revisions']:
			raise ValueError('details display mode must be one of "details", "journal", "revisions"')
		if self.__soap_display_mode == mode:
			return
		self.__soap_display_mode = mode
		self.__update_text_for_selected_node()

	details_display_mode = property(_get_details_display_mode, _set_details_display_mode)

#================================================================
# FIXME: still needed ?
from Gnumed.wxGladeWidgets import wxgScrolledEMRTreePnl

class cScrolledEMRTreePnl(wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl):
	"""A scrollable panel holding an EMR tree.

	Lacks a widget to display details for selected items. The
	tree data will be refetched - if necessary - whenever
	repopulate_ui() is called, e.g., when the patient is changed.
	"""
	def __init__(self, *args, **kwds):
		wxgScrolledEMRTreePnl.wxgScrolledEMRTreePnl.__init__(self, *args, **kwds)

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
		self._pnl_emr_tree._emr_tree.soap_display = self._TCTRL_item_details
		self._pnl_emr_tree._emr_tree.image_display = self._PNL_visual_soap
		self._pnl_emr_tree._emr_tree.set_enable_display_mode_selection_callback(self.enable_display_mode_selection)
		self._pnl_emr_tree._emr_tree.soap_editor_adder = self._add_soap_editor
		self._pnl_emr_tree._emr_tree.edit_mode_selector = self._select_edit_mode
		self.__register_events()

		self.editing = False
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		return True
	#--------------------------------------------------------
	def _get_editing(self):
		return self.__editing

	def _set_editing(self, editing):
		self.__editing = editing
		self.enable_display_mode_selection(enable = not self.__editing)
		if self.__editing:
			self._BTN_switch_browse_edit.SetLabel(_('&Browse %s') % gmTools.u_ellipsis)
			self._PNL_browse.Hide()
			self._PNL_visual_soap.Hide()
			self._PNL_edit.Show()
		else:
			self._BTN_switch_browse_edit.SetLabel(_('&New notes %s') % gmTools.u_ellipsis)
			self._PNL_edit.Hide()
			self._PNL_visual_soap.Show()
			self._PNL_browse.Show()
		self._PNL_right_side.GetSizer().Layout()

	editing = property(_get_editing, _set_editing)
	#--------------------------------------------------------
	# event handler
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._pnl_emr_tree._emr_tree.patient = None
		self._PNL_edit.patient = None
		return True
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		if self.GetParent().GetCurrentPage() != self:
			return True
		self.repopulate_ui()
		return True
	#--------------------------------------------------------
	def _on_show_details_selected(self, event):
		self._pnl_emr_tree._emr_tree.details_display_mode = u'details'
	#--------------------------------------------------------
	def _on_show_journal_selected(self, event):
		self._pnl_emr_tree._emr_tree.details_display_mode = u'journal'
	#--------------------------------------------------------
	def _on_show_revisions_selected(self, event):
		self._pnl_emr_tree._emr_tree.details_display_mode = u'revisions'
	#--------------------------------------------------------
	def _on_switch_browse_edit_button_pressed(self, event):
		self.editing = not self.__editing
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def repopulate_ui(self):
		"""Fills UI with data."""
		pat = gmPerson.gmCurrentPatient()
		self._pnl_emr_tree._emr_tree.patient = pat
		self._PNL_edit.patient = pat
		self._splitter_browser.SetSashPosition(self._splitter_browser.GetSizeTuple()[0]/3, True)
		return True
	#--------------------------------------------------------
	def enable_display_mode_selection(self, enable):
		if self.editing:
			enable = False
		if enable:
			self._RBTN_details.Enable(True)
			self._RBTN_journal.Enable(True)
			self._RBTN_revisions.Enable(True)
			return
		self._RBTN_details.Enable(False)
		self._RBTN_journal.Enable(False)
		self._RBTN_revisions.Enable(False)
	#--------------------------------------------------------
	def _add_soap_editor(self, problem=None, allow_same_problem=False):
		self._PNL_edit._NB_soap_editors.add_editor(problem = problem, allow_same_problem = allow_same_problem)
	#--------------------------------------------------------
	def _select_edit_mode(self, edit=True):
		self.editing = edit

#================================================================
from Gnumed.wxGladeWidgets import wxgEMRJournalPluginPnl

class cEMRJournalPluginPnl(wxgEMRJournalPluginPnl.wxgEMRJournalPluginPnl):

	def __init__(self, *args, **kwds):

		wxgEMRJournalPluginPnl.wxgEMRJournalPluginPnl.__init__(self, *args, **kwds)
		self._TCTRL_journal.disable_keyword_expansions()
		self._TCTRL_journal.SetValue(u'')
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._TCTRL_journal.SetValue(u'')
		exporter = gmPatientExporter.cEMRJournalExporter()
		if self._RBTN_by_encounter.GetValue():
			fname = exporter.export_to_file_by_encounter(patient = gmPerson.gmCurrentPatient())
		else:
			fname = exporter.export_to_file_by_mod_time(patient = gmPerson.gmCurrentPatient())

		f = io.open(fname, mode = 'rt', encoding = 'utf8', errors = 'replace')
		for line in f:
			self._TCTRL_journal.AppendText(line)
		f.close()

		self._TCTRL_journal.ShowPosition(self._TCTRL_journal.GetLastPosition())
		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		return True

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._TCTRL_journal.SetValue(u'')
		return True

	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		if self.GetParent().GetCurrentPage() != self:
			return True
		self.repopulate_ui()
		return True

	#--------------------------------------------------------
	def _on_order_by_encounter_selected(self, event):
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_order_by_last_mod_selected(self, event):
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_button_find_pressed(self, event):
		self._TCTRL_journal.show_find_dialog(title = _('Find text in EMR Journal'))

#================================================================
from Gnumed.wxGladeWidgets import wxgEMRListJournalPluginPnl

class cEMRListJournalPluginPnl(wxgEMRListJournalPluginPnl.wxgEMRListJournalPluginPnl):

	def __init__(self, *args, **kwds):

		wxgEMRListJournalPluginPnl.wxgEMRListJournalPluginPnl.__init__(self, *args, **kwds)

		self._LCTRL_journal.select_callback = self._on_row_selected
		self._TCTRL_details.SetValue(u'')

		self.__load_timer = gmTimer.cTimer(callback = self._on_load_details, delay = 1000, cookie = 'EMRListJournalPluginDBLoadTimer')

		self.__data = {}

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._LCTRL_journal.remove_items_safely()
		self._TCTRL_details.SetValue(u'')

		if self._RBTN_by_encounter.Value:		# (... is True:)
			order_by = u'c_vej.encounter_started, c_vej.pk_episode, c_vej.src_table, scr, c_vej.modified_when'
						#, c_vej.clin_when (should not make a relevant difference)
			date_col_header = _('Encounter')
			date_fields = ['encounter_started', 'modified_when']
		elif self._RBTN_by_last_modified.Value:	# (... is True:)
			order_by = u'c_vej.modified_when, c_vej.pk_episode, c_vej.src_table, scr'
						#, c_vej.clin_when (should not make a relevant difference)
			date_col_header = _('Modified')
			date_fields = ['modified_when']
		elif self._RBTN_by_item_time.Value:		# (... is True:)
			order_by = u'c_vej.clin_when, c_vej.pk_episode, c_vej.src_table, scr, c_vej.modified_when'
			date_col_header = _('Clinical time')
			date_fields = ['clin_when', 'modified_when']
		else:
			raise ValueError('invalid EMR journal list sort state')

		self._LCTRL_journal.set_columns([date_col_header, u'', _('Entry'), _('Who / When')])
		self._LCTRL_journal.set_resize_column(3)

		journal = gmPerson.gmCurrentPatient().emr.get_as_journal(order_by = order_by)

		items = []
		data = []
		self.__data = {}
		prev_date = None
		for entry in journal:
			if entry['narrative'].strip() == u'':
				continue
			soap_cat = gmSoapDefs.soap_cat2l10n[entry['soap_cat']]
			who = u'%s (%s)' % (entry['modified_by'], entry['date_modified'])
			try:
				entry_date = gmDateTime.pydt_strftime(entry[date_fields[0]], u'%Y-%m-%d')
			except KeyError:
				entry_date = gmDateTime.pydt_strftime(entry[date_fields[1]], u'%Y-%m-%d')
			if entry_date == prev_date:
				date2show = u''
			else:
				date2show = entry_date
				prev_date = entry_date
			lines = entry['narrative'].strip().split(u'\n')
			entry_line = lines[0].rstrip()
			items.append([date2show, soap_cat, entry_line, who])
			try:
				self.__data[entry['src_table']]
			except KeyError:
				self.__data[entry['src_table']] = {}
			try:
				self.__data[entry['src_table']][entry['src_pk']]
			except KeyError:
				self.__data[entry['src_table']][entry['src_pk']] = {}
				self.__data[entry['src_table']][entry['src_pk']]['entry'] = entry
				self.__data[entry['src_table']][entry['src_pk']]['formatted_instance'] = None
				if entry['encounter_started'] is None:
					enc_duration = gmTools.u_diameter
				else:
					enc_duration = u'%s - %s' % (
						gmDateTime.pydt_strftime(entry['encounter_started'], '%Y %b %d  %H:%M'),
						gmDateTime.pydt_strftime(entry['encounter_last_affirmed'], '%H:%M')
					)
				self.__data[entry['src_table']][entry['src_pk']]['formatted_header'] = _(
					u'Chart entry: %s       [#%s in %s]\n'
					u' Modified: %s by %s (%s rev %s)\n'
					u'\n'
					u'Health issue: %s%s\n'
					u'Episode: %s%s\n'
					u'Encounter: %s%s'
				) % (
					gmClinicalRecord.format_clin_root_item_type(entry['src_table']),
					entry['src_pk'],
					entry['src_table'],
					entry['date_modified'],
					entry['modified_by'],
					gmTools.u_arrow2right,
					entry['row_version'],
					gmTools.coalesce(entry['health_issue'], gmTools.u_diameter, u'%s'),
					gmTools.bool2subst(entry['issue_active'], u' (' + _('active') + u')', u' (' + _('inactive') + u')', u''),
					gmTools.coalesce(entry['episode'], gmTools.u_diameter, u'%s'),
					gmTools.bool2subst(entry['episode_open'], u' (' +  _('open') + u')', u' (' +  _('closed') + u')', u''),
					enc_duration,
					gmTools.coalesce(entry['encounter_l10n_type'], u'', u' (%s)'),
				)
				self.__data[entry['src_table']][entry['src_pk']]['formatted_root_item'] = _(
					u'%s\n'
					u'\n'
					u'                        rev %s (%s) by %s in <%s>'
				) % (
					entry['narrative'].strip(),
					entry['row_version'],
					entry['date_modified'],
					entry['modified_by'],
					entry['src_table']
				)
			data.append ({
				'table': entry['src_table'],
				'pk': entry['src_pk']
			})
			if len(lines) > 1:
				lines = lines[1:]
				idx = 0
				last_line = len(lines)
				for entry_line in lines:
					idx += 1
					if entry_line.strip() == u'':
						continue
					if idx == last_line:
						bar = gmTools.u_box_bottom_left_arc
					else:
						bar = gmTools.u_box_vert_light_4dashes
					items.append([u'', bar, entry_line.rstrip(), who])
					data.append ({
						'table': entry['src_table'],
						'pk': entry['src_pk']
					})

		self._LCTRL_journal.set_string_items(items)
		self._LCTRL_journal.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE_USEHEADER])
		self._LCTRL_journal.set_data(data)

		self._LCTRL_journal.SetFocus()
		return True

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		return True

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._LCTRL_journal.remove_items_safely()
		self._TCTRL_details.SetValue(u'')
		self.__data = {}
		return True

	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		if self.GetParent().GetCurrentPage() != self:
			return True
		self.repopulate_ui()
		return True

	#--------------------------------------------------------
	def _on_row_selected(self, evt):
		# FIXME: work on all selected
		data = self._LCTRL_journal.get_item_data(item_idx = evt.Index)
		if self.__data[data['table']][data['pk']]['formatted_instance'] is None:
			txt = _(
				u'%s\n'
				u'%s\n'
				u'%s'
			) % (
				self.__data[data['table']][data['pk']]['formatted_header'],
				gmTools.u_box_horiz_4dashes * 40,
				self.__data[data['table']][data['pk']]['formatted_root_item']
			)

			self._TCTRL_details.SetValue(txt)
			self.__load_timer.Stop()
			self.__load_timer.Start(oneShot = True)
			return

		txt = _(
			u'%s\n'
			u'%s\n'
			u'%s'
		) % (
			self.__data[data['table']][data['pk']]['formatted_header'],
			gmTools.u_box_horiz_4dashes * 40,
			self.__data[data['table']][data['pk']]['formatted_instance']
		)
		self._TCTRL_details.SetValue(txt)

	#--------------------------------------------------------
	def _on_load_details(self, cookie):
		data = self._LCTRL_journal.get_selected_item_data(only_one = True)
		if self.__data[data['table']][data['pk']]['formatted_instance'] is None:
			self.__data[data['table']][data['pk']]['formatted_instance'] = gmClinicalRecord.format_clin_root_item(data['table'], data['pk'], patient = gmPerson.gmCurrentPatient())
		txt = _(
			u'%s\n'
			u'%s\n'
			u'%s'
		) % (
			self.__data[data['table']][data['pk']]['formatted_header'],
			gmTools.u_box_horiz_4dashes * 40,
			self.__data[data['table']][data['pk']]['formatted_instance']
		)
		wx.CallAfter(self._TCTRL_details.SetValue, txt)

	#--------------------------------------------------------
	def _on_order_by_encounter_selected(self, event):
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_order_by_last_mod_selected(self, event):
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_order_by_item_time_selected(self, event):
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_order_by_item_time_selected(self, event):
		event.Skip()
		self.repopulate_ui()

	#--------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		event.Skip()

	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		event.Skip()

	#--------------------------------------------------------
#	def _on_button_find_pressed(self, event):
#		self._TCTRL_details.show_find_dialog(title = _('Find text in EMR Journal'))

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	_log.info("starting emr browser...")

	try:
		# obtain patient
		patient = gmPersonSearch.ask_for_patient()
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
	except Exception:
		_log.exception("unhandled exception caught !")
		# but re-raise them
		raise

	_log.info("closing emr browser...")

#================================================================
