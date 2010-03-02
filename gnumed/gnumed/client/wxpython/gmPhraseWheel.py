"""GNUmed phrasewheel.

A class, extending wx.TextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
############################################################################
__version__ = "$Revision: 1.136 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan <sjtan@bigpond.com>"
__license__ = "GPL"

# stdlib
import string, types, time, sys, re as regex, os.path


# 3rd party
import wx
import wx.lib.mixins.listctrl as listmixins
import wx.lib.pubsub


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools


import logging
_log = logging.getLogger('macosx')


color_prw_invalid = 'pink'
color_prw_valid = None				# this is used by code outside this module

default_phrase_separators = '[;/|]+'
default_spelling_word_separators = '[\W\d_]+'

# those can be used by the <accepted_chars> phrasewheel parameter
NUMERIC = '0-9'
ALPHANUMERIC = 'a-zA-Z0-9'
EMAIL_CHARS = "a-zA-Z0-9\-_@\."
WEB_CHARS = "a-zA-Z0-9\.\-_/:"


_timers = []
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
		sel_idx = self.GetFirstSelected()
		if sel_idx == -1:
			return None
		return self.__data[sel_idx]['data']
	#--------------------------------------------------------
	def get_selected_item_label(self):
		sel_idx = self.GetFirstSelected()
		if sel_idx == -1:
			return None
		return self.__data[sel_idx]['label']
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
		self.final_regex_error_msg = _('The content is invalid. It must match the regular expression: [%%s]. <%s>') % self.__class__.__name__
		self.phrase_separators = default_phrase_separators
		self.navigate_after_selection = False
		self.speller = None
		self.speller_word_separators = default_spelling_word_separators
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
		wx.TextCtrl.__init__(self, parent, id, **kwargs)

		self.__non_edit_font = self.GetFont()
		self.__color_valid = self.GetBackgroundColour()
		global color_prw_valid
		if color_prw_valid is None:
			color_prw_valid = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)

		self.__init_dropdown(parent = parent)
		self.__register_events()
		self.__init_timer()
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
				self.display_as_valid(valid = True)
				self.suppress_text_update_smarts = True
				wx.TextCtrl.SetValue(self, match['label'])
				self.data = data
				return True

		# no match found ...
		if self.selection_only:
			return False

		self.data = data
		self.display_as_valid(valid = True)
		return True
	#---------------------------------------------------------
	def GetData(self, can_create=False, as_instance=False):
		"""Retrieve the data associated with the displayed string.
		"""
		if self.data is None:
			if can_create:
				self._create_data()

		if self.data is not None:
			if as_instance:
				return self._data2instance()

		return self.data
	#---------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		self.suppress_text_update_smarts = suppress_smarts

		if data is not None:
			self.suppress_text_update_smarts = True
			self.data = data
		wx.TextCtrl.SetValue(self, value)
		self.display_as_valid(valid = True)

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
			self.display_as_valid(valid = False)
			return False

		return True
	#--------------------------------------------------------
	def set_context(self, context=None, val=None):
		if self.matcher is not None:
			self.matcher.set_context(context=context, val=val)
	#---------------------------------------------------------
	def unset_context(self, context=None):
		if self.matcher is not None:
			self.matcher.unset_context(context=context)
	#--------------------------------------------------------
	def enable_default_spellchecker(self):
		# FIXME: use Debian's wgerman-medical as "personal" wordlist if available
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
	def display_as_valid(self, valid=None):
		if valid is True:
			self.SetBackgroundColour(self.__color_valid)
		elif valid is False:
			self.SetBackgroundColour(color_prw_invalid)
		else:
			raise ArgumentError(u'<valid> must be True or False')
		self.Refresh()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	# picklist handling
	#--------------------------------------------------------
	def __init_dropdown(self, parent = None):
		szr_dropdown = None
		try:
			#raise NotImplementedError		# for testing
			self.__dropdown_needs_relative_position = False
			self.__picklist_dropdown = wx.PopupWindow(parent)
			list_parent = self.__picklist_dropdown
			self.__use_fake_popup = False
		except NotImplementedError:
			self.__use_fake_popup = True

			# on MacOSX wx.PopupWindow is not implemented, so emulate it
			add_picklist_to_sizer = True
			szr_dropdown = wx.BoxSizer(wx.VERTICAL)

			# using wx.MiniFrame
			self.__dropdown_needs_relative_position = False
			self.__picklist_dropdown = wx.MiniFrame (
				parent = parent,
				id = -1,
				style = wx.SIMPLE_BORDER | wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_NO_TASKBAR | wx.POPUP_WINDOW
			)
			scroll_win = wx.ScrolledWindow(parent = self.__picklist_dropdown, style = wx.NO_BORDER)
			scroll_win.SetSizer(szr_dropdown)
			list_parent = scroll_win

			# using wx.Window
			#self.__dropdown_needs_relative_position = True
			#self.__picklist_dropdown = wx.ScrolledWindow(parent=parent, style = wx.RAISED_BORDER)
			#self.__picklist_dropdown.SetSizer(szr_dropdown)
			#list_parent = self.__picklist_dropdown

		self.mac_log('dropdown parent: %s' % self.__picklist_dropdown.GetParent())

		# FIXME: support optional headers
#		if kwargs['show_list_headers']:
#			flags = 0
#		else:
#			flags = wx.LC_NO_HEADER
		self._picklist = cPhraseWheelListCtrl (
			list_parent,
			style = wx.LC_NO_HEADER
		)
		self._picklist.InsertColumn(0, '')

		if szr_dropdown is not None:
			szr_dropdown.Add(self._picklist, 1, wx.EXPAND)

		self.__picklist_dropdown.Hide()
	#--------------------------------------------------------
	def _show_picklist(self):
		"""Display the pick list."""

		border_width = 4
		extra_height = 25

		self.__picklist_dropdown.Hide()

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
		self.mac_log('dropdown needs rows: %s' % rows)
		dropdown_size = self.__picklist_dropdown.GetSize()
		pw_size = self.GetSize()
		dropdown_size.SetWidth(pw_size.width)
		dropdown_size.SetHeight (
			(pw_size.height * rows)
			+ border_width
			+ extra_height
		)

		# recalculate position
		(pw_x_abs, pw_y_abs) = self.ClientToScreenXY(0,0)
		self.mac_log('phrasewheel position (on screen): x:%s-%s, y:%s-%s' % (pw_x_abs, (pw_x_abs+pw_size.width), pw_y_abs, (pw_y_abs+pw_size.height)))
		dropdown_new_x = pw_x_abs
		dropdown_new_y = pw_y_abs + pw_size.height
		self.mac_log('desired dropdown position (on screen): x:%s-%s, y:%s-%s' % (dropdown_new_x, (dropdown_new_x+dropdown_size.width), dropdown_new_y, (dropdown_new_y+dropdown_size.height)))
		self.mac_log('desired dropdown size: %s' % dropdown_size)

		# reaches beyond screen ?
		if (dropdown_new_y + dropdown_size.height) > self._screenheight:
			self.mac_log('dropdown extends offscreen (screen max y: %s)' % self._screenheight)
			max_height = self._screenheight - dropdown_new_y - 4
			self.mac_log('max dropdown height would be: %s' % max_height)
			if max_height > ((pw_size.height * 2) + 4):
				dropdown_size.SetHeight(max_height)
				self.mac_log('possible dropdown position (on screen): x:%s-%s, y:%s-%s' % (dropdown_new_x, (dropdown_new_x+dropdown_size.width), dropdown_new_y, (dropdown_new_y+dropdown_size.height)))
				self.mac_log('possible dropdown size: %s' % dropdown_size)

		# now set dimensions
		self.__picklist_dropdown.SetSize(dropdown_size)
		self._picklist.SetSize(self.__picklist_dropdown.GetClientSize())
		self.mac_log('pick list size set to: %s' % self.__picklist_dropdown.GetSize())
		if self.__dropdown_needs_relative_position:
			dropdown_new_x, dropdown_new_y = self.__picklist_dropdown.GetParent().ScreenToClientXY(dropdown_new_x, dropdown_new_y)
		self.__picklist_dropdown.MoveXY(dropdown_new_x, dropdown_new_y)

		# select first value
		self._picklist.Select(0)

		# and show it
		self.__picklist_dropdown.Show(True)

		dd_tl = self.__picklist_dropdown.ClientToScreenXY(0,0)
		dd_size = self.__picklist_dropdown.GetSize()
		dd_br = self.__picklist_dropdown.ClientToScreenXY(dd_size.width, dd_size.height)
		self.mac_log('dropdown placement now (on screen): x:%s-%s, y:%s-%s' % (dd_tl[0], dd_br[0], dd_tl[1], dd_br[1]))
	#--------------------------------------------------------
	def _hide_picklist(self):
		"""Hide the pick list."""
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
			if self.__phrase_separators is None:
				self.input2match = self.GetValue().strip()
			else:
				# get current(ly relevant part of) input
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

		# get all currently matching items
		if self.matcher is not None:
			matched, self.__current_matches = self.matcher.getMatches(self.input2match)
			self._picklist.SetItems(self.__current_matches)

		# no matches found: might simply be due to a typo, so spellcheck
		if len(self.__current_matches) == 0:
			if self.speller is not None:
				# filter out the last word
				word = regex.split(self.__speller_word_separators, self.input2match)[-1]
				if word.strip() != u'':
					success = False
					try:
						success = self.speller.check(word)
					except:
						_log.exception('had to disable enchant spell checker')
						self.speller = None
					if success:
						spells = self.speller.suggest(word)
						truncated_input2match = self.input2match[:self.input2match.rindex(word)]
						for spell in spells:
							self.__current_matches.append({'label': truncated_input2match + spell, 'data': None})
						self._picklist.SetItems(self.__current_matches)
	#--------------------------------------------------------
	def _picklist_selection2display_string(self):
		return self._picklist.GetItemText(self._picklist.GetFirstSelected())
	#--------------------------------------------------------
	# internal helpers: GUI
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
			if self.GetValue().strip() == u'':
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
		"""Under certain circumstances takes special action on TAB.

		returns:
			True: TAB was handled
			False: TAB was not handled
		"""
		if not self.__picklist_dropdown.IsShown():
			return False

		if len(self.__current_matches) != 1:
			return False

		if not self.selection_only:
			return False

		self.__select_picklist_row(new_row_idx=0)
		self._on_list_item_selected()

		return True
	#--------------------------------------------------------
	# internal helpers: logic
	#--------------------------------------------------------
	def _create_data(self):
		raise NotImplementedError('[%s]: cannot create data object' % self.__class__.__name__)
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
	def _set_final_regex(self, final_regex='.*'):
		self.__final_regex = regex.compile(final_regex, flags = regex.LOCALE | regex.UNICODE)

	def _get_final_regex(self):
		return self.__final_regex.pattern

	final_regex = property(_get_final_regex, _set_final_regex)
	#--------------------------------------------------------
	def _set_final_regex_error_msg(self, msg):
		self.__final_regex_error_msg = msg % self.final_regex

	def _get_final_regex_error_msg(self):
		return self.__final_regex_error_msg

	final_regex_error_msg = property(_get_final_regex_error_msg, _set_final_regex_error_msg)
	#--------------------------------------------------------
	def _set_phrase_separators(self, phrase_separators):
		if phrase_separators is None:
			self.__phrase_separators = None
		else:
			self.__phrase_separators = regex.compile(phrase_separators, flags = regex.LOCALE | regex.UNICODE)

	def _get_phrase_separators(self):
		if self.__phrase_separators is None:
			return None
		return self.__phrase_separators.pattern

	phrase_separators = property(_get_phrase_separators, _set_phrase_separators)
	#--------------------------------------------------------
	def _set_speller_word_separators(self, word_separators):
		if word_separators is None:
			self.__speller_word_separators = regex.compile('[\W\d_]+', flags = regex.LOCALE | regex.UNICODE)
		else:
			self.__speller_word_separators = regex.compile(word_separators, flags = regex.LOCALE | regex.UNICODE)

	def _get_speller_word_separators(self):
		return self.__speller_word_separators.pattern

	speller_word_separators = property(_get_speller_word_separators, _set_speller_word_separators)
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
		self.display_as_valid(valid = True)

		data = self._picklist.GetSelectedItemData()	# just so that _picklist_selection2display_string can use it
		if data is None:
			return

		self.data = data

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
			self.__on_tab()
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

		# if empty string then hide list dropdown window
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

		self.__non_edit_font = self.GetFont()
		edit_font = self.GetFont()
		edit_font.SetPointSize(pointSize = self.__non_edit_font.GetPointSize() + 1)
		self.SetFont(edit_font)
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
		self._has_focus = False

		# don't need timer and pick list anymore
		self.__timer.Stop()
		self._hide_picklist()

		# unset selection
		self.SetSelection(1,1)

		self.SetFont(self.__non_edit_font)
		self.Refresh()

		is_valid = True

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
						break

		# no exact match found
		if self.data is None:
			if self.selection_only:
				wx.lib.pubsub.Publisher().sendMessage (
					topic = 'statustext',
					data = {'msg': self.selection_only_error_msg}
				)
				is_valid = False

		# check value against final_regex if any given
		if self.__final_regex.match(self.GetValue().strip()) is None:
			wx.lib.pubsub.Publisher().sendMessage (
				topic = 'statustext',
				data = {'msg': self.final_regex_error_msg}
			)
			is_valid = False

		self.display_as_valid(valid = is_valid)

		# notify interested parties
		for callback in self._on_lose_focus_callbacks:
			callback()

		event.Skip()
		return True
	#----------------------------------------------------
	def mac_log(self, msg):
		if self.__use_fake_popup:
			_log.debug(msg)
#--------------------------------------------------------
# MAIN
#--------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

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
		mp.word_separators = '[ \t=+&:@]+'
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
