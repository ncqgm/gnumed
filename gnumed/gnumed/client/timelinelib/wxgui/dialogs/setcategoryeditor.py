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

from timelinelib.editors.setcategory import SetCategoryEditor
from timelinelib.wxgui.components.categorychoice import CategoryChoice
from timelinelib.wxgui.utils import BORDER


class CategoryEditorGuiCreator(object):
    
    def _create_gui(self):
        properties_box = wx.BoxSizer(wx.VERTICAL)
        self._add_input_controls(properties_box)
        self._add_buttons(properties_box)
        self._make_sure_title_is_visible(properties_box)
        self.SetSizerAndFit(properties_box)
        self._bind_handlers()

    def _add_input_controls(self, sizer):
        category_selector = self._create_category_selector()
        sizer.Add(category_selector, flag=wx.EXPAND|wx.ALL, border=BORDER, proportion=1)

    def _add_buttons(self, properties_box):
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        properties_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)

    def _make_sure_title_is_visible(self, sizer):
        sizer.SetMinSize((270,-1))
        
    def _bind_handlers(self):
        self.Bind(wx.EVT_CHOICE, self.lst_category.on_choice, self.lst_category)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)

    def _create_category_selector(self):
        ROWS = 4
        COLS = 2
        VGAP = BORDER
        HGAP = BORDER
        GROWABLE_COL_INDEX = 1
        grid = wx.FlexGridSizer(ROWS, COLS, VGAP, HGAP)
        grid.AddGrowableCol(GROWABLE_COL_INDEX)
        self.lst_category = CategoryChoice(self, self.timeline)
        self.lst_category.select(None)
        label = wx.StaticText(self, label=_("Select a Category:"))
        grid.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)
        return grid
        
        
class ApiUsedByController(object):
    
    def get_category(self):
        return self.lst_category.get()
        
    def close(self):
        self.EndModal(wx.ID_OK)

    def cancel(self):
        self.EndModal(wx.ID_CANCEL)
            
    
class SetCategoryEditorDialog(wx.Dialog, CategoryEditorGuiCreator, ApiUsedByController):
    
    def __init__(self, parent, timeline, selected_event_ids=[]):
        title = self._get_title(selected_event_ids)
        wx.Dialog.__init__(self, parent, title=title, name="set_category_editor",
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.timeline = timeline
        self._create_gui()
        self.controller = SetCategoryEditor(self, timeline, selected_event_ids)

    def _btn_ok_on_click(self, evt):
        self.controller.save()

    def _get_title(self, selected_event_ids):
        if selected_event_ids == []:
            return _("Set Category on events without category")
        else:
            return _("Set Category on selected events")
    
