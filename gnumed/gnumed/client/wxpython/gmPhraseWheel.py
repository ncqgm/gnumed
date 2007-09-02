"""GNUmed phrasewheel.

A class, extending wx.TextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPhraseWheel.py,v $
# $Id: gmPhraseWheel.py,v 1.109 2007-09-02 20:56:30 ncq Exp $
__version__ = "$Revision: 1.109 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan <sjtan@bigpond.com>"
__license__ = "GPL"

# stdlib
import string, types, time, sys, re as regex, os.path


# 3rd party
import wx
import wx.lib.mixins.listctrl as listmixins


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.wxpython import gmTimer, gmGuiHelpers
from Gnumed.pycommon import gmTools, gmSignals, gmDispatcher

#============================================================
# those can be used by the <accepted_chars> phrasewheel parameter
NUMERIC = '0-9'
ALPHANUMERIC = 'a-zA-Z0-9'
EMAIL_CHARS = "a-zA-Z0-9\-_@\."
WEB_CHARS = "a-zA-Z0-9\.\-_/:"

#============================================================
# FIXME: merge with gmListWidgets
class cPhraseWheelListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):
	def __init__(self, *args, **kwargs):
		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER
		except: pass
		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#--------------------------------------------------------
	def SetItems(self, items):
		self.DeleteAllItems()
		self.__data = items
		pos = len(items) + 1
		for item in items:
			row_num = self.InsertStringItem(pos, label=item['label'])
	#--------------------------------------------------------
	def GetSelectedItemData(self):
		return self.__data[self.GetFirstSelected()]['data']
	#--------------------------------------------------------
	def get_selected_item_label(self):
		return self.__data[self.GetFirstSelected()]['label']
#============================================================
# FIXME: cols in pick list, snap_to_basename+set selection, learn() -> PWL
class cPhraseWheel(wx.TextCtrl):
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
	@param phrase_separators: if not None, input is split into phrases
		at boundaries defined by this regex and matching/spellchecking
		is performed on the phrase the cursor is in only
	@type phrase_separators: None or a string holding a valid regex pattern
	@param navigate_after_selection: whether or not to immediately
		navigate to the widget next-in-tab-order after selecting an
		item from the dropdown picklist
	@type navigate_after_selection: boolean
	@param speller: if not None used to spellcheck the current input
		and to retrieve suggested replacements/completions
	@type speller: None or a L{enchant Dict<enchant>} descendant
	@param picklist_delay: this much time of user inactivity must have
		passed before the input related smarts kick in and the drop
		down pick list is shown
	@type picklist_delay: integer (milliseconds)
	"""
	def __init__ (self, parent=None, id=-1, value='', *args, **kwargs):

		# behaviour
		self.matcher = None
		self.selection_only = False
		self.selection_only_error_msg = _('You must select a value from the picklist or type an exact match.')
		self.capitalisation_mode = gmTools.CAPS_NONE
		self.accepted_chars = None
		self.final_regex = '.*'
		self.final_regex_error_msg = _('The content is invalid. It must match the pattern: [%s]')
		self.phrase_separators = '[;/|]+'
		self.navigate_after_selection = False
		self.speller = None
		self.speller_word_separators = '[\W\d_]+'
		self.picklist_delay = 150		# milliseconds

		# state tracking
		self._has_focus = False
		self.suppress_text_update_smarts = False
		self.__current_matches = []
		self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
		self.input2match = ''
		self.left_part = ''
		self.right_part = ''
		self.data = None

		self._on_selection_callbacks = []
		self._on_lose_focus_callbacks = []
		self._on_set_focus_callbacks = []
		self._on_modified_callbacks = []

		try:
			kwargs['style'] = kwargs['style'] | wx.TE_PROCESS_TAB
		except KeyError:
			kwargs['style'] = wx.TE_PROCESS_TAB
		wx.TextCtrl.__init__ (self, parent, id, **kwargs)

		# multiple matches dropdown list
		try:
			self.__picklist_dropdown = wx.PopupWindow(parent)
			add_picklist_to_sizer = False
		except NotImplementedError:
			# on MacOSX wx.PopupWindow is not implemented
			self.__picklist_dropdown = wx.Window(parent=self, style = wx.SIMPLE_BORDER)
			szr_scroll = wx.BoxSizer(wx.VERTICAL)
			self.__picklist_dropdown.SetSizer(szr_scroll)
			add_picklist_to_sizer = True

		# FIXME: support optional headers
