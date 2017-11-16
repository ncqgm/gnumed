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


import urllib

from timelinelib.wxgui.framework import Controller


class FeedbackDialogController(Controller):

    def on_init(self, webbrowser, info, subject, body):
        self.webbrowser = webbrowser
        self.view.SetInfoText(info)
        self.view.SetToText("thetimelineproj-user@lists.sourceforge.net")
        self.view.SetSubjectText(subject)
        self.view.SetBodyText(body)

    def on_default_click(self, event):
        attr = self._get_url_attributes()
        url = "mailto:%s?subject=%s&body=%s" % (
            urllib.quote(attr["to"]),
            urllib.quote(attr["subject"]),
            urllib.quote(attr["body"]),
        )
        self.webbrowser.open(url)

    def on_gmail_click(self, event):
        attr = self._get_url_attributes()
        url = "https://mail.google.com/mail/?compose=1&view=cm&fs=1&to=%s&su=%s&body=%s" % (
            urllib.quote(attr["to"]),
            urllib.quote(attr["subject"]),
            urllib.quote(attr["body"]),
        )
        self.webbrowser.open(url)

    def on_other_click(self, event):
        self.view.DisplayInformationMessage(
            caption=_("Other email client"),
            message=_("Copy and paste this email into your favorite email client and send it from there."))

    def _get_url_attributes(self):
        return {
            "to": self.view.GetToText().encode("utf-8"),
            "subject": self.view.GetSubjectText().encode("utf-8"),
            "body": self.view.GetBodyText().encode("utf-8"),
        }
