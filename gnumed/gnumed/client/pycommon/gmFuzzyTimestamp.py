#===========================================================================
__doc__ = (
"""GNUmed fuzzy timestamp implementation.

This module implements a class which allows the programmer
to define the degree of fuzziness, uncertainty or
imprecision of the timestamp contained within.

This is useful in fields such as medicine where only partial
timestamps may be known for certain events.
""")
#===========================================================================
# $Id: gmFuzzyTimestamp.py,v 1.10 2007-03-02 15:30:24 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmFuzzyTimestamp.py,v $
__version__ = "$Revision: 1.10 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# stdlib
import sys, datetime as pyDT, re as regex, locale

# 3rd party
import mx.DateTime as mxDT

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
# FIXME: remove this dependancy
#from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime

(	acc_years,
	acc_months,
	acc_days,
	acc_hours,
	acc_minutes,
	acc_seconds,
	acc_subseconds
) = range(1,8)

_accuracy_strings = {
	1: 'years',
	2: 'months',
	3: 'days',
	4: 'hours',
	5: 'minutes',
	6: 'seconds',
	7: 'subseconds'
}

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
#===========================================================================
def __explicit_offset(str_timestamp, offset_chars='hdwmy'):
	"""
			Default is 'hdwm':
			h - hours
			d - days
			w - weeks
			m - months
			y - years

		This also defines the significance of the order of the characters.
	"""
	# "+/-XXd/w/m/t"
	if not regex.match("^(\s|\t)*(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[%s](\s|\t)*$" % offset_chars, str_timestamp):
		return []
	val = int(regex.findall('\d{1,2}', str_timestamp)[0])
	offset_char = regex.findall('[%s]' % offset_chars, str_timestamp)[0].lower()

	now = mxDT.now()
	enc = locale.getlocale()[1]

	# allow past ?
	is_future = True
	if str_timestamp.find('-') > -1:
		is_future = False

	ts = None
	# hours
	if offset_char == offset_chars[0]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(hours = val)
			label = _('in %d hour(s) - %s') % (val, ts.strftime('%H:%M'))
		else:
			ts = now - mxDT.RelativeDateTime(hours = val)
			label = _('%d hour(s) ago - %s') % (val, ts.strftime('%H:%M'))
		accuracy = acc_subseconds
	# days
	elif offset_char == offset_chars[1]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(days = val)
			label = _('in %d day(s) - %s') % (val, ts.strftime('%A, %x').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(days = val)
			label = _('%d day(s) ago - %s') % (val, ts.strftime('%A, %x').decode(enc))
		accuracy = acc_days
	# weeks
	elif offset_char == offset_chars[2]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(weeks = val)
			label = _('in %d week(s) - %s') % (val, ts.strftime('%A, %x').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(weeks = val)
			label = _('%d week(s) ago - %s)') % (val, ts.strftime('%A, %x').decode(enc))
		accuracy = acc_days
	# months
	elif offset_char == offset_chars[3]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(months = val)
			label = _('in %d month(s) - %s') % (val, ts.strftime('%A, %x').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(months = val)
			label = _('%d month(s) ago - %s') % (val, ts.strftime('%A, %x').decode(enc))
		accuracy = acc_days
	# years
	elif offset_char == offset_chars[4]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(years = val)
			label = _('in %d year(s) - %s') % (val, ts.strftime('%A, %x').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(years = val)
			label = _('%d year(s) ago - %s') % (val, ts.strftime('%A, %x').decode(enc))
		accuracy = acc_months

	if ts is None:
		return []

	tmp = {
		'data': cFuzzyTimestamp(timestamp = ts, accuracy = accuracy),
		'label': label
	}
	return [tmp]
#---------------------------------------------------------------------------
def __single_char(str_timestamp, trigger_chars='ndmy'):
	"""This matches on single characters.

	Spaces and tabs are discarded.

	Default is 'ndmy':
		n - now
		d - toDay
		m - toMorrow	Someone please suggest a synonym !
		y - yesterday

	This also defines the significance of the order of the characters.
	"""
	if not regex.match('^(\s|\t)*[%s]{1}(\s|\t)*$' % trigger_chars, str_timestamp):
		return []
	val = str_timestamp.strip().lower()

	now = mxDT.now()
	enc = locale.getlocale()[1]

	# FIXME: handle uebermorgen/vorgestern ?

	# right now
	if val == trigger_chars[0]:
		ts = now
		return [{
			'data': cFuzzyTimestamp (
				timestamp = ts,
				accuracy = acc_subseconds
			),
			'label': _('right now (%s, %s)') % (ts.strftime('%A').decode(enc), ts)
		}]

	# today
	if val == trigger_chars[1]:
		return [{
			'data': cFuzzyTimestamp (
				timestamp = now,
				accuracy = acc_days
			),
			'label': _('today (%s)') % now.strftime('%A, %Y-%m-%d').decode(enc)
		}]

	# tomorrow
	if val == trigger_chars[2]:
		ts = now + mxDT.RelativeDateTime(days = +1)
		return [{
			'data': cFuzzyTimestamp (
				timestamp = ts,
				accuracy = acc_days
			),
			'label': _('tomorrow (%s)') % ts.strftime('%A, %Y-%m-%d').decode(enc)
		}]

	# yesterday
	if val == trigger_chars[3]:
		ts = now + mxDT.RelativeDateTime(days = -1)
		return [{
			'data': cFuzzyTimestamp (
				timestamp = ts,
				accuracy = acc_days
			),
			'label': _('yesterday (%s)') % ts.strftime('%A, %Y-%m-%d').decode(enc)
		}]

	return []
#---------------------------------------------------------------------------
def __single_slash(str_timestamp):
	"""Expand fragments containing a single slash.

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
	matches = []
	now = mxDT.now()
	if regex.match("^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*$", str_timestamp):
		val = int(regex.findall('', str_timestamp))

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
				'data': cFuzzyTimestamp(timestamp = now, accuracy = acc_months),
				'label': '%.2d/%s' % (val, now.year)
			})
			ts = now + mxDT.RelativeDateTime(years = 1)
			matches.append ({
				'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_months),
				'label': '%.2d/%s' % (val, ts.year)
			})
			ts = now + mxDT.RelativeDateTime(years = -1)
			matches.append ({
				'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_months),
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

	elif regex.match("^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}(\s|\t)*$", str_timestamp):
		parts = regex.findall('\d+', str_timestamp)
		fts = cFuzzyTimestamp (
			timestamp = mxDT.now() + mxDT.RelativeDateTime(year = int(parts[1]), month = int(parts[0])),
			accuracy = acc_months
		)
		matches.append ({
			'data': fts,
			'label': fts.format_accurately()
		})

	return matches
#---------------------------------------------------------------------------
def __numbers_only(str_timestamp):
	"""This matches on single numbers.

	Spaces or tabs are discarded.
	"""
	if not regex.match("^(\s|\t)*\d{1,4}(\s|\t)*$", str_timestamp):
		return []

	# strftime() returns str but in the localized encoding,
	# so we may need to decode that to unicode
	enc = locale.getlocale()[1]
	now = mxDT.now()
	val = int(regex.findall('\d{1,4}', str_timestamp)[0])

	matches = []

	# that year
	if (1850 < val) and (val < 2100):
		ts = now + mxDT.RelativeDateTime(year = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_years
		)
		tmp = {
			'data': target_date,
			'label': '%s' % target_date
		}
		matches.append(tmp)

	# day X of this month
	if val <= month_length[now.month]:
		ts = now + mxDT.RelativeDateTime(day = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (this month) - a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		}
		matches.append(tmp)

	# day X of next month
	if val <= month_length[(now + mxDT.RelativeDateTime(months = 1)).month]:
		ts = now + mxDT.RelativeDateTime(months = 1, day = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (next month) - a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		}
		matches.append(tmp)

	# day X of last month
	if val <= month_length[(now + mxDT.RelativeDateTime(months = -1)).month]:
		ts = now + mxDT.RelativeDateTime(months = -1, day = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (last month) - a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		}
		matches.append(tmp)

	# X days from now
	if val <= 400:				# more than a year ahead in days ?? nah !
		ts = now + mxDT.RelativeDateTime(days = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts
		)
		tmp = {
			'data': target_date,
			'label': _('in %d day(s) - %s') % (val, target_date.timestamp.strftime('%A, %x').decode(enc))
		}
		matches.append(tmp)

	# X weeks from now
	if val <= 50:				# pregnancy takes about 40 weeks :-)
		ts = now + mxDT.RelativeDateTime(weeks = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts
		)
		tmp = {
			'data': target_date,
			'label': _('in %d week(s) - %s') % (val, target_date.timestamp.strftime('%A, %x').decode(enc))
		}
		matches.append(tmp)

	# month X of ...
	if val < 13:
		# ... this year
		ts = now + mxDT.RelativeDateTime(month = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_months
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s this year)') % (target_date, ts.strftime('%B').decode(enc))
		}
		matches.append(tmp)

		# ... next year
		ts = now + mxDT.RelativeDateTime(years = 1, month = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_months
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s next year)') % (target_date, ts.strftime('%B').decode(enc))
		}
		matches.append(tmp)

		# ... last year
		ts = now + mxDT.RelativeDateTime(years = -1, month = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_months
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s last year)') % (target_date, ts.strftime('%B').decode(enc))
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
		ts = now + mxDT.RelativeDateTime(weekday = (val-1, 0))
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%s this week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		}
		matches.append(tmp)

		# ... next week
		ts = now + mxDT.RelativeDateTime(weeks = +1, weekday = (val-1, 0))
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%s next week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		}
		matches.append(tmp)

		# ... last week
		ts = now + mxDT.RelativeDateTime(weeks = -1, weekday = (val-1, 0))
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%s last week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		}
		matches.append(tmp)

	if val < 100:
		matches.append ({
			'data': None,
			'label': '%s/' % (1900 + val)
		})

	if val == 200:
		tmp = {
			'data': cFuzzyTimestamp(timestamp = now, accuracy = acc_days),
			'label': '%s' % target_date
		}
		matches.append(tmp)
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = now, accuracy = acc_months),
			'label': '%.2d/%s' % (now.month, now.year)
		})
		matches.append ({
			'data': None,
			'label': '%s/' % now.year
		})
		matches.append ({
			'data': None,
			'label': '%s/' % (now.year + 1)
		})
		matches.append ({
			'data': None,
			'label': '%s/' % (now.year - 1)
		})

	if val < 200 and val >= 190:
		for i in range(10):
			matches.append ({
				'data': None,
				'label': '%s%s/' % (val, i)
			})

	return matches
#---------------------------------------------------------------------------
def __single_dot(str_timestamp):
	"""Expand fragments containing a single dot.

	Standard colloquial date format in Germany: day.month.year

	"14."
		- 14th current month this year
		- 14th next month this year
	"""
	if not regex.match("^(\s|\t)*\d{1,2}\.{1}(\s|\t)*$", str_timestamp):
		return []

	val = int(regex.findall('\d+', str_timestamp)[0])
	now = mxDT.now()
	enc = locale.getlocale()[1]

	matches = []

	# day X of this month
	ts = now + mxDT.RelativeDateTime(day = val)
	if val > 0 and val <= month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s this month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
		})

	# day X of next month
	ts = now + mxDT.RelativeDateTime(day = val, months = +1)
	if val > 0 and val <= month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s next month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
		})

	# day X of last month
	ts = now + mxDT.RelativeDateTime(day = val, months = -1)
	if val > 0 and val <= month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s last month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
		})

	return matches
#---------------------------------------------------------------------------
def str2fuzzy_timestamp_matches(str_timestamp=None, default_time=None):
	"""
	Turn a string into candidate fuzzy timestamps and auto-completions the user is likely to type.

	You MUST have called locale.setlocale(locale.LC_ALL, '')
	somewhere in your code previously.

	@param default_time: if you want to force the time part of the time
		stamp to a given value and the user doesn't type and time part
		this value will be used
	@type default_time: an mx.DateTime.DateTimeDelta instance
	"""
	matches = __single_dot(str_timestamp)
	matches.extend(__numbers_only(str_timestamp))
	matches.extend(__single_slash(str_timestamp))
	matches.extend(__single_char(str_timestamp))
	matches.extend(__explicit_offset(str_timestamp))

	# try mxDT parsers
	if mxDT is not None:
		try:
			# date ?
			date_only = mxDT.Parser.DateFromString (
				text = str_timestamp,
				formats = ('euro', 'iso', 'us', 'altus', 'altiso', 'lit', 'altlit', 'eurlit')
			)
			# time, too ?
			time = mxDT.Parser.TimeFromString(text = str_timestamp)
			datetime = date_only + time
			if datetime == date_only:
				accuracy = acc_days
				if isinstance(default_time, mxDT.DateTimeDeltaType):
					datetime = date_only + default_time
					accuracy = acc_minutes
			else:
				accuracy = acc_subseconds
			fts = cFuzzyTimestamp (
				timestamp = datetime,
				accuracy = accuracy
			)
			matches.append ({
				'data': fts,
				'label': fts.format_accurately()
			})
		except (ValueError, mxDT.RangeError):
			pass

	return matches
#===========================================================================
class cFuzzyTimestamp:

	"""A timestamp implementation with definable inaccuracy.

	This class contains an mxDateTime.DateTime instance to
	hold the actual timestamp. It adds an accuracy attribute
	to allow the programmer to set the precision of the
	timestamp.

	The timestamp will have to be initialzed with a fully
	precise value (which may, of course, contain partially
	fake data to make up for missing values). One can then
	set the accuracy value to indicate up to which part of
	the timestamp the data is valid. Optionally a modifier
	can be set to indicate further specification of the
	value (such as "summer", "afternoon", etc).

	accuracy values:
		1: year only
		...
		7: everything including milliseconds value

	Unfortunately, one cannot directly derive a class from mx.DateTime.DateTime :-(
	"""
	#-----------------------------------------------------------------------
	def __init__(self, timestamp=None, accuracy=acc_subseconds, modifier=''):

		if timestamp is None:
			timestamp = mxDT.now()
			accuracy = acc_subseconds
			modifier = ''

		if isinstance(timestamp, pyDT.datetime):
			timestamp = mxDT.DateTime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)

		if type(timestamp) != mxDT.DateTimeType:
			raise TypeError, '%s.__init__(): <timestamp> must be of mx.DateTime.DateTime or datetime.datetime type' % self.__class__.__name__

		self.timestamp = timestamp

		if (accuracy < 1) or (accuracy > 7):
			raise ValueError, '%s.__init__(): <accuracy> must be between 1 and 7' % self.__class__.__name__
		self.accuracy = accuracy

		self.modifier =  modifier

	#-----------------------------------------------------------------------
	# magic API
	#-----------------------------------------------------------------------
	def __str__(self):
		"""Return string representation meaningful to a user, also for %s formatting."""
		return self.format_accurately()
	#-----------------------------------------------------------------------
	def __repr__(self):
		"""Return string meaningful to a programmer to aid in debugging."""
		tmp = '<[%s]: timestamp [%s], accuracy [%s] (%s), modifier [%s] at %s>' % (
			self.__class__.__name__,
			repr(self.timestamp),
			self.accuracy,
			_accuracy_strings[self.accuracy],
			self.modifier,
			id(self)
		)
		return tmp
	#-----------------------------------------------------------------------
	# external API
	#-----------------------------------------------------------------------
	def strftime(self, format_string):
		if self.accuracy == 7:
			return self.timestamp.strftime(format_string)
		return self.format_accurately()
	#-----------------------------------------------------------------------
	def Format(self, format_string):
		return self.strftime(format_string)
	#-----------------------------------------------------------------------
	def format_accurately(self):
		if self.accuracy == acc_years:
			return unicode(self.timestamp.year)

		if self.accuracy == acc_months:
			return unicode(self.timestamp.strftime('%m/%Y'))

		if self.accuracy == acc_days:
			return unicode(self.timestamp.strftime('%Y-%m-%d'))

		if self.accuracy == acc_hours:
			return unicode(self.timestamp.strftime("%Y-%m-%d %I%p"))

		if self.accuracy == acc_minutes:
			return unicode(self.timestamp.strftime("%Y-%m-%d %H:%M"))

		if self.accuracy == acc_seconds:
			return unicode(self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

		if self.accuracy == acc_subseconds:
			return unicode(self.timestamp)

		raise ValueError, '%s.format_accurately(): <accuracy> (%s) must be between 1 and 7' % (
			self.__class__.__name__,
			self.accuracy
		)
	#-----------------------------------------------------------------------
	def get_mxdt(self):
		return self.timestamp
	#-----------------------------------------------------------------------
	def get_pydt(self):
		tz = gmDateTime.cFixedOffsetTimezone(self.timestamp.gmtoffset().minutes, self.timestamp.tz)
		secs, msecs = divmod(self.timestamp.second, 1)
		ts = pyDT.datetime (
			year = self.timestamp.year,
			month = self.timestamp.month,
			day = self.timestamp.day,
			hour = self.timestamp.hour,
			minute = self.timestamp.minute,
			second = secs,
			microsecond = msecs,
			tzinfo = tz
		)
		return ts
#===========================================================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N, gmLog
	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
	gmDateTime.init()

	#-------------------------------------------------
	def test_str2fuzzy_timestamp_matches():
		print "testing function str2fuzzy_timestamp_matches"
		print "--------------------------------------------"

		val = None
		while val != 'exit':
			val = raw_input('Enter date fragment: ')
			matches = str2fuzzy_timestamp_matches(str_timestamp = val)
			for match in matches:
				print match['label']
				print match['data']
				print "---------------"

	#-------------------------------------------------
	def test_cFuzzyTimeStamp():
		print "testing fuzzy timestamp class"
		print "-----------------------------"

		ts = mxDT.now()
		print "mx.DateTime timestamp", type(ts)
		print "  print ...       :", ts
		print "  print '%%s' %% ...: %s" % ts
		print "  str()           :", str(ts)
		print "  repr()          :", repr(ts)

		fts = cFuzzyTimestamp()
		print "\nfuzzy timestamp <%s '%s'>" % ('class', fts.__class__.__name__)
		for accuracy in range(1,8):
			fts.accuracy = accuracy
			print "  accuracy         : %s (%s)" % (accuracy, _accuracy_strings[accuracy])
			print "  format_accurately:", fts.format_accurately()
			print "  strftime()       :", fts.strftime('%c')
			print "  print ...        :", fts
			print "  print '%%s' %% ... : %s" % fts
			print "  str()            :", str(fts)
			print "  repr()           :", repr(fts)
			raw_input('press ENTER to continue')
	#-------------------------------------------------

	test_str2fuzzy_timestamp_matches()

#===========================================================================
# $Log: gmFuzzyTimestamp.py,v $
# Revision 1.10  2007-03-02 15:30:24  ncq
# - must decode() strftime() output
#
# Revision 1.9  2007/02/16 10:20:39  ncq
# - improved doc strings
#
# Revision 1.8  2007/02/16 10:15:27  ncq
# - strftime() returns str() but encoded, so we need
#   locale.getlocale()[1] to properly decode that to
#   unicode, which needs the locale system to have been
#   initialized
# - improved test suite
#
# Revision 1.7  2007/01/10 22:43:39  ncq
# - depend on gmDateTime, not gmPG2
#
# Revision 1.6  2006/11/27 23:00:45  ncq
# - add str2fuzzy_timestamp_matches() with all the needed infrastructure
# - some unicode()ing
# - user more symbolic names
#
# Revision 1.5  2006/11/07 23:49:08  ncq
# - make runnable standalone for testing
# - add get_mxdt()/get_pydt()
#   - but thus requires gmPG2, yuck, work around later
#
# Revision 1.4  2006/10/31 17:18:55  ncq
# - make cFuzzyTimestamp accept datetime.datetime instances, too
#
# Revision 1.3  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.2  2006/05/24 09:59:57  ncq
# - add constants for accuracy values
# - __init__() now defaults to now()
# - add accuracy-aware Format()/strftime() proxies
#
# Revision 1.1  2006/05/22 12:00:00  ncq
# - first cut at this
#
#
