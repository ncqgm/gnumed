"""gmResizingWidgets - Resizing widgets for use in GnuMed.

"""
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmResizingWidgets.py,v $
# $Id: gmResizingWidgets.py,v 1.5 2004-12-14 10:26:01 ihaywood Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "Ian Haywood, Karsten Hilbert"
__license__ = 'GPL  (details at http://www.gnu.org)'

from wxPython import wx

STYLE_ERROR=1
STYLE_TEXT=2
STYLE_EMBED=4

#====================================================================
class cPickList (wx.wxListBox):
	def __init__ (self, parent, pos, size, callback):
		wx.wxListBox.__init__(self, parent, -1, pos, size, style=wx.wxLB_SINGLE | wx.wxLB_NEEDED_SB)
		self.callback = callback
		self.alive = 1 # 0=dead, 1=alive, 2=must die
		wx.EVT_LISTBOX (self, self.GetId(), self.OnList)
	#------------------------------------------------
	def SetItems (self, items):
		"""
		Sets the items, Items is a dict with label, data, weight items
		"""
		items.sort (lambda a,b: cmp(b['weight'], a['weight']))
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
		self.Destroy() # this is only safe when in the event handler of another widget
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
			wx.wxCallAfter (self.Destroy) # in theory we shouldn't have to do this,
									   # but when we don't, wx segfaults.
	#------------------------------------------------
	def Destroy (self):
		self.alive = 0
		wx.wxListBox.Destroy (self)
#====================================================================
class cPopupFrame(wx.wxFrame):
#	def __init__ (self, text, widget_class, originator=None, pos=wxDefaultPosition):
#		wxFrame.__init__(self, None, wxNewId(), widget_class.__name__, pos=pos, style=wxSIMPLE_BORDER)
#		self.win = widget_class(self, -1, pos = pos, size = wxSize(300, 150), complete = self.OnOK)
	def __init__ (self, text, widget, originator=None, pos=wx.wxDefaultPosition):
		wx.wxFrame.__init__(self, None, wx.wxNewId(), widget.__class__.__name__, pos=pos, style=wx.wxSIMPLE_BORDER)
		widget.set_completion_callback(self.OnOK)
		self.win = widget
		self.text = text
		self.originator = originator

		self.__do_layout()

		EVT_BUTTON(self.__BTN_OK, self.__BTN_OK.GetId(), self.OnOK)
		EVT_BUTTON(self.__BTN_Cancel, self.__BTN_Cancel.GetId(), self._on_close)
		self.win.SetFocus ()
	#------------------------------------------------
	def __do_layout(self):
		self.__BTN_OK = wx.wxButton (self, -1, _("OK"), style=wx.wxBU_EXACTFIT)
		self.__BTN_Cancel = wx.wxButton (self, -1, _("Cancel"), style=wx.wxBU_EXACTFIT)
		szr_btns = wx.wxBoxSizer (wx.wxHORIZONTAL)
		szr_btns.Add(self.__BTN_OK, 0, 0)
		szr_btns.Add(self.__BTN_Cancel, 0, 0)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.win, 1, wx.wxEXPAND, 0)
		szr_main.Add(szr_btns, 0, wx.wxEXPAND)

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
			self.originator.Embed ("%s: %s" % (self.text, self.win.GetSummary()))
		self.Close ()
#====================================================================
class cResizingWindow(wx.wxScrolledWindow):
	"""A vertically-scrolled window which allows subwindows
	   to change their size, and adjusts accordingly.
	"""
	def __init__ (self, parent, id, pos = wx.wxDefaultPosition, size = wx.wxDefaultSize, complete = None):

		wx.wxScrolledWindow.__init__(self, parent, id, pos = pos, size = size, style=wx.wxVSCROLL)
		self.SetScrollRate(0, 20) # suppresses X scrolling by setting X rate to zero

		self.__lines = [[]]
