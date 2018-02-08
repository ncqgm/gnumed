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


from timelinelib.wxgui.dialogs.importevents.controller import ImportEventsDialogController
from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.utils import WildcardHelper


class ImportEventsDialog(Dialog):

    """
    <BoxSizerVertical>
        <Header label="$(header_label)"
            border="ALL"
        />
        <FileChooser
            name="file_chooser"
            dialog_wildcard="$(dialog_wildcard)"
            event_EVT_FILE_PATH_CHANGED="on_file_path_changed"
            border="LEFT|RIGHT"
        />
        <FeedbackText
            name="feedback_text"
            width="300"
            height="70"
            border="ALL"
            proportion="1"
        />
        <DialogButtonsOkCancelSizer
            border="LEFT|BOTTOM|RIGHT"
            event_EVT_BUTTON__ID_OK="on_ok_clicked"
        />
    </BoxSizerVertical>
    """

    def __init__(self, db, parent=None):
        Dialog.__init__(self, ImportEventsDialogController, parent, {
            "header_label": _("Select timeline to import from:"),
            "dialog_wildcard": WildcardHelper(_("Timeline files"), ["timeline", "ics"]).wildcard_string(),
        }, title=_("Import events"))
        self.controller.on_init(db)

    def GetFilePath(self):
        return self.file_chooser.GetFilePath()

    def SetSuccess(self, text):
        self.feedback_text.SetSuccess(text)
        self.GetSizer().Layout()

    def SetError(self, text):
        self.feedback_text.SetError(text)
        self.GetSizer().Layout()
