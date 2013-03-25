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

import wx.calendar

from timelinelib.config.paths import ICONS_DIR
from timelinelib.time import try_to_create_wx_date_time_from_dmy
from timelinelib.time import WxTimeType
from timelinelib.wxgui.utils import _display_error_message


class WxDateTimePicker(wx.Panel):

    def __init__(self, parent, show_time=True, config=None):
        wx.Panel.__init__(self, parent)
        self.config = config
        self._create_gui()
        self.controller = WxDateTimePickerController(
            self.date_picker, self.time_picker, wx.DateTime.Now)
        self.show_time(show_time)

    def show_time(self, show=True):
        self.time_picker.Show(show)
        self.GetSizer().Layout()

    def set_value(self, value):
        self.controller.set_value(value)

    def get_value(self):
        return self.controller.get_value()

    def _create_gui(self):
        self.date_picker = WxDatePicker(self)
        self.date_button = self._create_date_button()
        self.time_picker = WxTimePicker(self)
        self._layout_controls()

    def _create_date_button(self):
        image = wx.Bitmap(os.path.join(ICONS_DIR, "calendar.png"))
        date_button = wx.BitmapButton(self, bitmap=image)
        self.Bind(wx.EVT_BUTTON, self._date_button_on_click, date_button)
        return date_button

    def _layout_controls(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        flags = wx.ALIGN_CENTER_VERTICAL
        sizer.Add(self.date_picker, proportion=1, flag=flags)
        sizer.Add(self.date_button, proportion=0, flag=flags)
        sizer.Add(self.time_picker, proportion=0, flag=flags)
        self.SetSizerAndFit(sizer)

    def _date_button_on_click(self, evt):
        try:
            self.calendar_popup = self._create_calendar_popup()
            self._position_calendar_popup(evt)
            self.calendar_popup.Popup()
        except:
            _display_error_message(_("Invalid date"))

    def _create_calendar_popup(self):
        wx_date = self.controller.get_value()
        calendar_popup = CalendarPopup(self, wx_date, self.config)
        calendar_popup.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED,
                            self._calendar_on_date_changed)
        calendar_popup.Bind(wx.calendar.EVT_CALENDAR,
                            self._calendar_on_date_changed_dclick)
        return calendar_popup

    def _position_calendar_popup(self, evt):
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen((0,0))
        size = btn.GetSize()
        self.calendar_popup.Position(pos, (0, size[1]))

    def _calendar_on_date_changed(self, evt):
        wx_date = evt.GetEventObject().GetDate()
        self.date_picker.set_date(wx_date)

    def _calendar_on_date_changed_dclick(self, evt):
        self.time_picker.SetFocus()
        self.calendar_popup.Dismiss()


class WxDateTimePickerController(object):

    def __init__(self, date_picker, time_picker, now_fn):
        self.date_picker = date_picker
        self.time_picker = time_picker
        self.now_fn = now_fn

    def set_value(self, date_time):
        if date_time == None:
            date_time = self.now_fn()
        self.date_picker.set_date(date_time)
        self.time_picker.set_time(date_time)

    def get_value(self):
        wx_date = self.date_picker.get_date()
        if self.time_picker.IsShown():
            wx_time = self.time_picker.get_time()
            wx_date.SetHour(wx_time.GetHour())
            wx_date.SetMinute(wx_time.GetMinute())
        return wx_date


