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


WARNING_BG_COLOR = (251, 100, 100)
INFO_BG_COLOR = ((251, 203, 58))


class MessageBar(wx.Panel):

    """
    This class is used to create (or hide) a message text displayed
    at the top of the Timeline window.
    A message comes in two flavors:
       - Information message
       - Warning message
    What distinguishes the two flavors is the background color of the
    message text area.
    """

    def __init__(self, parent, name=None):
        """The name parameter is needed for testing purposes."""
        wx.Panel.__init__(self, parent, style=wx.BORDER_NONE)
        self._create_gui()

    def ShowWarningMessage(self, message):
        self._show_message(message, WARNING_BG_COLOR)

    def ShowInformationMessage(self, message):
        self._show_message(message, INFO_BG_COLOR)

    def ShowNoMessage(self):
        self.Hide()
        self.GetParent().Layout()

    def _create_gui(self):
        self._inner_panel = wx.Panel(self)
        self._label = wx.StaticText(self._inner_panel, style=wx.ALIGN_CENTRE_HORIZONTAL)
        self._add_with_border(self, self._inner_panel, 2, style=wx.EXPAND)
        self._add_with_border(self._inner_panel, self._label, 5, style=wx.ALIGN_CENTER)

    def _add_with_border(self, parent, child, border, style=0):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(child, proportion=1, flag=wx.ALL | style, border=border)
        parent.SetSizer(sizer)

    def _show_message(self, message, color):
        self._set_colour(color)
        self._set_message(message)
        self._repaint_window()

    def _set_colour(self, colour):
        self.SetBackgroundColour(darken_color(colour))
        self._inner_panel.SetBackgroundColour(colour)

    def _set_message(self, message):
        self._label.SetLabel(message)

    def _repaint_window(self):
        self.Refresh()
        self.Show()
        self.GetParent().Layout()
