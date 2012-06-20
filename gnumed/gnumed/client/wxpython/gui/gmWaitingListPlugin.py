#=====================================================
# GNUmed waiting list
#=====================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmWaitingListWidgets

#======================================================================
class gmWaitingListPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the waiting list."""

	tab_name = _('Waiting list')
	#--------------------------------------------------------
	def __init__(self):
		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmWaitingListPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmWaitingListWidgets.cWaitingListPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('office', _('&Waiting list'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
