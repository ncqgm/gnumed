"""GNUmed date input widget

All GNUmed date input should happen via classes in
this module.

@copyright: author(s)
"""
#==============================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL v2 or later (details at http://www.gnu.org)"

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
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers

_log = logging.getLogger('gm.ui')

#============================================================
#class cIntervalMatchProvider(gmMatchProvider.cMatchProvider):
#	"""Turns strings into candidate intervals."""
#	def __init__(self):
#
#		gmMatchProvider.cMatchProvider.__init__(self)
#
#		self.setThresholds(aPhrase = 1, aWord = 998, aSubstring = 999)
#		self.word_separators = None
##		self.ignored_chars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
#	#--------------------------------------------------------
#	# external API
#	#--------------------------------------------------------
#	#--------------------------------------------------------
#	# base class API
#	#--------------------------------------------------------
#	def getMatchesByPhrase(self, aFragment):
#		intv = gmDateTime.str2interval(str_interval = aFragment)
#
#		if intv is None:
#			return (False, [])
#
#		items = [{
#			'data': intv,
#			'field_label': gmDateTime.format_interval(intv, gmDateTime.acc_minutes),
#			'list_label': gmDateTime.format_interval(intv, gmDateTime.acc_minutes)
#		}]
#
#		return (True, items)
#	#--------------------------------------------------------
#	def getMatchesByWord(self, aFragment):
#		return self.getMatchesByPhrase(aFragment)
#	#--------------------------------------------------------
#	def getMatchesBySubstr(self, aFragment):
#		return self.getMatchesByPhrase(aFragment)
#	#--------------------------------------------------------
#	def getAllMatches(self):
#		matches = (False, [])
#		return matches

#============================================================
class cIntervalPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.phrase_separators = None
		self.display_accuracy = None
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _update_candidates_in_picklist(self, val):
		intv = gmDateTime.str2interval(str_interval = val)
		if intv is None:
			self._current_match_candidates = []
		else:
			self._current_match_candidates = [{
				'data': intv,
				'field_label': gmDateTime.format_interval(intv, gmDateTime.acc_minutes),
				'list_label': gmDateTime.format_interval(intv, gmDateTime.acc_minutes)
			}]
		self._picklist.SetItems(self._current_match_candidates)
	#---------------------------------------------------------
