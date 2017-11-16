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
from timelinelib.wxgui.components.maincanvas.inputhandler import InputHandler


class MainCanvas(TimelineCanvas):

    def __init__(self, parent, main_frame, status_bar):
        TimelineCanvas.__init__(self, parent)
        self.main_frame = main_frame
        self._status_bar = status_bar
        self.SetInputHandler(InputHandler(self))
        self.balloon_show_timer = wx.Timer(self, -1)
        self.balloon_hide_timer = wx.Timer(self, -1)
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_TIMER, self._on_balloon_show_timer, self.balloon_show_timer)
        self.Bind(wx.EVT_TIMER, self._on_balloon_hide_timer, self.balloon_hide_timer)
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

    def _on_left_down(self, event):
        self.main_frame.save_time_period()
        self.SetFocus()
        self._input_handler.left_mouse_down(
            event.GetX(), event.GetY(), event.ControlDown(), event.ShiftDown(),
            event.AltDown())

    def _on_left_dclick(self, event):
        self._input_handler.left_mouse_dclick(
            event.GetX(), event.GetY(), event.ControlDown(), event.AltDown())

    def _on_left_up(self, event):
        self._input_handler.left_mouse_up()

    def _on_motion(self, event):
        self._input_handler.mouse_moved(event.GetX(), event.GetY(), event.AltDown())

    def _on_balloon_show_timer(self, event):
        self._input_handler.balloon_show_timer_fired()

    def _on_balloon_hide_timer(self, event):
        self._input_handler.balloon_hide_timer_fired()

    def _on_dragscroll(self, event):
        self._input_handler.dragscroll_timer_fired()

    def _on_middle_down(self, event):
        self._input_handler.middle_mouse_down(event.GetX())

    def _on_mousewheel(self, evt):
        self.main_frame.save_time_period()
        self._input_handler.mouse_wheel_moved(
            evt.GetWheelRotation(), evt.ControlDown(), evt.ShiftDown(),
            evt.AltDown(), evt.GetX())

    def start_balloon_show_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_show_timer.Start(milliseconds, oneShot)

    def start_balloon_hide_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_hide_timer.Start(milliseconds, oneShot)

    def start_dragscroll_timer(self, milliseconds=-1, oneShot=False):
        self.dragscroll_timer.Start(milliseconds, oneShot)

    def stop_dragscroll_timer(self):
        self.dragscroll_timer.Stop()
