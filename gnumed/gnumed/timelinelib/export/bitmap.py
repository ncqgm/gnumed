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


import os.path

import wx

from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import WildcardHelper


def export_to_image(main_frame):
    images_wildcard_helper = WildcardHelper(
        _("Image files"), [("png", wx.BITMAP_TYPE_PNG)])
    wildcard = images_wildcard_helper.wildcard_string()
    dialog = wx.FileDialog(main_frame, message=_("Export to Image"),
                           wildcard=wildcard, style=wx.FD_SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = images_wildcard_helper.get_path(dialog)
        overwrite_question = _("File '%s' exists. Overwrite?") % path
        if (not os.path.exists(path) or
            _ask_question(overwrite_question, main_frame) == wx.YES):
            bitmap = main_frame.main_panel.drawing_area.get_current_image()
            image = wx.ImageFromBitmap(bitmap)
            type = images_wildcard_helper.get_extension_data(path)
            image.SaveFile(path, type)
    dialog.Destroy()
