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

from timelinelib.wxgui.framework import Controller


class TextDisplayDialogController(Controller):

    def on_init(self, text):
        self.view.SetText(text)

    def on_copy_click(self, event):
        if wx.TheClipboard.Open():
            self._copy_text_to_clipboard()
        else:
            self.view.DisplayErrorMessage(_("Unable to copy to clipboard."))

    def _copy_text_to_clipboard(self):
        obj = wx.TextDataObject(self.view.GetText())
        wx.TheClipboard.SetData(obj)
        wx.TheClipboard.Close()
