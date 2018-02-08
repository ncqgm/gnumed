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


import os

import wx

from timelinelib.config.paths import ICONS_DIR
from timelinelib.wxgui.dialogs.eventeditortabselection.controller import EventEditorTabSelectionDialogController
from timelinelib.wxgui.framework import Dialog


class EventEditorTabSelectionDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticText label="$(header_text)" border="ALL"/>
        <BoxSizerHorizontal border="LEFT|RIGHT" proportion="1">
            <ListBox
                name="lst_tab_order"
                width="120"
                height="150"
                proportion="1"
                event_EVT_LISTBOX="on_selection_changed"
            />
            <Spacer />
            <BoxSizerVertical align="ALIGN_CENTER_VERTICAL">
                <BitmapButton
                    name="btn_up"
                    bitmap="$(up_bitmap)"
                    event_EVT_BUTTON="on_up"
                />
                <Spacer />
                <BitmapButton
                    name="btn_down"
                    bitmap="$(down_bitmap)"
                    event_EVT_BUTTON="on_down"
                />
            </BoxSizerVertical>
        </BoxSizerHorizontal>
        <DialogButtonsOkCancelSizer
            border="ALL"
            event_EVT_BUTTON__ID_OK="on_ok"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, config):
        Dialog.__init__(self, EventEditorTabSelectionDialogController, parent, {
            "header_text": _("Select Tab Order:"),
            "up_bitmap": self._GetBitmap(wx.ART_GO_UP),
            "down_bitmap": self._GetBitmap(wx.ART_GO_DOWN)
        }, title=_("Event Editor Tab Order"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init(config)

    def FillListbox(self, tab_items):
        for text, key in tab_items:
            self.lst_tab_order.Append(text, key)
        self.lst_tab_order.Select(0)

    def Close(self):
        self.EndModalOk()

    def GetSelection(self):
        return self.lst_tab_order.GetSelection()

    def GetClientData(self, inx):
        return self.lst_tab_order.GetClientData(inx)

    def DisableBtnDown(self):
        self.btn_down.Disable()

    def EnableBtnDown(self):
        self.btn_down.Enable()

    def DisableBtnUp(self):
        self.btn_up.Disable()

    def EnableBtnUp(self):
        self.btn_up.Enable()

    def MoveSelectionUp(self, inx):
        self._MoveSelection(inx, -1)

    def MoveSelectionDown(self, inx):
        self._MoveSelection(inx, 1)

    def _MoveSelection(self, inx, offset):
        text = self.lst_tab_order.GetString(inx)
        key = self.lst_tab_order.GetClientData(inx)
        self.lst_tab_order.Delete(inx)
        self.lst_tab_order.Insert(text, inx + offset, key)
        self.lst_tab_order.Select(inx + offset)

    def _GetBitmap(self, bitmap_id):
        if 'wxMSW' in wx.PlatformInfo:
            name = {wx.ART_GO_UP: "up.png", wx.ART_GO_DOWN: "down.png"}
            return wx.Bitmap(os.path.join(ICONS_DIR, name[bitmap_id]))
        else:
            size = (24, 24)
            return wx.ArtProvider.GetBitmap(bitmap_id, wx.ART_TOOLBAR, size)
