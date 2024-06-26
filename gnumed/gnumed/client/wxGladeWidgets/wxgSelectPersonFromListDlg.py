# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class wxgSelectPersonFromListDlg(wx.Dialog):
	def __init__(self, *args, **kwds):
		# begin wxGlade: wxgSelectPersonFromListDlg.__init__
		kwds["style"] = kwds.get("style", 0) | wx.CAPTION | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetSize((600, 404))
		self.SetTitle(_("Select person from list"))

		_szr_main = wx.BoxSizer(wx.VERTICAL)

		_lbl_message = wx.StaticText(self, wx.ID_ANY, _("Please select a person from the list below."), style=wx.ALIGN_CENTER_HORIZONTAL)
		_szr_main.Add(_lbl_message, 0, wx.EXPAND, 0)

		from Gnumed.wxpython.gmListWidgets import cReportListCtrl
		self._LCTRL_persons = cReportListCtrl(self, wx.ID_ANY, style=wx.BORDER_NONE | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
		self._LCTRL_persons.SetFocus()
		_szr_main.Add(self._LCTRL_persons, 1, wx.EXPAND, 0)

		_szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		_szr_main.Add(_szr_buttons, 0, wx.EXPAND, 0)

		self._BTN_new_patient = wx.Button(self, wx.ID_NEW, "")
		self._BTN_new_patient.SetToolTip(_("Create a new patient."))
		_szr_buttons.Add(self._BTN_new_patient, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		_szr_buttons.Add((20, 20), 1, wx.EXPAND, 0)

		self._BTN_select = wx.Button(self, wx.ID_OK, _("Select"))
		self._BTN_select.SetToolTip(_("Select the person highlighted in the list above."))
		self._BTN_select.Enable(False)
		self._BTN_select.SetDefault()
		_szr_buttons.Add(self._BTN_select, 0, 0, 0)

		_szr_buttons.Add((20, 20), 1, wx.EXPAND, 0)

		self._BTN_cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
		self._BTN_cancel.SetToolTip(_("Cancel person selection."))
		_szr_buttons.Add(self._BTN_cancel, 0, 0, 0)

		self.SetSizer(_szr_main)

		self.Layout()
		self.Centre()

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated, self._LCTRL_persons)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected, self._LCTRL_persons)
		self.Bind(wx.EVT_BUTTON, self._on_new_patient_button_pressed, self._BTN_new_patient)
		# end wxGlade

	def _on_list_item_activated(self, event):  # wxGlade: wxgSelectPersonFromListDlg.<event_handler>
		print("Event handler '_on_list_item_activated' not implemented!")
		event.Skip()

	def _on_list_item_selected(self, event):  # wxGlade: wxgSelectPersonFromListDlg.<event_handler>
		print("Event handler '_on_list_item_selected' not implemented!")
		event.Skip()

	def _on_new_patient_button_pressed(self, event):  # wxGlade: wxgSelectPersonFromListDlg.<event_handler>
		print("Event handler '_on_new_patient_button_pressed' not implemented!")
		event.Skip()

# end of class wxgSelectPersonFromListDlg
