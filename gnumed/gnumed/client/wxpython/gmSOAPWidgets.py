"""GnuMed SOAP related widgets.

The code in here is independant of gmPG.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmSOAPWidgets.py,v $
# $Id: gmSOAPWidgets.py,v 1.73 2006-06-20 14:26:36 ncq Exp $
__version__ = "$Revision: 1.73 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std library
import types

# 3rd party
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmI18N, gmLog, gmExceptions, gmMatchProvider
from Gnumed.wxpython import gmResizingWidgets, gmPhraseWheel, gmEMRStructWidgets, gmGuiHelpers, gmRegetMixin, gmMultiSash, gmVaccWidgets, gmEditArea
from Gnumed.business import gmPerson, gmEMRStructItems, gmSOAPimporter

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
def create_issue_popup(parent, pos, size, style, data_sink):
	ea = gmEMRStructWidgets.cHealthIssueEditArea (
		parent,
		-1,
		wx.DefaultPosition,
		wx.DefaultSize,
		wx.NO_BORDER | wx.TAB_TRAVERSAL,
		data_sink = data_sink
	)
	popup = gmEditArea.cEditAreaPopup (
		parent = parent,
		id = -1,
		title = '',
		pos = pos,
		size = size,
		style = style,
		name = '',
		edit_area = ea
	)
	return popup
#============================================================
def create_vacc_popup(parent, pos, size, style, data_sink):
	ea = gmVaccWidgets.cVaccinationEditArea (
		parent = parent,
		id = -1,
      	pos = pos,
		size = size,
		style = style,
		data_sink = data_sink
	)
	popup = gmEditArea.cEditAreaPopup (
		parent = parent,
		id = -1,
		title = _('Enter vaccination given'),
		pos = pos,
		size = size,
		style = style,
		name = '',
		edit_area = ea
	)
	return popup
#============================================================
# FIXME: keywords hardcoded for now, load from cfg in backend instead
progress_note_keywords = {
	's': {
		'$missing_action': {},
		'phx': {
			'widget_factory': create_issue_popup,
			'widget_data_sink': None
		},
		'ea:': {
			'widget_factory': create_issue_popup,
			'widget_data_sink': None
		},
		'$vacc': {
			'widget_factory': create_vacc_popup,
			'widget_data_sink': None
		},
		'impf:': {
			'widget_factory': create_vacc_popup,
			'widget_data_sink': None
		},
		'icpc:': {},
		'icpc?': {}
	},
	'o': {
		'icpc:': {},
		'icpc?': {}
	},
	'a': {
		'icpc:': {},
		'icpc?': {}
	},
	'p': {
		'$vacc': {
			'widget_factory': create_vacc_popup,
			'widget_data_sink': None
		},
		'icpc:': {},
		'icpc?': {}
	}
}
#============================================================
class cProgressNoteInputNotebook(wx.Notebook, gmRegetMixin.cRegetOnPaintMixin):
	"""Notebook style widget displaying progress note editors.
	"""
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize):
		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			pos = pos,
			size = size,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER | wx.VSCROLL | wx.HSCROLL,
			name = self.__class__.__name__
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pat = gmPerson.gmCurrentPatient()
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def add_editor(self, problem=None):
		"""Add a progress note editor page."""
		label = _('new episode')
		if problem is not None:
			emr = self.__pat.get_emr()
			if isinstance(problem, gmEMRStructItems.cEpisode):
				problem = emr.episode2problem(episode = problem)
			elif isinstance(problem, gmEMRStructItems.cHealthIssue):
				problem = emr.health_issue2problem(issue = problem)
			if isinstance(problem, gmEMRStructItems.cProblem):
				label = problem['problem']
			else:
				_log.Log(gmLog.lErr, 'cannot open progress note editor for [%s] (TypeError)' % str(problem))
				return False
			# FIXME: configure length
			if len(label) > 23:
				label = label[:20] + '...'
		new_page = cResizingSoapPanel(parent = self, problem = problem)
		return self.AddPage (
			page = new_page,
			text = label,
			select = True
		)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __do_layout(self):
		# add one empty unassociated progress note editor - which to
		# have (by all sensible accounts) seems to be the intent when
		# instantiating this class
		self.add_editor()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		print '[%s._populate_with_data] nothing to do, really...' % self.__class__.__name__
		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.pre_patient_selection(), receiver=self._on_pre_patient_selection)
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._on_post_patient_selection)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self._on_episodes_modified)
		gmDispatcher.connect(signal=gmSignals.application_closing(), receiver=self._on_application_closing)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		"""Another patient is about to be activated."""
#		print "[%s]: another patient is about to become active" % self.__class__.__name__
#		print "need code to:"
#		print "- ask user about unsaved progress notes"
		pass
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Patient changed."""
		self.DeleteAllPages()
		self.add_editor()
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_episodes_modified(self):
#		print "[%s]: episode modified" % self.__class__.__name__
#		print "need code to deal with:"
#		print "- deleted episode that we show so we can notify the user"
#		print "- renamed episode so we can update our episode label"
#		self._schedule_data_reget()
		pass
	#--------------------------------------------------------
	def _on_application_closing(self):
		"""Patient changed."""
#		print "[%s]: the application is closing down" % self.__class__.__name__
#		print "need code to:"
#		print "- ask user about unsaved data"
		pass
