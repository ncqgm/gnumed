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
from the name of the main executing script unless explicitely passed
to install_domain(). Likewise with the language you want to see.

This module searches for message catalog files in 3 main locations:
 - in standard POSIX places (/usr/share/locale/ ...)
 - below "${YOURAPPNAME_DIR}/locale/"
 - below "<directory of binary of your app>/../locale/"

For DOS/Windows I don't know of standard places so probably only the
last option will work. I don't know a thing about classic Mac behaviour.
New Macs are POSIX, of course.

The language you want to see is derived from  environment
variables by the locale system.

@copyright: authors
"""
#===========================================================================
# $Id: gmI18N.py,v 1.25 2006-06-30 14:15:39 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmI18N.py,v $
__version__ = "$Revision: 1.25 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, os.path, os, re, locale, gettext
import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

system_locale = ''
system_locale_level = {}

__tag__ = 'translate this or i18n will not work properly !'

# Q: I can't use non-ascii characters in labels and menus.
# A: This can happen if your Python's sytem encoding is ascii and
#    wxPython is non-unicode. Edit/create the file sitecustomize.py
#    (should be somewhere in your PYTHONPATH), and put these magic lines:
#
#	import sys
#	sys.setdefaultencoding('iso8859-1') # replace with encoding you want to be the default one

#===========================================================================
def __split_locale_into_levels():
	"""Split locale into language, country and variant parts.

	- we have observed the following formats in the wild:
	  - de_DE@euro
	  - ec_CA.UTF-8
	  - en_US:en
	  - German_Germany.1252
	"""
	global system_locale_level
	system_locale_level['full'] = system_locale
	# trim '@<variant>' part
	system_locale_level['country'] = re.split('@|:|\.', system_locale, 1)[0]
	# trim '_<COUNTRY>@<variant>' part
	system_locale_level['language'] = system_locale.split('_', 1)[0]
#---------------------------------------------------------------------------
def __log_locale_settings(message=None):
	_setlocale_categories = {}
	for category in 'LC_ALL LC_CTYPE LC_COLLATE LC_TIME LC_MONETARY LC_MESSAGES LC_NUMERIC'.split():
		try:
			_setlocale_categories[category] = getattr(locale, category)
		except:
			_log.Log(gmLog.lErr, 'this OS does not have locale.%s' % category)

	_getlocale_categories = {}
	for category in 'LC_CTYPE LC_COLLATE LC_TIME LC_MONETARY LC_MESSAGES LC_NUMERIC'.split():
		try:
			_getlocale_categories[category] = getattr(locale, category)
		except:
			_log.Log(gmLog.lErr, 'this OS does not have locale.%s' % category)

	if message is not None:
		_log.Log(gmLog.lData, message)

	_log.Log(gmLog.lData, 'current locale settings:')
	_log.Log(gmLog.lData, 'locale.get_locale(): %s' % str(locale.getlocale()))
	for category in _getlocale_categories.keys():
		_log.Log (gmLog.lData, 'locale.get_locale(%s): %s' % (category, locale.getlocale(_getlocale_categories[category])))

	for category in _setlocale_categories.keys():
		_log.Log (gmLog.lData, '(locale.set_locale(%s): %s)' % (category, locale.setlocale(_setlocale_categories[category])))

	try:
		_log.Log(gmLog.lData, 'locale.getdefaultlocale() - default (user) locale: %s' % str(locale.getdefaultlocale()))
	except ValueError:
		_log.LogException('the OS locale setup seems faulty')

	_log.Log(gmLog.lData, 'locale.getpreferredencoding(): [%s]' % str(locale.getpreferredencoding(do_setlocale=False)))

	_log.Log(gmLog.lData, 'sys.getdefaultencoding(): [%s]' % sys.getdefaultencoding())

	_log.Log(gmLog.lData, 'locale related environment variables (LANG is typically used):')
	for var in 'LANGUAGE LC_ALL LC_CTYPE LANG'.split():
		try:
			_log.Log(gmLog.lData, '${%s}=%s' % (var, os.environ[var]))
		except KeyError:
			_log.Log(gmLog.lData, '${%s} not set' % (var))

	_log.Log(gmLog.lData, 'database of locale conventions:')
	data = locale.localeconv()
	for key in data.keys():
		_log.Log(gmLog.lData, 'locale.localeconv(%s): %s' % (key, data[key]))

	_nl_langinfo_categories = {}
	for category in 'CODESET D_T_FMT D_FMT T_FMT T_FMT_AMPM RADIXCHAR THOUSEP YESEXPR NOEXPR CRNCYSTR ERA ERA_D_T_FMT ERA_D_FMT ALT_DIGITS'.split():
		try:
			_nl_langinfo_categories[category] = getattr(locale, category)
		except:
			_log.Log(gmLog.lErr, 'this OS does not support nl_langinfo category locale.%s' % category)
	try:
		for category in _nl_langinfo_categories.keys():
			_log.Log(gmLog.lData, 'locale.nl_langinfo(%s): %s' % (category, locale.nl_langinfo(_nl_langinfo_categories[category])))
	except:
		_log.LogException('this OS does not support nl_langinfo', sys.exc_info())

#---------------------------------------------------------------------------
def activate_locale():
	"""Get system locale from environment."""
	global system_locale

	# logging state of affairs
	__log_locale_settings('unmodified startup locale settings (should be [C])')

	# activate user-preferred locale
	loc, enc = None, None
	try:
		# check whether already set
		loc, loc_enc = locale.getlocale()
		if loc is None:
			loc = locale.setlocale(locale.LC_ALL, '')
			_log.Log(gmLog.lData, "activating user-default locale with <locale.setlocale(locale.LC_ALL, '')> returns: [%s]" % loc)
		else:
			_log.Log(gmLog.lInfo, 'user-default locale already activated')
		loc, loc_enc = locale.getlocale()
	except AttributeError:
		_log.LogException('Windows does not support locale.LC_ALL', sys.exc_info(), verbose=0)
	except:
		_log.LogException('error activating user-default locale', sys.exc_info(), verbose=0)

	__log_locale_settings('locale settings after activating user-default locale')

	# did we find any locale setting ? assume en_EN if not
	if loc in [None, 'C']:
		_log.Log(gmLog.lErr, 'the current system locale is still [None] or [C], assuming [en_EN]')
		system_locale = "en_EN"
	else:
		system_locale = loc

		py_enc = sys.getdefaultencoding()
		pref_loc_enc = locale.getpreferredencoding(do_setlocale=False)

		if loc_enc is None:
			loc_enc = python_enc

		if (py_enc == 'ascii') or (py_enc != loc_enc):
			_log.Log(gmLog.lInfo, 'Python string encoding (%s) is <ascii> or does not match encoding suggested by locale (%s)' % (py_enc, loc_enc))
			_log.Log(gmLog.lInfo, 'trying to set Python string encoding to [%s]' % loc_enc)
			try:
				sys.setdefaultencoding(loc_enc)
			except AttributeError:
				_log.Log(gmLog.lErr, 'Python string encoding must have been set already')
			except LookupError:
				_log.Log(gmLog.lErr, 'invalid encoding [%s], cannot set Python string encoding' % loc_enc)

	# generate system locale levels
	__split_locale_into_levels()

	# logging state of affairs
	__log_locale_settings('locale settings after trying to set Python string encoding')
#---------------------------------------------------------------------------
def install_domain(text_domain=None, language=None, unicode_flag=0):
	"""Install a text domain suitable for the main script."""

	if unicode_flag not in [0, 1]:
		raise ValueError, '<unicode_flag> cannot be [%s], must be 0 or 1' % unicode_flag

	# text domain directly specified ?
	if text_domain is None:
		# get text domain from name of script
		text_domain = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	_log.Log(gmLog.lInfo, 'text domain is [%s]' % text_domain)

	_log.Log(gmLog.lData, 'searching message catalog file for system locale [%s]' % system_locale)
	for env_var in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
		tmp = os.getenv(env_var)
		if env_var is None:
			_log.Log(gmLog.lData, '${%s} not set' % env_var)
		else:
			_log.Log(gmLog.lData, '${%s} = [%s]' % (env_var, tmp))

	if language is not None:
		_log.Log(gmLog.lInfo, 'explicit setting of ${LANG} requested: [%s]' % language)
		_log.Log(gmLog.lInfo, 'this will override the system locale language setting')
		os.environ['LANG'] = language

	# search for message catalog
	candidates = []
	# 1) try standard places first
	if os.name == 'posix':
		_log.Log(gmLog.lData, 'system is POSIX, looking in standard locations (see Python Manual)')
		# if this is reported to segfault/fail/except on some
		# systems we may have to assume "sys.prefix/share/locale/"
		candidates.append(gettext.bindtextdomain(text_domain))
	else:
		_log.Log(gmLog.lData, 'No use looking in standard POSIX locations - not a POSIX system.')
	# 2) $(<script-name>_DIR)/
	env_key = "%s_DIR" % os.path.splitext(os.path.basename(sys.argv[0]))[0].upper()
	_log.Log(gmLog.lData, 'looking at ${%s}' % env_key)
	if os.environ.has_key(env_key):
		loc_dir = os.path.abspath(os.path.join(os.environ[env_key], 'locale'))
		_log.Log(gmLog.lData, '${%s} = "%s" -> [%s]' % (env_key, os.environ[env_key], loc_dir))
		candidates.append(loc_dir)
	else:
		_log.Log(gmLog.lInfo, "${%s} not set" % env_key)
	# 3) one level above path to binary
	#    last resort for inferior operating systems such as DOS/Windows
	#    strip one directory level
	#    this is a rather neat trick :-)
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'locale'))
	_log.Log(gmLog.lData, 'looking above binary install directory [%s]' % loc_dir)
	candidates.append(loc_dir)
	# 4) in path to binary
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'locale' ))
	_log.Log(gmLog.lData, 'looking in binary install directory [%s]' % loc_dir)
	candidates.append(loc_dir)

	# now try to actually install it
	for candidate in candidates:
		_log.Log(gmLog.lData, 'trying [%s]' % candidate)
		if not os.path.exists(candidate):
			continue
		try:
			gettext.install(text_domain, candidate, unicode=unicode_flag)
		except:
			_log.LogException('installing textdomain [%s] failed from [%s]' % (text_domain, candidate), sys.exc_info(), verbose=0)
			continue
		# does it translate ?
		if _(__tag__) == __tag__:
			_log.Log(gmLog.lData, 'does not translate: [%s] => [%s]' % (__tag__, _(__tag__)))
			continue
		else:
			_log.Log(gmLog.lData, 'found msg catalog: [%s] => [%s]' % (__tag__, _(__tag__)))
			return True

	# 5) install a dummy translation class
	_log.Log(gmLog.lWarn, "Giving up and falling back to NullTranslations() class in despair.")
	# this shouldn't fail
	dummy = gettext.NullTranslations()
	dummy.install()
	return True
#===========================================================================
# Main
#---------------------------------------------------------------------------
if __name__ == "__main__":
	print "======================================================================"
	print __doc__
	print "======================================================================"
	print "authors:", __author__
	print "license:", __license__, "; version:", __version__
	activate_locale()
	print "system locale: ", system_locale, "; levels:", system_locale_level
	install_domain()
	# == do not remove this line =============================
	tmp = _('translate this or i18n will not work properly !')
	# ========================================================

#=====================================================================
# $Log: gmI18N.py,v $
# Revision 1.25  2006-06-30 14:15:39  ncq
# - remove dependancy on gmCLI
# - set unicode_flag, text_domain and language explicitely in install_domain()
#
# Revision 1.24  2006/06/26 21:35:57  ncq
# - improved logging
#
# Revision 1.23  2006/06/20 09:37:33  ncq
# - variable naming error
#
# Revision 1.22  2006/06/19 07:12:05  ncq
# - getlocale() does not support LC_ALL
#
# Revision 1.21  2006/06/19 07:06:13  ncq
# - arch linux cannot locale.get_locale(locale.LC_ALL)  :-(
#
# Revision 1.20  2006/06/17 12:36:40  ncq
# - remove testing cruft
#
# Revision 1.19  2006/06/17 12:25:22  ncq
# - for some extremly strange reason "AttributeError" is not accepted as
#   an exception name in "except AttributeError:"
#
# Revision 1.18  2006/06/17 11:49:26  ncq
# - make locale.LC_* robust against platform diffs
#
# Revision 1.17  2006/06/15 07:55:35  ncq
# - ever better logging of affairs
#
# Revision 1.16  2006/06/14 15:53:17  ncq
# - attempt setting Python string encoding if appears to not be set
#
# Revision 1.15  2006/06/13 20:34:40  ncq
# - now has *explicit* activate_locale() and install_domain()
# - much improved logging
#
# Revision 1.14  2006/06/12 21:41:46  ncq
# - improved locale setting logging
#
# Revision 1.13  2005/10/30 15:50:01  ncq
# - only try to activate user preferred locale if it does not appear
#   to be activated yet, also catch one more exception to make failing
#   locale stuff non-fatal
#
# Revision 1.12  2005/08/18 18:41:48  ncq
# - Windows does not know proper i18n
#
# Revision 1.11  2005/08/18 18:30:57  ncq
# - allow explicit setting of $LANG by --lang-gettext
#
# Revision 1.10  2005/08/18 18:10:52  ncq
# - explicitely dump l10n related env vars as Windows
#   is dumb and needs to be debugged
#
# Revision 1.9  2005/08/06 16:26:50  ncq
# - read locale for messages from LC_MESSAGES, not LC_ALL
#
# Revision 1.8  2005/07/18 09:12:12  ncq
# - make __install_domain more robust
#
# Revision 1.7  2005/04/24 15:48:47  ncq
# - change unicode_flag default to 0
# - add comment on proper fix involving sitecustomize.py
#
# Revision 1.6  2005/03/30 22:08:57  ncq
# - properly handle 0/1 in --unicode-gettext
#
# Revision 1.5  2005/03/29 07:25:39  ncq
# - improve docs
# - add unicode CLI switch to toggle unicode gettext use
# - use std lib locale modules to get system locale
#
# Revision 1.4  2004/06/26 23:06:00  ncq
# - cleanup
# - I checked it, no matter where we import (function-/class-/method-
#   local or globally) it will always only be done once so we can
#   get rid of the semaphore
#
# Revision 1.3  2004/06/25 12:29:13  ncq
# - cleanup
#
# Revision 1.2  2004/06/25 07:11:15  ncq
# - make gmI18N self-aware (eg. remember installing _())
#   so we should be able to safely import gmI18N anywhere
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.29  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.28  2003/06/26 21:34:03  ncq
# - fatal->verbose
#
# Revision 1.27  2003/04/25 08:48:47  ncq
# - refactored, now also take into account different delimiters (see __split_locale*)
#
# Revision 1.26  2003/04/18 09:00:02  ncq
# - assume en_EN for locale if none found
#
# Revision 1.25  2003/03/24 16:52:27  ncq
# - calculate system locale levels at startup
#
# Revision 1.24  2003/02/05 21:27:05  ncq
# - more aptly names a variable
#
# Revision 1.23  2003/02/01 02:42:46  ncq
# - log -> _log to prevent namespace pollution on import
#
# Revision 1.22  2003/02/01 02:39:53  ncq
# - get and remember user's locale
#
# Revision 1.21  2002/12/09 23:39:50  ncq
# - only try standard message catalog locations on true POSIX systems
#   as windows will choke on it
#
# Revision 1.20  2002/11/18 09:41:25  ncq
# - removed magic #! interpreter incantation line to make Debian happy
#
# Revision 1.19  2002/11/17 20:09:10  ncq
# - always display __doc__ when called standalone
#
# Revision 1.18  2002/09/26 13:16:52  ncq
# - log version
#
# Revision 1.17  2002/09/23 02:23:16  ncq
# - comment on why it fails on some version of Windows
#
# Revision 1.16  2002/09/22 18:38:58  ncq
# - added big comment on gmTimeFormat
#
# Revision 1.15  2002/09/10 07:52:29  ncq
# - increased log level of gmTimeFormat
#
# Revision 1.14  2002/09/08 15:57:42  ncq
# - added log cvs keyword
#
