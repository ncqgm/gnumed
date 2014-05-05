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


"""
Naming and other conventions:
All data needed for configuration of shortcuts are collected in metadata 
objects wich are of type Metadata.
The text in a menu item to the right of the \t character is called shortcut.
Examples of shortcuts: Ctrl+N, PgUp, Shift+Ctrl+X
The shortcut, if it exists, consists of an optional modifier and a shortcut 
key. So the format of a shortcut is: [modifier +] shortcut_key.
The text in a menu item describing the action is called function.
wxid is the ID associated with the menu item.
cfgid is the ID used in the configuration file associated with a shortcut.
"""


import timelinelib.wxgui.dialogs.mainframe as mf


class Metadata(object):
    def __init__(self, wxid, cfgid, function, modifier, key):
        self.wxid = wxid
        self.cfgid = cfgid
        self.function = function
        self.modifier = modifier
        self.key = key
        
        
CTRL_MODIFIER = "Ctrl"
ALT_MODIFIER = "Alt" 
NO_MODIFIER = "" 
LABEL = "%s->%%s"
LABEL_FILE = LABEL % _("File")
LABEL_EDIT = LABEL % _("Edit")
LABEL_VIEW = LABEL % _("View")
LABEL_TIMELINE = LABEL % _("Timeline")
LABEL_NAVIGATE = LABEL % _("Navigate")
LABEL_HELP = LABEL % _("Help")
NAVLABEL = "%s(%s)->%%s"
LABEL_NAVIGATE_TIME = NAVLABEL % (_("Navigate"), "tm")
LABEL_NAVIGATE_NUM = NAVLABEL % (_("Navigate"), "num")
METADATA = [
             # File
             Metadata(mf.ID_NEW, "shortcut_file_new",  LABEL_FILE % _("File Timeline..."), CTRL_MODIFIER, "N"),
             Metadata(mf.ID_NEW_NUMERIC, "shortcut_file_new_numeric",  LABEL_FILE % _("Numeric Timeline..."), NO_MODIFIER, ""),
             Metadata(mf.ID_NEW_DIR, "shortcut_file_new_dir",  LABEL_FILE % _("Directory Timeline..."), NO_MODIFIER, ""),
             Metadata(mf.ID_SAVEAS, "shortcut_save_as",  LABEL_FILE % _("Save As..."), NO_MODIFIER, ""),
             Metadata(mf.ID_IMPORT, "shortcut_import",  LABEL_FILE % _("Import..."), NO_MODIFIER, ""),
             Metadata(mf.ID_EXPORT, "shortcut_export",  LABEL_FILE % _("Export Current view to Image..."), NO_MODIFIER, ""),
             Metadata(mf.ID_EXPORT_ALL, "shortcut_export_all",  LABEL_FILE % _("Export Whole Timeline to Images..."), NO_MODIFIER, ""),
             Metadata(mf.ID_EXPORT_SVG, "shortcut_export_svg",  LABEL_FILE % _("Export to SVG..."), NO_MODIFIER, ""),
             Metadata(mf.ID_EXIT, "shortcut_exit",  LABEL_FILE % _("Exit"), NO_MODIFIER, ""),
             # Edit
             Metadata(mf.ID_FIND, "shortcut_find",  LABEL_EDIT % _("Find"), CTRL_MODIFIER, "F"),
             Metadata(mf.ID_PREFERENCES, "shortcut_preferences",  LABEL_EDIT % _("Preferences"), NO_MODIFIER, ""),
             Metadata(mf.ID_EDIT_SHORTCUTS, "shortcut_shortcuts",  LABEL_EDIT % _("Shortcuts"), NO_MODIFIER, ""),
             # View
             Metadata(mf.ID_SIDEBAR, "shortcut_sidebar", LABEL_VIEW % _("Sidebar"), CTRL_MODIFIER, "I"),
             Metadata(mf.ID_LEGEND, "shortcut_legend",  LABEL_VIEW % _("Legend"),  NO_MODIFIER,  ""),
             Metadata(mf.ID_BALLOONS, "shortcut_ballons",  LABEL_VIEW % _("Ballons on hover"),  NO_MODIFIER,  ""),
             Metadata(mf.ID_ZOOMIN, "shortcut_zoomin", LABEL_VIEW % _("Zoom In"),  CTRL_MODIFIER,  "+"),
             Metadata(mf.ID_ZOOMOUT, "shortcut_zoomout", LABEL_VIEW % _("Zoom Out"),  CTRL_MODIFIER,  "-"),
             Metadata(mf.ID_VERT_ZOOMIN, "shortcut_vertical_zoomin", LABEL_VIEW % _("Vertical Zoom In"),  ALT_MODIFIER,  "+"),
             Metadata(mf.ID_VERT_ZOOMOUT, "shortcut_vertical_zoomout", LABEL_VIEW % _("Vertical Zoom Out"),  ALT_MODIFIER,  "-"),
             # Timeline
             Metadata(mf.ID_CREATE_EVENT, "shortcut_create_event", LABEL_TIMELINE % _("Create Event"), NO_MODIFIER, ""),
             Metadata(mf.ID_EDIT_EVENT, "shortcut_edit_event", LABEL_TIMELINE % _("Edit Selected Event"), NO_MODIFIER, ""),
             Metadata(mf.ID_DUPLICATE_EVENT, "shortcut_duplicate_event", LABEL_TIMELINE % _("Duplicate Selected Event"), NO_MODIFIER, ""),
             Metadata(mf.ID_SET_CATEGORY_ON_SELECTED, "shortcut_set_category_on_selected", LABEL_TIMELINE % _("Set Category on Selected Events"), NO_MODIFIER, ""),
             Metadata(mf.ID_MEASURE_DISTANCE, "shortcut_measure_distance", LABEL_TIMELINE % _("Measure Distance between two Events"), NO_MODIFIER, ""),
             Metadata(mf.ID_SET_CATEGORY_ON_WITHOUT, "shortcut_set_category_on_without", LABEL_TIMELINE % _("Set Category on events without category"), NO_MODIFIER, ""),
             Metadata(mf.ID_EDIT_CATEGORIES, "shortcut_edit_categories", LABEL_TIMELINE % _("Edit Categories"), NO_MODIFIER, ""),
             Metadata(mf.ID_SET_READONLY, "shortcut_set_readonly", LABEL_TIMELINE % _("Read Only"), NO_MODIFIER, ""),
             # Help
             Metadata(mf.ID_HELP, "shortcut_help_content", LABEL_HELP % _("Contents"), NO_MODIFIER, "F1"),
             Metadata(mf.ID_TUTORIAL, "shortcut_tutorial", LABEL_HELP % _("Getting started tutorial"), NO_MODIFIER, ""),
             Metadata(mf.ID_FEEDBACK, "shortcut_feedback", LABEL_HELP % _("Give Feedback"), NO_MODIFIER, ""),
             Metadata(mf.ID_CONTACT, "shortcut_contact", LABEL_HELP % _("Contact"), NO_MODIFIER, ""),
             Metadata(mf.ID_ABOUT, "shortcut_about", LABEL_HELP % _("About"), NO_MODIFIER, ""),
             # Navigate
             Metadata(mf.ID_FIND_FIRST, "shortcut_find_first_event", LABEL_NAVIGATE % _("Find First Event"), NO_MODIFIER, ""),
             Metadata(mf.ID_FIND_LAST, "shortcut_find_last_event", LABEL_NAVIGATE % _("Find Last Event"), NO_MODIFIER, ""),
             Metadata(mf.ID_FIT_ALL, "shortcut_find_all_events", LABEL_NAVIGATE % _("Find All Events"), NO_MODIFIER, ""),
             ]
