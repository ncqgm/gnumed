# -*- coding: utf-8 -*-
"""GNUmed StyledTextCtrl subclass for SOAP editing.

based on: 11/21/2003 - Jeff Grimmett (grimmtooth@softhome.net)
"""
#================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys


import wx
import wx.stc


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.business import gmSoapDefs
from Gnumed.wxpython import gmKeywordExpansionWidgets
from Gnumed.wxpython.gmTextCtrl import cUnicodeInsertion_TextCtrlMixin


_log = logging.getLogger('gm.stc')

#================================================================
class cWxTextCtrlCompatibility_StcMixin():

	def __init__(self, *args, **kwargs):
		if not isinstance(self, wx.stc.StyledTextCtrl):
			raise TypeError('[%s]: can only be applied to wx.stc.StyledTextCtrl, not [%s]' % (cWxTextCtrlCompatibility_StcMixin, self.__class__.__name__))

	#--------------------------------------------------
	# wx.TextCtrl compatibility
	#--------------------------------------------------
	def GetValue(self):
		_log.debug('%s.GetValue() - %s', cWxTextCtrlCompatibility_StcMixin, self.__class__.__name__)
		return self.GetText()

	#--------------------------------------------------
	def SetValue(self, value):
		_log.debug('%s.SetValue() - %s', cWxTextCtrlCompatibility_StcMixin, self.__class__.__name__)
		return self.SetText(value)

	#--------------------------------------------------
	def WriteText(self, value):
		return self.InsertText(self.CurrentPos, value)

	#--------------------------------------------------
	def GetLastPosition(self):
		return self.Length

	LastPosition = property(GetLastPosition)

	#--------------------------------------------------
	def GetNumberOfLines(self):
		return self.LineCount

	#--------------------------------------------------
	def GetLineText(self, line_no):
		return self.GetLine(line_no)

	#--------------------------------------------------
	def GetInsertionPoint(self):
		return self.CurrentPos

	def SetInsertionPoint(self, position):
		self.CurrentPos = position

	InsertionPoint = property(GetInsertionPoint, SetInsertionPoint)

	#--------------------------------------------------
	def ShowPosition(self, position):
		#self.ScrollToLine(self.LineFromPosition(position))
		self.CurrentPos = position
		self.EnsureCaretVisible()

	#--------------------------------------------------
	def IsMultiLine(self):
		return True

	#--------------------------------------------------
	def PositionToXY(self, position):
		try:
			#return wx.stc.StyledTextCtrl.PositionToXY(position)			# does not work
			#return wx.TextAreaBase.PositionToXY(position)					# does not work
			return super(wx.TextAreaBase, self).PositionToXY(position)
		except AttributeError:
			# reimplement for wxPython 2.8,
			# this is moot now, hwoever, since 2.8 returned an (x, y) tuple
			return (True, self.GetColumn(position), self.LineFromPosition(position))

	#--------------------------------------------------
	def Replace(self, start, end, replacement):
		self.SetSelection(start, end)
		self.ReplaceSelection(replacement)
		wx.CallAfter(self.SetSelection, 0, 0)

