"""GNUmed patient EMR tree browser widgets"""
#================================================================
__version__ = "$Revision: 2.1 $"
__author__ = "jl@leksoft.com.pl, cfmoro1976@yahoo.es, sjtan@swiftdsl.com.au, Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# std lib
import sys, types, os.path, StringIO, codecs, logging, datetime as pyDT, pprint, tempfile
import libxml2, libxslt, cgi
# 3rd party
import wx

# GNUmed libs
from Gnumed.pycommon import gmI18N, gmDispatcher, gmExceptions, gmTools, gmDateTime, gmPG2
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter, gmClinNarrative, gmForms
from Gnumed.wxpython import gmGuiHelpers, gmEMRStructWidgets, gmSOAPWidgets, gmAllergyWidgets, gmNarrativeWidgets
from Gnumed.wxGladeWidgets import wxgScrolledEMRTreePnl, wxgEMRMultiViewPnl

_log = logging.getLogger('gm.ui')
_log.info(__version__)
#--------------------------------------------------------
def get_paperwork_template_pk(template_type=u''):
	# suggested place for this function: business/gmForms.py
	# Be careful: it mathes either short or long description.
	# Currently neither short nor long description is UNIQUE:
	#    CONSTRAINT paperwork_templates_name_long_key UNIQUE (name_long, name_short)
	if template_type != u'' :
		cmd = u"""select pk_paperwork_template
			from ref.v_paperwork_templates
			where template_type=%(template_type)s"""
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'template_type': template_type}}])
		if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError, 'no template [%s]' % (template_type)
		return rows[0][0]
	else:
		return None
