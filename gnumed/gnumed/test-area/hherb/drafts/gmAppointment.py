__version__ = "$Revision: 1.1 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

from wxPython.wx import *
from wxPython.calendar import *
from wxPython.utils import *

import gettext
_ = gettext.gettext

import gmScheduleGrid

#----------------------------------------------------------------------

ID_CALENDAR = wxNewId()
ID_COMBO_STAFF = wxNewId()

class AppointmentPanel(wxPanel):
	def __init__(self, parent, ID):
		wxPanel.__init__(self, parent, ID)
		szrMain = wxBoxSizer( wxHORIZONTAL )
		szrLeft = wxBoxSizer( wxVERTICAL )
		szrRight = wxBoxSizer( wxVERTICAL )
		szrMain.AddSizer(szrLeft, 1, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 1 )
		szrMain.AddSizer(szrRight, 0, wxALIGN_TOP|wxLEFT|wxRIGHT, 1 )


		self.schedule = gmScheduleGrid.ScheduleGrid(self)
		szrLeft.AddWindow(self.schedule,1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )

		self.calendar  = wxCalendarCtrl(self, ID_CALENDAR, wxDateTime_Now(),
                             style = wxCAL_SHOW_HOLIDAYS | wxCAL_MONDAY_FIRST)
		szrRight.AddWindow(self.calendar, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
		EVT_CALENDAR(self, ID_CALENDAR, self.OnCalSelected)

		txt = wxStaticText( self, -1, _("Appointment with:"), wxDefaultPosition, wxDefaultSize, 0 )
		szrRight.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.cbStaffSelection = wxComboBox( self, ID_COMBO_STAFF, "", wxDefaultPosition, wxSize(70,-1),
		[_("Nurse"),_("Any doctor")] , wxCB_DROPDOWN )
		szrRight.AddWindow( self.cbStaffSelection, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )


		self.SetSizer(szrMain)
		self.SetAutoLayout(true)

		szrMain.Fit(self)
		szrMain.SetSizeHints(self)
		#self.Fit()


	def OnCalSelected(self, evt):
		print'OnCalSelected: %s\n' % evt.GetDate()


if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(AppointmentPanel, -1)
	app.MainLoop()
