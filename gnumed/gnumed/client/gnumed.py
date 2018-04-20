#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

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
--version, -V
 Show version information.
--help, -h, or -?
 Show this help.
"""
#==========================================================
__author__ = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"


# standard library
import sys
import os
import platform
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
current_client_version = u'1.7.2rc1'
current_client_branch = u'1.7'

_log = None
_pre_log_buffer = []
_cfg = None
_old_sig_term = None
_known_short_options = u'h?V'
_known_long_options = [
	u'debug',
	u'slave',
	u'skip-update-check',
	u'profile=',
	u'text-domain=',
	u'log-file=',
	u'conf-file=',
	u'lang-gettext=',
	u'ui=',
	u'override-schema-check',
	u'local-import',
	u'help',
	u'version',
	u'hipaa',
	u'wxp=',
	u'tool='
]

_known_ui_types = [
	u'web',
	u'wxp',
	u'chweb'
]

_known_tools = [
	u'check_enc_epi_xref',
	u'export_pat_emr_structure'
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

sys.path is currently set to:

 %s

If you are running from a copy of the CVS tree make sure you
did run gnumed/check-prerequisites.sh with good results.

If you still encounter errors after checking the above
requirements please ask on the mailing list.
"""


missing_cli_config_file = u"""
GNUmed startup: Missing configuration file.
-------------------------------------------

You explicitly specified a configuration file
on the command line:

	--conf-file=%s

The file does not exist, however.
"""


no_config_files = u"""
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
def setup_python_path():

	if not u'--local-import' in sys.argv:
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

	print("Adjusting PYTHONPATH ...")
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
def setup_fault_handler(target=None):
	try:
		import faulthandler
	except ImportError:
		print("Faulthandler not available ...")
		_pre_log_buffer.append('<faulthandler> not available')
		return
	if target is None:
		faulthandler.enable()
		_pre_log_buffer.append('<faulthandler> enabled, target = [console]: %s (%s)' % (faulthandler, faulthandler.__version__))
		return
	_pre_log_buffer.append('<faulthandler> enabled, target = [%s]: %s (%s)' % (target, faulthandler, faulthandler.__version__))
	faulthandler.enable(file = target)

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
def log_startup_info():
	global _pre_log_buffer
	if len(_pre_log_buffer) > 0:
		_log.info('early startup log buffer:')
	for line in _pre_log_buffer:
		_log.info(u' ' + line)
	del _pre_log_buffer
	_log.info(u'GNUmed client version [%s] on branch [%s]', current_client_version, current_client_branch)
	_log.info(u'Platform: %s', platform.uname())
	_log.info((u'Python %s on %s (%s)' % (sys.version, sys.platform, os.name)).replace(u'\n', u'<\\n>'))
	try:
		import lsb_release
		_log.info(u'lsb_release: %s', lsb_release.get_distro_information())
	except ImportError:
		pass
	_log.info('os.getcwd(): [%s]', os.getcwd())
	_log.info('process environment:')
	for key, val in os.environ.items():
		_log.info(u' %s: %s' % (
			(u'${%s}' % key).rjust(30),
			# this won't work in Python3 because that'll be a byte sequence, not a string and thus will need .ENcode
			val.decode(encoding = sys.getfilesystemencoding(), errors = 'replace')
		))

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
		option = u'debug',
		value = val
	)

	val = _cfg.get(option = '--slave', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = u'slave',
		value = val
	)

	val = _cfg.get(option = '--skip-update-check', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = u'skip-update-check',
		value = val
	)

	val = _cfg.get(option = '--hipaa', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = u'hipaa',
		value = val
	)

	val = _cfg.get(option = '--local-import', source_order = [('cli', 'return')])
	if val is None:
		val = False
	_cfg.set_option (
		option = u'local-import',
		value = val
	)

	_cfg.set_option (
		option = u'client_version',
		value = current_client_version
	)

	_cfg.set_option (
		option = u'client_branch',
		value = current_client_branch
	)

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
	gmI18N.install_domain(domain = td, language = l, prefer_local_catalog = _cfg.get(option = u'local-import'))

	# make sure we re-get the default encoding
	# in case it changed
	gmLog2.set_string_encoding()

#==========================================================
def handle_help_request():
	src = [(u'cli', u'return')]

	help_requested = (
		_cfg.get(option = u'--help', source_order = src) or
		_cfg.get(option = u'-h', source_order = src) or
		_cfg.get(option = u'-?', source_order = src)
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
	src = [(u'cli', u'return')]

	version_requested = (
		_cfg.get(option = u'--version', source_order = src) or
		_cfg.get(option = u'-V', source_order = src)
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

	gnumed_DIR_README_TEXT = u"""GNUmed Electronic Medical Record

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
	paths = gmTools.gmPaths(app_name = u'gnumed')
	print("Temp dir:", paths.tmp_dir)

	# ensure there's a user-level config file
	io.open(os.path.expanduser(os.path.join('~', '.gnumed', 'gnumed.conf')), mode = 'a+t').close()

	# symlink log file into temporary directory for easier debugging (everything in one place)
	logfile_link = os.path.join(paths.tmp_dir, 'zzz-gnumed.log')
	gmTools.mklink (gmLog2._logfile.name, logfile_link, overwrite = False)
	print("Linked log file:", logfile_link)

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
	paths = gmTools.gmPaths(app_name = u'gnumed')

	candidates = [
		# the current working dir
		[u'workbase', os.path.join(paths.working_dir, 'gnumed.conf')],
		# /etc/gnumed/
		[u'system', os.path.join(paths.system_config_dir, 'gnumed-client.conf')],
		# ~/.gnumed/
		[u'user', os.path.join(paths.user_config_dir, 'gnumed.conf')],
		# CVS/tgz tree .../gnumed/client/ (IOW a local installation)
		[u'local', os.path.join(paths.local_base_dir, 'gnumed.conf')]
	]
	# --conf-file=
	explicit_fname = _cfg.get(option = u'--conf-file', source_order = [(u'cli', u'return')])
	if explicit_fname is None:
		candidates.append([u'explicit', None])
	else:
		candidates.append([u'explicit', explicit_fname])

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
	fname = u'mime_type2file_extension.conf'
	_cfg.add_file_source (
		source = u'user-mime',
		file = os.path.join(paths.user_config_dir, fname),
		encoding = enc
	)
	_cfg.add_file_source (
		source = u'system-mime',
		file = os.path.join(paths.system_config_dir, fname),
		encoding = enc
	)

