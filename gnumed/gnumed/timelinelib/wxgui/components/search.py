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


import os.path

import wx

from timelinelib.config.paths import ICONS_DIR


class SearchBar(wx.ToolBar):

    def __init__(self, parent, close_fn):
        wx.ToolBar.__init__(self, parent, style=wx.TB_HORIZONTAL|wx.TB_BOTTOM)
        self.last_search = None
        self.result = []
        self.result_index = 0
        self.view = None
        self.close_fn = close_fn
        self._create_gui()
        self._update_buttons()

    def set_view(self, view):
        self.view = view
        self.Enable(view is not None)

    def _create_gui(self):
        icon_size = (16, 16)
        # Close button
        if 'wxMSW' in wx.PlatformInfo:
            close_bmp = wx.Bitmap(os.path.join(ICONS_DIR, "close.png"))
        else:
            close_bmp = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_TOOLBAR,
                                             icon_size)
        self.AddLabelTool(wx.ID_CLOSE, "", close_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_close_on_click, id=wx.ID_CLOSE)
        # Search box
        self.search = wx.SearchCtrl(self, size=(150, -1),
                                    style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                  self._search_on_search_btn, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_on_text_enter, self.search)
        self.AddControl(self.search)
        # Prev button
        prev_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                                            icon_size)
        self.AddLabelTool(wx.ID_BACKWARD, "", prev_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_prev_on_click, id=wx.ID_BACKWARD)
        # Next button
        next_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR,
                                            icon_size)
        self.AddLabelTool(wx.ID_FORWARD, "", next_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_next_on_click, id=wx.ID_FORWARD)
        # No match label
        self.lbl_no_match = wx.StaticText(self, label=_("No match"))
        self.lbl_no_match.Show(False)
        self.AddControl(self.lbl_no_match)
        # Single match label
        self.lbl_single_match = wx.StaticText(self, label=_("Only one match"))
        self.lbl_single_match.Show(False)
        self.AddControl(self.lbl_single_match)
        # Finish it up
        self.Realize()

    def _btn_close_on_click(self, e):
        self.close_fn()

    def _search_on_search_btn(self, e):
        self._search()

    def _search_on_text_enter(self, e):
        self._search()

    def _btn_prev_on_click(self, e):
        self._prev()

    def _btn_next_on_click(self, e):
        self._next()

    def _search(self):
        new_search = self.search.GetValue()
        if self.last_search is not None and self.last_search == new_search:
            self._next()
        else:
            self.last_search = new_search
            if self.view is not None:
                events = self.view.get_timeline().search(self.last_search)
                filtered_events = self.view.get_view_properties().filter_events(events)
                self.result = filtered_events
            else:
                self.result = []
            self.result_index = 0
            self._navigate_to_match()
            self.lbl_no_match.Show(len(self.result) == 0)
            self.lbl_single_match.Show(len(self.result) == 1)
        self._update_buttons()

    def _update_buttons(self):
        enable_backward = bool(self.result and self.result_index > 0)
        self.EnableTool(wx.ID_BACKWARD, enable_backward)
        enable_forward = bool(self.result and
                              self.result_index < (len(self.result) - 1))
        self.EnableTool(wx.ID_FORWARD, enable_forward)

    def _next(self):
        if self.result > 0 and self.result_index < (len(self.result) - 1):
            self.result_index += 1
            self._navigate_to_match()
            self._update_buttons()

    def _prev(self):
        if self.result > 0 and self.result_index > 0:
            self.result_index -= 1
            self._navigate_to_match()
            self._update_buttons()

    def _navigate_to_match(self):
        if (self.view is not None and
            self.result_index in range(len(self.result))):
            event = self.result[self.result_index]
            self.view.navigate_timeline(lambda tp: tp.center(event.mean_time()))
