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
Implementation of timeline database with xml file storage.
"""


from os.path import abspath
from xml.sax.saxutils import escape as xmlescape
import base64
import os.path
import re
import shutil
import StringIO

import wx

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Container
from timelinelib.db.objects import Event
from timelinelib.db.objects import Subevent
from timelinelib.db.objects import TimePeriod
from timelinelib.db.utils import safe_write, create_non_exising_path
from timelinelib.meta.version import get_version
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.utils import ex_msg
from timelinelib.xml.parser import ANY
from timelinelib.xml.parser import OPTIONAL
from timelinelib.xml.parser import parse
from timelinelib.xml.parser import parse_fn_store
from timelinelib.xml.parser import SINGLE
from timelinelib.xml.parser import Tag


ENCODING = "utf-8"
INDENT1 = "  "
INDENT2 = "    "
INDENT3 = "      "


# Must be defined before the XmlTimeline class since it is used as a decorator
def wrap_in_tag(func, name, indent=""):
    def wrapper(*args, **kwargs):
        file = args[1] # 1st argument is self, 2nd argument is file
        file.write(indent)
        file.write("<")
        file.write(name)
        file.write(">\n")
        func(*args, **kwargs)
        file.write(indent)
        file.write("</")
        file.write(name)
        file.write(">\n")
    return wrapper


class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class XmlTimeline(MemoryDB):

    def __init__(self, path, load=True, import_timeline=False):
        MemoryDB.__init__(self)
        self.path = path
        self.time_type = GregorianTimeType()
        if load == True:
            self._load()
            self._fill_containers()

    def _parse_time(self, time_string):
        return self.get_time_type().parse_time(time_string)

    def _time_string(self, time):
        return self.get_time_type().time_string(time)

    def _fill_containers(self):
        container_events = [event for event in self.events
                            if event.is_container()]
        subevents = [event for event in self.events
                     if event.is_subevent()]
        containers = {}
        for container in container_events:
            containers[container.cid()] = container
        for subevent in subevents:
            try:
                container = containers[subevent.cid()]
                container.register_subevent(subevent)
            except:
                #TODO: Create container
                pass

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
            # _parse_version will create the rest of the schema dynamically
            partial_schema = Tag("timeline", SINGLE, None, [
                Tag("version", SINGLE, self._parse_version)
            ])
            tmp_dict = {
                "partial_schema": partial_schema,
                "category_map": {},
                "hidden_categories": [],
            }
            self.disable_save()
            parse(self.path, partial_schema, tmp_dict)
            self.enable_save(call_save=False)
        except Exception, e:
            msg = _("Unable to read timeline data from '%s'.")
            whole_msg = (msg + "\n\n%s") % (abspath(self.path), ex_msg(e))
            raise TimelineIOError(whole_msg)

    def import_timeline(self, path):
        try:
            self.importing = True
            p = self.path
            self.path = path
            self._load()
            self._fill_containers()
            self.path = p
        finally:
            self.importing = False

    def _parse_version(self, text, tmp_dict):
        match = re.search(r"^(\d+).(\d+).(\d+)(dev.*)?$", text)
        if match:
            (x, y, z) = (int(match.group(1)), int(match.group(2)),
                         int(match.group(3)))
            self._backup((x, y, z))
            tmp_dict["version"] = (x, y, z)
            self._create_rest_of_schema(tmp_dict)
        else:
            raise ParseException("Could not parse version number from '%s'."
                                 % text)

    def _backup(self, current_version):
        (x, y, z) = current_version
        if x == 0:
            shutil.copy(self.path,
                        create_non_exising_path(self.path, "pre100bak"))

    def _create_rest_of_schema(self, tmp_dict):
        """
        Ensure all versions of the xml format can be parsed with this schema.

        tmp_dict["version"] can be used to create different schemas depending
        on the version.
        """
        tmp_dict["partial_schema"].add_child_tags([
            Tag("categories", SINGLE, None, [
                Tag("category", ANY, self._parse_category, [
                    Tag("name", SINGLE, parse_fn_store("tmp_name")),
                    Tag("color", SINGLE, parse_fn_store("tmp_color")),
                    Tag("font_color", OPTIONAL, parse_fn_store("tmp_font_color")),
                    Tag("parent", OPTIONAL, parse_fn_store("tmp_parent")),
                ])
            ]),
            Tag("events", SINGLE, None, [
                Tag("event", ANY, self._parse_event, [
                    Tag("start", SINGLE, parse_fn_store("tmp_start")),
                    Tag("end", SINGLE, parse_fn_store("tmp_end")),
                    Tag("text", SINGLE, parse_fn_store("tmp_text")),
                    Tag("fuzzy", OPTIONAL, parse_fn_store("tmp_fuzzy")),
                    Tag("locked", OPTIONAL, parse_fn_store("tmp_locked")),
                    Tag("ends_today", OPTIONAL, parse_fn_store("tmp_ends_today")),
                    Tag("category", OPTIONAL,
                        parse_fn_store("tmp_category")),
                    Tag("description", OPTIONAL,
                        parse_fn_store("tmp_description")),
                    Tag("alert", OPTIONAL,
                        parse_fn_store("tmp_alert")),
                    Tag("hyperlink", OPTIONAL,
                        parse_fn_store("tmp_hyperlink")),
                    Tag("icon", OPTIONAL,
                        parse_fn_store("tmp_icon")),
                ])
            ]),
            Tag("view", SINGLE, None, [
                Tag("displayed_period", OPTIONAL,
                    self._parse_displayed_period, [
                    Tag("start", SINGLE, parse_fn_store("tmp_start")),
                    Tag("end", SINGLE, parse_fn_store("tmp_end")),
                ]),
                Tag("hidden_categories", OPTIONAL,
                    self._parse_hidden_categories, [
                    Tag("name", ANY, self._parse_hidden_category),
                ]),
            ]),
        ])

    def _parse_category(self, text, tmp_dict):
        name = tmp_dict.pop("tmp_name")
        color = parse_color(tmp_dict.pop("tmp_color"))
        font_color = self._parse_optional_color(tmp_dict, "tmp_font_color")
        parent_name = tmp_dict.pop("tmp_parent", None)
        if parent_name:
            parent = tmp_dict["category_map"].get(parent_name, None)
            if parent is None:
                raise ParseException("Parent category '%s' not found." % parent_name)
        else:
            parent = None
        category = Category(name, color, font_color, True, parent=parent)
        old_category = self._get_category_by_name(category)
        if old_category is not None:
            category = old_category     
        if not tmp_dict["category_map"].has_key(name):
            tmp_dict["category_map"][name] = category
            self.save_category(category)

    def _parse_event(self, text, tmp_dict):
        start = self._parse_time(tmp_dict.pop("tmp_start"))
        end = self._parse_time(tmp_dict.pop("tmp_end"))
        text = tmp_dict.pop("tmp_text")
        fuzzy = self._parse_optional_bool(tmp_dict, "tmp_fuzzy")
        locked = self._parse_optional_bool(tmp_dict, "tmp_locked")
        ends_today = self._parse_optional_bool(tmp_dict, "tmp_ends_today")
        category_text = tmp_dict.pop("tmp_category", None)
        if category_text is None:
            category = None
        else:
            category = tmp_dict["category_map"].get(category_text, None)
            if category is None:
                raise ParseException("Category '%s' not found." % category_text)
        description = tmp_dict.pop("tmp_description", None)
        alert_string = tmp_dict.pop("tmp_alert", None)
        alert = self._parse_alert_string(alert_string)
        icon_text = tmp_dict.pop("tmp_icon", None)
        if icon_text is None:
            icon = None
        else:
            icon = parse_icon(icon_text)
        hyperlink = tmp_dict.pop("tmp_hyperlink", None)
        if self._is_container_event(text):
            cid, text = self._extract_container_id(text)
            event = Container(self.get_time_type(), start, end, text, category, cid=cid)
        elif self._is_subevent(text):
            cid, text = self._extract_subid(text)
            event = Subevent(self.get_time_type(), start, end, text, category, cid=cid)
        else:
            if self._text_starts_with_added_space(text):
                text = self._remove_added_space(text)
            event = Event(self.get_time_type(), start, end, text, category, fuzzy, locked, ends_today)
        event.set_data("description", description)
        event.set_data("icon", icon)
        event.set_data("alert", alert)
        event.set_data("hyperlink", hyperlink)
        self.save_event(event)

    def _text_starts_with_added_space(self, text):
        return text[0:2] in (" (", " [")
    
    def _remove_added_space(self, text):
        return text[1:]
        
    def alert_string(self, alert):
        time, text = alert
        time_string = self._time_string(time)
        return "%s;%s" % (time_string, text)

    def _parse_alert_string(self, alert_string):
        if alert_string is not None:
            try:
                time_string, alert_text = alert_string.split(";", 1)
                alert_time = self._parse_time(time_string)
                alert = (alert_time, alert_text)
            except:
                raise ParseException("Could not parse alert from '%s'." % alert_string)
        else:
            alert = None
        return alert

    def _is_container_event(self, text):
        return text.startswith("[")

    def _is_subevent(self, text):
        return text.startswith("(")

    def _extract_container_id(self, text):
        str_id, text = text.split("]", 1)
        try:
            str_id = str_id[1:]
            id = int(str_id)
        except:
            id = -1
        return id, text

    def _extract_subid(self, text):
        id, text = text.split(")", 1)
        try:
            id = int(id[1:])
        except:
            id = -1
        return id, text

    def _parse_optional_bool(self, tmp_dict, id):
        if tmp_dict.has_key(id):
            return tmp_dict.pop(id) == "True"
        else:
            return False

    def _parse_optional_color(self, tmp_dict, id):
        if tmp_dict.has_key(id):
            return parse_color(tmp_dict.pop(id))
        else:
            return (0, 0, 0)

    def _parse_displayed_period(self, text, tmp_dict):
        start = self._parse_time(tmp_dict.pop("tmp_start"))
        end = self._parse_time(tmp_dict.pop("tmp_end"))
        self._set_displayed_period(TimePeriod(self.get_time_type(), start, end))

    def _parse_hidden_category(self, text, tmp_dict):
        category = tmp_dict["category_map"].get(text, None)
        if category is None:
            raise ParseException("Category '%s' not found." % text)
        tmp_dict["hidden_categories"].append(category)

    def _parse_hidden_categories(self, text, tmp_dict):
        self._set_hidden_categories(tmp_dict.pop("hidden_categories"))

    def _save(self):
        self._make_sure_subevets_are_saved_last()
        safe_write(self.path, ENCODING, self._write_xml_doc)

    def _make_sure_subevets_are_saved_last(self):
        subevents = [event for event in self.events if event.is_subevent()]
        events = [event for event in self.events if not event.is_subevent()]
        events.extend(subevents)
        self.events = events

    def _write_xml_doc(self, file):
        file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        self._write_timeline(file)

    def _write_timeline(self, file):
        write_simple_tag(file, "version", get_version(), INDENT1)
        self._write_categories(file)
        self._write_events(file)
        self._write_view(file)
    _write_timeline = wrap_in_tag(_write_timeline, "timeline")

    def _write_categories(self, file):
        def write_with_parent(categories, parent):
            for cat in categories:
                if cat.parent == parent:
                    self._write_category(file, cat)
                    write_with_parent(categories, cat)
        write_with_parent(self.get_categories(), None)
    _write_categories = wrap_in_tag(_write_categories, "categories", INDENT1)

    def _write_category(self, file, cat):
        write_simple_tag(file, "name", cat.name, INDENT3)
        write_simple_tag(file, "color", color_string(cat.color), INDENT3)
        write_simple_tag(file, "font_color", color_string(cat.font_color), INDENT3)
        if cat.parent:
            write_simple_tag(file, "parent", cat.parent.name, INDENT3)
    _write_category = wrap_in_tag(_write_category, "category", INDENT2)

    def _write_events(self, file):
        for evt in self.get_all_events():
            self._write_event(file, evt)
    _write_events = wrap_in_tag(_write_events, "events", INDENT1)

    def _write_event(self, file, evt):
        write_simple_tag(file, "start",
                         self._time_string(evt.time_period.start_time), INDENT3)
        write_simple_tag(file, "end",
                         self._time_string(evt.time_period.end_time), INDENT3)
        if evt.is_container():
            write_simple_tag(file, "text", "[%d]%s " % (evt.cid(), evt.text), INDENT3)
        elif evt.is_subevent():
            write_simple_tag(file, "text", "(%d)%s " % (evt.cid(), evt.text), INDENT3)
        else:
            text = evt.text
            if self._text_starts_with_container_tag(evt.text):
                text = self._add_leading_space_to_text(evt.text)
            write_simple_tag(file, "text", text, INDENT3)
        write_simple_tag(file, "fuzzy", "%s" % evt.fuzzy, INDENT3)
        write_simple_tag(file, "locked", "%s" % evt.locked, INDENT3)
        write_simple_tag(file, "ends_today", "%s" % evt.ends_today, INDENT3)
        if evt.category is not None:
            write_simple_tag(file, "category", evt.category.name, INDENT3)
        if evt.get_data("description") is not None:
            write_simple_tag(file, "description", evt.get_data("description"),
                             INDENT3)
        alert = evt.get_data("alert")
        if alert is not None:
            write_simple_tag(file, "alert", self.alert_string(alert),
                             INDENT3)
        hyperlink = evt.get_data("hyperlink")
        if hyperlink is not None:
            write_simple_tag(file, "hyperlink", hyperlink, INDENT3)
        if evt.get_data("icon") is not None:
            icon_text = icon_string(evt.get_data("icon"))
            write_simple_tag(file, "icon", icon_text, INDENT3)
    _write_event = wrap_in_tag(_write_event, "event", INDENT2)

    def _text_starts_with_container_tag(self, text):
        return text[0] in ('(', '[')

    def _add_leading_space_to_text(self, text):
        return " %s" % text
    
    def _write_view(self, file):
        if self._get_displayed_period() is not None:
            self._write_displayed_period(file)
        self._write_hidden_categories(file)
    _write_view = wrap_in_tag(_write_view, "view", INDENT1)

    def _write_displayed_period(self, file):
        period = self._get_displayed_period()
        write_simple_tag(file, "start",
                         self._time_string(period.start_time), INDENT3)
        write_simple_tag(file, "end",
                         self._time_string(period.end_time), INDENT3)
    _write_displayed_period = wrap_in_tag(_write_displayed_period,
                                          "displayed_period", INDENT2)

    def _write_hidden_categories(self, file):
        for cat in self._get_hidden_categories():
            write_simple_tag(file, "name", cat.name, INDENT3)
    _write_hidden_categories = wrap_in_tag(_write_hidden_categories,
                                           "hidden_categories", INDENT2)


def write_simple_tag(file, name, content, indent=""):
    file.write(indent)
    file.write("<")
    file.write(name)
    file.write(">")
    file.write(xmlescape(content))
    file.write("</")
    file.write(name)
    file.write(">\n")


def parse_bool(bool_string):
    """
    Expected format 'True' or 'False'.

    Return True or False.
    """
    if bool_string == "True":
        return True
    elif bool_string == "False":
        return False
    else:
        raise ParseException("Unknown boolean '%s'" % bool_string)


def color_string(color):
    return "%i,%i,%i" % color


def parse_color(color_string):
    """
    Expected format 'r,g,b'.

    Return a tuple (r, g, b).
    """
    def verify_255_number(num):
        if num < 0 or num > 255:
            raise ParseException("Color number not in range [0, 255], "
                                 "color string = '%s'" % color_string)
    match = re.search(r"^(\d+),(\d+),(\d+)$", color_string)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        verify_255_number(r)
        verify_255_number(g)
        verify_255_number(b)
        return (r, g, b)
    else:
        raise ParseException("Color not on correct format, color string = '%s'"
                             % color_string)

def icon_string(bitmap):
    output = StringIO.StringIO()
    image = wx.ImageFromBitmap(bitmap)
    image.SaveStream(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())


def parse_icon(string):
    """
    Expected format: base64 encoded png image.

    Return a wx.Bitmap.
    """
    try:
        input = StringIO.StringIO(base64.b64decode(string))
        image = wx.ImageFromStream(input, wx.BITMAP_TYPE_PNG)
        return image.ConvertToBitmap()
    except:
        raise ParseException("Could not parse icon from '%s'." % string)
