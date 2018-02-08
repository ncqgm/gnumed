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
from timelinelib.canvas.data.immutable import ImmutableCategory
from timelinelib.canvas.drawing.drawers import get_progress_color


EXPORTABLE_FIELDS = FIELDS = (_("Name"), _("Color"), _("Progress Color"), _("Done Color"), _("Parent"))


class Category(ItemBase):

    def __init__(self, db=None, id_=None, immutable_value=ImmutableCategory()):
        ItemBase.__init__(self, db, id_, immutable_value)
        self._parent = None

    def duplicate(self, target_db=None):
        duplicate = ItemBase.duplicate(self, target_db=target_db)
        if duplicate.db is self.db:
            duplicate.parent = self.parent
        return duplicate

    def update(self, name, color, font_color, parent=None):
        self.parent = None
        self.name = name
        self.color = color
        self.progress_color = get_progress_color(color)
        self.done_color = get_progress_color(color)
        if font_color is None:
            self.font_color = (0, 0, 0)
        else:
            self.font_color = font_color
        self.parent = parent
        return self

    def save(self):
        self._update_parent_id()
        with self._db.transaction("Save category") as t:
            t.save_category(self._immutable_value, self.ensure_id())
        return self

    def _update_parent_id(self):
        if self.parent is None:
            self._immutable_value = self._immutable_value.update(
                parent_id=None
            )
        elif self.parent.id is None:
            raise Exception("Unknown parent")
        else:
            self._immutable_value = self._immutable_value.update(
                parent_id=self.parent.id
            )

    def delete(self):
        with self._db.transaction("Delete category") as t:
            t.delete_category(self.id)
        self.id = None

    def reload(self):
        return self._db.get_category_by_id(self.id)

    def get_name(self):
        return self._immutable_value.name

    def set_name(self, name):
        self._immutable_value = self._immutable_value.update(name=name)
        return self

    name = property(get_name, set_name)

    def get_color(self):
        return self._immutable_value.color

    def set_color(self, color):
        self._immutable_value = self._immutable_value.update(color=color)
        return self

    color = property(get_color, set_color)

    def get_progress_color(self):
        return self._immutable_value.progress_color

    def set_progress_color(self, color):
        self._immutable_value = self._immutable_value.update(progress_color=color)
        return self

    progress_color = property(get_progress_color, set_progress_color)

    def get_done_color(self):
        return self._immutable_value.done_color

    def set_done_color(self, color):
        self._immutable_value = self._immutable_value.update(done_color=color)
        return self

    done_color = property(get_done_color, set_done_color)

    def get_font_color(self):
        return self._immutable_value.font_color

    def set_font_color(self, font_color):
        self._immutable_value = self._immutable_value.update(font_color=font_color)
        return self

    font_color = property(get_font_color, set_font_color)

    def _get_parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent
        return self

    parent = property(_get_parent, set_parent)

    def get_exportable_fields(self):
        return EXPORTABLE_FIELDS

    def __repr__(self):
        return "Category<id=%r, name=%r, color=%r, font_color=%r>" % (
            self.get_id(), self.get_name(), self.get_color(),
            self.get_font_color())

    def __eq__(self, other):
        if self is other:
            return True
        return (isinstance(other, Category) and
                self.get_id() == other.get_id() and
                self.get_name() == other.get_name() and
                self.get_color() == other.get_color() and
                self.get_progress_color() == other.get_progress_color() and
                self.get_done_color() == other.get_done_color() and
                self.get_font_color() == other.get_font_color() and
                self._get_parent() == other._get_parent())

    def __ne__(self, other):
        return not (self == other)


def sort_categories(categories):
    return sorted(list(categories), key=lambda category: category.get_name().lower())
