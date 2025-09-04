# -*- coding: utf-8 -*-


"""GNUmed general tools."""

#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# std libs
import sys
import os
import os.path
import csv
import tempfile
import logging
import hashlib
import decimal
import getpass
import functools
import json
import shutil
import zipfile
import datetime as pydt
import re as regex
import xml.sax.saxutils as xml_tools
from typing import Any
from types import ModuleType
# old:
import pickle, zlib
# docutils
du_core = None


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
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


u_currency_pound = '\u00A3'				# Pound sign
u_currency_sign = '\u00A4'					# generic currency sign
u_currency_yen = '\u00A5'					# Yen sign
u_right_double_angle_quote = '\u00AB'		# <<
u_registered_trademark = '\u00AE'
u_plus_minus = '\u00B1'
u_superscript_one = '\u00B9'				# ^1
u_left_double_angle_quote = '\u00BB'		# >>
u_one_quarter = '\u00BC'
u_one_half = '\u00BD'
u_three_quarters = '\u00BE'
u_multiply = '\u00D7'						# x
u_greek_ALPHA = '\u0391'
u_greek_alpha = '\u03b1'
u_greek_OMEGA = '\u03A9'
u_greek_omega = '\u03c9'
u_dagger = '\u2020'
u_triangular_bullet = '\u2023'					# triangular bullet  (>)
u_ellipsis = '\u2026'							# ...
u_euro = '\u20AC'								# EURO sign
u_numero = '\u2116'								# No. / # sign
u_down_left_arrow = '\u21B5'					# <-'
u_left_arrow = '\u2190'							# <--
u_up_arrow = '\u2191'
u_arrow2right = '\u2192'						# -->
u_down_arrow = '\u2193'
u_left_arrow_with_tail = '\u21a2'				# <--<
u_arrow2right_from_bar = '\u21a6'				# |->
u_arrow2right_until_vertical_bar = '\u21e5'		# -->|
u_sum = '\u2211'								# sigma
u_almost_equal_to = '\u2248'					# approximately / nearly / roughly
u_corresponds_to = '\u2258'
u_infinity = '\u221E'
u_arrow2right_until_vertical_bar2 = '\u2b72'	# -->|

u_diameter = '\u2300'
u_checkmark_crossed_out = '\u237B'
u_box_horiz_high = '\u23ba'
u_box_vert_left = '\u23b8'
u_box_vert_right = '\u23b9'

u_space_as_open_box = '\u2423'

u_box_horiz_single = '\u2500'				# -
u_box_vert_light = '\u2502'
u_box_horiz_light_3dashes = '\u2504'		# ...
u_box_vert_light_4dashes = '\u2506'
u_box_horiz_4dashes = '\u2508'				# ....
u_box_T_right = '\u251c'					# |-
u_box_T_left = '\u2524'						# -|
u_box_T_down = '\u252c'
u_box_T_up = '\u2534'
u_box_plus = '\u253c'
u_box_top_double = '\u2550'
u_box_top_left_double_single = '\u2552'
u_box_top_right_double_single = '\u2555'
u_box_top_left_arc = '\u256d'
u_box_top_right_arc = '\u256e'
u_box_bottom_right_arc = '\u256f'
u_box_bottom_left_arc = '\u2570'
u_box_horiz_light_heavy = '\u257c'
u_box_horiz_heavy_light = '\u257e'

u_skull_and_crossbones = '\u2620'
u_caduceus = '\u2624'
u_frowning_face = '\u2639'
u_smiling_face = '\u263a'
u_black_heart = '\u2665'
u_female = '\u2640'
u_male = '\u2642'
u_male_female = '\u26a5'
u_chain = '\u26d3'

u_checkmark_thin = '\u2713'
u_checkmark_thick = '\u2714'
u_heavy_greek_cross = '\u271a'
u_arrow2right_thick = '\u2794'
u_writing_hand = '\u270d'
u_pencil_1 = '\u270e'
u_pencil_2 = '\u270f'
u_pencil_3 = '\u2710'
u_latin_cross = '\u271d'

u_arrow2right_until_black_diamond = '\u291e'	# ->*

u_kanji_yen = '\u5186'							# Yen kanji
u_replacement_character = '\ufffd'
u_padlock_closed = '\u1f512'
u_padlock_open = '\u1f513'
u_link_symbol = '\u1f517'

u_kidneys = '\u1fad8'							# beans :-)


_kB = 1024
_MB = 1024 * _kB
_GB = 1024 * _MB
_TB = 1024 * _GB
_PB = 1024 * _TB


_client_version = None


_GM_TITLE_PREFIX = 'GMd'
_GM_DIR_DESC_FILENAME_PREFIX = '.00-README.GNUmed'

#===========================================================================
def handle_uncaught_exception_console(t, v, tb):

	print(".========================================================")
	print("| Unhandled exception caught !")
	print("| Type :", t)
	print("| Value:", v)
	print("`========================================================")
	_log.critical('unhandled exception caught', exc_info = (t,v,tb))
	sys.__excepthook__(t,v,tb)

#===========================================================================
# path level operations
#---------------------------------------------------------------------------
def normalize_path(path:str) -> str:
	norm_path = os.path.normcase(os.path.abspath(os.path.expanduser(path)))
	_log.debug('%s -> %s', path, norm_path)
	return norm_path

#---------------------------------------------------------------------------
def mkdir(directory:str=None, mode=None) -> bool:
	"""Create directory.

	- creates parent dirs if necessary
	- does not fail if directory exists

	Args:
		mode: numeric, say 0o0700 for "-rwx------"

	Returns:
		True/False based on success
	"""
	if os.path.isdir(directory):
		if mode is None:
			return True

		changed = False
		old_umask = os.umask(0)
		try:
			# does not WORK !
			#os.chmod(directory, mode, follow_symlinks = (os.chmod in os.supports_follow_symlinks))	# can't do better
			os.chmod(directory, mode)
			changed = True
		finally:
			os.umask(old_umask)
		return changed

	if mode is None:
		os.makedirs(directory)
		return True

	old_umask = os.umask(0)
	try:
		os.makedirs(directory, mode)
	finally:
		os.umask(old_umask)
	return True

#---------------------------------------------------------------------------
def create_directory_description_file(directory:str=None, readme:str=None, suffix:str=None) -> bool:
	"""Create a directory description file.

		Returns:
			<False> if it cannot create the description file.
	"""
	assert (directory is not None), '<directory> must not be None'

	README_fname = _GM_DIR_DESC_FILENAME_PREFIX + coalesce(suffix, '.dir')
	README_path = os.path.abspath(os.path.expanduser(os.path.join(directory, README_fname)))
	_log.debug('%s', README_path)
	if readme is None:
		_log.debug('no README text, boilerplate only')
	try:
		README = open(README_path, mode = 'wt', encoding = 'utf8')
	except Exception:
		return False

	line = 'GNUmed v%s -- %s' % (_client_version, pydt.datetime.now().strftime('%c'))
	len_sep = len(line)
	README.write(line)
	README.write('\n')
	line = README_path
	len_sep = max(len_sep, len(line))
	README.write(line)
	README.write('\n')
	README.write('-' * len_sep)
	README.write('\n')
	README.write('\n')
	README.write(readme)
	README.write('\n')
	README.close()
	return True

#---------------------------------------------------------------------------
def rmdir(directory:str) -> int:
	"""Remove a directory _and_ its content.

	Returns:
		Count of items that were not removable. IOW, 0 = success.
	"""
	#-------------------------------
	def _on_rm_error(func, path, exc):
		_log.error('error while shutil.rmtree(%s)', path, exc_info=exc)
		return True

	#-------------------------------
	error_count = 0
	try:
		shutil.rmtree(directory, False, _on_rm_error)
	except Exception:
		_log.exception('cannot shutil.rmtree(%s)', directory)
		error_count += 1
	return error_count

#---------------------------------------------------------------------------
def rm_dir_content(directory:str) -> bool:
	"""Remove the content of _directory_.
	"""
	_log.debug('cleaning out [%s]', directory)
	try:
		items = os.listdir(directory)
	except OSError:
		return False

	for item in items:
		# attempt file/link removal and ignore (but log) errors
		full_item = os.path.join(directory, item)
		try:
			os.remove(full_item)
		except OSError:		# as per the docs, this is a directory
			_log.debug('[%s] seems to be a subdirectory', full_item)
			errors = rmdir(full_item)
			if errors > 0:
				return False

		except Exception:
			_log.exception('cannot os.remove(%s) [a file or a link]', full_item)
			return False

	return True

#---------------------------------------------------------------------------
def mk_sandbox_dir(prefix:str=None, base_dir:str=None) -> str:
	"""Create a sandbox directory.

	Args:
		prefix: use this prefix to the directory name
		base_dir: create sandbox inside this directory, or else in the temp dir

	Returns:
		The newly created sandbox directory.
	"""
	if base_dir is None:
		base_dir = gmPaths().tmp_dir
	else:
		if not os.path.isdir(base_dir):
			mkdir(base_dir, mode = 0o0700)	# (invoking user only)
	if prefix is None:
		prefix = 'sndbx-'
	return tempfile.mkdtemp(prefix = prefix, suffix = '', dir = base_dir)

#---------------------------------------------------------------------------
def parent_dir(directory:str) -> str:
	"""/tmp/path/subdir/ -> /tmp/path/"""
	return os.path.abspath(os.path.join(directory, '..'))

#---------------------------------------------------------------------------
def dirname_stem(directory:str) -> str:
	"""Return stem of leaf directory name.

	- /home/user/dir/ -> dir
	- /home/user/dir  -> dir
	"""
	# normpath removes trailing slashes if any
	return os.path.basename(os.path.normpath(directory))

#---------------------------------------------------------------------------
def dir_is_empty(directory:str=None) -> bool:
	"""Check for any entries inside _directory_.

	Returns:
		True / False / None (directory not found)
	"""
	try:
		empty = (len(os.listdir(directory)) == 0)
	except OSError as exc:
		if exc.errno != 2:	# no such file
			raise
		empty = None
	return empty

#---------------------------------------------------------------------------
def dir_list_files(directory:str=None, exclude_subdirs:bool=True) -> list[str]:
	try:
		all_dir_items = os.listdir(directory)
	except OSError:
		_log.exception('cannot list dir [%s]', directory)
		return None

	filenames2return = []
	for item in all_dir_items:
		item = os.path.join(directory, item)
		if os.path.isdir(item):
			if exclude_subdirs:
				continue
		filenames2return.append(item)
	return filenames2return

