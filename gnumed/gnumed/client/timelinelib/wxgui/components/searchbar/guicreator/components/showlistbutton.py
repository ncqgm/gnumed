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


HELP_TEXT = _("List matches")
LABEL = ""


class ShowListButton:
    
    def __init__(self, parent, controller):
        self._controller = controller
        bmp = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, parent._icon_size)
        parent.AddTool(wx.ID_MORE, LABEL, bmp, shortHelp=HELP_TEXT)
        parent.Bind(wx.EVT_TOOL, self._event_handler, id=wx.ID_MORE)
        
    def _event_handler(self, evt):
        self._controller.list()
                