class CalendarPopup(wx.PopupTransientWindow):

    def __init__(self, parent, wx_date, config):
        self.config = config
        self.controller = CalendarPopupController(self)
        wx.PopupTransientWindow.__init__(self, parent, style=wx.BORDER_NONE)
        border = 2
        style = self._get_cal_style()
        self.cal = wx.calendar.CalendarCtrl(self, -1, wx_date,
                                            pos=(border,border), style=style)
        self._set_cal_range()
        self._set_size(border)
        self._bind_events()

    def _get_cal_style(self):
        style = (wx.calendar.CAL_SHOW_HOLIDAYS |
                 wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
        if self.config.week_start == "monday":
            style |= wx.calendar.CAL_MONDAY_FIRST
        else:
            style |= wx.calendar.CAL_SUNDAY_FIRST
        return style

    def _set_cal_range(self):
        min_date, msg = WxTimeType().get_min_time()
        max_date, msg = WxTimeType().get_max_time()
        max_date -= wx.DateSpan.Day()
        self.cal.SetDateRange(min_date, max_date)

    def _set_size(self, border):
        size = self.cal.GetBestSize()
        self.SetSize((size.width + border * 2, size.height + border * 2))

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


class WxDatePicker(wx.TextCtrl):

    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = WxDatePickerController(self)
        self._bind_events()
        self._resize_to_fit_text()

    def get_date(self):
        return self.controller.get_date()

    def set_date(self, wx_date):
        self.controller.set_date(wx_date)

    def get_date_string(self):
        return self.GetValue()

    def set_date_string(self, date_string):
        return self.SetValue(date_string)

    def _bind_events(self):
        self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)
        self.Bind(wx.EVT_CHAR, self._on_char)
        self.Bind(wx.EVT_TEXT, self._on_text)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_set_focus(self, evt):
        # CallAfter is a trick to prevent default behavior of selecting all
        # text when a TextCtrl is given focus
        wx.CallAfter(self.controller.on_set_focus)

    def _on_kill_focus(self, evt):
        # Trick to not make selection text disappear when focus is lost (we
        # remove the selection instead)
        self.controller.on_kill_focus()
        self.SetSelection(0, 0)

    def _on_char(self, evt):
        if evt.GetKeyCode() == wx.WXK_TAB:
            if evt.ShiftDown():
                skip = self.controller.on_shift_tab()
            else:
                skip = self.controller.on_tab()
        else:
            skip = True
        evt.Skip(skip)

    def _on_text(self, evt):
        self.controller.on_text_changed()

    def _on_key_down(self, evt):
        if evt.GetKeyCode() == wx.WXK_UP:
            self.controller.on_up()
        elif evt.GetKeyCode() == wx.WXK_DOWN:
            self.controller.on_down()
        else:
            evt.Skip()

    def _resize_to_fit_text(self):
        w, h = self.GetTextExtent("0000-00-00")
        width = w + 20
        self.SetMinSize((width, -1))


