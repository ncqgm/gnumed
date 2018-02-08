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


import humblewx
import wx


class GregorianDatePickerController(humblewx.Controller):

    def on_init(self, date_formatter, date_modifier):
        self._date_formatter = date_formatter
        self._date_modifier = date_modifier

    def on_text(self, event):
        self._validate()

    def on_char(self, event):
        skip = True
        if event.GetKeyCode() == wx.WXK_TAB:
            if event.ShiftDown():
                tab_handled = self.on_shift_tab()
            else:
                tab_handled = self.on_tab()
            skip = not tab_handled
        elif event.GetKeyCode() == wx.WXK_UP:
            self.on_key_up()
            skip = False
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.on_key_down()
            skip = False
        event.Skip(skip)

    def _validate(self):
        try:
            self.get_gregorian_date()
        except ValueError:
            self.view.SetBackgroundColour("pink")
        else:
            self.view.SetBackgroundColour(wx.NullColour)

    def on_tab(self):
        return self._select_region(self._date_formatter.get_next_region)

    def on_shift_tab(self):
        return self._select_region(self._date_formatter.get_previous_region)

    def _select_region(self, get_region_fn):
        region = get_region_fn(
            self.view.GetText(),
            self.view.GetCursorPosition()
        )
        if region is None:
            return False
        else:
            self.view.SetSelection(region)
            return True

    def on_key_up(self):
        try:
            date = self.get_gregorian_date()
        except ValueError:
            pass
        else:
            self.set_gregorian_date(self._get_incrementer()(date))

    def on_key_down(self):
        try:
            date = self.get_gregorian_date()
        except ValueError:
            pass
        else:
            self.set_gregorian_date(self._get_decrementer()(date))

    def set_gregorian_date(self, date):
        (formatted_date, is_bc) = self._date_formatter.format(date)
        self.view.SetText(formatted_date)
        self.view.SetIsBc(is_bc)

    def get_gregorian_date(self):
        return self._date_formatter.parse((
            self.view.GetText(),
            self.view.GetIsBc(),
        ))

    def _get_incrementer(self):
        return {
            self._date_formatter.YEAR: self._date_modifier.increment_year,
            self._date_formatter.MONTH: self._date_modifier.increment_month,
            self._date_formatter.DAY: self._date_modifier.increment_day,
        }[self._get_region_type()]

    def _get_decrementer(self):
        return {
            self._date_formatter.YEAR: self._date_modifier.decrement_year,
            self._date_formatter.MONTH: self._date_modifier.decrement_month,
            self._date_formatter.DAY: self._date_modifier.decrement_day,
        }[self._get_region_type()]

    def _get_region_type(self):
        return self._date_formatter.get_region_type(
            self.view.GetText(),
            self.view.GetCursorPosition()
        )
