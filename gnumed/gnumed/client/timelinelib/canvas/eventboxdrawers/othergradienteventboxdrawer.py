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


import wx

from timelinelib.canvas.drawing.utils import darken_color
from timelinelib.canvas.drawing.utils import lighten_color
from timelinelib.canvas.eventboxdrawers.defaulteventboxdrawer import DefaultEventBoxDrawer


class OtherGradientEventBoxDrawer(DefaultEventBoxDrawer):

    def __init__(self, fuzzy_edges=False):
        self._fuzzy_edges = fuzzy_edges

    def _draw_background(self, dc, rect, event):
        dc.SetPen(self._get_pen(dc, event))
        if self._fuzzy_edges and event.get_fuzzy():
            self._draw_background_and_fuzzy_edges(dc, rect, event)
        else:
            self._draw_background_no_fuzzy_edges(dc, rect, event)

    def _draw_background_no_fuzzy_edges(self, dc, rect, event):
        dc.DrawRectangle(rect)
        inner_rect = wx.Rect(*rect)
        inner_rect.Deflate(1, 1)
        dc.GradientFillLinear(inner_rect, self._get_light_color(event), self._get_dark_color(event), wx.WEST)

    def _draw_background_and_fuzzy_edges(self, dc, rect, event):
        self._draw_fuzzy_rect_outer_lines(dc, rect)
        self._draw_fuzzy_rect_fill_first_half(dc, rect, event)
        self._draw_fuzzy_rect_fill_second_half(dc, rect, event)

    def _draw_fuzzy_rect_outer_lines(self, dc, rect):
        dc.DrawLine(rect.GetX(), rect.GetY(), rect.GetX() + rect.GetWidth(), rect.GetY())
        dc.DrawLine(rect.GetX(), rect.GetY() + rect.GetHeight() - 1,
                    rect.GetX() + rect.GetWidth(), rect.GetY() + rect.GetHeight() - 1)

    def _draw_fuzzy_rect_fill_first_half(self, dc, rect, event):
        inner_rect = self._get_half_rect(rect)
        dc.GradientFillLinear(inner_rect, wx.WHITE, self._get_dark_color(event), wx.EAST)

    def _draw_fuzzy_rect_fill_second_half(self, dc, rect, event):
        inner_rect = self._get_half_rect(rect)
        inner_rect.SetPosition(wx.Point(inner_rect.GetX() + inner_rect.GetWidth(), inner_rect.GetY()))
        dc.GradientFillLinear(inner_rect, wx.WHITE, self._get_dark_color(event), wx.WEST)

    def _get_half_rect(self, rect):
        inner_rect = wx.Rect(*rect)
        inner_rect.Deflate(1, 1)
        inner_rect.SetWidth(inner_rect.GetWidth() / 2)
        return inner_rect

    def _draw_fuzzy_edges(self, dc, rect, event):
        """Overrides base class function."""
        if not self._fuzzy_edges:
            super(OtherGradientEventBoxDrawer, self)._draw_fuzzy_edges(dc, rect, event)

    def _get_light_color(self, event):
        return lighten_color(self._get_event_color(event))

    def _get_dark_color(self, event):
        return darken_color(self._get_event_color(event), factor=0.8)
