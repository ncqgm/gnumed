#!/usr/bin/python
#
# Copyright: Horst Herb, Karsten Hilbert
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.
"""
gnumed - launcher for the main gnumed GUI client module
Use as basis for a 'standalone' program.
"""

__version__ = "$Revision: 1.8 $"
__author__ = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import sys, os
# GNUmed modules
import gmLog

def main(argv):
	"""Launch the gnumed wx GUI client.
	arguments: should be sys.argv"""

	appPath = os.path.split(argv[0])[0]

	# console is Good(tm)
	aLogTarget = gmLog.LogTargetConsole(gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aLogTarget)

#<DEBUG>
	# log file
	aFile = gmLog.LogTargetFile (os.path.basename(sys.argv[0]) + ".log", "a", gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aFile)

	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module.')
	gmLog.gmDefLog.Log(gmLog.lInfo, "appPath = " + appPath)
#</DEBUG>

	try:
		#change into our working directory
		#this does NOT affect the cwd in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: \
			Cannot change into application directory [%s]" % appPath, exc)

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


if __name__ == "__main__":
	main(sys.argv)
