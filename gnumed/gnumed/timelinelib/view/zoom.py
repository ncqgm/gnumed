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


from timelinelib.view.periodbase import SelectPeriodByDragInputHandler


class ZoomByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, controller, status_bar_adapter, start_time):
        SelectPeriodByDragInputHandler.__init__(self, controller, start_time)
        self.controller = controller
        self.status_bar_adapter = status_bar_adapter
        self.status_bar_adapter.set_text(_("Select region to zoom into"))

    def mouse_moved(self, x, y, alt_down=False):
        SelectPeriodByDragInputHandler.mouse_moved(self, x, y, alt_down)
        try:
            p = self.get_current_period()
        except ValueError:
            self.status_bar_adapter.set_text(_("Region too long"))
        else:
            if p.delta() < p.time_type.get_min_zoom_delta()[0]:
                self.status_bar_adapter.set_text(_("Region too short"))
            else:
                self.status_bar_adapter.set_text("")

    def end_action(self):
        self.status_bar_adapter.set_text("")
        period = self.get_last_valid_period()
        start = period.start_time
        end = period.end_time
        delta = end - start
        if period.time_type.zoom_is_ok(delta):
            # Don't zoom in to less than an hour which upsets things.
            self.controller.navigate_timeline(lambda tp: tp.update(start, end))
