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


from sys import version as python_version
import platform
import sys
import traceback

import wx

from timelinelib.meta.version import get_version
from timelinelib.wxgui.dialogs.mainframe import MainFrame
from timelinelib.wxgui.dialogs.feedback import show_feedback_dialog


def start_wx_application(application_arguments, before_main_loop_hook=None):
    app = wx.App(False)
    main_frame = MainFrame(application_arguments)
    main_frame.Show()
    sys.excepthook = unhandled_exception_hook
    if before_main_loop_hook:
        before_main_loop_hook()
    app.MainLoop()


def unhandled_exception_hook(type, value, tb):
    show_feedback_dialog(
        parent=None,
        info=create_info_message(),
        subject=create_subject(type, value),
        body=create_error_message(type, value, tb))


def create_info_message():
    return ("An unexpected error has occurred. Help us fix it by reporting "
            "the error through this form. "
            "It would also be useful to describe what you did just "
            "before the error occurred.")


def create_subject(type, value):
    exception_message = "".join(traceback.format_exception_only(type, value)).strip()
    return "Crash report: %s" % exception_message


def create_error_message(type, value, tb):
    stacktrace = ("".join(traceback.format_exception(type, value, tb))).strip()
    versions = create_versions_message()
    return "Describe what you did here...\n\n%s\n\n%s" % (stacktrace, versions)


def create_versions_message():
    return "\n".join([
        "Timeline version: %s" % get_version(),
        "System version: %s" % ", ".join(platform.uname()),
        "Python version: %s" % python_version.replace("\n", ""),
        "wxPython version: %s" % wx.version(),
    ])
