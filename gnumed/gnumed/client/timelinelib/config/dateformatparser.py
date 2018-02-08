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


from timelinelib.calendar.gregorian.dateformatter import GregorianDateFormatter


REGION_START_POS = 0
REGION_LENGTH = 1
REGION_SEPARATOR = 2
REGION_TYPE = 3
YEAR = GregorianDateFormatter.YEAR
MONTH = GregorianDateFormatter.MONTH
DAY = GregorianDateFormatter.DAY
ERROR_TEXT = _("""\
Invalid Date Format:

The format should contain
    one year placeholder  = yyyy
    one month placeholder = mmm or mm
    one day placeholder   = dd
    two placeholders for separators between year, month and day

Separators can't contain the letters y, m or d

Example of valid formats:
    yyyy-mm-dd
    dd/mm/yyyy
    mmm/dd-yyyy
        """)


class DateFormatParser(object):

    def get_error_text(self):
        return ERROR_TEXT

    def is_valid(self, date_format):
        try:
            self.parse(date_format)
            return True
        except ValueError:
            return False

    def parse(self, date_format):
        self.regions = self._to_regions(date_format)
        return self

    def get_separators(self):
        return self.regions[1][REGION_SEPARATOR], self.regions[2][REGION_SEPARATOR]

    def get_region_order(self):
        return (self._get_region_type_index(YEAR), self._get_region_type_index(MONTH), self._get_region_type_index(DAY))

    def use_abbreviated_month_names(self):
        for i in range(len(self.regions)):
            if self.regions[i][REGION_TYPE] == MONTH:
                return self.regions[i][REGION_LENGTH] == 3
        return False

    def _get_region_type_index(self, region_type):
        for i in range(len(self.regions)):
            if self.regions[i][REGION_TYPE] == region_type:
                return i

    def _to_regions(self, date_format):
        fmt = date_format.lower()
        self._assert_leading_char_is_a_date_placeholder(date_format)
        self._assert_trailing_char_is_a_date_placeholder(date_format)
        fmt, regions = self._get_regions(fmt, date_format)
        self._get_separators_placeholders(fmt, regions)
        return regions

    def _assert_leading_char_is_a_date_placeholder(self, date_format):
        if date_format[0] not in ("y", "m", "d"):
            raise ValueError()

    def _assert_trailing_char_is_a_date_placeholder(self, date_format):
        if date_format[-1] not in ("y", "m", "d"):
            raise ValueError()

    def _get_separators_placeholders(self, fmt, regions):
        separator1_length = regions[1][REGION_START_POS] - regions[0][REGION_LENGTH]
        regions[1][REGION_SEPARATOR] = fmt[:separator1_length]
        regions[2][REGION_SEPARATOR] = fmt[separator1_length:]

    def _get_regions(self, fmt, date_format):
        def getKey(item):
            return item[0]
        fmt, region0 = self._get_and_remove_year_region(fmt, date_format)
        fmt, region1 = self._get_and_remove_month_region(fmt, date_format)
        fmt, region2 = self._get_and_remove_day_region(fmt, date_format)
        regions = [region0, region1, region2]
        if "y" in fmt or "m" in fmt or "d" in fmt:
            raise ValueError()
        regions.sort(key=getKey)
        return fmt, regions

    def _get_and_remove_year_region(self, fmt, date_format):
        return self._get_and_remove_region(fmt, date_format, "yyyy", YEAR)

    def _get_and_remove_month_region(self, fmt, date_format):
        if "mmm" in fmt:
            return self._get_and_remove_region(fmt, date_format, "mmm", MONTH)
        elif "mm" in fmt:
            return self._get_and_remove_region(fmt, date_format, "mm", MONTH)
        else:
            raise ValueError()

    def _get_and_remove_day_region(self, fmt, date_format):
        return self._get_and_remove_region(fmt, date_format, "dd", DAY)

    def _get_and_remove_region(self, fmt, date_format, placeholder, region_type):
        if placeholder in fmt:
            fmt = fmt.replace(placeholder, "", 1)
            index = date_format.lower().index(placeholder)
            return fmt, [index, len(placeholder), "", region_type]
        else:
            raise ValueError()
