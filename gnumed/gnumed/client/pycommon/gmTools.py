# -*- coding: utf8 -*-
__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmTools.py,v 1.66 2008-08-28 18:32:24 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmTools.py,v $
__version__ = "$Revision: 1.66 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

# std libs
import datetime as pydt, re as regex, sys, os, os.path, csv, tempfile, logging, codecs, urllib2 as wget


# GNUmed libs
if __name__ == '__main__':
	# for testing:
	logging.basicConfig(level = logging.DEBUG)
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

from Gnumed.pycommon import gmBorg


_log = logging.getLogger('gm.tools')
_log.info(__version__)

# CAPitalization modes:
(	CAPS_NONE,					# don't touch it
	CAPS_FIRST,					# CAP first char, leave rest as is
	CAPS_ALLCAPS,				# CAP all chars
	CAPS_WORDS,					# CAP first char of every word
	CAPS_NAMES,					# CAP in a way suitable for names (tries to be smart)
	CAPS_FIRST_ONLY				# CAP first char, lowercase the rest
) = range(6)

default_mail_sender = u'gnumed@gmx.net'
default_mail_receiver = u'gnumed-devel@gnu.org'
default_mail_server = u'mail.gmx.net'


u_registered_trademark = u'\u00ae'
u_ellipsis = u'\u2026'
u_diameter = u'\u2300'
u_checkmark_crossed_out = u'\u237B'
u_checkmark_thin = u'\u2713'
u_checkmark_thick = u'\u2714'
u_writing_hand = u'\u270d'
u_pencil_1 = u'\u270e'
u_pencil_2 = u'\u270f'
u_pencil_3 = u'\u2710'

#===========================================================================
def check_for_update(url=None, current_branch=None, current_version=None, consider_latest_branch=False):
	"""Check for new releases at <url>.

	Returns (bool, text).
	True: new release available
	False: up to data
	None: don't know
	"""
	try:
		remote_file = wget.urlopen(url)
	except (wget.URLError, ValueError, OSError):
		_log.exception("cannot retrieve version file from [%s]", url)
		return (None, _('Cannot retrieve version information.'))

	_log.debug('retrieving version information from [%s]', url)

	from Gnumed.pycommon import gmCfg2
	cfg = gmCfg2.gmCfgData()
	cfg.add_stream_source(source = 'gm-versions', stream = remote_file)
	remote_file.close()

	latest_branch = cfg.get('latest branch', 'branch', source_order = [('gm-versions', 'return')])