#	def _on_lose_focus(self, event):
#		# are we valid ?
#		if len(self._data) == 0:
#			self._set_data_to_first_match()
#
#		# let the base class do its thing
#		super(cIntervalPhraseWheel, self)._on_lose_focus(event)
	#--------------------------------------------------------
	def _picklist_item2display_string(self, item=None):
		intv = item['data']
		if intv is not None:
			return gmDateTime.format_interval (
				interval = intv,
				accuracy_wanted = self.display_accuracy
			)
		return item['field_label']
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		intv = self.GetData()
		if intv is None:
			return u''
		return gmDateTime.format_interval (
			interval = intv,
			accuracy_wanted = self.display_accuracy
		)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetValue(self, value):

		if isinstance(value, pyDT.timedelta):
			self.SetText(data = value, suppress_smarts = True)
			return

		if value is None:
			value = u''

		super(cIntervalPhraseWheel, self).SetValue(value)
	#--------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		if data is not None:
			if value.strip() == u'':
				value = gmDateTime.format_interval (
					interval = data,
					accuracy_wanted = self.display_accuracy
				)

		super(cIntervalPhraseWheel, self).SetText(value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is None:
			super(cIntervalPhraseWheel, self).SetText(u'', None)
			return

		value = gmDateTime.format_interval (
			interval = data,
			accuracy_wanted = self.display_accuracy
		)
		super(cIntervalPhraseWheel, self).SetText(value = value, data = data)
	#--------------------------------------------------------
	def GetData(self):
		if len(self._data) == 0:
			self._set_data_to_first_match()

		return super(cIntervalPhraseWheel, self).GetData()

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

		if len(matches) == 0:
			return (False, [])

		items = []
		for match in matches:
			if match['data'] is None:
				items.append ({
					'data': None,
					'field_label': match['label'],
					'list_label': match['label']
				})
				continue

			data = match['data'].replace (
				hour = 11,
				minute = 11,
				second = 11,
				microsecond = 111111
			)
			list_label = gmDateTime.pydt_strftime (
				data,
				format = '%A, %d. %B %Y (%x)',
				accuracy = gmDateTime.acc_days
			)
			items.append ({
				'data': data,
				'field_label': match['label'],
				'list_label': list_label
			})

		return (True, items)
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

#		# consider this:
#		dlg = cCalendarDatePickerDlg(None)
#		# FIXME: show below parent
#		dlg.CentreOnScreen()
#
#		if dlg.ShowModal() == wx.ID_OK:
#			date = dlg.cal.Date
#			if date is not None:
#				if date.IsValid():
#					date = gmDateTime.wxDate2py_dt(wxDate = date).replace (
#						hour = 11,
#						minute = 11,
#						second = 11,
#						microsecond = 111111
#					)
#					lbl = gmDateTime.pydt_strftime(date, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days)
#					matches = (True, [{'data': date, 'label': lbl}])
#		dlg.Destroy()
#
#		return matches

#============================================================
class cDateInputPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		self.matcher = cDateMatchProvider()
		self.phrase_separators = None

		self.static_tooltip_extra = _('<ALT-C/K>: pick from (c/k)alendar')
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
#	def __text2timestamp(self):
#
#		self._update_candidates_in_picklist(val = self.GetValue().strip())
#
#		if len(self._current_match_candidates) == 1:
#			return self._current_match_candidates[0]['data']
#
#		return None
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

		date = gmDateTime.wxDate2py_dt(wxDate = date).replace (
			hour = 11,
			minute = 11,
			second = 11,
			microsecond = 111111
		)
		val = gmDateTime.pydt_strftime(date, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days)
		self.SetText(value = val, data = date, suppress_smarts = True)
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		# no valid date yet ?
		if len(self._data) == 0:
			self._set_data_to_first_match()
			date = self.GetData()
			if date is not None:
				self.SetValue(gmDateTime.pydt_strftime(date, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days))

		# let the base class do its thing
		super(cDateInputPhraseWheel, self)._on_lose_focus(event)
	#--------------------------------------------------------
	def _picklist_item2display_string(self, item=None):
		data = item['data']
		if data is not None:
			return gmDateTime.pydt_strftime(data, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days)
		return item['field_label']
	#--------------------------------------------------------
	def _on_key_down(self, event):

		# <ALT-C> / <ALT-K> -> calendar
		if event.AltDown() is True:
			char = unichr(event.GetUnicodeKey())
			if char in u'ckCK':
				self.__pick_from_calendar()
				return

		super(cDateInputPhraseWheel, self)._on_key_down(event)
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if len(self._data) == 0:
			return u''

		date = self.GetData()
		# if match provider only provided completions
		# but not a full date with it
		if date is None:
			return u''

		return gmDateTime.pydt_strftime (
			date,
			format = '%A, %d. %B %Y (%x)',
			accuracy = gmDateTime.acc_days
		)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetValue(self, value):

		if isinstance(value, pyDT.datetime):
			date = value.replace (
				hour = 11,
				minute = 11,
				second = 11,
				microsecond = 111111
			)
			self.SetText(data = date, suppress_smarts = True)
			return

		if value is None:
			value = u''

		super(self.__class__, self).SetValue(value)
	#--------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		if data is not None:
			if isinstance(data, gmDateTime.cFuzzyTimestamp):
				data = data.timestamp.replace (
					hour = 11,
					minute = 11,
					second = 11,
					microsecond = 111111
				)
			if value.strip() == u'':
				value = gmDateTime.pydt_strftime(data, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days)

		super(self.__class__, self).SetText(value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is None:
			gmPhraseWheel.cPhraseWheel.SetText(self, u'', None)
			return
		self.SetText(data = data)
	#--------------------------------------------------------
	def GetData(self):
		if len(self._data) == 0:
			self._set_data_to_first_match()

		return super(self.__class__, self).GetData()
	#--------------------------------------------------------
	def is_valid_timestamp(self, allow_empty=True):
		if len(self._data) > 0:
			self.display_as_valid(True)
			return True

		if self.GetValue().strip() == u'':
			if allow_empty:
				self.display_as_valid(True)
				return True
			else:
				self.display_as_valid(False)
				return False

		# skip showing calendar on '*' from here
		if self.GetValue().strip() == u'*':
			self.display_as_valid(False)
			return False

		# try to auto-snap to first match
		self._set_data_to_first_match()
		if len(self._data) == 0:
			self.display_as_valid(False)
			return False

		date = self.GetData()
		self.SetValue(gmDateTime.pydt_strftime(date, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days))#, none_str = u'')
		self.display_as_valid(True)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_date(self):
		return self.GetData()

	def _set_date(self, date):
		raise AttributeError('._set_date not implemented')
#		val = gmDateTime.pydt_strftime(date, format = '%Y-%m-%d', accuracy = gmDateTime.acc_days)
#		self.data = date.replace (
#			hour = 11,
#			minute = 11,
#			second = 11,
#			microsecond = 111111
#		)

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
		matches = gmDateTime.str2fuzzy_timestamp_matches(aFragment.strip())

		if len(matches) == 0:
			return (False, [])

		items = []
		for match in matches:
			items.append ({
				'data': match['data'],
				'field_label': match['label'],
				'list_label': match['label']
			})

		return (True, items)
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
		return (False, [])

#==================================================
class cFuzzyTimestampInput(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		self.matcher = cMatchProvider_FuzzyTimestamp()
		self.phrase_separators = None
		self.selection_only = True
		self.selection_only_error_msg = _('Cannot interpret input as timestamp.')
		self.display_accuracy = None
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __text2timestamp(self, val=None):
		if val is None:
			val = self.GetValue()
		val = val.strip()
		if val == u'':
			return None
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
			date = self.__text2timestamp()
			if date is not None:
				self.SetValue(value = date.format_accurately(accuracy = self.display_accuracy))
				self.data = date

		# let the base class do its thing
		gmPhraseWheel.cPhraseWheel._on_lose_focus(self, event)
	#--------------------------------------------------------
	def _picklist_item2display_string(self, item=None):
		data = item['data']
		if data is not None:
			return data.format_accurately(accuracy = self.display_accuracy)
		return item['field_label']
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetText(self, value=u'', data=None, suppress_smarts=False):

		if data is not None:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			if value.strip() == u'':
				value = data.format_accurately(accuracy = self.display_accuracy)

		gmPhraseWheel.cPhraseWheel.SetText(self, value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is None:
			gmPhraseWheel.cPhraseWheel.SetText(self, u'', None)
		else:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			gmPhraseWheel.cPhraseWheel.SetText(self, value = data.format_accurately(accuracy = self.display_accuracy), data = data)
	#--------------------------------------------------------
	def is_valid_timestamp(self, empty_is_valid=True):
		if self.GetData() is not None:
			return True

		# skip empty value
		if self.GetValue().strip() == u'':
			if empty_is_valid:
				return True
			return False

		date = self.__text2timestamp()
		if date is None:
			return False

		self.SetText (
			value = date.format_accurately(accuracy = self.display_accuracy),
			data = date,
			suppress_smarts = True
		)

		return True
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
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
			val = raw_input('Enter date fragment ("exit" to quit): ')
			found, matches = mp.getMatches(aFragment=val)
			for match in matches:
				#print match
				print match['label']
				print match['data']
				print "---------------"
	#--------------------------------------------------------
	def test_fuzzy_picker():
		app = wx.PyWidgetTester(size = (300, 40))
		app.SetWidget(cFuzzyTimestampInput, id=-1, size=(180,20), pos=(10,20))
		app.MainLoop()
	#--------------------------------------------------------
	def test_picker():
		app = wx.PyWidgetTester(size = (300, 40))
		app.SetWidget(cDateInputPhraseWheel, id=-1, size=(180,20), pos=(10,20))
		app.MainLoop()
	#--------------------------------------------------------
	#test_cli()
	#test_fuzzy_picker()
	test_picker()

#==================================================
