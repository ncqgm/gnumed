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


class NowLine:
    
    def __init__(self, drawer):
        self._drawer = drawer
        self._scene = drawer.scene
        self._dc = drawer.dc        
        self._appearance = drawer.appearance
    
    def draw(self):
        x = self._calculate_x_pos()
        if self._now_line_is_visible(x):
            self._draw_line(x)
            
    def _calculate_x_pos(self):
        now_time = self._drawer.time_type.now()
        return self._scene.x_pos_for_time(now_time)
        
    def _now_line_is_visible(self, x):
        return x > 0 and x < self._scene.width

    def _draw_line(self, x):
        self._dc.SetPen(self._drawer.now_pen)
        self._dc.DrawLine(x, 0, x, self._scene.height)
        if self._appearance.get_use_bold_nowline():
            self._dc.DrawLine(x + 1, 0, x + 1, self._scene.height)
            self._dc.DrawLine(x - 1, 0, x - 1, self._scene.height)    
