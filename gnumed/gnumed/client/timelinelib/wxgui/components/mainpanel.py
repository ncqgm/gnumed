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


import wx

from timelinelib.canvas.data import TimePeriod
from timelinelib.wxgui.components.welcomepanel import WelcomePanel
from timelinelib.wxgui.components.timelinepanel import TimelinePanel
from timelinelib.wxgui.components.searchbar.view import SearchBar
from timelinelib.wxgui.components.propertyeditors.iconeditor import FileToBitmapConverter


class FileDropTarget(wx.FileDropTarget):

    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        try:
            bitmap = FileToBitmapConverter().convert(filenames[0])
            self.obj.controller.event_at(x, y).set_icon(bitmap)
        except:
            pass

    def OnDragOver(self, x, y, defResult):
        if self.obj.controller.event_at(x, y):
            return defResult
        else:
            return wx.DragNone



class MainPanel(wx.Panel):
    """
    Panel that covers the whole client area of MainFrame.

    Displays one of the following panels:

      * The welcome panel (show_welcome_panel)
      * The timeline panel (show_timeline_panel)

    Also displays the search bar.
    """

    def __init__(self, parent, config, main_frame):
        wx.Panel.__init__(self, parent)
        self.config = config
        self.main_frame = main_frame
        self._create_gui()
        # Install variables for backwards compatibility
        self.category_tree = self.timeline_panel.sidebar.category_tree
        self.show_sidebar = self.timeline_panel.show_sidebar
        self.hide_sidebar = self.timeline_panel.hide_sidebar
        self.get_sidebar_width = self.timeline_panel.get_sidebar_width

    def get_export_periods(self, first_time, last_time):
        periods = []
        current_period = None
        if self.main_frame.timeline:
            time_type = self.main_frame.timeline.get_time_type()
            current_period = self.get_view_properties().displayed_period
            period_delta = current_period.end_time - current_period.start_time
            periods.append(current_period)
            start_time = current_period.start_time
            period = current_period
            while first_time < start_time:
                start_time = period.start_time - period_delta
                end_time = period.start_time
                period = TimePeriod(start_time, end_time)
                periods.insert(0, period)
            end_time = current_period.end_time
            period = current_period
            while last_time > end_time:
                start_time = period.end_time
                end_time = period.end_time + period_delta
                period = TimePeriod(start_time, end_time)
                periods.append(period)
        return periods, current_period
        
    def timeline_panel_visible(self):
        return self.timeline_panel.IsShown()

    def show_welcome_panel(self):
        self._show_panel(self.welcome_panel)

    def show_timeline_panel(self):
        self._show_panel(self.timeline_panel)

    def show_searchbar(self, show=True):
        self.searchbar.Show(show)
        if show is True:
            self.searchbar.Focus()
        self.GetSizer().Layout()

    def _remove_timeline_and_show_welcome_panel(self):
        self.category_tree.set_no_timeline_view()
        self.set_searchbar_timeline_canvas(None)
        self.timeline_panel.SetDb(None)
        self.show_welcome_panel()

    def display_timeline(self, timeline):
        if timeline is None:
            # Do we ever end up here with the welcome panel displayed?
            self._remove_timeline_and_show_welcome_panel()
        else:
            self._show_new_timeline(timeline)

    def _show_new_timeline(self, timeline):
        self.timeline_panel.SetDb(timeline)
        canvas = self.get_timeline_canvas()
        self.category_tree.set_timeline_view(canvas.GetDb(), canvas.GetViewProperties())
        self.set_searchbar_timeline_canvas(canvas)
        self.show_timeline_panel()
        canvas.SetDropTarget(FileDropTarget(canvas))

    def get_timeline_canvas(self):
        return self.timeline_panel.get_timeline_canvas()

    def save_view_properties(self, timeline):
        timeline.save_view_properties(self.get_view_properties())

    def get_displayed_period_delta(self):
        return self.get_view_properties().displayed_period.delta()

    def get_time_period(self):
        return self.timeline_panel.get_time_period()

    def get_ids_of_two_first_selected_events(self):
        view_properties = self.get_view_properties()
        return (view_properties.selected_event_ids[0],
                view_properties.selected_event_ids[1])

    def get_selected_event_ids(self):
        return self.get_view_properties().get_selected_event_ids()

    def get_id_of_first_selected_event(self):
        return self.get_view_properties().get_selected_event_ids()[0]

    def get_nbr_of_selected_events(self):
        return len(self.get_view_properties().get_selected_event_ids())

    def open_event_editor(self, event):
        self.timeline_panel.open_event_editor(event)

    def redraw_timeline(self):
        self.timeline_panel.redraw_timeline()

    def Navigate(self, navigation_fn):
        return self.timeline_panel.Navigate(navigation_fn)

    def get_visible_events(self, all_events):
        view_properties = self.get_view_properties()
        visible_events = view_properties.filter_events(all_events)
        return visible_events

    def set_searchbar_timeline_canvas(self, timeline_canvas):
        self.searchbar.SetTimelineCanvas(timeline_canvas)

    def get_view_properties(self):
        return self.timeline_panel.get_view_properties()

    def _create_gui(self):
        # Search bar
        self.searchbar = SearchBar(self)
        self.searchbar.Show(False)
        # Panels
        self.welcome_panel = WelcomePanel(self, self.main_frame)
        self.timeline_panel = TimelinePanel(
            self, self.config, self.main_frame.status_bar_adapter,
            self.main_frame)
        # Layout
        self.sizerOuter = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.welcome_panel, flag=wx.GROW, proportion=1)
        self.sizer.Add(self.timeline_panel, flag=wx.GROW, proportion=1)
        self.sizerOuter.Add(self.sizer, flag=wx.GROW, proportion=1)
        self.sizerOuter.Add(self.searchbar, flag=wx.GROW, proportion=0)
        self.SetSizer(self.sizerOuter)

    def _show_panel(self, panel):
        self._hide_all_panels()
        panel.Show(True)
        self.sizerOuter.Layout()
        panel.activated()

    def _hide_all_panels(self):
        for panel_to_hide in [self.welcome_panel, self.timeline_panel]:
            panel_to_hide.Show(False)
