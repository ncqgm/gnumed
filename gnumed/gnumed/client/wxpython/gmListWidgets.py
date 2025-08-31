"""GNUmed list controls and widgets.

TODO:

	From: Rob McMullen <rob.mcmullen@gmail.com>
	To: wxPython-users@lists.wxwidgets.org
	Subject: Re: [wxPython-users] ANN: ColumnSizer mixin for ListCtrl

	Thanks for all the suggestions, on and off line.  There's an update
	with a new name (ColumnAutoSizeMixin) and better sizing algorithm at:

	https://trac.flipturn.org/browser/trunk/peppy/lib/column_autosize.py

	sorting: https://code.activestate.com/recipes/426407/
"""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import logging
import threading
import time
import locale
import os
import csv
import re as regex
import datetime as pydt


import wx
import wx.lib.mixins.listctrl as listmixins


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.wxpython.gmGuiHelpers import decorate_window_title, undecorate_window_title


_log = logging.getLogger('gm.list_ui')

#================================================================
try:
	_WX__LIST_HITTEST_ONITEMRIGHT = wx.LIST_HITTEST_ONITEMRIGHT
except AttributeError:
	_WX__LIST_HITTEST_ONITEMRIGHT = -1
	_log.debug('this platform does not support <wx.LIST_HITTEST_ONITEMRIGHT>')

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
			close_on_activate=False,
			left_extra_button=None,
			middle_extra_button=None,
			right_extra_button=None,
			list_tooltip_callback=None):
	"""Let user select item(s) from a list.

	- new_callback: ()
	- edit_callback: (item data)
	- delete_callback: (item data)
	- refresh_callback: (listctrl)
	- activate_callback: (event)
	- list_tooltip_callback: (item data)

	- left/middle/right_extra_button: (label, tooltip, <callback> [, wants_list_ctrl])
		<wants_list_ctrl> is optional
		<callback> is called with item_data (or listctrl) as the only argument
		if <callback> returns TRUE, the listctrl will be refreshed, if a refresh_callback is available

	returns:
		on [CANCEL]: None
		on [OK]:
			if any items selected:
				if single_selection:
					the data of the selected item
				else:
					list of data of selected items
			else:
				if can_return_empty is True AND [OK] button was pressed:
					empty list
				else:
					None
	"""
	caption = decorate_window_title(gmTools.coalesce(caption, _('generic multi choice dialog')))

	dlg = cGenericListSelectorDlg(parent, -1, title = caption, msg = msg, single_selection = single_selection)
	dlg.refresh_callback = refresh_callback
	dlg.edit_callback = edit_callback
	dlg.new_callback = new_callback
	dlg.delete_callback = delete_callback
	dlg.list_tooltip_callback = list_tooltip_callback

	dlg.can_return_empty = can_return_empty
	dlg.ignore_OK_button = ignore_OK_button
	dlg.close_on_activate = close_on_activate
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
		if single_selection:
			dlg.set_selections(selections = selections[:1])
		else:
			dlg.set_selections(selections = selections)

	btn_pressed = dlg.ShowModal()
	sels = dlg.get_selected_item_data(only_one = single_selection)
	dlg.DestroyLater()
	if btn_pressed == wx.ID_OK:
		if can_return_empty and (sels is None):
			return []
		return sels

	return None

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgGenericListSelectorDlg

