"""GNUmed provider inbox handling widgets.
"""
#================================================================
__version__ = "$Revision: 1.48 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmDispatcher, gmTools, gmCfg, gmPG2, gmExceptions
from Gnumed.business import gmPerson, gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets, gmPlugin, gmRegetMixin, gmPhraseWheel
from Gnumed.wxpython import gmEditArea, gmAuthWidgets, gmPatSearchWidgets, gmVaccWidgets, gmCfgWidgets
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl, wxgTextExpansionEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)

_indicator = {
	-1: '',
	0: '',
	1: '*!!*'
}
#============================================================
class cTextExpansionEditAreaPnl(wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl):

	def __init__(self, *args, **kwds):

		try:
			self.__keyword = kwds['keyword']
			del kwds['keyword']
		except KeyError:
			self.__keyword = None

		wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl.__init__(self, *args, **kwds)

		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	def save(self):
		if not self.__valid_for_save():
			return False

		if self.__keyword is None:
			result = gmPG2.add_text_expansion (
				keyword = self._TCTRL_keyword.GetValue().strip(),
				expansion = self._TCTRL_expansion.GetValue(),
				public = self._RBTN_public.GetValue()
			)
		else:
			gmPG2.edit_text_expansion (
				keyword = self._TCTRL_keyword.GetValue().strip(),
				expansion = self._TCTRL_expansion.GetValue()
			)
			result = True

		return result
	#--------------------------------------------------------
	def refresh(self):
		self.__init_ui()
#		if self.__keyword is not None:
#			self._TCTRL_expansion.SetValue(u'')
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._TCTRL_keyword.Bind(wx.EVT_TEXT, self._on_keyword_modified)
	#--------------------------------------------------------
	def _on_keyword_modified(self, evt):
		if self._TCTRL_keyword.GetValue().strip() == u'':
			self._TCTRL_expansion.Enable(False)
		else:
			self._TCTRL_expansion.Enable(True)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __valid_for_save(self):

		kwd = self._TCTRL_keyword.GetValue().strip()
		if kwd == u'':
			self._TCTRL_keyword.SetBackgroundColour('pink')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without keyword.'), beep = True)
			return False
		self._TCTRL_keyword.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if self._TCTRL_expansion.GetValue().strip() == u'':
			self._TCTRL_expansion.SetBackgroundColour('pink')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without expansion text.'), beep = True)
			return False
		self._TCTRL_expansion.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		return True
	#--------------------------------------------------------
	def __init_ui(self, keyword=None):

		if keyword is not None:
			self.__keyword = keyword

		if self.__keyword is None:
			self._TCTRL_keyword.SetValue(u'')
			self._TCTRL_keyword.Enable(True)
			self._TCTRL_expansion.SetValue(u'')
			self._TCTRL_expansion.Enable(False)
			self._RBTN_public.Enable(True)
			self._RBTN_private.Enable(True)
			self._RBTN_public.SetValue(1)
		else:
			expansion = gmPG2.expand_keyword(keyword = self.__keyword)
			self._TCTRL_keyword.SetValue(self.__keyword)
			self._TCTRL_keyword.Enable(False)
			self._TCTRL_expansion.SetValue(gmTools.coalesce(expansion, u''))
			self._TCTRL_expansion.Enable(True)
			self._RBTN_public.Enable(False)
			self._RBTN_private.Enable(False)
