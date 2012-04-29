"""GNUmed provider inbox handling widgets.
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmSurgery
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmVaccWidgets
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmDataPackWidgets


_log = logging.getLogger('gm.ui')

_indicator = {
	-1: '',
	0: '',
	1: '*!!*'
}
#============================================================
def configure_fallback_primary_provider(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	staff = gmStaff.get_staff_list()
	choices = [ [
			s[u'short_alias'],
			u'%s%s %s' % (
				gmTools.coalesce(s['title'], u'', u'%s '),
				s['firstnames'],
				s['lastnames']
			),
			s['l10n_role'],
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
#====================================================================
class cMessageTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = u"""
			SELECT DISTINCT ON (label)
				pk_type,
				(l10n_type || ' (' || l10n_category || ')')
					AS label
			FROM
				dem.v_inbox_item_type
			WHERE
				l10n_type %(fragment_condition)s
					OR
				type %(fragment_condition)s
					OR
				l10n_category %(fragment_condition)s
					OR
				category %(fragment_condition)s
			ORDER BY label
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		self.matcher = mp
		self.SetToolTipString(_('Select a message type.'))
	#----------------------------------------------------------------
	def _create_data(self):
		if self.GetData() is not None:
			return

		val = self.GetValue().strip()
		if val == u'':
			return

		self.SetText (
			value = val,
			data = gmProviderInbox.create_inbox_item_type(message_type = val)
		)
#====================================================================
def _display_clinical_reminders():
	wx.CallAfter(__display_clinical_reminders)

gmDispatcher.connect(signal = u'post_patient_selection', receiver = _display_clinical_reminders)

def __display_clinical_reminders():
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		return
	for msg in pat.due_messages:
		if msg['expiry_date'] is None:
			exp = u''
		else:
			exp = _(' - expires %s') % gmDateTime.pydt_strftime (
				msg['expiry_date'],
				'%Y %b %d',
				accuracy = gmDateTime.acc_days
			)
		txt = _(
			'Due for %s (since %s%s):\n'
			'%s'
			'%s'
			'\n'
			'Patient: %s\n'
			'Reminder by: %s'
		) % (
			gmDateTime.format_interval_medically(msg['interval_due']),
			gmDateTime.pydt_strftime(msg['due_date'], '%Y %b %d', accuracy = gmDateTime.acc_days),
			exp,
			gmTools.coalesce(msg['comment'], u'', u'\n%s\n'),
			gmTools.coalesce(msg['data'], u'', u'\n%s\n'),
			pat['description_gender'],
			msg['modified_by']
		)
		gmGuiHelpers.gm_show_warning (
			aTitle = _('Clinical reminder'),
			aMessage = txt
		)
	for hint in pat.dynamic_hints:
		txt = u'%s\n\n          %s' % (
			gmTools.wrap(hint['hint'], width = 50, initial_indent = u' ', subsequent_indent = u' '),
			hint['source']
		)
		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			None,
			-1,
			caption = _('Clinical hint'),
			question = txt,
			button_defs = [
				{'label': _('OK'), 'tooltip': _('OK'), 'default': True},
				{'label': _('More info'), 'tooltip': _('Go to [%s]') % hint['url']}
			]
		)
		button = dlg.ShowModal()
		dlg.Destroy()
		if button == wx.ID_NO:
			gmNetworkTools.open_url_in_browser(hint['url'], autoraise = False)

	return
#====================================================================
from Gnumed.wxGladeWidgets import wxgInboxMessageEAPnl

