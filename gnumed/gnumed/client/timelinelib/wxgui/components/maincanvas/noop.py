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


from timelinelib.wxgui.components.maincanvas.inputhandler import InputHandler
from timelinelib.general.methodcontainer import MethodContainer
from timelinelib.wxgui.keyboard import Keyboard


"""
A NoOpInputHandler gets messages about the start of a user input, such as a
mouse move action, and delegates the workload to fulfill the user action, to
another event handler
"""


class NoOpInputHandler(InputHandler):

    def __init__(self, state, timeline_canvas):
        InputHandler.__init__(self, timeline_canvas)
        self._state = state

    def left_mouse_down(self, cursor, keyboard):

        def toggle_balloon_stickyness():
            event_with_balloon = self._canvas.GetBalloonAt(cursor)
            if event_with_balloon:
                self._canvas.toggle_balloon_stickyness(event_with_balloon)

        def event_at_cursor():
            return self._canvas.GetEventAt(cursor, keyboard.alt)

        toggle_balloon_stickyness()
        event = event_at_cursor()
        if event:
            self._left_mouse_down_on_event(self._state, event, cursor, keyboard)
        else:
            self._left_mouse_down_on_timeline(self._state, cursor, keyboard)

    def _left_mouse_down_on_event(self, state, event, cursor, keyboard):

        def hit_resize_handle():
            return self._canvas.hit_resize_handle(cursor, keyboard)

        def is_resize_command():
            return hit_resize_handle() is not None

        def hit_move_handle():
            return self._canvas.hit_move_handle(cursor, keyboard)

        def is_move_command():
            if event.get_ends_today():
                return False
            else:
                return hit_move_handle()

        def start_event_action(action_method, action_arg):
            if state.ok_to_edit():
                try:
                    action_method(event, action_arg)
                except:
                    state.edit_ends()
                    raise

        def resize_event():
            start_event_action(state.change_to_resize_by_drag, hit_resize_handle())

        def move_event():
            start_event_action(state.change_to_move_by_drag, self._canvas.GetTimeAt(cursor.x))

        def toggle_event_selection():
            self._canvas.toggle_event_selection(cursor, keyboard)

        methods = MethodContainer(
            [
                (is_resize_command(), resize_event),
                (is_move_command(), move_event)
            ],
            default_method=toggle_event_selection)
        methods.select(True)()

    def _left_mouse_down_on_timeline(self, state, cursor, keyboard):

        def scroll():
            state.change_to_scroll_by_drag(cursor)

        def create_event():
            self._canvas.ClearSelectedEvents()
            state.change_to_create_period_event_by_drag(cursor)

        def zoom():
            self._canvas.ClearSelectedEvents()
            state.change_to_zoom_by_drag(cursor)

        def select():
            state.change_to_select(cursor)

        methods = MethodContainer(
            [
                (Keyboard.NONE, scroll),
                (Keyboard.SHIFT, zoom),
                (Keyboard.CTRL, create_event),
                (Keyboard.SHIFT | Keyboard.CTRL, select),
            ])
        methods.select(keyboard.keys_combination)()
