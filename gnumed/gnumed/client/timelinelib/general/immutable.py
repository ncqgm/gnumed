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


class ImmutableDict(tuple):

    def __new__(cls, *args, **kwargs):
        if (len(args) == 1 and
            len(kwargs) == 0 and
            isinstance(args[0], _AlreadyCopiedDict)):
            d = args[0].value
        else:
            d = {}
            for arg in args:
                d.update(arg)
            for key, value in kwargs.iteritems():
                d[key] = value
        return tuple.__new__(cls, (d,))

    @property
    def _internal(self):
        return tuple.__getitem__(self, 0)

    def update(self, *args, **kwargs):
        return self.__class__(self._internal, *args, **kwargs)

    def remove(self, key):
        new = {}
        new.update(self._internal)
        del new[key]
        return self.__class__(_AlreadyCopiedDict(new))

    def map(self, fn):
        return self.__class__(_AlreadyCopiedDict({
            key: fn(value)
            for key, value
            in self._internal.iteritems()
        }))

    def get(self, name, default=None):
        return self._internal.get(name, default)

    def __len__(self):
        return len(self._internal)

    def __contains__(self, item):
        return item in self._internal

    def __getitem__(self, name):
        return self._internal[name]

    def __iter__(self):
        return self._internal.iteritems()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self._internal == other._internal
        )

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        items = []
        items.append(self.__class__.__name__)
        items.append("({\n")
        for key, value in self:
            items.append("  ")
            items.append(repr(key))
            items.append(": ")
            for index, line in enumerate(repr(value).split("\n")):
                if index > 0:
                    items.append("\n  ")
                items.append(line)
            items.append(",\n")
        items.append("})")
        return "".join(items)


class ImmutableRecordMeta(type):

    def __new__(cls, name, bases, attrs):
        def create_property(name):
            return property(
                lambda self: self.get(name)
            )
        base_attributes = []
        for base in bases:
            base_attributes.extend(dir(base))
        fields = {}
        for key, value in list(attrs.iteritems()):
            if isinstance(value, Field):
                if key in base_attributes:
                    raise ValueError(
                        "{0!r} is a reserved field name".format(key)
                    )
                fields[key] = value
                attrs[key] = create_property(key)
        attrs["_immutable_record_fields"] = fields
        return super(ImmutableRecordMeta, cls).__new__(cls, name, bases, attrs)


class Field(object):

    def __init__(self, default=None):
        self.default = default


class ImmutableRecord(ImmutableDict):

    __metaclass__ = ImmutableRecordMeta

    def __new__(cls, *args, **kwargs):
        defaults = {
            key: value.default
            for key, value
            in cls._immutable_record_fields.iteritems()
        }
        d = ImmutableDict.__new__(cls, defaults, *args, **kwargs)
        for key, value in d:
            if key not in cls._immutable_record_fields:
                raise ValueError("{0!r} is not a valid field of {1}".format(
                    key,
                    cls.__name__
                ))
        return d


class _AlreadyCopiedDict(object):

    """
    A special value that can be passed as the single value to the constructor
    of ImmutableDict to prevent unnecessary copying.
    """

    def __init__(self, value):
        self.value = value
