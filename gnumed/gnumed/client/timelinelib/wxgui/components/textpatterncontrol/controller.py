# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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


class TextPatternControlController(humblewx.Controller):

    def on_init(self):
        self.separators = []
        self.last_selected_group = None
        self.validator = None
        self.up_handlers = {}
        self.down_handlers = {}

    def on_after_set_focus(self):
        if self.view.GetSelection() != (0, len(self.view.GetValue())):
            return
        elif self.last_selected_group is None:
            self._select_group(self.get_selected_group())
        else:
            self._select_group(self.last_selected_group)

    def on_kill_focus(self, event):
        self.last_selected_group = self.get_selected_group()
        self.view.SetSelection(0, 0)

    def on_text(self, event):
        self.validate()

    def on_char(self, event):
        skip = True
        if event.GetKeyCode() == wx.WXK_TAB:
            if event.ShiftDown():
                skip = self.on_shift_tab()
                flag = wx.NavigationKeyEvent.IsBackward
            else:
                skip = self.on_tab()
                flag = wx.NavigationKeyEvent.IsForward
            if skip:
                event.EventObject.Navigate(flags=flag)
            skip = False
        elif (event.GetKeyCode() == wx.WXK_UP and
              self.view.GetSelectedGroup() in self.up_handlers and
              self._is_text_valid()):
            self.up_handlers[self.view.GetSelectedGroup()]()
            skip = False
        elif (event.GetKeyCode() == wx.WXK_DOWN and
              self.view.GetSelectedGroup() in self.down_handlers and
              self._is_text_valid()):
            self.down_handlers[self.view.GetSelectedGroup()]()
            skip = False
        event.Skip(skip)

    def on_tab(self):
        return not self._select_group(self.get_selected_group() + 1)

    def on_shift_tab(self):
        return not self._select_group(self.get_selected_group() - 1)

    def get_parts(self):
        if self._get_groups() is not None:
            return [value for (value, _, _) in self._get_groups()]
        return None

    def get_selected_group(self):
        (selection_start, _) = self.view.GetSelection()
        if self._get_groups() is not None:
            for (index, (_, start, end)) in enumerate(self._get_groups()):
                if selection_start >= start and selection_start <= end:
                    return index
        return 0

    def set_separators(self, separators):
        self.separators = separators
        self.validate()

    def set_parts(self, parts):
        (start, end) = self.view.GetSelection()
        text = ""
        for (index, value) in enumerate(parts):
            if index > 0:
                text += self.separators[index-1]
            text += value
        self.view.SetValue(text)
        self.validate()
        self.view.SetSelection(start, end)

    def set_validator(self, validator):
        self.validator = validator
        self.validate()

    def set_up_handler(self, group, up_handler):
        self.up_handlers[group] = up_handler

    def set_down_handler(self, group, down_handler):
        self.down_handlers[group] = down_handler

    def validate(self):
        if self._is_text_valid():
            self.view.SetBackgroundColour(wx.NullColour)
        else:
            self.view.SetBackgroundColour("pink")
        self.view.Refresh()

    def _get_groups(self):
        text = self.view.GetValue()
        groups = []
        start = 0
        for separator in self.separators:
            separator_pos = text[start:].find(separator)
            if separator_pos == -1:
                return None
            groups.append(self._extract_section(start, start+separator_pos))
            start += separator_pos + len(separator)
        groups.append(self._extract_section(start, len(text)))
        return groups

    def _extract_section(self, start, end):
        return (self.view.GetValue()[start:end], start, end)

    def _is_text_valid(self):
        if self.get_parts() is None:
            return False
        elif self.validator is None:
            return True
        else:
            return self.validator()

    def _select_group(self, section_to_focus):
        if self._get_groups() is not None:
            for (index, (_, start, end)) in enumerate(self._get_groups()):
                if index == section_to_focus:
                    self.view.SetSelection(start, end)
                    return True
        return False
