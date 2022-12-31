# -*- coding: utf-8 -*-

__doc__ = """
GNUmed date/time handling.

This modules provides access to date/time handling
and offers an fuzzy timestamp implementation

It utilizes

	- Python time
	- Python datetime
	- mxDateTime

Note that if you want locale-aware formatting you need to call

	locale.setlocale(locale.LC_ALL, '')

somewhere before importing this script.

Note regarding UTC offsets
--------------------------

Looking from Greenwich:
	WEST (IOW "behind"): negative values
	EAST (IOW "ahead"):  positive values

This is in compliance with what datetime.tzinfo.utcoffset()
does but NOT what time.altzone/time.timezone do !

This module also implements a class which allows the
programmer to define the degree of fuzziness, uncertainty
or imprecision of the timestamp contained within.

This is useful in fields such as medicine where only partial
timestamps may be known for certain events.

Other useful links:

	http://joda-time.sourceforge.net/key_instant.html
"""
#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# stdlib
import sys, datetime as pyDT, time, os, re as regex, locale, logging


# 3rd party
#import mx.DateTime as mxDT


if __name__ == '__main__':
	sys.path.insert(0, '../../')
#from Gnumed.pycommon import gmI18N


_log = logging.getLogger('gm.datetime')
#_log.info(u'mx.DateTime version: %s', mxDT.__version__)

dst_locally_in_use = None
dst_currently_in_effect = None

py_timezone_name = None
py_dst_timezone_name = None
current_local_utc_offset_in_seconds = None
#current_local_timezone_interval = None
current_local_iso_numeric_timezone_string = None
current_local_timezone_name = None

gmCurrentLocalTimezone = 'gmCurrentLocalTimezone not initialized'


(	acc_years,
	acc_months,
	acc_weeks,
	acc_days,
	acc_hours,
	acc_minutes,
	acc_seconds,
	acc_subseconds
) = range(1,9)

_accuracy_strings = {
	1: 'years',
	2: 'months',
	3: 'weeks',
	4: 'days',
	5: 'hours',
	6: 'minutes',
	7: 'seconds',
	8: 'subseconds'
}

gregorian_month_length = {
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

avg_days_per_gregorian_year = 365
avg_days_per_gregorian_month = 30
avg_seconds_per_day = 24 * 60 * 60
days_per_week = 7

#===========================================================================
# module init
#---------------------------------------------------------------------------
def init():

#	_log.debug('mx.DateTime.now(): [%s]' % mxDT.now())
	_log.debug('datetime.now()   : [%s]' % pyDT.datetime.now())
	_log.debug('time.localtime() : [%s]' % str(time.localtime()))
	_log.debug('time.gmtime()    : [%s]' % str(time.gmtime()))

	try:
		_log.debug('$TZ: [%s]' % os.environ['TZ'])
	except KeyError:
		_log.debug('$TZ not defined')

	_log.debug('time.daylight           : [%s] (whether or not DST is locally used at all)', time.daylight)
	_log.debug('time.timezone           : [%s] seconds (+/-: WEST/EAST of Greenwich)', time.timezone)
	_log.debug('time.altzone            : [%s] seconds (+/-: WEST/EAST of Greenwich)', time.altzone)
	_log.debug('time.tzname             : [%s / %s] (non-DST / DST)' % time.tzname)
	_log.debug('time.localtime.tm_zone  : [%s]', time.localtime().tm_zone)
	_log.debug('time.localtime.tm_gmtoff: [%s]', time.localtime().tm_gmtoff)
#	_log.debug('mx.DateTime.now().gmtoffset(): [%s]' % mxDT.now().gmtoffset())

	global py_timezone_name
	py_timezone_name = time.tzname[0]

	global py_dst_timezone_name
	py_dst_timezone_name = time.tzname[1]

	global dst_locally_in_use
	dst_locally_in_use = (time.daylight != 0)

	global dst_currently_in_effect
	dst_currently_in_effect = bool(time.localtime()[8])
	_log.debug('DST currently in effect: [%s]' % dst_currently_in_effect)

	if (not dst_locally_in_use) and dst_currently_in_effect:
		_log.error('system inconsistency: DST not in use - but DST currently in effect ?')

	global current_local_utc_offset_in_seconds
	msg = 'DST currently%sin effect: using UTC offset of [%s] seconds instead of [%s] seconds'
	if dst_currently_in_effect:
		current_local_utc_offset_in_seconds = time.altzone * -1
		_log.debug(msg % (' ', time.altzone * -1, time.timezone * -1))
	else:
		current_local_utc_offset_in_seconds = time.timezone * -1
		_log.debug(msg % (' not ', time.timezone * -1, time.altzone * -1))

	if current_local_utc_offset_in_seconds < 0:
		_log.debug('UTC offset is negative, assuming WEST of Greenwich (clock is "behind")')
	elif current_local_utc_offset_in_seconds > 0:
		_log.debug('UTC offset is positive, assuming EAST of Greenwich (clock is "ahead")')
	else:
		_log.debug('UTC offset is ZERO, assuming Greenwich Time')

#	global current_local_timezone_interval
#	current_local_timezone_interval = mxDT.now().gmtoffset()
#	_log.debug('ISO timezone: [%s] (taken from mx.DateTime.now().gmtoffset())' % current_local_timezone_interval)

	global current_local_iso_numeric_timezone_string
#	current_local_iso_numeric_timezone_string = str(current_local_timezone_interval).replace(',', '.')
	current_local_iso_numeric_timezone_string = '%s' % current_local_utc_offset_in_seconds
	_log.debug('ISO numeric timezone string: [%s]' % current_local_iso_numeric_timezone_string)

	global current_local_timezone_name
	try:
		current_local_timezone_name = os.environ['TZ']
	except KeyError:
		if dst_currently_in_effect:
			current_local_timezone_name = time.tzname[1]
		else:
			current_local_timezone_name = time.tzname[0]

	global gmCurrentLocalTimezone
	gmCurrentLocalTimezone = cPlatformLocalTimezone()
	_log.debug('local-timezone class: %s', cPlatformLocalTimezone)
	_log.debug('local-timezone instance: %s', gmCurrentLocalTimezone)
#	_log.debug('')
#		print (" (total) UTC offset:", gmCurrentLocalTimezone.utcoffset(pyDT.datetime.now()))
#		print (" DST adjustment:", gmCurrentLocalTimezone.dst(pyDT.datetime.now()))
#		print (" timezone name:", gmCurrentLocalTimezone.tzname(pyDT.datetime.now()))

#===========================================================================
# local timezone implementation (lifted from the docs)
#
# A class capturing the platform's idea of local time.
# (May result in wrong values on historical times in
#  timezones where UTC offset and/or the DST rules had
#  changed in the past.)
#---------------------------------------------------------------------------
class cPlatformLocalTimezone(pyDT.tzinfo):

	#-----------------------------------------------------------------------
	def __init__(self):
		self._SECOND = pyDT.timedelta(seconds = 1)
		self._nonDST_OFFSET_FROM_UTC = pyDT.timedelta(seconds = -time.timezone)
		if time.daylight:
			self._DST_OFFSET_FROM_UTC = pyDT.timedelta(seconds = -time.altzone)
		else:
			self._DST_OFFSET_FROM_UTC = self._nonDST_OFFSET_FROM_UTC
		self._DST_SHIFT = self._DST_OFFSET_FROM_UTC - self._nonDST_OFFSET_FROM_UTC
		_log.debug('[%s]: UTC->non-DST offset [%s], UTC->DST offset [%s], DST shift [%s]', self.__class__.__name__, self._nonDST_OFFSET_FROM_UTC, self._DST_OFFSET_FROM_UTC, self._DST_SHIFT)

	#-----------------------------------------------------------------------
	def fromutc(self, dt):
		assert dt.tzinfo is self
		stamp = (dt - pyDT.datetime(1970, 1, 1, tzinfo = self)) // self._SECOND
		args = time.localtime(stamp)[:6]
		dst_diff = self._DST_SHIFT // self._SECOND
		# Detect fold
		fold = (args == time.localtime(stamp - dst_diff))
		return pyDT.datetime(*args, microsecond = dt.microsecond, tzinfo = self, fold = fold)

	#-----------------------------------------------------------------------
	def utcoffset(self, dt):
		if self._isdst(dt):
			return self._DST_OFFSET_FROM_UTC
		return self._nonDST_OFFSET_FROM_UTC

	#-----------------------------------------------------------------------
	def dst(self, dt):
		if self._isdst(dt):
			return self._DST_SHIFT
		return pyDT.timedelta(0)

	#-----------------------------------------------------------------------
	def tzname(self, dt):
		return time.tzname[self._isdst(dt)]

	#-----------------------------------------------------------------------
	def _isdst(self, dt):
		tt = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, 0)
		try:
			stamp = time.mktime(tt)
		except (OverflowError, ValueError):
			_log.exception('overflow in time.mktime(%s)', tt)
			return False

		tt = time.localtime(stamp)
		return tt.tm_isdst > 0

