# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx
import wx.adv

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
from Gnumed.wxpython.gmTextCtrl import cTextCtrl
from Gnumed.wxpython.gmListWidgets import cReportListCtrl
from Gnumed.wxpython.gmATCWidgets import cATCPhraseWheel
from Gnumed.wxpython.gmLOINCWidgets import cLOINCPhraseWheel
# end wxGlade


class wxgSubstanceEAPnl(wx.ScrolledWindow):
	def __init__(self, *args, **kwds):
		# begin wxGlade: wxgSubstanceEAPnl.__init__
		kwds["style"] = kwds.get("style", 0) | wx.BORDER_NONE | wx.TAB_TRAVERSAL
		wx.ScrolledWindow.__init__(self, *args, **kwds)
		self._TCTRL_substance = cTextCtrl(self, wx.ID_ANY, "")
		self._HL_atc_list = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, _("ATC Code"), _("http://www.whocc.no/atc_ddd_index/"), style=wx.adv.HL_DEFAULT_STYLE)
		self._PRW_atc = cATCPhraseWheel(self, wx.ID_ANY, "")
		self._TCTRL_instructions = cTextCtrl(self, wx.ID_ANY, "")
		self._HL_loinc_list = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, _("LOINCs"), _("https://search.loinc.org"), style=wx.adv.HL_DEFAULT_STYLE)
		self._PRW_loinc = cLOINCPhraseWheel(self, wx.ID_ANY, "")
		self._BTN_add_loinc = wx.Button(self, wx.ID_ANY, _("Add"), style=wx.BU_EXACTFIT)
		self._LCTRL_loincs = cReportListCtrl(self, wx.ID_ANY, style=wx.BORDER_NONE | wx.LC_REPORT)
		self._BTN_remove_loincs = wx.Button(self, wx.ID_ANY, _("Remove"), style=wx.BU_EXACTFIT)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self._on_add_loinc_button_pressed, self._BTN_add_loinc)
		self.Bind(wx.EVT_BUTTON, self._on_remove_loincs_button_pressed, self._BTN_remove_loincs)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: wxgSubstanceEAPnl.__set_properties
		self.SetScrollRate(10, 10)
		self._TCTRL_substance.SetToolTip(_("Enter the name of the substance.\n\nExamples:\n- metoprolol\n- tobacco\n- alcohol\n- marihuana\n- aloe vera\n- ibuprofen"))
		self._HL_atc_list.SetToolTip(_("Browse ATC list."))
		self._TCTRL_instructions.SetToolTip(_("Generic intake instructions for this substance."))
		self._HL_loinc_list.SetToolTip(_("Browse LOINC list."))
		self._BTN_add_loinc.SetToolTip(_("Add LOINC code to list of LOINC codes to monitor."))
		self._BTN_remove_loincs.SetToolTip(_("Remove selected LOINC codes from the list of codes to monitor."))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: wxgSubstanceEAPnl.__do_layout
		_gszr_main = wx.FlexGridSizer(6, 2, 1, 3)
		__szr_loinc_selection = wx.BoxSizer(wx.HORIZONTAL)
		__lbl_substance = wx.StaticText(self, wx.ID_ANY, _("Substance"))
		__lbl_substance.SetForegroundColour(wx.Colour(255, 0, 0))
		_gszr_main.Add(__lbl_substance, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._TCTRL_substance, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add(self._HL_atc_list, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._PRW_atc, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		__lbl_instructions = wx.StaticText(self, wx.ID_ANY, _("Instructions"))
		_gszr_main.Add(__lbl_instructions, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(self._TCTRL_instructions, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add(self._HL_loinc_list, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		__szr_loinc_selection.Add(self._PRW_loinc, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.RIGHT, 3)
		__szr_loinc_selection.Add(self._BTN_add_loinc, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		_gszr_main.Add(__szr_loinc_selection, 1, wx.EXPAND, 0)
		_gszr_main.Add((20, 20), 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add(self._LCTRL_loincs, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add((20, 20), 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		_gszr_main.Add(self._BTN_remove_loincs, 0, wx.ALIGN_CENTER, 0)
		self.SetSizer(_gszr_main)
		_gszr_main.Fit(self)
		_gszr_main.AddGrowableRow(4)
		_gszr_main.AddGrowableCol(1)
		self.Layout()
		# end wxGlade

	def _on_add_loinc_button_pressed(self, event):  # wxGlade: wxgSubstanceEAPnl.<event_handler>
		print("Event handler '_on_add_loinc_button_pressed' not implemented!")
		event.Skip()

	def _on_remove_loincs_button_pressed(self, event):  # wxGlade: wxgSubstanceEAPnl.<event_handler>
		print("Event handler '_on_remove_loincs_button_pressed' not implemented!")
		event.Skip()

# end of class wxgSubstanceEAPnl
