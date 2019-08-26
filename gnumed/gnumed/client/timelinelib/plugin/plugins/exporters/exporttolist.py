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

from timelinelib.wxgui.utils import BORDER
from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.plugins.exporters import EXPORTER
from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonsclosesizer import DialogButtonsCloseSizer
import wx.lib.mixins.listctrl as listmix


class ListExporter(PluginBase):

    def service(self):
        return EXPORTER

    def display_name(self):
        return _("Export to Listbox...")

    def run(self, main_frame):
        self.db = main_frame.timeline
        dlg = ListboxDialog(self.display_name()[:-3])
        dlg.populate(self._get_events(main_frame))
        dlg.ShowModal()
        dlg.Destroy()

    def _get_events(self, main_frame):
        visible_categories = self._get_visible_categories(main_frame)
        return [
            (
                self.db.get_time_type().format_period(event.get_time_period()),
                event.get_text()
            )
            for event
            in sorted(
                self.db.get_all_events(),
                key=lambda event: event.get_start_time()
            )
            if (main_frame.config.filtered_listbox_export and event.get_category() in visible_categories) or not main_frame.config.filtered_listbox_export
        ]

    def _get_visible_categories(self, main_frame):
        if main_frame.config.filtered_listbox_export:
            vp = main_frame.get_view_properties()
            return [cat for cat in self.db.get_categories() if vp.is_category_visible(cat)]
        else:
            return [cat for cat in self.db.get_categories()]


class ListboxDialog(wx.Dialog):

    def __init__(self, title, parent=None, events=None):
        wx.Dialog.__init__(self, parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self._create_gui()
        if events is not None:
            self.populate(events)

    def populate(self, events):
        self.list.populate(events)

    def _create_gui(self):
        self.list = TestListCtrl(self)
        self.btn_copy = self._create_copy_button()
        vbox = self._create_vbox(self.list, self.btn_copy, DialogButtonsCloseSizer(self))
        self.SetSizerAndFit(vbox)

    def _create_copy_button(self):
        btn_copy = wx.Button(self, wx.ID_COPY)
        self.Bind(wx.EVT_BUTTON, self.on_copy, btn_copy)
        return btn_copy

    def on_copy(self, evt):
        if wx.TheClipboard.Open():
            self._copy_text_to_clipboard()
        else:
            self.view.DisplayErrorMessage(_("Unable to copy to clipboard."))

    def _copy_text_to_clipboard(self):
        obj = wx.TextDataObject(self.GetText())
        wx.TheClipboard.SetData(obj)
        wx.TheClipboard.Close()

    def GetText(self):
        return self.list.GetText()

    def _create_vbox(self, ctrl, btn_copy, btn_box):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(btn_copy, 0, flag=wx.ALL | wx.EXPAND, border=BORDER)
        hbox.Add(btn_box, 1, flag=wx.ALL, border=BORDER)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(ctrl, 1, flag=wx.ALL | wx.EXPAND, border=BORDER)
        vbox.Add(hbox, 0, flag=wx.ALL | wx.EXPAND, border=BORDER)
        return vbox


class TestListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, parent, pos=wx.DefaultPosition, size=(400, 400), style=wx.LC_REPORT):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

    def populate(self, items):
        self.InsertColumn(0, _("Time period"))
        self.InsertColumn(1, _("Event"))
        for period, event in items:
            self.Append([period, event])
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def GetText(self):
        collector = []
        for i in range(self.GetItemCount()):
            item = self.GetItem(i, 0)
            collector.append(item.GetText())
            collector.append("\t")
            item = self.GetItem(i, 1)
            collector.append(item.GetText())
            collector.append("\n")
        return "".join(collector)
