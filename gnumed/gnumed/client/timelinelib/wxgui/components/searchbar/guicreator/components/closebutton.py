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

from timelinelib.config.paths import ICONS_DIR


IMAGE = "close.png"
HELP_TEXT = _("Close")
LABEL = ""


class CloseButton:
    
    def __init__(self, parent):
        self._parent = parent
        parent.AddTool(wx.ID_CLOSE, LABEL, self._bmp(parent), shortHelp=HELP_TEXT)
        parent.Bind(wx.EVT_TOOL, self._event_handler, id=wx.ID_CLOSE)

    def _bmp(self, parent):
        if 'wxMSW' in wx.PlatformInfo:
            return wx.Bitmap(os.path.join(ICONS_DIR, IMAGE))
        else:
            return wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_TOOLBAR, parent._icon_size)
        
    def _event_handler(self, evt):
        self._parent.Close()
