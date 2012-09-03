# -*- coding: utf8 -*-
"""GNUmed keyword snippet expansions

Copyright: authors
"""
#============================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.kwd_exp')

#============================================================
_SQL_get_keyword_expansions = u"SELECT * FROM ref.v_your_keyword_expansions WHERE %s"

class cKeywordExpansion(gmBusinessDBObject.cBusinessDBObject):
	"""Keyword indexed text snippets or chunks of data. Used as text macros or to put into documents."""
	_cmd_fetch_payload = _SQL_get_keyword_expansions % u"pk_expansion = %s"
	_cmds_store_payload = [
		u"""
			UPDATE ref.keyword_expansion SET
				keyword = gm.nullify_empty_string(%(keyword)s),
				textual_data = gm.nullify_empty_string(%(expansion)s)
			WHERE
				pk = %(pk_expansion)s
					AND
				xmin = %(xmin_expansion)s
			RETURNING
				xmin as xmin_expansion
		"""
	]
	_updatable_fields = [
		u'keyword',
		u'expansion',
		u'key_id'
	]
	#--------------------------------------------------------
	def format(self):
		txt = u'%s            #%s\n' % (
			gmTools.bool2subst (
				self._payload[self._idx['is_textual']],
				_('Textual keyword expansion'),
				_('Binary keyword expansion')
			),
			self._payload[self._idx['pk_expansion']]
		)
		txt += u' %s%s\n' % (
			gmTools.bool2subst (
				self._payload[self._idx['private_expansion']],
				_('private'),
				_('public')
			),
			gmTools.bool2subst (
				(self._payload[self._idx['key_id']] is None),
				u'',
				u', %s' % _('encrypted')
			)
		)
		txt += _(' Keyword: %s\n') % self._payload[self._idx['keyword']]
		txt += _(' Owner: %s\n') % self._payload[self._idx['owner']]
		txt += gmTools.bool2subst (
			(self._payload[self._idx['key_id']] is None),
			u'',
			_(' Key ID: %s\n') % self._payload[self._idx['key_id']]
		)
		if self._payload[self._idx['is_textual']]:
			txt += u'\n%s' % self._payload[self._idx['expansion']]
		else:
			txt += u' Data: %s (%s Bytes)' % (gmTools.size2str(self._payload[self._idx['data_size']]), self._payload[self._idx['data_size']])

		return txt

#------------------------------------------------------------
def get_keyword_expansions(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_keyword_expansions % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cKeywordExpansion(row = {'data': r, 'idx': idx, 'pk_field': 'pk_expansion'}) for r in rows ]

