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


def _(message):
    return message  # deferred translation


BOSP_ENGLISH_MONTH_NAMES = [
    _("Praios"),
    _("Rondra"),
    _("Efferd"),
    _("Travia"),
    _("Boron"),
    _("Hesinde"),
    _("Firun"),
    _("Tsa"),
    _("Phex"),
    _("Peraine"),
    _("Ingerimm"),
    _("Rahja"),
    _("Nameless Days")
]


BOSP_ABBREVIATED_ENGLISH_MONTH_NAMES = [
    _("PRA"),
    _("RON"),
    _("EFF"),
    _("TRA"),
    _("BOR"),
    _("HES"),
    _("FIR"),
    _("TSA"),
    _("PHE"),
    _("PER"),
    _("ING"),
    _("RAH"),
    _("NL"),
]
del _


def bosp_month_from_english_name(month_name):
    return BOSP_ENGLISH_MONTH_NAMES.index(month_name) + 1


def bosp_name_of_month(month):
    return _(BOSP_ENGLISH_MONTH_NAMES[month - 1])


def bosp_abbreviated_name_of_month(month):
    return _(BOSP_ABBREVIATED_ENGLISH_MONTH_NAMES[month - 1])


def bosp_month_from_abbreviated_name(month_name):
    i = 0
    for mn in BOSP_ABBREVIATED_ENGLISH_MONTH_NAMES:
        i += 1
        if _(mn) == month_name:
            return i
    return 13
