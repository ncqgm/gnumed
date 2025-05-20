# -*- coding: utf-8 -*-
"""GNUmed auto hints middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools

from Gnumed.business import gmStaff

_log = logging.getLogger('gm.hints')

(
	HINT_POPUP_NONE,			# this hint is not to be popped up
	HINT_POPUP_BY_ITSELF,		# this hint is intended to be poppep up by itself
	HINT_POPUP_IN_LIST			# this hint is intended to be popped up amongst a list of hints
) = (0, 1, 2)
#============================================================
# dynamic hints API
#------------------------------------------------------------
_SQL_get_dynamic_hints = "SELECT * FROM ref.v_auto_hints WHERE %s"

class cDynamicHint(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a dynamic hint to be run against the database."""

	_cmd_fetch_payload = _SQL_get_dynamic_hints % "pk_auto_hint = %s"
	_cmds_store_payload = [
		"""UPDATE ref.auto_hint SET
				query = gm.nullify_empty_string(%(query)s),
				recommendation_query = gm.nullify_empty_string(%(recommendation_query)s),
				title = gm.nullify_empty_string(%(title)s),
				hint = gm.nullify_empty_string(%(hint)s),
				url = gm.nullify_empty_string(%(url)s),
				source = gm.nullify_empty_string(%(source)s),
				is_active = %(is_active)s,
				popup_type = %(popup_type)s,
				highlight_as_priority = %(highlight_as_priority)s
			WHERE
				pk = %(pk_auto_hint)s
					AND
				xmin = %(xmin_auto_hint)s
			RETURNING
				xmin AS xmin_auto_hint
		"""
	]
	_updatable_fields = [
		'query',
		'recommendation_query',
		'title',
		'hint',
		'url',
		'source',
		'is_active',
		'popup_type',
		'highlight_as_priority'
	]
	#--------------------------------------------------------
	def format_maximum_information(self, patient):
		return self.format(include_sql = True).split('\n')

	#--------------------------------------------------------
	def format(self, include_sql=False):
		txt = '%s               [#%s]\n' % (
			gmTools.bool2subst(self._payload['is_active'], _('Active clinical hint'), _('Inactive clinical hint')),
			self._payload['pk_auto_hint']
		)
		txt += '\n'
		txt += self._payload['title']
		txt += '\n'
		txt += '\n'
		txt += _('Source: %s\n') % self._payload['source']
		txt += _('Language: %s\n') % self._payload['lang']
		txt += '\n'
		txt += gmTools.wrap(self._payload['hint'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
		txt += '\n'
		txt += '\n'
		if self._payload['recommendation'] is not None:
			txt += gmTools.wrap(self._payload['recommendation'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
			txt += '\n'
			txt += '\n'
		txt += gmTools.wrap (
			gmTools.coalesce(self._payload['url'], ''),
			width = 50,
			initial_indent = ' ',
			subsequent_indent = ' '
		)
		txt += '\n'
		if include_sql:
			txt += '\n'
			txt += gmTools.wrap(self._payload['query'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
			txt += '\n'
			if self._payload['recommendation_query'] is not None:
				txt += '\n'
				txt += gmTools.wrap(self._payload['recommendation_query'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
				txt += '\n'
		if self._payload['rationale4suppression'] is not None:
			txt += '\n'
			txt += _('Rationale for suppression:')
			txt += '\n'
			txt += gmTools.wrap(self._payload['rationale4suppression'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
			txt += '\n'
		return txt

	#--------------------------------------------------------
	def suppress(self, rationale=None, pk_encounter=None):
		return suppress_dynamic_hint (
			pk_hint = self._payload['pk_auto_hint'],
			pk_encounter = pk_encounter,
			rationale = rationale
		)
	#--------------------------------------------------------
	def invalidate_suppression(self, pk_encounter=None):
		return invalidate_hint_suppression (
			pk_hint = self._payload['pk_auto_hint'],
			pk_encounter = pk_encounter
		)

	#--------------------------------------------------------
	def _get_failed(self):
		return self._payload['title'].startswith('ERROR checking for [')

	failed = property(_get_failed)

#------------------------------------------------------------
def get_dynamic_hints(order_by=None, link_obj=None, return_pks=False):
	if order_by is None:
		order_by = 'TRUE'
	else:
		order_by = 'TRUE ORDER BY %s' % order_by
	cmd = _SQL_get_dynamic_hints % order_by
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_auto_hint'] for r in rows ]
	return [ cDynamicHint(row = {'data': r, 'pk_field': 'pk_auto_hint'}) for r in rows ]

#------------------------------------------------------------
def create_dynamic_hint(link_obj=None, query=None, title=None, hint=None, source=None):
	args = {
		'query': query,
		'title': title,
		'hint': hint,
		'source': source,
		'usr': gmStaff.gmCurrentProvider()['db_user']
	}
	cmd = """
		INSERT INTO ref.auto_hint (
			query,
			title,
			hint,
			source,
			lang
		) VALUES (
			gm.nullify_empty_string(%(query)s),
			gm.nullify_empty_string(%(title)s),
			gm.nullify_empty_string(%(hint)s),
			gm.nullify_empty_string(%(source)s),
			i18n.get_curr_lang(%(usr)s)
		)
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}], return_data = True)
	return cDynamicHint(aPK_obj = rows[0]['pk'], link_obj = link_obj)

#------------------------------------------------------------
def delete_dynamic_hint(link_obj=None, pk_hint=None):
	args = {'pk': pk_hint}
	cmd = "DELETE FROM ref.auto_hint WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
def get_hints_for_patient(pk_identity=None, pk_encounter=None):
	conn = gmPG2.get_connection()
	curs = conn.cursor()
	curs.callproc('clin.get_hints_for_patient', [pk_identity])
	rows = curs.fetchall()
	curs.close()
	conn.rollback()

	applying_rows = []
	for row in rows:
		if row['rationale4suppression'] is None:
			applying_rows.append(row)
			continue
		if row['rationale4suppression'].startswith('magic_tag::'):
			_log.debug('hint with magic tag: %s', row['rationale4suppression'])
			if 'suppression_needs_invalidation' in row['rationale4suppression']:
				_log.debug('database asks for invalidation of suppression of hint [%s]', row)
				if pk_encounter is not None:
					invalidate_hint_suppression(pk_hint = row['pk_auto_hint'], pk_encounter = pk_encounter)
			if 'does_not_apply' in row['rationale4suppression']:
				continue
			# we would need to reload the relevant hint at this time,
			# however currently, only hints which do not apply ask
			# for invalidation of suppression
		applying_rows.append(row)

	return [ cDynamicHint(row = {'data': r, 'pk_field': 'pk_auto_hint'}) for r in applying_rows ]

#------------------------------------------------------------
def suppress_dynamic_hint(pk_hint=None, rationale=None, pk_encounter=None):
	args = {
		'hint': pk_hint,
		'rationale': rationale,
		'enc': pk_encounter
	}
	cmd = """
		DELETE FROM clin.suppressed_hint
		WHERE
			fk_hint = %(hint)s
				AND
			fk_encounter IN (
				SELECT pk FROM clin.encounter WHERE fk_patient = (
					SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s
				)
			)
	"""
	queries = [{'sql': cmd, 'args': args}]
	cmd = """
		INSERT INTO clin.suppressed_hint (
			fk_encounter,
			fk_hint,
			rationale,
			md5_sum
		) VALUES (
			%(enc)s,
			%(hint)s,
			%(rationale)s,
			(SELECT r_vah.md5_sum FROM ref.v_auto_hints r_vah WHERE r_vah.pk_auto_hint = %(hint)s)
		)
	"""
	queries.append({'sql': cmd, 'args': args})
	gmPG2.run_rw_queries(queries = queries)
	return True

#------------------------------------------------------------
# suppressed dynamic hints
#------------------------------------------------------------
_SQL_get_suppressed_hints = "SELECT * FROM clin.v_suppressed_hints WHERE %s"

class cSuppressedHint(gmBusinessDBObject.cBusinessDBObject):
	"""Represents suppressed dynamic hints per patient."""

	_cmd_fetch_payload:str = _SQL_get_suppressed_hints % "pk_suppressed_hint = %s"
	_cmds_store_payload:list = []
	_updatable_fields:list = []
	#--------------------------------------------------------
	def format(self):
		txt = '%s               [#%s]\n' % (
			gmTools.bool2subst(self._payload['is_active'], _('Suppressed active dynamic hint'), _('Suppressed inactive dynamic hint')),
			self._payload['pk_suppressed_hint']
		)
		txt += '\n'
		txt += '%s\n\n' % self._payload['title']
		txt += _('Suppressed by: %s\n') % self._payload['suppressed_by']
		txt += _('Suppressed at: %s\n') % self._payload['suppressed_when'].strftime('%Y %b %d')
		txt += _('Hint #: %s\n') % self._payload['pk_hint']
		txt += _('Patient #: %s\n') % self._payload['pk_identity']
		txt += _('MD5 (currently): %s\n') % self._payload['md5_hint']
		txt += _('MD5 (at suppression): %s\n') % self._payload['md5_suppressed']
		txt += _('Source: %s\n') % self._payload['source']
		txt += _('Language: %s\n') % self._payload['lang']
		txt += '\n'
		txt += '%s\n' % gmTools.wrap(self._payload['hint'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
		txt += '\n'
		if self._payload['recommendation'] is not None:
			txt += '\n'
			txt += '%s\n' % gmTools.wrap(self._payload['recommendation'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
			txt += '\n'
		txt += '%s\n' % gmTools.wrap (
			gmTools.coalesce(self._payload['url'], ''),
			width = 50,
			initial_indent = ' ',
			subsequent_indent = ' '
		)
		txt += '\n'
		txt += '%s\n' % gmTools.wrap(self._payload['query'], width = 50, initial_indent = ' ', subsequent_indent = ' ')
		return txt

#------------------------------------------------------------
def get_suppressed_hints(pk_identity=None, order_by=None, return_pks=False):
	args = {'pat': pk_identity}
	if pk_identity is None:
		where = 'true'
	else:
		where = "pk_identity = %(pat)s"
	if order_by is None:
		order_by = ''
	else:
		order_by = ' ORDER BY %s' % order_by
	cmd = (_SQL_get_suppressed_hints % where) + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_suppressed_hint'] for r in rows ]
	return [ cSuppressedHint(row = {'data': r, 'pk_field': 'pk_suppressed_hint'}) for r in rows ]

#------------------------------------------------------------
def delete_suppressed_hint(pk_suppressed_hint=None):
	args = {'pk': pk_suppressed_hint}
	cmd = "DELETE FROM clin.suppressed_hint WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
def invalidate_hint_suppression(pk_hint=None, pk_encounter=None):
	_log.debug('invalidating suppression of hint #%s', pk_hint)
	args = {
		'pk_hint': pk_hint,
		'enc': pk_encounter,
		'fake_md5': '***INVALIDATED***'			# only needs to NOT match ANY md5 sum
	}
	cmd = """
		UPDATE clin.suppressed_hint SET
			fk_encounter = %(enc)s,
			md5_sum = %(fake_md5)s
		WHERE
			pk = (
				SELECT pk_suppressed_hint
				FROM clin.v_suppressed_hints
				WHERE
					pk_hint = %(pk_hint)s
						AND
					pk_identity = (
						SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s
					)
			)
	"""
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#---------------------------------------
	def test_auto_hints():
#		for row in get_dynamic_hints():
#			print row
		for row in get_hints_for_patient(pk_identity = 12):
			print(row)
	#---------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	test_auto_hints()
