"""GNUmed TextCtrl sbuclass."""
#===================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys


import wx
import wx.lib.expando


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmShellAPI
from Gnumed.wxpython import gmKeywordExpansionWidgets


_log = logging.getLogger('gm.txtctrl')

#============================================================
color_tctrl_invalid = 'pink'
color_tctrl_partially_invalid = 'yellow'

class cColoredStatus_TextCtrlMixin():
	"""Mixin for setting background color based on validity of content.

	Note that due to Python MRO classes using this mixin must
	list it before their base class (because we override Enable/Disable).
	"""
	def __init__(self, *args, **kwargs):

		if not isinstance(self, (wx.TextCtrl)):
			raise TypeError('[%s]: can only be applied to wx.TextCtrl, not [%s]' % (cColoredStatus_TextCtrlMixin, self.__class__.__name__))

		self.__initial_background_color = self.GetBackgroundColour()
		self.__previous_enabled_bg_color = self.__initial_background_color

	#--------------------------------------------------------
	def display_as_valid(self, valid=True):
		if valid is True:
			color2show = self.__initial_background_color
		elif valid is False:
			color2show = color_tctrl_invalid
		elif valid is None:
			color2show = color_tctrl_partially_invalid
		else:
			raise ValueError('<valid> must be True or False or None')

		if self.IsEnabled():
			self.SetBackgroundColour(color2show)
			self.Refresh()
			return

		# remember for when it gets enabled
		self.__previous_enabled_bg_color = color2show

	#--------------------------------------------------------
	def display_as_disabled(self, disabled=None):
		current_enabled_state = self.IsEnabled()
		desired_enabled_state = disabled is False
		if current_enabled_state is desired_enabled_state:
			return

		if disabled is True:
			self.__previous_enabled_bg_color = self.GetBackgroundColour()
			color2show = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
		elif disabled is False:
			color2show = self.__previous_enabled_bg_color
		else:
			raise ValueError('<disabled> must be True or False')

		self.SetBackgroundColour(color2show)
		self.Refresh()

	#--------------------------------------------------------
	def Disable(self):
		self.Enable(enable = False)

	#--------------------------------------------------------
	def Enable(self, enable=True):

		if self.IsEnabled() is enable:
			return

		wx.TextCtrl.Enable(self, enable)

		if enable is True:
			self.SetBackgroundColour(self.__previous_enabled_bg_color)
		elif enable is False:
			self.__previous_enabled_bg_color = self.GetBackgroundColour()
			self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
		else:
			raise ValueError('<enable> must be True or False')

		self.Refresh()

#============================================================
_KNOWN_UNICODE_SELECTORS = [
	'kcharselect',			# KDE
	'gucharmap',			# GNOME
	'BabelMap.exe',			# Windows, supposed to be better than charmap.exe
	'charmap.exe',			# Microsoft utility
	'gm-unicode2clipboard'	# generic GNUmed workaround
	# Mac OSX supposedly features built-in support
]

found, __UNICODE_SELECTOR_APP = gmShellAPI.find_first_binary(binaries = _KNOWN_UNICODE_SELECTORS)
if found:
	_log.debug('found [%s] for unicode character selection', __UNICODE_SELECTOR_APP)
else:
	_log.error('no unicode character selection tool found')
	_log.debug('known tools: %s', _KNOWN_UNICODE_SELECTORS)
	_log.debug('gm-unicode2clipboard: no arguments passed in')
	_log.debug('gm-unicode2clipboard: if the clipboard contains new data upon return GNUmed will import the active text control')


class cUnicodeInsertion_TextCtrlMixin():
	"""Insert unicode characters into text control via selection tool."""

#	_unicode_selector = None

	def __init__(self, *args, **kwargs):
		if not isinstance(self, (wx.TextCtrl, wx.stc.StyledTextCtrl)):
			raise TypeError('[%s]: can only be applied to wx.TextCtrl or wx.stc.StyledTextCtrl, not [%s]' % (cUnicodeInsertion_TextCtrlMixin, self.__class__.__name__))

#		if cUnicodeInsertion_TextCtrlMixin._unicode_selector is None:
#			found, cUnicodeInsertion_TextCtrlMixin._unicode_selector = gmShellAPI.find_first_binary(binaries = _KNOWN_UNICODE_SELECTORS)
#			if found:
#				_log.debug('found [%s] for unicode character selection', cUnicodeInsertion_TextCtrlMixin._unicode_selector)
#			else:
#				_log.error('no unicode character selection tool found')

	#--------------------------------------------------------
	def mixin_insert_unicode_character(self):