class cInboxMessageEAPnl(wxgInboxMessageEAPnl.wxgInboxMessageEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['message']
			del kwargs['message']
		except KeyError:
			data = None

		wxgInboxMessageEAPnl.wxgInboxMessageEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		if not gmPerson.gmCurrentPatient().connected:
			self._CHBOX_active_patient.SetValue(False)
			self._CHBOX_active_patient.Enable(False)
			self._PRW_patient.Enable(True)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._TCTRL_subject.GetValue().strip() == u'':
			validity = False
			self.display_ctrl_as_valid(ctrl = self._TCTRL_subject, valid = False)
		else:
			self.display_ctrl_as_valid(ctrl = self._TCTRL_subject, valid = True)

		if self._PRW_type.GetValue().strip() == u'':
			validity = False
			self._PRW_type.display_as_valid(False)
		else:
			self._PRW_type.display_as_valid(True)

		missing_receiver = (
			(self._CHBOX_send_to_me.IsChecked() is False)
				and
			(self._PRW_receiver.GetData() is None)
		)

		missing_patient = (
			(self._CHBOX_active_patient.IsChecked() is False)
				and
			(self._PRW_patient.person is None)
		)

		if missing_receiver and missing_patient:
			validity = False
			self.display_ctrl_as_valid(ctrl = self._CHBOX_send_to_me, valid = False)
			self._PRW_receiver.display_as_valid(False)
			self.display_ctrl_as_valid(ctrl = self._CHBOX_active_patient, valid = False)
			self.display_ctrl_as_valid(ctrl = self._PRW_patient, valid = False)
		else:
			self.display_ctrl_as_valid(ctrl = self._CHBOX_send_to_me, valid = True)
			self._PRW_receiver.display_as_valid(True)
			self.display_ctrl_as_valid(ctrl = self._CHBOX_active_patient, valid = True)
			self.display_ctrl_as_valid(ctrl = self._PRW_patient, valid = True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat_id = None
		if self._CHBOX_active_patient.GetValue() is True:
			pat_id = gmPerson.gmCurrentPatient().ID
		else:
			if self._PRW_patient.person is not None:
				pat_id = self._PRW_patient.person.ID

		receiver = None
		if self._CHBOX_send_to_me.IsChecked():
			receiver = gmStaff.gmCurrentProvider()['pk_staff']
		else:
			if self._PRW_receiver.GetData() is not None:
				receiver = self._PRW_receiver.GetData()

		msg = gmProviderInbox.create_inbox_message (
			patient = pat_id,
			staff = receiver,
			message_type = self._PRW_type.GetData(can_create = True),
			subject = self._TCTRL_subject.GetValue().strip()
		)

		msg['data'] = self._TCTRL_message.GetValue().strip()

		if self._PRW_due.is_valid_timestamp():
			msg['due_date'] = self._PRW_due.date

		if self._PRW_expiry.is_valid_timestamp():
			msg['expiry_date'] = self._PRW_expiry.date

		if self._RBTN_normal.GetValue() is True:
			msg['importance'] = 0
		elif self._RBTN_high.GetValue() is True:
			msg['importance'] = 1
		else:
			msg['importance'] = -1

		msg.save()
		self.data = msg
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['comment'] = self._TCTRL_subject.GetValue().strip()
		self.data['pk_type'] = self._PRW_type.GetData(can_create = True)

		if self._CHBOX_send_to_me.IsChecked():
			self.data['pk_staff'] = gmStaff.gmCurrentProvider()['pk_staff']
		else:
			self.data['pk_staff'] = self._PRW_receiver.GetData()

		self.data['data'] = self._TCTRL_message.GetValue().strip()

		if self._CHBOX_active_patient.GetValue() is True:
			self.data['pk_patient'] = gmPerson.gmCurrentPatient().ID
		else:
			if self._PRW_patient.person is None:
				self.data['pk_patient'] = None
			else:
				self.data['pk_patient'] = self._PRW_patient.person.ID

		if self._PRW_due.is_valid_timestamp():
			self.data['due_date'] = self._PRW_due.date

		if self._PRW_expiry.is_valid_timestamp():
			self.data['expiry_date'] = self._PRW_expiry.date

		if self._RBTN_normal.GetValue() is True:
			self.data['importance'] = 0
		elif self._RBTN_high.GetValue() is True:
			self.data['importance'] = 1
		else:
			self.data['importance'] = -1

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_subject.SetValue(u'')
		self._PRW_type.SetText(value = u'', data = None)
		self._CHBOX_send_to_me.SetValue(True)
		self._PRW_receiver.Enable(False)
		self._PRW_receiver.SetData(data = gmStaff.gmCurrentProvider()['pk_staff'])
		self._TCTRL_message.SetValue(u'')
		self._PRW_due.SetText(data = None)
		self._PRW_expiry.SetText(data = None)
		self._RBTN_normal.SetValue(True)
		self._RBTN_high.SetValue(False)
		self._RBTN_low.SetValue(False)

		self._PRW_patient.person = None

		if gmPerson.gmCurrentPatient().connected:
			self._CHBOX_active_patient.Enable(True)
			self._CHBOX_active_patient.SetValue(True)
			self._PRW_patient.Enable(False)
		else:
			self._CHBOX_active_patient.Enable(False)
			self._CHBOX_active_patient.SetValue(False)
			self._PRW_patient.Enable(True)

		self._TCTRL_subject.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._TCTRL_subject.SetValue(gmTools.coalesce(self.data['comment'], u''))
		self._PRW_type.SetData(data = self.data['pk_type'])

		curr_prov = gmStaff.gmCurrentProvider()
		curr_pat = gmPerson.gmCurrentPatient()

		if curr_prov['pk_staff'] == self.data['pk_staff']:
			self._CHBOX_send_to_me.SetValue(True)
			self._PRW_receiver.Enable(False)
			self._PRW_receiver.SetData(data = gmStaff.gmCurrentProvider()['pk_staff'])
		else:
			self._CHBOX_send_to_me.SetValue(False)
			self._PRW_receiver.Enable(True)
			self._PRW_receiver.SetData(data = self.data['pk_staff'])

		self._TCTRL_message.SetValue(gmTools.coalesce(self.data['data'], u''))

		if curr_pat.connected:
			self._CHBOX_active_patient.Enable(True)
			if curr_pat.ID == self.data['pk_patient']:
				self._CHBOX_active_patient.SetValue(True)
				self._PRW_patient.Enable(False)
				self._PRW_patient.person = None
			else:
				self._CHBOX_active_patient.SetValue(False)
				self._PRW_patient.Enable(True)
				if self.data['pk_patient'] is None:
					self._PRW_patient.person = None
				else:
					self._PRW_patient.person = gmPerson.cIdentity(aPK_obj = self.data['pk_patient'])
		else:
			self._CHBOX_active_patient.Enable(False)
			self._CHBOX_active_patient.SetValue(False)
			self._PRW_patient.Enable(True)
			if self.data['pk_patient'] is None:
				self._PRW_patient.person = None
			else:
				self._PRW_patient.person = gmPerson.cIdentity(aPK_obj = self.data['pk_patient'])

		self._PRW_due.SetText(data = self.data['due_date'])
		self._PRW_expiry.SetText(data = self.data['expiry_date'])

		self._RBTN_normal.SetValue(False)
		self._RBTN_high.SetValue(False)
		self._RBTN_low.SetValue(False)
		{	-1: self._RBTN_low,
			0: self._RBTN_normal,
			1: self._RBTN_high
		}[self.data['importance']].SetValue(True)

		self._TCTRL_subject.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_active_patient_checked(self, event):
		if self._CHBOX_active_patient.IsChecked():
			self._PRW_patient.Enable(False)
			self._PRW_patient.person = None
		else:
			self._PRW_patient.Enable(True)
	#----------------------------------------------------------------
	def _on_send_to_me_checked(self, event):
		if self._CHBOX_send_to_me.IsChecked():
			self._PRW_receiver.Enable(False)
			self._PRW_receiver.SetData(data = gmStaff.gmCurrentProvider()['pk_staff'])
		else:
			self._PRW_receiver.Enable(True)
			self._PRW_receiver.SetText(value = u'', data = None)
#============================================================
def edit_inbox_message(parent=None, message=None, single_entry=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cInboxMessageEAPnl(parent = parent, id = -1)
	ea.data = message
	ea.mode = gmTools.coalesce(message, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(message, _('Adding new inbox message'), _('Editing inbox message')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#============================================================
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl

class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl, gmRegetMixin.cRegetOnPaintMixin):

	_item_handlers = {}

	#--------------------------------------------------------
	def __init__(self, *args, **kwds):

		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.provider = gmStaff.gmCurrentProvider()
		self.filter_mode = 'all'
		self.__init_ui()

		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
		cProviderInboxPnl._item_handlers['clinical.review results'] = self._goto_measurements_review
		cProviderInboxPnl._item_handlers['clinical.review lab'] = self._goto_measurements_review
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
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_message_inbox_mod_db)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_message_inbox_mod_db)
		gmDispatcher.connect(signal = u'doc_obj_review_mod_db', receiver = self._on_message_inbox_mod_db)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.set_columns([u'', _('Sent'), _('Category'), _('Type'), _('Message')])

		msg = _('\n Inbox of %(title)s %(lname)s.\n') % {
			'title': gmTools.coalesce (
				self.provider['title'],
				gmPerson.map_gender2salutation(self.provider['gender'])
			),
			'lname': self.provider['lastnames']
		}

		self._LCTRL_provider_inbox.item_tooltip_callback = self._get_msg_tooltip

		self._msg_welcome.SetLabel(msg)

		if gmPerson.gmCurrentPatient().connected:
			self._RBTN_active_patient.Enable()
	#--------------------------------------------------------
	def __populate_inbox(self):
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
		self._TXT_inbox_item_comment.SetValue(u'')
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
			if msg['pk_patient'] is None:
				gmGuiHelpers.gm_show_warning (
					_('No double-click action pre-programmed into\n'
					'GNUmed for message category and type:\n'
					'\n'
					' [%s]\n'
					) % handler_key,
					_('handling provider inbox item')
				)
				return False
			handle_item = self._goto_patient

		if not handle_item(pk_context = msg['pk_context'], pk_patient = msg['pk_patient']):
			_log.error('item handler returned <False>')
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
		menu = wx.Menu(title = _('Inbox Message Actions:'))

		if self.__focussed_msg['pk_patient'] is not None:
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('Activate patient')))
			wx.EVT_MENU(menu, ID, self._on_goto_patient)

		if not self.__focussed_msg['is_virtual']:
			# - delete message
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('Delete')))
			wx.EVT_MENU(menu, ID, self._on_delete_focussed_msg)
			# - edit message
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('Edit')))
			wx.EVT_MENU(menu, ID, self._on_edit_focussed_msg)

