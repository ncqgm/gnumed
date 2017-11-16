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


from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.dialogs.systeminfo.controller import SystemInfoDialogController


class SystemInfoDialog(Dialog):

    """
    <BoxSizerVertical>
        <FlexGridSizer name="grid" rows="0" columns="2" border="ALL" >
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(system_version)"/>
            <StaticText align="ALIGN_CENTER_VERTICAL" name="system_version" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(python_version)" />
            <StaticText align="ALIGN_CENTER_VERTICAL" name="python_version" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(wxpython_version)" />
            <StaticText align="ALIGN_CENTER_VERTICAL" name="wxpython_version" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(locale_setting)" />
            <StaticText align="ALIGN_CENTER_VERTICAL" name="locale_setting" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(date_format)" />
            <StaticText align="ALIGN_CENTER_VERTICAL" name="date_format" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(config_file)" />
            <StaticText align="ALIGN_CENTER_VERTICAL" name="config_file" />
        </FlexGridSizer>
        <BoxSizerHorizontal>
            <StretchSpacer/>
            <DialogButtonsCloseSizer  border="LEFT|RIGHT|BOTTOM" align="ALIGN_RIGHT"/>
        </BoxSizerHorizontal>
    </BoxSizerVertical>
    """

    def __init__(self, parent):
        Dialog.__init__(self, SystemInfoDialogController, parent, {
            "system_version": _("System version:"),
            "python_version": _("Python version:"),
            "wxpython_version": _("wxPython version:"),
            "locale_setting": _("Locale setting:"),
            "date_format": _("Locale date format:"),
            "config_file": _("Configuration file:"),
        }, title=_("System Information"))
        self.controller.on_init(parent)

    def SetSystemVersion(self, value):
        self.system_version.SetLabel(value)

    def SetPythonVersion(self, value):
        self.python_version.SetLabel(value)

    def SetWxPythonVersion(self, value):
        self.wxpython_version.SetLabel(value)

    def SetLocaleSetting(self, value):
        self.locale_setting.SetLabel(value)

    def SetDateFormat(self, value):
        self.date_format.SetLabel(value)

    def SetConfigFile(self, value):
        self.config_file.SetLabel(value)


def show_system_info_dialog(*args, **kwargs):
    dialog = SystemInfoDialog(get_frame_window(args[0]))
    try:
        dialog.ShowModal()
    finally:
        dialog.Destroy()


def get_frame_window(evt):
    frame = get_frame_from_invoking_window(evt)
    if frame is None:
        frame = get_frame_from_menu_bar(evt)
    return frame


def get_frame_from_invoking_window(evt):
    evt_object = evt.GetEventObject()
    if hasattr(evt_object, 'InvokingWindow'):
        return evt_object.InvokingWindow


def get_frame_from_menu_bar(evt):
    evt_object = evt.GetEventObject()
    if hasattr(evt_object, 'MenuBar'):
        menu_bar = evt_object.MenuBar
        if hasattr(menu_bar, 'Parent'):
            return menu_bar.Parent
