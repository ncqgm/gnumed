#!/usr/bin/python
#############################################################################
#
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
__version__ = "$Revision: 1.12 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import sys, os
# GNUmed modules
import gmLog
# ---------------------------------------------------------------------------
if __name__ == "__main__":
	"""Launch the gnumed wx GUI client."""
	appPath = os.path.split(os.path.abspath(sys.argv[0]))[0]

	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aLogTarget)

#<DEBUG>
	# log file
	aFile = gmLog.cLogTargetFile (gmLog.lInfo, os.path.basename(sys.argv[0]) + ".log", "a")
	gmLog.gmDefLog.AddTarget(aFile)

	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module.')
	gmLog.gmDefLog.Log(gmLog.lInfo, "appPath = " + appPath)
#</DEBUG>

	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		print "Cannot change into application directory [%s]" % appPath


	try:
		import gmGuiMain
	except ImportError:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Cannot load gmGuiMain", exc)
		sys.exit("CRITICAL ERROR: Can't find module gmGuiMain! - Program halted\n \
		           Please check whether your PYTHONPATH environment variable\n \
			   is set correctly")

	#run gnumed and intercept _all_ exceptions (but reraise them ...)
	try:
	    gmGuiMain.main()
	except:
	    exc = sys.exc_info()
	    gmLog.gmDefLog.LogException ("Exception: Unhandled exception encountered.", exc)
	    raise

#<DEBUG>
	gmLog.gmDefLog.Log(gmLog.lInfo, 'Shutting down as main module.')
#</DEBUG>
