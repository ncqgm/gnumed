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

from timelinelib.editors.propertyeditors.baseeditor import BaseEditor


class DescriptionEditorGuiCreator(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
            
    def create_sizer(self):
        return wx.BoxSizer()
        
    def create_controls(self):
        text = self._create_text_control()
        return (text,)
    
    def put_controls_in_sizer(self, sizer, controls):
        text, = controls 
        sizer.Add(text, 1, wx.ALL|wx.EXPAND, 0)
        
    def _create_text_control(self):
        self.data = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_CHAR, self._on_char)
        return self.data
        
    def _on_char(self, evt):
        if self._ctrl_a(evt):
            self.SelectAll()
        else: 
            evt.Skip()
            
    def _ctrl_a(self, evt):
        KEY_CODE_A = 1
        return evt.ControlDown() and evt.KeyCode == KEY_CODE_A

                    
class DescriptionEditor(BaseEditor, DescriptionEditorGuiCreator):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, parent, editor)
        DescriptionEditorGuiCreator.__init__(self, parent)
        self.create_gui()

    def get_data(self):
        description = self.data.GetValue().strip()
        if description != "":
            return description
        return None

    def clear_data(self):
        self.data.SetValue("")
