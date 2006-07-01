#!/usr/bin/env python
#===========================================================
# gnumed.py - launcher for the main GNUmed GUI client module
#===========================================================

__doc__ = """
GNUmed
======
This is the launcher for the main GNUmed GUI client. It is
intended to be used as a standalone program.

--quiet
 Be extra quiet and show only _real_ errors in the log.
--debug
 Be extra verbose and report nearly everything that's going
 on. Useful for, well, debugging :-)
--profile=<file>
 Activate profiling and write profile data to <file>.
--talkback
 Run the client and upon exiting run a talkback client where
 you can enter a comment and send the log off to the bug hunters.
 Very useful when used in conjunction with --debug.
--text-domain=<a text domain>
 Set this to change the name of the language file to be loaded.
 Note, this does not change the directory the file is searched in,
 only the name of the file where messages are loaded from. The
 standard textdomain is, of course, "gnumed.mo".
--log-file=<a log file>
 Use this to change the name of the log file.
 See gmLog.py to find out where the standard log file would
 end up.
--conf-file=<file>
 Use configuration file <file> instead of searching for it in
 standard locations.
--unicode-gettext=<0 | 1>
 Use unicode (1) or non-unicode (0) gettext. This is needed for older
 (< 2.5) and non-unicode compiled wx.Widgets/wxPython libraries.
--lang-gettext=<language>
 Explicitely set the language to use in gettext translation. The very
 same effect can be achieved by setting the environment variable $LANG
 from a launcher script.
--override-schema-check
 Continue loading the client even if the database schema version
 and the client software version cannot be verified to be compatible.
--help, -h, or -?
 Show this help.
"""
#==========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
# $Id: gnumed.py,v 1.97 2006-07-01 11:33:52 ncq Exp $
__version__ = "$Revision: 1.97 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = "GPL (details at http://www.gnu.org)"


# standard library
import sys, os, os.path, signal

#==========================================================
# don't run as module
if __name__ != "__main__":
	print "GNUmed startup: This should not be imported as a module !"
	print "---------------------------------------------------------"
	print __doc__
	sys.exit(0)

#==========================================================
# advise not to run as root
if os.name in ['posix'] and os.geteuid() == 0:
	print """
GNUmed startup: GNUmed should not be run as root.
-------------------------------------------------

Running GNUmed as root can potentially put all
your medical data at risk. It is strongly advised
against. Please run GNUmed as a non-root user.
"""
	sys.exit(1)

#==========================================================
# Python 2.3 on Mandrake turns True/False deprecation warnings
# into exceptions, so revert them to warnings again
try:
	import warnings
	warnings.filterwarnings("default", "Use\sPython.s\sFalse\sinstead", DeprecationWarning)
	warnings.filterwarnings("default", "Use\sPython.s\sTrue\sinstead", DeprecationWarning)
except:
	pass

#==========================================================
_log = None
_cfg = None
_email_logger = None
gmLog = None
_old_sig_hup = None
_old_sig_term = None

#==========================================================
def handle_uncaught_exception(t, v, tb):
	print ",========================================================"
	print "| Unhandled exception caught !"
	print "| Type :", t
	print "| Value:", v
	print "`========================================================"
	_log.LogException('unhandled exception caught', (t,v,tb))
	# FIXME: allow user to mail report to developers from here
	sys.__excepthook__(t,v,tb)

#==========================================================
def setup_logging():
	import_error_sermon = """
CRITICAL ERROR: Cannot load GNUmed Python modules ! - Program halted.

Please make sure you have:

- the required third-party Python modules installed
- the GNUmed Python modules installed in site-packages/
- your PYTHONPATH environment variable set up correctly

If you still encounter errors after checking the above
rquirements please ask on the mailing list.
"""
	try:
		from Gnumed.pycommon import gmLog as _gmLog
		from Gnumed.pycommon import gmCLI as _gmCLI
	except ImportError:
		sys.exit(import_error_sermon)

	global gmLog
	gmLog = _gmLog
	global _log
	_log = gmLog.gmDefLog
	global gmCLI
	gmCLI = _gmCLI

	# talkback mode ?
	if gmCLI.has_arg('--talkback'):
		# email logger as a loop device
		global _email_logger
		_email_logger = gmLog.cLogTargetEMail(gmLog.lInfo, aFrom = "GNUmed client", aTo = ("fixme@gnumed.net",), anSMTPServer = "mail.best1-host.com")
		_log.AddTarget (_email_logger)

	# debug level logging ?
	if gmCLI.has_arg("--debug"):
		print "GNUmed startup: Activating verbose log level for debugging."
		_log.SetAllLogLevels(gmLog.lData)
	elif gmCLI.has_arg ("--quiet"):
		_log.SetAllLogLevels(gmLog.lErr)
	else:
		_log.SetAllLogLevels(gmLog.lInfo)

	# Console Is Good(tm)
	# ... but only for Panics and important messages
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lErr)
	_log.AddTarget(aLogTarget)

	return 1
