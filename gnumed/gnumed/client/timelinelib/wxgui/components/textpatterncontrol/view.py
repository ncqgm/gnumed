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


import wx

from timelinelib.wxgui.components.textctrl import TextCtrl
from timelinelib.wxgui.components.textpatterncontrol.controller import TextPatternControlController


class TextPatternControl(TextCtrl):

    def __init__(self, parent, name=None, fit_text=None):
        TextCtrl.__init__(
            self,
            parent,
            style=wx.TE_PROCESS_TAB,
            fit_text=fit_text
        )
        self.controller = TextPatternControlController(self)
        self._bind_events()
        self.controller.on_init()

    def GetParts(self):
        return self.controller.get_parts()

    def GetSelectedGroup(self):
        return self.controller.get_selected_group()

    def SetSeparators(self, separators):
        self.controller.set_separators(separators)

    def SetParts(self, parts):
        self.controller.set_parts(parts)

    def SetValidator(self, validator):
        self.controller.set_validator(validator)

    def SetUpHandler(self, group, up_handler):
        self.controller.set_up_handler(group, up_handler)

    def SetDownHandler(self, group, down_handler):
        self.controller.set_down_handler(group, down_handler)

    def Validate(self):
        self.controller.validate()

    def _bind_events(self):
        self.Bind(wx.EVT_CHAR, self.controller.on_char)
        self.Bind(wx.EVT_TEXT, self.controller.on_text)
        self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.controller.on_kill_focus)

    def _on_set_focus(self, event):
        wx.CallAfter(self.controller.on_after_set_focus)
        event.Skip()
