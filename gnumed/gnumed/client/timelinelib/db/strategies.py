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


from timelinelib.db.interface import ContainerStrategy
from timelinelib.canvas.data.subevent import Subevent


class DefaultContainerStrategy(ContainerStrategy):

    def __init__(self, container):
        ContainerStrategy.__init__(self, container)

    def register_subevent(self, subevent):
        if not isinstance(subevent, Subevent):
            raise TypeError("Expected Subevent object")
        if self._is_subevent_missing(subevent):
            self._append_subevent(subevent)
            if len(self.container.subevents) != 1:
                self._adjust_time_period(subevent)

    def _append_subevent(self, subevent):
        self.container.subevents.append(subevent)
        self._sort_subevents()

    def _sort_subevents(self):
        without_sort_order = []
        with_sort_order = []
        for subevent in self.container.subevents:
            if subevent.sort_order is None:
                without_sort_order.append(subevent)
            else:
                with_sort_order.append(subevent)
        self.container.subevents = sorted(
            with_sort_order,
            key=lambda subevent: subevent.sort_order
        ) + without_sort_order

    def unregister_subevent(self, subevent):
        if self._is_subevent_missing(subevent):
            return
        self.container.subevents.remove(subevent)

    def update(self, subevent):
        self.unregister_subevent(subevent)
        self.register_subevent(subevent)

    def allow_ends_today_on_subevents(self):
        return False

    def _adjust_time_period(self, new_event):
        """
        If the event to be added to the container overlaps any other
        event in the container or if the new event is outside of the
        container time period the container time period must be adjusted.
        """
        event = self._event_totally_overlapping_new_event(new_event)
        if event is not None:
            self._adjust_when_new_event_is_totally_overlapped(new_event, event)
        else:
            events = self._events_overlapped_by_new_event(new_event)
            if len(events) > 0:
                self._adjust_when_new_event_partially_overlaps_other_events(new_event, events)

    def _adjust_when_new_event_is_totally_overlapped(self, new_event, event):
        # Situation:
        #    event:       +--------------------------------------------+
        #    new_event:                  +-------------+
        #                 |- left_delta -|             |- right_delta -|
        #
        #      or         +----------+
        #      or                                  +-------------------+
        #      or         +--------------------------------------------+
        #      or                      +
        #      or         +
        #      or                                                      +
        left_delta = event.start_to_start(new_event).delta()
        right_delta = new_event.end_to_end(event).delta()
        if left_delta > right_delta:
            self._move_events_left(new_event, event)
        else:
            self._move_events_right(new_event, event)

    def _move_events_left(self, new_event, event):
        delta = new_event.start_to_end(event).delta()
        latest_start_time = event.get_time_period().start_time
        self._move_early_events_left(new_event, latest_start_time, delta)

    def _move_events_right(self, new_event, event):
        delta = event.start_to_end(new_event).delta()
        earliest_start_time = event.get_time_period().start_time
        self._move_late_events_right(new_event, earliest_start_time, delta)

    def _adjust_when_new_event_partially_overlaps_other_events(self, new_event, events):
        # Situation:
        #                                 V = threshold_time
        #                            |-td-|
        #    new_event:              +----------------------+
        #    events:                 +-------------+
        #      or              +-------------+
        #      or                        +-------------+
        #      or                             +-------------+
        #      or                                      +-------------+
        threshold_time = self._calc_threshold_time(new_event)
        event = self._some_event_in_new_event_threshold_time(new_event,
                                                             events,
                                                             threshold_time)
        if event is not None:
            self._adjust_threshold_triggered_events(new_event, event, threshold_time)
        earliest_start = self._earliest_start_time_for_event_that_starts_within_new_event(new_event,
                                                                                          events,
                                                                                          threshold_time)
        if earliest_start is not None:
            self._adjust_events_starting_in_new_event(new_event, earliest_start)

    def _calc_threshold_time(self, new_event):
        td = new_event.time_span() * 0.2
        threshold_time = new_event.get_time_period().start_time + td
        return threshold_time

    def _some_event_in_new_event_threshold_time(self, new_event, events, end):
        start = new_event.get_time_period().start_time
        for event in events:
            if event is new_event:
                continue
            if (event.get_time_period().end_time >= start and event.get_time_period().end_time <= end):
                return event
            if (event.get_time_period().start_time <= start and event.get_time_period().end_time > end):
                return event
        return None

    def _adjust_threshold_triggered_events(self, new_event, event, threshold_time):
        delta = event.get_time_period().end_time - new_event.get_time_period().start_time
        self._move_early_events_left(new_event, threshold_time, delta)

    def _earliest_start_time_for_event_that_starts_within_new_event(self, new_event, events, thr):
        start = new_event.get_time_period().start_time
        end = new_event.get_time_period().end_time
        min_start = None
        for event in events:
            if not event.is_period():
                if event.get_time_period().start_time < thr:
                    continue
            if (event.get_time_period().start_time >= start and event.get_time_period().start_time <= end):
                if min_start is None:
                    min_start = event.get_time_period().start_time
                else:
                    if event.get_time_period().start_time < min_start:
                        min_start = event.get_time_period().start_time
        return min_start

    def _adjust_events_starting_in_new_event(self, new_event, earliest_start):
        delta = new_event.get_time_period().end_time - earliest_start
        self._move_late_events_right(new_event, earliest_start, delta)

    def _event_totally_overlapping_new_event(self, new_event):
        for event in self.container.subevents:
            if event is new_event:
                continue
            if (self._event_totally_overlaps_new_event(new_event, event)):
                return event
        return None

    def _event_totally_overlaps_new_event(self, new_event, event):
        return (event.get_time_period().start_time <= new_event.get_time_period().start_time and
                event.get_time_period().end_time >= new_event.get_time_period().end_time)

    def _events_overlapped_by_new_event(self, new_event):
        overlapping_events = []
        for event in self.container.subevents:
            if event is not new_event:
                if (self._starts_within(event, new_event) or self._ends_within(event, new_event)):
                    overlapping_events.append(event)
        return overlapping_events

    def _starts_within(self, event, new_event):
        s1 = event.get_time_period().start_time >= new_event.get_time_period().start_time
        s2 = event.get_time_period().start_time <= new_event.get_time_period().end_time
        return (s1 and s2)

    def _ends_within(self, event, new_event):
        s1 = event.get_time_period().end_time >= new_event.get_time_period().start_time
        s2 = event.get_time_period().end_time <= new_event.get_time_period().end_time
        return (s1 and s2)

    def _move_early_events_left(self, new_event, latest_start_time, delta):
        delta = -delta
        for event in self.container.subevents:
            if event is new_event:
                continue
            if event.get_time_period().start_time <= latest_start_time:
                event.move_delta(delta)

    def _move_late_events_right(self, new_event, earliest_start_time, delta):
        for event in self.container.subevents:
            if event is new_event:
                continue
            if event.get_time_period().start_time >= earliest_start_time:
                event.move_delta(delta)

    def _is_subevent_missing(self, subevent):
        for x in self.container.subevents:
            if x is subevent:
                return False
        return True


class ExtendedContainerStrategy(DefaultContainerStrategy):

    def register_subevent(self, subevent):
        if not isinstance(subevent, Subevent):
            raise TypeError("Expected Subevent object")
        if self._is_subevent_missing(subevent):
            self._append_subevent(subevent)

    def allow_ends_today_on_subevents(self):
        return True
