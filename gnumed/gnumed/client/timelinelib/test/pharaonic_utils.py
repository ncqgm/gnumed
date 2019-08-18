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

"""
Contains unit test utility functions.

Many functions use a human readable date and time string as argument.
Such a string has a day, month, year and an optional time like this::

   "1 I Akhet 2012" or "12 I Akhet 2017 12:05:30"
"""

import random

from timelinelib.calendar.pharaonic.pharaonic import PharaonicDateTime
from timelinelib.calendar.pharaonic.monthnames import ABBREVIATED_ENGLISH_MONTH_NAMES
from timelinelib.calendar.pharaonic.time import PharaonicDelta
from timelinelib.calendar.pharaonic.timetype import PharaonicTimeType
from timelinelib.canvas.data import Category
from timelinelib.canvas.data import Container
from timelinelib.canvas.data import Era
from timelinelib.canvas.data import Event
from timelinelib.canvas.data import Subevent
from timelinelib.canvas.data import TimePeriod


ANY_TIME = "1 I Akhet 1710"
ANY_NUM_TIME = 10


def pharaonic_period(human_start_time, human_end_time):
    """
    Create a pharaonic TimePeriod object.
    The start and end times are strings in a human readable format.
    """
    return TimePeriod(human_time_to_pharaonic(human_start_time),
                      human_time_to_pharaonic(human_end_time))


def numeric_period(start, end):
    """
    Create a numeric TimePeriod object.
    The start and end are numeric values.
    """
    return TimePeriod(start, end)


def human_time_to_pharaonic(human_time):
    """
    Create a :doc:`PharaonicTime <timelinelib.calendar.pharaonic.time>` object
    from a human readable date and time string.
    """
    (year, month, day, hour, minute, seconds) = human_time_to_ymdhm(human_time)
    return PharaonicDateTime(year, month, day, hour, minute, seconds).to_time()


def a_time_period():
    """Create a random :doc:`TimePeriod <timelinelib_canvas_data_timeperiod>` object."""
    year = random.randint(1, 3900)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    end_year = year + random.randint(1, 5)
    end_month = random.randint(1, 12)
    end_day = random.randint(1, 28)
    return TimePeriod(PharaonicDateTime(year, month, day, 0, 0, 0).to_time(),
                      PharaonicDateTime(end_year, end_month, end_day, 0, 0, 0).to_time())

def human_time_to_ymdhm(human_time):
    """
    Convert a human readable date and time string into a tuple of
    numeric values.
    """
    parts = human_time.split(" ")
    day_part, month_part_1, month_part_2, year_part = parts[0], parts[1], parts[2], parts[3]
    month_part = month_part_1 + " " + month_part_2
    day = int(day_part)
    month = ABBREVIATED_ENGLISH_MONTH_NAMES.index(month_part) + 1
    year = int(year_part)
    if len(parts) == 5:
        hour = int(parts[4][:2])
        minute = int(parts[4][3:5])
        if len(parts[3]) == 8:
            seconds = int(parts[3][6:8])
        else:
            seconds = 0
    else:
        hour = 0
        minute = 0
        seconds = 0
    return (year, month, day, hour, minute, seconds)


def an_event():
    """Create an :doc:`Event <timelinelib_canvas_data_event>` object."""
    return an_event_with(time=ANY_TIME)


def an_event_with(human_start_time=None, human_end_time=None, time=ANY_TIME,
                  text="foo", fuzzy=False, locked=False, ends_today=False,
                  category=None, default_color=None):
    """Create an :doc:`Event <timelinelib_canvas_data_event>` object."""
    if human_start_time and human_end_time:
        start = human_time_to_pharaonic(human_start_time)
        end = human_time_to_pharaonic(human_end_time)
    else:
        start = human_time_to_pharaonic(time)
        end = human_time_to_pharaonic(time)
    event = Event().update(
        start,
        end,
        text,
        category=category,
        fuzzy=fuzzy,
        locked=locked,
        ends_today=ends_today
    )
    event.set_default_color(default_color)
    return event


