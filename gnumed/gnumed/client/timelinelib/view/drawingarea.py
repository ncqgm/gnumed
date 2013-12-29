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


import datetime
import webbrowser

import wx

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import TimeOutOfRangeLeftError
from timelinelib.db.objects import TimeOutOfRangeRightError
from timelinelib.db.utils import safe_locking
from timelinelib.drawing.utils import get_default_font
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.monitoring import monitoring
from timelinelib.utilities.observer import STATE_CHANGE_ANY
from timelinelib.utilities.observer import STATE_CHANGE_CATEGORY
from timelinelib.utils import ex_msg
from timelinelib.view.move import MoveByDragInputHandler
from timelinelib.view.noop import NoOpInputHandler
from timelinelib.view.periodevent import CreatePeriodEventByDragInputHandler
from timelinelib.view.resize import ResizeByDragInputHandler
from timelinelib.view.scrolldrag import ScrollByDragInputHandler
from timelinelib.view.zoom import ZoomByDragInputHandler


# The width in pixels of the vertical scroll zones.
# When the mouse reaches the any of the two scroll zone areas, scrolling
# of the timeline will take place if there is an ongoing selection of the
# timeline. The scroll zone areas are found at the beginning and at the
# end of the timeline.
SCROLL_ZONE_WIDTH = 20
HSCROLL_STEP = 25
LEFT_RIGHT_SCROLL_FACTOR = 1 / 200.0
MOUSE_SCROLL_FACTOR = 1 / 10.0