class cGenericListSelectorDlg(wxgGenericListSelectorDlg.wxgGenericListSelectorDlg):
	"""A dialog holding a list and a few buttons to act on the items."""

	def __init__(self, *args, **kwargs):

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError:
			msg = None

		try:
			title = kwargs['title']
		except KeyError:
			title = self.__class__.__name__
		kwargs['title'] = decorate_window_title(title)

		try:
			single_selection = kwargs['single_selection']
			del kwargs['single_selection']
		except KeyError:
			single_selection = False

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

		self.select_callback = None				# called when an item is selected, data of topmost selected item passed in
		self._LCTRL_items.select_callback = self._on_list_item_selected_in_listctrl
		self.close_on_activate = False
		self._LCTRL_items.activate_callback = self._on_list_item_activated_in_listctrl
		if single_selection:
			self._LCTRL_items.SetSingleStyle(wx.LC_SINGLE_SEL, add = True)

	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)

	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		self._LCTRL_items.set_column_widths(widths = widths)

	#------------------------------------------------------------
	def set_string_items(self, items=None, reshow=True):
		self._LCTRL_items.set_string_items(items = items, reshow = reshow)
		self._LCTRL_items.set_column_widths()
		#self._LCTRL_items.Select(0)

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
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			if not self.can_return_empty:
				self._BTN_cancel.SetDefault()
				self._BTN_ok.Enable(False)
			self._BTN_edit.Enable(False)
			self._BTN_delete.Enable(False)

		event.Skip()

	#------------------------------------------------------------
	def _on_new_button_pressed(self, event):
		self.__do_insert()
		event.Skip()

	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		# if the edit button *can* be pressed there are *supposed*
		# to be both an item selected and an editor configured
		self.__do_edit()
		event.Skip()

	#------------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		# if the delete button *can* be pressed there are *supposed*
		# to be both an item selected and a deletor configured

		no_items = len(self._LCTRL_items.get_selected_items(only_one = False))
		if no_items == 0:
			return

		if no_items > 1:
			style = wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP
			title = _('Deleting list items')
			question = _(
				'You have selected %s list items.\n'
				'\n'
				'Really delete all %s items ?'
			) % (no_items, no_items)
			dlg = wx.MessageDialog(None, question, title, style)
			btn_pressed = dlg.ShowModal()
			dlg.DestroyLater()
			if btn_pressed == wx.ID_NO:
				self._LCTRL_items.SetFocus()
				return
			if btn_pressed == wx.ID_CANCEL:
				self._LCTRL_items.SetFocus()
				return

		self.__do_delete()
		event.Skip()

	#------------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		if self.__left_extra_button_wants_list:
			item_data = self._LCTRL_items
		else:
			item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__left_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
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

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
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

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def _on_list_item_selected_in_listctrl(self, event):
		event.Skip()
		if not self.__ignore_OK_button:
			self._BTN_ok.SetDefault()
			self._BTN_ok.Enable(True)
		if self.edit_callback is not None:
			self._BTN_edit.Enable(True)
		if self.delete_callback is not None:
			self._BTN_delete.Enable(True)
		if self.__select_callback is not None:
			item = self._LCTRL_items.get_selected_item_data(only_one = True)
			self.__select_callback(item)

	#------------------------------------------------------------
	def _on_list_item_activated_in_listctrl(self, event):
		event.Skip()
		if self.__ignore_OK_button:
			return

		if not self.close_on_activate:
			return

		item = self._LCTRL_items.get_selected_item_data(only_one = True)
		if not item:
			if not self.can_return_empty:
				return

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
			return item

	#------------------------------------------------------------
	def _on_delete_key_pressed_in_listctrl(self):
		self.__do_delete()

	#------------------------------------------------------------
	def __do_delete(self):
		any_deleted = False
		for item_data in self._LCTRL_items.get_selected_item_data(only_one = False):
			if item_data is None:
				continue
			if self.__delete_callback(item_data):
				any_deleted = True

		self._LCTRL_items.SetFocus()

		if any_deleted is False:
			return

		if self.__refresh_callback is None:
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_edit_invoked_in_listctrl(self):
		self.__do_edit()

	#------------------------------------------------------------
	def __do_edit(self):
		if not self.__edit_callback(self._LCTRL_items.get_selected_item_data(only_one = True)):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_insert_key_pressed_in_listctrl(self):
		self.__do_insert()

	#------------------------------------------------------------
	def __do_insert(self):
		if not self.__new_callback():
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
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
		self._BTN_extra_left.SetToolTip(tooltip)
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
		self._BTN_extra_middle.SetToolTip(tooltip)
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
		self._BTN_extra_right.SetToolTip(tooltip)
		self._BTN_extra_right.Enable(True)
		self._BTN_extra_right.Show()

	right_extra_button = property(lambda x:x, _set_right_extra_button)

	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		if callback is not None:
			if self.__refresh_callback is None:
				raise ValueError('refresh callback must be set before new callback can be set')
			if not callable(callback):
				raise ValueError('<new> callback is not a callable: %s' % callback)
		self.__new_callback = callback

		if callback is None:
			self._BTN_new.Enable(False)
			self._BTN_new.Hide()
			self._LCTRL_items.new_callback = None
		else:
			self._BTN_new.Enable(True)
			self._BTN_new.Show()
			self._LCTRL_items.new_callback = self._on_insert_key_pressed_in_listctrl

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
			self._LCTRL_items.edit_callback = None
		else:
			self._BTN_edit.Enable(True)
			self._BTN_edit.Show()
			self._LCTRL_items.edit_callback = self._on_edit_invoked_in_listctrl

	edit_callback = property(_get_edit_callback, _set_edit_callback)

	#------------------------------------------------------------
	def _get_delete_callback(self):
		return self.__delete_callback

	def _set_delete_callback(self, callback):
		if callback is not None:
			if self.__refresh_callback is None:
				raise ValueError('refresh callback must be set before delete callback can be set')
			if not callable(callback):
				raise ValueError('<delete> callback is not a callable: %s' % callback)
		self.__delete_callback = callback
		if callback is None:
			self._BTN_delete.Enable(False)
			self._BTN_delete.Hide()
			self._LCTRL_items.delete_callback = None
		else:
			self._BTN_delete.Enable(True)
			self._BTN_delete.Show()
			self._LCTRL_items.delete_callback = self._on_delete_key_pressed_in_listctrl

	delete_callback = property(_get_delete_callback, _set_delete_callback)

	#------------------------------------------------------------
	def _get_refresh_callback(self):
		return self.__refresh_callback

	def _set_refresh_callback_helper(self):
		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	def _set_refresh_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<refresh> callback is not a callable: %s' % callback)
		self.__refresh_callback = callback
		if callback is not None:
			wx.CallAfter(self._set_refresh_callback_helper)

	refresh_callback = property(_get_refresh_callback, _set_refresh_callback)

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

		self.left_extra_button = None
		self.middle_extra_button = None
		self.right_extra_button = None

		# new/edit/delete must return True/False to enable refresh
		self.refresh_callback = None			# called when new/edit/delete callbacks return True (IOW were not cancelled)
		self.new_callback = None				# called when NEW button pressed, no argument passed in
		self.edit_callback = None				# called when EDIT button pressed, data of topmost selected item passed in
		self.delete_callback = None				# called when DELETE button pressed, data of topmost selected item passed in

		self.select_callback = None				# called when an item is selected, data of topmost selected item passed in
		self._LCTRL_items.select_callback = self._on_list_item_selected_in_listctrl

	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)

	#------------------------------------------------------------
	def set_string_items(self, items=None, reshow=True):
		self._LCTRL_items.set_string_items(items = items, reshow = reshow)
		self._LCTRL_items.set_column_widths()

		if (items is None) or (len(items) == 0):
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
		#else:
		#	self._LCTRL_items.Select(0)

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
	# internal helpers
	#------------------------------------------------------------
	def _on_list_item_selected_in_listctrl(self, event):
		event.Skip()
		if self.__edit_callback is not None:
			self._BTN_edit.Enable(True)
		if self.__delete_callback is not None:
			self._BTN_remove.Enable(True)
		if self.__select_callback is not None:
			item = self._LCTRL_items.get_selected_item_data(only_one = True)
			self.__select_callback(item)

	#------------------------------------------------------------
	def _on_delete_key_pressed_in_listctrl(self):
		self.__do_delete()

	#------------------------------------------------------------
	def __do_delete(self):
		if self.__delete_callback is None:
			return

		item = self._LCTRL_items.get_selected_item_data(only_one = True)
		if item is None:
			return

		if not self.__delete_callback(item):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_edit_invoked_in_listctrl(self):
		self.__do_edit()

	#------------------------------------------------------------
	def __do_edit(self):
		if self.__edit_callback is None:
			return

		item = self._LCTRL_items.get_selected_item_data(only_one = True)
		if item is None:
			return

		if not self.__edit_callback(item):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_insert_key_pressed_in_listctrl(self):
		self.__do_insert()

	#------------------------------------------------------------
	def __do_insert(self):
		if self.__new_callback is None:
			return

		if not self.__new_callback():
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		event.Skip()
		if self._LCTRL_items.get_selected_items(only_one = True) == -1:
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
			if self.__select_callback is not None:
				self.__select_callback(None)

	#------------------------------------------------------------
	def _on_list_item_activated(self, event):
		event.Skip()
		self._on_edit_button_pressed(event)

	#------------------------------------------------------------
	def _on_add_button_pressed(self, event):
		self.__do_insert()

	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		self.__do_edit()

	#------------------------------------------------------------
	def _on_remove_button_pressed(self, event):
		self.__do_delete()

	#------------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one = True)
		if not self.__left_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_middle_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one = True)
		if not self.__middle_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	def _on_right_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__right_extra_button_callback(item_data):
			self._LCTRL_items.SetFocus()
			return

		if self.__refresh_callback is None:
			self._LCTRL_items.SetFocus()
			return

		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.SetFocus()

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		if callback is not None:
			if self.__refresh_callback is None:
				raise ValueError('refresh callback must be set before new callback can be set')
			if not callable(callback):
				raise ValueError('<new> callback is not a callable: %s' % callback)
		self.__new_callback = callback

		if callback is None:
			self._BTN_add.Enable(False)
			self._BTN_add.Hide()
			self._LCTRL_items.new_callback = None
		else:
			self._BTN_add.Enable(True)
			self._BTN_add.Show()
			self._LCTRL_items.new_callback = self._on_insert_key_pressed_in_listctrl

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
			self._LCTRL_items.edit_callback = None
		else:
			self._BTN_edit.Enable(True)
			self._BTN_edit.Show()
			self._LCTRL_items.edit_callback = self._on_edit_invoked_in_listctrl

	edit_callback = property(_get_edit_callback, _set_edit_callback)

	#------------------------------------------------------------
	def _get_delete_callback(self):
		return self.__delete_callback

	def _set_delete_callback(self, callback):
		if callback is not None:
			if self.__refresh_callback is None:
				raise ValueError('refresh callback must be set before delete callback can be set')
			if not callable(callback):
				raise ValueError('<delete> callback is not a callable: %s' % callback)
		self.__delete_callback = callback
		if callback is None:
			self._BTN_remove.Enable(False)
			self._BTN_remove.Hide()
			self._LCTRL_items.delete_callback = None
		else:
			self._BTN_remove.Enable(True)
			self._BTN_remove.Show()
			self._LCTRL_items.delete_callback = self._on_delete_key_pressed_in_listctrl

	delete_callback = property(_get_delete_callback, _set_delete_callback)

	#------------------------------------------------------------
	def _get_refresh_callback(self):
		return self.__refresh_callback

	def _set_refresh_callback_helper(self):
		wx.BeginBusyCursor()
		self._LCTRL_items.RememberItemSelection()
		try:
			self.__refresh_callback(lctrl = self._LCTRL_items)
			self._LCTRL_items.RestoreItemSelection()
			self._LCTRL_items.set_column_widths()
		finally:
			wx.EndBusyCursor()

	def _set_refresh_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<refresh> callback is not a callable: %s' % callback)
		self.__refresh_callback = callback
		if callback is not None:
			wx.CallAfter(self._set_refresh_callback_helper)

	refresh_callback = property(_get_refresh_callback, _set_refresh_callback)

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
			self._LBL_message.SetLabel('')
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
		self._BTN_extra_left.SetToolTip(tooltip)
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
		self._BTN_extra_middle.SetToolTip(tooltip)
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
		self._BTN_extra_right.SetToolTip(tooltip)
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

		try:
			title = kwargs['title']
		except KeyError:
			title = self.__class__.__name__
		kwargs['title'] = decorate_window_title(title)

		wxgItemPickerDlg.wxgItemPickerDlg.__init__(self, *args, **kwargs)

		if msg is None:
			self._LBL_msg.Hide()
		else:
			self._LBL_msg.SetLabel(msg)

		self.ignore_dupes_on_picking = True

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
			return

		if len(columns_right) < len(columns):
			cols = columns
		else:
			cols = columns_right[:len(columns)]
		self._LCTRL_right.set_columns(columns = cols)

	#------------------------------------------------------------
	def set_string_items(self, items=None, reshow=True):
		self._LCTRL_left.set_string_items(items = items, reshow = reshow)
		self._LCTRL_left.set_column_widths()
		self._LCTRL_right.set_string_items(reshow = False)

		self._BTN_left2right.Enable(False)
		self._BTN_right2left.Enable(False)

	#------------------------------------------------------------
	def set_selections(self, selections = None):
		self._LCTRL_left.set_selections(selections = selections)

	#------------------------------------------------------------
	def set_choices(self, choices=None, data=None, reshow=True):
		self.set_string_items(items = choices, reshow = reshow)
		if data is not None:
			self.set_data(data = data)

	#------------------------------------------------------------
	def set_picks(self, picks=None, data=None, reshow=True):
		self._LCTRL_right.set_string_items(picks, reshow = reshow)
		self._LCTRL_right.set_column_widths()
		if data is not None:
			self._LCTRL_right.set_data(data = data)

	#------------------------------------------------------------
	def set_data(self, data = None):
		self._LCTRL_left.set_data(data = data)

	#------------------------------------------------------------
	def get_picks(self):
		return self._LCTRL_right.get_item_data()

	picks = property(get_picks)

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
		self._BTN_extra.SetToolTip(tooltip)
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

		if self.ignore_dupes_on_picking is False:
			right_items.extend(selected_items)
			right_data.extend(selected_data)
			self._LCTRL_right.set_string_items(items = right_items, reshow = True)
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
		self._LCTRL_right.set_string_items(items = right_items, reshow = True)
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
# listctrl mixins
#----------------------------------------------------------------
class cColumnSorterMixin:
	"""
	A mixin class that handles sorting of a wx.ListCtrl in REPORT mode when
	the column header is clicked on.

	There are a few requirements needed in order for this to work generically:

	  1. Items in the list control must have a unique data value set
		 with list.SetItemData.

	  2. The combined class must provide a method <_generate_map_for_sorting>
		 which produces a dictionary keyed by row idx with each entry being a
		 sequence of strings representing the value in each column of that row.

	Interesting methods to override are GetColumnSorter,
	GetSecondarySortValues, and GetSortImages.	See below for details.

	Lifted from wx.lib.mixins.listctrl and adapted.
	"""
	sort_order_tags = {
		True: ' \u2193',
		False: ' \u2191'
	}
	#------------------------------------------------------------
	def __init__(self, numColumns):
		method_needed = '_generate_map_for_sorting'
		assert(isinstance(self, wx.ListCtrl)), '<%s> must be mixed in with a wx.ListCtrl descendant' % self.__class__
		assert(hasattr(self, method_needed)), '<%s> must have a method <%s>' % (self, method_needed)

		self.itemDataMap = None
		self.__previous_sort_state = None
		self.SetColumnCount(numColumns)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.__on_col_click, self)

		try:
			self.RememberItemSelection
			self.__retain_selection_state = True
		except AttributeError:
			_log.exception('cannot enable item selection retainment across sorts, cannot detect SelectionStateMixin via <RememberItemSelection>')
			self.__retain_selection_state = False

	#------------------------------------------------------------
	def SetColumnCount(self, newNumColumns):
		self._colSortFlag = [0] * newNumColumns
		self._col = -1

	#------------------------------------------------------------
	def SortListItems(self, col=-1, ascending=1):
		"""Sort the list on demand.	 Can also be used to set the sort column and order."""
		oldCol = self._col
		if col != -1:
			self._col = col
			self._colSortFlag[col] = ascending
		if self.__retain_selection_state:
			self.RememberItemSelection()
		self._update_sorting_metadata()
		self.SortItems(self.GetColumnSorter())
		if self.__retain_selection_state:
			self.RestoreItemSelection()
		self.__updateImages(oldCol)
		self.update_sorting_indicator()

	#------------------------------------------------------------
	def GetColumnWidths(self):
		"""
		Returns a list of column widths.  Can be used to help restore the current
		view later.
		"""
		rv = []
		for x in range(len(self._colSortFlag)):
			rv.append(self.GetColumnWidth(x))
		return rv

	#------------------------------------------------------------
	def GetSortImages(self):
		"""
		Returns a tuple of image list indexesthe indexes in the image list for an image to be put on the column
		header when sorting in descending order.
		"""
		return (-1, -1)	 # (descending, ascending) image IDs

	#------------------------------------------------------------
	def GetColumnSorter(self):
		"""Returns a callable object to be used for comparing column values when sorting."""
		return self.__ColumnSorter

	#------------------------------------------------------------
	def GetSecondarySortValues(self, col, key1, key2):
		"""Returns a tuple of 2 values to use for secondary sort values when the
		   items in the selected column match equal.  The default just returns the
		   item data values."""
		return (key1, key2)

	#------------------------------------------------------------
	def __on_col_click(self, evt):
		evt.Skip()
		oldCol = self._col
		self._col = evt.GetColumn()
		self._colSortFlag[self._col] = int(not self._colSortFlag[self._col])
		if self.__retain_selection_state:
			self.RememberItemSelection()
		self._update_sorting_metadata()
		self.SortItems(self.GetColumnSorter())
		if self.__retain_selection_state:
			self.RestoreItemSelection()
		if wx.Platform != "__WXMAC__" or wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") == 1:
			self.__updateImages(oldCol)
		self.update_sorting_indicator()
		self.OnSortOrderChanged()

	#------------------------------------------------------------
	def OnSortOrderChanged(self):
		"""
		Callback called after sort order has changed (whenever user
		clicked column header).
		"""
		pass

	#------------------------------------------------------------
	def __ColumnSorter(self, key1, key2):
		col = self._col
		ascending = self._colSortFlag[col]
		item1 = self.itemDataMap[key1][col]
		item2 = self.itemDataMap[key2][col]
		cmpVal = locale.strcoll(item1, item2)
		if cmpVal == 0:
			cmpVal = self._cmp(*self.GetSecondarySortValues(col, key1, key2))
		if ascending:
			return cmpVal
		else:
			return -cmpVal

	#------------------------------------------------------------
	def __updateImages(self, oldCol):
		sortImages = self.GetSortImages()
		if self._col != -1 and sortImages[0] != -1:
			img = sortImages[self._colSortFlag[self._col]]
			self._update_sorting_metadata()
			if oldCol != -1:
				self.ClearColumnImage(oldCol)
			self.SetColumnImage(self._col, img)

	#------------------------------------------------------------
	# sorting state API
	#------------------------------------------------------------
	def GetSortState(self):
		"""
		Return a tuple containing the index of the column that was last sorted
		and the sort direction of that column.
		Usage:
		col, ascending = self.GetSortState()
		# Make changes to list items... then resort
		self.SortListItems(col, ascending)
		"""
		return (self._col, self._colSortFlag[self._col])

	#------------------------------------------------------------
	def RememberSortState(self):
		self.__previous_sort_state = self.GetSortState()

	#------------------------------------------------------------
	def RestoreSortState(self):
		if self.__previous_sort_state is None:
			return

		self.SortListItems(*self.__previous_sort_state)

	#------------------------------------------------------------
	# sorting indicator handling
	#------------------------------------------------------------
	def remove_sorting_indicators_from_column_labels(self):
		for col_idx in range(self.ColumnCount):
			self._remove_sorting_indicator_from_column_label(col_idx)

	#------------------------------------------------------------
	def update_sorting_indicator(self):
		self.remove_sorting_indicators_from_column_labels()
		if self._col == -1:
			return

		col_state = self.GetColumn(self._col)
		col_state.Text += self.sort_order_tags[self._colSortFlag[self._col]]
		self.SetColumn(self._col, col_state)

	#------------------------------------------------------------
	def __remove_sorting_indicator(self, text):
		for tag in self.sort_order_tags.values():
			if text.endswith(tag):
				text = text[:-len(tag)]
		return text

	#------------------------------------------------------------
	def _remove_sorting_indicator_from_column_label(self, col_idx):
		assert (col_idx > -1), '<col_idx> must be non-negative integer'
		if col_idx > self.ColumnCount:
			_log.warning('<col_idx>=%s, but .ColumnCount=%s', col_idx, self.ColumnCount)
			return

		col_state = self.GetColumn(col_idx)
		cleaned_header = self.__remove_sorting_indicator(col_state.Text)
		if col_state.Text == cleaned_header:
			return

		col_state.Text = cleaned_header
		self.SetColumn(col_idx, col_state)

	#------------------------------------------------------------
	# sorting metadata API
	#------------------------------------------------------------
	def invalidate_sorting_metadata(self):
		"""Mark sorting metadata as invalid.

		To be called whenever list data changes.
		"""
		self.itemDataMap = None
		self.SetColumnCount(self.ColumnCount)
		self.remove_sorting_indicators_from_column_labels()

	#------------------------------------------------------------
	def _update_sorting_metadata(self):
		"""Update the sorting metadata.

		Calls _generate_map_for_sorting in the combined class
		IF the metadata has been invalidated before.
		"""
		if self.itemDataMap is not None:
			return

		self.itemDataMap = self._generate_map_for_sorting()

	#------------------------------------------------------------
	# generic helper code
	#------------------------------------------------------------
	def _cmp(self, a, b):
		return (a > b) - (a < b)

