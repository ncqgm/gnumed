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


from timelinelib.utilities.observer import Observable


class CategoriesFacade(Observable):

    def __init__(self, db, view_properties):
        Observable.__init__(self)
        self.db = db
        self.view_properties = view_properties
        self.db.listen_for_any(self._notify)
        self.view_properties.listen_for_any(self._notify)

    def get_all(self):
        return self.db.get_categories()

    def get_immediate_children(self, parent):
        return [category for category in self.db.get_categories()
                if category.parent == parent]

    def get_all_children(self, parent):
        all_children = []
        for child in self.get_immediate_children(parent):
            all_children.append(child)
            all_children.extend(self.get_all_children(child))
        return all_children

    def get_parents(self, child):
        parents = []
        while child.parent:
            parents.append(child.parent)
            child = child.parent
        return parents

    def get_parents_for_checked_childs(self):
        parents = []
        for category in self._get_all_checked_categories():
            parents.extend(self.get_parents(category))
        return parents

    def is_visible(self, category):
        return self.view_properties.is_category_visible(category)

    def is_event_with_category_visible(self, category):
        return self.view_properties.is_event_with_category_visible(category)

    def _get_all_checked_categories(self):
        return [category for category in self.db.get_categories()
                if self.is_visible(category)]