#----------------------------------------------------------------------
class cSoapSTC(cUnicodeInsertion_TextCtrlMixin, gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin, cWxTextCtrlCompatibility_StcMixin, wx.stc.StyledTextCtrl):

	_MARKER_ADM = 0
	_MARKER_S = 1
	_MARKER_O = 2
	_MARKER_A = 3
	_MARKER_P = 4
	_MARKER_U = 5
	_MARKER_LINE_BG_LIGHT_GREY = 31

	_DEFINED_MARKERS_MASK = (
		_MARKER_ADM
			|
		_MARKER_S
			|
		_MARKER_O
			|
		_MARKER_A
			|
		_MARKER_P
			|
		_MARKER_U
			|
		_MARKER_LINE_BG_LIGHT_GREY
	)

	_DEFINED_MARKER_NUMS = [
		_MARKER_ADM,
		_MARKER_S,
		_MARKER_O,
		_MARKER_A,
		_MARKER_P,
		_MARKER_U,
		_MARKER_LINE_BG_LIGHT_GREY
	]
	_SOAP_MARKER_NUMS = [
		_MARKER_ADM,
		_MARKER_S,
		_MARKER_O,
		_MARKER_A,
		_MARKER_P,
		_MARKER_U
	]
	_SOAP2MARKER = {
		None: _MARKER_ADM,
		' ': _MARKER_ADM,
		'.': _MARKER_ADM,
		's': _MARKER_S,
		'o': _MARKER_O,
		'a': _MARKER_A,
		'p': _MARKER_P,
		'u': _MARKER_U,
		'S': _MARKER_S,
		'O': _MARKER_O,
		'A': _MARKER_A,
		'P': _MARKER_P,
		'U': _MARKER_U
	}
	_MARKER2SOAP = {
		_MARKER_ADM: None,
		_MARKER_S: 's',
		_MARKER_O: 'o',
		_MARKER_A: 'a',
		_MARKER_P: 'p',
		_MARKER_U: 'u'
	}
	_SOAPMARKER2BACKGROUND = {
		_MARKER_ADM: False,
		_MARKER_S: True,
		_MARKER_O: False,
		_MARKER_A: True,
		_MARKER_P: False,
		_MARKER_U: True
	}

	def __init__(self, *args, **kwargs):

		# normalize wxGlade output
		if args[2] == '':
			l_args = list(args)
			l_args[2] = wx.DefaultPosition
			args = tuple(l_args)
		wx.stc.StyledTextCtrl.__init__(self, *args, **kwargs)
		cWxTextCtrlCompatibility_StcMixin.__init__(self)
		gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin.__init__(self)
		cUnicodeInsertion_TextCtrlMixin.__init__(self)

		# wrapping and overflow
		self.SetWrapMode(wx.stc.STC_WRAP_NONE)
		# said to be problematic:
		self.SetEdgeColumn(80)
		self.SetEdgeColour('grey')
		#self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
		self.SetEdgeMode(wx.stc.STC_EDGE_BACKGROUND)

		# EOL style
		self.SetEOLMode(wx.stc.STC_EOL_LF)
		#self.SetViewEOL(1)										# visual debugging
		self.SetViewEOL(0)

		# whitespace handling
		#self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEAFTERINDENT)	# visual debugging
		self.SetViewWhiteSpace(wx.stc.STC_WS_INVISIBLE)
		#self.SetWhitespaceBackground(1, a_color)					# 1 = override lexer
		#self.SetWhitespaceForeground(1, a_color)					# 1 = override lexer

		# caret handling
		#self.SetCaretLineBackground('light goldenrod yellow')
		self.SetCaretLineBackground('khaki')
		self.SetCaretLineVisible(1)

		# margins
		# left margin: 0 pixel widths
		self.SetMarginLeft(0)
		# margin 0: SOAP markers
		self.SetMarginType(0, wx.stc.STC_MARGIN_SYMBOL)
		self.SetMarginWidth(0, 16)
		self.SetMarginMask(0, cSoapSTC._DEFINED_MARKERS_MASK)
		# margin 1 and 2: additional 2-letter markers (not yet supported)
		self.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
		self.SetMarginMask(1, 0)
		self.SetMarginWidth(1, 0)
		self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
		self.SetMarginMask(2, 0)
		self.SetMarginWidth(2, 0)

		# markers
		# can only use ASCII so far, so must make sure translations are ASCII:
		self.MarkerDefine(cSoapSTC._MARKER_ADM, wx.stc.STC_MARK_CHARACTER + ord('.'), 'blue', 'white')
		self.MarkerDefine(cSoapSTC._MARKER_S, wx.stc.STC_MARK_CHARACTER + ord(gmSoapDefs.soap_cat2l10n['s']), 'blue', 'grey96')
		self.MarkerDefine(cSoapSTC._MARKER_O, wx.stc.STC_MARK_CHARACTER + ord(gmSoapDefs.soap_cat2l10n['o']), 'blue', 'white')
		self.MarkerDefine(cSoapSTC._MARKER_A, wx.stc.STC_MARK_CHARACTER + ord(gmSoapDefs.soap_cat2l10n['a']), 'blue', 'grey96')
		self.MarkerDefine(cSoapSTC._MARKER_P, wx.stc.STC_MARK_CHARACTER + ord(gmSoapDefs.soap_cat2l10n['p']), 'blue', 'white')
		self.MarkerDefine(cSoapSTC._MARKER_U, wx.stc.STC_MARK_CHARACTER + ord(gmSoapDefs.soap_cat2l10n['u']), 'blue', 'grey96')
		self.MarkerDefine(cSoapSTC._MARKER_LINE_BG_LIGHT_GREY, wx.stc.STC_MARK_BACKGROUND, 'grey96', 'grey96')

		# unset hotkeys we want to re-define
		#self.CmdKeyClear('t', wx.stc.STC_SCMOD_CTRL)	# does not seem to work
		self.__changing_SOAP_cat = False
		self.__markers_of_prev_line = None
		self.__ensure_has_all_soap_types = False

		# we do our own popup menu
		self.UsePopUp(0)
		self.__build_context_menu()

		# always keep one line of each of .SOAP around
		self.SetText_from_SOAP()

		self.__register_events()

		# text expansion mixin
		self.enable_keyword_expansions()

	#-------------------------------------------------------
	# SOAP-enhanced text setting
	#-------------------------------------------------------
	def SetText(self, *args, **kwargs):
		_log.debug('%s.SetText()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.SetText(self, *args, **kwargs)

	def AddText(self, *args, **kwargs):
		_log.debug('%s.AddText()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.AddText(self, *args, **kwargs)

	def AddStyledText(self, *args, **kwargs):
		_log.debug('%s.AddStyledText()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.AddStyledText(self, *args, **kwargs)

	def InsertText(self, *args, **kwargs):
		_log.debug('%s.InsertText()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.InsertText(self, *args, **kwargs)

	#-------------------------------------------------------
	def ReplaceSelection(self, text):
		sel_start, sel_end = self.GetSelection()
		start_line = self.LineFromPosition(sel_start)
		end_line = start_line + text.count('\n')
		start_line_soap_cat = self.MarkerGet(start_line)
		#_log.debug(u'replacing @ pos %s-%s with %s lines (line %s to line %s)', sel_start, sel_end, text.count(u'\n'), start_line, end_line)
		wx.stc.StyledTextCtrl.ReplaceSelection(self, text)
		if start_line != end_line:
			for target_line in range(start_line, end_line):
				self.MarkerDelete(target_line, -1)
				self.__set_markers_of_line(target_line, start_line_soap_cat)

	#-------------------------------------------------------
	def ReplaceTarget(self, *args, **kwargs):
		_log.debug('%s.ReplaceTarget()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.ReplaceTarget(self, *args, **kwargs)

	def ReplaceTargetRE(self, *args, **kwargs):
		_log.debug('%s.ReplaceTargetRE()', self.__class__.__name__)
		wx.stc.StyledTextCtrl.ReplaceTargetRE(self, *args, **kwargs)

	#-------------------------------------------------------
	# external API
	#-------------------------------------------------------
	def SetText_from_SOAP(self, soap=None, sort_order=None):
		# defaults
		if soap is None:
			#soap = {None: [u'']} # 'soap' will be added below by normalization
			soap = {}
		if sort_order is None:
			sort_order = ['s', 'o', 'a', 'p', None, 'u']

		# normalize input
		for cat in 'soap':
			try:
				soap[cat]
			except KeyError:
				soap[cat] = ['']
		for cat in ['u', None]:
			try:
				soap[cat]
			except KeyError:
				soap[cat] = []
		if '.' in soap:
			soap[None].extend(soap['.'])
			del soap['.']
		if ' ' in soap:
			soap[None].extend(soap[' '])
			del soap[' ']

		# normalize sort order
		for cat in 'soapu':
			if cat not in sort_order:
				sort_order.append(cat)
		if None not in sort_order:
			sort_order.append(None)

		# sort and flatten
		soap_lines = []
		line_categories = []
		for cat in sort_order:
			lines = soap[cat]
			if len(lines) == 0:
				continue
			for line in lines:
				soap_lines.append(line.strip())
				line_categories.append(cat)

		_log.debug('%s.SetText_from_SOAP(): 1 controlled use of .SetText() follows', self.__class__.__name__)
		self.SetText('\n'.join(soap_lines))

		for idx in range(len(line_categories)):
			self.set_soap_cat_of_line(idx, line_categories[idx])

	#-------------------------------------------------------
	def GetText_as_SOAP(self):
		lines = self.GetText().split('\n')
		soap = {}
		for line_idx in range(len(lines)):
			cat = self.get_soap_cat_of_line(line_idx)
			if cat == -1:
				cat = 'u'
			try:
				soap[cat]
			except KeyError:
				soap[cat] = []
			soap[cat].append(lines[line_idx])
		return soap

	soap = property(GetText_as_SOAP)

	#--------------------------------------------------------
	def _get_empty(self):
		soap = self.GetText_as_SOAP()
		for cat in soap:
			if ''.join([ l.strip() for l in soap[cat] ]) != '':
				return False
		return True

	empty = property(_get_empty)

	#-------------------------------------------------------
	def sort_by_SOAP(self, sort_order=None):
		self.SetText_from_SOAP(self.GetText_as_SOAP(), sort_order)

	#-------------------------------------------------------
	def append_soap_line(self, soap_cat):
		#caret_pos = self.CurrentPos
		self.GotoPos(self.Length)
		self.AddText('\n')
		self.set_soap_cat_of_line(self.LineCount, soap_cat)

	#-------------------------------------------------------
	# generic helpers
	#-------------------------------------------------------
	def strip_trailing_whitespace_from_line(self, line):
		line_text = self.GetLine(line)
		line_start = self.PositionFromLine(line)
		line_end = self.GetLineEndPosition(line)
		self.SetTargetStart(line_start)
		self.SetTargetEnd(line_end)
		self.ReplaceTarget(line_text.rstrip())

	#-------------------------------------------------------
	def caret_coords_in_stc(self):
		return self.PointFromPosition(self.CurrentPos)

	#-------------------------------------------------------
	def caret_coords_on_screen(self):
		return self.ClientToScreen(self.caret_coords_in_stc())

	#-------------------------------------------------------
	# internal helpers
	#-------------------------------------------------------
	def __build_context_menu(self):

		# build menu
		self.__popup_menu = wx.Menu(title = _('SOAP Editor Actions:'))

		# sort
		item = self.__popup_menu.Append(-1, _('&Sort lines'), _('Sort lines by SOAP category'))
		self.Bind(wx.EVT_MENU, self.__on_sort_by_soap, item)

		# expand keyword
		item = self.__popup_menu.Append(-1, _('e&Xpand keyword'), _('Expand keyword / macro'))
		self.Bind(wx.EVT_MENU, self.__on_expand_keyword, item)

		# insert unicode
		item = self.__popup_menu.Append(-1, _('Insert &Unicode'), _('Insert a unicode character'))
		self.Bind(wx.EVT_MENU, self.__on_insert_unicode, item)

		self.__popup_menu.AppendSeparator()

		# undo
		# redo

		# submenu "line"
		menu_line = wx.Menu()

		item = menu_line.Append(-1, _('as &Subjective'), _('Set line to category "Subjective"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_Soap, item)
		item = menu_line.Append(-1, _('as &Objective'), _('Set line to category "Objective"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_sOap, item)
		item = menu_line.Append(-1, _('as &Assessment'), _('Set line to category "Assessment"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_soAp, item)
		item = menu_line.Append(-1, _('as &Plan'), _('Set line to category "Plan"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_soaP, item)
		item = menu_line.Append(-1, _('as &Unspecified'), _('Set line to category "unspecified"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_soapU, item)
		item = menu_line.Append(-1, _('as ad&Ministrative'), _('Set line to category "administrative"'))
		self.Bind(wx.EVT_MENU, self.__on_make_line_soapADM, item)
		menu_line.AppendSeparator()
		item = menu_line.Append(-1, _('\u2192 &Clipboard'), _('Copy line to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_line2clipboard, item)
		item = menu_line.Append(-1, _('\u2192 +Clipboard+'), _('Add line to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_add_line2clipboard, item)
		# encrypt

		# submenu "text"
		menu_all = wx.Menu()

		item = menu_all.Append(-1, _('\u2192 &Clipboard'), _('Copy content to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_content2clipboard, item)
		item = menu_all.Append(-1, _('\u2192 +Clipboard+'), _('Add content to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_add_content2clipboard, item)
		# ------
		# cut
		# copy
		# paste
		# delete
		# -------

		# selected region
		self.__menu_selection = wx.Menu()

		item = self.__menu_selection.Append(-1, _('\u2192 &Clipboard'), _('Copy selection to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_region2clipboard, item)
		item = self.__menu_selection.Append(-1, _('\u2192 +Clipboard+'), _('Add selection to clipboard'))
		self.Bind(wx.EVT_MENU, self.__on_add_region2clipboard, item)

		self.__popup_menu.Append(wx.NewId(), _('&Line ...'), menu_line)
		self.__popup_menu.Append(wx.NewId(), _('&Text ...'), menu_all)
		self.__popup_menu.Append(wx.NewId(), _('&Region ...'), self.__menu_selection)

	#-------------------------------------------------------
	def __show_context_menu(self, position):
		sel_start, sel_end = self.GetSelection()
		sel_menu_id = self.__popup_menu.FindItem(_('&Region ...'))
		if sel_start == sel_end:
			self.__popup_menu.Enable(sel_menu_id, False)
		else:
			self.__popup_menu.Enable(sel_menu_id, True)

		self.PopupMenu(self.__popup_menu, position)

	#-------------------------------------------------------
	def __get_clipboard_text(self):
		if wx.TheClipboard.IsOpened():
			_log.debug('clipboard already open')
			return ''
		if not wx.TheClipboard.Open():
			_log.debug('cannot open clipboard')
			return ''
		data_obj = wx.TextDataObject()
		got_it = wx.TheClipboard.GetData(data_obj)
		if not got_it:
			return ''
		return data_obj.Text

	#-------------------------------------------------------
	# context menu handlers
	#-------------------------------------------------------
	def __on_expand_keyword(self, evt):
		self.attempt_expansion(show_list_if_needed = True)

	#-------------------------------------------------------
	def __on_insert_unicode(self, evt):
		self.mixin_insert_unicode_character()

	#-------------------------------------------------------
	def __on_content2clipboard(self, evt):
		txt = self.GetText().strip()
		if txt == '':
			return
		self.CopyText(len(txt), txt)

	#-------------------------------------------------------
	def __on_add_content2clipboard(self, evt):
		txt = self.GetText().strip()
		if txt == '':
			return
		txt = self.__get_clipboard_text() + '\n' + txt
		self.CopyText(len(txt), txt)

	#-------------------------------------------------------
	def __on_region2clipboard(self, evt):
		self.Copy()

	#-------------------------------------------------------
	def __on_add_region2clipboard(self, evt):
		region = self.GetTextRange(self.SelectionStart, self.SelectionEnd)
		if region.strip() == '':
			return
		txt = self.__get_clipboard_text() + '\n' + region
		self.CopyText(len(txt), txt)

	#-------------------------------------------------------
	def __on_line2clipboard(self, evt):
		txt = self.GetLine(self.CurrentLine).strip()
		if txt == '':
			return
		self.CopyText(len(txt), txt)

	#-------------------------------------------------------
	def __on_add_line2clipboard(self, evt):
		txt = self.GetLine(self.CurrentLine).strip()
		if txt == '':
			return
		txt = self.__get_clipboard_text() + '\n' + txt
		self.CopyText(len(txt), txt)

	#-------------------------------------------------------
	def __on_make_line_Soap(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, 's')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_make_line_sOap(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, 'o')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_make_line_soAp(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, 'a')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_make_line_soaP(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, 'p')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_make_line_soapU(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, 'u')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_make_line_soapADM(self, evt):
		self.set_soap_cat_of_line(self.CurrentLine, '.')
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __on_sort_by_soap(self, evt):
		self.sort_by_SOAP()

	#-------------------------------------------------------
	# marker related helpers
	#-------------------------------------------------------
	def _clone_markers(self, source, target):
		self.MarkerDelete(target, -1)
		self.__set_markers_of_line(target, self.MarkerGet(source))

	#-------------------------------------------------------
	def __set_markers_of_line(self, line, markers):
		for marker_num in cSoapSTC._DEFINED_MARKER_NUMS:
			if markers & (1 << marker_num):
				self.MarkerAdd(line, marker_num)

	#-------------------------------------------------------
	def get_soap_marker_of_line(self, line):
		markers = self.MarkerGet(line)
		for marker_num in cSoapSTC._SOAP_MARKER_NUMS:
			if markers & (1 << marker_num):
				return marker_num

		return -1		# should only happen when deleting all lines -> STC empties out INCLUDING existing markers ...

	#-------------------------------------------------------
	def get_soap_cat_of_line(self, line):
		markers = self.MarkerGet(line)
		for marker_num in cSoapSTC._SOAP_MARKER_NUMS:
			if markers & (1 << marker_num):
				return cSoapSTC._MARKER2SOAP[marker_num]

		return -1		# should only happen when deleting all lines -> STC empties out INCLUDING existing markers ...

	#-------------------------------------------------------
	def set_soap_cat_of_line(self, line, soap_category):
		# remove all SOAP markers of this line
		for marker_num in cSoapSTC._SOAP_MARKER_NUMS:
			self.MarkerDelete(line, marker_num)
		self.MarkerDelete(line, cSoapSTC._MARKER_LINE_BG_LIGHT_GREY)
		# set desired marker
		new_marker_num = cSoapSTC._SOAP2MARKER[soap_category]
		self.MarkerAdd(line, new_marker_num)
		if cSoapSTC._SOAPMARKER2BACKGROUND[new_marker_num]:
			self.MarkerAdd(line, cSoapSTC._MARKER_LINE_BG_LIGHT_GREY)
		return True

	#-------------------------------------------------------
	def check_has_all_soap_types(self):
		for marker_num in [ cSoapSTC._MARKER_S, cSoapSTC._MARKER_O, cSoapSTC._MARKER_A, cSoapSTC._MARKER_P ]:
			if self.MarkerNext(0, (1 << marker_num)) == -1:
				return False
		return True

	#-------------------------------------------------------
	def ensure_has_all_soap_types(self):
		self.__ensure_has_all_soap_types = False
		self.sort_by_SOAP()

	#-------------------------------------------------------
	def marker_count(self, marker):
		line_count = 0
		line_w_marker = -1
		while True:
			line_w_marker = self.MarkerNext(line_w_marker + 1, (1 << marker))
			if line_w_marker == -1:
				break
			line_count += 1
		return line_count

	#-------------------------------------------------------
	def soap_cat_count(self, soap_category):
		marker = cSoapSTC._SOAP2MARKER[soap_category]
		return self.marker_count(marker)

	#-------------------------------------------------------
	# key handlers
	#-------------------------------------------------------
	def __handle_delete_key(self, evt):

		if evt.HasModifiers():
			# we only handle DELETE w/o modifiers so far
			evt.Skip()
			return False

		sel_start, sel_end = self.GetSelection()
		if sel_start != sel_end:
			evt.Skip()
			sel_start_line = self.LineFromPosition(sel_start)
			sel_end_line = self.LineFromPosition(sel_end)
			# within one line -> allow in any case
			if sel_start_line == sel_end_line:
				return
			sel_start_soap_marker = self.get_soap_marker_of_line(sel_start_line)
			sel_end_soap_marker = self.get_soap_marker_of_line(sel_end_line)
			if sel_start_soap_marker == sel_end_soap_marker:
				# across lines of the same SOAP type -> allow
				return
			self.__ensure_has_all_soap_types = True
			return

		curr_line = self.CurrentLine
		if (curr_line + 1) == self.LineCount:			# adjust for line index being 0-based
			# we are on the last line, therefore we cannot end up
			# pulling up a next line (and thereby remove the only
			# line with a given SOAP category in case the last+1
			# line would happen to be the only one of that category)
			evt.Skip()
			return False

		# in last column
		caret_pos = self.GetColumn(self.CurrentPos)
		max_pos = self.LineLength(curr_line) - 1
		if caret_pos < max_pos:
			# DELETE _inside_ a line (as opposed to at the
			# _end_ of one) will not pull up the next line
			# so no special SOAP checking
			evt.Skip()
			return False

		soap_marker_current_line = self.get_soap_marker_of_line(curr_line)
		soap_marker_next_line = self.get_soap_marker_of_line(curr_line + 1)
		if soap_marker_current_line == soap_marker_next_line:
			# pulling up a line of the _same_ SOAP category
			# is fine - and exactly what the user intended
			# so allow that to happen (IOW no special DELETE
			# handling)
			evt.Skip()
			return False

		# now we have got
		# - a DELETE
		# - without modifier keys
		# - _not_ on the last line
		# - in the last column of the current line
		# - but the next line is of a different SOAP category
		# so, do NOT evt.Skip() - IOW, ignore this DELETE
		return True

	#-------------------------------------------------------
	def __handle_backspace_key(self, evt):

		if evt.HasModifiers():
			# we only handle BACKSPACE w/o modifiers so far
			evt.Skip()
			return False

		sel_start, sel_end = self.GetSelection()
		if sel_start != sel_end:
			evt.Skip()
			sel_start_line = self.LineFromPosition(sel_start)
			sel_end_line = self.LineFromPosition(sel_end)
			# within one line -> allow in any case
			if sel_start_line == sel_end_line:
				return
			sel_start_soap_marker = self.get_soap_marker_of_line(sel_start_line)
			sel_end_soap_marker = self.get_soap_marker_of_line(sel_end_line)
			if sel_start_soap_marker == sel_end_soap_marker:
				# across lines of the same SOAP type -> allow
				return
			self.__ensure_has_all_soap_types = True
			return

		curr_line = self.LineFromPosition(self.CurrentPos)
		if curr_line == 0:
			# cannot BACKSPACE into line -1 anyway
			evt.Skip()
			return False

		if self.GetColumn(self.CurrentPos) > 0:
			# not in first column, so not BACKSPACing into previous line
			evt.Skip()
			return False

		soap_marker_current_line = self.get_soap_marker_of_line(curr_line)
		soap_marker_next_line = self.get_soap_marker_of_line(curr_line - 1)
		if soap_marker_current_line == soap_marker_next_line:
			# backspacing into previous line of the _same_ SOAP
			# category is fine - and exactly what the user
			# intended so allow that to happen (IOW no special
			# DELETE handling)
			evt.Skip()
			return False

		# now we have got
		# - a BACKSPACE
		# - without modifier keys
		# - _not_ on the first line
		# - in the first column of the current line
		# - but the previous line is of a different SOAP category
		# so, do NOT evt.Skip() - IOW, ignore this BACKSPACE
		return True

	#-------------------------------------------------------
	def __handle_return_key_down(self, evt):
		# currently we always want to pass on the RETURN (but remember the markers)
		evt.Skip()
		if evt.HasModifiers():
			# we only handle RETURN w/o modifiers so far
			self.__markers_of_prev_line = None
			return
		self.__markers_of_prev_line = self.MarkerGet(self.CurrentLine)

	#-------------------------------------------------------
	def __handle_soap_category_key_down(self, key, line):
		self.__changing_SOAP_cat = False
		try:
			soap_category = gmSoapDefs.l10n2soap_cat[key]
		except KeyError:
			if key.islower():
				key = key.upper()
			else:
				key = key.casefold()
			try:
				soap_category = gmSoapDefs.l10n2soap_cat[key]
			except KeyError:
				return
		self.set_soap_cat_of_line(line, soap_category)
		wx.CallAfter(self.sort_by_SOAP)

	#-------------------------------------------------------
	def __handle_menu_key_down(self, evt):
		if wx.MAJOR_VERSION > 2:
			evt.Skip()
			return
		# on wxp2 we need to explicitly handle WXK_MENU
		# for the context menu to properly work on a key press
		self.__show_context_menu(self.caret_coords_on_screen())

	#-------------------------------------------------------
	def _on_context_menu_activated(self, evt):
		menu_position = evt.GetPosition()
		if menu_position == wx.DefaultPosition:
			caret_pos_in_stc = self.PointFromPosition(self.CurrentPos)
			caret_pos_on_screen = self.ClientToScreen(caret_pos_in_stc)
			menu_position = caret_pos_on_screen
		self.__show_context_menu(menu_position)

	#-------------------------------------------------------
	# event setup and handlers
	#-------------------------------------------------------
	def __register_events(self):
		# wxPython events
		self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)			# happens before key gets into STC
		#self.Bind(wx.EVT_CHAR, self._on_wx_char)				# happens before char gets into STC
		self.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu_activated)

		# STC events
		self.Bind(wx.stc.EVT_STC_CHARADDED, self._on_stc_char_added)
		self.Bind(wx.stc.EVT_STC_CHANGE, self._on_stc_change)

		#self.Bind(stc.EVT_STC_DO_DROP, self.OnDoDrop)
		#self.Bind(stc.EVT_STC_DRAG_OVER, self.OnDragOver)
		#self.Bind(stc.EVT_STC_START_DRAG, self.OnStartDrag)
		#self.Bind(stc.EVT_STC_MODIFIED, self.OnModified)

		#self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

	#-------------------------------------------------------
	def _on_wx_char(self, evt):
		evt.Skip()

	#-------------------------------------------------------
	def _on_key_down(self, evt):

		# CTRL-T has been pressed last, now another character has been pressed
		if self.__changing_SOAP_cat:
			self.__handle_soap_category_key_down(chr(evt.GetUnicodeKey()).casefold(), self.CurrentLine)
			# somehow put cursor into the changed (and possibly moved) line
			return

		key = evt.KeyCode

		# ENTER
		if key == wx.WXK_RETURN:
			self.__handle_return_key_down(evt)
			return

		# BACKSPACE
		if key == wx.WXK_BACK:
			self.__handle_backspace_key(evt)
			return

		# DELETE
		if key == wx.WXK_DELETE:
			self.__handle_delete_key(evt)
			return

		# MENU
		if key == wx.WXK_MENU:
			self.__handle_menu_key_down(evt)
			return

		# CTRL-T: set Type
		if key == ord('T'):
			if evt.HasModifiers():
				if evt.CmdDown():		# CTRL-T or APPLE-T
					self.__changing_SOAP_cat = True
					return

		evt.Skip()			# make sure unhandled keys get to the STC

	#-------------------------------------------------------
	def _on_stc_char_added(self, evt):
		evt.Skip()
		key = evt.GetKey()
		if key == 10:
			# we cannot simply transfer the markers of the previous
			# line (where we pressed RETURN) into the current line
			# (which appeared after the RETURN) because the STC handles
			# creating the "new" line differently based on where in the
			# previous line RETURN was pressed (!) -- if it happened
			# to be in position 0 (at the start of the line) the previous
			# line is pushed DOWN and an empty line is inserted BEFORE
			# the previous line (likely an optimization)
			# hence we need to remember the markers of the real previous
			# line from _before_ the new line gets created and use that
			# auto-set the markers of the new line... |-)
			if self.__markers_of_prev_line is None:
				return
			self.__set_markers_of_line(self.CurrentLine - 1, self.__markers_of_prev_line)
			self.__set_markers_of_line(self.CurrentLine, self.__markers_of_prev_line)
			self.__markers_of_prev_line = None
			return

	#-------------------------------------------------------
	def _on_stc_change(self, evt):
		if self.__ensure_has_all_soap_types:
			wx.CallAfter(self.ensure_has_all_soap_types)

	#-------------------------------------------------------
	#-------------------------------------------------------
	#-------------------------------------------------------
	#-------------------------------------------------------
	# unused:
	#-------------------------------------------------------
	def OnDestroy(self, evt):
		# This is how the clipboard contents can be preserved after
		# the app has exited.
		wx.TheClipboard.Flush()
		evt.Skip()


#	def OnStartDrag(self, evt):
#		#self.log.write("OnStartDrag: %d, %s\n"
#		#			   % (evt.GetDragAllowMove(), evt.GetDragText()))
#		if debug and evt.GetPosition() < 250:
#			evt.SetDragAllowMove(False)		# you can prevent moving of text (only copy)
#			evt.SetDragText("DRAGGED TEXT") # you can change what is dragged
#			#evt.SetDragText("")			 # or prevent the drag with empty text
#
#
#	def OnDragOver(self, evt):
#		#self.log.write(
#		#	"OnDragOver: x,y=(%d, %d)  pos: %d	DragResult: %d\n"
#		#	% (evt.GetX(), evt.GetY(), evt.GetPosition(), evt.GetDragResult())
#		#	)
#
#		if debug and evt.GetPosition() < 250:
#			evt.SetDragResult(wx.DragNone)	 # prevent dropping at the beginning of the buffer
#
#
#	def OnDoDrop(self, evt):
#		#self.log.write("OnDoDrop: x,y=(%d, %d)	pos: %d	 DragResult: %d\n"
#		#			   "\ttext: %s\n"
#		#			   % (evt.GetX(), evt.GetY(), evt.GetPosition(), evt.GetDragResult(),
#		#				  evt.GetDragText()))
#
#		if debug and evt.GetPosition() < 500:
#			evt.SetDragText("DROPPED TEXT")	 # Can change text if needed
#			#evt.SetDragResult(wx.DragNone)	 # Can also change the drag operation, but it
#											 # is probably better to do it in OnDragOver so
#											 # there is visual feedback
#
#			#evt.SetPosition(25)			 # Can also change position, but I'm not sure why
#											 # you would want to...


	def OnModified(self, evt):
		#self.log.write("""OnModified
#		Mod type:	  %s
#		At position:  %d
#		Lines added:  %d
#		Text Length:  %d
#		Text:		  %s\n""" % ( self.transModType(evt.GetModificationType()),
#								  evt.GetPosition(),
#								  evt.GetLinesAdded(),
#								  evt.GetLength(),
#								  repr(evt.GetText()) ))
		pass


	def transModType(self, modType):
		st = ""
		table = [(wx.stc.STC_MOD_INSERTTEXT, "InsertText"),
				 (wx.stc.STC_MOD_DELETETEXT, "DeleteText"),
				 (wx.stc.STC_MOD_CHANGESTYLE, "ChangeStyle"),
				 (wx.stc.STC_MOD_CHANGEFOLD, "ChangeFold"),
				 (wx.stc.STC_PERFORMED_USER, "UserFlag"),
				 (wx.stc.STC_PERFORMED_UNDO, "Undo"),
				 (wx.stc.STC_PERFORMED_REDO, "Redo"),
				 (wx.stc.STC_LASTSTEPINUNDOREDO, "Last-Undo/Redo"),
				 (wx.stc.STC_MOD_CHANGEMARKER, "ChangeMarker"),
				 (wx.stc.STC_MOD_BEFOREINSERT, "B4-Insert"),
				 (wx.stc.STC_MOD_BEFOREDELETE, "B4-Delete")
				 ]

		for flag,text in table:
			if flag & modType:
				st = st + text + " "

		if not st:
			st = 'UNKNOWN'

		return st

#----------------------------------------------------------------------
#----------------------------------------------------------------------
#----------------------------------------------------------------------
if wx.Platform == '__WXMSW__':
	face1 = 'Arial'
	face2 = 'Times New Roman'
	face3 = 'Courier New'
	pb = 12
else:
	face1 = 'Helvetica'
	face2 = 'Times'
	face3 = 'Courier'
	pb = 14


_USE_PANEL = 1

def runTest(frame, nb):
	if not _USE_PANEL:
		ed = p = cSoapSTC(nb, -1)

	else:
		p = wx.Panel(nb, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		#ed = cSoapSTC(p, -1, log)
		ed = cSoapSTC(p, -1, None)
		s = wx.BoxSizer(wx.HORIZONTAL)
		s.Add(ed, 1, wx.EXPAND)
		p.SetSizer(s)
		p.SetAutoLayout(True)


	#ed.SetBufferedDraw(False)
	#ed.StyleClearAll()
	#ed.SetScrollWidth(800)
	#ed.SetWrapMode(True)
	#ed.SetUseAntiAliasing(False)	 
	#ed.SetViewEOL(True)

	#ed.CmdKeyClear(wx.stc.STC_KEY_BACK,
	#				wx.stc.STC_SCMOD_CTRL)
	#ed.CmdKeyAssign(wx.stc.STC_KEY_BACK,
	#				 wx.stc.STC_SCMOD_CTRL,
	#				 wx.stc.STC_CMD_DELWORDLEFT)

	ed.SetText('abcdefgs')

	if True:
	#if wx.USE_UNICODE:
		import codecs
		decode = codecs.lookup("utf-8")[1]

		ed.GotoPos(ed.GetLength())
		ed.AddText("\n\nwx.StyledTextCtrl can also do Unicode:\n")
		#uniline = ed.GetCurrentLine()
		unitext, l = decode('\xd0\x9f\xd0\xb8\xd1\x82\xd0\xbe\xd0\xbd - '
							'\xd0\xbb\xd1\x83\xd1\x87\xd1\x88\xd0\xb8\xd0\xb9 '
							'\xd1\x8f\xd0\xb7\xd1\x8b\xd0\xba \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb3\xd1\x80\xd0\xb0\xd0\xbc\xd0\xbc\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f!\n\n')
		ed.AddText('\tRussian: ')
		ed.AddText(unitext)
		ed.GotoPos(0)
	#else:
	#	 #ed.StyleSetFontEncoding(wx.stc.STC_STYLE_DEFAULT, wx.FONTENCODING_KOI8)
	#	 #text = u'\u041f\u0438\u0442\u043e\u043d - \u043b\u0443\u0447\u0448\u0438\u0439 \u044f\u0437\u044b\u043a \n\u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f!'
	#	 #text = text.encode('koi8-r')
	#	 #ed.StyleSetFontEncoding(wx.stc.STC_STYLE_DEFAULT, wx.FONTENCODING_BIG5)
	#	 #text = u'Python \u662f\u6700\u597d\u7684\u7de8\u7a0b\u8a9e\u8a00\uff01'
	#	 #text = text.encode('big5')
	#	 ed.GotoPos(ed.GetLength())
	#	 ed.AddText('\n\n' + text)

	ed.EmptyUndoBuffer()

	# make some styles
	ed.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "size:%d,face:%s" % (pb, face3))
	ed.StyleClearAll()
	ed.StyleSetSpec(1, "size:%d,bold,face:%s,fore:#0000FF" % (pb, face1))
	ed.StyleSetSpec(2, "face:%s,italic,fore:#FF0000,size:%d" % (face2, pb))
	ed.StyleSetSpec(3, "face:%s,bold,size:%d" % (face2, pb))
	ed.StyleSetSpec(4, "face:%s,size:%d" % (face1, pb-1))

	# Now set some text to those styles...	Normally this would be
	# done in an event handler that happens when text needs displayed.
	ed.StartStyling(98, 0xff)
	ed.SetStyling(6, 1)	 # set style for 6 characters using style 1

	ed.StartStyling(190, 0xff)
	ed.SetStyling(20, 2)

	ed.StartStyling(310, 0xff)
	ed.SetStyling(4, 3)
	ed.SetStyling(2, 0)
	ed.SetStyling(10, 4)


	# line numbers in the margin
	ed.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
	ed.SetMarginWidth(0, 22)
	ed.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "size:%d,face:%s" % (pb-2, face1))

	# setup some markers
	ed.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
	ed.MarkerDefine(0, wx.stc.STC_MARK_ROUNDRECT, "#CCFF00", "RED")
	ed.MarkerDefine(1, wx.stc.STC_MARK_CIRCLE, "FOREST GREEN", "SIENNA")
	ed.MarkerDefine(2, wx.stc.STC_MARK_SHORTARROW, "blue", "blue")
	ed.MarkerDefine(3, wx.stc.STC_MARK_ARROW, "#00FF00", "#00FF00")

	# put some markers on some lines
	ed.MarkerAdd(17, 0)
	ed.MarkerAdd(18, 1)
	ed.MarkerAdd(19, 2)
	ed.MarkerAdd(20, 3)
	ed.MarkerAdd(20, 0)


	# and finally, an indicator or two
	ed.IndicatorSetStyle(0, wx.stc.STC_INDIC_SQUIGGLE)
	ed.IndicatorSetForeground(0, wx.RED)
	ed.IndicatorSetStyle(1, wx.stc.STC_INDIC_DIAGONAL)
	ed.IndicatorSetForeground(1, wx.BLUE)
	ed.IndicatorSetStyle(2, wx.stc.STC_INDIC_STRIKE)
	ed.IndicatorSetForeground(2, wx.RED)

	ed.StartStyling(836, wx.stc.STC_INDICS_MASK)
	ed.SetStyling(10, wx.stc.STC_INDIC0_MASK)
	ed.SetStyling(8, wx.stc.STC_INDIC1_MASK)
	ed.SetStyling(10, wx.stc.STC_INDIC2_MASK | wx.stc.STC_INDIC1_MASK)


	# some test stuff...
#	if debug:
#		print("GetTextLength(): ", ed.GetTextLength(), len(ed.GetText()))
#		print("GetText(): ", repr(ed.GetText()))
#		print()
#		print("GetStyledText(98, 104): ", repr(ed.GetStyledText(98, 104)), len(ed.GetStyledText(98, 104)))
#		print()
#		print("GetCurLine(): ", repr(ed.GetCurLine()))
#		ed.GotoPos(5)
#		print("GetCurLine(): ", repr(ed.GetCurLine()))
#		print()
#		print("GetLine(1): ", repr(ed.GetLine(1)))
#		print()
#		ed.SetSelection(25, 35)
#		print("GetSelectedText(): ", repr(ed.GetSelectedText()))
#		print("GetTextRange(25, 35): ", repr(ed.GetTextRange(25, 35)))
#		print("FindText(0, max, 'indicators'): ", end=' ')
#		print(ed.FindText(0, ed.GetTextLength(), "indicators"))
#		if wx.USE_UNICODE:
#			end = ed.GetLength()
#			start = ed.PositionFromLine(uniline)
#			print("GetTextRange(%d, %d): " % (start, end), end=' ')
#			print(repr(ed.GetTextRange(start, end)))
#
#
#	wx.CallAfter(ed.GotoPos, 0)
	return p


#----------------------------------------------------------------------
overview = """\
<html><body>
Once again, no docs yet.  <b>Sorry.</b>	 But <a href="data/stc.h.html">this</a>
and <a href="https://www.scintilla.org/ScintillaDoc.html">this</a> should
be helpful.
</body><html>
"""

#===================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	import wx.lib.colourdb

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#-----------------------------------------------
	def test_stc():
#		app = wx.PyWidgetTester(size = (600, 600))
		wx.lib.colourdb.updateColourDB()
		#print wx.lib.colourdb.getColourList()
#		app.SetWidget(cSoapSTC, -1, (100,50))
#		app.MainLoop()
		return True

#		app = wx.PyWidgetTester(size = (200, 50))
#		tc = cTextCtrl(app.frame, -1)
#		#tc.enable_keyword_expansions()
#		app.frame.Show(True)
#		app.MainLoop()
#		return True

	#-----------------------------------------------
	test_stc()
