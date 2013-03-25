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


from timelinelib.db.objects import Container
from timelinelib.repositories.dbwrapper import DbWrapperEventRepository


class ContainerEditor(object):
    """
    This controller is responsible for two things:
      1. creating a new Container event
      2. updating properties of an existing Container event
    When creating a new Container event the result is NOT stored in the
    timeline database. This happens later when the first event added to the
    container is saved to the database.
    The reason for this behavior is that we don't want to have empty Conatiners
    in the database.
    When updating the properties of an existing Container event the changes
    are stored in the timeline database.
    """
    def __init__(self, view, db, container):
        self._set_initial_values_to_member_variables(view, db, container)
        self._set_view_initial_values()

    def _set_initial_values_to_member_variables(self, view, db, container):
        self.view = view
        self.db = db
        self.container = container
        self.container_exists = (self.container != None)
        if self.container_exists:
            self.name = self.container.text
            self.category = self.container.category
        else:
            self.name = ""
            self.category = None

    def _set_view_initial_values(self):
        self.view.set_name(self.name)
        self.view.set_category(self.category)

    #
    # Dialog API
    #
    def save(self):
        self.name = self.view.get_name()
        self.category = self.view.get_category()
        try:
            self._verify_name()
            if self.container_exists:
                self._update_container()
            else:
                self._create_container()
            self.view.close()
        except ValueError:
            pass

    def get_container(self):
        return self.container

    #
    # Internals
    #
    def _verify_name(self):
        name_is_invalid = (self.name == "")
        if name_is_invalid:
            msg = _("Field '%s' can't be empty.") % _("Name")
            self.view.display_invalid_name(msg)
            raise ValueError()

    def _update_container(self):
        self.container.update_properties(self.name, self.category)
        self._save_to_db()

    def _save_to_db(self):
        try:
            DbWrapperEventRepository(self.db).save(self.container)
        except Exception, ex:
            self.view.display_db_exception(ex)
            raise ex

    def _create_container(self):
        time_type = self.db.get_time_type()
        start = time_type.now()
        end = start
        self.container = Container(time_type, start, end, self.name,
                                   self.category)
