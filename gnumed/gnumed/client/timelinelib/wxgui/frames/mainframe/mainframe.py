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

import wx.lib.newevent

from timelinelib.canvas.data import TimePeriod
from timelinelib.config.dotfile import read_config
from timelinelib.config.paths import ICONS_DIR
from timelinelib.config.paths import LOCALE_DIR
from timelinelib.dataexport.timelinexml import export_db_to_timeline_xml
from timelinelib.db import db_open
from timelinelib.features.experimental.experimentalfeatures import ExperimentalFeatures
from timelinelib.meta.about import APPLICATION_NAME
from timelinelib.calendar.bosparanian.timetype import BosparanianTimeType
from timelinelib.calendar.num.timetype import NumTimeType
from timelinelib.utils import ex_msg
from timelinelib.wxgui.dialogs.changenowdate.view import ChangeNowDateDialog
from timelinelib.wxgui.dialogs.eraseditor.view import ErasEditorDialog
from timelinelib.wxgui.dialogs.setcategory.view import SetCategoryDialog
from timelinelib.wxgui.dialogs.timeeditor.view import TimeEditorDialog
from timelinelib.wxgui.frames.helpbrowserframe.helpbrowserframe import HelpBrowserFrame
from timelinelib.wxgui.frames.mainframe.mainframecontroller import LockedException
from timelinelib.wxgui.frames.mainframe.mainframecontroller import MainFrameController
from timelinelib.wxgui.timer import TimelineTimer
from timelinelib.wxgui.utils import display_categories_editor_moved_message
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import display_information_message
from timelinelib.wxgui.utils import WildcardHelper
import timelinelib.wxgui.frames.mainframe.guicreator as guic
from timelinelib.wxgui.frames.mainframe.controllerapi import MainFrameApiUsedByController
from timelinelib.wxgui.frames.mainframe.alertcontroller import AlertController
from timelinelib.wxgui.frames.mainframe.menucontroller import MenuController
from timelinelib.calendar.coptic.timetype import CopticTimeType
from timelinelib.calendar.pharaonic.timetype import PharaonicTimeType

CatsViewChangedEvent, EVT_CATS_VIEW_CHANGED = wx.lib.newevent.NewCommandEvent()


