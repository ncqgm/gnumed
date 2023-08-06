#!/usr/bin/env python3

__doc__ = """GNUmed client launcher.

This is the launcher for the GNUmed GUI client. It takes
care of all the pre- and post-GUI runtime environment setup.

--quiet
 Be extra quiet and show only _real_ errors in the log.
--debug
 Pre-set the [debug mode] checkbox in the login dialog to
 increase verbosity in the log file. Useful for, well, debugging :-)
--slave
 Pre-set the [enable remote control] checkbox in the login
 dialog to enable the XML-RPC remote control feature.
--hipaa
 Enable HIPAA functionality which has user impact.
--profile=<file>
 Activate profiling and write profile data to <file>.
--tool=<TOOL>
 Run TOOL instead of the main GUI.
--text-domain=<text domain>
 Set this to change the name of the language file to be loaded.
 Note, this does not change the directory the file is searched in,
 only the name of the file where messages are loaded from. The
 standard textdomain is, of course, "gnumed.mo".
--log-file=<file>
 Use this to change the name of the log file.
 See gmLog2.py to find out where the standard log file would
 end up.
--conf-file=<file>
 Use configuration file <file> instead of searching for it in
 standard locations.
--lang-gettext=<language>
 Explicitly set the language to use in gettext translation. The very
 same effect can be achieved by setting the environment variable $LANG
 from a launcher script.
--override-schema-check
 Continue loading the client even if the database schema version
 and the client software version cannot be verified to be compatible.
--skip-update-check
 Skip checking for client updates. This is useful during development
 and when the update check URL is unavailable (down).
--local-import
 Adjust the PYTHONPATH such that GNUmed can be run from a local source tree.
--ui=<ui type>
 Start an alternative UI. Defaults to wxPython if not specified.
 Currently "wxp" (wxPython) only.
--wxp=<version>
 Explicitely request a wxPython version. Can be set to either "2" or "3".
 Defaults to "try 3, then 2" if not set.
--special=<special>
 Used for debugging.
--version, -V
 Show version information.
--help, -h, or -?
 Show this help.
"""
#==========================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"


# standard library
import sys
import os
import platform
import faulthandler
import random
import logging
import signal
import os.path
import shutil
import stat
import io


# do not run as module
if __name__ != "__main__":
	print("GNUmed startup: This is not intended to be imported as a module !")
	print("-----------------------------------------------------------------")
	print(__doc__)
	sys.exit(1)


# do not run as root
if os.name in ['posix'] and os.geteuid() == 0:
	print("""
GNUmed startup: GNUmed should not be run as root.
-------------------------------------------------

Running GNUmed as <root> can potentially put all
your medical data at risk. It is strongly advised
against. Please run GNUmed as a non-root user.
""")
	sys.exit(1)

#----------------------------------------------------------
current_client_version = '1.8.15'
current_client_branch = '1.8'

_log = None
_pre_log_buffer = []
_cfg = None
_old_sig_term = None
_known_short_options = 'h?V'
_known_long_options = [
	'debug',
	'slave',
	'skip-update-check',
	'profile=',
	'text-domain=',
	'log-file=',
	'conf-file=',
	'lang-gettext=',
	'ui=',
	'override-schema-check',
	'local-import',
	'help',
	'version',
	'hipaa',
	'wxp=',
	'tool=',
	'special='
]

_known_ui_types = [
	'web',
	'wxp',
	'chweb'
]

_known_tools = [
	'check_enc_epi_xref',
	'export_pat_emr_structure',
	'check_mimetypes_in_archive',
	'read_all_rows_of_table',
	'fingerprint_db'
]


import_error_sermon = """
GNUmed startup: Cannot load GNUmed Python modules !
---------------------------------------------------
CRITICAL ERROR: Program halted.

Please make sure you have:

 1) the required third-party Python modules installed
 2) the GNUmed Python modules linked or installed into site-packages/
    (if you do not run from a CVS tree the installer should have taken care of that)
 3) your PYTHONPATH environment variable set up correctly

<sys.path> is currently set to:

 %s

If you are running from a copy of the CVS tree make sure you
did run gnumed/check-prerequisites.sh with good results.

If you still encounter errors after checking the above
requirements please ask on the mailing list.
"""


