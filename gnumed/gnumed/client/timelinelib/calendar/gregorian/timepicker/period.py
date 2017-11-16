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


from timelinelib.calendar.gregorian.timetype import GregorianTimeType
from timelinelib.calendar.gregorian.timetype import has_nonzero_time
from timelinelib.canvas.data import TimePeriod
from timelinelib.wxgui.framework import Controller
from timelinelib.wxgui.framework import Panel


class GregorianPeriodPicker(Panel):

    """
    <BoxSizerVertical>
        <BoxSizerHorizontal>
            <TimePicker
                name="start_time"
                time_type="$(time_type)"
                config="$(config)"
            />
            <Spacer />
            <StaticText
                label="$(to_label)"
                name="to_label"
                align="ALIGN_CENTER_VERTICAL"
            />
            <Spacer />
            <TimePicker
                name="end_time"
                time_type="$(time_type)"
                config="$(config)"
            />
        </BoxSizerHorizontal>
        <Spacer />
        <BoxSizerHorizontal>
            <CheckBox
                name="period_checkbox"
                event_EVT_CHECKBOX="on_period_checkbox_changed"
                label="$(period_checkbox_text)" />
            <CheckBox
                name="show_time_checkbox"
                event_EVT_CHECKBOX="on_show_time_checkbox_changed"
                label="$(show_time_checkbox_text)"
            />
        </BoxSizerHorizontal>
    </BoxSizerVertical>
    """

    def __init__(self, parent, config, name=None):
        Panel.__init__(self, GregorianPeriodPickerController, parent, {
            "time_type": GregorianTimeType(),
            "config": config,
            "to_label": _("to"),
            "period_checkbox_text": _("Period"),
            "show_time_checkbox_text": _("Show time"),
        })

    def GetValue(self):
        return self.controller.get_value()

    def SetValue(self, time_period):
        self.controller.set_value(time_period)

    def GetStartValue(self):
        return self.start_time.get_value()

    def SetStartValue(self, time):
        self.start_time.set_value(time)

    def GetEndValue(self):
        return self.end_time.get_value()

    def SetEndValue(self, time):
        self.end_time.set_value(time)

    def GetShowPeriod(self):
        return self.period_checkbox.GetValue()

    def SetShowPeriod(self, show):
        self.period_checkbox.SetValue(show)
        self.to_label.Show(show)
        self.end_time.Show(show)
        self.Layout()

    def GetShowTime(self):
        return self.show_time_checkbox.GetValue()

    def SetShowTime(self, show):
        self.show_time_checkbox.SetValue(show)
        self.start_time.show_time(show)
        self.end_time.show_time(show)

    def DisableTime(self):
        self.SetShowTime(False)
        self.show_time_checkbox.Disable()


class GregorianPeriodPickerController(Controller):

    def get_value(self):
        return TimePeriod(self._get_start(), self._get_end())

    def set_value(self, time_period):
        self.view.SetStartValue(time_period.get_start_time())
        self.view.SetEndValue(time_period.get_end_time())
        self.view.SetShowPeriod(time_period.is_period())
        self.view.SetShowTime(has_nonzero_time(time_period))

    def on_period_checkbox_changed(self, event):
        self.view.SetShowPeriod(event.IsChecked())

    def on_show_time_checkbox_changed(self, event):
        self.view.SetShowTime(event.IsChecked())

    def _get_start(self):
        return self.view.GetStartValue()

    def _get_end(self):
        if self.view.GetShowPeriod():
            return self.view.GetEndValue()
        else:
            return self._get_start()
