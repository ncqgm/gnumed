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


import timelinelib.time.timeline as timeline


class Gregorian(object):

    def __init__(self, year, month, day, hour, minute, second):
        if not is_valid(year, month, day):
            raise ValueError("Invalid gregorian date %s-%s-%s" % (year, month, day))
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def replace(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return Gregorian(year, month, self.day,
                         self.hour, self.minute, self.second)

    def days_in_month(self):
        return days_in_month(self.year, self.month)

    def to_tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute,
                self.second)

    def to_date_tuple(self):
        return (self.year, self.month, self.day)

    def to_time_tuple(self):
        return (self.hour, self.minute, self.second)

    def to_time(self):
        days = to_julian_day(self.year, self.month, self.day)
        seconds = self.hour * 60 * 60 + self.minute * 60 + self.second
        return timeline.Time(days, seconds)

    def __eq__(self, other):
        return (isinstance(other, Gregorian) and
                self.to_tuple() == other.to_tuple())

    def __repr__(self):
        return "Gregorian<%d-%02d-%02d %02d:%02d:%02d>" % self.to_tuple()


def is_valid(year, month, day):
    return (month >= 1
       and  month <= 12
       and  day >= 1
       and  day <= days_in_month(year, month))


def is_valid_time(hour, minute, second):
    return (hour >= 0
       and hour < 24
       and minute >= 0
       and minute < 60
       and second >= 0
       and second < 60)


def days_in_month(year, month):
    if month in [4, 6, 9, 11]:
        return 30
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if is_leap_year(year):
        return 29
    return 28


def is_leap_year(year):
    return year % 4 == 0 and (year % 400 == 0 or not year % 100 == 0)


