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
The ApplicationArguments class parses the command line arguments and
options when the application is started.

If the application is started with:
    python3 timeline.py -h
    
a text will be displayed that describes valid arguments and valid
options.

:doc:`Tests are found here <unit_config_arguments>`.
"""


from optparse import OptionParser
import os.path

from timelinelib.meta.version import get_full_version

import wx


class ApplicationArguments(object):

    def __init__(self):
        self._option_parser = self._create_option_parser()
        self._create_config_file_option()
        self._create_debug_option()

    def parse_from(self, arguments):
        (self.options, self.arguments) = self._option_parser.parse_args(arguments)

    def get_files(self):
        return self.arguments

    def get_first_file(self):
        try:
            return self.arguments[0]
        except IndexError:
            return None

    def has_files(self):
        return len(self.arguments) > 0

    def get_debug_flag(self):
        return self.options.debug

    def get_config_file_path(self):
        if self.options.config_file_path:
            return self.options.config_file_path
        else:
            return os.path.join(
                wx.StandardPaths.Get().GetUserConfigDir(),
                ".thetimelineproj.cfg")

    def _create_option_parser(self):
        return OptionParser(
            usage="%prog [options] [filename]",
            version=self._create_version_string())
        
    def _create_version_string(self):
        return "%prog " + get_full_version()
    
    def _create_config_file_option(self):
        self._option_parser.add_option(
            "-c", "--config-file", dest="config_file_path", default=None,
            help="Path to config file")

    def _create_debug_option(self):
        self._option_parser.add_option(
            "--debug",
            default=False, action="store_true",
            help="Run Timeline with extra debug output")
    
