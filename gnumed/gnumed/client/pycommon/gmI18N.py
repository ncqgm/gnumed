"""GNUmed client internationalization/localization.

All i18n/l10n issues should be handled through this modules.

Theory of operation:

To activate proper locale settings and translation services you need to

- import this module
- call activate_locale()
- call install_domain()

The translating method gettext.gettext() will then be
installed into the global (!) namespace as _(). Your own
modules thus need not do _anything_ (not even import gmI18N)
to have _() available to them for translating strings. You
need to make sure, however, that gmI18N is imported in your
main module before any of the modules using it. In order to
resolve circular references involving modules that
absolutely _have_ to be imported before this module you can
explicitely import gmI18N into them at the very beginning.

The text domain (i.e. the name of the message catalog file)
is derived from the name of the main executing script unless
explicitely passed to install_domain(). The language you
want to translate to is derived from environment variables
by the locale system unless explicitely passed to
install_domain().

This module searches for message catalog files in 3 main locations:

 - standard POSIX places (/usr/share/locale/ ...)
 - below "${YOURAPPNAME_DIR}/locale/"
 - below "<directory of binary of your app>/../locale/"

For DOS/Windows I don't know of standard places so probably
only the last option will work. I don't know a thing about
classic Mac behaviour. New Macs are POSIX, of course.

It will then try to install candidates and *verify* whether
the translation works by checking for the translation of a
tag within itself (this is similar to the self-compiling
compiler inserting a backdoor into its self-compiled
copies).

If none of this works it will fall back to making _() a noop.

@copyright: authors
"""
#===========================================================================
# $Id: gmI18N.py,v 1.37 2007-12-20 13:09:13 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmI18N.py,v $
__version__ = "$Revision: 1.37 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


#stdlib
import sys, os.path, os, re as regex, locale, gettext, logging


_log = logging.getLogger('gm.i18n')
_log.info(__version__)

system_locale = ''
system_locale_level = {}


# **********************************************************
# == do not remove this line ===============================
# it is needed to check for successful installation of
# the desired message catalog
# **********************************************************
__orig_tag__ = u'Translate this or i18n will not work properly !'
# **********************************************************
# **********************************************************

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
	_log.debug('splitting canonical locale [%s] into levels' % system_locale)

	global system_locale_level
	system_locale_level['full'] = system_locale
	# trim '@<variant>' part
	system_locale_level['country'] = regex.split('@|:|\.', system_locale, 1)[0]
	# trim '_<COUNTRY>@<variant>' part
	system_locale_level['language'] = system_locale.split('_', 1)[0]

	_log.debug('system locale levels: %s' % system_locale_level)
