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

import sys, os
import gmLog

if __name__ == "__main__":
	"launch the gnumed wx GUI client "
	appPath = os.path.split(sys.argv[0])[0]

	# log file
	aFile = gmLog.LogTargetFile (os.path.basename(sys.argv[0]) + ".log", "a", gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aFile)

	# console is Good(tm)
	aLogTarget = gmLog.LogTargetConsole(gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aLogTarget)

	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module.')
	gmLog.gmDefLog.Log(gmLog.lInfo, "appPath = " + appPath)

	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		pass

	try:
		import gmGuiMain
	except ImportError:
		gmLog.gmDefLog.Log(gmLog.lPanic, "Cannot load gmGuiMain")
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception caught !", exc)
		sys.exit("CRITICAL ERROR: Can't find module gmGuiMain! - Program halted")

	#run gnumed!
	gmGuiMain.main()
