# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
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


import wx

from timelinelib.calendar.bosparanian.bosparanian import BosparanianDateTime, is_valid_time
from timelinelib.calendar.bosparanian.dateformatter import BosparanianDateFormatter
from timelinelib.calendar.bosparanian.time import BosparanianDelta
from timelinelib.calendar.bosparanian.timetype import BosparanianTimeType


class BosparanianDateTimePicker(wx.Panel):

    def __init__(self, parent, show_time=True, config=None, on_change=None):
        wx.Panel.__init__(self, parent)
        self.config = config
        self._create_gui(on_change)
        self.controller = BosparanianDateTimePickerController(
            self.date_picker, self.time_picker, BosparanianTimeType().now)
        self.show_time(show_time)
        self.parent = parent

    def on_return(self):
        try:
            self.parent.on_return()
        except AttributeError:
            pass

    def on_escape(self):
        try:
            self.parent.on_escape()
        except AttributeError:
            pass

    def show_time(self, show=True):
        self.time_picker.Show(show)
        self.GetSizer().Layout()

    def get_value(self):
        try:
            return self.controller.get_value()
        except ValueError:
            pass

    def set_value(self, value):
        self.controller.set_value(value)

    def _create_gui(self, on_change):
        self.date_picker = BosparanianDatePicker(self, on_change)
        self.time_picker = BosparanianTimePicker(self, on_change)
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.date_picker, proportion=1,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.time_picker, proportion=0,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)


class BosparanianDateTimePickerController(object):

    def __init__(self, date_picker, time_picker, now_fn):
        self.date_picker = date_picker
        self.time_picker = time_picker
        self.now_fn = now_fn

    def get_value(self):
        if self.time_picker.IsShown():
            hour, minute, second = self.time_picker.get_value()
        else:
            hour, minute, second = (0, 0, 0)
        year, month, day = self.date_picker.get_value()
        return BosparanianDateTime(year, month, day, hour, minute, second).to_time()

    def set_value(self, time):
        if time is None:
            time = self.now_fn()
        self.date_picker.set_value(BosparanianDateTime.from_time(time).to_date_tuple())
        self.time_picker.set_value(BosparanianDateTime.from_time(time).to_time_tuple())


class BosparanianDatePicker(wx.TextCtrl):

    def __init__(self, parent, on_change):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = BosparanianDatePickerController(self, on_change=on_change)
        self._bind_events()
        self._resize_to_fit_text()
        self.parent = parent

    def get_value(self):
        return self.controller.get_value()

    def set_value(self, date):
        self.controller.set_value(date)

    def get_date_string(self):
        return self.GetValue()

    def set_date_string(self, date_string):
        date_str, bc_year = date_string
        return self.SetValue(date_str)

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
            elif (evt.GetKeyCode() == wx.WXK_NUMPAD_ENTER or
                  evt.GetKeyCode() == wx.WXK_RETURN):
                self.parent.on_return()
            elif (evt.GetKeyCode() == wx.WXK_ESCAPE):
                self.parent.on_escape()
            else:
                evt.Skip()
        self.Bind(wx.EVT_KEY_DOWN, on_key_down)

    def _resize_to_fit_text(self):
        w, _ = self.GetTextExtent("0000BF-MMM-00")
        width = w + 20
        self.SetMinSize((width, -1))


