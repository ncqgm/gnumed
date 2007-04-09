# -*- coding: latin1 -*-
__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmTools.py,v 1.19 2007-04-09 16:30:31 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmTools.py,v $
__version__ = "$Revision: 1.19 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# std libs
import datetime as pydt, re as regex, sys, os


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


ooo_start_cmd = 'oowriter -accept="socket,host=localhost,port=2002;urp;"'

# CAPitalization modes:
(
	CAPS_NONE,					# don't touch it
	CAPS_FIRST,					# CAP first char, leave rest as is
	CAPS_ALLCAPS,				# CAP all chars
	CAPS_WORDS,					# CAP first char of every word
	CAPS_NAMES,					# CAP in a way suitable for names (tries to be smart)
	CAPS_FIRST_ONLY				# CAP first char, lowercase the rest
) = range(6)

default_mail_sender = u'gnumed@gmx.net'
default_mail_receiver = u'gnumed-devel@gnu.org'
default_mail_server = u'mail.gmx.net'

#===========================================================================
def send_mail(sender=None, receiver=None, message=None, server=None, auth=None, debug=False):
	if message is None:
		return False
	message = message.lstrip().lstrip('\r\n').lstrip()

	if sender is None:
		sender = default_mail_sender

	if receiver is None:
		receiver = [default_mail_receiver]

	if server is None:
		server = default_mail_server

	import smtplib
	session = smtplib.SMTP(server)
	session.set_debuglevel(debug)
	if auth is not None:
		session.login(auth['user'], auth['password'])
	refused = session.sendmail(sender, receiver, message)
	session.quit()
	if len(refused) != 0:
		_log.Log(gmLog.lErr, "refused recipients: %s" % refused)
		return False

	return True
#===========================================================================
def mkdir(directory=None):
	try:
		os.makedirs(directory)
	except OSError, e:
		if (e.errno == 17) and not os.path.isdir(directory):
			raise
	return True
#===========================================================================
def import_module_from_directory(module_path=None, module_name=None):
	"""Import a module from any location."""
	if module_path not in sys.path:
		_log.Log(gmLog.lInfo, 'appending to sys.path: [%s]' % module_path)
		sys.path.append(module_path)
		remove_path = True
	else:
		remove_path = False

	if module_name.endswith('.py'):
		module_name = module_name[:-3]

	try:
		module = __import__(module_name)
		_log.Log(gmLog.lInfo, 'imported module [%s] as [%s]' % (module_name, module))
	except StandardError:
		_log.LogException('cannot __import__() module [%s] from [%s]' % (module_name, module_path), exc_info=sys.exc_info(), verbose=0)
		if remove_path:
			sys.path.remove(module_path)
		raise

	if remove_path:
		sys.path.remove(module_path)

	return module
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
		from com.sun.star.connection import NoConnectException as UnoNoConnectException
	except ImportError:
		_log.Log(gmLog.lInfo, 'open_uri_in_ooo(): cannot import UNO, OpenOffice and/or UNO installed ?')
		# fail gracefully if OOo/UNO isn't insalled
		return False

	# failing early is good
	document_uri = uno.systemPathToFileUrl(filename)

	resolver_uri = "com.sun.star.bridge.UnoUrlResolver"
	remote_context_uri = "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"
	ooo_desktop_uri = "com.sun.star.frame.Desktop"

	local_context = uno.getComponentContext()
	uri_resolver = local_context.ServiceManager.createInstanceWithContext(resolver_uri, local_context)

	try:
		remote_context = uri_resolver.resolve(remote_context_uri)
	except UnoNoConnectException:
		_log.Log(gmLog.lInfo, 'Cannot connect to OOo server. Trying to start one with: [%s]' % ooo_start_cmd)
		os.system(ooo_start_cmd)
		remote_context	= uri_resolver.resolve(remote_context_uri)

	ooo_desktop	= remote_context.ServiceManager.createInstanceWithContext(ooo_desktop_uri, remote_context)
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
# text related tools
#---------------------------------------------------------------------------
def coalesce(initial=None, instead=None, template_initial=None, template_instead=None):
	"""Modelled after the SQL coalesce function.

	To be used to simplify constructs like:

		if value is None:
			real_value = some_other_value
		else:
			real_value = some_template_with_%s_formatter % value
		print real_value

	@param initial: the value to be tested for <None>
	@type initial: any Python type, must have a __str__ method if template_initial is not None
	@param instead: the value to be returned if <initial> is None
	@type instead: any Python type, must have a __str__ method if template_instead is not None
	@param template_initial: if <initial> is returned replace the value into this template, must contain one <%s> 
	@type template_initial: string or None
	@param template_instead: if <instead> is returned replace the value into this template, must contain one <%s> 
	@type template_instead: string or None
	"""
	if initial is None:
		if template_instead is None:
			return instead
		return template_instead % instead
	if template_initial is None:
		return initial
	return template_initial % initial
#---------------------------------------------------------------------------
def __cap_name(match_obj=None):
	val = match_obj.group(0).lower()
	if val in ['von', 'van', 'de', 'la', 'l', 'der', 'den']:			# FIXME: this needs to expand, configurable ?
		return val
	buf = list(val)
	buf[0] = buf[0].upper()
	for part in ['mac', 'mc', 'de', 'la']:
		if len(val) > len(part) and val[:len(part)] == part:
			buf[len(part)] = buf[len(part)].upper()
	return ''.join(buf)
