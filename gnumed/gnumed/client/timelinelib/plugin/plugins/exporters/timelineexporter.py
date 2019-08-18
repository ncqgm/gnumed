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


from __future__ import with_statement


import os.path

import wx

from timelinelib.plugin.factory import EXPORTER
from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.wxgui.dialogs.export.controller import CSV_FILE
from timelinelib.wxgui.dialogs.export.view import ExportDialog
from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import WildcardHelper


class TimelineExporter(PluginBase):

    def service(self):
        return EXPORTER

    def display_name(self):
        return _("Export Timeline to File...")

    def wxid(self):
        from timelinelib.wxgui.frames.mainframe.guicreator import ID_EXPORT
        return ID_EXPORT

    def run(self, main_frame):
        self.timeline = main_frame.timeline
        dlg = ExportDialog(main_frame)
        if dlg.ShowModal() == wx.ID_OK:
            self.export_timeline(dlg, main_frame)
        dlg.Destroy()

    def export_timeline(self, dlg, main_frame):
        path, _ = get_path(main_frame)
        if path is not None and overwrite_existing_path(main_frame, path):
            if dlg.GetExportType() == CSV_FILE:
                CsvExporter(self.timeline, path, dlg).export()


class CsvExporter(object):

    def __init__(self, timeline, path, dlg):
        self.path = path
        self.timeline = timeline
        self.text_encoding = dlg.GetTextEncoding()
        self.encoding_error_strategy = dlg.GetTextEncodingErrorStrategy()
        self.export_events = dlg.GetExportEvents()
        self.export_categories = dlg.GetExportCategories()
        self.event_fields = dlg.GetEventFields()
        self.category_fields = dlg.GetCategoryFields()

    def export(self):
        with open(self.path, "wb") as f:
            self._write_events(f, self.event_fields)
            self._write_categories(f, self.category_fields)

    def _write_events(self, f, event_fields):
        if self.export_events:
            self._write_label(f, _("Events"))
            self._write_heading(f, event_fields)
            self._write_events_fields(f, event_fields)

    def _write_categories(self, f, category_fields):
        if self.export_categories:
            self._write_label(f, _("Categories"))
            self._write_heading(f, category_fields)
            self._write_categories_fields(f, category_fields)

    def _write_label(self, f, text):
        self._write_encoded_text(f, text)
        self._write(f, "\n")

    def _write_heading(self, f, fields):
        for field in fields:
            self._write_encoded_text(f, field)
        self._write(f, "\n")

    def _write_events_fields(self, f, event_fields):
        for event in self.timeline.get_all_events():
            self._write_event(f, event, event_fields)
        self._write(f, "\n")

    def _write_categories_fields(self, f, category_fields):
        for category in self.timeline.get_categories():
            self._write_category(f, category, category_fields)

    def _write_event(self, f, event, event_fields):
        if _("Text") in event_fields:
            self._write_encoded_text(f, event.get_text())
        if _("Description") in event_fields:
            self._write_encoded_text(f, self._get_event_description(event))
        if _("Start") in event_fields:
            self._write_time_value(f, event.get_time_period().start_time)
        if _("End") in event_fields:
            self._write_time_value(f, event.get_time_period().end_time)
        if _("Category") in event_fields:
            self._write_encoded_text(f, self._get_event_category(event))
        if _("Fuzzy") in event_fields:
            self._write_boolean_value(f, event.get_fuzzy())
        if _("Locked") in event_fields:
            self._write_boolean_value(f, event.get_locked())
        if _("Ends Today") in event_fields:
            self._write_boolean_value(f, event.get_ends_today())
        if _("Hyperlink") in event_fields:
            self._write(f, "%s;" % event.get_hyperlink())
        if _("Progress") in event_fields:
            self._write(f, "%s;" % event.get_progress())
        if _("Progress Color") in event_fields:
            self._write_color_value(f, event.get_progress_color())
        if _("Done Color") in event_fields:
            self._write_color_value(f, event.get_done_color())
        if _("Alert") in event_fields:
            self._write(f, "%s;" % self._get_alert_string(event.get_alert()))
        if _("Is Container") in event_fields:
            self._write_boolean_value(f, event.is_container())
        if _("Is Subevent") in event_fields:
            self._write_boolean_value(f, event.is_subevent())
        self._write(f, "\n")

    def _write_category(self, f, category, category_fields):
        if _("Name") in category_fields:
            self._write_encoded_text(f, category.get_name())
        if _("Color") in category_fields:
            self._write_color_value(f, category.get_color())
        if _("Progress Color") in category_fields:
            self._write_color_value(f, category.get_progress_color())
        if _("Done Color") in category_fields:
            self._write_color_value(f, category.get_done_color())
        if _("Parent") in category_fields:
            self._write_encoded_text(f, self._get_parent(category))
        self._write(f, "\n")

    def _get_event_description(self, event):
        if event.get_description() is not None:
            return event.get_description()
        else:
            return ""

    def _get_event_category(self, event):
        if event.get_category() is not None:
            return event.get_category().get_name()
        else:
            return ""

    def _get_parent(self, category):
        if category._get_parent():
            return category._get_parent().get_name()

    def _get_category_parent(self, cat):
        if cat._get_parent() is not None:
            return cat._get_parent().get_name()
        else:
            return ""

    def _get_time_string(self, time_value):
        return self.timeline.get_time_type().time_string(time_value)

    def _get_alert_string(self, alert):
        if alert:
            time, text = alert
            return "%s %s" % (self._get_time_string(time), text)
        else:
            return ""

    def _write_encoded_text(self, f, text):
        if text is not None:
            text = text.replace('"', '""')
        self._write(f, "\"%s\";" % text)

    def _write_time_value(self, f, time_value):
        self._write(f, "%s;" % self.timeline.get_time_type().time_string(time_value))

    def _write_color_value(self, f, color):
        self._write(f, "(%d, %d, %d);" % color)

    def _write_boolean_value(self, f, value):
        self._write(f, "%s;" % value)

    def _write(self, f, text):
        f.write(text.encode(self.text_encoding, self.encoding_error_strategy))


def get_path(main_frame):
    image_type = None
    path = None
    file_info = _("export files")
    file_types = [("csv", "")]
    images_wildcard_helper = WildcardHelper(file_info, file_types)
    wildcard = images_wildcard_helper.wildcard_string()
    dialog = wx.FileDialog(main_frame, message=_("Export"), wildcard=wildcard, style=wx.FD_SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = images_wildcard_helper.get_path(dialog)
        image_type = images_wildcard_helper.get_extension_data(path)
    dialog.Destroy()
    return path, image_type


def overwrite_existing_path(main_frame, path):
    if os.path.exists(path):
        overwrite_question = _("File '%s' exists. Overwrite?") % path
        return _ask_question(overwrite_question, main_frame) == wx.YES
    return True
