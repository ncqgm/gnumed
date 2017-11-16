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

from timelinelib.wxgui.components.categorytree import CustomCategoryTree


class Sidebar(wx.Panel):

    def __init__(self, main_frame, parent):
        self.main_frame = main_frame
        wx.Panel.__init__(self, parent, style=wx.BORDER_NONE)
        self.Hide()
        self._create_gui()

    def _create_gui(self):
        self.category_tree = CustomCategoryTree(self)
        label = _("View Categories Individually")
        self.cbx_toggle_cat_view = wx.CheckBox(self, -1, label)
        # Layout
        sizer = wx.GridBagSizer(vgap=0, hgap=0)
        sizer.AddGrowableCol(0, proportion=0)
        sizer.AddGrowableRow(0, proportion=0)
        sizer.Add(self.category_tree, (0, 0), flag=wx.GROW)
        sizer.Add(self.cbx_toggle_cat_view, (1, 0), flag=wx.ALL, border=5)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CHECKBOX, self._cbx_on_click, self.cbx_toggle_cat_view)

    def ok_to_edit(self):
        return self.main_frame.ok_to_edit()

    def edit_ends(self):
        return self.main_frame.edit_ends()

    def _cbx_on_click(self, evt):
        from timelinelib.wxgui.frames.mainframe.mainframe import CatsViewChangedEvent
        event = CatsViewChangedEvent(self.GetId())
        event.ClientData = evt.GetEventObject().IsChecked()
        self.GetEventHandler().ProcessEvent(event)
