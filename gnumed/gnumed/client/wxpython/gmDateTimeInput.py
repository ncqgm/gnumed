# -*- coding: iso-8859-1 -*-
"""GNUmed date input widget

All GNUmed date input should happen via classes in
this module. Initially this is just a plain text box
but using this throughout GNUmed will allow us to
transparently add features.

@copyright: author(s)
"""
#==============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDateTimeInput.py,v $
# $Id: gmDateTimeInput.py,v 1.49 2006-12-21 10:54:18 ncq Exp $
__version__ = "$Revision: 1.49 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

import re, string, sys, time

import mx.DateTime as mxDT, wx

# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmMatchProvider, gmExceptions, gmI18N, gmFuzzyTimestamp
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers

_log = gmLog.gmDefLog

#============================================================
class cMatchProvider_FuzzyTimestamp(gmMatchProvider.cMatchProvider):
	def __init__(self):
		self.__allow_past = 1
		self.__shifting_base = None
		self.set_single_character_triggers()
		self.set_offset_chars()
		gmMatchProvider.cMatchProvider.__init__(self)
		self.setThresholds(aPhrase = 1, aWord = 998, aSubstring = 999)
		self.setWordSeparators('xxx_do_not_separate_words_xxx')
#		self.setIgnoredChars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_single_character_triggers(self, triggers = 'ndmy'):
		"""Set trigger characters.

		Default is 'ndmy':
			n - now
			d - toDay
			m - toMorrow	Someone please suggest a synonym !
			y - yesterday

		This also defines the significance of the order of the characters.
		"""
		self.__single_char_triggers = triggers[:4].lower()
	#--------------------------------------------------------
	def set_offset_chars(self, offset_chars = 'hdwmy'):
		"""Set offset characters.

		Default is 'hdwm':
			h - hours
			d - days
			w - weeks
			m - months
			y - years

		This also defines the significance of the order of the characters.
		"""
		self.__offset_chars = offset_chars[:5].lower()
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
		matches = gmFuzzyTimestamp.str2fuzzy_timestamp_matches(aFragment.strip())
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

		# setup custom match provider
		kwargs['aMatchProvider'] = cMatchProvider_FuzzyTimestamp()

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.allow_multiple_phrases(False)
		self.selection_only = False
		self.set_snap_to_first_match(True)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __text2timestamp(self, val=None):

		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if val is None:
			val = self.GetValue().strip()

		# skip empty value
		if val == '':
			return None

		matches = gmFuzzyTimestamp.str2fuzzy_timestamp_matches(str_timestamp=val)
		if len(matches) == 0:
			self.SetBackgroundColour('pink')
			msg = _('Cannot parse <%s> into proper timestamp.') % val
			wx.CallAfter(gmGuiHelpers.gm_statustext, msg)
			return None

		if len(matches) > 1:
			msg = _('Warning ! More than one timestamp possible for [%s]. Choosing first one.') % val
			wx.CallAfter(gmGuiHelpers.gm_statustext, msg)

		return matches[0]
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		match = self.__text2timestamp()
		if match is None:
			self.data = None
		else:
			wx.TextCtrl.SetValue(self, match['label'])
			self.data = match['data']
		gmPhraseWheel.cPhraseWheel._on_lose_focus(self, event)
	#--------------------------------------------------------
	def _calc_display_string(self):
		data = self._picklist.GetSelectedItemData()
		if data is None:
			return self.GetValue()
		return data.format_accurately()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetData(self, data=None):
		self.data = data
		if data is not None:
			gmPhraseWheel.cPhraseWheel.SetValue(self, self.data.format_accurately())
		else:
			gmPhraseWheel.cPhraseWheel.SetValue(self, '')
	#--------------------------------------------------------
	def SetValue(self, val, data=None):
		gmPhraseWheel.cPhraseWheel.SetValue(self, val, data=data)
		if data is None:
			match = self.__text2timestamp()
			if match is not None:
				self.data = match['data']
	#--------------------------------------------------------
	def is_valid_timestamp(self):
		if self.__text2timestamp() is None:
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
	#----------------------------------------------
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':
	#----------------------------------------------------
	def test_cli():
		mp = cMatchProvider_FuzzyTimestamp()
		mp.setWordSeparators('xxx_do_not_separate_words_xxx')
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
	gmI18N.activate_locale()
	gmI18N.install_domain(text_domain='gnumed')
#	test_cli()
	test_gui()

