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


import wx

from timelinelib.wxgui.dialogs.eventlist.view import EventListDialog


class SearchBarController(object):

    def __init__(self, view):
        self._view = view
        self._result = []
        self._result_index = 0
        self._last_search = None
        self._last_period = None

    def set_timeline_canvas(self, timeline_canvas):
        self._timeline_canvas = timeline_canvas
        self._view.Enable(timeline_canvas is not None)
        if timeline_canvas is not None:
            self._view.SetPeriodChoices(self._timeline_canvas.GetPeriodChoices())

    def search(self):
        new_search = self._view.GetValue()
        new_period = self._view.GetPeriod()
        if (
            (self._last_search is not None and self._last_search == new_search) and 
            (self._last_period is not None and self._last_period == new_period)):
            self.next()
        else:
            self._last_search = new_search
            self._last_period = new_period
            self._search_for_events(new_search, new_period)
            self._result_index = 0
            self.navigate_to_match()
            self._set_result_label()
            self._view.UpdateButtons()

    def _search_for_events(self, new_search, new_period):
        if self._timeline_canvas is not None:
            self._result = self._timeline_canvas.GetFilteredEvents(new_search, new_period)
        else:
            self._result = []
        
    def _set_result_label(self):
        nbr_of_matches = len(self._result)
        if nbr_of_matches == 0:
            self._view.UpdateNbrOfMatchesLabel(' ' * 4 + _('No matches found'))
        elif nbr_of_matches == 1:
            self._view.UpdateNbrOfMatchesLabel(' ' * 4 + _('Only one match found'))
        else:
            self._view.UpdateNbrOfMatchesLabel(' ' * 4 + '%d ' % nbr_of_matches + _('matches found'))

    def next(self):
        if self._on_last_match():
            self._result_index = 0
        else:
            self._result_index += 1
        self.navigate_to_match()
        self._view.UpdateButtons()

    def prev(self):
        if not self._on_first_match():
            self._result_index -= 1
            self.navigate_to_match()
            self._view.UpdateButtons()

    def list(self):
        event_list = [event.get_label(self._timeline_canvas.GetTimeType()) for event in self._result]
        dlg = EventListDialog(self._view, event_list)
        if dlg.ShowModal() == wx.ID_OK:
            self._result_index = dlg.GetSelectedIndex()
            self.navigate_to_match()
        dlg.Destroy()

    def navigate_to_match(self):
        if (self._timeline_canvas is not None and self._result_index in range(len(self._result))):
            event = self._result[self._result_index]
            self._timeline_canvas.Navigate(lambda tp: tp.center(event.mean_time()))
            self._timeline_canvas.HighligtEvent(event, clear=True)

    def enable_backward(self):
        return bool(self._result and self._result_index > 0)

    def enable_forward(self):
        return bool(self._result and self._result_index < (len(self._result) - 1))

    def enable_list(self):
        return bool(len(self._result) > 0)

    def _on_first_match(self):
        return self._result and self._result_index == 0

    def _on_last_match(self):
        return self._result and self._result_index == (len(self._result) - 1)


