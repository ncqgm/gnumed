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


import os
import webbrowser

import wx

from timelinelib.canvas import EVT_DIVIDER_POSITION_CHANGED
from timelinelib.canvas import EVT_TIMELINE_REDRAWN
from timelinelib.db.utils import safe_locking
from timelinelib.general.encodings import to_unicode
from timelinelib.general.observer import Listener
from timelinelib.wxgui.components.maincanvas.createperiodeventbydrag import CreatePeriodEventByDragInputHandler
from timelinelib.wxgui.components.maincanvas.maincanvas import MainCanvas
from timelinelib.wxgui.components.maincanvas.movebydrag import MoveByDragInputHandler
from timelinelib.wxgui.components.maincanvas.noop import NoOpInputHandler
from timelinelib.wxgui.components.maincanvas.resizebydrag import ResizeByDragInputHandler
from timelinelib.wxgui.components.maincanvas.scrollbydrag import ScrollByDragInputHandler
from timelinelib.wxgui.components.maincanvas.zoombydrag import ZoomByDragInputHandler
from timelinelib.wxgui.components.maincanvas.selectevents import SelectEventsInputHandler
from timelinelib.wxgui.components.messagebar import MessageBar
from timelinelib.wxgui.components.sidebar import Sidebar
from timelinelib.wxgui.dialogs.duplicateevent.view import open_duplicate_event_dialog_for_event
from timelinelib.wxgui.dialogs.editevent.view import open_create_event_editor
from timelinelib.wxgui.dialogs.editevent.view import open_event_editor_for
from timelinelib.wxgui.dialogs.milestone.view import open_milestone_editor_for
from timelinelib.wxgui.frames.mainframe.toolbar import ToolbarCreator
from timelinelib.wxgui.utils import _ask_question
from timelinelib.config.paths import ICONS_DIR
from timelinelib.wxgui.cursor import Cursor


LEFT_RIGHT_SCROLL_FACTOR = 1 / 200.0


