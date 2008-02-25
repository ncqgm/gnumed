"""GNUmed provider inbox handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmProviderInboxWidgets.py,v $
# $Id: gmProviderInboxWidgets.py,v 1.23 2008-02-25 17:40:45 ncq Exp $
__version__ = "$Revision: 1.23 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmTools, gmCfg
from Gnumed.business import gmPerson, gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets, gmPlugin, gmRegetMixin
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

_indicator = {
	-1: '',
	0: '',
	1: '!'
}

#============================================================
# practice related widgets 
#============================================================
# FIXME: this should be moved elsewhere !

#============================================================
def configure_workplace_plugins(parent=None):

	#-----------------------------------
	def edit(workplace=None):

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
				'\nSelect the plugins to load for the workplace "%s".\n'
				'\n'
				'Note that he plugins currently associated with\n'
				'this workplace are preselected.\n'
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
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	curr_workplace = gmSurgery.gmCurrentPractice().active_workplace
	workplaces = gmSurgery.gmCurrentPractice().workplaces
	try:
		sels = [workplaces.index(curr_workplace)]
	except ValueError:
		sels = []

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _(
			'\nSelect the workplace to configure below.\n'
			'\n'
			'The currently active workplace is preselected.\n'
		),
		caption = _('Configuring GNUmed workplaces ...'),
		choices = workplaces,
		selections = sels,
		columns = [_('Workplace')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit
	)
#============================================================
class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl, gmRegetMixin.cRegetOnPaintMixin):

	_item_handlers = {}
	#--------------------------------------------------------
	def __init__(self, *args, **kwds):
		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.provider = gmPerson.gmCurrentProvider()
		self.__init_ui()
		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__populate_inbox()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'provider_inbox_mod_db', receiver = self._on_provider_inbox_mod_db)
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.set_columns([u'', _('category'), _('type'), _('message')])

		msg = _("""
		Welcome %(title)s %(lname)s !

	Below find the new messages in your Inbox.
""") % {
			'title': gmTools.coalesce (
				self.provider['title'],
				gmPerson.map_gender2salutation(self.provider['gender'])
			),
			'lname': self.provider['lastnames']
		}

		self._msg_welcome.SetLabel(msg)
	#--------------------------------------------------------
	def __populate_inbox(self):
		"""Fill UI with data."""
		self.__msgs = self.provider.inbox.messages

		self._LCTRL_provider_inbox.set_string_items(items = [ [_indicator[m[0]], m[1], m[2], m[3]] for m in self.__msgs ])
		self._LCTRL_provider_inbox.set_data(data = self.__msgs)
		self._LCTRL_provider_inbox.set_column_widths()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_provider_inbox_mod_db(self, *args, **kwargs):
		wx.CallAfter(self._schedule_data_reget)
		gmDispatcher.send(signal = u'request_user_attention', msg = _('Please check your GNUmed Inbox !'))
	#--------------------------------------------------------
	def _lst_item_activated(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		handler_key = '%s.%s' % (msg[4], msg[5])
		try:
			handle_item = cProviderInboxPnl._item_handlers[handler_key]
		except KeyError:
			gmGuiHelpers.gm_show_warning (
				_(
"""Unknown message type:

 [%s]

Don't know what to do with it.
Leaving message in inbox.""") % handler_key,
				_('handling provider inbox item')
			)
			return False
		if not handle_item(pk_context = msg[6]):
			_log.Log(gmLog.lErr, 'item handler returned "false"')
			_log.Log(gmLog.lErr, 'handler key: [%s]' % handler_key)
			_log.Log(gmLog.lErr, 'message: %s' % str(msg))
			return False
		return True
	#--------------------------------------------------------
	def _lst_item_focused(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		if msg[7] is None:
			tmp = _('Message: %s') % msg[3]
		else:
			tmp = _('Message: %s\nData: %s') % (msg[3], msg[7])
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
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('delete message')))
		wx.EVT_MENU(menu, ID, self._on_delete_focussed_msg)
		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	# item handlers
	#--------------------------------------------------------
	def _on_delete_focussed_msg(self, evt):
		if not self.provider.inbox.delete_message(self.__focussed_msg[8]):
			gmDispatcher.send(signal='statustext', msg=_('Cannot remove message from Inbox.'))
			return False
		return True
	#--------------------------------------------------------
	def _goto_doc_review(self, pk_context=None):
		if not gmPerson.set_active_patient(patient=gmPerson.cIdentity(aPK_obj=pk_context)):
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents'
				  'for patient [%s]. However, I cannot find'
				  'that patient in the GNUmed database.'
				) % pk_context,
				_('handling provider inbox item')
			)
			return False
		gmDispatcher.send(signal = 'display_widget', name = 'gmShowMedDocs', sort_mode = 'review')
		return True
#============================================================
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	def test_configure_wp_plugins():
		app = wx.PyWidgetTester(size = (400, 300))
		configure_workplace_plugins()

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		test_configure_wp_plugins()

#============================================================
# $Log: gmProviderInboxWidgets.py,v $
# Revision 1.23  2008-02-25 17:40:45  ncq
# - establish db cfg instance early enough
#
# Revision 1.22  2008/01/30 14:03:42  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.21  2008/01/27 21:18:45  ncq
# - don't crash on trying to edit module-less workplace
#
# Revision 1.20  2008/01/05 16:41:27  ncq
# - remove logging from gm_show_*()
#
# Revision 1.19  2007/11/28 11:56:30  ncq
# - better logging
#
# Revision 1.18  2007/11/23 23:36:38  ncq
# - finish configure_workplace_plugins()
#
# Revision 1.17  2007/11/02 13:59:33  ncq
# - request user attention when new item arrives
#
# Revision 1.16  2007/10/30 12:51:45  ncq
# - make it a reget mixin child
# - cleanup
# - listen on backend changes
#
# Revision 1.15  2007/10/08 13:05:10  ncq
# - use gmListWidgets.cReportListCtrl
# - fix right-click on empty message list crashes
# - start test suite
# - start configure_workplace_plugins()
#
# Revision 1.14  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.13  2007/05/14 13:11:25  ncq
# - use statustext() signal
#
# Revision 1.12  2007/01/04 22:52:34  ncq
# - show proper salutation for people without title
#
# Revision 1.11  2006/12/17 20:46:24  ncq
# - cleanup
#
# Revision 1.10  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.9  2006/05/28 16:19:54  ncq
# - repopulate_ui() needed for receive_focus() from plugin base class
#
# Revision 1.8  2006/05/20 18:55:21  ncq
# - calculate handler via original category/type not i18ned one
#
# Revision 1.7  2006/05/16 15:56:03  ncq
# - properly resize columns
#
# Revision 1.6  2006/05/15 14:46:38  ncq
# - implement message deletion via context menu popup
#
# Revision 1.5  2006/05/15 13:39:31  ncq
# - cleanup
#
# Revision 1.4  2006/05/12 22:04:22  ncq
# - add _populate_with_data()
# - fully implement _goto_doc_review()
#
# Revision 1.3  2006/05/12 12:21:58  ncq
# - implement double-click item handling
# - use gmCurrentProvider
# - show message on item focused
#
# Revision 1.2  2006/01/22 18:10:52  ncq
# - now really display messages from backend
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#