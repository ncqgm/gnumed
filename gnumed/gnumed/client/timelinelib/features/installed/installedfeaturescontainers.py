# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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


from timelinelib.features.installed.installedfeature import InstalledFeature


DISPLAY_NAME = "&Containers"
DESCRIPTION = """
             Containers are a way to group events together.
             In a container events can not overlap, so if you add a new event to a container
             all other events are moved to give room for the new event. The same thing happens
             if you resize an event within the container.

             Have a look at this video for a demo. http://www.youtube.com/watch?v=dBwEQ3vqB_I
             """


class InstalledFeatureContainers(InstalledFeature):

    def __init__(self):
        InstalledFeature.__init__(self, DISPLAY_NAME, DESCRIPTION)
