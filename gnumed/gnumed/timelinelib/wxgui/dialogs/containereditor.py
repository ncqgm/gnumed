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

from timelinelib.editors.container import ContainerEditor
from timelinelib.wxgui.components.categorychoice import CategoryChoice
from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import _display_error_message
from timelinelib.wxgui.utils import _set_focus_and_select
import timelinelib.wxgui.utils as gui_utils


class StaticContainerEditorDialog(wx.Dialog):

    def __init__(self, parent, title, db):
        wx.Dialog.__init__(self, parent, title=title, name="container_editor",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.db = db
        self._create_gui()

    def _create_gui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._create_propeties_groupbox(sizer)
        self._create_buttons(sizer)
        self.SetSizerAndFit(sizer)
        self.txt_name.SetFocus()

    def _create_propeties_groupbox(self, sizer):
        groupbox = wx.StaticBox(self, wx.ID_ANY, _("Container Properties"))
        box = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        self._create_properties_groupbox_content(box)
        sizer.Add(box, flag=wx.EXPAND|wx.ALL, border=BORDER, proportion=1)

    def _create_properties_groupbox_content(self, sizer):
        grid = wx.FlexGridSizer(4, 2, BORDER, BORDER)
        grid.AddGrowableCol(1)
        self._create_name_textctrl(grid)
        self._create_categories_listbox(grid)
        sizer.Add(grid, flag=wx.ALL|wx.EXPAND, border=BORDER)

    def _create_name_textctrl(self, grid):
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, name="name")
        label = wx.StaticText(self, label=_("Name:"))
        grid.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.txt_name, flag=wx.EXPAND)

    def _create_categories_listbox(self, grid):
        self.lst_category = CategoryChoice(self, self.db)
        label = wx.StaticText(self, label=_("Category:"))
        grid.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)

    def _create_buttons(self, properties_box):
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        properties_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)


class ContainerEditorControllerApi(object):

    def __init__(self, db, container):
        self._bind_events()
        self.controller = ContainerEditor(self, db, container)

    def set_name(self, name):
        self.txt_name.SetValue(name)

    def get_name(self):
        return self.txt_name.GetValue().strip()

    def set_category(self, category):
        self.lst_category.select(category)

    def get_category(self):
        return self.lst_category.get()

    def display_invalid_name(self, message):
        _display_error_message(message, self)
        _set_focus_and_select(self.txt_name)

    def display_db_exception(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def close(self):
        self.EndModal(wx.ID_OK)

    def _bind_events(self):
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        self.Bind(wx.EVT_CHOICE, self.lst_category.on_choice, self.lst_category)

    def _btn_ok_on_click(self, evt):
        self.controller.save()


class ContainerEditorDialog(StaticContainerEditorDialog,
                            ContainerEditorControllerApi):
    """
    This dialog is used for two purposes, editing an existing container
    event and creating a new container event (container==None).
    The 'business logic' is handled by the controller.
    """
    def __init__(self, parent, title, db, container=None):
        StaticContainerEditorDialog.__init__(self, parent, title, db)
        ContainerEditorControllerApi.__init__(self, db, container)

    #
    # Parent API
    #
    def get_edited_container(self):
        return self.controller.get_container()
