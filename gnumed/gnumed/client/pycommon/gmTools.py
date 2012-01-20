# -*- coding: utf8 -*-
__doc__ = """GNUmed general tools."""

#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# std libs
import re as regex, sys, os, os.path, csv, tempfile, logging, hashlib
import decimal
import cPickle, zlib
import xml.sax.saxutils as xml_tools


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

# CAPitalization modes:
(	CAPS_NONE,					# don't touch it
	CAPS_FIRST,					# CAP first char, leave rest as is
	CAPS_ALLCAPS,				# CAP all chars
	CAPS_WORDS,					# CAP first char of every word
	CAPS_NAMES,					# CAP in a way suitable for names (tries to be smart)
	CAPS_FIRST_ONLY				# CAP first char, lowercase the rest
) = range(6)


u_right_double_angle_quote = u'\u00AB'		# <<
u_registered_trademark = u'\u00AE'
u_plus_minus = u'\u00B1'
u_left_double_angle_quote = u'\u00BB'		# >>
u_one_quarter = u'\u00BC'
u_one_half = u'\u00BD'
u_three_quarters = u'\u00BE'
u_ellipsis = u'\u2026'
u_down_left_arrow = u'\u21B5'				# <-'
u_left_arrow = u'\u2190'					# <--
u_right_arrow = u'\u2192'					# -->
u_sum = u'\u2211'
u_corresponds_to = u'\u2258'
u_infinity = u'\u221E'
u_diameter = u'\u2300'
u_checkmark_crossed_out = u'\u237B'
u_box_horiz_single = u'\u2500'
u_box_horiz_4dashes = u'\u2508'
u_box_top_double = u'\u2550'
u_box_top_left_double_single = u'\u2552'
u_box_top_right_double_single = u'\u2555'
u_box_top_left_arc = u'\u256d'
u_box_bottom_right_arc = u'\u256f'
u_box_bottom_left_arc = u'\u2570'
u_box_horiz_light_heavy = u'\u257c'
u_box_horiz_heavy_light = u'\u257e'
u_skull_and_crossbones = u'\u2620'
u_frowning_face = u'\u2639'
u_smiling_face = u'\u263a'
u_black_heart = u'\u2665'
u_checkmark_thin = u'\u2713'
u_checkmark_thick = u'\u2714'
u_writing_hand = u'\u270d'
u_pencil_1 = u'\u270e'
u_pencil_2 = u'\u270f'
u_pencil_3 = u'\u2710'
u_latin_cross = u'\u271d'
u_replacement_character = u'\ufffd'
u_link_symbol = u'\u1f517'

#===========================================================================
def handle_uncaught_exception_console(t, v, tb):

	print ".========================================================"
	print "| Unhandled exception caught !"
	print "| Type :", t
	print "| Value:", v
	print "`========================================================"
	_log.critical('unhandled exception caught', exc_info = (t,v,tb))
	sys.__excepthook__(t,v,tb)
#===========================================================================
# path level operations
#---------------------------------------------------------------------------
def mkdir(directory=None):
	try:
		os.makedirs(directory)
	except OSError, e:
		if (e.errno == 17) and not os.path.isdir(directory):
			raise
	return True

