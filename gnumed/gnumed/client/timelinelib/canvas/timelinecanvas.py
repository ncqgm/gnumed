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

from timelinelib.canvas.events import create_divider_position_changed_event
from timelinelib.canvas.timelinecanvascontroller import TimelineCanvasController


MOVE_HANDLE = 0
LEFT_RESIZE_HANDLE = 1
RIGHT_RESIZE_HANDLE = 2
# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5
HSCROLL_STEP = 25


class TimelineCanvas(wx.Panel):
    """
    This is the surface on which a timeline is drawn. It is also the object that handles user
    input events such as mouse and keyboard actions.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER | wx.WANTS_CHARS)
        self.controller = TimelineCanvasController(self)
        self.surface_bitmap = None
        self._create_gui()
        self.SetDividerPosition(50)
        self._highlight_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_highlight_timer, self._highlight_timer)

    def GetAppearance(self):
        return self.controller.get_appearance()

    def SetAppearance(self, appearance):
        self.controller.set_appearance(appearance)

    def GetDividerPosition(self):
        return self._divider_position

    def SetDividerPosition(self, position):
        self._divider_position = int(min(100, max(0, position)))
        self.PostEvent(create_divider_position_changed_event())
        self.controller.redraw_timeline()

    def GetHiddenEventCount(self):
        return self.controller.drawing_algorithm.get_hidden_event_count()

    def Scroll(self, factor):
        self.Navigate(lambda tp: tp.move_delta(-tp.delta() * factor))

    def UseFastDraw(self, use):
        self.controller.use_fast_draw(use)
        self.Redraw()

    def GetHScrollAmount(self):
        return self.controller.view_properties.hscroll_amount

    def SetHScrollAmount(self, amount):
        self.controller.view_properties.hscroll_amount = amount

    def IncrementEventTextFont(self):
        self.controller.drawing_algorithm.increment_font_size()

    def DecrementEventTextFont(self):
        self.controller.drawing_algorithm.decrement_font_size()

    def SetPeriodSelection(self, period):
        if period is None:
            self.controller.view_properties.period_selection = None
        else:
            self.controller.view_properties.period_selection = (period.start_time, period.end_time)
        self.controller._redraw_timeline()

    def Snap(self, time):
        return self.controller.get_drawer().snap(time)

    def PostEvent(self, event):
        wx.PostEvent(self, event)

    def SetEventBoxDrawer(self, event_box_drawer):
        self.controller.set_event_box_drawer(event_box_drawer)
        self.redraw_timeline()

    def SetEventSelected(self, event, is_selected):
        self.controller.view_properties.set_selected(event, is_selected)

    def ClearSelectedEvents(self):
        self.controller.view_properties.clear_selected()

    def SelectAllEvents(self):
        self.controller.view_properties.select_all_events()

    def IsEventSelected(self, event):
        return self.controller.is_selected(event)

    def SetHoveredEvent(self, event):
        self.controller.view_properties.change_hovered_event(event)

    def GetHoveredEvent(self):
        return self.controller.view_properties.hovered_event

    def GetSelectedEvent(self):
        selected_events = self.GetSelectedEvents()
        if len(selected_events) == 1:
            return selected_events[0]
        return None

    def GetSelectedEvents(self):
        return self.controller.get_selected_events()

    def GetClosestOverlappingEvent(self, event, up):
        return self.controller.drawing_algorithm.get_closest_overlapping_event(event, up=up)

    def GetTimeType(self):
        return self.get_timeline().get_time_type()

    def GetDb(self):
        return self.get_timeline()

    def GetEventAt(self, x, y, prefer_container=False):
        return self.controller.drawing_algorithm.event_at(x, y, prefer_container)

    def GetEventWithHitInfoAt(self, x, y, prefer_container=False):
        event_and_rect = self.controller.event_with_rect_at(x, y, prefer_container)
        if event_and_rect is not None:
            event, rect = event_and_rect
            center = rect.X + rect.Width / 2
            if abs(x - center) <= HIT_REGION_PX_WITH:
                return (event, MOVE_HANDLE)
            elif abs(x - rect.X) < HIT_REGION_PX_WITH:
                return (event, LEFT_RESIZE_HANDLE)
            elif abs(rect.X + rect.Width - x) < HIT_REGION_PX_WITH:
                return (event, RIGHT_RESIZE_HANDLE)
        return None

    def GetBalloonAt(self, x, y):
        return self.controller.drawing_algorithm.balloon_at(x, y)

    def EventHasStickyBalloon(self, event):
        return self.controller.view_properties.event_has_sticky_balloon(event)

    def SetEventStickyBalloon(self, event, is_sticky):
        self.controller.view_properties.set_event_has_sticky_balloon(event, is_sticky)
        self.redraw_timeline()

    def GetTimeAt(self, x):
        return self.controller.get_time(x)

    def get_timeline(self):
        return self.controller.get_timeline()

    def set_timeline(self, timeline):
        self.controller.set_timeline(timeline)

    def get_view_properties(self):
        return self.controller.get_view_properties()

    def SaveAsPng(self, path):
        wx.ImageFromBitmap(self.surface_bitmap).SaveFile(path, wx.BITMAP_TYPE_PNG)

    def SaveAsSvg(self, path):
        from timelinelib.canvas.svg import export
        export(path, self.controller.get_timeline(), self.controller.get_drawer().scene,
               self.controller.view_properties, self.GetAppearance())

    def get_filtered_events(self, search_target):
        events = self.get_timeline().search(search_target)
        return self.get_view_properties().filter_events(events)

    def get_time_period(self):
        return self.controller.get_time_period()

    def Navigate(self, navigation_fn):
        self.controller.navigate(navigation_fn)

    def Redraw(self):
        self.redraw_timeline()

    def EventIsPeriod(self, event):
        return self.controller.event_is_period(event)

    def redraw_timeline(self):
        self.controller.redraw_timeline()

    def redraw_surface(self, fn_draw):
        width, height = self.GetSizeTuple()
        self.surface_bitmap = wx.EmptyBitmap(width, height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.surface_bitmap)
        memdc.BeginDrawing()
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.PENSTYLE_SOLID))
        memdc.Clear()
        fn_draw(memdc)
        memdc.EndDrawing()
        del memdc
        self.Refresh()
        self.Update()

    def set_select_period_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))

    def set_size_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def set_move_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))

    def set_default_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def zoom_in(self):
        self.Zoom(1, self._get_half_width())

    def zoom_out(self):
        self.Zoom(-1, self._get_half_width())

    def vert_zoom_in(self):
        self.ZoomVertically(1)

    def vert_zoom_out(self):
        self.ZoomVertically(-1)

    def Zoom(self, direction, x):
        """ zoom time line at position x """
        width, _ = self.GetSizeTuple()
        x_percent_of_width = float(x) / width
        self.Navigate(lambda tp: tp.zoom(direction, x_percent_of_width))

    def ZoomVertically(self, direction):
        if direction > 0:
            self.IncrementEventTextFont()
        else:
            self.DecrementEventTextFont()
        self.Redraw()

    def Scrollvertically(self, direction):
        if direction > 0:
            self._scroll_up()
        else:
            self._scroll_down()
        self.Redraw()

    def _scroll_up(self):
        self.SetHScrollAmount(max(0, self.GetHScrollAmount() - HSCROLL_STEP))

    def _scroll_down(self):
        self.SetHScrollAmount(self.GetHScrollAmount() + HSCROLL_STEP)

    def _get_half_width(self):
        return self.GetSize()[0] / 2

    def _create_gui(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _on_erase_background(self, event):
        # For double buffering
        pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        if self.surface_bitmap:
            dc.DrawBitmap(self.surface_bitmap, 0, 0, True)
        else:
            pass  # TODO: Fill with white?
        dc.EndDrawing()

    def _on_size(self, evt):
        self.controller.window_resized()

    def highligt_event(self, event, clear=False):
        self.controller.view_properties.add_highlight(event, clear=clear)
        if not self._highlight_timer.IsRunning():
            self._highlight_timer.Start(milliseconds=180)

    def _on_highlight_timer(self, evt):
        self.redraw_timeline()
        self.controller.view_properties.tick_highlights(limit=15)
        if not self.controller.view_properties.has_higlights():
            self._highlight_timer.Stop()
