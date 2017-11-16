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

from timelinelib.canvas.drawing.utils import darken_color


class MessageBar(wx.Panel):

    def __init__(self, parent, name=None):
        wx.Panel.__init__(self, parent, style=wx.BORDER_NONE)
        self._create_gui()

    def _create_gui(self):
        self._inner_panel = wx.Panel(self)
        self._label = wx.StaticText(self._inner_panel,
                                    style=wx.ALIGN_CENTRE_HORIZONTAL)
        self._add_with_border(self, self._inner_panel, 2,
                              style=wx.EXPAND)
        self._add_with_border(self._inner_panel, self._label, 5,
                              style=wx.ALIGN_CENTER)

    def _add_with_border(self, parent, child, border, style=0):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(child, proportion=1, flag=wx.ALL | style, border=border)
        parent.SetSizer(sizer)

    def ShowWarningMessage(self, message):
        self._set_colour((251, 100, 100))
        self._label.SetLabel(message)
        self._show()
        self.GetParent().Layout()

    def ShowInformationMessage(self, message):
        self._set_colour((251, 203, 58))
        self._label.SetLabel(message)
        self._show()
        self.GetParent().Layout()

    def ShowNoMessage(self):
        self.Hide()
        self.GetParent().Layout()

    def _show(self):
        self.Refresh()
        self.Show()

    def _set_colour(self, colour):
        self.SetBackgroundColour(darken_color(colour))
        self._inner_panel.SetBackgroundColour(colour)
