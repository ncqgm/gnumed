# I posted this to the pyPgSQL mailing list but
# no one seemed to care.

# if your pyPgSQL sometimes returns 0:00:00 instead
# of an interval then use this patch on it

def interval2DateTimeDelta(self, s):
	"""Parses PostgreSQL INTERVALs.
	The expected format is [[[-]YY years] [-]DD days] [-]HH:MM:SS.ss"""
	parser = DateTime.Parser.DateTimeDeltaFromString

	ydh = s.split()
	ago = 1

	result = DateTimeDelta(0) 

	# Convert any years using 365.2425 days per year, which is PostgreSQL's
	# assumption about the number of days in a year.
	if len(ydh) > 1:
		if ydh[1].lower().startswith('year'):
			result += parser('%s days' % ((int(ydh[0]) * 365.2425),))
			ydh = ydh[2:]

	# Convert any months using 30 days per month, which is PostgreSQL's
	# assumption about the number of days in a months IF it doesn't
	# know the end or start date of the interval. If PG DOES know either
	# date it will use the correct length of the month, eg 28-31 days.
	# However, at this stage we have no way of telling which one it
	# was. If you want to work with accurate intervals (eg. post-processing
	# them) you need to use date1-date2 syntax rather than age(date1, date2)
	# in your queries.
	#
	# This is per discussion on pgsql-general:
	#  http://www.spinics.net/lists/pgsql/msg09668.html
	# Google for: >>>"interval output format" available that removes ambiguity<<<
	#
	# Note: Should a notice be provided to the user that post-processing
	#       year/month intervals is unsafe practice ?
	if len(ydh) > 1:
		if ydh[1].lower().startswith('mon'):
			result += parser('%s days' % ((int(ydh[0]) * 30),))
			ydh = ydh[2:]

	# Converts any days and adds it to the years (as an interval)
	if len(ydh) > 1:
		if ydh[1].lower().startswith('day'):
			result += parser('%s days' % (ydh[0],))
			ydh = ydh[2:]

	# Adds in the hours, minutes, seconds (as an interval)
	if len(ydh) > 0:
		result += parser(ydh[0])

	return result