class TimelinePanelGuiCreator(wx.Panel):

    def __init__(self, parent):
        self.sidebar_width = self.config.sidebar_width
        wx.Panel.__init__(self, parent)
        self._create_gui()

    def BitmapFromIcon(self, icon):
        return wx.Bitmap(os.path.join(ICONS_DIR, icon))

    def CreateToolbar(self):
        return wx.ToolBar(self, wx.ID_ANY)

    def _create_gui(self):
        self._create_toolbar()
        self._create_warning_bar()
        self._create_divider_line_slider()
        self._create_splitter()
        self._layout_components()

    def _create_toolbar(self):
        self.tool_bar = ToolbarCreator(self, self.config).create()

    def _create_warning_bar(self):
        self.message_bar = MessageBar(self)

    def _create_divider_line_slider(self):

        def on_slider(evt):
            self.config.divider_line_slider_pos = evt.GetPosition()

        style = wx.SL_LEFT | wx.SL_VERTICAL
        self.divider_line_slider = wx.Slider(self, size=(20, -1), style=style)
        self.Bind(wx.EVT_SCROLL, on_slider, self.divider_line_slider)

        self.divider_line_slider.Bind(wx.EVT_SLIDER, self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU, self._slider_on_context_menu)

    def _slider_on_slider(self, evt):
        self.timeline_canvas.SetDividerPosition(self.divider_line_slider.GetValue())

    def _slider_on_context_menu(self, evt):
        menu = wx.Menu()
        menu_item = wx.MenuItem(menu, wx.NewId(), _("Center"))
        self.Bind(wx.EVT_MENU, self._context_menu_on_menu_center, id=menu_item.GetId())
        menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_menu_center(self, evt):
        self.timeline_canvas.SetDividerPosition(50)

    def _create_splitter(self):
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(50)
        self.Bind(
            wx.EVT_SPLITTER_SASH_POS_CHANGED,
            self._splitter_on_splitter_sash_pos_changed, self.splitter)
        self._create_sidebar()
        self._create_timeline_canvas()
        self.splitter.Initialize(self.timeline_canvas)

    def _splitter_on_splitter_sash_pos_changed(self, event):
        if self.IsShown():
            self.sidebar_width = self.splitter.GetSashPosition()

    def _create_sidebar(self):
        self.sidebar = Sidebar(self._edit_controller, self.splitter)

    def _create_timeline_canvas(self):
        self.timeline_canvas = MainCanvas(
            self.splitter, self._edit_controller, self.status_bar_adapter)
        self.timeline_canvas.Bind(
            wx.EVT_LEFT_DCLICK,
            self._timeline_canvas_on_double_clicked
        )
        self.timeline_canvas.Bind(
            wx.EVT_RIGHT_DOWN,
            self._timeline_canvas_on_right_down
        )
        self.timeline_canvas.Bind(
            wx.EVT_KEY_DOWN,
            self._timeline_canvas_on_key_down
        )
        self.timeline_canvas.Bind(
            EVT_DIVIDER_POSITION_CHANGED,
            self._timeline_canvas_on_divider_position_changed
        )
        self.timeline_canvas.Bind(
            EVT_TIMELINE_REDRAWN,
            self._timeline_canvas_on_timeline_redrawn
        )
        self.timeline_canvas.SetDividerPosition(self.config.divider_line_slider_pos)
        self.timeline_canvas.SetEventBoxDrawer(self._get_saved_event_box_drawer())
        self.timeline_canvas.SetInputHandler(NoOpInputHandler(
            InputHandlerState(
                self.timeline_canvas, self.status_bar_adapter,
                self._edit_controller, self.config),
            self.timeline_canvas))

        def update_appearance():
            appearance = self.timeline_canvas.GetAppearance()
            appearance.set_legend_visible(self.config.show_legend)
            appearance.set_balloons_visible(self.config.balloon_on_hover)
            appearance.set_hide_events_done(self.config.hide_events_done)
            appearance.set_minor_strip_divider_line_colour(self.config.minor_strip_divider_line_colour)
            appearance.set_major_strip_divider_line_colour(self.config.major_strip_divider_line_colour)
            appearance.set_now_line_colour(self.config.now_line_colour)
            appearance.set_weekend_colour(self.config.weekend_colour)
            appearance.set_bg_colour(self.config.bg_colour)
            appearance.set_colorize_weekends(self.config.colorize_weekends)
            appearance.set_draw_period_events_to_right(self.config.draw_point_events_to_right)
            appearance.set_text_below_icon(self.config.text_below_icon)
            appearance.set_minor_strip_font(self.config.minor_strip_font)
            appearance.set_major_strip_font(self.config.major_strip_font)
            appearance.set_balloon_font(self.config.balloon_font)
            appearance.set_legend_font(self.config.legend_font)
            appearance.set_center_event_texts(self.config.center_event_texts)
            appearance.set_never_show_period_events_as_point_events(self.config.never_show_period_events_as_point_events)
            appearance.set_week_start(self.config.get_week_start())
            appearance.set_use_inertial_scrolling(self.config.use_inertial_scrolling)
            appearance.set_fuzzy_icon(self.config.fuzzy_icon)
            appearance.set_locked_icon(self.config.locked_icon)
            appearance.set_hyperlink_icon(self.config.hyperlink_icon)
            appearance.set_vertical_space_between_events(self.config.vertical_space_between_events)
            appearance.set_skip_s_in_decade_text(self.config.skip_s_in_decade_text)
            appearance.set_display_checkmark_on_events_done(self.config.display_checkmark_on_events_done)
            appearance.set_never_use_time(self.config.never_use_time)
            appearance.set_legend_pos(self.config.legend_pos)
        self.config.listen_for_any(update_appearance)
        update_appearance()

    def _get_saved_event_box_drawer(self):
        from timelinelib.plugin import factory
        from timelinelib.plugin.factory import EVENTBOX_DRAWER
        from timelinelib.plugin.plugins.eventboxdrawers.defaulteventboxdrawer import DefaultEventBoxDrawer
        plugin = factory.get_plugin(EVENTBOX_DRAWER, self.config.get_selected_event_box_drawer()) or DefaultEventBoxDrawer()
        return plugin.run()

    def _timeline_canvas_on_double_clicked(self, event):
        if self.timeline_canvas.GetDb().is_read_only():
            return
        cursor = Cursor(event.GetX(), event.GetY())
        timeline_event = self.timeline_canvas.GetEventAt(cursor)
        time = self.timeline_canvas.GetTimeAt(cursor.x)
        if timeline_event is not None:
            if timeline_event.is_milestone():
                self.open_milestone_editor(timeline_event)
            else:
                self.open_event_editor(timeline_event)
        else:
            open_create_event_editor(
                self._edit_controller,
                self,
                self.config,
                self.timeline_canvas.GetDb(),
                time,
                time)
        event.Skip()

    def _timeline_canvas_on_right_down(self, event):
        cursor = Cursor(event.GetX(), event.GetY())
        timeline_event = self.timeline_canvas.GetEventAt(cursor)
        if timeline_event is not None and not self.timeline_canvas.GetDb().is_read_only():
            self.timeline_canvas.SetEventSelected(timeline_event, True)
            self._display_event_context_menu()
        else:
            display_timeline_context_menu = getattr(self.main_frame, "display_timeline_context_menu", None)
            if callable(display_timeline_context_menu):
                display_timeline_context_menu()
        event.Skip()

    def _timeline_canvas_on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            self._delete_selected_events()
        elif event.GetKeyCode() == wx.WXK_UP:
            self.move_selected_event_up()
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.move_selected_event_down()
        elif event.AltDown() and event.GetKeyCode() in (wx.WXK_RIGHT, wx.WXK_NUMPAD_RIGHT):
            self.timeline_canvas.Scroll(LEFT_RIGHT_SCROLL_FACTOR)
        elif event.AltDown() and event.GetKeyCode() in (wx.WXK_LEFT, wx.WXK_NUMPAD_LEFT):
            self.timeline_canvas.Scroll(-LEFT_RIGHT_SCROLL_FACTOR)
        else:
            event.Skip()

    def move_selected_event_up(self):
        self._try_move_event_vertically(True)

    def move_selected_event_down(self):
        self._try_move_event_vertically(False)

    def _try_move_event_vertically(self, up=True):
        event = self.timeline_canvas.GetSelectedEvent()
        if event is not None:
            self._move_event_vertically(event, up)

    def _move_event_vertically(self, event, up=True):
        def edit_function():
            (
                overlapping_event,
                direction
            ) = self.timeline_canvas.GetClosestOverlappingEvent(event, up=up)
            if overlapping_event is None:
                pass
            elif direction > 0:
                self.timeline_canvas.GetDb().place_event_after_event(
                    event,
                    overlapping_event
                )
            else:
                self.timeline_canvas.GetDb().place_event_before_event(
                    event,
                    overlapping_event
                )
            # GetClosestOverlappingEvent inflates rectangles, so subsequent
            # calls do calculations on incorrect rectangles. A redraw
            # recalculates all rectangles.
            self.redraw_timeline()
        safe_locking(self._edit_controller, edit_function)

    def _display_event_context_menu(self):
        menu_definitions = [
            (_("Delete"), self._context_menu_on_delete_event, None),
        ]
        nbr_of_selected_events = len(self.timeline_canvas.GetSelectedEvents())
        if nbr_of_selected_events == 1:
            menu_definitions.insert(0, (_("Edit"), self._context_menu_on_edit_event, None))
            menu_definitions.insert(1, (_("Duplicate..."), self._context_menu_on_duplicate_event, None))
        menu_definitions.append((_("Mark Event as Done"), self._context_menu_on_done_event, None))
        menu_definitions.append((_("Select Category..."), self._context_menu_on_select_category, None))
        if nbr_of_selected_events == 1 and self.timeline_canvas.GetSelectedEvent().has_data():
            menu_definitions.append((_("Sticky Balloon"), self._context_menu_on_sticky_balloon_event, None))
        if nbr_of_selected_events == 1:
            hyperlinks = self.timeline_canvas.GetSelectedEvent().get_data("hyperlink")
            if hyperlinks is not None:
                imp = wx.Menu()
                menuid = 0
                for hyperlink in hyperlinks.split(";"):
                    imp.Append(menuid, hyperlink)
                    menuid += 1
                menu_definitions.append((_("Goto URL"), self._context_menu_on_goto_hyperlink_event, imp))
        menu = wx.Menu()
        for menu_definition in menu_definitions:
            text, method, imp = menu_definition
            menu_item = wx.MenuItem(menu, wx.NewId(), text)
            if imp is not None:
                for menu_item in imp.GetMenuItems():
                    self.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
                menu.AppendMenu(wx.ID_ANY, text, imp)
            else:
                self.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
                menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_delete_event(self, evt):
        self._delete_selected_events()

    def _delete_selected_events(self):
        selected_events = self.timeline_canvas.GetSelectedEvents()
        number_of_selected_events = len(selected_events)

        def edit_function():
            if user_ack():
                with self.timeline_canvas.GetDb().transaction("Delete events"):
                    for event in selected_events:
                        event.delete()
            self.timeline_canvas.ClearSelectedEvents()

        def user_ack():
            if number_of_selected_events > 1:
                text = _("Are you sure you want to delete %d events?" %
                         number_of_selected_events)
            else:
                text = _("Are you sure you want to delete this event?")
            return _ask_question(text) == wx.YES
        safe_locking(self._edit_controller, edit_function)

    def _context_menu_on_edit_event(self, evt):
        self.open_event_editor(self.timeline_canvas.GetSelectedEvent())

    def _context_menu_on_duplicate_event(self, evt):
        open_duplicate_event_dialog_for_event(
            self._edit_controller,
            self,
            self.timeline_canvas.GetDb(),
            self.timeline_canvas.GetSelectedEvent())

    # @experimental_feature(EVENT_DONE)
    def _context_menu_on_done_event(self, evt):
        def edit_function():
            with self.timeline_canvas.GetDb().transaction("Mark events done"):
                for event in self.timeline_canvas.GetSelectedEvents():
                    if not event.is_container():
                        event.set_progress(100)
                        event.save()
            self.timeline_canvas.ClearSelectedEvents()
        safe_locking(self._edit_controller, edit_function)

    def _context_menu_on_select_category(self, evt):
        # TODO: Disable the context menu if the main_frame don't have
        #       a set_category_on_selected() method
        set_category_on_selected = getattr(self.main_frame, 'set_category_on_selected', None)
        if callable(set_category_on_selected):
            set_category_on_selected()

    def _context_menu_on_sticky_balloon_event(self, evt):
        self.timeline_canvas.SetEventStickyBalloon(self.timeline_canvas.GetSelectedEvent(), True)

    def _context_menu_on_goto_hyperlink_event(self, evt):
        hyperlinks = self.timeline_canvas.GetSelectedEvent().get_data("hyperlink")
        hyperlink = hyperlinks.split(";")[evt.Id]
        webbrowser.open(to_unicode(hyperlink))

    def _timeline_canvas_on_divider_position_changed(self, event):
        self.divider_line_slider.SetValue(self.timeline_canvas.GetDividerPosition())
        self.config.divider_line_slider_pos = self.timeline_canvas.GetDividerPosition()

    def _timeline_canvas_on_timeline_redrawn(self, event):
        text = _("%s events hidden") % self.timeline_canvas.GetHiddenEventCount()
        self.status_bar_adapter.set_hidden_event_count_text(text)
        enable_disable_menus = getattr(self.main_frame, 'enable_disable_menus')
        if callable(enable_disable_menus):
            enable_disable_menus()

    def _layout_components(self):
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.splitter, proportion=1, flag=wx.EXPAND)
        hsizer.Add(self.divider_line_slider, proportion=0, flag=wx.EXPAND)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.tool_bar, proportion=0, flag=wx.EXPAND)
        vsizer.Add(self.message_bar, proportion=0, flag=wx.EXPAND)
        vsizer.Add(hsizer, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vsizer)