#	latest_release_on_latest_branch = cfg.get('latest branch', 'latest release', source_order = [('gm-versions', 'return')])
	latest_release_on_latest_branch = cfg.get('branch %s' % latest_branch, 'latest release', source_order = [('gm-versions', 'return')])
	latest_release_on_current_branch = cfg.get('branch %s' % current_branch, 'latest release', source_order = [('gm-versions', 'return')])

	_log.info('current release: %s', current_version)
	_log.info('current branch: %s', current_branch)
	_log.info('latest release on current branch: %s', latest_release_on_current_branch)
	_log.info('latest branch: %s', latest_branch)
	_log.info('latest release on latest branch: %s', latest_release_on_latest_branch)

	# anything known ?
	no_release_information_available = (
		(
			(latest_release_on_current_branch is None) and
			(latest_release_on_latest_branch is None)
		) or (
			not consider_latest_branch and
			(latest_release_on_current_branch is None)
		)
	)
	if no_release_information_available:
		msg = _('There is no version information available from:\n\n %s') % url
		return (None, msg)

	# up to date ?
	if not consider_latest_branch:
		if current_version <= latest_release_on_current_branch:
			return (False, None)
	else:
		if current_version <= latest_release_on_latest_branch:
			return (False, None)
		if latest_release_on_latest_branch is None:
			if current_version <= latest_release_on_current_branch:
				return (False, None)

	current_branch_release_available = (
		(latest_release_on_current_branch is not None) and
		(latest_release_on_current_branch > current_version)
	)

	latest_branch_release_available = (
		(latest_branch is not None)
			and
		(
			(latest_branch > current_branch) or (
				(latest_branch == current_branch) and
				(latest_release_on_latest_branch > current_version)
			)
		)
	)

	if not (current_branch_release_available or latest_branch_release_available):
		return (False, None)

	# not up to date
	msg = _('A new version of GNUmed is available.\n\n')
	msg += _(' Your version: "%s"\n') % current_version
	if consider_latest_branch:
		if current_branch_release_available:
			msg += _(' New version: "%s"\n') % latest_release_on_current_branch
			msg += _(' - bug fixes only\n')
			msg += _(' - no database upgrade needed\n')
		if latest_branch_release_available:
			msg += _(' New version: "%s"\n') % latest_release_on_latest_branch
			msg += _(' - bug fixes and new features\n')
			msg += _(' - database upgrade required\n')
	else:
		msg += _(' New version: "%s"\n') % latest_release_on_current_branch
		msg += _(' - bug fixes only\n')
		msg += _(' - no database upgrade needed\n')

	msg += '\n\n'
	msg += _('Version information loaded from:\n [%s]') % url

	return (True, msg)
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
def handle_uncaught_exception_console(t, v, tb):

	print ",========================================================"
	print "| Unhandled exception caught !"
	print "| Type :", t
	print "| Value:", v
	print "`========================================================"
	_log.critical('unhandled exception caught', exc_info = (t,v,tb))
	sys.__excepthook__(t,v,tb)
#===========================================================================
class gmPaths(gmBorg.cBorg):

	def __init__(self, app_name=None, wx=None):
		"""Setup pathes.

		<app_name> will default to (name of the script - .py)
		"""
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
			_log.info('app name detected as [%s]', app_name)
		else:
			_log.info('app name passed in as [%s]', app_name)

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
			_log.debug('wxPython not available')
			self.__log_paths()
			return True

		# retry with wxPython
		std_paths = wx.StandardPaths.Get()
		_log.info('wxPython app name set to [%s]', wx.GetApp().GetAppName())

		try:
			self.user_config_dir = os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name)
		except ValueError:
			mkdir(os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name))
			self.user_config_dir = os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name)

		try:
			tmp = std_paths.GetConfigDir()
			if not tmp.endswith(app_name):
				tmp = os.path.join(tmp, app_name)
			self.system_config_dir = tmp
		except ValueError:
			pass

		try:
			# Robin attests that the following doesn't give
			# sane values on Windows, so IFDEF it
			if 'wxMSW' in wx.PlatformInfo:
				_log.warning('this platform (wxMSW) returns a broken value for the system-wide application data dir')
				self.system_app_data_dir = self.local_base_dir
			else:
				self.system_app_data_dir = std_paths.GetDataDir()
		except ValueError:
			pass

		self.__log_paths()
		return True
	#--------------------------------------
	def __log_paths(self):
		_log.debug('local application base dir: %s', self.local_base_dir)
		_log.debug('current working dir: %s', self.working_dir)
		_log.debug('user home dir: %s', os.path.expanduser('~'))
		_log.debug('user-specific config dir: %s', self.user_config_dir)
		_log.debug('system-wide config dir: %s', self.system_config_dir)
		_log.debug('system-wide application data dir: %s', self.system_app_data_dir)
	#--------------------------------------
	# properties
	#--------------------------------------
	def _set_user_config_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:user_config_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.error(msg)
			raise ValueError(msg)
		self.__user_config_dir = path

	def _get_user_config_dir(self):
		return self.__user_config_dir

	user_config_dir = property(_get_user_config_dir, _set_user_config_dir)
	#--------------------------------------
	def _set_system_config_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:system_config_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.error(msg)
			raise ValueError(msg)
		self.__system_config_dir = path

	def _get_system_config_dir(self):
		return self.__system_config_dir

	system_config_dir = property(_get_system_config_dir, _set_system_config_dir)
	#--------------------------------------
	def _set_system_app_data_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:system_app_data_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.error(msg)
			raise ValueError(msg)
		self.__system_app_data_dir = path

	def _get_system_app_data_dir(self):
		return self.__system_app_data_dir

	system_app_data_dir = property(_get_system_app_data_dir, _set_system_app_data_dir)
