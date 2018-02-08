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


from timelinelib.wxgui.framework import Controller


class EditCategoryDialogController(Controller):

    def on_init(self, db, category):
        self._db = db
        self._create_category(category)
        self.view.PopulateCategories(exclude=category)
        self._populate_view()

    def on_ok_clicked(self, event):
        if self._validate():
            self._populate_category()
            self._category.save()
            self.view.EndModalOk()

    def get_edited_category(self):
        return self._category

    def _create_category(self, category):
        if category is None:
            self._category = self._db.new_category()
        else:
            self._category = category

    def _populate_view(self):
        self.view.SetName(self._category.name)
        self.view.SetColor(self._category.color)
        self.view.SetProgressColor(self._category.progress_color)
        self.view.SetDoneColor(self._category.done_color)
        self.view.SetFontColor(self._category.font_color)
        self.view.SetParent(self._category.parent)

    def _validate(self):
        new_name = self.view.GetName()
        if not self._is_name_valid(new_name):
            self.view.HandleInvalidName(new_name)
            return False
        if self._is_name_in_use(new_name):
            self.view.HandleUsedName(new_name)
            return False
        return True

    def _is_name_valid(self, name):
        return len(name) > 0

    def _is_name_in_use(self, name):
        for cat in self._db.get_categories():
            if cat != self._category and cat.get_name() == name:
                return True
        return False

    def _populate_category(self):
        self._category.name = self.view.GetName()
        self._category.color = self.view.GetColor()
        self._category.progress_color = self.view.GetProgressColor()
        self._category.done_color = self.view.GetDoneColor()
        self._category.font_color = self.view.GetFontColor()
        self._category.parent = self.view.GetParent()
