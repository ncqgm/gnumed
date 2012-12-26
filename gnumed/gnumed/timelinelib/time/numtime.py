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


import re

from timelinelib.time.typeinterface import TimeType
from timelinelib.db.objects import time_period_center
from timelinelib.drawing.interface import Strip
from timelinelib.drawing.utils import get_default_font
from timelinelib.db.objects import TimePeriod


class NumTimeType(TimeType):

    def time_string(self, time):
        return "%s" % (time)

    def parse_time(self, time_string):
        match = re.search(r"^([-]?\d+(.\d+)?)$", time_string)
        if match:
            time = float(match.group(1))
            try:
                return time
            except ValueError:
                raise ValueError("Invalid time, time string = '%s'" % time_string)
        else:
            raise ValueError("Time not on correct format = '%s'" % time_string)

    def get_navigation_functions(self):
        return [
            (_("Go to &Zero\tCtrl+Z"), go_to_zero_fn),
            (_("Go to &Time\tCtrl+T"), go_to_time_fn),
            ("SEP", None),
            (_("Backward\tPgUp"), backward_fn),
            (_("Forward\tPgDn"), forward_fn),
        ]

    def is_date_time_type(self):
        return False

    def format_period(self, time_period):
        """Returns a unicode string describing the time period."""
        if time_period.is_period():
            label = u"%s to %s" % (time_period.start_time, time_period.end_time)
        else:
            label = u"%s" % time_period.start_time
        return label

    def format_delta(self, delta):
        return "%d" % delta

    def get_min_time(self):
        return(None, None)

    def get_max_time(self):
        return(None, None)

    def choose_strip(self, metrics, config):
        start_time = 1
        end_time = 2
        limit = 30
        period = TimePeriod(self, start_time, end_time)
        period_width = metrics.calc_exact_width(period)
        while period_width == 0:
            start_time *= 10
            end_time *= 10
            limit /= 10
            period = TimePeriod(self, start_time, end_time)
            period_width = metrics.calc_exact_width(period)
        nbr_of_units = metrics.width / period_width
        size = 1
        while nbr_of_units > limit:
            size *= 10
            nbr_of_units /= 10
        return (NumStrip(size * 10), NumStrip(size))

    def mult_timedelta(self, delta, num):
        return delta * num

    def get_default_time_period(self):
        return time_period_center(self, 0, 100)

    def now(self):
        return 0

    def get_time_at_x(self, time_period, x_percent_of_width):
        """Return the time at pixel `x`."""
        delta = time_period.end_time - time_period.start_time
        return time_period.start_time + delta * x_percent_of_width

    def div_timedeltas(self, delta1, delta2):
        return delta1 / delta2

    def get_max_zoom_delta(self):
        return (None, None)

    def get_min_zoom_delta(self):
        return (5, _("Can't zoom deeper than 5"))

    def get_zero_delta(self):
        return 0

    def time_period_has_nonzero_time(self, time_period):
        return False

    def get_name(self):
        return u"numtime"

    def get_duplicate_functions(self):
        return [
            (_("1-period"), lambda p, d : move_period(p, d)),
            (_("10-period"), lambda p, d : move_period(p, d * 10)),
            (_("100-period"), lambda p, d : move_period(p, d * 100)),
            (_("1000-period"), lambda p, d : move_period(p, d * 1000)),
        ]

    def zoom_is_ok(self, delta):
        return (delta >= 5)

    def half_delta(self, delta):
        return delta / 2

    def margin_delta(self, delta):
        return delta / 24

    def eventtimes_equals(self, time1, time2):
        return time_string(time1) == time_string(time2)


class NumStrip(Strip):

    def __init__(self, size):
        self.size = size

    def label(self, time, major=False):
        return "%s" % (time)

    def start(self, time):
        start = int((time / self.size)) * self.size
        if time < 0:
            start -= self.size
        return start

    def increment(self, time):
        return time + self.size

    def get_font(self, time_period):
        return get_default_font(8)


def go_to_zero_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.center(0))


def go_to_time_fn(main_frame, current_period, navigation_fn):
    def navigate_to(time):
        navigation_fn(lambda tp: tp.center(time))
    main_frame.display_time_editor_dialog(
        NumTimeType(), current_period.mean_time(), navigate_to, _("Go to Time"))


def backward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.start_time - current_period.end_time
    navigation_fn(lambda tp: tp.move_delta(delta))


def forward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.end_time - current_period.start_time
    navigation_fn(lambda tp: tp.move_delta(delta))


def move_period(period, delta):
    start_time = period.start_time + delta
    end_time = period.end_time + delta
    return TimePeriod(period.time_type, start_time, end_time)
