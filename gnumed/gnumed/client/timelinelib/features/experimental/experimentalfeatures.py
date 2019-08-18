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


"""
ExperimentalFeatures is responsible for reading and storing experimental features
   configuration, to and from the configuration file.
   It also holds a list of available experimental features.
   All experimental features are instantiated when this file is loaded.

To add a new experimental feature, do as follows:
    - Create a new file in timelinelib.features.experimental, defining a class
      that inherits from ExperimentalFeature and calls the parent __init__()-
      function with the two arguments DISPLAY_NAME and DESCRIPTION.
    - Instantiate the new experimental feature class in this file like...
        NAME = NewExperimentalFeatureClass()
    - Add the instantiated object to the FEATURES list in this file.
    - Implement the feature logic under the condition...
        if NAME.enabled():
    - If new methods are created that only are used by the new feature,
      decorate these functions with @experimental_feature(NAME)
"""


from timelinelib.features.experimental.experimentalfeaturecontainersize import ExperimentalFeatureContainerSize
from timelinelib.features.experimental.experimentalfeaturenegativejuliandays import ExperimentalFeatureNegativeJulianDays
from timelinelib.features.experimental.experimentalfeatureextendedcontainerstrategy import ExperimentalFeatureExtendedContainerStrategy


EXTENDED_CONTAINER_HEIGHT = ExperimentalFeatureContainerSize()
NEGATIVE_JULIAN_DAYS = ExperimentalFeatureNegativeJulianDays()
EXTENDED_CONTAINER_STRATEGY = ExperimentalFeatureExtendedContainerStrategy()
FEATURES = (EXTENDED_CONTAINER_HEIGHT, NEGATIVE_JULIAN_DAYS, EXTENDED_CONTAINER_STRATEGY)


class ExperimentalFeatureException(Exception):
    pass


class ExperimentalFeatures(object):

    def __str__(self):
        """
        Formats the configuration string for all experimental features,
        which is a semicolon separated list of feature configurations.
           features-configuration ::= (feature-configuration ';')*
           feature-configuration ::=  feature-name  '='  ('True'|'False')
        """
        collector = []
        for feature in FEATURES:
            collector.append(feature.get_config())
        return "".join(collector)

    def get_all_features(self):
        return FEATURES

    def set_active_state_on_all_features_from_config_string(self, cfg_string):
        for item in cfg_string.split(";"):
            if "=" in item:
                name, value = item.split("=")
                self.set_active_state_on_feature_by_name(name.strip(), value.strip() == "True")

    def set_active_state_on_feature_by_index(self, feature_index, value):
        FEATURES[feature_index].set_active(value)

    def set_active_state_on_feature_by_name(self, name, value):
        for feature in FEATURES:
            if feature.get_config_name() == name:
                feature.set_active(value)
                return
            elif feature.get_display_name() == name:
                feature.set_active(value)
                return


def experimental_feature(feature):
    """
    The syntax for decorators with arguments is a bit different - the decorator
    with arguments should return a function that will take a function and return
    another function. So it should really return a normal decorator.

    Decorator used for methods, only used by an Experimental feature.
    The purpose of the decorator is to simplify removal of the feature
    code if it is decided not to implement the feature.
    Example:
       @experimental_feature(EVENT_DONE)
       def foo()
           pass
    """
    def deco(foo):
        if feature not in FEATURES:
            raise ExperimentalFeatureException("Feature '%s', not implemented" % feature.get_display_name())
        return foo
    return deco