missing_cli_config_file = """
GNUmed startup: Missing configuration file.
-------------------------------------------

You explicitly specified a configuration file
on the command line:

	--conf-file=%s

The file does not exist, however.
"""


no_config_files = """
GNUmed startup: Missing configuration files.
--------------------------------------------

None of the below candidate configuration
files could be found:

 %s

Cannot run GNUmed without any of them.
"""

#==========================================================
# convenience functions
#----------------------------------------------------------
def _symlink_windows(source, link_name):
	import ctypes
	csl = ctypes.windll.kernel32.CreateSymbolicLinkW
	csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
	csl.restype = ctypes.c_ubyte
	if os.path.isdir(source):
		flags = 1
	else:
		flags = 0
	ret_code = csl(link_name, source.replace('/', '\\'), flags)
	if ret_code == 0:
		raise ctypes.WinError()
	return ret_code

#==========================================================
# startup helpers
#----------------------------------------------------------
def setup_fault_handler(target=None):
	if target is None:
		faulthandler.enable()
		_pre_log_buffer.append('<faulthandler> enabled, target = [console]: %s' % faulthandler)
		return
	_pre_log_buffer.append('<faulthandler> enabled, target = [%s]: %s' % (target, faulthandler))
	faulthandler.enable(file = target)

#==========================================================
def setup_console_encoding():
	print_lines = []
	try:
		sys.stdout.reconfigure(errors = 'surrogateescape')
		sys.stderr.reconfigure(errors = 'surrogateescape')
		_pre_log_buffer.append('stdout/stderr reconfigured to use <surrogateescape> for encoding errors')
		return
	except AttributeError:
		line = 'cannot reconfigure sys.stdout/stderr to use <errors="surrogateescape"> (needs Python 3.7+)'
		_pre_log_buffer.append(line)
		print_lines.append(line)
	try:
		_pre_log_buffer.append('sys.stdout/stderr default to "${PYTHONIOENCODING}=%s"' % os.environ['PYTHONIOENCODING'])
		return
	except KeyError:
		lines = [
			'${PYTHONIOENCODING} is not set up, use <PYTHONIOENCODING=utf-8:surrogateescape> in the shell (for Python < 3.7)',
			'console encoding errors may occur'
		]
		for line in lines:
			print_lines.append(line)
			_pre_log_buffer.append(line)
		for line in print_lines:
			print('GNUmed startup:', line)

#==========================================================
def setup_python_path():

	if not '--local-import' in sys.argv:
		_pre_log_buffer.append('running against systemwide install')
		return

	local_python_import_dir = os.path.dirname (
		os.path.abspath(os.path.join(sys.argv[0], '..'))
	)
	print("Running from local source tree (%s) ..." % local_python_import_dir)
	_pre_log_buffer.append("running from local source tree: %s" % local_python_import_dir)

	# does the path exist at all, physically ?
	# (*broken* links are reported as False)
	link_name = os.path.join(local_python_import_dir, 'Gnumed')
	if os.path.exists(link_name):
		_pre_log_buffer.append('local module import dir symlink exists: %s' % link_name)
	else:
		real_dir = os.path.join(local_python_import_dir, 'client')
		print('Creating local module import symlink ...')
		print(' real dir:', real_dir)
		print('     link:', link_name)
		try:
			os.symlink(real_dir, link_name)
		except AttributeError:
			_pre_log_buffer.append('Windows does not have os.symlink(), resorting to ctypes')
			result = _symlink_windows(real_dir, link_name)
			_pre_log_buffer.append('ctypes.windll.kernel32.CreateSymbolicLinkW() exit code: %s', result)
		_pre_log_buffer.append('created local module import dir symlink: link [%s] => dir [%s]' % (link_name, real_dir))

	sys.path.insert(0, local_python_import_dir)
	_pre_log_buffer.append('sys.path with local module import base dir prepended: %s' % sys.path)

