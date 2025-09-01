"""gmResizingWidgets - Resizing widgets for use in GNUmed.

Design by Richard Terry and Ian Haywood.
"""
#====================================================================
__author__ = "Ian Haywood, Karsten Hilbert, Richard Terry"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging, re as regex


import wx
import wx.stc


from Gnumed.pycommon import gmDispatcher
from Gnumed.business import gmKeywordExpansion
from Gnumed.wxpython import gmGuiHelpers

_log = logging.getLogger('gm.ui')
if __name__ == '__main__':
	_ = lambda x:x

STYLE_ERROR=1
STYLE_TEXT=2
STYLE_EMBED=4

#====================================================================
class cPickList(wx.ListBox):
	def __init__ (self, parent, pos, size, callback):
		wx.ListBox.__init__(self, parent, -1, pos, size, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
		self.callback = callback
		self.alive = 1 # 0=dead, 1=alive, 2=must die
		wx.EVT_LISTBOX (self, self.GetId(), self.OnList)
	#------------------------------------------------
	def SetItems (self, items):
		"""
		Sets the items, Items is a dict with label, data, weight items
		"""
		#items.sort (lambda a,b: cmp(b['weight'], a['weight']))
		self.Clear()
		self.Set([item['label'] for item in items])
		n = 0
		for item in items:
			self.SetClientData(n, item['data'])
			# n += 1  ??
		self.SetSelection(0)
	#------------------------------------------------
	def Up(self):
		line = self.GetSelection()
		if line > 0:
			self.SetSelection(line-1)
	#------------------------------------------------
	def Down(self):
		line = self.GetSelection()
		if line < self.GetCount()-1:
			self.SetSelection(line+1)
	#------------------------------------------------
	def Enter (self):
		line = self.GetSelection()
		if line >= 0:
			text = self.GetString(line)
			data = self.GetClientData(line)
			self.callback(text, data)
		self.alive = 2
		self.DestroyLater() # this is only safe when in the event handler of another widget
	#------------------------------------------------
	def OnList(self, event):
		event.Skip()
		if self.alive != 2:
			line = self.GetSelection()
			if line >= 0:
				text = self.GetString(line)
				data = self.GetClientData(line)
				self.callback (text, data)
			self.alive = 2
		else:
			wx.CallAfter (self.Destroy) # in theory we shouldn't have to do this,
									   # but when we don't, wx segfaults.
	#------------------------------------------------
	def Destroy (self):
		self.alive = 0
		wx.ListBox.Destroy (self)
#====================================================================
# according to Ian there isn't really a particular reason
# why we do not use wxMiniFrame instead of wx.Frame or even a wxWindow
class cPopupFrame(wx.Frame):
#	def __init__ (self, embed_header, widget_class, originator=None, pos=wx.DefaultPosition):
#		wx.Frame.__init__(self, None, wxNewId(), widget_class.__name__, pos=pos, style=wx.SIMPLE_BORDER)
#		self.win = widget_class(self, -1, pos = pos, size = wx.Size(300, 150), complete = self.OnOK)
	def __init__ (self, embed_header, widget, originator=None, pos=wx.DefaultPosition):
		wx.Frame.__init__(self, None, wx.NewId(), widget.__class__.__name__, pos=pos, style=wx.SIMPLE_BORDER)
		widget.set_completion_callback(self.OnOK)
		self.win = widget
		self.embed_header = embed_header
		self.originator = originator

		self.__do_layout()

		wx.EVT_BUTTON(self.__BTN_OK, self.__BTN_OK.GetId(), self.OnOK)
		wx.EVT_BUTTON(self.__BTN_Cancel, self.__BTN_Cancel.GetId(), self._on_close)
		self.win.SetFocus ()
	#------------------------------------------------
	def __do_layout(self):
		self.__BTN_OK = wx.Button (self, -1, _("OK"), style=wx.BU_EXACTFIT)
		self.__BTN_Cancel = wx.Button (self, -1, _("Cancel"), style=wx.BU_EXACTFIT)
		szr_btns = wx.BoxSizer (wx.HORIZONTAL)
		szr_btns.Add(self.__BTN_OK, 0, 0)
		szr_btns.Add(self.__BTN_Cancel, 0, 0)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.win, 1, wx.EXPAND, 0)
		szr_main.Add(szr_btns, 0, wx.EXPAND)

		self.SetAutoLayout(1)
		self.SetSizer(szr_main)
		szr_main.Fit(self)
		szr_main.SetSizeHints(self)
		self.Layout()
	#------------------------------------------------
	def _on_close (self, event):
		self.Close()
	#------------------------------------------------
	def OnOK (self, event=None):
		if self.originator:
			self.originator.Embed ("%s: %s" % (self.embed_header, self.win.GetSummary()))
		self.Close ()
#====================================================================
class cSTCval:
	def __init__(self):
		self.text = None
		self.data = None