#==================================================
# - free text input: start string with "
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.49  2006-12-21 10:54:18  ncq
# - add SetData
#
# Revision 1.48  2006/11/27 23:14:33  ncq
# - remove prints
#
# Revision 1.47  2006/11/27 23:04:49  ncq
# - factor out UI-independant code
#
# Revision 1.46  2006/11/27 12:39:00  ncq
# - remove useless check
#
# Revision 1.45  2006/11/26 22:38:14  ncq
# - recognize 1953 as meaning that year :-)
#
# Revision 1.44  2006/11/24 14:19:43  ncq
# - variable name fix in __text2timestamp
#
# Revision 1.43  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.42  2006/11/19 11:11:57  ncq
# - fix wrong return value
#
# Revision 1.41  2006/07/19 20:29:50  ncq
# - import cleanup
#
# Revision 1.40  2006/07/01 13:12:32  ncq
# - improve test harness
#
# Revision 1.39  2006/06/15 15:35:30  ncq
# - better error handling
#
# Revision 1.38  2006/06/05 21:30:08  ncq
# - add single-dot expander so German 23. expands to 23rd this month this year
# - add is_valid_timestamp() to external API so patient wizard can use it
#
# Revision 1.37  2006/06/04 21:50:32  ncq
# - cleanup
#
# Revision 1.36  2006/06/02 13:17:50  ncq
# - add configurable offset chars for i18n
# - various cleanups and optimizations
# - fix __explicit_offset to use proper fuzzy timestamp
# - __validate() -> __text2timestamp() and smarten up
#
# Revision 1.35  2006/06/02 10:12:09  ncq
# - cleanup
# - add more fragment expanders
#
# Revision 1.34  2006/05/24 10:35:38  ncq
# - better named match provider
#
# Revision 1.33  2006/05/24 10:12:37  ncq
# - cleanup
# - timestamp match provider:
#   - use fuzzy timestamp
#   - i18n()ize single character triggers
#   - improve phrasewheel strings
# - fuzzy timestamp phrasewheel
#   - a lot of cleanup
# - proper test code
#
# Revision 1.32  2006/05/20 18:37:10  ncq
# - cleanup
#
# Revision 1.31  2006/05/12 12:08:51  ncq
# - comment out proposed fix for unicode problems
#
# Revision 1.30  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.29  2005/09/28 15:57:47  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.28  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.27  2005/09/25 01:13:06  ihaywood
# use a nicer way of discovering non-Unicode wxPython builds
# I resisted the temptation to use "if os.environ['USER'] == 'ncq':"
#
# Revision 1.26  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.25  2005/08/22 13:03:46  ncq
# - set bounds on "day of month" calculations
#
# Revision 1.24  2005/07/31 16:22:25  ncq
# - need to import "time"
#
# Revision 1.23  2005/07/31 16:04:19  ncq
# - on some platforms, notably MS Windows mx.DateTime does not support
#   strptime(), hence use time.strptime()
#
# Revision 1.22  2005/07/31 15:32:50  ncq
# - cleanup
#
# Revision 1.21  2005/07/31 15:23:40  ncq
# - fixed long-standing validation logic bug
# - logging is best done using proper syntax, too
#
# Revision 1.20  2005/07/27 15:17:06  ncq
# - properly catch date input error such that we
#   may find the bug on Windows
#
# Revision 1.19  2005/06/08 22:01:42  cfmoro
# Avoid validating when empty date
#
# Revision 1.18  2005/06/08 21:19:50  cfmoro
# Crash fix
#
# Revision 1.17  2005/06/04 09:55:32  ncq
# - also call parent class _on_lose_focus so we don't loose
#   callbacks set by other people
#
# Revision 1.16  2005/06/03 00:54:33  cfmoro
# Validte date in SetValue
#
# Revision 1.15  2005/06/03 00:36:54  cfmoro
# Validate date on setValue
#
# Revision 1.14  2005/06/02 23:28:54  cfmoro
# Date validation
#
# Revision 1.13  2005/04/25 17:11:33  ncq
# - set encoding for file
#
# Revision 1.12  2005/04/24 15:05:22  ncq
# - use gmI18N properly
#
# Revision 1.11  2004/12/23 16:20:15  ncq
# - add licence
#
# Revision 1.10  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.9  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.8  2004/02/25 09:46:21  ncq
# - import from pycommon now, not python-common
#
# Revision 1.7  2003/11/05 22:21:06  sjtan
#
# let's gmDateInput specify id_callback in constructor list.
#
# Revision 1.6  2003/11/04 10:35:23  ihaywood
# match providers in gmDemographicRecord
#
# Revision 1.5  2003/10/06 17:49:40  ncq
# - remove dependancy on gmI18N on standalone test run
#
# Revision 1.4  2003/10/02 20:51:12  ncq
# - add alt-XX shortcuts, move __* to _*
#
# Revision 1.3  2003/09/30 18:47:47  ncq
# - converted date time input field into phrase wheel descendant
#
# Revision 1.2  2003/08/10 00:57:15  ncq
# - add TODO item
#
# Revision 1.1  2003/05/23 14:05:01  ncq
# - first implementation
#
