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
from timelinelib.wxgui.dialogs.feedback import show_feedback_dialog


class FeedbackButton(wx.BitmapButton):

    def __init__(self, parent, info, subject):
        self.parent = parent
        self.info = info
        self.subject = subject
        self._init_gui()

    def _init_gui(self):
        feedback_bitmap = wx.Bitmap(os.path.join(ICONS_DIR, "feedback.png"))
        wx.BitmapButton.__init__(self, self.parent, wx.ID_ANY, feedback_bitmap)
        self.SetToolTip(wx.ToolTip(_("Give feedback")))
        self.Bind(wx.EVT_BUTTON, self.on_click, self)

    def on_click(self, event):
        show_feedback_dialog(self.info, self.subject, "", self.parent)
