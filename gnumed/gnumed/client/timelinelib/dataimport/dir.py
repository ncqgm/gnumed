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


from datetime import datetime
import colorsys
import os.path

from timelinelib.calendar.gregorian.gregorian import GregorianDateTime
from timelinelib.canvas.data.db import MemoryDB
from timelinelib.canvas.data.exceptions import TimelineIOError
from timelinelib.canvas.data import Category
from timelinelib.canvas.data import Event


def import_db_from_dir(path):
    db = MemoryDB()
    db.set_readonly()
    _load(db, path)
    db.clear_transactions()
    return db


def _load(db, dir_path):
    """
    Load timeline data from the given directory.

    Each filename inside the directory (at any level) becomes an event where
    the text is the filename name and the time is the modification time for
    the filename.

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
        color_ranges = {}  # Used to color categories
        color_ranges[dir_path] = (0.0, 1.0, 1.0)
        all_cats = []
        parents = {}
        for (dirpath, dirnames, filenames) in os.walk(dir_path):
            # Assign color ranges
            (rstart, rend, b) = color_ranges[dirpath]
            step = (rend - rstart) / (len(dirnames) + 1)
            next_start = rstart + step
            new_b = b - 0.2
            if new_b < 0:
                new_b = 0
            for dirname in dirnames:
                next_end = next_start + step
                color_ranges[os.path.join(dirpath, dirname)] = (next_start, next_end, new_b)
                next_start = next_end
            # Create the stuff
            p = parents.get(os.path.normpath(os.path.join(dirpath, "..")),
                            None)
            cat = Category().update(dirpath, (233, 233, 233), None, parent=p)
            parents[os.path.normpath(dirpath)] = cat
            all_cats.append(cat)
            db.save_category(cat)
            for filename in filenames:
                path_inner = os.path.join(dirpath, filename)
                evt = _event_from_path(db, path_inner)
                db.save_event(evt)
        # Hide all categories but the first
        db.set_hidden_categories(all_cats[1:])
        # Set colors and change names
        used_names = []
        for cat in db.get_categories():
            cat.color = _color_from_range(color_ranges[cat.name])
            cat.name = get_unique_cat_name(os.path.basename(cat.name), used_names)
            db.save_category(cat)
    except Exception as e:
        msg = _("Unable to read from filename '%s'.") % dir_path
        whole_msg = "%s\n\n%s" % (msg, e)
        print(whole_msg)
        raise TimelineIOError(whole_msg)


def get_unique_cat_name(name, used_names):
    cat_name = name
    if cat_name in used_names:
        i = 1
        cat_name = "%s(%d)" % (name, i)
        while cat_name in used_names:
            i += 1
            cat_name = "%s(%d)" % (name, i)
    used_names.append(cat_name)
    return cat_name


def _event_from_path(db, file_path):
    stat = os.stat(file_path)
    # st_atime (time of most recent access),
    # st_mtime (time of most recent content modification),
    # st_ctime (platform dependent; time of most recent metadata change on
    #           Unix, or the time of creation on Windows):
    dt = datetime.fromtimestamp(int(stat.st_mtime))
    start_time = GregorianDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second).to_time()
    end_time = start_time
    if start_time > end_time:
        start_time, end_time = end_time, start_time
    text = os.path.basename(file_path)
    category = _category_from_path(db, file_path)
    evt = Event().update(start_time, end_time, text, category)
    return evt


def _category_from_path(db, file_path):
    for cat in db.get_categories():
        if cat.name == os.path.dirname(file_path):
            return cat
    return None


def _color_from_range(color_range):
    (rstart, _, b) = color_range
    (r, g, b) = colorsys.hsv_to_rgb(rstart, b, 1)
    return (r * 255, g * 255, b * 255)
