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

from timelinelib.config.preferences import PreferencesEditor
from timelinelib.wxgui.utils import BORDER


class PreferencesDialog(wx.Dialog):

    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, title=_("Preferences"))
        self._create_gui()
        self._controller = PreferencesEditor(self, config)
        self._controller.initialize_controls()

    def set_checkbox_use_inertial_scrolling(self, value):
        self.chb_inertial_scrolling.SetValue(value)

    def set_checkbox_open_recent_at_startup(self, value):
        self.chb_open_recent.SetValue(value)

    def set_week_start(self, index):
        self.choice_week.SetSelection(index)

    def _create_gui(self):
        main_box = self._create_main_box()
        self.SetSizerAndFit(main_box)

    def _create_main_box(self):
        notebook = self._create_nootebook_control()
        button_box = self._create_button_box()
        main_box = wx.BoxSizer(wx.VERTICAL)
        flag = wx.ALL|wx.EXPAND
        main_box.Add(notebook, flag=flag, border=BORDER, proportion=1)
        main_box.Add(button_box, flag=flag, border=BORDER)
        return main_box

    def _create_nootebook_control(self):
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        self._create_general_tab(notebook)
        self._create_date_time_tab(notebook)
        return notebook

    def _create_button_box(self):
        btn_close = self._create_close_button()
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        return button_box

    def _create_general_tab(self, notebook):
        panel = self._create_tab_panel(notebook, _("General"))
        controls = self._create_general_tab_controls(panel)
        self._size_tab_panel(panel, controls)

    def _create_general_tab_controls(self, panel):
        self.chb_open_recent = self._create_chb_open_recent(panel)
        self.chb_inertial_scrolling = self._create_chb_inertial_scrolling(panel)
        return (self.chb_open_recent, self.chb_inertial_scrolling)

    def _create_date_time_tab(self, notebook):
        panel = self._create_tab_panel(notebook, _("Date && Time"))
        controls = self._create_date_time_tab_controls(panel)
        self._size_tab_panel(panel, controls)

    def _create_date_time_tab_controls(self, panel):
        self.choice_week = self._create_choice_week(panel)
        grid = wx.FlexGridSizer(1, 2, BORDER, BORDER)
        grid.Add(wx.StaticText(panel, label=_("Week start on:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.choice_week, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        return (grid,)
    
    def _create_tab_panel(self, notebook, label):
        panel = wx.Panel(notebook)
        notebook.AddPage(panel, label)
        return panel

    def _size_tab_panel(self, panel, controls):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for control in controls:
            sizer.Add(control, flag=wx.ALL|wx.EXPAND, border=BORDER)
        panel.SetSizer(sizer)

    def _create_chb_open_recent(self, panel):
        label = _("Open most recent timeline on startup")
        handler = self._chb_open_recent_startup_on_checkbox
        chb = self._create_chb(panel, label, handler)
        return chb

    def _create_chb_inertial_scrolling(self, panel):
        label = _("Use inertial scrolling")
        handler = self._chb_use_inertial_scrolling_on_checkbox
        chb = self._create_chb(panel, label, handler)
        return chb

    def _create_chb(self, panel, label, handler):
        chb = wx.CheckBox(panel, label=label)
        self.Bind(wx.EVT_CHECKBOX, handler, chb)
        return chb

    def _create_choice_week(self, panel):
        choice_week = wx.Choice(panel, choices=[_("Monday"), _("Sunday")])
        self.Bind(wx.EVT_CHOICE, self._choice_week_on_choice, choice_week)
        return choice_week

    def _create_close_button(self):
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        return btn_close

    def _chb_use_inertial_scrolling_on_checkbox(self, evt):
        self._controller.on_use_inertial_scrolling_changed(evt.IsChecked())

    def _chb_open_recent_startup_on_checkbox(self, evt):
        self._controller.on_open_recent_changed(evt.IsChecked())

    def _choice_week_on_choice(self, evt):
        self._controller.on_week_start_changed(evt.IsChecked())

    def _btn_close_on_click(self, e):
        self.EndModal(wx.ID_OK)
