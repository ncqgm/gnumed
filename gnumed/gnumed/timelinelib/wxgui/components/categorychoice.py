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


import wx

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects.category import sort_categories
from timelinelib.wxgui.dialogs.categorieseditor import CategoriesEditor
from timelinelib.wxgui.dialogs.categoryeditor import WxCategoryEdtiorDialog
import timelinelib.wxgui.utils as gui_utils


class CategoryChoice(wx.Choice):

    def __init__(self, parent, timeline):
        wx.Choice.__init__(self, parent, wx.ID_ANY)
        self.timeline = timeline

    def select(self, select_category):
        # We can not do error handling here since this method is also called
        # from the constructor (and then error handling is done by the code
        # calling the constructor).
        self.Clear()
        self.Append("", None) # The None-category
        selection_set = False
        current_item_index = 1
        for cat in sort_categories(self.timeline.get_categories()):
            self.Append(cat.name, cat)
            if cat == select_category:
                self.SetSelection(current_item_index)
                selection_set = True
            current_item_index += 1
        self.last_real_category_index = current_item_index - 1
        self.add_category_item_index = self.last_real_category_index + 2
        self.edit_categoris_item_index = self.last_real_category_index + 3
        self.Append("", None)
        self.Append(_("Add new"), None)
        self.Append(_("Edit categories"), None)
        if not selection_set:
            self.SetSelection(0)
        self.current_category_selection = self.GetSelection()

    def get(self):
        selection = self.GetSelection()
        category = self.GetClientData(selection)
        return category

    def on_choice(self, e):
        new_selection_index = e.GetSelection()
        if new_selection_index > self.last_real_category_index:
            self.SetSelection(self.current_category_selection)
            if new_selection_index == self.add_category_item_index:
                self._add_category()
            elif new_selection_index == self.edit_categoris_item_index:
                self._edit_categories()
        else:
            self.current_category_selection = new_selection_index

    def _add_category(self):
        def create_category_editor():
            return WxCategoryEdtiorDialog(self, _("Add Category"),
                                          self.timeline, None)
        def handle_success(dialog):
            if dialog.GetReturnCode() == wx.ID_OK:
                try:
                    self.select(dialog.get_edited_category())
                except TimelineIOError, e:
                    gui_utils.handle_db_error_in_dialog(self, e)
        gui_utils.show_modal(create_category_editor,
                             gui_utils.create_dialog_db_error_handler(self),
                             handle_success)

    def _edit_categories(self):
        def create_categories_editor():
            return CategoriesEditor(self, self.timeline)
        def handle_success(dialog):
            try:
                prev_index = self.GetSelection()
                prev_category = self.GetClientData(prev_index)
                self.select(prev_category)
            except TimelineIOError, e:
                gui_utils.handle_db_error_in_dialog(self, e)
        gui_utils.show_modal(create_categories_editor,
                             gui_utils.create_dialog_db_error_handler(self),
                             handle_success)
