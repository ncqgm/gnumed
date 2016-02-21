"""GNUmed SOAP related defintions"""
#============================================================
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
	u' ': _U_ELLIPSIS,
	u'': _U_ELLIPSIS,
	None: _U_ELLIPSIS
}


l10n2soap_cat = {
	_('SOAP_char_S=S').replace(u'SOAP_char_S=', u''): u's',
	_('SOAP_char_O=O').replace(u'SOAP_char_O=', u''): u'o',
	_('SOAP_char_A=A').replace(u'SOAP_char_A=', u''): u'a',
	_('SOAP_char_P=P').replace(u'SOAP_char_P=', u''): u'p',
	_('SOAP_char_U=U').replace(u'SOAP_char_U=', u''): u'u',
	_U_ELLIPSIS: None
}


soap_cat2l10n_str = {
	u's': _('SOAP_string_Subjective=Subjective').replace(u'SOAP_string_Subjective=', u''),
	u'o': _('SOAP_string_Objective=Objective').replace(u'SOAP_string_Objective=', u''),
	u'a': _('SOAP_string_Assessment=Assessment').replace(u'SOAP_string_Assessment=', u''),
	u'p': _('SOAP_string_Plan=Plan').replace(u'SOAP_string_Plan=', u''),
	u'u': _('SOAP_string_Unspecified=Unspecified').replace(u'SOAP_string_Unspecified=', u''),
	u' ': _('SOAP_string_Administrative=Administrative').replace(u'SOAP_string_Administrative=', u''),
	u'': _('SOAP_string_Administrative=Administrative').replace(u'SOAP_string_Administrative=', u''),
	None: _('SOAP_string_Administrative=Administrative').replace(u'SOAP_string_Administrative=', u'')
}

#============================================================
