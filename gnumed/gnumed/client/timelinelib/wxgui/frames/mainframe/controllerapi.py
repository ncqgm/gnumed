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


import os.path

import wx

from timelinelib.meta.about import APPLICATION_NAME
import timelinelib.wxgui.frames.mainframe.guicreator as guic


class MainFrameApiUsedByController(object):

    def set_timeline_readonly(self):
        self._set_readonly_text_in_status_bar()
        self.enable_disable_menus()

    def update_open_recent_submenu(self):
        self._clear_recent_menu_items()
        self._create_recent_menu_items()

    def display_timeline(self, timeline):
        self.timeline = timeline
        self.menu_controller.on_timeline_change(timeline)
        self.main_panel.display_timeline(timeline)
        self._set_title()
        self._set_readonly_text_in_status_bar()

    def update_navigation_menu_items(self):
        self._clear_navigation_menu_items()
        if self.timeline:
            self._create_navigation_menu_items()
            self.shortcut_controller.add_navigation_functions()

    # Also used by TinmelineView
    def enable_disable_menus(self):
        self.menu_controller.enable_disable_menus(self.main_panel.timeline_panel_visible())
        self._enable_disable_one_selected_event_menus()
        self._enable_disable_measure_distance_between_two_events_menu()
        self._enable_disable_searchbar()
        self._enable_disable_undo()

    def _set_title(self):
        if self.timeline is None:
            self.SetTitle(APPLICATION_NAME)
        else:
            self.SetTitle("%s (%s) - %s" % (
                os.path.basename(self.timeline.path),
                os.path.dirname(os.path.abspath(self.timeline.path)),
                APPLICATION_NAME))

    def _set_readonly_text_in_status_bar(self):
        if self.controller.timeline_is_readonly():
            text = _("read-only")
        else:
            text = ""
        self.status_bar_adapter.set_read_only_text(text)

    def _clear_navigation_menu_items(self):
        while self._navigation_menu_items:
            item = self._navigation_menu_items.pop()
            if item in self._navigate_menu.MenuItems:
                self._navigate_menu.Remove(item)
        self._navigation_functions_by_menu_item_id.clear()

    def _create_navigation_menu_items(self):
        item_data = self.timeline.get_time_type().get_navigation_functions()
        pos = 0
        id_offset = self.get_navigation_id_offset()
        for (itemstr, fn) in item_data:
            if itemstr == "SEP":
                item = self._navigate_menu.InsertSeparator(pos)
            else:
                wxid = guic.ID_NAVIGATE + id_offset
                item = self._navigate_menu.Insert(pos, wxid, itemstr)
                self._navigation_functions_by_menu_item_id[item.GetId()] = fn
                self.Bind(wx.EVT_MENU, self._navigation_menu_item_on_click, item)
                self.shortcut_items[wxid] = item
                id_offset += 1
            self._navigation_menu_items.append(item)
            pos += 1

    def get_navigation_id_offset(self):
        id_offset = 0
        if self.timeline.get_time_type().get_name() == "numtime":
            id_offset = 100
        return id_offset

    def _navigation_menu_item_on_click(self, evt):
        self.save_time_period()
        fn = self._navigation_functions_by_menu_item_id[evt.GetId()]
        time_period = self.main_panel.get_time_period()
        fn(self, time_period, self.main_panel.Navigate)

    def _clear_recent_menu_items(self):
        for item in self.mnu_file_open_recent_submenu.GetMenuItems():
            self.mnu_file_open_recent_submenu.Delete(item)

    def _create_recent_menu_items(self):
        self.open_recent_map = {}
        for path in self.config.get_recently_opened():
            self._map_path_to_recent_menu_item(path)

    def _map_path_to_recent_menu_item(self, path):
        name = "%s (%s)" % (
            os.path.basename(path),
            os.path.dirname(os.path.abspath(path)))
        item = self.mnu_file_open_recent_submenu.Append(wx.ID_ANY, name)
        self.open_recent_map[item.GetId()] = path
        self.Bind(wx.EVT_MENU, self._mnu_file_open_recent_item_on_click, item)

    def _mnu_file_open_recent_item_on_click(self, event):
        path = self.open_recent_map[event.GetId()]
        self.controller.open_timeline_if_exists(path)

    def _enable_disable_one_selected_event_menus(self):
        nbr_of_selected_events = self.main_panel.get_nbr_of_selected_events()
        one_event_selected = nbr_of_selected_events == 1
        some_event_selected = nbr_of_selected_events > 0
        mnu_edit_event = self. _timeline_menu.FindItemById(guic.ID_EDIT_EVENT)
        mnu_duplicate_event = self. _timeline_menu.FindItemById(guic.ID_DUPLICATE_EVENT)
        mnu_set_category = self. _timeline_menu.FindItemById(guic.ID_SET_CATEGORY_ON_SELECTED)
        mnu_edit_event.Enable(one_event_selected)
        mnu_duplicate_event.Enable(one_event_selected)
        mnu_set_category.Enable(some_event_selected)
        self._timeline_menu.FindItemById(guic.ID_MOVE_EVENT_UP).Enable(one_event_selected)
        self._timeline_menu.FindItemById(guic.ID_MOVE_EVENT_DOWN).Enable(one_event_selected)

    def _enable_disable_measure_distance_between_two_events_menu(self):
        two_events_selected = self.main_panel.get_nbr_of_selected_events() == 2
        mnu_measure_distance = self._timeline_menu.FindItemById(guic.ID_MEASURE_DISTANCE)
        mnu_measure_distance.Enable(two_events_selected)

    def _enable_disable_searchbar(self):
        if self.timeline is None:
            self.main_panel.show_searchbar(False)

    def _enable_disable_undo(self):
        mnu_undo = self._timeline_menu.FindItemById(guic.ID_UNDO)
        mnu_redo = self._timeline_menu.FindItemById(guic.ID_REDO)
        if self.timeline is not None:
            mnu_undo.Enable(self.timeline.undo_enabled())
            mnu_redo.Enable(self.timeline.redo_enabled())
        else:
            mnu_undo.Enable(False)
            mnu_redo.Enable(False)
