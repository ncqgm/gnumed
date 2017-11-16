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


from timelinelib.wxgui.components.maincanvas.periodbase import SelectPeriodByDragInputHandler


class ZoomByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, state, timeline_canvas, main_frame, status_bar, start_time):
        SelectPeriodByDragInputHandler.__init__(self, state, timeline_canvas, main_frame, start_time)
        self.timeline_canvas = timeline_canvas
        self._status_bar = status_bar
        self._status_bar.set_text(_("Select region to zoom into"))

    def end_action(self):
        self._status_bar.set_text("")
        period = self.get_last_valid_period()
        start = period.start_time
        end = period.end_time
        self.timeline_canvas.Navigate(lambda tp: tp.update(start, end))
