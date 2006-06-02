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
# $Id: gmDateTimeInput.py,v 1.36 2006-06-02 13:17:50 ncq Exp $
__version__ = "$Revision: 1.36 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

import re, string, sys, time

import mx.DateTime as mxDT
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmMatchProvider, gmExceptions, gmI18N, gmFuzzyTimestamp
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog

month_length = {
	1: 31,
	2: 28,		# FIXME: make leap year aware
	3: 31,
	4: 30,
	5: 31,
	6: 30,
	7: 31,
	8: 31,
	9: 30,
	10: 31,
	11: 30,
	12: 31
}

#============================================================
class cMatchProvider_FuzzyTimestamp(gmMatchProvider.cMatchProvider):
	def __init__(self):
		self.__allow_past = 1 
		self.__shifting_base = None
		self.__expanders = []
		self.__expanders.append(self.__numbers_only)
		self.__expanders.append(self.__single_char)
		self.__expanders.append(self.__explicit_offset)
		self.__expanders.append(self.__single_slash)
		self.set_single_character_triggers()
		self.set_offset_chars()
		gmMatchProvider.cMatchProvider.__init__(self)
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
		aFragment = aFragment.strip()
		matches = []
		for expander in self.__expanders:
			items = expander(aFragment)
			if items is not None:
				matches.extend(items)
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
		return None
	#--------------------------------------------------------
	# date fragment expanders
	#--------------------------------------------------------
	def __single_slash(self, aFragment):
		"""Expand fragments containt a single slash.

		"5/"
			- 2005/					(2000 - 2025)
			- 1995/					(1990 - 1999)
			- Mai/current year
			- Mai/next year
			- Mai/last year
			- Mai/200x
			- Mai/20xx
			- Mai/199x
			- Mai/198x
			- Mai/197x
			- Mai/19xx
		"""

		if not re.match("^\d{1,2}/{1}$", aFragment):
			return None
		val = int(aFragment.replace('/', ''))

		matches = []

		if val < 100 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s/' % (val + 1900)
			})

		if val < 26 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s/' % (val + 2000)
			})

		if val < 10 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s/' % (val + 1990)
			})

		if val < 13 and val > 0:
			matches.append ({
				'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = self.__now, accuracy = gmFuzzyTimestamp.acc_months),
				'label': '%.2d/%s' % (val, self.__now.year)
			})
			ts = self.__now + mxDT.RelativeDateTime(years = 1)
			matches.append ({
				'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = ts, accuracy = gmFuzzyTimestamp.acc_months),
				'label': '%.2d/%s' % (val, ts.year)
			})
			ts = self.__now + mxDT.RelativeDateTime(years = -1)
			matches.append ({
				'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = ts, accuracy = gmFuzzyTimestamp.acc_months),
				'label': '%.2d/%s' % (val, ts.year)
			})
			matches.append ({
				'data': None,
				'label': '%.2d/200' % val
			})
			matches.append ({
				'data': None,
				'label': '%.2d/20' % val
			})
			matches.append ({
				'data': None,
				'label': '%.2d/199' % val
			})
			matches.append ({
				'data': None,
				'label': '%.2d/198' % val
			})
			matches.append ({
				'data': None,
				'label': '%.2d/197' % val
			})
			matches.append ({
				'data': None,
				'label': '%.2d/19' % val
			})

		return matches
	#--------------------------------------------------------
	def __numbers_only(self, aFragment):
		"""This matches on single numbers.

		Spaces or tabs are discarded.
		"""
		if not re.match("^\d+$", aFragment):
			return None
		val = int(aFragment)

		matches = []

		# day X of this month
		if val <= month_length[self.__now.month]:
			ts = self.__now + mxDT.RelativeDateTime(day = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%d. of %s (this month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
			}
			matches.append(tmp)

		# day X of next month
		if val <= month_length[(self.__now + mxDT.RelativeDateTime(months = 1)).month]:
			ts = self.__now + mxDT.RelativeDateTime(months = 1, day = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%d. of %s (next month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
			}
			matches.append(tmp)

		# day X of last month
		if val <= month_length[(self.__now + mxDT.RelativeDateTime(months = -1)).month]:
			ts = self.__now + mxDT.RelativeDateTime(months = -1, day = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%d. of %s (last month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
			}
			matches.append(tmp)

		# X days from now
		if val <= 400:				# more than a year ahead in days ?? nah !
			ts = self.__now + mxDT.RelativeDateTime(days = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts
			)
			tmp = {
				'data': target_date,
				'label': _('in %d day(s) - %s') % (val, target_date.timestamp.strftime('%A, %x'))
			}
			matches.append(tmp)

		# X weeks from now
		if val <= 50:				# pregnancy takes about 40 weeks :-)
			ts = self.__now + mxDT.RelativeDateTime(weeks = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts
			)
			tmp = {
				'data': target_date,
				'label': _('in %d week(s) - %s') % (val, target_date.timestamp.strftime('%A, %x'))
			}
			matches.append(tmp)

		# month X of ...
		if val < 13:
			# ... this year
			ts = self.__now + mxDT.RelativeDateTime(month = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_months
			)
			tmp = {
				'data': target_date,
				'label': _('%s (%s this year)') % (target_date, ts.strftime('%B'))
			}
			matches.append(tmp)

			# ... next year
			ts = self.__now + mxDT.RelativeDateTime(years = 1, month = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_months
			)
			tmp = {
				'data': target_date,
				'label': _('%s (%s next year)') % (target_date, ts.strftime('%B'))
			}
			matches.append(tmp)

			# ... last year
			ts = self.__now + mxDT.RelativeDateTime(years = -1, month = val)
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_months
			)
			tmp = {
				'data': target_date,
				'label': _('%s (%s last year)') % (target_date, ts.strftime('%B'))
			}
			matches.append(tmp)

			# fragment expansion
			matches.append ({
				'data': None,
				'label': '%s/200' % val
			})
			matches.append ({
				'data': None,
				'label': '%s/199' % val
			})
			matches.append ({
				'data': None,
				'label': '%s/198' % val
			})
			matches.append ({
				'data': None,
				'label': '%s/19' % val
			})

		# day X of ...
		if val < 8:
			# ... this week
			ts = self.__now + mxDT.RelativeDateTime(weekday = (val-1, 0))
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%s this week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
			}
			matches.append(tmp)

			# ... next week
			ts = self.__now + mxDT.RelativeDateTime(weeks = +1, weekday = (val-1, 0))
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%s next week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
			}
			matches.append(tmp)

			# ... last week
			ts = self.__now + mxDT.RelativeDateTime(weeks = -1, weekday = (val-1, 0))
			target_date = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = ts,
				accuracy = gmFuzzyTimestamp.acc_days
			)
			tmp = {
				'data': target_date,
				'label': _('%s last week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
			}
			matches.append(tmp)

		if val < 100:
			matches.append ({
				'data': None,
				'label': '%s/' % (1900 + val)
			})

		if val == 200:
			tmp = {
				'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = self.__now, accuracy = gmFuzzyTimestamp.acc_days),
				'label': '%s' % target_date
			}
			matches.append(tmp)
			matches.append ({
				'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = self.__now, accuracy = gmFuzzyTimestamp.acc_months),
				'label': '%s/%.2d' % (self.__now.year, self.__now.month)
			})
			matches.append ({
				'data': None,
				'label': '%s/' % self.__now.year
			})
			matches.append ({
				'data': None,
				'label': '%s/' % (self.__now.year + 1)
			})
			matches.append ({
				'data': None,
				'label': '%s/' % (self.__now.year - 1)
			})

		if val < 200 and val >= 190:
			for i in range(10):
				matches.append ({
					'data': None,
					'label': '%s%s/' % (val, i)
				})

		return matches
	#--------------------------------------------------------
	def __single_char(self, aFragment):
		"""This matches on single characters.

		Spaces and tabs are discarded."""

		if not re.match('^[%s]$' % self.__single_char_triggers, aFragment):
			return None
		val = aFragment.lower()

		# FIXME: handle uebermorgen/vorgestern ?

		# right now
		if val == self.__single_char_triggers[0]:
			ts = self.__now
			return [{
				'data': gmFuzzyTimestamp.cFuzzyTimestamp (
					timestamp = ts,
					accuracy = gmFuzzyTimestamp.acc_subseconds
				),
				'label': _('right now (%s, %s)') % (ts.strftime('%A'), ts)
			}]

		# today
		if val == self.__single_char_triggers[1]:
			return [{
				'data': gmFuzzyTimestamp.cFuzzyTimestamp (
					timestamp = self.__now,
					accuracy = gmFuzzyTimestamp.acc_days
				),
				'label': _('today (%s)') % self.__now.strftime('%A, %Y-%m-%d')
			}]

		# tomorrow
		if val == self.__single_char_triggers[2]:
			ts = self.__now + mxDT.RelativeDateTime(days = +1)
			return [{
				'data': gmFuzzyTimestamp.cFuzzyTimestamp (
					timestamp = ts,
					accuracy = gmFuzzyTimestamp.acc_days
				),
				'label': _('tomorrow (%s)') % ts.strftime('%A, %Y-%m-%d')
			}]

		# yesterday
		if val == self.__single_char_triggers[3]:
			ts = self.__now + mxDT.RelativeDateTime(days = -1)
			return [{
				'data': gmFuzzyTimestamp.cFuzzyTimestamp (
					timestamp = ts,
					accuracy = gmFuzzyTimestamp.acc_days
				),
				'label': _('yesterday (%s)') % ts.strftime('%A, %Y-%m-%d')
			}]

		return None
	#--------------------------------------------------------
	def __explicit_offset(self, aFragment):
		# "+/-XXd/w/m/t"
		if not re.match("^(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[%s]$" % self.__offset_chars, aFragment):
			return None
		aFragment = aFragment.lower()

		# allow past ?
		is_future = True
		if string.find(aFragment, '-') > -1:
			is_future = False

		val = int(re.search('\d{1,2}', aFragment).group())

		ts = None
		# hours
		if aFragment[-1] == self.__offset_chars[0]:
			if is_future:
				ts = self.__now + mxDT.RelativeDateTime(hours = val)
				label = _('in %d hour(s) - %s') % (val, ts.strftime('%H:%M'))
			else:
				ts = self.__now - mxDT.RelativeDateTime(hours = val)
				label = _('%d hour(s) ago - %s') % (val, ts.strftime('%H:%M'))
			accuracy = gmFuzzyTimestamp.acc_subseconds
		# days
		elif aFragment[-1] == self.__offset_chars[1]:
			if is_future:
				ts = self.__now + mxDT.RelativeDateTime(days = val)
				label = _('in %d day(s) - %s') % (val, ts.strftime('%A, %x'))
			else:
				ts = self.__now - mxDT.RelativeDateTime(days = val)
				label = _('%d day(s) ago - %s') % (val, ts.strftime('%A, %x'))
			accuracy = gmFuzzyTimestamp.acc_days
		# weeks
		elif aFragment[-1] == self.__offset_chars[2]:
			if is_future:
				ts = self.__now + mxDT.RelativeDateTime(weeks = val)
				label = _('in %d week(s) - %s') % (val, ts.strftime('%A, %x'))
			else:
				ts = self.__now - mxDT.RelativeDateTime(weeks = val)
				label = _('%d week(s) ago - %s)') % (val, ts.strftime('%A, %x'))
			accuracy = gmFuzzyTimestamp.acc_days
		# months
		elif aFragment[-1] == self.__offset_chars[3]:
			if is_future:
				ts = self.__now + mxDT.RelativeDateTime(months = val)
				label = _('in %d month(s) - %s') % (val, ts.strftime('%A, %x'))
			else:
				ts = self.__now - mxDT.RelativeDateTime(months = val)
				label = _('%d month(s) ago - %s') % (val, ts.strftime('%A, %x'))
			accuracy = gmFuzzyTimestamp.acc_days
		# years
		elif aFragment[-1] == self.__offset_chars[4]:
			if is_future:
				ts = self.__now + mxDT.RelativeDateTime(years = val)
				label = _('in %d year(s) - %s') % (val, ts.strftime('%A, %x'))
			else:
				ts = self.__now - mxDT.RelativeDateTime(years = val)
				label = _('%d year(s) ago - %s') % (val, ts.strftime('%A, %x'))
			accuracy = gmFuzzyTimestamp.acc_months

		if ts is None:
			return None

		tmp = {
			'data': gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = ts, accuracy = accuracy),
			'label': label
		}
		return [tmp]
