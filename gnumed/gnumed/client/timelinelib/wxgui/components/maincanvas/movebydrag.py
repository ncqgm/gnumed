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


from timelinelib.wxgui.components.maincanvas.scrollbase import ScrollViewInputHandler


class MoveByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, state, timeline_canvas, event, start_drag_time):
        ScrollViewInputHandler.__init__(self, timeline_canvas)
        self._state = state
        self.start_drag_time = start_drag_time
        self._store_event_periods(event)
        self._transaction = self.timeline_canvas.GetDb().transaction("Move events")

    def _store_event_periods(self, event_being_dragged):
        self.event_periods = []
        selected_events = self.timeline_canvas.GetSelectedEvents()
        if event_being_dragged not in selected_events:
            return
        for event in selected_events:
            period_pair = (event, event.get_time_period())
            if event == event_being_dragged:
                self.event_periods.insert(0, period_pair)
            else:
                self.event_periods.append(period_pair)
            if event.is_container():
                for subevent in event.subevents:
                    period_pair = (subevent, subevent.get_time_period())
                    self.event_periods.append(period_pair)
        assert self.event_periods[0][0] == event_being_dragged

    def mouse_moved(self, cursor, keyboard):
        ScrollViewInputHandler.mouse_moved(self, cursor, keyboard)
        self._move_event()

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self._state.display_status("")
        self._transaction.commit()
        self._state.edit_ends()
        self._state.change_to_no_op()

    def view_scrolled(self):
        self._move_event()

    def _move_event(self):
        if len(self.event_periods) == 0:
            return
        if self._any_event_locked():
            self._state.display_status(_("Can't move locked event"))
            return
        self._move_selected_events()
        self.timeline_canvas.Redraw()

    def _any_event_locked(self):
        for (event, _) in self.event_periods:
            if event.get_locked():
                return True
        return False

    def _move_selected_events(self):
        try:
            total_move_delta = self._get_total_move_delta()
            for (event, original_period) in self.event_periods:
                event.update_period_o(original_period.move_delta(total_move_delta))
                event.save()
        except ValueError as ex:
            self.status_bar.set_text("%s" % ex)

    def _get_total_move_delta(self):
        moved_delta = self._get_moved_delta()
        if self.timeline_canvas.EventIsPeriod(self.event_periods[0][0]):
            new_period = self.event_periods[0][1].move_delta(moved_delta)
            snapped_period = self._snap(new_period)
            return snapped_period.start_time - self.event_periods[0][1].start_time
        else:
            return moved_delta

    def _get_moved_delta(self):
        current_time = self.timeline_canvas.GetTimeAt(self.last_x)
        return current_time - self.start_drag_time

    def _snap(self, period):
        start = period.start_time
        end = period.end_time
        start_snapped = self.timeline_canvas.Snap(start)
        end_snapped = self.timeline_canvas.Snap(end)
        if start_snapped != start:
            return period.move_delta(start_snapped - start)
        elif end_snapped != end:
            return period.move_delta(end_snapped - end)
        else:
            return period