#---------------------------------------------------------------------------
class gmPaths(gmBorg.cBorg):
	"""This class provides the following paths:

	.home_dir
	.local_base_dir
	.working_dir
	.user_config_dir
	.system_config_dir
	.system_app_data_dir
	.tmp_dir (readonly)
	"""
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

		if wx is None:
			_log.debug('wxPython not available')
		_log.debug('detecting paths directly')

		if app_name is None:
			app_name, ext = os.path.splitext(os.path.basename(sys.argv[0]))
			_log.info('app name detected as [%s]', app_name)
		else:
			_log.info('app name passed in as [%s]', app_name)

		# the user home, doesn't work in Wine so work around that
		self.__home_dir = None

		# where the main script (the "binary") is installed
		#self.local_base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '.'))
		self.local_base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

		# the current working dir at the OS
		self.working_dir = os.path.abspath(os.curdir)

		# user-specific config dir, usually below the home dir
		#mkdir(os.path.expanduser(os.path.join('~', '.%s' % app_name)))
		#self.user_config_dir = os.path.expanduser(os.path.join('~', '.%s' % app_name))
		mkdir(os.path.join(self.home_dir, '.%s' % app_name))
		self.user_config_dir = os.path.join(self.home_dir, '.%s' % app_name)

		# system-wide config dir, usually below /etc/ under UN*X
		try:
			self.system_config_dir = os.path.join('/etc', app_name)
		except ValueError:
			#self.system_config_dir = self.local_base_dir
			self.system_config_dir = self.user_config_dir

		# system-wide application data dir
		try:
			self.system_app_data_dir = os.path.join(sys.prefix, 'share', app_name)
		except ValueError:
			self.system_app_data_dir = self.local_base_dir

		# temporary directory
		try:
			self.__tmp_dir_already_set
			_log.debug('temp dir already set')
		except AttributeError:
			tmp_base = os.path.join(tempfile.gettempdir(), app_name)
			mkdir(tmp_base)
			_log.info('previous temp dir: %s', tempfile.gettempdir())
			tempfile.tempdir = tmp_base
			_log.info('intermediate temp dir: %s', tempfile.gettempdir())
			self.tmp_dir = tempfile.mkdtemp(prefix = r'gm-')

		self.__log_paths()
		if wx is None:
			return True

		# retry with wxPython
		_log.debug('re-detecting paths with wxPython')

		std_paths = wx.StandardPaths.Get()
		_log.info('wxPython app name is [%s]', wx.GetApp().GetAppName())

		# user-specific config dir, usually below the home dir
		mkdir(os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name))
		self.user_config_dir = os.path.join(std_paths.GetUserConfigDir(), '.%s' % app_name)

		# system-wide config dir, usually below /etc/ under UN*X
		try:
			tmp = std_paths.GetConfigDir()
			if not tmp.endswith(app_name):
				tmp = os.path.join(tmp, app_name)
			self.system_config_dir = tmp
		except ValueError:
			# leave it at what it was from direct detection
			pass

		# system-wide application data dir
		# Robin attests that the following doesn't always
		# give sane values on Windows, so IFDEF it
		if 'wxMSW' in wx.PlatformInfo:
			_log.warning('this platform (wxMSW) sometimes returns a broken value for the system-wide application data dir')
		else:
			try:
				self.system_app_data_dir = std_paths.GetDataDir()
			except ValueError:
				pass

		self.__log_paths()
		return True
	#--------------------------------------
	def __log_paths(self):
		_log.debug('sys.argv[0]: %s', sys.argv[0])
		_log.debug('local application base dir: %s', self.local_base_dir)
		_log.debug('current working dir: %s', self.working_dir)
		#_log.debug('user home dir: %s', os.path.expanduser('~'))
		_log.debug('user home dir: %s', self.home_dir)
		_log.debug('user-specific config dir: %s', self.user_config_dir)
		_log.debug('system-wide config dir: %s', self.system_config_dir)
		_log.debug('system-wide application data dir: %s', self.system_app_data_dir)
		_log.debug('temporary dir: %s', self.tmp_dir)
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
	#--------------------------------------
	def _set_home_dir(self, path):
		raise ValueError('invalid to set home dir')

	def _get_home_dir(self):
		if self.__home_dir is not None:
			return self.__home_dir

		tmp = os.path.expanduser('~')
		if tmp == '~':
			_log.error('this platform does not expand ~ properly')
			try:
				tmp = os.environ['USERPROFILE']
			except KeyError:
				_log.error('cannot access $USERPROFILE in environment')

		if not (
			os.access(tmp, os.R_OK)
				and
			os.access(tmp, os.X_OK)
				and
			os.access(tmp, os.W_OK)
		):
			msg = '[%s:home_dir]: invalid path [%s]' % (self.__class__.__name__, tmp)
			_log.error(msg)
			raise ValueError(msg)

		self.__home_dir = tmp
		return self.__home_dir

	home_dir = property(_get_home_dir, _set_home_dir)
	#--------------------------------------
	def _set_tmp_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:tmp_dir]: invalid path [%s]' % (self.__class__.__name__, path)
			_log.error(msg)
			raise ValueError(msg)
		_log.debug('previous temp dir: %s', tempfile.gettempdir())
		self.__tmp_dir = path
		tempfile.tempdir = self.__tmp_dir
		self.__tmp_dir_already_set = True

	def _get_tmp_dir(self):
		return self.__tmp_dir

	tmp_dir = property(_get_tmp_dir, _set_tmp_dir)
