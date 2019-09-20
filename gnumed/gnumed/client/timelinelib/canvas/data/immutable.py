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


from timelinelib.canvas.drawing.drawers import get_progress_color
from timelinelib.general.immutable import Field
from timelinelib.general.immutable import ImmutableDict
from timelinelib.general.immutable import ImmutableRecord


class ImmutableEvent(ImmutableRecord):

    text = Field(None)
    time_period = Field(None)
    category_id = Field(None)
    category_ids = Field(ImmutableDict())
    fuzzy = Field(False)
    locked = Field(False)
    ends_today = Field(False)
    description = Field(None)
    icon = Field(None)
    hyperlink = Field(None)
    alert = Field(None)
    progress = Field(None)
    default_color = Field(None)
    container_id = Field(None)
    sort_order = Field(None)


class ImmutableMilestone(ImmutableRecord):

    text = Field(None)
    category_id = Field(None)
    category_ids = Field(ImmutableDict())
    time_period = Field(None)
    description = Field(None)
    default_color = Field((255, 255, 128))
    sort_order = Field(None)


class ImmutableEra(ImmutableRecord):

    name = Field(None)
    time_period = Field(None)
    color = Field((200, 200, 200))
    ends_today = Field(False)


class ImmutableCategory(ImmutableRecord):

    name = Field("")
    color = Field((255, 0, 0))
    progress_color = Field(get_progress_color((255, 0, 0)))
    done_color = Field(get_progress_color((255, 0, 0)))
    font_color = Field((0, 0, 0))
    parent_id = Field(None)


class ImmutableContainer(ImmutableRecord):

    text = Field(None)
    category_id = Field(None)
    category_ids = Field(ImmutableDict())
    time_period = Field(None)
    description = Field(None)


class ImmutableDB(ImmutableRecord):

    categories = Field(ImmutableDict())
    containers = Field(ImmutableDict())
    events = Field(ImmutableDict())
    milestones = Field(ImmutableDict())
    eras = Field(ImmutableDict())

    def save_event(self, event, id_):
        self._ensure_non_none_category_exists(event.category_id)
        self._ensure_non_none_container_exists(event.container_id)
        return self.update(
            events=self.events.update({
                id_: event,
            })
        )

    def delete_event(self, id_):
        self._ensure_event_exists(id_)
        return self.update(
            events=self.events.remove(id_)
        )

    def save_milestone(self, milestone, id_):
        self._ensure_non_none_category_exists(milestone.category_id)
        return self.update(
            milestones=self.milestones.update({
                id_: milestone
            })
        )

    def delete_milestone(self, id_):
        self._ensure_milestone_exists(id_)
        return self.update(
            milestones=self.milestones.remove(id_)
        )

    def save_era(self, era, id_):
        return self.update(
            eras=self.eras.update({
                id_: era,
            })
        )

    def delete_era(self, id_):
        self._ensure_era_exists(id_)
        return self.update(
            eras=self.eras.remove(id_)
        )

    def save_category(self, category, id_):
        self._ensure_category_name_is_unique(id_, category.name)
        self._ensure_non_none_category_exists(category.parent_id)
        self._ensure_no_category_circular(id_, category.parent_id)
        return self.update(
            categories=self.categories.update({id_: category})
        )

    def delete_category(self, delete_id):
        self._ensure_category_exists(delete_id)
        new_parent_id = self.categories.get(delete_id).parent_id

        def update_parent_id(category):
            if category.parent_id == delete_id:
                return category.update(parent_id=new_parent_id)
            else:
                return category

        def update_category_id(thing):
            if thing.category_id == delete_id:
                return thing.update(category_id=new_parent_id)
            else:
                return thing
        return self.update(
            categories=self.categories.remove(delete_id).map(update_parent_id),
            events=self.events.map(update_category_id),
            milestones=self.milestones.map(update_category_id),
            containers=self.containers.map(update_category_id)
        )

    def save_container(self, container, id_):
        self._ensure_non_none_category_exists(container.category_id)
        return self.update(
            containers=self.containers.update({id_: container})
        )

    def delete_container(self, delete_id):
        self._ensure_container_exists(delete_id)

        def update_container_id(event):
            if event.container_id == delete_id:
                return event.update(container_id=None)
            else:
                return event
        return self.update(
            containers=self.containers.remove(delete_id),
            events=self.events.map(update_container_id),
        )

    def _ensure_event_exists(self, id_):
        if id_ not in self.events:
            raise InvalidOperationError(
                "Event with id {0!r} does not exist".format(id_)
            )

    def _ensure_milestone_exists(self, id_):
        if id_ not in self.milestones:
            raise InvalidOperationError(
                "Milestone with id {0!r} does not exist".format(id_)
            )

    def _ensure_era_exists(self, id_):
        if id_ not in self.eras:
            raise InvalidOperationError(
                "Era with id {0!r} does not exist".format(id_)
            )

    def _ensure_category_name_is_unique(self, save_id, save_name):
        for id_, category in self.categories:
            if id_ != save_id and category.name == save_name:
                raise InvalidOperationError(
                    "Category name {0!r} is not unique".format(save_name)
                )

    def _ensure_non_none_category_exists(self, id_):
        if id_ is not None:
            self._ensure_category_exists(id_)

    def _ensure_category_exists(self, id_):
        if id_ not in self.categories:
            raise InvalidOperationError(
                "Category with id {0!r} does not exist".format(id_)
            )

    def _ensure_no_category_circular(self, save_id, parent_id):
        while parent_id is not None:
            if parent_id == save_id:
                raise InvalidOperationError(
                    "Circular category parent"
                )
            else:
                parent_id = self.categories.get(parent_id).parent_id

    def _ensure_non_none_container_exists(self, id_):
        if id_ is not None:
            self._ensure_container_exists(id_)

    def _ensure_container_exists(self, id_):
        if id_ not in self.containers:
            raise InvalidOperationError(
                "Container with id {0!r} does not exist".format(id_)
            )


class InvalidOperationError(Exception):
    pass