class WxDatePickerController(object):

    def __init__(self, py_date_picker, error_bg="pink"):
        self.wx_date_picker = py_date_picker
        self.error_bg = error_bg
        self.original_bg = self.wx_date_picker.GetBackgroundColour()
        self.separator = WxTimeType().event_date_string(WxTimeType().now())[4]
        self.region_year = 0
        self.region_month = 1
        self.region_day = 2
        self.region_siblings = ((self.region_year, self.region_month),
                                (self.region_month, self.region_day))
        self.preferred_day = None
        self.save_preferred_day = True
        self.last_selection = None

    def get_date(self):
        try:
            (year, month, day) = self._parse_year_month_day()
            if year == 0:
                raise ValueError("Invalid date.")
            if year < 0:
                year +=1
            wx_date = try_to_create_wx_date_time_from_dmy(day, month - 1, year)
            self._ensure_date_within_allowed_period(wx_date)
            return wx_date
        except ValueError:
            raise ValueError("Invalid date.")

    def set_date(self, wx_date):
        bc_year = wx.DateTime.ConvertYearToBC(wx_date.Year)
        tmp_date = wx.DateTimeFromDMY(wx_date.Day, wx_date.Month, bc_year)
        date_string = WxTimeType().event_date_string(tmp_date)
        self.wx_date_picker.set_date_string(date_string)

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.wx_date_picker.SetSelection(start, end)
        else:
            self._select_region_if_possible(self.region_year)
            self.last_selection = self.wx_date_picker.GetSelection()

    def on_kill_focus(self):
        if self.last_selection:
            self.last_selection = self.wx_date_picker.GetSelection()

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
            current_date = self.get_date()
            # To prevent saving of preferred day when year or month is changed
            # in on_up() and on_down()...
            # Save preferred day only when text is entered in the date text
            # control and not when up or down keys has been used.
            # When up and down keys are used, the preferred day is saved in
            # on_up() and on_down() only when day is changed.
            if self.save_preferred_day:
                self._save_preferred_day(current_date)

    def on_up(self):
        if not self._current_date_is_valid():
            return
        if self._insertion_point_in_region(self.region_year):
            new_date = self._increment_year()
        elif self._insertion_point_in_region(self.region_month):
            new_date = self._increment_month()
        else:
            new_date = self._increment_day()
            self._save_preferred_day(new_date)
        self._set_new_date_and_restore_selection(new_date)

    def on_down(self):
        if not self._current_date_is_valid():
            return
        if self._insertion_point_in_region(self.region_year):
            new_date = self._decrement_year()
        elif self._insertion_point_in_region(self.region_month):
            new_date = self._decrement_month()
        else:
            new_date = self._decrement_day()
            self._save_preferred_day(new_date)
        self._set_new_date_and_restore_selection(new_date)

    def _increment_year(self):
        date = self.get_date()
        if date.Year < WxTimeType().get_max_time()[0].Year - 1:
            date = self._set_valid_day(date.Year + 1, date.Month, date.Day)
        return date

    def _increment_month(self):
        date = self.get_date()
        if date.Month < 11:
            date = self._set_valid_day(date.Year, date.Month + 1, date.Day)
        elif date.Year < WxTimeType().get_max_time()[0].Year - 1:
            date = self._set_valid_day(date.Year + 1, 0, date.Day)
        return date

    def _increment_day(self):
        date = self.get_date()
        if date <  WxTimeType().get_max_time()[0] - wx.TimeSpan.Day():
            date = date + wx.DateSpan.Day()
        return date

    def _decrement_year(self):
        date = self.get_date()
        if date.Year > WxTimeType().get_min_time()[0].Year:
            date = self._set_valid_day(date.Year - 1, date.Month, date.Day)
        return date

    def _decrement_month(self):
        date = self.get_date()
        if date.Month > 0:
            date = self._set_valid_day(date.Year, date.Month - 1, date.Day)
        elif date.Year > WxTimeType().get_min_time()[0].Year:
            date = self._set_valid_day(date.Year - 1, 11, date.Day)
        return date

    def _decrement_day(self):
        date = self.get_date()
        if date.Day > 1:
            date.SetDay(date.Day - 1)
        elif date.Month > 0:
            date = self._set_valid_day(date.Year, date.Month - 1, 31)
        elif date.Year > WxTimeType().get_min_time()[0].Year:
            date = self._set_valid_day(date.Year - 1, 11, 31)
        return date

    def _change_background_depending_on_date_validity(self):
        if self._current_date_is_valid():
            color = self.original_bg
        else:
            color = self.error_bg
        self.wx_date_picker.SetBackgroundColour(color)
        self.wx_date_picker.SetFocus()
        self.wx_date_picker.Refresh()

    def _parse_year_month_day(self):
        date_string = self.wx_date_picker.get_date_string()
        date_bc = False
        if (date_string[0:1] == self.separator):
            date_string = date_string[1:]
            date_bc = True
        components = date_string.split(self.separator)
        if len(components) != 3:
            raise ValueError()
        year  = int(components[self.region_year])
        if date_bc:
            year = -year
        month = int(components[self.region_month])
        day   = int(components[self.region_day])
        return (year, month, day)

    def _ensure_date_within_allowed_period(self, wx_date):
        if (wx_date >= WxTimeType().get_max_time()[0] or
            wx_date <  WxTimeType().get_min_time()[0]):
            raise ValueError()

    def _set_new_date_and_restore_selection(self, new_date):
        def restore_selection(selection):
            self.wx_date_picker.SetSelection(selection[0], selection[1])
        selection = self.wx_date_picker.GetSelection()
        self.save_preferred_day = False
        if self.preferred_day != None:
            new_date = self._set_valid_day(new_date.Year, new_date.Month,
                                           self.preferred_day)
        self.set_date(new_date)
        restore_selection(selection)
        self.save_preferred_day = True

    def _set_valid_day(self, new_year, new_month, new_day):
        while True:
            try:
                return try_to_create_wx_date_time_from_dmy(new_day, new_month, new_year)
            except ValueError:
                new_day -= 1

    def _save_preferred_day(self, date):
        day = date.Day
        if day > 28:
            self.preferred_day = day
        else:
            self.preferred_day = None

    def _current_date_is_valid(self):
        try:
            self.get_date()
        except ValueError:
            return False
        return True

    def _select_region_if_possible(self, region):
        region_range = self._get_region_range(region)
        if region_range:
            self.wx_date_picker.SetSelection(region_range[0], region_range[-1])

    def _insertion_point_in_region(self, n):
        region_range = self._get_region_range(n)
        if region_range:
            return self.wx_date_picker.GetInsertionPoint() in region_range

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
        date = self.wx_date_picker.get_date_string()
        if not date_has_exactly_two_seperators(date):
            return None
        pos_range = calculate_pos_range(n, date)
        return pos_range


class WxTimePicker(wx.TextCtrl):

    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = WxTimePickerController(self)
        self._bind_events()
        self._resize_to_fit_text()

    def get_time(self):
        return self.controller.get_time()

    def set_time(self, wx_time):
        self.controller.set_time(wx_time)

    def get_time_string(self):
        return self.GetValue()

    def set_time_string(self, time_string):
        self.SetValue(time_string)

    def _bind_events(self):
        self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)
        self.Bind(wx.EVT_CHAR, self._on_char)
        self.Bind(wx.EVT_TEXT, self._on_text)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_set_focus(self, evt):
        # CallAfter is a trick to prevent default behavior of selecting all
        # text when a TextCtrl is given focus
        wx.CallAfter(self.controller.on_set_focus)

    def _on_kill_focus(self, evt):
        # Trick to not make selection text disappear when focus is lost (we
        # remove the selection instead)
        self.controller.on_kill_focus()
        self.SetSelection(0, 0)

    def _on_char(self, evt):
        if evt.GetKeyCode() == wx.WXK_TAB:
            if evt.ShiftDown():
                skip = self.controller.on_shift_tab()
            else:
                skip = self.controller.on_tab()
        else:
            skip = True
        evt.Skip(skip)

    def _on_text(self, evt):
        self.controller.on_text_changed()

    def _on_key_down(self, evt):
        if evt.GetKeyCode() == wx.WXK_UP:
            self.controller.on_up()
        elif evt.GetKeyCode() == wx.WXK_DOWN:
            self.controller.on_down()
        else:
            evt.Skip()

    def _resize_to_fit_text(self):
        w, h = self.GetTextExtent("00:00")
        width = w + 20
        self.SetMinSize((width, -1))