#================================================================
class SelectionStateMixin:
	"""This mixin allows saving/restoring selection state."""

	def __init__(self):
		assert(isinstance(self, wx.ListCtrl)), '<%s> must be mixed in with wx.ListCtrl'
		self.__previously_selected_items = []
		self.__item_identity_callback = None

	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def RememberItemSelection(self):
		"""Remember the currently selected items."""
		self.__previously_selected_items = []
		if self.ItemCount == 0:
			return

		if self.__item_identity_callback is None:
			return

		for sel_idx in self.__get_item_selections():
			self.__previously_selected_items.append(self.__item_identity_callback(sel_idx))

	#------------------------------------------------------------
	def RestoreItemSelection(self):
		"""Restore (a remembered) item selection (if any)."""
		if not self.__previously_selected_items:
			return

		if self.ItemCount == 0:
			return

		if self.__item_identity_callback is None:
			return

		for item_idx in range(self.ItemCount):
			if self.__item_identity_callback(item_idx) in self.__previously_selected_items:
				self.Select(idx = item_idx, on = 1)
			else:
				self.Select(idx = item_idx, on = 0)

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def __get_item_identity_callback(self):
		"""The function to call for retrieving the identity of a list item."""
		return self.__item_identity_callback

	def __set_item_identity_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<ItemIdentityCallback> is neither None nor callable: %s' % callback)

		self.__item_identity_callback = callback

	ItemIdentityCallback = property(__get_item_identity_callback, __set_item_identity_callback)

	#------------------------------------------------------------
	# helpers
	#------------------------------------------------------------
	def __get_item_selections(self):
		if self.ItemCount == 0:
			return []

		selections = []
		idx = self.GetFirstSelected()
		while idx != -1:
			selections.append(idx)
			idx = self.GetNextSelected(idx)
		return selections

#================================================================
class DnDMixin:
	"""This mixin enables drag and drop of list items."""

	def __init__(self):
		assert(isinstance(self, wx.ListCtrl)), '<%s> must be mixed in with wx.ListCtrl'
		self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDragInit, id = self.GetId())

	#------------------------------------------------------------
	def OnDragInit(self, evt):
		evt.Skip()
		drag_data = self.get_drag_data_object()
		if drag_data is None:
			return

		src = wx.DropSource(self)
		src.SetData(drag_data)
		src.DoDragDrop(True)

	#------------------------------------------------------------
	def get_drag_data_object(self):
		"""Get data to be dragged.

		Returns:
			A drag data object, or None if nothing is to be dragged.

		Override to provide whatever data is to be dragged.
		The overrider itself can provide a default or call
		some external callback.
		"""
		return None

#================================================================
class cReportListCtrl(DnDMixin, listmixins.ListCtrlAutoWidthMixin, cColumnSorterMixin, SelectionStateMixin, wx.ListCtrl):

	# sorting: at set_string_items() time all items will be
	# adorned with their initial row number as wxPython data,
	# this is used later for a) sorting and b) to access
	# GNUmed data objects associated with rows,
	# the latter are ordered in initial row number order
	# at set_data() time

	def __init__(self, *args, **kwargs):

		self.debug = None
		self.map_item_idx2data_idx = self.GetItemData

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) == wx.LC_SINGLE_SEL)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		SelectionStateMixin.__init__(self)
		cColumnSorterMixin.__init__(self, 0)
		self.invalidate_sorting_metadata()
		self.__secondary_sort_col = None
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
		DnDMixin.__init__(self)

		# cols/rows
		self.__widths = None
		self.__data = None

		# event callbacks
		self.__select_callback = None
		self.__deselect_callback = None
		self.__activate_callback = None
		self.__new_callback = None
		self.__edit_callback = None
		self.__delete_callback = None
		self.__dnd_callback = None

		# context menu
		self.__extend_popup_menu_callback = None
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_list_item_rightclicked)	# (also handled by MENU key on EVT_LIST_KEY_DOWN)

		# row tooltips
		self.__item_tooltip_callback = None
		self.__tt_last_item = None
		self.__tt_static_part_base = ''
		self.__tt_static_part = self.__tt_static_part_base
		self.Bind(wx.EVT_MOTION, self._on_mouse_motion)

		# search related:
		self.__search_term = None
		self.__next_line_to_search = 0
		self.__searchable_cols = None

		# general event handling