class MainFrame(wx.Frame, guic.GuiCreator, MainFrameApiUsedByController):

    def __init__(self, application_arguments):
        self.config = read_config(application_arguments.get_config_file_path())
        wx.Frame.__init__(self, None, size=self.config.get_window_size(),
                          pos=self.config.get_window_pos(),
                          style=wx.DEFAULT_FRAME_STYLE, name="main_frame")
        self.Bind(EVT_CATS_VIEW_CHANGED, self._on_cats_view_changed)
        # To enable translations of wx stock items.
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.locale.AddCatalogLookupPathPrefix(LOCALE_DIR)
        self.locale.AddCatalog("wxstd")
        self.help_browser = HelpBrowserFrame(self)
        self.controller = MainFrameController(self, db_open, self.config)
        self.menu_controller = MenuController()
        self._set_initial_values_to_member_variables()
        self._create_print_data()
        self._set_experimental_features()
        self._create_gui()
        self.Maximize(self.config.window_maximized)
        self.SetTitle(APPLICATION_NAME)
        self.SetIcons(self._load_icon_bundle())
        self.main_panel.show_welcome_panel()
        self.enable_disable_menus()
        self.controller.on_started(application_arguments)
        self._create_and_start_timer()
        self.prev_time_period = None

    def DisplayErrorMessage(self, message):
        display_error_message(message, parent=self)

    def DisplayStatus(self, message):
        self.status_bar_adapter.set_text(message)

    # API:s used by time types
    def week_starts_on_monday(self):
        return self.controller.week_starts_on_monday()

    def display_time_editor_dialog(self, time_type, initial_time,
                                   handle_new_time_fn, title):
        dialog = TimeEditorDialog(self, self.config, time_type, initial_time, title)
        dialog.ShowModal()
        result = dialog.GetReturnCode()
        if result == wx.ID_OK:
            handle_new_time_fn(dialog.GetTime())
        dialog.Destroy()

    def display_now_date_editor_dialog(self, handle_new_time_fn, title):
        dialog = ChangeNowDateDialog(self, self.config, self.timeline, handle_new_time_fn, title)
        dialog.Show()

    def save_time_period(self):
        self.prev_time_period = self.main_panel.get_time_period()

    # Concurrent editing
    def ok_to_edit(self):
        try:
            return self.controller.ok_to_edit()
        except LockedException:
            return False

    def get_lockfile_path(self):
        return self.controller._get_lockpath()

    def edit_ends(self):
        self.controller.edit_ends()

    def get_view_properties(self, ):
        return self.main_panel.get_view_properties()

    def _on_cats_view_changed(self, evt):
        self.main_panel.get_view_properties().change_view_cats_individually(evt.GetClientData())

    # Creation process methods
    def _set_initial_values_to_member_variables(self):
        self.timeline = None
        self.timeline_wildcard_helper = WildcardHelper(
            _("Timeline files"), ["timeline", "ics"])
        self.images_svg_wildcard_helper = WildcardHelper(
            _("SVG files"), ["svg"])

    def _create_print_data(self):
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printData.SetOrientation(wx.LANDSCAPE)

    def _create_and_start_timer(self):
        self.alert_dialog_open = False
        self.timer = TimelineTimer(self)
        self.timer.register(self._timer_tick)
        self.timer.start(10000)

    def _timer_tick(self, evt):
        self._handle_event_alerts()

    def _set_experimental_features(self):
        ExperimentalFeatures().set_active_state_on_all_features_from_config_string(self.config.experimental_features)

    def _load_icon_bundle(self):
        bundle = wx.IconBundle()
        for size in ["16", "32", "48"]:
            iconpath = os.path.join(ICONS_DIR, "%s.png" % size)
            icon = wx.Icon(wx.Bitmap(wx.Image(iconpath)))
            bundle.AddIcon(icon)
        return bundle

    # File Menu action handlers
    def _create_new_timeline(self, timetype=None):
        path = self._get_file_path()
        if path is not None:
            self.controller.open_timeline(path, timetype)

    def _create_new_bosparanian_timeline(self):
        self._create_new_timeline(BosparanianTimeType())
    
    def _create_new_coptic_timeline(self):
        self._create_new_timeline(CopticTimeType())
            
    def _create_new_pharaonic_timeline(self):
        self._create_new_timeline(PharaonicTimeType())
        
    def _create_new_numeric_timeline(self):
        self._create_new_timeline(NumTimeType())

    def _get_file_path(self):
        path = None
        wildcard = self.timeline_wildcard_helper.wildcard_string()
        dialog = wx.FileDialog(self, message=_("Create Timeline"),
                               wildcard=wildcard, style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path = self.timeline_wildcard_helper.get_path(dialog)
            if os.path.exists(path):
                msg_first_part = _("The specified timeline already exists.")
                msg_second_part = _("Opening timeline instead of creating new.")
                wx.MessageBox("%s\n\n%s" % (msg_first_part, msg_second_part),
                              _("Information"),
                              wx.OK | wx.ICON_INFORMATION, self)
        dialog.Destroy()
        return path

    def _create_new_dir_timeline(self):
        dialog = wx.DirDialog(self, message=_("Create Timeline"))
        if dialog.ShowModal() == wx.ID_OK:
            self.controller.open_timeline(dialog.GetPath())
        dialog.Destroy()

    def _open_existing_timeline(self):
        directory = ""
        if self.timeline is not None:
            directory = os.path.dirname(self.timeline.path)
        wildcard = self.timeline_wildcard_helper.wildcard_string()
        dialog = wx.FileDialog(self, message=_("Open Timeline"),
                               defaultDir=directory,
                               wildcard=wildcard, style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.controller.open_timeline(dialog.GetPath())
        dialog.Destroy()

    def _save_as(self):
        new_timeline_path = self._get_new_timeline_path_from_user()
        self._save_timeline_to_new_path(new_timeline_path)

    def _get_new_timeline_path_from_user(self):
        defaultDir = os.path.dirname(self.timeline.path)
        wildcard_helper = WildcardHelper(_("Timeline files"), ["timeline"])
        wildcard = wildcard_helper.wildcard_string()
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        message = _("Save Timeline As")
        dialog = wx.FileDialog(self, message=message, defaultDir=defaultDir,
                               wildcard=wildcard, style=style)
        if dialog.ShowModal() == wx.ID_OK:
            new_timeline_path = wildcard_helper.get_path(dialog)
        else:
            new_timeline_path = None
        dialog.Destroy()
        return new_timeline_path

    def _save_timeline_to_new_path(self, new_timeline_path):
        if new_timeline_path is not None:
            assert new_timeline_path.endswith(".timeline")
            export_db_to_timeline_xml(self.timeline, new_timeline_path)
            self.controller.open_timeline(new_timeline_path)

    def _window_on_close(self, event):
        self.timer.stop()
        self._save_application_config()
        try:
            if self.ok_to_edit():
                self.save_current_timeline_data()
        finally:
            self.edit_ends()
        self.Destroy()

    def _save_application_config(self):
        self.config.set_window_size(self.GetSize())
        self.config.set_window_pos(self.GetPosition())
        self.config.window_maximized = self.IsMaximized()
        self.config.sidebar_width = self.main_panel.get_sidebar_width()
        try:
            self.config.write()
        except IOError as ex:
            friendly = _("Unable to write configuration file.")
            msg = "%s\n\n%s" % (friendly, ex_msg(ex))
            display_error_message(msg, self)

    def save_current_timeline_data(self):
        if self.timeline:
            self.main_panel.save_view_properties(self.timeline)

    # Timeline Menu action handlers
    def _measure_distance_between_events(self):
        event1, event2 = self._get_selected_events()
        self._display_distance(event1.distance_to(event2))

    def _get_selected_events(self):
        event_id_1, event_id_2 = self.main_panel.get_ids_of_two_first_selected_events()
        event1 = self.timeline.find_event_with_id(event_id_1)
        event2 = self.timeline.find_event_with_id(event_id_2)
        return event1, event2

    def _display_distance(self, distance):
        caption = _("Distance between selected events")
        if distance is None:
            distance_text = _("Events are overlapping or distance is 0")
        else:
            distance_text = self.timeline.get_time_type().format_delta(distance)
        display_information_message(caption, distance_text)

    def _set_category(self):
        dialog = SetCategoryDialog(self, self.timeline)
        dialog.ShowModal()
        dialog.Destroy()
        self.main_panel.redraw_timeline()

    def _set_category_to_selected_events(self):
        selected_event_ids = self.main_panel.get_selected_event_ids()
        dialog = SetCategoryDialog(self, self.timeline, selected_event_ids)
        dialog.ShowModal()
        dialog.Destroy()

    def _edit_categories(self):
        display_categories_editor_moved_message(self)

    def _edit_eras(self):
        dialog = ErasEditorDialog(self, self.timeline, self.config)
        dialog.ShowModal()
        dialog.Destroy()
        self.main_panel.redraw_timeline()

    def _fit_all_events(self):
        all_period = self._period_for_all_visible_events()
        if all_period is None:
            return
        if all_period.is_period():
            self.main_panel.Navigate(lambda tp: tp.update(all_period.start_time, all_period.end_time))
        else:
            self.main_panel.Navigate(lambda tp: tp.center(all_period.mean_time()))

    def _period_for_all_visible_events(self):
        try:
            visible_events = self._all_visible_events()
            if len(visible_events) > 0:
                start = self._first_time(visible_events)
                end = self._last_time(visible_events)
                return TimePeriod(start, end).zoom(-1)
            else:
                return None
        except ValueError as ex:
            display_error_message(str(ex))
        return None

    def _all_visible_events(self):
        all_events = self.timeline.get_all_events()
        return self.main_panel.get_visible_events(all_events)

    def _first_time(self, events):
        start_time = lambda event: event.get_start_time()
        return start_time(min(events, key=start_time))

    def _last_time(self, events):
        end_time = lambda event: event.get_end_time()
        return end_time(max(events, key=end_time))

    def get_export_periods(self):
        events = self._all_visible_events()
        first_time = self._first_time(events)
        last_time = self._last_time(events)
        return self.main_panel.get_export_periods(first_time, last_time)

    # Timer event handlers
    def _handle_event_alerts(self):
        if self.timeline is None:
            return
        if self.alert_dialog_open:
            return
        self._display_events_alerts()
        self.alert_dialog_open = False

    def _display_events_alerts(self):
        self.alert_dialog_open = True
        all_events = self.timeline.get_all_events()
        AlertController(self).display_events_alerts(all_events, self.timeline.get_time_type())
