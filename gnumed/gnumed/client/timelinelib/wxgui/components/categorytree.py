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


import wx

from timelinelib.db.utils import safe_locking
from timelinelib.drawing.utils import darken_color
from timelinelib.drawing.utils import get_default_font
from timelinelib.monitoring import monitoring
from timelinelib.repositories.categories import CategoriesFacade
from timelinelib.utilities.observer import Observable
from timelinelib.wxgui.components.cattree import add_category
from timelinelib.wxgui.components.cattree import delete_category
from timelinelib.wxgui.components.cattree import edit_category


class CustomCategoryTree(wx.ScrolledWindow):

    def __init__(self, parent, handle_db_error):
        wx.ScrolledWindow.__init__(self, parent)
        self.parent = parent
        self.handle_db_error = handle_db_error
        self._create_context_menu()
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
        self.model = CustomCategoryTreeModel()
        self.model.listen_for_any(self._redraw)
        self.renderer = CustomCategoryTreeRenderer(self, self.model)
        self.set_no_timeline_view()
        self._size_to_model()
        self._draw_bitmap()

    def set_no_timeline_view(self):
        self.db = None
        self.view_properties = None
        self.model.set_categories(None)

    def set_timeline_view(self, db, view_properties):
        self.db = db
        self.view_properties = view_properties
        self.model.set_categories(CategoriesFacade(db, view_properties))

    def check_categories(self, categories):
        self.view_properties.set_categories_visible(categories)

    def uncheck_categories(self, categories):
        self.view_properties.set_categories_visible(categories, False)

    def _has_timeline_view(self):
        return self.db is not None and self.view_properties is not None

    def _on_paint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer_image, wx.BUFFER_VIRTUAL_AREA)

    def _on_size(self, event):
        self._size_to_model()

    def _on_left_down(self, event):
        self.SetFocus()
        self._store_hit_info(event)
        hit_category = self.last_hit_info.get_category()
        if self.last_hit_info.is_on_arrow():
            self.model.toggle_expandedness(hit_category)
        elif self.last_hit_info.is_on_checkbox():
            self.view_properties.toggle_category_visibility(hit_category)

    def _on_right_down(self, event):
        def edit_function():
            self._store_hit_info(event)
            for (menu_item, should_be_enabled_fn) in self.context_menu_items:
                menu_item.Enable(should_be_enabled_fn(self.last_hit_info))
            self.PopupMenu(self.context_menu)
        safe_locking(self.parent, edit_function)

    def _on_menu_edit(self, e):
        hit_category = self.last_hit_info.get_category()
        if hit_category:
            edit_category(self, self.db, hit_category, self.handle_db_error)

    def _on_menu_add(self, e):
        add_category(self, self.db, self.handle_db_error)

    def _on_menu_delete(self, e):
        hit_category = self.last_hit_info.get_category()
        if hit_category:
            delete_category(self, self.db, hit_category, self.handle_db_error)

    def _on_menu_check_all(self, e):
        self.view_properties.set_categories_visible(
            self.db.get_categories())

    def _on_menu_check_children(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_immediate_children())

    def _on_menu_check_all_children(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_all_children())

    def _on_menu_check_parents(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_parents())

    def _on_menu_check_parents_for_checked_children(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_parents_for_checked_childs())

    def _on_menu_uncheck_all(self, e):
        self.view_properties.set_categories_visible(
            self.db.get_categories(), False)

    def _on_menu_uncheck_children(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_immediate_children(), False)

    def _on_menu_uncheck_all_children(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_all_children(), False)

    def _on_menu_uncheck_parents(self, e):
        self.view_properties.set_categories_visible(
            self.last_hit_info.get_parents(), False)

    def _store_hit_info(self, event):
        (x, y) = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        self.last_hit_info = self.model.hit(x, y)

    def _redraw(self):
        self.SetVirtualSize((-1, self.model.ITEM_HEIGHT_PX * len(self.model.items)))
        self.SetScrollRate(0, self.model.ITEM_HEIGHT_PX/2)
        self._draw_bitmap()
        self.Refresh()
        self.Update()

    def _draw_bitmap(self):
        width, height = self.GetVirtualSizeTuple()
        self.buffer_image = wx.EmptyBitmap(width, height)
        memdc = wx.BufferedDC(None, self.buffer_image)
        memdc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        memdc.Clear()
        memdc.BeginDrawing()
        monitoring.timer_start()
        self.renderer.render(memdc)
        monitoring.timer_end()
        if monitoring.IS_ENABLED:
            (width, height) = self.GetSizeTuple()
            redraw_time = monitoring.timer_elapsed_ms()
            monitoring.count_category_redraw()
            memdc.SetTextForeground((255, 0, 0))
            memdc.SetFont(get_default_font(10, bold=True))
            memdc.DrawText("Redraw count: %d" % monitoring.category_redraw_count, 10, height - 35)
            memdc.DrawText("Last redraw time: %.3f ms" % redraw_time, 10, height - 20)
        memdc.EndDrawing()
        del memdc

    def _size_to_model(self):
        (view_width, view_height) = self.GetVirtualSizeTuple()
        self.model.set_view_size(view_width, view_height)

    def _create_context_menu(self):
        def add_item(name, callback, should_be_enabled_fn):
            item = wx.MenuItem(self.context_menu, wx.ID_ANY, name)
            self.context_menu.AppendItem(item)
            self.Bind(wx.EVT_MENU, callback, item)
            self.context_menu_items.append((item, should_be_enabled_fn))
            return item
        self.context_menu_items = []
        self.context_menu = wx.Menu()
        add_item(
            _("Edit..."),
            self._on_menu_edit,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Add..."),
            self._on_menu_add,
            lambda hit_info: self._has_timeline_view())
        add_item(
            _("Delete"),
            self._on_menu_delete,
            lambda hit_info: hit_info.has_category())
        self.context_menu.AppendSeparator()
        add_item(
            _("Check All"),
            self._on_menu_check_all,
            lambda hit_info: self._has_timeline_view())
        add_item(
            _("Check children"),
            self._on_menu_check_children,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Check all children"),
            self._on_menu_check_all_children,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Check all parents"),
            self._on_menu_check_parents,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Check parents for checked children"),
            self._on_menu_check_parents_for_checked_children,
            lambda hit_info: self._has_timeline_view())
        self.context_menu.AppendSeparator()
        add_item(
            _("Uncheck All"),
            self._on_menu_uncheck_all,
            lambda hit_info: self._has_timeline_view())
        add_item(
            _("Uncheck children"),
            self._on_menu_uncheck_children,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Uncheck all children"),
            self._on_menu_uncheck_all_children,
            lambda hit_info: hit_info.has_category())
        add_item(
            _("Uncheck all parents"),
            self._on_menu_uncheck_parents,
            lambda hit_info: hit_info.has_category())


