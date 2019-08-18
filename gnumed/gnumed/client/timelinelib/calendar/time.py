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


class ComparableValue(object):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.value != other.value
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.value < other.value
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.value <= other.value
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.value > other.value
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.value >= other.value
        else:
            return NotImplemented


class GenericTimeMixin(object):

    def __radd__(self, other):
        return self + other
    
    def to_str(self):
        return repr(self)


class GenericDeltaMixin(object):

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return -1 * self
