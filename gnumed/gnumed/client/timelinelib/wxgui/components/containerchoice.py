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
import wx.lib.newevent

from timelinelib.canvas.data.exceptions import TimelineIOError
from timelinelib.wxgui.dialogs.editcontainer.view import EditContainerDialog
import timelinelib.wxgui.utils as gui_utils


class ContainerChoice(wx.Choice):

    ContainerChangedEvent, EVT_CONTAINER_CHANGED = wx.lib.newevent.NewEvent()

    def __init__(self, parent, db, **kwargs):
        wx.Choice.__init__(self, parent, **kwargs)
        self.db = db
        self._clear()
        self.Bind(wx.EVT_CHOICE, self._on_choice)

    def Fill(self, select_container):
        self._clear()
        self._fill(self.db.get_containers(), select_container)

    def GetSelectedContainer(self):
        selection = self.GetSelection()
        if selection != -1:
            return self.GetClientData(selection)
        else:
            return None

    def _on_choice(self, event):
        new_selection_index = event.GetSelection()
        if new_selection_index > self.last_real_container_index:
            self.SetSelection(self.current_container_selection)
            if new_selection_index == self.add_container_item_index:
                self._add_container()
        else:
            self.current_container_selection = new_selection_index
            wx.PostEvent(self, self.ContainerChangedEvent())

    def _add_container(self):
        dialog = EditContainerDialog(self, _("Add Container"), self.db, None)
        if dialog.ShowModal() == wx.ID_OK:
            self.Fill(dialog.GetEditedContainer())
        dialog.Destroy()

    def _clear(self):
        self.last_real_container_index = None
        self.add_container_item_index = None
        self.current_container_selection = None
        self.Clear()

    def _fill(self, containers, select_container):
        self.Append("", None)
        selection_set = False
        current_item_index = 1
        if select_container is not None and select_container not in containers:
            self.Append(select_container.text, select_container)
            self._select(current_item_index)
            current_item_index += 1
            selection_set = True
        for container in containers:
            self.Append(container.text, container)
            if not selection_set:
                if container == select_container:
                    self._select(current_item_index)
                    selection_set = True
            current_item_index += 1
        self.last_real_container_index = current_item_index - 1
        self.add_container_item_index = self.last_real_container_index + 2
        self.Append("", None)
        self.Append(_("Add new"), None)
        if not selection_set:
            self._select(0)

    def _select(self, index):
        self.SetSelection(index)
        self.current_container_selection = self.GetSelection()
        wx.PostEvent(self, self.ContainerChangedEvent())
