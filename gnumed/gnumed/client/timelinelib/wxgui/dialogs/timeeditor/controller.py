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


from timelinelib.wxgui.framework import Controller
from timelinelib.wxgui.utils import display_error_message
from timelinelib.utils import ex_msg


class TimeEditorDialogController(Controller):

    def on_init(self, time):
        self.view.SetTime(time)

    def ok_button_clicked(self, evt):
        try:
            if self.view.GetTime() is None:
                raise ValueError(_("Invalid date"))
        except ValueError as ex:
            display_error_message(ex_msg(ex))
        else:
            self.view.Close()
