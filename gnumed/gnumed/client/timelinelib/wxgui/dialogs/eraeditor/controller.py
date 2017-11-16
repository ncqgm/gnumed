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


from timelinelib.wxgui.framework import Controller


class EraEditorDialogController(Controller):

    def on_init(self, era):
        self.era = era
        self._populate_view()

    def on_ok(self, evt):
        try:
            self._validate_input()
        except ValueError:
            pass
        else:
            self._update_era()
            self.view.EndModalOk()

    def _populate_view(self):
        self.view.SetPeriod(self.era.get_time_period())
        self.view.SetName(self.era.get_name())
        self.view.SetColor(self.era.get_color())
        self.view.SetEndsToday(self.era.ends_today())

    def _validate_input(self):
        self._validate_name()
        self._validate_period()

    def _validate_name(self):
        if self.view.GetName() == "":
            msg = _("Field '%s' can't be empty.") % _("Name")
            self.view.DisplayInvalidName(msg)
            raise ValueError()

    def _validate_period(self):
        try:
            self.view.GetPeriod()
        except ValueError as e:
            self.view.DisplayInvalidPeriod(str(e))
            raise ValueError()

    def _update_era(self):
        self.era.update(
            self.view.GetPeriod().get_start_time(),
            self.view.GetPeriod().get_end_time(),
            self.view.GetName(),
            self.view.GetColor()[:3]
        )
        self.era.set_ends_today(self.view.GetEndsToday())