#==========================================================
def setup_local_repo_path():

	local_repo_path = os.path.expanduser(os.path.join (
		'~',
		'.gnumed',
		'local_code',
		str(current_client_branch)
	))
	local_wxGladeWidgets_path = os.path.join(local_repo_path, 'Gnumed', 'wxGladeWidgets')

	if not os.path.exists(local_wxGladeWidgets_path):
		_log.debug('[%s] not found', local_wxGladeWidgets_path)
		_log.info('local wxGlade widgets repository not available')
		return

	_log.info('local wxGlade widgets repository found:')
	_log.info(local_wxGladeWidgets_path)

	if not os.access(local_wxGladeWidgets_path, os.R_OK):
		_log.error('invalid repo: no read access')
		return

	all_entries = os.listdir(os.path.join(local_repo_path, 'Gnumed'))
	_log.debug('repo base contains: %s', all_entries)
	all_entries.remove('wxGladeWidgets')
	try:
		all_entries.remove('__init__.py')
	except ValueError:
		_log.error('invalid repo: lacking __init__.py')
		return
	try:
		all_entries.remove('__init__.pyc')
	except ValueError:
		pass

	if len(all_entries) > 0:
		_log.error('insecure repo: additional files or directories found')
		return

	# repo must be 0700 (rwx------)
	stat_val = os.stat(local_wxGladeWidgets_path)
	_log.debug('repo stat(): %s', stat_val)
	perms = stat.S_IMODE(stat_val.st_mode)
	_log.debug('repo permissions: %s (octal: %s)', perms, oct(perms))
	if perms != 448:				# octal 0700
		if os.name in ['nt']:
			_log.warning('this platform does not support os.stat() permission checking')
		else:
			_log.error('insecure repo: permissions not 0600')
			return

	print("Activating local wxGlade widgets repository (%s) ..." % local_wxGladeWidgets_path)
	sys.path.insert(0, local_repo_path)
	_log.debug('sys.path with repo:')
	_log.debug(sys.path)

#==========================================================
def setup_logging():
	try:
		from Gnumed.pycommon import gmLog2 as _gmLog2
	except ImportError:
		print(import_error_sermon % '\n '.join(sys.path))
		sys.exit(1)

	print("Log file:", _gmLog2._logfile.name)
	setup_fault_handler(target = _gmLog2._logfile)

	global gmLog2
	gmLog2 = _gmLog2

	global _log
	_log = logging.getLogger('gm.launcher')

#==========================================================
def __log_module_sys():
	_log.info('module <sys> info:')
	attrs2skip = ['__doc__', 'copyright', '__name__', '__spec__']
	for attr_name in dir(sys):
		if attr_name in attrs2skip:
			continue
		if attr_name.startswith('set'):
			continue
		attr = getattr(sys, attr_name)
		if not attr_name.startswith('get'):
			_log.info('%s: %s', attr_name.rjust(30), attr)
			continue
		if callable(attr):
			try:
				_log.info('%s: %s', attr_name.rjust(30), attr())
			except Exception:
				_log.exception('%s: <cannot log>', attr_name.rjust(30))
			continue

#----------------------------------------------------------
def __log_module_platform():
	_log.info('module <platform> info:')
	attrs2skip = ['__doc__', '__copyright__', '__name__', '__spec__', '__cached__', '__builtins__']
	for attr_name in dir(platform):
		if attr_name in attrs2skip:
			continue
		if attr_name.startswith('set'):
			continue
		attr = getattr(platform, attr_name)
		if callable(attr):
			if attr_name.startswith('_'):
				_log.info('%s: %s', attr_name.rjust(30), attr)
				continue
			try:
				_log.info('%s: %s', attr_name.rjust(30), attr())
			except Exception:
				_log.exception('%s: <cannot log>', attr_name.rjust(30))
			continue
		_log.info('%s: %s', attr_name.rjust(30), attr)
		continue

