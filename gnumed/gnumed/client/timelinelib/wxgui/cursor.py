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


"""
A representation of the cursor and it's position on in the Timeline window.
"""


class Cursor(object):

    def __init__(self, x=0, y=0):
        self._start_pos = (x, y)
        self._current_pos = (x, y)
        self._has_moved = False

    def __repr__(self):
        return 'Cursor from (%d, %d) at %d, %d' % (self._start_pos[0],
                                                   self._start_pos[1],
                                                   self._current_pos[0],
                                                   self._current_pos[1])

    @property
    def x(self):
        return self._current_pos[0]

    @property
    def y(self):
        return self._current_pos[1]

    @property
    def pos(self):
        return self._current_pos

    @property
    def start(self):
        return self._start_pos

    @property
    def rect(self):
        x0, y0 = self._start_pos
        x1, y1 = self._current_pos
        return (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y0 - y1))

    def has_moved(self):
        return self._has_moved

    def reset_move(self):
        self.move(*self._current_pos)

    def move(self, x, y):
        self._has_moved = self._current_pos != (x, y)
        self._current_pos = (x, y)
