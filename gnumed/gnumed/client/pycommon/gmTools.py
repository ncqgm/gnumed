# -*- coding: utf8 -*-
__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmTools.py,v 1.40 2007-10-09 10:29:02 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmTools.py,v $
__version__ = "$Revision: 1.40 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# std libs
import datetime as pydt, re as regex, sys, os, os.path, csv, tempfile


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmBorg


_ = lambda x:x

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

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
def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
	# csv.py doesn't do Unicode; encode temporarily as UTF-8:
	csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), dialect=dialect, **kwargs)

	for row in csv_reader:
		# decode UTF-8 back to Unicode, cell by cell:
		yield [unicode(cell, 'utf-8') for cell in row]
#===========================================================================
def handle_uncaught_exception(t, v, tb):

	print ",========================================================"
	print "| Unhandled exception caught !"
	print "| Type :", t
	print "| Value:", v
	print "`========================================================"
	_log.LogException('unhandled exception caught', (t,v,tb), verbose=True)
	# FIXME: allow user to mail report to developers from here
	sys.__excepthook__(t,v,tb)

#===========================================================================
class gmPaths(gmBorg.cBorg):

	def __init__(self, app_name=None, wx=None):
		gmBorg.cBorg.__init__(self)

		try:
			self.already_inited
			return
		except AttributeError:
			pass

		self.init_paths(app_name=app_name, wx=wx)
		self.already_inited = True
	#--------------------------------------
	# public API
	#--------------------------------------
	def init_paths(self, app_name=None, wx=None):

		if app_name is None:
			app_name, ext = os.path.splitext(os.path.basename(sys.argv[0]))

		self.local_base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
		self.working_dir = os.path.abspath(os.curdir)

		try:
			self.user_config_dir = os.path.expanduser(os.path.join('~', '.%s' % app_name))
		except ValueError:
			mkdir(os.path.expanduser(os.path.join('~', '.%s' % app_name)))
			self.user_config_dir = os.path.expanduser(os.path.join('~', '.%s' % app_name))

		try:
			self.system_config_dir = os.path.join('/etc', app_name)
		except ValueError:
			self.system_config_dir = self.local_base_dir
		try:
			self.system_app_data_dir = os.path.join(sys.prefix, 'share', app_name)
		except ValueError:
			self.system_app_data_dir = self.local_base_dir

		if wx is None:
			_log.Log(gmLog.lData, 'wxPython not available')
			self.__log_paths()
			return True

		#--------------------
		# retry with wxPython
		std_paths = wx.StandardPaths.Get()

		try:
			self.user_config_dir = os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name)
		except ValueError:
			mkdir(os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name))
			self.user_config_dir = os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name)

		try:
			#self.system_config_dir = os.path.join(std_paths.GetConfigDir(), app_name)
			self.system_config_dir = std_paths.GetConfigDir()
		except ValueError:
			pass

		try:
			# Robin attests that the following doesn't give
			# sane values on Windows, so IFDEF it
			if 'wxMSW' in wx.PlatformInfo:
				_log.Log(gmLog.lWarn, 'this platform returns a broken value for the system-wide application data dir')
				self.system_app_data_dir = self.local_base_dir
			else:
				self.system_app_data_dir = std_paths.GetDataDir()
		except ValueError:
			pass

		self.__log_paths()
		return True
	#--------------------------------------
	def __log_paths(self):
		_log.Log(gmLog.lData, 'local application base dir: %s' % self.local_base_dir)
		_log.Log(gmLog.lData, 'current working dir: %s' % self.working_dir)
		_log.Log(gmLog.lData, 'user home dir: %s' % os.path.expanduser('~'))
		_log.Log(gmLog.lData, 'user-specific config dir: %s' % self.user_config_dir)
		_log.Log(gmLog.lData, 'system-wide config dir: %s' % self.system_config_dir)
		_log.Log(gmLog.lData, 'system-wide application data dir: %s' % self.system_app_data_dir)
	#--------------------------------------
	# properties
	#--------------------------------------
	def _set_user_config_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:user_config_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.Log(gmLog.lErr, msg)
			raise ValueError(msg)
		self.__user_config_dir = path

	def _get_user_config_dir(self):
		return self.__user_config_dir

	user_config_dir = property(_get_user_config_dir, _set_user_config_dir)
	#--------------------------------------
	def _set_system_config_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:system_config_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.Log(gmLog.lErr, msg)
			raise ValueError(msg)
		self.__system_config_dir = path

	def _get_system_config_dir(self):
		return self.__system_config_dir

	system_config_dir = property(_get_system_config_dir, _set_system_config_dir)
	#--------------------------------------
	def _set_system_app_data_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:system_app_data_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.Log(gmLog.lErr, msg)
			raise ValueError(msg)
		self.__system_app_data_dir = path

	def _get_system_app_data_dir(self):
		return self.__system_app_data_dir

	system_app_data_dir = property(_get_system_app_data_dir, _set_system_app_data_dir)
