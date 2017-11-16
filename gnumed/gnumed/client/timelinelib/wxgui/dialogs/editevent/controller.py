# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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

from timelinelib.canvas.data import Event
from timelinelib.canvas.data import Subevent
from timelinelib.canvas.data import TimePeriod
from timelinelib.features.experimental.experimentalfeatures import EXTENDED_CONTAINER_STRATEGY
from timelinelib.utils import ex_msg
from timelinelib.wxgui.framework import Controller


class EditEventDialogController(Controller):

    def on_init(self, config, time_type, event_repository, timeline, start, end, event):
        self.config = config
        self.timeline = timeline
        self.time_type = time_type
        self.event_repository = event_repository
        self._set_values(start, end, event)
        self.view.SetFocusOnFirstControl()

    def on_locked_checkbox_changed(self, event):
        self._enable_disable_ends_today()

    def on_container_changed(self, event):
        self._enable_disable_ends_today()
        self._enable_disable_locked(EXTENDED_CONTAINER_STRATEGY.enabled())

    def on_enlarge_click(self, event):
        self.reduced_size = self.view.GetSize()
        self.reduced_pos = self.view.GetPosition()
        screen_width, screen_height = wx.DisplaySize()
        dialog_size = (screen_width * 0.9, screen_height * 0.8)
        dialog_pos = (screen_width * 0.05, screen_height * 0.05)
        self._set_position_and_size(dialog_pos, dialog_size)

    def on_reduce_click(self, event):
        self._set_position_and_size(self.reduced_pos, self.reduced_size)

    def on_ok_clicked(self, event):
        self._create_or_update_event()

    def on_duplicate(self, evt):
        self._create_or_update_event()
        if self._done:
            self._duplicate_event()

    def _duplicate_event(self):
        dlg = self.view.GetDuplicateEventDialog(self.timeline, self.event)
        dlg.ShowModal()
        dlg.Destroy()

    def _create_or_update_event(self):
        try:
            with self.timeline.transaction("Save event"):
                self._save_event()
            if self.view.IsAddMoreChecked():
                self.event = None
                self.view.SetName("")
                self.view.ClearEventData()
                self.view.SetFocusOnFirstControl()
                self._done = False
            else:
                if self.opened_from_menu:
                    self.config.event_editor_show_period = self.view.GetShowPeriod()
                    self.config.event_editor_show_time = self.view.GetShowTime()
                self.view.EndModalOk()
                self._done = True
        except ValueError:
            self._done = True

    def _set_values(self, start, end, event):
        self.event = event
        self.opened_from_menu = self.event is None and start is None
        if self.event is None:
            self._set_period_in_view(start, end)
            self.view.SetName("")
            self.view.SetCategory(None)
            self.view.SetFuzzy(False)
            self.view.SetLocked(False)
            self.view.SetEndsToday(False)
            self.view.SetContainer(None)
            self.view.SetShowAddMoreCheckbox(True)
        else:
            self._set_period_in_view(
                self.event.get_time_period().start_time,
                self.event.get_time_period().end_time
            )
            self.view.SetName(self.event.get_text())
            self.view.SetCategory(self.event.get_category())
            self.view.SetFuzzy(self.event.get_fuzzy())
            self.view.SetLocked(self.event.get_locked())
            self.view.SetEndsToday(self.event.get_ends_today())
            self.view.SetEventData(self.event.data)
            if self.event.is_subevent():
                self.view.SetContainer(self.event.container)
            else:
                self.view.SetContainer(None)
            self.view.SetShowAddMoreCheckbox(False)

    def _set_period_in_view(self, start, end):
        self.view.SetPeriod(self._get_period(start, end))
        if self.event:
            pass
        else:
            if self.opened_from_menu:
                self.view.SetShowPeriod(self.config.event_editor_show_period)
                self.view.SetShowTime(self.config.event_editor_show_time)
            else:
                pass
        if self.config.never_use_time:
            self.view.DisableTime()
        elif self.event is None and self.config.uncheck_time_for_new_events:
            self.view.SetShowTime(False)

    def _get_period(self, start, end):
        if start is None and end is None:
            time = self.time_type.now()
            return TimePeriod(time, time)
        elif end is None:
            return TimePeriod(start, start)
        else:
            return TimePeriod(start, end)

    def _get_period_from_view(self):
        try:
            period = self.view.GetPeriod()
        except ValueError as ex:
            self.view.DisplayInvalidPeriod("%s" % ex_msg(ex))
            raise ValueError()
        (start, end) = (period.get_start_time(), period.get_end_time())
        if self.event is not None and self.view.GetLocked():
            self._verify_that_time_has_not_been_changed(start, end)
        end = self._adjust_end_if_ends_today(start, end)
        TimePeriod(start, end)
        return (start, end)

    def _verify_that_time_has_not_been_changed(self, start, end):
        original_start = self.event.get_start_time()
        original_end = self.event.get_end_time()
        if (original_start != start or
            (not self.view.GetEndsToday() and original_end != end)):
            self.view.SetPeriod(self.event.get_time_period())
            error_message = _("You can't change time when the Event is locked")
            self.view.DisplayInvalidPeriod(error_message)
            raise ValueError()

    def _save_event(self):
        if self.event is None:
            self._create_new_event()
        else:
            self._update_event()
        self.event.data = self.view.GetEventData()
        self._save_event_to_db()

    def _update_event(self):
        container_selected = (self.view.GetContainer() is not None)
        if container_selected:
            self._update_event_when_container_selected()
        else:
            self._update_event_when_container_not_selected()

    def _update_event_when_container_selected(self):
        if self.event.is_subevent():
            self._update_event_when_container_selected_and_event_is_subevent()
        else:
            self._add_event_to_container()

    def _update_event_when_container_selected_and_event_is_subevent(self):
        if self.event.container == self.view.GetContainer():
            (start, end) = self._get_period_from_view()
            self.event.update(
                start,
                end,
                self.view.GetName(),
                self.view.GetCategory(),
                self.view.GetFuzzy(),
                self.view.GetLocked(),
                self.view.GetEndsToday()
            )
        else:
            self._change_container()

    def _update_event_when_container_not_selected(self):
        if self.event.is_subevent():
            self._remove_event_from_container()
        else:
            (start, end) = self._get_period_from_view()
            self.event.update(
                start,
                end,
                self.view.GetName(),
                self.view.GetCategory(),
                self.view.GetFuzzy(),
                self.view.GetLocked(),
                self.view.GetEndsToday()
            )

    def _remove_event_from_container(self):
        self.event.container = None
        if self.event.id is not None:
            self.timeline.delete_event(self.event)
        self._create_new_event()

    def _add_event_to_container(self):
        self.timeline.delete_event(self.event)
        self._create_subevent()

    def _change_container(self):
        if self._is_new_container(self.view.GetContainer()):
            self._add_new_container()
        self._remove_event_from_container()
        self.event.container = self.view.GetContainer()

    def _create_new_event(self):
        if self.view.GetContainer() is not None:
            self._create_subevent()
        else:
            (start, end) = self._get_period_from_view()
            self.event = Event().update(
                start,
                end,
                self.view.GetName(),
                self.view.GetCategory(),
                self.view.GetFuzzy(),
                self.view.GetLocked(),
                self.view.GetEndsToday()
            )

    def _create_subevent(self):
        if self._is_new_container(self.view.GetContainer()):
            self._add_new_container()
        (start, end) = self._get_period_from_view()
        self.event = Subevent().update(
            start,
            end,
            self.view.GetName(),
            self.view.GetCategory(),
            ends_today=self.view.GetEndsToday()
        )
        self.event.container = self.view.GetContainer()

    def _is_new_container(self, container):
        return container not in self.timeline.get_containers()

    def _add_new_container(self):
        self._save_container_to_db()

    def _adjust_end_if_ends_today(self, start, end):
        if self.view.GetEndsToday():
            end_time = self.time_type.now()
        else:
            end_time = end
        if end_time < start:
            self.view.DisplayInvalidPeriod(_("End must be > Start"))
            raise ValueError()
        return end_time

    def _save_event_to_db(self):
        self.event_repository.save(self.event)

    def _save_container_to_db(self):
        self.event_repository.save(self.view.GetContainer())

    def _enable_disable_ends_today(self):
        enable = ((self._container_not_selected() or self._container_allows_ends_today()) and
                  not self.view.GetLocked() and
                  self._start_is_in_history())
        self.view.EnableEndsToday(enable)

    def _enable_disable_locked(self, extended_container_strategy_enabled):
        if self.event is not None and extended_container_strategy_enabled:
            enable = not self.event.is_container()
        else:
            enable = self._container_not_selected()
        self.view.EnableLocked(enable)

    def _container_not_selected(self):
        return self.view.GetContainer() is None

    def _container_allows_ends_today(self):
        container = self.view.GetContainer()
        if container is None:
            return True
        else:
            return container.allow_ends_today_on_subevents()

    def _start_is_in_history(self):
        if self.event is None:
            return True
        if self.event.get_start_time() is None:
            return False
        return self.event.get_start_time() < self.time_type.now()

    def _set_position_and_size(self, pos, size):
        self.view.SetPosition(pos)
        self.view.SetSize(size)
