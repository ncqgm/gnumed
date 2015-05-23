__doc__ = """GNUmed TextCtrl sbuclass."""
#===================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.wxpython import gmKeywordExpansionWidgets


_log = logging.getLogger('gm.txtctrl')


#============================================================
class cTextSearch_TextCtrlMixin():

	def __init__(self):
		if not isinstance(self, (wx.TextCtrl, wx.stc.StyledTextCtrl)):
			raise TypeError('[%s]: can only be applied to wx.TextCtrl or wx.stc.StyledTextCtrl, not [%s]' % (cKeywordExpansion_TextCtrlMixin, self.__class__.__name__))

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
		search_term = self.__mixin_find_replace_data.GetFindString().lower()
		match_start = self.Value.lower().find(search_term, self.__mixin_find_replace_last_match_end)
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
		self.__mixin_find_replace_dlg.Destroy()
		self.__mixin_find_replace_data = None
		self.__mixin_find_replace_dlg = None
		self.__mixin_find_replace_last_match_end = 0

#============================================================
color_tctrl_invalid = 'pink'
color_tctrl_partially_invalid = 'yellow'

class cTextCtrl(wx.TextCtrl, gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin, cTextSearch_TextCtrlMixin):

	def __init__(self, *args, **kwargs):

		wx.TextCtrl.__init__(self, *args, **kwargs)

		self._on_set_focus_callbacks = []
		self._on_lose_focus_callbacks = []
		self._on_modified_callbacks = []

		self.__initial_background_color = self.GetBackgroundColour()

		gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin.__init__(self)
		self.enable_keyword_expansions()

		cTextSearch_TextCtrlMixin.__init__(self)

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
			#wx.EVT_TEXT(self, self.GetId(), self._on_text_update)
	#--------------------------------------------------------
	# state display API
	#--------------------------------------------------------
	def display_as_valid(self, valid=None, partially_invalid=False):
		if valid is True:
			self.SetBackgroundColour(self.__initial_background_color)
		elif valid is False:
			if partially_invalid:
				self.SetBackgroundColour(color_tctrl_partially_invalid)
			else:
				self.SetBackgroundColour(color_tctrl_invalid)
		else:
			raise ValueError(u'<valid> must be True or False')
		self.Refresh()
	#--------------------------------------------------------
	def display_as_disabled(self, disabled=None):
		if disabled is True:
			self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BACKGROUND))
		elif disabled is False:
			self.SetBackgroundColour(self.__initial_background_color)
		else:
			raise ValueError(u'<disabled> must be True or False')
		self.Refresh()
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

#===================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	#-----------------------------------------------
	def test_gm_textctrl():
		app = wx.PyWidgetTester(size = (200, 50))
		tc = cTextCtrl(parent = app.frame, id = -1)
		#tc.enable_keyword_expansions()
		app.frame.Show(True)
		app.MainLoop()
		return True
	#-----------------------------------------------
	test_gm_textctrl()

#---------------------------------------------------
