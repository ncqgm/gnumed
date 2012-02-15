#======================================================================
# GNUmed billing plugin
#
# @copyright: authors
#======================================================================
__author__ = "Nico Latzer <nl@mnet-online.de>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging

import wx

from Gnumed.wxpython import gmPlugin
#from Gnumed.wxpython import gmBillItemWidgets
from Gnumed.wxpython import gmBillingWidgets

_log = logging.getLogger('gm.billing')

#======================================================================
class gmBillingPlugin(gmPlugin.cNotebookPlugin):

	tab_name = _('Billing')

	def name(self):
		return gmBillingPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmBillingWidgets.cBillingPluginPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		pass

	def can_receive_focus(self):
		if not self._verify_patient_avail():
			return None
		return 1

#======================================================================
if __name__ == '__main__':
    pass