#===========================================================================
def send_mail(sender=None, receiver=None, message=None, server=None, auth=None, debug=False):
	"""Send an E-Mail.

	<debug>: see smtplib.set_debuglevel()
	<auth>: {'user': ..., 'password': ...}
	<receiver>: a list of email addresses
	"""
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
#---------------------------------------------------------------------------
def get_unique_filename(prefix=None, suffix=None, dir=None):
	"""This introduces a race condition between the file.close() and
	actually using the filename.

	The file will not exist after calling this function.
	"""
	kwargs = {'dir': dir}

	if prefix is None:
		kwargs['prefix'] = 'gnumed-'
	else:
		kwargs['prefix'] = prefix

	if suffix is None:
		kwargs['suffix'] = '.tmp'
	else:
		if not suffix.startswith('.'):
			suffix = '.' + suffix
		kwargs['suffix'] = suffix

	f = tempfile.NamedTemporaryFile(**kwargs)
	filename = f.name
	f.close()

	return filename
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
		_log.LogException('cannot __import__() module [%s] from [%s]' % (module_name, module_path), verbose=0)
		if remove_path:
			sys.path.remove(module_path)
		raise

	if remove_path:
		sys.path.remove(module_path)

	return module
#===========================================================================
# FIXME: should this not be in gmTime or some such?
# close enough on average
days_per_year = 365
days_per_month = 30
days_per_week = 7
#---------------------------------------------------------------------------
def str2interval(str_interval=None):

	# "(~)35(yYjJaA)"	- at age 35 years
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(y|Y|j|J|a|A|\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(days = (int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]) * days_per_year))

	# "(~)12mM" - at age 12 months
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(m|M)+(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		years, months = divmod (
			int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]),
			12
		)
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# weeks
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(w|W)+(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(weeks = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# days
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(d|D|t|T)+(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(days = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# hours
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(h|H)+(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(hours = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/12 - months
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*12(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		years, months = divmod (
			int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]),
			12
		)
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# x/52 - weeks
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*52(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
#		return pydt.timedelta(days = (int(regex.findall('\d+', str_interval)[0]) * days_per_week))
		return pydt.timedelta(weeks = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/7 - days
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*7(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(days = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/24 - hours
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*24(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(hours = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# x/60 - minutes
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*/(\s|\t)*60(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(minutes = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# nYnM - years, months
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(y|Y|j|J|a|A|\s|\t)+\d+(\s|\t)*(m|M)+(\s|\t)*$', str_interval, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	return None
#===========================================================================
# text related tools
#---------------------------------------------------------------------------
_kB = 1024
_MB = 1024 * _kB
_GB = 1024 * _MB
_TB = 1024 * _GB
_PB = 1024 * _TB
#---------------------------------------------------------------------------
def size2str(size=0, template='%s'):
	if size == 1:
		return template % _('1 Byte')
	if size < 10 * _kB:
		return template % _('%s Bytes') % size
	if size < _MB:
		return template % u'%.1f kB' % (float(size) / _kB)
	if size < _GB:
		return template % u'%.1f MB' % (float(size) / _MB)
	if size < _TB:
		return template % u'%.1f GB' % (float(size) / _GB)
	if size < _PB:
		return template % u'%.1f TB' % (float(size) / _TB)
	return template % u'%.1f PB' % (float(size) / _PB)
#---------------------------------------------------------------------------
def bool2str(bool=None, true_str='True', false_str='False'):
	if bool is True:
		return true_str
	return false_str
#---------------------------------------------------------------------------
def none_if(value=None, none_equivalent=None):
	"""Modelled after the SQL NULLIF function."""
	if value == none_equivalent:
		return None
	return value
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

	Ideas:
		- list of None-equivalents
		- list of insteads: initial, [instead, template], [instead, template], [instead, template], template_initial, ...
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
		return regex.sub(ur'(\w)(\w+)', lambda x: x.group(1).upper() + x.group(2).lower(), text)

	if mode == CAPS_NAMES:
		#return regex.sub(r'\w+', __cap_name, text)
		return capitalize(text=text, mode=CAPS_FIRST)		# until fixed

	print "ERROR: invalid capitalization mode: [%s], leaving input as is" % mode
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
		print 'testing capitalize() ...'
		success = True
		pairs = [
			# [original, expected result, CAPS mode]
			[u'Boot', u'Boot', CAPS_FIRST_ONLY],
			[u'boot', u'Boot', CAPS_FIRST_ONLY],
			[u'booT', u'Boot', CAPS_FIRST_ONLY],
			[u'BoOt', u'Boot', CAPS_FIRST_ONLY],
			[u'boots-Schau', u'Boots-Schau', CAPS_WORDS],
			[u'boots-sChau', u'Boots-Schau', CAPS_WORDS],
			[u'boot camp', u'Boot Camp', CAPS_WORDS],
			[u'fahrner-Kampe', u'Fahrner-Kampe', CAPS_NAMES],
			[u'häkkönen', u'Häkkönen', CAPS_NAMES],
			[u'McBurney', u'McBurney', CAPS_NAMES],
			[u'mcBurney', u'McBurney', CAPS_NAMES],
			[u'blumberg', u'Blumberg', CAPS_NAMES],
			[u'roVsing', u'RoVsing', CAPS_NAMES],
			[u'Özdemir', u'Özdemir', CAPS_NAMES],
			[u'özdemir', u'Özdemir', CAPS_NAMES],
		]
		for pair in pairs:
			result = capitalize(pair[0], pair[2])
			if result != pair[1]:
				success = False
				print 'ERROR (caps mode %s): "%s" -> "%s", expected "%s"' % (pair[2], pair[0], result, pair[1])

		if success:
			print "... SUCCESS"

		return success
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
	def test_gmPaths():
		print "testing gmPaths()"
		print "-----------------"
		paths = gmPaths(wx=None, app_name='gnumed')
		print "user     config dir:", paths.user_config_dir
		print "system   config dir:", paths.system_config_dir
		print "local      base dir:", paths.local_base_dir
		print "system app data dir:", paths.system_app_data_dir
		print "working directory  :", paths.working_dir
	#-----------------------------------------------------------------------
	def test_none_if():
		print "testing none_if()"
		print "-----------------"
		tests = [
			[None, None, None],
			['a', 'a', None],
			['a', 'b', 'a'],
			['a', None, 'a'],
			[None, 'a', None],
			[1, 1, None],
			[1, 2, 1],
			[1, None, 1],
			[None, 1, None]
		]

		for test in tests:
			if none_if(value = test[0], none_equivalent = test[1]) != test[2]:
				print 'ERROR: none_if(%s) returned [%s], expected [%s]' % (test[0], none_if(test[0], test[1]), test[2])

		return True
	#-----------------------------------------------------------------------
	def test_bool2str():
		tests = [
			[True, 'Yes', 'Yes', 'Yes'],
			[False, 'OK', 'not OK', 'not OK']
		]
		for test in tests:
			if bool2str(test[0], test[1], test[2]) != test[3]:
				print 'ERROR: bool2str(%s, %s, %s) returned [%s], expected [%s]' % (test[0], test[1], test[2], bool2str(test[0], test[1], test[2]), test[3])

		return True

	#-----------------------------------------------------------------------
	def test_get_unique_filename():
		print get_unique_filename()
		print get_unique_filename(prefix='test-')
		print get_unique_filename(suffix='tst')
		print get_unique_filename(prefix='test-', suffix='tst')
		print get_unique_filename(dir='/home/ncq/Archiv/')
	#-----------------------------------------------------------------------
	def test_size2str():
		print "testing size2str()"
		print "------------------"
		tests = [0, 1, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000, 100000000000, 1000000000000, 10000000000000]
		for test in tests:
			print size2str(test)
	#-----------------------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		#test_str2interval()
		#test_coalesce()
		#test_capitalize()
		#test_import_module()
		#test_mkdir()
		#test_send_mail()
		#test_gmPaths()
		#test_none_if()
		#test_bool2str()
		#test_get_unique_filename()
		test_size2str()

#===========================================================================
# $Log: gmTools.py,v $
# Revision 1.40  2007-10-09 10:29:02  ncq
# - clean up import_module_from_directory()
#
# Revision 1.39  2007/10/08 12:48:17  ncq
# - normalize / and \ in import_module_from_directory() so it works on Windows
#
# Revision 1.38  2007/08/29 14:33:56  ncq
# - better document get_unique_filename()
#
# Revision 1.37  2007/08/28 21:47:19  ncq
# - log user home dir
#
# Revision 1.36  2007/08/15 09:18:56  ncq
# - size2str() and test
#
# Revision 1.35  2007/08/07 21:41:02  ncq
# - cPaths -> gmPaths
#
# Revision 1.34  2007/07/13 09:47:38  ncq
# - fix and test suite for get_unique_filename()
#
# Revision 1.33  2007/07/11 21:06:51  ncq
# - improved docs
# - get_unique_filename()
#
# Revision 1.32  2007/07/10 20:45:42  ncq
# - add unicode CSV reader
# - factor out OOo related code
#
# Revision 1.31  2007/06/19 12:43:17  ncq
# - add bool2str() and test
#
# Revision 1.30  2007/06/10 09:56:03  ncq
# - u''ificiation and flags in regex calls
#
# Revision 1.29  2007/05/17 15:12:59  ncq
# - even more careful about pathes
#
# Revision 1.28  2007/05/17 15:10:16  ncq
# - create user config dir if it doesn't exist
#
# Revision 1.27  2007/05/15 08:20:13  ncq
# - ifdef GetDataDir() on wxMSW as per Robin's suggestion
#
# Revision 1.26  2007/05/14 08:35:06  ncq
# - better logging
# - try to handle platforms with broken GetDataDir()
#
# Revision 1.25  2007/05/13 21:20:54  ncq
# - improved logging
#
# Revision 1.24  2007/05/13 20:22:17  ncq
# - log errors
#
# Revision 1.23  2007/05/08 16:03:55  ncq
# - add console exception display handler
#
# Revision 1.22  2007/05/07 12:31:06  ncq
# - improved path handling and testing
# - switch file to utf8
#
# Revision 1.21  2007/04/21 19:38:27  ncq
# - add none_if() and test suite
#
# Revision 1.20  2007/04/19 13:09:52  ncq
# - add cPaths borg and test suite
#
# Revision 1.19  2007/04/09 16:30:31  ncq
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