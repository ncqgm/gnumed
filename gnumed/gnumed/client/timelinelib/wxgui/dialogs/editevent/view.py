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

from timelinelib.db.utils import safe_locking
from timelinelib.repositories.dbwrapper import DbWrapperEventRepository
from timelinelib.wxgui.dialogs.editcontainer.view import EditContainerDialog
from timelinelib.wxgui.dialogs.editevent.controller import EditEventDialogController
from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.utils import _set_focus_and_select
from timelinelib.wxgui.dialogs.duplicateevent.view import DuplicateEventDialog


class EditEventDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticBoxSizerVertical label="$(properties_label)" border="ALL" proportion="1">
            <FlexGridSizer name="grid_sizer" columns="2" growableColumns="1" border="ALL" proportion="1">
                %s
            </FlexGridSizer>
        </StaticBoxSizerVertical>
        <CheckBox
            name="add_more_checkbox"
            label="$(add_more_label)"
            border="LEFT|RIGHT|BOTTOM"
        />
        <BoxSizerHorizontal border="LEFT|RIGHT|BOTTOM">
            <TwoStateButton
                initial_state_label="$(enlarge)"
                second_state_label="$(reduce)"
                event_EVT_INITIAL_STATE_CLICKED="on_enlarge_click"
                event_EVT_SECOND_STATE_CLICKED="on_reduce_click"
            />
            <Spacer />
            <Button
                name="duplicate"
                label="$(duplicate_label)"
                event_EVT_BUTTON="on_duplicate"
            />
            <StretchSpacer />
            <DialogButtonsOkCancelSizer
                event_EVT_BUTTON__ID_OK="on_ok_clicked"
            />
        </BoxSizerHorizontal>
    </BoxSizerVertical>
    """

    TIME_DETAILS_ROW = """
        <StaticText align="ALIGN_CENTER_VERTICAL" label="$(when_label)" />
        <BoxSizerHorizontal>
            <PeriodPicker
                name="period_picker"
                time_type="$(time_type)"
                config="$(config)"
            />
        </BoxSizerHorizontal>
    """

    CHECKBOX_ROW = """
        <Spacer />
        <FlexGridSizer rows="1">
            <CheckBox
                name="fuzzy_checkbox"
                label="$(fuzzy_checkbox_text)"
            />
            <CheckBox
                name="locked_checkbox"
                event_EVT_CHECKBOX="on_locked_checkbox_changed"
                label="$(locked_checkbox_text)"
            />
            <CheckBox
                name="ends_today_checkbox"
                label="$(ends_today_checkbox_text)"
            />
        </FlexGridSizer>
    """

    TEXT_FIELD_ROW = """
        <StaticText align="ALIGN_CENTER_VERTICAL" label="$(text_label)" />
        <TextCtrl name="name" />
    """

    CATEGORY_LISTBOX_ROW = """
        <StaticText align="ALIGN_CENTER_VERTICAL" label="$(category_label)" />
        <CategoryChoice
            name="category_choice"
            allow_add="True"
            allow_edit="True"
            timeline="$(db)"
            align="ALIGN_LEFT"
        />
    """

    CONTAINER_LISTBOX_ROW = """
        <StaticText align="ALIGN_CENTER_VERTICAL" label="$(container_label)" />
        <ContainerChoice
            name="container_choice"
            event_EVT_CONTAINER_CHANGED="on_container_changed"
            db="$(db)"
            align="ALIGN_LEFT"
        />
    """

    NOTEBOOK_ROW = """
        <Spacer />
        <Notebook name="notebook" style="BK_DEFAULT">
            <DescriptionEditor
                name="description"
                notebookLabel="$(page_description)"
                editor="$(self)"
                proportion="1"
            />
            <IconEditor
                name="icon"
                notebookLabel="$(page_icon)"
                editor="$(self)"
                proportion="1"
            />
            <AlertEditor
                name="alert"
                notebookLabel="$(page_alert)"
                editor="$(self)"
                proportion="1"
            />
            <HyperlinkEditor
                name="hyperlink"
                notebookLabel="$(page_hyperlink)"
                editor="$(self)"
                proportion="1"
            />
            <ProgressEditor
                name="progress"
                notebookLabel="$(page_progress)"
                editor="$(self)"
                proportion="1"
            />
            <ColorEditor
                name="default_color"
                notebookLabel="$(color)"
                editor="$(self)"
                proportion="1"
            />
        </Notebook>
    """

    def __init__(self, parent, config, title, db, start=None, end=None, event=None):
        self.parent = parent
        self.timeline = db
        self.config = config
        self.start = start
        self.event = event
        self._insert_rows_in_correct_order_in_xml()
        Dialog.__init__(self, EditEventDialogController, parent, {
            "self": self,
            "db": db,
            "time_type": db.get_time_type(),
            "config": config,
            "properties_label": _("Event Properties"),
            "when_label": _("When:"),
            "fuzzy_checkbox_text": _("Fuzzy"),
            "locked_checkbox_text": _("Locked"),
            "ends_today_checkbox_text": _("Ends today"),
            "text_label": _("Text:"),
            "category_label": _("Category:"),
            "container_label": _("Container:"),
            "page_description": _("Description"),
            "page_icon": _("Icon"),
            "page_alert": _("Alert"),
            "page_hyperlink": _("Hyperlink"),
            "page_progress": _("Progress"),
            "color": _("Default color"),
            "add_more_label": _("Add more events after this one"),
            "enlarge": _("&Enlarge"),
            "reduce": _("&Reduce"),
            "duplicate_label": _("Save and Duplicate"),
        }, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.controller.on_init(
            config,
            db.get_time_type(),
            DbWrapperEventRepository(db),
            db,
            start,
            end,
            event)
        self._make_row_with_notebook_growable()
        self.SetMinSize((800, -1))
        self.Fit()
        self.SetMinSize(self.GetSize())

    def GetDuplicateEventDialog(self, timeline, event):
        return DuplicateEventDialog(self.parent, timeline, event)

    def GetPeriod(self):
        return self.period_picker.GetValue()

    def SetPeriod(self, value):
        self.period_picker.SetValue(value)

    def GetShowPeriod(self):
        return self.period_picker.GetShowPeriod()

    def SetShowPeriod(self, value):
        self.period_picker.SetShowPeriod(value)

    def GetShowTime(self):
        return self.period_picker.GetShowTime()

    def SetShowTime(self, value):
        self.period_picker.SetShowTime(value)

    def DisableTime(self):
        self.period_picker.DisableTime()

    def GetFuzzy(self):
        return self.fuzzy_checkbox.GetValue()

    def SetFuzzy(self, value):
        self.fuzzy_checkbox.SetValue(value)

    def GetLocked(self):
        return self.locked_checkbox.GetValue()

    def SetLocked(self, value):
        self.locked_checkbox.SetValue(value)

    def EnableLocked(self, value):
        self.locked_checkbox.Enable(value)

    def GetEndsToday(self):
        return self.ends_today_checkbox.GetValue()

    def SetEndsToday(self, value):
        self.ends_today_checkbox.SetValue(value)

    def EnableEndsToday(self, value):
        self.ends_today_checkbox.Enable(value)

    def GetName(self):
        return self.name.GetValue().strip()

    def SetName(self, value):
        self.name.SetValue(value)

    def GetCategory(self):
        return self.category_choice.GetSelectedCategory()

    def SetCategory(self, value):
        self.category_choice.Populate(select=value)

    def GetContainer(self):
        return self.container_choice.GetSelectedContainer()

    def SetContainer(self, value):
        self.container_choice.Fill(value)

    def GetEventData(self):
        event_data = {}
        for data_id, editor in self._get_event_data():
            data = editor.get_data()
            if data is not None:
                event_data[data_id] = editor.get_data()
        return event_data

    def SetEventData(self, event_data):
        for data_id, editor in self._get_event_data():
            if data_id in event_data:
                data = event_data[data_id]
                if data is not None:
                    editor.set_data(data)

    def ClearEventData(self):
        for _, editor in self._get_event_data():
            editor.clear_data()

    def IsAddMoreChecked(self):
        return self.add_more_checkbox.GetValue()

    def SetShowAddMoreCheckbox(self, value):
        self.add_more_checkbox.Show(value)
        self.add_more_checkbox.SetValue(False)
        self.SetSizerAndFit(self.GetSizer())

    def SetFocusOnFirstControl(self):
        control = {
            "0": self.period_picker,
            "1": self.fuzzy_checkbox,
            "2": self.name,
            "3": self.category_choice,
            "4": self.container_choice,
            ":": self.notebook,
        }[self.config.event_editor_tab_order[0]]
        _set_focus_and_select(control)

    def DisplayInvalidPeriod(self, message):
        self._display_invalid_input(message, self.period_picker)

    def _display_invalid_input(self, message, control):
        self.DisplayErrorMessage(message)
        _set_focus_and_select(control)

    def _get_event_data(self):
        return [
            ("description", self.description),
            ("alert", self.alert),
            ("icon", self.icon),
            ("hyperlink", self.hyperlink),
            ("progress", self.progress),
            ("default_color", self.default_color)
        ]

    def _insert_rows_in_correct_order_in_xml(self):
        rows_by_key = {
            "0": self.TIME_DETAILS_ROW,
            "1": self.CHECKBOX_ROW,
            "2": self.TEXT_FIELD_ROW,
            "3": self.CATEGORY_LISTBOX_ROW,
            "4": self.CONTAINER_LISTBOX_ROW,
            ":": self.NOTEBOOK_ROW,
        }
        placeholder_content = "".join(rows_by_key[key] for key in self.config.event_editor_tab_order)
        self.__doc__ = self.__doc__ % placeholder_content

    def _make_row_with_notebook_growable(self):
        self.grid_sizer.AddGrowableRow(self.config.event_editor_tab_order.index(":"))


def open_event_editor_for(edit_controller, parent, config, db, event):
    def create_event_editor():
        if event.is_container():
            title = _("Edit Container")
            return EditContainerDialog(parent, title, db, event)
        else:
            return EditEventDialog(
                parent, config, _("Edit Event"), db, event=event)

    def edit_function():
        dialog = create_event_editor()
        dialog.ShowModal()
        dialog.Destroy()
    safe_locking(edit_controller, edit_function)


def open_create_event_editor(edit_controller, parent, config, db, start=None, end=None):
    def create_event_editor():
        label = _("Create Event")
        return EditEventDialog(parent, config, label, db, start, end)

    def edit_function():
        dialog = create_event_editor()
        dialog.ShowModal()
        dialog.Destroy()
    safe_locking(edit_controller, edit_function)
