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


class ProgressEditorGuiCreator(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
      
    def create_sizer(self):
        return wx.GridBagSizer(vgap=10, hgap=10)
        
    def create_controls(self):
        label = wx.StaticText(self, label=_("Progress %:"))
        self.data = self._create_spin_control()
        return (label, self.data)
    
    def put_controls_in_sizer(self, sizer, controls):
        label, spin_ctrl = controls 
        span = wx.GBSpan(rowspan=1, colspan=1)
        sizer.Add(label, wx.GBPosition(row=1, col=0), span)
        sizer.Add(spin_ctrl, wx.GBPosition(row=1, col=1), span)
       
    def _create_spin_control(self):
        progress = wx.SpinCtrl(self, size=(50, -1))
        progress.SetRange(0, 100)
        return progress


class ProgressEditor(BaseEditor, ProgressEditorGuiCreator):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, parent, editor)
        ProgressEditorGuiCreator.__init__(self, parent)
        self.create_gui()

    def focus(self):
        super(ProgressEditor, self).focus()
        self._select_all()
        
    def _select_all(self):
        self.data.SetSelection(0, -1)

    def clear_data(self):
        self.data.SetValue(0)