#------------------------------------------------------------
def get_expansion(keyword=None, textual_only=True):

	where_parts = [u'keyword = %(kwd)s']
	args = {'kwd': keyword}

	if textual_only:
		where_parts.append(u'is_textual IS TRUE')

	cmd = _SQL_get_keyword_expansions % u' AND '.join(where_parts)
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	if len(rows) == 0:
		return None

	return cKeywordExpansion(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_expansion'})

#------------------------------------------------------------
def create_keyword_expansion(keyword=None, text=None, data_file=None, public=True):

	if None not in [text, data_file]:
		raise ValueError('either <text> or <data> must be non-NULL')

	# already exists ?
	cmd = u"SELECT 1 FROM ref.v_your_keyword_expansions WHERE public_expansion IS %(public)s AND keyword = %(kwd)s"
	args = {'kwd': keyword, 'public': public}
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	if len(rows) != 0:
		# can't create duplicate
		return False

	if data_file is not None:
		text = u'fake data'
	args = {u'kwd': keyword, u'txt': text}
	if public:
		cmd = u"""
			INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
			VALUES (
				gm.nullify_empty_string(%(kwd)s),
				gm.nullify_empty_string(%(txt)s),
				null
			)
			RETURNING pk
		"""
	else:
		cmd = u"""
			INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
			VALUES (
				gm.nullify_empty_string(%(kwd)s),
				gm.nullify_empty_string(%(txt)s),
				(SELECT pk FROM dem.staff WHERE db_user = current_user)
			)
			RETURNING pk
		"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	expansion = cKeywordExpansion(aPK_obj = rows[0]['pk'])
	expansion.update_data_from_file(filename = data_file)

	global __textual_expansion_keywords
	__textual_expansion_keywords = None

	return expansion
#------------------------------------------------------------
def delete_keyword_expansion(pk=None):
	args = {'pk': pk}
	cmd = u"DELETE FROM ref.keyword_expansion WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	global __textual_expansion_keywords
	__textual_expansion_keywords = None

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

	cmd = u"""SELECT keyword, public_expansion, private_expansion, owner FROM ref.v_keyword_expansions WHERE is_textual IS TRUE"""
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}])
	__textual_expansion_keywords = rows

	_log.info('retrieved %s expansion keywords', len(__textual_expansion_keywords))

	return __textual_expansion_keywords
#------------------------------------------------------------------------
def get_matching_textual_keywords(fragment=None):

	if fragment is None:
		return []

	return [ kwd['keyword'] for kwd in get_textual_expansion_keywords() if kwd['keyword'].startswith(fragment) ]

#------------------------------------------------------------------------
def expand_keyword(keyword = None):

	# Easter Egg ;-)
	if keyword == u'$$steffi':
		return u'Hai, play !  Versucht das ! (Keks dazu ?)  :-)'

	cmd = u"""SELECT expansion FROM ref.v_your_keyword_expansions WHERE keyword = %(kwd)s"""
	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])

	if len(rows) == 0:
		return None

	return rows[0]['expansion']
#------------------------------------------------------------------------
def add_text_expansion(keyword=None, expansion=None, public=None):

	if public:
		cmd = u"SELECT 1 FROM ref.v_keyword_expansions WHERE public_expansion IS TRUE AND keyword = %(kwd)s"
	else:
		cmd = u"SELECT 1 FROM ref.v_your_keyword_expansions WHERE private_expansion IS TRUE AND keyword = %(kwd)s"

	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])
	if len(rows) != 0:
		return False

	if public:
		cmd = u"""
INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
VALUES (%(kwd)s, %(exp)s, null)"""
	else:
		cmd = u"""
INSERT INTO ref.keyword_expansion (keyword, textual_data, fk_staff)
VALUES (%(kwd)s, %(exp)s, (SELECT pk FROM dem.staff WHERE db_user = current_user))"""

	rows, idx = run_rw_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword, 'exp': expansion}}])

	global __textual_expansion_keywords
	__textual_expansion_keywords = None

	return True
#------------------------------------------------------------------------
def delete_text_expansion(keyword):
	cmd = u"""
DELETE FROM ref.keyword_expansion WHERE
	keyword = %(kwd)s AND (
		(fk_staff = (SELECT pk FROM dem.staff WHERE db_user = current_user))
			OR
		(fk_staff IS NULL AND owner = current_user)
	)"""
	rows, idx = run_rw_queries(queries = [{'cmd': cmd, 'args': {'kwd': keyword}}])

	global __textual_expansion_keywords
	__textual_expansion_keywords = None
#------------------------------------------------------------------------
def edit_text_expansion(keyword, expansion):

	cmd1 = u"""
		DELETE FROM ref.keyword_expansion
		WHERE
			keyword = %(kwd)s
				AND
			fk_staff = (SELECT pk FROM dem.staff WHERE db_user = current_user)"""

	cmd2 = u"""
		INSERT INTO ref.keyword_expansion (
			keyword, textual_data, fk_staff
		) VALUES (
			%(kwd)s,
			%(exp)s,
			(SELECT pk FROM dem.staff WHERE db_user = current_user)
		)"""
	args = {'kwd': keyword, 'exp': expansion}
	rows, idx = run_rw_queries(queries = [
		{'cmd': cmd1, 'args': args},
		{'cmd': cmd2, 'args': args},
	])

	global __textual_expansion_keywords
	__textual_expansion_keywords = None

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
		print "keywords, from database:"
		print get_textual_expansion_keywords()
		print "keywords, cached:"
		print get_textual_expansion_keywords()
		print "'$keyword' expands to:"
		print expand_keyword(keyword = u'$dvt')

	#--------------------------------------------------------------------
	def test_kwd_expansions():
		for k in get_keyword_expansions():
			print k.format()
			print ""
	#--------------------------------------------------------------------
	#test_textual_expansion()
	test_kwd_expansions()
