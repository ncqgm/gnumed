__version__ = "$Revision: 1.4 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

import time

from wxPython.wx import *
from wxPython.calendar import *
from wxPython.utils import *

import gettext
_ = gettext.gettext

import gmDoctorsSchedulePnl

ID_BTN_CALENDAR = wxNewId()
ID_TEXTCTRL_WEEKSELECTION = wxNewId()

class ScheduleAllDoctorsPnl(wxPanel):
	def __init__(self, parent, doctors=["Dr. Herb", "Dr. Eburn"]):
		wxPanel.__init__(self, parent, -1)
		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrDateSelection = wxBoxSizer(wxHORIZONTAL)
		self.DateSelectionPanel(self, self.szrDateSelection)
		self.szrMain.AddSizer(self.szrDateSelection, 0, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT|wxTOP|wxBOTTOM, 15 )
		self.szrSchedules = wxBoxSizer(wxHORIZONTAL)
		self.schedules = []
		index=0
		for doctor in doctors:
			#pnl =
			self.schedules.append(gmDoctorsSchedulePnl.DoctorsSchedulePnl(self, doctor=None))
			self.szrSchedules.AddWindow(self.schedules[index], 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
			index+=1
		self.schedules[0].SetDoctor(1)
		self.schedules[1].SetDoctor(3)
		self.szrMain.AddSizer(self.szrSchedules, 1, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )

		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)
		self.SetDate()


	def OnCalendar(self):
		pass


	def DateSelectionPanel(self, parent, sizer):
		txt = wxStaticText( self, -1, _("Appointments for week:"), wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.tcWeekSelection = wxTextCtrl( parent, ID_TEXTCTRL_WEEKSELECTION, "", wxDefaultPosition, wxSize(80,-1), 0 )
		sizer.AddWindow(self.tcWeekSelection, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.btnCalendar = wxButton( self, ID_BTN_CALENDAR, "Calendar", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnCalendar, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_CALENDAR, self.OnCalendar)


	def SetDate(self, date=None):
		self.date = date
		if self.date==None:
			self.date= time.localtime()
		for i in range(len(self.schedules)):
			self.schedules[i].SetDate(self.date)




if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(ScheduleAllDoctorsPnl)
	app.MainLoop()


