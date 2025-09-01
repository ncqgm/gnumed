"""GNUmed provider inbox handling widgets.
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
#from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmGender
from Gnumed.business import gmStaff
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmClinicalRecord

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython.gmPatSearchWidgets import set_active_patient
from Gnumed.wxpython.gmVaccWidgets import manage_vaccinations


_log = logging.getLogger('gm.ui')

_indicator = {
	-1: '',
	0: '',
	1: '*!!*'
}

#====================================================================
class cMessageTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = """
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
		self.SetToolTip(_('Select a message type.'))
	#----------------------------------------------------------------
	def _create_data(self, link_obj=None):
		if self.GetData() is not None:
			return

		val = self.GetValue().strip()
		if val == '':
			return

		self.SetText (
			value = val,
			data = gmProviderInbox.create_inbox_item_type(message_type = val)
		)

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

		if self._TCTRL_subject.GetValue().strip() == '':
			validity = False
			self.display_ctrl_as_valid(ctrl = self._TCTRL_subject, valid = False)
		else:
			self.display_ctrl_as_valid(ctrl = self._TCTRL_subject, valid = True)

		if self._PRW_type.GetValue().strip() == '':
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

		if self._PRW_due.is_valid_timestamp(empty_is_valid = True):
			self._PRW_due.display_as_valid(True)
		else:
			# non-empty but also not valid
			validity = False
			self._PRW_due.display_as_valid(False)

		if self._PRW_expiry.is_valid_timestamp(empty_is_valid = True):
			self._PRW_expiry.display_as_valid(True)
		else:
			# non-empty but also not valid
			validity = False
			self._PRW_expiry.display_as_valid(False)

		# if .due is not empty AND valid
		if self._PRW_due.is_valid_timestamp(empty_is_valid = False):
			# and if .expiry is ALSO not empty AND valid
			if self._PRW_expiry.is_valid_timestamp(empty_is_valid = False):
				# only then compare .due and .expiry
				if not self._PRW_expiry.date > self._PRW_due.date:
					validity = False
					self._PRW_expiry.display_as_valid(False)
					self.StatusText = _('Message cannot expire before being due.')

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
		self._TCTRL_subject.SetValue('')
		self._PRW_type.SetText(value = '', data = None)
		self._CHBOX_send_to_me.SetValue(True)
		self._PRW_receiver.Enable(False)
		self._PRW_receiver.SetData(data = gmStaff.gmCurrentProvider()['pk_staff'])
		self._TCTRL_message.SetValue('')
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

		self._TCTRL_subject.SetValue(gmTools.coalesce(self.data['comment'], ''))
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

		self._TCTRL_message.SetValue(gmTools.coalesce(self.data['data'], ''))

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
					self._PRW_patient.person = gmPerson.cPerson(aPK_obj = self.data['pk_patient'])
		else:
			self._CHBOX_active_patient.Enable(False)
			self._CHBOX_active_patient.SetValue(False)
			self._PRW_patient.Enable(True)
			if self.data['pk_patient'] is None:
				self._PRW_patient.person = None
			else:
				self._PRW_patient.person = gmPerson.cPerson(aPK_obj = self.data['pk_patient'])

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
			self._PRW_receiver.SetText(value = '', data = None)

