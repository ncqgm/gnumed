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


import urllib


DESCRIBE_TEXT = "Describe what you did here..."


class FeedbackForm(object):

    def __init__(self, dialog, webbrowser):
        self.dialog = dialog
        self.webbrowser = webbrowser

    def populate(self, info, subject, body):
        self.dialog.set_info_text(info)
        self.dialog.set_to_text("thetimelineproj-user@lists.sourceforge.net")
        self.dialog.set_subject_text(subject)
        self.dialog.set_body_text(body)
        if body.startswith(DESCRIBE_TEXT):
            self.dialog.set_body_selection(0, len(DESCRIBE_TEXT))

    def send_with_default(self):
        self.webbrowser.open("mailto:%s?subject=%s&body=%s" % (
            urllib.quote(self.dialog.get_to_text()),
            urllib.quote(self.dialog.get_subject_text()),
            urllib.quote(self.dialog.get_body_text())))

    def send_with_gmail(self):
        self.webbrowser.open("https://mail.google.com/mail/?compose=1&view=cm&fs=1&to=%s&su=%s&body=%s" % (
            urllib.quote(self.dialog.get_to_text()),
            urllib.quote(self.dialog.get_subject_text()),
            urllib.quote(self.dialog.get_body_text())))
