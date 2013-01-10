# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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

from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import _display_error_message
from timelinelib.editors.textdisplay import TextDisplayEditor


class TextDisplayDialogGui(wx.Dialog):

    def __init__(self, title, parent=None):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()

    def _create_gui(self):
        self._text = self._create_text_control()
        button_box = self._create_button_box()
        vbox = self._create_vbox(self._text, button_box)
        self.SetSizerAndFit(vbox)

    def _create_text_control(self):
        return wx.TextCtrl(self, size=(660, 300), style=wx.TE_MULTILINE)

    def _create_button_box(self):
        self.btn_copy = self._create_copy_btn()
        self.btn_close = self._create_close_btn()
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_copy, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.LEFT, border=BORDER)
        return button_box

    def _create_vbox(self, text, btn_box):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(text, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(btn_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        return vbox

    def _create_copy_btn(self):
        btn_copy = wx.Button(self, wx.ID_COPY)
        return btn_copy

    def _create_close_btn(self):
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        return btn_close


class TextDisplayDialog(TextDisplayDialogGui):

    def __init__(self, title, text, parent=None):
        TextDisplayDialogGui.__init__(self, title, parent)
        self._bind_events()
        self.controller = TextDisplayEditor(self, text)
        self.controller.initialize()

    def set_text(self, text):
        self._text.SetValue(text)

    def get_text(self):
        return self._text.GetValue()

    def _bind_events(self):
        self.Bind(wx.EVT_BUTTON, self._btn_copy_on_click, self.btn_copy)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, self.btn_close)

    def _btn_copy_on_click(self, evt):
        if wx.TheClipboard.Open():
            self._copy_text_to_clipboard()
        else:
            _display_error_message(_("Unable to copy to clipboard."))

    def _copy_text_to_clipboard(self):
        obj = wx.TextDataObject(self.controller.get_text())
        wx.TheClipboard.SetData(obj)
        wx.TheClipboard.Close()
    def _btn_close_on_click(self, evt):
        self.Close()
