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


def ex_msg(e):
    """Return exception error string."""
    try:
        return str(e)
    except UnicodeEncodeError:
        if len(e.args) == 1:
            return e.args[0]
        else:
            # Exceptions raised by Timeline (the only ones that might be
            # unicode) should always contain a single unicode message. So we
            # should never end up here.
            return ""
