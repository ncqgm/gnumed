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

from timelinelib.editors.propertyeditors.baseeditor import BaseEditor


class HyperlinkEditorGuiCreator(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
            
    def create_sizer(self):
        return wx.GridBagSizer(5, 5)
        
    def create_controls(self):
        self.btn_add = self._create_add_button()
        self.btn_clear = self._create_clear_button()
        self.btn_test = self._create_test_button()
        self.url_panel = self._create_input_controls()
        return (self.btn_add, self.btn_clear, self.btn_test, self.url_panel)
    
    def put_controls_in_sizer(self, sizer, controls):
        self.btn_add, self.btn_clear, self.btn_test, self.url_panel = controls     
        sizer.Add(self.btn_add, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.btn_clear, wx.GBPosition(0, 1), wx.GBSpan(1, 1))
        sizer.Add(self.btn_test, wx.GBPosition(0, 2), wx.GBSpan(1, 1))
        sizer.Add(self.url_panel, wx.GBPosition(2, 0), wx.GBSpan(4, 5))

    def _create_add_button(self):
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        return btn_add

    def _create_clear_button(self):
        btn_clear = wx.Button(self, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn_clear)
        return btn_clear

    def _create_test_button(self):
        btn_test = wx.Button(self, wx.ID_ANY, _("Test"))
        self.Bind(wx.EVT_BUTTON, self._btn_test_on_click, btn_test)
        return btn_test

    def _create_input_controls(self):
        panel = wx.Panel(self)
        label = wx.StaticText(panel, label=_("URL:"))
        self.data = wx.TextCtrl(panel, size=(300,20))
        sizer = wx.GridBagSizer(5, 10)
        sizer.Add(label, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.data, wx.GBPosition(0, 1), wx.GBSpan(1, 9))
        panel.SetSizerAndFit(sizer)
        return panel


class HyperlinkEditor(BaseEditor, HyperlinkEditorGuiCreator):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, parent, editor)
        HyperlinkEditorGuiCreator.__init__(self, parent)
        self.create_gui()
        self._initialize_data()

    def _initialize_data(self):
        self._set_initial_text()
        self._set_visible(False)

    def _set_initial_text(self):
        self.data.SetValue("")

    def get_data(self):
        if self.url_visible:
            return self.data.GetValue()
        else:
            return None

    def set_data(self, data):
        if data == None:
            self._set_visible(False)
        else:
            self._set_visible(True)
            self.data.SetValue(data)

    def _btn_add_on_click(self, evt):
        self._set_visible(True)

    def _btn_clear_on_click(self, evt):
        self.clear_data()

    def _btn_test_on_click(self, evt):
        webbrowser.open(self.get_data())

    def clear_data(self):
        self._set_initial_text()
        self._set_visible(False)

    def _set_visible(self, value):
        self.url_visible = value
        self.url_panel.Show(self.url_visible)
        self.btn_add.Enable(not value)
        self.btn_clear.Enable(value)
        self.btn_test.Enable(value)
        self.GetSizer().Layout()
