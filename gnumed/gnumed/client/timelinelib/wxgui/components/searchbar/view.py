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
The search bar is a gui component displayed in the status bar whenever 
the user presses Ctrl+F. It consists of the following visual components.
    * A close button
    * A search button
    * A text field
    * A backward navigation button
    * A forward navigation button
    * A 'display list' button
    * Report labels for 'no event found' and 'one event found'

The parent of the component is the TimelinePanel.
   
As with all gui components all business logic is handles by a controller.
Actions on the components are directly delegated to the controller.

The component (or actually the controller) needs a Canvas object in order 
to find events containing the given text. The Canvas object is injected 
with the SetTimelineCanvas() function.
        
"""

import wx

from timelinelib.wxgui.components.searchbar.controller import SearchBarController
from timelinelib.wxgui.components.searchbar.guicreator.guicreator import GuiCreator


class SearchBar(wx.ToolBar, GuiCreator):

    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, style=wx.TB_HORIZONTAL | wx.TB_BOTTOM)
        self._controller = SearchBarController(self)
        self._create_gui()
        self.UpdateButtons()

    #
    # Parent API
    #
    
    def SetTimelineCanvas(self, timeline_canvas):
        self._controller.set_timeline_canvas(timeline_canvas)

    #
    # Controller APIs
    #
    
    def GetValue(self):
        return self._search.GetValue()

    def GetPeriod(self):
        return self._period.GetString()

    def UpdateNbrOfMatchesLabel(self, label):
        self._result_label.SetLabel(label)
        self._result_label.Show(True)

    def UpdateButtons(self):
        self.EnableTool(wx.ID_BACKWARD, self._controller.enable_backward())
        self.EnableTool(wx.ID_FORWARD, self._controller.enable_forward())
        self.EnableTool(wx.ID_MORE, self._controller.enable_list())

    def SetPeriodChoices(self, choices):
        self._period.SetPeriodChoices(choices)

    def Close(self):
        self._result_label.Show(False)
        self.Show(False)
        self.GetParent().Layout()       
