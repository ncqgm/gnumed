# -*- coding: utf-8 -*-
"""GNUmed allergies notebook plugin"""

#======================================================================
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging

import wx

from Gnumed.wxpython import gmPlugin

_log = logging.getLogger('gm.ui')

if __name__ == "__main__":
	_ = lambda x:x

#======================================================================
class gmAllergiesPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the allergies window."""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	tab_name = _('Allergies')

	def name (self):
		return gmAllergiesPlugin.tab_name

	def GetWidget (self, parent):
#		self._widget = gmAllergyWidgets.cAllergyPanel(parent, -1)
#		return self._widget
		return wx.Panel(parent, -1)

	def MenuInfo (self):
		return ('view', '&Allergies')

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.PyWidgetTester(size = (600, 600))
	#app.SetWidget(gmAllergyWidgets.cAllergyPanel, -1)
	app.MainLoop()
