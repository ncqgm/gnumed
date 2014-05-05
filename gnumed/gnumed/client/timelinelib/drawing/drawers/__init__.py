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


GRAY_FACTOR = 1.2
LUMINENCE_FACTOR = 0.8


def get_progress_color(base_color):
    """
    Return a color that is slightly brighter then the base_color.
    For shades of gray the constant GRAY_FACTOR decides the brightness.
    Higher factor gives more brightness.
    For other colors the LUMINENCE_FACTOR decides the brightness.
    Smaller factor gives more brightness.
    """
    if min(base_color) == max(base_color):
        return adjust_gray_luminence(base_color)
    else:
        return adjust_color_luminence(base_color)


def adjust_gray_luminence(base_color):
    r = apply_gray_factor_on_item(base_color[0])
    g = apply_gray_factor_on_item(base_color[1])
    b = apply_gray_factor_on_item(base_color[2])
    return (r, g, b)


def apply_gray_factor_on_item(item):
    return min(255, int(GRAY_FACTOR * item))
    
    
def adjust_color_luminence(base_color):
    h, s, l = rgb2hsl(base_color)
    l = LUMINENCE_FACTOR * s
    return  hsl2rgb(h, s, l)


def rgb2hsl(color):
    r = float(color[0]) / 255.0
    g = float(color[1]) / 255.0
    b = float(color[2]) / 255.0
    var_min = min(r, g, b)
    var_max = max(r, g, b)
    del_max = var_max - var_min
    l = (var_max + var_min) / 2.0
    if del_max == 0:
        h = 0
        s = 0
    else:
        if l < 0.5:
            s = del_max / (var_max + var_min)
        else:
            s = del_max / (2.0 - var_max - var_min)
        del_r = (((var_max - r) / 6.0) + (del_max / 2.0)) / del_max
        del_g = (((var_max - g) / 6.0) + (del_max / 2.0)) / del_max
        del_b = (((var_max - b) / 6.0) + (del_max / 2.0)) / del_max

        if (r == var_max):
            h = del_b - del_g
        elif (g == var_max):
            h = (1.0 / 3.0) + del_r - del_b
        elif (b == var_max):
            h = (2.0 / 3.0) + del_g - del_r
        if (h < 0):
            h += 1.0
        if (h > 1.0):
            h -= 1.0
    return (h, s, l)


def hsl2rgb(h, s, l):
    if s == 0:
        r = l * 155
        g = l * 255
        b = l * 255
    else:
        if (l < 0.5):
            var_2 = l * (1.0 + s)
        else:
            var_2 = (l + s) - (s * l)
        var_1 = 2.0 * l - var_2;
        r = 255 * hue_2_rgb(var_1, var_2, h + (1.0 / 3.0));
        g = 255 * hue_2_rgb(var_1, var_2, h);
        b = 255 * hue_2_rgb(var_1, var_2, h - (1.0 / 3.0));
    return (r, g, b)


def hue_2_rgb(v1, v2, vh):
    if (vh < 0):
        vh += 1.0
    if (vh > 1.0):
        vh -= 1.0
    if ((6.0 * vh) < 1):
        return (v1 + (v2 - v1) * 6.0 * vh)
    if ((2.0 * vh) < 1.0):
        return (v2)
    if ((3.0 * vh) < 2.0):
        x = (v1 + (v2 - v1) * ((2.0 / 3.0 - vh) * 6.0))
        return x
    return v1
