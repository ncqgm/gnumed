"""
This is a window for the office functions of GNUMed.
Appointments, billing.

Status: blank screen

"""


# make this into GNUMed plugin

import gmPlugin
from wxPython.wx import *

class gmOffice (gmPlugin.wxNotebookPlugin):

	def name (self):
		return "Office"

	def MenuInfo (self):
		return ("view", "&Office")

	def GetWidget (self, parent):
		return wxPanel (parent, -1)
