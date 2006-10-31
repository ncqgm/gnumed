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
# $Id: gmFuzzyTimestamp.py,v 1.4 2006-10-31 17:18:55 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmFuzzyTimestamp.py,v $
__version__ = "$Revision: 1.4 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import datetime as pyDT

import mx.DateTime as mxDT

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
		if self.accuracy == 1:
			return str(self.timestamp.year)

		if self.accuracy == 2:
			return self.timestamp.strftime('%m/%Y')

		if self.accuracy == 3:
			return self.timestamp.strftime('%Y-%m-%d')

		if self.accuracy == 4:
			return self.timestamp.strftime("%Y-%m-%d %I%p")

		if self.accuracy == 5:
			return self.timestamp.strftime("%Y-%m-%d %H:%M")

		if self.accuracy == 6:
			return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

		if self.accuracy == 7:
			return str(self.timestamp)

		raise ValueError, '%s.format_accurately(): <accuracy> (%s) must be between 1 and 7' % (
			self.__class__.__name__,
			self.accuracy
		)

#===========================================================================
if __name__ == '__main__':

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

#===========================================================================
# $Log: gmFuzzyTimestamp.py,v $
# Revision 1.4  2006-10-31 17:18:55  ncq
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
