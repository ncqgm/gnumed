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


# A category was added, edited, or deleted
STATE_CHANGE_CATEGORY = 1
# Something happened that changed the state of the timeline
STATE_CHANGE_ANY = 2
# A timer ticked
TIMER_TICK = 3


class Observable(object):

    def __init__(self):
        self._observers = []
        self._listeners = []

    def listen_for(self, event, function):
        self._listeners.append((True, event, function))

    def listen_for_any(self, function):
        self._listeners.append((False, None, function))

    def unlisten(self, function):
        self._listeners = [x for x in self._listeners if x[2] != function]

    def register(self, fn):
        self._observers.append(fn)

    def unregister(self, fn):
        if fn in self._observers:
            self._observers.remove(fn)

    def _notify(self, state_change=None):
        for (listen_for_specific, event, function) in self._listeners:
            if listen_for_specific:
                if state_change == event:
                    function()
            else:
                function()
        for fn in self._observers:
            fn(state_change)