#---------------------------------------------------------------------------
def copy_tree_content(directory:str, target_directory:str) -> str:
	"""Copy the *content* of _directory_ into _target_directory_.

	The target directory is created if need be.

	Returns:
		The target directory or None on error.
	"""
	assert (directory is not None), 'source <directory> must not be None'
	assert (target_directory is not None), '<target_directory> must not be None'
	_log.debug('copying content of [%s] into [%s]', directory, target_directory)
	try:
		base_dir_items = os.listdir(directory)
	except OSError:
		_log.exception('cannot list dir [%s]', directory)
		return None

	for item in base_dir_items:
		full_item = os.path.join(directory, item)
		if os.path.isdir(full_item):
			target_subdir = os.path.join(target_directory, item)
			try:
				shutil.copytree(full_item, target_subdir)
				continue
			except Exception:
				_log.exception('cannot copy subdir [%s]', full_item)
				return None

		try:
			shutil.copy2(full_item, target_directory)
		except Exception:
			_log.exception('cannot copy file [%s]', full_item)
			return None

	return target_directory

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class gmPaths(gmBorg.cBorg):
	"""Singleton class providing standard paths.

	Consider using "platformdirs" from pypi.

	- .home_dir: user home

	- .local_base_dir: script installation dir

	- .working_dir: current dir

	- .user_config_dir, in the following order:
		- ~/.config/gnumed/
		- ~/

	- .user_appdata_dir, in the following order:
		- ~/.local/gnumed/
		- ~/

	- .system_config_dir

	- .system_app_data_dir

	- .tmp_dir: instance-local

	- .user_tmp_dir: user-local (NOT per instance)

	- .bytea_cache_dir: caches downloaded BYTEA data

	- .user_work_dir: app specific user work dir, say, ~/gnumed/

	It will take into account the application name.
	"""
	def __init__(self, app_name:str=None, wx:ModuleType=None):
		"""Setup paths.

		Args:
			app_name: name of application, default "name of main script without .py"
			wx: wxPython module reference, optional, used to detect more standard paths
		"""
		if hasattr(self, 'already_inited'):
			if not wx:
				return
			if self.__wx:
				return

		self.__wx:ModuleType = wx
		self.init_paths(app_name = app_name)
		self.already_inited:bool = True

	#--------------------------------------
	# public API
	#--------------------------------------
	def init_paths(self, app_name:str=None, wx=None) -> bool:
		"""Detect paths in the system.

		Args:
			app_name: name of application, default "name of main script without .py"
			wx: wxPython module reference, optional, used to better detect standard paths
		"""
		if not self.__wx:
			self.__wx = wx
		if not self.__wx:
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
		if getattr(sys, 'frozen', False):
			_log.info('frozen app, installed into temporary path')
			# this would find the path of *THIS* file
			#self.local_base_dir = os.path.dirname(__file__)
			# while this is documented on the web, the ${_MEIPASS2} does not exist
			#self.local_base_dir = os.environ.get('_MEIPASS2')
			# this is what Martin Zibricky <mzibr.public@gmail.com> told us to use
			# when asking about this on pyinstaller@googlegroups.com
			#self.local_base_dir = sys._MEIPASS
			# however, we are --onedir, so we should look at sys.executable
			# as per the pyinstaller manual
			self.local_base_dir = os.path.dirname(sys.executable)
		else:
			self.local_base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

		# the current working dir at the OS
		self.working_dir = os.path.abspath(os.curdir)

		# user-specific config dir, usually below the home dir, default to $XDG_CONFIG_HOME
		_dir = os.path.join(self.home_dir, '.config', app_name)
		if not mkdir(_dir):
			_log.error('cannot make config dir [%s], falling back to home dir', _dir)
			_dir = self.home_dir
		self.user_config_dir = _dir

		# user-specific app dir, usually below the home dir
		mkdir(os.path.join(self.home_dir, app_name))
		self.user_work_dir = os.path.join(self.home_dir, app_name)

		# user-specific app data/state dir, usually below home dir
		_dir = os.path.join(self.home_dir, '.local', app_name)
		if not mkdir(_dir):
			_log.error('cannot make data/state dir [%s], falling back to home dir', _dir)
			_dir = self.home_dir
		self.user_appdata_dir = _dir

		# system-wide config dir, under UN*X usually below /etc/
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
			_log.info('temp file prefix: %s', tempfile.gettempprefix())
			_log.info('initial (user level) temp dir: %s', tempfile.gettempdir())
			bytes_free = shutil.disk_usage(tempfile.gettempdir()).free
			_log.info('free disk space for temp dir: %s (%s bytes)', size2str(size = bytes_free), bytes_free)
			# $TMP/gnumed-$USER/
			self.user_tmp_dir = os.path.join(tempfile.gettempdir(), '%s-%s' % (app_name, getpass.getuser()))
			mkdir(self.user_tmp_dir, 0o700)
			_log.info('intermediate (app+user level) temp dir: %s', self.user_tmp_dir)
			# $TMP/gnumed-$USER/g-$UNIQUE/
			tempfile.tempdir = self.user_tmp_dir # tell mkdtemp about intermediate dir
			self.tmp_dir = tempfile.mkdtemp(prefix = 'g-') # will set tempfile.tempdir as side effect
			_log.info('final (app instance level) temp dir: %s', tempfile.gettempdir())
		create_directory_description_file(directory = self.tmp_dir, readme = 'client instance tmp dir')

		# BYTEA cache dir
		cache_dir = os.path.join(self.user_tmp_dir, '.bytea_cache')
		try:
			stat = os.stat(cache_dir)
			_log.warning('reusing BYTEA cache dir: %s', cache_dir)
			_log.debug(stat)
		except FileNotFoundError:
			mkdir(cache_dir, mode = 0o0700)
		self.bytea_cache_dir = cache_dir
		create_directory_description_file(directory = self.bytea_cache_dir, readme = 'cache dir for BYTEA data')

		self.__log_paths()
		if not self.__wx:
			return True

		# retry with wxPython
		_log.debug('re-detecting paths with wxPython')
		std_paths = self.__wx.StandardPaths.Get()
		_log.info('wxPython app name is [%s]', self.__wx.GetApp().GetAppName())

		# user-specific config dir, usually below the home dir
		_dir = std_paths.UserConfigDir
		if _dir == self.home_dir:
			_dir = os.path.join(self.home_dir, '.config', app_name)
		else:
			_dir = os.path.join(_dir, '.%s' % app_name)
		if not mkdir(_dir):
			_log.error('cannot make config dir [%s], falling back to home dir', _dir)
			_dir = self.home_dir
		self.user_config_dir = _dir

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
		if 'wxMSW' in self.__wx.PlatformInfo:
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
		_log.debug('sys.executable: %s', sys.executable)
		_log.debug('sys._MEIPASS: %s', getattr(sys, '_MEIPASS', '<not found>'))
		_log.debug('os.environ["_MEIPASS2"]: %s', os.environ.get('_MEIPASS2', '<not found>'))
		_log.debug('__file__ : %s', __file__)
		_log.debug('local application base dir: %s', self.local_base_dir)
		_log.debug('current working dir: %s', self.working_dir)
		_log.debug('user home dir: %s', self.home_dir)
		_log.debug('user-specific config dir: %s', self.user_config_dir)
		_log.debug('user-specific application data dir: %s', self.user_appdata_dir)
		_log.debug('system-wide config dir: %s', self.system_config_dir)
		_log.debug('system-wide application data dir: %s', self.system_app_data_dir)
		_log.debug('temporary dir (user): %s', self.user_tmp_dir)
		_log.debug('temporary dir (instance): %s', self.tmp_dir)
		_log.debug('temporary dir (tempfile.tempdir): %s', tempfile.tempdir)
		_log.debug('temporary dir (tempfile.gettempdir()): %s', tempfile.gettempdir())
		_log.debug('BYTEA cache dir: %s', self.bytea_cache_dir)

	#--------------------------------------
	# properties
	#--------------------------------------
	def _set_user_config_dir(self, path):
		if not (os.access(path, os.R_OK) and os.access(path, os.X_OK)):
			msg = '[%s:user_config_dir]: unusable path [%s]' % (self.__class__.__name__, path)
			_log.error(msg)
			raise ValueError(msg)
		self.__user_config_dir = path

	def _get_user_config_dir(self):
		"""User-level application configuration data directory."""
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
		"""System-wide application configuration directory.

		Typically not writable.
		"""
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
		"""The system-wide application data directory.

		Typically not writable.
		"""
		return self.__system_app_data_dir

	system_app_data_dir = property(_get_system_app_data_dir, _set_system_app_data_dir)

	#--------------------------------------
	def _set_home_dir(self, path):
		raise ValueError('invalid to set home dir')

	def _get_home_dir(self):
		"""Home directory of OS user."""
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
		_log.debug('new temp dir: %s', tempfile.gettempdir())
		self.__tmp_dir_already_set = True

	def _get_tmp_dir(self):
		"""Temporary directory.

		- per instance of main script

		- _may_ be confined to the OS user
		"""
		return self.__tmp_dir

	tmp_dir = property(_get_tmp_dir, _set_tmp_dir)

#===========================================================================
# file related tools
#---------------------------------------------------------------------------
def recode_file(source_file=None, target_file=None, source_encoding='utf8', target_encoding=None, base_dir=None, error_mode='replace'):
	if target_encoding is None:
		return source_file

	if target_encoding == source_encoding:
		return source_file

	if target_file is None:
		target_file = get_unique_filename (
			prefix = '%s-%s_%s-' % (fname_stem(source_file), source_encoding, target_encoding),
			suffix = fname_extension(source_file, '.txt'),
			tmp_dir = base_dir
		)
	_log.debug('[%s] -> [%s] (%s -> %s)', source_encoding, target_encoding, source_file, target_file)
	in_file = open(source_file, mode = 'rt', encoding = source_encoding)
	out_file = open(target_file, mode = 'wt', encoding = target_encoding, errors = error_mode)
	for line in in_file:
		out_file.write(line)
	out_file.close()
	in_file.close()
	return target_file

#---------------------------------------------------------------------------
def unzip_archive(archive_name, target_dir=None, remove_archive=False):
	_log.debug('unzipping [%s] -> [%s]', archive_name, target_dir)
	success = False
	try:
		with zipfile.ZipFile(archive_name) as archive:
			archive.extractall(target_dir)
		success = True
	except Exception:
		_log.exception('cannot unzip')
		return False
	if remove_archive:
		remove_file(archive_name)
	return success

#---------------------------------------------------------------------------
def remove_file(filename:str, log_error:bool=True, force:bool=False) -> bool:
	"""Remove a file.

	Args:
		filename: file to remove
		force: if remove does not work attempt to rename the file

	Returns:
		True/False: Removed or not.
	"""
	if not os.path.lexists(filename):
		return True

	# attempt file removal and ignore (but log) errors
	try:
		os.remove(filename)
		return True

	except Exception:
		if log_error:
			_log.exception('cannot os.remove(%s)', filename)
	if not force:
		return False

	tmp_name = get_unique_filename(tmp_dir = fname_dir(filename))
	_log.debug('attempting os.replace(%s -> %s)', filename, tmp_name)
	try:
		os.replace(filename, tmp_name)
		return True

	except Exception:
		if log_error:
			_log.exception('cannot os.replace(%s)', filename)
	return False

