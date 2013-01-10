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


from timelinelib.db.objects import Event
from timelinelib.db.objects import PeriodTooLongError
from timelinelib.db.objects import Subevent
from timelinelib.db.objects import TimePeriod
from timelinelib.utils import ex_msg


class EventEditor(object):

    def __init__(self, view):
        self.view = view

    def edit(self, time_type, event_repository, timeline, start, end, event):
        self.timeline = timeline
        self.time_type = time_type
        self.event_repository = event_repository
        self._set_values(start, end, event)
        self._set_view_content()

    def create_or_update_event(self):
        try:
            self._get_and_verify_input()
            self._save_event()
            if self.view.get_show_add_more():
                self.view.clear_dialog()
            else:
                self.view.close()
        except ValueError:
            pass

    def clear(self):
        self.name = ""
        self.event = None
        self.view.set_name(self.name)
        self.view.set_focus("start")

    def start_is_in_history(self):
        if self.start is None:
            return False
        return self.start < self.timeline.time_type.now()
    
    def _set_values(self, start, end, event):
        self.event = event
        if self.event != None:
            self.start = self.event.time_period.start_time
            self.end = self.event.time_period.end_time
            self.name = self.event.text
            self.category = self.event.category
            self.fuzzy = self.event.fuzzy
            self.locked = self.event.locked
            self.ends_today = self.event.ends_today
        else:
            self.start = start
            self.end = end
            self.name = ""
            self.category = None
            self.fuzzy = False
            self.locked = False
            self.ends_today = False

    def _set_view_content(self):
        if self.event != None:
            self.view.set_event_data(self.event.data)
            if self.event.is_subevent():
                self.view.set_container(self.event.container)
            else:
                self.view.set_container(None)
        else:
            self.view.set_container(None)
        self.view.set_start(self.start)
        self.view.set_end(self.end)
        self.view.set_name(self.name)
        self.view.set_category(self.category)
        self.view.set_show_period(self.end > self.start)
        self.view.set_show_time(self._event_has_nonzero_time())
        self.view.set_show_add_more(self.event == None)
        self.view.set_fuzzy(self.fuzzy)
        self.view.set_locked(self.locked)
        self.view.set_ends_today(self.ends_today)
        if self.start != self.end:
            self.view.set_focus("text")
        else:
            self.view.set_focus("start")

    def _get_and_verify_input(self):
        self.name = self._get_name(self.view.get_name())
        self.fuzzy = self.view.get_fuzzy()
        self.locked = self.view.get_locked()
        self.ends_today = self.view.get_ends_today()
        self.category = self.view.get_category()
        start = self.get_start_from_view()
        if self._dialog_has_signalled_invalid_input(start):
            raise ValueError()
        end = self.get_end_from_view()
        if self._dialog_has_signalled_invalid_input(end):
            raise ValueError()
        if self.event != None and self.locked:
            self._verify_that_time_has_not_been_changed(start, end)
        self.start = self._validate_and_save_start(self.get_start_from_view())
        self.end = self._validate_and_save_end(self.get_end_from_view())
        self._validate_period()
        self.container = self.view.get_container()

    def get_start_from_view(self):
        try:
            return self.view.get_start()
        except ValueError, ex:
            self.view.display_invalid_start("%s" % ex_msg(ex))

    def get_end_from_view(self):
        if self.view.get_show_period():
            try:
                return self.view.get_end()
            except ValueError, ex:
                self.view.display_invalid_end("%s" % ex_msg(ex))
        else:
            return self.get_start_from_view()

    def _dialog_has_signalled_invalid_input(self, time):
        return time == None

    def _verify_that_time_has_not_been_changed(self, start, end):
        self._exception_if_start_has_changed(start)
        if not self.ends_today:
            self._exception_if_end_has_changed(end)

    def _exception_if_start_has_changed(self, start):
        if not self.time_type.eventtimes_equals(self.start, start):
            self.view.set_start(self.start)
            self._exception_when_start_or_end_has_changed()

    def _exception_if_end_has_changed(self, end):
        if not self.time_type.eventtimes_equals(self.end, end):
            self.view.set_end(self.end)
            self._exception_when_start_or_end_has_changed()

    def _exception_when_start_or_end_has_changed(self):
        error_message = _("You can't change time when the Event is locked")
        self.view.display_invalid_start(error_message)
        raise ValueError()

    def _save_event(self):
        if self.event == None:
            self._create_new_event()
        else:
            self._update_event()
        self.event.data = self.view.get_event_data()
        self._save_event_to_db()

    def _update_event(self):
        container_selected = (self.container != None)
        if container_selected:
            if self.event.is_subevent():
                if self.event.container == self.container:
                    self.event.update(self.start, self.end, self.name,
                                      self.category, self.fuzzy, self.locked,
                                      self.ends_today)
                else:
                    self._change_container()
            else:
                self._add_event_to_container()
        else:
            if self.event.is_subevent():
                self._remove_event_from_container()
                pass
            else:
                self.event.update(self.start, self.end, self.name,
                                  self.category, self.fuzzy, self.locked,
                                  self.ends_today)

    def _remove_event_from_container(self):
        self.event.container.unregister_subevent(self.event)
        self.timeline.delete_event(self.event)
        self._create_new_event()

    def _add_event_to_container(self):
        self.timeline.delete_event(self.event)
        self._create_subevent()

    def _change_container(self):
        self.event.container.unregister_subevent(self.event)
        self.container.register_subevent(self.event)

    def _create_new_event(self):
        if self.container != None:
            self._create_subevent()
        else:
            self.event = Event(self.time_type, self.start, self.end, self.name,
                               self.category, self.fuzzy, self.locked,
                               self.ends_today)

    def _create_subevent(self):
        if self.is_new_container(self.container):
            self.add_new_container()
        self.event = Subevent(self.time_type, self.start, self.end, self.name,
                              self.category, self.container)

    def is_new_container(self, container):
        return container not in self.timeline.get_containers()

    def add_new_container(self):
        max_id = 0
        for container in self.timeline.get_containers():
            if container.cid() > max_id:
                max_id = container.cid()
        max_id += 1
        self.container.set_cid(max_id)
        self._save_container_to_db()

    def _validate_and_save_start(self, start):
        if start == None:
            raise ValueError()
        return start

    def _validate_and_save_end(self, end):
        if end == None:
            raise ValueError()
        if end < self.start:
            self.view.display_invalid_start(_("End must be > Start"))
            raise ValueError()
        return end

    def _validate_period(self):
        try:
            TimePeriod(self.time_type, self.start, self.end)
        except PeriodTooLongError:
            self.view.display_error_message(_("Entered period is too long."))
            raise ValueError()

    def _get_name(self, name):
        if name == "":
            msg = _("Field '%s' can't be empty.") % _("Text")
            self.view.display_invalid_name(msg)
            raise ValueError()
        return name

    def _save_event_to_db(self):
        try:
            self.event_repository.save(self.event)
        except Exception, e:
            self.view.display_db_exception(e)

    def _save_container_to_db(self):
        try:
            self.event_repository.save(self.container)
        except Exception, e:
            self.view.display_db_exception(e)

    def _event_has_nonzero_time(self):
        try:
            time_type = self.time_type
            time_period = TimePeriod(time_type, self.start, self.end)
            return time_period.has_nonzero_time()
        except Exception:
            return False
