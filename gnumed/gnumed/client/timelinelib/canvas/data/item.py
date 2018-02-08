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


from timelinelib.canvas.data.timeperiod import TimePeriod


class TimelineItem(object):
    """
    I represent any item that should be displayed on a timeline.

    I have a time period and methods to manipulate it.

    Specific items inherit from me.
    """

    def get_time_period(self):
        return self._immutable_value.time_period

    def get_start_time(self):
        return self.time_period.get_start_time()

    def get_end_time(self):
        return self.time_period.get_end_time()

    def set_time_period(self, time_period):
        self._immutable_value = self._immutable_value.update(time_period=time_period)
        return self

    time_period = property(get_time_period, set_time_period)

    def update_period(self, start_time, end_time):
        self.set_time_period(TimePeriod(start_time, end_time))

    def update_period_o(self, new_period):
        self.update_period(new_period.start_time, new_period.end_time)

    def start_to_start(self, event):
        return self.time_period.start_to_start(event.get_time_period())

    def start_to_end(self, event):
        return self.time_period.start_to_end(event.get_time_period())

    def end_to_end(self, event):
        return self.time_period.end_to_end(event.get_time_period())

    def move_delta(self, delta):
        self.set_time_period(self.time_period.move_delta(delta))

    def inside_period(self, time_period):
        return self.time_period.inside_period(time_period)

    def is_period(self):
        return self.time_period.is_period()

    def mean_time(self):
        return self.time_period.mean_time()

    def time_span(self):
        return self.time_period.end_time - self.time_period.start_time

    def overlaps(self, event):
        return self.time_period.overlaps(event.get_time_period())

    def distance_to(self, event):
        return self.time_period.distance_to(event.get_time_period())
