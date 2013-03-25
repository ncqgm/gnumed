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


import datetime

import wx

from timelinelib.drawing.drawers.default import DefaultDrawingAlgorithm
from timelinelib.play.playcontroller import PlayController


class PlayFrame(wx.Dialog):

    def __init__(self, timeline, config):
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
        self.close_button = wx.Button(self, wx.ID_ANY, label=_("Close"))
        self.drawing_area = DrawingArea(self)
        self.Bind(wx.EVT_BUTTON, self.on_close_clicked, self.close_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.drawing_area)
        vbox.Add(self.close_button)
        self.SetSizerAndFit(vbox)

        drawing_algorithm = DefaultDrawingAlgorithm()
        self.controller = PlayController(
            self, timeline, drawing_algorithm, config)
        self.controller.start_movie()

    def start_timer(self, interval_in_ms):
        self.timer = OurTimer(self.controller.tick)
        self.timer.Start(interval_in_ms)

    def stop_timer(self):
        self.timer.Stop()

    def redraw_drawing_area(self, fn):
        self.drawing_area.redraw_surface(fn)

    def on_close_clicked(self, e):
        self.controller.on_close_clicked()

    def close(self):
        self.EndModal(wx.ID_OK)

    def get_view_period_length(self):
        return datetime.timedelta(days=10)


class OurTimer(wx.Timer):

    def __init__(self, fn):
        wx.Timer.__init__(self)
        self.tick_function = fn

    def Notify(self):
        self.tick_function()


class DrawingArea(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(600, 400))
        self.surface_bitmap = None
        self._create_gui()

    def _create_gui(self):
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def redraw_surface(self, fn_draw):
        width, height = self.GetSizeTuple()
        self.surface_bitmap = wx.EmptyBitmap(width, height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.surface_bitmap)
        memdc.BeginDrawing()
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
        memdc.Clear()
        fn_draw(memdc)
        memdc.EndDrawing()
        del memdc
        self.Refresh()
        self.Update()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        if self.surface_bitmap:
            dc.DrawBitmap(self.surface_bitmap, 0, 0, True)
        else:
            pass # TODO: Fill with white?
        dc.EndDrawing()

