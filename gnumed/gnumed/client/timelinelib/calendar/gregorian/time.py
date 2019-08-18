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


from timelinelib.calendar.time import ComparableValue
from timelinelib.calendar.time import GenericDeltaMixin
from timelinelib.calendar.time import GenericTimeMixin


SECONDS_IN_DAY = 24 * 60 * 60


class GregorianTime(GenericTimeMixin):

    MIN_JULIAN_DAY = 0

    @property
    def DeltaClass(self):
        return GregorianDelta

    @classmethod
    def min(cls):
        return cls(cls.MIN_JULIAN_DAY, 0)

    @classmethod
    def set_min_julian_day(cls, allow_negative_julian_yeras):
        if allow_negative_julian_yeras:
            cls.MIN_JULIAN_DAY = -1000000000000000000000000000000000000000000000000
        else:
            cls.MIN_JULIAN_DAY = 0

    def __init__(self, julian_day, seconds):
        if julian_day < self.MIN_JULIAN_DAY:
            raise ValueError("julian_day must be >= %d" % self.MIN_JULIAN_DAY)
        if seconds < 0 or seconds >= SECONDS_IN_DAY:
            raise ValueError("seconds must be >= 0 and <= 24*60*60")
        self.julian_day = julian_day
        self.seconds = seconds

    def __eq__(self, time):
        return (isinstance(time, self.__class__) and
                self.julian_day == time.julian_day and
                self.seconds == time.seconds)

    def __ne__(self, time):
        return not (self == time)

    def __add__(self, delta):
        if isinstance(delta, self.DeltaClass):
            seconds = self.seconds + delta.seconds
            seconds_in_day = int(self.julian_day + seconds / SECONDS_IN_DAY)
            return self.__class__(seconds_in_day, seconds % SECONDS_IN_DAY)
        raise TypeError(
            "%s + %s not supported" % (self.__class__.__name__, type(delta))
        )

    def __sub__(self, other):
        if isinstance(other, self.DeltaClass):
            seconds = self.seconds - other.seconds
            if seconds < 0:
                if seconds % SECONDS_IN_DAY == 0:
                    days = abs(seconds) // SECONDS_IN_DAY
                    seconds = 0
                else:
                    days = abs(seconds) // SECONDS_IN_DAY + 1
                    seconds = SECONDS_IN_DAY - abs(seconds) % SECONDS_IN_DAY
                return self.__class__(self.julian_day - days, seconds)
            else:
                return self.__class__(self.julian_day, seconds)
        else:
            days_diff = self.julian_day - other.julian_day
            seconds_diff = self.seconds - other.seconds
            return self.DeltaClass(days_diff * SECONDS_IN_DAY + seconds_diff)

    def __gt__(self, dt):
        return (self.julian_day, self.seconds) > (dt.julian_day, dt.seconds)

    def __ge__(self, dt):
        return self == dt or self > dt

    def __lt__(self, dt):
        return (self.julian_day, self.seconds) < (dt.julian_day, dt.seconds)

    def __repr__(self):
        return "{0}({1!r}, {2!r})".format(
            self.__class__.__name__,
            self.julian_day,
            self.seconds
        )
    
    def to_str(self):
        from timelinelib.calendar.gregorian.gregorian import GregorianDateTime
        return GregorianDateTime.from_time(self)
    
    def get_time_of_day(self):
        hours = self.seconds // 3600
        minutes = (self.seconds // 60) % 60
        seconds = self.seconds % 60
        return (hours, minutes, seconds)


class GregorianDelta(ComparableValue, GenericDeltaMixin):

    @classmethod
    def from_seconds(cls, seconds):
        return cls(seconds)

    @classmethod
    def from_days(cls, days):
        return cls(SECONDS_IN_DAY * days)

    @property
    def seconds(self):
        return self.value

    def __div__(self, value):
        if isinstance(value, self.__class__):
            return float(self.seconds) / float(value.seconds)
        else:
            return self.__class__(self.seconds // value)

    def __truediv__(self, value):
        if isinstance(value, self.__class__):
            return float(self.seconds) / float(value.seconds)
        else:
            return self.__class__(self.seconds // value)

    def __sub__(self, delta):
        return self.__class__(self.seconds - delta.seconds)

    def __mul__(self, value):
        return self.__class__(int(self.seconds * value))

    def get_days(self):
        return self.seconds // SECONDS_IN_DAY

    def get_hours(self):
        return (self.seconds // (60 * 60)) % 24

    def get_minutes(self):
        return (self.seconds // 60) % 60

    def __repr__(self):
        return "{0}({1!r})".format(
            self.__class__.__name__,
            self.seconds
        )
