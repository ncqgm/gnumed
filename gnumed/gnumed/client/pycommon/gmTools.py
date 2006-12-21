__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmTools.py,v 1.8 2006-12-21 10:53:53 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmTools.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import datetime as pydt, re as regex

#===========================================================================
def open_uri_in_ooo(filename=None):
	"""Connect to OOo and open document.

	<filename> must be absolute

	Actually, this whole thing is redundant. We should just
	use call_editor_on_mimetype(filename). The advantage of
	this is that we can connect to a single OOo *server*.

	You will need to start an OOo server before using this:

		oowriter -accept="socket,host=localhost,port=2002;urp;"
	"""
	try:
		import uno
	except ImportError:
		_log.Log(gmLog.lInfo, 'open_uri_in_ooo(): cannot import UNO, OpenOffice and/or UNO installed ?')
		# fail gracefully if OOo/UNO isn't insalled
		return False

	# failing early is good
	document_uri = uno.systemPathToFileUrl(filename)

	resolver_uri		= "com.sun.star.bridge.UnoUrlResolver"
	remote_context_uri	= "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
	ooo_desktop_uri		= "com.sun.star.frame.Desktop"

	local_context	= uno.getComponentContext()
	uri_resolver	= local_context.ServiceManager.createInstanceWithContext(resolver_uri, local_context)
	# FIXME: this can fail with a connect exception, catch it and start OOo like above
	remote_context	= uri_resolver.resolve(remote_context_uri)
	ooo_desktop		= remote_context.ServiceManager.createInstanceWithContext(ooo_desktop_uri, remote_context)

	document = ooo_desktop.loadComponentFromURL(document_uri, "_blank", 0, ())

	return True
#===========================================================================
# FIXME: should this not be in gmTime or some such?
# close enough on average
days_per_year = 365
days_per_month = 30
days_per_week = 7
#---------------------------------------------------------------------------
def str2interval(str_interval=None):

	# "(~)35(yYjJaA)"	- at age 35 years
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(y|Y|j|J|a|A|\s|\t)*$', str_interval):
		return pydt.timedelta(days = (int(regex.findall('\d+', str_interval)[0]) * days_per_year))

	# "(~)12mM" - at age 12 months
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(m|M)+(\s|\t)*$', str_interval):
		years, months = divmod(int(regex.findall('\d+', str_interval)[0]), 12)
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# weeks
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(w|W)+(\s|\t)*$', str_interval):
		return pydt.timedelta(weeks = int(regex.findall('\d+', str_interval)[0]))

	# days
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(d|D|t|T)+(\s|\t)*$', str_interval):
		return pydt.timedelta(days = int(regex.findall('\d+', str_interval)[0]))

	# hours
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(h|H)+(\s|\t)*$', str_interval):
		return pydt.timedelta(hours = int(regex.findall('\d+', str_interval)[0]))

	# x/12 - months
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*12(\s|\t)*$', str_interval):
		years, months = divmod(int(regex.findall('\d+', str_interval)[0]), 12)
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# x/52 - weeks
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*52(\s|\t)*$', str_interval):
#		return pydt.timedelta(days = (int(regex.findall('\d+', str_interval)[0]) * days_per_week))
		return pydt.timedelta(weeks = int(regex.findall('\d+', str_interval)[0]))

	# x/7 - days
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*7(\s|\t)*$', str_interval):
		return pydt.timedelta(days = int(regex.findall('\d+', str_interval)[0]))

	# x/24 - hours
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*24(\s|\t)*$', str_interval):
		return pydt.timedelta(hours = int(regex.findall('\d+', str_interval)[0]))

	# x/60 - minutes
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*60(\s|\t)*$', str_interval):
		return pydt.timedelta(minutes = int(regex.findall('\d+', str_interval)[0]))

	# nYnM - years, months
	if regex.match('^(\s|\t)*~*(\s|\t)*\d+(y|Y|j|J|a|A|\s|\t)+\d+(\s|\t)*(m|M)+(\s|\t)*$', str_interval):
		parts = regex.findall('\d+', str_interval)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	return None
