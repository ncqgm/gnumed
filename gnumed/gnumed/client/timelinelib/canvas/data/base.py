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


class ItemBase(object):

    def __init__(self, db, id_, immutable_value):
        self._db = db
        self._id = id_
        self._immutable_value = immutable_value

    def duplicate(self, target_db=None):
        if target_db is None:
            db = self.db
        else:
            db = target_db
        return self.__class__(db=db, immutable_value=self._immutable_value)

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, value):
        if self._db is None:
            self._db = value
        elif self._db is not value:
            raise ValueError("Can't change db")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def get_id(self):
        return self.id

    def has_id(self):
        return self.id is not None

    def set_id(self, id_):
        self.id = id_
        return self

    def ensure_id(self):
        if self.id is None:
            self.id = self.db.next_id()
        return self.id


def create_noop_property(klass, name, value):
    def getter(self):
        return value

    def setter(self, value):
        return self
    setattr(klass, "get_{0}".format(name), getter)
    setattr(klass, "set_{0}".format(name), setter)
    setattr(klass, "{0}".format(name), property(getter, setter))