#====================================================================
class cResizingWindow(wx.ScrolledWindow):
	"""A vertically-scrolled window which allows subwindows
	   to change their size, and adjusts accordingly.
	"""
	def __init__ (self, parent, id, pos = wx.DefaultPosition, size = wx.DefaultSize):

		wx.ScrolledWindow.__init__(self, parent, id, pos = pos, size = size, style=wx.VSCROLL)
		self.SetScrollRate(0, 20) # suppresses X scrolling by setting X rate to zero

#		self.__list = None
#		self.complete = complete	# ??

		self.__input_lines = [[]]
		self.__szr_main = None
		self.DoLayout()
		self.__szr_main = wx.FlexGridSizer(len(self.__input_lines), 2, 0, 0)
		for line in self.__input_lines:
			if len(line) != 0:
				# first label goes into column 1
				if line[0]['label'] is not None:
					self.__szr_main.Add(line[0]['label'], 1)
				else:
					self.__szr_main.Add((1, 1))
				# the rest gets crammed into column 2
				h_szr = wx.BoxSizer (wx.HORIZONTAL)
				h_szr.Add(line[0]['instance'], 1, wx.EXPAND)
				for widget in line[1:]:
					if widget['label'] is not None:
						h_szr.Add(widget['label'], 0)
					h_szr.Add(widget['instance'], 1, wx.EXPAND)
				self.__szr_main.Add(h_szr, 1, wx.EXPAND)
		self.__szr_main.AddGrowableCol(1)
		self.__szr_main.Add((1, 1))

		self.SetSizer(self.__szr_main)
		self.__szr_main.Fit(self)
		self.FitInside()
	#------------------------------------------------
	def AddWidget(self, widget, label=None):
		"""
		Adds a widget, optionally with label
		
		@type label: string
		@param label: text of the label
		@type widgets: wx.Window descendant
		"""
		if label is None:
			textbox = None
		else:
			textbox = wx.StaticText(self, -1, label, style=wx.ALIGN_RIGHT)
		# append to last line
		self.__input_lines[-1].append({'ID': label, 'label': textbox, 'instance': widget})
	#------------------------------------------------
	def Newline (self):
		"""
		Starts a newline on the widget
		"""
		self.__input_lines.append([])
	#------------------------------------------------
	def DoLayout (self):
		"""
		Overridden by descendants, this function uses AddWidget and Newline to form
		the outline of the widget
		"""
		_log.error('[%s] forgot to override DoLayout()' % self.__class__.__name__)
	#------------------------------------------------
	def ReSize (self, widget, new_height):
		"""Called when a child widget has a new height, redoes the layout.
		"""
		if self.__szr_main is not None:
			self.__szr_main.SetItemMinSize(widget, -1, new_height)
			self.__szr_main.FitInside(self)
	#------------------------------------------------
	def EnsureVisible (self, widget, cur_x = 0, cur_y = 0):
		"""
		Ensures widget is visible
		
		@param widget: a child widget
		@type cur_x: integer
		@param cur_x: the X co-ordinate of the cursor inside widget, if applicable
		@type cur_y: integer
		@param cur_y: the Y co-ordinate of the cursor inside widget
		"""
		# get widget position
		x, y = widget.GetPosition()
		# adjust for cursor offset
		x += cur_x
		y += cur_y
		# convert to virtual coordinates
		x, y = self.CalcUnscrolledPosition(x, y)
		x_dimension, y_dimension = self.GetScrollPixelsPerUnit()
		y = y / y_dimension
		# currently, don't bother with X direction
		self.Scroll (-1, round(y))
	#------------------------------------------------
	def SetValue(self, values):
		"""
		Runs SetValue() on all the fields

		@type values: dictionary
		@param values: keys are the labels, values are passed to SetValue()
		"""
		# FIXME: adapt to cSTCval
		for line in self.__input_lines:
			for widget in line:
				if widget['ID'] in values:
					if isinstance(widget['instance'], wx.stc.StyledTextCtrl):
						widget['instance'].SetText(values[widget['ID']])
					elif isinstance(widget['instance'], (wx.Choice, wx.RadioBox)):
						widget['instance'].SetSelection(values[widget['ID']])
					else:
						widget['instance'].SetValue(values[widget['ID']])
	#------------------------------------------------
	def GetValue(self):
		"""Return dict of values of inner widgets.

		Returns a dictionary of the results of GetValue()
		called on all widgets, keyed by label
		Unlabelled widgets don't get called
		"""
		# FIXME: this does not detect ID collisions between lines
		vals = {}
		for line in self.__input_lines:
			for widget in line:
				if widget['ID'] is None:
					continue
				result = cSTCval()
				if isinstance(widget['instance'], cResizingSTC):
					result.text = widget['instance'].GetText()
					result.data = widget['instance'].GetData()
				elif isinstance(widget['instance'], wx.stc.StyledTextCtrl):
					result.text = widget['instance'].GetText()
				elif isinstance(widget['instance'], (wx.Choice, wx.RadioBox)):
					result.selection = widget['instance'].GetSelection()
				else:
					result.value = widget['instance'].GetValue()
				vals[widget['ID']] = result
		return vals
	#------------------------------------------------
	def Clear (self):
		"""
		Clears all widgets where this makes sense
		"""
		for line in self.__input_lines:
			for widget in line:
				if isinstance (widget['instance'], wx.stc.StyledTextCtrl):
					widget['instance'].ClearAll()
				elif isinstance (widget['instance'], wx.TextCtrl):
					widget['instance'].Clear()
				elif isinstance (widget['instance'], (wx.ToggleButton, wx.CheckBox, wx.RadioButton, wx.Gauge)):
					widget['instance'].SetValue(0)
				elif isinstance (widget['instance'], (wx.Choice, wx.ComboBox, wx.RadioBox)):
					widget['instance'].SetSelection(0)
				elif isinstance (widget['instance'], wx.SpinCtrl):
					widget['instance'].SetValue(widget['instance'].GetMin())
	#------------------------------------------------
	def SetFocus (self):
		# try to focus on the first line if we can.
		try:
			self.lines[0][0]['instance'].SetFocus()
		except IndexError:
			pass
		except AttributeError:
			pass
	#------------------------------------------------
	def GetPickList (self, callback, x_intended, y_intended):
		"""
		Returns a pick list, destroying a pre-existing pick list for this widget

		the alive member is true until the object is Destroy ()'ed

		@param callback: called when a item is selected,
		@type callback: callable
		@param x_intended: the X-position where the list should appear
		@type x_intended: int
		@param x: the Y-position where the list should appear
		@type y_intended: int

		@return: PickList
		"""
