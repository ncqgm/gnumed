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
from timelinelib.wxgui.dialogs.eventlist import EventListDialog 

class GuiCreator(object):

    def _create_gui(self):
        self.icon_size = (16, 16)
        self._create_close_button()
        self._create_search_box()
        self._create_prev_button()
        self._create_next_button()
        self._create_list_button()
        self._create_no_match_label()
        self._create_single_match_label()
        self.Realize()

    def set_focus(self):
        self.search.SetFocus()

    def _create_search_box(self):
        self.search = wx.SearchCtrl(self, size=(150, -1),
                                    style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                  self._search_on_search_btn, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_on_text_enter, self.search)
        self.AddControl(self.search)

    def _create_close_button(self):
        if 'wxMSW' in wx.PlatformInfo:
            close_bmp = wx.Bitmap(os.path.join(ICONS_DIR, "close.png"))
        else:
            close_bmp = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_TOOLBAR,
                                             self.icon_size)
        self.AddLabelTool(wx.ID_CLOSE, "", close_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_close_on_click, id=wx.ID_CLOSE)

    def _create_prev_button(self):
        prev_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                                            self.icon_size)
        self.AddLabelTool(wx.ID_BACKWARD, "", prev_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_prev_on_click, id=wx.ID_BACKWARD)

    def _create_next_button(self):
        next_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, self.icon_size)
        self.AddLabelTool(wx.ID_FORWARD, "", next_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_next_on_click, id=wx.ID_FORWARD)

    def _create_list_button(self):
        list_bmp = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, self.icon_size)
        self.AddLabelTool(wx.ID_MORE, "", list_bmp, shortHelp="")
        self.Bind(wx.EVT_TOOL, self._btn_list_on_click, id=wx.ID_MORE)

    def _create_no_match_label(self):
        self.lbl_no_match = wx.StaticText(self, label=_("No match"))
        self.lbl_no_match.Show(False)
        self.AddControl(self.lbl_no_match)

    def _create_single_match_label(self):
        self.lbl_single_match = wx.StaticText(self, label=_("Only one match"))
        self.lbl_single_match.Show(False)
        self.AddControl(self.lbl_single_match)

    def _btn_close_on_click(self, e):
        self.Show(False)

    def _search_on_search_btn(self, e):
        self.controller.search()

    def _search_on_text_enter(self, e):
        self.controller.search()

    def _btn_prev_on_click(self, e):
        self.controller.prev()

    def _btn_next_on_click(self, e):
        self.controller.next()

    def _btn_list_on_click(self, e):
        self.controller.list()


class SearchBarController(object):

    def __init__(self, view):
        self.view = view
        self.result = []
        self.result_index = 0
        self.last_search = None

    def set_drawing_area_panel(self, drawing_area_panel):
        self.drawing_area_panel = drawing_area_panel
        self.view.Enable(drawing_area_panel is not None)

    def search(self):
        new_search = self.view.get_value()
        if self.last_search is not None and self.last_search == new_search:
            self.next()
        else:
            self.last_search = new_search
            if self.drawing_area_panel is not None:
                self.result = self.drawing_area_panel.get_filtered_events(new_search)
            else:
                self.result = []
            self.result_index = 0
            self.navigate_to_match()
            self.view.update_nomatch_labels(len(self.result) == 0)
            self.view.update_singlematch_label(len(self.result) == 1)
        self.view.update_buttons()

    def next(self):
        if not self._on_last_match():
            self.result_index += 1
            self.navigate_to_match()
            self.view.update_buttons()

    def prev(self):
        if not self._on_first_match():
            self.result_index -= 1
            self.navigate_to_match()
            self.view.update_buttons()

    def list(self):
        event_list = [event.get_label() for event in self.result]
        dlg = EventListDialog(self.view, event_list)
        if dlg.ShowModal() == wx.ID_OK:
            self.result_index = dlg.get_selected_index()
            self.navigate_to_match()
        dlg.Destroy()
    
    def navigate_to_match(self):
        if (self.drawing_area_panel is not None and self.result_index in range(len(self.result))):
            event = self.result[self.result_index]
            self.drawing_area_panel.navigate_timeline(lambda tp: tp.center(event.mean_time()))

    def enable_backward(self):
        return bool(self.result and self.result_index > 0)

    def enable_forward(self):
        return bool(self.result and self.result_index < (len(self.result) - 1))

    def enable_list(self):
        return bool(len(self.result) > 0)

    def _on_first_match(self):
        return self.result > 0 and self.result_index == 0

    def _on_last_match(self):
        return self.result > 0 and self.result_index ==  (len(self.result) - 1)


class SearchBar(wx.ToolBar, GuiCreator):

    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_HORIZONTAL|wx.TB_BOTTOM)
        self.controller = SearchBarController(self)
        self._create_gui()
        self.update_buttons()

    def set_drawing_area_panel(self, drawing_area_panel):
        self.controller.set_drawing_area_panel(drawing_area_panel)

    def get_value(self):
        return self.search.GetValue()

    def update_nomatch_labels(self, nomatch):
        self.lbl_no_match.Show(nomatch)

    def update_singlematch_label(self, singlematch):
        self.lbl_single_match.Show(singlematch)

    def update_buttons(self):
        self.EnableTool(wx.ID_BACKWARD, self.controller.enable_backward())
        self.EnableTool(wx.ID_FORWARD, self.controller.enable_forward())
        self.EnableTool(wx.ID_MORE, self.controller.enable_list())
