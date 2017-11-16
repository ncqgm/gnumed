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


from timelinelib.wxgui.dialogs.fieldselection.controller import FIELDS
from timelinelib.wxgui.framework import Controller


CSV_FILE = _("CSV File")
TARGET_TYPES = (CSV_FILE,)
TEXT_ENCODINGS = ("utf-8", "cp1252", "cp850")


class ExportDialogController(Controller):

    def on_init(self):
        self.event_fields = FIELDS["Event"]
        self.category_fields = FIELDS["Category"]
        self.view.SetTargetTypes(TARGET_TYPES)
        self.view.SetTextEncodings(TEXT_ENCODINGS)
        self.view.SetEvents(True)
        self.view.SetCategories(False)

    def on_ok(self, evt):
        try:
            if self._validate_input():
                self.view.Close()
        except ValueError:
            pass

    def on_edit_event_fields(self, evt):
        self.view.EditEventFields()

    def on_edit_categories_fields(self, evt):
        self.view.EditCategoryFields()

    def get_event_fields(self):
        return self.event_fields

    def set_event_fields(self, fields):
        self.event_fields = fields

    def get_category_fields(self):
        return self.category_fields

    def set_category_fields(self, fields):
        self.category_fields = fields

    def _validate_input(self):
        if not self.view.GetExportEvents() and not self.view.GetExportCategories():
            self.view.DisplayInformationMessage(_("Invalid Data"), _("At least one Export Item must be selected"))
            return False
        if self.view.GetExportEvents() and self.event_fields == []:
            self.view.DisplayInformationMessage(_("Invalid Data"), _("At least one Event Field must be selected"))
            return False
        if self.view.GetExportCategories() and self.category_fields == []:
            self.view.DisplayInformationMessage(_("Invalid Data"), _("At least one Category Field must be selected"))
            return False
        return True
