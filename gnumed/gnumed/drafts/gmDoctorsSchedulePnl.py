__version__ = "$Revision: 1.2 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

from wxPython.wx import *
from wxPython.calendar import *
from wxPython.utils import *

import gettext
_ = gettext.gettext

import gmPG
import gmScheduleGrid

ID_COMBO_STAFF = wxNewId()

class DoctorsSchedulePnl(wxPanel):
	def __init__(self, parent, doctor = None):
		wxPanel.__init__(self, parent, -1)

		self.dbpool=gmPG.ConnectionPool()
		self.db = self.dbpool.GetConnection('personalia')
		self.doctor=doctor

		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrTopRow = wxBoxSizer(wxHORIZONTAL)
		session_interval = 15
		if doctor == "Dr. Eburn":
			session_interval = 20
		self.schedule = gmScheduleGrid.ScheduleGrid(self, session_interval=session_interval)
		self.szrButtons = wxBoxSizer(wxHORIZONTAL)
		self.szrMain.AddSizer(self.szrTopRow, 0, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )
		self.szrMain.AddWindow(self.schedule, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
		self.szrMain.AddSizer(self.szrButtons, 0, wxALIGN_TOP|wxLEFT|wxRIGHT, 1 )

		txt = wxStaticText( self, -1, _("App. with:"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrTopRow.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.cbStaffSelection = wxComboBox( self, ID_COMBO_STAFF, "", wxDefaultPosition, wxSize(70,-1),
		["Dr. Herb","Dr. Eburn", "Dr. Kamerman", "Dr. Leneham", "Dr. Wearne", "Locum"] , wxCB_DROPDOWN )
		self.szrTopRow.AddWindow( self.cbStaffSelection, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

		if self.doctor is not None:
			self.cbStaffSelection.SetSelection(self.cbStaffSelection.FindString(doctor))
		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)

if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(DoctorsSchedulePnl)
	app.MainLoop()
