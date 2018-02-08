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
import webbrowser

from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.dialogs.slideshow.controller import SlideshowDialogController
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import get_user_ack


class SlideshowDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticBoxSizerVertical
            label="$(events_label)"
            border="ALL"
            proportion="1">
            <RadioButton
                label="Only visible events"
                border="TOP|BOTTOM|LEFT"
                name="rb_visible_events" />
            <RadioButton
                label="All events"
                border="BOTTOM|LEFT"
                name="rb_all_events" />
        </StaticBoxSizerVertical>
        <StaticBoxSizerVertical
            label="$(target_dir_label)"
            border="BOTTOM|LEFT|RIGHT"
            proportion="0">
            <BoxSizerHorizontal>
                <TextCtrl
                    border="BOTTOM|LEFT"
                    width="200"
                    name="tb_target_dir" />
                <Button
                    label="..."
                    border="BOTTOM|LEFT"
                    width="25"
                    name="tb_target" 
                    event_EVT_BUTTON="on_change_dir" />
            </BoxSizerHorizontal>
        </StaticBoxSizerVertical>
        <DialogButtonsOkCancelSizer
            border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_OK="on_start"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, db, canvas):
        self._db = db
        self._canvas = canvas
        Dialog.__init__(self, SlideshowDialogController, parent, {
            "events_label": _("Select Events"),
            "target_dir_label": _("Save html pages at")
        }, title=_("Start Slide Show"))
        self.controller.on_init(db, canvas)

    def ChangeDir(self):
        dialog = wx.DirDialog(self, _("Select html pages directory"), "")
        if dialog.ShowModal() == wx.ID_OK:
            self.tb_target_dir.SetValue(dialog.GetPath())
        dialog.Destroy()

    def AllEventsSelected(self):
        return self.rb_all_events.GetValue()

    def GetTargetDir(self):
        return self.tb_target_dir.GetValue()

    def InvalidTargetDir(self, message):
        display_error_message(message)
        self.tb_target_dir.SetFocus()

    def GetUserAck(self, query):
        return get_user_ack(query)

    def DisplayStartPage(self, page_path):
        webbrowser.open(page_path, new=1)


def open_slideshow_dialog(db, canvas):
    dialog = SlideshowDialog(None, db, canvas)
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()
