__version__ = "$Revision: 1.2 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

from wxPython.wx import *
from wxPython.grid import *
#from wxPython.lib.mixins.grid import wxGridAutoEditMixin
from wxPython.lib import colourdb

import time

import gettext
_ = gettext.gettext

#--------------------------------------------------------------------------

days_of_week = (_("Monday"),
                _("Tuesday"),
				_("Wednesday"),
				_("Thursday"),
				_("Friday"),
				_("Saturday"),
				_("Sunday"))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ParseTimeInterval(interval):
	res = []
	s = string.split(interval, "-")
	if len(s) != 2:
		return None
	for str in s:
		h,m = string.split(str, ":")
		res.append((int(h), int(m)))
	return res

def GenerateExcludedTimes(exclude, interval=15):
	"""returns a list of time strings in the format 'hh:mm'
	'exclude' is a list of time interval strings in the format
	'hh:mm-hh:mm' separarted by single white spaces between
	time interval strings. Interval is the time interval in
	minutes between two generated intervals"""

	excl = []
	exlist = string.split(exclude, " ")
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


def DayOfWeekLabels(include_sunday=1):
	"""Return a list of day names starting with Monday,
	optionally including Sunday if 'include_sunday' is not 0"""

	if include_sunday:
		return days_of_week
	else:
		return days_of_week[:6]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class ScheduleGrid(wxGrid): ##, wxGridAutoEditMixin):
    def __init__(self, parent, hour_start=9, hour_end=18, session_interval=15, exclude=None, log=sys.stdout):
        wxGrid.__init__(self, parent, -1)
        ##wxGridAutoEditMixin.__init__(self)
        self.log = log
        self.moveTo = None
        self.Date = time.localtime()

        self.clr_appointed = wxColour(240,220,140)
        self.clr_not_available = wxLIGHT_GREY
        self.clr_today = wxColour(255,255,125)
        self.clr_selected_day = wxColour(190,225,255)

        #EVT_IDLE(self, self.OnIdle)
        self.weekdaylabels = DayOfWeekLabels(include_sunday=0)
        self.timelabels = TimeLabels(hour_start, hour_end, session_interval, exclude)
        self.CreateGrid(len(self.timelabels), len(self.weekdaylabels))

        #label the columns
        labels =  self.weekdaylabels
        index=0
        for index in range(len(labels)):
              self.SetColLabelValue(index, labels[index])

        #label the rows
        labels = self.timelabels
        index=0
        for index in range(len(labels)):
            self.SetRowLabelValue(index, labels[index])

        self.SetColLabelAlignment(wxALIGN_LEFT, wxALIGN_BOTTOM)
        self.SetColumnColours()

        # test all the events
        EVT_GRID_CELL_LEFT_CLICK(self, self.OnCellLeftClick)
        EVT_GRID_CELL_RIGHT_CLICK(self, self.OnCellRightClick)
        EVT_GRID_CELL_LEFT_DCLICK(self, self.OnCellLeftDClick)
        EVT_GRID_CELL_RIGHT_DCLICK(self, self.OnCellRightDClick)

        EVT_GRID_LABEL_LEFT_CLICK(self, self.OnLabelLeftClick)
        EVT_GRID_LABEL_RIGHT_CLICK(self, self.OnLabelRightClick)
        EVT_GRID_LABEL_LEFT_DCLICK(self, self.OnLabelLeftDClick)
        EVT_GRID_LABEL_RIGHT_DCLICK(self, self.OnLabelRightDClick)

        EVT_GRID_ROW_SIZE(self, self.OnRowSize)
        EVT_GRID_COL_SIZE(self, self.OnColSize)

        EVT_GRID_RANGE_SELECT(self, self.OnRangeSelect)
        EVT_GRID_CELL_CHANGE(self, self.OnCellChange)
        EVT_GRID_SELECT_CELL(self, self.OnSelectCell)

        EVT_GRID_EDITOR_SHOWN(self, self.OnEditorShown)
        EVT_GRID_EDITOR_HIDDEN(self, self.OnEditorHidden)
        EVT_GRID_EDITOR_CREATED(self, self.OnEditorCreated)


    def SetColumnColours(self):
        #mark today in special colours
        current_week = time.strftime('%W')
        displayed_week = time.strftime('%W', self.Date)
        if current_week == displayed_week:
            attr = wxGridCellAttr()
            attr.SetBackgroundColour(self.clr_today)
            attr.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD))
            #make Monday first day of the week
            current_day = int(time.strftime('%w'))-1
            if current_day == -1:
                current_day=6
            self.SetColAttr(current_day, attr)
        #mark day selected in Calendar in special colours
        attr = wxGridCellAttr()
        attr.SetBackgroundColour(self.clr_selected_day)
        attr.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD))
        #make Monday first day of the week
        selected_day = int(time.strftime('%w', self.Date))-1
        if selected_day == -1:
            selected_day=6
        self.SetColAttr(selected_day, attr)


    def SetDate(self,date):
        self.Date=Date
        self.SetColumnColours()

    def AppointmentSelected(self, row, col):
        day = self.weekdaylabels[col]
        time = self.timelabels[row]
        value = self.GetCellValue(row, col)
        print "Appointment on %s at %s o'clock for %s" % (day, time, value)

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
        self.log.write("OnCellRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
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
            if surname[0]=='+' and len(surname)>1: surname=surname[1:]
            increment = string.count(sl[1], '+')
            if increment < 1:
                firstname=sl[1]
                increment=string.count(sl[2], '+')
            print 'increment is',increment
        except:
            pass
        return surname, firstname, increment



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
            for i in range(increment+1):
                print 'i=', i
                self.SetCellBackgroundColour(row+i, col, self.clr_appointed)
                if i > 0: incstr = '+'
                else: incstr=''
                self.SetCellValue(row+i, col, "%s%s, %s" % (incstr, surname, firstname))
        else:
            self.SetCellBackgroundColour(row, col, wxWHITE)


    def OnCellChange(self, evt):
        self.log.write("OnCellChange: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Show how to stay in a cell that has bad data.  We can't just
        # call SetGridCursor here since we are nested inside one so it
        # won't have any effect.  Instead, set coordinants to move to in
        # idle time.
        row = evt.GetRow()
        col = evt.GetCol()
        value = self.GetCellValue(row, col)
        self.AppointmentMade(row, col, value)
        #value = self.GetCellValue(evt.GetRow(), evt.GetCol())
        #if value == 'no good':
        #    self.moveTo = evt.GetRow(), evt.GetCol()


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


