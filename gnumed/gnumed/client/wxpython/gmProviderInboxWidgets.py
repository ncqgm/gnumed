"""GNUmed provider inbox handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmProviderInboxWidgets.py,v $
# $Id: gmProviderInboxWidgets.py,v 1.8 2006-05-20 18:55:21 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#import os.path, sys, re, time

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmSignals
from Gnumed.business import gmProviderInbox, gmPerson
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

_indicator = {
	-1: '',
	0: '',
	1: '!'
}

#============================================================
class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl):

	_item_handlers = {}
	#--------------------------------------------------------
	def __init__(self, *args, **kwds):
		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		self.__init_ui()
		self._populate_with_data()
		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.InsertColumn(0, '')
		self._LCTRL_provider_inbox.InsertColumn(1, _('category'))
		self._LCTRL_provider_inbox.InsertColumn(2, _('type'))
		self._LCTRL_provider_inbox.InsertColumn(3, _('message'))

		_me = gmPerson.gmCurrentProvider()
		msg = _("""
		Welcome %(title)s %(lname)s !

	Below find the new messages in your Inbox.
""") % {'title': _me['title'], 'lname': _me['lastnames']}

		self._msg_welcome.SetLabel(msg)
	#--------------------------------------------------------
	# gmPlugin.cNotebookPlugin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Fill UI with data."""
		self._LCTRL_provider_inbox.DeleteAllItems()

		inbox = gmProviderInbox.cProviderInbox()
		self.__msgs = inbox.get_messages()
		msgs = self.__msgs[0:]
		msgs.reverse()
		for msg in msgs:
			item_idx = self._LCTRL_provider_inbox.InsertItem(info=wx.ListItem())
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=0, label=_indicator[msg[0]])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=1, label=msg[1])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=2, label=msg[2])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=3, label=msg[3])

		# FIXME: isn't there a way to say "resize all cols" ?
		self._LCTRL_provider_inbox.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
		self._LCTRL_provider_inbox.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
		self._LCTRL_provider_inbox.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE)
		self._LCTRL_provider_inbox.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _lst_item_activated(self, evt):
		msg = self.__msgs[evt.m_itemIndex]
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
				_('handling provider inbox item'),
				gmLog.lWarn
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
		msg = self.__msgs[evt.m_itemIndex]
		if msg[7] is None:
			tmp = _('Message: %s') % msg[3]
		else:
			tmp = _('Message: %s\nData: %s') % (msg[3], msg[7])
		self._TXT_inbox_item_comment.SetValue(tmp)
	#--------------------------------------------------------
	def _lst_item_right_clicked(self, evt):
		self.__focussed_msg = self.__msgs[evt.m_itemIndex]
		# build menu
		menu = wx.Menu(title = _('Inbox Message menu'))
		# - delete message
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, 'delete message'))
		wx.EVT_MENU(menu, ID, self._on_delete_focussed_msg)
		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	# item handlers
	#--------------------------------------------------------
	def _on_delete_focussed_msg(self, evt):
		inbox = gmProviderInbox.cProviderInbox()
		if not inbox.delete_message(self.__focussed_msg[8]):
			gmGuiHelpers.gm_beep_statustext (
				_('Cannot remove message from Inbox.')
			)
			return False
		self._populate_with_data()
		return True
	#--------------------------------------------------------
	def _goto_doc_review(self, pk_context=None):
		if not gmPerson.set_active_patient(patient=gmPerson.cIdentity(aPK_obj=pk_context)):
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents'
				  'for patient [%s]. However, I cannot find'
				  'that patient in the GNUmed database.'
				) % pk_context,
				_('handling provider inbox item'),
				gmLog.lErr
			)
			return False
		gmDispatcher.send(gmSignals.display_widget(), name='gmShowMedDocs', sort_mode='review')
		return True
#============================================================
# $Log: gmProviderInboxWidgets.py,v $
# Revision 1.8  2006-05-20 18:55:21  ncq
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