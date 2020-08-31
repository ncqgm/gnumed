# -*- coding: utf-8 -*-

"""GNUmed data mining plugin aka SimpleReports"""
#=====================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmDataMiningWidgets

if __name__ == '__main__':
	_ = lambda x:x
#======================================================================
class gmDataMiningPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate a simple data mining window."""

	tab_name = _('Reports')
	#--------------------------------------------------------
	def __init__(self):
		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmDataMiningPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmDataMiningWidgets.cDataMiningPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('tools', _('&Report Generator'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
