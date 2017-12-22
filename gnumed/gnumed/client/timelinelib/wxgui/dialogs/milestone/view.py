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
from timelinelib.wxgui.dialogs.milestone.controller import EditMilestoneDialogController
from timelinelib.db.utils import safe_locking


class EditMilestoneDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticBoxSizerVertical label="$(groupbox_text)" border="ALL" >
            <FlexGridSizer rows="0" columns="2" border="ALL">
                <StaticText
                    label="$(when_text)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <TimePicker
                    time_type="$(time_type)"
                    config="$(config)"
                    name="dtp_time"
                />
                <StaticText
                    label="$(description_text)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <TextCtrl name="txt_description" />
                <StaticText
                    label="$(description_label)"
                    align="ALIGN_CENTER_VERTICAL"
                />
                <TextCtrl name="txt_label" />
                <StaticText
                    align="ALIGN_CENTER_VERTICAL"
                    label="$(category_label)"
                />
                <CategoryChoice
                    name="category_choice"
                    allow_add="True"
                    allow_edit="True"
                    timeline="$(db)"
                    align="ALIGN_LEFT"
                />
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
            border="LEFT|BOTTOM|RIGHT"
            event_EVT_BUTTON__ID_OK="on_ok_clicked"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, title, db, config, milestone):
        Dialog.__init__(self, EditMilestoneDialogController, parent, {
            "groupbox_text": _("Milestone Properties"),
            "when_text": _("When:"),
            "time_type": db.time_type,
            "description_text": _("Description:"),
            "description_label": _("Label:"),
            "category_label": _("Category:"),
            "colour_text": _("Colour:"),
            "config": config,
            "db": db,
        }, title=title)
        self.controller.on_init(db, milestone)
        self._milestone = milestone
        self.txt_label.Bind(wx.EVT_CHAR, self.handle_keypress)

    def GetTime(self):
        return self.dtp_time.get_value()

    def SetTime(self, start_time):
        self.dtp_time.set_value(start_time)

    def GetDescription(self):
        return self.txt_description.GetValue()

    def SetDescription(self, description):
        if description is None:
            self.txt_description.SetValue("")
        else:
            self.txt_description.SetValue(description)

    def GetLabel(self):
        return self.txt_label.GetValue()

    def SetLable(self, label):
        self.txt_label.SetValue(label)

    def GetCategory(self):
        return self.category_choice.GetSelectedCategory()

    def SetCategory(self, value):
        self.category_choice.Populate(select=value)

    def GetColour(self):
        return self.colorpicker.GetValue()

    def SetColor(self, color):
        self.colorpicker.SetValue(color)

    def handle_keypress(self, evt):
        self.txt_label.Clear()
        evt.Skip()


def open_milestone_editor_for(edit_controller, parent, config, db, event=None):

    def create_milestone_editor():
        if event is None:
            label = _("Create Milestone")
        else:
            label = _("Edit Milestone")
        return EditMilestoneDialog(parent, label, db, config, event)

    def edit_function():
        dialog = create_milestone_editor()
        dialog.ShowModal()
        dialog.Destroy()
    safe_locking(edit_controller, edit_function)