class CustomCategoryTreeRenderer(object):

    INNER_PADDING = 2
    TRIANGLE_SIZE = 8

    def __init__(self, window, model):
        self.window = window
        self.model = model

    def render(self, dc):
        self.dc = dc
        self._render_items(self.model.items)
        del self.dc

    def _render_items(self, items):
        self.dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
        for item in items:
            self._render_item(item)

    def _render_item(self, item):
        if item["has_children"]:
            self._render_arrow(item)
        self._render_checkbox(item)
        self._render_name(item)
        self._render_color_box(item)

    def _render_arrow(self, item):
        self.dc.SetBrush(wx.Brush(wx.Color(100, 100, 100), wx.SOLID))
        self.dc.SetPen(wx.Pen(wx.Color(100, 100, 100), 0, wx.SOLID))
        offset = self.TRIANGLE_SIZE/2
        center_x = item["x"] + 2*self.INNER_PADDING + offset
        center_y = item["y"] + self.model.ITEM_HEIGHT_PX/2 - 1
        if item["expanded"]:
            open_polygon = [
                wx.Point(center_x - offset, center_y - offset),
                wx.Point(center_x + offset, center_y - offset),
                wx.Point(center_x         , center_y + offset),
            ]
            self.dc.DrawPolygon(open_polygon)
        else:
            closed_polygon = [
                wx.Point(center_x - offset, center_y - offset),
                wx.Point(center_x - offset, center_y + offset),
                wx.Point(center_x + offset, center_y),
            ]
            self.dc.DrawPolygon(closed_polygon)

    def _render_name(self, item):
        x = item["x"] + self.TRIANGLE_SIZE + 4 * self.INNER_PADDING + 20
        (w, h) = self.dc.GetTextExtent(item["name"])
        if item["actually_visible"]:
            self.dc.SetTextForeground(self.window.GetForegroundColour())
        else:
            self.dc.SetTextForeground((150, 150, 150))
        self.dc.DrawText(item["name"],
                         x + self.INNER_PADDING,
                         item["y"] + (self.model.ITEM_HEIGHT_PX - h)/2)

    def _render_checkbox(self, item):
        (w, h) = (17, 17)
        bouning_rect = wx.Rect(item["x"] + self.model.INDENT_PX,
                               item["y"] + (self.model.ITEM_HEIGHT_PX - h)/2,
                               w,
                               h)
        if item["visible"]:
            flag = wx.CONTROL_CHECKED
        else:
            flag = 0
        renderer = wx.RendererNative.Get()
        renderer.DrawCheckBox(self.window, self.dc, bouning_rect, flag)

    def _render_color_box(self, item):
        color = item.get("color", None)
        self.dc.SetBrush(wx.Brush(color, wx.SOLID))
        self.dc.SetPen(wx.Pen(darken_color(color), 1, wx.SOLID))
        (w, h) = (16, 16)
        self.dc.DrawRectangle(
            item["x"] + item["width"] - w - self.INNER_PADDING,
            item["y"] + self.model.ITEM_HEIGHT_PX/2 - h/2,
            w,
            h)


