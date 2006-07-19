"""GNUmed phrasewheel.

A class, extending wx.TextCtrl, which has a drop-down pick list,
automatically filled based on the inital letters typed. Based on the
interface of Richard Terry's Visual Basic client

This is based on seminal work by Ian Haywood <ihaywood@gnu.org>
"""
#@copyright: GPL

############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPhraseWheel.py,v $
# $Id: gmPhraseWheel.py,v 1.76 2006-07-19 20:29:50 ncq Exp $
__version__ = "$Revision: 1.76 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood, S.J.Tan <sjtan@bigpond.com>"

import string, types, time, sys, re

import wxversion
import wx
import wx.lib.mixins.listctrl as listmixins

from Gnumed.wxpython import gmTimer, gmGuiHelpers
from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmMatchProvider, gmGuiBroker, gmNull

_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lInfo, __version__)

#============================================================
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
#============================================================
class cPhraseWheel (wx.TextCtrl):
	"""Widget for smart guessing of user fields, after Richard Terry's interface."""

	default_phrase_separators = re.compile('[;/|]+')

	def __init__ (
		self, parent=None, id=-1, value='',
		aMatchProvider = None,
		aDelay = 150,
		selection_only = False,
		*args,
		**kwargs):

		self.__matcher = aMatchProvider
		self.__real_matcher = None
		self.__currMatches = []
		self._input_was_selected = False

		self.phrase_separators = cPhraseWheel.default_phrase_separators
		self.allow_multiple_phrases()

		self.input2match = ''
		self.left_part = ''
		self.right_part = ''
		self.data = None
		
		self.selection_only = selection_only
		self._has_focus = False
		self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

		self._on_selection_callbacks = []
		self._on_lose_focus_callbacks = []
		self._on_set_focus_callbacks = []
		self.notified_listeners = False

		wx.TextCtrl.__init__ (self, parent, id, **kwargs)

		# multiple matches dropdown list
		self.__dropdown = wx.PopupWindow(parent)

		# FIXME: support optional headers
