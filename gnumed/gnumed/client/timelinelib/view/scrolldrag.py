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


import time

from timelinelib.view.inputhandler import InputHandler


class ScrollByDragInputHandler(InputHandler):

    def __init__(self, controller, start_time):
        self.controller = controller
        self.start_time = start_time
        self.last_clock_time = time.clock()
        self.last_x = 0
        self.last_x_distance = 0
        self.speed_px_per_sec = 0
        self.INERTIAL_SCROLLING_SPEED_THRESHOLD = 200

    def mouse_moved(self, x, y, alt_down=False):
        self._calculate_sped(x)
        self._scroll_timeline(x)

    def left_mouse_up(self):
        self.controller.change_input_handler_to_no_op()
        if self.controller.config.use_inertial_scrolling:
            if self.speed_px_per_sec > self.INERTIAL_SCROLLING_SPEED_THRESHOLD:
                self._inertial_scrolling()

    def _calculate_sped(self, x):
        MAX_SPEED = 10000
        self.last_x_distance = x - self.last_x
        self.last_x = x
        current_clock_time = time.clock()
        elapsed_clock_time = current_clock_time - self.last_clock_time
        if elapsed_clock_time == 0:
            self.speed_px_per_sec = MAX_SPEED
        else:
            self.speed_px_per_sec = min(MAX_SPEED, abs(self.last_x_distance /
                                        elapsed_clock_time))
        self.last_clock_time = current_clock_time

    def _scroll_timeline(self, x):
        self.current_time = self.controller.get_time(x)
        delta = (self.current_time - self.start_time)
        self.controller._scroll_timeline(delta)

    def _inertial_scrolling(self):
        frame_time = self._calculate_frame_time()
        value_factor = self._calculate_scroll_factor()
        inertial_func = (0.20, 0.15, 0.10, 0.10, 0.10, 0.08, 0.06, 0.06, 0.05)
        #inertial_func = (0.20, 0.15, 0.10, 0.10, 0.07, 0.05, 0.02, 0.05)
        self.controller.use_fast_draw(True)
        next_frame_time = time.clock()
        for value in inertial_func:
            self.controller._scroll_timeline_view(value * value_factor)
            next_frame_time += frame_time
            sleep_time = next_frame_time - time.clock()
            if sleep_time >= 0:
                time.sleep(sleep_time)
        self.controller.use_fast_draw(False)
        self.controller._redraw_timeline()

    def _calculate_frame_time(self):
        MAX_FRAME_RATE = 26.0
        frames_per_second = (MAX_FRAME_RATE * self.speed_px_per_sec /
                             (100 + self.speed_px_per_sec))
        frame_time = 1.0 / frames_per_second
        return frame_time

    def _calculate_scroll_factor(self):
        if self.current_time > self.start_time:
            direction = 1
        else:
            direction = -1
        scroll_factor = (direction * self.speed_px_per_sec /
                        self.INERTIAL_SCROLLING_SPEED_THRESHOLD)
        return scroll_factor
