# -*- coding: utf8 -*-
"""GNUmed text expansion widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import re as regex


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')

_text_expansion_fillin_regex = r'\$<.*>\$'

#============================================================
from Gnumed.wxGladeWidgets import wxgTextExpansionEditAreaPnl

class cTextExpansionEditAreaPnl(wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwds):

		try:
			data = kwds['keyword']
			del kwds['keyword']
		except KeyError:
			data = None

		wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl.__init__(self, *args, **kwds)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	def __init_ui(self, keyword=None):

		if keyword is not None:
			self.data = keyword
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._TCTRL_keyword.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_keyword, valid = False)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without keyword.'), beep = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_keyword, valid = True)

		if self._TCTRL_expansion.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_expansion, valid = False)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without expansion text.'), beep = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_expansion, valid = True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		kwd = self._TCTRL_keyword.GetValue().strip()
		saved = gmPG2.add_text_expansion (
			keyword = kwd,
			expansion = self._TCTRL_expansion.GetValue(),
			public = self._RBTN_public.GetValue()
		)
		if not saved:
			return False

		self.data = kwd
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		kwd = self._TCTRL_keyword.GetValue().strip()
		gmPG2.edit_text_expansion (
			keyword = kwd,
			expansion = self._TCTRL_expansion.GetValue()
		)
		self.data = kwd
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_keyword.SetValue(u'')
		self._TCTRL_keyword.Enable(True)
		self._TCTRL_expansion.SetValue(u'')
		self._TCTRL_expansion.Enable(False)
		self._RBTN_public.Enable(True)
		self._RBTN_private.Enable(True)
		self._RBTN_public.SetValue(1)

		self._TCTRL_keyword.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._TCTRL_keyword.SetValue(u'%s%s' % (self.data, _(u'___copy')))
		self._TCTRL_keyword.Enable(True)
		expansion = gmPG2.expand_keyword(keyword = self.data)
		self._TCTRL_expansion.SetValue(gmTools.coalesce(expansion, u''))
		self._TCTRL_expansion.Enable(True)
		self._RBTN_public.Enable(True)
		self._RBTN_private.Enable(True)
		self._RBTN_public.SetValue(1)

		self._TCTRL_keyword.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_keyword.SetValue(self.data)
		self._TCTRL_keyword.Enable(False)
		expansion = gmPG2.expand_keyword(keyword = self.data)
		self._TCTRL_expansion.SetValue(gmTools.coalesce(expansion, u''))
		self._TCTRL_expansion.Enable(True)
		self._RBTN_public.Enable(False)
		self._RBTN_private.Enable(False)

		self._TCTRL_expansion.SetFocus()
	#----------------------------------------------------------------
	# event handling
	#----------------------------------------------------------------
	def __register_interests(self):
		self._TCTRL_keyword.Bind(wx.EVT_TEXT, self._on_keyword_modified)
	#----------------------------------------------------------------
	def _on_keyword_modified(self, evt):
		if self._TCTRL_keyword.GetValue().strip() == u'':
			self._TCTRL_expansion.Enable(False)
		else:
			self._TCTRL_expansion.Enable(True)
#============================================================
def configure_keyword_text_expansion(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#----------------------
	def delete(keyword=None):
		gmPG2.delete_text_expansion(keyword = keyword)
		return True
	#----------------------
	def edit(keyword=None):
		ea = cTextExpansionEditAreaPnl(parent, -1, keyword = keyword)
		dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea)
		dlg.SetTitle (
			gmTools.coalesce(keyword, _('Adding text expansion'), _('Editing text expansion "%s"'))
		)
		if dlg.ShowModal() == wx.ID_OK:
			return True

		return False
	#----------------------
	def refresh(lctrl=None):
		kwds = [ [
				r[0],
				gmTools.bool2subst(r[1], gmTools.u_checkmark_thick, u''),
				gmTools.bool2subst(r[2], gmTools.u_checkmark_thick, u''),
				r[3]
			] for r in gmPG2.get_text_expansion_keywords()
		]
		data = [ r[0] for r in gmPG2.get_text_expansion_keywords() ]
		lctrl.set_string_items(kwds)
		lctrl.set_data(data)
	#----------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the keyword you want to edit !\n'),
		caption = _('Editing keyword-based text expansions ...'),
		columns = [_('Keyword'), _('Public'), _('Private'), _('Owner')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
from Gnumed.wxGladeWidgets import wxgTextExpansionFillInDlg

class cTextExpansionFillInDlg(wxgTextExpansionFillInDlg.wxgTextExpansionFillInDlg):

	def __init__(self, *args, **kwds):
		wxgTextExpansionFillInDlg.wxgTextExpansionFillInDlg.__init__(self, *args, **kwds)

		self.__expansion = None
		self.__init_ui()
	#---------------------------------------------
	def __init_ui(self):
		self._LBL_top_part.SetLabel(u'')
		self._LBL_left_part.SetLabel(u'')
		self._LBL_left_part.Hide()
		self._TCTRL_fillin.SetValue(u'')
		self._TCTRL_fillin.Disable()
		self._TCTRL_fillin.Hide()
		self._LBL_right_part.SetLabel(u'')
		self._LBL_right_part.Hide()
		self._LBL_bottom_part.SetLabel(u'')
		self._BTN_OK.Disable()
		self._BTN_forward.Disable()
		self._BTN_cancel.SetFocus()
		self._LBL_hint.SetLabel(u'')
	#---------------------------------------------
	def __goto_next_fillin(self):
		if self.__expansion is None:
			return

		if self.__new_expansion:
			self.__filled_in = self.__expansion
			self.__new_expansion = False
		else:
			self.__filled_in = (
				self._LBL_top_part.GetLabel() +
				self.__left_splitter +
				self._LBL_left_part.GetLabel() +
				self._TCTRL_fillin.GetValue().strip() +
				self._LBL_right_part.GetLabel() +
				self.__right_splitter +
				self._LBL_bottom_part.GetLabel()
			)

		# anything to fill in ?
		if regex.search(_text_expansion_fillin_regex, self.__filled_in) is None:
			# no
			self._LBL_top_part.SetLabel(self.__filled_in)
			self._LBL_left_part.SetLabel(u'')
			self._LBL_left_part.Hide()
			self._TCTRL_fillin.SetValue(u'')
			self._TCTRL_fillin.Disable()
			self._TCTRL_fillin.Hide()
			self._LBL_right_part.SetLabel(u'')
			self._LBL_right_part.Hide()
			self._LBL_bottom_part.SetLabel(u'')
			self._BTN_OK.Enable()
			self._BTN_forward.Disable()
			self._BTN_OK.SetDefault()
			return

		# yes
		top, fillin, bottom = regex.split(r'(' + _text_expansion_fillin_regex + r')', self.__filled_in, maxsplit = 1)
		top_parts = top.rsplit(u'\n', 1)
		top_part = top_parts[0]
		if len(top_parts) == 1:
			self.__left_splitter = u''
			left_part = u''
		else:
			self.__left_splitter = u'\n'
			left_part = top_parts[1]
		bottom_parts = bottom.split(u'\n', 1)
		if len(bottom_parts) == 1:
			parts = bottom_parts[0].split(u' ', 1)
			right_part = parts[0]
			if len(parts) == 1:
				self.__right_splitter = u''
				bottom_part = u''
			else:
				self.__right_splitter = u' '
				bottom_part = parts[1]
		else:
			self.__right_splitter = u'\n'
			right_part = bottom_parts[0]
			bottom_part =  bottom_parts[1]
		hint = fillin.strip('$').strip('<').strip('>').strip()
		self._LBL_top_part.SetLabel(top_part)
		self._LBL_left_part.SetLabel(left_part)
		self._LBL_left_part.Show()
		self._TCTRL_fillin.Enable()
		self._TCTRL_fillin.SetValue(u'')
		self._TCTRL_fillin.Show()
		self._LBL_right_part.SetLabel(right_part)
		self._LBL_right_part.Show()
		self._LBL_bottom_part.SetLabel(bottom_part)
		self._BTN_OK.Disable()
		self._BTN_forward.Enable()
		self._BTN_forward.SetDefault()
		self._LBL_hint.SetLabel(hint)
		self._TCTRL_fillin.SetFocus()

		self.Layout()
		self.Fit()
	#---------------------------------------------
	# properties
	#---------------------------------------------
	def _get_expansion(self):
		return self.__expansion

	def _set_expansion(self, expansion):
		self.__expansion = expansion
		self.__new_expansion = True
		self.__goto_next_fillin()
		return

	expansion = property(_get_expansion, _set_expansion)
	#---------------------------------------------
	def _get_filled_in(self):
		return self.__filled_in

	filled_in_expansion = property(_get_filled_in, lambda x:x)
	#---------------------------------------------
	def _on_forward_button_pressed(self, event):
		self.__goto_next_fillin()
#============================================================
def expand_keyword(parent=None, keyword=None, show_list=False):
	"""Expand keyword and replace inside it.

	Returns:
		None: aborted or no expansion available
		u'': empty expansion
		u'<text>' the expansion
	"""
	if keyword is None:
		return None

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if show_list:
		candidates = gmPG2.get_keyword_expansion_candidates(keyword = keyword)
		if len(candidates) == 0:
			return None
		if len(candidates) == 1:
			keyword = candidates[0]
		else:
			keyword = gmListWidgets.get_choices_from_list (
				parent = parent,
				msg = _(
					'Several macros match the keyword [%s].\n'
					'\n'
					'Please select the expansion you want to happen.'
				) % keyword,
				caption = _('Selecting text macro'),
				choices = candidates,
				columns = [_('Keyword')],
				single_selection = True,
				can_return_empty = False
			)
			if keyword is None:
				return None

	expansion = gmPG2.expand_keyword(keyword = keyword)

	# not found
	if expansion is None:
		return None

	# no replacement necessary:
	if expansion.strip() == u'':
		return expansion

	if regex.search(_text_expansion_fillin_regex, expansion) is not None:
		dlg = cTextExpansionFillInDlg(None, -1)
		dlg.expansion = expansion
		button = dlg.ShowModal()
		if button == wx.ID_OK:
			expansion = dlg.filled_in_expansion
		dlg.Destroy()

	return expansion

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_fillin():
		expansion = u"""HEMORR²HAGES: Blutungsrisiko unter OAK