#		if kwargs['show_list_headers']:
#			flags = 0
#		else:
#			flags = wx.LC_NO_HEADER
		self._picklist = cPhraseWheelListCtrl (
			self.__dropdown,
			style = wx.LC_NO_HEADER
		)
		self._picklist.InsertColumn(0, '')

		self.__dropdown.Hide()

		# set event handlers
		self.__register_events()

		self.__gb = gmGuiBroker.GuiBroker()
		if self.__gb.has_key('main.slave_mode') and self.__gb['main.slave_mode']:
			_log.Log(gmLog.lWarn, 'disabling gmTimer in slave mode')
			self.__timer = gmNull.cNull()
		else:
			self.__timer = gmTimer.cTimer (
				callback = self._on_timer_fired,
				delay = aDelay
			)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def allow_multiple_phrases(self, state = True):
		self.__handle_multiple_phrases = state
	#--------------------------------------------------------
	def setMatchProvider (self, mp):
		self.__matcher = mp
		self.__real_matcher = None
	#--------------------------------------------------------
	def add_callback_on_selection(self, callback=None):
		"""Add a callback for a listener.

		The callback will be invoked whenever an item is selected
		from the picklist. The associated data is passed in as
		a single parameter. Callbacks must be able to cope with
		None as the data parameter as that is sent whenever the
		user changes a previously selected value.
		"""
		if not callable(callback):
			_log.Log(gmLog.lWarn, 'ignoring callback [%s], it is not callable' % callback)
			return False
		self._on_selection_callbacks.append(callback)
	#---------------------------------------------------------
	def add_callback_on_set_focus(self, callback=None):
		if not callable(callback):
			_log.Log(gmLog.lWarn, 'ignoring callback [%s] - not callable' % callback)
			return False
		self._on_set_focus_callbacks.append(callback)
	#---------------------------------------------------------
	def add_callback_on_lose_focus(self, callback=None):
		if not callable(callback):
			_log.Log(gmLog.lWarn, 'ignoring callback [%s] - not callable' % callback)
			return False
		self._on_lose_focus_callbacks.append(callback)
	#---------------------------------------------------------
	def SetData(self, data=None):
		"""Set the data and thereby set the value, too.

		If you call SetData() when self.selection_only is
		false you better be prepared doing a scan of the
		entire potential match space.

		The whole thing will only work if data is found
		in the match space anyways.
		"""
		matched, matches = self.__matcher.getMatches('*')
		if not matched and self.selection_only:
			return False
		if len(matches) == 0:
			return False
		for match in matches:
			if match['data'] == data:
				self.SetValue(value = match['label'], data = data)
				return True
		return False
	#---------------------------------------------------------
	def GetData (self):
		"""
		Retrieve the data associated with the displayed string.
		"""
		return self.data
	#---------------------------------------------------------
	def SetValue (self, value, data=None):

		wx.TextCtrl.SetValue(self, value)
		self._input_was_selected = False

		# set data item if available
		if data is not None:
			self.data = data
			self._input_was_selected = True
			return True

		# or try to find one from matches
		stat, matches = self.__matcher.getMatches(aFragment = value)
		for match in matches:
			if match['label'] == value:
				self.data = match['data']
				self._input_was_selected = True
				return True

		# not found
		self.data = None
		if self.selection_only:
			return False
		return True
	#--------------------------------------------------------
	def set_context (self, context, val):
		if self.__real_matcher:
			# forget any caching, as it's now invalid
			self.__matcher = self.__real_matcher
			self.__real_matcher = None
		if self.__matcher:
			self.__matcher.set_context (context, val)
		else:
			_log.Log(gmLog.lErr, "aMatchProvider must be set to set context")
	#---------------------------------------------------------
	def _updateMatches(self, val=None):
		"""Get the matches for the currently typed input fragment."""

		if val is None:
			# get current(ly relevant part of) input
			if self.__handle_multiple_phrases:
				entire_input = self.GetValue()
				cursor_pos = self.GetInsertionPoint()
				left_of_cursor = entire_input[:cursor_pos]
				right_of_cursor = entire_input[cursor_pos:]
				left_boundary = self.phrase_separators.search(left_of_cursor)
				if left_boundary is not None:
					phrase_start = left_boundary.end()
				else:
					phrase_start = 0
				self.left_part = entire_input[:phrase_start]
				# find next phrase separator after cursor position
				right_boundary = self.phrase_separators.search(right_of_cursor)
				if right_boundary is not None:
					phrase_end = cursor_pos + (right_boundary.start() - 1)
				else:
					phrase_end = len(entire_input) - 1
				self.right_part = entire_input[phrase_end+1:]
				self.input2match = entire_input[phrase_start:phrase_end+1]
			else:
				self.input2match = self.GetValue()
		else:
			# find matches for given value
			self.input2match = val

		# get all currently matching items
		if self.__matcher:
			matched, self.__currMatches = self.__matcher.getMatches(self.input2match)
			self._picklist.SetItems(self.__currMatches)
		else:
			_log.Log(gmLog.lWarn, "using phrasewheel without match provider")
	#--------------------------------------------------------
	def _show_dropdown(self):
		"""Display the pick list."""

		self._hide_dropdown()

		# this helps if the current input was already selected from the
		# list but still is the substring of another pick list item
		if self._input_was_selected:
			return 1

		if not self._has_focus:
			return 1

		if len(self.__currMatches) == 0:
			return 1

		# if only one match and text == match
		if len(self.__currMatches) == 1:
			if self.__currMatches[0]['label'] == self.input2match:
				self._input_was_selected = 1
				self.data = self.__currMatches[0]['data']
				return 1

		# recalculate size
		rows = len(self.__currMatches)
		if rows < 2:
			rows = 2
		if rows > 20:
			rows = 20
		dropdown_size = self.__dropdown.GetSize()
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
		self.__dropdown.SetSize(dropdown_size)
		self._picklist.SetSize(self.__dropdown.GetClientSize())
		self.__dropdown.MoveXY(new_x, new_y)

		# select first value
		self._picklist.Select(0)

		# and show it
		self.__dropdown.Show(True)
	#--------------------------------------------------------
	def _hide_dropdown(self):
		"""Hide the pick list."""
		if self.__dropdown.IsShown():
			self.__dropdown.Hide()		# dismiss the dropdown list window
	#--------------------------------------------------------
	def _calc_display_string(self):
		return self._picklist.GetItemText(self._picklist.GetFirstSelected())
	#--------------------------------------------------------
	# specific event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, *args, **kwargs):
		"""Gets called when user selected a list item."""
		self._hide_dropdown()

		# update our display
		if self.__handle_multiple_phrases:
			wx.TextCtrl.SetValue (self, '%s%s%s' % (self.left_part, self._calc_display_string(), self.right_part))
		else:
			wx.TextCtrl.SetValue (self, self._calc_display_string())
		self.Navigate()
		self.MarkDirty()

		self.data = self._picklist.GetSelectedItemData()
		self._input_was_selected = True

		# and tell the listeners about the user's selection
		for call_listener in self._on_selection_callbacks:
			call_listener(self.data)
		self.notified_listeners = True
	#--------------------------------------------------------
	# individual key handlers
	#--------------------------------------------------------
	def _on_enter(self):
		"""Called when the user pressed <ENTER>."""
		if self.__dropdown.IsShown():
			self._on_list_item_selected()
		else:
			self.Navigate()
	#--------------------------------------------------------
	def __on_cursor_down(self):

		if self.__dropdown.IsShown():
			selected = self._picklist.GetFirstSelected()
			if selected < (len(self.__currMatches) - 1):
				self._picklist.Select(selected+1)
				self._picklist.EnsureVisible(selected+1)

		# if we don't yet have a pick list
		# - open new pick list
		# (this can happen when we TAB into a field pre-filled
		#  with the top-weighted contextual data but want to
		#  select another contextual item)
		else:
			self.__timer.Stop()
			if self.GetValue().strip() == '':
				self._updateMatches(val='*')
			else:
				self._updateMatches()
			self._show_dropdown()
	#--------------------------------------------------------
	def __on_cursor_up(self):
		if self.__dropdown.IsShown():
			selected = self._picklist.GetFirstSelected()
			if selected > 0:
				self._picklist.Select(selected-1)
				self._picklist.EnsureVisible(selected-1)
		else:
			# FIXME: input history ?
			pass
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
	# event handlers
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

		# user pressed <ENTER>
		if keycode == wx.WXK_RETURN:
			self._on_enter()
			return

		# FIXME: need PAGE UP/DOWN//POS1/END here
		event.Skip()
		return
	#--------------------------------------------------------
	def _on_text_update (self, event):
		"""Internal handler for wx.EVT_TEXT (called when text has changed)"""

		self._input_was_selected = False
		self.data = None

		# if empty string then kill list dropdown window
		# we also don't need a timer event then
		if self.GetValue().strip() == 0:
			self._hide_dropdown()
			self.__timer.Stop()
		else:
			# start timer for delayed match retrieval
			# milliseconds needed for Windows bug
			self.__timer.Start(oneShot = True)

		if self.notified_listeners:
			# Aargh! we told the listeners that we selected <foo>
			# but now the user is typing again !
			for notify_listener in self._on_selection_callbacks:
				notify_listener(None)
			self.notified_listeners = False
	#--------------------------------------------------------
	def _on_timer_fired(self, cookie):
		"""Callback for delayed match retrieval timer.

		if we end up here:
		 - delay has passed without user input
		 - the value in the input field has not changed since the timer started
		"""
		# update matches according to current input
		self._updateMatches()

		# we now have either:
		# - all possible items (within reasonable limits) if input was '*'
		# - all matching items
		# - an empty match list if no matches were found
		# also, our picklist is refilled and sorted according to weight

		wx.CallAfter(self._show_dropdown)
	#--------------------------------------------------------
	def _on_set_focus(self, event):

		self._has_focus = True
		event.Skip()

		# notify interested parties
		for callback in self._on_set_focus_callbacks:
			try:
				if not callback():
					print "[%s:_on_set_focus]: %s returned False" % (self.__class__.__name__, str(callback))
			except:
				_log.LogException("[%s:_on_set_focus]: error calling %s" % (self.__class__.__name__, str(callback)), sys.exc_info())

		# if empty set to first "match"
		if self.GetValue().strip() == '':
			# programmers better make sure the turnaround time is limited
			self._updateMatches()
			if len(self.__currMatches) > 0:
				wx.TextCtrl.SetValue(self, self.__currMatches[0]['label'])
				self.data = self.__currMatches[0]['data']
				self._input_was_selected = True
				self.MarkDirty()

		return True
	#--------------------------------------------------------
	def _on_lose_focus(self, event):

		self._has_focus = False
		event.Skip()

		# don't need timer and pick list anymore
		self.__timer.Stop()
		self._hide_dropdown()

		# can/must we auto-set the value from the match list ?
		if (self.selection_only) and (not self._input_was_selected) and (self.GetValue().strip() != ''):
			self._updateMatches()
			no_matches = len(self.__currMatches)
			if no_matches == 1:
				wx.TextCtrl.SetValue(self, self.__currMatches[0]['label'])
				self.data = self.__currMatches[0]['data']
				self._input_was_selected = True
				self.MarkDirty()
			elif no_matches > 1:
				gmGuiHelpers.gm_beep_statustext(_('Cannot auto-select from list. There are several matches for the input.'))
				return True
			else:
				gmGuiHelpers.gm_beep_statustext(_('There are no matches for this input.'))
				self.Clear()
				return True

		# notify interested parties
		for callback in self._on_lose_focus_callbacks:
			try:
				if not callback():
					print "[%s:_on_lose_focus]: %s returned False" % (self.__class__.__name__, str(callback))
			except:
				_log.LogException("[%s:_on_lose_focus]: error calling %s" % (self.__class__.__name__, str(callback)), sys.exc_info())
		return True
