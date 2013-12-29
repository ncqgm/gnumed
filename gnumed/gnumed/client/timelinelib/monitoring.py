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


import sys
import time

from timelinelib.meta.version import DEV


class Monitoring(object):

    IS_ENABLED = DEV

    def __init__(self):
        self.timeline_redraw_count = 0
        self.category_redraw_count = 0
        self.timer = Timer()

    def count_timeline_redraw(self):
        self.timeline_redraw_count += 1

    def count_category_redraw(self):
        self.category_redraw_count += 1

    def timer_start(self):
        self.timer.start()

    def timer_end(self):
        self.timer.end()

    def timer_elapsed_ms(self):
        return self.timer.elapsed_ms()


class Timer(object):

    def __init__(self):
        # Taken from timeit.py (Python standard library)
        if sys.platform == "win32":
            # On Windows, the best timer is time.clock()
            self.default_timer = time.clock
        else:
            # On most other platforms the best timer is time.time()
            self.default_timer = time.time

    def start(self):
        self._start = self.default_timer()

    def end(self):
        self._end = self.default_timer()

    def elapsed_ms(self):
        return (self._end - self._start) * 1000


monitoring = Monitoring()
