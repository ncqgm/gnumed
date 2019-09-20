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


BOSP_ABBREVIATED_WEEKDAY_NAMES = [
    _("Wind"),
    _("Earth"),
    _("Market"),
    _("Praios"),
    _("Rohal"),
    _("Fire"),
    _("Water"),
]
del _


def bosp_abbreviated_name_of_weekday(weekday):
    return _(BOSP_ABBREVIATED_WEEKDAY_NAMES[weekday])
