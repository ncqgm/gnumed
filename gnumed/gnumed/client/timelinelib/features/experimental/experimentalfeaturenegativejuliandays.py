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


from timelinelib.calendar.gregorian.time import GregorianTime
from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature


CONFIG_NAME = "Accept negative Julian days"
DISPLAY_NAME = _("Accept negative Julian days")
DESCRIPTION = _("""
              Enables the use of dates before Julian day = 0 (4713 BC)

              This means that prehistorical dates can be used.
              We are not quiet sure that the calculations works correctly
              for negative julian days and therefore it's an experimental feature.

              Be aware of the fact that a timeline created with this feature active,
              may not be readable with Timeline if the feature is switched off.
              """)


class ExperimentalFeatureNegativeJulianDays(ExperimentalFeature):

    def __init__(self):
        ExperimentalFeature.__init__(self, DISPLAY_NAME, DESCRIPTION, CONFIG_NAME)

    def set_active(self, value):
        self.active = value
        GregorianTime.set_min_julian_day(value)
