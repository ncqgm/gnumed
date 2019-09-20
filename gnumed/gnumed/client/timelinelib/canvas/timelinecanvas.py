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

from timelinelib.canvas.events import create_divider_position_changed_event
from timelinelib.canvas.timelinecanvascontroller import TimelineCanvasController
from timelinelib.wxgui.keyboard import Keyboard
from timelinelib.wxgui.cursor import Cursor
from timelinelib.canvas.data import TimePeriod
from timelinelib.canvas.highlighttimer import HighlightTimer
import timelinelib.wxgui.utils as guiutils


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

    HORIZONTAL = 8
    VERTICAL = 16
    BOTH = 32

    START = 0
    DRAG = 1
    STOP = 2

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER | wx.WANTS_CHARS)
        self._controller = TimelineCanvasController(self)
        self._surface_bitmap = None
        self._create_gui()
        self.SetDividerPosition(50)
        self._highlight_timer = HighlightTimer(self._highlight_timer_tick)
        self._last_balloon_event = None
        self._waiting = False

    def GetAppearance(self):
        return self._controller.get_appearance()

    def SetAppearance(self, appearance):
        self._controller.set_appearance(appearance)

    def GetDividerPosition(self):
        return self._divider_position

    def SetDividerPosition(self, position):
        self._divider_position = int(min(100, max(0, position)))
        self.PostEvent(create_divider_position_changed_event())
        self._controller.redraw_timeline()

    def GetHiddenEventCount(self):
        return self._controller.get_hidden_event_count()

    def Scroll(self, factor):
        self.Navigate(lambda tp: tp.move_delta(-tp.delta() * factor))

    def DrawSelectionRect(self, cursor):
        self._controller.set_selection_rect(cursor)

    def RemoveSelectionRect(self):
        self._controller.remove_selection_rect()

    def UseFastDraw(self, use):
        self._controller.use_fast_draw(use)
        self.Redraw()

    def GetHScrollAmount(self):
        return self._controller.get_hscroll_amount()

    def SetHScrollAmount(self, amount):
        self._controller.set_hscroll_amount(amount)

    def IncrementEventTextFont(self):
        self._controller.increment_font_size()

    def DecrementEventTextFont(self):
        self._controller.decrement_font_size()

    def SetPeriodSelection(self, period):
        self._controller.set_period_selection(period)

    def Snap(self, time):
        return self._controller.snap(time)

    def PostEvent(self, event):
        wx.PostEvent(self, event)

    def SetEventBoxDrawer(self, event_box_drawer):
        self._controller.set_event_box_drawer(event_box_drawer)
        self.Redraw()

    def SetEventSelected(self, event, is_selected):
        self._controller.set_selected(event, is_selected)

    def ClearSelectedEvents(self):
        self._controller.clear_selected()

    def SelectAllEvents(self):
        self._controller.select_all_events()

    def IsEventSelected(self, event):
        return self._controller.is_selected(event)

    def SetHoveredEvent(self, event):
        self._controller.set_hovered_event(event)

    def GetHoveredEvent(self):
        return self._controller.get_hovered_event

    def GetSelectedEvent(self):
        selected_events = self.GetSelectedEvents()
        if len(selected_events) == 1:
            return selected_events[0]
        return None

    def GetSelectedEvents(self):
        return self._controller.get_selected_events()

    def GetClosestOverlappingEvent(self, event, up):
        return self._controller.get_closest_overlapping_event(event, up=up)

    def GetTimeType(self):
        return self.GetDb().get_time_type()

    def GetDb(self):
        return self._controller.get_timeline()

    def IsReadOnly(self):
        return self.GetDb().is_read_only()

    def GetEventAtCursor(self, prefer_container=False):
        cursor = Cursor(*self.ScreenToClient(wx.GetMousePosition()))
        return self.GetEventAt(cursor, prefer_container)

    def GetEventAt(self, cursor, prefer_container=False):
        return self._controller.event_at(cursor.x, cursor.y, prefer_container)

    def SelectEventsInRect(self, rect):
        self._controller.select_events_in_rect(rect)

    def GetEventWithHitInfoAt(self, cursor, keyboard=Keyboard()):
        x, y = cursor.pos
        prefer_container = keyboard
        event_and_rect = self._controller.event_with_rect_at(x, y, prefer_container.alt)
        if event_and_rect is not None:
            event, rect = event_and_rect
            center = rect.X + rect.Width // 2
            if abs(x - center) <= HIT_REGION_PX_WITH:
                return (event, MOVE_HANDLE)
            elif abs(x - rect.X) < HIT_REGION_PX_WITH:
                return (event, LEFT_RESIZE_HANDLE)
            elif abs(rect.X + rect.Width - x) < HIT_REGION_PX_WITH:
                return (event, RIGHT_RESIZE_HANDLE)
        return None

    def GetBalloonAtCursor(self):
        cursor = Cursor(*self.ScreenToClient(wx.GetMousePosition()))
        return self._controller.balloon_at(cursor)

    def GetBalloonAt(self, cursor):
        return self._controller.balloon_at(cursor)

    def EventHasStickyBalloon(self, event):
        return self._controller.event_has_sticky_balloon(event)

    def SetEventStickyBalloon(self, event, is_sticky):
        self._controller.set_event_sticky_balloon(event, is_sticky)

    def GetTimeAt(self, x):
        return self._controller.get_time(x)

    def SetTimeline(self, timeline):
        self._controller.set_timeline(timeline)

    def GetViewProperties(self):
        return self._controller.get_view_properties()

    def SaveAsPng(self, path):
        self._surface_bitmap.ConvertToImage().SaveFile(path, wx.BITMAP_TYPE_PNG)

    def SaveAsSvg(self, path):
        from timelinelib.canvas.svg import export
        export(path, self._controller.get_timeline(), self._controller.scene,
               self._controller.get_view_properties(), self.GetAppearance())

    def GetFilteredEvents(self, search_target, search_period):
        events = self.GetDb().search(search_target)
        return self._controller.filter_events(events, search_period)

    def GetTimePeriod(self):
        return self._controller.get_time_period()

    def Navigate(self, navigation_fn):
        self._controller.navigate(navigation_fn)

    def Redraw(self):
        self._controller.redraw_timeline()

    def EventIsPeriod(self, event):
        return self._controller.event_is_period(event)

    def RedrawSurface(self, fn_draw):
        width, height = self.GetSize()
        self._surface_bitmap = wx.Bitmap(width, height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self._surface_bitmap)
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_SOLID))
        memdc.Clear()
        fn_draw(memdc)
        del memdc
        self.Refresh()
        self.Update()

    def set_size_cursor(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_SIZEWE))

    def set_move_cursor(self):
        self.SetCursor(wx.Cursor(wx.CURSOR_SIZING))

    def set_default_cursor(self):
        guiutils.set_default_cursor(self)

    def zoom_in(self):
        self.Zoom(1, self._get_half_width())

    def zoom_out(self):
        self.Zoom(-1, self._get_half_width())

    def Zoom(self, direction, x):
        """ zoom time line at position x """
        width, _ = self.GetSize()
        x_percent_of_width = x / width
        self.Navigate(lambda tp: tp.zoom(direction, x_percent_of_width))

    def vertical_zoom_in(self):
        self.ZoomVertically(1)

    def vertical_zoom_out(self):
        self.ZoomVertically(-1)

    def ZoomVertically(self, direction):
        if direction > 0:
            self.IncrementEventTextFont()
        else:
            self.DecrementEventTextFont()

    def Scrollvertically(self, direction):
        if direction > 0:
            self._scroll_up()
        else:
            self._scroll_down()
        self.Redraw()

    # ----(Helper functions simplifying usage of timeline component)--------

    def SetStartTime(self, evt):
        self._start_time = self.GetTimeAt(evt.GetX())

    def _direction(self, evt):
        rotation = evt.GetWheelRotation()
        return 1 if rotation > 0 else -1 if rotation < 0 else 0

    def ZoomHorizontallyOnMouseWheel(self, evt):
        self.Zoom(self._direction(evt), evt.GetX())

    def ZoomVerticallyOnMouseWheel(self, evt):
        if self._direction(evt) > 0:
            self.IncrementEventTextFont()
        else:
            self.DecrementEventTextFont()

    def ScrollHorizontallyOnMouseWheel(self, evt):
        self.Scroll(evt.GetWheelRotation() / 1200.0)

    def ScrollVerticallyOnMouseWheel(self, evt):
        self.SetDividerPosition(self.GetDividerPosition() + self._direction(evt))

    def SpecialScrollVerticallyOnMouseWheel(self, evt):
        self.Scrollvertically(self._direction(evt))

    def DisplayBalloons(self, evt):

        def cursor_has_left_event():
            # TODO: Can't figure out why self.GetEventAtCursor() returns None
            # in this situation. The LeftDown check saves us for the moment.
            if wx.GetMouseState().LeftIsDown():
                return False
            else:
                return self.GetEventAtCursor() != self._last_balloon_event

        def no_balloon_at_cursor():
            return not self.GetBalloonAtCursor()

        def update_last_seen_event():
            if self._last_balloon_event is None:
                self._last_balloon_event = self.GetEventAtCursor()
            elif cursor_has_left_event() and no_balloon_at_cursor():
                self._last_balloon_event = None
            return self._last_balloon_event

        def delayed_call():
            if self.GetAppearance().get_balloons_visible():
                self.SetHoveredEvent(self._last_balloon_event)
                self._waiting = False

        # Same delay as when we used timers
        # Don't issue call when in wait state, to avoid flicker
        if not self._waiting:
            update_last_seen_event()
            self._wating = True
            wx.CallLater(500, delayed_call)

    def GetTimelineInfoText(self, evt):

        def format_current_pos_time_string(x):
            tm = self.GetTimeAt(x)
            return self.GetTimeType().format_period(TimePeriod(tm, tm))

        event = self.GetEventAtCursor()
        if event:
            return event.get_label(self.GetTimeType())
        else:
            return format_current_pos_time_string(evt.GetX())

    def SetCursorShape(self, evt):

        def get_cursor():
            return Cursor(evt.GetX(), evt.GetY())

        def get_keyboard():
            return Keyboard(evt.ControlDown(), evt.ShiftDown(), evt.AltDown())

        def hit_resize_handle():
            try:
                event, hit_info = self.GetEventWithHitInfoAt(get_cursor(), get_keyboard())
                if event.get_locked():
                    return None
                if event.is_milestone():
                    return None
                if not self.IsEventSelected(event):
                    return None
                if hit_info == LEFT_RESIZE_HANDLE:
                    return wx.LEFT
                if hit_info == RIGHT_RESIZE_HANDLE:
                    return wx.RIGHT
                return None
            except:
                return None

        def hit_move_handle():
            event_and_hit_info = self.GetEventWithHitInfoAt(get_cursor(), get_keyboard())
            if event_and_hit_info is None:
                return False
            (event, hit_info) = event_and_hit_info
            if event.get_locked():
                return False
            if not self.IsEventSelected(event):
                return False
            if event.get_ends_today():
                return False
            return hit_info == MOVE_HANDLE

        def over_resize_handle():
            return hit_resize_handle() is not None

        def over_move_handle():
            return hit_move_handle()

        if over_resize_handle():
            self.set_size_cursor()
        elif over_move_handle():
            self.set_move_cursor()
        else:
            self.set_default_cursor()

    def CenterAtCursor(self, evt):
        _time_at_cursor = self.GetTimeAt(evt.GetX())
        self.Navigate(lambda tp: tp.center(_time_at_cursor))

    def ToggleEventSelection(self, evt):

        def get_cursor():
            return Cursor(evt.GetX(), evt.GetY())

        event = self.GetEventAt(get_cursor(), evt.AltDown())
        if event:
            self.SetEventSelected(event, not self.IsEventSelected(event))

    def InitDragScroll(self, direction=wx.HORIZONTAL):
        self._scrolling = False
        self._scrolling_direction = direction

    def StartDragScroll(self, evt):
        self._scrolling = True
        self._drag_scroll_start_time = self.GetTimeAt(evt.GetX())
        self._start_mouse_pos = evt.GetY()
        self._start_divider_pos = self.GetDividerPosition()

    def DragScroll(self, evt):
        if self._scrolling:
            if self._scrolling_direction in (wx.HORIZONTAL, wx.BOTH):
                delta = self._drag_scroll_start_time - self.GetTimeAt(evt.GetX())
                self.Navigate(lambda tp: tp.move_delta(delta))
            if self._scrolling_direction in (wx.VERTICAL, wx.BOTH):
                percentage_distance = 100 * float(evt.GetY() - self._start_mouse_pos) / float(self.GetSize()[1])
                new_pos = self._start_divider_pos + percentage_distance
                self.SetDividerPosition(new_pos)

    def StopDragScroll(self):
        self._scrolling = False

    def InitDragEventSelect(self):
        self._selecting = False

    def StartDragEventSelect(self, evt):
        self._selecting = True
        self._cursor = self.GetCursor(evt)

    def DragEventSelect(self, evt):
        if self._selecting:
            cursor = self.GetCursor(evt)
            self._cursor.move(*cursor.pos)
            self.DrawSelectionRect(self._cursor)

    def GetCursor(self, evt):
        return Cursor(evt.GetX(), evt.GetY())

    def StopDragEventSelect(self):
        if self._selecting:
            self.SelectEventsInRect(self._cursor.rect)
            self.RemoveSelectionRect()
            self._selecting = False

    def InitZoomSelect(self):
        self._zooming = False
        
    def StartZoomSelect(self, evt):
        self._zooming = True
        self._start_time = self.GetTimeAt(evt.GetX())
        self._end_time = self.GetTimeAt(evt.GetX())

    def DragZoom(self, evt):
        if self._zooming:
            self._end_time = self.GetTimeAt(evt.GetX())
            self.SetPeriodSelection(TimePeriod(self._start_time, self._end_time))

    def StopDragZoom(self):
        self._zooming = False
        self.SetPeriodSelection(None)
        self.Navigate(lambda tp: tp.update(self._start_time, self._end_time))

    def InitDragPeriodSelect(self):
        self._period_select = False

    def StartDragPeriodSelect(self, evt):
        self._period_select = True
        self._start_time = self.GetTimeAt(evt.GetX())
        self._end_time = self.GetTimeAt(evt.GetX())

    def DragPeriodSelect(self, evt):
        if self._period_select:
            self._end_time = self.GetTimeAt(evt.GetX())
            self.SetPeriodSelection(TimePeriod(self._start_time, self._end_time))

    def StopDragPeriodSelect(self):
        self._period_select = False
        self.SetPeriodSelection(None)
        return self._start_time, self._end_time

    def InitDrag(self, scroll=None, zoom=None, period_select=None, event_select=None):

        def init_scroll():
            if self.BOTH & scroll:
                self.InitDragScroll(direction=wx.BOTH)
                self._drag_scroll = scroll - self.BOTH
            elif self.HORIZONTAL & scroll:
                self.InitDragScroll(direction=wx.HORIZONTAL)
                self._drag_scroll = scroll - self.HORIZONTAL
            elif self.VERTICAL & scroll:
                self.InitDragScroll(direction=wx.VERTICAL)
                self._drag_scroll = scroll - self.VERTICAL
            else:
                self._drag_scroll = None
            if self._drag_scroll is not None:
                self._methods[self._drag_scroll] = (self.StartDragScroll,
                                                    self.DragScroll,
                                                    self.StopDragScroll)

        def init_zoom():
            if zoom not in self._methods:
                self.InitZoomSelect()
                self._methods[zoom] = (self.StartZoomSelect,
                                       self.DragZoom,
                                       self.StopDragZoom)

        def init_period_select():
            if not period_select in self._methods:
                self.InitDragPeriodSelect()
                self._methods[period_select] = (self.StartDragPeriodSelect,
                                                self.DragPeriodSelect,
                                                self.StopDragPeriodSelect)

        def init_event_select():
            if not event_select in self._methods:
                self.InitDragEventSelect()
                self._methods[event_select] = (self.StartDragEventSelect,
                                               self.DragEventSelect,
                                               self.StopDragEventSelect)

        self._drag_scroll = scroll
        self._drag_zoom = zoom
        self._drag_period_select = period_select
        self._drag_event_select = event_select
        self._methods = {}

        if scroll:
            init_scroll()
        if zoom:
            init_zoom()
        if period_select:
            init_period_select()
        if event_select:
            init_event_select()

    def CallDragMethod(self, index, evt):

        def calc_cotrol_keys_value(evt):
            combo = 0
            if evt.ControlDown():
                combo += Keyboard.CTRL
            if evt.ShiftDown():
                combo += Keyboard.SHIFT
            if evt.AltDown():
                combo += Keyboard.ALT
            return combo

        combo = calc_cotrol_keys_value(evt)
        if combo in self._methods:
            if index == self.STOP:
                self._methods[combo][index]()
            else:
                self._methods[combo][index](evt)

    def GetPeriodChoices(self):
        return self._controller.get_period_choices()

    @property
    def view_properties(self):
        return self._controller.view_properties

    # ------------

    def _scroll_up(self):
        self.SetHScrollAmount(max(0, self.GetHScrollAmount() - HSCROLL_STEP))

    def _scroll_down(self):
        self.SetHScrollAmount(self.GetHScrollAmount() + HSCROLL_STEP)

    def _get_half_width(self):
        return self.GetSize()[0] // 2

    def _create_gui(self):
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

    def _on_erase_background(self, event):
        # For double buffering
        pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        if self._surface_bitmap:
            dc.DrawBitmap(self._surface_bitmap, 0, 0, True)
        else:
            pass  # TODO: Fill with white?

    def _on_size(self, evt):
        self._controller.window_resized()

    def HighligtEvent(self, event, clear=False):
        self._controller.add_highlight(event, clear)
        self._highlight_timer.start_highlighting()

    def _highlight_timer_tick(self):
        self.Redraw()
        self._controller.tick_highlights()
        if not self._controller.has_higlights():
            self._highlight_timer.Stop()
