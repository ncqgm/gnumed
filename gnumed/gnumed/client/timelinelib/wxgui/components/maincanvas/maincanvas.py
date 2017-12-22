# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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

from timelinelib.canvas.data import TimeOutOfRangeLeftError
from timelinelib.canvas.data import TimeOutOfRangeRightError
from timelinelib.canvas import TimelineCanvas
from timelinelib.utils import ex_msg
from timelinelib.wxgui.cursor import Cursor
from timelinelib.wxgui.keyboard import Keyboard
from timelinelib.wxgui.components.maincanvas.inputhandler import InputHandler
from timelinelib.general.methodcontainer import MethodContainer
from timelinelib.canvas.data import TimePeriod
from timelinelib.canvas.timelinecanvas import LEFT_RESIZE_HANDLE
from timelinelib.canvas.timelinecanvas import RIGHT_RESIZE_HANDLE
from timelinelib.canvas.timelinecanvas import MOVE_HANDLE


class MainCanvas(TimelineCanvas):

    def __init__(self, parent, edit_controller, status_bar):
        TimelineCanvas.__init__(self, parent)
        self._edit_controller = edit_controller
        self._status_bar = status_bar
        self.SetInputHandler(InputHandler(self))
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_TIMER, self._on_dragscroll, self.dragscroll_timer)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel)

    def SetDb(self, db):
        db.display_in_canvas(self)

    def Navigate(self, navigation_fn):
        try:
            TimelineCanvas.Navigate(self, navigation_fn)
        except (TimeOutOfRangeLeftError) as e:
            self._status_bar.set_text(_("Can't scroll more to the left"))
        except (TimeOutOfRangeRightError) as e:
            self._status_bar.set_text(_("Can't scroll more to the right"))
        except (ValueError, OverflowError) as e:
            self._status_bar.set_text(ex_msg(e))
        else:
            self._status_bar.set_text("")

    def SetInputHandler(self, input_handler):
        self._input_handler = input_handler

    def _on_left_down(self, evt):
        self._edit_controller.save_time_period()
        self.SetFocus()
        self._input_handler.left_mouse_down(self._get_cursor(evt),
                                            self._get_keyboard(evt))

    def _on_left_dclick(self, evt):
        """
        Event handler used when the left mouse button has been double clicked.

        If the timeline is readonly, no action is taken.
        If the mouse hits an event, a dialog opens for editing this event.
        Otherwise a dialog for creating a new event is opened.
        """
        if self.IsReadOnly():
            return
        # Since the event sequence is, 1. EVT_LEFT_DOWN  2. EVT_LEFT_UP
        # 3. EVT_LEFT_DCLICK we must compensate for the toggle_event_selection
        # that occurs in the handling of EVT_LEFT_DOWN, since we still want
        # the event(s) selected or deselected after a left doubleclick
        # It doesn't look too god but I havent found any other way to do it.
        self.ToggleEventSelection(evt)

    def _get_cursor(self, evt):
        return Cursor(evt.GetX(), evt.GetY())

    def _get_keyboard(self, evt):
        return Keyboard(evt.ControlDown(), evt.ShiftDown(), evt.AltDown())

    def _on_left_up(self, event):
        self._input_handler.left_mouse_up()

    def _on_motion(self, evt):
        self.DisplayBalloons(evt)
        self._status_bar.set_text(self.GetTimelineInfoText(evt))
        self.SetCursorShape(evt)
        self._input_handler.mouse_moved(self._get_cursor(evt),
                                        self._get_keyboard(evt))

    def _on_dragscroll(self, event):
        self._input_handler.dragscroll_timer_fired()

    def _on_middle_down(self, evt):
        self.CenterAtCursor(evt)

    def _on_mousewheel(self, evt):
        self._edit_controller.save_time_period()

        keyboard = self._get_keyboard(evt)
        methods = MethodContainer(
            [
                (Keyboard.CTRL, self.ZoomHorizontallyOnMouseWheel),
                (Keyboard.SHIFT + Keyboard.CTRL, self.SpecialScrollVerticallyOnMouseWheel),
                (Keyboard.SHIFT, self.ScrollVerticallyOnMouseWheel),
                (Keyboard.ALT, self.ZoomVerticallyOnMouseWheel),
            ], default_method=self.ScrollHorizontallyOnMouseWheel
        )
        methods.select(keyboard.keys_combination)(evt)

    def start_dragscroll_timer(self, milliseconds=-1, oneShot=False):
        self.dragscroll_timer.Start(milliseconds, oneShot)

    def stop_dragscroll_timer(self):
        self.dragscroll_timer.Stop()

    def toggle_event_selection(self, cursor, keyboard):

        def toggle_event_selection_when_event_is_hit(event):
            selected = not self.IsEventSelected(event)
            if keyboard.ctrl:
                self.SetEventSelected(event, selected)
            else:
                self.ClearSelectedEvents()
                self.SetEventSelected(event, selected)

        event = self.GetEventAt(cursor, keyboard.alt)
        if event:
            toggle_event_selection_when_event_is_hit(event)
        else:
            self.ClearSelectedEvents()

    def format_current_pos_time_string(self, x):
        tm = self.GetTimeAt(x)
        return self.GetTimeType().format_period(TimePeriod(tm, tm))

    def toggle_balloon_stickyness(self, event_with_balloon):
        stick = not self.EventHasStickyBalloon(event_with_balloon)
        self.SetEventStickyBalloon(event_with_balloon, stick)
        if stick:
            self.Redraw()
        else:
            if self.GetAppearance().get_balloons_visible():
                self.SetHoveredEvent(event_with_balloon)
            else:
                self.SetHoveredEvent(None)

    def hit_resize_handle(self, cursor, keyboard):
        try:
            event, hit_info = self.GetEventWithHitInfoAt(cursor, keyboard)
            if event.get_locked():
                return None
            if event.is_milestone():
                return None
            if not self.IsEventSelected(event):
                return None
            if hit_info == LEFT_RESIZE_HANDLE:
                return wx.LEFT
            if hit_info == RIGHT_RESIZE_HANDLE:
                return wx.RIGHT
            return None
        except:
            return None

    def hit_move_handle(self, cursor, keyboard):
        event_and_hit_info = self.GetEventWithHitInfoAt(cursor, keyboard)
        if event_and_hit_info is None:
            return False
        (event, hit_info) = event_and_hit_info
        if event.get_locked():
            return False
        if not self.IsEventSelected(event):
            return False
        return hit_info == MOVE_HANDLE


def step_function(x_value):
    y_value = 0
    if x_value < 0:
        y_value = -1
    elif x_value > 0:
        y_value = 1
    return y_value
