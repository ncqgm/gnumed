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


from timelinelib.db.exceptions import TimelineIOError


FORWARD = 0
BACKWARD = 1
BOTH = 2


class DuplicateEventEditor(object):

    def __init__(self, view, db, event):
        self.view = view
        self.db = db
        self.event = event

    def initialize(self):
        self.view.set_count(1)
        self.view.set_frequency(1)
        self.view.select_move_period_fn_at_index(0)
        self.view.set_direction(FORWARD)

    def create_duplicates_and_save(self):
        (periods, nbr_of_missing_dates) = self._repeat_period(
            self.event.time_period,
            self.view.get_move_period_fn(),
            self.view.get_frequency(),
            self.view.get_count(),
            self.view.get_direction())
        try:
            for period in periods:
                event = self.event.clone()
                event.update_period(period.start_time, period.end_time)
                self.db.save_event(event)
            if nbr_of_missing_dates > 0:
                self.view.handle_date_errors(nbr_of_missing_dates)
            self.view.close()
        except TimelineIOError, e:
            self.view.handle_db_error(e)

    def _repeat_period(self, period, move_period_fn, frequency,
                       repetitions, direction):
        periods = []
        nbr_of_missing_dates = 0
        for index in self._calc_indicies(direction, repetitions):
            new_period = move_period_fn(period, index*frequency)
            if new_period == None:
                nbr_of_missing_dates += 1
            else:
                periods.append(new_period)
        return (periods, nbr_of_missing_dates)

    def _calc_indicies(self, direction, repetitions):
        if direction == FORWARD:
            return range(1, repetitions + 1)
        elif direction == BACKWARD:
            return range(-repetitions, 0)
        elif direction == BOTH:
            indicies = range(-repetitions, repetitions + 1)
            indicies.remove(0)
            return indicies
        else:
            raise Exception("Invalid direction.")
