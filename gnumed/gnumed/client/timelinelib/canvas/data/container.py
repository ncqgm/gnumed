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


from timelinelib.canvas.data.base import create_noop_property
from timelinelib.canvas.data.event import Event
from timelinelib.canvas.data.event import DEFAULT_COLOR
from timelinelib.canvas.data.immutable import ImmutableContainer
from timelinelib.canvas.data.timeperiod import TimePeriod
from timelinelib.features.experimental.experimentalfeatures import EXTENDED_CONTAINER_STRATEGY


class Container(Event):

    def __init__(self, db=None, id_=None, immutable_value=ImmutableContainer()):
        Event.__init__(self, db=db, id_=id_, immutable_value=immutable_value)
        self._subevents = []
        self._is_in_update = False
        import timelinelib.db.strategies
        if EXTENDED_CONTAINER_STRATEGY.enabled():
            self.strategy = timelinelib.db.strategies.ExtendedContainerStrategy(self)
        else:
            self.strategy = timelinelib.db.strategies.DefaultContainerStrategy(self)

    @property
    def subevents(self):
        return self._subevents

    @subevents.setter
    def subevents(self, value):
        self._subevents = value

    def save(self):
        self._update_category_id()
        with self._db.transaction("Save container") as t:
            t.save_container(self._immutable_value, self.ensure_id())
        return self

    def delete(self):
        with self._db.transaction("Delete container") as t:
            t.delete_container(self.id)
        self.id = None

    def get_time_period(self):
        if len(self.subevents) == 0:
            return self._immutable_value.time_period
        else:
            return TimePeriod(
                min([event.get_start_time() for event in self.subevents]),
                max([event.get_end_time() for event in self.subevents])
            )

    def set_time_period(self, value):
        self._immutable_value = self._immutable_value.update(time_period=value)
        return self

    time_period = property(get_time_period, set_time_period)

    def get_sort_order(self):
        if len(self.subevents) == 0:
            return 0
        else:
            return min(
                self.subevents,
                key=lambda event: event.sort_order
            ).sort_order

    def set_sort_order(self, sort_order):
        # Don't save it
        return self

    sort_order = property(get_sort_order, set_sort_order)

    def __eq__(self, other):
        return (isinstance(other, Container) and
                super(Container, self).__eq__(other))

    def is_container(self):
        return True

    def is_subevent(self):
        return False

    def register_subevent(self, subevent):
        self.strategy.register_subevent(subevent)

    def unregister_subevent(self, subevent):
        self.strategy.unregister_subevent(subevent)

    def update_container(self, subevent):
        if self._is_in_update:
            return
        try:
            self._is_in_update = True
            self.strategy.update(subevent)
        finally:
            self._is_in_update = False

    def update_properties(self, text, category=None):
        self.set_text(text)
        self.set_category(category)

    def allow_ends_today_on_subevents(self):
        return self.strategy.allow_ends_today_on_subevents()


create_noop_property(Container, "fuzzy", False)
create_noop_property(Container, "locked", False)
create_noop_property(Container, "ends_today", False)
create_noop_property(Container, "description", None)
create_noop_property(Container, "icon", None)
create_noop_property(Container, "hyperlink", None)
create_noop_property(Container, "alert", None)
create_noop_property(Container, "progress", None)
create_noop_property(Container, "default_color", DEFAULT_COLOR)
