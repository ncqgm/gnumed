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

from timelinelib.wxgui.utils import time_picker_for

from timelinelib.editors.propertyeditors.baseeditor import BaseEditor


class AlertEditorGuiCreator(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
            
    def create_sizer(self):
        return wx.GridBagSizer(vgap=5, hgap=5)
        
    def create_controls(self):
        self.btn_add = self._create_add_button()
        self.btn_clear = self._create_clear_button()
        self.input_panel = self._create_input_controls()
        return (self.btn_add, self.btn_clear, self.input_panel)
    
    def put_controls_in_sizer(self, sizer, controls):
        btn_add, btn_clear, input_panel = controls 
        sizer.Add(btn_add, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(btn_clear, wx.GBPosition(0, 1), wx.GBSpan(1, 1))
        sizer.Add(input_panel, wx.GBPosition(1, 0), wx.GBSpan(4, 5))
        
    def _create_add_button(self):
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        return btn_add

    def _create_clear_button(self):
        btn_clear = wx.Button(self, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn_clear)
        return btn_clear

    def _create_input_controls(self):
        alert_panel = wx.Panel(self)
        time_type = self.editor.timeline.get_time_type()
        self.dtp_start =  time_picker_for(time_type)(alert_panel, config=self.editor.config)
        self.text_data = wx.TextCtrl(alert_panel, size=(300,80), style=wx.TE_MULTILINE)
        self.data = self.dtp_start
        self._layout_input_controls(alert_panel)
        return alert_panel

    def _layout_input_controls(self, alert_panel):
        when = wx.StaticText(alert_panel, label=_("When:"))
        text = wx.StaticText(alert_panel, label=_("Text:"))
        sizer = wx.GridBagSizer(5, 10)
        sizer.Add(when, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.dtp_start, wx.GBPosition(0, 1), wx.GBSpan(1, 3))
        sizer.Add(text, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        sizer.Add(self.text_data, wx.GBPosition(1, 1), wx.GBSpan(1, 9))
        alert_panel.SetSizerAndFit(sizer)


class AlertEditor(BaseEditor, AlertEditorGuiCreator):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, parent, editor)
        AlertEditorGuiCreator.__init__(self, parent)
        self.create_gui()
        self._initialize_data()

    def _initialize_data(self):
        self._set_initial_time()
        self._set_initial_text()
        self._set_visible(False)

    def _set_initial_time(self):
        if self.editor.event is not None:
            self.dtp_start.set_value(self.editor.event.time_period.start_time)
        else:
            self.dtp_start.set_value(self.editor.start)

    def _set_initial_text(self):
        self.text_data.SetValue("")

    def get_data(self):
        if self.input_visible:
            time = self.dtp_start.get_value()
            text = self.text_data.GetValue()
            return (time, text)
        else:
            return None

    def set_data(self, data):
        if data == None:
            self._set_visible(False)
        else:
            self._set_visible(True)
            time, text = data
            self.dtp_start.set_value(time)
            self.text_data.SetValue(text)

    def _btn_add_on_click(self, evt):
        self._set_visible(True)

    def _btn_clear_on_click(self, evt):
        self.clear_data()

    def clear_data(self):
        self._set_initial_time()
        self._set_initial_text()
        self._set_visible(False)

    def _set_visible(self, value):
        self.input_visible = value
        self.input_panel.Show(self.input_visible)
        self.btn_add.Enable(not value)
        self.btn_clear.Enable(value)
        self.GetSizer().Layout()