#---------------------------------------------------------------------------
def rename_file(filename:str, new_filename:str, overwrite:bool=False, allow_symlink:bool=False, allow_hardlink:bool=True) -> bool:
	"""Rename a file.

	Args:
		filename: source filename
		new_filename: target filename
		overwrite: overwrite existing target ?
		allow_symlink: allow soft links ?
		allow_hardlink: allow hard links ?

	Returns:
		True/False: Renamed or not.
	"""
	_log.debug('renaming: [%s] -> [%s]', filename, new_filename)
	if filename == new_filename:
		_log.debug('no copy onto self')
		return True

	if not os.path.lexists(filename):
		_log.error('source does not exist')
		return False

	if overwrite and not remove_file(new_filename, force = True):
		_log.error('cannot remove existing target')
		return False

	try:
		shutil.move(filename, new_filename)
		return True

	except OSError:
		_log.exception('shutil.move() failed')

	try:
		os.replace(filename, new_filename)
		return True

	except Exception:
		_log.exception('os.replace() failed')

	if allow_hardlink:
		try:
			os.link(filename, new_filename)
			return True

		except Exception:
			_log.exception('os.link() failed')

	if allow_symlink:
		try:
			os.symlink(filename, new_filename)
			return True

		except Exception:
			_log.exception('os.symlink() failed')

	return False

#---------------------------------------------------------------------------
def file2md5(filename:str=None, return_hex:bool=True):
	blocksize = 2**10 * 128			# 128k, since md5 uses 128 byte blocks
	_log.debug('md5(%s): <%s> byte blocks', filename, blocksize)
	f = open(filename, mode = 'rb')
	md5 = hashlib.md5()
	while True:
		data = f.read(blocksize)
		if not data:
			break
		md5.update(data)
	f.close()
	_log.debug('md5(%s): %s', filename, md5.hexdigest())
	if return_hex:
		return md5.hexdigest()

	return md5.digest()

#---------------------------------------------------------------------------
def file2chunked_md5(filename=None, chunk_size=500*_MB):
	_log.debug('chunked_md5(%s, chunk_size=%s bytes)', filename, chunk_size)
	md5_concat = ''
	f = open(filename, 'rb')
	while True:
		md5 = hashlib.md5()
		data = f.read(chunk_size)
		if not data:
			break
		md5.update(data)
		md5_concat += md5.hexdigest()
	f.close()
	md5 = hashlib.md5()
	md5.update(md5_concat)
	hex_digest = md5.hexdigest()
	_log.debug('md5("%s"): %s', md5_concat, hex_digest)
	return hex_digest

#---------------------------------------------------------------------------
default_csv_reader_rest_key = 'list_of_values_of_unknown_fields'

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, encoding='utf-8', **kwargs):
	try:
		is_dict_reader = kwargs['dict']
		del kwargs['dict']
	except KeyError:
		is_dict_reader = False

	if is_dict_reader:
		kwargs['restkey'] = default_csv_reader_rest_key
		return csv.DictReader(unicode_csv_data, dialect=dialect, **kwargs)
	return csv.reader(unicode_csv_data, dialect=dialect, **kwargs)




def old_unicode2charset_encoder(unicode_csv_data, encoding='utf-8'):
	for line in unicode_csv_data:
		yield line.encode(encoding)

#def utf_8_encoder(unicode_csv_data):
#	for line in unicode_csv_data:
#		yield line.encode('utf-8')

def old_unicode_csv_reader(unicode_csv_data, dialect=csv.excel, encoding='utf-8', **kwargs):

	# csv.py doesn't do Unicode; encode temporarily as UTF-8:
	try:
		is_dict_reader = kwargs['dict']
		del kwargs['dict']
		if is_dict_reader is not True:
			raise KeyError
		kwargs['restkey'] = default_csv_reader_rest_key
		csv_reader = csv.DictReader(old_unicode2charset_encoder(unicode_csv_data), dialect=dialect, **kwargs)
	except KeyError:
		is_dict_reader = False
		csv_reader = csv.reader(old_unicode2charset_encoder(unicode_csv_data), dialect=dialect, **kwargs)

	for row in csv_reader:
		# decode ENCODING back to Unicode, cell by cell:
		if is_dict_reader:
			for key in row:
				if key == default_csv_reader_rest_key:
					old_data = row[key]
					new_data = []
					for val in old_data:
						new_data.append(str(val, encoding))
					row[key] = new_data
					if default_csv_reader_rest_key not in csv_reader.fieldnames:
						csv_reader.fieldnames.append(default_csv_reader_rest_key)
				else:
					row[key] = str(row[key], encoding)
			yield row
		else:
			yield [ str(cell, encoding) for cell in row ]
			#yield [str(cell, 'utf-8') for cell in row]

#---------------------------------------------------------------------------
def fname_sanitize(filename:str) -> str:
	"""Normalizes unicode, removes non-alpha characters, converts spaces to underscores."""

	dir_part, name_part = os.path.split(filename)
	if name_part == '':
		return filename

	import unicodedata
	name_part = unicodedata.normalize('NFKD', name_part)
	# remove everything not in group []
	name_part = regex.sub (
		r'[^.\w\s[\]()%§#+-]',
		'',
		name_part,
		flags = regex.UNICODE
	).strip()
	# translate whitespace to underscore
	name_part = regex.sub (
		r'\s+',
		'_',
		name_part,
		flags = regex.UNICODE
	)
	return os.path.join(dir_part, name_part)

#---------------------------------------------------------------------------
def fname_stem(filename:str) -> str:
	"""/home/user/dir/filename.ext -> filename"""
	return os.path.splitext(os.path.basename(filename))[0]

#---------------------------------------------------------------------------
def fname_stem_with_path(filename:str) -> str:
	"""/home/user/dir/filename.ext -> /home/user/dir/filename"""
	return os.path.splitext(filename)[0]

#---------------------------------------------------------------------------
def fname_extension(filename:str=None, fallback:str=None) -> str:
	"""	/home/user/dir/filename.ext -> .ext

	If extension becomes '' or '.' -> return fallback if any else return ''.

	Args:
		fallback: Return this if extension computes to '.' or '' (IOW, is empty)
	"""
	ext = os.path.splitext(filename)[1]
	if ext.strip() not in ['.', '']:
		return ext
	if fallback is None:
		return ''
	return fallback

#---------------------------------------------------------------------------
def fname_dir(filename:str) -> str:
	"""/home/user/dir/filename.ext -> /home/user/dir"""
	return os.path.split(filename)[0]

#---------------------------------------------------------------------------
def fname_from_path(filename):
	"""/home/user/dir/filename.ext -> filename.ext"""
	return os.path.split(filename)[1]

#---------------------------------------------------------------------------
def get_unique_filename(prefix:str=None, suffix:str=None, tmp_dir:str=None, include_timestamp:bool=False) -> str:
	"""Generate a unique filename.

	Args:
		prefix: use this prefix to the filename, default 'gm-', '' means "no prefix"
		suffix: use this suffix to the filename, default '.tmp'
		tmp_dir: generate filename based suitable for this directory, default system tmpdir
		include_timestamp: include current timestamp within the filename

	Returns:
		The full path of a unique file not existing at this moment.

	There is a TOCTOU race conditition between generating the
	filename here and actually using the filename in callers.

	Note: The file will NOT exist after calling this function.
	"""
	if tmp_dir is None:
		gmPaths()		# setup tmp dir if necessary
	else:
		if (
			not os.access(tmp_dir, os.F_OK)
				or
			not os.access(tmp_dir, os.X_OK | os.W_OK)
		):
			_log.warning('cannot os.access() temporary dir [%s], using system default', tmp_dir)
			tmp_dir = None

	if include_timestamp:
		ts = pydt.datetime.now().strftime('%m%d-%H%M%S-')
	else:
		ts = ''
	kwargs:dict[str, Any] = {
		'dir': tmp_dir,
		#  make sure file gets deleted as soon as it is
		# .close()d so we can "safely" open it again
		'delete': True
	}
	if prefix is None:
		kwargs['prefix'] = 'gm-%s' % ts
	else:
		kwargs['prefix'] = prefix + ts
	if suffix in [None, '']:
		kwargs['suffix'] = '.tmp'
	else:
		if not suffix.startswith('.'):
			suffix = '.' + suffix
		kwargs['suffix'] = suffix
	f = tempfile.NamedTemporaryFile(**kwargs)
	filename = f.name
	f.close()

	return filename

#---------------------------------------------------------------------------
def __make_symlink_on_windows(physical_name, link_name):
	import ctypes
	#windows_create_symlink = ctypes.windll.kernel32.CreateSymbolicLinkW
	kernel32 = ctypes.WinDLL('kernel32', use_last_error = True)
	windows_create_symlink = kernel32.CreateSymbolicLinkW
	windows_create_symlink.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
	windows_create_symlink.restype = ctypes.c_ubyte
	if os.path.isdir(physical_name):
		flags = 1
	else:
		flags = 0
	ret_code = windows_create_symlink(link_name, physical_name.replace('/', '\\'), flags)
	_log.debug('ctypes.windll.kernel32.CreateSymbolicLinkW() [%s] exit code: %s', windows_create_symlink, ret_code)
	if ret_code == 0:
		raise ctypes.WinError()
	return ret_code

#---------------------------------------------------------------------------
def mklink(physical_name:str, link_name:str, overwrite:bool=False) -> bool:
	"""Create a symbolic link.

	Args:
		physical_name: the pre-existing filesystem object the symlink is to point to
		link_name: the name of the symlink pointing to the existing filesystem object
	"""
	_log.debug('creating symlink (overwrite = %s):', overwrite)
	_log.debug('link [%s] =>', link_name)
	_log.debug('=> physical [%s]', physical_name)

	if os.path.exists(link_name):
		_log.debug('link exists')
		if overwrite:
			return True			# unsafe :/
		return False

	try:
		os.symlink(physical_name, link_name)
	except (AttributeError, NotImplementedError):
		_log.debug('this Python does not have os.symlink(), trying via ctypes')
		__make_symlink_on_windows(physical_name, link_name)
	except PermissionError:
		_log.exception('cannot create link')
		return False
	#except OSError:
	#	unprivileged on Windows
	return True

#===========================================================================
def import_module_from_directory(module_path=None, module_name=None, always_remove_path=False):
	"""Import a module from any location."""

	_log.debug('CWD: %s', os.getcwd())
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
	except Exception:
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
def empty_str(text:str) -> bool:
	"""Check "text" for emptiness.

	Returns:

	* True: None, '', '\w*'
	* False: ' anything else 1234'
	"""
	if text: return False
	# could still be '\w+'
	if text.strip(): return False
	return True