#==========================================================
def setup_locale():
	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()

	td = None
	if gmCLI.has_arg('--text-domain'):
		td = gmCLI.arg['--text-domain']

	l = None
	if gmCLI.has_arg('--lang-gettext'):
		td = gmCLI.arg['--lang-gettext']

	u = 0
	if gmCLI.has_arg('--unicode-gettext'):
		u = int(gmCLI.arg['--unicode-gettext'])

	gmI18N.install_domain(text_domain = td, language = l, unicode_flag = u)

	return True
#==========================================================
def setup_cfg_file():
	from Gnumed.pycommon import gmCfg, gmNull
	if isinstance(gmCfg.gmDefCfgFile, gmNull.cNull):
		if gmCfg.create_default_cfg_file():
			# now that we got the file we can reopen it as a config file :-)
			try:
				f = gmCfg.cCfgFile()
			except:
				print "GNUmed startup: Cannot open or create config file by any means."
				print "GNUmed startup: Please see the log for details."
				_log.LogException('unhandled exception', sys.exc_info(), verbose=0)
				sys.exit(0)
			gmCfg.gmDefCfgFile = f
		else:
			print "GNUmed startup: Cannot open or create config file by any means.\nPlease see the log for details."
			sys.exit(0)
	global _cfg
	_cfg = gmCfg.gmDefCfgFile
#==========================================================
def handle_sig_hup(signum, frame):
	print "SIGHUP caught"
	print signum
	print frame
	if _old_sig_hup in [None, signal.SIG_IGN]:
		sys.exit(signal.SIGHUP)
	else:
		_old_sig_hup(signum, frame)
#----------------------------------------------------------
def handle_sig_term(signum, frame):
	print "SIGTERM caught"
	print signum
	print frame
	if _old_sig_term in [None, signal.SIG_IGN]:
		sys.exit(signal.SIGTERM)
	else:
		_old_sig_term(signum, frame)
#----------------------------------------------------------
def setup_signal_handlers():
	global _old_sig_hup
	old_sig_hup = signal.signal(signal.SIGHUP, handle_sig_hup)
	global _old_sig_term
	old_sig_term = signal.signal(signal.SIGTERM, handle_sig_term)
#==========================================================
def get_resource_dir():
	"""Detect resource directory base.

	1) resource directory defined in config file
	  - this will allow people to start GNUmed from any
	    dir they want on any OS they happen to run
    2) assume /usr/share/gnumed/ as resource dir
	  - this will work on POSIX/LSB systems and may work
	    on Cygwin systems
	  - this is the no-brainer for stock UN*X
    3) finally try one level below path to binary
      - last resort for lesser systems
	  - this is the no-brainer for DOS/Windows
	  - it also allows running from a local CVS copy
	"""
	print "GNUmed startup: Determining GNUmed resource directory ..."
	# config file
	candidate = _cfg.get('client', 'resource directory')
	if candidate not in [None, '']:
		# expand ~/... and ~*/...
		# normalize case
		# connect to / dir
		tmp = os.path.normcase(os.path.abspath(os.path.expanduser(candidate)))
		if os.access(tmp, os.R_OK):
			return tmp
		print "- resource path [%s] not accessible" % tmp
		print '- adjust [client] -> "resource directory"'
		print "  in the config file"
		return None

	# - normalize and convert slashes to local filesystem convention
	tmp = os.path.normcase('/usr/share/gnumed/')
	if os.access(tmp, os.R_OK):
		return tmp

	print '- standard resource path [%s] not accessible' % tmp
	print '- seems like we are running from an arbitrary'
	print '  directory (like a CVS tree or on Windows)'

	# get path to binary
	tmp = os.path.abspath(os.path.dirname(sys.argv[0]))
	# strip one directory level
	# this is a rather neat trick :-)
	tmp = os.path.normpath(os.path.join(tmp, '..'))
	# sanity check (paranoia rulez)
	if os.access(tmp, os.R_OK):
		return tmp

	print '- resource path [%s] not accessible' % tmp
	print ''
	print 'GNUmed startup: Something is really rotten here. We better'
	print 'GNUmed startup: fail gracefully ! Please ask your administrator'
	print 'GNUmed startup: for help.'

	return None
