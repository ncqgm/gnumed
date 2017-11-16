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


import wx

from timelinelib.wxgui.dialogs.feature.controller import FeatureDialogController
from timelinelib.wxgui.framework import Dialog


class FeatureDialog(Dialog):

    """
    <BoxSizerVertical>

        <StaticText name="feature_name" label="" width="600" border="ALL" />

        <TextCtrl name="feature_description" height="200"
            style="TE_MULTILINE|TE_READONLY|TE_RICH|TE_AUTO_URL" border="LEFT|RIGHT|BOTTOM"
            event_EVT_TEXT_URL="on_text_url"
        />

        <BoxSizerHorizontal>
            <Button label="$(give_feedback_button_text)" event_EVT_BUTTON="on_give_feedback" border="BOTTOM|LEFT" />
            <StretchSpacer />
            <DialogButtonsCloseSizer border="BOTTOM|RIGHT"/>
        </BoxSizerHorizontal>

    </BoxSizerVertical>
    """

    def __init__(self, parent, feature):
        Dialog.__init__(self, FeatureDialogController, parent, {
            "give_feedback_button_text": _("Give Feedback")
        }, title=_("Feedback On Feature"))
        self._make_info_label_bold()
        self.controller.on_init(feature)

    def SetFeatureName(self, name):
        self.feature_name.SetLabel(name)

    def SetFeatureDescription(self, description):
        self.feature_description.SetValue(description)

    def GetDescription(self):
        return self.feature_description.GetValue()

    def _make_info_label_bold(self):
        font = self.feature_name.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.feature_name.SetFont(font)


def show_feature_feedback_dialog(feature, parent=None):
    dialog = FeatureDialog(parent, feature)
    dialog.ShowModal()
    dialog.Destroy()
