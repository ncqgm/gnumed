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


import os.path

import wx

from timelinelib.editors.propertyeditors.baseeditor import BaseEditor


class IconEditorGuiCreator(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
                
    def create_sizer(self):
        return wx.GridBagSizer(5, 5)
        
    def create_controls(self):
        self.MAX_SIZE = (128, 128)
        self.img_icon = self._create_icon()
        description = self._create_description()
        btn_select = self._create_select_button()
        btn_clear = self._create_clear_button()
        return (description, btn_select, btn_clear, self.img_icon )
    
    def put_controls_in_sizer(self, sizer, controls):
        description, btn_select, btn_clear, img_icon = controls     
        sizer.Add(description, wx.GBPosition(0, 0), wx.GBSpan(1, 2))
        sizer.Add(btn_select, wx.GBPosition(1, 0), wx.GBSpan(1, 1))
        sizer.Add(btn_clear, wx.GBPosition(1, 1), wx.GBSpan(1, 1))
        sizer.Add(img_icon, wx.GBPosition(0, 2), wx.GBSpan(2, 1))

    def _create_select_button(self):
        btn = wx.Button(self, wx.ID_OPEN)
        self.Bind(wx.EVT_BUTTON, self._btn_select_on_click, btn)
        return btn
        
    def _create_clear_button(self):
        btn = wx.Button(self, wx.ID_CLEAR)
        self.Bind(wx.EVT_BUTTON, self._btn_clear_on_click, btn)
        return btn

    def _create_description(self):
        label = _("Images will be scaled to fit inside a %ix%i box.")
        return wx.StaticText(self, label=label % self.MAX_SIZE)

    def _create_icon(self):
        return wx.StaticBitmap(self, size=self.MAX_SIZE)


class IconEditor(BaseEditor, IconEditorGuiCreator):

    def __init__(self, parent, editor):
        BaseEditor.__init__(self, parent, editor)
        IconEditorGuiCreator.__init__(self, parent)
        self.create_gui()
        self._initialize_data()

    def get_data(self):
        return self.get_icon()

    def set_data(self, data):
        self.set_icon(data)

    def clear_data(self):
        self.set_icon(None)

    def set_icon(self, bmp):
        self.bmp = bmp
        if self.bmp == None:
            self.img_icon.SetBitmap(wx.EmptyBitmap(1, 1))
        else:
            self.img_icon.SetBitmap(bmp)
        self.GetSizer().Layout()

    def get_icon(self):
        return self.bmp

    def _initialize_data(self):
        self.bmp = None

    def _btn_select_on_click(self, evt):
        dialog = wx.FileDialog(self, message=_("Select Icon"),
                               wildcard="*", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if os.path.exists(path):
                image = wx.EmptyImage(0, 0)
                success = image.LoadFile(path)
                # LoadFile will show error popup if not successful
                if success:
                    # Resize image if too large
                    (w, h) = image.GetSize()
                    (W, H) = self.MAX_SIZE
                    if w > W:
                        factor = float(W) / float(w)
                        w = w * factor
                        h = h * factor
                    if h > H:
                        factor = float(H) / float(h)
                        w = w * factor
                        h = h * factor
                    image = image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
                    self.set_icon(image.ConvertToBitmap())
        dialog.Destroy()

    def _btn_clear_on_click(self, evt):
        self.set_icon(None)
