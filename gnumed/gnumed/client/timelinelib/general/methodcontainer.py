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


from collections import defaultdict


class MethodContainer(object):

    def __init__(self, methods_kvp, default_method=None):
        self._default_method = default_method
        if self._all_keys_are_booleans(methods_kvp):
            if self._first_truthy_method(methods_kvp):
                self._container = defaultdict(self._default, [(True, self._first_truthy_method(methods_kvp))])
            else:
                self._container = defaultdict(self._default, [])
        else:
            self._container = defaultdict(self._default, methods_kvp)

    def select(self, key):
        return self._container[key]

    def _all_keys_are_booleans(self, methods_kvp):
        return len([m for k, m in methods_kvp if not isinstance(k, bool)]) == 0

    def _first_truthy_method(self, methods_kvp):
        for key, method in methods_kvp:
            if key:
                return method

    def _default(self):
        if self._default_method is None:
            return self._noop
        else:
            return self._default_method

    def _noop(self, *args, **kwargs):
        pass


