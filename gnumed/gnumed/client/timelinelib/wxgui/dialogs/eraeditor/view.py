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


from timelinelib.wxgui.dialogs.eraeditor.controller import EraEditorDialogController
from timelinelib.wxgui.framework import Dialog


class EraEditorDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticBoxSizerVertical label="$(groupbox_text)" border="ALL" >
            <FlexGridSizer rows="0" columns="2" border="ALL">
                <StaticText
                    label="$(when_text)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <PeriodPicker
                    time_type="$(time_type)"
                    config="$(config)"
                    name="period_picker"
                />
                <Spacer />
                <BoxSizerHorizontal >
                    <CheckBox
                        align="ALIGN_CENTER_VERTICAL"
                        label="$(ends_today_text)"
                        name="cbx_ends_today"
                    />
                </BoxSizerHorizontal>
                <StaticText
                    label="$(name_text)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <TextCtrl name="txt_name" />
                <StaticText
                    label="$(colour_text)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <ColourSelect
                    name="colorpicker"
                    align="ALIGN_CENTER_VERTICAL"
                    width="60"
                    height="30"
                />
            </FlexGridSizer>
        </StaticBoxSizerVertical>
        <DialogButtonsOkCancelSizer
            border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_OK="on_ok"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, title, time_type, config, era):
        Dialog.__init__(self, EraEditorDialogController, parent, {
            "groupbox_text": _("Era Properties"),
            "name_text": _("Name:"),
            "colour_text": _("Colour:"),
            "when_text": _("When:"),
            "time_type": time_type,
            "config": config,
            "ends_today_text":  _("Ends today"),
        }, title=title)
        self.controller.on_init(era)
        self.period_picker.SetFocus()

    def GetPeriod(self):
        return self.period_picker.GetValue()

    def SetPeriod(self, time_period):
        self.period_picker.SetValue(time_period)

    def GetEndsToday(self):
        return self.cbx_ends_today.IsChecked()

    def SetEndsToday(self, value):
        self.cbx_ends_today.SetValue(value)

    def GetName(self):
        return self.txt_name.GetValue()

    def SetName(self, name):
        self.txt_name.SetValue(name)

    def GetColor(self):
        return self.colorpicker.GetValue()

    def SetColor(self, new_color):
        self.colorpicker.SetValue(new_color)

    def DisplayInvalidPeriod(self, message):
        self.DisplayErrorMessage(message, focus_widget=self.period_picker)

    def DisplayInvalidName(self, message):
        self.DisplayErrorMessage(message, focus_widget=self.txt_name)

    def DisplayInvalidColor(self, message):
        self.DisplayErrorMessage(message, focus_widget=self.colorpicker)
