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

from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonssizer import DialogButtonsSizer


class DialogButtonsEditAddRemoveCloseSizer(DialogButtonsSizer):

    def __init__(self, parent):
        DialogButtonsSizer.__init__(self, parent)
        parent.btn_edit = wx.Button(parent, wx.ID_EDIT)
        parent.btn_add = wx.Button(parent, wx.ID_ADD)
        parent.btn_remove = wx.Button(parent, wx.ID_REMOVE)
        parent.btn_close = wx.Button(parent, wx.ID_CLOSE)
        self.buttons = (parent.btn_edit, parent.btn_add, parent.btn_remove, parent.btn_close)
        self.default = 3
        self.AddButtons(self.buttons, self.default)
        parent.SetEscapeId(wx.ID_ANY)
        parent.SetAffirmativeId(wx.ID_CLOSE)
