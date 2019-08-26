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


"""

"""


import os

import wx

from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import WildcardHelper
from timelinelib.wxgui.utils import display_warning_message
from timelinelib.proxies.drawingarea import DrawingAreaProxy


EXPORTER = "exporter"


def export_to_image(main_frame):
    path = _get_image_path(main_frame)
    if path is not None and _overwrite_existing_path(main_frame, path):
        main_frame.main_panel.timeline_panel.timeline_canvas.SaveAsPng(path)


def export_to_images(main_frame):
    path = _get_image_path(main_frame)
    if path is not None:
        try:
            periods, current_period = main_frame.get_export_periods()
        except ValueError:
            msg = _("The first image contains a Julian day < 0\n\nNavigate to first event or\nUse the feature 'Accept negative Julian days'")
            display_warning_message(msg)
            return
        view_properties = DrawingAreaProxy(main_frame).view_properties
        view_properties.set_use_fixed_event_vertical_pos(True)
        path_without_extension, extension = path.rsplit(".", 1)
        view_properties.set_use_fixed_event_vertical_pos(True)
        view_properties.periods = periods
        count = 1
        paths = []
        for period in periods:
            path = "%s_%d.%s" % (path_without_extension, count, extension)
            if _overwrite_existing_path(main_frame, path):
                main_frame.main_panel.timeline_panel.timeline_canvas.Navigate(lambda tp: period)
                main_frame.main_panel.timeline_panel.timeline_canvas.SaveAsPng(path)
            count += 1
            paths.append(path)
        view_properties.set_use_fixed_event_vertical_pos(False)
        main_frame.main_panel.timeline_panel.timeline_canvas.Navigate(lambda tp: current_period)
        merged_image_path = "%s_merged.%s" % (path_without_extension, extension)
        merge_images(paths, merged_image_path)


def _get_image_path(main_frame):
    path = None
    file_info = _("Image files")
    file_types = [("png", wx.BITMAP_TYPE_PNG)]
    images_wildcard_helper = WildcardHelper(file_info, file_types)
    wildcard = images_wildcard_helper.wildcard_string()
    dialog = wx.FileDialog(main_frame, message=_("Export to Image"), wildcard=wildcard, style=wx.FD_SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = images_wildcard_helper.get_path(dialog)
    dialog.Destroy()
    return path


def _overwrite_existing_path(main_frame, path):
    if os.path.exists(path):
        overwrite_question = _("File '%s' exists. Overwrite?") % path
        return _ask_question(overwrite_question, main_frame) == wx.YES
    return True


def merge_images(images_paths, merged_image_path):
    from PIL import Image
    images = map(Image.open, images_paths)
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for image in images:
        new_image.paste(image, (x_offset, 0))
        x_offset += image.size[0]
    new_image.save(merged_image_path)
