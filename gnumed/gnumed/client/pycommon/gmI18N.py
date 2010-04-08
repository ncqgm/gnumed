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
explicitly import gmI18N into them at the very beginning.

The text domain (i.e. the name of the message catalog file)
is derived from the name of the main executing script unless
explicitly passed to install_domain(). The language you
want to translate to is derived from environment variables
by the locale system unless explicitly passed to
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
__version__ = "$Revision: 1.50 $"
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import sys, os.path, os, re as regex, locale, gettext, logging, codecs


_log = logging.getLogger('gm.i18n')
_log.info(__version__)

system_locale = ''
system_locale_level = {}


_translate_original = lambda x:x

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
	_log.debug('splitting canonical locale [%s] into levels', system_locale)

	global system_locale_level
	system_locale_level['full'] = system_locale
	# trim '@<variant>' part
	system_locale_level['country'] = regex.split('@|:|\.', system_locale, 1)[0]
	# trim '_<COUNTRY>@<variant>' part
	system_locale_level['language'] = system_locale.split('_', 1)[0]

	_log.debug('system locale levels: %s', system_locale_level)
#---------------------------------------------------------------------------
def __log_locale_settings(message=None):
	_setlocale_categories = {}
	for category in 'LC_ALL LC_CTYPE LC_COLLATE LC_TIME LC_MONETARY LC_MESSAGES LC_NUMERIC'.split():
		try:
			_setlocale_categories[category] = getattr(locale, category)
		except:
			_log.warning('this OS does not have locale.%s', category)

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
		loc_enc_compare = loc_enc.replace(u'-', u'')
	else:
		loc_enc_compare = loc_enc
	if pref_loc_enc.upper().replace(u'-', u'') != loc_enc_compare:
		_log.warning('encoding suggested by locale (%s) does not match encoding currently set in locale (%s)' % (pref_loc_enc, loc_enc))
		_log.warning('this might lead to encoding errors')
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
def _translate_protected(term):
	"""This wraps _().

	It protects against translation errors such as a different number of "%s".
	"""
	translation = _translate_original(term)

	if translation.count(u'%s') == term.count(u'%s'):
		return translation

	_log.error('count(%s) mismatch, returning untranslated string')
	_log.error('original   : %s', term)
	_log.error('translation: %s', translation)
	return term
#---------------------------------------------------------------------------
# external API
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
def install_domain(domain=None, language=None, prefer_local_catalog=False):
	"""Install a text domain suitable for the main script."""

	# text domain directly specified ?
	if domain is None:
		_log.info('domain not specified, deriving from script name')
		# get text domain from name of script
		domain = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	_log.info('text domain is [%s]' % domain)

	# http://www.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap08.html
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

	# - locally
	if prefer_local_catalog:
		_log.debug('preferring local message catalog')
		# - one level above path to binary
		#    last resort for inferior operating systems such as DOS/Windows
		#    strip one directory level
		#    this is a rather neat trick :-)
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'locale'))
		_log.debug('looking above binary install directory [%s]' % loc_dir)
		candidates.append(loc_dir)
		# - in path to binary
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'locale' ))
		_log.debug('looking in binary install directory [%s]' % loc_dir)
		candidates.append(loc_dir)

	# - standard places
	if os.name == 'posix':
		_log.debug('system is POSIX, looking in standard locations (see Python Manual)')
		# if this is reported to segfault/fail/except on some
		# systems we may have to assume "sys.prefix/share/locale/"
		candidates.append(gettext.bindtextdomain(domain))
	else:
		_log.debug('No use looking in standard POSIX locations - not a POSIX system.')

	# - $(<script-name>_DIR)/
	env_key = "%s_DIR" % os.path.splitext(os.path.basename(sys.argv[0]))[0].upper()
	_log.debug('looking at ${%s}' % env_key)
	if os.environ.has_key(env_key):
		loc_dir = os.path.abspath(os.path.join(os.environ[env_key], 'locale'))
		_log.debug('${%s} = "%s" -> [%s]' % (env_key, os.environ[env_key], loc_dir))
		candidates.append(loc_dir)
	else:
		_log.info("${%s} not set" % env_key)

	# - locally
	if not prefer_local_catalog:
		# - one level above path to binary
		#    last resort for inferior operating systems such as DOS/Windows
		#    strip one directory level
		#    this is a rather neat trick :-)
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'locale'))
		_log.debug('looking above binary install directory [%s]' % loc_dir)
		candidates.append(loc_dir)
		# - in path to binary
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'locale' ))
		_log.debug('looking in binary install directory [%s]' % loc_dir)
		candidates.append(loc_dir)

	# now try to actually install it
	for candidate in candidates:
		_log.debug('trying [%s](/%s/LC_MESSAGES/%s.mo)', candidate, system_locale, domain)
		if not os.path.exists(candidate):
			continue
		try:
			gettext.install(domain, candidate, unicode=1)
		except:
			_log.exception('installing text domain [%s] failed from [%s]', domain, candidate)
			continue
		global _
		# does it translate ?
		if _(__orig_tag__) == __orig_tag__:
			_log.debug('does not translate: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
			continue
		else:
			_log.debug('found msg catalog: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
			import __builtin__
			global _translate_original
			_translate_original = __builtin__._
			__builtin__._ = _translate_protected
			return True

	# 5) install a dummy translation class
	_log.warning("falling back to NullTranslations() class")
	# this shouldn't fail
	dummy = gettext.NullTranslations()
	dummy.install()
	return True
#===========================================================================
_encoding_mismatch_already_logged = False

def get_encoding():
	"""Try to get a sane encoding.

	On MaxOSX locale.setlocale(locale.LC_ALL, '') does not
	have the desired effect, so that locale.getlocale()[1]
	still returns None. So in that case try to fallback to
	locale.getpreferredencoding().

	<sys.getdefaultencoding()>
		- what Python itself uses to convert string <-> unicode
		  when no other encoding was specified
		- ascii by default
		- can be set in site.py and sitecustomize.py
	<locale.getpreferredencoding()>
		- what the current locale would *recommend* using
		  as the encoding for text conversion
	<locale.getlocale()[1]>
		- what the current locale is *actually* using
		  as the encoding for text conversion
	"""
	enc = sys.getdefaultencoding()
	if enc != 'ascii':
		return enc
	enc = locale.getlocale()[1]
	if enc is not None:
		return enc
	global _encoding_mismatch_already_logged
	if not _encoding_mismatch_already_logged:
		_log.debug('*actual* encoding of locale is None, using encoding *recommended* by locale')
		_encoding_mismatch_already_logged = True
	return locale.getpreferredencoding(do_setlocale=False)
#===========================================================================
# Main
#---------------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	logging.basicConfig(level = logging.DEBUG)

	print "======================================================================"
	print "GNUmed i18n"
	print ""
	print "authors:", __author__
	print "license:", __license__, "; version:", __version__
	print "======================================================================"

	activate_locale()
	print "system locale: ", system_locale, "; levels:", system_locale_level
	print "likely encoding:", get_encoding()

	if len(sys.argv) > 1:
		install_domain(domain = sys.argv[2])
	else:
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

