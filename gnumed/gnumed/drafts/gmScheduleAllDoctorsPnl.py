__version__ = "$Revision: 1.2 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

from wxPython.wx import *
from wxPython.calendar import *
from wxPython.utils import *

import gettext
_ = gettext.gettext

import gmDoctorsSchedulePnl

class ScheduleAllDoctorsPnl(wxPanel):
	def __init__(self, parent, doctors=["Dr. Herb", "Dr. Eburn"]):
		wxPanel.__init__(self, parent, -1)
		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrSchedules = wxBoxSizer(wxHORIZONTAL)
		self.schedules = []
		index=0
		for doctor in doctors:
			#pnl =
			self.schedules.append(gmDoctorsSchedulePnl.DoctorsSchedulePnl(self, doctor))
			self.szrSchedules.AddWindow(self.schedules[index], 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
			index+=1
		self.szrMain.AddSizer(self.szrSchedules, 1, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )

		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)


if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(ScheduleAllDoctorsPnl)
	app.MainLoop()


