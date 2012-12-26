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

import timelinelib.wxgui.utils as gui_utils
from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.components.cattree import CategoriesTree
from timelinelib.wxgui.components.cattree import add_category
from timelinelib.wxgui.components.cattree import edit_category
from timelinelib.wxgui.components.cattree import delete_category


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"))
        self.db = timeline
        self.cat_tree = self._create_gui()
        self._fill_controls_with_data()

    def _fill_controls_with_data(self):
        self.cat_tree.initialize_from_db(self.db)

    def _create_gui(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        cat_tree = self._create_cat_tree(vbox)
        self._create_buttons(vbox)
        self.SetSizerAndFit(vbox)
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        return cat_tree

    def _window_on_close(self, e):
        self.cat_tree.destroy()
        self.EndModal(wx.ID_CLOSE)

    def _create_cat_tree(self, vbox):
        cat_tree = CategoriesTree(self, self.db_error_handler)
        cat_tree.SetMinSize((-1, 200))
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self._cat_tree_on_sel_changed,
                  cat_tree)
        vbox.Add(cat_tree, flag=wx.ALL|wx.EXPAND, border=BORDER)
        return cat_tree

    def _cat_tree_on_sel_changed(self, e):
        self._updateButtons()

    def _create_buttons(self, vbox):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_edit = self._create_edit_button(button_box)
        self._create_add_button(button_box)
        self.btn_del = self._create_delete_button(button_box)
        self._create_close_button(button_box)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)

    def _create_edit_button(self, button_box):
        btn = wx.Button(self, wx.ID_EDIT)
        btn.Disable()
        self.Bind(wx.EVT_BUTTON, self._btn_edit_on_click, btn)
        button_box.Add(btn, flag=wx.RIGHT, border=BORDER)
        return btn

    def _btn_edit_on_click(self, e):
        selected_category = self.cat_tree.get_selected_category()
        if selected_category is not None:
            edit_category(self, self.db, selected_category,
                          self.db_error_handler)
            self._updateButtons()

    def _create_add_button(self, button_box):
        btn = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn)
        button_box.Add(btn, flag=wx.RIGHT, border=BORDER)
        return btn

    def _btn_add_on_click(self, e):
        add_category(self, self.db, self.db_error_handler)
        self._updateButtons()

    def _create_delete_button(self, button_box):
        btn = wx.Button(self, wx.ID_DELETE)
        btn.Disable()
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, btn)
        button_box.Add(btn, flag=wx.RIGHT, border=BORDER)
        return btn

    def _btn_del_on_click(self, e):
        selected_category = self.cat_tree.get_selected_category()
        if selected_category is not None:
            delete_category(self, self.db, selected_category,
                            self.db_error_handler)
            self._updateButtons()

    def _create_close_button(self, button_box):
        btn = wx.Button(self, wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn)
        button_box.Add(btn, flag=wx.LEFT, border=BORDER)
        return btn

    def _btn_close_on_click(self, e):
        self.Close()

    def db_error_handler(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def _updateButtons(self):
        selected_category = self.cat_tree.get_selected_category() is not None
        self.btn_edit.Enable(selected_category)
        self.btn_del.Enable(selected_category)

