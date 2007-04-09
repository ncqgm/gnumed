"""GNUmed list controls and widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmListWidgets.py,v $
# $Id: gmListWidgets.py,v 1.4 2007-04-09 18:51:47 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import wx
import wx.lib.mixins.listctrl as listmixins

#================================================================
class cReportListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):

	def __init__(self, *args, **kwargs):

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) != 0)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		"""(Re)define the columns.

		Note that this will (have to) delete the items.
		"""
		self.DeleteAllItems()
		for idx in range(self.GetColumnCount()):
			self.DeleteColumn(idx)
		if columns is None:
			return
		for idx in range(len(columns)):
			self.InsertColumn(idx, columns[idx])
	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		if widths is None:
			for idx in range(self.GetColumnCount()):
				self.SetColumnWidth(col = idx, width = wx.LIST_AUTOSIZE)
			return

		for idx in range(len(widths)):
			self.SetColumnWidth(col = idx, width = widths[idx])
	#------------------------------------------------------------
	def set_data(self, data = None):
		"""<data must be a list corresponding to the item indices>"""
		self.__data = data
	#------------------------------------------------------------
	def get_item_data(self, item_idx = None):
		return self.__data[item_idx]
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=True):

		if self.__is_single_selection or only_one:
			return self.__data[self.GetFirstSelected()]

		data = []
		idx = self.GetFirstSelected()
		while idx != -1:
			idx = self.GetNextSelected()
			data.append(self.__data[idx])

		return data
	#------------------------------------------------------------
	def deselect_selected_item(self):
		self.Select(idx = self.GetFirstSelected(), on = 0)
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':
	print "no obvious syntax errors"
	print "please write a real unit test"

#================================================================
# $Log: gmListWidgets.py,v $
# Revision 1.4  2007-04-09 18:51:47  ncq
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