#===========================================================================
def send_mail(sender=None, receiver=None, message=None, server=None, auth=None, debug=False, subject=None, encoding='latin1'):
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

	if subject is None:
		subject = u'gmTools.py: send_mail() test'

	body = u"""From: %s
To: %s
Subject: %s

%s
""" % (sender, u', '.join(receiver), subject[:50].replace('\r', '/').replace('\n', '/'), message)

	import smtplib
	session = smtplib.SMTP(server)
	session.set_debuglevel(debug)
	if auth is not None:
		session.login(auth['user'], auth['password'])
	refused = session.sendmail(sender, receiver, body.encode(encoding))
	session.quit()
	if len(refused) != 0:
		_log.error("refused recipients: %s" % refused)
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
		_log.info('appending to sys.path: [%s]' % module_path)
		sys.path.append(module_path)
		remove_path = True
	else:
		remove_path = False

	if module_name.endswith('.py'):
		module_name = module_name[:-3]

	try:
		module = __import__(module_name)
		_log.info('imported module [%s] as [%s]' % (module_name, module))
	except StandardError:
		_log.exception('cannot __import__() module [%s] from [%s]' % (module_name, module_path))
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

	unit_keys = {
		'year': _('yYaA_keys_year'),
		'month': _('mM_keys_month'),
		'week': _('wW_keys_week'),
		'day': _('dD_keys_day'),
		'hour': _('hH_keys_hour')
	}

	# "(~)35(yY)"	- at age 35 years
	keys = '|'.join(list(unit_keys['year'].replace('_keys_year', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(%s|\s|\t)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(days = (int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]) * days_per_year))

	# "(~)12mM" - at age 12 months
	keys = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(%s)+(\s|\t)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		years, months = divmod (
			int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]),
			12
		)
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# weeks
	keys = '|'.join(list(unit_keys['week'].replace('_keys_week', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(%s)+(\s|\t)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(weeks = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# days
	keys = '|'.join(list(unit_keys['day'].replace('_keys_day', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(%s)+(\s|\t)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
		return pydt.timedelta(days = int(regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)[0]))

	# hours
	keys = '|'.join(list(unit_keys['hour'].replace('_keys_hour', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(\s|\t)*(%s)+(\s|\t)*$' % keys, str_interval, flags = regex.LOCALE | regex.UNICODE):
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
	keys_year = '|'.join(list(unit_keys['year'].replace('_keys_year', u'')))
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+(\s|\t)*$' % (keys_year, keys_month), str_interval, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)
		years, months = divmod(int(parts[1]), 12)
		years += int(parts[0])
		return pydt.timedelta(days = ((years * days_per_year) + (months * days_per_month)))

	# nMnW - months, weeks
	keys_month = '|'.join(list(unit_keys['month'].replace('_keys_month', u'')))
	keys_week = '|'.join(list(unit_keys['week'].replace('_keys_week', u'')))
	if regex.match(u'^(\s|\t)*~*(\s|\t)*\d+(%s|\s|\t)+\d+(\s|\t)*(%s)+(\s|\t)*$' % (keys_month, keys_week), str_interval, flags = regex.LOCALE | regex.UNICODE):
		parts = regex.findall(u'\d+', str_interval, flags = regex.LOCALE | regex.UNICODE)
		months, weeks = divmod(int(parts[1]), 4)
		months += int(parts[0])
		return pydt.timedelta(days = ((months * days_per_month) + (weeks * days_per_week)))

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
def bool2subst(boolean=None, true_return=True, false_return=False, none_return=None):
	if boolean is None:
		return none_return
	if boolean is True:
		return true_return
	if boolean is False:
		return false_return
	raise ValueError('bool2subst(): <boolean> arg must be either of True, False, None')
#---------------------------------------------------------------------------
def bool2str(boolean=None, true_str='True', false_str='False'):
	return bool2subst (
		boolean = bool(boolean),
		true_return = true_str,
		false_return = false_str
	)
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

	try:
		return template_initial % initial
	except TypeError:
		return template_initial
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
		if len(text) == 1:
			return text[0].upper()
		return text[0].upper() + text[1:]

	if mode == CAPS_ALLCAPS:
		return text.upper()

	if mode == CAPS_FIRST_ONLY:
		if len(text) == 1:
			return text[0].upper()
		return text[0].upper() + text[1:].lower()

	if mode == CAPS_WORDS:
		return regex.sub(ur'(\w)(\w+)', lambda x: x.group(1).upper() + x.group(2).lower(), text)

	if mode == CAPS_NAMES:
		#return regex.sub(r'\w+', __cap_name, text)
		return capitalize(text=text, mode=CAPS_FIRST)		# until fixed

	print "ERROR: invalid capitalization mode: [%s], leaving input as is" % mode
	return text
#---------------------------------------------------------------------------
def wrap(text=None, width=None, initial_indent=u'', subsequent_indent=u'', eol=u'\n'):
	"""A word-wrap function that preserves existing line breaks
	and most spaces in the text. Expects that existing line
	breaks are posix newlines (\n).
	"""
	wrapped = initial_indent + reduce (
		lambda line, word, width=width: '%s%s%s' % (
			line,
			' \n'[(len(line) - line.rfind('\n') - 1 + len(word.split('\n',1)[0]) >= width)],
			word
		),
		text.split(' ')
	)

	if subsequent_indent != u'':
		wrapped = (u'\n%s' % subsequent_indent).join(wrapped.split('\n'))

	if eol != u'\n':
		wrapped = wrapped.replace('\n', eol)

	return wrapped
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
			'10m1w',
			'invalid interval input'
		]

		for str_interval in str_intervals:
			print "input: <%s>" % str_interval
			print "  ==>", str2interval(str_interval=str_interval)

		return True
	#-----------------------------------------------------------------------
	def test_coalesce():
		print 'testing coalesce()'
		print "------------------"
		tests = [
			[None, 'something other than <None>', None, None, 'something other than <None>'],
			['Captain', 'Mr.', '%s.'[:4], 'Mr.', 'Capt.'],
			['value to test', 'test 3 failed', 'template with "%s" included', None, 'template with "value to test" included'],
			['value to test', 'test 4 failed', 'template with value not included', None, 'template with value not included'],
			[None, 'initial value was None', 'template_initial: %s', None, 'initial value was None'],
			[None, 'initial value was None', 'template_initial: %%(abc)s', None, 'initial value was None']
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
	def test_bool2subst():

		print bool2subst(True, 'True', 'False', 'is None')
		print bool2subst(False, 'True', 'False', 'is None')
		print bool2subst(None, 'True', 'False', 'is None')
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
	def test_wrap():
		test = 'line 1\nline 2\nline 3'

		print "wrap 5-6-7 initial 0, subsequent 0"
		print wrap(test, 5)
		print
		print wrap(test, 6)
		print
		print wrap(test, 7)
		print "-------"
		raw_input()
		print "wrap 5 initial 1-1-3, subsequent 1-3-1"
		print wrap(test, 5, u' ', u' ')
		print
		print wrap(test, 5, u' ', u'   ')
		print
		print wrap(test, 5, u'   ', u' ')
		print "-------"
		raw_input()
		print "wrap 6 initial 1-1-3, subsequent 1-3-1"
		print wrap(test, 6, u' ', u' ')
		print
		print wrap(test, 6, u' ', u'   ')
		print
		print wrap(test, 6, u'   ', u' ')
		print "-------"
		raw_input()
		print "wrap 7 initial 1-1-3, subsequent 1-3-1"
		print wrap(test, 7, u' ', u' ')
		print
		print wrap(test, 7, u' ', u'   ')
		print
		print wrap(test, 7, u'   ', u' ')
	#-----------------------------------------------------------------------
	def test_check_for_update():

		test_data = [
			('http://www.gnumed.de/downloads/gnumed-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', True),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.5', True)
		]

		for test in test_data:
			print "arguments:", test
			found, msg = check_for_update(test[0], test[1], test[2], test[3])
			print msg

		return
	#-----------------------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		#test_check_for_update()
		#test_str2interval()
		test_coalesce()
		#test_capitalize()
		#test_import_module()
		#test_mkdir()
		#test_send_mail()
		#test_gmPaths()
		#test_none_if()
		#test_bool2str()
		#test_bool2subst()
		#test_get_unique_filename()
		#test_size2str()
		#test_wrap()

#===========================================================================
# $Log: gmTools.py,v $
# Revision 1.66  2008-08-28 18:32:24  ncq
# - read latest branch then latest release from branch group
#
# Revision 1.65  2008/08/20 13:53:57  ncq
# - add some coalesce tests
#
# Revision 1.64  2008/07/28 15:43:35  ncq
# - teach wrap() about target EOL
#
# Revision 1.63  2008/07/12 15:30:56  ncq
# - improved coalesce test
#
# Revision 1.62  2008/07/12 15:24:37  ncq
# - impove coalesce to allow template_initial to be returned *instead* of
#   initial substituted into the template by not including a substitution
#
# Revision 1.61  2008/07/10 20:51:38  ncq
# - better logging
#
# Revision 1.60  2008/07/10 19:59:09  ncq
# - better logging
# - check whether sys config dir ends in "gnumed"
#
# Revision 1.59  2008/07/07 11:34:41  ncq
# - robustify capsify on single character strings
#
# Revision 1.58  2008/06/28 18:25:01  ncq
# - add unicode Registered TM symbol
#
# Revision 1.57  2008/05/31 16:32:42  ncq
# - a couple of unicode shortcuts
#
# Revision 1.56  2008/05/26 12:05:50  ncq
# - improved wording of update message
# - better handling of CVS tip
#
# Revision 1.55  2008/05/21 15:51:45  ncq
# - if cannot open update URL may throw OSError, so deal with that
#
# Revision 1.54  2008/05/21 14:01:32  ncq
# - add check_for_update and tests
#
# Revision 1.53  2008/05/13 14:09:36  ncq
# - str2interval: support xMxW syntax
#
# Revision 1.52  2008/05/07 15:18:01  ncq
# - i18n str2interval
#
# Revision 1.51  2008/04/16 20:34:43  ncq
# - add bool2subst tests
#
# Revision 1.50  2008/04/11 12:24:39  ncq
# - add initial_indent/subsequent_indent and tests to wrap()
#
# Revision 1.49  2008/03/20 15:29:51  ncq
# - bool2subst() supporting None, make bool2str() use it
#
# Revision 1.48  2008/03/02 15:10:32  ncq
# - truncate exception comment to 50 chars when used as subject
#
# Revision 1.47  2008/01/16 19:42:24  ncq
# - whitespace sync
#
# Revision 1.46  2007/12/23 11:59:40  ncq
# - improved docs
#
# Revision 1.45  2007/12/12 16:24:09  ncq
# - general cleanup
#
# Revision 1.44  2007/12/11 14:33:48  ncq
# - use standard logging module
#
# Revision 1.43  2007/11/28 13:59:23  ncq
# - test improved
#
# Revision 1.42  2007/11/21 13:28:35  ncq
# - enhance send_mail() with subject and encoding
# - handle body formatting
#
# Revision 1.41  2007/10/23 21:23:30  ncq
# - cleanup
#
# Revision 1.40  2007/10/09 10:29:02  ncq
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