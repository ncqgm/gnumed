#======================================================================
# GnuMed immunisation/vaccination patient plugin
# ----------------------------------------------
#
# this plugin holds the immunisation details
#
# @copyright: author
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmVaccinationsPlugin.py,v $
# $Id: gmVaccinationsPlugin.py,v 1.6 2005-09-28 21:27:30 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

# panel class holding editing prompts and text boxes
from Gnumed.wxpython import gmPlugin, gmVaccWidgets
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

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
# $Log: gmVaccinationsPlugin.py,v $
# Revision 1.6  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.5  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.4  2004/09/18 13:56:34  ncq
# - translate tab label
#
# Revision 1.3  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.2  2004/07/15 23:27:04  ncq
# - typo fix
#
# Revision 1.1  2004/07/15 23:16:21  ncq
# - refactor vaccinations GUI code into
#   - gmVaccWidgets.py: layout manager independant widgets
#   - gui/gmVaccinationsPlugins.py: Horst space notebook plugin
#   - patient/gmPG_Immunisation.py: erstwhile Richard space patient plugin
#
