"""GNUmed SOAP related defintions"""

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://gnu.org)'
#============================================================
if __name__ == '__main__':
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain(domain = 'gnumed')


_U_ELLIPSIS = '\u2026'

KNOWN_SOAP_CATS = list('soapu')
KNOWN_SOAP_CATS.append(None)		# admin category


soap_cat2l10n = {
	's': _('S##tx: single character for SOAP category <Subjective>'),
	'o': _('O##tx: single character for SOAP category <Objective>'),
	'a': _('A##tx: single character for SOAP category <Assessment>'),
	'p': _('P##tx: single character for SOAP category <Plan>'),
	'u': _('U##tx: single character for SOAP pseudo category <Unspecified>'),
	'': _U_ELLIPSIS,		# admin
	None: _U_ELLIPSIS		# admin
}


soap_cat2l10n_str = {
	's': _('Subjective##tx: name for SOAP category <Subjective>'),
	'o': _('Objective##tx: name for SOAP category <Objective>'),
	'a': _('Assessment##tx: name for SOAP category <Assessment>'),
	'p': _('Plan##tx: name for SOAP category <Plan>'),
	'u': _('Unspecified##tx: name for SOAP pseudo category <Unspecified>'),
	'':  _('Administrative##tx: name for SOAP pseudo category <Administrative>'),
	None: _('Administrative##tx: name for SOAP pseudo category <Administrative>')
}


l10n2soap_cat = {
	'%s' % soap_cat2l10n['s']: 's',
	'%s' % soap_cat2l10n['o']: 'o',
	'%s' % soap_cat2l10n['a']: 'a',
	'%s' % soap_cat2l10n['p']: 'p',
	'%s' % soap_cat2l10n['u']: 'u',
	_U_ELLIPSIS: None,
	'.': None,
	' ': None,
	'': None
}

#============================================================
def soap_cats_str2list(soap_cats:list|str=None) -> list[str]:
	"""Normalize SOAP categories, preserving order.

	Args:
		soap_cats: string or list
		* None -> process KNOWN_SOAP_CATS (all, that is)
		* [] -> []
		* '' -> []
		* ' ' -> [None]	(admin)
	"""
	if soap_cats is None:
		soap_cats = KNOWN_SOAP_CATS
	soap_cats = list(soap_cats)
	normalized_cats:list = []
	for cat in soap_cats:
		if cat in [' ', None]:
			if None in normalized_cats:
				continue
			normalized_cats.append(None)
			continue
		cat = cat.casefold()
		if cat in KNOWN_SOAP_CATS:
			if cat in normalized_cats:
				continue
			normalized_cats.append(cat)
	return normalized_cats

#============================================================
def are_valid_soap_cats(soap_cats:str|list, allow_upper:bool=True) -> bool:
	"""Check whether _soap_cats_ contains valid category markers only.

	Args:
		soap_cats: string or list
		allow_upper: whether uppercase is considered valid
	"""
	for cat2test in soap_cats:
		if cat2test in KNOWN_SOAP_CATS:
			continue
		if not allow_upper:
			return False

		if cat2test.casefold() in KNOWN_SOAP_CATS:
			continue
		return False

	return True

#============================================================
def normalize_soap_cat(soap_cat:str) -> str|bool:
	soap_cat = soap_cat.casefold()
	if soap_cat in KNOWN_SOAP_CATS:
		return soap_cat

	return False		# type: ignore [return-value]

#============================================================
if __name__ == '__main__':

	import sys

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	sys.path.insert(0, '../../')
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed', prefer_local_catalog = True)

	#--------------------------------------------------------
	def test_translation():
		for c in KNOWN_SOAP_CATS:
			print('category:', c)
			print(' l10n char:', soap_cat2l10n[c])
			print(' l10n str:', soap_cat2l10n_str[c])

	#--------------------------------------------------------
	def test_are_valid_cats():
		cats = [
			list('soapu'),
			list('soapuSOAPU'),
			list('soapux'),
			list('soapuX'),
			list('soapuSOAPUx'),
			[None],
			['s', None],
			['s', None, 'O'],
			['s', None, 'x'],
			['s', None, 'X'],
		]
		for cat_list in cats:
			print(cat_list)
			print('  valid (plain):', are_valid_soap_cats(cat_list, False))
			print('  valid (w/ upper):', are_valid_soap_cats(cat_list, True))

	#--------------------------------------------------------
	test_translation()
	#test_are_valid_cats()
