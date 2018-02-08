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


from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.dialogs.dateformat.controller import DateFormatDialogController


class DateFormatDialog(Dialog):

    """
    <BoxSizerVertical>
        <FlexGridSizer name="grid" rows="0" columns="2" border="ALL" >
            <StaticText
                align="ALIGN_CENTER_VERTICAL"
                label="$(date_format_text)"
            />
            <TextCtrl name="date_format" fit_text="__YYYY__MMM__DD__" />
            <StaticText
                align="ALIGN_CENTER_VERTICAL"
                label="$(locale_date_format_text)"
            />
            <StaticText
                align="ALIGN_CENTER_VERTICAL"
                name="locale_date_format"
            />
        </FlexGridSizer>
        <BoxSizerHorizontal>
            <StretchSpacer/>
            <DialogButtonsOkCancelSizer
                border="ALL"
                event_EVT_BUTTON__ID_OK="on_ok"
            />
        </BoxSizerHorizontal>
    </BoxSizerVertical>
    """

    def __init__(self, parent, config):
        Dialog.__init__(self, DateFormatDialogController, parent, {
            "date_format_text": _("Date format:"),
            "locale_date_format_text": _("Locale Date format:"),
        }, title=_("Set Date format"))
        self.controller.on_init(config)

    def SetDateFormat(self, value):
        self.date_format.SetValue(value)

    def GetDateFormat(self):
        return self.date_format.GetValue()

    def SetLocaleDateFormat(self, value):
        self.locale_date_format.SetLabel(value)

    def DisplayErrorMessage(self, message):
        Dialog.DisplayErrorMessage(self, message)
        self.date_format.SetFocus()
