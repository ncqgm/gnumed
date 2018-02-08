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


import wx

from timelinelib.wxgui.dialogs.export.controller import ExportDialogController
from timelinelib.wxgui.dialogs.fieldselection.view import FieldSelectionDialog
from timelinelib.wxgui.framework import Dialog
from timelinelib.wxgui.utils import display_information_message


IGNORE = _("Ignore")
REPLACE = _("Replace")
XML_REPLACE = _("XML-Replace")
STRICT = _("Strict")
STRATEGY = {IGNORE: "ignore", REPLACE: "replace", XML_REPLACE: "xmlcharrefreplace", STRICT: "strict"}


class ExportDialog(Dialog):

    """
    <BoxSizerVertical>
        <StaticBoxSizerVertical label="$(type_description_text)" border="ALL">
            <ListBox style="LB_SINGLE" name="lb_target_types" />
        </StaticBoxSizerVertical>

        <StaticBoxSizerVertical label="$(encoding_description_text)" border="LEFT|RIGHT|BOTTOM">
            <ListBox style="LB_SINGLE" name="lb_text_encodings" />
        </StaticBoxSizerVertical>

        <StaticBoxSizerVertical label="$(encoding_error_strategy_text)" border="LEFT|RIGHT|BOTTOM">
            <ListBox 
                style="LB_SINGLE" 
                name="lb_error_strategies" 
                choices="$(lb_error_strategies_choices)" />
        </StaticBoxSizerVertical>

        <StaticBoxSizerVertical label="$(export_items_description_text)" border="LEFT|RIGHT|BOTTOM">
            <FlexGridSizer rows="0" columns="2" border="ALL">
                <CheckBox align="ALIGN_CENTER_VERTICAL" label="$(events_text)" name="cbx_events" />
                <Button align="ALIGN_CENTER_VERTICAL" label="$(select_text)"
                    event_EVT_BUTTON="on_edit_event_fields" />
                <CheckBox align="ALIGN_CENTER_VERTICAL" label="$(categories_text)" name="cbx_categories"/>
                <Button align="ALIGN_CENTER_VERTICAL" label="$(select_text)"
                    event_EVT_BUTTON="on_edit_categories_fields" />
            </FlexGridSizer>
        </StaticBoxSizerVertical>

        <DialogButtonsOkCancelSizer
            border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_OK="on_ok"
        />
    </BoxSizerVertical>
    """

    def __init__(self, parent):
        Dialog.__init__(self, ExportDialogController, parent, {
            "type_description_text": _("Select Export File Type"),
            "encoding_description_text": _("Select Text Encoding"),
            "encoding_error_strategy_text": _("Select encoding error strategy"),
            "export_items_description_text": _("Select Items to export"),
            "events_text": _("Events"),
            "categories_text": _("Categories"),
            "select_text": _("Select Fields..."),
            "lb_error_strategies_choices": [IGNORE, REPLACE, XML_REPLACE, STRICT],
        }, title=_("Export Timeline"))
        self.controller.on_init()
        self.lb_error_strategies.Select(0)

    def SetTargetTypes(self, types):
        self.lb_target_types.AppendItems(types)
        self.lb_target_types.Select(0)

    def SetTextEncodings(self, encodings):
        self.lb_text_encodings.AppendItems(encodings)
        self.lb_text_encodings.Select(0)

    def SetEvents(self, state):
        self.cbx_events.SetValue(state)

    def SetCategories(self, state):
        self.cbx_categories.SetValue(state)

    def EditEventFields(self):
        dlg = FieldSelectionDialog(self, _("Select Event Fields"), "Event",
                                   self.controller.get_event_fields())
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.set_event_fields(dlg.GetSelectedFields())
        dlg.Destroy()

    def EditCategoryFields(self):
        dlg = FieldSelectionDialog(self, _("Select Category Fields"), "Category",
                                   self.controller.get_category_fields())
        if dlg.ShowModal() == wx.ID_OK:
            self.controller.set_category_fields(dlg.GetSelectedFields())
        dlg.Destroy()

    def GetExportEvents(self):
        return self.cbx_events.GetValue()

    def GetExportCategories(self):
        return self.cbx_categories.GetValue()

    def DisplayInformationMessage(self, label, text):
        display_information_message(label, text, self)

    def Close(self):
        self.EndModal(wx.ID_OK)

    def GetExportType(self):
        return self.lb_target_types.GetStringSelection()

    def GetTextEncoding(self):
        return self.lb_text_encodings.GetStringSelection()

    def GetTextEncodingErrorStrategy(self):
        return STRATEGY[self.lb_error_strategies.GetStringSelection()]

    def GetEventFields(self):
        return self.controller.get_event_fields()

    def GetCategoryFields(self):
        return self.controller.get_category_fields()
