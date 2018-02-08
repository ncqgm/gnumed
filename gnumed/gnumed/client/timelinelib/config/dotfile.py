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


"""
Handle application configuration.

This module is global and can be used by all modules. Before accessing
configurations, the read function should be called. To save the current
configuration back to file, call the write method.
"""


from ConfigParser import ConfigParser
from ConfigParser import DEFAULTSECT
import os.path
import sys

import wx

from timelinelib.calendar.gregorian.dateformatter import GregorianDateFormatter
from timelinelib.config.dateformatparser import DateFormatParser
from timelinelib.general.observer import Observable
from timelinelib.wxgui.components.font import Font
from timelinelib.wxgui.utils import display_information_message


# Name used in ConfigParser
SELECTED_EVENT_BOX_DRAWER = "selected_event_box_drawer"
WINDOW_WIDTH = "window_width"
WINDOW_HEIGHT = "window_height"
WINDOW_XPOS = "window xpos"
WINDOW_YPOS = "window ypos"
RECENT_FILES = "recent_files"
WEEK_START = "week_start"
DATE_FORMAT = "date_format"
DEFAULTS = {
    SELECTED_EVENT_BOX_DRAWER: "Default Event box drawer",
    WINDOW_WIDTH: "900",
    WINDOW_HEIGHT: "500",
    WINDOW_XPOS: "-1",
    WINDOW_YPOS: "-1",
    RECENT_FILES: "",
    WEEK_START: "monday",
    DATE_FORMAT: "yyyy-mm-dd",
}
# Some settings
MAX_NBR_OF_RECENT_FILES_SAVED = 5
ENCODING = "utf-8"


def read_config(path):
    config = Config(path)
    config.read()
    return config