#===========================================================================
# convenience functions
#---------------------------------------------------------------------------
def get_next_month(dt):
	next_month = dt.month + 1
	if next_month == 13:
		return 1
	return next_month

#---------------------------------------------------------------------------
def get_last_month(dt):
	last_month = dt.month - 1
	if last_month == 0:
		return 12
	return last_month

#---------------------------------------------------------------------------
def get_date_of_weekday_in_week_of_date(weekday, base_dt=None):
	# weekday:
	# 0 = Sunday
	# 1 = Monday ...
	if weekday not in [0,1,2,3,4,5,6,7]:
		raise ValueError('weekday must be in 0 (Sunday) to 7 (Sunday, again)')
	if base_dt is None:
		base_dt = pydt_now_here()
	dt_weekday = base_dt.isoweekday()		# 1 = Mon
	day_diff = dt_weekday - weekday
	days2add = (-1 * day_diff)
	return pydt_add(base_dt, days = days2add)

#---------------------------------------------------------------------------
def get_date_of_weekday_following_date(weekday, base_dt=None):
	# weekday:
	# 0 = Sunday		# will be wrapped to 7
	# 1 = Monday ...
	if weekday not in [0,1,2,3,4,5,6,7]:
		raise ValueError('weekday must be in 0 (Sunday) to 7 (Sunday, again)')
	if weekday == 0:
		weekday = 7
	if base_dt is None:
		base_dt = pydt_now_here()
	dt_weekday = base_dt.isoweekday()		# 1 = Mon
	days2add = weekday - dt_weekday
	if days2add == 0:
		days2add = 7
	elif days2add < 0:
		days2add += 7
	return pydt_add(base_dt, days = days2add)

