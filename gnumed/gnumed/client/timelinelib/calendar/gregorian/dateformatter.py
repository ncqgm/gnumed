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


from timelinelib.calendar.gregorian.gregorian import days_in_month
from timelinelib.calendar.gregorian.monthnames import abbreviated_name_of_month
from timelinelib.calendar.gregorian.monthnames import month_of_abbreviated_name


class GregorianDateFormatter(object):

    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"

    def __init__(self):
        self.set_separators("-", "-")
        self.set_region_order(year=0, month=1, day=2)
        self.use_abbreviated_name_for_month(False)
        self.use_date_default_values = False
        self.default_year = '2000'
        self.default_month = '01'
        self.default_day = '01'

    def use_abbreviated_name_for_month(self, value):
        self._use_abbreviated_name_for_month = value

    def set_separators(self, first, second):
        if not first or not second:
            raise ValueError("Can not set empty separator.")
        self._first_separator = first
        self._second_separator = second

    def set_region_order(self, year, month, day):
        if set([year, month, day]) != set([0, 1, 2]):
            raise ValueError("Invalid region order. Must be a combination of 0, 1, and 2.")
        self._year_position = year
        self._month_position = month
        self._day_position = day

    def set_defaults(self, use_date_default_values, default_year=None, default_month=None, default_day=None):
        self.use_date_default_values = use_date_default_values
        self.default_year = default_year
        self.default_month = default_month
        self.default_day = default_day
        
    def format(self, ymd_tuple):
        (year, month, day) = ymd_tuple
        return (self._format_date(year, month, day), self._is_bc(year))

    def parse(self, date_bc_tuple):
        (date, is_bc) = date_bc_tuple
        regions = self._split(date)
        if self.use_date_default_values:
            self.set_default_regions(regions, date)
        year = self._parse_year(regions[self._year_position], is_bc)
        month = self._parse_month(regions[self._month_position])
        day = self._parse_day(regions[self._day_position], year, month)
        return (year, month, day)

    def set_default_regions(self, regions, date):
        if regions == ['', '', '']:
            regions[0] = date
        for n in range(3):
            if regions[n] == '':
                self.set_default_for_region(regions, n)

    def set_default_for_region(self, regions, n):
        if self._year_position == n:
            regions[n] = self.default_year
        elif self._month_position == n:
            regions[n] = self.default_month
        elif self._day_position == n:
            regions[n] = self.default_day
          
    def get_region_type(self, date_string, cursor_position):
        return {
            self._year_position: self.YEAR,
            self._month_position: self.MONTH,
            self._day_position: self.DAY,
        }[self._get_region(date_string, cursor_position)]

    def _get_region(self, date_string, cursor_position):
        if cursor_position < self._get_region_start(date_string, 1):
            return 0
        elif cursor_position < self._get_region_start(date_string, 2):
            return 1
        else:
            return 2

    def _split(self, date_string):
        region_1 = region_2 = region_3 = ''
        try:
            (region_1, region_2) = date_string.split(self._first_separator, 1)
            (region_2, region_3) = region_2.split(self._second_separator, 1)
        except ValueError:
            pass
        return [
            region_1,
            region_2,
            region_3,
        ]

    def get_next_region(self, date_string, cursor_position):
        if self._cursor_at_end_of_string(date_string, cursor_position):
            return None
        for region in [1, 2]:
            if cursor_position < self._get_region_start(date_string, region):
                return self._get_region_selection(date_string, region)
        return None

    def _cursor_at_end_of_string(self, date_string, cursor_position):
        return cursor_position == len(date_string)

    def get_previous_region(self, date_string, cursor_position):
        for region in [1, 0]:
            if cursor_position > self._get_region_end(date_string, region):
                return self._get_region_selection(date_string, region)
        return None

    def _get_region_selection(self, date_string, which_region):
        return (self._get_region_start(date_string, which_region),
                self._get_region_len(date_string, which_region))

    def _get_region_len(self, date_string, which_region):
        return len(self._split(date_string)[which_region])

    def _get_region_start(self, date_string, which_region):
        part_delimiter = {
            0: 0,
            1: 2,
            2: 4,
        }[which_region]
        return len("".join(self._get_all_parts(date_string)[:part_delimiter]))

    def _get_region_end(self, date_string, which_region):
        part_delimiter = {
            0: 1,
            1: 3,
            2: 5,
        }[which_region]
        return len("".join(self._get_all_parts(date_string)[:part_delimiter]))

    def _get_all_parts(self, date_string):
        regions = self._split(date_string)
        return [
            regions[0],
            self._first_separator,
            regions[1],
            self._second_separator,
            regions[2],
        ]

    def _format_date(self, year, month, day):
        regions = {
            self._year_position: self._format_year(year),
            self._month_position: self._format_month(month),
            self._day_position: self._format_day(day),
        }
        return "".join([
            regions[0],
            self._first_separator,
            regions[1],
            self._second_separator,
            regions[2],
        ])

    def _format_year(self, year):
        if self._is_bc(year):
            new_year = 1 - year
        else:
            new_year = year
        return "%04d" % new_year

    def _is_bc(self, year):
        return year <= 0

    def _parse_year(self, year_string, is_bc):
        if is_bc:
            return 1 - int(year_string)
        else:
            return int(year_string)

    def _format_month(self, month):
        if self._use_abbreviated_name_for_month:
            return abbreviated_name_of_month(month)
        else:
            return "%02d" % month

    def _parse_month(self, month_string):
        if self._use_abbreviated_name_for_month:
            return month_of_abbreviated_name(month_string)
        else:
            month = int(month_string)
            if month - 1 in range(12):
                return month
            else:
                raise ValueError("Invalid month")

    def _format_day(self, day):
        return "%02d" % day

    def _parse_day(self, day_string, year, month):
        day = int(day_string)
        if day - 1 in range(days_in_month(year, month)):
            return day
        else:
            raise ValueError("Invalid day")