#---------------------------------------------------------------------------
def __log_locale_settings(message=None):
	_setlocale_categories = {}
	for category in 'LC_ALL LC_CTYPE LC_COLLATE LC_TIME LC_MONETARY LC_MESSAGES LC_NUMERIC'.split():
		try:
			_setlocale_categories[category] = getattr(locale, category)
		except:
			_log.warning('this OS does not have locale.%s' % category)

	_getlocale_categories = {}
	for category in 'LC_CTYPE LC_COLLATE LC_TIME LC_MONETARY LC_MESSAGES LC_NUMERIC'.split():
		try:
			_getlocale_categories[category] = getattr(locale, category)
		except:
			pass

	if message is not None:
		_log.debug(message)

	_log.debug('current locale settings:')
	_log.debug('locale.get_locale(): %s' % str(locale.getlocale()))
	for category in _getlocale_categories.keys():
		_log.debug('locale.get_locale(%s): %s' % (category, locale.getlocale(_getlocale_categories[category])))

	for category in _setlocale_categories.keys():
		_log.debug('(locale.set_locale(%s): %s)' % (category, locale.setlocale(_setlocale_categories[category])))

	try:
		_log.debug('locale.getdefaultlocale() - default (user) locale: %s' % str(locale.getdefaultlocale()))
	except ValueError:
		_log.exception('the OS locale setup seems faulty')

	_log.debug('encoding sanity check (also check "locale.nl_langinfo(CODESET)" below):')
	pref_loc_enc = locale.getpreferredencoding(do_setlocale=False)
	loc_enc = locale.getlocale()[1]
	py_str_enc = sys.getdefaultencoding()
	sys_fs_enc = sys.getfilesystemencoding()
	_log.debug('sys.getdefaultencoding(): [%s]' % py_str_enc)
	_log.debug('locale.getpreferredencoding(): [%s]' % pref_loc_enc)
	_log.debug('locale.getlocale()[1]: [%s]' % loc_enc)
	_log.debug('sys.getfilesystemencoding(): [%s]' % sys_fs_enc)
	if loc_enc is not None:
		loc_enc = loc_enc.upper()
	if pref_loc_enc.upper() != loc_enc:
		_log.warning('encoding suggested by locale (%s) does not match encoding currently set in locale (%s)' % (pref_loc_enc, loc_enc))
		_log.warning('this might lead to encoding errors')
	import codecs
	for enc in [pref_loc_enc, loc_enc, py_str_enc, sys_fs_enc]:
		if enc is not None:
			try:
				codecs.lookup(enc)
				_log.debug('<codecs> module CAN handle encoding [%s]' % enc)
			except LookupError:
				_log.warning('<codecs> module can NOT handle encoding [%s]' % enc)
	_log.debug('on Linux you can determine a likely candidate for the encoding by running "locale charmap"')

	_log.debug('locale related environment variables (${LANG} is typically used):')
	for var in 'LANGUAGE LC_ALL LC_CTYPE LANG'.split():
		try:
			_log.debug('${%s}=%s' % (var, os.environ[var]))
		except KeyError:
			_log.debug('${%s} not set' % (var))

	_log.debug('database of locale conventions:')
	data = locale.localeconv()
	for key in data.keys():
		if loc_enc is None:
			_log.debug(u'locale.localeconv(%s): %s', key, data[key])
		else:
			try:
				_log.debug(u'locale.localeconv(%s): %s', key, unicode(data[key]))
			except UnicodeDecodeError:
				_log.debug(u'locale.localeconv(%s): %s', key, unicode(data[key], loc_enc))
	_nl_langinfo_categories = {}
	for category in 'CODESET D_T_FMT D_FMT T_FMT T_FMT_AMPM RADIXCHAR THOUSEP YESEXPR NOEXPR CRNCYSTR ERA ERA_D_T_FMT ERA_D_FMT ALT_DIGITS'.split():
		try:
			_nl_langinfo_categories[category] = getattr(locale, category)
		except:
			_log.warning('this OS does not support nl_langinfo category locale.%s' % category)
	try:
		for category in _nl_langinfo_categories.keys():
			if loc_enc is None:
				_log.debug('locale.nl_langinfo(%s): %s' % (category, locale.nl_langinfo(_nl_langinfo_categories[category])))
			else:
				try:
					_log.debug(u'locale.nl_langinfo(%s): %s', category, unicode(locale.nl_langinfo(_nl_langinfo_categories[category])))
				except UnicodeDecodeError:
					_log.debug(u'locale.nl_langinfo(%s): %s', category, unicode(locale.nl_langinfo(_nl_langinfo_categories[category]), loc_enc))
	except:
		_log.exception('this OS does not support nl_langinfo')
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
			_log.debug("activating user-default locale with <locale.setlocale(locale.LC_ALL, '')> returns: [%s]" % loc)
		else:
			_log.info('user-default locale already activated')
		loc, loc_enc = locale.getlocale()
	except AttributeError:
		_log.exception('Windows does not support locale.LC_ALL')
	except:
		_log.exception('error activating user-default locale')

	# logging state of affairs
	__log_locale_settings('locale settings after activating user-default locale')

	# did we find any locale setting ? assume en_EN if not
	if loc in [None, 'C']:
		_log.error('the current system locale is still [None] or [C], assuming [en_EN]')
		system_locale = "en_EN"
	else:
		system_locale = loc

	# generate system locale levels
	__split_locale_into_levels()

	return True