#===========================================================================
# file related tools
#---------------------------------------------------------------------------
def file2md5(filename=None, return_hex=True):
	blocksize = 2**10 * 128			# 128k, since md5 use 128 byte blocks
	_log.debug('md5(%s): <%s> byte blocks', filename, blocksize)

	f = open(filename, 'rb')

	md5 = hashlib.md5()
	while True:
		data = f.read(blocksize)
		if not data:
			break
		md5.update(data)

	_log.debug('md5(%s): %s', filename, md5.hexdigest())

	if return_hex:
		return md5.hexdigest()
	return md5.digest()
#---------------------------------------------------------------------------
def unicode2charset_encoder(unicode_csv_data, encoding='utf-8'):
	for line in unicode_csv_data:
		yield line.encode(encoding)

#def utf_8_encoder(unicode_csv_data):
#	for line in unicode_csv_data:
#		yield line.encode('utf-8')

default_csv_reader_rest_key = u'list_of_values_of_unknown_fields'

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, encoding='utf-8', **kwargs):

	# csv.py doesn't do Unicode; encode temporarily as UTF-8:
	try:
		is_dict_reader = kwargs['dict']
		del kwargs['dict']
		if is_dict_reader is not True:
			raise KeyError
		kwargs['restkey'] = default_csv_reader_rest_key
		csv_reader = csv.DictReader(unicode2charset_encoder(unicode_csv_data), dialect=dialect, **kwargs)
	except KeyError:
		is_dict_reader = False
		csv_reader = csv.reader(unicode2charset_encoder(unicode_csv_data), dialect=dialect, **kwargs)

	for row in csv_reader:
		# decode ENCODING back to Unicode, cell by cell:
		if is_dict_reader:
			for key in row.keys():
				if key == default_csv_reader_rest_key:
					old_data = row[key]
					new_data = []
					for val in old_data:
						new_data.append(unicode(val, encoding))
					row[key] = new_data
					if default_csv_reader_rest_key not in csv_reader.fieldnames:
						csv_reader.fieldnames.append(default_csv_reader_rest_key)
				else:
					row[key] = unicode(row[key], encoding)
			yield row
		else:
			yield [ unicode(cell, encoding) for cell in row ]
			#yield [unicode(cell, 'utf-8') for cell in row]