#		if self.__focussed_msg['pk_staff'] is not None:
#			# - distribute to other providers
#			ID = wx.NewId()
#			menu.AppendItem(wx.MenuItem(menu, ID, _('Distribute')))
#			wx.EVT_MENU(menu, ID, self._on_distribute_focussed_msg)

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
	def _on_add_button_pressed(self, event):
		edit_inbox_message(parent = self, message = None, single_entry = False)
	#--------------------------------------------------------
	def _get_msg_tooltip(self, msg):
		return msg.format()
#		tt = u'%s: %s%s\n' % (
#			msg['received_when'].strftime('%A, %Y %B %d, %H:%M').decode(gmI18N.get_encoding()),
#			gmTools.bool2subst(msg['is_virtual'], _('virtual message'), _('message')),
#			gmTools.coalesce(msg['pk_inbox_message'], u'', u' #%s ')
#		)
#
#		tt += u'%s: %s\n' % (
#			msg['l10n_category'],
#			msg['l10n_type']
#		)
#
#		tt += u'%s %s %s\n' % (
#			msg['modified_by'],
#			gmTools.u_right_arrow,
#			gmTools.coalesce(msg['provider'], _('everyone'))
#		)
#
#		tt += u'\n%s%s%s\n\n' % (
#			gmTools.u_left_double_angle_quote,
#			msg['comment'],
#			gmTools.u_right_double_angle_quote
#		)
#
#		tt += gmTools.coalesce (
#			msg['pk_patient'],
#			u'',
#			u'%s\n\n' % _('Patient #%s')
#		)
#
#		if msg['data'] is not None:
#			tt += msg['data'][:150]
#			if len(msg['data']) > 150:
#				tt += gmTools.u_ellipsis
#
#		return tt
	#--------------------------------------------------------
	# item handlers
	#--------------------------------------------------------
	def _on_goto_patient(self, evt):
		return self._goto_patient(pk_patient = self.__focussed_msg['pk_patient'])
	#--------------------------------------------------------
	def _on_delete_focussed_msg(self, evt):
		if self.__focussed_msg['is_virtual']:
			gmDispatcher.send(signal = 'statustext', msg = _('You must deal with the reason for this message to remove it from your inbox.'), beep = True)
			return False

		if not self.provider.inbox.delete_message(self.__focussed_msg['pk_inbox_message']):
			gmDispatcher.send(signal='statustext', msg=_('Problem removing message from Inbox.'))
			return False
		return True
	#--------------------------------------------------------
	def _on_edit_focussed_msg(self, evt):
		if self.__focussed_msg['is_virtual']:
			gmDispatcher.send(signal = 'statustext', msg = _('This message cannot be edited because it is virtual.'))
			return False
		edit_inbox_message(parent = self, message = self.__focussed_msg, single_entry = True)
		return True
	#--------------------------------------------------------
	def _on_distribute_focussed_msg(self, evt):
		if self.__focussed_msg['pk_staff'] is None:
			gmDispatcher.send(signal = 'statustext', msg = _('This message is already visible to all providers.'))
			return False
		print "now distributing"
		return True
	#--------------------------------------------------------
	def _goto_patient(self, pk_context=None, pk_patient=None):

		wx.BeginBusyCursor()

		msg = _('There is a message about patient [%s].\n\n'
			'However, I cannot find that\n'
			'patient in the GNUmed database.'
		) % pk_patient

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False
		except:
			wx.EndBusyCursor()
			raise

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		return True
	#--------------------------------------------------------
	def _goto_doc_review(self, pk_context=None, pk_patient=None):

		msg = _('Supposedly there are unreviewed documents\n'
			'for patient [%s]. However, I cannot find\n'
			'that patient in the GNUmed database.'
		) % pk_patient

		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmShowMedDocs', sort_mode = 'review')
		return True
	#--------------------------------------------------------
	def _goto_measurements_review(self, pk_context=None, pk_patient=None):

		msg = _('Supposedly there are unreviewed results\n'
			'for patient [%s]. However, I cannot find\n'
			'that patient in the GNUmed database.'
		) % pk_patient

		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return True
	#--------------------------------------------------------
	def _goto_vaccination_review(self, pk_context=None, pk_patient=None):

		msg = _('Supposedly there are conflicting vaccinations\n'
			'for patient [%s]. However, I cannot find\n'
			'that patient in the GNUmed database.'
		) % pk_patient

		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg,	_('handling provider inbox item'))
			return False

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		wx.CallAfter(gmVaccWidgets.manage_vaccinations)

		return True
