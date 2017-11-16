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


"""
ExperimentalFeature:  Common base class for all experimental features.
"""


from timelinelib.features.feature import Feature


class ExperimentalFeature(Feature):

    def __init__(self, display_name, description, config_name=""):
        Feature.__init__(self, display_name, description, config_name)
        self.active = False

    def set_active(self, value):
        self.active = value

    def enabled(self):
        return self.active

    def get_config(self):
        return "%s=%s;" % (self.config_name.encode("utf-8"), str(self.active))