#===========================================================================
def coalesce(initial=None, instead=None, template=None):
	"""Modelled after the SQL coalesce function.

	To be used to simplify constructs like:

		if value is None:
			real_value = some_other_value
		else:
			real_value = some_template_with_%s_formatter % value
		print real_value

	<initial>: the string to be tested for None
	<instead>: the string to be returned if <initial> is None
	<template>: the template into which to insert <initial> if <initial> is NOT None, must contain one %s or similar
	"""
	if initial is None:
		return instead
	if template is None:
		return initial
	return template % initial
#---------------------------------------------------------------------------
def capitalize(text=None):
	"""Capitalize the first character but leave the rest alone."""
	return text[0].capitalize() + text[1:]
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	#-----------------------------------------------------------------------
	def test_str2interval():
		print "testing str2interval()"
		print "----------------------"

		str_intervals = [
			'7', '12', ' 12', '12 ', ' 12 ', '	12	', '0', '~12', '~ 12', ' ~ 12', '	~	12 ',
			'12a', '12 a', '12	a', '12j', '12J', '12y', '12Y', '	~ 	12	a	 ', '~0a',
			'12m', '17 m', '12	m', '17M', '	~ 	17	m	 ', ' ~ 3	/ 12	', '7/12', '0/12',
			'12w', '17 w', '12	w', '17W', '	~ 	17	w	 ', ' ~ 15	/ 52', '2/52', '0/52',
			'12d', '17 d', '12	t', '17D', '	~ 	17	T	 ', ' ~ 12	/ 7', '3/7', '0/7',
			'12h', '17 h', '12	H', '17H', '	~ 	17	h	 ', ' ~ 36	/ 24', '7/24', '0/24',
			' ~ 36	/ 60', '7/60', '190/60', '0/60',
			'12a1m', '12 a 1  M', '12	a17m', '12j		12m', '12J7m', '12y7m', '12Y7M', '	~ 	12	a	 37 m	', '~0a0m',
			'invalid interval input'
		]

		for str_interval in str_intervals:
			print "interval:", str2interval(str_interval=str_interval), "; original: <%s>" % str_interval

		return True
	#-----------------------------------------------------------------------
	def test_coalesce():
		print 'testing coalesce()'
		print "------------------"
		val = None
		print 'value          : %s (%s)' % (val, type(val))
		print 'coalesce(value): %s (%s)' % (coalesce(val, 'something other than <None>'), type(coalesce(val, 'something other than <None>')))
		return True
	#-----------------------------------------------------------------------
	def test_capitalize():
		print 'testing capitalize()'
		for word in ['Boot', 'boot', 'booT', 'boots-Schau', 'boot camp']:
			print word, capitalize(word)
		return True
	#-----------------------------------------------------------------------
	print __doc__

	test_str2interval()
	#test_coalesce()
	#test_capitalize()

#===========================================================================
# $Log: gmTools.py,v $
# Revision 1.8  2006-12-21 10:53:53  ncq
# - document coalesce() better
#
# Revision 1.7  2006/12/18 15:51:12  ncq
# - comment how to start server OOo writer
#
# Revision 1.6  2006/12/17 20:47:16  ncq
# - add open_uri_in_ooo()
#
# Revision 1.5  2006/11/27 23:02:08  ncq
# - add comment
#
# Revision 1.4  2006/11/24 09:52:09  ncq
# - add str2interval() - this will need to end up in an interval input phrasewheel !
# - improve test suite
#
# Revision 1.3  2006/11/20 15:58:10  ncq
# - template handling in coalesce()
#
# Revision 1.2  2006/10/31 16:03:06  ncq
# - add capitalize() and test
#
# Revision 1.1  2006/09/03 08:53:19  ncq
# - first version
#
#