#---------------------------------------------------------------------------
def size2str(size=0, template='%s'):
	if size == 1:
		return template % _('1 Byte')
	if size < 10 * _kB:
		return template % _('%s Bytes') % size
	if size < _MB:
		return template % '%.1f kB' % (float(size) / _kB)
	if size < _GB:
		return template % '%.1f MB' % (float(size) / _MB)
	if size < _TB:
		return template % '%.1f GB' % (float(size) / _GB)
	if size < _PB:
		return template % '%.1f TB' % (float(size) / _TB)
	return template % '%.1f PB' % (float(size) / _PB)

#---------------------------------------------------------------------------
def bool2subst(boolean=None, true_return=True, false_return=False, none_return=None):
	if boolean is None:
		return none_return
	if boolean:
		return true_return
	if not boolean:
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
def xor(val1, val2, mutually_exclusive_values:list=None, check_defined:bool=False) -> bool:
	"""Test values for not BOTH being in list of mutually exclusive values.

	This can be used to assert mutually exclusive function
	inputs (say, a patient name and a patient PK for a search
	function).

	Args:
		val1: value to check
		val2: value to check
		mutually_exclusive_values: in which *either* one *or* the other value must not be contained

	Returns:
		True if only one of the values is defined.
		False if both values are undefined or defined.
	"""
	if mutually_exclusive_values is None:
		mutually_exclusive_values = [None]
	if (val1 in mutually_exclusive_values) and (val2 in mutually_exclusive_values):
		return False

	if (val1 not in mutually_exclusive_values) and (val2 not in mutually_exclusive_values):
		return False

	return True

#---------------------------------------------------------------------------
def none_if(value=None, none_equivalent=None, strip_string=False):
	"""Modelled after the SQL NULLIF function.

	Args:
		value: the value to test for "none"-likeness
		none_equivalent: values to be considered eqivalent to "none"
		strip_string: apply .strip() to value
	"""
	if value is None:
		return None

	if strip_string:
		stripped = value.strip()
	else:
		stripped = value
	if stripped == none_equivalent:
		return None

	#return value
	return stripped

#---------------------------------------------------------------------------
def coalesce(value2test=None, return_instead=None, template4value=None, template4instead=None, none_equivalents=None, function4value=None, value2return=None):
	"""Modelled after the SQL coalesce function.

	To be used to simplify constructs like:

		if value2test is None (or in none_equivalents):
			value = (template4instead % return_instead) or return_instead
		else:
			value = (template4value % value2test) or value2test
		print(value)

	Args:
		value2test: the value to be tested for _None_
		return_instead: the value to be returned if _value2test_ *is* None
		template4value: if _value2test_ is returned, substitute the value into this template (which must contain one '%s')
		template4instead: if "return_instead" is returned, substitute the instead-value into this template (which must contain one <%s>)
		function4value: a tuple of (function name, function arguments) to call on _value2test_, eg "function4value = ('strftime', '%Y-%m-%d')"
		value2return: a *value* to return if _value2test_ is NOT None, AND there's no _template4value_

	Ideas:
		- list of return_insteads: initial, [return_instead, template], [return_instead, template], [return_instead, template], template4value, ...
	"""
	if none_equivalents is None:
		none_equivalents = [None]

	if value2test in none_equivalents:
		if template4instead is None:
			return return_instead
		return template4instead % return_instead

	# at this point, value2test was not equivalent to None

	# 1) explicit value to return supplied ?
	if value2return is not None:
		return value2return

	value2return = value2test
	# 2) function supplied to be applied to the value ?
	if function4value is not None:
		funcname, args = function4value
		func = getattr(value2test, funcname)
		value2return = func(args)

	# 3) template supplied to be applied to the value ?
	if template4value is None:
		return value2return

	try:
		return template4value % value2return
	except TypeError:
#	except (TypeError, ValueError):
		# this should go, actually, only needed because "old" calls
		# to coalesce will still abuse template4value as explicit value2return,
		# relying on the replacement to above to fail
		if hasattr(_log, 'log_stack_trace'):
			_log.log_stack_trace(message = 'deprecated use of <template4value> for <value2return>')
		else:
			_log.error('deprecated use of <template4value> for <value2return>')
			_log.error(locals())
		return template4value

#---------------------------------------------------------------------------
def __cap_name(match_obj=None):
	val = match_obj.group(0).casefold()
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

	if len(text) == 0:
		return text

	if mode == CAPS_FIRST:
		if len(text) == 1:
			return text[0].upper()
		return text[0].upper() + text[1:]

	if mode == CAPS_ALLCAPS:
		return text.upper()

	if mode == CAPS_FIRST_ONLY:
#		if len(text) == 1:
#			return text[0].upper()
		return text[0].upper() + text[1:].casefold()

	if mode == CAPS_WORDS:
		#return regex.sub(ur'(\w)(\w+)', lambda x: x.group(1).upper() + x.group(2).casefold(), text)
		return regex.sub(r'(\w)(\w+)', lambda x: x.group(1).upper() + x.group(2).casefold(), text)

	if mode == CAPS_NAMES:
		#return regex.sub(r'\w+', __cap_name, text)
		return capitalize(text=text, mode=CAPS_FIRST)		# until fixed

	print("ERROR: invalid capitalization mode: [%s], leaving input as is" % mode)
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
	if isinstance(val, str):
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
	if isinstance(val, str):
		val = val.replace(',', '.', 1)
		val = val.strip()

	try:
		int_val = int(val)
	except (TypeError, ValueError):
		_log.exception('int(%s) failed', val)
		return False, initial

	if minval is not None:
		if int_val < minval:
			_log.debug('%s < min (%s)', val, minval)
			return False, initial
	if maxval is not None:
		if int_val > maxval:
			_log.debug('%s > max (%s)', val, maxval)
			return False, initial

	return True, int_val

#---------------------------------------------------------------------------
def strip_prefix(text, prefix, remove_repeats=False, remove_whitespace=False):
	if remove_whitespace:
		text = text.lstrip()
	if not text.startswith(prefix):
		return text

	text = text.replace(prefix, '', 1)
	if not remove_repeats:
		if remove_whitespace:
			return text.lstrip()
		return text

	return strip_prefix(text, prefix, remove_repeats = True, remove_whitespace = remove_whitespace)

#---------------------------------------------------------------------------
def strip_suffix(text, suffix, remove_repeats=False, remove_whitespace=False):
	suffix_len = len(suffix)
	if remove_repeats:
		if remove_whitespace:
			while text.rstrip().endswith(suffix):
				text = text.rstrip()[:-suffix_len].rstrip()
			return text
		while text.endswith(suffix):
			text = text[:-suffix_len]
		return text
	if remove_whitespace:
		return text.rstrip()[:-suffix_len].rstrip()
	return text[:-suffix_len]

#---------------------------------------------------------------------------
def strip_leading_empty_lines(lines=None, text=None, eol='\n', return_list=True):
	if lines is None:
		lines = text.split(eol)

	while True:
		if lines[0].strip(eol).strip() != '':
			break
		lines = lines[1:]

	if return_list:
		return lines

	return eol.join(lines)

#---------------------------------------------------------------------------
def strip_trailing_empty_lines(lines=None, text=None, eol='\n', return_list=True):
	if lines is None:
		lines = text.split(eol)

	while True:
		if lines[-1].strip(eol).strip() != '':
			break
		lines = lines[:-1]

	if return_list:
		return lines

	return eol.join(lines)

#---------------------------------------------------------------------------
def strip_empty_lines(lines=None, text=None, eol='\n', return_list=True):
	return strip_trailing_empty_lines (
		lines = strip_leading_empty_lines(lines = lines, text = text, eol = eol, return_list = True),
		text = None,
		eol = eol,
		return_list = return_list
	)

#---------------------------------------------------------------------------
def list2text(lines, initial_indent='', subsequent_indent='', eol='\n', strip_leading_empty_lines=True, strip_trailing_empty_lines=True, strip_trailing_whitespace=True, max_line_width=None):

	if len(lines) == 0:
		return ''

	if strip_leading_empty_lines:
		lines = strip_leading_empty_lines(lines = lines, eol = eol, return_list = True)

	if strip_trailing_empty_lines:
		lines = strip_trailing_empty_lines(lines = lines, eol = eol, return_list = True)

	if strip_trailing_whitespace:
		lines = [ l.rstrip() for l in lines ]

	if max_line_width is not None:
		wrapped_lines = []
		for l in lines:
			wrapped_lines.extend(wrap(l, max_line_width).split('\n'))
		lines = wrapped_lines

	indented_lines = [initial_indent + lines[0]]
	indented_lines.extend([ subsequent_indent + l for l in lines[1:] ])

	return eol.join(indented_lines)

#---------------------------------------------------------------------------
def wrap(text=None, width=None, initial_indent='', subsequent_indent='', eol='\n'):
	"""A word-wrap function that preserves existing line breaks
	and most spaces in the text. Expects that existing line
	breaks are posix newlines (\n).
	"""
	if width is None:
		return text

	wrapped = initial_indent + functools.reduce (
		lambda line, word, width=width: '%s%s%s' % (
			line,
			' \n'[(len(line) - line.rfind('\n') - 1 + len(word.split('\n',1)[0]) >= width)],
			word
		),
		text.split(' ')
	)
	if subsequent_indent != '':
		wrapped = ('\n%s' % subsequent_indent).join(wrapped.split('\n'))
	if eol != '\n':
		wrapped = wrapped.replace('\n', eol)
	return wrapped

#---------------------------------------------------------------------------
def unwrap(text=None, max_length=None, strip_whitespace=True, remove_empty_lines=True, line_separator = ' // '):

	text = text.replace('\r', '')
	lines = text.split('\n')
	text = ''
	for line in lines:

		if strip_whitespace:
			line = line.strip().strip('\t').strip()

		if remove_empty_lines:
			if line == '':
				continue

		text += ('%s%s' % (line, line_separator))

	text = text.rstrip(line_separator)

	if max_length is not None:
		text = text[:max_length]

	text = text.rstrip(line_separator)

	return text

#---------------------------------------------------------------------------
def shorten_text(text:str=None, max_length:int=None, ellipsis:str=u_ellipsis) -> str:
	"""Shorten <text> to <max_length>-1 and append <ellipsis>."""
	if not max_length:
		return text

	if len(text) <= max_length:
		return text

	return text[:max_length-1] + ellipsis