#		# retire previous pick list
#		if self.__list and self.__list.alive:
#			self.__list.DestroyLater()
		our_width, our_height = self.GetSize()
		char_height = self.GetCharHeight()
		# make list 9 lines of height char_height high
		list_height = char_height * 9
		# and find best placement
		# - height
		if (list_height + char_height) > our_height:
			list_height = our_height
			y_final = 0
		elif (y_intended + list_height + char_height) > our_height:
			y_final = our_height - list_height
		else:
			y_final = y_intended + char_height
		# - width
		list_width = int(list_height / 1.4)
		if list_width > our_width:
			list_width = our_width
			x_final = 0
		elif (x_intended + list_width) > our_width:
			x_final = our_width - list_width
		else:
			x_final = x_intended
#		self.__list = cPickList(self, wx.Point(x_final, y_final), wx.Size(list_width, list_height), callback=callback)
#		return self.__list
		list = cPickList(self, wx.Point(x_final, y_final), wx.Size(list_width, list_height), callback=callback)
		return list
	#------------------------------------------------
#	def set_completion_callback(self, callback):
#		self.complete = callback
	#------------------------------------------------
	def GetSummary (self):
		"""Gets a terse summary string for the data in the widget"""
		return ""
#====================================================================
class cResizingSTC(wx.stc.StyledTextCtrl):
	"""
	A StyledTextCrl that monitors the size of its internal text and
	resizes the parent accordingly.

	MUST ONLY be used inside ResizingWindow !

	FIXME: override standard STC popup menu
	"""
	def __init__ (self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, data=None):
		if not isinstance(parent, cResizingWindow):
			 raise ValueError('parent of %s MUST be a ResizingWindow' % self.__class__.__name__)

		wx.stc.StyledTextCtrl.__init__ (self, parent, id, pos, size, style)

		self.SetWrapMode (wx.stc.STC_WRAP_WORD)
		# FIXME: configure
		self.StyleSetSpec (STYLE_ERROR, "fore:#7F11010,bold")
		self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
		self.StyleSetChangeable (STYLE_EMBED, 0)
#		self.StyleSetHotSpot (STYLE_EMBED, 1)
		self.SetEOLMode (wx.stc.STC_EOL_LF)

		self.__register_interests()

		self.next_in_tab_order = None
		self.prev_in_tab_order = None

		self.__parent = parent

		self.__popup_keywords = {}

		# FIXME: delay configurable
#		self.__timer = gmTimer.cTimer (
#			callback = self._on_timer_fired,
#			delay = 300
#		)
		self.__matcher = None

		self.__show_list = 1
		self.__embed = {}
		self.list = None
		self.no_list = 0			# ??

		self.__data = data			# this is just a placeholder for data to be attached to this STC, will be returned from GetData()

		self.__keyword_separators = regex.compile(r"[!?'.,:;)}\]\r\n\s\t" + r'"]+')
	#------------------------------------------------
	# public API
	#------------------------------------------------
	def set_keywords(self, popup_keywords=None):
		if popup_keywords is None:
			return
		self.__popup_keywords = popup_keywords
	#------------------------------------------------
	def SetText(self, text):
		self.__show_list = 0
		wx.stc.StyledTextCtrl.SetText(self, text)
		self.__show_list = 1
	#------------------------------------------------
	def ReplaceText (self, start, end, text, style=None):
		self.replace_text(start, end, text, style)
	#------------------------------------------------
	def Embed (self, text, data=None):
		self.no_list = 1
		self.ReplaceText(self.fragment_start, self.fragment_end, text+';', STYLE_EMBED)
		self.GotoPos(self.fragment_start+len (text)+1)
		self.SetFocus()
