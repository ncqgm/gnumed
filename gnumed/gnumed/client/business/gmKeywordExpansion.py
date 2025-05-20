# -*- coding: utf-8 -*-
"""GNUmed keyword snippet expansions

Copyright: authors
"""
#============================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import sys
import os
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib


_log = logging.getLogger('gm.kwd_exp')

#============================================================
_SQL_get_keyword_expansions = "SELECT * FROM ref.v_your_keyword_expansions WHERE %s"

class cKeywordExpansion(gmBusinessDBObject.cBusinessDBObject):
	"""Keyword indexed text snippets or chunks of data. Used as text macros or to put into documents."""
	_cmd_fetch_payload = _SQL_get_keyword_expansions % "pk_expansion = %s"
	_cmds_store_payload = [
		"""
			UPDATE ref.keyword_expansion SET
				keyword = gm.nullify_empty_string(%(keyword)s),
				textual_data = CASE
					WHEN gm.nullify_empty_string(%(expansion)s) IS NULL
						THEN CASE
							WHEN binary_data IS NULL THEN '---fake_data---'
							ELSE NULL
						END
					ELSE gm.nullify_empty_string(%(expansion)s)
				END,
				binary_data = CASE
					WHEN gm.nullify_empty_string(%(expansion)s) IS NULL THEN binary_data
					ELSE NULL
				END,
				encrypted = %(is_encrypted)s
			WHERE
				pk = %(pk_expansion)s
					AND
				xmin = %(xmin_expansion)s
			RETURNING
				xmin as xmin_expansion
		"""
	]
	_updatable_fields = [
		'keyword',
		'expansion',
		'is_encrypted'
	]

	#--------------------------------------------------------
	def save_to_file(self, aChunkSize=0, target_mime=None, target_extension=None, ignore_conversion_problems=False):

		if self._payload['is_textual']:
			return None

		if self._payload['data_size'] == 0:
			return None

		exported_fname = gmTools.get_unique_filename(prefix = 'gm-data_snippet-')
		success = gmPG2.bytea2file (
			data_query = {
				'sql': 'SELECT substring(binary_data from %(start)s for %(size)s) FROM ref.keyword_expansion WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = exported_fname,
			chunk_size = aChunkSize,
			data_size = self._payload['data_size']
		)

		if not success:
			return None

		if target_mime is None:
			return exported_fname

		converted_fname = gmMimeLib.convert_file(filename = exported_fname, target_mime = target_mime)
		if converted_fname is not None:
			return converted_fname

		_log.warning('conversion failed')
		if ignore_conversion_problems:
			_log.warning('programmed to ignore conversion problems, hoping receiver can handle [%s]', exported_fname)
			return exported_fname

		return None

	#--------------------------------------------------------
	def update_data_from_file(self, filename=None):
		if not (os.access(filename, os.R_OK) and os.path.isfile(filename)):
			_log.error('[%s] is not a readable file' % filename)
			return False

		gmPG2.file2bytea (
			query = "UPDATE ref.keyword_expansion SET binary_data = %(data)s::bytea, textual_data = NULL WHERE pk = %(pk)s",
			filename = filename,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()

		global __textual_expansion_keywords
		__textual_expansion_keywords = None
		global __keyword_expansions
		__keyword_expansions = None

		return True

	#--------------------------------------------------------
	def format(self):
		txt = '%s            #%s\n' % (
			gmTools.bool2subst (
				self._payload['is_textual'],
				_('Textual keyword expansion'),
				_('Binary keyword expansion')
			),
			self._payload['pk_expansion']
		)
		txt += ' %s%s\n' % (
			gmTools.bool2subst (
				self._payload['private_expansion'],
				_('private'),
				_('public')
			),
			gmTools.bool2subst (
				self._payload['is_encrypted'],
				', %s' % _('encrypted'),
				''
			)
		)
		txt += _(' Keyword: %s\n') % self._payload['keyword']
		txt += _(' Owner: %s\n') % self._payload['owner']
		if self._payload['is_textual']:
			txt += '\n%s' % self._payload['expansion']
		else:
			txt += ' Data: %s (%s Bytes)' % (gmTools.size2str(self._payload['data_size']), self._payload['data_size'])

		return txt

#------------------------------------------------------------
__keyword_expansions = None

def get_keyword_expansions(order_by=None, force_reload=False, return_pks=False):
	global __keyword_expansions
	if not force_reload:
		if __keyword_expansions is not None:
			return __keyword_expansions

	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_keyword_expansions % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_expansion'] for r in rows ]

	__keyword_expansions = [ cKeywordExpansion(row = {'data': r, 'pk_field': 'pk_expansion'}) for r in rows ]
	return __keyword_expansions

#------------------------------------------------------------
def get_expansion(keyword=None, textual_only=True, binary_only=False):

	if False not in [textual_only, binary_only]:
		raise ValueError('one of <textual_only> and <binary_only> must be False')

	where_parts = ['keyword = %(kwd)s']
	args = {'kwd': keyword}

	if textual_only:
		where_parts.append('is_textual IS TRUE')

	cmd = _SQL_get_keyword_expansions % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None

	return cKeywordExpansion(row = {'data': rows[0], 'pk_field': 'pk_expansion'})

#------------------------------------------------------------
def create_keyword_expansion(keyword=None, text=None, data_file=None, public=True):

	if text is not None:
		if text.strip() == '':
			text = None

	if None not in [text, data_file]:
		raise ValueError('either <text> or <data_file> must be non-NULL')

	# already exists ?
	cmd = "SELECT 1 FROM ref.v_your_keyword_expansions WHERE public_expansion IS %(public)s AND keyword = %(kwd)s"
	args = {'kwd': keyword, 'public': public}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) != 0:
		# can't create duplicate
		return False

	if data_file is not None:
		text = 'fake data'
	args = {'kwd': keyword, 'txt': text}
	if public:
		cmd = """
			INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
			VALUES (
				gm.nullify_empty_string(%(kwd)s),
				gm.nullify_empty_string(%(txt)s),
				null
			)
			RETURNING pk
		"""
	else:
		cmd = """
			INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
			VALUES (
				gm.nullify_empty_string(%(kwd)s),
				gm.nullify_empty_string(%(txt)s),
				(SELECT pk FROM dem.staff WHERE db_user = current_user)
			)
			RETURNING pk
		"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	expansion = cKeywordExpansion(aPK_obj = rows[0]['pk'])
	if data_file is not None:
		expansion.update_data_from_file(filename = data_file)

	global __textual_expansion_keywords
	__textual_expansion_keywords = None
	global __keyword_expansions
	__keyword_expansions = None

	return expansion
#------------------------------------------------------------
def delete_keyword_expansion(pk=None):
	args = {'pk': pk}
	cmd = "DELETE FROM ref.keyword_expansion WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	global __textual_expansion_keywords
	__textual_expansion_keywords = None
	global __keyword_expansions
	__keyword_expansions = None

	return True

#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
__textual_expansion_keywords = None

def get_textual_expansion_keywords():
	global __textual_expansion_keywords
	if __textual_expansion_keywords is not None:
		return __textual_expansion_keywords

	cmd = """SELECT keyword, public_expansion, private_expansion, owner FROM ref.v_keyword_expansions WHERE is_textual IS TRUE"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	__textual_expansion_keywords = rows

	_log.info('retrieved %s textual expansion keywords', len(__textual_expansion_keywords))

	return __textual_expansion_keywords
#------------------------------------------------------------------------
def get_matching_textual_keywords(fragment=None):

	if fragment is None:
		return []

	return [ kwd['keyword'] for kwd in get_textual_expansion_keywords() if kwd['keyword'].startswith(fragment) ]

#------------------------------------------------------------------------
def expand_keyword(keyword = None):

	# Easter Egg ;-)
	if keyword == '$$steffi':
		return 'Hai, play !  Versucht das ! (Keks dazu ?)  :-)'

	cmd = """SELECT expansion FROM ref.v_your_keyword_expansions WHERE keyword = %(kwd)s"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'kwd': keyword}}])

	if len(rows) == 0:
		return None

	return rows[0]['expansion']
#============================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	logging.basicConfig(level=logging.DEBUG)

	from Gnumed.pycommon import gmI18N
	gmI18N.install_domain('gnumed')
	gmI18N.activate_locale()

	#--------------------------------------------------------------------
	def test_textual_expansion():
		print("keywords, from database:")
		print(get_textual_expansion_keywords())
		print("keywords, cached:")
		print(get_textual_expansion_keywords())
		print("'$keyword' expands to:")
		print(expand_keyword(keyword = '$dvt'))

	#--------------------------------------------------------------------
	def test_kwd_expansions():
		for k in get_keyword_expansions():
			print(k.format())
			print("")
	#--------------------------------------------------------------------
	#test_textual_expansion()
	test_kwd_expansions()