#============================================================
def configure_keyword_text_expansion(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#----------------------
	def delete(keyword=None):
		gmPG2.delete_text_expansion(keyword = keyword)
		return True
	#----------------------
	def edit(keyword=None):
		# add new keyword
		ea = cTextExpansionEditAreaPnl(parent, -1, keyword=keyword)
		dlg = gmEditArea.cGenericEditAreaDlg(parent, -1, edit_area = ea)
		dlg.SetTitle (
			gmTools.coalesce(keyword, _('Adding text expansion'), _('Editing text expansion "%s"'))
		)
		if dlg.ShowModal() == wx.ID_OK:
			return True

		return False
	#----------------------
	def refresh(lctrl=None):
		kwds = [ [
				r[0],
				gmTools.bool2subst(r[1], gmTools.u_checkmark_thick, u''),
				gmTools.bool2subst(r[2], gmTools.u_checkmark_thick, u''),
				r[3]
			] for r in gmPG2.get_text_expansion_keywords()
		]
		data = [ r[0] for r in gmPG2.get_text_expansion_keywords() ]
		lctrl.set_string_items(kwds)
		lctrl.set_data(data)
	#----------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the keyword you want to edit !\n'),
		caption = _('Editing keyword-based text expansions ...'),
		columns = [_('Keyword'), _('Public'), _('Private'), _('Owner')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
def configure_fallback_primary_provider(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	staff = gmPerson.get_staff_list()
	choices = [ [
			s[u'short_alias'],
			u'%s%s %s' % (
				gmTools.coalesce(s['title'], u'', u'%s '),
				s['firstnames'],
				s['lastnames']
			),
			s['role'],
			gmTools.coalesce(s['comment'], u'')
		]
		for s in staff
		if s['is_active'] is True
	]
	data = [ s['pk_staff'] for s in staff if s['is_active'] is True ]

	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Please select the provider to fall back to in case\n'
			'no primary provider is configured for a patient.\n'
		),
		option = 'patient.fallback_primary_provider',
		bias = 'user',
		default_value = None,
		choices = choices,
		columns = [_('Alias'), _('Provider'), _('Role'), _('Comment')],
		data = data,
		caption = _('Configuring fallback primary provider')
	)
#============================================================
class cProviderPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = gmPerson.cMatchProvider_Provider()
		self.SetToolTipString(_('Select a healthcare provider.'))
		self.selection_only = True
#============================================================
# practice related widgets 
#============================================================
def show_audit_trail(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('showing audit trail'))
	if conn is None:
		return False

	#-----------------------------------
	def refresh(lctrl):
		cmd = u'SELECT * FROM audit.v_audit_trail ORDER BY audit_when_ts'
		rows, idx = gmPG2.run_ro_queries(link_obj = conn, queries = [{'cmd': cmd}], get_col_idx = False)
		lctrl.set_string_items (
			[ [
				r['event_when'],
				r['event_by'],
				u'%s %s %s' % (
					gmTools.coalesce(r['row_version_before'], gmTools.u_diameter),
					gmTools.u_right_arrow,
					gmTools.coalesce(r['row_version_after'], gmTools.u_diameter)
				),
				r['event_table'],
				r['event'],
				r['pk_audit']
			] for r in rows ]
		)
	#-----------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = u'',
		caption = _('GNUmed database audit log ...'),
		columns = [ _('When'), _('Who'), _('Revisions'), _('Table'), _('Event'), '#' ],
		single_selection = True,
		refresh_callback = refresh
	)

