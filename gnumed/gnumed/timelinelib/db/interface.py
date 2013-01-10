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


class ContainerStrategy(object):

    def __init__(self, container):
        self.container = container

    def register_subevent(self, subevent):
        """Return the event with the latest end time."""
        raise NotImplementedError()

    def unregister_subevent(self, subevent):
        """Return the event with the latest end time."""
        raise NotImplementedError()

    def update(self, subevent):
        """Update container properties when adding a new sub-event."""
        raise NotImplementedError()
