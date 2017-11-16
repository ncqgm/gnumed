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


from timelinelib.canvas.data import TimePeriod
from timelinelib.wxgui.components.maincanvas.scrollbase import ScrollViewInputHandler


class SelectPeriodByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, state, timeline_canvas, main_frame, initial_time):
        ScrollViewInputHandler.__init__(self, timeline_canvas)
        self._state = state
        self._main_frame = main_frame
        self.timeline_canvas = timeline_canvas
        self.initial_time = initial_time
        self.last_valid_time = initial_time
        self.current_time = initial_time

    def mouse_moved(self, x, y, alt_down=False):
        ScrollViewInputHandler.mouse_moved(self, x, y, alt_down)
        self._move_current_time()

    def view_scrolled(self):
        self._move_current_time()

    def _move_current_time(self):
        try:
            self.current_time = self.timeline_canvas.GetTimeAt(self.last_x)
            period = self.get_current_period()
            self.last_valid_time = self.current_time
        except ValueError:
            period = self.get_last_valid_period()
        self.timeline_canvas.SetPeriodSelection(period)

    def get_last_valid_period(self):
        return self._get_period(self.initial_time, self.last_valid_time)

    def get_current_period(self):
        return self._get_period(self.initial_time, self.current_time)

    def _get_period(self, t1, t2):
        if t1 > t2:
            start = t2
            end = t1
        else:
            start = t1
            end = t2
        return TimePeriod(
            self.timeline_canvas.Snap(start),
            self.timeline_canvas.Snap(end))

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self._end_action()

    def _end_action(self):
        self.end_action()
        self._remove_selection()
        self._state.change_to_no_op()
        self._main_frame.edit_ends()

    def _remove_selection(self):
        self.timeline_canvas.SetPeriodSelection(None)

    def end_action(self):
        raise Exception("end_action not implemented in subclass.")
