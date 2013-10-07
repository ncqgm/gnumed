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


from timelinelib.db.backends.xmlfile import XmlTimeline


def _set_time_type(xml_timeline, timeline):
    try:
        xml_timeline.time_type = timeline.time_type
    except:
        # IcsTimeline doesn't have any categories
        pass


def _set_all_categories(xml_timeline, timeline):
    try:
        for cat in timeline.categories:
            xml_timeline.categories.append(cat)
    except:
        # IcsTimeline doesn't have any categories
        pass


def _set_hidden_categories(xml_timeline, timeline):
    try:
        for cat in timeline.hidden_categories:
            xml_timeline.hidden_categories.append(cat)
    except:
        # IcsTimeline doesn't have any categories
        pass


def _set_categories(xml_timeline, timeline):
    _set_all_categories(xml_timeline, timeline)
    _set_hidden_categories(xml_timeline, timeline)


def _set_events(xml_timeline, timeline):
    for event in timeline.events:
        xml_timeline.events.append(event)


def transform_to_xml_timeline(path, timeline):
    xml_timeline = XmlTimeline(path, load=False)
    _set_time_type(xml_timeline, timeline)
    _set_categories(xml_timeline, timeline)
    _set_events(xml_timeline, timeline)
    return xml_timeline
    