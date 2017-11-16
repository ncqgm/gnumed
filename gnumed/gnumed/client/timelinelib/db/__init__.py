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


import os.path
import tempfile

from timelinelib.canvas.data.exceptions import TimelineIOError
from timelinelib.canvas.data import Category
from timelinelib.canvas.data import Event
from timelinelib.canvas.data import TimePeriod
from timelinelib.canvas.drawing.viewproperties import ViewProperties


def db_open(path, timetype=None):
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
        return open_gregorian_tutorial_timeline(path)
    elif path == ":numtutorial:":
        return open_numeric_tutorial_timeline(path)
    elif os.path.isdir(path):
        return open_directory_timeline(path)
    elif path.endswith(".timeline"):
        return db_open_timeline(path, timetype)
    elif path.endswith(".ics"):
        return db_open_ics(path)
    else:
        msg_template = (_("Unable to open timeline '%s'.") + "\n\n" +
                        _("Unknown format."))
        raise TimelineIOError(msg_template % path)


def open_gregorian_tutorial_timeline(path):
    from timelinelib.dataimport.tutorial import create_in_memory_gregorian_tutorial_db
    db = create_in_memory_gregorian_tutorial_db()
    db.path = path
    return db


def open_numeric_tutorial_timeline(path):
    from timelinelib.dataimport.tutorial import create_in_memory_numeric_tutorial_db
    db = create_in_memory_numeric_tutorial_db()
    db.path = path
    return db


def open_directory_timeline(path):
    from timelinelib.dataimport.dir import import_db_from_dir
    db = import_db_from_dir(path)
    db.path = path
    return db


def db_open_timeline(path, timetype=None):
    if (os.path.exists(path) and file_starts_with(path, "# Written by Timeline ")):
        raise TimelineIOError(_("You are trying to open an old file with a new version of timeline. Please install version 0.21.1 of timeline to convert it to the new format."))
    else:
        return db_open_newtype_timeline(path, timetype)


def db_open_newtype_timeline(path, timetype=None):
    if os.path.exists(path):
        from timelinelib.dataimport.timelinexml import import_db_from_timeline_xml
        db = import_db_from_timeline_xml(path)
        if dir_is_read_only(path):
            from timelinelib.wxgui.utils import display_warning_message
            db.set_readonly()
            display_warning_message(_("Since the directory of the Timeline file is not writable,\nthe timeline is opened in read-only mode"))
            return db
    else:
        from timelinelib.canvas.data.db import MemoryDB
        from timelinelib.calendar.gregorian.timetype import GregorianTimeType
        db = MemoryDB()
        if timetype is None:
            db.set_time_type(GregorianTimeType())
        else:
            db.set_time_type(timetype)

    def save_callback():
        from timelinelib.dataexport.timelinexml import export_db_to_timeline_xml
        export_db_to_timeline_xml(db, path)
    db.register_save_callback(save_callback)
    db.set_should_lock(True)
    return db


def dir_is_read_only(path):
    try:
        testfile = tempfile.TemporaryFile(dir=os.path.dirname(os.path.abspath(path)))
    except:
        return True
    else:
        testfile.close()
        return False


def db_open_ics(path):
    try:
        import icalendar
        from timelinelib.wxgui.dialogs.importics.view import ImportIcsDialog
    except ImportError:
        raise TimelineIOError(_("Could not find iCalendar Python package. It is required for working with ICS files."))
    else:
        from timelinelib.dataimport.ics import import_db_from_ics
        return import_db_from_ics(path, ImportIcsDialog)


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
