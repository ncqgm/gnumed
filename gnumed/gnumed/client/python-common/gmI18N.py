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
 - below $GNUMED_DIR/locale/
 - below (one level above binary directory)/locale/

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
__version__ = "$Revision: 1.16 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
############################################################################

import gettext, sys, os.path, string
import gmLog, gmCLI
log = gmLog.gmDefLog
#---------------------------------------------------------------------------
def install_domain():
	"""Install a text domain suitable for the main script.
	"""
	text_domain = ""
	# text domain given on command line ?
	if gmCLI.has_arg('--text-domain'):
		text_domain = gmCLI.arg['--text-domain']
	# else get text domain from name of script 
	else:
		text_domain = os.path.splitext(os.path.basename(sys.argv[0]))[0]

	log.Log(gmLog.lInfo, 'text domain is "%s"' % text_domain)

	# explicitely probe user locale settings
	env_key = 'LANGUAGE'
	if os.environ.has_key(env_key):
		log.Log(gmLog.lData, '$(%s) is set to "%s"' % (env_key, os.environ[env_key]))
	else:
		log.Log(gmLog.lData, '$(%s) is not set' % (env_key))

	env_key = 'LC_ALL'
	if os.environ.has_key(env_key):
		log.Log(gmLog.lData, '$(%s) is set to "%s"' % (env_key, os.environ[env_key]))
	else:
		log.Log(gmLog.lData, '$(%s) is not set' % (env_key))

	env_key = 'LC_MESSAGES'
	if os.environ.has_key(env_key):
		log.Log(gmLog.lData, '$(%s) is set to "%s"' % (env_key, os.environ[env_key]))
	else:
		log.Log(gmLog.lData, '$(%s) is not set' % (env_key))

	env_key = 'LANG'
	if os.environ.has_key(env_key):
		log.Log(gmLog.lData, '$(%s) is set to "%s"' % (env_key, os.environ[env_key]))
	else:
		log.Log(gmLog.lData, '$(%s) is not set' % (env_key))

	log.Log(gmLog.lData, 'Searching message catalog file.')
	# now we can install this text domain
	# 1) try standard places first
	log.Log(gmLog.lData, 'Looking in standard POSIX locations (see Python Manual).')
	try:
		gettext.install(text_domain)
		log.Log(gmLog.lData, 'Found message catalog.')
		return 1
	except IOError:
		# most likely we didn't have a .mo file
		exc = sys.exc_info()
		log.LogException('Cannot install textdomain from standard POSIX locations.', exc, fatal=0)

	# 2) $(<script-name>_DIR)/
	env_key = "%s_DIR" % string.upper(os.path.splitext(os.path.basename(sys.argv[0]))[0])
	log.Log(gmLog.lData, 'Looking behind environment variable $(%s).' % env_key)
	if os.environ.has_key(env_key):
		loc_dir = os.path.abspath(os.path.join(os.environ[env_key], "locale"))
		log.Log(gmLog.lData, '$(%s) = "%s" -> [%s]' % (env_key, os.environ[env_key], loc_dir))
		if os.path.exists(loc_dir):
			try:
				gettext.install(text_domain, loc_dir)
				log.Log(gmLog.lData, 'Found message catalog.')
				return 1
			except IOError:
				# most likely we didn't have a .mo file
				exc = sys.exc_info()
				log.LogException('Cannot install textdomain from custom location [%s].' % (loc_dir), exc)
		else:
			log.Log(gmLog.lWarn, 'Custom location [%s] does not exist. Cannot install textdomain from there.' % (loc_dir))
	else:
		log.Log(gmLog.lInfo, "Environment variable %s is not set." % env_key)

	# 3) one level below path to binary
	#    last resort for inferior operating systems such as DOS/Windows
	#    strip one directory level
	#    this is a rather neat trick :-)
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'locale'))
	log.Log(gmLog.lData, 'Looking in application level directory [%s].' % loc_dir)
	#    sanity check (paranoia rulez)
	if os.path.exists(loc_dir):
		try:
			gettext.install(text_domain, loc_dir)
			log.Log(gmLog.lData, 'Found message catalog.')
			return 1
		except IOError:
			# most likely we didn't have a .mo file
			exc = sys.exc_info()
			log.LogException('Cannot install textdomain from one level above binary location [%s].' % (loc_dir), exc, 0)
	else:
		log.Log(gmLog.lWarn, "The application level locale directory [%s] does not exist. Cannot install textdomain from there." % (loc_dir))

	# 4) in path to binary
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'locale' ))
	log.Log(gmLog.lData, 'Looking in application level directory [%s].' % loc_dir)
	#    sanity check (paranoia rulez)
	if os.path.exists(loc_dir):
		try:
			gettext.install(text_domain, loc_dir)
			log.Log(gmLog.lData, 'Found message catalog.')
			return 1
		except IOError:
			# most likely we didn't have a .mo file
			exc = sys.exc_info()
			log.LogException('Cannot install textdomain from within path to binary [%s].' % (loc_dir), exc, 0)
	else:
		log.Log(gmLog.lWarn, "The application level locale directory [%s] does not exist. Cannot install textdomain from there." % (loc_dir))

	# 5) install a dummy translation class
	log.Log(gmLog.lWarn, "Giving up and falling back to NullTranslations() class in despair.")
	# this shouldn't fail
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

# gmTimeFormat is used to define a standard way of
# displaying a date as a string,
# this is marked for translation by _(),
# this way this variable can be used as a crude
# means of date formatting localization
gmTimeformat = _("%Y-%m-%d  %H:%M:%S")

log.Log(gmLog.lData, 'local time format set to "%s"' % gmTimeformat)

#=====================================================================
# $Log: gmI18N.py,v $
# Revision 1.16  2002-09-22 18:38:58  ncq
# - added big comment on gmTimeFormat
#
# Revision 1.15  2002/09/10 07:52:29  ncq
# - increased log level of gmTimeFormat
#
# Revision 1.14  2002/09/08 15:57:42  ncq
# - added log cvs keyword
#