class Config(Observable):

    """
    Provide read and write access to application configuration settings.

    Built as a wrapper around ConfigParser: Properties exist to read and write
    values but ConfigParser does the actual reading and writing of the
    configuration file.
    """

    def __init__(self, path):
        Observable.__init__(self)
        self.path = path
        self.config_parser = ConfigParser(DEFAULTS)

    def read(self):
        """Read settings from file specified in constructor."""
        if self.path:
            self.config_parser.read(self.path)

    def write(self):
        """
        Write settings to file specified in constructor and raise IOError if
        failed.
        """
        f = open(self.path, "w")
        try:
            self.config_parser.write(f)
        finally:
            f.close()

    def get_selected_event_box_drawer(self):
        return self.config_parser.get(DEFAULTSECT, SELECTED_EVENT_BOX_DRAWER).decode("utf-8")

    def set_selected_event_box_drawer(self, selected):
        self.config_parser.set(DEFAULTSECT, SELECTED_EVENT_BOX_DRAWER, str(selected.encode("utf-8")))

    def get_window_size(self):
        return (self.config_parser.getint(DEFAULTSECT, WINDOW_WIDTH),
                self.config_parser.getint(DEFAULTSECT, WINDOW_HEIGHT))

    def set_window_size(self, size):
        width, height = size
        self.config_parser.set(DEFAULTSECT, WINDOW_WIDTH, str(width))
        self.config_parser.set(DEFAULTSECT, WINDOW_HEIGHT, str(height))

    def get_window_pos(self):
        width, _ = self.get_window_size()
        # Make sure that some area of the window is visible on the screen
        # Some part of the titlebar must be visible
        xpos = max(-width + 100,
                   self.config_parser.getint(DEFAULTSECT, WINDOW_XPOS))
        # Titlebar must not be above the upper screen border
        ypos = max(0, self.config_parser.getint(DEFAULTSECT, WINDOW_YPOS))
        return (xpos, ypos)

    def set_window_pos(self, pos):
        xpos, ypos = pos
        self.config_parser.set(DEFAULTSECT, WINDOW_XPOS, str(xpos))
        self.config_parser.set(DEFAULTSECT, WINDOW_YPOS, str(ypos))

    def get_recently_opened(self):
        ro = self.config_parser.get(DEFAULTSECT, RECENT_FILES).decode(ENCODING).split(",")
        # Filter out empty elements: "".split(",") will return [""] but we want
        # the empty list
        ro_filtered = [x for x in ro if x]
        return ro_filtered

    def has_recently_opened_files(self):
        if not self.open_recent_at_startup:
            return False
        else:
            return len(self.get_recently_opened()) > 0

    def get_latest_recently_opened_file(self):
        return self.get_recently_opened()[0]

    def append_recently_opened(self, path):
        if path in [":tutorial:"]:
            # Special timelines should not be saved
            return
        if isinstance(path, str):
            # This path might have come from the command line so we need to convert
            # it to unicode
            path = path.decode(sys.getfilesystemencoding())
        abs_path = os.path.abspath(path)
        current = self.get_recently_opened()
        # Just keep one entry of the same path in the list
        if abs_path in current:
            current.remove(abs_path)
        current.insert(0, abs_path)
        self.config_parser.set(DEFAULTSECT, RECENT_FILES,
                               (",".join(current[:MAX_NBR_OF_RECENT_FILES_SAVED])).encode(ENCODING))

    def get_week_start(self):
        return self.config_parser.get(DEFAULTSECT, WEEK_START)

    def set_week_start(self, week_start):
        if week_start not in ["monday", "sunday"]:
            raise ValueError("Invalid week start.")
        self.config_parser.set(DEFAULTSECT, WEEK_START, week_start)
        self._notify()

    def get_shortcut_key(self, cfgid, default):
        try:
            return self.config_parser.get(DEFAULTSECT, cfgid)
        except:
            self.set_shortcut_key(cfgid, default)
            return default

    def set_shortcut_key(self, cfgid, value):
        self.config_parser.set(DEFAULTSECT, cfgid, value)

    def _string_to_tuple(self, tuple_string):
        return tuple([int(x.strip()) for x in tuple_string[1:-1].split(",")])

    def _tuple_to_string(self, tuple_data):
        return str(tuple_data)

    def get_date_formatter(self):
        parser = DateFormatParser().parse(self.get_date_format())
        date_formatter = GregorianDateFormatter()
        date_formatter.set_separators(*parser.get_separators())
        date_formatter.set_region_order(*parser.get_region_order())
        date_formatter.use_abbreviated_name_for_month(parser.use_abbreviated_month_names())
        return date_formatter

    def get_date_format(self):
        return self.config_parser.get(DEFAULTSECT, DATE_FORMAT)

    def set_date_format(self, date_format):
        self.config_parser.set(DEFAULTSECT, DATE_FORMAT, date_format)
        self._notify()
    date_format = property(get_date_format, set_date_format)

    def _toStr(self, value):
        try:
            return str(value)
        except UnicodeEncodeError:
            display_information_message(_("Warning"), _("The selected value contains invalid characters and can't be saved"))

    def _get(self, key):
        if key in BOOLEANS:
            return self._get_boolean(key)
        elif key in INTS:
            return self._get_int(key)
        elif key in COLOURS:
            return self._get_colour(key)
        elif key in FONTS:
            return self._get_font(key)
        else:
            return self.config_parser.get(DEFAULTSECT, key)

    def _get_int(self, key):
        value = self.config_parser.get(DEFAULTSECT, key)
        return int(value)

    def _get_boolean(self, key):
        return self.config_parser.getboolean(DEFAULTSECT, key)

    def _get_colour(self, key):
        return self._string_to_tuple(self.config_parser.get(DEFAULTSECT, key))

    def _get_font(self, key):
        return self.config_parser.get(DEFAULTSECT, key)

    def _set(self, key, value):
        if key in COLOURS:
            self._set_colour(key, value)
        elif key in FONTS:
            self._set_font(key, value)
        else:
            if self._toStr(value) is not None:
                self.config_parser.set(DEFAULTSECT, key, self._toStr(value))
                self._notify()

    def _set_colour(self, key, value):
        self.config_parser.set(DEFAULTSECT, key, self._tuple_to_string(value))

    def _set_font(self, key, value):
        if self._toStr(value) is not None:
            self.config_parser.set(DEFAULTSECT, key, value)
            self._notify()