#---------------------------------------------------------------------------
def install_domain(domain=None, language=None):
	"""Install a text domain suitable for the main script."""

	# text domain directly specified ?
	if domain is None:
		# get text domain from name of script
		domain = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	_log.info('text domain is [%s]' % domain)

	_log.debug('searching message catalog file for system locale [%s]' % system_locale)
	for env_var in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
		tmp = os.getenv(env_var)
		if env_var is None:
			_log.debug('${%s} not set' % env_var)
		else:
			_log.debug('${%s} = [%s]' % (env_var, tmp))

	if language is not None:
		_log.info('explicit setting of ${LANG} requested: [%s]' % language)
		_log.info('this will override the system locale language setting')
		os.environ['LANG'] = language

	# search for message catalog
	candidates = []
	# 1) try standard places first
	if os.name == 'posix':
		_log.debug('system is POSIX, looking in standard locations (see Python Manual)')
		# if this is reported to segfault/fail/except on some
		# systems we may have to assume "sys.prefix/share/locale/"
		candidates.append(gettext.bindtextdomain(domain))
	else:
		_log.debug('No use looking in standard POSIX locations - not a POSIX system.')
	# 2) $(<script-name>_DIR)/
	env_key = "%s_DIR" % os.path.splitext(os.path.basename(sys.argv[0]))[0].upper()
	_log.debug('looking at ${%s}' % env_key)
	if os.environ.has_key(env_key):
		loc_dir = os.path.abspath(os.path.join(os.environ[env_key], 'locale'))
		_log.debug('${%s} = "%s" -> [%s]' % (env_key, os.environ[env_key], loc_dir))
		candidates.append(loc_dir)
	else:
		_log.info("${%s} not set" % env_key)
	# 3) one level above path to binary
	#    last resort for inferior operating systems such as DOS/Windows
	#    strip one directory level
	#    this is a rather neat trick :-)
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'locale'))
	_log.debug('looking above binary install directory [%s]' % loc_dir)
	candidates.append(loc_dir)
	# 4) in path to binary
	loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'locale' ))
	_log.debug('looking in binary install directory [%s]' % loc_dir)
	candidates.append(loc_dir)

	# now try to actually install it
	for candidate in candidates:
		_log.debug('trying [%s](/%s/LC_MESSAGES/%s.mo)' % (candidate, system_locale, domain))
		if not os.path.exists(candidate):
			continue
		try:
			gettext.install(domain, candidate, unicode=1)
		except:
			_log.exception('installing text domain [%s] failed from [%s]' % (domain, candidate))
			continue
		# does it translate ?
		if _(__orig_tag__) == __orig_tag__:
			_log.debug('does not translate: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
			continue
		else:
			_log.debug('found msg catalog: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
			return True

	# 5) install a dummy translation class
	_log.warning("Giving up and falling back to NullTranslations() class in despair.")
	# this shouldn't fail
	dummy = gettext.NullTranslations()
	dummy.install()
	return True
#===========================================================================
def get_encoding():
	"""Try to get a sane encoding.

	On MaxOSX locale.setlocale(locale.LC_ALL, '') does not
	have the desired effect. locale.getlocale()[1] still
	returns None. So in that case try to fallback to
	locale.getpreferredencoding().
	"""
	loc = locale.getlocale()[1]
	if loc is not None:
		return loc
	return locale.getpreferredencoding(do_setlocale=False)
#===========================================================================
# Main
#---------------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) > 1 and sys.argv[1] == u'test':

		logging.basicConfig(level = logging.DEBUG)

		print "======================================================================"
		print "GNUmed i18n"
		print ""
		print "authors:", __author__
		print "license:", __license__, "; version:", __version__
		print "======================================================================"
		activate_locale()
		print "system locale: ", system_locale, "; levels:", system_locale_level
		install_domain()
		# ********************************************************
		# == do not remove this line =============================
		# it is needed to check for successful installation of
		# the desired message catalog
		# ********************************************************
		tmp = _('Translate this or i18n will not work properly !')
		# ********************************************************
		# ********************************************************

#=====================================================================
# $Log: gmI18N.py,v $
# Revision 1.37  2007-12-20 13:09:13  ncq
# - improved docs and variable naming
#
# Revision 1.36  2007/12/12 16:18:31  ncq
# - cleanup
# - need to be careful about logging locale settings since
#   they come in the active locale ...
#
# Revision 1.35  2007/12/11 15:36:18  ncq
# - no more gmLog2.py importing
#
# Revision 1.34  2007/12/11 14:27:02  ncq
# - use std logging
#
# Revision 1.33  2007/07/10 20:34:37  ncq
# - in install_domain(): rename text_domain arg to domain
#
# Revision 1.32  2007/04/01 15:20:52  ncq
# - add get_encoding()
# - fix test suite
#
# Revision 1.31  2006/09/01 14:41:22  ncq
# - always use UNICODE gettext
#
# Revision 1.30  2006/07/10 21:44:23  ncq
# - slightly better logging
#
# Revision 1.29  2006/07/04 14:11:29  ncq
# - downgrade some errors to warnings and show them once, only
#
# Revision 1.28  2006/07/01 13:12:14  ncq
# - better logging
#
# Revision 1.27  2006/07/01 11:23:50  ncq
# - one more hint added
#
# Revision 1.26  2006/07/01 09:42:30  ncq
# - ever better logging and handling of encoding
#
# Revision 1.25  2006/06/30 14:15:39  ncq
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
