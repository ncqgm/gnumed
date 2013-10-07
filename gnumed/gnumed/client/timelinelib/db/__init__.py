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


import os.path

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.backends.tutorial import create_in_memory_tutorial_db
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.wxgui.utils import display_warning_message


current_timeline = None


def db_open(path, import_timeline=False):
    """
    Create timeline database that can read and write timeline data from and to
    persistent storage identified by path.

    Throw a TimelineIOError exception if not able to read from the given path.

    Valid values for path:

      - special string ":tutorial:"
      - string with suffix .timeline
      - string with suffix .ics
      - string denoting a directory
    """
    if path == ":tutorial:":
        return open_tutorial_timeline(path)
    elif os.path.isdir(path):
        return open_directory_timeline(path)
    elif path.endswith(".timeline"):
        return db_open_timeline(path, import_timeline)
    elif path.endswith(".ics"):
        return db_open_ics(path, import_timeline)
    else:
        msg_template = (_("Unable to open timeline '%s'.") + "\n\n" +
                        _("Unknown format."))
        raise TimelineIOError(msg_template % path)


def open_tutorial_timeline(path):
    global current_timeline
    current_timeline = create_in_memory_tutorial_db()
    current_timeline.path = path
    return  current_timeline


def open_directory_timeline(path):
    from timelinelib.db.backends.dir import DirTimeline
    global current_timeline
    current_timeline = DirTimeline(path)
    current_timeline.path = path
    return current_timeline


def db_open_timeline(path, import_timeline=False):
    if import_timeline and current_timeline:
        return db_import_timeline(path)
    elif (os.path.exists(path) and file_starts_with(path, "# Written by Timeline ")):
        raise TimelineIOError(_("You are trying to open an old file with a new version of timeline. Please install version 0.21.1 of timeline to convert it to the new format."))
    else:
        return db_open_newtype_timeline(path)


def db_import_timeline(path):
    global current_timeline
    if os.path.isdir(current_timeline.path):
        display_warning_message(_("Other timelines can't be imported to a directory timeline"))
        return current_timeline
    if current_timeline.path == ":tutorial:":
        display_warning_message(_("Tutorial must be saved as a timeline to be able to import other timeline"))
        return current_timeline
    extension = current_timeline.path.rsplit(".", 1)[1]
    if extension != "timeline":
        display_warning_message(_("Only %s files can be imported") % extension)
        return current_timeline
    current_timeline.import_timeline(path)
    return current_timeline


def db_open_newtype_timeline(path):
    global current_timeline
    from timelinelib.db.backends.xmlfile import XmlTimeline
    current_timeline = XmlTimeline(path, import_timeline=False)
    return current_timeline


def db_open_ics(path, import_timeline=False):
    global current_timeline
    try:
        import icalendar
    except ImportError:
        raise TimelineIOError(_("Could not find iCalendar Python package. It is required for working with ICS files. See the Timeline website or the doc/installing.rst file for instructions how to install it."))
    else:
        from timelinelib.db.backends.ics import IcsTimeline
        if import_timeline and current_timeline:
            extension = current_timeline.path.rsplit(".", 1)[1]
            if extension != "ics":
                display_warning_message(_("Only %s files can be imported") % extension)
                return current_timeline
            current_timeline.import_timeline(path)
        else:
            current_timeline = IcsTimeline(path)
        return current_timeline


def file_starts_with(path, start):
    return read_first_line(path).startswith(start)


def read_first_line(path):
    try:
        f = open(path)
        try:
            line = f.readline()
            return line
        finally:
            f.close()
    except IOError:
        raise TimelineIOError("Unable to read data from '%s'." % path)


def copy_db(from_db, to_db):
    """
    Copy all content from one db to another.

    to_db is assumed to have no categories (conflicting category names are not
    handled).
    """
    if isinstance(to_db, MemoryDB):
        to_db.disable_save()
    # Copy categories (parent attribute fixed later)
    cat_map = {}
    for cat in from_db.get_categories():
        # name, color, and visible all immutable so safe to copy
        new_cat = Category(cat.name, cat.color, None, cat.visible)
        cat_map[cat.name] = new_cat
        to_db.save_category(new_cat)
    # Fix parent attribute
    for cat in from_db.get_categories():
        if cat.parent is not None:
            cat_map[cat.name].parent = cat_map[cat.parent.name]
    # Copy events
    for event in from_db.get_all_events():
        cat = None
        if event.category is not None:
            cat = cat_map[event.category.name]
        # start_time, end_time, and text all immutable so safe to copy
        new_event = Event(to_db.get_time_type(), event.time_period.start_time,
                          event.time_period.end_time,
                          event.text,
                          cat)
        # description immutable so safe to copy
        if event.get_data("description") is not None:
            new_event.set_data("description", event.get_data("description"))
        # icon immutable in practice (since never modified) so safe to copy
        if event.get_data("icon") is not None:
            new_event.set_data("icon", event.get_data("icon"))
        to_db.save_event(new_event)
    # Copy view properties (ViewProperties is specific to db so we need to copy
    # like this instead of just using load/save_view_properties in db).
    from_vp = ViewProperties()
    from_db.load_view_properties(from_vp)
    to_vp = ViewProperties()
    for from_cat in from_db.get_categories():
        cat = cat_map[from_cat.name]
        visible = from_vp.category_visible(from_cat)
        to_vp.set_category_visible(cat, visible)
    if from_vp.displayed_period is not None:
        # start_time and end_time immutable so safe to copy
        start = from_vp.displayed_period.start_time
        end = from_vp.displayed_period.end_time
        to_vp.displayed_period = TimePeriod(to_db.get_time_type(), start, end)
    to_db.save_view_properties(to_vp)
    # Save
    if isinstance(to_db, MemoryDB):
        to_db.enable_save()
