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


import os.path


_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_ROOT = _ROOT.decode("utf-8")
_ICONROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ICONROOT = _ICONROOT.decode("utf-8")
ICONS_DIR = os.path.join(_ICONROOT, u"tlicons")
EVENT_ICONS_DIR = os.path.join(_ICONROOT, u"tlicons", u"event_icons")
LOCALE_DIR = os.path.join(_ROOT, u"translations")
HELP_RESOURCES_DIR = os.path.join(_ROOT, u"help_resources")
