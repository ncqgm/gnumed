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


class ViewProperties(object):
    """
    Store properties of a view.

    Some timeline databases support storing some of these view properties
    together with the data.
    """

    def __init__(self):
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

    def get_displayed_period(self):
        return self.displayed_period
    
    def filter_events(self, events):
        if self.view_cats_individually:
            return self.filter_events_individually(events)
        else:
            return self.filter_events_with_all_parents_selected(events)

    def filter_events_with_all_parents_selected(self, events):
        def category_visible(e, cat):
            if cat is None:
                return True
            elif e.is_subevent():
                container_visible = category_visible(e.container,
                                                     e.container.category)
                if container_visible:
                    if self.category_visible(cat) == True:
                        return category_visible(e, cat.parent)
                    else:
                        return False
                else:
                    return False
            elif self.category_visible(cat) == True:
                return category_visible(e, cat.parent)
            else:
                return False
        return [e for e in events if category_visible(e, e.category)]

    def filter_events_individually(self, events):
        def category_visible(e, cat):
            if cat is None:
                return True
            elif e.is_subevent():
                container_visible = category_visible(e.container,
                                                     e.container.category)
                if container_visible:
                    if self.category_visible(cat) == True:
                        return True
                    else:
                        return False
                else:
                    return False
            elif self.category_visible(cat) == True:
                return True
            else:
                return False
        return [e for e in events if category_visible(e, e.category)]

    def is_selected(self, event):
        return event.id in self.selected_event_ids

    def clear_selected(self):
        self.selected_event_ids = []

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

    def set_selected(self, event, is_selected=True):
        if is_selected == True and not event.id in self.selected_event_ids:
            self.selected_event_ids.append(event.id)
        elif is_selected == False and event.id in self.selected_event_ids:
            self.selected_event_ids.remove(event.id)

    def set_displayed_period(self, period):
        self.displayed_period = period

    def get_selected_event_ids(self):
        return self.selected_event_ids[:]

    def category_visible(self, category):
        return not category.id in self.hidden_categories

    def set_category_visible(self, category, is_visible=True):
        if is_visible == True and category.id in self.hidden_categories:
            self.hidden_categories.remove(category.id)
        elif is_visible == False and not category.id in self.hidden_categories:
            self.hidden_categories.append(category.id)

