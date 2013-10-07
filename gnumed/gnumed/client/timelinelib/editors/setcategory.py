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


from timelinelib.wxgui.utils import display_error_message

 
class SetCategoryEditor(object):
    
    def __init__(self, view, timeline, selected_event_ids=[]):
        self.view = view
        self.timeline = timeline
        self.selected_event_ids = selected_event_ids
            
    def save(self):
        category = self.view.get_category()
        if not self._category_is_given(category) and self.selected_event_ids == []:
            display_error_message(_("You must select a category!"))
        else:
            self._save_category_in_events(category)
            self.view.close()

    def _category_is_given(self, category):
        return category != None
    
    def _save_category_in_events(self, category):
        if self.selected_event_ids == []:
            self._save_category_in_events_for_events_without_category(category)
        else:
            self._save_category_in_events_for_selected_events(category)

    def _save_category_in_events_for_selected_events(self, category):
        for event_id in self.selected_event_ids:
            event = self.timeline.find_event_with_id(event_id)
            event.category = category

    def _save_category_in_events_for_events_without_category(self, category):
        for event in self.timeline.events:
            if event.category == None:
                event.category = category

    def _events_without_category_exists(self):
        for event in self.timeline.events:
            if event.category == None:
                return True
        return False
    
        