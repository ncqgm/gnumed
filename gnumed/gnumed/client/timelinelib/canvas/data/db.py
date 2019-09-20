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


import collections
import contextlib

from timelinelib.calendar.gregorian.timetype import GregorianTimeType
from timelinelib.canvas.data.exceptions import TimelineIOError
from timelinelib.canvas.data.immutable import ImmutableDB
from timelinelib.canvas.data import Category
from timelinelib.canvas.data import Container
from timelinelib.canvas.data import Era
from timelinelib.canvas.data import Eras
from timelinelib.canvas.data import Event
from timelinelib.canvas.data import Milestone
from timelinelib.canvas.data import Subevent
from timelinelib.canvas.data import TimePeriod
from timelinelib.canvas.data.transactions import Transactions
from timelinelib.general.observer import Observable


# A category was added, edited, or deleted
STATE_CHANGE_CATEGORY = 1
# Something happened that changed the state of the timeline
STATE_CHANGE_ANY = 2


class MemoryDB(Observable):

    def __init__(self):
        Observable.__init__(self)
        self._id_counter = 0
        self._transactions = Transactions(ImmutableDB())
        self._transactions.listen_for_any(self._transaction_committed)
        self.path = ""
        self.displayed_period = None
        self._hidden_category_ids = []
        self.time_type = GregorianTimeType()
        self.saved_now = self.time_type.now()
        self.readonly = False
        self._save_callback = None
        self._should_lock = False
        self._current_query = None

    def new_category(self, **kwargs):
        return self._create_wrapper(Category, **kwargs)

    def new_milestone(self, **kwargs):
        return self._create_wrapper(Milestone, **kwargs)

    def new_era(self, **kwargs):
        return self._create_wrapper(Era, **kwargs)

    def new_event(self, **kwargs):
        return self._create_wrapper(Event, **kwargs)

    def new_container(self, **kwargs):
        return self._create_wrapper(Container, **kwargs)

    def new_subevent(self, **kwargs):
        return self._create_wrapper(Subevent, **kwargs)

    def _create_wrapper(self, wrapper_class, **kwargs):
        wrapper = wrapper_class(db=self)
        if hasattr(wrapper, "time_period") and "time_period" not in kwargs:
            now = self.time_type.now()
            kwargs["time_period"] = TimePeriod(now, now)
        if "container" in kwargs:
            container = kwargs.pop("container")
        else:
            container = None
        for name, value in kwargs.items():
            setattr(wrapper, name, value)
        if container is not None:
            wrapper.container = container
        return wrapper

    def next_id(self):
        self._id_counter += 1
        return self._id_counter

    def transaction(self, name):
        return self._transactions.new(name)

    def clear_transactions(self):
        self._transactions.clear()

    def transactions_status(self):
        return self._transactions.status

    def display_in_canvas(self, canvas):
        canvas.SetTimeline(self)

    def is_saved(self):
        return self._save_callback is not None

    def get_should_lock(self):
        return self._should_lock

    def set_should_lock(self, should_lock):
        self._should_lock = should_lock

    def register_save_callback(self, callback):
        self._save_callback = callback

    def get_time_type(self):
        return self.time_type

    def set_time_type(self, time_type):
        self.time_type = time_type
        if time_type is not None:
            self.saved_now = time_type.now()

    def is_read_only(self):
        return self.readonly

    def set_readonly(self):
        self.readonly = True
        self._notify(STATE_CHANGE_ANY)

    def search(self, search_string):
        return _generic_event_search(self.get_all_events(), search_string)

    def get_events(self, time_period):
        return self._get_events(lambda immutable_event:
            immutable_event.time_period.inside_period(time_period)
        )

    def get_all_events(self):
        return self._get_events(lambda immutable_event: True)

    def get_max_sort_order(self):
        max = -1
        for id_, immutable_value in self._transactions.value.milestones:
            sort_order = immutable_value["sort_order"]
            if sort_order > max:
                max = sort_order
        for id_, immutable_value in self._transactions.value.events:
            sort_order = immutable_value["sort_order"]
            if sort_order > max:
                max = sort_order
        return max

    def _get_events(self, criteria_fn):
        with self._query() as query:
            return (
                self._get_milestones(criteria_fn) +
                sort_events(self.get_containers() + [
                    query.get_event(id_)
                    for id_, immutable_event
                    in self._transactions.value.events
                    if criteria_fn(immutable_event)
                ])
            )

    def _get_milestones(self, criteria_fn):
        with self._query() as query:
            return [
                query.get_milestone(id_)
                for id_, immutable_milestone
                in self._transactions.value.milestones
                if criteria_fn(immutable_milestone)
            ]

    def get_first_event(self):
        if len(self._transactions.value.events) == 0:
            return None
        else:
            id_, immutable_event = min(
                self._transactions.value.events,
                key=lambda id__immutable_event:
                    id__immutable_event[1].time_period.start_time
            )
            with self._query() as query:
                return query.get_event(id_)

    def get_last_event(self):
        if len(self._transactions.value.events) == 0:
            return None
        else:
            id_, immutable_event = max(
                self._transactions.value.events,
                key=lambda id__immutable_event1:
                    id__immutable_event1[1].time_period.end_time
            )
            with self._query() as query:
                return query.get_event(id_)

    def save_events(self, events):
        try:
            with self.transaction("Save events"):
                for event in events:
                    event.db = self
                    event.save()
        except Exception as e:
            raise TimelineIOError("Saving event failed: %s" % e)

    def save_event(self, event):
        self.save_events([event])

    def delete_event(self, event_or_id):
        try:
            if isinstance(event_or_id, Event):
                event = event_or_id
            else:
                event = self.find_event_with_id(event_or_id)
            event.db = self
            event.delete()
        except Exception as e:
            raise TimelineIOError("Deleting event failed: %s" % e)

    def get_all_eras(self):
        return self._get_eras().get_all()

    def get_all_periods(self):
        return self._get_eras().get_all_periods()

    def _get_eras(self):
        with self._query() as query:
            return Eras(
                now_func=self.time_type.now,
                eras=[
                    query.get_era(id_)
                    for id_, immutable_era
                    in self._transactions.value.eras
                ]
            )

    def save_era(self, era):
        try:
            era.db = self
            era.save()
        except Exception as e:
            raise TimelineIOError("Saving Era failed: %s" % e)

    def delete_era(self, era):
        try:
            era.db = self
            era.delete()
        except Exception as e:
            raise TimelineIOError("Deleting Era failed: %s" % e)

    def get_categories(self):
        with self._query() as query:
            return [
                query.get_category(id_)
                for id_, immutable_category
                in self._transactions.value.categories
            ]

    def get_containers(self):
        with self._query() as query:
            return [
                query.get_container(id_)
                for id_, immutable_container
                in self._transactions.value.containers
            ]

    def save_category(self, category):
        try:
            category.db = self
            category.save()
        except Exception as e:
            raise TimelineIOError("Saving category failed: %s" % e)

    def get_category_by_name(self, name):
        with self._query() as query:
            for id_, immutable_category in self._transactions.value.categories:
                if immutable_category.name == name:
                    return query.get_category(id_)
            return None

    def get_category_by_id(self, id_):
        for category in self.get_categories():
            if category.id == id_:
                return category

    def delete_category(self, category_or_id):
        try:
            if isinstance(category_or_id, Category):
                category = category_or_id
            else:
                with self._query() as query:
                    category = query.get_category(category_or_id)
            if category.id in self._hidden_category_ids:
                self._hidden_category_ids.remove(category.id)
            category.db = self
            category.delete()
        except Exception as e:
            raise TimelineIOError("Deleting category failed: %s" % e)

    def get_saved_now(self):
        return self.saved_now

    def set_saved_now(self, time):
        self.saved_now = time
        self.time_type.set_saved_now(time)

    def load_view_properties(self, view_properties):
        view_properties.displayed_period = self.displayed_period
        for cat in self.get_categories():
            visible = cat.id not in self._hidden_category_ids
            view_properties.set_category_visible(cat, visible)

    def save_view_properties(self, view_properties):
        if view_properties.displayed_period is not None:
            if not view_properties.displayed_period.is_period():
                raise TimelineIOError(_("Displayed period must be > 0."))
            self.displayed_period = view_properties.displayed_period
        self._hidden_category_ids = []
        for cat in self.get_categories():
            if not view_properties.is_category_visible(cat):
                self._hidden_category_ids.append(cat.id)
        self._save()

    def place_event_after_event(self, event_to_place, target_event):
        self._place_event(
            lambda index_to_place, index_target: index_to_place < index_target,
            event_to_place.id,
            target_event.id
        )

    def place_event_before_event(self, event_to_place, target_event):
        self._place_event(
            lambda index_to_place, index_target: index_to_place > index_target,
            event_to_place.id,
            target_event.id
        )

    def _place_event(self, validate_index, id_to_place, id_target):
        all_events = [
            event
            for event
            in self.get_all_events()
            if not event.is_subevent()
        ]
        for events in self._get_event_lists(all_events):
            if self._move(events, validate_index, id_to_place, id_target):
                with self.transaction("Move event"):
                    EventSorter().save_sort_order(all_events)
                    return

    def _get_event_lists(self, all_events):
        yield all_events
        for event in all_events:
            if event.is_container():
                yield event.subevents

    def _move(self, events, validate_index, id_to_place, id_target):
        index_to_place = None
        index_target = None
        for index, event in enumerate(events):
            if event.id == id_to_place:
                index_to_place = index
            if event.id == id_target:
                index_target = index
        if index_to_place is None:
            return False
        if index_target is None:
            return False
        if validate_index(index_to_place, index_target):
            events.insert(index_target, events.pop(index_to_place))
            return True
        return False

    def undo(self):
        index = self._get_undo_index()
        if index is not None:
            self._transactions.move(index)

    def redo(self):
        index = self._get_redo_index()
        if index is not None:
            self._transactions.move(index)

    def undo_enabled(self):
        return not self.is_read_only() and self._get_undo_index() is not None

    def redo_enabled(self):
        return not self.is_read_only() and self._get_redo_index() is not None

    def _get_undo_index(self):
        index, is_in_transaction, history = self._transactions.status
        if index > 0:
            return index - 1
        else:
            return None

    def _get_redo_index(self):
        index, is_in_transaction, history = self._transactions.status
        if index < len(history) - 1:
            return index + 1
        else:
            return None

    def find_event_with_ids(self, ids):
        with self._query() as query:
            events = [self.find_event_with_id(id_) for id_ in ids]
            events = [e for e in events if e is not None]
            return events

    def find_event_with_id(self, event_id):
        with self._query() as query:
            if query.event_exists(event_id):
                return query.get_event(event_id)
            if query.container_exists(event_id):
                return query.get_container(event_id)
            if query.milestone_exists(event_id):
                return query.get_milestone(event_id)

    def _transaction_committed(self):
        self._save()
        self._notify(STATE_CHANGE_ANY)

    def _save(self):
        if self._save_callback is not None:
            self._save_callback()

    def get_displayed_period(self):
        """
        Inheritors can call this method to get the displayed period used in
        load_view_properties and save_view_properties.
        """
        return self.displayed_period

    def set_displayed_period(self, period):
        """
        Inheritors can call this method to set the displayed period used in
        load_view_properties and save_view_properties.
        """
        self.displayed_period = period

    def get_hidden_categories(self):
        with self._query() as query:
            return [
                query.get_category(id_)
                for id_
                in self._hidden_category_ids
            ]

    def set_hidden_categories(self, hidden_categories):
        self._hidden_category_ids = []
        for cat in hidden_categories:
            if cat.id not in self._transactions.value.categories:
                raise ValueError("Category '%s' not in db." % cat.get_name())
            self._hidden_category_ids.append(cat.id)

    def import_db(self, db):
        if self.get_time_type() != db.get_time_type():
            raise Exception("Import failed: time type does not match")
        with self.transaction("Import events"):
            for event in db.get_all_events():
                self._import_item(event)

    def _import_item(self, item):
        if item.is_subevent():
            # Sub events are handled when importing the container
            return
        new_item = item.duplicate(target_db=self)
        new_item.category = self._import_category(item.category)
        new_item.save()
        if item.is_container():
            for subevent in item.subevents:
                new_sub = subevent.duplicate(target_db=self)
                new_sub.category = self._import_category(subevent.category)
                new_sub.container = new_item
                new_sub.save()

    def _import_category(self, category):
        if category is None:
            return None
        elif self._has_category_with_name(category.get_name()):
            return self.get_category_by_name(category.get_name())
        else:
            new_cat = category.duplicate(target_db=self)
            new_cat.parent = self._import_category(category.parent)
            new_cat.save()
            return new_cat

    def _has_category_with_name(self, name):
        for category in self.get_categories():
            if category.get_name() == name:
                return True
        return False

    def compress(self):
        with self.transaction("Compress events"):
            self._set_events_order_from_rows(self._place_events_on_rows())

    def _set_events_order_from_rows(self, rows):
        event_sorter = EventSorter()
        for key in sorted(rows.keys()):
            event_sorter.save_sort_order(rows[key])

    def _place_events_on_rows(self):
        rows = collections.defaultdict(lambda: [])
        for event in self._length_sort():
            inx = 0
            while True:
                if self._fits_on_row(rows[inx], event):
                    event.r = inx
                    rows[inx].append(event)
                    break
                inx += 1
        return rows

    def _length_sort(self):
        all_events = self.get_all_events()
        reordered_events = [
            event
            for event
            in all_events
            if not event.is_subevent() and not event.is_milestone()
        ]
        reordered_events = self._sort_by_length(reordered_events)
        return reordered_events

    def _sort_by_length(self, events):
        return sorted(events, key=self._event_length, reverse=True)

    def _event_length(self, evt):
        return evt.get_time_period().delta()

    def _fits_on_row(self, row_events, event):
        for ev in row_events:
            if ev.overlaps(event):
                return False
        return True

    @contextlib.contextmanager
    def _query(self):
        need_to_create_query = self._current_query is None
        if need_to_create_query:
            self._current_query = Query(self, self._transactions.value)
        try:
            yield self._current_query
        finally:
            if need_to_create_query:
                self._current_query = None


