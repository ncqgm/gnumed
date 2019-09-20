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


import wx.adv

from timelinelib.meta.version import get_full_version


APPLICATION_NAME = "Timeline"
COPYRIGHT_TEXT = "Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019 The %s Authors" % APPLICATION_NAME
APPLICATION_DESCRIPTION = "Timeline is a free, cross-platform application for displaying and navigating events on a timeline."
WEBSITE = "http://thetimelineproj.sourceforge.net/"
DEVELOPERS = [
    "Developers:",
    "    Rickard Lindberg",
    "    Roger Lindberg",
    "Contributors:",
    "    Alan Jackson",
    "    Glenn J. Mason",
    "    Joe Gilmour",
    "    Thomas Mohr",
    "    Linostar",
    "    Norbert Langermann",
    "    Jean-Gilles Guyrandy",
]
TRANSLATORS = [
    "Basque:",
    "    Urtzi Odriozola",
    "Brazilian Portuguese:",
    "    Leo Frigo",
    "    Marcelo Ribeiro de Almeida",
    "    Waldir Leôncio",
    "Catalan:",
    "    BennyBeat",
    "Chinese (Simplified):",
    "    rockxie",
    "French:",
    "    Francois Tissandier",
    "German:",
    "    MixCool",
    "    Nils Steinger",
    "    Daniel Winzen",
    "    cmdrhenner",
    "    Norbert Langermann",
    "Greek:",
    "    Yannis Kaskamanidis",
    "Hebrew:",
    "    Yaron Shahrabani",
    "Lithuanian:",
    "    Mantas Kriauciunas",
    "    rpocius",
    "Polish:",
    "    Andrzej Korcala 'Greybrow'",
    "Portuguese:",
    "    Leo Frigo",
    "Russian:",
    "    Andrew Yakush",
    "    Sergey Sedov",
    "    Alexander 'FONTER' Zinin",
    "    DronAn[BY]",
    "Spanish:",
    "    Leandro Pavón Serrano",
    "    Leo Frigo",
    "    Roman Gelbort",
    "    Sebastián Ortega",
    "Swedish:",
    "    Rickard Lindberg",
    "    Roger Lindberg",
    "    Daniel Nylander",
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


def display_about_dialog(args, *kwargs):
    info = wx.adv.AboutDialogInfo()
    info.Name = APPLICATION_NAME
    info.Version = get_full_version()
    info.Copyright = COPYRIGHT_TEXT
    info.Description = APPLICATION_DESCRIPTION
    info.WebSite = (WEBSITE, "%s Website" % APPLICATION_NAME)
    info.Developers = DEVELOPERS
    info.Translators = TRANSLATORS
    info.Artists = ARTISTS
    info.License = LICENSE
    wx.adv.AboutBox(info)
