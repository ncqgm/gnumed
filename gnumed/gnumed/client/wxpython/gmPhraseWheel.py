"""GNUmed phrasewheel.

A class, extending wx.TextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client.

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
############################################################################
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan <sjtan@bigpond.com>"
__license__ = "GPL"

# stdlib
import sys
import re as regex


# 3rd party
import wx
import wx.lib.mixins.listctrl as listmixins


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher


import logging
_log = logging.getLogger('macosx')


color_prw_invalid = 'pink'
color_prw_partially_invalid = 'yellow'
color_prw_valid = None				# this is used by code outside this module
COLOR_BG_PRW_WITH_FOCUS = 'light yellow'

#default_phrase_separators = r'[;/|]+'
default_phrase_separators = r';+'

# those can be used by the <accepted_chars> phrasewheel parameter
NUMERIC = '0-9'
ALPHANUMERIC = 'a-zA-Z0-9'
EMAIL_CHARS = "a-zA-Z0-9\-_@\."
WEB_CHARS = "a-zA-Z0-9\.\-_/:"


_timers:list = []

#============================================================
def shutdown():
	"""It can be useful to call this early from your shutdown code to avoid hangs on Notify()."""
	global _timers
	_log.info('shutting down %s pending timers', len(_timers))
	for timer in _timers:
		_log.debug('timer [%s]', timer)
		timer.Stop()
	_timers = []

#------------------------------------------------------------
class _cPRWTimer(wx.Timer):

	def __init__(self, *args, **kwargs):
		wx.Timer.__init__(self, *args, **kwargs)
		self.callback = lambda x:x
		global _timers
		_timers.append(self)

	def Notify(self):
		self.callback()

#============================================================
# FIXME: merge with gmListWidgets
class cPhraseWheelListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):

	def __init__(self, *args, **kwargs):
		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER
		except KeyError:
			pass
		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#--------------------------------------------------------
	def SetItems(self, items):
		self.DeleteAllItems()
		self.__data = items
		pos = len(items) + 1
		for item in items:
			#self.InsertItem(pos, label = item['list_label'])
			self.InsertItem(pos, item['list_label'])
	#--------------------------------------------------------
	def GetSelectedItemData(self):
		sel_idx = self.GetFirstSelected()
		if sel_idx == -1:
			return None
		return self.__data[sel_idx]['data']
	#--------------------------------------------------------
	def get_selected_item(self):
		sel_idx = self.GetFirstSelected()
		if sel_idx == -1:
			return None
		return self.__data[sel_idx]
	#--------------------------------------------------------
	def get_selected_item_label(self):
		sel_idx = self.GetFirstSelected()
		if sel_idx == -1:
			return None
		return self.__data[sel_idx]['list_label']

#============================================================
# base class for both single- and multi-phrase phrase wheels
#------------------------------------------------------------
class cPhraseWheelBase(wx.TextCtrl):
	"""Widget for smart guessing of user fields, after Richard Terry's interface.

	- VB implementation by Richard Terry
	- Python port by Ian Haywood for GNUmed
	- enhanced by Karsten Hilbert for GNUmed
	- enhanced by Ian Haywood for aumed
	- enhanced by Karsten Hilbert for GNUmed

	@param matcher: a class used to find matches for the current input
	@type matcher: a L{match provider<Gnumed.pycommon.gmMatchProvider.cMatchProvider>}
		instance or C{None}

	@param selection_only: whether free-text can be entered without associated data
	@type selection_only: boolean

	@param capitalisation_mode: how to auto-capitalize input, valid values
		are found in L{capitalize()<Gnumed.pycommon.gmTools.capitalize>}
	@type capitalisation_mode: integer

	@param accepted_chars: a regex pattern defining the characters
		acceptable in the input string, if None no checking is performed
	@type accepted_chars: None or a string holding a valid regex pattern

	@param final_regex: when the control loses focus the input is
		checked against this regular expression
	@type final_regex: a string holding a valid regex pattern

	@param navigate_after_selection: whether or not to immediately
		navigate to the widget next-in-tab-order after selecting an
		item from the dropdown picklist
	@type navigate_after_selection: boolean

	@param picklist_delay: this much time of user inactivity must have
		passed before the input related smarts kick in and the drop
		down pick list is shown
	@type picklist_delay: integer (milliseconds)
	"""
	def __init__ (self, parent=None, id=-1, *args, **kwargs):

		# behaviour
		self.matcher = None
		self.selection_only = False
		self.selection_only_error_msg = _('You must select a value from the picklist or type an exact match.')
		self.capitalisation_mode = gmTools.CAPS_NONE
		self.accepted_chars = None
		self.final_regex = '.*'
		self.final_regex_error_msg = _('The content is invalid. It must match the regular expression: [%%s]. <%s>') % self.__class__.__name__
		self.navigate_after_selection = False
		self.picklist_delay = 150		# milliseconds

		# state tracking
		self._has_focus = False
		self._current_match_candidates = []
		self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
		self.suppress_text_update_smarts = False

		self.__static_tt = None
		self.__static_tt_extra = None
		#  list_label - what's been selected from the dropdown list
		#  field_label - what's being shown in the widget after selection for the selected dropdown list item
		#  data - the underlying data corresponding to the selected item
		self._data = {}

		self._on_selection_callbacks = []
		self._on_lose_focus_callbacks = []
		self._on_set_focus_callbacks = []
		self._on_modified_callbacks = []

		try:
			kwargs['style'] = kwargs['style'] | wx.TE_PROCESS_TAB | wx.TE_PROCESS_ENTER
		except KeyError:
			kwargs['style'] = wx.TE_PROCESS_TAB | wx.TE_PROCESS_ENTER
		super(cPhraseWheelBase, self).__init__(parent, id, **kwargs)

		self.__my_startup_color = self.GetBackgroundColour()
		self.__background_color_without_focus = self.GetBackgroundColour()
		global color_prw_valid
		if color_prw_valid is None:
			color_prw_valid = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

		self.__init_dropdown(parent = parent)
		self.__register_events()
		self.__init_timer()

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def GetData(self, can_create:bool=False, as_instance:bool=False, link_obj=None):
		"""Retrieve the data associated with the displayed string(s).

		Returns:
			None, if no data available, and unable to create data.

			Or a data instance, if requested and data is available or create-able.

			Or the data itself.
		"""
		if not self._data:
			if can_create:
				self._create_data(link_obj = link_obj)

		if not self._data:
			return None

		if as_instance:
			return self._data2instance(link_obj = link_obj)

		return self._data['data']

	#---------------------------------------------------------
	def SetText(self, value:str='', data=None, suppress_smarts:bool=False):
		"""Set both value and data of phrasewheel.

		Args:
			value: some text to display in the control
			data: the data value represented by the displayed text
			suppress_smarts: whether to generate data based on value, always True if data is passed in
		"""
		if value is None:
			value = ''

		if (value == '') and (data is None):
			self._data = {}
			super(cPhraseWheelBase, self).SetValue(value)
			return

		self.suppress_text_update_smarts = suppress_smarts

		if data:
			self.suppress_text_update_smarts = True
			self._data = self._dictify_data(data = data, value = value)
		super(cPhraseWheelBase, self).SetValue(value)
		self.display_as_valid(valid = True)

		# if data already available
		if len(self._data) > 0:
			return True

		# empty text value ?
		if value == '':
			# valid value not required ?
			if not self.selection_only:
				return True

		if not self._set_data_to_first_match():
			# not found
			if self.selection_only:
				self.display_as_valid(valid = False)
				return False

		return True

	#--------------------------------------------------------
	def set_from_instance(self, instance):
		raise NotImplementedError('[%s]: set_from_instance()' % self.__class__.__name__)
	#--------------------------------------------------------
	def set_from_pk(self, pk):
		raise NotImplementedError('[%s]: set_from_pk()' % self.__class__.__name__)
	#--------------------------------------------------------
	def display_as_valid(self, valid:bool=True):
		"""Color input field based on content validity.

			valid: whether the content ist valid (True) or invalid (False), False = partially invalid
		"""
		assert valid in [True, False, None], '<valid> must be True or False or None'
		if valid is True:
			color2show = self.__my_startup_color
		elif valid is False:
			color2show = color_prw_invalid
		else:
			color2show = color_prw_partially_invalid
		if self.IsEnabled():
			self.SetBackgroundColour(color2show)
			self.Refresh()
			return

		self.__previous_enabled_bg_color = color2show

	#--------------------------------------------------------
	def Disable(self):
		self.Enable(enable = False)
	#--------------------------------------------------------
	def Enable(self, enable=True):
		if self.IsEnabled() is enable:
			return

		if self.IsEnabled():
			self.__previous_enabled_bg_color = self.GetBackgroundColour()

		super(cPhraseWheelBase, self).Enable(enable)

		if enable is True:
			#self.SetBackgroundColour(color_prw_valid)
			self.SetBackgroundColour(self.__previous_enabled_bg_color)
		elif enable is False:
			self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
		else:
			raise ValueError('<enable> must be True or False')

		self.Refresh()

	#--------------------------------------------------------
	# callback API
	#--------------------------------------------------------
	def add_callback_on_selection(self, callback=None):
		"""Add a callback for invocation when a picklist item is selected.

		The callback will be invoked whenever an item is selected
		from the picklist. The associated data is passed in as
		a single parameter. Callbacks must be able to cope with
		None as the data parameter as that is sent whenever the
		user changes a previously selected value.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_selection]: ignoring callback [%s], it is not callable' % callback)

		self._on_selection_callbacks.append(callback)

	#---------------------------------------------------------
	def add_callback_on_set_focus(self, callback=None):
		"""Add a callback for invocation when getting focus."""
		if not callable(callback):
			raise ValueError('[add_callback_on_set_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_set_focus_callbacks.append(callback)

	#---------------------------------------------------------
	def add_callback_on_lose_focus(self, callback=None):
		"""Add a callback for invocation when losing focus."""
		if not callable(callback):
			raise ValueError('[add_callback_on_lose_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_lose_focus_callbacks.append(callback)
	#---------------------------------------------------------
	def add_callback_on_modified(self, callback=None):
		"""Add a callback for invocation when the content is modified.

		This callback will NOT be passed any values.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_modified]: ignoring callback [%s] - not callable' % callback)

		self._on_modified_callbacks.append(callback)
	#--------------------------------------------------------
	# match provider proxies
	#--------------------------------------------------------
	def set_context(self, context=None, val=None):
		if self.matcher is not None:
			self.matcher.set_context(context=context, val=val)
	#---------------------------------------------------------
	def unset_context(self, context=None):
		if self.matcher is not None:
			self.matcher.unset_context(context=context)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	# picklist handling
	#--------------------------------------------------------
	def __init_dropdown(self, parent = None):
		szr_dropdown = None
		try:
			#raise NotImplementedError		# uncomment for testing
			self.__dropdown_needs_relative_position = False
			self._picklist_dropdown = wx.PopupWindow(parent)
			list_parent = self._picklist_dropdown
			self.__use_fake_popup = False
		except NotImplementedError:
			self.__use_fake_popup = True
			# on MacOSX wx.PopupWindow is not implemented, so emulate it
			szr_dropdown = wx.BoxSizer(wx.VERTICAL)
			# using wx.MiniFrame
			self.__dropdown_needs_relative_position = False
			self._picklist_dropdown = wx.MiniFrame (
				parent = parent,
				id = -1,
				style = wx.SIMPLE_BORDER | wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_NO_TASKBAR | wx.POPUP_WINDOW
			)
			scroll_win = wx.ScrolledWindow(parent = self._picklist_dropdown, style = wx.NO_BORDER)
			scroll_win.SetSizer(szr_dropdown)
			list_parent = scroll_win
			# using wx.Window
			#self.__dropdown_needs_relative_position = True
			#self._picklist_dropdown = wx.ScrolledWindow(parent=parent, style = wx.RAISED_BORDER)
			#self._picklist_dropdown.SetSizer(szr_dropdown)
			#list_parent = self._picklist_dropdown

		self.__mac_log('dropdown parent: %s' % self._picklist_dropdown.GetParent())

		self._picklist = cPhraseWheelListCtrl (
			list_parent,
			style = wx.LC_NO_HEADER
		)
		self._picklist.InsertColumn(0, '')

		if szr_dropdown is not None:
			szr_dropdown.Add(self._picklist, 1, wx.EXPAND)

		self._picklist_dropdown.Hide()

	#--------------------------------------------------------
	def _show_picklist(self, input2match):
		"""Display the pick list if useful."""

		self._picklist_dropdown.Hide()

		if not self._has_focus:
			return

		if len(self._current_match_candidates) == 0:
			return

		# if only one match and text == match: do not show
		# picklist but rather pick that match
		if len(self._current_match_candidates) == 1:
			candidate = self._current_match_candidates[0]
			if candidate['field_label'] == input2match:
				self._update_data_from_picked_item(candidate)
				return

		# recalculate size
		dropdown_size = self._picklist_dropdown.GetSize()
		border_width = 4
		extra_height = 25
		# height
		rows = len(self._current_match_candidates)
		if rows < 2:				# 2 rows minimum
			rows = 2
		if rows > 20:				# 20 rows maximum
			rows = 20
		self.__mac_log('dropdown needs rows: %s' % rows)
		pw_size = self.GetSize()
		dropdown_size.SetHeight (
			(pw_size.height * rows)
			+ border_width
			+ extra_height
		)
		# width
		dropdown_size.SetWidth(min (
			self.Size.width * 2,
			self.Parent.Size.width
		))

		# recalculate position
		(pw_x_abs, pw_y_abs) = self.ClientToScreen(0,0)
		self.__mac_log('phrasewheel position (on screen): x:%s-%s, y:%s-%s' % (pw_x_abs, (pw_x_abs+pw_size.width), pw_y_abs, (pw_y_abs+pw_size.height)))
		dropdown_new_x = pw_x_abs
		dropdown_new_y = pw_y_abs + pw_size.height
		self.__mac_log('desired dropdown position (on screen): x:%s-%s, y:%s-%s' % (dropdown_new_x, (dropdown_new_x+dropdown_size.width), dropdown_new_y, (dropdown_new_y+dropdown_size.height)))
		self.__mac_log('desired dropdown size: %s' % dropdown_size)

		# reaches beyond screen ?
		if (dropdown_new_y + dropdown_size.height) > self._screenheight:
			self.__mac_log('dropdown extends offscreen (screen max y: %s)' % self._screenheight)
			max_height = self._screenheight - dropdown_new_y - 4
			self.__mac_log('max dropdown height would be: %s' % max_height)
			if max_height > ((pw_size.height * 2) + 4):
				dropdown_size.SetHeight(max_height)
				self.__mac_log('possible dropdown position (on screen): x:%s-%s, y:%s-%s' % (dropdown_new_x, (dropdown_new_x+dropdown_size.width), dropdown_new_y, (dropdown_new_y+dropdown_size.height)))
				self.__mac_log('possible dropdown size: %s' % dropdown_size)

		# now set dimensions
		self._picklist_dropdown.SetSize(dropdown_size)
		self._picklist.SetSize(self._picklist_dropdown.GetClientSize())
		self.__mac_log('pick list size set to: %s' % self._picklist_dropdown.GetSize())
		if self.__dropdown_needs_relative_position:
			dropdown_new_x, dropdown_new_y = self._picklist_dropdown.GetParent().ScreenToClientXY(dropdown_new_x, dropdown_new_y)
		self._picklist_dropdown.Move(dropdown_new_x, dropdown_new_y)

		# select first value
		self._picklist.Select(0)

		# and show it
		self._picklist_dropdown.Show(True)

#		dropdown_top_left = self._picklist_dropdown.ClientToScreen(0,0)
#		dropdown_size = self._picklist_dropdown.GetSize()
#		dropdown_bottom_right = self._picklist_dropdown.ClientToScreen(dropdown_size.width, dropdown_size.height)
#		self.__mac_log('dropdown placement now (on screen): x:%s-%s, y:%s-%s' % (
#			dropdown_top_left[0],
#			dropdown_bottom_right[0],
#			dropdown_top_left[1],
#			dropdown_bottom_right[1])
#		)

	#--------------------------------------------------------
	def _hide_picklist(self):
		"""Hide the pick list."""
		self._picklist_dropdown.Hide()

	#--------------------------------------------------------
	def _select_picklist_row(self, new_row_idx=None, old_row_idx=None):
		"""Mark the given picklist row as selected."""
		if old_row_idx is not None:
			pass			# FIXME: do we need unselect here ? Select() should do it for us
		self._picklist.Select(new_row_idx)
		self._picklist.EnsureVisible(new_row_idx)
	#--------------------------------------------------------
	def _picklist_item2display_string(self, item=None):
		"""Get string to display in the field for the given picklist item."""
		if item is None:
			item = self._picklist.get_selected_item()
		try:
			return item['field_label']
		except KeyError:
			pass
		try:
			return item['list_label']
		except KeyError:
			pass
		try:
			return item['label']
		except KeyError:
			return '<no field_*/list_*/label in item>'
			#return self._picklist.GetItemText(self._picklist.GetFirstSelected())

	#--------------------------------------------------------
	def _update_display_from_picked_item(self, item):
		"""Update the display to show item strings."""
		# default to single phrase
		display_string = self._picklist_item2display_string(item = item)
		self.suppress_text_update_smarts = True
		super(cPhraseWheelBase, self).SetValue(display_string)
		# in single-phrase phrasewheels always set cursor to end of string
		self.SetInsertionPoint(self.GetLastPosition())
		return

	#--------------------------------------------------------
	# match generation
	#--------------------------------------------------------
	def _extract_fragment_to_match_on(self):
		raise NotImplementedError('[%s]: fragment extraction not implemented' % self.__class__.__name__)
	#---------------------------------------------------------
	def _update_candidates_in_picklist(self, val):
		"""Get candidates matching the currently typed input."""

		# get all currently matching items
		self._current_match_candidates = []
		if self.matcher is not None:
			matched, self._current_match_candidates = self.matcher.getMatches(val)
			self._picklist.SetItems(self._current_match_candidates)

	#--------------------------------------------------------
	# tooltip handling
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		# child classes can override this to provide
		# per data item dynamic tooltips,
		# by default do not support dynamic tooltip parts:
		return None

	#--------------------------------------------------------
	def __recalculate_tooltip(self):
		"""Calculate dynamic tooltip part based on data item.

		- called via ._set_data() each time property .data (-> .__data) is set
		- hence also called the first time data is set
		- the static tooltip can be set any number of ways before that
		- only when data is first set does the dynamic part become relevant
		- hence it is sufficient to remember the static part when .data is
		  set for the first time
		"""
		if self.__static_tt is None:
			if self.ToolTip is None:
				self.__static_tt = ''
			else:
				self.__static_tt = self.ToolTip.Tip

		# need to always calculate static part because
		# the dynamic part can have *become* None, again,
		# in which case we want to be able to re-set the
		# tooltip to the static part
		static_part = self.__static_tt
		if (self.__static_tt_extra) is not None and (self.__static_tt_extra.strip() != ''):
			static_part = '%s\n\n%s' % (
				static_part,
				self.__static_tt_extra
			)

		dynamic_part = self._get_data_tooltip()
		if dynamic_part is None:
			self.SetToolTip(static_part)
			return

		if static_part == '':
			tt = dynamic_part
		else:
			if dynamic_part.strip() == '':
				tt = static_part
			else:
				tt = '%s\n\n%s\n\n%s' % (
					dynamic_part,
					gmTools.u_box_horiz_single * 32,
					static_part
				)

		self.SetToolTip(tt)

	#--------------------------------------------------------
	def _get_static_tt_extra(self):
		return self.__static_tt_extra

	def _set_static_tt_extra(self, tt):
		self.__static_tt_extra = tt

	static_tooltip_extra = property(_get_static_tt_extra, _set_static_tt_extra)

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
		self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
		self.Bind(wx.EVT_KILL_FOCUS, self._on_lose_focus)
		self.Bind(wx.EVT_TEXT, self._on_text_update)
		self._picklist.Bind(wx.EVT_LEFT_DCLICK, self._on_list_item_selected)

	#--------------------------------------------------------
	def _on_key_down(self, event):
		"""Is called when a key is pressed."""

		keycode = event.GetKeyCode()

		if keycode == wx.WXK_DOWN:
			self.__on_cursor_down()
			return

		if keycode == wx.WXK_UP:
			self.__on_cursor_up()
			return

		if keycode == wx.WXK_RETURN:
			self._on_enter()
			return

		if keycode == wx.WXK_TAB:
			if event.ShiftDown():
				self.Navigate(flags = wx.NavigationKeyEvent.IsBackward)
				return
			self.__on_tab()
			self.Navigate(flags = wx.NavigationKeyEvent.IsForward)
			return

		# FIXME: need PAGE UP/DOWN//POS1/END here to move in picklist
		if keycode in [wx.WXK_SHIFT, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT]:
			pass

		# need to handle all non-character key presses *before* this check
		elif not self.__char_is_allowed(char = chr(event.GetUnicodeKey())):
			wx.Bell()
			# Richard doesn't show any error message here
			return

		event.Skip()
		return
	#--------------------------------------------------------
	def _on_set_focus(self, event):

		self._has_focus = True
		event.Skip()

		self.__background_color_without_focus = self.GetBackgroundColour()
		self.SetBackgroundColour(COLOR_BG_PRW_WITH_FOCUS)
		self.Refresh()

		# notify interested parties
		for callback in self._on_set_focus_callbacks:
			callback()

		self.__timer.Start(oneShot = True, milliseconds = self.picklist_delay)
		return True
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		"""Do stuff when leaving the control.

		The user has had her say, so don't second guess
		intentions but do report error conditions.
		"""
		event.Skip()
		self._has_focus = False
		self.__timer.Stop()
		self._hide_picklist()
		self.SetBackgroundColour(self.__background_color_without_focus)
		self.Refresh()
		wx.CallAfter(self.__on_lost_focus)
		return True

	#--------------------------------------------------------
	def __on_lost_focus(self):
		if not self:
			return

		self.SetSelection(1,1)
		is_valid = True
		# the user may have typed a phrase that is an exact match,
		# however, just typing it won't associate data from the
		# picklist, so try do that now
		self._set_data_to_first_match()

		# check value against final_regex if any given
		if self.__final_regex.match(self.GetValue().strip()) is None:
			gmDispatcher.send(signal = 'statustext', msg = self.final_regex_error_msg % self.final_regex)
			is_valid = False

		self.display_as_valid(valid = is_valid)

		# notify interested parties
		for callback in self._on_lose_focus_callbacks:
			callback()
	#--------------------------------------------------------
	def _on_list_item_selected(self, *args, **kwargs):
		"""Gets called when user selected a list item."""

		self._hide_picklist()

		item = self._picklist.get_selected_item()
		# huh ?
		if item is None:
			self.display_as_valid(valid = True)
			return

		self._update_display_from_picked_item(item)
		self._update_data_from_picked_item(item)
		self.MarkDirty()

		# and tell the listeners about the user's selection
		for callback in self._on_selection_callbacks:
			callback(self._data)

		if self.navigate_after_selection:
			self.Navigate()

		return
	#--------------------------------------------------------
	def _on_text_update (self, event):
		"""Internal handler for wx.EVT_TEXT.

		Called when text was changed by user or by SetValue().
		"""
		if self.suppress_text_update_smarts:
			self.suppress_text_update_smarts = False
			return

		self._adjust_data_after_text_update()
		self._current_match_candidates = []

		val = self.GetValue().strip()
		ins_point = self.GetInsertionPoint()

		# if empty string then hide list dropdown window
		# we also don't need a timer event then
		if val == '':
			self._hide_picklist()
			self.__timer.Stop()
		else:
			new_val = gmTools.capitalize(text = val, mode = self.capitalisation_mode)
			if new_val != val:
				self.suppress_text_update_smarts = True
				super(cPhraseWheelBase, self).SetValue(new_val)
				if ins_point > len(new_val):
					self.SetInsertionPointEnd()
				else:
					self.SetInsertionPoint(ins_point)
					# FIXME: SetSelection() ?

			# start timer for delayed match retrieval
			self.__timer.Start(oneShot = True, milliseconds = self.picklist_delay)

		# notify interested parties
		for callback in self._on_modified_callbacks:
			callback()

		return
	#--------------------------------------------------------
	# keypress handling
	#--------------------------------------------------------
	def _on_enter(self):
		"""Called when the user pressed <ENTER>."""
		if self._picklist_dropdown.IsShown():
			self._on_list_item_selected()
			return

		# FIXME: check for errors before navigation
		self.Navigate()

	#--------------------------------------------------------
	def __on_cursor_down(self):

		if self._picklist_dropdown.IsShown():
			idx_selected = self._picklist.GetFirstSelected()
			if idx_selected < (len(self._current_match_candidates) - 1):
				self._select_picklist_row(idx_selected + 1, idx_selected)
			return

		# if we don't yet have a pick list: open new pick list
		# (this can happen when we TAB into a field pre-filled
		# with the top-weighted contextual item but want to
		# select another contextual item)
		self.__timer.Stop()
		if self.GetValue().strip() == '':
			val = '*'
		else:
			val = self._extract_fragment_to_match_on()
		self._update_candidates_in_picklist(val = val)
		self._show_picklist(input2match = val)

	#--------------------------------------------------------
	def __on_cursor_up(self):
		if self._picklist_dropdown.IsShown():
			selected = self._picklist.GetFirstSelected()
			if selected > 0:
				self._select_picklist_row(selected-1, selected)
		#else:
		#	# FIXME: input history ?

	#--------------------------------------------------------
	def __on_tab(self):
		"""Under certain circumstances take special action on <TAB>.

		returns:
			True: <TAB> was handled
			False: <TAB> was not handled

		-> can be used to decide whether to do further <TAB> handling outside this class
		"""
		# are we seeing the picklist ?
		if not self._picklist_dropdown.IsShown():
			return False

		# with only one candidate ?
		if len(self._current_match_candidates) != 1:
			return False

		# and do we require the input to be picked from the candidates ?
		if not self.selection_only:
			return False

		# then auto-select that item
		self._select_picklist_row(new_row_idx = 0)
		self._on_list_item_selected()

		return True
	#--------------------------------------------------------
	# timer handling
	#--------------------------------------------------------
	def __init_timer(self):
		self.__timer = _cPRWTimer()
		self.__timer.callback = self._on_timer_fired
		# initially stopped
		self.__timer.Stop()
	#--------------------------------------------------------
	def _on_timer_fired(self):
		"""Callback for delayed match retrieval timer.

		if we end up here:
		 - delay has passed without user input
		 - the value in the input field has not changed since the timer started
		"""
		# update matches according to current input
		val = self._extract_fragment_to_match_on()
		self._update_candidates_in_picklist(val = val)

		# we now have either:
		# - all possible items (within reasonable limits) if input was '*'
		# - all matching items
		# - an empty match list if no matches were found
		# also, our picklist is refilled and sorted according to weight
		wx.CallAfter(self._show_picklist, input2match = val)
	#----------------------------------------------------
	# random helpers and properties
	#----------------------------------------------------
	def __mac_log(self, msg):
		if self.__use_fake_popup:
			_log.debug(msg)

	#--------------------------------------------------------
	def __char_is_allowed(self, char=None):
		# if undefined accept all chars
		if self.accepted_chars is None:
			return True
		return (self.__accepted_chars.match(char) is not None)

	#--------------------------------------------------------
	def _set_accepted_chars(self, accepted_chars=None):
		if accepted_chars is None:
			self.__accepted_chars = None
		else:
			self.__accepted_chars = regex.compile(accepted_chars)

	def _get_accepted_chars(self):
		if self.__accepted_chars is None:
			return None
		return self.__accepted_chars.pattern

	accepted_chars = property(_get_accepted_chars, _set_accepted_chars)

	#--------------------------------------------------------
	def _set_final_regex(self, final_regex=r'.*'):
		self.__final_regex = regex.compile(final_regex, flags = regex.UNICODE)

	def _get_final_regex(self):
		return self.__final_regex.pattern

	final_regex = property(_get_final_regex, _set_final_regex)

	#--------------------------------------------------------
	def _set_final_regex_error_msg(self, msg):
		self.__final_regex_error_msg = msg

	def _get_final_regex_error_msg(self):
		return self.__final_regex_error_msg

	final_regex_error_msg = property(_get_final_regex_error_msg, _set_final_regex_error_msg)

	#--------------------------------------------------------
	# data munging
	#--------------------------------------------------------
	def _set_data_to_first_match(self):
		return False

	#--------------------------------------------------------
	def _update_data_from_picked_item(self, item):
		self._data = self._dictify_data(data = item)

	#---------------------------------------------------------
	def _dictify_data(self, data=None, value=None) -> dict:
		if isinstance(data, dict):
			# test for dict being well-formed
			data['data']
			data['list_label']
			data['field_label']
			return data

		if not value:
			value = '%s' % data
		return {'data': data, 'list_label': value, 'field_label': value}

#	#--------------------------------------------------------
#	def _dictify_data(self, data=None, value=None):
#		raise NotImplementedError('[%s]: _dictify_data()' % self.__class__.__name__)
	#---------------------------------------------------------
	def _adjust_data_after_text_update(self):
		raise NotImplementedError('[%s]: cannot adjust data after text update' % self.__class__.__name__)
	#--------------------------------------------------------
	def _data2match(self, data):
		if self.matcher is None:
			return None
		return self.matcher.get_match_by_data(data = data)

	#--------------------------------------------------------
	def _create_data(self, link_obj=None):
		"""Must set self._data if possible/successful."""
		raise NotImplementedError('[%s]: cannot create data object' % self.__class__.__name__)

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		"""Turn selected data into class instance.

		Returns:
			A class instance, typically a subclass of gmBusinessDBObject.cBusinessDBObject, or None.
		"""
		raise NotImplementedError('[%s]: cannot turn data object' % self.__class__.__name__)

	#--------------------------------------------------------
	def _get_raw_data(self):
		return self._data

	def _set_raw_data(self, raw_data:dict):
		"""Explicitly set raw data of phrasewheel.

		Args:
			raw_data: a dict with the keys 'data' (the actual value), 'list_label' (shown in the picklist when selecting an item), and 'field_label' (shown in the phrasewheel after this idem had been selected)
		"""
		self._data = raw_data
		self.__recalculate_tooltip()

	raw_data = property(_get_raw_data, _set_raw_data)

#============================================================
# FIXME: cols in pick list
# FIXME: snap_to_basename+set selection
# FIXME: learn() -> PWL
# FIXME: up-arrow: show recent (in-memory) history
#----------------------------------------------------------
# ideas
#----------------------------------------------------------
#- display possible completion but highlighted for deletion
#(- cycle through possible completions)
#- pre-fill selection with SELECT ... LIMIT 25
#- async threads for match retrieval instead of timer
#  - on truncated results return item "..." -> selection forcefully retrieves all matches

#- generators/yield()
#- OnChar() - process a char event

# split input into words and match components against known phrases

# make special list window:
# - deletion of items
# - highlight matched parts
# - faster scrolling
# - wxEditableListBox ?

# - if non-learning (i.e. fast select only): autocomplete with match
#   and move cursor to end of match
#-----------------------------------------------------------------------------------------------
# darn ! this clever hack won't work since we may have crossed a search location threshold
#----
#	#self.__prevFragment = "***********-very-unlikely--------------***************"
#	#self.__prevMatches = []		# a list of tuples (ID, listbox name, weight)
#
#	# is the current fragment just a longer version of the previous fragment ?
#	if string.find(aFragment, self.__prevFragment) == 0:
#	    # we then need to search in the previous matches only
#	    for prevMatch in self.__prevMatches:
#		if string.find(prevMatch[1], aFragment) == 0:
#		    matches.append(prevMatch)
#	    # remember current matches
#	    self.__prefMatches = matches
#	    # no matches found
#	    if len(matches) == 0:
#		return [(1,_('*no matching items found*'),1)]
#	    else:
#		return matches
#----
#TODO:
# - see spincontrol for list box handling
# stop list (list of negatives): "an" -> "animal" but not "and"
#-----
#> > remember, you should be searching on  either weighted data, or in some
#> > situations a start string search on indexed data
#>
#> Can you be a bit more specific on this ?

#searching ones own previous text entered  would usually be instring but
#weighted (ie the phrases you use the most auto filter to the top)

#Searching a drug database for a   drug product name is usually more
#functional if it does a start string search, not an instring search which is
#much slower and usually unecesary.  There are many other examples but trust
#me one needs both

# FIXME: support selection-only-or-empty

#============================================================
class cPhraseWheel(cPhraseWheelBase):
	"""Standard single-value Phrasewheel."""

	#---------------------------------------------------------
	def SetData(self, data=None):
		"""Set the data and thereby set the value, too. if possible.

		If you call SetData() you better be prepared
		doing a scan of the entire potential match space.

		The data value must be found in the match space.

		Args:
			data: None -> unset data, otherwise a valid (as per match provider) value from the search space
		"""
		if data is None:
			self._data = {}
			return True

		# try getting match candidates
		self._update_candidates_in_picklist('*')

		# do we require a match ?
		if self.selection_only:
			# yes, but we don't have any candidates
			if len(self._current_match_candidates) == 0:
				self.display_as_valid(valid = False)
				return False

		# among candidates look for a match with <data>
		for candidate in self._current_match_candidates:
			if candidate['data'] == data:
				super(cPhraseWheel, self).SetText (
					value = candidate['field_label'],
					data = data,
					suppress_smarts = True
				)
				return True

		# no match found in candidates (but needed) ...
		if self.selection_only:
			self.display_as_valid(valid = False)
			return False

		# match providers simply return values, so turn them into the dict internally
		self._data = self._dictify_data(data = data)
		self.display_as_valid(valid = True)
		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def _show_picklist(self, input2match):

		# this helps if the current input was already selected from the
		# list but still is the substring of another pick list item or
		# else the picklist will re-open just after selection
		if len(self._data) > 0:
			self._picklist_dropdown.Hide()
			return

		return super(cPhraseWheel, self)._show_picklist(input2match = input2match)

	#--------------------------------------------------------
	def _set_data_to_first_match(self):
		# data already set ?
		if len(self._data) > 0:
			return True

		# needed ?
		val = self.GetValue().strip()
		if val == '':
			return True

		# so try
		self._update_candidates_in_picklist(val = val)
		for candidate in self._current_match_candidates:
			if candidate['field_label'] == val:
				self._update_data_from_picked_item(candidate)
				self.MarkDirty()
				# tell listeners about the user's selection
				for callback in self._on_selection_callbacks:
					callback(self._data)
				return True

		# no exact match found
		if self.selection_only:
			gmDispatcher.send(signal = 'statustext', msg = self.selection_only_error_msg)
			return False

		return True

	#---------------------------------------------------------
	def _adjust_data_after_text_update(self):
		self._data = {}

	#---------------------------------------------------------
	def _extract_fragment_to_match_on(self):
		return self.GetValue().strip()

#	#---------------------------------------------------------
#	def _dictify_data(self, data=None, value=None):
#		# assume data to always be old style
#		if value is None:
#			value = '%s' % data
#		return {'data': data, 'list_label': value, 'field_label': value}

#============================================================
class cMultiPhraseWheel(cPhraseWheelBase):

	def __init__(self, *args, **kwargs):

		super(cMultiPhraseWheel, self).__init__(*args, **kwargs)

		self.phrase_separators = default_phrase_separators
		self.left_part = ''
		self.right_part = ''

	#---------------------------------------------------------
	def GetData(self, can_create=False, as_instance=False, link_obj=None):
		super().GetData(can_create = can_create, link_obj = link_obj)
		if len(self._data) > 0:
			if as_instance:
				return self._data2instance(link_obj = link_obj)

		return list(self._data.values())

	#---------------------------------------------------------
	def list2data_dict(self, data_items=None):

		data_dict = {}

		for item in data_items:
			try:
				list_label = item['list_label']
			except KeyError:
				list_label = item['label']
			try:
				field_label = item['field_label']
			except KeyError:
				field_label = list_label
			data_dict[field_label] = {'data': item['data'], 'list_label': list_label, 'field_label': field_label}

		return data_dict
	#---------------------------------------------------------
	# internal API
	#---------------------------------------------------------
	def _adjust_data_after_text_update(self):
		# the textctrl display must already be set properly
		new_data = {}
		# this way of looping automatically removes stale
		# data for labels which are no longer displayed
		for displayed_label in self.displayed_strings:
			try:
				new_data[displayed_label] = self._data[displayed_label]
			except KeyError:
				# this removes stale data for which there
				# is no displayed_label anymore
				pass

		self.data = new_data
	#---------------------------------------------------------
	def _extract_fragment_to_match_on(self):

		cursor_pos = self.GetInsertionPoint()

		entire_input = self.GetValue()
		if self.__phrase_separators.search(entire_input) is None:
			self.left_part = ''
			self.right_part = ''
			return self.GetValue().strip()

		string_left_of_cursor = entire_input[:cursor_pos]
		string_right_of_cursor = entire_input[cursor_pos:]

		left_parts = [ lp.strip() for lp in self.__phrase_separators.split(string_left_of_cursor) ]
		if len(left_parts) == 0:
			self.left_part = ''
		else:
			self.left_part = '%s%s ' % (
				('%s ' % self.__phrase_separators.pattern[0]).join(left_parts[:-1]),
				self.__phrase_separators.pattern[0]
			)

		right_parts = [ rp.strip() for rp in self.__phrase_separators.split(string_right_of_cursor) ]
		self.right_part = '%s %s' % (
			self.__phrase_separators.pattern[0],
			('%s ' % self.__phrase_separators.pattern[0]).join(right_parts[1:])
		)

		val = (left_parts[-1] + right_parts[0]).strip()
		return val
	#--------------------------------------------------------
	def _update_display_from_picked_item(self, item):
		val = ('%s%s%s' % (
			self.left_part,
			self._picklist_item2display_string(item = item),
			self.right_part
		)).lstrip().lstrip(';').strip()
		self.suppress_text_update_smarts = True
		super(cMultiPhraseWheel, self).SetValue(val)
		# find item end and move cursor to that place:
		item_end = val.index(item['field_label']) + len(item['field_label'])
		self.SetInsertionPoint(item_end)
		return
	#--------------------------------------------------------
	def _update_data_from_picked_item(self, item):

		# add item to the data
		self._data[item['field_label']] = item

		# the textctrl display must already be set properly
		field_labels = [ p.strip() for p in self.__phrase_separators.split(self.GetValue().strip()) ]
		new_data = {}
		# this way of looping automatically removes stale
		# data for labels which are no longer displayed
		for field_label in field_labels:
			try:
				new_data[field_label] = self._data[field_label]
			except KeyError:
				# this removes stale data for which there
				# is no displayed_label anymore
				pass

		self.data = new_data
	#---------------------------------------------------------
	def _dictify_data(self, data=None, value=None):
		if type(data) == type([]):
			# useful because self.GetData() returns just such a list
			return self.list2data_dict(data_items = data)
		# else assume new-style already-dictified data
		return data
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _set_phrase_separators(self, phrase_separators):
		"""Set phrase separators.

		- must be a valid regular expression pattern

		input is split into phrases at boundaries defined by
		this regex and matching is performed on the phrase
		the cursor is in only,

		after selection from picklist phrase_separators[0] is
		added to the end of the match in the PRW
		"""
		self.__phrase_separators = regex.compile(phrase_separators, flags = regex.UNICODE)

	def _get_phrase_separators(self):
		return self.__phrase_separators.pattern

	phrase_separators = property(_get_phrase_separators, _set_phrase_separators)
	#--------------------------------------------------------
	def _get_displayed_strings(self):
		return [ p.strip() for p in self.__phrase_separators.split(self.GetValue().strip()) if p.strip() != '' ]

	displayed_strings = property(_get_displayed_strings)
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#from Gnumed.pycommon import gmPG2, gmMatchProvider

	prw = None				# used for access from display_values_*
	#--------------------------------------------------------
	def display_values_set_focus(*args, **kwargs):
		print("got focus:")
		print("value:", prw.GetValue())
		print("data :", prw.GetData())
		return True
	#--------------------------------------------------------
	def display_values_lose_focus(*args, **kwargs):
		print("lost focus:")
		print("value:", prw.GetValue())
		print("data :", prw.GetData())
		return True
	#--------------------------------------------------------
	def display_values_modified(*args, **kwargs):
		print("modified:")
		print("value:", prw.GetValue())
		print("data :", prw.GetData())
		return True
	#--------------------------------------------------------
	def display_values_selected(*args, **kwargs):
		print("selected:")
		print("value:", prw.GetValue())
		print("data :", prw.GetData())
		return True
	#--------------------------------------------------------
	#--------------------------------------------------------
#	def test_prw_fixed_list():
#		app = wx.PyWidgetTester(size = (200, 50))

#		items = [	{'data': 1, 'list_label': "Bloggs", 'field_label': "Bloggs", 'weight': 0},
#					{'data': 2, 'list_label': "Baker", 'field_label': "Baker", 'weight': 0},
#					{'data': 3, 'list_label': "Jones", 'field_label': "Jones", 'weight': 0},
#					{'data': 4, 'list_label': "Judson", 'field_label': "Judson", 'weight': 0},
#					{'data': 5, 'list_label': "Jacobs", 'field_label': "Jacobs", 'weight': 0},
#					{'data': 6, 'list_label': "Judson-Jacobs", 'field_label': "Judson-Jacobs", 'weight': 0}
#				]

#		mp = gmMatchProvider.cMatchProvider_FixedList(items)
		# do NOT treat "-" as a word separator here as there are names like "asa-sismussen"
#		mp.word_separators = '[ \t=+&:@]+'
#		global prw
#		prw = cPhraseWheel(app.frame, -1)
#		prw.matcher = mp
#		prw.capitalisation_mode = gmTools.CAPS_NAMES
#		prw.add_callback_on_set_focus(callback=display_values_set_focus)
#		prw.add_callback_on_modified(callback=display_values_modified)
#		prw.add_callback_on_lose_focus(callback=display_values_lose_focus)
#		prw.add_callback_on_selection(callback=display_values_selected)

#		app.frame.Show(True)
#		app.MainLoop()

#		return True
	#--------------------------------------------------------
#	def test_prw_sql2():
#		print("Do you want to test the database connected phrase wheel ?")
#		yes_no = input('y/n: ')
#		if yes_no != 'y':
#			return True

#		gmPG2.get_connection()
#		query = """SELECT code, code || ': ' || _(name), _(name) FROM dem.country WHERE _(name) %(fragment_condition)s"""
#		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
#		app = wx.PyWidgetTester(size = (400, 50))
#		global prw
		#prw = cPhraseWheel(app.frame, -1)
#		prw = cMultiPhraseWheel(app.frame, -1)
#		prw.matcher = mp

#		app.frame.Show(True)
#		app.MainLoop()

#		return True
	#--------------------------------------------------------
#	def test_prw_patients():
#		gmPG2.get_connection()
#		query = """
#			select
#				pk_identity,
#				firstnames || ' ' || lastnames || ', ' || to_char(dob, 'YYYY-MM-DD'),
#				firstnames || ' ' || lastnames
#			from
#				dem.v_active_persons
#			where
#				firstnames || lastnames %(fragment_condition)s
#		"""
#		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
#		app = wx.PyWidgetTester(size = (500, 50))
#		global prw
#		prw = cPhraseWheel(app.frame, -1)
#		prw.matcher = mp
#		prw.selection_only = True

#		app.frame.Show(True)
#		app.MainLoop()

#		return True

	#--------------------------------------------------------
	#test_prw_fixed_list()
	#test_prw_sql2()
#	test_prw_patients()

#==================================================
