# -*- coding: utf-8 -*-
"""GNUmed external care classes.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

# standard libs
import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

from Gnumed.business import gmOrganization


_log = logging.getLogger('gm.ext_care')

#============================================================
_SQL_get_external_care_items = """SELECT * FROM clin.v_external_care WHERE %s"""

class cExternalCareItem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents an external care item.

	Note: Upon saving .issue being (non-empty AND not None) will
	override .fk_health_issue (IOW, if your code wants to set
	.fk_health_issue to something other than NULL it needs to
	unset .issue explicitly (to u'' or None)).
	"""
	_cmd_fetch_payload = _SQL_get_external_care_items % "pk_external_care = %s"
	_cmds_store_payload = [
		"""UPDATE clin.external_care SET
				comment = gm.nullify_empty_string(%(comment)s),
				fk_encounter = %(pk_encounter)s,
				issue = gm.nullify_empty_string(%(issue)s),
				provider = gm.nullify_empty_string(%(provider)s),
				fk_org_unit = %(pk_org_unit)s,
				inactive = %(inactive)s,
				fk_health_issue = (
					CASE
						WHEN gm.is_null_or_blank_string(%(issue)s) IS TRUE THEN %(pk_health_issue)s
						ELSE NULL
					END
				)::integer
			WHERE
				pk = %(pk_external_care)s
					AND
				xmin = %(xmin_external_care)s
			RETURNING
				xmin AS xmin_external_care
		""",
		_SQL_get_external_care_items % "pk_external_care = %(pk_external_care)s"
	]
	_updatable_fields = [
		'pk_encounter',
		'pk_health_issue',
		'pk_org_unit',
		'issue',
		'provider',
		'comment',
		'inactive'
	]
	#--------------------------------------------------------
	def format(self, with_health_issue=True, with_address=False, with_comms=False):
		lines = []
		lines.append(_('External care%s             #%s') % (
			gmTools.bool2subst (
				self._payload['inactive'],
				' (%s)' % _('inactive'),
				'',
				' [ERROR: .inactive is NULL]'
			),
			self._payload['pk_external_care']
		))
		if with_health_issue:
			if self._payload['pk_health_issue'] is None:
				lines.append(' ' + _('Issue: %s') % self._payload['issue'])
			else:
				lines.append(' ' + _('Health issue: %s') % self._payload['issue'])
				lines.append('  (' + _('also treated here') + ')')
		if self._payload['provider'] is not None:
			lines.append(' ' + _('Provider: %s') % self._payload['provider'])
		lines.append(' ' + _('Location: %s@%s') % (self._payload['unit'], self._payload['organization']))
		unit = self.org_unit
		if with_address:
			adr = unit.address
			if adr is not None:
				lines.extend(adr.format())
		if with_comms:
			for comm in unit.comm_channels:
				lines.append('  %s: %s%s' % (
					comm['l10n_comm_type'],
					comm['url'],
					gmTools.bool2subst(comm['is_confidential'], _(' (confidential)'), '', '')
				))
		if self._payload['comment'] is not None:
			lines.append('')
			lines.append(' ' + self._payload['comment'])

		return lines
	#--------------------------------------------------------
	def _get_org_unit(self):
		return gmOrganization.cOrgUnit(self._payload['pk_org_unit'])

	org_unit = property(_get_org_unit)

#------------------------------------------------------------
def get_external_care_items(order_by=None, pk_identity=None, pk_health_issue=None, exclude_inactive=False, return_pks=False):

	args = {
		'pk_pat': pk_identity,
		'pk_issue': pk_health_issue
	}
	where_parts = []
	if pk_identity is not None:
		where_parts.append('pk_identity = %(pk_pat)s')
	if pk_health_issue is not None:
		where_parts.append('pk_health_issue = %(pk_issue)s')
	if exclude_inactive is True:
		where_parts.append('inactive IS FALSE')

	if len(where_parts) == 0:
		where = 'TRUE'
	else:
		where = ' AND '.join(where_parts)

	if order_by is not None:
		where = '%s ORDER BY %s' % (
			where,
			order_by
		)

	cmd = _SQL_get_external_care_items % where
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_external_care'] for r in rows ]

	return [ cExternalCareItem(row = {'data': r, 'pk_field': 'pk_external_care'}) for r in rows ]

#------------------------------------------------------------
def create_external_care_item(pk_health_issue=None, issue=None, pk_org_unit=None, pk_encounter=None):
	args = {
		'pk_health_issue': pk_health_issue,
		'issue': issue,
		'pk_org_unit': pk_org_unit,
		'enc': pk_encounter
	}
	cmd = """
		INSERT INTO clin.external_care (
			issue,
			fk_health_issue,
			fk_encounter,
			fk_org_unit
		) VALUES (
			gm.nullify_empty_string(%(issue)s),
			(CASE
				WHEN gm.is_null_or_blank_string(%(issue)s) IS TRUE THEN %(pk_health_issue)s
				ELSE NULL
			END)::integer,
			%(enc)s,
			%(pk_org_unit)s
		)
		RETURNING pk"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cExternalCareItem(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_external_care_item(pk_external_care=None):
	args = {'pk': pk_external_care}
	cmd = "DELETE FROM clin.external_care WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#from Gnumed.pycommon import gmLog2
	#-----------------------------------------
	def test_get_care_items():
		for item in get_external_care_items(pk_identity = 12, order_by = 'provider'):
			print(item.format())

	#-----------------------------------------
	test_get_care_items()
