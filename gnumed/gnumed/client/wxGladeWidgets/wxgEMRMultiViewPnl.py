#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#@+leo-ver=5-thin
#@+node:jll2.20130407165702.3142: * @thin wxgEMRMultiViewPnl.py
#@@first
#@@first
#@@language python
#@@tabwidth 2

#@+<<imports>>
#@+node:jll2.20130407165702.3143: ** <<imports>>

import wx

#@-<<imports>>
#@+others
#@+node:jll2.20130407165702.3144: ** class wxgEMRMultiViewPnl
class wxgEMRMultiViewPnl(wx.Panel):

		def __init__(self, *args, **kwds):

				from Gnumed.wxpython import gmEMRMultiViewWidgets

				# begin wxGlade: wxgEMRMultiViewPnl.__init__
				kwds["style"] = wx.TAB_TRAVERSAL
				wx.Panel.__init__(self, *args, **kwds)
				self._splitter_browser = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)
				self.__pnl_right_side = wx.Panel(self._splitter_browser, -1, style=wx.NO_BORDER)
				self.__pnl_left_side = wx.Panel(self._splitter_browser, -1, style=wx.NO_BORDER|wx.TAB_TRAVERSAL)
				self._pnl_emr_tree = gmEMRMultiViewWidgets.cEMRTree(self.__pnl_left_side, -1)
				self._view_type = wx.RadioBox(self.__pnl_left_side, -1, _("view type"), choices=[_("overview"), _("journal"), _("changes log")], majorDimension=3, style=wx.RA_SPECIFY_COLS)
				self._item_details = wx.TextCtrl(self.__pnl_right_side, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.NO_BORDER)
				self._btn_print = wx.Button(self.__pnl_right_side, -1, _("Print"))

				self.__set_properties()
				self.__do_layout()

				self.Bind(wx.EVT_BUTTON, self._print_btn_pressed, self._btn_print)
				# end wxGlade

		def __set_properties(self):
				# begin wxGlade: wxgEMRMultiViewPnl.__set_properties
				self._view_type.SetMinSize((336, 41))
				self._view_type.SetSelection(0)
				# end wxGlade
				self._item_details.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))

		def __do_layout(self):
				# begin wxGlade: wxgEMRMultiViewPnl.__do_layout
				__szr_main = wx.BoxSizer(wx.HORIZONTAL)
				__szr_right_side = wx.BoxSizer(wx.VERTICAL)
				buttons = wx.BoxSizer(wx.HORIZONTAL)
				__szr_left_side = wx.BoxSizer(wx.VERTICAL)
				__szr_left_side.Add(self._pnl_emr_tree, 1, wx.EXPAND, 0)
				__szr_left_side.Add(self._view_type, 0, wx.ALL, 2)
				self.__pnl_left_side.SetSizer(__szr_left_side)
				__szr_right_side.Add(self._item_details, 1, wx.EXPAND, 0)
				buttons.Add(self._btn_print, 0, 0, 0)
				__szr_right_side.Add(buttons, 0, wx.ALL, 8)
				self.__pnl_right_side.SetSizer(__szr_right_side)
				self._splitter_browser.SplitVertically(self.__pnl_left_side, self.__pnl_right_side, 340)
				__szr_main.Add(self._splitter_browser, 1, wx.EXPAND, 0)
				self.SetSizer(__szr_main)
				__szr_main.Fit(self)
				# end wxGlade

		def _print_btn_pressed(self, event): # wxGlade: wxgEMRMultiViewPnl.<event_handler>
				print "Event handler `_print_btn_pressed' not implemented"
				event.Skip()

# end of class wxgEMRMultiViewPnl
#@-others

#@-leo
