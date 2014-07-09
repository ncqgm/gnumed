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
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"), name="categories_editor", 
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.db = timeline
        self._create_gui()
        self._bind()

    def ok_to_edit(self):
        """
        This method is called from the categories tree control when
        right-clicked to verify that editing is ok. But in this case
        editing has already been approved by opening the CategoriesEditor
        so we just return True
        """
        return True
    
    def edit_ends(self):
        """
        This method is called from the categories tree control when
        editing ends to reset edit-ok state. But that will be done anyway
        when we close the CategoriesEditor, so we do nothing.
        """
    
    def _create_gui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._create_cat_tree(), flag=wx.ALL|wx.EXPAND, border=BORDER, proportion=1)
        sizer.Add(self._create_buttons(), flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(sizer)
        self.cat_tree.initialize_from_db(self.db)

    def _bind(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        self.Bind(wx.EVT_SIZE, self._on_size, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self._cat_tree_on_sel_changed, self.cat_tree)
        self.Bind(wx.EVT_BUTTON, self._btn_edit_on_click, id=wx.ID_EDIT)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, id=wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, id=wx.ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, id=wx.ID_CLOSE)

    def _create_cat_tree(self):
        self.cat_tree = CategoriesTree(self, self.db_error_handler)
        self.cat_tree.SetMinSize((-1, 200))
        return self.cat_tree

    def _create_buttons(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._create_edit_button(), flag=wx.RIGHT, border=BORDER)
        sizer.Add(self._create_add_button(), flag=wx.RIGHT, border=BORDER)
        sizer.Add(self._create_delete_button(), flag=wx.RIGHT, border=BORDER)
        sizer.Add(self._create_close_button(), flag=wx.LEFT, border=BORDER)
        self._enable_buttons(False)
        return sizer

    def _create_edit_button(self):
        self.btn_edit = wx.Button(self, wx.ID_EDIT)
        return self.btn_edit

    def _create_add_button(self):
        return wx.Button(self, wx.ID_ADD)

    def _create_delete_button(self):
        self.btn_del = wx.Button(self, wx.ID_DELETE)
        return self.btn_del

    def _create_close_button(self):
        return wx.Button(self, wx.ID_CLOSE)

    def _enable_buttons(self, enabled):
        self.btn_del.Enable(enabled)
        self.btn_edit.Enable(enabled)
        
    def _updateButtons(self):
        selected_category = self.cat_tree.get_selected_category() is not None
        self._enable_buttons(selected_category)

    def _btn_edit_on_click(self, e):
        selected_category = self.cat_tree.get_selected_category()
        if selected_category is not None:
            edit_category(self, self.db, selected_category,
                          self.db_error_handler)
            self._updateButtons()

    def _btn_add_on_click(self, e):
        add_category(self, self.db, self.db_error_handler)
        self._updateButtons()

    def _btn_del_on_click(self, e):
        selected_category = self.cat_tree.get_selected_category()
        if selected_category is not None:
            delete_category(self, self.db, selected_category, self.db_error_handler)
            self._updateButtons()

    def _cat_tree_on_sel_changed(self, e):
        self._updateButtons()

    def _on_size(self, evt):
        self.Layout()
        
    def _window_on_close(self, e):
        self.cat_tree.destroy()
        self.EndModal(wx.ID_CLOSE)

    def _btn_close_on_click(self, e):
        self.Close()

    def db_error_handler(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

