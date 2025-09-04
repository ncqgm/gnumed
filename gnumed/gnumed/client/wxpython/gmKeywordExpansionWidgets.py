# -*- coding: utf-8 -*-
"""GNUmed keyword expansion widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import re as regex


import wx
import wx.stc


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.business import gmKeywordExpansion
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')

_text_expansion_fillin_regex = r'\$\[[^]]*\]\$'

#============================================================
class cKeywordExpansion_TextCtrlMixin():

	def __init__(self, *args, **kwargs):
		if not isinstance(self, (wx.TextCtrl, wx.stc.StyledTextCtrl)):
			raise TypeError('[%s]: can only be applied to wx.TextCtrl or wx.stc.StyledTextCtrl, not [%s]' % (cKeywordExpansion_TextCtrlMixin, self.__class__.__name__))

	#--------------------------------------------------------
	def enable_keyword_expansions(self):
		pattern = r"[!?'.,:;)}\]\r\n\s\t" + r'"]+'
		self.__keyword_separators = regex.compile(pattern)
		self.Bind(wx.EVT_CHAR, self.__on_char_in_keyword_expansion_mixin)

	#--------------------------------------------------------
	def disable_keyword_expansions(self):
		self.Unbind(wx.EVT_CHAR)

	#--------------------------------------------------------
	def attempt_expansion(self, show_list_if_needed=False):

		visible, caret_pos_in_line, line_no = self.PositionToXY(self.InsertionPoint)
		line = self.GetLineText(line_no)
		keyword_candidate = self.__keyword_separators.split(line[:caret_pos_in_line])[-1]

		if (
			(show_list_if_needed is False)
				and
			(keyword_candidate != '$$steffi')			# Easter Egg ;-)
				and
			(keyword_candidate not in [ r[0] for r in gmKeywordExpansion.get_textual_expansion_keywords() ])
		):
			return

		# why does this work despite the wx.TextCtrl docs saying that
		# InsertionPoint values cannot be used as indices into strings ?
		# because we never cross an EOL which is the only documented
		# reason for insertion point to be off the string index
		start = self.InsertionPoint - len(keyword_candidate)
		wx.CallAfter(self.__replace_keyword_with_expansion, keyword = keyword_candidate, position = start, show_list_if_needed = show_list_if_needed)
		return

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __on_char_in_keyword_expansion_mixin(self, evt):
		evt.Skip()

		# empty ?
		if self.LastPosition == 1:
			return

		char = chr(evt.GetUnicodeKey())

		user_wants_expansion_attempt = False
		if evt.GetModifiers() == (wx.MOD_CMD | wx.MOD_ALT):	# portable CTRL-ALT-...
			if evt.GetKeyCode() == wx.WXK_RETURN:			# CTRL-ALT-ENTER
				user_wants_expansion_attempt = True
			elif evt.GetKeyCode() == 20:					# CTRL-ALT-T
				user_wants_expansion_attempt = True
			else:
				return

		if user_wants_expansion_attempt is False:
			# user did not press CTRL-ALT-ENTER,
			# however, did they last enter a
			# "keyword separator", active character ?
			if self.__keyword_separators.match(char) is None:
				return

		self.attempt_expansion(show_list_if_needed = user_wants_expansion_attempt)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __replace_keyword_with_expansion(self, keyword=None, position=None, show_list_if_needed=False):

		expansion = expand_keyword(parent = self, keyword = keyword, show_list_if_needed = show_list_if_needed)
		if expansion is None:
			return
		if expansion == '':
			return

		if not self.IsMultiLine():
			expansion_lines = gmTools.strip_leading_empty_lines (
				lines = gmTools.strip_trailing_empty_lines (
					text = expansion,
					return_list = True
				),
				return_list = True
			)
			if len(expansion_lines) == 0:
				return
			if len(expansion_lines) == 1:
				expansion = expansion_lines[0]
			else:
				msg = _(
					'The fragment <%s> expands to multiple lines !\n'
					'\n'
					'This text field can hold one line only, hwoever.\n'
					'\n'
					'Please select the line you want to insert:'
				) % keyword
				expansion = gmListWidgets.get_choices_from_list (
					parent = self,
					msg = msg,
					caption = _('Adapting multi-line expansion to single-line text field'),
					choices = expansion_lines,
					selections = [0],
					columns = [_('Keyword expansion lines')],
					single_selection = True,
					can_return_empty = False
				)
				if expansion is None:
					return

		self.Replace (
			position,
			position + len(keyword),
			expansion
		)

		self.SetInsertionPoint(position + len(expansion) + 1)
		self.ShowPosition(position + len(expansion) + 1)

		return

#============================================================
from Gnumed.wxGladeWidgets import wxgTextExpansionEditAreaPnl

class cTextExpansionEditAreaPnl(wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwds):

		try:
			data = kwds['expansion']
			del kwds['expansion']
		except KeyError:
			data = None

		wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl.__init__(self, *args, **kwds)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

#		self.__init_ui()
		self.__register_interests()

		self.__data_filename = None

	#--------------------------------------------------------
#	def __init_ui(self, expansion=None):
#		self._BTN_select_data_file.Enable(False)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		has_expansion = (
			(self._TCTRL_expansion.GetValue().strip() != '')
				or
			(self.__data_filename is not None)
				or
			((self.data is not None) and (self.data['is_textual'] is False))
		)

		if has_expansion:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_expansion, valid = True)
			self.display_tctrl_as_valid(tctrl = self._TCTRL_data_file, valid = True)
		else:
			validity = False
			self.StatusText = _('Cannot save keyword expansion without text or data expansion.')
			self.display_tctrl_as_valid(tctrl = self._TCTRL_expansion, valid = False)
			self.display_tctrl_as_valid(tctrl = self._TCTRL_data_file, valid = False)
			if self.data is None:
				self._TCTRL_expansion.SetFocus()
			else:
				if self.data['is_textual']:
					self._TCTRL_expansion.SetFocus()
				else:
					self._BTN_select_data_file.SetFocus()

		if self._TCTRL_keyword.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_keyword, valid = False)
			self.StatusText = _('Cannot save keyword expansion without keyword.')
			self._TCTRL_keyword.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_keyword, valid = True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		expansion = gmKeywordExpansion.create_keyword_expansion (
			keyword = self._TCTRL_keyword.GetValue().strip(),
			text = self._TCTRL_expansion.GetValue(),
			data_file = self.__data_filename,
			public = self._RBTN_public.GetValue()
		)

		if expansion is False:
			return False

		expansion['is_encrypted'] = self._CHBOX_is_encrypted.IsChecked()
		expansion.save()

		self.data = expansion
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['expansion'] = self._TCTRL_expansion.GetValue().strip()
		self.data['is_encrypted'] = self._CHBOX_is_encrypted.IsChecked()
		self.data.save()

		if self.__data_filename is not None:
			self.data.update_data_from_file(filename = self.__data_filename)

		return True
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self.__data_filename = None

		self._TCTRL_keyword.SetValue('')
		self._TCTRL_keyword.Enable(True)

		self._LBL_data.Enable(False)
		self._BTN_select_data_file.Enable(False)
		self._TCTRL_data_file.SetValue('')
		self._CHBOX_is_encrypted.SetValue(False)
		self._CHBOX_is_encrypted.Enable(False)

		self._LBL_text.Enable(False)
		self._TCTRL_expansion.SetValue('')
		self._TCTRL_expansion.Enable(False)

		self._RBTN_public.Enable(False)
		self._RBTN_private.Enable(False)
		self._RBTN_public.SetValue(1)

		self._TCTRL_keyword.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_from_existing()

		self._TCTRL_keyword.SetValue('%s%s' % (self.data, _('___copy')))
		self._TCTRL_keyword.Enable(True)

		self._RBTN_public.Enable(True)
		self._RBTN_private.Enable(True)

		self._TCTRL_keyword.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self.__data_filename = None

		self._TCTRL_keyword.SetValue(self.data['keyword'])
		self._TCTRL_keyword.Enable(False)

		if self.data['is_textual']:
			self._LBL_text.Enable(True)
			self._TCTRL_expansion.SetValue(gmTools.coalesce(self.data['expansion'], ''))

			self._LBL_data.Enable(False)
			self._BTN_select_data_file.Enable(False)
			self._TCTRL_data_file.SetValue('')
			self._CHBOX_is_encrypted.SetValue(False)
			self._CHBOX_is_encrypted.Enable(False)
		else:
			self._LBL_text.Enable(False)
			self._TCTRL_expansion.SetValue('')

			self._LBL_data.Enable(True)
			self._BTN_select_data_file.Enable(True)
			self._TCTRL_data_file.SetValue(_('Size: %s') % gmTools.size2str(self.data['data_size']))
			self._CHBOX_is_encrypted.SetValue(self.data['is_encrypted'])
			self._CHBOX_is_encrypted.Enable(True)

		self._RBTN_public.Enable(False)
		self._RBTN_private.Enable(False)
		if self.data['public_expansion']:
			self._RBTN_public.SetValue(1)
		else:
			self._RBTN_private.SetValue(1)

		if self.data['is_textual']:
			self._TCTRL_expansion.SetFocus()
		else:
			self._BTN_select_data_file.SetFocus()
	#----------------------------------------------------------------
	# event handling
	#----------------------------------------------------------------
	def __register_interests(self):
		self._TCTRL_keyword.Bind(wx.EVT_TEXT, self._on_keyword_modified)
		self._TCTRL_expansion.Bind(wx.EVT_TEXT, self._on_expansion_modified)
	#----------------------------------------------------------------
	def _on_keyword_modified(self, evt):
		if self._TCTRL_keyword.GetValue().strip() == '':
			self._LBL_text.Enable(False)
			self._TCTRL_expansion.Enable(False)
			self._LBL_data.Enable(False)
			self._BTN_select_data_file.Enable(False)
			self._CHBOX_is_encrypted.Enable(False)
			self._RBTN_public.Enable(False)
			self._RBTN_private.Enable(False)
			return

		# keyword is not empty
		# mode must be new(_from_existing) or else
		# we cannot modify the keyword in the first place
		self._LBL_text.Enable(True)
		self._TCTRL_expansion.Enable(True)
		self._LBL_data.Enable(True)
		self._BTN_select_data_file.Enable(True)
		self._RBTN_public.Enable(True)
		self._RBTN_private.Enable(True)
	#----------------------------------------------------------------
	def _on_expansion_modified(self, evt):
		if self._TCTRL_expansion.GetValue().strip() == '':
			self._LBL_data.Enable(True)
			self._BTN_select_data_file.Enable(True)
			return

		self.__data_filename = None
		self._LBL_data.Enable(False)
		self._BTN_select_data_file.Enable(False)
		self._TCTRL_data_file.SetValue('')
		self._CHBOX_is_encrypted.Enable(False)
	#----------------------------------------------------------------
	def _on_select_data_file_button_pressed(self, event):
		wildcards = [
			"%s (*)|*" % _('all files'),
			"%s (*.*)|*.*" % _('all files (Windows)')
		]

		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose the file containing the data snippet'),
			wildcard = '|'.join(wildcards),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self.__data_filename = dlg.GetPath()
			self._TCTRL_data_file.SetValue(self.__data_filename)
			self._CHBOX_is_encrypted.SetValue(False)
			self._CHBOX_is_encrypted.Enable(True)

		dlg.DestroyLater()

#============================================================
def configure_keyword_text_expansion(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#----------------------
	def delete(expansion=None):
		gmKeywordExpansion.delete_keyword_expansion(pk = expansion['pk_expansion'])
		return True
	#----------------------
	def edit(expansion=None):
		ea = cTextExpansionEditAreaPnl(parent, -1, expansion = expansion)
		dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea)
		if expansion is None:
			title = _('Adding keyword expansion')
		else:
			title = _('Editing keyword expansion "%s"') % expansion['keyword']
		dlg.SetTitle(title)
		if dlg.ShowModal() == wx.ID_OK:
			return True

		return False
	#----------------------
	def tooltip(expansion):
		return expansion.format()
	#----------------------
	def refresh(lctrl=None):
		expansions = gmKeywordExpansion.get_keyword_expansions(order_by = 'is_textual DESC, keyword, public_expansion', force_reload = True)
		items = [[
				e['keyword'],
				gmTools.bool2subst(e['is_textual'], _('text'), _('data')),
				gmTools.bool2subst(e['public_expansion'], _('public'), _('private'))
			] for e in expansions
		]
		lctrl.set_string_items(items)
		lctrl.set_data(expansions)
	#----------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the keyword you want to edit !\n'),
		caption = _('Editing keyword-based expansions ...'),
		columns = [_('Keyword'), _('Type'), _('Scope')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = tooltip
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgTextExpansionFillInDlg

class cTextExpansionFillInDlg(wxgTextExpansionFillInDlg.wxgTextExpansionFillInDlg):

	def __init__(self, *args, **kwds):
		wxgTextExpansionFillInDlg.wxgTextExpansionFillInDlg.__init__(self, *args, **kwds)

		self.__expansion = None
		self.__left_splitter = ''
		self.__right_splitter = ''
		self.__init_ui()
	#---------------------------------------------
	def __init_ui(self):
		self._LBL_top_part.SetLabel('')
		font = self._LBL_left_part.GetFont()
		font.SetPointSize(pointSize = font.GetPointSize() + 1)
		self._LBL_left_part.SetFont(font)
		self._LBL_left_part.SetLabel('')
		self._LBL_left_part.Hide()
		font = self._TCTRL_fillin.GetFont()
		font.SetPointSize(pointSize = font.GetPointSize() + 1)
		self._TCTRL_fillin.SetFont(font)
		self._TCTRL_fillin.SetValue('')
		self._TCTRL_fillin.SetBackgroundColour('yellow')
		self._TCTRL_fillin.Disable()
		self._TCTRL_fillin.Hide()
		font = self._LBL_right_part.GetFont()
		font.SetPointSize(pointSize = font.GetPointSize() + 1)
		self._LBL_right_part.SetFont(font)
		self._LBL_right_part.SetLabel('')
		self._LBL_right_part.Hide()
		self._LBL_bottom_part.SetLabel('')
		self._BTN_OK.Disable()
		self._BTN_forward.Disable()
		self._BTN_cancel.SetFocus()
		self._LBL_hint.SetLabel('')
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
			self._LBL_left_part.SetLabel('')
			self._LBL_left_part.Hide()
			self._TCTRL_fillin.SetValue('')
			self._TCTRL_fillin.Disable()
			self._TCTRL_fillin.Hide()
			self._LBL_right_part.SetLabel('')
			self._LBL_right_part.Hide()
			self._LBL_bottom_part.SetLabel('')
			self._BTN_OK.Enable()
			self._BTN_forward.Disable()
			self._BTN_OK.SetDefault()
			return

		# yes
		top, fillin, bottom = regex.split(r'(' + _text_expansion_fillin_regex + r')', self.__filled_in, maxsplit = 1)
		top_parts = top.rsplit('\n', 1)
		top_part = top_parts[0]
		if len(top_parts) == 1:
			self.__left_splitter = ''
			left_part = ''
		else:
			self.__left_splitter = '\n'
			left_part = top_parts[1]
		bottom_parts = bottom.split('\n', 1)
		if len(bottom_parts) == 1:
			parts = bottom_parts[0].split(' ', 1)
			right_part = parts[0]
			if len(parts) == 1:
				self.__right_splitter = ''
				bottom_part = ''
			else:
				self.__right_splitter = ' '
				bottom_part = parts[1]
		else:
			self.__right_splitter = '\n'
			right_part = bottom_parts[0]
			bottom_part =  bottom_parts[1]
		hint = fillin.strip('$').strip('[').strip(']').strip()
		self._LBL_top_part.SetLabel(top_part)
		self._LBL_left_part.SetLabel(left_part)
		self._LBL_left_part.Show()
		self._TCTRL_fillin.Enable()
		self._TCTRL_fillin.SetValue('')
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

	filled_in_expansion = property(_get_filled_in)
	#---------------------------------------------
	def _set_keyword(self, keyword):
		self.SetTitle(_('Expanding <%s>') % keyword)

	keyword = property(lambda x:x, _set_keyword)
	#---------------------------------------------
	# event handlers
	#---------------------------------------------
	def _on_forward_button_pressed(self, event):
		self.__goto_next_fillin()

#============================================================
def expand_keyword(parent=None, keyword=None, show_list_if_needed=False):
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

	if show_list_if_needed:
		candidates = gmKeywordExpansion.get_matching_textual_keywords(fragment = keyword)
		if len(candidates) == 0:
			return None
		if len(candidates) == 1:
			keyword = candidates[0]
		else:
			keyword = gmListWidgets.get_choices_from_list (
				parent = parent,
				msg = _(
					'Several macro keywords match the fragment [%s].\n'
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

	expansion = gmKeywordExpansion.expand_keyword(keyword = keyword)

	# not found
	if expansion is None:
		return None

	# no replacement necessary:
	if expansion.strip() == '':
		return expansion

	if regex.search(_text_expansion_fillin_regex, expansion) is not None:
		dlg = cTextExpansionFillInDlg(None, -1)
		dlg.keyword = keyword
		dlg.expansion = expansion
		button = dlg.ShowModal()
		if button == wx.ID_OK:
			expansion = dlg.filled_in_expansion
		dlg.DestroyLater()

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
		expansion = """HEMORR²HAGES: Blutungsrisiko unter OAK
