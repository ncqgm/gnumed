#!/usr/bin/env python
#############################################################################
# gnumed - launcher for the main gnumed GUI client module
# ---------------------------------------------------------------------------
#
# @copyright: author
############################################################################
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
--help, -h, or -?
 Well, show this help.

License: GPL (details at http://www.gnu.org)
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
__version__ = "$Revision: 1.56 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import sys, os, os.path

# Python 2.3 on Mandrake seems to turn True/False deprecation warnings
# into exceptions, revert them to warnings again
import warnings
warnings.filterwarnings("default", "Use\sPython.s\sFalse\sinstead", DeprecationWarning)
warnings.filterwarnings("default", "Use\sPython.s\sTrue\sinstead", DeprecationWarning)

# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------
if __name__ == "__main__":
	"""Launch the GnuMed wxPython GUI client."""

	appPath = get_base_dir()
	if appPath is None:
		sys.exit("CRITICAL ERROR: Cannot determine base path.")

	# manually extend our module search path
	sys.path.append(os.path.join(appPath, 'wxpython'))
	sys.path.append(os.path.join(appPath, 'python-common'))
	sys.path.append(os.path.join(appPath, 'business'))

	_log = None
	try:
		import gmLog
		_log = gmLog.gmDefLog
		import gmCLI
	except:
		if _log is not None:
			_log.LogException("Cannot import gmCLI.", sys.exc_info(), verbose=1)
		sys.exit("""
CRITICAL ERROR: Can't load gmLog or gmCLI ! - Program halted.

Please check whether your PYTHONPATH environment variable is
set correctly and whether you have all necessary third-party
Python modules installed.

In rare situations it may be necessary to set the GNUMED_DIR
environment variable.

There may also be a log file to check for errors. You
can increase its log level with '--debug'.
""")

	if gmCLI.has_arg('--talkback'):
		# email logger as a loop device
		email_logger = gmLog.cLogTargetEMail(gmLog.lInfo, aFrom = "GnuMed client", aTo = ("fixme@gnumed.net",), anSMTPServer = "mail.best1-host.com")
		_log.AddTarget (email_logger)

	if gmCLI.has_arg("--help") or gmCLI.has_arg("-h") or gmCLI.has_arg("-?"):
		print "help requested"
		print "--------------"
		print __doc__
		sys.exit(0)

	if gmCLI.has_arg("--debug"):
		print "Activating verbose log level for debugging."
		_log.SetAllLogLevels(gmLog.lData)
	elif gmCLI.has_arg ("--quiet"):
		_log.SetAllLogLevels(gmLog.lErr)
	else:
		_log.SetAllLogLevels(gmLog.lInfo)

	# console is Good(tm)
	# ... but only for Panics and important messages
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lPanic)
	_log.AddTarget(aLogTarget)

	_log.Log(gmLog.lInfo, 'Starting up as main module (%s).' % __version__)
	_log.Log(gmLog.lData, "resource path: " + appPath)
	_log.Log(gmLog.lData, "module search path: " + str(sys.path))

	# force import of gmCfg so we can check if we need to create a config file
	import gmCfg
	_cfg = gmCfg.gmDefCfgFile
	if _cfg is None:
		if gmCfg.create_default_cfg_file():
			# now that we got the file we can reopen it as a config file :-)
			try:
				f = gmCfg.cCfgFile()
			except:
				print "Cannot open or create config file by any means.\nPlease see the log for details."
				_log.LogException('unhandled exception', sys.exc_info(), verbose=0)
				raise

			gmCfg.gmDefCfgFile = f
			_cfg = gmCfg.gmDefCfgFile

	try:
		import gmI18N
		import gmGuiBroker
		import gmGuiMain
	except:
		_log.LogException ("Exception: Cannot load modules.", sys.exc_info(), verbose=1)
		sys.exit("""
CRITICAL ERROR: Can't load gmI18N, gmGuiBroker or gmGuiMain !
                Program halted.

Please check whether your PYTHONPATH environment variable is
set correctly and whether you have all necessary third-party
Python modules installed.

In rare situations it may be necessary to set the GNUMED_DIR
environment variable.

Please also make sure to check the log file for errors. You
can increase its log level with '--debug'.
""")

	gb = gmGuiBroker.GuiBroker ()

	gb['gnumed_dir'] = appPath # EVERYONE must use this!

	try:
		# change into our working directory
		# this does NOT affect the cwd in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		exc = sys.exc_info()
		_log.LogException('Exception: cannot change into resource directory ' + appPath, exc, verbose=0)
		# let's try going on anyways

	# run gnumed
	try:
		gmGuiMain.main()
	# and intercept _almost_ all exceptions (but reraise them ...)
	except StandardError:
		exc = sys.exc_info()
		_log.LogException ("Exception: Unhandled exception encountered.", exc, verbose=1)
		if gmCLI.has_arg('--talkback'):
			import gmTalkback
			gmTalkback.run(email_logger)
		raise

	#<DEBUG>
	_log.Log(gmLog.lInfo, 'Normally shutting down as main module.')
	#</DEBUG>

	if gmCLI.has_arg('--talkback'):
		import gmTalkback
		gmTalkback.run(email_logger)

else:
	print "This shouldn't be used as a module !"
	print "------------------------------------"
	print __doc__

#============================================================================
# $Log: gnumed.py,v $
# Revision 1.56  2003-11-17 10:56:39  sjtan
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
