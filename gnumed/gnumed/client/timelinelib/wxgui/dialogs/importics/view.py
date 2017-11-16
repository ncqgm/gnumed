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

from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.dialogs.importics.controller import ImportIcsDialogController


class ImportIcsDialog(Dialog):
    """
    <BoxSizerVertical>
        <StaticText
            name="VeventLocation"
            label="VEVENT.LOCATION"
            border="LEFT|TOP"
        />
        <CheckBox
            name="import_location"
            label="$(import_location_label)"
            border="ALL"
        />
        <StaticText
            name="ValarmTrigger"
            label="VALARM.TRIGGER"
            border="LEFT|TOP"
        />
        <CheckBox
            name ="trigger_as_start_time"
            label="$(trigger_as_start_time_label)"
            border="ALL"
        />
        <CheckBox
            name="trigger_as_alarm"
            label="$(trigger_as_alarm)"
            border="LEFT|BOTTOM"
        />
        <DialogButtonsCloseSizer
            border="ALL"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent=None):
        Dialog.__init__(self, ImportIcsDialogController, parent, {
            "import_location_label": _("Import in event description"),
            "trigger_as_start_time_label": _("Use as start date of event"),
            "trigger_as_alarm": _("Use as event alarm time"),
        }, title=_("Options for ICS import"))
        self.controller.on_init()
        self._make_static_texts_bold()

    def get_import_location(self):
        return self.import_location.GetValue()

    def get_trigger_as_start_time(self):
        return self.trigger_as_start_time.GetValue()

    def get_trigger_as_alarm(self):
        return self.trigger_as_alarm.GetValue()

    def _make_static_texts_bold(self):
        f = self.VeventLocation.GetFont()
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        self.VeventLocation.SetFont(f)
        self.ValarmTrigger.SetFont(f)
