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


class Metrics(object):
    """
    Convert between pixel coordinates and time coordinates.
    """

    def __init__(self, size, time_type, time_period, divider_line_slider):
        self.width, self.height = size
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_height = int(round(divider_line_slider * self.height))
        self.time_type = time_type
        self.time_period = time_period

    def calc_exact_x(self, time):
        """Return the x position in pixels as a float for the given time."""
        return self.width * (
            (time - self.time_period.start_time) / self.time_period.delta()
        )

    def calc_x(self, time):
        """Return the x position in pixels as an integer for the given time."""
        try:
            return int(round(self.calc_exact_x(time)))
        except OverflowError:
            if time < self.time_period.start_time:
                return -1
            if time > self.time_period.end_time:
                return self.width + 1

    def calc_exact_width(self, time_period):
        """Return the with in pixels as a float for the given time_period."""
        return (self.calc_exact_x(time_period.end_time) -
                self.calc_exact_x(time_period.start_time))

    def calc_width(self, time_period):
        """Return the with in pixels as an integer for the given time_period."""
        return (self.calc_x(time_period.end_time) -
                self.calc_x(time_period.start_time)) + 1

    def get_time(self, x):
        """Return the time at pixel `x`."""
        if self.width == 0:
            x_percent_of_width = 0
        else:
            x_percent_of_width = float(x) / self.width
        return self.time_period.get_time_at_percent(x_percent_of_width)

    def get_difftime(self, x1, x2):
        """Return the time length between two x positions."""
        return self.get_time(x1) - self.get_time(x2)


def darken_color(color, factor=0.7):
    if (factor < 0.0 or factor > 1.0):
        return color
    return tuple([int(x * factor) for x in color])


def lighten_color(color, factor=1.5):
    if (factor < 1.0 or factor > 255.0):
        return color
    if (color == (0, 0, 0)):
        color = (1, 1, 1)  # avoid multiplying factor by zero
    return tuple([min(int(x * factor), 255) for x in color])


def get_colour(rgb_tuple):
    return wx.Colour(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
