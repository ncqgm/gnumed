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


import webbrowser

from timelinelib.wxgui.dialogs.feedback.view import show_feedback_dialog
from timelinelib.wxgui.framework import Controller


class FeatureDialogController(Controller):

    def on_init(self, feature):
        self.feature = feature
        self.view.SetFeatureName(feature.get_display_name())
        self.view.SetFeatureDescription(feature.get_description())

    def on_give_feedback(self, evt):
        show_feedback_dialog("", self.feature.get_display_name(), "")

    def on_text_url(self, evt):
        if evt.MouseEvent.LeftUp():
            webbrowser.open(self._get_url(evt))
        evt.Skip()

    def _get_url(self, evt):
        start = evt.GetURLStart()
        end = evt.GetURLEnd()
        return self.view.GetDescription()[start:end]
