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


import wx

from timelinelib.general.observer import Observable
from timelinelib.wxgui.components.font import Font


class Appearance(Observable):

    def __init__(self):
        Observable.__init__(self)
        self._build_property("legend_visible", True)
        self._build_property("balloons_visible", True)
        self._build_property("hide_events_done", False)
        self._build_property("minor_strip_divider_line_colour", (200, 200, 200))
        self._build_property("major_strip_divider_line_colour", (200, 200, 200))
        self._build_property("now_line_colour", (200, 0, 0))
        self._build_property("weekend_colour", (255, 255, 255))
        self._build_property("bg_colour", (255, 255, 255))
        self._build_property("colorize_weekends", False)
        self._build_property("draw_period_events_to_right", False)
        self._build_property("text_below_icon", False)
        self._build_property("minor_strip_font", Font(8).serialize())
        self._build_property("major_strip_font", Font(12, weight=wx.FONTWEIGHT_BOLD).serialize())
        self._build_property("legend_font", Font(8).serialize())
        self._build_property("balloon_font", Font(8).serialize())
        self._build_property("center_event_texts", False)
        self._build_property("never_show_period_events_as_point_events", False)
        self._build_property("week_start", "monday")
        self._build_property("use_inertial_scrolling", False)
        self._build_property("fuzzy_icon", "fuzzy.png")
        self._build_property("locked_icon", "locked.png")
        self._build_property("hyperlink_icon", "hyperlink.png")
        self._build_property("vertical_space_between_events", 5)
        self._build_property("skip_s_in_decade_text", False)
        self._build_property("display_checkmark_on_events_done", False)
        self._build_property("never_use_time", False)
        self._build_property("legend_pos", 0)

    def _build_property(self, name, initial_value):

        def getter():
            return getattr(self, "_%s" % name)

        def setter(new_value):
            old_value = getter()
            if new_value != old_value:
                setattr(self, "_%s" % name, new_value)
                self._notify()

        setattr(self, "get_%s" % name, getter)
        setattr(self, "set_%s" % name, setter)
        setattr(self, "_%s" % name, initial_value)
