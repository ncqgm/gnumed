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


"""\
Defines properties common to all types of Timeline features.

All types of Timeline features must inherit from this bas class
"""


class Feature(object):

    def __init__(self, display_name, description, config_name=""):
        self.display_name = display_name
        self.description = description
        self.config_name = config_name

    def get_display_name(self):
        return self.display_name

    def get_description(self):
        return self.description

    def get_config_name(self):
        return self.config_name

