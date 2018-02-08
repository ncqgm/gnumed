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


from timelinelib.wxgui.dialogs.shortcutseditor.controller import ShortcutsEditorDialogController
from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.utils import display_warning_message
from timelinelib.wxgui.utils import PopupTextWindow


class ShortcutsEditorDialog(Dialog):

    """
    <BoxSizerVertical>
        <FlexGridSizer name="grid" rows="0" columns="2" border="ALL" >
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(functions)" />
            <ComboBox name="cb_functions" style="CB_READONLY" width="280" align="ALIGN_CENTER_VERTICAL"
                event_EVT_COMBOBOX="on_selection_changed" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(modifiers)" />
            <ComboBox name="cb_modifiers" style="CB_READONLY"  align="ALIGN_CENTER_VERTICAL" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(shortcutkey)" />
            <ComboBox name="cb_shortcut_keys" style="CB_READONLY"  align="ALIGN_CENTER_VERTICAL" />
        </FlexGridSizer>
        <DialogButtonsApplyCloseSizer
            border="LEFT|BOTTOM|RIGHT"
            event_EVT_BUTTON__ID_APPLY="on_apply_clicked"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, shortcut_config):
        Dialog.__init__(self, ShortcutsEditorDialogController, parent, {
            "functions": _("Functions:"),
            "modifiers": _("Modifier:"),
            "shortcutkey": _("Shortcut Key:"),
        }, title=_("Edit Shortcuts"))
        self.controller.on_init(shortcut_config)

    def SetFunctions(self, choices):
        self.cb_functions.AppendItems(choices)
        self.cb_functions.SetValue(choices[0])

    def SetModifiers(self, choices, value):
        self.cb_modifiers.AppendItems(choices)
        self.SetModifier(value)

    def SetModifier(self, value):
        self.cb_modifiers.SetValue(value)

    def SetShortcutKeys(self, choices, value):
        self.cb_shortcut_keys.AppendItems(choices)
        self.SetShortcutKey(value)

    def SetShortcutKey(self, value):
        self.cb_shortcut_keys.SetValue(value)

    def GetFunction(self):
        return self.cb_functions.GetValue()

    def GetShortcutKey(self):
        return self.cb_shortcut_keys.GetValue()

    def GetModifier(self):
        return self.cb_modifiers.GetValue()

    def DisplayAckPopupWindow(self, text):
        def calculate_ack_popup_window_position():
            return [a + b for a, b in zip(self.GetPosition(), self.btn_apply.GetPosition())]
        PopupTextWindow(self, text, pos=calculate_ack_popup_window_position())

    def DisplayWarningMessage(self, text):
        display_warning_message(text)
