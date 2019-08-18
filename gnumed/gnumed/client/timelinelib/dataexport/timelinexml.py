# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
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


from xml.sax.saxutils import escape as xmlescape
import base64
import io

import wx

from timelinelib.db.utils import safe_write
from timelinelib.meta.version import get_full_version


ENCODING = "utf-8"
INDENT1 = "  "
INDENT2 = "    "
INDENT3 = "      "


def export_db_to_timeline_xml(db, path):
    Exporter(db).export(path)


def wrap_in_tag(func, name, indent=""):
    def wrapper(*args, **kwargs):
        dbfile = args[1]  # 1st argument is self, 2nd argument is dbfile
        dbfile.write(indent)
        dbfile.write("<")
        dbfile.write(name)
        dbfile.write(">\n")
        func(*args, **kwargs)
        dbfile.write(indent)
        dbfile.write("</")
        dbfile.write(name)
        dbfile.write(">\n")
    return wrapper


class Exporter(object):

    def __init__(self, db):
        self.db = db

    def export(self, path):
        safe_write(path, ENCODING, self._write_xml_doc)

    def _time_string(self, time):
        return self.db.get_time_type().time_string(time)

    def _write_xml_doc(self, xmlfile):
        xmlfile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        self._write_timeline(xmlfile)

    def _write_timeline(self, xmlfile):
        write_simple_tag(xmlfile, "version", get_full_version(), INDENT1)
        write_simple_tag(xmlfile, "timetype", self.db.get_time_type().get_name(), INDENT1)
        if len(self.db.get_all_eras()) > 0:
            self._write_eras(xmlfile)
        self._write_categories(xmlfile)
        self._write_events(xmlfile)
        self._write_view(xmlfile)
        self._write_now_value(xmlfile)
    _write_timeline = wrap_in_tag(_write_timeline, "timeline")

    def _write_categories(self, xmlfile):
        def write_with_parent(categories, parent):
            for cat in categories:
                if cat._get_parent() == parent:
                    self._write_category(xmlfile, cat)
                    write_with_parent(categories, cat)
        write_with_parent(self.db.get_categories(), None)
    _write_categories = wrap_in_tag(_write_categories, "categories", INDENT1)

    def _write_category(self, xmlfile, cat):
        write_simple_tag(xmlfile, "name", cat.get_name(), INDENT3)
        write_simple_tag(xmlfile, "color", color_string(cat.get_color()), INDENT3)
        write_simple_tag(xmlfile, "progress_color", color_string(cat.get_progress_color()), INDENT3)
        write_simple_tag(xmlfile, "done_color", color_string(cat.get_done_color()), INDENT3)
        write_simple_tag(xmlfile, "font_color", color_string(cat.get_font_color()), INDENT3)
        if cat._get_parent():
            write_simple_tag(xmlfile, "parent", cat._get_parent().get_name(), INDENT3)
    _write_category = wrap_in_tag(_write_category, "category", INDENT2)

    def _write_events(self, xmlfile):
        all_events = self.db.get_all_events()
        containers = [event for event in all_events if event.is_container()]
        rest = [event for event in all_events if not event.is_container()]
        for evt in containers + rest:
            self._write_event(xmlfile, evt)
    _write_events = wrap_in_tag(_write_events, "events", INDENT1)

    def _write_event(self, xmlfile, evt):
        write_simple_tag(xmlfile, "start",
                         self._time_string(evt.get_time_period().start_time), INDENT3)
        write_simple_tag(xmlfile, "end",
                         self._time_string(evt.get_time_period().end_time), INDENT3)
        if evt.is_container():
            write_simple_tag(xmlfile, "text", "[%d]%s" % (evt.id, evt.get_text()), INDENT3)
        elif evt.is_subevent():
            write_simple_tag(xmlfile, "text", "(%d)%s" % (evt.container.id, evt.get_text()), INDENT3)
        else:
            text = evt.get_text()
            if self._text_starts_with_container_tag(evt.get_text()):
                text = self._add_leading_space_to_text(evt.get_text())
            write_simple_tag(xmlfile, "text", text, INDENT3)
        if evt.get_data("progress") is not None:
            write_simple_tag(xmlfile, "progress", "%s" % evt.get_data("progress"), INDENT3)
        write_simple_tag(xmlfile, "fuzzy", "%s" % evt.get_fuzzy(), INDENT3)
        write_simple_tag(xmlfile, "locked", "%s" % evt.get_locked(), INDENT3)
        write_simple_tag(xmlfile, "ends_today", "%s" % evt.get_ends_today(), INDENT3)
        if evt.get_category() is not None:
            write_simple_tag(xmlfile, "category", evt.get_category().get_name(), INDENT3)
        if evt.get_data("description") is not None:
            write_simple_tag(xmlfile, "description", evt.get_data("description"), INDENT3)
        alert = evt.get_data("alert")
        if alert is not None:
            write_simple_tag(xmlfile, "alert", alert_string(self.db.get_time_type(), alert),
                             INDENT3)
        hyperlink = evt.get_data("hyperlink")
        if hyperlink is not None:
            write_simple_tag(xmlfile, "hyperlink", hyperlink, INDENT3)
        if evt.get_data("icon") is not None:
            icon_text = icon_string(evt.get_data("icon"))
            write_simple_tag(xmlfile, "icon", icon_text, INDENT3)
        default_color = evt.get_data("default_color")
        if default_color is not None:
            write_simple_tag(xmlfile, "default_color", color_string(default_color), INDENT3)
        if evt.is_milestone():
            write_simple_tag(xmlfile, "milestone", "True", INDENT3)
    _write_event = wrap_in_tag(_write_event, "event", INDENT2)

    def _write_eras(self, xmlfile):
        for era in self.db.get_all_eras():
            self._write_era(xmlfile, era)
    _write_eras = wrap_in_tag(_write_eras, "eras", INDENT1)

    def _write_era(self, xmlfile, era):
        write_simple_tag(xmlfile, "name", era.get_name(), INDENT3)
        write_simple_tag(xmlfile, "start", self._time_string(era.get_time_period().start_time), INDENT3)
        write_simple_tag(xmlfile, "end", self._time_string(era.get_time_period().end_time), INDENT3)
        write_simple_tag(xmlfile, "color", color_string(era.get_color()), INDENT3)
        write_simple_tag(xmlfile, "ends_today", "%s" % era.ends_today(), INDENT3)
    _write_era = wrap_in_tag(_write_era, "era", INDENT2)

    def _text_starts_with_container_tag(self, text):
        if len(text) > 0:
            return text[0] in ('(', '[')
        else:
            return False

    def _add_leading_space_to_text(self, text):
        return " %s" % text

    def _write_view(self, xmlfile):
        if self.db.get_displayed_period() is not None:
            self._write_displayed_period(xmlfile)
        self._write_hidden_categories(xmlfile)
    _write_view = wrap_in_tag(_write_view, "view", INDENT1)


    def _write_displayed_period(self, xmlfile):
        period = self.db.get_displayed_period()
        write_simple_tag(xmlfile, "start",
                         self._time_string(period.start_time), INDENT3)
        write_simple_tag(xmlfile, "end",
                         self._time_string(period.end_time), INDENT3)
    _write_displayed_period = wrap_in_tag(_write_displayed_period,
                                          "displayed_period", INDENT2)

    def _write_hidden_categories(self, xmlfile):
        for cat in self.db.get_hidden_categories():
            write_simple_tag(xmlfile, "name", cat.get_name(), INDENT3)
    _write_hidden_categories = wrap_in_tag(_write_hidden_categories,
                                           "hidden_categories", INDENT2)

    def _write_now_value(self, xmlfile):
        if self.db.get_time_type().supports_saved_now():
            time = self.db.get_time_type().time_string(self.db.time_type.now())
            write_simple_tag(xmlfile, "now", time, INDENT1)


def write_simple_tag(xmlfile, name, content, indent=""):
    xmlfile.write(indent)
    xmlfile.write("<")
    xmlfile.write(name)
    xmlfile.write(">")
    xmlfile.write(xmlescape(content))
    xmlfile.write("</")
    xmlfile.write(name)
    xmlfile.write(">\n")


def color_string(color):
    return "%i,%i,%i" % color[:3]


def icon_string(bitmap):
    output = io.StringIO()
    image = wx.ImageFromBitmap(bitmap)
    image.SaveStream(output, wx.BITMAP_TYPE_PNG)
    return base64.b64encode(output.getvalue())


def alert_string(time_type, alert):
    time, text = alert
    time_string = time_type.time_string(time)
    return "%s;%s" % (time_string, text)
