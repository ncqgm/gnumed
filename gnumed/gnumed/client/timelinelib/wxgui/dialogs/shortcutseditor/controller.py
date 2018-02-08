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


class MissingInput(Exception):
    pass


class DuplicateShortcut(Exception):
    pass


class ShortcutsEditorDialogController(Controller):

    def on_init(self, shortcut_config):
        self.shortcut_config = shortcut_config
        if shortcut_config:
            functions = self.shortcut_config.get_functions()
            modifier, key = self.shortcut_config.get_modifier_and_key(functions[0])
            self.view.SetFunctions(functions)
            self.view.SetModifiers(self.shortcut_config.get_modifiers(), modifier)
            self.view.SetShortcutKeys(self.shortcut_config.get_shortcuts(), key)

    def on_apply_clicked(self, evt):
        self._set_new_shortcut_for_selected_function()

    def on_selection_changed(self, evt):
        self._select_modifier_and_key_for_selected_function()

    def _select_modifier_and_key_for_selected_function(self):
        function = self.view.GetFunction()
        modifier, key = self.shortcut_config.get_modifier_and_key(function)
        self.view.SetModifier(modifier)
        self.view.SetShortcutKey(key)

    def _set_new_shortcut_for_selected_function(self):
        try:
            self._validate_input()
            self._validate_shortcut()
            function = self.view.GetFunction()
            shortcut = self._get_shortcut()
            self.shortcut_config.edit(function, shortcut)
            self.view.DisplayAckPopupWindow(_("Shortcut is saved"))
        except MissingInput as ex:
            self.view.DisplayWarningMessage(ex.message)
        except DuplicateShortcut as ex:
            self.view.DisplayWarningMessage(ex.message)

    def _validate_input(self):
        shortcut_key = self.view.GetShortcutKey()
        modifier = self.view.GetModifier()
        if not self.shortcut_config.is_valid(modifier, shortcut_key):
            raise MissingInput(_("Both Modifier and Shortcut key must be given!"))

    def _validate_shortcut(self):
        shortcut = self._get_shortcut()
        if self.shortcut_config.exists(shortcut):
            raise DuplicateShortcut(_("The shortcut %s is already bound to function '%s'!") %
                                    (shortcut, self.shortcut_config.get_function(shortcut)))

    def _get_shortcut(self):
        modifier = self.view.GetModifier()
        shortcut_key = self.view.GetShortcutKey()
        shortcut = "%s+%s" % (modifier, shortcut_key)
        if shortcut.startswith("+"):
            shortcut = shortcut[1:]
        return shortcut
