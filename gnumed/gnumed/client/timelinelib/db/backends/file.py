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


# This database was only used in version 0.1.0 - 0.9.0.
# We plan to remove this in version 1.0.0.


from datetime import datetime
from os.path import abspath
import base64
import codecs
import os.path
import re
import StringIO

import wx

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.db.utils import safe_write
from timelinelib.meta.version import get_version
from timelinelib.utils import ex_msg


ENCODING = "utf-8"


class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class FileTimeline(MemoryDB):
    """
    The general format of the file looks like this for version >= 0.3.0:

      # Written by Timeline 0.3.0 on 2009-7-23 9:40:33
      PREFERRED-PERIOD:...
      CATEGORY:...
      ...
      EVENT:...
      ...
      # END

    Only the first and last line are required. See comments in _load_*
    functions for information how the format looks like for the different
    parts.
    """

    def __init__(self, path):
        """
        Create a new timeline and read data from file.

        If the file does not exist a new timeline will be created.
        """
        MemoryDB.__init__(self)
        self.path = path
        self._load()

    def _parse_time(self, time_string):
        return self.get_time_type().parse_time(time_string)

    def _time_string(self, time):
        return self.get_time_type().time_string(time)

    def _load(self):
        """
        Load timeline data from the file that this timeline points to.

        This should only be done once when this class is created.

        The data is stored internally until we do a save.

        If a read error occurs a TimelineIOError will be raised.
        """
        if not os.path.exists(self.path):
            # Nothing to load. Will create a new timeline on save.
            return
        try:
            file = codecs.open(self.path, "r", ENCODING)
            try:
                self.disable_save()
                try:
                    self._load_from_lines(file)
                except Exception, pe:
                    # This should always be a ParseException, but if we made a
                    # mistake somewhere we still would like to mark the file as
                    # corrupt so we don't overwrite it later.
                    msg1 = _("Unable to read timeline data from '%s'.")
                    msg2 = "\n\n" + ex_msg(pe)
                    raise TimelineIOError((msg1 % abspath(self.path)) + msg2)
            finally:
                self.enable_save(call_save=False)
                file.close()
        except IOError, e:
            msg = _("Unable to read from file '%s'.")
            whole_msg = (msg + "\n\n%s") % (abspath(self.path), e)
            raise TimelineIOError(whole_msg)

    def _load_from_lines(self, file):
        current_line = file.readline()
        # Load header
        self._load_header(current_line.rstrip("\r\n"))
        current_line = file.readline()
        # Load preferred period
        if current_line.startswith("PREFERRED-PERIOD:"):
            self._load_preferred_period(current_line[17:].rstrip("\r\n"))
            current_line = file.readline()
        # Load categories
        hidden_categories = []
        while current_line.startswith("CATEGORY:"):
            (cat, hidden) = self._load_category(current_line[9:].rstrip("\r\n"))
            if hidden == True:
                hidden_categories.append(cat)
            current_line = file.readline()
        self._set_hidden_categories(hidden_categories)
        # Load events
        while current_line.startswith("EVENT:"):
            self._load_event(current_line[6:].rstrip("\r\n"))
            current_line = file.readline()
        # Check for footer if version >= 0.3.0 (version read by _load_header)
        if self.file_version >= (0, 3, 0):
            self._load_footer(current_line.rstrip("\r\n"))
            current_line = file.readline()
            # Ensure no more data
            if current_line:
                raise ParseException("File continues after EOF marker.")

    def _load_header(self, header_text):
        """
        Expected format '# Written by Timeline <version> on <date>'.

        Expected format of <version> '0.3.0[dev<revision>]'.

        We are just interested in the first part of the version.
        """
        match = re.search(r"^# Written by Timeline (\d+)\.(\d+)\.(\d+)",
                          header_text)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            tiny = int(match.group(3))
            self.file_version = (major, minor, tiny)
        else:
            raise ParseException("Unable to load header from '%s'." % header_text)

    def _load_preferred_period(self, period_text):
        """Expected format 'start_time;end_time'."""
        times = split_on_semicolon(period_text)
        try:
            if len(times) != 2:
                raise ParseException("Unexpected number of components.")
            tp = TimePeriod(self.get_time_type(), self._parse_time(times[0]),
                            self._parse_time(times[1]))
            self._set_displayed_period(tp)
            if not tp.is_period():
                raise ParseException("Length not > 0.")
        except ParseException, e:
            raise ParseException("Unable to parse preferred period from '%s': %s" % (period_text, ex_msg(e)))

    def _load_category(self, category_text):
        """
        Expected format 'name;color;visible'.

        Visible attribute added in version 0.2.0. If it is not found (we read
        an older file), we automatically set it to True.
        """
        category_data = split_on_semicolon(category_text)
        try:
            if len(category_data) != 2 and len(category_data) != 3:
                raise ParseException("Unexpected number of components.")
            name = dequote(category_data[0])
            color = parse_color(category_data[1])
            visible = True
            if len(category_data) == 3:
                visible = parse_bool(category_data[2])
            cat = Category(name, color, None, visible)
            self.save_category(cat)
            return (cat, not visible)
        except ParseException, e:
            raise ParseException("Unable to parse category from '%s': %s" % (category_text, ex_msg(e)))

    def _load_event(self, event_text):
        """
        Expected format 'start_time;end_time;text;category[;id:data]*'.

        Changed in version 0.4.0: made category compulsory and added support
        for additional data. Format for version < 0.4.0 looked like this:
        'start_time;end_time;text[;category]'.

        If an event does not have a category the empty string will be written
        as category name. Since category names can not be the empty string
        there will be no confusion.
        """
        event_specification = split_on_semicolon(event_text)
        try:
            if self.file_version < (0, 4, 0):
                if (len(event_specification) != 3 and
                    len(event_specification) != 4):
                    raise ParseException("Unexpected number of components.")
                start_time = self._parse_time(event_specification[0])
                end_time = self._parse_time(event_specification[1])
                text = dequote(event_specification[2])
                cat_name = None
                if len(event_specification) == 4:
                    cat_name = dequote(event_specification[3])
                category = self._get_category(cat_name)
                evt = Event(self.get_time_type(), start_time, end_time, text, category)
                self.save_event(evt)
                return True
            else:
                if len(event_specification) < 4:
                    raise ParseException("Unexpected number of components.")
                start_time = self._parse_time(event_specification[0])
                end_time = self._parse_time(event_specification[1])
                text = dequote(event_specification[2])
                category = self._get_category(dequote(event_specification[3]))
                event = Event(self.get_time_type(), start_time, end_time, text, category)
                for item in event_specification[4:]:
                    id, data = item.split(":", 1)
                    if id not in self.supported_event_data():
                        raise ParseException("Can't parse event data with id '%s'." % id)
                    decode = get_decode_function(id)
                    event.set_data(id, decode(dequote(data)))
                self.save_event(event)
        except ParseException, e:
            raise ParseException("Unable to parse event from '%s': %s" % (event_text, ex_msg(e)))

    def _load_footer(self, footer_text):
        """Expected format '# END'."""
        if not footer_text == "# END":
            raise ParseException("Unable to load footer from '%s'." % footer_text)

    def _get_category(self, name):
        for category in self.get_categories():
            if category.name == name:
                return category
        return None

    def _save(self):
        """
        Save timeline data to the file that this timeline points to.

        If we have read corrupt data from a file it is not possible to still
        have an instance of this database. So it is always safe to write.
        """
        def write_fn(file):
            self._write_header(file)
            self._write_preferred_period(file)
            self._write_categories(file)
            self._write_events(file)
            self._write_footer(file)
        safe_write(self.path, ENCODING, write_fn)

    def _write_header(self, file):
        file.write("# Written by Timeline %s on %s\n" % (
            get_version(),
            self._time_string(datetime.now())))

    def _write_preferred_period(self, file):
        tp = self._get_displayed_period()
        if tp is not None:
            file.write("PREFERRED-PERIOD:%s;%s\n" % (
                self._time_string(tp.start_time),
                self._time_string(tp.end_time)))

    def _write_categories(self, file):
        def save(category):
            r, g, b = cat.color
            visible = (category not in self._get_hidden_categories())
            file.write("CATEGORY:%s;%s,%s,%s;%s\n" % (quote(cat.name),
                                                      r, g, b,
                                                      visible))
        for cat in self.get_categories():
            save(cat)

    def _write_events(self, file):
        def save(event):
            file.write("EVENT:%s;%s;%s" % (
                self._time_string(event.time_period.start_time),
                self._time_string(event.time_period.end_time),
                quote(event.text)))
            if event.category:
                file.write(";%s" % quote(event.category.name))
            else:
                file.write(";")
            for data_id in self.supported_event_data():
                data = event.get_data(data_id)
                if data != None:
                    encode = get_encode_function(data_id)
                    file.write(";%s:%s" % (data_id,
                                           quote(encode(data))))
            file.write("\n")
        for event in self.get_all_events():
            save(event)

    def _write_footer(self, file):
        file.write(u"# END\n")


