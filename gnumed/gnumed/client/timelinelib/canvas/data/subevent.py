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


from timelinelib.canvas.data.event import Event
from timelinelib.canvas.data.immutable import ImmutableEvent
from timelinelib.features.experimental.experimentalfeatures import EXTENDED_CONTAINER_STRATEGY


class Subevent(Event):

    def __init__(self, db=None, id_=None, immutable_value=ImmutableEvent()):
        Event.__init__(self, db=db, id_=id_, immutable_value=immutable_value)
        if not EXTENDED_CONTAINER_STRATEGY.enabled():
            self.locked = False

    def save(self, save_all_subevents=True):
        with self._db.transaction("Save event"):
            if save_all_subevents and self.container is not None:
                for subevent in self.container.subevents:
                    subevent.db = self.container.db
                    subevent.save(save_all_subevents=False)
            else:
                Event.save(self)
        return self

    def __eq__(self, other):
        return (isinstance(other, Subevent) and
                super(Subevent, self).__eq__(other))

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "Subevent<id=%r, text=%r, ...>" % (
            self.get_id(), self.get_text())

    def is_container(self):
        """Overrides parent method."""
        return False

    def is_subevent(self):
        """Overrides parent method."""
        return True

    def get_time_period(self):
        return self._immutable_value.time_period

    def set_time_period(self, time_period):
        self._immutable_value = self._immutable_value.update(time_period=time_period)
        if self.container is not None:
            self.container.update_container(self)
        return self

    time_period = property(get_time_period, set_time_period)