#----------------------------------------------------------
def __log_module_os():
	_log.info('module <os> info:')
	for n in os.confstr_names:
		_log.info('%s: %s', ('confstr[%s]' % n).rjust(40), os.confstr(n))
	for n in os.sysconf_names:
		try:
			_log.info('%s: %s', ('sysconf[%s]' % n).rjust(40), os.sysconf(n))
		except Exception:
			_log.exception('%s: <invalid> ??', ('sysconf[%s]' % n).rjust(30))
	os_attrs = ['name', 'ctermid', 'getcwd', 'get_exec_path', 'getegid', 'geteuid', 'getgid', 'getgroups', 'getlogin', 'getpgrp', 'getpid', 'getppid', 'getresuid', 'getresgid', 'getuid', 'supports_bytes_environ', 'uname', 'get_terminal_size', 'pathconf_names', 'times', 'cpu_count', 'curdir', 'pardir', 'sep', 'altsep', 'extsep', 'pathsep', 'defpath', 'linesep', 'devnull']
	for attr_name in os_attrs:
		attr = getattr(os, attr_name)
		if callable(attr):
			try:
				_log.info('%s: %s', attr_name.rjust(40), attr())
			except Exception as exc:
				_log.error('%s: a callable, but call failed (%s)', attr_name.rjust(40), exc)
			continue
		_log.info('%s: %s', attr_name.rjust(40), attr)
	_log.info('process environment:')
	for key, val in os.environ.items():
		_log.info(' %s: %s' % (('${%s}' % key).rjust(40), val))

#----------------------------------------------------------
def __log_module_sysconfig():
	import sysconfig
	_log.info('module <sysconfig> info:')
	_log.info(' platform [%s] -- python version [%s]', sysconfig.get_platform(), sysconfig.get_python_version())
	_log.info(' sysconfig.get_paths():')
	paths = sysconfig.get_paths()
	for path in paths:
		_log.info('%s: %s', path.rjust(40), paths[path])
	_log.info(' sysconfig.get_config_vars():')
	conf_vars = sysconfig.get_config_vars()
	for var in conf_vars:
		_log.info('%s: %s', var.rjust(45), conf_vars[var])

#----------------------------------------------------------
def log_startup_info():
	global _pre_log_buffer
	if len(_pre_log_buffer) > 0:
		_log.info('early startup log buffer:')
	for line in _pre_log_buffer:
		_log.info(' ' + line)
	del _pre_log_buffer
	_log.info('GNUmed client version [%s] on branch [%s]', current_client_version, current_client_branch)
	_log.info('Platform: %s', platform.uname())
	_log.info(('Python %s on %s (%s)' % (sys.version, sys.platform, os.name)).replace('\n', '<\\n>'))
	try:
		import lsb_release
		_log.info('lsb_release: %s', lsb_release.get_distro_information())
	except ImportError:
		pass
	__log_module_sys()
	__log_module_platform()
	__log_module_os()
	__log_module_sysconfig()

	#for f in [ mod.__spec__ for mod in sys.modules.values() ]:
	#	print(f.origin)

#==========================================================
def setup_console_exception_handler():
	from Gnumed.pycommon.gmTools import handle_uncaught_exception_console

	sys.excepthook = handle_uncaught_exception_console

