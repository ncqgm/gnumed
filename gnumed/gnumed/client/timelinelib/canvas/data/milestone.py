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
from timelinelib.canvas.data.immutable import ImmutableMilestone


"""
 A milestone is a special case of a point event. It is normally rendered directly
 on the time scale. It is used to mark a milestone in a timeline.
"""


class Milestone(Event):

    def __init__(self, db=None, id_=None, immutable_value=ImmutableMilestone()):
        Event.__init__(self, db=db, id_=id_, immutable_value=immutable_value)

    def save(self):
        self._update_category_id()
        self._update_sort_order()
        with self._db.transaction("Save milestone") as t:
            t.save_milestone(self._immutable_value, self.ensure_id())
        return self

    def delete(self):
        with self._db.transaction("Delete milestone") as t:
            t.delete_milestone(self.id)
        self.id = None

    def get_time(self):
        return self.get_time_period().start_time

    def is_milestone(self):
        return True


create_noop_property(Milestone, "fuzzy", False)
create_noop_property(Milestone, "locked", False)
create_noop_property(Milestone, "ends_today", False)
create_noop_property(Milestone, "progress", None)
create_noop_property(Milestone, "alert", None)
create_noop_property(Milestone, "hyperlink", None)
create_noop_property(Milestone, "icon", None)
