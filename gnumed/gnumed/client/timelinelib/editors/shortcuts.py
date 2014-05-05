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


from timelinelib.wxgui.utils import display_warning_message


class MissingInput(Exception):
    pass


class DuplicateShortcut(Exception):
    pass


class ShortcutsEditor(object):
    def __init__(self, view, shortcut_config):
        self.view = view
        self.shortcut_config = shortcut_config
        self._populate_view()

    #
    # View API
    #
    def on_function_selected(self):
        self._select_modifier_and_key_for_selected_function()
        
    def apply(self):
        self._set_new_shortcut_for_selected_function()
        pass

    #
    # Internals
    #
    def _select_modifier_and_key_for_selected_function(self):
        function = self.view.get_function()
        modifier, key = self.shortcut_config.get_modifier_and_key(function)
        self.view.set_modifier(modifier)
        self.view.set_shortcut_key(key)
            
    def _set_new_shortcut_for_selected_function(self):
        try:
            self._validate_input()
            self._validate_shortcut()
            function = self.view.get_function()
            shortcut = self._get_shortcut()
            self.shortcut_config.edit(function, shortcut)
        except MissingInput, ex:
            display_warning_message(ex.message)
        except DuplicateShortcut, ex:
            display_warning_message(ex.message)
        
    def _validate_input(self):
        shortcut_key = self.view.get_shortcut_key()
        modifier = self.view.get_modifier()
        if not self.shortcut_config.is_valid(modifier, shortcut_key):
            raise MissingInput(_("Both Modifier and Shortcut key must be given!"))
       
    def _validate_shortcut(self):
        shortcut = self._get_shortcut()
        if self.shortcut_config.exists(shortcut):
            function = self.view.get_function()
            raise DuplicateShortcut(_("The shortcut %s is already bound to function '%s'!") % 
                                    (shortcut, self.shortcut_config.get_function(shortcut)))

    def _get_shortcut(self): 
        modifier = self.view.get_modifier()
        shortcut_key = self.view.get_shortcut_key()
        shortcut = "%s+%s" % (modifier, shortcut_key)
        if shortcut.startswith("+"):
            shortcut = shortcut[1:]
        return shortcut
                                
    #
    # Construction
    #
    def _populate_view(self):
        functions = self.shortcut_config.get_functions()
        modifier, key = self.shortcut_config.get_modifier_and_key(functions[0])
        self.view.set_functions(functions)
        self.view.set_modifiers(self.shortcut_config.get_modifiers(), modifier)
        self.view.set_shortcut_keys(self.shortcut_config.get_shortcuts(), key)
        