#==========================================================
def setup_cli():
	from Gnumed.pycommon import gmCfg2

	global _cfg
	_cfg = gmCfg2.gmCfgData()
	_cfg.add_cli (
		short_options = _known_short_options,
		long_options = _known_long_options
	)

	val = _cfg.get(option = '--debug', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = 'debug',
		value = val
	)

	val = _cfg.get(option = '--slave', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = 'slave',
		value = val
	)

	val = _cfg.get(option = '--skip-update-check', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = 'skip-update-check',
		value = val
	)

	val = _cfg.get(option = '--hipaa', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = 'hipaa',
		value = val
	)

	val = _cfg.get(option = '--local-import', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = 'local-import',
		value = val
	)

	_cfg.set_option (
		option = 'client_version',
		value = current_client_version
	)

	_cfg.set_option (
		option = 'client_branch',
		value = current_client_branch
	)

	value = _cfg.get(option = '--special', source_order = [('cli', 'return')])
	if value:
		value = value.split(',')
		print('GNUmed startup: --special:', value)
	else:
		value = []
	_cfg.set_option(option = 'special', value = value)

#==========================================================
def handle_sig_term(signum, frame):
	_log.critical('SIGTERM (SIG%s) received, shutting down ...' % signum)
	gmLog2.flush()
	print('GNUmed: SIGTERM (SIG%s) received, shutting down ...' % signum)
	if frame is not None:
		print('%s::%s@%s' % (frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno))

	# FIXME: need to do something useful here

	if _old_sig_term in [None, signal.SIG_IGN]:
		sys.exit(1)
	else:
		_old_sig_term(signum, frame)

#----------------------------------------------------------
def setup_signal_handlers():
	global _old_sig_term
	old_sig_term = signal.signal(signal.SIGTERM, handle_sig_term)

#==========================================================
def setup_locale():
	gmI18N.activate_locale()

	td = _cfg.get(option = '--text-domain', source_order = [('cli', 'return')])
	l =  _cfg.get(option = '--lang-gettext', source_order = [('cli', 'return')])
	gmI18N.install_domain(domain = td, language = l, prefer_local_catalog = _cfg.get(option = 'local-import'))

#	# make sure we re-get the default encoding
#	# in case it changed
#	gmLog2.set_string_encoding()

#==========================================================
def handle_help_request():
	src = [('cli', 'return')]

	help_requested = (
		_cfg.get(option = '--help', source_order = src) or
		_cfg.get(option = '-h', source_order = src) or
		_cfg.get(option = '-?', source_order = src)
	)

	if help_requested:
		print(_(
			'Help requested\n'
			'--------------'
		))
		print(__doc__)
		sys.exit(0)

#==========================================================
def handle_version_request():
	src = [('cli', 'return')]

	version_requested = (
		_cfg.get(option = '--version', source_order = src) or
		_cfg.get(option = '-V', source_order = src)
	)

	if version_requested:

		from Gnumed.pycommon.gmPG2 import map_client_branch2required_db_version, known_schema_hashes

		print('GNUmed version information')
		print('--------------------------')
		print('client     : %s on branch [%s]' % (current_client_version, current_client_branch))
		print('database   : %s' % map_client_branch2required_db_version[current_client_branch])
		print('schema hash: %s' % known_schema_hashes[map_client_branch2required_db_version[current_client_branch]])
		sys.exit(0)

#==========================================================
def setup_paths_and_files():
	"""Create needed paths in user home directory."""

	gnumed_DIR_README_TEXT = """GNUmed Electronic Medical Record

	%s/

This directory should only ever contain files which the
user will come into direct contact with while using the
application (say, by selecting a file from the file system,
as when selecting document parts from files). You can create
subdirectories here as you see fit for the purpose.

This directory will also serve as the default directory when
GNUmed asks the user to select a directory for storing a
file.

Any files which are NOT intended for direct user interaction
but must be configured to live at a known location (say,
inter-application data exchange files) should be put under
the hidden directory "%s/".""" % (
		os.path.expanduser(os.path.join('~', 'gnumed')),
		os.path.expanduser(os.path.join('~', '.gnumed'))
	)

	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'scripts')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'spellcheck')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'error_logs')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed')))

	README = io.open(os.path.expanduser(os.path.join('~', 'gnumed', '00_README')), mode = 'wt', encoding = 'utf8')
	README.write(gnumed_DIR_README_TEXT)
	README.close()

	# wxPython not available yet
	paths = gmTools.gmPaths(app_name = 'gnumed')
	print("Temp dir:", paths.tmp_dir)

	# ensure there's a user-level config file
	io.open(os.path.expanduser(os.path.join('~', '.gnumed', 'gnumed.conf')), mode = 'a+t').close()

	# symlink log file into temporary directory for easier debugging (everything in one place)
	logfile_link = os.path.join(paths.tmp_dir, 'zzz-gnumed.log')
	gmTools.mklink (gmLog2._logfile.name, logfile_link, overwrite = False)

