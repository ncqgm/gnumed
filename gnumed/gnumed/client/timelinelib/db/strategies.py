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


from timelinelib.db.interface import ContainerStrategy


class DefaultContainerStrategy(ContainerStrategy):

    def __init__(self, container):
        ContainerStrategy.__init__(self, container)

    def register_subevent(self, subevent):
        if subevent not in self.container.events:
            self.container.events.append(subevent)
            subevent.register_container(self.container)
            if len(self.container.events) == 1:
                self._set_time_period()
            else:
                self._adjust_time_period(subevent)

    def unregister_subevent(self, subevent):
        if subevent not in self.container.events:
            return
        self.container.events.remove(subevent)
        self._set_time_period()

    def update(self, subevent):
        self.unregister_subevent(subevent)
        self.register_subevent(subevent)
        self._set_time_period()

    def _set_time_period(self):
        """
        The container time period starts where the subevent with the earliest
        start time, starts, and it ends where the subevent whith the latest end
        time ends.
           Subevents   +------+  +--------+    +--+
           Container   +--------------------------+
        """
        if len(self.container.events) == 0:
            return
        self._set_start_time(self.container.events[0])
        self._set_end_time(self.container.events[0])
        for event in self.container.events:
            if self._container_starts_after_event(event):
                self._set_start_time(event)
            if self._container_ends_before_event(event):
                self._set_end_time(event)

    def _container_starts_after_event(self, subevent):
        return (self.container.time_period.start_time >
                subevent.time_period.start_time)

    def _container_ends_before_event(self, event):
        return (self.container.time_period.end_time <
                event.time_period.end_time)

    def _set_start_time(self, event):
        self.container.time_period.start_time = event.time_period.start_time

    def _set_end_time(self, event):
        self.container.time_period.end_time = event.time_period.end_time

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
        self._set_time_period()

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
        left_delta = new_event.time_period.start_time - event.time_period.start_time
        right_delta = event.time_period.end_time - new_event.time_period.end_time
        move_left = left_delta > right_delta
        if move_left:
            self._move_events_left(new_event, event)
        else:
            self._move_events_right(new_event, event)

    def _move_events_left(self, new_event, event):
        delta = event.time_period.end_time - new_event.time_period.start_time
        latest_start_time = event.time_period.start_time
        self._move_early_events_left(new_event, latest_start_time, delta)

    def _move_events_right(self, new_event, event):
        delta = new_event.time_period.end_time - event.time_period.start_time
        earliest_start_time = event.time_period.start_time
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
        td = new_event.time_span()
        td = new_event.time_type.mult_timedelta(td, 0.2)
        threshold_time = new_event.time_period.start_time + td
        return threshold_time

    def _some_event_in_new_event_threshold_time(self, new_event, events, end):
        start = new_event.time_period.start_time
        for event in events:
            if event == new_event:
                continue
            if event.time_period.end_time >= start and event.time_period.end_time <= end:
                return event
            if event.time_period.start_time <= start and event.time_period.end_time > end:
                return event
        return None

    def _adjust_threshold_triggered_events(self, new_event, event, threshold_time):
        delta = event.time_period.end_time - new_event.time_period.start_time
        self._move_early_events_left(new_event, threshold_time, delta)

    def _earliest_start_time_for_event_that_starts_within_new_event(self, new_event, events, thr):
        start = new_event.time_period.start_time
        end = new_event.time_period.end_time
        min_start = None
        for event in events:
            if not event.is_period():
                if event.time_period.start_time < thr:
                    continue
            if event.time_period.start_time >= start and event.time_period.start_time <= end:
                if min_start == None:
                    min_start = event.time_period.start_time
                else:
                    if event.time_period.start_time < min_start:
                        min_start = event.time_period.start_time
        return min_start

    def _adjust_events_starting_in_new_event(self, new_event, earliest_start):
        delta = new_event.time_period.end_time - earliest_start
        self._move_late_events_right(new_event, earliest_start, delta)

    def _event_totally_overlapping_new_event(self, new_event):
        for event in self.container.events:
            if event == new_event:
                continue
            if (self._event_totally_overlaps_new_event(new_event, event)):
                return event
        return None

    def _event_totally_overlaps_new_event(self, new_event, event):
        return (event.time_period.start_time <= new_event.time_period.start_time and
                event.time_period.end_time >= new_event.time_period.end_time)

    def _events_overlapped_by_new_event(self, new_event):
        overlapping_events = []
        for event in self.container.events:
            if event != new_event:
                if (self._starts_within(event, new_event) or
                    self._ends_within(event, new_event)):
                    overlapping_events.append(event)
        return overlapping_events

    def _starts_within(self, event, new_event):
        s1 = event.time_period.start_time >= new_event.time_period.start_time
        s2 = event.time_period.start_time <= new_event.time_period.end_time
        return (s1 and s2)

    def _ends_within(self, event, new_event):
        s1 = event.time_period.end_time >= new_event.time_period.start_time
        s2 = event.time_period.end_time <= new_event.time_period.end_time
        return (s1 and s2)

    def _move_early_events_left(self, new_event, latest_start_time, delta):
        delta = -delta
        for event in self.container.events:
            if event == new_event:
                continue
            if event.time_period.start_time <= latest_start_time:
                self._adjust_event_time_period(event, delta)

    def _move_late_events_right(self, new_event, earliest_start_time, delta):
        for event in self.container.events:
            if event == new_event:
                continue
            if event.time_period.start_time >= earliest_start_time:
                self._adjust_event_time_period(event, delta)

    def _adjust_event_time_period(self, event, delta):
        new_start = event.time_period.start_time + delta
        new_end = event.time_period.end_time + delta
        event.time_period.start_time = new_start
        event.time_period.end_time = new_end
