"""GNUmed list controls and widgets.

TODO:

	From: Rob McMullen <rob.mcmullen@gmail.com>
	To: wxPython-users@lists.wxwidgets.org
	Subject: Re: [wxPython-users] ANN: ColumnSizer mixin for ListCtrl

	Thanks for all the suggestions, on and off line.  There's an update
	with a new name (ColumnAutoSizeMixin) and better sizing algorithm at:

	http://trac.flipturn.org/browser/trunk/peppy/lib/column_autosize.py

	sorting: http://code.activestate.com/recipes/426407/
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import types
import logging
import thread
import time
import re as regex


import wx
import wx.lib.mixins.listctrl as listmixins


_log = logging.getLogger('gm.list_ui')
#================================================================
# FIXME: configurable callback on double-click action

def get_choices_from_list (
			parent=None,
			msg=None,
			caption=None,
			columns=None,
			choices=None,
			data=None,
			selections=None,
			edit_callback=None,
			new_callback=None,
			delete_callback=None,
			refresh_callback=None,
			single_selection=False,
			can_return_empty=False,
			ignore_OK_button=False,
			left_extra_button=None,
			middle_extra_button=None,
			right_extra_button=None,
			list_tooltip_callback=None):
	"""Let user select item(s) from a list.

	- new_callback: ()
	- edit_callback: (item data)
	- delete_callback: (item data)
	- refresh_callback: (listctrl)
	- list_tooltip_callback: (item data)

	- left/middle/right_extra_button: (label, tooltip, <callback> [, wants_list_ctrl])
		wants_list_ctrl is optional
		<callback> is called with item_data (or listctrl) as the only argument

	returns:
		on [CANCEL]: None
		on [OK]:
			if any items selected:
				list of selected items
			else:
				if can_return_empty is True:
					empty list
				else:
					None
	"""
	if caption is None:
		caption = _('generic multi choice dialog')

	if single_selection:
		dlg = cGenericListSelectorDlg(parent, -1, title = caption, msg = msg, style = wx.LC_SINGLE_SEL)
	else:
		dlg = cGenericListSelectorDlg(parent, -1, title = caption, msg = msg)

	dlg.refresh_callback = refresh_callback
	dlg.edit_callback = edit_callback
	dlg.new_callback = new_callback
	dlg.delete_callback = delete_callback
	dlg.list_tooltip_callback = list_tooltip_callback

	dlg.ignore_OK_button = ignore_OK_button
	dlg.left_extra_button = left_extra_button
	dlg.middle_extra_button = middle_extra_button
	dlg.right_extra_button = right_extra_button

	dlg.set_columns(columns = columns)

	if refresh_callback is None:
		dlg.set_string_items(items = choices)		# list ctrl will refresh anyway if possible
		dlg.set_column_widths()

	if data is not None:
		dlg.set_data(data = data)					# can override data set if refresh_callback is not None

	if selections is not None:
		dlg.set_selections(selections = selections)
	dlg.can_return_empty = can_return_empty

	btn_pressed = dlg.ShowModal()
	sels = dlg.get_selected_item_data(only_one = single_selection)
	dlg.Destroy()

	if btn_pressed == wx.ID_OK:
		if can_return_empty and (sels is None):
			return []
		return sels

	return None
#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgGenericListSelectorDlg

class cGenericListSelectorDlg(wxgGenericListSelectorDlg.wxgGenericListSelectorDlg):
	"""A dialog holding a list and a few buttons to act on the items."""

	# FIXME: configurable callback on double-click action

	def __init__(self, *args, **kwargs):

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError: msg = None

		wxgGenericListSelectorDlg.wxgGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.message = msg

		self.left_extra_button = None
		self.middle_extra_button = None
		self.right_extra_button = None

		self.refresh_callback = None			# called when new/edit/delete callbacks return True (IOW were not cancelled)
		self.new_callback = None				# called when NEW button pressed, no argument passed in
		self.edit_callback = None				# called when EDIT button pressed, data of topmost selected item passed in
		self.delete_callback = None				# called when DELETE button pressed, data of topmost selected item passed in

		self.can_return_empty = False
		self.ignore_OK_button = False			# by default do show/use the OK button
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)
	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		self._LCTRL_items.set_column_widths(widths = widths)
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.Select(0)
	#------------------------------------------------------------
	def set_selections(self, selections = None):
		self._LCTRL_items.set_selections(selections = selections)
		if selections is None:
			return
		if len(selections) == 0:
			return
		if self.ignore_OK_button:
			return
		self._BTN_ok.Enable(True)
		self._BTN_ok.SetDefault()
	#------------------------------------------------------------
	def set_data(self, data = None):
		self._LCTRL_items.set_data(data = data)
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):
		return self._LCTRL_items.get_selected_item_data(only_one=only_one)
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_selected(self, event):
		if not self.__ignore_OK_button:
			self._BTN_ok.SetDefault()
			self._BTN_ok.Enable(True)

		if self.edit_callback is not None:
			self._BTN_edit.Enable(True)

		if self.delete_callback is not None:
			self._BTN_delete.Enable(True)
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			if not self.can_return_empty:
				self._BTN_cancel.SetDefault()
				self._BTN_ok.Enable(False)
			self._BTN_edit.Enable(False)
			self._BTN_delete.Enable(False)
	#------------------------------------------------------------
	def _on_new_button_pressed(self, event):
		if not self.new_callback():
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		# if the edit button *can* be pressed there are *supposed*
		# to be both an item selected and an editor configured
		if not self.edit_callback(self._LCTRL_items.get_selected_item_data(only_one=True)):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		# if the delete button *can* be pressed there are *supposed*
		# to be both an item selected and a deletor configured
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item_data is None:
			self._LCTRL_items.SetFocus()
			return
		if not self.delete_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		if self.__left_extra_button_wants_list:
			item_data = self._LCTRL_items
		else:
			item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__left_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_middle_extra_button_pressed(self, event):
		if self.__middle_extra_button_wants_list:
			item_data = self._LCTRL_items
		else:
			item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__middle_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_right_extra_button_pressed(self, event):
		if self.__right_extra_button_wants_list:
			item_data = self._LCTRL_items
		else:
			item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__right_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _set_ignore_OK_button(self, ignored):
		self.__ignore_OK_button = ignored
		if self.__ignore_OK_button:
			self._BTN_ok.Hide()
			self._BTN_ok.Enable(False)
		else:
			self._BTN_ok.Show()
			if self._LCTRL_items.get_selected_items(only_one=True) == -1:
				if self.can_return_empty:
					self._BTN_ok.Enable(True)
				else:
					self._BTN_ok.Enable(False)
					self._BTN_cancel.SetDefault()

	ignore_OK_button = property(lambda x:x, _set_ignore_OK_button)
	#------------------------------------------------------------
	def _set_left_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_left.Enable(False)
			self._BTN_extra_left.Hide()
			self.__left_extra_button_callback = None
			self.__left_extra_button_wants_list = False
			return

		if len(definition) == 3:
			(label, tooltip, callback) = definition
			wants_list = False
		else:
			(label, tooltip, callback, wants_list) = definition

		if not callable(callback):
			raise ValueError('<left extra button> callback is not a callable: %s' % callback)
		self.__left_extra_button_callback = callback
		self.__left_extra_button_wants_list = wants_list
		self._BTN_extra_left.SetLabel(label)
		self._BTN_extra_left.SetToolTipString(tooltip)
		self._BTN_extra_left.Enable(True)
		self._BTN_extra_left.Show()

	left_extra_button = property(lambda x:x, _set_left_extra_button)
	#------------------------------------------------------------
	def _set_middle_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_middle.Enable(False)
			self._BTN_extra_middle.Hide()
			self.__middle_extra_button_callback = None
			self.__middle_extra_button_wants_list = False
			return

		if len(definition) == 3:
			(label, tooltip, callback) = definition
			wants_list = False
		else:
			(label, tooltip, callback, wants_list) = definition

		if not callable(callback):
			raise ValueError('<middle extra button> callback is not a callable: %s' % callback)
		self.__middle_extra_button_callback = callback
		self.__middle_extra_button_wants_list = wants_list
		self._BTN_extra_middle.SetLabel(label)
		self._BTN_extra_middle.SetToolTipString(tooltip)
		self._BTN_extra_middle.Enable(True)
		self._BTN_extra_middle.Show()

	middle_extra_button = property(lambda x:x, _set_middle_extra_button)
	#------------------------------------------------------------
	def _set_right_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_right.Enable(False)
			self._BTN_extra_right.Hide()
			self.__right_extra_button_callback = None
			self.__right_extra_button_wants_list = False
			return

		if len(definition) == 3:
			(label, tooltip, callback) = definition
			wants_list = False
		else:
			(label, tooltip, callback, wants_list) = definition

		if not callable(callback):
			raise ValueError('<right extra button> callback is not a callable: %s' % callback)
		self.__right_extra_button_callback = callback
		self.__right_extra_button_wants_list = wants_list
		self._BTN_extra_right.SetLabel(label)
		self._BTN_extra_right.SetToolTipString(tooltip)
		self._BTN_extra_right.Enable(True)
		self._BTN_extra_right.Show()

	right_extra_button = property(lambda x:x, _set_right_extra_button)
	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		if callback is not None:
			if self.refresh_callback is None:
				raise ValueError('refresh callback must be set before new callback can be set')
			if not callable(callback):
				raise ValueError('<new> callback is not a callable: %s' % callback)
		self.__new_callback = callback

		if callback is None:
			self._BTN_new.Enable(False)
			self._BTN_new.Hide()
		else:
			self._BTN_new.Enable(True)
			self._BTN_new.Show()

	new_callback = property(_get_new_callback, _set_new_callback)
	#------------------------------------------------------------
	def _get_edit_callback(self):
		return self.__edit_callback

	def _set_edit_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<edit> callback is not a callable: %s' % callback)
		self.__edit_callback = callback

		if callback is None:
			self._BTN_edit.Enable(False)
			self._BTN_edit.Hide()
		else:
			self._BTN_edit.Enable(True)
			self._BTN_edit.Show()

	edit_callback = property(_get_edit_callback, _set_edit_callback)
	#------------------------------------------------------------
	def _get_delete_callback(self):
		return self.__delete_callback

	def _set_delete_callback(self, callback):
		if callback is not None:
			if self.refresh_callback is None:
				raise ValueError('refresh callback must be set before delete callback can be set')
			if not callable(callback):
				raise ValueError('<delete> callback is not a callable: %s' % callback)
		self.__delete_callback = callback

		if callback is None:
			self._BTN_delete.Enable(False)
			self._BTN_delete.Hide()
		else:
			self._BTN_delete.Enable(True)
			self._BTN_delete.Show()

	delete_callback = property(_get_delete_callback, _set_delete_callback)
	#------------------------------------------------------------
	def _get_refresh_callback(self):
		return self.__refresh_callback

	def _set_refresh_callback_helper(self):
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()

	def _set_refresh_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<refresh> callback is not a callable: %s' % callback)
		self.__refresh_callback = callback
		if callback is not None:
			wx.CallAfter(self._set_refresh_callback_helper)

	refresh_callback = property(_get_refresh_callback, _set_refresh_callback)
	#------------------------------------------------------------
	def _set_list_tooltip_callback(self, callback):
		self._LCTRL_items.item_tooltip_callback = callback

	list_tooltip_callback = property(lambda x:x, _set_list_tooltip_callback)
	#def _get_tooltip(self, item):		# inside a class
	#def _get_tooltip(item):			# outside a class
	#------------------------------------------------------------
	def _set_message(self, message):
		if message is None:
			self._LBL_message.Hide()
			return
		self._LBL_message.SetLabel(message)
		self._LBL_message.Show()

	message = property(lambda x:x, _set_message)
#================================================================
from Gnumed.wxGladeWidgets import wxgGenericListManagerPnl

class cGenericListManagerPnl(wxgGenericListManagerPnl.wxgGenericListManagerPnl):
	"""A panel holding a generic multi-column list and action buttions."""

	def __init__(self, *args, **kwargs):

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError: msg = None

		wxgGenericListManagerPnl.wxgGenericListManagerPnl.__init__(self, *args, **kwargs)

		if msg is None:
			self._LBL_message.Hide()
		else:
			self._LBL_message.SetLabel(msg)

		# new/edit/delete must return True/False to enable refresh
		self.__new_callback = None				# called when NEW button pressed, no argument passed in
		self.edit_callback = None				# called when EDIT button pressed, data of topmost selected item passed in
		self.delete_callback = None				# called when DELETE button pressed, data of topmost selected item passed in
		self.refresh_callback = None			# called when new/edit/delete callbacks return True (IOW were not cancelled)

		self.__select_callback = None			# called when an item is selected, data of topmost selected item passed in

		self.left_extra_button = None
		self.middle_extra_button = None
		self.right_extra_button = None
	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()

		if (items is None) or (len(items) == 0):
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
		else:
			self._LCTRL_items.Select(0)
	#------------------------------------------------------------
	def set_selections(self, selections = None):
		self._LCTRL_items.set_selections(selections = selections)
	#------------------------------------------------------------
	def set_data(self, data = None):
		self._LCTRL_items.set_data(data = data)
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):
		return self._LCTRL_items.get_selected_item_data(only_one=only_one)
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_selected(self, event):
		if self.edit_callback is not None:
			self._BTN_edit.Enable(True)
		if self.delete_callback is not None:
			self._BTN_remove.Enable(True)
		if self.__select_callback is not None:
			item = self._LCTRL_items.get_selected_item_data(only_one=True)
			self.__select_callback(item)
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
			if self.__select_callback is not None:
				self.__select_callback(None)
	#------------------------------------------------------------
	def _on_add_button_pressed(self, event):
		if not self.new_callback():
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
	#------------------------------------------------------------
	def _on_list_item_activated(self, event):
		if self.edit_callback is None:
			return
		self._on_edit_button_pressed(event)
	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		item = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item is None:
			return
		if not self.edit_callback(item):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
	#------------------------------------------------------------
	def _on_remove_button_pressed(self, event):
		item = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item is None:
			return
		if not self.delete_callback(item):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
	#------------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__left_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_middle_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__middle_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	def _on_right_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__right_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return
		if self.refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.SetFocus()
	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<new> callback is not a callable: %s' % callback)
		self.__new_callback = callback
		self._BTN_add.Enable(callback is not None)

	new_callback = property(_get_new_callback, _set_new_callback)
	#------------------------------------------------------------
	def _get_select_callback(self):
		return self.__select_callback

	def _set_select_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<select> callback is not a callable: %s' % callback)
		self.__select_callback = callback

	select_callback = property(_get_select_callback, _set_select_callback)
	#------------------------------------------------------------
	def _get_message(self):
		return self._LBL_message.GetLabel()

	def _set_message(self, msg):
		if msg is None:
			self._LBL_message.Hide()
			self._LBL_message.SetLabel(u'')
		else:
			self._LBL_message.SetLabel(msg)
			self._LBL_message.Show()
		self.Layout()

	message = property(_get_message, _set_message)
	#------------------------------------------------------------
	def _set_left_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_left.Enable(False)
			self._BTN_extra_left.Hide()
			self.__left_extra_button_callback = None
			return

		(label, tooltip, callback) = definition
		if not callable(callback):
			raise ValueError('<left extra button> callback is not a callable: %s' % callback)
		self.__left_extra_button_callback = callback
		self._BTN_extra_left.SetLabel(label)
		self._BTN_extra_left.SetToolTipString(tooltip)
		self._BTN_extra_left.Enable(True)
		self._BTN_extra_left.Show()

	left_extra_button = property(lambda x:x, _set_left_extra_button)
	#------------------------------------------------------------
	def _set_middle_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_middle.Enable(False)
			self._BTN_extra_middle.Hide()
			self.__middle_extra_button_callback = None
			return

		(label, tooltip, callback) = definition
		if not callable(callback):
			raise ValueError('<middle extra button> callback is not a callable: %s' % callback)
		self.__middle_extra_button_callback = callback
		self._BTN_extra_middle.SetLabel(label)
		self._BTN_extra_middle.SetToolTipString(tooltip)
		self._BTN_extra_middle.Enable(True)
		self._BTN_extra_middle.Show()

	middle_extra_button = property(lambda x:x, _set_middle_extra_button)
	#------------------------------------------------------------
	def _set_right_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_right.Enable(False)
			self._BTN_extra_right.Hide()
			self.__right_extra_button_callback = None
			return

		(label, tooltip, callback) = definition
		if not callable(callback):
			raise ValueError('<right extra button> callback is not a callable: %s' % callback)
		self.__right_extra_button_callback = callback
		self._BTN_extra_right.SetLabel(label)
		self._BTN_extra_right.SetToolTipString(tooltip)
		self._BTN_extra_right.Enable(True)
		self._BTN_extra_right.Show()

	right_extra_button = property(lambda x:x, _set_right_extra_button)
#================================================================
from Gnumed.wxGladeWidgets import wxgItemPickerDlg

class cItemPickerDlg(wxgItemPickerDlg.wxgItemPickerDlg):

	def __init__(self, *args, **kwargs):

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError:
			msg = None

		wxgItemPickerDlg.wxgItemPickerDlg.__init__(self, *args, **kwargs)

		if msg is None:
			self._LBL_msg.Hide()
		else:
			self._LBL_msg.SetLabel(msg)

		self.allow_duplicate_picks = True

		self._LCTRL_left.activate_callback = self.__pick_selected
		self.__extra_button_callback = None

		self._LCTRL_left.SetFocus()
	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def set_columns(self, columns=None, columns_right=None):
		self._LCTRL_left.set_columns(columns = columns)
		if columns_right is None:
			self._LCTRL_right.set_columns(columns = columns)
		else:
			if len(columns_right) < len(columns):
				cols = columns
			else:
				cols = columns_right[:len(columns)]
			self._LCTRL_right.set_columns(columns = cols)
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		self._LCTRL_left.set_string_items(items = items)
		self._LCTRL_left.set_column_widths()
		self._LCTRL_right.set_string_items()

		self._BTN_left2right.Enable(False)
		self._BTN_right2left.Enable(False)
	#------------------------------------------------------------
	def set_selections(self, selections = None):
		self._LCTRL_left.set_selections(selections = selections)
	#------------------------------------------------------------
	def set_choices(self, choices=None, data=None):
		self.set_string_items(items = choices)
		if data is not None:
			self.set_data(data = data)
	#------------------------------------------------------------
	def set_picks(self, picks=None, data=None):
		self._LCTRL_right.set_string_items(picks)
		self._LCTRL_right.set_column_widths()
		if data is not None:
			self._LCTRL_right.set_data(data = data)
	#------------------------------------------------------------
	def set_data(self, data = None):
		self._LCTRL_left.set_data(data = data)
	#------------------------------------------------------------
	def get_picks(self):
		return self._LCTRL_right.get_item_data()

	picks = property(get_picks, lambda x:x)
	#------------------------------------------------------------
	def _set_extra_button(self, definition):
		if definition is None:
			self._BTN_extra.Enable(False)
			self._BTN_extra.Hide()
			self.__extra_button_callback = None
			return

		(label, tooltip, callback) = definition
		if not callable(callback):
			raise ValueError('<extra button> callback is not a callable: %s' % callback)
		self.__extra_button_callback = callback
		self._BTN_extra.SetLabel(label)
		self._BTN_extra.SetToolTipString(tooltip)
		self._BTN_extra.Enable(True)
		self._BTN_extra.Show()

	extra_button = property(lambda x:x, _set_extra_button)
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __pick_selected(self, event=None):
		if self._LCTRL_left.get_selected_items(only_one = True) == -1:
			return

		right_items = self._LCTRL_right.get_string_items()
		right_data = self._LCTRL_right.get_item_data()
		if right_data is None:
			right_data = []

		selected_items = self._LCTRL_left.get_selected_string_items(only_one = False)
		selected_data = self._LCTRL_left.get_selected_item_data(only_one = False)

		if self.allow_duplicate_picks:
			right_items.extend(selected_items)
			right_data.extend(selected_data)
			self._LCTRL_right.set_string_items(items = right_items)
			self._LCTRL_right.set_data(data = right_data)
			self._LCTRL_right.set_column_widths()
#			print u'%s <-> %s (items)' % (self._LCTRL_left.ItemCount, self._LCTRL_right.ItemCount)
#			print u'%s <-> %s (data)' % (len(self._LCTRL_left.data), len(self._LCTRL_right.data))
			return

		for sel_item, sel_data in zip(selected_items, selected_data):
			if sel_item in right_items:
				continue
			right_items.append(sel_item)
			right_data.append(sel_data)
		self._LCTRL_right.set_string_items(items = right_items)
		self._LCTRL_right.set_data(data = right_data)
		self._LCTRL_right.set_column_widths()
#		print u'%s <-> %s (items)' % (self._LCTRL_left.ItemCount, self._LCTRL_right.ItemCount)
#		print u'%s <-> %s (data)' % (len(self._LCTRL_left.data), len(self._LCTRL_right.data))
	#------------------------------------------------------------
	def __remove_selected_picks(self):
		if self._LCTRL_right.get_selected_items(only_one = True) == -1:
			return

		for item_idx in self._LCTRL_right.get_selected_items(only_one = False):
			self._LCTRL_right.remove_item(item_idx)

		if self._LCTRL_right.GetItemCount() == 0:
			self._BTN_right2left.Enable(False)

#		print u'%s <-> %s (items)' % (self._LCTRL_left.ItemCount, self._LCTRL_right.ItemCount)
#		print u'%s <-> %s (data)' % (len(self._LCTRL_left.data), len(self._LCTRL_right.data))
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_left_list_item_selected(self, event):
		self._BTN_left2right.Enable(True)
	#------------------------------------------------------------
	def _on_left_list_item_deselected(self, event):
		if self._LCTRL_left.get_selected_items(only_one = True) == -1:
			self._BTN_left2right.Enable(False)
	#------------------------------------------------------------
	def _on_right_list_item_selected(self, event):
		self._BTN_right2left.Enable(True)
	#------------------------------------------------------------
	def _on_right_list_item_deselected(self, event):
		if self._LCTRL_right.get_selected_items(only_one = True) == -1:
			self._BTN_right2left.Enable(False)
	#------------------------------------------------------------
	def _on_button_left2right_pressed(self, event):
		self.__pick_selected()
	#------------------------------------------------------------
	def _on_button_right2left_pressed(self, event):
		self.__remove_selected_picks()
	#------------------------------------------------------------
	def _on_extra_button_pressed(self, event):
		self.__extra_button_callback()
	#------------------------------------------------------------
	def _set_left_item_tooltip_callback(self, callback):
		self._LCTRL_left.item_tooltip_callback = callback

	left_item_tooltip_callback = property(lambda x:x, _set_left_item_tooltip_callback)
	#------------------------------------------------------------
	def _set_right_item_tooltip_callback(self, callback):
		self._LCTRL_right.item_tooltip_callback = callback

	right_item_tooltip_callback = property(lambda x:x, _set_right_item_tooltip_callback)

#================================================================
class cReportListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin, listmixins.ColumnSorterMixin):

	# sorting: at set_string_items() time all items will be
	# adorned with their initial row number as wxPython data,
	# this is used later for a) sorting and b) to access
	# GNUmed data objects associated with rows,
	# the latter are ordered in initial row number order
	# at set_data() time

	map_item_idx2data_idx = wx.ListCtrl.GetItemData

	sort_order_tags = {
		True: u' [\u03b1\u0391 \u2192 \u03c9\u03A9]',
		False: u' [\u03c9\u03A9 \u2192 \u03b1\u0391]'
	}

	def __init__(self, *args, **kwargs):

		self.debug = None

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) == wx.LC_SINGLE_SEL)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)

		# required for column sorting, MUST have this name
		self._invalidate_sorting_metadata()					# must be called after each (external/direct) list item update
		listmixins.ColumnSorterMixin.__init__(self, 0)		# must be called again after adding columns (why ?)
		# for debugging sorting:
		#self.Bind(wx.EVT_LIST_COL_CLICK, self._on_col_click, self)

		self.__widths = None
		self.__data = None
		self.__activate_callback = None
		self.__rightclick_callback = None

		self.__item_tooltip_callback = None
		self.__tt_last_item = None
		self.__tt_static_part = _("""Select the items you want to work on.

