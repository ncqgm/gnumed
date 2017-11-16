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

from timelinelib.canvas.data import sort_categories


# Border, in pixels, between controls in a window (should always be used when
# border is needed)
BORDER = 5
unlock_function = None


class WildcardHelper(object):

    def __init__(self, name, extensions):
        self.name = name
        self.ext_data = {}
        self.ext_names = []
        self._extract_ext_info(extensions)

    def wildcard_string(self):
        return "%s (%s)|%s" % (
            self.name,
            ", ".join(["*." + e for e in self.ext_names]),
            ";".join(["*." + e for e in self.ext_names]))

    def get_path(self, dialog):
        path = dialog.GetPath()
        for ext_name in self.ext_names:
            if path.endswith("." + ext_name):
                return path
        return "%s.%s" % (path, self.ext_names[0])

    def get_extension_data(self, path):
        split_path = path.split(".")
        if len(split_path) > 1:
            ext_name = split_path[-1]
            return self.ext_data.get(ext_name, None)
        return None

    def _extract_ext_info(self, extensions):
        for ext in extensions:
            if isinstance(ext, tuple):
                name, data = ext
                self.ext_data[name] = data
                self.ext_names.append(name)
            else:
                self.ext_names.append(ext)


class PopupTextWindow(wx.PopupTransientWindow):

    def __init__(self, parent, text, color="#D3F4B8", timeout=1200, pos=None):
        self.timeout = timeout
        wx.PopupTransientWindow.__init__(self, parent, wx.NO_BORDER)
        self.SetBackgroundColour(color)
        st = wx.StaticText(self, wx.ID_ANY, text, pos=(10, 10))
        sz = st.GetBestSize()
        self.SetSize((sz.width + 20, sz.height + 20))
        if pos:
            self.Position(pos, (-1, -1))
        self.Popup()

    def ProcessLeftDown(self, evt):
        return False

    def Popup(self):
        super(PopupTextWindow, self).Popup()
        wx.CallLater(self.timeout, self.Dismiss)


def category_tree(category_list, parent=None, remove=None):
    """
    Transform flat list of categories to a tree based on parent attribute.

    The top-level categories have the given parent and each level in the tree
    is sorted.

    If remove is given then the subtree with remove as root will not be
    included.

    The tree is represented as a list of tuples, (cat, sub-tree), where cat is
    the parent category and subtree is the same tree representation of the
    children.
    """
    children = [child for child in category_list
                if (child._get_parent() is parent and child is not remove)]
    sorted_children = sort_categories(children)
    tree = [(x, category_tree(category_list, x, remove))
            for x in sorted_children]
    return tree


def _set_focus_and_select(ctrl):
    ctrl.SetFocus()
    if hasattr(ctrl, "SelectAll"):
        ctrl.SelectAll()


def display_error_message(message, parent=None):
    """Display an error message in a modal dialog box"""
    dial = wx.MessageDialog(parent, message, _("Error"), wx.OK | wx.ICON_ERROR)
    dial.ShowModal()


def display_warning_message(message, parent=None):
    dial = wx.MessageDialog(parent, message, _("Warning"), wx.OK | wx.ICON_WARNING)
    dial.ShowModal()


def display_information_message(caption, message, parent=None):
    dialog = wx.MessageDialog(parent, message, caption,
                              wx.OK | wx.ICON_INFORMATION)
    dialog.ShowModal()
    dialog.Destroy()


def display_categories_editor_moved_message(parent):
    display_information_message(
        caption=_("Dialog moved"),
        message=_("This dialog has been removed. Edit categories in the sidebar instead."),
        parent=parent)


def get_user_ack(question, parent=None):
    return wx.MessageBox(question, _("Question"),
                         wx.YES_NO | wx.CENTRE | wx.NO_DEFAULT, parent) == wx.YES


def _ask_question(question, parent=None):
    """Ask a yes/no question and return the reply."""
    return wx.MessageBox(question, _("Question"),
                         wx.YES_NO | wx.CENTRE | wx.NO_DEFAULT, parent)


def set_wait_cursor(parent):
    parent.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))


def set_default_cursor(parent):
    parent.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))


def set_focus(parent, name):
    for child in parent.GetChildren():
        if child.GetName() == name:
            child.SetFocus()
            break


def register_unlock_function(function):
    global unlock_function
    unlock_function = function
