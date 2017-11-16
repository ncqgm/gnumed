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


from ConfigParser import DEFAULTSECT
from ConfigParser import SafeConfigParser

from timelinelib.general.observer import Observable


class Config(Observable):

    def __init__(self, item_dicts):
        Observable.__init__(self)
        self._config_parser = SafeConfigParser()
        self._build(item_dicts)

    def read(self, path):
        self._config_parser.read(path)

    def write(self, path):
        with open(path, "wb") as f:
            self._config_parser.write(f)

    def _build(self, item_dicts):
        for item_dict in item_dicts:
            self._build_item(Item(item_dict))

    def _build_item(self, item):
        def getter():
            return item.get_decoder()(self._config_parser.get(
                item.get_section(),
                item.get_config_name()
            ))

        def setter(value):
            self._config_parser.set(
                item.get_section(),
                item.get_config_name(),
                item.get_encoder()(value)
            )
            self._notify()
        setattr(self, "get_%s" % item.get_name(), getter)
        setattr(self, "set_%s" % item.get_name(), setter)
        setter(item.get_default())


class Item(object):

    def __init__(self, item_dict):
        self._item_dict = item_dict

    def get_name(self):
        return self._item_dict["name"]

    def get_config_name(self):
        return self._item_dict.get("config_name", self.get_name())

    def get_section(self):
        return DEFAULTSECT

    def get_default(self):
        return self._item_dict["default"]

    def get_encoder(self):
        return {
            "text": self._text_to_string,
            "integer": str,
            "boolean": str,
        }[self._get_data_type()]

    def get_decoder(self):
        return {
            "text": self._string_to_text,
            "integer": int,
            "boolean": self._string_to_bool,
        }[self._get_data_type()]

    def _get_data_type(self):
        return self._item_dict.get("data_type", "text")

    def _text_to_string(self, text):
        if isinstance(text, unicode):
            return text.encode("utf-8")
        else:
            return text

    def _string_to_text(self, string):
        return string.decode("utf-8")

    def _string_to_bool(self, string):
        return {
            "true": True,
            "false": False,
        }[string.lower()]