#		if data:
#			self.__embed[text] = data
		self.no_list = 0
	#------------------------------------------------
	def DelPhrase (self, pos):
		# FIXME: optimize
		end = pos+1
		while (end < self.GetLength()) and (self.GetCharAt(end) != ord(';')):
			end += 1
		start = pos
		while (start > 0) and (self.GetCharAt(start and start-1) != ord(';')):
			start -= 1
		self.SetTargetStart(start)
		self.SetTargetEnd(end)
		self.ReplaceTarget('')
	#------------------------------------------------
	def SetFocus(self, x=None, line=None):
		"""Set focus to current position in STC.

		- make sure that's visible, too
		"""
		wx.stc.StyledTextCtrl.SetFocus(self)
		# goto first line ?
		if line == 1:
			if x is None:
				x = 0
			self.GotoPos(self.PositionFromPoint(wx.Point(x,0)))
			return
		# goto last line ?
		if line == -1:
			_log.debug('going to last line in STC')
			last_char_pos = self.GetLength()
			if x is None:
				self.GotoPos(last_char_pos)
				_log.debug('no X given, use X=%s' % last_char_pos.x)
				return
			y = self.PointFromPosition(last_char_pos).y
			_log.debug('going to given X=%s' % x)
			self.GotoPos(self.PositionFromPoint(wx.Point(x,y)))
			return
		# goto last current position
		cur = self.PointFromPosition(self.GetCurrentPos())
		self.__parent.EnsureVisible (self, cur.x, cur.y)
	#------------------------------------------------
	def AttachMatcher (self, matcher):
		"""
		Attaches a gmMatchProvider to the STC,this will be used to drive auto-completion
		"""
		self.__matcher = matcher
	#------------------------------------------------
	def SetData(self, data):
		"""
		Configures the data associated with this STC
		@param data The associated data
		@type data Any object
		"""
		self.__data = data
	#------------------------------------------------
	def GetData(self):
		"""
		Retrieves the data associated with this STC
		"""
		return self.__data
	#------------------------------------------------
	def replace_text(self, start=None, end=None, text=None, style=None):
		"""
		Oddly, the otherwise very rich wx.STC API does not provide an
		easy way to replace text, so we provide it here.

		@param start: the position in the text to start from
		@param length: the length of the string to replace
		@param text: the new string
		@param style: the style for the replaced string
		"""
		self.SetTargetStart(start)
		self.SetTargetEnd(end)
		self.ReplaceTarget(text)
		if style is not None:
			self.StartStyling(start, 0xFF)
			self.SetStyling(len(text), style)
	#------------------------------------------------
	def replace_keyword_with_expansion(self, keyword=None, position=None):

		if keyword == '$$steffi':			# Easter Egg ;-)
			expansion = 'Hai, play! Versucht das!  (Keks dazu?)  :-)'
		else:
			expansion = gmKeywordExpansion.expand_keyword(keyword = keyword)

		if expansion is None:
			return

		if expansion == '':
			return

		self.replace_text (
			start = position,
			end = position + len(keyword),
			text = expansion
		)

		self.GotoPos(position + len(expansion) + 1)
		#wx.stc.StyledTextCtrl.SetFocus(self)
		cur = self.PointFromPosition(position + len(expansion) + 1)
		self.__parent.EnsureVisible(self, cur.x, cur.y)

	#------------------------------------------------
	# event handling
	#------------------------------------------------
	def __register_interests(self):
		self.SetModEventMask (wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT | wx.stc.STC_PERFORMED_USER)
		self.Bind(wx.stc.EVT_STC_MODIFIED, self.__on_STC_modified)
		self.Bind(wx.EVT_KEY_DOWN, self.__on_key_down)
		self.Bind(wx.EVT_KEY_UP, self.__OnKeyUp)
		#wx.EVT_KEY_UP (self, self.__OnKeyUp)
		self.Bind(wx.EVT_CHAR, self.__on_char)

	#------------------------------------------------
	def __on_STC_modified(self, event):

		# did the user do anything of note to us ?
		if not (event.GetModificationType() & (wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT)):
			event.Skip()
			return

		last_char_pos = self.GetLength()

		# stop timer if empty
		if last_char_pos == 0:
#			self.__timer.Stop()
			return

		# do we need to resize ?
		line_height = self.TextHeight(0)
		true_txt_height = (self.PointFromPosition(last_char_pos).y - self.PointFromPosition(0).y) + line_height
		x, visible_height = self.GetSize()
		if visible_height < true_txt_height:
#			print "line:", line_height
#			print "before resize: too small"
#			print "visible height", visible_height
#			print "true text hgt", true_txt_height
			n, remainder = divmod((true_txt_height - visible_height), line_height)
			if remainder > 0: n = n + 1
			target_height = visible_height + (n * line_height)
			self.__parent.ReSize(self, target_height)
#			print "after resize"
			x, y = self.GetSize()
