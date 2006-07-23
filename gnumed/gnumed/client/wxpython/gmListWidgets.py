"""GNUmed list controls and widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmListWidgets.py,v $
# $Id: gmListWidgets.py,v 1.1 2006-07-23 20:34:50 ncq Exp $
__version__ = "$Revision: 1.1 $"
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

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#------------------------------------------------------------
	def set_data(self, data = None):
		self.__data = data
	#------------------------------------------------------------
	def get_item_data(self, item_idx = None):
		return self.__data[item_idx]

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':
	print "no obvious syntax errors"
	print "please write a real unit test"

#================================================================
# $Log: gmListWidgets.py,v $
# Revision 1.1  2006-07-23 20:34:50  ncq
# - list controls and widgets
#
#