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


"""
Implementation of read-only timeline database where events show modification
times of files in a directory.
"""


import os
import os.path
import colorsys
from datetime import datetime
from datetime import timedelta
import time

import wx

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event


class DirTimeline(MemoryDB):

    def __init__(self, path):
        MemoryDB.__init__(self)
        self._load(path)

    def is_read_only(self):
        """Override MemoryDB's read-only attribute."""
        return True

    def _load(self, dir_path):
        """
        Load timeline data from the given directory.

        Each file inside the directory (at any level) becomes an event where
        the text is the file name and the time is the modification time for
        the file.

        For each sub-directory a category is created and all events (files)
        belong the category (directory) in which they are.
        """
        if not os.path.exists(dir_path):
            # Nothing to load
            return
        if not os.path.isdir(dir_path):
            # Nothing to load
            return
        try:
            self.disable_save()
            color_ranges = {} # Used to color categories
            color_ranges[dir_path] = (0.0, 1.0, 1.0)
            all_cats = []
            parents = {}
            for (dirpath, dirnames, filenames) in os.walk(dir_path):
                # Assign color ranges
                range = (rstart, rend, b) = color_ranges[dirpath]
                step = (rend - rstart) / (len(dirnames) + 1)
                next_start = rstart + step
                new_b = b - 0.2
                if new_b < 0:
                    new_b = 0
                for dir in dirnames:
                    next_end = next_start + step
                    color_ranges[os.path.join(dirpath, dir)] = (next_start,
                                                                next_end, new_b)
                    next_start = next_end
                # Create the stuff
                p = parents.get(os.path.normpath(os.path.join(dirpath, "..")),
                                None)
                cat = Category(dirpath, (233, 233, 233), None, False, parent=p)
                parents[os.path.normpath(dirpath)] = cat
                all_cats.append(cat)
                self.save_category(cat)
                for file in filenames:
                    path_inner = os.path.join(dirpath, file)
                    evt = self._event_from_path(path_inner)
                    self.save_event(evt)
            # Hide all categories but the first
            self._set_hidden_categories(all_cats[1:])
            # Set colors and change names
            for cat in self.get_categories():
                cat.color = self._color_from_range(color_ranges[cat.name])
                cat.name = os.path.basename(cat.name)
                self.save_category(cat)
        except Exception, e:
            msg = _("Unable to read from file '%s'.") % dir_path
            whole_msg = "%s\n\n%s" % (msg, e)
            raise TimelineIOError(whole_msg)
        finally:
            self.enable_save(call_save=False)

    def _event_from_path(self, file_path):
        stat = os.stat(file_path)
        # st_atime (time of most recent access),
        # st_mtime (time of most recent content modification),
        # st_ctime (platform dependent; time of most recent metadata change on
        #           Unix, or the time of creation on Windows):
        start_time = datetime.fromtimestamp(int(stat.st_mtime))
        end_time = start_time
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        text = os.path.basename(file_path)
        category = self._category_from_path(file_path)
        evt = Event(self.get_time_type(), start_time, end_time, text, category)
        return evt

    def _category_from_path(self, file_path):
        for cat in self.get_categories():
            if cat.name == os.path.dirname(file_path):
                return cat
        return None

    def _category_from_name(self, name):
        for cat in self.get_categories():
            if cat.name == name:
                return cat
        return None

    def _color_from_range(self, range):
        (rstart, rend, b) = range
        (r, g, b) = colorsys.hsv_to_rgb(rstart, b, 1)
        return (r*255, g*255, b*255)
