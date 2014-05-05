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

from timelinelib.editors.shortcuts import ShortcutsEditor 


class ShortcutsGuiCreator(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=_("Edit Shortcuts"))
        self._create_gui()
        self._bind_events()

    def _create_gui(self):
        main_box = self._create_main_box()
        self.SetSizerAndFit(main_box)

    def _create_main_box(self):
        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(self._create_combobox_grid(), 1, wx.ALL|wx.EXPAND, 5)
        main_box.Add(self._create_buttons_box(), 0, wx.BOTTOM|wx.EXPAND, 5)
        return main_box
        
    def _create_combobox_grid(self):
        self.cb_functions = self._creat_readonly_combobox(width=280)
        self.cb_modifiers = self._creat_readonly_combobox()
        self.cb_shortcut_keys = self._creat_readonly_combobox()
        grid = wx.FlexGridSizer(rows=0, cols=2, vgap=5, hgap=5)
        grid.Add(wx.StaticText(self, -1, _("Functions:")))
        grid.Add(self.cb_functions)
        grid.Add(wx.StaticText(self, -1, _("Modifier:")))
        grid.Add(self.cb_modifiers)
        grid.Add(wx.StaticText(self, -1, _("Shortcut Key:")))
        grid.Add(self.cb_shortcut_keys)
        return grid
        
    def _creat_readonly_combobox(self, width=-1):
        return wx.ComboBox(self, -1, size=(width, -1), style=wx.CB_READONLY)
        
    def _create_buttons_box(self):
        self.btn_apply = wx.Button(self, wx.ID_APPLY)
        self.btn_close = wx.Button(self, wx.ID_CLOSE)
        self.btn_apply.SetDefault()
        self.SetAffirmativeId(wx.ID_CLOSE)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddStretchSpacer()
        box.Add(self.btn_apply, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT, 5)
        box.Add(self.btn_close, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT, 5)
        return box
                
    def _bind_events(self):
        self.Bind(wx.EVT_COMBOBOX, self._on_select, self.cb_functions)
        self.Bind(wx.EVT_BUTTON, self._btn_apply_on_click, self.btn_apply)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, self.btn_close)
        
        
class ShortcutsEditorDialog(ShortcutsGuiCreator):

    def __init__(self, parent, shortcut_config):
        ShortcutsGuiCreator.__init__(self, parent)
        self.controller = ShortcutsEditor(self, shortcut_config) 

    #
    # Controller API
    #
    def set_functions(self, choices):
        self.cb_functions.AppendItems(choices)
        self.cb_functions.SetValue(choices[0])
        
    def set_shortcut_keys(self, choices, value):
        self.cb_shortcut_keys.AppendItems(choices)
        self.set_shortcut_key(value)
        
    def set_shortcut_key(self, value):
        self.cb_shortcut_keys.SetValue(value)

    def set_modifiers(self, choices, value):
        self.cb_modifiers.AppendItems(choices)
        self.set_modifier(value)
        
    def set_modifier(self, value):
        self.cb_modifiers.SetValue(value)
        
    def get_function(self):
        return self.cb_functions.GetValue()

    def get_shortcut_key(self):
        return self.cb_shortcut_keys.GetValue()

    def get_modifier(self):
        return self.cb_modifiers.GetValue()

    #
    # Event Handlers
    #
    def _on_select(self, evt):
        self.controller.on_function_selected()
        
    def _btn_close_on_click(self, evt):
        self.EndModal(wx.ID_OK)
        
    def _btn_apply_on_click(self, e):
        self.controller.apply()
        