# To add a new boolean, integer, colour or string configuration item
# you only have to add that item to one of the dictionaries below.
BOOLEAN_CONFIGS = (
    {'name': 'show_toolbar', 'default': 'True'},
    {'name': 'show_sidebar', 'default': 'True'},
    {'name': 'show_legend', 'default': 'True'},
    {'name': 'window_maximized', 'default': 'False'},
    {'name': 'open_recent_at_startup', 'default': 'True'},
    {'name': 'balloon_on_hover', 'default': 'True'},
    {'name': 'use_inertial_scrolling', 'default': 'False'},
    {'name': 'never_show_period_events_as_point_events', 'default': 'False'},
    {'name': 'draw_point_events_to_right', 'default': 'False'},
    {'name': 'event_editor_show_period', 'default': 'False'},
    {'name': 'event_editor_show_time', 'default': 'False'},
    {'name': 'center_event_texts', 'default': 'False'},
    {'name': 'uncheck_time_for_new_events', 'default': 'False'},
    {'name': 'text_below_icon', 'default': 'False'},
    {'name': 'colorize_weekends', 'default': 'False'},
    {'name': 'skip_s_in_decade_text', 'default': 'False'},
    {'name': 'display_checkmark_on_events_done', 'default': 'False'},
    {'name': 'never_use_time', 'default': 'False'},
    {'name': 'hide_events_done', 'default': 'False'},
)
INT_CONFIGS = (
    {'name': 'sidebar_width', 'default': '200'},
    {'name': 'divider_line_slider_pos', 'default': '50'},
    {'name': 'vertical_space_between_events', 'default': '5'},
    {'name': 'legend_pos', 'default': '0'},
)
STR_CONFIGS = (
    {'name': 'experimental_features', 'default': ''},
    {'name': 'event_editor_tab_order', 'default': '01234:'},
    {'name': 'fuzzy_icon', 'default': 'fuzzy.png'},
    {'name': 'locked_icon', 'default': 'locked.png'},
    {'name': 'hyperlink_icon', 'default': 'hyperlink.png'},
)
COLOUR_CONFIGS = (
    {'name': 'now_line_colour', 'default': '(200, 0, 0)'},
    {'name': 'weekend_colour', 'default': '(255, 255, 255)'},
    {'name': 'bg_colour', 'default': '(255, 255, 255)'},
    {'name': 'minor_strip_divider_line_colour', 'default': '(200, 200, 200)'},
    {'name': 'major_strip_divider_line_colour', 'default': '(200, 200, 200)'},
)
FONT_CONFIGS = (
    {'name': 'minor_strip_font', 'default': '10:74:90:90:False:Tahoma:33:(0, 0, 0, 255)'},
    {'name': 'major_strip_font', 'default': '10:74:90:90:False:Tahoma:33:(0, 0, 0, 255)'},
    {'name': 'legend_font', 'default': '10:74:90:90:False:Tahoma:33:(0, 0, 0, 255)'},
    {'name': 'balloon_font', 'default': '10:74:90:90:False:Tahoma:33:(0, 0, 0, 255)'},
)
BOOLEANS = [d['name'] for d in BOOLEAN_CONFIGS]
INTS = [d['name'] for d in INT_CONFIGS]
COLOURS = [d['name'] for d in COLOUR_CONFIGS]
FONTS = [d['name'] for d in FONT_CONFIGS]


def setatt(name):
    setattr(Config, name, property(lambda self: self._get(name),
                                   lambda self, value: self._set(name, str(value))))

# Create properties dynamically
for data in BOOLEAN_CONFIGS + INT_CONFIGS + STR_CONFIGS + COLOUR_CONFIGS + FONT_CONFIGS:
    setatt(data['name'])
    DEFAULTS[data['name']] = data['default']
