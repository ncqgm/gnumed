#!/usr/bin/python
#---------------------------------------------------------------------------
# THIS NEEDS TO BE IMPORTED FIRST IN YOUR MODULES !
#---------------------------------------------------------------------------
#
# gmI18N - "Internationalisation" helper classes, functions and variables
#          Anything related to language dependency goes here
# --------------------------------------------------------------------------
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gettext, getopt, gmLog
# @change log:
#	25.10.2001 hherb first draft, untested
#	10.07.2002 khilbert converted to class based API, added magic
# @TODO: Almost everything, most prominently translations
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmI18N.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
#---------------------------------------------------------------------------
import gettext, getopt, sys, os.path
import gmLog
log = gmLog.gmDefLog
#---------------------------------------------------------------------------
def install_domain():
	cmd_line = []
	known_opts = []
	text_domain = ""
	# text domain given on command line ?
	# long options only !
	try:
		cmd_line = getopt.getopt(sys.argv[1:], '', ['text-domain=',])
	except getopt.GetoptError:
		log.Log(gmLog.lInfo, "problem parsing command line or --text-domain=<> not given")
		exc = sys.exc_info()
		log.LogException("Non-fatal exception caught:", exc)

	# 1) tuple(cmd_line) -> (known options, junk)
	if len(cmd_line) > 0:
		known_opts = cmd_line[0]
		log.Log(gmLog.lData, 'cmd line is "%s"' % str(cmd_line))
	if len(known_opts) > 0:
		# 2) sequence(known_opt) -> (opt 1, opt 2, ..., opt n)
		first_opt = known_opts[0]
		# 3) tuple(first_opt) -> (option name, option value)
		text_domain = first_opt[1]
	# else get text domain from name of script 
	else:
		text_domain = os.path.splitext(os.path.basename(sys.argv[0]))[0]

	log.Log(gmLog.lInfo, 'text domain is "%s"' % text_domain)

	# now we can install this text domain
	try:
		gettext.install(text_domain)
	except IOError:
		# most likely we didn't have a .mo file
		exc = sys.exc_info()
		log.LogException('Cannot install textdomain "%s". Falling back to NullTranslations class.' % text_domain, exc)
		# and install a dummy translation class
		dummy = gettext.NullTranslations()
		dummy.install()
#---------------------------------------------------------------------------
# Main
#---------------------------------------------------------------------------
if __name__ == "__main__":
	log.SetAllLogLevels(gmLog.lData)
else:
	pass

install_domain()

# we can now safely set up a bunch of variables
gmTimeformat = _("%Y-%m-%d  %H:%M:%S")
log.Log(gmLog.lInfo, 'local time format set to "%s"' % gmTimeformat)