class BosparanianDatePickerController(object):

    def __init__(self, date_picker, error_bg="pink", on_change=None):
        self.date_picker = date_picker
        self.error_bg = error_bg
        self.original_bg = self.date_picker.GetBackgroundColour()
        self.date_formatter = BosparanianDateFormatter()
        self.separator = self.date_formatter.separator()
        self.region_year, self.region_month, self.region_day = self.date_formatter.get_regions()
        self.region_siblings = ((self.region_year, self.region_month),
                                (self.region_month, self.region_day))
        self.preferred_day = None
        self.save_preferred_day = True
        self.last_selection = None
        self.on_change = on_change

    def get_value(self):
        try:
            (year, month, day) = self._parse_year_month_day()
            self._ensure_within_allowed_period((year, month, day))
            return (year, month, day)
        except ValueError:
            raise ValueError("Invalid date.")

    def set_value(self, value):
        year, month, day = value
        date_string = self.date_formatter.format(year, month, day)
        self.date_picker.set_date_string(date_string)
        self._on_change()

    def _on_change(self):
        if self._current_date_is_valid() and not self.on_change is None:
            self.on_change()

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.date_picker.SetSelection(start, end)
        else:
            self._select_region_if_possible(self.region_year)
            self.last_selection = self.date_picker.GetSelection()

    def on_kill_focus(self):
        if self.last_selection:
            self.last_selection = self.date_picker.GetSelection()

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
            current_date = self.get_value()
            # To prevent saving of preferred day when year or month is changed
            # in on_up() and on_down()...
            # Save preferred day only when text is entered in the date text
            # control and not when up or down keys has been used.
            # When up and down keys are used, the preferred day is saved in
            # on_up() and on_down() only when day is changed.
            if self.save_preferred_day:
                self._save_preferred_day(current_date)
            self._on_change()

    def on_up(self):
        max_year = BosparanianDateTime.from_time(BosparanianTimeType().get_max_time()).year
        def increment_year(date):
            year, month, day = date
            if year < max_year - 1:
                return self._set_valid_day(year + 1, month, day)
            return date
        def increment_month(date):
            year, month, day = date
            if month < 13:
                return self._set_valid_day(year, month + 1, day)
            elif year < max_year - 1:
                return self._set_valid_day(year + 1, 1, day)
            return date
        def increment_day(date):
            year, month, day = date
            time = BosparanianDateTime.from_ymd(year, month, day).to_time()
            if time < BosparanianTimeType().get_max_time() - BosparanianDelta.from_days(1):
                return BosparanianDateTime.from_time(time + BosparanianDelta.from_days(1)).to_date_tuple()
            return date
        if not self._current_date_is_valid():
            return
        selection = self.date_picker.GetSelection()
        current_date = self.get_value()
        if self._insertion_point_in_region(self.region_year):
            new_date = increment_year(current_date)
        elif self._insertion_point_in_region(self.region_month):
            new_date = increment_month(current_date)
        else:
            new_date = increment_day(current_date)
            self._save_preferred_day(new_date)
        if current_date != new_date:
            self._set_new_date_and_restore_selection(new_date, selection)
        self._on_change()

    def on_down(self):
        def decrement_year(date):
            year, month, day = date
            if year > BosparanianDateTime.from_time(BosparanianTimeType().get_min_time()).year:
                return self._set_valid_day(year - 1, month, day)
            return date
        def decrement_month(date):
            year, month, day = date
            if month > 1:
                return self._set_valid_day(year, month - 1, day)
            elif year > BosparanianDateTime.from_time(BosparanianTimeType().get_min_time()).year:
                return self._set_valid_day(year - 1, 13, day)
            return date
        def decrement_day(date):
            year, month, day = date
            if day > 1:
                return self._set_valid_day(year, month, day - 1)
            elif month > 1:
                return self._set_valid_day(year, month - 1, 30)
            elif year > BosparanianDateTime.from_time(BosparanianTimeType().get_min_time()).year:
                return self._set_valid_day(year - 1, 13, 5)
            return date
        if not self._current_date_is_valid():
            return
        selection = self.date_picker.GetSelection()
        current_date = self.get_value()
        if self._insertion_point_in_region(self.region_year):
            new_date = decrement_year(current_date)
        elif self._insertion_point_in_region(self.region_month):
            new_date = decrement_month(current_date)
        else:
            year, month, day = current_date
            BosparanianDateTime.from_ymd(year, month, day)
            if BosparanianDateTime.from_ymd(year, month, day).to_time() == BosparanianTimeType().get_min_time():
                return
            new_date = decrement_day(current_date)
            self._save_preferred_day(new_date)
        if current_date != new_date:
            self._set_new_date_and_restore_selection(new_date, selection)
        self._on_change()

    def _change_background_depending_on_date_validity(self):
        if self._current_date_is_valid():
            self.date_picker.SetBackgroundColour(self.original_bg)
        else:
            self.date_picker.SetBackgroundColour(self.error_bg)
        self.date_picker.SetFocus()
        self.date_picker.Refresh()

    def _parse_year_month_day(self):
        return self.date_formatter.parse(self.date_picker.get_date_string())

    def _ensure_within_allowed_period(self, date):
        year, month, day = date
        time = BosparanianDateTime(year, month, day, 0, 0, 0).to_time()
        if (time >= BosparanianTimeType().get_max_time() or
            time < BosparanianTimeType().get_min_time()):
            raise ValueError()

    def _set_new_date_and_restore_selection(self, new_date, selection):
        def restore_selection(selection):
            self.date_picker.SetSelection(selection[0], selection[1])
        self.save_preferred_day = False
        if self.preferred_day is not None:
            year, month, _ = new_date
            new_date = self._set_valid_day(year, month, self.preferred_day)
        self.set_value(new_date)
        restore_selection(selection)
        self.save_preferred_day = True

    def _set_valid_day(self, new_year, new_month, new_day):
        done = False
        while not done:
            try:
                date = BosparanianDateTime.from_ymd(new_year, new_month, new_day)
                done = True
            except Exception:
                new_day -= 1
        return date.to_date_tuple()

    def _save_preferred_day(self, date):
        _, _, day = date
        if day > 28:
            self.preferred_day = day
        else:
            self.preferred_day = None

    def _current_date_is_valid(self):
        try:
            self.get_value()
        except ValueError:
            return False
        return True

    def _select_region_if_possible(self, region):
        region_range = self._get_region_range(region)
        if region_range:
            self.date_picker.SetSelection(region_range[0], region_range[-1])

    def _insertion_point_in_region(self, n):
        region_range = self._get_region_range(n)
        if region_range:
            return self.date_picker.GetInsertionPoint() in region_range

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
        date = self.date_picker.get_date_string()
        if not date_has_exactly_two_seperators(date):
            return None
        pos_range = calculate_pos_range(n, date)
        return pos_range


