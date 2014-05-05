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

from timelinelib.wxgui.utils import BORDER
from timelinelib.proxies.sidebar import SidebarProxy


class FindDialogGuiCreator(wx.Dialog):

    def __init__(self, mainframe, timeline):
        wx.Dialog.__init__(self, mainframe, title=_("Category Finder"), name="container_editor",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.mainframe = mainframe
        self.db = timeline
        self._create_gui()
        self.txt_name.SetFocus()

    def _create_gui(self):
        sizer = self._create_sizer()
        controls = self._create_controls()
        self._layout_controls(sizer, controls)
        self.SetSizerAndFit(sizer)

    def _create_sizer(self):
        sizer = wx.FlexGridSizer(2, 1, BORDER, BORDER)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        return sizer
        
    def _create_controls(self):
        return (self._create_content(), self._create_buttons())
    
    def _layout_controls(self, sizer, controls):
        content, buttons = controls
        sizer.Add(content, flag=wx.ALL|wx.EXPAND, border=BORDER)
        sizer.Add(buttons, flag=wx.ALL, border=BORDER)
        
    def _create_content(self):
        sizer = self._create_content_sizer()
        controls = self._create_content_controls()
        self._layout_content_controls(sizer, controls)
        return sizer

    def _create_content_controls(self):
        return (self._create_name_textctrl(),
                self._create_categories_listbox())
        
    def _create_content_sizer(self):
        sizer = wx.FlexGridSizer(2, 1, BORDER, BORDER)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(1)
        return sizer
 
    def _layout_content_controls(self, sizer, controls):
        for control in controls:
            sizer.Add(control, flag=wx.EXPAND)
           
    def _create_name_textctrl(self):
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, name="name")
        self.Bind(wx.EVT_TEXT, self._on_char, self.txt_name)
        return self.txt_name
    
    def _create_categories_listbox(self):
        self.lst_category = wx.ListBox(self, -1)
        self._fill_categories_listbox()
        return self.lst_category
    
    def _create_buttons(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_check = wx.Button(self, wx.ID_ANY, _("Check"))
        btn_uncheck = wx.Button(self, wx.ID_ANY, _("Uncheck"))
        btn_close = wx.Button(self, wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_check_on_click, btn_check)
        self.Bind(wx.EVT_BUTTON, self._btn_uncheck_on_click, btn_uncheck)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        sizer.Add(btn_check)
        sizer.Add(btn_uncheck)
        sizer.Add(btn_close)
        return sizer

    
class CategoryFindDialog(FindDialogGuiCreator):

    def __init__(self, parent, timeline):
        FindDialogGuiCreator.__init__(self, parent, timeline)

    def _on_char(self, evt):
        self._fill_categories_listbox()

    def _fill_categories_listbox(self):
        text = self.txt_name.GetValue()
        categories = sorted([category.name for category in self.db.get_categories()
                             if category.name.upper().startswith(text.upper())])
        self.lst_category.SetItems(categories)

    def _btn_check_on_click(self, evt):
        SidebarProxy(self.mainframe).check_categories(self._get_categories())

    def _btn_uncheck_on_click(self, evt):
        SidebarProxy(self.mainframe).uncheck_categories(self._get_categories())
        
    def _btn_close_on_click(self, evt):
        self.EndModal(wx.OK)
            
    def _get_categories(self):
        names = self.lst_category.GetItems()
        return sorted([category for category in self.db.get_categories()
                       if category.name in names])
