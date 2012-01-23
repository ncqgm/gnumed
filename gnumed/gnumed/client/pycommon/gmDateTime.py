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
__version__ = "$Revision: 1.34 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# stdlib
import sys, datetime as pyDT, time, os, re as regex, locale, logging


# 3rd party
import mx.DateTime as mxDT
import psycopg2						# this will go once datetime has timezone classes


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N


_log = logging.getLogger('gm.datetime')
_log.info(__version__)
_log.info(u'mx.DateTime version: %s', mxDT.__version__)

dst_locally_in_use = None
dst_currently_in_effect = None

current_local_utc_offset_in_seconds = None
current_local_timezone_interval = None
current_local_iso_numeric_timezone_string = None
current_local_timezone_name = None
py_timezone_name = None
py_dst_timezone_name = None

cLocalTimezone = psycopg2.tz.LocalTimezone					# remove as soon as datetime supports timezone classes
cFixedOffsetTimezone = psycopg2.tz.FixedOffsetTimezone		# remove as soon as datetime supports timezone classes
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

	_log.debug('mx.DateTime.now(): [%s]' % mxDT.now())
	_log.debug('datetime.now()   : [%s]' % pyDT.datetime.now())
	_log.debug('time.localtime() : [%s]' % str(time.localtime()))
	_log.debug('time.gmtime()    : [%s]' % str(time.gmtime()))

	try:
		_log.debug('$TZ: [%s]' % os.environ['TZ'])
	except KeyError:
		_log.debug('$TZ not defined')

	_log.debug('time.daylight: [%s] (whether or not DST is locally used at all)' % time.daylight)
	_log.debug('time.timezone: [%s] seconds' % time.timezone)
	_log.debug('time.altzone : [%s] seconds' % time.altzone)
	_log.debug('time.tzname  : [%s / %s] (non-DST / DST)' % time.tzname)
	_log.debug('mx.DateTime.now().gmtoffset(): [%s]' % mxDT.now().gmtoffset())

	global py_timezone_name
	py_timezone_name = time.tzname[0].decode(gmI18N.get_encoding(), 'replace')

	global py_dst_timezone_name
	py_dst_timezone_name = time.tzname[1].decode(gmI18N.get_encoding(), 'replace')

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

	if current_local_utc_offset_in_seconds > 0:
		_log.debug('UTC offset is positive, assuming EAST of Greenwich (clock is "ahead")')
	elif current_local_utc_offset_in_seconds < 0:
		_log.debug('UTC offset is negative, assuming WEST of Greenwich (clock is "behind")')
	else:
		_log.debug('UTC offset is ZERO, assuming Greenwich Time')

	global current_local_timezone_interval
	current_local_timezone_interval = mxDT.now().gmtoffset()
	_log.debug('ISO timezone: [%s] (taken from mx.DateTime.now().gmtoffset())' % current_local_timezone_interval)

	global current_local_iso_numeric_timezone_string
	current_local_iso_numeric_timezone_string = str(current_local_timezone_interval).replace(',', '.')

	global current_local_timezone_name
	try:
		current_local_timezone_name = os.environ['TZ'].decode(gmI18N.get_encoding(), 'replace')
	except KeyError:
		if dst_currently_in_effect:
			current_local_timezone_name = time.tzname[1].decode(gmI18N.get_encoding(), 'replace')
		else:
			current_local_timezone_name = time.tzname[0].decode(gmI18N.get_encoding(), 'replace')

	# do some magic to convert Python's timezone to a valid ISO timezone
	# is this safe or will it return things like 13.5 hours ?
	#_default_client_timezone = "%+.1f" % (-tz / 3600.0)
	#_log.info('assuming default client time zone of [%s]' % _default_client_timezone)

	global gmCurrentLocalTimezone
	gmCurrentLocalTimezone = cFixedOffsetTimezone (
		offset = (current_local_utc_offset_in_seconds / 60),
		name = current_local_iso_numeric_timezone_string
	)
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
		tz_name = current_local_iso_numeric_timezone_string

	if dst_currently_in_effect:
		tz = cFixedOffsetTimezone (
			offset = ((time.altzone * -1) / 60),
			name = tz_name
		)
	else:
		tz = cFixedOffsetTimezone (
			offset = ((time.timezone * -1) / 60),
			name = tz_name
		)

	try:
		return pyDT.datetime (
			year = mxDateTime.year,
			month = mxDateTime.month,
			day = mxDateTime.day,
			tzinfo = tz
		)
	except:
		_log.debug (u'error converting mx.DateTime.DateTime to Python: %s-%s-%s %s:%s %s.%s',
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
def format_dob(dob, format='%x', encoding=None, none_string=None):
	if dob is None:
		if none_string is None:
			return _('** DOB unknown **')
		return none_string

	return pydt_strftime(dob, format = format, encoding = encoding, accuracy = acc_days)
#---------------------------------------------------------------------------
def pydt_strftime(dt, format='%c', encoding=None, accuracy=None):

	if encoding is None:
		encoding = gmI18N.get_encoding()

	try:
		return dt.strftime(format).decode(encoding, 'replace')
	except ValueError:
		_log.exception('Python cannot strftime() this <datetime>')

	if accuracy == acc_days:
		return u'%04d-%02d-%02d' % (
			dt.year,
			dt.month,
			dt.day
		)

	if accuracy == acc_minutes:
		return u'%04d-%02d-%02d %02d:%02d' % (
			dt.year,
			dt.month,
			dt.day,
			dt.hour,
			dt.minute
		)

	return u'%04d-%02d-%02d %02d:%02d:%02d' % (
		dt.year,
		dt.month,
		dt.day,
		dt.hour,
		dt.minute,
		dt.second
	)
#---------------------------------------------------------------------------
def pydt_now_here():
	"""Returns NOW @ HERE (IOW, in the local timezone."""
	return pyDT.datetime.now(gmCurrentLocalTimezone)
#---------------------------------------------------------------------------
def pydt_max_here():
	return pyDT.datetime.max.replace(tzinfo = gmCurrentLocalTimezone)
#---------------------------------------------------------------------------
def wx_now_here(wx=None):
	"""Returns NOW @ HERE (IOW, in the local timezone."""
	return py_dt2wxDate(py_dt = pydt_now_here(), wx = wx)
#===========================================================================
# wxPython conversions
#---------------------------------------------------------------------------
def wxDate2py_dt(wxDate=None):
	if not wxDate.IsValid():
		raise ValueError (u'invalid wxDate: %s-%s-%s %s:%s %s.%s',
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
	except:
		_log.debug (u'error converting wxDateTime to Python: %s-%s-%s %s:%s %s.%s',
			wxDate.GetYear(),
			wxDate.GetMonth(),
			wxDate.GetDay(),
			wxDate.GetHour(),
			wxDate.GetMinute(),
			wxDate.GetSecond(),
			wxDate.GetMillisecond()
		)
		raise
#---------------------------------------------------------------------------
def py_dt2wxDate(py_dt=None, wx=None):
	_log.debug(u'setting wx.DateTime from: %s-%s-%s', py_dt.year, py_dt.month, py_dt.day)
	# Robin Dunn says that for SetYear/*Month/*Day the wx.DateTime MUST already
	# be valid (by definition) or, put the other way round, you must Set() day,
	# month, and year at once
	wxdt = wx.DateTimeFromDMY(py_dt.day, py_dt.month-1, py_dt.year)
	return wxdt
#===========================================================================
# interval related
#---------------------------------------------------------------------------
def format_interval(interval=None, accuracy_wanted=None, none_string=None):

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

	tmp = u''

	if years > 0:
		tmp += u'%s%s' % (int(years), _('interval_format_tag::years::y')[-1:])

	if accuracy_wanted < acc_months:
		return tmp.strip()

	if months > 0:
		tmp += u' %s%s' % (int(months), _('interval_format_tag::months::m')[-1:])

	if accuracy_wanted < acc_weeks:
		return tmp.strip()

	if weeks > 0:
		tmp += u' %s%s' % (int(weeks), _('interval_format_tag::weeks::w')[-1:])

	if accuracy_wanted < acc_days:
		return tmp.strip()

	if days > 0:
		tmp += u' %s%s' % (int(days), _('interval_format_tag::days::d')[-1:])

	if accuracy_wanted < acc_hours:
		return tmp.strip()

	if hours > 0:
		tmp += u' %s/24' % int(hours)

	if accuracy_wanted < acc_minutes:
		return tmp.strip()

	if mins > 0:
		tmp += u' %s/60' % int(mins)

	if accuracy_wanted < acc_seconds:
		return tmp.strip()

	if secs > 0:
		tmp += u' %s/60' % int(secs)

	return tmp.strip()
#---------------------------------------------------------------------------
def format_interval_medically(interval=None):
	"""Formats an interval.

	This isn't mathematically correct but close enough for display.
	"""
	# FIXME: i18n for abbrevs

	# more than 1 year ?
	if interval.days > 363:
		years, days = divmod(interval.days, 364)
		leap_days, tmp = divmod(years, 4)
		months, day = divmod((days + leap_days), 30.33)
		if int(months) == 0:
			return "%sy" % int(years)
		return "%sy %sm" % (int(years), int(months))

	# more than 30 days / 1 month ?
	if interval.days > 30:
		months, days = divmod(interval.days, 30.33)
		weeks, days = divmod(days, 7)
		if int(weeks + days) == 0:
			result = '%smo' % int(months)
		else:
			result = '%sm' % int(months)
		if int(weeks) != 0:
			result += ' %sw' % int(weeks)
		if int(days) != 0:
			result += ' %sd' % int(days)
		return result

	# between 7 and 30 days ?
	if interval.days > 7:
		return "%sd" % interval.days

	# between 1 and 7 days ?
	if interval.days > 0:
		hours, seconds = divmod(interval.seconds, 3600)
		if hours == 0:
			return '%sd' % interval.days
		return "%sd (%sh)" % (interval.days, int(hours))

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
def calculate_apparent_age(start=None, end=None):
	"""The result of this is a tuple (years, ..., seconds) as one would
	'expect' a date to look like, that is, simple differences between
	the fields.

	No need for 100/400 years leap days rule	because 2000 WAS a leap year.

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
			return u'%s%s' % (
				years,
				_('y::year_abbreviation').replace('::year_abbreviation', u'')
			)
		return u'%s%s %s%s' % (
			years,
			_('y::year_abbreviation').replace('::year_abbreviation', u''),
			months,
			_('m::month_abbreviation').replace('::month_abbreviation', u'')
		)

	# more than 1 month ?
	if months > 1:
		if days == 0:
			return u'%s%s' % (
				months,
				_('mo::month_only_abbreviation').replace('::month_only_abbreviation', u'')
			)

		result = u'%s%s' % (
			months,
			_('m::month_abbreviation').replace('::month_abbreviation', u'')
		)

		weeks, days = divmod(days, 7)
		if int(weeks) != 0:
			result += u'%s%s' % (
				int(weeks),
				_('w::week_abbreviation').replace('::week_abbreviation', u'')
			)
		if int(days) != 0:
			result += u'%s%s' % (
				int(days),
				_('d::day_abbreviation').replace('::day_abbreviation', u'')
			)

		return result

	# between 7 days and 1 month
	if days > 7:
		return u"%s%s" % (
			days,
			_('d::day_abbreviation').replace('::day_abbreviation', u'')
		)

	# between 1 and 7 days ?
	if days > 0:
		if hours == 0:
			return u'%s%s' % (
				days,
				_('d::day_abbreviation').replace('::day_abbreviation', u'')
			)
		return u'%s%s (%s%s)' % (
			days,
			_('d::day_abbreviation').replace('::day_abbreviation', u''),
			hours,
			_('h::hour_abbreviation').replace('::hour_abbreviation', u'')
		)

	# between 5 hours and 1 day
	if hours > 5:
		return u'%s%s' % (
			hours,
			_('h::hour_abbreviation').replace('::hour_abbreviation', u'')
		)

	# between 1 and 5 hours
	if hours > 1:
		if minutes == 0:
			return u'%s%s' % (
				hours,
				_('h::hour_abbreviation').replace('::hour_abbreviation', u'')
			)
		return u'%s:%02d' % (
			hours,
			minutes
		)

	# between 5 and 60 minutes
	if minutes > 5:
		return u"0:%02d" % minutes

	# less than 5 minutes
	if minutes == 0:
		return u'%s%s' % (
			seconds,
			_('s::second_abbreviation').replace('::second_abbreviation', u'')
		)
	if seconds == 0:
		return u"0:%02d" % minutes
	return "%s.%s%s" % (
		minutes,
		seconds,
		_('s::second_abbreviation').replace('::second_abbreviation', u'')
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
	keys = '|'.join(list(unit_keys['year'].replace('_keys_year', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(%s)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(days = (int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]) * avg_days_per_gregorian_year))

	# "(~)12mM" - at age 12 months
	keys = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		years, months = divmod (
			int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# weeks
	keys = '|'.join(list(unit_keys['week'].replace('_keys_week', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(weeks = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# days
	keys = '|'.join(list(unit_keys['day'].replace('_keys_day', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# hours
	keys = '|'.join(list(unit_keys['hour'].replace('_keys_hour', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*(%s)+$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/12 - months
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*12$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		years, months = divmod (
			int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]),
			12
		)
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# x/52 - weeks
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*52$', str_interval, flags = regex.LOCALE | regex.UNICODE):
#		return pyDT.timedelta(days = (int(regex.findall('\d+', str_interval)[0]) * days_per_week))
		return pyDT.timedelta(weeks = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/7 - days
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*7$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(days = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/24 - hours
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*24$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(hours = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/60 - minutes
	if regex.match(u'^~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*60$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pyDT.timedelta(minutes = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# nYnM - years, months
	keys_year = '|'.join(list(unit_keys['year'].replace('_keys_year', u'')))
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_year, keys_month), str_interval, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pyDT.timedelta(days = ((years * avg_days_per_gregorian_year) + (months * avg_days_per_gregorian_month)))

	# nMnW - months, weeks
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	keys_week = '|'.join(list(unit_keys['week'].replace('_keys_week', u'')))
	if regex.match(u'^~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+$' % (keys_month, keys_week), str_interval, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)
		months, weeks = divmod(int(parts[1]), 4)
		months += int(parts[0])
		return pyDT.timedelta(days = ((months * avg_days_per_gregorian_month) + (weeks * days_per_week)))

	return None
#===========================================================================
# string -> date parser
#---------------------------------------------------------------------------
def __single_char2py_dt(str2parse, trigger_chars=None):
	"""This matches on single characters.

	Spaces and tabs are discarded.

	Default is 'ndmy':
		n - Now
		d - toDay
		m - toMorrow	Someone please suggest a synonym !
		y - Yesterday

	This also defines the significance of the order of the characters.
	"""
	if trigger_chars is None:
		trigger_chars = _('ndmy (single character date triggers)')[:4].lower()

	str2parse = str2parse.strip().lower()

	if len(str2parse) != 1:
		return []

	if str2parse not in trigger_chars:
		return []

	now = mxDT.now()
	enc = gmI18N.get_encoding()

	# FIXME: handle uebermorgen/vorgestern ?

	# right now
	if str2parse == trigger_chars[0]:
		return [{
			'data': mxdt2py_dt(now),
			'label': _('right now (%s, %s)') % (now.strftime('%A').decode(enc), now)
		}]

	# today
	if str2parse == trigger_chars[1]:
		return [{
			'data': mxdt2py_dt(now),
			'label': _('today (%s)') % now.strftime('%A, %Y-%m-%d').decode(enc)
		}]

	# tomorrow
	if str2parse == trigger_chars[2]:
		ts = now + mxDT.RelativeDateTime(days = +1)
		return [{
			'data': mxdt2py_dt(ts),
			'label': _('tomorrow (%s)') % ts.strftime('%A, %Y-%m-%d').decode(enc)
		}]

	# yesterday
	if str2parse == trigger_chars[3]:
		ts = now + mxDT.RelativeDateTime(days = -1)
		return [{
			'data': mxdt2py_dt(ts),
			'label': _('yesterday (%s)') % ts.strftime('%A, %Y-%m-%d').decode(enc)
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
	str2parse = str2parse.strip()

	if not str2parse.endswith(u'.'):
		return []

	str2parse = str2parse[:-1]
	try:
		day_val = int(str2parse)
	except ValueError:
		return []

	if (day_val < -31) or (day_val > 31) or (day_val == 0):
		return []

	now = mxDT.now()
	enc = gmI18N.get_encoding()
	matches = []

	# day X of last month only
	if day_val < 0:
		ts = now + mxDT.RelativeDateTime(day = abs(day_val), months = -1)
		if abs(day_val) <= gregorian_month_length[ts.month]:
			matches.append ({
				'data': mxdt2py_dt(ts),
				'label': _('%s-%s-%s: a %s last month') % (ts.year, ts.month, ts.day, ts.strftime('%A').decode(enc))
			})

	# day X of this month
	if day_val > 0:
		ts = now + mxDT.RelativeDateTime(day = day_val)
		if day_val <= gregorian_month_length[ts.month]:
			matches.append ({
				'data': mxdt2py_dt(ts),
				'label': _('%s-%s-%s: a %s this month') % (ts.year, ts.month, ts.day, ts.strftime('%A').decode(enc))
			})

	# day X of next month
	if day_val > 0:
		ts = now + mxDT.RelativeDateTime(day = day_val, months = +1)
		if day_val <= gregorian_month_length[ts.month]:
			matches.append ({
				'data': mxdt2py_dt(ts),
				'label': _('%s-%s-%s: a %s next month') % (ts.year, ts.month, ts.day, ts.strftime('%A').decode(enc))
			})

	# day X of last month
	if day_val > 0:
		ts = now + mxDT.RelativeDateTime(day = day_val, months = -1)
		if day_val <= gregorian_month_length[ts.month]:
			matches.append ({
				'data': mxdt2py_dt(ts),
				'label': _('%s-%s-%s: a %s last month') % (ts.year, ts.month, ts.day, ts.strftime('%A').decode(enc))
			})

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

	now = mxDT.now()

	# 5/1999
	if regex.match(r"^\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(r'\d+', str2parse, flags = regex.LOCALE | regex.UNICODE)
		ts = now + mxDT.RelativeDateTime(year = int(parts[1]), month = int(parts[0]))
		return [{
			'data': mxdt2py_dt(ts),
			'label': ts.strftime('%Y-%m-%d').decode(enc)
		}]

	matches = []
	# 5/
	if regex.match(r"^\d{1,2}(\s|\t)*/+$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		val = int(str2parse[:-1].strip())

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
			ts = now + mxDT.RelativeDateTime(years = 1)
			matches.append ({
				'data': None,
				'label': '%s-%.2d-' % (ts.year, val)
			})
			# "11/" -> "11/last year"
			ts = now + mxDT.RelativeDateTime(years = -1)
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

	# strftime() returns str but in the localized encoding,
	# so we may need to decode that to unicode
	enc = gmI18N.get_encoding()
	now = mxDT.now()

	matches = []

	# that year
	if (1850 < val) and (val < 2100):
		ts = now + mxDT.RelativeDateTime(year = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': ts.strftime('%Y-%m-%d')
		})

	# day X of this month
	if (val > 0) and (val <= gregorian_month_length[now.month]):
		ts = now + mxDT.RelativeDateTime(day = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%d. of %s (this month): a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		})

	# day X of next month
	if (val > 0) and (val < 32):
		ts = now + mxDT.RelativeDateTime(months = 1, day = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%d. of %s (next month): a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		})

	# day X of last month
	if (val > 0) and (val < 32):
		ts = now + mxDT.RelativeDateTime(months = -1, day = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%d. of %s (last month): a %s') % (val, ts.strftime('%B').decode(enc), ts.strftime('%A').decode(enc))
		})

	# X days from now
	if (val > 0) and (val <= 400):				# more than a year ahead in days ?? nah !
		ts = now + mxDT.RelativeDateTime(days = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('in %d day(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		})
	if (val < 0) and (val >= -400):				# more than a year back in days ?? nah !
		ts = now - mxDT.RelativeDateTime(days = abs(val))
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%d day(s) ago: %s') % (abs(val), ts.strftime('%A, %Y-%m-%d').decode(enc))
		})

	# X weeks from now
	if (val > 0) and (val <= 50):				# pregnancy takes about 40 weeks :-)
		ts = now + mxDT.RelativeDateTime(weeks = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('in %d week(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		})
	if (val < 0) and (val >= -50):				# pregnancy takes about 40 weeks :-)
		ts = now - mxDT.RelativeDateTime(weeks = abs(val))
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%d week(s) ago: %s') % (abs(val), ts.strftime('%A, %Y-%m-%d').decode(enc))
		})

	# month X of ...
	if (val < 13) and (val > 0):
		# ... this year
		ts = now + mxDT.RelativeDateTime(month = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s (%s this year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B').decode(enc))
		})

		# ... next year
		ts = now + mxDT.RelativeDateTime(years = 1, month = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s (%s next year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B').decode(enc))
		})

		# ... last year
		ts = now + mxDT.RelativeDateTime(years = -1, month = val)
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s (%s last year)') % (ts.strftime('%Y-%m-%d'), ts.strftime('%B').decode(enc))
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

	# day X of ...
	if (val < 8) and (val > 0):
		# ... this week
		ts = now + mxDT.RelativeDateTime(weekday = (val-1, 0))
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s this week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		})

		# ... next week
		ts = now + mxDT.RelativeDateTime(weeks = +1, weekday = (val-1, 0))
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s next week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		})

		# ... last week
		ts = now + mxDT.RelativeDateTime(weeks = -1, weekday = (val-1, 0))
		matches.append ({
			'data': mxdt2py_dt(ts),
			'label': _('%s last week (%s of %s)') % (ts.strftime('%A').decode(enc), ts.day, ts.strftime('%B').decode(enc))
		})

	if (val < 100) and (val > 0):
		matches.append ({
			'data': None,
			'label': '%s-' % (1900 + val)
		})

	if val == 201:
		tmp = {
			'data': mxdt2py_dt(now),
			'label': now.strftime('%Y-%m-%d')
		}
		matches.append(tmp)
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
	"""
			Default is 'hdwmy':
			h - hours
			d - days
			w - weeks
			m - months
			y - years

		This also defines the significance of the order of the characters.
	"""
	if offset_chars is None:
		offset_chars = _('hdwmy (single character date offset triggers)')[:5].lower()

	str2parse = str2parse.strip()

	# "+/-XXd/w/m/t"
	if not regex.match(r"^(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[%s]$" % offset_chars, str2parse, flags = regex.LOCALE | regex.UNICODE):
		return []

	# into the past ?
	if str2parse.startswith(u'-'):
		is_future = False
		str2parse = str2parse[1:].strip()
	else:
		is_future = True
		str2parse = str2parse.replace(u'+', u'').strip()

	val = int(regex.findall(u'\d{1,2}', str2parse, flags = regex.LOCALE | regex.UNICODE)[0])
	offset_char = regex.findall(u'[%s]' % offset_chars, str2parse, flags = regex.LOCALE | regex.UNICODE)[0].lower()

	now = mxDT.now()
	enc = gmI18N.get_encoding()

	ts = None
	# hours
	if offset_char == offset_chars[0]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(hours = val)
			label = _('in %d hour(s): %s') % (val, ts.strftime('%H:%M'))
		else:
			ts = now - mxDT.RelativeDateTime(hours = val)
			label = _('%d hour(s) ago: %s') % (val, ts.strftime('%H:%M'))
	# days
	elif offset_char == offset_chars[1]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(days = val)
			label = _('in %d day(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(days = val)
			label = _('%d day(s) ago: %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
	# weeks
	elif offset_char == offset_chars[2]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(weeks = val)
			label = _('in %d week(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(weeks = val)
			label = _('%d week(s) ago: %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
	# months
	elif offset_char == offset_chars[3]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(months = val)
			label = _('in %d month(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(months = val)
			label = _('%d month(s) ago: %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
	# years
	elif offset_char == offset_chars[4]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(years = val)
			label = _('in %d year(s): %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(years = val)
			label = _('%d year(s) ago: %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))

	if ts is None:
		return []

	return [{
		'data': mxdt2py_dt(ts),
		'label': label
	}]
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

	# try mxDT parsers
	try:
		date = mxDT.Parser.DateFromString (
			text = str2parse,
			formats = ('euro', 'iso', 'us', 'altus', 'altiso', 'lit', 'altlit', 'eurlit')
		)
		matches.append ({
			'data': mxdt2py_dt(date),
			'label': date.strftime('%Y-%m-%d')
		})
	except (ValueError, OverflowError, mxDT.RangeError):
		pass

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

	patterns.append('%m-%d-%Y')
	patterns.append('%m-%d-%y')
	patterns.append('%m/%d/%Y')
	patterns.append('%m/%d/%y')

	patterns.append('%Y.%m.%d')
	patterns.append('%y.%m.%d')

	for pattern in patterns:
		try:
			date = pyDT.datetime.strptime(str2parse, pattern).replace (
				hour = 11,
				minute = 11,
				second = 11,
				tzinfo = gmCurrentLocalTimezone
			)
			matches.append ({
				'data': date,
				'label': pydt_strftime(date, format = '%Y-%m-%d', accuracy = acc_days)
			})
		except AttributeError:
			# strptime() only available starting with Python 2.5
			break
		except OverflowError:
			# time.mktime() cannot handle dates older than a platform-dependant limit :-(
			continue
		except ValueError:
			# C-level overflow
			continue

	return matches
#===========================================================================
# string -> fuzzy timestamp parser
#---------------------------------------------------------------------------
def __explicit_offset(str2parse, offset_chars=None):
	"""
			Default is 'hdwm':
			h - hours
			d - days
			w - weeks
			m - months
			y - years

		This also defines the significance of the order of the characters.
	"""
	if offset_chars is None:
		offset_chars = _('hdwmy (single character date offset triggers)')[:5].lower()

	# "+/-XXd/w/m/t"
	if not regex.match(u"^(\s|\t)*(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[%s](\s|\t)*$" % offset_chars, str2parse, flags = regex.LOCALE | regex.UNICODE):
		return []
	val = int(regex.findall(u'\d{1,2}', str2parse, flags = regex.LOCALE | regex.UNICODE)[0])
	offset_char = regex.findall(u'[%s]' % offset_chars, str2parse, flags = regex.LOCALE | regex.UNICODE)[0].lower()

	now = mxDT.now()
	enc = gmI18N.get_encoding()

	# allow past ?
	is_future = True
	if str2parse.find('-') > -1:
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
			label = _('in %d day(s) - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(days = val)
			label = _('%d day(s) ago - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		accuracy = acc_days
	# weeks
	elif offset_char == offset_chars[2]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(weeks = val)
			label = _('in %d week(s) - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(weeks = val)
			label = _('%d week(s) ago - %s)') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		accuracy = acc_days
	# months
	elif offset_char == offset_chars[3]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(months = val)
			label = _('in %d month(s) - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(months = val)
			label = _('%d month(s) ago - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		accuracy = acc_days
	# years
	elif offset_char == offset_chars[4]:
		if is_future:
			ts = now + mxDT.RelativeDateTime(years = val)
			label = _('in %d year(s) - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		else:
			ts = now - mxDT.RelativeDateTime(years = val)
			label = _('%d year(s) ago - %s') % (val, ts.strftime('%A, %Y-%m-%d').decode(enc))
		accuracy = acc_months

	if ts is None:
		return []

	tmp = {
		'data': cFuzzyTimestamp(timestamp = ts, accuracy = accuracy),
		'label': label
	}
	return [tmp]
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
	now = mxDT.now()
	if regex.match(u"^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		val = int(regex.findall(u'\d+', str2parse, flags = regex.LOCALE | regex.UNICODE)[0])

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

	elif regex.match(u"^(\s|\t)*\d{1,2}(\s|\t)*/+(\s|\t)*\d{4}(\s|\t)*$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str2parse, flags = regex.LOCALE | regex.UNICODE)
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
def __numbers_only(str2parse):
	"""This matches on single numbers.

	Spaces or tabs are discarded.
	"""
	if not regex.match(u"^(\s|\t)*\d{1,4}(\s|\t)*$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		return []

	# strftime() returns str but in the localized encoding,
	# so we may need to decode that to unicode
	enc = gmI18N.get_encoding()
	now = mxDT.now()
	val = int(regex.findall(u'\d{1,4}', str2parse, flags = regex.LOCALE | regex.UNICODE)[0])

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
	if val <= gregorian_month_length[now.month]:
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
	if val <= gregorian_month_length[(now + mxDT.RelativeDateTime(months = 1)).month]:
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
	if val <= gregorian_month_length[(now + mxDT.RelativeDateTime(months = -1)).month]:
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
			'label': _('in %d day(s) - %s') % (val, target_date.timestamp.strftime('%A, %Y-%m-%d').decode(enc))
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
			'label': _('in %d week(s) - %s') % (val, target_date.timestamp.strftime('%A, %Y-%m-%d').decode(enc))
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
def __single_dot(str2parse):
	"""Expand fragments containing a single dot.

	Standard colloquial date format in Germany: day.month.year

	"14."
		- 14th current month this year
		- 14th next month this year
	"""
	if not regex.match(u"^(\s|\t)*\d{1,2}\.{1}(\s|\t)*$", str2parse, flags = regex.LOCALE | regex.UNICODE):
		return []

	val = int(regex.findall(u'\d+', str2parse, flags = regex.LOCALE | regex.UNICODE)[0])
	now = mxDT.now()
	enc = gmI18N.get_encoding()

	matches = []

	# day X of this month
	ts = now + mxDT.RelativeDateTime(day = val)
	if val > 0 and val <= gregorian_month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s this month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
		})

	# day X of next month
	ts = now + mxDT.RelativeDateTime(day = val, months = +1)
	if val > 0 and val <= gregorian_month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s next month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
		})

	# day X of last month
	ts = now + mxDT.RelativeDateTime(day = val, months = -1)
	if val > 0 and val <= gregorian_month_length[ts.month]:
		matches.append ({
			'data': cFuzzyTimestamp(timestamp = ts, accuracy = acc_days),
			'label': '%s.%s.%s - a %s last month' % (ts.day, ts.month, ts.year, ts.strftime('%A').decode(enc))
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
	matches = __single_dot(str2parse)
	matches.extend(__numbers_only(str2parse))
	matches.extend(__single_slash(str2parse))
	ms = __single_char2py_dt(str2parse)
	for m in ms:
		matches.append ({
			'data': cFuzzyTimestamp (
				timestamp = m['data'],
				accuracy = acc_days
			),
			'label': m['label']
		})
	matches.extend(__explicit_offset(str2parse))

	# try mxDT parsers
	try:
		# date ?
		date_only = mxDT.Parser.DateFromString (
			text = str2parse,
			formats = ('euro', 'iso', 'us', 'altus', 'altiso', 'lit', 'altlit', 'eurlit')
		)
		# time, too ?
		time_part = mxDT.Parser.TimeFromString(text = str2parse)
		datetime = date_only + time_part
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

	if patterns is None:
		patterns = []

	patterns.append(['%Y-%m-%d', acc_days])
	patterns.append(['%y-%m-%d', acc_days])
	patterns.append(['%Y/%m/%d', acc_days])
	patterns.append(['%y/%m/%d', acc_days])

	patterns.append(['%d-%m-%Y', acc_days])
	patterns.append(['%d-%m-%y', acc_days])
	patterns.append(['%d/%m/%Y', acc_days])
	patterns.append(['%d/%m/%y', acc_days])

	patterns.append(['%m-%d-%Y', acc_days])
	patterns.append(['%m-%d-%y', acc_days])
	patterns.append(['%m/%d/%Y', acc_days])
	patterns.append(['%m/%d/%y', acc_days])

	patterns.append(['%Y.%m.%d', acc_days])
	patterns.append(['%y.%m.%d', acc_days])


	for pattern in patterns:
		try:
			fts = cFuzzyTimestamp (
				timestamp = pyDT.datetime.fromtimestamp(time.mktime(time.strptime(str2parse, pattern[0]))),
				accuracy = pattern[1]
			)
			matches.append ({
				'data': fts,
				'label': fts.format_accurately()
			})
		except AttributeError:
			# strptime() only available starting with Python 2.5
			break
		except OverflowError:
			# time.mktime() cannot handle dates older than a platform-dependant limit :-(
			continue
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

		if (accuracy < 1) or (accuracy > 8):
			raise ValueError('%s.__init__(): <accuracy> must be between 1 and 8' % self.__class__.__name__)

		if isinstance(timestamp, pyDT.datetime):
			timestamp = mxDT.DateTime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)

		if type(timestamp) != mxDT.DateTimeType:
			raise TypeError('%s.__init__(): <timestamp> must be of mx.DateTime.DateTime or datetime.datetime type' % self.__class__.__name__)

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
			return unicode(self.timestamp.year)

		if accuracy == acc_months:
			return unicode(self.timestamp.strftime('%m/%Y'))	# FIXME: use 3-letter month ?

		if accuracy == acc_weeks:
			return unicode(self.timestamp.strftime('%m/%Y'))	# FIXME: use 3-letter month ?

		if accuracy == acc_days:
			return unicode(self.timestamp.strftime('%Y-%m-%d'))

		if accuracy == acc_hours:
			return unicode(self.timestamp.strftime("%Y-%m-%d %I%p"))

		if accuracy == acc_minutes:
			return unicode(self.timestamp.strftime("%Y-%m-%d %H:%M"))

		if accuracy == acc_seconds:
			return unicode(self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

		if accuracy == acc_subseconds:
			return unicode(self.timestamp)

		raise ValueError, '%s.format_accurately(): <accuracy> (%s) must be between 1 and 7' % (
			self.__class__.__name__,
			accuracy
		)
	#-----------------------------------------------------------------------
	def get_mxdt(self):
		return self.timestamp
	#-----------------------------------------------------------------------
	def get_pydt(self):
		try:
			gmtoffset = self.timestamp.gmtoffset()
		except mxDT.Error:
			# Windows cannot deal with dates < 1970, so
			# when that happens switch to now()
			now = mxDT.now()
			gmtoffset = now.gmtoffset()
		tz = cFixedOffsetTimezone(gmtoffset.minutes, self.timestamp.tz)
		secs, msecs = divmod(self.timestamp.second, 1)
		ts = pyDT.datetime (
			year = self.timestamp.year,
			month = self.timestamp.month,
			day = self.timestamp.day,
			hour = self.timestamp.hour,
			minute = self.timestamp.minute,
			second = int(secs),
			microsecond = int(msecs * 1000),
			tzinfo = tz
		)
		return ts
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != "test":
		sys.exit()

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
		for tmp in intervals_as_str:
			intv = str2interval(str_interval = tmp)
			for acc in _accuracy_strings.keys():
				print '[%s]: "%s" -> "%s"' % (acc, tmp, format_interval(intv, acc))
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
			pyDT.timedelta(weeks = 52 * 30),
			pyDT.timedelta(weeks = 52 * 79, days = 33)
		]

		idx = 1
		for intv in intervals:
			print '%s) %s -> %s' % (idx, intv, format_interval_medically(intv))
			idx += 1
	#-----------------------------------------------------------------------
	def test_str2interval():
		print "testing str2interval()"
		print "----------------------"

		for interval_as_str in intervals_as_str:
			print "input: <%s>" % interval_as_str
			print "  ==>", str2interval(str_interval=interval_as_str)

		return True
	#-------------------------------------------------
	def test_date_time():
		print "DST currently in effect:", dst_currently_in_effect
		print "current UTC offset:", current_local_utc_offset_in_seconds, "seconds"
		print "current timezone (interval):", current_local_timezone_interval
		print "current timezone (ISO conformant numeric string):", current_local_iso_numeric_timezone_string
		print "local timezone class:", cLocalTimezone
		print ""
		tz = cLocalTimezone()
		print "local timezone instance:", tz
		print " (total) UTC offset:", tz.utcoffset(pyDT.datetime.now())
		print " DST adjustment:", tz.dst(pyDT.datetime.now())
		print " timezone name:", tz.tzname(pyDT.datetime.now())
		print ""
		print "current local timezone:", gmCurrentLocalTimezone
		print " (total) UTC offset:", gmCurrentLocalTimezone.utcoffset(pyDT.datetime.now())
		print " DST adjustment:", gmCurrentLocalTimezone.dst(pyDT.datetime.now())
		print " timezone name:", gmCurrentLocalTimezone.tzname(pyDT.datetime.now())
		print ""
		print "now here:", pydt_now_here()
		print ""
	#-------------------------------------------------
	def test_str2fuzzy_timestamp_matches():
		print "testing function str2fuzzy_timestamp_matches"
		print "--------------------------------------------"

		val = None
		while val != 'exit':
			val = raw_input('Enter date fragment ("exit" quits): ')
			matches = str2fuzzy_timestamp_matches(str2parse = val)
			for match in matches:
				print 'label shown  :', match['label']
				print 'data attached:', match['data'], match['data'].timestamp
				print ""
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
	def test_get_pydt():
		print "testing platform for handling dates before 1970"
		print "-----------------------------------------------"
		ts = mxDT.DateTime(1935, 4, 2)
		fts = cFuzzyTimestamp(timestamp=ts)
		print "fts           :", fts
		print "fts.get_pydt():", fts.get_pydt()
	#-------------------------------------------------
	def test_calculate_apparent_age():
		start = pydt_now_here().replace(year = 1974).replace(month = 10).replace(day = 23)
		print calculate_apparent_age(start = start)
		print format_apparent_age_medically(calculate_apparent_age(start = start))

		start = pydt_now_here().replace(year = 1979).replace(month = 3).replace(day = 13)
		print calculate_apparent_age(start = start)
		print format_apparent_age_medically(calculate_apparent_age(start = start))

		start = pydt_now_here().replace(year = 1979).replace(month = 2, day = 2)
		end = pydt_now_here().replace(year = 1979).replace(month = 3).replace(day = 31)
		print calculate_apparent_age(start = start, end = end)

		start = pydt_now_here().replace(year = 2009).replace(month = 7, day = 21)
		print format_apparent_age_medically(calculate_apparent_age(start = start))

		print "-------"
		start = pydt_now_here().replace(year = 2011).replace(month = 1).replace(day = 23).replace(hour = 12).replace(minute = 11)
		print calculate_apparent_age(start = start)
		print format_apparent_age_medically(calculate_apparent_age(start = start))
	#-------------------------------------------------
	def test_str2pydt():
		print "testing function str2pydt_matches"
		print "---------------------------------"

		val = None
		while val != 'exit':
			val = raw_input('Enter date fragment ("exit" quits): ')
			matches = str2pydt_matches(str2parse = val)
			for match in matches:
				print 'label shown  :', match['label']
				print 'data attached:', match['data']
				print ""
			print "---------------"
	#-------------------------------------------------
	def test_pydt_strftime():
		dt = pydt_now_here()
		print pydt_strftime(dt)
		print pydt_strftime(dt, accuracy = acc_days)
		print pydt_strftime(dt, accuracy = acc_minutes)
		print pydt_strftime(dt, accuracy = acc_seconds)
		dt = dt.replace(year = 1899)
		print pydt_strftime(dt)
		print pydt_strftime(dt, accuracy = acc_days)
		print pydt_strftime(dt, accuracy = acc_minutes)
		print pydt_strftime(dt, accuracy = acc_seconds)
	#-------------------------------------------------
	# GNUmed libs
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	init()

	#test_date_time()
	#test_str2fuzzy_timestamp_matches()
	#test_cFuzzyTimeStamp()
	#test_get_pydt()
	#test_str2interval()
	#test_format_interval()
	#test_format_interval_medically()
	test_calculate_apparent_age()
	#test_str2pydt()
	#test_pydt_strftime()

#===========================================================================
