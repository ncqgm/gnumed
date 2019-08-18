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


import wx


class ToolbarCreator(object):

    def __init__(self, parent, config):
        self._parent = parent
        self._config = config

    def create(self):
        self.toolbar = self._parent.CreateToolbar()
        self._add_event_text_alignment()
        self.toolbar.AddSeparator()
        self._add_point_event_alignment()
        self.toolbar.Realize()
        self._set_visibility()
        self._config.listen_for_any(self._set_visibility)
        return self.toolbar

    def _add_event_text_alignment(self):
        spec = {'tool-1-name': _("Center"),
                'tool-2-name': _("Left"),
                'tool-1-image': 'format-justify-center.png',
                'tool-2-image': 'format-justify-left.png',
                'config-name': 'center_event_texts',
                }
        self._toggle_toolbar(spec)

    def _add_point_event_alignment(self):
        spec = {'tool-1-name': _("Left"),
                'tool-2-name': _("Center"),
                'tool-1-image': 'event-line-left.png',
                'tool-2-image': 'event-line-center.png',
                'config-name': 'draw_point_events_to_right',
                }
        self._toggle_toolbar(spec)

    def _add_radio(self, text, icon):
        return self.toolbar.AddRadioTool(
            wx.ID_ANY,
            text,
            self._parent.BitmapFromIcon(icon),
            shortHelp=text
        )

    def _set_visibility(self):
        self.toolbar.Show(self._config.show_toolbar)
        self._parent.Layout()

    def _toggle_toolbar(self, spec):
        first_tool = self._add_radio(spec['tool-1-name'], spec['tool-1-image'])
        second_tool = self._add_radio(spec['tool-2-name'], spec['tool-2-image'])

        def on_first_tool_click(event):
            self._config._set(spec['config-name'], True)

        def on_second_tool_click(event):
            self._config._set(spec['config-name'], False)

        def check_item_corresponding_to_config():
            if self._config._get(spec['config-name']):
                self.toolbar.ToggleTool(first_tool.GetId(), True)
            else:
                self.toolbar.ToggleTool(second_tool.GetId(), True)
        self._parent.Bind(wx.EVT_TOOL, on_first_tool_click, first_tool)
        self._parent.Bind(wx.EVT_TOOL, on_second_tool_click, second_tool)
        self._config.listen_for_any(check_item_corresponding_to_config)
        check_item_corresponding_to_config()