def from_julian_day(julian_day):
    """
    This algorithm is described here:

    * http://www.tondering.dk/claus/cal/julperiod.php#formula

    Integer division works differently in C and in Python for negative numbers.
    C truncates towards 0 and Python truncates towards negative infinity:
    http://python-history.blogspot.se/2010/08/why-pythons-integer-division-floors.html

    The above source don't state which to be used. If we can prove that
    division-expressions are always positive, we can be sure this algorithm
    works the same in C and in Python.

    We must prove that:

    1) m             >= 0
    2) ((5 * e) + 2) >= 0  =>  e >= 0
    3) (1461 * d)    >= 0  =>  d >= 0
    4) ((4 * c) + 3) >= 0  =>  c >= 0
    5) (b * 146097)  >= 0  =>  b >= 0
    6) ((4 * a) + 3) >= 0  =>  a >= 0

    Let's work from the top:

    julian_day >= 0                   =>

    a >= 0 + 32044
       = 32044                        =>

    This proves 6).

    b >= ((4 * 32044) + 3) // 146097
       = 0

    This proves 5).

    Let's look at c:

    c = a - ((b * 146097) // 4)
      = a - (((((4 * a) + 3) // 146097) * 146097) // 4)

    For c to be >= 0, then

    (((((4 * a) + 3) // 146097) * 146097) // 4) <= a

    Let's look at this component: ((((4 * a) + 3) // 146097) * 146097)

    This expression can never be larger than (4 * a) + 3. That gives this:

    ((4 * a) + 3) // 4 <= a, which holds.

    This proves 4).

    Now, let's look at d:

    d = ((4 * c) + 3) // 1461

    If c is >= 0, then d is also >= 0.

    This proves 3).

    Let's look at e:

    e = c - ((1461 * d) // 4)
      = c - ((1461 * (((4 * c) + 3) // 1461)) // 4)

    The same resoning as above can be used to conclude that e >= 0.

    This proves 2).

    Now, let's look at m:

    m = ((5 * e) + 2) // 153

    If e >= 0, then m is also >= 0.

    This proves 1).
    """
    if julian_day < 0:
        raise ValueError("from_julian_day only works for positive julian days, but was %s" % julian_day)
    a = julian_day + 32044
    b = ((4 * a) + 3) // 146097
    c = a - ((b * 146097) // 4)
    d = ((4 * c) + 3) // 1461
    e = c - ((1461 * d) // 4)
    m = ((5 * e) + 2) // 153
    day = e - (((153 * m) + 2) // 5) + 1
    month = m + 3 - (12 * (m // 10))
    year = (b * 100) + d - 4800 + (m // 10)
    return (year, month, day)


def to_julian_day(year, month, day):
    """
    This algorithm is described here:

    * http://www.tondering.dk/claus/cal/julperiod.php#formula
    * http://en.wikipedia.org/wiki/Julian_day#Converting_Julian_or_Gregorian_calendar_date_to_Julian_Day_Number

    Integer division works differently in C and in Python for negative numbers.
    C truncates towards 0 and Python truncates towards negative infinity:
    http://python-history.blogspot.se/2010/08/why-pythons-integer-division-floors.html

    The above sources don't state which to be used. If we can prove that
    division-expressions are always positive, we can be sure this algorithm
    works the same in C and in Python.

    We must prove that:

    1) y >= 0
    2) ((153 * m) + 2) >= 0

    Let's prove 1):

    y = year + 4800 - a
      = year + 4800 - ((14 - month) // 12)

    year >= -4713 (gives a julian day of 0)

    so

    year + 4800 >= -4713 + 4800 = 87

    The expression ((14 - month) // 12) varies between 0 and 1 when month
    varies between 1 and 12. Therefore y >= 87 - 1 = 86, and 1) is proved.

    Let's prove 2):

    m = month + (12 * a) - 3
      = month + (12 * ((14 - month) // 12)) - 3

    1 <= month <= 12

    m(1)  = 1  + (12 * ((14 - 1)  // 12)) - 3 = 1  + (12 * 1) - 3 = 10
    m(2)  = 2  + (12 * ((14 - 2)  // 12)) - 3 = 2  + (12 * 1) - 3 = 11
    m(3)  = 3  + (12 * ((14 - 3)  // 12)) - 3 = 3  + (12 * 0) - 3 = 0
    m(4)  = 4  + (12 * ((14 - 4)  // 12)) - 3 = 4  + (12 * 0) - 3 = 1
    m(5)  = 5  + (12 * ((14 - 5)  // 12)) - 3 = 5  + (12 * 0) - 3 = 2
    m(6)  = 6  + (12 * ((14 - 6)  // 12)) - 3 = 6  + (12 * 0) - 3 = 3
    m(7)  = 7  + (12 * ((14 - 7)  // 12)) - 3 = 7  + (12 * 0) - 3 = 4
    m(8)  = 8  + (12 * ((14 - 8)  // 12)) - 3 = 8  + (12 * 0) - 3 = 5
    m(9)  = 9  + (12 * ((14 - 9)  // 12)) - 3 = 9  + (12 * 0) - 3 = 6
    m(10) = 10 + (12 * ((14 - 10) // 12)) - 3 = 10 + (12 * 0) - 3 = 7
    m(11) = 11 + (12 * ((14 - 11) // 12)) - 3 = 11 + (12 * 0) - 3 = 8
    m(12) = 12 + (12 * ((14 - 12) // 12)) - 3 = 12 + (12 * 0) - 3 = 9

    So, m is always > 0. Which also makes the expression ((153 * m) + 2) > 0,
    and 2) is proved.
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + (12 * a) - 3
    julian_day = (day
                  + (((153 * m) + 2) // 5)
                  + (y * 365)
                  + (y // 4)
                  - (y // 100)
                  + (y // 400)
                  - 32045)
    if julian_day < 0:
        raise ValueError("to_julian_day only works for positive julian days, but was %s" % julian_day)
    return julian_day


def gregorian_week(time):
    def monday_week_1(year):
        jan_4 = from_date(year, 1, 4).to_time()
        return jan_4 - timeline.delta_from_days(jan_4.get_day_of_week())
    def days_between(end, start):
        return end.julian_day - start.julian_day
    def days_since_monday_week_1(time):
        year = from_time(time).year
        diff = days_between(end=time, start=monday_week_1(year + 1))
        if diff >= 0:
            return diff
        diff = days_between(end=time, start=monday_week_1(year))
        if diff >= 0:
            return diff
        diff = days_between(end=time, start=monday_week_1(year - 1))
        if diff >= 0:
            return diff
        raise ValueError("should not end up here")
    return days_since_monday_week_1(time) / 7 + 1


def from_time(time):
    (year, month, day) = from_julian_day(time.julian_day)
    (hour, minute, second) = time.get_time_of_day()
    return Gregorian(year, month, day, hour, minute, second)


def from_date(year, month, day):
    return Gregorian(year, month, day, 0, 0, 0)
