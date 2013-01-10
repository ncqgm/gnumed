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


import math
import os.path

import wx

from timelinelib.config.paths import ICONS_DIR
from timelinelib.db.objects.category import sort_categories
from timelinelib.drawing.interface import Drawer
from timelinelib.drawing.scene import TimelineScene
from timelinelib.drawing.utils import darken_color
from timelinelib.drawing.utils import get_default_font


OUTER_PADDING = 5 # Space between event boxes (pixels)
INNER_PADDING = 3 # Space inside event box to text (pixels)
PERIOD_THRESHOLD = 20  # Periods smaller than this are drawn as events (pixels)
BALLOON_RADIUS = 12
DATA_INDICATOR_SIZE = 10
CONTRAST_RATIO_THREASHOLD = 2250
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class DefaultDrawingAlgorithm(Drawer):

    def __init__(self):
        self._create_fonts()
        self._create_pens()
        self._create_brushes()
        self.fast_draw = False

    def _create_fonts(self):
        self.header_font = get_default_font(12, True)
        self.small_text_font = get_default_font(8)
        self.small_text_font_bold = get_default_font(8, True)

    def _create_pens(self):
        self.red_solid_pen = wx.Pen(wx.Color(255,0, 0), 1, wx.SOLID)
        self.black_solid_pen = wx.Pen(wx.Color(0, 0, 0), 1, wx.SOLID)
        self.darkred_solid_pen = wx.Pen(wx.Color(200, 0, 0), 1, wx.SOLID)
        self.black_dashed_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.USER_DASH)
        self.black_dashed_pen.SetDashes([2, 2])
        self.black_dashed_pen.SetCap(wx.CAP_BUTT)
        self.grey_solid_pen = wx.Pen(wx.Color(200, 200, 200), 1, wx.SOLID)
        self.red_solid_pen = wx.Pen(wx.Color(255, 0, 0), 1, wx.SOLID)

    def _create_brushes(self):
        self.white_solid_brush = wx.Brush(wx.Color(255, 255, 255), wx.SOLID)
        self.black_solid_brush = wx.Brush(wx.Color(0, 0, 0), wx.SOLID)
        self.red_solid_brush = wx.Brush(wx.Color(255, 0, 0), wx.SOLID)
        self.lightgrey_solid_brush = wx.Brush(wx.Color(230, 230, 230), wx.SOLID)

    def event_is_period(self, time_period):
        period_width_in_pixels = self.scene.width_of_period(time_period)
        return period_width_in_pixels > PERIOD_THRESHOLD

    def _get_text_extent(self, text):
        self.dc.SetFont(self.small_text_font)
        tw, th = self.dc.GetTextExtent(text)
        return (tw, th)

    def get_closest_overlapping_event(self, event_to_move, up=True):
        return self.scene.get_closest_overlapping_event(event_to_move, up=up)

    def draw(self, dc, timeline, view_properties, config):
        self.config = config
        self.dc = dc
        self.time_type = timeline.get_time_type()
        self.scene = self._create_scene(
            dc.GetSizeTuple(), timeline, view_properties, self._get_text_extent)
        self._perform_drawing(view_properties)
        del self.dc # Program crashes if we don't delete the dc reference.

    def _create_scene(self, size, db, view_properties, get_text_extent_fn):
        scene = TimelineScene(size, db, view_properties, get_text_extent_fn, self.config)
        scene.set_outer_padding(OUTER_PADDING)
        scene.set_inner_padding(INNER_PADDING)
        scene.set_period_threshold(PERIOD_THRESHOLD)
        scene.set_data_indicator_size(DATA_INDICATOR_SIZE)
        scene.create()
        return scene

    def _perform_drawing(self, view_properties):
        if self.fast_draw:
            self._perform_fast_drawing(view_properties)
        else:
            self._perform_normal_drawing(view_properties)

    def _perform_fast_drawing(self, view_properties):
        self._draw_bg(view_properties)
        self._draw_events(view_properties)

    def _perform_normal_drawing(self, view_properties):
        self._draw_period_selection(view_properties)
        self._draw_bg(view_properties)
        self._draw_events(view_properties)
        self._draw_legend(view_properties, self._extract_categories())
        self._draw_ballons(view_properties)

    def snap(self, time, snap_region=10):
        if self._distance_to_left_border(time) < snap_region:
            return self._get_time_at_left_border(time)
        elif self._distance_to_right_border(time)  < snap_region:
            return self._get_time_at_right_border(time)
        else:
            return time

    def _distance_to_left_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return self.scene.distance_between_times(time, left_strip_time)

    def _distance_to_right_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return self.scene.distance_between_times(time, right_strip_time)

    def _get_time_at_left_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return left_strip_time

    def _get_time_at_right_border(self, time):
        left_strip_time, right_strip_time = self._snap_region(time)
        return right_strip_time

    def _snap_region(self, time):
        left_strip_time = self.scene.minor_strip.start(time)
        right_strip_time = self.scene.minor_strip.increment(left_strip_time)
        return (left_strip_time, right_strip_time)

    def snap_selection(self, period_selection):
        start, end = period_selection
        return (self.snap(start), self.snap(end))

    def event_at(self, x, y, alt_down=False):
        container_event = None
        for (event, rect) in self.scene.event_data:
            if rect.Contains(wx.Point(x, y)):
                if event.is_container():
                    if alt_down:
                        return event
                    container_event = event
                else:
                    return event
        return container_event

    def event_with_rect_at(self, x, y, alt_down=False):
        container_event = None
        container_rect = None
        for (event, rect) in self.scene.event_data:
            if rect.Contains(wx.Point(x, y)):
                if event.is_container():
                    if alt_down:
                        return event, rect
                    container_event = event
                    container_rect = rect
                else:
                    return event, rect
        if container_event == None:
            return None
        return container_event, container_rect

    def event_rect(self, evt):
        for (event, rect) in self.scene.event_data:
            if evt == event:
                return rect
        return None

    def balloon_at(self, x, y):
        event = None
        for (event_in_list, rect) in self.balloon_data:
            if rect.Contains(wx.Point(x, y)):
                event = event_in_list
        return event

    def get_time(self, x):
        return self.scene.get_time(x)

    def get_hidden_event_count(self):
        return self.scene.get_hidden_event_count()

    def _draw_period_selection(self, view_properties):
        if not view_properties.period_selection:
            return
        start, end = view_properties.period_selection
        start_x = self.scene.x_pos_for_time(start)
        end_x = self.scene.x_pos_for_time(end)
        self.dc.SetBrush(self.lightgrey_solid_brush)
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawRectangle(start_x, 0,
                              end_x - start_x + 1, self.scene.height)

    def _draw_bg(self, view_properties):
        if self.fast_draw:
            self._draw_fast_bg()
        else:
            self._draw_normal_bg(view_properties)

    def _draw_fast_bg(self):
        self._draw_minor_strips()
        self._draw_divider_line()

    def _draw_normal_bg(self, view_properties):
        self._draw_minor_strips()
        self._draw_major_strips()
        self._draw_divider_line()
        self._draw_now_line()

    def _draw_minor_strips(self):
        for strip_period in self.scene.minor_strip_data:
            self._draw_minor_strip_divider_line_at(strip_period.end_time)
            self._draw_minor_strip_label(strip_period)

    def _draw_minor_strip_divider_line_at(self, time):
        x = self.scene.x_pos_for_time(time)
        self.dc.SetPen(self.black_dashed_pen)
        self.dc.DrawLine(x, 0, x, self.scene.height)

    def _draw_minor_strip_label(self, strip_period):
        label = self.scene.minor_strip.label(strip_period.start_time)
        self.dc.SetFont(self.scene.minor_strip.get_font(strip_period))
        (tw, th) = self.dc.GetTextExtent(label)
        middle = self.scene.x_pos_for_time(strip_period.mean_time())
        middley = self.scene.divider_y
        self.dc.DrawText(label, middle - tw / 2, middley - th)

    def _draw_major_strips(self):
        self.dc.SetFont(self.header_font)
        self.dc.SetPen(self.grey_solid_pen)
        for time_period in self.scene.major_strip_data:
            self._draw_major_strip_end_line(time_period)
            self._draw_major_strip_label(time_period)

    def _draw_major_strip_end_line(self, time_period):
        end_time = self.time_type.adjust_for_bc_years(time_period.end_time) 
        x = self.scene.x_pos_for_time(end_time)
        self.dc.DrawLine(x, 0, x, self.scene.height)

    def _draw_major_strip_label(self, time_period):
        label = self.scene.major_strip.label(time_period.start_time, True)
        x = self._calculate_major_strip_label_x(time_period, label)
        self.dc.DrawText(label, x, INNER_PADDING)

    def _calculate_major_strip_label_x(self, time_period, label):
        (tw, th) = self.dc.GetTextExtent(label)
        x = self.scene.x_pos_for_time(time_period.mean_time()) - tw / 2
        if x - INNER_PADDING < 0:
            x = INNER_PADDING
            right = self.scene.x_pos_for_time(time_period.end_time)
            if x + tw + INNER_PADDING > right:
                x = right - tw - INNER_PADDING
        elif x + tw + INNER_PADDING > self.scene.width:
            x = self.scene.width - tw - INNER_PADDING
            left = self.scene.x_pos_for_time(time_period.start_time)
            if x < left + INNER_PADDING:
                x = left + INNER_PADDING
        return x

    def _draw_divider_line(self):
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawLine(0, self.scene.divider_y, self.scene.width,
                         self.scene.divider_y)

    def _draw_lines_to_non_period_events(self, view_properties):
        for (event, rect) in self.scene.event_data:
            if self._invisible_container_subevent(event, rect):
                continue
            if self._event_displayed_as_point_event(rect):
                self._draw_line(view_properties, event, rect)

    def _invisible_container_subevent(self, event, rect):
        return (self._subevent_displayed_as_point_event(event, rect) and
                event.is_period())

    def _event_displayed_as_point_event(self, rect):
        return self.scene.divider_y > rect.Y

    def _draw_line(self, view_properties, event, rect):
        x = self.scene.x_pos_for_time(event.mean_time())
        y = rect.Y + rect.Height
        y2 = self._get_end_of_line(event)
        self._set_line_color(view_properties, event)
        self.dc.DrawLine(x, y, x, y2)
        self.dc.DrawCircle(x, y2, 2)

    def _get_end_of_line(self, event):
        if self._point_subevent(event):
            y = self._get_container_y(event.container_id)
        else:
            y = self.scene.divider_y
        return y

    def _point_subevent(self, event):
        return event.is_subevent() and not event.is_period()

    def _get_container_y(self, id):
        for (event, rect) in self.scene.event_data:
            if event.is_container():
                if event.container_id == id:
                    return rect.y - 1
        return self.scene.divider_y

    def _set_line_color(self, view_properties, event):
        if view_properties.is_selected(event):
            self.dc.SetPen(self.red_solid_pen)
            self.dc.SetBrush(self.red_solid_brush)
        else:
            self.dc.SetBrush(self.black_solid_brush)
            self.dc.SetPen(self.black_solid_pen)

    def _draw_now_line(self):
        now_time = self.time_type.now()
        x = self.scene.x_pos_for_time(now_time)
        if x > 0 and x < self.scene.width:
            self.dc.SetPen(self.darkred_solid_pen)
            self.dc.DrawLine(x, 0, x, self.scene.height)

    def _extract_categories(self):
        categories = []
        for (event, rect) in self.scene.event_data:
            cat = event.category
            if cat and not cat in categories:
                categories.append(cat)
        return sort_categories(categories)

    def _draw_legend(self, view_properties, categories):
        if self._legend_should_be_drawn(view_properties, categories):
            self.dc.SetFont(self.small_text_font)
            rect = self._calculate_legend_rect(categories)
            self._draw_legend_box(rect)
            self._draw_legend_items(rect, categories)

    def _legend_should_be_drawn(self, view_properties, categories):
        return view_properties.show_legend and len(categories) > 0

    def _calculate_legend_rect(self, categories):
        max_width = 0
        height = INNER_PADDING
        for cat in categories:
            tw, th = self.dc.GetTextExtent(cat.name)
            height = height + th + INNER_PADDING
            if tw > max_width:
                max_width = tw
        item_height = self._text_height_with_current_font()
        width = max_width + 4 * INNER_PADDING + item_height
        return wx.Rect(OUTER_PADDING,
                       self.scene.height - height - OUTER_PADDING,
                       width,
                       height)

    def _draw_legend_box(self, rect):
        self.dc.SetBrush(self.white_solid_brush)
        self.dc.SetPen(self.black_solid_pen)
        self.dc.DrawRectangleRect(rect)

    def _text_height_with_current_font(self):
        STRING_WITH_MIXED_CAPITALIZATION = "jJ"
        tw, th = self.dc.GetTextExtent(STRING_WITH_MIXED_CAPITALIZATION)
        return th

    def _draw_legend_items(self, rect, categories):
        item_height = self._text_height_with_current_font()
        cur_y = rect.Y + INNER_PADDING
        for cat in categories:
            base_color = cat.color
            border_color = darken_color(base_color)
            self.dc.SetBrush(wx.Brush(base_color, wx.SOLID))
            self.dc.SetPen(wx.Pen(border_color, 1, wx.SOLID))
            color_box_rect = (OUTER_PADDING + rect.Width - item_height -
                              INNER_PADDING,
                              cur_y, item_height, item_height)
            self.dc.DrawRectangleRect(color_box_rect)
            self.dc.SetTextForeground((0, 0, 0))
            self.dc.DrawText(cat.name, OUTER_PADDING + INNER_PADDING, cur_y)
            cur_y = cur_y + item_height + INNER_PADDING

    def _draw_events(self, view_properties):
        """Draw all event boxes and the text inside them."""
        self.dc.SetFont(self.small_text_font)
        self.dc.DestroyClippingRegion()
        self._draw_lines_to_non_period_events(view_properties)
        for (event, rect) in self.scene.event_data:
            if event.is_container():
                self._draw_container(event, rect, view_properties)
            else:
                self._draw_event(event, rect, view_properties)

    def _draw_container(self, event, rect, view_properties):
        box_rect = wx.Rect(rect.X - 2, rect.Y - 2, rect.Width + 4, rect.Height + 4)
        self._draw_box(box_rect, event)
        if self._event_displayed_as_point_event(rect):
            self._draw_text(rect, event)
        if view_properties.is_selected(event):
            self._draw_selection_and_handles(rect, event)

    def _draw_event(self, event, rect, view_properties):
        if self._subevent_displayed_as_point_event(event, rect):
            if event.is_period():
                return
        self._draw_box(rect, event)
        self._draw_text(rect, event)
        if event.has_data():
            self._draw_contents_indicator(event, rect)
        if view_properties.is_selected(event):
            self._draw_selection_and_handles(rect, event)

    def _subevent_displayed_as_point_event(self, event, rect):
        return (event.is_subevent() and
                self._event_displayed_as_point_event(rect))

    def _draw_box(self, rect, event):
        self.dc.SetClippingRect(rect)
        self.dc.SetBrush(self._get_box_brush(event))
        self.dc.SetPen(self._get_box_pen(event))
        self.dc.DrawRectangleRect(rect)
        if event.fuzzy:
            self._draw_fuzzy_edges(rect, event)
        if event.locked:
            self._draw_locked_edges(rect, event)
        self.dc.DestroyClippingRegion()

    def _draw_fuzzy_edges(self, rect, event):
        self._draw_fuzzy_start(rect, event)
        self._draw_fuzzy_end(rect, event)

    def _draw_fuzzy_start(self, rect, event):
        """
          p1     /p2 ----------
                /
          p3  <
                \
          p4     \p5 ----------
        """
        x1 = rect.x
        x2 = rect.x + rect.height / 2
        y1 = rect.y
        y2 = rect.y + rect.height / 2
        y3 = rect.y + rect.height
        p1 = wx.Point(x1, y1)
        p2 = wx.Point(x2, y1)
        p3 = wx.Point(x1, y2)
        p4 = wx.Point(x1, y3)
        p5 = wx.Point(x2, y3)
        self.draw_fuzzy(event, p1, p2, p3, p4, p5)

    def _draw_fuzzy_end(self, rect, event):
        """
          ---- P2\    p1
                  \
                   >  p3
                  /
          ---- p4/    p4
        """
        x1 = rect.x + rect.width - rect.height / 2
        x2 = rect.x + rect.width
        y1 = rect.y
        y2 = rect.y + rect.height / 2
        y3 = rect.y + rect.height
        p1 = wx.Point(x2, y1)
        p2 = wx.Point(x1, y1)
        p3 = wx.Point(x2, y2)
        p4 = wx.Point(x2, y3)
        p5 = wx.Point(x1, y3)
        self.draw_fuzzy(event, p1, p2, p3, p4, p5)

    def draw_fuzzy(self, event, p1, p2, p3, p4, p5):
        self._draw_fuzzy_polygon(p1, p2 ,p3)
        self._draw_fuzzy_polygon(p3, p4 ,p5)
        self._draw_fuzzy_border(event, p2, p3, p5)

    def _draw_fuzzy_polygon(self, p1, p2 ,p3):
        self.dc.SetBrush(wx.WHITE_BRUSH)
        self.dc.SetPen(wx.WHITE_PEN)
        self.dc.DrawPolygon((p1, p2, p3))

    def _draw_fuzzy_border(self, event, p1, p2, p3):
        gc = wx.GraphicsContext.Create(self.dc)
        path = gc.CreatePath()
        path.MoveToPoint(p1.x, p1.y)
        path.AddLineToPoint(p2.x, p2.y)
        path.AddLineToPoint(p3.x, p3.y)
        gc.SetPen(self._get_box_pen(event))
        gc.StrokePath(path)

    def _draw_locked_edges(self, rect, event):
        self._draw_locked_start(event, rect)
        self._draw_locked_end(event, rect)

    def _draw_locked_start(self, event, rect):
        x = rect.x
        if event.fuzzy:
            start_angle = -math.pi / 4
            end_angle = math.pi / 4
        else:
            start_angle = -math.pi
            end_angle = math.pi
        self._draw_locked(event, rect, x, start_angle, end_angle)

    def _draw_locked_end(self, event, rect):
        x = rect.x + rect.width
        if event.fuzzy:
            start_angle = 3 * math.pi / 4
            end_angle = 5 * math.pi / 4
        else:
            start_angle = math.pi / 2
            end_angle = 3 * math.pi / 2
        self._draw_locked(event, rect, x, start_angle, end_angle)

    def _draw_locked(self, event, rect, x, start_angle, end_angle):
        y = rect.y + rect.height / 2
        r = rect.height / 2.5
        self.dc.SetBrush(wx.WHITE_BRUSH)
        self.dc.SetPen(wx.WHITE_PEN)
        self.dc.DrawCircle(x, y, r)
        self.dc.SetPen(self._get_box_pen(event))
        self.draw_segment(event, x, y, r, start_angle, end_angle)

    def draw_segment(self, event, x0, y0, r, start_angle, end_angle):
        gc = wx.GraphicsContext.Create(self.dc)
        path = gc.CreatePath()
        segment_length = 2.0 * (end_angle - start_angle) * r
        delta = (end_angle - start_angle) / segment_length
        angle = start_angle
        x1 = r * math.cos(angle) + x0
        y1 = r * math.sin(angle) + y0
        path.MoveToPoint(x1, y1)
        while angle < end_angle:
            angle += delta
            if angle > end_angle:
                angle = end_angle
            x2 = r * math.cos(angle) + x0
            y2 = r * math.sin(angle) + y0
            path.AddLineToPoint(x2, y2)
            x1 = x2
            y1 = y2
        gc.SetPen(self._get_box_pen(event))
        gc.StrokePath(path)

    def _draw_text(self, rect, event):
        # Ensure that we can't draw content outside inner rectangle
        rect_copy = wx.Rect(*rect)
        rect_copy.Deflate(INNER_PADDING, INNER_PADDING)
        if rect_copy.Width > 0:
            # Draw the text (if there is room for it)
            self.dc.SetClippingRect(rect_copy)
            text_x = rect.X + INNER_PADDING
            if event.fuzzy or event.locked:
                text_x += rect.Height / 2
            text_y = rect.Y + INNER_PADDING
            if text_x < INNER_PADDING:
                text_x = INNER_PADDING
            self._set_text_foreground_color(event)
            self.dc.DrawText(event.text, text_x, text_y)
            self.dc.DestroyClippingRegion()

    def _set_text_foreground_color(self, event):
        if event.category is None:
            fg_color = BLACK
        elif event.category.font_color is None:
            fg_color = BLACK
        else:
            font_color = event.category.font_color
            fg_color = wx.Color(font_color[0], font_color[1], font_color[2])
        self.dc.SetTextForeground(fg_color)

    def _draw_contents_indicator(self, event, rect):
        """
        The data contents indicator is a small triangle drawn in the upper
        right corner of the event rectangle.
        """
        self.dc.SetClippingRect(rect)
        corner_x = rect.X + rect.Width
        if corner_x > self.scene.width:
            corner_x = self.scene.width
        points = (
            wx.Point(corner_x - DATA_INDICATOR_SIZE, rect.Y),
            wx.Point(corner_x, rect.Y),
            wx.Point(corner_x, rect.Y + DATA_INDICATOR_SIZE),
        )
        self.dc.SetBrush(self._get_box_indicator_brush(event))
        self.dc.SetPen(wx.TRANSPARENT_PEN)
        self.dc.DrawPolygon(points)
        self.dc.DestroyClippingRegion()

    def _draw_selection_and_handles(self, rect, event):
        self.dc.SetClippingRect(rect)
        small_rect = wx.Rect(*rect)
        small_rect.Deflate(1, 1)
        border_color = self._get_border_color(event)
        border_color = darken_color(border_color)
        pen = wx.Pen(border_color, 1, wx.SOLID)
        self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        self.dc.SetPen(pen)
        self.dc.DrawRectangleRect(small_rect)
        self._draw_handles(rect, event)
        self.dc.DestroyClippingRegion()

    def _draw_handles(self, rect, event):
        SIZE = 4
        big_rect = wx.Rect(rect.X - SIZE, rect.Y - SIZE, rect.Width + 2 * SIZE, rect.Height + 2 * SIZE)
        self.dc.DestroyClippingRegion()
        self.dc.SetClippingRect(big_rect)
        y = rect.Y + rect.Height/2 - SIZE/2
        x = rect.X - SIZE / 2
        west_rect   = wx.Rect(x + 1             , y, SIZE, SIZE)
        center_rect = wx.Rect(x + rect.Width / 2, y, SIZE, SIZE)
        east_rect   = wx.Rect(x + rect.Width - 1, y, SIZE, SIZE)
        self.dc.SetBrush(wx.Brush("BLACK", wx.SOLID))
        self.dc.SetPen(wx.Pen("BLACK", 1, wx.SOLID))
        if not event.locked:
            self.dc.DrawRectangleRect(east_rect)
            self.dc.DrawRectangleRect(west_rect)
        if not event.locked and not event.ends_today:
            self.dc.DrawRectangleRect(center_rect)

    def _get_base_color(self, event):
        if event.category:
            base_color = event.category.color
        else:
            base_color = (200, 200, 200)
        return base_color

    def _get_border_color(self, event):
        base_color = self._get_base_color(event)
        border_color = darken_color(base_color)
        return border_color

    def _get_box_pen(self, event):
        border_color = self._get_border_color(event)
        pen = wx.Pen(border_color, 1, wx.SOLID)
        return pen

    def _get_box_brush(self, event):
        base_color = self._get_base_color(event)
        brush = wx.Brush(base_color, wx.SOLID)
        return brush

    def _get_box_indicator_brush(self, event):
        base_color = self._get_base_color(event)
        darker_color = darken_color(base_color, 0.6)
        brush = wx.Brush(darker_color, wx.SOLID)
        return brush

    def _get_selected_box_brush(self, event):
        border_color = self._get_border_color(event)
        brush = wx.Brush(border_color, wx.BDIAGONAL_HATCH)
        return brush

    def _draw_ballons(self, view_properties):
        """Draw ballons on selected events that has 'description' data."""
        self.balloon_data = []     # List of (event, rect)
        top_event = None
        top_rect = None
        self.dc.SetTextForeground(BLACK)
        for (event, rect) in self.scene.event_data:
            if (event.get_data("description") != None or
                event.get_data("icon") != None):
                sticky = view_properties.event_has_sticky_balloon(event)
                if (view_properties.event_is_hovered(event) or sticky):
                    if not sticky:
                        top_event, top_rect = event, rect
                    self._draw_ballon(event, rect, sticky)
        # Make the unsticky balloon appear on top
        if top_event is not None:
            self._draw_ballon(top_event, top_rect, False)

    def _draw_ballon(self, event, event_rect, sticky):
        """Draw one ballon on a selected event that has 'description' data."""
        # Constants
        MIN_TEXT_WIDTH = 200
        MIN_WIDTH = 100
        SLIDER_WIDTH = 20

        inner_rect_w = 0
        inner_rect_h = 0
        # Icon
        (iw, ih) = (0, 0)
        icon = event.get_data("icon")
        if icon != None:
            (iw, ih) = icon.Size
            inner_rect_w = iw
            inner_rect_h = ih
        max_text_width = max(MIN_TEXT_WIDTH, (self.scene.width - SLIDER_WIDTH - event_rect.X - iw))
        # Text
        self.dc.SetFont(get_default_font(8))
        font_h = self.dc.GetCharHeight()
        (tw, th) = (0, 0)
        description = event.get_data("description")
        lines = None
        if description != None:
            lines = break_text(description, self.dc, max_text_width)
            th = len(lines) * self.dc.GetCharHeight()
            for line in lines:
                (lw, lh) = self.dc.GetTextExtent(line)
                tw = max(lw, tw)
            if icon != None:
                inner_rect_w += BALLOON_RADIUS
            inner_rect_w += min(tw, max_text_width)
            inner_rect_h = max(inner_rect_h, th)
        inner_rect_w = max(MIN_WIDTH, inner_rect_w)
        bounding_rect, x, y = self._draw_balloon_bg(
            self.dc, (inner_rect_w, inner_rect_h),
            (event_rect.X + event_rect.Width / 2,
            event_rect.Y),
            True, sticky)
        if icon != None:
            self.dc.DrawBitmap(icon, x, y, False)
            x += iw + BALLOON_RADIUS
        if lines != None:
            ty = y
            for line in lines:
                self.dc.DrawText(line, x, ty)
                ty += font_h
            x += tw
        # Write data so we know where the balloon was drawn
        # Following two lines can be used when debugging the rectangle
        #self.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        #self.dc.DrawRectangleRect(bounding_rect)
        self.balloon_data.append((event, bounding_rect))

    def _draw_balloon_bg(self, dc, inner_size, tip_pos, above, sticky):
        """
        Draw the balloon background leaving inner_size for content.

        tip_pos determines where the tip of the ballon should be.

        above determines if the balloon should be above the tip (True) or below
        (False). This is not currently implemented.

                    W
           |----------------|
             ______________           _
            /              \          |             R = Corner Radius
           |                |         |            AA = Left Arrow-leg angle
           |  W_ARROW       |         |  H     MARGIN = Text margin
           |     |--|       |         |             * = Starting point
            \____    ______/          _
                /  /                  |
               /_/                    |  H_ARROW
              *                       -
           |----|
           ARROW_OFFSET

        Calculation of points starts at the tip of the arrow and continues
        clockwise around the ballon.

        Return (bounding_rect, x, y) where x and y is at top of inner region.
        """
        # Prepare path object
        gc = wx.GraphicsContext.Create(self.dc)
        path = gc.CreatePath()
        # Calculate path
        R = BALLOON_RADIUS
        W = 1 * R + inner_size[0]
        H = 1 * R + inner_size[1]
        H_ARROW = 14
        W_ARROW = 15
        W_ARROW_OFFSET = R + 25
        AA = 20
        # Starting point at the tip of the arrow
        (tipx, tipy) = tip_pos
        p0 = wx.Point(tipx, tipy)
        path.MoveToPoint(p0.x, p0.y)
        # Next point is the left base of the arrow
        p1 = wx.Point(p0.x + H_ARROW * math.tan(math.radians(AA)),
                      p0.y - H_ARROW)
        path.AddLineToPoint(p1.x, p1.y)
        # Start of lower left rounded corner
        p2 = wx.Point(p1.x - W_ARROW_OFFSET + R, p1.y)
        path.AddLineToPoint(p2.x, p2.y)
        # The lower left rounded corner. p3 is the center of the arc
        p3 = wx.Point(p2.x, p2.y - R)
        path.AddArc(p3.x, p3.y, R, math.radians(90), math.radians(180))
        # The left side
        p4 = wx.Point(p3.x - R, p3.y - H + R)
        left_x = p4.x
        path.AddLineToPoint(p4.x, p4.y)
        # The upper left rounded corner. p5 is the center of the arc
        p5 = wx.Point(p4.x + R, p4.y)
        path.AddArc(p5.x, p5.y, R, math.radians(180), math.radians(-90))
        # The upper side
        p6 = wx.Point(p5.x + W - R, p5.y - R)
        top_y = p6.y
        path.AddLineToPoint(p6.x, p6.y)
        # The upper right rounded corner. p7 is the center of the arc
        p7 = wx.Point(p6.x, p6.y + R)
        path.AddArc(p7.x, p7.y, R, math.radians(-90), math.radians(0))
        # The right side
        p8 = wx.Point(p7.x + R , p7.y + H - R)
        path.AddLineToPoint(p8.x, p8.y)
        # The lower right rounded corner. p9 is the center of the arc
        p9 = wx.Point(p8.x - R, p8.y)
        path.AddArc(p9.x, p9.y, R, math.radians(0), math.radians(90))
        # The lower side
        p10 = wx.Point(p9.x - W + W_ARROW +  W_ARROW_OFFSET, p9.y + R)
        path.AddLineToPoint(p10.x, p10.y)
        path.CloseSubpath()
        # Draw sharp lines on GTK which uses Cairo
        # See: http://www.cairographics.org/FAQ/#sharp_lines
        gc.Translate(0.5, 0.5)
        # Draw the ballon
        BORDER_COLOR = wx.Color(127, 127, 127)
        BG_COLOR = wx.Color(255, 255, 231)
        PEN = wx.Pen(BORDER_COLOR, 1, wx.SOLID)
        BRUSH = wx.Brush(BG_COLOR, wx.SOLID)
        gc.SetPen(PEN)
        gc.SetBrush(BRUSH)
        gc.DrawPath(path)
        # Draw the pin
        if sticky:
            pin = wx.Bitmap(os.path.join(ICONS_DIR, "stickypin.png"))
        else:
            pin = wx.Bitmap(os.path.join(ICONS_DIR, "unstickypin.png"))
        self.dc.DrawBitmap(pin, p7.x -5, p6.y + 5, True)

        # Return
        bx = left_x
        by = top_y
        bw = W + R + 1
        bh = H + R + H_ARROW + 1
        bounding_rect = wx.Rect(bx, by, bw, bh)
        return (bounding_rect, left_x + BALLOON_RADIUS, top_y + BALLOON_RADIUS)


