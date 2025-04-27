# -*- coding: utf-8 -*-

"""GNUmed gender handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys
import time
import datetime as pyDT
import threading
import logging
import inspect
from xml.etree import ElementTree as etree

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	_ = lambda x:x
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2

from Gnumed.business.gmXdtMappings import map_gender_gm2xdt


_log = logging.getLogger('gm.person')

__LIST__gender_defs = None

__MAP__gender2salutation = None
__MAP__gender2string = None
__MAP__gender2symbol = None

#============================================================
_SQL_get_gender_labels = 'SELECT * FROM dem.v_gender_labels'

class cGenderLabel(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a gender label."""

	_cmd_fetch_payload = '%s WHERE pk_gender_label = %%s' % _SQL_get_gender_labels
	_cmds_store_payload = [
		"""UPDATE dem.gender_label SET
				tag = gm.nullify_empty_string(%(tag)s),
				label = gm.nullify_empty_string(%(label)s),
				symbol = gm.nullify_empty_string(%(symbol)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_gender_label)s
					AND
				xmin = %(xmin_gender_label)s
			RETURNING
				xmin AS xmin_gender_label,
				_(tag) as l10n_tag,
				_(label) as l10n_label,
				_(symbol) as l10n_symbol
		"""
	]
	_updatable_fields = [
		'tag',
		'label',
		'symbol',
		'comment'
	]
	#--------------------------------------------------------
	def format(self):
		symbol = map_gender2symbol(gender = self._payload['tag'])
		line = '%(l10n_tag)s: %(l10n_label)s' % self._payload
		if symbol:
			line += ' (%s)' % symbol
		return line

	#--------------------------------------------------------
	def store_field_translation(self, original:str, translation:str, link_obj=None):
		return gmPG2.update_translation_in_database (
			language = None,	# use current DB language
			original = original,
			translation = translation,
			link_obj = link_obj
		)

#------------------------------------------------------------
def get_genders(as_instance:bool=False, order_by:str=None) -> list:
	"""Retrieves the list of known genders from the database."""
	global __LIST__gender_defs
	if not __LIST__gender_defs:
		SQL = _SQL_get_gender_labels
		if order_by:
			SQL += ' ORDER BY %s' % order_by
		__LIST__gender_defs = gmPG2.run_ro_queries(queries = [{'cmd': SQL}])
		_log.debug('gender definitions in database: %s' % __LIST__gender_defs)
	if not as_instance:
		return __LIST__gender_defs

	return [ cGenderLabel(row = {'data': r, 'pk_field': 'pk_gender_label'}) for r in __LIST__gender_defs ]

