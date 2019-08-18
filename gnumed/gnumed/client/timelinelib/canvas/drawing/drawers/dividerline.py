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

class DividerLine:

    def __init__(self, drawer):
        self._scene = drawer.scene
        self._dc = drawer.dc        
        self._appearance = drawer.appearance
        
    def draw(self):
        {0: self.draw_at_top, 
         1: self.draw_at_divider, 
         2: self.draw_at_bottom}[self._appearance.get_time_scale_pos()]()
                     
    def draw_at_divider(self):
        self._draw(self._scene.divider_y)
    
    def draw_at_top(self):
        (_, text_height) = self._dc.GetTextExtent('M')
        self._draw(2 * text_height + 2)
    
    def draw_at_bottom(self):
        (_, text_height) = self._dc.GetTextExtent('M')
        self._draw(self._scene.height - text_height)

    def _draw(self, y):
        self._dc.SetPen(resource.get_pen('black-solid'))
        self._dc.DrawLine(0, y, self._scene.width, y)        
