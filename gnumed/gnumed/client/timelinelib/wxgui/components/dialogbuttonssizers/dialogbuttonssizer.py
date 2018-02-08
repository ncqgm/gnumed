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

from timelinelib.wxgui.framework import SMALL_BORDER


class DialogButtonsSizer(wx.BoxSizer):

    def __init__(self, parent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

    def AddButtons(self, buttons, default):
        self.AddStretchSpacer()
        for (index, button) in enumerate(buttons):
            if index == 0:
                border = 0
            else:
                border = wx.LEFT
            self.Add(button, 0, border | wx.EXPAND, SMALL_BORDER)
        if default is not None:
            buttons[default].SetDefault()