class Query(object):

    def __init__(self, db, immutable_db):
        self._db = db
        self._immutable_db = immutable_db
        self._wrappers = {}

    def container_exists(self, id_):
        return id_ in self._immutable_db.containers

    def event_exists(self, id_):
        return id_ in self._immutable_db.events

    def milestone_exists(self, id_):
        return id_ in self._immutable_db.milestones

    def get_category(self, id_):
        if id_ not in self._wrappers:
            self._wrappers[id_] = self._create_category_wrapper(id_)
        return self._wrappers[id_]

    def get_container(self, id_):
        if id_ not in self._wrappers:
            self._wrappers[id_] = self._create_container_wrapper(id_)
            self._load_subevents(self._wrappers[id_])
        return self._wrappers[id_]

    def get_event(self, id_):
        if id_ not in self._wrappers:
            self._wrappers[id_] = self._create_event_wrapper(id_)
            immutable_event = self._immutable_db.events.get(id_)
            if immutable_event.container_id is not None:
                # Loading the container will load and populate all subevents
                self.get_container(immutable_event.container_id)
        return self._wrappers[id_]

    def get_milestone(self, id_):
        if id_ not in self._wrappers:
            self._wrappers[id_] = self._create_milestone_wrapper(id_)
        return self._wrappers[id_]

    def get_era(self, id_):
        if id_ not in self._wrappers:
            self._wrappers[id_] = self._create_era_wrapper(id_)
        return self._wrappers[id_]

    def _load_subevents(self, container):
        for subevent_id, immutable_event in self._immutable_db.events:
            if immutable_event.container_id == container.id:
                self.get_event(subevent_id).container = container

    def _create_category_wrapper(self, id_):
        immutable_category = self._immutable_db.categories.get(id_)
        wrapper = Category(
            db=self._db,
            id_=id_,
            immutable_value=immutable_category,
        )
        wrapper.parent = self._get_maybe_category(immutable_category.parent_id)
        return wrapper

    def _create_container_wrapper(self, id_):
        immutable_container = self._immutable_db.containers.get(id_)
        wrapper = Container(
            db=self._db,
            id_=id_,
            immutable_value=immutable_container,
        )
        wrapper.category = self._get_maybe_category(immutable_container.category_id)
        lst = []
        for key in immutable_container.category_ids:
            lst.append(self._get_maybe_category(key))
        wrapper.set_categories(lst)
        return wrapper

    def _create_event_wrapper(self, id_):
        immutable_event = self._immutable_db.events.get(id_)
        if immutable_event.container_id is None:
            klass = Event
        else:
            klass = Subevent
        wrapper = klass(
            db=self._db,
            id_=id_,
            immutable_value=immutable_event,
        )
        wrapper.category = self._get_maybe_category(immutable_event.category_id)
        lst = []
        for key in immutable_event.category_ids:
            lst.append(self._get_maybe_category(key))
        wrapper.set_categories(lst)
        return wrapper

    def _create_milestone_wrapper(self, id_):
        immutable_milestone = self._immutable_db.milestones.get(id_)
        wrapper = Milestone(
            db=self._db,
            id_=id_,
            immutable_value=immutable_milestone,
        )
        wrapper.category = self._get_maybe_category(immutable_milestone.category_id)
        lst = []
        for key in immutable_milestone.category_ids:
            lst.append(self._get_maybe_category(key))
        wrapper.set_categories(lst)
        return wrapper

    def _create_era_wrapper(self, id_):
        immutable_era = self._immutable_db.eras.get(id_)
        return Era(
            db=self._db,
            id_=id_,
            immutable_value=immutable_era,
        )

    def _get_maybe_category(self, category_id):
        if category_id is None:
            return None
        else:
            return self.get_category(category_id)


class EventSorter(object):

    def __init__(self):
        self._sort_order = 0

    def save_sort_order(self, events):
        for event in events:
            if event.is_container():
                self.save_sort_order(event.subevents)
            else:
                if event.sort_order != self._sort_order:
                    event.sort_order = self._sort_order
                    event.save()
                self._sort_order += 1


def sort_events(events):
    return sorted(events, key=lambda event: event.sort_order)


def _generic_event_search(events, search_string):
    def match(event):
        target = search_string.lower()
        description = event.get_data("description")
        if description is None:
            description = ""
        else:
            description = description.lower()
        return target in event.get_text().lower() or target in description
    def mean_time(event):
        return event.mean_time()
    matches = [event for event in events if match(event)]
    matches.sort(key=mean_time)
    return matches