class TimelinePanel(TimelinePanelGuiCreator):

    def __init__(self, parent, config, status_bar_adapter, main_frame):
        self.config = config
        self.status_bar_adapter = status_bar_adapter
        self.main_frame = main_frame
        self._edit_controller = main_frame
        TimelinePanelGuiCreator.__init__(self, parent)
        self._db_listener = Listener(self._on_db_changed)

    def SetDb(self, db):
        self.timeline_canvas.SetDb(db)
        self._db_listener.set_observable(db)

    def get_timeline_canvas(self):
        return self.timeline_canvas

    def get_time_period(self):
        return self.timeline_canvas.get_time_period()

    def open_event_editor(self, event):
        open_event_editor_for(
            self._edit_controller,
            self,
            self.config,
            self.timeline_canvas.GetDb(),
            event)

    def open_milestone_editor(self, event):
        open_milestone_editor_for(
            self._edit_controller,
            self,
            self.config,
            self.timeline_canvas.GetDb(),
            event)

    def redraw_timeline(self):
        self.timeline_canvas.Redraw()

    def Navigate(self, navigation_fn):
        return self.timeline_canvas.Navigate(navigation_fn)

    def get_view_properties(self):
        return self.timeline_canvas.get_view_properties()

    def get_sidebar_width(self):
        return self.sidebar_width

    def show_sidebar(self):
        self.splitter.SplitVertically(self.sidebar, self.timeline_canvas, self.sidebar_width)
        self.splitter.SetSashPosition(self.sidebar_width)
        self.splitter.SetMinimumPaneSize(self.sidebar.GetBestSize()[0])

    def hide_sidebar(self):
        self.splitter.Unsplit(self.sidebar)

    def activated(self):
        if self.config.show_sidebar:
            self.show_sidebar()

    def _on_db_changed(self, db):
        if db.is_read_only():
            header = _("This timeline is read-only.")
            body = _("To edit this timeline, save it to a new file: File -> Save As.")
            self.message_bar.ShowInformationMessage("%s\n%s" % (header, body))
        elif not db.is_saved():
            header = _("This timeline is not being saved.")
            body = _("To save this timeline, save it to a new file: File -> Save As.")
            self.message_bar.ShowWarningMessage("%s\n%s" % (header, body))
        else:
            self.message_bar.ShowNoMessage()


