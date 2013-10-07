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

from timelinelib.editors.duplicateevent import DuplicateEventEditor
from timelinelib.wxgui.utils import BORDER
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import _set_focus_and_select
import timelinelib.wxgui.utils as gui_utils
from timelinelib.db.utils import safe_locking


class DuplicateEventDialog(wx.Dialog):

    def __init__(self, parent, db, event):
        wx.Dialog.__init__(self, parent, title=_("Duplicate Event"))
        self._create_gui(db.get_time_type().get_duplicate_functions())
        self.controller = DuplicateEventEditor(self, db, event)
        self.controller.initialize()

    def set_count(self, count):
        self.sc_count.SetValue(count)

    def get_count(self):
        return self.sc_count.GetValue()

    def set_frequency(self, count):
        self.sc_frequency.SetValue(count)

    def get_frequency(self):
        return self.sc_frequency.GetValue()

    def select_move_period_fn_at_index(self, index):
        self.rb_period.SetSelection(index)

    def get_move_period_fn(self):
        return self._move_period_fns[self.rb_period.GetSelection()]

    def set_direction(self, direction):
        self.rb_direction.SetSelection(direction)

    def get_direction(self):
        return self.rb_direction.GetSelection()

    def close(self):
        self.EndModal(wx.ID_OK)

    def handle_db_error(self, e):
        gui_utils.handle_db_error_in_dialog(self, e)

    def handle_date_errors(self, error_count):
       display_error_message(
            _("%d Events not duplicated due to missing dates.")
            % error_count)

    def _create_gui(self, move_period_config):
        self._move_period_fns = [fn for (label, fn) in move_period_config]
        period_list = [label for (label, fn) in move_period_config]
        vbox = wx.BoxSizer(wx.VERTICAL)
        self._create_and_add_sc_count_box(vbox)
        self._create_and_add_rb_period(vbox, period_list)
        self._create_and_add_sc_frequency_box(vbox)
        self._create_and_add_rb_direction(vbox)
        self._create_and_add_button_box(vbox)
        self.SetSizerAndFit(vbox)
        _set_focus_and_select(self.sc_count)

    def _create_and_add_sc_count_box(self, form):
        sc_count_box = self._create_count_spin_control()
        form.Add(sc_count_box, border=BORDER)

    def _create_count_spin_control(self):
        st_count = wx.StaticText(self, label=_("Number of duplicates:"))
        self.sc_count = wx.SpinCtrl(self, wx.ID_ANY, size=(50,-1))
        self.sc_count.SetRange(1,999)
        self.sc_count.SetValue(1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st_count, flag=wx.ALL, border=BORDER)
        hbox.Add(self.sc_count, flag=wx.ALL, border=BORDER)
        return hbox

    def _create_and_add_rb_period(self, form, period_list):
        self.rb_period = wx.RadioBox(self, wx.ID_ANY, _("Period"),
                                     wx.DefaultPosition, wx.DefaultSize,
                                     period_list)
        form.Add(self.rb_period, flag=wx.ALL|wx.EXPAND, border=BORDER)

    def _create_and_add_sc_frequency_box(self, form):
        sc_frequency_box = self._creat_frequency_spin_control()
        form.Add(sc_frequency_box, border=BORDER)

    def _creat_frequency_spin_control(self):
        st_frequency = wx.StaticText(self, label=_("Frequency:"))
        self.sc_frequency = wx.SpinCtrl(self, wx.ID_ANY, size=(50,-1))
        self.sc_frequency.SetRange(1,999)
        self.sc_frequency.SetValue(1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(st_frequency, flag=wx.ALL, border=BORDER)
        hbox.Add(self.sc_frequency, flag=wx.ALL, border=BORDER)
        return hbox

    def _create_and_add_rb_direction(self, form):
        direction_list = [_("Forward"), _("Backward"), _("Both")]
        self.rb_direction = wx.RadioBox(self, wx.ID_ANY, _("Direction"),
                                        choices=direction_list)
        form.Add(self.rb_direction, flag=wx.ALL|wx.EXPAND, border=BORDER)

    def _create_and_add_button_box(self, form):
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        form.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)

    def _btn_ok_on_click(self, e):
        gui_utils.set_wait_cursor(self)
        self.controller.create_duplicates_and_save()
        gui_utils.set_default_cursor(self)


def open_duplicate_event_dialog_for_event(parent, db, handle_db_error, event):
    def create_dialog():
        return DuplicateEventDialog(parent, db, event)
    def edit_function():
        gui_utils.show_modal(create_dialog, handle_db_error)
    safe_locking(parent, edit_function)
