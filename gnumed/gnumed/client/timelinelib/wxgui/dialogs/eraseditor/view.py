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


import wx

from timelinelib.wxgui.dialogs.eraseditor.controller import ErasEditorDialogController
from timelinelib.wxgui.framework import Dialog


class ErasEditorDialog(Dialog):

    """
    <BoxSizerVertical>
        <ListBox name="lb_eras" border="ALL" proportion="1" height="250"
            event_EVT_LISTBOX_DCLICK="on_dclick"
        />
        <DialogButtonsEditAddRemoveCloseSizer border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_ADD="on_add"
            event_EVT_BUTTON__ID_REMOVE="on_remove"
            event_EVT_BUTTON__ID_EDIT="on_edit"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, db, config):
        Dialog.__init__(self, ErasEditorDialogController, parent, {},
                        title=_("Edit Era's"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init(db, config)

    def SetEras(self, eras):
        for era in eras:
            self.lb_eras.Append(era.get_name(), era)
        if len(eras) > 0:
            self.lb_eras.SetSelection(0)
        self._EnableDisableButtons()

    def GetSelectedEra(self):
        return self.lb_eras.GetClientData(self.lb_eras.GetSelection())

    def UpdateEra(self, era):
        self.lb_eras.SetString(self.lb_eras.GetSelection(), era.get_name())

    def AppendEra(self, era):
        self.lb_eras.Append(era.get_name(), era)
        self.lb_eras.Select(self.lb_eras.GetCount() - 1)
        self._EnableDisableButtons()

    def RemoveEra(self, era):
        def select_era(inx):
            if self.lb_eras.GetCount() == inx:
                inx -= 1
            if inx >= 0:
                self.lb_eras.SetSelection(inx)
        inx = self.lb_eras.GetSelection()
        self.lb_eras.Delete(inx)
        select_era(inx)
        self._EnableDisableButtons()

    def _EnableDisableButtons(self):
        if self.lb_eras.GetCount() == 0:
            self.btn_remove.Enable(False)
            self.btn_edit.Enable(False)
        else:
            self.btn_remove.Enable(True)
            self.btn_edit.Enable(True)