#---------------------------------------------------------------------------
def get_unique_filename(prefix=None, suffix=None, tmp_dir=None):
	"""This introduces a race condition between the file.close() and
	actually using the filename.

	The file will not exist after calling this function.
	"""
	if tmp_dir is not None:
		if (
			not os.access(tmp_dir, os.F_OK)
				or
			not os.access(tmp_dir, os.X_OK | os.W_OK)
		):
			_log.info('cannot find temporary dir [%s], using system default', tmp_dir)
			tmp_dir = None

	kwargs = {'dir': tmp_dir}

	if prefix is None:
		kwargs['prefix'] = 'gnumed-'
	else:
		kwargs['prefix'] = prefix

	if suffix in [None, u'']:
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
def import_module_from_directory(module_path=None, module_name=None, always_remove_path=False):
	"""Import a module from any location."""

	remove_path = always_remove_path or False
	if module_path not in sys.path:
		_log.info('appending to sys.path: [%s]' % module_path)
		sys.path.append(module_path)
		remove_path = True

	_log.debug('will remove import path: %s', remove_path)

	if module_name.endswith('.py'):
		module_name = module_name[:-3]

	try:
		module = __import__(module_name)
	except StandardError:
		_log.exception('cannot __import__() module [%s] from [%s]' % (module_name, module_path))
		while module_path in sys.path:
			sys.path.remove(module_path)
		raise

	_log.info('imported module [%s] as [%s]' % (module_name, module))
	if remove_path:
		while module_path in sys.path:
			sys.path.remove(module_path)

	return module
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
def none_if(value=None, none_equivalent=None, strip_string=False):
	"""Modelled after the SQL NULLIF function."""
	if value is None:
		return None
	if strip_string:
		stripped = value.strip()
	else:
		stripped = value
	if stripped == none_equivalent:
		return None
	return value
#---------------------------------------------------------------------------
def coalesce(initial=None, instead=None, template_initial=None, template_instead=None, none_equivalents=None, function_initial=None):
	"""Modelled after the SQL coalesce function.

	To be used to simplify constructs like:

		if initial is None (or in none_equivalents):
			real_value = (template_instead % instead) or instead
		else:
			real_value = (template_initial % initial) or initial
		print real_value

	@param initial: the value to be tested for <None>
	@type initial: any Python type, must have a __str__ method if template_initial is not None
	@param instead: the value to be returned if <initial> is None
	@type instead: any Python type, must have a __str__ method if template_instead is not None
	@param template_initial: if <initial> is returned replace the value into this template, must contain one <%s> 
	@type template_initial: string or None
	@param template_instead: if <instead> is returned replace the value into this template, must contain one <%s> 
	@type template_instead: string or None

	example:
		function_initial = ('strftime', '%Y-%m-%d')

	Ideas:
		- list of insteads: initial, [instead, template], [instead, template], [instead, template], template_initial, ...
	"""
	if none_equivalents is None:
		none_equivalents = [None]

	if initial in none_equivalents:

		if template_instead is None:
			return instead

		return template_instead % instead

	if function_initial is not None:
		funcname, args = function_initial
		func = getattr(initial, funcname)
		initial = func(args)

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
def input2decimal(initial=None):

	if isinstance(initial, decimal.Decimal):
		return True, initial

	val = initial

	# float ? -> to string first
	if type(val) == type(float(1.4)):
		val = str(val)

	# string ? -> "," to "."
	if isinstance(val, basestring):
		val = val.replace(',', '.', 1)
		val = val.strip()

	try:
		d = decimal.Decimal(val)
		return True, d
	except (TypeError, decimal.InvalidOperation):
		return False, val
#---------------------------------------------------------------------------
def input2int(initial=None, minval=None, maxval=None):

	val = initial

	# string ? -> "," to "."
	if isinstance(val, basestring):
		val = val.replace(',', '.', 1)
		val = val.strip()

	try:
		int_val = int(val)
	except (TypeError, ValueError):
		_log.exception('int(%s) failed', val)
		return False, val

	if minval is not None:
		if int_val < minval:
			_log.debug('%s < min (%s)', val, minval)
			return False, val
	if maxval is not None:
		if int_val > maxval:
			_log.debug('%s > max (%s)', val, maxval)
			return False, val

	return True, int_val
#---------------------------------------------------------------------------
def strip_leading_empty_lines(lines=None, text=None, eol=u'\n'):
	return_join = False
	if lines is None:
		return_join = True
		lines = eol.split(text)

	while True:
		if lines[0].strip(eol).strip() != u'':
			break
		lines = lines[1:]

	if return_join:
		return eol.join(lines)

	return lines