#			print "visible height", y

		if ((visible_height - line_height) > true_txt_height):
#			print "line:", line_height
#			print "before resize: too big"
#			print "visible height", visible_height
#			print "true text hgt", true_txt_height
#			n, delta = divmod((visible_height - true_txt_height), line_height)
#			target_height = visible_height - (n * line_height)
			target_height = visible_height - line_height
			self.__parent.ReSize(self, target_height)
#			print "after resize"
			x, y = self.GetSize()
#			print "visible height", y

		# is currently relevant term a keyword for popping up an edit area or something ?
		fragment = self.__get_focussed_fragment()
		if fragment in self.__popup_keywords:
#			self.__timer.Stop()
			self.__handle_keyword(fragment)
			return
		# else restart timer for match list
#		self.__timer.Start(oneShot = True)
#		event.Skip()
		return
	#------------------------------------------------
	def __on_key_down(self, event):
		"""Act on some key presses we want to process ourselves."""

#		if (self.list is not None) and not self.list.alive:
#			self.list = None # someone else has destroyed our list!

#		curs_pos = self.GetCurrentPos()

		# <DOWN>
		# - if in list: scroll list
		# - if in last line: goto first line, same character, in next_in_tab_order
		# - else standard behaviour
		#if event.GetKeyCode() == wx.WXK_DOWN:
#			if (self.list is not None) and self.list.alive:
#				self.list.Down()
#				return
#			print "arrow down @ %s (line %s of %s)" % (curs_pos, self.LineFromPosition(curs_pos), self.GetLineCount())
		#	if self.LineFromPosition(curs_pos)+1 == self.GetLineCount():
		#		if self.next_in_tab_order is not None:
		#			curs_coords = self.PointFromPosition(curs_pos)
		#			self.next_in_tab_order.SetFocus(x=curs_coords.x, line=1)
		#			return

		# <UP>
		# - if in list: scroll list
		# - if in first line: goto last line, same character, in prev_in_tab_order
		# - else standard behaviour
		#if event.GetKeyCode() == wx.WXK_UP:
		#	_log.debug('<UP-ARROW> key press detected')
#			if (self.list is not None) and self.list.alive:
#				self.list.Up()
#				return
		#	_log.debug('pos %s = line %s' % (curs_pos, self.LineFromPosition(curs_pos)))
		#	if self.LineFromPosition(curs_pos) == 0:
		#		_log.debug('first line of STC - special handling')
		#		if self.prev_in_tab_order is not None:
		#			_log.debug('prev_in_tab_order = %s' % str(self.prev_in_tab_order))
		#			curs_coords = self.PointFromPosition(curs_pos)
		#			_log.debug('cursor coordinates in current STC: %s:%s' % (curs_coords.x, curs_coords.y))
		#			self.prev_in_tab_order.SetFocus(x=curs_coords.x, line=-1)
		#			return
		#	else:
		#		_log.debug('not first line of STC - standard handling')

		# <TAB> key
		# - move to next/prev_in_tab_order
		# FIXME: what about inside a list ?
		if event.GetKeyCode() == wx.WXK_TAB:
			if event.ShiftDown():
				if self.prev_in_tab_order is not None:
					self.prev_in_tab_order.SetFocus()
			else:
				if self.next_in_tab_order is not None:
					self.next_in_tab_order.SetFocus()
			return

		# <DEL>
		# - if inside embedded string
		#	- delete entire string and data dict
		# - else standard behaviour
#		if event.GetKeyCode() == wx.WXK_DELETE:
#			# FIXME: perhaps add check for regex, too ?
#			if self.GetStyleAt(curs_pos) == STYLE_EMBED:
#				self.DelPhrase(curs_pos)
#				# FIXME: also delete corresponding "additional data" dict ...
#				return

		# <BACKSPACE>
		# - if inside embedded string
		#	- delete entire string and data dict
		# - else standard behaviour
#		if event.GetKeyCode() == wx.WXK_BACK:
#			# FIXME: perhaps add check for regex, too ?
#			if self.GetStyleAt(curs_pos-1) == STYLE_EMBED:
#				self.DelPhrase (curs_pos-1)
#				# FIXME: also delete corresponding "additional data" dict ...
#				return

		event.Skip()	# skip to next event handler to keep processing
	#------------------------------------------------
	def __OnKeyUp (self, event):
		if not self.list:
			curs_pos = self.PointFromPosition(self.GetCurrentPos())
			self.__parent.EnsureVisible (self, curs_pos.x, curs_pos.y)
	#------------------------------------------------
	def __on_char(self, evt):

		char = chr(evt.GetUnicodeKey())

		if self.__keyword_separators.match(char) is not None:
			if self.GetLength() == 1:
				evt.Skip()
				return

			line, caret_pos = self.GetCurLine()
			word = self.__keyword_separators.split(line[:caret_pos])[-1]
			if (word not in [ r[0] for r in gmKeywordExpansion.get_textual_expansion_keywords() ]) and (word != '$$steffi'):		# Easter Egg ;-)
				evt.Skip()
				return

			start = self.GetCurrentPos() - len(word)
			wx.CallAfter(self.replace_keyword_with_expansion, word, start)
			evt.Skip()
			return

		evt.Skip()
	#------------------------------------------------
