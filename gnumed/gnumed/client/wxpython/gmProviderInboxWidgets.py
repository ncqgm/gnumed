"""GNUmed provider inbox handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmProviderInboxWidgets.py,v $
# $Id: gmProviderInboxWidgets.py,v 1.2 2006-01-22 18:10:52 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#import os.path, sys, re, time

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmWhoAmI
#, gmCfg, gmPG, gmMimeLib, gmExceptions
from Gnumed.business import gmProviderInbox
# gmPerson, gmMedDoc
#from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

_me = gmWhoAmI.cWhoAmI()

_indicator = {
	-1: '',
	0: '',
	1: '!'
}

#============================================================
class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl):
	def __init__(self, *args, **kwds):
		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		self.__init_ui_data()
	#--------------------------------------------------------
	def __init_ui_data(self):
		msg = _(
"""
	Welcome %(title)s %(lname)s !

Below find the currently pending items on your TODO list.

Have a nice day.

""") % {'title': _me.get_staff_title(), 'lname': _me.get_lastname()}

		self._msg_welcome.SetLabel(msg)

		self._LCTRL_provider_inbox.InsertColumn(0, '')
		self._LCTRL_provider_inbox.InsertColumn(1, _('category'))
		self._LCTRL_provider_inbox.InsertColumn(2, _('type'))
		self._LCTRL_provider_inbox.InsertColumn(3, _('message'))

		inbox = gmProviderInbox.cProviderInbox(provider_id=_me.get_staff_ID())
		msgs = inbox.get_messages()
		for msg in msgs:
			item_idx = self._LCTRL_provider_inbox.InsertItem(info=wx.ListItem())
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=0, label=_indicator[msg[0]])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=1, label=msg[1])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=2, label=msg[2])
			self._LCTRL_provider_inbox.SetStringItem(index = item_idx, col=3, label=msg[3])

#============================================================
# $Log: gmProviderInboxWidgets.py,v $
# Revision 1.2  2006-01-22 18:10:52  ncq
# - now really display messages from backend
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#