#---------------------------------------------------------------------------
def strip_trailing_empty_lines(lines=None, text=None, eol=u'\n'):
	return_join = False
	if lines is None:
		return_join = True
		lines = eol.split(text)

	while True:
		if lines[-1].strip(eol).strip() != u'':
			break
		lines = lines[:-1]

	if return_join:
		return eol.join(lines)

	return lines
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
#---------------------------------------------------------------------------
def unwrap(text=None, max_length=None, strip_whitespace=True, remove_empty_lines=True, line_separator = u' // '):

	text = text.replace(u'\r', u'')
	lines = text.split(u'\n')
	text = u''
	for line in lines:

		if strip_whitespace:
			line = line.strip().strip(u'\t').strip()

		if remove_empty_lines:
			if line == u'':
				continue

		text += (u'%s%s' % (line, line_separator))

	text = text.rstrip(line_separator)

	if max_length is not None:
		text = text[:max_length]

	text = text.rstrip(line_separator)

	return text
#---------------------------------------------------------------------------
def xml_escape_string(text=None):
	"""check for special XML characters and transform them"""
	return xml_tools.escape (
		text,
		entities = {
			u'&': u'&amp;'
		}
	)
#	text = text.replace(u'&', u'&amp;')
#	return text
#---------------------------------------------------------------------------
def tex_escape_string(text=None):
	"""check for special LaTeX characters and transform them"""

	text = text.replace(u'\\', u'$\\backslash$')
	text = text.replace(u'{', u'\\{')
	text = text.replace(u'}', u'\\}')
	text = text.replace(u'%', u'\\%')
	text = text.replace(u'&', u'\\&')
	text = text.replace(u'#', u'\\#')
	text = text.replace(u'$', u'\\$')
	text = text.replace(u'_', u'\\_')

	text = text.replace(u'^', u'\\verb#^#')
	text = text.replace('~','\\verb#~#')

	return text
#---------------------------------------------------------------------------
def prompted_input(prompt=None, default=None):
	"""Obtains entry from standard input.

	prompt: Prompt text to display in standard output
	default: Default value (for user to press enter only)
	CTRL-C: aborts and returns None
	"""
	if prompt is None:
		msg = u'(CTRL-C aborts)'
	else:
		msg = u'%s (CTRL-C aborts)' % prompt

	if default is None:
		msg = msg + u': '
	else:
		msg = u'%s [%s]: ' % (msg, default)

	try:
		usr_input = raw_input(msg)
	except KeyboardInterrupt:
		return None

	if usr_input == '':
		return default

	return usr_input

#===========================================================================
# image handling tools
#---------------------------------------------------------------------------
# builtin (ugly but tried and true) fallback icon
__icon_serpent = \
"""x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec"""

