__version__ = "$Revision: 1.1 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

import time

from wxPython.wx import *
#from wxPython.calendar import *
#from wxPython.utils import *

import gettext
_ = gettext.gettext

import gmDoctorsSchedulePnl, gmCalendarDlg

ID_BTN_CALENDAR = wxNewId()
ID_BTN_TODAY = wxNewId()
ID_BTN_NEXTWEEK = wxNewId()
ID_BTN_NEXTFORTNIGHT = wxNewId()
ID_BTN_NEXTMONTH = wxNewId()
ID_TEXTCTRL_WEEKSELECTION = wxNewId()
ID_CHOICE_NUMSCHEDULES = wxNewId()

class ScheduleAllDoctorsPnl(wxPanel):
	def __init__(self, parent, doctors=1):
		wxPanel.__init__(self, parent, -1)
		self.parent = parent
		self.date = time.localtime()
		self.schedules = []
		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrDateSelection = wxBoxSizer(wxHORIZONTAL)
		self.DateSelectionPanel(self, self.szrDateSelection)
		self.szrMain.AddSizer(self.szrDateSelection, 0, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT|wxTOP|wxBOTTOM, 15 )
		self.szrSchedules = wxBoxSizer(wxHORIZONTAL)
		self.szrMain.AddSizer(self.szrSchedules, 1, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )
		self.InitSchedules(doctors)
		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)
		self.schedules[0].schedule.SetFocus()
		self.schedules[0].schedule.GoToDateTime()


	def InitSchedules(self, number_of_doctors=1):
		"""Add one schedule widget for each number_of_doctors to the window"""
		for schedule in self.schedules:
			self.szrSchedules.RemoveWindow(schedule)
		self.schedules = []
		for index in range(number_of_doctors):
			#pnl =
			self.schedules.append(gmDoctorsSchedulePnl.DoctorsSchedulePnl(self, doctor=None))
			self.szrSchedules.AddWindow(self.schedules[index], 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
			self.schedules[index].SetDoctor(index+1)  #database ids start with 1 not 0
			index+=1
		self.szrSchedules.Layout()
		self.szrMain.Layout()



	def DateSelectionPanel(self, parent, sizer):
		"""Add a number of date selection widgets to the schedule main window"""
		txt = wxStaticText( self, -1, _("Display :"), wxDefaultPosition, wxDefaultSize, 5 )
		sizer.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.chNumSchedules = wxChoice( parent, ID_CHOICE_NUMSCHEDULES, wxDefaultPosition, wxSize(40, -1), ['1','2','3','4', '5', '6'], wxNO_BORDER)
		EVT_CHOICE(self, ID_CHOICE_NUMSCHEDULES, self.OnNumSchedules)
		sizer.AddWindow(self.chNumSchedules, 0, wxALIGN_CENTER_VERTICAL, 0 )
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
		"""Add 'days' to date. If date is None, 'days' are added to the current date.
		Returns a date tuple"""
		if date==None:
			date=self.date
		start = time.mktime(date)
		return(time.localtime(start+86400*days))

	def OnNumSchedules(self, evt):
		n = int(self.chNumSchedules.GetSelection())+1
		print "On NumSchedules", n
		if n>0:
			self.InitSchedules(n)

	def OnBtnToday(self, evt):
		"""Sets the start date in the schedule to today"""
		self.SetDate(time.localtime())


	def OnBtnNextWeek(self, evt):
		"""Advances the start date in the schedule by one week"""
		self.date = self.AddDays(7)
		self.SetDate(self.date)

	def OnBtnNextFortnight(self, evt):
		"""Advances the start date in the schedule by a fortnight"""
		self.date = self.AddDays(14)
		self.SetDate(self.date)

	def OnBtnNextMonth(self, evt):
		"""Advances the start date in the schedule by one month"""
		self.date = self.AddDays(30)
		self.SetDate(self.date)

	def OnCalendar(self, evt):
		"""Displays a calendar from which the user can select the schedule start date"""
		d=gmCalendarDlg.PopupCalendar(self, -1, "Select a date:")
		retval = d.ShowModal() # Shows it
		if retval == 1:
			date = d.GetSelection()
			self.SetDate(time.strptime(date, "%Y-%m-%d"))
		d.Destroy() # finally destroy it when finished.


	def SetDate(self, date=None):
		"""Set the schedule widget's's start date (as displayed in first column)"""
		self.date = date
		if self.date==None:
			self.date= time.localtime()
		for schedule in self.schedules:
			schedule.SetDate(self.date)




if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(ScheduleAllDoctorsPnl)
	app.MainLoop()


