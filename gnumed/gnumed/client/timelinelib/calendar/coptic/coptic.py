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


from timelinelib.calendar.coptic.time import CopticDelta
from timelinelib.calendar.coptic.time import CopticTime


FIRST_DAY = 1825030       


class CopticDateTime(object):

    def __init__(self, year, month, day, hour, minute, second):
        if not is_valid(year, month, day):
            raise ValueError("Invalid coptic date %s-%s-%s" % (year, month, day))
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.to_tuple() == other.to_tuple())

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def from_ymd(cls, year, month, day):
        return cls(year, month, day, 0, 0, 0)

    @classmethod
    def from_time(cls, time):
        (year, month, day) = julian_day_to_coptic_ymd(time.julian_day)
        (hour, minute, second) = time.get_time_of_day()
        return cls(year, month, day, hour, minute, second)
        
    @property
    def week_number(self):
        def tkyriaka_week_1(year):
            from timelinelib.calendar.coptic.timetype import CopticTimeType
            thoth_4 = CopticDateTime.from_ymd(year, 1, 4).to_time()
            thoth_4_day_of_week = CopticTimeType().get_day_of_week(thoth_4)
            return thoth_4 - CopticDelta.from_days(thoth_4_day_of_week)

        def days_between(end, start):
            return end.julian_day - start.julian_day

        def days_since_tkyriaka_week_1(time):
            year = CopticDateTime.from_time(time).year
            diff = days_between(end=time, start=tkyriaka_week_1(year + 1))
            if diff >= 0:
                return diff
            diff = days_between(end=time, start=tkyriaka_week_1(year))
            if diff >= 0:
                return diff
            diff = days_between(end=time, start=tkyriaka_week_1(year - 1))
            if diff >= 0:
                return diff
            raise ValueError("should not end up here")
        # TODO: days_since_monday_week_1, unresolved!!!
        return days_since_monday_week_1(self.to_time()) // 7 + 1
    """
        if self.month == 13:
            return 0
        
        length_of_week = 10
        days_into_year = ((self.month - 1)*30) + self.day
               
        if self.day % length_of_week > 0:
            return (days_into_year / length_of_week) + 1
        
        return days_into_year / length_of_week
        """
         
    def is_bc(self):
        return self.year <= 0

    def replace(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return self.__class__(
            year,
            month,
            self.day,
            self.hour,
            self.minute,
            self.second
        )

    def days_in_month(self):
        return days_in_month(self.year, self.month)

    def to_tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute,
                self.second)

    def to_date_tuple(self):
        return self.year, self.month, self.day

    def to_time_tuple(self):
        return self.hour, self.minute, self.second

    def to_time(self):
        days = coptic_ymd_to_julian_day(self.year, self.month, self.day)
        seconds = self.hour * 60 * 60 + self.minute * 60 + self.second
        return CopticTime(days, seconds)

    def is_first_day_in_year(self):
        return (self.month == 1 and
                self.day == 1 and
                self.hour == 0 and
                self.minute == 0 and
                self.second == 0)

    def is_first_of_month(self):
        return (self.day == 1 and
                self.hour == 0 and
                self.minute == 0 and
                self.second == 0)

    def __repr__(self):
        return "CopticDateTime<%d-%02d-%02d %02d:%02d:%02d>" % self.to_tuple()


def days_in_month(year, month):
    if month <= 12:
        return 30
    elif is_leap_year(year):
        return 6
    else:
        return 5


def is_leap_year(year):
    if year > 0 and (year+1) % 4 == 0:
        return True
    elif year < 0 and year % 4 == 0:
        return True
    else:
        return False


def num_leap_years(year):
    return int(abs(year//4))


def is_valid_time(hour, minute, second):
    return (
        hour >= 0 and hour < 24 and
        minute >= 0 and minute < 60 and
        second >= 0 and second < 60
    )


def is_valid(year, month, day):
    return month >= 1 and month <= 13 and day >= 1 and day <= days_in_month(year, month)


def julian_day_to_coptic_ymd(julian_day):
    """
    This calendar calculation was originally published in Explanatory Supplement to the Astronomical Almanac, S.E. Urban and P.K. Seidelman, Eds. (2012). You can purchase the book at uscibooks.com/urban.htm. "15.11 Calendar Conversion Algorithms" from the following pdf is used in the below code. https://aa.usno.navy.mil/publications/docs/c15_usb_online.pdf
    """
    if julian_day < CopticTime.MIN_JULIAN_DAY:
        raise ValueError("coptic_day_to_gregorian_ymd only works for julian days >= %d, but was %d" % (CopticTime.MIN_JULIAN_DAY, julian_day))
    # year_inx = int((julian_day - FIRST_DAY) / 365)
    # days_inx = (julian_day - FIRST_DAY) - year_inx * 365
    # month_inx = days_inx / 30
    # day_inx = days_inx - month_inx * 30
    
    y = 4996
    j = 124
    m = 0
    n = 13
    r = 4
    p = 1461
    q = 0
    v = 3
    u = 1
    s = 30
    t = 0
    w = 0
    
    f = julian_day + j
    e = r * f + v
    g = (e % p)//r
    h = u * g + w
    day = ((h % s)//u) + 1
    month = (((h // s) + m) % n) + 1
    year = (e // p) - y + (n + m - month)//n
    return year, month, day
    # return (year_inx + 1, month_inx + 1, day_inx + 1)


def coptic_ymd_to_julian_day(year, month, day):
    """
    Coptic year 1 = Julian day 1825030
    """
    # julian_day = FIRST_DAY + (year - 1) * 365 + (month - 1) * 30 + (day - 1)
    # num_leap_days = num_leap_years(year)
    # julian_day = FIRST_DAY + (year - 1 - num_leap_days)*365 + num_leap_days*366 + (month - 1)*30 + (day - 1)
   
    y = 4996
    j = 124
    m = 0
    n = 13
    r = 4
    p = 1461
    q = 0
    v = 3
    u = 1
    s = 30
    t = 0
    w = 0
    
    h = month - m
    g = year + y - (n-h)//n
    f = (h - 1 + n) % n
    e = (p * g + q)//r + day - 1 -j
    julian_day = e + (s * f + t)//u
    
    if julian_day < CopticTime.MIN_JULIAN_DAY:
        raise ValueError("coptic_ymd_to_julian_day only works for julian days >= %d, but was %d" % (CopticTime.MIN_JULIAN_DAY, julian_day))
    return julian_day
