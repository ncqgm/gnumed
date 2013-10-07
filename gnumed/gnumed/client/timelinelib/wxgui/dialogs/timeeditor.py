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


import wx

from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import time_picker_for
from timelinelib.utils import ex_msg
import timelinelib.calendar.gregorian as gregorian


class TimeEditorDialog(wx.Dialog):

    def __init__(self, parent, config, time_type, time, title):
        wx.Dialog.__init__(self, parent, title=title)
        self.time_type = time_type
        self.config = config
        self._create_gui()
        self.time_picker.set_value(time)
        if self._should_display_show_time_checkbox():
            self.time_picker.show_time(self.checkbox.IsChecked())
        self.time_picker.SetFocus()

    def _create_gui(self):
        self._create_show_time_checkbox()
        self._create_time_picker()
        self._create_buttons()
        self._layout_components()

    def _create_show_time_checkbox(self):
        if self._should_display_show_time_checkbox():
            self.checkbox = wx.CheckBox(self, label=_("Show time"))
            self.checkbox.SetValue(False)
            self.Bind(wx.EVT_CHECKBOX, self._show_time_checkbox_on_checked, self.checkbox)

    def _show_time_checkbox_on_checked(self, e):
        self.time_picker.show_time(e.IsChecked())

    def _create_time_picker(self):
        self.time_picker = time_picker_for(self.time_type)(self, config=self.config)

    def _create_buttons(self):
        self.button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._ok_button_on_click, id=wx.ID_OK)

    def _ok_button_on_click(self, e):
        self.on_return()

    def on_return(self):
        try:
            self.time = self.time_picker.get_value()
            if not self.checkbox.IsChecked():
                gt = gregorian.from_time(self.time)
                gt.hour = 12
                self.time = gt.to_time()
        except ValueError, ex:
            display_error_message(ex_msg(ex))
        else:
            self.EndModal(wx.ID_OK)
        
    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        if self._should_display_show_time_checkbox():
            vbox.Add(self.checkbox, flag=wx.LEFT|wx.TOP|wx.RIGHT,
                     border=BORDER, proportion=1)
        if self._should_display_show_time_checkbox():
            flag = wx.EXPAND|wx.RIGHT|wx.BOTTOM|wx.LEFT
        else:
            flag = wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.LEFT
        vbox.Add(self.time_picker, flag=flag,
                 border=BORDER, proportion=1)
        vbox.Add(self.button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def _should_display_show_time_checkbox(self):
        return self.time_type.is_date_time_type()
