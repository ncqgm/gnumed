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
This is the main package of The Timeline Project.

The only code for running Timeline that is not in this package
is the module timeline.py. That is the main module for starting
the Timeline application.

Contains the boolean flag DEBUG_ENABLED. This flag is set with the
application argument --debug at start of Timeline. When enabled,
timer and counting statistics are shown in the main panel.
"""


DEBUG_ENABLED = False
