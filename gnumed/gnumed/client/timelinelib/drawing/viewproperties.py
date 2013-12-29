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


class ViewProperties(Observable):
    """
    Store properties of a view.

    Some timeline databases support storing some of these view properties
    together with the data.
    """

    def __init__(self):
        Observable.__init__(self)
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self.hidden_categories = []
        self.period_selection = None
        self.show_legend = True
        self.divider_position = 0.5
        self.displayed_period = None
        self.hscroll_amount = 0
        self.view_cats_individually = False

    def clear_db_specific(self):
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self.hidden_categories = []
        self.period_selection = None
        self.displayed_period = None
        self._notify()

    def change_hovered_event(self, event):
        if self.hovered_event != event:
            self.hovered_event = event
            self._notify()

    def change_show_legend(self, show):
        if self.show_legend != show:
            self.show_legend = show
            self._notify()

    def change_view_cats_individually(self, view_cats_individually):
        if self.view_cats_individually != view_cats_individually:
            self.view_cats_individually = view_cats_individually
            self._notify()

    def get_displayed_period(self):
        return self.displayed_period

    def filter_events(self, events):
        return [event for event in events if self._is_event_visible(event)]

    def _is_event_visible(self, event):
        if event.is_subevent():
            return (self.is_event_with_category_visible(event.category) and
                    self.is_event_with_category_visible(event.container.category))
        else:
            return self.is_event_with_category_visible(event.category)

    def is_selected(self, event):
        return event.id in self.selected_event_ids

    def clear_selected(self):
        if self.selected_event_ids:
            self.selected_event_ids = []
            self._notify()

    def event_is_hovered(self, event):
        return (self.hovered_event is not None and
                event.id == self.hovered_event.id)

    def event_has_sticky_balloon(self, event):
        return event.id in self.sticky_balloon_event_ids

    def set_event_has_sticky_balloon(self, event, has_sticky=True):
        if has_sticky == True and not event.id in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.append(event.id)
        elif has_sticky == False and event.id in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.remove(event.id)
        self._notify()

    def set_selected(self, event, is_selected=True):
        if is_selected == True and not event.id in self.selected_event_ids:
            self.selected_event_ids.append(event.id)
            self._notify()
        elif is_selected == False and event.id in self.selected_event_ids:
            self.selected_event_ids.remove(event.id)
            self._notify()

    def set_only_selected(self, event, is_selected):
        if is_selected:
            if self.selected_event_ids != [event.id]:
                self.selected_event_ids = [event.id]
                self._notify()
        else:
            self.clear_selected()

    def set_displayed_period(self, period):
        self.displayed_period = period
        self._notify()

    def get_selected_event_ids(self):
        return self.selected_event_ids[:]

    def toggle_category_visibility(self, category):
        self.set_category_visible(category,
                                  not self.is_category_visible(category))

    def is_category_visible(self, category):
        return category.id not in self.hidden_categories

    def is_event_with_category_visible(self, category):
        if category is None:
            return True
        elif self.view_cats_individually:
            return self.is_category_visible(category)
        else:
            return self._is_category_recursively_visible(category)

    def _is_category_recursively_visible(self, category):
        if self.is_category_visible(category):
            if category.parent is None:
                return True
            else:
                return self._is_category_recursively_visible(category.parent)
        else:
            return False

    def set_categories_visible(self, categories, is_visible=True):
        category_ids = [category.id for category in categories]
        self._set_categories_with_ids_visible(category_ids, is_visible)

    def set_category_visible(self, category, is_visible=True):
        self._set_categories_with_ids_visible([category.id], is_visible)

    def _set_categories_with_ids_visible(self, category_ids, is_visible):
        need_notify = False
        for id in category_ids:
            if is_visible == True and id in self.hidden_categories:
                self.hidden_categories.remove(id)
                need_notify = True
            elif is_visible == False and not id in self.hidden_categories:
                self.hidden_categories.append(id)
                need_notify = True
        if need_notify:
            self._notify()
