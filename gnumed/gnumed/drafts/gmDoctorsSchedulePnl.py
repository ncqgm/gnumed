__version__ = "$Revision: 1.3 $"

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

doctorquery = "select title, firstname, surname, id_staff from v_doctors_only"
preferred_interval_query = "select duration from v_duration_standard where id_staff = %d"
doc_available_query = "select is_available(%d, %s)"    #id_doctor, date, time

class DoctorsSchedulePnl(wxPanel):
	def __init__(self, parent, doctor = None):
		wxPanel.__init__(self, parent, -1)

		self.dbpool=gmPG.ConnectionPool()
		self.db = self.dbpool.GetConnection('appointments')
		cur = self.db.cursor()
		cur.execute(doctorquery);
		self.doctors=gmPG.dictresult(cur);

		self.doctor_labels = []
		for doc in self.doctors:
			label = "%s %s %s (%d)" % (doc['title'], doc['givennames'], doc['surnames'], doc['id_staff'])
			self.doctor_labels.append(label)

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
		self.doctor_labels , wxCB_DROPDOWN )
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
