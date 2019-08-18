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


class TextInput:
    
    def __init__(self, parent, controller):
        self._controller = controller
        self._search = wx.SearchCtrl(parent, size=(150, -1), style=wx.TE_PROCESS_ENTER)
        parent.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._event_handler, self._search)
        parent.Bind(wx.EVT_TEXT_ENTER, self._event_handler, self._search)
        parent.AddControl(self._search)
        
    def SetFocus(self):
        self._search.SetFocus()
        
    def GetValue(self):
        return self._search.GetValue()
        
    def _event_handler(self, evt):
        self._controller.search()        
        