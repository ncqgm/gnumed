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


from timelinelib.calendar.coptic.coptic import is_valid_time
from timelinelib.wxgui.components import TextPatternControl


class CopticTimePicker(TextPatternControl):

    HOUR_GROUP = 0
    MINUTE_GROUP = 1

    def __init__(self, parent):
        TextPatternControl.__init__(self, parent, fit_text="00:00")
        self.SetSeparators([":"])
        self.SetValidator(self._is_time_valid)
        self.SetUpHandler(self.HOUR_GROUP, self._increment_hour)
        self.SetUpHandler(self.MINUTE_GROUP, self._increment_minute)
        self.SetDownHandler(self.HOUR_GROUP, self._decrement_hour)
        self.SetDownHandler(self.MINUTE_GROUP, self._decrement_minute)

    def GetCopticTime(self):
        return parts_to_coptic_time(self.GetParts())

    def SetCopticTime(self, time):
        self.SetParts(coptic_time_to_parts(time))

    def _is_time_valid(self):
        try:
            self.GetCopticTime()
        except ValueError:
            return False
        else:
            return True

    def _increment_hour(self):
        self.SetCopticTime(increment_hour(self.GetCopticTime()))

    def _increment_minute(self):
        self.SetCopticTime(increment_minute(self.GetCopticTime()))

    def _decrement_hour(self):
        self.SetCopticTime(decrement_hour(self.GetCopticTime()))

    def _decrement_minute(self):
        self.SetCopticTime(decrement_minute(self.GetCopticTime()))


def coptic_time_to_parts(time):
    (hour, minute, second) = time
    return [
        "%02d" % hour,
        "%02d" % minute,
    ]


def parts_to_coptic_time(parts):
    [hour_str, minute_str] = parts
    hour = int(hour_str)
    minute = int(minute_str)
    if not is_valid_time(hour, minute, 0):
        raise ValueError()
    return (hour, minute, 0)


def increment_hour(time):
    hour, minute, second = time
    new_hour = hour + 1
    if new_hour > 23:
        new_hour = 0
    return (new_hour, minute, second)


def increment_minute(time):
    hour, minute, second = time
    new_hour = hour
    new_minute = minute + 1
    if new_minute > 59:
        new_minute = 0
        new_hour = hour + 1
        if new_hour > 23:
            new_hour = 0
    return (new_hour, new_minute, second)


def decrement_hour(time):
    hour, minute, second = time
    new_hour = hour - 1
    if new_hour < 0:
        new_hour = 23
    return (new_hour, minute, second)


def decrement_minute(time):
    hour, minute, second = time
    new_hour = hour
    new_minute = minute - 1
    if new_minute < 0:
        new_minute = 59
        new_hour = hour - 1
        if new_hour < 0:
            new_hour = 23
    return (new_hour, new_minute, second)
