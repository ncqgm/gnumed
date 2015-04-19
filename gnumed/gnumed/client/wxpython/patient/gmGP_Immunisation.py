# -*- coding: utf-8 -*-
#======================================================================
# GNUmed immunisation/vaccination patient plugin
#
# this plugin holds the immunisation details
#
# @copyright: author
#======================================================================
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin_Patient, gmVaccWidgets

#======================================================================
class gmGP_Immunisation(gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the immunisation window."""

	__icons = {
"""icon_syringe""": 'x\xdam\xd0\xb1\n\x80 \x10\x06\xe0\xbd\xa7\xf8\xa1\xc1\xa6\x9f$\xe8\x01\x1a\
\x1a[Z\\#\x9a\x8a\xea\xfd\xa7N3\xf4\xb0C\x90\xff\xf3\x0e\xd4\xe6\xb8m5\x1b\
\xdbCV\x07k\xaae6\xc4\x8a\xe1X\xd6=$H\x9a\xaes\x0b\xc1I\xa8G\xa9\xb6\x8d\x87\
\xa9H\xa0@\xafe\xa7\xa8Bi\xa2\xdfs$\x19,G:\x175\xa1\x98W\x85\xc1\x9c\x1e\xcf\
Mc4\x85\x9f%\xfc\xae\x93!\xd5K_\xd4\x86\xf8\xa1?\x88\x12\xf9\x00 =F\x87'
}

	def name (self):
		return 'Immunisations Window'

	def MenuInfo (self):
		return ('view', '&Immunisation')

	def GetIconData(self, anIconID = None):
		if anIconID is None:
			return self.__icons[_("""icon_syringe""")]
		else:
			if anIconID in self.__icons:
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_syringe""")]

	def GetWidget (self, parent):
		return gmVaccWidgets.ImmunisationPanel (parent, -1)
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	print "there isn't really any unit test for this"
#	from wxPython.wx import *
#	app = wxPyWidgetTester(size = (600, 600))
#	app.SetWidget(gmVaccWidgets.ImmunisationPanel, -1)
#	app.MainLoop()
#======================================================================
