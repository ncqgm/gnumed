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

"""Contains the Monitoring class."""

from timelinelib.timer import Timer


class Monitoring(object):
    """
    * Kepp track of the number of times the timeline has been redrawn.
    * Measure the time it takes to redraw.
    """
    def __init__(self, timer=None):
        self._timeline_redraw_count = 0
        self._category_redraw_count = 0
        if timer is None:
            self._timer = Timer()
        else:
            self._timer = timer

    def count_timeline_redraw(self):
        """Increment counter."""
        self._timeline_redraw_count += 1

    def count_category_redraw(self):
        """Increment counter."""
        self._category_redraw_count += 1

    def timer_start(self):
        """Start time measurement."""
        self._timer.start()

    def timer_end(self):
        """Stop time measurement."""
        self._timer.end()

    @property
    def timer_elapsed_ms(self):
        "return the elapsed time in milliseconds."
        return self._timer.elapsed_ms
