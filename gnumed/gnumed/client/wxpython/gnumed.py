#!/usr/bin/env python
################################################################
# gnumed - launcher for the main gnumed GUI client module
# --------------------------------------------------------------
#
# @copyright: author
################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.

"""GNUmed
======
This is the launcher for the main GNUmed GUI client. It is
intended to be used as a standalone program.

Command line arguments:

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
--slave=<cookie>
 Start in slave mode for being controlled by other applications.
 This will start an XML-RPC server listening for script commands.
--port=<a port number>
 Which port to listen on if running in slave mode.
--help, -h, or -?
 Well, show this help.

License: GPL (details at http://www.gnu.org)
"""
#==========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
__version__ = "$Revision: 1.67 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import sys, os, os.path

if __name__ != "__main__":
	print "This shouldn't be used as a module !"
	print "------------------------------------"
	print __doc__
	sys.exit(1)
#==========================================================
# Python 2.3 on Mandrake seems to turn True/False deprecation warnings
# into exceptions, so revert them to warnings again
try:
	import warnings
	warnings.filterwarnings("default", "Use\sPython.s\sFalse\sinstead", DeprecationWarning)
	warnings.filterwarnings("default", "Use\sPython.s\sTrue\sinstead", DeprecationWarning)
except:
	pass

import_error_sermon = """
CRITICAL ERROR: Cannot load GnuMed Python modules ! - Program halted.

Please make sure you have:

- the required third-party Python modules installed
- the GnuMed Python modules installed in site-packages/
- your PYTHONPATH environment variable set up correctly

If you still encounter errors after checking the above
rquirements please ask on the mailing list.
"""
_log = None
_cfg = None
_email_logger = None
gmLog = None
#==========================================================
def setup_logging():
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
		_email_logger = gmLog.cLogTargetEMail(gmLog.lInfo, aFrom = "GnuMed client", aTo = ("fixme@gnumed.net",), anSMTPServer = "mail.best1-host.com")
		_log.AddTarget (_email_logger)

	# debug level logging ?
	if gmCLI.has_arg("--debug"):
		print "Activating verbose log level for debugging."
		_log.SetAllLogLevels(gmLog.lData)
	elif gmCLI.has_arg ("--quiet"):
		_log.SetAllLogLevels(gmLog.lErr)
	else:
		_log.SetAllLogLevels(gmLog.lInfo)

	# Console Is Good(tm)
	# ... but only for Panics and important messages
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lPanic)
	_log.AddTarget(aLogTarget)

	return 1
#==========================================================
def setup_cfg_file():
	from Gnumed.pycommon import gmCfg, gmNull
	if isinstance(gmCfg.gmDefCfgFile, gmNull.cNull):
		if gmCfg.create_default_cfg_file():
			# now that we got the file we can reopen it as a config file :-)
			try:
				f = gmCfg.cCfgFile()
			except:
				print "Cannot open or create config file by any means."
				print "Please see the log for details."
				_log.LogException('unhandled exception', sys.exc_info(), verbose=0)
				sys.exit(0)
			gmCfg.gmDefCfgFile = f
		else:
			print "Cannot open or create config file by any means.\nPlease see the log for details."
			sys.exit(0)
	global _cfg
	_cfg = gmCfg.gmDefCfgFile
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
	print "Determining GnuMed resource directory ..."
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
	print 'Something is really rotten here. We better'
	print 'fail gracefully ! Please ask your administrator'
	print 'for help.'

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
	print "Determining GnuMed base directory ..."
	# environment variable
	if os.environ.has_key('GNUMED_DIR'):
		tmp = os.environ['GNUMED_DIR']
		# - however, we don't want any random rogue to throw us off
		#   balance so we check whether that's a valid path,
		# - note that it may still be the wrong directory
		if os.path.exists(tmp):
			return os.path.abspath(tmp)
		print '- environment variable GNUMED_DIR contains [%s]' % tmp
		print '  (this is not a valid path, however)'
	else:
		print '- environment variable GNUMED_DIR not set'
		print '  (only necessary if nothing else works, though)'

	# standard path
	# - normalize and convert slashes to local filesystem convention
	tmp = os.path.normcase('/usr/share/gnumed/')
	# - sanity check
	if os.path.exists(tmp):
		return os.path.abspath(tmp)

	print '- standard path [%s] not accessible' % tmp
	print '- seems like we are running from an arbitrary'
	print '  directory (like a CVS tree or on Windows)'

	# get path to binary
	tmp = os.path.abspath(os.path.dirname(sys.argv[0]))
	# strip one directory level
	# this is a rather neat trick :-)
	tmp = os.path.normpath(os.path.join(tmp, '..'))
	# sanity check (paranoia rulez)
	if os.path.exists(tmp):
		return os.path.abspath(tmp)

	print '- application installation path [%s] not accessible' % tmp
	print ''
	print 'Something is really rotten here. We better'
	print 'fail gracefully ! This may be one of those'
	print 'cases where setting GNUMED_DIR might help.'

	return None

#==========================================================
# main - launch the GnuMed wxPython GUI client
#----------------------------------------------------------
setup_logging()

# help requested ?
if gmCLI.has_arg("--help") or gmCLI.has_arg("-h") or gmCLI.has_arg("-?"):
	print "help requested"
	print "--------------"
	print __doc__
	sys.exit(0)

_log.Log(gmLog.lInfo, 'Starting up as main module (%s).' % __version__)
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

# now actually run gnumed
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
# Revision 1.67  2004-08-16 11:59:10  ncq
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
