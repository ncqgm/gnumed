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


class TimeType(object):

    def time_string(self, time):
        raise NotImplementedError("time_string not implemented.")

    def parse_time(self, time_string):
        raise NotImplementedError("parse_time not implemented.")

    def get_navigation_functions(self):
        raise NotImplementedError("get_navigation_functions not implemented.")

    def is_date_time_type(self):
        raise NotImplementedError("is_date_time_type not implemented.")

    def format_period(self, time_period):
        raise NotImplementedError("format_period not implemented.")

    def format_delta(self, time_period):
        raise NotImplementedError("format_delta not implemented.")

    def get_min_time(self):
        raise NotImplementedError("return the min time for this time type.")

    def get_max_time(self):
        raise NotImplementedError("return the max time for this time type.")

    def choose_strip(self, metrics, config):
        raise NotImplementedError("choose_strip not implemented.")

    def mult_timedelta(self, delta, num):
        raise NotImplementedError("mult_timedelta not implemented.")

    def get_default_time_period(self):
        raise NotImplementedError("get_default_time_period not implemented.")

    def now(self):
        raise NotImplementedError("now not implemented.")

    def get_time_at_x(self, time_period, x_percent_of_width):
        """Return the time at pixel `x`."""
        raise NotImplementedError("get_time_for_x not implemented.")

    def div_timedeltas(self, delta1, delta2):
        raise NotImplementedError("div_timedeltas not implemented.")

    def get_max_zoom_delta(self):
        raise NotImplementedError("get_max_zoom_delta not implemented.")

    def get_min_zoom_delta(self):
        raise NotImplementedError("get_max_zoom_delta not implemented.")

    def get_zero_delta(self):
        raise NotImplementedError("get_zero_delta not implemented.")

    def time_period_has_nonzero_time(self, time_period):
        raise NotImplementedError("time_period_has_nonzero_time not implemented.")

    def get_name(self):
        raise NotImplementedError("get_name not implemented.")

    def get_duplicate_functions(self):
        raise NotImplementedError("get_duplicate_functions not implemented.")

    def half_delta(self, delta):
        raise NotImplementedError("half_delta not implemented.")

    def margin_delta(self, delta):
        raise NotImplementedError("margin_delta not implemented.")

    def event_date_string(self, time):
        raise NotImplementedError("event_date_string not implemented.")

    def event_time_string(self, time):
        raise NotImplementedError("event_time_string not implemented.")

    def eventtimes_equals(self, time1, time2):
        raise NotImplementedError("eventtimes_equals not implemented.")

    def adjust_for_bc_years(self, time):
        raise NotImplementedError("adjust_for_bc_years not implemented.")
