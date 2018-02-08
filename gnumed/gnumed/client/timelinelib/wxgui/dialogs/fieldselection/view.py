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

from timelinelib.wxgui.dialogs.fieldselection.controller import FieldSelectionDialogController
from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.utils import BORDER


class FieldSelectionDialog(Dialog):

    """
    <BoxSizerVertical name="sizer">
        <StaticBoxSizerVertical label="$(description_text)" name="box" border="ALL"/>
        <DialogButtonsOkCancelSizer  border="BOTTOM|LEFT|RIGHT"/>
    </BoxSizerVertical>
    """

    def __init__(self, parent, title, data, fields):
        self.static_box = None
        Dialog.__init__(self, FieldSelectionDialogController, parent, {
            "description_text": _("Select Fields to Export")
        }, title=title)
        self.controller.on_init(data, fields)

    def CreateFieldCheckboxes(self, all_fields, fields):
        self.cbxs = []
        for field in all_fields:
            cbx = wx.CheckBox(self, label=field)
            cbx.SetValue(field in fields)
            self.cbxs.append(cbx)
            self.box.Add(cbx, flag=wx.EXPAND | wx.ALL, border=BORDER)
        self.SetSizerAndFit(self.sizer)

    def GetFields(self):
        fields = []
        for cbx in self.cbxs:
            fields.append((cbx.GetLabel(), cbx.IsChecked()))
        return fields

    def GetSelectedFields(self):
        return self.controller.get_selected_fields()
