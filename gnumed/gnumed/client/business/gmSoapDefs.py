"""GNUmed SOAP related defintions"""

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://gnu.org)'

#============================================================
import logging


try:
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

#============================================================
_U_ELLIPSIS = u'\u2026'

KNOWN_SOAP_CATS = list(u'soapu')
KNOWN_SOAP_CATS.append(None)


soap_cat2l10n = {
	u's': _('SOAP_char_S=S').replace(u'SOAP_char_S=', u''),
	u'o': _('SOAP_char_O=O').replace(u'SOAP_char_O=', u''),
	u'a': _('SOAP_char_A=A').replace(u'SOAP_char_A=', u''),
	u'p': _('SOAP_char_P=P').replace(u'SOAP_char_P=', u''),
	u'u': _('SOAP_char_U=U').replace(u'SOAP_char_U=', u''),
	None: _U_ELLIPSIS
}


soap_cat2l10n_str = {
	u's': _('SOAP_string_Subjective=Subjective').replace(u'SOAP_string_Subjective=', u''),
	u'o': _('SOAP_string_Objective=Objective').replace(u'SOAP_string_Objective=', u''),
	u'a': _('SOAP_string_Assessment=Assessment').replace(u'SOAP_string_Assessment=', u''),
	u'p': _('SOAP_string_Plan=Plan').replace(u'SOAP_string_Plan=', u''),
	u'u': _('SOAP_string_Unspecified=Unspecified').replace(u'SOAP_string_Unspecified=', u''),
	None: _('SOAP_string_Administrative=Administrative').replace(u'SOAP_string_Administrative=', u'')
}


l10n2soap_cat = {
	_('SOAP_char_S=S').replace(u'SOAP_char_S=', u''): u's',
	_('SOAP_char_O=O').replace(u'SOAP_char_O=', u''): u'o',
	_('SOAP_char_A=A').replace(u'SOAP_char_A=', u''): u'a',
	_('SOAP_char_P=P').replace(u'SOAP_char_P=', u''): u'p',
	_('SOAP_char_U=U').replace(u'SOAP_char_U=', u''): u'u',
	_U_ELLIPSIS: None,
	u'.': None,
	u' ': None,
	u'': None
}

#============================================================
def soap_cats2list(soap_cats):
	"""Normalizes a string or list of SOAP categories, preserving order.

		None -> gmSoapDefs.KNOWN_SOAP_CATS (all)
		[] -> []
		u'' -> []
		u' ' -> [None]	(admin)
	"""
	if soap_cats is None:
		return KNOWN_SOAP_CATS

	normalized_cats = []
	for cat in soap_cats:
		if cat in [u' ', None]:
			if None in normalized_cats:
				continue
			normalized_cats.append(None)
			continue
		cat = cat.lower()
		if cat in gmSoapDefs.KNOWN_SOAP_CATS:
			if cat in normalized_cats:
				continue
			normalized_cats.append(cat)

	return normalized_cats

#============================================================
if __name__ == '__main__':

	import sys

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	sys.path.insert(0, '../../')

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
	def test_translation():
		for c in KNOWN_SOAP_CATS:
			print c, soap_cat2l10n[c], soap_cat2l10n_str[c]

	#--------------------------------------------------------
	test_translation()