#		if cUnicodeInsertion_TextCtrlMixin._unicode_selector is None:
		if __UNICODE_SELECTOR_APP is None:
			return False

		# read clipboard
		if wx.TheClipboard.IsOpened():
			_log.error('clipboard already open')
			return False

		if not wx.TheClipboard.Open():
			_log.error('cannot open clipboard')
			return False

		data_obj = wx.TextDataObject()
		prev_clip = None
		got_it = wx.TheClipboard.GetData(data_obj)
		if got_it:
			prev_clip = data_obj.Text
		# run selector
		#if not gmShellAPI.run_command_in_shell(command = cUnicodeInsertion_TextCtrlMixin._unicode_selector, blocking = True):
		if not gmShellAPI.run_command_in_shell(command = __UNICODE_SELECTOR_APP, blocking = True):
			wx.TheClipboard.Close()
			return False

		# read clipboard again
		got_it = wx.TheClipboard.GetData(data_obj)
		wx.TheClipboard.Close()
		if not got_it:
			_log.debug('clipboard does not contain text')
			return False

		curr_clip = data_obj.Text
		# insert clip if any
		if curr_clip == prev_clip:
			# nothing put into clipboard (that is, clipboard still the same)
			return False

		self.WriteText(curr_clip)
		return True

#============================================================
class cTextSearch_TextCtrlMixin():
	"""Code using classes with this mixin must call
	   show_find_dialog() at appropriate times. Everything
	   else will be handled.
	"""
	def __init__(self, *args, **kwargs):
		if not isinstance(self, (wx.TextCtrl, wx.stc.StyledTextCtrl)):
			raise TypeError('[%s]: can only be applied to wx.TextCtrl or wx.stc.StyledTextCtrl, not [%s]' % (cTextSearch_TextCtrlMixin, self.__class__.__name__))

		self.__mixin_find_replace_data = None
		self.__mixin_find_replace_dlg = None
		self.__mixin_find_replace_last_match_start = 0
		self.__mixin_find_replace_last_match_end = 0
		self.__mixin_find_replace_last_match_attr = None

	#--------------------------------------------------------
	def show_find_dialog(self, title=None):

		if self.__mixin_find_replace_dlg is not None:
			return self.__mixin_find_replace_dlg

		self.__mixin_find_replace_last_match_end = 0

		if title is None:
			title = _('Find text')
		self.__mixin_find_replace_data = wx.FindReplaceData()
		self.__mixin_find_replace_dlg = wx.FindReplaceDialog (
			self,
			self.__mixin_find_replace_data,
			title,
			wx.FR_NOUPDOWN | wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD
		)
		self.__mixin_find_replace_dlg.Bind(wx.EVT_FIND, self._mixin_on_find)
		self.__mixin_find_replace_dlg.Bind(wx.EVT_FIND_NEXT, self._mixin_on_find)
		self.__mixin_find_replace_dlg.Bind(wx.EVT_FIND_CLOSE, self._mixin_on_find_close)
		self.__mixin_find_replace_dlg.Show()
		return self.__mixin_find_replace_dlg

	#--------------------------------------------------------
	# events
	#--------------------------------------------------------
	def _mixin_on_find(self, evt):

		# reset style of previous match
		if self.__mixin_find_replace_last_match_attr is not None:
			self.SetStyle (
				self.__mixin_find_replace_last_match_start,
				self.__mixin_find_replace_last_match_end,
				self.__mixin_find_replace_last_match_attr
			)

		# find current match
		search_term = self.__mixin_find_replace_data.GetFindString().casefold()
		match_start = self.Value.casefold().find(search_term, self.__mixin_find_replace_last_match_end)
		if match_start == -1:
			# wrap around
			self.__mixin_find_replace_last_match_start = 0
			self.__mixin_find_replace_last_match_end = 0
			wx.Bell()
			return

		# remember current match for next time around
		attr = wx.TextAttr()
		if self.GetStyle(match_start, attr):
			self.__mixin_find_replace_last_match_attr = attr
		else:
			self.__mixin_find_replace_last_match_attr = None
		self.__mixin_find_replace_last_match_start = match_start
		self.__mixin_find_replace_last_match_end = match_start + len(search_term)

		# react to current match
		self.Freeze()
		self.SetStyle (
			self.__mixin_find_replace_last_match_start,
			self.__mixin_find_replace_last_match_end,
			wx.TextAttr("red", "black")
		)
		self.ShowPosition(0)
		self.ShowPosition(self.__mixin_find_replace_last_match_end)
		self.Thaw()

	#--------------------------------------------------------
	def _mixin_on_find_close(self, evt):
		# cleanup after last match if any
		if self.__mixin_find_replace_last_match_attr is not None:
			self.SetStyle (
				self.__mixin_find_replace_last_match_start,
				self.__mixin_find_replace_last_match_end,
				self.__mixin_find_replace_last_match_attr
			)
		# deactivate the events
		self.__mixin_find_replace_dlg.Unbind(wx.EVT_FIND)
		self.__mixin_find_replace_dlg.Unbind(wx.EVT_FIND_NEXT)
		self.__mixin_find_replace_dlg.Unbind(wx.EVT_FIND_CLOSE)
		# unshow dialog
		self.__mixin_find_replace_dlg.DestroyLater()
		self.__mixin_find_replace_data = None
		self.__mixin_find_replace_dlg = None
		self.__mixin_find_replace_last_match_end = 0