#	def _cb_on_popup_completion(self, was_cancelled=False):
#		"""Callback for popup completion.
#
#		- this is called when the user has signalled
#		  being done interacting with the popup
#		- if was_cancelled is True the popup content should
#		  be ignored and no further action taken on it
#		"""
#		print "popup interaction completed"
#		if was_cancelled:
#			print "popup cancelled, ignoring data"
##			self.__popup.DestroyLater()
#			self.__popup = None
#			return
#		print "getting data from popup and acting on it"
#		print self.__popup.GetData()
#		# FIXME: wxCallAfter(embed) and store
#		# maybe be a little smarter here
#		self.__popup.DestroyLater()
#		self.__popup = None
	#------------------------------------------------
	def _on_timer_fired(self, cookie):
#		print 'timer <%s> fired' % cookie
		fragment = self.__get_focussed_fragment()
		if fragment.strip() == '':
			return 1
#		print 'should popup context pick list on <%s> now' % fragment

		return 1

		# - get matches and popup select list
		if self.no_list:
			return
		if self.__matcher is None:
			return
		if not self.__show_list:
			return

		# do indeed show list
		if len(fragment) == 0:
			if (self.list is not None) and self.list.alive:
				self.list.DestroyLater()
			return
		matches_found, matches = self.__matcher.getMatches(fragment)
		if not matches_found:
			if (self.list is not None) and self.list.alive:
				self.list.DestroyLater()
			return

		curs_pos = self.GetCurrentPos()
		if not ((self.list is not None) and self.list.alive):
			x, y = self.GetPosition()
			p = self.PointFromPosition(curs_pos)
			self.list = self.__parent.GetPickList(self.__userlist, x+p.x, y+p.y)
		self.list.SetItems(matches)
	#------------------------------------------------
	# internal API
	#------------------------------------------------
	def __get_focussed_fragment(self):
		curs_pos = self.GetCurrentPos()
		text = self.GetText()
		self.fragment_start = text.rfind(';', 0, curs_pos)				# FIXME: ';' hardcoded as separator
		if self.fragment_start == -1:
			self.fragment_start = 0
		else:
			self.fragment_start += 1
		last_char_pos = self.GetLength()
		self.fragment_end = text.find(';', curs_pos, last_char_pos)		# FIXME: ';' hardcoded as separator
		if self.fragment_end == -1:
			self.fragment_end = last_char_pos
		return text[self.fragment_start:self.fragment_end].strip()
	#------------------------------------------------
	def __get_best_popup_geom(self):
#		print "calculating optimal popup geometry"
		parent_width, parent_height = self.__parent.GetSize()
#		print "parent size is %sx%s pixel" % (parent_width, parent_height)
		# FIXME: this should be gotten from ourselves, not the parent, but how ?
		parent_char_height = self.__parent.GetCharHeight()
#		print "char height in parent is", parent_char_height, "pixel"
		# make popup 9 lines of height parent_char_height high
		# FIXME: better detect this, but how ?
		popup_height = parent_char_height * 9
#		print "hence intended popup height is", popup_height, "pixel"
		# get STC displacement inside parent
		stc_origin_x, stc_origin_y = self.GetPosition()
#		print "inside parent STC is @ %s:%s" % (stc_origin_x, stc_origin_y)
		# get current cursor position inside STC in pixels
		curs_pos = self.PointFromPosition(self.GetCurrentPos())
#		print "inside STC cursor is @ %s:%s" % (curs_pos.x, curs_pos.y)
		# find best placement
		# - height
		if (popup_height + parent_char_height) > parent_height:
			# don't let popup get bigger than parent window
			popup_height = parent_height
			popup_y_pos = 0
		elif ((popup_height + parent_char_height) + (curs_pos.y + stc_origin_y)) > parent_height:
			# if would fit inside but forced (partially) outside
			# by cursor position then move inside
			popup_y_pos = parent_height - popup_height
		else:
			popup_y_pos = (curs_pos.y + stc_origin_y) + parent_char_height
		# - width
		popup_width = int(popup_height / 1.4)		# Golden Cut
		if popup_width > parent_width:
			# don't let popup get bigger than parent window
			popup_width = parent_width
			popup_x_pos = 0
		elif (popup_width + (curs_pos.x + stc_origin_x)) > parent_width:
			# if would fit inside but forced (partially) outside
			# by cursor position then move inside
			popup_x_pos = parent_width - popup_width
		else:
			popup_x_pos = curs_pos.x + stc_origin_x
#		print "optimal geometry = %sx%s @ %s:%s" % (popup_width, popup_height, popup_x_pos, popup_y_pos)
		return (wx.Point(popup_x_pos, popup_y_pos), wx.Size(popup_width, popup_height))
	#------------------------------------------------
	def __handle_keyword(self, kwd=None):
		try:
			create_widget = self.__popup_keywords[kwd]['widget_factory']
		except KeyError:
			gmDispatcher.send(signal='statustext', msg=_('No action configured for keyword [%s].') % kwd)
			return False