def parse_bool(bool_string):
    """
    Return True or False.

    Expected format 'True' or 'False'.
    """
    if bool_string == "True":
        return True
    elif bool_string == "False":
        return False
    else:
        raise ParseException("Unknown boolean '%s'" % bool_string)


def parse_color(color_string):
    """
    Return a tuple (r, g, b) or raise exception.

    Expected format 'r,g,b'.
    """
    def verify_255_number(num):
        if num < 0 or num > 255:
            raise ParseException("Color number not in range [0, 255], color string = '%s'" % color_string)
    match = re.search(r"^(\d+),(\d+),(\d+)$", color_string)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        verify_255_number(r)
        verify_255_number(g)
        verify_255_number(b)
        return (r, g, b)
    else:
        raise ParseException("Color not on correct format, color string = '%s'" % color_string)


def split_on_semicolon(text):
    """
    The delimiter is ; but only if not proceeded by backslash.

    Examples:

        'foo;bar' -> ['foo', 'bar']
        'foo\;bar;barfoo -> ['foo\;bar', 'barfoo']
    """
    return re.split(r"(?<!\\);", text)


def dequote(text):
    def repl(match):
        after_backslash = match.group(1)
        if after_backslash == "n":
            return "\n"
        elif after_backslash == "r":
            return "\r"
        else:
            return after_backslash
    return re.sub(r"\\(.)", repl, text)


def quote(text):
    def repl(match):
        match_char = match.group(0)
        if match_char == "\n":
            return "\\n"
        elif match_char == "\r":
            return "\\r"
        else:
            return "\\" + match_char
    return re.sub(";|\n|\r|\\\\", repl, text)


def identity(obj):
    return obj


def encode_icon(data):
    """Data is wx.Bitmap."""
    output = StringIO.StringIO()
    image = wx.ImageFromBitmap(data)
    image.SaveStream(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())


def decode_icon(string):
    """Return is wx.Bitmap."""
    input = StringIO.StringIO(base64.b64decode(string))
    image = wx.ImageFromStream(input, wx.BITMAP_TYPE_PNG)
    return image.ConvertToBitmap()


def get_encode_function(id):
    if id == "description":
        return identity
    elif id == "icon":
        return encode_icon
    else:
        raise ValueError("Can't find encode function for event data with id '%s'." % id)


def get_decode_function(id):
    if id == "description":
        return identity
    elif id == "icon":
        return decode_icon
    else:
        raise ValueError("Can't find decode function for event data with id '%s'." % id)