A discontinuous selection may depend on your holding down a platform-dependent modifier key (<ctrl>, <alt>, etc) or key combination (eg. <ctrl-shift> or <ctrl-alt>) while clicking.""")
		self.Bind(wx.EVT_MOTION, self._on_mouse_motion)

		self.__next_line_to_search = 0
		self.__search_data = None
		self.__search_dlg = None
		self.__searchable_cols = None
#		self.Bind(wx.EVT_KILL_FOCUS, self._on_lost_focus)
		self.Bind(wx.EVT_CHAR, self._on_char)
		self.Bind(wx.EVT_FIND_CLOSE, self._on_search_dlg_closed)
		self.Bind(wx.EVT_FIND, self._on_search_first_match)
		self.Bind(wx.EVT_FIND_NEXT, self._on_search_next_match)
	#------------------------------------------------------------
	# setters
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		"""(Re)define the columns.

		Note that this will (have to) delete the items.
		"""
		self.ClearAll()
		self.__tt_last_item = None
		if columns is None:
			return
		for idx in range(len(columns)):
			self.InsertColumn(idx, columns[idx])

		self._invalidate_sorting_metadata()
	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		"""Set the column width policy.

		widths = None:
			use previous policy if any or default policy
		widths != None:
			use this policy and remember it for later calls

		This means there is no way to *revert* to the default policy :-(
		"""
		# explicit policy ?
		if widths is not None:
			self.__widths = widths
			for idx in range(len(self.__widths)):
				self.SetColumnWidth(col = idx, width = self.__widths[idx])
			return

		# previous policy ?
		if self.__widths is not None:
			for idx in range(len(self.__widths)):
				self.SetColumnWidth(col = idx, width = self.__widths[idx])
			return

		# default policy !
		if self.GetItemCount() == 0:
			width_type = wx.LIST_AUTOSIZE_USEHEADER
		else:
			width_type = wx.LIST_AUTOSIZE
		for idx in range(self.GetColumnCount()):
			self.SetColumnWidth(col = idx, width = width_type)
	#------------------------------------------------------------
	def set_string_items(self, items=None):
		"""All item members must be unicode()able or None."""

		wx.BeginBusyCursor()
		self._invalidate_sorting_metadata()

		# remove existing items
		loop = 0
		while True:
			if loop > 3:
				_log.debug('unable to delete list items after looping 3 times, continuing and hoping for the best')
				break
			loop += 1
			if self.debug is not None:
				_log.debug('[round %s] GetItemCount() before DeleteAllItems(): %s (%s, thread [%s])', loop, self.GetItemCount(), self.debug, thread.get_ident())
			if not self.DeleteAllItems():
				_log.debug('DeleteAllItems() failed (%s)', self.debug)
			item_count = self.GetItemCount()
			if self.debug is not None:
				_log.debug('GetItemCount() after DeleteAllItems(): %s (%s)', item_count, self.debug)
			if item_count == 0:
				break
			wx.SafeYield(None, True)
			_log.debug('GetItemCount() not 0 after DeleteAllItems() (%s)', self.debug)
			time.sleep(0.3)
			wx.SafeYield(None, True)

		if items is None:
			self.data = None
			wx.EndBusyCursor()
			return

		# insert new items
		for item in items:
			try:
				item[0]
				if not isinstance(item, basestring):
					is_numerically_iterable = True
				# do not iterate over individual chars in a string, however
				else:
					is_numerically_iterable = False
			except TypeError:
				is_numerically_iterable = False

			if is_numerically_iterable:
				# cannot use errors='replace' since then
				# None/ints/unicode strings fail to get encoded
				col_val = unicode(item[0])
				row_num = self.InsertStringItem(index = sys.maxint, label = col_val)
				for col_num in range(1, min(self.GetColumnCount(), len(item))):
					col_val = unicode(item[col_num])
					self.SetStringItem(index = row_num, col = col_num, label = col_val)
			else:
				# cannot use errors='replace' since then None/ints/unicode strings fails to get encoded
				col_val = unicode(item)
				row_num = self.InsertStringItem(index = sys.maxint, label = col_val)

		# set data to be a copy of items
		self.data = items

		wx.EndBusyCursor()
	#------------------------------------------------------------
	def set_data(self, data=None):
		"""<data> assumed to be a list corresponding to the item indices"""
		if data is not None:
			item_count = self.GetItemCount()
			if len(data) != item_count:
				_log.debug('<data> length (%s) must be equal to number of list items (%s)  (%s, thread [%s])', len(data), item_count, self.debug, thread.get_ident())
			for item_idx in range(len(data)):
				self.SetItemData(item_idx, item_idx)
		self.__data = data
		self.__tt_last_item = None
		# string data (rows/visible list items) not modified,
		# so no need to call _update_sorting_metadata
		return

	def _get_data(self):
		# slower than "return self.__data" but helps with detecting
		# problems with len(__data)<>self.GetItemCount()
		return self.get_item_data() 		# returns all data if item_idx is None

	data = property(_get_data, set_data)
	#------------------------------------------------------------
	def set_selections(self, selections=None):
		self.Select(0, on = 0)
		if selections is None:
			return
		for idx in selections:
			self.Select(idx = idx, on = 1)

	def __get_selections(self):
		if self.__is_single_selection:
			return [self.GetFirstSelected()]
		selections = []
		idx = self.GetFirstSelected()
		while idx != -1:
			selections.append(idx)
			idx = self.GetNextSelected(idx)
		return selections

	selections = property(__get_selections, set_selections)
	#------------------------------------------------------------
	# getters
	#------------------------------------------------------------
	def get_column_labels(self):
		labels = []
		for col_idx in self.GetColumnCount():
			col = self.GetColumn(col = col_idx)
			labels.append(col.GetText())
		return labels
	#------------------------------------------------------------
	def get_item(self, item_idx=None):
		if item_idx is not None:
			return self.GetItem(item_idx)
	#------------------------------------------------------------
	def get_items(self):
		return [ self.GetItem(item_idx) for item_idx in range(self.GetItemCount()) ]
	#------------------------------------------------------------
	def get_string_items(self):
		return [ self.GetItemText(item_idx) for item_idx in range(self.GetItemCount()) ]
	#------------------------------------------------------------
	def get_selected_items(self, only_one=False):

		if self.__is_single_selection or only_one:
			return self.GetFirstSelected()

		items = []
		idx = self.GetFirstSelected()
		while idx != -1:
			items.append(idx)
			idx = self.GetNextSelected(idx)

		return items
	#------------------------------------------------------------
	def get_selected_string_items(self, only_one=False):

		if self.__is_single_selection or only_one:
			return self.GetItemText(self.GetFirstSelected())

		items = []
		idx = self.GetFirstSelected()
		while idx != -1:
			items.append(self.GetItemText(idx))
			idx = self.GetNextSelected(idx)

		return items
	#------------------------------------------------------------
	def get_item_data(self, item_idx = None):
		if self.__data is None:	# this isn't entirely clean
			return None

		if item_idx is not None:
			return self.__data[self.map_item_idx2data_idx(item_idx)]

		# if <idx> is None return all data up to item_count,
		# in case of len(__data) <> self.GetItemCount() this
		# gives the chance to figure out what is going on
		return [ self.__data[self.map_item_idx2data_idx(item_idx)] for item_idx in range(self.GetItemCount()) ]
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):

		if self.__is_single_selection or only_one:
			if self.__data is None:
				return None
			idx = self.GetFirstSelected()
			if idx == -1:
				return None
			return self.__data[self.map_item_idx2data_idx(idx)]

		data = []
		if self.__data is None:
			return data
		idx = self.GetFirstSelected()
		while idx != -1:
			data.append(self.__data[self.map_item_idx2data_idx(idx)])
			idx = self.GetNextSelected(idx)

		return data
	#------------------------------------------------------------
	def deselect_selected_item(self):
		self.Select(idx = self.GetFirstSelected(), on = 0)
	#------------------------------------------------------------
	def remove_item(self, item_idx=None):
		# do NOT remove the corresponding data because even if
		# the item pointing to this data instance is gone all
		# other items will still point to their corresponding
		# *initial* row numbers
		#if self.__data is not None:
		#	del self.__data[self.map_item_idx2data_idx(item_idx)]
		self.DeleteItem(item_idx)
		self.__tt_last_item = None
		self._invalidate_sorting_metadata()
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_activated(self, event):
		event.Skip()
		if self.__activate_callback is not None:
			self.__activate_callback(event)
	#------------------------------------------------------------
	def _on_list_item_rightclicked(self, event):
		event.Skip()
		if self.__rightclick_callback is not None:
			self.__rightclick_callback(event)
	#------------------------------------------------------------
	def _on_char(self, evt):

		if evt.GetModifiers() != wx.MOD_CMD:
			evt.Skip()
			return

		if unichr(evt.GetRawKeyCode()) != u'f':
			evt.Skip()
			return

		if self.__search_dlg is not None:
			self.__search_dlg.Close()
			return

		if self.__searchable_cols is None:
			self.searchable_columns = None

		if len(self.__searchable_cols) == 0:
			return

		if self.__search_data is None:
			self.__search_data = wx.FindReplaceData()
		self.__search_dlg = wx.FindReplaceDialog (
			self,
			self.__search_data,
			_('Search in list'),
			wx.FR_NOUPDOWN | wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD
		)
		self.__search_dlg.Show(True)
	#------------------------------------------------------------
	def _on_mouse_motion(self, event):
		"""Update tooltip on mouse motion.

			for s in dir(wx):
				if s.startswith('LIST_HITTEST'):
					print s, getattr(wx, s)

			LIST_HITTEST_ABOVE 1
			LIST_HITTEST_BELOW 2
			LIST_HITTEST_NOWHERE 4
			LIST_HITTEST_ONITEM 672
			LIST_HITTEST_ONITEMICON 32
			LIST_HITTEST_ONITEMLABEL 128
			LIST_HITTEST_ONITEMRIGHT 256
			LIST_HITTEST_ONITEMSTATEICON 512
			LIST_HITTEST_TOLEFT 1024
			LIST_HITTEST_TORIGHT 2048
		"""
		item_idx, where_flag = self.HitTest(wx.Point(event.X, event.Y))

		# pointer on item related area at all ?
		if where_flag not in [
			wx.LIST_HITTEST_ONITEMLABEL,
			wx.LIST_HITTEST_ONITEMICON,
			wx.LIST_HITTEST_ONITEMSTATEICON,
			wx.LIST_HITTEST_ONITEMRIGHT,
			wx.LIST_HITTEST_ONITEM
		]:
			self.__tt_last_item = None						# not on any item
			self.SetToolTipString(self.__tt_static_part)
			return

		# same item as last time around ?
		if self.__tt_last_item == item_idx:
			return

		# remeber the new item we are on
		self.__tt_last_item = item_idx

		# HitTest() can return -1 if it so pleases, meaning that no item
		# was hit or else that maybe there aren't any items (empty list)
		if item_idx == wx.NOT_FOUND:
			self.SetToolTipString(self.__tt_static_part)
			return

		# do we *have* item data ?
		if self.__data is None:
			self.SetToolTipString(self.__tt_static_part)
			return

		# under some circumstances the item_idx returned
		# by HitTest() may be out of bounds with respect to
		# self.__data, this hints at a sync problem between
		# setting display items and associated data
		if (
			(item_idx > (len(self.__data) - 1))
				or
			(item_idx < -1)
		):
			self.SetToolTipString(self.__tt_static_part)
			print "*************************************************************"
			print "GNUmed has detected an inconsistency with list item tooltips."
			print ""
			print "This is not a big problem and you can keep working."
			print ""
			print "However, please send us the following so we can fix GNUmed:"
			print ""
			print "item idx: %s" % item_idx
			print 'where flag: %s' % where_flag
			print 'data list length: %s' % len(self.__data)
			print "*************************************************************"
			return

		dyna_tt = None
		if self.__item_tooltip_callback is not None:
			dyna_tt = self.__item_tooltip_callback(self.__data[self.map_item_idx2data_idx(item_idx)])

		if dyna_tt is None:
			self.SetToolTipString(self.__tt_static_part)
			return

		self.SetToolTipString(dyna_tt)
	#------------------------------------------------------------
	# search related methods
	#------------------------------------------------------------
	def _on_search_dlg_closed(self, evt):
		self.__search_dlg.Destroy()
		self.__search_dlg = None
	#------------------------------------------------------------
#	def _on_lost_focus(self, evt):
#		evt.Skip()
#		if self.__search_dlg is None:
#			return
##		print self.FindFocus()
##		print self.__search_dlg
#		#self.__search_dlg.Close()
	#------------------------------------------------------------
	def __on_search_match(self, search_term):
		for row_idx in range(self.__next_line_to_search, self.ItemCount):
			for col_idx in range(self.ColumnCount):
				if col_idx not in self.__searchable_cols:
					continue
				col_val = self.GetItem(row_idx, col_idx).GetText()
				if regex.search(search_term, col_val, regex.U | regex.I) is not None:
					self.Select(row_idx)
					self.EnsureVisible(row_idx)
					if row_idx == self.ItemCount - 1:
						# wrap around
						self.__next_line_to_search = 0
					else:
						self.__next_line_to_search = row_idx + 1
					return True
		# wrap around
		self.__next_line_to_search = 0
		return False
	#------------------------------------------------------------
	def _on_search_first_match(self, evt):
		self.__on_search_match(evt.GetFindString())
	#------------------------------------------------------------
	def _on_search_next_match(self, evt):
		self.__on_search_match(evt.GetFindString())
	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_activate_callback(self):
		return self.__activate_callback

	def _set_activate_callback(self, callback):
		if callback is None:
			self.Unbind(wx.EVT_LIST_ITEM_ACTIVATED)
		else:
			if not callable(callback):
				raise ValueError('<activate> callback is not a callable: %s' % callback)
			self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated)
		self.__activate_callback = callback

	activate_callback = property(_get_activate_callback, _set_activate_callback)
	#------------------------------------------------------------
	def _get_rightclick_callback(self):
		return self.__rightclick_callback

	def _set_rightclick_callback(self, callback):
		if callback is None:
			self.Unbind(wx.EVT_LIST_ITEM_RIGHT_CLICK)
		else:
			if not callable(callback):
				raise ValueError('<rightclick> callback is not a callable: %s' % callback)
			self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_list_item_rightclicked)
		self.__rightclick_callback = callback

	rightclick_callback = property(_get_rightclick_callback, _set_rightclick_callback)
	#------------------------------------------------------------
	def _set_item_tooltip_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<item_tooltip> callback is not a callable: %s' % callback)
		self.__item_tooltip_callback = callback

	# the callback must be a function which takes a single argument
	# the argument is the data for the item the tooltip is on
	# the callback must return None if no item tooltip is to be shown
	# otherwise it must return a string (possibly with \n)
	item_tooltip_callback = property(lambda x:x, _set_item_tooltip_callback)
	#------------------------------------------------------------
	def _set_searchable_cols(self, cols):
		# zero-based list of which columns to search
		if cols is None:
			self.__searchable_cols = range(self.ColumnCount)
			return
		# weed out columns to be searched which
		# don't exist and uniquify them
		new_cols = {}
		for col in cols:
			if col < self.ColumnCount:
				new_cols[col] = True
		self.__searchable_cols = new_cols.keys()

	searchable_columns = property(lambda x:x, _set_searchable_cols)
	#------------------------------------------------------------
	# ColumnSorterMixin API
	#------------------------------------------------------------
	def GetListCtrl(self):
		if self.itemDataMap is None:
			self._update_sorting_metadata()
		return self								# required
	#------------------------------------------------------------
	def OnSortOrderChanged(self):
		self._cleanup_column_headers()
		# annotate sort column
		col_idx, is_ascending = self.GetSortState()
		col_state = self.GetColumn(col_idx)
		col_state.m_text += self.sort_order_tags[is_ascending]
		self.SetColumn(col_idx, col_state)
	#------------------------------------------------------------
	def _generate_map_for_sorting(self):
		dict2sort = {}
		item_count = self.GetItemCount()
		if item_count == 0:
			return dict2sort
		col_count = self.GetColumnCount()
		for item_idx in range(item_count):
			dict2sort[item_idx] = ()
			if col_count == 0:
				continue
			for col_idx in range(col_count):
				dict2sort[item_idx] += (self.GetItem(item_idx, col_idx).GetText(), )

		return dict2sort
	#------------------------------------------------------------
	def _cleanup_column_headers(self):
		for col_idx in range(self.ColumnCount):
			col_state = self.GetColumn(col_idx)
			if col_state.m_text.endswith(self.sort_order_tags[True]):
				col_state.m_text = col_state.m_text[:-len(self.sort_order_tags[True])]
			if col_state.m_text.endswith(self.sort_order_tags[False]):
				col_state.m_text = col_state.m_text[:-len(self.sort_order_tags[False])]
			self.SetColumn(col_idx, col_state)
	#------------------------------------------------------------
	def _invalidate_sorting_metadata(self):
		self.itemDataMap = None
		self.SetColumnCount(self.GetColumnCount())
		self._cleanup_column_headers()
	#------------------------------------------------------------
	def _update_sorting_metadata(self):
		self.itemDataMap = self._generate_map_for_sorting()
	#------------------------------------------------------------
	def _on_col_click(self, event):
		# for debugging:
		# print "column clicked : %s" % (event.GetColumn())
		# column, order = self.GetSortState()
		# print "column %s sort %s" % (column, order)
		# print self._colSortFlag
		# print self.itemDataMap
		event.Skip()

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	sys.path.insert(0, '../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#------------------------------------------------------------
	def test_wxMultiChoiceDialog():
		app = wx.PyWidgetTester(size = (400, 500))
		dlg = wx.MultiChoiceDialog (
			parent = None,
			message = 'test message',
			caption = 'test caption',
			choices = ['a', 'b', 'c', 'd', 'e']
		)
		dlg.ShowModal()
		sels = dlg.GetSelections()
		print "selected:"
		for sel in sels:
			print sel
	#------------------------------------------------------------
	def test_get_choices_from_list():

		def edit(argument):
			print "editor called with:"
			print argument

		def refresh(lctrl):
			choices = ['a', 'b', 'c']
			lctrl.set_string_items(choices)

		app = wx.PyWidgetTester(size = (200, 50))
		chosen = get_choices_from_list (
#			msg = 'select a health issue\nfrom the list below\n',
			caption = 'select health issues',
			#choices = [['D.M.II', '4'], ['MS', '3'], ['Fraktur', '2']],
			#columns = ['issue', 'no of episodes']
			columns = ['issue'],
			refresh_callback = refresh
			#, edit_callback = edit
		)
		print "chosen:"
		print chosen
	#------------------------------------------------------------
	def test_item_picker_dlg():
		app = wx.PyWidgetTester(size = (200, 50))
		dlg = cItemPickerDlg(None, -1, msg = 'Pick a few items:')
		dlg.set_columns(['Plugins'], ['Load in workplace', 'dummy'])
		#dlg.set_columns(['Plugins'], [])
		dlg.set_string_items(['patient', 'emr', 'docs'])
		result = dlg.ShowModal()
		print result
		print dlg.get_picks()
	#------------------------------------------------------------
	#test_get_choices_from_list()
	#test_wxMultiChoiceDialog()
	test_item_picker_dlg()

#================================================================
#