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


from timelinelib.db.objects import TimePeriod
from timelinelib.view.scrollbase import ScrollViewInputHandler


class SelectPeriodByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, controller, initial_time):
        ScrollViewInputHandler.__init__(self, controller)
        self.controller = controller
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
            self.current_time = self.controller.get_time(self.last_x)
            period = self.get_current_period()
            self.last_valid_time = self.current_time
        except ValueError:
            period = self.get_last_valid_period()
        self.controller.view_properties.period_selection = (period.start_time, period.end_time)
        self.controller._redraw_timeline()

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
            self.controller.get_timeline().get_time_type(),
            self.controller.get_drawer().snap(start),
            self.controller.get_drawer().snap(end))

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self._end_action()

    def _end_action(self):
        self.end_action()
        self._remove_selection()
        self.controller.change_input_handler_to_no_op()

    def _remove_selection(self):
        self.controller.view_properties.period_selection = None
        self.controller.redraw_timeline()

    def end_action(self):
        raise Exception("end_action not implemented in subclass.")
