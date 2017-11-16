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

from timelinelib.canvas.data.exceptions import TimelineIOError
from timelinelib.repositories.dbwrapper import DbWrapperCategoryRepository
from timelinelib.wxgui.dialogs.editcategory.view import EditCategoryDialog
import timelinelib.wxgui.utils as gui_utils


class CategoryChoice(wx.Choice):

    def __init__(self, parent, timeline, allow_add=False, allow_edit=False, **kwargs):
        wx.Choice.__init__(self, parent, wx.ID_ANY, **kwargs)
        self.timeline = timeline
        self.category_repository = DbWrapperCategoryRepository(self.timeline)
        self.allow_add = allow_add
        self.allow_edit = allow_edit
        self.Bind(wx.EVT_CHOICE, self._on_choice)
        self._clear()

    def Populate(self, exclude=None, select=None):
        self.exclude = exclude
        self._clear()
        self._populate_tree(self.category_repository.get_tree(remove=exclude))
        self.SetSelectedCategory(select)

    def GetSelectedCategory(self):
        if self.GetSelection() == wx.NOT_FOUND:
            return None
        return self.GetClientData(self.GetSelection())

    def SetSelectedCategory(self, category):
        self.SetSelection(self._get_index(category))
        self.current_category_selection = self.GetSelection()

    def _clear(self):
        self.Clear()
        self.add_category_item_index = None
        self.edit_categoris_item_index = None
        self.last_real_category_index = None
        self.current_category_selection = self.GetSelection()

    def _get_index(self, category):
        for index in range(self.GetCount()):
            if self.GetClientData(index) == category:
                return index
        return 0

    def _populate_tree(self, tree):
        self.Append("", None)
        self._append_tree(tree)
        self.last_real_category_index = self.GetCount() - 1
        if self.allow_add or self.allow_edit:
            self.Append("", None)
        if self.allow_add:
            self.add_category_item_index = self.GetCount()
            self.Append(_("Add new"), None)
        if self.allow_edit:
            self.edit_categoris_item_index = self.GetCount()
            self.Append(_("Edit categories"), None)

    def _append_tree(self, tree, indent=""):
        for (category, subtree) in tree:
            self.Append(indent + category.name, category)
            self._append_tree(subtree, indent + "    ")

    def _on_choice(self, event):
        new_selection_index = event.GetSelection()
        if new_selection_index > self.last_real_category_index:
            self.SetSelection(self.current_category_selection)
            if new_selection_index == self.add_category_item_index:
                self._add_category()
            elif new_selection_index == self.edit_categoris_item_index:
                self._edit_categories()
        else:
            self.current_category_selection = new_selection_index

    def _add_category(self):
        dialog = EditCategoryDialog(self,
                                    _("Add Category"),
                                    self.timeline,
                                    None)
        if dialog.ShowModal() == wx.ID_OK:
            self.Populate(select=dialog.GetEditedCategory(),
                          exclude=self.exclude)
        dialog.Destroy()

    def _edit_categories(self):
        gui_utils.display_categories_editor_moved_message(self)