#==================================================
class cFuzzyTimestampInput(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		# setup custom match provider
		matcher = cMatchProvider_FuzzyTimestamp()
		matcher.setWordSeparators('xxx_do_not_separate_words_xxx')
#		matcher.setIgnoredChars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
		matcher.setThresholds(aWord = 998, aSubstring = 999)
		kwargs['aMatchProvider'] = matcher

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.allow_multiple_phrases(None)
		self.selection_only = False

#		self.__display_format = _('%Y-%m-%d')
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __text2timestamp(self):
		# does have timestamp object associated with it
		if self.data is not None:
			return True

		val = self.GetValue().strip()

		# skip empty value
		if val == '':
			return True

		# xx/yyyy ?
		if re.match("^\d{1,2}/{1}\d{4}$", val):
			parts = val.split('/')
			self.data = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = self.__now + mxDT.RelativeDateTime(year = int(part[1]), month = int(part[0])),
				accuracy = gmFuzzyTimestamp.acc_months
			)
			return True

		# date ?
		try:
			date = mxDT.Parser.DateFromString (
				text = val,
				formats = ('euro', 'iso', 'us', 'altus', 'altiso', 'lit', 'altlit', 'eurlit')
			)
			accuracy = gmFuzzyTimestamp.acc_days
			# time, too ?
			time = mxDT.Parser.TimeFromString(text = val)
			datetime = date + time
			if datetime != date:
				accuracy = gmFuzzyTimestamp.acc_subseconds
			self.data = gmFuzzyTimestamp.cFuzzyTimestamp (
				timestamp = datetime,
				accuracy = accuracy
			)
			return True
		except ValueError:
			msg = _('Cannot parse <%s> into proper timestamp.')
			return False

