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


from timelinelib.wxgui.components.maincanvas.periodbase import SelectPeriodByDragInputHandler
from timelinelib.wxgui.dialogs.editevent.view import open_create_event_editor


class CreatePeriodEventByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, state, view, config, initial_time):
        SelectPeriodByDragInputHandler.__init__(self, state, view, initial_time)
        self._config = config

        self._state.display_status(_("Select region for event"))

    def end_action(self):
        self._state.display_status("")
        start, end = self.get_last_valid_period().start_and_end_time
        open_create_event_editor(
            self._state,
            self.timeline_canvas,
            self._config,
            self.timeline_canvas.GetDb(),
            start,
            end)
