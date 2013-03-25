# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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


from optparse import OptionParser
import os.path

from timelinelib.meta.version import get_version

import wx


class ApplicationArguments(object):

    def __init__(self):
        version_string = "%prog " + get_version()
        self.option_parser = OptionParser(
            usage="%prog [options] [filename]",
            version=version_string)
        self.option_parser.add_option(
            "-c", "--config-file", dest="config_file_path", default=None,
            help="Path to config file")

    def parse_from(self, arguments):
        (self.options, self.arguments) = self.option_parser.parse_args(arguments)

    def get_files(self):
        return self.arguments

    def get_config_file_path(self):
        if self.options.config_file_path:
            return self.options.config_file_path
        else:
            return os.path.join(
                wx.StandardPaths.Get().GetUserConfigDir(),
                ".thetimelineproj.cfg")
