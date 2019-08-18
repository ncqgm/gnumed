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


import timelinelib.wxgui.components.searchbar.guicreator.components as components


class GuiCreator(object):

    def _create_gui(self):
        self._icon_size = (16, 16)
        self._create_components()
        self.Realize()
        self._result_label.Show(False)
        
    def Focus(self):
        self._search.SetFocus()

    def OnChoice(self, evt):
        self.Focus()
        
    def SetPeriodSelections(self, values):
        self._period.SetPeriodChoices(values)
            
    def _create_components(self):
        components.CloseButton(self)
        self._search = components.TextInput(self, self._controller)
        components.PrevButton(self, self._controller)
        components.NextButton(self, self._controller)
        components.ShowListButton(self, self._controller)
        self._period = components.PeriodSelection(self, self._controller)
        self._result_label = components.TextLabel(self, '')