#==========================================================
def setup_date_time():
	gmDateTime.init()

#==========================================================
def setup_cfg():
	"""Detect and setup access to GNUmed config file.

	Parts of this will have limited value due to
	wxPython not yet being available.
	"""

	enc = gmI18N.get_encoding()
	paths = gmTools.gmPaths(app_name = 'gnumed')

	candidates = [
		# the current working dir
		['workbase', os.path.join(paths.working_dir, 'gnumed.conf')],
		# /etc/gnumed/
		['system', os.path.join(paths.system_config_dir, 'gnumed-client.conf')],
		# ~/.gnumed/
		['user', os.path.join(paths.user_config_dir, 'gnumed.conf')],
		# CVS/tgz tree .../gnumed/client/ (IOW a local installation)
		['local', os.path.join(paths.local_base_dir, 'gnumed.conf')]
	]
	# --conf-file=
	explicit_fname = _cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
	if explicit_fname is None:
		candidates.append(['explicit', None])
	else:
		candidates.append(['explicit', explicit_fname])

	for candidate in candidates:
		_cfg.add_file_source (
			source = candidate[0],
			file = candidate[1],
			encoding = enc
		)

	# --conf-file given but does not actually exist ?
	if explicit_fname is not None:
		if _cfg.source_files['explicit'] is None:
			_log.error('--conf-file argument does not exist')
			print(missing_cli_config_file % explicit_fname)
			sys.exit(1)

	# any config file found at all ?
	found_any_file = False
	for f in _cfg.source_files.values():
		if f is not None:
			found_any_file = True
			break
	if not found_any_file:
		_log.error('no config file found at all')
		print(no_config_files % '\n '.join(candidates))
		sys.exit(1)

	# mime type handling sources
	fname = 'mime_type2file_extension.conf'
	_cfg.add_file_source (
		source = 'user-mime',
		file = os.path.join(paths.user_config_dir, fname),
		encoding = enc
	)
	_cfg.add_file_source (
		source = 'system-mime',
		file = os.path.join(paths.system_config_dir, fname),
		encoding = enc
	)

#==========================================================
def setup_ui_type():
	global ui_type
	ui_type = _cfg.get(option = '--ui', source_order = [('cli', 'return')])
	if ui_type in [True, False, None]:
		ui_type = 'wxp'
	ui_type = ui_type.strip()
	if ui_type not in _known_ui_types:
		_log.error('unknown UI type requested: %s', ui_type)
		_log.debug('known UI types are: %s', str(_known_ui_types))
		print("GNUmed startup: Unknown UI type (%s). Defaulting to wxPython client." % ui_type)
		ui_type = 'wxp'
	_log.debug('UI type: %s', ui_type)

#==========================================================
def setup_backend_environment():

	db_version = gmPG2.map_client_branch2required_db_version[current_client_branch]
	_log.info('client expects database version [%s]', db_version)
	_cfg.set_option (
		option = 'database_version',
		value = db_version
	)

	# set up database connection timezone
	timezone = _cfg.get (
		group = 'backend',
		option = 'client timezone',
		source_order = [
			('explicit', 'return'),
			('workbase', 'return'),
			('local', 'return'),
			('user', 'return'),
			('system', 'return')
		]
	)
#	if timezone is not None:
#		gmPG2.set_default_client_timezone(timezone)

