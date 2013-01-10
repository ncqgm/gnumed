# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


import os.path
import datetime

import wx.calendar

from timelinelib.config.paths import ICONS_DIR
from timelinelib.time import PyTimeType
from timelinelib.wxgui.utils import _display_error_message


class PyDateTimePicker(wx.Panel):

    def __init__(self, parent, show_time=True, config=None):
        wx.Panel.__init__(self, parent)
        self.config = config
        self._create_gui()
        self.controller = PyDateTimePickerController(
            self.date_picker, self.time_picker, datetime.datetime.now)
        self.show_time(show_time)

    def show_time(self, show=True):
        self.time_picker.Show(show)
        self.GetSizer().Layout()

    def get_value(self):
        return self.controller.get_value()

    def set_value(self, value):
        self.controller.set_value(value)

    def _create_gui(self):
        self.date_picker = PyDatePicker(self)
        image = wx.Bitmap(os.path.join(ICONS_DIR, "calendar.png"))
        self.date_button = wx.BitmapButton(self, bitmap=image)
        self.Bind(wx.EVT_BUTTON, self._date_button_on_click, self.date_button)
        self.time_picker = PyTimePicker(self)
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.date_picker, proportion=1,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.date_button, proportion=0,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.time_picker, proportion=0,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)

    def _date_button_on_click(self, evt):
        try:
            wx_date = self._py_date_to_wx_date(self.date_picker.get_py_date())
            calendar_popup = CalendarPopup(self, wx_date, self.config)
            calendar_popup.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED,
                                self._calendar_on_date_changed)
            calendar_popup.Bind(wx.calendar.EVT_CALENDAR,
                                self._calendar_on_date_changed_dclick)
            btn = evt.GetEventObject()
            pos = btn.ClientToScreen((0,0))
            sz = btn.GetSize()
            calendar_popup.Position(pos, (0, sz[1]))
            calendar_popup.Popup()
            self.calendar_popup = calendar_popup
        except ValueError:
             _display_error_message(_("Invalid date"))


    def _calendar_on_date_changed(self, evt):
        wx_date = evt.GetEventObject().GetDate()
        py_date = datetime.datetime(wx_date.Year, wx_date.Month+1, wx_date.Day)
        self.date_picker.set_py_date(py_date)

    def _calendar_on_date_changed_dclick(self, evt):
        self.time_picker.SetFocus()
        self.calendar_popup.Dismiss()

    def _py_date_to_wx_date(self, py_date):
        return wx.DateTimeFromDMY(py_date.day, py_date.month-1, py_date.year,
                                  0, 0, 0)


class PyDateTimePickerController(object):

    def __init__(self, date_picker, time_picker, now_fn):
        self.date_picker = date_picker
        self.time_picker = time_picker
        self.now_fn = now_fn

    def get_value(self):
        time = datetime.time(0, 0)
        if self.time_picker.IsShown():
            time = self.time_picker.get_py_time()
        return datetime.datetime.combine(self.date_picker.get_py_date(), time)

    def set_value(self, py_date_time):
        if py_date_time == None:
            py_date_time = self.now_fn()
        self.date_picker.set_py_date(py_date_time.date())
        self.time_picker.set_py_time(py_date_time.time())