--------------------------------------
Am Heart J. 2006 Mar;151(3):713-9.

$<1 oder 0 eingeben>$ H epatische oder Nierenerkrankung
$<1 oder 0 eingeben>$ E thanolabusus
$<1 oder 0 eingeben>$ M alignom
$<1 oder 0 eingeben>$ O ld patient (> 75 Jahre)
$<1 oder 0 eingeben>$ R eduzierte Thrombozytenzahl/-funktion
$<2 oder 0 eingeben>$ R²ekurrente (frühere) große Blutung
$<1 oder 0 eingeben>$ H ypertonie (unkontrolliert)
$<1 oder 0 eingeben>$ A nämie
$<1 oder 0 eingeben>$ G enetische Faktoren
$<1 oder 0 eingeben>$ E xzessives Sturzrisiko
$<1 oder 0 eingeben>$ S Schlaganfall in der Anamnese
--------------------------------------
Summe   Rate großer Blutungen
        pro 100 Patientenjahre
 0          1.9
 1          2.5
 2          5.3
 3          8.4
 4         10.4
>4         12.3

Bewertung: Summe = $<Summe ausrechnen und bewerten>$"""

		app = wx.PyWidgetTester(size = (600, 600))
		dlg = cTextExpansionFillInDlg(None, -1)
		dlg.expansion = expansion
		dlg.ShowModal()
		#app.MainLoop()
	#----------------------------------------
	test_fillin()