#============================================================
class cNotebookedProgressNoteInputPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""A progress note input panel.

	Left hand side:
	- problem list (health issues and active episodes)

	Right hand side:
	- progress note editors notebook
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""Contructs a new instance of SOAP input panel

		@param parent: Wx parent widget
		@param id: Wx widget id
		"""
		# Call parents constructors
		wx.Panel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.NO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()

		# ui contruction and event handling set up
		self.__do_layout()
		self.__register_interests()
		self.reset_ui_content()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def reset_ui_content(self):
		"""
		Clear all information from input panel
		"""
		self.__LST_problems.Clear()
		self.__soap_notebook.DeleteAllPages()
		self.__soap_notebook.add_editor()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.

		left: problem list (mix of issues and episodes)
		right: soap editors
		"""
		# SOAP input panel main splitter window
		self.__splitter = wx.SplitterWindow(self, -1)

		# left hand side
		PNL_list = wx.Panel(self.__splitter, -1)
		# - header
		list_header = wx.StaticText (
			parent = PNL_list,
			id = -1,
			label = _('Active Problems'),
			style = wx.NO_BORDER | wx.ALIGN_CENTRE
		)
		# - problem list
		self.__LST_problems = wx.ListBox (
			PNL_list,
			-1,
			style= wx.NO_BORDER
		)
		# - arrange
		szr_left = wx.BoxSizer(wx.VERTICAL)
		szr_left.Add(list_header, 0)
		szr_left.Add(self.__LST_problems, 1, wx.EXPAND)
		PNL_list.SetSizerAndFit(szr_left)

		# right hand side
		# - soap inputs panel
		PNL_soap_editors = wx.Panel(self.__splitter, -1)
		# - progress note notebook
		self.__soap_notebook = cProgressNoteInputNotebook(PNL_soap_editors, -1)
		# - buttons
		self.__BTN_add_unassociated = wx.Button(PNL_soap_editors, -1, _('&New'))
		self.__BTN_add_unassociated.SetToolTipString(_('add editor for new unassociated progress note'))

		self.__BTN_clear = wx.Button(PNL_soap_editors, -1, _('&Reset'))
		self.__BTN_clear.SetToolTipString(_('clear progress note editor'))

		self.__BTN_save = wx.Button(PNL_soap_editors, -1, _('&Save'))
		self.__BTN_save.SetToolTipString(_('save progress note into medical record'))

#		self.__BTN_discard = wx.Button(PNL_soap_editors, -1, _('&Discard'))
#		self.__BTN_discard.SetToolTipString(_('Discard progress note and close editor. This will loose any data you already typed into this editor !'))

		# - arrange
		szr_btns_right = wx.BoxSizer(wx.HORIZONTAL)
		szr_btns_right.Add(self.__BTN_add_unassociated, 0, wx.SHAPED)
		szr_btns_right.Add(self.__BTN_clear, 0, wx.SHAPED)
		szr_btns_right.Add(self.__BTN_save, 0, wx.SHAPED)
