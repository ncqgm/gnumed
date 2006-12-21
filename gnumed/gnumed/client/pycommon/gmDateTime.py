#===========================================================================
__doc__ = (
"""GNUmed date time handling.

This modules provides access to date/time handling.

It utilitzes

	- Python time
	- Python datetime
	- mxDateTime

Note that if you want locale-aware formatting you need to call

	locale.setlocale(locale.LC_ALL, '')

somehwere before importing this script.
""")
#===========================================================================
# $Id: gmDateTime.py,v 1.1 2006-12-21 10:50:50 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmDateTime.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# stdlib
import sys, datetime as pyDT, time, os

# 3rd party
import mx.DateTime as mxDT

# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

dst_currently_in_effect = None
current_utc_offset = None
current_iso_timezone = None

#===========================================================================
def init():

	_log.Log(gmLog.lData, 'mx.DateTime.now(): [%s]' % mxDT.now())
	_log.Log(gmLog.lData, 'datetime.now()   : [%s]' % pyDT.datetime.now())
	_log.Log(gmLog.lData, 'time.localtime() : [%s]' % str(time.localtime()))
	_log.Log(gmLog.lData, 'time.gmtime()    : [%s]' % str(time.gmtime()))

	try:
		_log.Log(gmLog.lData, '$TZ: [%s]' % os.environ['TZ'])
	except KeyError:
		_log.Log(gmLog.lData, '$TZ not defined')

	_log.Log(gmLog.lData, 'time.daylight                : [%s]' % time.daylight)
	_log.Log(gmLog.lData, 'time.timezone                : [%s] seconds' % time.timezone)
	_log.Log(gmLog.lData, 'time.altzone                 : [%s] seconds' % time.altzone)
	_log.Log(gmLog.lData, 'time.tzname                  : [%s / %s] (non-DST / DST)' % time.tzname)
	_log.Log(gmLog.lData, 'mx.DateTime.now().gmtoffset(): [%s]' % mxDT.now().gmtoffset())

	global dst_currently_in_effect
	dst_currently_in_effect = bool(time.localtime()[8])
	_log.Log(gmLog.lData, 'DST currently in effect: [%s]' % dst_currently_in_effect)

	global current_utc_offset
	msg = 'DST currently%sin effect, using UTC offset of [%s] seconds instead of [%s] seconds'
	if dst_currently_in_effect:
		current_utc_offset = time.altzone
		_log.Log(gmLog.lData, msg % (' ', time.altzone, time.timezone))
	else:
		current_utc_offset = time.timezone
		_log.Log(gmLog.lData, msg % (' not ', time.timezone, time.altzone))

	if current_utc_offset < 0:
		_log.Log(gmLog.lData, 'UTC offset is negative, assuming EAST of Greenwich')
	elif current_utc_offset > 0:
		_log.Log(gmLog.lData, 'UTC offset is positive, assuming WEST of Greenwich')
	else:
		_log.Log(gmLog.lData, 'UTC offset is ZERO, assuming Greenwich')

	global current_iso_timezone
	current_iso_timezone = mxDT.now().gmtoffset()
	_log.Log(gmLog.lData, 'ISO timezone: [%s] (taken from mx.DateTime.now().gmtoffset())' % current_iso_timezone)

	# do some magic to convert Python's timezone to a valid ISO timezone
	# is this safe or will it return things like 13.5 hours ?
	#_default_client_timezone = "%+.1f" % (-tz / 3600.0)
	#_log.Log(gmLog.lInfo, 'assuming default client time zone of [%s]' % _default_client_timezone)

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	init()

#===========================================================================
# $Log: gmDateTime.py,v $
# Revision 1.1  2006-12-21 10:50:50  ncq
# - date/time handling
#
#
