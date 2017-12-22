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


class InputHandler(object):

    def __init__(self, timeline_canvas):
        self.timeline_canvas = timeline_canvas
        self._canvas = timeline_canvas

    def left_mouse_down(self, cursor, keyboard):
        pass

    def mouse_moved(self, cursor, keyboard):
        pass

    def left_mouse_up(self):
        pass

    def dragscroll_timer_fired(self):
        pass
