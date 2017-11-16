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


import os

import wx

from timelinelib.plugin.factory import EXPORTER
from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import WildcardHelper


class SvgExporter(PluginBase):

    def service(self):
        return EXPORTER

    def display_name(self):
        return _("Export to SVG...")

    def wxid(self):
        from timelinelib.wxgui.frames.mainframe.guicreator import ID_EXPORT_SVG
        return ID_EXPORT_SVG

    def run(self, main_frame):
        if not has_pysvg_module():
            display_error_message(_("Could not find pysvg Python package. It is needed to export to SVG."), self)
            return
        helper = WildcardHelper(_("SVG files"), ["svg"])
        wildcard = helper.wildcard_string()
        dialog = wx.FileDialog(main_frame, message=_("Export to SVG"), wildcard=wildcard, style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path = helper.get_path(dialog)
            overwrite_question = _("File '%s' exists. Overwrite?") % path
            if (not os.path.exists(path) or _ask_question(overwrite_question, main_frame) == wx.YES):
                main_frame.main_panel.timeline_panel.timeline_canvas.SaveAsSvg(path)
        dialog.Destroy()


def has_pysvg_module():
    try:
        import pysvg
        return True
    except ImportError:
        return False
