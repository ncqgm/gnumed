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


from timelinelib.wxgui.dialogs.setcategory.controller import SetCategoryDialogController
from timelinelib.wxgui.framework import Dialog


class SetCategoryDialog(Dialog):

    """
    <BoxSizerVertical>
        <FlexGridSizer columns="2" growableColumns="1" proportion="1" border="ALL">
            <StaticText
                label="$(label)"
                align="ALIGN_CENTER_VERTICAL"
            />
            <CategoryChoice
                name="category_choice"
                timeline="$(db)"
                align="ALIGN_CENTER_VERTICAL"
            />
        </FlexGridSizer>
        <DialogButtonsOkCancelSizer
            border="LEFT|BOTTOM|RIGHT"
            event_EVT_BUTTON__ID_OK="on_ok_clicked"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent, db, selected_event_ids=[]):
        Dialog.__init__(self, SetCategoryDialogController, parent, {
            "db": db,
            "label": _("Select a Category:"),
        })
        self.controller.on_init(db, selected_event_ids)

    def PopulateCategories(self):
        self.category_choice.Populate()
        self.Fit()

    def GetSelectedCategory(self):
        return self.category_choice.GetSelectedCategory()