#		self.__list = None
#		self.__matcher = None
#		self.__popup = None

		self.prev = None
		self.next = None
		self.complete = complete	# ??

		self.__szr_main = None
		self.DoLayout()
		self.__szr_main = wx.wxFlexGridSizer(len(self.__lines), 2)
		for line in self.__lines:
			if len(line) != 0:
				# first label goes into column 1
				if line[0]['label'] is not None:
					self.__szr_main.Add(line[0]['label'], 1)
				else:
					self.__szr_main.Add((1, 1))
				# the rest gets crammed into column 2
				h_szr = wx.wxBoxSizer (wx.wxHORIZONTAL)
				h_szr.Add(line[0]['instance'], 1, wx.wxGROW)
				for widget in line[1:]:
					if widget['label'] is not None:
						h_szr.Add(widget['label'], 0)
					h_szr.Add(widget['instance'], 1, wx.wxGROW)
				self.__szr_main.Add(h_szr, 1, wx.wxGROW)
		self.__szr_main.AddGrowableCol(1)
		self.__szr_main.Add((1, 1))

		self.SetSizer(self.__szr_main)
		self.FitInside()
	#------------------------------------------------
	def AddWidget(self, widget, label=None):
		"""
		Adds a widget, optionally with label
		
		@type label: string
		@param label: text of the label
		@type widgets: wx.wxWindow descendant
		"""
		if label is None:
			textbox = None
		else:
			textbox = wx.wxStaticText (self, -1, label, style=wx.wxALIGN_RIGHT)
		# append to last line
		self.__lines[-1].append({'ID': label, 'label': textbox, 'instance': widget})
	#------------------------------------------------
	def Newline (self):
		"""
		Starts a newline on the widget
		"""
		self.__lines.append([])
	#------------------------------------------------
	def DoLayout (self):
		"""
		Overridden by descendants, this function uses AddWidget and Newline to form
		the outline of the widget
		"""
		pass
	#------------------------------------------------
	def ReSize (self, widget, new_height):
		"""
		Called when a child widget has a new height, redoes the layout
		"""
		if self.__szr_main:
			self.__szr_main.SetItemMinSize (widget, -1, new_height)
			self.__szr_main.FitInside (self)
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
		x, y = widget.GetPositionTuple()
		# adjust for cursor offset
		x += cur_x
		y += cur_y
		# convert to virtual coordinates
		x, y = self.CalcUnscrolledPosition(x, y)
		x_dimension, y_dimension = self.GetScrollPixelsPerUnit()
		y = y / y_dimension
		# currently, don't bother with X direction
		self.Scroll (-1, y)
	#------------------------------------------------
	def SetValue(self, values):
		"""
		Runs SetValue() on all the fields

		@type values: dictionary
		@param values: keys are the labels, values are passed to SetValue()
		"""
		for widget_list in self.__lines:
			for widget in line:
				if values.has_key(widget['ID']):
					if isinstance(widget['instance'], wx.wxStyledTextCtrl):
						widget['instance'].SetText(values[widget['ID']])
					elif isinstance(widget['instance'], (wx.wxChoice, wx.wxRadioBox)):
						widget['instance'].SetSelection(values[widget['ID']])
					else:
						widget['instance'].SetValue(values[widget['ID']])
	#------------------------------------------------
	def GetValue(self):
		"""
		Returns a dictionary of the results of GetValue()
		called on all widgets, keyed by label
		Unlabelled widgets don't get called
		"""
		# FIXME: this does not detect ID collisions between lines
		vals = {}
		for widget_list in self.__lines:
			for widget in line:
				if widget['ID'] is not None:
					if isinstance(widget['instance'], wx.wxStyledTextCtrl):
						vals[widget['ID']] = widget['instance'].GetText()
					elif isinstance(widget['instance'], (wx.wxChoice, wx.wxRadioBox)):
						vals[widget['ID']] = widget['instance'].GetSelection()
					else:
						vals[widget['ID']] = widget['instance'].GetValue ()
		return vals
	#------------------------------------------------
	def Clear (self):
		"""
		Clears all widgets where this makes sense
		"""
		for line in self.__lines:
			for widget in line:
				if isinstance (widget['instance'], wx.wxStyledTextCtrl):
					widget['instance'].ClearAll()
				elif isinstance (widget['instance'], wx.wxTextCtrl):
					widget['instance'].Clear()
				elif isinstance (widget['instance'], (wx.wxToggleButton, wx.wxCheckBox, wx.wxRadioButton, wx.wxGauge)):
					widget['instance'].SetValue(0)
				elif isinstance (widget['instance'], (wx.wxChoice, wx.wxComboBox, wx.wxRadioBox)):
					widget['instance'].SetSelection(0)
				elif isinstance (widget['instance'], wx.wxSpinCtrl):
					widget['instance'].SetValue(widget['instance'].GetMin())

	#------------------------------------------------
	def SetFocus (self):
		try:
			self.lines[0][0]['instance'].SetFocus ()
			# try to focus on the first line if we can.
		except IndexError:
			pass
		except AttributeError:
			pass
	#------------------------------------------------
	def GetPickList (self, callback, x, y):
		"""
		Returns a pick list, destroying a pre-existing pick list for this widget

		the alive member is true until the object is Destroy ()'ed

		@param callback: called when a item is selected,
		@type callback: callable
		@param x: the X-position where the list should appear
		@type x: int
		@param x: the Y-position where the list should appear
		@type y: int

		@return: PickList
		"""