#		szr_btns_right.Add(self.__BTN_discard, 0, wx.SHAPED)

		szr_right = wx.BoxSizer(wx.VERTICAL)
		szr_right.Add(self.__soap_notebook, 1, wx.EXPAND)
		szr_right.Add(szr_btns_right)
		PNL_soap_editors.SetSizerAndFit(szr_right)

		# arrange widgets
		self.__splitter.SetMinimumPaneSize(20)
		self.__splitter.SplitVertically(PNL_list, PNL_soap_editors)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__splitter, 1, wx.EXPAND, 0)
		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	def __refresh_problem_list(self):
		"""Update health problems list.
		"""
		self.__LST_problems.Clear()
		emr = self.__pat.get_emr()
		problems = emr.get_problems()
		for problem in problems:
			if not problem['problem_active']:
				continue
			if problem['type'] == 'issue':
				issue = emr.problem2issue(problem)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk'])
				if last_encounter is None:
					last = issue['modified_when'].Format('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].Format('%m/%Y')
			elif problem['type'] == 'episode':
				epi = emr.problem2episode(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].Format('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].Format('%m/%Y')
			item = _('%s "%s" (%s)') % (last, problem['problem'], problem['l10n_type'])
			self.__LST_problems.Append(item, problem)
		splitter_width = self.__splitter.GetSizeTuple()[0]
		self.__splitter.SetSashPosition((splitter_width / 2), True)
		return True
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
#		wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self.__on_discard)
		wx.EVT_BUTTON(self.__BTN_add_unassociated, self.__BTN_add_unassociated.GetId(), self.__on_add_unassociated)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._on_post_patient_selection)
		gmDispatcher.connect(signal=gmSignals.episodes_modified(), receiver=self._on_episodes_modified)
		# FIXME: issues modified missing
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Patient changed."""
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_episodes_modified(self):
		# FIXME: this should rather *schedule* a reget which would
		# FIXME: then happen immediately in visible widgets
		self._schedule_data_reget()
	#--------------------------------------------------------
	def __on_clear(self, event):
		"""Clear raised SOAP input widget.
		"""
		soap_nb_page = self.__soap_notebook.GetPage(self.__soap_notebook.GetSelection())
		soap_nb_page.Clear()
	#--------------------------------------------------------
	def __on_discard(self, event):
		"""Discard raised SOAP input widget.

		Will throw away data !
		"""
		self.__soap_notebook.DeletePage(self.__soap_notebook.GetSelection())
	#--------------------------------------------------------
	def __on_add_unassociated(self, evt):
		"""Add new editor for as-yet unassociated progress note.
		"""
		self.__soap_notebook.add_editor()
	#--------------------------------------------------------
	def __on_problem_activated(self, event):
		"""
		When the user changes health issue selection, update selected issue
		reference and update buttons according its input status.

		when the user selects a problem in the problem list:
			- check whether selection is issue or episode
			- if editor for episode exists: focus it
			- if no editor for episode exists: create one and focus it
		"""
		problem_idx = self.__LST_problems.GetSelection()
		problem = self.__LST_problems.GetClientData(problem_idx)
		emr = self.__pat.get_emr()

		title = _('opening progress note editor')
		msg = _('Cannot open progress note editor for\n\n'
				'[%s].\n\n') % problem['problem']

		if problem['type'] == 'issue':
			# health issue selected: user wants to start new episode
			if self.__soap_notebook.add_editor(problem = problem):
				# FIXME: ask whether closing "previous" episodes for issue
				return True
			gmGuiHelpers.gm_show_error(aMessage = msg, aTitle = title)
			return False

		# must be episode, then
		# editor for it already there ?
		for page_idx in range(self.__soap_notebook.GetPageCount()):
			page = self.__soap_notebook.GetPage(page_idx)
			pnl_problem = page.get_problem()
			# skip unassociated
			if pnl_problem is None:
				continue
			# skip issues
			if pnl_problem['type'] != 'episode':
				continue
			if pnl_problem['pk_episode'] == problem['pk_episode']:
				# yes, so raise that editor (returns idx of old page)
				self.__soap_notebook.SetSelection(page_idx)
				return True

		# no, add editor for episode
		if self.__soap_notebook.add_editor(problem = problem):
			return True
		gmGuiHelpers.gm_show_error(aMessage = msg, aTitle = title)
		return False
	#--------------------------------------------------------
	def __on_save(self, event):
		"""Save data to backend and close editor.
		"""
		page_idx = self.__soap_notebook.GetSelection()
		soap_nb_page = self.__soap_notebook.GetPage(page_idx)
		if not soap_nb_page.save():
			return False
		self.__soap_notebook.DeletePage(page_idx)
		self.__refresh_problem_list()
		return True
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
#		self.reset_ui_content()
		if self.__refresh_problem_list():
			return True
		return False
#============================================================
class cSOAPLineDef:
	def __init__(self):
		self.label = _('label missing')
		self.text = ''
		self.soap_cat = _('soap cat missing')
		self.is_rfe = False		# later support via types
		self.data = None
#============================================================
# FIXME: this should be a more generic(ally named) class
# FIXME: living elsewhere
class cPopupDataHolder:

	_data_savers = {}

	def __init__(self):
		self.__data = {}
	#--------------------------------------------------------
	def store_data(self, popup_type=None, desc=None, data=None, old_desc=None):
		# FIXME: do fancy validations

		print "storing popup data:", desc
		print "type", popup_type
		print "data", data

		# verify structure
		try:
			self.__data[popup_type]
		except KeyError:
			self.__data[popup_type] = {}
		# store new data
		self.__data[popup_type][desc] = {
			'data': data
		}
		# remove old data if necessary
		try:
			del self.__data[popup_type][old_desc]
		except:
			pass
		return True
	#--------------------------------------------------------
	def save(self):
		for popup_type in self.__data.keys():
			try:
				saver_func = self.__data_savers[popup_type]
			except KeyError:
				_log.LogException('no saver for popup data type [%s] configured' % popup_type)
				return False
			for desc in self.__data[popup_type].keys():
				data = self.__data[popup_type][desc]['data']
				saver_func(data)
		return True
	#--------------------------------------------------------
	def clear(self):
		self.__data = {}
	#--------------------------------------------------------
#	def remove_data(self, popup_type=None, desc=None):
#		del self.__data[popup_type][desc]
	#--------------------------------------------------------
	# def get_descs(self, popup_type=None, origination_soap=None):
	# def get_data(self, desc=None):
	# def rename_data(self, old_desc=None, new_desc=None):
#============================================================
class cResizingSoapWin (gmResizingWidgets.cResizingWindow):

	def __init__(self, parent, size, input_defs=None, problem=None):
		"""Resizing SOAP note input editor.

		This is a wrapper around a few resizing STCs (the
		labels and categories are settable) which are
		customized to accept progress note input. It provides
		the unified resizing behaviour.

		Knows how to save it's data into the backend.

		@param input_defs: note's labels and categories
		@type input_defs: list of cSOAPLineDef instances
		"""
		if input_defs is None or len(input_defs) == 0:
			raise gmExceptions.ConstructorError, 'cannot generate note with field defs [%s]' % input_defs

		# FIXME: *actually* this should be a session-local
		# FIXME: holding store at the cClinicalRecord level
		self.__embedded_data_holder = cPopupDataHolder()

		self.__input_defs = input_defs

		gmResizingWidgets.cResizingWindow.__init__(self, parent, id=-1, size=size)

		self.__problem = problem
		if isinstance(problem, gmEMRStructItems.cEpisode):
			self.__problem = emr.episode2problem(episode = problem)
		elif isinstance(problem, gmEMRStructItems.cHealthIssue):
			self.__problem = emr.health_issue2problem(issue = problem)
		self.__pat = gmPerson.gmCurrentPatient()
	#--------------------------------------------------------
	# cResizingWindow API
	#--------------------------------------------------------
	def DoLayout(self):
		"""Visually display input note according to user defined labels.
		"""
		# configure keywords
		for soap_cat in progress_note_keywords.keys():
			category = progress_note_keywords[soap_cat]
			for kwd in category.keys():
				category[kwd]['widget_data_sink'] = self.__embedded_data_holder.store_data
		input_fields = []
		# add fields to edit widget
		# note: this may produce identically labelled lines
		for line_def in self.__input_defs:
			input_field = gmResizingWidgets.cResizingSTC(self, -1, data = line_def)
			input_field.SetText(line_def.text)
			kwds = progress_note_keywords[line_def.soap_cat]
			input_field.set_keywords(popup_keywords=kwds)
			# FIXME: pending matcher setup
			self.AddWidget(widget=input_field, label=line_def.label)
			self.Newline()
			input_fields.append(input_field)
		# setup tab navigation between input fields
		for field_idx in range(len(input_fields)):
			# previous
			try:
				input_fields[field_idx].prev_in_tab_order = input_fields[field_idx-1]
			except IndexError:
				input_fields[field_idx].prev_in_tab_order = None
			# next
			try:
				input_fields[field_idx].next_in_tab_order = input_fields[field_idx+1]
			except IndexError:
				input_fields[field_idx].next_in_tab_order = None
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def save(self):
		"""Save data into backend."""

		# fill progress_note for import
		progress_note = []
		aoe = ''
		rfe = ''
		has_rfe = False
		has_plan = False
		soap_lines_contents = self.GetValue()
		for line_content in soap_lines_contents.values():
			if line_content.text.strip() == '':
				continue
			progress_note.append ({
				gmSOAPimporter.soap_bundle_SOAP_CAT_KEY: line_content.data.soap_cat,
				gmSOAPimporter.soap_bundle_TYPES_KEY: [],		# these types need to come from the editor
				gmSOAPimporter.soap_bundle_TEXT_KEY: line_content.text.rstrip()
			})
			if line_content.data.is_rfe:
				rfe += line_content.text.rstrip()
				has_rfe = True
			if line_content.data.soap_cat == 'p':
				has_plan = True
			if line_content.data.soap_cat == 'a':
				aoe += line_content.text.rstrip()
		if not (has_rfe and has_plan):
			msg = _('Progress note must have Reason for Encounter and Plan.')
			gmGuiHelpers.gm_show_info(msg, _('saving progress note'), gmLog.lErr)
			return False

		# work out episode name
		emr = self.__pat.get_emr()
		episode = None
		problem = self.__problem
		# - new episode, must get name from narrative (or user)
		if (problem is None) or (problem['type'] == 'issue'):
			if len(aoe) != 0:
				epi_name = aoe
			else:
				epi_name = rfe
			if problem is None:
				episode = emr.add_episode(episode_name = epi_name[:45], is_open = True)		# FIXME: un-hardcode length ?
			else:
				issue = emr.problem2issue(problem)
				# FIXME: make ttl configurable
				ttl = 90	# 90 days, 3 months
				all_closed = issue.close_expired_episodes(ttl=ttl)

				if all_closed:
					gmGuiHelpers.gm_beep_statustext(_('Closed episodes older than %s days on health issue [%s]') % (ttl, issue['description']))
					# either error or non-expired open episode exists
					# FIXME: all_closed not working

				open_epis = emr.get_episodes(open_status = True)
				open_epis = filter(lambda epi: epi['pk_health_issue'] == issue['pk'], open_epis)
				if len(open_epis) > 1:
						_log.Log(gmLog.lErr, 'there is more than one open episode for health issue [%s]' % str(issue))
						for e in open_epis:
							_log.Log(gmLog.lData, str(e))

				if len(open_epis) == 1:
						# need to ask user what to do
						# - close old open episode and continue with new one ?
						# - use old open episode as is ?
						# - use old open episode but rename ?
						#xxxxxxxxxxxxxxxxxxxx
						
						print "FIXME  len(open_epis) == 1"
						d = wx.MessageDialog (
							self,
							_("There is an episode still open for this issue. Close the old episode (yes)\nRelink under old episode(no)\nThink about it (cancel)"),
							caption = "WARNING !",
							style = wx.YES| wx.NO | wx.CANCEL
						)
						answ = d.ShowModal()
						if answ == wx.ID_YES:
							open_epis[0]['episode_open'] = False
							open_epis[0].save_payload()
						elif answ == wx.ID_NO:
							episode = open_epis[0]
						else:
							return False
						
				if episode is None:
					# error, close all and hope things work out ...
					issue.close_expired_episodes(ttl=-1)
					episode = emr.add_episode(episode_name = epi_name[:45], pk_health_issue = problem['pk_health_issue'], is_open = True)

			if episode is None:
				msg = _('Cannot create episode [%s] to save progress note under.' % epi_name)
				gmGuiHelpers.gm_show_error(msg, _('saving progress note'), gmLog.lErr)
				return False
			epi_id = episode['pk_episode']
		else:
			epi_id = problem['pk_episode']

		# set up clinical context in progress note
		encounter = emr.get_active_encounter()
		staff_id = gmPerson.gmCurrentProvider()['pk_staff']
		clin_ctx = {
			gmSOAPimporter.soap_bundle_EPISODE_ID_KEY: epi_id,
			gmSOAPimporter.soap_bundle_ENCOUNTER_ID_KEY: encounter['pk_encounter'],
			gmSOAPimporter.soap_bundle_STAFF_ID_KEY: staff_id
		}
		for line in progress_note:
			line[gmSOAPimporter.soap_bundle_CLIN_CTX_KEY] = clin_ctx

		# dump progress note to backend
		importer = gmSOAPimporter.cSOAPImporter()
		if not importer.import_soap(progress_note):
			gmGuiHelpers.gm_show_error(_('Error saving progress note.'), _('saving progress note'), gmLog.lErr)
			return False

		# dump embedded data to backend
		if not self.__embedded_data_holder.save():
			gmGuiHelpers.gm_show_error (
				_('Error saving embedded data.'),
				_('saving progress note'),
				gmLog.lErr
			)
			return False
		self.__embedded_data_holder.clear()

		return True
	#--------------------------------------------------------
	def get_problem(self):
		return self.__problem
#============================================================
class cResizingSoapPanel(wx.Panel):
	"""Basic progress note panel.

	It provides a gmResizingWindow based progress note editor
	with a header line. The header either displays the episode
	this progress note is associated with or it allows for
	entering an episode name. The episode name either names
	an existing episode or is the name for a new episode.

	This panel knows how to save it's data into the backend.

	Can work as:
		a) Progress note creation: displays an empty set of soap entries to
		create a new soap note for the given episode (or unassociated)
	"""
	#--------------------------------------------------------
	def __init__(self, parent, problem=None, input_defs=None):
		"""
		Construct a new SOAP input widget.

		@param parent: the parent widget

		@param episode: the episode to create the SOAP editor for.
		@type episode gmEMRStructItems.cEpisode instance or None (to create an
		unassociated progress note). A gmEMRStructItems.cProblem instance is 
		also allowed to be passed, as the widget will obtain the related cEpisode.

		@param input_defs: the display and associated data for each displayed narrative
		@type input_defs: a list of cSOAPLineDef instances
		"""
		if not isinstance(problem, (gmEMRStructItems.cHealthIssue, gmEMRStructItems.cEpisode, gmEMRStructItems.cProblem, types.NoneType)):
			raise gmExceptions.ConstructorError, 'problem [%s] is of type %s, must be issue, episode, problem or None' % (str(problem), type(problem))

		self.__is_saved = False
		# do layout
		wx.Panel.__init__ (
			self,
			parent,
			-1,
			wx.DefaultPosition,
			wx.DefaultSize,
			wx.NO_BORDER | wx.TAB_TRAVERSAL
		)
		# - editor
		if input_defs is None:
			soap_lines = []
			# make Richard the default ;-)
			# FIXME: actually, should be read from backend
			line = cSOAPLineDef()
			line.label = _('Patient Request')
			line.soap_cat = 's'
			line.is_rfe = True
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('History Taken')
			line.soap_cat = 's'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Findings')
			line.soap_cat = 'o'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Assessment')
			line.soap_cat = 'a'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Plan')
			line.soap_cat = 'p'
			soap_lines.append(line)
		else:
			soap_lines = input_defs
		self.__soap_editor = cResizingSoapWin (
			self,
			size = wx.DefaultSize,
			input_defs = soap_lines,
			problem = problem
		)
		# - arrange
		self.__szr_main = wx.BoxSizer(wx.VERTICAL)
		self.__szr_main.Add(self.__soap_editor, 1, wx.EXPAND)
		self.SetSizerAndFit(self.__szr_main)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_problem(self):
		"""Retrieve the related problem for this SOAP input widget.
		"""
		return self.__soap_editor.get_problem()
	#--------------------------------------------------------
	def is_unassociated_editor(self):
		"""
		Retrieves whether the current editor is not associated
		with any episode.
		"""
		return ((self.__problem is None) or (self.__problem['type'] == 'issue'))
	#--------------------------------------------------------
	def get_editor(self):
		"""Retrieves widget's SOAP text editor.
		"""
		return self.__soap_editor
	#--------------------------------------------------------
	def Clear(self):
		"""Clear any entries in widget's SOAP text editor
		"""
		self.__soap_editor.Clear()
	#--------------------------------------------------------
	def SetSaved(self, is_saved):
		"""
		Set SOAP input widget saved (dumped to backend) state

		@param is_saved: Flag indicating wether the SOAP has been dumped to
						 persistent backend
		@type is_saved: boolean
		"""
		self.__is_saved = is_saved
		self.Clear()
	#--------------------------------------------------------
	def IsSaved(self):
		"""
		Check SOAP input widget saved (dumped to backend) state
		"""
		return self.__is_saved
	def save(self):
		return self.__soap_editor.save()
#============================================================
class cSingleBoxSOAP(wx.TextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wx.TextCtrl.__init__(self, *args, **kwargs)
#============================================================
class cSingleBoxSOAPPanel(wx.Panel):
	"""Single Box free text SOAP input.

	This widget was suggested by David Guest on the mailing
	list. All it does is provide a single multi-line textbox
	for typing free-text clinical notes which are stored as
	Subjective.
	"""
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
		self.__do_layout()
		self.__pat = gmPerson.gmCurrentPatient()
		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.__soap_box = cSingleBoxSOAP (
			self,
			-1,
			'',
			style = wx.TE_MULTILINE
		)
		# buttons below that
		self.__BTN_save = wx.Button(self, wx.NewId(), _("save"))
		self.__BTN_save.SetToolTipString(_('save clinical note in EMR'))
		self.__BTN_discard = wx.Button(self, wx.NewId(), _("discard"))
		self.__BTN_discard.SetToolTipString(_('discard clinical note'))
		szr_btns = wx.BoxSizer(wx.HORIZONTAL)
		szr_btns.Add(self.__BTN_save, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.__BTN_discard, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wx.StaticBoxSizer(wx.StaticBox(self, -1, _("clinical progress note")), wx.VERTICAL)
		szr_outer.Add(self.__soap_box, 1, wx.EXPAND, 0)
		szr_outer.Add(szr_btns, 0, wx.EXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self._on_save_note)
		wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.pre_patient_selection(), receiver = self._save_note)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_note)

		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_note(self, event):
		self.__save_note()
		#event.Skip()
	#--------------------------------------------------------
	def _on_discard_note(self, event):
		# FIXME: maybe ask for confirmation ?
		self.__soap_box.SetValue('')
		#event.Skip()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_note(self):
		wx.CallAfter(self.__save_note)
	#--------------------------------------------------------
	def __save_note(self):
		# sanity checks
		if self.__pat is None:
			return True
		if not self.__pat.is_connected():
			return True
		if not self.__soap_box.IsModified():
			return True
		note = self.__soap_box.GetValue()
		if note.strip() == '':
			return True
		# now save note
		emr = self.__pat.get_emr()
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot access clinical record of patient')
			return False
		if not emr.add_clin_narrative(note, soap_cat='s'):
			_log.Log(gmLog.lErr, 'error saving clinical note')
			return False
		self.__soap_box.SetValue('')
		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')
	#--------------------------------------------------------
	def get_narrative(pk_encounter=None, pk_health_issue = None, default_labels=None):
		"""
		Retrieve the soap editor input lines definitions built from
		all the narratives for the given issue along a specific
		encounter.
		
		@param pk_health_issue The id of the health issue to obtain the narratives for.
		@param pk_health_issue An integer instance

		@param pk_encounter The id of the encounter to obtain the narratives for.
		@type A gmEMRStructItems.cEncounter instance.

		@param default_labels: The user customized labels for each
		soap category.
		@type default_labels: A dictionary instance which keys are
		soap categories.
		"""
		
		# custom labels
		if default_labels is None:
			default_labels = {
				's': _('History Taken'),
				'o': _('Findings'),
				'a': _('Assessment'),
				'p': _('Plan')
		}		
		
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		soap_lines = []
		# for each soap cat
		for soap_cat in gmSOAPimporter.soap_bundle_SOAP_CATS:
			# retrieve narrative for given encounter
			narr_items =  emr.get_clin_narrative (
				encounters = [pk_encounter],
				issues = [pk_health_issue],
				soap_cats = [soap_cat]
			)
			for narrative in narr_items:
				try:
					# FIXME: add more data such as doctor sig
					label_txt = default_labels[narrative['soap_cat']]
				except:
					label_txt = narrative['soap_cat']				
				line = cSOAPLineDef()
				line.label = label_txt
				line.text = narrative['narrative']
#				line.data['narrative instance'] = narrative
				soap_lines.append(line)
		return soap_lines
	#--------------------------------------------------------
	def create_widget_on_test_kwd1(*args, **kwargs):
		print "test keyword must have been typed..."
		print "actually this would have to return a suitable wx.Window subclass instance"
		print "args:", args
		print "kwd args:"
		for key in kwargs.keys():
			print key, "->", kwargs[key]
	#--------------------------------------------------------
	def create_widget_on_test_kwd2(*args, **kwargs):
		msg = (
			"test keyword must have been typed...\n"
			"actually this would have to return a suitable wx.Window subclass instance\n"
		)
		for arg in args:
			msg = msg + "\narg ==> %s" % arg
		for key in kwargs.keys():
			msg = msg + "\n%s ==> %s" % (key, kwargs[key])
		gmGuiHelpers.gm_show_info (
			aMessage = msg,
			aTitle = 'msg box on create_widget from test_keyword'
		)
	#--------------------------------------------------------
	def test_soap_notebook():
		print 'testing notebooked soap input...'
		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cProgressNoteInputNotebook(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
	#--------------------------------------------------------
	def test_soap_notebook_panel():
		print 'testing notebooked soap panel...'
		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cNotebookedProgressNoteInputPanel(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
	#--------------------------------------------------------
	_log.SetAllLogLevels(gmLog.lData)

	try:
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)

		#test_soap_notebook()
		test_soap_notebook_panel()

#		# multisash soap
#		print 'testing multisashed soap input...'
#		application = wx.PyWidgetTester(size=(800,500))
#		soap_input = cMultiSashedProgressNoteInputPanel(application.frame, -1)
#		application.frame.Show(True)
#		application.MainLoop()
				
#		# soap widget displaying all narratives for an issue along an encounter
#		print 'testing soap editor for encounter narratives...'
#		episode = gmEMRStructItems.cEpisode(aPK_obj=1)
#		encounter = gmEMRStructItems.cEncounter(aPK_obj=1)
#		narrative = get_narrative(pk_encounter = encounter['pk_encounter'], pk_health_issue = episode['pk_health_issue'])
#		default_labels = {'s':'Subjective', 'o':'Objective', 'a':'Assesment', 'p':'Plan'}
#		app = wx.PyWidgetTester(size=(300,500))		
#		app.SetWidget(cResizingSoapPanel, episode, narrative)
#		app.MainLoop()
#		del app
		
#		# soap progress note for episode
#		print 'testing soap editor for episode...'
#		app = wx.PyWidgetTester(size=(300,300))
#		app.SetWidget(cResizingSoapPanel, episode)
#		app.MainLoop()
#		del app
		
#		# soap progress note for problem
#		print 'testing soap editor for problem...'
#		problem = gmEMRStructItems.cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': 1})		
#		app = wx.PyWidgetTester(size=(300,300))
#		app.SetWidget(cResizingSoapPanel, problem)
#		app.MainLoop()
#		del app		
		
#		# unassociated soap progress note
#		print 'testing unassociated soap editor...'
#		app = wx.PyWidgetTester(size=(300,300))
#		app.SetWidget(cResizingSoapPanel, None)
#		app.MainLoop()
#		del app		
		
#		# unstructured progress note
#		print 'testing unstructured progress note...'
#		app = wx.PyWidgetTester(size=(600,600))
#		app.SetWidget(cSingleBoxSOAPPanel, -1)
#		app.MainLoop()
		
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

#============================================================
# $Log: gmSOAPWidgets.py,v $
# Revision 1.73  2006-06-20 14:26:36  ncq
# - do not refresh problem list too early or threading will kill us
#
# Revision 1.72  2006/06/17 19:56:24  ncq
# - immediately refresh problem list when episode_changed() signal arrives
#
# Revision 1.71  2006/06/17 14:26:30  ncq
# - missing return True
#
# Revision 1.70  2006/06/17 14:00:03  ncq
# - cleanup
#
# Revision 1.69  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.68  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.67  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.66  2006/01/03 12:12:03  ncq
# - make epydoc happy re _()
#
# Revision 1.65  2005/12/27 19:01:07  ncq
# - define vacc popup keyword just for testing
# - slightly massage Syan's close-episodes-on-creation patch
#
# Revision 1.64  2005/12/27 02:52:40  sjtan
#
# allow choice of closing old episode, or relinking to old episode, whenever opening a new episode in the present of an already open episode of an issue.
# Small logic error fixed where the id of the health_issue was passed in as the id of an episode.
#
# Revision 1.63  2005/12/26 12:03:10  sjtan
#
# more schema matching. some delegation .
#
# Revision 1.62  2005/10/21 09:25:52  ncq
# - verify input structure in store_data()
# - reorder __init__ so cSoapWin does not fail
# - better recursion in data_sink setting for keywords
#
# Revision 1.61  2005/10/20 07:44:44  ncq
# - cleanup++, some refactoring for clarity
# - new way of handling popup data
#
# Revision 1.60  2005/10/04 13:09:49  sjtan
# correct syntax errors; get soap entry working again.
#
# Revision 1.59  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.58  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.57  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.56  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.55  2005/09/26 04:31:27  ihaywood
# allow problem to be passed to clinical popup EditAreas
#
# Revision 1.54  2005/09/12 15:10:43  ncq
# - robustify auto-closing of episodes
#
# Revision 1.53  2005/09/11 17:39:54  ncq
# - auto-close episodes older than 90 days when a new episode
#   for the same health issue is started by the user,
#   still lacking user interaction for "old" episodes younger than that
#
# Revision 1.52  2005/09/09 13:53:03  ncq
# - make progress note editor deal with cProblem instances and
#   add appropriate casts in callers, thereby simplifying code
# - auto-generate episode names where appropriate
#
# Revision 1.51  2005/08/22 13:27:47  ncq
# - properly return error from SetHeadingTxt
#
# Revision 1.50  2005/07/21 21:01:26  ncq
# - cleanup
#
# Revision 1.49  2005/06/20 13:15:02  cfmoro
# Port to changes in cEpisodeSelector
#
# Revision 1.48  2005/05/17 08:10:44  ncq
# - rearrange/relabel buttons/drop "discard" button on progress
#    notes notebook according to user feedback
#
# Revision 1.47  2005/05/14 14:59:41  ncq
# - cleanups, teach proper levels to listen to signals
# - listen to "activating_patient" so we can save progress notes *before* changing patient
# - reset SOAP notebook on patient_selected
#
# Revision 1.46  2005/05/12 15:12:57  ncq
# - improved problem list look and feel
#
# Revision 1.45  2005/05/08 21:49:11  ncq
# - cleanup, improve test code
# - add progress note editor notebook and use it
# - teach cResizingSoapPanel how to save itself
#
# Revision 1.44  2005/05/06 15:32:11  ncq
# - initial notebooked progress note input widget and test code
#
# Revision 1.43  2005/05/05 06:50:27  ncq
# - more work on pre-0.1 issues: use BoxSizer instead of FlexGridSizer
#   for progress note editor so STC *should* occupy whole width of
#   multisash, however, redrawing makes it wrong again at times
# - add dummy popup keywords for pending ICPC coding
# - try to drop from heading to STC on enter
# - make TAB move from heading to STC
# - we might want to make the header part of the same TAB container as the STC
#
# Revision 1.42  2005/04/27 18:51:06  ncq
# - slightly change Syans fix for the failing soap import to properly
#   take advantage of the existing infrastructure, my bad
#
# Revision 1.41  2005/04/27 14:49:38  sjtan
#
# allow the save clin_item to work by fixing a small bug where soap_cat isn't passed.
#
# Revision 1.40  2005/04/25 08:34:03  ncq
# - cleanup
# - don't display closed episodes in problem list
# - don't wipe out half-baked progress notes when switching
#   back and forth after relevant backend changes
#
# Revision 1.39  2005/04/24 14:52:15  ncq
# - use generic edit area popup for health issues
#
# Revision 1.38  2005/04/20 22:22:41  ncq
# - create_vacc_popup/create_issue_popup
#
# Revision 1.37  2005/04/18 19:25:50  ncq
# - configure Plan input field to popup vaccinations edit area
#   on keyword $vacc
# - simplify cSoapLineDef because progress note input widget
#   is not used to *edit* progress notes ...
#
# Revision 1.36  2005/04/12 16:22:28  ncq
# - remove faulty _()
#
# Revision 1.35  2005/04/12 10:06:06  ncq
# - cleanup
#
# Revision 1.34  2005/04/03 20:18:27  ncq
# - I feel haphazardous - enable actual progress note writing on [save]  :-))
#
# Revision 1.33  2005/03/29 18:43:06  cfmoro
# Removed debugging lines O:)
#
# Revision 1.32  2005/03/29 18:40:55  cfmoro
# Fixed last encounter date when does not exists
#
# Revision 1.31  2005/03/29 07:31:01  ncq
# - according to user feedback:
#   - switch sides for problem selection/progress note editor
#   - add header to problem list
#   - improve problem list formatting/display "last open"
# - remove debugging code
#
# Revision 1.30  2005/03/18 16:48:41  cfmoro
# Fixes to integrate multisash notes input plugin in wxclient
#
# Revision 1.29  2005/03/17 21:23:16  cfmoro
# Using cClinicalRecord.problem2episode to take advantage of episode cache
#
# Revision 1.28  2005/03/17 19:53:13  cfmoro
# Fixes derived from different combination of events. Replaced button state by per action sanity check for 0.1
#
# Revision 1.27  2005/03/17 17:48:20  cfmoro
# Using types.NoneType to detect unassociated progress note
#
# Revision 1.26  2005/03/17 16:41:30  ncq
# - properly allow explicit None episodes to indicate "unassociated"
#
# Revision 1.25  2005/03/17 13:35:23  ncq
# - some cleanup
#
# Revision 1.24  2005/03/16 19:29:22  cfmoro
# cResizingSoapPanel accepting cProblem instance of type episode
#
# Revision 1.23  2005/03/16 17:47:30  cfmoro
# Minor fixes after moving the file. Restored test harness
#
# Revision 1.22  2005/03/15 08:07:52  ncq
# - incorporated cMultiSashedProgressNoteInputPanel from Carlos' test area
# - needs fixing/cleanup
# - test harness needs to be ported
#
# Revision 1.21  2005/03/14 21:02:41  cfmoro
# Handle changing text in unassociated notes
#
# Revision 1.20  2005/03/14 18:41:53  cfmoro
# Indent fix
#
# Revision 1.19  2005/03/14 18:39:49  cfmoro
# Clear phrasewheel on saving unassociated note
#
# Revision 1.18  2005/03/14 17:36:51  cfmoro
# Added unit test for unassociated progress note
#
# Revision 1.17  2005/03/14 14:39:18  ncq
# - somewhat improve Carlos' support for unassociated progress notes
#
# Revision 1.16  2005/03/13 09:05:06  cfmoro
# Added intial support for unassociated progress notes
#
# Revision 1.15  2005/03/09 19:41:18  cfmoro
# Decoupled cResizingSoapPanel from editing problem-encounter soap notes use case
#
# Revision 1.14  2005/03/04 19:44:28  cfmoro
# Minor fixes from unit test
#
# Revision 1.13  2005/03/03 21:12:49  ncq
# - some cleanups, switch to using data transfer classes
#   instead of complex and unwieldy dictionaries
#
# Revision 1.12  2005/02/23 03:20:44  cfmoro
# Restores SetProblem function. Clean ups
#
# Revision 1.11  2005/02/21 19:07:42  ncq
# - some cleanup
#
# Revision 1.10  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.9  2005/01/28 18:35:42  cfmoro
# Removed problem idx number
#
# Revision 1.8  2005/01/18 13:38:24  ncq
# - cleanup
# - input_defs needs to be list as dict does not guarantee order
# - make Richard-SOAP the default
#
# Revision 1.7  2005/01/17 19:55:28  cfmoro
# Adapted to receive cProblem instances for SOAP edition
#
# Revision 1.6  2005/01/13 14:28:07  ncq
# - cleanup
#
# Revision 1.5  2005/01/11 08:12:39  ncq
# - fix a whole bunch of bugs from moving to main trunk
#
# Revision 1.4  2005/01/10 20:14:02  cfmoro
# Import sys
#
# Revision 1.3  2005/01/10 17:50:36  ncq
# - carry over last bits and pieces from test-area
#
# Revision 1.2  2005/01/10 17:48:03  ncq
# - all of test_area/cfmoro/soap_input/gmSoapWidgets.py moved here
#
# Revision 1.1  2005/01/10 16:14:35  ncq
# - soap widgets independant of the backend (gmPG) live in here
#
# Revision 1.13	 2004/06/30 20:33:41  ncq
# - add_clinical_note() -> add_clin_narrative()
#
# Revision 1.12	 2004/03/09 07:54:32  ncq
# - can call __save_note() from button press handler directly
#
# Revision 1.11	 2004/03/08 23:35:10  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.10	 2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.9	2004/02/05 23:49:52	 ncq
# - use wxCallAfter()
#
# Revision 1.8	2003/11/09 14:29:11	 ncq
# - new API style in clinical record
#
# Revision 1.7	2003/10/26 01:36:13	 ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.6	2003/07/05 12:57:23	 ncq
# - catch one more error on saving note
#
# Revision 1.5	2003/06/26 22:26:04	 ncq
# - streamlined _save_note()
#
# Revision 1.4	2003/06/25 22:51:24	 ncq
# - now also handle signale application_closing()
#
# Revision 1.3	2003/06/24 12:57:05	 ncq
# - actually connect to backend
# - save note on patient change and on explicit save request
#
# Revision 1.2	2003/06/22 16:20:33	 ncq
# - start backend connection
#
# Revision 1.1	2003/06/19 16:50:32	 ncq
# - let's make something simple but functional first
#
#
