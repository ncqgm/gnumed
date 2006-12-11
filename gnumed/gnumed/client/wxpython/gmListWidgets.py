"""GNUmed list controls and widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmListWidgets.py,v $
# $Id: gmListWidgets.py,v 1.2 2006-12-11 20:50:45 ncq Exp $
__version__ = "$Revision: 1.2 $"
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

		# FIXME: remember SINGLE_SELECTION and use that in get_selected_item_data()

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#------------------------------------------------------------
	def set_data(self, data = None):
		"""<data must be a list corresponding to the item indices>"""
		self.__data = data
	#------------------------------------------------------------
	def get_item_data(self, item_idx = None):
		return self.__data[item_idx]
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=True):
		# FIXME: support only_one overriding self.is_single_choice
		# FIXME: idx = GetFirstSelected, while idx != -1: idx = GetNextSelected()
		return self.__data[self.GetFirstSelected()]
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
# Revision 1.2  2006-12-11 20:50:45  ncq
# - get_selected_item_data()
# - deselect_selected_item()
#
# Revision 1.1  2006/07/23 20:34:50  ncq
# - list controls and widgets
#
#