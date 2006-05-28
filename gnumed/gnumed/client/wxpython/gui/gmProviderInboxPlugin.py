#=====================================================
# GNUmed provider inbox plugin
# later to evolve into a more complete "provider-centric hub"
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmProviderInboxPlugin.py,v $
# $Id: gmProviderInboxPlugin.py,v 1.5 2006-05-28 16:15:27 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

try:
    import wxversion
    import wx
except ImportError:
    from wxPython import wx

from Gnumed.wxpython import gmPlugin, gmProviderInboxWidgets

#======================================================================
class gmProviderInboxPlugin(gmPlugin.cNotebookPlugin, gmPlugin.cPatientChange_PluginMixin):
	"""Plugin to encapsulate the provider inbox window."""

	tab_name = _('Inbox')
	#--------------------------------------------------------
	def __init__(self):
		gmPlugin.cNotebookPlugin.__init__(self)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmProviderInboxPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmProviderInboxWidgets.cProviderInboxPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('tools', _('provider inbox'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
	#--------------------------------------------------------
	# gmPlugin.cPatientChange_PluginMixin API
	#--------------------------------------------------------
	def _pre_patient_selection(self, **kwds):
		pass
	#--------------------------------------------------------
	def _post_patient_selection(self, **kwds):
		self.Raise()
		return True
#======================================================================
# $Log: gmProviderInboxPlugin.py,v $
# Revision 1.5  2006-05-28 16:15:27  ncq
# - populate already handled by plugin base class now
#
# Revision 1.4  2006/05/20 18:56:03  ncq
# - use receive_focus() interface
#
# Revision 1.3  2006/05/15 13:41:05  ncq
# - use patient change signal mixin
# - raise ourselves when patient has changed
#
# Revision 1.2  2006/05/15 11:07:26  ncq
# - cleanup
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#