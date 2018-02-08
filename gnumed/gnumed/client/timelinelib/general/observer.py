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


class Listener(object):

    def __init__(self, callback):
        self._observable = None
        self._callback = callback

    def set_observable(self, observable):
        self._unlisten()
        self._observable = observable
        self._listen()

    def _unlisten(self):
        if self._observable is not None:
            self._observable.unlisten(self._listener)

    def _listen(self):
        if self._observable is not None:
            self._observable.listen_for_any(self._listener)
            self._listener()

    def _listener(self):
        self._callback(self._observable)
