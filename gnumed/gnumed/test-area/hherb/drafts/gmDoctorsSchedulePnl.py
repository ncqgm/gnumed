__version__ = "$Revision: 1.1 $"

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

doctorquery = "select title, givennames, surnames, id from v_doctors_only"
preferred_interval_query = "select duration from v_duration_standard where id_staff = %d"
doc_available_query = "select is_available(%d, %s)"    #id_doctor, date, time
days_off_query = "select day_of_week from days_off where id_staff = %d"

class DoctorsSchedulePnl(wxPanel):
	def __init__(self, parent, doctor = None):
		wxPanel.__init__(self, parent, -1)

		self.dbpool=gmPG.ConnectionPool()
		self.db = self.dbpool.GetConnection('appointments')
		cur = self.db.cursor()
		cur.execute(doctorquery);
		self.doctors=gmPG.dictResult(cur);
		#print self.doctors
		self.doctor=doctor
		self.doctorindex = {}
		#to look up a doctor's id depending on the index in the combo box
		#as combo box Set/Get client data seems buggy


		self.szrMain = wxBoxSizer(wxVERTICAL)
		self.szrTopRow = wxBoxSizer(wxHORIZONTAL)

		session_interval = 15

		self.schedule = gmScheduleGrid.ScheduleGrid(self, session_interval=session_interval)

		self.szrButtons = wxBoxSizer(wxHORIZONTAL)
		self.szrMain.AddSizer(self.szrTopRow, 0, wxGROW|wxALIGN_TOP|wxLEFT|wxRIGHT, 5 )
		self.szrMain.AddWindow(self.schedule, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 3 )
		self.szrMain.AddSizer(self.szrButtons, 0, wxALIGN_TOP|wxLEFT|wxRIGHT, 1 )

		txt = wxStaticText( self, -1, _("with:"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrTopRow.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.cbStaffSelection = wxComboBox( self, ID_COMBO_STAFF, "", wxDefaultPosition, wxSize(70,-1),
		[] , wxCB_DROPDOWN )
		EVT_COMBOBOX(self, ID_COMBO_STAFF, self.OnStaffSelected)
		self.szrTopRow.AddWindow( self.cbStaffSelection, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

		self.FillComboStaff(self.doctors)
		if self.doctor is not None:
			#print "Setting Doctor", self.doctor
			self.SetDoctor(self.doctor)
			#print "Blocking days for ", self.doctor
			self.BlockDays(self.doctor)

		self.SetSizer(self.szrMain)
		self.SetAutoLayout(true)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)
		self.schedule.GoToDateTime()


	def FillComboStaff(self, doctors):
		index=0
		for doc in doctors:
			docstr = "%s %s %s" % (doc['title'], doc['givennames'], doc['surnames'])
			id = doc['id']
			self.doctorindex[index] = id;
			self.cbStaffSelection.Append(docstr, id)
			self.cbStaffSelection.SetClientData(index, id)
			index+=1


	def SelectDoctor(self, doctor_id):
		self.doctor = doctor_id
		self.schedule.SetDoctor(self.doctor)
		cur = self.db.cursor()
		cur.execute(preferred_interval_query % doctor_id)
		try:
			(self.interval, )= cur.fetchone()
			if self.interval is None or self.interval < 5:
				self.interval=15
		except:
			self.interval=15
		#self.schedule.SetInterval(interval=self.interval)
		self.schedule.Recreate(interval = self.interval)
		self.BlockDays(doctor_id)


	def BlockDays(self, doctor_id):
		cur = self.db.cursor()
		cur.execute(days_off_query % doctor_id)
		days_off = cur.fetchall()
		for day in days_off:
			self.schedule.BlockDay(day[0])


	def SetDoctor(self, doctor_id):
		cbindex = -1
		for key in self.doctorindex.keys():
			if self.doctorindex[key] == doctor_id:
				cbindex = key
				break
		if cbindex > -1:
			self.cbStaffSelection.SetSelection(cbindex)
			self.SelectDoctor(doctor_id)



	def OnStaffSelected(self, evt):
		idx = evt.GetSelection()
		id = self.doctorindex[idx]
		if id is not None:
			#print "Selecting doctor", id
			self.SelectDoctor(id)



	def SetDate(self, date):
		self.date = date
		self.schedule.SetDate(date)
		#self.BlockDays(self.doctor)



if __name__ == '__main__':
	app = wxPyWidgetTester(size=(600,440))
	#show the login panel in a main window
	app.SetWidget(DoctorsSchedulePnl)
	app.MainLoop()
