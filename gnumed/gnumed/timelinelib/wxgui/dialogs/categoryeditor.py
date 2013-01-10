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
import wx.lib.colourselect as colourselect

import timelinelib.wxgui.utils as gui_utils
from timelinelib.wxgui.utils import _display_error_message
from timelinelib.wxgui.utils import _set_focus_and_select
from timelinelib.wxgui.utils import BORDER
from timelinelib.editors.category import CategoryEditor
from timelinelib.repositories.dbwrapper import DbWrapperCategoryRepository


class WxCategoryEdtiorDialog(wx.Dialog):

    def __init__(self, parent, title, timeline, category):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self.controller = CategoryEditor(self)
        self.controller.edit(category, DbWrapperCategoryRepository(timeline))

    def set_category_tree(self, tree):
        def add_tree(tree, indent=""):
            for (root, subtree) in tree:
                self.parentlistbox.Append(indent + root.name, root)
                add_tree(subtree, indent + "    ")
        self.parentlistbox.Clear()
        self.parentlistbox.Append("", None) # No parent
        add_tree(tree)
        self.SetSizerAndFit(self.vbox)

    def get_name(self):
        return self.txt_name.GetValue().strip()

    def set_name(self, new_name):
        self.txt_name.SetValue(new_name)

    def get_color(self):
        # Convert wx.Color to (r, g, b) tuple
        (r, g, b) = self.colorpicker.GetValue()
        return (r, g, b)

    def get_font_color(self):
        # Convert wx.Color to (r, g, b) tuple
        (r, g, b) = self.fontcolorpicker.GetValue()
        return (r, g, b)

    def set_color(self, new_color):
        self.colorpicker.SetValue(new_color)

    def set_font_color(self, new_color):
        self.fontcolorpicker.SetValue(new_color)

    def get_parent(self):
        selection = self.parentlistbox.GetSelection()
        if selection == wx.NOT_FOUND:
            return None
        return self.parentlistbox.GetClientData(selection)

    def set_parent(self, parent):
        no_items = self.parentlistbox.GetCount()
        for i in range(0, no_items):
            if self.parentlistbox.GetClientData(i) is parent:
                self.parentlistbox.SetSelection(i)
                return

    def close(self):
        self.EndModal(wx.ID_OK)

    def handle_invalid_name(self, name):
        msg = _("Category name '%s' not valid. Must be non-empty.")
        _display_error_message(msg % name, self)
        _set_focus_and_select(self.txt_name)

    def handle_used_name(self, name):
        msg = _("Category name '%s' already in use.")
        _display_error_message(msg % name, self)
        _set_focus_and_select(self.txt_name)

    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def get_edited_category(self):
        return self.controller.category

    def _create_gui(self):
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        field_grid = self._create_field_grid()
        button_box = self._create_button_box()
        self.vbox.Add(field_grid, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        _set_focus_and_select(self.txt_name)

    def _create_field_grid(self):
        self.txt_name = wx.TextCtrl(self, size=(150, -1))
        self.colorpicker = colourselect.ColourSelect(self)
        self.fontcolorpicker = colourselect.ColourSelect(self)
        self.parentlistbox = wx.Choice(self, wx.ID_ANY)
        grid = wx.FlexGridSizer(3, 2, BORDER, BORDER)
        self._add_ctrl_to_grid(_("Name:"), self.txt_name, grid)
        self._add_ctrl_to_grid(_("Color:"), self.colorpicker, grid)
        self._add_ctrl_to_grid(_("Font Color:"), self.fontcolorpicker, grid)
        self._add_ctrl_to_grid(_("Parent:"), self.parentlistbox, grid)
        return grid

    def _add_ctrl_to_grid(self, name, ctrl, grid):
        grid.Add(wx.StaticText(self, label=name), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(ctrl)

    def _create_button_box(self):
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        return button_box

    def _btn_ok_on_click(self, e):
        self.controller.save()
