#!/usr/bin/python
#############################################################################
# gnumed - launcher for the main gnumed GUI client module
# ---------------------------------------------------------------------------
#
# @copyright: author
# @dependencies:
# @change log:
#	01.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
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
--text-domain=<a_text_domain>
 Set this to change the name of the language file to be loaded.
 Note, this does not change the directory the file is searched in,
 only the name of the file where messages are loaded from. The
 standard textdomain is, of course, "gnumed.mo".
--log-file=<a_log_file>
 Use this to change the name of the log file.
 See gmLog.py to find out where the standard log file would
 end up.
--help, -h, or -?
 Well, show this help.

License: GPL (details at http://www.gnu.org)
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
__version__ = "$Revision: 1.41 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import sys, os, os.path
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
	# environment variable
	if os.environ.has_key('GNUMED_DIR'):
		tmp = os.environ['GNUMED_DIR']
	else:
		tmp = ""
	# however, we don't want any random rogue to throw us off
	# balance so we check whether that's a valid path,
	# note that it may still be the wrong directory
	if os.path.exists(tmp):
		return os.path.abspath(tmp)

	print 'Environment variable GNUMED_DIR contains "%s".' % tmp
	print 'This is not a valid path, however.'
	print 'Trying to fall back to system defaults.'

	# standard path
	# - normalize and convert slahes to local filesystem convention
	tmp = os.path.normcase('/usr/share/gnumed/')
	# sanity check
	if os.path.exists(tmp):
		return os.path.abspath(tmp)

	print 'Standard path "%s" does not exist.' % tmp
	print 'Desperately trying to fall back to last resort measures.'
	print 'This may be an indicator we are running Windows or something.'

	# one level below path to binary
	tmp = os.path.abspath(os.path.dirname(sys.argv[0]))
	# strip one directory level
	# this is a rather neat trick :-)
	tmp = os.path.normpath(os.path.join(tmp, '..'))
	# sanity check (paranoia rulez)
	if os.path.exists(tmp):
		return os.path.abspath(tmp)

	print 'Cannot verify path one level below path to binary (%s).' % tmp
	print 'Something is really rotten here. We better fail gracefully.'
	return None
# ---------------------------------------------------------------------------
if __name__ == "__main__":
	"""Launch the gnumed wx GUI client."""

	appPath = get_base_dir()
	if appPath == None:
		sys.exit("CRITICAL ERROR: Cannot determine base path.")

	# manually extend our module search path
	sys.path.append(os.path.join(appPath, 'wxpython'))
	sys.path.append(os.path.join(appPath, 'python-common'))

	try:
		import gmLog
		import gmCLI
	except ImportError:
		sys.exit("CRITICAL ERROR: Can't load gmLog or gmCLI ! - Program halted.\n \
				  Please check whether your PYTHONPATH and/or GNUMED_DIR environment\n \
				  variables are set correctly.")

	if gmCLI.has_arg('--talkback'):
		# email logger as a loop device
		email_logger = gmLog.cLogTargetEMail(gmLog.lInfo, aFrom = "GNUmed client", aTo = ("fixme@gnumed.net",), anSMTPServer = "mail.best1-host.com")
		gmLog.gmDefLog.AddTarget (email_logger)

	if gmCLI.has_arg("--help") or gmCLI.has_arg("-h") or gmCLI.has_arg("-?"):
		print "help requested"
		print "--------------"
		print __doc__
		sys.exit(0)

	if gmCLI.has_arg("--debug"):
		print "Activating verbose output for debugging."
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
	elif gmCLI.has_arg ("--quiet"):
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lErr)
	else:
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lInfo)

	# console is Good(tm)
	# but only for Panics and important messages
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lPanic)
	gmLog.gmDefLog.AddTarget(aLogTarget)


	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module (%s).' % __version__)
	gmLog.gmDefLog.Log(gmLog.lData, "resource path: " + appPath)
	gmLog.gmDefLog.Log(gmLog.lData, "module search path: " + str(sys.path))

	try:
		import gmI18N
		import gmGuiBroker
		import gmGuiMain
	except ImportError:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Cannot load modules.", exc)
		sys.exit("CRITICAL ERROR: Can't load gmI18N, gmGuiBroker or gmGuiMain ! - Program halted.\n \
				  Please check whether your PYTHONPATH and/or GNUMED_DIR environment\n \
				  variables are set correctly.")

	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = appPath # EVERYONE must use this!

	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException('Exception: cannot change into resource directory ' + appPath, exc, fatal=0)
		# let's try going on anyways

	# run gnumed and intercept _all_ exceptions (but reraise them ...)
	try:
		gmGuiMain.main()
	except:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Unhandled exception encountered.", exc, fatal=0)
		if gmCLI.has_arg('--talkback'):
			import gmTalkback
			gmTalkback.run(email_logger)
		raise

	#<DEBUG>
	gmLog.gmDefLog.Log(gmLog.lInfo, 'Normally shutting down as main module.')
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
# Revision 1.41  2002-11-03 13:22:20  ncq
# - phase 1: raise log level of console logger to lPanic only
# - gives a lot less confusing output
#
# Revision 1.40  2002/09/08 23:31:09  ncq
# - really fail on failing to load a module
#
