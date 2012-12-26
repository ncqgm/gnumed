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


from timelinelib.repositories.interface import CategoryRepository
from timelinelib.repositories.interface import EventRepository
from timelinelib.wxgui.utils import category_tree


class DbWrapperCategoryRepository(CategoryRepository):

    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.get_categories()

    def get_tree(self, remove):
        return category_tree(self.get_all(), remove=remove)

    def save(self, category):
        self.db.save_category(category)


class DbWrapperEventRepository(EventRepository):

    def __init__(self, db):
        self.db = db

    def save(self, event):
        self.db.save_event(event)
