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
from timelinelib.db.objects import Category


class CategoryEditor(object):

    def __init__(self, view):
        self.view = view

    def edit(self, category, category_repository):
        self.category = category
        self.category_repository = category_repository
        try:
            tree = self.category_repository.get_tree(remove=self.category)
        except TimelineIOError, e:
            self.view.handle_db_error(e)
        else:
            self.view.set_category_tree(tree)
            if self.category is None:
                self.view.set_name("")
                self.view.set_color((255, 0, 0))
                self.view.set_font_color((0, 0, 0))
                self.view.set_parent(None)
            else:
                self.view.set_name(self.category.name)
                self.view.set_color(self.category.color)
                self.view.set_font_color(self.category.font_color)
                self.view.set_parent(self.category.parent)

    def save(self):
        try:
            new_name = self.view.get_name()
            new_color = self.view.get_color()
            new_font_color = self.view.get_font_color()
            new_parent = self.view.get_parent()
            if not self._name_valid(new_name):
                self.view.handle_invalid_name(new_name)
                return
            if self._name_in_use(new_name):
                self.view.handle_used_name(new_name)
                return
            if self.category is None:
                self.category = Category(new_name, new_color, new_font_color,
                                         True, parent=new_parent)
            else:
                self.category.name = new_name
                self.category.color = new_color
                self.category.font_color = new_font_color
                self.category.parent = new_parent
            self.category_repository.save(self.category)
            self.view.close()
        except TimelineIOError, e:
            self.view.handle_db_error(e)

    def _name_valid(self, name):
        return len(name) > 0

    def _name_in_use(self, name):
        for cat in self.category_repository.get_all():
            if cat != self.category and cat.name == name:
                return True
        return False
