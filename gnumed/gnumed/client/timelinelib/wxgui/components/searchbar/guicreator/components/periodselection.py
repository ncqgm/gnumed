# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
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


LABEL = _("In: ")
NAME = _("Select period")

class PeriodSelection:
    
    def __init__(self, parent, controller):
        self._controller = controller
        self._period_label = wx.StaticText(parent, wx.ID_ANY, LABEL) 
        parent.AddControl(self._period_label)
        self._period = wx.Choice(parent, wx.ID_ANY, size=(150, -1), choices=[], name=NAME)
        parent.AddControl(self._period)
        parent.Bind(wx.EVT_CHOICE, parent.OnChoice, self._period)

    def SetPeriodChoices(self, values):
        self._period.Clear()
        for value in values:
            self._period.Append(value)
        self._period.SetSelection(0)
                            
    def GetString(self):
        return self._period.GetString(self._period.GetSelection())        
