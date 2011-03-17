"""GNUmed date input widget

All GNUmed date input should happen via classes in
this module.

@copyright: author(s)
"""
#==============================================================================
__version__ = "$Revision: 1.66 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

# standard libary
import re, string, sys, time, datetime as pyDT, logging


# 3rd party
import mx.DateTime as mxDT
import wx
import wx.calendar


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers

_log = logging.getLogger('gm.ui')

#============================================================
class cCalendarDatePickerDlg(wx.Dialog):
	"""Shows a calendar control from which the user can pick a date."""
	def __init__(self, parent):

		wx.Dialog.__init__(self, parent, title = _('Pick a date ...'))
		panel = wx.Panel(self, -1)

		sizer = wx.BoxSizer(wx.VERTICAL)
		panel.SetSizer(sizer)

		cal = wx.calendar.CalendarCtrl(panel)

		if sys.platform != 'win32':
			# gtk truncates the year - this fixes it
			w, h = cal.Size
			cal.Size = (w+25, h)
			cal.MinSize = cal.Size

		sizer.Add(cal, 0)

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.Add((0, 0), 1)
		btn_ok = wx.Button(panel, wx.ID_OK)
		btn_ok.SetDefault()
		button_sizer.Add(btn_ok, 0, wx.ALL, 2)
		button_sizer.Add((0, 0), 1)
		btn_can = wx.Button(panel, wx.ID_CANCEL)
		button_sizer.Add(btn_can, 0, wx.ALL, 2)
		button_sizer.Add((0, 0), 1)
		sizer.Add(button_sizer, 1, wx.EXPAND | wx.ALL, 10)
		sizer.Fit(panel)
		self.ClientSize = panel.Size

		cal.Bind(wx.EVT_KEY_DOWN, self.__on_key_down)
		cal.SetFocus()
		self.cal = cal
	#-----------------------------------------------------------
	def __on_key_down(self, evt):
		code = evt.KeyCode
		if code == wx.WXK_TAB:
			self.cal.Navigate()
		elif code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.EndModal(wx.ID_OK)
		elif code == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
		else:
			evt.Skip()

#============================================================
class cDateMatchProvider(gmMatchProvider.cMatchProvider):
	"""Turns strings into candidate dates.

	Matching on "all" (*, '') will pop up a calendar :-)
	"""
	def __init__(self):

		gmMatchProvider.cMatchProvider.__init__(self)

		self.setThresholds(aPhrase = 1, aWord = 998, aSubstring = 999)
		self.word_separators = None
#		self.ignored_chars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	#--------------------------------------------------------
	# base class API
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		matches = gmDateTime.str2pydt_matches(str2parse = aFragment.strip())
		if len(matches) > 0:
			return (True, matches)
		else:
			return (False, [])
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""

		matches = (False, [])
		return matches

		dlg = cCalendarDatePickerDlg(None)
		# FIXME: show below parent
		dlg.CentreOnScreen()

		if dlg.ShowModal() == wx.ID_OK:
			date = dlg.cal.Date
			if date is not None:
				if date.IsValid():
					date = gmDateTime.wxDate2py_dt(wxDate = date)
					matches = (True, [{'data': date, 'label': date.strftime('%Y-%m-%d')}])
		dlg.Destroy()

		return matches
