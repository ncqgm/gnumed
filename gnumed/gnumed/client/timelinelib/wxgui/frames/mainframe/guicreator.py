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

"""
A base class for the mainframe window, responsible for creating the GUI.
"""


import collections
import wx

from timelinelib.db.utils import safe_locking
from timelinelib.meta.about import display_about_dialog
from timelinelib.plugin.factory import EVENTBOX_DRAWER
from timelinelib.plugin.factory import EXPORTER
from timelinelib.plugin import factory
from timelinelib.proxies.drawingarea import DrawingAreaProxy
from timelinelib.wxgui.components.mainpanel import MainPanel
from timelinelib.wxgui.components.statusbaradapter import StatusBarAdapter
from timelinelib.wxgui.dialogs.duplicateevent.view import open_duplicate_event_dialog_for_event
from timelinelib.wxgui.dialogs.editevent.view import open_create_event_editor
from timelinelib.wxgui.dialogs.feedback.view import show_feedback_dialog
from timelinelib.wxgui.dialogs.filenew.view import FileNewDialog
from timelinelib.wxgui.dialogs.importevents.view import ImportEventsDialog
from timelinelib.wxgui.dialogs.milestone.view import open_milestone_editor_for
from timelinelib.wxgui.dialogs.preferences.view import PreferencesDialog
from timelinelib.wxgui.dialogs.shortcutseditor.view import ShortcutsEditorDialog
from timelinelib.wxgui.dialogs.systeminfo.view import show_system_info_dialog


NONE = 0
CHECKBOX = 1
CHECKED_RB = 2
UNCHECKED_RB = 3
ID_SIDEBAR = wx.NewId()
ID_LEGEND = wx.NewId()
ID_BALLOONS = wx.NewId()
ID_ZOOMIN = wx.NewId()
ID_ZOOMOUT = wx.NewId()
ID_VERT_ZOOMIN = wx.NewId()
ID_VERT_ZOOMOUT = wx.NewId()
ID_CREATE_EVENT = wx.NewId()
ID_CREATE_MILESTONE = wx.NewId()
ID_PT_EVENT_TO_RIGHT = wx.NewId()
ID_EDIT_EVENT = wx.NewId()
ID_DUPLICATE_EVENT = wx.NewId()
ID_SET_CATEGORY_ON_SELECTED = wx.NewId()
ID_MEASURE_DISTANCE = wx.NewId()
ID_COMPRESS = wx.NewId()
ID_SET_CATEGORY_ON_WITHOUT = wx.NewId()
ID_EDIT_ERAS = wx.NewId()
ID_SET_READONLY = wx.NewId()
ID_FIND_FIRST = wx.NewId()
ID_FIND_LAST = wx.NewId()
ID_FIT_ALL = wx.NewId()
ID_EDIT_SHORTCUTS = wx.NewId()
ID_TUTORIAL = wx.NewId()
ID_NUMTUTORIAL = wx.NewId()
ID_FEEDBACK = wx.NewId()
ID_CONTACT = wx.NewId()
ID_SYSTEM_INFO = wx.NewId()
ID_IMPORT = wx.NewId()
ID_EXPORT = wx.NewId()
ID_EXPORT_ALL = wx.NewId()
ID_EXPORT_SVG = wx.NewId()
ID_FIND_CATEGORIES = wx.NewId()
ID_SELECT_ALL = wx.NewId()
ID_RESTORE_TIME_PERIOD = wx.NewId()
ID_NEW = wx.ID_NEW
ID_FIND = wx.ID_FIND
ID_UNDO = wx.NewId()
ID_REDO = wx.NewId()
ID_PREFERENCES = wx.ID_PREFERENCES
ID_HELP = wx.ID_HELP
ID_ABOUT = wx.ID_ABOUT
ID_SAVEAS = wx.ID_SAVEAS
ID_EXIT = wx.ID_EXIT
ID_MOVE_EVENT_UP = wx.NewId()
ID_MOVE_EVENT_DOWN = wx.NewId()
ID_PRESENTATION = wx.NewId()
ID_HIDE_DONE = wx.NewId()
ID_NAVIGATE = wx.NewId() + 100


