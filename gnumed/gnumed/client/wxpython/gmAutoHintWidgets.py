"""GNUmed auto/dynamic hints widgets.
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmAutoHints

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmDataPackWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.auto_hints')

#================================================================
def _display_clinical_reminders():

	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		return

	# reminders
	for msg in pat.overdue_messages:
		if msg['expiry_date'] is None:
			exp = ''
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
			gmTools.coalesce(msg['comment'], '', '\n%s\n'),
			gmTools.coalesce(msg['data'], '', '\n%s\n'),
			pat['description_gender'],
			msg['modified_by']
		)
		gmGuiHelpers.gm_show_warning (
			aTitle = _('Clinical reminder'),
			aMessage = txt
		)

	# dynamic hints
	hints2aggregate = []
	emr = pat.emr
	hint_dlg = cDynamicHintDlg(wx.GetApp().GetTopWindow(), -1)
	# single-hint popups
	for hint in emr.dynamic_hints:
		if hint['popup_type'] == 0:
			continue
		if hint['popup_type'] == 2:
			hints2aggregate.append(hint)
			continue
		hint_dlg.hint = hint
		if hint_dlg.ShowModal() == wx.ID_APPLY:
			hint.suppress (
				rationale = hint_dlg.rationale.strip(),
				pk_encounter = emr.current_encounter['pk_encounter']
			)
	hint_dlg.DestroyLater()
	# aggregate popup
	if len(hints2aggregate) > 0:
		hints_dlg = cDynamicHintListDlg(wx.GetApp().GetTopWindow(), -1)
		hints_dlg.pk_encounter = emr.current_encounter['pk_encounter']
		hints_dlg.hints = hints2aggregate
		hints_dlg.ShowModal()
		hints_dlg.DestroyLater()

	return

gmDispatcher.connect(signal = 'post_patient_selection', receiver = _display_clinical_reminders)

#================================================================
def edit_dynamic_hint(parent=None, hint=None, single_entry=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cAutoHintEAPnl(parent, -1)
	ea.data = hint
	ea.mode = gmTools.coalesce(hint, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(hint, _('Adding automatic dynamic hint'), _('Editing automatic dynamic hint')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#================================================================
def manage_dynamic_hints(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def manage_data_packs(item):
		gmDataPackWidgets.manage_data_packs(parent = parent)
		return True
	#------------------------------------------------------------
	def edit_hint(hint=None):
		return edit_dynamic_hint(parent = parent, hint = hint, single_entry = (hint is not None))
	#------------------------------------------------------------
	def del_hint(hint=None):
		if hint is None:
			return False
		really_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting automatic dynamic hint'),
			question = _('Really delete this dynamic hint ?\n\n [%s]') % hint['title']
		)
		if not really_delete:
			return False

		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('deleting a dynamic hint'))
		if conn is None:
			return False
		gmAutoHints.delete_dynamic_hint(link_obj = conn, pk_hint = hint['pk_auto_hint'])
		conn.commit()
		conn.close()
		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		hints = gmAutoHints.get_dynamic_hints(order_by = 'is_active DESC, source, hint')
		items = [ [
			gmTools.bool2subst(h['is_active'], gmTools.u_checkmark_thin, ''),
			h['title'],
			h['source'][:30],
			h['hint'][:60],
			gmTools.coalesce(h['url'], '')[:60],
			h['lang'],
			h['pk_auto_hint']
		] for h in hints ]
		lctrl.set_string_items(items)
		lctrl.set_data(hints)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nDynamic hints registered with GNUmed.\n'),
		caption = _('Showing dynamic hints.'),
		columns = [ _('Active'), _('Title'), _('Source'), _('Hint'), 'URL', _('Language'), '#' ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit_hint,
		new_callback = edit_hint,
		delete_callback = del_hint,
#		left_extra_button = (
#			_('(De)-Activate'),
#			_('Toggle activation of the selected hint'),
#			toggle_activation
#		),
		# button to show DB schema
		right_extra_button = (
			_('Data packs'),
			_('Browse and install automatic dynamic hints data packs'),
			manage_data_packs
		),
		list_tooltip_callback = get_tooltip
	)

#================================================================
from Gnumed.wxGladeWidgets import wxgDynamicHintDlg

class cDynamicHintDlg(wxgDynamicHintDlg.wxgDynamicHintDlg):

	def __init__(self, *args, **kwargs):

		try:
			self.__hint = kwargs['hint']
			del kwargs['hint']
		except KeyError:
			self.__hint = None
		wxgDynamicHintDlg.wxgDynamicHintDlg.__init__(self, *args, **kwargs)
		self.__init_ui()
	#------------------------------------------------------------
	def _get_hint(self):
		return self.__hint

	def _set_hint(self, hint):
		self.__hint = hint
		self.__refresh()

	hint = property(_get_hint, _set_hint)
	#------------------------------------------------------------
	def _get_rationale(self):
		return self._TCTRL_rationale.GetValue().strip()

	rationale = property(_get_rationale, lambda x:x)

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._TCTRL_rationale.add_callback_on_modified(callback = self._on_rationale_modified)

	#------------------------------------------------------------
	def __refresh(self):
		if self.__hint is None:
			self._TCTRL_title.SetValue('')
			self._TCTRL_hint.SetValue('')
			self._URL_info.SetURL('')
			self._URL_info.Disable()
			self._TCTRL_source.SetValue('')
			self._LBL_previous_rationale.Hide()
			self._TCTRL_previous_rationale.Hide()
		else:
			self._TCTRL_title.SetValue(self.__hint['title'])
			self._TCTRL_hint.SetValue('%s%s' % (
				self.__hint['hint'],
				gmTools.coalesce(self.__hint['recommendation'], '', '\n\n%s')
			))
			if self.__hint['url'] is None:
				self._URL_info.SetURL('')
				self._URL_info.Disable()
			else:
				self._URL_info.SetURL(self.__hint['url'])
				self._URL_info.Enable()
			self._TCTRL_source.SetValue(_('By: %s') % self.__hint['source'])
			if self.__hint['rationale4suppression'] is None:
				self._LBL_previous_rationale.Hide()
				self._TCTRL_previous_rationale.Hide()
				self._BTN_transfer_previous_rationale.Hide()
				self._BTN_transfer_previous_rationale.Disable()
			else:
				self._LBL_previous_rationale.Show()
				self._TCTRL_previous_rationale.Show()
				self._TCTRL_previous_rationale.SetValue(self.__hint['rationale4suppression'])
				self._BTN_transfer_previous_rationale.Show()
				self._BTN_transfer_previous_rationale.Enable()

		self._TCTRL_rationale.SetValue('')
		self._BTN_suppress.Disable()
		self._TCTRL_rationale.SetFocus()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_rationale_modified(self):
		if self._TCTRL_rationale.GetValue().strip() == '':
			self._BTN_suppress.Disable()
			self._BTN_OK.SetDefault()
		else:
			self._BTN_suppress.Enable()
			self._BTN_suppress.SetDefault()

	#------------------------------------------------------------
	def _on_suppress_button_pressed(self, event):
		event.Skip()
		if self.__hint is None:
			return
		val = self._TCTRL_rationale.GetValue().strip()
		if val == '':
			return
		if self.IsModal():
			self.EndModal(wx.ID_APPLY)
		else:
			self.Close()

	#------------------------------------------------------------
	def _on_manage_hints_button_pressed(self, event):
		event.Skip()
		manage_dynamic_hints(parent = self)

	#------------------------------------------------------------
	def _on_transfer_previous_rationale_button_pressed(self, event):
		event.Skip()
		prev = self._TCTRL_previous_rationale.Value.strip()
		if prev == u'':
			return
		self._TCTRL_rationale.Value = prev

#================================================================
from Gnumed.wxGladeWidgets import wxgDynamicHintListDlg

class cDynamicHintListDlg(wxgDynamicHintListDlg.wxgDynamicHintListDlg):

	def __init__(self, *args, **kwargs):

		try:
			self.__hints = kwargs['hints']
			del kwargs['hints']
		except KeyError:
			self.__hints = None
		wxgDynamicHintListDlg.wxgDynamicHintListDlg.__init__(self, *args, **kwargs)
		self.__pk_encounter = None
		self.__init_ui()

	#------------------------------------------------------------
	def _get_hints(self):
		return self.__hints

	def _set_hints(self, hints):
		if len(hints) == 0:
			hints = None
		self.__hints = hints
		self.__refresh()

	hints = property(_get_hints, _set_hints)

	#------------------------------------------------------------
	def _set_pk_encounter(self, pk_encounter):
		self.__pk_encounter = pk_encounter

	pk_encounter = property(lambda x:x, _set_pk_encounter)

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_hints.set_columns([_('Hint'), _('Source')])
		self._LCTRL_hints.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_hints.set_resize_column(column = 0)
		self._LCTRL_hints.select_callback = self._on_hint_selected
		self._LCTRL_hints.deselect_callback = self._on_hint_deselected
		self._TCTRL_rationale.add_callback_on_modified(callback = self._on_rationale_modified)

	#------------------------------------------------------------
	def __refresh(self):
		if self.__hints is None:
			self._LCTRL_hints.set_string_items()
			self._TCTRL_hint.SetValue('')
			self._URL_info.SetURL('')
			self._URL_info.Disable()
			self._TCTRL_source.SetValue('')
			self._TCTRL_rationale.SetValue('')
			self._BTN_suppress.Disable()
			self._LBL_previous_rationale.Hide()
			self._TCTRL_previous_rationale.Hide()
			self._LCTRL_hints.SetFocus()
			return

		priority_hints = []
		non_priority_hints = []
		for hint in self.__hints:
			if hint['highlight_as_priority']:
				priority_hints.append(hint)
			else:
				non_priority_hints.append(hint)

		ordered_hints = []
		ordered_hints.extend(priority_hints)
		ordered_hints.extend(non_priority_hints)

		self._LCTRL_hints.set_string_items([ [h['title'], h['source']] for h in ordered_hints ])
		self._LCTRL_hints.set_data(ordered_hints)
		for idx in range(len(priority_hints)):
			self._LCTRL_hints.SetItemTextColour(idx, wx.Colour('YELLOW'))
		self._LCTRL_hints.Select(0)

	#------------------------------------------------------------
	def _on_hint_selected(self, evt):
		hint = self._LCTRL_hints.get_selected_item_data(only_one = True)

		self._TCTRL_hint.SetValue('%s%s' % (
			hint['hint'],
			gmTools.coalesce(hint['recommendation'], '', '\n\n%s')
		))
		if hint['url'] is None:
			self._URL_info.SetURL('')
			self._URL_info.Disable()
		else:
			self._URL_info.SetURL(hint['url'])
			self._URL_info.Enable()
		self._TCTRL_source.SetValue(_('By: %s') % hint['source'])
		self._TCTRL_rationale.SetValue('')
		self._BTN_suppress.Disable()

		if hint['rationale4suppression'] is None:
			self._LBL_previous_rationale.Hide()
			self._TCTRL_previous_rationale.Hide()
			self._TCTRL_previous_rationale.SetValue('')
		else:
			self._LBL_previous_rationale.Show()
			self._TCTRL_previous_rationale.SetValue(hint['rationale4suppression'])
			self._TCTRL_previous_rationale.Show()

		self._TCTRL_rationale.SetFocus()

	#------------------------------------------------------------
	def _on_hint_deselected(self, evt):
		self._TCTRL_hint.SetValue('')
		self._URL_info.SetURL('')
		self._URL_info.Disable()
		self._TCTRL_source.SetValue('')
		self._TCTRL_rationale.SetValue('')
		self._LBL_previous_rationale.Hide()
		self._TCTRL_previous_rationale.Hide()
		self._TCTRL_previous_rationale.SetValue('')
		self._BTN_suppress.Disable()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_rationale_modified(self):
		if self._TCTRL_rationale.GetValue().strip() == '':
			self._BTN_suppress.Disable()
		else:
			self._BTN_suppress.Enable()

	#------------------------------------------------------------
	def _on_suppress_button_pressed(self, event):
		event.Skip()
		val = self._TCTRL_rationale.GetValue().strip()
		if val == '':
			return
		hint = self._LCTRL_hints.get_selected_item_data(only_one = True)
		suppressed = hint.suppress (
			rationale = val,
			pk_encounter = self.__pk_encounter
		)
		if not suppressed:
			self.StatusText = _('Cannot suppress hint.')
			return False
		if len(self.__hints) == 1:
			# singular hint now suppressed -> close
			if self.IsModal():
				self.EndModal(wx.ID_APPLY)
			else:
				self.Close()
		self.StatusText = _('Hint now suppressed in this patient.')
		pk_of_suppressed_hint = hint['pk_auto_hint']
		remaining_hints = [ h for h in self.__hints if h['pk_auto_hint'] != pk_of_suppressed_hint ]
		self.hints = remaining_hints

	#------------------------------------------------------------
	def _on_manage_hints_button_pressed(self, event):
		event.Skip()
		manage_dynamic_hints(parent = self)

#================================================================
from Gnumed.wxGladeWidgets import wxgAutoHintEAPnl

class cAutoHintEAPnl(wxgAutoHintEAPnl.wxgAutoHintEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['hint']
			del kwargs['hint']
		except KeyError:
			data = None

		wxgAutoHintEAPnl.wxgAutoHintEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._TCTRL_source.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_source, valid = False)
			self.StatusText = _('No entry in field <Source>.')
			self._TCTRL_source.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_source, valid = True)

		if self._TCTRL_query.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_query, valid = False)
			self.StatusText = _('No entry in field <Conditions>.')
			self._TCTRL_query.SetFocus()
		else:
			# FIXME: run SQL
			self.display_tctrl_as_valid(tctrl = self._TCTRL_query, valid = True)

		if self._TCTRL_hint.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_hint, valid = False)
			self.StatusText = _('No entry in field <Description>.')
			self._TCTRL_hint.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_hint, valid = True)

		if self._TCTRL_title.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_title, valid = False)
			self.StatusText = _('No entry in field <Title>.')
			self._TCTRL_title.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_title, valid = True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('creating a new dynamic hint'))
		if conn is None:
			return False

		curs = conn.cursor()
		data = gmAutoHints.create_dynamic_hint (
			link_obj = curs,		# it seems this MUST be a cursor or else the successfully created row will not show up -- but why ?!?
			query = self._TCTRL_query.GetValue().strip(),
			title = self._TCTRL_title.GetValue().strip(),
			hint = self._TCTRL_hint.GetValue().strip(),
			source = self._TCTRL_source.GetValue().strip()
		)
		curs.close()
		data['url'] = self._TCTRL_url.GetValue().strip()
		data['recommendation_query'] = self._TCTRL_recommendation_query.GetValue().strip()
		data['is_active'] = self._CHBOX_is_active.GetValue()
		data['highlight_as_priority'] = self._CHBOX_highlight.GetValue()
		if self._RBTN_popup_none.GetValue() is True:
			data['popup_type'] = 0
		elif self._RBTN_popup_single.GetValue() is True:
			data['popup_type'] = 1
		elif self._RBTN_popup_multiple.GetValue() is True:
			data['popup_type'] = 2
		else:
			raise ValueError('no popup type radio button selected - should be impossible')
		data.save(conn = conn)
		conn.commit()
		conn.close()

		self.data = data

		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('updating an existing dynamic hint'))
		if conn is None:
			return False

		self.data['title'] = self._TCTRL_title.GetValue().strip()
		self.data['hint'] = self._TCTRL_hint.GetValue().strip()
		self.data['query'] = self._TCTRL_query.GetValue().strip()
		self.data['source'] = self._TCTRL_source.GetValue().strip()
		self.data['url'] = self._TCTRL_url.GetValue().strip()
		self.data['recommendation_query'] = self._TCTRL_recommendation_query.GetValue().strip()
		self.data['is_active'] = self._CHBOX_is_active.GetValue()
		self.data['highlight_as_priority'] = self._CHBOX_highlight.GetValue()
		if self._RBTN_popup_none.GetValue() is True:
			self.data['popup_type'] = 0
		elif self._RBTN_popup_single.GetValue() is True:
			self.data['popup_type'] = 1
		elif self._RBTN_popup_multiple.GetValue() is True:
			self.data['popup_type'] = 2
		else:
			raise ValueError('no popup type radio button selected - should be impossible')
		self.data.save(conn = conn)
		conn.commit()
		conn.close()

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_title.SetValue('')
		self._TCTRL_hint.SetValue('')
		self._TCTRL_query.SetValue('')
		self._TCTRL_recommendation_query.SetValue('')
		self._TCTRL_source.SetValue('')
		self._TCTRL_url.SetValue('')
		self._CHBOX_is_active.SetValue(True)
		self._CHBOX_highlight.SetValue(True)
		self._RBTN_popup_single.SetValue(True)

		self._TCTRL_title.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._TCTRL_source.SetValue(self.data['source'])

		self._TCTRL_title.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_title.SetValue(self.data['title'])
		self._TCTRL_hint.SetValue(self.data['hint'])
		self._TCTRL_query.SetValue(self.data['query'])
		self._TCTRL_recommendation_query.SetValue(gmTools.coalesce(self.data['recommendation_query'], ''))
		self._TCTRL_source.SetValue(self.data['source'])
		self._TCTRL_url.SetValue(gmTools.coalesce(self.data['url'], ''))
		self._CHBOX_is_active.SetValue(self.data['is_active'])
		self._CHBOX_highlight.SetValue(self.data['highlight_as_priority'])
		if self.data['popup_type'] == 0:
			self._RBTN_popup_none.SetValue(True)
		elif self.data['popup_type'] == 1:
			self._RBTN_popup_single.SetValue(True)
		elif self.data['popup_type'] == 2:
			self._RBTN_popup_multiple.SetValue(True)
		else:
			raise ValueError('invalid popup type value [%s] - should be impossible' % self.data['popup_type'])

		self._TCTRL_query.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_check_url_button_pressed(self, event):
		url = self._TCTRL_url.GetValue().strip()
		if url == '':
			return
		if not gmNetworkTools.open_url_in_browser(url, new = 2, autoraise = True):
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = False)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = True)

#================================================================
def manage_suppressed_hints(parent=None, pk_identity=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def get_tooltip(item):
		if item is None:
			return None
		return item.format()
	#------------------------------------------------------------
	def manage_hints(item):
		manage_dynamic_hints(parent = parent)
		return True
	#------------------------------------------------------------
	def del_hint(hint=None):
		if hint is None:
			return False
		really_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting suppressed dynamic hint'),
			question = _('Really delete the suppression of this dynamic hint ?\n\n [%s]') % hint['title']
		)
		if not really_delete:
			return False
		gmAutoHints.delete_suppressed_hint(pk_suppressed_hint = hint['pk_suppressed_hint'])
		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		hints = gmAutoHints.get_suppressed_hints(pk_identity = pk_identity, order_by = 'title')
		items = [ [
			h['title'],
			gmDateTime.pydt_strftime(h['suppressed_when'], '%Y %b %d'),
			h['suppressed_by'],
			h['rationale'],
			gmTools.bool2subst(h['is_active'], gmTools.u_checkmark_thin, ''),
			h['source'][:30],
			gmTools.coalesce(h['url'], '')[:60],
			h['pk_hint']
		] for h in hints ]
		lctrl.set_string_items(items)
		lctrl.set_data(hints)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nDynamic hints suppressed in this patient.\n'),
		caption = _('Showing suppressed dynamic hints.'),
		columns = [ _('Title'), _('When'), _('By'), _('Rationale'), _('Active'), _('Source'), 'URL', 'Hint #' ],
		single_selection = True,
		ignore_OK_button = True,
		refresh_callback = refresh,
		delete_callback = del_hint,
		right_extra_button = (
			_('Manage hints'),
			_('Manage automatic dynamic hints'),
			manage_hints
		),
		list_tooltip_callback = get_tooltip
	)

#================================================================
# main
#================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

#	def test_message_inbox():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cProviderInboxPnl, -1)
#		app.MainLoop()

#	def test_msg_ea():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cInboxMessageEAPnl, -1)
#		app.MainLoop()

	#test_message_inbox()
	#test_msg_ea()