FUNCTION_KEYS = ["PgDn", "PgUp", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
SHORTCUT_KEYS = ["", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
                 "O", "P", "Q", "R", "S", "T", "U", "V", "X", "Y", "Z",
                 "1", "2", "3", "4", "5", "6", "7", "8", "9", 
                 "+", "-",
                ] + FUNCTION_KEYS 
NON_EMPTY_MODIFIERS = ["Ctrl", "Alt", "Shift+Ctrl", "Shift+Alt", "Alt+Ctrl", "Shift+Alt+Ctrl"]
MODIFIERS = ["", ] + NON_EMPTY_MODIFIERS


class ShortcutController(object):
    def __init__(self, shortcut_config, wxItems):
        self.shortcut_config = shortcut_config
        self.wxItems = wxItems
        
    def load_config_settings(self):
        for metadata in METADATA:
            self._load_config_setting(metadata)
    
    def get_functions(self):
        return [metadata.function for metadata in METADATA]
        
    def get_modifiers(self):
        return MODIFIERS

    def get_shortcuts(self):
        return SHORTCUT_KEYS
    
    def get_function(self, shortcut):
        for metadata in METADATA:
            if self._shortcut_from_metadata(metadata) == shortcut:
                return metadata.function
        
    def get_modifier_and_key(self, function):
        for metadata in METADATA:
            if metadata.function == function:
                return metadata.modifier, metadata.key
            
    def is_valid(self, modifier, shortcut_key):
        if modifier == "":
            return shortcut_key in ["",] + FUNCTION_KEYS
        else:
            return modifier in MODIFIERS and shortcut_key in SHORTCUT_KEYS[1:]
        
    def exists(self, shortcut):
        return shortcut in [self._shortcut_from_metadata(metadata) for metadata in METADATA
                            if self._shortcut_from_metadata(metadata) != ""]
    
    def wxid_exists(self, wxid):
        return wxid in [shortcut.wxid for shortcut in METADATA]

    def is_function_key(self, shortcut):
        return shortcut in FUNCTION_KEYS
    
    def add_navigation_functions(self):
        self._add_time_navigation_functions()
        self._add_numeric_navigation_functions()
        
    def edit(self, function, new_shortcut):
        for metadata in METADATA:
            if metadata.function == function:
                try:
                    self._edit(metadata.wxid, new_shortcut, self.wxItems[metadata.wxid])
                except KeyError:
                    pass
        
    #
    # Internals
    #s
    def _add_time_navigation_functions(self):
        self._add_navigation_functions(0, LABEL_NAVIGATE_TIME)

    def _add_numeric_navigation_functions(self):
        self._add_navigation_functions(100, LABEL_NAVIGATE_NUM)

    def _add_navigation_functions(self, id_offset, function_format):
        try:
            pos = id_offset
            while True:
                wxid = mf.ID_NAVIGATE + pos
                if not self.wxid_exists(wxid):
                    self._add_navigation_function(wxid, function_format)
                else:
                    self._set_menuitem_shortcut(wxid)
                pos += 1
        except KeyError, ex:
            # We will end up here when there are no more navigation functions
            pass

    def _add_navigation_function(self, wxid, function_format):
        function = self._get_function_from_menuitem(wxid)
        modifier, shortcut_key = self._get_modifier_and_key_from_menuitem(wxid)
        metadata = Metadata(wxid, "shortcut_navigate_%s" % str(wxid), function_format % function, modifier, shortcut_key)
        METADATA.append(metadata)
        self._load_config_setting(metadata)
        
    def _get_function_from_menuitem(self, wxid):
        menu_item = self.wxItems[wxid]
        label = menu_item.GetItemLabel()
        function = label.split("\t")[0]
        function = function.replace("&", "")
        return function
    
    def _get_modifier_and_key_from_menuitem(self, wxid):
        menu_item = self.wxItems[wxid]
        label = menu_item.GetItemLabel()
        try:
            shortcut = label.split("\t")[1]
            try:
                modifier, shortcut_key = shortcut.split("+")
            except:
                modifier, shortcut_key = ("", shortcut) 
        except:
            modifier, shortcut_key = ("", "")
        return modifier, shortcut_key
    
    def _load_config_setting(self, metadata):
        shortcut = self._shortcut_from_metadata(metadata)
        shortcut = self.shortcut_config.get_shortcut_key(metadata.cfgid, shortcut)
        self.edit(metadata.function, shortcut)
    
    def _edit(self, wxid, new_shortcut, menu_item):
        if new_shortcut == "":
            new_shortcut = "+"
        if self._valid(new_shortcut):
            for metadata in METADATA:
                if metadata.wxid == wxid:
                    self._edit_shortcut(metadata, new_shortcut, menu_item)
                    break
    
    def _valid(self, shortcut):
        if shortcut == "+":
            return True
        return not self.exists(shortcut)
            
    def _edit_shortcut(self, metadata, new_shortcut, menu_item):
        try:
            metadata.modifier, metadata.key = new_shortcut.rsplit("+", 1)
        except:
            metadata.modifier, metadata.key = ("", new_shortcut)
        self.shortcut_config.set_shortcut_key(metadata.cfgid, new_shortcut)
        self._set_menuitem_label(menu_item, new_shortcut)

    def _set_menuitem_label(self, menu_item, new_shortcut):
        label = menu_item.GetItemLabel()
        prefix = label.split("\t")[0]
        if new_shortcut in ("", "+"):
            new_label = prefix
        else:
            new_label = "%s\t%s" % (prefix, new_shortcut)
        menu_item.SetItemLabel(new_label)

    def _shortcut_from_metadata(self, metadata):
        if metadata.modifier != "":
            return "%s+%s" % (metadata.modifier, metadata.key)
        else:
            return metadata.key

    def _set_menuitem_shortcut(self, wxid):
        menu_item = self.wxItems[wxid]
        for metadata in METADATA:
            if metadata.wxid == wxid:
                shortcut_key = self._shortcut_from_metadata(metadata)
                self._set_menuitem_label(menu_item, shortcut_key)
                break
