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
import webbrowser

from timelinelib.feedback.feature import FeatureForm
from timelinelib.wxgui.utils import BORDER


INFO_LABEL_WIDTH = 600
BODY_TEXT_HEIGHT = 200


class FeatureDialogGui(wx.Dialog):

    def __init__(self, parent=None):
        wx.Dialog.__init__(self, parent, title=_("Feedback On Feature"))
        self._create_gui()

    def _create_gui(self):
        self._create_feature_name_label()
        self._create_feature_text_field()
        self._create_feedback_button()
        self._create_cancel_button()
        self._layout_components()
        self._set_default_component()

    def _create_feature_name_label(self):
        self.info_label = wx.StaticText(self, size=(INFO_LABEL_WIDTH, -1))
        self._make_info_label_bold()

    def _make_info_label_bold(self):
        font = self.info_label.GetFont()
        font.SetWeight(wx.BOLD)
        self.info_label.SetFont(font)

    def _create_feature_text_field(self):
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_AUTO_URL
        self.body_text = wx.TextCtrl(self, size=(-1, BODY_TEXT_HEIGHT), style=style)
        self.body_text.Bind(wx.EVT_TEXT_URL, self._on_text_url)
        
    def _on_text_url(self, evt):
        if evt.MouseEvent.LeftUp(): 
            start = evt.GetURLStart()
            end = evt.GetURLEnd()
            url = self.body_text.GetValue()[start:end]
            webbrowser.open(url)
        evt.Skip() 


    def _create_feedback_button(self):
        def on_click(event):
            self.controller.give_feedback()
        self.btn_feedback = wx.Button(self, label=_("Give Feedback"))
        self.Bind(wx.EVT_BUTTON, on_click, self.btn_feedback)

    def _create_cancel_button(self):
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL)
        self.btn_cancel.SetFocus()
        self.SetAffirmativeId(wx.ID_CANCEL)

    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.info_label, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(self.body_text, flag=wx.ALL|wx.EXPAND, border=BORDER)
        vbox.Add(self._create_button_box(), flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_feedback, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_cancel, flag=wx.LEFT, border=BORDER)
        return button_box
    
    def _set_default_component(self):
        self.btn_feedback.SetDefault()
        self.btn_feedback.SetFocus()


class FeatureDialog(FeatureDialogGui):

    def __init__(self, parent=None):
        FeatureDialogGui.__init__(self, parent)
        self.controller = FeatureForm(self)

    def set_feature_name(self, text):
        self.info_label.SetLabel(text)
        self.info_label.Wrap(INFO_LABEL_WIDTH)
        self.Fit()

    def set_feature_description(self, text):
        self.body_text.SetValue(text)
