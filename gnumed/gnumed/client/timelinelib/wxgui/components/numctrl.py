# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017  Rickard Lindberg, Roger Lindberg
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


class NumCtrl(wx.Panel):

    def __init__(self, parent, size=(-1, -1)):
        wx.Panel.__init__(self, parent)
        self._CreateGui(size)

    def _CreateGui(self, size):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, size=size)
        self.spin = wx.SpinButton(self, style=wx.SP_VERTICAL, size=(-1, self.text.GetSize()[1] + 5))
        sizer.Add(self.text, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.spin, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.Bind(wx.EVT_CHAR, self._OnKeyPress, self.text)
        self.Bind(wx.EVT_SPIN_UP, self._OnSpinUp, self.spin)
        self.Bind(wx.EVT_SPIN_DOWN, self._OnSpinDown, self.spin)
        self.SetSizerAndFit(sizer)

    def SetValue(self, value):
        self.text.SetValue(value)

    def GetValue(self):
        return self.text.GetValue()

    def _OnKeyPress(self, event):
        if self.ValidKeyCode(event.GetKeyCode()):
            event.Skip()

    def _OnSpinUp(self, event):
        self._Spin(1)

    def _OnSpinDown(self, event):
        self._Spin(-1)

    def _Spin(self, value):
        self.SetValue(str(int(self.GetValue()) + value))

    def ValidKeyCode(self, keycode):
        """Allow digits, and a minus sign in the first position."""
        if IsAscci(keycode):
            if IsMinus(keycode):
                if self.MinusIsOk():
                    return True
                else:
                    return False
            elif IsNotAlpha(keycode):
                return True
            else:
                return False
        return True

    def MinusIsOk(self):
        return '-' not in self.GetValue() and self.GetInsertionPoint() == 0


def IsNotAlpha(keycode):
    return not chr(keycode).isalpha()


def IsMinus(keycode):
    return chr(keycode) == '-'


def IsAscci(keycode):
    return keycode < 255