#		best_pos, best_size = self.__get_best_popup_geom()
		screen_pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos()))
		top_parent = wx.GetTopLevelParent(self)
		best_pos = top_parent.ScreenToClient(screen_pos)
		try:
			popup = create_widget (
				parent = top_parent,
				pos = best_pos,
				size = wx.Size(400, 300),
				style = wx.SUNKEN_BORDER,
				data_sink = self.__popup_keywords[kwd]['widget_data_sink']
			)
		except Exception:
			_log.exception('cannot call [%s] on keyword [%s] to create widget' % (create_widget, kwd))
			gmGuiHelpers.gm_show_error (
				error = _('Cannot invoke [%s] for keyword [%s].') % (create_widget, kwd),
				title = _('showing keyword popup')
			)
			return False

		if not isinstance(popup, wx.Dialog):
			gmDispatcher.send(signal='statustext', msg=_('Action [%s] on keyword [%s] is invalid.') % (create_widget, kwd))
			_log.error('keyword [%s] triggered action [%s]' % (kwd, create_widget))
			_log.error('the result (%s) is not a wx.Dialog subclass instance, however' % str(popup))
			return False

		# display widget
		result = popup.ShowModal()
		if result == wx.ID_OK:
			summary = popup.get_summary()
			wx.CallAfter(self.Embed, summary)
		popup.DestroyLater()
	#------------------------------------------------
	def __userlist (self, text, data=None):
		# this is a callback
#		--- old --------------
#		# FIXME: need explanation on instance/callable business, it seems complicated
#		if issubclass(data, cResizingWindow):
#			win = data (
#				self,
#				-1,
#				pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos())),
#				size = wx.Size(300, 150)
#			)
#			cPopupFrame (
#				embed_header = text,
#				widget = win,
#				originator = self,
#				pos = self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos()))
#			).Show()
#		elif callable(data):
#			data (text, self.__parent, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ())))
#		--- old --------------
		if self.MakePopup (text, data, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ()))):
			pass
		else:
			self.Embed (text, data)
	#--------------------------------------------------
	def MakePopup (self, text, data, parent, cursor_position):
		"""
		An overrideable method, called whenever a match is made in this STC
		Designed for producing popups, but the overrider can in fact, do
		whatever they please.

		@return True if a poup-up or similar actually happened (which suppresses inserting the match string in the text
		@rtype boolean
		"""
		#cPopupFrame(text, win, self, cursor_position)).Show()
		return False
#====================================================================
#====================================================================
if __name__ == '__main__':

#	from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList
#	from Gnumed.pycommon import gmI18N

	def create_widget_on_test_kwd1(*args, **kwargs):
		print("test keyword must have been typed...")
		print("actually this would have to return a suitable wx.Window subclass instance")
		print("args:", args)
		print("kwd args:")
		for key in kwargs:
			print(key, "->", kwargs[key])
	#================================================================
	def create_widget_on_test_kwd2(*args, **kwargs):
		msg = (
			"test keyword must have been typed...\n"
			"actually this would have to return a suitable wx.Window subclass instance\n"
		)
		for arg in args:
			msg = msg + "\narg ==> %s" % arg
		for key in kwargs:
			msg = msg + "\n%s ==> %s" % (key, kwargs[key])
		gmGuiHelpers.gm_show_info (
			info = msg,
			title = 'msg box on create_widget from test_keyword'
		)
	#================================================================
	class cTestKwdPopupPanel(wx.Panel):
		def __init__(self, parent, pos, size, style, completion_callback):
			wx.Panel.__init__ (
				self,
				parent,
				-1,
				pos,
				size,
				style
			)
			self.__completion_callback = completion_callback
			self._wx.ID_BTN_OK = wx.NewId()
			self._wx.ID_BTN_Cancel = wx.NewId()
			self.__do_layout()
			self.__register_interests()
			self.Show()

		def __do_layout(self):
			# message
			msg = "test keyword popup"
			text = wx.StaticText (self, -1, msg)
			# buttons
			self.btn_OK = wx.Button(self, self._wx.ID_BTN_OK, _("OK"))
			self.btn_OK.SetToolTip(_('dismiss popup and embed data'))
			self.btn_Cancel = wx.Button(self, self._wx.ID_BTN_Cancel, _("Cancel"))
			self.btn_Cancel.SetToolTip(_('dismiss popup and throw away data'))
			szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
			szr_buttons.Add(self.btn_OK, 1, wx.EXPAND | wx.ALL, 1)
			szr_buttons.Add(5, 0, 0)
			szr_buttons.Add(self.btn_Cancel, 1, wx.EXPAND | wx.ALL, 1)
			# arrange
			szr_main = wx.BoxSizer(wx.VERTICAL)
			szr_main.Add(text, 1, wx.EXPAND | wx.ALL, 1)
			szr_main.Add(szr_buttons, 0)
			# layout
			self.SetAutoLayout(True)
			self.SetSizer(szr_main)
			szr_main.Fit(self)

		def __register_interests(self):
			wx.EVT_BUTTON(self.btn_OK, self._wx.ID_BTN_OK, self._on_ok)
			wx.EVT_BUTTON(self.btn_Cancel, self._wx.ID_BTN_Cancel, self._on_cancel)

		def _on_ok(self, event):
			self.__completion_callback(was_cancelled = False)

		def _on_cancel(self, event):
			self.__completion_callback(was_cancelled = True)
	#================================================================
	def create_widget_on_test_kwd3(parent, pos, size, style, completion_callback):
		pnl = cTestKwdPopupPanel (
			parent = parent,
			pos = pos,
			size = size,
			style = style,
			completion_callback = completion_callback
		)
		return pnl
	#================================================================
	class cSoapWin (cResizingWindow):
		def DoLayout(self):
			self.input1 = cResizingSTC(self, -1)
			self.input2 = cResizingSTC(self, -1)
			self.input3 = cResizingSTC(self, -1)

			self.input1.prev_in_tab_order = None
			self.input1.next_in_tab_order = self.input2
			self.input2.prev_in_tab_order = self.input1
			self.input2.next_in_tab_order = self.input3
			self.input3.prev_in_tab_order = self.input2
			self.input3.next_in_tab_order = None

			self.AddWidget (widget=self.input1, label="S")
			self.Newline()
			self.AddWidget (widget=self.input2, label="O")
			self.Newline()
			self.AddWidget (widget=self.input3, label="A+P")

			kwds = {}
			kwds['$test_keyword'] = {'widget_factory': create_widget_on_test_kwd3}
			self.input2.set_keywords(popup_keywords=kwds)
	#================================================================
	class cSoapPanel(wx.Panel):
		def __init__ (self, parent, id):
			wx.Panel.__init__(self, parent, id)
			#sizer = wx.BoxSizer(wx.VERTICAL)
			self.soap = cSoapWin(self, -1)
			self.save = wx.Button (self, -1, _(" Save "))
			self.delete = wx.Button (self, -1, _(" Delete "))
			self.new = wx.Button (self, -1, _(" New "))
