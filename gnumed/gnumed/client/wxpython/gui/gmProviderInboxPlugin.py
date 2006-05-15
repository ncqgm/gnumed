#=====================================================
# GNUmed provider inbox plugin
# later to evolve into a more complete "provider-centric hub"
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmProviderInboxPlugin.py,v $
# $Id: gmProviderInboxPlugin.py,v 1.2 2006-05-15 11:07:26 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

try:
    import wxversion
    import wx
except ImportError:
    from wxPython import wx

from Gnumed.wxpython import gmPlugin, gmProviderInboxWidgets

#======================================================================
class gmProviderInboxPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the provider inbox window."""

	tab_name = _('Inbox')

	def name(self):
		return gmProviderInboxPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmProviderInboxWidgets.cProviderInboxPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('tools', _('provider inbox'))

	def can_receive_focus(self):
		return 1
#======================================================================
# $Log: gmProviderInboxPlugin.py,v $
# Revision 1.2  2006-05-15 11:07:26  ncq
# - cleanup
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#