# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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


"""
A representation of the keyboard and it's control key states.
"""


class Keyboard(object):

    CTRL = 4
    SHIFT = 2
    ALT = 1
    NONE = 0

    def __init__(self, ctrl=False, shift=False, alt=False):
        self._ctrl = ctrl
        self._shift = shift
        self._alt = alt

    @property
    def ctrl(self):
        return self._ctrl

    @property
    def shift(self):
        return self._shift

    @property
    def alt(self):
        return self._alt

    @property
    def keys_combination(self):
        """
        This function returns a unique integer value for each combination
        of control keys. It may seem a little odd to use the if statements
        but that has been proven to be the most efficient way of converting
        a boolean to an int.
        """
        return ((Keyboard.CTRL if self._ctrl else 0) +
                (Keyboard.SHIFT if self._shift else 0) +
                (Keyboard.ALT if self._alt else 0))
