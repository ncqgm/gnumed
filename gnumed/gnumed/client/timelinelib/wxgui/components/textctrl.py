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


class TextCtrl(wx.TextCtrl):

    """
    TextCtrl enhances wx.TextCtrl.

    It takes an optional `fit_text` keyword argument. If given, the TextCtrl is
    resized to fit that text.
    """

    def __init__(self, *args, **kwargs):
        fit_text = kwargs.pop("fit_text", None)
        wx.TextCtrl.__init__(self, *args, **kwargs)
        if fit_text is not None:
            self._fit_text(fit_text)

    def _fit_text(self, text):
        (w, h) = self.GetTextExtent(text)
        self.SetInitialSize((w + 20, -1))
