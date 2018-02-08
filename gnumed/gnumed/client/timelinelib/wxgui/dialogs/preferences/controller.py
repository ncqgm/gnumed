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


import os

import wx

from timelinelib.wxgui.components.font import deserialize_font
from timelinelib.wxgui.framework import Controller
from timelinelib.config.paths import EVENT_ICONS_DIR


class PreferencesDialogController(Controller):

    def on_init(self, config, experimental_features):
        self.config = config
        self.experimental_features = experimental_features
        self.weeks_map = ((0, "monday"), (1, "sunday"))
        self._set_initial_values()

    def on_close(self):
        self.config.minor_strip_divider_line_colour = str(self.view.GetMinorStripColor())
        self.config.major_strip_divider_line_colour = str(self.view.GetMajorStripColor())
        self.config.now_line_colour = str(self.view.GetNowLineColor())
        self.config.weekend_colour = str(self.view.GetWeekendColor())
        self.config.bg_color = str(self.view.GetBgColor())
        self.config.legend_pos = self.view.GetLegendPos()

    def on_open_recent_change(self, event):
        self.config.open_recent_at_startup = event.IsChecked()

    def on_inertial_scrolling_changed(self, event):
        self.config.use_inertial_scrolling = event.IsChecked()

    def on_never_period_point_changed(self, event):
        self.config.never_show_period_events_as_point_events = event.IsChecked()

    def on_center_text_changed(self, event):
        self.config.center_event_texts = event.IsChecked()

    def on_display_checkmark_on_events_done_changed(self, event):
        self.config.display_checkmark_on_events_done = event.IsChecked()

    def on_week_start_changed(self, event):
        self.config.set_week_start(self._index_week(event.GetSelection()))

    def on_date_formatter_click(self, event):
        self.view.ShowSelectDateFormatDialog(self.config)
        self.view.SetCurrentDateFormat("%s: %s" % (_("Current"), self.config.date_format))

    def on_uncheck_time_for_new_events(self, event):
        self.config.uncheck_time_for_new_events = event.IsChecked()

    def on_text_below_icon(self, event):
        self.config.text_below_icon = event.IsChecked()

    def on_tab_order_click(self, event):
        self.view.ShowSelectTabOrderDialog(self.config)

    def on_balloon_click(self, evt):
        font = deserialize_font(self.config.balloon_font)
        if self.view.ShowEditFontDialog(font):
            self.config.balloon_font = font.serialize()
            self.view.SetBalloonFont(font)

    def on_major_strip_click(self, event):
        font = deserialize_font(self.config.major_strip_font)
        if self.view.ShowEditFontDialog(font):
            self.config.major_strip_font = font.serialize()
            self.view.SetMajorStripFont(font)

    def on_minor_strip_click(self, event):
        font = deserialize_font(self.config.minor_strip_font)
        if self.view.ShowEditFontDialog(font):
            self.config.minor_strip_font = font.serialize()
            self.view.SetMinorStripFont(font)

    def on_legend_click(self, event):
        font = deserialize_font(self.config.legend_font)
        if self.view.ShowEditFontDialog(font):
            self.config.legend_font = font.serialize()
            self.view.SetLegendFont(font)

    def on_experimental_changed(self, event):
        self.experimental_features.set_active_state_on_feature_by_name(
            event.GetEventObject().GetLabel(), event.IsChecked())
        self.config.experimental_features = str(self.experimental_features)

    def on_fuzzy_icon_changed(self, event):
        self.config.fuzzy_icon = event.GetString()
        self.view.DisplayIcons()

    def on_locked_icon_changed(self, event):
        self.config.locked_icon = event.GetString()
        self.view.DisplayIcons()

    def on_hyperlink_icon_changed(self, event):
        self.config.hyperlink_icon = event.GetString()
        self.view.DisplayIcons()

    def on_vertical_space_between_events_click(self, event):
        self.config.vertical_space_between_events = self.view.GetVerticalSpaceBetweenEvents()

    def on_colorize_weekends(self, event):
        self.config.colorize_weekends = self.view.GetColorizeWeekends()

    def on_skip_s_in_decade_text(self, event):
        self.config.skip_s_in_decade_text = self.view.GetSkipSInDecadeText()

    def on_never_use_time_change(self, event):
        self.config.never_use_time = self.view.GetNeverUseTime()

    def _set_initial_values(self):
        self.view.SetOpenRecentCheckboxValue(self.config.open_recent_at_startup)
        self.view.SetInertialScrollingCheckboxValue(self.config.use_inertial_scrolling)
        self.view.SetNeverPeriodPointCheckboxValue(self.config.never_show_period_events_as_point_events)
        self.view.SetCenterTextCheckboxValue(self.config.center_event_texts)
        self.view.SetWeekStartSelection(self._week_index(self.config.get_week_start()))
        self.view.AddExperimentalFeatures(self.experimental_features.get_all_features())
        self.view.SetUncheckTimeForNewEventsCheckboxValue(self.config.uncheck_time_for_new_events)
        self.view.SetTextBelowIconCheckboxValue(self.config.text_below_icon)
        self.view.SetMinorStripColor(wx.Colour(*self.config.minor_strip_divider_line_colour))
        self.view.SetMajorStripColor(wx.Colour(*self.config.major_strip_divider_line_colour))
        self.view.SetNowLineColor(wx.Colour(*self.config.now_line_colour))
        self.view.SetWeekendColor(wx.Colour(*self.config.weekend_colour))
        self.view.SetBgColor(wx.Colour(*self.config.bg_colour))
        choices = [f for f in os.listdir(EVENT_ICONS_DIR) if f.endswith(".png")]
        self.view.SetIconsChoices(choices)
        self.view.SetFuzzyIcon(self.config.fuzzy_icon)
        self.view.SetLockedIcon(self.config.locked_icon)
        self.view.SetHyperlinkIcon(self.config.hyperlink_icon)
        self.view.SetCurrentDateFormat("%s: %s" % (_("Current"), self.config.date_format))
        self.view.DisplayIcons()
        self.view.SetVerticalSpaceBetweenEvents(self.config.vertical_space_between_events)
        self.view.SetColorizeWeekends(self.config.colorize_weekends)
        self.view.SetSkipSInDecadeText(self.config.skip_s_in_decade_text)
        self.view.SetDisplayCheckmarkOnEventsDone(self.config.display_checkmark_on_events_done)
        self.view.SetNeverUseTime(self.config.never_use_time)
        self.view.SetMajorStripFont(deserialize_font(self.config.major_strip_font))
        self.view.SetMinorStripFont(deserialize_font(self.config.minor_strip_font))
        self.view.SetLegendFont(deserialize_font(self.config.legend_font))
        self.view.SetBalloonFont(deserialize_font(self.config.balloon_font))
        self.view.SetLegendPos(self.config.legend_pos)

    def _week_index(self, week):
        for (i, w) in self.weeks_map:
            if w == week:
                return i
        raise ValueError("Unknown week '%s'." % week)

    def _index_week(self, index):
        for (i, w) in self.weeks_map:
            if i == index:
                return w
        raise ValueError("Unknown week index '%s'." % index)
