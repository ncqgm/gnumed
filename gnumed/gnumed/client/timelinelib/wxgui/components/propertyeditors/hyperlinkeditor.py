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

from timelinelib.wxgui.components.propertyeditors.baseeditor import BaseEditor


class HyperlinkEditorGuiCreator(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

    def create_sizer(self):
        return wx.GridBagSizer(5, 5)

    def create_controls(self):
        self.btn_add = self._create_id_button(wx.ID_ADD, self._btn_add_on_click)
        self.btn_clear = self._create_id_button(wx.ID_CLEAR, self._btn_clear_on_click)
        self.btn_append = self._create_button(_("&Append"), self._btn_append_on_click)
        self.btn_remove = self._create_button(_("&Remove"), self._btn_remove_on_click)
        self.btn_test = self._create_button(_("Te&st"), self._btn_test_on_click)
        self.url_panel = self._create_input_controls()
        return (self.btn_add, self.btn_clear, self.btn_test, self.url_panel)

    def put_controls_in_sizer(self, sizer, controls):
        self.btn_add, self.btn_clear, self.btn_test, self.url_panel = controls
        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.btn_add)
        box_sizer.Add(self.btn_clear)
        box_sizer.Add(self.btn_append)
        box_sizer.Add(self.btn_remove)
        box_sizer.Add(self.btn_test)
        sizer.Add(box_sizer, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.url_panel, wx.GBPosition(1, 0), wx.GBSpan(4, 5), wx.EXPAND | wx.ALL)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)

    def _create_id_button(self, wxid, handler):
        btn = wx.Button(self, wxid)
        self.Bind(wx.EVT_BUTTON, handler, btn)
        return btn

    def _create_button(self, label, handler):
        btn = wx.Button(self, wx.ID_ANY, label)
        self.Bind(wx.EVT_BUTTON, handler, btn)
        return btn

    def _create_input_controls(self):
        TEXT_WIDTH = 300
        panel = wx.Panel(self)
        label = wx.StaticText(panel, label=_("URL:"))
        self.data = wx.TextCtrl(panel, size=(TEXT_WIDTH, 20))
        self.list = wx.ListBox(panel, wx.ID_ANY, size=(TEXT_WIDTH, -1))
        sizer = wx.GridBagSizer(5, 10)
        sizer.Add(label, wx.GBPosition(0, 0), wx.GBSpan(1, 1))
        sizer.Add(self.data, wx.GBPosition(0, 1), wx.GBSpan(1, 9), wx.EXPAND | wx.ALL, 1)
        sizer.Add(self.list, wx.GBPosition(1, 1), wx.GBSpan(1, 9), wx.EXPAND | wx.ALL, 1)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(1)
        panel.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_LISTBOX, self._lb_on_click, self.list)
        self.data.Bind(wx.EVT_SET_FOCUS, self._txt_on_focus)
        return panel


class HyperlinkEditor(BaseEditor, HyperlinkEditorGuiCreator):

    def __init__(self, parent, editor, name=""):
        BaseEditor.__init__(self, parent, editor)
        HyperlinkEditorGuiCreator.__init__(self, parent)
        self.create_gui()
        self._set_visible(False)

    def get_data(self):
        if self.url_visible:
            urls = [item for item in self.list.GetItems() if len(item.strip()) > 0]
            if len(urls) > 0:
                return ";".join(urls)
            else:
                return None
        else:
            return None

    def set_data(self, data):
        if data is None:
            self._set_visible(False)
        else:
            self._set_visible(True)
            self.list.InsertItems(data.split(";"), 0)

    def _btn_add_on_click(self, evt):
        self._set_visible(True)

    def _btn_clear_on_click(self, evt):
        self.clear_data()

    def _btn_append_on_click(self, evt):
        if len(self.data.GetValue().strip()) > 0:
            self.list.Append(self.data.GetValue())
            self.data.SetValue("")
            self._change_btn_visibility()
        self.data.SetFocus()

    def _btn_remove_on_click(self, evt):
        try:
            self.list.Delete(self.list.GetSelection())
        except:
            pass
        self.data.SetFocus()

    def _btn_test_on_click(self, evt):
        url = self.list.GetStringSelection()
        if len(url) > 0:
            webbrowser.open(url)

    def _lb_on_click(self, evt):
        self._change_btn_visibility()

    def _txt_on_focus(self, evt):
        self.list.Deselect(wx.NOT_FOUND)
        self._change_btn_visibility()

    def clear_data(self):
        self._set_visible(False)

    def _set_visible(self, value):
        self.url_visible = value
        self.url_panel.Show(self.url_visible)
        self.btn_add.Enable(not value)
        self.btn_clear.Enable(value)
        self.btn_append.Enable(value)
        self.GetSizer().Layout()
        self.data.SetFocus()

    def _change_btn_visibility(self):
        if self.list.GetSelection() == wx.NOT_FOUND:
            self.btn_remove.Enable(False)
            self.btn_test.Enable(False)
            self.btn_append.Enable(True)
        else:
            self.btn_remove.Enable(True)
            self.btn_test.Enable(True)
            self.btn_append.Enable(False)

