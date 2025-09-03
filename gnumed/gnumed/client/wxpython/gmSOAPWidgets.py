"""GNUmed SOAP related widgets.
"""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import logging
import sys


import wx


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgDB

from Gnumed.business import gmPerson
from Gnumed.business import gmHealthIssue
from Gnumed.business import gmSOAPimporter
from Gnumed.business import gmPraxis
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmStaff
from Gnumed.business import gmEpisode
from Gnumed.business import gmProblem

from Gnumed.wxpython import gmResizingWidgets, gmEMRStructWidgets, gmGuiHelpers, gmRegetMixin, gmEditArea, gmPatSearchWidgets, gmVaccWidgets

_log = logging.getLogger('gm.ui')
if __name__ == '__main__':
	_ = lambda x:x

#============================================================
def create_issue_popup(parent, pos, size, style, data_sink):
	ea = gmEMRStructWidgets.cHealthIssueEditAreaPnl (
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
	ea = gmVaccWidgets.cVaccinationEAPnl (
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
		'phx$': {
			'widget_factory': create_issue_popup,
			'widget_data_sink': None
		},
		'ea$:': {
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
	"""A notebook holding panels with progress note editors.

	There is one progress note editor panel for each episode being worked on.
	"""
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize):
		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			pos = pos,
			size = size,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER,
			name = self.__class__.__name__
		)
		_log.debug('created wx.Notebook: %s with ID %s', self.__class__.__name__, self.Id)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pat = gmPerson.gmCurrentPatient()
		self.__do_layout()
		self.__register_interests()

	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def add_editor(self, problem=None, allow_same_problem=False):
		"""Add a progress note editor page.

		The way <allow_same_problem> is currently used in callers
		it only applies to unassociated episodes.
		"""
		problem_to_add = problem

		# determine label
		if problem is None:
			label = _('new problem')
			problem_to_add = None
		else:
			problem_to_add = gmProblem.cProblem.from_issue_or_episode(problem)
			if not isinstance(problem_to_add, gmProblem.cProblem):
				raise TypeError('cannot open progress note editor for [%s]' % problem)

			# FIXME: configure maximum length
			label = gmTools.shorten_text(text = problem_to_add['problem'],	max_length = 23)
		if allow_same_problem:
			new_page = cResizingSoapPanel(parent = self, problem = problem_to_add)
			result = self.AddPage (
				page = new_page,
				text = label,
				select = True
			)
			return result

		# check for dupes
		# new unassociated problem
		if problem_to_add is None:
			# check for dupes
			for page_idx in range(self.GetPageCount()):
				page = self.GetPage(page_idx)
				# found
				if page.get_problem() is None:
					self.SetSelection(page_idx)
					return True
				continue
			# not found
			new_page = cResizingSoapPanel(parent = self, problem = problem_to_add)
			result = self.AddPage (
				page = new_page,
				text = label,
				select = True
			)
			return result

		# real problem
		# - raise existing editor ?
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			problem_of_page = page.get_problem()
			# editor is for unassociated new problem
			if problem_of_page is None:
				continue
			# editor is for episode
			if problem_of_page['type'] == 'episode':
				if problem_to_add['type'] == 'issue':
					is_equal = (problem_of_page['pk_health_issue'] == problem_to_add['pk_health_issue'])
				else:
					is_equal = (problem_of_page['pk_episode'] == problem_to_add['pk_episode'])
				if is_equal:
					self.SetSelection(page_idx)
					return True
				continue
			# editor is for health issue
			if problem_of_page['type'] == 'issue':
				if problem_of_page['pk_health_issue'] == problem_to_add['pk_health_issue']:
					self.SetSelection(page_idx)
					return True
				continue

		# - add new editor
		new_page = cResizingSoapPanel(parent = self, problem = problem_to_add)
		result = self.AddPage (
			page = new_page,
			text = label,
			select = True
		)

		return result

	#--------------------------------------------------------
	def close_current_editor(self):

		page_idx = self.GetSelection()
		page = self.GetPage(page_idx)

		if not page.editor_empty():
			really_discard = gmGuiHelpers.gm_show_question (
				_('Are you sure you really want to\n'
				  'discard this progress note ?\n'
				),
				_('Discarding progress note')
			)
			if really_discard is False:
				return

		self.DeletePage(page_idx)

		# always keep one unassociated editor open
		if self.GetPageCount() == 0:
			self.add_editor()
	#--------------------------------------------------------
	def warn_on_unsaved_soap(self):

		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			if page.editor_empty():
				continue

			gmGuiHelpers.gm_show_warning (
				_('There are unsaved progress notes !\n'),
				_('Unsaved progress notes')
			)
			return False

		return True
	#--------------------------------------------------------
	def save_unsaved_soap(self):
		save_all = False
		dlg = None
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			if page.editor_empty():
				continue

			if dlg is None:
				dlg = gmGuiHelpers.c3ButtonQuestionDlg (
					self, 
					-1,
					caption = _('Unsaved progress note'),
					question = _(
						'This progress note has not been saved yet.\n'
						'\n'
						'Do you want to save it or discard it ?\n\n'
					),
					button_defs = [
						{'label': _('&Save'), 'tooltip': _('Save this progress note'), 'default': True},
						{'label': _('&Discard'), 'tooltip': _('Discard this progress note'), 'default': False},
						{'label': _('Save &all'), 'tooltip': _('Save all remaining unsaved progress notes'), 'default': False}
					]
				)

			if not save_all:
				self.ChangeSelection(page_idx)
				decision = dlg.ShowModal()
				if decision == wx.ID_NO:
					_log.info('user requested discarding of unsaved progress note')
					continue
				if decision == wx.ID_CANCEL:
					save_all = True
			page.save()

		if dlg is not None:
			dlg.DestroyLater()
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
		print('[%s._populate_with_data] nothing to do, really...' % self.__class__.__name__)
		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events

		# client internal signals
		gmDispatcher.connect(signal = 'post_patient_selection', receiver=self._on_post_patient_selection)
#		gmDispatcher.connect(signal = u'application_closing', receiver=self._on_application_closing)

		self.__pat.register_before_switching_from_patient_callback(callback = self._before_switching_from_patient_callback)

		gmDispatcher.send(signal = 'register_pre_exit_callback', callback = self._pre_exit_callback)
	#--------------------------------------------------------
	def _before_switching_from_patient_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns True.
		"""
		return self.warn_on_unsaved_soap()
	#--------------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to be shut down.

		Shutdown will not proceed before this returns.
		"""
		self.save_unsaved_soap()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Patient changed."""
		self.DeleteAllPages()
		self.add_editor()
		self._schedule_data_reget()
	#--------------------------------------------------------
#	def _on_application_closing(self):
#		"""GNUmed is shutting down."""
#		print "[%s]: the application is closing down" % self.__class__.__name__
#		print "************************************"
#		print "need to ask user about SOAP saving !"
#		print "************************************"
	#--------------------------------------------------------
#	def _on_episodes_modified(self):
#		print "[%s]: episode modified" % self.__class__.__name__
#		print "need code to deal with:"
#		print "- deleted episode that we show so we can notify the user"
#		print "- renamed episode so we can update our episode label"
#		self._schedule_data_reget()
#		pass
#============================================================
class cNotebookedProgressNoteInputPanel(wx.Panel):
	"""A panel for entering multiple progress notes in context.

	Expects to be used as a notebook page.

	Left hand side:
	- problem list (health issues and active episodes)

	Right hand side:
	- notebook with progress note editors

	Listens to patient change signals, thus acts on the current patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""Constructs a new instance of SOAP input panel

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
		self.__pat = gmPerson.gmCurrentPatient()

		# ui construction and event handling set up
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
			label = _('Active problems'),
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
		tt = _(
			'Add editor for a new unassociated progress note.\n\n'
			'There is a configuration option whether or not to\n'
			'allow several new unassociated progress notes at once.'
		)
		self.__BTN_add_unassociated.SetToolTip(tt)

		self.__BTN_save = wx.Button(PNL_soap_editors, -1, _('&Save'))
		self.__BTN_save.SetToolTip(_('Save progress note into medical record and close this editor.'))

		self.__BTN_clear = wx.Button(PNL_soap_editors, -1, _('&Clear'))
		self.__BTN_clear.SetToolTip(_('Clear this progress note editor.'))

		self.__BTN_discard = wx.Button(PNL_soap_editors, -1, _('&Discard'))
		self.__BTN_discard.SetToolTip(_('Discard progress note and close this editor. You will loose any data already typed into this editor !'))

		# - arrange
		szr_btns_right = wx.BoxSizer(wx.HORIZONTAL)
		szr_btns_right.Add(self.__BTN_add_unassociated, 0, wx.SHAPED)
		szr_btns_right.Add(self.__BTN_clear, 0, wx.SHAPED)
		szr_btns_right.Add(self.__BTN_save, 0, wx.SHAPED)
		szr_btns_right.Add(self.__BTN_discard, 0, wx.SHAPED)

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
		emr = self.__pat.emr
		problems = emr.get_problems()
		for problem in problems:
			if not problem['problem_active']:
				continue
			if problem['type'] == 'issue':
				issue = gmHealthIssue.cHealthIssue.from_problem(problem)
				last_encounter = emr.get_last_encounter(issue_id = issue['pk_health_issue'])
				if last_encounter is None:
					last = issue['modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				label = '%s: %s "%s"' % (last, problem['l10n_type'], problem['problem'])
			elif problem['type'] == 'episode':
				epi = gmEpisode.cEpisode.from_problem(problem)
				last_encounter = emr.get_last_encounter(episode_id = epi['pk_episode'])
				if last_encounter is None:
					last = epi['episode_modified_when'].strftime('%m/%Y')
				else:
					last = last_encounter['last_affirmed'].strftime('%m/%Y')
				label = '%s: %s "%s"%s' % (
					last,
					problem['l10n_type'],
					problem['problem'],
					gmTools.coalesce(value2test = epi['health_issue'], return_instead = '', template4value = ' (%s)')
				)
			self.__LST_problems.Append(label, problem)
		splitter_width = self.__splitter.GetSize()[0]
		self.__splitter.SetSashPosition((splitter_width // 2), True)
		self.Refresh()
		#self.Update()
		return True

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		self.__LST_problems.Bind(wx.EVT_LISTBOX_DCLICK, self.__on_problem_activated)
		self.__BTN_save.Bind(wx.EVT_BUTTON, self.__on_save)
		self.__BTN_clear.Bind(wx.EVT_BUTTON, self.__on_clear)
		self.__BTN_discard.Bind(wx.EVT_BUTTON, self.__on_discard)
		self.__BTN_add_unassociated.Bind(wx.EVT_BUTTON, self.__on_add_unassociated)
		#wx.EVT_LISTBOX_DCLICK(self.__LST_problems, self.__LST_problems.GetId(), self.__on_problem_activated)
		#wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self.__on_save)
		#wx.EVT_BUTTON(self.__BTN_clear, self.__BTN_clear.GetId(), self.__on_clear)
		#wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self.__on_discard)
		#wx.EVT_BUTTON(self.__BTN_add_unassociated, self.__BTN_add_unassociated.GetId(), self.__on_add_unassociated)

		# client internal signals
		gmDispatcher.connect(signal='post_patient_selection', receiver=self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'clin.episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = 'clin.health_issue_mod_db', receiver = self._on_episode_issue_mod_db)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Patient changed."""
		if self.GetParent().GetCurrentPage() == self:
			self.reset_ui_content()
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		if self.GetParent().GetCurrentPage() == self:
			self.__refresh_problem_list()
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
		self.__soap_notebook.close_current_editor()
	#--------------------------------------------------------
	def __on_add_unassociated(self, evt):
		"""Add new editor for as-yet unassociated progress note.

		Clinical logic as per discussion with Jim Busser:

		- if patient has no episodes:
			- new patient
			- always allow several NEWs
		- if patient has episodes:
			- allow several NEWs per configuration
		"""
		emr = self.__pat.emr
		epis = emr.get_episodes()

		if len(epis) == 0:
			value = True
		else:
			value = gmCfgDB.get4user (
				option = 'horstspace.soap_editor.allow_same_episode_multiple_times',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				default = False
			)

		self.__soap_notebook.add_editor(allow_same_problem = value)
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

		if self.__soap_notebook.add_editor(problem = problem):
			return True

		gmGuiHelpers.gm_show_error (
			error = _(
				'Cannot open progress note editor for\n\n'
				'[%s].\n\n'
			) % problem['problem'],
			title = _('opening progress note editor')
		)
		return False
	#--------------------------------------------------------
	def __on_save(self, event):
		"""Save data to backend and close editor.
		"""
		page_idx = self.__soap_notebook.GetSelection()
		soap_nb_page = self.__soap_notebook.GetPage(page_idx)
		if not soap_nb_page.save():
			gmDispatcher.send(signal='statustext', msg=_('Problem saving progress note: duplicate information ?'))
			return False
		self.__soap_notebook.DeletePage(page_idx)
		# always keep one unassociated editor open
		self.__soap_notebook.add_editor()
		#self.__refresh_problem_list()
		return True
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self.__refresh_problem_list()
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

	_data_savers:dict = {}

	def __init__(self):
		self.__data = {}
	#--------------------------------------------------------
	def store_data(self, popup_type=None, desc=None, data=None, old_desc=None):
		# FIXME: do fancy validations

		print("storing popup data:", desc)
		print("type", popup_type)
		print("data", data)

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
		except Exception:
			pass
		return True
	#--------------------------------------------------------
	def save(self):
		for popup_type in self.__data:
			try:
				saver_func = self._data_savers[popup_type]
			except KeyError:
				_log.exception('no saver for popup data type [%s] configured', popup_type)
				return False
			for desc in self.__data[popup_type]:
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
class cResizingSoapWin(gmResizingWidgets.cResizingWindow):
	"""Resizing SOAP note input editor.

	This is a wrapper around a few resizing STCs (the
	labels and categories are settable) which are
	customized to accept progress note input. It provides
	the unified resizing behaviour.
	"""
	def __init__(self, parent, size, input_defs=None, problem=None):
		"""Initialize SOAP note input editor.

		@param input_defs: note's labels and categories
		@type input_defs: list of cSOAPLineDef instances
		"""
		if input_defs is None or len(input_defs) == 0:
			raise gmExceptions.ConstructorError('cannot generate note with field defs [%s]' % input_defs)

		# FIXME: *actually* this should be a session-local
		# FIXME: holding store at the c_ClinicalRecord level
		self.__embedded_data_holder = cPopupDataHolder()

		self.__input_defs = input_defs

		gmResizingWidgets.cResizingWindow.__init__(self, parent, id=-1, size=size)

		self.__problem = gmProblem.cProblem.from_issue_or_episode(problem)
		self.__pat = gmPerson.gmCurrentPatient()

	#--------------------------------------------------------
	# cResizingWindow API
	#--------------------------------------------------------
	def DoLayout(self):
		"""Visually display input note according to user defined labels.
		"""
		# configure keywords
		for soap_cat in progress_note_keywords:
			category = progress_note_keywords[soap_cat]
			for kwd in category:
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
		#has_rfe = False
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
				#has_rfe = True
				rfe += line_content.text.rstrip()
			if line_content.data.soap_cat == 'a':
				aoe += line_content.text.rstrip()

		emr = self.__pat.emr

		# - new episode, must get name from narrative (or user)
		if (self.__problem is None) or (self.__problem['type'] == 'issue'):
			# work out episode name
			epi_name = ''
			if len(aoe) != 0:
				epi_name = aoe
			else:
				epi_name = rfe

			dlg = wx.TextEntryDialog (
				self,
				_('Enter a descriptive name for this new problem:'),
				caption = _('Creating a problem (episode) to save the notelet under ...'),
				value = epi_name.replace('\r', '//').replace('\n', '//'),
				style = wx.OK | wx.CANCEL | wx.CENTRE
			)
			decision = dlg.ShowModal()
			if decision != wx.ID_OK:
				return False

			epi_name = dlg.GetValue().strip()
			if epi_name == '':
				gmGuiHelpers.gm_show_error(_('Cannot save a new problem without a name.'), _('saving progress note'))
				return False

			# new unassociated episode
			new_episode = emr.add_episode(episode_name = epi_name[:45], pk_health_issue = None, is_open = True)

			if self.__problem is not None:
				issue = gmHealthIssue.cHealthIssue.from_problem(self.__problem)
				if not gmEMRStructWidgets.move_episode_to_issue(episode = new_episode, target_issue = issue, save_to_backend = True):
					print("error moving episode to issue")

			epi_id = new_episode['pk_episode']
		else:
			epi_id = self.__problem['pk_episode']

		# set up clinical context in progress note
		encounter = emr.active_encounter
		staff_id = gmStaff.gmCurrentProvider()['pk_staff']
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
			gmGuiHelpers.gm_show_error(_('Error saving progress note.'), _('saving progress note'))
			return False

		# dump embedded data to backend
		if not self.__embedded_data_holder.save():
			gmGuiHelpers.gm_show_error (
				_('Error saving embedded data.'),
				_('saving progress note')
			)
			return False
		self.__embedded_data_holder.clear()

		return True
	#--------------------------------------------------------
	def get_problem(self):
		return self.__problem
	#--------------------------------------------------------
	def is_empty(self):
		editor_content = self.GetValue()

		for field_content in editor_content.values():
			if field_content.text.strip() != '':
				return False

		return True
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
		@type episode gmEpisode.cEpisode instance or None (to create an
		unassociated progress note). A gmProblem.cProblem instance is 
		also allowed to be passed, as the widget will obtain the related cEpisode.

		@param input_defs: the display and associated data for each displayed narrative
		@type input_defs: a list of cSOAPLineDef instances
		"""
		if not isinstance(problem, (gmHealthIssue.cHealthIssue, gmEpisode.cEpisode, gmProblem.cProblem, type(None))):
			raise gmExceptions.ConstructorError('problem [%s] is of type %s, must be issue, episode, problem or None' % (str(problem), type(problem)))

		self.__is_saved = False
		# do layout
		wx.Panel.__init__(self, parent, -1, style = wx.NO_BORDER | wx.TAB_TRAVERSAL)
		# - editor
		if input_defs is None:
			soap_lines = []
			# make Richard the default ;-)
			# FIXME: actually, should be read from backend
			line = cSOAPLineDef()
			line.label = _('Visit Purpose')
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

		@param is_saved: Flag indicating whether the SOAP has been dumped to
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
	#--------------------------------------------------------
	def save(self):
		return self.__soap_editor.save()
	#--------------------------------------------------------
	def editor_empty(self):
		return self.__soap_editor.is_empty()
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
			raise gmExceptions.ConstructorError('cannot register interests')
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
		self.__BTN_save.SetToolTip(_('save clinical note in EMR'))
		self.__BTN_discard = wx.Button(self, wx.NewId(), _("discard"))
		self.__BTN_discard.SetToolTip(_('discard clinical note'))
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
		self.__BTN_save.Bind(wx.EVT_BUTTON, self._on_save_note)
		self.__BTN_discard.Bind(wx.EVT_BUTTON, self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = 'application_closing', receiver = self._save_note)
		# really should be synchronous:
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._save_note)

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
		# xxxxxx
		# FIXME: this should be a sync callback
		# xxxxxx
		wx.CallAfter(self.__save_note)
	#--------------------------------------------------------
	def __save_note(self):
		# sanity checks
		if self.__pat is None:
			return True
		if not self.__pat.connected:
			return True
		if not self.__soap_box.IsModified():
			return True
		note = self.__soap_box.GetValue()
		if note.strip() == '':
			return True
		# now save note
		emr = self.__pat.emr
		if emr is None:
			_log.error('cannot access clinical record of patient')
			return False
		if not emr.add_clin_narrative(note, soap_cat='s'):
			_log.error('error saving clinical note')
			return False
		self.__soap_box.SetValue('')
		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------
	def get_narrative(pk_encounter=None, pk_health_issue = None, default_labels=None):
		"""
		Retrieve the soap editor input lines definitions built from
		all the narratives for the given issue along a specific
		encounter.

		@param pk_health_issue The id of the health issue to obtain the narratives for.
		@param pk_health_issue An integer instance

		@param pk_encounter The id of the encounter to obtain the narratives for.
		@type A gmEncounter.cEncounter instance.

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
		emr = pat.emr
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
				except Exception:
					label_txt = narrative['soap_cat']
				line = cSOAPLineDef()
				line.label = label_txt
				line.text = narrative['narrative']
#				line.data['narrative instance'] = narrative
				soap_lines.append(line)
		return soap_lines
	#--------------------------------------------------------
	def create_widget_on_test_kwd1(*args, **kwargs):
		print("test keyword must have been typed...")
		print("actually this would have to return a suitable wx.Window subclass instance")
		print("args:", args)
		print("kwd args:")
		for key in kwargs:
			print(key, "->", kwargs[key])
	#--------------------------------------------------------
	def create_widget_on_test_kwd2(*args, **kwargs):
		msg = (
			"test keyword must have been typed...\n"
			"actually this would have to return a suitable wx.Window subclass instance\n"
		)
		for arg in args:
			msg = msg + "\narg ==> %s" % arg
		for key in kwargs:
			msg = msg + "\n%s ==> %s" % (key, kwargs[key])
		gmGuiHelpers.gm_show_info (
			info = msg,
			title = 'msg box on create_widget from test_keyword'
		)
	#--------------------------------------------------------
	def test_soap_notebook():
		print('testing notebooked soap input...')
#		application = wx.PyWidgetTester(size=(800,500))
		#soap_input = 
#		cProgressNoteInputNotebook(application.frame, -1)
#		application.frame.Show(True)
#		application.MainLoop()
	#--------------------------------------------------------
	def test_soap_notebook_panel():
		print('testing notebooked soap panel...')
#		application = wx.PyWidgetTester(size=(800,500))
		#soap_input = 
#		cNotebookedProgressNoteInputPanel(application.frame, -1)
#		application.frame.Show(True)
#		application.MainLoop()
	#--------------------------------------------------------

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("No patient. Exiting gracefully...")
		sys.exit(0)

	gmPatSearchWidgets.set_active_patient(patient=patient)

	#test_soap_notebook()
	test_soap_notebook_panel()

#	# multisash soap
#	print 'testing multisashed soap input...'
#	application = wx.PyWidgetTester(size=(800,500))
#	soap_input = cMultiSashedProgressNoteInputPanel(application.frame, -1)
#	application.frame.Show(True)
#	application.MainLoop()

#	# soap widget displaying all narratives for an issue along an encounter
#	print 'testing soap editor for encounter narratives...'
#	episode = gmEpisode.cEpisode(aPK_obj=1)
#	encounter = gmEncounter.cEncounter(aPK_obj=1)
#	narrative = get_narrative(pk_encounter = encounter['pk_encounter'], pk_health_issue = episode['pk_health_issue'])
#	default_labels = {'s':'Subjective', 'o':'Objective', 'a':'Assesment', 'p':'Plan'}
#	app = wx.PyWidgetTester(size=(300,500))
#	app.SetWidget(cResizingSoapPanel, episode, narrative)
#	app.MainLoop()
#	del app

#	# soap progress note for episode
#	print 'testing soap editor for episode...'
#	app = wx.PyWidgetTester(size=(300,300))
#	app.SetWidget(cResizingSoapPanel, episode)
#	app.MainLoop()
#	del app

#	# soap progress note for problem
#	print 'testing soap editor for problem...'
#	problem = gmHealthIssue.cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': 1})
#	app = wx.PyWidgetTester(size=(300,300))
#	app.SetWidget(cResizingSoapPanel, problem)
#	app.MainLoop()
#	del app

#	# unassociated soap progress note
#	print 'testing unassociated soap editor...'
#	app = wx.PyWidgetTester(size=(300,300))
#	app.SetWidget(cResizingSoapPanel, None)
#	app.MainLoop()
#	del app

#	# unstructured progress note
#	print 'testing unstructured progress note...'
#	app = wx.PyWidgetTester(size=(600,600))
#	app.SetWidget(cSingleBoxSOAPPanel, -1)
#	app.MainLoop()


#============================================================
