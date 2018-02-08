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

from timelinelib.wxgui.dialogs.filenew.controller import FileNewDialogController
from timelinelib.wxgui.framework import Dialog


class FileNewDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticText
            label="$(explanation_text)"
            border="ALL"
        />
        <BoxSizerHorizontal
            proportion="1"
            border="LEFT|RIGHT"
        >
            <ListBox
                name="type_list"
                width="150"
                height="200"
                event_EVT_LISTBOX="on_selection_changed"
            />
            <StaticBoxSizerVertical
                proportion="1"
                label="$(description_text)"
                border="LEFT"
            >
                <StaticText
                    name="description"
                    width="200"
                    style="ST_NO_AUTORESIZE"
                    proportion="1"
                    border="ALL"
                />
            </StaticBoxSizerVertical>
        </BoxSizerHorizontal>
        <DialogButtonsOkCancelSizer
            border="ALL"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, items):
        Dialog.__init__(self, FileNewDialogController, parent, {
            "explanation_text": _("Choose what type of timeline you want to create."),
            "description_text": _("Description"),
        }, title=_("Create new timeline"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init(items)

    def SetItems(self, items):
        self.type_list.SetItems(items)
        self.type_list.SetFocus()

    def SelectItem(self, index):
        self.type_list.SetSelection(index)
        event = wx.CommandEvent()
        event.SetInt(index)
        self.controller.on_selection_changed(event)

    def SetDescription(self, text):
        self.description.SetLabel(text)

    def GetSelection(self):
        return self.controller.get_selection()
