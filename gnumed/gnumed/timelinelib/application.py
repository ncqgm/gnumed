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


from timelinelib.db.exceptions import TimelineIOError


class TimelineApplication(object):

    def __init__(self, main_frame, db_open_fn, config):
        self.main_frame = main_frame
        self.db_open_fn = db_open_fn
        self.config = config
        self.timeline = None

    def on_started(self, application_arguments):
        input_files = application_arguments.get_files()
        if len(input_files) == 0:
            ro = self.config.get_recently_opened()
            if self.config.get_open_recent_at_startup() and len(ro) > 0:
                self.main_frame.open_timeline_if_exists(ro[0])
        else:
            for input_file in input_files:
                self.main_frame.open_timeline(input_file)

    def open_timeline(self, path):
        try:
            self.timeline = self.db_open_fn(path, self.config.get_use_wide_date_range())
        except TimelineIOError, e:
            self.main_frame.handle_db_error(e)
        else:
            self.config.append_recently_opened(path)
            self.main_frame._update_open_recent_submenu()
            self.main_frame._display_timeline(self.timeline)

    def set_no_timeline(self):
        self.timeline = None
        self.main_frame._display_timeline(None)

    def on_play_clicked(self):
        self.main_frame.open_play_frame(self.timeline)
