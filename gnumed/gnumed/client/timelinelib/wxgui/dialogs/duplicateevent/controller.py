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


from timelinelib.wxgui.framework import Controller


FORWARD = 0
BACKWARD = 1
BOTH = 2


class DuplicateEventDialogController(Controller):

    def on_init(self, event, event_duplicator=None):
        if event_duplicator is None:
            self.event_duplicator = EventDuplicator()
        else:
            self.event_duplicator = event_duplicator
        self.event = event
        self._set_default_values()

    def on_ok(self, evt):
        self._create_duplicates()
        self.view.Close()

    def _set_default_values(self):
        self.view.SetCount(1)
        self.view.SetFrequency(1)
        self.view.SetDirection(FORWARD)
        self.view.SelectMovePeriodFnAtIndex(0)

    def _create_duplicates(self):
        missing_dates_count, periods = self._repeat_period(
            self.event.time_period
        )
        self.event_duplicator.duplicate(self.event, periods)
        if missing_dates_count > 0:
            self.view.HandleDateErrors(missing_dates_count)

    def _repeat_period(self, period):
        missing_dates_count = 0
        periods = []
        for index in self._calculate_indicies():
            new_period = self.view.GetMovePeriodFn()(
                period,
                index * self.view.GetFrequency()
            )
            if new_period is None:
                missing_dates_count += 1
            else:
                periods.append(new_period)
        return (missing_dates_count, periods)

    def _calculate_indicies(self):
        direction = self.view.GetDirection()
        repetitions = self.view.GetCount()
        if direction == FORWARD:
            return range(1, repetitions + 1)
        elif direction == BACKWARD:
            return range(-repetitions, 0)
        elif direction == BOTH:
            indicies = list(range(-repetitions, repetitions + 1))
            indicies.remove(0)
            return indicies
        else:
            raise Exception("Invalid direction.")


class EventDuplicator(object):

    def duplicate(self, event, periods):
        with event.db.transaction("Duplicate event"):
            self._duplicate_events(event, periods)

    def _duplicate_events(self, event, periods):
        for period in periods:
            self._duplicate_event(event, period)

    def _duplicate_event(self, event, period):
        duplicate = event.duplicate()
        duplicate.time_period = period
        duplicate.container = event.container
        duplicate.save()
        if event.is_container():
            delta = period.get_start_time() - event.get_start_time()
            for subevent in event.subevents:
                duplicate_subevent = subevent.duplicate()
                duplicate_subevent.time_period = subevent.time_period.move_delta(delta)
                # It is important to set time period before container, because
                # otherwise the strategy might move events unexpectedly.
                duplicate_subevent.container = duplicate
                duplicate_subevent.save()
