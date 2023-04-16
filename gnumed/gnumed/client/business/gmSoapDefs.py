"""GNUmed SOAP related defintions"""

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://gnu.org)'
#============================================================
if __name__ == '__main__':
	# we are the main script, setup a fake _() for now,
	# such that it can be used in module level definitions
	_ = lambda x:x
else:
	# we are being imported from elsewhere
	try:
		# do we already have _() ?
		_
	except NameError:
		# no, so setup i18n handling
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_U_ELLIPSIS = '\u2026'

KNOWN_SOAP_CATS = list('soapu')
KNOWN_SOAP_CATS.append(None)		# admin category


soap_cat2l10n = {
	's': _('SOAP_char_S=S').replace('SOAP_char_S=', ''),
	'o': _('SOAP_char_O=O').replace('SOAP_char_O=', ''),
	'a': _('SOAP_char_A=A').replace('SOAP_char_A=', ''),
	'p': _('SOAP_char_P=P').replace('SOAP_char_P=', ''),
	'u': _('SOAP_char_U=U').replace('SOAP_char_U=', ''),
	'': _U_ELLIPSIS,		# admin
	None: _U_ELLIPSIS		# admin
}


soap_cat2l10n_str = {
	's': _('SOAP_string_Subjective=Subjective').replace('SOAP_string_Subjective=', ''),
	'o': _('SOAP_string_Objective=Objective').replace('SOAP_string_Objective=', ''),
	'a': _('SOAP_string_Assessment=Assessment').replace('SOAP_string_Assessment=', ''),
	'p': _('SOAP_string_Plan=Plan').replace('SOAP_string_Plan=', ''),
	'u': _('SOAP_string_Unspecified=Unspecified').replace('SOAP_string_Unspecified=', ''),
	'':  _('SOAP_string_Administrative=Administrative').replace('SOAP_string_Administrative=', ''),
	None: _('SOAP_string_Administrative=Administrative').replace('SOAP_string_Administrative=', '')
}


l10n2soap_cat = {
	_('SOAP_char_S=S').replace('SOAP_char_S=', ''): 's',
	_('SOAP_char_O=O').replace('SOAP_char_O=', ''): 'o',
	_('SOAP_char_A=A').replace('SOAP_char_A=', ''): 'a',
	_('SOAP_char_P=P').replace('SOAP_char_P=', ''): 'p',
	_('SOAP_char_U=U').replace('SOAP_char_U=', ''): 'u',
	_U_ELLIPSIS: None,
	'.': None,
	' ': None,
	'': None
}

#============================================================
def soap_cats_str2list(soap_cats:str) -> list[str]:
	"""Normalize SOAP categories, preserving order.

	Args:
		soap_cats: string or list
		* None -> gmSoapDefs.KNOWN_SOAP_CATS (all)
		* [] -> []
		* '' -> []
		* ' ' -> [None]	(admin)
	"""
	if soap_cats is None:
		return KNOWN_SOAP_CATS

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
def are_valid_soap_cats(soap_cats:str, allow_upper:bool=True) -> bool:
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
def normalize_soap_cat(soap_cat:str) -> str: # | bool:
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
	gmI18N.install_domain()

	#--------------------------------------------------------
	def test_translation():
		for c in KNOWN_SOAP_CATS:
			print(c, soap_cat2l10n[c], soap_cat2l10n_str[c])

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
	test_are_valid_cats()
