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


import wx

from timelinelib.wxgui.utils import BORDER


class EventListDialog(wx.Dialog):

    def __init__(self, parent, event_list):
        wx.Dialog.__init__(self, parent, title=_("Found Events"), name="event_list",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.event_list = event_list
        self._create_gui()
        self._bind()

    def get_selected_index(self):
        return self.lb_eventlist.GetSelection()
        
    def _create_gui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._create_listbox(), flag=wx.ALL|wx.EXPAND, border=BORDER, proportion=1)
        sizer.Add(self._create_buttons(), flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(sizer)

    def _create_listbox(self):
        self.lb_eventlist = wx.ListBox(self, wx.ID_ANY, choices=self.event_list)
        return self.lb_eventlist

    def _create_buttons(self):
        return self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        
    def _bind(self):
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        self.Bind(wx.EVT_SIZE, self._on_size, self)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self._btn_ok_on_click, self.lb_eventlist)
        self.Bind(wx.EVT_CLOSE, self._window_on_close)

    def _btn_ok_on_click(self, evt):
        self.EndModal(wx.ID_OK)

    def _on_size(self, evt):
        self.Layout()
        
    def _window_on_close(self, e):
        self.EndModal(wx.ID_CANCEL)
