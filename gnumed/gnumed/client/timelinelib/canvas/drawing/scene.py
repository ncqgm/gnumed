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

from timelinelib.canvas.drawing.utils import Metrics
from timelinelib.canvas.data import TimePeriod


FORWARD = 1
BACKWARD = -1


class TimelineScene(object):

    def __init__(self, size, db, view_properties, get_text_size_fn, appearance):
        self._db = db
        self._view_properties = view_properties
        self._get_text_size_fn = get_text_size_fn
        self._appearance = appearance
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
        """
        Creating a scene means that pixel sizes and positions are calculated
        for events and strips.
        """
        self.event_data = self._calc_event_sizes_and_positions()
        self.minor_strip_data, self.major_strip_data = self._calc_strips_sizes_and_positions()

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
        self._inflate_event_rects_to_get_right_dimensions_for_overlap_calculations()
        rect = self._get_event_rect(selected_event)
        period = self._event_rect_drawn_as_period(rect)
        direction = self._get_direction(period, up)
        evt = self._get_overlapping_event(period, direction, selected_event, rect)
        return (evt, direction)

    def center_text(self):
        return self._appearance.get_center_event_texts()

    def _inflate_event_rects_to_get_right_dimensions_for_overlap_calculations(self):
        for (_, rect) in self.event_data:
            rect.Inflate(self._outer_padding, self._outer_padding)

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
        event_data = self._get_overlapping_events_list(period, rect)
        event = self._get_overlapping_event_from_list(event_data, direction,
                                                      selected_event)
        return event

    def _get_overlapping_events_list(self, period, rect):
        if period:
            return self._get_list_with_overlapping_period_events(rect)
        else:
            return self._get_list_with_overlapping_point_events(rect)

    def _get_overlapping_event_from_list(self, event_data, direction, selected_event):
        if direction == FORWARD:
            return self._get_next_overlapping_event(event_data, selected_event)
        else:
            return self._get_prev_overlapping_event(event_data, selected_event)

    def _get_next_overlapping_event(self, event_data, selected_event):
        selected_event_found = False
        for (e, _) in event_data:
            if not selected_event.is_subevent() and e.is_subevent():
                continue
            if selected_event_found:
                return e
            else:
                if e == selected_event:
                    selected_event_found = True
        return None

    def _get_prev_overlapping_event(self, event_data, selected_event):
        prev_event = None
        for (e, _) in event_data:
            if not selected_event.is_subevent() and e.is_subevent():
                continue
            if e == selected_event:
                return prev_event
            prev_event = e

    def _calc_event_sizes_and_positions(self):
        self.events_from_db = self._db.get_events(self._view_properties.displayed_period)
        visible_events = self._view_properties.filter_events(self.events_from_db)
        visible_events = self._place_subevents_after_container(visible_events)
        return self._calc_event_rects(visible_events)

    def _place_subevents_after_container(self, events):
        """
        All subevents belonging to a container are placed directly after
        the container event in the events list.
        This is necessary because the position of the subevents are
        dependent on the position of the container. So the container metrics
        must be calculated first.
        """
        result = []
        for event in events:
            if event.is_container():
                result.append(event)
                result.extend(self._get_container_subevents(event, events))
            elif not event.is_subevent():
                result.append(event)
        return result

    def _get_container_subevents(self, container, events):
        return [
            evt for evt
            in events
            if evt.is_subevent() and evt.container is container
        ]

    def _calc_event_rects(self, events):
        self.event_data = self._calc_non_overlapping_event_rects(events)
        self._deflate_rects(self.event_data)
        return self.event_data

    def _calc_non_overlapping_event_rects(self, events):
        self.event_data = []
        for event in events:
            rect = self._create_ideal_rect_for_event(event)
            self._prevent_overlapping_by_adjusting_rect_y(event, rect)
            self.event_data.append((event, rect))
        return self.event_data

    def _deflate_rects(self, event_data):
        for (_, rect) in event_data:
            rect.Deflate(self._outer_padding, self._outer_padding)

    def _create_ideal_rect_for_event(self, event):
        self._reset_ends_today_when_start_date_is_in_future(event)
        if event.ends_today:
            event.set_end_time(self._db.get_time_type().now())
        if self._display_as_period(event):
            return self._calc_ideal_rect_for_period_event(event)
        else:
            return self._calc_ideal_rect_for_non_period_event(event)

    def _reset_ends_today_when_start_date_is_in_future(self, event):
        if event.ends_today and self._start_date_is_in_future(event):
            event.ends_today = False

    def _start_date_is_in_future(self, event):
        return event.get_time_period().start_time > self._db.get_time_type().now()

    def _display_as_period(self, event):
        return self._metrics.calc_width(event.get_time_period()) > self._period_threshold

    def _calc_ideal_rect_for_period_event(self, event):
        rw, rh = self._calc_width_and_height_for_period_event(event)
        rx = self._calc_x_pos_for_period_event(event)
        ry = self._calc_y_pos_for_period_event(event)
        return self._calc_ideal_wx_rect(rx, ry, rw, rh)

    def _calc_width_and_height_for_period_event(self, event):
        _, th = self._get_text_size(event.get_text())
        ew = self._metrics.calc_width(event.get_time_period())
        min_w = 5 * self._outer_padding
        rw = max(ew + 2 * self._outer_padding, min_w)
        rh = th + 2 * self._inner_padding + 2 * self._outer_padding
        return rw, rh

    def _calc_x_pos_for_period_event(self, event):
        return self._metrics.calc_x(event.get_time_period().start_time) - self._outer_padding

    def _calc_y_pos_for_period_event(self, event):
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

    def _calc_ideal_rect_for_non_period_event(self, event):
        if self.never_show_period_events_as_point_events() and event.is_period():
            return self._calc_invisible_wx_rect()
        else:
            rw, rh = self._calc_width_and_height_for_non_period_event(event)
            rx = self._calc_x_pos_for_non_period_event(event, rw)
            ry = self._calc_y_pos_for_non_period_event(event, rh)
            if event.is_milestone():
                rw = rh
                rx = self._metrics.calc_x(event.get_time_period().start_time) - rw / 2
                return wx.Rect(rx, ry, rw, rh)
            return self._calc_ideal_wx_rect(rx, ry, rw, rh)

    def _calc_invisible_wx_rect(self):
        return self._calc_ideal_wx_rect(-1, -1, 0, 0)

    def _calc_width_and_height_for_non_period_event(self, event):
        tw, th = self._get_text_size(event.get_text())
        rw = tw + 2 * self._inner_padding + 2 * self._outer_padding
        rh = th + 2 * self._inner_padding + 2 * self._outer_padding
        if event.has_data():
            rw += self._data_indicator_size / 3
        if event.get_fuzzy() or event.get_locked():
            rw += th + 2 * self._inner_padding
        return rw, rh

    def _calc_x_pos_for_non_period_event(self, event, rw):
        if self._appearance.get_draw_period_events_to_right():
            return self._metrics.calc_x(event.get_time_period().start_time) - self._outer_padding
        else:
            return self._metrics.calc_x(event.mean_time()) - rw / 2

    def _calc_y_pos_for_non_period_event(self, event, rh):
        if event.is_milestone():
            return self._metrics.half_height - rh / 2
        else:
            return self._metrics.half_height - rh - self._baseline_padding

    def _get_text_size(self, text):
        if len(text) > 0:
            return self._get_text_size_fn(text)
        else:
            return self._get_text_size_fn(" ")

    def never_show_period_events_as_point_events(self):
        return self._appearance.get_never_show_period_events_as_point_events()

    def _calc_ideal_wx_rect(self, rx, ry, rw, rh):
        # Drawing stuff on huge x-coordinates causes drawing to fail.
        # MARGIN must be big enough to hide outer padding, borders, and
        # selection markers.
        MARGIN = 15
        if rx < (-MARGIN):
            move_distance = abs(rx) - MARGIN
            rx += move_distance
            rw -= move_distance
        right_edge_x = rx + rw
        if right_edge_x > self.width + MARGIN:
            rw -= right_edge_x - self.width - MARGIN
        return wx.Rect(rx, ry, rw, rh)

    def _calc_strips_sizes_and_positions(self):
        """Fill the two arrays `minor_strip_data` and `major_strip_data`."""

        def fill(strip_list, strip):
            """Fill the given list with the given strip."""
            try:
                current_start = strip.start(self._view_properties.displayed_period.start_time)
                while current_start < self._view_properties.displayed_period.end_time:
                    next_start = strip.increment(current_start)
                    strip_list.append(TimePeriod(current_start, next_start))
                    current_start = next_start
            except:
                # Exception occurs when major=century and when we are at the end of the calendar
                pass
        major_strip_data = []  # List of time_period
        minor_strip_data = []  # List of time_period
        self.major_strip, self.minor_strip = self._db.get_time_type().choose_strip(self._metrics, self._appearance)
        if hasattr(self.major_strip, 'set_skip_s_in_decade_text'):
            self.major_strip.set_skip_s_in_decade_text(self._view_properties.get_skip_s_in_decade_text())
        if hasattr(self.minor_strip, 'set_skip_s_in_decade_text'):
            self.minor_strip.set_skip_s_in_decade_text(self._view_properties.get_skip_s_in_decade_text())
        fill(major_strip_data, self.major_strip)
        fill(minor_strip_data, self.minor_strip)
        return (minor_strip_data, major_strip_data)

    def minor_strip_is_day(self):
        return self.minor_strip.is_day()

    def is_weekend_day(self, time):
        return self._db.time_type.is_weekend_day(time)

    def get_hidden_event_count(self):
        return len(self.events_from_db) - self._count_visible_events()

    def _count_visible_events(self):
        num_visible = 0
        for (_, rect) in self.event_data:
            if rect.Y < self.height and (rect.Y + rect.Height) > 0:
                num_visible += 1
        return num_visible

    def _prevent_overlapping_by_adjusting_rect_y(self, event, event_rect):
        if event.is_milestone():
            return
        if event.is_subevent() and self._display_as_period(event):
            self._adjust_subevent_rect(event, event_rect)
        else:
            if self._display_as_period(event):
                self._adjust_period_rect(event_rect)
            else:
                self._adjust_point_rect(event_rect)

    def _adjust_period_rect(self, event_rect):
        rect = self._get_overlapping_period_rect_with_largest_y(event_rect)
        if rect is not None:
            event_rect.Y = rect.Y + rect.height

    def _adjust_subevent_rect(self, subevent, event_rect):
        rect = self._get_overlapping_subevent_rect_with_largest_y(subevent, event_rect)
        if rect is not None:
            event_rect.Y = rect.Y + rect.height
            self._adjust_container_rect_height(subevent, event_rect)

    def _adjust_container_rect_height(self, subevent, event_rect):
        for (evt, rect) in self.event_data:
            if evt.is_container() and evt is subevent.container:
                _, th = self._get_text_size(evt.get_text())
                rh = th + 2 * (self._inner_padding + self._outer_padding)
                h = event_rect.Y - rect.Y + rh
                if rect.height < h:
                    rect.Height = h
                break

    def _get_overlapping_subevent_rect_with_largest_y(self, subevent, event_rect):
        event_data = self._get_list_with_overlapping_subevents(subevent, event_rect)
        rect_with_largest_y = None
        for (_, rect) in event_data:
            if rect_with_largest_y is None or rect.Y > rect_with_largest_y.Y:
                rect_with_largest_y = rect
        return rect_with_largest_y

    def _get_overlapping_period_rect_with_largest_y(self, event_rect):
        event_data = self._get_list_with_overlapping_period_events(event_rect)
        rect_with_largest_yh = None
        for (_, rect) in event_data:
            if rect_with_largest_yh is None or rect.Y + rect.Height > rect_with_largest_yh.Y + rect_with_largest_yh.Height:
                rect_with_largest_yh = rect
        return rect_with_largest_yh

    def _get_list_with_overlapping_period_events(self, event_rect):
        return [(event, rect) for (event, rect) in self.event_data
                if (self._rects_overlap(event_rect, rect) and
                    rect.Y >= self.divider_y)]

    def _get_list_with_overlapping_subevents(self, subevent, event_rect):
        ls = [(event, rect) for (event, rect) in self.event_data
              if (event.is_subevent() and
                  event.container is subevent.container and
                  self._rects_overlap(event_rect, rect) and
                  rect.Y >= self.divider_y)]
        return ls

    def _adjust_point_rect(self, event_rect):
        rect = self._get_overlapping_point_rect_with_smallest_y(event_rect)
        if rect is not None:
            event_rect.Y = rect.Y - event_rect.height

    def _get_overlapping_point_rect_with_smallest_y(self, event_rect):
        event_data = self._get_list_with_overlapping_point_events(event_rect)
        rect_with_smallest_y = None
        for (_, rect) in event_data:
            if rect_with_smallest_y is None or rect.Y < rect_with_smallest_y.Y:
                rect_with_smallest_y = rect
        return rect_with_smallest_y

    def _get_list_with_overlapping_point_events(self, event_rect):
        return [(event, rect) for (event, rect) in self.event_data
                if (self._rects_overlap(event_rect, rect) and
                    rect.Y < self.divider_y)]

    def _rects_overlap(self, rect1, rect2):
        REMOVE_X_PADDING = 2 + self._outer_padding * 2
        return (rect2.x + REMOVE_X_PADDING <= rect1.x + rect1.width and
                rect1.x + REMOVE_X_PADDING <= rect2.x + rect2.width)
