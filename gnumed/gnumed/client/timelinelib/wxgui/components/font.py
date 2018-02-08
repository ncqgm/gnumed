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


import wx


FONT_FACE_ENCODING = "utf-8"


class Font(wx.Font):

    def __init__(self, point_size=12, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
                 weight=wx.FONTWEIGHT_NORMAL, underlined=False, face_name="", encoding=wx.FONTENCODING_DEFAULT,
                 wxcolor=wx.BLACK):
        self.wxcolor = wxcolor
        wx.Font.__init__(self, point_size, family, style, weight, underlined, face_name, encoding)

    def _get_wxcolor(self):
        return self.wxcolor

    def _set_wxcolor(self, wxcolor):
        self.wxcolor = wxcolor

    WxColor = property(_get_wxcolor, _set_wxcolor)

    def _get_wxfont(self):
        return self

    def _set_wxfont(self, wxfont):
        self.PointSize = wxfont.PointSize
        self.Family = wxfont.Family
        self.Style = wxfont.Style
        self.Weight = wxfont.Weight
        self.SetUnderlined(wxfont.GetUnderlined())
        self.FaceName = wxfont.FaceName
        self.Encoding = wxfont.Encoding

    WxFont = property(_get_wxfont, _set_wxfont)

    def serialize(self):
        return "%s:%s:%s:%s:%s:%s:%s:%s" % (
            self.PointSize,
            self.Family,
            self.Style,
            self.Weight,
            self.GetUnderlined(),
            self.FaceName.encode(FONT_FACE_ENCODING),
            self.Encoding,
            self.WxColor,
        )

    def increment(self, step=2):
        self.PointSize += step

    def decrement(self, step=2):
        self.PointSize -= step


# Profiling of timelinelib\wxgui\components\font.py:63(deserialize_font)
#
# Open Timeline and drag-scroll 10 times back and forth with the mouse.
#
# Before caching Font info:
#          ncalls  tottime  percall  cumtime  percall
# Try 1:     4265    0.154    0.000    0.610    0.000
# Try 2:     4395    0.154    0.000    0.613    0.000
# Try 3:     3801    0.133    0.000    0.528    0.000
# Try 4:     4430    0.152    0.000    0.607    0.000
# Try 5:     3926    0.139    0.000    0.553    0.000
#
# After caching Font info:
# Try 1:     3894    0.004    0.000    0.004    0.000
# Try 2:     5246    0.005    0.000    0.005    0.000
# Try 3:     4972    0.004    0.000    0.005    0.000
# Try 4:     4611    0.004    0.000    0.005    0.000
# Try 5:     3306    0.003    0.000    0.003    0.000

font_cache = {}


def deserialize_font(serialized_font):
    if serialized_font not in font_cache:
        bool_map = {"True": True, "False": False}
        (
            point_size,
            family,
            style,
            weight,
            underlined,
            facename,
            encoding,
            color,
        ) = serialized_font.split(":")
        color_args = color[1:-1].split(",")
        wxcolor = wx.Colour(
            int(color_args[0]),
            int(color_args[1]),
            int(color_args[2]),
            int(color_args[3])
        )
        font = Font(
            int(point_size),
            int(family),
            int(style),
            int(weight),
            bool_map[underlined],
            facename.decode(FONT_FACE_ENCODING),
            int(encoding),
            wxcolor
        )
        font_cache[serialized_font] = font
    return font_cache[serialized_font]


def set_minor_strip_text_font(font, dc, force_bold=False, force_normal=False, force_italic=False, force_upright=False):
    set_text_font(font, dc, force_bold, force_normal, force_italic, force_upright)


def set_major_strip_text_font(font, dc, force_bold=False, force_normal=False, force_italic=False, force_upright=False):
    set_text_font(font, dc, force_bold, force_normal, force_italic, force_upright)


def set_balloon_text_font(font, dc, force_bold=False, force_normal=False, force_italic=False, force_upright=False):
    set_text_font(font, dc, force_bold, force_normal, force_italic, force_upright)


def set_legend_text_font(font, dc):
    set_text_font(font, dc)


def set_text_font(selectable_font, dc, force_bold=False, force_normal=False, force_italic=False, force_upright=False):
    font = deserialize_font(selectable_font)
    old_weight = font.Weight
    old_style = font.Style
    if force_bold:
        font.Weight = wx.FONTWEIGHT_BOLD
    elif force_normal:
        font.Weight = wx.FONTWEIGHT_NORMAL
    if force_italic:
        font.Style = wx.FONTSTYLE_ITALIC
    elif force_upright:
        font.Style = wx.FONTSTYLE_NORMAL
    dc.SetFont(font)
    dc.SetTextForeground(font.WxColor)
    font.Style = old_style
    font.Weight = old_weight


def edit_font_data(parent_window, font):
    data = wx.FontData()
    data.SetInitialFont(font)
    data.SetColour(font.WxColor)
    dialog = wx.FontDialog(parent_window, data)
    try:
        if dialog.ShowModal() == wx.ID_OK:
            font_data = dialog.GetFontData()
            font.WxFont = font_data.GetChosenFont()
            font.WxColor = font_data.GetColour()
            return True
        else:
            return False
    finally:
        dialog.Destroy()
