#!/bin/env python
#This software is free software by the terms of the GPL license

"""This module provides a calendar window for date selection"""


__version__ = "$Revision: 1.1 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__


import time

from wxPython.wx import *
from wxPython.calendar import *

# text translation function for localization purposes
import gettext
_ = gettext.gettext

ID_CALENDAR = wxNewId()
ID_CALENDAR_SELECTED = wxNewId()

class PopupCalendar(wxDialog):
	"""pops up a month display calendar. Parameter 'date' can override the default
	which is the current date. Returns 1 if a date was selected, != 1 else.
	With GetSelection() the selected date can be requested, it is returned in ISO format"""

	def __init__(self, parent, id, title, pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxDEFAULT_DIALOG_STYLE|wxRESIZE_BORDER, date=None ):
		wxDialog.__init__(self, parent, id, title, pos, size, style)
		self.date = date
		if self.date == None:
			self.date = wxDateTime_Now()
		self.date_selected = None
		self.calendar = wxCalendarCtrl(self, ID_CALENDAR, self.date, pos = (5,50),
			style = wxCAL_SHOW_HOLIDAYS|wxCAL_MONDAY_FIRST)
		self.Fit()

		EVT_CALENDAR(self, ID_CALENDAR, self.OnCalSelected)


	def OnCalSelected(self, evt):
		date = evt.GetDate()
		self.date_selected = date.FormatISODate()
		#self.date_selected = time.strptime(date, "%a %d %b %Y %H:%M:%S %Z")
		#print self.date_selected
		self.EndModal(1)

	def GetSelection(self):
		return self.date_selected



if __name__ == "__main__":

	ID_TEST = wxNewId()
	ID_EXIT = wxNewId()
	class testapp (wxApp):

		def OnInit (self):
			frame = wxFrame(None,-4, "Testing...", size=wxSize (600, 400),
					style=wxDEFAULT_FRAME_STYLE|
					wxNO_FULL_REPAINT_ON_RESIZE)
			filemenu= wxMenu()
			filemenu.Append(ID_TEST, "&Test","Testing this module")
			filemenu.AppendSeparator()
			filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
			# Creating the menubar.
			menuBar = wxMenuBar()
			menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
			frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
			txt = wxStaticText( frame, -1, _("Select 'test' from the 'File' menu"), wxDefaultPosition, wxDefaultSize, 0 )
			EVT_MENU(frame, ID_TEST, self.OnTest)
			EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)
			frame.Show(1)
			return 1


		def OnTest(self,e):
			d=PopupCalendar(None, -1, "Select a date:")
			retval = d.ShowModal() # Shows it
			if retval == 1:
				print d.GetSelection()
			else:
				print "user has cancelled"
			d.Destroy() # finally destroy it when finished.

		def OnCloseWindow (self, e):
			self.ExitMainLoop ()


	app = testapp (0)
	app.MainLoop ()


