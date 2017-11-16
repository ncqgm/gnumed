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


from timelinelib.wxgui.framework import Controller


class ChangeNowDateDialogController(Controller):

    def on_init(self, db, handle_new_time_fn):
        self.db = db
        self.handle_new_time_fn = handle_new_time_fn
        self._set_initial_values()

    def on_show_time_changed(self, event):
        self.view.ShowTime(self.view.IsShowTimeChecked())

    def on_time_changed(self):
        try:
            self.db.set_saved_now(self._get_timepicker_time())
            self._trigger_new_time_callback()
        except ValueError:
            pass

    def _set_initial_values(self):
        self.view.SetNowValue(self.db.get_saved_now())
        self.view.ShowTime(self.view.IsShowTimeChecked())
        self.view.FocusTimePicker()
        self._trigger_new_time_callback()

    def _trigger_new_time_callback(self):
        self.handle_new_time_fn(self.db.get_saved_now())

    def _get_timepicker_time(self):
        time = self.view.GetNowValue()
        if time is None:
            raise ValueError()
        return time
