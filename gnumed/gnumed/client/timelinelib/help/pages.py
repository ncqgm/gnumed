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
All help pages for the help system.

Template for translator comments (should be before all body parts):

# TRANSLATORS: This text uses special markup.
# DON'T translate 'HelpFigure(..)' or 'Help(..)'.
# Just write them as they are.
# Stars produce emphasized text. DON'T remove them.
# Dashes produce bullet lists. DON'T remove them.
"""


def install(help_system):

    help_system.install_page(
        id="contents",
        header=_("Help contents"),
        body=("""
- **%s**
    - Help(where_is_save)
    - Help(categories_delete)
    - Help(why_not_timeline_in_my_language)
    - Help(week_numbers_sunday_week_start)
- **%s**
    - Help(timeline)
    - Help(events)
    - Help(categories)
- **%s**
    - Help(create_event)
    - Help(edit_event)
    - Help(move_event_vertically)
    - Help(delete_event)
    - Help(edit_categories)
    - Help(select_events)
- **Help(contact)**
""" % (_("Questions and answers"), _("Concepts"), _("Tasks"))))


    help_system.install_page(
        id="where_is_save",
        header=_("Where is the save button?"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
There is no save button. Timeline will automatically save your data whenever needed.
"""))


    help_system.install_page(
        id="week_numbers_sunday_week_start",
        header=_("Where do the week numbers go if I start my weeks on Sunday?"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The date data object used does not support week numbers for weeks that start on Sunday at present.  We plan on using a different date object that will support this in future versions.
"""))


    help_system.install_page(
        id="timeline",
        header=_("Timeline"),
        related_pages=["events", "categories", "contact"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The timeline shows dates according to the Gregorian calendar on the x-axis. Currently the dates are limited to dates between year 10 and year 9989.

Future versions might support various kinds of timelines so that you for example can specify a time in terms of number of minutes since a start time. If you are interested in such a feature, please get in touch.
"""))

    help_system.install_page(
        id="events",
        header=_("Events"),
        related_pages=["categories"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
An event is the basic data type for representing information on the timeline.  It must specify where on the timeline is should be placed (when that event happened). This can be either a specific point in time or a period.
"""))

    help_system.install_page(
        id="categories",
        header=_("Categories"),
        related_pages=["categories_delete", "events"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
Categories are used to group events. An event can only belong to one category. All events that belong to the same category are displayed with the same background color.
"""))

    help_system.install_page(
        id="create_event",
        header=_("Create event"),
        related_pages=["events", "delete_event"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The *Create Event* dialog can be opened in the following ways:

- Select *Timeline* - *Create Event* from the menu.
- Double click with the *left* mouse button on the timeline.
- Press the *Ctrl* key, thereafter hold *left* mouse button down on the timeline, drag the mouse and release it.
"""))

    help_system.install_page(
        id="edit_event",
        header=_("Edit event"),
        related_pages=["events", "delete_event"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The *Edit Event* dialog can be opened by double clicking on an event.
"""))

    help_system.install_page(
        id="move_event_vertically",
        header=_("Move event vertically"),
        related_pages=["events", "select_events"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
An event can be moved vertically. This is done by first selecting the event and therefter using the Alt+Up or Alt+Down keys.
"""))

    help_system.install_page(
        id="select_events",
        header=_("Selecting events"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
To select an event, click on it. To select multiple events, hold down the *Ctrl* key while clicking events.
"""))

    help_system.install_page(
        id="delete_event",
        header=_("Delete event"),
        related_pages=["select_events", "events"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
To delete an event, select it and press the *Del* key. Multiple events can be deleted at the same time.
"""))

    help_system.install_page(
        id="categories_delete",
        header=_("Will associated events be deleted when I delete a category?"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
No. The events will still be there but they will not belong to a category.
"""))

    help_system.install_page(
        id="edit_categories",
        header=_("Edit categories"),
        related_pages=["categories"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
Categories can be managed in the *Edit Categories* dialog (*Timeline* > *Edit Categories*). To edit an existing category, double click on it.

The visibility of categories can also be edited in the sidebar (*View* > *Sidebar*).
"""))

    help_system.install_page(
        id="contact",
        header=_("Contact"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
If you have more questions about Timeline, or if you want to get in contact with users and developers of Timeline, send an email to the user mailing list: <thetimelineproj-user@lists.sourceforge.net>. (Please use English.)
"""))

    help_system.install_page(
        id="why_not_timeline_in_my_language",
        header=_("Why is Timeline not available in my language?"),
        related_pages=["contact"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
Timeline is developed and translated by volunteers. If you would like to contribute translations you are very much welcome to contact us.
"""))
