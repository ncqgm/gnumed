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


SECONDS_IN_DAY = 24 * 60 * 60


class Time(object):

    def __init__(self, julian_day, seconds):
        if julian_day < 0:
            raise ValueError("julian_day must be >= 0")
        if seconds < 0 or seconds >= SECONDS_IN_DAY:
            raise ValueError("seconds must be >= 0 and <= 24*60*60")
        self.julian_day = julian_day
        self.seconds = seconds

    def __eq__(self, time):
        return (isinstance(time, Time) and
                self.julian_day == time.julian_day and
                self.seconds == time.seconds)

    def __ne__(self, time):
        return not self.__eq__(time)

    def __add__(self, delta):
        if isinstance(delta, TimeDelta):
            seconds = self.seconds + delta.seconds
            return Time(self.julian_day + seconds / SECONDS_IN_DAY, seconds % SECONDS_IN_DAY)
        raise TypeError("Time + %s not supported" % type(delta))

    def __sub__(self, other):
        if isinstance(other, TimeDelta):
            seconds = self.seconds - other.seconds
            if seconds < 0:
                if seconds % SECONDS_IN_DAY == 0:
                    days = abs(seconds) / SECONDS_IN_DAY
                    seconds = 0
                else:
                    days = abs(seconds) / SECONDS_IN_DAY + 1
                    seconds = SECONDS_IN_DAY - abs(seconds) % SECONDS_IN_DAY
                return Time(self.julian_day - days, seconds)
            else:
                return Time(self.julian_day, seconds)
        else:
            days_diff = self.julian_day - other.julian_day
            seconds_diff = self.seconds - other.seconds
            return TimeDelta(days_diff * SECONDS_IN_DAY + seconds_diff)

    def __gt__(self, dt):
        return (self.julian_day, self.seconds) > (dt.julian_day, dt.seconds)

    def __ge__(self, dt):
        return self == dt or self > dt

    def __lt__(self, dt):
        return (self.julian_day, self.seconds) < (dt.julian_day, dt.seconds)

    def __repr__(self):
        return "Time<%s, %s>" % (self.julian_day, self.seconds)

    def get_time_of_day(self):
        hours = self.seconds / 3600
        minutes = (self.seconds / 60) % 60
        seconds = self.seconds % 60
        return (hours, minutes, seconds)

    def get_day_of_week(self):
        return self.julian_day % 7


class TimeDelta(object):

    def __init__(self, seconds):
        self.seconds = seconds

    def __div__(self, value):
        if isinstance(value, TimeDelta):
            return float(self.seconds) / float(value.seconds)
        else:
            return TimeDelta(self.seconds / value)

    def __sub__(self, delta):
        return TimeDelta(self.seconds - delta.seconds)

    def __neg__(self):
        return TimeDelta(-self.seconds)

    def __mul__(self, value):
        return TimeDelta(int(self.seconds * value))

    def __rmul__(self, value):
        return self * value

    def __eq__(self, d):
        return isinstance(d, TimeDelta) and self.seconds == d.seconds

    def __gt__(self, d):
        return self.seconds > d.seconds

    def __lt__(self, d):
        return self.seconds < d.seconds

    def get_days(self):
        return self.seconds / SECONDS_IN_DAY

    def get_hours(self):
        return (self.seconds / (60 * 60)) % 24

    def get_minutes(self):
        return (self.seconds / 60) % 60

    def __repr__(self):
        return "TimeDelta[%s]" % self.seconds


def delta_from_seconds(seconds):
    return TimeDelta(seconds)


def delta_from_days(days):
    return TimeDelta(SECONDS_IN_DAY * days)
