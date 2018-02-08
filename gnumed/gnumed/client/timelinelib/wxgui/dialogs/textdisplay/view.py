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

from timelinelib.wxgui.dialogs.textdisplay.controller import TextDisplayDialogController
from timelinelib.wxgui.framework import Dialog


class TextDisplayDialog(Dialog):

    """
    <BoxSizerVertical>
        <TextCtrl name="text" style="TE_MULTILINE" width="660" height="300" border="ALL" />
        <BoxSizerHorizontal border="LEFT|BOTTOM|RIGHT">
            <Button id="$(id_copy)" border="RIGHT" event_EVT_BUTTON="on_copy_click" />
            <StretchSpacer />
            <DialogButtonsCloseSizer />
        </BoxSizerHorizontal>
    </BoxSizerVertical>
    """

    def __init__(self, title, text='', parent=None):
        Dialog.__init__(self, TextDisplayDialogController, parent, {
            "id_copy": wx.ID_COPY,
        }, title=title)
        self.controller.on_init(text)

    def GetText(self):
        return self.text.GetValue()

    def SetText(self, text):
        self.text.SetValue(text)
