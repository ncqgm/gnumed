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
# $Id: gmDateTimeInput.py,v 1.62 2008-06-18 15:46:49 ncq Exp $
__version__ = "$Revision: 1.62 $"
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

#		# now valid ?
#		if self.data is not None:
#			# yes, so set text from the data (to make sure we can re-parse it later if need be)
#			gmPhraseWheel.cPhraseWheel.SetText(self, value=self.data.format_accurately(), data=self.data)

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
#		if data is None:
#			data = self.__text2timestamp(val=value)

		if data is not None:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			if value.strip() == u'':
				value = data.format_accurately()

		gmPhraseWheel.cPhraseWheel.SetText(self, value = value, data = data, suppress_smarts = suppress_smarts)
	#--------------------------------------------------------
	def SetData(self, data=None):
		if data is not None:
			if isinstance(data, pyDT.datetime):
				data = gmDateTime.cFuzzyTimestamp(timestamp=data)
			gmPhraseWheel.cPhraseWheel.SetText(self, value = data.format_accurately(), data = data)
		else:
			gmPhraseWheel.cPhraseWheel.SetText(self, u'', None)
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
		test_cli()
#		test_gui()

#==================================================
# - free text input: start string with "
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.62  2008-06-18 15:46:49  ncq
# - cleanup: offset/trigger chars are handled in the str 2 timestamp function directly
#
# Revision 1.61  2008/06/15 20:33:55  ncq
# - adjust to match provider properties
#
# Revision 1.60  2008/05/07 15:20:36  ncq
# - support suppress smarts in SetText
#
# Revision 1.59  2008/04/02 10:22:03  ncq
# - optionalize test suite running
#
# Revision 1.58  2008/03/05 22:30:13  ncq
# - new style logging
#
# Revision 1.57  2007/07/10 20:28:36  ncq
# - consolidate install_domain() args
#
# Revision 1.56  2007/06/15 10:24:53  ncq
# - adjust to change function signature
#
# Revision 1.55  2007/04/02 18:39:52  ncq
# - gmFuzzyTimestamp -> gmDateTime
#
# Revision 1.54  2007/03/18 14:01:52  ncq
# - re-add lost 1.54
#
# Revision 1.54  2007/03/12 12:26:15  ncq
# - allow SetData/SetText to take datetime.datetime instances
#
# Revision 1.53  2007/02/16 12:51:07  ncq
# - fix is_valid_timestamp()
#
# Revision 1.52  2007/02/16 10:23:44  ncq
# - make it selection_only and set error message
# - u''ify more
# - delegate more work to standard phrasewheel code
# - add SetText()
# - fix _picklist_selection2display_string()
# - need to activate locale in test suite
#
# Revision 1.51  2007/02/05 12:15:23  ncq
# - no more aMatchProvider/selection_only in cPhraseWheel.__init__()
#
# Revision 1.50  2007/02/04 15:51:00  ncq
# - no more snap_to_first_match
# - use SetText()
# - explicetly unset phrase separators
#
# Revision 1.49  2006/12/21 10:54:18  ncq
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
