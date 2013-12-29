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

from timelinelib.drawing import get_drawer
from timelinelib.view.drawingarea import DrawingArea
from timelinelib.wxgui.dialogs.duplicateevent import open_duplicate_event_dialog_for_event
from timelinelib.wxgui.dialogs.eventeditor import open_create_event_editor
from timelinelib.wxgui.dialogs.eventeditor import open_event_editor_for
from timelinelib.wxgui.utils import _ask_question


class DrawingAreaPanel(wx.Panel):

    def __init__(self, parent, status_bar_adapter, divider_line_slider,
                 fn_handle_db_error, config, main_frame):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self.fn_handle_db_error = fn_handle_db_error
        self.config = config
        self.main_frame = main_frame
        self.controller = DrawingArea(
            self, status_bar_adapter, config, get_drawer(),
            divider_line_slider, fn_handle_db_error)
        self.surface_bitmap = None
        self._create_gui()

    def get_drawer(self):
        return self.controller.get_drawer()

    def get_timeline(self):
        return self.controller.get_timeline()

    def get_view_properties(self):
        return self.controller.get_view_properties()

    def get_current_image(self):
        return self.surface_bitmap

    def get_filtered_events(self, search_target):
        events = self.get_timeline().search(search_target)
        return self.get_view_properties().filter_events(events)
        
    def set_timeline(self, timeline):
        self.controller.set_timeline(timeline)

    def show_hide_legend(self, show):
        self.controller.show_hide_legend(show)

    def get_time_period(self):
        return self.controller.get_time_period()

    def navigate_timeline(self, navigation_fn):
        self.controller.navigate_timeline(navigation_fn)

    def redraw_timeline(self):
        self.controller.redraw_timeline()

    def balloon_visibility_changed(self, visible):
        self.controller.balloon_visibility_changed(visible)

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

    def enable_disable_menus(self):
        self.main_frame.enable_disable_menus()

    def open_event_editor_for(self, event):
        open_event_editor_for(
            self,
            self.config,
            self.controller.get_timeline(),
            self.fn_handle_db_error,
            event)

    def open_duplicate_event_dialog_for_event(self, event):
        open_duplicate_event_dialog_for_event(
            self,
            self.controller.get_timeline(),
            self.fn_handle_db_error,
            event)

    def open_create_event_editor(self, start_time, end_time):
        open_create_event_editor(
            self,
            self.config,
            self.controller.get_timeline(),
            self.fn_handle_db_error,
            start_time,
            end_time)

    def start_balloon_show_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_show_timer.Start(milliseconds, oneShot)

    def start_balloon_hide_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_hide_timer.Start(milliseconds, oneShot)

    def start_dragscroll_timer(self, milliseconds=-1, oneShot=False):
        self.dragscroll_timer.Start(milliseconds, oneShot)

    def stop_dragscroll_timer(self):
        self.dragscroll_timer.Stop()

    def set_select_period_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))

    def set_size_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def set_move_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))

    def set_default_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def ask_question(self, question):
        return _ask_question(question, self)

    def ok_to_edit(self):
        return self.main_frame.ok_to_edit()
    
    def edit_ends(self):
        self.SetFocusIgnoringChildren()
        return self.main_frame.edit_ends()

    def zoom_in(self):
        self.controller.mouse_wheel_moved(120, True, False, False, self._get_half_width())
    
    def zoom_out(self):
        self.controller.mouse_wheel_moved(-120, True, False, False, self._get_half_width())

    def vert_zoom_in(self):
        self.controller.mouse_wheel_moved(120, False, False, True, self._get_half_width())
    
    def vert_zoom_out(self):
        self.controller.mouse_wheel_moved(-120, False, False, True, self._get_half_width())

    def _get_half_width(self):
        return self.GetSize()[0] / 2
        
    def _create_gui(self):
        self.balloon_show_timer = wx.Timer(self, -1)
        self.balloon_hide_timer = wx.Timer(self, -1)
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_show_timer, self.balloon_show_timer)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_hide_timer, self.balloon_hide_timer)
        self.Bind(wx.EVT_TIMER,            self._on_dragscroll, self.dragscroll_timer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_PAINT,            self._on_paint)
        self.Bind(wx.EVT_SIZE,             self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN,        self._on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN,       self._on_right_down)
        self.Bind(wx.EVT_LEFT_DCLICK,      self._on_left_dclick)
        self.Bind(wx.EVT_MIDDLE_UP,        self._on_middle_up)
        self.Bind(wx.EVT_LEFT_UP,          self._on_left_up)
        self.Bind(wx.EVT_ENTER_WINDOW,     self._on_enter)
        self.Bind(wx.EVT_MOTION,           self._on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL,       self._on_mousewheel)
        self.Bind(wx.EVT_KEY_DOWN,         self._on_key_down)
        self.Bind(wx.EVT_KEY_UP,           self._on_key_up)

    def _on_balloon_show_timer(self, evt):
        self.controller.balloon_show_timer_fired()

    def _on_balloon_hide_timer(self, evt):
        self.controller.balloon_hide_timer_fired()

    def _on_dragscroll(self, evt):
        self.controller.dragscroll_timer_fired()

    def _on_erase_background(self, event):
        # For double buffering
        pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        if self.surface_bitmap:
            dc.DrawBitmap(self.surface_bitmap, 0, 0, True)
        else:
            pass # TODO: Fill with white?
        dc.EndDrawing()

    def _on_size(self, evt):
        self.controller.window_resized()

    def _on_left_down(self, evt):
        self.controller.left_mouse_down(evt.GetX(), evt.GetY(), evt.ControlDown(),
                                        evt.ShiftDown(), evt.AltDown())
        evt.Skip()

    def _on_right_down(self, evt):
        self.controller.right_mouse_down(evt.GetX(), evt.GetY(), evt.AltDown())

    def _on_left_dclick(self, evt):
        self.controller.left_mouse_dclick(evt.GetX(), evt.GetY(), evt.ControlDown(),
                                          evt.AltDown())

    def _on_middle_up(self, evt):
        self.controller.middle_mouse_clicked(evt.GetX())

    def _on_left_up(self, evt):
        self.controller.left_mouse_up()

    def _on_enter(self, evt):
        self.controller.mouse_enter(evt.GetX(), evt.LeftIsDown())

    def _on_motion(self, evt):
        self.controller.mouse_moved(evt.GetX(), evt.GetY(), evt.AltDown())

    def _on_mousewheel(self, evt):
        self.controller.mouse_wheel_moved(evt.GetWheelRotation(), evt.ControlDown(), evt.ShiftDown(), evt.AltDown(), evt.GetX())

    def _on_key_down(self, evt):
        self.controller.key_down(evt.GetKeyCode(), evt.AltDown())
        evt.Skip()

    def _on_key_up(self, evt):
        self.controller.key_up(evt.GetKeyCode())
