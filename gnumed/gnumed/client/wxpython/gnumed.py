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

if __name__ == "__main__":
	"launch the gnumed wx GUI client "
	appPath = ''
	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		appPath = os.path.split(sys.argv[0])[0]
		os.chdir(appPath)
	except:
		pass

	try:
		import gmGuiMain
	except:
		print "CRITICAL ERROR: Can't find module gmGuiMain! - Program halted"

	#run gnumed!
	gmGuiMain.main()