def a_subevent():
    """Create a :doc:`Subevent <timelinelib_canvas_data_subevent>` object."""
    return a_subevent_with()


def a_subevent_with(start=None, end=None, time=ANY_TIME, text="sub", category=None, container=None):
    """Create a :doc:`Subevent <timelinelib_canvas_data_subevent>` object."""
    if start and end:
        start = human_time_to_pharaonic(start)
        end = human_time_to_pharaonic(end)
    else:
        start = human_time_to_pharaonic(time)
        end = human_time_to_pharaonic(time)
    event = Subevent().update(start, end, text, category=category)
    event.container = container
    return event


def a_container(name, category, sub_events):
    """Create a :doc:`Container <timelinelib_canvas_data_container>` object."""
    start = human_time_to_pharaonic(ANY_TIME)
    end = human_time_to_pharaonic(ANY_TIME)
    container = Container().update(start, end, name, category=category)
    all_events = []
    all_events.append(container)
    for (name, category) in sub_events:
        event = Subevent().update(start, end, name, category=category)
        event.container = container
        all_events.append(event)
    return all_events


def a_container_with(text="container", category=None):
    """Create a :doc:`Container <timelinelib_canvas_data_container>` object."""
    start = human_time_to_pharaonic(ANY_TIME)
    end = human_time_to_pharaonic(ANY_TIME)
    container = Container().update(start, end, text, category=category)
    return container


def a_category():
    """Create a :doc:`Category <timelinelib_canvas_data_category>` object."""
    return a_category_with(name="category")


def a_category_with(name, color=(255, 0, 0), font_color=(0, 255, 255),
                    parent=None):
    """Create a :doc:`Category <timelinelib_canvas_data_category>` object."""
    return Category().update(
        name=name,
        color=color,
        font_color=font_color,
        parent=parent
    )


def a_pharaonic_era():
    """Create an :doc:`Era <timelinelib_canvas_data_era>` object."""
    return a_pharaonic_era_with()


def a_pharaonic_era_with(start=None, end=None, time=ANY_TIME, name="foo",
                         color=(128, 128, 128), time_type=PharaonicTimeType(),
                         ends_today=False):
    """Create an :doc:`Era <timelinelib_canvas_data_era>` object."""
    if start and end:
        start = human_time_to_pharaonic(start)
        end = human_time_to_pharaonic(end)
    else:
        start = human_time_to_pharaonic(time)
        end = human_time_to_pharaonic(time)
    era = Era().update(start, end, name, color)
    era.set_ends_today(ends_today)
    return era


def a_numeric_era():
    """Create an :doc:`Era <timelinelib_canvas_data_era>` object."""
    return a_numeric_era_with()


def a_numeric_era_with(start=None, end=None, time=ANY_NUM_TIME, name="foo", color=(128, 128, 128)):
    """Create an :doc:`Era <timelinelib_canvas_data_era>` object."""
    if not (start or end):
        start = time
        end = time
    return Era().update(start, end, name, color)


def inc(number):
    """Return the number + 1. If number is None return 8."""
    if number is None:
        return 8
    else:
        return number + 1


def new_cat(event):
    """Return a new category."""
    if event.get_category() is None:
        return a_category_with(name="new category")
    else:
        return a_category_with(name="was: %s" % event.get_category().get_name())


def new_parent(category):
    """Return a new category parent."""
    if category._get_parent() is None:
        return a_category_with(name="new category")
    else:
        return a_category_with(name="was: %s" % category._get_parent().get_name())


def new_progress(event):
    """Return the event's progress + 1. If the event's progress is None, return 8."""
    if event.get_progress() is None:
        return 8
    else:
        return (event.get_progress() + 1) % 100


def modifier_change_ends_today(event):
    """Toggle the event's ends-today property."""
    if event.get_locked():
        event.set_locked(False)
        event.set_ends_today(not event.get_ends_today())
        event.set_locked(True)
    else:
        event.set_ends_today(not event.get_ends_today())
    return event


