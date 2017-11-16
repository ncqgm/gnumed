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
Contains the LegendDrawer class.
Tests are defined :doc:`Here <unit_canvas_drawing_drawers_legenddrawer>`.
"""

import wx
import timelinelib.wxgui.components.font as font
from timelinelib.canvas.drawing.graphobject import GraphObject
from timelinelib.canvas.drawing.utils import darken_color


# INNER_PADDING = 3  # Space inside event box to text (pixels)
# OUTER_PADDING = 5  # Space between event boxes (pixels)
IP = 3
OP = 5

BOTTOM_LEFT = 0
"""Default value."""
TOP_LEFT = 1
"""."""
TOP_RIGHT = 2
"""."""
BOTTOM_RIGHT = 3
"""."""


class LegendDrawer():
    """
    The legend is a box containing one item row for each category
    displayed in a timeline. An item contains a text and colored
    box. The text is the category text and the color is the color
    of the category. The legend box can be placed at different
    locations on the Teimeline panel. When measures are calculated
    it's assumed that it will be placed in the upper left corner::
                                      OP
           IP                        |  | 
          |  |              >|   |< text_height
          +--------------------------+---
          |                          |    IP
          |                  +---+   |---
          |   Xxxxxxx yyyy   |   |   |
          |                  +---+   |---
          |                          |    IP
          |                  +---+   |---
          |   Xxxxxxx yyyy   |   |   |    text_height
          |                  +---+   |---
          |   |          |     :     |
          |    text_width      :     |
          |                    :     |
          +--------------------------+
                          |  |    |  |
                           OP      IP
    """

    def __init__(self, dc, scene, categories):
        self._dc = dc
        self._scene = scene
        self._categories = categories

    def draw(self):
        """Draw the legend on the Timeline panel."""
        go = self._create_graph_object()
        self._draw_rectangle(go)
        self._draw_legend_items(go)

    def _draw_legend_items(self, go):
        for item in go.childs:
            self._draw_legend_item(item)

    def _draw_legend_item(self, go):
        self._dc.DrawText(go.text, *go.point)
        self._draw_Legend_item_color_box(go.first_child)

    def _draw_Legend_item_color_box(self, go):
        self._draw_rectangle(go)

    def _draw_rectangle(self, go):
        self._dc.SetBrush(go.brush_color)
        self._dc.SetPen(go.pen_color)
        self._dc.DrawRectangleRect(wx.Rect(*go.rect))

    def _create_graph_object(self):
        tw, th = self._get_text_metrics(self._categories)
        box_width = tw + th + OP + 2 * IP
        box_height = len(self._categories) * (IP + th) + IP
        return self._create_legend(box_width, box_height, tw, th)

    def _get_text_metrics(self, categories):
        """
        Return the text width of the longest category text and the
        height of the first category text.
        """
        font.set_legend_text_font(self._scene._appearance.get_legend_font(), self._dc)
        twth = [self._dc.GetTextExtent(cat.name) for cat in categories]
        maxw = max(twth, key=lambda x: x[0])[0]
        return maxw, twth[0][1]

    def _create_legend(self, box_width, box_height, tw, th):
        go = GraphObject(w=box_width, h=box_height)
        go.brush_color = wx.Brush(wx.Colour(255, 255, 255), wx.PENSTYLE_SOLID)
        go.pen_color = wx.Pen(wx.Colour(0, 0, 0), 1, wx.PENSTYLE_SOLID)
        go.childs = self._legend_items(tw, th)
        go.translate(OP, OP)
        self._set_legend_pos(go)
        return go

    def _legend_items(self, tw, th):
        collector = []
        for i in xrange(len(self._categories)):
            y = i * (th + IP)
            go = GraphObject(y=y, text=self._categories[i].name)
            go.add_child(self._color_box(tw, th, y, self._categories[i]))
            go.translate(IP, IP)
            collector.append(go)
        return collector

    def _color_box(self, tw, th, y, category):
        go = GraphObject(x=tw + OP, y=y, w=th, h=th)
        go.brush_color = wx.Brush(wx.Colour(*category.color))
        go.pen_color = wx.Pen(wx.Colour(*darken_color(category.color)))
        return go

    def _set_legend_pos(self, go):
        x = self._scene.width - 2 * OP - go.width
        y = self._scene.height - 2 * OP - go.height
        poses = {TOP_LEFT: (0, 0),
                 TOP_RIGHT: (x, 0),
                 BOTTOM_LEFT: (0, y),
                 BOTTOM_RIGHT: (x, y)}
        go.translate(*poses[self._scene._view_properties.legend_pos])