#============================================================
class cDateInputPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		self.matcher = cDateMatchProvider()
		self.phrase_separators = None

		self.static_tooltip_extra = _('<ALT-C>: pick from Calendar')
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __text2timestamp(self, val=None):

		if val is None:
			val = self.GetValue().strip()

		success, matches = self.matcher.getMatchesByPhrase(val)

		if len(matches) == 1:
			return matches[0]['data']

		return None
	#--------------------------------------------------------
	def __pick_from_calendar(self):
		dlg = cCalendarDatePickerDlg(self)
		# FIXME: show below parent
		dlg.CentreOnScreen()
		decision = dlg.ShowModal()
		date = dlg.cal.Date
		dlg.Destroy()

		if decision != wx.ID_OK:
			return

		if date is None:
			return

		if not date.IsValid():
			return

		date = gmDateTime.wxDate2py_dt(wxDate = date)
		self.SetText(value = date.strftime('%Y-%m-%d'), data = date, suppress_smarts = True)
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		# are we valid ?
		if self.data is None:
			# no, so try
			self.data = self.__text2timestamp()

		# let the base class do its thing
		super(self.__class__, self)._on_lose_focus(event)
	#--------------------------------------------------------
	def _picklist_selection2display_string(self):
		data = self._picklist.GetSelectedItemData()
		if data is not None:
			return data.strftime('%Y-%m-%d')
		return self._picklist.get_selected_item_label()
	#--------------------------------------------------------
	def _on_key_down(self, event):

		# <ALT-C> / <ALT-K> -> calendar
		if event.AltDown() is True:
			char = unichr(event.GetUnicodeKey())
			if char in u'ckCK':
				self.__pick_from_calendar()
				return

		super(self.__class__, self)._on_key_down(event)
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if self.data is None:
			return u''

		return self.data.strftime('%A, %d. %B %Y (%x)').decode(gmI18N.get_encoding())
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetValue(self, value):

		if isinstance(value, pyDT.datetime):
			self.SetText(data = value, suppress_smarts = True)
			return

		if value is None:
			value = u''

		super(self.__class__, self).SetValue(value)
	#--------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		if data is not None:
			if isinstance(data, gmDateTime.cFuzzyTimestamp):
				data = data.timestamp
			if value.strip() == u'':
				value = data.strftime('%Y-%m-%d')

		super(self.__class__, self).SetText(value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is None:
			gmPhraseWheel.cPhraseWheel.SetText(self, u'', None)
		else:
			if isinstance(data, gmDateTime.cFuzzyTimestamp):
				data = data.timestamp
			super(self.__class__, self).SetText(value = data.strftime('%Y-%m-%d'), data = data)
	#--------------------------------------------------------
	def GetData(self):
		if self.data is None:
			self.data = self.__text2timestamp()

		return super(self.__class__, self).GetData()
	#--------------------------------------------------------
	def is_valid_timestamp(self, empty_is_valid=True):
		if self.data is not None:
			self.display_as_valid(True)
			return True

		if self.GetValue().strip() == u'':
			if empty_is_valid:
				self.display_as_valid(True)
				return True
			else:
				self.display_as_valid(False)
				return False

		# skip showing calendar on '*'
		if self.GetValue().strip() == u'*':
			self.display_as_valid(False)
			return False

		self.data = self.__text2timestamp()
		if self.data is None:
			self.display_as_valid(False)
			return False

		self.display_as_valid(True)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_date(self):
		return self.data

	def _set_date(self, date):
		self.data = date

	date = property(_get_date, _set_date)
#============================================================
class cMatchProvider_FuzzyTimestamp(gmMatchProvider.cMatchProvider):
	def __init__(self):
		self.__allow_past = 1
		self.__shifting_base = None

		gmMatchProvider.cMatchProvider.__init__(self)

		self.setThresholds(aPhrase = 1, aWord = 998, aSubstring = 999)
		self.word_separators = None
#		self.ignored_chars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	#--------------------------------------------------------
	# base class API
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		self.__now = mxDT.now()
		matches = gmDateTime.str2fuzzy_timestamp_matches(aFragment.strip())
		if len(matches) > 0:
			return (True, matches)
		else:
			return (False, [])
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		# FIXME: popup calendar to pick from
		return (False, [])
#==================================================
class cFuzzyTimestampInput(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		self.matcher = cMatchProvider_FuzzyTimestamp()
		self.phrase_separators = None
		self.selection_only = True
		self.selection_only_error_msg = _('Cannot interpret input as timestamp.')
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __text2timestamp(self, val=None):

		if val is None:
			val = self.GetValue().strip()

		success, matches = self.matcher.getMatchesByPhrase(val)
		if len(matches) == 1:
			return matches[0]['data']

		return None
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		# are we valid ?
		if self.data is None:
			# no, so try
			self.data = self.__text2timestamp()

		# let the base class do its thing
		gmPhraseWheel.cPhraseWheel._on_lose_focus(self, event)
	#--------------------------------------------------------
	def _picklist_selection2display_string(self):
		data = self._picklist.GetSelectedItemData()
		if data is not None:
			return data.format_accurately()
		return self._picklist.get_selected_item_label()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		if data is not None:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			if value.strip() == u'':
				value = data.format_accurately()

		gmPhraseWheel.cPhraseWheel.SetText(self, value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is None:
			gmPhraseWheel.cPhraseWheel.SetText(self, u'', None)
		else:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			gmPhraseWheel.cPhraseWheel.SetText(self, value = data.format_accurately(), data = data)
	#--------------------------------------------------------
	def is_valid_timestamp(self):
		if self.data is not None:
			return True

		# skip empty value
		if self.GetValue().strip() == u'':
			return True

		self.data = self.__text2timestamp()
		if self.data is None:
			return False

		return True
#==================================================
class cTimeInput(wx.TextCtrl):
	def __init__(self, parent, *args, **kwargs):
		if len(args) < 2:
			if not kwargs.has_key('value'):
				kwargs['value'] = _('enter time here')
		wx.TextCtrl.__init__(
			self,
			parent,
			*args,
			**kwargs
		)
#==================================================
class cDateInputCtrl(wx.DatePickerCtrl):

	#----------------------------------------------
	def SetValue(self, value):
		"""Set either datetime.datetime or wx.DateTime"""

		if isinstance(value, (pyDT.date, pyDT.datetime)):
			value = gmDateTime.py_dt2wxDate(py_dt = value, wx = wx)

		elif value is None:
			value = wx.DefaultDateTime

		wx.DatePickerCtrl.SetValue(self, value)
	#----------------------------------------------
	def GetValue(self, as_pydt=False, invalid_as_none=False):
		"""Returns datetime.datetime values"""

		# datepicker can fail to pick up user changes by keyboard until
		# it has lost focus, so do that but also set the focus back to us,
		# now, this is a side-effect (after .GetValue focus will be
		# here) but at least it is predictable ...
		self.Navigate()
		self.SetFocus()
		value = wx.DatePickerCtrl.GetValue(self)

		if value is None:
			return None

		# manage null dates (useful when wx.DP_ALLOWNONE is set)
		if not value.IsValid():
			if invalid_as_none:
				return None
			else:
				return value

		self.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		self.Refresh()

		if not as_pydt:
			return value

		return gmDateTime.wxDate2py_dt(value)
	#----------------------------------------------
	# def convenience wrapper
	#----------------------------------------------
	def is_valid_timestamp(self, allow_none=True, invalid_as_none=False):
		val = self.GetValue(as_pydt = False, invalid_as_none = invalid_as_none)

		if val is None:
			if allow_none:
				valid = True
			else:
				valid = False
		else:
			valid = val.IsValid()

		if valid:
			self.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		else:
			self.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)

		self.Refresh()
		return valid
	#----------------------------------------------
	def get_pydt(self):
		return self.GetValue(as_pydt = True)
	#----------------------------------------------
	def display_as_valid(self, valid=True):
		if valid is True:
			self.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		else:
			self.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
		self.Refresh()
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[2] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	gmDateTime.init()

	#----------------------------------------------------
	def test_cli():
		mp = cMatchProvider_FuzzyTimestamp()
		mp.word_separators = None
		mp.setThresholds(aWord = 998, aSubstring = 999)
		val = None
		while val != 'exit':
			print "************************************"
			val = raw_input('Enter date fragment: ')
			found, matches = mp.getMatches(aFragment=val)
			for match in matches:
				print match['label']
				print match['data']
				print "---------------"
	#--------------------------------------------------------
	def test_gui():
		app = wx.PyWidgetTester(size = (200, 300))
		app.SetWidget(cFuzzyTimestampInput, id=-1, size=(180,20), pos=(10,20))
		app.MainLoop()
	#--------------------------------------------------------
	def test_picker():
		app = wx.PyWidgetTester(size = (200, 300))
		app.SetWidget(cDateInputCtrl, id=-1, size=(180,20), pos=(10,20))
		app.MainLoop()
	#--------------------------------------------------------
	#test_cli()
	#test_gui()
	test_picker()

#==================================================