class DrawingArea(object):

    def __init__(self, view, status_bar_adapter, config, drawing_algorithm,
                 divider_line_slider, fn_handle_db_error):
        self.config = config
        self.view = view
        self.status_bar_adapter = status_bar_adapter
        self.drawing_algorithm = drawing_algorithm
        self.divider_line_slider = divider_line_slider
        self.fn_handle_db_error = fn_handle_db_error
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.divider_line_slider.Bind(wx.EVT_SLIDER,       self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU, self._slider_on_context_menu)
        self.change_input_handler_to_no_op()
        self.fast_draw = False
        self.timeline = None

    def change_input_handler_to_zoom_by_drag(self, start_time):
        self.input_handler = ZoomByDragInputHandler(self, self.status_bar_adapter, start_time)

    def change_input_handler_to_create_period_event_by_drag(self, initial_time):
        self.input_handler = CreatePeriodEventByDragInputHandler(self, self.view, initial_time)

    def change_input_handler_to_resize_by_drag(self, event, direction):
        self.input_handler = ResizeByDragInputHandler(
            self, self.status_bar_adapter, event, direction)

    def change_input_handler_to_move_by_drag(self, event, start_drag_time):
        self.input_handler = MoveByDragInputHandler(
            self, self.status_bar_adapter, event, start_drag_time)

    def change_input_handler_to_scroll_by_drag(self, start_time):
        self.input_handler = ScrollByDragInputHandler(self, start_time)

    def change_input_handler_to_no_op(self):
        self.input_handler = NoOpInputHandler(self, self.view)
        self.view.edit_ends()

    def get_drawer(self):
        return self.drawing_algorithm

    def get_timeline(self):
        return self.timeline

    def get_view_properties(self):
        return self.view_properties

    def set_timeline(self, timeline):
        """Inform what timeline to draw."""
        self._unregister_timeline(self.timeline)
        if timeline is None:
            self._set_null_timeline()
        else:
            self._set_non_null_timeline(timeline)

    def use_fast_draw(self, value):
        self.fast_draw = value

    def _set_null_timeline(self):
        self.timeline = None
        self.time_type = None
        self.view.Disable()

    def _set_non_null_timeline(self, timeline):
        self.timeline = timeline
        self.time_type = timeline.get_time_type()
        self.timeline.register(self._timeline_changed)
        self.view_properties.unlisten(self._redraw_timeline)
        properties_loaded = self._load_view_properties()
        if properties_loaded:
            self.view_properties.listen_for_any(self._redraw_timeline)
            self._redraw_timeline()
            self.view.Enable()
            self.view.SetFocus()

    def _load_view_properties(self):
        properties_loaded = True
        try:
            self.view_properties.clear_db_specific()
            self.timeline.load_view_properties(self.view_properties)
            if self.view_properties.displayed_period is None:
                default_tp = self.time_type.get_default_time_period()
                self.view_properties.displayed_period = default_tp
            self.view_properties.hscroll_amount = 0
        except TimelineIOError, e:
            self.fn_handle_db_error(e)
            properties_loaded = False
        return properties_loaded

    def _unregister_timeline(self, timeline):
        if timeline != None:
            timeline.unregister(self._timeline_changed)

    def show_hide_legend(self, show):
        self.view_properties.change_show_legend(show)

    def get_time_period(self):
        """Return currently displayed time period."""
        if self.timeline == None:
            raise Exception(_("No timeline set"))
        return self.view_properties.displayed_period

    def navigate_timeline(self, navigation_fn):
        """
        Perform a navigation operation followed by a redraw.

        The navigation_fn should take one argument which is the time period
        that should be manipulated in order to carry out the navigation
        operation.

        Should the navigation operation fail (max zoom level reached, etc) a
        message will be displayed in the statusbar.

        Note: The time period should never be modified directly. This method
        should always be used instead.
        """
        if self.timeline == None:
            raise Exception(_("No timeline set"))
        try:
            self.view_properties.displayed_period = navigation_fn(self.view_properties.displayed_period)
            self._redraw_timeline()
            self.status_bar_adapter.set_text("")
        except (TimeOutOfRangeLeftError), e:
            self.status_bar_adapter.set_text(_("Can't scroll more to the left"))
        except (TimeOutOfRangeRightError), e:
            self.status_bar_adapter.set_text(_("Can't scroll more to the right"))
        except (ValueError, OverflowError), e:
            self.status_bar_adapter.set_text(ex_msg(e))

    def redraw_timeline(self):
        self._redraw_timeline()

    def window_resized(self):
        self._redraw_timeline()

    def left_mouse_down(self, x, y, ctrl_down, shift_down, alt_down=False):
        self.input_handler.left_mouse_down(x, y, ctrl_down, shift_down, alt_down)

    def right_mouse_down(self, x, y, alt_down=False):
        """
        Event handler used when the right mouse button has been pressed.

        If the mouse hits an event and the timeline is not readonly, the
        context menu for that event is displayed.
        """
        if self.timeline.is_read_only():
            return
        self.context_menu_event = self.drawing_algorithm.event_at(x, y, alt_down)
        if self.context_menu_event is None:
            return
        self.view_properties.set_selected(self.context_menu_event, True)
        menu_definitions = [
            (_("Edit"), self._context_menu_on_edit_event),
            (_("Duplicate..."), self._context_menu_on_duplicate_event),
            (_("Delete"), self._context_menu_on_delete_event),
        ]
        if self.context_menu_event.has_data():
            menu_definitions.append((_("Sticky Balloon"), self._context_menu_on_sticky_balloon_event))
        hyperlink = self.context_menu_event.get_data("hyperlink")
        if hyperlink is not None:
            menu_definitions.append((_("Goto URL"), self._context_menu_on_goto_hyperlink_event))
        menu = wx.Menu()
        for menu_definition in menu_definitions:
            text, method = menu_definition
            menu_item = wx.MenuItem(menu, wx.NewId(), text)
            self.view.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
            menu.AppendItem(menu_item)
        self.view.PopupMenu(menu)
        menu.Destroy()

    def _one_and_only_one_event_selected(self):
        selected_event_ids = self.view_properties.get_selected_event_ids()
        nbr_of_selected_event_ids = len(selected_event_ids)
        return nbr_of_selected_event_ids == 1

    def _get_first_selected_event(self):
        selected_event_ids = self.view_properties.get_selected_event_ids()
        if len(selected_event_ids) > 0:
            id = selected_event_ids[0]
            return self.timeline.find_event_with_id(id)
        return None

    def _context_menu_on_edit_event(self, evt):
        self.view.open_event_editor_for(self.context_menu_event)

    def _context_menu_on_duplicate_event(self, evt):
        self.view.open_duplicate_event_dialog_for_event(self.context_menu_event)

    def _context_menu_on_delete_event(self, evt):
        self.context_menu_event.selected = True
        self._delete_selected_events()

    def _context_menu_on_sticky_balloon_event(self, evt):
        self.view_properties.set_event_has_sticky_balloon(self.context_menu_event, has_sticky=True)
        self._redraw_timeline()

    def _context_menu_on_goto_hyperlink_event(self, evt):
        hyperlink = self.context_menu_event.get_data("hyperlink")
        webbrowser.open(hyperlink)

    def left_mouse_dclick(self, x, y, ctrl_down, alt_down=False):
        """
        Event handler used when the left mouse button has been double clicked.

        If the timeline is readonly, no action is taken.
        If the mouse hits an event, a dialog opens for editing this event.
        Otherwise a dialog for creating a new event is opened.
        """
        if self.timeline.is_read_only():
            return
        # Since the event sequence is, 1. EVT_LEFT_DOWN  2. EVT_LEFT_UP
        # 3. EVT_LEFT_DCLICK we must compensate for the toggle_event_selection
        # that occurs in the handling of EVT_LEFT_DOWN, since we still want
        # the event(s) selected or deselected after a left doubleclick
        # It doesn't look too god but I havent found any other way to do it.
        self._toggle_event_selection(x, y, ctrl_down, alt_down)
        event = self.drawing_algorithm.event_at(x, y, alt_down)
        if event:
            self.view.open_event_editor_for(event)
        else:
            current_time = self.get_time(x)
            self.view.open_create_event_editor(current_time, current_time)

    def get_time(self, x):
        return self.drawing_algorithm.get_time(x)

    def event_with_rect_at(self, x, y, alt_down=False):
        return self.drawing_algorithm.event_with_rect_at(x, y, alt_down)

    def event_at(self, x, y, alt_down=False):
        return self.drawing_algorithm.event_at(x, y, alt_down)

    def is_selected(self, event):
        return self.view_properties.is_selected(event)

    def event_is_period(self, event):
        return self.get_drawer().event_is_period(event.time_period)

    def snap(self, time):
        return self.get_drawer().snap(time)

    def get_selected_events(self):
        return [self.timeline.find_event_with_id(id_) for id_ in
                self.view_properties.get_selected_event_ids()]

    def middle_mouse_clicked(self, x):
        self.navigate_timeline(lambda tp: tp.center(self.get_time(x)))

    def left_mouse_up(self):
        self.input_handler.left_mouse_up()

    def mouse_enter(self, x, left_is_down):
        """
        Mouse event handler, when the mouse is entering the window.

        If there is an ongoing selection-marking (dragscroll timer running)
        and the left mouse button is not down when we enter the window, we
        want to simulate a 'mouse left up'-event, so that the dialog for
        creating an event will be opened or sizing, moving stops.
        """
        if self.dragscroll_timer_running:
            if not left_is_down:
                self.left_mouse_up()

    def mouse_moved(self, x, y, alt_down=False):
        self.input_handler.mouse_moved(x, y, alt_down)

    def mouse_wheel_moved(self, rotation, ctrl_down, shift_down, alt_down, x):
        direction = _step_function(rotation)
        if ctrl_down:
            if shift_down:
                self._scroll_horizontal(direction)
            else:
                self._zoom_timeline(direction, x)
        elif shift_down:
            self.divider_line_slider.SetValue(self.divider_line_slider.GetValue() + direction)
            self._redraw_timeline()
        elif alt_down:
            if direction > 0:
                self.drawing_algorithm.increment_font_size()
            else:
                self.drawing_algorithm.decrement_font_size()
            self._redraw_timeline()
        else:
            self._scroll_timeline_view(direction)

    def _scroll_horizontal(self, direction):
        if direction > 0:
            self._scroll_up()
        else:
            self._scroll_down()
        self._redraw_timeline()
        
    def _scroll_up(self):
        self.view_properties.hscroll_amount -= HSCROLL_STEP
        if self.view_properties.hscroll_amount < 0:
            self.view_properties.hscroll_amount = 0
    
    def _scroll_down(self):
        self.view_properties.hscroll_amount += HSCROLL_STEP
    
    def key_down(self, keycode, alt_down):
        if keycode == wx.WXK_DELETE:
            self._delete_selected_events()
        elif alt_down:
            if keycode == wx.WXK_UP:
                self._try_move_event_vertically(True)
            elif keycode == wx.WXK_DOWN:
                self._try_move_event_vertically(False)
            elif keycode in (wx.WXK_RIGHT, wx.WXK_NUMPAD_RIGHT):
                self._scroll_timeline_view_by_factor(LEFT_RIGHT_SCROLL_FACTOR)
            elif keycode in (wx.WXK_LEFT, wx.WXK_NUMPAD_LEFT):
                self._scroll_timeline_view_by_factor(-LEFT_RIGHT_SCROLL_FACTOR)

    def _try_move_event_vertically(self, up=True):
        if self._one_and_only_one_event_selected():
            self._move_event_vertically(up)

    def _move_event_vertically(self, up=True):
        def edit_function():
            selected_event = self._get_first_selected_event()
            (overlapping_event, direction) = self.drawing_algorithm.get_closest_overlapping_event(selected_event,
                                                                                                  up=up)
            if overlapping_event is None:
                return
            if direction > 0:
                self.timeline.place_event_after_event(selected_event,
                                                      overlapping_event)
            else:
                self.timeline.place_event_before_event(selected_event,
                                                       overlapping_event)
            self._redraw_timeline()
            self.timeline._save_if_not_disabled()
        safe_locking(self.view, edit_function)

    def key_up(self, keycode):
        if keycode == wx.WXK_CONTROL:
            self.view.set_default_cursor()

    def _slider_on_slider(self, evt):
        self._redraw_timeline()

    def _slider_on_context_menu(self, evt):
        """A right click has occured in the divider-line slider."""
        menu = wx.Menu()
        menu_item = wx.MenuItem(menu, wx.NewId(), _("Center"))
        self.view.Bind(wx.EVT_MENU, self._context_menu_on_menu_center,
                  id=menu_item.GetId())
        menu.AppendItem(menu_item)
        self.view.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_menu_center(self, evt):
        """The 'Center' context menu has been selected."""
        self.divider_line_slider.SetValue(50)
        self._redraw_timeline()

    def _timeline_changed(self, state_change):
        if (state_change == STATE_CHANGE_ANY or
            state_change == STATE_CHANGE_CATEGORY):
            self._redraw_timeline()

    def _set_initial_values_to_member_variables(self):
        self.timeline = None
        self.view_properties = ViewProperties()
        self.view_properties.change_show_legend(self.config.get_show_legend())
        self.view_properties.show_balloons_on_hover = self.config.get_balloon_on_hover()
        self.dragscroll_timer_running = False

    def _set_colors_and_styles(self):
        """Define the look and feel of the drawing area."""
        self.view.SetBackgroundColour(wx.WHITE)
        self.view.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.view.set_default_cursor()
        self.view.Disable()

    def _redraw_timeline(self):
        def fn_draw(dc):
            try:
                self.drawing_algorithm.use_fast_draw(self.fast_draw)
                monitoring.timer_start()
                self.drawing_algorithm.draw(dc, self.timeline, self.view_properties, self.config)
                monitoring.timer_end()
                if monitoring.IS_ENABLED:
                    (width, height) = self.view.GetSizeTuple()
                    redraw_time = monitoring.timer_elapsed_ms()
                    monitoring.count_timeline_redraw()
                    dc.SetTextForeground((255, 0, 0))
                    dc.SetFont(get_default_font(12, bold=True))
                    dc.DrawText("Redraw count: %d" % monitoring.timeline_redraw_count, width - 300, height - 60)
                    dc.DrawText("Last redraw time: %.3f ms" % redraw_time, width - 300, height - 40)
            except TimelineIOError, e:
                self.fn_handle_db_error(e)
            finally:
                self.drawing_algorithm.use_fast_draw(False)
        if self.timeline and self.view_properties.displayed_period:
            self.view_properties.divider_position = (self.divider_line_slider.GetValue())
            self.view_properties.divider_position = (float(self.divider_line_slider.GetValue()) / 100.0)
            self.view.redraw_surface(fn_draw)
            self.view.enable_disable_menus()
            self._display_hidden_event_count()

    def _display_hidden_event_count(self):
        text = _("%s events hidden") % self.drawing_algorithm.get_hidden_event_count()
        self.status_bar_adapter.set_hidden_event_count_text(text)

    def _toggle_event_selection(self, xpixelpos, ypixelpos, control_down, alt_down=False):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos, alt_down)
        if event:
            selected = not self.view_properties.is_selected(event)
            if control_down:
                self.view_properties.set_selected(event, selected)
            else:
                self.view_properties.set_only_selected(event, selected)
        else:
            self.view_properties.clear_selected()
        return event != None

    def _display_eventinfo_in_statusbar(self, xpixelpos, ypixelpos, alt_down=False):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos, alt_down)
        if event != None:
            label = event.get_label()
        else:
            label = self._format_current_pos_datetime_string(xpixelpos)
        self.status_bar_adapter.set_text(label)

    def _format_current_pos_datetime_string(self, xpos):
        tm = self.get_time(xpos)
        dt = self.time_type.event_date_string(tm)
        tm = self.time_type.event_time_string(tm)
        return "%s %s" % (dt, tm)
        
    def balloon_show_timer_fired(self):
        self.input_handler.balloon_show_timer_fired()

    def balloon_hide_timer_fired(self):
        self.input_handler.balloon_hide_timer_fired()

    def _redraw_balloons(self, event):
        self.view_properties.change_hovered_event(event)

    def _in_scroll_zone(self, x):
        """
        Return True if x is within the left hand or right hand area
        where timed scrolling shall start/continue.
        """
        width, height = self.view.GetSizeTuple()
        if width - x < SCROLL_ZONE_WIDTH or x < SCROLL_ZONE_WIDTH:
            return True
        return False

    def dragscroll_timer_fired(self):
        self.input_handler.dragscroll_timer_fired()

    def _scroll_timeline_view(self, direction):
        factor = direction * MOUSE_SCROLL_FACTOR
        self._scroll_timeline_view_by_factor(factor)

    def _scroll_timeline_view_by_factor(self, factor):
        time_period = self.view_properties.displayed_period
        delta = self.time_type.mult_timedelta(time_period.delta(), factor)
        self._scroll_timeline(delta)

    def _scroll_timeline(self, delta):
        self.navigate_timeline(lambda tp: tp.move_delta(-delta))

    def _zoom_timeline(self, direction, x):
        """ zoom time line at position x """
        width, height = self.view.GetSizeTuple()
        x_percent_of_width=float(x)/width
        self.navigate_timeline(lambda tp: tp.zoom(direction, x_percent_of_width))

    def _delete_selected_events(self):
        """After acknowledge from the user, delete all selected events."""
        selected_event_ids = self.view_properties.get_selected_event_ids()
        nbr_of_selected_event_ids = len(selected_event_ids)
        def user_ack():
            if nbr_of_selected_event_ids > 1:
                text = _("Are you sure you want to delete %d events?" %
                         nbr_of_selected_event_ids)
            else:
                text = _("Are you sure you want to delete this event?")
            return self.view.ask_question(text) == wx.YES
        def exception_handler(ex):
            if isinstance(ex, TimelineIOError):
                self.fn_handle_db_error(ex)
            else:
                raise(ex)
        def edit_function():
            if user_ack():
                for event_id in selected_event_ids:
                    self.timeline.delete_event(event_id)
            self.view_properties.clear_selected()
        safe_locking(self.view, edit_function, exception_handler)
            
    def balloon_visibility_changed(self, visible):
        self.view_properties.show_balloons_on_hover = visible
        # When display on hovering is disabled we have to make sure
        # that any visible balloon is removed.
        # TODO: Do we really need that?
        if not visible:
            self._redraw_timeline()


def _step_function(x_value):
    y_value = 0
    if x_value < 0:
        y_value = -1
    elif x_value > 0:
        y_value = 1
    return y_value