--------------------------------------
Am Heart J. 2006 Mar;151(3):713-9.

$[1 oder 0 eingeben]$ H epatische oder Nierenerkrankung
$[1 oder 0 eingeben]$ E thanolabusus
$[1 oder 0 eingeben]$ M alignom
$[1 oder 0 eingeben]$ O ld patient (> 75 Jahre)
$[1 oder 0 eingeben]$ R eduzierte Thrombozytenzahl/-funktion
$[2 oder 0 eingeben]$ R²ekurrente (frühere) große Blutung
$[1 oder 0 eingeben]$ H ypertonie (unkontrolliert)
$[1 oder 0 eingeben]$ A nämie
$[1 oder 0 eingeben]$ G enetische Faktoren
$[1 oder 0 eingeben]$ E xzessives Sturzrisiko
$[1 oder 0 eingeben]$ S Schlaganfall in der Anamnese
--------------------------------------
Summe   Rate großer Blutungen
        pro 100 Patientenjahre
 0          1.9
 1          2.5
 2          5.3
 3          8.4
 4         10.4
>4         12.3

Bewertung: Summe = $[Summe ausrechnen und bewerten]$"""

		#app = 
#		wx.PyWidgetTester(size = (600, 600))
		dlg = cTextExpansionFillInDlg(None, -1)
		dlg.expansion = expansion
		dlg.ShowModal()
		#app.MainLoop()

	#----------------------------------------
	test_fillin()