#		if kwargs['show_list_headers']:
#			flags = 0
#		else:
#			flags = wx.LC_NO_HEADER
		self._picklist = cPhraseWheelListCtrl (
			self.__picklist_dropdown,
			style = wx.LC_NO_HEADER
		)
		self._picklist.InsertColumn(0, '')

		if add_picklist_to_sizer:
			szr_scroll.Add(self._picklist, 1, wx.EXPAND)

		self.__picklist_dropdown.Hide()

		# set event handlers
		self.__register_events()

		self.__timer = gmTimer.cTimer (
			callback = self._on_timer_fired,
			delay = self.picklist_delay
		)
		# initially stopped
		self.__timer.Stop()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def add_callback_on_selection(self, callback=None):
		"""
		Add a callback for invocation when a picklist item is selected.

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
		"""
		Add a callback for invocation when getting focus.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_set_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_set_focus_callbacks.append(callback)
	#---------------------------------------------------------
	def add_callback_on_lose_focus(self, callback=None):
		"""
		Add a callback for invocation when losing focus.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_lose_focus]: ignoring callback [%s] - not callable' % callback)

		self._on_lose_focus_callbacks.append(callback)
	#---------------------------------------------------------
	def add_callback_on_modified(self, callback=None):
		"""
		Add a callback for invocation when the content is modified.
		"""
		if not callable(callback):
			raise ValueError('[add_callback_on_modified]: ignoring callback [%s] - not callable' % callback)

		self._on_modified_callbacks.append(callback)
	#---------------------------------------------------------
	def SetData(self, data=None):
		"""
		Set the data and thereby set the value, too.

		If you call SetData() you better be prepared
		doing a scan of the entire potential match space.

		The whole thing will only work if data is found
		in the match space anyways.
		"""
		if self.matcher is None:
			matched, matches = (False, [])
		else:
			matched, matches = self.matcher.getMatches('*')

		if self.selection_only:
			if not matched or (len(matches) == 0):
				return False

		for match in matches:
			if match['data'] == data:
				self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				self.suppress_text_update_smarts = True
				wx.TextCtrl.SetValue(self, match['label'])
				self.data = data
				return True

		# no match found ...
		if self.selection_only:
			return False

		self.data = data
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		return True
	#---------------------------------------------------------
	def GetData(self):
		"""
		Retrieve the data associated with the displayed string.
		"""
		return self.data
	#---------------------------------------------------------
	def SetText (self, value=u'', data=None):

		if data is not None:
			self.suppress_text_update_smarts = True
			self.data = data
		wx.TextCtrl.SetValue(self, value)
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		# if data already available
		if self.data is not None:
			return True

		if value == u'' and not self.selection_only:
			return True

		# or try to find data from matches
		if self.matcher is None:
			stat, matches = (False, [])
		else:
			stat, matches = self.matcher.getMatches(aFragment = value)

		for match in matches:
			if match['label'] == value:
				self.data = match['data']
				return True

		# not found
		if self.selection_only:
			self.SetBackgroundColour('pink')
			return False

		return True
	#--------------------------------------------------------
	def set_context (self, context=None, val=None):
		if self.matcher is not None:
			self.matcher.set_context(context=context, val=val)
	#---------------------------------------------------------
	def unset_context(self, context=None):
		if self.matcher is not None:
			self.matcher.unset_context(context=context)
	#--------------------------------------------------------
	def enable_default_spellchecker(self):
		try:
			import enchant
		except ImportError:
			self.speller = None
			return False
		try:
			self.speller = enchant.DictWithPWL(None, os.path.expanduser(os.path.join('~', '.gnumed', 'spellcheck', 'wordlist.pwl')))
		except enchant.DictNotFoundError:
			self.speller = None
			return False
		return True
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	# picklist handling
	#--------------------------------------------------------
	def _show_picklist(self):
		"""Display the pick list."""

		self._hide_picklist()

		# this helps if the current input was already selected from the
		# list but still is the substring of another pick list item
		if self.data is not None:
			return

		if not self._has_focus:
			return

		if len(self.__current_matches) == 0:
			return

		# if only one match and text == match
		if len(self.__current_matches) == 1:
			if self.__current_matches[0]['label'] == self.input2match:
				self.data = self.__current_matches[0]['data']
				return

		# recalculate size
		rows = len(self.__current_matches)
		if rows < 2:				# 2 rows minimum
			rows = 2
		if rows > 20:				# 20 rows maximum
			rows = 20
		dropdown_size = self.__picklist_dropdown.GetSize()
		pw_size = self.GetSize()
		dropdown_size.SetWidth(pw_size.width)
		dropdown_size.SetHeight((pw_size.height * rows) + 4)	# adjust for border width

		# recalculate position
		(pw_x_abs, pw_y_abs) = self.ClientToScreenXY(0,0)
		new_x = pw_x_abs
		new_y = pw_y_abs + pw_size.height
		# reaches beyond screen ?
		if (dropdown_size.height + new_y) > self._screenheight:
			max_height = self._screenheight - new_y - 4
			if max_height > ((pw_size.height * 2) + 4):
				dropdown_size.SetHeight(max_height)

		# now set dimensions
		self.__picklist_dropdown.SetSize(dropdown_size)
		self._picklist.SetSize(self.__picklist_dropdown.GetClientSize())
		self.__picklist_dropdown.MoveXY(new_x, new_y)

		# select first value
		self._picklist.Select(0)

		# and show it
		self.__picklist_dropdown.Show(True)
	#--------------------------------------------------------
	def _hide_picklist(self):
		"""Hide the pick list."""
		if self.__picklist_dropdown.IsShown():
			self.__picklist_dropdown.Hide()		# dismiss the dropdown list window
	#--------------------------------------------------------
	def __select_picklist_row(self, new_row_idx=None, old_row_idx=None):
		if old_row_idx is not None:
			pass			# FIXME: do we need unselect here ? Select() should do it for us
		self._picklist.Select(new_row_idx)
		self._picklist.EnsureVisible(new_row_idx)
	#---------------------------------------------------------
	def __update_matches_in_picklist(self, val=None):
		"""Get the matches for the currently typed input fragment."""

		self.input2match = val
		if self.input2match is None:
			# get current(ly relevant part of) input
			if self.__phrase_separators is not None:
				entire_input = self.GetValue()
				cursor_pos = self.GetInsertionPoint()
				left_of_cursor = entire_input[:cursor_pos]
				right_of_cursor = entire_input[cursor_pos:]
				left_boundary = self.__phrase_separators.search(left_of_cursor)
				if left_boundary is not None:
					phrase_start = left_boundary.end()
				else:
					phrase_start = 0
				self.left_part = entire_input[:phrase_start]
				# find next phrase separator after cursor position
				right_boundary = self.__phrase_separators.search(right_of_cursor)
				if right_boundary is not None:
					phrase_end = cursor_pos + (right_boundary.start() - 1)
				else:
					phrase_end = len(entire_input) - 1
				self.right_part = entire_input[phrase_end+1:]
				self.input2match = entire_input[phrase_start:phrase_end+1]
			else:
				self.input2match = self.GetValue().strip()

		# get all currently matching items
		if self.matcher is not None:
			matched, self.__current_matches = self.matcher.getMatches(self.input2match)
			self._picklist.SetItems(self.__current_matches)

		# no matches found: might simply be due to a typo, so spellcheck
		if len(self.__current_matches) == 0:
			if self.speller is not None:
				# filter out the last word
				word = regex.split(self.__speller_word_separators, self.input2match)[-1]
				if not self.speller.check(word):
					spells = self.speller.suggest(word)
					truncated_input2match = self.input2match[:self.input2match.rindex(word)]
					for spell in spells:
						self.__current_matches.append({'label': truncated_input2match + spell, 'data': None})
					self._picklist.SetItems(self.__current_matches)

	#--------------------------------------------------------
	# internal helpers: GUI
	#--------------------------------------------------------
	def _picklist_selection2display_string(self):
		return self._picklist.GetItemText(self._picklist.GetFirstSelected())
	#--------------------------------------------------------
	def _on_enter(self):
		"""Called when the user pressed <ENTER>."""
		if self.__picklist_dropdown.IsShown():
			self._on_list_item_selected()
		else:
			# FIXME: check for errors before navigation
			self.Navigate()
	#--------------------------------------------------------
	def __on_cursor_down(self):

		if self.__picklist_dropdown.IsShown():
			selected = self._picklist.GetFirstSelected()
			if selected < (len(self.__current_matches) - 1):
				self.__select_picklist_row(selected+1, selected)

		# if we don't yet have a pick list: open new pick list
		# (this can happen when we TAB into a field pre-filled
		# with the top-weighted contextual data but want to
		# select another contextual item)
		else:
			self.__timer.Stop()
			if self.GetValue().strip() == '':
				self.__update_matches_in_picklist(val='*')
			else:
				self.__update_matches_in_picklist()
			self._show_picklist()
	#--------------------------------------------------------
	def __on_cursor_up(self):
		if self.__picklist_dropdown.IsShown():
			selected = self._picklist.GetFirstSelected()
			if selected > 0:
				self.__select_picklist_row(selected-1, selected)
		else:
			# FIXME: input history ?
			pass
	#--------------------------------------------------------
	def __on_tab(self):
		if self.__picklist_dropdown.IsShown():
			if len(self.__current_matches) == 1:
				self.__select_picklist_row(new_row_idx=0)
				self._on_list_item_selected()
				return True
		return False
	#--------------------------------------------------------
	# internal helpers: logic
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
	#------------
	def _get_accepted_chars(self):
		if self.__accepted_chars is None:
			return None
		return self.__accepted_chars.pattern
	#------------
	accepted_chars = property(_get_accepted_chars, _set_accepted_chars)
	#--------------------------------------------------------
	def _set_final_regex(self, final_regex='.*'):
		self.__final_regex = regex.compile(final_regex)
	#------------
	def _get_final_regex(self):
		return self.__final_regex.pattern
	#------------
	final_regex = property(_get_final_regex, _set_final_regex)
	#--------------------------------------------------------
	def _set_phrase_separators(self, phrase_separators):
		if phrase_separators is None:
			self.__phrase_separators = None
		else:
			self.__phrase_separators = regex.compile(phrase_separators)
	#------------
	def _get_phrase_separators(self):
		if self.__phrase_separators is None:
			return None
		return self.__phrase_separators.pattern
	#------------
	phrase_separators = property(_get_phrase_separators, _set_phrase_separators)
	#--------------------------------------------------------
	def _set_speller_word_separators(self, word_separators):
		if word_separators is None:
			self.__speller_word_separators = regex.compile('[\W\d_]+')
		else:
			self.__speller_word_separators = regex.compile(word_separators)
	#------------
	def _get_speller_word_separators(self):
		return self.__speller_word_separators.pattern
	#------------
	speller_word_separators = property(_get_speller_word_separators, _set_speller_word_separators)
	#--------------------------------------------------------
	def _on_timer_fired(self, cookie):
		"""Callback for delayed match retrieval timer.

		if we end up here:
		 - delay has passed without user input
		 - the value in the input field has not changed since the timer started
		"""
		# update matches according to current input
		self.__update_matches_in_picklist()

		# we now have either:
		# - all possible items (within reasonable limits) if input was '*'
		# - all matching items
		# - an empty match list if no matches were found
		# also, our picklist is refilled and sorted according to weight

		wx.CallAfter(self._show_picklist)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		wx.EVT_TEXT(self, self.GetId(), self._on_text_update)
		wx.EVT_KEY_DOWN (self, self._on_key_down)
		wx.EVT_SET_FOCUS(self, self._on_set_focus)
		wx.EVT_KILL_FOCUS(self, self._on_lose_focus)
		self._picklist.Bind(wx.EVT_LEFT_DCLICK, self._on_list_item_selected)
	#--------------------------------------------------------
	def _on_list_item_selected(self, *args, **kwargs):
		"""Gets called when user selected a list item."""

		self._hide_picklist()
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		self.data = self._picklist.GetSelectedItemData()	# just so that _picklist_selection2display_string could use it

		# update our display
		self.suppress_text_update_smarts = True
		if self.__phrase_separators is not None:
			wx.TextCtrl.SetValue(self, u'%s%s%s' % (self.left_part, self._picklist_selection2display_string(), self.right_part))
		else:
			wx.TextCtrl.SetValue(self, self._picklist_selection2display_string())

		self.data = self._picklist.GetSelectedItemData()
		self.MarkDirty()

		# and tell the listeners about the user's selection
		for callback in self._on_selection_callbacks:
			callback(self.data)

		if self.navigate_after_selection:
			self.Navigate()
		else:
			self.SetInsertionPoint(self.GetLastPosition())

		return
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
			tab_handled = self.__on_tab()
			if not tab_handled:
				self.Navigate(flags = wx.NavigationKeyEvent.IsForward)
			return

		# FIXME: need PAGE UP/DOWN//POS1/END here to move in picklist
		if keycode in [wx.WXK_SHIFT, wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT]:
			pass

		# need to handle all non-character key presses *before* this check
		elif not self.__char_is_allowed(char = unichr(event.GetUnicodeKey())):
			# FIXME: configure ?
			wx.Bell()
			# FIXME: display error message ?  Richard doesn't ...
			return

		event.Skip()
		return
	#--------------------------------------------------------
	def _on_text_update (self, event):
		"""Internal handler for wx.EVT_TEXT.

		Called when text was changed by user or SetValue().
		"""
		if self.suppress_text_update_smarts:
			self.suppress_text_update_smarts = False
			return

		self.data = None
		self.__current_matches = []

		# if empty string then kill list dropdown window
		# we also don't need a timer event then
		val = self.GetValue().strip()
		ins_point = self.GetInsertionPoint()
		if val == u'':
			self._hide_picklist()
			self.__timer.Stop()
		else:
			new_val = gmTools.capitalize(text = val, mode = self.capitalisation_mode)
			if new_val != val:
				self.suppress_text_update_smarts = True
				wx.TextCtrl.SetValue(self, new_val)
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
	def _on_set_focus(self, event):

		self._has_focus = True
		event.Skip()

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
		self._has_focus = False

		# don't need timer and pick list anymore
		self.__timer.Stop()
		self._hide_picklist()

		# unset selection
		self.SetSelection(1,1)

		# the user may have typed a phrase that is an exact match,
		# however, just typing it won't associate data from the
		# picklist, so do that now
		if self.data is None:
			val = self.GetValue().strip()
			if val != u'':
				self.__update_matches_in_picklist()
				for match in self.__current_matches:
					if match['label'] == val:
						self.data = match['data']
						self.MarkDirty()
						self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
						break

		# no exact match found
		if self.data is None:
			if self.selection_only:
				gmDispatcher.send(signal='statustext', msg=self.selection_only_error_msg)
				self.SetBackgroundColour('pink')

		# check value against final_regex if any given
		if not self.__final_regex.match(self.GetValue().strip()):
			gmDispatcher.send(signal='statustext', msg=self.final_regex_error_msg % self.__final_regex.pattern)
			self.SetBackgroundColour('pink')

		# notify interested parties
		for callback in self._on_lose_focus_callbacks:
			callback()

		event.Skip()
		return True
#--------------------------------------------------------
# MAIN
#--------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	from Gnumed.pycommon import gmPG2, gmMatchProvider

	prw = None
	#--------------------------------------------------------
	def display_values_set_focus(*args, **kwargs):
		print "got focus:"
		print "value:", prw.GetValue()
		print "data :", prw.GetData()
		return True
	#--------------------------------------------------------
	def display_values_lose_focus(*args, **kwargs):
		print "lost focus:"
		print "value:", prw.GetValue()
		print "data :", prw.GetData()
		return True
	#--------------------------------------------------------
	def display_values_modified(*args, **kwargs):
		print "modified:"
		print "value:", prw.GetValue()
		print "data :", prw.GetData()
		return True
	#--------------------------------------------------------
	def display_values_selected(*args, **kwargs):
		print "selected:"
		print "value:", prw.GetValue()
		print "data :", prw.GetData()
		return True
	#--------------------------------------------------------
	def test_prw_fixed_list():
		app = wx.PyWidgetTester(size = (200, 50))

		items = [	{'data':1, 'label':"Bloggs"},
					{'data':2, 'label':"Baker"},
					{'data':3, 'label':"Jones"},
					{'data':4, 'label':"Judson"},
					{'data':5, 'label':"Jacobs"},
					{'data':6, 'label':"Judson-Jacobs"}
				]

		mp = gmMatchProvider.cMatchProvider_FixedList(items)
		# do NOT treat "-" as a word separator here as there are names like "asa-sismussen"
		mp.setWordSeparators(separators = '[ \t=+&:@]+')
		global prw
		prw = cPhraseWheel(parent = app.frame, id = -1)
		prw.matcher = mp
		prw.capitalisation_mode = gmTools.CAPS_NAMES
		prw.add_callback_on_set_focus(callback=display_values_set_focus)
		prw.add_callback_on_modified(callback=display_values_modified)
		prw.add_callback_on_lose_focus(callback=display_values_lose_focus)
		prw.add_callback_on_selection(callback=display_values_selected)

		app.frame.Show(True)
		app.MainLoop()

		return True
	#--------------------------------------------------------
	def test_prw_sql2():
		print "Do you want to test the database connected phrase wheel ?"
		yes_no = raw_input('y/n: ')
		if yes_no != 'y':
			return True

		gmPG2.get_connection()
		# FIXME: add callbacks
		# FIXME: add context
		query = u'select code, name from dem.country where _(name) %(fragment_condition)s'
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
		app = wx.PyWidgetTester(size = (200, 50))
		global prw
		prw = cPhraseWheel(parent = app.frame, id = -1)
		prw.matcher = mp

		app.frame.Show(True)
		app.MainLoop()

		return True
	#--------------------------------------------------------
	def test_prw_patients():
		gmPG2.get_connection()
		query = u"select pk_identity, firstnames || ' ' || lastnames || ' ' || dob::text as pat_name from dem.v_basic_person where firstnames || lastnames %(fragment_condition)s"

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
		app = wx.PyWidgetTester(size = (200, 50))
		global prw
		prw = cPhraseWheel(parent = app.frame, id = -1)
		prw.matcher = mp

		app.frame.Show(True)
		app.MainLoop()

		return True
	#--------------------------------------------------------
	def test_spell_checking_prw():
		app = wx.PyWidgetTester(size = (200, 50))

		global prw
		prw = cPhraseWheel(parent = app.frame, id = -1)

		prw.add_callback_on_set_focus(callback=display_values_set_focus)
		prw.add_callback_on_modified(callback=display_values_modified)
		prw.add_callback_on_lose_focus(callback=display_values_lose_focus)
		prw.add_callback_on_selection(callback=display_values_selected)

		prw.enable_default_spellchecker()

		app.frame.Show(True)
		app.MainLoop()

		return True
	#--------------------------------------------------------
#	test_prw_fixed_list()
#	test_prw_sql2()
	test_spell_checking_prw()
#	test_prw_patients()

#==================================================
# $Log: gmPhraseWheel.py,v $
# Revision 1.109  2007-09-02 20:56:30  ncq
# - cleanup
#
# Revision 1.108  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.107  2007/07/10 20:27:27  ncq
# - install_domain() arg consolidation
#
# Revision 1.106  2007/07/03 16:03:04  ncq
# - cleanup
# - compile final_regex_error_msg just before using it
#   since self.final_regex can have changed
#
# Revision 1.105  2007/05/14 14:43:11  ncq
# - allow TAB to select item from picklist if only one match available
#
# Revision 1.104  2007/05/14 13:11:25  ncq
# - use statustext() signal
#
# Revision 1.103  2007/04/19 13:14:30  ncq
# - don't fail input if enchant/aspell installed but no dict available ...
#
# Revision 1.102  2007/04/02 15:16:55  ncq
# - make spell checker act on last word of phrase only
# - to that end add property speller_word_separators, a
#   regex which defaults to standard word boundaries + digits + _
#
# Revision 1.101  2007/04/02 14:31:35  ncq
# - cleanup
#
# Revision 1.100  2007/04/01 16:33:47  ncq
# - try another parent for the MacOSX popup window
#
# Revision 1.99  2007/03/31 20:09:06  ncq
# - make enchant optional
#
# Revision 1.98  2007/03/27 10:29:49  ncq
# - better placement for default word list
#
# Revision 1.97  2007/03/27 09:59:26  ncq
# - enable_default_spellchecker()
#
# Revision 1.96  2007/02/16 10:22:09  ncq
# - _calc_display_string -> _picklist_selection2display_string to better reflect its use
#
# Revision 1.95  2007/02/06 13:45:39  ncq
# - much improved docs
# - remove aDelay from __init__ and make it a class variable
# - thereby we can now dynamically adjust it at runtime :-)
# - add patient searcher phrasewheel example
#
# Revision 1.94  2007/02/05 12:11:17  ncq
# - put GPL into __license__
# - code and layout cleanup
# - remove dependancy on gmLog
# - cleanup __init__ interface:
# 	- remove selection_only
# 	- remove aMatchProvider
# 	- set both directly on instance members now
# - implement spell checking plus test case for it
# - implement configurable error messages
#
# Revision 1.93  2007/02/04 18:50:12  ncq
# - capitalisation_mode is now instance variable
#
# Revision 1.92  2007/02/04 16:04:03  ncq
# - reduce imports
# - add accepted_chars constants
# - enhance phrasewheel:
#   - better credits
#   - cleaner __init__ signature
#   - user properties
#   - code layout/naming cleanup
#   - no more snap_to_first_match for now
#   - add capitalisation mode
#   - add accepted chars checking
#   - add final regex matching
#   - allow suppressing recursive _on_text_update()
#   - always use time, even in slave mode
#   - lots of logic consolidation
#   - add SetText() and favour it over SetValue()
#
# Revision 1.91  2007/01/20 22:52:27  ncq
# - .KeyCode -> GetKeyCode()
#
# Revision 1.90  2007/01/18 22:07:52  ncq
# - (Get)KeyCode() -> KeyCode so 2.8 can do
#
# Revision 1.89  2007/01/06 23:44:19  ncq
# - explicitely unset selection on lose focus
#
# Revision 1.88  2006/11/28 20:51:13  ncq
# - a missing self
# - remove some prints
#
# Revision 1.87  2006/11/27 23:08:36  ncq
# - add snap_to_first_match
# - add on_modified callbacks
# - set background in lose_focus in some cases
# - improve test suite
#
# Revision 1.86  2006/11/27 12:42:31  ncq
# - somewhat improved dropdown picklist on Mac, not properly positioned yet
#
# Revision 1.85  2006/11/26 21:42:47  ncq
# - don't use wx.ScrolledWindow or we suffer double-scrollers
#
# Revision 1.84  2006/11/26 20:58:20  ncq
# - try working around lacking wx.PopupWindow
#
# Revision 1.83  2006/11/26 14:51:19  ncq
# - cleanup/improve test suite so we can get MacOSX nailed (down)
#
# Revision 1.82  2006/11/26 14:09:59  ncq
# - fix sys.path when running standalone for test suite
# - fix test suite
#
# Revision 1.81  2006/11/24 09:58:39  ncq
# - cleanup
# - make it really work when matcher is None
#
# Revision 1.80  2006/11/19 11:16:02  ncq
# - remove self._input_was_selected
#
# Revision 1.79  2006/11/06 12:54:00  ncq
# - we don't actually need self._input_was_selected thanks to self.data
#
# Revision 1.78  2006/11/05 16:10:11  ncq
# - cleanup
# - now really handle context
# - add unset_context()
# - stop timer in __init__()
# - start timer in _on_set_focus()
# - some u''-ification
#
# Revision 1.77  2006/10/25 07:24:51  ncq
# - gmPG -> gmPG2
# - match provider _SQL deprecated
#
# Revision 1.76  2006/07/19 20:29:50  ncq
# - import cleanup
#
# Revision 1.75  2006/07/04 14:15:17  ncq
# - lots of cleanup
# - make dropdown list scroll !  :-)
# - add customized list control
# - don't make dropdown go below screen height
#
# Revision 1.74  2006/07/01 15:14:26  ncq
# - lots of cleanup
# - simple border around list dropdown
# - remove on_resize handling
# - remove setdependant()
# - handle down-arrow to drop down list
#
# Revision 1.73  2006/07/01 13:14:50  ncq
# - cleanup as gleaned from TextCtrlAutoComplete
#
# Revision 1.72  2006/06/28 22:16:08  ncq
# - add SetData() -- which only works if data can be found in the match space
#
# Revision 1.71  2006/06/18 13:47:29  ncq
# - set self.input_was_selected=True if SetValue() does have data with it
#
# Revision 1.70  2006/06/05 21:36:40  ncq
# - cleanup
#
# Revision 1.69  2006/06/02 09:59:03  ncq
# - must invalidate associated data object *as soon as*
#   the text in the control changes
#
# Revision 1.68  2006/05/31 10:28:27  ncq
# - cleanup
# - deprecation warning for <id_callback> argument
#
# Revision 1.67  2006/05/25 22:24:20  ncq
# - self.__input_was_selected -> self._input_was_selected
#   because subclasses need access to it
#
# Revision 1.66  2006/05/24 09:47:34  ncq
# - remove superfluous self._is_modified, use MarkDirty() instead
# - cleanup SetValue()
# - client data in picklist better be object, not string
# - add _calc_display_string() for better reuse in subclasses
# - fix "pick list windows too small if one match" at the cost of extra
#   empty row when no horizontal scrollbar needed ...
#
# Revision 1.65  2006/05/20 18:54:15  ncq
# - cleanup
#
# Revision 1.64  2006/05/01 18:49:49  ncq
# - add_callback_on_set_focus()
#
# Revision 1.63  2005/10/09 08:15:21  ihaywood
# SetValue () has optional second parameter to set data.
#
# Revision 1.62  2005/10/09 02:19:40  ihaywood
# the address widget now has the appropriate widget order and behaviour for australia
# when os.environ["LANG"] == 'en_AU' (is their a more graceful way of doing this?)
#
# Remember our postcodes work very differently.
#
# Revision 1.61  2005/10/04 00:04:45  sjtan
# convert to wx.; catch some transitional errors temporarily
#
# Revision 1.60  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.59  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.58  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.57  2005/08/14 15:37:36  ncq
# - cleanup
#
# Revision 1.56  2005/07/24 11:35:59  ncq
# - use robustified gmTimer.Start() interface
#
# Revision 1.55  2005/07/23 21:55:40  shilbert
# *** empty log message ***
#
# Revision 1.54  2005/07/23 21:10:58  ncq
# - explicitely use milliseconds=-1 in timer.Start()
#
# Revision 1.53  2005/07/23 19:24:58  ncq
# - debug timer start() on windows
#
# Revision 1.52  2005/07/04 11:20:59  ncq
# - cleanup cruft
# - on_set_focus() set value to first match if previously empty
# - on_lose_focus() set value if selection_only and only one match and not yet selected
#
# Revision 1.51  2005/06/14 19:55:37  cfmoro
# Set selection flag when setting value
#
# Revision 1.50  2005/06/07 10:18:23  ncq
# - cleanup
# - setContext -> set_context
#
# Revision 1.49  2005/06/01 23:09:02  ncq
# - set default phrasewheel delay to 150ms
#
# Revision 1.48  2005/05/23 16:42:50  ncq
# - when we SetValue(val) we need to only check those matches
#   that actually *can* match, eg the output of getMatches(val)
#
# Revision 1.47  2005/05/22 23:09:13  cfmoro
# Adjust the underlying data when setting the phrasewheel value
#
# Revision 1.46  2005/05/17 08:06:38  ncq
# - support for callbacks on lost focus
#
# Revision 1.45  2005/05/14 15:06:48  ncq
# - GetData()
#
# Revision 1.44  2005/05/05 06:31:06  ncq
# - remove dead cWheelTimer code in favour of gmTimer.py
# - add self._on_enter_callbacks and add_callback_on_enter()
# - addCallback() -> add_callback_on_selection()
#
# Revision 1.43  2005/03/14 14:37:56  ncq
# - only disable timer if slave mode is really active
#
# Revision 1.42  2004/12/27 16:23:39  ncq
# - gmTimer callbacks take a cookie
#
# Revision 1.41  2004/12/23 16:21:21  ncq
# - some cleanup
#
# Revision 1.40  2004/10/16 22:42:12  sjtan
#
# script for unitesting; guard for unit tests where unit uses gmPhraseWheel; fixup where version of wxPython doesn't allow
# a child widget to be multiply inserted (gmDemographics) ; try block for later versions of wxWidgets that might fail
# the Add (.. w,h, ... ) because expecting Add(.. (w,h) ...)
#
# Revision 1.39  2004/09/13 09:24:30  ncq
# - don't start timers in slave_mode since cannot start from
#   other than main thread, this is a dirty fix but will do for now
#
# Revision 1.38  2004/06/25 12:30:52  ncq
# - use True/False
#
# Revision 1.37  2004/06/17 11:43:15  ihaywood
# Some minor bugfixes.
# My first experiments with wxGlade
# changed gmPhraseWheel so the match provider can be added after instantiation
# (as wxGlade can't do this itself)
#
# Revision 1.36  2004/05/02 22:53:53  ncq
# - cleanup
#
# Revision 1.35  2004/05/01 10:27:47  shilbert
# - self._picklist.Append() needs string or unicode object
#
# Revision 1.34  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.33  2004/03/02 10:21:10  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.32  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.31  2004/01/12 13:14:39  ncq
# - remove dead code
# - correctly calculate new pick list position: don't go to TOPLEVEL
#   window but rather to immediate parent ...
#
# Revision 1.30  2004/01/06 10:06:02  ncq
# - make SQL based phrase wheel test work again
#
# Revision 1.29  2003/11/19 23:42:00  ncq
# - cleanup, comment out snap()
#
# Revision 1.28  2003/11/18 23:17:47  ncq
# - cleanup, fixed variable names
#
# Revision 1.27  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.26  2003/11/09 14:28:30  ncq
# - cleanup
#
# Revision 1.25  2003/11/09 02:24:42  ncq
# - added Syans "input was selected from list" state flag to avoid unnecessary list
#   drop downs
# - variable name cleanup
#
# Revision 1.24  2003/11/07 20:48:04  ncq
# - place comments where they belong
#
# Revision 1.23  2003/11/05 22:21:06  sjtan
#
# let's gmDateInput specify id_callback in constructor list.
#
# Revision 1.22  2003/11/04 10:35:23  ihaywood
# match providers in gmDemographicRecord
#
# Revision 1.21  2003/11/04 01:40:27  ihaywood
# match providers moved to python-common
#
# Revision 1.20  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.19  2003/10/09 15:45:16  ncq
# - validate cookie column in score tables, too
#
# Revision 1.18  2003/10/07 22:20:50  ncq
# - ported Syan's extra_sql_condition extension
# - make SQL match provider aware of separate scoring tables
#
# Revision 1.17  2003/10/03 00:20:25  ncq
# - handle case where matches = 1 and match = input -> don't show picklist
#
# Revision 1.16  2003/10/02 20:51:12  ncq
# - add alt-XX shortcuts, move __* to _*
#
# Revision 1.15  2003/09/30 18:52:40  ncq
# - factored out date input wheel
#
# Revision 1.14  2003/09/29 23:11:58  ncq
# - add __explicit_offset() date expander
#
# Revision 1.13  2003/09/29 00:16:55  ncq
# - added date match provider
#
# Revision 1.12  2003/09/21 10:55:04  ncq
# - coalesce merge conflicts due to optional SQL phrase wheel testing
#
# Revision 1.11  2003/09/21 07:52:57  ihaywood
# those bloody umlauts killed by python interpreter!
#
# Revision 1.10  2003/09/17 05:54:32  ihaywood
# phrasewheel box size now approximate to length of search results
#
# Revision 1.8  2003/09/16 22:25:45  ncq
# - cleanup
# - added first draft of single-column-per-table SQL match provider
# - added module test for SQL matcher
#
# Revision 1.7  2003/09/15 16:05:30  ncq
# - allow several phrases to be typed in and only try to match
#   the one the cursor is in at the moment
#
# Revision 1.6  2003/09/13 17:46:29  ncq
# - pattern match word separators
# - pattern match ignore characters as per Richard's suggestion
# - start work on phrase separator pattern matching with extraction of
#   relevant input part (where the cursor is at currently)
#
# Revision 1.5  2003/09/10 01:50:25  ncq
# - cleanup
#
#
#==================================================

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
#	#self.__prevFragment = "XXXXXXXXXXXXXXXXXX-very-unlikely--------------XXXXXXXXXXXXXXX"
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

# maybe store fixed list matches as balanced tree if otherwise to slow
#-----
#> > remember, you should be searching on  either weighted data, or in some
#> > situations a start string search on indexed data
#>
#> Can you be a bit more specific on this ?

#seaching ones own previous text entered  would usually be instring but
#weighted (ie the phrases you use the most auto filter to the top)

#Searching a drug database for a   drug brand name is usually more
#functional if it does a start string search, not an instring search which is
#much slower and usually unecesary.  There are many other examples but trust
#me one needs both
#-----
