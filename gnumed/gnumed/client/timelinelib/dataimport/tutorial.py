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


from timelinelib.calendar.gregorian.gregorian import GregorianDateTime
from timelinelib.calendar.gregorian.time import GregorianDelta
from timelinelib.calendar.num.time import NumDelta
from timelinelib.canvas.data.db import MemoryDB
from timelinelib.canvas.data import TimePeriod


class TutorialTimelineCreator(object):

    def __init__(self):
        self.db = MemoryDB()
        self.db.time_type = self.get_time_type()
        self.start, self.end = self.get_start_end()
        self.db.set_displayed_period(TimePeriod(self.start, self.end))
        self.last_cat = None

    def add_category(self, name, color, font_color, make_last_added_parent=False):
        if make_last_added_parent:
            parent = self.last_cat
        else:
            parent = None
        self.prev_cat = self.last_cat
        self.last_cat = self.db.new_category().update(
            name=name,
            color=color,
            font_color=font_color,
            parent=parent
        ).save()

    def add_milestone(self, time_add, text, label):
        start, end = self._calc_start_end(time_add, time_add)
        self.db.new_milestone(
            description=text
        ).update(start, start, label).save()

    def add_era(self, start_add, end_add, name):
        start, end = self._calc_start_end(start_add, end_add)
        self.db.new_era(
        ).update(start, end, name, color=(250, 250, 230)).save()

    def add_event(self, text, description, start_add, end_add=None, hyperlink=None):
        start, end = self._calc_start_end(start_add, end_add)
        event = self.db.new_event().update(start, end, text, self.last_cat)
        if description:
            event.set_data("description", description)
        if hyperlink:
            event.set_hyperlink(hyperlink)
        event.set_default_color((200, 200, 200))
        event.save()

    def add_container(self, text, description, start_add, end_add=None):
        start, end = self._calc_start_end(start_add, end_add)
        return self.db.new_container(
        ).update(start, end, text, self.prev_cat).save()

    def add_subevent(self, container, text, description, start_add, end_add=None, hyperlink=None):
        start, end = self._calc_start_end(start_add, end_add)
        event = self.db.new_subevent(
            container=container,
            time_period=TimePeriod(start, end)
        ).update(start, end, text, self.last_cat)
        if description:
            event.set_data("description", description)
        if hyperlink:
            event.set_hyperlink(hyperlink)
        event.save()

    def get_db(self):
        self.db.clear_transactions()
        return self.db

    def _calc_start_end(self, start_add, end_add=None):
        start = self.start + self.get_delta(start_add)
        end = start
        if end_add is not None:
            end = self.start + self.get_delta(end_add)
        return (start, end)


class GregorianTutorialTimelineCreator(TutorialTimelineCreator):

    def get_time_type(self):
        from timelinelib.calendar.gregorian.timetype import GregorianTimeType
        return GregorianTimeType()

    def get_start_end(self):
        now = GregorianDateTime.from_time(self.db.time_type.now())
        start = GregorianDateTime(
            now.year,
            now.month,
            1,
            0,
            0,
            0
        ).to_time()
        end = start + self.get_delta(30)
        return (start, end)

    def get_delta(self, value):
        return GregorianDelta.from_days(value)


class NumericTutorialTimelineCreator(TutorialTimelineCreator):

    def get_time_type(self):
        from timelinelib.calendar.num.timetype import NumTimeType
        return NumTimeType()

    def get_start_end(self):
        start = self.db.time_type.now()
        end = start + self.get_delta(30)
        return (start, end)

    def get_delta(self, value):
        return NumDelta(value)


def create_in_memory_gregorian_tutorial_db():
    return create_in_memory_tutorial_db(GregorianTutorialTimelineCreator())


def create_in_memory_numeric_tutorial_db():
    return create_in_memory_tutorial_db(NumericTutorialTimelineCreator())


def create_in_memory_tutorial_db(tutcreator):
    tutcreator.add_milestone(
        1,
        _("Start"),
        "<",
    )
    tutcreator.add_milestone(
        29,
        _("End"),
        ">",
    )
    tutcreator.add_era(
        20, 28,
        _("Example era"),
    )
    tutcreator.add_category(
        _("Welcome"), (255, 80, 80), (0, 0, 0)
    )
    tutcreator.add_event(
        _("Welcome to Timeline"), "",  4
    )
    tutcreator.add_category(
        _("Intro"), (250, 250, 20), (0, 0, 0)
    )
    tutcreator.add_event(
        _("This event has hyperlinks"),
        _("Right-click for context menu where the hyperlinks can be accessed."),
        11,
        19,
        "https://sourceforge.net/projects/thetimelineproj/;http://thetimelineproj.sourceforge.net/"
    )
    tutcreator.add_event(
        _("Hover me!"),
        _("Hovering events with a triangle shows the event description."),
        5
    )
    tutcreator.add_category(
        _("Features"), (100, 100, 250), (250, 250, 20)
    )
    tutcreator.add_event(
        _("Scroll"),
        _("Left click somewhere on the timeline and start dragging."
          "\n\n"
          "You can also use the mouse wheel."
          "\n\n"
          "You can also middle click with the mouse to center around that point."),
        5,
        10
    )
    container = tutcreator.add_container(
        _("Container"),
        _("?"),
        5,
        10
    )
    tutcreator.add_subevent(
        container,
        _("Resize me"),
        _("Container Subevent 1\nClick on the event to get the resize handles"),
        5,
        10
    )
    tutcreator.add_subevent(
        container,
        _("Drag me"),
        _("Container Subevent 2\n\n"
          "Click on the event to get the drag handle and drag it.\n\n"
          "To drag the whole container, click on it while holding down the Alt key. "
          "Keep the Alt key down and find the drag point at the center of the container and drag it."),
        12,
        18
    )
    tutcreator.add_subevent(
        container,
        _("View Container demo video"),
        _("Container Subevent 3\n\n"
          "Select hyperlink to show demo video.\n\n"
          "Right-click in the event and select 'Goto URL' in the popup menu and select the first (and only) link"),
        19,
        24,
        "http://www.youtube.com/watch?v=dBwEQ3vqB_I"
    )
    tutcreator.add_event(
        _("Zoom"),
        _("Hold down Ctrl while scrolling the mouse wheel."
          "\n\n"
          "Hold down Shift while dragging with the mouse."),
        6,
        11
    )
    tutcreator.add_event(
        _("Create event"),
        _("Double click somewhere on the timeline."
          "\n\n"
          "Hold down Ctrl while dragging the mouse to select a period."),
        12,
        18
    )
    tutcreator.add_event(
        _("Edit event"),
        _("Double click on an event."),
        12,
        18
    )
    tutcreator.add_event(
        _("Select event"),
        _("Click on it."
          "\n\n"
          "Hold down Ctrl while clicking events to select multiple."),
        20,
        25
    )
    tutcreator.add_event(
        _("Delete event"),
        _("Select events to be deleted and press the Del key."),
        19,
        24
    )
    tutcreator.add_event(
        _("Resize and move me!"),
        _("First select me and then drag the handles."),
        11,
        19
    )
    tutcreator.add_category(
        _("Saving"), (50, 200, 50), (0, 0, 0)
    )
    tutcreator.add_event(
        _("Saving"),
        _("This timeline is stored in memory and modifications to it will not "
          "be persisted between sessions."
          "\n\n"
          "Choose File/New/File Timeline to create a timeline that is saved on "
          "disk."),
        23
    )
    return tutcreator.get_db()
