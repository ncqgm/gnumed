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
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmDataPackWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.auto_hints')

#================================================================
def _display_clinical_reminders():
	wx.CallAfter(__display_clinical_reminders)

gmDispatcher.connect(signal = u'post_patient_selection', receiver = _display_clinical_reminders)

def __display_clinical_reminders():
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		return
	for msg in pat.overdue_messages:
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
		txt = u'%s\n\n%s\n\n          %s' % (
			hint['title'],
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

#================================================================
def edit_dynamic_hint(parent=None, hint=None, single_entry=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cAutoHintEAPnl(parent = parent, id = -1)
	ea.data = hint
	ea.mode = gmTools.coalesce(hint, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(hint, _('Adding automatic dynamic hint'), _('Editing automatic dynamic hint')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
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
		gmProviderInbox.delete_dynamic_hint(link_obj = conn, pk_hint = hint['pk'])
		conn.commit()
		conn.close()
		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		hints = gmProviderInbox.get_dynamic_hints(order_by = u'is_active DESC, source, hint')
		items = [ [
			gmTools.bool2subst(h['is_active'], gmTools.u_checkmark_thin, u''),
			h['title'],
			h['source'][:30],
			h['hint'][:60],
			gmTools.coalesce(h['url'], u'')[:60],
			h['lang'],
			h['pk']
		] for h in hints ]
		lctrl.set_string_items(items)
		lctrl.set_data(hints)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nDynamic hints registered with GNUmed.\n'),
		caption = _('Showing dynamic hints.'),
		columns = [ _('Active'), _('Title'), _('Source'), _('Hint'), u'URL', _('Language'), u'#' ],
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

		if self._TCTRL_source.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_source, valid = False)
			self.status_message = _('No entry in field <Source>.')
			self._TCTRL_source.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_source, valid = True)

		if self._TCTRL_query.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_query, valid = False)
			self.status_message = _('No entry in field <Conditions>.')
			self._TCTRL_query.SetFocus()
		else:
			# FIXME: run SQL
			self.display_tctrl_as_valid(tctrl = self._TCTRL_query, valid = True)

		if self._TCTRL_hint.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_hint, valid = False)
			self.status_message = _('No entry in field <Description>.')
			self._TCTRL_hint.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_hint, valid = True)

		if self._TCTRL_title.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_title, valid = False)
			self.status_message = _('No entry in field <Title>.')
			self._TCTRL_title.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_title, valid = True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('creating a new dynamic hint'))
		if conn is None:
			return False

		data = gmProviderInbox.create_dynamic_hint (
			link_obj = conn,
			query = self._TCTRL_query.GetValue().strip(),
			title = self._TCTRL_title.GetValue().strip(),
			hint = self._TCTRL_hint.GetValue().strip(),
			source = self._TCTRL_source.GetValue().strip()
		)
		url = self._TCTRL_url.GetValue().strip()
		if url != u'':
			data['url'] = url
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
		self.data['is_active'] = self._CHBOX_is_active.GetValue()
		self.data.save(conn = conn)
		conn.commit()
		conn.close()

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_title.SetValue(u'')
		self._TCTRL_hint.SetValue(u'')
		self._TCTRL_query.SetValue(u'')
		self._TCTRL_source.SetValue(u'')
		self._TCTRL_url.SetValue(u'')
		self._CHBOX_is_active.SetValue(True)

		self._TCTRL_title.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._TCTRL_source.SetValue(self.data['source'])
		self._CHBOX_is_active.SetValue(True)

		self._TCTRL_title.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_title.SetValue(self.data['title'])
		self._TCTRL_hint.SetValue(self.data['hint'])
		self._TCTRL_query.SetValue(self.data['query'])
		self._TCTRL_source.SetValue(self.data['source'])
		self._TCTRL_url.SetValue(gmTools.coalesce(self.data['url'], u''))
		self._CHBOX_is_active.SetValue(self.data['is_active'])

		self._TCTRL_query.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_check_url_button_pressed(self, event):
		url = self._TCTRL_url.GetValue().strip()
		if url == u'':
			return
		if not gmNetworkTools.open_url_in_browser(url, new = 2, autoraise = True):
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = False)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = True)
#================================================================


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
