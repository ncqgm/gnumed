__version__ = "$Revision: 1.6 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

import string
import time

from wxPython.wx import *
from wxPython.grid import *
#from wxPython.lib.mixins.grid import wxGridAutoEditMixin
from wxPython.lib import colourdb

import gettext
_ = gettext.gettext

import gmPG

ID_LISTBOX_SELECTION = wxNewId()

#--------------------------------------------------------------------------

days_of_week = (_("Monday"),
                _("Tuesday"),
		_("Wednesday"),
		_("Thursday"),
		_("Friday"),
		_("Saturday"),
		_("Sunday"))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pat_by_names_query = \
	"select id, lastnames, firstnames, dob from v_basic_person where lastnames ILIKE '%s%%' and firstnames ILIKE '%s%%'"
pat_by_surnames_query = \
	"select id, lastnames, firstnames, dob from v_basic_person where lastnames ILIKE '%s%%'"

def ParseTimeInterval(interval):
	res = []
	s = string.split(interval, "-")
	if len(s) != 2:
		return None
	for str in s:
		h,m = string.split(str, ":")
		res.append((int(h), int(m)))
	return res

def GenerateExcludedTimes(excluded, interval=15):
	"""returns a list of time strings in the format 'hh:mm'
	'exclude' is a list of time interval strings in the format
	'hh:mm-hh:mm' separarted by single white spaces between
	time interval strings. Interval is the time interval in
	minutes between two generated intervals"""

	if excluded is None:
		return []

	excl = []
	exlist = string.split(excluded, " ")
	for ex in exlist:
		ti = ParseTimeInterval(ex)
		if ti is None:
			continue
		from_h, from_m = ti[0]
		to_h, to_m = ti[1]
		str = "%02d:%02d" % (from_h, from_m)
		excl.append(str)
		finished = 0
		while not finished:
			from_m += interval
			if from_m>=60:
				from_m=0
				from_h+=1
			if from_h > to_h:
				break
			if from_h == to_h and from_m >= to_m:
				break
			str = "%02d:%02d" % (from_h, from_m)
			excl.append(str)
	return excl


def TimeLabels(start=9, end=18, interval=15, exclude=None):
	"""Return a list of formatted time strings beginning at
	 'start' hours, incremented by 'interval' minutes until
	 'end' hours are reached (but not included)
	 exclude is a list of time intervals separated by a single whitespace
	 in the format of 'hh:mm-hh:mm'"""

	if exclude is not None:
		excludelist = GenerateExcludedTimes(exclude, interval)
	else:
		excludelist = []
	print excludelist
	labels = []
	print start, end
	for hour in range(start, end):
		for minute in range(0,60, interval):
			str="%02d:%02d" % (hour, minute)
			if str not in excludelist:
				labels.append(str)
	return labels

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def DayOfWeekLabels(date=None, days=7):
	"""Return a list of day names starting with Monday,
	optionally including Sunday if 'include_sunday' is not 0"""

	if date is None:
		date = time.localtime()
	dow = DayOfWeek(date)
	one_day = 86400 #seconds
	start_day = time.mktime(date)
	labels = []
	index = dow
	for day in range(days):
		lbl = "%s\n%s" % (days_of_week[index], 
			time.strftime("%d/%m/%y", time.localtime(start_day)) )
		labels.append(lbl)
		index+=1
		start_day+=one_day
		if index>6:
			index=0
	return labels

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def DayOfWeek(date=None):
	if date is None:
		#Make Monday first day of the week:
		current_day = int(time.strftime('%w') )-1
	else:
		current_day = int(time.strftime('%w', date ) )-1
	if current_day == -1:
		current_day=6
	return current_day