def get_icon(wx=None):

	paths = gmPaths(app_name = u'gnumed', wx = wx)

	candidates = [
		os.path.join(paths.system_app_data_dir, 'bitmaps', 'gm_icon-serpent_and_gnu.png'),
		os.path.join(paths.local_base_dir, 'bitmaps', 'gm_icon-serpent_and_gnu.png'),
		os.path.join(paths.system_app_data_dir, 'bitmaps', 'serpent.png'),
		os.path.join(paths.local_base_dir, 'bitmaps', 'serpent.png')
	]

	found_as = None
	for candidate in candidates:
		try:
			open(candidate, 'r').close()
			found_as = candidate
			break
		except IOError:
			_log.debug('icon not found in [%s]', candidate)

	if found_as is None:
		_log.warning('no icon file found, falling back to builtin (ugly) icon')
		icon_bmp_data = wx.BitmapFromXPMData(cPickle.loads(zlib.decompress(__icon_serpent)))
		icon.CopyFromBitmap(icon_bmp_data)
	else:
		_log.debug('icon found in [%s]', found_as)
		icon = wx.EmptyIcon()
		try:
			icon.LoadFile(found_as, wx.BITMAP_TYPE_ANY)		#_PNG
		except AttributeError:
			_log.exception(u"this platform doesn't support wx.Icon().LoadFile()")

	return icon
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#-----------------------------------------------------------------------
	def test_input2decimal():

		tests = [
			[None, False],

			['', False],
			[' 0 ', True, 0],

			[0, True, 0],
			[0.0, True, 0],
			[.0, True, 0],
			['0', True, 0],
			['0.0', True, 0],
			['0,0', True, 0],
			['00.0', True, 0],
			['.0', True, 0],
			[',0', True, 0],

			[0.1, True, decimal.Decimal('0.1')],
			[.01, True, decimal.Decimal('0.01')],
			['0.1', True, decimal.Decimal('0.1')],
			['0,1', True, decimal.Decimal('0.1')],
			['00.1', True, decimal.Decimal('0.1')],
			['.1', True, decimal.Decimal('0.1')],
			[',1', True, decimal.Decimal('0.1')],

			[1, True, 1],
			[1.0, True, 1],
			['1', True, 1],
			['1.', True, 1],
			['1,', True, 1],
			['1.0', True, 1],
			['1,0', True, 1],
			['01.0', True, 1],
			['01,0', True, 1],
			[' 01, ', True, 1],

			[decimal.Decimal('1.1'), True, decimal.Decimal('1.1')]
		]
		for test in tests:
			conversion_worked, result = input2decimal(initial = test[0])

			expected2work = test[1]

			if conversion_worked:
				if expected2work:
					if result == test[2]:
						continue
					else:
						print "ERROR (conversion result wrong): >%s<, expected >%s<, got >%s<" % (test[0], test[2], result)
				else:
					print "ERROR (conversion worked but was expected to fail): >%s<, got >%s<" % (test[0], result)
			else:
				if not expected2work:
					continue
				else:
					print "ERROR (conversion failed but was expected to work): >%s<, expected >%s<" % (test[0], test[2])
	#-----------------------------------------------------------------------
	def test_input2int():
		print input2int(0)
		print input2int('0')
		print input2int(u'0', 0, 0)
	#-----------------------------------------------------------------------
	def test_coalesce():

		import datetime as dt
		print coalesce(initial = dt.datetime.now(), template_initial = u'-- %s --', function_initial = ('strftime', u'%Y-%m-%d'))

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
	def test_gmPaths():
		print "testing gmPaths()"
		print "-----------------"
		paths = gmPaths(wx=None, app_name='gnumed')
		print "user     config dir:", paths.user_config_dir
		print "system   config dir:", paths.system_config_dir
		print "local      base dir:", paths.local_base_dir
		print "system app data dir:", paths.system_app_data_dir
		print "working directory  :", paths.working_dir
		print "temp directory     :", paths.tmp_dir
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
		print get_unique_filename(tmp_dir='/home/ncq/Archiv/')
	#-----------------------------------------------------------------------
	def test_size2str():
		print "testing size2str()"
		print "------------------"
		tests = [0, 1, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000, 100000000000, 1000000000000, 10000000000000]
		for test in tests:
			print size2str(test)
	#-----------------------------------------------------------------------
	def test_unwrap():

		test = """
second line\n
	3rd starts with tab  \n
 4th with a space	\n

6th

"""
		print unwrap(text = test, max_length = 25)
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
	def test_md5():
		print '%s: %s' % (sys.argv[2], file2md5(sys.argv[2]))
	#-----------------------------------------------------------------------
	def test_unicode():
		print u_link_symbol * 10
	#-----------------------------------------------------------------------
	#test_coalesce()
	#test_capitalize()
	#test_import_module()
	#test_mkdir()
	#test_gmPaths()
	#test_none_if()
	#test_bool2str()
	#test_bool2subst()
	#test_get_unique_filename()
	#test_size2str()
	#test_wrap()
	#test_input2decimal()
	#test_input2int()
	#test_unwrap()
	#test_md5()
	test_unicode()

#===========================================================================