#		# retire previous pick list
#		if self.__list and self.__list.alive:
#			self.__list.Destroy()
		our_width, our_height = self.GetSizeTuple()
		char_height = self.GetCharHeight()
		# make list 9 lines high
		list_height = char_height * 9
		# and find best placement
		if (list_height + char_height) > our_height:
			list_height = our_height
			y = 0
		elif (y + list_height + char_height) > our_height:
			y = our_height - list_height
		else:
			y += char_height
		list_width = int(list_height / 1.4)
		if list_width > our_width:
			list_width = our_width
			x = 0
		elif (x + list_width) > our_width:
			x = our_width - list_width
#		self.__list = cPickList(self, wx.wxPoint(x, y), wx.wxSize(list_width, list_height), callback)
#		return self.__list
		list = cPickList(self, wx.wxPoint(x, y), wx.wxSize(list_width, list_height), callback)
		return list
	#------------------------------------------------
	def set_completion_callback(self, callback):
		self.complete = callback
	#------------------------------------------------
	def GetSummary (self):
		"""Gets a terse summary string for the data in the widget"""
		return ""
	#------------------------------------------------
#	FIXME: I don't think this should know about something as specific as cClinItem ...
#	def Set (self, item):
#		"""
#		Accepts a cClinItem, sets the widget to reflect its contents
#		"""
#		pass
	#------------------------------------------------
#	def Save (self, item):
#		"""
#		Accepts a cClinItem, sets *it* to reflect the widget's contents
#		"""
#		pass

#==========================================================
class cResizingSTC (wx.wxStyledTextCtrl):
	"""
	A StyledTextCrl that monitors the size of its internal text and
	resizes the parent accordingly.
	
	MUST ONLY be used inside ResizingWindow !
	"""
	def __init__ (self, parent, id, pos=wx.wxDefaultPosition, size=wx.wxDefaultSize, style=0):
		if not isinstance(parent, cResizingWindow):
			 raise ValueError, 'parent of %s MUST be a ResizingWindow' % self.__class__.__name__
		wx.wxStyledTextCtrl.__init__ (self, parent, id, pos, size, style)
		self.SetWrapMode (wx.wxSTC_WRAP_WORD)
		self.StyleSetSpec (STYLE_ERROR, "fore:#7F11010,bold")
		self.StyleSetSpec (STYLE_EMBED, "fore:#4040B0")
		self.StyleSetChangeable (STYLE_EMBED, 0)
