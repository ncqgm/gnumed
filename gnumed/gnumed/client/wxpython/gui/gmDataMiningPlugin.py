#=====================================================
# GNUmed data mining plugin aka SimpleReports
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmDataMiningPlugin.py,v $
# $Id: gmDataMiningPlugin.py,v 1.1 2007-04-06 23:09:13 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import wx

from Gnumed.wxpython import gmPlugin, gmPatSearchWidgets

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
		self._widget = gmPatSearchWidgets.cDataMiningPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('tools', _('Report Generator'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
#======================================================================
# $Log: gmDataMiningPlugin.py,v $
# Revision 1.1  2007-04-06 23:09:13  ncq
# - this is new
#
#