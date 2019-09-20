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


import timelinelib.canvas.drawing.drawers.resources as resource
import timelinelib.wxgui.components.font as font


class MinorStripDrawer:
    
    def __init__(self, drawer):
        self._scene = drawer.scene
        self._dc = drawer.dc
        self._time_type = drawer.time_type
        self._appearance = drawer.appearance
        drawer.dc.SetPen(resource.get_pen('gray-dashed'))
    
    def draw(self, label, start_time, end_time):
        self._draw_minor_strip_divider_line_at(end_time)
        self._draw_minor_strip_label(label, start_time, end_time)
        
    def _draw_minor_strip_divider_line_at(self, end_time):
        x = self._scene.x_pos_for_time(end_time)
        self._dc.DrawLine(x, 0, x, self._scene.height)

    def _draw_minor_strip_label(self, label, start_time, end_time):
        self._set_minor_strip_font(start_time)
        x = self._calc_label_x_start_pos(label, start_time, end_time)
        height = self._get_label_height(label)
        {0: self._draw_at_top, 
         1: self._draw_at_divider, 
         2: self._draw_at_bottom}[self._appearance.get_time_scale_pos()](label, x, height)
        
    def _draw_at_divider(self, label, x, height):
        self._dc.DrawText(label, x, self._scene.divider_y - height)

    def _draw_at_top(self, label, x, height):
        self._dc.DrawText(label, x, height + 1)

    def _draw_at_bottom(self, label, x, height):
        self._dc.DrawText(label, x, self._scene.height - 2 * height)
        
    def _calc_label_x_start_pos(self, label, start_time, end_time):
        width = self._get_label_width(label)
        start_x = self._scene.x_pos_for_time(start_time)
        end_x = self._scene.x_pos_for_time(end_time)
        return (start_x + end_x - width) // 2

    def _get_label_width(self, label):
        return self._dc.GetTextExtent(label)[0]
        
    def _get_label_height(self, label):
        return self._dc.GetTextExtent(label)[1]

    def _set_minor_strip_font(self, start_time):
        if self._scene.minor_strip_is_day():
            bold = self._time_type.is_weekend_day(start_time)
            italic = self._time_type.is_special_day(start_time)
            font.set_minor_strip_text_font(self._appearance.get_minor_strip_font(), 
                                           self._dc,
                                           force_bold=bold, 
                                           force_normal=not bold, 
                                           force_italic=italic, 
                                           force_upright=not italic)
        else:
            font.set_minor_strip_text_font(self._appearance.get_minor_strip_font(), self._dc)
        
