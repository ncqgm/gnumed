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


"""
Defines the interface that drawers should adhere to.
"""


class Drawer(object):
    """
    Draw timeline onto a device context and provide information about drawing.
    """

    def draw(self, dc, timeline, view_properties, config):
        """
        Draw a representation of a timeline.

        The dc is used to do the actual drawing. The timeline is used to get
        the events to visualize. The view properties contains information like
        which events are selected in the view we are drawing for and what
        period is currently displayed.

        When the dc is temporarily stored in a class variable such as self.dc,
        this class variable must be deleted before the draw method ends.
        """

    def use_fast_draw(self, value):
        self.fast_draw = value

    def event_is_period(self, time_period):
        """
        Return True if the event time_period will make the event appear
        below the center line, as a period event.
        """
        return None

    def snap(self, time, snap_region=10):
        """Snap time to minor strip if within snap_region pixels."""
        return time

    def snap_selection(self, period_selection):
        """
        Return a tuple where the selection has been stretched to fit to minor
        strip.

        period_selection: (start, end)
        Return: (new_start, new_end)
        """
        return period_selection

    def event_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) or None if no event there.
        """
        return None

    def event_with_rect_at(self, x, y):
        """
        Return the event at pixel coordinate (x, y) and its rect in a tuple
        (event, rect) or None if no event there.
        """
        return None

    def event_rect_at(self, event):
        """
        Return the rect for the given event or None if no event isn't found.
        """
        return None

    def is_balloon_at(self, event, x, y):
        """
        Return True if a balloon for event is drawn at (x, y), otherwise False.
        """

    def get_closest_overlapping_event(self, event_to_move, up=True):
        raise NotImplementedError()


class Strip(object):
    """
    An interface for strips.

    The different strips are implemented in subclasses below.

    The timeline is divided in major and minor strips. The minor strip might
    for example be days, and the major strip months. Major strips are divided
    with a solid line and minor strips with dotted lines. Typically maximum
    three major strips should be shown and the rest will be minor strips.
    """

    def label(self, time, major=False):
        """
        Return the label for this strip at the given time when used as major or
        minor strip.
        """

    def start(self, time):
        """
        Return the start time for this strip and the given time.

        For example, if the time is 2008-08-31 and the strip is month, the
        start would be 2008-08-01.
        """

    def increment(self, time):
        """
        Increment the given time so that it points to the start of the next
        strip.
        """

    def get_font(self, time_period):
        """
        Return the preferred font for this strip
        """