class ScheduleGrid(wxGrid): ##, wxGridAutoEditMixin):
	def __init__(self, parent, doctor_id=None, hour_start=9, hour_end=18, session_interval=15, exclude=None, date=None, days=7, log=sys.stdout):
		wxGrid.__init__(self, parent, -1, style=wxWANTS_CHARS | wxSIMPLE_BORDER)
		##wxGridAutoEditMixin.__init__(self)
		pool = gmPG.ConnectionPool()
		self.db = pool.GetConnection('personalia')
		self.doctor_id = doctor_id
		self.log = log
		self.days=days
		self.hour_start = hour_start
		self.hour_end = hour_end
		self.session_interval = session_interval
		self.exclude = exclude
		self.moveTo = None
		if date is None:
			self.Date = time.localtime()
		else:
			self.Date = date

		self.clr_appointed = wxColour(240,220,140)
		self.clr_not_available = wxLIGHT_GREY
		self.clr_today = wxColour(255,255,125)
		self.clr_selected_day = wxColour(190,225,255)

		self.MakeGrid()

		#EVT_IDLE(self, self.OnIdle)


		# test all the events
  		EVT_CHAR(self.GetGridWindow(), self.OnChar)
		#EVT_GRID_CELL_LEFT_CLICK(self, self.OnCellLeftClick)
		EVT_GRID_CELL_RIGHT_CLICK(self, self.OnCellRightClick)
		#EVT_GRID_CELL_LEFT_DCLICK(self, self.OnCellLeftDClick)
		#EVT_GRID_CELL_RIGHT_DCLICK(self, self.OnCellRightDClick)

		#EVT_GRID_LABEL_LEFT_CLICK(self, self.OnLabelLeftClick)
		#EVT_GRID_LABEL_RIGHT_CLICK(self, self.OnLabelRightClick)
		#EVT_GRID_LABEL_LEFT_DCLICK(self, self.OnLabelLeftDClick)
		#EVT_GRID_LABEL_RIGHT_DCLICK(self, self.OnLabelRightDClick)
		#EVT_GRID_ROW_SIZE(self, self.OnRowSize)
		#EVT_GRID_COL_SIZE(self, self.OnColSize)

		#EVT_GRID_RANGE_SELECT(self, self.OnRangeSelect)
		EVT_GRID_CELL_CHANGE(self, self.OnCellChange)
		#EVT_GRID_SELECT_CELL(self, self.OnSelectCell)

		#EVT_GRID_EDITOR_SHOWN(self, self.OnEditorShown)
		#EVT_GRID_EDITOR_HIDDEN(self, self.OnEditorHidden)
		#EVT_GRID_EDITOR_CREATED(self, self.OnEditorCreated)

		EVT_KEY_DOWN(self,self.OnKeyDown)

	def OnKeyDown(self,evt):
		code = evt.KeyCode()
		if code == WXK_TAB:
			print "tab!"

		elif code == WXK_RETURN:
			evt.Skip()
		else:
			evt.Skip()


	def OnChar(self, evt):
		print "OnCHar"
		evt.Skip()

	def SetDoctor(self, id):
		self.doctor_id = id

	def MakeGrid(self):
		self.weekdaylabels = DayOfWeekLabels(self.Date, self.days)
		self.timelabels = TimeLabels(self.hour_start, self.hour_end, self.session_interval, self.exclude)
		self.CreateGrid(len(self.timelabels), len(self.weekdaylabels))

		#label the rows with default values
		self.SetInterval()
		#label the columns with default values
		self.SetDate(self.Date)


	def Recreate(self):
		print "called recreate"
		self.SetDate(self.Date)


	def SetInterval(self, start=None, end=None, interval=None, exclude=None):
		if start is not None: self.hour_start = start
		if end is not None: self.hour_end = end
		if interval is not None: self.session_interval = interval
		if exclude is not None: self.exclude=exclude

		#label the rows
		self.timelabels = TimeLabels(start=self.hour_start, end=self.hour_end, 
			interval=self.session_interval, exclude=self.exclude)
		index=0
		for index in range(len(self.timelabels)):
			self.SetRowLabelValue(index, self.timelabels[index])


	def SetColumnColours(self):
		#mark today in special colours
		today_attr = wxGridCellAttr()
		today_attr.SetBackgroundColour(self.clr_today)
		now = time.time()
		start = time.mktime(self.Date)
		delta = (now-start)/86400
		is_current=0
		if delta > 0 and delta < self.days:
			#we are displaying the current week,
			#so today must be the first day displayed
			self.SetColAttr(0, today_attr)
			is_current=1




	def BlockDate(self, blocked_date):
		start = time.mktime(self.Date)
		blocked = time.mktime(blocked_date)
		delta = (blocked-start)/86400
		if delta>0 and delta <self.days:
			attr = wxGridCellAttr()
			attr.SetBackgroundColour(wxLIGHT_GREY)
			self.SetColAttr(delta, attr)



	def BlockDay(self, weekday):
		start = DayOfWeek(self.Date)
		dow = start
		for index in range(self.days):
			if dow>6:
				dow=0
			if weekday == dow:
				date = time.localtime(time.mktime(self.Date)+index*86400)
				self.BlockDate(date)
			dow+=1


	def SetDate(self, date):
		self.Date=date
		#set the columns
		self.DeleteCols(0, self.GetNumberCols())
		self.AppendCols(self.days)
		self.weekdaylabels = DayOfWeekLabels(self.Date, self.days)
		index=0
		for index in range(len(self.weekdaylabels)):
			self.SetColLabelValue(index, self.weekdaylabels[index])
		#set the rows
		self.DeleteRows(0, self.GetNumberRows())
		self.AppendRows(len(self.timelabels))
		#label the rows with default values
		self.SetInterval()
		#label the columns with default values
		self.SetColumnColours()
		#dow = DayOfWeek(self.Date)
		#scroll if neccessary so that the selected dat is visible
		#self.MakeCellVisible(dow, 1)

	def AddDays(self, days, date=None):
		if date==None:
			date=self.Date
		start = time.mktime(date)
		return(time.localtime(start+86400*days))


	def GetCellDate(self, column):
		date = self.Date
		#delete hours, minutes, seconds - we only want the date, not the time
		return self.AddDays(column, date)


	def GetCellTime(self, row):
		return self.GetRowLabelValue(row)
		#parse time string in label (format hh:mm)
		#hm = string.split(tstr, ":")
		#return time in seconds
		#return (int(hm[0])*360) + (int(hm[1])*60)


	def GetCellDateTime(self, row, column):
		datestr = time.strftime("%Y-%m-%d", self.GetCellDate(column))
		timestr = self.GetCellTime(row)
		tds = "%s %s" % (datestr, timestr)
		print "tds", tds
		return time.strptime(tds, "%Y-%m-%d %H:%M")


	def AppointmentSelected(self, row, col):
		datetime=self.GetCellDateTime(row, col)
		value = self.GetCellValue(row, col)
		dts = time.strftime("%Y-%m-%d %H:%M", datetime)
		print "Appointment on %s for %s" % (dts, value)

	def OnCellLeftClick(self, evt):
		self.AppointmentSelected(evt.GetRow(), evt.GetCol())
		evt.Skip()

	def OnPatientArrived(self, evt):
		print "Patient has arrived"

	def OnPatientSeen(self, evt):
		print "Patient has been seen"

	def OnBillPatient(self, evt):
		print "Patient has been billed"

	def OnBulkBillPatient(self, evt):
		print "Thou shalt not bulk bill"

	def OnAddPatient(self, evt):
		print "Add patient"

	def OnCellRightClick(self, evt):
		row = evt.GetRow()
		col = evt.GetCol()
		self.SetGridCursor(row,col)
		value = self.GetCellValue(row, col)
		crect = self.CellToRect(row, col)

		#create a popup menu
		menu = wxMenu()
		menu.Append(0, _("Arrived"))
		menu.Append(1, _("Seen"))
		menu.Append(2, _("Bill"))
		menu.Append(3, _("Bulk bill"))
		menu.Append(4, _("Add Patient"))

		#connect the events to event handler functions
		EVT_MENU(self, 0, self.OnPatientArrived)
		EVT_MENU(self, 1, self.OnPatientSeen)
		EVT_MENU(self, 2, self.OnBillPatient)
		EVT_MENU(self, 2, self.OnBulkBillPatient)
		EVT_MENU(self, 2, self.OnAddPatient)

		#show the menu
		self.PopupMenu(menu, wxPoint(crect.x, crect.y))

		#free resources
		menu.Destroy()

		#anybody else needs to intercept right click events?
		evt.Skip()

	def OnCellLeftDClick(self, evt):
		self.log.write("OnCellLeftDClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnCellRightDClick(self, evt):
		self.log.write("OnCellRightDClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelLeftClick(self, evt):
		self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelRightClick(self, evt):
		self.log.write("OnLabelRightClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelLeftDClick(self, evt):
		self.log.write("OnLabelLeftDClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelRightDClick(self, evt):
		self.log.write("OnLabelRightDClick: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()


	def OnRowSize(self, evt):
		self.log.write("OnRowSize: row %d, %s\n" %
			(evt.GetRowOrCol(), evt.GetPosition()))
		evt.Skip()

	def OnColSize(self, evt):
		self.log.write("OnColSize: col %d, %s\n" %
			(evt.GetRowOrCol(), evt.GetPosition()))
		evt.Skip()

	def OnRangeSelect(self, evt):
		if evt.Selecting():
			self.log.write("OnRangeSelect: top-left %s, bottom-right %s\n" %
				(evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))
		evt.Skip()


	def ParseAppEntry(self, value):
		"""parses the contents of a cell: see function AppointmentMade()
		for an explanation of the parsing results"""

		firstname=None; surname=None; increment=0
		sl = string.split(value, " ")
		try:
			surname=sl[0]
			if surname[0]=='+' and len(surname)>1:
				surname=surname[1:]
			increment = string.count(sl[1], '+')
			if increment < 1:
				firstname=sl[1]
			increment=string.count(sl[2], '+')

		except:
			pass
        	return surname, firstname, increment


	def NewPatient(self, surname, firstname):
		return None


	def ChoosePatient(self, patient_dict):
		crect = self.CellToRect(self.GetGridCursorRow(), self.GetGridCursorCol())
		self.li = wxListBox( self, ID_LISTBOX_SELECTION, wxPoint(crect.x, crect.y+crect.height), wxSize(200,120),
        		[] , wxLB_SINGLE )
		for p in patient_dict:
			self.li.Append("%s, %s" % (p["lastnames"], p["firstnames"]), p["id"])
		self.li.SetFocus()
		EVT_LISTBOX(self, ID_LISTBOX_SELECTION, self.OnItemSelected)


	def OnItemSelected(self, evt):
		print "Item was selected", self.li.GetClientData(self.li.GetSelection())
		self.SetCellValue(self.GetGridCursorRow(), self.GetGridCursorCol(), self.li.GetString(self.li.GetSelection()))
		self.li.Destroy()


	def GetPatientByName(self, surname, firstname=None):
		cur = self.db.cursor()
		if firstname is not None:
			qstr = pat_by_names_query % (surname, firstname)
			print qstr
			cur.execute(qstr)
		else:
			qstr = pat_by_surnames_query % surname
			print qstr
			cur.execute(qstr)
		result = gmPG.dictResult(cur)
		n = len(result)
		if n == 0:
			return self.NewPatient(surname, firstname)
		elif n == 1:
			pat = result[0]
			return pat["id"], pat["firstname"], pat["surname"]
		else:
			return self.ChoosePatient(result)



	def AppointmentMade(self, row, col, value):
		"""This function parses the contents of a grid cell. It expects
		at least one character sequence which is interpreted as part of a surname.
		If enother character sequence separated by a space is eoncountered,
		it is interpreted as part of a given name. Any '+' found separated
		by a space from either surname or surname and given name will
		increment the length of the appoinment (number of '+' times the
		preferred time increment of the chosen doctor)"""

		if  value is not None and value != '':
			surname, firstname, increment = self.ParseAppEntry(value)
			self.GetPatientByName(surname, firstname);
			return
			if id is None:
				return
			for i in range(increment+1):
				self.SetCellBackgroundColour(row+i, col, self.clr_appointed)
				if i > 0:
					incstr = '+'
				else:
					incstr=''
				#self.SetCellValue(row+i, col, "%s%s, %s" % (incstr, surname, firstname))
		else:
			self.SetCellBackgroundColour(row, col, wxWHITE)
		datetime=self.GetCellDateTime(row, col)
		duration = self.session_interval + increment * self.session_interval

		dts = time.strftime("%Y-%m-%d %H:%M", datetime)
		print "%d min. Appointment made for % s on %s with Dr. [id=%d]" % (duration, value, dts, self.doctor_id)


	def OnCellChange(self, evt):
		row = evt.GetRow()
		col = evt.GetCol()
		value = self.GetCellValue(row, col)
		if value[0]=='+':
			return
		self.AppointmentMade(row, col, value)


	def OnIdle(self, evt):
		if self.moveTo != None:
			self.SetGridCursor(self.moveTo[0], self.moveTo[1])
			self.moveTo = None
		evt.Skip()


	def OnSelectCell(self, evt):
		self.log.write("OnSelectCell: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))

		# Another way to stay in a cell that has a bad value...
		row = self.GetGridCursorRow()
		col = self.GetGridCursorCol()
		if self.IsCellEditControlEnabled():
			self.HideCellEditControl()
			self.DisableCellEditControl()
		value = self.GetCellValue(row, col)
		if value == 'no good 2':
			return  # cancels the cell selection
		evt.Skip()


	def OnEditorShown(self, evt):
		self.log.write("OnEditorShown: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnEditorHidden(self, evt):
		self.log.write("OnEditorHidden: (%d,%d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnEditorCreated(self, evt):
		self.log.write("OnEditorCreated: (%d, %d) %s\n" %
			(evt.GetRow(), evt.GetCol(), evt.GetControl()))



#---------------------------------------------------------------------------

class TestFrame(wxFrame):
	def __init__(self, parent):
		wxFrame.__init__(self, parent, -1, "Simple Grid Demo", size=(640,480))
		grid = ScheduleGrid(self)



#---------------------------------------------------------------------------

if __name__ == '__main__':
	import sys
	app = wxPySimpleApp()
	frame = TestFrame(None)
	frame.Show(true)
	app.MainLoop()


#---------------------------------------------------------------------------


