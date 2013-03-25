# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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


from timelinelib.view.inputhandler import InputHandler


# dragscroll timer interval in milliseconds
DRAGSCROLL_TIMER_MSINTERVAL = 300
# timeline. The scroll zone areas are found at the beginning and at the
# end of the timeline.
SCROLL_ZONE_WIDTH = 20


class ScrollViewInputHandler(InputHandler):

    def __init__(self, controller):
        self.controller = controller
        self.view = controller.view
        self.timer_running = False

    def mouse_moved(self, x, y, alt_down=False):
        self.last_x = x
        if self.controller._in_scroll_zone(x) and not self.timer_running:
            self.view.start_dragscroll_timer(milliseconds=DRAGSCROLL_TIMER_MSINTERVAL)
            self.timer_running = True

    def left_mouse_up(self):
        self.view.stop_dragscroll_timer()

    def dragscroll_timer_fired(self):
        if self.controller._in_scroll_zone(self.last_x):
            if self.last_x < SCROLL_ZONE_WIDTH:
                direction = 1
            else:
                direction = -1
            self.controller._scroll_timeline_view(direction)
            self.view_scrolled()

    def view_scrolled(self):
        raise Exception("view_scrolled not implemented in subclass.")