#--------------------------------------------------------
# MAIN
#--------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmI18N
	#----------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wx.App):
		def OnInit (self):

			frame = wx.Frame (
				None,
				-4,
				"phrase wheel test for GNUmed",
				size=wx.Size(300, 350),
				style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE
			)

			items = [	{'data':1, 'label':"Bloggs", 	'weight':5},
						{'data':2, 'label':"Baker",  	'weight':4},
						{'data':3, 'label':"Jones",  	'weight':3},
						{'data':4, 'label':"Judson", 	'weight':2},
						{'data':5, 'label':"Jacobs", 	'weight':1},
						{'data':6, 'label':"Judson-Jacobs",'weight':5}
					]
			mp1 = gmMatchProvider.cMatchProvider_FixedList(items)
			# do NOT treat "-" as a word separator here as there are names like "asa-sismussen"
			mp1.setWordSeparators(separators = '[ \t=+&:@]+')
			ww1 = cPhraseWheel(
				parent = frame,
				id = -1,
#				pos = (50, 50),
#				size = (180, 30),
				aMatchProvider = mp1
			)

			print "Do you want to test the database connected phrase wheel ?"
			yes_no = raw_input('y/n: ')
			if yes_no == 'y':
				src = {
					'service': 'default',
					'table': 'gmpw_sql_test',
					'column': 'phrase',
					'limit': 25
				}
				score = {
					'service': 'default',
					'table': 'score_gmpw_sql_test',
					'column': 'fk_gmpw_sql_test'
				}
				mp2 = gmMatchProvider.cMatchProvider_SQL([src], score)
				ww2 = cPhraseWheel(
					parent = frame,
					id = -1,
					pos = (50, 250),
					size = (180, 30),
					aMatchProvider = mp2
				)

			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()

#==================================================
# $Log: gmPhraseWheel.py,v $
# Revision 1.76  2006-07-19 20:29:50  ncq
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
#- weighing by incrementing counter - if rollover, reset all counters to percentage of self.value()
#- ageing of item weight
#- async threads for match retrieval instead of timer
#  - on truncated results return item "..." -> selection forcefully retrieves all matches

#- plugin for pattern matching/validation of input

#- generators/yield()
#- OnChar() - process a char event

# split input into words and match components against known phrases
# -> accumulate weights into total item weight

# - case insensitive by default but
# - make case sensitive matching possible
#   - if no matches found revert to case _insensitive_ matching
# - maybe _sensitive_ by default + auto-revert if too few matches ?

# make special list window:
# - deletion of items
# - highlight matched parts
# - faster scrolling
# - wxEditableListBox ?

# - press down only once to get into list
# - moving between list members is too slow

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