#		self.StyleSetHotSpot (STYLE_EMBED, 1)
		self.SetEOLMode (wx.wxSTC_EOL_LF)
		self.SetModEventMask (wx.wxSTC_MOD_INSERTTEXT | wx.wxSTC_MOD_DELETETEXT | wx.wxSTC_PERFORMED_USER)

		wx.EVT_STC_MODIFIED (self, self.GetId(), self.__on_STC_modified)
		wx.EVT_KEY_DOWN (self, self.__OnKeyDown)
		wx.EVT_KEY_UP (self, self.__OnKeyUp)

		self.__popup_keywords = {}

		self.parent = parent
		self.__show_list = 1
		self.__embed = {}
		self.list = 0
		self.no_list = 0			# ??
		self.__matcher = None
	#------------------------------------------------
	# public API
	#------------------------------------------------
	def SetText(self, text):
		self.__show_list = 0
		wx.wxStyledTextCtrl.SetText(self, text)
		self.__show_list = 1
	#------------------------------------------------
	def ReplaceText (self, start, end, text, style=-1, space=0):
		"""
		Oddly, the otherwise very rich wxSTC API does not provide an
		easy way to replace text, so we provide it here.

		@param start: the position in the text to start from
		@param length: the length of the string to replace
		@param text: the new string
		@param style: the style for the replaced string
		"""
		self.SetTargetStart(start)
		self.SetTargetEnd(end)
		self.ReplaceTarget(text)
		if style > -1:
			self.StartStyling(start, 0xFF)
			self.SetStyling(len(text), style)
	#------------------------------------------------
	def set_keywords(self, popup_keywords=None):
		if popup_keywords is None:
			return
		self.__popup_keywords = popup_keywords
	#------------------------------------------------
	def Embed (self, text, data=None):
		self.no_list = 1
		self.ReplaceText (self.fragment_start, self.fragment_end, text+';', STYLE_EMBED, 1)
		self.GotoPos (self.fragment_start+len (text)+1)
		self.SetFocus ()
		if data:
			self.__embed[text] = data
		self.no_list = 0
	#------------------------------------------------
	def DelPhrase (self, pos):
		end = pos+1
		while end < self.GetLength () and self.GetCharAt (end) != ord(';'):
			end += 1
		start = pos
		while start > 0 and self.GetCharAt (start and start-1) != ord (';'):
			start -= 1
		self.SetTargetStart (start)
		self.SetTargetEnd (end)
		self.ReplaceTarget ('')
	#------------------------------------------------
	def SetFocus (self):
		wx.wxStyledTextCtrl.SetFocus(self)
		cur = self.PointFromPosition(self.GetCurrentPos())
		self.parent.EnsureVisible (self, cur.x, cur.y)
	#------------------------------------------------
	def AttachMatcher (self, matcher):
		"""
		Attaches a gmMatchProvider to the STC,this will be used to drive auto-completion
		"""
		self.__matcher = matcher
	#------------------------------------------------
	# event handlers
	#------------------------------------------------
	def __on_STC_modified(self, event):
		event.Skip()
		# did the user do anything of note ?
		if not (event.GetModificationType() & (wx.wxSTC_MOD_INSERTTEXT | wx.wxSTC_MOD_DELETETEXT)):
			return
		# do we need to resize ?
		last_char_pos = self.GetLength()
		true_txt_height = (self.PointFromPosition(last_char_pos).y - self.PointFromPosition(0).y) + self.TextHeight(0)
		x, visible_height = self.GetSizeTuple()
		if visible_height != true_txt_height:
			self.parent.ReSize(self, true_txt_height)
		# get current relevant string
		curs_pos = self.GetCurrentPos()
		text = self.GetText()
		self.fragment_start = text.rfind(';', 0, curs_pos)				# FIXME: ';' hardcoded as separator
		if self.fragment_start == -1:
			self.fragment_start = 0
		else:
			self.fragment_start += 1
		self.fragment_end = text.find(';', curs_pos, last_char_pos)		# FIXME: ';' hardcoded as separator
		if self.fragment_end == -1:
			self.fragment_end = last_char_pos
		fragment = text[self.fragment_start:self.fragment_end].strip()
		# is it a keyword for popping up an edit area or something ?
		if fragment in self.__popup_keywords.keys():
			print fragment, "is a popup keyword"
			return

		return

		# FIXME: we need to use a timeout here !

		# - get matches and popup select list
		if self.no_list:
			return
		if self.__matcher is None:
			return
		if not self.__show_list:
			return

		# do indeed show list
		if len(fragment) == 0:
			if self.list and self.list.alive:
				self.list.Destroy()
			return
		matches_found, matches = self.__matcher.getMatches(fragment)
		if not matches_found:
			if self.list and self.list.alive:
				self.list.Destroy()
			return
		if not (self.list and self.list.alive):
			x, y = self.GetPositionTuple()
			p = self.PointFromPosition(curs_pos)
			self.list = self.parent.GetPickList(self.__userlist, x+p.x, y+p.y)
		self.list.SetItems(matches)
	#------------------------------------------------
	def __OnKeyDown (self, event):
		if self.list and not self.list.alive:
			self.list = None # someone else has destroyed our list!
		pos = self.GetCurrentPos()

		if event.KeyCode () == wx.WXK_TAB:
			if event.m_shiftDown:
				if self.prev:
					self.prev.SetFocus()
			else:
				if self.next:
					self.next.SetFocus()
				elif self.parent.complete:
					self.parent.complete()

		elif self.parent.complete and event.KeyCode() == wx.WXK_F12:
			self.parent.complete ()

		elif event.KeyCode () == ord (';'):
			if self.GetLength () == 0:
				wx.wxBell ()
			elif self.GetCharAt (pos and pos-1) == ord (';'):
				wx.wxBell ()
			else:
				event.Skip ()

		elif event.KeyCode () == wx.WXK_DELETE:
			if self.GetStyleAt (pos) == STYLE_EMBED:
				self.DelPhrase (pos)
			else:
				event.Skip ()

		elif event.KeyCode () == wx.WXK_BACK:
			if self.GetStyleAt (pos and pos-1) == STYLE_EMBED:
				self.DelPhrase (pos and pos-1)
			else:
				event.Skip ()

		elif event.KeyCode () == wx.WXK_RETURN and not event.m_shiftDown:
			if self.list and self.list.alive:
				self.list.Enter ()
			elif pos == self.GetLength ():
				if self.GetCharAt (pos and pos-1) == ord (';'):
					if self.next:
						self.next.SetFocus ()
					elif self.parent.complete:
						self.parent.complete ()
				else:
					self.AddText (';')
			elif self.GetLength () == 0 and self.next ():
				self.next.SetFocus ()
			else:
				event.Skip()

		elif self.list and self.list.alive and event.KeyCode () == wx.WXK_UP:
			self.list.Up()

		elif self.list and self.list.alive and event.KeyCode () == wx.WXK_DOWN:
			self.list.Down()

		else:
			event.Skip ()
	#------------------------------------------------
	def __OnKeyUp (self, event):
		if not self.list:
			cur = self.PointFromPosition (self.GetCurrentPos())
			self.parent.EnsureVisible (self, cur.x, cur.y)
	#------------------------------------------------
	def __userlist (self, text, data=None):
		# this is a callback
		# FIXME: need explanation on instance/callable business, it seems complicated
		if issubclass(data, cResizingWindow):
			win = data(self, -1, pos = pos, size = wxSize(300, 150))
			cPopupFrame(text, win, self, self.ClientToScreen(self.PointFromPosition(self.GetCurrentPos()))).Show()
		elif callable (data):
			data (text, self.parent, self, self.ClientToScreen (self.PointFromPosition (self.GetCurrentPos ())))
		else:
			self.Embed (text, data)
