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


from timelinelib.db.objects.timeperiod import TimePeriod


class Event(object):

    def __init__(self, time_type, start_time, end_time, text, category=None,
                 fuzzy=False, locked=False, ends_today=False):
        self.time_type = time_type
        self.fuzzy = fuzzy
        self.locked = locked
        self.ends_today = ends_today
        self.id = None
        self.selected = False
        self.draw_ballon = False
        self.update(start_time, end_time, text, category)
        self.data = {}

    def has_id(self):
        return self.id is not None

    def set_id(self, id):
        self.id = id

    def update(self, start_time, end_time, text, category=None, fuzzy=None,
               locked=None, ends_today=None):
        """Change the event data."""
        self.time_period = TimePeriod(self.time_type, start_time, end_time)
        self.text = text
        self.category = category
        if ends_today is not None:
            if not self.locked:
                self.ends_today = ends_today
        if fuzzy is not None:
            self.fuzzy = fuzzy
        if locked is not None:
            self.locked = locked

    def update_period(self, start_time, end_time):
        """Change the event period."""
        self.time_period = TimePeriod(self.time_type, start_time, end_time)

    def update_period_o(self, new_period):
        self.update_period(new_period.start_time, new_period.end_time)

    def update_start(self, start_time):
        """Change the event data."""
        if start_time <= self.time_period.end_time:
            self.time_period = TimePeriod(
                self.time_type, start_time, self.time_period.end_time)
            return True
        return False

    def update_end(self, end_time):
        """Change the event data."""
        if end_time >= self.time_period.start_time:
            self.time_period = TimePeriod(
                self.time_type, self.time_period.start_time, end_time)
            return True
        return False

    def inside_period(self, time_period):
        """Wrapper for time period method."""
        return self.time_period.overlap(time_period)

    def is_period(self):
        """Wrapper for time period method."""
        return self.time_period.is_period()

    def mean_time(self):
        """Wrapper for time period method."""
        return self.time_period.mean_time()

    def get_data(self, id):
        """
        Return data with the given id or None if no data with that id exists.

        See set_data for information how ids map to data.
        """
        return self.data.get(id, None)

    def set_data(self, id, data):
        """
        Set data with the given id.

        Here is how ids map to data:

            description - string
            icon - wx.Bitmap
        """
        self.data[id] = data

    def has_data(self):
        """Return True if the event has associated data, or False if not."""
        for id in self.data:
            if self.data[id] != None:
                return True
        return False

    def get_label(self):
        """Returns a unicode label describing the event."""
        return u"%s (%s)" % (self.text, self.time_period.get_label())

    def clone(self):
        # Objects of type datetime are immutable.
        new_event = Event(self.time_type, self.time_period.start_time,
                          self.time_period.end_time, self.text, self.category)
        # Description is immutable
        new_event.set_data("description", self.get_data("description") )
        # Icon is immutable in the sense that it is never changed by our
        # application.
        new_event.set_data("icon", self.get_data("icon"))
        new_event.set_data("hyperlink", self.get_data("hyperlink"))
        return new_event

    def is_container(self):
        return False

    def is_subevent(self):
        return False

    def time_span(self):
        return self.time_period.end_time - self.time_period.start_time
