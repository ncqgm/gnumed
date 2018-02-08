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

import wx

from timelinelib.wxgui.dialogs.feedback.controller import FeedbackDialogController
from timelinelib.wxgui.framework import Dialog


class FeedbackDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticText name="info" border="LEFT|TOP|RIGHT" />
        <FlexGridSizer columns="2" growableColumns="1" growableRows="2" proportion="1" border="ALL">
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(to_text)" />
            <TextCtrl name="to_text" style="TE_READONLY" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(subject_text)" />
            <TextCtrl name="subject_text" />
            <StaticText align="ALIGN_TOP" label="$(body_text)" />
            <TextCtrlSelect name="body_text" height="200" style="TE_MULTILINE" />
            <StaticText align="ALIGN_CENTER_VERTICAL" label="$(send_with_text)" />
            <BoxSizerHorizontal>
                <Button label="$(default_button_text)" borderType="SMALL" border="RIGHT" event_EVT_BUTTON="on_default_click" />
                <Button label="$(gmail_button_text)" borderType="SMALL" border="RIGHT" event_EVT_BUTTON="on_gmail_click" />
                <Button label="$(other_button_text)" border="RIGHT" event_EVT_BUTTON="on_other_click" />
                <StretchSpacer />
                <DialogButtonsCloseSizer />
            </BoxSizerHorizontal>
        </FlexGridSizer>
    </BoxSizerVertical>
    """

    def __init__(self, parent, info, subject, body):
        Dialog.__init__(self, FeedbackDialogController, parent, {
            "title_text": _("Email Feedback"),
            "to_text": _("To:"),
            "subject_text": _("Subject:"),
            "body_text": _("Body:"),
            "send_with_text": _("Send With:"),
            "default_button_text": _("Default client"),
            "gmail_button_text": _("Gmail"),
            "other_button_text": _("Other"),
        }, title=_("Email Feedback"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init(webbrowser, info, subject, body)
        self.body_text.SetFocus()

    def SetInfoText(self, text):
        self.info.SetLabel(text)
        self.SetSizerAndFit(self.GetSizer())

    def GetToText(self):
        return self.to_text.GetValue()

    def SetToText(self, text):
        self.to_text.SetValue(text)

    def GetSubjectText(self):
        return self.subject_text.GetValue()

    def SetSubjectText(self, text):
        self.subject_text.SetValue(text)

    def GetBodyText(self):
        return self.body_text.GetValue()

    def SetBodyText(self, text):
        self.body_text.SetValue(text)

    def SelectAllBodyText(self):
        self.body_text.SelectAll()


def show_feedback_dialog(info, subject, body, parent=None):
    dialog = FeedbackDialog(parent, info, subject, body)
    dialog.ShowModal()
    dialog.Destroy()
