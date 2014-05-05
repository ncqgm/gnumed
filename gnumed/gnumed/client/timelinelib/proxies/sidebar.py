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


class SidebarProxy():
    
    def __init__(self, creator):
        from timelinelib.wxgui.dialogs.mainframe import MainFrame
        if isinstance(creator, MainFrame):
            self.sidebar = creator.main_panel.timeline_panel.sidebar
        
    def mouse_over_sidebar(self):
        pos = wx.GetMousePosition()
        panel_pos = self.sidebar.ScreenToClient(pos)
        size = self.sidebar.Size
        return panel_pos.x <= size.width and panel_pos.y < size.height
        
    def check_categories(self, categories):
        self.sidebar.category_tree.check_categories(categories)
        
    def uncheck_categories(self, categories):
        self.sidebar.category_tree.uncheck_categories(categories)
