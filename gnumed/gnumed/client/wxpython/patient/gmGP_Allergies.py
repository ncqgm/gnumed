# -*- coding: utf-8 -*-
#============================================================================
# gmGP_Allergies
#
# @dependencies: wxPython (>= version 2.3.1)
#============================================================================
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'


from Gnumed.wxpython import gmPlugin_Patient, gmAllergyWidgets

#============================================================================
class gmGP_Allergies (gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the allergies window"""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	def name (self):
		return 'Allergies'

	def MenuInfo (self):
		return ('view', '&Allergies')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_letter_A""")]
		else:
			if anIconID in self.__icons:
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_letter_A""")]

	def GetWidget (self, parent):
		pass
#		return gmAllergyWidgets.cAllergyPanel (parent, -1)

#============================================================================
if __name__ == "__main__":
	print "no unit test available"
#	from wxPython.wx import *
#	app = wxPyWidgetTester(size = (600, 600))
#	app.SetWidget(AllergyPanel, -1)
#	app.MainLoop()
#============================================================================
