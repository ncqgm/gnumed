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


import wx.adv

from timelinelib.wxgui.components.hyperlinkbutton import HyperlinkButton


class WelcomePanel(wx.Panel):

    def __init__(self, parent, main_frame):
        wx.Panel.__init__(self, parent)
        self.main_frame = main_frame
        self._create_gui()

    def _create_gui(self):
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # Text 1
        t1 = wx.StaticText(self, label=_("No timeline opened."))
        vsizer.Add(t1, flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Spacer
        vsizer.AddSpacer(20)
        # Text 2
        t2 = wx.StaticText(self, label=_("First time using Timeline?"))
        vsizer.Add(t2, flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Button
        btn_tutorial = HyperlinkButton(self, _("Getting started tutorial"))
        self.Bind(wx.adv.EVT_HYPERLINK, self._btn_tutorial_on_click, btn_tutorial)
        vsizer.Add(btn_tutorial, flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Sizer
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(vsizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, proportion=1)
        self.SetSizer(hsizer)

    def _btn_tutorial_on_click(self, e):
        self.main_frame.controller.open_timeline(":tutorial:")

    def activated(self):
        pass
