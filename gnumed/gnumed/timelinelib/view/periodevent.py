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


class CreatePeriodEventByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, controller, view, initial_time):
        SelectPeriodByDragInputHandler.__init__(self, controller, initial_time)
        self.view = view

    def end_action(self):
        period = self.get_last_valid_period()
        self.view.open_create_event_editor(period.start_time, period.end_time)
