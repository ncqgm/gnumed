#!/usr/bin/python

#===========================================================================
# THIS NEEDS TO BE IMPORTED FIRST IN YOUR MODULES !
#===========================================================================

"""GNUmed client internationalization/localization.

All i18n/l10n issues should be handled through this modules.

Theory of operation:

By importing this module a textdomain providing translations is
automatically installed. The translating method gettext.gettext()
is installed into the global (!) namespace as _(). Your own modules thus
need not do _anything_ (not even import gmI18N) to have _() available
to them for translating strings. You need to make sure, however, that
gmI18N is imported in your main module before any of the modules using
it. In order to resolve circular references involving modules that
absolutely _have_ to be imported before this module you can explicitely
import gmI18N into them at the very beginning.

The text domain (i.e. the name of the message catalog file) is derived
from the name of the main executing script unless explicitely given on
the command line like this:
 --text-domain=<your text domain>

This module searches for message catalog files in 3 main locations:
 - in standard POSIX places (/usr/share/locale/ ...)
 - below $GNUMED_DIR
 - below (one level above binary directory)

For DOS/Windows I don't know of standard places so only the last
option will work unless you have CygWin installed. I don't know a
thing about classic Mac behaviour. New Mac's are POSIX, of course.

The language you want to see is derived from the following locale
related environment variables (in this order):
 - LANGUAGE
 - LC_ALL
 - LC_MESSAGES
 - LANG

@license: GPL (details at http://www.gnu.org)
@copyright: author
"""
#---------------------------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmI18N.py,v $
__version__ = "$Revision: 1.4 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
############################################################################

import gettext, getopt, sys, os.path, string
import gmLog
log = gmLog.gmDefLog
#---------------------------------------------------------------------------
def install_domain():
	"""Install a text domain suitable for the main script.
	"""
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
	# 1) try standard places first
	try:
		gettext.install(text_domain)
		return 1
	except IOError:
		# most likely we didn't have a .mo file
		exc = sys.exc_info()
		log.LogException('Cannot install textdomain from standard locations.', exc)

	# 2) $(<script-name>_DIR)/
	env_key = "%s_DIR" % string.upper(os.path.splitext(os.path.basename(sys.argv[0]))[0])
	if os.environ.has_key(env_key):
		loc_dir = os.path.abspath(os.environ(env_key))
		if os.path.exists(loc_dir):
			try:
				gettext.install(text_domain, loc_dir)
				return 1
			except IOError:
				# most likely we didn't have a .mo file
				exc = sys.exc_info()
				log.LogException('Cannot install textdomain from custom location "%s=%s".' % (env_key, loc_dir), exc)
		else:
			log.Log(gmLog.lErr, 'Custom location "%s=%s" does not exist. Cannot install textdomain from there.' % (loc_dir, env_key))
	else:
		log.Log(gmLog.lInfo, "Environment variable %s is not set." % env_key)

	# 3) one level below path to binary
	#    last resort for inferior operating systems such as DOS/Windows
	loc_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
	#    strip one directory level
	#    this is a rather neat trick :-)
	loc_dir = os.path.normpath(os.path.join(loc_dir, '..'))
	#    sanity check (paranoia rulez)
	if os.path.exists(loc_dir):
		try:
			gettext.install(text_domain, loc_dir)
			return 1
		except IOError:
			# most likely we didn't have a .mo file
			exc = sys.exc_info()
			log.LogException('Cannot install textdomain from one level above binary location [%s].' % (loc_dir), exc)
	else:
		# this should not happen at all
		log.Log(gmLog.lWarn, "Huh ? Binary seems to be installed in a non-existant directory (%s) ?!? I'm scared but I'll try to be brave." % (loc_dir))

	# 4) install a dummy translation class
	log.Log(gmLog.lWarn, "Falling back to NullTranslations class in despair.")
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
