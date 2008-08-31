#!/usr/bin/env python

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
--profile=<file>
 Activate profiling and write profile data to <file>.
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
 Explicitely set the language to use in gettext translation. The very
 same effect can be achieved by setting the environment variable $LANG
 from a launcher script.
--override-schema-check
 Continue loading the client even if the database schema version
 and the client software version cannot be verified to be compatible.
--local-import
 Adjust the PYTHONPATH such that GNUmed can be run from a local source tree.
--help, -h, or -?
 Show this help.
"""
#==========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
# $Id: gnumed.py,v 1.143 2008-08-31 14:52:58 ncq Exp $
__version__ = "$Revision: 1.143 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = "GPL (details at http://www.gnu.org)"

# standard library
import sys, os, os.path, signal, logging


# do not run as module
if __name__ != "__main__":
	print "GNUmed startup: This is not intended to be imported as a module !"
	print "-----------------------------------------------------------------"
	print __doc__
	sys.exit(1)


# do not run as root
if os.name in ['posix'] and os.geteuid() == 0:
	print """
GNUmed startup: GNUmed should not be run as root.
-------------------------------------------------

Running GNUmed as <root> can potentially put all
your medical data at risk. It is strongly advised
against. Please run GNUmed as a non-root user.
"""
	sys.exit(1)

#----------------------------------------------------------
_log = None
_cfg = None
_old_sig_term = None
_known_short_options = u'h?'
_known_long_options = [
	u'debug',
	u'slave',
	u'profile=',
	u'text-domain=',
	u'log-file=',
	u'conf-file=',
	u'lang-gettext=',
	u'override-schema-check',
	u'local-import',
	u'help'
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

You explicitely specified a configuration file
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
#==========================================================
def setup_python_path():

	if not u'--local-import' in sys.argv:
		return

	print "GNUmed startup: Running from local source tree."
	print "-----------------------------------------------"

	local_python_base_dir = os.path.dirname (
		os.path.abspath(os.path.join(sys.argv[0], '..', '..'))
	)

	# does the path exist at all, physically ?
	# note that broken links are reported as True
	if not os.path.lexists(os.path.join(local_python_base_dir, 'Gnumed')):
		src = os.path.join(local_python_base_dir, 'client')
		dst = os.path.join(local_python_base_dir, 'Gnumed')
		print "Creating module import symlink ..."
		print '', dst, '=>'
		print '    =>', src
		os.symlink(src, dst)

	print "Adjusting PYTHONPATH ..."
	sys.path.insert(0, local_python_base_dir)
#==========================================================
def setup_logging():
	try:
		from Gnumed.pycommon import gmLog2 as _gmLog2
	except ImportError:
		sys.exit(import_error_sermon % '\n '.join(sys.path))

	global gmLog2
	gmLog2 = _gmLog2

	global _log
	_log = logging.getLogger('gm.launcher')
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
#==========================================================
def handle_sig_term(signum, frame):
	_log.critical('SIGTERM (SIG%s) received, shutting down ...' % signum)
	gmLog2.flush()
	print 'GNUmed: SIGTERM (SIG%s) received, shutting down ...' % signum
	if frame is not None:
		print '%s::%s@%s' % (frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno)

	# FIXME: need to do something useful here

	if _old_sig_term in [None, signal.SIG_IGN]:
		sys.exit(signal.SIGTERM)
	else:
		_old_sig_term(signum, frame)
#----------------------------------------------------------
def setup_signal_handlers():
	global _old_sig_term
	old_sig_term = signal.signal(signal.SIGTERM, handle_sig_term)
#==========================================================
#def setup_legacy_logging():
#	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
#==========================================================
def setup_locale():
	gmI18N.activate_locale()
	td = _cfg.get(option = '--text-domain', source_order = [('cli', 'return')])
	l =  _cfg.get(option = '--lang-gettext', source_order = [('cli', 'return')])
	gmI18N.install_domain(domain = td, language = l)

	# make sure we re-get the default encoding
	# in case it changed
	gmLog2.set_string_encoding()
#==========================================================
def check_help_request():
	src = [(u'cli', u'return')]

	help_requested = (
		_cfg.get(option = u'--help', source_order = src) or
		_cfg.get(option = u'-h', source_order = src) or
		_cfg.get(option = u'-?', source_order = src)
	)

	if help_requested:
		print _(
			'Help requested\n'
			'--------------'
		)
		print __doc__
		sys.exit(0)
#==========================================================
def setup_paths_and_files():
	"""Create needed paths in user home directory."""

	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'scripts')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'spellcheck')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', '.gnumed', 'tmp')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'docs')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'xDT')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'EMR')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed', 'xDT')))
	gmTools.mkdir(os.path.expanduser(os.path.join('~', 'gnumed', 'logs')))

	paths = gmTools.gmPaths(app_name = u'gnumed')

	open(os.path.expanduser(os.path.join('~', '.gnumed', 'gnumed.conf')), 'a+').close()
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
			sys.exit(missing_config_file % fname)

	# any config file found at all ?
	found_any_file = False
	for f in _cfg.source_files.values():
		if f is not None:
			found_any_file = True
			break
	if not found_any_file:
		_log.error('no config file found at all')
		sys.exit(no_config_files % '\n '.join(candidates))

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
def setup_backend():
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
def shutdown_backend():
	gmPG2.shutdown()
#==========================================================
def shutdown_logging():

	if _cfg.get(option = u'debug'):
		import types

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

#		rcfile = open('./gm-refcount.lst', 'wb')
#		for refcount, class_ in get_refcounts():
#			if not class_.__name__.startswith('wx'):
#				rcfile.write('%10d %s\n' % (refcount, class_.__name__))
#		rcfile.close()

	# do not choke on Windows
	logging.raiseExceptions = False

#==========================================================
# main - launch the GNUmed wxPython GUI client
#----------------------------------------------------------
setup_python_path()
setup_logging()

_log.info('Starting up as main module (%s).', __version__)
_log.info('Python %s on %s (%s)', sys.version, sys.platform, os.name)

setup_console_exception_handler()
setup_cli()
setup_signal_handlers()

from Gnumed.pycommon import gmI18N, gmTools, gmDateTime, gmHooks

#setup_legacy_logging()
setup_locale()
check_help_request()
setup_paths_and_files()
setup_date_time()
setup_cfg()

from Gnumed.pycommon import gmPG2

setup_backend()


gmHooks.run_hook_script(hook = u'startup-before-GUI')

from Gnumed.wxpython import gmGuiMain
profile_file = _cfg.get(option = u'--profile', source_order = [(u'cli', u'return')])
if profile_file is not None:
	_log.info('writing profiling data into %s', profile_file)
	import profile
	profile.run('gmGuiMain.main()', profile_file)
else:
	gmGuiMain.main()

gmHooks.run_hook_script(hook = u'shutdown-post-GUI')


shutdown_backend()
_log.info('Normally shutting down as main module.')
shutdown_logging()

#==========================================================
# $Log: gnumed.py,v $
# Revision 1.143  2008-08-31 14:52:58  ncq
# - improved error messages
# - streamline setup_cfg and properly handle no --conf-file
# - detect and signal "no conf file at all"
#
# Revision 1.142  2008/08/05 12:47:14  ncq
# - support --local-import
# - some cleanup
#
# Revision 1.141  2008/07/10 21:08:16  ncq
# - call path detection with app name
#
# Revision 1.140  2008/06/11 19:12:13  ncq
# - add a comment
#
# Revision 1.139  2008/05/29 13:32:22  ncq
# - signal handlers cleanup
#
# Revision 1.138  2008/04/13 14:40:17  ncq
# - no old style logging anymore
#
# Revision 1.137  2008/03/06 21:30:49  ncq
# - comment out legacy logging
# - shutdown_backend()
# - shutdown_logging()
#
# Revision 1.136  2008/03/06 18:29:30  ncq
# - standard lib logging only
#
# Revision 1.135  2008/02/25 17:43:40  ncq
# - try suppressing the Python-on-Windows logging bug
#
# Revision 1.134  2008/01/30 14:10:40  ncq
# - cleanup
#
# Revision 1.133  2008/01/14 20:45:45  ncq
# - use set_string_encoding()
#
# Revision 1.132  2008/01/05 22:32:33  ncq
# - setup_backend()
#
# Revision 1.131  2007/12/26 21:06:38  ncq
# - don't use gmTools too early
#
# Revision 1.130  2007/12/26 20:59:41  ncq
# - fix faulty parens
#
# Revision 1.129  2007/12/26 20:53:15  ncq
# - set_option does not take None, so use gmTools.coalesce()
#
# Revision 1.128  2007/12/26 20:18:44  ncq
# - add = to long options where needed
#
# Revision 1.127  2007/12/26 12:36:37  ncq
# - missing :
# - extra or
#
# Revision 1.126  2007/12/23 21:15:26  ncq
# - add setup_backend()
#
# Revision 1.125  2007/12/23 20:56:32  ncq
# - cleanup++
#
# Revision 1.124  2007/12/12 16:26:10  ncq
# - a whole bunch of cleanup, particularly related to logging
#
# Revision 1.123  2007/10/21 20:21:17  ncq
# - no more mandatory global config file
#
# Revision 1.122  2007/09/04 23:30:42  ncq
# - explain --slave
#
# Revision 1.121  2007/08/07 21:42:40  ncq
# - cPaths -> gmPaths
#
# Revision 1.120  2007/07/22 09:28:13  ncq
# - tmp/ now in .gnumed/
#
# Revision 1.119  2007/07/13 09:12:35  ncq
# - setup signal handler
#
# Revision 1.118  2007/05/21 14:49:42  ncq
# - create gnumed/export/EMR/
#
# Revision 1.117  2007/05/08 16:07:00  ncq
# - console exception display handler factored out
# - cleanup
#
# Revision 1.116  2007/05/08 11:16:51  ncq
# - cleanup
#
# Revision 1.115  2007/05/07 12:34:41  ncq
# - better --debug docs
# - cleanup
# - always startup with --debug enabled
#
# Revision 1.114  2007/04/19 13:14:50  ncq
# - init paths
#
# Revision 1.113  2007/04/11 20:47:13  ncq
# - no more 'resource dir' and 'gnumed_dir'
#
# Revision 1.112  2007/03/27 10:29:49  ncq
# - better placement for default word list
#
# Revision 1.111  2007/03/26 14:45:36  ncq
# - cleanup
# - remove --talkback handling (it will be better supported next version)
# - create path gnumed/logs/ at startup
#
# Revision 1.110  2007/03/18 14:11:34  ncq
# - a bit of clenaup/refactoring
# - add hooks before/after GUI
#
# Revision 1.109  2007/03/08 11:54:18  ncq
# - no more ~/.gnumed/user-preferences.conf
#
# Revision 1.108  2007/02/22 17:38:09  ncq
# - add gnumed/export/xDT/
#
# Revision 1.107  2007/01/30 17:50:14  ncq
# - improved doc string
#
# Revision 1.106  2007/01/30 17:41:03  ncq
# - setup needed pathes in home dir of user at startup
#
# Revision 1.105  2006/12/21 17:54:43  ncq
# - init date/time handling early on
#
# Revision 1.104  2006/11/15 00:40:35  ncq
# - if we encounter and unhandled exception we can just as well be verbose
#
# Revision 1.103  2006/09/01 14:47:22  ncq
# - no more --unicode-gettext handling
#
# Revision 1.102  2006/08/08 10:28:30  ncq
# - show sys.path when failing to import GNUmed modules
#
# Revision 1.101  2006/08/08 10:13:01  ncq
# - fix typo
#
# Revision 1.100  2006/08/01 18:49:06  ncq
# - improve wording on failure to load our own modules
#
# Revision 1.99  2006/07/24 19:28:01  ncq
# - fixed variable verwechsling
#
# Revision 1.98  2006/07/01 13:15:04  ncq
# - cleanup
#
# Revision 1.97  2006/07/01 11:33:52  ncq
# - --text-domain/--lang-gettext/--unicode-gettext CLI options
#   must now be provided by gmI18N *importers*
#
# Revision 1.96  2006/06/26 21:38:09  ncq
# - cleanup
#
# Revision 1.95  2006/06/15 21:34:46  ncq
# - log unhandled exceptions, too
#
# Revision 1.94  2006/06/13 20:36:57  ncq
# - use gmI18N only, don't mess with locale ourselves
#
# Revision 1.93  2006/06/06 20:56:24  ncq
# - cleanup
#
# Revision 1.92  2006/05/24 09:56:02  ncq
# - cleanup
# - hook sys.excepthook
#
# Revision 1.91  2005/12/27 19:02:41  ncq
# - document --overide-schema-check
#
# Revision 1.90  2005/12/23 15:43:23  ncq
# - refuse to be run as root
# - exit with status 0 if imported as module
#
# Revision 1.89  2005/12/11 13:31:44  ncq
# - deal with people setting their locale to something they don't have installed
#
# Revision 1.88  2005/10/30 15:53:13  ncq
# - try to be more careful and more precise when setting up the locale
#
# Revision 1.87  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.86  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.85  2005/08/18 18:57:58  ncq
# - document --lang-gettext
#
# Revision 1.84  2005/07/24 11:36:44  ncq
# - cleanup
#
# Revision 1.83  2005/07/23 14:41:13  shilbert
# - locale setup failed on MS Windows
#
# Revision 1.82  2005/07/17 17:22:04  ncq
# - handle path expansion/normalization more carefully to
#   hopefully cope with MS Windows shortcomings
# - be slightly more informative on startup re paths
#
# Revision 1.81  2005/07/16 18:36:35  ncq
# - more careful error catching around locale access
#
# Revision 1.80  2005/07/04 11:27:57  ncq
# - GnuMed -> GNUmed
#
# Revision 1.79  2005/06/29 15:11:05  ncq
# - make startup messages a bit more consistent
#
# Revision 1.78  2005/06/23 15:00:53  ncq
# - log default string encoding
#
# Revision 1.77  2005/04/26 20:02:48  ncq
# - cleanup
#
# Revision 1.76  2005/04/25 17:32:58  ncq
# - entirely comment out setup_locale
#
# Revision 1.75  2005/04/24 14:06:38  ncq
# - commented out a few locale queries that seemed to crash Richard's system ...
#
# Revision 1.74  2005/04/11 18:02:34  ncq
# - initial code to handle signals
#
# Revision 1.73  2005/03/30 22:10:39  ncq
# - even more better logging ...
#
# Revision 1.72  2005/03/29 07:32:36  ncq
# - add --unicode-gettext
# - add setup_locale()
#
# Revision 1.71  2005/02/03 20:35:41  ncq
# - slightly silence the console
#
# Revision 1.70  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.69  2004/09/13 09:31:10  ncq
# - --slave and --port now in config file, remove help
#
# Revision 1.68  2004/09/10 10:40:48  ncq
# - add --conf-file option to --help output
#
# Revision 1.67  2004/08/16 11:59:10  ncq
# - fix existence check for config file (eg. test for Null instance, not None)
#
# Revision 1.66  2004/07/17 11:36:35  ncq
# - comment out refcounting even on normal --debug runs
#
# Revision 1.65  2004/06/26 23:10:18  ncq
# - add object refcounting when --debug
#
# Revision 1.64  2004/06/25 12:31:36  ncq
# - add profiling support via --profile=<file>
#
# Revision 1.63  2004/06/25 08:04:07  ncq
# - missing ) found by epydoc
#
# Revision 1.62  2004/06/23 21:07:26  ncq
# - log Python version, platform type, os name at startup
#
# Revision 1.61  2004/05/11 08:10:27  ncq
# - try: except: the warnings.filterwarnings code as some Pythons don't seem to have it
#
# Revision 1.60  2004/03/25 11:02:37  ncq
# - cleanup
#
# Revision 1.59  2004/03/04 19:45:51  ncq
# - add get_resource_path()
# - reorder main() flow
# - switch to from Gnumed.* import *
#
# Revision 1.58  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.57  2004/02/05 23:52:37  ncq
# - --slave/--port docstring
#
# Revision 1.56  2003/11/17 10:56:39  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.55  2003/06/19 15:29:20  ncq
# - spelling, cleanup
#
# Revision 1.54  2003/06/01 12:28:23  ncq
# - fatal now "verbose" in LogException, use it
#
# Revision 1.53  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.52  2003/04/02 13:31:57  ncq
# - turn Mandrake Python 2.3 True/False DeprecationWarning exceptions back into simple Warnings
#
# Revision 1.51  2003/03/30 00:24:00  ncq
# - typos
# - (hopefully) less confusing printk()s at startup
#
# Revision 1.50  2003/02/08 00:37:49  ncq
# - cleanup, one more module dir
#
# Revision 1.49  2003/02/07 21:06:02  sjtan
#
# refactored edit_area_gen_handler to handler_generator and handler_gen_editarea. New handler for gmSelectPerson
#
# Revision 1.48  2003/02/03 14:29:08  ncq
# - finally fixed that annoying Pseudo error exception.SystemExit on login dialog cancellation
#
# Revision 1.47  2003/01/20 08:25:15  ncq
# - better error messages
#
# Revision 1.46  2003/01/19 13:16:46  ncq
# - better instructions on failing starts
#
# Revision 1.45  2003/01/14 19:36:39  ncq
# - better logging of fatal exceptions
#
# Revision 1.44  2002/11/06 11:52:43  ncq
# - correct misleading printk()s
#
# Revision 1.43  2002/11/04 15:38:59  ncq
# - use helper in gmCfg for config file creation
#
# Revision 1.42  2002/11/03 14:10:15  ncq
# - autocreate empty config file on failing to find one
# - might fail on Windows - untested so far
#
# Revision 1.41  2002/11/03 13:22:20  ncq
# - phase 1: raise log level of console logger to lPanic only
# - gives a lot less confusing output
#
# Revision 1.40  2002/09/08 23:31:09  ncq
# - really fail on failing to load a module
#
# @change log:
#	01.03.2002 hherb first draft, untested
