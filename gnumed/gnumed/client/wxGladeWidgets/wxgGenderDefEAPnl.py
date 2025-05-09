# -*- coding: UTF-8 -*-
#
# generated by wxGlade
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
from Gnumed.wxpython import gmTextCtrl
# end wxGlade


class wxgGenderDefEAPnl(wx.ScrolledWindow):
	def __init__(self, *args, **kwds):
		# begin wxGlade: wxgGenderDefEAPnl.__init__
		kwds["style"] = kwds.get("style", 0) | wx.BORDER_NONE | wx.TAB_TRAVERSAL
		wx.ScrolledWindow.__init__(self, *args, **kwds)
		self.SetScrollRate(10, 10)

		_gszr_main = wx.FlexGridSizer(5, 2, 1, 3)

		__lbl_name = wx.StaticText(self, wx.ID_ANY, _("Name"))
		__lbl_name.SetForegroundColour(wx.Colour(255, 0, 0))
		__lbl_name.SetToolTip(_("The name for this gender definition."))
		_gszr_main.Add(__lbl_name, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		self._TCTRL_name = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		_gszr_main.Add(self._TCTRL_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

		__lbl_name_l10n = wx.StaticText(self, wx.ID_ANY, _("Translation"), style=wx.ALIGN_CENTER_HORIZONTAL)
		__lbl_name_l10n.SetToolTip(_("Translation of name into your language."))
		_gszr_main.Add(__lbl_name_l10n, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		self._TCTRL_name_l10n = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		_gszr_main.Add(self._TCTRL_name_l10n, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

		__lbl_abbreviation = wx.StaticText(self, wx.ID_ANY, _("Abbreviation"))
		__lbl_abbreviation.SetForegroundColour(wx.Colour(255, 0, 0))
		__lbl_abbreviation.SetToolTip(_("An abbreviation for this gender definition."))
		_gszr_main.Add(__lbl_abbreviation, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		__szr_abbreviation = wx.BoxSizer(wx.HORIZONTAL)
		_gszr_main.Add(__szr_abbreviation, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

		self._TCTRL_abbreviation = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		__szr_abbreviation.Add(self._TCTRL_abbreviation, 1, wx.EXPAND, 0)

		_lbl_abbreviation_l10n = wx.StaticText(self, wx.ID_ANY, _("Translation:"), style=wx.ALIGN_CENTER_HORIZONTAL)
		_lbl_abbreviation_l10n.SetToolTip(_("Translation of abbreviation into your language."))
		__szr_abbreviation.Add(_lbl_abbreviation_l10n, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)

		self._TCTRL_l10n_abbreviation = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		__szr_abbreviation.Add(self._TCTRL_l10n_abbreviation, 1, wx.EXPAND | wx.LEFT, 3)

		__lbl_symbol = wx.StaticText(self, wx.ID_ANY, _("Symbol"))
		__lbl_symbol.SetToolTip(_("Symbolic representation for this gender."))
		_gszr_main.Add(__lbl_symbol, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		__szr_generic = wx.BoxSizer(wx.HORIZONTAL)
		_gszr_main.Add(__szr_generic, 1, wx.EXPAND, 0)

		self._TCTRL_symbol = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		__szr_generic.Add(self._TCTRL_symbol, 1, wx.EXPAND, 0)

		_lbl_symbol_l10n = wx.StaticText(self, wx.ID_ANY, _("Alternative:"), style=wx.ALIGN_CENTER_HORIZONTAL)
		_lbl_symbol_l10n.SetToolTip(_("Symbol for this gender appropriate to your culture."))
		__szr_generic.Add(_lbl_symbol_l10n, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)

		self._TCTRL_symbol_l10n = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		__szr_generic.Add(self._TCTRL_symbol_l10n, 1, wx.EXPAND | wx.LEFT, 3)

		__lbl_comment = wx.StaticText(self, wx.ID_ANY, _("Comment"))
		__lbl_comment.SetToolTip(_("A descriptive comment on this gender definition."))
		_gszr_main.Add(__lbl_comment, 0, wx.ALIGN_CENTER_VERTICAL, 0)

		self._TCTRL_comment = gmTextCtrl.cTextCtrl(self, wx.ID_ANY, "", style=wx.BORDER_NONE)
		_gszr_main.Add(self._TCTRL_comment, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

		_gszr_main.AddGrowableCol(1)
		self.SetSizer(_gszr_main)
		_gszr_main.Fit(self)

		self.Layout()
		# end wxGlade

# end of class wxgGenderDefEAPnl
