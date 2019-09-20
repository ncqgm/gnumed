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


class TimeType(object):

    def time_string(self, time):
        raise NotImplementedError("time_string not implemented.")

    def parse_time(self, time_string):
        raise NotImplementedError("parse_time not implemented.")

    def get_navigation_functions(self):
        raise NotImplementedError("get_navigation_functions not implemented.")

    def format_period(self, time_period):
        raise NotImplementedError("format_period not implemented.")

    def format_delta(self, time_period):
        raise NotImplementedError("format_delta not implemented.")

    def get_min_time(self):
        raise NotImplementedError("return the min time for this time type.")

    def get_max_time(self):
        raise NotImplementedError("return the max time for this time type.")

    def choose_strip(self, metrics, appearance):
        raise NotImplementedError("choose_strip not implemented.")

    def get_default_time_period(self):
        raise NotImplementedError("get_default_time_period not implemented.")

    def supports_saved_now(self):
        raise NotImplementedError("supports_saved_now not implemented.")

    def set_saved_now(self, time):
        raise NotImplementedError("set_saved_now not implemented.")

    def now(self):
        raise NotImplementedError("now not implemented.")

    def get_min_zoom_delta(self):
        raise NotImplementedError("get_min_zoom_delta not implemented.")

    def get_name(self):
        raise NotImplementedError("get_name not implemented.")

    def get_duplicate_functions(self):
        raise NotImplementedError("get_duplicate_functions not implemented.")

    def is_special_day(self, time):
        raise NotImplementedError("is_special_day not implemented.")

    def is_weekend_day(self, time):
        raise NotImplementedError("is_weekend_day not implemented.")
