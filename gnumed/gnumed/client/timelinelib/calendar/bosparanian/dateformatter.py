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


from timelinelib.calendar.bosparanian.monthnames import bosp_abbreviated_name_of_month
from timelinelib.calendar.bosparanian.monthnames import bosp_month_from_abbreviated_name


class BosparanianDateFormatter(object):

    def __init__(self):
        self._separator = "-"

    def format(self, year, month, day):
        mstr = bosp_abbreviated_name_of_month(month)
        return ("%4d-%3s-%02d" % (year, mstr, day), self._is_bc_year(year))

    def parse(self, dt):
        try:
            year, mstr, day = dt.rsplit(self._separator, 2)
        except:
            raise ValueError()
        month = bosp_month_from_abbreviated_name(mstr)
        return int(year), int(month), int(day)

    def separator(self):
        return self._separator

    def get_regions(self):
        year = 0
        month = 1
        day = 2
        return year, month, day

    def _is_bc_year(self, year):
        return year <= 0