#---------------------------------------------------------------------------
def capitalize(text=None, mode=CAPS_NAMES):
	"""Capitalize the first character but leave the rest alone.

	Note that we must be careful about the locale, this may
	have issues ! However, for UTF strings it should just work.
	"""
	if (mode is None) or (mode == CAPS_NONE):
		return text

	if mode == CAPS_FIRST:
		return text[0].upper() + text[1:]

	if mode == CAPS_ALLCAPS:
		return text.upper()

	if mode == CAPS_FIRST_ONLY:
		return text[0].upper() + text[1:].lower()

	if mode == CAPS_WORDS:
		return regex.sub(r'(\w)(\w+)', lambda x: x.group(1).upper() + x.group(2).lower(), text)

	if mode == CAPS_NAMES:
		#return regex.sub(r'\w+', __cap_name, text)
		return capitalize(text=text, mode=CAPS_FIRST)		# until fixed

	print "ERROR: invalid capitalize() mode: [%s], leaving input as is", mode
	return text
#---------------------------------------------------------------------------
def wrap(text, width):
	"""
	A word-wrap function that preserves existing line breaks
	and most spaces in the text. Expects that existing line
	breaks are posix newlines (\n).

	FIXME: add initial/subsequent indent etc
	"""
	return reduce (
		lambda line, word, width=width: '%s%s%s' % (
			line,
			' \n'[(
				len(line)
				- line.rfind('\n')
				- 1
				+ len(word.split('\n',1)[0])
				>= width
			)],
			word),
		text.split(' ')
	)
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)

	#-----------------------------------------------------------------------
	def test_open_uri_in_ooo():
		try:
			open_uri_in_ooo(filename=sys.argv[1])
		except:
			_log.LogException('cannot open [%s] in OOo' % sys.argv[1])
			raise
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
		tests = [
			[None, 'something other than <None>', None, None, 'something other than <None>']
		]
		passed = True
		for test in tests:
			result = coalesce (
				initial = test[0],
				instead = test[1],
				template_initial = test[2],
				template_instead = test[3]
			)
			if result != test[4]:
				print "ERROR"
				print "coalesce: (%s, %s, %s, %s)" % (test[0], test[1], test[2], test[3])
				print "expected:", test[4]
				print "received:", result
				passed = False

		if passed:
			print "passed"
		else:
			print "failed"
		return passed
	#-----------------------------------------------------------------------
	def test_capitalize():
		print 'testing capitalize()'
		print '--------------------'
		pairs = [
			[u'Boot', u'Boot', CAPS_FIRST_ONLY],
			[u'boot', u'Boot', CAPS_FIRST_ONLY],
			[u'booT', u'Boot', CAPS_FIRST_ONLY],
			[u'BoOt', u'Boot', CAPS_FIRST_ONLY],
			[u'boots-Schau', u'Boots-Schau', CAPS_WORDS],
			[u'boots-sChau', u'Boots-Schau', CAPS_WORDS],
			[u'boot camp', u'Boot Camp', CAPS_WORDS],
			[u'fahrner-Kampe', u'Fahrner-Kampe', CAPS_NAMES],
			[u'häkkönen', u'Häkkönen', CAPS_NAMES]
		]
		for pair in pairs:
			result = capitalize(pair[0], pair[2])
			if result != pair[1]:
				print 'ERROR (caps mode %s): "%s" -> "%s", expected "%s"' % (pair[2], pair[0], result, pair[1])

		return True
	#-----------------------------------------------------------------------
	def test_import_module():
		print "testing import_module_from_directory()"
		path = sys.argv[1]
		name = sys.argv[2]
		try:
			mod = import_module_from_directory(module_path = path, module_name = name)
		except:
			print "module import failed, see log"
			return False

		print "module import succeeded", mod
		print dir(mod)
		return True
	#-----------------------------------------------------------------------
	def test_mkdir():
		print "testing mkdir()"
		mkdir(sys.argv[1])
	#-----------------------------------------------------------------------
	def test_send_mail():
		msg = u"""
To: %s
From: %s
Subject: gmTools test suite mail

This is a test mail from the gmTools.py module.
""" % (default_mail_receiver, default_mail_sender)
		print "mail sending succeeded:", send_mail (
			receiver = [default_mail_receiver, u'karsten.hilbert@gmx.net'],
			message = msg,
			auth = {'user': default_mail_sender, 'password': u'gm/bugs/gmx'},
			debug = True
		)
	#-----------------------------------------------------------------------
	print __doc__

	#test_str2interval()
	test_coalesce()
	#test_capitalize()
	#test_open_uri_in_ooo()
	#test_import_module()
	#test_mkdir()
	#test_send_mail()

#===========================================================================
# $Log: gmTools.py,v $
# Revision 1.19  2007-04-09 16:30:31  ncq
# - add send_mail()
#
# Revision 1.18  2007/03/08 16:19:30  ncq
# - typo and cleanup
#
# Revision 1.17  2007/02/17 13:58:11  ncq
# - improved coalesce()
#
# Revision 1.16  2007/02/04 16:43:01  ncq
# - improve capitalize() test suite
# - set coding
#
# Revision 1.15  2007/02/04 16:29:51  ncq
# - make umlauts u''
#
# Revision 1.14  2007/02/04 15:33:28  ncq
# - enhance capitalize() and add mode CONSTS for it
#   - however, CAPS_NAMES for now maps to CAPS_FIRST until fixed for Heller-Brunner
# - slightly improved test suite for it
#
# Revision 1.13  2007/01/30 17:38:28  ncq
# - add mkdir() and a test for it
#
# Revision 1.12  2007/01/20 22:04:01  ncq
# - strip ".py" from script name if it is there
#
# Revision 1.11  2007/01/18 12:46:30  ncq
# - add reasonably safe import_module_from_directory() and test
#
# Revision 1.10  2007/01/15 20:20:39  ncq
# - add wrap()
#
# Revision 1.9  2007/01/06 17:05:57  ncq
# - start OOo server if cannot connect to one
# - test suite
#
# Revision 1.8  2006/12/21 10:53:53  ncq
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