EVENT_MODIFIERS = [
    ("change fuzzy", lambda event:
        event.set_fuzzy(not event.get_fuzzy())),
    ("change locked", lambda event:
        event.set_locked(not event.get_locked())),
    ("change ends today", modifier_change_ends_today),
    ("change id", lambda event:
        event.set_id(inc(event.get_id()))),
    ("change time period", lambda event:
        event.set_time_period(event.get_time_period().move_delta(PharaonicDelta.from_days(1)))),
    ("change text", lambda event:
        event.set_text("was: %s" % event.get_text())),
    ("change category", lambda event:
        event.set_category(new_cat(event))),
    ("change icon", lambda event:
        event.set_icon("was: %s" % event.get_icon())),
    ("change description", lambda event:
        event.set_description("was: %s" % event.get_description())),
    ("change hyperlink", lambda event:
        event.set_hyperlink("was: %s" % event.get_hyperlink())),
    ("change progress", lambda event:
        event.set_progress(new_progress(event))),
    ("change alert", lambda event:
        event.set_alert("was: %s" % event.get_alert())),
]


SUBEVENT_MODIFIERS = EVENT_MODIFIERS


CONTAINER_MODIFIERS = [
    ("change time period", lambda event:
        event.set_time_period(event.get_time_period().move_delta(PharaonicDelta.from_days(1)))),
    ("change text", lambda event:
        event.set_text("was: %s" % event.get_text())),
    ("change category", lambda event:
        event.set_category(new_cat(event))),
]


CATEGORY_MODIFIERS = [
    ("change name", lambda category:
        category.set_name("was: %s" % category.get_name())),
    ("change id", lambda category:
        category.set_id(inc(category.get_id()))),
    ("change color", lambda category:
        category.set_color(category.get_color() + (1, 0, 3))),
    ("change font color", lambda category:
        category.set_font_color(category.get_font_color() + (1, 0, 3))),
    ("change parent", lambda category:
        category.set_parent(new_parent(category))),
]


TIME_PERIOD_MODIFIERS = [
    ("zoom", lambda time_period: time_period.zoom(-1)),
    ("move left", lambda time_period: time_period.move(-1)),
    ("move right", lambda time_period: time_period.move(1)),
]


ERA_MODIFIERS = [
    ("change id", lambda era: era.set_id(inc(era.get_id()))),
    ("change time period", lambda era: era.set_time_period(era.get_time_period().move_delta(PharaonicDelta.from_days(1)))),
    ("change text", lambda era: era.set_name("was: %s" % era.get_name())),
    ("change color", lambda era: era.set_color(tuple([x + 1 for x in era.get_color()])))
]

NUM_ERA_MODIFIERS = [
    ("change id", lambda era: era.set_id(inc(era.get_id()))),
    ("change time period", lambda era: era.set_time_period(era.get_time_period().move_delta(1))),
    ("change text", lambda era: era.set_name("was: %s" % era.get_name())),
    ("change color", lambda era: era.set_color(tuple([x + 1 for x in era.get_color()])))
]


TIME_MODIFIERS = [
    ("add", lambda time: time + PharaonicDelta(1)),
]


class ObjectWithTruthValue(object):
    """An object of this class can be treated as a boolean."""
    def __init__(self, truth_value):
        self.truth_value = truth_value

    def __nonzero__(self):
        return self.truth_value


def select_language(language):
    """
    Select the system locale language.
    This function is Windows specific.
    """
    import platform
    from timelinelib.config.paths import LOCALE_DIR
    from timelinelib.meta.about import APPLICATION_NAME
    if platform.system() == "Windows":
        import gettext
        import os
        os.environ['LANG'] = language
        gettext.install(APPLICATION_NAME.lower(), LOCALE_DIR, unicode=True)


class _ANY(object):
    """An object of this class is always considered equal to any other object."""

    def __eq__(self, other):
        return True
ANY = _ANY()
"""This object is always considered equal to any other object."""
