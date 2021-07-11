__doc__ = """GNUmed client internationalization/localization.

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
 - below "${YOURAPPNAME_DIR}/po/"
 - below "<directory of binary of your app>/../po/"

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
__author__ = "H. Herb <hherb@gnumed.net>, I. Haywood <i.haywood@ugrad.unimelb.edu.au>, K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"


# stdlib
import sys
import os.path
import os
import locale
import gettext
import logging
import codecs
import builtins
import re as regex


builtins._ = lambda x:x

_log = logging.getLogger('gm.i18n')

system_locale = ''
system_locale_level = {}

_translate_via_gettext = lambda x:x
_substitutes_regex = regex.compile(r'%\(.+?\)s')

# ***************************************************************************
# ***************************************************************************
# The following line is needed to check for successful
# installation of the desired message catalog.
# -- do not remove or change this line --------------------------------------
__orig_tag__ = 'Translate this or i18n into <en_EN> will not work properly !'
# ***************************************************************************
# ***************************************************************************

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
	for category in 'LC_ALL LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION'.split():
		try:
			_setlocale_categories[category] = getattr(locale, category)
		except Exception:
			_log.warning('this OS does not have locale.%s', category)
	_getlocale_categories = {}
	for category in 'LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION'.split():
		try:
			_getlocale_categories[category] = getattr(locale, category)
		except Exception:
			pass
	if message is not None:
		_log.debug(message)

	_log.debug('current locale settings:')
	_log.debug('locale.getlocale(): %s' % str(locale.getlocale()))
	for category in _getlocale_categories:
		_log.debug('locale.getlocale(%s): %s' % (category, locale.getlocale(_getlocale_categories[category])))
	for category in _setlocale_categories:
		_log.debug('(locale.setlocale(%s): %s)' % (category, locale.setlocale(_setlocale_categories[category])))
	try:
		_log.debug('locale.getdefaultlocale() - default (user) locale: %s' % str(locale.getdefaultlocale()))
	except ValueError:
		_log.exception('the OS locale setup seems faulty')

	_log.debug('encoding sanity check (also check "locale.nl_langinfo(CODESET)" below):')
	pref_loc_enc = locale.getpreferredencoding(do_setlocale = False)
	loc_enc = locale.getlocale()[1]
	py_str_enc = sys.getdefaultencoding()
	sys_fs_enc = sys.getfilesystemencoding()
	_log.debug('sys.getdefaultencoding(): [%s]' % py_str_enc)
	_log.debug('locale.getpreferredencoding(): [%s]' % pref_loc_enc)
	_log.debug('locale.getlocale()[1]: [%s]' % loc_enc)
	_log.debug('sys.getfilesystemencoding(): [%s]' % sys_fs_enc)
	if loc_enc is not None:
		loc_enc = loc_enc.upper()
		loc_enc_compare = loc_enc.replace('-', '')
	else:
		loc_enc_compare = loc_enc
	if pref_loc_enc.upper().replace('-', '') != loc_enc_compare:
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
	for key in data:
		if loc_enc is None:
			_log.debug('locale.localeconv(%s): %s', key, data[key])
		else:
			try:
				_log.debug('locale.localeconv(%s): %s', key, str(data[key]))
			except UnicodeDecodeError:
				_log.debug('locale.localeconv(%s): %s', key, str(data[key], loc_enc))
	_nl_langinfo_categories = {}
	for category in 'CODESET D_T_FMT D_FMT T_FMT T_FMT_AMPM RADIXCHAR THOUSEP YESEXPR NOEXPR CRNCYSTR ERA ERA_D_T_FMT ERA_D_FMT ALT_DIGITS'.split():
		try:
			_nl_langinfo_categories[category] = getattr(locale, category)
		except Exception:
			_log.warning('this OS does not support nl_langinfo category locale.%s' % category)
	try:
		for category in _nl_langinfo_categories:
			if loc_enc is None:
				_log.debug('locale.nl_langinfo(%s): %s' % (category, locale.nl_langinfo(_nl_langinfo_categories[category])))
			else:
				try:
					_log.debug('locale.nl_langinfo(%s): %s', category, str(locale.nl_langinfo(_nl_langinfo_categories[category])))
				except UnicodeDecodeError:
					_log.debug('locale.nl_langinfo(%s): %s', category, str(locale.nl_langinfo(_nl_langinfo_categories[category]), loc_enc))
	except Exception:
		_log.exception('this OS does not support nl_langinfo')

	_log.debug('gmI18N.get_encoding(): %s', get_encoding())

#---------------------------------------------------------------------------
def _translate_safely(term):
	"""This wraps _().

	It protects against translation errors such as a different number of "%s".
	"""
	translation = _translate_via_gettext(term)

	# different number of %s substitutes ?
	if translation.count('%s') != term.count('%s'):
		_log.error('count("%s") mismatch, returning untranslated string')
		_log.error('original   : %s', term)
		_log.error('translation: %s', translation)
		return term

	substitution_keys_in_original = set(_substitutes_regex.findall(term))
	substitution_keys_in_translation = set(_substitutes_regex.findall(translation))

	if not substitution_keys_in_translation.issubset(substitution_keys_in_original):
		_log.error('"%(...)s" keys in translation not a subset of keys in original, returning untranslated string')
		_log.error('original   : %s', term)
		_log.error('translation: %s', translation)
		return term

	return translation

#---------------------------------------------------------------------------
# external API
#---------------------------------------------------------------------------
def activate_locale():
	"""Get system locale from environment."""
	global system_locale
	__log_locale_settings('unmodified startup locale settings (could be [C])')
	loc, enc = None, None
	# activate user-preferred locale
	try:
		loc = locale.setlocale(locale.LC_ALL, '')
		_log.debug("activating user-default locale with <locale.setlocale(locale.LC_ALL, '')> returns: [%s]" % loc)
	except AttributeError:
		_log.exception('Windows does not support locale.LC_ALL')
	except Exception:
		_log.exception('error activating user-default locale')
		_log.log_stack_trace()
	__log_locale_settings('locale settings after activating user-default locale')
	# assume en_EN if we did not find any locale settings
	if loc in [None, 'C']:
		_log.error('the current system locale is still [None] or [C], falling back to [en_EN]')
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
	_log.debug('checking process environment:')
	for env_var in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
		tmp = os.getenv(env_var)
		if env_var is None:
			_log.debug(' ${%s} not set' % env_var)
		else:
			_log.debug(' ${%s} = [%s]' % (env_var, tmp))
	# language codes to try
	lang_candidates = []
	# first: explicit language or default system language
	# language=None: unadulterated default language for user (locale.getlocale()[0] value)
	# language != None: explicit language setting as passed in by the caller
	lang_candidates.append(language)
	if language is not None:
		_log.info('explicit request for target language [%s]' % language)
		# next: try default language for user if explicit language fails
		lang_candidates.append(None)
	# next try locale.getlocale()[0], if different (this can be strange on, say, Windows: Hungarian_Hungary)
	if locale.getlocale()[0] not in lang_candidates:
		lang_candidates.append(locale.getlocale()[0])
	# next try locale.get*default*locale()[0], if different
	if locale.getdefaultlocale()[0] not in lang_candidates:
		lang_candidates.append(locale.getdefaultlocale()[0])
	_log.debug('languages to try for translation: %s (None: implicit system default)', lang_candidates)
	initial_lang = os.getenv('LANG')
	_log.info('initial ${LANG} setting: %s', initial_lang)
	# loop over language candidates
	for lang_candidate in lang_candidates:
		# setup baseline
		_log.debug('resetting ${LANG} to initial user default [%s]', initial_lang)
		if initial_lang is None:
			del os.environ['LANG']
			lang2log = '$LANG=<>'
		else:
			os.environ['LANG'] = initial_lang
			lang2log = '$LANG(default)=%s' % initial_lang
		# setup candidate language
		if lang_candidate is not None:
			_log.info('explicitely overriding system locale language [%s] by setting ${LANG} to [%s]', initial_lang, lang_candidate)
			os.environ['LANG'] = lang_candidate
			lang2log = '$LANG(explicit)=%s' % lang_candidate
		if __install_domain(domain = domain, prefer_local_catalog = prefer_local_catalog, language = lang2log):
			return True

	# install a dummy translation class
	_log.warning("falling back to NullTranslations() class")
	# this shouldn't fail
	dummy = gettext.NullTranslations()
	dummy.install()
	return True

#---------------------------------------------------------------------------
def __install_domain(domain, prefer_local_catalog, language='?'):
	# <language> only used for logging

	# search for message catalog
	candidate_PO_dirs = []
	# - locally
	if prefer_local_catalog:
		_log.debug('prioritizing local message catalog')
		# - one level above path to binary
		#    last resort for inferior operating systems such as DOS/Windows
		#    strip one directory level
		#    this is a rather neat trick :-)
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'po'))
		_log.debug('looking one level above binary install directory: %s', loc_dir)
		candidate_PO_dirs.append(loc_dir)
		# - in path to binary
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'po'))
		_log.debug('looking in binary install directory: %s', loc_dir)
		candidate_PO_dirs.append(loc_dir)
	# - standard places
	if os.name == 'posix':
		_log.debug('system is POSIX, looking in standard locations (see Python Manual)')
		# if this is reported to segfault/fail/except on some
		# systems we may have to assume "sys.prefix/share/locale/"
		candidate_PO_dirs.append(gettext.bindtextdomain(domain))
	else:
		_log.debug('No use looking in standard POSIX locations - not a POSIX system.')
	# - $(<script-name>_DIR)/
	env_key = "%s_DIR" % os.path.splitext(os.path.basename(sys.argv[0]))[0].upper()
	_log.debug('looking at ${%s}' % env_key)
	if env_key in os.environ:
		loc_dir = os.path.abspath(os.path.join(os.environ[env_key], 'po'))
		_log.debug('${%s} = "%s" -> [%s]' % (env_key, os.environ[env_key], loc_dir))
		candidate_PO_dirs.append(loc_dir)
	else:
		_log.info("${%s} not set" % env_key)
	# - locally
	if not prefer_local_catalog:
		# - one level above path to binary
		#    last resort for inferior operating systems such as DOS/Windows
		#    strip one directory level
		#    this is a rather neat trick :-)
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'po'))
		_log.debug('looking above binary install directory [%s]' % loc_dir)
		candidate_PO_dirs.append(loc_dir)
		# - in path to binary
		loc_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'po' ))
		_log.debug('looking in binary install directory [%s]' % loc_dir)
		candidate_PO_dirs.append(loc_dir)
	# now try to actually install it
	for candidate_PO_dir in candidate_PO_dirs:
		_log.debug('trying with (base=%s, %s, domain=%s)', candidate_PO_dir, language, domain)
		_log.debug(' -> %s.mo', os.path.join(candidate_PO_dir, language, domain))
		if not os.path.exists(candidate_PO_dir):
			continue
		try:
			gettext.install(domain, candidate_PO_dir)
		except Exception:
			_log.exception('installing text domain [%s] failed from [%s]', domain, candidate_PO_dir)
			continue
		global _
		# does it translate ?
		if _(__orig_tag__) == __orig_tag__:
			_log.debug('does not translate: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
			continue
		_log.debug('found msg catalog: [%s] => [%s]', __orig_tag__, _(__orig_tag__))
		global _translate_via_gettext
		_translate_via_gettext = builtins._
		builtins._ = _translate_safely
		return True

	return False

#===========================================================================
_encoding_mismatch_already_logged = False
_current_encoding = None

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
	<locale.getlocale()[1]>
		- what the current locale is *actually* using
		  as the encoding for text conversion
	<locale.getpreferredencoding()>
		- what the current locale would *recommend* using
		  as the encoding for text conversion
	"""
	global _current_encoding
	if _current_encoding is not None:
		return _current_encoding

	enc = sys.getdefaultencoding()
	if enc != 'ascii':
		_current_encoding = enc
		return _current_encoding

	enc = locale.getlocale()[1]
	if enc is not None:
		_current_encoding = enc
		return _current_encoding

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

	if sys.argv[1] != 'test':
		sys.exit()

	logging.basicConfig(level = logging.DEBUG)
	#----------------------------------------------------------------------
	def test_strcoll():
		candidates = [
#			(u'a', u'a'),
#			(u'a', u'b'),
#			(u'1', u'1'),
#			(u'1', u'2'),
#			(u'A', u'A'),
#			(u'a', u'A'),
			('\u270d', '\u270d'),
			('4', '\u270d' + '4'),
			('4.4', '\u270d' + '4.4'),
			('44', '\u270d' + '44'),
			('4', '\u270d' + '9'),
			('4', '\u270d' + '2'),
#			(u'9', u'\u270d' + u'9'),
#			(u'9', u'\u270d' + u'4'),

		]
		for cands in candidates:
			print(cands[0], '<vs>', cands[1], '=', locale.strcoll(cands[0], cands[1]))
#			print(cands[1], u'<vs>', cands[0], '=', locale.strcoll(cands[1], cands[0]))

	#----------------------------------------------------------------------
	print("======================================================================")
	print("GNUmed i18n")
	print("")
	print("authors:", __author__)
	print("license:", __license__)
	print("======================================================================")

	activate_locale()
	print("system locale: ", system_locale, "; levels:", system_locale_level)
	print("likely encoding:", get_encoding())

	if len(sys.argv) > 2:
		install_domain(domain = sys.argv[2])
	else:
		install_domain()

	test_strcoll()

	# ********************************************************************* #
	# == do not remove this line ========================================== #
	# it is needed to check for successful installation of                  #
	# the desired message catalog                                           #
	# ********************************************************************* #
	tmp = _('Translate this or i18n into <en_EN> will not work properly !') #
	# ********************************************************************* #
	# ********************************************************************* #