#==========================================================
def run_gui():
	gmHooks.run_hook_script(hook = 'startup-before-GUI')

	if ui_type == 'wxp':
		from Gnumed.wxpython import gmGuiMain
		profile_file = _cfg.get(option = '--profile', source_order = [('cli', 'return')])
		if profile_file is not None:
			_log.info('writing profiling data into %s', profile_file)
			import profile
			profile.run('gmGuiMain.main()', profile_file)
		else:
			gmGuiMain.main()
	#elif ui_type == u'web':
	#	from Gnumed.proxiedpyjamas import gmWebGuiServer
	#	gmWebGuiServer.main()
	#elif ui_type == u'chweb':
	#	from Gnumed.CherryPy import gmGuiWeb
	#	gmGuiWeb.main()

	gmHooks.run_hook_script(hook = 'shutdown-post-GUI')

	return 0

#==========================================================
def run_tool():
	"""Run a console tool.

	Exit codes as per man page:
		   0: normal termination of the client
		 < 0: some error occurred while trying to run a console tool
			  -1: an unknown console tool was requested
			< -1: an error occurred while a console tool was run
		-999: hard abort of the client

	One of these needs to be returned from this function (and,
	by extension from the tool having been run, if any).
	"""
	tool = _cfg.get(option = '--tool', source_order = [('cli', 'return')])
	if tool is None:
		# not running a tool
		return None

	if tool not in _known_tools:
		_log.error('unknown tool requested: %s', tool)
		print('GNUmed startup: Unknown tool [%s] requested.' % tool)
		print('GNUmed startup: Known tools: %s' % _known_tools)
		return -1

	print('')
	print('==============================================')
	print('Running tool: %s' % tool)
	print('----------------------------------------------')
	print('')
	login, creds = gmPG2.request_login_params()
	gmConnectionPool._VERBOSE_PG_LOG = _cfg.get(option = 'debug')
	pool = gmConnectionPool.gmConnectionPool()
	pool.credentials = creds
	print('')

	if tool == 'read_all_rows_of_table':
		result = gmPG2.read_all_rows_of_table()
		if result in [None, True]:
			print('Success.')
			return 0
		print('Failed. Check the log for details.')
		return -2

	if tool == 'check_mimetypes_in_archive':
		from Gnumed.business import gmDocuments
		return gmDocuments.check_mimetypes_in_archive()

	if tool == 'check_enc_epi_xref':
		from Gnumed.business import gmEMRStructItems
		return gmEMRStructItems.check_fk_encounter_fk_episode_x_ref()

	if tool == 'fingerprint_db':
		fname = 'db-fingerprint.txt'
		result = gmPG2.get_db_fingerprint(fname = fname, with_dump = True)
		if result == fname:
			print('Success: %s' % fname)
			return 0
		print('Failed. Check the log for details.')
		return -2

	if tool == 'export_pat_emr_structure':
		# setup praxis
		from Gnumed.business import gmPraxis
		praxis = gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.get_praxis_branches()[0])
		# get patient
		from Gnumed.business import gmPersonSearch
		pat = gmPersonSearch.ask_for_patient()
		# setup exporters
		from Gnumed.business import gmEMRStructItems
		from Gnumed.exporters import gmTimelineExporter
		from Gnumed.exporters import gmPatientExporter
		while pat is not None:
			print('patient:', pat['description_gender'])
			# as EMR structure
			fname = os.path.expanduser('~/gnumed/gm-emr_structure-%s.txt' % pat.subdir_name)
			print('EMR structure:', gmEMRStructItems.export_emr_structure(patient = pat, filename = fname))
			# as timeline
			fname = os.path.expanduser('~/gnumed/gm-emr-%s.timeline' % pat.subdir_name)
			try:
				print('EMR timeline:', gmTimelineExporter.create_timeline_file (
					patient = pat,
					filename = fname,
					include_documents = True,
					include_vaccinations = True,
					include_encounters = True
				))
			finally:
				pass
			# as journal by encounter
			exporter = gmPatientExporter.cEMRJournalExporter()
			fname = os.path.expanduser('~/gnumed/gm-emr-journal_by_encounter-%s.txt' % pat.subdir_name)
			print('EMR journal (by encounter):', exporter.save_to_file_by_encounter(patient = pat, filename = fname))
			# as journal by mod time
			fname = os.path.expanduser('~/gnumed/gm-emr-journal_by_mod_time-%s.txt' % pat.subdir_name)
			print('EMR journal (by mod time):', exporter.save_to_file_by_mod_time(patient = pat, filename = fname))
			# as statistical summary
			fname = os.path.expanduser('~/gnumed/gm-emr-statistics-%s.txt' % pat.subdir_name)
			output_file = io.open(fname, mode = 'wt', encoding = 'utf8', errors = 'replace')
			emr = pat.emr
			output_file.write(emr.format_statistics())
			output_file.close()
			print('EMR statistics:', fname)
			# as text file
			exporter = gmPatientExporter.cEmrExport(patient = pat)
			fname = os.path.expanduser('~/gnumed/gm-emr-text_export-%s.txt' % pat.subdir_name)
			output_file = io.open(fname, mode = 'wt', encoding = 'utf8', errors = 'replace')
			exporter.set_output_file(output_file)
			exporter.dump_constraints()
			exporter.dump_demographic_record(True)
			exporter.dump_clinical_record()
			exporter.dump_med_docs()
			output_file.close()
			print('EMR text file:', fname)
			# another patient ?
			pat = gmPersonSearch.ask_for_patient()
		return 0

	# tool export_patient_as (vcf, gdt, ...)
	#if tool == 'export_pat_demographics':

	# should not happen (because checked against _known_tools)
	return -1

