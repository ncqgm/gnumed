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

from timelinelib.features.experimental.experimentalfeatures import ExperimentalFeatures
from timelinelib.wxgui.components.font import edit_font_data
from timelinelib.wxgui.dialogs.eventeditortabselection.view import EventEditorTabSelectionDialog
from timelinelib.wxgui.dialogs.dateformat.view import DateFormatDialog
from timelinelib.wxgui.dialogs.preferences.controller import PreferencesDialogController
from timelinelib.wxgui.framework import Dialog
from timelinelib.config.paths import EVENT_ICONS_DIR


class PreferencesDialog(Dialog):

    """
    <BoxSizerVertical>
        <Notebook border="ALL" proportion="1" width="600">
            <Panel notebookLabel="$(general_text)">
                <BoxSizerVertical>
                    <FlexGridSizer columns="1" border="ALL">
                        <CheckBox
                            name="open_recent_checkbox"
                            event_EVT_CHECKBOX="on_open_recent_change"
                            label="$(open_recent_text)"
                        />
                        <CheckBox
                            name="inertial_scrolling_checkbox"
                            event_EVT_CHECKBOX="on_inertial_scrolling_changed"
                            label="$(inertial_scrolling_text)"
                        />
                        <CheckBox
                            name="never_period_point_checkbox"
                            event_EVT_CHECKBOX="on_never_period_point_changed"
                            label="$(never_period_point_text)"
                        />
                        <CheckBox
                            name="center_text_checkbox"
                            event_EVT_CHECKBOX="on_center_text_changed"
                            label="$(center_text_text)"
                        />
                        <CheckBox
                            name="display_checkmark_on_events_done_checkbox"
                            event_EVT_CHECKBOX="on_display_checkmark_on_events_done_changed"
                            label="$(display_checkmark_on_events_done_text)"
                        />
                        <CheckBox
                            name="uncheck_time_for_new_events"
                            event_EVT_CHECKBOX="on_uncheck_time_for_new_events"
                            label="$(uncheck_time_for_new_events_text)"
                        />
                        <CheckBox
                            name="text_below_icon"
                            event_EVT_CHECKBOX="on_text_below_icon"
                            label="$(text_below_icon_text)"
                        />
                        <CheckBox
                            name="filtered_listbox_export"
                            event_EVT_CHECKBOX="on_filtered_listbox_export"
                            label="$(text_filtered_listbox_export)"
                        />
                        <Button
                            name="select_tab_order"
                            event_EVT_BUTTON="on_tab_order_click"
                            label="$(tab_order_text)"
                            align="ALIGN_LEFT"
                        />
                        <BoxSizerHorizontal>
                            <StaticText
                                name="vertical_space_between_events_text"
                                label="$(vertical_space_between_events_text)"
                                align="ALIGN_CENTER_VERTICAL"
                            />
                            <SpinCtrl
                                name="vertical_space_between_events"
                                event_EVT_SPINCTRL="on_vertical_space_between_events_click"
                                align="ALIGN_LEFT"
                                width="50"
                            />
                        </BoxSizerHorizontal>
                        <RadioBox
                            name="legend_positions"
                            choices="$(legend_positions)"
                            label="$(legend_positions_text)"
                        />
                    </FlexGridSizer>
                </BoxSizerVertical>
            </Panel>
            <Panel notebookLabel="$(date_time_text)">
                <BoxSizerVertical>
                    <FlexGridSizer columns="2" border="ALL">
                        <StaticText
                            label="$(week_start_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Choice
                            name="week_start_choice"
                            event_EVT_CHOICE="on_week_start_changed"
                            choices="$(week_start_choices)"
                        />
                        <Button
                            name="select_date_formatter"
                            event_EVT_BUTTON="on_date_formatter_click"
                            label="$(date_formatter_text)"
                            align="ALIGN_LEFT"
                        />
                        <StaticText
                            name="current_date_format"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <CheckBox
                            name="skip_s_in_decade_text"
                            event_EVT_CHECKBOX="on_skip_s_in_decade_text"
                            label="$(skip_s_in_decade_text_text)"
                        />
                        <Spacer />
                        <CheckBox
                            name="never_use_time_checkbox"
                            event_EVT_CHECKBOX="on_never_use_time_change"
                            label="$(never_use_time_text)"
                        />
			<Spacer />
                        <CheckBox
                            name="use_second_checkbox"
                            event_EVT_CHECKBOX="on_use_second_change"
                            label="$(use_second_text)"
                        />
                        <Spacer />
                        <CheckBox
                            name="use_date_default_values_checkbox"
                            event_EVT_CHECKBOX="on_use_date_default_values"
                            label="$(use_date_default_values)"
                        />
                        <Spacer />
                        <StaticText
                            label="$(default_year)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <TextCtrl 
                            name="txt_default_year" 
                            fit_text="MMMM" 
                        />                        
                        <StaticText
                            label="$(default_month)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <TextCtrl 
                            name="txt_default_month" 
                            fit_text="MM" 
                        />                        
                        <StaticText
                            label="$(default_day)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <TextCtrl 
                            name="txt_default_day" 
                            fit_text="MM" 
                        />                      
                        <RadioBox
                            name="time_scale_positions"
                            choices="$(time_scale_positions)"
                            label="$(time_scale_positions_text)"
                        />
                    </FlexGridSizer>
                </BoxSizerVertical>
            </Panel>
            <Panel notebookLabel="$(fonts_text)">
                <BoxSizerVertical name="font_sizer">
                    <FlexGridSizer columns="3" border="ALL">
                        <StaticText
                            label="$(major_strip_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Button
                            name="select_major_strip"
                            event_EVT_BUTTON="on_major_strip_click"
                            label="$(edit_text)"
                        />
                        <StaticText
                            name="major_strip_font_sample"
                            label="Timeline"
                        />
                        <StaticText
                            label="$(minor_strip_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Button
                            name="select_minor_strip"
                            event_EVT_BUTTON="on_minor_strip_click"
                            label="$(edit_text)"
                        />
                        <StaticText
                            name="minor_strip_font_sample"
                            label="Timeline"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                       <StaticText
                            label="$(legends_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Button
                            name="select_legend"
                            event_EVT_BUTTON="on_legend_click"
                            label="$(edit_text)"
                        />
                        <StaticText
                            name="legend_font_sample"
                            label="Timeline"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <StaticText
                            label="$(balloon_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Button
                            name="select_balloon"
                            event_EVT_BUTTON="on_balloon_click"
                            label="$(edit_text)"
                        />
                        <StaticText
                            name="balloon_font_sample"
                            label="Timeline"
                        />
                    </FlexGridSizer>
                </BoxSizerVertical>
            </Panel>
            <Panel notebookLabel="$(colours_text)">
                <BoxSizerVertical>
                    <FlexGridSizer columns="2" border="ALL">
                        <StaticText
                            label="$(bg_colour_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <ColourSelect
                            name="bg_colorpicker"
                            align="ALIGN_CENTER_VERTICAL"
                            width="60"
                            height="30"
                        />
                        <StaticText
                            label="$(minor_strip_colour_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <ColourSelect
                            name="minor_strip_colorpicker"
                            align="ALIGN_CENTER_VERTICAL"
                            width="60"
                            height="30"
                        />
                        <StaticText
                            label="$(major_strip_colour_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <ColourSelect
                            name="major_strip_colorpicker"
                            align="ALIGN_CENTER_VERTICAL"
                            width="60"
                            height="30"
                        />
                        <StaticText
                            label="$(now_line_colour_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <BoxSizerHorizontal>
                            <ColourSelect
                                name="now_line_colorpicker"
                                align="ALIGN_CENTER_VERTICAL"
                                width="60"
                                height="30"
                            />
                            <Spacer />
                            <CheckBox
                                name="use_bold_nowline"
                                event_EVT_CHECKBOX="on_use_bold_nowline"
                                label="$(use_bold_nowline_text)"
                            />
                        </BoxSizerHorizontal>
                        <StaticText
                            label="$(weekend_colour_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <BoxSizerHorizontal>
                            <ColourSelect
                                name="weekend_colorpicker"
                                align="ALIGN_CENTER_VERTICAL"
                                width="60"
                                height="30"
                            />
                            <Spacer />
                            <CheckBox
                                name="colorize_weekends"
                                event_EVT_CHECKBOX="on_colorize_weekends"
                                label="$(colorize_weekends_text)"
                            />
                        </BoxSizerHorizontal>
                    </FlexGridSizer>
                </BoxSizerVertical>
            </Panel>
            <Panel notebookLabel="$(icons_text)">
                <BoxSizerVertical name="x">
                    <FlexGridSizer columns="3" border="ALL">
                        <StaticText
                            label="$(fuzzy_icon_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Choice
                            name="fuzzy_icon_choice"
                            event_EVT_CHOICE="on_fuzzy_icon_changed"
                        />
                        <StaticBitmap
                            name="fuzzy_icon"
                        />
                        <StaticText
                            label="$(locked_icon_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Choice
                            name="locked_icon_choice"
                            event_EVT_CHOICE="on_locked_icon_changed"
                        />
                        <StaticBitmap
                            name="locked_icon"
                        />
                        <StaticText
                            label="$(hyperlink_icon_text)"
                            align="ALIGN_CENTER_VERTICAL"
                        />
                        <Choice
                            name="hyperlink_icon_choice"
                            event_EVT_CHOICE="on_hyperlink_icon_changed"
                        />
                        <StaticBitmap
                            name="hyperlink_icon"
                        />
                    </FlexGridSizer>
                </BoxSizerVertical>
            </Panel>
            <Panel name="experimental_panel" notebookLabel="$(experimental_text)">
                <BoxSizerVertical>
                    <FlexGridSizer
                        name="experimental_panel_sizer"
                        columns="1"
                        border="ALL"
                    />
                </BoxSizerVertical>
            </Panel>
        </Notebook>
        <DialogButtonsCloseSizer border="LEFT|BOTTOM|RIGHT" />
    </BoxSizerVertical>
    """

    def __init__(self, parent, config):
        Dialog.__init__(self, PreferencesDialogController, parent, {
            "general_text": _("General"),
            "open_recent_text": _("Open most recent timeline on startup"),
            "inertial_scrolling_text": _("Use inertial scrolling"),
            "never_period_point_text": _("Never show period Events as point Events"),
            "center_text_text": _("Center Event texts"),
            "uncheck_time_for_new_events_text": _("Uncheck time checkbox for new events"),
            "text_below_icon_text": _("Balloon text below icon"),
            "text_filtered_listbox_export": _("Filter items in listbox export, on categories"),
            "tab_order_text": _("Select Event Editor Tab Order"),
            "date_formatter_text": _("Select Date format"),
            "date_time_text": _("Date && Time"),
            "week_start_text": _("Week start on:"),
            "week_start_choices": [_("Monday"), _("Sunday")],
            "fonts_text": _("Fonts"),
            "colours_text": _("Colours"),
            "major_strip_text": _("Major Strips:"),
            "minor_strip_text": _("Minor Strips:"),
            "balloon_text": _("Balloons:"),
            "icons_text": _("Icons"),
            "fuzzy_icon_text": _("Fuzzy icon"),
            "locked_icon_text": _("Locked icon"),
            "hyperlink_icon_text": _("Hyperlink icon"),
            "legends_text": _("Legends:"),
            "edit_text": _("Edit"),
            "experimental_text": _("Experimental Features"),
            "minor_strip_colour_text": _("Minor strip divider line:"),
            "major_strip_colour_text": _("Major strip divider line:"),
            "now_line_colour_text": _("Now line:"),
            "weekend_colour_text": _("Weekends:"),
            "use_bold_nowline_text": _("Use bold line"),
            "bg_colour_text": _("Background"),
            "vertical_space_between_events_text": _("Vertical space between Events (px)"),
            "colorize_weekends_text": _("Colorize weekends"),
            "skip_s_in_decade_text_text": _("Skip s in decade text"),
            "display_checkmark_on_events_done_text": _("Display checkmark when events are done"),
            "never_use_time_text": _("Never use time precision for events"),
            "use_second_text": _("Use second precision for time"),
            "legend_positions_text": _("Legend Position"),
            "legend_positions": [_("Bottom-Left"), _("Top-Left"), _("Top-Right"), _("Bottom-Right")],
            "time_scale_positions": [_("Top"), _("Center"), _("Bottom")],
            "time_scale_positions_text": _("Time scale position"),
            "default_year": _("Default Year"),
            "default_month": _("Default Month"),
            "default_day": _("Default Day"),
            "use_date_default_values": _("Use date default values"),
        }, title=_("Preferences"))
        self.controller.on_init(config, ExperimentalFeatures())
        self.font_sizer.Layout()

    def SetIconsChoices(self, choices):
        self.fuzzy_icon_choice.SetItems(choices)
        self.locked_icon_choice.SetItems(choices)
        self.hyperlink_icon_choice.SetItems(choices)

    def SetFuzzyIcon(self, icon_name):
        self._setIcon(self.fuzzy_icon_choice, icon_name)

    def SetLockedIcon(self, icon_name):
        self._setIcon(self.locked_icon_choice, icon_name)

    def SetHyperlinkIcon(self, icon_name):
        self._setIcon(self.hyperlink_icon_choice, icon_name)

    def SetCurrentDateFormat(self, current_date_format):
        self.current_date_format.SetLabel(current_date_format)

    def _setIcon(self, icon_ctrl, icon_name):
        if not icon_ctrl.SetStringSelection(icon_name):
            icon_ctrl.Select(0)

    def DisplayIcons(self):
        self.fuzzy_icon.SetBitmap(wx.Bitmap(os.path.join(EVENT_ICONS_DIR, self.fuzzy_icon_choice.GetStringSelection())))
        self.locked_icon.SetBitmap(wx.Bitmap(os.path.join(EVENT_ICONS_DIR, self.locked_icon_choice.GetStringSelection())))
        self.hyperlink_icon.SetBitmap(wx.Bitmap(os.path.join(EVENT_ICONS_DIR, self.hyperlink_icon_choice.GetStringSelection())))
        self.Refresh()

    def Destroy(self):
        self.controller.on_close()
        super(PreferencesDialog, self).Destroy()

    def SetOpenRecentCheckboxValue(self, value):
        self.open_recent_checkbox.SetValue(value)

    def SetInertialScrollingCheckboxValue(self, value):
        self.inertial_scrolling_checkbox.SetValue(value)

    def SetNeverPeriodPointCheckboxValue(self, value):
        self.never_period_point_checkbox.SetValue(value)

    def SetUncheckTimeForNewEventsCheckboxValue(self, value):
        self.uncheck_time_for_new_events.SetValue(value)

    def SetTextBelowIconCheckboxValue(self, value):
        self.text_below_icon.SetValue(value)

    def SetFilteredListboxExport(self, value):
        self.filtered_listbox_export.SetValue(value)

    def SetCenterTextCheckboxValue(self, value):
        self.center_text_checkbox.SetValue(value)

    def SetDisplayCheckmarkOnEventsDone(self, value):
        self.display_checkmark_on_events_done_checkbox.SetValue(value)

    def SetWeekStartSelection(self, value):
        self.week_start_choice.Select(value)

    def SetNeverUseTime(self, value):
        self.never_use_time_checkbox.SetValue(value)

    def SetUseSecond(self, value):
        self.use_second_checkbox.SetValue(value)

    def SetUseDateDefaultValues(self, value):
        self.use_date_default_values_checkbox.SetValue(value)
        
    def SetDefaultYear(self, value):
        self.txt_default_year.SetValue(value)
        
    def SetDefaultMonth(self, value):
        self.txt_default_month.SetValue(value)

    def SetDefaultDay(self, value):
        self.txt_default_day.SetValue(value)
        
    def GetDefaultYear(self):
        return self.txt_default_year.GetValue()
        
    def GetDefaultMonth(self):
        return self.txt_default_month.GetValue()

    def GetDefaultDay(self):
        return self.txt_default_day.GetValue()
        
    def GetNeverUseTime(self):
        return self.never_use_time_checkbox.GetValue()

    def GetUseSecond(self):
        return self.use_second_checkbox.GetValue()

    def GetUseDateDefaultValues(self):
        return self.use_date_default_values_checkbox.GetValue()
        
    def AddExperimentalFeatures(self, features):
        for feature in features:
            name = feature.get_display_name()
            cb = wx.CheckBox(self.experimental_panel, label=name, name=name)
            cb.SetValue(feature.enabled())
            self.experimental_panel_sizer.Add(cb)
            self.Bind(wx.EVT_CHECKBOX, self.controller.on_experimental_changed, cb)
        self.experimental_panel_sizer.Fit(self)
        self.Fit()

    def ShowSelectTabOrderDialog(self, config):
        dialog = EventEditorTabSelectionDialog(self, config)
        dialog.ShowModal()
        dialog.Destroy()

    def ShowSelectDateFormatDialog(self, config):
        dialog = DateFormatDialog(self, config)
        dialog.ShowModal()
        dialog.Destroy()

    def ShowEditFontDialog(self, font):
        return edit_font_data(self, font)

    def GetMinorStripColor(self):
        return self.minor_strip_colorpicker.GetValue()

    def SetMinorStripColor(self, new_color):
        self.minor_strip_colorpicker.SetValue(new_color)

    def GetMajorStripColor(self):
        return self.major_strip_colorpicker.GetValue()

    def SetMajorStripColor(self, new_color):
        self.major_strip_colorpicker.SetValue(new_color)

    def GetNowLineColor(self):
        return self.now_line_colorpicker.GetValue()

    def SetNowLineColor(self, new_color):
        self.now_line_colorpicker.SetValue(new_color)

    def GetBgColor(self):
        return self.bg_colorpicker.GetValue()

    def SetBgColor(self, new_color):
        self.bg_colorpicker.SetValue(new_color)

    def GetWeekendColor(self):
        return self.weekend_colorpicker.GetValue()

    def SetWeekendColor(self, new_color):
        self.weekend_colorpicker.SetValue(new_color)

    def SetVerticalSpaceBetweenEvents(self, value):
        self.vertical_space_between_events.SetValue(value)

    def GetVerticalSpaceBetweenEvents(self):
        return self.vertical_space_between_events.GetValue()

    def SetColorizeWeekends(self, value):
        return self.colorize_weekends.SetValue(value)

    def GetUseBoldNowline(self):
        return self.use_bold_nowline.IsChecked()

    def SetUseBoldNowline(self, value):
        return self.use_bold_nowline.SetValue(value)

    def GetColorizeWeekends(self):
        return self.colorize_weekends.IsChecked()

    def SetSkipSInDecadeText(self, value):
        return self.skip_s_in_decade_text.SetValue(value)

    def GetSkipSInDecadeText(self):
        return self.skip_s_in_decade_text.IsChecked()

    def SetMajorStripFont(self, font):
        self._SetFont(self.major_strip_font_sample, font)

    def SetMinorStripFont(self, font):
        self._SetFont(self.minor_strip_font_sample, font)

    def SetLegendFont(self, font):
        self._SetFont(self.legend_font_sample, font)

    def SetBalloonFont(self, font):
        self._SetFont(self.balloon_font_sample, font)

    def GetLegendPos(self):
        return self.legend_positions.GetSelection()

    def SetLegendPos(self, pos):
        self.legend_positions.SetSelection(pos)

    def GetTimeScalePos(self):
        return self.time_scale_positions.GetSelection()

    def SetTimeScalePos(self, pos):
        self.time_scale_positions.SetSelection(pos)

    def _SetFont(self, control, font):
        control.SetFont(font)
        control.SetForegroundColour(font.WxColor)
        self.font_sizer.Layout()
