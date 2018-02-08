# -*- coding: utf-8 -*-
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


"""\
Defines and handle Timeline features.

A feature in Timeline can come in several flavours.
   * Installed
   * Experimental

An installed feature is functionality that is built and implemented in
Timeline. A Timeline user can give feedback on an installed feature
through a menu selection in the Help menu.

An experimental feature is functionality that we want to test and see
how it works and how it is liked by the users. It is not yet decided
if it will become a part of Timeline.
The user has the option to switch an experimental feature on or off
in the Timeline Edit->Preferences dialog.
As with installed features the user can give feedback on experimental
features through a menu selection in the Help menu.
"""