#============================================================
def edit_inbox_message(parent=None, message=None, single_entry=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cInboxMessageEAPnl(parent, -1)
	ea.data = message
	ea.mode = gmTools.coalesce(message, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(message, _('Adding new inbox message'), _('Editing inbox message')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#============================================================
def manage_reminders(parent=None, patient=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		reminders = gmProviderInbox.get_reminders(pk_patient = patient)
		items = [ [
			gmTools.bool2subst (
				r['is_overdue'],
				_('overdue for %s'),
				_('due in %s')
			) % gmDateTime.format_interval_medically(r['interval_due']),
			r['comment'],
			r['pk_inbox_message']
		] for r in reminders ]
		lctrl.set_string_items(items)
		lctrl.set_data(reminders)
	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = None,
		caption = _('Reminders for the current patient'),
		columns = [ _('Status'), _('Subject'), '#' ],
		single_selection = False,
		can_return_empty = True,
		ignore_OK_button = False,
		refresh_callback = refresh
#		edit_callback=None,
#		new_callback=None,
#		delete_callback=None,
#		left_extra_button=None,
#		middle_extra_button=None,
#		right_extra_button=None
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl

class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl, gmRegetMixin.cRegetOnPaintMixin):

	_item_handlers:dict = {}

	#--------------------------------------------------------
	def __init__(self, *args, **kwds):

		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.provider = gmStaff.gmCurrentProvider()
		self.__init_ui()

		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
		cProviderInboxPnl._item_handlers['clinical.review results'] = self._goto_measurements_review
		cProviderInboxPnl._item_handlers['clinical.review lab'] = self._goto_measurements_review
		cProviderInboxPnl._item_handlers['clinical.review vaccs'] = self._goto_vaccination_review

		self.__register_interests()
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _schedule_data_reget(self):
		_log.debug('called by reget-on-paint mixin API')
		gmRegetMixin.cRegetOnPaintMixin._schedule_data_reget(self)
	#--------------------------------------------------------
	def _populate_with_data(self):
		_log.debug('_populate_with_data() (after _schedule_data_reget ?)')
		self.__populate_inbox()
		return True
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		_log.debug('called by notebook plugin API, skipping inbox loading')
		#gmRegetMixin.cRegetOnPaintMixin.repopulate_ui(self)
		return True

	#--------------------------------------------------------
	def filter_by_active_patient(self):
		self._CHBOX_active_patient.SetValue(True)
		self._TXT_inbox_item_comment.SetValue('')
		self.__populate_inbox()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'dem.message_inbox_mod_db', receiver = self._on_message_inbox_mod_db)
		# FIXME: listen for results insertion/deletion
		gmDispatcher.connect(signal = 'clin.reviewed_test_results_mod_db', receiver = self._on_results_mod_db)
		gmDispatcher.connect(signal = 'dem.identity_mod_db', receiver = self._on_identity_mod_db)
		gmDispatcher.connect(signal = 'blobs.doc_med_mod_db', receiver = self._on_doc_mod_db)
		gmDispatcher.connect(signal = 'blobs.reviewed_doc_objs_mod_db', receiver = self._on_doc_obj_review_mod_db)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)

	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.debug = 'provider inbox list'

		self._LCTRL_provider_inbox.set_columns(['', _('Generated'), _('Status'), _('Patient'), _('Message'), _('Category - Type')])
		self._LCTRL_provider_inbox.searchable_columns = [2, 3, 4, 5]
		self._LCTRL_provider_inbox.item_tooltip_callback = self._get_msg_tooltip
		self._LCTRL_provider_inbox.extend_popup_menu_callback = self._extend_popup_menu
		self._LCTRL_provider_inbox.select_callback = self.__msg_selected
		self._LCTRL_provider_inbox.activate_callback = self.__msg_activated
		self.__update_greeting()

		if gmPerson.gmCurrentPatient().connected:
			self._CHBOX_active_patient.Enable()

	#--------------------------------------------------------
	def __update_greeting(self, no_of_messages=None):
		msg = _(' Inbox of %s %s%s') % (
			gmTools.coalesce (
				self.provider['title'],
				gmGender.map_gender2salutation(self.provider['gender'])
			),
			self.provider['lastnames'],
			gmTools.coalesce(no_of_messages, '.', _(': %s message(s)'))
		)
		self._msg_welcome.SetLabel(msg)

	#--------------------------------------------------------
	def __populate_inbox(self):
		_log.debug('populating provider inbox')

		# calculate constraints
		pk_patient = None
		if self._CHBOX_active_patient.IsChecked():
			_log.debug('restricting to active patient')
			curr_pat = gmPerson.gmCurrentPatient()
			if curr_pat.connected:
				pk_patient = curr_pat.ID

		include_without_provider = True
		if self._CHBOX_active_provider.IsChecked():
			_log.debug('restricting to active provider directly')
			include_without_provider = False

		# get which messages to show
		if self._RBTN_relevant_messages.GetValue():
			_log.debug('loading relevant messages')
			self.__msgs = self.provider.inbox.get_relevant_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider
			)
		elif self._RBTN_all_messages.GetValue():
			_log.debug('loading all but expired messages')
			self.__msgs = self.provider.inbox.get_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider,
				exclude_expired = True,
				expired_only = False,
				overdue_only = False,
				unscheduled_only = False,
				exclude_unscheduled = False
			)
		elif self._RBTN_overdue_messages.GetValue():
			_log.debug('loading overdue messages only')
			self.__msgs = self.provider.inbox.get_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider,
				exclude_expired = True,
				expired_only = False,
				overdue_only = True,
				unscheduled_only = False,
				exclude_unscheduled = True,
				order_by = 'due_date, importance DESC, received_when DESC'
			)
		elif self._RBTN_scheduled_messages.GetValue():
			_log.debug('loading scheduled messages only')
			self.__msgs = self.provider.inbox.get_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider,
				exclude_expired = True,
				expired_only = False,
				overdue_only = False,
				unscheduled_only = False,
				exclude_unscheduled = True,
				order_by = 'due_date, importance DESC, received_when DESC'
			)
		elif self._RBTN_unscheduled_messages.GetValue():
			_log.debug('loading unscheduled messages only')
			self.__msgs = self.provider.inbox.get_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider,
				exclude_expired = True,
				expired_only = False,
				overdue_only = False,
				unscheduled_only = True,
				exclude_unscheduled = False
			)
		elif self._RBTN_expired_messages.GetValue():
			_log.debug('loading expired messages only')
			self.__msgs = self.provider.inbox.get_messages (
				pk_patient = pk_patient,
				include_without_provider = include_without_provider,
				exclude_expired = False,
				expired_only = True,
				overdue_only = False,
				unscheduled_only = False,
				exclude_unscheduled = True,
				order_by = 'expiry_date DESC, importance DESC, received_when DESC'
			)

		_log.debug('total # of inbox msgs: %s', len(self.__msgs))

		items = []
		for m in self.__msgs:
			item = [_indicator[m['importance']]]
			item.append('%s: %s%s%s' % (
				m['received_when'].strftime('%Y-%m-%d'),
				m['modified_by'],
				gmTools.u_arrow2right,
				gmTools.coalesce(m['provider'], _('all'))
			))
			if m['due_date'] is None:
				item.append('')
			else:
				if m['is_expired'] is True:
					item.append(_('expired'))
				else:
					if m['is_overdue'] is True:
						item.append(_('%s overdue') % gmDateTime.format_interval_medically(m['interval_due']))
					else:
						item.append(_('due in %s') % gmDateTime.format_interval_medically(m['interval_due']))
			#pat
			if m['pk_patient'] is None:
				item.append('')
			else:
				item.append('%s, %s%s %s #%s' % (
					m['lastnames'],
					m['firstnames'],
					gmTools.coalesce(m['l10n_gender'], '', ' (%s)'),
					gmDateTime.format_dob(m['dob'], format = '%Y %b %d', none_string = ''),
					m['pk_patient']
				))
			item.append(m['comment'])
			item.append('%s - %s' % (m['l10n_category'], m['l10n_type']))
			items.append(item)

		_log.debug('# of list items created from msgs: %s', len(items))
		self._LCTRL_provider_inbox.set_string_items(items = items)
		self._LCTRL_provider_inbox.set_data(data = self.__msgs)
		self._LCTRL_provider_inbox.set_column_widths()
		self._TXT_inbox_item_comment.SetValue('')
		self.__update_greeting(len(items))

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_results_mod_db(self):
		_log.debug('reviewed_test_results_mod_db')
		self._on_message_inbox_mod_db()
	#--------------------------------------------------------
	def _on_identity_mod_db(self):
		_log.debug('identity_mod_db')
		self._on_message_inbox_mod_db()
	#--------------------------------------------------------
	def _on_doc_obj_review_mod_db(self):
		_log.debug('doc_obj_review_mod_db')
		self._on_message_inbox_mod_db()
	#--------------------------------------------------------
	def _on_doc_mod_db(self):
		_log.debug('doc_mod_db')
		self._on_message_inbox_mod_db()
	#--------------------------------------------------------
	def _on_message_inbox_mod_db(self, *args, **kwargs):
		_log.debug('message_inbox_mod_db')
		self._schedule_data_reget()
		gmDispatcher.send(signal = 'request_user_attention', msg = _('Please check your GNUmed Inbox !'))
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		_log.debug('post_patient_selection')
		self._CHBOX_active_patient.Enable()
		self._schedule_data_reget()

	#--------------------------------------------------------
	def __msg_activated(self, evt):

		try:
			msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		except IndexError:
			_log.exception('problem with provider inbox item data access')
			gmGuiHelpers.gm_show_error (
				title = _('handling provider inbox item'),
				error = _('There was a problem accessing the message data.')
			)
			_log.debug('effecting inbox reload')
			wx.CallAfter(self.__populate_inbox)
			return False

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
	def __msg_selected(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		if msg['data'] is None:
			tmp = _('Message: %s') % msg['comment']
		else:
			tmp = _('Message: %s\nData: %s') % (msg['comment'], msg['data'])
		self._TXT_inbox_item_comment.SetValue(tmp)

	#--------------------------------------------------------
	def _extend_popup_menu(self, menu=None):
		tmp = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if tmp is None:
			return
		self.__focussed_msg = tmp

		if self.__focussed_msg['pk_patient'] is not None:
			menu_item = menu.Append(-1, _('Activate patient'))
			self.Bind(wx.EVT_MENU, self._on_goto_patient, menu_item)

		if not self.__focussed_msg['is_virtual']:
			menu_item = menu.Append(-1, _('Delete'))
			self.Bind(wx.EVT_MENU, self._on_delete_focussed_msg, menu_item)
			menu_item = menu.Append(-1, _('Edit'))
			self.Bind(wx.EVT_MENU, self._on_edit_focussed_msg, menu_item)

#		if self.__focussed_msg['pk_staff'] is not None:
#			# - distribute to other providers
#			item = menu.AppendItem(wx.MenuItem(menu, ID, _('Distribute')))
#			self.Bind(wx.EVT_MENU(menu, self._on_distribute_focussed_msg, item)

	#--------------------------------------------------------
	def _on_message_range_radiobutton_selected(self, event):
		self._TXT_inbox_item_comment.SetValue('')
		_log.debug('_on_message_range_radiobutton_selected')
		self.__populate_inbox()
	#--------------------------------------------------------
	def _on_active_patient_checkbox_ticked(self, event):
		self._TXT_inbox_item_comment.SetValue('')
		_log.debug('_on_active_patient_checkbox_ticked')
		self.__populate_inbox()
	#--------------------------------------------------------
	def _on_active_provider_checkbox_ticked(self, event):
		self._TXT_inbox_item_comment.SetValue('')
		_log.debug('_on_active_provider_checkbox_ticked')
		self.__populate_inbox()
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		edit_inbox_message(parent = self, message = None, single_entry = False)
	#--------------------------------------------------------
	def _get_msg_tooltip(self, msg):
		return msg.format()
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

		# message to a certain provider ?
		if self.__focussed_msg['pk_staff'] is not None:
			# do not delete messages to *other* providers
			if self.__focussed_msg['pk_staff'] != gmStaff.gmCurrentProvider()['pk_staff']:
				gmDispatcher.send(signal = 'statustext', msg = _('This message can only be deleted by [%s].') % self.__focussed_msg['provider'], beep = True)
				return False

		pk_patient = self.__focussed_msg['pk_patient']
		if pk_patient is not None:
			emr = gmClinicalRecord.cClinicalRecord(aPKey = pk_patient)
			epi = emr.add_episode(episode_name = 'administrative', is_open = False)
			soap_cat = gmTools.bool2subst (
				(self.__focussed_msg['category'] == 'clinical'),
				'u',
				None
			)
			narr = _('Deleted inbox message:\n%s') % self.__focussed_msg.format(with_patient = False)
			emr.add_clin_narrative(note = narr, soap_cat = soap_cat, episode = epi)
			gmDispatcher.send(signal = 'statustext', msg = _('Recorded deletion of inbox message in EMR.'), beep = False)

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
		print("now distributing")
		return True
	#--------------------------------------------------------
	def _goto_patient(self, pk_context=None, pk_patient=None):

		wx.BeginBusyCursor()
		msg = _('There is a message about patient [%s].\n\n'
			'However, I cannot find that\n'
			'patient in the GNUmed database.'
		) % pk_patient
		pat = None
		try:
			pat = gmPerson.cPerson(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			_log.exception('patient [%s] not found', pk_patient)
		finally:
			wx.EndBusyCursor()
		if pat is None:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		success = set_active_patient(patient = pat)
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
			pat = gmPerson.cPerson(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		success = set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		gmDispatcher.send(signal = 'display_widget', name = 'gmShowMedDocs', sort_mode = 'review')
		return True
	#--------------------------------------------------------
	def _goto_measurements_review(self, pk_context=None, pk_patient=None):

		msg = _('Supposedly there are unreviewed results\n'
			'for patient [%s]. However, I cannot find\n'
			'that patient in the GNUmed database.'
		) % pk_patient

		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cPerson(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		success = set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		gmDispatcher.send(signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return True
	#--------------------------------------------------------
	def _goto_vaccination_review(self, pk_context=None, pk_patient=None):

		msg = _('Supposedly there are conflicting vaccinations\n'
			'for patient [%s]. However, I cannot find\n'
			'that patient in the GNUmed database.'
		) % pk_patient

		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cPerson(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error(msg,	_('handling provider inbox item'))
			return False

		success = set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error(msg, _('handling provider inbox item'))
			return False

		wx.CallAfter(manage_vaccinations)

		return True

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	def test_message_inbox():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cProviderInboxPnl, -1)
#		app.MainLoop()

#	def test_msg_ea():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cInboxMessageEAPnl, -1)
#		app.MainLoop()


	#test_message_inbox()
#	test_msg_ea()

#============================================================
