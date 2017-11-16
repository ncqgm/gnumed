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


from timelinelib.wxgui.dialogs.changenowdate.controller import ChangeNowDateDialogController
from timelinelib.wxgui.framework import Dialog


class ChangeNowDateDialog(Dialog):

    """
    <BoxSizerVertical>
        <CheckBox
            name="show_time_checkbox"
            label="$(show_time_text)"
            event_EVT_CHECKBOX="on_show_time_changed"
            border="LEFT|TOP|RIGHT"
        />
        <TimePicker
            name="time_picker"
            time_type="$(time_type)"
            config="$(config)"
            on_change="$(time_picker_on_change)"
            border="LEFT|BOTTOM|RIGHT"
        />
        <DialogButtonsCloseSizer
            border="LEFT|BOTTOM|RIGHT"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, config, db, handle_new_time_fn, title):
        Dialog.__init__(self, ChangeNowDateDialogController, parent, {
            "show_time_text": _("Show time"),
            "time_type": db.get_time_type(),
            "config": config,
            "time_picker_on_change": self._time_picker_on_change,
        }, title=title)
        self.controller.on_init(db, handle_new_time_fn)

    def GetNowValue(self):
        return self.time_picker.get_value()

    def SetNowValue(self, value):
        self.time_picker.set_value(value)

    def ShowTime(self, value):
        self.time_picker.show_time(value)

    def IsShowTimeChecked(self):
        return self.show_time_checkbox.GetValue()

    def FocusTimePicker(self):
        self.time_picker.SetFocus()

    def _time_picker_on_change(self):
        self.controller.on_time_changed()