class InputHandlerState(object):

    def __init__(self, canvas, status_bar, edit_controller, config):
        self._timeline_canvas = canvas
        self._status_bar = status_bar
        self._edit_controller = edit_controller
        self._config = config

    def ok_to_edit(self):
        return self._edit_controller.ok_to_edit()

    def edit_ends(self):
        return self._edit_controller.edit_ends()

    def display_status(self, message):
        return self._edit_controller.DisplayStatus(message)

    def change_to_no_op(self):
        self._timeline_canvas.SetInputHandler(
            NoOpInputHandler(self, self._timeline_canvas))

    def change_to_move_by_drag(self, event, start_drag_time):
        self._timeline_canvas.SetInputHandler(
            MoveByDragInputHandler(self, self._timeline_canvas, event, start_drag_time))

    def change_to_zoom_by_drag(self, cursor):
        start_time = self._timeline_canvas.GetTimeAt(cursor.x)
        self._timeline_canvas.SetInputHandler(
            ZoomByDragInputHandler(self, self._timeline_canvas, start_time))

    def change_to_select(self, cursor):
        self._timeline_canvas.SetInputHandler(
            SelectEventsInputHandler(self, self._timeline_canvas, cursor))

    def change_to_resize_by_drag(self, event, direction):
        self._timeline_canvas.SetInputHandler(
            ResizeByDragInputHandler(self, self._timeline_canvas, event, direction))

    def change_to_scroll_by_drag(self, cursor):
        start_time = self._timeline_canvas.GetTimeAt(cursor.x)
        y = cursor.y
        self._timeline_canvas.SetInputHandler(
            ScrollByDragInputHandler(self, self._timeline_canvas, start_time, y))

    def change_to_create_period_event_by_drag(self, cursor):
        time_at_x = self._timeline_canvas.GetTimeAt(cursor.x)
        self._timeline_canvas.SetInputHandler(
            CreatePeriodEventByDragInputHandler(self, self._timeline_canvas, self._config, time_at_x))