#===========================================================================
# mxDateTime conversions
#---------------------------------------------------------------------------
def mxdt2py_dt(mxDateTime):

	if isinstance(mxDateTime, pyDT.datetime):
		return mxDateTime

	try:
		tz_name = str(mxDateTime.gmtoffset()).replace(',', '.')
	except mxDT.Error:
		_log.debug('mx.DateTime cannot gmtoffset() this timestamp, assuming local time')
		#tz_name = current_local_iso_numeric_timezone_string
		tz_name = current_local_timezone_name

	if dst_currently_in_effect:
		# convert
		tz = cFixedOffsetTimezone (
			offset = ((time.altzone * -1) // 60),
			name = tz_name
		)
	else:
		# convert
		tz = cFixedOffsetTimezone (
			offset = ((time.timezone * -1) // 60),
			name = tz_name
		)

	try:
		return pyDT.datetime (
			year = mxDateTime.year,
			month = mxDateTime.month,
			day = mxDateTime.day,
			tzinfo = tz
		)
	except Exception:
		_log.debug ('error converting mx.DateTime.DateTime to Python: %s-%s-%s %s:%s %s.%s',
			mxDateTime.year,
			mxDateTime.month,
			mxDateTime.day,
			mxDateTime.hour,
			mxDateTime.minute,
			mxDateTime.second,
			mxDateTime.tz
		)
		raise

#===========================================================================
def format_dob(dob, format='%Y %b %d', none_string=None, dob_is_estimated=False):
	if dob is None:
		if none_string is None:
			return _('** DOB unknown **')
		return none_string

	dob_txt = pydt_strftime(dob, format = format, accuracy = acc_days)
	if dob_is_estimated:
		return '%s%s' % ('\u2248', dob_txt)

	return dob_txt

#---------------------------------------------------------------------------
def pydt_strftime(dt=None, format='%Y %b %d  %H:%M.%S', accuracy=None, none_str=None):

	if dt is None:
		if none_str is not None:
			return none_str
		raise ValueError('must provide <none_str> if <dt>=None is to be dealt with')

	try:
		return dt.strftime(format)

	except ValueError:
		_log.exception()
		return 'strftime() error'

#---------------------------------------------------------------------------
def pydt_add(dt, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0):
	if months > 11 or months < -11:
		raise ValueError('pydt_add(): months must be within [-11..11]')

	dt = dt + pyDT.timedelta (
		weeks = weeks,
		days = days,
		hours = hours,
		minutes = minutes,
		seconds = seconds,
		milliseconds = milliseconds,
		microseconds = microseconds
	)
	if (years == 0) and (months == 0):
		return dt
	target_year = dt.year + years
	target_month = dt.month + months
	if target_month > 12:
		target_year += 1
		target_month -= 12
	elif target_month < 1:
		target_year -= 1
		target_month += 12
	return pydt_replace(dt, year = target_year, month = target_month, strict = False)

#---------------------------------------------------------------------------
def pydt_replace(dt, strict=True, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None):
	# normalization required because .replace() does not
	# deal with keyword arguments being None ...
	if year is None:
		year = dt.year
	if month is None:
		month = dt.month
	if day is None:
		day = dt.day
	if hour is None:
		hour = dt.hour
	if minute is None:
		minute = dt.minute
	if second is None:
		second = dt.second
	if microsecond is None:
		microsecond = dt.microsecond
	if tzinfo is None:
		tzinfo = dt.tzinfo		# can fail on naive dt's

	if strict:
		return dt.replace(year = year, month = month, day = day, hour = hour, minute = minute, second = second, microsecond = microsecond, tzinfo = tzinfo)

	try:
		return dt.replace(year = year, month = month, day = day, hour = hour, minute = minute, second = second, microsecond = microsecond, tzinfo = tzinfo)
	except ValueError:
		_log.debug('error replacing datetime member(s): %s', locals())

	# (target/existing) day did not exist in target month (which raised the exception)
	if month == 2:
		if day > 28:
			if is_leap_year(year):
				day = 29
			else:
				day = 28
	else:
		if day == 31:
			day = 30

	return dt.replace(year = year, month = month, day = day, hour = hour, minute = minute, second = second, microsecond = microsecond, tzinfo = tzinfo)

#---------------------------------------------------------------------------
def pydt_is_today(dt):
	now = pyDT.datetime.now(gmCurrentLocalTimezone)
	if dt.day != now.day:
		return False
	if dt.month != now.month:
		return False
	if dt.year != now.year:
		return False
	return True

#---------------------------------------------------------------------------
def pydt_now_here():
	"""Returns NOW @ HERE (IOW, in the local timezone."""
	return pyDT.datetime.now(gmCurrentLocalTimezone)

#---------------------------------------------------------------------------
def pydt_max_here():
	return pyDT.datetime.max.replace(tzinfo = gmCurrentLocalTimezone)

#===========================================================================
# wxPython conversions
#---------------------------------------------------------------------------
def wxDate2py_dt(wxDate=None):
	if not wxDate.IsValid():
		raise ValueError ('invalid wxDate: %s-%s-%s %s:%s %s.%s',
			wxDate.GetYear(),
			wxDate.GetMonth(),
			wxDate.GetDay(),
			wxDate.GetHour(),
			wxDate.GetMinute(),
			wxDate.GetSecond(),
			wxDate.GetMillisecond()
		)

	try:
		return pyDT.datetime (
			year = wxDate.GetYear(),
			month = wxDate.GetMonth() + 1,
			day = wxDate.GetDay(),
			tzinfo = gmCurrentLocalTimezone
		)
	except Exception:
		_log.debug ('error converting wxDateTime to Python: %s-%s-%s %s:%s %s.%s',
			wxDate.GetYear(),
			wxDate.GetMonth(),
			wxDate.GetDay(),
			wxDate.GetHour(),
			wxDate.GetMinute(),
			wxDate.GetSecond(),
			wxDate.GetMillisecond()
		)
		raise

#===========================================================================
# interval related
#---------------------------------------------------------------------------
def format_interval(interval=None, accuracy_wanted=None, none_string=None, verbose=False):

	if accuracy_wanted is None:
		accuracy_wanted = acc_seconds

	if interval is None:
		if none_string is not None:
			return none_string

	years, days = divmod(interval.days, avg_days_per_gregorian_year)
	months, days = divmod(days, avg_days_per_gregorian_month)
	weeks, days = divmod(days, days_per_week)
	days, secs = divmod((days * avg_seconds_per_day) + interval.seconds, avg_seconds_per_day)
	hours, secs = divmod(secs, 3600)
	mins, secs = divmod(secs, 60)

	tmp = ''

	if years > 0:
		if verbose:
			if years > 1:
				tag = ' ' + _('years')
			else:
				tag = ' ' + _('year')
		else:
			tag = _('interval_format_tag::years::y')[-1:]
		tmp += '%s%s' % (int(years), tag)

	if accuracy_wanted < acc_months:
		if tmp == '':
			if verbose:
				return _('0 years')
			return '0%s' % _('interval_format_tag::years::y')[-1:]
		return tmp.strip()

	if months > 0:
		if verbose:
			if months > 1:
				tag = ' ' + _('months')
			else:
				tag = ' ' + _('month')
		else:
			tag = _('interval_format_tag::months::m')[-1:]
		tmp += ' %s%s' % (int(months), tag)

	if accuracy_wanted < acc_weeks:
		if tmp == '':
			if verbose:
				return _('0 months')
			return '0%s' % _('interval_format_tag::months::m')[-1:]
		return tmp.strip()

	if weeks > 0:
		if verbose:
			if weeks > 1:
				tag = ' ' + _('weeks')
			else:
				tag = ' ' + _('week')
		else:
			tag = _('interval_format_tag::weeks::w')[-1:]
		tmp += ' %s%s' % (int(weeks), tag)

	if accuracy_wanted < acc_days:
		if tmp == '':
			if verbose:
				return _('0 weeks')
			return '0%s' % _('interval_format_tag::weeks::w')[-1:]
		return tmp.strip()

	if days > 0:
		if verbose:
			if days > 1:
				tag = ' ' + _('days')
			else:
				tag = ' ' + _('day')
		else:
			tag = _('interval_format_tag::days::d')[-1:]
		tmp += ' %s%s' % (int(days), tag)

	if accuracy_wanted < acc_hours:
		if tmp == '':
			if verbose:
				return _('0 days')
			return '0%s' % _('interval_format_tag::days::d')[-1:]
		return tmp.strip()

	if hours > 0:
		if verbose:
			if hours > 1:
				tag = ' ' + _('hours')
			else:
				tag = ' ' + _('hour')
		else:
			tag = '/24'
		tmp += ' %s%s' % (int(hours), tag)

	if accuracy_wanted < acc_minutes:
		if tmp == '':
			if verbose:
				return _('0 hours')
			return '0/24'
		return tmp.strip()

	if mins > 0:
		if verbose:
			if mins > 1:
				tag = ' ' + _('minutes')
			else:
				tag = ' ' + _('minute')
		else:
			tag = '/60'
		tmp += ' %s%s' % (int(mins), tag)

	if accuracy_wanted < acc_seconds:
		if tmp == '':
			if verbose:
				return _('0 minutes')
			return '0/60'
		return tmp.strip()

	if secs > 0:
		if verbose:
			if secs > 1:
				tag = ' ' + _('seconds')
			else:
				tag = ' ' + _('second')
		else:
			tag = 's'
		tmp += ' %s%s' % (int(secs), tag)

	if tmp == '':
		if verbose:
			return _('0 seconds')
		return '0s'

	return tmp.strip()

#---------------------------------------------------------------------------
def format_interval_medically(interval=None):
	"""Formats an interval.

	This isn't mathematically correct but close enough for display.
	"""
	# more than 1 year ?
	if interval.days > 364:
		years, days = divmod(interval.days, avg_days_per_gregorian_year)
		leap_days, tmp = divmod(years, 4)
		days_left_without_leap_days = days - leap_days
		months, day = divmod((days_left_without_leap_days), 30.33)
		if int(months) == 0:
			return "%s%s" % (int(years), _('interval_format_tag::years::y')[-1:])
		return "%s%s %s%s" % (int(years), _('interval_format_tag::years::y')[-1:], int(months), _('interval_format_tag::months::m')[-1:])

	# more than 30 days / 1 month ?
	if interval.days > 30:
		months, days = divmod(interval.days, 30.33)
		weeks, days = divmod(days, 7)
		if int(weeks + days) == 0:
			result = '%smo' % int(months)
		else:
			result = '%s%s' % (int(months), _('interval_format_tag::months::m')[-1:])
		if int(weeks) != 0:
			result += ' %s%s' % (int(weeks), _('interval_format_tag::weeks::w')[-1:])
		if int(days) != 0:
			result += ' %s%s' % (int(days), _('interval_format_tag::days::d')[-1:])
		return result

	# between 7 and 30 days ?
	if interval.days > 7:
		return "%s%s" % (interval.days, _('interval_format_tag::days::d')[-1:])

	# between 1 and 7 days ?
	if interval.days > 0:
		hours, seconds = divmod(interval.seconds, 3600)
		if hours == 0:
			return '%s%s' % (interval.days, _('interval_format_tag::days::d')[-1:])
		return "%s%s (%sh)" % (interval.days, _('interval_format_tag::days::d')[-1:], int(hours))

	# between 5 hours and 1 day
	if interval.seconds > (5*3600):
		return "%sh" % int(interval.seconds // 3600)

	# between 1 and 5 hours
	if interval.seconds > 3600:
		hours, seconds = divmod(interval.seconds, 3600)
		minutes = seconds // 60
		if minutes == 0:
			return '%sh' % int(hours)
		return "%s:%02d" % (int(hours), int(minutes))

	# minutes only
	if interval.seconds > (5*60):
		return "0:%02d" % (int(interval.seconds // 60))

	# seconds
	minutes, seconds = divmod(interval.seconds, 60)
	if minutes == 0:
		return '%ss' % int(seconds)
	if seconds == 0:
		return '0:%02d' % int(minutes)
	return "%s.%ss" % (int(minutes), int(seconds))

#---------------------------------------------------------------------------
def format_pregnancy_weeks(age):
	weeks, days = divmod(age.days, 7)
	return '%s%s%s%s' % (
		int(weeks),
		_('interval_format_tag::weeks::w')[-1:],
		days,
		_('interval_format_tag::days::d')[-1:]
	)

#---------------------------------------------------------------------------
def format_pregnancy_months(age):
	months, remainder = divmod(age.days, 28)
	return '%s%s' % (
		int(months) + 1,
		_('interval_format_tag::months::m')[-1:]
	)

#---------------------------------------------------------------------------
def is_leap_year(year):
	if year < 1582:		# no leap years before Gregorian Reform
		_log.debug('%s: before Gregorian Reform', year)
		return False

	# year is multiple of 4 ?
	div, remainder = divmod(year, 4)
	# * NOT divisible by 4
	# -> common year
	if remainder > 0:
		return False

	# year is a multiple of 100 ?
	div, remainder = divmod(year, 100)
	# * divisible by 4
	# * NOT divisible by 100
	# -> leap year
	if remainder > 0:
		return True

	# year is a multiple of 400 ?
	div, remainder = divmod(year, 400)
	# * divisible by 4
	# * divisible by 100, so, perhaps not leaping ?
	# * but ALSO divisible by 400
	# -> leap year
	if remainder == 0:
		return True

	# all others
	# -> common year
	return False

#---------------------------------------------------------------------------
def calculate_apparent_age(start=None, end=None):
	"""The result of this is a tuple (years, ..., seconds) as one would
	'expect' an age to look like, that is, simple differences between
	the fields:

		(years, months, days, hours, minutes, seconds)

	This does not take into account time zones which may
	shift the result by one day.

	<start> and <end> must by python datetime instances
	<end> is assumed to be "now" if not given
	"""
	if end is None:
		end = pyDT.datetime.now(gmCurrentLocalTimezone)

	if end < start:
		raise ValueError('calculate_apparent_age(): <end> (%s) before <start> (%s)' % (end, start))

	if end == start:
		return (0, 0, 0, 0, 0, 0)

	# steer clear of leap years
	if end.month == 2:
		if end.day == 29:
			if not is_leap_year(start.year):
				end = end.replace(day = 28)

	# years
	years = end.year - start.year
	end = end.replace(year = start.year)
	if end < start:
		years = years - 1

	# months
	if end.month == start.month:
		if end < start:
			months = 11
		else:
			months = 0
	else:
		months = end.month - start.month
		if months < 0:
			months = months + 12
		if end.day > gregorian_month_length[start.month]:
			end = end.replace(month = start.month, day = gregorian_month_length[start.month])
		else:
			end = end.replace(month = start.month)
		if end < start:
			months = months - 1

	# days
	if end.day == start.day:
		if end < start:
			days = gregorian_month_length[start.month] - 1
		else:
			days = 0
	else:
		days = end.day - start.day
		if days < 0:
			days = days + gregorian_month_length[start.month]
		end = end.replace(day = start.day)
		if end < start:
			days = days - 1

	# hours
	if end.hour == start.hour:
		hours = 0
	else:
		hours = end.hour - start.hour
		if hours < 0:
			hours = hours + 24
		end = end.replace(hour = start.hour)
		if end < start:
			hours = hours - 1

	# minutes
	if end.minute == start.minute:
		minutes = 0
	else:
		minutes = end.minute - start.minute
		if minutes < 0:
			minutes = minutes + 60
		end = end.replace(minute = start.minute)
		if end < start:
			minutes = minutes - 1

	# seconds
	if end.second == start.second:
		seconds = 0
	else:
		seconds = end.second - start.second
		if seconds < 0:
			seconds = seconds + 60
		end = end.replace(second = start.second)
		if end < start:
			seconds = seconds - 1

	return (years, months, days, hours, minutes, seconds)

#---------------------------------------------------------------------------
def format_apparent_age_medically(age=None):
	"""<age> must be a tuple as created by calculate_apparent_age()"""

	(years, months, days, hours, minutes, seconds) = age

	# at least 1 year ?
	if years > 0:
		if months == 0:
			return '%s%s' % (
				years,
				_('y::year_abbreviation').replace('::year_abbreviation', '')
			)
		return '%s%s %s%s' % (
			years,
			_('y::year_abbreviation').replace('::year_abbreviation', ''),
			months,
			_('m::month_abbreviation').replace('::month_abbreviation', '')
		)

	# at least 1 month ?
	if months > 0:
		if days == 0:
			return '%s%s' % (
				months,
				_('mo::month_only_abbreviation').replace('::month_only_abbreviation', '')
			)

		result = '%s%s' % (
			months,
			_('m::month_abbreviation').replace('::month_abbreviation', '')
		)

		weeks, days = divmod(days, 7)
		if int(weeks) != 0:
			result += '%s%s' % (
				int(weeks),
				_('w::week_abbreviation').replace('::week_abbreviation', '')
			)
		if int(days) != 0:
			result += '%s%s' % (
				int(days),
				_('d::day_abbreviation').replace('::day_abbreviation', '')
			)

		return result

	# between 7 days and 1 month
	if days > 7:
		return "%s%s" % (
			days,
			_('d::day_abbreviation').replace('::day_abbreviation', '')
		)

	# between 1 and 7 days ?
	if days > 0:
		if hours == 0:
			return '%s%s' % (
				days,
				_('d::day_abbreviation').replace('::day_abbreviation', '')
			)
		return '%s%s (%s%s)' % (
			days,
			_('d::day_abbreviation').replace('::day_abbreviation', ''),
			hours,
			_('h::hour_abbreviation').replace('::hour_abbreviation', '')
		)

	# between 5 hours and 1 day
	if hours > 5:
		return '%s%s' % (
			hours,
			_('h::hour_abbreviation').replace('::hour_abbreviation', '')
		)

	# between 1 and 5 hours
	if hours > 1:
		if minutes == 0:
			return '%s%s' % (
				hours,
				_('h::hour_abbreviation').replace('::hour_abbreviation', '')
			)
		return '%s:%02d' % (
			hours,
			minutes
		)

	# between 5 and 60 minutes
	if minutes > 5:
		return "0:%02d" % minutes

	# less than 5 minutes
	if minutes == 0:
		return '%s%s' % (
			seconds,
			_('s::second_abbreviation').replace('::second_abbreviation', '')
		)
	if seconds == 0:
		return "0:%02d" % minutes
	return "%s.%s%s" % (
		minutes,
		seconds,
		_('s::second_abbreviation').replace('::second_abbreviation', '')
	)
#---------------------------------------------------------------------------
def str2interval(str_interval=None):

	unit_keys = {
		'year': _('yYaA_keys_year'),
		'month': _('mM_keys_month'),
		'week': _('wW_keys_week'),
		'day': _('dD_keys_day'),
		'hour': _('hH_keys_hour')
	}

	str_interval = str_interval.strip()

	# "(~)35(yY)"	- at age 35 years
	keys = '|'.join(list(unit_keys['year'].replace('_keys_year', '')))
	if regex.match('^~*(\s|\t)*\d+(%s)*$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = (int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]) * avg_days_per_gregorian_year))

	# "(~)12mM" - at age 12 months
	keys = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		years, months = divmod (
			int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# weeks
	keys = '|'.join(list(unit_keys['week'].replace('_keys_week', '')))
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(weeks = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# days
	keys = '|'.join(list(unit_keys['day'].replace('_keys_day', '')))
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# hours
	keys = '|'.join(list(unit_keys['hour'].replace('_keys_hour', '')))
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/12 - months
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*12$', str_interval, flags = regex.UNICODE):
		years, months = divmod (
			int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# x/52 - weeks
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*52$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(weeks = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/7 - days
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*7$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/24 - hours
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*24$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/60 - minutes
	if regex.match('^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*60$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(minutes = int(regex.findall('\d+', str_interval, flags = regex.UNICODE)[0]))

	# nYnM - years, months
	keys_year = '|'.join(list(unit_keys['year'].replace('_keys_year', '')))
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	if regex.match('^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_year, keys_month), str_interval, flags = regex.UNICODE):
		parts = regex.findall('\d+', str_interval, flags = regex.UNICODE)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# nMnW - months, weeks
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	keys_week = '|'.join(list(unit_keys['week'].replace('_keys_week', '')))
	if regex.match('^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_month, keys_week), str_interval, flags = regex.UNICODE):
		parts = regex.findall('\d+', str_interval, flags = regex.UNICODE)
		months, weeks = divmod(int(parts[1]), 4)
		months += int(parts[0])
		return pyDT.timedelta(days = ((months * avg_days_per_gregorian_month) + (weeks * days_per_week)))

	return None

#===========================================================================
# string -> python datetime parser
#---------------------------------------------------------------------------
def __single_char2py_dt(str2parse, trigger_chars=None):
	"""This matches on single characters.

	Spaces and tabs are discarded.

	Default is 'ndmy':
		n - _N_ow
		d - to_D_ay
		m - to_M_orrow	Someone please suggest a synonym ! ("2" does not cut it ...)
		y - _Y_esterday

	This also defines the significance of the order of the characters.
	"""
	str2parse = str2parse.strip().lower()
	if len(str2parse) != 1:
		return []

	if trigger_chars is None:
		trigger_chars = _('ndmy (single character date triggers)')[:4].lower()

	if str2parse not in trigger_chars:
		return []

	now = pydt_now_here()

	# FIXME: handle uebermorgen/vorgestern ?

	# right now
	if str2parse == trigger_chars[0]:
		return [{
			'data': now,
			'label': _('right now (%s, %s)') % (now.strftime('%A'), now)
		}]
	# today
	if str2parse == trigger_chars[1]:
		return [{
			'data': now,
			'label': _('today (%s)') % now.strftime('%A, %Y-%m-%d')
		}]
	# tomorrow
	if str2parse == trigger_chars[2]:
		ts = pydt_add(now, days = 1)
		return [{
			'data': ts,
			'label': _('tomorrow (%s)') % ts.strftime('%A, %Y-%m-%d')
		}]
	# yesterday
	if str2parse == trigger_chars[3]:
		ts = pydt_add(now, days = -1)
		return [{
			'data': ts,
			'label': _('yesterday (%s)') % ts.strftime('%A, %Y-%m-%d')
		}]
	return []

#---------------------------------------------------------------------------
def __single_dot2py_dt(str2parse):
	"""Expand fragments containing a single dot.

	Standard colloquial date format in Germany: day.month.year

	"14."
		- the 14th of the current month
		- the 14th of next month
	"-14."
		- the 14th of last month
	"""
	str2parse = str2parse.replace(' ', '').replace('\t', '')

	if not str2parse.endswith('.'):
		return []
	try:
		day_val = int(str2parse[:-1])
	except ValueError:
		return []
	if (day_val < -31) or (day_val > 31) or (day_val == 0):
		return []

	now = pydt_now_here()
	matches = []

	# day X of last month only
	if day_val < 0:
		ts = pydt_replace(pydt_add(now, months = -1), day = abs(day_val), strict = False)
		if ts.day == day_val:
			matches.append ({
				'data': ts,
				'label': _('%s-%s-%s: a %s last month') % (ts.year, ts.month, ts.day, ts.strftime('%A'))
			})

	# day X of ...
	if day_val > 0:
		# ... this month
		try:
			ts = pydt_replace(now, day = day_val, strict = False)
			matches.append ({
				'data': ts,
				'label': _('%s-%s-%s: a %s this month') % (ts.year, ts.month, ts.day, ts.strftime('%A'))
			})
		except ValueError:
			pass
		# ... next month
		try:
			ts = pydt_replace(pydt_add(now, months = 1), day = day_val, strict = False)
			if ts.day == day_val:
				matches.append ({
					'data': ts,
					'label': _('%s-%s-%s: a %s next month') % (ts.year, ts.month, ts.day, ts.strftime('%A'))
				})
		except ValueError:
			pass
		# ... last month
		try:
			ts = pydt_replace(pydt_add(now, months = -1), day = day_val, strict = False)
			if ts.day == day_val:
				matches.append ({
					'data': ts,
					'label': _('%s-%s-%s: a %s last month') % (ts.year, ts.month, ts.day, ts.strftime('%A'))
				})
		except ValueError:
			pass

	return matches

#---------------------------------------------------------------------------
def __single_slash2py_dt(str2parse):
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

	5/1999
	6/2004
	"""
	str2parse = str2parse.strip()

	now = pydt_now_here()

	# 5/1999
	if regex.match(r"^\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}$", str2parse, flags = regex.UNICODE):
		month, year = regex.findall(r'\d+', str2parse, flags = regex.UNICODE)
		ts = pydt_replace(now, year = int(year), month = int(month), strict = False)
		return [{
			'data': ts,
			'label': ts.strftime('%Y-%m-%d')
		}]

	matches = []
	# 5/
	if regex.match(r"^\d{1,2}(\s|\t)*/+$", str2parse, flags = regex.UNICODE):
		val = int(str2parse.rstrip('/').strip())

		# "55/" -> "1955"
		if val < 100 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s-' % (val + 1900)
			})
		# "11/" -> "2011"
		if val < 26 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s-' % (val + 2000)
			})
		# "5/" -> "1995"
		if val < 10 and val >= 0:
			matches.append ({
				'data': None,
				'label': '%s-' % (val + 1990)
			})
		if val < 13 and val > 0:
			# "11/" -> "11/this year"
			matches.append ({
				'data': None,
				'label': '%s-%.2d-' % (now.year, val)
			})
			# "11/" -> "11/next year"
			ts = pydt_add(now, years = 1)
			matches.append ({
				'data': None,
				'label': '%s-%.2d-' % (ts.year, val)
			})
			# "11/" -> "11/last year"
			ts = pydt_add(now, years = -1)
			matches.append ({
				'data': None,
				'label': '%s-%.2d-' % (ts.year, val)
			})
			# "11/" -> "201?-11-"
			matches.append ({
				'data': None,
				'label': '201?-%.2d-' % val
			})
			# "11/" -> "200?-11-"
			matches.append ({
				'data': None,
				'label': '200?-%.2d-' % val
			})
			# "11/" -> "20??-11-"
			matches.append ({
				'data': None,
				'label': '20??-%.2d-' % val
			})
			# "11/" -> "199?-11-"
			matches.append ({
				'data': None,
				'label': '199?-%.2d-' % val
			})
			# "11/" -> "198?-11-"
			matches.append ({
				'data': None,
				'label': '198?-%.2d-' % val
			})
			# "11/" -> "198?-11-"
			matches.append ({
				'data': None,
				'label': '197?-%.2d-' % val
			})
			# "11/" -> "19??-11-"
			matches.append ({
				'data': None,
				'label': '19??-%.2d-' % val
			})

	return matches

#---------------------------------------------------------------------------
def __numbers_only2py_dt(str2parse):
	"""This matches on single numbers.

	Spaces or tabs are discarded.
	"""
	try:
		val = int(str2parse.strip())
	except ValueError:
		return []

	now = pydt_now_here()

	matches = []

	# that year
	if (1850 < val) and (val < 2100):
		ts = pydt_replace(now, year = val, strict = False)
		matches.append ({
			'data': ts,
			'label': ts.strftime('%Y-%m-%d')
		})
	# day X of this month
	if (val > 0) and (val <= gregorian_month_length[now.month]):
		ts = pydt_replace(now, day = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%d. of %s (this month): a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		})
	# day X of ...
	if (val > 0) and (val < 32):
		# ... next month
		ts = pydt_replace(pydt_add(now, months = 1), day = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%d. of %s (next month): a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		})
		# ... last month
		ts = pydt_replace(pydt_add(now, months = -1), day = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%d. of %s (last month): a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		})
	# X days from now
	if (val > 0) and (val <= 400):				# more than a year ahead in days ?? nah !
		ts = pydt_add(now, days = val)
		matches.append ({
			'data': ts,
			'label': _('in %d day(s): %s') % (val, ts.strftime('%A, %Y-%m-%d'))
		})
	if (val < 0) and (val >= -400):				# more than a year back in days ?? nah !
		ts = pydt_add(now, days = val)
		matches.append ({
			'data': ts,
			'label': _('%d day(s) ago: %s') % (abs(val), ts.strftime('%A, %Y-%m-%d'))
		})
	# X weeks from now
	if (val > 0) and (val <= 50):				# pregnancy takes about 40 weeks :-)
		ts = pydt_add(now, weeks = val)
		matches.append ({
			'data': ts,
			'label': _('in %d week(s): %s') % (val, ts.strftime('%A, %Y-%m-%d'))
		})
	if (val < 0) and (val >= -50):				# pregnancy takes about 40 weeks :-)
		ts = pydt_add(now, weeks = val)
		matches.append ({
			'data': ts,
			'label': _('%d week(s) ago: %s') % (abs(val), ts.strftime('%A, %Y-%m-%d'))
		})

	# month X of ...
	if (val < 13) and (val > 0):
		# ... this year
		ts = pydt_replace(now, month = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%s (%s this year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B'))
		})
		# ... next year
		ts = pydt_replace(pydt_add(now, years = 1), month = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%s (%s next year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B'))
		})
		# ... last year
		ts = pydt_replace(pydt_add(now, years = -1), month = val, strict = False)
		matches.append ({
			'data': ts,
			'label': _('%s (%s last year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B'))
		})
		# fragment expansion
		matches.append ({
			'data': None,
			'label': '200?-%s' % val
		})
		matches.append ({
			'data': None,
			'label': '199?-%s' % val
		})
		matches.append ({
			'data': None,
			'label': '198?-%s' % val
		})
		matches.append ({
			'data': None,
			'label': '19??-%s' % val
		})

	# needs mxDT
#	# day X of ...
#	if (val < 8) and (val > 0):
#		# ... this week
#		ts = now + mxDT.RelativeDateTime(weekday = (val-1, 0))
#		matches.append ({
#			'data': mxdt2py_dt(ts),
#			'label': _('%s this week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		})
#		# ... next week
#		ts = now + mxDT.RelativeDateTime(weeks = +1, weekday = (val-1, 0))
#		matches.append ({
#			'data': mxdt2py_dt(ts),
#			'label': _('%s next week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		})
#		# ... last week
#		ts = now + mxDT.RelativeDateTime(weeks = -1, weekday = (val-1, 0))
#		matches.append ({
#			'data': mxdt2py_dt(ts),
#			'label': _('%s last week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		})

	if (val < 100) and (val > 0):
		matches.append ({
			'data': None,
			'label': '%s-' % (1900 + val)
		})

	if val == 201:
		matches.append ({
			'data': now,
			'label': now.strftime('%Y-%m-%d')
		})
		matches.append ({
			'data': None,
			'label': now.strftime('%Y-%m')
		})
		matches.append ({
			'data': None,
			'label': now.strftime('%Y')
		})
		matches.append ({
			'data': None,
			'label': '%s-' % (now.year + 1)
		})
		matches.append ({
			'data': None,
			'label': '%s-' % (now.year - 1)
		})

	if val < 200 and val >= 190:
		for i in range(10):
			matches.append ({
				'data': None,
				'label': '%s%s-' % (val, i)
			})

	return matches

#---------------------------------------------------------------------------
def __explicit_offset2py_dt(str2parse, offset_chars=None):
	"""Default is 'hdwmy':
			h - hours
			d - days
			w - weeks
			m - months
			y - years

		This also defines the significance of the order of the characters.
	"""
	if offset_chars is None:
		offset_chars = _('hdwmy (single character date offset triggers)')[:5].lower()

	str2parse = str2parse.replace(' ', '').replace('\t', '')
	# "+/-XXXh/d/w/m/t"
	if regex.fullmatch(r"(\+|-){,1}\d{1,3}[%s]" % offset_chars, str2parse) is None:
		return []

	offset_val = int(str2parse[:-1])
	offset_char = str2parse[-1:]
	is_past = str2parse.startswith('-')
	now = pydt_now_here()
	ts = None

	# hours
	if offset_char == offset_chars[0]:
		ts = pydt_add(now, hours = offset_val)
		if is_past:
			label = _('%d hour(s) ago: %s') % (abs(offset_val), ts.strftime('%H:%M'))
		else:
			label = _('in %d hour(s): %s') % (offset_val, ts.strftime('%H:%M'))
	# days
	elif offset_char == offset_chars[1]:
		ts = pydt_add(now, days = offset_val)
		if is_past:
			label = _('%d day(s) ago: %s') % (abs(offset_val), ts.strftime('%A, %Y-%m-%d'))
		else:
			label = _('in %d day(s): %s') % (offset_val, ts.strftime('%A, %Y-%m-%d'))
	# weeks
	elif offset_char == offset_chars[2]:
		ts = pydt_add(now, weeks = offset_val)
		if is_past:
			label = _('%d week(s) ago: %s') % (abs(offset_val), ts.strftime('%A, %Y-%m-%d'))
		else:
			label = _('in %d week(s): %s') % (offset_val, ts.strftime('%A, %Y-%m-%d'))
	# months
	elif offset_char == offset_chars[3]:
		ts = pydt_add(now, months = offset_val)
		if is_past:
			label = _('%d month(s) ago: %s') % (abs(offset_val), ts.strftime('%A, %Y-%m-%d'))
		else:
			label = _('in %d month(s): %s') % (offset_val, ts.strftime('%A, %Y-%m-%d'))
	# years
	elif offset_char == offset_chars[4]:
		ts = pydt_add(now, years = offset_val)
		if is_past:
			label = _('%d year(s) ago: %s') % (abs(offset_val), ts.strftime('%A, %Y-%m-%d'))
		else:
			label = _('in %d year(s): %s') % (offset_val, ts.strftime('%A, %Y-%m-%d'))

	if ts is None:
		return []

	return [{'data': ts, 'label': label}]

#---------------------------------------------------------------------------
def str2pydt_matches(str2parse=None, patterns=None):
	"""Turn a string into candidate dates and auto-completions the user is likely to type.

	You MUST have called locale.setlocale(locale.LC_ALL, '')
	somewhere in your code previously.

	@param patterns: list of time.strptime compatible date pattern
	@type patterns: list
	"""
	matches = []
	matches.extend(__single_dot2py_dt(str2parse))
	matches.extend(__numbers_only2py_dt(str2parse))
	matches.extend(__single_slash2py_dt(str2parse))
	matches.extend(__single_char2py_dt(str2parse))
	matches.extend(__explicit_offset2py_dt(str2parse))

	# apply explicit patterns
	if patterns is None:
		patterns = []

	patterns.append('%Y-%m-%d')
	patterns.append('%y-%m-%d')
	patterns.append('%Y/%m/%d')
	patterns.append('%y/%m/%d')

	patterns.append('%d-%m-%Y')
	patterns.append('%d-%m-%y')
	patterns.append('%d/%m/%Y')
	patterns.append('%d/%m/%y')
	patterns.append('%d.%m.%Y')

	patterns.append('%m-%d-%Y')
	patterns.append('%m-%d-%y')
	patterns.append('%m/%d/%Y')
	patterns.append('%m/%d/%y')

	patterns.append('%Y.%m.%d')

	parts = str2parse.split(maxsplit = 1)
	hour = 11
	minute = 11
	second = 11
	if len(parts) > 1:
		for pattern in ['%H:%M', '%H:%M:%S']:
			try:
				date = pyDT.datetime.strptime(parts[1], pattern)
				hour = date.hour
				minute = date.minute
				second = date.second
				break
			except ValueError:
				# C-level overflow
				continue
	for pattern in patterns:
		try:
			date = pyDT.datetime.strptime(parts[0], pattern).replace (
				hour = hour,
				minute = minute,
				second = second,
				tzinfo = gmCurrentLocalTimezone
			)
			matches.append ({
				'data': date,
				'label': pydt_strftime(date, format = '%Y-%m-%d', accuracy = acc_days)
			})
		except ValueError:
			# C-level overflow
			continue


	return matches

#===========================================================================
# string -> fuzzy timestamp parser
#---------------------------------------------------------------------------
def __single_slash(str2parse):
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
	now = pydt_now_here()
	# "xx/yyyy"
	if regex.match("^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}(\s|\t)*$", str2parse, flags = regex.UNICODE):
		parts = regex.findall('\d+', str2parse, flags = regex.UNICODE)
		month = int(parts[0])
		if month in range(1, 13):
			fts = cFuzzyTimestamp (
				timestamp = now.replace(year = int(parts[1], month = month)),
				accuracy = acc_months
			)
			matches.append ({
				'data': fts,
				'label': fts.format_accurately()
			})
	# "xx/"
	elif regex.match("^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*$", str2parse, flags = regex.UNICODE):
		val = int(regex.findall('\d+', str2parse, flags = regex.UNICODE)[0])

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
			ts = now.replace(year = now.year + 1)
			matches.append ({
				'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_months),
				'label': '%.2d/%s' % (val, ts.year)
			})
			ts = now.replace(year = now.year - 1)
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

	return matches

#---------------------------------------------------------------------------
def __numbers_only(str2parse):
	"""This matches on single numbers.

	Spaces or tabs are discarded.
	"""
	if not regex.match("^(\s|\t)*\d{1,4}(\s|\t)*$", str2parse, flags = regex.UNICODE):
		return []

	val = int(regex.findall('\d{1,4}', str2parse, flags = regex.UNICODE)[0])
	if val == 0:
		return []

	now = pydt_now_here()
	matches = []
	# today in that year
	if (1850 < val) and (val < 2100):
		target_date = cFuzzyTimestamp (
			timestamp = now.replace(year = val),
			accuracy = acc_years
		)
		tmp = {
			'data': target_date,
			'label': '%s' % target_date
		}
		matches.append(tmp)

	# day X of this month
	if val <= gregorian_month_length[now.month]:
		ts = now.replace(day = val)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (this month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		}
		matches.append(tmp)

	# day X of next month
	next_month = get_next_month(now)
	if val <= gregorian_month_length[next_month]:
		ts = now.replace(day = val, month = next_month)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (next month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		}
		matches.append(tmp)

	# day X of last month
	last_month = get_last_month(now)
	if val <= gregorian_month_length[last_month]:
		ts = now.replace(day = val, month = last_month)
		target_date = cFuzzyTimestamp (
			timestamp = ts,
			accuracy = acc_days
		)
		tmp = {
			'data': target_date,
			'label': _('%d. of %s (last month) - a %s') % (val, ts.strftime('%B'), ts.strftime('%A'))
		}
		matches.append(tmp)

	# X days from now
	if val <= 400:				# more than a year ahead in days ?? nah !
		target_date = cFuzzyTimestamp(timestamp = now + pyDT.timedelta(days = val))
		tmp = {
			'data': target_date,
			'label': _('in %d day(s) - %s') % (val, target_date.timestamp.strftime('%A, %Y-%m-%d'))
		}
		matches.append(tmp)

	# X weeks from now
	if val <= 50:				# pregnancy takes about 40 weeks :-)
		target_date = cFuzzyTimestamp(timestamp = now + pyDT.timedelta(weeks = val))
		tmp = {
			'data': target_date,
			'label': _('in %d week(s) - %s') % (val, target_date.timestamp.strftime('%A, %Y-%m-%d'))
		}
		matches.append(tmp)

	# month X of ...
	if val < 13:
		# ... this year
		target_date = cFuzzyTimestamp (
			timestamp = pydt_replace(now, month = val, strict = False),
			accuracy = acc_months
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s this year)') % (target_date, ts.strftime('%B'))
		}
		matches.append(tmp)

		# ... next year
		target_date = cFuzzyTimestamp (
			timestamp = pydt_add(pydt_replace(now, month = val, strict = False), years = 1),
			accuracy = acc_months
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s next year)') % (target_date, ts.strftime('%B'))
		}
		matches.append(tmp)

		# ... last year
		target_date = cFuzzyTimestamp (
			timestamp = pydt_add(pydt_replace(now, month = val, strict = False), years = -1),
			accuracy = acc_months
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

	# reactivate when mxDT becomes available on py3k
#	# day X of ...
#	if val < 8:
#		# ... this week
#		ts = now + mxDT.RelativeDateTime(weekday = (val-1, 0))
#		target_date = cFuzzyTimestamp (
#			timestamp = ts,
#			accuracy = acc_days
#		)
#		tmp = {
#			'data': target_date,
#			'label': _('%s this week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		}
#		matches.append(tmp)
#
#		# ... next week
#		ts = now + mxDT.RelativeDateTime(weeks = +1, weekday = (val-1, 0))
#		target_date = cFuzzyTimestamp (
#			timestamp = ts,
#			accuracy = acc_days
#		)
#		tmp = {
#			'data': target_date,
#			'label': _('%s next week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		}
#		matches.append(tmp)

#		# ... last week
#		ts = now + mxDT.RelativeDateTime(weeks = -1, weekday = (val-1, 0))
#		target_date = cFuzzyTimestamp (
#			timestamp = ts,
#			accuracy = acc_days
#		)
#		tmp = {
#			'data': target_date,
#			'label': _('%s last week (%s of %s)') % (ts.strftime('%A'), ts.day, ts.strftime('%B'))
#		}
#		matches.append(tmp)

	if val < 100:
		matches.append ({
			'data': None,
			'label': '%s/' % (1900 + val)
		})

	# year 2k
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
def str2fuzzy_timestamp_matches(str2parse=None, default_time=None, patterns=None):
	"""
	Turn a string into candidate fuzzy timestamps and auto-completions the user is likely to type.

	You MUST have called locale.setlocale(locale.LC_ALL, '')
	somewhere in your code previously.

	@param default_time: if you want to force the time part of the time
		stamp to a given value and the user doesn't type any time part
		this value will be used
	@type default_time: an mx.DateTime.DateTimeDelta instance

	@param patterns: list of [time.strptime compatible date/time pattern, accuracy]
	@type patterns: list
	"""
	matches = []

	matches.extend(__numbers_only(str2parse))
	matches.extend(__single_slash(str2parse))

	matches.extend ([
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = acc_days),
			'label': m['label']
		} for m in __single_dot2py_dt(str2parse)
	])
	matches.extend ([
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = acc_days),
			'label': m['label']
		} for m in __single_char2py_dt(str2parse)
	])
	matches.extend ([
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = acc_days),
			'label': m['label']
		} for m in __explicit_offset2py_dt(str2parse)
	])

	if patterns is None:
		patterns = []
	patterns.extend([
		'%Y-%m-%d',
		'%y-%m-%d',
		'%Y/%m/%d',
		'%y/%m/%d',
		'%d-%m-%Y',
		'%d-%m-%y',
		'%d/%m/%Y',
		'%d/%m/%y',
		'%d.%m.%Y',
		'%m-%d-%Y',
		'%m-%d-%y',
		'%m/%d/%Y',
		'%m/%d/%y'
	])

	parts = str2parse.split(maxsplit = 1)
	hour = 11
	minute = 11
	second = 11
	acc = acc_days
	if len(parts) > 1:
		for pattern in ['%H:%M', '%H:%M:%S']:
			try:
				date = pyDT.datetime.strptime(parts[1], pattern)
				hour = date.hour
				minute = date.minute
				second = date.second
				acc = acc_minutes
				break
			except ValueError:
				# C-level overflow
				continue
	for pattern in patterns:
		try:
			ts = pyDT.datetime.strptime(parts[0], pattern).replace (
				hour = hour,
				minute = minute,
				second = second,
				tzinfo = gmCurrentLocalTimezone
			)
			fts = cFuzzyTimestamp(timestamp = ts, accuracy = acc)
			matches.append ({
				'data': fts,
				'label': fts.format_accurately()
			})
		except ValueError:
			# C-level overflow
			continue
	return matches

#===========================================================================
# fuzzy timestamp class
#---------------------------------------------------------------------------
class cFuzzyTimestamp:

	# FIXME: add properties for year, month, ...

	"""A timestamp implementation with definable inaccuracy.

	This class contains an datetime.datetime instance to
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
			timestamp = pydt_now_here()
			accuracy = acc_subseconds
			modifier = ''

		if (accuracy < 1) or (accuracy > 8):
			raise ValueError('%s.__init__(): <accuracy> must be between 1 and 8' % self.__class__.__name__)

		if not isinstance(timestamp, pyDT.datetime):
			raise TypeError('%s.__init__(): <timestamp> must be of datetime.datetime type, but is %s' % self.__class__.__name__, type(timestamp))

		if timestamp.tzinfo is None:
			raise ValueError('%s.__init__(): <tzinfo> must be defined' % self.__class__.__name__)

		self.timestamp = timestamp
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
	def format_accurately(self, accuracy=None):
		if accuracy is None:
			accuracy = self.accuracy

		if accuracy == acc_years:
			return str(self.timestamp.year)

		if accuracy == acc_months:
			return self.timestamp.strftime('%m/%Y')	# FIXME: use 3-letter month ?

		if accuracy == acc_weeks:
			return self.timestamp.strftime('%m/%Y')	# FIXME: use 3-letter month ?

		if accuracy == acc_days:
			return self.timestamp.strftime('%Y-%m-%d')

		if accuracy == acc_hours:
			return self.timestamp.strftime("%Y-%m-%d %I%p")

		if accuracy == acc_minutes:
			return self.timestamp.strftime("%Y-%m-%d %H:%M")

		if accuracy == acc_seconds:
			return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

		if accuracy == acc_subseconds:
			return self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")

		raise ValueError('%s.format_accurately(): <accuracy> (%s) must be between 1 and 7' % (
			self.__class__.__name__,
			accuracy
		))

	#-----------------------------------------------------------------------
	def get_pydt(self):
		return self.timestamp

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != "test":
		sys.exit()

	from Gnumed.pycommon import gmI18N
	from Gnumed.pycommon import gmLog2

	#-----------------------------------------------------------------------
	intervals_as_str = [
		'7', '12', ' 12', '12 ', ' 12 ', '	12	', '0', '~12', '~ 12', ' ~ 12', '	~	12 ',
		'12a', '12 a', '12	a', '12j', '12J', '12y', '12Y', '	~ 	12	a	 ', '~0a',
		'12m', '17 m', '12	m', '17M', '	~ 	17	m	 ', ' ~ 3	/ 12	', '7/12', '0/12',
		'12w', '17 w', '12	w', '17W', '	~ 	17	w	 ', ' ~ 15	/ 52', '2/52', '0/52',
		'12d', '17 d', '12	t', '17D', '	~ 	17	T	 ', ' ~ 12	/ 7', '3/7', '0/7',
		'12h', '17 h', '12	H', '17H', '	~ 	17	h	 ', ' ~ 36	/ 24', '7/24', '0/24',
		' ~ 36	/ 60', '7/60', '190/60', '0/60',
		'12a1m', '12 a 1  M', '12	a17m', '12j		12m', '12J7m', '12y7m', '12Y7M', '	~ 	12	a	 37 m	', '~0a0m',
		'10m1w',
		'invalid interval input'
	]
	#-----------------------------------------------------------------------
	def test_format_interval():
		intv = pyDT.timedelta(minutes=1, seconds=2)
		for acc in _accuracy_strings:
			print ('[%s]: "%s" -> "%s"' % (acc, intv, format_interval(intv, acc)))
		return

		for tmp in intervals_as_str:
			intv = str2interval(str_interval = tmp)
			if intv is None:
				print(tmp, '->', intv)
				continue
			for acc in _accuracy_strings:
				print ('[%s]: "%s" -> "%s"' % (acc, tmp, format_interval(intv, acc)))

	#-----------------------------------------------------------------------
	def test_format_interval_medically():

		intervals = [
			pyDT.timedelta(seconds = 1),
			pyDT.timedelta(seconds = 5),
			pyDT.timedelta(seconds = 30),
			pyDT.timedelta(seconds = 60),
			pyDT.timedelta(seconds = 94),
			pyDT.timedelta(seconds = 120),
			pyDT.timedelta(minutes = 5),
			pyDT.timedelta(minutes = 30),
			pyDT.timedelta(minutes = 60),
			pyDT.timedelta(minutes = 90),
			pyDT.timedelta(minutes = 120),
			pyDT.timedelta(minutes = 200),
			pyDT.timedelta(minutes = 400),
			pyDT.timedelta(minutes = 600),
			pyDT.timedelta(minutes = 800),
			pyDT.timedelta(minutes = 1100),
			pyDT.timedelta(minutes = 2000),
			pyDT.timedelta(minutes = 3500),
			pyDT.timedelta(minutes = 4000),
			pyDT.timedelta(hours = 1),
			pyDT.timedelta(hours = 2),
			pyDT.timedelta(hours = 4),
			pyDT.timedelta(hours = 8),
			pyDT.timedelta(hours = 12),
			pyDT.timedelta(hours = 20),
			pyDT.timedelta(hours = 23),
			pyDT.timedelta(hours = 24),
			pyDT.timedelta(hours = 25),
			pyDT.timedelta(hours = 30),
			pyDT.timedelta(hours = 48),
			pyDT.timedelta(hours = 98),
			pyDT.timedelta(hours = 120),
			pyDT.timedelta(days = 1),
			pyDT.timedelta(days = 2),
			pyDT.timedelta(days = 4),
			pyDT.timedelta(days = 16),
			pyDT.timedelta(days = 29),
			pyDT.timedelta(days = 30),
			pyDT.timedelta(days = 31),
			pyDT.timedelta(days = 37),
			pyDT.timedelta(days = 40),
			pyDT.timedelta(days = 47),
			pyDT.timedelta(days = 126),
			pyDT.timedelta(days = 127),
			pyDT.timedelta(days = 128),
			pyDT.timedelta(days = 300),
			pyDT.timedelta(days = 359),
			pyDT.timedelta(days = 360),
			pyDT.timedelta(days = 361),
			pyDT.timedelta(days = 362),
			pyDT.timedelta(days = 363),
			pyDT.timedelta(days = 364),
			pyDT.timedelta(days = 365),
			pyDT.timedelta(days = 366),
			pyDT.timedelta(days = 367),
			pyDT.timedelta(days = 400),
			pyDT.timedelta(weeks = 53 * 30),
			pyDT.timedelta(weeks = 53 * 79, days = 33)
		]
		idx = 1
		for intv in intervals:
			print ('%s) %s -> %s' % (idx, intv, format_interval_medically(intv)))
			idx += 1
	#-----------------------------------------------------------------------
	def test_str2interval():
		print ("testing str2interval()")
		print ("----------------------")

		for interval_as_str in intervals_as_str:
			print ("input: <%s>" % interval_as_str)
			print ("  ==>", str2interval(str_interval=interval_as_str))

		return True
	#-------------------------------------------------
	def test_date_time():
		print ("DST currently in effect:", dst_currently_in_effect)
		print ("current UTC offset:", current_local_utc_offset_in_seconds, "seconds")
		#print ("current timezone (interval):", current_local_timezone_interval)
		print ("current timezone (ISO conformant numeric string):", current_local_iso_numeric_timezone_string)
		print ("local timezone class:", cPlatformLocalTimezone)
		print ("")
		tz = cPlatformLocalTimezone()
		print ("local timezone instance:", tz)
		print (" (total) UTC offset:", tz.utcoffset(pyDT.datetime.now()))
		print (" DST adjustment:", tz.dst(pyDT.datetime.now()))
		print (" timezone name:", tz.tzname(pyDT.datetime.now()))
		print ("")
		print ("current local timezone:", gmCurrentLocalTimezone)
		print (" (total) UTC offset:", gmCurrentLocalTimezone.utcoffset(pyDT.datetime.now()))
		print (" DST adjustment:", gmCurrentLocalTimezone.dst(pyDT.datetime.now()))
		print (" timezone name:", gmCurrentLocalTimezone.tzname(pyDT.datetime.now()))
		print ("")
		print ("now here:", pydt_now_here())
		print ("")

	#-------------------------------------------------
	def test_str2fuzzy_timestamp_matches():
		print ("testing function str2fuzzy_timestamp_matches")
		print ("--------------------------------------------")

		val = None
		while val != 'exit':
			val = input('Enter date fragment ("exit" quits): ')
			matches = str2fuzzy_timestamp_matches(str2parse = val)
			for match in matches:
				print ('label shown  :', match['label'])
				print ('data attached:', match['data'], match['data'].timestamp)
				print ("")
			print ("---------------")

	#-------------------------------------------------
	def test_cFuzzyTimeStamp():
		print ("testing fuzzy timestamp class")
		print ("-----------------------------")

		fts = cFuzzyTimestamp()
		print ("\nfuzzy timestamp <%s '%s'>" % ('class', fts.__class__.__name__))
		for accuracy in range(1,8):
			fts.accuracy = accuracy
			print ("  accuracy         : %s (%s)" % (accuracy, _accuracy_strings[accuracy]))
			print ("  format_accurately:", fts.format_accurately())
			print ("  strftime()       :", fts.strftime('%Y %b %d  %H:%M:%S'))
			print ("  print ...        :", fts)
			print ("  print '%%s' %% ... : %s" % fts)
			print ("  str()            :", str(fts))
			print ("  repr()           :", repr(fts))
			input('press ENTER to continue')

	#-------------------------------------------------
	def test_get_pydt():
		print ("testing platform for handling dates before 1970")
		print ("-----------------------------------------------")
		ts = mxDT.DateTime(1935, 4, 2)
		fts = cFuzzyTimestamp(timestamp=ts)
		print ("fts           :", fts)
		print ("fts.get_pydt():", fts.get_pydt())
	#-------------------------------------------------
	def test_calculate_apparent_age():
		# test leap year glitches
		start = pydt_now_here().replace(year = 2000).replace(month = 2).replace(day = 29)
		end = pydt_now_here().replace(year = 2012).replace(month = 2).replace(day = 27)
		print ("start is leap year: 29.2.2000")
		print (" ", calculate_apparent_age(start = start, end = end))
		print (" ", format_apparent_age_medically(calculate_apparent_age(start = start)))

		start = pydt_now_here().replace(month = 10).replace(day = 23).replace(year = 1974)
		end = pydt_now_here().replace(year = 2012).replace(month = 2).replace(day = 29)
		print ("end is leap year: 29.2.2012")
		print (" ", calculate_apparent_age(start = start, end = end))
		print (" ", format_apparent_age_medically(calculate_apparent_age(start = start)))

		start = pydt_now_here().replace(year = 2000).replace(month = 2).replace(day = 29)
		end = pydt_now_here().replace(year = 2012).replace(month = 2).replace(day = 29)
		print ("start is leap year: 29.2.2000")
		print ("end is leap year: 29.2.2012")
		print (" ", calculate_apparent_age(start = start, end = end))
		print (" ", format_apparent_age_medically(calculate_apparent_age(start = start)))

		print ("leap year tests worked")

		start = pydt_now_here().replace(month = 10).replace(day = 23).replace(year = 1974)
		print (calculate_apparent_age(start = start))
		print (format_apparent_age_medically(calculate_apparent_age(start = start)))

		start = pydt_now_here().replace(month = 3).replace(day = 13).replace(year = 1979)
		print (calculate_apparent_age(start = start))
		print (format_apparent_age_medically(calculate_apparent_age(start = start)))

		start = pydt_now_here().replace(month = 2, day = 2).replace(year = 1979)
		end = pydt_now_here().replace(month = 3).replace(day = 31).replace(year = 1979)
		print (calculate_apparent_age(start = start, end = end))

		start = pydt_now_here().replace(month = 7, day = 21).replace(year = 2009)
		print (format_apparent_age_medically(calculate_apparent_age(start = start)))

		print ("-------")
		start = pydt_now_here().replace(month = 1).replace(day = 23).replace(hour = 12).replace(minute = 11).replace(year = 2011)
		print (calculate_apparent_age(start = start))
		print (format_apparent_age_medically(calculate_apparent_age(start = start)))
	#-------------------------------------------------
	def test_str2pydt():
		print ("testing function str2pydt_matches")
		print ("---------------------------------")

		val = None
		while val != 'exit':
			val = input('Enter date fragment ("exit" quits): ')
			matches = str2pydt_matches(str2parse = val)
			for match in matches:
				print ('label shown  :', match['label'])
				print ('data attached:', match['data'])
				print ("")
			print ("---------------")

	#-------------------------------------------------
	def test_pydt_strftime():
		dt = pydt_now_here()
		print (pydt_strftime(dt, '-(%Y %b %d)-'))
		print (pydt_strftime(dt))
		print (pydt_strftime(dt, accuracy = acc_days))
		print (pydt_strftime(dt, accuracy = acc_minutes))
		print (pydt_strftime(dt, accuracy = acc_seconds))
		dt = dt.replace(year = 1899)
		print (pydt_strftime(dt))
		print (pydt_strftime(dt, accuracy = acc_days))
		print (pydt_strftime(dt, accuracy = acc_minutes))
		print (pydt_strftime(dt, accuracy = acc_seconds))
		dt = dt.replace(year = 198)
		print (pydt_strftime(dt, accuracy = acc_seconds))
	#-------------------------------------------------
	def test_is_leap_year():
		for idx in range(120):
			year = 1993 + idx
			tmp, offset = divmod(idx, 4)
			if is_leap_year(year):
				print (offset+1, '--', year, 'leaps')
			else:
				print (offset+1, '--', year)

	#-------------------------------------------------
	def test_get_date_of_weekday_in_week_of_date():
		dt = pydt_now_here()
		print('weekday', dt.isoweekday(), '(2day):', dt)
		for weekday in range(8):
			dt = get_date_of_weekday_in_week_of_date(weekday)
			print('weekday', weekday, '(same):', dt)
			dt = get_date_of_weekday_following_date(weekday)
			print('weekday', weekday, '(next):', dt)
		try:
			get_date_of_weekday_in_week_of_date(8)
		except ValueError as exc:
			print(exc)
		try:
			get_date_of_weekday_following_date(8)
		except ValueError as exc:
			print(exc)

	#-------------------------------------------------
	def test__numbers_only():
		for val in range(-1, 35):
			matches = __numbers_only(str(val))
			print(val, ':')
			for m in matches:
				print('  ', m)
			input()

	#-------------------------------------------------
	# GNUmed libs
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	init()

	#test_date_time()
	#test_str2fuzzy_timestamp_matches()
	#test_get_date_of_weekday_in_week_of_date()
	#test_cFuzzyTimeStamp()
	#test_get_pydt()
	#test_str2interval()
	#test_format_interval()
	#test_format_interval_medically()
	#test_str2pydt()
	#test_pydt_strftime()
	#test_calculate_apparent_age()
	#test_is_leap_year()
	test__numbers_only()

#===========================================================================
