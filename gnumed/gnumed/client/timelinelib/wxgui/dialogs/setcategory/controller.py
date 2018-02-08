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


class SetCategoryDialogController(Controller):

    def on_init(self, db, selected_event_ids):
        self._db = db
        self._selected_event_ids = selected_event_ids
        self.view.PopulateCategories()
        self._set_title()

    def on_ok_clicked(self, event):
        category = self.view.GetSelectedCategory()
        if not self._category_is_given(category) and self._selected_event_ids == []:
            self.view.DisplayErrorMessage(_("You must select a category!"))
        else:
            self._save_category_in_events(category)
            self.view.EndModalOk()

    def _set_title(self):
        if self._selected_event_ids == []:
            self.view.SetTitle(_("Set Category on events without category"))
        else:
            self.view.SetTitle(_("Set Category on selected events"))

    def _category_is_given(self, category):
        return category is not None

    def _save_category_in_events(self, category):
        with self._db.transaction("Set category"):
            if self._selected_event_ids == []:
                self._save_category_in_events_for_events_without_category(category)
            else:
                self._save_category_in_events_for_selected_events(category)

    def _save_category_in_events_for_selected_events(self, category):
        for event_id in self._selected_event_ids:
            event = self._db.find_event_with_id(event_id)
            event.set_category(category)
            event.save()

    def _save_category_in_events_for_events_without_category(self, category):
        for event in self._db.get_all_events():
            if event.get_category() is None:
                event.set_category(category)
                event.save()