#============================================================
# FIXME: this should be moved elsewhere !
#------------------------------------------------------------
def configure_workplace_plugins(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------
	def delete(workplace):

		curr_workplace = gmSurgery.gmCurrentPractice().active_workplace
		if workplace == curr_workplace:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete the active workplace.'), beep = True)
			return False

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent,
			-1,
			caption = _('Deleting workplace ...'),
			question = _('Are you sure you want to delete this workplace ?\n\n "%s"\n') % workplace,
			show_checkbox = True,
			checkbox_msg = _('delete configuration, too'),
			checkbox_tooltip = _(
				'Check this if you want to delete all configuration items\n'
				'for this workplace along with the workplace itself.'
			),
			button_defs = [
				{'label': _('Delete'), 'tooltip': _('Yes, delete this workplace.'), 'default': True},
				{'label': _('Do NOT delete'), 'tooltip': _('No, do NOT delete this workplace'), 'default': False}
			]
		)

		decision = dlg.ShowModal()
		if decision != wx.ID_YES:
			dlg.Destroy()
			return False

		include_cfg = dlg.checkbox_is_checked()
		dlg.Destroy()

		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('delete workplace'))
		if not dbo_conn:
			return False

		gmSurgery.delete_workplace(workplace = workplace, conn = dbo_conn, delete_config = include_cfg)
		return True
	#-----------------------------------
	def edit(workplace=None):

		dbcfg = gmCfg.cCfgSQL()

		if workplace is None:
			dlg = wx.TextEntryDialog (
				parent = parent,
				message = _('Enter a descriptive name for the new workplace:'),
				caption = _('Configuring GNUmed workplaces ...'),
				defaultValue = u'',
				style = wx.OK | wx.CENTRE
			)
			dlg.ShowModal()
			workplace = dlg.GetValue().strip()
			if workplace == u'':
				gmGuiHelpers.gm_show_error(_('Cannot save a new workplace without a name.'), _('Configuring GNUmed workplaces ...'))
				return False
			curr_plugins = []
		else:
			curr_plugins = gmTools.coalesce(dbcfg.get2 (
				option = u'horstspace.notebook.plugin_load_order',
				workplace = workplace,
				bias = 'workplace'
				), []
			)

		msg = _(
			'Pick the plugin(s) to be loaded the next time the client is restarted under the workplace:\n'
			'\n'
			'    [%s]\n'
		) % workplace

		picker = gmListWidgets.cItemPickerDlg (
			parent,
			-1,
			title = _('Configuring workplace plugins ...'),
			msg = msg
		)
		picker.set_columns(['Available plugins'], ['Active plugins'])
		available_plugins = gmPlugin.get_installed_plugins(plugin_dir = 'gui')
		picker.set_choices(available_plugins)
		picker.set_picks(picks = curr_plugins)
		btn_pressed = picker.ShowModal()
		if btn_pressed != wx.ID_OK:
			picker.Destroy()
			return False

		new_plugins = picker.get_picks()
		picker.Destroy()
		if new_plugins == curr_plugins:
			return True

		if new_plugins is None:
			return True

		dbcfg.set (
			option = u'horstspace.notebook.plugin_load_order',
			value = new_plugins,
			workplace = workplace
		)

		return True
	#-----------------------------------
	def edit_old(workplace=None):

		available_plugins = gmPlugin.get_installed_plugins(plugin_dir='gui')

		dbcfg = gmCfg.cCfgSQL()

		if workplace is None:
			dlg = wx.TextEntryDialog (
				parent = parent,
				message = _('Enter a descriptive name for the new workplace:'),
				caption = _('Configuring GNUmed workplaces ...'),
				defaultValue = u'',
				style = wx.OK | wx.CENTRE
			)
			dlg.ShowModal()
			workplace = dlg.GetValue().strip()
			if workplace == u'':
				gmGuiHelpers.gm_show_error(_('Cannot save a new workplace without a name.'), _('Configuring GNUmed workplaces ...'))
				return False
			curr_plugins = []
			choices = available_plugins
		else:
			curr_plugins = gmTools.coalesce(dbcfg.get2 (
				option = u'horstspace.notebook.plugin_load_order',
				workplace = workplace,
				bias = 'workplace'
				), []
			)
			choices = curr_plugins[:]
			for p in available_plugins:
				if p not in choices:
					choices.append(p)

		sels = range(len(curr_plugins))
		new_plugins = gmListWidgets.get_choices_from_list (
			parent = parent,
			msg = _(
				'\n'
				'Select the plugin(s) to be loaded the next time\n'
				'the client is restarted under the workplace:\n'
				'\n'
				' [%s]'
				'\n'
			) % workplace,
			caption = _('Configuring GNUmed workplaces ...'),
			choices = choices,
			selections = sels,
			columns = [_('Plugins')],
			single_selection = False
		)

		if new_plugins == curr_plugins:
			return True

		if new_plugins is None:
			return True

		dbcfg.set (
			option = u'horstspace.notebook.plugin_load_order',
			value = new_plugins,
			workplace = workplace
		)

		return True
	#-----------------------------------
	def clone(workplace=None):
		if workplace is None:
			return False

		new_name = wx.GetTextFromUser (
			message = _('Enter a name for the new workplace !'),
			caption = _('Cloning workplace'),
			default_value = u'%s-2' % workplace,
			parent = parent
		).strip()

		if new_name == u'':
			return False

		dbcfg = gmCfg.cCfgSQL()
		opt = u'horstspace.notebook.plugin_load_order'

		plugins = dbcfg.get2 (
			option = opt,
			workplace = workplace,
			bias = 'workplace'
		)

		dbcfg.set (
			option = opt,
			value = plugins,
			workplace = new_name
		)

		# FIXME: clone cfg, too

		return True
	#-----------------------------------
	def refresh(lctrl):
		workplaces = gmSurgery.gmCurrentPractice().workplaces
		curr_workplace = gmSurgery.gmCurrentPractice().active_workplace
		try:
			sels = [workplaces.index(curr_workplace)]
		except ValueError:
			sels = []

		lctrl.set_string_items(workplaces)
		lctrl.set_selections(selections = sels)
	#-----------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _(
			'\nSelect the workplace to configure below.\n'
			'\n'
			'The currently active workplace is preselected.\n'
		),
		caption = _('Configuring GNUmed workplaces ...'),
		columns = [_('Workplace')],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		left_extra_button = (_('Clone'), _('Clone the selected workplace'), clone)
	)
