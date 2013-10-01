# -*- coding: utf-8 -*-
#======================================================================
# GNUmed immunisation/vaccination patient plugin
# ----------------------------------------------
#
# this plugin holds the immunisation details
#
# @copyright: author
#======================================================================
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import wx

# panel class holding editing prompts and text boxes
from Gnumed.wxpython import gmPlugin, gmVaccWidgets

_log = gmLog.gmDefLog

#======================================================================
class gmVaccinationsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the immunisation window."""

	__icons = {
"""icon_syringe""": 'x\xdam\xd0\xb1\n\x80 \x10\x06\xe0\xbd\xa7\xf8\xa1\xc1\xa6\x9f$\xe8\x01\x1a\
\x1a[Z\\#\x9a\x8a\xea\xfd\xa7N3\xf4\xb0C\x90\xff\xf3\x0e\xd4\xe6\xb8m5\x1b\
\xdbCV\x07k\xaae6\xc4\x8a\xe1X\xd6=$H\x9a\xaes\x0b\xc1I\xa8G\xa9\xb6\x8d\x87\
\xa9H\xa0@\xafe\xa7\xa8Bi\xa2\xdfs$\x19,G:\x175\xa1\x98W\x85\xc1\x9c\x1e\xcf\
Mc4\x85\x9f%\xfc\xae\x93!\xd5K_\xd4\x86\xf8\xa1?\x88\x12\xf9\x00 =F\x87'
}

	tab_name = _('Vaccinations')

	def name (self):
		return gmVaccinationsPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmVaccWidgets.cImmunisationsPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('view', _('&Vaccinations'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(gmVaccWidgets.cImmunisationsPanel, -1)
	app.MainLoop()
#======================================================================
