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
__version__ = "$Revision: 1.20 $"
__author__  = "H. Herb <hherb@gnumed.net>, K. Hilbert <Karsten.Hilbert@gmx.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import sys, os, gettext
_ = gettext.gettext
# ---------------------------------------------------------------------------
if __name__ == "__main__":
	"""Launch the gnumed wx GUI client."""
	# there has been a lot of confusion about paths
	# NEW RULE 1: nobody, but nobody, queries argv except here
	# NEW RULE 2: no assumptions made about the current directory
	# both of these are due to portability

	# some OS (Windows/DOS) will have the base path set in the environment
	if os.environ.has_key('GNUMED'):
		# Windows or other OS that has set everything
		appPath = os.environ['GNUMED']
	else:
		# Linux, set by home dir
		appPath = os.path.abspath (os.path.split (sys.argv[0])[0])
		# problem: we are in gnumed/client/wxpython, but the base
		# directory is ALWAYS gnumed/client
		# therefor remove "wxpython" from the end of the path
		# FIXME: this is rather ugly in technique
		appPath = appPath[:-9]
		# manually extend our module search path
		sys.path.append(os.path.join(appPath, 'wxpython'))
		sys.path.append(os.path.join(appPath, 'python-common'))
	try:
		import gmLog
		#print "imported gmLog"
		import gmGuiBroker
		#print "imported gui broker"
		import gmGuiMain
		#print "imported gui main"
		import gmI18N
		#print "imported i18n"
	except ImportError:
		exc = sys.exc_info()
		gmLog.gmDefLog.LogException ("Exception: Cannot load gmGuiMain", exc)
		sys.exit("CRITICAL ERROR: Can't find module gmGuiMain! - Program halted\n \
				Please check whether your PYTHONPATH environment variable\n \
				is set correctly")

	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = appPath # EVERYONE must use this!
	#<DEBUG>
	# console is Good(tm)
	aLogTarget = gmLog.cLogTargetConsole(gmLog.lInfo)
	gmLog.gmDefLog.AddTarget(aLogTarget)
	gmLog.gmDefLog.Log(gmLog.lInfo, 'Starting up as main module.')
	gmLog.gmDefLog.Log(gmLog.lInfo, _("set resource path to: ") + appPath)
	#</DEBUG>
	try:
		#change into our working directory
		#this does NOT affect the cdw in the shell from where gnumed is started!
		os.chdir(appPath)
	except:
		print "Cannot change into application directory [%s]" % appPath

	#run gnumed and intercept _all_ exceptions (but reraise them ...)
	try:
	    gmGuiMain.main()
	except:
	    exc = sys.exc_info()
	    gmLog.gmDefLog.LogException ("Exception: Unhandled exception encountered.", exc)
	    raise

#<DEBUG>
#	gmLog.gmDefLog.Log(gmLog.lInfo, 'Shutting down as main module.')
#</DEBUG>
