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


class PreferencesEditor(object):

    def __init__(self, dialog, config):
        self.dialog = dialog
        self.config = config
        self.weeks_map = ((0, "monday"), (1, "sunday"))

    def initialize_controls(self):
        self.dialog.set_checkbox_use_inertial_scrolling(
            self.config.get_use_inertial_scrolling())
        self.dialog.set_checkbox_open_recent_at_startup(
            self.config.get_open_recent_at_startup())
        index = self._week_index(self.config.week_start)
        self.dialog.set_week_start(index)

    def on_use_inertial_scrolling_changed(self, value):
        self.config.set_use_inertial_scrolling(value)

    def on_open_recent_changed(self, value):
        self.config.set_open_recent_at_startup(value)

    def on_week_start_changed(self, value):
        self.config.week_start = self._index_week(value)

    def _week_index(self, week):
        for (i, w) in self.weeks_map:
            if w == week:
                return i
        raise ValueError("Unknown week '%s'." % week)

    def _index_week(self, index):
        for (i, w) in self.weeks_map:
            if i == index:
                return w
        raise ValueError("Unknown week index '%s'." % index)
