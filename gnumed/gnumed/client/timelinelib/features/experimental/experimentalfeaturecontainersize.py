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
from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature
from timelinelib.wxgui.components.font import Font


CONFIG_NAME = "Extend Container height"
DISPLAY_NAME = _("Extend Container height")
DESCRIPTION = _("""
              Extend the height of a container so that the container name becomes visible.

              This also has the side effect that ordinary events come farther apart in
              the vertical direction.

              The font for the container name has a fixed size when you zoom vertically (Alt + Mouse wheel)
              """)
Y_OFFSET = -16
PADDING = 12
OUTER_PAADING = 4
TEXT_OFFSET = -2
INNER_PADDING = 3
FONT_SIZE = 8


class ExperimentalFeatureContainerSize(ExperimentalFeature):

    def __init__(self):
        ExperimentalFeature.__init__(self, DISPLAY_NAME, DESCRIPTION, CONFIG_NAME)

    def get_extra_outer_padding_to_avoid_vertical_overlapping(self):
        return OUTER_PAADING

    def get_vertical_larger_box_rect(self, rect):
        return wx.Rect(rect.X - 2, rect.Y - 2 - PADDING, rect.Width + 4, rect.Height + 4 + PADDING)

    def draw_container_text_top_adjusted(self, text, dc, rect):
        old_font = dc.GetFont()
        dc.SetFont(Font(FONT_SIZE))
        dc.SetClippingRect(wx.Rect(rect.X, rect.Y + Y_OFFSET, rect.Width, rect.Height))
        text_x = rect.X + INNER_PADDING
        text_y = rect.Y + INNER_PADDING + TEXT_OFFSET
        dc.DrawText(text, text_x, text_y)
        dc.SetFont(old_font)