#		self.Bind(wx.EVT_KILL_FOCUS, self._on_lost_focus)
		self.Bind(wx.EVT_CHAR, self._on_char)						# CTRL-F / CTRL-N (LIST_KEY_DOWN does not support modifiers)
		self.Bind(wx.EVT_LIST_KEY_DOWN, self._on_list_key_down)		# context menu key -> context menu / DEL / INS

	#------------------------------------------------------------
	# debug sizing
	#------------------------------------------------------------
	def __log_sizing(self, caller_name, *args, **kwargs):
		if self.debug is None:
			return False
		if not self.debug.endswith('_sizing'):
			return False
		_log.debug('[%s.%s]: *args = (%s), **kwargs = (%s)', self.debug, caller_name, str(args), str(kwargs))
		return True

	#------------------------------------------------------------
	def CacheBestSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).CacheBestSize(*args, **kwargs)

	#------------------------------------------------------------
	def Fit(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).Fit(*args, **kwargs)

	#------------------------------------------------------------
	def FitInside(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).FitInside(*args, **kwargs)

	#------------------------------------------------------------
	def InvalidateBestSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).InvalidateBestSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetBestFittingSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetBestFittingSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetInitialSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetInitialSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetClientSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetClientSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetClientSizeWH(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetClientSizeWH(*args, **kwargs)

	#------------------------------------------------------------
	def SetMaxClientSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetMaxClientSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetMaxSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetMaxSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetMinClientSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetMinClientSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetMinSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetMinSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetSizeHints(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetSizeHints(*args, **kwargs)

	#------------------------------------------------------------
	def SetSizeHintsSz(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetSizeHintsSz(*args, **kwargs)

	#------------------------------------------------------------
	def SetSizeWH(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetSizeWH(*args, **kwargs)

	#------------------------------------------------------------
	def SetVirtualSize(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetVirtualSize(*args, **kwargs)

	#------------------------------------------------------------
	def SetVirtualSizeHints(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetVirtualSizeHints(self, *args, **kwargs)

	#------------------------------------------------------------
	def SetVirtualSizeHintsSz(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetVirtualSizeHintsSz(*args, **kwargs)

	#------------------------------------------------------------
	def SetVirtualSizeWH(self, *args, **kwargs):
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return super(cReportListCtrl, self).SetVirtualSizeWH(*args, **kwargs)

	#------------------------------------------------------------
	def GetAdjustedBestSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetAdjustedBestSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetEffectiveMinSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetEffectiveMinSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetBestSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetBestSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetBestSizeTuple(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetBestSizeTuple(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetBestVirtualSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetBestVirtualSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

#	#------------------------------------------------------------
#	def GetClientSize(self, *args, **kwargs):
#		res = super(cReportListCtrl, self).GetClientSize(*args, **kwargs)
#		kwargs['sizing_function_result'] = res
#		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
#		return res

	#------------------------------------------------------------
	def GetClientSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetClientSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMaxClientSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMaxClientSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMaxHeight(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMaxHeight(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMaxSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMaxSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMaxWidth(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMaxWidth(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMinClientSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMinClientSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMinHeight(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMinHeight(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMinSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMinSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetMinWidth(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetMinWidth(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetVirtualSize(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetVirtualSize(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

	#------------------------------------------------------------
	def GetVirtualSizeTuple(self, *args, **kwargs):
		res = super(cReportListCtrl, self).GetVirtualSizeTuple(*args, **kwargs)
		kwargs['sizing_function_result'] = res
		self.__log_sizing(sys._getframe().f_code.co_name, *args, **kwargs)
		return res

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
		self.invalidate_sorting_metadata()

	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		"""Set the column width policy.

		widths = None:
			use previous policy if any or default policy
		widths != None:
			use this policy and remember it for later calls

		options:
			wx.LIST_AUTOSIZE_USEHEADER
			wx.LIST_AUTOSIZE

		This means there is no way to *revert* to the default policy :-(
		"""
		if widths:
			# explicit policy ?
			self.__widths = widths
			for idx in range(len(self.__widths)):
				self.SetColumnWidth(idx, self.__widths[idx])
			return

		# previous policy ?
		if self.__widths:
			for idx in range(len(self.__widths)):
				self.SetColumnWidth(idx, self.__widths[idx])
			return

		# default policy !
		if self.GetItemCount() == 0:
			width_type = wx.LIST_AUTOSIZE_USEHEADER
		else:
			width_type = wx.LIST_AUTOSIZE
		for idx in range(self.GetColumnCount()):
			self.SetColumnWidth(idx, width_type)

	#------------------------------------------------------------
	def set_resize_column(self, column='LAST'):
		if column != 'LAST':
			if column > self.ColumnCount:
				return
		# this column will take up all remaining space courtesy of the width mixin
		self.setResizeColumn(column)

	#------------------------------------------------------------
	def set_column_label(self, col_idx, label):
		assert(col_idx > -1), '<col_idx> must be positive integer'
		if col_idx > self.ColumnCount:
			_log.warning('<col_idx>=%s, .ColumnCount=%s', col_idx, self.ColumnCount)
			return

		col_state = self.GetColumn(col_idx)
		col_state.Text = label
		self.SetColumn(col_idx, col_state)
		self.update_sorting_indicator()

	#------------------------------------------------------------
	def remove_items_safely(self, max_tries=3):
		self.invalidate_sorting_metadata()
		tries = 0
		while tries < max_tries:
			if self.debug is not None:
				if self.debug.endswith('_deleting'):
					_log.debug('[round %s] <%s>.GetItemCount() before DeleteAllItems(): %s (thread [%s])', tries, self.debug, self.GetItemCount(), threading.get_native_id())
			if not self.DeleteAllItems():
				_log.error('<%s>.DeleteAllItems() failed', self.debug)
			item_count = self.GetItemCount()
			if item_count == 0:
				return True

			wx.SafeYield(None, True)
			_log.error('<%s>.GetItemCount() not 0 (rather: %s) after DeleteAllItems()', self.debug, item_count)
			time.sleep(0.3)
			wx.SafeYield(None, True)
			tries += 1

		_log.error('<%s>: unable to delete list items after looping %s times', self.debug, max_tries)
		return False

	#------------------------------------------------------------
	def set_string_items(self, items=None, reshow=True, unwrap:bool=True):
		"""All item members must be str()able or None.

		Args:
			reshow: whether to ensure the previously top-most visible item is visible again after updating the list
			unwrap: whether to unfold multi-line text into a single line
		"""
		wx.BeginBusyCursor()
		self.invalidate_sorting_metadata()

		if self.ItemCount == 0:
			topmost_visible = 0
		else:
			topmost_visible = self.GetFirstSelected()
			if topmost_visible == -1:
				topmost_visible = self.GetFocusedItem()
			if topmost_visible == -1:
				topmost_visible = self.TopItem

		if not self.remove_items_safely(max_tries = 3):
			_log.error("cannot remove items (!?), continuing and hoping for the best")

		if items is None:
			self.data = None
			wx.EndBusyCursor()
			return

		# insert new items
		for item in items:
			# item is a single string
			# (typical special case: items=rows are a list-of-strings)
			if isinstance(item, str):
				self.InsertItem(sys.maxsize, item.replace('\r\n', ' [CRLF] ').replace('\n', ' [LF] '))
				continue
			# item is something else, either ...
			try:
				# ... an iterable
				col_val = str(item[0])
				row_num = self.InsertItem(sys.maxsize, col_val)
				for col_num in range(1, min(self.GetColumnCount(), len(item))):
					col_val = str(item[col_num]).replace('\r\n', ' [CRLF] ').replace('\n', ' [LF] ')
					self.SetItem(row_num, col_num, col_val)
			except (TypeError, KeyError, IndexError):
				# ... an *empty* iterable [IndexError]
				# ... or not iterable (None, int, instance, dict [KeyError] ...)
				col_val = str(item).replace('\r\n', ' [CRLF] ').replace('\n', ' [LF] ')
				self.InsertItem(sys.maxsize, col_val)

		if reshow:
			if self.ItemCount > 0:
				if topmost_visible < self.ItemCount:
					self.EnsureVisible(topmost_visible)
					self.Focus(topmost_visible)
				else:
					self.EnsureVisible(self.ItemCount - 1)
					self.Focus(self.ItemCount - 1)

		# set data to be a copy of items
		self.data = items

		wx.EndBusyCursor()

	#--------------------------
	def get_string_items(self):
		if self.ItemCount == 0:
			return []

		rows = []
		for row_idx in range(self.ItemCount):
			row = []
			for col_idx in range(self.ColumnCount):
				row.append(self.GetItem(row_idx, col_idx).GetText())
			rows.append(row)
		return rows

		# old: only returned first column
		#return [ self.GetItemText(item_idx) for item_idx in range(self.GetItemCount()) ]

	string_items = property(get_string_items, set_string_items)

	#------------------------------------------------------------
	def append_string_items_and_data(self, new_items, new_data=None, allow_dupes=False):
		if len(new_items) == 0:
			return

		if new_data is None:
			new_data = new_items

		existing_data = self.get_item_data()
		if existing_data is None:
			existing_data = []

		if allow_dupes:
			self.set_string_items (
				items = self.string_items.extend(new_items),
				reshow = True
			)
			self.data = existing_data.extend(new_data)
			self.set_column_widths()
			return

		existing_items = self.get_string_items()
		for new_item, new_data in zip(new_items, new_data):
			if new_item in existing_items:
				continue
			existing_items.append(new_item)
			existing_data.append(new_data)
		self.set_string_items (
			items = existing_items,
			reshow = True
		)
		self.data = existing_data
		self.set_column_widths()

	#------------------------------------------------------------
	def set_data(self, data=None):
		"""<data> assumed to be a list corresponding to the item indices"""
		if data is not None:
			item_count = self.GetItemCount()
			if len(data) != item_count:
				_log.debug('<data> length (%s) must be equal to number of list items (%s)  (%s, thread [%s])', len(data), item_count, self.debug, threading.get_native_id())
			for item_idx in range(len(data)):
				self.SetItemData(item_idx, item_idx)
		self.__data = data
		self.__tt_last_item = None
		# string data (rows/visible list items) not modified,
		# so no need to call invalidate_sorting_metadata
		return

	def _get_data(self):
		# slower than "return self.__data" but helps with detecting
		# problems with len(__data) != self.GetItemCount(),
		# also takes care of returning data in the order corresponding
		# to the order get_string_items returns rows
		return self.get_item_data() 		# returns all data since item_idx is None

	data = property(_get_data, set_data)

	#------------------------------------------------------------
	def set_selections(self, selections=None):
		# not sure why this is done:
		if self.ItemCount > 0:
			self.Select(0, on = 0)
		if selections is None:
			return

		for idx in selections:
			self.Select(idx = idx, on = 1)

	def __get_selections(self):
		if self.ItemCount == 0:
			return []

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
		for col_idx in range(self.ColumnCount):
			col = self.GetColumn(col = col_idx)
			labels.append(col.Text)
		return labels

	column_labels = property(get_column_labels)

	#------------------------------------------------------------
	def get_item(self, item_idx=None):
		if item_idx == -1:
			return None

		if self.ItemCount == 0:
			_log.warning('no items')
			return None

		if item_idx is not None:
			return self.GetItem(item_idx)

		_log.error('get_item(None) called')
		return None

	#------------------------------------------------------------
	def get_items(self):
		if self.ItemCount == 0:
			return []
		return [ self.GetItem(item_idx) for item_idx in range(self.ItemCount) ]

	items = property(get_items)

	#------------------------------------------------------------
	def get_selected_items(self, only_one=False):
		if self.ItemCount == 0:
			if self.__is_single_selection or only_one:
				return None
			return []

		if self.__is_single_selection or only_one:
			selected = self.GetFirstSelected()
			if selected == -1:
				return None
			return selected

		items = []
		idx = self.GetFirstSelected()
		while idx != -1:
			items.append(idx)
			idx = self.GetNextSelected(idx)
		return items

	selected_items = property(get_selected_items)

	#------------------------------------------------------------
	def get_selected_string_items(self, only_one=False):

		if self.ItemCount == 0:
			if self.__is_single_selection or only_one:
				return None
			return []

		if self.__is_single_selection or only_one:
			return self.GetItemText(self.GetFirstSelected())

		items = []
		idx = self.GetFirstSelected()
		while idx != -1:
			items.append(self.GetItemText(idx))
			idx = self.GetNextSelected(idx)

		return items

	selected_string_items = property(get_selected_string_items)

	#------------------------------------------------------------
	def get_item_data(self, item_idx=None):

		if self.__data is None:	# this isn't entirely clean
			return None

		if item_idx is not None:
			return self.__data[self.map_item_idx2data_idx(item_idx)]

		# if <idx> is None return all data up to item_count,
		# in case of len(__data) != self.GetItemCount() this
		# gives the chance to figure out what is going on
		return [ self.__data[self.map_item_idx2data_idx(item_idx)] for item_idx in range(self.GetItemCount()) ]

	item_data = property(get_item_data)

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

	selected_item_data = property(get_selected_item_data)

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
		self.invalidate_sorting_metadata()

	#------------------------------------------------------------
	# checked items interface
	#------------------------------------------------------------
	def get_checked_items(self):
		if self.ItemCount == 0:
			return []

		return [ item_idx for item_idx in range(self.ItemCount) if self.IsItemChecked(item_idx) ]

	checked_items = property(get_checked_items)

	#------------------------------------------------------------
	def get_checked_items_data(self):
		if self.ItemCount == 0:
			return []

		return [ self.__data[self.map_item_idx2data_idx(item_idx)] for item_idx in range(self.ItemCount) if self.IsItemChecked(item_idx) ]

	checked_items_data = property(get_checked_items_data)

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __show_context_menu(self, item_idx):

		if item_idx == -1:
			return

		if self.ItemCount == 0:
			return

		# generate data for access from menu item handlers
		col_headers = []
		self._rclicked_row_idx = item_idx
		self._rclicked_row_data = self.get_item_data(item_idx = self._rclicked_row_idx)
		self._rclicked_row_cells = []
		self._rclicked_row_cells_w_hdr = []
		for col_idx in range(self.ColumnCount):
			cell_content = self.GetItem(self._rclicked_row_idx, col_idx).Text.strip()
			col_header = self.GetColumn(col_idx).Text.strip()
			col_headers.append(col_header)
			self._rclicked_row_cells.append(cell_content)
			self._rclicked_row_cells_w_hdr.append('%s: %s' % (col_header, cell_content))
		# build context menu
		items = self.selected_items
		if self.__is_single_selection:
			if items is None:
				no_of_selected_items = 0
			else:
				no_of_selected_items = 1
		else:
			no_of_selected_items = len(items)
		if no_of_selected_items == 0:
			title = _('List Item Actions')
		elif no_of_selected_items == 1:
			title = _('List Item Actions (selected: 1 entry)')
		else:
			title = _('List Item Actions (selected: %s entries)') % no_of_selected_items
		self._context_menu = wx.Menu(title = title)
		needs_separator = False
		if self.__new_callback is not None:
			menu_item = self._context_menu.Append(-1, _('Add (<INS>)'))
			self.Bind(wx.EVT_MENU, self._on_add_row, menu_item)
			needs_separator = True
		if self.__edit_callback is not None:
			menu_item = self._context_menu.Append(-1, _('&Edit'))
			self.Bind(wx.EVT_MENU, self._on_edit_row, menu_item)
			needs_separator = True
		if self.__delete_callback is not None:
			menu_item = self._context_menu.Append(-1, _('Delete (<DEL>)'))
			self.Bind(wx.EVT_MENU, self._on_delete_row, menu_item)
			needs_separator = True
		if needs_separator:
			self._context_menu.AppendSeparator()
		menu_item = self._context_menu.Append(-1, _('Find (<CTRL-F>)'))
		self.Bind(wx.EVT_MENU, self._on_show_search_dialog, menu_item)
		if self.__search_term is not None:
			if self.__search_term.strip() != '':
				menu_item = self._context_menu.Append(-1, _('Find next [%s] (<CTRL-N>)') % self.__search_term)
				self.Bind(wx.EVT_MENU, self._on_search_match, menu_item)
		self._context_menu.AppendSeparator()
		# save to file
		# - all rows
		save_all_menu = wx.Menu()
		menu_item = save_all_menu.Append(-1, _('as &text'))
		self.Bind(wx.EVT_MENU, self._all_rows2file, menu_item)
		menu_item = save_all_menu.Append(-1, _('as &CSV'))
		self.Bind(wx.EVT_MENU, self._all_rows2csv, menu_item)
		menu_item = save_all_menu.Append(-1, _('as t&ooltips'))
		self.Bind(wx.EVT_MENU, self._all_row_tooltips2file, menu_item)
		menu_item = save_all_menu.Append(-1, _('as &data'))
		self.Bind(wx.EVT_MENU, self._all_row_data2file, menu_item)
		save_menu = wx.Menu()
		save_menu.Append(-1, _('&all rows ...'), save_all_menu)
		# - selected rows if any
		if no_of_selected_items > 0:
			save_selected_menu = wx.Menu()
			menu_item = save_selected_menu.Append(-1, _('as &text'))
			self.Bind(wx.EVT_MENU, self._selected_rows2file, menu_item)
			menu_item = save_selected_menu.Append(-1, _('as &CSV'))
			self.Bind(wx.EVT_MENU, self._selected_rows2csv, menu_item)
			menu_item = save_selected_menu.Append(-1, _('as t&ooltips'))
			self.Bind(wx.EVT_MENU, self._selected_row_tooltips2file, menu_item)
			menu_item = save_selected_menu.Append(-1, _('as &data'))
			self.Bind(wx.EVT_MENU, self._selected_row_data2file, menu_item)
			save_menu.Append(-1, _('&selected row(s) ...'), save_selected_menu)
		# put into clipboard
		# - right-clicked/MENU-keyed row
		clip_activated_menu = wx.Menu()
		menu_item = clip_activated_menu.Append(-1, _('as &one-liner'))
		self.Bind(wx.EVT_MENU, self._row2clipboard, menu_item)
		menu_item = clip_activated_menu.Append(-1, _('as &multi-liner (per field)'))
		self.Bind(wx.EVT_MENU, self._row_list2clipboard, menu_item)
		menu_item = clip_activated_menu.Append(-1, _('as &tooltip'))
		self.Bind(wx.EVT_MENU, self._tooltip2clipboard, menu_item)
		if hasattr(self._rclicked_row_data, 'format'):
			menu_item = clip_activated_menu.Append(-1, _('as &data (text)'))
			self.Bind(wx.EVT_MENU, self._data2clipboard, menu_item)
		clip_cols_menu = wx.Menu()
		for col_idx in range(self.ColumnCount):
			col_content = self._rclicked_row_cells[col_idx].strip()
			if col_content == '':
				continue
			txt = '&%s: "%s" [#%s]' % (
				col_idx+1,
				shorten_text(col_content, 35),
				col_idx
			)
			menu_item = clip_cols_menu.Append(-1, txt)
			self.Bind(wx.EVT_MENU, self._col2clipboard, menu_item)
			col_header = col_headers[col_idx]
			if col_header:
				txt = '%s: "%s: %s" [#%s]' % (
					col_idx+1,
					shorten_text(col_header, 8),
					shorten_text(col_content, 35),
					col_idx
				)
				menu_item = clip_cols_menu.Append(-1, txt)
				self.Bind(wx.EVT_MENU, self._col_w_hdr2clipboard, menu_item)
		clip_activated_menu.Append(-1, _('from &field'), clip_cols_menu)
		# - selected rows
		if no_of_selected_items > 0:
			clip_selected_menu = wx.Menu()
			menu_item = clip_selected_menu.Append(-1, _('as &one-liner(s)'))
			self.Bind(wx.EVT_MENU, self._rows2clipboard, menu_item)
			menu_item = clip_selected_menu.Append(-1, _('as &tooltip(s)'))
			self.Bind(wx.EVT_MENU, self._tooltips2clipboard, menu_item)
			menu_item = clip_selected_menu.Append(-1, _('as &data (text)'))
			self.Bind(wx.EVT_MENU, self._datas2clipboard, menu_item)
		clip_menu = wx.Menu()
		clip_menu.Append(-1, _('&activated row ...'), clip_activated_menu)
		clip_menu.Append(-1, _('&selected row(s) ...'), clip_selected_menu)
		# screenshot menu
		screenshot_menu = wx.Menu()
		menu_item = screenshot_menu.Append(-1, _('&Save'))
		self.Bind(wx.EVT_MENU, self._visible_rows_screenshot2file, menu_item)
		menu_item = screenshot_menu.Append(-1, _('E&xport area'))
		self.Bind(wx.EVT_MENU, self._visible_rows_screenshot2export_area, menu_item)
		# primary popup
		self._context_menu.Append(-1, _('Screen&shot ...'), screenshot_menu)
		self._context_menu.Append(-1, _('Save to &file...'), save_menu)
		self._context_menu.Append(-1, _('Copy to &clipboard...'), clip_menu)
		if self.__extend_popup_menu_callback is not None:
			self._context_menu.AppendSeparator()
			self.__extend_popup_menu_callback(menu = self._context_menu)

		# show menu
		self.PopupMenu(self._context_menu, wx.DefaultPosition)
		self._context_menu.Destroy()
		return

	#------------------------------------------------------------
	def __handle_delete(self):
		if self.__delete_callback is None:
			return

		no_items = len(self.get_selected_items(only_one = False))
		if no_items == 0:
			return

		if no_items > 1:
			question = _(
				'%s list items are selected.\n'
				'\n'
				'Really delete all %s items ?'
			) % (no_items, no_items)
			title = _('Deleting list items')
			style = wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP
			dlg = wx.MessageDialog(None, question, title, style)
			btn_pressed = dlg.ShowModal()
			dlg.DestroyLater()
			if btn_pressed == wx.ID_NO:
				self.SetFocus()
				return
			if btn_pressed == wx.ID_CANCEL:
				self.SetFocus()
				return

		self.__delete_callback()
		return

	#------------------------------------------------------------
	def __handle_insert(self):
		if self.__new_callback is None:
			return
		self.__new_callback()

	#------------------------------------------------------------
	def __handle_edit(self):
		if self.__edit_callback is None:
			return
		self.__edit_callback()

	#------------------------------------------------------------
	def __show_search_dialog(self):
		#print "showing search dlg"
		if self.__search_term is None:
			#print "no prev search term"
			default = ''
		else:
			#print "prev search term:", self.__search_term
			default = self.__search_term
		search_term = wx.GetTextFromUser (
			_('Enter search term:'),
			_('List search'),
			default_value = default
		)
		if search_term.strip() == '':
			#print "empty search term"
			self.__search_term = None
			self.__tt_static_part = self.__tt_static_part_base
			return

		#print "search term:", search_term
		self.__search_term = search_term
		self.__tt_static_part = _(
			'Current search term: [[%s]]\n'
			'\n'
			'%s'
		) % (
			search_term,
			self.__tt_static_part_base
		)
		self.__search_match()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_activated(self, event):
		event.Skip()
		if self.__activate_callback is not None:
			self.__activate_callback(event)
			return

		# default double-click / ENTER action: edit
		self.__handle_edit()

	#------------------------------------------------------------
	def _on_list_item_selected(self, event):
		event.Skip()
		if self.__select_callback is not None:
			self.__select_callback(event)

	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		event.Skip()
		if self.__deselect_callback is not None:
			self.__deselect_callback(event)

	#------------------------------------------------------------
	def _on_list_item_rightclicked(self, event):
		event.Skip()
		self.__show_context_menu(event.Index)

	#------------------------------------------------------------
	def _on_list_key_down(self, evt):
		evt.Skip()

		if evt.KeyCode == wx.WXK_DELETE:
			self.__handle_delete()
			return

		if evt.KeyCode == wx.WXK_INSERT:
			self.__handle_insert()
			return

		if evt.KeyCode == wx.WXK_MENU:
			self.__show_context_menu(evt.Index)
			return

	#------------------------------------------------------------
	def _on_char(self, evt):

		if chr(evt.GetRawKeyCode()) == 'f':
			if evt.GetModifiers() == wx.MOD_CMD:
				#print "search dialog invoked"
				self.__show_search_dialog()
				return

		if chr(evt.GetRawKeyCode()) == 'n':
			if evt.GetModifiers() == wx.MOD_CMD:
				#print "search-next key invoked"
				self.__search_match()
				return

		evt.Skip()
		return

	#------------------------------------------------------------
	def _on_mouse_motion(self, event):
		"""Update tooltip on mouse motion.

			for s in dir(wx):
				if s.startswith('LIST_HITTEST'):
					print(s, getattr(wx, s))

			LIST_HITTEST_ABOVE 1
			LIST_HITTEST_BELOW 2
			LIST_HITTEST_NOWHERE 4
			LIST_HITTEST_ONITEM 672
			LIST_HITTEST_ONITEMICON 32
			LIST_HITTEST_ONITEMLABEL 128
			LIST_HITTEST_ONITEMRIGHT 256			# not existant in wxPython 4.2
			LIST_HITTEST_ONITEMSTATEICON 512
			LIST_HITTEST_TOLEFT 1024
			LIST_HITTEST_TORIGHT 2048
		"""
		event.Skip()

		item_idx, where_flag = self.HitTest(wx.Point(event.X, event.Y))

		# pointer on item related area at all ?
		if where_flag not in [
			wx.LIST_HITTEST_ONITEMLABEL,
			wx.LIST_HITTEST_ONITEMICON,
			wx.LIST_HITTEST_ONITEMSTATEICON,
			#wx.LIST_HITTEST_ONITEMRIGHT,
			_WX__LIST_HITTEST_ONITEMRIGHT,
			wx.LIST_HITTEST_ONITEM
		]:
			self.__tt_last_item = None						# not on any item
			self.SetToolTip(self.__tt_static_part)
			return

		# same item as last time around ?
		if self.__tt_last_item == item_idx:
			return

		# remember the new item we are on
		self.__tt_last_item = item_idx

		# HitTest() can return -1 if it so pleases, meaning that no item
		# was hit or else that maybe there aren't any items (empty list)
		if item_idx == wx.NOT_FOUND:
			self.SetToolTip(self.__tt_static_part)
			return

		# do we *have* item data ?
		if self.__data is None:
			self.SetToolTip(self.__tt_static_part)
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
			self.SetToolTip(self.__tt_static_part)
			print("*************************************************************")
			print("GNUmed has detected an inconsistency with list item tooltips.")
			print("")
			print("This is not a big problem and you can keep working.")
			print("")
			print("However, please send us the following so we can fix GNUmed:")
			print("")
			print("item idx: %s" % item_idx)
			print('where flag: %s' % where_flag)
			print('data list length: %s' % len(self.__data))
			print("*************************************************************")
			return

		dyna_tt = None
		if self.__item_tooltip_callback is not None:
			dyna_tt = self.__item_tooltip_callback(self.__data[self.map_item_idx2data_idx(item_idx)])
			if isinstance(dyna_tt, list):
				dyna_tt = '\n'.join(dyna_tt)

		if dyna_tt is None:
			self.SetToolTip(self.__tt_static_part)
			return

		self.SetToolTip(dyna_tt)

	#------------------------------------------------------------
	# context menu event hendlers
	#------------------------------------------------------------
	def _on_add_row(self, evt):
		evt.Skip()
		self.__handle_insert()

	#------------------------------------------------------------
	def _on_edit_row(self, evt):
		evt.Skip()
		self.__handle_edit()

	#------------------------------------------------------------
	def _on_delete_row(self, evt):
		evt.Skip()
		self.__handle_delete()

	#------------------------------------------------------------
	def _on_show_search_dialog(self, evt):
		evt.Skip()
		self.__show_search_dialog()

	#------------------------------------------------------------
	def _on_search_match(self, evt):
		evt.Skip()
		self.__search_match()

	#------------------------------------------------------------
	def _all_rows2file(self, evt):

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-all_rows-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		col_labels = self.column_labels
		line = '%s' % ' || '.join(col_labels)
		txt_file.write('%s\n' % line)
		txt_file.write(('=' * len(line)) + '\n')

		for item_idx in range(self.ItemCount):
			fields = []
			for col_idx in range(self.ColumnCount):
				fields.append(self.GetItem(item_idx, col_idx).Text)
			txt_file.write('%s\n' % ' || '.join(fields))

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('All rows saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _all_rows2csv(self, evt):

		csv_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-all_rows-%s.csv' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		csv_file = open(csv_name, mode = 'wt', encoding = 'utf8')
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow([ l for l in self.column_labels ])
		for item_idx in range(self.ItemCount):
			fields = []
			for col_idx in range(self.ColumnCount):
				fields.append(self.GetItem(item_idx, col_idx).Text)
			csv_writer.writerow([ f for f in fields ])
		csv_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('All rows saved to [%s].') % csv_name)

	#------------------------------------------------------------
	def _all_row_tooltips2file(self, evt):

		if (self.__data is None) or (self.__item_tooltip_callback is None):
			return

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-list_tooltips-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		for data in self.data:
			tt = self.__item_tooltip_callback(data)
			if tt is None:
				continue
			txt_file.write('%s\n\n' % tt)

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('All tooltips saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _all_row_data2file(self, evt):

		if self.__data is None:
			return

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-list_data-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		for data in self.data:
			if hasattr(data, 'format'):
				txt = data.format()
				if type(txt) is list:
					txt = '\n'.join(txt)
			else:
				txt = '%s' % data
			txt_file.write('%s\n\n' % txt)

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('All data saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _selected_rows2file(self, evt):

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-some_rows-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		col_labels = self.column_labels
		line = '%s' % ' || '.join(col_labels)
		txt_file.write('%s\n' % line)
		txt_file.write(('=' * len(line)) + '\n')

		items = self.selected_items
		if self.__is_single_selection:
			items = [items]

		for item_idx in items:
			fields = []
			for col_idx in range(self.ColumnCount):
				fields.append(self.GetItem(item_idx, col_idx).Text)
			txt_file.write('%s\n' % ' || '.join(fields))

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('Selected rows saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _selected_rows2csv(self, evt):

		csv_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-some_rows-%s.csv' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		csv_file = open(csv_name, mode = 'wt', encoding = 'utf8')
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow([ l for l in self.column_labels ])
		items = self.selected_items
		if self.__is_single_selection:
			items = [items]
		for item_idx in items:
			fields = []
			for col_idx in range(self.ColumnCount):
				fields.append(self.GetItem(item_idx, col_idx).Text)
			csv_writer.writerow([ f for f in fields ])
		csv_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('Selected rows saved to [%s].') % csv_name)

	#------------------------------------------------------------
	def _selected_row_tooltips2file(self, evt):

		if (self.__data is None) or (self.__item_tooltip_callback is None):
			return

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-list_tooltips-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		for data in self.selected_item_data:
			tt = self.__item_tooltip_callback(data)
			if tt is None:
				continue
			txt_file.write('%s\n\n' % tt)

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('Selected tooltips saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _selected_row_data2file(self, evt):

		if self.__data is None:
			return

		txt_name = os.path.join(gmTools.gmPaths().user_work_dir, 'gm-list_data-%s.txt' % pydt.datetime.now().strftime('%m%d-%H%M%S'))
		txt_file = open(txt_name, mode = 'wt', encoding = 'utf8')

		for data in self.selected_item_data:
			if hasattr(data, 'format'):
				txt = data.format()
				if type(txt) is list:
					txt = '\n'.join(txt)
			else:
				txt = '%s' % data
			txt_file.write('%s\n\n' % txt)

		txt_file.close()
		gmDispatcher.send(signal = 'statustext', msg = _('Selected data saved to [%s].') % txt_name)

	#------------------------------------------------------------
	def _visible_rows_screenshot2file(self, evt):
		dlg = self.containing_dlg
		if dlg is None:
			widget2screenshot = self
		else:
			widget2screenshot = dlg
		png_name = os.path.join (
			gmTools.gmPaths().user_work_dir,
			'gm-%s-%s.png' % (self.useful_title, pydt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
		)
		from Gnumed.wxpython.gmGuiHelpers import save_screenshot_to_file
		save_screenshot_to_file(filename = png_name, widget = widget2screenshot, settle_time = 500)

	#------------------------------------------------------------
	def _visible_rows_screenshot2export_area(self, evt):
		dlg = self.containing_dlg
		if dlg is None:
			widget2screenshot = self
		else:
			widget2screenshot = dlg
		from Gnumed.wxpython.gmGuiHelpers import save_screenshot_to_file
		screenshot_file = save_screenshot_to_file(widget = widget2screenshot, settle_time = 500)
		gmDispatcher.send(signal = 'add_file_to_export_area', filename = screenshot_file, hint = _('GMd screenshot'))

	#------------------------------------------------------------
	def _tooltip2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return

		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		data_obj = wx.TextDataObject()
		if (self.__data is None) or (self.__item_tooltip_callback is None):
			txt = self.__tt_static_part
		else:
			txt = self.__item_tooltip_callback(self.__data[self.map_item_idx2data_idx(self._rclicked_row_idx)])
			if txt is None:
				txt = self.__tt_static_part
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _tooltips2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		if (self.__data is None) or (self.__item_tooltip_callback is None):
			return

		tts = []
		for data in self.selected_item_data:
			tt = self.__item_tooltip_callback(data)
			if tt is None:
				continue
			tts.append(tt)

		if len(tts) == 0:
			return

		data_obj = wx.TextDataObject()
		data_obj.SetText('\n\n'.join(tts))
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_tooltip2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		if (self.__data is None) or (self.__item_tooltip_callback is None):
			txt += self.__tt_static_part
		else:
			tmp = self.__item_tooltip_callback(self.__data[self.map_item_idx2data_idx(self._rclicked_row_idx)])
			if tmp is None:
				txt += self.__tt_static_part
			else:
				txt += tmp

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_tooltips2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		if (self.__data is None) or (self.__item_tooltip_callback is None):
			return

		tts = []
		for data in self.selected_item_data:
			tt = self.__item_tooltip_callback(data)
			if tt is None:
				continue
			tts.append(tt)

		if len(tts) == 0:
			return

		data_obj = wx.TextDataObject()
		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n\n'
		txt += '\n\n'.join(tts)

		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _row2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()
		data_obj.SetText(' // '.join(self._rclicked_row_cells))
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _rows2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		rows = []
		for item_idx in self.selected_items:
			rows.append(' // '.join([ self.GetItem(item_idx, col_idx).Text.strip() for col_idx in range(self.ColumnCount) ]))

		data_obj = wx.TextDataObject()
		data_obj.SetText('\n\n'.join(rows))
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_row2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		txt += ' // '.join(self._rclicked_row_cells)

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_rows2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		rows = []
		for item_idx in self.selected_items:
			rows.append(' // '.join([ self.GetItem(item_idx, col_idx).Text.strip() for col_idx in range(self.ColumnCount) ]))

		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'
		txt += '\n\n'.join(rows)

		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _row_list2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()
		data_obj.SetText('\n'.join(self._rclicked_row_cells_w_hdr))
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_row_list2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		txt += '\n'.join(self._rclicked_row_cells_w_hdr)

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _data2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()
		txt = self._rclicked_row_data.format()
		if type(txt) == type([]):
			txt = '\n'.join(txt)
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _datas2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		data_as_txt = []
		for data in self.selected_item_data:
			if hasattr(data, 'format'):
				txt = data.format()
				if type(txt) is list:
					txt = '\n'.join(txt)
			else:
				txt = '%s' % data
			data_as_txt.append(txt)

		data_obj = wx.TextDataObject()
		data_obj.SetText('\n\n'.join(data_as_txt))
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_data2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		tmp = self._rclicked_row_data.format()
		if type(tmp) == type([]):
			txt += '\n'.join(tmp)
		else:
			txt += tmp

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_datas2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return

		data_as_txt = []
		for data in self.selected_item_data:
			if hasattr(data, 'format'):
				txt = data.format()
				if type(txt) is list:
					txt = '\n'.join(txt)
			else:
				txt = '%s' % data
			data_as_txt.append(txt)

		data_obj = wx.TextDataObject()
		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'
		txt += '\n'.join(data_as_txt)

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _col2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		#col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.split(u':', 1)[0].rstrip(u':')) - 1
		col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.rsplit('#', 1)[1].rstrip(']'))
		txt = self._rclicked_row_cells[col_idx]

		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_col2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		#col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.split(u':', 1)[0].rstrip(u':')) - 1
		col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.rsplit('#', 1)[1].rstrip(']'))
		txt += self._rclicked_row_cells[col_idx]

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _col_w_hdr2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		#col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.split(u':', 1)[0].rstrip(u':')) - 1
		col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.rsplit('#', 1)[1].rstrip(']'))
		txt = self._rclicked_row_cells_w_hdr[col_idx]

		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	def _add_col_w_hdr2clipboard(self, evt):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return
		data_obj = wx.TextDataObject()

		txt = ''
		# get previous text
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			txt = data_obj.Text + '\n'

		# add text
		#col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.split(u':', 1)[0].rstrip(u':')) - 1
		col_idx = int(self._context_menu.FindItemById(evt.Id).ItemLabel.rsplit('#', 1)[1].rstrip(']'))
		txt += self._rclicked_row_cells_w_hdr[col_idx]

		# set text
		data_obj.SetText(txt)
		wx.TheClipboard.SetData(data_obj)
		wx.TheClipboard.Close()

	#------------------------------------------------------------
	# search related methods
	#------------------------------------------------------------
#	def _on_lost_focus(self, evt):
#		evt.Skip()
#		if self.__search_dlg is None:
#			return
##		print self.FindFocus()
##		print self.__search_dlg
#		#self.__search_dlg.Close()

	#------------------------------------------------------------
	def __search_match(self):
		#print "search_match"
		if self.__search_term is None:
			#print "no search term"
			return False
		if self.__search_term.strip() == '':
			#print "empty search term"
			return False
		if self.__searchable_cols is None:
			#print "searchable cols not initialized, now setting"
			self.searchable_columns = None
		if len(self.__searchable_cols) == 0:
			#print "no cols to search"
			return False

		#print "on searching for match on:", self.__search_term
		for row_idx in range(self.__next_line_to_search, self.ItemCount):
			for col_idx in range(self.ColumnCount):
				if col_idx not in self.__searchable_cols:
					continue
				col_val = self.GetItem(row_idx, col_idx).GetText()
				if regex.search(self.__search_term, col_val, regex.U | regex.I) is not None:
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
	def _set_searchable_cols(self, cols):
		#print "setting searchable cols to:", cols
		# zero-based list of which columns to search
		if cols is None:
			#print "setting searchable cols to:", range(self.ColumnCount)
			self.__searchable_cols = range(self.ColumnCount)
			return
		# weed out columns to be searched which
		# don't exist and uniquify them
		new_cols = {}
		for col in cols:
			if col < self.ColumnCount:
				new_cols[col] = True
		self.__searchable_cols = list(new_cols)

	searchable_columns = property(lambda x:x, _set_searchable_cols)

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_activate_callback(self):
		return self.__activate_callback

	def _set_activate_callback(self, callback):
		if callback is None:
			self.Unbind(wx.EVT_LIST_ITEM_ACTIVATED)
			self.__activate_callback = None
			return
		if not callable(callback):
			raise ValueError('<activate> callback is not a callable: %s' % callback)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated)
		self.__activate_callback = callback

	activate_callback = property(_get_activate_callback, _set_activate_callback)

	#------------------------------------------------------------
	def _get_select_callback(self):
		return self.__select_callback

	def _set_select_callback(self, callback):
		if callback is None:
			self.Unbind(wx.EVT_LIST_ITEM_SELECTED)
			self.__select_callback = None
			return
		if not callable(callback):
			raise ValueError('<selected> callback is not a callable: %s' % callback)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected)
		self.__select_callback = callback

	select_callback = property(_get_select_callback, _set_select_callback)

	#------------------------------------------------------------
	def _get_deselect_callback(self):
		return self.__deselect_callback

	def _set_deselect_callback(self, callback):
		if callback is None:
			self.Unbind(wx.EVT_LIST_ITEM_DESELECTED)
			self.__deselect_callback = None
			return
		if not callable(callback):
			raise ValueError('<deselected> callback is not a callable: %s' % callback)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_list_item_deselected)
		self.__deselect_callback = callback

	deselect_callback = property(_get_deselect_callback, _set_deselect_callback)

	#------------------------------------------------------------
	def _get_delete_callback(self):
		return self.__delete_callback

	def _set_delete_callback(self, callback):
		if callback is None:
			#self.Unbind(wx.EVT_LIST_ITEM_SELECTED)
			self.__delete_callback = None
			return
		if not callable(callback):
			raise ValueError('<delete> callback is not a callable: %s' % callback)
		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected)
		self.__delete_callback = callback

	delete_callback = property(_get_delete_callback, _set_delete_callback)

	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		if callback is None:
			self.__new_callback = None
			return
		if not callable(callback):
			raise ValueError('<new> callback is not a callable: %s' % callback)
		self.__new_callback = callback

	new_callback = property(_get_new_callback, _set_new_callback)

	#------------------------------------------------------------
	def _get_edit_callback(self):
		return self.__edit_callback

	def _set_edit_callback(self, callback):
		if callback is None:
			self.__edit_callback = None
			return
		if not callable(callback):
			raise ValueError('<edit> callback is not a callable: %s' % callback)
		self.__edit_callback = callback

	edit_callback = property(_get_edit_callback, _set_edit_callback)

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
	def _set_extend_popup_menu_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<extend_popup_menu> callback is not a callable: %s' % callback)
		self.__extend_popup_menu_callback = callback

	extend_popup_menu_callback = property(lambda x:x, _set_extend_popup_menu_callback)

	#------------------------------------------------------------
	# cColumnSorterMixin API
	#------------------------------------------------------------
	def _generate_map_for_sorting(self):
		dict2sort = {}
		row_count = self.GetItemCount()
		if row_count == 0:
			return dict2sort

		col_count = self.GetColumnCount()
		for row_idx in range(row_count):
			dict2sort[row_idx] = ()
			if col_count == 0:
				continue
			for col_idx in range(col_count):
				dict2sort[row_idx] += (self.GetItem(row_idx, col_idx).GetText(), )
				# debugging:
				#print u'[%s:%s] ' % (row_idx, col_idx), self.GetItem(row_idx, col_idx).GetText()
		return dict2sort

	#------------------------------------------------------------
	def __get_secondary_sort_col(self):
		return self.__secondary_sort_col

	def __set_secondary_sort_col(self, col):
		if col is None:
			self.__secondary_sort_col = None
			return
		if col > self.ColumnCount:
			raise ValueError('cannot secondary-sort on col [%s], there are only [%s] columns', col, self.ColumnCount)
		self.__secondary_sort_col = col

	secondary_sort_column = property(__get_secondary_sort_col, __set_secondary_sort_col)

	#------------------------------------------------------------
	# drag and drop mixin API
	#------------------------------------------------------------
	def get_drag_data_object(self):
		"""Get data to be dragged.

		Returns:
			A drag data object, or None if nothing is to be dragged.

		Override to provide whatever data is to be dragged.
		The overrider itself can provide a default or call
		some external callback.
		"""
		if self.__dnd_callback is not None:
			return self.__dnd_callback()

		item = self.get_selected_items(only_one = True)
		data = self.get_selected_item_data(only_one = True)
		if (item is None) and (data is None):
			return None

		data_obj = wx.DataObjectComposite()
		if data is not None:
			if hasattr(data, 'format'):
				txt = data.format()
				if type(txt) is list:
					txt = '\n'.join(txt)
			else:
				txt = '%s' % data
			txt_data = wx.TextDataObject(txt)
			data_obj.Add(txt_data, True)
		if item is not None:
			fields = []
			for col_idx in range(self.ColumnCount):
				fields.append(self.GetItem(item, col_idx).Text)
			txt = '%s\n' % ' || '.join(fields)
			txt_data = wx.TextDataObject(txt)
			data_obj.Add(txt_data, False)
		#tdo = wx.PyTextDataObject(str(item))
		return data_obj

	#------------------------------------------------------------
	def _get_dnd_callback(self):
		return self.__dnd_callback

	def _set_dnd_callback(self, callback):
		if callback is None:
			self.__dnd_callback = None
			return

		if not callable(callback):
			raise ValueError('<dnd> callback is not a callable: %s' % callback)

		self.__dnd_callback = callback

	dnd_callback = property(_get_dnd_callback, _set_dnd_callback)

	#------------------------------------------------------------
	#------------------------------------------------------------
	def __get_useful_title(self):
		title = undecorate_window_title(gmTools.coalesce(self.container_title, '').rstrip())
		if title != '':
			return title

		if self.ColumnCount == 0:
			return _('list')

		col_labels = []
		for col_idx in range(self.ColumnCount):
			col_label = self.GetColumn(col_idx).Text.strip()
			if col_label != '':
				col_labels.append(col_label)
		return _('list') + '-[%s]' % ']_['.join(col_labels)

	useful_title = property(__get_useful_title)

	#------------------------------------------------------------
	def __get_container_title(self, widget=None):
		if widget is None:
			widget = self
		if hasattr(widget, 'GetTitle'):
			title = widget.GetTitle().strip()
			if title != '':
				return title

		parent = widget.GetParent()
		if parent is None:
			return None

		return self.__get_container_title(widget = parent)

	container_title = property(__get_container_title)

	#------------------------------------------------------------
	def __get_containing_dlg(self, widget=None):
		if widget is None:
			widget = self
		if isinstance(widget, wx.Dialog):
			return widget

		parent = widget.GetParent()
		if parent is None:
			return None

		return self.__get_containing_dlg(widget = parent)

	containing_dlg = property(__get_containing_dlg)

#================================================================
def shorten_text(text=None, max_length=None):
	if len(text) <= max_length:
		return text
	return text[:max_length-1] + '\u2026'

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
		#app = wx.PyWidgetTester(size = (400, 500))
		dlg = wx.MultiChoiceDialog (
			parent = None,
			message = 'test message',
			caption = 'test caption',
			choices = ['a', 'b', 'c', 'd', 'e']
		)
		dlg.ShowModal()
		sels = dlg.GetSelections()
		print("selected:")
		for sel in sels:
			print(sel)

	#------------------------------------------------------------
	def test_get_choices_from_list():

		def edit(argument):
			print("editor called with:")
			print(argument)

		def refresh(lctrl):
			choices = ['a', 'b', 'c']
			lctrl.set_string_items(choices)

		#app = 
		wx.App()
		chosen = get_choices_from_list (
#			msg = 'select a health issue\nfrom the list below\n',
			caption = 'select health issues',
			#choices = [['D.M.II', '4'], ['MS', '3'], ['Fraktur', '2']],
			#columns = ['issue', 'no of episodes']
			columns = ['issue'],
			refresh_callback = refresh,
			single_selection = False
			#, edit_callback = edit
		)
		print("chosen:")
		print(chosen)

	#------------------------------------------------------------
	def test_item_picker_dlg():
		#app = wx.PyWidgetTester(size = (200, 50))
		#app = 
		wx.App((200, 50))
		dlg = cItemPickerDlg(None, -1, msg = 'Pick a few items:')
		dlg.set_columns(['Plugins'], ['Load in workplace', 'dummy'])
		#dlg.set_columns(['Plugins'], [])
		dlg.set_string_items(['patient', 'emr', 'docs'])
		result = dlg.ShowModal()
		print(result)
		print(dlg.get_picks())

	#------------------------------------------------------------
	test_get_choices_from_list()
	#test_wxMultiChoiceDialog()
	#test_item_picker_dlg()

#================================================================
