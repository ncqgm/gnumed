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


class TwoStateButton(wx.Button):

    InitialStateClickedEvent, EVT_INITIAL_STATE_CLICKED = wx.lib.newevent.NewEvent()
    SecondStateClickedEvent, EVT_SECOND_STATE_CLICKED = wx.lib.newevent.NewEvent()

    def __init__(self, parent, initial_state_label, second_state_label, *args, **kwargs):
        wx.Button.__init__(self, parent, label=initial_state_label, *args, **kwargs)
        self.initial_state_label = initial_state_label
        self.second_state_label = second_state_label
        self.Bind(wx.EVT_BUTTON, self._on_click)

    def _on_click(self, event):
        if self.GetLabel() == self.initial_state_label:
            wx.PostEvent(self, self.InitialStateClickedEvent())
            self.SetLabel(self.second_state_label)
        elif self.GetLabel() == self.second_state_label:
            wx.PostEvent(self, self.SecondStateClickedEvent())
            self.SetLabel(self.initial_state_label)