#		try:
#			# FIXME: make this way more generous in accepting date input
#			date = time.strptime(val, self.__display_format)
#		except:
#			msg = _('Invalid date. Date format: %s ' % self.__display_format)
#			gmGuiHelpers.gm_beep_statustext(msg)
#			self.SetBackgroundColour('pink')
#			self.Refresh()
#			return False

		# valid date
		return True
	#--------------------------------------------------------
	# phrasewheel internal API
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		if not self.__text2timestamp():
			self.SetBackgroundColour('pink')
			self.Refresh()
		else:
			self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			self.Refresh()

		gmPhraseWheel.cPhraseWheel._on_lose_focus(self, event)
	#--------------------------------------------------------
	def _calc_display_string(self):
		data = self._picklist.GetClientData(self._picklist.GetSelection())
		if data is None:
			data = self._picklist.GetStringSelection()
		return '%s' % data
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def SetValue(self, val, data=None):
		gmPhraseWheel.cPhraseWheel.SetValue(self, val, data=data)
		if self.data is None:
			self.__text2timestamp()
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
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wx.App):
		def OnInit (self):

			frame = wx.Frame (
				None,
				-4,
				"date input wheel test for GNUmed",
				size=wx.Size(300, 350),
				style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE
			)

			date_wheel = cFuzzyTimestampInput (
				parent = frame,
				id = -1,
				pos = (50, 50),
				size = (180, 30)
			)
			date_wheel.on_resize (None)

			frame.Show (1)
			return 1
	#--------------------------------------------------------
#	app = TestApp()
#	app.MainLoop()

#	app = wx.PyWidgetTester(size = (200, 300))
#	app.SetWidget(cFuzzyTimestampInput, id=-1, size=(180,20), pos=(10,20))
#	app.MainLoop()

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

#==================================================
# - free text input: start string with "
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.36  2006-06-02 13:17:50  ncq
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
