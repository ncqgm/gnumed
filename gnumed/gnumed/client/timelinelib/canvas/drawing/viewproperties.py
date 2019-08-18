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


from timelinelib.general.observer import Observable


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
        self._hidden_category_ids = []
        self.period_selection = None
        self.divider_position = 0.5
        self.displayed_period = None
        self.hscroll_amount = 0
        self.view_cats_individually = False
        self.fixed_event_vertical_pos = False
        self.fuzzy_icon = None
        self.locked_icon = None
        self.hyperlink_icon = None
        self.skip_s_in_decade_text = False
        self.display_checkmark_on_events_done = False
        self._legend_pos = 0
        self._time_scale_pos = 1
        self._hide_events_done = False
        self._all_events = []
        self._event_highlight_counters = {}
        self._selection_rect = None

    def is_highlighted(self, event):
        return event.get_id() in self._event_highlight_counters

    def has_higlights(self):
        return len(self._event_highlight_counters) > 0

    def add_highlight(self, event, clear):
        if clear:
            self._event_highlight_counters.clear()
        self._event_highlight_counters[event.get_id()] = 0

    def get_highlight_count(self, event):
        return self._event_highlight_counters[event.get_id()]

    def tick_highlights(self, limit):
        self._event_highlight_counters = {
            event_id: count + 1
            for event_id, count in self._event_highlight_counters.items()
            if count < limit
        }

    @property
    def legend_pos(self):
        return self._legend_pos

    @legend_pos.setter
    def legend_pos(self, pos):
        self._legend_pos = pos

    @property
    def time_scale_pos(self):
        return self._time_scale_pos

    @time_scale_pos.setter
    def time_scale_pos(self, pos):
        self._time_scale_pos = pos

    @property
    def hide_events_done(self):
        return self._hide_events_done

    @hide_events_done.setter
    def hide_events_done(self, value):
        self._hide_events_done = value

    def get_fuzzy_icon(self):
        return self.fuzzy_icon

    def set_fuzzy_icon(self, name):
        self.fuzzy_icon = name

    def get_locked_icon(self):
        return self.locked_icon

    def set_locked_icon(self, name):
        self.locked_icon = name

    def get_hyperlink_icon(self):
        return self.hyperlink_icon

    def set_hyperlink_icon(self, name):
        self.hyperlink_icon = name

    def get_skip_s_in_decade_text(self):
        return self.skip_s_in_decade_text

    def set_skip_s_in_decade_text(self, value):
        self.skip_s_in_decade_text = value

    def get_display_checkmark_on_events_done(self):
        return self.display_checkmark_on_events_done

    def set_display_checkmark_on_events_done(self, value):
        self.display_checkmark_on_events_done = value

    def set_use_fixed_event_vertical_pos(self, value):
        self.fixed_event_vertical_pos = value

    def use_fixed_event_vertical_pos(self):
        return self.fixed_event_vertical_pos

    def clear_db_specific(self):
        self.sticky_balloon_event_ids = []
        self.hovered_event = None
        self.selected_event_ids = []
        self._hidden_category_ids = []
        self.period_selection = None
        self.displayed_period = None
        self._event_highlight_counters = {}
        self._notify()

    def change_hovered_event(self, event):
        if self.hovered_event != event:
            self.hovered_event = event
            self._notify()

    def set_selection_rect(self, rect):
        self._selection_rect = rect

    def change_view_cats_individually(self, view_cats_individually):
        if self.view_cats_individually != view_cats_individually:
            self.view_cats_individually = view_cats_individually
            self._notify()

    def get_displayed_period(self):
        return self.displayed_period

    def filter_events(self, events):
        self._all_events = events
        return [event for event in events if self._is_event_visible(event)]

    def _is_event_visible(self, event):
        if self._hide_events_done and event.get_progress() == 100:
            return False
        if event.is_subevent():
            return (self.is_event_with_category_visible(event.get_category()) and
                    self.is_event_with_category_visible(event.container.get_category()))
        else:
            return self.is_event_with_category_visible(event.get_category())

    def is_selected(self, event):
        return event.get_id() in self.selected_event_ids

    def clear_selected(self):
        if self.selected_event_ids:
            self.selected_event_ids = []
            self._notify()

    def select_all_events(self):
        self.selected_event_ids = [event.get_id() for event in self._all_events
                                   if not event.is_container()]
        self._notify()

    def event_is_hovered(self, event):
        return (self.hovered_event is not None and
                event.id == self.hovered_event.id)

    def event_has_sticky_balloon(self, event):
        return event.id in self.sticky_balloon_event_ids

    def set_event_has_sticky_balloon(self, event, has_sticky=True):
        if has_sticky is True and event.id not in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.append(event.id)
        elif has_sticky is False and event.id in self.sticky_balloon_event_ids:
            self.sticky_balloon_event_ids.remove(event.id)
        self._notify()

    def set_selected(self, event, is_selected=True):
        if is_selected is True and not event.get_id() in self.selected_event_ids:
            self.selected_event_ids.append(event.get_id())
            self._notify()
        elif is_selected is False and event.get_id() in self.selected_event_ids:
            self.selected_event_ids.remove(event.get_id())
            self._notify()

    def set_all_selected(self, events):
        for event in events:
            if not event.get_id() in self.selected_event_ids:
                self.selected_event_ids.append(event.get_id())
        self._notify()

    def set_only_selected(self, event, is_selected):
        if is_selected:
            if self.selected_event_ids != [event.get_id()]:
                self.selected_event_ids = [event.get_id()]
                self._notify()
        else:
            self.clear_selected()

    def set_displayed_period(self, period, notify=True):
        self.displayed_period = period
        if notify:
            self._notify()

    def get_selected_event_ids(self):
        return self.selected_event_ids[:]

    def toggle_category_visibility(self, category):
        self.set_category_visible(category,
                                  not self.is_category_visible(category))

    def is_category_visible(self, category):
        return category.get_id() not in self._hidden_category_ids

    def is_event_with_category_visible(self, category):
        if category is None:
            return True
        elif self.view_cats_individually:
            return self.is_category_visible(category)
        else:
            return self._is_category_recursively_visible(category)

    def _is_category_recursively_visible(self, category):
        if self.is_category_visible(category):
            if category._get_parent() is None:
                return True
            else:
                return self._is_category_recursively_visible(category._get_parent())
        else:
            return False

    def set_categories_visible(self, categories, is_visible=True):
        category_ids = [category.id for category in categories]
        self._set_categories_with_ids_visible(category_ids, is_visible)

    def set_category_visible(self, category, is_visible=True):
        self._set_categories_with_ids_visible([category.get_id()], is_visible)

    def _set_categories_with_ids_visible(self, category_ids, is_visible):
        need_notify = False
        for category_id in category_ids:
            if is_visible is True and category_id in self._hidden_category_ids:
                self._hidden_category_ids.remove(category_id)
                need_notify = True
            elif is_visible is False and category_id not in self._hidden_category_ids:
                self._hidden_category_ids.append(category_id)
                need_notify = True
        if need_notify:
            self._notify()
