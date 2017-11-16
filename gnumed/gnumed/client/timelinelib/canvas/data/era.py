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


from timelinelib.canvas.data.base import ItemBase
from timelinelib.canvas.data.immutable import ImmutableEra
from timelinelib.canvas.data.item import TimelineItem


DEFAULT_ERA_COLOR = (200, 200, 200)


class Era(ItemBase, TimelineItem):
    """
    A clearly defined period of time of arbitrary but well-defined length.
    An Era is indicated in a timeline, by setting the background color
    to the Era color for the Era time period. The Era name is also
    drawn on the timeline within the Era time period.
    """

    def __init__(self, db=None, id_=None, immutable_value=ImmutableEra()):
        ItemBase.__init__(self, db, id_, immutable_value)

    def save(self):
        with self._db.transaction("Save era") as t:
            t.save_era(self._immutable_value, self.ensure_id())
        return self

    def delete(self):
        with self._db.transaction("Delete era") as t:
            t.delete_era(self.id)
        self.id = None

    def __eq__(self, other):
        return (isinstance(other, Era) and
                self.get_id() == other.get_id() and
                self.get_time_period() == other.get_time_period() and
                self.get_name() == other.get_name() and
                self.get_color() == other.get_color())

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return self.get_start_time() > other.get_start_time()

    def __lt__(self, other):
        return self.get_start_time() < other.get_start_time()

    def ends_today(self):
        return self._immutable_value.ends_today

    def set_ends_today(self, value):
        self._immutable_value = self._immutable_value.update(ends_today=value)

    _ends_today = property(ends_today, set_ends_today)

    def update(self, start_time, end_time, name, color=DEFAULT_ERA_COLOR):
        """ """
        self.update_period(start_time, end_time)
        self.name = name.strip()
        self.color = color
        return self

    def set_name(self, name):
        self._immutable_value = self._immutable_value.update(name=name.strip())
        return self

    def get_name(self):
        return self._immutable_value.name

    name = property(get_name, set_name)

    def set_color(self, color):
        self._immutable_value = self._immutable_value.update(color=color)
        return self

    def get_color(self):
        return self._immutable_value.color

    color = property(get_color, set_color)

    def overlapping(self, era):
        """ """
        if era.get_start_time() >= self.get_end_time():
            return 0
        if era.get_start_time() == self.get_start_time():
            if era.get_end_time() == self.get_end_time():
                return 4
            if era.get_end_time() > self.get_end_time():
                return 2
            else:
                return 3
        if era.get_end_time() == self.get_end_time():
            return 5
        if era.get_end_time() > self.get_end_time():
            return 1
        return 6