class WxTimePickerController(object):

    def __init__(self, wx_time_picker):
        self.wx_time_picker = wx_time_picker
        self.original_bg = self.wx_time_picker.GetBackgroundColour()
        self.separator = WxTimeType().event_time_string(WxTimeType().now())[2]
        self.hour_part = 0
        self.minute_part = 1
        self.last_selection = None

    def get_time(self):
        try:
            split = self.wx_time_picker.get_time_string().split(self.separator)
            if len(split) != 2:
                raise ValueError()
            hour_string, minute_string = split
            hour = int(hour_string)
            minute = int(minute_string)
            return wx.DateTimeFromHMS(hour, minute, 0)
        except ValueError:
            raise ValueError("Invalid time.")

    def set_time(self, wx_time):
        time_string = WxTimeType().event_time_string(wx_time)
        self.wx_time_picker.set_time_string(time_string)

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.wx_time_picker.SetSelection(start, end)
        else:
            self._select_part(self.hour_part)

    def on_kill_focus(self):
        self.last_selection = self.wx_time_picker.GetSelection()

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
            self.get_time()
            self.wx_time_picker.SetBackgroundColour(self.original_bg)
        except ValueError:
            self.wx_time_picker.SetBackgroundColour("pink")
        self.wx_time_picker.Refresh()

    def on_up(self):
        if not self._time_is_valid():
            return
        if self._in_hour_part():
            new_time = self._increment_hour()
        else:
            new_time = self._increment_minutes()
        self._set_new_time_and_restore_selection(new_time)

    def on_down(self):
        if not self._time_is_valid():
            return
        if self._in_hour_part():
            new_time = self._decrement_hour()
        else:
            new_time = self._decrement_minutes()
        self._set_new_time_and_restore_selection(new_time)

    def _increment_hour(self):
        time = self.get_time()
        new_hour = time.Hour + 1
        if new_hour > 23:
            new_hour = 0
        time.SetHour(new_hour)
        return time

    def _increment_minutes(self):
        time = self.get_time()
        new_hour = time.Hour
        new_minute = time.Minute + 1
        if new_minute > 59:
            new_minute = 0
            new_hour = time.Hour + 1
            if new_hour > 23:
                new_hour = 0
        time.SetHour(new_hour)
        time.SetMinute(new_minute)
        return time

    def _decrement_hour(self):
        time = self.get_time()
        new_hour = time.Hour - 1
        if new_hour < 0:
            new_hour = 23
        time.SetHour(new_hour)
        return time

    def _decrement_minutes(self):
        time = self.get_time()
        new_hour = time.Hour
        new_minute = time.Minute - 1
        if new_minute < 0:
            new_minute = 59
            new_hour = time.Hour - 1
            if new_hour < 0:
                new_hour = 23
        time.SetHour(new_hour)
        time.SetMinute(new_minute)
        return time

    def _set_new_time_and_restore_selection(self, new_time):
        def restore_selection(selection):
            self.wx_time_picker.SetSelection(selection[0], selection[1])
        selection = self.wx_time_picker.GetSelection()
        self.set_time(new_time)
        restore_selection(selection)

    def _time_is_valid(self):
        try:
            self.get_time()
        except ValueError:
            return False
        return True

    def _select_part(self, part):
        if self._separator_pos() == -1:
            return
        if part == self.hour_part:
            self.wx_time_picker.SetSelection(0, self._separator_pos())
        else:
            time_string_len = len(self.wx_time_picker.get_time_string())
            self.wx_time_picker.SetSelection(self._separator_pos() + 1, time_string_len)
        self.preferred_part = part

    def _in_hour_part(self):
        if self._separator_pos() == -1:
            return
        return self.wx_time_picker.GetInsertionPoint() <= self._separator_pos()

    def _in_minute_part(self):
        if self._separator_pos() == -1:
            return
        return self.wx_time_picker.GetInsertionPoint() > self._separator_pos()

    def _separator_pos(self):
        return self.wx_time_picker.get_time_string().find(self.separator)