#==========================================================
def setup_ui_type():
	global ui_type
	ui_type = _cfg.get(option = u'--ui', source_order = [(u'cli', u'return')])
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
		option = u'database_version',
		value = db_version
	)

	# set up database connection timezone
	timezone = _cfg.get (
		group = u'backend',
		option = 'client timezone',
		source_order = [
			('explicit', 'return'),
			('workbase', 'return'),
			('local', 'return'),
			('user', 'return'),
			('system', 'return')
		]
	)
	if timezone is not None:
		gmPG2.set_default_client_timezone(timezone)

#==========================================================
def run_gui():
	gmHooks.run_hook_script(hook = u'startup-before-GUI')

	if ui_type == u'wxp':
		from Gnumed.wxpython import gmGuiMain
		profile_file = _cfg.get(option = u'--profile', source_order = [(u'cli', u'return')])
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

	gmHooks.run_hook_script(hook = u'shutdown-post-GUI')

	return 0

#==========================================================
def run_tool():
	tool = _cfg.get(option = u'--tool', source_order = [(u'cli', u'return')])
	if tool is None:
		# not running a tool
		return None

	if tool not in _known_tools:
		_log.error(u'unknown tool requested: %s', tool)
		print('GNUmed startup: Unknown tool [%s] requested.' % tool)
		print('GNUmed startup: Known tools: %s' % _known_tools)
		return -1

	print('')
	print('==============================================')
	print('Running tool: %s' % tool)
	print('----------------------------------------------')
	print('')

	if tool == u'check_enc_epi_xref':
		from Gnumed.business import gmEMRStructItems
		return gmEMRStructItems.check_fk_encounter_fk_episode_x_ref()

	if tool == u'export_pat_emr_structure':
		from Gnumed.business import gmEMRStructItems
		return gmEMRStructItems.export_patient_emr_structure()

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

	if _cfg.get(option = u'debug'):
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
if ui_type in [u'web']:
	gmPG2.auto_request_login_params = False
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
