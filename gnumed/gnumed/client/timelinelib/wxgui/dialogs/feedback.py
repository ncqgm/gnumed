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


import webbrowser

import wx

from timelinelib.feedback.form import FeedbackForm
from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import display_information_message


INFO_LABEL_WIDTH = 600


class FeedbackDialog(wx.Dialog):

    def __init__(self, parent=None):
        wx.Dialog.__init__(self, parent, title="Feedback")
        self.controller = FeedbackForm(self, webbrowser)
        self._create_gui()

    def _create_gui(self):
        self._create_title_label()
        self._create_info_label()
        self._create_to_text_field()
        self._create_subject_text_field()
        self._create_body_text_field()
        self._create_send_default_button()
        self._create_send_gmail_button()
        self._create_send_other_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()

    def _create_title_label(self):
        self.title_label = wx.StaticText(self, label=_("Email Feedback"),
                                         style=wx.ALIGN_CENTER)
        self._increase_title_font_size()

    def _increase_title_font_size(self):
        font = self.title_label.GetFont()
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label.SetFont(font)

    def _create_info_label(self):
        self.info_label = wx.StaticText(self, size=(INFO_LABEL_WIDTH, -1))
        self._make_info_label_bold()

    def _make_info_label_bold(self):
        font = self.info_label.GetFont()
        font.SetWeight(wx.BOLD)
        self.info_label.SetFont(font)

    def _create_to_text_field(self):
        self.to_text = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)

    def _create_subject_text_field(self):
        self.subject_text = wx.TextCtrl(self, wx.ID_ANY)

    def _create_body_text_field(self):
        self.body_text = wx.TextCtrl(self, size=(-1, 200), style=wx.TE_MULTILINE)
        self.body_text.Bind(wx.EVT_CHAR, self._on_char)

    def _on_char(self, evt):
        if self._ctrl_a(evt):
            self.body_text.SelectAll()
        else: 
            evt.Skip()
        
    def _ctrl_a(self, evt):
        KEY_CODE_A = 1
        return evt.ControlDown() and evt.KeyCode == KEY_CODE_A

    def _create_send_default_button(self):
        def on_click(event):
            self.controller.send_with_default()
        self.btn_default_client = wx.Button(self, label=_("Default client"))
        self.Bind(wx.EVT_BUTTON, on_click, self.btn_default_client)

    def _create_send_gmail_button(self):
        def on_click(event):
            self.controller.send_with_gmail()
        self.btn_gmail = wx.Button(self, label=_("Gmail"))
        self.Bind(wx.EVT_BUTTON, on_click, self.btn_gmail)

    def _create_send_other_button(self):
        def on_click(evt):
            display_information_message(
                caption=_("Other email client"),
                message=_("Copy and paste this email into your favorite email client and send it from there."),
                parent=self)
        self.btn_other = wx.Button(self, label=_("Other"))
        self.Bind(wx.EVT_BUTTON, on_click, self.btn_other)

    def _create_close_button(self):
        self.btn_close = wx.Button(self, wx.ID_CLOSE)
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)

    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_label, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(self.info_label, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(self._create_layout_grid(), flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def _create_layout_grid(self):
        grid = wx.FlexGridSizer(4, 2, BORDER, BORDER)
        grid.AddGrowableCol(1)
        grid.Add(wx.StaticText(self, label=_("To:")), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.to_text, flag=wx.EXPAND)
        grid.Add(wx.StaticText(self, label=_("Subject:")), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.subject_text, flag=wx.EXPAND)
        grid.Add(wx.StaticText(self, label=_("Body:")), flag=0)
        grid.Add(self.body_text, flag=wx.EXPAND)
        grid.Add(wx.StaticText(self, label=_("Send With:")), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self._create_button_box(), flag=wx.EXPAND)
        return grid

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_default_client, flag=wx.RIGHT, border=BORDER)
        button_box.Add(self.btn_gmail, flag=wx.RIGHT, border=BORDER)
        button_box.Add(self.btn_other, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.LEFT, border=BORDER)
        return button_box

    def _set_focus_component(self):
        self.body_text.SetFocus()

    def get_to_text(self):
        return self.to_text.GetValue()

    def get_subject_text(self):
        return self.subject_text.GetValue()

    def get_body_text(self):
        return self.body_text.GetValue()

    def set_info_text(self, text):
        self.info_label.SetLabel(text)
        self.info_label.Wrap(INFO_LABEL_WIDTH)
        self.Fit()

    def set_to_text(self, text):
        self.to_text.SetValue(text)

    def set_subject_text(self, text):
        self.subject_text.SetValue(text)

    def set_body_text(self, text):
        self.body_text.SetValue(text)

    def set_body_selection(self, start, end):
        self.body_text.SetSelection(start, end)


def show_feedback_dialog(info, subject, body, parent=None):
    dialog = FeedbackDialog(parent)
    dialog.controller.populate(info, subject, body)
    dialog.ShowModal()
    dialog.Destroy()
