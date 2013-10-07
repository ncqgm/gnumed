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
    - Help(multiple_users)
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
    - Help(import_timeline)
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
        id="multiple_users",
        header=_("Can multiple users work with the same timeline?"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
There are some support for multiple users to work on the same timeline file.

When you try to make a change and someone else has made a change you will be asked to make one of two choices:

- Set timeline in read-only mode.
- Synchronize the timeline.
 
During the your edit action the timeline is locked for changes by others. If you try to edit a timeline when it is locked by someone else you will be notified about this situation.
"""))

    help_system.install_page(
        id="timeline",
        header=_("Timeline"),
        related_pages=["scrolling", "zooming", "import_timeline", "events", "categories", "contact"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The timeline shows dates according to the Gregorian calendar on the x-axis. Currently the earliest date is limited to Julian day 0 (November 24, 4714 BC).

Future versions might support various kinds of timelines so that you for example can specify a time in terms of number of minutes since a start time. If you are interested in such a feature, please get in touch.

The timeline is divided in two areas with a horizontal adjustable divider line. Period events are displayed below the line and point events are displayed above the line.
"""))

    help_system.install_page(
        id="scrolling",
        header=_("Scrolling Timeline"),
        related_pages=["timeline"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
A Timeline can be scrolled both horizontal (along time axis) and vertically (along event axis)

There are two ways to scroll horizontal. You can either use the different options in the Navigation menu or you can use the mouse. To use the mouse, hold down the left mouse button and drag the mouse horizontally.

To scroll vertically, hold down the Shift- and Ctrl-keys and scroll the mouse wheel.
Events are scrolled towards or away from the divider line separating point- and period-events.

"""))

    help_system.install_page(
        id="zooming",
        header=_("Zooming Timeline"),
        related_pages=["timeline"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
A Timeline can be Zoomed both horizontal (along time axis) and vertically (along event axis)

To zoom vertically, hold down the Ctrl-key and scroll the mouse wheel.

To zoom vertically, hold down the Alt-key and scroll the mouse wheel.
"""))

    help_system.install_page(
        id="events",
        header=_("Events"),
        related_pages=["event_properties", "create_event", "select_events", "edit_event", "delete_event", "move_event_vertically", "duplicate_event", "categories"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
An event is the basic data type for representing information on the timeline.  It must specify where on the timeline it should be placed (when that event happened). This can be either a specific point in time or a period.
"""))

    help_system.install_page(
        id="event_properties",
        header=_("Event Properties"),
        related_pages=["events", "event_containers"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
For an event the following properties can be defined.

 - Start Date and Time.
 - End Date and Time (if period event).
 - Text - The label displayed for an event.
 - Category - A way to group events together.
 - Container - Another way to group events together.
 - Fuzzy - Draw start and end of event fuzzy, to indicate that exact times are unknown.
 - Locked - Start- and End-points can't be changed.
 - Ends Today - The End-point is always set to current date.
 - Description - Event description that is shown i the balloon.
 - Icon - Image icon shown in balloon.
 - Alert - An alert dialog is opened at the specified alert time.
 - Hyperlink - A hyperlink that can be reached in the event context menu.
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
        related_pages=["events", "select_events"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
The *Edit Event* dialog can be opened by double clicking on an event or by selecting one event and select the 'Timeline -> Edit Selected Event...' menu.
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
        id="duplicate_event",
        header=_("Duplicate event"),
        related_pages=["events", "select_events"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
An event can be duplicated. Select the event you want to duplicate and select the 'Timeline -> Duplicate Selected Event...' menu.
Now a dialog appears in which you can define

 - How many duplications to do
 - The time period used
 - The frequency of time periods
 - The direction
 
 If number of duplications = 3, time span = day and frequency = 2, you will get 3 new copies of the event spread out with the time span of 2 days between them.
 
 You can also get to the duplication dialog from the event context menu, wich appears if you right-click an event with the mouse.
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
        id="import_timeline",
        header=_("Import timeline"),
        related_pages=["timeline"],
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
This feature can be used to merge two timelines into one.

First open a timeline and then select menu 'File -> Import timeline...' and select the timeline to be imported.
"""))

    help_system.install_page(
        id="event_containers",
        header=_("Event Containers"),
        # TRANSLATORS: This text uses special markup.
        # DON'T translate 'HelpFigure(..)' or 'Help(..)'.
        # Just write them as they are.
        # Stars produce emphasized text. DON'T remove them.
        # Dashes produce bullet lists. DON'T remove them.
        body=_("""
Containers are a way to group events together.
In a container events can not overlap, so if you add a new event to a container
all other events are moved to give room for the new event. The same thing happens
if you resize an event within the container.
             
Have a look at this video for a demo. 
    <http://www.youtube.com/watch?v=dBwEQ3vqB_I>
"""))

    help_system.install_page(
        id="delete_event",
        header=_("Delete event"),
        related_pages=["events", "select_events"],
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
