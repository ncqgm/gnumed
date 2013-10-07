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

from timelinelib.drawing.utils import Metrics
from timelinelib.db.objects import TimePeriod


FORWARD  = 1
BACKWARD = -1

class TimelineScene(object):

    def __init__(self, size, db, view_properties, get_text_size_fn, config):
        self._db = db
        self._view_properties = view_properties
        self._get_text_size = get_text_size_fn
        self._config = config
        self._outer_padding = 5
        self._inner_padding = 3
        self._baseline_padding = 15
        self._period_threshold = 20
        self._data_indicator_size = 10
        self._metrics = Metrics(size, self._db.get_time_type(),
                                self._view_properties.displayed_period,
                                self._view_properties.divider_position)
        self.width, self.height = size
        self.divider_y = self._metrics.half_height
        self.event_data = []
        self.major_strip = None
        self.minor_strip = None
        self.major_strip_data = []
        self.minor_strip_data = []

    def set_outer_padding(self, outer_padding):
        self._outer_padding = outer_padding

    def set_inner_padding(self, inner_padding):
        self._inner_padding = inner_padding

    def set_baseline_padding(self, baseline_padding):
        self._baseline_padding = baseline_padding

    def set_period_threshold(self, period_threshold):
        self._period_threshold = period_threshold

    def set_data_indicator_size(self, data_indicator_size):
        self._data_indicator_size = data_indicator_size

    def create(self):
        self._calc_event_positions()
        self._calc_strips()

    def x_pos_for_time(self, time):
        return self._metrics.calc_x(time)

    def x_pos_for_now(self):
        now = self._db.get_time_type().now()
        return self._metrics.calc_x(now)

    def get_time(self, x):
        return self._metrics.get_time(x)

    def distance_between_times(self, time1, time2):
        time1_x = self._metrics.calc_exact_x(time1)
        time2_x = self._metrics.calc_exact_x(time2)
        distance = abs(time1_x - time2_x)
        return distance

    def width_of_period(self, time_period):
        return self._metrics.calc_width(time_period)

    def get_closest_overlapping_event(self, selected_event, up=True):
        rect = self._get_event_rect(selected_event)
        period = self._event_rect_drawn_as_period(rect)
        direction = self._get_direction(period, up)
        evt = self._get_overlapping_event(period, direction, selected_event, rect)
        return (evt, direction)

    def _get_event_rect(self, event):
        for (evt, rect) in self.event_data:
            if evt == event:
                return rect
        return None

    def _event_rect_drawn_as_period(self, event_rect):
        return event_rect.Y >= self.divider_y

    def _get_direction(self, period, up):
        if up:
            if period:
                direction = BACKWARD
            else:
                direction = FORWARD
        else:
            if period:
                direction = FORWARD
            else:
                direction = BACKWARD
        return direction

    def _get_overlapping_event(self, period, direction, selected_event, rect):
        list = self._get_overlapping_events_list(period, rect)
        event = self._get_overlapping_event_from_list(list, direction,
                                                      selected_event)
        return event

    def _get_overlapping_events_list(self, period, rect):
        if period:
            list = self._get_list_with_overlapping_period_events(rect)
        else:
            list = self._get_list_with_overlapping_point_events(rect)
        return list

    def _get_overlapping_event_from_list(self, list, direction, selected_event):
        if direction == FORWARD:
            return self._get_next_overlapping_event(list, selected_event)
        else:
            return self._get_prev_overlapping_event(list, selected_event)

    def _get_next_overlapping_event(self, list, selected_event):
        selected_event_found = False
        for (e,r) in list:
            if selected_event_found:
                return e
            else:
                if e == selected_event:
                    selected_event_found = True
        return None

    def _get_prev_overlapping_event(self, list, selected_event):
        prev_event = None
        for (e,r) in list:
            if e == selected_event:
                return prev_event
            prev_event = e

    def _calc_event_positions(self):
        self.events_from_db = self._db.get_events(self._view_properties.displayed_period)
        visible_events = self._view_properties.filter_events(self.events_from_db)
        visible_events = self._place_subevents_last(visible_events)
        self._calc_rects(visible_events)

    def _place_subevents_last(self, events):
        reordered_events = [event  for event in events
                            if not event.is_subevent()]
        subevents = [event for event in events
                     if event.is_subevent()]
        reordered_events.extend(subevents)
        return reordered_events

    def _calc_rects(self, events):
        self.event_data = []
        for event in events:
            rect = self._create_rectangle_for_event(event)
            self.event_data.append((event, rect))
        for (event, rect) in self.event_data:
            rect.Deflate(self._outer_padding, self._outer_padding)

    def _create_rectangle_for_event(self, event):
        if self._period_subevent(event):
            return self._create_rectangle_for_period_subevent(event)
        else:
            return self._create_rectangle_for_possibly_overlapping_event(event)

    def _period_subevent(self, event):
        return event.is_subevent() and event.is_period()

    def _create_rectangle_for_period_subevent(self, event):
        return self._create_ideal_rect_for_event(event)

    def _create_rectangle_for_possibly_overlapping_event(self, event):
        rect = self._create_ideal_rect_for_event(event)
        self._ensure_rect_is_not_far_outisde_screen(rect)
        self._prevent_overlapping_by_adjusting_rect_y(event, rect)
        return rect

    def _create_ideal_rect_for_event(self, event):
        if event.ends_today:
            event.time_period.end_time = self._db.get_time_type().now()
        if self._display_as_period(event) or event.is_subevent():
            if self._display_as_period(event):
                return self._create_ideal_rect_for_period_event(event)
            else:
                return self._create_ideal_rect_for_non_period_event(event)
        else:
            return self._create_ideal_rect_for_non_period_event(event)

    def _display_as_period(self, event):
        if event.is_container():
            event_width = self._calc_min_subevent_threshold_width(event)
        else:
            event_width = self._metrics.calc_width(event.time_period)
        return event_width > self._period_threshold

    def _calc_min_subevent_threshold_width(self, container):
        min_width = self._metrics.calc_width(container.time_period)
        for event in container.events:
            if event.is_period():
                width = self._calc_subevent_threshold_width(event)
                if width > 0 and width < min_width:
                    min_width = width
        return min_width

    def _calc_subevent_threshold_width(self, event):
        # The enlarging factor allows sub-events to be smaller than a normal
        # event before the container becomes a point event.
        enlarging_factor = 2
        return enlarging_factor * self._metrics.calc_width(event.time_period)

    def _create_ideal_rect_for_period_event(self, event):
        tw, th = self._get_text_size(event.text)
        ew = self._metrics.calc_width(event.time_period)
        min_w = 5 * self._outer_padding
        rw = max(ew + 2 * self._outer_padding, min_w)
        rh = th + 2 * self._inner_padding + 2 * self._outer_padding
        rx = (self._metrics.calc_x(event.time_period.start_time) -
              self._outer_padding)
        ry = self._get_ry(event)
        rect = wx.Rect(rx, ry, rw, rh)
        return rect

    def _get_ry(self, event):
        if event.is_subevent():
            if event.is_period():
                return self._get_container_ry(event)
            else:
                return self._metrics.half_height - self._baseline_padding
        else:
            return self._metrics.half_height + self._baseline_padding

    def _get_container_ry(self, subevent):
        for (event, rect) in self.event_data:
            if event == subevent.container:
                return rect.y
        return self._metrics.half_height + self._baseline_padding

    def _create_ideal_rect_for_non_period_event(self, event):
        tw, th = self._get_text_size(event.text)
        rw = tw + 2 * self._inner_padding + 2 * self._outer_padding
        rh = th + 2 * self._inner_padding + 2 * self._outer_padding
        if event.has_data():
            rw += self._data_indicator_size / 3
        if event.fuzzy or event.locked:
            rw += th + 2 * self._inner_padding
        rx = self._metrics.calc_x(event.mean_time()) - rw / 2
        ry = self._metrics.half_height - rh - self._baseline_padding
        rect = wx.Rect(rx, ry, rw, rh)
        return rect

    def _ensure_rect_is_not_far_outisde_screen(self, rect):
        # Drawing stuff on huge x-coordinates causes drawing to fail.
        # MARGIN must be big enough to hide outer padding, borders, and
        # selection markers.
        rx = rect.GetX()
        rw = rect.GetWidth()
        MARGIN = 50
        if rx < -MARGIN:
            distance_beyond_left_margin = -rx - MARGIN
            rx += distance_beyond_left_margin
            rw -= distance_beyond_left_margin
        right_edge_x = rx + rw
        if right_edge_x > self._metrics.width + MARGIN:
            rw -= right_edge_x - self._metrics.width - MARGIN
        rect.SetX(rx)
        rect.SetWidth(rw)

    def _calc_strips(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""
        def fill(list, strip):
            """Fill the given list with the given strip."""
            try:
                current_start = strip.start(self._view_properties.displayed_period.start_time)
                while current_start < self._view_properties.displayed_period.end_time:
                    next_start = strip.increment(current_start)
                    list.append(TimePeriod(self._db.get_time_type(), current_start, next_start))
                    current_start = next_start
            except:
                #Exception occurs when major=century and when we are at the end of the calendar
                pass
        self.major_strip_data = [] # List of time_period
        self.minor_strip_data = [] # List of time_period
        self.major_strip, self.minor_strip = self._db.get_time_type().choose_strip(self._metrics, self._config)
        fill(self.major_strip_data, self.major_strip)
        fill(self.minor_strip_data, self.minor_strip)

    def get_hidden_event_count(self):
        return len(self.events_from_db) - self._count_visible_events()

    def _count_visible_events(self):
        num_visible = 0
        for (event, rect) in self.event_data:
            if rect.Y < self.height and (rect.Y + rect.Height) > 0:
                num_visible += 1
        return num_visible

    def _prevent_overlapping_by_adjusting_rect_y(self, event, event_rect):
        if self._display_as_period(event):
            self._adjust_period_rect(event_rect)
        else:
            self._adjust_point_rect(event_rect)

    def _adjust_period_rect(self, event_rect):
        rect = self._get_overlapping_period_rect_with_largest_y(event_rect)
        if rect is not None:
            event_rect.Y = rect.Y + event_rect.height

    def _get_overlapping_period_rect_with_largest_y(self, event_rect):
        list = self._get_list_with_overlapping_period_events(event_rect)
        rect_with_largest_y = None
        for (event, rect) in list:
            if rect_with_largest_y is None or rect.Y > rect_with_largest_y.Y:
                rect_with_largest_y = rect
        return rect_with_largest_y

    def _get_list_with_overlapping_period_events(self, event_rect):
        return [(event, rect) for (event, rect) in self.event_data
                if (self._rects_overlap(event_rect, rect) and
                    rect.Y >= self.divider_y )]

    def _adjust_point_rect(self, event_rect):
        rect = self._get_overlapping_point_rect_with_smallest_y(event_rect)
        if rect is not None:
            event_rect.Y =  rect.Y - event_rect.height

    def _get_overlapping_point_rect_with_smallest_y(self, event_rect):
        list = self._get_list_with_overlapping_point_events(event_rect)
        rect_with_smallest_y = None
        for (event, rect) in list:
            if rect_with_smallest_y is None or rect.Y < rect_with_smallest_y.Y:
                rect_with_smallest_y = rect
        return rect_with_smallest_y

    def _get_list_with_overlapping_point_events(self, event_rect):
        return [(event, rect) for (event, rect) in self.event_data
                if (self._rects_overlap(event_rect, rect) and
                    rect.Y < self.divider_y  )]

    def _rects_overlap(self, rect1, rect2):
        return (rect2.x <= rect1.x + rect1.width and
                rect1.x <= rect2.x + rect2.width)