#================================================================
def export_emr_item(item = None, mode = "journal", header_only = False):
	"""Export single EMR item (health issue, episode, encounter or narrative) as text
	mode :  "overview"|"journal"|"changes log"
	"""
	if mode not in ["overview","journal","changes log"]:
		raise ValueError('Invalid mode: [%s]' % mode)
		return

	__output = StringIO.StringIO()
	__qs = u'\u00BB' #fancy quotes for description field
	__qe = u'\u00AB'
	# the audit trail tables start with this prefix
	audit_trail_table_prefix = u'log_'
	# and inherit from this table
	audit_trail_parent_table = u'audit_trail'
	# audited tables inherit these fields
	audit_fields_table = u'audit_fields'
	# audit stuff lives in this schema
	audit_schema = u'audit'


	if isinstance(item, gmEMRStructItems.cHealthIssue):
			if mode == "overview":
				__output.write("overview not implemented")
			elif mode == "journal":
				#get the health issue start and end time  
				cmd= u"""select min(clin_when) AS start, max(clin_when) AS end, pk_episode
							FROM clin.v_pat_items
							WHERE pk_health_issue = %(pk_health_issue)s
							GROUP BY pk_episode
							ORDER BY start"""
				rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_health_issue': item['pk_health_issue']}}])
				#this query returns 1 row even when there are no encounters within this health issue
				if len(rows) == 0:
					__start = u''
					__end = _(u'no episodes found')
				else:
					__start = min([row['start'] for row in rows]).strftime("%x")
					__end = max([row['end'] for row in rows]).strftime("%x")
				#**************
				#health issue: <health issue description> (<modified_by>)
				#   <start date> - <end date>
				__output.write(u'health issue: %s%s%s\n' % (__qs, item['description'], __qe))
				__output.write(u'   %s - %s\n' % (__start, __end))
				if not header_only:
					for _pk_episode in [row['pk_episode'] for row in rows]:
						__output.write(u'*'*20+'\n')
						__output.write(export_emr_item(gmEMRStructItems.cEpisode(aPK_obj=_pk_episode), mode))

			elif mode == "changes log":
				cmd= u"""SELECT Null AS audit_action, Null AS audit_when, Null AS audit_by, 
						pk_audit, row_version, modified_when, modified_by, pk, 
						description, laterality, age_noted, is_active, clinically_relevant, 
						is_confidential, is_cause_of_death, fk_encounter
				  	FROM clin.health_issue
					WHERE pk = %(pk_health_issue)s
					UNION ALL
					SELECT audit_action, audit_when, audit_by, 
						 pk_audit, row_version, modified_when, modified_by, 
						 pk, description, laterality, age_noted, is_active, 
						 clinically_relevant, is_confidential, is_cause_of_death, fk_encounter
					FROM audit.log_health_issue
					WHERE pk_audit = (SELECT pk_audit FROM clin.health_issue WHERE pk = %(pk_health_issue)s)
					ORDER BY row_version DESC
					"""
				rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_health_issue': item['pk_health_issue']}}], get_col_idx=True)
				__output.write(u'health issue: %s%s%s\n\n' % (__qs, item['description'], __qe))
				__fields_ordered = [ key for (key, value) in sorted(idx.items(), key=lambda (x, y): y)]
				__current_version = {}
				for col in __fields_ordered[3:]: #skip first 3 fields
					__current_version[col] = rows[0][col]
				__output.write(u'-'*20+'\n')
				__output.write(u'\ncurrent values:\n')
				__output.write(pprint.pformat(__current_version))	#NOTE: pprint.pformat automatically sorts dictionary
				__output.write(u'\n')
				if __current_version['row_version'] == 0:
					__output.write(u'-'*20+'\n')
					__output.write(u'no previous versions of this record')
				else:
					cols={}
					for col in __fields_ordered:
						cols[col] = [ row[col] for row in rows ]
					__output.write(u'-'*20+'\n')
					__output.write(u'\nall values with <audit_action>, <audit_when>, <audit_by> fields (current value first):\n')
					__output.write(u'\n'+pprint.pformat(cols)+'\n')
	elif isinstance(item, gmEMRStructItems.cEpisode):
			if mode == "overview":
				__output.write("overview not implemented")
			elif mode == "journal":
				#get the encounters with start and end time  
				cmd= u"""SELECT min(clin_when) AS start, max(clin_when) as end, pk_encounter 
							FROM clin.v_pat_items
							WHERE pk_episode = %(pk_episode)s
							GROUP BY pk_encounter
							ORDER BY start
							"""
				rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_episode': item['pk_episode']}}])
				if len(rows) == 0:
					__start = u''
					__end = _(u'no encounters found')
					_log.info(u'episode %s without encounters' % item['pk_episode'])
				else:
					__start = min([row['start'] for row in rows]).strftime("%x")
					__end = max([row['end'] for row in rows]).strftime("%x")
				#**************
				#episode: <episode description> (<modified_by>)
				#   <start date> - <end date>
				#__output.write(u'**********************\n')
				#__output.write(u'episode: %s (%s, %s)\n' % (item['description'], item['episode_modified_by'], item['episode_modified_when'].strftime("%x %H:%M")))
				__output.write(u'episode: %s%s%s\n' % (__qs, item['description'], __qe))
				__output.write(u'   %s - %s\n' % (__start, __end))
				if not header_only:
					for _pk_encounter in [row['pk_encounter'] for row in rows]:
						__output.write((u'='*20)+'\n')
						__output.write(export_emr_item(gmEMRStructItems.cEncounter(aPK_obj=_pk_encounter), mode))

			elif mode == "changes log":
				cmd= u"""SELECT Null AS audit_action, Null AS audit_when, Null AS audit_by, 
						pk_audit, row_version, modified_when, modified_by, 
						pk, fk_health_issue, description, is_open, fk_encounter
					FROM clin.episode
				  	WHERE pk = %(pk_episode)s
					UNION ALL
					SELECT audit_action, audit_when, audit_by, 
						pk_audit, row_version, modified_when, modified_by, 
						pk, fk_health_issue, description, is_open, fk_encounter
					FROM audit.log_episode
					WHERE pk_audit = (SELECT pk_audit FROM clin.episode WHERE pk = %(pk_episode)s)
					ORDER BY row_version DESC
					"""
				rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_episode': item['pk_episode']}}], get_col_idx=True)
				__output.write(u'episode: %s%s%s\n\n' % (__qs, item['description'], __qe))
				__fields_ordered = [ key for (key, value) in sorted(idx.items(), key=lambda (x, y): y)]
				__current_version = {}
				for col in __fields_ordered[3:]: #skip first 3 fields
					__current_version[col] = rows[0][col]
				__output.write(u'-'*20+'\n')
				__output.write(u'\ncurrent values:\n')
				__output.write(pprint.pformat(__current_version))	#NOTE: pprint.pformat automatically sorts dictionary
				__output.write(u'\n')
				if __current_version['row_version'] == 0:
					__output.write(u'-'*20+'\n')
					__output.write(u'no previous versions of this record')
				else:
					cols={}
					for col in __fields_ordered:
						cols[col] = [ row[col] for row in rows ]
					__output.write(u'-'*20+'\n')
					__output.write(u'\nall values with <audit_action>, <audit_when>, <audit_by> fields (current value first):\n')
					__output.write(u'\n'+pprint.pformat(cols)+'\n')
	elif isinstance(item, gmEMRStructItems.cEncounter):
			if mode == "overview":
				__output.write("overview not implemented")
			elif mode == "journal":
				#======================
				#   <started> - <ENC type> (<provider>, <modified_when>)
				#__output.write(u'======================\n')
				__output.write("%s - %s   (%s, %s)\n" % (item['started'].strftime("%x"), item['l10n_type'], item['provider'], item['modified_when'].strftime("%x %H:%M")))
				#__output.write(u'-'*20+'\n')
				if not item['reason_for_encounter'] is None:
					__output.write("   RFE: %s\n" % item['reason_for_encounter'])
				if not item['assessment_of_encounter'] is None:
					__output.write("   AOE: %s\n" % item['assessment_of_encounter'])
				#__output.write("\n")
				if not header_only:
					#get narratives
					cmd= u"""SELECT vpi.soap_cat, vpi.narrative
								FROM clin.v_pat_items vpi
								JOIN clin.soap_cat_ranks scr ON vpi.soap_cat = scr.soap_cat
								WHERE pk_encounter = %(pk_encounter)s
								ORDER BY scr.rank, vpi.clin_when
								"""
					rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_encounter': item['pk_encounter']}}])
					for _narrative in rows:
						__output.write(u'\n-- ' + gmClinNarrative.soap_cat2l10n_str[_narrative['soap_cat']] + ':\n')
						__output.write(gmTools.coalesce(_narrative['narrative'], u'')+'\n')
			elif mode == "changes log":
				cmd= u"""SELECT Null AS audit_action, Null AS audit_when, Null AS audit_by,
						pk_audit, row_version, modified_when, modified_by, 
						pk, fk_patient, fk_type, fk_location, source_time_zone, 
						reason_for_encounter, assessment_of_encounter, started, last_affirmed
					FROM clin.encounter
					WHERE pk = %(pk_encounter)s
					UNION ALL
					SELECT audit_action, audit_when, audit_by, 
						pk_audit, orig_version, orig_when, orig_by, 
						pk, fk_patient, fk_type, fk_location, source_time_zone, 
								 reason_for_encounter, assessment_of_encounter, started, last_affirmed
					FROM audit.log_encounter
					WHERE pk_audit = (SELECT pk_audit FROM clin.encounter WHERE pk = %(pk_encounter)s)
					ORDER BY row_version DESC
					"""
				rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_encounter': item['pk_encounter']}}], get_col_idx=True)
				__output.write(u'encounter: %s%s%s\n\n' % (__qs, item['type'], __qe))
				__fields_ordered = [ key for (key, value) in sorted(idx.items(), key=lambda (x, y): y)]
				__current_version = {}
				for col in __fields_ordered[3:]: #skip first 3 fields
					__current_version[col] = rows[0][col]
				__output.write(u'-'*20+'\n')
				__output.write(u'\ncurrent values:\n')
				__output.write(pprint.pformat(__current_version))	#NOTE: pprint.pformat automatically sorts dictionary
				__output.write(u'\n')
				if __current_version['row_version'] == 0:
					__output.write(u'-'*20+'\n')
					__output.write(u'no previous versions of this record')
				else:
					cols={}
					for col in __fields_ordered:
						cols[col] = [ row[col] for row in rows ]
					__output.write(u'-'*20+'\n')
					__output.write(u'\nall values with <audit_action>, <audit_when>, <audit_by> fields (current value first):\n')
					__output.write(u'\n'+pprint.pformat(cols)+'\n')
				if not header_only:
					__output.write('\n'+u'='*20+u'\n  narratives\n'+u'='*20)
					#get narratives
					cmd= u"""SELECT vpi.pk_item, vpi.src_table, vpi.soap_cat
								FROM clin.v_pat_items vpi
								JOIN clin.soap_cat_ranks scr ON vpi.soap_cat = scr.soap_cat
								WHERE pk_encounter = %(pk_encounter)s
								ORDER BY scr.rank, vpi.clin_when
								"""
					narratives, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_encounter': item['pk_encounter']}}])
					print narratives #DEBUG
					for __narrative in narratives:
						print __narrative #DEBUG
						__output.write('\n\n'+u'-'*20)
						__output.write(u'\n-- ' + gmClinNarrative.soap_cat2l10n_str[__narrative['soap_cat']] + ':\n')
						# select current table
						_schema, _table = __narrative['src_table'].split( '.')
						cols_source = gmPG2.get_col_names(schema = _schema, table = _table)
						print cols_source #DEBUG
						cols_inherited = gmPG2.get_col_names(schema = audit_schema, table = audit_fields_table)
						cols_data = []
						for col in cols_source:
							if col not in cols_inherited:
								cols_data.append(col)
						cmd = u'SELECT  Null AS audit_action, Null AS audit_when, Null AS audit_by, \n'
						cmd += u', '.join(cols_source)
						cmd += u'\nFROM  %s\n'% __narrative['src_table']
						cmd += u"""WHERE pk_item = %(pk_item)s
							UNION ALL
							SELECT audit_action, audit_when, audit_by, 
							pk_audit, orig_version, orig_when, orig_by, 
							"""
						cmd += u', '.join(cols_data)
						cmd += u'\nFROM %s.%s%s \n' % (audit_schema, audit_trail_table_prefix, _table)
						cmd += u'WHERE pk_audit = (SELECT pk_audit FROM %s ' % __narrative['src_table']
						cmd += u'WHERE pk_item = %(pk_item)s ) ' 
						cmd += u'\nORDER BY row_version DESC'
						rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk_item': __narrative['pk_item']}}], get_col_idx=True)
						__fields_ordered = [ key for (key, value) in sorted(idx.items(), key=lambda (x, y): y)]
						__current_version = {}
						for col in __fields_ordered[3:]: #skip first 3 fields
							__current_version[col] = rows[0][col]
						__output.write(u'-'*20+'\n')
						__output.write(u'\ncurrent values:\n')
						__output.write(pprint.pformat(__current_version))	#NOTE: pprint.pformat automatically sorts dictionary
						__output.write(u'\n')
						if __current_version['row_version'] == 0:
							__output.write(u'-'*20+'\n')
							__output.write(u'no previous versions of this record')
						else:
							cols={}
							for col in __fields_ordered:
								cols[col] = [ row[col] for row in rows ]
							__output.write(u'-'*20+'\n')
							__output.write(u'\nall values with <audit_action>, <audit_when>, <audit_by> fields (current value first):\n')
							__output.write(u'\n'+pprint.pformat(cols)+'\n')
						# select audit table
	else:
			if mode == "overview":
				__output.write("overview of EMR not implemented, select another item")
			elif mode == "journal":
				__output.write("journal of EMR not implemented, select another item")
			elif mode == "changes log":
				__output.write("changes of EMR not implemented, select another item")
	return __output.getvalue()
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
	def repopulate_ui(self):
		self.refresh()
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
		#self.__update_text_for_selected_node()

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
# define a class for HTML forms (for printing)
#================================================================
class cFormXML(gmForms.cFormEngine):
	"""This class can create XML document from placeholders and supplied data,
	then process it with XSLT template and display results
	"""
	_preview_program = u'oowriter '	#this program must be in the system PATH
	def __init__ (self, template=None):
		self._FormData = None
		if template is None:
			_log.error(u'%s: cannot create form instance without a template' % __name__)
			return
		gmForms.FormEngine.__init__(self, template = template)
		self._XSLTData = template.get_data()
		#FIXME: what about encoding conversions?
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def process(self, placeholders_data):
		"""replaces placeholders with supplied data"""
		#"""make XML file from dictionary"""

		__header = '<?xml version="1.0" encoding="UTF-8"?>\n'
		__body = u''
		for (key, value) in placeholders_data.items():
			__body += u'<%(key)s>%(value)s</%(key)s>\n' % {'key': key, 'value' : cgi.escape(value)}
		self._XMLData =__header.encode('utf-8') + __body.encode('utf-8')
		#"""process XML data according to supplied XSLT, producing HTML"""

		styledoc = libxml2.parseDoc(self._XSLTData)
		style = libxslt.parseStylesheetDoc(styledoc)
		doc = libxml2.parseDoc(self._XMLData)
		result = style.applyStylesheet(doc, None)
		self._FormData = result.serialize()

		style.freeStylesheet()
		doc.freeDoc()
		result.freeDoc()
	#--------------------------------------------------------
	def preview(self):
		if self._FormData is None:
			raise ValueError, u'Previev request for empty form. Make sure the form is properly initialized and process() was performed'
		print "creating temp file"
		try:
			_handle, self.filename = tempfile.mkstemp('.html', 'gm-report-', text = True)

			os.write(_handle, self._FormData.encode('UTF-8'))
		except:
			print "no temp file"
			_log.error('%s: cannot write to temporary file' % __name__)
			return
		os.close(_handle)
		_command = self.__class__._preview_program + self.filename
		try:
			#os.spawnl(os.P_NOWAIT, 'swriter', 'swriter', filename)
			os.system(_command)
		except:
			_log.error('%s: cannot launch report preview program' % __name__)
		#os.unlink(self.filename) #delete file
		#FIXME: under Windows the temp file is deleted before preview program gets it (under Linux it works OK) 
	#--------------------------------------------------------
	def print_directly(self):
		#not so fast, look at it first
		self.preview()
