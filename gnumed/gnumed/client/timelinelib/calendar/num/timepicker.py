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

from timelinelib.calendar.num.time import NumTime
from timelinelib.wxgui.components.numctrl import NumCtrl


class NumTimePicker(wx.Panel):

    def __init__(self, parent, show_time=False, config=None, on_change=None):
        wx.Panel.__init__(self, parent)
        self.time_picker = self._create_gui()

    def get_value(self):
        return NumTime(int(self.time_picker.GetValue()))

    def set_value(self, num_time):
        if num_time is None:
            self.time_picker.SetValue('0')
        else:
            self.time_picker.SetValue(str(int(num_time.value)))

    def select_all(self):
        self.time_picker.SetSelection(0, len(str(self.get_value())))

    def _create_gui(self):
        time_picker = NumCtrl(self, size=(300, -1))
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(time_picker, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)
        return time_picker