#============================================================
class cTextCtrl(gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin, cTextSearch_TextCtrlMixin, cColoredStatus_TextCtrlMixin, cUnicodeInsertion_TextCtrlMixin, wx.TextCtrl):

	def __init__(self, *args, **kwargs):

		self._on_set_focus_callbacks = []
		self._on_lose_focus_callbacks = []
		self._on_modified_callbacks = []

		wx.TextCtrl.__init__(self, *args, **kwargs)
		gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin.__init__(self)
		cTextSearch_TextCtrlMixin.__init__(self)
		cColoredStatus_TextCtrlMixin.__init__(self)
		cUnicodeInsertion_TextCtrlMixin.__init__(self)

		self.enable_keyword_expansions()

	#--------------------------------------------------------
	# callback API
	#--------------------------------------------------------
	def add_callback_on_set_focus(self, callback=None):
		"""Add a callback for invocation when getting focus."""
		if not callable(callback):
			raise ValueError('[add_callback_on_set_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_set_focus_callbacks.append(callback)
		if len(self._on_set_focus_callbacks) == 1:
			self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
	#---------------------------------------------------------
	def add_callback_on_lose_focus(self, callback=None):
		"""Add a callback for invocation when losing focus."""
		if not callable(callback):
			raise ValueError('[add_callback_on_lose_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_lose_focus_callbacks.append(callback)
		if len(self._on_lose_focus_callbacks) == 1:
			self.Bind(wx.EVT_KILL_FOCUS, self._on_lose_focus)
	#---------------------------------------------------------
	def add_callback_on_modified(self, callback=None):
		"""Add a callback for invocation when the content is modified.

		This callback will NOT be passed any values.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_modified]: ignoring callback [%s] - not callable' % callback)

		self._on_modified_callbacks.append(callback)
		if len(self._on_modified_callbacks) == 1:
			self.Bind(wx.EVT_TEXT, self._on_text_update)

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_set_focus(self, event):
		event.Skip()
		for callback in self._on_set_focus_callbacks:
			callback()
		return True
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		"""Do stuff when leaving the control.

		The user has had her say, so don't second guess
		intentions but do report error conditions.
		"""
		event.Skip()
		wx.CallAfter(self.__on_lost_focus)
		return True
	#--------------------------------------------------------
	def __on_lost_focus(self):
		for callback in self._on_lose_focus_callbacks:
			callback()
	#--------------------------------------------------------
	def _on_text_update (self, event):
		"""Internal handler for wx.EVT_TEXT.

		Called when text was changed by user or by SetValue().
		"""
		for callback in self._on_modified_callbacks:
			callback()
		return

#============================================================
# expando based text ctrl classes
#============================================================
class cExpandoTextCtrlHandling_PanelMixin():
	"""Mixin for panels wishing to handel expando text ctrls within themselves.

	Panels using this mixin will need to call

		self.bind_expando_layout_event(<expando_field>)

	on each <expando_field> they wish to auto-expand.
	"""
	#--------------------------------------------------------
	def bind_expando_layout_event(self, expando):
		self.Bind(wx.lib.expando.EVT_ETC_LAYOUT_NEEDED, self._on_expando_needs_layout)

	#--------------------------------------------------------
	def _on_expando_needs_layout(self, evt):
		# need to tell ourselves to re-Layout to refresh scroll bars
		# provoke adding scrollbar if needed
		#self.Fit()				# works on Linux but not on Windows
		self.FitInside()		# needed on Windows rather than self.Fit()
		if self.HasScrollbar(wx.VERTICAL):
			# scroll panel to show cursor
			expando = self.FindWindowById(evt.GetId())
			y_expando = expando.GetPosition()[1]
			h_expando = expando.GetSize()[1]
			line_of_cursor = expando.PositionToXY(expando.GetInsertionPoint())[2] + 1
			if expando.NumberOfLines == 0:
				no_of_lines = 1
			else:
				no_of_lines = expando.NumberOfLines
			y_cursor = int(round((float(line_of_cursor) / no_of_lines) * h_expando))
			y_desired_visible = y_expando + y_cursor
			y_view = self.GetViewStart()[1]
			h_view = self.GetClientSize()[1]
#			print "expando:", y_expando, "->", h_expando, ", lines:", expando.NumberOfLines
#			print "cursor :", y_cursor, "at line", line_of_cursor, ", insertion point:", expando.GetInsertionPoint()
#			print "wanted :", y_desired_visible
#			print "view-y :", y_view
#			print "scroll2:", h_view
			# expando starts before view
			if y_desired_visible < y_view:
#				print "need to scroll up"
				self.Scroll(0, y_desired_visible)
			if y_desired_visible > h_view:
#				print "need to scroll down"
				self.Scroll(0, y_desired_visible)

#============================================================
class cExpandoTextCtrl(gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin, cTextSearch_TextCtrlMixin, cColoredStatus_TextCtrlMixin, wx.lib.expando.ExpandoTextCtrl):
	"""Expando based text ctrl

	- auto-sizing on input
	- keyword based text expansion
	- text search on show_find_dialog()
	- (on demand) status based background color

	Parent panels should apply the cExpandoTextCtrlHandling_PanelMixin.
	"""
	def __init__(self, *args, **kwargs):

		wx.lib.expando.ExpandoTextCtrl.__init__(self, *args, **kwargs)
		gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin.__init__(self)
		cTextSearch_TextCtrlMixin.__init__(self)
		cColoredStatus_TextCtrlMixin.__init__(self)

		self.__register_interests()
		self.enable_keyword_expansions()

	#------------------------------------------------
	# event handling
	#------------------------------------------------
	def __register_interests(self):
		self.Bind(wx.EVT_SET_FOCUS, self.__cExpandoTextCtrl_on_focus)

	#--------------------------------------------------------
	def __cExpandoTextCtrl_on_focus(self, evt):
		evt.Skip()	# allow other processing to happen
		wx.CallAfter(self._cExpandoTextCtrl_after_on_focus)

	#--------------------------------------------------------
	def _cExpandoTextCtrl_after_on_focus(self):
		# robustify against Py__DeadObjectError (RuntimeError) - since
		# we are called from wx's CallAfter this SoapCtrl may be gone
		# by the time we get around to handling this layout request,
		# say, on patient change or some such
		if not self:
			return

		#wx. CallAfter(self._adjustCtrl)
		evt = wx.PyCommandEvent(wx.lib.expando.wxEVT_ETC_LAYOUT_NEEDED, self.GetId())
		evt.SetEventObject(self)
		#evt.height = None
		#evt.numLines = None
		#evt.height = self.GetSize().height
		#evt.numLines = self.GetNumberOfLines()
		self.GetEventHandler().ProcessEvent(evt)

	#------------------------------------------------
	# fix platform expando.py if needed
	#------------------------------------------------
	def _wrapLine(self, line, dc, max_width):

		if wx.MAJOR_VERSION > 2:
			return wx.lib.expando.ExpandoTextCtrl._wrapLine(self, line, dc, max_width)

		if (wx.MAJOR_VERSION == 2) and (wx.MINOR_VERSION > 8):
			return wx.lib.expando.ExpandoTextCtrl._wrapLine(self, line, dc, max_width)

		# THIS FIX LIFTED FROM TRUNK IN SVN:
		# Estimate where the control will wrap the lines and
		# return the count of extra lines needed.
		partial_text_extents = dc.GetPartialTextExtents(line)
		max_width -= wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
		idx = 0
		start = 0
		count_of_extra_lines_needed = 0
		idx_of_last_blank = -1
		while idx < len(partial_text_extents):
		    if line[idx] == ' ':
		        idx_of_last_blank = idx
		    if (partial_text_extents[idx] - start) > max_width:
		        # we've reached the max width, add a new line
		        count_of_extra_lines_needed += 1
		        # did we see a space? if so restart the count at that pos
		        if idx_of_last_blank != -1:
		            idx = idx_of_last_blank + 1
		            idx_of_last_blank = -1
		        if idx < len(partial_text_extents):
		            start = partial_text_extents[idx]
		    else:
		        idx += 1
		return count_of_extra_lines_needed

#===================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	#-----------------------------------------------
#	def test_gm_textctrl():
#		app = wx.PyWidgetTester(size = (200, 50))
#		#tc = 
#		cTextCtrl(app.frame, -1)
#		#tc.enable_keyword_expansions()
#		#tc.Enable(False)
#		app.frame.Show(True)
#		app.MainLoop()
#		return True
	#-----------------------------------------------
#	test_gm_textctrl()