class BosparanianTimePicker(wx.TextCtrl):

    def __init__(self, parent, on_change):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
        self.controller = BosparanianTimePickerController(self, on_change)
        self._bind_events()
        self._resize_to_fit_text()
        self.parent = parent

    def get_value(self):
        return self.controller.get_value()

    def set_value(self, value):
        self.controller.set_value(value)

    def _get_time_string(self):
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
            elif (evt.GetKeyCode() == wx.WXK_NUMPAD_ENTER or
                  evt.GetKeyCode() == wx.WXK_RETURN):
                self.parent.on_return()
            elif (evt.GetKeyCode() == wx.WXK_ESCAPE):
                self.parent.on_escape()
            else:
                evt.Skip()
        self.Bind(wx.EVT_KEY_DOWN, on_key_down)

    def _resize_to_fit_text(self):
        w, _ = self.GetTextExtent("00:00")
        width = w + 20
        self.SetMinSize((width, -1))


class BosparanianTimePickerController(object):

    def __init__(self, time_picker, on_change):
        self.time_picker = time_picker
        self.original_bg = self.time_picker.GetBackgroundColour()
        self.separator = ":"
        self.hour_part = 0
        self.minute_part = 1
        self.last_selection = None
        self.on_change = on_change

    def get_value(self):
        try:
            split = self.time_picker._get_time_string().split(self.separator)
            if len(split) != 2:
                raise ValueError()
            hour_string, minute_string = split
            hour = int(hour_string)
            minute = int(minute_string)
            if not is_valid_time(hour, minute, 0):
                raise ValueError()
            return (hour, minute, 0)
        except ValueError:
            raise ValueError("Invalid time.")

    def set_value(self, value):
        hour, minute, _ = value
        time_string = "%02d:%02d" % (hour, minute)
        self.time_picker.set_time_string(time_string)
        self._on_change()

    def _on_change(self):
        if self._time_is_valid() and not self.on_change is None:
            self.on_change()

    def on_set_focus(self):
        if self.last_selection:
            start, end = self.last_selection
            self.time_picker.SetSelection(start, end)
        else:
            self._select_part(self.hour_part)

    def on_kill_focus(self):
        self.last_selection = self.time_picker.GetSelection()

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
            self.get_value()
            self.time_picker.SetBackgroundColour(self.original_bg)
        except ValueError:
            self.time_picker.SetBackgroundColour("pink")
        self.time_picker.Refresh()

    def on_up(self):
        def increment_hour(time):
            hour, minute, second = time
            new_hour = hour + 1
            if new_hour > 23:
                new_hour = 0
            return (new_hour, minute, second)
        def increment_minutes(time):
            hour, minute, second = time
            new_hour = hour
            new_minute = minute + 1
            if new_minute > 59:
                new_minute = 0
                new_hour = hour + 1
                if new_hour > 23:
                    new_hour = 0
            return (new_hour, new_minute, second)
        if not self._time_is_valid():
            return
        selection = self.time_picker.GetSelection()
        current_time = self.get_value()
        if self._in_hour_part():
            new_time = increment_hour(current_time)
        else:
            new_time = increment_minutes(current_time)
        if current_time != new_time:
            self._set_new_time_and_restore_selection(new_time, selection)
        self._on_change()

    def on_down(self):
        def decrement_hour(time):
            hour, minute, second = time
            new_hour = hour - 1
            if new_hour < 0:
                new_hour = 23
            return (new_hour, minute, second)
        def decrement_minutes(time):
            hour, minute, second = time
            new_hour = hour
            new_minute = minute - 1
            if new_minute < 0:
                new_minute = 59
                new_hour = hour - 1
                if new_hour < 0:
                    new_hour = 23
            return (new_hour, new_minute, second)
        if not self._time_is_valid():
            return
        selection = self.time_picker.GetSelection()
        current_time = self.get_value()
        if self._in_hour_part():
            new_time = decrement_hour(current_time)
        else:
            new_time = decrement_minutes(current_time)
        if current_time != new_time:
            self._set_new_time_and_restore_selection(new_time, selection)
        self._on_change()

    def _set_new_time_and_restore_selection(self, new_time, selection):
        def restore_selection(selection):
            self.time_picker.SetSelection(selection[0], selection[1])
        self.set_value(new_time)
        restore_selection(selection)

    def _time_is_valid(self):
        try:
            self.get_value()
        except ValueError:
            return False
        return True

    def _select_part(self, part):
        if self._separator_pos() == -1:
            return
        if part == self.hour_part:
            self.time_picker.SetSelection(0, self._separator_pos())
        else:
            time_string_len = len(self.time_picker._get_time_string())
            self.time_picker.SetSelection(self._separator_pos() + 1, time_string_len)
        self.preferred_part = part

    def _in_hour_part(self):
        if self._separator_pos() == -1:
            return
        return self.time_picker.GetInsertionPoint() <= self._separator_pos()

    def _in_minute_part(self):
        if self._separator_pos() == -1:
            return
        return self.time_picker.GetInsertionPoint() > self._separator_pos()

    def _separator_pos(self):
        return self.time_picker._get_time_string().find(self.separator)
