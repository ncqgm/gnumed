"""GNUmed list controls and widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmListWidgets.py,v $
# $Id: gmListWidgets.py,v 1.22 2008-02-26 16:28:04 ncq Exp $
__version__ = "$Revision: 1.22 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, types


import wx
import wx.lib.mixins.listctrl as listmixins


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson
from Gnumed.pycommon import gmTools, gmDispatcher
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgGenericListSelectorDlg, wxgGenericListManagerPnl

#================================================================
def get_choices_from_list(parent=None, msg=None, caption=None, choices=None, selections=None, columns=None, data=None, edit_callback=None, new_callback=None, delete_callback=None, refresh_callback=None, single_selection=False):
	"""Let user select item(s) from a list.

	- edit_callback: (item data)
	- new_callback: ()
	- delete_callback: (item data)
	- refresh_callback: (listctrl)
	"""
	if caption is None:
		caption = _('generic multi choice dialog')

	if single_selection:
		dlg = cGenericListSelectorDlg(parent, -1, title = caption, msg = msg, style = wx.LC_SINGLE_SEL)
	else:
		dlg = cGenericListSelectorDlg(parent, -1, title = caption, msg = msg)
	dlg.edit_callback = edit_callback
	dlg.new_callback = new_callback
	dlg.delete_callback = delete_callback
	dlg.refresh_callback = refresh_callback
	dlg.set_columns(columns = columns)
	dlg.set_string_items(items = choices)
	if selections is not None:
		dlg.set_selections(selections = selections)
	if data is not None:
		dlg.set_data(data=data)

	btn_pressed = dlg.ShowModal()
	sels = dlg.get_selected_item_data(only_one = single_selection)
	dlg.Destroy()

	if btn_pressed == wx.ID_OK:
		return sels

	return None
#----------------------------------------------------------------
class cGenericListSelectorDlg(wxgGenericListSelectorDlg.wxgGenericListSelectorDlg):

	def __init__(self, *args, **kwargs):

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError: msg = None

		wxgGenericListSelectorDlg.wxgGenericListSelectorDlg.__init__(self, *args, **kwargs)

		if msg is None:
			self._LBL_message.Hide()
		else:
			self._LBL_message.SetLabel(msg)

		self.__new_callback = None				# called when NEW button pressed, no argument passed in
		self.edit_callback = None				# called when EDIT button pressed, data of topmost selected item passed in
		self.delete_callback = None				# called when DELETE button pressed, data of topmost selected item passed in
		self.refresh_callback = None			# called when new/edit/delete callbacks return True (IOW were not cancelled)
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
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
		self._BTN_ok.Enable(True)
		self._BTN_ok.SetDefault()
		if self.edit_callback is not None:
			self._BTN_edit.Enable(True)
		if self.delete_callback is not None:
			self._BTN_delete.Enable(True)
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			self._BTN_ok.Enable(False)
			self._BTN_cancel.SetDefault()
			self._BTN_edit.Enable(False)
			self._BTN_delete.Enable(False)
	#------------------------------------------------------------
	def _on_new_button_pressed(self, event):
		if not self.new_callback():
			return
		if self.refresh_callback is None:
			return
		self.refresh_callback(lctrl = self._LCTRL_items)
	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		# if the edit button *can* be pressed there are *supposed*
		# to be both an item selected and an editor configured
		if not self.edit_callback(self._LCTRL_items.get_selected_item_data(only_one=True)):
			return
		if self.refresh_callback is None:
			return
		self.refresh_callback(lctrl = self._LCTRL_items)
	#------------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		# if the delete button *can* be pressed there are *supposed*
		# to be both an item selected and an deletor configured
		if not self.delete_callback(self._LCTRL_items.get_selected_item_data(only_one=True)):
			return
		if self.refresh_callback is None:
			return
		self.refresh_callback(lctrl = self._LCTRL_items)
	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_noop(self):
		return self.__new_callback

	def _set_new_callback(self, callback):
		self.__new_callback = callback
		self._BTN_new.Enable(callback is not None)

	new_callback = property(_get_noop, _set_new_callback)
#================================================================
class cGenericListManagerPnl(wxgGenericListManagerPnl.wxgGenericListManagerPnl):

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
		self.refresh_callback(lctrl = self._LCTRL_items)
	#------------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		item = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item is None:
			return
		if not self.edit_callback(item):
			return
		if self.refresh_callback is None:
			return
		self.refresh_callback(lctrl = self._LCTRL_items)
	#------------------------------------------------------------
	def _on_remove_button_pressed(self, event):
		item = self._LCTRL_items.get_selected_item_data(only_one=True)
		if item is None:
			return
		if not self.delete_callback(item):
			return
		if self.refresh_callback is None:
			return
		self.refresh_callback(lctrl = self._LCTRL_items)
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
class cReportListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):

	def __init__(self, *args, **kwargs):

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) == wx.LC_SINGLE_SEL)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#------------------------------------------------------------
	# setters
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		"""(Re)define the columns.

		Note that this will (have to) delete the items.
		"""
		self.ClearAll()
		if columns is None:
			return
		for idx in range(len(columns)):
			self.InsertColumn(idx, columns[idx])
	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		if widths is None:
			if self.GetItemCount() == 0:
				width_type = wx.LIST_AUTOSIZE_USEHEADER
			else:
				width_type = wx.LIST_AUTOSIZE
			for idx in range(self.GetColumnCount()):
				self.SetColumnWidth(col = idx, width = width_type)
			return

		for idx in range(len(widths)):
			self.SetColumnWidth(col = idx, width = widths[idx])
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		"""All item members must be unicode()able or None."""

		self.DeleteAllItems()
		self.__data = items

		if items is None:
			return

		for item in items:
			if type(item) == types.ListType:
				# cannot use errors='replace' since then None/ints/unicode strings fails to get encoded
				col_val = unicode(item[0])
				row_num = self.InsertStringItem(index = sys.maxint, label = col_val)
				for col_idx in range(1, len(item)):
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
	#------------------------------------------------------------
	def set_selections(self, selections=None):
		self.Select(0, on = 0)
		for idx in selections:
			self.Select(idx = idx, on = 1)
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
	def get_item_data(self, item_idx = None):
		if self.__data is None:	# this isn't entirely clean
			return None

		return self.__data[item_idx]
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
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

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

		app = wx.PyWidgetTester(size = (200, 50))
		chosen = get_choices_from_list (
#			msg = 'select a health issue\nfrom the list below\n',
			caption = 'select health issues',
			choices = [['D.M.II', '4'], ['MS', '3'], ['Fraktur', '2']],
			columns = ['issue', 'no of episodes'],
			edit_callback = edit
		)
		print "chosen:"
		print chosen
	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		test_get_choices_from_list()
		#test_wxMultiChoiceDialog()

#================================================================
# $Log: gmListWidgets.py,v $
# Revision 1.22  2008-02-26 16:28:04  ncq
# - when auto-setting col widths in lists w/o items use header as width ;-)
#
# Revision 1.21  2007/11/28 22:37:00  ncq
# - robustify in the absence of selected values
#
# Revision 1.20  2007/11/23 23:34:39  ncq
# - when explicitely setting the selections deselect the
#   0th-index item selected by default
#
# Revision 1.19  2007/11/17 16:38:13  ncq
# - cGenericListManagerPnl
#
# Revision 1.18  2007/10/08 12:56:02  ncq
# - document callbacks
# - protect against self.__data being None in get(_selected)_item_data()
#
# Revision 1.17  2007/09/24 18:37:08  ncq
# - get_column_labels()
#
# Revision 1.16  2007/09/20 19:10:15  ncq
# - carefully handle list item insertion - handle both list
#   of lists and list of strings
#
# Revision 1.15  2007/09/07 22:38:04  ncq
# - remove Fit() call since it's counterproductive for the list
#
# Revision 1.14  2007/09/02 20:54:26  ncq
# - remove cruft
# - support refresh_callback
#
# Revision 1.13  2007/08/31 23:05:05  ncq
# - fix single selection list
#
# Revision 1.12  2007/08/29 14:41:54  ncq
# - no more singular get_choice_from_list()
# - support add/delete callbacks in generic list selector
#
# Revision 1.11  2007/08/20 16:22:51  ncq
# - make get_choice(s)_from_list() more generic
# - cleanup, improved test
# - support edit button and message in generic list selector
#
# Revision 1.10  2007/07/22 09:26:25  ncq
# - new get_choice_from_list()
#
# Revision 1.9  2007/07/09 12:45:47  ncq
# - fix unicode()ing in set_string_items(): can't use (..., errors='replace') :-(
# - factor out cPatientListingCtrl into gmDataMiningWidgets.py
#
# Revision 1.8  2007/07/07 12:42:00  ncq
# - set_string_items now applies unicode() to all item members
# - cPatientListingCtrl and test suite
#
# Revision 1.7  2007/06/28 12:38:15  ncq
# - fix logic reversal in get_selected_*()
#
# Revision 1.6  2007/06/18 20:33:56  ncq
# - add get_choice(s)_from_list()
# - add cGenericListSelectorDlg
# - add set_string_items()/set_selections()/get_selected_items()
# - improve test suite
#
# Revision 1.5  2007/06/12 16:03:02  ncq
# - properly get rid of all columns in set_columns()
#
# Revision 1.4  2007/04/09 18:51:47  ncq
# - add support for multiple selections and auto-setting the widths
#
# Revision 1.3  2007/03/18 14:09:31  ncq
# - add set_columns() and set_column_widths()
#
# Revision 1.2  2006/12/11 20:50:45  ncq
# - get_selected_item_data()
# - deselect_selected_item()
#
# Revision 1.1  2006/07/23 20:34:50  ncq
# - list controls and widgets
#
#