"""GNUmed date input widget

All GNUmed date input should happen via classes in
this module. Initially this is just a plain text box
but using this throughout GNUmed will allow us to
transparently add features.

@copyright: author(s)
"""
#==============================================================================
__version__ = "$Revision: 1.66 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

import re, string, sys, time, datetime as pyDT, logging


import mx.DateTime as mxDT, wx


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmMatchProvider, gmDateTime
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers

_log = logging.getLogger('gm.ui')

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
		#matches = gmDateTime.str2fuzzy_timestamp_matches(str2parse=val)
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

	def __init__(self, *args, **kwargs):

		wx.DatePickerCtrl.__init__(self,*args,**kwargs)
		#super(cDateInputCtrl, self).__init__(*args, **kwargs)
		#self.Bind(wx.EVT_DATE_CHANGED, self.__on_date_changed, self)
	#----------------------------------------------
	def SetValue(self, value):
		"""Set either datetime.datetime or wx.DateTime"""

		if isinstance(value, (pyDT.date, pyDT.datetime)):
			wxvalue = wx.DateTime()
			wxvalue.Set(year = value.year, month = value.month-1, day = value.day)
			value = wxvalue

		elif value is None:
			value = wx.DefaultDateTime

		wx.DatePickerCtrl.SetValue(self, value)
	#----------------------------------------------
	def GetValue(self, as_pydt=False):
		"""Returns datetime.datetime values"""

		value = wx.DatePickerCtrl.GetValue(self)

		if value is None:
			return None

		# manage null dates (useful when wx.DP_ALLOWNONE is set)
		if not value.IsValid():
			return None

		self.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
		self.Refresh()

		if not as_pydt:
			return value

		return gmDateTime.wxDate2py_dt(value)
	#----------------------------------------------
	# def convenience wrapper
	#----------------------------------------------
	def is_valid_timestamp(self, allow_none=True):
		val = self.GetValue()

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

	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		from Gnumed.pycommon import gmI18N
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
# - free text input: start string with "
#==================================================