#============================================================
def browse_dynamic_hints(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def switch_activation(item):
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Switching clinical hint activation'))
		if conn is None:
			return False
		item['is_active'] = not item['is_active']
		return item.save(conn = conn)
	#------------------------------------------------------------
	def manage_data_packs(item):
		gmDataPackWidgets.manage_data_packs(parent = parent)
		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		hints = gmProviderInbox.get_dynamic_hints(order_by = u'is_active DESC, source, hint')
		items = [ [
			gmTools.bool2subst(h['is_active'], gmTools.u_checkmark_thin, u''),
			h['source'][:30],
			h['hint'][:60],
			gmTools.coalesce(h['url'], u'')[:60],
			h['lang'],
			h['query'][:25],
			h['pk']
		] for h in hints ]
		lctrl.set_string_items(items)
		lctrl.set_data(hints)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nDynamic hints registered with GNUmed.\n'),
		caption = _('Showing dynamic hints.'),
		columns = [ _('Active'), _('Source'), _('Hint'), u'URL', _('Language'), u'SQL', u'#' ],
		single_selection = True,
		refresh_callback = refresh,
		left_extra_button = (
			_('(De)-Activate'),
			_('Switch activation of the selected hint'),
			switch_activation
		),
		right_extra_button = (
			_('Data packs'),
			_('Browse and install clinical hints data packs'),
			manage_data_packs
		),
		list_tooltip_callback = get_tooltip
	)

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

	def test_msg_ea():
		app = wx.PyWidgetTester(size = (800, 600))
		app.SetWidget(cInboxMessageEAPnl, -1)
		app.MainLoop()


	#test_configure_wp_plugins()
	#test_message_inbox()
	test_msg_ea()

#============================================================