class cFormTemplate(gmForms.cFormTemplate):
	"""add get_data function"""
	def get_data(self):
		"""Returns template data as string"""
		cmd = u'SELECT data FROM ref.paperwork_templates WHERE pk = %(pk)s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError, 'Cannot get data for template pk = %s' % (self.pk_obj)
			return
		return unicode(str(rows[0][0]), 'UTF-8')	# FIXME: why this conversion is needed?
#============================================================
class cSplittedEMRTreeBrowserPnl(wxgEMRMultiViewPnl.wxgEMRMultiViewPnl):
	"""A splitter window holding an EMR tree.

	The left hand side displays a scrollable EMR tree while
	on the right details for selected items are displayed.

	Expects to be put into a Notebook.
	"""
	def __init__(self, *args, **kwds):
		wxgEMRMultiViewPnl.wxgEMRMultiViewPnl.__init__(self, *args, **kwds)

		#self._pnl_emr_tree._emr_tree.set_narrative_display(narrative_display = self._item_details)
		#self._pnl_emr_tree.set_narrative_display(narrative_display = self._item_details)
		self.__patient = gmPerson.gmCurrentPatient()
		self.__emr = self._pnl_emr_tree
		self.__register_events()
		self.__curr_node = self.__emr.GetRootItem()
		if self.__patient.connected:
			self.__show_details_for_selected_node()
	#--------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		wx.EVT_TREE_SEL_CHANGED (self._pnl_emr_tree, self._pnl_emr_tree.GetId(), self._on_tree_item_selected)
		wx.EVT_RADIOBOX( self, self._view_type.GetId(), self._on_view_type_selected)
		return True
	#--------------------------------------------------------
	def __show_details_for_selected_node(self, node = None):
		"""If selected node is an encounter, displays detailed information and corresponding narrative"""
		if node is None:
			node = self.__curr_node	#FIXME: how to make this default in the definition line?
		node_data = self.__emr.GetPyData(node)
		__patient_name = self.__patient.get_active_name()
		# update displayed text
		header = u'*** EMR %s generated %s ***\n' % (self._view_type.GetStringSelection(), pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone).strftime("%x %X"))
		header += u'______________________\n\n'
		header += u'   patient: %s %s\n' % (__patient_name['lastnames'], __patient_name['firstnames'])
		header += u'______________________\n\n'
		footer = u'\n*** end of EMR %s ***' % self._view_type.GetStringSelection()

		if self._view_type.GetStringSelection() == "overview":
			#preserve previous method of generating output 
			if isinstance(node_data, (gmEMRStructItems.cHealthIssue, types.DictType)):
				# FIXME: turn into real dummy issue
				if node_data['pk_health_issue'] is None:
					txt = _('Pool of unassociated episodes:\n\n  "%s"') % node_data['description']
				else:
					txt = node_data.format(left_margin=1, patient = self.__patient)

			elif isinstance(node_data, gmEMRStructItems.cEpisode):
				txt = node_data.format(left_margin = 1, patient = self.__patient)

			elif isinstance(node_data, gmEMRStructItems.cEncounter):
				epi = self.__emr.GetPyData(self.__emr.GetItemParent(node))
				txt = node_data.format(episodes = [epi['pk_episode']], with_soap = True, left_margin = 1, patient = self.__patient)

			else:
				emr = self.__patient.get_emr()
				txt = emr.format_summary()

		else:
			#new method of generating output 
			txt = export_emr_item(item = node_data, mode = self._view_type.GetStringSelection()) 

		self._item_details.Clear()
		self._item_details.WriteText(header + txt + footer)
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		sel_item = event.GetItem()
		self.__curr_node = sel_item
		self.__show_details_for_selected_node(self.__curr_node)

		return True
	def _on_view_type_selected(self, event):
		#just repaint current node
		# __show_details_for_selected_node checks for value of this RadioBox itself
		self.__show_details_for_selected_node(self.__curr_node)
	#--------------------------------------------------------
	def _print_btn_pressed(self, event): # wxGlade: wxgEncounterEditPnl.<event_handler>
			data = {
				'text': self._item_details.GetValue()
				}
			__template_type = "print.plain_text"
			template = cFormTemplate(aPK_obj=get_paperwork_template_pk(template_type=__template_type))
			self.__form = cFormXML(template = template)
			self.__form.process(placeholders_data = data)
			self.__form.preview()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		if self.GetParent().GetCurrentPage() == self:
			self.repopulate_ui()
		return True
	#--------------------------------------------------------
	def repopulate_ui(self):
		"""Fills UI with data."""
		self._pnl_emr_tree.repopulate_ui()
		#self._splitter_browser.SetSashPosition(self._splitter_browser.GetSizeTuple()[0]/3, True)
		return True

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	print "no test code, but it can be tested using gmEMRMultiViewPlugin"

#================================================================
# $Log: gmEMRMultiViewWidgets.py,v $
# Revision 2.1  2009/08/25 02:25:01  jl
# - first version after changing name from gmEMRBrowser
# - added radiobox for selecting view as "summary", "journal" or "changes log"
# - added print button for right pane
#
# Revision 1.93.2.2  2008/10/12 17:02:59  ncq
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