class CalendarPopup(wx.PopupTransientWindow):

    def __init__(self, parent, wx_date, config):
        self.config = config
        wx.PopupTransientWindow.__init__(self, parent, style=wx.BORDER_NONE)
        self._create_gui(wx_date)
        self.controller = CalendarPopupController(self)
        self._bind_events()

    def _create_gui(self, wx_date):
        BORDER = 2
        self.cal = self._create_calendar_control(wx_date, BORDER)
        size = self.cal.GetBestSize()
        self.SetSize((size.width + BORDER * 2, size.height + BORDER * 2))

    def _create_calendar_control(self, wx_date, border):
        style = self._get_cal_style()
        cal = wx.calendar.CalendarCtrl(self, -1, wx_date,
                                       pos=(border,border), style=style)
        self._set_cal_range(cal)
        return cal

    def _get_cal_style(self):
        style = (wx.calendar.CAL_SHOW_HOLIDAYS |
                 wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
        if self.config.week_start == "monday":
            style |= wx.calendar.CAL_MONDAY_FIRST
        else:
            style |= wx.calendar.CAL_SUNDAY_FIRST
        return style

    def _set_cal_range(self, cal):
        min_date, msg = PyTimeType().get_min_time()
        max_date, msg = PyTimeType().get_max_time()
        min_date = self._py_date_to_wx_date(min_date)
        max_date = self._py_date_to_wx_date(max_date) - wx.DateSpan.Day()
        cal.SetDateRange(min_date, max_date)

    def _py_date_to_wx_date(self, py_date):
        return wx.DateTimeFromDMY(py_date.day, py_date.month - 1, py_date.year,
                                  0, 0, 0)

    def _bind_events(self):
        def on_month(evt):
            self.controller.on_month()
        def on_day(evt):
            self.controller.on_day()
        self.cal.Bind(wx.calendar.EVT_CALENDAR_MONTH, on_month)
        self.cal.Bind(wx.calendar.EVT_CALENDAR_DAY, on_day)

    def OnDismiss(self):
        self.controller.on_dismiss()


class CalendarPopupController(object):

    def __init__(self, calendar_popup):
        self.calendar_popup = calendar_popup
        self.repop = False
        self.repoped = False

    def on_month(self):
        self.repop = True

    def on_day(self):
        self.repop = True

    def on_dismiss(self):
        # This funny code makes the calender control stay open when you change
        # month or day. The control is closed on a double-click on a day or
        # a single click outside of the control
        if self.repop and not self.repoped:
            self.calendar_popup.Popup()
            self.repoped = True


class PyDatePicker(wx.TextCtrl):

    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = PyDatePickerController(self)
        self._bind_events()
        self._resize_to_fit_text()

    def get_py_date(self):
        return self.controller.get_py_date()

    def set_py_date(self, py_date):
        self.controller.set_py_date(py_date)

    def get_date_string(self):
        return self.GetValue()

    def set_date_string(self, date_string):
        return self.SetValue(date_string)

    def _bind_events(self):
        def on_set_focus(evt):
            # CallAfter is a trick to prevent default behavior of selecting all
            # text when a TextCtrl is given focus
            wx.CallAfter(self.controller.on_set_focus)
        self.Bind(wx.EVT_SET_FOCUS, on_set_focus)
        def on_kill_focus(evt):
            # Trick to not make selection text disappear when focus is lost (we
            # remove the selection instead)
            self.controller.on_kill_focus()
            self.SetSelection(0, 0)
        self.Bind(wx.EVT_KILL_FOCUS, on_kill_focus)
        def on_char(evt):
            if evt.GetKeyCode() == wx.WXK_TAB:
                if evt.ShiftDown():
                    skip = self.controller.on_shift_tab()
                else:
                    skip = self.controller.on_tab()
            else:
                skip = True
            evt.Skip(skip)
        self.Bind(wx.EVT_CHAR, on_char)
        def on_text(evt):
            self.controller.on_text_changed()
        self.Bind(wx.EVT_TEXT, on_text)
        def on_key_down(evt):
            if evt.GetKeyCode() == wx.WXK_UP:
                self.controller.on_up()
            elif evt.GetKeyCode() == wx.WXK_DOWN:
                self.controller.on_down()
            else:
                evt.Skip()
        self.Bind(wx.EVT_KEY_DOWN, on_key_down)

    def _resize_to_fit_text(self):
        w, h = self.GetTextExtent("0000-00-00")
        width = w + 20
        self.SetMinSize((width, -1))


class PyDatePickerController(object):

    def __init__(self, py_date_picker, error_bg="pink"):
        self.py_date_picker = py_date_picker
        self.error_bg = error_bg
        self.original_bg = self.py_date_picker.GetBackgroundColour()
        self.separator = PyTimeType().event_date_string(PyTimeType().now())[4]
        self.region_year = 0
        self.region_month = 1
        self.region_day = 2
        self.region_siblings = ((self.region_year, self.region_month),
                                (self.region_month, self.region_day))
        self.preferred_day = None
        self.save_preferred_day = True
        self.last_selection = None

    def get_py_date(self):
        try:
            (year, month, day) = self._parse_year_month_day()
            py_date = datetime.date(year, month, day)
            self._ensure_within_allowed_period(py_date)
            return py_date
        except ValueError:
            raise ValueError("Invalid date.")

    def set_py_date(self, py_date):
        date_string = PyTimeType().event_date_string(py_date)
        self.py_date_picker.set_date_string(date_string)

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.py_date_picker.SetSelection(start, end)
        else:
            self._select_region_if_possible(self.region_year)
            self.last_selection = self.py_date_picker.GetSelection()

    def on_kill_focus(self):
        if self.last_selection:
            self.last_selection = self.py_date_picker.GetSelection()

    def on_tab(self):
        for (left_region, right_region) in self.region_siblings:
            if self._insertion_point_in_region(left_region):
                self._select_region_if_possible(right_region)
                return False
        return True

    def on_shift_tab(self):
        for (left_region, right_region) in self.region_siblings:
            if self._insertion_point_in_region(right_region):
                self._select_region_if_possible(left_region)
                return False
        return True

    def on_text_changed(self):
        self._change_background_depending_on_date_validity()
        if self._current_date_is_valid():
            current_date = self.get_py_date()
            # To prevent saving of preferred day when year or month is changed
            # in on_up() and on_down()...
            # Save preferred day only when text is entered in the date text
            # control and not when up or down keys has been used.
            # When up and down keys are used, the preferred day is saved in
            # on_up() and on_down() only when day is changed.
            if self.save_preferred_day:
                self._save_preferred_day(current_date)

    def on_up(self):
        def increment_year(date):
            if date.year < PyTimeType().get_max_time()[0].year - 1:
                return self._set_valid_day(date.year + 1, date.month, date.day)
            return date
        def increment_month(date):
            if date.month < 12:
                return self._set_valid_day(date.year, date.month + 1,
                                           date.day)
            elif date.year < PyTimeType().get_max_time()[0].year - 1:
                return self._set_valid_day(date.year + 1, 1, date.day)
            return date
        def increment_day(date):
            if date <  PyTimeType().get_max_time()[0].date() - datetime.timedelta(days=1):
                return date + datetime.timedelta(days=1)
            return date
        if not self._current_date_is_valid():
            return
        selection = self.py_date_picker.GetSelection()
        current_date = self.get_py_date()
        if self._insertion_point_in_region(self.region_year):
            new_date = increment_year(current_date)
        elif self._insertion_point_in_region(self.region_month):
            new_date = increment_month(current_date)
        else:
            new_date = increment_day(current_date)
            self._save_preferred_day(new_date)
        if current_date != new_date:
            self._set_new_date_and_restore_selection(new_date, selection)

    def on_down(self):
        def decrement_year(date):
            if date.year > PyTimeType().get_min_time()[0].year:
                return self._set_valid_day(date.year - 1, date.month, date.day)
            return date
        def decrement_month(date):
            if date.month > 1:
                return self._set_valid_day(date.year, date.month - 1, date.day)
            elif date.year > PyTimeType().get_min_time()[0].year:
                return self._set_valid_day(date.year - 1, 12, date.day)
            return date
        def decrement_day(date):
            if date.day > 1:
                return date.replace(day=date.day - 1)
            elif date.month > 1:
                return self._set_valid_day(date.year, date.month - 1, 31)
            elif date.year > PyTimeType().get_min_time()[0].year:
                return self._set_valid_day(date.year - 1, 12, 31)
            return date
        if not self._current_date_is_valid():
            return
        selection = self.py_date_picker.GetSelection()
        current_date = self.get_py_date()
        if self._insertion_point_in_region(self.region_year):
            new_date = decrement_year(current_date)
        elif self._insertion_point_in_region(self.region_month):
            new_date = decrement_month(current_date)
        else:
            new_date = decrement_day(current_date)
            self._save_preferred_day(new_date)
        if current_date != new_date:
            self._set_new_date_and_restore_selection(new_date, selection)

    def _change_background_depending_on_date_validity(self):
        if self._current_date_is_valid():
            self.py_date_picker.SetBackgroundColour(self.original_bg)
        else:
            self.py_date_picker.SetBackgroundColour(self.error_bg)
        self.py_date_picker.SetFocus()
        self.py_date_picker.Refresh()

    def _parse_year_month_day(self):
        components = self.py_date_picker.get_date_string().split(self.separator)
        if len(components) != 3:
            raise ValueError()
        year  = int(components[self.region_year])
        month = int(components[self.region_month])
        day   = int(components[self.region_day])
        return (year, month, day)

    def _ensure_within_allowed_period(self, py_date):
        py_date_time = datetime.datetime(py_date.year, py_date.month, py_date.day)
        if (py_date_time >= PyTimeType().get_max_time()[0] or
            py_date_time <  PyTimeType().get_min_time()[0]):
            raise ValueError()

    def _set_new_date_and_restore_selection(self, new_date, selection):
        def restore_selection(selection):
            self.py_date_picker.SetSelection(selection[0], selection[1])
        self.save_preferred_day = False
        if self.preferred_day != None:
            new_date = self._set_valid_day(new_date.year, new_date.month,
                                           self.preferred_day)
        self.set_py_date(new_date)
        restore_selection(selection)
        self.save_preferred_day = True

    def _set_valid_day(self, new_year, new_month, new_day):
        done = False
        while not done:
            try:
                date = datetime.date(year=new_year, month=new_month, day=new_day)
                done = True
            except Exception, ex:
                new_day -= 1
        return date

    def _save_preferred_day(self, date):
        if date.day > 28:
            self.preferred_day = date.day
        else:
            self.preferred_day = None

    def _current_date_is_valid(self):
        try:
            self.get_py_date()
        except ValueError:
            return False
        return True

    def _select_region_if_possible(self, region):
        region_range = self._get_region_range(region)
        if region_range:
            self.py_date_picker.SetSelection(region_range[0], region_range[-1])

    def _insertion_point_in_region(self, n):
        region_range = self._get_region_range(n)
        if region_range:
            return self.py_date_picker.GetInsertionPoint() in region_range

    def _get_region_range(self, n):
        # Returns a range of valid cursor positions for a valid region year,
        # month or day.
        def region_is_not_valid(region):
            return region not in (self.region_year, self.region_month,
                                  self.region_day)
        def date_has_exactly_two_seperators(datestring):
            return len(datestring.split(self.separator)) == 3
        def calculate_pos_range(region, datestring):
            pos_of_separator1 = datestring.find(self.separator)
            pos_of_separator2 = datestring.find(self.separator,
                                                pos_of_separator1 + 1)
            if region == self.region_year:
                return range(0, pos_of_separator1 + 1)
            elif region == self.region_month:
                return range(pos_of_separator1 + 1, pos_of_separator2 + 1)
            else:
                return range(pos_of_separator2 + 1, len(datestring) + 1)
        if region_is_not_valid(n):
            return None
        date = self.py_date_picker.get_date_string()
        if not date_has_exactly_two_seperators(date):
            return None
        pos_range = calculate_pos_range(n, date)
        return pos_range


class PyTimePicker(wx.TextCtrl):

    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = PyTimePickerController(self)
        self._bind_events()
        self._resize_to_fit_text()

    def get_py_time(self):
        return self.controller.get_py_time()

    def set_py_time(self, py_time):
        self.controller.set_py_time(py_time)

    def get_time_string(self):
        return self.GetValue()

    def set_time_string(self, time_string):
        self.SetValue(time_string)

    def _bind_events(self):
        def on_set_focus(evt):
            # CallAfter is a trick to prevent default behavior of selecting all
            # text when a TextCtrl is given focus
            wx.CallAfter(self.controller.on_set_focus)
        self.Bind(wx.EVT_SET_FOCUS, on_set_focus)
        def on_kill_focus(evt):
            # Trick to not make selection text disappear when focus is lost (we
            # remove the selection instead)
            self.controller.on_kill_focus()
            self.SetSelection(0, 0)
        self.Bind(wx.EVT_KILL_FOCUS, on_kill_focus)
        def on_char(evt):
            if evt.GetKeyCode() == wx.WXK_TAB:
                if evt.ShiftDown():
                    skip = self.controller.on_shift_tab()
                else:
                    skip = self.controller.on_tab()
            else:
                skip = True
            evt.Skip(skip)
        self.Bind(wx.EVT_CHAR, on_char)
        def on_text(evt):
            self.controller.on_text_changed()
        self.Bind(wx.EVT_TEXT, on_text)
        def on_key_down(evt):
            if evt.GetKeyCode() == wx.WXK_UP:
                self.controller.on_up()
            elif evt.GetKeyCode() == wx.WXK_DOWN:
                self.controller.on_down()
            else:
                evt.Skip()
        self.Bind(wx.EVT_KEY_DOWN, on_key_down)

    def _resize_to_fit_text(self):
        w, h = self.GetTextExtent("00:00")
        width = w + 20
        self.SetMinSize((width, -1))


class PyTimePickerController(object):

    def __init__(self, py_time_picker):
        self.py_time_picker = py_time_picker
        self.original_bg = self.py_time_picker.GetBackgroundColour()
        self.separator = PyTimeType().event_time_string(PyTimeType().now())[2]
        self.hour_part = 0
        self.minute_part = 1
        self.last_selection = None

    def get_py_time(self):
        try:
            split = self.py_time_picker.get_time_string().split(self.separator)
            if len(split) != 2:
                raise ValueError()
            hour_string, minute_string = split
            hour = int(hour_string)
            minute = int(minute_string)
            return datetime.time(hour, minute)
        except ValueError:
            raise ValueError("Invalid time.")

    def set_py_time(self, py_time):
        time_string = PyTimeType().event_time_string(py_time)
        self.py_time_picker.set_time_string(time_string)

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.py_time_picker.SetSelection(start, end)
        else:
            self._select_part(self.hour_part)

    def on_kill_focus(self):
        self.last_selection = self.py_time_picker.GetSelection()

    def on_tab(self):
        if self._in_minute_part():
            return True
        self._select_part(self.minute_part)
        return False

    def on_shift_tab(self):
        if self._in_hour_part():
            return True
        self._select_part(self.hour_part)
        return False

    def on_text_changed(self):
        try:
            self.get_py_time()
            self.py_time_picker.SetBackgroundColour(self.original_bg)
        except ValueError:
            self.py_time_picker.SetBackgroundColour("pink")
        self.py_time_picker.Refresh()

    def on_up(self):
        def increment_hour(time):
            new_hour = time.hour + 1
            if new_hour > 23:
                new_hour = 0
            return time.replace(hour=new_hour)
        def increment_minutes(time):
            new_hour = time.hour
            new_minute = time.minute + 1
            if new_minute > 59:
                new_minute = 0
                new_hour = time.hour + 1
                if new_hour > 23:
                    new_hour = 0
            return time.replace(hour=new_hour, minute=new_minute)
        if not self._time_is_valid():
            return
        selection = self.py_time_picker.GetSelection()
        current_time = self.get_py_time()
        if self._in_hour_part():
            new_time = increment_hour(current_time)
        else:
            new_time = increment_minutes(current_time)
        if current_time != new_time:
            self._set_new_time_and_restore_selection(new_time, selection)

    def on_down(self):
        def decrement_hour(time):
            new_hour = time.hour - 1
            if new_hour < 0:
                new_hour = 23
            return time.replace(hour=new_hour)
        def decrement_minutes(time):
            new_hour = time.hour
            new_minute = time.minute - 1
            if new_minute < 0:
                new_minute = 59
                new_hour = time.hour - 1
                if new_hour < 0:
                    new_hour = 23
            return time.replace(hour=new_hour, minute=new_minute)
        if not self._time_is_valid():
            return
        selection = self.py_time_picker.GetSelection()
        current_time = self.get_py_time()
        if self._in_hour_part():
            new_time = decrement_hour(current_time)
        else:
            new_time = decrement_minutes(current_time)
        if current_time != new_time:
            self._set_new_time_and_restore_selection(new_time, selection)

    def _set_new_time_and_restore_selection(self, new_time, selection):
        def restore_selection(selection):
            self.py_time_picker.SetSelection(selection[0], selection[1])
        self.set_py_time(new_time)
        restore_selection(selection)

    def _time_is_valid(self):
        try:
            self.get_py_time()
        except ValueError:
            return False
        return True

    def _select_part(self, part):
        if self._separator_pos() == -1:
            return
        if part == self.hour_part:
            self.py_time_picker.SetSelection(0, self._separator_pos())
        else:
            time_string_len = len(self.py_time_picker.get_time_string())
            self.py_time_picker.SetSelection(self._separator_pos() + 1, time_string_len)
        self.preferred_part = part

    def _in_hour_part(self):
        if self._separator_pos() == -1:
            return
        return self.py_time_picker.GetInsertionPoint() <= self._separator_pos()

    def _in_minute_part(self):
        if self._separator_pos() == -1:
            return
        return self.py_time_picker.GetInsertionPoint() > self._separator_pos()

    def _separator_pos(self):
        return self.py_time_picker.get_time_string().find(self.separator)
