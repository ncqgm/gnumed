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


from timelinelib.wxgui.framework import Controller


class EditContainerDialogController(Controller):

    """
    This controller is responsible for two things:

    1. Creating a new container
    2. Updating properties of an existing container

    When creating a new container the result is NOT stored in the database.
    This happens later when the first event added to the container is saved to
    the database.

    The reason for this behavior is that we don't want to have empty containers
    in the database. When updating the properties of an existing container the
    changes are stored in the timeline database.
    """

    def on_init(self, db, container):
        self.view.PopulateCategories()
        self._create_container(db, container)
        self._populate_view()

    def on_ok_clicked(self, event):
        if self._validate():
            self._populate_container()
            if self._is_updating:
                self._container.save()
            self.view.EndModalOk()

    def get_container(self):
        return self._container

    def _create_container(self, db, container):
        if container is None:
            self._is_updating = False
            self._container = db.new_container(text="", category=None)
        else:
            self._is_updating = True
            self._container = container

    def _populate_view(self):
        self.view.SetName(self._container.get_text())
        self.view.SetCategory(self._container.get_category())

    def _validate(self):
        if self.view.GetName() == "":
            self.view.DisplayInvalidName(
                _("Field '%s' can't be empty.") % _("Name")
            )
            return False
        return True

    def _populate_container(self):
        self._container.text = self.view.GetName()
        self._container.category = self.view.GetCategory()
