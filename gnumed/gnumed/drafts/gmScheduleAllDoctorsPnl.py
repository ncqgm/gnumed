__version__ = "$Revision: 1.7 $"

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
ID_BTN_TODAY = wxNewId()
ID_BTN_NEXTWEEK = wxNewId()
ID_BTN_NEXTFORTNIGHT = wxNewId()
ID_BTN_NEXTMONTH = wxNewId()
ID_TEXTCTRL_WEEKSELECTION = wxNewId()

class ScheduleAllDoctorsPnl(wxPanel):
	def __init__(self, parent, doctors=2):
		wxPanel.__init__(self, parent, -1)
		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrDateSelection = wxBoxSizer(wxHORIZONTAL)
		self.DateSelectionPanel(self, self.szrDateSelection)
		self.szrMain.AddSizer(self.szrDateSelection, 0, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT|wxTOP|wxBOTTOM, 15 )
		self.szrSchedules = wxBoxSizer(wxHORIZONTAL)
		self.schedules = []
		for index in range(doctors):
			#pnl =
			self.schedules.append(gmDoctorsSchedulePnl.DoctorsSchedulePnl(self, doctor=None))
			self.szrSchedules.AddWindow(self.schedules[index], 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
			self.schedules[index].SetDoctor(index+1)  #database ids start with 1 not 0
			index+=1
		self.szrMain.AddSizer(self.szrSchedules, 1, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )

		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)
		self.SetDate()
		self.schedules[0].schedule.SetFocus()
		self.schedules[0].schedule.GoToDateTime()



	def DateSelectionPanel(self, parent, sizer):
		txt = wxStaticText( self, -1, _("Appointments for :"), wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.tcDateSelection = wxTextCtrl( parent, ID_TEXTCTRL_WEEKSELECTION, "", wxDefaultPosition, wxSize(80,-1), 0 )
		sizer.AddWindow(self.tcDateSelection, 0, wxALIGN_CENTER_VERTICAL, 5 )
		#display appointments starting from today
		self.btnToday = wxButton( self, ID_BTN_TODAY, "today", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnToday, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_TODAY, self.OnBtnToday)
		#make appoinment next week
		self.btnNextWeek = wxButton( self, ID_BTN_NEXTWEEK, "next week", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnNextWeek, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_NEXTWEEK, self.OnBtnNextWeek)
		#make appoinment in a fortnight's time
		self.btnNextFortnight = wxButton( self, ID_BTN_NEXTFORTNIGHT, "in a fortnight", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnNextFortnight, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_NEXTFORTNIGHT, self.OnBtnNextFortnight)
		#make appoinment in a month's time
		self.btnNextMonth = wxButton( self, ID_BTN_NEXTMONTH, "in one month", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnNextMonth, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_NEXTMONTH, self.OnBtnNextMonth)
		#popup calendar
		self.btnCalendar = wxButton( self, ID_BTN_CALENDAR, "Calendar", wxDefaultPosition, wxDefaultSize, 0 )
		sizer.AddWindow( self.btnCalendar, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, ID_BTN_CALENDAR, self.OnCalendar)


		
	def AddDays(self, days, date=None):
		if date==None:
			date=self.date
		start = time.mktime(date)
		return(time.localtime(start+86400*days))

	def OnBtnToday(self, evt):
		self.SetDate(time.localtime())


	def OnBtnNextWeek(self, evt):
		self.date = self.AddDays(7)
		self.SetDate(self.date)

	def OnBtnNextFortnight(self, evt):
		self.date = self.AddDays(14)
		self.SetDate(self.date)

	def OnBtnNextMonth(self, evt):
		self.date = self.AddDays(30)
		self.SetDate(self.date)

	def OnCalendar(self, evt):
		pass

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


