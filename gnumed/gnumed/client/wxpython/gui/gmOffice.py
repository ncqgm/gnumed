"""
This is a window for the office functions of GNUMed.
Appointments, billing.

Status: blank screen

"""

# make this into GNUMed plugin

from Gnumed.wxpython import gmPlugin
from wxPython.wx import *

class gmOffice (gmPlugin.wxNotebookPlugin):

    tab_name = _("Office")

    def name (self):
        return gmOffice.tab_name

    def MenuInfo (self):
        return ("view", _("&Office"))

    def GetWidget (self, parent):
        return wxPanel (parent, -1)
