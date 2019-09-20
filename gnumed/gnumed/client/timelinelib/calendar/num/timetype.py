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


"""Contains the class NumTimeType."""


import math
import re

from timelinelib.calendar.num.time import NumDelta
from timelinelib.calendar.num.time import NumTime
from timelinelib.calendar.timetype import TimeType
from timelinelib.canvas.data import TimePeriod
from timelinelib.canvas.data import time_period_center
from timelinelib.canvas.drawing.interface import Strip


class NumTimeType(TimeType):

    """The class."""

    def __eq__(self, other):
        return isinstance(other, NumTimeType)

    def __ne__(self, other):
        return not (self == other)

    def time_string(self, time):
        return "%s" % (time.value)

    def parse_time(self, time_string):
        match = re.search(r"^([-]?\d+(.\d+)?(e[+]\d+)?)$", time_string)
        if match:
            if '.' in time_string or 'e' in time_string:
                time = float(match.group(1))
            else:
                time = int(match.group(1))
            try:
                return NumTime(time)
            except ValueError:
                raise ValueError("Invalid time, time string = '%s'" % time_string)
        else:
            raise ValueError("Time not on correct format = '%s'" % time_string)

    def get_navigation_functions(self):
        return [
            (_("Go to &Zero") + "\tCtrl+Z", go_to_zero_fn),
            (_("Go to &Time") + "\tCtrl+T", go_to_time_fn),
            ("SEP", None),
            (_("Backward") + "\tPgUp", backward_fn),
            (_("Forward") + "\tPgDn", forward_fn),
        ]

    def format_period(self, time_period):
        """Returns a unicode string describing the time period."""
        if time_period.is_period():
            label = "%s to %s" % (
                time_period.start_time.value,
                time_period.end_time.value
            )
        else:
            label = "%s" % time_period.start_time.value
        return label

    def format_delta(self, delta):
        return "%d" % delta.value

    def get_min_time(self):
        return None

    def get_max_time(self):
        return None

    def choose_strip(self, metrics, appearance):
        # Choose an exponent that will make the minor strip just larger than
        # the displayed period:
        #
        #     10**x > period_delta   =>
        #     x > log(period_delta)
        exponent = int(math.log(metrics.time_period.delta().value, 10)) + 1
        # Keep decreasing the exponent until the minor strip is small enough.
        while True:
            if exponent == 0:
                break
            next_minor_strip_with_px = metrics.calc_exact_width(
                TimePeriod(
                    NumTime(0),
                    NumTime(10 ** (exponent - 1))
                )
            )
            if next_minor_strip_with_px > 30:
                exponent -= 1
            else:
                break
        return (NumStrip(10 ** (exponent + 1)), NumStrip(10 ** exponent))

    def get_default_time_period(self):
        return time_period_center(NumTime(0), NumDelta(100))

    def now(self):
        return NumTime(0)

    def get_min_zoom_delta(self):
        return (NumDelta(5), _("Can't zoom deeper than 5"))

    def get_name(self):
        return "numtime"

    def get_duplicate_functions(self):
        return [
            (_("1-period"), lambda p, d: move_period(p, d)),
            (_("10-period"), lambda p, d: move_period(p, d * 10)),
            (_("100-period"), lambda p, d: move_period(p, d * 100)),
            (_("1000-period"), lambda p, d: move_period(p, d * 1000)),
        ]

    def supports_saved_now(self):
        return False

    def create_time_picker(self, parent, *args, **kwargs):
        from timelinelib.calendar.num.timepicker import NumTimePicker
        return NumTimePicker(parent, *args, **kwargs)

    def create_period_picker(self, parent, *args, **kwargs):
        from timelinelib.calendar.num.periodpicker import NumPeriodPicker
        return NumPeriodPicker(parent, *args, **kwargs)


class NumStrip(Strip):

    def __init__(self, size):
        self.size = size

    def label(self, time, major=False):
        return "%s" % time.value

    def start(self, time):
        start = int(time.value / self.size) * self.size
        if time < NumTime(0):
            start -= self.size
        return NumTime(start)

    def increment(self, time):
        return time + NumDelta(self.size)


def go_to_zero_fn(main_frame, current_period, navigation_fn):
    navigation_fn(lambda tp: tp.center(NumTime(0)))


def go_to_time_fn(main_frame, current_period, navigation_fn):
    def navigate_to(time):
        navigation_fn(lambda tp: tp.center(time))
    main_frame.display_time_editor_dialog(
        NumTimeType(),
        current_period.mean_time(),
        navigate_to,
        _("Go to Time")
    )


def backward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.start_time - current_period.end_time
    navigation_fn(lambda tp: tp.move_delta(delta))


def forward_fn(main_frame, current_period, navigation_fn):
    delta = current_period.end_time - current_period.start_time
    navigation_fn(lambda tp: tp.move_delta(delta))


def move_period(period, num):
    delta = NumDelta(num)
    start_time = period.start_time + delta
    end_time = period.end_time + delta
    return TimePeriod(start_time, end_time)
