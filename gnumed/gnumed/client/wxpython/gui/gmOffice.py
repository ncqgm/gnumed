"""
This is a window for the office functions of GNUMed.
Appointments, billing.

Status: blank screen

"""

# make this into GNUMed plugin

from Gnumed.pycommon import gmI18N
from Gnumed.wxpython import gmPlugin

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

class gmOffice (gmPlugin.cNotebookPluginOld):

	tab_name = _("Office")

	def name (self):
		return gmOffice.tab_name

	def MenuInfo (self):
		return ("view", _("&Office"))

	def GetWidget (self, parent):
		return wx.wx.Panel(parent, -1)
