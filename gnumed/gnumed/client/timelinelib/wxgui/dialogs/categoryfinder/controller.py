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
from timelinelib.proxies.sidebar import SidebarProxy


class CategoryFinderDialogController(Controller):

    def on_init(self, db, mainframe):
        self.db = db
        self.mainframe = mainframe
        self.view.SetCategories(self._get_categories_names())
        self.set_sidebar_proxy(SidebarProxy(self.mainframe))

    def set_sidebar_proxy(self, sidebar_proxy):
        self.sidebar_proxy = sidebar_proxy

    def on_char(self, evt):
        self.view.SetCategories(self._get_categories_names())

    def on_check(self, evt):
        self.sidebar_proxy.check_categories(self._get_categories())

    def on_uncheck(self, evt):
        self.sidebar_proxy.uncheck_categories(self._get_categories())

    def _get_categories_names(self):
        return sorted([category.name for category in self._get_categories()])

    def _get_categories(self):
        target = self.view.GetTarget()
        return [category for category in self.db.get_categories()
                if category.name.upper().startswith(target.upper())]
