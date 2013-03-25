# -*- coding: utf-8 -*-
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


import wx

from timelinelib.meta.version import get_version


APPLICATION_NAME = "Timeline"
COPYRIGHT_TEXT = "Copyright (C) 2009, 2010, 2011 The %s Authors" % APPLICATION_NAME
APPLICATION_DESCRIPTION = "Timeline is a free, cross-platform application for displaying and navigating events on a timeline."
WEBSITE = "http://thetimelineproj.sourceforge.net/"
DEVELOPERS = [
    u"Developers:",
    u"    Rickard Lindberg",
    u"    Roger Lindberg",
    u"Contributors:",
    u"    Alan Jackson",
    u"    Glenn J. Mason",
    u"    Joe Gilmour",
    u"    Thomas Mohr",
]
TRANSLATORS = [
    u"Brazilian Portuguese:",
    u"    Leo Frigo",
    u"    Marcelo Ribeiro de Almeida",
    u"    Waldir Leôncio",
    u"Catalan:",
    u"    BennyBeat",
    u"French:",
    u"    Francois Tissandier",
    u"German:",
    u"    MixCool",
    u"    Nils Steinger",
    u"Hebrew:",
    u"    Yaron Shahrabani",
    u"Polish:",
    u"    Andrzej Korcala 'Greybrow'",
    u"Portuguese:",
    u"    Leo Frigo",
    u"Russian:",
    u"    Andrew Yakush",
    u"    Sergey Sedov",
    u"Spanish:",
    u"    Leandro Pavón Serrano",
    u"    Leo Frigo",
    u"    Roman Gelbort",
    u"    Sebastián Ortega",
    u"Swedish:",
    u"    Rickard Lindberg",
    u"    Roger Lindberg",
]
ARTISTS = ["Sara Lindberg",
           "Tango Desktop Project (Icons on Windows)"]
LICENSE = """Timeline is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Timeline is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Timeline.  If not, see <http://www.gnu.org/licenses/>."""


def display_about_dialog():
    info = wx.AboutDialogInfo()
    info.Name = APPLICATION_NAME
    info.Version = get_version()
    info.Copyright = COPYRIGHT_TEXT
    info.Description = APPLICATION_DESCRIPTION
    info.WebSite = (WEBSITE, "%s Website" % APPLICATION_NAME)
    info.Developers = DEVELOPERS
    info.Translators = TRANSLATORS
    info.Artists = ARTISTS
    info.License = LICENSE
    wx.AboutBox(info)
