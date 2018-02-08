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
Contains the GraphObject class.
Tests are defined :doc:`Here <unit_canvas_drawing_graphobject>`.
"""

import operator


class GraphObject(object):
    """
    Contains metric and color information and a list of child
    graphical objects.
    When a Graphical object is translated to another position
    all of its children are also translated.
    The purpose is to be able to define a graphical object
    position relative to it's parent.
    """

    def __init__(self, x=0, y=0, w=0, h=0, text=''):
        self._childs = []
        self._rect = (x, y, w, h)
        self._text = text
        self._brush_color = (0, 0, 0)
        self._pen_color = (0, 0, 0)

    def translate(self, x, y):
        """
        Translate this object to a new position and translate
        all of it's child the same amount.
        """
        self._rect = tuple(map(operator.add, self._rect, (x, y, 0, 0)))
        for child in self.childs:
            child.translate(x, y)

    @property
    def childs(self):
        """Getter and Setter property."""
        return self._childs

    @childs.setter
    def childs(self, childs):
        """ """
        self._childs = childs

    @property
    def first_child(self):
        """Getter property."""
        return self._childs[0]

    def add_child(self, child):
        """Add a new child to the list of childs."""
        self._childs.append(child)

    @property
    def text(self):
        """Getter property."""
        return self._text

    @property
    def point(self):
        """Getter property."""
        return self.rect[:2]

    @property
    def rect(self):
        """Getter property."""
        return self._rect

    @property
    def width(self):
        """Getter property."""
        return self._rect[2]

    @property
    def height(self):
        """Getter property."""
        return self._rect[3]

    @property
    def brush_color(self):
        """Getter and Setter property."""
        return self._brush_color

    @brush_color.setter
    def brush_color(self, brush_color):
        self._brush_color = brush_color

    @property
    def pen_color(self):
        """Getter and Setter property."""
        return self._pen_color

    @pen_color.setter
    def pen_color(self, pen_color):
        self._pen_color = pen_color
