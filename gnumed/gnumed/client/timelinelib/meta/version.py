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


import sys


TYPE_DEV = "development"
TYPE_BETA = "beta"
TYPE_FINAL = ""
VERSION = (2, 0, 0)
TYPE = TYPE_DEV
REVISION_HASH = ""
REVISION_DATE = ""


def get_full_version():
    parts = []
    parts.append(get_version_number_string())
    if TYPE:
        parts.append(TYPE)
    if (REVISION_HASH or REVISION_DATE):
        revision_parts = []
        if REVISION_HASH:
            revision_parts.append(REVISION_HASH)
        if REVISION_DATE:
            revision_parts.append(REVISION_DATE)
        parts.append("(%s)" % " ".join(revision_parts))
    return " ".join(parts)


def get_filename_version():
    parts = []
    parts.append("timeline")
    parts.append(get_version_number_string())
    if not is_final():
        parts.append(TYPE)
        parts.append(REVISION_HASH)
        parts.append(REVISION_DATE)
    return "-".join(parts)


def get_version_number_string():
    return "%s.%s.%s" % VERSION


def is_dev():
    return TYPE == TYPE_DEV


def is_final():
    return TYPE == TYPE_FINAL
