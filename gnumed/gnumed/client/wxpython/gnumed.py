#!/usr/bin/python
#############################################################################
# gnumed - launcher for the main gnumed GUI client module
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	01.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.
"""
gnumed - launcher for the main gnumed GUI client module
Use as standalone program.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gnumed.py,v $
__version__ = "$Revision: 1.33 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import sys, os, os.path, getopt
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
	# - normalize and convert slahes to fs local convention
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
def call_main():
	"""Call the appropriate main().
	"""
	# long options only !
	cmd_line = []
	try:
		cmd_line = getopt.getopt(sys.argv[1:], '', ['talkback',])
	except getopt.GetoptError:
		pass

	# 1) tuple(cmd_line) -> (known options, junk)
	known_opts = []
	if len(cmd_line) > 0:
		known_opts = cmd_line[0]

	if len(known_opts) > 0:
		with_email_log = 1
	else:
		with_email_log = 0

	# run gnumed and intercept _all_ exceptions (but reraise them ...)
	try:
		if with_email_log:
			gmGuiMain.main_with_talkback()
		else:
			gmGuiMain.main()
	except:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Unhandled exception encountered.", exc)
		raise
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
	except ImportError:
		sys.exit("CRITICAL ERROR: Can't load gmLog ! - Program halted.\n \
				  Please check whether your PYTHONPATH and/or GNUMED_DIR environment\n \
				  variables are set correctly.")

	# long options only !
	cmd_line = []
	try:
		cmd_line = getopt.getopt(sys.argv[1:], '', ['debug',])
	except getopt.GetoptError:
		pass

	# 1) tuple(cmd_line) -> (known options, junk)
	known_opts = []
	if len(cmd_line) > 0:
		known_opts = cmd_line[0]

	if len(known_opts) > 0:
		# know everything in debugging versions
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
		print "debug"
	else:
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lInfo)
		print "no debug"

	#<DEBUG>
	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aLogTarget)
	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module (%s).' % __version__)
	#</DEBUG>

	gmLog.gmDefLog.Log(gmLog.lData, "resource path: " + appPath)
	gmLog.gmDefLog.Log(gmLog.lData, "module search path: " + str(sys.path))

	try:
		import gmI18N
		import gmGuiBroker
		import gmGuiMain
	except ImportError:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Cannot load modules.", exc)
		sys.exit("CRITICAL ERROR: Can't find modules to load ! - Program halted.\n \
				  Please check whether your PYTHONPATH and/or GNUMED_DIR environment variables\n \
				  are set correctly.")

	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = appPath # EVERYONE must use this!

	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException('Exception: cannot change into resource directory ' + appPath, exc)
		# let's try going on anyways

	# now go do the stuff
	call_main()

	#<DEBUG>
	gmLog.gmDefLog.Log(gmLog.lInfo, 'Shutting down as main module.')
	#</DEBUG>

else:
	print "Nothing useful here."