class GuiCreator(object):

    def _create_gui(self):
        self.shortcut_items = {}
        self._create_status_bar()
        self._create_main_panel()
        self._create_main_menu_bar()
        self._bind_frame_events()

    def _create_status_bar(self):
        self.CreateStatusBar()
        self.status_bar_adapter = StatusBarAdapter(self.GetStatusBar())

    def _create_main_panel(self):
        self.main_panel = MainPanel(self, self.config, self)

    def _create_main_menu_bar(self):
        main_menu_bar = wx.MenuBar()
        main_menu_bar.Append(self._create_file_menu(), _("&File"))
        main_menu_bar.Append(self._create_edit_menu(), _("&Edit"))
        main_menu_bar.Append(self._create_view_menu(), _("&View"))
        main_menu_bar.Append(self._create_timeline_menu(), _("&Timeline"))
        main_menu_bar.Append(self._create_navigate_menu(), _("&Navigate"))
        main_menu_bar.Append(self._create_help_menu(), _("&Help"))
        self._set_shortcuts()
        self.SetMenuBar(main_menu_bar)
        self.update_navigation_menu_items()
        self.enable_disable_menus()

    def _set_shortcuts(self):
        from timelinelib.config.shortcut import ShortcutController
        self.shortcut_controller = ShortcutController(self.config, self.shortcut_items)
        self.shortcut_controller.load_config_settings()

    def _bind_frame_events(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)

    def _create_file_menu(self):
        file_menu = wx.Menu()
        self._create_file_new_menu_item(file_menu)
        self._create_file_open_menu_item(file_menu)
        self._create_file_open_recent_menu(file_menu)
        file_menu.AppendSeparator()
        self._create_file_save_as_menu(file_menu)
        file_menu.AppendSeparator()
        self._create_import_menu_item(file_menu)
        file_menu.AppendSeparator()
        self._create_export_menues(file_menu)
        file_menu.AppendSeparator()
        self._create_file_exit_menu_item(file_menu)
        self._file_menu = file_menu
        return file_menu

    def _create_export_menues(self, file_menu):

        def create_click_handler(plugin, main_frame):
            def event_handler(evt):
                plugin.run(main_frame)
            return event_handler

        submenu = wx.Menu()
        file_menu.Append(wx.ID_ANY, _("Export"), submenu)
        for plugin in factory.get_plugins(EXPORTER):
            mnu = submenu.Append(wx.ID_ANY, plugin.display_name(), plugin.display_name())
            self.menu_controller.add_menu_requiring_timeline(mnu)
            handler = create_click_handler(plugin, self)
            self.Bind(wx.EVT_MENU, handler, mnu)
            method = getattr(plugin, "wxid", None)
            if callable(method):
                self.shortcut_items[method()] = mnu

    def _create_file_new_menu_item(self, file_menu):
        accel = wx.GetStockLabel(wx.ID_NEW, wx.STOCK_WITH_ACCELERATOR | wx.STOCK_WITH_MNEMONIC)
        accel = accel.split("\t", 1)[1]
        file_menu.Append(
            wx.ID_NEW, _("New...") + "\t" + accel, _("Create a new timeline"))
        self.shortcut_items[wx.ID_NEW] = file_menu.FindItemById(wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self._mnu_file_new_on_click, id=wx.ID_NEW)

    def _create_file_open_menu_item(self, file_menu):
        file_menu.Append(
            wx.ID_OPEN, self._add_ellipses_to_menuitem(wx.ID_OPEN),
            _("Open an existing timeline"))
        self.Bind(wx.EVT_MENU, self._mnu_file_open_on_click, id=wx.ID_OPEN)

    def _create_file_open_recent_menu(self, file_menu):
        self.mnu_file_open_recent_submenu = wx.Menu()
        file_menu.Append(wx.ID_ANY, _("Open &Recent"), self.mnu_file_open_recent_submenu)
        self.update_open_recent_submenu()

    def _create_file_save_as_menu(self, file_menu):
        menu = file_menu.Append(wx.ID_SAVEAS, "", _("Save As..."))
        self.shortcut_items[wx.ID_SAVEAS] = menu
        self.Bind(wx.EVT_MENU, self.mnu_file_save_as_on_click, id=wx.ID_SAVEAS)

    def _create_import_menu_item(self, file_menu):
        mnu_file_import = file_menu.Append(
            ID_IMPORT, _("Import events..."), _("Import events..."))
        self.shortcut_items[ID_IMPORT] = mnu_file_import
        self.Bind(wx.EVT_MENU, self._mnu_file_import_on_click, mnu_file_import)
        self.menu_controller.add_menu_requiring_writable_timeline(mnu_file_import)

    def _create_file_exit_menu_item(self, file_menu):
        file_menu.Append(wx.ID_EXIT, "", _("Exit the program"))
        self.shortcut_items[wx.ID_EXIT] = file_menu.FindItemById(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self._mnu_file_exit_on_click, id=wx.ID_EXIT)

    def _create_edit_menu(self):
        from timelinelib.wxgui.dialogs.categoryfinder.view import CategoryFinderDialog

        def create_category_find_dialog():
            return CategoryFinderDialog(self, self.timeline)

        def find(evt):
            self.main_panel.show_searchbar(True)

        def find_categories(evt):
            dialog = create_category_find_dialog()
            dialog.ShowModal()
            dialog.Destroy()

        def select_all(evt):
            self.controller.select_all()

        def preferences(evt):
            def edit_function():
                dialog = PreferencesDialog(self, self.config)
                dialog.ShowModal()
                dialog.Destroy()
            safe_locking(self, edit_function)

        def edit_shortcuts(evt):

            def edit_function():
                dialog = ShortcutsEditorDialog(self, self.shortcut_controller)
                dialog.ShowModal()
                dialog.Destroy()
            safe_locking(self, edit_function)
        cbx = NONE
        items_spec = ((wx.ID_FIND, find, None, cbx),
                      (ID_FIND_CATEGORIES, find_categories, _("Find Categories..."), cbx),
                      None,
                      (ID_SELECT_ALL, select_all, _("Select All Events"), cbx),
                      None,
                      (wx.ID_PREFERENCES, preferences, None, cbx),
                      (ID_EDIT_SHORTCUTS, edit_shortcuts, _("Shortcuts..."), cbx))
        self._edit_menu = self._create_menu(items_spec)
        self._add_edit_menu_items_to_controller(self._edit_menu)
        return self._edit_menu

    def _add_edit_menu_items_to_controller(self, edit_menu):
        find_item = edit_menu.FindItemById(ID_FIND)
        find_categories_item = edit_menu.FindItemById(ID_FIND_CATEGORIES)
        self.menu_controller.add_menu_requiring_timeline(find_item)
        self.menu_controller.add_menu_requiring_timeline(find_categories_item)

    def _create_view_menu(self):

        def sidebar(evt):
            self.config.show_sidebar = evt.IsChecked()
            if evt.IsChecked():
                self.main_panel.show_sidebar()
            else:
                self.main_panel.hide_sidebar()

        def legend(evt):
            self.config.show_legend = evt.IsChecked()

        def balloons(evt):
            self.config.balloon_on_hover = evt.IsChecked()

        def zoomin(evt):
            DrawingAreaProxy(self).zoom_in()

        def zoomout(evt):
            DrawingAreaProxy(self).zoom_out()

        def vert_zoomin(evt):
            DrawingAreaProxy(self).vertical_zoom_in()

        def vert_zoomout(evt):
            DrawingAreaProxy(self).vertical_zoom_out()

        def start_slide_show(evt):
            canvas = self.main_panel.get_timeline_canvas()
            self.controller.start_slide_show(canvas)

        def hide_events_done(evt):
            self.config.hide_events_done = evt.IsChecked()

        items_spec = [self._create_view_toolbar_menu_item,
                      (ID_SIDEBAR, sidebar, _("&Sidebar") + "\tCtrl+I", CHECKBOX),
                      (ID_LEGEND, legend, _("&Legend"), CHECKBOX),
                      None,
                      (ID_BALLOONS, balloons, _("&Balloons on hover"), CHECKBOX),
                      None,
                      (ID_ZOOMIN, zoomin, _("Zoom &In") + "\tCtrl++", NONE),
                      (ID_ZOOMOUT, zoomout, _("Zoom &Out") + "\tCtrl+-", NONE),
                      (ID_VERT_ZOOMIN, vert_zoomin, _("Vertical Zoom &In") + "\tAlt++", NONE),
                      (ID_VERT_ZOOMOUT, vert_zoomout, _("Vertical Zoom &Out") + "\tAlt+-", NONE),
                      None,
                      self._create_view_point_event_alignment_menu,
                      None,
                      self._create_event_box_drawers_menu,
                      None,
                      (ID_PRESENTATION, start_slide_show, _("Start slide show") + "...", NONE),
                      None,
                      (ID_HIDE_DONE, hide_events_done, _("&Hide Events done"), CHECKBOX),
                      ]
        self._view_menu = self._create_menu(items_spec)
        self._check_view_menu_items(self._view_menu)
        self._add_view_menu_items_to_controller(self._view_menu)
        return self._view_menu

    def _create_view_toolbar_menu_item(self, view_menu):
        item = view_menu.Append(wx.ID_ANY, _("Toolbar"), kind=wx.ITEM_CHECK)

        def on_click(event):
            self.config.show_toolbar = event.IsChecked()

        def check_item_corresponding_to_config():
            item.Check(self.config.show_toolbar)

        self.Bind(wx.EVT_MENU, on_click, item)
        self.config.listen_for_any(check_item_corresponding_to_config)
        check_item_corresponding_to_config()

    def _create_event_box_drawers_menu(self, view_menu):

        def create_click_handler(plugin):
            def event_handler(evt):
                self.main_panel.get_timeline_canvas().SetEventBoxDrawer(plugin.run())
                self.config.set_selected_event_box_drawer(plugin.display_name())
            return event_handler

        items = []
        for plugin in factory.get_plugins(EVENTBOX_DRAWER):
            if plugin.display_name() == self.config.get_selected_event_box_drawer():
                items.append((wx.ID_ANY, create_click_handler(plugin), plugin.display_name(), CHECKED_RB))
            else:
                items.append((wx.ID_ANY, create_click_handler(plugin), plugin.display_name(), UNCHECKED_RB))
        sub_menu = self._create_menu(items)
        view_menu.Append(wx.ID_ANY, _("Event appearance"), sub_menu)

    def _create_view_point_event_alignment_menu(self, view_menu):
        sub_menu = wx.Menu()
        left_item = sub_menu.Append(wx.ID_ANY, _("Left"), kind=wx.ITEM_RADIO)
        center_item = sub_menu.Append(wx.ID_ANY, _("Center"), kind=wx.ITEM_RADIO)
        view_menu.Append(wx.ID_ANY, _("Point event alignment"), sub_menu)

        def on_first_tool_click(event):
            self.config.draw_point_events_to_right = True

        def on_second_tool_click(event):
            self.config.draw_point_events_to_right = False

        def check_item_corresponding_to_config():
            if self.config.draw_point_events_to_right:
                left_item.Check()
            else:
                center_item.Check()

        self.Bind(wx.EVT_MENU, on_first_tool_click, left_item)
        self.Bind(wx.EVT_MENU, on_second_tool_click, center_item)
        self.config.listen_for_any(check_item_corresponding_to_config)
        check_item_corresponding_to_config()

    def _check_view_menu_items(self, view_menu):

        def item(item_id):
            return view_menu.FindItemById(item_id)

        item(ID_SIDEBAR).Check(self.config.show_sidebar)
        item(ID_LEGEND).Check(self.config.show_legend)
        item(ID_BALLOONS).Check(self.config.balloon_on_hover)
        item(ID_HIDE_DONE).Check(self.config.hide_events_done)

    def _add_view_menu_items_to_controller(self, view_menu):
        sidebar_item = view_menu.FindItemById(ID_SIDEBAR)
        legend_item = view_menu.FindItemById(ID_LEGEND)
        balloons_item = view_menu.FindItemById(ID_BALLOONS)
        self.menu_controller.add_menu_requiring_visible_timeline_view(sidebar_item)
        self.menu_controller.add_menu_requiring_timeline(legend_item)
        self.menu_controller.add_menu_requiring_timeline(balloons_item)
        self.menu_controller.add_menu_requiring_timeline(view_menu.FindItemById(ID_ZOOMIN))
        self.menu_controller.add_menu_requiring_timeline(view_menu.FindItemById(ID_ZOOMOUT))
        self.menu_controller.add_menu_requiring_timeline(view_menu.FindItemById(ID_VERT_ZOOMIN))
        self.menu_controller.add_menu_requiring_timeline(view_menu.FindItemById(ID_VERT_ZOOMOUT))

    def set_category_on_selected(self):

        def edit_function():
            self._set_category_to_selected_events()

        safe_locking(self, edit_function)

    def _create_timeline_menu(self):

        def create_event(evt):
            open_create_event_editor(self, self, self.config, self.timeline)

        def edit_event(evt):
            try:
                event_id = self.main_panel.get_id_of_first_selected_event()
                event = self.timeline.find_event_with_id(event_id)
            except IndexError:
                # No event selected so do nothing!
                return
            self.main_panel.open_event_editor(event)

        def duplicate_event(evt):
            try:
                event_id = self.main_panel.get_id_of_first_selected_event()
                event = self.timeline.find_event_with_id(event_id)
            except IndexError:
                # No event selected so do nothing!
                return
            open_duplicate_event_dialog_for_event(self, self, self.timeline, event)

        def create_milestone(evt):
            open_milestone_editor_for(self, self, self.config, self.timeline)

        def set_categoryon_selected(evt):

            def edit_function():
                self._set_category_to_selected_events()
            safe_locking(self, edit_function)

        def measure_distance(evt):
            self._measure_distance_between_events()

        def set_category_on_without(evt):
            def edit_function():
                self._set_category()
            safe_locking(self, edit_function)

        def edit_eras(evt):
            def edit_function():
                self._edit_eras()
            safe_locking(self, edit_function)

        def set_readonly(evt):
            self.controller.set_timeline_in_readonly_mode()

        def undo(evt):
            safe_locking(self, self.timeline.undo)

        def redo(evt):
            safe_locking(self, self.timeline.redo)

        def compress(evt):
            safe_locking(self, self.timeline.compress)

        def move_up_handler(event):
            self.main_panel.timeline_panel.move_selected_event_up()

        def move_down_handler(event):
            self.main_panel.timeline_panel.move_selected_event_down()

        cbx = NONE
        items_spec = ((ID_CREATE_EVENT, create_event, _("Create &Event..."), cbx),
                      (ID_EDIT_EVENT, edit_event, _("&Edit Selected Event..."), cbx),
                      (ID_DUPLICATE_EVENT, duplicate_event, _("&Duplicate Selected Event..."), cbx),
                      (ID_SET_CATEGORY_ON_SELECTED, set_categoryon_selected, _("Set Category on Selected Events..."), cbx),
                      (ID_MOVE_EVENT_UP, move_up_handler, _("Move event up") + "\tAlt+Up", cbx),
                      (ID_MOVE_EVENT_DOWN, move_down_handler, _("Move event down") + "\tAlt+Down", cbx),
                      None,
                      (ID_CREATE_MILESTONE, create_milestone, _("Create &Milestone..."), cbx),
                      None,
                      (ID_COMPRESS, compress, _("&Compress timeline Events"), cbx),
                      None,
                      (ID_MEASURE_DISTANCE, measure_distance, _("&Measure Distance between two Events..."), cbx),
                      None,
                      (ID_SET_CATEGORY_ON_WITHOUT, set_category_on_without,
                       _("Set Category on events &without category..."), cbx),
                      None,
                      (ID_EDIT_ERAS, edit_eras, _("Edit Era's..."), cbx),
                      None,
                      (ID_SET_READONLY, set_readonly, _("&Read Only"), cbx),
                      None,
                      (ID_UNDO, undo, _("&Undo") + "\tCtrl+Z", cbx),
                      (ID_REDO, redo, _("&Redo") + "\tAlt+Z", cbx))
        self._timeline_menu = self._create_menu(items_spec)
        self._add_timeline_menu_items_to_controller(self._timeline_menu)
        return self._timeline_menu

    def _add_timeline_menu_items_to_controller(self, menu):
        self._add_to_controller_requiring_writeable_timeline(menu, ID_CREATE_EVENT)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_EDIT_EVENT)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_CREATE_MILESTONE)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_DUPLICATE_EVENT)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_SET_CATEGORY_ON_SELECTED)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_MEASURE_DISTANCE)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_SET_CATEGORY_ON_WITHOUT)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_SET_READONLY)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_EDIT_ERAS)
        self._add_to_controller_requiring_writeable_timeline(menu, ID_COMPRESS)

    def _add_to_controller_requiring_writeable_timeline(self, menu, item_id):
        mnu_item = menu.FindItemById(item_id)
        self.menu_controller.add_menu_requiring_writable_timeline(mnu_item)

    def _create_navigate_menu(self):

        def find_first(evt):
            event = self.timeline.get_first_event()
            if event:
                start = event.get_start_time()
                delta = self.main_panel.get_displayed_period_delta()
                end = start + delta
                margin_delta = delta / 24
                self.main_panel.Navigate(lambda tp: tp.update(start, end, -margin_delta))

        def find_last(evt):
            event = self.timeline.get_last_event()
            if event:
                end = event.get_end_time()
                delta = self.main_panel.get_displayed_period_delta()
                try:
                    start = end - delta
                except ValueError:
                    start = self.timeline.get_time_type().get_min_time()
                margin_delta = delta / 24
                self.main_panel.Navigate(lambda tp: tp.update(start, end, end_delta=margin_delta))

        def restore_time_period(evt):
            if self.prev_time_period:
                self.main_panel.Navigate(lambda tp: self.prev_time_period)

        def fit_all(evt):
            self._fit_all_events()

        cbx = NONE
        items_spec = (None,
                      (ID_FIND_FIRST, find_first, _("Find &First Event"), cbx),
                      (ID_FIND_LAST, find_last, _("Find &Last Event"), cbx),
                      (ID_FIT_ALL, fit_all, _("Fit &All Events"), cbx),
                      None,
                      (ID_RESTORE_TIME_PERIOD, restore_time_period, _("Go to previous time period"), cbx),)
        self._navigation_menu_items = []
        self._navigation_functions_by_menu_item_id = {}
        self.update_navigation_menu_items()
        self._navigate_menu = self._create_menu(items_spec)
        self._add_navigate_menu_items_to_controller(self._navigate_menu)
        return self._navigate_menu

    def _add_navigate_menu_items_to_controller(self, menu):
        self._add_to_controller_requiring_timeline(menu, ID_FIND_FIRST)
        self._add_to_controller_requiring_timeline(menu, ID_FIND_LAST)
        self._add_to_controller_requiring_timeline(menu, ID_FIT_ALL)

    def _add_to_controller_requiring_timeline(self, menu, item_id):
        mnu_item = menu.FindItemById(item_id)
        self.menu_controller.add_menu_requiring_timeline(mnu_item)

    def _create_help_menu(self):

        def feedback(e):
            show_feedback_dialog(parent=None, info="", subject=_("Feedback"), body="")

        cbx = NONE
        items_spec = [(wx.ID_HELP, self.help_browser.show_contents_page, _("&Contents") + "\tF1", cbx),
                      None,
                      (ID_TUTORIAL, self.controller.open_gregorian_tutorial_timeline, _("Getting started &tutorial"), cbx),
                      (ID_NUMTUTORIAL, self.controller.open_numeric_tutorial_timeline, _("Getting started numeric &tutorial"), cbx),
                      None,
                      (ID_FEEDBACK, feedback, _("Give &Feedback..."), cbx),
                      (ID_CONTACT, self.help_browser.show_contact_page, _("Co&ntact"), cbx),
                      None,
                      (ID_SYSTEM_INFO, show_system_info_dialog, _("System information"), cbx),
                      None,
                      (wx.ID_ABOUT, display_about_dialog, None, cbx)]
        self._help_menu = self._create_menu(items_spec)
        return self._help_menu

    def _create_menu(self, items_spec):
        menu = wx.Menu()
        for item in items_spec:
            if item is not None:
                self._create_menu_item(menu, item)
            else:
                menu.AppendSeparator()
        return menu

    def _create_menu_item(self, menu, item_spec):
        if isinstance(item_spec, collections.Callable):
            item_spec(menu)
        else:
            item_id, handler, label, checkbox = item_spec
            if label is not None:
                if checkbox == CHECKBOX:
                    item = menu.Append(item_id, label, kind=wx.ITEM_CHECK)
                elif checkbox == CHECKED_RB:
                    item = menu.Append(item_id, label, kind=wx.ITEM_RADIO)
                    item.Check(True)
                elif checkbox == UNCHECKED_RB:
                    item = menu.Append(item_id, label, kind=wx.ITEM_RADIO)
                else:
                    if label is not None:
                        item = menu.Append(item_id, label)
                    else:
                        item = menu.Append(item_id)
            else:
                item = menu.Append(item_id)
            self.shortcut_items[item_id] = menu.FindItemById(item_id)
            self.Bind(wx.EVT_MENU, handler, item)

    def _mnu_file_new_on_click(self, event):
        items = [
            {
                "text": _("Gregorian"),
                "description": _("This creates a timeline using the standard calendar."),
                "create_fn": self._create_new_timeline,
            },
            {
                "text": _("Numeric"),
                "description": _("This creates a timeline that has numbers on the x-axis instead of dates."),
                "create_fn": self._create_new_numeric_timeline,
            },
            {
                "text": _("Directory"),
                "description": _("This creates a timeline where the modification date of files in a directory are shown as events."),
                "create_fn": self._create_new_dir_timeline,
            },
            {
                "text": _("Bosparanian"),
                "description": _("This creates a timeline using the fictuous Bosparanian calendar from the German pen-and-paper RPG \"The Dark Eye\" (\"Das schwarze Auge\", DSA)."),
                "create_fn": self._create_new_bosparanian_timeline,
            },
            {
                "text": _("Pharaonic"),
                "description": _("This creates a timeline using the ancient egypt pharaonic calendar"),
                "create_fn": self._create_new_pharaonic_timeline,
            },
            {
                "text": _("Coptic"),
                "description": _("This creates a timeline using the coptic calendar"),
                "create_fn": self._create_new_coptic_timeline,
            },
        ]
        dialog = FileNewDialog(self, items)
        if dialog.ShowModal() == wx.ID_OK:
            dialog.GetSelection()["create_fn"]()
        dialog.Destroy()

    def _mnu_file_open_on_click(self, event):
        self._open_existing_timeline()

    def mnu_file_save_as_on_click(self, event):
        if self.timeline is not None:
            self._save_as()

    def _mnu_file_import_on_click(self, menu):
        def open_import_dialog():
            dialog = ImportEventsDialog(self.timeline, self)
            dialog.ShowModal()
            dialog.Destroy()
        safe_locking(self, open_import_dialog)

    def _mnu_file_exit_on_click(self, evt):
        self.Close()

    def _add_ellipses_to_menuitem(self, wx_id):
        plain = wx.GetStockLabel(wx_id, wx.STOCK_WITH_ACCELERATOR | wx.STOCK_WITH_MNEMONIC)
        # format of plain 'xxx[\tyyy]', example '&New\tCtrl+N'
        tab_index = plain.find("\t")
        if tab_index != -1:
            return plain[:tab_index] + "..." + plain[tab_index:]
        return plain + "..."
