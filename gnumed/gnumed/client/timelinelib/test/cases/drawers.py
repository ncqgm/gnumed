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


import unittest

from timelinelib.test.cases.wxapp import WxAppTestCase


TEXT_HEIGHT = 20
TEXT_WIDTH = 40


class describe_drawers(WxAppTestCase):

    def create_scene(self, width, height, divider_y):
        return Scene(width, height, divider_y)

    def create_dc(self):
        return Dc()

    def install_gettext(self):
        import gettext
        from timelinelib.config.paths import LOCALE_DIR
        from timelinelib.meta.about import APPLICATION_NAME
        gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)


class Dc:

    def __init__(self):
        self._set_pen_call_count = 0
        self._set_draw_line_call_count = 0
        self._set_draw_text_call_count = 0
        self._font = None
        self._text_foreground = None
        self._text = None
        self._text_x = None
        self._text_y = None

    @property
    def pen_call_count(self):
        return self._set_pen_call_count

    @property
    def draw_line_call_count(self):
        return self._set_draw_line_call_count

    @property
    def draw_text_call_count(self):
        return self._set_draw_text_call_count

    @property
    def x1(self):
        return self._x1

    @property
    def y1(self):
        return self._y1

    @property
    def x2(self):
        return self._x2

    @property
    def y2(self):
        return self._y2

    @property
    def font(self):
        return self._font

    @property
    def text_foreground(self):
        return self._text_foreground

    @property
    def text(self):
        return self._text

    @property
    def text_x(self):
        return self._text_x

    @property
    def text_y(self):
        return self._text_y

    def SetPen(self, pen):
        self._set_pen_call_count += 1

    def SetTextForeground(self, color):
        self._text_foreground = color

    def DrawLine(self, x1, y1, x2, y2):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._set_draw_line_call_count += 1

    def DrawText(self, text, x, y):
        self._text = text
        self._text_x = x
        self._text_y = y
        self._set_draw_text_call_count += 1

    def GetTextExtent(self, text):
        return TEXT_WIDTH, TEXT_HEIGHT

    def SetFont(self, font):
        self._font = font


class Scene:

    def __init__(self, width, height, divider_y):
        self._width = width
        self._height = height
        self._divider_y = divider_y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def divider_y(self):
        return self._divider_y

    def x_pos_for_time(self, time):
        return 100

    def minor_strip_is_day(self):
        return True


def install_gettext():
    import gettext
    from timelinelib.config.paths import LOCALE_DIR
    from timelinelib.meta.about import APPLICATION_NAME
    gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)
