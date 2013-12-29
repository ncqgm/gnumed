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


VERSION = (1, 1, 0)
DEV = False


def get_version():
    if DEV:
        return ("%s.%s.%sdev" % VERSION) + DEV_REVISION
    return "%s.%s.%s" % VERSION


def _get_revision():
    try:
        import os
        from subprocess import Popen, PIPE
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        cmd = ["hg", "id", "-i", "-R", root]
        rev = Popen(cmd, stdout=PIPE).communicate()[0].strip()
        return rev
    except:
        return "0"


if DEV:
    DEV_REVISION = _get_revision()
