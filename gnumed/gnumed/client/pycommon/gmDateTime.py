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
"""
#===========================================================================
# $Id: gmDateTime.py,v 1.34 2009-11-13 21:04:45 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmDateTime.py,v $
__version__ = "$Revision: 1.34 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

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
def pydt_now_here():
	"""Returns NOW @ HERE (IOW, in the local timezone."""
	return pyDT.datetime.now(gmCurrentLocalTimezone)
#---------------------------------------------------------------------------
def wx_now_here(wx=None):
	"""Returns NOW @ HERE (IOW, in the local timezone."""
	return py_dt2wxDate(py_dt = pydt_now_here(), wx = wx)
#===========================================================================
# wxPython conversions
#---------------------------------------------------------------------------
def wxDate2py_dt(wxDate=None):
	if not wxDate.IsValid():
		raise ArgumentError (u'invalid wxDate: %s-%s-%s %s:%s %s.%s',
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
	wxdt = wx.DateTime()
	wxdt.SetYear(py_dt.year)
	wxdt.SetMonth(py_dt.month-1)
	wxdt.SetDay(py_dt.day)
	return wxdt
#===========================================================================
# interval related
#---------------------------------------------------------------------------
def format_interval(interval=None, accuracy_wanted=acc_seconds):

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
	if interval.days > 360:
		years, days = divmod(interval.days, 360)
		months, day = divmod(days, 30)
		if months == 0:
			return "%sy" % int(years)
		return "%sy %sm" % (int(years), int(months))

	# more than 30 days / 1 month ?
	if interval.days > 30:
		months, days = divmod(interval.days, 30)
		weeks, days = divmod(days, 7)
		if (weeks + days) == 0:
			result = '%smo' % int(months)
		else:
			result = '%sm' % int(months)
		if weeks != 0:
			result += ' %sw' % int(weeks)
		if days != 0:
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
		return "%sh %sm" % (int(hours), int(minutes))

	# minutes only
	if interval.seconds > (5*60):
		return "%smi" % (int(interval.seconds // 60))

	# seconds
	minutes, seconds = divmod(interval.seconds, 60)
	if minutes == 0:
		return '%ss' % int(seconds)
	if seconds == 0:
		return '%smi' % int(minutes)
	return "%sm %ss" % (int(minutes), int(seconds))
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
# string -> timestamp parsers
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
def __single_char(str2parse, trigger_chars=None):
	"""This matches on single characters.

	Spaces and tabs are discarded.

	Default is 'ndmy':
		n - now
		d - toDay
		m - toMorrow	Someone please suggest a synonym !
		y - yesterday

	This also defines the significance of the order of the characters.
	"""
	if trigger_chars is None:
		trigger_chars = _('ndmy (single character date triggers)')[:4].lower()

	if not regex.match(u'^(\s|\t)*[%s]{1}(\s|\t)*$' % trigger_chars, str2parse, flags = regex.LOCALE | regex.UNICODE):
		return []
	val = str2parse.strip().lower()

	now = mxDT.now()
	enc = gmI18N.get_encoding()

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
	matches.extend(__single_char(str2parse))
	matches.extend(__explicit_offset(str2parse))

	# try mxDT parsers
	if mxDT is not None:
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

	patterns.append(['%Y.%m.%d', acc_days])
	patterns.append(['%Y/%m/%d', acc_days])

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

		if isinstance(timestamp, pyDT.datetime):
			timestamp = mxDT.DateTime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)

		if type(timestamp) != mxDT.DateTimeType:
			raise TypeError, '%s.__init__(): <timestamp> must be of mx.DateTime.DateTime or datetime.datetime type' % self.__class__.__name__

		self.timestamp = timestamp

		if (accuracy < 1) or (accuracy > 8):
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
			return unicode(self.timestamp.strftime('%m/%Y'))	# FIXME: use 3-letter month ?

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
			second = secs,
			microsecond = msecs,
			tzinfo = tz
		)
		return ts
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

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
			pyDT.timedelta(days = 400)
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
				print 'data attached:', match['data']
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
	if len(sys.argv) > 1 and sys.argv[1] == "test":

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
		test_format_interval_medically()

#===========================================================================
# $Log: gmDateTime.py,v $
# Revision 1.34  2009-11-13 21:04:45  ncq
# - improved medical interval formatting
#
# Revision 1.33  2009/11/08 20:43:04  ncq
# - improved format-interval-medically plus tests
#
# Revision 1.32  2009/11/06 15:07:40  ncq
# - re-formatting for clarity
# - simplify str2interval regexes
#
# Revision 1.31  2009/10/29 17:14:11  ncq
# - improve (simplify) str2interval
#
# Revision 1.30  2009/09/23 14:32:05  ncq
# - pydt-now-here()
#
# Revision 1.29  2009/07/09 16:42:06  ncq
# - ISO date formatting
#
# Revision 1.28  2009/06/04 14:50:06  ncq
# - re-import lost formatters
#
# Revision 1.28  2009/05/28 10:48:29  ncq
# - format_interval(_medically)
#
# Revision 1.27  2009/04/19 22:23:36  ncq
# - move interval parsers here
#
# Revision 1.26  2009/04/03 09:33:22  ncq
# - conversions for wx.DateTime
#
# Revision 1.25  2009/02/05 14:28:30  ncq
# - comment
#
# Revision 1.24  2008/11/17 23:11:38  ncq
# - provide properly utf8iefied py_*_timezone_name
#
# Revision 1.23  2008/11/03 10:28:03  ncq
# - improved wording
#
# Revision 1.22  2008/10/22 12:07:28  ncq
# - log mx.DateTime version
# - use %x in strftime
#
# Revision 1.21  2008/06/18 15:28:32  ncq
# - properly i18n trigger chars in str 2 timestamp conversions
# - document "patterns" arg for str 2 timestamp conversion
#
# Revision 1.20  2008/05/19 15:45:26  ncq
# - re-adjust timezone handling code
# - remember timezone *name* for PG
#
# Revision 1.19  2008/04/12 22:30:46  ncq
# - support more date/time patterns
#
# Revision 1.18  2008/01/13 01:14:26  ncq
# - does need gmI18N
#
# Revision 1.17  2008/01/05 16:37:47  ncq
# - typo fix
#
# Revision 1.16  2007/12/12 16:17:15  ncq
# - better logger names
#
# Revision 1.15  2007/12/11 14:18:20  ncq
# - stdlib logging
#
# Revision 1.14  2007/09/04 23:28:06  ncq
# - document what's happening
#
# Revision 1.13  2007/09/04 21:59:30  ncq
# - try to work around Windows breakage before 1970
#
# Revision 1.12  2007/09/03 12:56:00  ncq
# - test for dates before 1970
#
# Revision 1.11  2007/06/15 08:10:40  ncq
# - improve test suite
#
# Revision 1.10  2007/06/15 08:01:09  ncq
# - better argument naming
# - fix regexen for unicode/locale
#
# Revision 1.9  2007/05/21 17:13:12  ncq
# - import gmI18N
#
# Revision 1.8  2007/04/23 16:56:54  ncq
# - poperly place misplaced "
#
# Revision 1.7  2007/04/02 18:21:27  ncq
# - incorporate all of gmFuzzyTimestamp.py
#
# Revision 1.6  2007/01/16 17:59:55  ncq
# - improved docs and tests
# - normalized UTC offset since time and datetime modules
#   do not agree sign vs direction
#
# Revision 1.5  2007/01/16 13:42:21  ncq
# - add gmCurrentLocalTimezone() as cFixedOffsetTimezone instance
#   with values taken from currently applicable UTC offset
#
# Revision 1.4  2007/01/10 22:31:10  ncq
# - add FixedOffsetTimezone() from psycopg2.tz
#
# Revision 1.3  2006/12/22 16:54:28  ncq
# - add cLocalTimezone from psycopg2 until datetime supports it
# - better logging
# - enhanced test suite
#
# Revision 1.2  2006/12/21 17:44:26  ncq
# - differentiate between timezone as interval and as string
# - if timezone string is to be ISO aware it cannot contain ","
#
# Revision 1.1  2006/12/21 10:50:50  ncq
# - date/time handling
#
#
#===========================================================================
# old Log for gmFuzzyTimestamp.py:
#
# Revision 1.11  2007/04/01 15:27:09  ncq
# - safely get_encoding()
#
# Revision 1.10  2007/03/02 15:30:24  ncq
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
