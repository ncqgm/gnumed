# -*- coding: utf-8 -*-

"""GNUmed date/time handling.

This modules provides access to date/time handling
and offers an fuzzy timestamp implementation

It utilizes

	- Python time
	- Python datetime

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
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# stdlib
import sys
import datetime as pyDT
import time
import os
import re as regex
import logging
from typing import Callable


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	# we are the main script, setup a fake _() for now,
	# such that it can be used in module level definitions
	_ = lambda x:x
else:
	# we are being imported from elsewhere, say, mypy or some such
	try:
		# do we already have _() ?
		_
	except NameError:
		# no, setup i18n handling
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_log = logging.getLogger('gm.datetime')

dst_locally_in_use = None
dst_currently_in_effect = None

py_timezone_name = None
py_dst_timezone_name = None
current_local_utc_offset_in_seconds = None
current_local_iso_numeric_timezone_string = None
current_local_timezone_name = None

gmCurrentLocalTimezone = None

(	ACC_YEARS,
	ACC_MONTHS,
	ACC_WEEKS,
	ACC_DAYS,
	ACC_HOURS,
	ACC_MINUTES,
	ACC_SECONDS,
	ACC_SUBSECONDS
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

AVG_DAYS_PER_GREGORIAN_YEAR = 365
AVG_DAYS_PER_GREGORIAN_MONTH = 30
AVG_SECONDS_PER_DAY = 24 * 60 * 60
DAYS_PER_WEEK = 7

#===========================================================================
# module init
#---------------------------------------------------------------------------
def init():
	"""Initialize date/time handling and log date/time environment."""

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

	global current_local_iso_numeric_timezone_string
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
class cPlatformLocalTimezone(pyDT.tzinfo):
	"""Local timezone implementation (lifted from the docs).

	A class capturing the platform's idea of local time.

	May result in wrong values on historical times in
	timezones where UTC offset and/or the DST rules had
	changed in the past."""
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
			_log.exception('overflow in time.mktime(%s), assuming non-DST', tt)
			return False

		tt = time.localtime(stamp)
		return tt.tm_isdst > 0

#===========================================================================
# convenience functions
#---------------------------------------------------------------------------
def get_next_month(dt:pyDT.datetime):
	next_month = dt.month + 1
	return 1 if next_month == 13 else next_month

#---------------------------------------------------------------------------
def get_last_month(dt:pyDT.datetime):
	last_month = dt.month - 1
	return 12 if last_month == 0 else last_month

#---------------------------------------------------------------------------
def get_date_of_weekday_in_week_of_date(weekday:int, base_dt:pyDT.datetime=None) -> pyDT.datetime:
	# weekday:
	# 0 = Sunday
	# 1 = Monday ...
	assert weekday in [0,1,2,3,4,5,6,7], 'weekday must be in 0 (Sunday) to 7 (Sunday, again)'

	if base_dt is None:
		base_dt = pydt_now_here()
	dt_weekday = base_dt.isoweekday()		# 1 = Mon
	day_diff = dt_weekday - weekday
	days2add = (-1 * day_diff)
	return pydt_add(base_dt, days = days2add)

#---------------------------------------------------------------------------
def get_date_of_weekday_following_date(weekday, base_dt:pyDT.datetime=None):
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

#---------------------------------------------------------------------------
def format_dob(dob:pyDT.datetime, format:str='%Y %b %d', none_string:str=None, dob_is_estimated:bool=False) -> str:
	if dob is None:
		return none_string if none_string else _('** DOB unknown **')

	dob_txt = dob.strftime(format)
	if dob_is_estimated:
		dob_txt = '\u2248' + dob_txt
	return dob_txt

#---------------------------------------------------------------------------
def pydt_strftime(dt:pyDT.datetime=None, format:str='%Y %b %d  %H:%M.%S', none_str:str=None):
	if dt is None:
		if none_str is not None:	# can be '', though ...
			return none_str
		raise ValueError('must provide <none_str> if <dt>=None is to be dealt with')

	try:
		return dt.strftime(format)

	except ValueError:
		_log.exception('strftime() error')
		return 'strftime() error'

#---------------------------------------------------------------------------
def pydt_add (
	dt:pyDT.datetime,
	years:int=0,
	months:int=0,
	weeks:int=0,
	days:int=0,
	hours:int=0,
	minutes:int=0,
	seconds:int=0,
	milliseconds:int=0,
	microseconds:int=0
) -> pyDT.datetime:
	"""Add some time to a given datetime."""
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
def pydt_replace (
	dt:pyDT.datetime,
	strict=True,
	year=None,
	month=None,
	day=None,
	hour=None,
	minute=None,
	second=None,
	microsecond=None,
	tzinfo=None
) -> pyDT.datetime:
	"""Replace parts of a datetime.

	Python's datetime.replace() fails if the target datetime
	does not exist (say, going from October 31st to November
	'31st' by replacing the month). This code can take heed
	of such things, when <strict> is False. The result will
	not be mathematically correct but likely what's meant in
	real live (last of October -> last of November). This
	can be particularly striking when going from January
	31st to February 28th (!) in non-leap years ...

	Args:
		strict: adjust - or not - for impossible target datetimes
	"""
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
def pydt_is_same_day(dt1, dt2):
	if dt1.day != dt2.day:
		return False
	if dt1.month != dt2.month:
		return False
	if dt1.year != dt2.year:
		return False

	return True

#---------------------------------------------------------------------------
def pydt_is_today(dt):
	"""Check whether <dt> is today."""
	if not dt:
		return None

	now = pyDT.datetime.now(gmCurrentLocalTimezone)
	return pydt_is_same_day(dt, now)

#---------------------------------------------------------------------------
def pydt_is_yesterday(dt):
	"""Check whether <dt> is yesterday."""
	if not dt:
		return None

	yesterday = pyDT.datetime.now(gmCurrentLocalTimezone) - pyDT.timedelta(days = 1)
	return pydt_is_same_day(dt, yesterday)

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
def __get_time_part_tags(verbose:bool=False, time_parts:dict[str,int]=None) -> dict[str,str]:
	if verbose:
		return {
			'years': ' ' + (_('year') if time_parts['years'] == 1 else _('years')),
			'months': ' ' + (_('month') if time_parts['months'] == 1 else _('months')),
			'weeks': ' ' + (_('week') if time_parts['weeks'] == 1 else _('weeks')),
			'days': ' ' + (_('day') if time_parts['days'] == 1 else _('days')),
			'hours': ' ' + (_('hour') if time_parts['hours'] == 1 else _('hours')),
			'minutes': ' ' + (_('minute') if time_parts['minutes'] == 1 else _('minutes')),
			'seconds': ' ' + (_('second') if time_parts['seconds'] == 1 else _('seconds'))
		}

	return {
		'years': _('interval_format_tag::years::y')[-1],
		'months': _('interval_format_tag::months::m')[-1],
		'weeks': _('interval_format_tag::weeks::w')[-1],
		'days': _('interval_format_tag::days::d')[-1],
		'hours': '/24',
		'minutes': '/60',
		'seconds': _('interval_format_tag::seconds::s')[-1]
	}

#---------------------------------------------------------------------------
def __split_up_interval(interval) -> dict[str,int]:
	parts = {}
	parts['years'], leftover_days = divmod(interval.days, AVG_DAYS_PER_GREGORIAN_YEAR)
	parts['months'], leftover_days = divmod(leftover_days, AVG_DAYS_PER_GREGORIAN_MONTH)
	parts['weeks'], leftover_days = divmod(leftover_days, DAYS_PER_WEEK)
	leftover_seconds = (leftover_days * AVG_SECONDS_PER_DAY) + interval.seconds
	parts['days'], leftover_secs = divmod(leftover_seconds, AVG_SECONDS_PER_DAY)
	parts['hours'], leftover_secs = divmod(leftover_secs, 3600)
	parts['mins'], parts['secs'] = divmod(leftover_secs, 60)
	return parts

#---------------------------------------------------------------------------
def __format_interval__special_cases (
	parts:dict[str,int],
	tags:dict[str,str],
	accuracy_wanted:int,
	verbose:bool=False
) -> str | None:
	if parts['years'] == 0:
		if accuracy_wanted < ACC_MONTHS:
			return _('0 years') if verbose else '0%s' % tags['years']

	if parts['years'] + parts['months'] == 0:
		if accuracy_wanted < ACC_WEEKS:
			return _('0 months') if verbose else '0%s' % tags['months']

	if parts['years'] + parts['months'] + parts['weeks'] == 0:
		if accuracy_wanted < ACC_DAYS:
			return _('0 weeks') if verbose else '0%s' % tags['weeks']

	if parts['years'] + parts['months'] + parts['weeks'] + parts['days'] == 0:
		if accuracy_wanted < ACC_HOURS:
			return _('0 days') if verbose else '0%s' % tags['days']

	if parts['years'] + parts['months'] + parts['weeks'] + parts['days'] + parts['hours'] == 0:
		if accuracy_wanted < ACC_MINUTES:
			return _('0 hours') if verbose else '0/24'

	if parts['years'] + parts['months'] + parts['weeks'] + parts['days'] + parts['hours'] + parts['mins'] == 0:
		if accuracy_wanted < ACC_SECONDS:
			return _('0 minutes') if verbose else '0/60'

	if parts['years'] + parts['months'] + parts['weeks'] + parts['days'] + parts['hours'] + parts['mins'] + parts['secs'] == 0:
		return _('0 seconds') if verbose else '0s'

	return None

#---------------------------------------------------------------------------
def format_interval(interval=None, accuracy_wanted:int=None, none_string:str=None, verbose:bool=False) -> str:
	"""Formats an interval.
	"""
	if interval is None:
		return none_string

	if accuracy_wanted is None:
		accuracy_wanted = ACC_SECONDS
	parts = __split_up_interval(interval)
	tags = __get_time_part_tags(verbose = verbose, time_parts = parts)
	# special cases
	special_case_formatted = __format_interval__special_cases(parts, tags, accuracy_wanted)
	if special_case_formatted:
		return special_case_formatted

	# normal cases
	formatted_intv = ''
	if parts['years'] > 0:
		formatted_intv += '%s%s' % (int(parts['years']), tags['years'])
	if accuracy_wanted < ACC_MONTHS:
		return formatted_intv.strip()

	if parts['months'] > 0:
		formatted_intv += ' %s%s' % (int(parts['months']), tags['months'])
	if accuracy_wanted < ACC_WEEKS:
		return formatted_intv.strip()

	if parts['weeks'] > 0:
		formatted_intv += ' %s%s' % (int(parts['weeks']), tags['weeks'])
	if accuracy_wanted < ACC_DAYS:
		return formatted_intv.strip()

	if parts['days'] > 0:
		formatted_intv += ' %s%s' % (int(parts['days']), tags['days'])
	if accuracy_wanted < ACC_HOURS:
		return formatted_intv.strip()

	if parts['hours'] > 0:
		formatted_intv += ' %s%s' % (int(parts['hours']), tags['hours'])
	if accuracy_wanted < ACC_MINUTES:
		return formatted_intv.strip()

	if parts['mins'] > 0:
		formatted_intv += ' %s%s' % (int(parts['mins']), tags['minutes'])
	if accuracy_wanted < ACC_SECONDS:
		return formatted_intv.strip()

	if parts['secs'] > 0:
		formatted_intv += ' %s%s' % (int(parts['secs']), tags['seconds'])
	return formatted_intv.strip()

#---------------------------------------------------------------------------
def format_interval_medically(interval:pyDT.timedelta=None, terse:bool=False, approximation_prefix:str=None, zero_duration_strings:list[str]=None):
	"""Formats an interval.

		This isn't mathematically correct but close enough for display.

	Args:
		interval: the interval to format
		terse: output terse formatting or not
		approximation_mark: an approxiation mark to apply in the formatting, if any
		zero_duration_strings: a list of two strings, terse and verbose form, to return if a zero duration interval is to be formatted
	"""
	assert interval is not None, '<interval> must be given'

	if interval.total_seconds() == 0:
		if not zero_duration_strings:
			zero_duration_strings = [
				_('zero_duration_symbol::\u2300').removeprefix('zero_duration_symbol::'),
				_('zero_duration_text::no duration').removeprefix('zero_duration_text::')
			]
		if terse:
			return zero_duration_strings[0]
		return zero_duration_strings[1]

	spacer = '' if terse else ' '
	prefix = approximation_prefix if approximation_prefix else ''
	# more than 1 year ?
	if interval.days > 364:
		years, days = divmod(interval.days, AVG_DAYS_PER_GREGORIAN_YEAR)
		months, day = divmod(days, 30.33)
		if int(months) == 0:
			return '%s%s%s%s' % (
				prefix,
				spacer,
				int(years),
				_('interval_format_tag::years::y')[-1:]
			)

		return '%s%s%s%s%s%s%s' % (
			prefix,
			spacer,
			int(years),
			_('interval_format_tag::years::y')[-1:],
			spacer,
			int(months),
			_('interval_format_tag::months::m')[-1:]
		)

	# more than 30 days / 1 month ?
	if interval.days > 30:
		months, days = divmod(interval.days, 30.33)					# type: ignore [assignment]
		weeks, days = divmod(days, 7)
		result = '%s%s%s%s' % (
			prefix,
			spacer,
			int(months),
			_('interval_format_tag::months::m')[-1:]
		)
		if int(weeks) != 0:
			result += '%s%s%s' % (spacer, int(weeks), _('interval_format_tag::weeks::w')[-1:])
		if int(days) != 0:
			result += '%s%s%s' % (spacer, int(days), _('interval_format_tag::days::d')[-1:])
		return result

	# between 7 and 30 days ?
	if interval.days > 7:
		return '%s%s%s%s' % (prefix, spacer, interval.days, _('interval_format_tag::days::d')[-1:])

	# between 1 and 7 days ?
	if interval.days > 0:
		hours, seconds = divmod(interval.seconds, 3600)
		if hours == 0:
			return '%s%s%s%s' % (prefix, spacer, interval.days, _('interval_format_tag::days::d')[-1:])

		return "%s%s%s%s%s%sh" % (
			prefix,
			spacer,
			interval.days,
			_('interval_format_tag::days::d')[-1:],
			spacer,
			int(hours)
		)

	# between 5 hours and 1 day
	if interval.seconds > (5*3600):
		return '%s%s%sh' % (prefix, spacer, int(interval.seconds // 3600))

	# between 1 and 5 hours
	if interval.seconds > 3600:
		hours, seconds = divmod(interval.seconds, 3600)
		minutes = seconds // 60
		if minutes == 0:
			return '%s%s%sh' % (prefix, spacer, int(hours))
		return '%s:%02d' % (int(hours), int(minutes))

	# minutes only
	if interval.seconds > (5*60):
		return "0:%02d" % (int(interval.seconds // 60))

	# seconds
	minutes, seconds = divmod(interval.seconds, 60)
	if minutes == 0:
		return '%ss' % int(seconds)
	if seconds == 0:
		return '0:%02d' % int(minutes)
	return '%s.%ss' % (int(minutes), int(seconds))

#---------------------------------------------------------------------------
def format_pregnancy_weeks(age):
	weeks, days = divmod(age.days, 7)
	return '%s%s%s%s' % (
		int(weeks),
		_('interval_format_tag::weeks::w')[-1:],
		int(days),
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
def calculate_apparent_age(start=None, end=None) -> tuple:
	"""Calculate age in a way humans naively expect it.

	This does *not* take into account time zones which may
	shift the result by up to one day.

	Args:
		start: the beginning of the period-to-be-aged, the 'birth' if you will
		end: the end of the period, default *now*

	Returns:
		A tuple (years, ..., seconds) as simple differences
		between the fields:

			(years, months, days, hours, minutes, seconds)
	"""
	assert not((end is None) and (start is None)), 'one of <start> or <end> must be given'

	now = pyDT.datetime.now(gmCurrentLocalTimezone)
	if end is None:
		if start <= now:
			end = now
		else:
			end = start
			start = now
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
	if regex.match(r'^~*(\s|\t)*\d+(%s)*$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = (int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]) * AVG_DAYS_PER_GREGORIAN_YEAR))

	# "(~)12mM" - at age 12 months
	keys = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		years, months = divmod (
			int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * AVG_DAYS_PER_GREGORIAN_YEAR) + (months * AVG_DAYS_PER_GREGORIAN_MONTH)))

	# weeks
	keys = '|'.join(list(unit_keys['week'].replace('_keys_week', '')))
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(weeks = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# days
	keys = '|'.join(list(unit_keys['day'].replace('_keys_day', '')))
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# hours
	keys = '|'.join(list(unit_keys['hour'].replace('_keys_hour', '')))
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/12 - months
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*12$', str_interval, flags = regex.UNICODE):
		years, months = divmod (
			int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * AVG_DAYS_PER_GREGORIAN_YEAR) + (months * AVG_DAYS_PER_GREGORIAN_MONTH)))

	# x/52 - weeks
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*52$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(weeks = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/7 - days
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*7$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/24 - hours
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*24$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# x/60 - minutes
	if regex.match(r'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*60$', str_interval, flags = regex.UNICODE):
		return pyDT.timedelta(minutes = int(regex.findall(r'\d+', str_interval, flags = regex.UNICODE)[0]))

	# nYnM - years, months
	keys_year = '|'.join(list(unit_keys['year'].replace('_keys_year', '')))
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	if regex.match(r'^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_year, keys_month), str_interval, flags = regex.UNICODE):
		parts = regex.findall(r'\d+', str_interval, flags = regex.UNICODE)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pyDT.timedelta(days = ((years * AVG_DAYS_PER_GREGORIAN_YEAR) + (months * AVG_DAYS_PER_GREGORIAN_MONTH)))

	# nMnW - months, weeks
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', '')))
	keys_week = '|'.join(list(unit_keys['week'].replace('_keys_week', '')))
	if regex.match(r'^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_month, keys_week), str_interval, flags = regex.UNICODE):
		parts = regex.findall(r'\d+', str_interval, flags = regex.UNICODE)
		months, weeks = divmod(int(parts[1]), 4)
		months += int(parts[0])
		return pyDT.timedelta(days = ((months * AVG_DAYS_PER_GREGORIAN_MONTH) + (weeks * DAYS_PER_WEEK)))

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
	str2parse = str2parse.strip().casefold()
	if len(str2parse) != 1:
		return []

	if trigger_chars is None:
		trigger_chars = _('ndmy (single character date triggers)')[:4].casefold()

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
		offset_chars = _('hdwmy (single character date offset triggers)')[:5].casefold()

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
STR2PYDT_DEFAULT_PATTERNS = [
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
	'%m/%d/%y',
	'%Y.%m.%d'
]
"""Default patterns being passed to strptime()."""

STR2PYDT_PARSERS:list[Callable[[str], dict]] = [
	__single_dot2py_dt,
	__numbers_only2py_dt,
	__single_slash2py_dt,
	__single_char2py_dt,
	__explicit_offset2py_dt
]
"""Specialized parsers for string -> datetime conversion."""

#---------------------------------------------------------------------------
def str2pydt_matches(str2parse:str=None, patterns:list=None) -> list:
	"""Turn a string into candidate datetimes.

	Args:
		str2parse: string to turn into candidate datetimes
		patterns: additional patterns to try with strptime()

	A number of default patterns will be tried. Also, a few
	specialized parsers will be run. See the source for
	details.

	If the input contains a space followed by more characters
	matching either hour:minute or hour:minute:second that
	will be used as the time part of the datetime returned.
	Otherwise 11:11:11 will be used as default.

	Note: You must have previously called

		locale.setlocale(locale.LC_ALL, '')

	somewhere in your code.

	Returns:
		List of Python datetimes the input could be parsed as.
	"""
	matches:list[dict] = []
	for parser in STR2PYDT_PARSERS:
		matches.extend(parser(str2parse))
	hour = 11
	minute = 11
	second = 11
	lbl_fmt = '%Y-%m-%d'
	parts = str2parse.split(maxsplit = 1)
	if len(parts) > 1:
		for pattern in ['%H:%M', '%H:%M:%S']:
			try:
				date = pyDT.datetime.strptime(parts[1], pattern)
				hour = date.hour
				minute = date.minute
				second = date.second
				lbl_fmt = '%Y-%m-%d %H:%M'
				break
			except ValueError:		# C-level overflow
				continue
	if patterns is None:
		patterns = []
	patterns.extend(STR2PYDT_DEFAULT_PATTERNS)
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
				'label': date.strftime(lbl_fmt)
			})
		except ValueError:			# C-level overflow
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
	if regex.match(r"^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}(\s|\t)*$", str2parse, flags = regex.UNICODE):
		parts = regex.findall(r'\d+', str2parse, flags = regex.UNICODE)
		month = int(parts[0])
		if month in range(1, 13):
			fts = cFuzzyTimestamp (
				timestamp = now.replace(year = int(parts[1], month = month)),
				accuracy = ACC_MONTHS
			)
			matches.append ({
				'data': fts,
				'label': fts.format_accurately()
			})
	# "xx/"
	elif regex.match(r"^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*$", str2parse, flags = regex.UNICODE):
		val = int(regex.findall(r'\d+', str2parse, flags = regex.UNICODE)[0])

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
				'data': cFuzzyTimestamp(timestamp = now, accuracy = ACC_MONTHS),
				'label': '%.2d/%s' % (val, now.year)
			})
			ts = now.replace(year = now.year + 1)
			matches.append ({
				'data': cFuzzyTimestamp(timestamp = ts, accuracy = ACC_MONTHS),
				'label': '%.2d/%s' % (val, ts.year)
			})
			ts = now.replace(year = now.year - 1)
			matches.append ({
				'data': cFuzzyTimestamp(timestamp = ts, accuracy = ACC_MONTHS),
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
	if not regex.match(r"^(\s|\t)*\d{1,4}(\s|\t)*$", str2parse, flags = regex.UNICODE):
		return []

	val = int(regex.findall(r'\d{1,4}', str2parse, flags = regex.UNICODE)[0])
	if val == 0:
		return []

	now = pydt_now_here()
	matches = []
	# today in that year
	if (1850 < val) and (val < 2100):
		target_date = cFuzzyTimestamp (
			timestamp = now.replace(year = val),
			accuracy = ACC_YEARS
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
			accuracy = ACC_DAYS
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
			accuracy = ACC_DAYS
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
			accuracy = ACC_DAYS
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
			accuracy = ACC_MONTHS
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s this year)') % (target_date, ts.strftime('%B'))
		}
		matches.append(tmp)

		# ... next year
		target_date = cFuzzyTimestamp (
			timestamp = pydt_add(pydt_replace(now, month = val, strict = False), years = 1),
			accuracy = ACC_MONTHS
		)
		tmp = {
			'data': target_date,
			'label': _('%s (%s next year)') % (target_date, ts.strftime('%B'))
		}
		matches.append(tmp)

		# ... last year
		target_date = cFuzzyTimestamp (
			timestamp = pydt_add(pydt_replace(now, month = val, strict = False), years = -1),
			accuracy = ACC_MONTHS
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
#			accuracy = ACC_DAYS
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
#			accuracy = ACC_DAYS
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
#			accuracy = ACC_DAYS
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
			'data': cFuzzyTimestamp(timestamp = now, accuracy = ACC_DAYS),
			'label': '%s' % target_date
		}
		matches.append(tmp)
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = now, accuracy = ACC_MONTHS),
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
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = ACC_DAYS),
			'label': m['label']
		} for m in __single_dot2py_dt(str2parse)
	])
	matches.extend ([
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = ACC_DAYS),
			'label': m['label']
		} for m in __single_char2py_dt(str2parse)
	])
	matches.extend ([
		{	'data': cFuzzyTimestamp(timestamp = m['data'], accuracy = ACC_DAYS),
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
	acc = ACC_DAYS
	if len(parts) > 1:
		for pattern in ['%H:%M', '%H:%M:%S']:
			try:
				date = pyDT.datetime.strptime(parts[1], pattern)
				hour = date.hour
				minute = date.minute
				second = date.second
				acc = ACC_MINUTES
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

	The timestamp will have to be initialized with a fully
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
	def __init__(self, timestamp=None, accuracy=ACC_SUBSECONDS, modifier=''):

		if timestamp is None:
			timestamp = pydt_now_here()
			accuracy = ACC_SUBSECONDS
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

		if accuracy == ACC_YEARS:
			return str(self.timestamp.year)

		if accuracy == ACC_MONTHS:
			return self.timestamp.strftime('%m/%Y')	# FIXME: use 3-letter month ?

		if accuracy == ACC_WEEKS:
			return self.timestamp.strftime('%m/%Y')	# FIXME: use 3-letter month ?

		if accuracy == ACC_DAYS:
			return self.timestamp.strftime('%Y-%m-%d')

		if accuracy == ACC_HOURS:
			return self.timestamp.strftime("%Y-%m-%d %I%p")

		if accuracy == ACC_MINUTES:
			return self.timestamp.strftime("%Y-%m-%d %H:%M")

		if accuracy == ACC_SECONDS:
			return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

		if accuracy == ACC_SUBSECONDS:
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

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

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

		now = pydt_now_here()
		print(format_interval_medically(now - now, terse = False))
		print(format_interval_medically(now - now, terse = True))
		return

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
			pyDT.timedelta(weeks = 53 * 79, days = 33),
			pyDT.timedelta(days = 3650)
		]
		idx = 1
		for intv in intervals:
			print('%s) %s:' % (idx, intv))
			print(' -> %s // %s // %s // %s' % (
				format_interval_medically(intv, terse = False),
				format_interval_medically(intv, terse = False, approximation_prefix = '\u2248'),
				format_interval_medically(intv, terse = True),
				format_interval_medically(intv, terse = True, approximation_prefix = '\u2248')
			))
			idx += 1
			if idx / 20 in [1.0, 2.0, 3.0]:
				input('next')
		#intv = pyDT.timedelta(days = 3650)
		#print ('%s -> %s' % (intv, format_interval_medically(intv)))

	#-----------------------------------------------------------------------
	def test_str2interval():
		print ("testing str2interval()")
		print ("----------------------")

		for interval_as_str in intervals_as_str:
			print ("input: <%s>" % interval_as_str)
			print ("  ==>", str2interval(str_interval=interval_as_str))

		return True

	#-------------------------------------------------
	def test_local_tz():
		tz = cPlatformLocalTimezone()
		print ("local timezone instance:", tz)
		print (" (total) UTC offset:", tz.utcoffset(pyDT.datetime.now()))
		print (" DST adjustment:", tz.dst(pyDT.datetime.now()))
		print (" timezone name:", tz.tzname(pyDT.datetime.now()))
		print('SECOND:', tz._SECOND)
		print('non-DST offset:', tz._nonDST_OFFSET_FROM_UTC)
		print('DST offset:', tz._DST_OFFSET_FROM_UTC)
		print('shift:', tz._DST_SHIFT)

	#-------------------------------------------------
	def test_date_time():
		print ("DST currently in effect:", dst_currently_in_effect)
		print ("current UTC offset:", current_local_utc_offset_in_seconds, "seconds")
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
		#ts = mxDT.DateTime(1935, 4, 2)
		#fts = cFuzzyTimestamp(timestamp=ts)
		#print ("fts           :", fts)
		#print ("fts.get_pydt():", fts.get_pydt())
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
	def test_str2pydt_matches():
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
		print (pydt_strftime(dt))
		print (pydt_strftime(dt))
		print (pydt_strftime(dt))
		dt = dt.replace(year = 1899)
		print (pydt_strftime(dt))
		print (pydt_strftime(dt))
		print (pydt_strftime(dt))
		print (pydt_strftime(dt))
		dt = dt.replace(year = 198)
		print (pydt_strftime(dt))
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
	#test_str2pydt_matches()
	#test_get_date_of_weekday_in_week_of_date()
	#test_cFuzzyTimeStamp()
	#test_get_pydt()
	#test_str2interval()
	test_format_interval()
	#test_format_interval_medically()
	#test_pydt_strftime()
	#test_calculate_apparent_age()
	#test_is_leap_year()
	#test__numbers_only()
	#test_local_tz()

#===========================================================================
