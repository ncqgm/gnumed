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


from timelinelib.wxgui.framework import Controller


CONTROL_ROWS_CREATORS = {"0": "Time details", "1": "Checkboxes",
                         "2": "Text Field", "3": "Categories listbox",
                         "4": "Container listbox", ":": "Notebook"}


class EventEditorTabSelectionDialogController(Controller):

    def on_init(self, config):
        self.config = config
        tab_items = []
        for key in self.config.event_editor_tab_order:
            tab_items.append((CONTROL_ROWS_CREATORS[key], key))
        self.view.FillListbox(tab_items)
        self.view.EnableBtnDown()
        self.view.DisableBtnUp()

    def on_ok(self, evt):
        self._save_tab_order()
        self.view.Close()

    def on_selection_changed(self, evt):
        if self._is_first_selected():
            self.view.DisableBtnUp()
        else:
            self.view.EnableBtnUp()
        if self._is_last_selected():
            self.view.DisableBtnDown()
        else:
            self.view.EnableBtnDown()

    def on_up(self, evt):
        inx = self.view.GetSelection()
        self.view.MoveSelectionUp(inx)
        if inx == 1:
            self.view.DisableBtnUp()
        self.view.EnableBtnDown()

    def on_down(self, evt):
        inx = self.view.GetSelection()
        self.view.MoveSelectionDown(inx)
        if inx == len(CONTROL_ROWS_CREATORS) - 2:
            self.view.DisableBtnDown()
        self.view.EnableBtnUp()

    def _is_first_selected(self):
        return self.view.GetSelection() == 0

    def _is_last_selected(self):
        return self.view.GetSelection() == (len(CONTROL_ROWS_CREATORS) - 1)

    def _save_tab_order(self):
        collector = []
        for i in range(len(self.config.event_editor_tab_order)):
            collector.append(self.view.GetClientData(i))
        self.config.event_editor_tab_order = "".join(collector)