class CustomCategoryTreeModel(Observable):

    ITEM_HEIGHT_PX = 22
    INDENT_PX = 15

    def __init__(self):
        Observable.__init__(self)
        self.view_width = 0
        self.view_height = 0
        self.categories = None
        self.collapsed_category_ids = []
        self.items = []

    def get_items(self):
        return self.items

    def set_view_size(self, view_width, view_height):
        self.view_width = view_width
        self.view_height = view_height
        self._update_items()

    def set_categories(self, categories):
        if self.categories:
            self.categories.unlisten(self._update_items)
        self.categories = categories
        if self.categories:
            self.categories.listen_for_any(self._update_items)
        self._update_items()

    def hit(self, x, y):
        item = self._item_at(y)
        if item:
            return HitInfo(self.categories,
                           item["category"],
                           self._hits_arrow(x, item),
                           self._hits_checkbox(x, item))
        else:
            return HitInfo(self.categories, None, False, False)

    def toggle_expandedness(self, category):
        if category.id in self.collapsed_category_ids:
            self.collapsed_category_ids.remove(category.id)
            self._update_items()
        else:
            self.collapsed_category_ids.append(category.id)
            self._update_items()

    def _item_at(self, y):
        index = y // self.ITEM_HEIGHT_PX
        if index < len(self.items):
            return self.items[index]
        else:
            return None

    def _hits_arrow(self, x, item):
        return (x > item["x"] and
                x < (item["x"] + self.INDENT_PX))

    def _hits_checkbox(self, x, item):
        return (x > (item["x"] + self.INDENT_PX) and
                x < (item["x"] + 2*self.INDENT_PX))

    def _update_items(self):
        self.items = []
        self.y = 0
        self._update_from_tree(self._list_to_tree(self._get_categories()))
        self._notify(None)

    def _get_categories(self):
        if self.categories is None:
            return []
        else:
            return self.categories.get_all()

    def _list_to_tree(self, categories, parent=None):
        top = [category for category in categories if (category.parent == parent)]
        sorted_top = sorted(top, key=lambda category: category.name)
        return [(category, self._list_to_tree(categories, category)) for
                category in sorted_top]

    def _update_from_tree(self, category_tree, indent_level=0):
        for (category, child_tree) in category_tree:
            expanded = category.id not in self.collapsed_category_ids
            self.items.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "visible": self._is_category_visible(category),
                "x": indent_level * self.INDENT_PX,
                "y": self.y,
                "width": self.view_width - indent_level * self.INDENT_PX,
                "expanded": expanded,
                "has_children": len(child_tree) > 0,
                "actually_visible": self._is_event_with_category_visible(category),
                "category": category,
            })
            self.y += self.ITEM_HEIGHT_PX
            if expanded:
                self._update_from_tree(child_tree, indent_level+1)

    def _is_category_visible(self, category):
        return self.categories.is_visible(category)

    def _is_event_with_category_visible(self, category):
        return self.categories.is_event_with_category_visible(category)


class HitInfo(object):

    def __init__(self, categories, category, is_on_arrow, is_on_checkbox):
        self._categories = categories
        self._category = category
        self._is_on_arrow = is_on_arrow
        self._is_on_checkbox = is_on_checkbox

    def has_category(self):
        return self._category is not None

    def get_category(self):
        return self._category

    def get_immediate_children(self):
        return self._categories.get_immediate_children(self._category)

    def get_all_children(self):
        return self._categories.get_all_children(self._category)

    def get_parents(self):
        return self._categories.get_parents(self._category)

    def get_parents_for_checked_childs(self):
        return self._categories.get_parents_for_checked_childs()
        
    def is_on_arrow(self):
        return self._is_on_arrow

    def is_on_checkbox(self):
        return self._is_on_checkbox