#====================================================
# $Log: gmResizingWidgets.py,v $
# Revision 1.5  2004-12-14 10:26:01  ihaywood
#
# minor fixes carried over from SOAP2.py
#
# Revision 1.4  2004/12/13 19:03:00  ncq
# - inching close to code that I actually understand
#
# Revision 1.3  2004/12/07 21:54:56  ncq
# - add some comments on proposed plan
#
# Revision 1.2  2004/12/06 20:46:49  ncq
# - a bit of cleanup
#
# Revision 1.1  2004/12/06 20:36:48  ncq
# - starting to integrate soap2
#
#
#====================================================
# Taken from:
# Source: /cvsroot/gnumed/gnumed/gnumed/test-area/ian/SOAP2.py,v
# Id: SOAP2.py,v 1.8 2004/11/09 13:13:18 ihaywood Exp
#
# Revision 1.8	2004/11/09 13:13:18	 ihaywood
# Licence added
#
# Segfaults fixed.
# Demonstration listbox for multiple SOAP entries, I had intended to drop
# this into the gnumed client, will check what Carlos is doing
#
# Still have vanishing cursor problem when returning  from a popup, can't
# seem to get it back even after explicit SetFocus ()
#
# Revision 1.7	2004/11/09 11:20:59	 ncq
# - just silly cleanup
#
# Revision 1.6	2004/11/09 11:19:47	 ncq
# - if we know that parent of ResizingSTC must be
#	ResizingWindow we can test for it
# - added some CVS keywords
# - this should not be a physical replacement for the edit
#	area, just a logical one where people want to use it !
#	IOW we will keep gmEditArea around as it IS a good design !
#
#----------------------------------------------------------------
# revision 1.5
# date: 2004/11/09 02:05:20;  author: ihaywood;	 state: Exp;  lines: +106 -100
# crashes less often now, the one stickler is clicking on the
# auto-completion list causes a segfault.
#
# This is becoming a candidate replacement for cEditArea
#
# revision 1.4
# date: 2004/11/08 09:36:28;  author: ihaywood;	 state: Exp;  lines: +86 -77
# fixed the crashing bu proper use of wxSize.SetItemMinSize (when all else
# fails, read the docs ;-)
#
# revision 1.3
# date: 2004/11/08 07:07:29;  author: ihaywood;	 state: Exp;  lines: +108 -22
# more fun with semicolons
# popups too: having a lot of trouble with this, many segfaults.
#
# revision 1.2
# date: 2004/11/02 11:55:59;  author: ihaywood;	 state: Exp;  lines: +198 -19
# more feaures, including completion box (unfortunately we can't use the
# one included with StyledTextCtrl)
#
# revision 1.1
# date: 2004/10/24 13:01:15;  author: ihaywood;	 state: Exp;
# prototypical SOAP editor, secondary to Sebastian's comments:
#	- Now shrinks as well as grows boxes
#	- TAB moves to next box, Shift-TAB goes back
