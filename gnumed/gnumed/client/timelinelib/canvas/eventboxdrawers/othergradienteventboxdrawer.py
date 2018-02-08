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

    def _draw_background(self, dc, rect, event):
        dc.SetPen(self._get_pen(dc, event))
        dc.DrawRectangleRect(rect)
        inner_rect = wx.Rect(*rect)
        inner_rect.Deflate(1, 1)
        dc.GradientFillLinear(inner_rect, self._get_light_color(event), self._get_dark_color(event), wx.WEST)

    def _get_light_color(self, event):
        return lighten_color(self._get_event_color(event))

    def _get_dark_color(self, event):
        return darken_color(self._get_event_color(event), factor=0.8)