#---------------------------------------------------------------------------
def shorten_words_in_line(text:str=None, max_length:int=None, min_word_length:int=3, ignore_numbers:bool=True, ellipsis:str=u_ellipsis) -> str:
	if text is None:
		return None

	if not max_length:
		return text

	if len(text) <= max_length:
		return text

	old_words = regex.split(r'\s+', text, flags = regex.UNICODE)
	nbr_old_words = len(old_words)
	max_word_length = max(min_word_length, (max_length // nbr_old_words))
	new_words = []
	for word in old_words:
		if len(word) <= max_word_length:
			new_words.append(word)
			continue
		if ignore_numbers:
			tmp = word.replace('-', '').replace('+', '').replace('.', '').replace(',', '').replace('/', '').replace('&', '').replace('*', '')
			if tmp.isdigit():
				new_words.append(word)
				continue
		new_words.append(word[:max_word_length] + ellipsis)
	return ' '.join(new_words)

#---------------------------------------------------------------------------
def xml_escape_string(text=None):
	"""check for special XML characters and transform them"""
	return xml_tools.escape(text)

#---------------------------------------------------------------------------
def tex_escape_string(text:str=None, replace_known_unicode:bool=True, replace_eol:bool=False, keep_visual_eol:bool=False, strip_whitespace:bool=True) -> str:
	"""Check for special TeX characters and transform them.

	Args:
		text: plain (unicode) text to escape for LaTeX processing,
			note that any valid LaTeX code contained within will be
			escaped, too
		replace_eol: replaces "\n" with "\\newline{}"
		keep_visual_eol: replaces "\n" with "\\newline{}%\n" such that
			both LaTeX will know to place a line break
			at this point as well as the visual formatting
			is preserved in the LaTeX source (think multi-
			row table cells)
		strip_whitespace: whether to remove surrounding whitespace

	Returns:
		A hopefully properly escaped string palatable to LaTeX.
	"""
	# must happen first
	text = text.replace('{', '-----{{{{{-----')
	text = text.replace('}', '-----}}}}}-----')

	text = text.replace('\\', '\\textbackslash{}')			# requires \usepackage{textcomp} in LaTeX source

	text = text.replace('-----{{{{{-----', '\\{{}')
	text = text.replace('-----}}}}}-----', '\\}{}')

	text = text.replace('^', '\\textasciicircum{}')
	text = text.replace('~', '\\textasciitilde{}')

	text = text.replace('%', '\\%{}')
	text = text.replace('&', '\\&{}')
	text = text.replace('#', '\\#{}')
	text = text.replace('$', '\\${}')
	text = text.replace('_', '\\_{}')
	if replace_eol:
		if keep_visual_eol:
			text = text.replace('\n', '\\newline{}%\n')
		else:
			text = text.replace('\n', '\\newline{}')

	if replace_known_unicode:
		# this should NOT be replaced for Xe(La)Tex
		text = text.replace(u_euro, '\\euro{}')		# requires \usepackage[official]{eurosym} in LaTeX source
		text = text.replace(u_sum, '$\\Sigma$')

	if strip_whitespace:
		return text.strip()

	return text

#---------------------------------------------------------------------------
def rst2latex_snippet(rst_text):
	global du_core
	if du_core is None:
		try:
			from docutils import core as du_core
		except ImportError:
			_log.warning('cannot turn ReST into LaTeX: docutils not installed')
			return tex_escape_string(text = rst_text)

	parts = du_core.publish_parts (
		source = rst_text.replace('\\', '\\\\'),
		source_path = '<internal>',
		writer_name = 'latex',
		#destination_path = '/path/to/LaTeX-template/for/calculating/relative/links/template.tex',
		settings_overrides = {
			'input_encoding': 'unicode'		# un-encoded unicode
		},
		enable_exit_status = True			# how to use ?
	)
	return parts['body']

#---------------------------------------------------------------------------
def rst2html(rst_text, replace_eol=False, keep_visual_eol=False):
	global du_core
	if du_core is None:
		try:
			from docutils import core as du_core
		except ImportError:
			_log.warning('cannot turn ReST into HTML: docutils not installed')
			return html_escape_string(text = rst_text, replace_eol=False, keep_visual_eol=False)

	parts = du_core.publish_parts (
		source = rst_text.replace('\\', '\\\\'),
		source_path = '<internal>',
		writer_name = 'latex',
		#destination_path = '/path/to/LaTeX-template/for/calculating/relative/links/template.tex',
		settings_overrides = {
			'input_encoding': 'unicode'		# un-encoded unicode
		},
		enable_exit_status = True			# how to use ?
	)
	return parts['body']

#---------------------------------------------------------------------------
def xetex_escape_string(text=None):
	# a web search did not reveal anything else for Xe(La)Tex
	# as opposed to LaTeX, except true unicode chars
	return tex_escape_string(text = text, replace_known_unicode = False)

#---------------------------------------------------------------------------
__html_escape_table = {
	"&": "&amp;",
	'"': "&quot;",
	"'": "&apos;",
	">": "&gt;",
	"<": "&lt;",
}

def html_escape_string(text=None, replace_eol=False, keep_visual_eol=False):
	text = ''.join(__html_escape_table.get(char, char) for char in text)
	if replace_eol:
		if keep_visual_eol:
			text = text.replace('\n', '<br>\n')
		else:
			text = text.replace('\n', '<br>')
	return text

#---------------------------------------------------------------------------
def dict2json(obj):
	return json.dumps(obj, default = json_serialize)

#---------------------------------------------------------------------------
def json_serialize(obj):
	if isinstance(obj, pydt.datetime):
		return obj.isoformat()
	raise TypeError('cannot json_serialize(%s)' % type(obj))

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
def compare_dict_likes(d1, d2, title1=None, title2=None):
	_log.info('comparing dict-likes: %s[%s] vs %s[%s]', coalesce(title1, '', '"%s" '), type(d1), coalesce(title2, '', '"%s" '), type(d2))
	try:
		d1 = dict(d1)
	except TypeError:
		pass
	try:
		d2 = dict(d2)
	except TypeError:
		pass
	keys_d1 = list(d1)
	keys_d2 = list(d2)
	different = False
	if len(keys_d1) != len(keys_d2):
		_log.info('different number of keys: %s vs %s', len(keys_d1), len(keys_d2))
		different = True
	for key in keys_d1:
		if key in keys_d2:
			if type(d1[key]) != type(d2[key]):
				_log.info('%25.25s: type(dict1) = %s = >>>%s<<<' % (key, type(d1[key]), d1[key]))
				_log.info('%25.25s  type(dict2) = %s = >>>%s<<<' % ('', type(d2[key]), d2[key]))
				different = True
				continue
			if d1[key] == d2[key]:
				_log.info('%25.25s:  both = >>>%s<<<' % (key, d1[key]))
			else:
				_log.info('%25.25s: dict1 = >>>%s<<<' % (key, d1[key]))
				_log.info('%25.25s  dict2 = >>>%s<<<' % ('', d2[key]))
				different = True
		else:
			_log.info('%25.25s: %50.50s | <MISSING>' % (key, '>>>%s<<<' % d1[key]))
			different = True
	for key in keys_d2:
		if key in keys_d1:
			continue
		_log.info('%25.25s: %50.50s | %.50s' % (key, '<MISSING>', '>>>%s<<<' % d2[key]))
		different = True
	if different:
		_log.warning('dict-likes appear to be different from each other')
		return False

	_log.info('dict-likes appear equal to each other')
	return True

#---------------------------------------------------------------------------
def format_dict_likes_comparison(d1, d2, title_left=None, title_right=None, left_margin=0, key_delim=' || ', data_delim=' | ', missing_string='=/=', difference_indicator='! ', ignore_diff_in_keys=None):

	_log.info('comparing dict-likes: %s[%s] vs %s[%s]', coalesce(title_left, '', '"%s" '), type(d1), coalesce(title_right, '', '"%s" '), type(d2))
	append_type = False
	if None not in [title_left, title_right]:
		append_type = True
		type_left = type(d1)
		type_right = type(d2)
	if title_left is None:
		title_left = '%s' % type_left
	if title_right is None:
		title_right = '%s' % type_right

	try: d1 = dict(d1)
	except TypeError: pass
	try: d2 = dict(d2)
	except TypeError: pass
	keys_d1 = list(d1)
	keys_d2 = list(d2)
	data = {}
	for key in keys_d1:
		data[key] = [d1[key], ' ']
		if key in d2:
			data[key][1] = d2[key]
	for key in keys_d2:
		if key in keys_d1:
			continue
		data[key] = [' ', d2[key]]
	max1 = max([ len('%s' % k) for k in keys_d1 ])
	max2 = max([ len('%s' % k) for k in keys_d2 ])
	max_len = max(max1, max2, len(_('<type>')))
	max_key_len_str = '%' + '%s.%s' % (max_len, max_len) + 's'
	max1 = max([ len('%s' % d1[k]) for k in keys_d1 ])
	max2 = max([ len('%s' % d2[k]) for k in keys_d2 ])
	max_data_len = min(max(max1, max2), 100)
	max_data_len_str = '%' + '%s.%s' % (max_data_len, max_data_len) + 's'
	diff_indicator_len_str = '%' + '%s.%s' % (len(difference_indicator), len(difference_indicator)) + 's'
	line_template = (' ' * left_margin) + diff_indicator_len_str + max_key_len_str + key_delim + max_data_len_str + data_delim + '%s'

	lines = []
	# debugging:
	#lines.append(u'                                        (40 regular spaces)')
	#lines.append((u' ' * 40) + u"(u' ' * 40)")
	#lines.append((u'%40.40s' % u'') + u"(u'%40.40s' % u'')")
	#lines.append((u'%40.40s' % u' ') + u"(u'%40.40s' % u' ')")
	#lines.append((u'%40.40s' % u'.') + u"(u'%40.40s' % u'.')")
	#lines.append(line_template)
	lines.append(line_template % ('', '', title_left, title_right))
	if append_type:
		lines.append(line_template % ('', _('<type>'), type_left, type_right))

	if ignore_diff_in_keys is None:
		ignore_diff_in_keys = []

	for key in keys_d1:
		append_type = False
		txt_left_col = '%s' % d1[key]
		try:
			txt_right_col = '%s' % d2[key]
			if type(d1[key]) != type(d2[key]):
				append_type = True
		except KeyError:
			txt_right_col = missing_string
		lines.append(line_template % (
			bool2subst (
				((txt_left_col == txt_right_col) or (key in ignore_diff_in_keys)),
				'',
				difference_indicator
			),
			key,
			shorten_text(txt_left_col, max_data_len),
			shorten_text(txt_right_col, max_data_len)
		))
		if append_type:
			lines.append(line_template % (
				'',
				_('<type>'),
				shorten_text('%s' % type(d1[key]), max_data_len),
				shorten_text('%s' % type(d2[key]), max_data_len)
			))

	for key in keys_d2:
		if key in keys_d1:
			continue
		lines.append(line_template % (
			bool2subst((key in ignore_diff_in_keys), '', difference_indicator),
			key,
			shorten_text(missing_string, max_data_len),
			shorten_text('%s' % d2[key], max_data_len)
		))

	return lines

#---------------------------------------------------------------------------
def format_dict_like(d, relevant_keys=None, template=None, missing_key_template='<[%(key)s] MISSING>', left_margin=0, tabular=False, value_delimiters=('>>>', '<<<'), eol='\n', values2ignore=None):
	if values2ignore is None:
		values2ignore = []
	if template is not None:
		# all keys in template better exist in d
		try:
			return template % d
		except KeyError:
			# or else
			_log.exception('template contains %%()s key(s) which do not exist in data dict')
		# try to extend dict <d> to contain all required keys,
		# for that to work <relevant_keys> better list all
		# keys used in <template>
		if relevant_keys is not None:
			for key in relevant_keys:
				try:
					d[key]
				except KeyError:
					d[key] = missing_key_template % {'key': key}
			return template % d

	if relevant_keys is None:
		relevant_keys = list(d)
	lines = []
	if value_delimiters is None:
		delim_left = ''
		delim_right = ''
	else:
		delim_left, delim_right = value_delimiters
	if tabular:
		max_len = max([ len('%s' % k) for k in relevant_keys ])
		max_len_str = '%s.%s' % (max_len, max_len)
		line_template = (' ' * left_margin) + '%' + max_len_str + ('s: %s%%s%s' % (delim_left, delim_right))
	else:
		line_template = (' ' * left_margin) + '%%s: %s%%s%s' % (delim_left, delim_right)
	for key in relevant_keys:
		try:
			val = d[key]
		except KeyError:
			continue
		if val not in values2ignore:
			lines.append(line_template % (key, val))
	if eol is None:
		return lines
	return eol.join(lines)

#---------------------------------------------------------------------------
def dict2table_row (
	d:dict,
	col_sep:str=' | ',
	bool3_vals:dict[bool|None,str]=None,
	date_format:str='%Y %b %d  %H:%M',
	max_row_lng:int=80,
	ellipsis:str=u_ellipsis,
	relevant_keys:list=None,
	missing_key_template:str='<?>',
	eol:str='\n'
) -> str:
	"""Turn a dict like into a row for a table.

	Args:
		bool3_vals: text replacements for True/False/None
		ellipsis:
			None - cell content will be wrapped as necessary
			empty ('') - cell content will not be shortened or wrapped
			nonempty - character(s) to signify abbreviation (say, dot, ellipsis, ...)
		relevant_keys: list of keys into <d> which are deemed relevant, and therefore required, too, also defines cell order
		eol: EOL to be used when wrapping cell content
	"""
	if not bool3_vals:
		bool3_vals = {True: 'True', False: 'False', None: '?'}
	if not relevant_keys:
		relevant_keys = list(d.keys())
	d = normalize_dict_like(d, relevant_keys, missing_key_template = missing_key_template)
	cells = []
	for key in relevant_keys:
		val = d[key]
		if isinstance(val, bool) or val is None:
			val = bool3_vals[val]
		elif isinstance(val, str):
			if ellipsis is None:
				# actually: wrap as necessary
				val = unwrap(val, line_separator = '//')
			elif ellipsis:
				val = unwrap(val, line_separator = '//')
				#val = gmTools.shorten_text()
			else:
				val = unwrap(val, line_separator = '//')
		elif isinstance(val, pydt.datetime):
			if not date_format:
				val = '%s' % val
			else:
				val = val.strftime(date_format)
		else:
			val = '%s' % val
		cells.append(val)

	print(col_sep.join(cells))
	return col_sep.join(cells)

#---------------------------------------------------------------------------
def dicts2table_columns(dict_list, left_margin=0, eol='\n', keys2ignore=None, column_labels=None, show_only_changes=False, equality_value='<=>', date_format=None):	#, relevant_keys=None, template=None
	"""Each dict in <dict_list> becomes a column of a table.

	Think of a list of lab results.

	- each key of dict becomes a row label, unless in keys2ignore

	- each entry in the <column_labels> list becomes a column title
	"""
	keys2show = []
	col_max_width = {}
	max_width_of_row_label_col = 0
	col_label_key = '__________#header#__________'
	if keys2ignore is None:
		keys2ignore = []
	if column_labels is not None:
		keys2ignore.append(col_label_key)

	# extract keys from all dicts and calculate column sizes
	for dict_idx in range(len(dict_list)):
		# convert potentially dict-*like* into dict
		d = dict(dict_list[dict_idx])
		# add max-len column label row from <column_labels> list, if available
		if column_labels is not None:
			d[col_label_key] = max(column_labels[dict_idx].split('\n'), key = len)
		field_lengths = []
		# loop over all keys in this dict
		for key in d:
			# ignore this key
			if key in keys2ignore:
				continue
			# remember length of value when displayed
			if isinstance(d[key], pydt.datetime):
				if date_format is None:
					field_lengths.append(len('%s' % d[key]))
				else:
					field_lengths.append(len(d[key].strftime(date_format)))
			else:
				field_lengths.append(len('%s' % d[key]))
			if key in keys2show:
				continue
			keys2show.append(key)
			max_width_of_row_label_col = max(max_width_of_row_label_col, len('%s' % key))
		col_max_width[dict_idx] = max(field_lengths)

	# pivot data into dict of lists per line
	lines = { k: [] for k in keys2show }
	prev_vals = {}
	for dict_idx in range(len(dict_list)):
		max_width_this_col = max(col_max_width[dict_idx], len(equality_value)) if show_only_changes else col_max_width[dict_idx]
		max_len_str = '%s.%s' % (max_width_this_col, max_width_this_col)
		field_template = ' %' + max_len_str + 's'
		d = dict_list[dict_idx]
		for key in keys2show:
			try:
				val = d[key]
			except KeyError:
				lines[key].append(field_template % _('<missing>'))
				continue
			if isinstance(val, pydt.datetime):
				if date_format is not None:
					val = val.strftime(date_format)
			lines[key].append(field_template % val)
			if show_only_changes:
				if key not in prev_vals:
					prev_vals[key] = '%s' % lines[key][-1]
					continue
				if lines[key][-1] != prev_vals[key]:
					prev_vals[key] = '%s' % lines[key][-1]
					continue
				lines[key][-1] = field_template % equality_value

	# format data into table
	table_lines = []
	max_len_str = '%s.%s' % (max_width_of_row_label_col, max_width_of_row_label_col)
	row_label_template = '%' + max_len_str + 's'
	for key in lines:
		# row label (= key) into first column
		line = (' ' * left_margin) + row_label_template % key + '|'
		# append list values as subsequent columns
		line += '|'.join(lines[key])
		table_lines.append(line)

	# insert lines with column labels (column headers) if any
	if column_labels is not None:
		# first column contains row labels, so no column label needed
		table_header_line_w_col_labels = (' ' * left_margin) + row_label_template % ''
		# second table header line: horizontal separator
		table_header_line_w_separator = (' ' * left_margin) + u_box_horiz_single * (max_width_of_row_label_col)
		max_col_label_widths = [ max(col_max_width[dict_idx], len(equality_value)) for dict_idx in range(len(dict_list)) ]
		for col_idx in range(len(column_labels)):
			max_len_str = '%s.%s' % (max_col_label_widths[col_idx], max_col_label_widths[col_idx])
			col_label_template = '%' + max_len_str + 's'
			table_header_line_w_col_labels += '| '
			table_header_line_w_col_labels += col_label_template % column_labels[col_idx]
			table_header_line_w_separator += '%s%s' % (u_box_plus, u_box_horiz_single)
			table_header_line_w_separator += u_box_horiz_single * max_col_label_widths[col_idx]
		table_lines.insert(0, table_header_line_w_separator)
		table_lines.insert(0, table_header_line_w_col_labels)

	if eol is None:
		return table_lines

	return ('|' + eol).join(table_lines) + '|' + eol

#---------------------------------------------------------------------------
def normalize_dict_like(d, required_keys:list, missing_key_template:str='<[%(key)s] MISSING>'):
	for key in required_keys:
		try:
			d[key]
		except KeyError:
			if missing_key_template is None:
				d[key] = None
			else:
				d[key] = missing_key_template % {'key': key}
	return d

#---------------------------------------------------------------------------
def enumerate_removable_partitions():
	try:
		import pyudev
		import psutil
	except ImportError:
		_log.error('pyudev and/or psutil not installed')
		return {}

	removable_partitions = {}
	ctxt = pyudev.Context()
	removable_devices = [ dev for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk') if dev.attributes.get('removable') == b'1' ]
	all_mounted_partitions = { part.device: part for part in psutil.disk_partitions() }
	for device in removable_devices:
		_log.debug('removable device: %s', device.properties['ID_MODEL'])
		partitions_on_removable_device = {
			part.device_node: {
				'type': device.properties['ID_TYPE'],
				'bus': device.properties['ID_BUS'],
				'device': device.properties['DEVNAME'],
				'partition': part.properties['DEVNAME'],
				'vendor': part.properties['ID_VENDOR'],
				'model': part.properties['ID_MODEL'],
				'fs_label': part.properties['ID_FS_LABEL'],
				'is_mounted': False,
				'mountpoint': None,
				'fs_type': None,
				'size_in_bytes': -1,
				'bytes_free': 0
			} for part in ctxt.list_devices(subsystem='block', DEVTYPE='partition', parent=device)
		}
		for part in partitions_on_removable_device:
			try:
				partitions_on_removable_device[part]['mountpoint'] = all_mounted_partitions[part].mountpoint
				partitions_on_removable_device[part]['is_mounted'] = True
				partitions_on_removable_device[part]['fs_type'] = all_mounted_partitions[part].fstype
				du = shutil.disk_usage(all_mounted_partitions[part].mountpoint)
				partitions_on_removable_device[part]['size_in_bytes'] = du.total
				partitions_on_removable_device[part]['bytes_free'] = du.free
			except KeyError:
				pass			# not mounted
		removable_partitions.update(partitions_on_removable_device)
	return removable_partitions

	# debugging:
	#ctxt = pyudev.Context()
	#for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk'):# if dev.attributes.get('removable') == b'1':
	#	for a in dev.attributes.available_attributes:
	#		print(a, dev.attributes.get(a))
	#	for key, value in dev.items():
	#		print('{key}={value}'.format(key=key, value=value))
	#	print('---------------------------')

#---------------------------------------------------------------------------
def enumerate_optical_writers():
	try:
		import pyudev
	except ImportError:
		_log.error('pyudev not installed')
		return []

	optical_writers = []
	ctxt = pyudev.Context()
	for dev in [ dev for dev in ctxt.list_devices(subsystem='block', DEVTYPE='disk') if dev.properties.get('ID_CDROM_CD_RW', None) == '1' ]:
		optical_writers.append ({
			'type': dev.properties['ID_TYPE'],
			'bus': dev.properties['ID_BUS'],
			'device': dev.properties['DEVNAME'],
			'model': dev.properties['ID_MODEL']
		})
	return optical_writers

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
def prompted_input(prompt=None, default=None):
	"""Obtain entry from standard input.

	CTRL-C aborts and returns _None_

	Args:
		prompt: Prompt text to display in standard output
		default: Default value (for user to press enter only)

	Returns:
		The input, _default_, or _None_.
	"""
	if prompt is None:
		msg = '(CTRL-C aborts)'
	else:
		msg = '%s (CTRL-C aborts)' % prompt

	if default is None:
		msg = msg + ': '
	else:
		msg = '%s [%s]: ' % (msg, default)

	try:
		usr_input = input(msg)
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

	paths = gmPaths(app_name = 'gnumed', wx = wx)

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
		icon_bmp_data = wx.BitmapFromXPMData(pickle.loads(zlib.decompress(__icon_serpent)))
		icon = wx.Icon()
		icon.CopyFromBitmap(icon_bmp_data)
	else:
		_log.debug('icon found in [%s]', found_as)
		icon = wx.Icon()
		try:
			icon.LoadFile(found_as, wx.BITMAP_TYPE_ANY)		#_PNG
		except AttributeError:
			_log.exception("this platform doesn't support wx.Icon().LoadFile()")

	return icon

#---------------------------------------------------------------------------
def create_qrcode(text:str=None, filename:str=None, qr_filename:str=None, verbose:bool=False, ecc_level:str='H', create_svg:bool=False) -> str:
	"""Create a QR code from text or a file.

	Args:
		text: data to encode
		filename: filename to read data from instead of processing _text_
		qr_filename: target file for QR code PNG image, if not specified: generated from _filename_ if that is given
		ecc_level: level of error correction coding, L/M/Q/H
		create_svg: whether to also create an SVG image

	Returns:
		Filename of QR code or _None_.

	The returned filename will be an SVG file if create_svg is 

		 (.png if create_svg is False, .svg if create_svg is True)
	"""
	assert xor(text, filename), 'either <text> OR <filename> must be specified'
	if not text:
		assert qr_filename if not filename else filename, '<qr_filename> must be specified if <filename> is unspecified'

	try:
		import pyqrcode
	except ImportError:
		_log.exception('cannot import <pyqrcode>')
		return None

	if text is None:
		with open(filename, mode = 'rt', encoding = 'utf-8-sig') as input_file:
			text = input_file.read()
	if qr_filename is None:
		if filename is None:
			qr_filename = get_unique_filename(prefix = 'gm-qr-', suffix = '.png')
		else:
			qr_filename = get_unique_filename (
				prefix = fname_stem(filename) + '-',
				suffix = fname_extension(filename) + '.png'
			)
	_log.debug('[%s] -> [%s]', filename, qr_filename)
	qr = pyqrcode.create(text, encoding = 'utf8', error = ecc_level)
	if verbose:
		print('input file:', filename)
		print('output file:', qr_filename)
		print('text to encode:', text)
		print(qr.terminal())
	qr.png(qr_filename, quiet_zone = 1)
	if create_svg:
		qr_filename += '.svg'
		qr.svg(qr_filename, quiet_zone = 1)
	return qr_filename

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# for testing:
	logging.basicConfig(level = logging.DEBUG)
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

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
						print("ERROR (conversion result wrong): >%s<, expected >%s<, got >%s<" % (test[0], test[2], result))
				else:
					print("ERROR (conversion worked but was expected to fail): >%s<, got >%s<" % (test[0], result))
			else:
				if not expected2work:
					continue
				else:
					print("ERROR (conversion failed but was expected to work): >%s<, expected >%s<" % (test[0], test[2]))
	#-----------------------------------------------------------------------
	def test_input2int():
		print(input2int(0))
		print(input2int('0'))
		print(input2int('0', 0, 0))
	#-----------------------------------------------------------------------
	def test_coalesce():

		val = None
		print(val, coalesce(val, 'is None', 'is not None'))
		val = 1
		print(val, coalesce(val, 'is None', 'is not None'))

		import datetime as dt
		print(coalesce(value2test = dt.datetime.now(), template4value = '-- %s --', function4value = ('strftime', '%Y-%m-%d')))

		print('testing coalesce()')
		print("------------------")
		tests = [
			[None, 'something other than <None>', None, None, 'something other than <None>'],
			['Captain', 'Mr.', '%s.'[:4], 'Mr.', 'Capt.'],
			['value to test', 'test 3 failed', 'template with "%s" included', None, 'template with "value to test" included'],
			['value to test', 'test 4 failed', 'template with value not included', None, 'template with value not included'],
			[None, 'initial value was None', 'template4value: %s', None, 'initial value was None'],
			[None, 'initial value was None', 'template4value: %%(abc)s', None, 'initial value was None']
		]
		passed = True
		for test in tests:
			result = coalesce (
				value2test = test[0],
				return_instead = test[1],
				template4value = test[2],
				template4instead = test[3]
			)
			if result != test[4]:
				print("ERROR")
				print("coalesce: (%s, %s, %s, %s)" % (test[0], test[1], test[2], test[3]))
				print("expected:", test[4])
				print("received:", result)
				passed = False

		if passed:
			print("passed")
		else:
			print("failed")
		return passed
	#-----------------------------------------------------------------------
	def test_capitalize():
		print('testing capitalize() ...')
		success = True
		pairs = [
			# [original, expected result, CAPS mode]
			['Boot', 'Boot', CAPS_FIRST_ONLY],
			['boot', 'Boot', CAPS_FIRST_ONLY],
			['booT', 'Boot', CAPS_FIRST_ONLY],
			['BoOt', 'Boot', CAPS_FIRST_ONLY],
			['boots-Schau', 'Boots-Schau', CAPS_WORDS],
			['boots-sChau', 'Boots-Schau', CAPS_WORDS],
			['boot camp', 'Boot Camp', CAPS_WORDS],
			['fahrner-Kampe', 'Fahrner-Kampe', CAPS_NAMES],
			['häkkönen', 'Häkkönen', CAPS_NAMES],
			['McBurney', 'McBurney', CAPS_NAMES],
			['mcBurney', 'McBurney', CAPS_NAMES],
			['blumberg', 'Blumberg', CAPS_NAMES],
			['roVsing', 'RoVsing', CAPS_NAMES],
			['Özdemir', 'Özdemir', CAPS_NAMES],
			['özdemir', 'Özdemir', CAPS_NAMES],
		]
		for pair in pairs:
			result = capitalize(pair[0], pair[2])
			if result != pair[1]:
				success = False
				print('ERROR (caps mode %s): "%s" -> "%s", expected "%s"' % (pair[2], pair[0], result, pair[1]))

		if success:
			print("... SUCCESS")

		return success
	#-----------------------------------------------------------------------
	def test_import_module():
		print("testing import_module_from_directory()")
		path = sys.argv[1]
		name = sys.argv[2]
		try:
			mod = import_module_from_directory(module_path = path, module_name = name)
		except Exception:
			print("module import failed, see log")
			return False

		print("module import succeeded", mod)
		print(dir(mod))
		return True
	#-----------------------------------------------------------------------
	def test_mkdir():
		print("testing mkdir(%s)" % sys.argv[2])
		mkdir(sys.argv[2], 0o0700)

	#-----------------------------------------------------------------------
	def test_gmPaths():
		print("testing gmPaths()")
		print("-----------------")
		#paths = gmPaths(wx=wx, app_name='gnumed')
		paths = gmPaths(wx=None, app_name='gnumed')
		print("user       home dir:", paths.home_dir)
		print("user     config dir:", paths.user_config_dir)
		print("user    appdata dir:", paths.user_appdata_dir)
		print("user       work dir:", paths.user_work_dir)
		print("user       temp dir:", paths.user_tmp_dir)
		print("app@user   temp dir:", paths.tmp_dir)
		print("system   config dir:", paths.system_config_dir)
		print("local      base dir:", paths.local_base_dir)
		print("system app data dir:", paths.system_app_data_dir)
		print("working directory  :", paths.working_dir)
		print("BYTEA cache dir    :", paths.bytea_cache_dir)

	#-----------------------------------------------------------------------
	def test_none_if():
		print("testing none_if()")
		print("-----------------")
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
				print('ERROR: none_if(%s) returned [%s], expected [%s]' % (test[0], none_if(test[0], test[1]), test[2]))

		return True
	#-----------------------------------------------------------------------
	def test_bool2str():
		tests = [
			[True, 'Yes', 'Yes', 'Yes'],
			[False, 'OK', 'not OK', 'not OK']
		]
		for test in tests:
			if bool2str(test[0], test[1], test[2]) != test[3]:
				print('ERROR: bool2str(%s, %s, %s) returned [%s], expected [%s]' % (test[0], test[1], test[2], bool2str(test[0], test[1], test[2]), test[3]))

		return True
	#-----------------------------------------------------------------------
	def test_bool2subst():

		print(bool2subst(True, 'True', 'False', 'is None'))
		print(bool2subst(False, 'True', 'False', 'is None'))
		print(bool2subst(None, 'True', 'False', 'is None'))
	#-----------------------------------------------------------------------
	def test_get_unique_filename():
		print(get_unique_filename())
		print(get_unique_filename(prefix='test-'))
		print(get_unique_filename(suffix='tst'))
		print(get_unique_filename(prefix='test-', suffix='tst'))
		print(get_unique_filename(tmp_dir='/home/ncq/Archiv/'))
	#-----------------------------------------------------------------------
	def test_size2str():
		print("testing size2str()")
		print("------------------")
		tests = [0, 1, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000, 10000000000, 100000000000, 1000000000000, 10000000000000]
		for test in tests:
			print(size2str(test))
	#-----------------------------------------------------------------------
	def test_unwrap():

		test = """
second line\n
	3rd starts with tab  \n
 4th with a space	\n

6th

"""
		print(unwrap(text = test, max_length = 25))
	#-----------------------------------------------------------------------
	def test_wrap():
		test = 'line 1\nline 2\nline 3'

		print("wrap 5-6-7 initial 0, subsequent 0")
		print(wrap(test, 5))
		print()
		print(wrap(test, 6))
		print()
		print(wrap(test, 7))
		print("-------")
		input()
		print("wrap 5 initial 1-1-3, subsequent 1-3-1")
		print(wrap(test, 5, ' ', ' '))
		print()
		print(wrap(test, 5, ' ', '   '))
		print()
		print(wrap(test, 5, '   ', ' '))
		print("-------")
		input()
		print("wrap 6 initial 1-1-3, subsequent 1-3-1")
		print(wrap(test, 6, ' ', ' '))
		print()
		print(wrap(test, 6, ' ', '   '))
		print()
		print(wrap(test, 6, '   ', ' '))
		print("-------")
		input()
		print("wrap 7 initial 1-1-3, subsequent 1-3-1")
		print(wrap(test, 7, ' ', ' '))
		print()
		print(wrap(test, 7, ' ', '   '))
		print()
		print(wrap(test, 7, '   ', ' '))
	#-----------------------------------------------------------------------
	def test_md5():
		print('md5 %s: %s' % (sys.argv[2], file2md5(sys.argv[2])))
		print('chunked md5 %s: %s' % (sys.argv[2], file2chunked_md5(sys.argv[2])))
	#-----------------------------------------------------------------------
	def test_unicode():
		print(u_link_symbol * 10)
		print(u_padlock_open)
		print(u_padlock_closed)
		print('\u1F5DD')
	#-----------------------------------------------------------------------
	def test_xml_escape():
		print(xml_escape_string('<'))
		print(xml_escape_string('>'))
		print(xml_escape_string('&'))
	#-----------------------------------------------------------------------
	def test_tex_escape():
		tests = ['\\', '^', '~', '{', '}', '%',  '&', '#', '$', '_', u_euro, 'abc\ndef\n\n1234']
		tests.append('  '.join(tests))
		for test in tests:
			print('%s:' % test, tex_escape_string(test))

	#-----------------------------------------------------------------------
	def test_rst2latex_snippet():
		tests = ['\\', '^', '~', '{', '}', '%',  '&', '#', '$', '_', u_euro, 'abc\ndef\n\n1234']
		tests.append('  '.join(tests))
		tests.append('C:\Windows\Programme\System 32\lala.txt')
		tests.extend([
			'should be identical',
			'text *some text* text',
			"""A List
======

1. 1
2. 2

3. ist-list
1. more
2. noch was ü
#. nummer x"""
		])
		for test in tests:
			print('==================================================')
			print('raw:')
			print(test)
			print('---------')
			print('ReST 2 LaTeX:')
			latex = rst2latex_snippet(test)
			print(latex)
			if latex.strip() == test.strip():
				print('=> identical')
			print('---------')
			print('tex_escape_string:')
			print(tex_escape_string(test))
			input()

	#-----------------------------------------------------------------------
	def test_strip_trailing_empty_lines():
		tests = [
			'one line, no embedded line breaks  ',
			'one line\nwith embedded\nline\nbreaks\n   '
		]
		for test in tests:
			print('as list:')
			print(strip_trailing_empty_lines(text = test, eol='\n', return_list = True))
			print('as string:')
			print('>>>%s<<<' % strip_trailing_empty_lines(text = test, eol='\n', return_list = False))
		tests = [
			['list', 'without', 'empty', 'trailing', 'lines'],
			['list', 'with', 'empty', 'trailing', 'lines', '', '  ', '']
		]
		for test in tests:
			print('as list:')
			print(strip_trailing_empty_lines(lines = test, eol = '\n', return_list = True))
			print('as string:')
			print(strip_trailing_empty_lines(lines = test, eol = '\n', return_list = False))
	#-----------------------------------------------------------------------
	def test_fname_stem():
		tests = [
			r'abc.exe',
			r'\abc.exe',
			r'c:\abc.exe',
			r'c:\d\abc.exe',
			r'/home/ncq/tmp.txt',
			r'~/tmp.txt',
			r'./tmp.txt',
			r'./.././tmp.txt',
			r'tmp.txt'
		]
		for t in tests:
			print("[%s] -> [%s]" % (t, fname_stem(t)))
	#-----------------------------------------------------------------------
	def test_dir_is_empty():
		print(sys.argv[2], 'empty:', dir_is_empty(sys.argv[2]))

	#-----------------------------------------------------------------------
	def test_compare_dicts():
		d1 = {}
		d2 = {}
		d1[1] = 1
		d1[2] = 2
		d1[3] = 3
		# 4
		d1[5] = 5

		d2[1] = 1
		d2[2] = None
		# 3
		d2[4] = 4

		#compare_dict_likes(d1, d2)

		d1 = {1: 1, 2: 2}
		d2 = {1: 1, 2: 2}

		#compare_dict_likes(d1, d2, 'same1', 'same2')
		print(format_dict_like(d1, tabular = False))
		print(format_dict_like(d1, tabular = True))
		#print(format_dict_like(d2))

	#-----------------------------------------------------------------------
	def test_format_compare_dicts():
		d1 = {}
		d2 = {}
		d1[1] = 1
		d1[2] = 2
		d1[3] = 3
		# 4
		d1[5] = 5

		d2[1] = 1
		d2[2] = None
		# 3
		d2[4] = 4

		print('\n'.join(format_dict_likes_comparison(d1, d2, 'd1', 'd2')))

		d1 = {1: 1, 2: 2}
		d2 = {1: 1, 2: 2}

		print('\n'.join(format_dict_likes_comparison(d1, d2, 'd1', 'd2')))

	#-----------------------------------------------------------------------
	def test_rm_dir():
		rmdir('cx:\windows\system3__2xxxxxxxxxxxxx')

	#-----------------------------------------------------------------------
	def test_rm_dir_content():
		#print(rm_dir_content('cx:\windows\system3__2xxxxxxxxxxxxx'))
		print(rm_dir_content('/tmp/user/1000/tmp'))

	#-----------------------------------------------------------------------
	def test_strip_prefix():
		tests = [
			('', '', ''),
			('a', 'a', ''),
			('GMd: a window title', _GM_TITLE_PREFIX + ':', 'a window title'),
			('\.br\MICROCYTES+1\.br\SPHEROCYTES       present\.br\POLYCHROMASIAmoderate\.br\\', '\.br\\', 'MICROCYTES+1\.br\SPHEROCYTES       present\.br\POLYCHROMASIAmoderate\.br\\')
		]
		for test in tests:
			text, prefix, expect = test
			result = strip_prefix(text, prefix, remove_whitespace = True)
			if result == expect:
				continue
			print('test failed:', test)
			print('result:', result)

	#-----------------------------------------------------------------------
	def test_shorten_text():
		tst = [
			('123', 1),
			('123', 2),
			('123', 3),
			('123', 4),
			('', 1),
			('1', 1),
			('12', 1),
			('', 2),
			('1', 2),
			('12', 2),
			('123', 2)
		]
		for txt, lng in tst:
			print('max', lng, 'of', txt, '=', shorten_text(txt, lng))
	#-----------------------------------------------------------------------
	def test_fname_sanitize():
		tests = [
			'/tmp/test.txt',
			'/tmp/ test.txt',
			'/tmp/ tes\\t.txt',
			'test'
		]
		for test in tests:
			print (test, fname_sanitize(test))

	#-----------------------------------------------------------------------
	def test_create_qrcode():
		print(create_qrcode(text = sys.argv[2], filename=None, qr_filename=None, verbose = True))

	#-----------------------------------------------------------------------
	def test_enumerate_removable_partitions():
		parts = enumerate_removable_partitions()
		for part_name in parts:
			part = parts[part_name]
			print(part['device'])
			print(part['partition'])
			if part['is_mounted']:
				print('%s@%s: %s on %s by %s @ %s (FS=%s: %s free of %s total)' % (
					part['type'],
					part['bus'],
					part['fs_label'],
					part['model'],
					part['vendor'],
					part['mountpoint'],
					part['fs_type'],
					part['bytes_free'],
					part['size_in_bytes']
				))
			else:
				print('%s@%s: %s on %s by %s (not mounted)' % (
					part['type'],
					part['bus'],
					part['fs_label'],
					part['model'],
					part['vendor']
				))

	#-----------------------------------------------------------------------
	def test_enumerate_optical_writers():
		for writer in enumerate_optical_writers():
			print('%s@%s: %s @ %s' % (
				writer['type'],
				writer['bus'],
				writer['model'],
				writer['device']
			))

	#-----------------------------------------------------------------------
	def test_copy_tree_content():
		print(sys.argv[2], '->', sys.argv[3])
		print(copy_tree_content(sys.argv[2], sys.argv[3]))

	#-----------------------------------------------------------------------
	def test_mk_sandbox_dir():
		print(mk_sandbox_dir(base_dir = '/tmp/abcd/efg/h'))

	#-----------------------------------------------------------------------
	def test_make_table_from_dicts():
		dicts = [
			{'pkey': 1, 'value': 'a122'},
			{'pkey': 2, 'value': 'b23'},
			{'pkey': 3, 'value': 'c3'},
			{'pkey': 4, 'value': 'd4ssssssssssss'},
			{'pkey': 5, 'value': 'd4  asdfas '},
			{'pkey': 5, 'value': 'c5---'},
		]
		with open('x.txt', 'w', encoding = 'utf8') as f:
			f.write(dicts2table_columns(dicts, left_margin=2, eol='\n', keys2ignore=None, show_only_changes=True, column_labels = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6']))
			#print(dicts2table_columns(dicts, left_margin=2, eol='\n', keys2ignore=None, show_only_changes=True, column_labels = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6']))

	#-----------------------------------------------------------------------
	def test_create_dir_desc_file():
		global _client_version
		_client_version = 'dev.test'
		print(create_directory_description_file (
			directory = './',
			readme = 'test\ntest2\nsome more text',
			suffix = None
		))

	#-----------------------------------------------------------------------
	def test_dir_list_files():
		print(dir_list_files(directory = sys.argv[2], exclude_subdirs = True))
		print(dir_list_files(directory = sys.argv[2], exclude_subdirs = False))

	#-----------------------------------------------------------------------
	def test_rename_file():
		print(rename_file (
			sys.argv[2],
			sys.argv[3],
			overwrite = True,
			allow_symlink = False,
			allow_hardlink = False
		))

	#-----------------------------------------------------------------------
	def test_xor():
		vals = [
			[False, False, [None]],
			[False, True, [None]],
			[True, True, [None]],
			[None, None, [None]],
			[None, True, [None]],
			[None, False, [None]],
			[None, 0, [None]],
			[None, 1, [None]],
			[None, '', [None]],
			[None, '   ', [None]],
			[None, '<None>', [None]],
			[0,0, [None]],
			[0,1, [None]],
			[1,1, [None]],
			[1,2, [None]],
			[1, '', [None]],
			[1, '   ', [None]],
			[1, '<1>', [None]],
		]
		for rec in vals:
			print('%s xor %s: %s (exactly one in: %s)' % (
				rec[0],
				rec[1],
				xor(rec[0], rec[1], rec[2]),
				rec[2]
			))

	#-----------------------------------------------------------------------
	test_xor()
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
	#test_xml_escape()
	#test_strip_trailing_empty_lines()
	#test_fname_stem()
	#test_tex_escape()
	#test_rst2latex_snippet()
	#test_dir_is_empty()
	#test_compare_dicts()
	#test_rm_dir()
	#test_rm_dir_content()
	#test_strip_prefix()
	#test_shorten_text()
	#test_format_compare_dicts()
	#test_fname_sanitize()
	#test_create_qrcode()
	#test_enumerate_removable_partitions()
	#test_enumerate_optical_writers()
	#test_copy_tree_content()
	#test_mk_sandbox_dir()
	#test_make_table_from_dicts()
	#test_create_dir_desc_file()
	#test_dir_list_files()
	#test_rename_file()

#===========================================================================
