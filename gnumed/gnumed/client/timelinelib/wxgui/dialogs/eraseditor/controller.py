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

from timelinelib.canvas.data.era import Era
from timelinelib.wxgui.dialogs.eraeditor.view import EraEditorDialog
from timelinelib.wxgui.framework import Controller


class ErasEditorDialogController(Controller):

    def on_init(self, db, config):
        self.db = db
        self.config = config
        self.eras = db.get_all_eras()
        self.view.SetEras(self.eras)
        self.editor_dialog = None

    def on_edit(self, evt):
        self._edit(self.view.GetSelectedEra())

    def on_dclick(self, evt):
        self._edit(self.view.GetSelectedEra())

    def on_add(self, evt):
        self._operate_with_modal_dialog(
            _("Add an Era"),
            self._create_era(),
            self._after_add
        )

    def on_remove(self, evt):
        era = self.view.GetSelectedEra()
        if era in self.eras:
            self.eras.remove(era)
            self.view.RemoveEra(era)
        self.db.delete_era(era)

    def _after_add(self, era):
        self.eras.append(era)
        self.view.AppendEra(era)
        self.db.save_era(era)

    def _edit(self, era):
        self._operate_with_modal_dialog(
            _("Edit an Era"),
            era,
            self._after_edit
        )

    def _after_edit(self, era):
        self.view.UpdateEra(era)
        self.db.save_era(era)

    def _create_era(self):
        start = self.db.time_type.now()
        end = start
        return Era().update(start, end, "New Era")

    def _operate_with_modal_dialog(self, label, era, operation):
        if self.editor_dialog is None:
            self.set_editor_dialog(EraEditorDialog(self.view, label, self.db.time_type, self.config, era))
        dlg = self.editor_dialog
        if dlg.ShowModal() == wx.ID_OK:
            operation(era)
        dlg.Destroy()
        self.editor_dialog = None

    def set_editor_dialog(self, dialog):
        """
        This function is used for test purposes only
        """
        self.editor_dialog = dialog