def break_text(text, dc, max_width_in_px):
    """ Break the text into lines so that they fits within the given width."""
    sentences = text.split("\n")
    lines = []
    for sentence in sentences:
        w, h = dc.GetTextExtent(sentence)
        if w <= max_width_in_px:
            lines.append(sentence)
        # The sentence is too long. Break it.
        else:
            break_sentence(dc, lines, sentence, max_width_in_px);
    return lines


def break_sentence(dc, lines, sentence, max_width_in_px):
    """Break a sentence into lines."""
    line = []
    max_word_len_in_ch = get_max_word_length(dc, max_width_in_px)
    words = break_line(dc, sentence, max_word_len_in_ch)
    for word in words:
        w, h = dc.GetTextExtent("".join(line) + word + " ")
        # Max line length reached. Start a new line
        if w > max_width_in_px:
            lines.append("".join(line))
            line = []
        line.append(word + " ")
        # Word edning with '-' is a broken word. Start a new line
        if word.endswith('-'):
            lines.append("".join(line))
            line = []
    if len(line) > 0:
        lines.append("".join(line))


def break_line(dc, sentence, max_word_len_in_ch):
    """Break a sentence into words."""
    words = sentence.split(" ")
    new_words = []
    for word in words:
        broken_words = break_word(dc, word, max_word_len_in_ch)
        for broken_word in broken_words:
            new_words.append(broken_word)
    return new_words


def break_word(dc, word, max_word_len_in_ch):
    """
    Break words if they are too long.

    If a single word is too long to fit we have to break it.
    If not we just return the word given.
    """
    words = []
    while len(word) > max_word_len_in_ch:
        word1 = word[0:max_word_len_in_ch] + "-"
        word =  word[max_word_len_in_ch:]
        words.append(word1)
    words.append(word)
    return words


def get_max_word_length(dc, max_width_in_px):
    TEMPLATE_CHAR = 'K'
    word = [TEMPLATE_CHAR]
    w, h = dc.GetTextExtent("".join(word))
    while w < max_width_in_px:
        word.append(TEMPLATE_CHAR)
        w, h = dc.GetTextExtent("".join(word))
    return len(word) - 1