#==========================================================
# shutdown helpers
#----------------------------------------------------------
def shutdown_backend():
	gmPG2.shutdown()

#==========================================================
def shutdown_logging():

#	if _cfg.get(option = u'debug'):
#		import types

#		def get_refcounts():
#			refcount = {}
#			# collect all classes
#			for module in sys.modules.values():
#				for sym in dir(module):
#					obj = getattr(module, sym)
#					if type(obj) is types.ClassType:
#						refcount[obj] = sys.getrefcount(obj)
#			# sort by refcount
#			pairs = map(lambda x: (x[1],x[0]), refcount.items())
#			pairs.sort()
#			pairs.reverse()
#			return pairs

#		rcfile = io.open('./gm-refcount.lst', 'wt', encoding = 'utf8')
#		for refcount, class_ in get_refcounts():
#			if not class_.__name__.startswith('wx'):
#				rcfile.write(u'%10d %s\n' % (refcount, class_.__name__))
#		rcfile.close()

	# do not choke on Windows
	logging.raiseExceptions = False

#==========================================================
def shutdown_tmp_dir():

	tmp_dir = gmTools.gmPaths().tmp_dir

	if _cfg.get(option = 'debug'):
		_log.debug('not removing tmp dir (--debug mode): %s', tmp_dir)
		return

	_log.warning('removing tmp dir: %s', tmp_dir)
	shutil.rmtree(tmp_dir, True)

#==========================================================
# main - launch the GNUmed wxPython GUI client
#----------------------------------------------------------

random.seed()

# setup
setup_fault_handler(target = None)
setup_console_encoding()
setup_python_path()
setup_logging()
log_startup_info()
setup_console_exception_handler()
setup_cli()
setup_signal_handlers()
setup_local_repo_path()

from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

setup_locale()
handle_help_request()
handle_version_request()
setup_paths_and_files()
setup_date_time()
setup_cfg()
setup_ui_type()

from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmConnectionPool
setup_backend_environment()

# main
exit_code = run_tool()
if exit_code is None:
	from Gnumed.pycommon import gmHooks
	exit_code = run_gui()

# shutdown
shutdown_backend()
shutdown_tmp_dir()
_log.info('Normally shutting down as main module.')
shutdown_logging()

sys.exit(exit_code)

#==========================================================
