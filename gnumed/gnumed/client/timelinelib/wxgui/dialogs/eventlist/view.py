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

from timelinelib.wxgui.dialogs.eventlist.controller import EventListDialogController
from timelinelib.wxgui.framework import Dialog


class EventListDialog(Dialog):

    """
    <BoxSizerVertical>

        <ListBox proportion="1" border="ALL" width="300"
            choices="$(event_list)"
            name="lb_events"
            event_EVT_LISTBOX_DCLICK="on_ok"
        />

        <DialogButtonsOkCancelSizer border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_OK="on_ok"
        />

    </BoxSizerVertical>
    """

    def __init__(self, parent, event_list):
        Dialog.__init__(self, EventListDialogController, parent, {
            "event_list": event_list
        }, title=_("Found Events"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init()
        if len(event_list) > 0:
            self.lb_events.SetSelection(0)

    def GetSelectedIndex(self):
        return self.lb_events.GetSelection()

    def Close(self):
        self.EndModal(wx.ID_OK)