#============================================================
class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl, gmRegetMixin.cRegetOnPaintMixin):

	_item_handlers = {}
	_patient_msg_types = ['clinical.review docs', 'clinical.review results', 'clinical.review vaccs']
	#--------------------------------------------------------
	def __init__(self, *args, **kwds):

		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.provider = gmPerson.gmCurrentProvider()
		self.filter_mode = 'all'
		self.__init_ui()

		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
		cProviderInboxPnl._item_handlers['clinical.review results'] = self._goto_measurements_review
		cProviderInboxPnl._item_handlers['clinical.review vaccs'] = self._goto_vaccination_review

		self.__register_interests()
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__populate_inbox()
		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'message_inbox_generic_mod_db', receiver = self._on_message_inbox_mod_db)
		gmDispatcher.connect(signal = u'message_inbox_mod_db', receiver = self._on_message_inbox_mod_db)
		# FIXME: listen for results insertion/deletion
		gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._on_message_inbox_mod_db)
		# FIXME: listen for doc insertion/deletion
		# FIXME: listen for doc reviews
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.set_columns([u'', _('date'), _('category'), _('type'), _('message')])

		msg = _('\n Inbox of %(title)s %(lname)s.\n') % {
			'title': gmTools.coalesce (
				self.provider['title'],
				gmPerson.map_gender2salutation(self.provider['gender'])
			),
			'lname': self.provider['lastnames']
		}

		self._msg_welcome.SetLabel(msg)

		if gmPerson.gmCurrentPatient().connected:
			self._RBTN_active_patient.Enable()
	#--------------------------------------------------------
	def __populate_inbox(self):

		"""Fill UI with data."""
		self.__msgs = self.provider.inbox.messages

		if self.filter_mode == 'active':
			if gmPerson.gmCurrentPatient().connected:
				curr_pat_id = gmPerson.gmCurrentPatient().ID
				self.__msgs = [ m for m in self.__msgs if m['pk_patient'] == curr_pat_id ]
			else:
				self.__msgs = []

		items = [
			[
				_indicator[m['importance']],
				m['received_when'].strftime('%Y-%m-%d'),
				m['l10n_category'],
				m['l10n_type'],
				m['comment']
			] for m in self.__msgs
		]
		self._LCTRL_provider_inbox.set_string_items(items = items)
		self._LCTRL_provider_inbox.set_data(data = self.__msgs)
		self._LCTRL_provider_inbox.set_column_widths()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
		wx.CallAfter(self._RBTN_active_patient.Enable)
	#--------------------------------------------------------
	def _on_message_inbox_mod_db(self, *args, **kwargs):
		wx.CallAfter(self._schedule_data_reget)
		gmDispatcher.send(signal = u'request_user_attention', msg = _('Please check your GNUmed Inbox !'))
	#--------------------------------------------------------
	def _lst_item_activated(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		handler_key = '%s.%s' % (msg['category'], msg['type'])
		try:
			handle_item = cProviderInboxPnl._item_handlers[handler_key]
		except KeyError:
			gmGuiHelpers.gm_show_warning (
				_(
"""No double-click action pre-programmed into
GNUmed for message category and type:

 [%s]
"""
) % handler_key,
				_('handling provider inbox item')
			)
			return False

		if not handle_item(pk_context = msg['pk_context'], pk_patient = msg['pk_patient']):
			_log.error('item handler returned "false"')
			_log.error('handler key: [%s]', handler_key)
			_log.error('message: %s', str(msg))
			return False

		return True
	#--------------------------------------------------------
	def _lst_item_focused(self, evt):
		pass
	#--------------------------------------------------------
	def _lst_item_selected(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		if msg['data'] is None:
			tmp = _('Message: %s') % msg['comment']
		else:
			tmp = _('Message: %s\nData: %s') % (msg['comment'], msg['data'])

		self._TXT_inbox_item_comment.SetValue(tmp)
	#--------------------------------------------------------
	def _lst_item_right_clicked(self, evt):
		tmp = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if tmp is None:
			return
		self.__focussed_msg = tmp

		# build menu
		menu = wx.Menu(title = _('Inbox Message menu'))
		# - delete message
		if not self.__focussed_msg['is_virtual']:
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('delete message')))
			wx.EVT_MENU(menu, ID, self._on_delete_focussed_msg)

		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def _on_all_messages_radiobutton_selected(self, event):
		self.filter_mode = 'all'
		self._TXT_inbox_item_comment.SetValue(u'')
		self.__populate_inbox()
	#--------------------------------------------------------
	def _on_active_patient_radiobutton_selected(self, event):
		self.filter_mode = 'active'
		self._TXT_inbox_item_comment.SetValue(u'')
		self.__populate_inbox()
	#--------------------------------------------------------
	# item handlers
	#--------------------------------------------------------
	def _on_delete_focussed_msg(self, evt):
		if self.__focussed_msg['is_virtual']:
			gmDispatcher.send(signal = 'statustext', msg = _('You must deal with the reason for this message to remove it from your inbox.'), beep = True)
			return False

		if not self.provider.inbox.delete_message(self.__focussed_msg['pk_message_inbox']):
			gmDispatcher.send(signal='statustext', msg=_('Problem removing message from Inbox.'))
			return False
		return True
	#--------------------------------------------------------
	def _goto_doc_review(self, pk_context=None, pk_patient=None):
		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmShowMedDocs', sort_mode = 'review')
		return True
	#--------------------------------------------------------
	def _goto_measurements_review(self, pk_context=None, pk_patient=None):
		wx.BeginBusyCursor()
		success = gmPatSearchWidgets.set_active_patient(patient=gmPerson.cIdentity(aPK_obj=pk_patient))
		wx.EndBusyCursor()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed results\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return True
	#--------------------------------------------------------
	def _goto_vaccination_review(self, pk_context=None, pk_patient=None):
		wx.BeginBusyCursor()
		success = gmPatSearchWidgets.set_active_patient(patient = gmPerson.cIdentity(aPK_obj = pk_patient))
		wx.EndBusyCursor()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are conflicting vaccinations\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		wx.CallAfter(gmVaccWidgets.manage_vaccinations)

		return True
#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	def test_configure_wp_plugins():
		app = wx.PyWidgetTester(size = (400, 300))
		configure_workplace_plugins()

	def test_message_inbox():
		app = wx.PyWidgetTester(size = (800, 600))
		app.SetWidget(cProviderInboxPnl, -1)
		app.MainLoop()


	test_configure_wp_plugins()
	#test_message_inbox()

#============================================================