#----------------------------------------------------------
def get_base_dir():
	"""Retrieve the global base directory.

	   The most preferable approach would be to just let
	   the user specify the name of a config file on the
	   command line but for that we'd have to load some
	   non-standard modules already unless we want to
	   duplicate the entire config file infrastructure
	   right here.

	   1) regardless of OS if the environment variable GNUMED_DIR
		  is set this directory will be tried as a base dir
		  - this will allow people to start GNUmed from any dir
		    they want on any OS they happen to run
		  - the variable name has been chosen to be descriptive
		    but still not waste too many resources
	   2) assume /usr/share/gnumed/ as base dir
		  - this will work on POSIX systems and may work on
		    Cygwin systems
		  - this is the no-brainer for stock UN*X
	   3) finally try one level below path to binary
	      - last resort for lesser systems
		  - this is the no-brainer for DOS/Windows
		  - it also allows running from a local CVS copy
	"""
	print "GNUmed startup: Determining GNUmed base directory ..."
	# environment variable
	if os.environ.has_key('GNUMED_DIR'):
		var = os.environ['GNUMED_DIR']
		# - expand '~' and '~user'
		# - expand '$var' and '${var}'
		# - make absolute (normalizes slashes, too)
		# - normalize case
		tmp = os.path.normcase (os.path.abspath (
			os.path.expandvars(os.path.expanduser(var))
		))
		print '- environment variable GNUMED_DIR contains [%s]' % tmp
		print '  this expands to [%s]' % tmp
		# - however, we don't want any random rogue to throw us off
		#   balance so we check whether that's a valid path
		# - note that it may still be the wrong directory
		if os.path.exists(tmp):
			return tmp
		print '  (this is not a valid path, however)'
	else:
		print '- environment variable GNUMED_DIR not set'
		print '  (only necessary if nothing else works, though)'

	# standard POSIX path
	# - only works on POSIX where the given string is a valid path definition
	tmp = '/usr/share/gnumed/'
	# - sanity check
	if os.path.exists(tmp):
		return tmp

	print '- standard path [%s] not accessible' % tmp
	print '- seems like we are running from an arbitrary'
	print '  directory (like a CVS tree or on Windows), namely:'

	# get path to binary
	bin = sys.argv[0]
	tmp = os.path.dirname(os.path.abspath(bin))
	# strip one directory level
	tmp = os.path.normpath(os.path.join(tmp, '..'))
	print '  [%s] -> [%s]' % (bin, tmp)
	# sanity check (paranoia rulez)
	if os.path.exists(tmp):
		return tmp

	print '- application installation path [%s] not accessible' % tmp
	print ''
	print 'GNUmed startup: Something is really rotten here. We better'
	print 'GNUmed startup: fail gracefully ! This may be one of those'
	print 'GNUmed startup: cases where setting GNUMED_DIR might help.'

	return None

#==========================================================
# main - launch the GNUmed wxPython GUI client
#----------------------------------------------------------
# set up top level exception handler
sys.excepthook = handle_uncaught_exception

setup_logging()

setup_locale()

# help requested ?
if gmCLI.has_arg("--help") or gmCLI.has_arg("-h") or gmCLI.has_arg("-?"):
	print _(
		'Help requested'
		'--------------'
	)
	print __doc__
	sys.exit(0)

#setup_signal_handlers()

_log.Log(gmLog.lInfo, 'Starting up as main module (%s).' % __version__)
_log.Log(gmLog.lInfo, 'command line is: %s' % str(gmCLI.arg))
_log.Log(gmLog.lInfo, 'Python %s on %s (%s)' % (sys.version, sys.platform, os.name))

setup_cfg_file()

appPath = get_base_dir()
if appPath is None:
	sys.exit("CRITICAL ERROR: Cannot determine base path.")
_log.Log(gmLog.lData, "old-style resource path: %s" % appPath)

resPath = get_resource_dir()
if resPath is None:
	sys.exit("CRITICAL ERROR: Cannot determine resouce path.")
_log.Log(gmLog.lData, "new-style resource path: %s" % resPath)

# import more of our stuff
from Gnumed.pycommon import gmI18N, gmGuiBroker

gb = gmGuiBroker.GuiBroker()
gb['gnumed_dir'] = appPath
gb['resource dir'] = resPath

# now actually run GNUmed
try:
	from Gnumed.wxpython import gmGuiMain
	# do we do profiling ?
	if gmCLI.has_arg('--profile'):
		profile_file = gmCLI.arg['--profile']
		_log.Log(gmLog.lInfo, 'writing profiling data into %s' % profile_file)
		import profile
		profile.run('gmGuiMain.main()', profile_file)
	else:
		gmGuiMain.main()
# and intercept almost all exceptions
except StandardError:
	exc = sys.exc_info()
	_log.LogException ("Exception: Unhandled exception encountered.", exc, verbose=1)
	if gmCLI.has_arg('--talkback'):
		import gmTalkback
		gmTalkback.run(_email_logger)
	# but reraise them ...
	raise

# do object refcounting
if gmCLI.has_arg('--debug'):
	import types

	def get_refcounts():
		refcount = {}
		# collect all classes
		for module in sys.modules.values():
			for sym in dir(module):
				obj = getattr(module, sym)
				if type(obj) is types.ClassType:
					refcount[obj] = sys.getrefcount(obj)
		# sort by refcount
		pairs = map(lambda x: (x[1],x[0]), refcount.items())
		pairs.sort()
		pairs.reverse()
		return pairs

	rcfile = open('./gm-refcount.lst', 'wb')
#	for refcount, class_ in get_refcounts():
#		if not class_.__name__.startswith('wx'):
#			rcfile.write('%10d %s\n' % (refcount, class_.__name__))
	rcfile.close()

# do we do talkback ?
if gmCLI.has_arg('--talkback'):
	import gmTalkback
	gmTalkback.run(_email_logger)

_log.Log(gmLog.lInfo, 'Normally shutting down as main module.')

#==========================================================
# $Log: gnumed.py,v $
# Revision 1.97  2006-07-01 11:33:52  ncq
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