#------------------------------------------------------------
def create_gender_label(tag:str=None, label:str=None, comment:str=None, symbol:str=None):
	args = {
		'tag': tag,
		'label': label,
		'cmt': comment,
		'sym': symbol
	}
	SQL = """
		INSERT INTO dem.gender_label (tag, label, comment, symbol) VALUES (
			gm.nullify_empty_string(%(tag)s),
			gm.nullify_empty_string(%(label)s),
			gm.nullify_empty_string(%(cmt)s),
			gm.nullify_empty_string(%(sym)s),
		)
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	return cGenderLabel(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_gender_label(pk_gender_label=None):
	args = {'pk': pk_gender_label}
	cmd = u"DELETE FROM dem.gender_label WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#------------------------------------------------------------
# widget code
#------------------------------------------------------------
#def edit_gender_label(parent=None, xxx=None, single_entry=False, presets=None):
#	pass

#i18n.upd_tx gmPG2.update_translation_in_database(language=None, original=None, translation=None, link_obj=None)

#------------------------------------------------------------
#def delete_gender_label():
#	pass

#------------------------------------------------------------
#def manage_gender_labels():
#	pass

#------------------------------------------------------------
# remember to add in clinical item generic workflows and generic clinical item formatting

#------------------------------------------------------------
#------------------------------------------------------------
map_gender2mf = {
	'm': 'm',
	'f': 'f',
	'tf': 'f',
	'tm': 'm',
	'h': 'mf'
}

# https://tools.ietf.org/html/rfc6350#section-6.2.7
# M F O N U
map_gender2vcard = {
	'm': 'M',
	'f': 'F',
	'tf': 'F',
	'tm': 'M',
	'h': 'O',
	None: 'U'
}

#------------------------------------------------------------
def map_gender2tag(gender:str=None) -> str:
	for gdef in get_genders():
		if gender in [gdef['tag'], gdef['l10n_tag'], gdef['label'], gdef['l10n_label'], gdef['symbol'], gdef['l10n_symbol']]:
			return gdef['tag']

	return None

#------------------------------------------------------------
def map_gender2string(gender:str=None) -> str:
	"""Maps GNUmed related i18n-aware gender specifiers to a human-readable string."""
	global __MAP__gender2string
	if not __MAP__gender2string:
		__MAP__gender2string = {
			'm': _('male'),
			'f': _('female'),
			'tf': '',
			'tm': '',
			'h': '',
			None: _('unknown gender')
		}
		for g in get_genders():
			if g['l10n_label']:
				__MAP__gender2string[g['l10n_tag']] = g['l10n_label']
				__MAP__gender2string[g['tag']] = g['l10n_label']
		_log.debug('gender -> string mapping: %s' % __MAP__gender2string)
	try:
		return __MAP__gender2string[gender]

	except KeyError:
		return '?%s?' % gender

#------------------------------------------------------------
def map_gender2symbol(gender:str=None) -> str:
	"""Maps GNUmed related i18n-aware gender specifiers to a unicode symbol."""
	global __MAP__gender2symbol
	if not __MAP__gender2symbol:
		# built-in defaults
		__MAP__gender2symbol = {
			'm': '\u2642',
			'f': '\u2640',
			'tf': '\u26A5\u2640',
			#'tf': u'\u2642\u2640-\u2640',
			'tm': '\u26A5\u2642',
			#'tm': u'\u2642\u2640-\u2642',
			'h': '\u26A5',
			#'h': u'\u2642\u2640',
			None: '?\u26A5?'
		}
		# update from database, possibly adding more genders
		for g in get_genders():
			if g['l10n_symbol']:
				__MAP__gender2symbol[g['l10n_tag']] = g['l10n_symbol']
				__MAP__gender2symbol[g['tag']] = g['l10n_symbol']
		_log.debug('gender -> symbol mapping: %s' % __MAP__gender2symbol)
	try:
		return __MAP__gender2symbol[gender]

	except KeyError:
		return '?%s?' % gender

#------------------------------------------------------------
def map_gender2salutation(gender=None):
	"""Maps GNUmed related i18n-aware gender specifiers to a human-readable salutation."""

	global __MAP__gender2salutation
	if not __MAP__gender2salutation:
		__MAP__gender2salutation = {
			'm': _('Mr'),
			'f': _('Mrs'),
			'tf': '',
			'tm': '',
			'h': '',
			None: ''
		}
	#	for g in get_genders():
	#		__MAP__gender2salutation[g['l10n_tag']] = __MAP__gender2salutation[g['tag']]
	#		__MAP__gender2salutation[g['label']] = __MAP__gender2salutation[g['tag']]
	#		__MAP__gender2salutation[g['l10n_label']] = __MAP__gender2salutation[g['tag']]
		_log.debug('gender -> salutation mapping: %s' % __MAP__gender2salutation)
	try:
		return __MAP__gender2salutation[gender]

	except KeyError:
		return ''

#------------------------------------------------------------
def map_firstnames2gender(firstnames=None):
	"""Try getting the gender for the given first name."""

	if firstnames is None:
		return None

	rows = gmPG2.run_ro_queries(queries = [{
		'cmd': "SELECT gender FROM dem.name_gender_map WHERE name ILIKE %(fn)s LIMIT 1",
		'args': {'fn': firstnames}
	}])

	if len(rows) == 0:
		return None

	return rows[0][0]

#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmLog2.print_logfile_name()

	#--------------------------------------------------------
	def test_gender_list():
		genders = get_genders()
		print("\n\nRetrieving gender enum (tag, label, symbol):")
		for gender in genders:
			print("%s, %s, %s, %s" % (gender['tag'], gender['l10n_label'], gender['l10n_symbol'], map_gender2symbol(gender['tag'])))

	#--------------------------------------------------------
	def test_get_gender_labels():
		for l in get_genders(as_instance = True):
			print(l.format())

	#--------------------------------------------------------

	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	#map_gender2salutation('m')
	test_get_gender_labels()
	#test_gender_list()