#			self.list = wx.ListBox (self, -1, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
			wx.EVT_BUTTON (self.save, self.save.GetId (), self.OnSave)
			wx.EVT_BUTTON (self.delete, self.delete.GetId (), self.OnDelete)
			wx.EVT_BUTTON (self.new, self.new.GetId (), self.OnNew)
#			wx.EVT_LISTBOX (self.list, self.list.GetId (), self.OnList)
			self.__do_layout()

		def __do_layout (self):
			sizer_1 = wx.BoxSizer(wx.VERTICAL)
			sizer_1.Add(self.soap, 3, wx.EXPAND, 0)
			sizer_2 = wx.BoxSizer (wx.HORIZONTAL)
			sizer_2.Add(self.save, 0, 0)
			sizer_2.Add(self.delete, 0, 0)
			sizer_2.Add(self.new, 0, 0)
			sizer_1.Add(sizer_2, 0, wx.EXPAND)
#			sizer_1.Add(self.list, 3, wx.EXPAND, 0)
			self.SetAutoLayout(1)
			self.SetSizer(sizer_1)
			sizer_1.Fit(self)
			sizer_1.SetSizeHints(self)
			self.Layout()

		def OnDelete (self, event):
			self.soap.Clear()
#			sel = self.list.GetSelection ()
#			if sel >= 0:
#				self.list.Delete (sel)

		def OnNew (self, event):
#			sel = self.list.GetSelection ()
#			if sel >= 0:
#				self.OnSave (None)
			self.soap.Clear()
#			self.list.SetSelection (sel, 0)

		def OnSave (self, event):
			#data = self.soap.GetValue()
#			title = data['Assessment'] or data['Subjective'] or data['Plan'] or data['Objective']
			self.soap.Clear()
#			sel = self.list.GetSelection ()
#			if sel < 0:
#				self.list.Append (title, data)
#			else:
#				self.list.SetClientData (sel, data)
#				self.list.SetString (sel, title)

#		def OnList (self, event):
#			self.soap.SetValues (event.GetClientData ())
	#================================================================
	class testFrame(wx.Frame):
		def __init__ (self, title):
			wx.Frame.__init__ (self, None, wx.NewId(), "test SOAP", size = wx.Size (350, 500)) # this frame will have big fat borders
			wx.EVT_CLOSE (self, self.OnClose)
			panel = cSoapPanel(self, -1)
			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add (panel, 1, wx.GROW)
			self.SetSizer(sizer)
			self.SetAutoLayout(1)
			sizer.Fit (self)
			self.Layout ()

		def OnClose (self, event):
			self.DestroyLater()
	#================================================================
	class testApp(wx.App):
		def OnInit (self):
			self.frame = testFrame ("testFrame")
			self.frame.Show()
			return 1
	#================================================================
	app = testApp(0)
	app.MainLoop()
#====================================================================
