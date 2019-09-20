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


from timelinelib.canvas.data.base import ItemBase
from timelinelib.canvas.data.immutable import ImmutableEvent
from timelinelib.canvas.data.item import TimelineItem
from timelinelib.canvas.drawing.drawers import get_progress_color


DEFAULT_COLOR = (200, 200, 200)
EXPORTABLE_FIELDS = (_("Text"), _("Description"), _("Start"), _("End"), _("Category"),
                     _("Fuzzy"), _("Locked"), _("Ends Today"), _("Hyperlink"),
                     _("Progress"), _("Progress Color"), _("Done Color"), _("Alert"),
                     _("Is Container"), _("Is Subevent"))


class Event(ItemBase, TimelineItem):

    def __init__(self, db=None, id_=None, immutable_value=ImmutableEvent()):
        ItemBase.__init__(self, db, id_, immutable_value)
        self._category = None
        self._categories = []
        self._container = None
        self._milestone = False

    def duplicate(self, target_db=None):
        duplicate = ItemBase.duplicate(self, target_db=target_db)
        if duplicate.db is self.db:
            duplicate.category = self.category
        duplicate.sort_order = None
        return duplicate

    def save(self):
        self._update_category_id()
        self._update_category_ids()
        self._update_container_id()
        self._update_sort_order()
        with self._db.transaction("Save event") as t:
            t.save_event(self._immutable_value, self.ensure_id())
        return self

    def reload(self):
        return self._db.find_event_with_id(self.id)

    def _update_category_id(self):
        if self.category is None:
            self._immutable_value = self._immutable_value.update(
                category_id=None
            )
        elif self.category.id is None:
            raise Exception("Unknown category")
        else:
            self._immutable_value = self._immutable_value.update(
                category_id=self.category.id
            )

    def _update_category_ids(self):
        if self._categories == list():
            self._immutable_value = self._immutable_value.update(
                category_ids={}
            )
        else:
            ids = [c.id for c in self._categories]
            # Using a dictionary because we don't have any ImmutableList class
            dic = {k: None for k in ids}
            self._immutable_value = self._immutable_value.update(
                category_ids=dic
            )

    def _update_container_id(self):
        if self.container is None:
            self._immutable_value = self._immutable_value.update(
                container_id=None
            )
        elif self.container.id is None:
            raise Exception("Unknown container")
        else:
            self._immutable_value = self._immutable_value.update(
                container_id=self.container.id
            )

    def _update_sort_order(self):
        if self.sort_order is None:
            self.sort_order = 1 + self.db.get_max_sort_order()

    def delete(self):
        with self._db.transaction("Delete event") as t:
            t.delete_event(self.id)
        self.id = None

    def __eq__(self, other):
        return (isinstance(other, Event) and
                self.get_fuzzy() == other.get_fuzzy() and
                self.get_locked() == other.get_locked() and
                self.get_ends_today() == other.get_ends_today() and
                self.get_id() == other.get_id() and
                self.get_time_period().start_time == other.get_time_period().start_time and
                (self.get_time_period().end_time == other.get_time_period().end_time or self.get_ends_today()) and
                self.get_text() == other.get_text() and
                self.get_category() == other.get_category() and
                self.get_description() == other.get_description() and
                self.get_hyperlink() == other.get_hyperlink() and
                self.get_progress() == other.get_progress() and
                self.get_alert() == other.get_alert() and
                self.get_icon() == other.get_icon() and
                self.get_default_color() == other.get_default_color())

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        raise NotImplementedError("I don't believe this is in use.")

    def __gt__(self, other):
        raise NotImplementedError("I don't believe this is in use.")

    def __le__(self, other):
        raise NotImplementedError("I don't believe this is in use.")

    def __ge__(self, other):
        raise NotImplementedError("I don't believe this is in use.")

    def __repr__(self):
        return "%s<id=%r, text=%r, time_period=%r, ...>" % (
            self.__class__.__name__,
            self.get_id(),
            self.get_text(),
            self.get_time_period()
        )

    def set_end_time(self, time):
        self.set_time_period(self.get_time_period().set_end_time(time))

    def get_text(self):
        return self._immutable_value.text

    def set_text(self, text):
        self._immutable_value = self._immutable_value.update(text=text.strip())
        return self

    text = property(get_text, set_text)

    def get_category(self):
        return self._category

    def get_category_name(self):
        if self.get_category():
            return self.get_category().get_name()
        else:
            return None

    def set_category(self, category):
        self._category = category
        return self

    category = property(get_category, set_category)

    def get_categories(self):
        return self._categories

    def set_categories(self, categories):
        if categories:
            if self.category:
                if self.category in categories:
                    categories.remove(self.category)
            else:
                self.category = categories[0]
                categories = categories[1:]
            self._categories = categories

    def get_container(self):
        return self._container

    def set_container(self, container):
        if self._container is not None:
            self._container.unregister_subevent(self)
        self._container = container
        if self._container is not None:
            self._container.register_subevent(self)
        return self

    container = property(get_container, set_container)

    def get_fuzzy(self):
        return self._immutable_value.fuzzy

    def set_fuzzy(self, fuzzy):
        self._immutable_value = self._immutable_value.update(fuzzy=fuzzy)
        return self

    fuzzy = property(get_fuzzy, set_fuzzy)

    def get_locked(self):
        return self._immutable_value.locked

    def set_locked(self, locked):
        self._immutable_value = self._immutable_value.update(locked=locked)
        return self

    locked = property(get_locked, set_locked)

    def get_ends_today(self):
        return self._immutable_value.ends_today

    def set_ends_today(self, ends_today):
        if not self.locked:
            self._immutable_value = self._immutable_value.update(ends_today=ends_today)
        return self

    ends_today = property(get_ends_today, set_ends_today)

    def get_description(self):
        return self._immutable_value.description

    def set_description(self, description):
        self._immutable_value = self._immutable_value.update(description=description)
        return self

    description = property(get_description, set_description)

    def get_icon(self):
        return self._immutable_value.icon

    def set_icon(self, icon):
        self._immutable_value = self._immutable_value.update(icon=icon)
        return self

    icon = property(get_icon, set_icon)

    def get_hyperlink(self):
        return self._immutable_value.hyperlink

    def set_hyperlink(self, hyperlink):
        self._immutable_value = self._immutable_value.update(hyperlink=hyperlink)
        return self

    hyperlink = property(get_hyperlink, set_hyperlink)

    def get_alert(self):
        return self._immutable_value.alert

    def set_alert(self, alert):
        self._immutable_value = self._immutable_value.update(alert=alert)
        return self

    alert = property(get_alert, set_alert)

    def get_progress(self):
        return self._immutable_value.progress

    def set_progress(self, progress):
        self._immutable_value = self._immutable_value.update(progress=progress)
        return self

    progress = property(get_progress, set_progress)

    def get_sort_order(self):
        return self._immutable_value.sort_order

    def set_sort_order(self, sort_order):
        self._immutable_value = self._immutable_value.update(sort_order=sort_order)
        return self

    sort_order = property(get_sort_order, set_sort_order)

    def get_default_color(self):
        color = self._immutable_value.default_color
        if color is None:
            color = DEFAULT_COLOR
        return color

    def set_default_color(self, color):
        self._immutable_value = self._immutable_value.update(default_color=color)
        return self

    default_color = property(get_default_color, set_default_color)

    def get_done_color(self):
        if self.category:
            return self.category.get_done_color()
        else:
            return get_progress_color(DEFAULT_COLOR)

    def get_progress_color(self):
        category = self.category
        if category:
            if self.get_progress() == 100:
                return category.get_done_color()
            else:
                return category.get_progress_color()
        else:
            return get_progress_color(DEFAULT_COLOR)

    def update(self, start_time, end_time, text, category=None, fuzzy=None,
               locked=None, ends_today=None):
        """Change the event data."""
        self.update_period(start_time, end_time)
        self.text = text.strip()
        self.category = category
        if ends_today is not None:
            if not self.locked:
                self.ends_today = ends_today
        if fuzzy is not None:
            self.fuzzy = fuzzy
        if locked is not None:
            self.locked = locked
        return self

    def get_data(self, event_id):
        """
        Return data with the given id or None if no data with that id exists.

        See set_data for information how ids map to data.
        """
        if event_id == "description":
            return self.description
        elif event_id == "icon":
            return self.icon
        elif event_id == "hyperlink":
            return self.hyperlink
        elif event_id == "alert":
            return self.alert
        elif event_id == "progress":
            return self.progress
        elif event_id == "default_color":
            if "default_color" in self._immutable_value:
                return self._immutable_value.default_color
            else:
                return None
        else:
            raise Exception("should not happen")

    def set_data(self, event_id, data):
        """
        Set data with the given id.

        Here is how ids map to data:

            description - string
            icon - wx.Bitmap
        """
        if event_id == "description":
            self.description = data
        elif event_id == "icon":
            self.icon = data
        elif event_id == "hyperlink":
            self.hyperlink = data
        elif event_id == "alert":
            self.alert = data
        elif event_id == "progress":
            self.progress = data
        elif event_id == "default_color":
            self.default_color = data
        else:
            raise Exception("should not happen")

    def get_whole_data(self):
        data = {}
        for event_id in DATA_FIELDS:
            data[event_id] = self.get_data(event_id)
        return data

    def set_whole_data(self, data):
        for event_id in DATA_FIELDS:
            self.set_data(event_id, data.get(event_id, None))

    data = property(get_whole_data, set_whole_data)

    def has_data(self):
        """Return True if the event has associated data, or False if not."""
        for event_id in DATA_FIELDS:
            if self.get_data(event_id) is not None:
                return True
        return False

    def has_balloon_data(self):
        """Return True if the event has associated data to be displayed in a balloon."""
        return (self.get_data("description") is not None or
                self.get_data("icon") is not None)

    def get_label(self, time_type):
        """Returns a unicode label describing the event."""
        event_label = "%s (%s)" % (
            self.text,
            time_type.format_period(self.get_time_period()),
        )
        duration_label = self._get_duration_label(time_type)
        if duration_label != "":
            return "%s  %s: %s" % (event_label, _("Duration"), duration_label)
        else:
            return event_label

    def _get_duration_label(self, time_type):
        label = time_type.format_delta(self.time_span())
        if label == "0":
            label = ""
        return label

    def is_container(self):
        return False

    def is_subevent(self):
        return False

    def is_milestone(self):
        return False

    def get_exportable_fields(self):
        return EXPORTABLE_FIELDS

    def set_milestone(self, value):
        self._milestone = value

    def get_milestone(self):
        return self._milestone


DATA_FIELDS = [
    "description",
    "icon",
    "hyperlink",
    "alert",
    "progress",
    "default_color",
]
