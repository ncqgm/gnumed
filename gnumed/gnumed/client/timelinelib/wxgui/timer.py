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

from timelinelib.utilities.observer import Observable
from timelinelib.utilities.observer import TIMER_TICK


class TimelineTimer(Observable):

    def __init__(self, parent):
        Observable.__init__(self)
        self.timer = wx.Timer(parent)
        parent.Bind(wx.EVT_TIMER, self._timer_tick, self.timer)

    def start(self, interval_in_ms):
        self.timer.Start(interval_in_ms)
        
    def _timer_tick(self, evt):
        self._notify(TIMER_TICK)
