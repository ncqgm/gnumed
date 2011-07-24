"""GNUmed list controls and widgets.

TODO:

	From: Rob McMullen <rob.mcmullen@gmail.com>
	To: wxPython-users@lists.wxwidgets.org
	Subject: Re: [wxPython-users] ANN: ColumnSizer mixin for ListCtrl

	Thanks for all the suggestions, on and off line.  There's an update
	with a new name (ColumnAutoSizeMixin) and better sizing algorithm at:

	http://trac.flipturn.org/browser/trunk/peppy/lib/column_autosize.py
"""
#================================================================
__version__ = "$Revision: 1.37 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, types


import wx
import wx.lib.mixins.listctrl as listmixins


if __name__ == '__main__':
	sys.path.insert(0, '../../')

#================================================================
# FIXME: configurable callback on double-click action

def get_choices_from_list (
			parent=None,
			msg=None,
			caption=None,
			choices=None,
			selections=None,
			columns=None,
			data=None,
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

	- left/middle/right_extra_button: (label, tooltip, <callback>)
		<callback> is called with item_data as the only argument

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
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		# if the edit button *can* be pressed there are *supposed*
		# to be both an item selected and an editor configured
		if not self.edit_callback(self._LCTRL_items.get_selected_item_data(only_one=True)):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
	#------------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		# if the delete button *can* be pressed there are *supposed*
		# to be both an item selected and a deletor configured
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item_data is None:
			return
		if not self.delete_callback(item_data):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
	#------------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__left_extra_button_callback(item_data):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
	#------------------------------------------------------------
	def _on_middle_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__middle_extra_button_callback(item_data):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
	#------------------------------------------------------------
	def _on_right_extra_button_pressed(self, event):
		item_data = self._LCTRL_items.get_selected_item_data(only_one=True)
		if not self.__right_extra_button_callback(item_data):
			return
		if self.refresh_callback is None:
			return
		wx.BeginBusyCursor()
		try:
			self.refresh_callback(lctrl = self._LCTRL_items)
		finally:
			wx.EndBusyCursor()
		self._LCTRL_items.set_column_widths()
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
	#def _get_tooltip(self, item):		# inside class
	#def _get_tooltip(item):			# outside class
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
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
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
	# properties
	#------------------------------------------------------------
	def _get_new_callback(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		self.__new_callback = callback
		self._BTN_add.Enable(callback is not None)

	new_callback = property(_get_new_callback, _set_new_callback)
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

		self._LCTRL_left.activate_callback = self.__pick_selected
		#self._LCTRL_left.item_tooltip_callback = self.__on_get_item_tooltip

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
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __pick_selected(self, event=None):
		if self._LCTRL_left.get_selected_items(only_one = True) == -1:
			return

		right_items = self._LCTRL_right.get_string_items()
		right_data = self._LCTRL_right.get_item_data()

		right_items.extend(self._LCTRL_left.get_selected_string_items(only_one = False))
		self._LCTRL_right.set_string_items(items = right_items)
		del right_items

		if right_data is None:
			self._LCTRL_right.set_data(data = self._LCTRL_left.get_selected_item_data(only_one = False))
		else:
			right_data.extend(self._LCTRL_left.get_selected_item_data(only_one = False))
			self._LCTRL_right.set_data(data = right_data)
		del right_data

		self._LCTRL_right.set_column_widths()
	#------------------------------------------------------------
	def __remove_selected_picks(self):
		if self._LCTRL_right.get_selected_items(only_one = True) == -1:
			return

		for item_idx in self._LCTRL_right.get_selected_items(only_one = False):
			self._LCTRL_right.remove_item(item_idx)

		if self._LCTRL_right.GetItemCount() == 0:
			self._BTN_right2left.Enable(False)
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
#================================================================
class cReportListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):

	# FIXME: searching by typing

	def __init__(self, *args, **kwargs):

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) == wx.LC_SINGLE_SEL)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)

		self.__widths = None
		self.__data = None
		self.__activate_callback = None

		self.Bind(wx.EVT_MOTION, self._on_mouse_motion)
		self.__item_tooltip_callback = None
		self.__tt_last_item = None
		self.__tt_static_part = _("""Select the items you want to work on.

A discontinuous selection may depend on your holding down a platform-dependent modifier key (<ctrl>, <alt>, etc) or key combination (eg. <ctrl-shift> or <ctrl-alt>) while clicking.""")
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
	def set_string_items(self, items = None):
		"""All item members must be unicode()able or None."""

		self.DeleteAllItems()
		self.__data = items
		self.__tt_last_item = None

		if items is None:
			return

		for item in items:
			try:
				item[0]
				if not isinstance(item, basestring):
					is_numerically_iterable = True
				else:
					is_numerically_iterable = False
			except TypeError:
				is_numerically_iterable = False

			if is_numerically_iterable:
				# cannot use errors='replace' since then
				# None/ints/unicode strings fail to get encoded
				col_val = unicode(item[0])
				row_num = self.InsertStringItem(index = sys.maxint, label = col_val)
				for col_idx in range(1, min(self.GetColumnCount(), len(item))):
					col_val = unicode(item[col_idx])
					self.SetStringItem(index = row_num, col = col_idx, label = col_val)
			else:
				# cannot use errors='replace' since then None/ints/unicode strings fails to get encoded
				col_val = unicode(item)
				row_num = self.InsertStringItem(index = sys.maxint, label = col_val)
	#------------------------------------------------------------
	def set_data(self, data = None):
		"""<data must be a list corresponding to the item indices>"""
		self.__data = data
		self.__tt_last_item = None
	#------------------------------------------------------------
	def set_selections(self, selections=None):
		self.Select(0, on = 0)
		for idx in selections:
			self.Select(idx = idx, on = 1)
			#self.SetItemState(idx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
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
			return self.__data[item_idx]

		return [ self.__data[item_idx] for item_idx in range(self.GetItemCount()) ]
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):

		if self.__is_single_selection or only_one:
			if self.__data is None:
				return None
			idx = self.GetFirstSelected()
			if idx == -1:
				return None
			return self.__data[idx]

		data = []
		if self.__data is None:
			return data
		idx = self.GetFirstSelected()
		while idx != -1:
			data.append(self.__data[idx])
			idx = self.GetNextSelected(idx)

		return data
	#------------------------------------------------------------
	def deselect_selected_item(self):
		self.Select(idx = self.GetFirstSelected(), on = 0)
	#------------------------------------------------------------
	def remove_item(self, item_idx=None):
		self.DeleteItem(item_idx)
		if self.__data is not None:
			del self.__data[item_idx]
		self.__tt_last_item = None
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_activated(self, event):
		event.Skip()
		if self.__activate_callback is not None:
			self.__activate_callback(event)
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
		if item_idx == -1:
			self.SetToolTipString(self.__tt_static_part)
			return

		# do we *have* item data ?
		if self.__data is None:
			self.SetToolTipString(self.__tt_static_part)
			return

		# under some circumstances the item_idx returned
		# by HitTest() may not be out of bounds with respect
		# to self.__data, this hints at a sync problem between
		# setting display items and associated data
		if (
			(item_idx > len(self.__data))
				or
			(item_idx < -1)
		):
			self.SetToolTipString(self.__tt_static_part)
			_log.error('item idx: %s', item_idx)
			_log.error('where flag: %s', where_flag)
			_log.error('data list length: %s', len(self.__data))
			for data in self.__data:
				_log.debug(data)
			print "*************************************************************"
			print "GNUmed has detected an inconsistency with list item tooltips."
			print ""
			print "This is not a big problem and you can keep working."
			print ""
			print "However, please send us the log file so we can fix GNUmed."
			print "*************************************************************"
			return

		dyna_tt = None
		if self.__item_tooltip_callback is not None:
			dyna_tt = self.__item_tooltip_callback(self.__data[item_idx])

		if dyna_tt is None:
			self.SetToolTipString(self.__tt_static_part)
			return

		self.SetToolTipString(dyna_tt)
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
	def _set_item_tooltip_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<item_tooltip> callback is not a callable: %s' % callback)
		self.__item_tooltip_callback = callback

	item_tooltip_callback = property(lambda x:x, _set_item_tooltip_callback)
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

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